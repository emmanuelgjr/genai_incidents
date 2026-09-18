# Datasheet — GenAI & Agentic AI Security Incidents

Following *Datasheets for Datasets* (Gebru et al.). For per-field definitions see
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md); for the formal schema see
[`schema/incident.schema.json`](../schema/incident.schema.json).

## Motivation
A consolidated, machine-readable index of GenAI and agentic-AI security
incidents, normalized and mapped to four core taxonomies (OWASP LLM Top 10,
OWASP Agentic Top 10 (ASI), NIST AI RMF, MITRE ATLAS), plus a companion
MAESTRO architectural-layer mapping and an experimental VERIS 1.4.1
crosswalk — so developers, AppSec/threat-intel teams, and researchers can
query, pivot, and cite incidents instead of re-scraping scattered trackers.
See TAXONOMIES.md for the full picture, including which taxonomies are
core, companion, or experimental. This dataset draws on other incident
trackers (AIID, MIT AI Risk Repository, AVID, and others; see the
Collection section below) as upstream sources rather than replacing them.

## Composition
- **Instances:** consolidated incidents (<!-- stats:incident_count -->13,361<!-- /stats:incident_count -->
  as of this build — authoritative live count in
  [`data/stats.json`](../data/stats.json)), each an alleged
  real-world harm, disclosed vulnerability, threat report, or research/red-team
  demonstration involving an AI system.
- **Split:** `corpus` = `security` vs `ai-harm`; `category` distinguishes
  real-world from research/red-team/regulatory entries.
- **Labels:** severity, attack_vector, and OWASP/NIST/ATLAS mappings — assigned
  by deterministic heuristics and, for a growing subset, human/assisted review
  (see `quality_tier`). Landmark-tier entries may additionally carry the
  evidence-gated `reversibility_class` and `discovery_method` labels, assigned
  only through curation overrides with closing-action evidence; absence means
  unassessed (see [`TAXONOMIES.md`](TAXONOMIES.md)).
- **Provenance:** every entry records its upstream `source_ids`.

## Collection
Aggregated from public, credible sources: AI Incident Database (AIID), AIAAIC,
OECD AI Incidents Monitor, MIT AI Risk Repository, MITRE ATLAS, AVID, NVD +
GitHub Security Advisories + OSV.dev (AI/ML packages), CISA KEV, OWASP, vendor threat
reports, and peer-reviewed venues (arXiv/USENIX/CCS/NDSS). Ingestion scripts
live in [`scripts/`](../scripts); each source is re-pulled, normalized, then
deduplicated by CVE / canonical URL / fuzzy title.

## Preprocessing & quality
- **Dedup:** union of taxonomy/refs, highest severity, most specific date;
  merged ids tombstoned in `id_deprecations.json`.
- **Classification:** `attack_vector` and framework mappings are filled by
  precision-first heuristics; `quality_tier` records vetting level.
- **Curation overrides:** explicit human/assisted decisions are recorded in
  [`data/curation_overrides.json`](../data/curation_overrides.json) and survive rebuilds.
- **Reproducibility:** the full build is deterministic and idempotent across
  calendar days (CI re-derives all outputs and fails on any drift).

## Uses
- AppSec triage and dependency/CVE lookup; threat-intel (STIX 2.1 export,
  ATLAS tactic/technique pivots); research on AI-incident trends and taxonomy.
- **Not** a complete census of all AI incidents, and not legal advice.

## Limitations & biases

---
**Warning — heuristic labels are not measured prevalence.** Most taxonomy and
severity labels in this dataset are assigned by deterministic heuristics, not
human review (`auto`-tier: unreviewed — see `quality_tier`). A mapping count
such as "N incidents tagged OWASP LLM01" reflects what the heuristics matched
across whichever sources happened to be aggregated. It is a labeling
artifact, not a measured rate of how often that failure mode occurs in the
real world. See `quality_tier` for which entries carry human/assisted
review, and the Heuristic labels bullet below for known gaps.

---

- **Source & language bias:** English-language, Western-media-skewed; under-counts
  unreported or non-English incidents.
- **Heuristic labels:** `auto`-tier mappings are unreviewed; `attack_vector`
  `other` (~36%) reflects genuinely uncategorized harm incidents.
- **Recency lag:** very recent CVEs may lack CVSS until NVD scores them.
- **Scope drift:** broad sources (AIAAIC/OECD) include pre-LLM algorithmic harms.
- **Untrusted free text (security):** `title`, `description`, `affected`,
  `impact` and `mitigations` are aggregated **verbatim** from upstream
  advisories and can contain raw HTML or exploit payloads (e.g.
  `<img src=x onerror=...>`) lifted from the original write-ups. The data is
  kept faithful on purpose — **consumers MUST HTML-escape/sanitize these
  fields before rendering them as HTML or Markdown.** The project's own web
  renderer escapes them; the data formats (JSON / STIX / HF) preserve the raw
  text.

## Distribution & licence
- **Data:** CC-BY-4.0. **Code:** MIT. DOI [10.5281/zenodo.20248675](https://doi.org/10.5281/zenodo.20248675).
- **AIAAIC-derived rows carry an additional obligation.** Every row whose
  `content_license` field names the AIAAIC Repository (CC BY-SA 4.0,
  share-alike) carries that field as a row-level attribution/share-alike
  obligation marker — this does not apply to the dataset as a whole. A
  separate, open question about whether an EU/UK *sui generis* database
  right also applies to this extraction is pending AIAAIC's reply to
  outreach (sent 2026-07-27) or a qualified-counsel resolution; the
  current worst-case exposure is bounded to those same rows, never
  dataset-wide. Full framing, and the current audited count of
  AIAAIC-citing rows: `NOTICE-DATA` and
  [`docs/SOURCE_LICENSES.md`](SOURCE_LICENSES.md) §1.1.
- **OECD-derived rows carry a narrower, separate obligation.** `description`
  on OECD AI Incidents and Hazards Monitor (AIM)-sourced rows is reduced to
  structural facts and a source link only — never AIM's LLM-generated
  `summary`/`evidences`, machine output derived from copyrighted
  third-party news. A small number of rows instead ship another source's
  description, where that source won the merge; every OECD AIM-sourced row
  carries a per-entry citation (`OECD (year), AI Incidents and Hazards
  Monitor, url (accessed on date)`) regardless of which description it
  ships. The `title` field is not covered by the reduction and remains an
  open question, tracked at the same posture as the AIAAIC headline
  question above. Exact per-row counts and the merge-precedence
  exceptions: `title`'s in `NOTICE-DATA`; `description`'s in
  [`docs/SOURCE_LICENSES.md`](SOURCE_LICENSES.md)'s OECD AIM
  summary-of-outcomes row (§1.5 covers the full licensing analysis).
- Distributed via GitHub, PyPI (`genai-incidents`), Hugging Face Datasets, a
  STIX 2.1 bundle, a static [TAXII-compatible discovery document](https://emmanuelgjr.github.io/genai_incidents/taxii2/discovery.json),
  and a [MISP feed](https://emmanuelgjr.github.io/genai_incidents/misp/) whose events
  carry `genai-incidents:*`, `mitre-atlas:*`, and VERIS 1.4.1 `veris:*` machinetags.

## Maintenance
Maintained at <https://github.com/emmanuelgjr/genai_incidents>; a weekly workflow
refreshes external sources via PR. Versioned with SemVer; see [`CHANGELOG.md`](../CHANGELOG.md).
Corrections welcome via issues/PRs and the curation-overrides file.
