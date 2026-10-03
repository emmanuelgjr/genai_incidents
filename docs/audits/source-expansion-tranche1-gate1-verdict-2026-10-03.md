# Source-expansion tranche 1 (reconstructed): licence pre-rows, red-reviewer gate 1: BOUNCE #1

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on
`ws0/tranche1-reconstructed` @ `06c7d561`.

**Provenance:** part 1 below was saved to disk exactly as the gate's message
arrived, then concatenated by shell. It was not retyped. Part 2 (the A1–A24
table, the different-route notes and the OSV advisory) will be appended
the same way when it arrives.

---

## Part 1: verdict and defects

VERDICT: BOUNCE (bounce #1 on ws0/tranche1-reconstructed @ 06c7d561). Part 1 of 2: the defects, with replacement text. The A1-A24 table, different-route notes and OSV advisory follow in part 2.

Shell checks refuted two rows outright (T1.6, T1.7). T1.4 needs a split score. T1.3, T1.5, T1.8, T1.9 and T1.10 need text corrections. Invariants are clean: only the two docs/specs files differ from origin/main; data/ and SOURCE_LICENSES.md have 0 diff; the scale table is byte-identical to main's.

DEFECTS

1. T1.4 CourtListener: the robots.txt is a real restriction, not a fetch limit. A plain curl gets a CloudFront 403. With a browser UA the file returns 200 text/plain (3,135 bytes). It ends with `User-agent: *` / `Disallow: /`. AI training, search and user bots (ClaudeBot, GPTBot, CCBot, Claude-User and others) also get `Disallow: /`, with only /help/, /feeds/, /terms/ and a few pages allowed. Line 1 reads "If you would like to crawl CourtListener, please contact us." Under the scale, 0 is triggered by "a robots.txt that disallows the content", so the precedent is the 1D.1 arXiv split.
REPLACE the summary row with:
| T1.4 | CourtListener / RECAP | 2 bulk / 0 site crawl | (a) with conditions, bulk S3 route only | Public Domain Mark on bulk data (gate-verified raw); robots.txt `User-agent: *` `Disallow: /` (gate-read); third-party works inside filings; API credentials not shareable |
REPLACE the Cleanliness score cell with:
**2 for the bulk-data route / 0 for HTTP crawling of www.courtlistener.com** (split, as 1D.1 arXiv). robots.txt disallows the whole site to generic and AI agents; the bulk files on the `com-courtlistener-storage` S3 bucket are the sanctioned channel and carry the Public Domain Mark.
REPLACE the Scrape-permitted cell with:
**robots.txt (gate, curl, 2026-10-03; a default curl UA gets a CloudFront 403, a browser UA gets 200 text/plain):** begins *"If you would like to crawl CourtListener, please contact us. We also have an extensive REST API and provide bulk data."* Named search engines may crawl, except `/api/rest/v1/` to `/v3/` and assets. AI training, search and user agents (ClaudeBot, GPTBot, CCBot, Claude-User and others) get `Disallow: /`, with `Allow` only for `/help/`, `/feeds/`, `/terms/` and a few info pages. The catch-all is `User-agent: *` `Disallow: /`. **No HTTP crawl of www.courtlistener.com without written permission.** **ToS** (gate, raw wiki HTML, "Updated: August 5, 2026"): the "Automated and Agentic Access" section sets credential and rate-limit rules (*"Do not use multiple accounts, registered clients, or credential rotation to exceed the rate limits that apply to your access level."*) and does not ban scraping, bulk or commercial use. The privacy section lists defending against "automated scraping" as a purpose. Bulk files are *"regenerated quarterly"* and are *"snapshots, not deltas"*.
REPLACE the Action cell with:
**(a) with conditions, bulk route only.** Ingest from the quarterly bulk files on the S3 bucket. Never crawl www.courtlistener.com (robots `Disallow: /`). Use the API only if the user rules that a credentialed API client is not a crawler under that robots file; otherwise ask FLP, as the robots file invites. Per-document provenance flag; exclude or downgrade to (c) any third-party copyrighted works; carry the non-endorsement line for generated summaries; privacy review of party names before ingest.

2. T1.6 0din: REFUTED "no licence found". 0DIN publishes its disclosures corpus on Hugging Face under CC BY 4.0. Evidence: the HF API for `0dinai/public-disclosures` returns `license:cc-by-4.0`, `gated: false`, lastModified 2026-05-15. The card reads "Creative Commons Attribution 4.0 International (CC-BY-4.0)" and "Attribute 0DIN (<https://0din.ai>) when redistributing or building on this dataset." The manifest has record_count 80; the site sitemap lists 82 /disclosures/ URLs. The Services Agreement exists at `/services_agreement`, not `/services-agreement`.
REPLACE the summary row with:
| T1.6 | 0din (Mozilla GenAI bounty) | 2 | (a) with conditions, HF dataset route only | CC BY 4.0 corpus `0dinai/public-disclosures` on Hugging Face (gate-found); prompt/response/signature fields must be dropped; mirror last exported 2026-05-15; site API and 0DIN Intel off-limits |
REPLACE the Cleanliness score cell with: **2** (explicit CC BY 4.0 grant by the publisher on its own disclosures corpus; conditions: field filter, attribution, staleness).
PREPEND to the License cell:
**CC BY 4.0 for the public disclosures corpus (gate-found 2026-10-03, raw; refutes "no licence found").** The 0DIN blog `https://0din.ai/blog/public-disclosures-corpus` (2026-05-15) says the corpus is *"distributed as a weekly versioned JSONL dataset on Hugging Face and Mozilla Data Collective — same data as 0din.ai/disclosures"*. Hugging Face API `api/datasets/0dinai/public-disclosures` (structured): `license:cc-by-4.0`, `gated: false`. Dataset card: *"Creative Commons Attribution 4.0 International (CC-BY-4.0)"* and *"Attribute 0DIN (<https://0din.ai>) when redistributing or building on this dataset."* `manifest.json`: 80 records, generated 2026-05-15. For allowlisted disclosures the records include *"pinned messages, variant prompts (with industry grouping preserved), and the current-version detection signature"*. The Master Services Agreement is a PDF at `0din.ai/services_agreement`, "last updated on April 2, 2026"; the earlier 404 was a guessed path. It binds Customers of ordered Services; under s5.2 Usage Restrictions, (j) bars them from *"engage in web scraping or data scraping on or related to the Services"*. 0DIN Intel docs footer: *"0DIN Intel content for licensed users only."*
REPLACE the Redistribute-verbatim cell with: **YES for the HF corpus under CC BY 4.0, minus the `messages`, `variant_prompts` and detection-signature fields** (jailbreak prompts and model outputs, i.e. raw payload text, which the project does not carry). **NO / UNKNOWN** for site pages outside the corpus and for 0DIN Intel.
REPLACE the Relicense-compatible cell with: **YES** (CC BY 4.0 to CC BY 4.0, attribution to 0DIN).
REPLACE the Action cell with: **(a) with conditions:** ingest from the HF dataset only, pinned to a revision, recording `manifest.json` `generated_at`; drop the prompt, response, variant and signature fields; attribution "0DIN (https://0din.ai), CC BY 4.0"; never use `0din.ai/api/` (robots-disallowed) or the 0DIN Intel feed (MSA; licensed users only); record the mirror's lag (last export 2026-05-15 despite "weekly"; 80 records vs 82 site disclosures).

3. T1.7 EPSS: REFUTED "FIRST terms pages 404 / no formal licence". Every FIRST footer links `/about/policies/terms` and `/copyright`; the 404s were guessed paths. The score stays 1, but the reason changes and it is no longer provisional.
REPLACE the summary row's blocking issue with: FIRST Services Terms of Use (gate-found) cover "API (Public)" with a revocable, non-transferable licence limited to vulnerability-disclosure, incident-response or preventative-cybersecurity uses; daily CSV hosted by Empirical Security; "attribution is requested"
REPLACE the Cleanliness score cell with: **1** (a licence exists but is purpose-limited and revocable, so it is not CC BY 4.0-compatible; facts + link not contested). Primary pages read by the gate; not provisional.
REPLACE the License cell's first sentence ("No formal licence found.") and its last sentence ("A 'free and open' statement ... not a licence") with:
**Purpose-limited licence, not an open one (gate-found 2026-10-03, raw).** FIRST Services Terms of Use, `https://www.first.org/about/policies/terms` ("Effective at September 2023"): "Services" includes *"API (Public)"*; `api.first.org/epss/` calls itself "FIRST.Org API v1". *"FIRST grants you a nonexclusive, nontransferable, revocable, limited license to view, copy, print, and distribute Content retrieved from the Services to the extent permissible under applicable laws only for vulnerability disclosure, cybersecurity incident response, or preventative cybersecurity uses"*; *"You may not use any Content available via the Services in any other manner or for any other purpose without the prior written permission of FIRST"*. `https://www.first.org/copyright`: *"All documents available on this site may be protected under the U.S. and Foreign Copyright Laws. Permission to reproduce may be required."* `https://www.first.org/epss/data`: the API *"should not be used for bulk downloads"*. The daily CSV is served from `epss.empiricalsecurity.com`, and the history repo `empiricalsec/epss_scores` has API `license: null` and no licence text in its README.
REPLACE Redistribute-verbatim and Relicense-compatible with: **NO** without FIRST's written permission. A purpose-limited, revocable licence cannot pass into a CC BY 4.0 dataset; whether daily scores are copyrightable is still not assessed.
APPEND to Scrape-permitted: `api.first.org/robots.txt` returns 404 (no rules declared); the API JSON carries `"access":"public"` and no licence key.

4. T1.5 FTC: one quote is not verbatim, and a clause and a carve-out are missing. The page reads "...not subject to copyright restrictions (17 U.S.C. 105)." The row's form ending "restrictions." gets 0 hits on the raw page; the cited form gets 1.
REPLACE the first Website Policy quote with: *"Most material on the FTC's website is considered work of the United States Government, meaning that the material is in the public domain and is not subject to copyright restrictions (17 U.S.C. 105)."*
INSERT after the attribution quote: *"In addition, any copyrighted work that consists predominantly of material produced by the FTC or other U.S. government agency must provide notice identifying such material and stating that it is not subject to copyright protection (17 U.S.C. 403)."*
REPLACE the third-party parenthetical with: (found *"in or included with public comments and filings, incorporated as photos or other graphics in FTC webpages or other materials prepared by our contractors"*). Add "contractor-prepared materials" to the carve-outs.
REPLACE the robots part of Scrape-permitted with: **robots.txt (gate, curl, full file, 2026-10-03):** `User-agent: *`, `Crawl-delay: 5`. Drupal disallows: `/core/`, `/profiles/`, `/admin/`, `/comment/reply/`, `/filter/tips`, `/node/add/`, `/search/`, `/user/register|password|login|logout`, their `/index.php/` twins, `/README.txt`, `/web.config`. Also `/es/node/*`, `/*/comment/*`, and query forms with `combine=` or `items_per_page=`. Plus eight legacy paths: three 2018-2019 `/news-events/events-calendar/` conference pages and five `/sites/default/files/documents/` `.htm`/`.shtm` statements. **`/legal-library/` and `/news-events/news/` are not disallowed; `/search/` is.** The Website Policy has no automated-access clause (raw grep 0 hits; "bulk" appears only as the "Bulk Publications" nav item).
REPLACE the Action sentence "The shell check of the disallowed paths decides whether `/legal-library` case pages are reachable" with: Case pages under `/legal-library/` are reachable under robots; discover them from the legal-library browse pages, never `/search/`; the dataset notice also meets the 17 U.S.C. 403 notice.

5. T1.3 CERT/CC: the open "Service" question is now answered, and item (2) is not current primary text.
REPLACE "Which 'Service' this means, and whether it reaches kb.cert.org, is **not established**." with: The TOU's scope is *"SEI websites, including SEI Weblogs and Wikis (collectively, the “Service”)"* (gate, raw, page dated "Wednesday, June 20, 2018"). It also says: *"Any unauthorized reproduction, publication, further distribution, or public exhibition of the materials provided on the Service, in whole or in part, is strictly prohibited."* kb.cert.org presents as an SEI site (footer "Software Engineering Institute", (c) CMU, SEI privacy link; SEI's own menu links "Vulnerability Notes" to kb.cert.org), so the TOU **likely** governs it. The note's own "Legal" link nonetheless points to the dead VINCE Code of Conduct.
APPEND to item (2): **Gate 2026-10-03: absent from `kb.cert.org/vuls/` and `certcc.github.io/VINCE-docs/copyright/` (raw, 0 hits). It is not current primary text; the nearest current text is the archive LICENSE in (5): "may be reproduced in its entirety, without modification, and freely distributed ... Permission is required for any other external and/or commercial use."**
REPLACE the Cleanliness score qualifier ("Could fall to 0 ... settle it") with: The SEI TOU bars copying, reproduction and mirroring of content, not extraction of facts, so the score is 1, following the 1C.3 Dutch AP precedent. It falls to 0 only if CMU states that the TOU bars automated access.
REPLACE the robots text with: **robots.txt: none declared** (404 HTML on both www and bare host, gate curl).

6. T1.10 GHSL: robots was obtained, and the AUP-scope question is now answered.
REPLACE the Scrape-permitted cell with: **robots.txt (gate, curl, 200 text/plain):** the entire file is `Sitemap: https://securitylab.github.com/sitemap.xml`. There are no User-agent or Disallow lines, so robots declares no restriction. **ToS:** GitHub's ToS defines "Website" to include *"GitHub-owned subdomains of github.com"*, so the ToS and AUP govern securitylab.github.com. AUP s6: *"You will not reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service without our express written permission."* AUP s7 allows the use of information *"regardless of whether the information was scraped, collected through our API, or obtained otherwise"* for researchers (open-access publications only) and archivists. The score stays 1: s6 restricts reproduction of the Service, not facts. It could fall to 0 if the researcher exception is read as not covering a redistributed dataset.
APPEND to License: a GHSA twin exists for the sample: CVE-2025-33214 maps to GHSA-rggg-jp6v-h52j (GitHub API, gate).

7. T1.8 OpenSSF: the inbound-licence reasoning is wrong for part of the corpus.
REPLACE "the Apache-2.0 position for third-party-contributed reports therefore rests on the repo-wide licence plus GitHub's inbound=outbound default for contributions, which is a general GitHub ToS rule and was not re-read for this row." with: the Apache-2.0 position for contributed reports rests on the repo-wide licence alone. GitHub's inbound=outbound rule (ToS D.6) reaches only PR contributions, and the PR author may not hold the rights to a vendor feed. CONTRIBUTING (raw, gate 2026-10-03) also describes bulk imports via `cmd/ingest` and **automated ingestion from contributors' AWS S3 or Google Cloud Storage buckets**, which is not a GitHub contribution at all, and states no licence term for either. README, CONTRIBUTING and CONTRIBUTION-GUIDELINES contain no licence, DCO, CLA or copyright text (raw grep, 0 hits).
The score stays 2; inbound licensing is a listed condition.

8. T1.9 (low severity): the HF ToS quote is cut mid-sentence and drops a scope limiter.
REPLACE the quote with: *"If you decide to set your Repository public, you grant each User a perpetual, irrevocable, worldwide, royalty-free, non-exclusive license to use, display, publish, reproduce, distribute, and make derivative works of your Content through our Services and functionalities"*. REPLACE the bold caveat with: **the licence runs only "through our Services and functionalities", so it gives a downstream dataset nothing.**

The foreman's framing was right on T1.9 (drop it; the gate confirmed across all 469 HF org repos) and on the OSV side question. It was not wrong anywhere I could test.


## Part 2: A1–A24 results, routes, OSV advisory

Part 2 of 2 (tranche-1 gate, BOUNCE #1): the A1-A24 results, different-route notes, the OSV advisory and the evidence. Everything below was fetched raw by curl on 2026-10-03, one request at a time per host, with FTC spaced at least 5 s apart. No robots-disallowed path was fetched; on www.courtlistener.com I fetched only robots.txt.

A1-A24 RESULTS
A1 CONFIRMED: kb.cert.org robots.txt is 404 HTML on both www and bare host. Note that kb.cert.org gzips even without Accept-Encoding, so an uncompressed grep sees binary.
A2 CONFIRMED: the footer anchor "Legal" points to vuls.cert.org/.../VINCE+Code+of+Conduct, which 301s to certcc.github.io and then 404s.
A3 CONFIRMED: the note's only rights text is "(c)2022 Carnegie Mellon University"; tag-stripped grep finds no licence wording.
A4 RESOLVED (defect 5): "SEI websites, including SEI Weblogs and Wikis (collectively, the Service)". The "June 20, 2018" date is confirmed.
A5 CONFIRMED: archive LICENSE.md read in full; external use is limited to unmodified reproduction, and anything else needs permission.
A6 CONFIRMED absent: "complete and unmodified" gets 0 hits on kb.cert.org/vuls/ and VINCE-docs/copyright (both 200). VINCE docs are CC BY-NC 4.0; the MIT text there belongs to the mkdocs theme.
A7 REFUTED (defect 1): User-agent * Disallow /.
A8 CONFIRMED: no scraping, bulk or commercial ban. The page body has the "Do not use multiple accounts" control phrase, and both ToS quotes are verbatim.
A9 CONFIRMED: "Our bulk data files are free of known copyright restrictions.", followed by the Public Domain Mark linking to creativecommons.org/publicdomain/mark/1.0/.
A10 CONFIRMED: 0 hits (status 200, "public domain" present).
A11 RESOLVED (defect 4): exact paths given there; legal-library is not disallowed.
A12 REFUTED: /services_agreement exists (MSA PDF dated 2026-04-02); /legal_archive also lists MSA versions from 2026-01-08 and 2025-06-30.
A13 CONFIRMED: /policy has no copyright, licence, reuse or scrape clause ("Last Updated: 2026-10-02"). All four quotes are verbatim.
A14 REFUTED in substance (defect 2): the Intel docs say "for licensed users only"; the sitemap has 267 URLs, 82 of them under /disclosures; the CC BY 4.0 HF corpus was found from the sitemap.
A15 REFUTED (defect 3): /about/policies/terms and /copyright exist.
A16 CONFIRMED: api.first.org robots.txt is 404; the JSON has no licence key.
A17 CONFIRMED: 0 licence, DCO or CLA hits in the three files. New finding from the same files: automated S3/GCS ingestion (defect 7).
A18 CONFIRMED: API spdx_id Apache-2.0; no NOTICE in the root; osv/ holds only malicious/, unmergable/ and withdrawn/, with no LICENSE file.
A19 see the OSV advisory below.
A20 CONFIRMED: all 469 huggingface org repos (pages 1-5) searched. Only security-workflows (CI tooling) and atif-scan (no description) match "secur|scan". The docs index has no advisory links; huggingface_hub /security-advisories returns []. The GHSA API does return transformers advisories, e.g. GHSA-x9r9-c232-4q39.
A21 CONFIRMED: no scrape or crawl clause; the "You own the Content you create" control phrase is present.
A22 CONFIRMED: the footer reads "GitHub Inc. (c) 2024" and links the GitHub ToS and Privacy pages.
A23 REFUTED as "not obtained": the complete file is a single Sitemap line (defect 6).
A24 RESOLVED: the GitHub ToS "Website" includes GitHub-owned subdomains. GHSA twin GHSA-rggg-jp6v-h52j exists. The three AUP quotes are verbatim.
Tally: 13 confirmed, 6 refuted or refuted-in-substance (A7, A12, A14, A15, A23, plus A17's new finding), 4 resolved, 0 still unverifiable.

QUOTE SPOT-CHECK: every quoted clause in T1.3, T1.4, T1.6, T1.8 and T1.10 is verbatim on its cited page, as are T1.7's FAQ and home quotes (one differs only by sentence-initial capital). The misses are T1.5's first quote (defect 4) and T1.9's truncation (defect 8). I proved the matcher fires: the row's FTC form gets 0 hits and the cited form gets 1.

SCORES AGAINST THE SCALE (after the fixes)
- T1.3: 1, with action (c)/(d). Fits the scale.
- T1.4: 2 bulk / 0 crawl (split per the 1D.1 arXiv precedent).
- T1.5: 2. Holds: §105(a) is verbatim at law.cornell.edu, and the FTC page cites §105 itself.
- T1.6: 2 (a filter separates the covered fields).
- T1.7: 1, no longer provisional.
- T1.8: 2.
- T1.9: n/a.
- T1.10: 1.
The D39 provisional clause no longer applies to any row: every grant was read from a primary page or an API.

DIFFERENT ROUTES (agreement 6)
- T1.4: found the CourtListener ToS and bulk-data pages through wiki.free.law/llms.txt and its robots file rather than the auditor's URLs. Re-confirmed the bulk route on S3; the robots result was a material finding.
- T1.5: read the FTC robots file in full and found the policy links from the page's own hrefs. FTC has no /sitemap.xml (404). Verified §105 from Cornell LII, a different host from the earlier gate.
- T1.8: used the GitHub API for the licence and the raw LICENSE, README and CONTRIBUTING files, then followed CONTRIBUTING into the bulk and automated ingestion paths. The OSV data page independently lists "OpenSSF Malicious Packages (Apache 2.0)".
- T1.6 and T1.7 were not in the brief, but following footer hrefs refuted both rows. The auditor's 404s were guessed URLs, the same failure shape tranche 2 found.

OSV ADVISORY (shipped data; not a defect of this branch)
- Half 1 CONFIRMED: google.github.io/osv.dev/data/ lists "OpenSSF Malicious Packages (Apache 2.0)" next to "GitHub Advisory Database (CC-BY 4.0)". The ossf repo licence is Apache-2.0 (API). Row 2.4's sentence "every source database actually reachable by this script is CC-BY 4.0" is FALSE. Proof that it is reachable: the tracked file ingest/cve_nvd_expanded.json holds 2 OSV records sourced from MAL-: MAL-2026-3607 (guardrails-ai) and MAL-2026-2144 (litellm). Their descriptions are verbatim OpenSSF report text ("Per source details. Do not edit below this line ... ## Source: google-open-source-security ..."). That file is committed (git ls-files), so the repo itself redistributes Apache-2.0 text under a CC BY claim.
- Half 2, the published layer: in data/incidents.json, grep -c '"MAL-' gives 1 line, and MAL-2026-3607 appears twice (control MAL-2099- gives 0). Both occurrences are in INC-08450, as a source_id and an OSV reference URL. Its description is the GHSA-6xwp-cp5h-q856 beproduct text (CC BY 4.0). The MAL text markers "Per source details" and "compromised through trivy" both get 0 hits. MAL-2026-2144 is absent from incidents.json; it appears only in an id list in data/issue88_remediation.json. So the published records carry no Apache text today, but the row's sentence is untrue, and the next MAL record without a GHSA twin would ship Apache-2.0 text.
- Proposed follow-up task (WS0): correct row 2.4 in place (a live surface, agreement 4). Then either filter MAL- records out of OSV_TARGETS results, or carry them as Apache-2.0 per record with attribution "OpenSSF Malicious Packages via OSV.dev". Also check whether ingest/*.json ships in any release artifact.
- Side observation for WS1: INC-08450 merges beproduct (GHSA-6xwp), mistralai (GHSA-wx9m, CVE-2026-46412) and guardrails-ai (MAL-2026-3607) under one id, with tags for all three. That may be an over-merge; I did not investigate further.

ADVISORY
- The "Absence findings" table should gain a result column taken from the list above. The working file says "routed to shell verification" with no outcome.
- T1.6 at score 2 raises a payload question for the user: the CC BY corpus includes jailbreak prompts, which the project does not carry. The field filter is the condition.

EVIDENCE / STATE
- Worktree HEAD: `git symbolic-ref -q HEAD` gives refs/heads/ws0/tranche1-reconstructed, at 06c7d561.
- `git diff --stat origin/main...HEAD` shows only the 2 docs/specs files (405 insertions); `git diff origin/main HEAD -- data docs/SOURCE_LICENSES.md` is empty.
- The scale table diff against main is empty.
- `git status --porcelain` is empty in both the worktree and the main tree; main is at refs/heads/main. That covers the working tree only, not refs.
- I wrote no repo files. Curl outputs are in my scratchpad only.
