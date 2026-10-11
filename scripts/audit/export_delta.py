"""Field-level before/after delta for the export artifacts (working agreement 2).

    python scripts/audit/export_delta.py stix BEFORE.json AFTER.json
    python scripts/audit/export_delta.py tree BEFORE_DIR AFTER_DIR      # byte-level, any dir
    python scripts/audit/export_delta.py misp BEFORE_DIR AFTER_DIR      # field-level MISP feed
    python scripts/audit/export_delta.py jsonl BEFORE.jsonl AFTER.jsonl # HF rows, by id

`stix`: object ID set, then per (type, field) the number of objects whose value
changed / were added / were removed, with one example. `tree`: file-set and
per-file byte identity, then for JSON files the same field-level walk.
Prints JSON on stdout; exit 0 always (the delta is a report, the judgement is
the reviewer's -- an undeclared moved field is a defect).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def _walk(a, b, path=""):
    """Yield (path, before, after) leaves that differ, descending dicts only."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                yield (f"{path}.{k}" if path else k, "<absent>", b[k])
            elif k not in b:
                yield (f"{path}.{k}" if path else k, a[k], "<absent>")
            else:
                yield from _walk(a[k], b[k], f"{path}.{k}" if path else k)
    elif a != b:
        yield (path, a, b)


def diff_objects(before: list[dict], after: list[dict], key=lambda o: o["id"],
                 kind=lambda o: o.get("type", "?")) -> dict:
    bi = {key(o): o for o in before}
    ai = {key(o): o for o in after}
    changed: dict[str, Counter] = defaultdict(Counter)
    example: dict[str, tuple] = {}
    for k in sorted(set(bi) & set(ai)):
        for path, x, y in _walk(bi[k], ai[k]):
            fld = f"{kind(ai[k])}:{path}"
            changed[fld]["objects"] += 1
            example.setdefault(fld, (k, x, y))
    return {
        "before_objects": len(bi), "after_objects": len(ai),
        "ids_removed": sorted(set(bi) - set(ai))[:5], "n_ids_removed": len(set(bi) - set(ai)),
        "ids_added": sorted(set(ai) - set(bi))[:5], "n_ids_added": len(set(ai) - set(bi)),
        "field_changes": {f: {"objects": c["objects"],
                              "example": {"id": example[f][0],
                                          "before": str(example[f][1])[:120],
                                          "after": str(example[f][2])[:120]}}
                          for f, c in sorted(changed.items())},
    }


def stix(b: Path, a: Path) -> dict:
    return diff_objects(json.loads(b.read_text("utf-8"))["objects"],
                        json.loads(a.read_text("utf-8"))["objects"])


def tree(b: Path, a: Path) -> dict:
    bf = {p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    af = {p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    out = {"files_removed": sorted(bf - af), "files_added": sorted(af - bf),
           "files_identical": 0, "files_changed": {}}
    for rel in sorted(bf & af):
        x, y = (b / rel).read_bytes(), (a / rel).read_bytes()
        if x == y:
            out["files_identical"] += 1
        else:
            out["files_changed"][rel] = {"bytes_before": len(x), "bytes_after": len(y)}
    return out


def misp(b: Path, a: Path) -> dict:
    """Field-level: event metadata by event uuid, attributes by attribute uuid,
    and attribute Tag lists as added/removed tag-predicate counts."""
    def load(d: Path):
        ev, attrs = {}, {}
        for p in sorted(d.glob("*.json")):
            if p.name in ("manifest.json", "build_manifest.json"):
                continue
            e = json.loads(p.read_text("utf-8"))["Event"]
            ev[e["uuid"]] = {k: v for k, v in e.items() if k != "Attribute"}
            for at in e["Attribute"]:
                attrs[at["uuid"]] = at
        return ev, attrs
    (be, ba), (ae, aa) = load(b), load(a)
    out = {"events": {"before": len(be), "after": len(ae),
                      "ids_removed": len(set(be) - set(ae)), "ids_added": len(set(ae) - set(be))},
           "attributes": {"before": len(ba), "after": len(aa),
                          "ids_removed": len(set(ba) - set(aa)), "ids_added": len(set(aa) - set(ba))}}
    ev_changed = Counter(); ex = {}
    for k in sorted(set(be) & set(ae)):
        for path, x, y in _walk(be[k], ae[k]):
            ev_changed[f"Event.{path}"] += 1; ex.setdefault(f"Event.{path}", (x, y))
    out["event_field_changes"] = {f: {"events": n, "example_before": str(ex[f][0])[:60],
                                      "example_after": str(ex[f][1])[:60]}
                                  for f, n in sorted(ev_changed.items())}
    fld = Counter(); tag_add = Counter(); tag_rm = Counter(); tag_ex = {}
    for k in sorted(set(ba) & set(aa)):
        x, y = ba[k], aa[k]
        for key in sorted(set(x) | set(y)):
            if key == "Tag":
                xt = {t["name"] for t in x.get("Tag", [])}
                yt = {t["name"] for t in y.get("Tag", [])}
                if xt != yt:
                    fld["Attribute.Tag"] += 1
                for t in yt - xt:
                    tag_add[t.split("=")[0]] += 1; tag_ex.setdefault(t.split("=")[0], t)
                for t in xt - yt:
                    tag_rm[t.split("=")[0]] += 1
            elif x.get(key) != y.get(key):
                fld[f"Attribute.{key}"] += 1
    out["attribute_field_changes"] = dict(fld)
    out["attribute_tags_added_by_predicate"] = dict(tag_add)
    out["attribute_tags_removed_by_predicate"] = dict(tag_rm)
    out["attribute_tag_added_examples"] = tag_ex
    mb = json.loads((b / "manifest.json").read_text("utf-8"))
    ma = json.loads((a / "manifest.json").read_text("utf-8"))
    out["manifest"] = diff_objects([{"id": k, **v} for k, v in mb.items()],
                                   [{"id": k, **v} for k, v in ma.items()],
                                   kind=lambda o: "manifest")["field_changes"]
    out["other_files"] = {f: (b / f).read_bytes() == (a / f).read_bytes()
                          for f in ("hashes.csv", "README.md") if (b / f).exists()}
    return out


def jsonl(b: Path, a: Path) -> dict:
    rows = lambda p: [json.loads(l) for l in p.read_text("utf-8").split(chr(10)) if l]
    return diff_objects(rows(b), rows(a), kind=lambda o: "row")


if __name__ == "__main__":
    mode, x, y = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    fn = {"stix": stix, "tree": tree, "misp": misp, "jsonl": jsonl}[mode]
    print(json.dumps(fn(x, y), indent=2))
