# genai_incidents: A Cross-Framework Dataset of GenAI and Agentic-AI Security Incidents

**Author:** Emmanuel Guilherme Junior
**Version of this draft:** tracks the dataset release noted in [`CITATION.cff`](../../CITATION.cff)
**Canonical DOI (concept):** [10.5281/zenodo.20248675](https://doi.org/10.5281/zenodo.20248675)
**Repository:** <https://github.com/emmanuelgjr/genai_incidents>

> Working methodology paper / datasheet-plus. Intended as the citable
> description of how the dataset is built, mapped, and governed. Numbers
> (incident counts, distributions) are stated as "as of release vX.Y.Z" and
> should be read against the live [`data/stats.json`](../../data/stats.json).

## Abstract

`genai_incidents` is an open, continuously-maintained dataset of publicly
disclosed security incidents and vulnerabilities involving generative-AI and
agentic-AI systems. Each entry is consolidated from multiple upstream sources,
deduplicated under stable identifiers, and **cross-mapped to six taxonomies**
— four core, stored on every applicable record (OWASP LLM Top 10 (2026),
OWASP Agentic (ASI) Top 10, NIST AI RMF, MITRE ATLAS); a companion mapping
stored where the source provides it (MAESTRO); and an experimental,
export-only crosswalk computed at MISP-export time rather than stored per
record (VERIS 1.4.1). The dataset is built
by a deterministic, reproducible pipeline; governed by an explicit written
inclusion policy; and published in interoperable formats (JSON, minified JSON,
STIX 2.1, a Python package, and a Hugging Face dataset) under open licences with
a DOI per version. This paper documents construction, the mapping methodology,
quality and governance controls, limitations, and reproducibility.

## 1. Motivation

AI-security knowledge is fragmented across news reports, academic papers, vendor
advisories, and vulnerability databases, with no shared taxonomy linking an
incident to the control frameworks it implicates. Practitioners doing red-team
planning, threat modelling, GRC mapping, or trend research must re-aggregate the
same scattered evidence repeatedly. `genai_incidents` exists to be a
consolidated, framework-mapped index — and, explicitly, to be *trustworthy*:
correctable, provenance-tracked, and scoped by a written policy rather than by
keyword luck.

## 2. Scope and inclusion policy

Scope is defined by a versioned, public policy ([`INCLUSION.md`](../../INCLUSION.md)).
An entry must satisfy three gates: **(i) AI-nexus** — the incident materially
involves a generative/agentic AI system or its supporting ML infrastructure;
**(ii) security/safety relevance** — a vulnerability, exploit, misuse, or
real-world harm; and **(iii) evidence** — at least one resolvable primary
source. Records failing any gate are excluded regardless of keyword matches.
Two tiers are surfaced explicitly: a curated/notable **landmark** set and the
comprehensive **feed** of vulnerabilities/advisories; headline claims cite the
landmark count rather than the raw total.

## 3. Sources

The dataset aggregates (non-exhaustive): the AI Incident Database (AIID), AIAAIC,
the OECD AI Incidents Monitor, the MIT AI Risk Repository / FutureTech Navigator,
MITRE ATLAS case studies, AVID, OWASP resources, the NVD, GitHub Security
Advisories (GHSA), and OSV.dev, plus academic venues (arXiv/USENIX/CCS/NDSS),
vendor threat reports, and red-team/safety benchmark catalogues
(JailbreakBench, HarmBench, AgentHarm, AgentDojo, garak, promptfoo, …). Each
source has a dedicated, restartable ingester under `scripts/`.

## 4. Construction pipeline

The build is a deterministic, idempotent pipeline
(`parse_existing.py → merge_and_dedupe.py → render_markdown.py → validate.py`):

1. **Normalise** every source record into the unified schema
   ([`schema/incident.schema.json`](../../schema/incident.schema.json)).
2. **Deduplicate** with first-hit-wins keys (CVE id › source id › normalised
   reference URL › fuzzy title within ±1 year), resolving every match to the
   *live* absorbing record to avoid silent content loss on transitive merges.
3. **Assign stable `INC-#####` ids**; merged-away ids are recorded in
   `id_deprecations.json`, so citations of any ID that carries a tombstone
   resolve. This is scoped: the 9 IDs in `docs/ID_POLICY.md` §1.4(a) are
   unrecorded (no tombstone), and 8 IDs return `None` from `resolve_id()` (see
   the v2.11.0 release notes).
4. **Finalise content fields** (attack vector, framework mappings, curation
   overrides) *before* history stamping, so the content snapshot is stable.
5. **Enrich**: CWE/CVSS from NVD/GHSA; CISA KEV exploited-in-the-wild flags;
   then derived provenance (`confidence`, `source_count`, `source_status`,
   `tier`).
6. **Retain-on-drop**: incidents are never silently lost when a source stops
   emitting them; they are carried forward and marked `source_status: retained`.
7. **Stamp** UTC dates, gated by a content snapshot so unchanged entries don't
   churn; render Markdown/site/STIX; **validate** against schema and invariants.

**Determinism.** The build must reproduce byte-identically across UTC days; CI
fails on any drift. This is what makes the dataset reproducible and auditable.

## 5. Cross-framework mapping

Mappings are produced by a combination of source-provided labels and
heuristics seeded from the finalised attack vector, then cascaded
(OWASP → ATLAS/NIST) via an authoritative technique→tactic map
(`mappings/mitre_atlas.json`, ATLAS v2026.06). Mapping decisions are content
fields under the determinism contract and are disputable via the corrections
process. We make no claim that heuristic mappings are expert-reviewed for every
entry; the `quality_tier` and `confidence` fields expose how vetted each record
is. A further export-only crosswalk maps the controlled `attack_vector`
vocabulary to VERIS 1.4.1 enum paths (`mappings/veris.json`), emitted as
`veris:*` machinetags in the MISP feed — closest-defensible-enum curation,
deliberately not derived by chaining ATLAS→ATT&CK→VERIS (see
[`TAXONOMIES.md`](../TAXONOMIES.md)).

## 6. Schema and provenance

Every entry carries identity (`id`, `source_ids`), classification (severity,
category, `corpus`), the taxonomy mappings described in section 5, optional CVE/CWE/CVSS and KEV
fields, and a **provenance block**: `quality_tier`, rule-derived `confidence`
(high/medium/low), `source_count`, `source_status`, `first_seen`/`last_seen`,
and `tier` (landmark vs feed). Landmark-tier entries may additionally carry two
optional, evidence-gated labels — `reversibility_class` (reversibility of the
incident's closing action) and `discovery_method` (how the incident was first
surfaced; VERIS 1.4.1 lineage) — assigned only through
`data/curation_overrides.json` with closing-action evidence in the override
note and enforced by a landmark-tier integrity invariant; absence means
unassessed. Free-text fields (`description`, etc.) are
aggregated **verbatim and are untrusted** — they can contain raw HTML/exploit
payloads — and must be escaped before rendering; the project's own renderer does
so, and a CI guard enforces it.

## 7. Quality and governance

- **Cross-entry invariants enforced in CI**: no CVE/source id is held by two
  live entries (the dedupe-integrity guarantee); every entry has a resolvable
  primary source (evidence gate); no out-of-scope malicious-package entry may
  survive (scope gate); deprecations resolve; generated outputs do not drift.
- **Precision discipline**: any ingest change that *adds* entries is
  relevance-sampled before merge — not merely count-checked. (A 2026-06 episode
  in which a substring filter admitted ~800 generic-malware records, and the
  retain-on-drop mechanism then preserved them, is the documented origin of both
  the scope policy and the automated scope gate.)
- **Corrections**: a public process (issue templates + [`CORRECTIONS.md`](../../CORRECTIONS.md))
  and a versioned scope policy make the dataset correctable.

## 8. Limitations and biases

English-language and Western-media skew; heuristic (unreviewed) labels in the
`auto` tier; recency lag for CVSS; scope drift in broad societal-harm sources;
and the inherent incompleteness of any incident corpus (absence of evidence is
not evidence of absence). See [`docs/DATASHEET.md`](../DATASHEET.md) for the full
treatment.

## 9. Availability and reproducibility

Open data (CC-BY-4.0) and code (MIT). Distributed via GitHub, PyPI
(`genai-incidents`), Hugging Face Datasets, a STIX 2.1 bundle, a static
TAXII-compatible discovery document, a MISP feed, a browsable site, and a
per-version DOI on Zenodo. The entire dataset is regenerable from the
committed ingest artifacts with `make build`; CI re-runs this on every change
and fails on drift, so any published release is reproducible from source.

## 10. Ethics

The dataset catalogues *disclosed* incidents and *public* advisories; it
contains no non-public exploit code authored by this project. Free-text payloads
embedded in upstream advisories are preserved for fidelity but flagged as
untrusted. The intended use is defensive: research, threat modelling, GRC, and
education.

## How to cite

See [`CITATION.cff`](../../CITATION.cff). Cite the concept DOI
[10.5281/zenodo.20248675](https://doi.org/10.5281/zenodo.20248675) for the
project, or a version DOI for a specific release.
