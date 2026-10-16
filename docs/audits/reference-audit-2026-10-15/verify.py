#!/usr/bin/env python
"""D130-2 per-ID verification of a built data/incidents.json against the spec (independent of the build path).

  python -I verify.py [path/to/incidents.json]      # default: data/incidents.json; exit 0 = all checks hold

Checks, per ID (not aggregates): every UNVERIFIED target is status=unverified with the exact status_reason; no other row is
unverified; every FIXED row is quality_tier=auto, holds exactly the expected reference list and the spec text; every row of
UNCHANGED/DEFERRED/DEFERRED_LABEL is byte-identical to base 589376db; every row outside the 30 is identical to base apart from
nothing; ID set and count equal; envelope incident_count/unverified_count move by exactly the unverified count.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import d1302_spec as S  # noqa: E402

path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data" / "incidents.json"
base_doc = json.loads(subprocess.run(["git", "show", "589376db:data/incidents.json"], cwd=REPO, check=True,
                                     capture_output=True).stdout.decode("utf-8"))
new_doc = json.loads(path.read_text(encoding="utf-8"))
b = {e["id"]: e for e in base_doc["incidents"]}
n = {e["id"]: e for e in new_doc["incidents"]}
fails = []


def chk(ok, msg):
    if not ok:
        fails.append(msg)


chk(set(b) == set(n) and len(b) == len(n), "ID set / entry count differ from base")
unv = set(S.UNVERIFIED)
for rid in unv:
    r = n[rid]
    chk(r.get("status") == "unverified", f"{rid} is not unverified")
    chk(r.get("status_reason") == {"code": "no-confirmed-source", "as_of": S.AS_OF}, f"{rid} status_reason wrong")
    chk(r["references"] == b[rid]["references"] and r["quality_tier"] == b[rid]["quality_tier"], f"{rid} refs/tier touched")
chk({i for i, r in n.items() if r.get("status") == "unverified"} == unv, "the set of unverified rows is not exactly the 10 targets")
for rid, sp in S.FIXED.items():
    r, o = n[rid], b[rid]
    exp, seen = [], set()
    for ref in o["references"]:
        if ref["url"] in sp["replace"]:
            for u in sp["replace"][ref["url"]]:
                if u not in seen:
                    exp.append(S.NEW_REFS[u]); seen.add(u)
        else:
            exp.append(ref)
    chk(r["references"] == exp, f"{rid} references differ from expected")
    chk(r["quality_tier"] == "auto", f"{rid} not demoted to auto")
    chk(r["description"] == sp["description"], f"{rid} description differs from spec")
    chk(r.get("status") is None, f"{rid} unexpectedly has a status")
    for f in ("title", "corpus"):
        if sp.get(f) or f in sp.get("pin", {}):
            chk(r[f] == (sp.get(f) or sp["pin"][f]), f"{rid} {f} wrong")
    for ref in r["references"]:
        chk(ref["url"] in S.EVIDENCE, f"{rid} keeps {ref['url']} with no this-session fetch evidence")
    for u in (x for olds in sp["replace"].values() for x in olds):
        chk(any(ref["url"] == u for ref in r["references"]), f"{rid} lacks {u}")
    for old in sp["replace"]:
        chk(all(ref["url"] != old for ref in r["references"]), f"{rid} still carries {old}")
for rid in list(S.UNCHANGED) + list(S.DEFERRED) + list(S.DEFERRED_LABEL):
    chk(n[rid] == b[rid], f"{rid} (not-to-change) differs from base")
touched = set(S.FIXED) | unv
for rid in set(b) - touched:
    chk(n[rid] == b[rid], f"{rid} outside the 22 touched rows differs from base")
chk(new_doc["incident_count"] == base_doc["incident_count"] - len(unv), "incident_count did not drop by exactly the unverified rows")
chk(new_doc["unverified_count"] == len(unv), "unverified_count != number of unverified rows")
print("FAIL" if fails else "OK", len(fails))
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
