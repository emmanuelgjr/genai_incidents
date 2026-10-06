"""scripts/atlas_entry_delta.py -- per-entity before/after delta for an ATLAS refresh
(CLAUDE.md working agreement 2: the field-level delta rule).

Compares two ``incidents.json`` files ENTRY BY ENTRY (by ``id``), never by
aggregate, and writes a markdown report listing:

* entry count and ID set before / after (added / removed ids, if any);
* every entry whose ``mitre_atlas`` or ``mitre_atlas_tactics`` changed
  (id, before, after, reason);
* every OTHER field that moved on any entry, with counts and examples --
  expected: ``updated`` (the merge stamps ``updated`` = build date when an
  entry's content snapshot changes) and nothing else; anything else is a
  defect to explain;
* a per-entity proof that every entry with no declared change is
  byte-identical (canonical JSON) before and after.

Usage::

    python scripts/atlas_entry_delta.py BEFORE.json AFTER.json OUT.md [--json OUT.json]

Offline; reads files only. ``reason`` text is derived from
``mappings/atlas_id_translations.json`` and the old/new pin technique->tactic
links (pass ``--old-pin`` with the previous mappings/mitre_atlas.json).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atlas_pin  # noqa: E402

DECLARED = ("mitre_atlas", "mitre_atlas_tactics")


def _canon(e: dict) -> str:
    return json.dumps(e, sort_keys=True, ensure_ascii=False)


def _links(pin: dict) -> dict[str, list[str]]:
    out = {}
    for k, v in (pin.get("techniques") or {}).items():
        out[k] = v.get("tactics") or []
    return out


def _tactics_for(ids, links) -> set[str]:
    s: set[str] = set()
    for t in ids:
        tac = links.get(t) or (links.get(t.rsplit(".", 1)[0]) if t.count(".") >= 2 else [])
        s.update(tac or [])
    return s


def compute(before_path: Path, after_path: Path, old_pin: dict | None, new_pin: dict) -> dict:
    b_doc = json.loads(before_path.read_text(encoding="utf-8"))
    a_doc = json.loads(after_path.read_text(encoding="utf-8"))
    b_all, a_all = b_doc["incidents"], a_doc["incidents"]
    envelope = {k: (b_doc.get(k), a_doc.get(k)) for k in sorted(set(b_doc) | set(a_doc))
                if k != "incidents" and b_doc.get(k) != a_doc.get(k)}
    b = {e["id"]: e for e in b_all}
    a = {e["id"]: e for e in a_all}
    assert len(b) == len(b_all) and len(a) == len(a_all), "duplicate ids"
    trans = atlas_pin.load_translations()
    old_links = _links(old_pin or {})
    new_links = _links(new_pin)

    changed, other_fields = [], defaultdict(list)
    untouched_total = untouched_identical = 0
    violations = []
    for eid in sorted(set(a) & set(b)):
        be, ae = b[eid], a[eid]
        keys = set(be) | set(ae)
        moved = sorted(k for k in keys if _canon({k: be.get(k)}) != _canon({k: ae.get(k)}))
        declared = [k for k in moved if k in DECLARED]
        others = [k for k in moved if k not in DECLARED]
        for k in others:
            other_fields[k].append(eid)
        if declared:
            bt, at = set(be.get("mitre_atlas") or []), set(ae.get("mitre_atlas") or [])
            btc, atc = set(be.get("mitre_atlas_tactics") or []), set(ae.get("mitre_atlas_tactics") or [])
            reasons = []
            for t in sorted(bt - at):
                if t in trans:
                    reasons.append(f"{t} -> {trans[t]} (id translation)")
                else:
                    reasons.append(f"{t} removed (UNEXPLAINED: no translation)")
            for t in sorted(at - bt):
                if not any(trans.get(x) == t for x in bt - at):
                    reasons.append(f"{t} added (UNEXPLAINED: not a translation target)")
            for tac in sorted(btc - atc):
                reasons.append(f"{tac} dropped: no remaining technique links to it"
                               if tac not in _tactics_for(at, new_links) else
                               f"{tac} dropped (UNEXPLAINED)")
            for tac in sorted(atc - btc):
                srcs = sorted(t for t in at if tac in _tactics_for([t], new_links)
                              and tac not in _tactics_for([t], old_links))
                reasons.append(f"{tac} added via new link from {', '.join(srcs)}" if srcs
                               else f"{tac} added (UNEXPLAINED)")
            changed.append({"id": eid, "fields": declared,
                            "mitre_atlas_before": sorted(bt), "mitre_atlas_after": sorted(at),
                            "tactics_before": sorted(btc), "tactics_after": sorted(atc),
                            "other_fields_moved": others, "reasons": reasons})
        else:
            untouched_total += 1
            if _canon(be) == _canon(ae):
                untouched_identical += 1
            else:
                violations.append({"id": eid, "fields": others})
    return {
        "before_count": len(b), "after_count": len(a),
        "ids_added": sorted(set(a) - set(b)), "ids_removed": sorted(set(b) - set(a)),
        "changed": changed, "other_fields": {k: v for k, v in sorted(other_fields.items())},
        "untouched_total": untouched_total, "untouched_identical": untouched_identical,
        "untouched_violations": violations,
        "old_version": (old_pin or {}).get("version"), "new_version": new_pin.get("version"),
        "envelope_moved": envelope,
    }


def _fmt(ids: list[str]) -> str:
    return ", ".join(f"`{i}`" for i in ids) or "-"


def render(r: dict, before_name: str, after_name: str, notes: str = "") -> str:
    ch = r["changed"]
    lines = [
        "# ATLAS refresh: per-entry field-level delta", "",
        f"ATLAS pin {r['old_version']} -> {r['new_version']}. Before = `{before_name}`, "
        f"after = `{after_name}`. Generated by `scripts/atlas_entry_delta.py`; do not hand-edit. "
        "(DO-NOT-REGENERATE once committed: it is a dated record of one refresh.)", "",
        *( [notes.rstrip(), ""] if notes else [] ),
        "## Entry count and ID set", "",
        f"- before: **{r['before_count']}** entries; after: **{r['after_count']}** entries.",
        f"- ids added: {_fmt(r['ids_added'])}; ids removed: {_fmt(r['ids_removed'])}.",
        f"- ID set identical: **{not r['ids_added'] and not r['ids_removed']}**.", "",
        "## Entries whose ATLAS codes changed", "",
        f"**{len(ch)}** entries changed `mitre_atlas` and/or `mitre_atlas_tactics`.", ""]
    by_pat = Counter()
    for c in ch:
        pat = (tuple(sorted(set(c["mitre_atlas_before"]) - set(c["mitre_atlas_after"]))),
               tuple(sorted(set(c["mitre_atlas_after"]) - set(c["mitre_atlas_before"]))),
               tuple(sorted(set(c["tactics_before"]) - set(c["tactics_after"]))),
               tuple(sorted(set(c["tactics_after"]) - set(c["tactics_before"]))))
        by_pat[pat] += 1
    lines += ["### Summary by change pattern", "",
              "| entries | techniques removed | techniques added | tactics removed | tactics added |",
              "|---:|---|---|---|---|"]
    for pat, n in by_pat.most_common():
        lines.append(f"| {n} | {_fmt(list(pat[0]))} | {_fmt(list(pat[1]))} | {_fmt(list(pat[2]))} | {_fmt(list(pat[3]))} |")
    unexplained = [c for c in ch if any("UNEXPLAINED" in x for x in c["reasons"])]
    lines += ["", f"Entries with an UNEXPLAINED change reason: **{len(unexplained)}**.", "",
              "### Every changed entry", "",
              "`before`/`after` show the codes that differ (full before/after lists for every "
              "entry are in the companion `.json`). Reason column derives from "
              "`mappings/atlas_id_translations.json` and the old/new pin technique->tactic links.", "",
              "| id | before (differing codes) | after (differing codes) | other fields moved | reason |",
              "|---|---|---|---|---|"]
    for c in ch:
        bt, at = set(c["mitre_atlas_before"]), set(c["mitre_atlas_after"])
        btc, atc = set(c["tactics_before"]), set(c["tactics_after"])
        bef = sorted(bt - at) + sorted(btc - atc)
        aft = sorted(at - bt) + sorted(atc - btc)
        lines.append(f"| {c['id']} | {_fmt(bef)} | {_fmt(aft)} | {_fmt(c['other_fields_moved'])} | "
                     f"{'; '.join(c['reasons'])} |")
    lines += ["", "## Every other field that moved", "",
              "Top-level envelope fields (outside `incidents`) that moved: "
              + ("; ".join(f"`{k}`: {a!r} -> {b!r}" for k, (a, b) in r["envelope_moved"].items())
                 or "none") + ".", "",
              "Per-entry fields:", ""]
    ch_ids = {c["id"] for c in ch}
    if not r["other_fields"]:
        lines.append("None.")
    else:
        lines += ["| field | entries where it moved | of which among the changed-code entries |",
                  "|---|---:|---:|"]
        for k, ids in r["other_fields"].items():
            lines.append(f"| `{k}` | {len(ids)} | {len(set(ids) & ch_ids)} |")
        outside = {k: sorted(set(ids) - ch_ids) for k, ids in r["other_fields"].items()
                   if set(ids) - ch_ids}
        lines += ["", "Fields that moved on entries OUTSIDE the changed-code set (each is a defect "
                      "unless explained):", ""]
        lines += [f"- `{k}`: {len(v)} entries, e.g. {_fmt(v[:5])}" for k, v in outside.items()] or ["- none"]
    lines += ["", "## Untouched entries are byte-identical (per entity)", "",
              f"Entries with no change to either declared field: **{r['untouched_total']}**. "
              f"Canonical-JSON (sorted keys) identical before vs after: **{r['untouched_identical']}**. "
              f"Violations: **{len(r['untouched_violations'])}**.", ""]
    for v in r["untouched_violations"][:50]:
        lines.append(f"- `{v['id']}` moved: {v['fields']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--old-pin", type=Path, default=None, help="previous mappings/mitre_atlas.json")
    ap.add_argument("--before-label", default=None, help="display name of BEFORE (default: file name)")
    ap.add_argument("--after-label", default=None, help="display name of AFTER (default: file name)")
    ap.add_argument("--notes", type=Path, default=None, help="markdown text inserted after the header")
    a = ap.parse_args()
    old_pin = atlas_pin.load_pin(a.old_pin) if a.old_pin else None
    r = compute(a.before, a.after, old_pin, atlas_pin.load_pin())
    a.out.parent.mkdir(parents=True, exist_ok=True)
    notes = a.notes.read_text(encoding="utf-8") if a.notes else ""
    a.out.write_text(render(r, a.before_label or a.before.name, a.after_label or a.after.name, notes),
                     encoding="utf-8", newline="\n")
    if a.json:
        a.json.write_text(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    moved = {k: len(v) for k, v in r["other_fields"].items()}
    print(f"[atlas-delta] {len(r['changed'])} entries changed codes; "
          f"{r['untouched_identical']}/{r['untouched_total']} untouched identical; "
          f"other fields moved: {moved}")
    return 0 if not r["untouched_violations"] and not r["ids_added"] and not r["ids_removed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
