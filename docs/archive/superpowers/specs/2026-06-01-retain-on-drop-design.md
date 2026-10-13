# Retain-on-drop for the genai_incidents pipeline

**Date:** 2026-06-01
**Status:** Approved (design); pending implementation
**Author:** maintainer + Claude Code

## Problem

The weekly auto-refresh silently loses incidents. The 2026-05-31 refresh PR
(#18) showed a net change of +5 (7,725 → 7,730) that masked **245 added /
240 removed** entries. Investigation confirmed the removals are not dedupe
merges (only 6 of 240 are recorded in `id_deprecations.json`) and the dropped
incidents do not reappear under any other id — they are genuinely gone. Several
are substantive real-world events (Waymo robotaxi recall, Tesla Autopilot
fatalities, etc.).

### Root cause (confirmed in code)

1. **The OECD ingester is a sliding window.** `scripts/ingest_oecd_aim.py`
   fetches only the newest `DEFAULT_LIMIT = 3000` sitemap URLs (the
   `Weekly auto-refresh` workflow passes `3000`) and **overwrites** the
   committed `ingest/oecd_aim_full_incidents.json` with just that fetch. The
   security-relevant OECD corpus exceeds 3,000 entries, so on each run the
   oldest entries fall outside the window and are erased from the committed
   ingest file.
2. **The build is not retentive.** `scripts/merge_and_dedupe.py` rebuilds
   `data/incidents.json` purely from `ingest/*.json` + `legacy_consolidated.json`.
   The previous `data/incidents.json` is read **only** for timestamp/id
   stability (`_load_prev_state`), never as a retention source. Anything missing
   from the current ingest files vanishes.

Net effect: as the OECD window slides, ~235 incidents/week silently disappear.

## Goal & semantics

Make the dataset **archival**: once an incident is published in
`data/incidents.json`, it is never silently dropped because an upstream source
stopped returning it. Incidents leave the dataset **only** via the existing
explicit deprecation/merge path (`id_deprecations.json`).

Two complementary fixes (both, per maintainer decision):

- **Part A** stops the loss at the source (OECD ingest file accumulates).
- **Part B** is a general backstop for *any* source that drops entries.

Out of scope (deliberate future follow-up): a `source_status` / `last_seen`
provenance field to distinguish "live in upstream feed" from "retained but
upstream no longer lists it." That requires per-entry last-seen tracking, which
collides with the cross-day determinism rule and spans the schema, validator,
and exports — it deserves its own focused PR.

## Part A — OECD ingester union (`scripts/ingest_oecd_aim.py`)

Extract the write step into a pure helper and union the fresh fetch with the
committed file instead of overwriting:

```
def union_with_existing(fresh: list[dict], existing: list[dict]) -> list[dict]:
    """Union by source_id. Fresh wins on conflict; aged-out entries survive.
    Output sorted by source_id for a deterministic, stable-ordered file."""
```

- Key on `source_id` (`OECD-AIM-<id>`).
- Entry in both → take the **fresh** version (latest content).
- Entry only in `existing` (aged out of the window) → **keep it**.
- Sort output by `source_id` so the committed file ordering is stable.

`main()` loads the existing committed file (if present), calls
`union_with_existing(out, existing)`, and writes the union. Result: the
committed OECD ingest file only grows; nothing ages out.

## Part B — build-level retention backstop (`scripts/merge_and_dedupe.py`)

> **Design revised during implementation.** The original plan re-fed prior
> incidents into `all_entries` *before* dedupe (a "step 2b"). Implementation
> testing showed that re-running already-built records through the raw-ingest
> dedupe is **non-idempotent** — the build oscillated (7725 → 7719 → 7725) and
> **silently dropped 17 CVEs** by exposing a latent dedupe bug (see "Discovered
> bug" below). The retention was therefore reworked as a **post-build top-up**
> that bypasses dedupe entirely.

Add **step 6c** in `main()`, *after* IDs are assigned (step 6) and *before*
`generated` is computed (step 7):

1. Compute `covered_keys` — every `source_id` + `cve_id` present in the
   freshly-built `surviving` set.
2. For each prior incident from `load_retained_priors(...)` (i.e. not
   explicitly deprecated): if **none** of its `source_id`/`cve_id` keys are in
   `covered_keys` (and its id isn't already used), the fresh build no longer
   represents it → append it **verbatim** to `surviving`, keeping its `id`,
   `added`, and `updated`. Otherwise skip it (already represented).

Key properties:

- The fresh ingest→dedupe build is **untouched** — byte-identical to the
  pre-retention pipeline. Retention only *adds* uncovered priors.
- A carried prior is preserved exactly as last published (not re-normalised,
  re-classified, or re-deduped), which is the correct archival semantic.
- A prior still emitted by any source is covered by the fresh build, so it is
  **not** duplicated.

### Determinism (the critical constraint)

The build must rebuild byte-identically across UTC days (see
`pipeline-determinism`). The top-up is safe because:

- The fresh build is deterministic exactly as before (unchanged code path).
- A carried prior keeps its stored `added`/`updated` (not today's date), so it
  never triggers an `updated` bump or a `generated` flap.
- Idempotent: on the next rebuild the carried prior is still uncovered (its
  source is still gone) → carried again, same id/timestamps → identical output.
  Verified on real data: 3 consecutive rebuilds are byte-identical and equal to
  the pre-change committed output (retention carries 0 until a source actually
  drops something).

### Discovered bug (pre-existing, deferred to a follow-up PR)

The dedupe indexes (`by_title`, and partially `by_cve`/`by_src`/`by_url`) can
hold references to **tombstoned** entries: `by_title` is never updated on a
transitive merge, and `_reindex` iterates a stale list snapshot so it misses
keys newly absorbed by `merge_into`. A later entry that matches such a stale key
is `merge_into`'d a dead entry and its content is silently dropped. This is
reproducible with a 4-entry ingest fixture and **no retention**, so it is a
latent core-dedupe bug — retention merely amplified it. It is dormant on current
real data (the committed build is stable and lossless). **Decision: ship the
safe top-up now; fix the core dedupe bug in a separate focused PR** (see
`docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md`).

## Testing

- **Retention:** remove an entry from an ingest fixture, rebuild, assert the
  entry persists in `data/incidents.json` with the **same** `INC-` id.
- **Deprecation still wins:** an id present in `id_deprecations.json` `from` is
  **not** resurrected by retention.
- **Ingester union:** unit-test `union_with_existing` directly (pure function,
  no network) — aged-out entry survives, shared entry takes fresh content,
  output is sorted by `source_id`.
- **Determinism:** build twice and with a faked future `date.today()`; assert
  zero field diffs and stable `generated`.

## Validation against PR #18

After the change, re-running the refresh flow on current `main` must **retain**
the ~235 OECD incidents that PR #18 would have dropped, rather than losing them.
Verify concretely (rebuild, diff incident-id set vs. main) before claiming done.

## Files touched

- `scripts/ingest_oecd_aim.py` — extract + call `union_with_existing`.
- `scripts/merge_and_dedupe.py` — add step 2b (retention backstop).
- `tests/` — new retention, deprecation, union, and determinism tests.

No schema, export (STIX/HF), or docs changes — retention is silent in v1.

## Rollout

Ship as a focused PR: branch → push → watch CI green → squash-merge → pull main
(per `working-style-pr-cadence`). Then re-run the weekly auto-refresh so the
next refresh PR is built on the retentive pipeline. Close the stale PR #18 and
re-run rather than merging it (its branch predates this change).
