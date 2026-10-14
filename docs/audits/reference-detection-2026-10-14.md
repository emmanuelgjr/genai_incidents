# Reference-quality detection, 2026-10-14

**Detection only, read-only, no data changed; agent-suggested, not human-reviewed.**
Produced by the pipeline-engineer agent at the foreman's request (candidate 1 of the user's outside brief).
Nothing under `data/` or any tracked file other than this report was touched. Every flagged row below is a
*candidate*; no row has been confirmed as wrong by a human. Cached third-party page text is not reproduced
here (titles and matched tokens only).

Script: `C:/Users/emman/AppData/Local/Temp/claude/C--repos-genai-incidents/0cbeb36b-c08c-48b9-a667-1bb2a887549c/scratchpad/refaudit/refaudit.py`
(scratch, outside the repo; Appendix A is the full text, so this report is the record). Corpus audited:
`data/incidents.json` at `c80b7e61`, 15,784 rows (15,755 standing + 29 retracted), 77,059 reference entries.

## 1. Two premises in the brief that do not hold

1. **"~3,200 v1.0 rows, many reviewed/curated" is not the legacy seed.** CHANGELOG 1.0.0 says "~3,200
   incidents" for the *whole* first release; the hand-curated seed is much smaller. In the current corpus the
   seed is the **176 rows** whose `source_ids` contain `INC-<n>` (106 rows, 113 distinct ids) and/or
   `LEGACY-INC-<n>` (103 rows, 108 distinct ids; 33 rows carry both). All 119 `quality_tier: curated` rows
   are in this set, plus 57 `reviewed`. `data/legacy_consolidated.json` holds 239 entries (`INC-00001`..) -
   I did not reconcile 239 vs 176 (merges/retirements); the audit runs on the shipped corpus.
2. **The placeholders are original, not a late regression.** `git log -S"2501.01234"` on
   `data/incidents.json` returns `c105bd7a "Initial dataset: 578 GenAI/agentic AI security incidents"`.
   The bad references have been present since the first commit.

Everything else the brief says about the eight named rows is confirmed (section 3), with two additions
(INC-036 also cites the EFF homepage as "research"; INC-042's "blog root" is `/blog/engineering/`, an index).

## 2. ID mapping: legacy source id -> current entry id

Legacy ids live in `source_ids`, never in `id`. Current `id` values (`INC-0xxxx`) are a different, later
numbering, so `INC-033` does NOT mean `INC-00033`. Lookup:
`next(e for e in incidents if "INC-033" in e["source_ids"])`.

| legacy source id | current id | quality_tier | other legacy source id |
|---|---|---|---|
| INC-033 | INC-03004 | reviewed | - |
| INC-036 | INC-02454 | curated | INC-039 (merged) |
| INC-037 | INC-02353 | reviewed | - |
| INC-040 | INC-03247 | reviewed | - |
| INC-041 | INC-02922 | reviewed | - |
| INC-042 | INC-04310 | reviewed | - |
| INC-045 | INC-03570 | reviewed | - |
| INC-046 | INC-03444 | reviewed | - |

## 3. VERDICTS (named rows)

All fetches via `ingest/common.fetch_once` (robots, 1 s/host, identifying UA); `fetched_at` is UTC, 2026-10-14.
arXiv pages: `https://arxiv.org/abs/<id>` (the `export.arxiv.org/api` endpoint is robots-disallowed for our UA, so it
was not used and not overridden).

| legacy id (current id) | current reference URL(s) | what it actually is (fetched) | rules tripped | brief |
|---|---|---|---|---|
| INC-033 (INC-03004) | `arxiv.org/abs/2501.01234` (type research) | real paper, wrong topic: title "Impact of QCD sum rules coupling constants on neutron stars structure" (fetched 10:40:19Z); no shared content tokens with entry title/affected, nor with the abstract | **R2** (title-no-overlap, summary-no-overlap; id also matches the placeholder-digit pattern `01234`) | CONFIRMED |
| INC-036 (INC-02454) | `reuters.com/legal/` (news); `eff.org/` (research) | reuters: section index (`/legal/`), **not fetchable**, robots.txt refused for our UA, so contents unverified; eff.org: organisation homepage, title "Electronic Frontier Foundation / Defending your rights in the digital world" (200, 11:00:13Z), though the reference title says "AI copyright training data legal analysis - EFF" | **R1** (both), **R4** (eff.org), **R5** ("$50M" absent from the one fetched source, the EFF homepage) | CONFIRMED (+ the EFF homepage, not in the brief) |
| INC-037 (INC-02353) | `msrc.microsoft.com/` (research) | MSRC portal homepage, title "MSRC - Microsoft Security Response Center" (200, 10:51:27Z) | **R1** (homepage), **R4** | CONFIRMED |
| INC-040 (INC-03247) | `usenix.org/conference/usenixsecurity25` (research) | conference landing page, title "USENIX Security '25 / USENIX" (200, 11:00:34Z), not a paper | **R1** (conference-index), **R4**, **R5** (23% absent from it) | CONFIRMED |
| INC-041 (INC-02922) | `risk.net/` (news) | publisher homepage, title "Risk.net - Financial Risk Management News Analysis" (200, 11:00:26Z) | **R1** (homepage), **R5** ($8M and 340 absent from it) | CONFIRMED |
| INC-042 (INC-04310) | `uber.com/blog/engineering/` (advisory) | blog section index by URL shape; fetch returned HTTP 406 (no content, so page kind unverified beyond the URL) | **R1** (index-segments) | CONFIRMED in substance; it is the engineering-blog index, not the bare blog root |
| INC-045 (INC-03570) | `arxiv.org/abs/2408.00000` (research) | **no such arXiv paper**: abs page HTTP 404 (re-checked 2026-10-14) | **R2** (placeholder-id, id-not-found) | CONFIRMED |
| INC-046 (INC-03444) | `arxiv.org/abs/2407.00000` (research) | **no such arXiv paper**: abs page HTTP 404 (re-checked 2026-10-14) | **R2** (placeholder-id, id-not-found) | CONFIRMED |

Caveat on R5 for 036/040/041: "absent" means absent from the *homepage text we could fetch*; it says the cited
page cannot support the figure, not that the figure is false.

## 4. COUNTS

Unit = distinct incident rows (a row with several flagged references counts once per rule). "Legacy" = the
176-row seed defined in section 1. R1-R4 run on all 15,784 rows; R2 on all 206 distinct arXiv ids (204 resolved,
2 are 404). R5 runs on the legacy seed only (1,143 distinct cited URLs; fetch outcomes: 1,008 HTTP 200, 50 x 404,
31 robots-refused, 26 x 403, 22 arXiv via the arXiv cache, 6 other: 2 network errors, 2 x 503, one 406, one 429).
Only 3 DOI-form URLs exist in the corpus (ACM/Springer), none flagged; a DOI metadata fetch was therefore not
built (R2-DOI is effectively a no-op on this corpus: a gap, not a pass).

| rule | rows (all) | of which legacy seed | by quality_tier (all rows) |
|---|---|---|---|
| R1 shallow / index page | 146 | 21 | auto 28, curated 10, reviewed 108 |
| R2 arXiv id/title mismatch | 11 | 9 | curated 3, reviewed 8 |
| R3 generic URL reused >=10 rows | 200 | 0 | auto 199, reviewed 1 |
| R4 "research" ref not on a paper host | 1,622 | 107 | auto 2, curated 95, reviewed 1,525 |
| R5 figure absent from all fetched sources (legacy only) | 25 | 25 | curated 11, reviewed 14 |
| **distinct rows tripping any rule** | **1,959** | **130 of 176** | reviewed 1,631, auto 229, curated 99 |

Higher-confidence subsets (my judgement of which rules indicate "not a source"; R3 and R4 are weak, see section 5):
R1 or R2: **156** rows (30 legacy: curated 13, reviewed 17; no auto). R1 or R2 or R5, legacy only: 47.
Legacy rows tripping R1-R4 (no network text needed): 122. 8 of the 25 R5 trips also trip R1/R2; in 6 the only
text-bearing source is itself an R1 page, so R5 partly re-detects the same bad references.

The unrefined brief wording (path depth <= 1, no query string) would flag **2,201** rows (38 legacy), 15x more
than the refined R1, dominated by news sites whose article slug is the single path segment (tw.news.yahoo.com,
businessinsider.com, ...). Both numbers are reported; R1 in the table is the refined one.

R2 sub-flags (rows): placeholder-id 3, id-not-found 2, title-no-overlap 9, title+summary-no-overlap 6.
Hand adjudication of the 11 (agent judgement, not human review): clearly wrong paper or nonexistent id: 7
(INC-03004, 03570, 03444, 04207, 03955, 03491, 03972); likely wrong paper: 1 (INC-04142, AgentDojo cited for
"RAG corpus poisoning"); tangential-but-plausible citations, probable false positives: 3 (INC-04067, 04383, 05052).

R5 states over the 176 legacy rows: TRIP 25, ok 14, no extractable figure 124, undetermined (no fetchable source
text) 13. The 124 "no figure" rows include figures the extractor does not capture (word numbers above twelve or
in prose such as "three separate incidents", ranges like "7-12 turns"), so R5 recall is incomplete; the 25 is a lower bound.

Raw script output (tables per rule, per source family; a row with ids from several families counts under each):

```
rows=15784 legacy=176 refs=77059
R1raw (depth<=1, no query) rows=2201 legacy=38
| rule | rows (all) | of which legacy seed | by quality_tier (all) |
| R1 | 146 | 21 | auto 28, curated 10, reviewed 108 |
| R2 | 11 | 9 | curated 3, reviewed 8 |
| R3 | 200 | 0 | auto 199, reviewed 1 |
| R4 | 1622 | 107 | auto 2, curated 95, reviewed 1525 |
| R5 | 25 | 25 | curated 11, reviewed 14 |
ANY rule: 1959 (legacy 130); tiers {'reviewed': 1631, 'curated': 99, 'auto': 229}
R1-R4 (no network text) 1951 122
--- by source family (rows may belong to several families)
| family | rows | R1 | R2 | R3 | R4 | R5 |
| AIAAIC | 1522 | 0 | 0 | 0 | 0 | 0 |
| AIID | 1584 | 1 | 0 | 0 | 1382 | 0 |
| ARXIV | 170 | 0 | 2 | 0 | 4 | 0 |
| ATLAS | 64 | 7 | 3 | 0 | 58 | 1 |
| AVID | 313 | 2 | 0 | 4 | 1 | 0 |
| CCS | 2 | 0 | 0 | 0 | 0 | 0 |
| CVE | 7443 | 93 | 0 | 200 | 25 | 2 |
| EXT | 47 | 1 | 0 | 0 | 31 | 0 |
| GARAK | 1 | 0 | 0 | 0 | 1 | 0 |
| GHSA | 828 | 7 | 0 | 0 | 3 | 1 |
| LEGACY-SEED | 176 | 21 | 9 | 0 | 107 | 25 |
| MAL | 1 | 0 | 0 | 0 | 0 | 0 |
| NDSS | 1 | 0 | 0 | 0 | 0 | 0 |
| OECD-AIM | 4104 | 19 | 0 | 0 | 113 | 0 |
| OWASP | 6 | 0 | 0 | 0 | 2 | 0 |
| PROMPTFOO | 1 | 0 | 0 | 0 | 1 | 0 |
| REDTEAM | 10 | 3 | 1 | 0 | 5 | 0 |
| RES | 116 | 8 | 0 | 0 | 93 | 0 |
| USENIX | 4 | 0 | 1 | 0 | 0 | 0 |
| VTR | 29 | 1 | 0 | 0 | 2 | 0 |
--- R2 sub-flags: {'placeholder-id': 3, 'id-not-found': 2, 'title-no-overlap': 9, 'summary-no-overlap': 6}
R1 reasons: {'homepage': 69, 'conference-index': 4, 'depth1-non-slug': 81, 'index-segments': 5}
R5 states: {'no-figure': 124, 'TRIP': 25, 'undetermined-no-source-text': 13, 'ok': 14}
legacy ref fetch outcomes: {'200': 1008, '404': 50, 'robots-refused': 31, '403': 26, 'arxiv-cache': 22, 'error': 2, '503': 2, '406': 1, '429': 1}
R3 threshold 10 ; reuse distribution: >=5: 43 >=10: 18 >=20: 3
  32 https://github.com/sooperset/mcp-atlassian/releases/tag/v0.22.0
  32 https://github.com/sooperset/mcp-atlassian/pull/1448
  32 https://github.com/sooperset/mcp-atlassian/commit/b041733473f95119dd539542a43c280737a8e460
  19 https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
  17 https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
  17 https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
  17 https://github.com/open-webui/open-webui/releases/tag/v0.10.0
  17 https://github.com/open-webui/open-webui/releases/tag/v0.11.1
  16 https://github.com/open-webui/open-webui/releases/tag/v0.11.0
  16 https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
  16 https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
  13 https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio
```

## 5. Rule definitions, failure inputs, and controls

Controls: `python -I refaudit.py controls` prints `ALL CONTROLS PASS` (28 PASS lines, Appendix C). For each
rule: the exact definition, the input that would make it fail, and the controls that were run.

**R1 - shallow or index URL.** References carrying a query string or fragment are skipped (they select a record,
e.g. `cve.org/CVERecord?id=`). Otherwise trips when: the path has 0 segments ("homepage"); or exactly 1 segment
that is not slug-like (slug-like = >= 2 hyphens, or >= 24 chars, or ends `.html/.htm/.shtml/.aspx/.php`, or
>= 5 consecutive digits); or a `/conference|event|events/<name>` URL; or every segment is in an index-word set
(blog, news, advisories, issues, research, engineering, ...). *Input that makes it fail:* a homepage written with
a query (`https://www.risk.net/?lang=en` - the control shows it is NOT flagged); a deep but generic page
(`/category/ai/page/2/`); a one-segment page with fewer than 2 hyphens that is really an article (`/glossary`).
Positive controls: risk.net, MSRC root, USENIX conference index, uber `/blog/engineering/` all trip.
Negative controls: a techcrunch article URL and a `cve.org/CVERecord?id=` URL do not.

**R2 - arXiv id check.** For every `arxiv.org/(abs|pdf|html)/<id>` reference: placeholder-id if the new-style
suffix is all zeros, a repeated digit, or in {01234, 1234, 12345, 56789, 5678}; id-not-found if the abs page is
HTTP 404; title-no-overlap if the arXiv title shares no content token with entry `title` + `affected` (tokens:
lowercase, length >= 3, stopwords and a generic-word list - llm, model(s), attack(s), security, ai, language, large,
data, ... - removed, trailing "s" stemmed); summary-no-overlap additionally against the abstract. Trips on any
sub-flag. *Input that makes it fail:* a wrong paper sharing one content word with the entry; a right paper whose
title uses different vocabulary than the entry (the 3 probable false positives); any DOI (not implemented; the
corpus has none flagged); non-arXiv paper links. Positive controls: INC-03004 (neutron star), INC-03570 and
INC-03444 (404) trip; a synthetic unrelated title trips. Negative controls: three real ARXIV-sourced rows
(universal adversarial attacks, AutoDAN, black-box jailbreaking) do not trip; a synthetic matching title does not;
`2402.12336` is not a placeholder.

**R3 - generic URL reuse.** URL normalised (lowercase host, no trailing slash, no fragment, query kept); a row
trips if any of its URLs appears on >= 10 distinct rows (threshold 10; 43 URLs reach 5, 18 reach 10, 3 reach 20).
Result: 200 rows via 18 URLs, **all** specific GitHub release/commit/PR or advisory pages shared by CVE rows for a
single fix (R3 intersect R1 = 0). R3 found no generic-URL abuse; treat it as a candidate feed only. *Input that
makes it fail:* a generic URL reused on 9 or fewer rows (control: reused on 10 rows flagged, on 9 not), or reused
with varying query strings. Top reused URLs are in the raw output above.

**R4 - "research" reference not on a paper host.** Field: `references[].type == "research"` (1,915 refs).
Deterministic rule, no fetch: trips unless the host is in a paper-host set (arxiv, doi.org, dl.acm.org,
ieeexplore, openreview, aclanthology, MLR/NeurIPS proceedings, springer, sciencedirect, ssrn, eprint.iacr,
semanticscholar, biorxiv/medrxiv, AAAI ojs, nature, science, pubmed, ndss, nist csrc, researchgate, research.google)
with >= 2 path segments, or a usenix `/presentation/` or `/system/files/` URL, or the path ends `.pdf`.
*Input that makes it fail:* a non-paper page on a paper host (control: `arxiv.org/list/cs.CR/new` is NOT flagged)
and a real paper on an unlisted host (flagged). **Weak rule:** `research` is also used for vendor write-ups and
for the AIRI Navigator aggregator (1,456 refs, 1,382 AIID rows), so R4 lists "what we call research", not errors.
Positive control: INC-02353 (MSRC root). Negative controls: a research ref on `arxiv.org/abs/...`; a non-research
type is out of scope.

**R5 - figure absent from every cited source (legacy seed only; the 1,143 cited URLs are the documented
population, chosen because fetching all 77,059 references is infeasible).** Figures extracted from `description`
+ `impact` + `title`: money (`$`, USD, EUR, GBP, with K/M/B/million/billion), percentages, durations (number +
minute/hour/day/week/month/year/second; word numbers to twelve) and counts (a number >= 10 or comma-grouped
followed by a noun; years excluded). Normalised to values; a figure is "found" if the same normalised figure is
extracted from any fetched source (counts: also any bare numeric token equal to it). TRIP = at least one source
text was fetched and some figure is found in none. A row with no fetchable text is `undetermined` (13 rows), not a
trip. *Input that makes it fail:* paywalled, blocked or PDF sources (no text, so undetermined), a figure only in
an image, and any figure the extractor does not parse. Controls: synthetic positive (figures absent -> TRIP);
synthetic negative ("$8 million", "40 percent" in the source for "$8M+", "40%" -> ok); undetermined is not a trip;
and a **tamper control on a real row that previously passed** (INC-04179): "$987,654 and 13.37%" appended to its
description in memory -> TRIP.

## 6. Limits (what this report does not establish)

* Detection only. No row was verified wrong by a human; no source was read for the claim it supports beyond
  token/figure presence.
* 31 legacy reference URLs were robots-refused and 80 more returned HTTP 404/403/406/429/503 (2 network errors):
  those sources are unverified, not clean.
* Page "kind" comes from the fetched `<title>` and URL shape; redirects are followed by urllib but the final URL
  is not recorded.
* Rows outside the legacy seed were not text-checked (R5 scope). R2's arXiv check covers all 206 ids corpus-wide.
* `data/legacy_consolidated.json` (239 entries) was not audited separately.

## 7. Re-derivation commands

`$SCRATCH` = `C:/Users/emman/AppData/Local/Temp/claude/C--repos-genai-incidents/0cbeb36b-c08c-48b9-a667-1bb2a887549c/scratchpad/refaudit`
(read-only; caches live there, never in the repo). cwd = repo root.

| figure | command |
|---|---|
| fetch arXiv metadata (206 ids, ~12 min) | `python -I $SCRATCH/refaudit.py fetch-arxiv` |
| fetch legacy cited URLs (1,121 URLs, ~25 min) | `python -I $SCRATCH/refaudit.py fetch-legacy` |
| every count, per-tier and per-family table in section 4 | `python -I $SCRATCH/refaudit.py stats` (offline, from cache; also writes `results.json`) |
| per-rule summary | `python -I $SCRATCH/refaudit.py run` |
| the 28 controls | `python -I $SCRATCH/refaudit.py controls` |
| sample tables below | `python -I $SCRATCH/samples.py` |
| legacy -> current id | `python -c "import json;d=json.load(open('data/incidents.json'))['incidents'];print({s:e['id'] for e in d for s in e['source_ids'] if s in ('INC-033','INC-036','INC-037','INC-040','INC-041','INC-042','INC-045','INC-046')})"` |
| legacy seed size (176) | `python -c "import json,re;d=json.load(open('data/incidents.json'))['incidents'];print(sum(any(re.match(r'^(LEGACY-)?INC-\d+$',s) for s in e['source_ids']) for e in d))"` |
| placeholder provenance | `git log --oneline -S"2501.01234" -- data/incidents.json` |

## 8. Sample of flagged rows

(ids are current ids; titles truncated; "legacy" marks the seed; R3 samples are the top-URL list in the raw output)

### R1 sample

| id | seed | tier | title | flagged URL | reason |
|---|---|---|---|---|---|
| INC-01015 | legacy | curated | Flowise v3.0.1 < 3.0.8 and all versions after with 'ALLOW_BUILTIN_DEP' | https://flowiseai.com | homepage |
| INC-01291 | legacy | curated | LangChain LLMMathChain prompt-injection RCE via Python exec | https://www.langchain.com/ | homepage |
| INC-01589 | legacy | curated | OpenClaw AI agent security crisis — 138 CVEs in 63 days, 341 malicious | https://openclaw.ai/blog | depth1-non-slug |
| INC-02353 | legacy | reviewed | Azure OpenAI content filter bypass via structured output mode | https://msrc.microsoft.com/ | homepage |
| INC-02454 | legacy | curated | Clearview AI biometric bias — $50M class action settlement | https://www.reuters.com/legal/ | depth1-non-slug |
| INC-02471 | legacy | curated | Cursor Workspace File Injection | https://github.com/MaccariTA | depth1-non-slug |
| INC-00021 |  | reviewed | A side-channel vulnerability exists in the implementation of BIP-39 mn | http://trezor.com | homepage |
| INC-00570 |  | reviewed | Aim Labs Continuing EchoLeak Research and Variants | https://www.aim.security/news | depth1-non-slug |
| INC-00864 |  | reviewed | Critical Vulnerability in Anthropic's MCP Exposes AI Systems to Remote | https://cybersecuritynews.com/flowise-vulnerability/ | depth1-non-slug |
| INC-01194 |  | reviewed | In its design for automatic terminal command execution, Sixth offers t | https://trysixth.com/ | homepage |

### R2 all

| id | entry title | arXiv URL | sub-flags | fetched arXiv title |
|---|---|---|---|---|
| INC-04142 | RAG corpus poisoning — embedding-space manipulation to force retrieval | https://arxiv.org/abs/2406.13352 | title-no-overlap+summary-no-overlap | AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks  |
| INC-03972 | MathPrompt: symbolic mathematics jailbreak attack | https://arxiv.org/abs/2410.15262 | title-no-overlap | HyQE: Ranking Contexts with Hypothetical Query Embeddings |
| INC-04207 | Skeleton Key: direct system prompt override (Microsoft) | https://arxiv.org/abs/2402.06627 | title-no-overlap+summary-no-overlap | Feedback Loops With Language Models Drive In-Context Reward Hacking |
| INC-03004 | OpenAI o1/o3 reasoning chain jailbreak via chain-of-thought manipulati | https://arxiv.org/abs/2501.01234 | placeholder-id+title-no-overlap+summary-no-overlap | Impact of QCD sum rules coupling constants on neutron stars structure |
| INC-03570 | Anthropic Claude context flooding — resource exhaustion via adversaria | https://arxiv.org/abs/2408.00000 | placeholder-id+id-not-found | (no such paper) |
| INC-03444 | Adversarial embedding attacks on production RAG systems | https://arxiv.org/abs/2407.00000 | placeholder-id+id-not-found | (no such paper) |
| INC-03491 | AI-generated CSAM detection evasion — adversarial manipulation of cont | https://arxiv.org/abs/2311.16090 | title-no-overlap | Self-correcting LLM-controlled Diffusion Models |
| INC-04067 | OpenAI GPT-4 system prompt extraction toolkit — systematic prompt leak | https://arxiv.org/abs/2403.06634 | title-no-overlap | Stealing Part of a Production Language Model |
| INC-03955 | LLM-generated malware evades endpoint detection — AI-assisted polymorp | https://arxiv.org/abs/2310.07906 | title-no-overlap+summary-no-overlap | Power Tracking Control of Heterogeneous Populations of TCLs with Parti |
| INC-04383 | Achieving Code Execution in MathGPT via Prompt Injection | https://arxiv.org/abs/2103.03874 | title-no-overlap | Measuring Mathematical Problem Solving With the MATH Dataset |
| INC-05052 | Attempted Evasion of ML Phishing Webpage Detection System | https://arxiv.org/abs/2212.14315 | title-no-overlap+summary-no-overlap | "Real Attackers Don't Compute Gradients": Bridging the Gap Between Adv |

### R4 sample

| id | seed | title | flagged URL |
|---|---|---|---|
| INC-00036 | legacy | A2A Protocol -- Agent Card Poisoning Vulnerability | https://live.paloaltonetworks.com/t5/community-blogs/safeguarding-ai-agents-an-i |
| INC-00198 | legacy | AI recommendation poisoning — hidden prompt injections in 'Summarize w | https://www.microsoft.com/en-us/security/blog/2026/02/10/ai-recommendation-poiso |
| INC-00627 | legacy | AnythingLLM Multiple CVEs | https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-rrmw-2j6x |
| INC-00668 | legacy | AWS Bedrock AgentCore "Agent God Mode" Privilege Escalation | https://unit42.paloaltonetworks.com/exploit-of-aws-agentcore-iam-god-mode/ |
| INC-00671 | legacy | Axios npm supply chain attack — North Korean Sapphire Sleet targets 70 | https://cloud.google.com/blog/topics/threat-intelligence/north-korea-threat-acto |
| INC-00131 |  | AI Coding Agent 'MJ Rathbun' Allegedly Published Personalized Accusato | https://www.airi-navigator.com/incidents/1373 |
| INC-00577 |  | Amazon Delivery Van Reportedly Became Stranded on Essex Mudflats After | https://www.airi-navigator.com/incidents/1376 |
| INC-00606 |  | Anthropic leaks Claude source code in unsecured data store | https://www.zscaler.com/blogs/security-research/anthropic-claude-code-leak |
| INC-00608 |  | Anthropic Said DeepSeek, Moonshot, and MiniMax Used Fraudulent Account | https://www.airi-navigator.com/incidents/1395 |
| INC-00643 |  | AppOmni Critical AI Agent Flaws in Microsoft Copilot Studio | https://winbuzzer.com/2026/02/04/critical-ai-agent-flaws-exposed-in-microsoft-an |

### R5 legacy trips

| id | tier | title | figures absent | text-bearing sources |
|---|---|---|---|---|
| INC-04490 | reviewed | Bing Chat 'Sydney' jailbreak — persona escape and threatening behaviou | ('dur', 2.0, 'h') | 1 |
| INC-03529 | reviewed | Air Canada chatbot invents bereavement discount policy — tribunal ruli | ('dur', 90.0, 'd'), ('usd', 650.0) | 2 |
| INC-04653 | reviewed | GitHub Copilot reproduces verbatim licensed code and embedded secrets | ('pct', 1.0) | 2 |
| INC-01288 | reviewed | LAAF v2.0 — Empirical LPCI breakthrough rates of 67–100% across 5 prod | ('pct', 85.0), ('pct', 92.0) | 2 |
| INC-03972 | reviewed | MathPrompt: symbolic mathematics jailbreak attack | ('pct', 73.6) | 1 |
| INC-05159 | reviewed | Meta Galactica model withdrawn after misinformation at launch | ('count', 72.0), ('dur', 72.0, 'h') | 1 |
| INC-02774 | curated | Italy Garante orders ChatGPT GDPR enforcement — consent and data minim | ('count', 15000000.0), ('usd', 15000000.0) | 2 |
| INC-02454 | curated | Clearview AI biometric bias — $50M class action settlement | ('count', 50000000.0), ('usd', 50000000.0) | 1 |
| INC-03247 | reviewed | Synthetic data re-identification — de-anonymized patients from synthet | ('pct', 23.0) | 1 |
| INC-02922 | reviewed | Multi-agent financial trading system flash crash — cascading autonomou | ('count', 340.0), ('usd', 8000000.0) | 1 |
| INC-04221 | reviewed | Stability AI synthetic CSAM generation — training data and output safe | ('count', 3000.0) | 1 |
| INC-03822 | reviewed | Google Gemini AI image generator refuses to depict white people — over | ('usd', 90000000000.0) | 2 |
| INC-04005 | reviewed | Microsoft Recall screenshots everything — OS-level data retention with | ('dur', 5.0, 's'), ('dur', 6.0, 'mo') | 1 |
| INC-03815 | reviewed | Google AI Overviews recommends adding glue to pizza — RAG hallucinatio | ('count', 11.0), ('dur', 11.0, 'y') | 1 |
| INC-03628 | reviewed | Character.AI teen suicide — AI companion encouraged self-harm | ('dur', 14.0, 'y') | 1 |
| INC-04070 | reviewed | OpenAI Whisper hallucinating medical transcriptions — fabricated diagn | ('count', 30000.0), ('pct', 1.0) | 1 |
| INC-00671 | curated | Axios npm supply chain attack — North Korean Sapphire Sleet targets 70 | ('dur', 3.0, 'h') | 1 |
| INC-02105 | curated | XBOW — first critical CVE discovered entirely by autonomous AI penetra | ('count', 1060.0), ('dur', 28.0, 'min'), ('dur', 40.0, 'h') | 2 |
| INC-01092 | curated | GlassWorm supply chain — 72 malicious VSCode extensions, 9 million ins | ('count', 433.0), ('count', 72.0), ('count', 9000000.0) | 1 |
| INC-00834 | curated | Clinejection — CI/CD pipeline compromise via Cline's issue triage bot, | ('count', 4000.0), ('dur', 8.0, 'h') | 1 |
| INC-00198 | curated | AI recommendation poisoning — hidden prompt injections in 'Summarize w | ('count', 12.0) | 1 |
| INC-01589 | curated | OpenClaw AI agent security crisis — 138 CVEs in 63 days, 341 malicious | ('count', 21000.0), ('count', 63.0), ('dur', 63.0, 'd') | 8 |
| INC-03194 | curated | Salesloft Drift OAuth breach — Chinese actor UNC6395 accesses 700+ Sal | ('count', 700.0) | 1 |
| INC-02190 | curated | AgentSeal MCP server mass scan — 66% of 1,808 servers have security fi | ('pct', 10.0), ('pct', 13.0), ('pct', 20.0), ('pct', 43.0) | 1 |
| INC-02878 | curated | mcp-remote OAuth Command Injection (CVE-2025-6514) | ('count', 437000.0) | 5 |

## Appendix A - refaudit.py (full text)

```python
#!/usr/bin/env python
"""Reference-quality detection (R1-R5) over data/incidents.json. READ-ONLY.

Detection only: writes nothing under the repo. Network goes ONLY through
ingest/common.fetch_once (robots, per-host rate limit, identifying UA).
Fetched pages are cached in <scratch>/cache (never in the repo).

  python refaudit.py fetch-arxiv     # arXiv export API, batched, cached
  python refaudit.py fetch-legacy    # fetch cited URLs of legacy-seed rows (R5)
  python refaudit.py run             # offline: apply R1-R5 from cache, write results.json
  python refaudit.py controls        # positive / negative controls
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
import time
import defusedxml.ElementTree as ET  # fetched XML is untrusted
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

REPO = Path("C:/repos/genai_incidents")
SCRATCH = Path(__file__).resolve().parent
CACHE = SCRATCH / "cache"
DATA = REPO / "data" / "incidents.json"
sys.path.insert(0, str(REPO))

LEGACY_RE = re.compile(r"^(LEGACY-)?INC-\d+$")

# ---------------------------------------------------------------- loading
def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["incidents"]


def is_legacy(e) -> bool:
    return any(LEGACY_RE.match(s) for s in e["source_ids"])


def families(e) -> set[str]:
    out = set()
    for s in e["source_ids"]:
        if LEGACY_RE.match(s):
            out.add("LEGACY-SEED")
        elif s.startswith("OECD-AIM"):
            out.add("OECD-AIM")
        else:
            out.add(re.split(r"[-_]", s)[0].rstrip("0123456789") or s)
    return out


# ---------------------------------------------------------------- caching / fetching
def cpath(key: str) -> Path:
    return CACHE / (hashlib.sha1(key.encode()).hexdigest() + ".json")


def cget(key):
    p = cpath(key)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def cput(key, obj):
    CACHE.mkdir(exist_ok=True)
    cpath(key).write_text(json.dumps(obj), encoding="utf-8")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def strip_html(b: bytes):
    t = b.decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    title = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    import html
    t = html.unescape(t)
    return title, re.sub(r"\s+", " ", t)[:2_000_000]


def fetch_url(url: str) -> dict:
    """One conduct-compliant fetch through ingest.common; result cached."""
    c = cget(url)
    if c:
        return c
    from ingest import common
    rec = {"url": url, "fetched_at": now()}
    try:
        body, hdr = common.fetch_once(url, timeout=25)
        ctype = (hdr.get("Content-Type") or "").lower()
        rec.update(status=200, content_type=ctype, bytes=len(body))
        if "pdf" in ctype or body[:4] == b"%PDF":
            rec.update(title=None, text="", kind="pdf-not-parsed")
        else:
            title, text = strip_html(body)
            rec.update(title=title, text=text, kind="html")
    except PermissionError as ex:
        rec.update(status="robots-refused", error=str(ex)[:120], text="", title=None, kind="none")
    except Exception as ex:  # noqa: BLE001 - record every failure, never raise
        code = getattr(ex, "code", None)
        rec.update(status=code or "error", error=f"{type(ex).__name__}: {ex}"[:160],
                   text="", title=None, kind="none")
    cput(url, rec)
    return rec


# ---------------------------------------------------------------- R1
INDEX_SEGMENTS = {
    "blog", "blogs", "news", "newsroom", "press", "advisories", "advisory", "security-advisories",
    "issues", "research", "resources", "articles", "insights", "engineering", "publications",
    "papers", "security", "legal", "about", "company", "products", "events", "conference",
    "conferences", "docs", "documentation", "home", "index", "en", "en-us", "us", "stories",
    "updates", "archive", "archives", "bulletins", "releases", "reports", "library", "learn",
}
CONF_INDEX_RE = re.compile(r"^/(conference|event|events)/[a-z0-9\-]+/?$", re.I)  # usenix.org/conference/usenixsecurity25


def segs(url):
    return [s for s in urlparse(url).path.split("/") if s]


def slug_like(seg: str) -> bool:
    """A single path segment that looks like an article slug / record id rather than a section name."""
    return (seg.count("-") >= 2 or len(seg) >= 24 or bool(re.search(r"\.(html?|shtml|aspx?|php)$", seg, re.I))
            or bool(re.search(r"\d{5,}", seg)))


def r1_raw(url: str) -> bool:
    """Unrefined brief wording: path depth <= 1 (no query/fragment)."""
    p = urlparse(url)
    return not (p.query or p.fragment) and len(segs(url)) <= 1


def r1(url: str) -> str | None:
    """Return reason string if url is a homepage / shallow / index page."""
    p = urlparse(url)
    if p.query or p.fragment:          # a query/fragment normally selects a record
        return None
    s = segs(url)
    if len(s) == 0:
        return "homepage"
    if len(s) == 1 and not slug_like(s[0]):
        return "depth1-non-slug"
    if CONF_INDEX_RE.match(p.path):
        return "conference-index"
    if s[-1].lower() in INDEX_SEGMENTS and all(x.lower() in INDEX_SEGMENTS for x in s):
        return "index-segments"
    return None


# ---------------------------------------------------------------- R2
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf|html)/([^?#\s]+?)(?:\.pdf)?(?:v\d+)?/?$", re.I)
DOI_RE = re.compile(r"(?:doi\.org/|/doi/(?:abs/|full/|pdf/|epdf/)?)(10\.\d{4,9}/[^?#\s]+)", re.I)
DOI_ART_RE = re.compile(r"/(?:article|articles)/(10\.\d{4,9}/[^?#\s]+)", re.I)
ARXIV_NEW = re.compile(r"^(\d{4})\.(\d{4,5})$")

STOP = set("""a an and are as at be but by for from has have how in into is it its of on or that the their this to
was were what when where which who why will with within without via using use used not no can may more most than then
their they them these those our out over under about after before between both each other such only own same so too
very new vs per also across against among through during up down off again further once here there all any few some
while""".split())
GENERIC = set("""llm llms model models attack attacks attacking ai artificial intelligence security research system
systems language large learning data adversarial vulnerability vulnerabilities exploit incident study analysis
paper based novel approach framework neural network networks deep machine production real world real-world
""".split())


def tokens(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z0-9][a-z0-9\-\.]*[a-z0-9]|[a-z0-9]", (text or "").lower()):
        for part in re.split(r"[\-\.]", w):
            if len(part) < 3 or part in STOP or part in GENERIC or part.isdigit():
                continue
            out.add(part[:-1] if part.endswith("s") and len(part) > 4 else part)
    return out


def arxiv_id(url: str) -> str | None:
    m = ARXIV_RE.search(url)
    return m.group(1) if m else None


def placeholder_arxiv(aid: str) -> bool:
    m = ARXIV_NEW.match(aid)
    if not m:
        return False
    suf = m.group(2)
    return bool(re.fullmatch(r"0+", suf) or re.fullmatch(r"(\d)\1+", suf) or suf in ("01234", "1234", "12345", "56789", "5678"))


def r2_entry(e, url: str, meta: dict | None):
    """meta: {'title','summary'} from arXiv API, or None=not found. Returns list of reasons."""
    reasons = []
    aid = arxiv_id(url)
    if aid is None:
        return reasons
    if placeholder_arxiv(aid):
        reasons.append("placeholder-id")
    if meta is None:
        reasons.append("id-not-found")
        return reasons
    ent = tokens(e["title"] + " " + (e.get("affected") or ""))
    if not (ent & tokens(meta["title"])):
        reasons.append("title-no-overlap")
        if not (ent & tokens(meta["summary"])):
            reasons.append("summary-no-overlap")
    return reasons


def _meta(t, name):
    m = re.search(r'<meta\s+name="%s"\s+content="(.*?)"\s*/?>' % name, t, re.S)
    import html
    return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else None


def fetch_arxiv(ids: list[str]):
    """export.arxiv.org/api is robots-disallowed for our UA (fail-closed, not overridden);
    use the robots-allowed abstract page https://arxiv.org/abs/<id>, 3.5 s spacing."""
    from ingest import common
    for n, i in enumerate([i for i in ids if not cget("arxiv:" + i)], 1):
        url = f"https://arxiv.org/abs/{i}"
        rec = {"id": i, "fetched_at": now(), "url": url}
        try:
            body, _ = common.fetch_once(url, timeout=40, min_interval=3.5)
            t = body.decode("utf-8", "replace")
            title = _meta(t, "citation_title")
            summ = _meta(t, "citation_abstract") or ""
            rec["meta"] = {"title": title, "summary": summ} if title else None
        except Exception as ex:  # noqa: BLE001
            code = getattr(ex, "code", None)
            if code == 404:
                rec["meta"] = None
            else:
                rec["error"] = f"{type(ex).__name__}: {ex}"[:160]
        cput("arxiv:" + i, rec)
        if n % 20 == 0:
            print("arxiv", n, flush=True)


# ---------------------------------------------------------------- R3 / R4
R3_THRESHOLD = 10
PAPER_HOSTS = {
    "arxiv.org", "export.arxiv.org", "doi.org", "dx.doi.org", "dl.acm.org", "ieeexplore.ieee.org",
    "openreview.net", "aclanthology.org", "proceedings.mlr.press", "proceedings.neurips.cc",
    "papers.nips.cc", "papers.neurips.cc", "link.springer.com", "www.sciencedirect.com", "ssrn.com",
    "papers.ssrn.com", "eprint.iacr.org", "www.semanticscholar.org", "www.biorxiv.org",
    "www.medrxiv.org", "ojs.aaai.org", "www.nature.com", "www.science.org", "pubmed.ncbi.nlm.nih.gov",
    "www.ndss-symposium.org", "research.google", "www.cs.cmu.edu", "csrc.nist.gov", "nvlpubs.nist.gov",
    "www.researchgate.net", "scholar.google.com",
}


def r4(ref) -> str | None:
    if ref["type"] != "research":
        return None
    p = urlparse(ref["url"])
    host, path = p.netloc.lower(), p.path.lower()
    if host in PAPER_HOSTS and len(segs(ref["url"])) >= 2:
        return None
    if host.endswith("usenix.org") and re.search(r"/(presentation|system/files)/", path):
        return None
    if path.endswith(".pdf"):
        return None
    return "research-ref-not-paper-host"


# ---------------------------------------------------------------- R5
WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve".split())}
MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mn": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}
UNIT = {"minute": "min", "minutes": "min", "min": "min", "mins": "min", "hour": "h", "hours": "h", "hr": "h",
        "hrs": "h", "day": "d", "days": "d", "week": "w", "weeks": "w", "month": "mo", "months": "mo",
        "year": "y", "years": "y", "second": "s", "seconds": "s"}
NUM = r"(\d[\d,]*(?:\.\d+)?|" + "|".join(WORDNUM) + ")"


def _n(s: str) -> float:
    s = s.lower()
    return float(WORDNUM[s]) if s in WORDNUM else float(s.replace(",", ""))


def figures(text: str) -> set[tuple]:
    t = text.replace("\u2014", " ").replace("\u2013", "-")
    out: set[tuple] = set()
    for m in re.finditer(r"(?:\$|usd\s?|us\$|eur\s?|\u20ac|\u00a3|gbp\s?)\s?" + NUM + r"\s?(k|thousand|mn|m|million|bn|b|billion)?\b",
                         t, re.I):
        v = _n(m.group(1)) * MULT.get((m.group(2) or "").lower(), 1)
        out.add(("usd", round(v, 2)))
    for m in re.finditer(NUM + r"\s?(thousand|million|billion)?\s?(?:us\s)?(?:dollars|usd|euros|pounds)\b", t, re.I):
        out.add(("usd", round(_n(m.group(1)) * MULT.get((m.group(2) or "").lower(), 1), 2)))
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s?(?:%|percent\b|per cent\b)", t, re.I):
        out.add(("pct", float(m.group(1))))
    for m in re.finditer(NUM + r"[\s\-]+(minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?|seconds?)\b", t, re.I):
        out.add(("dur", _n(m.group(1)), UNIT[m.group(2).lower()]))
    for m in re.finditer(r"(?<![\w\-\.])(\d{1,3}(?:,\d{3})+|\d{2,})\+?\s+(?!(?:million|billion|thousand|usd|dollars)\b)([a-z]{3,})", t):
        n = float(m.group(1).replace(",", ""))
        if 1900 <= n <= 2100 and "," not in m.group(1):
            continue                                     # a year
        out.add(("count", n))
    for m in re.finditer(NUM + r"\s?(k|thousand|million|billion)\+?\s+(?!usd|dollars)([a-z]{3,})", t, re.I):
        if m.group(1).lower() in WORDNUM and m.group(2).lower() not in ("thousand", "million", "billion"):
            continue
        out.add(("count", _n(m.group(1)) * MULT[m.group(2).lower()]))
    return out


def figure_in_source(fig, text: str, src_figs: set) -> bool:
    if fig in src_figs:
        return True
    if fig[0] == "count":                               # bare numeric token anywhere in the source
        n = fig[1]
        for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", text):
            try:
                if float(m.group().replace(",", "")) == n:
                    return True
            except ValueError:
                pass
    return False


def r5_row(e, srcs: list[dict]):
    """srcs = cached fetch records for the row's reference URLs."""
    figs = figures(e["description"] + " " + (e.get("impact") or "") + " " + e["title"])
    texts = [s for s in srcs if s.get("status") == 200 and s.get("text")]
    if not figs:
        return {"state": "no-figure", "missing": []}
    if not texts:
        return {"state": "undetermined-no-source-text", "figs": sorted(map(str, figs)), "missing": []}
    sfigs = [(s["text"], figures(s["text"])) for s in texts]
    missing = [f for f in figs if not any(figure_in_source(f, t, sf) for t, sf in sfigs)]
    return {"state": "TRIP" if missing else "ok", "figs": sorted(map(str, figs)),
            "missing": sorted(map(str, missing)), "sources_with_text": len(texts)}


# ---------------------------------------------------------------- driver
def norm_url(u: str) -> str:
    p = urlparse(u)
    return f"{p.scheme}://{p.netloc.lower()}{p.path.rstrip('/')}" + (f"?{p.query}" if p.query else "")


def cmd_fetch_arxiv():
    rows = load()
    ids = sorted({a for e in rows for r in e["references"] if (a := arxiv_id(r["url"]))})
    print(len(ids), "distinct arXiv ids")
    fetch_arxiv(ids)


def cmd_fetch_legacy():
    rows = [e for e in load() if is_legacy(e)]
    urls = sorted({r["url"] for e in rows for r in e["references"]})
    print(len(urls), "distinct legacy URLs", flush=True)
    # arxiv.org pages are covered by fetch-arxiv (3.5 s spacing); do not double-fetch
    todo = [u for u in urls if not cget(u) and urlparse(u).netloc != "arxiv.org"]
    print(len(todo), "to fetch", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for rec in ex.map(fetch_url, todo):
            done += 1
            if done % 50 == 0:
                print(done, "/", len(todo), flush=True)


def analyze(rows):
    res = {"R1": {}, "R2": {}, "R3": {}, "R4": {}, "R5": {}}
    url_rows = collections.defaultdict(set)
    for e in rows:
        for u in {norm_url(r["url"]) for r in e["references"]}:
            url_rows[u].add(e["id"])
    for e in rows:
        for r in e["references"]:
            why = r1(r["url"])
            if why:
                res["R1"].setdefault(e["id"], []).append([r["url"], why])
            why = r4(r)
            if why:
                res["R4"].setdefault(e["id"], []).append([r["url"], r["type"]])
            aid = arxiv_id(r["url"])
            if aid:
                c = cget("arxiv:" + aid)
                meta = c.get("meta") if c and "error" not in c else "NOFETCH"
                if meta == "NOFETCH":
                    continue
                why = r2_entry(e, r["url"], meta)
                if why:
                    res["R2"].setdefault(e["id"], []).append([r["url"], why, meta and meta["title"]])
            if len(url_rows[norm_url(r["url"])]) >= R3_THRESHOLD:
                res["R3"].setdefault(e["id"], []).append(r["url"])
    for e in rows:
        if is_legacy(e):
            srcs = []
            for r in e["references"]:
                aid = arxiv_id(r["url"])
                if aid:
                    c = cget("arxiv:" + aid)
                    m = c.get("meta") if c else None
                    srcs.append({"status": 200, "text": (m["title"] + " " + m["summary"]) if m else ""})
                else:
                    srcs.append(cget(r["url"]) or {"status": "not-fetched"})
            res["R5"][e["id"]] = r5_row(e, srcs)
    res["url_reuse"] = {u: len(v) for u, v in url_rows.items() if len(v) >= 5}
    return res


def cmd_run():
    rows = load()
    res = analyze(rows)
    (SCRATCH / "results.json").write_text(json.dumps(res), encoding="utf-8")
    report(rows, res)


def report(rows, res):
    by = {e["id"]: e for e in rows}
    legacy = {e["id"] for e in rows if is_legacy(e)}
    r5trip = {i for i, v in res["R5"].items() if v["state"] == "TRIP"}
    sets = {"R1": set(res["R1"]), "R2": set(res["R2"]), "R3": set(res["R3"]), "R4": set(res["R4"]), "R5": r5trip}
    sets["R2-strong(title+summary)"] = {i for i, v in res["R2"].items() if any("summary-no-overlap" in x[1] for x in v)}
    sets["R2-placeholder"] = {i for i, v in res["R2"].items() if any("placeholder-id" in x[1] for x in v)}
    sets["R2-not-found"] = {i for i, v in res["R2"].items() if any("id-not-found" in x[1] for x in v)}
    sets["R3-generic(R3&R1)"] = {i for i in sets["R3"] if any(r1(u) for u in res["R3"][i])}
    print("TOTAL rows", len(rows), "legacy", len(legacy))
    for k, s in sets.items():
        print(f"{k}: all={len(s)} legacy={len(s & legacy)}")
    anyr = set().union(sets["R1"], sets["R2"], sets["R3"], sets["R4"], sets["R5"])
    print("ANY of R1-R5: all=", len(anyr), "legacy=", len(anyr & legacy))
    print("legacy ANY of R1,R2,R4,R5:", len(legacy & set().union(sets["R1"], sets["R2"], sets["R4"], sets["R5"])))
    for k, s in sets.items():
        tier = collections.Counter(by[i]["quality_tier"] for i in s)
        fam = collections.Counter(f for i in s for f in families(by[i]))
        print(k, dict(tier), dict(fam.most_common(12)))
    st = collections.Counter(v["state"] for v in res["R5"].values())
    print("R5 states (legacy)", dict(st))


def cmd_controls():
    import copy
    rows = load()
    by = {e["id"]: e for e in rows}
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    # R1
    chk("R1 positive: risk.net homepage trips", r1("https://www.risk.net/"))
    chk("R1 positive: msrc root trips", r1("https://msrc.microsoft.com/"))
    chk("R1 positive: usenix conference index trips", r1("https://www.usenix.org/conference/usenixsecurity25"))
    chk("R1 positive: uber /blog/engineering/ trips", r1("https://www.uber.com/blog/engineering/"))
    chk("R1 negative: techcrunch article does not trip",
        not r1("https://techcrunch.com/2023/05/02/samsung-bans-use-of-generative-ai-tools-like-chatgpt-after-data-leak/"))
    chk("R1 negative: cve.org record (query) does not trip", not r1("https://www.cve.org/CVERecord?id=CVE-2024-50050"))
    chk("R1 KNOWN BLIND SPOT: homepage with ?lang=en does NOT trip (input that makes R1 fail)", not r1("https://www.risk.net/?lang=en"))
    # R2 (uses real cached arXiv metadata)
    for rid, expect in (("INC-03004", True), ("INC-03570", True), ("INC-03444", True)):
        e = by[rid]
        u = e["references"][0]["url"]
        c = cget("arxiv:" + arxiv_id(u))
        meta = c.get("meta") if c else None
        chk(f"R2 positive: {rid} {u} trips -> {r2_entry(e, u, meta)}", bool(r2_entry(e, u, meta)))
    good = [e for e in rows if any(x.startswith("ARXIV-") for x in e["source_ids"]) and not is_legacy(e)]
    shown = 0
    for e in good:
        for r in e["references"]:
            a = arxiv_id(r["url"])
            c = cget("arxiv:" + a) if a else None
            if c and c.get("meta"):
                got = r2_entry(e, r["url"], c["meta"])
                if shown < 3:
                    chk(f"R2 negative: {e['id']} {r['url']} ('{c['meta']['title'][:50]}') -> {got}", not got)
                    shown += 1
                break
        if shown >= 3:
            break
    chk("R2 placeholder positive 2408.00000", placeholder_arxiv("2408.00000"))
    chk("R2 placeholder negative 2402.12336", not placeholder_arxiv("2402.12336"))
    e = copy.deepcopy(by["INC-04853"])
    chk("R2 synthetic: unrelated title vs neutron-star title trips",
        "title-no-overlap" in r2_entry(e, "https://arxiv.org/abs/2501.01234", {"title": "Neutron star mergers", "summary": "gravitational waves"}))
    chk("R2 synthetic: matching title does not trip",
        not r2_entry(e, "https://arxiv.org/abs/2402.12336", {"title": "Samsung source code leak", "summary": "x"}))
    # R3: corrupt a copy so one generic URL is reused across 10 rows, then 9
    for n, want in ((10, True), (9, False)):
        cp = copy.deepcopy(rows[:200])
        for e in cp[:n]:
            e["references"].append({"title": "x", "url": "https://control.example/news/", "type": "news"})
        got = any("https://control.example/news/" in v for v in analyze(cp)["R3"].values())
        chk(f"R3 control: URL on {n} rows -> flagged={want}", got == want)
    # R4
    chk("R4 positive: INC-02353 msrc root (type research) trips", r4(by["INC-02353"]["references"][0]))
    chk("R4 negative: research ref on arxiv.org/abs/.. does not trip",
        not r4({"type": "research", "url": "https://arxiv.org/abs/2402.12336", "title": ""}))
    chk("R4 negative: type news is out of scope", not r4({"type": "news", "url": "https://x.example/", "title": ""}))
    chk("R4 KNOWN BLIND SPOT: non-paper page on a paper host (arxiv.org/list/cs.CR/new) does NOT trip",
        not r4({"type": "research", "url": "https://arxiv.org/list/cs.CR/new", "title": ""}))
    # R5
    e = {"title": "t", "description": "Loss of $8M+ and 40% of users over 3 days", "impact": ""}
    chk("R5 positive: figures absent from fetched source -> TRIP",
        r5_row(e, [{"status": 200, "text": "A generic page about trading."}])["state"] == "TRIP")
    chk("R5 negative: '$8 million', '40 percent', '3 days' in source -> ok (normalisation)",
        r5_row(e, [{"status": 200, "text": "lost eight... $8 million; 40 percent of users; for 3 days"}])["state"] == "ok")
    chk("R5 undetermined: no fetched text is NOT a trip",
        r5_row(e, [{"status": 403, "text": ""}])["state"] == "undetermined-no-source-text")
    # tamper a real legacy row that currently passes R5
    res = json.loads((SCRATCH / "results.json").read_text(encoding="utf-8")) if (SCRATCH / "results.json").exists() else {"R5": {}}
    okrows = [i for i, v in res["R5"].items() if v["state"] == "ok"]
    if okrows:
        e = copy.deepcopy(by[okrows[0]])
        e["description"] += " It cost $987,654 and 13.37% of capacity."
        srcs = [cget(r["url"]) or {"status": "not-fetched"} for r in e["references"]]
        chk(f"R5 tamper control on real row {okrows[0]}: appended figures -> TRIP", r5_row(e, srcs)["state"] == "TRIP")
    print("ALL CONTROLS PASS" if ok else "SOME CONTROLS FAILED")


def cmd_stats():
    """Markdown tables for the report; offline."""
    rows = load()
    res = analyze(rows)
    (SCRATCH / "results.json").write_text(json.dumps(res), encoding="utf-8")
    by = {e["id"]: e for e in rows}
    legacy = {e["id"] for e in rows if is_legacy(e)}
    r5t = {i for i, v in res["R5"].items() if v["state"] == "TRIP"}
    sets = {"R1": set(res["R1"]), "R2": set(res["R2"]), "R3": set(res["R3"]), "R4": set(res["R4"]), "R5": r5t}
    raw = {e["id"] for e in rows if any(r1_raw(r["url"]) for r in e["references"])}
    print(f"rows={len(rows)} legacy={len(legacy)} refs={sum(len(e['references']) for e in rows)}")
    print(f"R1raw (depth<=1, no query) rows={len(raw)} legacy={len(raw & legacy)}")
    print("| rule | rows (all) | of which legacy seed | by quality_tier (all) |")
    for k, s_ in sets.items():
        t = collections.Counter(by[i]["quality_tier"] for i in s_)
        print(f"| {k} | {len(s_)} | {len(s_ & legacy)} | " + ", ".join(f"{a} {b}" for a, b in sorted(t.items())) + " |")
    anyset = set().union(*sets.values())
    anyt = collections.Counter(by[i]["quality_tier"] for i in anyset)
    print(f"ANY rule: {len(anyset)} (legacy {len(anyset & legacy)}); tiers {dict(anyt)}")
    for what, ss in (("R1-R4 (no network text)", set().union(sets['R1'], sets['R2'], sets['R3'], sets['R4'])),):
        print(what, len(ss), len(ss & legacy))
    fams = sorted({f for e in rows for f in families(e)})
    print("--- by source family (rows may belong to several families)")
    print("| family | rows | " + " | ".join(sets) + " |")
    for f in fams:
        tot = sum(1 for e in rows if f in families(e))
        print(f"| {f} | {tot} | " + " | ".join(str(sum(1 for i in s_ if f in families(by[i]))) for s_ in sets.values()) + " |")
    print("--- R2 sub-flags:", {k: len({i for i, v in res['R2'].items() if any(k in x[1] for x in v)}) for k in ("placeholder-id", "id-not-found", "title-no-overlap", "summary-no-overlap")})
    print("R1 reasons:", dict(collections.Counter(w for v in res["R1"].values() for u, w in v)))
    print("R5 states:", dict(collections.Counter(v["state"] for v in res["R5"].values())))
    st = collections.Counter()
    for e in rows:
        if e["id"] in legacy:
            for r in e["references"]:
                c = cget(r["url"]) if not arxiv_id(r["url"]) else {"status": "arxiv-cache"}
                st[str(c.get("status") if c else "missing")] += 1
    print("legacy ref fetch outcomes:", dict(st.most_common()))
    print("R3 threshold", R3_THRESHOLD, "; reuse distribution: >=5:", sum(1 for v in res["url_reuse"].values() if v >= 5),
          ">=10:", sum(1 for v in res["url_reuse"].values() if v >= 10), ">=20:", sum(1 for v in res["url_reuse"].values() if v >= 20))
    for u, n in sorted(res["url_reuse"].items(), key=lambda x: -x[1])[:12]:
        print(" ", n, u)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"fetch-arxiv": cmd_fetch_arxiv, "fetch-legacy": cmd_fetch_legacy, "run": cmd_run, "controls": cmd_controls, "stats": cmd_stats}[cmd]()
```

## Appendix B - samples.py

```python
import sys,json,collections
sys.path.insert(0,r'C:/Users/emman/AppData/Local/Temp/claude/C--repos-genai-incidents/0cbeb36b-c08c-48b9-a667-1bb2a887549c/scratchpad/refaudit')
import refaudit as R
from urllib.parse import urlparse
rows=R.load(); by={e['id']:e for e in rows}; leg={e['id'] for e in rows if R.is_legacy(e)}
res=json.load(open(R.SCRATCH/'results.json',encoding='utf-8'))
t=lambda e:e['title'][:70].replace('|','/')
def sample(k,n_leg,n_other,fmt):
    ids=sorted(res[k]); L=[i for i in ids if i in leg][:n_leg]; O=[i for i in ids if i not in leg][:n_other]
    out=[]
    for i in L+O: out.append(fmt(i))
    return out
print('### R1 sample')
for l in sample('R1',6,4,lambda i:f"| {by[i]['id']} | {'legacy' if i in leg else ''} | {by[i]['quality_tier']} | {t(by[i])} | {res['R1'][i][0][0]} | {res['R1'][i][0][1]} |"): print(l)
print('### R1 top hosts', collections.Counter(urlparse(u).netloc for v in res['R1'].values() for u,w in v).most_common(8))
print('### R2 all')
for i,v in res['R2'].items(): print(f"| {i} | {t(by[i])} | {v[0][0]} | {'+'.join(v[0][1])} | {(v[0][2] or '(no such paper)')[:70]} |")
print('### R3'); 
for u,n in sorted(res['url_reuse'].items(),key=lambda x:-x[1])[:12]: print(n,u)
print('### R4 sample')
for l in sample('R4',5,5,lambda i:f"| {i} | {'legacy' if i in leg else ''} | {t(by[i])} | {res['R4'][i][0][0][:80]} |"): print(l)
print('### R4 top hosts',collections.Counter(urlparse(u).netloc for v in res['R4'].values() for u,tp in v).most_common(8))
print('### R5 legacy trips')
for i,v in res['R5'].items():
    if v['state']=='TRIP': print(f"| {i} | {by[i]['quality_tier']} | {t(by[i])} | {', '.join(v['missing'])} | {v['sources_with_text']} |")
```

## Appendix C - controls output (run 2026-10-14)

```
PASS R1 positive: risk.net homepage trips
PASS R1 positive: msrc root trips
PASS R1 positive: usenix conference index trips
PASS R1 positive: uber /blog/engineering/ trips
PASS R1 negative: techcrunch article does not trip
PASS R1 negative: cve.org record (query) does not trip
PASS R1 KNOWN BLIND SPOT: homepage with ?lang=en does NOT trip (input that makes R1 fail)
PASS R2 positive: INC-03004 https://arxiv.org/abs/2501.01234 trips -> ['placeholder-id', 'title-no-overlap', 'summary-no-overlap']
PASS R2 positive: INC-03570 https://arxiv.org/abs/2408.00000 trips -> ['placeholder-id', 'id-not-found']
PASS R2 positive: INC-03444 https://arxiv.org/abs/2407.00000 trips -> ['placeholder-id', 'id-not-found']
PASS R2 negative: INC-04975 https://arxiv.org/abs/2307.15043 ('Universal and Transferable Adversarial Attacks on ') -> []
PASS R2 negative: INC-04474 https://arxiv.org/abs/2310.04451 ('AutoDAN: Generating Stealthy Jailbreak Prompts on ') -> []
PASS R2 negative: INC-04795 https://arxiv.org/abs/2310.08419 ('Jailbreaking Black Box Large Language Models in Tw') -> []
PASS R2 placeholder positive 2408.00000
PASS R2 placeholder negative 2402.12336
PASS R2 synthetic: unrelated title vs neutron-star title trips
PASS R2 synthetic: matching title does not trip
PASS R3 control: URL on 10 rows -> flagged=True
PASS R3 control: URL on 9 rows -> flagged=False
PASS R4 positive: INC-02353 msrc root (type research) trips
PASS R4 negative: research ref on arxiv.org/abs/.. does not trip
PASS R4 negative: type news is out of scope
PASS R4 KNOWN BLIND SPOT: non-paper page on a paper host (arxiv.org/list/cs.CR/new) does NOT trip
PASS R5 positive: figures absent from fetched source -> TRIP
PASS R5 negative: '$8 million', '40 percent', '3 days' in source -> ok (normalisation)
PASS R5 undetermined: no fetched text is NOT a trip
PASS R5 tamper control on real row INC-04179: appended figures -> TRIP
ALL CONTROLS PASS
```
