# D42: WS4-T12 + WS4-T14 + tripwire replacement, implementation record, 2026-10-03

**Status: dated record. Do not regenerate.** Companion to
`docs/audits/refresh-tripwire-2026-10-03.md` (diagnosis) and
`docs/audits/D42-refresh-merge-review-2026-10-03.md` (the 17 changes awaiting the
user's ruling). No `data/*.json` was edited and no deprecation was written.

## What changed

| Item | Where | Effect |
|---|---|---|
| WS4-T12 stamp | `scripts/ingest_oecd_aim.py` (`normalize_body`) | every new OECD row carries `description_provenance: original`, `description_source: oecd-aim` |
| WS4-T12 merge side | `scripts/merge_and_dedupe.py` (`normalize_entry`) | backfills the same two fields for `OECD-AIM-*` rows retained from earlier crawls; never overwrites an explicit label; not in `_CONTENT_FIELDS`, so no `updated` bump |
| Step-4d hazard | `merge_and_dedupe.apply_curation_overrides` | a provenance label from an override applies only while the entry's description still contains the keyed source id (the OECD template does) |
| WS4-T14 | `.github/workflows/auto-refresh.yml` | `Refresh AIID snapshot` step before merge, `continue-on-error`, outcome in the summary, warning on failure |
| D42 gate | `merge_and_dedupe._check_refresh_merge_authorization` | aborts before any write on an unapproved OECD/AIID merge or retitle of a published ID |
| Tripwire replacement | `tests/test_aiid_signal_provenance.py` | explains every `aiid_id` row by exact derivation; the old exact-list test is removed with a dated note |

## Measurements [R]

**T12 field-level delta (agreement 2).** Rebuild of the committed inputs
(`python scripts/parse_existing.py && python scripts/merge_and_dedupe.py`) against
`git show HEAD:data/incidents.json`:

```
rows 13361 -> 13361, ID set identical
changed fields across all rows: description_provenance 3936, description_source 3936, nothing else
labelled "oecd-aim" but description is not the OECD template: 0
OECD template but unlabelled: 0
```

The last two lines are the per-row, independent route (label vs text prefix, both
directions); an aggregate count could not catch a mislabelled row. Only
`data/incidents.json` drifts (7,874 inserted lines); `incidents.min.json` and the
rendered files are unchanged. **This branch therefore fails
`.github/workflows/validate.yml`'s drift check until that rebuild is committed.
I did not commit it (the brief forbade data edits); the foreman must authorize
committing the rebuild with this merge.** The delta is labels only.

**T14.** `python scripts/ingest_aiid_snapshot.py` ran through `ingest/common.py`:
snapshot `backup-20260928101247` (108,565,558 bytes), 1,703 incidents parsed, 1,642
written, max `aiid_id` 1,714 (committed snapshot: 1,581), 3 m 19 s. The refreshed
`ingest/aiid_full.json` was not committed (a data refresh goes through the weekly
PR and the gate). Not wired into `source_health.json`: adding a fifth key would trip
`validate.py`'s registry-provenance source-key comparison; a failing AIID step is
reported by the summary warning only. Follow-up if wanted.

**New tripwire against the real 42-row input.** With today's OECD crawl: passes (all
rows labelled and exactly explained). With the T12 backfill disabled (pre-T12
behaviour), same input: fails with 31 "OECD template under an AIID signal is
unlabelled" problems. So the old failure is reproduced and now cleared by the
labelling, not by editing a list.

**Step-4d hazard fired for real.** With the fresh AIID snapshot (which contains
aiid_id 1574) and the pre-guard override logic, the new tripwire failed:
`aiid_id 1574: ships AIID-authored text but is labelled oecd-aim`. That is the
INC-00437 override mislabelling AIID text, as the old test's docstring warned. The
guard in `apply_curation_overrides` fixes it; the test passes after. The old
test's "1574 absent from the snapshot" assertion was dropped (it would fail every
week once T14 lands) with a dated note.

**Gate against the real input.** Today's OECD crawl alone: aborts with 11 changes (7
merges, 4 retitles), `Nothing was written`, data tree unchanged. OECD plus the fresh
AIID snapshot: 17 (7 merges, 10 retitles). Committed inputs: no abort, build
succeeds.

## Checks proven to fire (agreement 6)

| Check | Input that fails it | Test |
|---|---|---|
| unexplained text under `aiid_id` | AIID-prefix spoof; prose stuffed into the "Entities named" slot | `test_fires_on_aiid_prefix_spoof`, `..._prose_stuffed_into_entities_slot` |
| unlabelled OECD template | provenance fields cleared | `test_fires_on_unlabelled_oecd_template` |
| wrong-anchor label | `oecd-aim` on AIID-authored text | `test_fires_on_oecd_label_on_aiid_text` |
| title | a title no member row carries | `test_fires_on_title_not_from_any_member` |
| scope | exemption removed -> aiid_id 898 flagged; stale exemption flagged | `test_fires_on_row_outside_the_old_two_file_scope`, `test_fires_on_stale_exemption` |
| merge gate | unapproved merge, transitive merge, retitle-by-absorption | `tests/test_d42_refresh_merge_gate.py` |
| approval file | no user marker; edited after ruling | same file |
| workflow | step missing, non-blocking flag removed, misplaced | `tests/test_auto_refresh_workflow.py` |

Controls that must pass: unmutated rows, CVE-only merges, merges of never-published
IDs, a validly approved list.

## Known limits

- The tripwire builds from `ingest/*.json` only; the gitignored
  `data/legacy_consolidated.json` is not read, so legacy-only rows are out of
  scope. `aiid_id` 898 is exempted by name until its curation override exists
  (a data edit, owed to another task); the test fails if the exemption goes stale.
- The approval list's tamper-evidence is a hash of its own entries. Tamper plus
  recompute is not detectable until the ruling's commit pins the hash in code (as
  WS4-T21 did for D28). Until a list exists, the committed approval set is empty and
  a test asserts that.
- Two existing tests (`tests/test_merge_and_dedupe.py`, two functions) use `OECD-AIM-*`
  fixture ids and now supply a valid approval through the real file path; they
  exercise deprecation persistence, not the gate.
- Titles are checked against raw member titles only; their licensing posture is
  still unassessed.
