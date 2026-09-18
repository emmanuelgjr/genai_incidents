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
2. **Definition vs code.** `_derive_tier` is compared against the *documented*
   rule, re-implemented from the prose, over an exhaustive truth table that
   includes `category == "real-world"` — a second derivation path, not a
   rerun of the first. *Fires when:* code and published definition drift in
   either direction. This is the check that was missing when §3.3 happened.
3. **New variants cannot appear silently.** Producers are **discovered by
   scanning** `scripts/*.py` for reads of the two root artifacts; the
   registry records only each script's disposition (`CARRIES` / `INHERITS` /
   `INTERNAL`). *Fires when:* a new exporter appears undeclared, or a
   registered one disappears. A hand-maintained list that nothing forces to
   grow is the hole `check_dead_filters.py` was bounced for; discovery-by-
   scan is the same correction applied here.
4. **The freeze does not become permanent silence.** The assertions against
   the **committed** artifacts are `xfail(strict=True)`, not skipped — a
   skipped test is a check that cannot fail. They fail today (correctly:
   `data/` is frozen). On the first post-freeze rebuild they XPASS, strict
   mode reports XPASS as a FAILURE, and whoever rebuilds must delete the
   marker. **The gate re-arms itself; nobody has to remember.** A control
   test asserts the same property against `data/incidents.json`, which has
   always held — if that one ever fails, the published figure is wrong and
   the xfails would be misleading.

Result on this branch: **24 passed, 4 xfailed**; full suite **381 passed, 4
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
| `category == "real-world"` re-added to `_derive_tier` (the historical defect) | `test_derive_tier_matches_the_published_definition`, `test_category_real_world_is_not_a_landmark_criterion`, `test_fixture_spans_both_tiers` |
| one character changed in the package's schema copy | `test_schema_copies_are_byte_identical` |
| `genai-incidents:tier` tag removed from `export_misp.py` | `test_misp_feed_tags_tier` |
| a new `scripts/*.py` added that reads `data/incidents.json` | `test_no_unregistered_distribution_producer` |

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
  cross-reference removed, carry-everywhere commitment.
- `docs/DATA_DICTIONARY.md` — `tier` row corrected; new
  "Reproducing the landmark count" section with the per-variant table and
  the carry-in caveat.
- `scripts/merge_and_dedupe.py` — `tier` in `_slim_entry`.
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
python -m pytest tests/test_landmark_distribution.py -q   # 24 passed, 4 xfailed
python -m pytest -q                                       # full suite
python scripts/validate.py
python scripts/check_stats_drift.py
python scripts/check_dead_filters.py
git diff --stat origin/main -- data/                      # empty: D25(a) held
```

To watch the gate fail (then `git checkout --` the file):

```bash
# delete the `"tier": e.get("tier"),` line from _slim_entry, then:
python -m pytest tests/test_landmark_distribution.py -q   # 4 failures
```
