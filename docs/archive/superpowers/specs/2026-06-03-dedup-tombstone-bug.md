# Core dedupe bug: content lost when merging into tombstoned entries

**Date:** 2026-06-03
**Status:** Fixed (2026-06-10) — `_live()` resolution + loop-until-stable reindex in `dedupe_entries`; regression tests in `tests/test_merge_and_dedupe.py`. The fix recovered 24 previously-lost incidents (+39 CVEs, +210 source_ids) from the real dataset.
**Discovered by:** the retain-on-drop work (see
`2026-06-01-retain-on-drop-design.md`), which amplified this latent bug.

## Summary

`scripts/merge_and_dedupe.py`'s dedupe can **silently drop incident content**
(observed: 17 CVEs across 6 incidents during a retention build) by merging a
new entry into an entry that was already *tombstoned* (absorbed by a transitive
merge). The dead entry is discarded in step 4, taking the just-merged content
with it.

This is a **pre-existing** core-dedupe defect — reproducible without the
retention feature — but it is **dormant on current real ingest data** (the
committed build is stable at 7725 with no loss). It only manifests when many
key-sharing records flow through dedupe, which the (since-reworked) "re-feed
priors through dedupe" approach did at scale.

## Root cause

The dedupe keeps four indexes: `by_cve`, `by_src`, `by_url`, `by_title`. When
`_reindex` finds a key already owned by a different deduped entry, it does a
transitive merge: `merge_into(target, other)` then `other["_tombstoned"] = True`.
Two staleness problems leave indexes pointing at tombstoned entries:

1. **`by_title` is never updated by `_reindex`** (it only touches
   `by_cve`/`by_src`/`by_url`). After `other` is tombstoned, `by_title[tk]` can
   still point to it.
2. **`_reindex` iterates a stale snapshot.** `for c in target.get("cve_ids")`
   captures the list object once; `merge_into` reassigns `target["cve_ids"]` to
   a new list, so keys newly absorbed from `other` are **not** re-claimed to
   `target` in that pass. Those keys keep pointing at the now-tombstoned `other`.

Later, an entry whose only match is one of these stale keys takes the
`merge_into(<dead entry>, e)` path (the dedupe branches don't check
`_tombstoned`). `e` is not appended to `deduped`; the dead entry is dropped in
step 4 → `e`'s content is lost.

Evidence from a retention build (diagnostic instrumentation, since reverted):
```
by_title -> tombstoned: 153
by_cve   -> tombstoned: 49
by_src   -> tombstoned: 226
by_url   -> tombstoned: 807
orphaned-tombstoned entries w/ lost CVEs: 4–6 (varied run to run → non-idempotent)
```

## Minimal reproduction (no retention)

Four ingest entries, in order:

- `A {source_id: S-A, title: "Alpha", refs:[urlA]}` → new survivor.
- `B {source_id: S-B, cve: [CVE-7001], title: "Beta", refs:[urlB]}` → new survivor.
- `C {source_id: [S-A, S-B], title: "Gamma", refs:[urlC]}` → merges into A via
  `S-A`; `_reindex(A)` then claims `S-B` (owned by B) → **B tombstoned**, but
  `by_title["beta"]` still points at B.
- `D {source_id: S-D, cve: [CVE-7002], title: "Beta"}` → no cve/src/url hit;
  title hit `by_title["beta"]` = tombstoned B → `merge_into(B, D)` → B dropped →
  **CVE-7002 lost.**

A test asserting `CVE-7002` is present in the output **fails** on current code.

## Proposed fix (for the PR)

Make dedupe never operate on a tombstoned entry by resolving to the live
absorber:

1. When tombstoning, record the absorber: `other["_merged_into"] = target`.
2. Add `_live(entry)`: follow `_merged_into` while `_tombstoned`, with a cycle
   guard, returning the live root.
3. In every dedupe branch, resolve the hit with `_live(...)` before
   `merge_into`. In the title branch, resolve before the year check.
4. In `_claim`, resolve `other` via `_live` before comparing/merging, and make
   `_reindex` re-claim against `target`'s **current** keys until the key set
   stops growing (loop-until-stable), so absorbed keys are always re-pointed at
   the live target.

### Tests
- The 4-entry fixture above (asserts no CVE lost) — must fail before, pass after.
- Idempotency: building twice over a fixture that forces transitive merges is
  byte-stable.
- Full real-data rebuild: `incident_count` does not drop, no CVE set shrinks,
  and the build stays idempotent + cross-day stable (drift check green). Any
  change to the committed baseline must be explainable as **recovered**
  previously-lost content, not new loss.

## Why deferred

Fixing the central dedupe is delicate and could shift existing groupings; it
deserves its own focused PR with full determinism re-validation, rather than
being bundled into the retain-on-drop change (which is safe on its own because
its top-up bypasses dedupe entirely).
