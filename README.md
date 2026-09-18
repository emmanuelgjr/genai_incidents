# GenAI & Agentic AI Security Incidents

[![Incidents](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Femmanuelgjr%2Fgenai_incidents%2Fmain%2Fdata%2Fstats.json&query=%24.incident_count&label=incidents&color=9a3412&logo=databricks&logoColor=white)](https://emmanuelgjr.github.io/genai_incidents/)
[![Validate dataset](https://github.com/emmanuelgjr/genai_incidents/actions/workflows/validate.yml/badge.svg)](https://github.com/emmanuelgjr/genai_incidents/actions/workflows/validate.yml)
[![PyPI version](https://img.shields.io/pypi/v/genai-incidents?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/genai-incidents/)
[![Python versions](https://img.shields.io/pypi/pyversions/genai-incidents?logo=python&logoColor=white)](https://pypi.org/project/genai-incidents/)
[![Hugging Face dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dataset-yellow)](https://huggingface.co/datasets/emmanuelgjr/genai-incidents)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20248675.svg)](https://doi.org/10.5281/zenodo.20248675)
[![License: MIT (code)](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![License: CC-BY-4.0 (data)](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](LICENSE-DATA)

**genai_incidents** is a consolidated, machine-readable index of publicly disclosed security incidents, vulnerabilities, and red-team findings involving generative-AI and agentic-AI systems, normalized onto OWASP LLM/ASI Top 10, NIST AI RMF, and MITRE ATLAS so you can query and pivot across sources that don't share a schema. It's built for AppSec/threat-intel teams doing CVE and vendor-advisory triage, red-teamers scoping attack classes, and researchers tracking incident trends — pull it as a Python package, a Hugging Face dataset, raw JSON, or a STIX/TAXII/MISP feed. It is **not** a complete census of every AI incident, and most taxonomy/severity labels are heuristic-assigned rather than human-reviewed — see [Limitations & biases](docs/DATASHEET.md#limitations--biases) before citing a mapping count as a measured real-world rate.

- 🔎 **Searchable site:** <https://emmanuelgjr.github.io/genai_incidents/>
- 📦 **Python:** `pip install genai-incidents`
- 🤗 **Hugging Face:** [`emmanuelgjr/genai-incidents`](https://huggingface.co/datasets/emmanuelgjr/genai-incidents) — `load_dataset("emmanuelgjr/genai-incidents")`
- 🛰️ **STIX 2.1 bundle** (for OpenCTI / MISP / TAXII): <https://emmanuelgjr.github.io/genai_incidents/data/incidents.stix.json> — incidents as `x-genai-incident` SDOs linked to MITRE ATLAS `attack-pattern`s and CVE `vulnerability`s
- 📡 **TAXII 2.1 (static):** discovery at <https://emmanuelgjr.github.io/genai_incidents/taxii2/discovery.json> — a read-only static mirror of the STIX collection ([usage + caveats](https://emmanuelgjr.github.io/genai_incidents/taxii2/README.md))
- 🛡️ **MISP feed:** subscribe a MISP instance to <https://emmanuelgjr.github.io/genai_incidents/misp/> (Format: *MISP Feed*) — incidents grouped into year-events with `genai-incidents:*` / `mitre-atlas:*` / VERIS 1.4.1 `veris:*` tags
- 🪪 **DOI:** [`10.5281/zenodo.20248675`](https://doi.org/10.5281/zenodo.20248675) (Zenodo concept DOI — always the latest release; see [How to cite](#how-to-cite))

---

## What's in the data

<!-- stats:incident_count -->13,361<!-- /stats:incident_count --> entries as of the <!-- stats:generated -->2026-09-18<!-- /stats:generated --> build, <!-- stats:landmark_count -->1,915<!-- /stats:landmark_count --> of them `tier: landmark` — the curated, headline-worthy subset (see `docs/DATA_DICTIONARY.md`'s `tier` field for the exact definition); cite the landmark count, not the full corpus, when you mean "notable incidents." Coverage spans <!-- stats:year_min -->1983<!-- /stats:year_min -->–<!-- stats:year_max -->2026<!-- /stats:year_max -->. Full field reference: [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

Beyond the obvious title/description/severity fields, a few worth knowing about before you build on this data:

- **`content_license`** — a row-level marker on entries whose upstream source imposes its own attribution/share-alike obligation on that specific row, carried through the full JSON, the Hugging Face export, and the STIX bundle (as `x_content_license`). Its absence means no *known* obligation, not a guarantee the row is unencumbered.
- **`source_status` / `source_freshness`** — whether a row is still *emitted* by a build and whether the upstream source that fed it is still *refreshing* are tracked as two separate, independent facts. A committed ingest snapshot keeps re-emitting its rows every build even after the source that produced them goes dark, so a row being present is never itself a freshness claim — `source_freshness` is the field that actually says so, and it's published at [`data/source_freshness.json`](data/source_freshness.json).
- **`quality_tier` / `confidence`** — vetting level (`curated` / `reviewed` / `auto`) and a rule-derived confidence tier, so you can filter to only human/assisted-reviewed entries instead of the full heuristic-labeled corpus.
- **Tombstones, never deletions** — merged or withdrawn IDs are never dropped; they redirect (or terminate) via [`data/id_deprecations.json`](data/id_deprecations.json), so a citation of any ID this project has ever published resolves to something, never to silence. See [`docs/ID_POLICY.md`](docs/ID_POLICY.md) for the ID-stability commitment.

**Heuristic labels, stated plainly:** most taxonomy and severity labels are assigned by deterministic heuristics, not human review. A count like "N incidents tagged LLM01" is a labeling artifact of what the heuristics matched across whichever sources happened to be aggregated — it is not a measured rate of how often that failure mode occurs in the real world. This is the datasheet's own warning, not a paraphrase of it: see [Limitations & biases](docs/DATASHEET.md#limitations--biases) for the full statement and known gaps.

### Taxonomies mapped

- **OWASP Top 10 for LLM Applications (2026)** — `LLM01`–`LLM10` — _core_
- **OWASP Agentic Top 10 (ASI)** — `ASI01`–`ASI10` — _core_
- **NIST AI Risk Management Framework (AI 100-1)** — `GOVERN` / `MAP` / `MEASURE` / `MANAGE` subcategories — _core_
- **MITRE ATLAS** — tactics (`AML.TA00xx`) and techniques (`AML.T00xx`) — _core_
- **MAESTRO** architectural layers (`L1`–`L7`) — _companion_ (carried on entries whose upstream source already provides a MAESTRO mapping; not populated on every entry)
- **VERIS 1.4.1 crosswalk** (`veris:*` tags in the MISP export) — _experimental_ (a hand-curated crosswalk from `attack_vector`, emitted at export time only — not a stored per-incident schema field)

That's six taxonomies total, not four — see [`docs/TAXONOMIES.md`](docs/TAXONOMIES.md) for a chooser table and the full code lists.

**How this differs from AIID / MIT AI Risk Repository / AVID:** those projects are themselves primary or aggregated incident trackers, and this dataset draws on several of them as upstream sources (see [`docs/SOURCE_LICENSES.md`](docs/SOURCE_LICENSES.md)) rather than replacing them. What this project adds is normalization onto security-oriented taxonomies (OWASP LLM/ASI, NIST AI RMF, MITRE ATLAS) across sources that don't share a common schema. A full side-by-side positioning comparison is planned but not yet written.

## Documentation & policies

| | |
|---|---|
| Provenance, composition, limitations (Datasheets for Datasets) | [`docs/DATASHEET.md`](docs/DATASHEET.md) |
| Per-source license/ToS audit — every upstream, its terms, this project's remediation | [`docs/SOURCE_LICENSES.md`](docs/SOURCE_LICENSES.md) |
| How the CC-BY-4.0 data grant applies, and where it doesn't | [`NOTICE-DATA`](NOTICE-DATA) |
| Incident ID stability policy (tombstones, redirects always honored; ID-width decision still pending) | [`docs/ID_POLICY.md`](docs/ID_POLICY.md) |
| Ingestion conduct — rate limits, robots.txt, identification | [`docs/INGESTION_CONDUCT.md`](docs/INGESTION_CONDUCT.md) |
| Field reference | [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) |
| Taxonomy detail and chooser table | [`docs/TAXONOMIES.md`](docs/TAXONOMIES.md) |
| Scope contract — what's in/out, and why | [`INCLUSION.md`](INCLUSION.md) |
| Methodology paper | [`docs/paper/genai-incidents-methods.md`](docs/paper/genai-incidents-methods.md) |
| **Public evidence trail** — dated audits, delta reports, and rulings behind licensing/data/conduct decisions | [`docs/audits/`](docs/audits/) |
| Corrections & scope disputes — open a [data correction](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=data_correction.yml) or [scope dispute](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=scope_dispute.yml); accepted changes logged in | [`CORRECTIONS.md`](CORRECTIONS.md) |
| Changelog | [`CHANGELOG.md`](CHANGELOG.md) |

`docs/audits/` is unusual for a dataset repo, and deliberately so: rather than folding a licensing ruling or a data-migration rationale into a doc that then has to be kept perpetually current, each is a dated, standalone record of what was true and why a decision was made — worth a look if you want the reasoning behind a change, not just its result.

## Latest release

**<!-- stats:version -->2.10.0<!-- /stats:version --> — released 2026-09-18.** A **silent breaking change for anyone matching on `owasp_llm` code strings**: every code was migrated from the OWASP Top 10 for LLM Applications 2025 edition to the 2026 edition. The code space is identical before and after, so `LLM03` is still valid and now means *Excessive Agency* instead of *Supply Chain* — nothing errors, nothing fails validation. Concretely: a filter on `LLM03` matched roughly eight times as many rows at v2.9.0 as it matches today — the release notes give both exact counts and the command to re-derive them. Data at or before v2.9.0, including its Zenodo deposits, carries 2025 codes; the crosswalk is [`mappings/owasp_llm_2025_to_2026.json`](mappings/owasp_llm_2025_to_2026.json). Also fixes eight weeks of silently-dead weekly refreshes, an 800 KB page truncation that dropped ~38 incidents per run, and the OECD crawl budget. **Exactly one corpus row changed** — `INC-11516`'s description had the query string of an expired pre-signed URL removed; the entry count is unchanged, no row was added or removed, and OECD refresh merges remain frozen pending a URL over-merge fix. Full release notes — the consumer-impact section and the re-derivation recipe for every figure — are at [`docs/releases/v2.10.0.md`](docs/releases/v2.10.0.md); [`CHANGELOG.md`](CHANGELOG.md) carries the same entry.

---

## Layout

```
.
├── data/
│   ├── incidents.json          ← the full, authoritative dataset (use this)
│   ├── incidents.min.json      ← slim variant: id, title, taxonomy mappings, primary reference
│   ├── stats.json              ← the single source of every published count (invariant 6)
│   ├── id_deprecations.json    ← merged/withdrawn ID redirects and tombstones
│   ├── source_freshness.json   ← reviewed registry of which sources have stopped refreshing
│   └── legacy_consolidated.json ← intermediate output from the legacy parser
├── schema/
│   └── incident.schema.json    ← JSON Schema for one incident
├── mappings/
│   ├── owasp_llm_top10_2025.json
│   ├── owasp_asi_top10.json
│   ├── nist_ai_rmf.json
│   ├── mitre_atlas.json
│   ├── cwe_capec.json
│   ├── veris.json
│   └── maestro_layers.json
├── legacy/                     ← original source files (preserved verbatim)
├── ingest/                     ← per-source aggregator outputs (CVE, AIID, ATLAS, etc.)
├── scripts/
│   ├── parse_existing.py             ← parse legacy/ → data/legacy_consolidated.json
│   ├── ingest_external.py            ← parse cloned source repos under ../_external/ → ingest/*.json
│   ├── ingest_aiid_snapshot.py       ← AIID official weekly snapshot (sanctioned bulk channel) → ingest/aiid_full.json
│   ├── scrape_aiid.py                ← RETIRED per-page scrape (kept only as a reused parsing-logic library; disabled in Makefile)
│   ├── ingest_airi_navigator.py      ← MIT FutureTech AI Risk Navigator CSV → ingest/airi_navigator_incidents.json
│   ├── ingest_aiaaic_sheet.py        ← AIAAIC Repository public Google Sheet → ingest/aiaaic_sheet_incidents.json
│   ├── ingest_oecd_aim.py            ← OECD AI Incidents Monitor (large page crawl) → ingest/oecd_aim_full_incidents.json
│   ├── ingest_cve_nvd_expanded.py    ← pull AI-relevant CVEs from NVD/GHSA/OSV → ingest/cve_nvd_expanded.json
│   ├── ingest_cisa_kev.py            ← CISA Known Exploited Vulnerabilities catalog (enrichment only)
│   ├── merge_and_dedupe.py           ← merge legacy + ingest/* → data/incidents.json
│   ├── render_markdown.py            ← data/incidents.json → INCIDENTS.md + data/stats.json
│   ├── render_docs_stats.py          ← templates data/stats.json's counts into README/DATASHEET/site/CITATION.cff (invariant 6)
│   ├── check_stats_drift.py          ← CI gate: fails on any doc surface out of sync with data/stats.json, or a hardcoded total
│   ├── export_stix.py / export_taxii.py / export_misp.py / export_huggingface.py  ← format exporters
│   └── validate.py                   ← validate JSON against schema
├── INCIDENTS.md                ← rendered index: unified table, newest-first
├── docs/incidents/<year>.md    ← per-year detail shards linked from INCIDENTS.md
├── docs/audits/                ← dated project decision records (licensing, data, conduct) — see Documentation & policies below
├── tests/                      ← pytest suite for merge/render/export/ingest-conduct helpers
├── LICENSE                     ← MIT (covers code in scripts/, schema/, src/)
├── LICENSE-DATA                ← CC-BY-4.0 (covers the dataset under data/) — see Licensing below for exceptions
└── README.md
```

---

## What counts as an incident?

Every entry must satisfy three gates, defined precisely in [`INCLUSION.md`](INCLUSION.md) — the authoritative scope contract this project's own ingesters and reviewers decide against, not a keyword list. In gist (not a substitute for the real thing): a real **AI-nexus** (the AI/ML system is the target, the vector, or a material enabler of harm — not an incidental mention), **security or safety relevance** (a vulnerability, exploit, attack, misuse, or real-world harm, not a feature or benchmark), and **at least one citable primary source**. Broad fairness/bias-only harms with no security primitive are out of scope; see `INCLUSION.md` for the full definition and worked examples.

---

## Schema (summary)

See [`schema/incident.schema.json`](schema/incident.schema.json) for the canonical version, and [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) for the complete field-by-field reference (identity/provenance, quality/freshness, licensing, and evidence fields are not shown below to keep this summary short).

```jsonc
{
  "id": "INC-00001",                 // stable, never-reused ID — see docs/ID_POLICY.md for the padding-width policy
  "source_ids": ["AIID-123", "CVE-2025-..."],
  "cve_ids": ["CVE-2025-..."],
  "cwe_ids": ["CWE-918"],
  "cvss_score": 9.8,
  "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "aiid_id": 1234,                   // canonical AIID numeric ID when applicable
  "title": "...",
  "date": "2025-09",
  "disclosure_date": "2025-10-02",   // separate from incident date when known
  "year": 2025,
  "category": "real-world | research | red-team | vulnerability-disclosure | threat-report | policy",
  "description": "...",
  "attack_vector": "prompt-injection | rce | supply-chain | data-exfiltration | ...",
  "affected": "vendor/product",
  "impact": "...",
  "severity": "Critical | High | Medium | Low | Info",
  "owasp_llm": ["LLM01", "LLM06"],
  "owasp_asi": ["ASI01", "ASI02"],
  "nist_ai_rmf": ["MEASURE-2.7", "MAP-3.5"],
  "mitre_atlas": ["AML.T0051", "AML.T0051.001"],
  "mitre_atlas_tactics": ["AML.TA0004"],
  "maestro_layers": [{"layer":"L3","label":"Agent Frameworks & Tooling","role":"origin"}],
  "mitigations": ["..."],
  "references": [
    {"title":"Vendor advisory","url":"https://...","type":"vendor"}
  ],
  "tags": ["mcp","supply-chain"],
  "added": "2026-05-16",             // stable across re-runs
  "updated": "2026-05-16",           // only bumped when content actually changes
  "quality_tier": "curated | reviewed | auto",   // vetting level — see docs/DATA_DICTIONARY.md
  "content_license": null            // present only when this row owes an upstream attribution/share-alike obligation
}
```

---

## Using the dataset

Every distribution channel below ships from the same corpus, but not necessarily the same **build** of it — know which one you're getting before you rely on freshness.

### As a Python library

```bash
pip install genai-incidents
```

```python
from genai_incidents import query, by_cve, resolve_id

for inc in query(severity="Critical", attack_vector="prompt-injection", year=2026):
    print(inc["id"], "-", inc["title"])

print(by_cve("CVE-2026-21520"))   # all incidents that list this CVE
print(resolve_id("INC-00139"))    # follow merge history to the current canonical INC
```

**Staleness:** the PyPI package bundles a snapshot of the slim dataset (`incidents.min.json` + `id_deprecations.json`) taken at that release's build time and publishes on a tagged GitHub release (or a maintainer-triggered manual run) — `pip install` gives you the corpus as of the version you installed, not a live feed. The package's own release version and the dataset's content-vintage are not yet decoupled (that split — `data_version` distinct from code `__version__`, with a `fetch_latest()` to pull current data on demand — is planned but not shipped); today they're the same string. If you need current data, don't assume a `pip install` a week ago is still current — re-pull, or use one of the channels below.

### As a Hugging Face dataset

```python
from datasets import load_dataset
ds = load_dataset("emmanuelgjr/genai-incidents")
```

**Staleness:** published by `make huggingface` on each GitHub release (or manually via `workflow_dispatch`) — refreshed on releases, not continuously. Same vintage characteristics as the PyPI package.

### As the STIX 2.1 / TAXII / MISP feeds

<https://emmanuelgjr.github.io/genai_incidents/data/incidents.stix.json>, the [TAXII-compatible discovery document](https://emmanuelgjr.github.io/genai_incidents/taxii2/discovery.json), and the [MISP feed](https://emmanuelgjr.github.io/genai_incidents/misp/) are all rebuilt automatically by the Pages deploy workflow on every push to `main` that touches the corpus or an exporter script — the closest thing to "live" this project offers, though it is a rebuild-on-push, not a continuous feed. Build any of them locally with `make stix` / `make taxii` / `make misp`.

### As raw JSON

- Full: [`data/incidents.json`](data/incidents.json) — the authoritative, always-current copy; the site and the STIX/TAXII/MISP exports all build from this file.
- Slim: [`data/incidents.min.json`](data/incidents.min.json) — id/title/taxonomy mappings/primary reference only.
- Schema: [`schema/incident.schema.json`](schema/incident.schema.json)
- ID deprecations: [`data/id_deprecations.json`](data/id_deprecations.json) — for resolving citations of merged-away IDs

If you need the current corpus rather than a point-in-time snapshot, pull from `data/incidents.json` on `main` (or the site/STIX/TAXII/MISP exports, which build from it), not from PyPI or Hugging Face.

### As a website

Filterable, searchable, deep-linkable table at
<https://emmanuelgjr.github.io/genai_incidents/>.

## Regenerating the dataset

```bash
pip install -r requirements.txt
make build      # parse legacy, merge + dedupe, render, template doc stats (invariant 6), validate
make test       # pytest tests/
make ingest-all # (heavy: refresh AIID/AIRI/AIAAIC/OECD AIM/NVD from network)
```

Or run the steps individually:

```bash
python scripts/parse_existing.py     # legacy/ -> data/legacy_consolidated.json
python scripts/merge_and_dedupe.py   # legacy + ingest/* -> data/incidents.json
python scripts/render_markdown.py    # data/incidents.json -> INCIDENTS.md + docs/incidents/<year>.md + data/stats.json
python scripts/render_docs_stats.py  # data/stats.json -> templated counts in README/DATASHEET/site/CITATION.cff
python scripts/check_stats_drift.py  # CI gate: fails on drift or an unmarked hardcoded total
python scripts/validate.py           # schema check
```

Dedupe keys (first hit wins): (a) matching `cve_ids`, (b) matching `source_ids` (with `AIID-N-OECD` canonicalised to `AIID-N`), (c) matching normalized reference URL, (d) fuzzy title match within ±1 year — (c) and (d) are weak keys and refuse to fire across two entries with disjoint CVE sets. After each merge the indices are reindexed so transitive dupes (entry A absorbs CVE-3, then entry B with CVE-3 already exists → B is merged into A as well) all collapse. Merges union taxonomy mappings, references, tags, CVE/CWE IDs, and source IDs; take the highest severity; prefer the more-specific date (YYYY-MM-DD beats year-only) and reject future-year dates.

`added` and `updated` are preserved from the previous output; `updated` only bumps when an entry's content actually changes. That keeps `make build` deterministic for CI drift checks.

---

## Adding entries

Two paths:

1. **Manual**: append a properly-shaped object to `data/incidents.json` and run `scripts/render_markdown.py`. Ensure `references` has at least one resolvable URL.
2. **Automated**: drop a JSON array of raw entries into `ingest/<your_source>.json` (any reasonable shape — see `scripts/merge_and_dedupe.py` `normalize_entry` for the field tolerance), then re-run merge + render.

Always run `scripts/validate.py` before committing.

---

## Taxonomy mappings

The mapping files in `mappings/` document the controlled vocabulary used in this dataset. They are derived from the original sources:

- OWASP LLM Top 10 (2026): <https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/>
- OWASP Agentic Top 10 (ASI / "Agentic AI – Threats and Mitigations"): <https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/>
- NIST AI Risk Management Framework (AI 100-1): <https://www.nist.gov/itl/ai-risk-management-framework>
- NIST AI 600-1 Generative AI Profile: <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>
- MITRE ATLAS: <https://atlas.mitre.org/>
- MAESTRO (companion): <https://genai.owasp.org/resource/genai-security-project-maestro/>

When a framework releases a new version, update the mapping JSON in `mappings/` and re-run merge + validate.

---

## Sources aggregated

The current dataset draws from the following public sources. Each entry retains links back to the originating advisory, post, or paper:

- **OWASP GenAI Security Project** — incident roundups + Top 10 references
- **AI Incident Database (AIID)** ([incidentdatabase.ai](https://incidentdatabase.ai/), [github.com/responsible-ai-collaborative/aiid](https://github.com/responsible-ai-collaborative/aiid)) — ingested via AIID's official weekly snapshot archive (not per-page scraping); title + structured facts only, no verbatim narrative retained
- **OECD AI Incidents Monitor (AIM)** ([oecd.ai/en/incidents](https://oecd.ai/en/incidents)) — cross-listed against AIID via the official AIID-OECD bridge file; `title`/`summary` are LLM-generated (OpenAI o3-mini) from third-party news of unresolved copyright status, so `description` is reduced to structural facts + link and carries a per-entry OECD attribution (decision E21); `title` itself remains an open question — see [`NOTICE-DATA`](NOTICE-DATA) and `docs/SOURCE_LICENSES.md` §1.5
- **AIAAIC** ([aiaaic.org](https://www.aiaaic.org/aiaaic-repository)) — AI, Algorithmic, and Automation Incidents and Controversies; a CC BY-SA 4.0 source reduced to title/headline + categorical facts + link (decision D2), with row-level attribution/share-alike honored via a per-entry marker and an open database-right question — see [`NOTICE-DATA`](NOTICE-DATA) and `docs/SOURCE_LICENSES.md` §1.1
- **MITRE ATLAS** ([atlas.mitre.org](https://atlas.mitre.org/), [github.com/mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data)) — all case studies parsed from the YAML corpus
- **AVID** — AI Vulnerability Database ([avidml.org](https://avidml.org/))
- **CSET-AIID Harm Taxonomy** ([github.com/georgetown-cset/CSET-AIID-harm-taxonomy](https://github.com/georgetown-cset/CSET-AIID-harm-taxonomy)) — controlled vocabulary reference
- **NVD / CVE.org / GitHub Security Advisories / OSV.dev / CISA KEV** — AI/ML/LLM/agent CVEs pulled via REST API across a broad, actively-maintained keyword list
- **NVIDIA garak** ([github.com/NVIDIA/garak](https://github.com/NVIDIA/garak)) — one entry per LLM vulnerability scanner probe (canonical attack classes)
- **promptfoo** ([github.com/promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)) — one entry per red-team plugin/strategy
- **ModelOriented/CVE-AI** ([github.com/ModelOriented/CVE-AI](https://github.com/ModelOriented/CVE-AI)) — XAI-based AI model validation findings
- **Researcher and vendor blogs** — Embrace The Red, Tenable, Palo Alto Unit 42, Trail of Bits, Aim Security, Noma Security, Wiz Research, Lakera, Invariant Labs, PromptArmor, Pillar Security, Token Security, HiddenLayer, Robust Intelligence, Protect AI, Cato Networks CTRL, Endor Labs, Sysdig, Zenity Labs, JFrog, Datadog Security Labs, Reco, AppOmni, BeyondTrust, Oasis Security, Mindgard, Koi Security, Imperva, Sonar, Oligo Security, OX Security, SentinelOne, Check Point Research, Trend Micro, Tinfoil Security, ZeroPath, Cymulate, MaccariTA, and others.
- **Vendor threat reports** — Anthropic, OpenAI, Google Threat Intelligence (GTIG/TAG/Mandiant), Microsoft Threat Intelligence (MTAC/MSRC), AWS Security Bulletins, CrowdStrike, Recorded Future.
- **Academic papers** — selected USENIX Security / NDSS / S&P / CCS / arXiv entries with concrete adversarial PoCs.

If a source is missing or mis-attributed, open an issue or PR. **One tracked source is currently stale** (MIT AIRI Navigator's public bulk download was withdrawn; the corpus keeps re-emitting its last-fetched snapshot, unshrunk, under a dated hold) — see [`data/source_freshness.json`](data/source_freshness.json) for the reviewed, published status of every source this project actively monitors.

---

## Contributing

PRs welcome. Please:

- Add at least one verifiable URL per entry.
- Map to the four core taxonomies where applicable (MAESTRO and VERIS are not contributor-set — see CONTRIBUTING.md). If unsure, leave the field empty rather than guess.
- Run `scripts/validate.py` and `scripts/render_markdown.py` before opening a PR.
- For incidents you authored or first reported, that's totally fine — but please link the canonical writeup.

---

## Licensing

**MIT** for code (`scripts/`, `schema/`, `src/genai_incidents/`) — [`LICENSE`](LICENSE). **CC-BY-4.0** for the dataset and documentation (`data/`, `INCIDENTS.md`, `mappings/`, `docs/`) — [`LICENSE-DATA`](LICENSE-DATA). Neither of those is the whole story:

- **Two verbatim text bodies are Apache-2.0, not CC-BY-4.0, and are not relicensed by it**: MITRE ATLAS case-study text and NVIDIA garak probe docstrings, each reproduced under its own upstream license with its own attribution requirement that stays attached to that material specifically.
- **AIAAIC-derived rows (a CC BY-SA 4.0, share-alike source) carry a row-level `content_license` marker** — machine-readable, naming AIAAIC as the attribution/share-alike target on the specific rows it applies to, mirrored into the STIX export as `x_content_license`. This is a per-row obligation honored proactively, not a dataset-wide CC-BY-SA carve-out.
- **The OECD AI Incidents and Hazards Monitor (AIM) is a third upstream source carrying an active content obligation.** Its `description` field on AIM-sourced rows is reduced to structural facts and a source link rather than AIM's own LLM-generated summary text, and every AIM-sourced row carries a per-entry OECD attribution citation. The `title` field on those same rows is **not** covered by that reduction and remains a separate, open question.
- **AIID, despite also being a CC BY-SA source, is a resolved question, not an open one** for the population this project ships — the legal analysis concludes no row-level marker is owed there. The two sources reach different outcomes under the same kind of license grant for reasons specific to each maker's legal situs, not because one was treated more carefully than the other.

None of the above is exhaustive, and stating exact per-source row counts here would only drift out of sync with the audit that actually tracks them. [`NOTICE-DATA`](NOTICE-DATA) and [`docs/SOURCE_LICENSES.md`](docs/SOURCE_LICENSES.md) are the authoritative, currently-maintained accounts of every source's terms, this project's remediation for each, and the current per-source figures — read those, not this summary, before making a decision that depends on the details.

## How to cite

- **Citing the dataset as a whole** (statistics, trend analysis, benchmark construction, or other aggregate use): cite this repository using the preferred citation in [`CITATION.cff`](CITATION.cff), or the DOI badge above.
- **Citing an individual incident**: cite that incident's own primary source, not this repository. Every incident entry links to its underlying source(s) in its References section — use that link (or, for AIID-derived entries, the AIID citation URL already shown on the entry) as the citation. Citing genai_incidents alone for a single incident credits this aggregator instead of the reporter, researcher, or outlet who actually surfaced it.
- **Concept DOI vs. version DOI**: the DOI badge and `CITATION.cff` (`10.5281/zenodo.20248675`) are Zenodo's **concept DOI** — it always resolves to the latest release, and is the one to cite for general or ongoing use. Cite a release's own **version-specific DOI** only when deliberately pinning to that exact version (e.g. reproducing a result against a specific snapshot); see that release's own Zenodo record for its version DOI.
