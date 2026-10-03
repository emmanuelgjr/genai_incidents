# Wave 1 + wave 2 ingest: field-level delta (2026-10-03)

Branch `ws4/wave12-ingest`, code commit `f9ce8d06` (the data commit follows it).
Machine-readable twin: `wave12-ingest-delta-2026-10-03.json`. Produced by
`scripts/audit/wave12_delta.py` from the corpus at `9604752f` (before) and the
rebuilt corpus (after). Working agreement 2: unintended deltas are defects.
**Dated record, do not regenerate** (working agreement 4): a later refresh gets its own delta.

## 1. Result

| | before | after | delta |
|---|---:|---:|---:|
| `incident_count` | 13,361 | 15,872 | **+2,511** |
| corpus `security` | 12,816 | 15,327 | +2,511 |
| corpus `ai-harm` | 545 | 545 | +0 |
| category `vulnerability-disclosure` | 5,784 | 8,232 | +2,448 |
| all other categories | 7,577 | 7,640 | +63 |

Invariant 1 (never headline incidents + vulnerabilities + capabilities as one
number): `incident_count` above is the project's own stat; the
vulnerability / other split is shown beside it, and no combined headline is
introduced. Invariant 6 (docs counts from `stats.json`): `render_docs_stats.py`
re-templated README, DATASHEET and `docs/index.html` from `data/stats.json`;
`check_stats_drift.py` is clean (5 surfaces). Both are marked active in the
brief; this task did not re-verify the plan's Active-from table.

**New entries: 2,511. Changes to existing entries: 0.**
No ID removed, new IDs are a contiguous append above INC-14910
(INC-14911 .. INC-17421), no existing ID changed meaning.

New entries by origin (an entry holds every source that reached it; AVID and
cvelistV5 rows for the same CVE fold into one entry, so the sum of rows
emitted (280 + 2,705 + 63) exceeds the entry count):

| origin | new entries | of which vulnerability-disclosure |
|---|---:|---:|
| cvelistv5 | 2,240 | 2,240 |
| avid + cvelistv5 | 105 | 105 |
| avid | 103 | 103 |
| arxiv | 63 | 0 |

New vulnerability entries by publication month: backlog window (to 2026-06) 927;
post-2026-06 1,521.

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
| AVID | 519 (crosswalk AVID id -> CVE -> INC id in `wave12_avid.provenance.json`) | 7 |
| cvelistV5 | 2,324 | 67 (listed with INC id) |
| arXiv | 0 | 0 |

A future enrichment mechanism (extra source ids / cross-references on existing
entries, plus a schema home for AVID's SEP taxonomy, which `normalize_entry`
drops today) is the place to use that crosswalk; it needs a decision, not a
side effect of an ingest.

### ID set (invariants 3 and 9)

- new IDs: **2,511** (INC-14911 .. INC-17421)
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

## 4. AVID (`ingest/wave12_avid.json`, 280 rows)

Channel: `api.github.com/repos/avidml/avid-db/tarball/main` (2 MB) through
`fetch_once`; no `git clone`, so nothing to register in `INGESTION_CONDUCT.md`.
Repo commit `8eda5f4`, tarball sha256 `c0d5f5e6c96170c1db7280ed0d6b5facbda472f54463682907df829e57bc80ce`. Licence MIT, carried per row in
`content_license` (+ `description_source: avid`, `description_provenance: verbatim`).

Repo records read: 1,785 (drafts under `reports/review/` never read).
By class: {"LLM Evaluation": 556, "(none)": 1, "CVE Entry": 1098, "Third-party Report": 96, "AIID Incident": 18, "ATLAS Case Study": 16}.

| | rows |
|---|---:|
| `LLM Evaluation`, not emitted | 556 |
| already in corpus by AVID id | 87 |
| CVE reports failing the AI-relevance filter | 336 |
| CVE already in corpus (crosswalked) | 519 |
| would fold into an existing entry | 7 |
| **emitted** | **280** (193 CVE-keyed, 87 third-party reports) |

Corrections to the evaluation (section 4, AVID row), re-measured here:
- **The 556 `LLM Evaluation` reports are automated garak per-(model, probe) scan
  results** ("The model X was evaluated by the Garak LLM Vulnerability scanner
  using the probe Y"), the "AVID-native" share the n=40 sample saw. INCLUSION.md
  section 3 excludes benchmark runs, so none is emitted (`--include-evaluations`
  opts in). Net-new is therefore 280, not ~1,070.
- **213 of the 309 rows first built carried a machine-written "Reason for inclusion
  in AVID:" paragraph appended to the CNA text** (it argues, for instance, that
  Spring4Shell qualifies because Spring may sit in a serving stack). It is not
  part of the CVE record and it satisfied the AI-relevance test on its own
  ("...an AI model..."). It is stripped from `description`, and relevance is judged on
  the CNA text and affected product only. This is why 336 CVE reports
  are filtered out (flask-restx, Bot Framework SDK, Log4j, CUDA toolkit, Jenkins plugins,
  Apache Airflow...), listed in the provenance file for review.
- The repo yields 1,785 published records (1,794 JSON files including 9 drafts under
  `reports/review`); the evaluation's tree count was 1,790. 87 non-evaluation
  records are already in the corpus by AVID id; `AVID-2023-V025` is absent from the repo
  (as the evaluation found).
- Third-party report prose is cut to its first sentence(s) (not AVID's to license,
  evaluation 1B.5 caveat iii); CVE-class text is the CNA text (CVE ToU).

Spot-read, 25 of 280 seeded random (seed 2026): all 25 are AI/ML software
or model-vendor jailbreak disclosures (lunary, mlflow, h2o-3, PaddlePaddle, gradio,
ComfyUI-Manager, Qdrant, lollms, aim, superagi, litellm, PyTorch, and six guardrail-jailbreak
disclosures). 0 false positives in the sample.

| id | tag | affected | title |
|---|---|---|---|
| AVID-2026-R0003 | cve | lunary-ai/lunary | Improper Privilege Management in lunary-ai/lunary (CVE-2024-10273) |
| AVID-2026-R0032 | avid | lunary-ai/lunary | Improper Access Control in lunary-ai/lunary (CVE-2024-8999) |
| AVID-2026-R0093 | prompt-injection | DeepSeek DeepSeek R1, DeepSeek | Multiple Model Guardrail Jailbreak via "Scientific Framing for Wrapper |
| AVID-2026-R0095 | prompt-injection | Meta LLaMa 3.3, Mistral Mistra | Multiple Model Guardrail Jailbreak via "Servile Scientist" Tactic |
| AVID-2026-R0104 | prompt-injection | OpenAI GPT-4o | OpenAI GPT-4o Guardrail Jailbreak via "Zero-Width Unicode" Tactic |
| AVID-2026-R0106 | prompt-injection | Google Gemini 2.0 Flash, OpenA | Multiple Model Guardrail Jailbreak via "Fictional API Detection" Tacti |
| AVID-2026-R0110 | prompt-injection | Alibaba Qwen Turbo, Google Gem | Multiple Model Guardrail Jailbreak via "Apocalyptic Scenario" Tactic |
| AVID-2026-R0114 | prompt-injection | Alibaba Qwen Plus, Alibaba Qwe | Multiple Model Guardrail Jailbreak via "Chaotic Formatting" Tactic |
| AVID-2026-R1258 | cve | mlflow/mlflow | Absolute Path Traversal in mlflow/mlflow (CVE-2023-3765) |
| AVID-2026-R1265 | cve | PaddlePaddle | FPE in paddle.linalg.eig (CVE-2023-38677) |
| AVID-2026-R1304 | cve | gradio | Make the `/file` secure against file traversal attacks (CVE-2023-51449 |
| AVID-2026-R1310 | cve | PaddlePaddle | Stack overflow in paddle.linalg.lu_unpack (CVE-2023-52307) |
| AVID-2026-R1335 | command-injection | mlflow/mlflow | Command Injection (CVE-2023-6940) |
| AVID-2026-R1370 | cve | h2oai/h2o-3 | Jdbc Deserialization in h2oai/h2o-3 (CVE-2024-10553) |
| AVID-2026-R1373 | cve | gradio-app/gradio | Path Traversal in gradio-app/gradio (CVE-2024-10648) |
| AVID-2026-R1409 | cve | ComfyUI-Manager | The issue stems from a missing validation of the pip field in a POST r |
| AVID-2026-R1430 | cve | parisneo/lollms-webui | Path Traversal leading to Remote Code Execution in parisneo/lollms-web |
| AVID-2026-R1458 | cve | Qdrant | Qdrant Full Snapshot REST API snapshots.rs path traversal (CVE-2024-30 |
| AVID-2026-R1526 | cve | parisneo/lollms-webui | Remote Code Execution due to LFI in '/install_extension' in parisneo/l |
| AVID-2026-R1547 | cve | gradio | Lack of integrity check on the downloaded FRP client in Gradio (CVE-20 |
| AVID-2026-R1587 | cve | aimhubio/aim | Arbitrary File/Directory Deletion in aimhubio/aim (CVE-2024-6483) |
| AVID-2026-R1602 | cve | aimhubio/aim | CSRF in aimhubio/aim (CVE-2024-7760) |
| AVID-2026-R1635 | cve | transformeroptimus/superagi | Improper Privilege Management in transformeroptimus/superagi (CVE-2024 |
| AVID-2026-R1644 | cve | berriai/litellm | Exposure of Sensitive Information in berriai/litellm (CVE-2025-0330) |
| AVID-2026-R1656 | cve | PyTorch | PyTorch Tuple torch.ops.profiler._call_end_callbacks_on_jit_fut memory |

## 5. cvelistV5 (`ingest/wave12_cvelistv5.json`, 2,705 rows)

Channel: release `cve_2026-10-03_1400Z`, asset `2026-10-03_all_CVEs_at_midnight.zip.zip` (619,121,588 bytes, sha256
`2fa5d5e25b35bf87f0eec4cee20c6f1f8c140f512002fd17ff1b4f6e631abd79`), streamed to `ingest/_cache/` by the new
`ingest.common.fetch_to_file` (robots-checked, rate-limited, UA, retry, `.part` rename).
HTTP only. Licence CVE-TOU, carried per row. CVE JSON 5 records scanned: 210,713 (ids 2022+),
159,153 published on or after 2024-01-01.

**Filter** (`scripts/ai_relevance.py`, shared with AVID). Reuses the repo's own vocabularies
(`package_is_strongly_ai` / `STRONG_AI_PACKAGE_TOKENS`, `AI_PRODUCT_CPE_FRAGMENTS`,
`AI_CONTEXT_TOKENS` from `ingest_cve_nvd_expanded.py`) and changes how they are applied,
because applied to a full dump rather than to the results of an NVD keyword search they
break INCLUSION.md section 4: weak tokens (`agent`, `prompt`, `ai `, `ml `, `nemo`,
`claude`...) never decide alone and description tokens are word-bounded; product
fields (vendor, product, packageName, repo, collection URL, CPE, GitHub slug in a reference)
match as delimited segments; Red Hat container-image names (`rhoai/...-rhel9`) are not
evidence. **`data/ai_package_allowlist.json` (WS4-T4) does not exist**, and the
existing keyword/CPE lists miss real AI products, so a curated seed of 78 entries
(each one measured as a miss in this window; `ECOSYSTEM_SEED`) is added in the module, with the
candidate feeder (top weak-signal products that did NOT pass) committed in the
provenance file as `candidates_for_curation` for the WS4-T4 curation pass.

Yield, window and filter separately:

| | backlog 2024-01..2026-06 | post-2026-06 | total |
|---|---:|---:|---:|
| published, all CNAs | 121,318 | 37,835 | 158,262 |
| pass the AI-relevance filter | 3,468 | 1,628 | 5,096 |
| already in corpus | 2,276 | 48 | 2,324 |
| would fold into an existing entry (skipped) | 11 | 56 | 67 |
| **emitted** | **1,181** | **1,524** | **2,705** |

Against the evaluation: its backlog figure (>=416: EUVD route 293 + huntr route 228, sharing
105) was a lower bound from 26 query terms and a proxy regex; this filter finds
1,181 for the same window, the huntr slice alone
427 against 228. Two different filters, so the numbers are not
comparable beyond "the lower bound was low". The post-2026-06 catch-up (N2) is
1,524; the corpus's newest CVE month was 2026-07, so most of
it is genuinely new. 2,276 of 3,468 backlog matches
(65%) were already in the corpus.

huntr CNA (`@huntr_ai`, exact match; `Huntress` is a different CNA and an earlier regex
matched it): 788 records in window,
632 pass the same filter, 441 new
(backlog 427, post-window 14; the CNA's 2026 rate fell off, as the evaluation saw).
Tagged `huntr`; the bounty URL is kept as a `disclosure` reference; only the CVE record
text is taken.

REJECTED: 891 records in window, never emitted. **A REJECTED record
carries no description or affected-product data, so the AI filter cannot classify it**
(0 match). The sibling reconciliation task should key
rejection on the CVE ids already in the corpus, not on this filter.

Spot-read: 40 of 2,705 emitted rows, seeded random (seed 2026), judged by
whether the affected product is AI/ML/agent software (INCLUSION s1 gate 1).
**35 clear, 5 borderline, 0 false positive.** Borderline = AI-adjacent product with
a generic bug (n8n twice, a WordPress AI-chatbot plugin, Crawl4AI, Trigger.dev). Zero
false positives in 40 bounds the false-positive rate at about 7% (95% upper); earlier
pre-fix samples had found 3 of 45 description-only matches wrong (`claude` in patch
credits, a vendor-boilerplate "artificial intelligence"), which is what the `claude`
rule and the image-name rule now address. One known weak point: the bare `mcp` product
segment also matches unrelated products named "MCP ..."; none surfaced in the sample.

| cve | affected | evidence (product / description) | read |
|---|---|---|---|
| CVE-2023-52306 | PaddlePaddle | PaddlePaddle / - | TP |
| CVE-2024-10131 | infiniflow/infiniflow/ragflow | infiniflow/ragflow / llm | TP |
| CVE-2024-5133 | lunary-ai/lunary-ai/lunary | lunary-ai / - | TP |
| CVE-2024-5386 | lunary-ai/lunary-ai/lunary | lunary-ai / - | TP |
| CVE-2024-6669 | quantumcloud/WPBot – AI ChatBot for Live | - / ai chatbot | borderline |
| CVE-2024-7962 | gaizhenbiao/gaizhenbiao/chuanhuchatgpt | gaizhenbiao/chuanhuchatgpt / - | TP |
| CVE-2024-8251 | mintplex-labs/mintplex-labs/anything-llm | - / llm | TP |
| CVE-2024-9159 | gaizhenbiao/gaizhenbiao/chuanhuchatgpt | gaizhenbiao/chuanhuchatgpt / - | TP |
| CVE-2025-0739 | EmbedAI | EmbedAI / - | TP |
| CVE-2026-100585 | OpenClaw | OpenClaw / openclaw | TP |
| CVE-2026-101884 | OpenClaw/OpenClaw Windows Node | OpenClaw / openclaw | TP |
| CVE-2026-1114 | parisneo/parisneo/lollms | parisneo/lollms / - | TP |
| CVE-2026-13445 | IBM/Langflow OSS | Langflow OSS / langflow | TP |
| CVE-2026-18954 | AWS/documentdb-mcp-server | documentdb-mcp-server / mcp server | TP |
| CVE-2026-24165 | NVIDIA/BioNeMo Framework | BioNeMo Framework / - | TP |
| CVE-2026-24231 | NVIDIA/NemoClaw | NemoClaw / - | TP |
| CVE-2026-34753 | vllm-project/vllm | vllm-project / vllm | TP |
| CVE-2026-39424 | 1Panel-dev/MaxKB | MaxKB / ai assistant | TP |
| CVE-2026-43900 | ThinkInAIXYZ/deepchat | - / artificial intelligence | TP |
| CVE-2026-4964 | letta-ai/letta | letta-ai / - | TP |
| CVE-2026-54233 | vllm-project/vllm | vllm-project / vllm | TP |
| CVE-2026-56263 | Crawl4AI | Crawl4AI / - | borderline |
| CVE-2026-59259 | n8n | n8n / n8n | borderline |
| CVE-2026-61426 | MervinPraison/PraisonAI | PraisonAI / - | TP |
| CVE-2026-65975 | pydantic/pydantic-ai, pydantic/pydantic- | pydantic-ai / generative ai | TP |
| CVE-2026-66004 | ahujasid/blender-mcp | blender-mcp / prompt injection | TP |
| CVE-2026-69252 | FlowiseAI/Flowise | Flowise / flowise | TP |
| CVE-2026-70488 | open-webui | open-webui / open webui | TP |
| CVE-2026-70636 | FlowiseAI/Flowise | Flowise / flowise | TP |
| CVE-2026-73656 | triggerdotdev/trigger.dev | - / ai agents | borderline |
| CVE-2026-76059 | IBM/Langflow OSS | Langflow OSS / langflow | TP |
| CVE-2026-77083 | n8n-io/n8n | n8n-io / n8n | borderline |
| CVE-2026-7712 | MindsDB | MindsDB / - | TP |
| CVE-2026-78379 | Amazon/strands-agents-tools | - / llm | TP |
| CVE-2026-81102 | dropbox/mcp-server-dash | mcp-server-dash / mcp server | TP |
| CVE-2026-84452 | microsoft/winml-cli | - / ai models | TP |
| CVE-2026-85695 | lm-sys/FastChat | FastChat / - | TP |
| CVE-2026-86317 | ggml-org/llama.cpp | llama.cpp / llama | TP |
| CVE-2026-91836 | OpenClaw/ClawScan | OpenClaw / openclaw | TP |
| CVE-2026-93355 | BerriAI/litellm | litellm / litellm | TP |

## 6. arXiv cs.CR (`ingest/wave12_arxiv.json`, 63 rows)

Channel: `oaipmh.arxiv.org` (no robots.txt there, 404 == no restriction), set `cs:cs:CR`,
`metadataPrefix=arXiv`, 3.0 s between requests passed explicitly (`common.py` has no
Crawl-delay parser), single connection. Metadata only (title, authors, id, abstract,
categories; CC0); no full text, no e-print URL. `export.arxiv.org` is not touched.
Window: papers created 2025-10-03 .. 2026-10-03 (the last 12 months); 12,551
records harvested, 617 created before the window (re-datestamped).

**The yield is a curation decision, and the filter cannot reproduce the curated list.**
Filter: the title carries the attack (unambiguous GenAI-attack term, or an attack term plus a
GenAI target term), the abstract names a GenAI target, and the abstract carries a concrete
real-world claim (disclosure/CVE/in the wild/production or commercial system/RCE/end-to-end
or proof-of-concept), with defense/benchmark/survey/evaluation titles excluded. Operating
points, measured (12-month yield; recall = share of the 115 hand-curated rows'
own records that pass):

| variant | 12-month yield | curated recall |
|---|---:|---:|
| headline + target | 1,182 | 71/115 = 61% |
| + title exclusions (defense, benchmark, survey, ...) | 665 | 60/115 = 52% |
| + a named commercial or production system | 186 | 32/115 = 27% |
| **+ concrete real-world claim (shipped)** | 63 | 6/115 = 5% |

Shipped = the last row, because the brief's target was about 60-100 a year and a filter
that reaches it can only be that strict. The cost is stated plainly: **the hand-curated
`arxiv_incidents.json` is mostly influential method papers (GCG, AutoDAN, PAIR, TAP,
PoisonedRAG...), and a deterministic abstract rule recovers 6 of 115 of them.** The
two sets are different populations: this filter selects attack papers that claim a real-world
or deployed target, not the famous ones. If the maintainer wants the curated rate AND the
curated taste, that needs a committed approval list (as WS4-T4 does for CVEs), not a
sharper regex. Dedupe against the 123 curated rows: by arXiv id in source ids and reference
URLs (0 collisions) and by the merger's URL/title keys
(0). No human approved these 63.

Spot-read: 30 of 63, seeded random (seed 2026). Read as "is this an attack
paper whose target is a GenAI/agentic system": **28 yes, 2 borderline, 0 no.**
"Concrete" in the filter is a statement the abstract makes, not something this check verified.

| arXiv id | title | headline / concrete phrase | read |
|---|---|---|---|
| 2411.16769 | Red-Teaming Text-to-Image Models via In-Context Experience Replay and Semantic-Preserving Promp | red-teaming / commercial systems | TP |
| 2508.20863 | Misleading Large Language Models used (or misused) in Scientific Peer-Reviewing via Hidden Prom | prompt-injection / commercial llm | TP |
| 2508.21669 | Cybersecurity AI: Hacking the AI Hackers via Prompt Injection | prompt injection / proof-of-concept | TP |
| 2509.05755 | Red-Teaming Coding Agents from a Tool-Invocation Perspective: An Empirical Security Assessment | red-teaming / remote code execution | TP |
| 2510.21190 | The Trojan Example: Jailbreaking LLMs through Template Filling and Unsafety Reasoning | jailbreaking / commercial systems | TP |
| 2510.22963 | When Compression Becomes an Attack Surface: Black-Box Attacks on Prompt-Compressed LLM Agents | attack / real-world agent | TP |
| 2511.07876 | LoopLLM: Transferable Energy-Latency Attacks in LLMs via Repetitive Generation | attacks / commercial llms | TP |
| 2511.16709 | AutoBackdoor: Automating Backdoor Attacks via LLM Agents | backdoor / commercial models | TP |
| 2602.19450 | Red-Teaming Claude Opus and ChatGPT-based Security Advisors for Trusted Execution Environments | red-teaming / deployed llm | borderline |
| 2603.09246 | Reasoning-Oriented Programming: Chaining Semantic Gadgets to Jailbreak Large Vision Language Mo | jailbreak / commercial models | TP |
| 2603.27522 | Hidden Ads: Behavior Triggered Semantic Backdoors for Advertisement Injection in Vision Languag | backdoors / real-world deployment | TP |
| 2603.28013 | Kill-Chain Canaries: Stage-Level Tracking of Prompt Injection Across Attack Surfaces and Five P | prompt injection / production llms | TP |
| 2604.15368 | LogJack: Indirect Prompt Injection Through Cloud Logs Against LLM Debugging Agents | prompt injection / remote code execution | TP |
| 2604.21829 | Black-Box Skill Stealing Attack from Proprietary LLM Agents: An Empirical Study | stealing / commercial agent | TP |
| 2604.23711 | Spore: Efficient and Training-Free Privacy Extraction Attack on LLMs via Inference-Time Hybrid  | privacy extraction / real-world deployments | TP |
| 2604.28157 | FlashRT: Towards Computationally and Memory Efficient Red-Teaming for Prompt Injection and Know | prompt injection / real-world applications | borderline |
| 2605.11229 | Comment and Control: Hijacking Agentic Workflows via Context-Grounded Evolution | hijacking / responsibly disclos | TP |
| 2605.17971 | Babel: Jailbreaking Safety Attention via Obfuscation Distribution Optimized Sampling | jailbreaking / commercial models | TP |
| 2605.18133 | An Empirical Study of Privacy Leakage Chains via Prompt Injection in Black-Box Chatbot Environm | prompt injection / proof-of-concept | TP |
| 2606.06244 | Steering LLM Viewpoints through Fabricated Evidence Injection | injection / commercial llms | TP |
| 2606.15788 | GAS-Leak-LLM: Genetic Algorithm-Based Suffix Optimization for Black-Box LLM Jailbreaking | jailbreaking / commercial systems | TP |
| 2606.21077 | OTTER: A Red-Teaming System for Toxicity-Evading Jailbreak Prompt Optimization | jailbreak / production llms | TP |
| 2607.05120 | Agent Data Injection Attacks are Realistic Threats to AI Agents | injection attacks / real-world agents | TP |
| 2607.15657 | Do Agents Dream of False Memories? Black-box Visual Attacks on Long-term Memory in Multimodal A | attacks / deployed systems | TP |
| 2607.19267 | They'll Verify. They Just Won't Act. How Authority Framing and Laundered Code Turn a Trusted Ag | attack / production llms | TP |
| 2607.25936 | From Role Prompt to Infinite Thinking: Exploiting Persona Conditioning for Inference Cost Attac | exploiting / real-world applications | TP |
| 2608.04741 | LoginTrap: Uncovering Task-Agnostic Phishing-Style Indirect Prompt Injection Attacks against LL | prompt injection / end-to-end attack | TP |
| 2609.09553 | Arbitrary Cipher Attacks Against Large Language Models Do Not Require Fine-Tuning | attacks / commercial models | TP |
| 2609.32635 | Trust the Brand, Lose Control: How Identity Hijacks LLM Agent Orchestration | hijacks / production agent | TP |
| 2609.39902 | CodeMimicry: Exploiting Safety Generalization Lag in Large Language Models via Structured Code  | exploiting / commercial llms | TP |

## 7. Reproduce

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
