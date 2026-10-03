# Source-expansion tranche 1: estimates evidence (commands and raw counts)

**Dated record, measured 2026-10-03 by pipeline-engineer. Do not regenerate.**
(Working agreement 4.) It backs the "Estimates (pipeline-engineer)" and "Ranking"
sections of `docs/specs/source-expansion-tranche1-evaluation.md`. Raw counts and
name lists: `docs/specs/source-expansion-tranche1-estimates-evidence-2026-10-03.json`
(same directory; parses under strict UTF-8). Corpus measured: `data/incidents.json`
in this worktree (13,361 entries, `generated` 2026-09-18). Format follows
`source-expansion-estimates-evidence-2026-10-03.md` (tranche 2).

## Conduct while measuring

Every request went through `ingest/common.py::fetch_once` (imported from scratch
scripts outside the repo; none committed): identifying User-Agent, robots.txt check
(fail-closed), per-host spacing. Spacing was 3.0 s by default, 5.0 s for
`www.ftc.gov`, and **2.0 s for the 136-file AVID scan on
`raw.githubusercontent.com`** (below the 3 s used in tranche 2; `common.py`'s own
default is 1.0 s). Hosts contacted: `api.github.com` (about 30 calls),
`raw.githubusercontent.com` (about 170 files), `huggingface.co` (3),
`com-courtlistener-storage.s3.us-west-2.amazonaws.com` (about 22: listings, one
HEAD, one 300 KB and one 8 MB Range read), `wiki.free.law` (1 page),
`www.ftc.gov` (robots.txt only, always HTTP 403). **Never contacted:**
`www.courtlistener.com` (robots `Disallow: /`), any `ftc.gov` content path,
`0din.ai`. No `git clone`. No model call. The 0din JSONL was read in memory and only
metadata fields were kept (uuid, dates, title, severity, model list); the prompt,
response, variant and signature fields were never written to disk.

## Method-suspect disclosure (agreement 6)

- **Name proxies are not labels.** OpenSSF AI relevance is a regex over package
  names (strict and broad token lists below), then a spot-read of record summaries.
  The input that makes the proxy fail: it flagged 100 of 185 strict npm names as AI
  when they were `gemini` as a constellation word in a tea.xyz token-farming
  campaign; I removed them by a second heuristic (name contains the token `gemini`
  and has 3 or more hyphen/underscore parts, with no other strict token). That
  second heuristic is itself a guess and is stated, not hidden. Broad-only npm names
  also contained 147 `*_replicate_automation` / `*_z3n` spam names, removed the same
  way.
- **Precision is n=10 (pypi strict) and n=4 (npm, all spam before the filter).** Too
  small to publish as a rate; it is used only to say the proxy over-counts by a
  factor of about two.
- **npm is only partly listed.** The git trees API truncates at 100,000 entries, so
  the npm tree listing stops at `lintang-tea65`. Counts for npm are lower bounds on
  the names seen, not on the repo.
- **The CourtListener sample is not representative.** One 8 MB Range read, 98,837
  rows, not the last rows of the file (a bz2 stream cannot be decoded from its
  end). It shows density, not volume.
- **Overlap checks that can fail.** Corpus-overlap regexes were run on a name that
  must be present (`Rite Aid`, `Clearview`, `Malware in <name>`) and returned
  non-zero, so they discriminate. One probe (`Raine`) matched `Ukraine` (143
  entries) and is discarded. The AVID-to-0din link was found by reading AVID
  records, a different path from comparing titles, which matched only 1 of 73.

## Commands

All fetches below are `common.fetch_once(url, min_interval=...)`.

### T1.8 OpenSSF malicious-packages

1. `GET api.github.com/repos/ossf/malicious-packages/contents/osv/malicious` lists
   the ecosystem directories and their tree shas: crates.io, git, go, maven, npm,
   nuget, packagist, pypi, rubygems, vscode, vscode:open-vsx.org.
2. `GET .../git/trees/<sha>?recursive=1` per ecosystem. JSON blobs: pypi 11,780
   (not truncated), rubygems 4,238, nuget 782, crates.io 20, go 20, maven 2,
   vscode 4, packagist 1. **npm: truncated**, 37,382 blobs visible. A
   non-recursive `trees/<npm sha>` also truncates at exactly 100,000 entries
   (96,505 unscoped, 3,495 `@scope` directories), first name `--hiljson`, last
   `lintang-tea65`.
3. pypi records by id year (from file names `MAL-YYYY-N.json`): 2022: 20, 2023:
   6,467, 2024: 2,476, 2025: 1,419, 2026 (to 3 Oct): 1,398. Strict-token pypi names
   by year: 2023: 23, 2024: 9, 2025: 12, 2026: 30.
4. Strict token list (word-boundary on name parts): openai, chatgpt, gpt, llm, llms,
   langchain, langgraph, llamaindex, ollama, huggingface, tensorflow, pytorch,
   torch, keras, anthropic, claude, gemini, deepseek, mistralai, sklearn, scikit,
   onnx, mcp, copilot, vllm, gradio, autogpt, crewai, autogen. Broad-only adds ai,
   ml, genai, chatbot, llama, rag, replicate, embedding(s), transformers, diffusers,
   diffusion, streamlit, cohere, groq, bard, whisper. Counts: pypi strict 74
   (73 after the gemini filter), broad-only 47; npm unscoped strict 185 (85 after),
   broad-only 285 (138 after dropping spam); npm scopes strict 6; nuget strict 1;
   rubygems strict 1.
5. Spot-read: 10 pypi strict names and 4 pypi broad names (random.seed 20261003),
   `raw.githubusercontent.com/ossf/malicious-packages/main/osv/malicious/pypi/...`.
   Fields seen: `id` (`MAL-YYYY-N`), `summary` ("Malicious code in X (PyPI)"),
   `details` (per-source text from kam193, reversing-labs, amazon-inspector,
   checkmarx, ossf-package-analysis), `aliases` **null in all 14**, `references`
   (type WEB/ARTICLE), `database_specific` with `malicious-packages-origins` and, on
   some records, `iocs`. By summary, 5 of 10 strict names are AI-library targeting
   (instructor-mcp, scikit-leran, mlc-llm-nightly, strands-agents-anthropic,
   ant-mcp-proxy-for-test); the other 5 only carry an AI token in the name.
   4 npm names read (one API contents call each): all tea.xyz campaign.
6. Corpus overlap: titles `Malware in <name>` are 79 entries, all GHSA-keyed
   (2025: 37, 2026: 39, 2024: 2, 2022: 1); 62 of the 79 names are AI-named by the
   strict regex. Of the cleaned strict candidates, pypi 0 of 73 and npm 17 of 91
   already have a `Malware in <name>` entry. Entries containing a `MAL-` id: 1
   (INC-08450).
7. `content_license` in `schema/incident.schema.json`: one object, `obligations`
   enum is `attribution` or `share-alike`, 1,517 rows marked, all CC-BY-SA-4.0.

### T1.6 0din (Hugging Face corpus)

1. `GET huggingface.co/api/datasets/0dinai/public-disclosures`: sha `9c75d830...`,
   `lastModified` 2026-05-15T16:28:59Z, license tag cc-by-4.0, files
   `manifest.json`, `vulnerabilities.jsonl`.
2. `GET .../resolve/<sha>/manifest.json`: `record_count` 80, `generated_at`
   2026-05-15T16:28:53Z, schema 1.1.0. `GET .../vulnerabilities.jsonl`: 596,614 bytes,
   80 rows. `detection_signature`, `messages`, `variant_prompts` appear in 6 rows only.
   Published by month: 2025-02: 1, 2025-07: 17, 2025-08: 9, 2025-09: 8, 2025-10: 8,
   2025-11: 8, 2025-12: 2, 2026-01: 6, 2026-02: 10, 2026-03: 1, 2026-04: 10. Severity:
   79 low, 1 medium. `reference_urls` empty in all 80; no CVE id in any summary.
3. Title match against the corpus found 1 of 73 quoted-tactic titles
   (INC-02924). That under-counts. **Different route:** AVID-2026-R0059 (the source
   of INC-02924) cites `https://0din.ai/disclosures/<uuid>`. Scan of
   `raw.githubusercontent.com/avidml/avid-db/main/reports/2026/AVID-2026-R0001..R0136.json`
   (136 files, 0 errors; stop rule: 12 consecutive misses after R0061): reports
   R0059 to R0124 (66 reports) each cite one 0din uuid; all 66 uuids are in the HF
   corpus. 14 HF uuids are not in the scan; they were published 2026-02 (3), 2026-03
   (1), 2026-04 (10). The corpus holds 2 of the 66 AVID reports (R0059 -> INC-02924,
   R0060 -> INC-02923). No 0din uuid appears in the corpus text.

### T1.4 CourtListener (bulk S3 only)

1. `GET wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data`
   (robots_allowed True; page is JS-rendered, not parsed).
2. S3 listings `GET <bucket>/?list-type=2&prefix=bulk-data/<type>-&max-keys=1000`
   (bucket `com-courtlistener-storage`, robots_allowed True). Newest key for
   dockets, opinions, opinion-clusters, citation-map, parentheticals, oral-arguments
   is dated 2026-09-30 (current). Sizes of the 2026-09-30 files: dockets 5.14 GB,
   opinions 55.25 GB, opinion-clusters 2.47 GB, citation-map 0.53 GB, parentheticals
   0.29 GB, oral-arguments 0.69 GB (bz2). 37 dated dockets files since 2022-08.
3. Header: `HEAD` then `Range: bytes=0-299999` of `dockets-2026-09-30.csv.bz2`,
   decoded with `bz2.BZ2Decompressor`: 54 columns including `case_name`,
   `case_name_full`, `docket_number`, `date_filed`, `court_id`, `nature_of_suit`,
   `source`, `blocked`, `date_blocked`, `pacer_case_id`.
4. Tail sample: `Range: bytes=(L-8,000,000)-(L-1)`, bit-search for the bz2 block magic
   `31 41 59 26 53 59`, found at byte 88,982; fed `BZh9` + remainder to the
   decompressor; it yielded 41.5 MB then raised at the truncated block (expected).
   98,837 rows parsed. Core AI-defendant regex (openai, chatgpt, anthropic,
   stability ai, midjourney, character technologies, character.ai, clearview,
   perplexity, suno, udio, cohere, databricks, mosaicml, runway ai, deepseek):
   **1 hit** (Dalal v. Clearview AI, 1:25-cv-07804, S.D.N.Y., filed 2025-09-19). A
   looser regex (`ai`, `artificial intelligence`, `machine learning`, `llm`, ...)
   gave 9 hits, 2 to 3 of which are AI-related (Clearview; Healthy Home 365 v. Air
   AI Technologies; ArmorIQ AI trademark), the rest are surnames or company names.
   99 of the rows have nature-of-suit 820 (copyright).
5. Corpus probe for 12 named US AI suits: 9 found by name, 3 not found (see JSON).
6. Not done, by conduct: no request to `www.courtlistener.com`; `/api/` not used.

### T1.5 FTC

1. `robots_allowed('https://www.ftc.gov/legal-library/browse/cases-proceedings', 5.0)`
   returns False: `_get_robots_parser` logs `could not verify robots.txt for
   www.ftc.gov (HTTP Error 403: Forbidden)`. Repeated in 3 separate runs (cache
   cleared, 20 s apart) and by an explicit `fetch_once(.../robots.txt)`: always 403
   then `PermissionError`. No further request was made to the host.
2. A different User-Agent was **not** tried: that would be identity evasion and
   `common.py` strips caller UAs by design. The tranche-1 gate read the same robots.txt
   with curl and a default UA (pre-row T1.5). So the 403 is specific to this
   client's identity or to automated clients, and the host does **not** qualify for
   `ROBOTS_UNVERIFIABLE_ALLOWLIST` (which requires every client refused).
3. Corpus overlap, local only: 6 entries mention FTC or Federal Trade Commission in
   title/description/affected/impact; 2 entries carry an `ftc.gov` URL (INC-07386,
   INC-04395). Named FTC AI actions found by title: Rite Aid, Everalbum, DoNotPay,
   IntelliVision, Kurbo (Weight Watchers), Alexa COPPA. Not found: Rytr, Operation
   AI Comply, Workado, Air AI, Ascend Ecom, Click Profit, FBA Machine. The names are
   from the author's own knowledge, not fetched; whether each is an FTC action was not
   verified.

### Listed by name (corpus entries, local)

Entries (not lines) whose JSON contains: `kb.cert.org` 19, `VU#nnnnn` 1,
`securitylab.github.com` 18, `GHSL-yyyy-n` 27, `EPSS` or `epss` 0. These replace the
pre-row line counts (28, 40, 0), which counted lines.

## Verification recipe

- Re-run the T1.8 tree counts: steps 1 and 2 above; compare per-ecosystem blob counts
  (they grow weekly, so expect the pypi 2026 figure to be higher).
- Re-derive the 0din overlap by a second path: fetch
  `.../reports/2026/AVID-2026-R0059.json` and R0124, and check each cites
  `0din.ai/disclosures/<uuid>` with the uuid in the HF JSONL. A control that must
  fail: R0058 (Langflow CVE-2025-3248) and R0125 cite no 0din URL.
- Re-run the FTC check: `python -c "from ingest import common as c;
  print(c.robots_allowed('https://www.ftc.gov/legal-library/', 5.0))"` prints False
  while the 403 persists. If it ever prints True, the M=0 below is stale.
