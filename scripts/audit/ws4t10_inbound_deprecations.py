"""WS4-T10 attempt 3, new defect 1(a): inbound-deprecation table.

For every `id_deprecations.json` entry whose resolved target (following
chains) is one of the 47 split ids from
`docs/audits/WS4-T10-phaseB-delta-2026-09-15.json`, or `INC-07738` (the
Mythos merge), this recovers the retired id's ORIGINAL source_ids from git
history, locates where those sources land in a fixed build, and classifies
the deprecation as STILL_CORRECT (its recorded target still holds ALL of
its sources, and only its sources) or WRONG_AFTER_FIX.

**Identifying which entries need recovery is itself fully mechanical**
(the `find_hits()` step below, driven only by the committed
`id_deprecations.json` and the delta's own split-id list). **Recovering
each hit's ORIGINAL source_ids is NOT** — it requires a human (or a future
enhancement) to find, per retired id, a commit where that id still existed
as its own row, the same archaeology this attempt did by hand (binary
search across commits, checking `git show <sha>:data/incidents.json`).
`LOOKUPS` below is that human-supplied list for THIS run (2026-09-15,
committed corpus); a future rerun (e.g. after an OECD refresh introduces
new over-merges) must extend or replace it after redoing that
archaeology — `find_hits()` will tell you which retired ids need it.

Usage:
    python scripts/audit/ws4t10_inbound_deprecations.py <fixed_dir> \
        docs/audits/WS4-T10-phaseB-delta-2026-09-15.json \
        <out.json>
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict

# retired_id -> commit SHA where that id last existed as its own row,
# found by binary-searching `git show <sha>:data/incidents.json` around
# each entry's `id_deprecations.json` `date`. See the WS4-T10 attempt 3
# report for the full search log.
LOOKUPS = {
    "INC-00497": "8e624ba7",
    "INC-03128": "04d3661f",
    "INC-07771": "6622f2f6",
    "INC-08109": "6622f2f6",
    "INC-08133": "6622f2f6",
    "INC-08139": "de97e9ac",
    "INC-08146": "6622f2f6",
    "INC-08185": "6622f2f6",
}


def find_hits(deprec_list, split_ids):
    """Every `from` id whose deprecation chain resolves into `split_ids`.
    Purely mechanical -- no git history needed for this step."""
    deprec = {}
    for e in deprec_list:
        f, t = e.get("from"), e.get("into")
        if f and t:
            deprec[f] = t

    def resolve_chain(fid):
        seen = set()
        cur = fid
        chain = [cur]
        while cur in deprec and cur not in seen:
            seen.add(cur)
            cur = deprec[cur]
            chain.append(cur)
        return chain

    hits = {}
    for f in deprec:
        chain = resolve_chain(f)
        if chain[-1] in split_ids:
            hits[f] = chain
    return hits


def recover_source_ids(retired_id, sha):
    raw = subprocess.run(
        ["git", "show", f"{sha}:data/incidents.json"], capture_output=True, check=True
    ).stdout
    d = json.loads(raw)
    e = next((x for x in d["incidents"] if x["id"] == retired_id), None)
    if e is None:
        raise ValueError(f"{retired_id} not found at {sha} -- LOOKUPS entry is wrong")
    return e.get("title"), e.get("source_ids") or []


def classify(retired_id, sha, chain, fixed_incidents):
    src_to_new = {}
    for e in fixed_incidents:
        for s in e.get("source_ids") or []:
            src_to_new[s] = e["id"]

    title, srcs = recover_source_ids(retired_id, sha)
    landing = defaultdict(list)
    unmapped = []
    for s in srcs:
        nid = src_to_new.get(s)
        (landing[nid] if nid else unmapped).append(s)
    final_target = chain[-1]
    target_holds_any = final_target in landing
    still_correct = len(landing) == 1 and target_holds_any and not unmapped
    return {
        "retired_id": retired_id,
        "recovered_from_commit": sha,
        "recovered_title": title,
        "recovered_source_count": len(srcs),
        "current_deprecation_chain": chain,
        "current_final_target": final_target,
        "lands_on_new_rows_count": len(landing),
        "lands_on_new_rows": dict(landing),
        "unmapped_sources": unmapped,
        "current_target_still_holds_any_sources": target_holds_any,
        "classification": "STILL_CORRECT" if still_correct else "WRONG_AFTER_FIX",
    }


def main():
    fixed_dir, delta_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    delta = json.loads(open(delta_path, encoding="utf-8").read())
    split_ids = {s["old_id"] for s in delta["splits"]["rows"]}
    split_ids.add("INC-07738")  # the merged-away Mythos id, not a split but a retired intact id

    deprec_list = json.loads(
        open(f"{fixed_dir}/data/id_deprecations.json", encoding="utf-8").read()
    )["deprecations"]
    hits = find_hits(deprec_list, split_ids)

    missing_lookups = sorted(set(hits) - set(LOOKUPS))
    if missing_lookups:
        print(f"[FATAL] {len(missing_lookups)} inbound deprecation(s) resolve into a split id "
              f"but have no LOOKUPS entry: {missing_lookups}. Recover their source commit via "
              "git history (see this script's docstring) and add them to LOOKUPS before rerunning.")
        sys.exit(1)
    extra_lookups = sorted(set(LOOKUPS) - set(hits))
    if extra_lookups:
        print(f"[warn] LOOKUPS has {len(extra_lookups)} entr(ies) that no longer resolve into a "
              f"split id (stale from a prior run?): {extra_lookups}")

    fixed_incidents = json.loads(
        open(f"{fixed_dir}/data/incidents.json", encoding="utf-8").read()
    )["incidents"]

    results = [
        classify(retired_id, LOOKUPS[retired_id], chain, fixed_incidents)
        for retired_id, chain in sorted(hits.items())
    ]

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    wrong = [r for r in results if r["classification"] == "WRONG_AFTER_FIX"]
    print(f"{len(results)} inbound deprecations resolve into a split id / INC-07738")
    print(f"{len(wrong)} WRONG_AFTER_FIX: {[r['retired_id'] for r in wrong]}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
