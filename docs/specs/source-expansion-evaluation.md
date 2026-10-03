# Source-expansion evaluation — tranche 2 (worldwide)

**Working file, started 2026-10-02.** Scope record:
`docs/specs/source-expansion-tranche2-scope-2026-10-02.md` (dated, do not
regenerate). Rows below are **pre-rows** in the `docs/SOURCE_LICENSES.md`
column format (invariant 10: a source's real row lands in `SOURCE_LICENSES.md`
only inside that source's ingest PR; this file does not edit it). No ingest code
exists or is authorised before a user ruling.

**Author of section 1-3:** license-auditor. **No shell is available to this
agent.** Every page below was read through WebFetch (markdown-converting, may
truncate) or WebSearch. Per the standing absence rule, any "no licence / no
ToS / no robots.txt content found" statement is **method-suspect** and is
listed in the report under ABSENCE FINDINGS FOR SHELL VERIFICATION for a
red-reviewer curl+grep on the raw HTML. Where a row rests on a structured
endpoint (GitHub API JSON, a licence file in a repo) the row says so.

**Rework 2026-10-03 (after red-reviewer gate 1, BOUNCE #1).** The gate verdict
is `docs/audits/source-expansion-tranche2-gate1-verdict-2026-10-03.md` (dated
record, do not regenerate). Rows below were corrected **by transcription from
that verdict**, not by re-fetching: where a row says "verified by red-reviewer
via curl, 2026-10-03" the quoted clause is the gate's, taken from raw HTML by
shell, and was not re-measured by this agent (whose WebFetch tool is the one
that produced the false negatives). The original wrong statements are not
preserved inline; the verdict is the record of what was refuted. Section 1E
(two tranche-1 sources) was added in the same rework and is this agent's own
WebFetch/WebSearch work, method-suspect for absences.

**Facts re-checked vs. taken from the brief:** nothing from the brief is
carried forward unverified; each row's "Retrieval method" says what was
actually fetched. Where a licence prior ("NCSC = OGL", "ACSC = CC BY 4.0")
differs from what was found, the row says so under "Brief vs. found".

## Licensing-cleanliness scale (0-3), defined once

| Score | Meaning |
|---|---|
| **3** | Verbatim ingest into a CC BY 4.0 dataset is allowed: explicit permissive grant (CC0 / CC BY / OGL / public-domain work) covering the content we would take, automated access not prohibited, nothing left open. Action (a). |
| **2** | Verbatim ingest allowed **with a condition we must engineer for** (per-item third-party carve-outs, attribution/notice formalities, rate limits, a filter to separate covered from uncovered material, or a grant read only second-hand). Action (a) with conditions. |
| **1** | Verbatim ingest **not** allowed or **unknown** (non-commercial, no-derivatives, all-rights-reserved, contradictory or missing terms), but the **facts + link + original summary** shape is not itself contested: no explicit ban on automated access or on extracting facts; **or a grant known only from a search extract whose primary page could not be reached (provisional)**. Action (c) or (d). |
| **0** | **Even facts + link is contested**: an explicit prohibition on bulk/automated access or on open-licence redistribution of the data, a robots.txt that disallows the content, or a litigation history against scrapers. Do not ingest at all before a written permission. Action (d), interim "link only". |

The score is about the licence position only. It says nothing about volume, corpus
fit or maintenance cost; those go to the ranking, not here.

Action letters (as in `SOURCE_LICENSES.md`): (a) compatible · (b) share-alike
· (c) prohibited -> facts + link + original summary only · (d) unknown ->
outreach (user sends; none drafted here).

Project data licence for the "relicense-compatible" column: **CC BY 4.0**.

## Summary of pre-rows (29 candidates; 27 tranche 2 + 2 tranche 1)

Scores below are the **post-gate (2026-10-03)** scores. Verification status per
row is in the table after this one.

| # | Candidate | Score | Action | Blocking issue / condition |
|---|---|---|---|---|
| 1A.1 | UK NCSC | 3 | (a) | OGL v3.0 confirmed; per-record OGL notice; exclude third-party images/logos |
| 1A.2 | ACSC Australia | 2 -> **1** (provisional) | (d) | **Unverified, extract-sourced; scored 1 under the score-1 clause "a grant known only from a search extract whose primary page could not be reached (provisional)" (D39).** Site-wide CC BY 4.0 never read from the primary page (gate: TLS then 0 bytes, 4 ways); only a per-document corroboration (ISM README). Would return to 2 if the copyright page is read |
| 1A.3 | CCCS Canada | 1 | (c) | Non-commercial reproduction only (CSE terms; canada.ca terms same wording); **not** permissive, contrary to the brief's "trio" |
| 1A.4 | ENISA | 2 (reports) / **1** (web text) | (a) PDF reports; (c) web text; (d) DB | CC BY 4.0 for reports (policy read); web text: legal notice authorises **reproduction** with source, no adaptation grant; CC BY-NC-ND training material excluded |
| 1A.5 | BSI / CERT-Bund | 1 | (c) | Non-commercial, unmodified use only (BSI-wide); WID-specific terms **unverified** (JS app); sample CSAF has TLP:WHITE + liability-only disclaimer, no licence |
| 1A.6 | ANSSI / CERT-FR | 3 | (a) | Licence Ouverte 2.0 confirmed; do not fetch `/pdf`, `/fiche/`; attribution |
| 1A.7 | JPCERT/CC | 1 | (d) notification | `guide.html` s2: quotation free with source/title/URL; redistribution needs notification to `office@jpcert.or.jp`; not an open licence |
| 1A.8 | JVN / JVN iPedia | 1 | (d) | FAQ Q5-2 informal "no particular restrictions, please notify by email" vs "All rights reserved" footers; not a licence; jvn.jp side not covered by the FAQ |
| 1A.9 | SingCERT / CSA | **0** (was 1) | (d); no link-only | All rights reserved **and** caching/links/framing prohibited without permission; even facts + link contested |
| 1A.10 | CERT-EU | 1 | (d) | Legal notice (CERT-EU's own) says CC BY 4.0, same page footer says "All rights reserved"; no AI advisories seen |
| 1B.2 | EUVD | 1 | (d) | ENISA legal notice authorises reproduction of website material (does it reach the API data? unknown); euvd-docs-public LICENSE bars reuse of the docs; no data licence |
| 1B.3 | cvelistV5 | 2 | (a) cond. | CVE ToU requires MITRE notice; **no such notice in NOTICE-DATA / dep5 / SOURCE_LICENSES today** (targeted grep) |
| 1B.4 | VulnCheck KEV | 0 | (d) | Service Terms bar making data available under an open licence and AI training on free data; conflicts with its attribution page |
| 1B.5 | AVID | 2 | (a) cond. | MIT repo licence (structured); **already in corpus (109 entries) with no SOURCE_LICENSES row** |
| 1C.1 | Italy Garante | 1 | (d)/(c) | No general licence located; PDFs disallowed by robots; Italian |
| 1C.2 | EDPB registers | 2 / 1 | (c) + (d) | Custom reuse grant ("do not distort meaning"); national decisions' rights unclear |
| 1C.3 | Dutch AP | 1 | (c) | Copyright reserved, personal use + quotation; passing on to third parties or commercial processing requires contacting AP (gate read primary); robots GPTBot Disallow |
| 1C.4 | CNIL | 1 | (c); (a) open-data subset | Site text CC-BY-ND 4.0 FR; data.gouv.fr dataset "Sanctions prononcees par la CNIL" is under fr-lo (Licence Ouverte), supports the open-data subset |
| 1C.5 | UK ICO | 3 | (a) | OGL v3.0 "except where otherwise stated" (copyright-and-re-use page); required attribution string; honour Crawl-delay 6 |
| 1C.6 | Brazil ANPD | 1 | (c) | CC BY-ND 3.0 on all content; Portuguese |
| 1C.7 | Canada OPC | 1 | (c) | Non-commercial reproduction only |
| 1C.8 | BAILII | 0 | (c) link only | Terms bar bulk download/storage; robots disallows judgment trees; BAILII cannot authorise copying |
| 1C.9 | CanLII | 0 | (c) link only | robots `Disallow: /` (gate-confirmed); terms clause **unverified, extract-sourced** (403 DataDome); CanLII litigating over scraping |
| 1D.1 | arXiv cs.CR | 3 meta / 0 full text | (a) metadata incl. abstract | **Brief refuted:** abstract is CC0 metadata; never mirror e-prints; 1 req / 3 s |
| 1D.2 | HackerOne Hacktivity | 1 | (c) | Researcher keeps copyright; licences run only to HackerOne and Customer (current Community Member T&C, eff. 2026-05-11; Finder Terms 2023 superseded); no scrape clause found in 6 docs |
| 1D.3 | Bugcrowd | 0 | (c) link only | "Copying, redistribution, use or publication of any portion of our Website is strictly prohibited"; submissions confidential/assigned |
| 1D.4 | DEF CON AI Village / Black Hat | 1 | (c) | **Unverified, extract-sourced.** Speakers keep copyright; no downstream licence; fetches failed (reset / 403) |
| 1E.1 | huntr (Protect AI / Palo Alto Networks) | 1 | (c) | Contributions assigned exclusively to Palo Alto Networks (Participation Terms s7.1); no public reuse grant seen; **gate-2 fixed** |
| 1E.2 | CISA beyond KEV | 2 (CISA-authored) / 1 (co-sealed, third-party) | (a) with per-document filter | Federal works not copyrighted (17 U.S.C. s105, statute text verified by red-reviewer via curl, 2026-10-03), but co-sealed foreign-agency material is not; no CISA-wide licence statement located; **gate-2 fixed** |

### Verification status per row

**Key.** *gate-confirmed*: the gate re-measured the finding by shell on raw
HTML and it stood. *gate-refuted-and-fixed*: the gate refuted an earlier
statement and the row was rewritten from the gate's quotes. *unverifiable*:
the gate could not reach the primary page; the row rests on search extracts or
secondary sources and is labelled "unverified, extract-sourced" in the row.
*not yet gated*: added after the gate (section 1E).

| Row | Status |
|---|---|
| 1A.1 NCSC | gate-confirmed (OGL interop sentence corrected to verbatim) |
| 1A.2 ACSC | **unverifiable**; score lowered to 1 provisional |
| 1A.3 CCCS | gate-confirmed (citation corrected) |
| 1A.4 ENISA | gate-refuted-and-fixed |
| 1A.5 BSI/WID | no-open-licence half gate-confirmed; WID-specific terms **unverifiable** |
| 1A.6 ANSSI | gate-confirmed |
| 1A.7 JPCERT | gate-refuted-and-fixed |
| 1A.8 JVN | gate-refuted-and-fixed |
| 1A.9 CSA | gate-refuted-and-fixed (score 1 -> 0) |
| 1A.10 CERT-EU | contradiction gate-confirmed; "CERT-EU not named" gate-refuted-and-fixed |
| 1B.2 EUVD | gate-refuted-and-fixed |
| 1B.3 cvelistV5 | gate-confirmed on substance; check 13 false-fired, fixed |
| 1B.4 VulnCheck | gate-confirmed (both clauses verbatim) |
| 1B.5 AVID | gate-confirmed (site IDs corrected to R1714) |
| 1C.1 Garante | gate-confirmed |
| 1C.2 EDPB | gate-confirmed |
| 1C.3 Dutch AP | gate-confirmed, upgraded to primary |
| 1C.4 CNIL | gate-confirmed (dataset licence added from data.gouv.fr API) |
| 1C.5 ICO | gate-refuted-and-fixed (score stands) |
| 1C.6 ANPD | gate-confirmed |
| 1C.7 OPC | gate-confirmed |
| 1C.8 BAILII | gate-confirmed |
| 1C.9 CanLII | robots gate-confirmed; terms clause **unverifiable** |
| 1D.1 arXiv | gate-confirmed |
| 1D.2 HackerOne | gate-confirmed; terms superseded, fixed |
| 1D.3 Bugcrowd | gate-confirmed |
| 1D.4 DEF CON / Black Hat / AI Village | **unverifiable** |
| 1E.1 huntr | gate-2 fixed |
| 1E.2 CISA beyond KEV | gate-2 fixed |
| Rejections 2.1 CNNVD/CNVD, 2.3 VulDB | **unverifiable** (JS wall / SPA shell / 403) |
| Rejection 2.2 Snyk | gate-confirmed (2020 clause; current ToS makes Service Data Confidential Information) |
| W1 Art. 73 | gate-confirmed; Digital Omnibus OJ dates **unverified** |
| W2 EUVD API | gate-refuted-and-fixed (dated update added) |

Deliberate rejections: section 2. Dated watch items: section 3. Pipeline
estimates: section 4 (placeholder). Ranking: section 5 (placeholder).

---

## 1. Licence pre-rows

### 1A. Government / CERT

#### 1A.1 UK NCSC (National Cyber Security Centre)
*Content class:* guidance, news, blog posts, threat reports (RSS feeds
offered for exactly these five classes). Not a structured advisory database.
*Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **3** (but low machine-readability; see Scrape-permitted) |
| License | **OGL v3.0 CONFIRMED (brief prior correct).** NCSC Website Terms & Conditions, `https://www.ncsc.gov.uk/section/about-this-website/terms-and-conditions`: *"Content on the Websites is, unless stated otherwise, subject to Crown copyright."* / *"you may use or reuse the content published on the Websites without prior permission but must adhere to and accept the terms of the Open Government Licence (OGL) v3.0."* / *"You must acknowledge the source of the content and include a link to the Open Government Licence wherever possible."* Carve-outs: *"Where materials are stated to include material under licence from third parties, those materials are not licenced for re-use."*; *"Images credited to a third party are not Crown copyright and are not licenced for re-use."*; logos are excluded from the OGL grant. |
| Scrape-permitted | **robots.txt:** `https://www.ncsc.gov.uk/robots.txt` returned HTTP 404 to WebFetch (**ABSENCE FINDING, method-suspect; shell check listed**). **ToS:** the T&C page, fetched not truncated, contains no clause on automated access, scraping or APIs (**ABSENCE FINDING, method-suspect**). NCSC publishes RSS feeds (`https://www.ncsc.gov.uk/information/rss-feeds`: All, Guidance, News, Blog posts, Threat Reports); that page states no terms for the feeds. OGL v3.0 itself grants the right to "copy, publish, distribute and transmit" and to adapt and exploit commercially. |
| Redistribute-verbatim | **YES** under OGL v3.0, with attribution (OGL attribution statement + link), excluding third-party-licensed material and third-party images. |
| Relicense-compatible | **YES.** OGL v3.0 is attribution-only; a WebSearch extract of the National Archives' OGL v3 text (`https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/`) says (verbatim, verified by red-reviewer via curl, 2026-10-03; the earlier "interoperable" wording was not verbatim): *"These terms are compatible with the Creative Commons Attribution License 4.0 ... when the Information is adapted and licensed under either of those licences, you automatically satisfy the conditions of the OGL when you comply with the other."* We retain the NCSC attribution and the OGL notice alongside our CC BY 4.0 grant. The compatibility sentence is now read from the National Archives OGL page by the gate (raw HTML, curl); robots 404 (HTML "site unavailable" page) and the T&C absence of an access clause (only hit: "automatically waive") are gate-confirmed. |
| Action | **(a) compatible.** Condition: per-record "Contains public sector information licensed under the Open Government Licence v3.0" notice; drop any item flagged as third-party material. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch (markdown-converting) of the T&C URL above, response stated "not truncated"; WebFetch of `/information/rss-feeds`; WebFetch of `/robots.txt` -> 404. Substrings read: "Crown copyright", "Open Government Licence", "third parties", "automated". Source kind: rendered HTML (method-exposed for absences, not for the positive OGL clause). |
| Non-English / facts-only | English. Facts + link + original summary is available but not needed for licence reasons. |

#### 1A.2 ACSC / ASD Australia (cyber.gov.au)
*Content class:* alerts, advisories, publications, annual threat report, ISM
(OSCAL mirror on GitHub). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1 (provisional; was 2)**, under the scale's score-1 clause "a grant known only from a search extract whose primary page could not be reached (provisional)" (D39) -- **unverified, extract-sourced.** The site-wide CC BY 4.0 grant has never been read from a primary page by this agent or by the gate (gate 2026-10-03: `cyber.gov.au` and `asd.gov.au` both accept TLS then return 0 bytes, Akamai, four ways tried). The only primary corroboration is **per-document**: the ASD `ism-oscal` README, *"provided under a Creative Commons Attribution 4.0 International licence ... this licence only applies to material as set out in this document"*. A per-document grant does not establish a site-wide one, so this row is not scored as if the site-wide licence were confirmed; it would return to 2 (action (a) with conditions) once the copyright page is read. |
| License | **CC BY 4.0 International, per search-engine extract of the site copyright page -- NOT read from the page itself.** WebFetch of `https://www.cyber.gov.au/about-us/copyright` **timed out three times** (60 s each) and `robots.txt` and the alerts-and-advisories page timed out likewise, so the operative clause below is a **WebSearch summary** of that page, not a quotation: all material "is provided under a Creative Commons Attribution 4.0 International licence, with the exception of the Commonwealth Coat of Arms, the Australian Cyber Security Centre logo, content supplied by third parties, and other material specifically not provided under a Creative Commons Attribution 4.0 licence"; attribution form "(c) Commonwealth of Australia 2026". The same search showed that **some ASD documents use "Creative Commons Attribution 4.0 Australian Licence"** (the 2024-25 Annual Cyber Threat Report) while others use the International version -- a per-document variation. The brief's prior "CC BY 4.0" is therefore **plausibly right but unverified at the primary page**; the brief's implied "uniform" is refuted by the per-document variant. |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (timeout). **ToS: NOT OBTAINED** beyond the copyright page summary. Timeouts on this host recurred for every URL tried, which suggests bot protection or a slow origin; this is a **fetch-tool limit, not a finding about ACSC**. Status: **UNKNOWN pending shell check**. |
| Redistribute-verbatim | **YES per the CC BY 4.0 grant above, excluding** Coat of Arms, ACSC logo and third-party content (provisional until the page is read). |
| Relicense-compatible | **YES** (CC BY 4.0 -> CC BY 4.0), provisional. The Australian-port variant is a sibling licence, not identical; per-document licence field must be read. |
| Action | **(d) unknown until the copyright page is read**; the (a) path above applies only to the ISM OSCAL material under its README grant. A browser-session or different-network read of the copyright page is the route (curl and WebFetch both failed). |
| Date-checked | 2026-10-02 (search summary only) |
| Retrieval method | WebSearch query "cyber.gov.au copyright Creative Commons Attribution 4.0 content Australian Signals Directorate licence" (result summary, not page text). WebFetch of copyright, robots.txt, alerts page: all **timeout of 60000 ms**. Source kind: search-engine summary of rendered HTML (**weakest tier**). |
| Non-English / facts-only | English. |

#### 1A.3 CCCS Canada (Canadian Centre for Cyber Security)
*Content class:* alerts and advisories, publications. *Language:* English and
French (the site is bilingual; French is the official parallel text).

| Field | Value |
|---|---|
| Cleanliness score | **1** (brief's "permissive trio" framing is refuted for this member). Gate 2026-10-03 (curl): non-commercial clause verbatim as quoted; robots 404; CSE terms contain no access clause. **Citation correction:** the cyber.gc.ca homepage footer links `https://www.canada.ca/en/transparency/terms.html` (same non-commercial wording), and the CSE terms are linked from the about page; conclusion unchanged. The "terms-href" test in check 3 matches the canada.ca global footer and cannot by itself refute "CSE terms only". |
| License | **No open licence. Non-commercial reproduction only.** cyber.gc.ca footer links to the CSE terms (`https://cse-cst.gc.ca/en/corporate-information/terms-and-conditions`, confirmed via WebFetch of `https://www.cyber.gc.ca/en/about-cyber-centre`). That page, fetched 2026-10-02: *"Information on this site, other than government symbols and other graphics, has been posted with the intent that it be readily available for personal and public non-commercial use and may be reproduced, in part or in whole and by any means, without charge or further permission from CSE."* with conditions: due diligence on accuracy; CSE identified as source; reproduction *"not represented as an official version ... nor as having been made, in affiliation with or with the endorsement of CSE"*. And: *"Unless otherwise specified, you may not reproduce materials on these sites, in whole or in part, for the purposes of commercial redistribution without prior written permission of the CSE."* Non-Canadian commercial requests are "generally not permitted". |
| Scrape-permitted | **robots.txt: NOT FETCHED.** **ToS:** the page above has no automated-access clause (**ABSENCE FINDING, method-suspect**). The terms page the footer points to is the CSE's; whether a separate cyber.gc.ca-specific terms page exists was not established (two guessed cyber.gc.ca terms URLs returned 404). |
| Redistribute-verbatim | **NO for our purposes.** Non-commercial reproduction is permitted; this project's data is distributed under CC BY 4.0, which permits commercial downstream use, so verbatim CCCS text cannot be shipped under that grant. |
| Relicense-compatible | **NO.** A non-commercial-only permission cannot be folded into a CC BY 4.0 dataset. (Whether facts + link survive is a copyright-expression question; facts are not protected, but the Canadian *"commercial redistribution"* restriction is on "materials", so facts + link + original summary is the conservative remedy.) |
| Action | **(c) prohibited for verbatim -> facts + link + <=2-sentence original summary.** Optionally **(d)** a request to CSE for a commercial/open-data permission (user sends). Note Canada's Open Government Licence - Canada exists for departmental open data; **CCCS advisories are not published under it per this page**. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the CSE terms URL (clause text above, not truncated per tool); WebFetch of `/en/about-cyber-centre` to find the footer link; WebSearch for the cyber.gc.ca summary (agreed with the fetch). Two guessed URLs (`/en/terms-conditions`, `/en/about-cyber-centre/terms-conditions`) -> 404. Source kind: rendered HTML. The **positive** clause is not method-exposed; absence of an automated-access clause is. |
| Non-English / facts-only | Bilingual. Facts + link + original summary is the required shape; summary would be generated offline per the WS0-T3 rule. |

#### 1A.4 ENISA (publications and website)
*Content class:* threat-landscape reports, guidance, AI cybersecurity reports;
**not** a feed of advisories (EUVD is the vulnerability service, row 1B.2).
*Language:* English (some translations).

| Field | Value |
|---|---|
| Cleanliness score | **2 for PDF reports and media publications** (CC BY 4.0 with "unless otherwise noted" and third-party carve-outs); **1 for website page text** (reproduction authorised, adaptation not granted; see Legal notice below) |
| License | **CC BY 4.0 for publications.** Boilerplate extracted from multiple ENISA PDFs by WebSearch: *"Unless otherwise noted, the reuse of this document is authorised under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence"*; for photos or other material not under ENISA copyright, permission is to be sought from the copyright holders. The search also returned a paraphrase of ENISA's IPR policy: public reports and media publications under CC BY 4.0, re-user must state changes and may not imply endorsement; this rests on Commission Decision 2011/833/EU. **Primary text now read** (ENISA IPR Policy, public version, December 2021, `https://www.enisa.europa.eu/about-enisa/legal-notice/enisa-ipr-policy-public-version`, served as a PDF and read page by page from the saved file): s2.1.1 *"ENISA shares its public reports and media publications under open license with the use of Creative Commons – Attribution 4.0 – International (CC BY 4.0)."* / *"any possible re-use is allowed under the condition that ENISA is properly referenced as the source"*, plus: modifiers must state changes; no implied endorsement; partial use keeps the link to the original; translations must say ENISA did not endorse them. **Carve-out found:** s2.2 *educational/training courses and material* are **CC BY-NC-ND 4.0** (non-commercial, no derivatives) -- these must be excluded. s2.3 software is EUPL v1.2. Principle of attribution (s1.3): works are *"in principle free to share, free of charges and free to re-use"*. The policy speaks of "reports", "publications", "websites content" and "databases" generically in its definitions but **grants CC BY 4.0 only to public reports and media publications**; **website page text and any ENISA-run database/service (EUVD, row 1B.2) are not expressly licensed by this policy**. Reuse questions: `info@enisa.europa.eu`. **Legal notice (website text), verified by red-reviewer via curl, 2026-10-03:** the homepage footer links `https://www.enisa.europa.eu/about-enisa/legal-notice`, which states: *"Reproduction of ENISA material published on this website is authorized, provided the source is acknowledged, unless it is stated otherwise."* This is a **reproduction** permission with attribution. It is not CC BY, it grants **no right to adapt** (no derivative-works or sublicensing wording), and it yields to "unless stated otherwise". So verbatim web text may be reproduced with the source acknowledged, but a CC BY 4.0 relicense of it (which presupposes the right to license adaptations) is not supported. The footer also links a 2024-12 IPR path, but the PDF served there still reads "Public version \| December 2021", so the IPR-policy citation above stands. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` with only Drupal-style disallows (`/core/`, `/profiles/`, `/admin/`, `/search/`, `/user/...`, `/node/add/`, `/media/oembed`); publications and news paths are not disallowed. **ToS:** the legal notice above (found by the gate; the earlier "ToS not located" was refuted). No automated-access clause was reported by the gate in it. |
| Redistribute-verbatim | **YES for publications under CC BY 4.0** with attribution and change statement; **YES (reproduction, source acknowledged) for website text** unless stated otherwise; not for third-party photos/material. |
| Relicense-compatible | **YES** for CC BY 4.0 publications. **NO / not established for website text** (reproduction right only; no adaptation grant). |
| Action | **(a) compatible** for PDF reports and media publications (CC BY 4.0), excluding the CC BY-NC-ND training material and third-party photos. **(c) facts + link + original summary** for website page text (reproduction authorised, relicensing not). ENISA-run databases (EUVD) are row 1B.2, **(d)**. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebSearch (two queries) for the boilerplate; WebFetch of the IPR-policy URL -> returned a PDF that the markdown converter could not read; the saved PDF was then read directly with the Read tool (text layer + page images, pages 1-13, complete); WebFetch of robots.txt -> readable; WebFetch of two guessed legal-notice URLs -> 404 (the real path was found by the gate via the homepage footer). Legal-notice clause: red-reviewer via curl of raw HTML, 2026-10-03 (not re-fetched here). Source kind: primary PDF (policy clause, reliable) + search summary (boilerplate, weak) + robots.txt (reliable) + gate-read legal notice. |
| Non-English / facts-only | English primary. Facts-only not needed for licence reasons. |

#### 1A.5 BSI / CERT-Bund (Warn- und Informationsdienst, WID)
*Content class:* vulnerability short-advisories (Kurzinformationen), technical
warnings, CSAF documents, RSS. *Language:* **German** (some English).

| Field | Value |
|---|---|
| Cleanliness score | **1** (verbatim not allowed; facts + link + original summary is the shape) |
| License | **No open licence; non-commercial, unmodified use only.** BSI Nutzungsbedingungen, `https://www.bsi.bund.de/DE/Service/Nutzungsbedingungen/Nutzungsbedingungen_node.html` (WebFetch 2026-10-02): *"Software und Veröffentlichungen, die zum kostenfreien Download angeboten werden, dürfen nur zu nicht kommerziellen Zwecken verwendet werden."* / *"Eine weitergehende, insbesondere kommerzielle oder publizistische Verwendung bedarf der vorherigen Zustimmung durch das BSI."* / other downloadable content *"dürfen im Rahmen der gestatteten Verwendung nur unverändert verwendet werden."* (only IT-Grundschutz material may be modified, for internal security measures). **Gap:** the WID portal (`wid.cert-bund.de`) says it has its own "Nutzungsbedingungen"/Impressum; the fetches of the portal pages returned **only the page title** (JavaScript-rendered app shell or truncated), so the WID-specific terms and any licence field inside the CSAF documents were **not read**. Whether the WID terms are looser than the BSI-wide terms is **UNKNOWN -- unverified, extract-sourced: the gate also could not find them (WID is a JS app; 28 JS chunks grepped, route not found)**. Gate 2026-10-03 (curl): a sample CSAF advisory (wid-sec-w-2026-3717) carries `distribution` TLP:WHITE only and a liability-only `legal_disclaimer`, **no licence**; this supports "no open licence" but TLP:WHITE is a sharing marking, not a copyright grant. |
| Scrape-permitted | **robots.txt:** `bsi.bund.de/robots.txt` has `Crawl-delay: 10` (gate, curl); `wid.cert-bund.de/robots.txt` is 404 (gate, curl). **ToS:** no automated-access clause in the BSI page (**ABSENCE FINDING, method-suspect; gate-confirmed for the BSI-wide page only**). Official machine channels exist (RSS `https://wid.cert-bund.de/content/public/securityAdvisory/rss`, CSAF info page `https://wid.cert-bund.de/portal/wid/csaf/info`), which is evidence that machine access is intended, **not** evidence that reuse is licensed. |
| Redistribute-verbatim | **NO** (unmodified non-commercial use only; we would be modifying, translating and redistributing under a commercial-permitting licence). |
| Relicense-compatible | **NO.** |
| Action | **(c) prohibited -> facts + link + original summary** as the default. Possibly **(d)** if the WID/CSAF terms turn out looser: the CSAF `document.distribution` block is the first place to look and is a structured, JSON source, so a shell check of one real advisory settles it cheaply. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of BSI terms URL (clauses above, no truncation reported); WebFetch of two `wid.cert-bund.de` pages -> title only; WebSearch for WID terms. Source kind: rendered HTML (BSI) and a JS portal (WID, **method-suspect**). |
| Non-English / facts-only | **German.** Facts + link + original English summary is feasible; the summary must be generated offline, committed under `data/summaries/`, and written from the primary vendor advisory where possible, not translated from BSI prose (the same derivative-work caution as AIAAIC D2). |

#### 1A.6 ANSSI / CERT-FR
*Content class:* alerts (ALE), advisories (AVI), reports, IOCs, bulletins; RSS
for each. *Language:* **French** (some English).

| Field | Value |
|---|---|
| Cleanliness score | **3** |
| License | **Licence Ouverte / Open Licence v2.0 (Etalab), CONFIRMED.** CERT-FR Mentions legales, `https://www.cert.ssi.gouv.fr/mentions-legales/` (WebFetch 2026-10-02): *"Sauf mention explicite contraire, les contenus présents sur le site internet du CERT-FR sont couverts par la Licence ouverte / open licence, version 2.0."* Carve-out: trademark/logo (the ANSSI logo needs prior authorisation). Reuse requests: communication address on the page. Corroborated by a WebSearch summary of the same page and of the Etalab licence (attribution of source and date of last update). |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` `Disallow: /pdf`, `/tar`, `/js`, `/fonts`, `/fiche/`. Advisory paths (`/avis/`, `/alerte/`) are not disallowed; **PDF copies and `/fiche/` are**, so ingest must use the HTML/RSS only. **ToS:** the Mentions legales page offers RSS feeds (full, alerts, threat reports, advisories, IOCs, hardening, news) and has no clause restricting automated access (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **YES**, with source + date-of-last-update attribution. |
| Relicense-compatible | **YES.** Licence Ouverte 2.0 is an attribution-only licence that Etalab publishes as compatible with CC BY (taken on trust, see below). |
| Action | **(a) compatible.** Condition: per-record attribution (source = CERT-FR/ANSSI, date of last update, link to Licence Ouverte v2.0); do not fetch `/pdf` or `/fiche/` paths; exclude the ANSSI logo. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the Mentions legales URL (clause quoted above, not reported truncated), WebFetch of `robots.txt`, WebSearch cross-check. Source kind: rendered HTML (positive clause reliable; absence of an automated-access clause method-suspect) + robots.txt (reliable). |
| Non-English / facts-only | **French.** Because the licence is open, verbatim French text could be kept, but a French-only description in an English-schema corpus is of low value; the practical shape is original English summary + link, generated offline (pipeline-engineer decides). Licence does not force facts-only. |

#### 1A.7 JPCERT/CC (jpcert.or.jp: alerts, advisories, weekly reports)
*Content class:* alerts, security advisories, blog. *Language:* **Japanese** with
an English subset.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **Site terms exist (the earlier "No licence/ToS located" was REFUTED by the gate); they are a quotation/redistribution rule, not an open licence.** Verified by red-reviewer via curl of raw HTML, 2026-10-03: the homepage links `ご利用にあたって` = `https://www.jpcert.or.jp/guide.html`. Its section 2 (Japanese; gate's rendering, not re-read here): **quotation is free** provided source, title and URL are given; **転載・再配布 (reprinting / redistribution) requires notifying `office@jpcert.or.jp`** (quotation: notification requested, not required); JPCERT/CC coordinates third-party rights where needed; and **individual documents may carry their own conditions**. Footer `© 1996-2026 JPCERT/CC` stands. This is permission-with-notification for redistribution of JPCERT/CC's own text, not a CC/OGL-style grant: it says nothing about adaptation or sublicensing, so a CC BY 4.0 relicense is not supported. |
| Scrape-permitted | **robots.txt:** `https://www.jpcert.or.jp/robots.txt` -> 404 (confirmed by the gate, curl). **ToS:** `guide.html` s2 above; no access/automation clause was reported by the gate. |
| Redistribute-verbatim | **CONDITIONAL**: notification to `office@jpcert.or.jp` required per `guide.html` s2; per-document conditions may override. Not an unconditional YES. |
| Relicense-compatible | **UNKNOWN -> treated as NO** (no adaptation/sublicensing grant). |
| Action | **(d) notification/outreach.** The correct address is **`office@jpcert.or.jp`** (notification for redistribution; the earlier target was wrong). Do not ingest verbatim before notice is given and answered. Fallback shape: **(c) facts + link + original summary**, where quotation with source/title/URL is free. JPCERT advisory content is largely duplicated by JVN (row 1A.8). Score stays 1 (not 2): the redistribution permission is conditional and not a licence that supports CC BY. |
| Date-checked | 2026-10-02; corrected 2026-10-03 from the gate verdict |
| Retrieval method | Original: WebFetch of `/english/` and `/english/privacy.html` (guessed ToS URLs 404). That route missed the Japanese homepage's `ご利用にあたって` link. Correction: red-reviewer via curl of raw HTML (homepage link, `guide.html` s2, robots 404), 2026-10-03; not re-fetched here, and the Japanese text is carried from the gate's rendering. |
| Non-English / facts-only | Japanese primary. Original English summary + link; generated offline. |

#### 1A.8 JVN (Japan Vulnerability Notes, jvn.jp) and JVN iPedia (jvndb.jvn.jp)
Two services, two operators: **JVN** (jvn.jp) is run by JPCERT/CC and IPA;
**JVN iPedia** (jvndb.jvn.jp) and the **MyJVN API** are run by IPA. Reported
as one row per the brief, with the split recorded.
*Content class:* CVE-keyed vulnerability notes with CVSS, vendor status; feeds
in RSS 1.0 and the MyJVN API; English translations exist (`/en/`).
*Language:* Japanese + English.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **Copyright asserted ("All rights reserved"), with an informal FAQ statement of no restrictions plus a request to notify by email. No licence document.** JVN iPedia page footer: *"Copyright © 2007- IPA. All rights reserved."*; JVN feeds page (`https://jvn.jp/en/rss/index.html`): *"Copyright © 2000-2015 JPCERT/CC and IPA. All rights reserved."* **FAQ Q5-2** on `https://jvndb.jvn.jp/nav/jvndb_faq.html` (Shift_JIS; **verified by red-reviewer via curl, 2026-10-03**): 「引用、転載、再配布するにあたり、特に制限は設けておりません。また、ご利用の際はメールでお知らせいただくことをお願いしております。」 = *"no particular restrictions are set on quotation, reprinting or redistribution; when using it, we ask that you notify us by email."* **Q5-1** says the same for commercial use, subject to the MyJVN API terms. (The English-language FAQ path `/en/nav/jvndb_faq.html` is 404, and the "separately provided guidelines" sentence this row previously quoted is **not on the page**: 0 hits for "separately provided" and 別途. That sentence and the "guidelines not located" finding are withdrawn.) **MyJVN API terms** (`https://jvndb.jvn.jp/apis/termsofuse.html`, service terms 2010, rev. 2019, gate): disclaimer plus prohibited acts (malware, illegal acts, defamation); **no reuse restriction**. They are the API service terms, not "tool terms" (the separate PDF `.../myjvn/document/termsofuse.pdf`, enacted 2023.3.29, governs the two software tools, read earlier in full). **Auditor's reasoning on the score:** an informal FAQ permission is not a licence: it is unsigned by any rights-holder statement, conflicts with the "All rights reserved" footers on the same service, and says nothing about adaptation or sublicensing (so no basis for a CC BY 4.0 relicense). It also sits on **jvndb.jvn.jp (IPA)**; **jvn.jp (JPCERT/CC and IPA) is a separate site** whose own footer asserts rights and which the FAQ does not address. So the FAQ lowers the risk of facts + link but does not lift the score. |
| Scrape-permitted | **robots.txt:** 404 on both `jvndb.jvn.jp` and `jvn.jp` (gate, curl). **ToS:** MyJVN API service terms above: no scraping or reuse clause. The MyJVN API and RSS are *official machine channels* run for the purpose, which supports access. |
| Redistribute-verbatim | **UNKNOWN -> treated as NO** (informal FAQ statement only; conflicts with the footers). Note CVE text itself is separately governed by the CVE Terms of Use (row 1B.3); JVN's added value is the Japanese/English analysis, CVSS and vendor-status fields, on which IPA/JPCERT assert copyright. |
| Relicense-compatible | **UNKNOWN -> treated as NO.** |
| Action | **(d) unknown -> outreach** to IPA (`isec-jvndb@ipa.go.jp`; the page renders the address as an image with alt text "Mail Address isec-jvndb", so the "@ipa.go.jp" part is **inferred, not page text**) asking for a written statement of terms for quotation/redistribution/adaptation of JVN iPedia and JVN data, and whether CC BY-compatible reuse is allowed; the FAQ's own request to notify by email is the natural opener. User sends. Interim shape: **(c) facts + link**, where facts = JVNDB id, CVE id, dates, affected-product names, link; CVSS scores are IPA's analysis and sit in the grey zone. |
| Date-checked | 2026-10-02; corrected 2026-10-03 from the gate verdict |
| Retrieval method | Original: WebFetch of `jvndb.jvn.jp/en/`, `/en/nav/jvndbhelp.html`, `/nav/jvndb_faq.html`, `jvn.jp/en/rss/index.html`, `jvn.jp/en/nav/jvnhelp.html`, `/apis/termsofuse.html` (encoding problems / truncation), robots.txt (404), and the MyJVN tools PDF read in full. The WebFetch route misrepresented the Japanese FAQ (quoted a sentence not on the page). Correction: red-reviewer via curl of raw Shift_JIS HTML, 2026-10-03; Q5-1/Q5-2 and the API terms are carried from the gate, not re-fetched here. |
| Non-English / facts-only | Japanese + English. English text exists upstream, so translation is not needed; the facts + link + original summary shape applies if (c). |

#### 1A.9 SingCERT / CSA Singapore
*Content class:* alerts and advisories, playbooks, reports. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **0 (was 1).** Corrected after the gate: the terms also prohibit caching, links and framing without permission, which contests even the "facts + link" shape that score 1 requires to be uncontested. |
| License | **All rights reserved; written permission required, for reproduction AND for linking.** CSA Terms of Use, `https://www.csa.gov.sg/terms-of-use/`: *"Contents of this website shall not be reproduced, republished, uploaded, posted, transmitted or otherwise distributed"* without CSA's prior written permission; graphics and images likewise. **Clause missed in the first pass, verified by red-reviewer via curl, 2026-10-03:** *"Except as set forth below, caching and links to, and the framing of this website or any of the Contents are prohibited. You must secure permission from CSA prior to hyperlinking to, or framing, this website or any of the Contents, or engaging in similar activities."* The "Governing Law" cut-off ("shall be hear.") is genuine on the page, **not** a tool artefact (gate). |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-Agent: *` `Allow: /` `Disallow: /search`; sitemap listed. So robots permits crawling advisory pages. **ToS:** no explicit clause on robots, scraping or automated access found (**ABSENCE FINDING, method-suspect**), but the reproduction prohibition above applies to what scraping would yield. |
| Redistribute-verbatim | **NO** without CSA's written permission. |
| Relicense-compatible | **NO.** |
| Action | **(d) written permission required; no ingest and no hyperlinks until granted** (the link prohibition removes the "link only" interim that other score-0 rows use). No open-data licence for SingCERT advisories was found (**ABSENCE FINDING, method-suspect**: only the terms page was read; Singapore government open-data licensing was not searched). Expected value of asking is low. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the terms URL and of `robots.txt` (both read); WebSearch (matching extract). Source kind: rendered HTML; the clause is positive, so not method-exposed; the absence of an automated-access clause is. |
| Non-English / facts-only | English. No shape is available without permission (facts + link is itself contested by the link prohibition). |

#### 1A.10 CERT-EU
*Content class:* security advisories (14 published in 2026 up to 27 Sept, all
mainstream enterprise products, **none AI-related** on the page read), threat
landscape reports, RSS (`/publications/security-advisories-rss`). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (two statements on the same site contradict each other) |
| License | **CONTRADICTORY.** The legal notice at `https://cert.europa.eu/legal-notice` (WebFetch 2026-10-02) states reuse under the Commission policy: *"The reuse policy of European Commission documents is implemented by Commission Decision 2011/833/EU of 12 December 2011"*; content *"authorized under Creative Commons Attribution 4.0 International (CC-BY 4.0)"* with *"reuse is allowed, provided appropriate credit is given and changes are indicated"*; carve-outs for identifiable individuals, third-party works, and material under industrial property rights. **But** the security-advisories listing page, `https://cert.europa.eu/publications/security-advisories/` (WebFetch 2026-10-02), has the footer *"(c) 2022-2026 CERT-EU. All rights reserved."* and no TLP/licence marking. **Correction (gate, curl, 2026-10-03):** the legal notice **is CERT-EU's own** -- it reads "(c) ... (CERT-EU), 2023" and "CERT-EU maintains this website" -- so the earlier statement that it "did not mention CERT-EU" is refuted. The "All rights reserved" footer also appears **on the legal-notice page itself**, so the contradiction stands within a single document. Per the rule that ambiguity is not resolved in the project's favour: UNKNOWN. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** blacklist-style; named bots (FAST/Scirus, Nutch, Sogou, Xenu, discoverybot, Youdao) are `Disallow: /`; `User-agent: *` -> `Allow: /`, `Disallow: /files/css/*`, `/files/js/*`. **ToS:** no automated-access clause in the legal-notice extract (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **UNKNOWN**; CC BY 4.0 plausible per the legal notice, contradicted by the footer. |
| Relicense-compatible | **UNKNOWN**; would be YES if CC BY 4.0 applies. |
| Action | **(d) unknown -> outreach** to CERT-EU asking which statement governs advisory text. Interim: **(c)**. Low priority: the advisories seen were not AI-related, so the expected yield is near zero (volume belongs to the pipeline-engineer section). |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `/legal-notice`, `/publications/security-advisories/`, `/robots.txt`. Source kind: rendered HTML. The contradiction is a positive finding on two pages; the "no automated-access clause" is an absence finding. |
| Non-English / facts-only | English. |

### 1B. Vulnerability databases

#### 1B.2 EUVD (European Vulnerability Database, ENISA)
*Content class:* CVE-keyed and EUVD-id vulnerabilities, exploited and critical
lists, advisories, CVE<->EUVD mapping, KEV dump. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (unchanged after weighing the two items below) |
| License | **No licence for the data; a reproduction notice that may or may not reach it; a docs-repo licence that covers the docs only.** (Earlier "None located" was REFUTED by the gate.) (1) **ENISA Legal Notice**, `https://www.enisa.europa.eu/about-enisa/legal-notice`: *"Reproduction of ENISA material published on this website is authorized, provided the source is acknowledged, unless it is stated otherwise."* The EUVD SPA bundle (`main.bdd2ef30.js`) footer links this same notice (red-reviewer, curl, 2026-10-03). It is a reproduction permission for material "published on this website"; whether JSON served from `euvdservices.enisa.europa.eu` counts as such material is **not established**, and it grants no adaptation or CC BY right (row 1A.4). (2) **Official docs repo** `github.com/enisaeu/euvd-docs-public` (pushed 2026-09-18; GitHub API spdx `NOASSERTION`), LICENSE: *"This repository is made available solely for programmatic access by the EUVD frontend. No reuse, redistribution, or modification of its contents is permitted without written permission from ENISA."* That covers the **documentation repo, not the data**, but it shows ENISA expressly withholding reuse rights for at least the EUVD documentation and does not help the data question. Net: no data licence; at most a reproduction permission of uncertain reach. Score 1, (d). The ENISA IPR Policy (row 1A.4) grants CC BY 4.0 to *"public reports and media publications"* only; it does not name EUVD. A structured API response (`https://euvdservices.enisa.europa.eu/api/lastvulnerabilities`, fetched 2026-10-02 as JSON: fields `id, enisaUuid, description, datePublished, dateUpdated, baseScore, baseScoreVersion, baseScoreVector, references, aliases, assigner, epss, enisaIdVendor`) carries **no licence, terms or disclaimer field**. The UI/docs URLs `https://euvd.enisa.europa.eu/` and `/apidoc` returned only an error shell: *"The European Vulnerability Database application could not be loaded."* (a single-page app that the fetch tool could not run; **this is a tool limit, not a statement about the site**). Underlying data: CVE records (governed by the CVE ToU, row 1B.3), `epss` scores (FIRST), and CNA/ENISA enrichment. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02) at `euvd.enisa.europa.eu`:** `User-agent: *` `Disallow:` (empty = everything allowed). **ToS:** the ENISA Legal Notice above (linked from the SPA footer; found by the gate in the JS bundle). Official `apidoc.md` (in the docs repo): endpoints **"require no authentication"**; at most 8 or 100 records per request depending on endpoint; no versioning or changelog. API response headers carry no licence/Link/terms (gate, curl). |
| Redistribute-verbatim | **UNKNOWN.** CVE-derived fields: YES under CVE ToU with the MITRE notice. ENISA-added fields (EUVD id, enrichment): UNKNOWN. EPSS: FIRST's own terms apply (not checked here -- on trust). |
| Relicense-compatible | **UNKNOWN** for ENISA-added fields; CVE-derived fields compatible (row 1B.3). |
| Action | **(d) unknown -> outreach** to ENISA (`info@enisa.europa.eu`, the IPR policy's contact) on EUVD reuse; interim shape **(c)**: EUVD id + CVE id + link, descriptions taken from the CVE record, not from EUVD. Do not copy text from the `euvd-docs-public` repo (LICENSE bars it). The outreach should ask specifically whether the API data falls under the Legal Notice's reproduction clause and whether adaptation/CC BY relicensing is permitted. Third-party docs (`github.com/bytew0lf/EUVD-API`, "not official") are superseded by the official `apidoc.md`; see watch item W2. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `euvd.enisa.europa.eu/`, `/apidoc` -> error shell; WebFetch of `robots.txt` (readable); WebFetch of `euvdservices.enisa.europa.eu/api/lastvulnerabilities` -> JSON (**structured endpoint**); WebSearch for docs. Source kind: **JSON endpoint (reliable for fields present; silent on legal terms by construction)** + SPA shell (**method-suspect**: the shell hid the footer link; the gate found it in the JS bundle). Legal notice, docs-repo LICENSE and `apidoc.md` facts: red-reviewer via curl/GitHub, 2026-10-03; carried from the gate, not re-fetched here. |
| Non-English / facts-only | English. |

#### 1B.3 cvelistV5 (CVEProject/cvelistV5; CVE Program Terms of Use)
*Content class:* every CVE record in CVE JSON 5, upstream of NVD; bulk zips
(daily baseline, hourly deltas). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **2** (grant is clear and compatible; the notice condition is engineering work, and the repo currently shows no MITRE notice) |
| License | **CVE Terms of Use (SPDX id `CVE-TOU`).** GitHub repo license field is **`null`** (structured: `https://api.github.com/repos/CVEProject/cvelistV5`, fetched 2026-10-02 -- no repository LICENSE file; a `LICENSE` raw URL returned 404). README, `https://raw.githubusercontent.com/CVEProject/cvelistV5/main/README.md`: *"You may search, download, and use the content hosted in this repository, per the CVE Program Terms of Use."* The ToU text (`https://spdx.org/licenses/cve-tou.html`, fetched 2026-10-02; `cve.org/Legal/TermsOfUse` is a JS app the tool could not render): *"MITRE hereby grants you a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute Common Vulnerabilities and Exposures (CVE). Any copy you make for such purposes is authorized provided that you reproduce MITRE's copyright designation and this license in any such copy."* |
| Scrape-permitted | Not scraping: official bulk repo and release zips designed for mirroring (README: baseline zip daily, hourly delta zips, "about every 7 minutes" repo updates). GitHub API rate limits apply if cloned via API; use release assets or `git clone`. **robots.txt not applicable** (GitHub-hosted); **ToS** = the licence above. |
| Redistribute-verbatim | **YES**, with MITRE's copyright designation and the licence text reproduced in copies. |
| Relicense-compatible | **YES, with a notice condition.** The grant includes "sublicense" and "prepare derivative works", so a CC BY 4.0 grant by us over our derived dataset is allowed provided the MITRE notice and CVE-ToU text travel with it. **Existing-corpus gap:** the corpus already carries NVD-derived CVE text (SOURCE_LICENSES 2.2), so the MITRE notice requirement applies **today**, independent of this evaluation. **Correction (gate, 2026-10-03):** the earlier sentence "a grep for 'MITRE Corporation' found nothing" was **false** -- the original pattern ('Copyright.*MITRE|CVE.*Terms of Use') hits NOTICE-DATA:41 and .reuse/dep5:17 — both the MITRE ATLAS Apache notice, not the CVE ToU. The real check is a targeted `git grep` for `Common Vulnerabilities and Exposures`, `hereby grants you a perpetual` and `cve.org/Legal`, which finds **no notice-file hits**; the gap is **confirmed** by that check (section 6 item 13). **CVE ToU grant, from cve.org's own source** (`CVEProject/cve-website`, `src/views/Legal/TermsOfUse.vue`, gate): the grant includes "sublicense" and the condition to *"reproduce MITRE's copyright designation"* with the licence in any copy. |
| Action | **(a) compatible with condition.** Condition: add the CVE ToU notice (MITRE copyright designation + the licence sentence) to `NOTICE-DATA`/README for every CVE-derived record. For CNA-authored descriptions: the grant covers the CVE record; individual CNA text could in principle carry third-party rights, but the ToU does not carve any out. |
| Date-checked | 2026-10-02 |
| Retrieval method | **GitHub API JSON** (`license: null`), raw README via WebFetch, SPDX licence page via WebFetch (text of the licence), WebSearch (one extract agreeing). Source kind: **structured (API/SPDX) for the licence identity and text; README rendered**. `cve.org/Legal/TermsOfUse` not readable by the tool (JS app), so the canonical page was not read: the SPDX copy is the cited text. |
| Non-English / facts-only | English. |

#### 1B.4 VulnCheck KEV
*Content class:* superset of CISA KEV with additional exploited-in-the-wild
evidence and dates; JSON via VulnCheck Community API/index. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **0** (two documents from the same vendor point opposite ways; the restrictive one explicitly bars making the data available under an open licence, which is what a CC BY 4.0 release is) |
| License | **Two vendor documents conflict; not resolvable from public text.** (1) Attribution page, `https://docs.vulncheck.com/community/vulncheck-kev/attribution`: *"Leveraging VulnCheck KEV and the data in it, in your own production, solution, or service, is easy to do at no additional cost, but requires prominent attribution to VulnCheck."*; data must be labelled "VulnCheck Known Exploited Vulnerabilities" or "VulnCheck KEV"; usable "publicly or in cybersecurity product or service", "in whole or in part". Landing page `https://vulncheck.com/kev`: *"The VulnCheck KEV is a resource available to our registered Community members at no cost"*. (2) Service Terms, `https://www.vulncheck.com/service-terms` (titled "Enterprise Terms of Service" in search results): *"Customer may not make the Services Data available for free or under an open source or similar license"*; also, users without a paid subscription may not use a Free Offering *"or any data or output obtained from any Free Offering, for the purpose of developing, training, or fine-tuning any artificial intelligence model"*; no modify/translate/derivative-works of the Service. (3) A third-party licensing appendix (`vdb.vulnetix.com/licensing/`) lists VulnCheck KEV under "Commercial / Membership Required". A CC BY 4.0 dataset is exactly "available for free ... under an open ... license". Whether the Enterprise terms bind Community KEV users, and whether the attribution page's "publicly" permission overrides them, is **UNKNOWN**. |
| Scrape-permitted | **Registration and API token required** (Community account); automated access is the intended mode via the API, but token terms were not read. robots.txt not fetched. **ToS** as above. The AI-training clause is a second problem: our CC BY 4.0 data is explicitly reusable for model training. |
| Redistribute-verbatim | **UNKNOWN -> treated as NO.** |
| Relicense-compatible | **UNKNOWN -> treated as NO.** The "no open licence" clause is the operative reason. |
| Action | **(d) unknown -> outreach** to `community@vulncheck.com` (the address the attribution page gives for attribution questions) asking explicitly whether a CC BY 4.0 dataset containing VulnCheck KEV fields is permitted and whether the AI-training restriction reaches downstream users. Until answered: **do not ingest**. Note for the corpus: CISA KEV is already ingested (CC0, SOURCE_LICENSES 2.1); a VulnCheck-only `exploited_in_wild` flag would have to be shipped without redistributing the VulnCheck data (e.g. a pointer), which is a design question for the pipeline-engineer, not a licence fix. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `vulncheck.com/kev`, the attribution page, the FAQ (**truncated** -- redistribution Q&A not seen), `service-terms`; WebSearch. Source kind: rendered HTML. Clause texts are positive findings quoted through the markdown converter (paraphrase risk: the service-terms quotes should be re-read in raw HTML). **Gate 2026-10-03 (curl, script-stripped text): both service-terms clauses verbatim at `https://www.vulncheck.com/service-terms` (rev. April 20, 2026); the Free/Trial clause explicitly names the "community" version; the full untruncated FAQ has no redistribution Q&A, only "It's free! We only ask for prominent attribution."; the attribution page also says "Including VulnCheck KEV in your open source or commercial product is meant to be free". The conflict is real and sharper than recorded; 0 follows.** |
| Non-English / facts-only | English. |

#### 1B.5 AVID (AI Vulnerability Database)
*Content class:* AI failure-mode vulnerability records (AVID-YYYY-Vnnn) and
incident reports (AVID-YYYY-Rnnnn); taxonomy (SEP). *Language:* English.

**Already in the corpus.** The brief lists AVID as a candidate for ingestion.
It is not new: `ingest/avid_owasp_incidents.json` carries AVID-keyed records
(grep: 218 `AVID-20` mentions in `data/incidents.json`; the E5 audit,
`docs/audits/E5-corpus-composition-2026-07-31.md`, counts **109 entries with the
AVID id prefix**), `scripts/merge_and_dedupe.py:238` maps `avidml.org` to a
reference type, and `docs/DATA_DICTIONARY.md:121` lists the "ATLAS/AVID/garak
imports" as static, manual imports. **`docs/SOURCE_LICENSES.md` has no AVID row**
(Grep for "AVID" in that file: no match) although invariant 10 has been active
since that file landed. This pre-row can serve as the missing row.

**Existing curated subset (foreman correction 2026-10-02, counts re-checked by
Grep of the worktree).** `ingest/avid_owasp_incidents.json` has **130**
`source_id` rows: **109** `AVID-` and **21** other (OWASP GenAI roundup items).
It is hand-curated, with no ingest script (`ingest/README.md:37` per the
foreman). `grep -i "avid_owasp\|arxiv_incidents"` over `docs/SOURCE_LICENSES.md`
and `ingest/README.md` finds nothing in the former, so **no `SOURCE_LICENSES.md`
row names this file.** (An earlier line of this row said "218 mentions"; that
counted `AVID-20` strings in the JSON including cross-references, not rows.)
**Would this pre-row cover the 109 AVID rows? Yes**, as they are AVID-derived
and MIT applies; the MIT notice and per-record AVID link still have to be
confirmed present. **It does not cover the 21 OWASP rows**, whose licence is
unassessed here. Whether the 109 rows copy AVID text or are original
paraphrase was not compared. Recorded only; `SOURCE_LICENSES.md` untouched.

| Field | Value |
|---|---|
| Cleanliness score | **2** |
| License | **MIT for the `avidml/avid-db` repository (structured).** GitHub API (`https://api.github.com/repos/avidml/avid-db`, fetched 2026-10-02): `license: {key: mit, spdx_id: MIT}`; raw LICENSE: *"MIT License / Copyright (c) 2022 AI Vulnerability Database (AVID)"*. Repo contents (API): `reports`, `scripts`, `vulnerabilities` (`2022`, `2023` subfolders), `LICENSE`, `README.md`; last push 2026-03-26. **Caveats:** (i) MIT is a software licence applied to a data repo; it is the only grant found, and it covers the repo as a whole; (ii) the live site (`https://avidml.org/database/`) lists reports up to **AVID-2026-R1714** (gate, curl, 1,785 IDs; the earlier "R0518" came from a truncated fetch), so **the repo may lag the site**; (iii) records summarise third-party material (papers, news, other databases) whose rights are not AVID's to grant. The website database page showed **no licence statement** (**gate-confirmed by curl: no licence string in 508 KB / 1,785 IDs**) and `https://docs.avidml.org/` showed none in the portion fetched. |
| Scrape-permitted | Repo is public JSON on GitHub: clone, no scraping. Site `robots.txt`/ToS **not fetched** (not needed if the repo is the source). |
| Redistribute-verbatim | **YES for the repo content under MIT**, with the copyright and permission notice retained; excluding any third-party text inside records (not audited). |
| Relicense-compatible | **YES** (MIT is permissive and attribution-only), with the MIT notice reproduced. |
| Action | **(a) compatible with conditions:** keep the MIT notice with AVID-derived data; per-record `source` pointer to the AVID id; ingest from the repo, not from the website, so the licence in force is the MIT one. Existing 109 AVID-prefix entries: add the missing SOURCE_LICENSES row and confirm the MIT notice is carried (the entries seen in `ingest/avid_owasp_incidents.json` are short original-looking descriptions keyed to an AVID URL, which is consistent with facts + link, but they were **not compared against AVID text** in this pass). |
| WS7-T1 neighbour-positioning | AVID is one of the six RELATED_WORK neighbours named in `MASTER_IMPROVEMENT_PLAN.md` WS7-T1 (line 312; `docs/RELATED_WORK.md` **does not exist yet**, the plan's task is open). **Ingesting AVID does not change the positioning claim; it makes it more specific:** genai_incidents already consumes AVID (109 AVID-id entries by the E5 audit), so against AVID the honest sentence is that this corpus is a *cross-index that includes AVID records under AVID's MIT licence*, not an independent or superior AI-vulnerability database; the differentiator must come from the other axes in the WS7-T1 table (cross-source dedupe, taxonomy mappings, exports), never from record count or "single source of truth" (already purged under WS0-T5). Expanding the AVID share must not be described as AVID coverage unless the repo-vs-site lag (ii) is measured. |
| Date-checked | 2026-10-02 |
| Retrieval method | **GitHub API JSON** (`license`, `contents`), raw LICENSE via WebFetch (first lines), WebFetch of `avidml.org/database/` (truncated), `docs.avidml.org/` (portion read); local Grep of the worktree for existing AVID use. Source kind: **structured (licence)**; rendered HTML for the site (method-suspect for absences). |
| Non-English / facts-only | English. Facts + link remains the safe shape for third-party-derived fields. |

### 1C. Regulators and courts

**Cross-cutting note for every row in this section.** Regulator decisions and
judgments name private individuals and often contain special-category data.
Even where the licence allows reuse, a GDPR/PIPEDA/UK GDPR data-protection
question is separate and **not assessed here**; the safe shape in every row is
organisation-level facts (controller, system, outcome, fine, date) + link +
original summary, with no natural-person names. Several of these authorities
also state their own limits on reusing personal data (e.g. the Garante guidance
extract above and Italy's D.Lgs. 33/2013 reference).

#### 1C.1 Italy Garante per la protezione dei dati personali
*Content class:* provvedimenti (decisions/orders), newsletters, press releases (docweb). *Language:* **Italian**.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **No general licence located; one narrow CC BY grant; reproduction of "official text" allowed with source + non-official note (second-hand).** `https://www.garanteprivacy.it/temi/creative-commons` (WebFetch 2026-10-02): only the winning privacy-icon projects of a contest *"sono utilizzabili secondo i termini della licenza CC BY"*; the page gives no licence for provvedimenti, guidelines or general site content. A WebSearch extract of Garante docweb pages says that reproduction of the Garante's official texts in electronic/paper form is permitted *provided that the source is mentioned and the non-official status is noted* -- **I could not locate the page that says this**, so it is second-hand. A guessed `note-legali` URL returned 404. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` `Disallow: /*pdf*`, `/*.pdf$`, `/pdf`, `/web/guest/pdf`, `/*printPDF*` plus a few numbered docs and `/c/portal/*`. **HTML docweb pages are not disallowed; every PDF/print variant is.** **ToS: not located** (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **UNKNOWN** (the second-hand "source + non-official note" sentence is not an open licence). |
| Relicense-compatible | **UNKNOWN.** |
| Action | **(d) unknown -> outreach** for the licence of docweb content, interim **(c)** facts + link + original summary. Italian public-sector-information rules (a search extract cited D.Lgs. 33/2013) may make administrative documents reusable by default, but **that is a legal inference not checked here** and not resolved in the project's favour. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `/temi/creative-commons` (read), `/robots.txt` (read), a guessed legal-notes URL (404); WebSearch x2 (extracts only). Source kind: rendered HTML; whole row is substantially an absence finding. |
| Non-English / facts-only | **Italian.** Original English summary + link, generated offline; the Garante's own press releases in English, where they exist, are not a licence basis. |

#### 1C.2 EDPB registers (one-stop-shop decisions and related registers)
*Content class:* register of final one-stop-shop decisions (**1,582 items** at fetch time; filters include
topic "AI", lead authority, GDPR article, outcome), binding decisions, opinions. *Language:* decisions in the **national DPA language**; EDPB summaries in English; UI in 24 EU languages.

| Field | Value |
|---|---|
| Cleanliness score | **2** for EDPB-authored text; **1** for the national decisions the register links |
| License | **Custom EDPB reuse authorisation, not CC.** EDPB Copyright notice, `https://www.edpb.europa.eu/concernant-le-cepd/mentions-legales/copyright_en` (WebFetch 2026-10-02): *"The reuse of any information of this website is authorized for commercial and non-commercial purposes, under the following conditions:"* (1) *"The re-user is obliged to acknowledge the source of the document"*; (2) *"The original meaning or the message of the documents should not be distorted"*; (3) the EDPB *"cannot be held liable for any consequence stemming from the reuse"*. Reuse is defined as *"reproduction of textual data and multimedia items which are the property of the EDPB or of third parties and for which the EDPB holds the rights of use."* Also: users must not alter attributions or *"circumvent technical protections"*. The legal-notice URL tried first returned 404. **The register itself states** that summaries are *"made under the responsibility of the EDPB Secretariat for sole informative purpose"* and that anonymisation practice differs between DPAs. **Brief check:** the notice does not mention CC BY 4.0; the EDPB is **not** under the Commission's CC BY 4.0 blanket, so any assumption that "EU body = CC BY" would be wrong here. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** Drupal-style, `Disallow: /search`, `/search?`, `/admin/` etc.; register pages not disallowed. **ToS:** the notice bars circumventing technical protections but has no automated-access clause (**ABSENCE FINDING, method-suspect**). The register page showed **no export, RSS or API** (**ABSENCE FINDING, method-suspect**; the listing may be generated by JS or hide an export). |
| Redistribute-verbatim | **YES for EDPB-owned text, with conditions (1)-(3).** For national decisions linked from the register the rights holder is the national DPA ("third parties"); the EDPB grant covers them only where it "holds the rights of use" -- **not established per decision**. |
| Relicense-compatible | **CONDITIONAL / UNKNOWN.** Condition (2) (no distortion of meaning) is an extra restriction CC BY 4.0 does not itself impose; whether it can ride along inside a CC BY 4.0 release is a counsel question. Facts + link + original summary avoids the question. |
| Action | **(c) facts + link + original summary** by default; **(d)** clarification email to the EDPB Secretariat on (a) whether the register's decision PDFs may be redistributed and (b) condition (2) vs. CC BY. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the copyright notice, the register page, `robots.txt` (all read); WebSearch to find the notice URL. Source kind: rendered HTML. |
| Non-English / facts-only | Decisions are in **24 possible languages**; English summaries exist at register level. Original English summary + link; offline generation. |

#### 1C.3 Dutch DPA (Autoriteit Persoonsgegevens, AP)
*Content class:* fines and other sanctions, decisions, guidance. *Language:* **Dutch** with English pages.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **Copyright reserved; personal use and quotation with source citation; not an open licence. Now read as primary by the gate (curl, HTTP 200, `-A 'Mozilla/5.0'`, 2026-10-03); no longer extract-only.** The AP copyright page, `https://autoriteitpersoonsgegevens.nl/over-deze-website/copyright`, returned HTTP 403 to this agent's WebFetch. **New clause from the gate:** *"doorleveren aan derden of commercieel verwerken"* (passing on to third parties or commercial processing) requires contacting the AP. The page's Dutch text (verified by red-reviewer via curl, 2026-10-03): *"Er rust copyright op de teksten, foto's en andere afbeeldingen van de Autoriteit Persoonsgegevens (AP) op deze website."* / *"Voor de teksten geldt dat eigen gebruik (inclusief kopiëren) van de informatie is toegestaan. Onder voorwaarde dat u de bron vermeldt, mag u uit teksten van de AP citeren of (grote delen uit) teksten gebruiken."* (English gloss, not page text: personal use including copying is permitted, and quoting or using large parts of texts is allowed if the source is cited); photos and images may not be used; the AP logo is a registered Benelux trademark and no third-party use is permitted. **Refutation of a tempting shortcut:** `rijksoverheid.nl` publishes under CC0 1.0 (`https://www.rijksoverheid.nl/service/copyright`, fetched), but the AP is an independent authority with its own site and its own, narrower copyright page; the CC0 statement was **not** carried over. |
| Scrape-permitted | **robots.txt (gate, curl):** `GPTBot` is `Disallow: /`; `/documenten/*` is explicitly `Allow`ed, while `Disallow: /documenten` (the listing page) is also present. No other access clause reported. |
| Redistribute-verbatim | **NO** (personal use + quotation only; third-party/commercial processing requires contacting AP). |
| Relicense-compatible | **NO.** |
| Action | **(c) facts + link + original summary.** **(d)** optional: ask the AP whether its published sanction decisions are available under any open-government-information reuse regime. (A WebSearch result surfaced a Dutch open-data-directive implementation memorandum; its application to the AP was **not** examined.) |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of AP copyright page and English fines page -> **403**; WebSearch (2 queries) -> extract; WebFetch of rijksoverheid.nl copyright (read, not the AP). Correction: red-reviewer via curl, 2026-10-03, read the copyright page and robots.txt directly; this row's AP clauses are carried from the gate. |
| Non-English / facts-only | **Dutch.** Original English summary + link, offline. |

#### 1C.4 CNIL (France)
*Content class:* sanctions, mises en demeure, guidance, deliberations (published on Legifrance). *Language:* **French** (some English).

| Field | Value |
|---|---|
| Cleanliness score | **1** (site text is ND; the open-data channel is open but a different surface) |
| License | **Split by content type.** CNIL Mentions legales, `https://www.cnil.fr/fr/mentions-legales`, section "Reutilisation des contenus" (WebFetch 2026-10-02, quoted twice with the same result): texts: *"Les textes disponibles sur le site sont des contenus pédagogiques élaborés par la CNIL qui sont mis à disposition selon les termes de licence CC-BY-ND 4.0 FR"*; images/videos: CC-BY-NC-ND 4.0 FR; open data: *"Les données publiques détenues ou produites par la CNIL dans le cadre de l'open data sont mises à disposition par défaut selon les termes de la Licence ouverte"*. Also: *"Seules les délibérations adoptées en séance plénière et publiées sur légifrance sont de nature à engager la CNIL"*. **CC-BY-ND (no derivatives) is incompatible with a CC BY 4.0 relicense and with summaries that adapt the text**. The French open-data channel (decisions on Legifrance/data.gouv under Licence Ouverte) is the compatible route, but **which CNIL decisions are in that dataset was not established by this agent**. **Gate (data.gouv.fr API, 2026-10-03):** the dataset "Sanctions prononcées par la CNIL" exists with licence **`fr-lo` (Licence Ouverte)**, which supports the open-data subset; whether it contains AI-relevant decisions and how complete it is remain unmeasured. |
| Scrape-permitted | **robots.txt (gate, curl, read through line 191):** only Drupal paths. The earlier 60-line read is superseded. **ToS:** no automated-access clause in the Mentions legales extract (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **Site text: NO for our purpose** (ND forbids adaptation; verbatim copies could be redistributed under CC-BY-ND but not relicensed CC BY). **Open-data decisions: YES (Licence Ouverte), unverified.** |
| Relicense-compatible | **Site text: NO. Open-data: YES in principle** (Licence Ouverte 2.0 is attribution-only; see row 1A.6). |
| Action | **(a) for the open-data decision set once verified; (c) for site text.** Needs a follow-up fetch of the CNIL open-data/Legifrance licence page (not done). |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `mentions-legales` (twice), `robots.txt` (truncated to 60 lines by my own request). Source kind: rendered HTML. |
| Non-English / facts-only | **French.** Original English summary + link, offline. |

#### 1C.5 UK ICO (Information Commissioner's Office)
*Content class:* enforcement register (monetary penalties, enforcement notices, reprimands, prosecutions; 18 sector filters), guidance, AI-related actions. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **3** |
| License | **OGL v3.0.** ICO enforcement register page, `https://ico.org.uk/action-weve-taken/enforcement/` (WebFetch 2026-10-02): *"All text content is available under the Open Government Licence v3.0, except where otherwise stated."* with the OGL logo in the footer. Page also warns of date errors in some documents added before 31 December 2024. (An Apify third-party page claiming OGL was not relied on.) `ico.org.uk/global/copyright/` and a website-terms URL returned 404. **Copyright-and-re-use page (found by the gate, footer link, curl, 2026-10-03):** `https://ico.org.uk/global/copyright-and-re-use-of-materials/` -- OGL v3.0 *"except where otherwise stated"*; required attribution string: *"Information Commission's Office, [name and date of publication], licensed under the Open Government Licence"*; no automated-access clause. (The gate's rendering of the body name is "Information Commission's Office"; use the string exactly as the page gives it, and re-read it before writing the notice.) |
| Scrape-permitted | **robots.txt (fetched; `Crawl-delay: 6` confirmed by the gate):** `User-agent: *` `Crawl-delay: 6`, `Disallow: /private`, `/restricted`; `deepcrawl` bot is `Disallow: /`. So **6 s between requests**. **ToS:** the re-use page above has no automated-access clause (the earlier "website-terms page not found" was REFUTED). No export/RSS/API seen on the register page (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **YES**, with OGL attribution; except where otherwise stated (third-party material). |
| Relicense-compatible | **YES** (OGL v3.0 interoperable with CC BY 4.0; see row 1A.1 for the source of that statement). |
| Action | **(a) compatible.** Conditions: honour `Crawl-delay: 6`; per-record OGL notice; the "except where otherwise stated" carve-out must be handled per page; personal-data caution (cross-cutting note). |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the enforcement register page (licence sentence quoted), `robots.txt`, two 404s. Source kind: rendered HTML; the positive licence clause is not method-exposed. |
| Non-English / facts-only | English. |

#### 1C.6 Brazil ANPD (Autoridade Nacional de Protecao de Dados)
*Content class:* sanctions, technical notes, regulatory agenda, AI-related notes. *Language:* **Portuguese**.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **CC BY-ND 3.0 (Unported / "Nao Adaptada") on all portal content.** `https://www.gov.br/anpd/pt-br/acesso-a-informacao` (WebFetch 2026-10-02): *"Todo o conteúdo deste site está publicado sob a licença Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada"*; a WebSearch agrees and notes the same licence on other gov.br portals. |
| Scrape-permitted | **robots.txt (`https://www.gov.br/robots.txt`, fetched, first 60 lines, 2026-10-02):** a shared gov.br file with disallows for specific sub-sites (e.g. `/ebserh`, `/mre`) and Plone view suffixes; no ANPD-specific disallow seen **in the portion read**. **ToS:** none located beyond the licence (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **Verbatim, unmodified: YES under CC BY-ND 3.0 with attribution.** |
| Relicense-compatible | **NO.** ND forbids adaptation, and an ND work cannot be folded into a CC BY 4.0 dataset as if it were ours to license; a summary that adapts the text is arguably a derivative. |
| Action | **(c) facts + link + very short original summary.** Facts (controller, system, date, outcome, fine) are not protected expression; the licence does not reach them. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the ANPD access page and `gov.br/robots.txt`; WebSearch (agreeing). Source kind: rendered HTML. |
| Non-English / facts-only | **Portuguese.** Original English summary + link, offline. |

#### 1C.7 Canada OPC (Office of the Privacy Commissioner)
*Content class:* PIPEDA findings and investigation reports. *Language:* English and French.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **Non-commercial reproduction only.** OPC Website terms and conditions, `https://www.priv.gc.ca/en/privacy-and-transparency-at-the-opc/terms-and-conditions-of-use/` (WebFetch 2026-10-02): *"Unless otherwise specified, you may reproduce the materials in whole or in part and in any format for non-commercial purposes, without charge or further permission, provided you do the following:"* true and accurate reflection of the original; complete title and author; indicate it is a copy of the version on the OPC website. And: *"Unless otherwise specified, you may **not** reproduce materials on this site, in whole or in part, for commercial redistribution without prior written permission from us."* Same family of wording as CCCS/CSE (row 1A.3). |
| Scrape-permitted | **robots.txt: `https://www.priv.gc.ca/robots.txt` -> 404** (**ABSENCE FINDING, method-suspect**). **ToS:** no automated-access clause (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **NO** for a CC BY (commercial-permitting) dataset. |
| Relicense-compatible | **NO.** |
| Action | **(c) facts + link + original summary.** Optionally **(d)** ask the OPC whether findings are available under the Open Government Licence - Canada (many Canadian federal bodies offer it for datasets; **not established for OPC**). |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the OPC terms page (read), robots.txt (404), a guessed URL (404); WebSearch to find the page URL. Source kind: rendered HTML. |
| Non-English / facts-only | Bilingual EN/FR; English originals exist for findings, so no translation needed. |

#### 1C.8 BAILII (British and Irish Legal Information Institute)
*Content class:* UK and Irish judgments and legislation; for AI-litigation, the cases would be found by keyword filtering. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **0** |
| License | **No licence; BAILII expressly cannot authorise copying; bulk use prohibited.** BAILII terms, `https://www.bailii.org/bailii/copyright.html` (WebFetch 2026-10-02, two passes; the tool flagged truncation markers/gaps in the numbered list): *"The copyright in the text of legislation and judgments displayed on BAILII's website may belong to courts, other government bodies, judges, and/or to commercial publishers. BAILII cannot authorize any copying of such material."* Users may *"copy, print and distribute legal materials ... free of charge and without any other authorization from BAILII, provided that BAILII is identified as the source"* (a personal/ordinary-use permission that does not cure the third-party copyright). **Prohibited (s12):** *"incorporating search results or HTML versions of judgments into another website or into the output of a computer program"*; *"storing search results or HTML versions of judgments"*; *"external indexing of documents by web robots or spiders when such use is not authorized"*; *"abusive use ... via automated mechanisms or otherwise, in particular for bulk downloading of documents"*. **Enforcement (s16):** BAILII may block users and *"policy is to block entire domains which use such mechanisms without authorisation."* |
| Scrape-permitted | **NO.** robots.txt (fetched, readable, 2026-10-02): `User-agent: *` **`Disallow: /uk`, `/ew`, `/ie`, `/scot`, `/nie`, `/wales`, `/eu`, `/je`, `/sh`, `/worldlii`** (i.e., the judgment trees) and `User-agent: GPTBot` `Disallow: /`. The ToS prohibition and robots both bar what an ingest pipeline would do. |
| Redistribute-verbatim | **NO.** |
| Relicense-compatible | **NO.** |
| Action | **(c) link only, no pipeline fetch.** Do not crawl. A hand-curated list of citations (case name + neutral citation + BAILII link, entered by a human reading each case) is the most this source supports; the pipeline-engineer must not design a BAILII fetcher. Alternative primary sources (e.g. court-run public repositories) are outside this pass and **not assessed**. (d) is possible (BAILII invites authorisation requests) but the expected value is low. |
| Gate note | s12(a)-(d) and "block entire domains" verbatim (gate, plain curl UA; the page sits behind an Anubis proof-of-work for Mozilla UAs). New: *"BAILII has no objection to links from other websites"*. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `copyright.html` x2, `robots.txt`. Source kind: rendered HTML (clauses positive, robots reliable). The tool-reported truncation means other clauses may exist, but all of them can only narrow the picture further. |
| Non-English / facts-only | English. |

#### 1C.9 CanLII (Canadian Legal Information Institute)
*Content class:* Canadian judgments, tribunal decisions, legislation. *Language:* English and French.

| Field | Value |
|---|---|
| Cleanliness score | **0** |
| License | **Terms of use bar bulk/systematic download; CanLII has sued for it.** The CanLII terms page (`https://www.canlii.org/info/terms.html`) **returned HTTP 403 to WebFetch** (the site blocks the fetch tool; same for `/en/info/terms.html`). The clauses below come from a **WebSearch extract of that page**, not a fetch: the terms prohibit *"bulk or systematic downloading of documents, including via programmatic means or, for greater certainty, the hiring of human resources used to manually download documents"*; incorporating documents into another website in a way that masks their origin; and external indexing by robots not authorised by the robots exclusion file; they state a purpose of balancing *"the public's interest in free and open access to Canadian legal materials with interests of the participants in judicial proceedings ... at risk by the bulk access and use of those materials by commercial and other parties."* Third-party reporting (Law360 Canada, ABA, Dalhousie LibGuide, in the search results) states that CanLII filed a Notice of Claim against **Caseway AI Legal Ltd.** for bulk downloading/scraping in breach of the terms. |
| Scrape-permitted | **NO.** robots.txt (fetched, readable, 2026-10-02): the catch-all **`User-agent: *` -> `Disallow: /`** plus named-bot rules for Googlebot/Bing/GPTBot and others. The CanLII API (documented at `github.com/canlii/API_documentation`) appears to be a metadata-only service: a GitHub issue there asks for full-text support and notes the terms prohibit automated bulk downloading (**issue text read; the API README returned 404, so the API terms were NOT read**). |
| Redistribute-verbatim | **NO.** |
| Relicense-compatible | **NO.** |
| Action | **(c) link only, no pipeline fetch.** Same shape as BAILII: a hand-curated citation list, not a fetcher. (d) not recommended while litigation over exactly this behaviour is on foot. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch `canlii.org/info/terms.html` and `/en/info/terms.html` -> **403**; WebFetch `canlii.org/robots.txt` (read); WebSearch (extracts); WebFetch of the API GitHub issue (read). Source kind: **search-engine extract for the clause text (weak)**, robots.txt reliable. **UNVERIFIED, extract-sourced (gate 2026-10-03: 403 DataDome persists for curl).** The terms clause stays second-hand; only the robots catch-all `User-agent: * Disallow: /` is gate-confirmed, and it alone keeps the score at 0. |
| Non-English / facts-only | Bilingual. |

### 1D. Research and disclosure

#### 1D.1 arXiv cs.CR (filtered to AI-relevant papers)
*Content class:* paper metadata (title, authors, **abstract**, categories, DOI,
dates) and full text/e-prints. *Language:* English (some other).

**Existing curated subset (foreman correction 2026-10-02, counts re-checked).**
`ingest/arxiv_incidents.json` has **123** `source_id` rows (**116** `ARXIV-`,
7 other id forms), hand-curated, no ingest script. No `SOURCE_LICENSES.md` row
names it; section 4 of that file covers only the ten red-team benchmarks.
**Would this pre-row cover it? Only for the metadata half:** title, authors,
identifiers and abstract are CC0, so any of those fields in the 123 rows are
covered. If the curated rows also hold prose that is not arXiv metadata (e.g.
summaries of the full text), that prose is the maintainer's own, not covered
by or needing this row. Whether any row copies full-text passages was **not
checked**. Recorded only; `SOURCE_LICENSES.md` untouched. The proposed
systematic ingest is evaluated below as briefed.

**Correction to the brief's framing.** The brief says "metadata is CC0, but
abstracts and full text carry per-paper licences; separate the two". The first
half is right; **the second half is wrong for abstracts.** arXiv's own definition
puts the abstract inside the CC0 metadata (footnote on the API terms page,
quoted below). The correct split is **metadata including abstract (CC0)** vs
**full text/e-prints (per-paper licence, six options)**. One residual caution
remains (see Relicense-compatible).

| Field | Value |
|---|---|
| Cleanliness score | **3** for descriptive metadata incl. abstract; **0** for full text (not to be taken) |
| License | **Metadata incl. abstract: CC0 1.0.** arXiv API Terms of Use, `https://info.arxiv.org/help/api/tou.html` (WebFetch 2026-10-02): *"You are free to use descriptive metadata about arXiv e-prints under the terms of the Creative Commons Universal (CC0 1.0) Public Domain Declaration."* Footnote 1: *"Descriptive metadata includes information for discovery and identification purposes, and includes fields such as title, abstract, authors, identifiers, and classification terms."* (the footnote was returned by a targeted second fetch). **Full text:** `https://info.arxiv.org/help/license/index.html` lists the author's choices: CC BY 4.0, CC BY-SA 4.0, CC BY-NC-SA 4.0, CC BY-NC-ND 4.0, the arXiv perpetual non-exclusive licence 1.0 (*"limits re-use of any type"*), and CC0. The terms say you may not *"Store and serve arXiv e-prints (PDFs, source files, or other content) from your servers"* without the holder's permission unless the submission carries a permissive licence. |
| Scrape-permitted | **Yes via the sanctioned metadata channels; no for indiscriminate crawling.** `https://info.arxiv.org/help/bulk_data.html`: OAI-PMH (metadata for all articles, updated daily), the arXiv API, RSS, and the Kaggle metadata dataset. API ToU: *"make no more than one request every three seconds, and limit requests to a single connection at a time."* robots.txt (fetched, readable, 2026-10-02): header says *"indiscriminate automated downloads from this site are not permitted"*; default crawl-delay 15 s; `Disallow: /api`, `/e-print`, `/src`, `/search` for `*` (so use `export.arxiv.org` OAI-PMH/API, as the docs direct, not the main site). |
| Redistribute-verbatim | **Metadata + abstract: YES (CC0).** Full text: **NO** unless the specific paper is CC BY/CC0 (not worth a per-paper check). |
| Relicense-compatible | **YES for CC0 metadata** (CC0 imposes nothing). **Residual caution (not a blocker, flagged because ambiguity is not resolved in our favour):** the CC0 dedication is **arXiv's**; the abstract text is the **author's** expression, which authors license to arXiv non-exclusively. arXiv states it in its own terms, and the project already ingests arXiv items (116 `ARXIV-` entries per the E5 audit), but nothing read here shows that authors themselves waived rights in abstract prose. A short original summary written from the paper, with the arXiv id as link, removes the question if the maintainer wants it removed. |
| Action | **(a) compatible for metadata + abstract** (use OAI-PMH/API with the 3 s rule); **never** mirror e-print/PDF. Filtering to AI-relevant cs.CR papers is a pipeline matter. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the API ToU page (x2: summary and a targeted footnote request), license page, bulk-data page, `robots.txt`; WebSearch for corroboration (Kaggle dataset marked CC0). Source kind: rendered HTML, but a positive grant quoted from a primary arXiv page; **not an absence finding**. |
| Non-English / facts-only | English dominant; some papers in other languages. Facts-only not needed for metadata. |

#### 1D.2 HackerOne Hacktivity (disclosed reports)
*Content class:* publicly disclosed vulnerability reports and a Hacktivity feed
(program, severity, bounty, disclosure date, report text). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (verbatim report text not allowed; facts + link not clearly contested) |
| License | **No licence to the public; researchers keep ownership; licences run only to HackerOne and the Customer.** **Superseded terms (gate, curl, 2026-10-03):** `/terms/finder` now redirects to `/terms/community` (Community Member T&C, **effective May 11, 2026**), same substance (licences to HackerOne and the Customer only); the "Finder Terms 2023" below is the prior version and is kept as quoted. `hackerone.com/robots.txt` has only a `Sitemap` line; no scrape clause in 6 documents. HackerOne Finder Terms (2023), `https://www.hackerone.com/terms/finder-2023` (WebFetch 2026-10-02): *"HackerOne does not claim any ownership rights in any Finder Submissions"*; by making a submission available to a Customer the finder grants HackerOne **and** the Customer *"a perpetual, irrevocable, non-exclusive, transferable, sublicensable, worldwide, royalty-free license to use, copy, reproduce, display, modify, adapt, transmit, and distribute copies of that Finder Submission"* (the fuller phrasing is from a WebSearch extract of the Finder Terms; the fetch confirmed the structure: licences to HackerOne and Customers only). **The researcher's copyright in report text therefore survives and no grant reaches third parties.** The Disclosure Guidelines (`https://www.hackerone.com/terms/disclosure-guidelines`): reports can become public (*"the contents of the Report will be made public within 30 days if the Report state is 'Resolved'"* under the Default setting) but the guidelines contain **no reuse or licensing statement** for disclosed reports. The "Terms" URL `https://www.hackerone.com/terms` is the **Customer** T&C and does not cover public visitors. HackerOne AI Terms (`/terms/AI`): bar HackerOne from training general-purpose AI on Customer input; silent on third-party use of disclosed reports. |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (the fetch tool declined to print `www.hackerone.com/robots.txt` and returned only a sitemap pointer for `hackerone.com/robots.txt`). **ToS:** in the three HackerOne terms documents fetched (Customer T&C s3.3, General T&C, Finder Terms) **no explicit anti-scraping clause was found**, but s3.3 does prohibit bypassing *"any measures HackerOne may use to prevent or restrict access to the Services"* (**ABSENCE FINDING, method-suspect; and the Website Terms of Use / Copyright and IP Policy (`/dmca`) were not read**). Third-party scrapers of Hacktivity exist and say they use HackerOne's own web GraphQL API (WebSearch), which is **not** a documented public API and is not evidence of permission. |
| Redistribute-verbatim | **NO** (researcher copyright; no downstream licence). |
| Relicense-compatible | **NO.** |
| Action | **(c) facts + link + original summary** (program, CWE/class, severity, bounty, disclosure date, report URL; summary written by us). **Before any ingest, (d)/shell:** read the HackerOne Website Terms and `robots.txt` raw; consider a written permission request, since "disclosed" is not "licensed". The platform has no documented public bulk API; the pipeline-engineer must not build on the undocumented GraphQL endpoint. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `/terms` (Customer T&C), `/terms/finder-2023`, `/terms/general`, `/terms/disclosure-guidelines`, `/terms/AI`, two `robots.txt` URLs; WebSearch x2. Source kind: rendered HTML; the tool repeatedly summarised rather than quoted, so every clause here should be re-read in raw HTML. |
| Non-English / facts-only | English. |

#### 1D.3 Bugcrowd (disclosed programs/reports)
*Content class:* a limited set of publicly disclosed submissions (disclosure is
**off by default**); program pages. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **0** |
| License | **All website content reserved; submissions confidential by default and assigned or exclusively licensed to Bugcrowd.** Website Terms & Conditions, `https://www.bugcrowd.com/website-terms-and-conditions/` (WebFetch 2026-10-02): *"The copying, redistribution, use or publication by you of any portion of our Website is strictly prohibited."* and the licence to the visitor is *"non-exclusive, non-transferable, revocable ... strictly in accordance with our Legal Terms."* Standard Disclosure Terms, `https://www.bugcrowd.com/resources/hacker-resources/standard-disclosure-terms/`: researchers assign Testing Results to Bugcrowd and, to the extent not assignable, grant Bugcrowd *"irrevocable, paid-up, royalty free, perpetual, exclusive, sub-licensable ... transferable, and worldwide license"* (the exact assignment sentence is from a WebSearch extract of the Terms plus the fetch's quoted fragment); the default is *"ALL SUBMISSIONS ARE CONFIDENTIAL INFORMATION OF THE PROGRAM OWNER UNLESS OTHERWISE STATED"*; moral rights waived. Public Disclosure Policy (`https://docs.bugcrowd.com/researchers/disclosure/disclosure/`): public disclosure needs Program Owner approval; the page names no central public feed and **no reuse or ownership statement for disclosed reports**. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` `Disallow: /*?preview`, `/external_redirect`; sitemaps listed. So robots does not bar crawling. **ToS:** the "no copying, redistribution, use or publication of any portion of our Website" clause bars what ingest would do; no explicit scraping clause was found in the fetch (**ABSENCE FINDING, method-suspect**), which does not matter given the broader prohibition. |
| Redistribute-verbatim | **NO.** |
| Relicense-compatible | **NO.** |
| Action | **(c) link only.** Even facts-extraction is contested by "use ... of any portion of our Website". The disclosed set is small and opt-in per program, so the expected yield does not justify a **(d)** request. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of Website T&C, Standard Disclosure Terms, Public Disclosure doc, `bugcrowd.com/robots.txt`; WebSearch (extract of the Terms). Source kind: rendered HTML. |
| Non-English / facts-only | English. |

#### 1D.4 DEF CON AI Village and Black Hat archives
*Content class:* conference talk titles, abstracts, slides, videos, white papers; AI Village reports and workshop material. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** |
| License | **No open licence found; speakers keep copyright and grant the conference distribution rights.** DEF CON: WebSearch extract of the DEF CON call-for-papers form: speakers grant DEF CON Communications *"permission to duplicate, record and redistribute this presentation ... for educational, on-line, and all other purposes"* and submit presentations/tools *"for publication on the DEF CON media server"*; the media server (`media.defcon.org`, **WebFetch failed with ECONNRESET twice**) is described as open to browse and download. Black Hat: WebSearch extract of CFP terms: speakers grant Black Hat permission *"to record, reproduce, distribute, advertise, and show presentations"*; Black Hat describes its archive as *"provided free of charge as a service to the worldwide computer security community."* `blackhat.com/terms.html` returned **403** to WebFetch. AI Village (`https://aivillage.org/`, fetched): *"no explicit licensing or terms information is stated"* for reports, GRT reports or datasets; its GitHub org is `github.com/aivillage` (repo licences not checked; one guessed repo API returned 404). Result: **a licence to the conference, not to us; "free to download" is not "free to redistribute".** **UNVERIFIED, extract-sourced** (gate 2026-10-03: `defcon.org` connection reset, `blackhat.com/terms` 403, Black Hat robots only `Disallow: /errors/`); gate did read the AI Village GitHub org: repo licences mostly software (MIT/Apache), `awesome-ml-failures` none. |
| Scrape-permitted | **robots.txt: NOT OBTAINED** for `defcon.org` (ECONNRESET), `media.defcon.org` or `blackhat.com` (403). **ToS: not located** (**ABSENCE FINDINGS, method-suspect; the whole row is one**). |
| Redistribute-verbatim | **UNKNOWN -> treated as NO.** |
| Relicense-compatible | **UNKNOWN -> treated as NO.** |
| Action | **(c) facts + link + original summary** (talk title, speaker, year, venue, link to the archive entry; the conference listing of a title is a fact, our summary is ours). Per-repo licences for AI Village GitHub material (structured API licence field) is the cheap next check if any is wanted. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch (ECONNRESET x3, 403 x1, aivillage.org read), WebSearch x2 (extracts of CFP terms). Source kind: **search-engine extracts (weak)**; the CFP forms themselves were not fetched. |
| Non-English / facts-only | English. |

### 1E. Tranche 1 (partially reconstructed)

**The tranche-1 evaluation record of ten sources was not found on any ref,
transcript or artifact** (see PROGRESS.md: the foreman's searches of git,
transcripts, memory and artifacts came back empty). **Only two names are known**
from the user, and only they are evaluated here: huntr and CISA beyond KEV.
The other eight are unknown and are **not** guessed at. These are fresh
pre-rows written 2026-10-03 under the same scale, format, retrieval-method field
and absence rule as section 1, and have **not been through red-reviewer**. Every
absence statement in them is method-suspect and is routed to section 6 (items
31-33).

#### 1E.1 huntr (huntr.com, Protect AI / Palo Alto Networks)
*Content class:* AI/ML bug-bounty platform; disclosed bounty reports at
`huntr.com/bounties/<uuid>` (OSV = open-source vulnerabilities, MFV = model file
vulnerabilities). *Language:* English.

**Already referenced in the corpus.** A Grep of the worktree's
`data/incidents.json` for `huntr\.(com|dev)/bounties` returns **284 distinct bounty URLs (216 huntr.com + 68 huntr.dev; 277 distinct IDs) in 210 of 13,361 entries (gate, 2026-10-03)**: NVD reference URLs already point at huntr bounties. That is URL
references inside NVD-derived records, not ingestion of huntr report text, and
`docs/SOURCE_LICENSES.md` has no huntr row (Grep, case-insensitive: no match).
(Measured by red-reviewer on `data/incidents.json` @ 6d77a194.)

| Field | Value |
|---|---|
| Cleanliness score | **1** (verbatim report text not allowed; facts + link not shown to be contested, but the evidence is thin) |
| License | **No public licence found; contributions are assigned exclusively to Palo Alto Networks.** huntr is now operated under Palo Alto Networks (footer: *"2026 Palo Alto Networks, All rights reserved."*, linking PANW's Terms of Use `https://www.paloaltonetworks.com/legal-notices/terms-of-use` and `/participation-terms`). Huntr Participation Terms, `https://huntr.com/participation-terms` (WebFetch 2026-10-03, **summarising converter, quotes below are its output and need raw-HTML confirmation**): s7.1 (verified by red-reviewer via curl, 2026-10-03, raw HTML, 200, 113,801 B) *"Subject to Section 7.2 below, Contributors assign to Palo Alto Networks, Inc. on a worldwide, perpetual, irrevocable, and exclusive basis all their intellectual property rights (including copyrights and know-how) in and to all and any Contribution and/or related information provided by Contributors … including all rights to reproduce, modify, distribute, commercialize, incorporate into products, and communicate the Contribution and Vulnearability Information for any purpose and to any party."* ("Vulnearability" is the page's own typo); s7.2 *"Contributors retain the non-exclusive right to use the Contribution for non-commercial research and educational purposes."* followed by *"Contributors expressly agree not to disclose any Contribution to any third party."*; s7.3 *"We may share the Contribution with third parties as we deem necessary or desirable."*; s4.4 *"Contributors shall not post the submission on any other platform or medium of communication, unless approved by us in writing."* The tool reported no clause on public reuse of published reports and none on automated access. PANW Terms of Use (`https://www.paloaltonetworks.com/legal-notices/terms-of-use`, linked from the huntr footer as "Terms of Use"; scope "this website"; verified by red-reviewer via curl, 2026-10-03): *"EXCEPT AS EXPRESSLY SPECIFIED, NO PORTION OF THE INFORMATION ON THIS SITE MAY BE REPRODUCED, MODIFIED, PUBLISHED, UPLOADED, POSTED, TRANSMITTED, OR DISTRIBUTED IN ANY FORM, OR BY ANY MEANS, WITHOUT THE PRIOR WRITTEN PERMISSION OF PALO ALTO NETWORKS"*. Crawling is named only inside the forum-conduct list (*"Do not attack, abuse, interfere with … including … monitoring, crawling, spamming, using bots or scripts"*), not as a site-wide automated-access ban. Score 1 (c) still follows (reproduction barred; facts + link not contested). No statement of licence or copyright for published bounty reports appeared on the homepage (**ABSENCE FINDING, method-suspect**). Consequence if the extract is right: the rights holder in a report is PANW, not the reporter, and PANW has granted the public nothing found; the reporter's non-commercial retained right does not pass to us. |
| Scrape-permitted | robots.txt: 404 (curl, 2026-10-03; genuine — no robots file). /guidelines and /terms also genuine 404s. Homepage footer links /participation-terms, /code-of-conduct, /faq and PANW's Terms of Use / Privacy Statement. FAQ (raw Next.js payload): 'Currently, all new reports that we receive go through a co-ordinated disclosure process. This means that the advisory page is only visible to the reporter and maintainers of the vulnerable repository.' No automated-access clause in code of conduct or participation terms. (All verified by red-reviewer via curl, 2026-10-03.) |
| Redistribute-verbatim | **NO** (assigned to PANW; no public grant found). |
| Relicense-compatible | **NO.** |
| Action | **(c) facts + link + original summary** (huntr bounty URL, target repo, CVE id where present, CWE, dates, our own summary). **(d)** the user may ask PANW/huntr whether published bounty pages are reusable; the sensible first read is the **Participation Guidelines and PANW Terms of Use via shell**, which this agent could not reach. Do not scrape huntr.com before the raw-HTML checks (section 6, item 31). The NVD route, which already carries the bounty URL and a CVE-record description under the CVE ToU, is the licence-clean path to the same vulnerabilities. |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (markdown-converting, summarising): `huntr.com/participation-terms` (read, extract), `huntr.com` homepage (footer links), `huntr.com/terms`, `/robots.txt`, `/guidelines` (all 404, method-suspect); WebSearch x1 (titles and summaries only). Local Grep of `data/incidents.json` and `docs/SOURCE_LICENSES.md`. Source kind: **rendered HTML via a summarising converter; weak tier. Not shell-verified.** |
| Non-English / facts-only | English. |

#### 1E.2 CISA beyond KEV (advisories, alerts, joint AI-security guidance)
*Content class:* ICS advisories, cybersecurity advisories and alerts, and joint
guidance such as the "AI Data Security" Cybersecurity Information Sheet (CSI,
released 2025-05-22; co-sealed per a WebSearch extract by NSA, CISA, FBI, ASD's
ACSC, NCSC-NZ and NCSC-UK, marked TLP:CLEAR per that extract). *Language:* English.
KEV itself is already ingested (`docs/SOURCE_LICENSES.md` s2.1) and is out of
scope here.

| Field | Value |
|---|---|
| Cleanliness score | **2 for CISA-authored text** (US federal work, no copyright in the US, but a per-document filter is needed); **1 for co-sealed or third-party material** (rights sit with the other agencies or authors) |
| License | **No CISA-wide licence statement located; the basis is statute.** Works prepared by US federal government officers or employees as part of official duties are not eligible for copyright protection in the US under **17 U.S.C. s105**, verified verbatim by red-reviewer via curl, 2026-10-03 (law.cornell.edu/uscode/text/17/105 and govinfo USCODE-2023-title17-chap1-sec105): *"Copyright protection under this title is not available for any work of the United States Government, but the United States Government is not precluded from receiving and holding copyrights transferred to it by assignment, bequest, or otherwise."* CISA's Linking Policy, `https://www.cisa.gov/linking-policy` (WebFetch 2026-10-03, extract): *"It is a public domain website, so you can link to CISA.gov at no cost and without specific permissions."* This is a **linking** statement, not a content licence, and the same page says *"The Cybersecurity and Infrastructure Security Agency does not and cannot authorize the use of copyrighted materials contained in linked websites."* (extract). The Privacy Policy (`/privacy-policy`) has no copyright, reuse or scraping wording (extract). `https://www.cisa.gov/about/website-policies` is a genuine 404 (curl, 2026-10-03). The real policy pages are linked from `https://www.cisa.gov/site-links` (/terms-use, /notification, /intellectual-property-policy, /linking-policy; verified by red-reviewer via curl, 2026-10-03). Terms of Use: security/authorized-use boilerplate; no copyright, licence or automated-access clause (curl, 0 hits for copyright|public domain|automat|scrap|crawl|robot|bulk). Notification: *"All content on this website or received via email distribution through this website is Traffic Light Protocol (TLP):CLEAR, unless otherwise labeled with a different TLP marking. Recipients may share TLP:CLEAR information without restriction, subject to copyright controls."* Intellectual Property Policy: trademarks/logos only (CISA, CHEMLOCK, CSET, CYBERCORPS, NICCS, NCSWIC, PTS DIALER, SAFECOM); requests to licensing@cisa.dhs.gov. The CSI PDF at media.defense.gov returned 403 twice, so its co-sealer list and TLP marking stay **UNVERIFIED, extract-sourced**; CISA's own resource page says only *"CISA, the National Security Agency, the Federal Bureau of Investigation, and international partners released …"*. **Carve-outs that s105 does not cover:** (1) **co-sealed foreign-agency material** -- US s105 says nothing about NCSC-UK (Crown copyright / OGL, row 1A.1), ASD/ACSC (CC BY 4.0 on some documents, unverified, row 1A.2), or NCSC-NZ (not assessed); the AI Data Security CSI is a joint product, and who authored which parts is not stated in anything read; (2) third-party images, logos, quoted passages and vendor material inside advisories; (3) works by contractors, where copyright may be held; (4) the CSI PDF is hosted at `media.defense.gov` (NSA/DoD), not on CISA's site, so CISA's site policies would not govern it. The CISA alert page for the CSI says the product *"is provided subject to this Notification and this Privacy & Use policy"* (extract, with those policies linked; **not read**). |
| Scrape-permitted | **robots.txt (`https://www.cisa.gov/robots.txt`, fetched, readable, 2026-10-03):** Drupal-style `User-agent: *` with asset allows and disallows for `/core/`, `/profiles/`, `/admin/`, `/search/`, `/user/...`, `/media/oembed`, README files; `PetalBot` is `Disallow: /`. Advisory and alert paths are not disallowed in that file. **ToS:** no automated-access clause found in the Privacy Policy or Linking Policy extracts (**ABSENCE FINDING, method-suspect**); the policy pages linked from /site-links were read by red-reviewer (see License cell). CISA publishes feeds and a KEV JSON, which support access but are not a licence statement. |
| Redistribute-verbatim | **CISA-authored text: YES in the US by statute** (no copyright), with the Linking Policy's no-endorsement caution; **outside the US, not established** (other jurisdictions may protect US government works; not assessed). **Co-sealed material: NO until each agency's terms are applied.** |
| Relicense-compatible | **For CISA-authored text: a CC BY 4.0 dataset may carry public-domain-in-US text, but we cannot assert a licence over it;** the dataset notice should say CISA-authored text is a US government work and not licensed by us. **Co-sealed: depends on each co-sealer (OGL compatible per row 1A.1; ACSC unverified; NCSC-NZ unknown).** |
| Action | **(a) with conditions for CISA-authored advisories/alerts:** per-document provenance flag (author agency, co-seal list); exclude or downgrade to **(c) facts + link + original summary** any document with a co-seal, third-party image or vendor-supplied text; include the statute basis in the NOTICE-DATA row, as `SOURCE_LICENSES.md` s2.1 does for KEV (not re-read here). **(d) not needed for CISA-authored text; for the joint AI guidance, the question is which co-sealers' terms apply.** An AI-relevance filter is a pipeline matter. Do not assert "public domain" for co-sealed documents. |
| Date-checked | 2026-10-03 |
| Retrieval method | WebFetch (summarising): `cisa.gov/linking-policy` (read, extract), `/privacy-policy` (read, no relevant wording), `/robots.txt` (read in full), the CISA alert page for the AI Data Security CSI (read, extract), `/about/website-policies` (genuine 404) and a guessed CISA news URL (404); WebSearch x2 (co-sealer list and TLP marking, extract only). s105 text and the /site-links policy pages verified by red-reviewer via curl, 2026-10-03. Source kind: rendered HTML via a summarising converter (weak for absences) + robots.txt (reliable). **Not shell-verified.** |
| Non-English / facts-only | English. |

---

## 2. Deliberate rejections

Per the brief, not researched exhaustively; each carries enough evidence to
stand. Each rejection can be reopened by a written permission from the source.

### 2.1 CNNVD / CNVD (Chinese national vulnerability databases)
**Reason:** reuse terms were not found and the sites give no automatable access.
A WebSearch (`CNNVD CNVD database terms of use ...`) returned **no formal terms of
use, licence or reuse policy** for either database (**ABSENCE FINDING, method-suspect**:
search only, the sites themselves were not fetched), and secondary analysis
(Bitsight, `https://www.bitsight.com/blog/chinese-vulnerability-database-analysis-cnvd-cnnvd`)
reports that both require account creation and login, generate files
server-side on demand so that *"all requests require user interaction"*, and are
in Mandarin. With no licence, no stable machine channel and a Mandarin-only
corpus, the project would be taking unlicensed text through an unautomatable
path. Provenance concerns raised by third parties (e.g. Recorded Future via
CyberScoop, title only, not read) are **not** relied on. **Evidence kind:** search
extracts. **UNVERIFIED, extract-sourced (gate 2026-10-03):** CNVD answers with a
521 JS cookie wall, CNNVD with an SPA shell; neither terms page was read by the
gate. The rejection rests on the absence of a licence plus login/interaction
requirements, both secondary.

### 2.2 Snyk Vulnerability Database
**Reason:** restrictive commercial terms on the data. A WebSearch extract of the
Snyk Terms of Service (April 8, 2020 PDF,
`https://s3.amazonaws.com/EULA/36811992-19af-484d-9598-40c2b324a8d6-Snyk-EULA1.pdf`;
the PDF itself could not be read by the converter) says users must not
*"redistribute or transfer the Services, Platform, Documentation or Service Data to any third party or make any part of the Services, Documentation or Service Data available to be accessed, in whole or in part, by any third party."*
The feeds are licensed *"separately as standalone products"* (Snyk docs
extract). **Caveat:** that is a 2020 **customer** agreement; the terms of the
public `security.snyk.io` site were **not** read. The rejection stands on the
published rule that Service Data may not be passed to third parties, which a
CC BY 4.0 release would do; public GitHub/OSV-covered advisories are already
reachable through GHSA/OSV (SOURCE_LICENSES 2.3, 2.4). **Gate 2026-10-03:** the 2020
clause is verbatim in the PDF; the current `snyk.io` ToS makes Service Data
Snyk Confidential Information, which strengthens the rejection.

### 2.3 VulDB
**Reason:** non-commercial, share-alike licence. WebSearch extract of
`https://vuldb.com/kb/terms` (the page itself returned **HTTP 403** to
WebFetch): free users *"are not allowed to use the service in a commercial
context and have to attribute VulDB as source as defined by the license CC BY-NC-SA 4.0"*,
and the public-access licence forbids use of the data *"within a commercial
project"*; commercial use needs a paid subscription. CC BY-NC-SA is
incompatible with a CC BY 4.0 dataset on both counts (NC and SA). **Evidence kind:**
search extract. **UNVERIFIED, extract-sourced:** the gate also got 403 from
`vuldb.com/kb/terms` (2026-10-03).

### 2.4 News aggregators and newsletters (class)
**Reason:** OECD AIM already supplies news-derived coverage, so a second
aggregator adds dedupe load, not coverage. Local confirmation:
`docs/SOURCE_LICENSES.md` s1.5 records that the AIM event metadata is
*"LLM-generated (OpenAI's o3-mini) from the top three articles of each event,
selected from different news outlets"*, and the E5 audit counts **4,160 OECD
entries**. A newsletter/aggregator would re-describe the same news events,
and carries its own third-party-copyright exposure on top of the unresolved OECD
description question (E21, SOURCE_LICENSES s1.5). Discovery-only use (a human or
model-free feed of leads, no text kept) is not an ingest and is out of scope here.

---

## 3. Dated watch items

### W1. EU AI Act Article 73 serious-incident reporting (dated 2026-10-02)
**What exists today -- and a correction to the scope record's framing.** The
scope record speaks of a "serious-incident register" whose "existence, access
and reuse terms" are to be watched. **Article 73 as read does not create a public
register.** (`https://ai-act-law.eu/article/73/` and `https://artificialintelligenceact.eu/article/73/`,
fetched 2026-10-02, convenience copies of the Regulation, **not EUR-Lex**.)
Providers of high-risk AI systems report serious incidents to the **market
surveillance authorities of the Member State where the incident occurred**
(15 days standard; 2 days for widespread infringement or serious injury to health; 10 days
for death). Paragraph 11, verbatim: *"National competent authorities shall immediately notify the Commission of any serious incident, whether or not they have taken action on it, in accordance with Article 20 of Regulation (EU) 2019/1020."*
Neither fetched copy shows any provision making reports public, any Commission
register or database of incident reports, or any reuse terms. The only
database in the Act that the copies mention is the **EU database of high-risk AI
systems (Article 71)**, which is a registry of *systems*, not incidents. A
Digital-Omnibus-era change adds that providers of high-risk systems under the AI
Office's competence report to the AI Office (search extract), still not a public feed.
**Expected timing.** Article 73 reporting duties were to bite from **2 August 2026**
alongside the high-risk obligations. The **Digital Omnibus on AI** postponed the
high-risk obligations: **Annex III stand-alone systems to 2 December 2027, Annex I
products to 2 August 2028** (Gibson Dunn, fetched; political agreement 6-7 May
2026; WebSearch extracts state Parliament endorsed 16 June 2026, Council adopted
29 June 2026 and the Regulation entered into force 27 July 2026 -- **those
adoption/entry-into-force dates come from search extracts, not a fetched
Official Journal text**). That Article 73 reporting follows the same new dates is
an **inference, not read**. Commission **draft** guidance and reporting template
on Article 73 were issued 26 September 2025 (consultation to 7 November 2025);
a WebSearch extract says the final template had **not** been published as of
this search (**ABSENCE FINDING, method-suspect**).
**Conclusion for the evaluation:** there is **nothing to ingest today** and no
indication a public feed will exist; reports go to national authorities and the
Commission, with confidentiality presumably under Regulation (EU) 2019/1020
(**not read**). Revisit on: final Commission guidance publication, 2 December 2027,
and any implementing act on publication of incident statistics. Do not describe
Art. 73 as a source in any public claim.

**Update 2026-10-03 (gate):** Art. 73 para 11 confirmed verbatim against the
official OJ text (Publications Office Cellar; original 2024 text, not
consolidated; EUR-Lex returned 202/WAF): 0 hits for publish / public / database /
register. The Digital Omnibus OJ dates remain **unverified** (not fetched).

### W2. EUVD API maturation (dated 2026-10-02)

**Update 2026-10-03 (red-reviewer gate 1; the bullets below are preserved as
written 2026-10-02 and are superseded where this block disagrees; do not
regenerate them as current).** The official API docs are **readable**:
`apidoc.md` in `github.com/enisaeu/euvd-docs-public` (pushed 2026-09-18). It
documents the endpoints, states they **"require no authentication"**, caps
responses at **8 or 100 records per request** depending on endpoint, and shows
**no versioning and no changelog**. So "official docs unreadable / third-party
docs only" is refuted, and "Rate limits and authentication: not documented" is
refuted for authentication (none) and partly for limits (per-request caps).
The docs-repo LICENSE bars reuse of the docs (row 1B.2); do not copy its text.
The "Terms: not found" bullet is also superseded by the ENISA Legal Notice
(row 1B.2).
- **Stability.** The UI at `https://euvd.enisa.europa.eu/` and `/apidoc` returned
  only *"The European Vulnerability Database application could not be loaded"*
  (a single-page-app error shell, 2026-10-02, tool limit; cannot distinguish
  outage from JS requirement). The JSON API at `https://euvdservices.enisa.europa.eu/api/`
  **responded normally** to `lastvulnerabilities` (4 records, EUVD-2026-91381
  among them) and `search?text=machine learning&size=2` (`items`, `total: 472`;
  fields `id, enisaUuid, description, datePublished, dateUpdated, baseScore,
  baseScoreVersion, baseScoreVector, references, aliases, assigner, epss,
  exploitedSince, enisaIdProduct, enisaIdVendor`). Note `lastvulnerabilities`
  lacked `exploitedSince`/`enisaIdProduct` in the first record while `search`
  returned them: **the schema varies by endpoint.**
- **Versioning.** The URL carries no version segment. A WebSearch extract says the
  official API documentation was last updated **9 June 2025**; no changelog or
  deprecation policy was found (**ABSENCE FINDING, method-suspect**; the docs page is an SPA).
- **Bulk export.** Third-party docs (`https://github.com/bytew0lf/EUVD-API`, which
  states it is **not** official) list `/api/dump/cve-euvd-mapping` (CSV) and
  `/api/kev/dump` (JSON), daily at 07:00 UTC, and `/api/search` with `size` 1-100.
  The mapping dump **exists** (fetch aborted: *"maxContentLength size of 10485760
  exceeded"*, i.e. over 10 MB); other claims are second-hand. Latest/exploited/critical
  endpoints are capped at 8 records (third-party doc).
- **Rate limits and authentication.** Not documented in anything read.
- **Terms.** Not found (see row 1B.2; the ENISA IPR policy does not name EUVD).
- **Revisit when:** official `/apidoc` is readable and carries a licence/terms
  statement and a version/changelog; ENISA answers the reuse question; the
  `lastvulnerabilities` vs `search` schema differences are documented.

---

## 4. Volume / overlap / ingest shape / corpus fit / reconciliation / non-English (pipeline-engineer)

**Author of sections 4-5:** pipeline-engineer, 2026-10-03. Evidence (commands, raw
counts, ID lists): `docs/specs/source-expansion-estimates-evidence-2026-10-03.md`
and `.json` (same directory, dated records). Nothing here changes sections 1-3.
No ingest code exists or is proposed before a user ruling.

**Labels.** **[M]** = measured on 2026-10-03 (command in the evidence file).
**[E]** = estimated (reasoning given). "Proxy count" = a regex over descriptions,
spot-read but not a label. The corpus is `data/incidents.json` at `e2b1c988`: 13,361
entries, `generated` 2026-09-18, of which 6,986 carry a `CVE-` source id.

### 4.0 Findings that cut across candidates

1. **The corpus's own CVE refresh is stale, independent of any new source.** [M]
   The newest CVE-sourced entries are dated 2026-07 (15 entries; 2026-06 has 504).
   EUVD lists 537 proxy-AI CVEs published since 2026-07-01 and the corpus holds 22
   of them. That ~515-entry gap is a refresh backlog, not a new-source gain, and
   is **excluded** from every "new" figure below unless stated.
2. **The CVE-keyed sources are one universe seen through different doors.** [M]
   All 3,873 EUVD items returned by 26 AI queries carry a CVE alias; none is
   EUVD-only. huntr, EUVD, JVN, WID, ANSSI and cvelistV5 all key on CVE, so their
   AI-relevant sets overlap each other almost completely; only the ones that add
   fields beyond CVE text (EPSS, EUVD id, AVID taxonomy, huntr bounty URL) add
   information.
3. **The existing keyword sweep misses a measurable slice.** [M] In the window
   2024-01..2026-06 (clear of finding 1), 25% of EUVD's proxy-AI CVEs (302 of
   1,213) are not in the corpus, and 63% of huntr's (233 of 368). Spot-read items
   (12 + 15 + 14 sampled) are AI frameworks and apps (anything-llm, vLLM, Triton,
   gradio, lunary, dify, ragflow, MLflow). This is the WS4-T4 allowlist argument
   in numbers, and it means the new-CVE gain is real but modest.
4. **Accretion is already visible.** [M] 17 corpus entries (18 CVE ids), all
   `status: active` with no rejection marker, correspond to CVEs that NVD now marks
   `Rejected`, found by looking only at huntr's CNA slice (111 of 2,496 = 4.4% of
   that CNA's CVEs are Rejected). Every CVE-keyed source needs WS4-T2.
5. **`ingest/common.py` cannot reach several sources as it stands** [M]: see 4.1.
   It also does not parse `Crawl-delay` (the string never appears in the module),
   so ICO (6), BSI (10) and arXiv's main host (15) must be passed as
   `min_interval=` by the caller or the module extended.

### 4.1 Reachability through `ingest/common.py` (measured with `robots_allowed()` and live fetches)

| Result | Hosts / paths | Consequence |
|---|---|---|
| Refused: explicit Disallow | `export.arxiv.org` (`User-agent: * / Disallow: /`, read directly); `cert.ssi.gouv.fr/fiche/` and `/pdf`; `static.data.gouv.fr/resources/` (`Disallow: /resources`: the CNIL open-data CSVs live there); `autoriteitpersoonsgegevens.nl/documenten` | arXiv must use `oaipmh.arxiv.org` (allowed), not the API the ToU names. CNIL's open-data subset cannot be downloaded by the pipeline. The AP result is stdlib `robotparser` taking the **first** matching rule in file order, where the AP file lists `Disallow: /documenten` and `Allow: /documenten/*`; RFC 9309 would take the longest match. A parser fix, not a robots change, is the issue. |
| Refused: robots unverifiable, fail-closed | `www.cyber.gov.au` (read timed out), `defcon.org`, `media.defcon.org` (connection closed) | ACSC and DEF CON cannot be fetched. Neither qualifies for `ROBOTS_UNVERIFIABLE_ALLOWLIST` without dated evidence that every client is refused. |
| Allowed by allowlist, content 403 | `www.cisa.gov`: robots 403 (allowlisted), then `/cybersecurity-advisories/all.xml`, `/ics-advisories.xml`, `/news.xml` all HTTP 403 to the project User-Agent | CISA "beyond KEV" HTML/RSS is unreachable as identified. The structured route is `github.com/cisagov/CSAF`. |
| Allowed, usable | `oaipmh.arxiv.org`, `rss.arxiv.org`, NVD, `api.github.com`, `raw.githubusercontent.com`, GitHub release assets and `objects.githubusercontent.com`, `euvdservices.enisa.europa.eu`, NCSC, CCCS, `cert.ssi.gouv.fr` (avis, alerte), `jvndb.jvn.jp`, `jvn.jp`, `wid.cert-bund.de`, `cert.europa.eu`, `ico.org.uk`, `www.edpb.europa.eu`, `www.cnil.fr`, `www.garanteprivacy.it`, `www.gov.br`, `www.priv.gc.ca`, `hackerone.com`, `huntr.com`, `www.blackhat.com`, `aivillage.org`, `www.data.gouv.fr` (API only) | Reachable does not mean usable: see per-row shape (huntr, ICO). |
| Non-HTTP egress | `git clone` of `CVEProject/cvelistV5` (API-reported size 3.0 GB) | Must be registered in `docs/INGESTION_CONDUCT.md` (invariant 5 as amended D22). Avoidable: the HTTP release assets (daily baseline zip 619 MB; hourly delta zips 0.15-1.1 MB) go through `common.py`. |

### 4.2 Candidate rows

Each row: **Volume** (backlog + per-year rate, how, filter) · **Overlap** (new /
conflict / dedupe key) · **Shape** · **Fit** · **Reconciliation** · **Maint.**
(structure score 0-3: 3 = fixed machine format, 0 = scraped and undocumented) ·
**Non-English** where it applies. "Dedupe key" refers to `scripts/merge_and_dedupe.py`
(CVE, then reference URL, then fuzzy title).

#### cvelistV5 (1B.3, licence 2) 
- **Volume.** Universe = CVE records matching the WS4-T4 allowlist. No bulk
  AI count exists in the repo, so the measure is indirect: in the window
  2024-01..2026-06, EUVD's 26 AI queries return 1,213 proxy-AI CVEs, of which 302
  are not in the corpus [M]. That is a **lower bound** (26 query terms, not an
  allowlist). Steady state ~120 new/yr (302 over 30 months) plus the ~515 refresh
  backlog of finding 1 [E for the rate, M for the counts]. Filter: allowlist on
  CNA `affected[].vendor/product/packageName/collectionURL` (what the keyword
  sweep cannot see), keyword as candidate feeder only (WS4-T4).
- **Overlap.** ~75% already in the corpus (911 of 1,213 [M], window). Dedupe key:
  CVE. Conflicts: the corpus holds one severity per CVE; CNA-supplied CVSS in
  cvelistV5 vs NVD-derived values will differ for some fraction (**not measured**;
  [E] 10-30%, to be measured on the first fetch). Each divergence goes to
  `conflicts` per WS3.
- **Shape.** Bulk dump: baseline zip daily, hourly delta zips, CVE JSON 5, no auth,
  no rate limit beyond GitHub's; HTTP through `common.py` (host checks pass [M]).
- **Fit.** Vulnerabilities (the corpus's second-largest category, 5,784 of 13,361).
- **Reconciliation.** Best of the lot: `cveMetadata.state` (PUBLISHED/REJECTED)
  and `dateUpdated` are in every record; deltas hourly. Rejection churn [M, huntr
  slice]: 4.4% of a CNA's CVEs end Rejected; 17 corpus entries already stale.
- **Maint.** Structure 3. The CVE JSON 5 schema is versioned. Cost is size, not
  fragility. **Precondition:** the allowlist (WS4-T4) and the CVE ToU notice,
  which is missing from `NOTICE-DATA` today (section 1B.3).

#### huntr (1E.1; licence 1 for huntr.com, 2 for the CVE-route subset)
- **Volume.** **Measured via the CVE route, because the site has no structured
  channel.** NVD `sourceIdentifier=security@huntr.dev` returns 2,496 CVEs [M]; 111
  Rejected; 410 of the rest match the AI proxy regex, 368 in the window. By
  publication year (proxy): 2023: 28, 2024: 154, 2025: 172, 2026 to 3 Oct: 53 [M],
  so the rate is falling (~70/yr at the 2026 pace [E]). Filter: CNA = huntr plus
  the allowlist.
- **Overlap.** The gate's corpus figure reproduces: 277 distinct bounty IDs in 210
  of 13,361 entries [M] (216 huntr.com URLs; the huntr.dev count is 61 or 67
  depending on URL-form regex, 68 at the gate, immaterial). Through the CNA path:
  254 corpus entries are huntr-CNA CVEs (3.6% of the 6,986 CVE entries). Of the
  368 window AI CVEs, 135 are in the corpus and **233 (63%) are not** [M]. The
  two paths agree in direction (237 of the 277 corpus bounty IDs appear in the CNA
  set's NVD references; 2,381 of 2,496 huntr CVEs carry a bounty URL). Dedupe key:
  CVE. Conflicts: none expected (same NVD text).
- **Shape.** **huntr.com cannot be ingested as a source.** [M] `/sitemap.xml` and
  `/bounties` are 404; a bounty page returns HTTP 200, 75 KB, a generic title and
  **none** of the CVE, CWE, severity, status or repository fields. The page is a
  client-rendered shell and the FAQ says new reports are visible only to the
  reporter and maintainers (section 1E.1). The structured channel is the CNA's CVE
  records: this row is a **filter inside cvelistV5** (`assigner = security@huntr.dev`
  / `@huntr_ai`), keeping the bounty URL as a reference.
- **Fit.** Vulnerabilities in AI/ML open-source software.
- **Reconciliation.** As cvelistV5. huntr-specific: the CNA's 2026 rate drop
  (53 vs 172) after the Palo Alto acquisition means a flat extrapolation overstates.
- **Maint.** Structure 3 via CVE records; 0 for huntr.com itself.

#### AVID (1B.5, licence 2)
- **Volume.** [M] `avidml/avid-db` holds **1,790** distinct IDs: 40 vulnerabilities
  (2022: 13, 2023: 27) and 1,750 reports (2022: 5, 2023: 7, 2025: 25, **2026:
  1,713**, max R1714, matching the site's count at the gate). The repo is
  **current**, which closes the lag question in the 1B.5 caveat (ii).
  **Per-year rate is not estimable:** 25 reports in 2025 against 1,713 in 2026 is
  a bulk import, not a rate. Filter: none needed (the database is the filter).
- **Overlap.** The corpus has 110 AVID ids (109 in `source_ids`); 109 are in the
  repo and one, `AVID-2023-V025`, is **not** (an upstream removal or renumber:
  a retraction case already in the corpus). 1,681 repo IDs are absent from the
  corpus. A 40-report random sample of the 2026 reports [M, n=40] found 29 (73%)
  are CVE entries ("classof: CVE Entry", description copied from the CNA text),
  of which 14 (48%; 16 counting any mention) are already in the corpus as CVE
  entries; 11 (27%) are AVID-native ("LLM Evaluation", "Third-party Report").
  Net-new entries therefore ≈ 1,681 × (0.27 + 0.73 × 0.5) ≈ **1,070 (range 800-1,300,
  n=40, wide)** [E]; the other ~600 merge into existing CVE entries as extra
  `source_ids` and add AVID's SEP taxonomy. Dedupe key: AVID id, then CVE. Conflicts:
  CNA text vs corpus text (same CVE) are expected to be identical; taxonomy
  fields are additive.
- **Shape.** Git repo of JSON files, fixed schema (`data_version 0.3.3`),
  MIT, no auth. Walk the tree API (one call) and fetch changed files through
  `raw.githubusercontent.com`. A raw fetch per file at 3 s is ~85 min for the
  backlog, so use the `git` route (register it) or the repo tarball.
- **Fit.** Mixed: the CVE-derived majority are vulnerabilities; the native
  minority are incident/evaluation reports.
- **Reconciliation.** Repo history is the change log; ID-set diff catches removals
  (1 in 109 corpus ids already). No tombstones, so absence must be handled as
  `status` change, never deletion.
- **Maint.** Structure 3. Risk: AVID's 2026 import is automated, so its quality
  and cadence can change without notice. Needs the missing `SOURCE_LICENSES` row
  and the WS7-T1 sentence (1B.5).

#### arXiv cs.CR metadata (1D.1, licence 3 for metadata and abstract)
- **Volume.** [M, sampled] OAI-PMH, set `cs:cs:CR`, the first full week of June:
  papers created that month in the week's datestamps were 105 (2023), 133 (2024),
  107 (2025), 190 (2026); proxy-AI share 41%, 51%, 62%, 61%; proxy "AI attack"
  share (AI terms plus attack/vulnerability terms) 25%, 25%, 35%, 31%. Annualising
  single weeks is [E] and noisy: ~2,200 (2023) rising to ~6,000 (2026) proxy-AI
  papers/yr, ~1,400-3,100 attack-flavoured.
  The corpus's curated criterion (a paper demonstrating a concrete attack) is
  far narrower: 252 `research` entries exist today. [E] 60-100/yr after human
  triage; an unfiltered attack-flavoured ingest would add ~1,400-3,100/yr and swamp every statistic.
- **Overlap.** [M] 2 of 535 sampled papers (0.4%) are already in the corpus
  (149 arXiv ids total). Dedupe key: reference URL (arXiv abs id). Conflicts: none
  (no shared fields beyond id and title).
- **Shape.** **The API named in the ToU is unreachable through `common.py`**
  (`export.arxiv.org` robots `Disallow: /`, read directly). The reachable
  sanctioned channels are OAI-PMH (`oaipmh.arxiv.org`, allowed) and RSS
  (`rss.arxiv.org`, allowed). One response page covered a full week (630 KB, no
  resumption token). Keep the 3 s floor; the main host's Crawl-delay 15 applies
  only to `arxiv.org`, which we would not fetch.
- **Fit.** Capabilities / research (the existing `research` and
  `research-demonstrated` categories).
- **Reconciliation.** OAI-PMH carries deletion headers, so tombstones exist. Churn
  is high: [M] in the weeks sampled, 47% (2025) and 58% (2026) of the records
  touched were papers created in earlier months (version replacements and metadata
  edits). Detection by datestamp is easy; deciding whether a revision changes the
  entry's claim is not.
- **Maint.** Structure 3 (OAI-PMH is a fixed standard); the cost is the selection
  filter, which is a curation problem.

#### EUVD (1B.2, licence 1)
- **Volume.** Same universe as cvelistV5. [M] 1,213 proxy-AI items in the
  window (302 not in the corpus), 537 since 2026-07.
- **Overlap.** **~100% CVE-duplicate of cvelistV5**: 3,873 of 3,873 items carry a
  CVE alias, 0 EUVD-only [M]. Its unique content is the EUVD id, `epss` (present on
  all items), `exploitedSince` (5 of 3,873), ENISA's vendor/product mapping and the
  `assigner`. Dedupe key: CVE.
- **Shape.** JSON API, no auth, no versioning, 100 records/page. Quirks [M]: dates
  are locale strings with a narrow no-break space ("Aug 17, 2026, 9:16:10 PM"),
  the schema differs by endpoint, and the text search is fuzzy (872 hits for
  "vector database"). Rate limit undocumented; 3 s spacing was accepted.
- **Fit.** Vulnerabilities (as enrichment).
- **Reconciliation.** `dateUpdated` is a poor change signal: 58% of proxy-AI
  items published before 2026-04 (765 of 1,312) were updated more than 30 days
  after publication [M]. Detection must hash fields, not trust the date. No
  tombstone seen.
- **Maint.** Structure 2. Licence is (d) and unresolved; fields would be
  facts + link only.

#### ANSSI / CERT-FR (1A.6, licence 3; French)
- **Volume.** [M] 0 AI titles among 80 feed items (40 AVI + 40 ALE). Serial numbers
  give the rate: `CERTFR-2026-AVI-1257` on 2 Oct (≈1,650/yr annualised) and
  `ALE-011` (~14/yr). AI-relevant: [E] 5-15/yr, nearly all CVE-keyed vendor
  advisories (vendor products; none seen in the sample). Backlog [E] ~30-60.
- **Overlap.** CVE-keyed, so ~100% dup of cvelistV5 once that is in; new content is
  a French summary. Dedupe key: CVE, then URL.
- **Shape.** RSS (40 items, rolling) plus per-advisory HTML under `/avis/` and
  `/alerte/`; `/pdf` and `/fiche/` are disallowed (refused by `common.py`). The
  feed body is not valid UTF-8 (undecodable bytes, probably Latin-1) [M]: a
  parser must not assume UTF-8.
- **Fit.** Vulnerabilities (advisories).
- **Reconciliation.** Advisories are revised in place ("mise à jour") under the
  same id; detection by content hash. Retractions rare.
- **Maint.** Structure 2 (feed + HTML). **Non-English: French.** Summaries are
  original English, generated offline, committed under `data/summaries/`, never
  by a model call in `make build`; they count as original prose (WS0-T3).
  Volume [E] 5-15/yr.

#### BSI / WID (1A.5, licence 1; German)
- **Volume.** [M] CSAF white index: 13,874 advisories; by id year 2022: 1,208,
  2023: 3,055, 2024: 2,953, 2025: 2,940, 2026 to 3 Oct: 3,718. Feed sample: 2 of
  250 items mention "AI" (OpenShift AI). AI-relevant [E] ~1% = ~30/yr, all
  CVE-keyed.
- **Overlap.** Dup of cvelistV5; BSI's own contribution is its severity rating and
  German summary. Dedupe key: CVE.
- **Shape.** CSAF 2.0: `provider-metadata.json`, ROLIE feeds, `index.txt` (416 KB),
  one JSON per advisory; no auth. **Crawl-delay 10** must be passed as
  `min_interval=10`. Licence-wise a CSAF file has TLP:WHITE and no licence (1A.5),
  so the shape is facts + link.
- **Fit.** Vulnerabilities. **Reconciliation.** CSAF `tracking.revision_history`
  and `current_release_date` are explicit; heavy `[UPDATE]` churn (250 feed items in
  ~2 days).
- **Maint.** Structure 3. **Non-English: German.** Because CVE text is English,
  translation is largely unnecessary; any BSI-specific summary is written offline
  from the vendor advisory (1A.5). Volume [E] 0-30/yr.

#### JVN (1A.8, licence 1; Japanese and English)
- **Volume.** [M] MyJVN `feed=hnd` by `datePublic` year: 198 (2023), 207 (2024),
  179 (2025) JVN notes in total. Keyword counts: "machine learning" 0 / 5 / 4,
  "artificial intelligence" 2 / 0 / 0, "AI" 0 / 0 / 2, LLM / TensorFlow / PyTorch 0.
  Backlog [E] ~15, rate ~5/yr. JVN iPedia (the larger NVD-style mirror) could not
  be counted (`feed=sec` is invalid; the valid feed names were not found).
- **Overlap.** CVE-keyed; ~100% dup of cvelistV5 once ingested. The unique content
  is Japan-specific vendor coordination.
- **Shape.** Documented XML/RSS API, no auth, robots 404. Quirks [M]: errors come
  back as HTTP 200 with an `errCd`, the status schema version varies between
  calls (3.2 and 3.3), and a wrong parameter family silently returns `totalRes=0`.
- **Fit.** Vulnerabilities. **Reconciliation.** JVNDB ids carry revisions; low
  churn. **Maint.** Structure 3, quirky. **Non-English:** English text exists
  upstream, so no translation. Licence (d): outreach first.

#### CISA beyond KEV (1E.2, licence 2 for CISA-authored)
- **Volume.** [M] The structured route is `github.com/cisagov/CSAF`: OT/ICS
  advisories 422 (2024), 506 (2025), 416 (2026 to 2 Oct); IT advisories 7 / 32 /
  60. These are ICS and enterprise-product advisories; AI-relevance was **not
  measured** (the feeds are 403 and counting needs per-file reads). AI-relevant
  [E] ~0-5/yr from CSAF, plus joint AI-security guidance documents (~3-6/yr,
  backlog ~10-15, from the section 1E.2 description, not counted).
- **Overlap.** The corpus has 1 line referencing `cisa.gov` [M]; KEV is separate.
  Dedupe key: CVE for advisories, URL for guidance.
- **Shape.** HTML/RSS on `cisa.gov` returns 403 to the project User-Agent (see 4.1);
  CSAF via GitHub works. Guidance PDFs sit on `media.defense.gov` (403 at the gate).
- **Fit.** Mostly guidance (not a corpus category) plus a few product advisories.
- **Reconciliation.** CSAF has revision history; low churn.
- **Maint.** Structure 3 for CSAF, 0 for guidance. Per-document provenance flag
  (co-seals) is required by 1E.2.

#### UK NCSC (1A.1, licence 3)
- **Volume.** [M] sitemap 2,638 URLs; 70 have an AI token in the slug (lower
  bound). RSS: 20 items over 9 Jul to 28 Sep 2026 (≈90/yr), 3 AI titles
  → ~13 AI items/yr [E]. Filter: slug/title/body AI terms, then human keep only
  items documenting an incident or vulnerability (1 of the 25 AI titles seen is
  incident-like: the statement on incidents from frontier-AI evaluations).
- **Overlap.** 0 corpus references to `ncsc.gov.uk` [M]; all new. No ID to
  conflict on. Dedupe key: URL.
- **Shape.** RSS + sitemap + HTML; robots 404; no auth.
- **Fit.** Guidance and commentary: **not** a corpus category; a few
  incident-like items.
- **Reconciliation.** Pages are edited in place; the RSS carries no modified date;
  detection by hash. Churn low.
- **Maint.** Structure 2. English.

#### ICO enforcement (1C.5, licence 3)
- **Volume.** [E] AI-relevant enforcement: ~3-8/yr, backlog ~15. Not countable:
  [M] the register page's static HTML (50 KB) has a "Loading..." container and no
  result links; the data comes from an undocumented XHR.
- **Overlap.** Likely partial with AIAAIC/OECD for headline cases [E] ~50%. Dedupe
  key: URL, then fuzzy title (route ambiguous merges to the review queue,
  WS4-T5).
- **Shape.** HTML shell over an XHR, no feed. Crawl-delay 6 (`min_interval=6`).
- **Fit.** Real-world incidents (regulatory action). **Reconciliation.** Documents
  carry date errors before 31 Dec 2024 (the page says so); notices are
  occasionally amended.
- **Maint.** Structure 1. English.

#### ENISA reports (1A.4, licence 2 for CC BY 4.0 reports)
- **Volume.** [M] sitemap 2,946 URLs, 594 under `/publications/`, 11 with an AI
  token (lower bound). Rate [E] 2-4/yr.
- **Overlap.** 0 corpus references [M]. Dedupe key: URL.
- **Shape.** Sitemap + HTML + PDFs; robots allows. `lastmod` is unreliable (9 of 11
  show 2024).
- **Fit.** Reports/guidance, not incidents or vulnerabilities. **Reconciliation.**
  Static documents; low. **Maint.** Structure 2. English.

#### EDPB register (1C.2, licence 1 for the shape we would use)
- **Volume.** [M] 1,582 decisions (144 pages × 11); the "AI and technology" topic
  filter ends at pager index 4, so ≤55 decisions. That topic also holds
  biometrics and profiling; AI-incident-relevant [E] ~10-15, rate ~2-4/yr.
- **Overlap.** 1 corpus reference to `edpb.europa.eu` [M]. Dedupe key: URL, then
  title.
- **Shape.** Server-rendered Drupal HTML, topic facet, pager; no API/RSS seen; no
  Crawl-delay stated.
- **Fit.** Real-world incidents (enforcement). **Reconciliation.** Decisions are
  final once registered; low. **Maint.** Structure 2.
- **Non-English.** The register gives English summaries; the decisions are in
  national languages and are not needed (facts + link + original summary from the
  English text). Translation volume [E] ~0.

#### CCCS Canada (1A.3, licence 1)
- **Volume.** [M] RSS 50 items in 9 days (≈1,800/yr, vendor advisories), 0 AI
  titles. Backlog/rate [E] ≤10 and ≤3/yr.
- **Overlap.** 0 corpus references [M]. Dedupe key: URL. Not CVE-keyed in the feed.
- **Shape.** RSS/Atom endpoint (`/api/cccs/rss/v1/get`), robots 404. **Fit.** Advisories mirroring
  vendors; weak. **Reconciliation.** Frequent updates. **Maint.** Structure 3.
  Bilingual: English originals exist, no translation. Non-commercial terms mean
  facts + link only.

#### Garante (1C.1, licence 1; Italian)
- **Volume.** [E] (no structured channel reached) AI-relevant provvedimenti
  ~8-12/yr, backlog ~40-60 since 2020 (ChatGPT/OpenAI, Replika, DeepSeek, Clothoff,
  Clearview, delivery-platform algorithms are the kind of case). Overlap with
  AIAAIC/OECD for headline cases ~50-70% [E].
- **Shape.** HTML docweb; every PDF/print variant is robots-disallowed; reachable
  through `common.py` [M] but no feed measured. **Fit.** Real-world incidents.
  **Reconciliation.** Decisions are rarely amended; appeals appear as new
  documents. **Maint.** Structure 1.
- **Non-English: Italian.** Original English summaries, offline, committed;
  [E] ~10-15 per year, ~50 for the backlog.

#### Black Hat / DEF CON / AI Village (1D.4, licence 1, unverified)
- **Volume.** [E] ~30-50 AI-related talks/yr across both. Not countable: `defcon.org`
  and `media.defcon.org` are unreadable through `common.py` (fail-closed) [M];
  Black Hat's robots permit its schedule pages [M] but no page was counted.
- **Overlap.** 2 corpus references to `blackhat.com` [M]. **Shape.** HTML per-year
  schedule pages; DEF CON side unreachable. **Fit.** Capabilities (talks), not
  incidents or vulnerabilities. **Reconciliation.** Static per year.
  **Maint.** Structure 1. English.

#### Candidates with a volume of roughly zero or no reachable channel (still not licence-blocked)
- **ACSC (1A.2, scored 1 provisional per D39).** Not measurable: `cyber.gov.au` robots
  read timed out, so `common.py` fails closed [M]. Volume [E] ≤10 AI documents
  (AI guidance is co-published with NCSC/CISA/NSA, which are counted there).
  Non-commercial concerns do not apply; the licence is unverified.
- **JPCERT/CC (1A.7, licence 1; Japanese).** [M] English RDF: 6 items over
  10 Jun to 9 Sep 2026, all Microsoft/Adobe patch alerts, 0 AI. The Japanese RDF
  (36 items) was fetched but not analysed. AI-relevant [E] ≤2/yr; translation
  volume ≤2/yr. Content is largely duplicated by JVN.
- **CERT-EU (1A.10, licence 1).** [M] 10 advisories 30 Apr to 27 Sep 2026, 0 AI.
  The section-1 row already notes none AI-related. [E] ~0/yr.
- **Dutch AP (1C.3, licence 1; Dutch).** [E] ~2-4 AI-relevant decisions/yr,
  backlog ~10 (a Clearview fine, an Uber/algorithm case are of the type). Reachability:
  `common.py` refuses `/documenten` because of rule order (4.1) [M]. Translation
  ~2-4/yr. English pages exist.
- **CNIL (1C.4, licence 1; French; open-data subset (a)).** The licence-clean dataset
  "Sanctions prononcées par la CNIL" (`fr-lo`) was last updated 2025-05-05 and its
  sanctions CSV 2024-10-01 [M]; the CSV host is robots-disallowed [M]. AI-relevant
  [E] ~1-3/yr. Translation ~2-4/yr (including AI guidance).
- **Brazil ANPD (1C.6, licence 1; Portuguese).** [E] ~1-3/yr, backlog <10.
  Translation ~1-3/yr. CC BY-ND bars adaptation, so facts + link only.
- **Canada OPC (1C.7, licence 1; bilingual).** [E] ~1-2/yr (joint investigations),
  backlog ~5; English originals exist.
- **HackerOne (1D.2, licence 1).** [E] no documented public API; the only bulk
  route is the undocumented GraphQL endpoint that section 1D.2 says not to build
  on; 17 corpus references to `hackerone.com` [M]. Volume of AI-program
  disclosures not estimable without it.
- **huntr.com bounty pages directly** are covered under huntr above (no fields in
  the HTML).

### 4.3 Scored 0 in section 1: listed by name only

**Not estimated until written permission exists:** CSA / SingCERT (1A.9), VulnCheck
KEV (1B.4), BAILII (1C.8), CanLII (1C.9), Bugcrowd (1D.3), and arXiv full text
(1D.1, the 0 half; the metadata half is estimated above). Section 1 agrees with
the brief on all six: each is scored 0 there.

### 4.4 Non-English summary

Every translated or summarised sentence is **original prose generated offline and
committed** (for example under `data/summaries/`), per the WS0-T3 determinism
rule; **no model call enters the `make build` path**, and a translated summary
is treated as a derivative that needs its own provenance record (the AIAAIC D2
caution cited in 1A.5). [E] annual volume if every non-English row were adopted:
Garante 10-15, ANSSI 5-15, CNIL 2-4, AP 2-4, ANPD 1-3, JPCERT ≤2, BSI 0-30 (mostly
unnecessary: CVE text is English), JVN and EDPB and CCCS and OPC 0 (English exists)
→ **~20-45 summaries/yr excluding BSI (up to ~75 with it), plus a backlog of ~100-120**. None of this volume is
measured; it is the reason the non-English rows rank low.

---

## 5. Ranking and waves

### 5.1 Method

Ranking = licence cleanliness × volume × corpus fit × inverse maintenance cost
(the scope record, discipline 4). Each factor 0-3; product 0-81; a 0 on any factor
zeroes the candidate, deliberately (an unreachable or empty source is not worth a
wave).

| Factor | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| **L** licence cleanliness | section-1 score of the **subset actually ingested** (0-3) | | | |
| **V** new-entry volume after dedupe against the current corpus | ≥1,000 backlog or ≥200/yr | 100-999 or 20-199/yr | 10-99 or 3-19/yr | <10 and <3/yr |
| **F** corpus fit | squarely a current category with direct field mapping (CVE-keyed vulnerability, AI-vuln record) | fits a current category with partial mapping (enforcement action, curated research) | mostly guidance/capability content the corpus does not hold | no fit |
| **M** inverse maintenance cost | structured, fixed-format, reaches `common.py` cleanly | structured with quirks, or feed + stable HTML | scraped HTML/XHR, or needs a `common.py` change | cannot go through `common.py`, or only an undocumented endpoint |

ACSC is scored L=1 (provisional, D39) and every row whose section-1 status is
"unverifiable" is flagged **(U)**. V uses the numbers of section 4; it excludes the
515-entry refresh backlog of finding 4.0-1.

### 5.2 Factor table, sorted by product

| Rank | Candidate | L | V | F | M | Product | Note |
|---|---|---|---|---|---|---|---|
| 1 | **AVID** | 2 | 3 | 3 | 3 | **54** | V=3 rests on ~1,070 net-new [E, n=40]; at V=2 it ties cvelistV5 (36) |
| 2 | **cvelistV5** | 2 | 2 | 3 | 3 | **36** | needs allowlist + CVE ToU notice |
| 2 | huntr (CVE route) | 2 | 2 | 3 | 3 | 36 | **a filter inside cvelistV5**, not additive |
| 4 | **arXiv cs.CR metadata** | 3 | 2 | 2 | 2 | **24** | V depends on human triage; unfiltered it swamps the corpus |
| 5 | EUVD | 1 | 2 | 3 | 2 | 12 | ~100% CVE-dup of cvelistV5; licence (d) |
| 5 | ANSSI / CERT-FR | 3 | 1 | 2 | 2 | 12 | clean licence, almost no AI content |
| 7 | BSI / WID (U, WID-specific terms) | 1 | 1 | 3 | 3 | 9 | CVE-dup; facts + link |
| 8 | NCSC | 3 | 1 | 1 | 2 | 6 | guidance, not a corpus category |
| 8 | JVN | 1 | 1 | 3 | 2 | 6 | ~5 AI/yr; licence (d) |
| 8 | ICO | 3 | 1 | 2 | 1 | 6 | register is an XHR; Crawl-delay 6 |
| 11 | ENISA reports | 2 | 1 | 1 | 2 | 4 | |
| 11 | EDPB register | 1 | 1 | 2 | 2 | 4 | ≤55 decisions in AI topic |
| 13 | CCCS | 1 | 1 | 1 | 3 | 3 | non-commercial; 0 AI in 50-item sample |
| 14 | Garante | 1 | 1 | 2 | 1 | 2 | Italian; outreach |
| 14 | CISA beyond KEV | 2 | 1 | 1 | 1 | 2 | cisa.gov feeds 403; ICS-heavy |
| 14 | Black Hat / DEF CON (U) | 1 | 2 | 1 | 1 | 2 | DEF CON unreachable |
| 17 | ACSC (L=1, provisional, U) | 1 | 1 | 1 | 0 | 0 | unreachable via `common.py` |
| 17 | JPCERT/CC | 1 | 0 | 1 | 3 | 0 | no AI items; duplicated by JVN |
| 17 | CERT-EU | 1 | 0 | 1 | 3 | 0 | no AI items |
| 17 | Dutch AP | 1 | 1 | 2 | 0 | 0 | refused by `common.py` rule order |
| 17 | CNIL | 1 | 1 | 2 | 0 | 0 | open-data host robots-disallowed |
| 17 | Brazil ANPD | 1 | 0 | 2 | 1 | 0 | |
| 17 | Canada OPC | 1 | 0 | 2 | 1 | 0 | |
| 17 | HackerOne | 1 | 1 | 3 | 0 | 0 | undocumented API only |
| 17 | huntr.com bounty pages (direct) | 1 | 1 | 3 | 0 | 0 | HTML has no report fields |
| — | CSA, VulnCheck KEV, BAILII, CanLII, Bugcrowd, arXiv full text | 0 | — | — | — | not estimated | permission first |

**Sensitivity.** The top two do not move under a one-step change of any single
factor of AVID or cvelistV5 (AVID at L=1 gives 27, still above arXiv's 24; at V=2
it ties cvelistV5 at 36). Everything below rank 4 is at most 12, so ordering there
is within estimation error, and no source below arXiv adds more than ~50 entries/yr
by these measurements.

### 5.3 Waves

**Wave 1: AVID + cvelistV5 (with huntr as a filter inside it).** Why together:
they are the only candidates that add hundreds of entries on a clean licence, and
they share a dedupe key (CVE), so ingesting them together lets AVID's CVE-derived
reports merge into the CVE entries instead of racing them. huntr belongs here as a
CNA filter, not as a source of its own, because huntr.com serves no report fields.
**Needs before ingest:** (AVID) the missing `SOURCE_LICENSES.md` row and MIT notice
for the 109 existing AVID entries, the WS7-T1 neighbour sentence, a decision on the
repo `git` route (register in `INGESTION_CONDUCT.md`) vs tarball; (cvelistV5) the
CVE ToU notice in `NOTICE-DATA` (a gap that exists today), the WS4-T4 allowlist as
the filter (without it the ingest is unfiltered), WS4-T2 reconciliation handling
`REJECTED` before the first merge (17 stale entries already); (huntr) a WS0-T1 row
stating that only CVE-record text is taken and the bounty URL kept as a link.
No outreach needed. **Expected yield:** AVID ~1,070 net-new entries (800-1,300,
n=40 [E]) plus ~600 enrichments of existing CVE entries; cvelistV5 ~300 backlog in
the 30-month window [M, lower bound] plus ~120/yr [E], inside which huntr is 233
backlog [M] and ~40-70/yr [E]. **First-year total ≈ 1,200-1,600 net-new entries
(about +9-12% on 13,361)**; this is less than the sum of the parts because AVID's
CVE-keyed new reports and cvelistV5's new CVEs are largely the same universe
(not double counted), and it excludes the ~515 refresh backlog that a plain CVE
refresh would add anyway.

**Wave 2: arXiv cs.CR (OAI-PMH) + EUVD as enrichment only.** Why: arXiv is the only
remaining source with both a CC0 licence and a large gap (99.6% new), but its yield
is a curation decision, not a pipeline one. EUVD is dominated by cvelistV5 for
coverage and is worth it only for EPSS and EUVD ids on CVE entries that wave 1
creates, so it follows wave 1 and the ENISA reply. **Needs:** (arXiv) a
`SOURCE_LICENSES.md` row, a triage rule for "demonstrates a concrete attack" that is
deterministic in the build (keyword/heuristic candidate feeder plus a committed
human-approved list, as WS4-T4 does for CVEs), and a decision whether a `common.py`
exception for the API is wanted (not recommended: OAI-PMH works unmodified);
(EUVD) outreach to ENISA, which the user sends, on whether the API data is within
the Legal Notice's reproduction clause. **Expected yield:** arXiv 60-100 curated
entries/yr [E] (backlog a few hundred if the curated list is back-filled); EUVD 0 new
CVE entries [M]; enrichment (EPSS present on 3,873 of 3,873 items) of up to the
6,986 CVE-keyed corpus entries.

**Wave 3 (optional, low yield): regulators, ICO + EDPB (+ Garante).** Why: the only
incident-category additions, and the only place where the corpus gains something
AIID/AIAAIC/OECD may not carry. They are small (≤55 EDPB decisions in the AI topic;
ICO and Garante single digits per year), expensive per entry (HTML/XHR, Crawl-delay
6, Italian translation) and partially duplicated by AIAAIC/OECD. **Needs:** ICO
OGL notice and the XHR endpoint documented or the source hand-curated; EDPB facts +
link rule for national decisions; Garante outreach and an offline-translation
step. **Expected yield:** ~25-40 entries in the first year, ~10-15/yr after [E].
Recommendation: hand-curate rather than build parsers unless the user wants
the regulatory axis.

**Hold:** ANSSI, BSI, JVN, NCSC, ENISA, CCCS (low AI content or not a corpus
category), JPCERT, CERT-EU, AP, CNIL, ANPD, OPC, HackerOne (no AI content or no
reachable channel), ACSC (unverified, unreachable), CISA beyond KEV (403, ICS-heavy),
Black Hat / DEF CON.

### 5.4 Testing the prior

| Prior | What the measurement says |
|---|---|
| **Wave 1 = CISA (beyond KEV) + huntr + EUVD** | **Mostly not supported.** *CISA beyond KEV*: product 2. `cisa.gov` feeds return 403 to the project User-Agent; the structured route is the ICS-heavy CSAF repo; AI-relevant content is a handful of guidance documents a year; licence 2 with a co-seal carve-out. *huntr*: **supported as a target, not as a source.** 233 AI-relevant CVEs missing (63% of its window set) is the strongest single-CNA gap found, but huntr.com serves no report fields (HTTP 200 shell, 0 of 6 field markers), so it is a CNA filter inside cvelistV5. *EUVD*: not supported for wave one. 3,873 of 3,873 items are CVE-duplicates of cvelistV5, the licence is (d) with an outreach prerequisite, and the date format and fuzzy search are maintenance costs; its unique fields (EPSS, EUVD id) are enrichment. **Missing from the prior and ranked first:** AVID (already 109 entries, repo current at 1,790 IDs) and cvelistV5. |
| **Wave 2 = NCSC / ACSC / CCCS** | **Not supported.** NCSC is cleanly licensed (3) but publishes guidance and commentary, not incidents or vulnerabilities (product 6; 1 incident-like item in the 25 AI titles seen). **CCCS is non-commercial only**, so facts + link at best, with 0 AI titles in a 50-item sample (product 3). **ACSC cannot be reached through `common.py`** (robots read times out, fail-closed) and its licence is an unverified extract (product 0). The "permissive trio" is one permissive source with the wrong content, one restricted, one unreachable. |

### 5.5 Cross-tranche caveat

Tranche 1 was ten sources, but **only huntr and CISA beyond KEV are known** (the
record was lost; scope record 2026-10-02). This ranking therefore covers **29 of the
~37 candidates** (27 tranche 2 + 2 tranche 1; the other 8 tranche-1 names are
unknown). **It must not be presented as the final cross-tranche ranking**, and any
of the eight could outrank the 54 and 36 above.

### 5.6 Decision record: rejections and watch items (one line each, from sections 2-3)

- **Rejected:** CNNVD / CNVD (no reuse terms found, login-gated, Mandarin; extract-sourced, unverifiable); Snyk (Service Data may not be passed to third parties; current ToS makes it Confidential Information); VulDB (CC BY-NC-SA 4.0, incompatible; extract-sourced, 403); news aggregators and newsletters (OECD AIM already supplies news-derived coverage; discovery-only use is not an ingest).
- **Watch:** EU AI Act Article 73 (no public register in the text; revisit on final Commission guidance, 2 Dec 2027 and any publication act; Digital Omnibus OJ dates unverified); EUVD API maturation (docs `apidoc.md` is readable, no auth, 8/100 per request, no versioning or changelog; revisit when terms and a changelog exist; this section found the date format and per-endpoint schema differences, which add to that list).

---

## 6. Absence findings for shell verification

Gate 2 (2026-10-03): items 31–33 run by red-reviewer; results folded into 1E.1/1E.2 per D39.

**Status after gate 1 (2026-10-03).** Items 1-30 were run by red-reviewer
(`docs/audits/source-expansion-tranche2-gate1-verdict-2026-10-03.md`, RESULTS
table). Refuted: 4, 7, 8, 9 (new clause), 11, 20, and the web-text half of 10;
item 13 false-fired and is replaced below; 2, 24, 28, 29 (CNVD/CNNVD/VulDB) and
the WID half of 5 remain **unverifiable**. The commands below are kept as the
record of what was run; the verdict is the record of results. Items 31-33 were run by red-reviewer at gate 2 (2026-10-03); results folded into 1E.1/1E.2 per D39.

Every item below rests on WebFetch (a summarising converter) or WebSearch, so
each is method-suspect. Run against **raw HTML** (`curl -sL`, add
`-A 'Mozilla/5.0'` where noted). "Confirms" means the original finding stands;
"refutes" means the row must be revised. A 403/timeout that persists means the
clause stays search-extract-sourced and the row is not upgraded.

1. **NCSC (1A.1).**
   `curl -sIL https://www.ncsc.gov.uk/robots.txt | head -1` -> 404 confirms no robots.txt; 200 refutes (read it).
   `curl -sL https://www.ncsc.gov.uk/section/about-this-website/terms-and-conditions | grep -ioE 'automat|scrap|crawl|robot'` -> no output confirms no access clause; any hit refutes (read it).
2. **ACSC (1A.2; fetches timed out).**
   `curl -sL https://www.cyber.gov.au/about-us/copyright | grep -io 'creative commons attribution[^<]*'` -> CC BY 4.0 International text confirms the licence; other wording refutes.
   `curl -sL https://www.cyber.gov.au/robots.txt` -> read for Disallow on advisories.
3. **CCCS (1A.3).**
   `curl -sL https://www.cyber.gc.ca/robots.txt`.
   `curl -sL https://cse-cst.gc.ca/en/corporate-information/terms-and-conditions | grep -ioE 'automat|scrap|robot|crawl'` -> no output confirms.
   `curl -sL https://www.cyber.gc.ca/en | grep -io 'href="[^"]*terms[^"]*"'` -> a cyber.gc.ca-specific terms page refutes "CSE terms only".
4. **ENISA website text (1A.4).**
   `curl -sL https://www.enisa.europa.eu/ | grep -ioE 'href="[^"]*(legal|copyright|terms)[^"]*"'`, then grep each target for `CC BY|Creative Commons|reuse` -> a page-level CC BY 4.0 grant refutes "web text not covered".
5. **BSI / WID (1A.5).**
   `curl -sL https://wid.cert-bund.de/robots.txt`; `curl -sL https://www.bsi.bund.de/robots.txt`.
   `curl -sL https://wid.cert-bund.de/ | grep -io 'href="[^"]*nutzung[^"]*"'` then read that page.
   Fetch one CSAF advisory (via `https://wid.cert-bund.de/portal/wid/csaf/info`) and `jq .document.distribution` -> a licence/TLP:WHITE reuse statement refutes "no open licence".
6. **ANSSI (1A.6).** `curl -sL https://www.cert.ssi.gouv.fr/mentions-legales/ | grep -ioE 'automat|scrap|robot|moissonn'` -> no output confirms no access clause.
7. **JPCERT (1A.7; whole row is absence).**
   `curl -sIL https://www.jpcert.or.jp/robots.txt | head -1`.
   `for u in https://www.jpcert.or.jp/ https://www.jpcert.or.jp/english/; do curl -sL $u | grep -io 'href="[^"]*"' | grep -iE 'term|site|polic|copyright|rule'; done` -> a terms/copyright link refutes "no ToS located"; read it.
8. **JVN / iPedia (1A.8).**
   `curl -sIL https://jvndb.jvn.jp/robots.txt | head -1`.
   `curl -sL https://jvndb.jvn.jp/nav/jvndb_faq.html | grep -iE -A6 '引用|転載|再配布'` and `curl -sL https://jvndb.jvn.jp/en/nav/jvndb_faq.html | grep -i -A6 'redistribut'` -> a link to the "separately provided guidelines" refutes "guidelines not located"; follow it. **Result (gate): REFUTED the other way** -- the quoted sentence is not on the page; actual Q5-1/Q5-2 are in row 1A.8 and both phrases are withdrawn.
9. **CSA (1A.9).**
   `curl -sL https://www.csa.gov.sg/terms-of-use/ | grep -ioE 'automat|robot|scrap|spider'` -> no output confirms.
   `curl -sL https://www.csa.gov.sg/terms-of-use/ | grep -io 'Any claim relating to use of The Website[^<]*'` -> shows whether the page really cuts off.
10. **CERT-EU (1A.10).**
    `curl -sL https://cert.europa.eu/legal-notice | grep -ioE 'cert-eu[^<]{0,150}|creative commons[^<]{0,100}'` -> CERT-EU named in the CC BY grant resolves the contradiction toward CC BY.
    `curl -sL https://cert.europa.eu/publications/security-advisories/ | grep -io 'all rights reserved'` -> a hit confirms the footer conflict.
11. **EUVD (1B.2).**
    `curl -sL https://euvd.enisa.europa.eu/ | grep -ioE 'legal|terms|licen[cs]e|copyright'`; grep the SPA's linked JS bundles for `terms` and `licen`.
    `curl -sI https://euvdservices.enisa.europa.eu/api/lastvulnerabilities` -> look for licence/Link/terms headers.
12. **cvelistV5 repo licence (1B.3).** `curl -s https://api.github.com/repos/CVEProject/cvelistV5/license` -> 404 confirms `license: null`.
13. **CVE ToU notice absent from our repo (1B.3). Check replaced after the gate.**
    The original grep **false-fired**: the original pattern ('Copyright.*MITRE|CVE.*Terms of Use') hits NOTICE-DATA:41 and .reuse/dep5:17 — both the MITRE ATLAS Apache notice, not the CVE ToU (literal "MITRE Corporation" hits only .reuse/dep5:17; NOTICE-DATA line 41 is "The MITRE" and line 42 "Corporation"; verified by red-reviewer, 2026-10-03). Replacement:
    `git grep -nE 'Common Vulnerabilities and Exposures|hereby grants you a perpetual|cve\.org/Legal' -- NOTICE-DATA .reuse/dep5 README.md docs/SOURCE_LICENSES.md docs/DATASHEET.md` -> **no output confirms the compliance gap** (gate result 2026-10-03: no notice-file hits); a hit in a notice file that actually reproduces the CVE ToU grant refutes it. Input that would make this check fail (i.e. show a false "gap"): a notice that carries the CVE grant in paraphrase without any of the three strings. Read `NOTICE-DATA` once by eye to exclude that.
14. **VulnCheck (1B.4).**
    `curl -sL https://www.vulncheck.com/service-terms | grep -oiE '[^.]*(open source or similar license|artificial intelligence model)[^.]*'` -> both sentences present confirm the restrictive clauses (a miss refutes my quotes).
    `curl -sL https://docs.vulncheck.com/community/vulncheck-kev/faq | grep -ioE '[^.]*(redistribut|commercial|rate limit|token)[^.]*'` -> the FAQ fetch was truncated; any hit adds terms.
15. **AVID site licence (1B.5).** `curl -sL https://avidml.org/database/ | grep -ioE 'licen[cs]e|creative commons|CC[- ]BY'` -> no output confirms; a hit refutes (read it).
16. **Garante (1C.1).** `curl -sL https://www.garanteprivacy.it/ | grep -io 'href="[^"]*"' | grep -iE 'note|legal|copyright|licen'` -> a note-legali page refutes "ToS not located".
17. **EDPB (1C.2).**
    `curl -sL 'https://www.edpb.europa.eu/registers/register-of-final-one-stop-shop-decisions_en' | grep -ioE 'rss|export|csv|\.xml|/api'` -> a hit refutes "no export/API".
    `curl -sL https://www.edpb.europa.eu/concernant-le-cepd/mentions-legales/copyright_en | grep -ioE 'automat|scrap|robot'` -> no output confirms.
18. **Dutch AP (1C.3; 403 to fetch tool).**
    `curl -sL -A 'Mozilla/5.0' https://autoriteitpersoonsgegevens.nl/over-deze-website/copyright | grep -io 'copyright[^<]*'` -> must match the search-extract wording (personal use + quoting, source cited); `creative commons`/CC0 refutes.
    `curl -sL -A 'Mozilla/5.0' https://autoriteitpersoonsgegevens.nl/robots.txt`.
19. **CNIL (1C.4).**
    `curl -sL https://www.cnil.fr/robots.txt | sed -n '60,200p'` (I read only 60 lines).
    `curl -sL https://www.cnil.fr/fr/mentions-legales | grep -ioE 'robot|scrap|automat'` -> no output confirms.
    Also locate the CNIL open-data/Legifrance licence page for decisions (not yet fetched).
20. **ICO (1C.5).** `curl -sL https://ico.org.uk/ | grep -ioE 'href="[^"]*(terms|copyright|legal)[^"]*"'` -> find the website-terms page; read for automated-access wording.
21. **ANPD (1C.6).** `curl -s https://www.gov.br/robots.txt | grep -n -i anpd` -> no output confirms no ANPD-specific disallow.
22. **OPC (1C.7).** `curl -sI https://www.priv.gc.ca/robots.txt | head -1` -> 404 confirms.
23. **BAILII (1C.8).** `curl -sL https://www.bailii.org/bailii/copyright.html | grep -ioE '[^.]*(bulk|abusive|robot|spider|storing)[^.]*'` -> must reproduce s12(a)-(d); a miss refutes my quotes.
24. **CanLII (1C.9; 403 to fetch tool).** `curl -sL -A 'Mozilla/5.0' https://www.canlii.org/en/info/terms.html | grep -ioE '[^.]*(bulk|systematic|programmatic|robot)[^.]*'` -> must reproduce "bulk or systematic downloading ... programmatic means"; a persisting 403 leaves the clause second-hand.
25. **arXiv (1D.1; positive, for completeness).** `curl -sL https://info.arxiv.org/help/api/tou.html | grep -io 'Descriptive metadata includes[^<]*'` -> must list "abstract"; absence refutes my correction of the brief.
26. **HackerOne (1D.2).**
    `curl -sL https://hackerone.com/robots.txt`; `curl -sL https://www.hackerone.com/robots.txt`.
    `for u in terms/general terms/finder-2023 terms/disclosure-guidelines dmca; do curl -sL https://www.hackerone.com/$u | grep -ioE '[^.]*(scrap|crawl|automated|bot)[^.]*'; done` -> a hit refutes "no explicit anti-scraping clause". Also locate the website terms of use (not read).
27. **Bugcrowd (1D.3).**
    `curl -sL https://www.bugcrowd.com/website-terms-and-conditions/ | grep -ioE '[^.]*(scrap|crawl|robot|automated|spider)[^.]*'`.
    `curl -sL https://www.bugcrowd.com/resources/hacker-resources/standard-disclosure-terms/ | grep -io 'exclusive, sub-licensable[^.]*'` -> must show the assignment/licence sentence.
28. **DEF CON / Black Hat / AI Village (1D.4).**
    `curl -sL https://defcon.org/robots.txt`; `curl -sL https://media.defcon.org/robots.txt`; `curl -sL https://www.blackhat.com/robots.txt`.
    `curl -sL https://defcon.org/html/defcon-34/dc-34-cfp-form.html | grep -io 'permission to duplicate[^<]*'` -> must match the quoted grant.
    `curl -s https://api.github.com/orgs/aivillage/repos | grep -E '"name"|spdx_id'` -> structured licence per repo.
29. **Rejections (section 2).**
    `curl -sIL https://www.cnvd.org.cn/` and `https://www.cnnvd.org.cn/`, then grep pages for `使用条款|版权|声明` -> a terms page refutes "no terms found".
    `curl -sL -A 'Mozilla/5.0' https://vuldb.com/kb/terms | grep -io 'CC BY-NC-SA[^<]*'` -> must match.
    Snyk: download the EULA PDF (URL in 2.2), `pdftotext <file> - | grep -i -B1 -A2 'Service Data'`; and `curl -sL https://security.snyk.io/ | grep -ioE 'href="[^"]*(terms|licen)[^"]*"'` for the public-site terms.
30. **Watch items (section 3).**
    Art. 73 text from EUR-Lex: `curl -sL 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689' | grep -n -iE 'publicly available|serious incident'` -> any publication/register provision in Art. 73 refutes "no public register".
    Digital Omnibus Official Journal text: confirm the 27 July 2026 entry into force and the 2 Dec 2027 / 2 Aug 2028 dates, and whether Art. 73 timing moved.
    `curl -sL https://euvd.enisa.europa.eu/apidoc` raw, for a version/changelog/terms statement. (Superseded: the gate read `apidoc.md` in the official docs repo.)

New in the 2026-10-03 rework (tranche 1, section 1E; **not yet run**). Each states the input that would make the check fail, i.e. return the same output whether or not the thing is there.

31. **huntr (1E.1).** WebFetch gave 404 for `/terms`, `/guidelines` and `/robots.txt`; gate 2 (curl, 2026-10-03) found all three genuine 404s (the WebSearch listing of `/guidelines` is stale).
    `for u in robots.txt guidelines terms participation-terms code-of-conduct; do printf '%s ' $u; curl -s -o /dev/null -w '%{http_code}\n' -A 'Mozilla/5.0' https://huntr.com/$u; done` -> a 200 on `guidelines` refutes "404"; read it.
    `curl -sL -A 'Mozilla/5.0' https://huntr.com/participation-terms | sed -e 's/<[^>]*>/ /g' | grep -ioE '[^.]*(assign|exclusive|licen[cs]e|scrap|crawl|automated|publish)[^.]*'` -> must reproduce s7.1/7.2/7.3/4.4 as quoted; a miss means the summarising converter misquoted them.
    `curl -sL -A 'Mozilla/5.0' https://huntr.com/guidelines | sed -e 's/<[^>]*>/ /g' | grep -ioE '[^.]*(public|publish|disclos|licen[cs]e|copyright)[^.]*'` for a reuse statement on published reports.
    `curl -sL https://www.paloaltonetworks.com/legal-notices/terms-of-use | sed -e 's/<[^>]*>/ /g' | grep -ioE '[^.]*(scrap|crawl|robot|automated|reproduc)[^.]*'` (the PANW terms were not read).
    **Input that would make this fail silently:** a Cloudflare/JS challenge returning HTTP 200 with a challenge page; check the body contains "Participation" before trusting any grep. If the pages are an SPA shell, fetch the JS bundle as the gate did for EUVD and grep it.
32. **CISA beyond KEV (1E.2).** WebFetch 404'd `/about/website-policies`; gate 2 (curl, 2026-10-03) found it a genuine 404, with the real policy pages linked from `/site-links`.
    `curl -sIL https://www.cisa.gov/about/website-policies | head -3`; then `curl -sL https://www.cisa.gov/ | grep -ioE 'href="[^"]*(polic|copyright|reuse|terms)[^"]*"'` to find the real policies page, and grep each for `copyright|public domain|105|third.party|reus|scrap|automated`.
    `curl -sL https://media.defense.gov/2025/May/22/2003720601/-1/-1/0/CSI_AI_DATA_SECURITY.PDF -o csi.pdf && pdftotext csi.pdf - | grep -inE 'copyright|license|licence|TLP|disclaimer|©|crown|creative commons'` -> any copyright or licence wording in the PDF itself bears on the co-sealed carve-out; also read the cover for which agencies co-seal (the co-seal list here is from a search extract).
    **Input that would make this fail:** `pdftotext` on a scanned or image PDF returns nothing and looks like "no copyright wording"; check the output is non-empty and contains a known phrase ("AI Data Security") first.
33. **17 U.S.C. s105 and the NVD route (1E.1/1E.2).** s105 is now verified verbatim by gate 2 (law.cornell.edu and govinfo, 2026-10-03); the command run was: `curl -sL https://www.law.cornell.edu/uscode/text/17/105 | sed -e 's/<[^>]*>/ /g' | grep -ioE 'Copyright protection under this title is not available[^.]*\.'` -> must match; a miss means the citation in 1E.2 is wrong. Also confirm the corpus count: `grep -c 'huntr\.\(com\|dev\)/bounties' data/incidents.json` (line count) and `grep -oE 'huntr\.(com|dev)/bounties/[0-9a-f-]*' data/incidents.json | sort -u | wc -l` for the distinct-URL count; gate-measured 2026-10-03: 284 distinct bounty URLs (216 huntr.com + 68 huntr.dev; 277 distinct IDs) in 210 of 13,361 entries. **Input that would make the count check fail:** a minified data file makes the line count 1; use the `-o | sort -u` form as the real measure.


