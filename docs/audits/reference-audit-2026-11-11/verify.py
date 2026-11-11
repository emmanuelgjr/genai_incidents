#!/usr/bin/env python
"""D130-3a per-ID verification of the built data/incidents.json against the spec. Independent of the build path: it computes the
expected references/fields from the BASE rows (git show 64109452) and compares row by row.

  python -I verify.py [path/to/incidents.json]      # exit 0 = every check holds

Checks: ID set/count/order; every REMOVE row holds exactly the base references minus the listed URLs (order kept), is
quality_tier=auto and carries no status; every REPLACE row holds exactly the one new reference and the spec text and
no longer carries the old URL; every UNVERIFIED row has the exact status/status_reason with references and tier untouched;
no unverified row beyond the 10 base ones plus these 2; every other row is byte-identical to base; envelope counts move by
exactly the unverified rows; every URL written into the corpus has fetch evidence in the committed evidence file.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "reference-audit-2026-10-15"))
import d1303a_spec as S  # noqa: E402

import kept_refs as K  # noqa: E402

path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data" / "incidents.json"
kept_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "kept-evidence-2026-11-11.json"
base = json.loads(subprocess.run(["git", "show", f"{S.BASE}:data/incidents.json"], cwd=REPO, check=True,
                                 capture_output=True).stdout.decode("utf-8"))
new = json.loads(path.read_text(encoding="utf-8"))
b = {e["id"]: e for e in base["incidents"]}
n = {e["id"]: e for e in new["incidents"]}
fails = []


def chk(ok, msg):
    if not ok:
        fails.append(msg)


chk([e["id"] for e in base["incidents"]] == [e["id"] for e in new["incidents"]], "ID list/order differs from base")
for rid, urls in S.REMOVE.items():
    exp = [r for r in b[rid]["references"] if r["url"] not in urls]
    chk(n[rid]["references"] == exp, f"{rid} references differ from base minus {urls}")
    chk(n[rid]["quality_tier"] == "auto", f"{rid} not demoted to auto")
    chk(n[rid].get("status") == b[rid].get("status"), f"{rid} status changed")
    for u in urls:
        chk(all(r["url"] != u for r in n[rid]["references"]), f"{rid} still carries {u}")
    if rid in S.DEFERRED6:
        chk(n[rid]["tier"] == ("landmark" if (n[rid].get("aiid_id") or n[rid].get("corpus") == "ai-harm") else "feed"),
            f"{rid} tier not derived from the demotion")
    if rid in ("INC-04207", "INC-02471", "INC-02871"):
        chk("discovery_method" not in n[rid], f"{rid} still has discovery_method")
for rid, sp in S.REPLACE.items():
    r = n[rid]
    chk(r["references"] == [sp["ref"]], f"{rid} references are not exactly the one new reference")
    chk(r["quality_tier"] == "auto", f"{rid} not demoted to auto")
    for f in ("title", "description", "affected"):
        chk(r[f] == (sp.get(f) or b[rid][f]), f"{rid} {f} wrong")
    chk(all(x["url"] != sp["old"] for x in r["references"]), f"{rid} still carries {sp['old']}")
for rid in S.UNVERIFIED:
    r = n[rid]
    chk(r.get("status") == "unverified", f"{rid} is not unverified")
    chk(r.get("status_reason") == {"code": "no-confirmed-source", "as_of": S.AS_OF}, f"{rid} status_reason wrong")
    chk(r["references"] == b[rid]["references"] and r["quality_tier"] == b[rid]["quality_tier"], f"{rid} refs/tier touched")
base_unv = {i for i, e in b.items() if e.get("status") == "unverified"}
chk({i for i, e in n.items() if e.get("status") == "unverified"} == base_unv | set(S.UNVERIFIED), "unverified set is not base + targets")
targets = set(S.REMOVE) | set(S.REPLACE) | set(S.UNVERIFIED)
for rid in set(b) - targets:
    chk(n[rid] == b[rid], f"{rid} outside the {len(targets)} targets differs from base")
for rid in S.KEPT:
    chk(n[rid] == b[rid], f"{rid} (examined, not changed) differs from base")
d = len(S.UNVERIFIED)
chk(new["incident_count"] == base["incident_count"] - d, "incident_count did not drop by exactly the new unverified rows")
chk(new["unverified_count"] == base["unverified_count"] + d, "unverified_count did not rise by exactly the new unverified rows")
ev = json.loads((HERE / "fetch-evidence-2026-11-11.json").read_text(encoding="utf-8"))
ok_urls = {p["url"] for p in ev["checked_pages"] if p["status"] == 200}
for rid, sp in S.REPLACE.items():
    chk(sp["ref"]["url"] in ok_urls, f"{rid} new reference {sp['ref']['url']} has no 200 fetch evidence")
# kept-reference evidence (foreman rule C): <=15 kept refs -> every one has a record; larger -> exactly the deterministic sample
kept = json.loads(kept_path.read_text(encoding="utf-8"))
chk(set(kept["rows"]) == set(S.REMOVE), "kept evidence rows != the remove rows")
tl = {"evidenced": 0, "dead-or-blocked": 0, "page-without-token": 0}
for rid in S.REMOVE:
    refs = n[rid]["references"]
    rec = kept["rows"].get(rid)
    if rec is None:
        continue
    how, idx = K.selection(rid, refs)
    want = [refs[i]["url"] for i in idx]
    chk(rec["kept_references"] == len(refs), f"{rid} kept_references != built row")
    chk(rec["method"] == how, f"{rid} method {rec['method']} != {how}")
    chk([x["url"] for x in rec["references"]] == want, f"{rid} evidenced URLs differ from the {how} selection")
    if len(refs) <= 15:
        chk({x["url"] for x in rec["references"]} == {r["url"] for r in refs}, f"{rid} a kept reference has no evidence")
    for x in rec["references"]:
        chk(x["outcome"] in tl and x["status"] is not None and x["fetched_at"], f"{rid} bad record {x['url']}")
        chk((x["outcome"] == "evidenced") == (x["status"] == 200 and bool(x["tokens_matched"])), f"{rid} outcome inconsistent {x['url']}")
        if x["outcome"] in tl:
            tl[x["outcome"]] += 1
chk({k: kept["tally"][k] for k in tl} == tl, "tally does not equal the per-reference outcomes")
print("FAIL" if fails else "OK", len(fails))
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
