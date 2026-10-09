# Design note: where AIRI's review date lives (D57): 2026-10-09

Dated record by schema-architect (WS3), branch `ws3/v2130-schema-disputed-reviewby`.
Do not regenerate. If a later change overtakes it, add a dated update below and
leave this text as it is (working agreement 4).

## Question

User ruling D57 (option A of `docs/audits/airi-navigator-sunset-memo-2026-10-09.md`)
keeps the 1,382 AIRI Navigator rows frozen and marked stale, with a review date
of 2027-01-07. Memo §7 proposed a new optional `review_by` date in the registry's
`source` definition (`schema/source_freshness.schema.json`), next to `hold`. It
would be required whenever `status` is `stale` and propagated per row as the
minimum `review_by`, so that STIX/MISP/HF consumers can see the date.

The registry already has `hold {decision, until, note}`, described as "an open
decision about this source's future, with the date it must be resolved by".
AIRI's hold (D8, until 2026-08-28) had lapsed.

## Decision

1. **No separate `review_by` in the registry.** The review date is `hold.until`.
   A new hold `{decision: "D57", until: "2027-01-07", note}` replaces the lapsed
   D8 hold. The note records the D8 hold and its lapse, so the history is kept in
   the record rather than overwritten silently.
2. **`hold` is required on every `stale` source**, through a schema `if/then`
   in `schema/source_freshness.schema.json`. `scripts/validate.py` applies that
   schema to the registry. This keeps the memo's real requirement: no stale
   source can be undated.
3. **The per-row marker does carry the date**, as `source_freshness.review_by`.
   It is the earliest `hold.until` among the row's listed stale sources. This
   mirrors `as_of`, which is the earliest `last_success`, and the row field is
   named after the registry concept in the same way that `as_of` is named after
   `last_success`. It is derived in `scripts/merge_and_dedupe.py` and
   cross-checked in `validate.py` `check_source_freshness` (rule 8: equal to the
   earliest `until`, and absent iff no listed source has a hold).

## Reasons

- **Near-duplicate fields drift.** `review_by` ("the date a human must re-decide
  this stale source") and `hold.until` ("the date the deferred decision becomes
  live") describe the same commitment. The memo itself distinguishes them only as
  a "decision deadline for a named decision". D57 is a named decision, and its
  deadline is the review date. With two fields, the registry could say
  `review_by: 2027-01-07` with `hold.until: 2026-08-28`. That is the internally
  stale state the memo found (§5) and would make it expressible permanently. One
  date, one meaning, one place.
- **Requiring the hold when stale is the part of §7 that matters.** It turns
  "a stale source may be undated" from a convention into a failing build.
- **Per-row propagation is needed, and it costs no `updated` churn.** D57 asks for
  the review date on the HF rows, and the HF export dumps rows verbatim. The
  `incidents.min.json` consumer may not see the `airi-navigator` tag at all,
  because tags are truncated to 8. So the date has to be on the row, by the same
  self-sufficiency argument that put `as_of` there. The concern in the brief was
  that 1,382 rows would bump `updated`. That premise is **false**:
  `source_freshness` is outside `_CONTENT_FIELDS`
  (`scripts/merge_and_dedupe.py:1435-1446`, and the comment at the marker
  derivation), so adding `review_by` changes only that one sub-field. The
  delta measures this: `docs/audits/cve-sweep/v2130-schema-delta-2026-10-09.json`
  shows 1,382 entries with exactly one changed field, `source_freshness`, and
  0 `updated`/`last_seen` changes outside the 22 disputed entries.
- **Declarative, not wall-clock.** Neither the registry `until` nor the row
  `review_by` is compared with today in the build path, which stays
  deterministic. A passed date reads as overdue. Raising an alert is for a
  scheduled check or a human (memo §7 item 1), and is not built here.
- **Not done here:** STIX `x_source_freshness`, MISP machinetags, and the HF card
  wording (memo §7 items 3-5). These are WS6, v2.13.0 item 8. They can read
  `source_freshness.review_by` directly from each row.

## How data/source_freshness.json was changed

The brief's premise was that `data/*.json` must never be hand-edited and that the
file should be changed "through its producer". For this file the producer **is**
a reviewed hand edit. The registry is a documented curated input, in the same
class as `data/curation_overrides.json`. Its `_note`, `docs/DATA_DICTIONARY.md`
("hand-authored, reviewed, and read by the build ... Nothing in the build writes
it"), and the `_load_source_freshness_registry()` docstring ("written by
nothing") all say so. `grep` finds no script that writes it, only readers
(merge, validate, the HF export). The edit changes only `hold`.
`check_registry_provenance` compares `status`/`last_success` against
`main:ingest/_state/source_health.json` and still reports VERIFIED.
`observed_at` is deliberately unchanged, because no new health snapshot was
reconciled.

## Verification recipe

```
python scripts/validate.py          # registry valid; 1382 markers; review_by rule 8 passes
python -m pytest tests/test_validate.py -q -k "review_by or hold"
python - <<'PY'
import json
d=json.load(open("data/incidents.json",encoding="utf-8"))["incidents"]
m=[e for e in d if e.get("source_freshness")]
print(len(m), {e["source_freshness"].get("review_by") for e in m})   # 1382 {'2027-01-07'}
PY
```
