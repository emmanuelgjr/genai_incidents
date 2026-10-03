# Source-expansion evaluation: reconstructed tranche 1 (T1.3 to T1.10)

**Working file, started 2026-10-03.** Reconstruction record:
`docs/specs/source-expansion-tranche1-reconstruction-2026-10-03.md` (dated, do
not regenerate). T1.1 (CISA beyond KEV) and T1.2 (huntr) have gated pre-rows in
`docs/specs/source-expansion-evaluation.md` s1E.2 and s1E.1 and are not repeated
here. Rows are **pre-rows** in the `docs/SOURCE_LICENSES.md` column format
(invariant 10: a real row lands in `SOURCE_LICENSES.md` only inside that source's
ingest PR; this file does not edit it). No ingest code exists or is authorised
before a user ruling.

**Author: license-auditor. No shell is available to this agent.** Every page was
read through WebFetch (a markdown-converting, **summarising** fetch: it returns a
model-written extract, not page text, and may truncate) or WebSearch. Quoted
clauses below are therefore the fetch tool's quotations; they are **not**
byte-verified. They are marked "extract" unless a structured endpoint (GitHub API
JSON) carried them. Every absence statement ("no licence found", "no scrape
clause") is **method-suspect** and is routed to the section "Absence findings for
shell verification" at the end, with the exact check.

**Facts re-checked vs. taken from the brief:** nothing from the reconstruction
record is carried forward unverified. Where the record's framing was wrong the
row says so, and the section "Brief vs. found" lists the refutations.

## Scale and action letters

Copied unchanged from `docs/specs/source-expansion-evaluation.md` ("Licensing-
cleanliness scale (0-3), defined once").

| Score | Meaning |
|---|---|
| **3** | Verbatim ingest into a CC BY 4.0 dataset is allowed: explicit permissive grant (CC0 / CC BY / OGL / public-domain work) covering the content we would take, automated access not prohibited, nothing left open. Action (a). |
| **2** | Verbatim ingest allowed **with a condition we must engineer for** (per-item third-party carve-outs, attribution/notice formalities, rate limits, a filter to separate covered from uncovered material, or a grant read only second-hand). Action (a) with conditions. |
| **1** | Verbatim ingest **not** allowed or **unknown** (non-commercial, no-derivatives, all-rights-reserved, contradictory or missing terms), but the **facts + link + original summary** shape is not itself contested: no explicit ban on automated access or on extracting facts; **or a grant known only from a search extract whose primary page could not be reached (provisional)**. Action (c) or (d). |
| **0** | **Even facts + link is contested**: an explicit prohibition on bulk/automated access or on open-licence redistribution of the data, a robots.txt that disallows the content, or a litigation history against scrapers. Do not ingest at all before a written permission. Action (d), interim "link only". |

Action letters: (a) compatible · (b) share-alike · (c) prohibited -> facts + link
+ original summary only · (d) unknown -> outreach (user sends; none drafted
here). Project data licence for "relicense-compatible": **CC BY 4.0**.

## Summary

Scores are the specialist's first pass as corrected by red-reviewer gate 1 (BOUNCE #1, 2026-10-03, corrections applied verbatim); no gate has passed them yet.

| # | Source | Score | Action | Blocking issue |
|---|---|---|---|---|
| T1.3 | CERT/CC Vulnerability Notes | 1 | (c); (d) for the archive | Contradictory CMU terms: notes carry (c) CMU; footer "Legal" link is dead; the SEI terms found (2018) bar copying, derivative works and mirroring; sibling VINCE docs are CC BY-NC 4.0; the archived data repo LICENSE allows only unmodified redistribution. The SEI TOU (scope: SEI websites) likely governs kb.cert.org and bars reproduction and mirroring, not fact extraction (score 1, 1C.3 Dutch AP precedent); falls to 0 only if CMU states the TOU bars automated access |
| T1.4 | CourtListener / RECAP | 2 bulk / 0 site crawl | (a) with conditions, bulk S3 route only | Public Domain Mark on bulk data (gate-verified raw); robots.txt `User-agent: *` `Disallow: /` (gate-read); third-party works inside filings; API credentials not shareable |
| T1.5 | FTC enforcement actions | 2 | (a) with conditions | "Most material" is public domain (FTC's own words), third-party material in filings and comments carved out; robots Crawl-delay 5; `/legal-library/` and `/news-events/news/` not disallowed, `/search/` is (gate-read); 17 U.S.C. 403 notice applies to a work consisting predominantly of US government material |
| T1.6 | 0din (Mozilla GenAI bounty) | 2 | (a) with conditions, HF dataset route only | CC BY 4.0 corpus `0dinai/public-disclosures` on Hugging Face (gate-found); prompt/response/signature fields must be dropped; mirror last exported 2026-05-15; site API and 0DIN Intel off-limits |
| T1.7 | FIRST EPSS (enrichment) | 1 | (d) (light) | FIRST Services Terms of Use (gate-found) cover "API (Public)" with a revocable, non-transferable licence limited to vulnerability-disclosure, incident-response or preventative-cybersecurity uses; daily CSV hosted by Empirical Security; "attribution is requested" |
| T1.8 | OpenSSF malicious-packages | 2 | (a) with conditions | Apache-2.0 (GitHub API, structured). Apache NOTICE/licence carriage; no inbound-licence statement for contributed reports; **overlaps already-ingested OSV (row 2.4) and the 2.4 row's "every reachable database is CC-BY 4.0" sentence is false (gate-measured)** |
| T1.9 | Hugging Face security advisories / malicious-model disclosures | n/a (no such source) | recommend drop and replace | **Refuted:** no advisory feed or database exists; HF publishes a docs page and per-repo scanner status. Related content is third-party research or already in GHSA |
| T1.10 | GitHub Security Lab advisories | 1 | (c) | No content licence found on securitylab.github.com (footer "GitHub Inc. 2024"); GitHub AUP scraping definition; licence-clean route is the GHSA entry (CC BY 4.0) already ingested |

Corpus overlap, measured by Grep on `data/incidents.json` in this worktree
(lines containing the string; one entry can span many lines, so these are not
entry counts): `kb.cert.org` 28 lines; `courtlistener.com` 0; `ftc.gov` 2;
`0din.ai` 0; `securitylab.github.com|GHSL-` 40; `epss` 0; `MAL-20` 2 (alias
IDs inside OSV-derived records, for example `MAL-2026-3607` next to a GHSA id).
These are URL references or alias ids inside records from other sources, not
ingestion of these sources' text.

---

## 1. Licence pre-rows

### T1.3 CERT/CC Vulnerability Notes (kb.cert.org / VINCE)
*Content class:* Vulnerability Notes (VU#), a coordinated-disclosure database of
CMU SEI's CERT Division; JSON and CSAF via the Vulnerability Note API.
*Language:* English. Prior is **refuted in part**: the reconstruction record
guessed "CMU SEI terms; there may be a GitHub CERTCC/ data repo". The repos
exist (`CERTCC/VINCE`, `CERTCC/Vulnerability-Data-Archive`, archived) but carry
non-standard licences, not an open one.

| Field | Value |
|---|---|
| Cleanliness score | **1** (contradictory/unknown terms; facts + link not shown to be banned). The SEI TOU bars copying, reproduction and mirroring of content, not extraction of facts, so the score is 1, following the 1C.3 Dutch AP precedent. It falls to 0 only if CMU states that the TOU bars automated access |
| License | **No open licence located; terms found are mutually inconsistent.** (1) A sample note, `https://www.kb.cert.org/vuls/id/739007` (WebFetch 2026-10-03, extract), ends with *"©2022 Carnegie Mellon University"* and contains no licence or redistribution clause. Its footer "Legal" link is `https://vuls.cert.org/confluence/display/VIN/VINCE+Code+of+Conduct#VINCECodeofConduct-TermsofUse` (extract of the page's link list), which 301-redirects to `certcc.github.io/confluence/display/VIN/VINCE+Code+of+Conduct`, which returns **404**: the note's own legal link is dead. (2) Search extract (WebSearch, no primary page): notes "may be redistributed freely after the release date, provided that redistributed copies are complete and unmodified, and include all date and version information" (the old CERT/CC reproduction wording; **not read from a primary page, provisional**). **Gate 2026-10-03: absent from `kb.cert.org/vuls/` and `certcc.github.io/VINCE-docs/copyright/` (raw, 0 hits). It is not current primary text; the nearest current text is the archive LICENSE in (5): "may be reproduced in its entirety, without modification, and freely distributed ... Permission is required for any other external and/or commercial use."** (verified by red-reviewer via curl, 2026-10-03) (3) VINCE docs, `https://certcc.github.io/VINCE-docs/copyright/` (extract): work *"licensed under a Creative Commons Attribution-NonCommercial 4.0 International License"*; permission requests to permission@sei.cmu.edu. This page covers the VINCE documentation, not necessarily the notes. (4) SEI Legal, `https://www.sei.cmu.edu/legal/` (extract, last updated 2018-06-20): users may *"display the content of the Service only for your own personal use (i.e., non-commercial use)"* and may not *"copy, reproduce, alter, modify, create derivative works of, or publicly display any content"*, nor *"take the results from the Service and reformat and display them or mirror any portion"*. The TOU's scope is *"SEI websites, including SEI Weblogs and Wikis (collectively, the “Service”)"* (verified by red-reviewer via curl, 2026-10-03, raw; page dated "Wednesday, June 20, 2018"). It also says: *"Any unauthorized reproduction, publication, further distribution, or public exhibition of the materials provided on the Service, in whole or in part, is strictly prohibited."* kb.cert.org presents as an SEI site (footer "Software Engineering Institute", (c) CMU, SEI privacy link; SEI's own menu links "Vulnerability Notes" to kb.cert.org), so the TOU **likely** governs it. The note's own "Legal" link nonetheless points to the dead VINCE Code of Conduct. (5) `CERTCC/Vulnerability-Data-Archive` (GitHub API `license`: `NOASSERTION`, name "Other"; archived 2024-05-14; data to 2020-06-03): LICENSE.md text, via the API's decoded content, begins *"Copyright (c)2020 Carnegie Mellon University"* and says the material is approved for public release *"except as restricted below"*; a summarising fetch of the same file reports unmodified reproduction and distribution permitted, other uses requiring permission from permission@sei.cmu.edu. The README, same repo, says only ~6% of records are published Vulnerability Notes and the archive "has been supplanted by the VINCE API". (6) `CERTCC/VINCE` (software; API `license`: `NOASSERTION`, "Other"). |
| Scrape-permitted | **robots.txt: none declared** (404 HTML on both www and bare host; verified by red-reviewer via curl, 2026-10-03). **ToS:** the Vulnerability Note API docs (extract) say *"The Vulnerability Note API does not require authentication, Vulnerability Notes are public"*, with no rate limit stated; that supports API access but is not a licence. The SEI TOU in (4) bars mirroring of results but has no automated-access clause (gate, raw; grep for robot, spider, scrap, crawl, automated: 0 hits). Status: **no robots rules; no automated-access ban found; reproduction barred by the TOU** |
| Redistribute-verbatim | **NO / UNKNOWN.** Copyright is CMU's; the only grants found are non-commercial (VINCE docs), unmodified-only (archive, search extract) or absent. Verbatim text cannot go into a CC BY 4.0 dataset |
| Relicense-compatible | **NO.** Non-commercial and no-modification grants cannot be folded into CC BY 4.0 |
| Action | **(c) facts + link + <=2-sentence original summary** (VU#, title, CVE ids, dates, reporter-independent facts, link). **(d)** a permission request to permission@sei.cmu.edu would settle the open-licence question (user sends; not drafted here). Licence-clean route to the same facts: CERT/CC is a CNA, so notes with CVEs reach CVE records and NVD, which `SOURCE_LICENSES.md` already covers under the CVE ToU |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising) of: `kb.cert.org/vuls/` and `/vuls/id/739007` (not truncated per tool), `sei.cmu.edu/legal/` (via 301 from `/legal/index.cfm`), `certcc.github.io/VINCE-docs/copyright/`, `.../Vulnerability-Note-API/`, GitHub README and `raw.githubusercontent.com/.../LICENSE.md` of the archive, the dead Confluence link; GitHub API JSON for `CERTCC/Vulnerability-Data-Archive` and `CERTCC/VINCE` (structured: `license` field; the decoded `/license` endpoint returned the archive text). WebSearch x2 (search-extract tier: the "complete and unmodified" wording). Substrings sought: copyright, license, reproduce, redistribute, mirror, automated. Source kind: rendered HTML via a summarising converter (weak for absences) + GitHub API JSON (reliable) |
| Non-English / facts-only | English. Facts + link + original summary is the required shape; summary generated offline per the WS0-T3 rule |

### T1.4 CourtListener / RECAP (Free Law Project)
*Content class:* US court opinions, dockets, filings (RECAP archive of PACER
documents), oral arguments; REST API v4 and quarterly bulk CSV. *Language:*
English. AI relevance is a **filter problem** (AI-litigation dockets are a tiny
slice); a pipeline matter, not a licence one.

| Field | Value |
|---|---|
| Cleanliness score | **2 for the bulk-data route / 0 for HTTP crawling of www.courtlistener.com** (split, as 1D.1 arXiv). robots.txt disallows the whole site to generic and AI agents; the bulk files on the `com-courtlistener-storage` S3 bucket are the sanctioned channel and carry the Public Domain Mark. |
| License | **Bulk data: public domain, per FLP.** Bulk Legal Data wiki, `https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data` (WebFetch 2026-10-03, extract; reached by 301 from `courtlistener.com/help/api/bulk-data/`): the bulk files are *"free of known copyright restrictions"* and marked with the **Public Domain Mark**. Terms of Service, `https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies` (extract; tool said not truncated): *"judicial opinions, motions, and other filings are generally in the public domain"* but *"other court filings may contain third-party copyrighted works"*; also: *"If you republish or display our data, do not present it in a way that suggests Free Law Project produced, endorsed, or verified an AI-generated analysis of it."* The Public Domain Mark is FLP's statement, not a licence; the underlying works are US government works (court opinions) or party filings, the latter not always federal works. Carve-outs: third-party copyrighted works embedded in filings (books, articles, expert reports); personal data in dockets (a privacy matter, not a copyright one). |
| Scrape-permitted | **robots.txt (gate, curl, 2026-10-03; a default curl UA gets a CloudFront 403, a browser UA gets 200 text/plain):** begins *"If you would like to crawl CourtListener, please contact us. We also have an extensive REST API and provide bulk data."* Named search engines may crawl, except `/api/rest/v1/` to `/v3/` and assets. AI training, search and user agents (ClaudeBot, GPTBot, CCBot, Claude-User and others) get `Disallow: /`, with `Allow` only for `/help/`, `/feeds/`, `/terms/` and a few info pages. The catch-all is `User-agent: *` `Disallow: /`. **No HTTP crawl of www.courtlistener.com without written permission.** **ToS** (gate, raw wiki HTML, "Updated: August 5, 2026"): the "Automated and Agentic Access" section sets credential and rate-limit rules (*"Do not use multiple accounts, registered clients, or credential rotation to exceed the rate limits that apply to your access level."*) and does not ban scraping, bulk or commercial use. The privacy section lists defending against "automated scraping" as a purpose. Bulk files are *"regenerated quarterly"* and are *"snapshots, not deltas"*. |
| Redistribute-verbatim | **YES for opinions and FLP-authored data** (public domain), **with exceptions** for third-party works inside filings. Not verified per document class |
| Relicense-compatible | **Yes with a notice.** Public-domain text may sit in a CC BY 4.0 dataset, but we cannot assert a licence over it; the dataset notice should say the court text is public-domain and not licensed by us, and credit CourtListener / FLP as the source (a courtesy, not a condition found). Do not imply FLP endorsement of any AI-generated summary |
| Action | **(a) with conditions, bulk route only.** Ingest from the quarterly bulk files on the S3 bucket. Never crawl www.courtlistener.com (robots `Disallow: /`). Use the API only if the user rules that a credentialed API client is not a crawler under that robots file; otherwise ask FLP, as the robots file invites. Per-document provenance flag; exclude or downgrade to (c) any third-party copyrighted works; carry the non-endorsement line for generated summaries; privacy review of party names before ingest. |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising) of the bulk-data wiki and the ToS wiki (both returned, not truncated per tool); `courtlistener.com/terms/` and `/robots.txt` and `free.law/terms-of-service` returned 403 / 403 / 404; WebSearch x1 (search-extract tier: the May 2026 API membership). GitHub API for `freelawproject/courtlistener` (software; `license` `NOASSERTION`; not the data licence). Source kind: rendered HTML via a summarising converter + one GitHub API field. Gate 2026-10-03: raw curl re-reads; see the cells above. |
| Non-English / facts-only | English. Facts + link + original summary is available but not needed for licence reasons |

### T1.5 FTC enforcement actions involving AI (ftc.gov)
*Content class:* press releases, case pages, complaints, orders, business-blog
posts under `ftc.gov/legal-library` and `/news-events`. *Language:* English
(some Spanish pages under `/es/`). AI relevance is a filter problem.

| Field | Value |
|---|---|
| Cleanliness score | **2** (statute plus FTC's own policy; third-party carve-outs) |
| License | **US federal work; the FTC says so itself.** Statute: **17 U.S.C. s105**, *"Copyright protection under this title is not available for any work of the United States Government, but the United States Government is not precluded from receiving and holding copyrights transferred to it by assignment, bequest, or otherwise."* (text as verified verbatim by red-reviewer via curl on 2026-10-03, cited in `source-expansion-evaluation.md` s1E.2; **not re-fetched here**). FTC Website Policy, `https://www.ftc.gov/policy-notices/website-policy` (WebFetch 2026-10-03, extract; a second fetch of `/site-information/website-policy` returned the same clauses): *"Most material on the FTC's website is considered work of the United States Government, meaning that the material is in the public domain and is not subject to copyright restrictions (17 U.S.C. 105)."* (verified by red-reviewer via curl, 2026-10-03); *"The use, duplication, or redistribution of such material should be accompanied by appropriate attribution, where feasible (e.g., 'Source: United States Federal Trade Commission, www.ftc.gov')."*; *"In addition, any copyrighted work that consists predominantly of material produced by the FTC or other U.S. government agency must provide notice identifying such material and stating that it is not subject to copyright protection (17 U.S.C. 403)."*; third-party: *"is unable to grant or deny permission for any materials that may be posted on its website containing work copyrighted in whole or part by third parties"* (found *"in or included with public comments and filings, incorporated as photos or other graphics in FTC webpages or other materials prepared by our contractors"*); *"Fraudulent or deceptive use of any FTC material is strictly prohibited, and, except where expressly authorized, no FTC endorsement or affiliation shall be stated or implied."* Carve-outs: public comments and filings by third parties, contractor-prepared materials, photos and graphics, defendants' exhibits attached to FTC complaints, FTC seals (18 U.S.C. 701). Court orders and complaints filed by the FTC are federal-employee work, but attached exhibits may not be |
| Scrape-permitted | **robots.txt (gate, curl, full file, 2026-10-03):** `User-agent: *`, `Crawl-delay: 5`. Drupal disallows: `/core/`, `/profiles/`, `/admin/`, `/comment/reply/`, `/filter/tips`, `/node/add/`, `/search/`, `/user/register|password|login|logout`, their `/index.php/` twins, `/README.txt`, `/web.config`. Also `/es/node/*`, `/*/comment/*`, and query forms with `combine=` or `items_per_page=`. Plus eight legacy paths: three 2018-2019 `/news-events/events-calendar/` conference pages and five `/sites/default/files/documents/` `.htm`/`.shtm` statements. **`/legal-library/` and `/news-events/news/` are not disallowed; `/search/` is.** The Website Policy has no automated-access clause (raw grep 0 hits; "bulk" appears only as the "Bulk Publications" nav item). The Privacy Policy extract has no copyright or scraping wording |
| Redistribute-verbatim | **YES for FTC-authored text** (in the US by statute; outside the US not assessed). **NO / unknown for third-party material** inside filings and comments |
| Relicense-compatible | **Yes with a notice,** as for CISA-authored text in s1E.2: a CC BY 4.0 dataset may carry public-domain text, but we do not assert a licence over it; the dataset notice says FTC-authored text is a US government work. Never imply FTC endorsement |
| Action | **(a) with conditions:** honour Crawl-delay 5; per-document provenance flag; exclude third-party filings/comments and exhibits; attribution line "Source: United States Federal Trade Commission, www.ftc.gov"; no endorsement language. Case pages under `/legal-library/` are reachable under robots; discover them from the legal-library browse pages, never `/search/`; the dataset notice also meets the 17 U.S.C. 403 notice |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `ftc.gov/robots.txt`, `/policy-notices/website-policy`, `/site-information/website-policy`, `/policy-notices`, `/policy-notices/privacy-policy`, `/` (footer links); `/about-ftc/website-policies` 404. s105 text taken from the gate record, not re-fetched. Source kind: rendered HTML via a summarising converter (the positive FTC clauses are quoted by the tool; absences and the disallow list are method-exposed) |
| Non-English / facts-only | English (Spanish mirrors exist; skip). Facts + link + original summary is uncontested but not needed for FTC-authored text |

### T1.6 0din (0din.ai, Mozilla GenAI bug bounty)
*Content class:* GenAI model and application vulnerability disclosures published
after mitigation, plus a "0DIN Intel" threat feed. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **2** (explicit CC BY 4.0 grant by the publisher on its own disclosures corpus; conditions: field filter, attribution, staleness). |
| License | **CC BY 4.0 for the public disclosures corpus (gate-found 2026-10-03, raw; refutes "no licence found").** The 0DIN blog `https://0din.ai/blog/public-disclosures-corpus` (2026-05-15) says the corpus is *"distributed as a weekly versioned JSONL dataset on Hugging Face and Mozilla Data Collective — same data as 0din.ai/disclosures"*. Hugging Face API `api/datasets/0dinai/public-disclosures` (structured): `license:cc-by-4.0`, `gated: false`. Dataset card: *"Creative Commons Attribution 4.0 International (CC-BY-4.0)"* and *"Attribute 0DIN (<https://0din.ai>) when redistributing or building on this dataset."* `manifest.json`: 80 records, generated 2026-05-15. For allowlisted disclosures the records include *"pinned messages, variant prompts (with industry grouping preserved), and the current-version detection signature"*. The Master Services Agreement is a PDF at `0din.ai/services_agreement`, "last updated on April 2, 2026"; the earlier 404 was a guessed path. It binds Customers of ordered Services; under s5.2 Usage Restrictions, (j) bars them from *"engage in web scraping or data scraping on or related to the Services"*. 0DIN Intel docs footer: *"0DIN Intel content for licensed users only."* (all verified by red-reviewer via curl, 2026-10-03). **First-pass text follows, superseded for the HF corpus above; it still describes the 0din.ai site pages, for which no licence was found:** Bug Bounty Program Terms and Conditions, `https://0din.ai/policy` (WebFetch 2026-10-03, extract): *"All submissions will be covered under Mozilla's Website & Communications Terms of Use, granting us permission to make use of all submissions."*; publication: *"we will post and advertise the vulnerability publicly...we will provide (optional) credit to the discovering Researcher"*; and *"For model vulnerabilities, we will publish details of the vulnerability once we determine, in our sole discretion, that the vulnerability has been mitigated"*. The extract says the policy does **not** specify copyright ownership or public reuse. Mozilla Websites & Communications Terms of Use, `https://www.mozilla.org/en-US/about/legal/terms/mozilla/` (extract): submitters grant *"a nonexclusive, royalty-free, worldwide, sublicensable (to those we work with) license to use your Submission in connection with the Communications"*; Mozilla "generally releases its own content under Creative Commons or Mozilla Public License" but some content comes from sources that "prohibit further use ... without advance permission". That gives Mozilla a licence, not the public one, and is generic, not specific to 0din.ai. The 0din.ai footer (homepage extract) lists "Privacy", "Policy", "Services Agreement" and "Legal Archive"; **`/terms`, `/services-agreement` and `/legal` returned 404 (guessed paths; the gate found and read the MSA at `/services_agreement`, above)**. The GitHub repo `0din-ai/0din.ai` has `license: null` (API) and holds no advisory data. The homepage markets a paid "AI Vulnerability Intelligence" feed (Probe Packs); the "0DIN Intel" docs (read by the gate, above) restrict Intel content to licensed users; published disclosures are reusable through the CC BY 4.0 HF corpus, and the site pages themselves carry no licence (gate: one `/disclosures/` page, raw, no licence or copyright text) |
| Scrape-permitted | **robots.txt** (`https://0din.ai/robots.txt`, WebFetch 2026-10-03, extract, complete): `User-agent: *`; `Disallow: /admin`, `/api/`, `/api-docs`, `/jobs`, `/letter_opener`, `/up`, `/rails/`, `/users`; `Allow: /`; sitemap at `/sitemaps/sitemap.xml.gz`. Public advisory pages (`/disclosures/`, 82 URLs in the sitemap; gate) are not disallowed; the **API is disallowed**. **ToS:** `/policy` has no automated-access clause (gate, raw grep, 0 hits); the MSA's no-scraping term binds Customers of ordered Services (see License) |
| Redistribute-verbatim | **YES for the HF corpus under CC BY 4.0, minus the `messages`, `variant_prompts` and detection-signature fields** (jailbreak prompts and model outputs, i.e. raw payload text, which the project does not carry). **NO / UNKNOWN** for site pages outside the corpus and for 0DIN Intel. |
| Relicense-compatible | **YES** (CC BY 4.0 to CC BY 4.0, attribution to 0DIN). |
| Action | **(a) with conditions:** ingest from the HF dataset only, pinned to a revision, recording `manifest.json` `generated_at`; drop the prompt, response, variant and signature fields; attribution "0DIN (https://0din.ai), CC BY 4.0"; never use `0din.ai/api/` (robots-disallowed) or the 0DIN Intel feed (MSA; licensed users only); record the mirror's lag (last export 2026-05-15 despite "weekly"; 80 records vs 82 site disclosures). |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `0din.ai/policy` (read, extract), `/` (footer links), `/robots.txt` (read in full), `/terms`, `/services-agreement`, `/legal` (404), `mozilla.org/.../terms/mozilla/` (extract); GitHub API for `0din-ai/0din.ai` (structured); WebSearch x1 (titles and summaries; surfaced `0din.ai/privacy`, `0din.ai/privacy/2025-02-24` and an `0din-ai-mozilla.fastly-edge.com` mirror, none read). Source kind: rendered HTML via a summarising converter. Gate 2026-10-03: raw curl re-reads; see the cells above. |
| Non-English / facts-only | English. Facts + link + original summary is not shown to be contested |

### T1.7 FIRST EPSS (enrichment only)
*Content class:* a daily 0-1 exploitation-probability score and percentile for
every CVE (CSV, API at `api.first.org`, GitHub). **Enrichment only:** numbers
joined to existing CVE-keyed entries, not new incidents. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (a licence exists but is purpose-limited and revocable, so it is not CC BY 4.0-compatible; facts + link not contested). Primary pages read by the gate; not provisional. |
| License | **Purpose-limited licence, not an open one (gate-found 2026-10-03, raw).** FIRST Services Terms of Use, `https://www.first.org/about/policies/terms` ("Effective at September 2023"): "Services" includes *"API (Public)"*; `api.first.org/epss/` calls itself "FIRST.Org API v1". *"FIRST grants you a nonexclusive, nontransferable, revocable, limited license to view, copy, print, and distribute Content retrieved from the Services to the extent permissible under applicable laws only for vulnerability disclosure, cybersecurity incident response, or preventative cybersecurity uses"*; *"You may not use any Content available via the Services in any other manner or for any other purpose without the prior written permission of FIRST"*. `https://www.first.org/copyright`: *"All documents available on this site may be protected under the U.S. and Foreign Copyright Laws. Permission to reproduce may be required."* `https://www.first.org/epss/data`: the API *"should not be used for bulk downloads"*. The daily CSV is served from `epss.empiricalsecurity.com`, and the history repo `empiricalsec/epss_scores` has API `license: null` and no licence text in its README (all verified by red-reviewer via curl, 2026-10-03). **First-pass extract text follows (superseded where it conflicts):** EPSS home, `https://www.first.org/epss/` (WebFetch 2026-10-03, extract): *"EPSS publishes a 0-1 probability (with ranking percentiles) every day for every CVE and makes the data freely and openly accessible via CSV and API as well as a github repo"*; scores are "generated by Empirical Security and published freely to the community". EPSS FAQ, `https://www.first.org/epss/faq` (extract): *"EPSS scores are published freely via CSV download and API with no registration required."* and *"Attribution is requested when EPSS data is used in publications or products."* The training data cannot be shared because *"several data partners share exploitation telemetry under agreements that prohibit redistribution"*; that concerns the model's training data, not the published scores, but it shows partner-data terms sit behind the product. `https://www.first.org/epss/api` and `https://www.first.org/terms` returned **404**; `https://www.first.org/epss/data_stats` was not fetched. |
| Scrape-permitted | **robots.txt** (`https://www.first.org/robots.txt`, extract): `User-agent: *`, `Disallow: /signin*`, `Disallow: /_/links/*`; the EPSS pages are not disallowed. **`api.first.org` robots.txt was not fetched in the first pass (the gate's result follows).** The API is the published access route and needs no registration (FAQ extract). **ToS:** none located (**ABSENCE FINDING, method-suspect**; refuted by the gate, see License). `api.first.org/robots.txt` returns 404 (no rules declared); the API JSON carries `"access":"public"` and no licence key (verified by red-reviewer via curl, 2026-10-03) |
| Redistribute-verbatim | **NO** without FIRST's written permission. A purpose-limited, revocable licence cannot pass into a CC BY 4.0 dataset; whether daily scores are copyrightable is still not assessed. |
| Relicense-compatible | **NO** without FIRST's written permission (same reason). |
| Action | **(d) light:** ask FIRST (`first.org` contact page not read) whether EPSS scores may be redistributed inside a CC BY 4.0 dataset with attribution. Interim shape if the user wants none: store the CVE id and a **link to the EPSS API URL** for that CVE, not the score values, until answered. If the user rules to proceed anyway, the ruling must account for the FIRST Services Terms of Use (purpose-limited, revocable), not only the "freely and openly accessible" statement; record the score with its as-of date and the attribution line "EPSS, FIRST.org" |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `first.org/epss/` and `/epss/faq` (read, extracts), `/epss/api`, `/terms`, `/epss/data_stats` (404), `/robots.txt` (read). No shell, no GitHub API call for an EPSS repo. Source kind: rendered HTML via a summarising converter (**weak for absences; the central finding here is an absence**). Gate 2026-10-03: raw curl re-reads; see the cells above. |
| Non-English / facts-only | English. Facts + link + original summary is uncontested; as enrichment, the score is the only new content |

### T1.8 OpenSSF malicious-packages (github.com/ossf/malicious-packages)
*Content class:* reports of malicious packages in OSV schema (ids `MAL-YYYY-N`),
for npm, PyPI, crates.io and other OSV ecosystems; community and automated
contributions. *Language:* English. AI relevance is a **filter problem**: the
repo is overwhelmingly generic npm/PyPI malware; the AI/ML subset (packages
impersonating or trojanising ML libraries) is small.

| Field | Value |
|---|---|
| Cleanliness score | **2** (explicit permissive licence from a structured source; conditions: Apache notice carriage, no inbound-licence statement found for contributed reports) |
| License | **Apache-2.0 (structured).** GitHub API `https://api.github.com/repos/ossf/malicious-packages`, `license` field: `spdx_id` **`Apache-2.0`**, name "Apache License 2.0" (WebFetch of the JSON, 2026-10-03). `LICENSE` in the repo root: *"Apache License / Version 2.0, January 2004"* (raw file, extract). OSV data page, `https://google.github.io/osv.dev/data/` (extract): *"OpenSSF Malicious Packages: Apache 2.0"*. The repo root has no NOTICE file (API contents listing: `LICENSE`, `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CONTRIBUTION-GUIDELINES.md`, `osv/`, `docs/`, `site/`, Go sources). README (extract) states no licence for the reports themselves and names prior sources (GitHub Advisory Database filtered for malware; PyPI malware registries; Datadog's malicious-software-packages dataset). CONTRIBUTING (extract) states no DCO or CLA and no inbound licence (**ABSENCE FINDING, method-suspect**): the Apache-2.0 position for contributed reports rests on the repo-wide licence alone. GitHub's inbound=outbound rule (ToS D.6) reaches only PR contributions, and the PR author may not hold the rights to a vendor feed. CONTRIBUTING (raw, verified by red-reviewer via curl, 2026-10-03) also describes bulk imports via `cmd/ingest` and **automated ingestion from contributors' AWS S3 or Google Cloud Storage buckets**, which is not a GitHub contribution at all, and states no licence term for either. README, CONTRIBUTING and CONTRIBUTION-GUIDELINES contain no licence, DCO, CLA or copyright text (raw grep, 0 hits). The score stays 2; inbound licensing is a listed condition. Apache-2.0 is a software licence applied to data; it is permissive and its notice conditions are met by carrying the licence and attribution |
| Scrape-permitted | **robots.txt:** not applicable to `raw.githubusercontent.com` file access; GitHub's own terms govern (see T1.10: GitHub AUP defines "scraping" as automated extraction from the Service and excludes the API; the repo can be **cloned**, which is not scraping). The OSV API (`api.osv.dev`) is the documented route (`SOURCE_LICENSES.md` s2.4: "official public API designed for this query pattern"). **ToS:** no repo-level access restriction located (**ABSENCE FINDING, method-suspect**) |
| Redistribute-verbatim | **YES** under Apache-2.0: give recipients a copy of the licence, retain attribution notices, mark changes. Third-party credits and references inside reports stay with their authors |
| Relicense-compatible | **YES with conditions, but NOT relicensable.** Apache-2.0 does not permit re-licensing the reports as CC BY 4.0; the dataset must ship the reports as **Apache-2.0 components** within a CC BY 4.0 collection and say so in NOTICE-DATA (the model `SOURCE_LICENSES.md` s2.4 uses: the originating database's licence applies per record). Whether Apache-2.0 patent and attribution terms are acceptable to the project is a user ruling |
| Action | **(a) with conditions:** per-record `source` naming the OpenSSF Malicious Packages database and carrying "Apache-2.0"; add the Apache-2.0 text to the dataset's licence bundle; filter by an AI/ML-ecosystem rule defined in the pipeline brief. **Overlap flag (must route):** OSV.dev is already ingested (`SOURCE_LICENSES.md` s2.4) via `api.osv.dev/v1/query` over PyPI/npm/Go targets, and `MAL-` records are served by that API. Row 2.4 says *"every source database actually reachable by this script is CC-BY 4.0"*, but OSV's own data page lists OpenSSF Malicious Packages as Apache-2.0 and PyPI/npm queries can return `MAL-` records; Grep shows `MAL-2026-3607` as an alias in an existing record. Row 2.4's sentence is **false** (gate 2026-10-03): the tracked `ingest/cve_nvd_expanded.json` holds 2 OSV records sourced from `MAL-` ids (MAL-2026-3607, MAL-2026-2144) with verbatim OpenSSF report text; the published `data/incidents.json` carries no such text (MAL-2026-3607 appears only as a source id and OSV link on INC-08450, whose description is GHSA text). This is a truthfulness defect candidate in a live surface (corrected in place, per working agreement 4), not a reason to defer the row |
| Date-checked | 2026-10-03 |
| Retrieval method | **Structured:** GitHub API JSON `repos/ossf/malicious-packages` (`license` object) and `.../contents` (root listing). **Rendered/extract:** WebFetch of `raw.githubusercontent.com/.../LICENSE` and `/CONTRIBUTING.md`, `github.com/.../README.md`, `google.github.io/osv.dev/data/`; local Grep of `data/incidents.json` and `docs/SOURCE_LICENSES.md`. Positive licence finding rests on the API field (not exposed to the false-negative failure); the inbound-licence absence rests on a summarising fetch |
| Non-English / facts-only | English. Facts + link + original summary is uncontested but not needed |

### T1.9 Hugging Face security advisories / malicious-model disclosures
*Content class (as named in the reconstruction record):* HF-published
advisories and malicious-model reports. **Refuted: no such source exists.**

**What was actually found (all 2026-10-03):**
- `https://huggingface.co/docs/hub/security` (extract) is a documentation page
  about Hub security features (tokens, 2FA, SSO, GPG, malware scanning, pickle
  scanning, secrets scanning, and the Protect AI and JFrog third-party scanners)
  plus `security@huggingface.co` for questions. It lists **no advisory feed,
  database or disclosure archive**.
- GitHub API `orgs/huggingface/repos?per_page=100&sort=updated` (first page by
  update time, extract of the list): no repository named `security`,
  `advisories` or `malicious` (agents-course, hub-docs, lerobot, transformers,
  trl, diffusers, datasets, text-generation-inference, and others). The gate
  later checked all 469 org repos (see A20); no advisory repo.
- Vulnerabilities in HF-owned open-source libraries are published as GitHub
  Security Advisories and CVEs, so they reach GHSA and NVD, both already
  ingested. This was not independently enumerated.
- Malicious-model disclosures are written by third parties (JFrog, Protect AI,
  Wiz, and others, per a WebSearch result list) and belong to the existing
  vendor-blog class; they are not HF content.
- Per-repository scan status (Protect AI / JFrog flags) is shown on model pages;
  it is data about third-party uploads, with per-repo licences and no
  dataset-level licence.

| Field | Value |
|---|---|
| Cleanliness score | **n/a for the named source (it does not exist).** For the nearest real thing, per-model scan flags via the Hub API: **1** (unknown) |
| License | HF Terms of Service, `https://huggingface.co/terms-of-service` (WebFetch 2026-10-03, extract): *"You own the Content you create!"*; *"If you decide to set your Repository public, you grant each User a perpetual, irrevocable, worldwide, royalty-free, non-exclusive license to use, display, publish, reproduce, distribute, and make derivative works of your Content through our Services and functionalities"* (verified by red-reviewer via curl, 2026-10-03); **the licence runs only "through our Services and functionalities", so it gives a downstream dataset nothing**; *"Open Source license terms are not intended to be replaced or overridden"*. No site-wide data licence for scan results or security metadata found |
| Scrape-permitted | **robots.txt** (`https://huggingface.co/robots.txt`, extract, complete): `User-agent: *`, `Allow: /`, sitemap. **ToS:** no clause on scraping, crawling or rate limits in the extract (**ABSENCE FINDING, method-suspect**) |
| Redistribute-verbatim | **UNKNOWN** for scan flags and metadata (per-uploader licences; no dataset-level grant) |
| Relicense-compatible | **UNKNOWN** |
| Action | **Recommend: drop T1.9 as named; do not evaluate further.** Replacement and rationale below. If the user wants HF-side signal anyway: **(c)** facts + link (model repo URL, scanner verdict, date), and **(d)** a question to security@huggingface.co on reuse of scan results |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `huggingface.co/docs/hub/security`, `/terms-of-service`, `/robots.txt`; GitHub API `orgs/huggingface/repos` (first page, structured but limited); `api.github.com/repos/huggingface/hub-docs` (`license` `Apache-2.0`, docs repo only); WebSearch x1 (titles and summaries). Source kind: rendered HTML via a summarising converter + GitHub API JSON |
| Non-English / facts-only | English |

**Recommended replacement for T1.9 (not verified; a candidate to evaluate, not a row):**
the value the record wanted is *AI model-supply-chain security disclosures*.
Two options, in order:
1. **Do not add a source.** Those disclosures already arrive as (i) GHSAs/CVEs
   for HF libraries (ingested) and (ii) vendor blog posts from JFrog, Protect AI
   and Wiz, which fall in the existing vendor-blog class. A row would add no new
   licence-clean data.
2. **If a slot must be filled:** the **Zero Day Initiative published advisories**
   (zerodayinitiative.com), which regularly cover ML-framework and AI-product
   bugs. I have **not** fetched its terms or counted AI-relevant items; it is a
   candidate only, to be evaluated under the same discipline, and I make no claim
   about its licence. The alternative is a user-named source.

### T1.10 GitHub Security Lab advisories (securitylab.github.com)
*Content class:* GHSL coordinated-disclosure advisories (`GHSL-YYYY-NNN`) with
CVE ids, discovered by GitHub Security Lab, many in open-source projects
including some AI/ML code (a sample advisory, GHSL-2025-115, covers NVTabular
`Workflow.load` using `cloudpickle`). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (no content licence found; terms unclear; scraping defined and conditionally excepted; facts + link not shown to be banned) |
| License | **No content licence found on the advisory pages.** A sample advisory, `https://securitylab.github.com/advisories/GHSL-2025-115_NVTabular/` (WebFetch 2026-10-03, extract; tool said not truncated), shows the footer *"GitHub Inc. (c) 2024"* with links to GitHub's Terms and Privacy, and no licence or reuse text. The advisories index (extract) states: *"We publish vulnerabilities here only after patches are available."* GitHub API for `github/securitylab`: `license` **`MIT`** (structured) with description "Resources related to GitHub Security Lab"; that repo holds exploits and resources, not the advisory pages, and its MIT licence does not extend to the site. GitHub Terms of Service, `https://docs.github.com/en/site-policy/github-terms/github-terms-of-service` (extract): content ownership and licences are about *user* content (D.3 "You own Your Content"); API terms (Section H) prohibit abuse and excessive requests. GitHub Acceptable Use Policies (extract): *"Scraping refers to extracting information from our Service via an automated process, such as a bot or webcrawler. Scraping does not refer to the collection of information through our API."*; permitted exceptions: *"Researchers may use public, non-personal information from the Service for research purposes, only if any publications resulting from that research are open access."* and *"Archivists may use public information from the Service for archival purposes."* That is an exception for researchers, not a licence to redistribute. **Licence-clean route:** each GHSL advisory with a CVE normally has a GHSA record in the GitHub Advisory Database, which is **CC BY 4.0** (GitHub site-policy "additional products and features", extract: *"The GitHub Advisory Database is licensed under the Creative Commons Attribution 4.0 license"*) and is already ingested; the CVE record and NVD entry are covered by the CVE ToU. A GHSL write-up adds narrative detail (timeline, PoC) that GHSA may not carry; that narrative is the uncovered part. Whether a given GHSL advisory has a matching GHSA record was not enumerated in general, but a GHSA twin exists for the sample: CVE-2025-33214 maps to GHSA-rggg-jp6v-h52j (GitHub API; verified by red-reviewer via curl, 2026-10-03) |
| Scrape-permitted | **robots.txt (gate, curl, 200 text/plain):** the entire file is `Sitemap: https://securitylab.github.com/sitemap.xml`. There are no User-agent or Disallow lines, so robots declares no restriction. **ToS:** GitHub's ToS defines "Website" to include *"GitHub-owned subdomains of github.com"*, so the ToS and AUP govern securitylab.github.com. AUP s6: *"You will not reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service without our express written permission."* AUP s7 allows the use of information *"regardless of whether the information was scraped, collected through our API, or obtained otherwise"* for researchers (open-access publications only) and archivists. The score stays 1: s6 restricts reproduction of the Service, not facts. It could fall to 0 if the researcher exception is read as not covering a redistributed dataset. (verified by red-reviewer via curl, 2026-10-03) |
| Redistribute-verbatim | **NO / UNKNOWN** for the advisory text (no grant found). **YES under CC BY 4.0** for the GHSA record (already ingested) |
| Relicense-compatible | **NO / UNKNOWN** for the GHSL page text; **YES** for GHSA (CC BY 4.0 to CC BY 4.0, attribution to the GitHub Advisory Database) |
| Action | **(c) facts + link + original summary** for GHSL pages (GHSL id, project, CVE, CWE, dates, link, our own summary), taking verbatim description text only via the GHSA/CVE routes. **(d)** optional: ask GitHub (`securitylab@github.com`, address not verified here) whether GHSL advisory text may be reused. robots.txt declares no restriction, but AUP s6 bars reproducing any portion of the Service; take only facts and links from the site. Note possible near-duplication with GHSA at the entry level (dedupe key: CVE id) |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `securitylab.github.com/advisories/` and one advisory page, `/robots.txt` (pointer only), `docs.github.com` ToS, AUP, additional-products pages; GitHub API JSON `repos/github/securitylab` (structured: `license`); search for `github/securitylab-website` via the API returned 0 results. Source kind: rendered HTML via a summarising converter + one GitHub API field |
| Non-English / facts-only | English. Facts + link + original summary is not shown to be contested |

---

## Brief vs. found

The task said to refute reconstructed names that are poor choices.

1. **T1.9 (Hugging Face security advisories / malicious-model disclosures) is a
   poor choice and should be dropped.** No advisory feed or database exists
   (docs page lists features only; no advisory repo among all 469 HF org repos (gate));
   HF-library vulns arrive through GHSA/NVD; malicious-model write-ups are
   third-party vendor posts. Replacement: none required; if a slot must be
   filled, ZDI advisories as an unverified candidate (see T1.9).
2. **T1.8 (OpenSSF malicious-packages) is partly a duplicate.** OSV.dev is
   already ingested and serves `MAL-` records; the corpus already holds
   `MAL-` aliases. The new part is the AI/ML subset, which is a filter, not a
   source. The Apache-2.0 position also contradicts row 2.4's sentence that
   every reachable OSV database is CC-BY 4.0.
3. **T1.10 (GitHub Security Lab) is largely a duplicate** of GHSA/NVD at the
   fact level; only the narrative text is new, and it has no licence.
4. **T1.3 "there may be a GitHub CERTCC/ data repo": true but not an open
   licence.** `Vulnerability-Data-Archive` is archived (last data 2020-06-03,
   ~6% of its records are published notes) with a custom non-open licence
   whose nearest current text permits reproduction in its entirety, without
   modification (gate, 2026-10-03). The SEI TOU (scope: SEI websites) likely
   governs kb.cert.org and bars reproduction and mirroring; score stays 1.
5. **T1.4 / T1.5 premise "court records are public domain" and "US federal
   works": confirmed**, with third-party carve-outs in both. The reconstruction
   record's framing "site and API terms apply" is correct for CourtListener,
   and understated: its robots.txt is `User-agent: *` `Disallow: /` (the
   first-pass "403 = fetch limit" reading was refuted by the gate), so only the
   bulk S3 route is sanctioned. For FTC the framing is thin: no access clause,
   `/legal-library/` is not disallowed, and a 17 U.S.C. 403 notice is required only for a work consisting predominantly of US government material.
6. **T1.7 EPSS "usage terms":** the first-pass "no formal terms found" was
   **refuted by the gate**. FIRST's Services Terms of Use cover the public API
   with a revocable licence limited to vulnerability-disclosure, incident-
   response or preventative-cybersecurity uses (the guessed `/terms` path was
   a 404; the footer-linked `/about/policies/terms` exists). Score stays 1, for
   a different reason, and is no longer provisional. T1.6 (0din) was refuted
   in the same way: a CC BY 4.0 corpus exists on Hugging Face.
7. **T1.1 / T1.2 are not re-evaluated** (gated rows exist).

None of the eight is a non-existent site, but T1.9 names a source that does not
exist as described.

## Estimates (pipeline-engineer)

**Author:** pipeline-engineer, 2026-10-03. Evidence (commands, raw counts, name
lists): `docs/specs/source-expansion-tranche1-estimates-evidence-2026-10-03.md` and
`.json` (same directory, dated records). Nothing here changes sections 1 to 6 above.
No ingest code exists or is proposed before a user ruling. Method, factor scales and
labels are those of `docs/specs/source-expansion-evaluation.md` sections 4 and 5.

**Labels.** **[M]** = measured on 2026-10-03 (command in the evidence file). **[E]** =
estimated (reasoning given). A "proxy" is a regex over names or titles, spot-read,
not a label. The corpus is `data/incidents.json` in this worktree: 13,361 entries,
`generated` 2026-09-18.

**This is a reconstruction.** Tranche 1 is reconstructed: 8 of its 10 names (T1.3 to
T1.10) were inferred by the foreman from the tranche-2 brief, and only T1.1 and T1.2
were named by the user
(`docs/specs/source-expansion-tranche1-reconstruction-2026-10-03.md`). T1.9 is dropped
(section "Brief vs. found", item 1), so **9 of the 10 names remain**. Of those, this
section estimates 4 (T1.4, T1.5, T1.6, T1.8), carries 2 by citation (T1.1, T1.2), and
lists 3 by name (T1.3, T1.7, T1.10). Any name the user supplies replaces a
reconstructed one and needs its own estimate.

**Not re-measured, carried by citation.** T1.1 CISA beyond KEV and T1.2 huntr: factor
rows are those of tranche-2 sections 4.2 and 5.2, cited, not recomputed. Licence facts
for every row are the gated pre-rows above (PASS at `d1a6774b`); nothing from them is
re-derived here.

**Conduct.** Every request went through `ingest/common.py::fetch_once` (identifying
User-Agent, robots check, per-host spacing; one deviation: the 136-file AVID scan ran at
2.0 s, below tranche 2's 3.0 s). `www.courtlistener.com` was never contacted. No
`ftc.gov` content path was requested (robots.txt could not be verified, below). `0din.ai`
was not contacted (Hugging Face mirror only). Prompt, response and signature fields of
the 0din corpus were never written to disk.

### E.0 Findings that cut across the four estimated sources

1. **`www.ftc.gov` cannot be reached through `ingest/common.py` as it stands.** [M]
   robots.txt returns HTTP 403 to the project User-Agent: 3 separate runs, 2 attempts
   each, plus one explicit fetch; `common.py` fails closed. The tranche-1 gate read the
   same file with curl and a default UA (pre-row T1.5), so not every client is refused
   and the host does **not** meet the evidence standard for
   `ROBOTS_UNVERIFIABLE_ALLOWLIST`. I did not try another User-Agent: `common.py` strips
   caller UAs by design and trying one would be identity evasion. Same shape as
   `www.cisa.gov` in tranche-2 section 4.1.
2. **66 of the 80 records in the 0din Hugging Face corpus are already in the AVID
   repository that wave 1 ingests.** [M] AVID-2026-R0059 to R0124 each cite one
   `https://0din.ai/disclosures/<uuid>`, and all 66 uuids are in the HF corpus. The
   corpus holds 2 of the 66 today (INC-02924, INC-02923). A title comparison found only 1
   of 73, so it badly under-counts; the AVID link was found by reading AVID records.
3. **The corpus already carries a GHSA-sourced malicious-package stream.** [M] 79
   entries titled `Malware in <package>`, all GHSA-keyed, 62 of them AI-named by the
   strict token list. OpenSSF is a second route to the same kind of record, and the
   dedupe key has to be (ecosystem, package name), because the sampled OpenSSF records have `aliases: null` (14 of 14). The packages are not GHSA-less: GitHub's advisory database has a `type=malware` GHSA for 72 of the 73 pypi and 85 of the 85 unscoped npm strict names (gate 2026-10-03, GHSA API `affects=` per name), of which 17 (all npm) are in the corpus today. Most of OpenSSF's AI/ML gap is therefore reachable through the CC BY 4.0 GHSA route the corpus already ingests, by widening its malware filter.
4. **The headline AI litigation and the 2019-2024 FTC AI actions are already in the
   corpus** [M, name probes], through AIAAIC, AIID and OECD sources: 9 of 12 named US
   AI suits and 6 named FTC actions found by title (lists in the evidence file). Both
   sources add the tail and docket-level facts, not the headline cases.
5. **`common.py` reads a whole response into memory** (`resp.read()`), so the 5.14 GB
   CourtListener dockets file cannot be fetched in one call. [M] Chunked `Range`
   requests work through `fetch_once` (an 8,000,000-byte read returned
   exactly the requested bytes and a 300 KB head read decoded). `common.py` also never parses `Crawl-delay` (0 matches
   for the string in the module), so FTC's 5 s must be passed as `min_interval=`.

### E.1 Candidate rows

Each row: **Volume** · **Overlap** (dedupe key stated; not CVE alone) · **Shape** ·
**Fit** · **Reconciliation** (WS4-T2) · **Maint.** (structure 0-3, as tranche-2 section
4.2) · **Non-English**.

#### T1.4 CourtListener / RECAP, bulk S3 route only (licence 2; the site crawl is 0)
- **Volume.** [M] The bulk bucket `com-courtlistener-storage` lists current files
  (newest key 2026-09-30): `dockets` 5.14 GB, `opinion-clusters` 2.47 GB, `opinions`
  55.25 GB (not needed), all bz2 CSV. [M] One 8 MB `Range` read of the dockets file
  parsed to 98,837 dockets (ids 70.7M to 72.05M, created 2025-07 to 2025-12); **1** has a
  core AI-company defendant (Dalal v. Clearview AI, S.D.N.Y., filed 2025-09-19) and 99
  are copyright suits (nature of suit 820). A broader name regex gave 9 hits, of which 2
  to 3 are AI-related and the rest surnames or company names. So **a keyword filter on
  `case_name` is not a method**: it has both false positives and misses captions that
  name no AI company. The workable filter is a curated docket-id list (the corpus's own
  litigation entries plus a hand-curated seed, as WS4-T4 does for packages).
  [E] backlog 100-300 AI-litigation dockets, 10-40 new per year. No measurement supports
  these beyond the 1-in-98,837 density and the name probes; treat V as plus or minus one
  step.
- **Overlap.** [M] 0 corpus entries carry a courtlistener URL. [M] 9 of 12 named US AI
  suits are already in the corpus by title (NYT v. OpenAI, Authors Guild, Getty v.
  Stability, GitHub Copilot, Character.AI, Workday, Clearview); 3 not found by name
  (Kadrey v. Meta, Thomson Reuters v. Ross, Andersen v. Stability; title variants not all
  tried). **Dedupe key: (court_id, docket_number) and the CourtListener docket id.**
  Corpus titles are narrative ("Getty Images sues Stability AI for copyright abuse"), so
  the reference-URL and fuzzy-title tiers of `scripts/merge_and_dedupe.py` will mostly
  miss; matching to existing entries needs a curated crosswalk from docket id to INC id
  [E]. Merging into AIAAIC-derived rows touches the CC-BY-SA `content_license` marker
  (1,517 rows today).
- **Shape.** Bulk CSV on S3, `bz2`, no auth, robots check passes on the bucket host
  [M]. Chunked `Range` reads through `fetch_once` (E.0-5). Per refresh: dockets 5.14 GB
  plus clusters 2.47 GB [M] to download; bz2 blocks are independent, so a partial read
  is possible [M, used for the sample]. Site pages and `/api/` are not used.
- **Fit.** Litigation as a real-world event. Partial mapping: no attack vector, no
  severity, no OWASP code. Enrichment of existing litigation entries (docket number,
  court, filing and termination dates, status) is as valuable as new entries [E].
- **Reconciliation.** Medium. Dockets are mutable (status, termination date, caption).
  Bulk files are snapshots, not deltas (pre-row), so a refresh diffs a curated row set,
  not the file. The table has `blocked` and `date_blocked` columns [M, header]; a blocked
  docket must become `status` plus tombstone, never a silent drop. Privacy review of
  party names is a pre-row condition.
- **Maint.** Structure 2 (fixed CSV schema, 54 columns [M], but 5 GB per refresh and a
  curated seed to keep current).
- **Non-English.** English.

#### T1.5 FTC enforcement actions (licence 2)
- **Volume.** Not measurable: **the host is unreachable through `common.py` (E.0-1).**
  [E] 5-15 AI-related actions per year, from the author's knowledge of the 2023-2025
  pace; no fetch backs it. The corpus signal is [M] 6 entries mention FTC or the Federal Trade Commission in title, description, affected or impact (10 anywhere in the record, references included) and 2 carry an `ftc.gov` URL (INC-07386, INC-04395).
- **Overlap.** [M] By title, Rite Aid, Everalbum, DoNotPay, IntelliVision, Kurbo and Alexa
  COPPA are in the corpus (AIAAIC, AIID); not found: Rytr, Operation AI Comply, Workado,
  Air AI, Ascend Ecom, Click Profit, FBA Machine (names from the author's memory, not
  verified as FTC actions). So the tail is 2024-2026 actions. **Dedupe key: FTC case or
  docket number and the case-page URL**, then party name; not CVE. As with CourtListener,
  existing titles are narrative, so a crosswalk is needed [E].
- **Shape.** HTML under `/legal-library/` reached via browse pages (pre-row), Crawl-delay
  5 passed as `min_interval=5.0`. **Cannot start**: robots unverifiable, fail-closed.
- **Fit.** Enforcement action; partial mapping (as ICO in tranche 2).
- **Reconciliation.** Medium [E]: orders are amended and cases settle; case pages carry
  dates but no machine status.
- **Maint.** Structure 1 if reachable (scraped HTML, a `common.py` argument); **0 as
  things stand**.
- **Non-English.** English; Spanish mirrors under `/es/` are skipped (pre-row).

#### T1.6 0din, Hugging Face CC BY corpus only (licence 2)
- **Volume.** [M] `0dinai/public-disclosures` at revision `9c75d830`: 80 records, last
  modified 2026-05-15, i.e. **4.5 months stale** against the dataset card's "weekly".
  Published: 2025: 53, 2026 to April: 27 (months in the evidence file); 79 of 80 severity
  `low`. All 80 are `guardrail_jailbreak`. **Net-new against the corpus today: 78 of 80**
  [M]; **after wave 1 imports AVID: at most 14** [M], those published 2026-02 to 2026-04.
  [E] Further new records only if the mirror is refreshed; the site lists 82 (pre-row).
- **Overlap.** **Dedupe key: the 0din `uuid`** (the URL form `https://0din.ai/disclosures/<uuid>`
  is what AVID cites [M]). The HF `reference_urls` field is empty in all 80 [M], so the
  link has to be built from the uuid; whether that page resolves was not fetched. The
  reference-URL tier of `merge_and_dedupe.py` matches if the entry carries the same URL
  [E]; fuzzy title would miss (INC-02924 is retitled by curation). No CVE in any record.
- **Shape.** Pinned HF revision, one JSONL (596,614 bytes) plus `manifest.json`, through
  `huggingface.co` (robots allowed [M]); drop `messages`, `variant_prompts` and
  `detection_signature` (present in 6 of 80 records [M]); `researcher_credit` is a
  name or handle in 66 records, a privacy decision for the row [E]. Keep summary, title,
  models, dates, severity, taxonomy and the uuid link.
- **Fit.** Jailbreak and guardrail disclosures: the corpus has `research-demonstrated`
  (41) and AVID-derived entries of this kind. Partial mapping, no CVE or CWE.
- **Reconciliation.** Low. Key is the uuid; the pinned revision diffs cleanly; no
  rejection concept in the schema (1.1.0). A record vanishing between revisions (80 vs
  the site's 82 suggests lag, not removal) becomes `status` plus tombstone.
- **Maint.** Structure 3 (fixed JSONL schema). The risk is staleness, not format.
- **Non-English.** English.

#### T1.8 OpenSSF malicious-packages, AI/ML subset (licence 2, Apache-2.0)
- **Volume.** [M] The repo is large: pypi 11,780 packages (one record each; ids by year
  2023: 6,467, 2024: 2,476, 2025: 1,419, 2026 to 3 Oct: 1,398), rubygems 4,238, nuget
  782, npm **more than 100,000 top-level directories** (the listing truncates at 100,000,
  last name `lintang-tea65`). The AI/ML subset is a **filter problem on package names**,
  and the proxy is poor: strict-token names are pypi 73, npm 91 (first 100,000 only),
  nuget 1, rubygems 1 after removing 100 npm names where `gemini` is a constellation word
  in a tea.xyz token-farming campaign (that removal is itself a heuristic; the 4 npm
  records read were all that campaign). [M, n=10] by summary, 5 of 10 strict pypi names
  target an AI library (instructor-mcp, scikit-leran, mlc-llm-nightly,
  strands-agents-anthropic, ant-mcp-proxy-for-test) and 5 only carry an AI token in the
  name. [E] about 80 AI-library-targeting records in the backlog (166 candidates times
  about one half), range 40-120, and 15-40 new per year (pypi strict names: 2023: 23,
  2024: 9, 2025: 12, 2026 to date: 30). Wide: n=10.
- **Overlap.** [M] 0 of 73 pypi and 17 of 91 npm candidates already have a corpus entry
  `Malware in <name>` (GHSA-keyed); by package name about 90% are net-new (147 of 164).
  [M] 1 corpus entry cites a `MAL-` id (INC-08450). **Dedupe key: (ecosystem, package
  name)**, then GHSA alias; `aliases` is null in 14 of 14 sampled records, so the OpenSSF record carries no CVE or GHSA key; upstream, a `type=malware` GHSA exists for 157 of the 158 unscoped pypi and npm candidates (E.0-3), so a GHSA crosswalk by (ecosystem, package name) is available. The existing 79 GHSA malware entries are CC BY 4.0 and would
  win any text conflict.
- **Shape.** OSV JSON, one file per record, id `MAL-YYYY-N`, in
  `osv/malicious/<ecosystem>/<package>/`. Reachable through `common.py`: the trees API
  (one call per ecosystem; **npm truncates, so it needs per-prefix sharding or a `git`
  route that must be registered in `docs/INGESTION_CONDUCT.md`**) and `raw.githubusercontent.com`.
  Unauthenticated `api.github.com` is limited (documented 60 calls per hour; [M] the
  `X-RateLimit-Remaining` header read 33 down to 30 after about 27 calls). The OSV `all.zip` route was not tried.
- **Fit.** Supply-chain malware. The corpus already holds it as `threat-report` (79
  entries). Records have no severity, CVSS, CWE or CVE [M, 14 of 14]; the mapping is
  partial and the OWASP LLM03 code would come from the filter, not the record.
- **Reconciliation.** Medium. [M] 8 of 14 sampled records have `modified` later than
  `published` (a batch re-import on 2026-03-19 touched several) and the `schema_version`
  is mixed (1.5.0 and 1.7.4). No `withdrawn` field in 14 of 14; the OSV schema defines
  one [E], so a false-positive withdrawal is possible and must become `status` plus
  tombstone. Ids are append-only.
- **Maint.** Structure 2: fixed OSV schema, but a name filter that needs upkeep against
  campaign spam, a truncating npm listing, a rate-limited API, and mixed record
  provenance (`database_specific.malicious-packages-origins` names kam193,
  reversing-labs, amazon-inspector, checkmarx and ossf-package-analysis, none with a
  licence statement of its own, pre-row).
- **Non-English.** English.

**What per-record Apache-2.0 attribution costs here.** The brief notes the project is
excluding `MAL-` records from the OSV ingest because of Apache-2.0 (board note N6). I
could not confirm an exclusion: the board text I read (`PROGRESS.md` on `origin/main`,
`77e04846`) says the fix is to "either filter `MAL-` in the OSV ingest or attribute those
records per record as Apache-2.0", with no decision recorded. **Update 2026-10-03 (gate):** the board recorded the decision at `0641ec1e`, after this section was committed: `MAL-` records are EXCLUDED from the OSV route (`is_openssf_malicious` in `scripts/ingest_cve_nvd_expanded.py`, branch `ws4/wave12-ingest`, not yet on `main`; `SOURCE_LICENSES` row 2.4 states it), with MAL-2026-3607 kept as a bare identifier plus links. The decision is scoped to the OSV route and does not by itself zero a direct, per-record-attributed OpenSSF ingest; it does record that the project declined the per-record Apache cost once, so T1.8 at L=2 needs the user to accept that cost for this route. Costs of the attribute
route, for the roughly 80 rows above:
1. **Schema.** `content_license` in `schema/incident.schema.json` is **one object per
   row** and its `obligations` enum is only `attribution` or `share-alike` [M]. Apache-2.0
   needs the licence text to travel and changes to be stated (Apache-2.0 section 4;
   [E], not re-fetched here), so the enum needs new values and the schema's own
   `$comment` says each new source extends the conditional. A row that merges an AIAAIC
   source (CC-BY-SA, 1,517 rows today) with an OpenSSF source cannot carry two licences
   in one object. Both are WS3 changes.
2. **Surfaces.** The marker is mirrored into the HF export, `incidents.min.json` (marked
   rows only) and STIX `x_content_license` (schema description), so each gains Apache
   rows.
3. **Notice.** One-time: the Apache-2.0 text in the licence bundle and a NOTICE-DATA
   entry stating that records were normalised to the INC schema. Pre-row: no NOTICE file
   in the upstream repo.
4. **Merge discipline.** The marker is sticky and excluded from merge union; if a `MAL-`
   record merges into a GHSA entry, the survivor needs the Apache marker only if OpenSSF
   text is kept.
5. **The cheaper shape.** Taking facts plus link plus our own summary (ecosystem, package,
   dates, `MAL-` id as a link) would avoid items 1 to 4; whether that shape escapes the
   Apache terms is license-auditor's call, not mine.
6. **Already incurred.** The 2 `MAL-` records in `ingest/cve_nvd_expanded.json` carry
   verbatim OpenSSF text today (pre-row T1.8); that is N6, not a tranche-1 cost.

### E.2 Carried by citation (not re-measured)

- **T1.1 CISA beyond KEV.** L2 V1 F1 M1 = **2** (tranche-2 section 5.2, rank 14). `cisa.gov`
  feeds return 403; the structured route is the ICS-heavy CSAF repository.
- **T1.2 huntr.** L2 V2 F3 M3 = **36**, "a filter inside cvelistV5, not additive"
  (tranche-2 sections 4.2 and 5.2). huntr.com serves no report fields; 228 AI-relevant
  CVEs missing from the corpus in the 2024-01 to 2026-06 window.

### E.3 Listed by name only (licence 1; not estimated)

Facts and links only. Corpus counts are **entries** whose JSON contains the string [M],
not the line counts in the summary above (28, 40, 0 lines).

- **T1.3 CERT/CC Vulnerability Notes** (kb.cert.org). 19 corpus entries contain
  `kb.cert.org`; 1 contains a `VU#` id. Licence-clean route to the same facts: CVE
  records and NVD (pre-row T1.3). Links: <https://www.kb.cert.org/vuls/>,
  <https://certcc.github.io/VINCE-docs/copyright/>.
- **T1.7 FIRST EPSS** (enrichment). 0 corpus entries mention EPSS. Links:
  <https://www.first.org/epss/>, <https://www.first.org/about/policies/terms>. Tranche-2
  section 4.2 found EPSS present on 3,873 of 3,873 EUVD items, which is the other route.
- **T1.10 GitHub Security Lab** (securitylab.github.com). 18 corpus entries contain the
  host and 27 a `GHSL-` id. Links: <https://securitylab.github.com/advisories/>. The
  licence-clean twin is the GHSA record (pre-row T1.10).

With L=1 the product ceiling is 27 (V=F=M=3), below huntr's 36 and cvelistV5's 36, so a
later estimate of these three cannot move them above waves 1 or 2.

### E.4 Dropped

**T1.9 Hugging Face security advisories** (section "Brief vs. found", item 1): no such
source exists; not estimated.

### E.5 Non-English

All four estimated sources are English. FTC Spanish mirrors (`/es/`) are skipped. No
translated summary is needed, so the WS0-T3 rule (translations are original prose,
generated offline, never a model call in `make build`) is not engaged.

## Ranking

### R.1 Method

Same as tranche-2 section 5.1: product of L (licence cleanliness of the subset actually
ingested), V (new-entry volume after dedupe against the current corpus), F (corpus fit),
M (inverse maintenance cost), each 0-3; a 0 zeroes the candidate. Scales are copied
unchanged from `docs/specs/source-expansion-evaluation.md` section 5.1. Tranche-2 products
below are **cited, not recomputed**.

### R.2 Tranche-1 factor table

| Candidate | L | V | F | M | Product | Basis |
|---|---|---|---|---|---|---|
| T1.4 CourtListener (bulk S3) | 2 | 2 | 2 | 2 | **16** | V is [E] (100-300 curated dockets); at V=1 the product is 8 |
| T1.6 0din (HF corpus) | 2 | 1 | 2 | 3 | **12** | V=1 because 66 of 80 arrive via AVID in wave 1 (14 left) [M]; at V=2 (AVID skipped or mirror refreshed) it is 24 |
| T1.8 OpenSSF AI/ML subset | 2 | 1 | 2 | 2 | **8** | V=1: about 80 records, 15-40 per year [E], straddles the V=2 line; at V=2 it is 16; at L=1 (Apache not accepted) 4; zero if excluded; dominated by GHSA: 157 of 158 candidates have a CC BY 4.0 GHSA malware twin (E.0-3) |
| T1.5 FTC | 2 | 1 | 2 | 0 | **0** | M=0: robots.txt 403 through `common.py` (E.0-1); if reachable M=1 and the product is 4 |
| T1.1 CISA beyond KEV | 2 | 1 | 1 | 1 | 2 | cited, tranche-2 section 5.2 |
| T1.2 huntr (CVE route) | 2 | 2 | 3 | 3 | 36 | cited; a filter inside cvelistV5 |
| T1.3 CERT/CC, T1.7 EPSS, T1.10 GHSL | 1 | | | | not estimated | listed by name; ceiling 27 |
| T1.9 HF advisories | | | | | dropped | no such source |

### R.3 Cross-tranche ordering

Rank is competition ranking by product, as in tranche-2 section 5.2. Tranche-2 rows are
copied from that table (factors and product as published there); tranche-1 rows are new.
Rows with product 0 are collapsed.

| Rank | Candidate | Tranche | L V F M | Product | Proposed wave | Why |
|---|---|---|---|---|---|---|
| 1 | AVID | 2 | 2 3 3 3 | 54 | 1 (approved, in flight) | cited |
| 2 | cvelistV5 | 2 | 2 2 3 3 | 36 | 1 (approved, in flight) | cited |
| 2 | huntr (CVE route) | 1 (T1.2) | 2 2 3 3 | 36 | 1, as a filter inside cvelistV5 | cited |
| 4 | arXiv cs.CR metadata | 2 | 3 2 2 2 | 24 | 2 (approved; pending outreach) | cited |
| 5 | **CourtListener (bulk)** | 1 (T1.4) | 2 2 2 2 | **16** | **3** | only legal-process source; needs a curated docket seed, privacy review and chunked 5 GB reads; V is [E] |
| 6 | EUVD | 2 | 1 2 3 2 | 12 | 2, enrichment (pending outreach) | cited |
| 6 | ANSSI / CERT-FR | 2 | 3 1 2 2 | 12 | hold | cited |
| 6 | **0din (HF corpus)** | 1 (T1.6) | 2 1 2 3 | **12** | **3, after AVID merges** | 66 of 80 already arrive through AVID; adds at most 14, depends on the mirror being refreshed |
| 9 | BSI / WID | 2 | 1 1 3 3 | 9 | hold | cited |
| 10 | **OpenSSF AI/ML subset** | 1 (T1.8) | 2 1 2 2 | **8** | **4, gated on N6 and WS3** | about 80 records; 157 of 158 candidates have a GHSA malware twin (17 in the corpus), so the cheaper route is the existing GHSA ingest; Apache needs a schema change |
| 11 | NCSC, JVN, ICO | 2 | | 6 | hold / 3 (ICO) | cited |
| 14 | ENISA reports, EDPB register | 2 | | 4 | hold / 3 (EDPB) | cited |
| 16 | CCCS | 2 | | 3 | hold | cited |
| 17 | Garante, CISA beyond KEV (T1.1), Black Hat / DEF CON | 2 / 1 | | 2 | hold (Garante: tranche-2 optional wave 3) | cited |
| 20 | **FTC** and the tranche-2 zero rows (ACSC, JPCERT/CC, CERT-EU, Dutch AP, CNIL, ANPD, OPC, HackerOne, huntr.com direct) | 1 / 2 | | 0 | hold | FTC: unreachable through `common.py` today |
| n/a | CERT/CC, EPSS, GHSL | 1 | 1 | not estimated | hold | listed by name |

**Sensitivity.** None of the tranche-1 estimates exceeds 24, and 24 is reached only at an optimistic V: 0din at V=2, or CourtListener at V=3 (its V is [E], plus or minus one step). So **no estimated tranche-1 source outranks AVID, cvelistV5 or
huntr, and none outranks arXiv except by a tie.** That answers the tranche-2 caveat
(section 5.5) for the names estimated here: of the 8 reconstructed names, none that was
estimated lands above wave 2, and the 3 listed by name have a ceiling of 27. Ordering
among ranks 5 to 10 is within estimation error: one step on V reorders CourtListener,
0din and OpenSSF.

### R.4 Proposed waves

Waves 1 (AVID + cvelistV5 with huntr as a filter) and 2 (arXiv + EUVD as enrichment) are
user-approved and in flight (AVID and cvelistV5/huntr; arXiv and EUVD pending outreach).
Nothing below changes them. These are proposals for a user ruling.

- **Wave 3: legal-process and gap-fill.** (a) **0din**, once AVID's reports are merged:
  one pinned JSONL fetch, dedupe on the uuid URL, expected yield at most 14 entries until
  the mirror refreshes, so it may be deferred without loss. (b) **CourtListener bulk**:
  worth doing only as a curated docket list that enriches existing litigation entries and
  adds the tail. Needs before ingest: the curated seed, a privacy decision on party
  names, a `common.py`-compatible chunked `Range` reader, and handling of `blocked`
  dockets. This sits with tranche-2's optional wave 3 (ICO, EDPB, Garante), which is
  also a regulatory and legal axis; the user's call whether that axis is wanted.
- **Wave 4: OpenSSF AI/ML subset**, only if the user accepts per-record Apache-2.0 attribution for a direct route (N6 excluded `MAL-` from the OSV route at `0641ec1e`; that exclusion does not by itself close this row), and after the WS3 decisions (one licence object per row, the obligations enum). Because 157 of 158 candidates have a CC BY 4.0 GHSA malware twin (E.0-3), the cheaper alternative is to widen the existing GHSA malware filter, which needs neither.
- **Hold:** FTC (unreachable; a route needs either FTC's operator to accept the project
  User-Agent or reviewed evidence that fits the allowlist standard, neither of which
  exists), CISA beyond KEV (cited), CERT/CC, EPSS and GHSL (licence 1, listed by name).

### R.5 What in the brief was not supported or not verified

1. The brief says the project is excluding `MAL-` records from the OSV ingest. The board
   text I read records the choice as open (E.1, T1.8). I treated it as undecided. **Update 2026-10-03 (gate):** the brief was right on substance; the board recorded the exclusion at `0641ec1e`, after this section was written (see the T1.8 update in E.1).
2. The brief describes FTC as reachable "via browse pages, Crawl-delay 5". The browse
   pages are not reachable through `common.py` (E.0-1); Crawl-delay is correct per the
   pre-row but could not be exercised.
3. The pre-row corpus-overlap figures were line counts (28, 40, 0 lines); the entry
   counts are 19, 18 and 0 (E.3).
4. Not measured: the full npm package list (listing truncates), any FTC page content, any
   CourtListener volume beyond one 8 MB window, whether `https://0din.ai/disclosures/<uuid>`
   resolves, and OSV `all.zip` as an alternative OpenSSF route.

## Absence findings for shell verification

**Gate 2026-10-03 results (raw curl):** A1, A2, A3, A5, A6, A8, A9, A10, A13, A17, A18, A20, A21 and A22 CONFIRMED; the items marked below were refuted or answered.

Every item below is an absence or a not-obtained result. Each is presumed
method-suspect (summarising fetch, possible truncation, tag-split HTML). Each
check names an input that would make it fail or false-fire. Run on raw HTML
(`curl -sL`), not on rendered text. Use `-A "Mozilla/5.0"` where the host
returned 403, and record the HTTP status of every fetch, because a 403 or a
bot-challenge page makes "0 hits" meaningless.

| # | Row | Absence claimed | Check | Fails or false-fires if |
|---|---|---|---|---|
| A1 | T1.3 | kb.cert.org robots.txt: 404 | `curl -sIL https://www.kb.cert.org/robots.txt` then `curl -sL https://www.kb.cert.org/robots.txt \| head -50` | Server returns a 404 HTML shell for bots only, or redirects robots.txt to a login page that returns 200 (200 with HTML is not a robots file); compare with the `www`-less host |
| A2 | T1.3 | The note's "Legal" link is dead | `curl -sIL "https://vuls.cert.org/confluence/display/VIN/VINCE+Code+of+Conduct"`; `curl -sL https://www.kb.cert.org/vuls/id/739007 \| grep -io 'href="[^"]*[Ll]egal[^"]*"'` | A cookie/JS-set link differs from the static one; the Confluence redirect target changes with a trailing fragment; check 200 vs 404 on the final URL, not the first hop |
| A3 | T1.3 | No licence/redistribution clause in a note | `curl -sL https://www.kb.cert.org/vuls/id/739007 \| grep -iE 'licen[cs]e\|redistribut\|unmodified\|reproduc\|copyright\|creative commons'` | The clause is split across tags (`...under a </span><a ...>`), so grep a tag-stripped copy too: `curl -sL ... \| sed 's/<[^>]*>//g' \| grep -iE ...`; a page that loads the note by JS from the API (`/vuls/api/`) shows 0 hits for a reason that has nothing to do with absence |
| A4 | T1.3 | **ANSWERED by gate 2026-10-03:** the TOU scope is "SEI websites" and likely governs kb.cert.org (see T1.3). Original: whether SEI terms reach kb.cert.org (the "Service" definition) | `curl -sL https://www.sei.cmu.edu/legal/ \| sed 's/<[^>]*>//g' \| grep -inE 'service\|mirror\|derivative\|non-commercial\|automated\|crawl'`; then repeat on `https://www.sei.cmu.edu/legal/terms-of-use/` (guess) | The terms page differs by path (`/legal/` vs `/legal/terms-of-use/`); the 2018 date may mean a newer page exists; the grep finds "service" 100 times and proves nothing, so read the definition sentence |
| A5 | T1.3 | Archive LICENSE.md wording (extract disagrees with API text) | `curl -sL https://raw.githubusercontent.com/CERTCC/Vulnerability-Data-Archive/main/LICENSE.md` (read the full file, not a grep) | None: this is a plain text file; the check fails only if the file moved branches (use `/HEAD/`) |
| A6 | T1.3 | The "complete and unmodified" wording exists on a primary page | `curl -sL https://www.kb.cert.org/vuls/ \| sed 's/<[^>]*>//g' \| grep -iE 'complete and unmodified\|redistribut'` and the same on `https://certcc.github.io/VINCE-docs/copyright/` | The wording is from the old `cert.org/legal_stuff` page; if absent from kb.cert.org it is the old site's and the search extract was stale (the row would need correcting). A "0 hits" is only meaningful if the page returned 200 and was not a challenge page |
| A7 | T1.4 | **REFUTED by gate 2026-10-03:** CourtListener robots.txt (403) was not a fetch limit; browser UA gets 200 with `User-agent: *` `Disallow: /` (see T1.4) | `curl -sIL -A "Mozilla/5.0" https://www.courtlistener.com/robots.txt` and `curl -sL -A "Mozilla/5.0" https://www.courtlistener.com/robots.txt` | A Cloudflare/DataDome-type challenge returns 403/200 HTML; status 200 with `<html` in the body is not a robots file. If challenged, ask from a different network/browser session |
| A8 | T1.4 | ToS has no clause barring scraping, bulk or commercial use | `curl -sL -A "Mozilla/5.0" https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|crawl\|bulk\|automat\|commercial\|train\|AI'` | The wiki is a JS app (shell page with 0 body text): check that the output contains the phrase "Do not use multiple accounts" before trusting a 0-hit result on the other terms. Also check `https://www.courtlistener.com/terms/` |
| A9 | T1.4 | Bulk-data Public Domain Mark claim | `curl -sL https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data \| sed 's/<[^>]*>//g' \| grep -inE 'public domain\|copyright\|licen'` | JS-rendered wiki as in A8; confirm the page body contains "Bulk Legal Data" |
| A10 | T1.5 | FTC Website Policy has no automated-access clause | `curl -sL https://www.ftc.gov/policy-notices/website-policy \| sed 's/<[^>]*>//g' \| grep -inE 'automat\|scrap\|crawl\|robot\|bulk\|spider'` | A hit on "robot" in boilerplate is not a restriction: read the sentence; 0 hits on a page that returned a bot challenge is meaningless (check status and that the output contains "public domain") |
| A11 | T1.5 | **ANSWERED by gate 2026-10-03:** full robots read; `/legal-library/` not disallowed (see T1.5). Original: the exact disallowed paths (extract said "specific document paths related to FDA/FTC statements and events") | `curl -sL https://www.ftc.gov/robots.txt \| grep -inE 'disallow\|crawl-delay\|legal-library\|news-events\|cases\|enforcement'` | The disallow list may name paths in `/legal-library/` or `/news-events/` that overlap enforcement pages; compare against the URL patterns the pipeline would fetch |
| A12 | T1.6 | **REFUTED by gate 2026-10-03:** 0din Services Agreement exists at `/services_agreement` (the 404s were guessed paths) and a CC BY 4.0 corpus exists on HF (see T1.6). Original claim: Services Agreement / Terms (all 404) and any statement on advisory reuse | `curl -sIL https://0din.ai/services-agreement`; follow the footer link in raw HTML: `curl -sL https://0din.ai/ \| grep -oiE 'href="[^"]*(agreement\|terms\|legal\|privacy\|policy\|archive)[^"]*"'` then read each target | The footer is rendered by JS or uses relative links I guessed wrong (the 404s were guesses, not discovered URLs); a hit is only meaningful if the discovered URL returns 200 |
| A13 | T1.6 | `/policy` is silent on copyright/public reuse | `curl -sL https://0din.ai/policy \| sed 's/<[^>]*>//g' \| grep -inE 'copyright\|licen[cs]e\|reuse\|redistribut\|own\|intellectual\|scrap\|automat'` | The summariser may have dropped a long page tail; the grep must be run over the whole document; clause split across tags (strip tags first) |
| A14 | T1.6 | **REFUTED in substance by gate 2026-10-03:** the Intel docs say "0DIN Intel content for licensed users only"; the sitemap lists 82 `/disclosures/` pages, and the CC BY 4.0 HF corpus was found from it (see T1.6). Original: 0DIN Intel / threat-feed terms (unread) and whether advisories are public pages | `curl -sL https://0din.ai/docs/threat-feed/introduction \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|terms\|redistribut\|attribution\|commercial'`; and `curl -sL https://0din.ai/sitemaps/sitemap.xml.gz \| gunzip \| grep -c '<loc>'` to find advisory URL patterns | Docs may be a SPA (check body length); the sitemap may list only some pages; a gunzip failure means a bot challenge, not an empty sitemap |
| A15 | T1.7 | **REFUTED by gate 2026-10-03:** FIRST terms exist at `/about/policies/terms` and `/copyright` (see T1.7). Original claim: No formal EPSS licence/terms | `curl -sL https://www.first.org/epss/ \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|terms\|attribut\|cite\|commercial\|redistribut\|copyright'`; same on `/epss/faq`, `/epss/user-guide`, `/epss/articles`, `https://www.first.org/legal/`, and `https://www.first.org/about/policies/` (guesses; only discovered URLs count) | The EPSS "Usage" statement may sit in a different page than the ones fetched; a grep over a page missing its footer proves nothing, so also run `grep -oiE 'href="[^"]*(terms\|legal\|privacy\|licen)[^"]*"'` on the home page footer and follow what it finds |
| A16 | T1.7 | **ANSWERED by gate 2026-10-03:** `api.first.org/robots.txt` is 404 (no rules); API JSON has `"access":"public"`, no licence key. Original: api.first.org robots.txt not obtained; API terms | `curl -sIL https://api.first.org/robots.txt`; `curl -sL "https://api.first.org/data/v1/epss?cve=CVE-2021-44228" \| head -c 600` (inspect for any `license` or `terms` JSON key and response headers: `curl -sIL ...`) | A 404 robots.txt on an API host means "no restrictions declared", not "permission"; the JSON may carry no licence key |
| A17 | T1.8 | CONTRIBUTING / README state no inbound licence or DCO/CLA | `curl -sL https://raw.githubusercontent.com/ossf/malicious-packages/main/CONTRIBUTING.md \| grep -inE 'licen[cs]e\|DCO\|sign-off\|CLA\|apache\|copyright'`; same on `README.md`, `CONTRIBUTION-GUIDELINES.md` | Branch name differs (`main` vs `HEAD`); a hit on "licence" in a link title is not a clause: read it. This check is the plain-text kind and is reliable |
| A18 | T1.8 | Repo root has no NOTICE; confirm API `license` | `curl -s https://api.github.com/repos/ossf/malicious-packages \| grep -A4 '"license"'`; `curl -s https://api.github.com/repos/ossf/malicious-packages/contents \| grep '"name"'` | Unauthenticated API rate limiting returns a JSON error (`API rate limit exceeded`) with 403 and zero `license` hits; check status; the API reports the repo's top-level licence only, not per-file |
| A19 | T1.8 | **ANSWERED by gate 2026-10-03:** see T1.8 Action. Original: OSV-ingest overlap: which `MAL-` records the existing ingest stored and what row 2.4 says | `grep -c '"MAL-' data/incidents.json`; `grep -n 'MAL-' data/incidents.json \| head`; `grep -n 'Apache\|CC-BY\|OpenSSF' docs/SOURCE_LICENSES.md` | MAL- ids might appear only as aliases of GHSA ids (as `MAL-2026-3607` does) with the record's text sourced from GHSA (CC BY 4.0), in which case row 2.4's sentence is right in effect; the check must inspect each record's `source`/provenance field, not just the id |
| A20 | T1.9 | **CONFIRMED by gate 2026-10-03:** all 469 org repos (API pages 1-5) checked; only `security-workflows` (CI tooling) and `atif-scan` (no description) match secur or scan; no advisory repo. Original: No HF advisory feed or security-advisory repo | `curl -s "https://huggingface.co/api/models?filter=security" \| head -c 300` is not meaningful; use instead: `curl -sL https://huggingface.co/docs/hub/security \| grep -oiE 'href="[^"]*(advis\|disclos\|cve\|vulnerab)[^"]*"'`; `curl -s "https://api.github.com/orgs/huggingface/repos?per_page=100&page=2" \| grep '"name"'` (pages 2..n); `curl -s https://api.github.com/repos/huggingface/huggingface_hub/security-advisories` | The org has more than 100 repos (only page 1 was read); HF may host advisories under `huggingface.co/docs/hub/security-*` pages not linked from the index; the GitHub advisories endpoint may need auth (404/403 is not "none") |
| A21 | T1.9 | HF ToS has no scraping/crawling clause | `curl -sL https://huggingface.co/terms-of-service \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|crawl\|robot\|automat\|bot\b\|rate limit'` | The ToS is long and the summariser may have truncated; the page is an SPA with server-side text? (check the output contains "You own the Content you create"); content may also be in a separate `content-policy` page |
| A22 | T1.10 | No licence/copyright on GHSL pages beyond "GitHub Inc. 2024" | `curl -sL https://securitylab.github.com/advisories/GHSL-2025-115_NVTabular/ \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|copyright\|creative commons\|reuse\|(c)\|©'`; also `curl -sL https://securitylab.github.com/ \| grep -oiE 'href="[^"]*(terms\|licen\|legal\|policy)[^"]*"'` | A licence may live in the `securitylab-website`/`github/securitylab` repo's README or a `LICENSE` that the site footer links to: check `curl -s https://api.github.com/repos/github/securitylab/contents \| grep name` and follow the footer links |
| A23 | T1.10 | **ANSWERED by gate 2026-10-03:** the whole robots.txt is a `Sitemap:` line, no restrictions (see T1.10). Original: securitylab.github.com robots.txt (only a sitemap pointer returned) | `curl -sIL https://securitylab.github.com/robots.txt`; `curl -sL https://securitylab.github.com/robots.txt` | The extract may have dropped the `User-agent`/`Disallow` lines; 200 with HTML is not a robots file |
| A24 | T1.10 | **ANSWERED by gate 2026-10-03:** the GitHub ToS "Website" includes GitHub-owned subdomains, so the AUP governs; GHSA twin GHSA-rggg-jp6v-h52j exists for CVE-2025-33214 (see T1.10). Original: Whether the GitHub AUP scraping rule governs securitylab.github.com and whether GHSL advisories have GHSA twins | `curl -sL https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|research\|archiv'`; for a twin: `curl -s "https://api.github.com/advisories?cve_id=CVE-2025-33214"` | The docs page is client-rendered in part (confirm "Scraping refers to" appears); a missing GHSA twin by CVE does not mean none exists (twins can be keyed by GHSL id in references) |

### Checks that are not absences but should be confirmed by shell

- **S105 reference (T1.5):** the gate verified 17 U.S.C. §105(a) verbatim at law.cornell.edu (gate 1, 2026-10-03), a different host from the earlier gate's check.
- **Apache-2.0 reports "YES" (T1.8):** confirm that the licence of record is
  Apache-2.0 for the `osv/malicious/` tree (no per-directory LICENSE):
  `curl -s https://api.github.com/repos/ossf/malicious-packages/contents/osv | grep name`
  and look for any LICENSE file in subdirectories. Fails if a subdirectory
  carries its own LICENSE that the root API call cannot see.

### Invariant and control notes

- No file other than this one was edited. `docs/SOURCE_LICENSES.md` was read
  (Grep, and a read of s2.4) and not touched.
- Prove-it-fires note for A19: introduce a deliberately wrong expectation (for
  example, grep for `MAL-2099-`), which must return 0, before trusting any
  non-zero or zero count from the real run.
