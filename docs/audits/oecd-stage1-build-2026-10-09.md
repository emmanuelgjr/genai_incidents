# OECD/AIID unfreeze, stage 1 build record (2026-10-09)

Author: pipeline-engineer (WS4). Branch `ws4/v2130-oecd-stage1`, base `main` @ `b8e5ed00`.
User ruling D58: "C stage 1: deliberate freeze." Spec: `oecd-aiid-unfreeze-decision-memo-2026-10-09.md`
section 7, S1-S6. This is a dated record: do not regenerate it. The user rules on merge or decline.

## What this branch does

1. Ports the WS4-T12 (OECD description provenance labels), WS4-T14 (AIID snapshot step in the weekly
   refresh), tripwire replacement and D42 refresh-merge gate from `ws4/refresh-tripwire-42` @ `586f40c8`
   onto current `main`. Not a merge: `git diff a7343274 586f40c8` (12 files) applied with `--3way`;
   conflicts resolved by hand in `scripts/merge_and_dedupe.py` (kept main's `_apply_cve_rejections`
   and disputed handling, added `apply_curation_overrides`) and `.github/workflows/auto-refresh.yml` (kept
   main's `cve-sweep` job, its summary row, `needs-ruling` labelling and `body-path`; added the AIID step,
   summary row and warning). The four D42 audit files are carried over byte-for-byte as records.
   `scripts/ingest_aiid_snapshot.py` already existed on main; only its workflow wiring was missing.
2. Rebuilds `data/incidents.json` in Makefile order. Label-only.
3. Adds one sentence to the gate's abort message naming the freeze as deliberate (D58).
4. Adds `tests/test_oecd_stage1_freeze.py` (16 tests) and `scripts/audit/field_delta_vs_ref.py`.
5. CHANGELOG `[Unreleased]` entry, marked agent-suggested.

Nothing is unfrozen: no new rows, merges, retitles or deprecations.

## Premises that were wrong or incomplete

- **S5 "every `OECD-AIM-`-sourced row's description equals the rebuilt template" is false for 167 of
  4,104 rows.** Measured: 3,937 ship the rebuilt OECD template (all labelled); 162 ship AIID's template
  (AIID won the merge, e.g. INC-07351); 5 ship another source's text (INC-01435, -00813, -00602, -06470,
  -01434; read by hand). The test asserts the true partition (template / AIID template / the 5 named
  exemptions, a stale exemption fails) instead of the false equality. S9a ("0 rows ship OECD narrative")
  is stage-2 and not asserted here beyond: no OECD-sourced row's description is anything but one of the
  three classes above.
- **No pinned prior crawl exists on the old branch** (the 11/17 reproduction used a live crawl and a live
  snapshot; neither was committed). A live crawl is out of scope, so the fresh-input abort is shown on a
  constructed input (below). The 11/17 counts cannot be re-cited on current `main`.
- `main` advanced to `124f951b` during the work (PROGRESS.md only, +4 lines). The delta is taken against
  the stated base `b8e5ed00`; against `main` it is identical (data files unchanged by that commit).

## S1: field-level delta

Command (read-only, no network): `python scripts/audit/field_delta_vs_ref.py --ref b8e5ed00`

```
ref=b8e5ed00
rows: 15666 -> 15666; ids added=0 removed=0
id_deprecations.json byte-identical: True
top-level keys changed: []
rows with any change: 3936
  field description_provenance: 3936 rows  by source {'OECD': 3936}
  field description_source: 3936 rows  by source {'OECD': 3936}
```

The script reports every field in the union of keys per row, so a moved `updated`, `title`, `severity`,
`aiid_id`, `tags`, `references` or `corpus` would print. None did: those are 0. Top-level `generated`,
`version`, `incident_count`: unchanged.

Labelled rows, `(description_provenance, description_source)`, main vs branch:

| label | main | branch |
|---|---|---|
| original / oecd-aim | 1 (INC-00437) | 3,937 |
| original / aiaaic | 1,422 | 1,422 |
| original / None | 134 | 134 |
| verbatim / cvelistv5 | 2,046 | 2,046 |
| verbatim / cve-cna-via-avid | 125 | 125 |
| rows with `description_provenance` | 3,728 | 7,664 |
| rows with `description_source` | 3,594 | 7,530 |

3,728 re-measured on main (matches the memo); 3,936 re-derived (matches). All 3,936 changed rows are
OECD-sourced rows whose description is the OECD template.

**`updated` answer: no bump.** `description_provenance` and `description_source` are not in
`merge_and_dedupe._CONTENT_FIELDS` (lines 1473-1485), so labelling does not touch `updated`, and the delta
shows 0 `updated` changes. No user-visible timestamp consequence. (The new fields are visible in
`incidents.json` and the HF export; see S3.)

Rebuild is byte-exact: a second parse_existing/merge/render/render_docs_stats pass leaves every
`data/*.json` and `INCIDENTS.md` hash unchanged.

## S2: label check, both directions, with fire proofs

`tests/test_oecd_stage1_freeze.py::check_labels` rebuilds the template with `build_description()` from
the RAW ingest row's structural fields (positive control: the rebuild reproduces all 4,160 raw
descriptions) and checks A (label implies template) and B (template or OECD-prefix implies label).
It also fails an `oecd-aim` label on an AIID-template row. Input that fails each, shown firing by a test:

| mutation | test |
|---|---|
| unlabel one labelled row | `test_s2_fires_when_a_template_row_is_unlabelled` |
| relabel an AIID-template row `oecd-aim` | `test_s2_fires_when_an_aiid_template_row_is_relabelled` |
| edit text under a label | `test_s2_fires_on_a_label_over_edited_template_text` |
| OECD-prefix text on an unlabelled non-OECD row | `test_s2_fires_on_a_prefix_spoof_without_label` |

**Byte-level key-order change (declared 2026-10-09, gate advisory A1).** INC-00437's existing
`description_provenance` / `description_source` keys moved position in `data/incidents.json`: they now sit
after `aiid_id` instead of after `mitre_atlas_tactics`. Values are identical. Cause: on main the two labels
reached INC-00437 only through the step-4d curation override (applied after normalisation, so appended late);
the T12 backfill in `normalize_entry` now sets them at normalisation, immediately after `aiid_id`, and the
override re-writes the same values in place. This is why the diff is 7,874 insertions and 2 deletions (3,936
rows x 2 lines, plus the two moved lines). Value-level delta (above) cannot see it; `field_delta_vs_ref.py`
now prints a key-order report. No data was changed to address it.

## S3: derived artifacts

Measured by generating each artifact from this tree and from `git show b8e5ed00:data/incidents.json`
and comparing (scratch copy), plus `git status` after the render steps.

| artifact | new fields reach it? |
|---|---|
| `data/incidents.json` | yes (the delta above) |
| `incidents.min.json` x3 (`data/`, `docs/data/`, `src/genai_incidents/data/`) | no, byte-identical |
| `docs/data/*` slim files | no (unchanged in `git status`) |
| HF export `dist/hf/incidents.jsonl` (verbatim dump, not committed) | **yes**: 15,637 rows, `description_provenance` and `description_source` differ on exactly 3,936 rows, no other field; README card identical |
| STIX bundle | no, byte-identical to control |
| MISP feed | no, `diff -rq` clean |
| TAXII | no, `diff -rq` clean |
| `INCIDENTS.md`, `docs/incidents/*.md` | no (unchanged) |
| `data/stats.json` | no (unchanged) |

Only the Hugging Face dataset file changes on the next push; nothing else published is affected.

## S4: ingest files

`git diff b8e5ed00 --stat -- ingest/` is empty: `aiid_full.json`, `aiid_full.provenance.json`,
`oecd_aim_full_incidents.json` byte-identical. The snapshot step is wired in the workflow; no snapshot
output is committed.

## S5: the deliberate guard

- **Approval set empty.** `docs/audits/D42-approved-refresh-merges.json` does not exist.
  `test_committed_approval_set_is_empty` asserts absent-or-empty and an empty loaded set;
  `test_emptiness_check_fires_on_a_signed_nonempty_list` shows the loader returns a non-empty set on a signed
  list (the input that would fail the first). Also `test_d42_refresh_merge_gate.py`: unsigned list refused,
  list edited after the ruling refused. Known limit (inherited, documented in the T12/T14 note): tamper plus
  recompute is not detectable until a ruling pins the hash in code; stage 2 (S7).
- **Gate on fresh vs committed inputs.** `test_gate_aborts_on_fresh_bridging_input_and_not_on_committed_inputs`
  copies the repo to a scratch directory, builds on committed inputs (exit 0, no "Nothing was written"),
  then appends ONE OECD row whose `extra_source_ids` are two already-published AIID-only entries (the
  2026-10-03 mechanism, constructed). The build exits non-zero with `[FATAL] D42/D25(a) ... (2)`: one merge
  (INC-07566 -> INC-07354) and one retitle (INC-07354), "Nothing was written", and a hash of every
  `data/*` file and both ingest files is identical before and after. **Fire proof of the gate itself:**
  with the `_check_refresh_merge_authorization` call replaced by `pass`, that test fails
  (`returncode == 0`); restored. These counts (2) are for the constructed input, not the 11/17 of the live
  2026-10-03 run, which cannot be reproduced offline.
- **Full-corpus OECD template and attribution.** `check_partition` and `check_attribution` over all 4,104
  OECD-sourced rows: description class as in "Premises" above; 100% (4,104/4,104) carry
  `OECD (<year>), AI Incidents and Hazards Monitor, <url> (accessed on <added>)` on an oecd.ai reference
  whose URL matches the title. Fire proofs: `test_partition_fires_on_oecd_narrative_like_text`,
  `test_partition_fires_on_stale_exemption`, `test_attribution_fires_when_citation_is_removed_or_misdated`.
- **Workflow.** `tests/test_auto_refresh_workflow.py` (ported): AIID step present, `continue-on-error`,
  `id: ingest_aiid`, before the merge step, outcome reported; four mutations fire. New
  `check_fail_closed` (+ `test_fail_closed_check_fires`): the merge step is not `continue-on-error`, the PR
  step follows it, and no PR-touching step has `if: always()/failure()`; fires on both mutations.

## The accidental E21 tripwire test: decision

`tests/test_e21_partA_inc00437_provenance.py::test_oecd_aiid_content_disagreement_is_unique_to_inc00437`
**is removed**, as on `ws4/refresh-tripwire-42`, with a dated tombstone comment in place and its text in git
history. Reasons:

1. It asserted an exact two-row population (`[1574, 1575]`). It failed the weekly runs of 2026-09-14,
   09-20, 09-27 (and the 10-03/10-04 runs) because the population grew 2 -> 42 as OECD cites newer AIID ids
   than the committed snapshot, not because of a defect. It cannot be satisfied while the freeze is in
   force and the snapshot is refreshed.
2. It had three blind spots (prefix-spoofed descriptions, rows outside its two ingest files such as
   `aiid_id` 898, the `title` field). `tests/test_aiid_signal_provenance.py` (ported) explains every
   `aiid_id` row by independent derivation and is shown to fire on each blind spot.
3. A failing unit test is the wrong place for the freeze: it ran after the merge had already rewritten the
   data tree in the runner, and it could not distinguish "approved change" from "defect". The gate can.
4. Its companion assertion that aiid_id 1574 is absent from the snapshot is dropped with a dated note (the
   2026-09-28 snapshot contains 1574); the INC-00437 label is protected by the guard in
   `apply_curation_overrides`, tested in `test_d42_refresh_merge_gate.py`.

The tripwire that remains and still passes on committed inputs: `test_aiid_signal_provenance.py`.

## Weekly refresh behaviour while the freeze holds

On a run whose fresh OECD crawl (plus, now, the fresh AIID snapshot) would merge or retitle a published ID
through an OECD-AIM-/AIID- source id:

- **Failing step:** `refresh` job, step "Re-merge + render + validate" (`python scripts/merge_and_dedupe.py`),
  after `parse_existing.py`. It exits 1 with, on stderr:
  `[FATAL] D42/D25(a): this build would write OECD/AIID-driven change(s) to previously-published IDs that the user has not approved (N):`,
  one `merge ...` / `retitle ...` line per change (first 25), then
  `Nothing was written. This freeze is deliberate (D58, stage 1): a weekly refresh that reaches this gate fails closed until the user rules. Review the evidence list, then record the user's ruling in docs\audits\D42-approved-refresh-merges.json (see docs/audits/D42-refresh-merge-review-2026-10-03.md).`
  It aborts before the first output write; `data/` is untouched in the runner.
- **Skipped (all have the implicit `success()` condition):** Unit tests, Show summary, Newly retracted
  entries report, Ensure needs-ruling label, **Open / update refresh PR**, Remove stale needs-ruling label,
  Enforce source health, Enforce OECD skip-rule sampling probe. So **no PR opens or updates**, and the run is
  red (GitHub's failed-scheduled-workflow notification fires).
- **Already done before the gate:** the three ingest steps, the AIID snapshot step (`continue-on-error`),
  the ingest summary, source-health counters and the OECD skip-probe cursor persisted to `refresh-state`.
  The `cve-sweep` job is separate and unaffected: it runs, uploads its artifact and its dated log.
- **Whether it is red EVERY week** depends on the crawl: the memo's "yes" rests on the 2026-10-03
  measurement (the bridging comes from OECD rows that persist in the union-merged crawl). Not re-measured
  here (no live crawl). A week whose inputs create no gated change builds normally and opens a PR.

### Consequences the user should know before merging this branch

1. **While the gate holds, nothing else in the weekly refresh reaches a PR**: AIRI, AIAAIC, KEV, and the
   `cve-sweep` rejected/disputed CVE results and D60 retraction flagging are all produced or applied inside
   the same job and are lost with the red run (the sweep artifact is uploaded but never applied). The
   item-3 retraction path is therefore stalled for as long as stage 1 is in force. Not broken (it works the
   week the gate does not fire, and it is unchanged), but starved. Stage 2 (S7, suppression list) is what
   lets the run proceed.
2. The two "Enforce ..." steps (source health, skip-probe) are skipped on a gate abort. The run is already
   red; the counters were persisted earlier. Not changed here; making them `!cancelled() && ...` is a
   one-line follow-up if the user wants those messages even on a gate abort.
3. The weekly run now downloads AIID's ~108 MB snapshot (one index GET, one tarball GET through
   `ingest/common.py`: robots, rate limit, identifying User-Agent).

## S6: docs for WS0 (after the data lands; live surfaces corrected in place)

- `docs/SOURCE_LICENSES.md` 1.5 (OECD) and 1.2a (AIID): counts and the T12 label (3,937 rows
  `original/oecd-aim`).
- `NOTICE-DATA` lines ~195-198 and ~249-251; the "3,667 of 3,829" figure is stale: re-derived like-for-like
  figure is 3,937 of 4,104 (titles equal a raw OECD title is a separate stage-2 count; the label count is
  3,937 of 4,104 OECD-sourced rows, the other 167 ship AIID or other-source text).
- `.reuse/dep5` AIID lines.
- CHANGELOG: the agent-suggested entry is in `[Unreleased]`; WS0 to adopt or reword. Wording must say the T12
  label is a provenance label, not a licence marker (R8).
- `scripts/export_huggingface.py` card text mentions `description_source == "aiaaic"` only; the HF export now
  also carries `oecd-aim` labels (S3). WS0/docs-warden to decide whether the card should say so.
- DATASHEET / schema docs: `description_source` is a free-form slug in the schema (its description names `aiaaic` as an
  example) and `description_provenance` already allows `original`; `validate.py` passes; no schema change
  was made. The schema text could name `oecd-aim` as an example.

## Verification run on this branch

`pytest tests -q`: 728 passed, 1 xfailed. `scripts/validate.py`, `scripts/check_stats_drift.py`,
`scripts/lint_atlas_ids.py`: clean. `git status --porcelain` empty at commit.

## Addendum 2026-10-10: D67, the gate also holds OECD row additions and upstream title edits

User ruling D67: "Also hold OECD row additions." Without it, a week with no merge or retitle of a published
ID would open a normal PR carrying the whole unfrozen crawl (about 1,500 new OECD rows with LLM titles, per
the foreman; not re-measured here, no live crawl) plus upstream AIID title edits. Data is unchanged versus
9591ca0f (rebuild byte-exact, `git diff 9591ca0f -- data ingest INCIDENTS.md docs/incidents` empty).

**(a) What counts as an OECD-driven addition.** The unit is the OECD source row, not the entry ID: any
`OECD-AIM-` source id present in the build that no previously published entry carried in its `source_ids`.
This covers (i) a new ID built from a new OECD row, (ii) a mixed new row (OECD + AIID), and (iii) a new OECD
row absorbed into an already-published ID (the published ID gains an OECD source id, references and possibly
tags, with no title change and no deprecation, which the D42 gate alone never saw). Defining it by "new ID"
would have let (iii) through. Not held: a new AIID-only row (D67 names OECD additions; the fresh AIID
snapshot adds roughly 94 such rows with AIID-authored titles, which is a separate exposure the user has not
ruled on, see below). The check is skipped only when there is no previous build at all (empty baseline);
the weekly job checks out `data/incidents.json` from git, so that is not reachable there.

**(b) Upstream title edits: included.** A published entry whose title changes, whose current `source_ids`
include an `OECD-AIM-` or `AIID-` id, and whose new title is not set by a committed curation override, is held
as `title edit <id> (D67)`. This is the review's section C population (24 AIID/OECD rows edited upstream, for
example "Reportedly"/"Allegedly" insertions) and the user named it as exposure. The one reason found to
exempt something: the project's own curation-override titles, which are decisions, not upstream edits, so a
title equal to a `data/curation_overrides.json` title is not held (that is what the old
"retitle without absorbing is not gated" test protected). Cost: a future commit that changes an OECD/AIID row
title by any other route must carry a `retitle` approval; with the committed inputs nothing changes. Titles
of rows with no OECD/AIID source id (CVE, AVID, etc.) are not held.

**(c) Abort message.** One gate, one message: `[FATAL] D42/D25(a)+D67: this build would write
OECD/AIID-driven change(s) (merges/retitles/title edits of published IDs, or added OECD rows) that the user
has not approved (N):`, one line each (`merge`, `retitle`, `title edit`, `add OECD row(s) [...] (new row |
absorbed into published row) as <id>`), first 25 listed, then `Nothing was written. This freeze is deliberate
(D58/D67, stage 1): ...`. It runs before the first output write. Approvals use the same signed file; a new
approval kind `{"kind": "add", "source_id": "OECD-AIM-..."}` exists for stage 2. The committed set is still
empty and tested as such.

**(d) Committed inputs do not abort.** Real build on this tree: exit 0, `data/`, INCIDENTS.md and
docs/incidents unchanged. All 4,160 OECD source ids in `ingest/oecd_aim_full_incidents.json` are already
carried by published entries, and no published title differs.

**Tests and fire proofs.**
- Real-build subprocess tests in a scratch repo (`tests/test_oecd_stage1_freeze.py`): committed inputs build
  and reproduce `data/incidents.json` and `id_deprecations.json` byte-for-byte
  (`test_committed_inputs_do_not_abort`); a constructed pure OECD addition aborts with only the `add` line
  (`test_d67_gate_aborts_on_a_new_oecd_row`); a constructed AIID title edit on a published AIID-only row
  aborts with only the `title edit` line (`test_d67_gate_aborts_on_an_upstream_aiid_title_edit`); the D42
  bridging case still aborts. Each leaves every `data/*` file and both ingest files byte-identical.
- Unit tests (`tests/test_d42_refresh_merge_gate.py`): new row, mixed new row, absorbed new OECD id, upstream
  title edit, curated title not held, non-OECD title edit not held, new AIID-only row not held, approved `add`
  allowed.
- Fire proofs (gate part disabled, tests run, restored): with the addition check disabled
  (`if prev_by_id:` -> `if False:`) `test_d67_gate_aborts_on_a_new_oecd_row`,
  `test_new_oecd_row_aborts_and_unchanged_set_does_not` and `test_mixed_new_row_and_absorbed_new_oecd_id_abort`
  fail; with the title-edit branch disabled `test_d67_gate_aborts_on_an_upstream_aiid_title_edit` and
  `test_upstream_title_edit_on_gated_row_aborts` fail.
- `tests/test_merge_and_dedupe.py`: its from-scratch fixtures use `OECD-AIM-*` ids and edit titles to test
  deprecation persistence and the split guard, which the extended gate now holds; `_setup_tmp_repo` stubs the
  gate there (the gate has its own tests above, including real builds). The old test
  `test_retitle_without_absorbing_gated_ids_is_not_gated` is replaced by a curated-title version plus its
  uncurated counterpart.

**Open for the user (not decided here).** New AIID-only rows from the weekly snapshot (AIID-authored titles)
still flow into a PR; D67 as worded does not hold them. One-line change if wanted: extend the addition check
to `AIID-` source ids.
