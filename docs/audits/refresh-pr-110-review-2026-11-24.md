# Refresh PR #110 review (foreman, 2026-11-24)

Dated record. Do not regenerate: if a later run overtakes this, add a dated update.

## Why the public count has not moved since 2026-11-11

The weekly auto-refresh is working. The 2026-11-15 and 2026-11-22 scheduled runs both succeeded,
and the 11-22 run recreated PR #110 on `auto-refresh/data`. The PR was never merged, so `main`
stays at 15,780 (6a4d8261, 2026-11-11). Merging refresh PRs is the user's call (D112 precedent),
so the count moves only when someone merges.

## Staleness check

- PR base = `6a4d8261` = `origin/main` = merge-base. `main` has had no commits since the PR
  opened, so the PR is **not stale** and merging cannot revert newer work.
- Dispatched `Validate dataset` (run 45023703895) and `Site accessibility + integrity` (run
  45023705981) both ran on the PR head `42531400` and both report **success**. The two
  `pull_request` runs report "action_required" because the PR was opened with the workflow token
  (known, PROGRESS.md L1244).

## Per-entity delta [R] (independent of the PR body's D120 report)

Method: load `data/incidents.json` from both refs, key the rows by `id`, compare whole objects
field by field. This is a different route from the workflow's change report.

- Rows 15,821 → 15,845. **Removed: 0.** Added: 24 (INC-17371..INC-17394, all AIID-only, no OECD).
- stats: incident_count 15,780 → **15,804**, landmark 2,056 → 2,080. retracted 29, unverified 12
  and disputed 22 are unchanged.
- Changed existing rows: **33**.
  - 9 AIID rows: description 9, last_seen 9, updated 9, affected 8, title 1, corpus 1. This
    **matches the PR body's D120 table exactly.**
  - **24 CVE rows: `status_reason.as_of` only**, 2026-10-09 → 2026-11-22, with the code
    unchanged. The PR body does not list these. They are expected: the 11-22 sweep re-checked
    1,200 of 9,169 CVEs, found 0 state changes and refreshed the check date.
    `docs/audits/cve-sweep/2026-11-22.md` reports 0 new REJECTED and 0 new DISPUTED.
- OECD inputs are held: no OECD or AIRI ingest file is in the diff. AIAAIC ingest files are untouched.

## Advisories (not merge blockers)

1. **INC-07572 corpus ai-harm → security.** The row is AIID-195 + 2 OECD ids, a predictive-policing
   civil-rights incident. The only upstream change is the deployer string, which now begins
   "Law Enforcement". That is the description→classifier coupling seen in WS0-T3. The flip is
   declared in the PR body, but the new label is probably wrong. Route to label-scientist as a
   follow-up (override or classifier fix); do not hand-edit.
2. **All 24 new AIID rows get corpus `security`**, including medical-advice, facial-recognition
   and autonomous-vehicle incidents. Some attack_vector values also look wrong (INC-17387 is a
   rent-advice harm labelled `rce`). This is pre-existing classifier behaviour: 1,411 of the 1,621
   AIID rows on main are already `security`. It is not introduced by this PR. Same routing as 1.
3. The PR body's "newly retracted: none" is correct, but the body does not mention the 24 routine
   `as_of` bumps. This is a cosmetic report gap.

## Dependabot PRs #105–#109

All have validate 3.12/3.13 passing, plus a11y on the two that touch `a11y.yml`.

| PR | bump | touches | note |
|---|---|---|---|
| #105 | actions/checkout 6.1.0→7.0.1 (major) | all 10 workflows | node 24; credentials now persist to a separate file. auto-refresh / pages / publish do not run on PRs, so the first real test of those is the next scheduled run. |
| #106 | setup-chrome 1.7.3→2.2.0 (major) | a11y.yml | breaking: defaults to Chrome for Testing, which the repo already wants. a11y passed on the PR. |
| #107 | pypi-publish 1.14.2→1.14.3 | publish.yml | patch |
| #108 | create-pull-request 8.1.1→8.1.2 | auto-refresh, atlas-refresh, cve-enrich | patch; used by the refresh PR path |
| #109 | configure-pages 5→6 (major) | pages.yml | node 24 only |

Order: merge #110 first. The Dependabot PRs only touch workflows, so they cannot conflict with the data.
