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

Scores are pre-gate (this is the specialist's first pass; red-reviewer has not
yet checked any row).

| # | Source | Score | Action | Blocking issue |
|---|---|---|---|---|
| T1.3 | CERT/CC Vulnerability Notes | 1 | (c); (d) for the archive | Contradictory CMU terms: notes carry (c) CMU; footer "Legal" link is dead; the SEI terms found (2018) bar copying, derivative works and mirroring; sibling VINCE docs are CC BY-NC 4.0; the archived data repo LICENSE allows only unmodified redistribution. May drop to 0 on a raw-HTML read of the SEI terms |
| T1.4 | CourtListener / RECAP | 2 | (a) with conditions | Public Domain Mark on bulk data (extract); third-party works inside filings; API needs an account, credentials not shareable; robots.txt unread (403) |
| T1.5 | FTC enforcement actions | 2 | (a) with conditions | "Most material" is public domain (FTC's own words), third-party material in filings and comments carved out; robots Crawl-delay 5 and an unclear disallow list |
| T1.6 | 0din (Mozilla GenAI bounty) | 1 | (d) | No licence found for published advisories; submissions licensed to Mozilla; Terms / Services Agreement pages unread; feed is also a commercial product |
| T1.7 | FIRST EPSS (enrichment) | 1 | (d) (light) | No licence text found; "freely and openly accessible", "attribution is requested"; FIRST terms pages 404 |
| T1.8 | OpenSSF malicious-packages | 2 | (a) with conditions | Apache-2.0 (GitHub API, structured). Apache NOTICE/licence carriage; no inbound-licence statement for contributed reports; **overlaps already-ingested OSV (row 2.4) and the 2.4 row's "every reachable database is CC-BY 4.0" sentence looks stale** |
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
| Cleanliness score | **1** (contradictory/unknown terms; facts + link not shown to be banned). **Could fall to 0** if the SEI terms below govern kb.cert.org: they bar mirroring and reformatting, and a raw-HTML read is needed to settle it |
| License | **No open licence located; terms found are mutually inconsistent.** (1) A sample note, `https://www.kb.cert.org/vuls/id/739007` (WebFetch 2026-10-03, extract), ends with *"©2022 Carnegie Mellon University"* and contains no licence or redistribution clause. Its footer "Legal" link is `https://vuls.cert.org/confluence/display/VIN/VINCE+Code+of+Conduct#VINCECodeofConduct-TermsofUse` (extract of the page's link list), which 301-redirects to `certcc.github.io/confluence/display/VIN/VINCE+Code+of+Conduct`, which returns **404**: the note's own legal link is dead. (2) Search extract (WebSearch, no primary page): notes "may be redistributed freely after the release date, provided that redistributed copies are complete and unmodified, and include all date and version information" (the old CERT/CC reproduction wording; **not read from a primary page, provisional**). (3) VINCE docs, `https://certcc.github.io/VINCE-docs/copyright/` (extract): work *"licensed under a Creative Commons Attribution-NonCommercial 4.0 International License"*; permission requests to permission@sei.cmu.edu. This page covers the VINCE documentation, not necessarily the notes. (4) SEI Legal, `https://www.sei.cmu.edu/legal/` (extract, last updated 2018-06-20): users may *"display the content of the Service only for your own personal use (i.e., non-commercial use)"* and may not *"copy, reproduce, alter, modify, create derivative works of, or publicly display any content"*, nor *"take the results from the Service and reformat and display them or mirror any portion"*. Which "Service" this means, and whether it reaches kb.cert.org, is **not established**. (5) `CERTCC/Vulnerability-Data-Archive` (GitHub API `license`: `NOASSERTION`, name "Other"; archived 2024-05-14; data to 2020-06-03): LICENSE.md text, via the API's decoded content, begins *"Copyright (c)2020 Carnegie Mellon University"* and says the material is approved for public release *"except as restricted below"*; a summarising fetch of the same file reports unmodified reproduction and distribution permitted, other uses requiring permission from permission@sei.cmu.edu. The README, same repo, says only ~6% of records are published Vulnerability Notes and the archive "has been supplanted by the VINCE API". (6) `CERTCC/VINCE` (software; API `license`: `NOASSERTION`, "Other"). |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (`https://www.kb.cert.org/robots.txt` returned 404 to WebFetch; **ABSENCE FINDING, method-suspect**). **ToS:** the Vulnerability Note API docs (extract) say *"The Vulnerability Note API does not require authentication, Vulnerability Notes are public"*, with no rate limit stated; that supports API access but is not a licence. The SEI terms in (4) may restrict automated mirroring. Status: **UNKNOWN pending shell check** |
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
| Cleanliness score | **2** (permissive position; conditions to engineer) |
| License | **Bulk data: public domain, per FLP.** Bulk Legal Data wiki, `https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data` (WebFetch 2026-10-03, extract; reached by 301 from `courtlistener.com/help/api/bulk-data/`): the bulk files are *"free of known copyright restrictions"* and marked with the **Public Domain Mark**. Terms of Service, `https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies` (extract; tool said not truncated): *"judicial opinions, motions, and other filings are generally in the public domain"* but *"other court filings may contain third-party copyrighted works"*; also: *"If you republish or display our data, do not present it in a way that suggests Free Law Project produced, endorsed, or verified an AI-generated analysis of it."* The Public Domain Mark is FLP's statement, not a licence; the underlying works are US government works (court opinions) or party filings, the latter not always federal works. Carve-outs: third-party copyrighted works embedded in filings (books, articles, expert reports); personal data in dockets (a privacy matter, not a copyright one). |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (`https://www.courtlistener.com/robots.txt` returned HTTP 403 to WebFetch; **fetch-tool limit, not a finding**). **ToS** (extract): *"Do not use multiple accounts, registered clients, or credential rotation to exceed the rate limits that apply to your access level."*; credentials must not be shared, resold, pooled or transferred; the section of the ToS read states no prohibition on automated access or on commercial use (**ABSENCE FINDING, method-suspect**). Search extract: as of May 2026 the full API is included with a free account membership. Bulk CSV is the intended route for volume (an S3 bucket; quarterly snapshots, not deltas) and avoids rate limits |
| Redistribute-verbatim | **YES for opinions and FLP-authored data** (public domain), **with exceptions** for third-party works inside filings. Not verified per document class |
| Relicense-compatible | **Yes with a notice.** Public-domain text may sit in a CC BY 4.0 dataset, but we cannot assert a licence over it; the dataset notice should say the court text is public-domain and not licensed by us, and credit CourtListener / FLP as the source (a courtesy, not a condition found). Do not imply FLP endorsement of any AI-generated summary |
| Action | **(a) with conditions.** Bulk CSV, not the API, for volume; per-document provenance flag; exclude or downgrade to (c) any document identified as third-party copyrighted; carry the non-endorsement line for generated summaries; privacy review of party names and personal data before ingest (non-licensing; flag for the governance owner). Read robots.txt by shell before any HTTP crawl; none is needed for the bulk route |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising) of the bulk-data wiki and the ToS wiki (both returned, not truncated per tool); `courtlistener.com/terms/` and `/robots.txt` and `free.law/terms-of-service` returned 403 / 403 / 404; WebSearch x1 (search-extract tier: the May 2026 API membership). GitHub API for `freelawproject/courtlistener` (software; `license` `NOASSERTION`; not the data licence). Source kind: rendered HTML via a summarising converter + one GitHub API field |
| Non-English / facts-only | English. Facts + link + original summary is available but not needed for licence reasons |

### T1.5 FTC enforcement actions involving AI (ftc.gov)
*Content class:* press releases, case pages, complaints, orders, business-blog
posts under `ftc.gov/legal-library` and `/news-events`. *Language:* English
(some Spanish pages under `/es/`). AI relevance is a filter problem.

| Field | Value |
|---|---|
| Cleanliness score | **2** (statute plus FTC's own policy; third-party carve-outs) |
| License | **US federal work; the FTC says so itself.** Statute: **17 U.S.C. s105**, *"Copyright protection under this title is not available for any work of the United States Government, but the United States Government is not precluded from receiving and holding copyrights transferred to it by assignment, bequest, or otherwise."* (text as verified verbatim by red-reviewer via curl on 2026-10-03, cited in `source-expansion-evaluation.md` s1E.2; **not re-fetched here**). FTC Website Policy, `https://www.ftc.gov/policy-notices/website-policy` (WebFetch 2026-10-03, extract; a second fetch of `/site-information/website-policy` returned the same clauses): *"Most material on the FTC's website is considered work of the United States Government, meaning that the material is in the public domain and is not subject to copyright restrictions."*; *"The use, duplication, or redistribution of such material should be accompanied by appropriate attribution, where feasible (e.g., 'Source: United States Federal Trade Commission, www.ftc.gov')."*; third-party: *"is unable to grant or deny permission for any materials that may be posted on its website containing work copyrighted in whole or part by third parties"* (found "in or included with public comments and filings, incorporated as photos or other graphics"); *"Fraudulent or deceptive use of any FTC material is strictly prohibited, and, except where expressly authorized, no FTC endorsement or affiliation shall be stated or implied."* Carve-outs: public comments and filings by third parties, photos and graphics, defendants' exhibits attached to FTC complaints, FTC seals (18 U.S.C. 701). Court orders and complaints filed by the FTC are federal-employee work, but attached exhibits may not be |
| Scrape-permitted | **robots.txt** (`https://www.ftc.gov/robots.txt`, WebFetch 2026-10-03, extract): `User-agent: *`, **Crawl-delay: 5**, Drupal-style disallows (`/core/`, `/profiles/`, `/admin/`, `/search/`, `/node/add/`, `/comment/reply/`, `?combine=`, `?items_per_page=`, `/es/node/*`) and, per the extract, "specific document paths related to FDA/FTC statements and events" (**vague; the exact paths are unknown, shell check listed**). **ToS:** the Website Policy extract contains no automated-access clause (**ABSENCE FINDING, method-suspect**). The Privacy Policy extract has no copyright or scraping wording |
| Redistribute-verbatim | **YES for FTC-authored text** (in the US by statute; outside the US not assessed). **NO / unknown for third-party material** inside filings and comments |
| Relicense-compatible | **Yes with a notice,** as for CISA-authored text in s1E.2: a CC BY 4.0 dataset may carry public-domain text, but we do not assert a licence over it; the dataset notice says FTC-authored text is a US government work. Never imply FTC endorsement |
| Action | **(a) with conditions:** honour Crawl-delay 5; per-document provenance flag; exclude third-party filings/comments and exhibits; attribution line "Source: United States Federal Trade Commission, www.ftc.gov"; no endorsement language. The shell check of the disallowed paths decides whether `/legal-library` case pages are reachable |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `ftc.gov/robots.txt`, `/policy-notices/website-policy`, `/site-information/website-policy`, `/policy-notices`, `/policy-notices/privacy-policy`, `/` (footer links); `/about-ftc/website-policies` 404. s105 text taken from the gate record, not re-fetched. Source kind: rendered HTML via a summarising converter (the positive FTC clauses are quoted by the tool; absences and the disallow list are method-exposed) |
| Non-English / facts-only | English (Spanish mirrors exist; skip). Facts + link + original summary is uncontested but not needed for FTC-authored text |

### T1.6 0din (0din.ai, Mozilla GenAI bug bounty)
*Content class:* GenAI model and application vulnerability disclosures published
after mitigation, plus a "0DIN Intel" threat feed. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (no public licence found; submissions are licensed to Mozilla; facts + link not shown to be banned) |
| License | **No licence for published advisories found.** Bug Bounty Program Terms and Conditions, `https://0din.ai/policy` (WebFetch 2026-10-03, extract): *"All submissions will be covered under Mozilla's Website & Communications Terms of Use, granting us permission to make use of all submissions."*; publication: *"we will post and advertise the vulnerability publicly...we will provide (optional) credit to the discovering Researcher"*; and *"For model vulnerabilities, we will publish details of the vulnerability once we determine, in our sole discretion, that the vulnerability has been mitigated"*. The extract says the policy does **not** specify copyright ownership or public reuse. Mozilla Websites & Communications Terms of Use, `https://www.mozilla.org/en-US/about/legal/terms/mozilla/` (extract): submitters grant *"a nonexclusive, royalty-free, worldwide, sublicensable (to those we work with) license to use your Submission in connection with the Communications"*; Mozilla "generally releases its own content under Creative Commons or Mozilla Public License" but some content comes from sources that "prohibit further use ... without advance permission". That gives Mozilla a licence, not the public one, and is generic, not specific to 0din.ai. The 0din.ai footer (homepage extract) lists "Privacy", "Policy", "Services Agreement" and "Legal Archive"; **`/terms`, `/services-agreement` and `/legal` returned 404 and the Services Agreement was not read**. The GitHub repo `0din-ai/0din.ai` has `license: null` (API) and holds no advisory data. The homepage markets a paid "AI Vulnerability Intelligence" feed (Probe Packs); the "0DIN Intel" docs path `/docs/threat-feed/introduction` was not read, so whether published advisories are free to reuse is **unknown**, and a commercial feed raises the chance that bulk copying is contested |
| Scrape-permitted | **robots.txt** (`https://0din.ai/robots.txt`, WebFetch 2026-10-03, extract, complete): `User-agent: *`; `Disallow: /admin`, `/api/`, `/api-docs`, `/jobs`, `/letter_opener`, `/up`, `/rails/`, `/users`; `Allow: /`; sitemap at `/sitemaps/sitemap.xml.gz`. Public advisory pages are not disallowed (path not identified); the **API is disallowed**. **ToS:** no automated-access clause in the policy extract (**ABSENCE FINDING, method-suspect**); Services Agreement unread |
| Redistribute-verbatim | **NO / UNKNOWN.** No public grant found; Mozilla holds a licence to submissions; researcher copyright position not stated |
| Relicense-compatible | **NO / UNKNOWN** |
| Action | **(c) facts + link + original summary** (advisory URL, affected model, date, researcher credit if published, our own summary) and **(d)**: the Services Agreement and the 0DIN Intel terms must be read by shell before any scrape; the user may ask 0din@mozilla.com (address from the homepage footer) whether published advisories are reusable. Do not use `/api/` (disallowed) |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `0din.ai/policy` (read, extract), `/` (footer links), `/robots.txt` (read in full), `/terms`, `/services-agreement`, `/legal` (404), `mozilla.org/.../terms/mozilla/` (extract); GitHub API for `0din-ai/0din.ai` (structured); WebSearch x1 (titles and summaries; surfaced `0din.ai/privacy`, `0din.ai/privacy/2025-02-24` and an `0din-ai-mozilla.fastly-edge.com` mirror, none read). Source kind: rendered HTML via a summarising converter |
| Non-English / facts-only | English. Facts + link + original summary is not shown to be contested |

### T1.7 FIRST EPSS (enrichment only)
*Content class:* a daily 0-1 exploitation-probability score and percentile for
every CVE (CSV, API at `api.first.org`, GitHub). **Enrichment only:** numbers
joined to existing CVE-keyed entries, not new incidents. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (no licence text located; the access statements are permissive but informal; grant read only from a summarising extract, so provisional) |
| License | **No formal licence found.** EPSS home, `https://www.first.org/epss/` (WebFetch 2026-10-03, extract): *"EPSS publishes a 0-1 probability (with ranking percentiles) every day for every CVE and makes the data freely and openly accessible via CSV and API as well as a github repo"*; scores are "generated by Empirical Security and published freely to the community". EPSS FAQ, `https://www.first.org/epss/faq` (extract): *"EPSS scores are published freely via CSV download and API with no registration required."* and *"Attribution is requested when EPSS data is used in publications or products."* The training data cannot be shared because *"several data partners share exploitation telemetry under agreements that prohibit redistribution"*; that concerns the model's training data, not the published scores, but it shows partner-data terms sit behind the product. `https://www.first.org/epss/api` and `https://www.first.org/terms` returned **404**; `https://www.first.org/epss/data_stats` was not fetched. A "free and open" statement without a licence is not a grant we can cite, and "attribution is requested" is a request, not a licence term |
| Scrape-permitted | **robots.txt** (`https://www.first.org/robots.txt`, extract): `User-agent: *`, `Disallow: /signin*`, `Disallow: /_/links/*`; the EPSS pages are not disallowed. **`api.first.org` robots.txt was not fetched.** The API is the published access route and needs no registration (FAQ extract). **ToS:** none located (**ABSENCE FINDING, method-suspect**) |
| Redistribute-verbatim | **UNKNOWN.** Publication is free and open; no redistribution or derivative clause was found either way. Scores are numbers; whether a daily time series of them is copyrightable expression is not assessed (**not resolved in the project's favour**) |
| Relicense-compatible | **UNKNOWN.** No restriction found, and no grant to relicense found |
| Action | **(d) light:** ask FIRST (`first.org` contact page not read) whether EPSS scores may be redistributed inside a CC BY 4.0 dataset with attribution. Interim shape if the user wants none: store the CVE id and a **link to the EPSS API URL** for that CVE, not the score values, until answered. If the user rules to proceed on the "freely and openly accessible" statement, record the score with its as-of date and the attribution line "EPSS, FIRST.org" |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `first.org/epss/` and `/epss/faq` (read, extracts), `/epss/api`, `/terms`, `/epss/data_stats` (404), `/robots.txt` (read). No shell, no GitHub API call for an EPSS repo. Source kind: rendered HTML via a summarising converter (**weak for absences; the central finding here is an absence**) |
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
| License | **Apache-2.0 (structured).** GitHub API `https://api.github.com/repos/ossf/malicious-packages`, `license` field: `spdx_id` **`Apache-2.0`**, name "Apache License 2.0" (WebFetch of the JSON, 2026-10-03). `LICENSE` in the repo root: *"Apache License / Version 2.0, January 2004"* (raw file, extract). OSV data page, `https://google.github.io/osv.dev/data/` (extract): *"OpenSSF Malicious Packages: Apache 2.0"*. The repo root has no NOTICE file (API contents listing: `LICENSE`, `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CONTRIBUTION-GUIDELINES.md`, `osv/`, `docs/`, `site/`, Go sources). README (extract) states no licence for the reports themselves and names prior sources (GitHub Advisory Database filtered for malware; PyPI malware registries; Datadog's malicious-software-packages dataset). CONTRIBUTING (extract) states no DCO or CLA and no inbound licence (**ABSENCE FINDING, method-suspect**): the Apache-2.0 position for third-party-contributed reports therefore rests on the repo-wide licence plus GitHub's inbound=outbound default for contributions, which is a general GitHub ToS rule and was not re-read for this row. Apache-2.0 is a software licence applied to data; it is permissive and its notice conditions are met by carrying the licence and attribution |
| Scrape-permitted | **robots.txt:** not applicable to `raw.githubusercontent.com` file access; GitHub's own terms govern (see T1.10: GitHub AUP defines "scraping" as automated extraction from the Service and excludes the API; the repo can be **cloned**, which is not scraping). The OSV API (`api.osv.dev`) is the documented route (`SOURCE_LICENSES.md` s2.4: "official public API designed for this query pattern"). **ToS:** no repo-level access restriction located (**ABSENCE FINDING, method-suspect**) |
| Redistribute-verbatim | **YES** under Apache-2.0: give recipients a copy of the licence, retain attribution notices, mark changes. Third-party credits and references inside reports stay with their authors |
| Relicense-compatible | **YES with conditions, but NOT relicensable.** Apache-2.0 does not permit re-licensing the reports as CC BY 4.0; the dataset must ship the reports as **Apache-2.0 components** within a CC BY 4.0 collection and say so in NOTICE-DATA (the model `SOURCE_LICENSES.md` s2.4 uses: the originating database's licence applies per record). Whether Apache-2.0 patent and attribution terms are acceptable to the project is a user ruling |
| Action | **(a) with conditions:** per-record `source` naming the OpenSSF Malicious Packages database and carrying "Apache-2.0"; add the Apache-2.0 text to the dataset's licence bundle; filter by an AI/ML-ecosystem rule defined in the pipeline brief. **Overlap flag (must route):** OSV.dev is already ingested (`SOURCE_LICENSES.md` s2.4) via `api.osv.dev/v1/query` over PyPI/npm/Go targets, and `MAL-` records are served by that API. Row 2.4 says *"every source database actually reachable by this script is CC-BY 4.0"*, but OSV's own data page lists OpenSSF Malicious Packages as Apache-2.0 and PyPI/npm queries can return `MAL-` records; Grep shows `MAL-2026-3607` as an alias in an existing record. Row 2.4's sentence is therefore **likely stale for the MAL- subset** and needs a shell check of what the existing ingest actually stored (red-reviewer item below). This is a truthfulness defect candidate in a live surface (corrected in place, per working agreement 4), not a reason to defer the row |
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
  trl, diffusers, datasets, text-generation-inference, and others). Only the
  first 100 repos by recency were examined (**method-limited absence**).
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
| License | HF Terms of Service, `https://huggingface.co/terms-of-service` (WebFetch 2026-10-03, extract): *"You own the Content you create!"*; for public repositories users *"grant each User a perpetual, irrevocable, worldwide, royalty-free, non-exclusive license to use, display, publish, reproduce, distribute, and make derivative works of your Content"* (extract; **a licence to Users from the uploader, whose scope relative to the uploader's stated licence and to a downstream dataset licence was not analysed**); *"Open Source license terms are not intended to be replaced or overridden"*. No site-wide data licence for scan results or security metadata found |
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
| License | **No content licence found on the advisory pages.** A sample advisory, `https://securitylab.github.com/advisories/GHSL-2025-115_NVTabular/` (WebFetch 2026-10-03, extract; tool said not truncated), shows the footer *"GitHub Inc. (c) 2024"* with links to GitHub's Terms and Privacy, and no licence or reuse text. The advisories index (extract) states: *"We publish vulnerabilities here only after patches are available."* GitHub API for `github/securitylab`: `license` **`MIT`** (structured) with description "Resources related to GitHub Security Lab"; that repo holds exploits and resources, not the advisory pages, and its MIT licence does not extend to the site. GitHub Terms of Service, `https://docs.github.com/en/site-policy/github-terms/github-terms-of-service` (extract): content ownership and licences are about *user* content (D.3 "You own Your Content"); API terms (Section H) prohibit abuse and excessive requests. GitHub Acceptable Use Policies (extract): *"Scraping refers to extracting information from our Service via an automated process, such as a bot or webcrawler. Scraping does not refer to the collection of information through our API."*; permitted exceptions: *"Researchers may use public, non-personal information from the Service for research purposes, only if any publications resulting from that research are open access."* and *"Archivists may use public information from the Service for archival purposes."* That is an exception for researchers, not a licence to redistribute. **Licence-clean route:** each GHSL advisory with a CVE normally has a GHSA record in the GitHub Advisory Database, which is **CC BY 4.0** (GitHub site-policy "additional products and features", extract: *"The GitHub Advisory Database is licensed under the Creative Commons Attribution 4.0 license"*) and is already ingested; the CVE record and NVD entry are covered by the CVE ToU. A GHSL write-up adds narrative detail (timeline, PoC) that GHSA may not carry; that narrative is the uncovered part. Whether a given GHSL advisory has a matching GHSA record was not enumerated |
| Scrape-permitted | **robots.txt:** not obtained (the fetch of `https://securitylab.github.com/robots.txt` returned only a pointer to `sitemap.xml`; **ABSENCE FINDING, method-suspect**). **ToS:** the AUP scraping definition above applies to automated extraction from the Service; the site is a GitHub property, so whether the AUP governs `securitylab.github.com` is not stated in anything read. The sitemap route and a rate limit are the conservative defaults, but the researcher exception requires open-access publication, which a CC BY 4.0 dataset arguably is; **this is a legal reading, not resolved in the project's favour** |
| Redistribute-verbatim | **NO / UNKNOWN** for the advisory text (no grant found). **YES under CC BY 4.0** for the GHSA record (already ingested) |
| Relicense-compatible | **NO / UNKNOWN** for the GHSL page text; **YES** for GHSA (CC BY 4.0 to CC BY 4.0, attribution to the GitHub Advisory Database) |
| Action | **(c) facts + link + original summary** for GHSL pages (GHSL id, project, CVE, CWE, dates, link, our own summary), taking verbatim description text only via the GHSA/CVE routes. **(d)** optional: ask GitHub (`securitylab@github.com`, address not verified here) whether GHSL advisory text may be reused. Do not crawl `securitylab.github.com` before the shell checks below. Note possible near-duplication with GHSA at the entry level (dedupe key: CVE id) |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `securitylab.github.com/advisories/` and one advisory page, `/robots.txt` (pointer only), `docs.github.com` ToS, AUP, additional-products pages; GitHub API JSON `repos/github/securitylab` (structured: `license`); search for `github/securitylab-website` via the API returned 0 results. Source kind: rendered HTML via a summarising converter + one GitHub API field |
| Non-English / facts-only | English. Facts + link + original summary is not shown to be contested |

---

## Brief vs. found

The task said to refute reconstructed names that are poor choices.

1. **T1.9 (Hugging Face security advisories / malicious-model disclosures) is a
   poor choice and should be dropped.** No advisory feed or database exists
   (docs page lists features only; no advisory repo in the first 100 HF repos);
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
   ~6% of its records are published notes) with a custom non-open licence.
5. **T1.4 / T1.5 premise "court records are public domain" and "US federal
   works": confirmed**, with third-party carve-outs in both. The reconstruction
   record's framing "site and API terms apply" is correct for CourtListener (rate
   limits, credentials, AI-analysis non-endorsement) and thin for FTC.
6. **T1.7 EPSS "usage terms":** no formal terms were found; this is the weakest
   row, resting on an absence from two summarised pages.
7. **T1.1 / T1.2 are not re-evaluated** (gated rows exist).

None of the eight is a non-existent site, but T1.9 names a source that does not
exist as described.

## Estimates (pipeline-engineer)

*Placeholder. Filled by pipeline-engineer in the next step.*

## Ranking

*Placeholder. Filled in the next step.*

## Absence findings for shell verification

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
| A4 | T1.3 | Whether SEI terms reach kb.cert.org (the "Service" definition) | `curl -sL https://www.sei.cmu.edu/legal/ \| sed 's/<[^>]*>//g' \| grep -inE 'service\|mirror\|derivative\|non-commercial\|automated\|crawl'`; then repeat on `https://www.sei.cmu.edu/legal/terms-of-use/` (guess) | The terms page differs by path (`/legal/` vs `/legal/terms-of-use/`); the 2018 date may mean a newer page exists; the grep finds "service" 100 times and proves nothing, so read the definition sentence |
| A5 | T1.3 | Archive LICENSE.md wording (extract disagrees with API text) | `curl -sL https://raw.githubusercontent.com/CERTCC/Vulnerability-Data-Archive/main/LICENSE.md` (read the full file, not a grep) | None: this is a plain text file; the check fails only if the file moved branches (use `/HEAD/`) |
| A6 | T1.3 | The "complete and unmodified" wording exists on a primary page | `curl -sL https://www.kb.cert.org/vuls/ \| sed 's/<[^>]*>//g' \| grep -iE 'complete and unmodified\|redistribut'` and the same on `https://certcc.github.io/VINCE-docs/copyright/` | The wording is from the old `cert.org/legal_stuff` page; if absent from kb.cert.org it is the old site's and the search extract was stale (the row would need correcting). A "0 hits" is only meaningful if the page returned 200 and was not a challenge page |
| A7 | T1.4 | CourtListener robots.txt (403) | `curl -sIL -A "Mozilla/5.0" https://www.courtlistener.com/robots.txt` and `curl -sL -A "Mozilla/5.0" https://www.courtlistener.com/robots.txt` | A Cloudflare/DataDome-type challenge returns 403/200 HTML; status 200 with `<html` in the body is not a robots file. If challenged, ask from a different network/browser session |
| A8 | T1.4 | ToS has no clause barring scraping, bulk or commercial use | `curl -sL -A "Mozilla/5.0" https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|crawl\|bulk\|automat\|commercial\|train\|AI'` | The wiki is a JS app (shell page with 0 body text): check that the output contains the phrase "Do not use multiple accounts" before trusting a 0-hit result on the other terms. Also check `https://www.courtlistener.com/terms/` |
| A9 | T1.4 | Bulk-data Public Domain Mark claim | `curl -sL https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data \| sed 's/<[^>]*>//g' \| grep -inE 'public domain\|copyright\|licen'` | JS-rendered wiki as in A8; confirm the page body contains "Bulk Legal Data" |
| A10 | T1.5 | FTC Website Policy has no automated-access clause | `curl -sL https://www.ftc.gov/policy-notices/website-policy \| sed 's/<[^>]*>//g' \| grep -inE 'automat\|scrap\|crawl\|robot\|bulk\|spider'` | A hit on "robot" in boilerplate is not a restriction: read the sentence; 0 hits on a page that returned a bot challenge is meaningless (check status and that the output contains "public domain") |
| A11 | T1.5 | The exact disallowed paths (extract said "specific document paths related to FDA/FTC statements and events") | `curl -sL https://www.ftc.gov/robots.txt \| grep -inE 'disallow\|crawl-delay\|legal-library\|news-events\|cases\|enforcement'` | The disallow list may name paths in `/legal-library/` or `/news-events/` that overlap enforcement pages; compare against the URL patterns the pipeline would fetch |
| A12 | T1.6 | 0din Services Agreement / Terms (all 404) and any statement on advisory reuse | `curl -sIL https://0din.ai/services-agreement`; follow the footer link in raw HTML: `curl -sL https://0din.ai/ \| grep -oiE 'href="[^"]*(agreement\|terms\|legal\|privacy\|policy\|archive)[^"]*"'` then read each target | The footer is rendered by JS or uses relative links I guessed wrong (the 404s were guesses, not discovered URLs); a hit is only meaningful if the discovered URL returns 200 |
| A13 | T1.6 | `/policy` is silent on copyright/public reuse | `curl -sL https://0din.ai/policy \| sed 's/<[^>]*>//g' \| grep -inE 'copyright\|licen[cs]e\|reuse\|redistribut\|own\|intellectual\|scrap\|automat'` | The summariser may have dropped a long page tail; the grep must be run over the whole document; clause split across tags (strip tags first) |
| A14 | T1.6 | 0DIN Intel / threat-feed terms (unread) and whether advisories are public pages | `curl -sL https://0din.ai/docs/threat-feed/introduction \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|terms\|redistribut\|attribution\|commercial'`; and `curl -sL https://0din.ai/sitemaps/sitemap.xml.gz \| gunzip \| grep -c '<loc>'` to find advisory URL patterns | Docs may be a SPA (check body length); the sitemap may list only some pages; a gunzip failure means a bot challenge, not an empty sitemap |
| A15 | T1.7 | No formal EPSS licence/terms | `curl -sL https://www.first.org/epss/ \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|terms\|attribut\|cite\|commercial\|redistribut\|copyright'`; same on `/epss/faq`, `/epss/user-guide`, `/epss/articles`, `https://www.first.org/legal/`, and `https://www.first.org/about/policies/` (guesses; only discovered URLs count) | The EPSS "Usage" statement may sit in a different page than the ones fetched; a grep over a page missing its footer proves nothing, so also run `grep -oiE 'href="[^"]*(terms\|legal\|privacy\|licen)[^"]*"'` on the home page footer and follow what it finds |
| A16 | T1.7 | api.first.org robots.txt not obtained; API terms | `curl -sIL https://api.first.org/robots.txt`; `curl -sL "https://api.first.org/data/v1/epss?cve=CVE-2021-44228" \| head -c 600` (inspect for any `license` or `terms` JSON key and response headers: `curl -sIL ...`) | A 404 robots.txt on an API host means "no restrictions declared", not "permission"; the JSON may carry no licence key |
| A17 | T1.8 | CONTRIBUTING / README state no inbound licence or DCO/CLA | `curl -sL https://raw.githubusercontent.com/ossf/malicious-packages/main/CONTRIBUTING.md \| grep -inE 'licen[cs]e\|DCO\|sign-off\|CLA\|apache\|copyright'`; same on `README.md`, `CONTRIBUTION-GUIDELINES.md` | Branch name differs (`main` vs `HEAD`); a hit on "licence" in a link title is not a clause: read it. This check is the plain-text kind and is reliable |
| A18 | T1.8 | Repo root has no NOTICE; confirm API `license` | `curl -s https://api.github.com/repos/ossf/malicious-packages \| grep -A4 '"license"'`; `curl -s https://api.github.com/repos/ossf/malicious-packages/contents \| grep '"name"'` | Unauthenticated API rate limiting returns a JSON error (`API rate limit exceeded`) with 403 and zero `license` hits; check status; the API reports the repo's top-level licence only, not per-file |
| A19 | T1.8 | OSV-ingest overlap: which `MAL-` records the existing ingest stored and what row 2.4 says | `grep -c '"MAL-' data/incidents.json`; `grep -n 'MAL-' data/incidents.json \| head`; `grep -n 'Apache\|CC-BY\|OpenSSF' docs/SOURCE_LICENSES.md` | MAL- ids might appear only as aliases of GHSA ids (as `MAL-2026-3607` does) with the record's text sourced from GHSA (CC BY 4.0), in which case row 2.4's sentence is right in effect; the check must inspect each record's `source`/provenance field, not just the id |
| A20 | T1.9 | No HF advisory feed or security-advisory repo | `curl -s "https://huggingface.co/api/models?filter=security" \| head -c 300` is not meaningful; use instead: `curl -sL https://huggingface.co/docs/hub/security \| grep -oiE 'href="[^"]*(advis\|disclos\|cve\|vulnerab)[^"]*"'`; `curl -s "https://api.github.com/orgs/huggingface/repos?per_page=100&page=2" \| grep '"name"'` (pages 2..n); `curl -s https://api.github.com/repos/huggingface/huggingface_hub/security-advisories` | The org has more than 100 repos (only page 1 was read); HF may host advisories under `huggingface.co/docs/hub/security-*` pages not linked from the index; the GitHub advisories endpoint may need auth (404/403 is not "none") |
| A21 | T1.9 | HF ToS has no scraping/crawling clause | `curl -sL https://huggingface.co/terms-of-service \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|crawl\|robot\|automat\|bot\b\|rate limit'` | The ToS is long and the summariser may have truncated; the page is an SPA with server-side text? (check the output contains "You own the Content you create"); content may also be in a separate `content-policy` page |
| A22 | T1.10 | No licence/copyright on GHSL pages beyond "GitHub Inc. 2024" | `curl -sL https://securitylab.github.com/advisories/GHSL-2025-115_NVTabular/ \| sed 's/<[^>]*>//g' \| grep -inE 'licen[cs]e\|copyright\|creative commons\|reuse\|(c)\|©'`; also `curl -sL https://securitylab.github.com/ \| grep -oiE 'href="[^"]*(terms\|licen\|legal\|policy)[^"]*"'` | A licence may live in the `securitylab-website`/`github/securitylab` repo's README or a `LICENSE` that the site footer links to: check `curl -s https://api.github.com/repos/github/securitylab/contents \| grep name` and follow the footer links |
| A23 | T1.10 | securitylab.github.com robots.txt (only a sitemap pointer returned) | `curl -sIL https://securitylab.github.com/robots.txt`; `curl -sL https://securitylab.github.com/robots.txt` | The extract may have dropped the `User-agent`/`Disallow` lines; 200 with HTML is not a robots file |
| A24 | T1.10 | Whether the GitHub AUP scraping rule governs securitylab.github.com and whether GHSL advisories have GHSA twins | `curl -sL https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies \| sed 's/<[^>]*>//g' \| grep -inE 'scrap\|research\|archiv'`; for a twin: `curl -s "https://api.github.com/advisories?cve_id=CVE-2025-33214"` | The docs page is client-rendered in part (confirm "Scraping refers to" appears); a missing GHSA twin by CVE does not mean none exists (twins can be keyed by GHSL id in references) |

### Checks that are not absences but should be confirmed by shell

- **S105 reference (T1.5):** relies on the gate's earlier verbatim check; no
  re-fetch was done in this file.
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
