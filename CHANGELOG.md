# Changelog

All notable changes to the dataset and tooling are recorded here.
The dataset uses [SemVer](https://semver.org/) — major bumps for breaking
schema or ID changes, minor bumps for additive schema fields or large
ingest expansions, patch bumps for routine refreshes and bug fixes.

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
