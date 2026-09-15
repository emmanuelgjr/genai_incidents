"""WS4-T10 BOUNCE #1: full per-entity Phase B delta.

Produces the artifact committed at
docs/audits/WS4-T10-phaseB-delta-2026-09-15.json. Rerun this script any
time the normalizer or its blocklist changes, per working agreement 6
("prove it fires" applies to a re-run too, not just the first one) —
build_delta.py was itself proven to fire on a deliberately corrupted copy
of a control build (1 title edit, 1 downward severity edit, 1 dropped
reference, 1 gained reference, 1 removed row, 1 injected fake row — all 6
caught, 0 false negatives) before being trusted on the real before/after
(see the WS4-T10 BOUNCE #1 report for the paired output).

Reads two already-built data/incidents.json + data/id_deprecations.json
pairs (control = unchanged code at `main`, fixed = this branch's code) and
produces one JSON artifact with: id sets, per-field changes on ALL common
rows (including last_seen), severity changes with direction,
title/description swaps, the FULL split population (not just a sample)
with per-row survivor-continuity (does the id that keeps its old number
also keep its old title?), corpus-wide reference-URL gains/losses, and
the new deprecation(s).

Usage, from two detached scratch worktrees (never `git stash` — see
CLAUDE.md's git-safety rule for this session). **Pin control to `eeb7ca9c`
(the commit before this fix), not the symbolic `main`** (WS4-T10 attempt 3
advisory A3): once this branch merges, `main` will itself contain the fix,
so it stops being a valid "unfixed" baseline for this comparison.
    git worktree add --detach <control_dir> eeb7ca9c
    git worktree add --detach <fixed_dir> <this-branch's-commit>
    # in each: python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
    python scripts/audit/ws4t10_phaseb_delta.py <control_dir> <fixed_dir> \
        docs/audits/WS4-T10-phaseB-delta-2026-09-15.json
    git worktree remove <control_dir> --force
    git worktree remove <fixed_dir> --force
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict


def commit_of(d):
    try:
        return subprocess.run(
            ["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return None


def load_incidents(d):
    data = json.loads(open(f"{d}/data/incidents.json", encoding="utf-8").read())
    return {e["id"]: e for e in data["incidents"]}


def load_deprecations(d):
    return json.loads(open(f"{d}/data/id_deprecations.json", encoding="utf-8").read())["deprecations"]


def norm(v):
    if isinstance(v, list):
        try:
            return sorted(json.dumps(x, sort_keys=True) for x in v)
        except TypeError:
            return v
    return v


SEVERITY_ORDER = ["Info", "Low", "Medium", "High", "Critical"]


def main():
    control_dir, fixed_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    old = load_incidents(control_dir)
    new = load_incidents(fixed_dir)
    old_dep = load_deprecations(control_dir)
    new_dep = load_deprecations(fixed_dir)

    old_ids, new_ids = set(old), set(new)
    common = old_ids & new_ids
    new_only = sorted(new_ids - old_ids)
    gone = sorted(old_ids - new_ids)

    # --- per-field changes on ALL common rows, including last_seen -------
    all_fields = set()
    for eid in common:
        all_fields |= set(old[eid]) | set(new[eid])
    # `added` is invariant-4-immutable by construction; excluded because a
    # change there would itself be a defect, not a tracked field delta.
    all_fields.discard("added")

    common_changed = []
    severity_changes = []
    title_desc_changes = []
    invariant4_violations = {"bumped_no_content_change": [], "content_change_no_bump": []}
    for eid in sorted(common):
        o, n = old[eid], new[eid]
        changed = sorted(f for f in all_fields if f != "updated" and norm(o.get(f)) != norm(n.get(f)))
        updated_changed = o.get("updated") != n.get("updated")
        if changed:
            common_changed.append({"id": eid, "fields_changed": changed})
        if updated_changed and not changed:
            invariant4_violations["bumped_no_content_change"].append(eid)
        if changed and not updated_changed:
            invariant4_violations["content_change_no_bump"].append(eid)
        if "severity" in changed:
            os_, ns_ = o.get("severity"), n.get("severity")
            try:
                oi, ni = SEVERITY_ORDER.index(os_), SEVERITY_ORDER.index(ns_)
                direction = "up" if ni > oi else ("down" if ni < oi else "same")
            except ValueError:
                direction = "unknown"
            severity_changes.append({"id": eid, "old": os_, "new": ns_, "direction": direction})
        if "title" in changed or "description" in changed:
            title_desc_changes.append({
                "id": eid,
                "title_changed": "title" in changed,
                "description_changed": "description" in changed,
                "old_title": o.get("title"), "new_title": n.get("title"),
                "old_description_snip": (o.get("description") or "")[:200],
                "new_description_snip": (n.get("description") or "")[:200],
            })

    # --- split population: EVERY old id whose members now resolve to >1 --
    src_to_old, src_to_new = {}, {}
    for e in old.values():
        for s in e.get("source_ids") or []:
            src_to_old[s] = e["id"]
    for e in new.values():
        for s in e.get("source_ids") or []:
            src_to_new[s] = e["id"]

    old_to_new_ids = defaultdict(set)
    for s, oid in src_to_old.items():
        nid = src_to_new.get(s)
        if nid:
            old_to_new_ids[oid].add(nid)
    split_rows = {oid: nids for oid, nids in old_to_new_ids.items() if len(nids) > 1}

    splits = []
    for oid in sorted(split_rows):
        nids = split_rows[oid]
        o = old[oid]
        old_src_count = len(o.get("source_ids") or [])
        successors = []
        for nid in sorted(nids):
            n = new[nid]
            successors.append({
                "id": nid,
                "title": n.get("title"),
                "source_ids": sorted(n.get("source_ids") or []),
                "source_count": len(n.get("source_ids") or []),
            })
        successors.sort(key=lambda s: -s["source_count"])
        survivor = new.get(oid)  # the successor that literally kept the old id, if any
        survivor_title_same = bool(survivor) and survivor.get("title") == o.get("title")
        survivor_source_fraction = (
            (len(survivor.get("source_ids") or []) / old_src_count) if survivor and old_src_count else None
        )
        splits.append({
            "old_id": oid,
            "old_title": o.get("title"),
            "old_source_count": old_src_count,
            "split_into": len(nids),
            "successors": successors,
            "survivor_id": oid if survivor else None,
            "survivor_title_continuity": survivor_title_same,
            "survivor_source_fraction": survivor_source_fraction,
        })

    continuity_holds = sum(1 for s in splits if s["survivor_title_continuity"])
    continuity_breaks = len(splits) - continuity_holds

    # --- corpus-wide reference URL gains/losses ---------------------------
    def all_refs(d):
        urls = set()
        entries = 0
        for e in d.values():
            for r in e.get("references") or []:
                u = r.get("url")
                if u:
                    urls.add(u)
                    entries += 1
        return urls, entries

    old_urls, old_ref_entries = all_refs(old)
    new_urls, new_ref_entries = all_refs(new)
    gained_urls = sorted(new_urls - old_urls)
    lost_urls = sorted(old_urls - new_urls)

    per_row_ref_gains = []
    for eid in sorted(common):
        o_urls = {r.get("url") for r in (old[eid].get("references") or []) if r.get("url")}
        n_urls = {r.get("url") for r in (new[eid].get("references") or []) if r.get("url")}
        gained = sorted(n_urls - o_urls)
        lost = sorted(o_urls - n_urls)
        if gained or lost:
            per_row_ref_gains.append({"id": eid, "gained": gained, "lost": lost})

    # --- WS4-T10 attempt 3, advisory A1: common rows that GAINED source_ids.
    # Splitting should only ever REMOVE source_ids from a common row (content
    # leaving for a split-off sibling); a common row gaining a source_id it
    # didn't have before is a NEW merge the code change introduced -- worth
    # a name of its own, distinct from the generic per-field change list,
    # because it's exactly the shape of a fresh over-merge (the opposite
    # failure to the one this task exists to fix).
    common_rows_gained_source_ids = []
    for eid in sorted(common):
        o_srcs = set(old[eid].get("source_ids") or [])
        n_srcs = set(new[eid].get("source_ids") or [])
        gained_srcs = sorted(n_srcs - o_srcs)
        if gained_srcs:
            common_rows_gained_source_ids.append({"id": eid, "gained_source_ids": gained_srcs})

    # --- deprecations: full-record comparison, BOTH directions -------------
    # WS4-T10 attempt 3, advisory A1: the prior version's dep_key ignored
    # `date` and only checked one direction (new-only), so it could not
    # evidence invariant 9 (append-only, never edited/removed) -- a
    # deletion or in-place edit of an EXISTING record was invisible to it.
    # Compares the FULL record (from, into, reason, date) as the identity,
    # per the BOUNCE report: a historical entry's `date` is stable across
    # rebuilds (it's carried through from the prior incidents.json/
    # id_deprecations.json verbatim, never re-stamped -- only a genuinely
    # NEW entry gets today's date, see the A4 note below on that).
    def dep_key_full(d):
        return (d.get("from"), d.get("into"), d.get("reason"), d.get("date"))

    old_dep_by_key = {dep_key_full(d): d for d in old_dep}
    new_dep_by_key = {dep_key_full(d): d for d in new_dep}
    deleted_or_modified_keys = sorted(set(old_dep_by_key) - set(new_dep_by_key), key=str)
    deleted_or_modified = [old_dep_by_key[k] for k in deleted_or_modified_keys]
    new_only_deps = [new_dep_by_key[k] for k in sorted(set(new_dep_by_key) - set(old_dep_by_key), key=str)]
    # WS4-T10 attempt 3, advisory A4: any record in `new_only_deps` was
    # minted with today's wall-clock date (merge_and_dedupe.py's
    # `today_str`), so THIS artifact reproduces byte-for-byte only when
    # regenerated on the same UTC day as originally run -- documented
    # here rather than silently varying; `new_deprecations_dates_are_build_day`
    # names which field is date-volatile so a rerun's own diff doesn't
    # get mistaken for a real change.
    new_deprecations_build_dates = sorted({d.get("date") for d in new_only_deps if d.get("date")})

    result = {
        "control_commit": commit_of(control_dir), "fixed_commit": commit_of(fixed_dir),
        "id_sets": {
            "old_count": len(old_ids), "new_count": len(new_ids),
            "common_count": len(common),
            "new_only_count": len(new_only), "gone_count": len(gone),
            "gone": gone,
        },
        "common_rows_changed_count": len(common_changed),
        "common_rows_changed": common_changed,
        "severity_changes": severity_changes,
        "title_or_description_changes": title_desc_changes,
        "invariant4_violations": invariant4_violations,
        "splits": {
            "count": len(splits),
            "total_successor_rows": sum(s["split_into"] for s in splits),
            "survivor_title_continuity_holds": continuity_holds,
            "survivor_title_continuity_breaks": continuity_breaks,
            "rows": splits,
        },
        "references": {
            "distinct_url_count_old": len(old_urls), "distinct_url_count_new": len(new_urls),
            "reference_entry_count_old": old_ref_entries, "reference_entry_count_new": new_ref_entries,
            "distinct_urls_gained_count": len(gained_urls), "distinct_urls_lost_count": len(lost_urls),
            "distinct_urls_gained": gained_urls, "distinct_urls_lost": lost_urls,
            "per_row_gains_or_losses": per_row_ref_gains,
        },
        "common_rows_gained_source_ids": common_rows_gained_source_ids,
        "new_deprecations": new_only_deps,
        "deprecations_deleted_or_modified": deleted_or_modified,
        "new_deprecations_dates_are_build_day": True,
        "new_deprecations_build_dates": new_deprecations_build_dates,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"old={len(old_ids)} new={len(new_ids)} common={len(common)} new_only={len(new_only)} gone={len(gone)}")
    print(f"common rows changed: {len(common_changed)}")
    print(f"severity changes: {len(severity_changes)}")
    print(f"title/description changes: {len(title_desc_changes)}")
    print(f"invariant4 violations: {invariant4_violations}")
    print(f"splits: {len(splits)} total_successors={sum(s['split_into'] for s in splits)} "
          f"continuity_holds={continuity_holds} continuity_breaks={continuity_breaks}")
    print(f"references: distinct old={len(old_urls)} new={len(new_urls)} "
          f"gained={len(gained_urls)} lost={len(lost_urls)} "
          f"entries old={old_ref_entries} new={new_ref_entries}")
    print(f"common rows gained source_ids: {len(common_rows_gained_source_ids)} "
          f"-> {common_rows_gained_source_ids}")
    print(f"new deprecations: {len(new_only_deps)} -> {new_only_deps}")
    print(f"deprecations DELETED or MODIFIED (invariant 9 check): "
          f"{len(deleted_or_modified)} -> {deleted_or_modified}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
