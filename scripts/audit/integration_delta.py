"""Field-level before/after delta for the v2.12.0 integration (working
agreement 2): origin/main's data/incidents.json vs the build of main + WS4-T2
(rejected-CVE reconcile) + wave 1-2 ingest. Expected composition: all new IDs
are wave12; the only changed existing entries are the 29 retracted + 6 flagged
from WS4-T2, touching only status fields; nothing else moves.

The expected sets are derived here from the committed CVE-state snapshot
(ingest/cve_rejections.json) and the BEFORE data with plain set logic, and
cross-checked against the two branches' own committed audits; none of it is
read from merge_and_dedupe. The script also proves the check fires by
mutating one field in a copy of the after-data.

    python scripts/audit/integration_delta.py --before-ref origin/main \
        --out-json docs/audits/v2.12.0-integration-delta-2026-10-04.json \
        --out-md docs/audits/v2.12.0-integration-delta-2026-10-04.md
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WS42_FIELDS = {"status", "status_reason", "rejected_cve_ids", "updated", "last_seen"}
HEADER_OK = {"generated", "incident_count", "retracted_count"}


def expected_sets(before_entries, rejected):
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


def compute(before, after, rejected, wave12_ids):
    b = {e["id"]: e for e in before["incidents"]}
    a = {e["id"]: e for e in after["incidents"]}
    retract, flag = expected_sets(before["incidents"], rejected)
    affected = retract | flag
    new_ids = set(a) - set(b)
    out = {"defects": [], "changes": []}
    removed = sorted(set(b) - set(a))
    for i in removed:
        out["defects"].append(f"{i}: removed (invariant 3)")
    if new_ids != wave12_ids:
        out["defects"].append(
            f"new-ID set != wave12 audit new_ids (extra {sorted(new_ids - wave12_ids)[:5]}, "
            f"missing {sorted(wave12_ids - new_ids)[:5]})")
    cls = {"wave12": len(new_ids), "ws4-t2": 0, "unintended": 0}
    changed_ids = set()
    for i in sorted(set(a) & set(b)):
        fields = sorted(k for k in set(a[i]) | set(b[i]) if a[i].get(k) != b[i].get(k))
        if not fields:
            if i in affected:
                out["defects"].append(f"{i}: expected WS4-T2 change absent")
            continue
        changed_ids.add(i)
        for f in fields:
            if i in affected and f in WS42_FIELDS:
                c = "ws4-t2"
            else:
                c = "unintended"
                out["defects"].append(f"{i}.{f}: unintended change")
            cls[c] += 1
            out["changes"].append({"id": i, "field": f, "class": c,
                                   "before": b[i].get(f), "after": a[i].get(f)})
    for i in retract:
        if a[i].get("status") != "retracted":
            out["defects"].append(f"{i}: expected retracted, got {a[i].get('status')}")
    for i in flag:
        if a[i].get("status") == "retracted" or not a[i].get("rejected_cve_ids"):
            out["defects"].append(f"{i}: expected flagged-not-retracted")
    for i in new_ids:
        if a[i].get("status") == "retracted":
            out["defects"].append(f"{i}: new wave12 entry is retracted")
        if set(a[i].get("cve_ids") or []) & rejected:
            out["defects"].append(f"{i}: new wave12 entry carries a REJECTED CVE")
    hdr = {}
    for k in sorted((set(before) | set(after)) - {"incidents"}):
        if before.get(k) != after.get(k):
            hdr[k] = {"before": before.get(k), "after": after.get(k)}
            if k not in HEADER_OK:
                out["defects"].append(f"header {k} changed")
    ic = sum(1 for e in after["incidents"] if e.get("status") != "retracted")
    rc = sum(1 for e in after["incidents"] if e.get("status") == "retracted")
    if (after.get("incident_count"), after.get("retracted_count")) != (ic, rc):
        out["defects"].append(
            f"header counts {after.get('incident_count')}/{after.get('retracted_count')} != derived {ic}/{rc}")
    out["classification"] = cls
    out["header"] = hdr
    out["counts"] = {
        "entries_before": len(b), "entries_after": len(a),
        "added": len(new_ids), "removed": len(removed),
        "expected_retract": len(retract), "expected_flag": len(flag),
        "incident_count_derived": ic, "retracted_count_derived": rc,
        "existing_entries_changed": len(changed_ids),
    }
    out["retract_ids"] = sorted(retract)
    out["flag_ids"] = sorted(flag)
    out["new_ids_range"] = [min(new_ids), max(new_ids)] if new_ids else None
    return out


def render_md(r):
    c = r["counts"]
    L = ["# v2.12.0 integration delta (2026-10-04)", "",
         "Generated by `scripts/audit/integration_delta.py`; machine twin "
         "`v2.12.0-integration-delta-2026-10-04.json`. "
         f"Before = `{r['before_ref']}` (`f2d24448`) `data/incidents.json`; after = integrated "
         "`release/v2.12.0` build. Expected sets derived from `ingest/cve_rejections.json` plus the "
         "BEFORE data, cross-checked against both branches' committed audits.", "",
         f"**Defects: {len(r['defects'])}.**", "", "## Counts", "", "| measure | value |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in c.items()]
    cl = r["classification"]
    L += ["", "## Classification of changes", "", "| class | meaning | count |", "|---|---|---|",
          f"| wave12 | new entries (IDs {r['new_ids_range'][0]} .. {r['new_ids_range'][1]}) | {cl['wave12']} entries |",
          f"| ws4-t2 | field changes on retracted/flagged entries | {cl['ws4-t2']} fields on {c['existing_entries_changed']} entries |",
          f"| unintended | anything else | {cl['unintended']} |", "",
          "## Header", "", "| key | before | after |", "|---|---|---|"]
    L += [f"| {k} | {v['before']} | {v['after']} |" for k, v in r["header"].items()]
    by = {}
    for ch in r["changes"]:
        by[ch["field"]] = by.get(ch["field"], 0) + 1
    L += ["", "## WS4-T2 field changes by field", "", "| field | entries |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in sorted(by.items())]
    L += ["", f"Retracted ({len(r['retract_ids'])}): " + ", ".join(r["retract_ids"]), "",
          f"Flagged ({len(r['flag_ids'])}): " + ", ".join(r["flag_ids"]), "",
          "## Check fires", "",
          "A `title` mutation on an untouched existing entry, and a `severity` mutation on a retracted "
          "entry, each in a copy of the after-data, are reported as:", "",
          "```", json.dumps(r["fires"], indent=1), "```", "",
          "Per-field before/after values for every change are in the JSON twin (`changes`).", ""]
    if r["defects"]:
        L += ["## Defects", ""] + [f"- {d}" for d in r["defects"]]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="origin/main")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    args = ap.parse_args()
    raw = subprocess.run(["git", "show", f"{args.before_ref}:data/incidents.json"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    before = json.loads(raw.decode("utf-8"))
    after = json.load(open(ROOT / "data/incidents.json", encoding="utf-8"))
    st = json.load(open(ROOT / "ingest/cve_rejections.json", encoding="utf-8"))["states"]
    rejected = {c for c, v in st.items() if v.get("state") == "REJECTED"}
    w12 = set(json.load(open(ROOT / "docs/audits/wave12-ingest-delta-2026-10-03.json"))["new_ids"])
    res = compute(before, after, rejected, w12)
    ws = json.load(open(ROOT / "docs/audits/rejected-cve-reconcile-delta-2026-10-03.json"))
    if set(ws["entries"]) != set(res["retract_ids"]) | set(res["flag_ids"]):
        res["defects"].append("WS4-T2 audit entry set != independently derived retract|flag set")
    # Prove the check fires: mutate one field in copies of the after-data.
    affected = set(res["retract_ids"]) | set(res["flag_ids"])
    before_ids = {e["id"] for e in before["incidents"]}
    m = copy.deepcopy(after)
    next(e for e in m["incidents"] if e["id"] in before_ids and e["id"] not in affected)["title"] += " x"
    d1 = compute(before, m, rejected, w12)["defects"]
    m2 = copy.deepcopy(after)
    next(e for e in m2["incidents"] if e["id"] in set(res["retract_ids"]))["severity"] = "mutated"
    d2 = compute(before, m2, rejected, w12)["defects"]
    res["fires"] = {"title_on_untouched_entry": d1, "severity_on_retracted_entry": d2}
    if not (d1 and d2):
        res["defects"].append("SELFTEST: mutation did not fire")
    res["before_ref"] = args.before_ref
    if args.out_json:
        Path(args.out_json).write_text(
            json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        Path(args.out_md).write_text(render_md(res), encoding="utf-8")
    print(json.dumps({"counts": res["counts"], "classification": res["classification"],
                      "header": res["header"], "defects": res["defects"][:10],
                      "fires": res["fires"]}, indent=1))
    return 1 if res["defects"] else 0


if __name__ == "__main__":
    sys.exit(main())
