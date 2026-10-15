# Changelog

All notable changes to the dataset and tooling are recorded here.
The dataset uses [SemVer](https://semver.org/) — major bumps for breaking
schema or ID changes, minor bumps for additive schema fields or large
ingest expansions, patch bumps for routine refreshes and bug fixes.

## [Unreleased]

### Added - `status: unverified` and `unverified_count` (D130, schema machinery only)

- **Additive schema value.** `status` gains `unverified` (with `status_reason.code: no-confirmed-source`) for an entry whose references turn out not to be sources for it and for which no confirmed primary source could be found after a documented effort. It is treated like `retracted`: kept in `data/incidents.json` with its ID resolvable, not counted in `incident_count`, omitted from the site and the STIX/TAXII/MISP/Hugging Face exports. It is set only by a reviewed decision in `data/curation_overrides.json`, never by hand in `data/`.
- **New count.** `unverified_count` (outside `incident_count`, like `retracted_count`) is in `data/stats.json`, `build_manifest.json`, and the envelope of `data/incidents.json` and every `incidents.min.json` copy. In the envelopes it is **always present, 0 included** (D135), so those files change by one header line each; no entry changes. `INCIDENTS.md` gains an "unverified" line.
- **Consumer impact.** No entry is unverified yet (`unverified_count` is 0), so no row and no export changes. Later releases may mark rows unverified, and those rows will then drop out of the exports and out of `incident_count`. A consumer that checks `incident_count + retracted_count == len(incidents)` should add `unverified_count`.
- **Build-manifest schema now requires `unverified_count`.** A v2.13.0 `build_manifest.json` (which lacks the key) fails validation against the new `schema/build_manifest.schema.json`; validate each manifest against the schema shipped with it.
- **Precision sampling.** Future draws by `scripts/precision_sample.py` exclude unverified rows as they exclude retracted ones (D135); the ratified sample is unchanged and still reproduces from its pinned data.

### Changed - a corrupt ingest file now fails the build closed (D129)

- `merge_and_dedupe.py` used to print a WARN for an unparseable `ingest/*.json`, drop that source to 0 rows and exit 0 with its outputs written. It now refuses before any output is written, naming the file and the parse error, with the job-aware abort sentence. A payload that is not a list of rows (a scalar, or `incidents`/`entries`/`data` holding a non-list) is refused the same way. A legitimately empty list, and the dict-shaped side files in `ingest/` that carry no rows (provenance records, CISA KEV, CVE rejections), still load as before. No data change.

### Added - AIID-side lift of the OECD/AIID freeze (D114): 113 new AIID rows, 169 updated rows (INC-17221 to INC-17333)

- **+113 AIID-only rows, INC-17221 to INC-17333.** All are new AIID incidents the frozen
  snapshot did not carry. The title is the only AIID-authored text kept (E23 shape);
  the description is the project template.
- **169 existing rows updated, including 25 title edits** that use the row's own AIID
  snapshot title. **0 merges and 0 tombstones.** No ID is retired or reused.
- **OECD stays held.** The OECD side of the freeze is lifted only after suppression is
  built (D114 precondition); the refresh gate still holds the OECD inputs.
- **Title effects (D116, D119):** `INC-00437` and `INC-14682` switch from the OECD title to
  the AIID title, so OECD-titled rows go from 3,937 to 3,935.
- **Counts:** `incident_count` goes from 15,637 (v2.13.0) to 15,755 (15,784 rows including
  29 retracted), which is the 113 AIID rows plus the 5 AIAAIC rows below.
- AIID changes now ship through the weekly refresh. The first scheduled refresh under D114
  is Sunday 2026-10-18.

### Added - refresh PR #102: +5 AIAAIC rows (D112)

- Five new AIAAIC rows, INC-17216 to INC-17220, merged at `692bb672`. It was the first clean
  scheduled refresh since PR #97 (2026-07-27).

### Changed - AIRI Navigator retired (D108); the D57 hold is resolved (D124)

- **AIRI Navigator is retired as of 2026-10-13 (D108).** Its last successful download was on
  2026-05-31; it has returned 404 since 2026-06-07. It is no longer fetched and no longer alerts (`RETIRED_SOURCES` in
  `scripts/check_source_health.py`); the monthly retry and the `try_airi` workflow input
  are gone. Its rows and provenance stay unchanged and stay marked stale; none is
  deleted or tombstoned.
- **D124 (2026-10-13): D108 resolves the D57 hold.** `data/source_freshness.json` records
  the retirement and the resolution. The registry status stays `stale` (retirement is not
  a freshness value), and each row's `source_freshness` marker is unchanged.
- `make ingest-all` no longer runs `ingest-airi`.

### Changed - licensing own-wording rewrites (D97/D98) and one wrong-CVE fix (4 rows, 0 added or removed)

Merged after the v2.13.0 tag (`e6eb3410`).

- **INC-02436, INC-02646, INC-03233:** `description` rewritten in the project's own wording
  (D97/D98); `updated` and `last_seen` move with it.
- **INC-02382:** `title` and `tags` corrected, with the wrong CVE removed; `updated` and
  `last_seen` move with it.

### Changed - licensing: OWASP LLM mapping files are CC BY-SA 4.0 in part; ingest/ snapshots stay under upstream terms (D96, D99, D101; merge `48ffe0db`)

- **`mappings/owasp_llm_top10_2026.json`, `mappings/owasp_llm_top10_2025.json` and the crosswalk `mappings/owasp_llm_2025_to_2026.json`** are now marked `CC-BY-SA-4.0 AND CC-BY-4.0` (`.reuse/dep5` carve-out). Their OWASP risk codes, names and description or scope text come from, or follow, the OWASP Top 10 for LLM Applications, which is CC BY-SA 4.0 (D96, D99). The dataset itself stays CC BY 4.0.
- **`ingest/*.json`** is declared `LicenseRef-upstream-terms` (D101): these upstream snapshots stay under each upstream's own terms and are not covered by the project's CC BY 4.0 data grant or its MIT code licence. See `NOTICE-DATA` and `docs/SOURCE_LICENSES.md`.

### Fixed - refresh repair (merge `24adc076`): held inputs, overdue alert, empty-result guards

- **D66:** during a refresh the freshly fetched copies of the held OECD/AIID inputs are moved outside the work tree (`scripts/hold_pair_inputs.py`) and the committed versions restored, so the merge sees main's bytes; a guard fails the run before any PR is opened if a held path still differs or stash content is in the tree.
- **D63:** a scheduled overdue alert (`.github/workflows/refresh-overdue-alert.yml`, `scripts/refresh_overdue.py`) opens or updates one issue labelled `refresh-overdue` when no weekly refresh PR has been merged in time, and closes it once one has.
- **Empty-result guards** for the KEV and AIID ingests: a fetch that parses to nothing
  leaves the committed file untouched instead of overwriting it.

### Fixed - over-merge rule (D117); 0 data changes

- Aggregate round-up URLs (the OWASP "round-up" reference pages) are no longer
  reference-URL dedupe keys in `scripts/merge_and_dedupe.py`, so unrelated incidents that
  cite one such page are not merged. Grandfathered pairs still merge. **Published output is
  byte-identical** before and after. The split of the 3 rows already merged is a separate,
  later decision (D118).

### Added - refresh PR tooling: per-field change report (D120), PR-body size caps (D123), loud abort (D121)

- **D120:** the refresh PR reports every AIID-driven field change as a count per field, and lists
  the rows for severity, date, year, corpus, title and attack_vector only, with a flag for
  rows that carry an OECD id.
  It does not block; if it cannot be built it fails soft to a needs-ruling PR.
- **D123:** the report is truncated with a note when long, the full report goes to the
  step summary, and the whole `pr-body.md` is capped below GitHub's 65,536-character
  limit (`scripts/cap_pr_body.py`).
- **D121:** the AIID-side refusal stays fail-closed, and the abort message now says that
  AIAAIC, KEV and the CVE sweep did not ship.

### Fixed - refresh drift gate and AIAAIC loud failure (tooling only)

- The scheduled refresh now renders the doc stats (`render_docs_stats`) and runs
  `check_stats_drift` as a hard step before it opens a PR, so a refresh PR cannot carry
  counts that disagree with the docs. Main's drift check had been red after PR #102.
- `scripts/ingest_aiaaic_sheet.py` fails loudly when a required column is missing
  (`REQUIRED_COLUMNS`) instead of silently emitting fewer fields, and it adapts to the
  2026-10 sheet header. A yield drop below 90% of the committed count needs an explicit
  maintainer override (`accept_aiaaic_yield_drop`), which is now also written to the step
  summary and appended to the refresh PR body (B3). The headline/system sanity check reads
  the mapped id column rather than position 0 (B2).

### Fixed - precision-audit gate follow-ups (register items b4, b17; tooling only, 0 data changes)

- **b4:** `scripts/validate.py` no longer prints "precision: pending, authorised by D76"
  when the gate has found problems (for example a non-ISO `decided` in the marker). The
  line now reads "NOT authorised (N problem(s) ...)". A measured state with problems is
  suffixed "FAILING". On the committed tree the line is unchanged.
- **b17.1:** the audit-directory pin rejects every directory under
  `docs/audits/precision/` except the pinned one. The old date-shaped glob did not see a
  variant such as `2026-10-11b`.
- **b17.2:** `scripts/wilson_ci.py` and `scripts/evaluate_ai_relevance.py` no longer pick
  the newest audit directory. Without `--audit-dir` they refuse (rc 2) if more than one
  directory exists.
- **b17.3:** a precision figure typed into `docs/DATASHEET.md` outside the generated
  block now fails `validate.py` and `wilson_ci.py --check`. The check looks for three
  things:
  - a percentage or a 0.xx proportion in any paragraph, list item or table that mentions
    precision. A sentence-final "0.92." counts. Version strings such as "v2.13.0" and
    "CVSS 9.8." do not. "Precisions" counts as a mention. So does any
    "precision-<word>" compound, such as "precision-recall", "precision-weighted" or
    "precision-at-10", except the two design compounds the ingest rules use,
    "precision-first" and "precision-oriented". A figure next to only one of those two
    is not checked;
  - any figure in the "Measured precision" section, including explanatory ones. Figures
    there must come from the generator;
  - a duplicate block.

  It does not catch a bare integer, a figure written in words, or figures in other files.
  These limits are listed in `stray_precision_figures` and pinned by a test.

## [2.13.0] — 2026-10-13

### Changed - OWASP ASI re-pinned to the 2026 Top 10 for Agentic Applications; citation fixed; OWASP attribution added (v2.13.0 item 9, D78-D80, D83-D88)

- **Metadata relabel only: 0 entries change.** The codes `ASI01`-`ASI10`, their order, all
  ten risk names (D78 keeps the "&" form of ASI02/ASI03) and all ten descriptions are
  unchanged, so per-entry `owasp_asi` (and STIX `x_owasp_asi`) values are untouched:
  0 of 15,666 entries in `data/incidents.json` differ from the previous build, field by
  field, keyed by id; `updated` moves on 0 rows. Evidence:
  `docs/audits/item9-owasp-asi-2026-source-check-2026-10-12.md` (Correction 2 governs).
- **`mappings/owasp_asi_top10.json`:** `framework` "OWASP Agentic Top 10 (ASI)" ->
  "OWASP Top 10 for Agentic Applications" (D79); `version` "2025" -> "2026" (the PDF
  cover states "Version 2026 / December 2025"); `url` now points to the 2026 Top 10
  (<https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>)
  instead of the separate "Agentic AI - Threats and Mitigations" document, which it
  mis-cited. New keys: `citation` (cover title "OWASP Top 10 For Agentic Applications
  2026", edition, publisher, licence) and `related` (Threats and Mitigations v1.1,
  December 2025, cited separately).
- **`taxonomy_versions.owasp_asi` is now "2026"** in `data/stats.json`, the package's
  `taxonomy_versions()`, the STIX identity's `x_taxonomy_versions`, the MISP
  `genai-incidents:taxonomy-owasp-asi` tag and the Hugging Face card. **Consumer
  impact:** anything that keys on `owasp_asi == "2025"` must accept "2026". No exported
  code or name changes.
- **D89 exception notes:** the `.zenodo.json` description and the `CITATION.cff` abstract now
  state that `mappings/owasp_asi_top10.json` is CC-BY-SA-4.0 AND CC-BY-4.0 (the OWASP ASI
  codes and names are CC BY-SA 4.0), pointing to `NOTICE-DATA`.
- **Served TAXII discovery description (D90)** now names the "OWASP Top 10 for LLM
  Applications" and the "OWASP Top 10 for Agentic Applications" (was the unofficial
  "OWASP LLM/ASI" shorthand); the Hugging Face card now uses the current "OECD AI
  Incidents and Hazards Monitor" name for AIM.
- **Display name:** "OWASP Top 10 for Agentic Applications" on the live surfaces
  (`INCIDENTS.md`, README, `docs/TAXONOMIES.md`, `docs/DATASHEET.md`,
  `docs/DATA_DICTIONARY.md`, `CONTRIBUTING.md`, the site, `.zenodo.json`,
  `CITATION.cff`, `pyproject.toml`, the HF card, the coverage chart and the README
  taxonomy map). Every label that introduces or labels the codes carries "(ASI)" after
  the name (D85, extended by D88): the headings, the coverage chart title, the site's
  chart caption, the README banner chip and taxonomy-map card, `CONTRIBUTING.md`,
  `docs/DATA_DICTIONARY.md`, the `docs/TAXONOMIES.md` quick chooser, the README
  mapping-sources line, the `NOTICE-DATA` attribution lead and the
  `docs/SOURCE_LICENSES.md` section 3.6 heading. The mapping file's `framework` stays the
  bare title. The README tagline and red-teamer row now name "the OWASP Top 10 for LLM
  Applications" and "the OWASP Top 10 for Agentic Applications" instead of the
  shorthand "OWASP LLM/ASI (Top 10)" (D87). Four Threats-and-Mitigations mis-citations
  for the ASI codes are corrected (the mapping `url`, README, `docs/TAXONOMIES.md`, the
  site subtitle link); T&M is now cited separately.
- **Older variants of the name renamed too (D86).** "OWASP Agentic ASI Top 10" /
  "OWASP Agentic (ASI)" / "OWASP Agentic" are replaced in: the dataset-level
  `description` of `data/incidents.json` (the only key that moves in that file: 0
  entries change, `updated` moves on 0 rows; it reaches no export, and
  `incidents.min.json` does not carry it); the per-incident label in
  `docs/incidents/*.md` ("**OWASP Top 10 for Agentic Applications (ASI):**",
  13,586 lines in 30 files, one line per entry with ASI codes, nothing else
  changed); the README banner chip (hand-authored SVG; the chips now sit in two rows,
  because the full name with "(ASI)" does not fit one row in DejaVu Sans Bold without
  running into the artwork, and every chip is sized to fit its label in DejaVu Sans
  Bold, Arial and Segoe UI); the README taxonomy-map card (its title now wraps onto two
  lines clear of the "core" badge, `scripts/readme_assets/tax.py`); the social-card image (the taxonomy line is now set at
  26 px and wraps at its separators, because the full name does not fit one line at
  28 px); and the methods paper. The dated 2026-05-25 per-incident-pages plan is a
  record and is left as written. The two schema descriptions that named the
  framework (the top-level `description` and the `owasp_asi` property's) now read
  "OWASP Top 10 for Agentic Applications (ASI)" in `schema/incident.schema.json` and
  its packaged copy (D86); description text only, no type, enum, pattern or
  `required` change.
- **Attribution (D80, D83, D84):** OWASP's CC BY-SA 4.0 licence is verified from the
  PDF. New `docs/SOURCE_LICENSES.md` section 3.6; an OWASP attribution paragraph in
  `NOTICE-DATA` that covers the codes and names wherever they are reproduced; a
  `.reuse/dep5` carve-out for `mappings/owasp_asi_top10.json` (CC BY-SA 4.0 for the codes
  and names, CC BY 4.0 for the project's own descriptions); `LICENSES/CC-BY-SA-4.0.txt`,
  the SPDX License List text (`reuse download CC-BY-SA-4.0`, from
  spdx/license-list-data `text/CC-BY-SA-4.0.txt`; 18,375 bytes) (D84). `NOTICE-DATA` now
  counts eight upstream sources with an obligation detailed in it (it said three), and
  the OWASP attribution in it and in section 3.6 also lists `docs/charts/owasp_asi.svg`,
  which reproduces the ten risk names.
  The 21 `OWASP-*` source ids (18 `OWASP-GENAI-*` and 3 `OWASP-AIX-*`) of
  `ingest/avid_owasp_incidents.json`, folded into 6 rows, are a different
  upstream and stay OPEN.
- **New guard** `tests/test_owasp_asi_naming.py`. Before it, `validate.py` and
  `check_stats_drift.py` caught a stale `owasp_asi` only in `data/stats.json`. The guard
  fails on the retired name (with or without "OWASP", possessive, hyphenated, or split
  by a no-break space, `&nbsp;` or `<br>`), any other "OWASP Agentic ..." variant (no
  site is held, so any variant fails), the "ASI Top 10" / "LLM/ASI Top 10" shorthand
  (D87), the bare "OWASP LLM/ASI" or "OWASP LLM and ASI" used as a name for the two
  frameworks (D90; also with `&`, emphasis or a Unicode slash, and across adjacent Python
  string literals; "OWASP LLM and ASI codes" and the "OWASP ASI" label pass), an
  `owasp_asi` / `owasp-asi` version literal (including the MISP tag form),
  prose edition or title edition that disagrees with the pin, a T&M URL whose link text
  or preceding text does not name Threats and Mitigations, a missing "(ASI)" on a label
  for the codes (D88), a missing "(ASI)" heading, and an old name in the dataset
  description or the per-incident pages. Planted-input tests prove each rule fires, and
  legitimate-text controls prove the prose lists, the dated citation title, slugs and
  correct T&M citations pass. Known limits are stated in the file.

### Changed - tier, quality_tier, corpus and content_license are now content fields (user-ruled, D81/D82)

- **Consumer-visible.** `scripts/merge_and_dedupe.py` `_CONTENT_FIELDS` gains `tier`,
  `quality_tier`, `corpus` and `content_license` (`source_freshness` stays out). From now on a
  licence relabel or a classifier change on a row moves that row's `updated`, and with it its
  STIX `modified` and MISP timestamp, so a consumer keyed on those sees the change. This
  matters most for the 3,767 rows that carry `content_license` today (CVE-TOU 2,171, AIAAIC
  1,517, AVID 79).
- **Reversal.** This knowingly reverses the WS0-T3 link-1 gate ruling (2026-07-27) and the
  shape owner's recommendation that kept `content_license` out of the content set; the
  affected docs are corrected in place and the WS0-T3 spec carries a dated supersession note.
- **Build order.** `tier`, `quality_tier` and `corpus` are now derived before the `updated`
  comparison instead of after it. Without that, every rebuild on a new calendar day would
  have bumped `updated` on 15,657 rows (all except the 9 retained priors); the D73 gate
  measured this on two simulated new days (2026-10-13 and 2026-10-20). With it, the first rebuild moved 0 rows (no `updated`,
  `added` or other field moves, measured against origin/main).
- **Freeze widening (D82).** The D71 stage-1 OECD/AIID freeze now also holds `tier`,
  `quality_tier`, `corpus` and `content_license` changes on published OECD/AIID rows, because
  they are content fields and the freeze gates any content change on those rows. No OECD/AIID
  row carries `content_license` today (0 of the non-retracted OECD/AIID rows; the field is
  populated on 3,767 rows, none of them OECD/AIID), so this holds nothing yet.

### Changed - OECD description provenance labels; refresh merge gate made deliberate (agent-suggested, D58 stage 1)

- Agent-suggested; held for the user's merge ruling (the data change is user-visible
  only through two non-content fields). Labels-only: `description_provenance =
  "original"` and `description_source = "oecd-aim"` are now set on the 3,936
  OECD-template rows that lacked them (3,937 now carry it with INC-00437), from the
  WS4-T12 ingest stamp and a merge-time backfill keyed on the `OECD-AIM-` source id.
  Neither field is a content field, so `updated`, `generated`, counts, titles, IDs
  and `id_deprecations.json` are unchanged (0 rows, 0 deprecations). It is a
  provenance label, not a licence marker. The labels reach `incidents.json` and the
  Hugging Face JSONL export only; not `incidents.min.json`, STIX, MISP, TAXII,
  `INCIDENTS.md`, `docs/incidents/*.md` or `stats.json`.
- The OECD/AIID refresh freeze is now a deliberate gate (D58, extended by D67 and D71: nothing
  from the OECD/AIID pair reaches main until stage 2. It holds added OECD-AIM- and AIID- source rows, upstream
  title edits and, while an OECD/AIID ingest input differs from its commit, any content change to a published
  OECD/AIID row; the baseline is read from git HEAD and the gate fails closed if it is unreadable).
  `merge_and_dedupe.py` aborts with "Nothing was written" when a build would merge or
  retitle a previously published ID through an OECD-AIM-/AIID- source id, edit the
  title of a published OECD/AIID row, or add an OECD-AIM- source row not already
  published, without a signed user approval
  (`docs/audits/D42-approved-refresh-merges.json`, absent; a test asserts the set is
  empty). The weekly refresh gains the AIID snapshot step (WS4-T14, continue-on-error,
  output not committed) and therefore fails at "Re-merge + render + validate" while the
  freeze holds, instead of at the unrelated E21 unit test. That test
  (`test_oecd_aiid_content_disagreement_is_unique_to_inc00437`) is superseded by
  `tests/test_aiid_signal_provenance.py`. See `docs/audits/oecd-stage1-build-2026-10-09.md`.

### Changed - export integrity: STIX `modified`, SHA256SUMS over STIX/TAXII/MISP, `build_manifest.json` on every channel, D57/D64 surfaces (agent-suggested, draft)

- **STIX `modified` now changes when content changes.** It is the entry's `updated` date with
  the exporter version (`EXPORTER_VERSION`, currently 1) in the millisecond field, never earlier
  than `created`: an entry with no content change keeps a byte-identical SDO across builds, a
  changed entry moves forward, and an exporter change moves every object by 1 ms. Before this,
  `modified` was the bare `updated` date, so a change to the exporter (the 2026-10-01 OWASP
  `source_name` relabel) changed object content without changing `modified`. **Every object present in both the v2.12.0 and v2.13.0 bundles gets a new `modified`.** That is
  +1 ms for the 9,132 CVE objects and for the 9,784 incidents and 19,848 relationships whose
  entry is unchanged. The 5,853 incidents and 17,928 relationships whose entry changed take the
  new `updated` date. The 53 surviving ATLAS `attack-pattern` objects take the 2026-09-15 pin
  date. The ATLAS re-map retires 3 `attack-pattern` objects (`AML.T0019`, `AML.T0058`,
  `AML.T0015.001`) and 2,540 relationships, and adds 2 (`AML.T0115.000`, `AML.T0115.001`) and
  2,540 new relationships. A new `identity` object (carrying `x_taxonomy_versions`) appears for
  the first time. The count stays 65,141. Retired objects are not emitted as `revoked`; they are
  dropped. A client that dedupes on (`id`, `modified`) re-imports every surviving object, which
  also delivers the earlier label fix, but keeps the retired objects unless it prunes against
  the current bundle; static TAXII has no deletion signal. TAXII `manifest.json` `version`
  follows. What bumps what: `docs/VERSIONING.md`.
- **MISP event `timestamp` is derived from the data** (newest `updated` among the event's
  incidents, plus the exporter version in seconds) instead of the fixed Jan 1 of the event's year.
  A subscribed MISP decides whether to re-pull an event from that stamp, so no content change had
  ever reached a subscriber.
- **`SHA256SUMS` now covers the STIX bundle, the TAXII collection and the MISP feed.** The Pages
  workflow ran `gen_data_integrity.py` before `export_stix.py`, so the live `data/SHA256SUMS`
  listed only `incidents.core.json`, `incidents.min.json` and the `detail/` shards; it never
  listed the STIX bundle. The step now runs after the exports, writes one `SHA256SUMS` per
  served tree (`data/`, `taxii2/`, `misp/`), and the workflow re-verifies them against the built
  `_site/`. `scripts/verify_data_integrity.py` also checks every manifest against its schema and
  against `data/stats.json`.
- **`build_manifest.json` on every channel** (`commit`, `built_at`, `built_at_basis`, `dirty`,
  `version`, `incident_count`, `retracted_count`, `disputed_count`, `landmark_count`,
  `taxonomy_versions`; schema `schema/build_manifest.schema.json`; counts copied from
  `data/stats.json`): the Pages `data/`, `taxii2/` and `misp/` trees, the Hugging Face dataset,
  the PyPI package (`genai_incidents.build_manifest()`, `None` for an unstamped source checkout)
  and, new, the GitHub Release: a Release carried no assets before; `release-assets.yml` now
  attaches the STIX bundle, `incidents.min.json`, `taxii2.zip`, `misp-feed.zip`,
  `build_manifest.json` and `SHA256SUMS`. `built_at` is the committer date of `commit` (or
  `SOURCE_DATE_EPOCH`), not the wall clock, and the manifest is written only in export/release
  steps, never by `make build`, so builds stay byte-reproducible.
- **D57 on the exports.** STIX incident SDOs of rows carrying a `source_freshness` marker (1,382,
  all AIRI Navigator) gain `x_source_freshness {status, as_of, sources, review_by}` (absent
  elsewhere, never null, not in `labels`); their MISP attributes (6,002) gain the machinetags
  `genai-incidents:source-freshness`, `source-as-of` and `source-review-by`; the Hugging Face
  card now defines `review_by`. The rows themselves are unchanged.
- **D64 on the counts.** `data/stats.json` gains `disputed_count` (22). Disputed entries
  **stay counted**: they are inside `incident_count` (15,637), not beside it, and
  `retracted_count` (29) is outside it; no combined headline count exists. Year-shard cards of
  the 22 gain a **DISPUTED** note, `INCIDENTS.md` shows both sub-counts, the README headline row, the
  DATASHEET Instances line and the site hero carry a templated `stats:disputed_count` subset figure
  (the og/twitter meta descriptions quote neither sub-count, as with `retracted_count`), the Hugging Face card
  states the disputed count, and `check_stats_drift.py` now re-derives `incident_count`,
  `retracted_count`, `disputed_count` and `landmark_count` from the full and slim corpus and fails
  on any difference.
- Wording fix: `modified` / `updated` are documented as moving on content-field changes only;
  `tier`, `quality_tier`, `corpus`, `content_license`, `source_freshness` reach `modified` via an
  `EXPORTER_VERSION` bump (DATA_DICTIONARY, TAXII and MISP READMEs).
- The served `docs/data/incidents.core.json` gains the `status` field (`CORE_FIELDS` in
  `scripts/gen_docs_core_data.py`), present on the 22 disputed rows it carries (retracted rows are
  not served): 6,687,566 → 6,688,006 bytes (+440 B), re-measured by building the payload with and
  without `status` from the same corpus.
- No row in `data/incidents.json` or `incidents.min.json` changed. Field-level delta:
  `docs/audits/ws6-v2130-export-integrity-2026-10-11.md`.

### Added - N9 precision audit: seeded stratified sample, review sheet, Wilson script, DATASHEET section and validate gate (agent-suggested; measurement pending)

- `scripts/precision_sample.py` draws a seeded (`20261011`), stratified sample.
  It takes 100 rows from the `feed` tier and 50 from the `landmark` tier. The
  strata are tier x source family, and allocation is proportional within each
  tier. Inside a stratum, the draw is systematic over (quality_tier, year, id).
  Retracted rows are excluded. The output goes to
  `docs/audits/precision/2026-10-11/`: the frame with population per stratum,
  the sample, and the review sheet. `--check` reproduces every generated file
  byte-for-byte; a different seed does not reproduce them. The frame is `tier`,
  not `quality_tier == "auto"`. The two overlap, and most of the CVE/GHSA rows
  behind board note N9 are `quality_tier: reviewed` (see the audit README).
- `review_sheet.csv` comes pre-filled with **agent-suggested** labels and
  reasons (`suggested_by: agent`). The `human_label`/`human_by` columns are
  empty. No row has been human-reviewed. The suggestions are not a
  measurement and are not quoted as one; `agent_suggested_precision.json`
  holds them, marked as such.
- `scripts/wilson_ci.py` computes Wilson 95% intervals per tier, per stratum
  and overall from **human labels only**. It uses a stratified estimator
  weighted to stratum populations, at Kish effective n, and reports both
  `unsure` treatments. Labels without a reviewer, or with a reviewer that names
  an agent or model, are refused. With only suggestions filled, it reports
  "no human labels". It is unit-tested against Newcombe (1998), Table I. It
  also gives per-`quality_tier` domain estimates within each tier, flagged
  when n < 30. The sheet loader tolerates a spreadsheet's byte-order mark,
  CRLF line endings and re-quoting.
- `docs/DATASHEET.md` has a new "Measured precision" section. The figure block
  is generated from `results.json` (`wilson_ci.py --render-datasheet`) and
  currently reads "measurement pending", with the method, sample size and date.
- `scripts/validate.py` has a new precision gate. In every status (pending,
  partial and measured) it checks that:
  - the audit directory is the pinned one, with no other dated directory
    beside it;
  - the sample's entries match their own declared hash and a hash pinned in
    code;
  - the whole `frame.json` (stratum populations, which are the estimator's
    weights) matches a second hash pinned in code;
  - the sheet ids match the sample;
  - `results.json` and the DATASHEET block equal a fresh computation.

  While the measurement is pending or partial, it also requires a D28-form
  marker (`pending_authorization.json`). The marker's decision id is a
  placeholder for the user. While it is unratified, the gate passes with a
  warning through dataset version 2.13.x and fails from 2.14.0.
- `scripts/evaluate_ai_relevance.py` scores `ai_relevance.assess()` against the
  human labels with a confusion matrix. It does not run until the sheet
  returns: today it prints "no human labels".
- `.gitattributes`: `docs/audits/precision/**` is kept LF, so the
  byte-for-byte check holds on every OS. No `data/*.json` change.
- **Ratified and corrected (2026-10-11).** User ruling D76 ratified the
  pending state and accepted that the "100 auto" frame is the feed tier:
  `pending_authorization.json` and `REQUIRED_PRECISION_PENDING_DECISION`
  both carry `D76`, so validate passes without the UNRATIFIED warning at any
  version, and a placeholder or other id now fails. Precision is still
  unmeasured. Under ruling D75, `INCLUSION.md` §5 (the feed is not
  `quality_tier: auto`; 69% of it is `reviewed`) and §4 (no CI gate
  sample-audits ingest changes) were corrected in place, with two
  `CORRECTIONS.md` rows. In the same commit, §6's "admitting at `auto` tier"
  became "admitting at `quality_tier: auto`" (a meaning-preserving wording
  edit, so no `CORRECTIONS.md` row).
- **Tamper test runs again (2026-10-12).** When `data/incidents.json` moved past
  the frame's pinned hash, two tests began to skip. The test that proves
  `--check` rejects a tampered sample copy now reads the pinned blob
  (`git show 6da13032:data/incidents.json`) and runs on every CI run, as the
  reproduction test already did. The default-data test no longer skips. While
  the working data matches the pin, it asserts reproduction. Once the data has
  moved, it asserts that `--check` refuses. A new test proves that refusal
  fires. The gate now also requires the marker's `decided` to be an ISO
  `YYYY-MM-DD` date on the ratified path, so a `<YYYY-MM-DD>` placeholder no
  longer passes. No `data/*.json` change.

### Changed - drift check now covers the README "Latest release" line, version metadata and the HF card template

- `scripts/check_stats_drift.py` additionally fails CI when the README
  `## Latest release` lead line names a version or release date different from
  `data/stats.json` / the top released CHANGELOG heading, when `pyproject.toml`,
  `.zenodo.json` or `CITATION.cff` (version, `date-released`) disagree with them,
  (version read from the `[project]` table; CITATION must carry both a
  top-level and a preferred-citation `version:`), when the `ingest/common.py`
  `USER_AGENT` version or `INCIDENTS.md`'s `**Version:**` line disagree, or
  when the Hugging Face card template in `scripts/export_huggingface.py`
  loses its `{count}`/`{version}` placeholders or gains a literal total
  (grouped or ungrouped, 4+ digits, bare years excepted) or any `X.Y.Z`
  version literal (third-party `VERIS X.Y.Z` excepted). CHANGELOG headings
  with em dash, en dash or hyphen are all read. `docs/VERSIONING.md` steps 2,
  4 and 5 updated to match (CHANGELOG heading promotion and README lead line
  now belong to step 2). Previously a stale release date beside a current `stats:version`
  marker passed. No data or published-doc content changed (the audit found
  nothing stale at 4edd6bad).

### Changed - MITRE ATLAS pin refreshed 2026.06 -> 2026.09; `taxonomy_versions` published (draft)

- **ATLAS pin: 2026.06 -> 2026.09** (`collection.version` of the upstream release;
  `mitre-atlas/atlas-data` `dist/ATLAS-latest.yaml` is a text pointer to
  `dist/v6/ATLAS-2026.09.yaml`). The verbatim release is committed under `ingest/atlas/`
  with a sha256 (Apache-2.0, notice in `NOTICE-DATA`); `mappings/mitre_atlas.json` is now
  derived from it by `scripts/atlas_pin.py`, never hand-edited. Release diff: 38
  techniques/subtechniques added, 3 retired (`AML.T0019`, `AML.T0058`, `AML.T0104`, folded
  into the new `AML.T0115` "Publish Poisoned AI Artifacts"), 4 renamed, 5 technique->tactic
  links changed, tactic `AML.TA0001` renamed "AI Attack Staging" -> "AI Attack Adaptation"
  (`docs/audits/atlas-refresh-2026.09-release-diff.md`). Upstream also published 2026.07
  and 2026.08 in between; the pin went straight from 2026.06 to 2026.09, so this diff
  covers 2026.06 to 2026.09 directly and does not attribute changes to the intermediate releases.
- **5,841 entries change `mitre_atlas` and/or `mitre_atlas_tactics`; no entry added,
  removed or re-IDed.** 2,532 have a superseded technique id mechanically translated
  (`AML.T0058` -> `AML.T0115.001` on 2,498 entries, `AML.T0019` -> `AML.T0115.000` on 41,
  `AML.T0015.001` -> `AML.T0015` on 1, an id that never existed in these releases; those
  per-id counts sum to 2,540 but 8 entries carry both `AML.T0019` and `AML.T0058`, so 2,532
  distinct entries; re-derive with the command in the delta audit's correction note); 3,309
  change tactics only, through the new technique->tactic links. On those entries `updated`
  (and `last_seen`) move to the build date and nothing else does. Mapping heuristics are
  unchanged. 2,532 + 3,309 = 5,841. Every changed entry, with before/after and reason, and the per-entity proof
  that the other 9,825 are byte-identical:
  `docs/audits/atlas-refresh-delta-2026-10-06.md`. **Consumer impact:** anything filtering
  on `AML.T0058`/`AML.T0019` must use the `AML.T0115.*` ids; the old ids stay in the pin
  marked `deprecated`, never deleted.
- **Two pre-existing pin errors corrected (also in `CORRECTIONS.md`).** (a) `INC-06842`
  (AVID-2023-V012, `quality_tier: reviewed`) carried `AML.T0015.001`, an id absent from
  ATLAS 2026.06 and 2026.09 alike; it is now `AML.T0015`. (b) The old
  `mappings/mitre_atlas.json` listed `AML.T0009`, `AML.T0030`, `AML.T0038` and `AML.T0045`
  as part of "2026.06", but ATLAS 2026.06 does not contain them (nor 2025.12 or 2026.01,
  checked against the upstream releases); they are now marked `deprecated` in the pin
  (retained, never deleted). No entry in the corpus carried them.
- **`taxonomy_versions`** (`atlas`, `owasp_llm`, `owasp_asi`, `capec`, `veris`), derived
  from the pinned `mappings/*.json` and published in `data/stats.json`, as
  `x_taxonomy_versions` on a STIX `identity` object, as `genai-incidents:taxonomy-*` tags
  on every MISP event and manifest entry, in the Hugging Face card, and as
  `genai_incidents.taxonomy_versions()` in the package. `capec` is `null`: the CWE->CAPEC
  map predates version recording.
- **New CI lint** `scripts/lint_atlas_ids.py` (in `make build` and `validate.yml`): fails on
  any `AML.*` id in the corpus or `mappings/` that is absent from, or deprecated in, the pin,
  and on a pin that does not match the committed snapshot. **New monthly workflow**
  `.github/workflows/atlas-refresh.yml` re-pulls ATLAS and opens a PR with the diff report
  and the per-entry delta.

### Changed - rejected-CVE sweep runs on every weekly refresh; DISPUTED CVEs are detected (agent-suggested, draft)

- **First full sweep (2026-10-09).** All 9,169 corpus CVE ids were checked against the CVE
  List (0 fetch failures): 37 REJECTED (the same 37 as 2026-10-03, all `Rejected` in NVD, no
  disagreement), 9,124 PUBLISHED, 8 not in the CVE List. This covers the 2,171 CVEs on the wave
  1-2 entries that had no recorded state (2,150 from cvelistV5, 21 AVID-only): none is
  rejected. **No entry was newly retracted**; the 29 retractions stand. Their
  `status_reason.as_of` moved from 2026-10-03 to 2026-10-09 (the re-check date), which is the
  only change to `data/incidents.json` (29 fields, no `updated` bump).
- **The weekly refresh budget rose from 600 to 1,200 CVE fetches per run**, so every corpus
  CVE is re-checked within ceil(9,169 / 1,200) = 8 weeks instead of 16. The sweep runs as its
  own job (own 60-minute limit) with a 40-minute wall-clock cap (`--max-seconds 2400`; 1,200
  requests measure about 21 minutes), because inside the refresh job, after a 26-51 minute OECD
  step, it could be cancelled with the job. The 8 weeks assumes up to 2.0 s per request
  (measured 1.07).
  The refresh PR body now lists every entry the build newly retracts (retracted in this build,
  not on `main`: entry, CVE ids, tier) and the PR is labelled `needs-ruling` when one is a
  landmark entry or more than 10 are retracted; the refresh is flagged, never blocked. The
  summary shows the sweep step's own outcome, so a failed sweep reads as failed.
  Never-checked ids, then records that predate dispute detection, then the stalest check, go
  first. Every run writes a dated log (`docs/audits/cve-sweep/<date>.md` and `.json`: ids
  checked, state changes, NVD disagreements, new REJECTED, new DISPUTED, failures, coverage)
  and exits non-zero if more than 10 percent of fetches fail.
- **DISPUTED detection.** Upstream, "disputed" is not a record state: it is a CNA or ADP
  `disputed` tag, or a `** DISPUTED **` description prefix. The sweep now records it on the
  PUBLISHED record (`disputed: true`, `dispute_signals`): 26 CVEs today, all CNA tags, on 22
  entries that rest only on those CVEs. The merge can mark such an entry `status: disputed`
  with `status_reason.code: cve-disputed` and lower its `confidence` one level (it stays in
  `incident_count`), and `validate.py` checks it, **but it does not apply this yet: it needs
  one new value in `schema/incident.schema.json` (`status_reason.code` enum), which the
  schema owner has to add.** Until then the 22 entries are unchanged in the data.

### Changed - 22 CVE-disputed entries marked; AIRI rows carry a review date (agent-suggested, draft)

- **`cve-disputed` is now a `status_reason.code`** (user ruling D61). This turns on the
  emission described in the entry above. **22 entries are now `status: disputed`**: all
  `tier: feed`, none landmark. Their `confidence` drops one level (17 high to medium, 5 medium
  to low). They **stay counted**: `incident_count` is still 15,637, `retracted_count` is
  still 29, and the ID set is the same 15,666. Each of the 22 changes `status`,
  `status_reason`, `confidence`, `updated` and `last_seen`, and nothing else. The schema now also
  enforces two pairings: `retracted` goes only with `cve-rejected`, and `disputed` goes only
  with `cve-disputed` and never with `confidence: high`. `status_reason.as_of` is described
  as the date of the last re-check (D62), for both codes.
- **AIRI Navigator review date: 2027-01-07** (user ruling D57, option A). The registry's lapsed
  D8 hold (until 2026-08-28) is replaced by a D57 hold until 2027-01-07. Its note records the
  D8 lapse. Every `stale` source in `data/source_freshness.json` must now carry a dated
  `hold`. The 1,382 marked rows gain `source_freshness.review_by: 2027-01-07`, which is derived
  from the registry. This adds no `updated` bump, because the marker is not a content field.
  There is no separate `review_by` field in the registry; see
  `docs/audits/ws3-v2130-review-by-design-2026-10-09.md`. Tagging the date in the STIX, MISP
  and HF exports is a separate change.
- Field-level delta: `docs/audits/cve-sweep/v2130-schema-delta-2026-10-09.md` and `.json`.
  It covers 1,404 entries and 1,492 fields, with 0 defects.

### Behaviour changes - `load_deprecations()` returns a different shape for three keys (user ruling D72)

- **If you read `load_deprecations()` directly, three values change shape** compared with
  v2.12.0. The return type is still `dict[str, str | list[str]]`, but code that branches on
  `isinstance(value, list)` takes a different branch for these keys:
  - `INC-00311`: a list of 12 IDs -> the string `"INC-14726"`.
  - `INC-01897`: a list of 8 IDs -> the string `"INC-14612"`.
  - `INC-00497`: the string `"INC-00311"` -> a list of the same 12 IDs (`INC-14660` ...
    `INC-14907`) it used to reach through `INC-00311`.

  Two more values change but keep their shape (string -> string, item 4): `INC-03128`
  `"INC-00754"` -> `"INC-14909"` and `INC-08185` `"INC-08139"` -> `"INC-14742"`. No other key
  of the mapping changes (293 keys in both, of which 7 lists now and 8 in v2.12.0).
  **Use `resolve_id_status()`** rather than indexing the mapping; it names the reason for
  every ID. Re-derive: run `load_deprecations()` from the v2.12.0 tag's package
  (`src/genai_incidents` plus that tag's `data/id_deprecations.json` and
  `data/incidents.min.json`) and from this tree's, and diff the two mappings.
  The `resolve_id()` and `resolve_id_group()` answers that change are listed in the two
  entries below.

### Changed - three split IDs narrowed to their identified incidents; "never reused" claim corrected (agent-suggested, draft)

- **`resolve_id("INC-00311")` now returns `INC-14726` and `resolve_id("INC-01897")` returns
  `INC-14612`** instead of `None` (user ruling D69). `resolve_id_group()` returns one ID for
  each instead of 12 and 8. Each is the only live entry carrying the title the published row
  had in every release, cross-checked on date, description and headline source.
  `INC-00554` gets release-scoped records: `resolve_id_status("INC-00554", release=...)` gives
  `INC-14756` (v2.0.0-v2.7.0), `INC-14742` (v2.8.0) or `INC-14609` (v2.9.0-v2.10.0).
  Its `resolve_id()` stays `None` and `resolve_id_group()` stays the 100 IDs.
  `INC-00754` stays a group. This updates the entry below: of its four split retirements,
  only `INC-00754` still reports `group`.
- **7 deprecation records appended**, none edited (the 1,077 existing records are a byte
  prefix of the new file). The records include an unscoped restatement for `INC-00497`, which
  used to reach its 12 successors through `INC-00311`. Without it, `INC-00497` would have
  moved to `INC-14726`, an incident it never named. No other `resolve_id()` or
  `resolve_id_group()` answer changed, over a sweep of 16,731 IDs against `main`'s own
  package. The raw `load_deprecations()` mapping changed for `INC-00311`, `INC-01897` and
  `INC-00497`. Input: `docs/audits/ID-group-ids-appends-2026-10-10.json`, a new dated file
  read by the build after the 2026-10-09 one. Step 8a's D28 check now expands approved
  targets through `content_into_map()`, so a `successor-identified` record is not read as
  where a split's content went. `data/incidents.json` and every other data file are
  byte-identical.
- **Corrected: incident IDs are not "never reused"** (user ruling D70). Across release tags
  v2.0.0-v2.12.0, 591 IDs carried more than one title, some of them a different incident
  (e.g. `INC-00004`). The claim was corrected in place in `docs/DATA_DICTIONARY.md` and
  `README.md`. `docs/ID_POLICY.md` §4 rule 1 gets a dated compliance note, and
  `CORRECTIONS.md` gets a row. An audit to classify the 591 is queued:
  `docs/audits/ID-reuse-audit-spec-2026-10-10.md`. See `docs/ID_POLICY.md` §8.6.

### Added - `resolve_id_status()`: no published ID answers with silence (agent-suggested, draft)

- **17 published IDs answered with silence, not the 8 the v2.11.0 notes named.** The other
  nine were published in v2.0.0, dropped in v2.1.0 and never recorded (`INC-00522`,
  `INC-00609`, `INC-00951`, `INC-00952`, `INC-00955`, `INC-00956`, `INC-00957`, `INC-01355`,
  `INC-01660`; `docs/ID_POLICY.md` §1.4(a)). Re-derive:
  `python scripts/audit/silent_ids.py silent --ref 816b9271`.
- **New `genai_incidents.resolve_id_status(id, release=None)`** (user ruling D49). It returns a
  typed `IdStatus` whose `status` is one of `live`, `successor`, `group`, `release-dependent`,
  `pre-tombstone`, `withdrawn` or `unknown`, and which carries the successor, the full
  successor set and, where it applies, a per-release map. `resolve_id()` keeps its signature
  `str | None`. This closes the "never to silence" deviation the v2.11.0 notes disclosed
  (`docs/ID_POLICY.md` §8).
- **17 deprecation records appended**, and no existing record changed (byte-prefix checked).
  `INC-03128` -> `INC-14909` and `INC-08185` -> `INC-14742` (`successor-identified`), so
  **`resolve_id()` now returns these two instead of `None`**, and `resolve_id_group()` returns
  one ID for them instead of 11 and 100. No other `resolve_id()` or `resolve_id_group()`
  answer changed for any of the 1,065 distinct `from` IDs in `data/id_deprecations.json` after
  this change (golden comparison against `main`'s own package), nor across the 16,731 IDs that
  were live in any release tag, are live now, or appear as a `from`. `INC-00497` and `INC-08139` gain
  `release-scoped` records carrying the new `valid_for_releases` field, which give their
  successor per cited release (for example, `INC-00497` cited from v2.1.0 -> `INC-14789`, cited
  from v2.5.0 -> `INC-14907`). Each is followed by an unscoped restatement, so "last record
  wins" readers get the same answer as before. The nine IDs get `into: null` records with
  reason `unrecorded-drop-v2.1.0`. The four split retirements (`INC-00311`, `INC-00554`,
  `INC-00754`, `INC-01897`) have no data change and report `group`.
- **`data/id_deprecations.json` now has a schema** (`schema/id_deprecations.schema.json`),
  which `validate.py` enforces together with the cross-record rules for release-scoped records.
  `data/incidents.json` and every other data file are byte-identical. Delta:
  `docs/audits/ID-silent-ids-delta-2026-10-09.json`.

## [2.12.0] — 2026-10-04

> **These notes were gated before the cut** and the release was cut on
> 2026-10-04. Full disclosure, the consumer-impact section on the changed
> meaning of `incident_count`, and the re-derivation recipe for every figure:
> [`docs/releases/v2.12.0.md`](docs/releases/v2.12.0.md). Minor release: the new
> schema fields are optional and additive.

### Added - wave 1-2 sources: +2,305 machine-ingested entries (D40, D43)

- **2,305 new entries, `INC-14911` to `INC-17215`** (contiguous append; none
  removed; no existing entry changed by the ingest). All are
  `quality_tier: auto`, `tier: feed`, `confidence` derived per entry (2,070 medium, 131 low, 104 high): 2,250
  `vulnerability-disclosure` and 55 `research`, all in the `security` corpus.
  `incident_count` (stands) 13,361 -> 15,637 together with the retraction
  below; the landmark count (1,915) is unchanged.
- **Sources:** AVID (`avidml/avid-db`, MIT; repo tarball, not the website),
  cvelistV5 (CVE Program, CVE-TOU; including the huntr CNA slice, as CVE
  records only), and arXiv cs.CR metadata via OAI-PMH (CC0; deterministic
  selection only, no human-approved list, D43; the abstract is discarded and
  the description is original prose). New ingests `scripts/ingest_avid.py`,
  `scripts/ingest_cvelistv5.py`, `scripts/ingest_arxiv_oaipmh.py` and shared
  filter `scripts/ai_relevance.py` write `ingest/wave12_*.json`.
- **Not new-source coverage:** 1,374 of the 2,250 new vulnerability entries
  are dated after 2026-06 and mostly fill the corpus's stalled NVD refresh;
  876 are dated 2026-06 or earlier (857 in 2024-01 to 2026-06, 19 earlier; the ingest window is by publication date). Existing entries are **not**
  enriched by these sources (498 + 2,139 CVE-already-in-corpus rows and 72
  would-fold rows are skipped, crosswalk kept in the provenance files).
- **410 emitted rows (352 cvelistV5, 58 AVID; 79 of them huntr) are suppressed
  at merge** because their CVE ids are on the issue-#88 out-of-scope key list
  (`data/issue88_remediation.json`); they never reach the corpus.
- **EUVD (ENISA) is not ingested**: licence unresolved, outreach drafted and
  not sent.
- Delta: `docs/audits/wave12-ingest-delta-2026-10-03.md`; integration delta
  `docs/audits/v2.12.0-integration-delta-2026-10-04.md` (0 unintended).

### Changed - licensing and ingest conduct

- `docs/SOURCE_LICENSES.md`: new rows 2.5, 6.1 (AVID), 6.2 (cvelistV5/huntr),
  6.3 (arXiv OAI-PMH), 6.4 (EUVD, not ingested). CVE Terms of Use and AVID MIT
  notices added to `NOTICE-DATA` and `.reuse/dep5`.
- **Row 2.4 (OSV.dev) corrected in place:** the claim that every OSV database
  reachable by the script is CC-BY 4.0 was false; OpenSSF `MAL-` records
  (Apache-2.0) are now excluded from the OSV path.
- `ingest/common.py`: redirect targets are now robots-checked and
  rate-limited (previously only the first host was); new `fetch_to_file` for
  large streamed downloads. The refresh workflows gain a rejection-snapshot
  step.

### Known limitations (v2.12.0)

- The OECD/AIID weekly refresh remains frozen (D25(a), kept by D42).
- The AIRI Navigator ingest has been dead since 2026-05-31 (board note N8).
- The CVE/GHSA feed precision audit is open (board note N9).

### Changed - 29 entries retracted because their CVEs are REJECTED (WS4-T2, board note N1)

- **29 entries now carry `status: retracted`** and 6 more carry a
  `rejected_cve_ids` flag. A full sweep of the 6,998 CVE ids in the corpus
  **before wave 1-2** against the CVE record found 37 REJECTED (all 37 also `Rejected` in NVD);
  the evaluation's 18 were the huntr slice of them. Nothing was deleted and
  every `INC-*` ID still resolves. The 2,150 cvelistV5-sourced CVEs on the new entries were PUBLISHED at ingest (that ingest drops every non-PUBLISHED record), and the 21 CVEs that reach new entries only through AVID have no recorded rejection state yet; the next refresh checks never-checked ids first.
- **`incident_count` now counts incidents that stand** (D44): measured alone
  against 13,361 entries it was 13,332 (-29); integrated with the wave 1-2
  ingest above it is **15,637**. Retracted entries stay in `incidents` (file
  length is 15,666) and are counted in the new `retracted_count` (29;
  `incident_count + retracted_count == len(incidents)`). `load_incidents()`
  and the slim JSON return the retracted rows too. They are omitted
  from the INCIDENTS.md tables and charts, the site, and the
  STIX/MISP/TAXII/Hugging Face feeds; their year-shard cards stay, bannered.
  **Consumers asserting `len(incidents) == incident_count` must change.**
- New optional fields `status`, `status_reason`, `rejected_cve_ids` (absence
  of `status` means the entry stands). New ingest
  `scripts/ingest_cve_rejections.py` -> `ingest/cve_rejections.json`; the
  merge applies the rule offline. 4 of the 29 were rejected as duplicates of
  another CVE; see the delta. STIX/MISP/TAXII no longer emit rejected CVEs as
  vulnerabilities (`x_rejected_cve_ids` added). Delta:
  `docs/audits/rejected-cve-reconcile-delta-2026-10-03.md`.

### Changed — STIX/TAXII OWASP LLM `source_name` relabel (live since 2026-10-01, after the v2.11.0 cut)

- **Every OWASP LLM `external_reference` in the STIX bundle
  (`data/incidents.stix.json`) and the TAXII collection `05bbe2e9…` now has
  `source_name: "owasp-llm-top10-2026"`; it was
  `"owasp-llm-top10-2025"`.** 17,750 references changed, equal to the sum of
  `len(owasp_llm)` over the corpus. Commit `7dc80602`, merged 2026-10-01
  after the v2.11.0 cut (board ruling D32), so it is **not** in the v2.11.0
  release notes; it is live on Pages now.
- **Why:** the `owasp_llm` codes have been the 2026 edition since v2.10.0
  (migration applied 2026-08-17), so the 2025 label was wrong. Under the
  2025 edition `LLM03` reads as *Supply Chain*; in this data it means
  *Excessive Agency*. The edition is now derived from the crosswalk
  (`mappings/owasp_llm_2025_to_2026.json`, `to_version`), so a future
  migration cannot leave the label stale.
- **Consumers keying on the old string must change.** Replace
  `owasp-llm-top10-2025` with `owasp-llm-top10-2026` in your queries, or
  match both strings during the transition.
- **Re-import the STIX bundle.** The relabel changed object content
  (**11,753 `x-genai-incident` objects** carrying the 17,750 references, as measured on the v2.11.0 corpus; the v2.12.0 bundle carries 21,017 on 14,004 objects)
  without changing `modified`; SDO `id` and `modified` are unchanged
  (`modified` derives from entry dates). Consumers that treat an unchanged
  (`id`, `modified`) as an already-seen object version, as STIX 2.1
  versioning permits, **may not** pick up the corrected label from a normal
  re-sync. Prefer **delete-then-import** of the affected objects, or import
  the bundle into a clean instance.
- **Did not change:** SDO `id` and `modified`, the object count (54,485),
  the MISP feed, PyPI, the Hugging Face dataset, and every **committed**
  `data/*.json` file (the corpus). Only the STIX bundle and the TAXII
  `objects.json` changed. `docs/data/SHA256SUMS` does not cover the STIX
  bundle.

## [2.11.0] — 2026-10-01

> **These notes were gated before the cut** (board ruling D30, 2026-09-20)
> and the release was cut on 2026-10-01. Version strings read `2.10.0`
> across the repo before the cut; the data and code below were already on
> `main` from 2026-09-18. Full disclosure, the
> consumer-impact section, and the re-derivation recipe for every figure:
> [`docs/releases/v2.11.0.md`](docs/releases/v2.11.0.md).

### Added
- **`tier` now ships in every distributed variant** of the corpus, not only
  the full `data/incidents.json`: `data/incidents.min.json` (and the site
  and PyPI copies of it), the Hugging Face export, the STIX bundle
  (as `x_tier`), and the MISP feed. Previously the README-cited landmark
  count could not be reproduced from any distributed artifact except the
  full file. A known gap remains, deliberately deferred: the site's CSV
  export still lacks a `tier` column.
- **A build-time authorization guard** aborts before writing whenever a
  previously-single published ID would newly resolve to more than one row,
  unless the write is authorized by a list carrying the D28 approval
  marker, closed against tamper-plus-recompute by pinning the expected
  hash in code. Covered by 13 dedicated tests in
  `tests/test_merge_and_dedupe.py` (9 exercising the authorization check
  directly, 4 covering the retirement/resplit-correction paths it gates).
  File presence alone authorizes nothing.

### Fixed — the 47-split remediation (D28, 2026-09-18)
- **Fixed a query-string URL over-merge in `normalize_url()`** that had been
  silently collapsing unrelated incidents together under a single shared
  published ID whenever their source URLs differed only by query string.
  Concretely: `INC-00311`'s military-targeting incident had absorbed an
  unrelated Greek tax-authority AI story, and `INC-00754`'s ChatGPT case had
  absorbed an unrelated Jason Momoa deepfake-scam story.
- **Executed the previously-deferred unmerge the fix enables**, authorized
  by the user as D28 after review of per-split evidence
  (`docs/audits/WS4-T19-authorized-splits-2026-09-18.json`, 55 entries):
  - **13,060 → 13,361 entries (+301)** — 306 new IDs, 5 removed from the
    live set.
  - **43 published IDs keep their identity** (`keep_id` splits).
  - **D28 authorized and executed 4 permanent retirements** —
    `INC-00311`, `INC-00554`, `INC-00754`, `INC-01897` — because the row
    that had been mechanically inheriting the old ID was not its real
    successor.
  - **A 5th ID, `INC-07738`, also stops resolving to itself in this
    release**, via a separate, ordinary `reason: "merged"` tombstone into
    `INC-14757` — pre-existing dedupe behaviour, not part of the D28
    authorization, named here because it is just as real a
    stop-resolving-to-itself event for a consumer citing that ID.
  - **8 existing inbound redirects corrected** so they resolve to the
    D28-authorized successor set (4 needed new `id_deprecations.json`
    records; 4 already chain-resolved correctly once the 4 retirements
    above were in place).
  - **Every retired ID still resolves** through
    [`data/id_deprecations.json`](data/id_deprecations.json)
    (1,051 → 1,060 records, **+9**, append-only under invariant 9). No citation of any ID that carries a tombstone breaks; the nine IDs
    that predate the tombstone machinery (`INC-00522`, `INC-00609`,
    `INC-00951`, `INC-00952`, `INC-00955`, `INC-00956`, `INC-00957`,
    `INC-01355`, `INC-01660`) are a known, documented exception recorded
    in `docs/ID_POLICY.md` section 1.4(a), unchanged by this release. **Two
    counts over that file now diverge for the first time**: 1,060
    records but only **1,056 distinct `from` IDs** — `INC-07771`,
    `INC-08109`, `INC-08133`, `INC-08146` each carry an original
    `merged` tombstone (2026-06-28) plus the `resplit` record (2026-09-18)
    that corrects it; neither is deleted, per invariant 9. Reason
    breakdown across all 1,060: `out-of-scope` 704, `merged` 289,
    `orphaned-ingest-source-retired` 59, `split` 4, `resplit` 4.
  - **`landmark_count` 1,905 → 1,915 (+10)**, entirely a consequence of the
    split, not a re-classification: **−2** retired landmark rows, **+12**
    new landmark rows among the 306 new IDs, **0** existing rows flipped
    tier in either direction.
  - **`generated` moves to 2026-09-18**; the weekly refresh is unblocked for
    the first time since 2026-07-27, when a since-fixed CI persistence bug
    and then the D25(a) freeze had kept it dead or blocked.
- Full field-level delta:
  [`docs/audits/WS4-T21-delivered-delta-2026-09-18.md`](docs/audits/WS4-T21-delivered-delta-2026-09-18.md).

### Consumer impact
Anyone holding v2.10.0 or earlier has a corpus where `INC-00311`,
`INC-00554`, `INC-00754`, and `INC-01897` point at content that is not
theirs, and where `INC-07738` (a separate, ordinary merge, not part of the
D28 remediation) has also stopped resolving to itself. Anyone joining on
incident IDs across versions must re-resolve through
`data/id_deprecations.json`.

**Twelve IDs whose `resolve_id()` answer changes in this release** (re-derived
by sweeping the v2.10.0 tag's own package against this tree). Under v2.10.0
all twelve resolved to a single ID, and **four of those answers were wrong**.
- **Four were wrong under v2.10.0 and are corrected in this release (D31;
  `resolve_id()` now follows a one-element successor list):** `INC-07771`
  (was `INC-01271`) -> `INC-14814`, `INC-08109` (was `INC-01412`) ->
  `INC-14847`, `INC-08133` (was `INC-07736`) -> `INC-14850`, `INC-08146`
  (was `INC-00554`) -> `INC-14853`. They never returned `None` in a published
  package. `INC-01271`, `INC-01412` and `INC-07736` are still live rows about
  unrelated incidents; `INC-00554` is one of the retirements. **If you cached
  `resolve_id()` output from v2.10.0 or earlier for these four, re-resolve.**
- **Eight return `None`, for three different reasons. In every case the
  content still exists; what `None` means differs:**
  - **Four retirements - ambiguity:** `INC-00311` (12 successors),
    `INC-00554` (100), `INC-00754` (11), `INC-01897` (8). The over-merged row
    was split into real groups; no single successor exists.
  - **Two with an identified successor this release does not write as a
    record - a known answer the package does not yet give:** `INC-03128` ->
    **`INC-14909`** (Momoa deepfake), `INC-08185` -> **`INC-14742`** (Wolf
    Robots), identified by source IDs and reference URLs. v2.11.0 does not
    resolve them to it (D28's authorized fan-out ships as authorized);
    narrowing the records is a follow-up.
  - **Two whose meaning changed between releases - depends on the release
    cited; resolve by the release you cited:** `INC-00497` was the Saint
    Paisios scam in v2.0.0-v2.1.0 (-> `INC-14789`) and the Greek tax AI story
    in v2.2.0-v2.8.0 (-> `INC-14907`); `INC-08139` was the South Korea robotic
    endoscope project in v2.2.0-v2.5.0 (-> `INC-14852`) and Wolf Robots in
    v2.6.0-v2.7.0 (-> `INC-14742`).
- Two ways to act: (1) read `data/id_deprecations.json` directly - `into`
  is the full successor array, last record per `from` wins; (2) upgrade and
  call the new `resolve_id_group()`, which does not exist in the v2.10.0
  package.
- These eight remain an **open, disclosed deviation** from
  `docs/ID_POLICY.md` section 3 ("never to silence"), owned by the
  ID-policy workstream; this release does not resolve it.

**`load_deprecations()` return type change (D34).** It returned
`dict[str, str]` through v2.10.0; its values are now `str | list[str]`. **8 of
its 293 values are lists** (the four corrected IDs and the four retirements);
v2.11.0 is the first release with any list value. **v2.10.0's own
`resolve_id()`, run on v2.11.0 data, raises `TypeError: unhashable type:
'list'`** for each of the twelve IDs above. Upgrade the package and the data
together. A stable always-list accessor is a follow-up.

## [2.10.0] — 2026-09-18

### Changed (breaking for consumers of `owasp_llm`)
- **Migrated every `owasp_llm` code from the OWASP Top 10 for LLM Applications
  2025 edition to the 2026 edition** (published 2026-08-03). The 2026 revision
  is a renumbering plus one rename — no entry added, none removed — so the
  mapping is a bijection over `LLM01`–`LLM10`. All **17,498** code assignments
  across **11,556** entries were rewritten. Full delta, verification and scope
  limits: [`docs/audits/owasp-llm-2026-migration-delta-2026-08-17.md`](docs/audits/owasp-llm-2026-migration-delta-2026-08-17.md).
- **This is a silent breaking change for anyone matching on code strings.** The
  code space is identical before and after, so `LLM03` remains valid but now
  means *Excessive Agency* instead of *Supply Chain*. Data published up to and
  including **v2.9.0** (and its Zenodo DOIs) carries 2025 codes. Notable moves:
  Excessive Agency `LLM06`→`LLM03`, Supply Chain `LLM03`→`LLM04`, Improper
  Output Handling `LLM05`→`LLM10`, Unbounded Consumption `LLM10`→`LLM06`,
  Misinformation `LLM09`→`LLM07`.
- **`LLM07` System Prompt Leakage → `LLM08` Hidden Context Exposure**, renamed
  and widened by OWASP to all non-user-facing context assembled into the model's
  context window, not just the system prompt.
- Codes were **renumbered, not re-classified**. Entries that would newly qualify
  under a 2026 entry's widened scope were not added; that is annotation work
  (WS2) and is not claimed as done.

### Added
- `mappings/owasp_llm_top10_2026.json` — the 2026 catalog, sourced from the
  official text at
  <https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final>.
- `mappings/owasp_llm_2025_to_2026.json` — machine-readable crosswalk with
  per-entry rank moves and scope changes; the single source of truth for the
  migration.
- `scripts/migrate_owasp_llm_2026.py` — the deterministic migration, with a
  full field-level delta report and two independent double-apply guards (a
  permutation applied twice is silently wrong and passes schema validation).
- `mappings/owasp_llm_top10_2025.json` is retained and marked superseded:
  releases at or before v2.9.0 cannot be read correctly without it.

### Fixed
- **Sanitized one description.** `INC-11516` (`CVE-2023-36464`) quoted a GitHub
  attachment link from its upstream CVE text; that link was an S3 pre-signed URL
  whose `X-Amz-Credential` parameter is an AWS access key **ID** (a public
  identifier, not a secret), bound to a signature that expired five minutes after
  2023-06-27. `scripts/strip_presigned_urls.py` removes `X-Amz-*` parameters from
  URLs in the ingest snapshot, preserving the object path, any other query
  parameter, and prose mentions of `X-Amz-*` HTTP header names elsewhere. One
  entry, three fields (`description`, `updated`, `last_seen`); no row added or
  removed. Secret scanners match the `AKIA` pattern regardless of whether a
  secret is present, which blocked this release from being pushed.
- Retain-on-drop rows (entries carried verbatim out of the previous
  `data/incidents.json` after every source drops them) are a build **input**, not
  just an output. An inputs-only migration missed 9 of them — visible only as a
  distribution shift, since the totals still matched. Recorded in the audit above
  so future taxonomy migrations include that third input.

## [2.9.0] — 2026-07-31

Licensing and provenance release (Phase 1, "Honest"). Draft release notes
with the full field-level delta, a consumer-impact section listing every
tombstoned ID, and the re-derivation recipe for every figure below:
[`docs/releases/v2.9.0.md`](docs/releases/v2.9.0.md). **Cut 2026-07-31** as `v2.9.0`; the maintainer sent the final outreach
thread the same day, closing WS0-T4's outreach obligation at 4 of 4. Composition since the last cut release
(`v2.8.0`, 12,986 entries): **12,986 → 13,060 (+74 net** — 135 added by
routine refresh, 61 removed: 59 tombstoned by the orphaned-ingest-file
retirement below, `into: null`; 2 by ordinary cross-entity merge, `into:` a
surviving ID. Never silently deleted — `data/id_deprecations.json`).

### Added (licensing — row-level marking and attribution)
- **`content_license` row-level marker**, CC BY-SA 4.0, now carried by all
  **1,517** AIAAIC-derived rows (100% of AIAAIC-sourced rows in the
  corpus), mirrored into the STIX export as `x_content_license`
  (`docs/audits/WS0-E13-database-right-2026-07-18.md`, D11).
- **Per-entry OECD AIM attribution reference**, landed on **all 3,829 of
  3,829** OECD-AIM-sourced rows (plus 368 further rows that absorbed OECD
  content into a merged AIID entry) — `OECD (<year>), AI Incidents and
  Hazards Monitor, <page-url> (accessed on <first-ingest date>)`
  (`scripts/merge_and_dedupe.py::_apply_oecd_attribution`,
  `docs/audits/E21-5.3-oecd-attribution-2026-07-30.md`). Lands at
  `references[0]` — and so becomes the "Cite this incident" line — on
  3,667 of those rows; the one exception (`INC-00437`) correctly renders
  its AIID citation instead per existing render precedence.
- **`source_freshness` row-level marker** on **1,380** rows derived from a
  source whose feed went stale on 2026-05-31 (`status`, `as_of`,
  `sources`), plus a published, reconciled-against-a-named-copy
  `data/source_freshness.json` registry that `validate.py` holds to its
  own claim (D8).

### Changed (licensing — E21 outcome (B))
- **OECD AI Incidents and Hazards Monitor (AIM) `description` field
  reduced from LLM-synthesized narrative to an originally-templated,
  structural-facts-only sentence** (`scripts/ingest_oecd_aim.py::normalize_body()`
  / `build_description()`). AIM's `summary`/`title` fields are LLM-generated
  (OpenAI o3-mini) from third-party news article text of uncertain,
  unresolved copyright status (docs/audits/E21-oecd-narrative-licence-2026-07-30.md
  §2.4/§3) — `summary`/`evidences` continue to feed taxonomy/severity/corpus
  classification as ephemeral, never-persisted signals, exactly as
  `ingest_aiid_snapshot.py` already does for AIID's excluded `reports.text`.
  Applied retroactively to all 4,160 already-committed rows in
  `ingest/oecd_aim_full_incidents.json` via a one-off local transform
  (`scripts/migrate_oecd_description_reduction.py`, no network/model calls,
  no re-fetch) — 3,667 shipped rows' `description` changed as a result. The
  other 162 OECD-AIM-sourced rows ship a different upstream source's
  `description`, having lost the entity-merge — disclosed, not a miss.
  **`title` is explicitly out of scope for this reduction and still ships
  the same LLM-generated text verbatim on 3,667 of the 3,829 rows** — same
  posture as AIAAIC's retained-headline question below, not resolved here.
- **AIAAIC-derived rows carry facts and a source pointer, not narrative
  prose** — system/technology/sector/jurisdiction/affected plus a link to
  the specific AIAAIC entry, disposing of the copyright share-alike
  question over AIAAIC's cell text (D2). The retained AIAAIC headline is a
  separate, still-open question (E15/D17), same posture as OECD `title`
  above.
- **AIID ingestion moved to AIID's own official weekly snapshot channel**,
  replacing the retired high-volume scraper
  (`scripts/ingest_aiid_snapshot.py`, D1,
  `docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md`). AIID's
  license-excluded `reports.text` is never opened.
- **AIID content-licensing question resolved: no row-level marker is
  required for the population that ships (0 of 1,466 AIID-identified
  rows carry one) — a decision, not a gap.** AIID's US-situated maker
  categorically excludes the only AIID text this dataset ships (`title`)
  from copyright, and fails both the UK and EEA database-right
  qualification tests (`docs/audits/E23-aiid-marking-ruling-2026-07-30.md`).
  A separate, **dormant, non-shipping** population (hand-curated AIID rows
  plus AIRI Navigator's own AIID-derived rows) is **not** cleared by this
  ruling and is kept out only by current merge order — now enforced by a
  regression test, `tests/test_e23_aiid_dead_letter_tripwire.py`, rather
  than relying on that order holding by convention.
- **`corpus` (security/ai-harm) now persisted at OECD ingest time** from a
  derived signal only (never the narrative text itself), closing a
  merge-time reclassification coupling that would otherwise have silently
  moved 77–150 rows `ai-harm`→`security` once the narrative was removed —
  the same defect class WS0-T3 already fixed once for AIAAIC (2026-07-18).
  Verified: 0 unintended `corpus` moves from the reduction itself.

### Removed (dead ingest source)
- **`ingest/oecd_aim_incidents.json` retired** — an 86-row hand-curated OECD
  file with no producing script and no code reference anywhere in the repo,
  orphaned since `edaefc92` (2026-05-13) yet still silently shipping rows
  into every build via `merge_and_dedupe.py`'s generic `ingest/*.json` glob.
  59 of its 86 rows were the corpus's *only* source for that incident and
  are now tombstoned (`data/id_deprecations.json`, `into: null`); the
  remaining 27 were already cross-covered by AIID/OECD-AIM and simply lost
  the orphan file's contributed `source_ids`/`tags`/framework mappings on
  rebuild (disclosed, justified — not part of the narrative reduction
  itself). One row's classification changed as a direct, verified
  consequence (`INC-08170`: `security` → `ai-harm`, a correction, not a
  regression — `docs/audits/E21-reduction-delta-2026-07-30.md` §6).

### Conduct
- **All HTTP(S) ingest fetches route through a single module**
  (`ingest/common.py`): identifying User-Agent, fail-closed robots.txt
  check, per-host rate limiting, with one enumerated, evidenced host
  exception (`ROBOTS_UNVERIFIABLE_ALLOWLIST`). Non-HTTP egress (`gh api
  graphql`, vendor CLIs) is registered with its conduct properties, not
  exempted from disclosure (`docs/INGESTION_CONDUCT.md`).

## [2.8.0] — 2026-07-13

Data-quality release. Net composition 12,770 → 12,986 (+241 from the weekly
source refresh, −25 from removing non-GenAI scope contamination); landmark
1,858 → 1,865.

### Removed (scope precision)
- **25 non-GenAI CVE-bridge buckets excluded** per INCLUSION.md — entries where
  a weak key (shared reference URL / templated title) had collapsed dozens to
  hundreds of *unrelated, non-GenAI* CVE advisories into one incident:
  `dexidp/dex` (708 CVEs, was landmark), Juju (93, was landmark), ~11 ×
  Magento/Adobe Commerce, KaiOS, Google Chrome, four Jenkins plugins, Liferay,
  Mattermost, MantisBT, jackson-dataformat-toml, Firefox. Decisions and
  per-bucket rationale in `data/issue88_remediation.json`; each removal carries
  an `out-of-scope` deprecation so citations still resolve. The excluded
  buckets' source keys are suppressed **before** dedupe (enumerated statically),
  so the removal is idempotent and cannot resurrect on rebuild. (#88, #95)

### Added (labels)
- **55 landmark-tier `reversibility_class` / `discovery_method` labels**
  populated across two evidence-gated curation batches, each label citing
  closing-action or discovery-channel evidence in `data/curation_overrides.json`.
  (#91, #92)

### Changed
- **Weekly source refresh** — AIRI Navigator, AIAAIC, OECD AI Incidents Monitor
  (+241 incidents net; routine dedupe deprecations recorded). (#93)

### Tooling
- **`scripts/audit_cve_bridge.py`** — reproducible precision audit of the
  grandfathered disjoint-CVE weak-key merges (#36), classifying each multi-CVE
  incident. It surfaced the scope-contamination removed above and characterises
  the remaining GenAI over-merges (a ~542-advisory recovery) as the v3.0 one-way
  split re-baseline tracked in #88. (#94)

## [2.7.0] — 2026-07-03

Data-quality and interoperability release. Incident composition is unchanged
from v2.6.0 (12,770 entries, 0 added / 0 removed) — the work is in
classification precision, threat-intel mapping freshness, and the first
populated landmark-tier label.

### Changed (interoperability)
- **MITRE ATLAS mapping refreshed to content v2026.06** (`mappings/mitre_atlas.json`;
  ATLAS froze the old `dist/ATLAS.yaml` at 5.6.0, so `scripts/ingest_external.py`
  now parses the pinned `dist/v6/ATLAS-2026.06.yaml`). Adds techniques
  `AML.T0113`, `AML.T0114`, `AML.T0091.001`; no renames or removals for existing
  IDs. (#86)

### Changed (classification precision)
- **844 `attack_vector: other` entries reclassified from unanimous CWE evidence**
  (`other` 4,589 → 3,745). A new `mappings/cwe_attack_vector.json` maps 35
  unambiguous CWE classes to 10 vectors, applied only when text classification
  left an entry at `other` **and** every mappable CWE on it agrees (unanimity
  rule — mixed signals stay `other`). A 50-entry random sample reviewed 50/50
  defensible. (#89)

### Added (first labels)
- **First `reversibility_class` label populated** — INC-03152 (the Replit
  agent production-database deletion) classified `external-reversible`, with
  closing-action evidence in the curation override. The boundary rubric
  (realized-outcome, "who had to act?") is now documented in `TAXONOMIES.md`.
  First community-contributed label (proposal #74). (#85)

### Fixed
- **Dedupe no longer over-merges distinct-CVE incidents** on a full CVE-feed
  refresh — weak keys (shared reference URL, templated title) can no longer
  bridge two entries with disjoint CVE sets, including transitive claims
  (the shape that collapsed six distinct MLflow CVEs into one). Historical
  merges are grandfathered so committed data is byte-stable. (#87, #36)

### Docs
- Datasheet/methods-paper truth-pass: incident count corrected, the two v2.6.0
  landmark labels and the VERIS crosswalk documented, TAXII/MISP distribution
  and `veris:*` machinetags surfaced; Hugging Face `size_categories` now
  derived from the record count. (#84)

## [2.6.0] — 2026-07-02

### Added (Schema — landmark-tier labels)
- **`reversibility_class`** — optional enum (`read-only` / `reversible` /
  `external-reversible` / `irreversible`) classifying the reversibility of the
  action that closed the incident. Landmark-tier only, evidence-gated via
  `data/curation_overrides.json`, enforced by a new validate.py integrity
  invariant. Community proposal #74 (lineage: OWASP AISVS C09-02). (#76)
- **`discovery_method`** — optional enum (`security-researcher`,
  `actor-disclosure`, `customer-report`, `media-report`, `law-enforcement`,
  `internal-monitoring`, `internal-report`, `vendor-monitoring`, `other`)
  recording how the incident was first surfaced; same landmark gate (the
  validate.py invariant now covers both label fields). Lineage: VERIS 1.4.1
  `discovery_method`, flattened and AI-adapted. (#81)

### Added (Integrations)
- **VERIS 1.4.1 crosswalk** — hand-curated `mappings/veris.json` (35
  attack_vectors → 48 enum entries, mechanically verified and adversarially
  reviewed against official VERIS definitions), emitted as `veris:*`
  machinetags in the MISP feed alongside `genai-incidents:*` /
  `mitre-atlas:*`. Opens the dataset to VERIS consumers (DBIR contributor
  pipeline, cyber insurers, FAIR-style risk quantification) with zero schema
  surface. (#79)

### Data
- 11,658 → **12,770 incidents**: weekly auto-refresh (#75), OpenClaw
  ingest-coverage fix (#77 — `openclaw` added to the NVD keyword list,
  AI-context tokens, npm ecosystem allowlist and strict malware gate after
  CVE-2026-44112 was missed on wording alone), and a CVE-enrichment run
  (#78: +788 incidents including 276 previously-invisible OpenClaw
  advisories and CVE-2026-44112 itself as INC-14014; +936 CVEs; all 42
  removals recorded as merge deprecations).

### Notes
- Both new fields are additive and optional — absence means **unassessed**,
  never a claim. No existing records were modified for the schema change.
- Hardcoded marketing lower bound updated "11,500+" → "12,500+" (canonical
  count remains `data/stats.json`).

## [2.5.0] — 2026-06-11

### Added (Coverage — linkage graph, #30)
- **`capec_ids`** on every CWE-bearing entry — MITRE CAPEC attack patterns
  derived from `cwe_ids` via an authoritative CWE→CAPEC map
  (`mappings/cwe_capec.json`, built by `scripts/build_cwe_capec.py` from MITRE's
  CAPEC corpus). The complete, uncapped union; ~4,433 entries.
- **`purl`** on every entry with a structured `affected` identifier — Package-URLs
  (`pkg:type/namespace/name`) for entity resolution of affected packages
  (`pip/foo`→`pkg:pypi/foo`, `maven/g:a`→`pkg:maven/g/a`, scoped npm `%40`-encoded);
  ~3,620 entries.

### Added (Adoption — integrations, #33)
- **Static TAXII 2.1 endpoint** at `docs/taxii2/` (discovery, API root,
  collections, objects + manifest envelopes) — a read-only mirror of the STIX
  collection, generated at Pages deploy. `make taxii`.
- **MISP feed** at `docs/misp/` (manifest + one Event per year + `hashes.csv`)
  with `genai-incidents:*` / `mitre-atlas:technique` attribute tags. Subscribe a
  MISP instance to the feed URL. `make misp`.

### Notes
- Schema gains `capec_ids` + `purl` (additive). Both fields are derived in the
  provenance pass, kept out of the content snapshot, and added to the full
  `data/incidents.json` only (the slim site payload is unchanged). Incident
  composition is identical to v2.4.0 (0 added / 0 removed).

## [2.4.0] — 2026-06-11

### Added (Trust foundation)
- **[INCLUSION.md](INCLUSION.md)** — explicit scope policy: every entry must
  satisfy AI-nexus + security/safety-relevance + evidence gates.
- **Provenance fields** on every entry: `confidence` (transparent
  high/medium/low rule), `source_count`, `source_status` (active/retained),
  `first_seen`/`last_seen`.
- **Corrections process** — `data_correction` / `scope_dispute` issue
  templates and a public [CORRECTIONS.md](CORRECTIONS.md) log.

### Changed (enforced quality)
- CI now enforces two cross-entry invariants on every build: every entry has
  a resolvable primary source, and no out-of-scope malicious-package entry
  may survive (the v2.3.1 scope-purge is now a hard gate).

## [2.3.1] — 2026-06-10

### Fixed
- **Data precision:** the v2.3.0 GHSA MALWARE pass matched generic npm
  malware on weak substrings (`ai` in `chai-mocks`, `prompt` in
  `sudo-prompt`, `nemo` in `nemo-reporter`) and a loose description-token
  fallback — ~71% of the 465 malicious-package entries were not AI-related.
  MALWARE advisories now require a **strong, segment-boundary** match
  against a curated AI package allowlist (no weak substrings, no
  description fallback); the noise entries are dropped.

### Security / docs
- Documented that `title`/`description`/`affected`/`impact`/`mitigations`
  are **untrusted verbatim free text** (may contain raw HTML/exploit
  payloads); consumers must escape before rendering (schema + DATASHEET).
- Light/dark theme now also applies to the year-shard and 404 pages.

## [2.3.0] — 2026-06-10

### Added

- **9,209 → 12,062 incidents.** Deeper GitHub Security Advisory ingest
  (paged back to the 2022 floor) plus a new **MALWARE-classification
  pass** that surfaced **465 malicious-package** advisories (AI-ecosystem
  typosquats / trojaned deps), and ~31 new NVD keywords + OSV packages
  for high-CVE-count AI products (Langflow, LiteLLM, LangGraph, NeMo,
  DeepSpeed, vLLM, llama.cpp, …).
- **CISA KEV enrichment**: `exploited_in_wild` + `kev_date_added` flag
  incidents whose CVEs are in the Known Exploited Vulnerabilities catalog
  (deterministic, from a committed snapshot refreshed by the workflows).
- New `exploited_in_wild` / `kev_date_added` schema fields. README now
  carries a live incident-count badge fed by `data/stats.json`.

### Security

- **Fixed a stored XSS** on the generated incident pages: advisory
  descriptions containing raw HTML (e.g. `<img src=x onerror=...>`)
  executed when rendered as Markdown. All incident free-text is now
  HTML-escaped and link schemes are restricted to http(s)/mailto; a CI
  guard fails the build if raw HTML reaches a shard.

### Changed

- **Site rebuilt to scale**: custom Jekyll build (the managed builder
  stopped finishing at 12k pages) and the per-incident standalone pages
  were retired in favour of self-anchored year shards + client-side
  detail. Added a **light/dark theme** toggle.
- CI hardened: cross-entry integrity invariants (no CVE/source held by
  two live entries; deprecations resolve) and UTC-stable date stamps.

## [2.2.0] — 2026-06-10

### Added

- **CVE enrichment**: `cwe_ids` populated on 2,411 and `cvss_vector` on
  2,094 of the 2,493 CVE-bearing incidents (previously 0). New
  manually-dispatched `CVE enrichment` workflow re-pulls NVD + GHSA +
  OSV on CI (supports the `NVD_API_KEY` secret).
- **+1,361 incidents** from the first working GHSA ingest — a Windows
  encoding bug (`text=True` decoding `gh api` output as cp1252) had
  silently yielded 0 advisories; now UTF-8. Plus the weekly refresh
  (+427) and 9 hand-curated crosswalk-watch CVEs. Total: 7,725 → 9,209.

### Fixed

- **Core dedupe tombstone bug**: stale index pointers could merge new
  content into already-absorbed (tombstoned) entries, silently dropping
  it. Dedupe now resolves every hit to the live absorber and reindexes
  until stable; recovered 24 previously-lost incidents (+39 CVEs,
  +210 source_ids). See
  `docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md`.
- **UTC date stamps**: `added`/`updated`/`generated` now derive from
  the UTC calendar (`utc_today()`), so local builds behind UTC can't
  drift against CI.
- Removed CNA-rejected `CVE-2026-35020`; removed the phantom MITRE
  ATLAS technique `AML.T0039`.

### CI

- Validate workflow runs a Python 3.12/3.13 matrix with least-privilege
  permissions; publish/PR actions pinned to release commit SHAs
  (`gh-action-pypi-publish` v1.14.0, `create-pull-request` v8.1.1);
  weekly refresh reports per-source ingest outcomes and aborts if all
  sources fail.

## [2.1.0] — 2026-06-03

### Added

- Hugging Face dataset publishing (`emmanuelgjr/genai-incidents`) with
  enriched dataset card; STIX 2.1 export; retain-on-drop (incidents are
  never silently lost when a source drops them); red-team benchmark
  catalogue; MITRE ATLAS tactic backfill; CWE/CVSS-vector capture in the
  CVE ingester; GitHub Pages site redesign ("amber threat console").

## [2.0.0] — 2026-05-16

### Breaking

- `INC-*` IDs are now **stable across rebuilds**. Previously they were
  reassigned on every merge based on year+title order; citing
  `INC-00139` was unsafe because tomorrow's `INC-00139` could refer to
  a different incident. New rule: once assigned, an ID never moves. If
  an entry is merged away, the old ID is recorded in
  `data/id_deprecations.json` pointing at the surviving entry.
- Schema field `version` in `data/incidents.json` bumped to `2.0.0`.

### Added

- New schema fields: `quality_tier` (`curated` / `reviewed` / `auto`),
  `corpus` (`security` / `ai-harm`), `cwe_ids`, `cvss_vector`,
  `aiid_id`, `disclosure_date`.
- `CITATION.cff` for academic citation; `.zenodo.json` for DOI minting
  on GitHub releases.
- New ingest sources: AIAAIC public spreadsheet (~1,500 net-new entries
  after dedupe), OECD AI Incidents Monitor full corpus (~2,900 net-new
  after dedupe + security filter), MIT FutureTech AI Risk Navigator
  (~400 net-new + authoritative AIID dates for 1,020 existing entries).
- `make ingest-all`, `make test` targets.
- `tests/` with 33 unit tests covering dedup, classifiers, renderer.
- `docs/incidents/<year>.md` shards so the top-level `INCIDENTS.md`
  stays under GitHub's render budget.

### Fixed

- **Dedupe correctness** — three independent bugs caused the same
  incident to live as multiple `INC-*` records: (a) the dedup indices
  weren't refreshed after a merge, so absorbed CVEs missed the target
  on subsequent passes; (b) when an absorbed key already mapped to a
  different entry, the two should have transitively merged but didn't;
  (c) `AIID-N-OECD` (from the legacy bridge file) and `AIID-N` (from
  the fresh AIID scrape and OECD AIM) referenced the same incident but
  never matched. All three fixed; **0 duplicate CVEs, source IDs, or
  reference URLs** across 7,714 entries.
- **AIID year-fallback bug** — pages without machine-readable dates
  were getting the *maximum* year mentioned in title/description, so
  references to "the 2027 election" produced incidents dated 2027.
  Now: minimum plausible year, capped at the current year. 1,020
  AIID entries got authoritative dates via the AIRI bridge.
- **Deterministic builds** — `updated`/`generated` no longer stamped
  with `today` on every run; CI drift checks now stable.
- **Severity normalisation** — NVD's literal string `"None"` no longer
  fails schema validation.
- **CVE title cleanup** — generic NVD descriptions like _"A flaw has
  been found in MLflow…"_ and _"Gradio is an open-source Python
  package…"_ are rewritten to _"\<Product\> — \<Vector\> (CVE-…)"_.

### Changed

- `INCIDENTS.md` restructured: single unified table, newest-first.
  Per-incident detail blocks moved to year shards.
- README documents the full toolchain, sources, and reproducibility
  contract.

## [1.0.0] — 2026-05-13

Initial public release. ~3,200 incidents covering 2015–2026, mapped
across OWASP LLM Top 10 (2025), OWASP Agentic Top 10, NIST AI RMF, and
MITRE ATLAS.
