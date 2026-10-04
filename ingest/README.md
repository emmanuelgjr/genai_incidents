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
