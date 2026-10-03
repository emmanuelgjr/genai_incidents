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

**Facts re-checked vs. taken from the brief:** nothing from the brief is
carried forward unverified; each row's "Retrieval method" says what was
actually fetched. Where a licence prior ("NCSC = OGL", "ACSC = CC BY 4.0")
differs from what was found, the row says so under "Brief vs. found".

## Licensing-cleanliness scale (0-3), defined once

| Score | Meaning |
|---|---|
| **3** | Verbatim ingest into a CC BY 4.0 dataset is allowed: explicit permissive grant (CC0 / CC BY / OGL / public-domain work) covering the content we would take, automated access not prohibited, nothing left open. Action (a). |
| **2** | Verbatim ingest allowed **with a condition we must engineer for** (per-item third-party carve-outs, attribution/notice formalities, rate limits, a filter to separate covered from uncovered material, or a grant read only second-hand). Action (a) with conditions. |
| **1** | Verbatim ingest **not** allowed or **unknown** (non-commercial, no-derivatives, all-rights-reserved, contradictory or missing terms), but the **facts + link + original summary** shape is not itself contested: no explicit ban on automated access or on extracting facts. Action (c) or (d). |
| **0** | **Even facts + link is contested**: an explicit prohibition on bulk/automated access or on open-licence redistribution of the data, a robots.txt that disallows the content, or a litigation history against scrapers. Do not ingest at all before a written permission. Action (d), interim "link only". |

The score is about the licence position only. It says nothing about volume, corpus
fit or maintenance cost; those go to the ranking, not here.

Action letters (as in `SOURCE_LICENSES.md`): (a) compatible · (b) share-alike
· (c) prohibited -> facts + link + original summary only · (d) unknown ->
outreach (user sends; none drafted here).

Project data licence for the "relicense-compatible" column: **CC BY 4.0**.

## Summary of pre-rows (27 candidates)

| # | Candidate | Score | Action | Blocking issue / condition |
|---|---|---|---|---|
| 1A.1 | UK NCSC | 3 | (a) | OGL v3.0 confirmed; per-record OGL notice; exclude third-party images/logos |
| 1A.2 | ACSC Australia | 2 | (a) provisional | CC BY 4.0 known only from a search extract; the site timed out for every fetch; per-document "Australian" variant |
| 1A.3 | CCCS Canada | 1 | (c) | Non-commercial reproduction only (CSE terms); **not** permissive, contrary to the brief's "trio" |
| 1A.4 | ENISA | 2 | (a) PDF reports; (d) web/DB | CC BY 4.0 for reports (policy read); CC BY-NC-ND training material excluded; website text and databases not covered |
| 1A.5 | BSI / CERT-Bund | 1 | (c) | Non-commercial, unmodified use only; WID-specific terms not read |
| 1A.6 | ANSSI / CERT-FR | 3 | (a) | Licence Ouverte 2.0 confirmed; do not fetch `/pdf`, `/fiche/`; attribution |
| 1A.7 | JPCERT/CC | 1 | (d) | No licence or ToS located (all-absence row, method-suspect) |
| 1A.8 | JVN / JVN iPedia | 1 | (d) | "All rights reserved"; reuse guidelines referenced but not located; MyJVN terms cover tools, not data |
| 1A.9 | SingCERT / CSA | 1 | (c) | All rights reserved; reproduction needs written permission |
| 1A.10 | CERT-EU | 1 | (d) | Legal notice says CC BY 4.0, advisories page footer says "All rights reserved"; no AI advisories seen |
| 1B.2 | EUVD | 1 | (d) | No licence/terms located; docs SPA unreadable; IPR policy does not name EUVD |
| 1B.3 | cvelistV5 | 2 | (a) cond. | CVE ToU requires MITRE notice; **repo shows no such notice today** |
| 1B.4 | VulnCheck KEV | 0 | (d) | Service Terms bar making data available under an open licence and AI training on free data; conflicts with its attribution page |
| 1B.5 | AVID | 2 | (a) cond. | MIT repo licence (structured); **already in corpus (109 entries) with no SOURCE_LICENSES row** |
| 1C.1 | Italy Garante | 1 | (d)/(c) | No general licence located; PDFs disallowed by robots; Italian |
| 1C.2 | EDPB registers | 2 / 1 | (c) + (d) | Custom reuse grant ("do not distort meaning"); national decisions' rights unclear |
| 1C.3 | Dutch AP | 1 | (c) | Copyright reserved, personal use + quotation (search extract; site returns 403 to the fetch tool) |
| 1C.4 | CNIL | 1 | (c); (a) open-data subset | Site text CC-BY-ND 4.0 FR; open-data decisions under Licence Ouverte not verified |
| 1C.5 | UK ICO | 3 | (a) | OGL v3.0 on enforcement register; honour Crawl-delay 6; "except where otherwise stated" |
| 1C.6 | Brazil ANPD | 1 | (c) | CC BY-ND 3.0 on all content; Portuguese |
| 1C.7 | Canada OPC | 1 | (c) | Non-commercial reproduction only |
| 1C.8 | BAILII | 0 | (c) link only | Terms bar bulk download/storage; robots disallows judgment trees; BAILII cannot authorise copying |
| 1C.9 | CanLII | 0 | (c) link only | Terms bar bulk/systematic download; robots `Disallow: /`; CanLII litigating over scraping (clause text second-hand, site 403) |
| 1D.1 | arXiv cs.CR | 3 meta / 0 full text | (a) metadata incl. abstract | **Brief refuted:** abstract is CC0 metadata; never mirror e-prints; 1 req / 3 s |
| 1D.2 | HackerOne Hacktivity | 1 | (c) | Researcher keeps copyright; licences run only to HackerOne and Customer; robots/Website ToS not read |
| 1D.3 | Bugcrowd | 0 | (c) link only | "Copying, redistribution, use or publication of any portion of our Website is strictly prohibited"; submissions confidential/assigned |
| 1D.4 | DEF CON AI Village / Black Hat | 1 | (c) | Speakers keep copyright; no downstream licence; fetches mostly failed |

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
| Relicense-compatible | **YES.** OGL v3.0 is attribution-only; a WebSearch extract of the National Archives' OGL v3 text (`https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/`) says v3.0 *"is interoperable with Creative Commons' Attribution 4.0"* and that adapted Information licensed under either licence satisfies the OGL conditions by complying with the other. We retain the NCSC attribution and the OGL notice alongside our CC BY 4.0 grant. The compatibility sentence is a search-engine extract, not a fetch of the licence page -- listed under "taken on trust (partially corroborated)". |
| Action | **(a) compatible.** Condition: per-record "Contains public sector information licensed under the Open Government Licence v3.0" notice; drop any item flagged as third-party material. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch (markdown-converting) of the T&C URL above, response stated "not truncated"; WebFetch of `/information/rss-feeds`; WebFetch of `/robots.txt` -> 404. Substrings read: "Crown copyright", "Open Government Licence", "third parties", "automated". Source kind: rendered HTML (method-exposed for absences, not for the positive OGL clause). |
| Non-English / facts-only | English. Facts + link + original summary is available but not needed for licence reasons. |

#### 1A.2 ACSC / ASD Australia (cyber.gov.au)
*Content class:* alerts, advisories, publications, annual threat report, ISM
(OSCAL mirror on GitHub). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **2** (grant is real, but the primary page could not be fetched by this agent, and the licence has an "Australian" variant on some documents) |
| License | **CC BY 4.0 International, per search-engine extract of the site copyright page -- NOT read from the page itself.** WebFetch of `https://www.cyber.gov.au/about-us/copyright` **timed out three times** (60 s each) and `robots.txt` and the alerts-and-advisories page timed out likewise, so the operative clause below is a **WebSearch summary** of that page, not a quotation: all material "is provided under a Creative Commons Attribution 4.0 International licence, with the exception of the Commonwealth Coat of Arms, the Australian Cyber Security Centre logo, content supplied by third parties, and other material specifically not provided under a Creative Commons Attribution 4.0 licence"; attribution form "(c) Commonwealth of Australia 2026". The same search showed that **some ASD documents use "Creative Commons Attribution 4.0 Australian Licence"** (the 2024-25 Annual Cyber Threat Report) while others use the International version -- a per-document variation. The brief's prior "CC BY 4.0" is therefore **plausibly right but unverified at the primary page**; the brief's implied "uniform" is refuted by the per-document variant. |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (timeout). **ToS: NOT OBTAINED** beyond the copyright page summary. Timeouts on this host recurred for every URL tried, which suggests bot protection or a slow origin; this is a **fetch-tool limit, not a finding about ACSC**. Status: **UNKNOWN pending shell check**. |
| Redistribute-verbatim | **YES per the CC BY 4.0 grant above, excluding** Coat of Arms, ACSC logo and third-party content (provisional until the page is read). |
| Relicense-compatible | **YES** (CC BY 4.0 -> CC BY 4.0), provisional. The Australian-port variant is a sibling licence, not identical; per-document licence field must be read. |
| Action | **(a) compatible, provisional.** Cannot be recorded as confirmed until red-reviewer curls the copyright page and robots.txt. |
| Date-checked | 2026-10-02 (search summary only) |
| Retrieval method | WebSearch query "cyber.gov.au copyright Creative Commons Attribution 4.0 content Australian Signals Directorate licence" (result summary, not page text). WebFetch of copyright, robots.txt, alerts page: all **timeout of 60000 ms**. Source kind: search-engine summary of rendered HTML (**weakest tier**). |
| Non-English / facts-only | English. |

#### 1A.3 CCCS Canada (Canadian Centre for Cyber Security)
*Content class:* alerts and advisories, publications. *Language:* English and
French (the site is bilingual; French is the official parallel text).

| Field | Value |
|---|---|
| Cleanliness score | **1** (brief's "permissive trio" framing is refuted for this member) |
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
| Cleanliness score | **2** (CC BY 4.0 default with "unless otherwise noted" and third-party carve-outs) |
| License | **CC BY 4.0 for publications.** Boilerplate extracted from multiple ENISA PDFs by WebSearch: *"Unless otherwise noted, the reuse of this document is authorised under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence"*; for photos or other material not under ENISA copyright, permission is to be sought from the copyright holders. The search also returned a paraphrase of ENISA's IPR policy: public reports and media publications under CC BY 4.0, re-user must state changes and may not imply endorsement; this rests on Commission Decision 2011/833/EU. **Primary text now read** (ENISA IPR Policy, public version, December 2021, `https://www.enisa.europa.eu/about-enisa/legal-notice/enisa-ipr-policy-public-version`, served as a PDF and read page by page from the saved file): s2.1.1 *"ENISA shares its public reports and media publications under open license with the use of Creative Commons – Attribution 4.0 – International (CC BY 4.0)."* / *"any possible re-use is allowed under the condition that ENISA is properly referenced as the source"*, plus: modifiers must state changes; no implied endorsement; partial use keeps the link to the original; translations must say ENISA did not endorse them. **Carve-out found:** s2.2 *educational/training courses and material* are **CC BY-NC-ND 4.0** (non-commercial, no derivatives) -- these must be excluded. s2.3 software is EUPL v1.2. Principle of attribution (s1.3): works are *"in principle free to share, free of charges and free to re-use"*. The policy speaks of "reports", "publications", "websites content" and "databases" generically in its definitions but **grants CC BY 4.0 only to public reports and media publications**; **website page text and any ENISA-run database/service (EUVD, row 1B.2) are not expressly licensed by this policy**. Reuse questions: `info@enisa.europa.eu`. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` with only Drupal-style disallows (`/core/`, `/profiles/`, `/admin/`, `/search/`, `/user/...`, `/node/add/`, `/media/oembed`); publications and news paths are not disallowed. **ToS: not located** (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **YES for publications under CC BY 4.0** with attribution and change statement; not for third-party photos/material. |
| Relicense-compatible | **YES** for CC BY 4.0 publications. |
| Action | **(a) compatible** for PDF reports and media publications (CC BY 4.0), excluding the CC BY-NC-ND training material and third-party photos; ENISA website page text and ENISA-run databases are **not covered by the policy** -> treat as (d) unknown unless a page-level notice is found. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebSearch (two queries) for the boilerplate; WebFetch of the IPR-policy URL -> returned a PDF that the markdown converter could not read; the saved PDF was then read directly with the Read tool (text layer + page images, pages 1-13, complete); WebFetch of robots.txt -> readable; WebFetch of two guessed legal-notice URLs -> 404. Source kind: primary PDF (policy clause, reliable) + search summary (boilerplate, weak) + robots.txt (reliable). |
| Non-English / facts-only | English primary. Facts-only not needed for licence reasons. |

#### 1A.5 BSI / CERT-Bund (Warn- und Informationsdienst, WID)
*Content class:* vulnerability short-advisories (Kurzinformationen), technical
warnings, CSAF documents, RSS. *Language:* **German** (some English).

| Field | Value |
|---|---|
| Cleanliness score | **1** (verbatim not allowed; facts + link + original summary is the shape) |
| License | **No open licence; non-commercial, unmodified use only.** BSI Nutzungsbedingungen, `https://www.bsi.bund.de/DE/Service/Nutzungsbedingungen/Nutzungsbedingungen_node.html` (WebFetch 2026-10-02): *"Software und Veröffentlichungen, die zum kostenfreien Download angeboten werden, dürfen nur zu nicht kommerziellen Zwecken verwendet werden."* / *"Eine weitergehende, insbesondere kommerzielle oder publizistische Verwendung bedarf der vorherigen Zustimmung durch das BSI."* / other downloadable content *"dürfen im Rahmen der gestatteten Verwendung nur unverändert verwendet werden."* (only IT-Grundschutz material may be modified, for internal security measures). **Gap:** the WID portal (`wid.cert-bund.de`) says it has its own "Nutzungsbedingungen"/Impressum; the fetches of the portal pages returned **only the page title** (JavaScript-rendered app shell or truncated), so the WID-specific terms and any licence field inside the CSAF documents were **not read**. Whether the WID terms are looser than the BSI-wide terms is **UNKNOWN**. |
| Scrape-permitted | **robots.txt: NOT FETCHED** for `bsi.bund.de` or `wid.cert-bund.de`. **ToS:** no automated-access clause in the BSI page (**ABSENCE FINDING, method-suspect**). Official machine channels exist (RSS `https://wid.cert-bund.de/content/public/securityAdvisory/rss`, CSAF info page `https://wid.cert-bund.de/portal/wid/csaf/info`), which is evidence that machine access is intended, **not** evidence that reuse is licensed. |
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
| License | **No licence located; treated as All Rights Reserved.** `https://www.jpcert.or.jp/english/` footer: *"© 1996-2026 JPCERT/CC"*, with a single policy link (`/english/privacy.html`). That privacy page contains only: *"In the case where different rules are otherwise specified in the Terms of Service of JPCERT/CC's website or other documents, the specified rules shall prevail."* A Terms of Service document is therefore referenced but **was not located**: guessed URLs `/english/site.html`, `/site.html`, `/policy.html` all returned 404. |
| Scrape-permitted | **robots.txt:** `https://www.jpcert.or.jp/robots.txt` -> 404 (**ABSENCE FINDING, method-suspect**). **ToS: not located** (**ABSENCE FINDING, method-suspect**). |
| Redistribute-verbatim | **UNKNOWN** -> treated as NO. |
| Relicense-compatible | **UNKNOWN** -> treated as NO. |
| Action | **(d) unknown.** Do not ingest verbatim. Before any outreach, red-reviewer must run the raw-HTML checks listed in the report, because the Terms of Service the privacy page points to probably exists at a URL this agent did not guess. Fallback shape: **(c) facts + link + original summary**. JPCERT advisory content is largely duplicated by JVN (row 1A.8), which is the better structured source. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `/english/`, `/english/privacy.html` (both read), guessed `/english/site.html`, `/site.html`, `/policy.html`, `/robots.txt` (404). Source kind: rendered HTML; **the whole row is an absence finding and method-suspect**. |
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
| License | **No open licence found; copyright asserted; reuse terms deferred to a document not located.** JVN iPedia page footer: *"Copyright © 2007- IPA. All rights reserved."*; JVN feeds page (`https://jvn.jp/en/rss/index.html`): *"Copyright © 2000-2015 JPCERT/CC and IPA. All rights reserved."* and *"The tools provided in this website are available both to private and corporate users."* (a statement about the **tools**, not the data). JVN iPedia FAQ (`https://jvndb.jvn.jp/nav/jvndb_faq.html`, Q5-2): *"In regard to quotation, citation, and redistribution, please refer to the separately provided guidelines. When using this information, please confirm the applicable conditions in advance."* and Q5-1/Q4-4: commercial services *"must comply with MyJVN API Terms of Use"*. **Those guidelines were not located.** **Correction of a tempting reading:** the MyJVN terms (`https://jvndb.jvn.jp/apis/myjvn/document/termsofuse.pdf`, enacted 2023.3.29, read in full this pass via the saved PDF) govern only two **software tools** (mjcheck and MyJVN Version Checker for .NET): Art. 2 forbids copying/distributing *the tools*. They say nothing licensing the vulnerability **data**. A WebSearch summary claimed "no restrictions, asked to notify by email"; **that was not found in any page read** and is not relied on. |
| Scrape-permitted | **robots.txt:** `https://jvndb.jvn.jp/robots.txt` -> 404 (**ABSENCE FINDING, method-suspect**). **ToS:** MyJVN API terms page (`/apis/termsofuse.html`) is the tool terms above; no data-scraping clause found (**ABSENCE FINDING, method-suspect**). The MyJVN API and RSS are *official machine channels* run for the purpose, which supports access, not reuse. |
| Redistribute-verbatim | **UNKNOWN** -> treated as NO. Note CVE text itself is separately governed by the CVE Terms of Use (row 1B.3); JVN's added value is the Japanese/English analysis, CVSS and vendor-status fields, on which IPA/JPCERT assert copyright. |
| Relicense-compatible | **UNKNOWN** -> treated as NO. |
| Action | **(d) unknown -> outreach** to IPA (`isec-jvndb@ipa.go.jp`, the address the FAQ itself gives) asking for the "separately provided guidelines" on quotation/redistribution and whether CC-BY-compatible reuse is allowed. User sends. Interim shape: **(c) facts + link**, where facts = JVNDB id, CVE id, dates, affected-product names, link; CVSS scores are IPA's analysis and sit in the grey zone. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `jvndb.jvn.jp/en/`, `/en/nav/jvndbhelp.html`, `/nav/jvndb_faq.html`, `jvn.jp/en/rss/index.html`, `jvn.jp/en/nav/jvnhelp.html`, `/apis/termsofuse.html` (this one reported **character-encoding problems / truncation**), robots.txt (404); the MyJVN terms PDF was read in full from the tool's saved file. Source kind: rendered HTML + one PDF. The "guidelines not located" finding is an **absence finding, method-suspect**. |
| Non-English / facts-only | Japanese + English. English text exists upstream, so translation is not needed; the facts + link + original summary shape applies if (c). |

#### 1A.9 SingCERT / CSA Singapore
*Content class:* alerts and advisories, playbooks, reports. *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (verbatim not allowed; no explicit ban on automated access or on extracting facts) |
| License | **All rights reserved; written permission required.** CSA Terms of Use, `https://www.csa.gov.sg/terms-of-use/` (WebFetch 2026-10-02; corroborated by a WebSearch extract): *"Contents of this website shall not be reproduced, republished, uploaded, posted, transmitted or otherwise distributed"* without CSA's prior written permission; graphics and images likewise. The fetch reported no exception for government reuse or open-data frameworks, and the page's "Governing Law" sentence appeared cut off mid-sentence (**tool truncation or a page defect; the remainder of the page may hold more**). |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-Agent: *` `Allow: /` `Disallow: /search`; sitemap listed. So robots permits crawling advisory pages. **ToS:** no explicit clause on robots, scraping or automated access found (**ABSENCE FINDING, method-suspect**), but the reproduction prohibition above applies to what scraping would yield. |
| Redistribute-verbatim | **NO** without CSA's written permission. |
| Relicense-compatible | **NO.** |
| Action | **(c) prohibited -> facts + link + original summary.** No open-data licence for SingCERT advisories was found (**ABSENCE FINDING, method-suspect**: only the terms page was read; Singapore government open-data licensing was not searched). Whether CSA would grant permission is **(d)**, but the expected value is low. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of the terms URL and of `robots.txt` (both read); WebSearch (matching extract). Source kind: rendered HTML; the clause is positive, so not method-exposed; the absence of an automated-access clause is. |
| Non-English / facts-only | English. Facts + link + original summary is the only available shape. |

#### 1A.10 CERT-EU
*Content class:* security advisories (14 published in 2026 up to 27 Sept, all
mainstream enterprise products, **none AI-related** on the page read), threat
landscape reports, RSS (`/publications/security-advisories-rss`). *Language:* English.

| Field | Value |
|---|---|
| Cleanliness score | **1** (two statements on the same site contradict each other) |
| License | **CONTRADICTORY.** The legal notice at `https://cert.europa.eu/legal-notice` (WebFetch 2026-10-02) states reuse under the Commission policy: *"The reuse policy of European Commission documents is implemented by Commission Decision 2011/833/EU of 12 December 2011"*; content *"authorized under Creative Commons Attribution 4.0 International (CC-BY 4.0)"* with *"reuse is allowed, provided appropriate credit is given and changes are indicated"*; carve-outs for identifiable individuals, third-party works, and material under industrial property rights. **But** the security-advisories listing page, `https://cert.europa.eu/publications/security-advisories/` (WebFetch 2026-10-02), has the footer *"(c) 2022-2026 CERT-EU. All rights reserved."* and no TLP/licence marking. The legal-notice text read like generic Commission wording (it did not mention CERT-EU by name in the extract), so it is **not established that the legal-notice CC BY 4.0 grant is meant to cover CERT-EU's own advisory text.** Per the rule that ambiguity is not resolved in the project's favour: UNKNOWN. |
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
| Cleanliness score | **1** |
| License | **None located for the database or API.** The ENISA IPR Policy (row 1A.4) grants CC BY 4.0 to *"public reports and media publications"* only; it does not name EUVD. A structured API response (`https://euvdservices.enisa.europa.eu/api/lastvulnerabilities`, fetched 2026-10-02 as JSON: fields `id, enisaUuid, description, datePublished, dateUpdated, baseScore, baseScoreVersion, baseScoreVector, references, aliases, assigner, epss, enisaIdVendor`) carries **no licence, terms or disclaimer field**. The UI/docs URLs `https://euvd.enisa.europa.eu/` and `/apidoc` returned only an error shell: *"The European Vulnerability Database application could not be loaded."* (a single-page app that the fetch tool could not run; **this is a tool limit, not a statement about the site**). Underlying data: CVE records (governed by the CVE ToU, row 1B.3), `epss` scores (FIRST), and CNA/ENISA enrichment. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02) at `euvd.enisa.europa.eu`:** `User-agent: *` `Disallow:` (empty = everything allowed). **ToS: not located** (**ABSENCE FINDING, method-suspect**; the SPA shell is exactly the situation in which a ToS link exists but is invisible to this tool). The API is public and unauthenticated for the endpoint tried. |
| Redistribute-verbatim | **UNKNOWN.** CVE-derived fields: YES under CVE ToU with the MITRE notice. ENISA-added fields (EUVD id, enrichment): UNKNOWN. EPSS: FIRST's own terms apply (not checked here -- on trust). |
| Relicense-compatible | **UNKNOWN** for ENISA-added fields; CVE-derived fields compatible (row 1B.3). |
| Action | **(d) unknown -> outreach** to ENISA (`info@enisa.europa.eu`, the IPR policy's contact) on EUVD reuse; interim shape **(c)**: EUVD id + CVE id + link, descriptions taken from the CVE record, not from EUVD. Third-party community docs (`github.com/bytew0lf/EUVD-API`, explicitly "not the official documentation") list endpoints; see watch item W2. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of `euvd.enisa.europa.eu/`, `/apidoc` -> error shell; WebFetch of `robots.txt` (readable); WebFetch of `euvdservices.enisa.europa.eu/api/lastvulnerabilities` -> JSON (**structured endpoint**); WebSearch for docs. Source kind: **JSON endpoint (reliable for fields present; silent on legal terms by construction)** + SPA shell (**method-suspect**). |
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
| Relicense-compatible | **YES, with a notice condition.** The grant includes "sublicense" and "prepare derivative works", so a CC BY 4.0 grant by us over our derived dataset is allowed provided the MITRE notice and CVE-ToU text travel with it. **Existing-corpus gap, observed locally:** a Grep of `NOTICE*`, `README.md`, `docs/SOURCE_LICENSES.md` and `docs/DATASHEET.md` for "MITRE Corporation" or CVE terms-of-use found **nothing**; the corpus already carries NVD-derived CVE text (SOURCE_LICENSES 2.2). The MITRE notice requirement therefore applies **today**, independent of this evaluation. (Local grep, not method-exposed, but the glob form should be re-run by red-reviewer.) |
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
| Retrieval method | WebFetch of `vulncheck.com/kev`, the attribution page, the FAQ (**truncated** -- redistribution Q&A not seen), `service-terms`; WebSearch. Source kind: rendered HTML. Clause texts are positive findings quoted through the markdown converter (paraphrase risk: the service-terms quotes should be re-read in raw HTML). The FAQ truncation means "no redistribution Q&A" is an **absence finding, method-suspect**. |
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

| Field | Value |
|---|---|
| Cleanliness score | **2** |
| License | **MIT for the `avidml/avid-db` repository (structured).** GitHub API (`https://api.github.com/repos/avidml/avid-db`, fetched 2026-10-02): `license: {key: mit, spdx_id: MIT}`; raw LICENSE: *"MIT License / Copyright (c) 2022 AI Vulnerability Database (AVID)"*. Repo contents (API): `reports`, `scripts`, `vulnerabilities` (`2022`, `2023` subfolders), `LICENSE`, `README.md`; last push 2026-03-26. **Caveats:** (i) MIT is a software licence applied to a data repo; it is the only grant found, and it covers the repo as a whole; (ii) the live site (`https://avidml.org/database/`) lists reports up to AVID-2026-R0518+, so **the repo may lag the site**; (iii) records summarise third-party material (papers, news, other databases) whose rights are not AVID's to grant. The website database page showed **no licence statement** (**ABSENCE FINDING, method-suspect**; the page was truncated by the tool) and `https://docs.avidml.org/` showed none in the portion fetched. |
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
| License | **Copyright reserved; personal use and quotation with source citation; not an open licence (second-hand).** The AP copyright page, `https://autoriteitpersoonsgegevens.nl/over-deze-website/copyright`, **returned HTTP 403 to WebFetch** (the AP site blocks the fetch tool; the same happened for its English pages and, presumably, `robots.txt`). The text below is from a **WebSearch extract of that page**, not a fetch: *"Copyright rests on the texts, photos and other images of the Autoriteit Persoonsgegevens (AP) on this website"*; for texts, personal use (including copying) is permitted if the source is cited and quoting or using large parts of texts is allowed; photos and images may not be used; the AP logo is a registered Benelux trademark and no third-party use is permitted. **Refutation of a tempting shortcut:** `rijksoverheid.nl` publishes under CC0 1.0 (`https://www.rijksoverheid.nl/service/copyright`, fetched), but the AP is an independent authority with its own site and its own, narrower copyright page; the CC0 statement was **not** carried over. |
| Scrape-permitted | **robots.txt: NOT OBTAINED** (403). **ToS: NOT OBTAINED** beyond the copyright extract. Status UNKNOWN pending shell check. |
| Redistribute-verbatim | **NO** by the extract (personal use + quotation only). |
| Relicense-compatible | **NO.** |
| Action | **(c) facts + link + original summary.** **(d)** optional: ask the AP whether its published sanction decisions are available under any open-government-information reuse regime. (A WebSearch result surfaced a Dutch open-data-directive implementation memorandum; its application to the AP was **not** examined.) |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch of AP copyright page and English fines page -> **403**; WebSearch (2 queries) -> extract; WebFetch of rijksoverheid.nl copyright (read, not the AP). Source kind: search-engine extract (**weakest tier**) for the AP's terms. |
| Non-English / facts-only | **Dutch.** Original English summary + link, offline. |

#### 1C.4 CNIL (France)
*Content class:* sanctions, mises en demeure, guidance, deliberations (published on Legifrance). *Language:* **French** (some English).

| Field | Value |
|---|---|
| Cleanliness score | **1** (site text is ND; the open-data channel is open but a different surface) |
| License | **Split by content type.** CNIL Mentions legales, `https://www.cnil.fr/fr/mentions-legales`, section "Reutilisation des contenus" (WebFetch 2026-10-02, quoted twice with the same result): texts: *"Les textes disponibles sur le site sont des contenus pédagogiques élaborés par la CNIL qui sont mis à disposition selon les termes de licence CC-BY-ND 4.0 FR"*; images/videos: CC-BY-NC-ND 4.0 FR; open data: *"Les données publiques détenues ou produites par la CNIL dans le cadre de l'open data sont mises à disposition par défaut selon les termes de la Licence ouverte"*. Also: *"Seules les délibérations adoptées en séance plénière et publiées sur légifrance sont de nature à engager la CNIL"*. **CC-BY-ND (no derivatives) is incompatible with a CC BY 4.0 relicense and with summaries that adapt the text**. The French open-data channel (decisions on Legifrance/data.gouv under Licence Ouverte) is the compatible route, but **which CNIL decisions are in that dataset, and its licence page, were not fetched**. |
| Scrape-permitted | **robots.txt (fetched, readable, first ~60 lines only, 2026-10-02):** Drupal-style `User-agent: *` with asset allows and standard disallows; the remainder of the file was not read. **ToS:** no automated-access clause in the Mentions legales extract (**ABSENCE FINDING, method-suspect**). |
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
| License | **OGL v3.0.** ICO enforcement register page, `https://ico.org.uk/action-weve-taken/enforcement/` (WebFetch 2026-10-02): *"All text content is available under the Open Government Licence v3.0, except where otherwise stated."* with the OGL logo in the footer. Page also warns of date errors in some documents added before 31 December 2024. (An Apify third-party page claiming OGL was not relied on.) `ico.org.uk/global/copyright/` and a website-terms URL returned 404. |
| Scrape-permitted | **robots.txt (fetched, readable, 2026-10-02):** `User-agent: *` `Crawl-delay: 6`, `Disallow: /private`, `/restricted`; `deepcrawl` bot is `Disallow: /`. So **6 s between requests**. **ToS: the website-terms page was not found** (**ABSENCE FINDING, method-suspect**). No export/RSS/API seen on the register page (**ABSENCE FINDING, method-suspect**). |
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
| Retrieval method | WebFetch `canlii.org/info/terms.html` and `/en/info/terms.html` -> **403**; WebFetch `canlii.org/robots.txt` (read); WebSearch (extracts); WebFetch of the API GitHub issue (read). Source kind: **search-engine extract for the clause text (weak)**, robots.txt reliable. The quoted prohibition should be confirmed in raw HTML by red-reviewer before it is relied on. |
| Non-English / facts-only | Bilingual. |

### 1D. Research and disclosure

#### 1D.1 arXiv cs.CR (filtered to AI-relevant papers)
*Content class:* paper metadata (title, authors, **abstract**, categories, DOI,
dates) and full text/e-prints. *Language:* English (some other).

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
| License | **No licence to the public; researchers keep ownership; licences run only to HackerOne and the Customer.** HackerOne Finder Terms (2023), `https://www.hackerone.com/terms/finder-2023` (WebFetch 2026-10-02): *"HackerOne does not claim any ownership rights in any Finder Submissions"*; by making a submission available to a Customer the finder grants HackerOne **and** the Customer *"a perpetual, irrevocable, non-exclusive, transferable, sublicensable, worldwide, royalty-free license to use, copy, reproduce, display, modify, adapt, transmit, and distribute copies of that Finder Submission"* (the fuller phrasing is from a WebSearch extract of the Finder Terms; the fetch confirmed the structure: licences to HackerOne and Customers only). **The researcher's copyright in report text therefore survives and no grant reaches third parties.** The Disclosure Guidelines (`https://www.hackerone.com/terms/disclosure-guidelines`): reports can become public (*"the contents of the Report will be made public within 30 days if the Report state is 'Resolved'"* under the Default setting) but the guidelines contain **no reuse or licensing statement** for disclosed reports. The "Terms" URL `https://www.hackerone.com/terms` is the **Customer** T&C and does not cover public visitors. HackerOne AI Terms (`/terms/AI`): bar HackerOne from training general-purpose AI on Customer input; silent on third-party use of disclosed reports. |
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
| License | **No open licence found; speakers keep copyright and grant the conference distribution rights.** DEF CON: WebSearch extract of the DEF CON call-for-papers form: speakers grant DEF CON Communications *"permission to duplicate, record and redistribute this presentation ... for educational, on-line, and all other purposes"* and submit presentations/tools *"for publication on the DEF CON media server"*; the media server (`media.defcon.org`, **WebFetch failed with ECONNRESET twice**) is described as open to browse and download. Black Hat: WebSearch extract of CFP terms: speakers grant Black Hat permission *"to record, reproduce, distribute, advertise, and show presentations"*; Black Hat describes its archive as *"provided free of charge as a service to the worldwide computer security community."* `blackhat.com/terms.html` returned **403** to WebFetch. AI Village (`https://aivillage.org/`, fetched): *"no explicit licensing or terms information is stated"* for reports, GRT reports or datasets; its GitHub org is `github.com/aivillage` (repo licences not checked; one guessed repo API returned 404). Result: **a licence to the conference, not to us; "free to download" is not "free to redistribute".** |
| Scrape-permitted | **robots.txt: NOT OBTAINED** for `defcon.org` (ECONNRESET), `media.defcon.org` or `blackhat.com` (403). **ToS: not located** (**ABSENCE FINDINGS, method-suspect; the whole row is one**). |
| Redistribute-verbatim | **UNKNOWN -> treated as NO.** |
| Relicense-compatible | **UNKNOWN -> treated as NO.** |
| Action | **(c) facts + link + original summary** (talk title, speaker, year, venue, link to the archive entry; the conference listing of a title is a fact, our summary is ours). Per-repo licences for AI Village GitHub material (structured API licence field) is the cheap next check if any is wanted. |
| Date-checked | 2026-10-02 |
| Retrieval method | WebFetch (ECONNRESET x3, 403 x1, aivillage.org read), WebSearch x2 (extracts of CFP terms). Source kind: **search-engine extracts (weak)**; the CFP forms themselves were not fetched. |
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
extracts; red-reviewer to run the raw-HTML check listed in the report.

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
reachable through GHSA/OSV (SOURCE_LICENSES 2.3, 2.4).

### 2.3 VulDB
**Reason:** non-commercial, share-alike licence. WebSearch extract of
`https://vuldb.com/kb/terms` (the page itself returned **HTTP 403** to
WebFetch): free users *"are not allowed to use the service in a commercial
context and have to attribute VulDB as source as defined by the license CC BY-NC-SA 4.0"*,
and the public-access licence forbids use of the data *"within a commercial
project"*; commercial use needs a paid subscription. CC BY-NC-SA is
incompatible with a CC BY 4.0 dataset on both counts (NC and SA). **Evidence kind:**
search extract, to be confirmed in raw HTML.

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

### W2. EUVD API maturation (dated 2026-10-02)
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

*(Placeholder. Not filled by license-auditor. Per candidate that is not
licence-blocked: AI-relevant volume and method, overlap/dedupe against the
existing corpus, ingest shape, corpus fit, WS4-T2 reconciliation cost, and the
non-English handling for each non-English row above. Rows scored 0 in section 1
should not be estimated until a written permission exists.)*

---

## 5. Ranking and waves

*(Placeholder. Not filled by license-auditor. Method and every factor score to
be shown by the ranking step; licence-cleanliness scores from section 1 are an
input, not the ranking.)*

