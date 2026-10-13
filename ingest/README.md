# `ingest/`

Each `*.json` file here is a per-source aggregator output — a top-level JSON array of incident-shaped objects in a tolerant input schema (it doesn't need to match `schema/incident.schema.json` exactly; `scripts/merge_and_dedupe.py` normalizes on the way in).

## Adding a new source

1. Create `ingest/<source>.json` containing a JSON array of raw entries. Minimum per entry:

   ```jsonc
   {
     "source_id": "<unique-id-from-the-source>",
     "title": "...",
     "date": "YYYY-MM",
     "year": YYYY,
     "description": "...",
     "references": [{"url": "https://..."}]  // at least one URL required
   }
   ```

   All other fields (taxonomies, severity, etc.) are optional but encouraged.

2. Run `python scripts/merge_and_dedupe.py` — the normalizer will:
   - Coerce to the canonical schema
   - Backfill MITRE ATLAS / NIST AI RMF from OWASP codes if you didn't provide them
   - Dedupe by CVE → reference URL → fuzzy title match
   - Assign stable `INC-NNNNN` IDs

3. Run `python scripts/validate.py` and `python scripts/render_markdown.py`.

## Current source files

| File | Source | Notes |
|---|---|---|
| `aiid_incidents.json` | AI Incident Database security-relevant subset | Some entries also reference vendor/research writeups for verification |
| `aiid_full.json` | AI Incident Database, via AIID's official weekly snapshot channel (`scripts/ingest_aiid_snapshot.py`, `make ingest-aiid`) | Facts + link only — title + structured facts (date/entities/MIT taxonomy); AIID's own narrative `description` is used only as an ephemeral classification signal, never persisted. See `docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md`. |
| `atlas_incidents.json` | MITRE ATLAS case studies + adversarial-ML research cited in ATLAS | All entries map at least one ATLAS technique |
| `avid_owasp_incidents.json` | AVID + OWASP GenAI Project incident roundups | AVID taxonomy codes (`S/E/P-####`) preserved in `avid_categories` |
| `cve_incidents.json` | NVD-verified CVEs affecting AI/ML/LLM/agent stacks (2022-2026) | Every entry has a verified CVE ID and NVD URL |
| `research_incidents.json` | Researcher and vendor security blog disclosures | Embrace The Red, Tenable, Unit 42, etc. |
| `bounty_incidents.json` | HackerOne / huntr.dev / Bugcrowd disclosed AI bounties | _(may be present)_ |
| `arxiv_incidents.json` | arXiv + venue papers demonstrating concrete AI attacks | _(may be present)_ |
| `wave12_avid.json` | AVID (`avidml/avid-db`, MIT), via the GitHub tarball (`scripts/ingest_avid.py`, `make ingest-avid`) | CVE-derived and third-party reports only; the 556 automated garak scan results are excluded (INCLUSION.md section 3). MIT provenance per row in `content_license`. |
| `wave12_cvelistv5.json` | CVE Program record dump (`CVEProject/cvelistV5`, CVE ToU), AI-relevance filtered, huntr CNA tagged (`scripts/ingest_cvelistv5.py`, `make ingest-cvelistv5`) | New CVEs only; REJECTED records never emitted. Filter: `scripts/ai_relevance.py`. |
| `wave12_arxiv.json` | arXiv cs.CR metadata via OAI-PMH (CC0), deterministic attack-on-GenAI filter (`scripts/ingest_arxiv_oaipmh.py`, `make ingest-arxiv`) | Metadata only, never full text. Complements, does not reproduce, `arxiv_incidents.json`. |
| `*.provenance.json` | Per-ingest provenance (release tag, hashes, window, yields, skipped-and-why) | Not sources: the merger reads them as zero rows. |
| `threat_reports_incidents.json` | Vendor TI reports (Anthropic, OpenAI, GTI, MSTIC, etc.) | Each named operation/actor is split into its own entry |

## Licensing of the files in `ingest/`

The `*.json` files here are third-party upstream snapshots, or hand-curated
records derived from third-party sources. **They stay under each upstream's own
terms.** They are not covered by this project's CC BY 4.0 data grant
(`LICENSE-DATA`) or its MIT code licence (`LICENSE`), and no specific licence
(CC0, CC BY or other) is claimed for them. Some hand-curated files also contain
the maintainers' own short summaries and links; the file as a whole is still
marked with the upstream terms. In `.reuse/dep5` they carry the identifier
`LicenseRef-upstream-terms` (explained in `LICENSES/LicenseRef-upstream-terms.txt`).
The terms per source, and what this project does with each, are in
[`docs/SOURCE_LICENSES.md`](../docs/SOURCE_LICENSES.md); the notices the upstreams
require to travel with copies are in [`NOTICE-DATA`](../NOTICE-DATA).
`UNKNOWN` in `docs/SOURCE_LICENSES.md` means no rights are claimed, not that rights
are granted.

Project-authored files here keep the project's licences: `*.provenance.json`
(per-ingest provenance), `_state/` (source-health and probe state) and this
`README.md` are CC BY 4.0; `common.py` and `__init__.py` are MIT. The pinned MITRE
ATLAS snapshot `atlas/ATLAS-*.yaml` is Apache-2.0 (its own `.reuse/dep5` stanza).

`merge_and_dedupe.py` reads `ingest/*.json` only (`INGEST.glob("*.json")`), so this
`README.md` is never parsed as a source.

| File | Upstream | `docs/SOURCE_LICENSES.md` |
|---|---|---|
| `aiaaic_incidents.json`, `aiaaic_sheet_incidents.json` | AIAAIC Repository (CC BY-SA 4.0) | §1.1 |
| `aiid_full.json` | AI Incident Database, official snapshot | §1.2a |
| `aiid_incidents.json` | AI Incident Database, hand-curated rows | §1.2, §1.2a |
| `aiid_oecd_relationships.json` | AIID repo data file (ID and URL pairs) | §1.3 |
| `airi_navigator_incidents.json` | MIT FutureTech AIRI Navigator | §1.4 |
| `oecd_aim_full_incidents.json` | OECD AI Incidents and Hazards Monitor | §1.5 |
| `avid_owasp_incidents.json` | AVID (`AVID-*` rows) and OWASP Gen AI round-ups (`OWASP-*` rows) | §6.1, §1.6 |
| `research_incidents.json` | Researcher and vendor security blogs | §1.7 |
| `threat_reports_incidents.json` | Vendor threat-intelligence reports | §1.8 |
| `cisa_kev.json` | CISA Known Exploited Vulnerabilities | §2.1 |
| `cve_incidents.json`, `cve_nvd_expanded.json` | NVD, GitHub Security Advisories, OSV | §2.2, §2.3, §2.4 |
| `cve_rejections.json` | CVE Program record state (cvelistV5) | §2.5 |
| `wave12_cvelistv5.json` | CVE Program (cvelistV5, CVE Terms of Use) | §6.2 |
| `atlas_full.json`, `atlas_incidents.json` | MITRE ATLAS (Apache-2.0) | §3.1 |
| `garak_probes.json` | NVIDIA garak | §3.3 |
| `promptfoo_plugins.json` | promptfoo | §3.4 |
| `cve_ai_curated.json` | ModelOriented/CVE-AI | §3.5 |
| `redteam_benchmarks.json` | Academic red-team benchmark citations | §4 |
| `arxiv_incidents.json`, `wave12_arxiv.json` | arXiv papers and cs.CR metadata | §6.3 |
| `wave12_avid.json` | AVID (`avidml/avid-db`, MIT) | §6.1 |

## File order is load-bearing

`merge_and_dedupe.py` reads `ingest/*.json` in **sorted name order**, and a
reference-URL key goes to the first row that claims it. A new-source file that
sorts *before* an existing source can take that key from a grandfathered
multi-CVE entry and split it (measured 2026-10-03: ten entries, aborted by the
WS4-T19 split guard). New-source files therefore carry a `wave12_` prefix so
they sort after every existing source, and each new-source ingest skips any
row the merger would fold into an existing entry (`scripts/corpus_overlap.py`).
Keep both properties when adding a source.

## Re-running `ingest-cvelistv5` changes the data unless pinned

`make ingest-cvelistv5` with no arguments fetches the NEWEST baseline asset, so the output (and the
corpus) changes. The committed `wave12_cvelistv5.json` is pinned to release `cve_2026-10-03_1400Z`, asset
`2026-10-03_all_CVEs_at_midnight.zip.zip` (sha256 `2fa5d5e25b35...`, in the provenance file). To reproduce it
from a cached copy:

```
python scripts/ingest_cvelistv5.py --from-file ingest/_cache/cvelistv5/2026-10-03_all_CVEs_at_midnight.zip.zip     --release-tag cve_2026-10-03_1400Z
```

Run `make ingest-avid` first (cvelistV5 reads its AVID-to-CVE crosswalk), and against the pre-ingest corpus
(`git checkout <base> -- data/`): both scripts skip anything already in `data/incidents.json`.

## Don't

- Don't paste full HTML scrapes here. Summarize.
- Don't include entries without a verifiable URL.
- Don't worry about deduping against the rest of the dataset — the merger handles that.
