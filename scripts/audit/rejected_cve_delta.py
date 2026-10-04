"""Field-level before/after delta for the rejected-CVE reconciliation (working
agreement 2). Every changed field on every entry is enumerated and judged
against an expectation derived INDEPENDENTLY of the merge rule: the expected
sets come from the committed CVE-state snapshot with plain set logic here, not
from merge_and_dedupe._apply_cve_rejections. A delta outside the expectation
is a DEFECT, not noise.

    python scripts/audit/rejected_cve_delta.py --before-ref origin/main \
        --out-json docs/audits/rejected-cve-reconcile-delta-2026-10-03.json

Importable: ``compute(before, after, rejected)`` is pure and is exercised by
tests/test_rejected_cve_delta.py, including against deliberately corrupted
input (the check must be seen to fire).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Fields a rejection may legitimately touch on an affected entry. `updated`
# bumps because status/flag are content fields (invariant 4); `last_seen`
# mirrors `updated`.
AFFECTED_ALLOWED = {"status", "status_reason", "rejected_cve_ids", "updated", "last_seen"}
HEADER_ALLOWED = {"generated", "incident_count", "retracted_count"}


def expected_sets(before_entries: list[dict], rejected: set[str]) -> tuple[set[str], set[str]]:
    """(retract_ids, flag_only_ids), by plain set logic over the BEFORE data."""
    retract, flag = set(), set()
    for e in before_entries:
        cves = set(e.get("cve_ids") or [])
        if not cves & rejected:
            continue
        if cves <= rejected and set(e.get("source_ids") or []) <= rejected:
            retract.add(e["id"])
        else:
            flag.add(e["id"])
    return retract, flag


def compute(before: dict, after: dict, rejected: set[str]) -> dict:
    b = {e["id"]: e for e in before["incidents"]}
    a = {e["id"]: e for e in after["incidents"]}
    retract, flag = expected_sets(before["incidents"], rejected)
    affected = retract | flag
    out: dict = {"defects": [], "entries": {}, "id_set": {}, "header": {}}

    out["id_set"] = {
        "before": len(b), "after": len(a),
        "added": sorted(set(a) - set(b)), "removed": sorted(set(b) - set(a)),
    }
    for i in out["id_set"]["added"] + out["id_set"]["removed"]:
        out["defects"].append(f"{i}: entry added/removed (invariant 3: nothing may be deleted or minted)")

    for k in sorted((set(before) | set(after)) - {"incidents"}):
        if before.get(k) != after.get(k):
            out["header"][k] = {"before": before.get(k), "after": after.get(k)}
            if k not in HEADER_ALLOWED:
                out["defects"].append(f"header field {k!r} changed unexpectedly")

    for i in sorted(set(b) & set(a)):
        changed = {}
        for f in sorted(set(b[i]) | set(a[i])):
            if b[i].get(f) != a[i].get(f):
                changed[f] = {"before": b[i].get(f), "after": a[i].get(f)}
        if not changed:
            continue
        out["entries"][i] = changed
        if i not in affected:
            out["defects"].append(f"{i}: unaffected entry changed {sorted(changed)}")
            continue
        extra = set(changed) - AFFECTED_ALLOWED
        if extra:
            out["defects"].append(f"{i}: unexpected field(s) changed {sorted(extra)}")
        want_status = "retracted" if i in retract else None
        if a[i].get("status") != want_status:
            out["defects"].append(f"{i}: status {a[i].get('status')!r}, expected {want_status!r}")
        if sorted(a[i].get("rejected_cve_ids") or []) != sorted(set(a[i].get("cve_ids") or []) & rejected):
            out["defects"].append(f"{i}: rejected_cve_ids does not equal cve_ids ∩ REJECTED")
    for i in sorted(affected):
        if i in a and i not in out["entries"]:
            out["defects"].append(f"{i}: expected to change (rejected CVE) but did not")

    n_ret = sum(1 for e in a.values() if e.get("status") == "retracted")
    out["counts"] = {
        "expected_retracted": len(retract), "expected_flag_only": len(flag),
        "retracted_after": n_ret,
        "incident_count_before": before.get("incident_count"),
        "incident_count_after": after.get("incident_count"),
        "retracted_count_after": after.get("retracted_count"),
        "entries_changed": len(out["entries"]),
        "fields_changed": sum(len(v) for v in out["entries"].values()),
    }
    if n_ret != len(retract):
        out["defects"].append(f"retracted after build {n_ret} != expected {len(retract)}")
    if after.get("incident_count", 0) + n_ret != len(a):
        out["defects"].append("incident_count + retracted != len(incidents)")
    out["expected"] = {"retract": sorted(retract), "flag_only": sorted(flag)}
    return out


def _git_show(ref: str, path: str) -> dict:
    raw = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True,
                         capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="origin/main")
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()
    snap = json.loads((ROOT / "ingest" / "cve_rejections.json").read_text(encoding="utf-8"))
    rejected = {c for c, r in snap["states"].items() if r["state"] == "REJECTED"}
    before = _git_show(args.before_ref, "data/incidents.json")
    after = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    res = compute(before, after, rejected)

    # Secondary surfaces: stats.json, min.json id-set, id_deprecations.
    sb, sa = _git_show(args.before_ref, "data/stats.json"), json.loads(
        (ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    res["stats_json"] = {k: {"before": sb.get(k), "after": sa.get(k)}
                         for k in sorted(set(sb) | set(sa)) if sb.get(k) != sa.get(k)}
    mb = {e["id"] for e in _git_show(args.before_ref, "data/incidents.min.json")["incidents"]}
    ma = {e["id"] for e in json.loads(
        (ROOT / "data" / "incidents.min.json").read_text(encoding="utf-8"))["incidents"]}
    res["min_json_id_set_equal"] = mb == ma
    db = _git_show(args.before_ref, "data/id_deprecations.json")
    da = json.loads((ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8"))
    res["id_deprecations_unchanged"] = db == da
    if mb != ma:
        res["defects"].append("incidents.min.json id set changed")
    if db != da:
        res["defects"].append("id_deprecations.json changed (no ID is retired or minted here)")
    Path(args.out_json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"entries changed {res['counts']['entries_changed']}, fields changed "
          f"{res['counts']['fields_changed']}, defects {len(res['defects'])}")
    for d in res["defects"]:
        print("  DEFECT:", d)
    return 1 if res["defects"] else 0


if __name__ == "__main__":
    sys.exit(main())
