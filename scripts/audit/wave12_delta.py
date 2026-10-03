"""Field-level before/after delta for the wave-1/wave-2 ingest
(working agreement 2: any transformative data operation publishes a full
field-level delta; unintended deltas are DEFECTS).

    python scripts/audit/wave12_delta.py \\
        --before <git-ref>:data/incidents.json --after data/incidents.json \\
        --out-prefix docs/audits/wave12-ingest-delta-2026-10-03

What it computes, from two built corpora (no network, no model):

  * counts: total, the corpus split (security / ai-harm), the category split
    (vulnerability-disclosure vs everything else), tier;
  * ID sets: new IDs (must be a contiguous append above the old maximum --
    invariant 9), missing IDs (must be empty -- invariant 3);
  * invariant 9 "no existing ID changes meaning": for every existing ID the
    old source_ids / cve_ids must still be present and the title unchanged;
  * every changed field of every EXISTING entry, classified against an
    explicit, enumerated rule table (``RULES``). A change that no rule
    explains is UNINTENDED and makes the run exit 1.

The check can fail: ``--self-test`` corrupts a copy of the "after" corpus
(one title edit, one downward severity edit, one dropped source id, one
removed entry) and asserts each is caught; the transcript of that run is
pasted in the delta report.
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SEV_ORDER = {"Info": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def load(spec: str) -> dict:
    if ":" in spec and not Path(spec).exists():
        ref, path = spec.split(":", 1)
        raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
                             capture_output=True, check=True).stdout
        return json.loads(raw.decode("utf-8"))
    return json.loads(Path(spec).read_text(encoding="utf-8"))


def by_id(d: dict) -> dict[str, dict]:
    return {e["id"]: e for e in d["incidents"]}


def split_counts(entries: list[dict]) -> dict:
    return {
        "total": len(entries),
        "corpus": dict(collections.Counter(e.get("corpus") for e in entries)),
        "category": dict(collections.Counter(e.get("category") for e in entries)),
        "vulnerability_disclosure": sum(e.get("category") == "vulnerability-disclosure" for e in entries),
        "non_vulnerability": sum(e.get("category") != "vulnerability-disclosure" for e in entries),
        "tier": dict(collections.Counter(e.get("tier") for e in entries)),
    }


# ----------------------------------------------------------------------------
# Rule table: which changes to an existing entry are INTENDED, and why.
# A rule returns True when it fully explains the (field, old, new) change.
# ----------------------------------------------------------------------------
def _added_only(old, new) -> bool:
    old = old or []
    new = new or []
    return all(x in new for x in old) and len(new) > len(old)


def _is_avid_enrichment(e_after: dict) -> bool:
    return any(s.startswith("AVID-") for s in e_after.get("source_ids") or [])


RULES = {
    "source_ids": ("add-only: an AVID report (or CVE-keyed source id) for a CVE the entry already "
                   "held is folded in as an extra source id",
                   lambda o, n, ea: _added_only(o, n)),
    "references": ("add-only: the AVID record URL and AVID's source links are appended",
                   lambda o, n, ea: _added_only([json.dumps(x, sort_keys=True) for x in o or []],
                                                [json.dumps(x, sort_keys=True) for x in n or []])),
    "tags": ("add-only: tag union on merge (merge_into)",
             lambda o, n, ea: _added_only(o, n)),
    "source_count": ("derived: number of distinct sources, rises with source_ids",
                     lambda o, n, ea: (n or 0) > (o or 0)),
    "confidence": ("derived: 2+ distinct sources with a CVE => high (DATA_DICTIONARY)",
                   lambda o, n, ea: {"low": 0, "medium": 1, "high": 2}.get(n, -1)
                   > {"low": 0, "medium": 1, "high": 2}.get(o, 3)),
    "updated": ("bumps only on a content change, to the build date (invariant 4)",
                lambda o, n, ea: (n or "") > (o or "")),
    "last_seen": ("derived: latest source_freshness among the entry's sources",
                  lambda o, n, ea: (n or "") >= (o or "")),
    "first_seen": ("derived: earliest source_freshness among the entry's sources",
                   lambda o, n, ea: (n or "") <= (o or "9999")),
    "cve_ids": ("add-only: a CVE carried by the folded-in AVID report",
                lambda o, n, ea: _added_only(o, n)),
    "cwe_ids": ("add-only: CWE ids carried by the folded-in report",
                lambda o, n, ea: _added_only(o, n)),
    "purl": ("add-only: derived from affected packages",
             lambda o, n, ea: _added_only(o, n)),
    "capec_ids": ("add-only: derived from cwe_ids",
                  lambda o, n, ea: _added_only(o, n)),
}


def classify(field: str, old, new, e_after: dict) -> tuple[bool, str]:
    rule = RULES.get(field)
    if rule is None:
        return False, "no rule explains a change to this field"
    why, test = rule
    try:
        return bool(test(old, new, e_after)), why
    except Exception as exc:  # noqa: BLE001
        return False, f"rule errored: {exc}"


def diff(before: dict, after: dict) -> dict:
    b, a = by_id(before), by_id(after)
    new_ids = sorted(set(a) - set(b))
    missing = sorted(set(b) - set(a))
    max_old = max(int(i.split("-")[1]) for i in b)
    new_nums = sorted(int(i.split("-")[1]) for i in new_ids)
    contiguous = new_nums == list(range(max_old + 1, max_old + 1 + len(new_nums)))

    meaning_breaks = []
    changes = []          # one record per (id, field)
    changed_ids = set()
    for i in sorted(set(b) & set(a)):
        eb, ea = b[i], a[i]
        if not set(eb.get("source_ids") or []) <= set(ea.get("source_ids") or []) or \
           not set(eb.get("cve_ids") or []) <= set(ea.get("cve_ids") or []) or \
           eb.get("title") != ea.get("title"):
            meaning_breaks.append(i)
        for f in sorted(set(eb) | set(ea)):
            if eb.get(f) == ea.get(f):
                continue
            ok, why = classify(f, eb.get(f), ea.get(f), ea)
            changes.append({"id": i, "field": f, "before": eb.get(f), "after": ea.get(f),
                            "intended": ok, "justification": why})
            changed_ids.add(i)

    sev_down = [c["id"] for c in changes if c["field"] == "severity"
                and SEV_ORDER.get(c["after"], 2) < SEV_ORDER.get(c["before"], 2)]
    by_field = collections.Counter(c["field"] for c in changes)
    unintended = [c for c in changes if not c["intended"]]
    return {
        "before": split_counts(before["incidents"]),
        "after": split_counts(after["incidents"]),
        "new_ids": new_ids,
        "missing_ids": missing,
        "new_ids_contiguous_append_above_old_max": contiguous,
        "old_max_id_number": max_old,
        "existing_ids_whose_meaning_changed": meaning_breaks,
        "existing_entries_changed": len(changed_ids),
        "changed_ids": sorted(changed_ids),
        "changes_by_field": dict(by_field),
        "severity_downgrades": sev_down,
        "unintended": unintended,
        "changes": changes,
    }


def verdict(d: dict) -> list[str]:
    problems = []
    if d["missing_ids"]:
        problems.append(f"{len(d['missing_ids'])} entries removed (invariant 3)")
    if not d["new_ids_contiguous_append_above_old_max"]:
        problems.append("new IDs are not a contiguous append above the old maximum (invariant 9)")
    if d["existing_ids_whose_meaning_changed"]:
        problems.append(f"{len(d['existing_ids_whose_meaning_changed'])} existing IDs changed meaning (invariant 9)")
    if d["unintended"]:
        problems.append(f"{len(d['unintended'])} unintended field changes on existing entries")
    if d["severity_downgrades"]:
        problems.append(f"{len(d['severity_downgrades'])} severity downgrades")
    return problems


def self_test(before: dict, after: dict) -> bool:
    """Corrupt a copy of *after* four ways; each must be caught."""
    ok = True
    ids = sorted(set(by_id(before)) & set(by_id(after)))

    def run(label, mutate, expect_substr):
        nonlocal ok
        corrupted = copy.deepcopy(after)
        mutate(corrupted)
        problems = verdict(diff(before, corrupted))
        hit = any(expect_substr in p for p in problems)
        print(f"  self-test [{label}]: {'CAUGHT' if hit else 'MISSED'} -> {problems}")
        ok &= hit

    victim = ids[0]

    def edit_title(d):
        for e in d["incidents"]:
            if e["id"] == victim:
                e["title"] += " (tampered)"
    run("title edit on an existing entry", edit_title, "changed meaning")

    def downgrade(d):
        for e in d["incidents"]:
            if e["id"] == ids[1] and e.get("severity") != "Low":
                e["severity"] = "Low"
    run("severity downgrade", downgrade, "severity downgrades")

    def drop_src(d):
        for e in d["incidents"]:
            if e["id"] == ids[2] and len(e.get("source_ids") or []) > 0:
                e["source_ids"] = e["source_ids"][1:]
    run("dropped source id", drop_src, "changed meaning")

    def remove(d):
        d["incidents"] = [e for e in d["incidents"] if e["id"] != ids[3]]
    run("removed entry", remove, "removed")

    def sneaky_description(d):
        for e in d["incidents"]:
            if e["id"] == ids[4]:
                e["description"] += " tampered"
    run("description rewrite (no rule explains it)", sneaky_description, "unintended")
    return ok


def render_md(d: dict, meta: dict) -> str:
    L = []
    b, a = d["before"], d["after"]
    L.append("# Wave 1 + wave 2 ingest: field-level delta (2026-10-03)\n")
    L.append("Generated by `scripts/audit/wave12_delta.py`; machine-readable twin: "
             "`wave12-ingest-delta-2026-10-03.json`. Working agreement 2: unintended deltas are defects.\n")
    for k, v in meta.items():
        L.append(f"- {k}: {v}")
    L.append("\n## Counts, as the project reports them\n")
    L.append("| | before | after | delta |\n|---|---:|---:|---:|")
    L.append(f"| `incident_count` | {b['total']:,} | {a['total']:,} | {a['total'] - b['total']:+,} |")
    for c in sorted(set(b["corpus"]) | set(a["corpus"])):
        L.append(f"| corpus `{c}` | {b['corpus'].get(c, 0):,} | {a['corpus'].get(c, 0):,} | "
                 f"{a['corpus'].get(c, 0) - b['corpus'].get(c, 0):+,} |")
    L.append(f"| category `vulnerability-disclosure` | {b['vulnerability_disclosure']:,} | "
             f"{a['vulnerability_disclosure']:,} | {a['vulnerability_disclosure'] - b['vulnerability_disclosure']:+,} |")
    L.append(f"| category: all other | {b['non_vulnerability']:,} | {a['non_vulnerability']:,} | "
             f"{a['non_vulnerability'] - b['non_vulnerability']:+,} |")
    for c in sorted(set(b["category"]) | set(a["category"])):
        L.append(f"| &nbsp;&nbsp;`{c}` | {b['category'].get(c, 0):,} | {a['category'].get(c, 0):,} | "
                 f"{a['category'].get(c, 0) - b['category'].get(c, 0):+,} |")
    for c in sorted(set(b["tier"]) | set(a["tier"])):
        L.append(f"| tier `{c}` | {b['tier'].get(c, 0):,} | {a['tier'].get(c, 0):,} | "
                 f"{a['tier'].get(c, 0) - b['tier'].get(c, 0):+,} |")
    L.append("\n## ID set (invariants 3 and 9)\n")
    L.append(f"- new IDs: **{len(d['new_ids']):,}**"
             + (f" ({d['new_ids'][0]} .. {d['new_ids'][-1]})" if d["new_ids"] else ""))
    L.append(f"- contiguous append above the old maximum (INC-{d['old_max_id_number']:05d}): "
             f"**{d['new_ids_contiguous_append_above_old_max']}**")
    L.append(f"- IDs missing after: **{len(d['missing_ids'])}** (invariant 3)")
    L.append(f"- existing IDs whose meaning changed (source_ids/cve_ids lost, or title edited): "
             f"**{len(d['existing_ids_whose_meaning_changed'])}** (invariant 9)")
    L.append("\n## Changes to EXISTING entries, by field\n")
    L.append(f"{d['existing_entries_changed']:,} existing entries changed; "
             f"{sum(1 for c in d['changes'] if c['intended']):,} field changes explained by a rule, "
             f"**{len(d['unintended'])} unintended**.\n")
    L.append("| field | changes | intended | justification |\n|---|---:|---:|---|")
    for f, n in sorted(d["changes_by_field"].items(), key=lambda kv: -kv[1]):
        ch = [c for c in d["changes"] if c["field"] == f]
        ok = sum(c["intended"] for c in ch)
        L.append(f"| `{f}` | {n} | {ok} | {ch[0]['justification']} |")
    if d["unintended"]:
        L.append("\n### UNINTENDED (defects)\n")
        for c in d["unintended"][:200]:
            L.append(f"- {c['id']} `{c['field']}`: {json.dumps(c['before'])[:160]} -> {json.dumps(c['after'])[:160]}")
    L.append("\n### Changed existing entries (id: fields)\n")
    per = collections.defaultdict(list)
    for c in d["changes"]:
        per[c["id"]].append(c["field"])
    for i in sorted(per):
        L.append(f"- {i}: {', '.join(sorted(per[i]))}")
    L.append(f"\nSeverity downgrades: {len(d['severity_downgrades'])}.")
    L.append("\nThe full per-field before/after for every changed entry is in the JSON twin "
             "(`changes[]`, one record per entry and field).")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True, help="path or <git-ref>:<path>")
    ap.add_argument("--after", required=True)
    ap.add_argument("--out-prefix")
    ap.add_argument("--meta", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    before, after = load(args.before), load(args.after)
    if args.self_test:
        return 0 if self_test(before, after) else 1
    d = diff(before, after)
    problems = verdict(d)
    meta = dict(m.split("=", 1) for m in args.meta)
    if args.out_prefix:
        out = Path(args.out_prefix)
        (out.parent / (out.name + ".json")).write_text(
            json.dumps({"meta": meta, "problems": problems, **d}, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8")
        (out.parent / (out.name + ".md")).write_text(render_md(d, meta), encoding="utf-8")
    print(json.dumps({"before_total": d["before"]["total"], "after_total": d["after"]["total"],
                      "new_ids": len(d["new_ids"]), "existing_changed": d["existing_entries_changed"],
                      "changes_by_field": d["changes_by_field"], "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
