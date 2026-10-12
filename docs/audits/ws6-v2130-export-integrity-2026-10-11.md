# v2.13.0 item 8: export integrity, design and field-level delta (2026-10-11)

Dated record by distribution-engineer (WS6), branch `ws6/v2130-export-integrity`, from
main `6da13032`. Do not regenerate. If a later change overtakes it, add a dated update
below and leave this text as it is (working agreement 4).

Item (verbatim): "Export integrity: STIX modified bumps on content change (derive from
updated + exporter version); SHA256SUMS covers STIX/TAXII/MISP; build_manifest.json
(commit, built_at, incident_count, retracted_count, landmark_count, taxonomy_versions) on
every channel." With D57 (STIX/MISP/HF surface the AIRI review date) and D64 (disputed
rendering and count).

## 0. Premises checked (the brief was partly wrong)

| Premise | Finding |
|---|---|
| "STIX `modified`: derive from `updated` + exporter version" | Half already true. `export_stix.py` set `modified = _ts(updated or added or date)` (date at `.000Z`) and `created = _ts(added or date)`. What was missing is the exporter-version half, plus a gap in `updated` itself (section 1.3). |
| "SHA256SUMS: find where it is produced" | One place: `scripts/gen_data_integrity.py`, covering `docs/data/**/*.json` only. In `pages.yml` it ran BEFORE `export_stix.py`, so the **live** `data/SHA256SUMS` lists only `incidents.core.json`, `incidents.min.json` and `detail/*.json`: it never listed the STIX bundle, and `taxii2/` and `misp/` have no sums (404). The reorder is the real fix. |
| "GitHub release assets: find the producer" | There is none. `gh release view v2.12.0 --json assets` returns `[]`. A Release carries no assets, so there was nothing to put a manifest or sums beside. `release-assets.yml` is new. |
| "live STIX/TAXII publishing" | Live `data/incidents.stix.json` SHA-256 `693975e6e0e8...` equals a local export at `6da13032` byte for byte (also six sampled TAXII/MISP files), so the deploy is a verbatim copy and the exporters are deterministic. |
| "MISP: follow the machinetag pattern" | Followed. Separate finding: MISP event `timestamp` was a fixed Jan 1 of the event's year, and MISP decides what to re-pull from that stamp, so no content change ever reached a subscriber. Fixed here (section 2), because the new D57 tags would otherwise never arrive either. This goes beyond the stated item. |

## 1. STIX `modified`

### 1.1 Rule

```
modified = <updated date>T00:00:00.<EXPORTER_VERSION as 3 digits>Z      (never earlier than created)
```

`EXPORTER_VERSION` (`scripts/export_stix.py`, now 1; 0 was the implicit pre-v2.13.0
value) is the millisecond field of an RFC 3339 timestamp, range 0-999, validated. It is
bumped in the same change as any new/removed `x_` property, changed `source_name`, changed
entry-to-object mapping, or re-derivation of an exported field that is not in
`merge_and_dedupe._CONTENT_FIELDS`. `created` is unchanged (`added`, `.000Z`).
Shared objects: `attack-pattern` = the pinned ATLAS `release_date` (floor 2024-01-01);
`vulnerability` = constant (its content is the CVE id); `identity` = newest of all incident
`updated` dates and the taxonomy release dates. The identity over-bumps on every data
refresh by design: it carries `x_taxonomy_versions`, and the ASI/VERIS/CAPEC pins have no
date of their own, so over-bumping one object is the safe direction.

Why milliseconds: STIX 2.1 `modified` must be a timestamp >= `created`; a version
suffix keeps it a real, ordered timestamp, makes one bump = one tick on every object, and
needs no state file. TAXII `manifest.json` `version` is the object's `modified`, so it
follows with no code (`test_taxii_manifest_version_is_the_objects_modified`).

### 1.2 Proof (real corpus, 15,637 incidents, 65,141 objects; script and output)

`python -X utf8 scripts/audit/stix_modified_proof.py` :

```
build A == build B, whole bundle: True (65141 objects)
objects whose bytes changed after editing INC-02800: 8        # 1 SDO, 6 relationships, 1 identity
   x-genai-incident 90e6e4a1b1b4 2026-10-09T00:00:00.001Z -> 2026-10-12T00:00:00.001Z
   relationship ... x6          2026-10-09T00:00:00.001Z -> 2026-10-12T00:00:00.001Z
   identity c4ab5705efbc        2026-10-09T00:00:00.001Z -> 2026-10-12T00:00:00.001Z
all other objects byte-identical: True (65133 objects)
description edited WITHOUT updated bump -> modified unchanged: True
EXPORTER_VERSION+1: modified moved on 65141/65141 objects, every other field identical: True
```

So: no content change = byte-identical SDO across builds; a content change (with the
`updated` bump the merge records) moves exactly that entry's SDO and relationships
(plus the dataset identity); an exporter bump moves everything by 1 ms and nothing else.
The fourth line is the dependency, not a bug: `modified` is only as good as `updated`.

### 1.3 The gap in `updated` (needs a ruling, R1)

`merge_and_dedupe._CONTENT_FIELDS` is the set whose change bumps `updated`. Probing every
field of a real entry (`test_every_exported_entry_field_is_content_or_explicitly_declared`)
shows the SDO also reads five fields that are NOT in it: `tier`, `quality_tier`, `corpus`,
`content_license`, `source_freshness`. Re-deriving any of them changes the SDO and does not
move `updated`, so it reaches STIX consumers only through an `EXPORTER_VERSION` bump. I did
not edit the merge (pipeline-engineer's file). `source_freshness` was excluded on purpose
(design note `ws3-v2130-review-by-design-2026-10-09.md`: registry moves must not churn
`updated`). The test makes the boundary explicit: a NEW exported field in neither group
fails it. Second limit: `updated` is a date, so two content changes to one entry on the
same day give one `modified`.

## 2. MISP event timestamps (extension)

`timestamp` = newest `updated` among the event's incidents (UTC midnight, Unix seconds) +
`export_misp.EXPORTER_VERSION` seconds (now 1). Test: changing one 2025 incident moves only
the 2025 event; a version bump adds 1 s to every event.

## 3. SHA256SUMS and `build_manifest.json`

### 3.1 Determinism decision

`built_at` is **not** wall-clock time: it is the committer date of `commit`
(`built_at_basis: commit-date`) or `SOURCE_DATE_EPOCH` when set. The manifest is written
only in export/release steps (Pages, release-assets, publish, the HF export,
`make integrity`), never by `make build`: a committed file cannot contain its own commit,
and a wall-clock stamp would fail every byte-exact drift gate. Result: rebuilding a commit
gives byte-identical manifests and sums (two full export+integrity runs gave identical
SHA256SUMS: `b34182795a640...` data, `1a0426189bc08...` taxii2, `be17817e924a8...` misp,
`c291d586adbed...` hf). `dirty` records tracked-file changes (false on CI).

### 3.2 Channels

| Channel | Producer | `build_manifest.json` | `SHA256SUMS` | Covers |
|---|---|---|---|---|
| Site `data/` (Pages) | `gen_data_integrity.py` -> `export_integrity.gen_all`, after the exports | `docs/data/build_manifest.json` | `docs/data/SHA256SUMS` | `incidents.stix.json`, `incidents.min.json`, `incidents.core.json`, `detail/*.json`, the manifest |
| STIX bundle | same tree | (same) | (same) | the bundle |
| TAXII (`taxii2/`) | same | `docs/taxii2/build_manifest.json` | `docs/taxii2/SHA256SUMS` | discovery, root, collections, collection, `objects.json`, `manifest.json`, README, manifest |
| MISP (`misp/`) | same | `docs/misp/build_manifest.json` | `docs/misp/SHA256SUMS` | 31 event files, `manifest.json`, `hashes.csv`, README, manifest |
| GitHub Release | new `release-assets.yml` -> `package_release_assets.py` | `build_manifest.json` asset | `SHA256SUMS` asset | `incidents.stix.json`, `incidents.min.json`, `taxii2.zip`, `misp-feed.zip`, manifest (deterministic zips) |
| Hugging Face | `export_huggingface.build()` | `dist/hf/build_manifest.json` | `dist/hf/SHA256SUMS` | `incidents.jsonl`, `README.md`, manifest |
| PyPI | `publish.yml` step -> `export_integrity.py manifest`; shipped by `[tool.hatch.build] artifacts` (the file is gitignored) | `genai_incidents/data/build_manifest.json`; API `genai_incidents.build_manifest()` (None if unstamped) | none (PyPI has its own hashes) | n/a |

Pages additionally re-runs `sha256sum -c` over `_site/data`, `_site/taxii2`, `_site/misp`
(the Jekyll output), so "Jekyll copies these verbatim" is a gate, not an assumption.
`verify_data_integrity.py` checks, per tree, per file: digest, missing, unlisted, manifest
schema (`schema/build_manifest.schema.json`), and manifest counts == `data/stats.json`.
The auto-refresh, atlas-refresh and cve-enrich workflows are untouched (they do not run
the exporters; `render_markdown.py` writes `disputed_count` into stats on their rebuilds).

Wheel check (clean venv, `python -m build --wheel --no-isolation`, install, `python -I`):
the wheel contained `genai_incidents/data/build_manifest.json` and
`genai_incidents.build_manifest()` returned the stamped dict; an unstamped checkout
returns `None` (test).

## 4. D57 and D64

D57. STIX: `x_source_freshness {status, as_of, sources, review_by}` copied from the row,
null keys dropped, only on marked SDOs, not in `labels` (`_source_freshness`, beside
`x_content_license`). MISP: `genai-incidents:source-freshness`, `source-as-of`,
`source-review-by` on every attribute (title, CVE, link) of a marked row, none on others,
`review-by` omitted if the marker has no date. HF: the card defines `review_by`; the rows
already carried it. Counts are derived, not typed: 1,382 marked rows = 1,382 SDOs
carrying `x_source_freshness` = 6,002 MISP attributes of exactly those 1,382 incidents;
`review_by` values equal the registry's `hold.until` (independent path).

D64. `disputed_count` (22) is a **subset** of `incident_count` (15,637); `retracted_count`
(29) is outside it; no combined count exists anywhere (invariant 1). `render_markdown.py`
(sole writer) adds it to `stats.json`; a **DISPUTED** note on the 22 cards (parallel to the
RETRACTED banner, saying the entry stays counted); `INCIDENTS.md` shows both sub-counts as
indented lines under the total; `stats_docs_lib.FORMATTERS` registers `disputed_count` and
`retracted_count` for any surface that quotes them; the HF card states the disputed count
from `stats.json` and `build()` refuses if `stats.json` disagrees with the rows;
`check_stats_drift.py` re-derives all four counts from `data/incidents.json` AND the slim
`incidents.min.json` (two paths) and fails by key.

## 5. Field-level delta against `6da13032`

Method: baseline exports generated at `6da13032` (a throwaway checkout of that commit, then `make stix taxii misp huggingface` equivalents) into scratch, new exports from this
branch, compared with `scripts/audit/export_delta.py` (stix | misp | jsonl | tree).

**Committed artifacts**

| Artifact | Delta |
|---|---|
| `data/incidents.json`, `data/incidents.min.json`, `src/genai_incidents/data/*`, `docs/data/*`, charts, README, DATASHEET, CITATION | none (`git diff --stat 6da13032 HEAD -- ...` shows only `data/stats.json`) |
| `data/stats.json` | +1 key: `"disputed_count": 22` (no other key moved) |
| `INCIDENTS.md` | +2 lines (the two sub-count bullets) |
| `docs/incidents/{2021..2026}.md` | +44 lines = 22 DISPUTED notes + 22 blank lines (2+2+8+12+14+6 = 44); 0 lines removed |
| entry count / ID set | identical (merge re-run is a no-op: `git status` clean after the full chain) |

**STIX bundle (and TAXII `objects.json`, identical content)**: 65,141 -> 65,141 objects, 0
IDs added or removed. Changed fields: `modified` on `attack-pattern` 55 (`2024-01-01T00:00:00.000Z`
-> `2026-09-15T00:00:00.001Z`), `identity` 1 (-> `2026-10-09T...001Z`), `relationship`
40,316 (+1 ms), `vulnerability` 9,132 (+1 ms), `x-genai-incident` 15,637 (+1 ms); and added
`x-genai-incident:x_source_freshness` on 1,382. Nothing else moved.

**TAXII**: `manifest.json` `version` changed on 65,141 records (= the new `modified`); `date_added`
unchanged; new files `SHA256SUMS`, `build_manifest.json`; `README.md` changed (new sections);
`discovery.json`, `root.json`, `collections.json` and the collection resource identical.

**MISP**: 31 events, 101,604 attributes, same UUIDs. `Event.timestamp` changed on 31 events
(and 31 manifest records); `Attribute.Tag` changed on 6,002 attributes, all additions
(`source-freshness` 6,002, `source-as-of` 6,002, `source-review-by` 6,002), 0 removals;
`hashes.csv` identical; `README.md` changed; new `SHA256SUMS`, `build_manifest.json`.

**Hugging Face**: `incidents.jsonl` identical (0 rows changed of 15,637; the rows already
carried `review_by`); `README.md` card +3 text edits; new `SHA256SUMS`, `build_manifest.json`.

**Intended consequence for subscribers**: every STIX/TAXII `modified` moves once and every
MISP event timestamp moves once, so a client that dedupes on version re-imports everything
one time (this also delivers the 2026-10-01 OWASP `source_name` fix that never bumped
`modified`).

## 6. Fire proofs (agreement 6) and re-derivation

`scripts/audit/export_fire_proofs.py` corrupts one source line, runs the guarding check, expects failure,
restores with `git checkout`; all 11 fired:

| Corruption | Check that failed |
|---|---|
| `_ts_v` ignores `EXPORTER_VERSION` | `test_exporter_version_bump...` |
| `modified` stops reading `updated` | `test_content_change_bumps_modified...` |
| SDO exports `confidence` (not a content field) | `test_every_exported_entry_field_is_content_or_explicitly_declared` ("fields ['confidence'] change the STIX SDO but are neither...") |
| `x_source_freshness` not emitted | `-k source_freshness` |
| MISP freshness tags dropped | `test_misp_freshness_machinetags_only_on_marked_rows`, `..._real_feed_...` |
| MISP timestamp back to fixed year epoch | `test_misp_event_timestamp_moves...` |
| `verify_sums` stops comparing digests | `test_verify_fires_on_one_changed_byte_in_each_served_tree[data/taxii2/misp]` |
| `verify_all` stops comparing manifest to stats | `test_verify_fires_on_a_manifest_whose_counts_disagree_with_stats_json` |
| HF build stops shipping manifest/sums | `test_huggingface_build_ships_manifest_and_sums` |
| DISPUTED card branch removed | `test_disputed_card_has_banner_and_says_it_stays_counted` |
| `stats.json` `disputed_count` wrong | `check_stats_drift.py`: "disputed_count is 0 but the rows of incidents.min.json give 22" |

The Pages ordering bug is covered by `test_verify_fires_on_an_export_that_ran_after_the_sums`
(a file served but not listed fails by name).

Re-derive: `python scripts/export_stix.py && python scripts/export_taxii.py &&
python scripts/export_misp.py && python scripts/gen_data_integrity.py &&
python scripts/verify_data_integrity.py`; `python scripts/check_stats_drift.py`;
`git diff --stat 6da13032 HEAD -- data docs/incidents INCIDENTS.md`;
`python scripts/audit/export_delta.py stix <before> data/incidents.stix.json`.

## 7. Not done / not verified

- No live OpenCTI or MISP import was run (WS6-T3/T4 are separate). MISP's extra
  `build_manifest.json`/`SHA256SUMS` in the feed directory are expected to be ignored (a feed
  reader reads `manifest.json`, `hashes.csv` and the event files) but that is unverified
  against a live instance.
- `release-assets.yml`, the new `_site` verification step in `pages.yml` and the `publish.yml`
  stamp step have not run on GitHub; their commands were each run locally, and live
  byte-parity of the Jekyll output was checked on six sampled files. The first real run is
  the next published release.
- `src/genai_incidents/__init__.py` still has `VERSION = "2.0.0"` (WS6-T1); noticed, not touched.
