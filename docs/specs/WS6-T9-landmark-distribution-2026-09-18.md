# WS6-T9 — the `landmark` subset is not selectable in what we distribute

**Status:** decision made, mechanism implemented, carry-in blocked on the
D25(a) data freeze. **One item for the user** (§8).
**Author:** schema-architect (WS3 owns `schema/` and field shape).
**Date:** 2026-09-18. **Record, not a source — do not regenerate.** If later
work overtakes any part of this, append a dated update naming which half
changed; do not rewrite the text above it (working agreement 4).

---

## 1. Recommendation, in one sentence

**Ship it** — carry `tier` into every distributed variant, because the
README's instruction is correct and the field's absence from the slim
variants was never a decision: it is a one-line omission from the commit
that introduced the field, and that omission is now measurably corrupting
the published definition as well as the published count.

---

## 2. The two positions, and why "retire the instruction" loses

The brief was explicit that the answer was open, so both were costed.

**Retire the instruction** would mean deciding that `tier` is
curation-internal and that README should stop telling people to cite it.
Rejected on three grounds:

1. **The instruction is substantively right.** The corpus total is
   dominated by CVE/GHSA/OSV bulk. Citing 13,060 as "notable AI incidents"
   is precisely the conflation invariant 1 exists to forbid; README's
   sentence is the mitigation, not the problem.
2. **Retiring the sentence does not retire the figure.** `landmark_count`
   is an invariant-6 stats marker rendered into README, the datasheet, the
   site and the release notes. Removing the guidance while continuing to
   publish the number leaves readers a number with no stated meaning —
   working agreement 6(c) exactly: the claim survives, the ability to check
   it does not.
3. **Something already depends on the field being real.** `validate.py`
   gates `reversibility_class` and `discovery_method` on
   `tier == "landmark"`, and the MISP feed already tags it. `tier` is load-
   bearing today; it is not a curation scratchpad.

**Ship it** is also the smaller change: five one-line-ish additions to
producers, versus rewriting a published instruction and explaining a number
we would keep printing.

---

## 3. Evidence

### 3.1 It was an omission, not a decision

`git show 29273952` (#68, "two-tier landmark vs feed") touched nine files:
`data/incidents.json`, `data/stats.json`, `docs/DATA_DICTIONARY.md`,
`docs/app.js`, `docs/index.html`, both copies of `incident.schema.json`,
`scripts/merge_and_dedupe.py` and `scripts/render_markdown.py`.

It added a `<select id="tier">` with `landmark`/`feed` options to the site
and an `e.tier` predicate to `app.js`. Its diff against
`scripts/merge_and_dedupe.py` contains **no change to `_slim_entry`**.

That is decisive on the question the brief asked. The author shipped a UI
control that reads `tier` from the served payload in the same commit that
failed to put `tier` into the served payload. Nobody weighed slim-variant
inclusion and declined it; the field simply never reached the function, and
the site filter matched zero rows from the day it shipped until WS6-T5
removed it as dead. **No downstream code depends on the absence** — grepped
across `scripts/`, `src/`, `tests/` and `docs/*.js`.

### 3.2 `quality_tier` is not a usable substitute — measured

The brief asks whether the two fields are redundant. They are not, and the
gap is most of the subset.

| Measure | Value |
|---|---|
| `tier`: `feed` / `landmark` | 11,155 / **1,905** |
| `quality_tier`: `reviewed` / `auto` / `curated` | 10,835 / 2,106 / 119 |
| Landmark rows reconstructible from fields present in `incidents.min.json` (`quality_tier == "curated"` or `corpus == "ai-harm"`) | **659** |
| Landmark rows qualifying **only** via `aiid_id` (absent from the slim file) | **1,246** |
| Rows the proxy marks landmark that the code does not | 0 |

So the best a slim-file consumer can do is **659 of 1,905 — 34.6%**, with no
signal that they are missing the other 65%. The proxy is a strict subset,
which is the worst shape: it looks self-consistent and silently undercounts.

Reproduce:

```bash
python - <<'EOF'
import json, collections
full = json.load(open("data/incidents.json", encoding="utf-8"))["incidents"]
mini = json.load(open("data/incidents.min.json", encoding="utf-8"))["incidents"]
print(collections.Counter(e.get("tier") for e in full))
lm = {e["id"] for e in full if e.get("tier") == "landmark"}
px = {e["id"] for e in mini
      if e.get("quality_tier") == "curated" or e.get("corpus") == "ai-harm"}
print("landmark", len(lm), "reconstructible", len(px & lm), "proxy-only", len(px - lm))
EOF
```

### 3.3 A second defect, found while checking the dictionary

The brief asked whether `docs/DATA_DICTIONARY.md`'s definition matches the
data. **It does not, and neither does the schema's.** Both said:

> landmark (curated, AIID-linked real-world, ai-harm, **or real-world-category**…)

The `category == "real-world"` criterion was **removed from the code before
#68 merged** — its own commit message says so ("Sampling showed
category=real-world inflated landmark to 6,215… real-world-category alone
now lands in the feed tier"). The code was fixed; the two documents that
describe it were not.

| Definition | Rows it selects |
|---|---|
| `_derive_tier` (the code, and the published count) | **1,905** |
| `docs/DATA_DICTIONARY.md` + `schema` wording, read literally | **6,918** |
| `INCLUSION.md` §5, which the schema cross-referenced | **10,954** |

Three simultaneous published definitions of "landmark"; the two documented
ones overshoot the code by 3.6x and 5.8x. A consumer could not select the
rows **and** could not correctly reimplement the rule from our own authority
— which is the surface README points them at. Both documents are corrected
in this change; `INCLUSION.md` §5 is §8's item for the user.

### 3.4 Two consequences already on the record

The dead site filter (removed under WS6-T5, with `check_dead_filters.py`
added to catch the shape) and the `v2.10.0` release-note parenthetical
conceding that 1,905 "cannot be reproduced from every distributed variant".
PROGRESS.md records the release gate deliberately not blocking the cut on
it. Both are workarounds for this defect, not independent findings.

---

## 4. Invariant 7 — the letter, the purpose, and the gate

> **Invariant 7.** Raw upstream text only in full JSON; min.json/HF ship
> sanitized variants. *Active from: WS3-T6 done.*

Three separate things to say, kept separate on purpose:

**(a) The letter does not reach `tier`, and this is not a strained reading.**
The invariant's subject is *raw upstream text*. `tier` is a two-value enum
computed by `_derive_tier` from our own derived fields (`quality_tier`,
`aiid_id`, `corpus`) in our own build. No byte of it originates upstream.
It is not an exception to invariant 7; it is outside its subject matter.

**(b) The purpose agrees with the letter here, so there is no divergence to
report.** The slim variants exist to keep licensed upstream prose out of
redistributed files. Metadata is the thing they are supposed to carry — the
same file already carries `quality_tier`, `corpus`, `severity`,
`attack_vector`, `content_license` and `source_freshness`, several of them
added deliberately after invariant 7 was drafted. Excluding a derived enum
would serve no licensing purpose and would defeat the variant's own purpose.
Had letter and purpose diverged, this section would say so; they do not.

**(c) Invariant 7 is not yet ACTIVE, and the plan's description of HF is not
yet true.** Its gate is "WS3-T6 done"; WS3-T6 is not done (`description_safe`
appears nowhere in `schema/`, `data/` or `scripts/`). Today
`scripts/export_huggingface.py` writes each row of `data/incidents.json`
**verbatim** (`json.dumps(inc)`), so the HF export is a full dump, not a
sanitized variant. Two consequences worth stating plainly rather than
leaving for someone to trip over:

- HF **already carries `tier`**. No change is needed there for carry — only
  the dataset card needed to document the field.
- **WS3-T6 must not drop it.** When the sanitizer lands, the natural
  implementation is an allow-list projection, which is exactly how `tier`
  was lost the first time. The gate in §6 is written to fail in that case.

---

## 5. Per-variant mechanism — every variant, stated

A fix that lands in one variant and not the others recreates the defect in a
subtler form, so the full surface is enumerated. "Root" is the file a variant
derives from.

| # | Distributed variant | Root | Producer | Before | Change |
|---|---|---|---|---|---|
| 1 | `data/incidents.json` | — | `merge_and_dedupe.py` | `tier` ✅ | none |
| 2 | `data/incidents.min.json` | 1 | `merge_and_dedupe.py::_slim_entry` | ❌ | **add `tier` (unconditional)** |
| 3 | `docs/data/incidents.min.json` (site download, SHA-256 manifest) | 2 | `render_markdown.py` verbatim copy | ❌ | inherits 2 |
| 4 | `src/genai_incidents/data/incidents.min.json` (**PyPI wheel**) | 2 | `render_markdown.py` verbatim copy | ❌ | inherits 2 |
| 5 | `docs/data/incidents.core.json` (site first paint) | 2 | `gen_docs_core_data.py` | ❌ | **add `"tier"` to `CORE_FIELDS`** |
| 6 | `docs/data/detail/<year>.json` (lazy shards) | 2 | `gen_docs_core_data.py` | ❌ | none — deliberately core, not detail (§5.1) |
| 7 | Hugging Face `dist/hf/incidents.jsonl` | 1 | `export_huggingface.py` | `tier` ✅ | card documents it; see §4(c) |
| 8 | `data/incidents.stix.json` + `docs/data/` mirror | 1 | `export_stix.py` | ❌ (`x_quality_tier` only) | **add `x_tier`** |
| 9 | `docs/taxii2/` static TAXII | 8 | `export_taxii.py` (`from export_stix import build_bundle`) | ❌ | inherits 8 |
| 10 | `docs/misp/` feed | 1 | `export_misp.py` | `genai-incidents:tier` tag ✅ | none |
| 11 | `INCIDENTS.md`, `docs/incidents/<year>.md` | 1 | `render_markdown.py` | not rendered | none — prose surfaces, not selectable data |
| 12 | `data/stats.json` → invariant-6 markers | 1 | `render_markdown.py` | `landmark_count` ✅ | none |
| 13 | Python API `query()` | 4 | `src/genai_incidents/__init__.py` | no `tier=` kwarg | **add `tier=`** |
| 14 | `docs/og-image.png` | 2 | `make_og_image.py` | counts only | none |
| 15 | **Site CSV export** (the file a visitor downloads) | 5 + 6 | `docs/app.js` `CSV_COLUMNS` | ❌ | **PENDING — deferred to WS6, see §5.4** |

**5.4 The CSV export — deferred, and said out loud.** `docs/app.js` builds
the site's CSV from a hardcoded `CSV_COLUMNS` list carrying
`['quality_tier','Quality']` and no `tier`. Without this row, the first
post-freeze rebuild would give every distributed variant the selector
**except the file a visitor actually downloads** — this task's own defect,
surviving inside the fix.

It is **not changed here**, for a reason and not by omission: `CSV_COLUMNS`
reads the served payload, which does not carry `tier` until the rebuild, so
adding the column now ships a blank column to every CSV download in the
meantime. It is sequenced with the site filter restoration in §7 step 3, and
held open by `test_site_csv_export_carries_tier` — strict-xfail, so the
moment WS6 adds the column the marker must be removed.

**5.5 Why this variant was missed, which matters more than the variant.**
The §6(3) producer registry exists precisely to stop "the fix reached some
variants and not others", and it did not catch this: discovery globbed
`scripts/*.py` while the registry's own written definition — "derived from
one of the two root artifacts" — plainly covers `app.js`. The scan was
scoped to the language the author was working in rather than to the
definition the registry states. Discovery now covers `docs/*.js` as well,
`app.js` is registered `PENDING`, and
`test_discovery_covers_the_site_as_well_as_the_scripts` fails if anyone
narrows it back.

**5.1 Why `tier` is core and not a detail shard.** The site's filter, stats
and chart path reads only `incidents.core.json` on first load. A `tier` in a
lazy per-year shard would reproduce the state-dependent-search defect WS6-T5
found with `primary_reference`: a filter whose answer depends on which rows
happen to have been expanded. Same reasoning, recorded in the code.

**5.2 What is NOT in scope here.** The site's Tier `<select>` is **not**
restored by this change. Restoring it now would put a control back on the
page against a payload that will not carry the field until the first
post-freeze rebuild — `check_dead_filters.py` would fail, correctly. That
restoration is WS6's, sequenced after the rebuild (§7).

**5.3 Schema.** The field already existed in `schema/incident.schema.json`;
no structural change was required, so there is **no migration**. What did
change is its `description`: the retired `real-world-category` clause is
gone, the `INCLUSION.md §5` cross-reference is gone (§3.3), the derivation
is stated exactly, and the carry-everywhere commitment is written down where
the README sends people. Both schema copies are updated and a test now
asserts they stay byte-identical — the package's copy is itself a
distributed variant, and a drifted copy is this same defect one level up.

---

## 6. The gate — `tests/test_landmark_distribution.py`

Four jobs, and for each, the input that makes it fail (working agreement 6):

1. **Per-variant carry.** Slim, core-bundle, HF, STIX and MISP outputs are
   built from a real rebuild in `tmp_path` and compared to the full file
   **id-by-id**, not total-to-total, because an aggregate that still
   balances while rows inside it are wrong is form 6(d). *Fires when:* any
   producer stops emitting the field. **Measured:** deleting the `tier` line
   from `_slim_entry` failed 4 tests; deleting `x_tier` from `export_stix`,
   `"tier"` from `CORE_FIELDS` and `"tier"` from `query`'s filter dict
   failed 3 more (7 failures total, all restored).
2. **Definition vs code, genuinely in both directions.** The published
   definition is stated **machine-readably** in the schema, at the `tier`
   property's `x-derivation` (criteria as data, plus a `retired_criteria`
   list). The test builds its predicate **by reading that object** and
   compares it to `_derive_tier` over an exhaustive truth table. *Fires
   when:* a criterion is added or removed on **either** side — code-only and
   schema-only changes each break the equality. A second test requires that
   re-applying each `retired_criteria` entry would **change** the outcome, so
   "this criterion is retired" is falsifiable rather than merely asserted.
   The prose check is kept alongside and now **states its own limit**: token
   presence catches a criterion deleted from the prose and cannot catch one
   added, which is why `x-derivation` exists.

   *This replaced a check that did not do what it claimed — see §11(D2).*
3. **New variants cannot appear silently.** Producers are **discovered by
   scanning** `scripts/*.py` **and `docs/*.js`** for reads of the root
   artifacts (including the site's `incidents.core.json` / `data/detail/`
   shards); the registry records only each producer's disposition (`CARRIES`
   / `INHERITS` / `PENDING` / `INTERNAL`). *Fires when:* a new producer
   appears undeclared, or a registered one disappears. A hand-maintained
   list that nothing forces to grow is the hole `check_dead_filters.py` was
   bounced for; discovery-by-scan is the same correction applied here —
   **and §5.5 is what happened when that scan was scoped by file extension
   instead of by the definition.** The root-artifact pattern anchors
   `data/detail/`: unanchored, `detail/` matches NVD advisory URLs and
   dragged two ingest scripts in as false positives.
4. **The freeze does not become permanent silence.** The assertions against
   the **committed** artifacts are `xfail(strict=True)`, not skipped — a
   skipped test is a check that cannot fail. They fail today (correctly:
   `data/` is frozen). On the first post-freeze rebuild they XPASS, strict
   mode reports XPASS as a FAILURE, and whoever rebuilds must delete the
   marker. **The gate re-arms itself; nobody has to remember.** A control
   test asserts the same property against `data/incidents.json`, which has
   always held — if that one ever fails, the published figure is wrong and
   the xfails would be misleading.

Result on this branch: **30 passed, 5 xfailed**; full suite **387 passed, 5
xfailed**.

### 6.1 Proof that each gate fires

A gate nobody has seen fail is a gate nobody should cite, so every check was
broken deliberately and restored. Each row is a real run on this branch.

| Input corrupted | Tests that failed |
|---|---|
| `"tier"` line deleted from `_slim_entry` | `test_min_json_carries_tier_for_every_row`, `test_min_json_tier_is_never_null`, `test_landmark_count_reproducible_from_min_json`, `test_site_core_bundle_carries_tier` |
| `"tier"` removed from `CORE_FIELDS` | `test_tier_is_a_core_field_not_a_lazy_detail_shard` (+ the core-bundle carry test) |
| `x_tier` removed from `export_stix.py` | `test_stix_sdo_carries_x_tier` |
| `"tier": tier` removed from `query`'s filter dict | `test_package_query_filters_on_tier` |
| `category == "real-world"` re-added to `_derive_tier` (the historical defect, code side) | `test_derive_tier_matches_the_published_definition_in_both_directions`, `test_retired_criteria_are_genuinely_retired_and_the_check_is_not_vacuous`, `test_fixture_spans_both_tiers` |
| one character changed in the package's schema copy | `test_schema_copies_are_byte_identical` |
| `genai-incidents:tier` tag removed from `export_misp.py` | `test_misp_feed_tags_tier` |
| a new `scripts/*.py` added that reads `data/incidents.json` | `test_no_unregistered_distribution_producer` |
| **every standalone `tier` token stripped from `gen_docs_core_data.py`** (the input that silently PASSED before review) | `test_every_carrying_producer_actually_names_the_tier_field` |
| a source naming only `quality_tier` / only `x_tier` | `test_the_carries_check_is_not_satisfied_by_quality_tier` |
| **`category == "real-world"` added to the SCHEMA definition only, code untouched** (the direction that was invisible before review) | `test_derive_tier_matches_the_published_definition_in_both_directions`, `test_retired_criteria_are_genuinely_retired_and_the_check_is_not_vacuous` |
| `tier` added to `docs/app.js` `CSV_COLUMNS` | `test_site_csv_export_carries_tier` (XPASS(strict), forcing the marker's removal) |
| `quality_tier` column deleted from `CSV_COLUMNS` | `test_csv_columns_cover_every_core_field_that_is_a_filter_selector`, `test_csv_columns_parse_is_not_vacuous` |
| a CSV column naming a field the payload has not got | `test_csv_columns_reference_no_field_the_payload_cannot_supply` |
| discovery narrowed back to `scripts/*.py` only | `test_discovery_covers_the_site_as_well_as_the_scripts`, `test_registry_has_no_stale_entries` |

Two of those deserve a note. The `_derive_tier` break also tripped
**`test_fixture_spans_both_tiers`**, the guard-on-the-guard: re-adding the
retired criterion collapsed the test corpus to a single tier, which is
exactly the condition under which the carry assertions would stop being able
to catch a hardcoded value. It fired without being asked to.

And the self-rearming claim in §6(4) was verified rather than assumed — a
throwaway `@pytest.mark.xfail(strict=True)` test whose body passes reports
`[XPASS(strict)] … FAILED`, confirming that the first post-freeze rebuild
turns the two committed-artifact xfails into failures that must be cleared.

---

## 7. Carry-in — what is true today vs after the rebuild

`data/` is frozen under D25(a) and a rebuild is what populates the slim
variants, so this change is **the decision and the mechanism, not the
regenerated files**. Published data is byte-identical on this branch
(`git diff --stat origin/main -- data/` is empty).

**Reproducible from a distributed artifact today:** `data/incidents.json`,
the Hugging Face export, the MISP feed.
**After the first post-freeze rebuild + `make build`:** additionally the slim
JSON, its site and PyPI copies, the site core bundle, STIX and TAXII.

### 7.1 The post-rebuild state, measured rather than argued

A full build was run in a **scratch copy** of the tree — `parse_existing.py`
then `merge_and_dedupe.py`, the `make merge` order; running
`merge_and_dedupe.py` alone against a stale snapshot produces spurious
movement — and compared per-entity against the frozen published data.
Nothing under `data/` was touched.

| Measure | Published (frozen) | Rebuilt |
|---|---|---|
| entries, full / slim | 13,060 / 13,060 | 13,060 / 13,060 |
| ID set | — | **identical** (0 added, 0 removed) |
| `landmark` in the **full** file | 1,905 | **1,905** |
| `landmark` in **`incidents.min.json`** | *field absent* | **1,905** |
| `data/stats.json` `landmark_count` | 1,905 | — |
| rows whose `tier` moved | — | **0** |
| slim-variant field delta | — | **`tier`: 0 → 13,060 rows. Nothing else.** |
| other slim fields differing per-entity | — | **NONE** |

That last pair is the field-level delta working agreement 2 requires: the
only intended change is the added field, and no unintended field moved. And
the row that matters for this task's purpose is the fourth — **the rebuilt
slim file yields exactly the published `landmark_count`**, so after the
rebuild the figure README tells readers to cite is reproducible from the
slim artifact, not merely asserted to be.

Reproduce (in a scratch copy, never in the repo):

```bash
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
python - <<'EOF'
import json
mini = json.load(open("data/incidents.min.json", encoding="utf-8"))["incidents"]
print(len(mini), sum(1 for e in mini if e.get("tier") == "landmark"))   # 13060 1905
EOF
```

Sequenced follow-ups, for whoever lifts the freeze:

1. Rebuild; confirm the field-level delta is `tier` added to the slim
   variants and **nothing else** (working agreement 2).
2. Delete the two `xfail` markers in `tests/test_landmark_distribution.py`
   — the suite will demand it.
3. Hand WS6 the restoration of the site's Tier `<select>`, with
   `data-filter-field="tier"`; `check_dead_filters.py` will then pass on it.
4. Drop the `v2.10.0`-era parenthetical from future release notes, which is
   a live surface and corrected in place (working agreement 4). **The
   `v2.10.0` note itself is a dated record and stays as written** — it was
   true when written.
5. Re-run `scripts/gen_data_integrity.py`; the site SHA-256 manifest covers
   `docs/data/incidents.min.json`.

---

## 8. For the user — one ruling

**`INCLUSION.md` §5 contradicts the code, and `INCLUSION.md` is policy, not
schema.** §5 defines the two tiers as `quality_tier: curated/reviewed` vs
`auto` — **10,954** rows, versus the **1,905** the code marks and we publish.
The schema cited §5 as its authority; that cross-reference is removed here
rather than left pointing at a contradiction, but §5 itself is untouched.

Two ways to close it, both cheap, and it is a policy call:

- **(a) Reword §5 to describe the code** (curated OR AIID-linked OR ai-harm).
  Records that `tier` is a notability axis and `quality_tier` a vetting axis,
  and that §5 has always meant the former.
- **(b) Keep §5's intent and rename what it describes.** If §5 genuinely
  means "the reviewed core" — a different, defensible idea — then it is
  describing `quality_tier`, and should say so, leaving `tier` documented
  only by the dictionary and schema.

Recommendation: **(a)**. §5's own heading is "Tiers" and its closing line is
"Headline claims should cite the curated set, not the raw total" — the same
sentence README makes about `landmark`. It reads as the field's design note,
written before the field's derivation was narrowed in #68 and never updated.

Owner once ruled: whoever owns `INCLUSION.md` (governance-scribe / WS5),
not this task.

---

## 9. Files changed

- `schema/incident.schema.json`, `src/genai_incidents/schema/incident.schema.json`
  — `tier` description: exact derivation, retired clause removed, §5
  cross-reference removed, carry-everywhere commitment; plus the new
  `x-derivation` object stating the rule machine-readably (§6(2)). An
  unknown keyword annotates and does not constrain — `validate.py` still
  reports `13060/13060 entries valid`.
- `docs/DATA_DICTIONARY.md` — `tier` row corrected; new
  "Reproducing the landmark count" section with the per-variant table and
  the carry-in caveat.
- `scripts/merge_and_dedupe.py` — `tier` in `_slim_entry`; `_derive_tier`'s
  docstring no longer cites INCLUSION.md §5 (§11 D4) and points at
  `x-derivation` as its machine-readable twin.
- `scripts/gen_docs_core_data.py` — `tier` in `CORE_FIELDS`.
- `scripts/export_stix.py` — `x_tier` on the incident SDO.
- `scripts/export_huggingface.py` — dataset card documents `tier` + a filter
  example.
- `src/genai_incidents/__init__.py` — `query(tier=…)`.
- `tests/test_landmark_distribution.py` — new gate (§6).
- No change to `data/`, `docs/index.html`, `docs/app.js`, `PROGRESS.md` or
  `MASTER_IMPROVEMENT_PLAN.md`.

## 10. Verification recipe

```bash
python -m pytest tests/test_landmark_distribution.py -q   # 30 passed, 5 xfailed
python -m pytest -q                                       # 387 passed, 5 xfailed
python scripts/validate.py                                # 13060/13060 valid
python scripts/check_stats_drift.py                       # clean
git diff --stat origin/main -- data/                      # empty: D25(a) held
```

`python scripts/check_dead_filters.py` exits 1 with
`docs/data/incidents.core.json not found — run make docs-data first`. That is
**pre-existing and not caused by this change**: the core bundle is a CI build
artifact and is not committed (`git ls-files docs/data` lists only
`incidents.min.json`), so the script behaves identically on `main`.

To watch the gate fail (then `git checkout --` the file):

```bash
# delete the `"tier": e.get("tier"),` line from _slim_entry, then:
python -m pytest tests/test_landmark_distribution.py -q   # 4 failures
```

---

## 11. Review corrections — BOUNCE #1 (2026-09-18, same day)

Recorded rather than quietly patched, because three of the four were
**instances of this project's house failure mode inside the gate written to
enforce the rule against it**, and that is worth more as a record than as a
clean diff. The reviewer confirmed the decision, the mechanism and the
invariant-7 reading; what bounced was the gate.

**D1 — a check that could not fail, in four of seven cases.** The original
`test_every_carrying_producer_actually_mentions_tier` asserted `"tier" in
src`, which the substring **`quality_tier`** satisfies. Proven by the
reviewer: stripping every standalone `tier` token from
`gen_docs_core_data.py` left it passing. Vacuous for `merge_and_dedupe.py`,
`gen_docs_core_data.py`, `export_huggingface.py` and `export_stix.py` — and
its docstring claimed the opposite. **The tell was in this document:** it was
the one check absent from the §6.1 proof-of-fire table, i.e. the one never
seen to fail. Now masks the compound names before testing, with a companion
test feeding it the exact input that used to pass.

**D2 — a claim of bidirectionality that was false.** §6(2) originally read:

> *"`_derive_tier` is compared against the documented rule, re-implemented
> from the prose… Fires when: code and published definition drift in either
> direction. This is the check that was missing when §3.3 happened."*

The "documented rule" was a hand-copy of `_derive_tier` in the test file, so
only the code side could ever move: re-adding `category == "real-world"` to
all three published definitions gave **24 passed, 0 failures**. Against the
pre-fix prose it did fail three tests — but every one reported `tier
definition omits aiid_id`, firing on a *missing token*, not on the spurious
criterion that inflated the definition 3.6x. **The claim was true by accident
of vocabulary, not by the asserted mechanism.** Fixed by making the published
definition machine-readable (`x-derivation`) and driving the test's predicate
from it; the prose check now states its own limit instead of implying more.

**D3 — the missed variant: the site's CSV export.** See §5.4 and §5.5. The
substantive point is §5.5: the registry that exists to stop partial fixes
was scoped by file extension rather than by its own definition, so it could
not see `app.js`.

**D4 — a fourth surviving pointer.** `_derive_tier`'s docstring still opened
*"Two-tier split (INCLUSION.md §5)"* — the function the schema now calls the
definition of record still citing the authority removed elsewhere in this
change for contradicting it. Removed; the docstring now points at
`x-derivation`.

**Reviewer error, corrected — noted because it affects a published figure.**
The review advised that a post-freeze rebuild moves the totals
(13,060→13,075, landmark 1,905→1,846). That was its own artefact: it ran
`merge_and_dedupe.py` without `parse_existing.py` first, against a stale
snapshot. Re-derived correctly (§7.1), the rebuild is a no-op on counts and
IDs, and the rebuilt slim file yields **landmark = 1,905**, exactly the
published `landmark_count`. **No published figure moves.**
