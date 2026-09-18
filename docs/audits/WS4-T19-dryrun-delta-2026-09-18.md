# WS4-T19 — dry-run field-level delta (what the user would be approving)

**Status: RECORD, dated 2026-09-18. DO NOT REGENERATE.** Explains
`docs/audits/WS4-T19-dryrun-delta-2026-09-18.json`. Per working agreement
2 (field-level delta rule): every affected field is enumerated and every
intended delta is justified; an unintended delta is a defect. **Produced
entirely in detached scratch worktrees; no file under `data/` or
`schema/` in this repository was read for writing, or written.**

> **BOUNCE #1, 2026-09-18**: the reviewer independently reproduced every
> figure in this document (headline numbers, the 25-field breakdown, the
> invariant checks) and found none of them wrong. The bounce was on the
> companion evidence document's characterisation of its own confidence
> (see `docs/audits/WS4-T19-split-evidence-2026-09-18.md`'s BOUNCE #1
> box) and on this document's own regeneration recipe omitting a required
> `data/` reset step — fixed below.

- **control**: `origin/main` HEAD, commit `00b889c7` — today's committed
  13,060-row corpus, unchanged `normalize_url`.
- **fixed**: `origin/main` HEAD with `fe3a4845` ("Revert 'Merge WS4-T10'")
  reverted, commit `f2871dce` — WS4-T10's fix reapplied on top of
  everything currently on `main` (including WS4-T15), **plus this
  branch's pre-authorization guard** (Deliverable 3), run with the full
  55-entry proposed authorized list from Deliverable 2 in place so the
  build completes and produces output to diff.

Regenerate with (never against the real `data/` tree):
```
git worktree add --detach <control_dir> origin/main
git worktree add --detach <fixed_dir> origin/main
cd <fixed_dir> && git revert --no-edit fe3a4845
# copy this branch's scripts/merge_and_dedupe.py guard additions into <fixed_dir>
# copy docs/audits/WS4-T19-authorized-splits-2026-09-18.json into <fixed_dir>/docs/audits/
cd <control_dir> && python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
cd <fixed_dir>   && python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
python scripts/audit/ws4t10_phaseb_delta.py <control_dir> <fixed_dir> \
    docs/audits/WS4-T19-dryrun-delta-2026-09-18.json
git worktree remove <control_dir> --force
git worktree remove <fixed_dir> --force
```
**[BOUNCE #1 correction, dated 2026-09-18]** As written, `<fixed_dir>`'s
`data/` starts at the control commit and this recipe builds it exactly
ONCE, so it is not exposed to the stale-comparison risk below. **If you
extend this recipe to also demonstrate the guard's abort path in the same
tree** (e.g. running once WITHOUT the authorized list first, to see it
abort, before copying the list in and running again) — do that BEFORE
this recipe's own build, or reset `data/` in between:
`git checkout -- data/incidents.json data/id_deprecations.json
data/incidents.min.json` in `<fixed_dir>`. The guard compares against
whatever `data/incidents.json` currently holds
(`_load_prev_state()`), not a frozen baseline, so a second run in the
same tree after a first run already wrote the split corpus will not
detect the same splits as new — see
`docs/audits/WS4-T19-split-evidence-2026-09-18.md`'s Deliverable 3
section for the full explanation and the corrected two-step proof-of-fire
recipe.

## Headline numbers

| metric | before (control) | after (fixed, authorized) | delta |
|---|---|---|---|
| incident_count | 13,060 | 13,361 | **+301** |
| id_deprecations.json entries | 1,051 | 1,052 | **+1** (the `INC-07738`→`INC-14757` recovered-duplicate merge — pre-existing, not new to this remediation) |
| common rows (unaffected identity) | — | 13,059 | 13,060 old − 1 gone (`INC-07738`) |
| new-only rows | — | 302 | 47 splits' successors that aren't the survivor |
| gone (old id, no replacement row) | — | 1 (`INC-07738`) | absorbed into `INC-14757`, itself one of `INC-00623`'s split successors — not an additional row |
| common rows with ≥1 field changed | — | 47 | exactly the 47 split ids' own survivor rows (shedding split-off content changes their own aggregate fields) |
| **arithmetic check** | | | 47 splits alone: +302 (47 survive, 302 new). `INC-07738` merge alone: −1. Net: **+302 − 1 = +301**, matching `id_sets` exactly. |

**This reconciles the ±1 discrepancy the WS4-T15 spec's §1 resolved
per-entity** (not re-litigated here, but re-confirmed as part of this
independent re-derivation: `id_sets` gives `new_only_count=302,
gone_count=1`, and `INC-14757` is the sole point of overlap between
`splits.rows` and `new_deprecations` — it's already counted once among
`INC-00623`'s split successors).

## Field-level breakdown: what changed on the 47 common (survivor) rows

Every one of the 47 split ids' own row is a "common row" (it existed
before and after — it just now covers less content). Per-field change
counts across those 47 rows:

| field | # rows changed | why (intended / justified) |
|---|---|---|
| `last_seen` | 47 | every affected row's `last_seen` moves — the row now reflects a build where its content set actually changed. **Intended.** |
| `references` | 47 | every survivor sheds the references that belonged to now-split-off, unrelated content. **Intended** — this is the correction the fix exists to make. |
| `source_count` / `source_ids` | 47 | direct consequence of the split — each survivor's `source_ids` shrinks to only the sources that actually belong to it. **Intended.** |
| `mitre_atlas` | 32 | derived taxonomy field, recomputed from the survivor's now-correct (smaller) content set. **Intended** — a taxonomy tag inherited from split-off content is exactly the kind of contamination the fix removes. |
| `nist_ai_rmf` | 31 | same as above. **Intended.** |
| `mitre_atlas_tactics` / `owasp_asi` | 30 each | same as above. **Intended.** |
| `owasp_llm` | 29 | same as above. **Intended.** |
| `severity` | 26 | **all 26 changes are DOWNWARD** (e.g. Critical→High, Critical→Medium). This is severity CORRECTION, not severity loss: `merge_into`'s "pick the higher severity across all merged members" rule was picking up inflated severity from unrelated, now-split-off content. **Intended, and it is the exact shape of harm this task's brief names ("downward severity revisions must not be silently dropped") — this delta is what makes it visible and reviewable, not what causes it.** |
| `cve_ids` | 11 | a survivor sheds CVEs that belonged to split-off content. **Intended.** |
| `tags` | 10 | derived from content set. **Intended.** |
| `capec_ids` / `cwe_ids` | 9 each | derived from CVE set, which itself is corrected above. **Intended.** |
| `date`, `description`, `title` | 4 each | **exactly the 4 continuity-breaking splits** (`INC-00311`, `INC-00554`, `INC-00754`, `INC-01897`) — see the evidence doc. **Intended to be VISIBLE here** (this is precisely why those 4 are flagged for retirement rather than silently kept); not intended to SHIP as-is under the old id — that's what Deliverable 2's authorized list routes to `retire`, not `keep_id`. |
| `attack_vector`, `cvss_vector` | 3 each | derived from the corrected CVE/content set. **Intended.** |
| `affected`, `aiid_id` | 2 each | derived / provenance fields tracking the corrected content set. **Intended.** |
| `year`, `cvss_score`, `discovery_method`, `confidence` | 1 each | derived fields, same cause. **Intended.** |

**No field changed on any of the 47 that isn't explained by "this row's
content set is now smaller and correct."** No field outside this list
changed on any common row (`common_rows_changed_count` = 47, matching the
table above exhaustively — confirmed by iterating the full
`common_rows_changed` array in the JSON, not sampled).

## Invariant checks

- **Invariant 4** (`added` immutable; `updated` bumps only on content
  change): **0 violations**, either direction
  (`invariant4_violations.bumped_no_content_change` and
  `.content_change_no_bump` both empty).
- **Invariant 9** (append-only, never reused; a deprecation record is
  never deleted or edited): **0 violations**
  (`deprecations_deleted_or_modified` empty — every one of control's
  1,051 records is present, unmodified, in fixed's 1,052).
- **Reference URLs**: 377 distinct URLs newly shipped corpus-wide, **0
  lost** (66,025 → 66,402 distinct; 66,048 → 66,425 total entries).
  Matches the design doc's post-BOUNCE#1 re-measurement exactly.
- **New deprecations this build**: exactly 1 —
  `{"from": "INC-07738", "into": "INC-14757", "reason": "merged", "date":
  "2026-09-18", "retired_source_ids": ["OECD-AIM-2026-04-08-e597"]}` — the
  pre-existing recovered-duplicate merge (design doc §2.3/§8.4), not part
  of this remediation's own 4-retirement / 8-resplit proposal (those are
  NOT yet applied — this dry-run ran with the AUTHORIZED LIST present so
  the guard would let the build complete, but no `split`/`resplit` records
  are written by an ordinary rebuild; those are written by whatever
  script executes the authorized remediation, which this task does not
  run).

## ID-set summary

- 13,060 old ids → 13,059 common (unchanged identity) + 1 gone
  (`INC-07738`, absorbed).
- 13,361 new ids = 13,059 common + 302 new-only.
- Every one of the 302 new-only ids is `> INC-14604` (the prior corpus's
  max id) — confirmed, invariant-9-clean, monotonic counter.

## What the user would be approving, restated plainly

A rebuild that: keeps 43 ids exactly where they are (their own content
just gets more precise — less contamination, corrected severity, fewer
false taxonomy tags); retires 4 ids whose content the fix proves the old
id was pointing at the wrong thing; mints 302 new ids for content that
was always distinct but never had its own number; and writes 8 additional
redirect corrections for citations that currently point at now-stale
targets. Nothing is deleted. No id is reused. See
`docs/audits/WS4-T19-split-evidence-2026-09-18.md` for the full per-split
judgement this delta is the numeric confirmation of.
