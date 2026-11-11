# D130-3a: reference remediation, 2026-11-11 (the 6 deferred rows + batch 1 of the D130-3 list)

**Agent-suggested, not human-reviewed.** Every change below awaits the user's re-review (ruling D130(c)); every demoted
row carries a curation-override note saying so. Scope: the 6 rows D130-2 deferred (INC-01015, INC-01291, INC-01589,
INC-02471, INC-02871, INC-04207; ruling D139) plus batch 1 (32 rows) of the D130-3 target list, `list.json`. Batches 2-4 (94 rows) are
NOT done here. No third-party page text is copied here beyond page titles and the short tokens that link a fetched page to a
row.

Method (the D130-2 method, `docs/audits/reference-audit-2026-10-15/`): a URL is written into the corpus only if this session
fetched it through `ingest/common.fetch_once` (robots.txt, per-host rate limit, identifying User-Agent; `fetch_evidence.py`) and
the fetched page names the incident; `export_evidence.py` re-checks every token and aborts on a missing one. Discovery used
direct URL guesses, the publishers' own index pages and publisher/news site-search pages, fetched the same way; no general search engine
was usable (Bing returned unrelated pages, DuckDuckGo a bot challenge, Brave HTTP 429). References that are only REMOVED need no
replacement when the row keeps other references. **Untouched (kept) references were fetched in full on rows with <= 15 kept references
and sampled (method in the section "Evidence for the references the remove-rows kept") on larger rows**; this was added after the first
report, on the foreman's rule C. All changes are
`data/curation_overrides.json` entries generated from `d1303a_spec.py` by `build_overrides.py`; `data/incidents.json` and every other
`data/*.json` is build output and was not edited.

## The target list (`list.json`) and its reconciliation

`python -I docs/audits/reference-audit-2026-11-11/derive_list.py` (offline, deterministic, reads `data/incidents.json` at base
64109452 via `git show`; exits 1 unless it derives 126 + 6).

| step | rows |
|---|---|
| R1 or R2 rows in the detection report (run at c80b7e61; re-derived on the D130-2 base 589376db: `r1()` verbatim + the report's 11 R2 rows) | 156 |
| minus D130-2's legacy-seed rows (`INC-<n>` / `LEGACY-INC-<n>`) | -30 |
| = non-legacy R1/R2 rows | 126 |
| same rule run on 64109452 | 126 non-legacy (125 trip R1; INC-04383 trips R2 only) |
| plus the 6 rows D130-2 deferred | +6 |
| **list.json** | **132** (batch 0 = the 6 deferred; batches 1-4 = 32, 32, 31, 31 in stable ID order) |

Reconciliation: the numbers agree exactly (156 - 30 = 126), with two clarifications. (1) The 126 are the rows whose
source_ids carry no legacy `INC-<n>` id; INC-04383 (ATLAS case AML.CS0016) is the one R2-only row among them (its arXiv
reference is a background citation, title-no-overlap), the other non-legacy R2 row, INC-05052, also trips R1. (2) Of the 30
legacy rows, 8 left the R1/R2 set because D130-2 replaced their references; the other 22 still trip the rule at 64109452
(10 unverified, 3 unchanged, 6 deferred, 3 fixed rows whose R2 flag is a static row list), so a naive rerun of R1 over current data
gives 148 = 126 + 22, not 132. The 6 deferred rows are in this batch; the 3 D130-2 "unchanged" rows (INC-04067, INC-04142,
INC-08181: two over-merges and one false positive) stay out. No refresh added or removed a target. Batch 1 contains INC-04383 and
INC-05052 (the two non-legacy R2 rows) by ID order.

## Outcome (the 6 deferred rows + batch 1 of the D130-3 list = 38 rows)

| outcome | rows | ids |
|---|---|---|
| fixed (flagged reference removed) | 29 | INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207, INC-00021, INC-01194, INC-01348, INC-01553, INC-01724, INC-02076, INC-02150, INC-02347, INC-02505, INC-02516, INC-02761, INC-02800, INC-02864, INC-03209, INC-03276, INC-03292, INC-03423, INC-04285, INC-04383, INC-04959, INC-05009, INC-05421, INC-05425 |
| fixed (replaced) | 4 | INC-01641, INC-02498, INC-03212, INC-03248 |
| unverified | 2 | INC-00570, INC-03573 |
| unchanged (false positive) | 2 | INC-00864, INC-05052 |
| unchanged (deferred to WS4-T19) | 1 | INC-01600 |
| **total** | **38** | |

## Per-row outcomes

| id | batch | tier before | outcome | flagged URL (rule) -> fetch result 2026-11-11 | change |
|---|---|---|---|---|---|
| INC-01015 | 0 | curated | fixed (flagged reference removed) | `https://flowiseai.com` (homepage) -> HTTP 200, title "Flowise - Build AI Agents, Visually" | reference(s) removed; demoted to auto |
| INC-01291 | 0 | curated | fixed (flagged reference removed) | `https://www.langchain.com/` (homepage) -> HTTP 200, title "LangChain: the open agent platform to own your intelligence" | reference(s) removed; demoted to auto |
| INC-01589 | 0 | curated | fixed (flagged reference removed) | `https://openclaw.ai/blog` (depth1-non-slug) -> HTTP 200, title "Blog - OpenClaw" | reference(s) removed; demoted to auto |
| INC-02471 | 0 | curated | fixed (flagged reference removed) | `https://github.com/MaccariTA` (depth1-non-slug) -> HTTP 200, title "MaccariTA (MaccariTA) · GitHub" | reference(s) removed; demoted to auto |
| INC-02871 | 0 | curated | fixed (flagged reference removed) | `https://github.com/Y4tacker` (depth1-non-slug) -> HTTP 200, title "Y4tacker (Y4tacker) · GitHub" | reference(s) removed; demoted to auto |
| INC-04207 | 0 | curated | fixed (flagged reference removed) | `https://arxiv.org/abs/2402.06627` (R2 arXiv id/title mismatch) -> HTTP 200, title "[2402.06627] Feedback Loops With Language Models Drive In-Context Rewa" | reference(s) removed; demoted to auto |
| INC-00021 | 1 | reviewed | fixed (flagged reference removed) | `http://trezor.com` (homepage) -> HTTP 200, title "Сейфы: лучшие модели и новинки ТРЕЗОР" | reference(s) removed; demoted to auto |
| INC-00570 | 1 | reviewed | unverified | `https://www.aim.security/news` (depth1-non-slug) -> refused (robots.txt disallowed or unverifiable; fail-closed) | `status: unverified` (`no-confirmed-source`); references, title, tier untouched. The only reference is the publisher's news index (R1). Searched 2026-11-11 (all through fetch_once, or a search page where noted): aim.security/news and /lp/aim-labs-echoleak-blog-post and /sitemap.xml (robots.txt unverifiable, HTTP 403, so refused fail-closed); a web.archive.org snapshot of aim.security/news (lists EchoLeak, CurXecute and ASCII Smuggling items only, no 'variants' post); The Hacker News site search for 'EchoLeak', 'Aim Labs' and 'scope violation' (only the original EchoLeak coverage and Aim Labs' CurXecute Cursor RCE, CVE-2025-54135); the NVD 2.0 API keyword search 'EchoLeak' (0 results); BleepingComputer search for 'EchoLeak' (no results page content); Bing through WebFetch (returned unrelated 'AIM' pages) and DuckDuckGo (bot challenge). The only Aim Labs follow-up found is CurXecute, which is its own row INC-02469, and the original EchoLeak is INC-00924; pointing this row at either would create a duplicate. Nothing found names 'continued research into variants across multiple enterprise copilots'. Not found after this search; the search was limited to those routes. |
| INC-00864 | 1 | reviewed | unchanged (false positive) | `https://cybersecuritynews.com/flowise-vulnerability/` -> HTTP 200, title "Critical Vulnerability In Flowise Allows Remote Command Execution Via " | R1 false positive: an article (one-hyphen slug) on the OX Security finding that Anthropic's MCP SDKs allow command execution; it names the incident. |
| INC-01194 | 1 | reviewed | fixed (flagged reference removed) | `https://trysixth.com/` (homepage) -> HTTP 200, title "Sixth" | reference(s) removed; demoted to auto |
| INC-01348 | 1 | reviewed | fixed (flagged reference removed) | `https://www.llamaindex.ai/` (homepage) -> HTTP 200, title "LlamaIndex / AI Agents for Document OCR + Workflows" | reference(s) removed; demoted to auto |
| INC-01553 | 1 | reviewed | fixed (flagged reference removed) | `https://ollama.com/` (homepage) -> HTTP 200, title "Ollama · Run AI models locally and in the cloud" | reference(s) removed; demoted to auto |
| INC-01600 | 1 | reviewed | unchanged (deferred to WS4-T19) | `https://www.reco.ai/newsroom` -> HTTP 200, title "Reco Newsroom: AI Security News & Updates" | unchanged, deferred (bounce #1 lesson i): the only on-topic source found, the Reco OpenClaw article, is already INC-01589's first reference, so re-pointing this row would create a duplicate; the row is likely a duplicate/over-merge of INC-01589 (the OpenClaw crisis; its source_ids also carry a second seed id). Its flagged reco.ai/newsroom reference stays as found. Routed to WS4-T19 and to user re-review. |
| INC-01641 | 1 | reviewed | fixed (replaced) | `https://www.pillar.security/blog` (depth1-non-slug) -> HTTP 200, title "Pillar Blog / Latest stories about AI Security" | reference -> `https://www.pillar.security/blog/the-agent-security-paradox-when-trusted-commands-in-cursor-become-attack-vectors` (fetched 200, names the incident); description kept (supported by the page); demoted to auto |
| INC-01724 | 1 | reviewed | fixed (flagged reference removed) | `https://raytha.com` (homepage) -> HTTP 200, title "Raytha: the open source .NET CMS for developers who ship" | reference(s) removed; demoted to auto |
| INC-02076 | 1 | reviewed | fixed (flagged reference removed) | `https://www.kxan.com/driverless/` (depth1-non-slug) -> HTTP 403 | reference(s) removed; demoted to auto |
| INC-02150 | 1 | reviewed | fixed (flagged reference removed) | `http://openairinterface.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed); `https://cellularsecurity.org/ransacked` (depth1-non-slug) -> HTTP 200, title "Cellular Security / Florida Institute for Cybersecurity Research"; `https://openairinterface.org/` (homepage) -> HTTP 200, title "OpenAirInterface"; kept: `https://cellularsecurity.org/ransacked` -> HTTP 200, title "Cellular Security / Florida Institute for Cybersecurity Research" | reference(s) removed; demoted to auto |
| INC-02347 | 1 | reviewed | fixed (flagged reference removed) | `https://iocharger.com` (homepage) -> HTTP 200, title "OCPP EV Charger Manufacturer / Iocharger / Fleet Charging" | reference(s) removed; demoted to auto |
| INC-02498 | 1 | reviewed | fixed (replaced) | `https://embracethered.com/blog/` (depth1-non-slug) -> HTTP 200, title "Embrace The Red · Embrace The Red" | reference -> `https://embracethered.com/blog/posts/2024/deepseek-ai-prompt-injection-to-xss-and-account-takeover/` (fetched 200, names the incident); title, description re-derived; demoted to auto |
| INC-02505 | 1 | reviewed | fixed (flagged reference removed) | `http://dify.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed) | reference(s) removed; demoted to auto |
| INC-02516 | 1 | reviewed | fixed (flagged reference removed) | `https://dify.ai` (homepage) -> HTTP 200, title "Dify - The Platform for Production-Ready Agentic Workflows" | reference(s) removed; demoted to auto |
| INC-02761 | 1 | reviewed | fixed (flagged reference removed) | `http://langchain-chatglm-webui.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed) | reference(s) removed; demoted to auto |
| INC-02800 | 1 | reviewed | fixed (flagged reference removed) | `https://python.langchain.com/docs/security/` (index-segments) -> HTTP 200, title "LangChain overview - Docs by LangChain" | reference(s) removed; demoted to auto |
| INC-02864 | 1 | reviewed | fixed (flagged reference removed) | `https://mattermost.com/security-updates` (depth1-non-slug) -> HTTP 200, title "Security Updates / Mattermost Documentation" | reference(s) removed; demoted to auto |
| INC-03209 | 1 | reviewed | fixed (flagged reference removed) | `https://www.microsoft.com/en-us/security/blog/` (index-segments) -> HTTP 200, title "Microsoft Security Blog" | reference(s) removed; demoted to auto |
| INC-03212 | 1 | reviewed | fixed (replaced) | `https://unit42.paloaltonetworks.com/` (homepage) -> HTTP 200, title "Unit 42 - Latest Cybersecurity Research / Palo Alto Networks" | reference -> `https://unit42.paloaltonetworks.com/npm-supply-chain-attack/` (fetched 200, names the incident); title, description, affected re-derived; demoted to auto |
| INC-03248 | 1 | reviewed | fixed (replaced) | `https://www.sysdig.com/threat-research` (depth1-non-slug) -> HTTP 200, title "Threat Research / Sysdig" | reference -> `https://www.sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes` (fetched 200, names the incident); description kept (supported by the page); demoted to auto |
| INC-03276 | 1 | reviewed | fixed (flagged reference removed) | `https://dotapp.uk` (homepage) -> HTTP 200, title "Try out the Dot beta" | reference(s) removed; demoted to auto |
| INC-03292 | 1 | auto | fixed (flagged reference removed) | `https://phcode.dev/` (homepage) -> HTTP 200, title "Phoenix Code - Free Open Source Code Editor / Successor to Brackets"; `https://www.postbox-inc.com/` (homepage) -> HTTP 200, title "The Power Email App - Postbox" | reference(s) removed; already auto |
| INC-03423 | 1 | reviewed | fixed (flagged reference removed) | `https://monica.im/desktop` (depth1-non-slug) -> HTTP 200, title "Monica - Your GPT AI Assistant Chrome Extension" | reference(s) removed; demoted to auto |
| INC-03573 | 1 | reviewed | unverified | `https://www.anthropic.com/research` (depth1-non-slug) -> HTTP 200, title "Research \ Anthropic" | `status: unverified` (`no-confirmed-source`); references, title, tier untouched. The only reference is the publisher's research index (R1). Searched 2026-11-11 through fetch_once: anthropic.com/research, /news, /research/team/frontier-red-team, red.anthropic.com, /news/detecting-countering-misuse-aug-2025 and /news/building-safeguards-for-claude (all HTTP 200; none contains 'spear-phishing', 'spear phishing' or 'phishing' in a study of that name; the August 2025 misuse report names no such study); The Hacker News site search for 'Anthropic spear-phishing' and 'Anthropic Claude phishing' (reports of 2025-2026 Claude misuse, none a 2024 Frontier Threats Red Team spear-phishing scaling study). No search engine was available. The row also carries a second seed id (VTR-anthropic-election-influence-study-2024, an election-influence study) with no source either. Not found after this search; the search was limited to those routes. |
| INC-04285 | 1 | reviewed | fixed (flagged reference removed) | `https://premiumaddons.com/change-log/` (depth1-non-slug) -> HTTP 200, title "Premium Addons PRO Changelog / Premium Addons for Elementor" | reference(s) removed; demoted to auto |
| INC-04383 | 1 | reviewed | fixed (flagged reference removed) | `https://arxiv.org/abs/2103.03874` -> HTTP 200, title "[2103.03874] Measuring Mathematical Problem Solving With the MATH Data" | reference(s) removed; demoted to auto |
| INC-04959 | 1 | reviewed | fixed (flagged reference removed) | `https://www.oligo.security/shelltorch` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |
| INC-05009 | 1 | reviewed | fixed (flagged reference removed) | `https://docs.dependencytrack.org/changelog/` (depth1-non-slug) -> HTTP 200, title "Change Log / Dependency-Track" | reference(s) removed; demoted to auto |
| INC-05052 | 1 | reviewed | unchanged (false positive) | `https://real-gradients.github.io/` -> HTTP 200, title "Real Attackers Don't Compute Gradients"; `https://arxiv.org/abs/2212.14315` -> HTTP 200, title "[2212.14315] "Real Attackers Don't Compute Gradients": Bridging the Ga" | R1/R2 false positive: the dedicated site and paper behind ATLAS case AML.CS0032 (screenshots of 100 evasive phishing webpages, MLSEC anti-phishing analysis); the R2 title-overlap flag is a token artefact of a generic row title. |
| INC-05421 | 1 | reviewed | fixed (flagged reference removed) | `http://abna24.com/b4xD` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |
| INC-05425 | 1 | reviewed | fixed (flagged reference removed) | `http://abna24.com/b8b9` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |

## Field-level delta (working agreement 2)

Control = committed data at base 64109452; new = this branch's build. Entry count 15821 -> 15821; ID set equal: True; ID order equal: True; rows with any difference: 35 (= the 29 remove rows + 4 replace rows + 2 unverified rows); rows outside them with any difference: 0; unintended field moves: 0.

Envelope / `data/stats.json` keys that moved (declared set; any other key would be a defect, and none moved):

| key | before | after | cause |
|---|---|---|---|
| `generated` | 2026-11-08 | 2026-11-11 | build date stamp |
| `incident_count` | 15782 | 15780 | the 2 newly unverified rows leave the count |
| `landmark_count` | 2062 | 2056 | the 6 curated deferred rows leave the landmark tier by demotion (D130(c)) |
| `unverified_count` | 10 | 12 | the 2 newly unverified rows |

| field | rows | kind | justification |
|---|---|---|---|
| `affected` | 1 (INC-03212) | intended | INC-03212: package names the source does not name dropped |
| `confidence` | 20 | derived | `_derive_confidence`: curated/reviewed -> high; 2+ sources with a CVE stay high, 2+ sources or a CVE/CVSS give medium. Follows quality_tier only |
| `description` | 2 (INC-02498, INC-03212) | intended | re-derived from the confirmed source; claims the source does not support dropped |
| `discovery_method` | 3 (INC-02471, INC-02871, INC-04207) | intended | landmark-only label (integrity check): its override line is dropped for INC-04207 (D139(b)) and for INC-02471, INC-02871 (same mechanism, same reason; see Declared knock-ons) |
| `last_seen` | 35 | derived | history stamp: content changed (build date) |
| `quality_tier` | 32 | intended | ruling D130(c): every row whose reference is replaced or removed demotes to auto; never promoted. INC-03292 was already auto |
| `references` | 33 | intended | the D130-3a change itself |
| `status` | 2 (INC-00570, INC-03573) | intended | D130(b): unverified |
| `status_reason` | 2 (INC-00570, INC-03573) | intended | {code: no-confirmed-source, as_of: 2026-11-11} |
| `tier` | 6 (INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207) | derived | `_derive_tier`: curated -> landmark, so the 6 curated deferred rows (no aiid_id, corpus not ai-harm) become feed. Follows quality_tier only |
| `title` | 2 (INC-02498, INC-03212) | intended | re-derived from the confirmed source so title and description agree (bounce lesson iii) |
| `updated` | 35 | derived | history stamp: content changed (build date) |

`tier` landmark -> feed on 6 rows: INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207. `landmark_count` 2062 -> 2056. INC-02076 (reviewed) is demoted but stays landmark through its `aiid_id`.

`confidence` moved on 20 rows (INC-00021 high->medium, INC-01194 high->medium, INC-01641 high->low, INC-02076 high->medium, INC-02498 high->medium, INC-02505 high->medium, INC-02516 high->medium, INC-02761 high->medium, INC-02800 medium->low, INC-03209 high->low, INC-03212 high->low, INC-03248 high->low, INC-03276 high->medium, INC-04207 high->medium, INC-04285 high->medium, INC-04383 high->low, INC-04959 high->medium, INC-05009 high->medium, INC-05421 high->low, INC-05425 high->low).

Full per-row before/after: `delta-2026-11-11.json`.

## Evidence for the references the remove-rows kept (foreman rule C)

Rule as applied: **untouched references were fetched in full on rows with <= 15 kept references and sampled (first 5 + last 5 + 5 chosen by `random.Random(<row id>).sample` over the rest) on larger rows.** Every fetch went through `ingest/common.fetch_once`; `nvd.nist.gov/vuln/<CVE>` and `osv.dev/vulnerability/<id>` are JavaScript shells, so the same record was fetched from the NVD 2.0 API (7 s per request) / the OSV API, and the evidence file names both URLs. `kept_refs.py` does the work; `verify.py` re-derives the selection from the built rows and fails if a kept reference on a small row has no record, a large row's sample differs, or the tally disagrees (proved to fire by five mutations of a copy of the evidence file).

- Rows fully fetched: 24; rows sampled: 5 (INC-01015, INC-01291, INC-01348, INC-02347, INC-02864).
- **Tally (193 references fetched): evidenced 153 (HTTP 200 and an identifying token found: 111 by CVE/GHSA id, 42 by product keyword); dead-or-blocked 23 (kept, for the WS4 link-health task); page-without-token 17 (HTTP 200, no token: kept, for review); removal candidates 1 (below); no reference was removed on this evidence.**
- Four NVD pages for INC-02347 returned HTTP 503 on the first pass and 200 on a retry; the committed record is the retry.

| row | kept | method | evidenced | dead-or-blocked | page-without-token |
|---|---|---|---|---|---|
| INC-00021 | 2 | all | 2 | 0 | 0 |
| INC-01194 | 2 | all | 2 | 0 | 0 |
| INC-01348 | 119 | sample of 15 | 14 | 0 | 1 |
| INC-01553 | 11 | all | 8 | 1 | 2 |
| INC-01724 | 4 | all | 4 | 0 | 0 |
| INC-02076 | 14 | all | 8 | 6 | 0 |
| INC-02150 | 12 | all | 12 | 0 | 0 |
| INC-02347 | 17 | sample of 15 | 7 | 0 | 8 |
| INC-02505 | 5 | all | 4 | 1 | 0 |
| INC-02516 | 2 | all | 2 | 0 | 0 |
| INC-02761 | 3 | all | 3 | 0 | 0 |
| INC-02800 | 4 | all | 4 | 0 | 0 |
| INC-02864 | 74 | sample of 15 | 15 | 0 | 0 |
| INC-03209 | 2 | all | 1 | 1 | 0 |
| INC-03276 | 3 | all | 2 | 1 | 0 |
| INC-03292 | 4 | all | 4 | 0 | 0 |
| INC-03423 | 7 | all | 7 | 0 | 0 |
| INC-04285 | 2 | all | 1 | 0 | 1 |
| INC-04383 | 5 | all | 1 | 2 | 2 |
| INC-04959 | 6 | all | 5 | 0 | 1 |
| INC-05009 | 5 | all | 3 | 0 | 2 |
| INC-05421 | 6 | all | 2 | 4 | 0 |
| INC-05425 | 5 | all | 1 | 4 | 0 |
| INC-01015 | 442 | sample of 15 | 14 | 1 | 0 |
| INC-01291 | 177 | sample of 15 | 15 | 0 | 0 |
| INC-01589 | 9 | all | 7 | 2 | 0 |
| INC-02471 | 2 | all | 2 | 0 | 0 |
| INC-02871 | 2 | all | 2 | 0 | 0 |
| INC-04207 | 1 | all | 1 | 0 | 0 |

Not evidenced, by outcome (all kept: the rule removes only an exact R1-shaped or R2-flagged reference, and none of these is):

- dead or blocked (4xx/5xx, robots refusal, error): WS4 link-health:
  - INC-01553 `https://https://github.com/ollama/ollama` (robots-refused)
  - INC-02076 `https://www.dailymail.co.uk/news/article-15607199/waymo-car-austin-terror-attack-shooting-victims.html` (403)
  - INC-02076 `https://www.axios.com/local/austin/2026/03/02/waymo-vehicle-blocks-ems-austin-mass-shooting` (403)
  - INC-02076 `https://www.kxan.com/investigations/city-of-austin-will-push-for-new-driverless-vehicle-legislation/` (403)
  - INC-02076 `https://www.wkrn.com/news/local-news/nashville/new-video-shows-waymo-handling-busy-traffic-times-in-downtown-nashville/` (403)
  - INC-02076 `https://www.ft.com/content/9c3da2e4-a938-45c4-8fb8-021aca5e66b8` (403)
  - INC-02076 `https://www.koin.com/news/portland/self-driving-vehicle-company-waymo-will-launch-fleet-in-portland/` (403)
  - INC-02505 `https://gist.github.com/Cristliu/216ddbadaf3258498c93d408683ecabd` (404)
  - INC-03209 `https://atlas.mitre.org/studies/AML.CS0042` (404)
  - INC-03276 `https://github.com/EDMPL/Vulnerability-Research/tree/main/CVE-2024-57783` (404)
  - INC-04383 `https://atlas.mitre.org/studies/AML.CS0016` (404)
  - INC-04383 `https://lspace.swyx.io/p/reverse-prompt-eng` (robots-refused)
  - INC-05421 `https://www.aa.com.tr/ar/الدول-العربية/الحوثي-تعلن-استهداف-قاعدة-جوية-سعودية-بطائرة-مسيرة/2219972` (error)
  - INC-05421 `https://www.tasnimnews.com/ar/news/2021/04/23/2489918/%d8%b3%d9%84%d8%a7%d8%ad-%d8%a7%d9%84%d8%ac%d9%88-%d8%a7%d9%84%db%` (robots-refused)
  - INC-05421 `https://www.tasnimnews.com/ar/news/2021/04/25/2490929/%d8%b3%d9%84%d8%a7%d8%ad-%d8%a7%d9%84%d8%ac%d9%88-%d8%a7%d9%84%db%` (robots-refused)
  - INC-05421 `https://www.alalamtv.net/news/5553693/سلاح-الجو-اليمني-المسير-يشن-هجومًا-على-قاعدة-الملك-خالد` (robots-refused)
  - INC-05425 `https://www.tasnimnews.com/ar/news/2021/05/21/2507203/%d8%a7%d9%84%d8%b9%d9%85%db%8c%d8%af-%d8%b3%d8%b1%db%8c%d8%b9-%d8%` (robots-refused)
  - INC-05425 `https://www.alalamtv.net/news/5605668/العميد-سريع-يعلن-إسقاط-مقاتلة-تابعة-لسلاح-الجو-السعودي` (robots-refused)
  - INC-05425 `https://www.alahednews.com.lb/fastnewsdetails.php?fstid=120024` (404)
  - INC-05425 `https://www.arabstoday.net/36/124022-الحوثيون-يعلنون-إسقاط-مقاتلة-تابعة-لسلاح-الجو-السعودي` (robots-refused)
  - INC-01015 `https://www.vulncheck.com/advisories/flowise-auth-command-execution-and-sandbox-bypass-via-puppeteer-and-playwright-pack` (404)
  - INC-01589 `https://x.com/0xacb/status/2016913750557651228` (robots-refused)
  - INC-01589 `https://atlas.mitre.org/studies/AML.CS0050` (404)
- HTTP 200 but no identifying token in the page text (redirect stubs, JS shells, wiki/bounty pages): review:
  - INC-01348 `https://huntr.com/bounties/1bce0d61-ad03-4b22-bc32-8f99f92974e7` (200)
  - INC-01553 `https://kb.cert.org/vuls/id/518910` (200)
  - INC-01553 `https://huntr.com/bounties/172df98b-07cd-41ea-a628-366f8cd525c0` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43649/` (200)
  - INC-02347 `https://csirt.divd.nl/DIVD-2024-00035/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43650/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43651/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43653/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43655/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43656/` (200)
  - INC-02347 `https://csirt.divd.nl/CVE-2024-43657/` (200)
  - INC-04285 `https://www.wordfence.com/threat-intel/vulnerabilities/id/82e5fd9f-9a1f-4a4c-ac06-61bf65e3c8ab?source=cve` (200)
  - INC-04383 `https://arxiv.org/abs/2110.14168` (200)
  - INC-04383 `https://research.nccgroup.com/2022/12/05/exploring-prompt-injection-attacks` (200)
  - INC-04959 `http://packetstormsecurity.com/files/175095/PyTorch-Model-Server-Registration-Deserialization-Remote-Code-Execution.html` (200)
  - INC-05009 `https://github.com/showdownjs/showdown/wiki/Markdown%27s-XSS-Vulnerability-%28and-how-to-mitigate-it%29` (200)
  - INC-05009 `https://github.com/showdownjs/showdown/wiki/Markdown's-XSS-Vulnerability-(and-how-to-mitigate-it)` (200)

Removal CANDIDATES (kept, for user re-review; not removed):

- INC-04383 `https://arxiv.org/abs/2110.14168`: off-topic sibling citation (ATLAS footnote [2], 'Training Verifiers to Solve Math Word Problems'): HTTP 200, does not name the incident; not R1-shaped and not R2-flagged, so kept.

Notable: `INC-01553` carries a malformed reference `https://https://github.com/ollama/ollama` (double scheme); `INC-04383`'s NCC Group URL now serves the research index.


## Declared knock-ons and headline deltas (bounce lesson iv)

- `incident_count` 15,782 -> 15,780: exactly the 2 newly unverified rows (INC-00570, INC-03573); `unverified_count` 10 -> 12.
- `landmark_count` 2,062 -> 2,056: the 6 curated deferred rows (INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207) are
  demoted to `quality_tier: auto`, which makes them `tier: feed` (`_derive_tier`: curated -> landmark; no `aiid_id`, corpus not `ai-harm`).
  INC-04207: tier landmark -> feed and confidence high -> medium, as the D139 gate advised.
- `confidence` moves on 20 rows (`_derive_confidence`, follows the demotion only; the list is in the delta table).
- **`discovery_method` on 3 rows, one more than the D139 premise.** The integrity check refuses `discovery_method` outside the
  landmark tier. INC-04207's value came only from its INC-030 override line (dropped, per D139(b)). INC-02471 and INC-02871 (both curated
  landmark, demoted) carried the same kind of label from their own CVE override entries ("Advisory credits ... as the finder"); once
  demoted they would fail the check, so the `discovery_method` key is dropped from those two entries as well and its text is kept in
  `_d130_3a_prior_note`. This is the same mechanism and reason as D139(b) but names two rows the ruling did not; it is flagged for the
  user's re-review. Nothing else in those entries changed. `fields_clear` was not needed (no other source supplies the value).
- No row was deleted; no ID changed; entry count 15,821 and the ID set and order are unchanged.

## Rows whose description (or affected) changed: queue for a SEPARATE WS2 re-label (bounce lesson v; NOT done here)

INC-02498 (title, description) and INC-03212 (title, description, affected). The classifier-derived labels (`attack_vector`, `severity`,
`owasp_*`, `nist_ai_rmf`, `mitre_atlas*`, `category`, `tags`, ...) keep their base values on these two rows (the delta shows none moved)
and may reflect the old wording: INC-02498 (was "session/token handling weakness", now prompt injection to XSS to token theft) and
INC-03212 (was "LLM generated malicious scripts ... Crowdstrike, Postman, Zapier", now one bash script assessed LLM-generated). The other 33 changed
rows kept their text; their labels are unaffected.

## Observations and follow-ups (not actioned)

- **ATLAS case pages return 404 to our fetcher** (`atlas.mitre.org/studies/AML.CS0016`, `/AML.CS0032`, and `/studies`), although they are
  the canonical first reference of every ATLAS-sourced row. Not an R1/R2 flag; reported for the WS4 link-health task.
- **Over-merge stubs on single-incident rows.** INC-02498's source_ids include `RES-bing-copilot-zero-click-2024`, INC-01600's include
  `RES-reco-cursor-bg-2025`, and INC-03573's include `VTR-anthropic-election-influence-study-2024`: separate incidents, apparently merged on a shared
  index URL. The rows' titles and text describe only one incident each, so they were fixed/marked on that incident; the merge itself is a WS4-T19 item.
- **Date lag.** INC-02498 is dated 2025-01 but the confirmed page is dated 2024-11-29; left as found (a date change is outside D130-3a, like
  the D130-2 follow-up g).
- INC-00864's cybersecuritynews.com article and INC-05052's paper site were kept (R1/R2 false positives); INC-02150 keeps
  `https://cellularsecurity.org/ransacked` (fetched, names CVE-2024-24426) while its two homepages were removed.
- INC-00570 and INC-03573 stay unverified after a second, wider search (the routes tried are listed in each row's override note and in the
  per-row table above). aim.security is unfetchable under the fail-closed robots rule (robots.txt returns HTTP 403); INC-00570 may be
  re-checked if that host's robots.txt becomes verifiable. "Not found" here means not found by those routes, not proven absent.
- Dead and blocked kept references (listed in the evidence section) are for the WS4 link-health task; none was removed.
- **INC-01600 deferred (bounce #1, lesson i).** I first replaced its flagged `reco.ai/newsroom` with the Reco OpenClaw article, but that article is
  INC-01589's first reference at base, so the row would have duplicated INC-01589. It is reverted: the built row is byte-identical to base 64109452
  (flagged reference kept, tier unchanged) and is deferred to WS4-T19 and user re-review as a likely duplicate/over-merge of INC-01589.
  Reverting needed the generated outputs reset to base before the rebuild: a rebuild over the previous working tree re-stamped `updated`/`last_seen`.
- **INC-04383 removal candidate.** `https://arxiv.org/abs/2110.14168` (ATLAS footnote [2], GSM8K) is an off-topic sibling citation; it is kept
  because the rule removes only an exact R1-shaped or R2-flagged reference. Listed for user re-review.
- INC-01641 and INC-00868 are both CVE-2026-22708 (predates this branch): dedupe queue. INC-05425 and INC-05421 hold several blocked news
  references (Arabic-language sites, robots): link-health first.
- Existing refs the audit did not flag but met in passing: `research.nccgroup.com/2022/12/05/exploring-prompt-injection-attacks` (INC-04383) now
  serves an index page without the article; `lspace.swyx.io` could not be verified. Untouched.

## Reproduce

```
python -I docs/audits/reference-audit-2026-11-11/derive_list.py            # 126 + 6 = 132, exit 0
python -I docs/audits/reference-audit-2026-11-11/build_overrides.py --check # overrides file == spec (exit 0)
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py && python scripts/render_markdown.py \
  && python scripts/render_docs_stats.py && python scripts/validate.py && python scripts/lint_atlas_ids.py   # build; git status clean afterwards
python -I docs/audits/reference-audit-2026-11-11/kept_refs.py plan          # the 193 kept-reference fetches (network: `fetch`, offline: `export`)
python -I docs/audits/reference-audit-2026-11-11/verify.py                  # per-ID spec + kept-evidence check, OK 0
python -I docs/audits/reference-audit-2026-11-11/delta.py                   # delta vs 64109452, unintended []
```
