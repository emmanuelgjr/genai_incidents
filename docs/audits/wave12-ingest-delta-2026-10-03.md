# Wave 1 + wave 2 ingest: field-level delta (2026-10-03)

Branch `ws4/wave12-ingest`, code commit `394b35ac` (the data commit follows it).
Machine-readable twin: `wave12-ingest-delta-2026-10-03.json`. Produced by
`scripts/audit/wave12_delta.py` from the corpus at `9604752f` (before) and the
rebuilt corpus (after). Working agreement 2: unintended deltas are defects.
**Dated record, do not regenerate** (working agreement 4): a later refresh gets its own delta.

## 1. Result

| | before | after | delta |
|---|---:|---:|---:|
| `incident_count` | 13,361 | 15,666 | **+2,305** |
| corpus `security` | 12,816 | 15,121 | +2,305 |
| corpus `ai-harm` | 545 | 545 | +0 |
| category `vulnerability-disclosure` | 5,784 | 8,034 | +2,250 |
| all other categories | 7,577 | 7,632 | +55 |

Invariant 1 (never headline incidents + vulnerabilities + capabilities as one
number): `incident_count` above is the project's own stat; the
vulnerability / other split is shown beside it, and no combined headline is
introduced. Invariant 6 (docs counts from `stats.json`): `render_docs_stats.py`
re-templated README, DATASHEET and `docs/index.html` from `data/stats.json`;
`check_stats_drift.py` is clean (5 surfaces). Both are marked active in the
brief; this task did not re-verify the plan's Active-from table.

**New entries: 2,305. Changes to existing entries: 0.**
No ID removed, new IDs are a contiguous append above INC-14910
(INC-14911 .. INC-17215), no existing ID changed meaning.

New entries by origin (an entry holds every source that reached it; AVID and
cvelistV5 rows for the same CVE fold into one entry, so the sum of rows
emitted (270 + 2,502 + 55) exceeds the entry count):

| origin | new entries | of which vulnerability-disclosure |
|---|---:|---:|
| cvelistv5 | 2,046 | 2,046 |
| avid + cvelistv5 | 104 | 104 |
| avid | 100 | 100 |
| arxiv | 55 | 0 |

New vulnerability entries by publication month: backlog window (to 2026-06) 876;
post-2026-06 1,374.

## 2. Existing entries: nothing changes, by construction and by measurement

The brief expected AVID to enrich about 600 existing CVE entries. **It does not,
on purpose.** Folding a new row into an existing entry rewrites that entry (the
merger unions source ids, references and tags, bumps `updated`, derives
`confidence`...), and the first builds did worse than that. The measured
failure sequence, kept here because it is the reason for three design choices:

1. First build, AVID CVE rows for CVEs already in the corpus emitted: the
   WS4-T19 split guard **aborted the build** (10 grandfathered multi-CVE entries,
   INC-13533 among them, would have been split into 19+ rows). Cause: an AVID row
   sorts before the NVD rows in merge order, takes the shared reference-URL
   key, and the grandfathered bridge between the NVD rows is lost.
2. With (1) fixed by not emitting CVE-in-corpus rows, rows carrying NEW CVEs that
   still shared an advisory URL or a title with a CVE-less existing entry (57 GHSA-only
   advisories, one AVID-keyed row) were folded into it by the merger, rewriting
   it: title (INC-09034: a Telnyx PyPI malware entry took the title and description of
   a Trivy CVE), date and year (INC-04082), severity (4 entries, up) and
   `quality_tier` (8 entries, `reviewed` to `auto`). The delta tool flagged 79
   unintended field changes across 59 existing entries.
3. One more split (INC-03558, the MindsDB entry) from a new CVE row that claimed
   the HiddenLayer advisory URL before the NVD rows did.

Design that removes all three (each with a test): (a) `scripts/corpus_overlap.py`
tests every candidate row against the merger's own keys and **skips** any row the
merger would fold into an existing entry, listing it with the colliding INC id in
the provenance file; (b) the new files are named `wave12_*` so they sort after
every existing source and cannot take a key from a grandfathered cluster (the brief
named `ingest/avid_full.json`; that name sorts before `cve_*` and was the trigger);
(c) an AVID-keyed corpus entry stands for the CVEs AVID's repo assigns to it.

Skipped, with the information preserved offline in the provenance files:

| source | skipped, CVE already in corpus | skipped, would fold into an existing entry |
|---|---:|---:|
| AVID | 498 (crosswalk AVID id -> CVE -> INC id in `wave12_avid.provenance.json`) | 7 |
| cvelistV5 | 2,139 | 65 (listed with INC id) |
| arXiv | 0 | 0 |

A future enrichment mechanism (extra source ids / cross-references on existing
entries, plus a schema home for AVID's SEP taxonomy, which `normalize_entry`
drops today) is the place to use that crosswalk; it needs a decision, not a
side effect of an ingest.

### ID set (invariants 3 and 9)

- new IDs: **2,305** (INC-14911 .. INC-17215)
- contiguous append above the old maximum (INC-14910): **True**
- IDs missing after: **0** (invariant 3)
- existing IDs whose meaning changed (source_ids/cve_ids lost, or title edited): **0** (invariant 9)

### Changes to EXISTING entries, by field

0 existing entries changed; 0 field changes explained by a rule, **0 unintended**.

| field | changes | intended | justification |
|---|---:|---:|---|

### Changed existing entries (id: fields)


Severity downgrades: 0.

The full per-field before/after for every changed entry is in the JSON twin (`changes[]`, one record per entry and field).


## 3. The delta check, proved to fire (working agreement 6)

`wave12_delta.py --self-test` corrupts a copy of the after-corpus five ways
(title edit, severity downgrade, dropped source id, removed entry, an unexplained
description rewrite); all five were CAUGHT. Then an end-to-end corruption of an
INPUT: `ingest/wave12_avid.json` row AVID-2026-R1258 was edited to claim
CVE-2025-23254 (held by INC-02646) with severity Low and a tampered title, the
corpus was rebuilt, and the delta tool exited 1:

```
UNINTENDED INC-02646 owasp_asi ['ASI01','ASI02','ASI03','ASI04','ASI06'] -> ['ASI01','ASI02','ASI03','ASI04','ASI05','ASI06']
problems: ['1 unintended field changes on existing entries']
```

(The merge keeps the existing entry's title and severity, so those two edits were
absorbed; the rule table still caught the derived-field change that no rule
explains, together with 8 rule-explained additive changes: references,
source_ids, tags, source_count, capec_ids, cwe_ids, last_seen, updated.) The
input was restored, the corpus restored from the pre-corruption copy
(sha256 verified), and the delta returned to 0 changes.

Not changed either: `data/id_deprecations.json` (no merge retired an ID), every
existing entry's `added` and `updated`. The one global field that moves is `generated`
in `data/stats.json` (2026-09-18 -> 2026-10-03), which is what templates the README
and site date.

Control: with the three new ingest files moved aside, the build of the base
branch reproduced the committed `data/incidents.json` byte for byte (no diff in
`git status`), so none of the zero-change result is drift hidden by a stale base.
Rebuild with the new files in place twice, byte-identical (sha256 of
`incidents.json` and `incidents.min.json` equal).

## 4. AVID (`ingest/wave12_avid.json`, 270 rows)

Channel: `api.github.com/repos/avidml/avid-db/tarball/main` (2 MB) through
`fetch_once`; no `git clone`, so nothing to register in `INGESTION_CONDUCT.md`.
Repo commit `8eda5f4`, tarball sha256 `c0d5f5e6c96170c1db7280ed0d6b5facbda472f54463682907df829e57bc80ce`. Licence: MIT for AVID's own
metadata and the third-party rows; CNA text on CVE-class rows is under the CVE ToU (see below).

Repo records read: 1,785 (drafts under `reports/review/` never read).
By class: {"LLM Evaluation": 556, "(none)": 1, "CVE Entry": 1098, "Third-party Report": 96, "AIID Incident": 18, "ATLAS Case Study": 16}.

| | rows |
|---|---:|
| `LLM Evaluation`, not emitted | 556 |
| already in corpus by AVID id | 87 |
| CVE reports failing the AI-relevance filter | 367 |
| CVE already in corpus (crosswalked) | 498 |
| would fold into an existing entry | 7 |
| **emitted** | **270** (183 CVE-keyed, 87 third-party reports) |

Corrections to the evaluation (section 4, AVID row), re-measured here:
- **The 556 `LLM Evaluation` reports are automated garak per-(model, probe) scan
  results** ("The model X was evaluated by the Garak LLM Vulnerability scanner
  using the probe Y"), the "AVID-native" share the n=40 sample saw. INCLUSION.md
  section 3 excludes benchmark runs, so none is emitted (`--include-evaluations`
  opts in). Net-new is therefore 270, not ~1,070.
- **213 of the 309 rows first built carried a machine-written "Reason for inclusion
  in AVID:" paragraph appended to the CNA text** (it argues, for instance, that
  Spring4Shell qualifies because Spring may sit in a serving stack). It is not
  part of the CVE record and it satisfied the AI-relevance test on its own
  ("...an AI model..."). It is stripped from `description`, and relevance is judged on
  the CNA text and affected product only. This is why 367 CVE reports
  are filtered out (flask-restx, Bot Framework SDK, Log4j, CUDA toolkit, Jenkins plugins,
  Apache Airflow...), listed in the provenance file for review.
- The repo yields 1,785 published records (1,794 JSON files including 9 drafts under
  `reports/review`); the evaluation's tree count was 1,790. 87 non-evaluation
  records are already in the corpus by AVID id; `AVID-2023-V025` is absent from the repo
  (as the evaluation found).
- Third-party reports (87 rows) carry ORIGINAL deterministic prose from facts (id, class, month, affected
  artifacts, publishing host), `description_provenance: original`, MIT marker, no sentence of the report
  (gate defect 3, foreman ruling: the code matches SOURCE_LICENSES 6.1).
- CVE-class rows are CNA text: `content_license` is the CVE ToU marker (`CVE_TOU_MARKER`) and
  `description_source: cve-cna-via-avid` (gate defect 2); only the 87 third-party rows carry the MIT marker.

Spot-read, 25 of 270 seeded random (seed 2026): all 25 are AI/ML software
or model-vendor jailbreak disclosures (lunary, mlflow, h2o-3, PaddlePaddle, gradio,
ComfyUI-Manager, Qdrant, lollms, aim, superagi, litellm, PyTorch, and six guardrail-jailbreak
disclosures). 0 false positives in the sample.

| id | tag | affected | title |
|---|---|---|---|
| AVID-2026-R0003 | cve | lunary-ai/lunary | Improper Privilege Management in lunary-ai/lunary (CVE-2024-10273) |
| AVID-2026-R0009 | cve | eosphoros-ai/db-gpt | Denial of Service (DoS) via Multipart Boundary in eosphoros-ai/db-gpt  |
| AVID-2026-R0095 | prompt-injection | Meta LLaMa 3.3, Mistral Mistra | Multiple Model Guardrail Jailbreak via "Servile Scientist" Tactic |
| AVID-2026-R0104 | prompt-injection | OpenAI GPT-4o | OpenAI GPT-4o Guardrail Jailbreak via "Zero-Width Unicode" Tactic |
| AVID-2026-R0106 | prompt-injection | Google Gemini 2.0 Flash, OpenA | Multiple Model Guardrail Jailbreak via "Fictional API Detection" Tacti |
| AVID-2026-R0107 | prompt-injection | DALL-E3 | NSFWOpenAI DALL-E3 Guardrail Jailbreak via "Surprise Attack" Tactic |
| AVID-2026-R0110 | prompt-injection | Alibaba Qwen Turbo, Google Gem | Multiple Model Guardrail Jailbreak via "Apocalyptic Scenario" Tactic |
| AVID-2026-R0114 | prompt-injection | Alibaba Qwen Plus, Alibaba Qwe | Multiple Model Guardrail Jailbreak via "Chaotic Formatting" Tactic |
| AVID-2026-R0419 | third-party-report | Kiro IDE | Amazon Kiro IDE Data Exfiltration via Steering File |
| AVID-2026-R1182 | cve | mlflow/mlflow | Relative Path Traversal in mlflow/mlflow (CVE-2023-2356) |
| AVID-2026-R1295 | avid | mintplex-labs/anything-llm | Authentication Bypass by Primary Weakness in mintplex-labs/anything-ll |
| AVID-2026-R1296 | cve | mintplex-labs/anything-llm | SQL Injection in mintplex-labs/anything-llm (CVE-2023-4899) |
| AVID-2026-R1307 | cve | PaddlePaddle | Stack overflow in paddle.searchsorted (CVE-2023-52304) |
| AVID-2026-R1310 | cve | PaddlePaddle | Stack overflow in paddle.linalg.lu_unpack (CVE-2023-52307) |
| AVID-2026-R1359 | command-injection | paddlepaddle/paddle | Command injection in paddle.utils.download._wget_download (bypass filt |
| AVID-2026-R1382 | cve | haotian-liu/llava | Server-Side Request Forgery in haotian-liu/llava (CVE-2024-12068) |
| AVID-2026-R1402 | cve | lunary-ai/lunary | Session Reuse Vulnerability in lunary-ai/lunary (CVE-2024-1902) |
| AVID-2026-R1414 | cve | parisneo/lollms-webui | Path Traversal Vulnerability in parisneo/lollms-webui (CVE-2024-2178) |
| AVID-2026-R1548 | cve | gradio | Insecure communication between the FRP client and server in Gradio (CV |
| AVID-2026-R1586 | cve | aimhubio/aim | Arbitrary File Overwrite and Data Exfiltration in aimhubio/aim (CVE-20 |
| AVID-2026-R1606 | cve | danswer-ai/danswer | Arbitrary File Overwrite in danswer-ai/danswer (CVE-2024-7957) |
| AVID-2026-R1610 | cve | h2oai/h2o-3 | Denial of Service in h2oai/h2o-3 (CVE-2024-8062) |
| AVID-2026-R1652 | cve | mlflow/mlflow | Weak Password Requirements in mlflow/mlflow (CVE-2025-1474) |
| AVID-2026-R1673 | cve | Applio | Applio allows unsafe deserialization in model_information.py (CVE-2025 |
| AVID-2026-R1688 | cve | LMDeploy | InternLM LMDeploy conf.py open code injection (CVE-2025-3163) |

## 5. cvelistV5 (`ingest/wave12_cvelistv5.json`, 2,502 rows)

Channel: release `cve_2026-10-03_1400Z`, asset `2026-10-03_all_CVEs_at_midnight.zip.zip` (619,121,588 bytes, sha256
`2fa5d5e25b35bf87f0eec4cee20c6f1f8c140f512002fd17ff1b4f6e631abd79`), streamed to `ingest/_cache/` by the new
`ingest.common.fetch_to_file` (robots-checked, rate-limited, UA, retry, `.part` rename).
HTTP only. Licence CVE-TOU, carried per row. CVE JSON 5 records scanned: 210,713 (ids 2022+),
159,153 published on or after 2024-01-01.

**Filter** (`scripts/ai_relevance.py`, shared with AVID; gate defect 6 rules in the next paragraph). Reuses the repo's own vocabularies
(`package_is_strongly_ai` / `STRONG_AI_PACKAGE_TOKENS`, `AI_PRODUCT_CPE_FRAGMENTS`,
`AI_CONTEXT_TOKENS` from `ingest_cve_nvd_expanded.py`) and changes how they are applied,
because applied to a full dump rather than to the results of an NVD keyword search they
break INCLUSION.md section 4: weak tokens (`agent`, `prompt`, `ai `, `ml `, `nemo`,
`claude`...) never decide alone and description tokens are word-bounded; product
fields (vendor, product, packageName, repo, collection URL, CPE, GitHub slug in a reference)
match as delimited segments; Red Hat container-image names (`rhoai/...-rhel9`) are not
evidence. **`data/ai_package_allowlist.json` (WS4-T4) does not exist**, and the
existing keyword/CPE lists miss real AI products, so a curated seed of 90 entries
(each one measured as a miss in this window; `ECOSYSTEM_SEED`) is added in the module, with the
candidate feeder (top weak-signal products that did NOT pass) committed in the
provenance file as `candidates_for_curation` for the WS4-T4 curation pass.

Description-only matches (no product evidence) are borderline AI-nexus cases, and INCLUSION.md section 6
says to require a second signal, so BOUNCE #1 rules were added (each a switch in `ai_relevance.RULES`,
each with a test that shows it firing; recall cost = records of the 5,128 window matches before the rules):
(i) bounded `gpt-N` model form (drops the four MitraStar GPT-xxxx routers; recall cost on real GPT-N text: 0
observed); (ii) no description-only matches on Linux-kernel-CNA records (cost 13); (iii) credit and trailer clauses
("found/reported by ...", `Assisted-by:`) stripped before matching (cost 3); (iv) the INCLUSION s6 second signal
(a second distinct AI phrase, an AI-specific vector phrase, a self-sufficient phrase such as `mcp server`, or the phrase
also being a segment of the vendor/product/repo name; a product's self-description does NOT count) (cost 427, 8.3%,
overlapping with the others; 428 combined drops of 5,128 -> 4,700). Rather than an exclusion list. About a third of
the 427 are AI-native products admitted only by their self-description (nanobot, WeKnora, TensorZero, llava, Lumiverse,
Firecrawl...); those were added to `ECOSYSTEM_SEED` by name, the rest (Trigger.dev, Hatchet, Warp, weDocs...) stay out,
which is the gate's ruling on that shape. All 19 FPs the gate named drop out and are test cases
(`tests/fixtures/wave12/cvelistv5/gate1_false_positives.json`); `ruby_llm` (3 CVEs) stays in. Description-only rows
fell from 384 to 206.

Yield, window and filter separately:

| | backlog 2024-01..2026-06 | post-2026-06 | total |
|---|---:|---:|---:|
| published, all CNAs | 121,318 | 37,835 | 158,262 |
| pass the AI-relevance filter | 3,231 | 1,475 | 4,706 |
| already in corpus | 2,095 | 44 | 2,139 |
| would fold into an existing entry (skipped) | 11 | 54 | 65 |
| **emitted** | **1,125** | **1,377** | **2,502** |

Against the evaluation: its backlog figure (>=416: EUVD route 293 + huntr route 228, sharing
105) was a lower bound from 26 query terms and a proxy regex; this filter finds
1,125 for the same window, the huntr slice alone
433 against 228. Two different filters, so the numbers are not
comparable beyond "the lower bound was low". The post-2026-06 catch-up (N2) is
1,377; the corpus's newest CVE month was 2026-07, so most of
it is genuinely new. 2,095 of 3,231 backlog matches
(64%) were already in the corpus.

huntr CNA (`@huntr_ai`, exact match; `Huntress` is a different CNA and an earlier regex
matched it): 788 records in window,
636 pass the same filter, 447 new
(backlog 433, post-window 14; the CNA's 2026 rate fell off, as the evaluation saw).
Tagged `huntr`; the bounty URL is kept as a `disclosure` reference; only the CVE record
text is taken.

REJECTED: 891 records in window, never emitted. **A REJECTED record
carries no description or affected-product data, so the AI filter cannot classify it**
(0 match). The sibling reconciliation task should key
rejection on the CVE ids already in the corpus, not on this filter.

Re-sample of the description-only stratum after the rules: 40 of the 206 description-only rows
(seed 7), read as "is the affected product AI/ML/agent software". **40 plausible, 0 clear false positives,
1 borderline** (an AI-SEO WordPress plugin). Named MCP servers, gradio, anything-llm, New API, Void, Agno, Banks,
ruby_llm and Splunk AI Toolkit dominate. The earlier overall sample (40 rows, 0 false positives, 5 borderline)
predates the rules and is superseded.

| cve | affected | description phrase |
|---|---|---|
| CVE-2024-13059 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-1727 | gradio-app/gradio-app/gradio | gradio |
| CVE-2024-1728 | gradio-app/gradio-app/gradio | gradio |
| CVE-2024-2206 | gradio-app/gradio-app/gradio | gradio |
| CVE-2024-2913 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-3110 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-3150 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-4084 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-4284 | mintplex-labs/mintplex-labs/anything-llm | llm |
| CVE-2024-4325 | gradio-app/gradio-app/gradio | gradio |
| CVE-2024-47867 | gradio-app/gradio | gradio |
| CVE-2024-47870 | gradio-app/gradio | gradio |
| CVE-2024-4940 | gradio-app/gradio-app/gradio | gradio |
| CVE-2025-5320 | gradio-app/gradio | gradio |
| CVE-2025-59146 | QuantumNous/new-api | artificial intelligence |
| CVE-2025-61260 |  | model context protocol |
| CVE-2026-101057 | universal-tool-calling-protocol/python-u | mcp server |
| CVE-2026-15583 | Grafana/Grafana MCP Server | mcp server |
| CVE-2026-18875 | IBM/Financial Transaction Manager (FTM)  | ai agent |
| CVE-2026-28416 | gradio-app/gradio | gradio |
| CVE-2026-37003 |  | llm |
| CVE-2026-44934 | SUSE/Rancher | ai agent |
| CVE-2026-47769 | Work90210/APIFold | mcp server |
| CVE-2026-50125 | StacklokLabs/mkp | model context protocol |
| CVE-2026-61536 | masci/banks | llm |
| CVE-2026-64859 | QuantumNous/new-api | artificial intelligence |
| CVE-2026-6494 | Red Hat/Red Hat Ansible Automation Platf | mcp server |
| CVE-2026-65698 | voideditor/void | ai agent |
| CVE-2026-67425 | flytohub/flyto-core | anthropic |
| CVE-2026-67987 |  | llm |
| CVE-2026-67991 |  | llm |
| CVE-2026-75845 | ArcadeData/arcadedb | mcp server |
| CVE-2026-75858 | Hmbown/CodeWhale | prompt injection |
| CVE-2026-76395 | Splunk/Splunk AI Toolkit | machine learning |
| CVE-2026-79746 | samanhappy/mcphub | mcp server |
| CVE-2026-81095 | timescale/pg-aiguide | mcp server |
| CVE-2026-84779 | Sheikh Heera/Agentimus – AI SEO, llms.tx | ai agent |
| CVE-2026-91988 | dep0we/atomic-agents-stack | mcp server |
| CVE-2026-94486 | vercel/next.js | model context protocol |
| CVE-2026-96525 | Unknown/MCP Server for WordPress | mcp server |

## 6. arXiv cs.CR (`ingest/wave12_arxiv.json`, 55 rows)

Channel: `oaipmh.arxiv.org` (no robots.txt there, 404 == no restriction), set `cs:cs:CR`,
`metadataPrefix=arXiv`, 3.0 s between requests passed explicitly (`common.py` has no
Crawl-delay parser), single connection. Metadata only (title, authors, id, dates,
categories); no full text, no e-print URL. **The abstract is used by the filter and then discarded: the
row's `description` is original, deterministic prose composed from facts (id, authors, month,
categories, the filter's own reasons), `description_provenance: original`** - the CC0 dedication is
arXiv's and nothing shows authors waived rights in abstract prose (licence rows, foreman note). `export.arxiv.org` is not touched.
Window: papers FIRST SUBMITTED (v1) 2025-10 .. 2026-10, dated by the month in the new-style id (the OAI
`created` field is the latest version's date: 2411.16769 is v1 2024-11 but `created` 2026-09, so
20 of 63 rows were mis-dated and 8 were outside the window; gate defect 1). 12,616
records harvested, 2,352 dropped as v1 before the window (the 8 named by the gate get no IDs).

**The yield is a curation decision, and the filter cannot reproduce the curated list.**
Filter: the title carries the attack (unambiguous GenAI-attack term, or an attack term plus a
GenAI target term), the abstract names a GenAI target, and the abstract carries a concrete
real-world claim (disclosure/CVE/in the wild/production or commercial system/RCE/end-to-end
or proof-of-concept), with defense/benchmark/survey/evaluation titles excluded. Operating
points, measured (12-month yield; recall = share of the 115 hand-curated rows'
own records that pass):

| variant | 12-month yield | curated recall |
|---|---:|---:|
| headline + target | 1,011 | 71/115 = 61% |
| + title exclusions (defense, benchmark, survey, ...) | 563 | 60/115 = 52% |
| + a named commercial or production system | 156 | 32/115 = 27% |
| **+ concrete real-world claim (shipped)** | 55 | 6/115 = 5% |

Shipped = the last row, because the brief's target was about 60-100 a year and a filter
that reaches it can only be that strict. The cost is stated plainly: **the hand-curated
`arxiv_incidents.json` is mostly influential method papers (GCG, AutoDAN, PAIR, TAP,
PoisonedRAG...), and a deterministic abstract rule recovers 6 of 115 of them.** The
two sets are different populations: this filter selects attack papers that claim a real-world
or deployed target, not the famous ones. If the maintainer wants the curated rate AND the
curated taste, that needs a committed approval list (as WS4-T4 does for CVEs), not a
sharper regex. Dedupe against the 123 curated rows: by arXiv id in source ids and reference
URLs (0 collisions) and by the merger's URL/title keys
(0). No human approved these 55 (user ruling D43: deterministic selection only, no approved list): every row ships `quality_tier: auto` (enum curated/reviewed/auto), hence `confidence: low` and `tier: feed`. Before this fix they were silently classed `reviewed` because the merger's ARXIV- prefix rule treats the id as a research catalogue; `normalize_entry` now honours an explicit `auto` from a source (never curated/reviewed).

Spot-read: 30 of 55, seeded random (seed 2026). Read as "is this an attack
paper whose target is a GenAI/agentic system": **28 yes, 2 borderline, 0 no.** (Rows are now original text; the read is of title and abstract.)
"Concrete" in the filter is a statement the abstract makes, not something this check verified.

| arXiv id | title | headline / concrete phrase | read |
|---|---|---|---|
| 2510.01342 | Fine-Tuning Jailbreaks under Highly Constrained Black-Box Settings: A Three-Pronged Approach | jailbreaks / real-world deployment | TP |
| 2510.17904 | BreakFun: Jailbreaking LLMs via Object Instantiation under Simulated Code Execution | jailbreaking / commercial models | TP |
| 2510.21190 | The Trojan Example: Jailbreaking LLMs through Template Filling and Unsafety Reasoning | jailbreaking / commercial systems | TP |
| 2510.22963 | When Compression Becomes an Attack Surface: Black-Box Attacks on Prompt-Compressed LLM Agents | attack / real-world agent | TP |
| 2511.07876 | LoopLLM: Transferable Energy-Latency Attacks in LLMs via Repetitive Generation | attacks / commercial llms | TP |
| 2601.09625 | The Promptware Kill Chain: How Prompt Injections Gradually Evolved Into a Multistep Malware Del | prompt injections / production llm | TP |
| 2601.12460 | TrojanPraise: Jailbreak LLMs via Benign Fine-Tuning | jailbreak / commercial llms | TP |
| 2602.19450 | Red-Teaming Claude Opus and ChatGPT-based Security Advisors for Trusted Execution Environments | red-teaming / deployed llm | borderline |
| 2603.09246 | Reasoning-Oriented Programming: Chaining Semantic Gadgets to Jailbreak Large Vision Language Mo | jailbreak / commercial models | TP |
| 2603.13420 | Accelerating Suffix Jailbreak attacks with Prefix-Shared KV-cache | jailbreak / deployed llms | borderline |
| 2604.12232 | TEMPLATEFUZZ: Fine-Grained Chat Template Fuzzing for Jailbreaking and Red Teaming LLMs | jailbreaking / commercial llms | TP |
| 2604.21829 | Black-Box Skill Stealing Attack from Proprietary LLM Agents: An Empirical Study | stealing / commercial agent | TP |
| 2604.23711 | Spore: Efficient and Training-Free Privacy Extraction Attack on LLMs via Inference-Time Hybrid  | privacy extraction / real-world deployments | TP |
| 2605.11229 | Comment and Control: Hijacking Agentic Workflows via Context-Grounded Evolution | hijacking / responsibly disclos | TP |
| 2605.14460 | Exploiting LLM Agent Supply Chains via Payload-less Skills | exploiting / remote code execution | TP |
| 2605.30667 | Automatically Attacking Software Reverse Engineering AI Agents | attacking / proof-of-concept | TP |
| 2606.06244 | Steering LLM Viewpoints through Fabricated Evidence Injection | injection / commercial llms | TP |
| 2606.10742 | MemVenom: Triggered Poisoning of Multimodal Memories in Web Agents | poisoning / end-to-end attack | TP |
| 2606.15788 | GAS-Leak-LLM: Genetic Algorithm-Based Suffix Optimization for Black-Box LLM Jailbreaking | jailbreaking / commercial systems | TP |
| 2606.21077 | OTTER: A Red-Teaming System for Toxicity-Evading Jailbreak Prompt Optimization | jailbreak / production llms | TP |
| 2607.00481 | Beyond the Prompt: Jailbreaking Function-Calling LLMs via Simulated Moderation Traces | jailbreaking / commercial llms | TP |
| 2607.02961 | Overloading Large Vision-Language Models for Jailbreaking | jailbreaking / real-world applications | TP |
| 2607.15657 | Do Agents Dream of False Memories? Black-box Visual Attacks on Long-term Memory in Multimodal A | attacks / deployed systems | TP |
| 2607.19267 | They'll Verify. They Just Won't Act. How Authority Framing and Laundered Code Turn a Trusted Ag | attack / production llms | TP |
| 2607.23444 | Isolated but Exposed: Persistence-Based Memory Extraction Attack on LLM Agents | attack / production systems | TP |
| 2607.25936 | From Role Prompt to Infinite Thinking: Exploiting Persona Conditioning for Inference Cost Attac | exploiting / real-world applications | TP |
| 2608.23471 | InjecMEM: Memory Injection Attack on LLM Agent Memory Systems | memory injection / deployed llm | TP |
| 2609.04533 | Repeat-After-Me: Black-Box Adaptive Visual Prompt Injection | prompt injection / remote code execution | TP |
| 2609.09553 | Arbitrary Cipher Attacks Against Large Language Models Do Not Require Fine-Tuning | attacks / commercial models | TP |
| 2609.39902 | CodeMimicry: Exploiting Safety Generalization Lag in Large Language Models via Structured Code  | exploiting / commercial llms | TP |

## 7. OpenSSF Malicious Packages (MAL-, Apache-2.0) removed from the OSV path

OSV aggregates OpenSSF Malicious Packages records, which are Apache-2.0, not OSV's CC BY 4.0
(board note N6). Changes:
- `scripts/ingest_cve_nvd_expanded.py::is_openssf_malicious(v)` (id or alias `MAL-`, or an
  `ossf/malicious-packages` source marker) is applied in `fetch_osv` and in `osv_to_record`, so the
  OSV path never admits such a record. Row-level twin: `is_openssf_malicious_row`. Tests with
  recorded fixtures (`tests/fixtures/wave12/osv/`): the MAL fixture is excluded, an ordinary GHSA
  record passes, and with the predicate neutered the MAL text is converted (the test fails
  without the filter).
- The committed `ingest/cve_nvd_expanded.json` held 2 MAL rows. `scripts/audit/purge_openssf_mal.py`
  applies the same predicate (no hand edit; second run is a no-op). MAL-2026-2144 (litellm) is
  dropped; it was not cited by any corpus entry. **MAL-2026-3607 is kept as a bare identifier**:
  id, title label, affected package, tags and reference links, with the description replaced by an
  original sentence and the Apache text gone. The reason is structural, not sentimental: the corpus
  entry INC-08450 is held together by that row (its links bridge a nestjs-auth CVE and a mistralai
  GHSA, so it is already an over-merge), and dropping the row entirely makes the merger split
  INC-08450, which the WS4-T19 guard refuses without a user ruling (reproduced). Facts and links
  are not Apache-protected text; INC-08450's own title and description come from GHSA/CVE and do not
  change. Delta of this step on existing entries: none (no field, tag or `updated` moves).
- `data/incidents.json` is otherwise unaffected; `docs/SOURCE_LICENSES.md` row 2.4 should name
  `is_openssf_malicious` as the exclusion.

## 8. Notes for the licence rows

- No `git clone` anywhere: AVID is the GitHub tarball API, cvelistV5 the release asset, arXiv
  OAI-PMH, all through `ingest/common.py` (`fetch_once` / `fetch_to_file`). The pending
  non-HTTP-egress register entry is "not used".
- `AVID-2023-V025` is in the corpus (static `avid_owasp_incidents.json`) and no longer upstream.
  Nothing in this ingest or the build deletes it; it is listed in
  `wave12_avid.provenance.json` (`corpus_avid_ids_absent_from_repo`). Marking it with a status
  needs the WS4-T2 reconciliation mechanism (`status` + conflicts), which is the sibling task, not
  an ingest side effect. OAI-PMH deletion headers are parsed (`deleted: true`), counted, and only ever
  skip a candidate row; no corpus entry is touched.

## 9. Reproduce

```
git checkout ws4/wave12-ingest
# no network from here on: the committed ingest/*.json and data/ are the only inputs
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py   # make merge
python scripts/render_markdown.py && python scripts/render_docs_stats.py && python scripts/validate.py
python scripts/check_stats_drift.py
python scripts/audit/wave12_delta.py --before 9604752f:data/incidents.json --after data/incidents.json --self-test
pytest tests -q
# refresh the ingests (network, rate-limited, through ingest/common.py):
make ingest-avid && make ingest-cvelistv5 && make ingest-arxiv      # in that order
```

`make` is not installed on the machine this was run on; the recipes were run as the
commands above, which is what the Makefile targets expand to.
