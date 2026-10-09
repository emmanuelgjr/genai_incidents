"""Field-level before/after delta of data/incidents.json vs a git ref
(working agreement 2). Read-only; no network. Per-row, per-field: reports the
changed-row count for EVERY field (union of keys), split by row source class,
the ID-set comparison, top-level key changes, and whether
data/id_deprecations.json is byte-identical.

    python scripts/audit/field_delta_vs_ref.py [--ref main]

Source class of a row: 'OECD' if any source_id startswith OECD-AIM-, else the
prefix of its first source_id (CVE-/AIID-/AVID-/AIAAIC-/...).
"""
from __future__ import annotations
import argparse, collections, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _git_show(ref: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, capture_output=True).stdout


def source_class(e: dict) -> str:
    sids = e.get("source_ids") or []
    if any(str(s).startswith("OECD-AIM-") for s in sids):
        return "OECD"
    return (str(sids[0]).split("-")[0] if sids else "none")


def delta(before: dict, after: dict) -> dict:
    b = {e["id"]: e for e in before["incidents"]}
    a = {e["id"]: e for e in after["incidents"]}
    out = {"rows_before": len(b), "rows_after": len(a),
           "ids_added": sorted(set(a) - set(b)), "ids_removed": sorted(set(b) - set(a)),
           "fields": collections.defaultdict(collections.Counter), "changed_rows": 0}
    out["key_order_changed"] = []
    for i in sorted(set(a) & set(b)):
        if list(a[i]) != list(b[i]) and set(a[i]) == set(b[i]):
            out["key_order_changed"].append(i)
        keys = set(a[i]) | set(b[i])
        ch = [k for k in keys if a[i].get(k, "<absent>") != b[i].get(k, "<absent>")]
        if ch:
            out["changed_rows"] += 1
        for k in ch:
            out["fields"][k][source_class(a[i])] += 1
    out["top_level_changed"] = sorted(k for k in set(before) | set(after)
                                      if k != "incidents" and before.get(k, "<absent>") != after.get(k, "<absent>"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main")
    ns = ap.parse_args(argv)
    before = json.loads(_git_show(ns.ref, "data/incidents.json"))
    after = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    d = delta(before, after)
    dep_same = _git_show(ns.ref, "data/id_deprecations.json") == (ROOT / "data" / "id_deprecations.json").read_bytes()
    print(f"ref={ns.ref}")
    print(f"rows: {d['rows_before']} -> {d['rows_after']}; ids added={len(d['ids_added'])} removed={len(d['ids_removed'])}")
    print(f"id_deprecations.json byte-identical: {dep_same}")
    print(f"top-level keys changed: {d['top_level_changed']}")
    print(f"rows with any change: {d['changed_rows']}")
    ko = d["key_order_changed"]
    print(f"rows whose key ORDER changed with an identical key set (byte-level only): {len(ko)} {ko[:5]}")
    for k in sorted(d["fields"]):
        c = d["fields"][k]
        print(f"  field {k}: {sum(c.values())} rows  by source {dict(c)}")
    if not d["fields"]:
        print("  (no field changed on any row)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
