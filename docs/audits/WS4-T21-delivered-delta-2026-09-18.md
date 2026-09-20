# WS4-T21 delivered delta — 2026-09-18

**Status: DELIVERED.** This document describes what this branch's rebuild
*actually produced* against the tree at `origin/main` (13,060 rows), after
BOUNCE #1's defect-1 fix. It is a companion to, not a replacement for,
`docs/audits/WS4-T19-dryrun-delta-2026-09-18.md` — that document's own
figures (+1 deprecation, 26 severity changes, `updated` on 47 rows, title/
date/description confined to 4 ids) are **preserved unedited** per
agreement 4: they are an accurate record of what a bare rebuild with
WS4-T10's fix and WS4-T19's guard alone produces, **without** the
retirement-execution and inbound-redirect-correction steps this task
(WS4-T21) added. Those two artifacts describe two different builds of the
same authorized list; **this one is what shipped.**

Measured directly against the pre-build tree (a saved copy of
`origin/main`'s `data/incidents.json` / `data/id_deprecations.json`), not
against the dry-run document — an independent derivation, not a rerun of
someone else's method (agreement 6).

## Entry count / ID set

| | value |
|---|---|
| pre-build `incident_count` | 13,060 |
| post-build `incident_count` | 13,361 |
| **delta** | **+301** |
| ids removed from the active set | **5**: `INC-00311`, `INC-00554`, `INC-00754`, `INC-01897` (D28-authorized retirements) + `INC-07738` (ordinary, unrelated Mythos `merged` deprecation — pre-existing dedupe behaviour, not part of the 47-split remediation) |
| brand-new ids | 306 |
| common ids (same id, both builds) | 13,055 |

## Deprecations: `data/id_deprecations.json`

1,051 → 1,060 (**+9**). **Invariant 9 (append-only) checked directly**:
every one of the 1,051 pre-existing records is byte-identical in the
post-build file (`Counter` diff over `(from, into, reason, date)` empty);
nothing was edited or removed.

The 9 new records:

| from | reason | into (count) | why |
|---|---|---|---|
| `INC-00311` | `split` | 12 ids | D28 retirement — no survivor keeps the old id |
| `INC-00554` | `split` | 100 ids | D28 retirement |
| `INC-00754` | `split` | 11 ids | D28 retirement |
| `INC-01897` | `split` | 8 ids | D28 retirement |
| `INC-07738` | `merged` | `INC-14757` | ordinary dedupe (Mythos cross-successor observation, routed to WS4-T5 — unrelated to this authorization) |
| `INC-07771` | `resplit` | `INC-14814` | **BOUNCE #1 defect-1 fix**: was resolving to `INC-01271` (a `keep_id` survivor holding only part of its old content) |
| `INC-08109` | `resplit` | `INC-14847` | same shape, was resolving to `INC-01412` |
| `INC-08133` | `resplit` | `INC-14850` | same shape, was resolving to `INC-07736` |
| `INC-08146` | `resplit` | `INC-14853` | **BOUNCE #1 defect-1 fix**: was fanning out through the retired `INC-00554`'s full 100-successor set; D28 approved it exactly one |

Per-entity proof each corrected target is right, not inferred: each
successor's `title` matches the authorized list's own `recovered_title`
field **exactly** — `INC-14814`/`INC-14847`/`INC-14850`/`INC-14853`, all
four checked.

The other 4 of the 8 pre-existing inbound redirects
(`INC-00497`→`INC-00311`, `INC-03128`→`INC-00754`, `INC-08139`→`INC-00554`,
`INC-08185`→`INC-08139`→`INC-00554`) needed **no** new record: they
already chain-resolve, through the 4 retirement `split` records above, to
exactly the successor set D28's `new_targets` approves for them (verified
by expanding any retired-id references inside `new_targets` through the
same chain walk, per entity, not assumed).

## Field-level changes, common ids (13,055)

| field | # changed | note |
|---|---|---|
| `updated`, `last_seen`, `source_count`, `source_ids`, `references` | 43 | the 43 `keep_id` survivor rows — exactly the `keep_id` count, set-identical (verified: the 43 ids with `updated` bumped are exactly the 43 `keep_id` entries in the authorized list) |
| `mitre_atlas` | 28 | cascade of `owasp_llm`/`owasp_asi` reclassification on the same 43 rows (subset) |
| `nist_ai_rmf` | 27 | ” |
| `mitre_atlas_tactics` | 26 | ” |
| `owasp_asi` | 26 | ” |
| `owasp_llm` | 25 | ” |
| `severity` | 22 | all downward — see below |
| `cve_ids` | 10 | subset of the 43, references shed with the split |
| `capec_ids`, `cwe_ids`, `tags` | 8 each | derived-field cascade |
| `cvss_vector` | 2 | ” |
| `confidence`, `attack_vector` | 1 each | ” |

**`title` / `description` / `date`: 0 common ids.** This is the intended
outcome, not a gap — the 4 rows where those fields would otherwise have
changed under a shared id (the exact continuity-break bug) are the 4
retired ids, which are no longer "common" once correctly retired; they
show up as removed+added instead, per invariant 4.

**`added` immutable: 0 violations, all 13,055 common ids checked directly.**
**Invariant 4, checked directly, all 13,055 common ids: 0 violations**
(0 spurious `updated` bumps, 0 missed bumps).

## Severity: 22 changes, all downward, 0 upward

All 22 are inside the 43-row `keep_id` set (verified: every id in the
severity-change list is a `keep_id` entry in the authorized list; none is
one of the 4 retired ids, which — correctly — no longer appear as
"changed" under invariant 4 once retired rather than left mismatched).

## Reference URLs — corpus-wide (not per-common-id)

**377 gained / 0 lost.** Computed as a distinct-URL-set difference across
the WHOLE corpus (66,025 → 66,402 URLs), not restricted to common ids —
this is the number invariant under whether a row keeps its old id number,
since a URL belongs to the corpus regardless of which id currently holds
it. Unaffected by the BOUNCE #1 defect-1 fix (that fix only rewrites
`id_deprecations.json` redirect targets, never touches `references`).

## Other published-claim deltas

`data/stats.json`: `landmark_count` **1,905 → 1,915 (+10)**. Not
separately audited here — routed to docs-warden by the foreman, since a
change to a published claim (not merely an internal count) is out of this
task's own remediation scope; named here so the delta table is complete
per agreement 2.

## Determinism

`data/incidents.json` / `data/incidents.min.json` / `data/id_deprecations.json`
rebuilt three times from the committed inputs at this branch's HEAD;
sha256 identical across all three runs
(`b22622d1a6563dc…` / `5fff3aa03ad9c40…` / `72940ec3058341…`). The BOUNCE
#1 fix and the earlier retirement-execution step are both idempotent: a
build with nothing left to correct prints nothing for that step and
writes byte-identical output.

## Relationship to the D28-authorized list

Every id and target in this document traces to an entry in
`docs/audits/WS4-T19-authorized-splits-2026-09-18.json`'s `entries`
array, verified against that file's pinned `authorization.entries_sha256`
(`873c29a2b999335f9f1703510bbfec301028ae6ad6cb21a1d2a4e3db99654a4f`) —
the same value `scripts/merge_and_dedupe.py`'s
`REQUIRED_SPLIT_AUTHORIZATION_ENTRIES_SHA256` pins in code. Nothing in
this delta traces to a judgement made outside that list.
