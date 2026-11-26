# D159: evaluation of hackingincidents.ai as a candidate ingest source

**Date:** 2026-11-25 · **Author:** WS0 license-auditor · **Status:** DATED RECORD,
**do-not-regenerate** (supersede with a dated update; do not rewrite). Evaluation
only: no ingest code written, no `data/*.json` or `ingest/*.json` touched, no
outreach sent. The SOURCE_LICENSES row in section 3 is a DRAFT held here; per
invariant 10 it lands in `docs/SOURCE_LICENSES.md` in the same PR as the ingest.

## VERDICT / RECOMMENDATION (first)

**Ingest facts + link only, with an MIT notice carve-out, and with a non-blocking
clarification email (draft supplied). Do NOT ingest the `quote` field; hold the
site's `summary` field out until the operator answers.** Not "do not ingest": the
site is a real, structured, primary-sourced ledger with an explicit MIT data
statement. Not "ingest verbatim": the MIT statement is a software licence
applied to a dataset, the site disclaims third-party text, and no terms page exists.

Reasons in one paragraph each:

1. **Real and not an AI-incident aggregator we already ingest.** Operator is a named
   individual (Daniel Miessler / Unsupervised Learning). It is a curated ledger of
   cyberattacks where AI was used by the attacker, built from 240 swept sources,
   mostly vendor threat-intel (144) and press (45). It cites AIID in 22 incidents and
   OECD AIM in 0; it does not cite AIAAIC or NVD. It is not a republisher of
   AIID/AIAAIC/OECD text.
2. **Licence signal is positive but narrow.** `/about/` and `/data/` both state the
   data is "published under the license of the Substrate repository: MIT License,
   Copyright (c) 2025 Daniel Miessler". The Substrate repo's GitHub API `license`
   field is `MIT` (structured, not exposed to the markdown-truncation failure) and
   the repo contains `Data/AI-Hacking-Incidents/` with the same files. MIT is
   permissive (attribution + notice), so keeping the operator's own fields under MIT
   with the notice attached follows the ATLAS/Apache precedent (SOURCE_LICENSES 3.1).
   The site also states: "Short quotes from sources are credited to their publishers
   and remain under the publishers' terms." That excludes `quote` from anything MIT
   grants.
3. **Overlap is real but minority; most entries are novel.** In a 31-entry sample,
   7 (23%) are already in our corpus as the same event (AIID/OECD-derived), 3 are
   same-theme-different-event, 21 (68%) have no match. Zero of 16 primary vendor URLs
   checked appear anywhere in our corpus, so even matched events would gain a primary
   reference. Scale: 298 incidents against a 15,845-row corpus (at most ~1.9%).

## 1. Operator and primary-vs-aggregator

- Operator: "Daniel Miessler, through Unsupervised Learning" (`/about/`, WebFetch
  2026-11-25), linked to danielmiessler.com. Sister site: offsecharnesses.ai.
  **Operator jurisdiction not established by me** (no address on the pages I read);
  Miessler is publicly associated with the US, which would put the ledger outside
  EU/UK sui generis database right, but this is UNVERIFIED and I did not test it.
  E13 reasoning (docs/audits/WS0-E13-database-right-2026-07-18.md) turns on
  maker residence; US-based maker means no UK/EU database right subsists in the
  ledger as a database. Treat as likely-not-applicable, unconfirmed.
- Nature: **secondary curator over primary vendor/government sources.** Method page:
  "This site makes no attribution of its own"; actor names are labels from the cited
  source; Confirmed grade needs at least one primary source. 384 candidates reviewed
  (184 admitted, 117 merged, 83 excluded); 298 incidents, of which 114 were carried
  over from an earlier ledger.
- Does it re-publish AIID/AIAAIC/OECD/CVE/news content? Sources page (WebFetch):
  AIID listed, swept, 22 citing incidents. OECD AIM listed, swept, 0 citing.
  AIAAIC and NVD: not listed (on that page, rendered text, method-suspect; not
  relevant to inheritance since they are simply absent from the citation graph I
  sampled). "AI Threat Watch" (aithreat.io) case files: 34 citing incidents. **That
  is a second-order upstream whose terms we do not hold** (no row in
  SOURCE_LICENSES). Inherited-terms consequence: the link to aithreat.io is fine, but
  we must not reproduce aithreat.io prose via this ledger.
- AI-generated content: the method page says extraction and grading may be done by
  "the person or agent"; it does not say how prose is produced. Treat the `summary`
  text as possibly machine-written and of unknown provenance. Grade agreement between
  extractor and grader is 213/298 (71.5%), so the confidence field is a weak label.
  **Do not use it as ground truth** (same constraint as our heuristic-label warning).

## 2. Terms, licence, robots, export

| Item | Finding | Method / source kind |
|---|---|---|
| Licence statement | `/data/`: *"The data is published under the license of the Substrate repository: MIT License, Copyright (c) 2025 Daniel Miessler."* `/about/` says the same. | WebFetch (markdown-converted rendered text) of `/about/`, `/data/`. Positive finding. |
| Repo licence | `api.github.com/repos/danielmiessler/Substrate` `license.spdx_id` = `MIT`. `LICENSE` raw: "Copyright (c) 2025 Daniel Miessler" standard MIT. | **Structured JSON + raw file**: not method-suspect. |
| Data in repo | `contents/Data/AI-Hacking-Incidents` lists incidents.json (664,189 B), incidents.csv, sources.json/csv, candidates.json, regrade.json, update.ts, README/SUMMARY. | GitHub contents API (structured). |
| Third-party text | *"Short quotes from sources are credited to their publishers and remain under the publishers' terms."* | `/about/`, `/data/`. |
| Attribution request | *"hackingincidents.ai, Unsupervised Learning, accessed <date>"* | `/about/`, `/data/`. |
| robots.txt | `User-agent: *` / `Allow: /` / `Sitemap: https://hackingincidents.ai/sitemap.xml`. | WebFetch of `/robots.txt`; short file, so truncation risk low but it is still a markdown-converting tool; red-reviewer to curl raw. |
| Bulk export | `/incidents.json` (674 KB, 298 rows), `/incidents.csv`, `/sources.json` (279), `/sources.csv`; sitemap.xml 306 URLs (8 sections + 298 incident pages). No API, no RSS found. | `/data/` and `/sitemap.xml` via WebFetch. `incidents.json` fetch was truncated (689,852 chars; I read ~0-100k and 300k-400k) so total count of 298 is from the `/data/` page, not from counting the JSON. |
| Rate limits / ToS | **UNKNOWN, not confirmed absent.** `/about/`, `/method/`, `/sources/`, `/submit/`, `/data/` each stated no terms of use, no rate-limit text. Methods: WebFetch, markdown-converted, pages are small. Substrings looked for implicitly by the summariser: terms/licen/copyright/rate. **Method-suspect absence**; route to red-reviewer (checks below). | WebFetch only. |

Footer text on `/about/`: "This ledger covers publicly reported incidents only. We
aim to refresh it daily; the data is current to 24 Nov 2026." Daily refresh, so a
bulk fetch should be a single GET of the committed JSON at a modest cadence; the
GitHub repo copy (with history) is the better fetch target than scraping 298 pages.

**JSON shape (incidents.json, first records, truncated fetch):** top-level
`updated` ("2026-11-24") and `incidents[]`. No licence or attribution field in the
JSON itself (a licence-in-data gap: the licence lives on the HTML pages and the repo).

## 3. DRAFT SOURCE_LICENSES row (do not paste into SOURCE_LICENSES.md until the ingest PR)

### 1.9 hackingincidents.ai ledger (Substrate `Data/AI-Hacking-Incidents`) - DRAFT, D159, 2026-11-25
*Ingested by:* (proposed, not implemented) a fetch of the repo copy
`Data/AI-Hacking-Incidents/incidents.json` through `ingest/common.py`.

| Field | Value |
|---|---|
| License | **MIT (stated), applied to data by the operator.** `https://hackingincidents.ai/data/` and `/about/`: *"The data is published under the license of the Substrate repository: MIT License, Copyright (c) 2025 Daniel Miessler."* Repo `danielmiessler/Substrate` GitHub API `license.spdx_id` = `MIT`. Third-party text carve-out: *"Short quotes from sources are credited to their publishers and remain under the publishers' terms."* Retrieval: WebFetch (markdown) for the site pages, GitHub API JSON for the repo licence. |
| Scrape-permitted | **Yes for the bulk-export path.** robots.txt `Allow: /` for all agents; the dataset is offered as a download (`/incidents.json`, `/incidents.csv`) and in a public GitHub repo. No site ToS or rate limit located: **UNKNOWN, pending raw-HTML verification** (WebFetch, markdown-converted, five pages; not confirmed absent). |
| Redistribute-verbatim | **PARTIAL.** Operator-authored structured fields (id, title, date, actor, targets, models, outcome, grade, source list) YES under MIT with notice. `quote` NO (publisher terms). `summary` HOLD: provenance unknown (may be machine-written, may paraphrase vendor prose; MIT is a software licence and its application to a dataset is not spelled out). Vendor/press source titles and URLs: links are facts, keep as pointers. |
| Relicense-compatible | **YES, with a carve-out** (same shape as ATLAS 3.1): MIT does not require share-alike but requires the copyright and permission notice to travel with the covered material. It cannot be silently folded into a blanket "CC-BY-4.0, all rights ours". Operator-derived fields stay MIT-noticed in `NOTICE-DATA` and `.reuse/dep5`; the dataset's CC-BY-4.0 grant covers only our own selection and annotation. |
| Action | **(a) compatible with carve-out for structured fields; (c)-style handling for `quote`/`summary`** (id + url + our own offline-generated summary, per the WS0-T3 rule that summaries are generated offline and committed to `data/summaries/`, never during `make build`). Non-blocking clarification email drafted (`docs/audits/D159-hackingincidents-outreach-draft-2026-11-25.md`, NOT sent). Rows citing AIID inherit the AIID-snapshot terms (SOURCE_LICENSES 1.2a); rows citing aithreat.io inherit unknown terms (link only). |
| Date-checked | 2026-11-25 |

## 4. Data shape and scope

- **Count:** 298 incidents (`/data/` page; sitemap has 298 incident URLs, consistent).
  Sources registry 279 (240 swept, 13 cited-only, 26 unreachable).
- **Fields (from the JSON, truncated fetch):** `id` (slug), `title`, `date` (YYYY-MM,
  sometimes YYYY-MM-DD), `actor`, `actor_type`, `nexus`, `targets`, `ai_role`,
  `models`, `model_basis`, `autonomy`, `outcome`, `confidence` (Confirmed/Strong/
  Suspected), `confidence_reason`, `summary`, `quote`, `sources[]` (title, publisher,
  url, date, verified_on, fetch_status, primary), `single_source_reason`,
  `enrichment` (models, model_named, harness, countries, country_basis, sectors).
  Gaps relative to our schema: no CVE/CWE, no severity, no victim-count; actor,
  victim (`targets`), AI system (`models`/`harness`), attack type (`ai_role`) are
  present.
- **Primary references:** yes. Every sampled incident has at least one source URL
  to a vendor, government, or press page; `sources[].primary` is a boolean and
  Confirmed grade requires a primary source.
- **Scope fit:** all 298 are "cyberattacks where AI was known or strongly suspected
  to be used" (Jan 2023 onward): AI-as-weapon (agent frameworks, LLM-built malware,
  deepfake/voice fraud). Our corpus already carries this class (AIID Cairn/ARTEX
  entries, OECD PromptSpy/GREYVIBE, 2,948 deepfake/voice-clone lines), so in scope.
  Excludes AI-system-as-victim incidents (prompt injection, model flaws), so it is
  complementary to, not a replacement for, the AI-security half of the corpus.
  I did not count in-scope fraction exhaustively; every sampled entry was in scope.
  Weak labels: 71.5% grader agreement; 114 of 298 carried from an earlier ledger.

## 5. Overlap sample (n = 31; a gate can re-derive)

**Sample selection:** NOT random. The first 25 incidents in newest-first order from
`/incidents.json` (chars 0-100k) plus 6 from the 300k-400k window (older, 2026-05/06).
**Match method:** my keyword grep over `data/incidents.json` titles (case-insensitive
distinctive names), plus a URL grep for 16 primary reference URLs. Corpus is 15,845
INC rows. A same-event match was called only where an INC title names the same
actor/campaign/victim.

Legend: SAME = same event already in corpus; THEME = same theme, different event
(not counted as a match); NOVEL = no title or URL match found.

| # | hackingincidents.ai incident (slug) | Source URL (first) | Corpus result |
|---|---|---|---|
| 1 | 3am-affiliate-uk-school-suspected-ai-2026 | aithreat.io/cases/3am-ransomware-ai-uk-school/ | NOVEL |
| 2 | artex-github-oauth-secrets-2026 | Microsoft blog | NOVEL (THEME: INC-17356 ARTEX/ConnectWise, a different incident) |
| 3 | babidighost-jailbroken-agent-intrusions | playciso.com/blog/babidighost-... | NOVEL |
| 4 | barracuda-cloud-artex-breach-2026 | news.risky.biz/risky-bulletin-hackers-accessed-barracudas-cloud/ | NOVEL |
| 5 | bossai-ai-agent-campaign | Acronis | SAME-ish: INC (line 249763) "Attacker Reportedly Used BOSSAI AI Agents to Extract Emergency Dispatch Records in Taipei"; same campaign. Counted SAME. |
| 6 | cairn-glm-deepseek-semiconductor-defense-2026 | unit42.paloaltonetworks.com/cairn-framework-ai-autonomous-attacks/ | THEME (INC-17344 Cairn "100 company websites" is a different incident) |
| 7 | cairn-monai-label-university-intrusions | securityweek.com/amazon-china-linked-hackers-... | NOVEL (MONAI hits are unrelated CVE rows) |
| 8 | chainstack-ai-campaign-breach-2026 | aithreat.io/cases/chainstack-... | NOVEL |
| 9 | coinbase-elon-musk-deepfake-giveaway-2026-11 | Malwarebytes | NOVEL |
| 10 | conti-linked-ai-voice-ransomware | cisovoice.com/... | NOVEL |
| 11 | crafty-falcon-indian-bfsi-api-attacks-2026 | CERT-In | NOVEL |
| 12 | cyberstrikeai-education-intrusions-2026 | securelist.com/cyberstrikeai-attacks/121715/ | NOVEL |
| 13 | dprk-facestealer-deepfake-crypto-theft-2026 | ic3.gov/CSA/2026/261112.pdf | NOVEL |
| 14 | gitbook-ai-agent-intrusion-2026 | aithreat.io/cases/gitbook-... | NOVEL |
| 15 | kerala-sitharaman-deepfake-investment-fraud | indianexpress.com/... | THEME (AIID Sitharaman deepfake rows exist; the Kerala ₹1.45 crore case not seen) |
| 16 | leaky-castle-llm-exfiltrated-data-analysis-2026 | cloud.google.com/.../agentic-threat-activity-crosses-a-significant-threshold | NOVEL |
| 17 | operation-snowball-european-telecom | scworld.com/brief/... | NOVEL |
| 18 | sdny-ai-executive-impersonation-129m-2026 | justice.gov/... | NOVEL |
| 19 | silent-lynx-ai-assisted-tajik-document-theft | CloudSEK | NOVEL |
| 20 | strix-gambling-platform-compromise | coalitioninc.com/blog/security-labs/cyber-criminals-left-ai-hacking-tools-open-internet | NOVEL |
| 21 | vapor-panda-artex-global-espionage | NBC News | SAME: INC (line 249017) "VAPOR PANDA ... ARTEX AI Agents" |
| 22 | 123-reg-ai-driven-intrusion-2026 | aithreat.io/cases/123-reg-... | NOVEL |
| 23 | binance-hot-wallet-compromised-ai-tool-2026 | AI Incident Database | SAME: INC (line 249846) "Binance ... Internal AI Tool in $6.34 Billion Breach" |
| 24 | claude-pentestgpt-argentine-healthcare | crowdstrike.com/en-us/blog/crowdstrike-uncovers-new-agentic-ai-campaigns/ | SAME: INC (line 249110) "AI Agents to Breach Healthcare Organizations ... Argentina" |
| 25 | promptspy-android-gemini-agent | cloud.google.com/... ; welivesecurity.com/en/eset-research/promptspy-... | SAME: INC-00587 (OECD-AIM-2026-02-19-2f59) PromptSpy |
| 26 | greyvibe-russia-nexus-genai-2026 | withsecure.com/en/resources-hub/w-labs/greyvibe/ | SAME: INC-07966 (OECD-AIM-2026-05-29-1dbb) GREYVIBE |
| 27 | grok-bankrbot-morse-code-transfer-2026 | dexerto.com/... | SAME: INC with refs cryptoslate/cryptopolitan (Grok + Bankrbot Morse code, ~line 240630-240870) |
| 28 | sophos-ai-built-ransomware-toolkit-2026 | bleepingcomputer.com/... | NOVEL |
| 29 | ta4922-silentrunloader-llm-malware-2026 | proofpoint.com/... | NOVEL |
| 30 | unc6508-local-llm-in-victim-cloud-2026 | cloud.google.com/... from-prompting-to-autonomy | NOVEL |
| 31 | zenity-hijacked-ai-endpoints-strix-2026 | zenity.io/blog/real-world-ai-infrastructure-attacks-honeypots | NOVEL |

**Tally:** SAME 7 (#5, 21, 23, 24, 25, 26, 27), THEME 3 (#2, 6, 15), NOVEL 21.
Novel fraction = 21/31 = **68%** (95% interval on n=31 is wide, roughly 50-83%);
conservatively 21-24 of 31 counting THEME as novel-adjacent. Event-level overlap
= 23%. The 7 SAME matches are by AIID (#5, 21, 23, 24 look AIID-1766-1790
vintage) or OECD (#25, #26) provenance, so the overlap is exactly with sources we
already hold. **URL-level overlap: 0 of 16** primary vendor/government URLs grepped
(`unit42.../cairn`, `ic3.gov/CSA/2026/261112`, `aws.amazon.com/blogs/security/
amazon-threat-intelligence-observes`, welivesecurity promptspy, proofpoint ta4922,
zenity, bleepingcomputer toolkit, withsecure greyvibe, dexerto, coalitioninc,
straiker carliy0s, crowdstrike agentic, securelist cyberstrikeai, GTIG pages,
aithreat.io) appear in `data/incidents.json`. Our corpus cites news mirrors where
it has the event; ingesting this ledger would add primary references.

**Limits (conservative reading):** keyword-title matching misses same events titled
differently and over-credits similar names. Corpus has 15,845 rows; a true
dedupe needs the identity-key mechanism, not my grep. The sample is
newest-heavy (Nov 2026), where AIID snapshot lag makes novelty look higher than the
back catalogue (the 114 carried-over older incidents are likelier to overlap AIID).
Red-reviewer should draw a seeded random sample of 30 from the full 298.

## 6. Recommendation and conditions

**Ingest facts + link only.**

1. Fetch the repo copy of `Data/AI-Hacking-Incidents/incidents.json` (not the HTML
   pages), through `ingest/common.py`, committed verbatim with provenance (sha256,
   URL, date), like ATLAS. Refresh cadence no faster than weekly.
2. Keep: id, title, date, actor/actor_type/nexus, targets, models, outcome,
   confidence + confidence_reason as a labelled third-party grade, source URLs,
   source titles/publishers. **Exclude `quote`. Hold `summary` out** until
   operator response; generate our own summary offline per WS0-T3.
3. `NOTICE-DATA` and `.reuse/dep5`: add the MIT notice "Copyright (c) 2025 Daniel
   Miessler" for the ledger-derived fields; DATASHEET names the ledger as a source and
   states its confidence labels are third-party, 71.5%-agreement judgments, not ours.
4. Dedupe against AIID/OECD rows via the identity-key mechanism before adding;
   expect roughly a quarter of the ledger to collapse into existing rows, which
   should gain the ledger as an additional reference rather than a duplicate INC.
5. Rows citing aithreat.io (34 incidents): keep the URL only; no aithreat prose.
   If aithreat.io becomes a source in its own right it needs its own row.
6. Escalations for the user (not decided here): whether to ingest at all (policy),
   and whether to send the clarification email.

**Why not blocked pending outreach:** the stated licence is permissive and
explicit; the open questions (MIT-on-data scope, summary provenance, no ToS) bear
only on fields we are holding out. Conservatism here means claiming fewer rights
(fields), not blocking the facts.

## 7. Checks for red-reviewer (shell required; I have none)

1. Raw-HTML licence verification (not rendered text):
   `curl -sL https://hackingincidents.ai/about/ | grep -oi "MIT License[^<]*"` and
   the same for `/data/`; expect the "Substrate repository: MIT License, Copyright
   (c) 2025 Daniel Miessler" clause. Also look for terms the markdown pass may
   have dropped: `curl -sL <page> | grep -oiE "terms|licen[sc]e|copyright|rate.?limit|robots|attribution|permission"`
   on `/`, `/about/`, `/method/`, `/sources/`, `/submit/`, `/data/`, and one
   incident page, and on the footer of `/incidents/`. Record any hit; the
   absence finding in section 2 stands only after this.
2. `curl -s https://hackingincidents.ai/robots.txt` raw; confirm Allow: / and
   no Crawl-delay.
3. `curl -s https://api.github.com/repos/danielmiessler/Substrate | jq .license`
   and `.../contents/Data/AI-Hacking-Incidents`; confirm MIT and the file list.
   Also `curl -s https://raw.githubusercontent.com/danielmiessler/Substrate/main/Data/AI-Hacking-Incidents/README.md`
   and `source.md` for any data-specific terms not on the website (I did not read
   them).
4. Count and shape: download `incidents.json`, `jq '.incidents|length'` (expect
   298), `jq '.incidents|map(.sources|length)|add'`; confirm no top-level
   `license` key; count incidents citing `aithreat.io`, `AI Incident Database`,
   `AIAAIC`, `OECD` by publisher (I sampled, did not total them).
5. Overlap re-derivation by a method other than mine: seeded random 30 of 298;
   match by (a) reference URL set intersection against all `references[].url` in
   `data/incidents.json`, (b) normalised-title similarity, (c) manual same-event
   adjudication. Report SAME/THEME/NOVEL per row and compare with section 5; my
   0/16 URL overlap and 7/31 event overlap are the numbers to challenge. To
   prove the check fires: include 3 INC titles from our corpus (e.g. INC-17344,
   INC-07966, INC-00587) re-keyed as fake ledger rows and confirm they match.
6. Confirm the operator's jurisdiction (about page / whois / repo profile) so the
   E13 maker-residence reasoning can be closed for this source.
7. Check whether the `summary` strings are near-verbatim from the cited vendor
   pages (spot-check 10 summaries against their source text); this decides the
   hold on `summary`.
