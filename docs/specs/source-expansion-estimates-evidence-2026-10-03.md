# Source-expansion estimates: evidence (commands and raw counts)

**Dated record, measured 2026-10-03 by pipeline-engineer. Do not regenerate.**
(Working agreement 4.) It backs sections 4 and 5 of
`docs/specs/source-expansion-evaluation.md`. Raw counts and ID lists:
`docs/specs/source-expansion-estimates-evidence-2026-10-03.json` (same
directory). Corpus measured: `data/incidents.json` at `e2b1c988`
(13,361 entries, `generated` 2026-09-18).

## Conduct while measuring

Every live request below was sent through `ingest/common.py::fetch_once`
(imported from a scratch script outside the repo): identifying User-Agent,
robots.txt check (fail-closed), at least 3.0 s between requests to one host
(3.2 s typical; 7 s for NVD, 10.5 s for the BSI index, 6.5 s for ICO). Three
robots.txt files that `common.py` itself refuses to read were read once, directly,
with the same User-Agent (`export.arxiv.org`, `arxiv.org`, `static.data.gouv.fr`).
Nothing was fetched from a host or path that robots disallows (BAILII, CanLII,
ANSSI `/pdf` and `/fiche/`, AP `/documenten`, DEF CON, ACSC were not
fetched). The measuring scripts are **not** committed (no new scripts under
`scripts/` or `ingest/`); their logic is the commands below.

## Method-suspect disclosure (agreement 6)

Overlap figures use two independent paths where one existed. huntr: the NVD
CNA path (`sourceIdentifier`) against the bounty-URL path in the corpus, which
agree on direction (below). EUVD: a path (EUVD full-text search) different from
the one that built the corpus (NVD keyword sweep). The AI-relevance regex is a
**proxy**, not a label: it was spot-read (12 + 15 + 14 sampled items, all
plausibly AI/ML software). The input that would make each overlap check fail:
a CVE-id regex that matches nothing (the checks return both in-corpus and
not-in-corpus items, 911 / 302 for EUVD, 135 / 233 for huntr, so they
discriminate).

**Gate update 2026-10-03 (do not regenerate):** the membership test keyed on `CVE-` ids in `source_ids` only. 9 of the 302 EUVD ids and 5 of the 233 huntr ids are in the corpus as AVID-keyed entries whose title names the CVE. Corrected: 293 and 228; union 416. The input that makes this check fail is a CVE held under a non-CVE source id.

## Proxy AI-relevance regex (`TIGHT`, case-insensitive, on CVE description)

`llms? | large language models? | language models? | machine[- ]learning |
deep learning | neural networks? | pytorch | tensorflow | hugging ?face | mlflow |
onnx | keras | langchain | llama[-_ ]?index | ollama | gradio | openai | chatgpt |
prompt injection | jailbreak | model context protocol | mcp servers? | ai agents? |
agentic | generative ai | artificial intelligence | ai models? | ml models? | vllm |
triton inference | ray serve | bentoml | anything-?llm | flowise | autogpt |
crewai | autogen | langflow | dify | ragflow | lollms | text-generation-webui |
comfyui | stable[- ]diffusion | diffusers | transformers library | pickle(d)? model |
model files? | vector (database|store) | embedding model | rag | copilot |
cursor ide | claude | gemini | n8n | open[- ]webui | librechat | paddlepaddle | h2o`
(all with `\b` word boundaries). It over-matches (for example "copilot", "rag")
and under-matches (any AI software not in the list), so counts are labelled
proxy counts.

## Commands

1. **Corpus baselines (local).** Python over `data/incidents.json`: CVE ids in
   `source_ids` (6,986), CVE ids anywhere (7,156), AVID ids (110 anywhere, 109 in
   `source_ids`), arXiv ids (149 URLs), huntr bounty URLs
   (`huntr\.(com|dev)/bounties/[0-9a-f-]+`: 277 distinct IDs, 210 entries).
2. **huntr CNA via NVD.** `GET https://services.nvd.nist.gov/rest/json/cves/2.0?sourceIdentifier=security@huntr.dev&resultsPerPage=2000&startIndex={0,2000}` (min interval 7 s): `totalResults` 2,496.
3. **huntr.com probes.** `GET /sitemap.xml` 404, `GET /bounties` 404, `GET /bounties/<uuid>` 200 (75,276 B) with generic title and none of `CVE-`, `CWE`, `Severity`, `Disclosed`, `Repository`, `cvss` in the body.
4. **EUVD.** `GET https://euvdservices.enisa.europa.eu/api/search?text=<term>&size=100&page=<n>` for 26 terms (`large language model`, `LLM`, `machine learning`, `artificial intelligence`, `prompt injection`, `langchain`, `model context protocol`, `MCP server`, `pytorch`, `tensorflow`, `hugging face`, `AI agent`, `vector database`, `mlflow`, `ollama`, `llama`, `vllm`, `neural network`, `deep learning`, `onnx`, `gradio`, `jupyter`, `openai`, `chatbot`, `generative ai`, `transformers`). The search is fuzzy (`vector database` returned 872 items), so raw totals are not AI-relevant counts. 3,873 distinct items, all with a CVE alias.
5. **AVID.** `GET https://api.github.com/repos/avidml/avid-db/git/trees/main?recursive=1` (not truncated); 40-report random sample (`random.seed(11)`) of 2026 reports via `raw.githubusercontent.com/avidml/avid-db/main/reports/2026/<id>.json`.
6. **cvelistV5.** `GET api.github.com/repos/CVEProject/cvelistV5` and `/releases?per_page=3`.
7. **CISA CSAF.** `GET api.github.com/repos/cisagov/CSAF/git/trees/develop?recursive=1` (not truncated, 12,226 entries). `GET www.cisa.gov/cybersecurity-advisories/all.xml`, `.../ics-advisories.xml`, `/news.xml`: HTTP 403 each.
8. **arXiv.** `export.arxiv.org` is refused by `common.py` (its robots.txt is `User-agent: *` / `Disallow: /`, read directly). Sample via `GET https://oaipmh.arxiv.org/oai?verb=ListRecords&metadataPrefix=arXiv&set=cs:cs:CR&from=<d>&until=<d+6>` for the first full week of June 2023-2026; one response page each (no resumption token).
9. **JVN.** `GET https://jvndb.jvn.jp/myjvn?method=getVulnOverviewList&feed=hnd&lang=en&maxCountItem=1&rangeDatePublic=n&rangeDatePublished=n&rangeDateFirstPublished=n&datePublicStartY=Y&...EndD=31[&keyword=K]`, read `totalRes` from `status:Status`. `feed=sec` returns `errCd XX00000001`. The first attempt with `dateFirstPublished*` parameters returned 0 for everything (wrong parameter family), so those zeros were discarded.
10. **Feeds.** NCSC `.../api/1/services/v1/all-rss-feed.xml`; CCCS `.../api/cccs/rss/v1/get?feed=alerts_advisories&lang=en`; ANSSI `/avis/feed/` and `/alerte/feed/`; JPCERT `/english/rss/jpcert-en.rdf` and `/rss/jpcert.rdf`; JVN `/en/rss/jvn.rdf`; WID `/content/public/securityAdvisory/rss`; CERT-EU `/publications/security-advisories-rss`. Titles scanned with `\b(AI|artificial intelligence|machine learning|LLM|large language|generative|intelligence artificielle|KI|...)\b`.
11. **WID CSAF.** `GET https://wid.cert-bund.de/.well-known/csaf/white/index.txt` (min interval 10.5 s to honour the BSI Crawl-delay): 13,874 lines.
12. **Sitemaps.** `enisa.europa.eu/sitemap.xml` (2,946 URLs) and `ncsc.gov.uk/sitemap.xml?page=1,2` (2,638 URLs); AI filter = slug contains `ai`, `artificial`, `machine-learning`, `ml`, `llm`, `generative`, `genai`, `chatbot` as a hyphen-delimited token.
13. **EDPB.** `GET .../register-for-article-60-final-decisions_en` (last pager index 143, 11 per page) and `?topic[552]=552` (topic "AI and technology"; last pager index 4).
14. **ICO.** `GET ico.org.uk/action-weve-taken/enforcement/` with 6.5 s spacing: 49,963 B, results container reads "Loading...", no result links in the static HTML.
15. **CNIL.** `GET www.data.gouv.fr/api/1/datasets/?q=sanctions CNIL` (dataset 591af43d88ee3826b379093a, licence `fr-lo`, newest resource 2025-05-05, "depuis 2019" CSV dated 2024-10-01). The CSV is on `static.data.gouv.fr`, whose robots.txt carries `Disallow: /resources`: refused.
16. **Robots gate matrix.** `ingest.common.robots_allowed(url)` over 46 URLs in two passes (33 + 13; results in the JSON, key `common_py_robots_gate_results`).
17. **Stale-reject check.** NVD `vulnStatus == "Rejected"` among the 2,496 huntr-CNA CVEs (111) intersected with corpus `source_ids`: 17 corpus entries (18 CVE ids), all `source_status: active`, none with a rejection marker.

## What was NOT measured (so section 4 labels it [estimated])

HackerOne volume (no documented API), Black Hat and DEF CON volumes
(`defcon.org` unreadable through `common.py`), ACSC (robots unverifiable),
Garante, AP, ANPD, OPC, CNIL volumes (no countable structured channel reached),
CISA AI-document counts (`cisa.gov` feeds 403), and the share of overlapping CVEs
whose CVSS differs between sources (the corpus keeps one score).
