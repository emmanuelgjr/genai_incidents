# ID-reuse audit: task spec (queued, user ruling D70)

**Date:** 2026-10-10. **Author:** schema-architect (WS3). **Status:** spec
for a queued task. The audit has not been run. This file is a dated record:
when the audit lands, add a dated update below and do not rewrite this text.
**Do not regenerate.**

**Authority.** User ruling D70: "Queue an ID-reuse audit." This branch
(`ws3/v2130-group-ids`) only corrects the false "never reused" claim on live
surfaces (see `CORRECTIONS.md`, 2026-10-10) and writes this spec. The audit
itself is a separate task for the board.

## Why

`docs/DATA_DICTIONARY.md` said incident IDs are "Never reused".
`docs/ID_POLICY.md` §4 rule 1 states it as policy. The item-4 gate found that
the published record does not meet it. Re-derived for this spec on
`ws3/v2130-group-ids` (method in `docs/ID_POLICY.md` §8.6):

- 16,572 IDs were published across the 14 tags v2.0.0 to v2.12.0.
- **591** of them carried more than one title across those tags. By current
  `resolve_id_status()`: 575 `live`, 12 `withdrawn`, 3 `release-dependent`,
  1 `group`.
- The gate reported "14 withdrawn IDs". Its classification is not recorded,
  so the two figures may be counting different sets. This spec fixes one
  method (below).

A title change is not proof of reuse. Many will be retitles of the same
incident: an upstream title edit, or a template change such as the OECD-AIM
description template in v2.9.0. Some are a different incident under the same
number. `INC-00004` was an MLflow command injection (v2.0.0–v2.1.0), an
MLflow path traversal (v2.2.0–v2.5.0), and a Dex XML-encoding issue
(v2.6.0–v2.7.0), and is now `withdrawn`. Today no tool tells the two kinds
apart, and the API cannot answer for a live ID: `resolve_id_status()`
ignores `release=` when the ID is live (ID_POLICY §8.2).

## Scope

- **In:** every ID live in any `v*` tag's `data/incidents.json` with more than
  one distinct `title` across tags (591 at the time of writing). Also any ID
  whose `date`, or whose headline source (first `source_ids` element),
  changed between consecutive tags while the title stayed the same. That
  case is the same defect hidden behind an unchanged title. Count it
  separately.
- **Out:** making any data change. The audit produces evidence and proposals.
  Records follow only by a user ruling, as for D69. IDs live in only one tag
  are also out, since they cannot have been reused across releases.

## Method

1. **Per-ID history.** For each in-scope ID and each tag it was live in,
   record: `title`, `date`, `description` (first 300 chars), the full
   `source_ids`, `cve_ids` and the first reference URL. Read every tag with
   `git show <tag>:data/incidents.json`. Do not use the package or
   `id_deprecations.json` for history.
2. **Segment** each ID's tags into runs. A new run starts where the title,
   date or headline source changes from one tag to the next.
3. **Classify each boundary between runs.** Use these classes:
   - `retitle`: same incident. Headline source and date unchanged, or the
     new headline source is the old one's own upstream record re-keyed.
   - `different-incident`: the incident changed. Headline source and date
     both changed, and the description names a different event or product.
   - `over-merge-drift`: the row absorbed other incidents (its `source_ids`
     grew) and the named incident changed with it. `INC-00554` is the type
     case.
   - `undetermined`: the evidence does not decide. List it. Never guess.

   **Do not decide by source-set overlap.** Over-merged rows accumulate
   sources, so consecutive source sets almost always overlap. Measured while
   writing this spec: none of the 591 IDs has a pair of consecutive tags with
   disjoint `source_ids`. Yet `INC-00004` changed incident twice. Use the
   headline source, the date and the description.
4. **Successor per run.** For each run, find the single current live entry
   with that run's exact title, cross-checked on headline source and date
   (the ID_POLICY §8.4 criterion). Record "none" or "several" honestly.
5. **Prove the classifier fires (agreement 6).** Before reporting counts, show
   `INC-00004` classified `different-incident` at both boundaries. Show one
   hand-picked retitle classified `retitle`. Then corrupt one ID's history
   (swap a later run's headline source and date into an earlier run) and show
   the class changes.
6. **Second route.** A reviewer re-derives the `different-incident` set by a
   different method, for example per-run comparison of the first reference
   URL's host and path. Do not re-run step 3. Report agreement per ID, not
   as a total.

## Outputs (all committed before review)

- `docs/audits/ID-reuse-audit-<date>.json`: one object per in-scope ID, with
  its runs (tags, title, date, headline source, successor), the class of
  each boundary, and evidence strings.
- `docs/audits/ID-reuse-audit-<date>.md`: counts per class, split by current
  status (`live`, `withdrawn`, `release-dependent`, `group`, `successor`); the
  fire proofs; the second-route agreement table; and the list of
  `undetermined` IDs.
- **Proposals for a user ruling, not applied:**
  - (a) Retired IDs with `different-incident` boundaries: release-scoped
    records plus an unscoped restatement, as for `INC-00497` and `INC-00554`.
  - (b) Live IDs with `different-incident` boundaries: what to publish. Note
    that a release-scoped record for a *live* ID has no meaning today
    (`resolve_id_status()` ignores `release=` for live IDs), so this needs an
    API and schema decision first.
  - (c) Whether §4 rule 1 should be reworded to the guarantee the project
    actually keeps: a retired number is never issued to a new entry.
- A `CORRECTIONS.md` row with the classified counts, replacing the
  unclassified "591 with more than one title" figure used on 2026-10-10.

## Owner and dependencies

Owner: schema-architect (WS3). The ID policy is WS3's. Proposal (b) touches
the package API and the schema. Independent of D69, which is applied on this
branch. No release is blocked by this audit: the false claim is corrected on
every live surface now, and the audit replaces the corrected claim's figures
with classified ones.
