# Changelog

All notable changes to the dataset and tooling are recorded here.
The dataset uses [SemVer](https://semver.org/) — major bumps for breaking
schema or ID changes, minor bumps for additive schema fields or large
ingest expansions, patch bumps for routine refreshes and bug fixes.

## [Unreleased]

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
