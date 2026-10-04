# Source Licenses & Terms-of-Service Audit

**Task:** WS0-T1 · **Status:** every upstream source class enumerated from
`scripts/ingest_*.py` / `scripts/scrape_*.py` carries a row below; none are
blank. Ambiguous terms are marked **UNKNOWN** and are *not* resolved in the
project's favor — the conservative reading (fewer rights, not more) is
applied until outreach resolves them.

**How to read this table:**
- **scrape-permitted** — is bulk/automated fetching of this upstream allowed
  per its robots.txt and/or its Terms of Service, independent of licensing?
- **redistribute-verbatim** — may we keep and ship the source's own text
  (titles, descriptions, narrative) unmodified in our corpus?
- **relicense-compatible** — can content from this source be included under
  this project's CC-BY-4.0 data relicense without a carve-out?
- **action** — (a) compatible, document as-is · (b) share-alike (BY-SA):
  split license for that corpus / reduce to facts+link · (c) prohibited:
  drop verbatim text, keep `id + url + ≤2-sentence original summary` ·
  (d) unknown: outreach sent/drafted, pending status recorded.
- **UNKNOWN** — *terms not located by the methods stated in the row. This is
  **not** confirmed absence.* An UNKNOWN records the limits of our retrieval,
  not a fact about the upstream. Absence-based findings here are presumed
  method-suspect: on 2026-07-16 this document recorded AIAAIC as having no
  license, and it was wrong — the clause was in the raw HTML of both pages
  checked, split across tags inside a 4.4 MB page, and a markdown-converting
  fetch silently truncated it away. Any row asserting absence must state the
  retrieval method used and is verified against raw HTML (curl + grep, not
  rendered text) before it stands. Structured endpoints (e.g. a GitHub API
  `license` field) are not exposed to that failure mode; rendered HTML pages
  are. Treat an UNKNOWN as "go look again with a better tool," never as
  "there is nothing there."

Per invariant #10 (active the moment this file exists): any new source added
after this file lands must get its row in the same PR.

All terms below were fetched and read on **2026-07-15**. Terms change —
re-check before relying on a stale "date-checked."

---

## 1. Real-world incident sources

### 1.1 AIAAIC Repository
*Ingested by:* `scripts/ingest_aiaaic_sheet.py` (reads the AIAAIC-maintained
Google Sheet CSV export at `docs.google.com/spreadsheets/d/.../export?format=csv`).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY-SA 4.0.** aiaaic.org's site-wide footer, present on both the homepage and `/aiaaic-repository` (the exact page fronting the ingested sheet), states: *"AIAAIC content is available to use, copy, adapt, and redistribute under a"* [CC BY-SA 4.0 licence](https://creativecommons.org/licenses/by-sa/4.0/). Verified by direct primary-source fetch (raw HTML, not a markdown-converting tool): `curl -sL https://www.aiaaic.org/` → HTTP 200 → `grep -oi "cc by-sa"` → 3 hits; `https://www.aiaaic.org/aiaaic-repository` → HTTP 200 → 1 hit; independently corroborated by a second party's identical grep counts. Only `/about-aiaaic` genuinely lacks the notice. **Why my own earlier WebFetch-based attempts missed this:** the clause is split across HTML tags (`...under a </span><a class="XqQF9c" href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0 licence</a>`) inside a 4.4 MB page; a markdown-converting fetch of a page that size loses trailing content instead of rendering the split anchor as an adjacent link — the page is server-rendered, not JavaScript-dependent, contrary to my earlier hypothesis. That mechanism is now understood and doesn't change the fact itself, which is established. |
| Scrape-permitted | `aiaaic.org` itself returns 404 for `/robots.txt` (no file = no stated restriction). The actual fetch target is `docs.google.com`; its robots.txt (`https://docs.google.com/robots.txt`, fetched 2026-07-15) has `Allow: /spreadsheet` (prefix match, covers `/spreadsheets/d/.../export`) ahead of the blanket `Disallow: /`, so the CSV-export mechanism itself is not blocked by Google's robots.txt. No AIAAIC-specific ToS beyond the general CC BY-SA grant was found for the sheet-fetch cadence itself. |
| Redistribute-verbatim | **YES under the upstream grant** — CC BY-SA permits verbatim copying and adaptation, conditioned on share-alike redistribution and attribution. That said, **decision D2 (2026-07-16, human) means we choose not to exercise this right**: see Action. |
| Relicense-compatible | **NO.** Share-alike (BY-SA) is definitionally incompatible with folding this content into a plain CC-BY relicense of the whole corpus — a true statement about the upstream grant, independent of what we choose to do with it. |
| Action | **(b) copyright share-alike, honored by reduction — not by split-licensing.** Per decision D2 (2026-07-16, human): do not carry AIAAIC verbatim cell text; keep `title` (headline) + short non-narrative facts (`system`, `technology`, `sector`, `jurisdiction`, and the affected developer/deployer — an organisation name, not a taxonomy tag) + a source pointer to the specific AIAAIC entry. (On the 95 hand-curated rows in `ingest/aiaaic_incidents.json` — a separate ingest path from the sheet-derived 1,422 — `references[0].title` additionally carries AIAAIC's own headline verbatim behind a literal `"AIAAIC - "` prefix, on 49 of 92 joinable rows — joined against the raw cached sheet (`ingest/_cache/aiaaic_sheet.csv`, 2,159 URL-keyed rows), not the filtered 1,504-row `ingest/aiaaic_sheet_incidents.json` ingest output, which joins to a different population and yields a different joinable/verbatim count — including all 13 whose `title` field has since been replaced; per user ruling 2026-07-29 this is retained and disclosed as a citation of the cited work by its own title, not stripped as if it were an assertion of our own editorial voice — see `docs/audits/E16-title-similarity-review-2026-07-29.md` §4.) The dataset stays under one clean CC-BY-4.0 license with **no BY-SA subset** — there is no AIAAIC-specific `license: CC-BY-SA-4.0` field and no corresponding LICENSE-DATA carve-out (this recommendation is withdrawn; superseded by D2). The ATLAS/garak Apache-2.0 carve-outs (§3.1/§3.3) are unaffected — those stand on their own facts and D2 doesn't touch them. This is now the **permanent** handling for the *copyright* question over AIAAIC's narrative prose, not an interim measure pending outreach. A narrow, non-blocking clarification email to AIAAIC — on attribution format and confirming the recurring Google-Sheet CSV-export cadence is fine — is still worth sending but gates nothing here, and **has not yet been sent**; the email actually sent 2026-07-27 (`docs/outreach/aiaaic-facts-link.md`) asks the database-right/ShareAlike question below instead, not this one — see that paragraph for what it gates. **A second, narrower copyright question is open and folded into the same counsel ask as the database-right question below rather than resolved here: does AIAAIC's retained headline — an editorial characterisation, not a bare fact — itself defeat the "disposes of the copyright share-alike question" conclusion under UK/EU law (escalation E15, decided 2026-07-29 → D17)?** See counsel question 8 in `docs/audits/WS0-E13-database-right-2026-07-18.md` §5.1 for the full analysis; the existing row-level `content_license` marker described below already covers the headline regardless of how that question resolves, so nothing engineering-side hinges on the answer, only prose. **This does not resolve licensing risk for AIAAIC in full: the separate EU/UK sui generis database-right question is OPEN**, not answered by D2's copyright reasoning (facts are not copyrightable expression, but the database right protects a database's contents — including bare facts — as such, regardless of copyrightability). See `docs/audits/WS0-E13-database-right-2026-07-18.md` (E13, 2026-07-18; amended 2026-07-27), which finds subsistence and substantiality of AIAAIC's database right each more-likely-than-not for the current extraction — **1,422 rows carry the field-level `content_license` marker via AIAAIC-sheet descent; 1,517 rows cite an AIAAIC entry in total** (the 95-row gap is the hand-curated set above, now also marked per E16/D18, 2026-07-29) — not the stale "~1,513" this cell previously carried — and finds facts+link only a partial mitigation. **Direction decided and implemented: decision D11 (2026-07-27)**, per E13's §6.1 revised menu — (b) lightweight row-level ShareAlike/attribution containment, implemented via the `content_license` marker now reaching every AIAAIC-citing row, **plus** (d) scope-narrowing the AIAAIC extraction toward security-relevant entries via the WS1-T4/E5 mechanism, queued for Phase 2. Counsel engagement (option (a)) was not chosen; knowingly accepting residual risk (option (c)) was superseded by (b) actively containing the exposure. The email actually sent to AIAAIC on 2026-07-27 (`docs/outreach/aiaaic-facts-link.md`; reply clock 2026-08-26) asks exactly this database-right/ShareAlike question — not the narrow attribution/CSV-cadence clarification noted above, which remains unsent — so this question is pending AIAAIC's reply to that outreach or a qualified-counsel resolution, consistent with `docs/DATASHEET.md` and `.reuse/dep5`. **Established, not merely assumed (2026-07-27):** genai_incidents' sole maker is an individual habitually resident in Canada with no UK/EEA entity involved, so genai_incidents itself fails the reg 18(1)(a)/Art 11 maker-qualification test and holds no UK/EU sui generis database right of its own — CC BY-SA §4(b)'s *database-level* ShareAlike escalation is **dead**, not merely narrowed, and the worst case (if AIAAIC's own right subsists and this extraction is judged substantial) settles at §4(c)→§3(a) **row-level** ShareAlike on the AIAAIC-derived rows only, never a dataset-wide obligation on this repository's own CC-BY-4.0 grant. AIAAIC's own database-right subsistence and this extraction's substantiality (E13 §1–§2) remain open, fact-intensive UK-database-law questions pending qualified counsel, if the project chooses to seek it. |
| Derivative-work constraint (D2) | **AIAAIC-derived summaries must be written from the primary sources AIAAIC links to — never paraphrased from AIAAIC's own prose.** A close paraphrase of BY-SA text is arguably a derivative work, which would reimport the share-alike obligation that reducing to facts+link exists to shed. "Facts + link" is only a real remedy if the facts are independently sourced; laundering the same prose through a paraphrase is not a reduction. Binds the WS0-T3 implementation (see the plan's WS0-T3 body, which carries the same constraint). |
| Date-checked | 2026-07-15 (fact); 2026-07-16 (independently re-verified by primary-source fetch; D2 recorded same date) |

### 1.2 AI Incident Database (AIID) — direct scrape (RETIRED 2026-07-18)

**STATUS UPDATE (2026-07-18): this ingestion method is retired.** The
row below is preserved as the historical finding that motivated the
retirement (decision D1, 2026-07-16 — swap-half). The active ingest is
now §1.2a. `scripts/scrape_aiid.py`'s `main()` (the concurrent
per-page-scrape entry point) is disabled in `Makefile` (`make ingest-all`
never calls it) and MUST stay disabled; the module is kept only as a
function library (`TAXONOMY_RULES`, `severity_for`, `is_security_relevant`,
`map_taxonomy`) reused by §1.2a's ingest.

*Was ingested by:* `scripts/scrape_aiid.py` (concurrently fetched
`incidentdatabase.ai/cite/<id>/` HTML pages, 12 worker threads, and read
`og:title`/`og:description` meta tags).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY-SA 4.0** for specific named collections only — `incidentdatabase.ai/terms-of-use/` (fetched 2026-07-15) states: *"The following database collections are licensed under the Creative Commons attribution share-alike license"* (incidents, quickadd, duplicates, taxa, classifications, entities, entity_relationships). It explicitly **excludes** the `text` field of the `reports` collection from that license. |
| Scrape-permitted | **NO.** The same Terms of Use state, verbatim: *"High-volume means of accessing the Site, including but not limited to bots and spiders, are prohibited."* `scrape_aiid.py` ran a `ThreadPoolExecutor(max_workers=12)` against every `/cite/<id>/` URL harvested from sitemaps — this is exactly the high-volume/bot access the ToS prohibits. This was live in production until the stop-half of WS0-T4 (2026-07-16) disabled it. |
| Redistribute-verbatim | **NO** for the `text` field (explicitly carved out of the CC license, and AIID's own ownership over it is not established either — likely third-party news-article excerpt). The `og:description` scraped here may or may not have corresponded 1:1 to the excluded `text` field internally; that ambiguity did not matter because the *access method itself* was already prohibited regardless of which field was touched. |
| Relicense-compatible | **NO** for the CC-BY-SA-licensed fields (share-alike ≠ plain CC-BY). The `text` field is out of scope for any relicensing since it isn't AIID's to license in the first place. |
| Action taken | **Retired (2026-07-18).** Replaced end-to-end by §1.2a's sanctioned-snapshot ingest. See `docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md` and `docs/audits/WS0-T4-aiid-snapshot-swap-delta-2026-07-18.md` for the implementation and the full field-level before/after delta. |
| Date-checked | 2026-07-15 (retired 2026-07-18) |

### 1.2a AI Incident Database (AIID) — official sanctioned snapshot (ACTIVE, added 2026-07-18)

*Ingested by:* `scripts/ingest_aiid_snapshot.py` (`make ingest-aiid`),
downloading AIID's official weekly snapshot archive
(`backup-<timestamp>.tar.bz2`) from `https://incidentdatabase.ai/research/snapshots/`
(served from the R2 bucket `pub-72b2b2fc36ec423189843747af98f80e.r2.dev/`),
verified live 2026-07-18 (weekly cadence confirmed, latest at
verification: `backup-20260713110347.tar.bz2`). Output:
`ingest/aiid_full.json` (same filename as the retired scrape's output — a
deliberate drop-in replacement) + `ingest/aiid_full.provenance.json`
(snapshot URL/filename/sha256/fetched-at, a pinned provenance record).

| Field | Value |
|---|---|
| License | Same as §1.2 — CC BY-SA 4.0 for the `incidents`/`quickadd`/`duplicates`/`taxa`/`classifications`/`entities`/`entity_relationships` collections; the `reports` collection's `text` field is explicitly excluded. The snapshot archive itself ships a `license.txt` corroborating this: *"Report contents are subject to their own intellectual property rights. Unless otherwise noted, the database is shared under (CC BY-SA 4.0)."* |
| Scrape-permitted | **YES for this specific channel.** This is AIID's own named bulk-download mechanism, not a scrape of per-page HTML; no ToS prohibition applies to fetching a published snapshot archive the way the per-page bot-access prohibition applied to §1.2's method. |
| Redistribute-verbatim | **Deliberately NOT exercised for narrative text**, even though the `incidents.description` field (unlike `reports.text`) is technically within the CC-BY-SA grant. `ingest_aiid_snapshot.py` reads `incidents.description` only as an ephemeral, in-memory classification signal (security-relevance / attack_vector / severity heuristics) and never writes it to the output — the persisted `description` is always an original templated sentence built from structured facts (id, title, entities). Only the AIID-authored `title` (a short headline, not narrative) is kept verbatim, plus structured non-narrative facts (id, date, url, deployer/developer entity slugs, MIT AI Risk Repository categorical taxonomy fields). `reports.csv`/`reports.bson` are never even extracted from the archive. This keeps the ingest **more conservative than §1.2's retired method**, which persisted a truncated verbatim `og:description`. |
| Relicense-compatible | **RESOLVED 2026-07-30 (E23-ruling; BOUNCE #1 corrections applied 2026-07-30 — outcome unchanged), for the population that ships — NOT the same posture as AIAAIC's E13 question, and this asymmetry is now explained rather than merely asserted.** `docs/audits/E23-aiid-marking-ruling-2026-07-30.md` finds AIID's maker (Responsible AI Collaborative, Inc.) is a **US-situated entity** — principal place of business, venue, and arbitration all in Los Angeles, California, per its own Terms of Use, and US federal tax-exempt status (EIN 88-1046583, `incidentdatabase.ai/about/`); a specific state of incorporation is **not** stated on any AIID-controlled page and is **not material** to this analysis, since no US state satisfies the UK/EU database-right tests below. Two independent, reinforcing reasons follow: **(1) Copyright** — U.S. Circular 33 categorically excludes titles/short phrases from protection, unlike UK/EU law (which is why AIAAIC's parallel headline question, E15/D17, stayed open); the connecting factor is AIID's own **situs**, mirroring E13's method exactly, not AIID's Terms-of-Use choice-of-law clause (which cannot itself supply a copyright rule — US copyright is exclusively federal). **(2) Database right** — applying E13 §4.1's own maker-qualification gate (built for genai_incidents' own qualification) to AIID's maker instead: a US-situated body fails both reg 18(1)/(2)'s UK-nexus test and Directive 96/9/EC Art 11's EEA-nexus test, so **no UK or EU sui generis database right subsists in AIID's collections at all**, regardless of investment — a cleaner result than AIAAIC's, where the UK maker plausibly *does* qualify and the question stays open. **Attribution is separately confirmed adequate**, on the measured population — 1,463–1,464 of 1,465 shipped AIID rows name "AI Incident Database (AIID)" and link to the source entry; the two exceptions ship no AIID text and so owe no AIID attribution. **Scope limit, not a blanket clearance:** this resolution covers only the ~1,463-row population that actually ships (the sanctioned-snapshot path). It does **not** cover `ingest/aiid_incidents.json`'s 63 hand-curated rows or the 1,457 AIRI-Navigator rows sharing AIID's source-ID convention — both carry uncleared risk (paraphrased titles, narrative descriptions of unverified provenance) and are kept out of the shipped corpus only by current merge-order mechanics, not a compliance design. **Tripwire:** if a future pipeline/merge change ever causes that population's own text to reach `data/incidents.json`, this resolution does not carry over — that population reopens for its own review before it ships. See the ruling file for the full layer-by-layer reasoning, including the correction log at its top. |
| Action | **RESOLVED 2026-07-30 (E23-ruling) for the shipped population — no row-level `content_license` marker required, on the reasoning above.** No LICENSE-DATA carve-out added for AIID (parallel to AIAAIC's D2 outcome), and none is needed — the marker exists to hedge a share-alike/database-right exposure this population does not carry, not to hedge one that was merely reduced. `NOTICE-DATA` and `.reuse/dep5` **used to** describe AIID's exposure as "the same class of open question"/"same posture" as AIAAIC's E13 finding — **that framing was false and was CORRECTED on both surfaces 2026-07-30 (`7c4b4394`, gated PASS)** (exact content specified in the ruling file's "What NOTICE-DATA / .reuse/dep5 owe" section; not drafted here, out of this row's scope). The v2.9.0 release notice's AIID scope caveat is likewise owed an update from "open question under review" to "resolved, with a named tripwire" — see the ruling file §6. Invariant 3 (never silently drop a previously-present entry) verified for the original 2026-07-18 swap: 0 corpus IDs removed, see the delta report — unaffected by this update. |
| Date-checked | 2026-07-18 (acquisition method); 2026-07-30 (content-licensing question resolved, E23-ruling — see `docs/audits/E23-aiid-marking-ruling-2026-07-30.md`) |

### 1.3 AI Incident Database (AIID) — via AIID's own repo data file
*Ingested by:* `scripts/ingest_external.py::ingest_aiid_oecd_bridge()` (reads
`_external/aiid/site/gatsby-site/migrations/data/oecd_relationships_2025_09_09.json`,
a file from AIID's own cloned GitHub repo) and `scripts/scrape_aiid.py`'s
`load_aiid_urls()` (same file, used only to enumerate IDs) plus two
`_external/sitemap-*.xml` files.

| Field | Value |
|---|---|
| License | Same rights-holder as §1.2 (AIID / Responsible AI Collaborative). The `responsible-ai-collaborative/aiid` GitHub repo's own code-license field returns `"Other"`/`NOASSERTION` via the GitHub API (fetched 2026-07-15) — no plain LICENSE file at `main` (404 on the raw URL). This governs the *site's code*, not necessarily this specific data file, whose content (AIID-incident-ID ↔ OECD-URL pairs) is a factual mapping table, not creative expression. |
| Scrape-permitted | N/A — local git clone of a public repo, not a live fetch. |
| Redistribute-verbatim | The mapping itself (ID + URL pairs) is treated as facts, not copyrightable expression — low risk. The *synthesized description* the ingest writes (`"Cross-listed in the AI Incident Database (AIID) as incident #{id} and tracked by the OECD AI Incidents Monitor..."`) is original text, not copied. |
| Relicense-compatible | Compatible for the ID/URL facts and the original description sentence. |
| Action | (a) compatible, low risk. No change required beyond noting the repo's own unclear code license doesn't cover a bare facts file we already treat conservatively. |
| Date-checked | 2026-07-15 |

### 1.4 MIT FutureTech AIRI Navigator
*Ingested by:* `scripts/ingest_airi_navigator.py` (downloads
`airi-navigator.com/downloads/airi-data.zip`).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY 4.0**, established one hop away from AIRI Navigator itself. AIRI Navigator's own pages were re-tested a second time on 2026-07-16 by raw-HTML substring search (not a rendered or summarizing fetch) across the home page (198,546 bytes), /about (96,530 bytes), and all 23 /about and 27 /datasets JS bundles, for "cc by", "creative commons", "licen[cs]e", and "by-sa" — zero hits everywhere. That negative finding is genuine: these are small, low-content pages, so the truncation mechanism that produced the AIAAIC false negative doesn't plausibly apply, and this check confirms that directly rather than by inference. The license lives one hop away, at the source AIRI Navigator names as its own: its Terms-of-Use modal (the text lives only inside a bundled JS file, so a rendered HTML fetch of the page never surfaces it) states that the data presented on the site is drawn from the MIT AI Risk Repository at airisk.mit.edu and related research datasets, and points users to that database page for more information. Following that named source: airisk.mit.edu returned HTTP 200, 112,503 bytes of raw HTML, whose footer (a Webflow embed div) reads: "Website copyright MIT FutureTech 2026. Data from the MIT AI Risk Initiative is licensed under CC BY 4.0," linking to creativecommons.org/licenses/by/4.0. This is corroborated independently by that same page's own JSON-LD metadata, whose publishing-principles field points to the identical creativecommons.org/licenses/by/4.0 URL. Verification: raw-HTML fetch, cross-checked independently by two parties (red-reviewer and the foreman) on 2026-07-16. This transcription did not involve any new fetch against airisk.mit.edu or airi-navigator.com; the facts above were handed over already shell-verified per the board's WS0-T1 close-out brief (decision D3). |
| Scrape-permitted | airi-navigator.com's own robots.txt returned HTTP 200 with a permissive rule set: all user agents allowed at the root, with five paths disallowed — /embed/, /admin, /login, /design-system, and /api/. Terms of Use is the modal quoted above, and it is real operative text, not merely the data-quality caveat this row previously described. The /api/ disallow is the one restriction worth flagging: even if an API existed for this data, scraping it would not be conduct-compliant; it does not cover the ZIP-download path (see Action below for that path's current status). |
| Redistribute-verbatim | Compatible for AIRI Navigator's own data under the confirmed CC BY 4.0 grant, with attribution. Remains **UNKNOWN** specifically for the AIID-derived fields the tool wraps — see Relicense-compatible. |
| Relicense-compatible | Compatible for AIRI's own CC BY 4.0 data with attribution. **UNKNOWN** only for whether AIID's CC-BY-SA share-alike (Section 1.2) applies transitively to the AIID-derived fields AIRI Navigator wraps — a wrapper's own license cannot grant away an upstream share-alike obligation it doesn't itself hold. |
| Action | **(d) UNKNOWN, narrowed.** AIRI Navigator's own license is now established as CC BY 4.0 (see License above). What remains open is only the transitive-AIID-share-alike question. Outreach is redrafted accordingly: it now asks the AIRI Navigator maintainer (Spencer Michaels, contact given on the AIRI site) only about the AIID-derived-fields question, not about AIRI's own license, which the footer at airisk.mit.edu already answers. Separately, and independent of licensing: the ZIP download this ingest relies on (airi-navigator.com/downloads/airi-data.zip, the ZIP_URL constant in scripts/ingest_airi_navigator.py) now returns HTTP 404 with zero bytes, checked on both hosts with a browser user agent and referer header on 2026-07-16. The site's own source ties the download link's rendering to a feature-flag comparison that currently evaluates false, so the withdrawal looks deliberate on MIT FutureTech's part rather than an accidental move of the file. Cross-reference WS4-T9 / E6, which independently found this ingest currently non-functional. This source produces no data until that separate, non-licensing problem is fixed. |
| Outreach date | **Sent — two distinct messages, not one.** `docs/outreach/mit-airi-courtesy.md` (dead-ZIP courtesy notice + informal transitive-AIID question, to Spencer Michaels via airi-navigator.com) sent **2026-07-27**. `docs/outreach/airi-draft4-export-request.md` (substantive sanctioned-export/API request + the same transitive-AIID question stated more precisely, to `airisk@mit.edu`) sent **2026-07-29**. docs-warden finding N7 adjudicated these as distinct sends, not a resend of the same message — see that file's "Relationship to `docs/outreach/mit-airi-courtesy.md`" note. The "2026-07-16 (redrafted; not yet sent)" this row previously carried is stale, superseded by both sends above. |
| Follow-up date | **D8's 30-day AIRI-hold clock keys to the 2026-07-29 `airi-draft4-export-request.md` send, not the 2026-07-27 courtesy send.** Decision point: MIT's reply, or **2026-08-28**, whichever comes first — at that point D8's deferred retire-or-replace decision for AIRI becomes live. |
| Date-checked | 2026-07-16 |

### 1.5 OECD AI Incidents and Hazards Monitor (AIM)
*Ingested by:* `scripts/ingest_oecd_aim.py` (scrapes `oecd.ai/en/incidents/<id>`
pages via their embedded Angular `ng-state` JSON).

| Field | Value |
|---|---|
| License | Split. General OECD terms (`oecd.org/en/about/terms-conditions.html`) apply to OECD's *own* IP: *"Except where additional restrictions apply as stated above, you can extract from, download, copy, adapt, print, distribute, share and embed Data for any purpose, even for commercial use,"* conditioned on attribution (cite per the source's own citation format, or `OECD (year), (dataset name), (data source) DOI or URL (accessed on (date))`), with the same acknowledgment requirement passed through to any sub-licensees. Separately, **OECD written content published from 1 July 2024 onward defaults to CC BY 4.0** (the copyright/front-page of a given piece states whether a CC license applies and which one). **Re-fetch caveat:** this page still returned HTTP 403 to my direct automated fetch on 2026-07-15 (tried twice, both `https://` and `http://`) — both quotes above are corroborated across two independent web searches rather than a direct 200 read, which is a step up in confidence from the earlier single-cached-excerpt version of this row but still short of a primary-source fetch. **Still true as of 2026-07-30 (E21):** every OECD general-terms page tried that day (`terms-conditions.html`, `/termsandconditions/`, the open-access-policy page, the July-2024 press release) 403'd via WebFetch; `web.archive.org` is unreachable to this project's tools entirely; this fact remains corroborated by independent web search, not primary-source quoted. The AIM-specific methodology page (`oecd.ai/en/incidents-methodology`, fetched 2026-07-15, direct 200) explicitly disclaims: *"Any of the copyrights, trademarks... included in the AIM are the property of their respective owners"* — meaning the incident narrative text (drawn from aggregated third-party news articles) is **not OECD's to relicense**, and by extension not ours, regardless of which general-terms regime applies to OECD's own content. **Two facts added 2026-07-30 (E21, `docs/audits/E21-oecd-narrative-licence-2026-07-30.md`), both direct WebFetch reads of the same methodology page, HTTP 200:** (1) AIM explicitly says it is subject to the general terms — *"Your use of the OECD AI incidents and hazards monitor (previously AI Incidents Monitor) ("AIM") is subject to the terms and conditions found at www.oecd.org/termsandconditions"* — so the split above genuinely reaches AIM, not just OECD generally. (2) **Decisive: `title`/`summary`/`harm_type`/`severity`/`affected stakeholders`/`country` are not OECD-authored prose and not quoted news text — they are machine output:** *"Each event is enriched with relevant metadata, including an event title, summary, the harm type, severity, affected stakeholders, and the country where it occurred, among others. This metadata is LLM-generated (OpenAI's o3-mini) from the top three articles of each event, selected from different news outlets."* This disproves the "composed OECD editorial abstract" hypothesis this row carried between 2026-07-30's two revisions on the same day, and puts `description`'s actual provenance in a third category (LLM output derived from copyrighted third-party news, ownership unresolved) that E21 finds genuinely ambiguous under Layer 3 of its analysis — see that file §3 for the full reasoning, including a fair statement of the counter-reading. |
| Scrape-permitted | `oecd.ai/robots.txt` (fetched 2026-07-15, re-confirmed unchanged 2026-07-30 — same five rules) disallows only French-language sections (`/fr/community/`, `/fr/catalogue/`, `/fr/wonk/`, `/fr/dashboards/`, `/fr/data`) — no rule blocks `/en/incidents/`. No explicit rate limit stated by OECD. **Correction (2026-07-30):** the ingest now does route through the WS0-T4 common rate-limiter — `scripts/ingest_oecd_aim.py` imports `fetch_once`/`robust_fetch` from `ingest/common.py` (verified by direct code read) and its 10-worker pool queues through that module's shared per-host limiter (see §5, below); the "should route through... but [doesn't yet]" wording this row previously carried is stale, superseded by the WS0-T4 network-chokepoint migration (`8b1e8888`). **New, unresolved flag (2026-07-30):** the sitemap URL `oecd.ai/sitemaps/incident-monitor-sitemap.xml` — the exact URL `SITEMAP_URL` fetches — 302-redirects to a different host, `incidents-server.oecdai.org` (confirmed live via WebFetch). `robots_allowed()`/`_rate_limit()` in `ingest/common.py` key off the *original* URL's host (`oecd.ai`), and `urllib`'s automatic redirect-following means the bytes actually served come from a host whose own robots.txt is never checked. Whether individual `/en/incidents/<id>` pages redirect the same way is a shell-level question WebFetch could not resolve reliably; see the exact check named in the report for red-reviewer. |
| Redistribute-verbatim | **NO for `description` — RE-AFFIRMED 2026-07-30 (E21) on a corrected rationale.** Not because it is quoted third-party news copy (E21 disproves that: the `evidences` fallback fires on 0/4,160 rows, and `summary` doesn't appear in the evidences blob) but because `summary` (100% of shipping `description` text) is **LLM-generated (OpenAI o3-mini) from the top three source articles per event** — machine output derived from copyrighted third-party news, of genuinely ambiguous ownership, that OECD's own methodology-page disclaimer plausibly (not certainly) still reaches. E21 resolves this ambiguity conservatively per this document's own standing rule; see `docs/audits/E21-oecd-narrative-licence-2026-07-30.md` §3 for the full two-sided analysis. **`title` carries the identical open question** (generated by the same LLM call, same sentence) but is tracked separately, not folded into this NO — same posture as AIAAIC's retained-headline question (§1.1, E15/D17): lower per-item risk (a short label, not a multi-sentence digest), not resolved here. **Implemented and merged (2026-07-30, `6f06eaeb`):** `build_description()` in `scripts/ingest_oecd_aim.py` ships only a templated structural sentence (source id, date, named entities, classified attack vector, the AIM page link) and never `summary`/`evidences` — verified by direct code read. This finding is no longer a requirement pending code; the shipped `description` field already complies with it. |
| Relicense-compatible | Compatible for OECD's own structural data (incident IDs, dates, AIID cross-reference IDs, taxonomy tags, the `affected`/company list) under OECD's general Data-reuse terms. **Attribution implemented and merged (2026-07-30, E21 §5.3, `6f06eaeb`)** — the OECD-specific citation format `OECD (year), (dataset name), (data source) DOI or URL (accessed on (date))` is now emitted, as `OECD (<year>), AI Incidents and Hazards Monitor, <url> (accessed on <date>)`, on every one of the 3,829/3,829 OECD-AIM-sourced rows, plus 368 further entries whose only OECD-AIM content was absorbed into an AIID entry during merge but which still carry an `oecd.ai` page reference via the AIID-OECD bridge path (4,197 entries / 4,755 citation-shaped references total) — see `docs/audits/E21-5.3-oecd-attribution-2026-07-30.md` for the measurement. The "with attribution not yet implemented" / "no such string is emitted anywhere in this ingest today" wording this cell previously carried is **false as of `6f06eaeb`** and is corrected here, not merely softened. **Not compatible** for `description` (summary-derived narrative text), per Redistribute-verbatim above. |
| Action | **(b) — RESOLVED 2026-07-30 (E21) and IMPLEMENTED 2026-07-30 (merged `6f06eaeb`).** `docs/audits/E21-oecd-narrative-licence-2026-07-30.md` was commissioned specifically to test whether the "composed OECD abstract, may be CC-BY-4.0-governed" hypothesis this row carried (added earlier 2026-07-30) voided the reduction requirement. It does not: that hypothesis is disproven (`title`/`summary` are not OECD staff prose — they are **LLM-generated, OpenAI o3-mini, from the top three source articles per event**, per AIM's own methodology page) and the reduction was required, on the sharper rationale that this is machine output derived from copyrighted third-party news of unresolved ownership, resolved conservatively per this document's own standing rule. **`description` is reduced to structural facts + link** (source_id/date/affected/attack_vector/url only, never `summary`/`evidences`) — implemented in `build_description()`, `scripts/ingest_oecd_aim.py`, mirroring the in-repo precedent it copies (`ingest_external.py::ingest_aiid_oecd_bridge()`); verified by direct code read. **OECD attribution per entry is implemented** (`OECD (year), AI Incidents and Hazards Monitor, url (accessed on date)` format, E21 §5.3), reaching 3,829/3,829 OECD-AIM-sourced rows plus 368 AIID-bridge entries — see `docs/audits/E21-5.3-oecd-attribution-2026-07-30.md`. **`title` remains a separate, narrower open question** (same LLM pipeline, same sentence, lower per-item risk) — tracked at the same posture as AIAAIC's E15/D17 headline question, and was **not** put in this reduction's scope; the reduction above does not resolve `title`. **History was not rebuilt** — per D10's fix-forward precedent, this landed as a one-off **local transform** of the already-committed `ingest/oecd_aim_full_incidents.json` (E21 §5.4, revised after BOUNCE #1), reaching the 40 rows that have aged out of the current sitemap and can never be re-fetched by any limit setting, without the ~167-minute cold-cache re-ingest a full `OECD_AIM_LIMIT=0` re-fetch would require. **`corpus` protection from silent relabelling (E21 §5.1) is implemented as a decoupling, not the fallback-delta path:** `classify_corpus_signal()` in `scripts/ingest_oecd_aim.py` (verified by direct code read, lines 188–209) computes `corpus` from the same pre-reduction narrative seed and the identical keyword lists `merge_and_dedupe.py::_classify_corpus()` uses — imported, not duplicated, per that function's own docstring — so the persisted value matches what the merge-time classifier would have produced from the old wholesale `description`, byte for byte. The measured delta (target: 0 unintended `corpus` moves) is recorded in the E21 gate's own verdict, not restated here to avoid drift — red-reviewer or the gate transcript is the check to consult for the actual count. Outreach (`docs/outreach/oecd-aim-terms.md`) is unaffected by this resolution — it still asks OECD to confirm the terms and point to a bulk channel, and **remains drafted, not sent** (verified against `docs/outreach/README.md`, 2026-07-30). |
| Outreach date | **SENT 2026-07-31** to `ai@oecd.org` (user-confirmed, logged 2026-07-31) — the fourth and last of this project's outreach recipients, closing WS0-T4's outreach obligation at 4 of 4. *The E20 record of what this cell previously carried is preserved below, because it is the record of a correction, not merely a stale value:* **No draft existed until 2026-07-30 — the "2026-07-15 (drafted; not yet sent)" this row previously carried was false.** Verified 2026-07-30: `git log --all --diff-filter=A -- 'docs/outreach/*'` returns the complete set of outreach files ever committed to this repo (`aiaaic-correction.md`, `aiaaic-facts-link.md`, `aiid-goodwill.md`, `airi-draft4-export-request.md`, `annotator-recruitment.md`, `mit-airi-courtesy.md`, `README.md`) — no OECD file among them, confirming no such artifact ever existed on any branch (E20, 2026-07-29 — one of now seven confirmed instances of the E18 chat-only-deliverable pattern). A genuine draft, `docs/outreach/oecd-aim-terms.md`, was written to disk 2026-07-30 and is drafted, awaiting red-reviewer and the user's send — not sent as of this writing. |
| Follow-up date | **2026-08-21** — 21 days from the 2026-07-31 send, matching this file's other outreach items. If OECD has not replied by then, the follow-up is the user's to send. **Note what this clock does and does not gate:** it tracks the *terms question* (whether AIM's own structured data may be reused, and whether a sanctioned bulk channel exists). It does **not** gate the E21 reduction or the §5.3 attribution — both are implemented and merged, and were deliberately built to be correct without a reply. |
| Date-checked | 2026-07-15 (fact — general OECD terms + AIM methodology-page substance); 2026-07-30 (OECD terms page re-fetched — still HTTP 403, and now confirmed **not** UA-conditional: foreman-measured across four client/UA combinations (`urllib` with this project's own UA and with a browser UA, `curl` with a browser UA and with no UA) — 403 to every one, with small varying error-page bodies consistent with bot protection, not a selective block. By this measurement a primary-source fetch of the general terms page remains genuinely unavailable, not merely inconvenient — the License cell's existing "still short of a primary-source fetch" hedge stands, unweakened. AIM methodology page re-fetched — 200, and the exact 2026-07-15 quoted string is now **confirmed present verbatim in raw HTML, twice** (red-reviewer, `curl`, 2026-07-30); my own 2026-07-30 WebFetch-based re-check could not confirm the exact string and flagged that as a likely tool-summarization limitation rather than a page change — confirmed correct: the page did not change. The sitemap-redirect finding is narrower than first flagged: individual `/en/incidents/<id>` pages do **not** redirect off-host (7/7 probes 200, 0 redirects — red-reviewer/foreman, 2026-07-30); only the sitemap URL itself redirects, so the robots-verification gap this flags is a 1-fetch-per-weekly-run exposure, not a per-incident one); **2026-07-30 (E21, second pass same day)** — OECD general-terms pages re-tried (4 distinct URLs via WebFetch: `terms-conditions.html`, `/termsandconditions/`, the open-access-policy page, the July-2024 press release) — all four 403; `web.archive.org` unreachable to this project's tools; AIM methodology page re-fetched a third time (WebFetch, 200) and yielded two facts new to this row — AIM's explicit self-incorporation of the general terms, and the LLM-generation (o3-mini) mechanism behind `title`/`summary` — full detail and the resulting Redistribute-verbatim/Action revisions in `docs/audits/E21-oecd-narrative-licence-2026-07-30.md` |

---

## 2. Vulnerability / advisory sources

### 2.1 CISA Known Exploited Vulnerabilities (KEV) catalog
*Ingested by:* `scripts/ingest_cisa_kev.py` (fetches
`cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`).

| Field | Value |
|---|---|
| License | **CC0 1.0** confirmed via the community/CISA-adjacent mirror `cisagov/kev-data` LICENSE file (fetched 2026-07-15): *"The KEV database is distributed under the Creative Commons 0 1.0 License. You may use this data in any legal manner..."* Independently, as a work of the U.S. federal government, KEV content is not subject to domestic copyright (17 U.S.C. §105) regardless. The catalog JSON itself (fetched 2026-07-15) carries no license field in its metadata, but this is consistent with public-domain status rather than a gap. |
| Scrape-permitted | **YES** — the URL is CISA's own published machine-readable feed, designed for exactly this consumption. |
| Redistribute-verbatim | **YES.** |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

### 2.2 National Vulnerability Database (NVD)
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 1 — NVD REST API
2.0 keyword search).

| Field | Value |
|---|---|
| License | CVE/NVD records are U.S. government work (public domain domestically), but the NVD API imposes contractual usage terms independent of copyright: `nvd.nist.gov/developers/terms-of-use` (fetched 2026-07-15) requires a displayed notice — *"This product uses the NVD API but is not endorsed or certified by the NVD"* — states *"If you modify the content accessed through the API, you may not attribute the source as the NVD,"* and restricts API keys to the original requestor ("Keys should not be used by, or shared with, individuals or organizations other than the original requestor"). |
| Scrape-permitted | **YES, within stated rate limits** — 5 req/30s unauthenticated, 50 req/30s with an API key; the ingest script already paces requests accordingly (`NVD_SLEEP`). |
| Redistribute-verbatim | **YES** for unmodified content (public domain). Modified/derived text must not be presented as if it were still NVD's own text. |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible, with one compliance gap:** the required attribution notice above is not displayed anywhere in this repo's docs, README, or site. See the exact remediation requirement in the report. |
| Date-checked | 2026-07-15 |

### 2.3 GitHub Security Advisory Database (GHSA)
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 2 — `gh api graphql`
against `securityAdvisories`, both `GENERAL` and `MALWARE` classifications).

| Field | Value |
|---|---|
| License | **CC-BY 4.0**, confirmed via `github/advisory-database` repo (fetched 2026-07-15): *"This project is licensed under the terms of the CC-BY 4.0 open source license."* |
| Scrape-permitted | **YES** — accessed via GitHub's official authenticated GraphQL API (`gh api graphql`), not scraping. |
| Redistribute-verbatim | **YES**, with attribution. |
| Relicense-compatible | **YES** — CC-BY 4.0 is directly compatible with this project's CC-BY relicense (no share-alike conflict). |
| Action | **(a) compatible.** Confirm the render layer credits "GitHub Advisory Database" per entry (GHSA ID + link is already present in `references`). |
| Date-checked | 2026-07-15 |

### 2.4 OSV.dev
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 3 — `api.osv.dev/v1/query`
against the `OSV_TARGETS` list of PyPI, npm, and Go-ecosystem packages).

| Field | Value |
|---|---|
| License | OSV.dev is an **aggregator**; the *code* (`google/osv.dev` repo, fetched 2026-07-15) is Apache-2.0, but individual **records carry their originating database's license**, per `google.github.io/osv.dev/data/` (fetched 2026-07-15): PyPI Advisory Database = **CC-BY 4.0**, GitHub Advisory Database = **CC-BY 4.0**, Go Vulnerability Database = **CC-BY 4.0** (confirmed separately at `vuln.go.dev/copyright`, fetched 2026-07-15: *"licensed under the Creative Commons Attribution 4.0 License"*). **OSV aggregates databases under different licences, and not all are CC-BY 4.0.** The same data page lists "OpenSSF Malicious Packages (Apache 2.0)" beside "GitHub Advisory Database (CC-BY 4.0)", and the `ossf/malicious-packages` repo licence is Apache-2.0 (GitHub API). Its records carry `MAL-` ids; both committed examples are PyPI packages (MAL-2026-3607, guardrails-ai; MAL-2026-2144, litellm). **Handling: MAL- records are excluded from the OSV path by scripts/ingest_cve_nvd_expanded.py::is_openssf_malicious (id/alias prefix MAL- or an ossf/malicious-packages source marker). The two committed MAL rows were purged by scripts/audit/purge_openssf_mal.py: MAL-2026-2144 dropped; MAL-2026-3607 kept as a bare identifier only (id, OSV template title, affected package, tags, reference links; description replaced by an original sentence) because it holds INC-08450 together (board N7). No OpenSSF report text is kept, so no Apache-2.0 notice is added.** Of the other databases reachable via `OSV_TARGETS`, PyPI, GitHub and Go are CC-BY 4.0 as stated above. *Correction note (2026-10-03):* an earlier version of this cell said "every source database actually reachable by this script is CC-BY 4.0"; that was false. It was found by the tranche-1 gate (`docs/audits/source-expansion-tranche1-gate1-verdict-2026-10-03.md`, Part 2 "OSV ADVISORY"), which also measured that the committed `ingest/cve_nvd_expanded.json` holds 2 `MAL-` records (MAL-2026-3607, MAL-2026-2144) with verbatim OpenSSF report text, and that the published `data/incidents.json` carries no MAL text. |
| Scrape-permitted | **YES** — official public API designed for this query pattern. |
| Redistribute-verbatim | **YES**, with attribution to the specific originating advisory database (not just "OSV"). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible for CC-BY 4.0 origins only; `MAL-` (OpenSSF, Apache-2.0) records are excluded.** Ensure per-entry attribution names the originating DB (e.g. "PyPI Advisory Database via OSV.dev"), not just "OSV," since that's whose license actually applies. |
| Date-checked | 2026-07-15 |

---

## 3. Attack-capability / taxonomy sources

### 3.1 MITRE ATLAS
*Ingested by:* `scripts/ingest_external.py::ingest_atlas()` (parses
`_external/atlas-data/dist/v6/ATLAS-2026.06.yaml`, a git-cloned public repo).

| Field | Value |
|---|---|
| License | **Apache License 2.0**, confirmed via `mitre-atlas/atlas-data` LICENSE file (fetched 2026-07-15): *"Copyright 2021-2026 MITRE. Licensed under the Apache License, Version 2.0."* |
| Scrape-permitted | N/A — local clone of a public repo. |
| Redistribute-verbatim | **YES** under Apache-2.0 terms (case-study titles/descriptions are reproduced from the dist YAML). |
| Relicense-compatible | **YES, with a carve-out.** Apache-2.0 does not require share-alike, but it does require preserving the copyright/license notice on the covered material — MITRE's Apache-2.0 notice must stay attached to ATLAS-derived case-study text specifically; it cannot be silently folded into a blanket "CC-BY-4.0, all rights reserved by us" claim. |
| Action | **(a) compatible**, but the repo's licensing docs (LICENSE-DATA / this file) must state the ATLAS-derived carve-out explicitly — this is a direct input to WS0-T2. |
| Date-checked | 2026-07-15 |

### 3.2 CSET-AIID Harm Taxonomy
*Ingested by:* `scripts/ingest_external.py::ingest_cset()` (checks for the
presence of `_external/CSET-AIID-harm-taxonomy` and, if present, writes
**one** original reference entry describing the taxonomy — no data is
extracted from the repo's own files).

| Field | Value |
|---|---|
| License | **UNKNOWN / none granted.** GitHub API for `georgetown-cset/CSET-AIID-harm-taxonomy` (fetched 2026-07-15) returns `"license": null` — no LICENSE file, meaning default all-rights-reserved copyright applies. **Method note (added 2026-07-16):** this finding comes from the GitHub REST API's structured `license` JSON field, not a WebFetch of a rendered HTML page — small, fixed-shape JSON, not subject to the page-length/markdown-conversion failure mode that produced the AIAAIC miss. I did not additionally re-check via a raw `curl` of the repo's file tree (no shell access); red-reviewer can confirm with `gh api repos/georgetown-cset/CSET-AIID-harm-taxonomy --jq .license` if a second check is wanted. |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | **NO** (no permission granted) — moot in practice, since the current code does not copy any of the repo's actual content; it writes one original, hand-authored description of what the taxonomy is, with a link. |
| Relicense-compatible | **NO** for repo content generally; the single original description sentence we write ourselves is fine. |
| Action | **RESOLVED (2026-07-30, E20) — reduces to (a) compatible for current scope; no outreach owed.** No code change required: the ingest takes no verbatim content from the CSET-AIID repo — `ingest_external.py::ingest_cset()` writes exactly one original, hand-authored reference-entry description plus a link (see Redistribute-verbatim, above), which is unaffected by the repo's own unclear/no-license status. **Condition, not a permanent closure:** if CSET-derived entries in this corpus ever grow beyond that single hand-authored reference (any code change that extracts more than a link + original description from `_external/CSET-AIID-harm-taxonomy`), this row **REOPENS as (d) UNKNOWN** and outreach must be drafted and sent *before* that ingest expansion ships, not after. Per the user's ruling (E20, 2026-07-29): drafting an email to ask permission the project does not currently need would satisfy this cell rather than answer a real question; this tripwire is the deliberate substitute. |
| Outreach date | **No draft ever existed; none is owed under current scope.** Verified 2026-07-30: `git log --all --diff-filter=A -- 'docs/outreach/*'` returns the complete set of outreach files ever committed to this repo — no CSET file among them. The "2026-07-15 (drafted; not yet sent)" this row previously carried described an artifact that never existed on any branch (E20, 2026-07-29 — one of now seven confirmed instances of the E18 chat-only-deliverable pattern). Outreach is deferred to the tripwire condition in Action, above, not owed today. |
| Date-checked | 2026-07-15 (License fact, GitHub API); 2026-07-30 (this row's outreach-status correction, E20) |

### 3.3 NVIDIA garak
*Ingested by:* `scripts/ingest_external.py::ingest_garak()` (reads probe
`.py` files under `_external/garak/garak/probes/` and extracts each probe's
module docstring).

| Field | Value |
|---|---|
| License | **Apache License 2.0**, confirmed via `NVIDIA/garak` LICENSE file (fetched 2026-07-15). Copyright held by Leon Derczynski (2023) and NVIDIA Corporation & Affiliates (2023). |
| Scrape-permitted | N/A — local clone of a public repo. |
| Redistribute-verbatim | **YES under Apache-2.0**, but note this is the one source in this file where verbatim reproduction is *actually happening*: `ingest_garak()` copies each probe's docstring text directly into our `description` field (`"NVIDIA garak LLM vulnerability scanner probe `{probe_name}`. " + desc`). Apache-2.0 permits this, conditioned on preserving the copyright/license notice for the reproduced material. |
| Relicense-compatible | **YES, with the same carve-out as ATLAS (§3.1)** — garak-derived descriptions remain under Apache-2.0 attribution, not folded into a blanket CC-BY claim. |
| Action | **(a) compatible**, but needs an explicit NOTICE/attribution carve-out in LICENSE-DATA (WS0-T2 input) naming garak-derived entries specifically. |
| Date-checked | 2026-07-15 |

### 3.4 promptfoo
*Ingested by:* `scripts/ingest_external.py::ingest_promptfoo()` (extracts
plugin/strategy ID strings from `_external/promptfoo/src/redteam/constants/*.ts`;
writes original descriptions, not copied source text).

| Field | Value |
|---|---|
| License | **MIT**, confirmed via `promptfoo/promptfoo` LICENSE file (fetched 2026-07-15). |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | Not attempted — descriptions are original ("promptfoo red-team {kind} `{pid}`. Defines an automated test for this attack class..."), not copied from source. MIT would permit verbatim reuse anyway (with notice retained). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

### 3.5 ModelOriented/CVE-AI (curated CVE list)
*Ingested by:* `scripts/ingest_external.py::ingest_cve_ai_curated()` (reads
CSV/JSON export files from `_external/CVE-AI`, copying `title`/`description`
fields into our schema).

| Field | Value |
|---|---|
| License | **MIT**, confirmed via `ModelOriented/CVE-AI` repo footer license badge (fetched 2026-07-15). |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | **YES** under MIT, with attribution (already present via the reference link to the GitHub repo). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

---

## 4. Academic red-team benchmarks (hand-curated citations)

*Ingested by:* `scripts/ingest_redteam_benchmarks.py` — the script's own
docstring states this is *"a hand-curated, citation-backed list (no
scraping)."* Each `BENCHMARKS` tuple is an **original, hand-written
description** (benchmark size, harm categories, venue) with citation links;
no paper abstract or benchmark prompt data is scraped or copied verbatim.
That fact is the load-bearing compliance point for every row below: facts
about a published benchmark (size, categories, venue) are not copyrightable
expression, and none of these entries reproduce the papers' actual text.

Two of the ten linked code repositories were independently checked; the
other eight were **not** — flagged explicitly rather than guessed, since
none of them currently matter for compliance (no verbatim/code reuse occurs).

| Benchmark | Paper venue/license | Code repo license | Verified? |
|---|---|---|---|
| JailbreakBench | arXiv (2404.01318) | jailbreakbench.github.io | Not verified |
| HarmBench | arXiv (2402.04249) | harmbench.org | Not verified |
| AdvBench / llm-attacks | arXiv (2307.15043) | **MIT** (confirmed, `llm-attacks/llm-attacks` LICENSE, fetched 2026-07-15) | Code verified |
| AgentHarm | arXiv (2410.09024) | (no repo cited in our ingest) | Not verified |
| AgentDojo | arXiv (2406.13352) | **MIT** (confirmed, `ethz-spylab/agentdojo` LICENSE, fetched 2026-07-15) | Code verified |
| InjecAgent | arXiv (2403.02691) | (no repo cited in our ingest) | Not verified |
| OS-Harm | arXiv (2506.14866) | (no repo cited in our ingest) | Not verified |
| HackAPrompt | arXiv (2311.16119) | (no repo cited in our ingest) | Not verified |
| StrongREJECT | arXiv (2402.10260) | (no repo cited in our ingest) | Not verified |
| SafetyPrompts.com | arXiv (2404.05399) | safetyprompts.com | Not verified |

| Field | Value |
|---|---|
| License (papers) | All ten cite arXiv preprints. arXiv's non-exclusive distribution license (`info.arxiv.org/help/license/`, fetched 2026-07-15) is explicit that it is **"perpetual, non-exclusive"** to arXiv only and **"limits re-use of any type from other entities or individuals"** — i.e. arXiv's license does **not** grant us any reuse right over the papers' text. This is why the ingest script must never copy verbatim abstract/paper text — and, per the code read above, it currently doesn't. |
| Scrape-permitted | N/A — no scraping occurs; this is a hand-authored, hardcoded Python list. |
| Redistribute-verbatim | **NO, and not attempted.** Only original summary sentences + citation links are stored. |
| Relicense-compatible | **YES** for our own original summary sentences (our copyrightable expression). **NOT established** for the underlying datasets (actual jailbreak/attack prompt sets) — those are untouched today and must stay that way absent a fresh per-benchmark check. |
| Action | **(a) compatible as currently implemented**, with a hard guardrail for any future change: **never extend this ingest to copy verbatim abstract text or the underlying benchmark's raw prompt/behavior data without a fresh, per-benchmark license check.** See the exact requirement in the report. |
| Date-checked | 2026-07-15 |

---

## 5. Not a source (helper module)

`ingest/common.py` (formerly `scripts/ingest_utils.py` — promoted and
relocated during WS0-T4) provides `fetch_once()`, `robust_fetch()`, and
`conditional_fetch()`. It pulls no upstream content of its own and gets no
row here. It is no longer just a shared HTTP retry/caching helper: as of
`8b1e8888` it is this repo's **sole HTTP(S) network chokepoint** and the
subject of now-**ACTIVE invariant 5** (`MASTER_IMPROVEMENT_PLAN.md`) — every
live `ingest_*.py`/`scrape_*.py` fetch is required to route through it. What
it enforces per request — an identifying User-Agent, a fail-closed
robots.txt check, per-host rate limiting, and retry/backoff — is a conduct
question, not a per-source license question, so it is described and
evidenced in `docs/INGESTION_CONDUCT.md`, the authoritative doc for that
policy, rather than restated here.

---

## 6. Source-expansion waves 1-2 (user-approved 2026-10-03)

*Added 2026-10-03 under invariant 10, in the same PR line as the ingest code.*
Provenance of every fact below: `docs/specs/source-expansion-evaluation.md`
(gated PASS, merged `2504fb89`), rows 1B.5, 1B.3, 1E.1, 1D.1, 1B.2 and section
6 items 12-13, 15, 25, 31-33. Quotes marked "gate" were verified by
red-reviewer via curl on 2026-10-03 and are carried verbatim; **this section
re-fetched nothing** (the one exception is stated in the cvelistV5 row's
Retrieval method cell). The only fresh measurements are local `Grep` counts of
the two curated files (stated in the rows). Each row states its source kind
per this document's standing rule on absence findings.

### 6.1 AVID (AI Vulnerability Database; `avidml/avid-db`)
*Ingested by:* `scripts/ingest_avid.py` to `ingest/wave12_avid.json` (wave 1; systematic ingest from the repo, owner
pipeline-engineer). *Already in the corpus via:* `ingest/avid_owasp_incidents.json`
(hand-curated, no ingest script).

| Field | Value |
|---|---|
| License | **MIT**, for the `avidml/avid-db` repository. Structured source: GitHub API `https://api.github.com/repos/avidml/avid-db` -> `license: {key: mit, spdx_id: MIT}`; raw LICENSE reads *"MIT License / Copyright (c) 2022 AI Vulnerability Database (AVID)"* (evaluation row 1B.5; fetched 2026-10-02, gate-confirmed). **Caveats carried from the gate:** (i) MIT is a software licence applied to a data repo; it is the only grant found and covers the repo as a whole; (ii) records summarise third-party material (papers, news, other databases, CNA text) whose rights are not AVID's to grant, so the MIT grant does not reach that text; (iii) the website `avidml.org/database/` shows no licence statement (gate: curl, no licence string in 508 KB / 1,785 IDs), which is why the ingest source is the repo and not the site. |
| Scrape-permitted | Not scraping: public JSON in a public git repo (clone or tarball). Site `robots.txt`/ToS were not fetched and are not needed if the repo is the source; **the ingest must not read `avidml.org`**. HTTP retrieval goes through `ingest/common.py` (invariant 5); a `git clone` would be non-HTTP egress and needs its `docs/INGESTION_CONDUCT.md` register entry (not used: HTTP tarball / release asset through ingest/common.py; INGESTION_CONDUCT.md entry 3 records the decision). |
| Redistribute-verbatim | **YES for AVID-authored repo content under MIT**, with the copyright and permission notice retained (added to `NOTICE-DATA` and `.reuse/dep5`, 2026-10-03). **NO claim** over third-party text inside records (not audited). Records classed "CVE Entry" carry CNA text, which is governed by the CVE ToU (section 6.2), not by MIT. |
| Relicense-compatible | **YES** (MIT is permissive, attribution-only), with the MIT notice reproduced. |
| Action | **(a) compatible with conditions:** keep the MIT notice with AVID-derived data (done in `NOTICE-DATA`/`.reuse/dep5`); per-record reference to the AVID id/URL; ingest from the repo, not the website; store reports as facts + link + original summary where the record text is third-party-derived. **Existing curated file `ingest/avid_owasp_incidents.json` (Grep, 2026-10-03: 130 `source_id` rows, of which 109 `AVID-` and 21 `OWASP-GENAI-*`):** this row covers the **109 `AVID-` rows** (AVID-derived, MIT applies; the MIT notice now exists to travel with them). It does **NOT cover the 21 `OWASP-GENAI-*` rows**; their upstream (the OWASP GenAI Security Project roundup) has no row in this document and **they stay OPEN / unassessed** until one is written. Not compared: whether the 109 rows copy AVID text or are original paraphrase (the evaluation read them as short original-looking descriptions keyed to an AVID URL; unverified). One of the 110 AVID ids in the corpus, `AVID-2023-V025`, is not in the repo (upstream removal or renumber): handle as `status`, never deletion (invariants 3, 9). |
| Date-checked | 2026-10-02 (licence, gate-confirmed 2026-10-03); counts 2026-10-03 |
| Retrieval method | **Structured: GitHub API JSON** (`license` field) and raw LICENSE first lines; site absence finding verified by red-reviewer via curl on raw HTML (evaluation section 6 item 15). Carried from the gated evaluation, not re-fetched. The full MIT permission text in `NOTICE-DATA` is the standard SPDX MIT text; **red-reviewer should diff it against the raw LICENSE** (check below). |
| Non-English / facts-only | English. |

### 6.2 cvelistV5 (`CVEProject/cvelistV5`; CVE Program Terms of Use) including the huntr CNA slice
*Ingested by:* `scripts/ingest_cvelistv5.py` to `ingest/wave12_cvelistv5.json` (wave 1; CVE JSON 5 records, filtered by `scripts/ai_relevance.py`; the WS4-T4 allowlist does not exist yet; owner pipeline-engineer).

| Field | Value |
|---|---|
| License | **CVE Terms of Use (SPDX `CVE-TOU`).** GitHub repo `license` field is `null` (structured: `https://api.github.com/repos/CVEProject/cvelistV5`; no LICENSE file; raw URL 404). Repo README: *"You may search, download, and use the content hosted in this repository, per the CVE Program Terms of Use."* The grant (SPDX copy `https://spdx.org/licenses/cve-tou.html`; same text in cve.org's own source `CVEProject/cve-website`, `src/views/Legal/TermsOfUse.vue`, gate): *"MITRE hereby grants you a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute Common Vulnerabilities and Exposures (CVE™). Any copy you make for such purposes is authorized provided that you reproduce MITRE's copyright designation and this license in any such copy."* |
| Scrape-permitted | Not scraping: the official bulk repo and release zips, built for mirroring (README: daily baseline zip, hourly delta zips). robots.txt not applicable (GitHub-hosted). Release assets are HTTP and go through `ingest/common.py`; `git clone` would need its `INGESTION_CONDUCT.md` register entry (not used: HTTP tarball / release asset through ingest/common.py; INGESTION_CONDUCT.md entry 3 records the decision). |
| Redistribute-verbatim | **YES**, with MITRE's copyright designation and the licence text reproduced in copies. Individual CNA-authored description text could in principle carry third-party rights; the ToU carves none out (evaluation row 1B.3). |
| Relicense-compatible | **YES, with a notice condition.** The grant includes "sublicense" and "prepare derivative works", so a CC BY 4.0 grant by us over our derived dataset is allowed provided the MITRE designation and the CVE-ToU licence text travel with it. **The condition applies TODAY to the existing corpus**, not only to new ingest: it already carries NVD-derived CVE text (section 2.2). The gate confirmed no CVE-ToU notice existed in `NOTICE-DATA`, `.reuse/dep5` or this file (targeted `git grep`, evaluation section 6 item 13). The existing "MITRE" notices are the ATLAS **Apache-2.0** notice, a different instrument. **Remedied 2026-10-03:** the CVE ToU notice is now in `NOTICE-DATA` and `.reuse/dep5`. |
| Action | **(a) compatible with condition (condition now met in the notice files).** Selection is by the shared filter `scripts/ai_relevance.py` (gate-corrected; figures from `docs/audits/wave12-ingest-delta-2026-10-03.md` section 5). It reuses the repo's own vocabularies, applied so that weak tokens never decide alone, description tokens are word-bounded, and product fields (vendor, product, packageName, repo, collection URL, CPE) match as delimited segments. **The WS4-T4 allowlist (`data/ai_package_allowlist.json`) does not exist yet**, so a curated seed of 88 entries (`ECOSYSTEM_SEED`, each measured as a miss in the window) stands in for it, and the top weak-signal products that did not pass are committed in the provenance file as `candidates_for_curation`. Description-only matches (no product evidence) must carry the INCLUSION.md section 6 second signal; Linux-kernel-CNA description-only matches are rejected; credit and trailer clauses ("found/reported by ...", `Assisted-by:`) are stripped before matching; and `gpt-N` is matched only in a bounded model form. Measured: description-only rows fell from 454 of 2,705 emitted to 206 of 2,502 (cvelistV5-only entries: 384 of 2,240 to 150 of 2,046); a 40-row re-sample of that stratum found 40 plausible, 0 clear false positives, 1 borderline. Not a human-reviewed list. **huntr CNA slice (evaluation 1E.1):** huntr enters **only** as CVE records whose assigner is huntr (`security@huntr.dev` / `@huntr_ai`), under this row's CVE ToU grant. **huntr.com report text is NOT ingested**: huntr row 1E.1 is **(c)** (Participation Terms s7.1 assign contributions exclusively to Palo Alto Networks; PANW Terms of Use bar reproduction; no public reuse grant found), and huntr.com serves no structured report fields anyway. The bounty URL may be kept as a reference link inside a CVE record (facts + link). Nothing from `huntr.com` is fetched. The huntr route is the CNA filter, not a separate source. |
| Date-checked | 2026-10-02 (licence); gate re-verification 2026-10-03 |
| Retrieval method | **Structured (GitHub API JSON `license: null`, SPDX licence text)**; README rendered. `cve.org/Legal/TermsOfUse` is a JS app the tools could not render, so the cited text is the SPDX copy, corroborated by the gate's read of cve.org's own Vue source. The exact wording of "MITRE's copyright designation" was not established by the evaluation. The line used in `NOTICE-DATA`, `Copyright © 1999-2026, The MITRE Corporation.`, is cve.org's own site copyright: `CVEProject/cve-website` `src/components/FooterModule.vue` (rendered as 1999-{currentYear}), verified by foreman via curl 2026-10-03. It carries no "All rights reserved." A WebFetch of the Vue ToU source on 2026-10-03 returned only a summary stating the page contains no explicit copyright line; that is a summarising converter and is not evidence either way. |
| Non-English / facts-only | English. |

### 6.3 arXiv cs.CR metadata via OAI-PMH (`oaipmh.arxiv.org`)
*Ingested by:* `scripts/ingest_arxiv_oaipmh.py` to `ingest/wave12_arxiv.json` (wave 2; metadata only, selection by a deterministic
rule only, no human-approved list (D43); owner pipeline-engineer).
*Already in the corpus via:* `ingest/arxiv_incidents.json` (hand-curated, no ingest script).

| Field | Value |
|---|---|
| License | **Descriptive metadata: CC0 1.0.** arXiv API Terms of Use `https://info.arxiv.org/help/api/tou.html`: *"You are free to use descriptive metadata about arXiv e-prints under the terms of the Creative Commons Universal (CC0 1.0) Public Domain Declaration."* Footnote 1: *"Descriptive metadata includes information for discovery and identification purposes, and includes fields such as title, abstract, authors, identifiers, and classification terms."* The abstract is **inside** the CC0 metadata (gate-confirmed, evaluation section 6 item 25, positive finding). **Full text / e-prints: NOT covered**; per-paper author licences (CC BY, BY-SA, BY-NC-SA, BY-NC-ND, arXiv perpetual non-exclusive, CC0) and the ToU bar storing and serving e-prints without permission. |
| Scrape-permitted | **YES via OAI-PMH only.** `export.arxiv.org` robots.txt is `Disallow: /`, so the API named in the ToU is **unreachable through `ingest/common.py`** (fail-closed) and a `common.py` exception is not wanted; the route is **`oaipmh.arxiv.org`** (robots allows it; set `cs:cs:CR`). ToU: *"make no more than one request every three seconds, and limit requests to a single connection at a time."* Never fetch `arxiv.org` (Crawl-delay 15; `Disallow: /e-print`, `/src`, `/api`, `/search`) for this ingest. |
| Redistribute-verbatim | **Metadata incl. abstract: YES (CC0).** **Full text: NO**, never mirrored, never fetched. |
| Relicense-compatible | **YES for CC0 metadata** (CC0 imposes nothing). **Residual caution, not resolved in our favour:** the CC0 dedication is **arXiv's**; the abstract text is the **author's** expression, licensed to arXiv non-exclusively, and nothing read shows authors waived rights in abstract prose. The conservative shape, adopted here: ship **title, authors, identifiers, classification and an original summary written by us from the paper, with the arXiv id as link**; carry the verbatim abstract only if the maintainer decides to accept that residual. |
| Action | **(a) compatible for metadata; no abstract text ships: the abstract is used only by the filter and discarded, and the shipped `description` is original deterministic prose (`description_provenance: original`), so the residual above does not arise for the new rows.** Fields: title, authors, arXiv id/DOI, categories, dates, abstract (see residual). **Never** e-prints, PDFs or full text. Selection is deterministic only, per user ruling D43 (2026-10-04): **no human-approved list exists**, rows ship as `quality_tier: auto`, and a human curation pass may follow. The filter (delta section 6): the title carries the attack (an unambiguous GenAI-attack term, or an attack term plus a GenAI target term), the abstract names a GenAI target, and the abstract carries a concrete real-world claim; defense, benchmark, survey and evaluation titles are excluded. The window is papers first submitted (v1) 2025-10 to 2026-10, dated by the month in the new-style id, not by the OAI `created` field (which is the latest version's date). The abstract is used by the filter and then discarded; each row's `description` is original deterministic prose with `description_provenance: original`. No model call in the build path. Measured: 55 rows shipped, and the filter recovers only 6 of the 115 hand-curated rows' records, so it selects a different population from the curated list. Honour OAI-PMH deletion headers as `status` changes, not deletion (invariants 3, 9). **Existing curated file `ingest/arxiv_incidents.json` (Grep, 2026-10-03: 123 `source_id` rows):** this row covers **only the metadata half** (title, authors, identifiers, abstract, classification) of those rows. It does **NOT** cover any prose in them that is not arXiv metadata, which is the maintainer's own and needs no row, **nor** any full-text passage copied from a paper: whether any of the 123 rows copies full-text passages was **not checked** and stays **OPEN** until a reviewer compares them (check below). Section 4's ten benchmark citations are separate and unchanged. |
| Date-checked | 2026-10-02 (gate-confirmed 2026-10-03) |
| Retrieval method | Positive grant quoted from primary arXiv pages (rendered HTML, via WebFetch in the evaluation, then curl by the gate); robots findings read directly. **Not an absence finding.** Carried from the gated evaluation, not re-fetched. |
| Non-English / facts-only | Mostly English; some papers in other languages. |

### 6.4 EUVD (European Vulnerability Database, ENISA): NOT INGESTED, pending outreach
*Ingested by:* **nothing. EUVD is not ingested.** The user approved wave 2, but
the licence is **(d)** and outreach must settle it first.

| Field | Value |
|---|---|
| License | **UNKNOWN (no data licence).** ENISA Legal Notice `https://www.enisa.europa.eu/about-enisa/legal-notice`: *"Reproduction of ENISA material published on this website is authorized, provided the source is acknowledged, unless it is stated otherwise."* Whether JSON served from `euvdservices.enisa.europa.eu` is "material published on this website" is **not established**, and the notice grants no adaptation or CC BY right. The official docs repo `enisaeu/euvd-docs-public` LICENSE: *"No reuse, redistribution, or modification of its contents is permitted without written permission from ENISA."* (documentation only, but it shows reuse expressly withheld). Both gate-verified by red-reviewer via curl, 2026-10-03 (evaluation row 1B.2). |
| Scrape-permitted | robots.txt at `euvd.enisa.europa.eu` allows all; API requires no authentication. Moot until the licence question is answered. |
| Redistribute-verbatim | **UNKNOWN -> treated as NO.** CVE-derived fields are covered by the CVE ToU (section 6.2) and are taken from cvelistV5, not from EUVD. |
| Relicense-compatible | **UNKNOWN -> treated as NO** for ENISA-added fields (EUVD id, enrichment) and for EPSS (FIRST's terms, unchecked). |
| Action | **(d) outreach drafted, not sent:** `docs/outreach/enisa-euvd-reuse-2026-10-03.md`; the user sends. Until answered: **no EUVD field enters the corpus**, no EUVD text is copied, nothing from the docs repo is copied. EUVD is 100% CVE-duplicate of cvelistV5 (3,873 of 3,873 items [M], evaluation), so nothing in the CVE coverage depends on it; the only unique value is EUVD ids and EPSS. |
| Outreach date | **Drafted 2026-10-03; not sent.** Logged in `docs/outreach/README.md` when the user sends. |
| Date-checked | 2026-10-02 (gate-verified 2026-10-03) |
| Retrieval method | JSON endpoint (structured; silent on legal terms by construction); legal notice and docs-repo LICENSE verified by red-reviewer via curl. The SPA shell was method-suspect (it hid the footer link). Carried from the gated evaluation, not re-fetched. |
| Non-English / facts-only | English. |

---

## Summary of outcomes requiring escalation (not resolved in the project's favor)

| # | Source | Outcome | Why it's an escalation |
|---|---|---|---|
| 1 | AIID (§1.2, retired 2026-07-18) → AIID official snapshot (§1.2a, active) | **Both the acquisition-method violation AND the content-licensing question are RESOLVED for the shipped population (2026-07-18 / 2026-07-30-E23, corrections applied 2026-07-30 on BOUNCE #1 — outcome unchanged).** A separate, currently-non-shipping population carries a named tripwire, not a resolution. | Bot/high-volume access was prohibited by AIID's own Terms of Use; `scrape_aiid.py`'s scrape is retired and replaced by `scripts/ingest_aiid_snapshot.py` reading AIID's official weekly snapshot channel (WS0-T4 swap-half, decision D1). **Content-licensing question resolved 2026-07-30**, not merely flagged: `docs/audits/E23-aiid-marking-ruling-2026-07-30.md` finds AIID's maker is U.S.-situated (principal place of business, venue, and arbitration in Los Angeles, California; US federal tax-exempt status — a specific state of incorporation is not stated on any AIID-controlled page and is not material to the outcome), which — unlike AIAAIC's UK situs — categorically disposes of the copyright question over the retained `title` field (U.S. Circular 33's short-phrase exclusion, keyed to AIID's own situs, not its Terms-of-Use choice-of-law clause) and fails the UK/EU database-right maker-qualification gate outright (no UK or EU sui generis right subsists in AIID's collections for any maker, regardless of investment). **This is not "the same posture as AIAAIC's E13 finding" — it never was; nobody had checked AIID's maker domicile before now.** The ~1,463-row shipped population needs no row-level marker. A separate, currently-non-shipped population (63 hand-curated rows + 1,457 AIRI-Navigator rows sharing AIID's source-ID convention) is **not** cleared by this ruling and carries a tripwire: if it ever starts shipping, it reopens for its own review first. See `docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md` (method) and `docs/audits/E23-aiid-marking-ruling-2026-07-30.md` (content-licensing ruling, including its correction log). |
| 2 | AIAAIC Repository | **(b) copyright share-alike resolved by decision D2** — license confirmed CC BY-SA 4.0; handled by reducing to facts+link, not by split-licensing (a second, narrower copyright question over the retained headline itself — E15/D17 — is folded into the counsel ask below, not resolved separately here). **The separate EU/UK sui generis database-right question is OPEN, but its direction is DECIDED AND IMPLEMENTED (D11, 2026-07-27)**: row-level ShareAlike/attribution containment via the `content_license` marker (now reaching all 1,517 AIAAIC-citing rows, E16/D18) plus scope-narrowing queued for Phase 2 — see `docs/audits/WS0-E13-database-right-2026-07-18.md` (amended 2026-07-27). Whether to additionally engage qualified counsel on AIAAIC's own subsistence/substantiality (E13 §1–§2) remains open. | Verbatim spreadsheet-cell text carried a real copyright share-alike obligation; per D2 (2026-07-16, human) the project honors it by not carrying verbatim text at all, keeping one clean CC-BY-4.0 license with no BY-SA subset. That decision disposes of the *copyright* question for AIAAIC's narrative prose only — the retained headline is a separate, still-open copyright question (E15/D17). E13 (2026-07-18, amended 2026-07-27) finds AIAAIC's database right plausibly subsists and the extraction (1,422 field-marked rows / 1,517 citing rows total, not the stale ~1,513 this row previously carried) plausibly meets the substantiality threshold even after the D2/D9 reduction — facts+link mitigates but does not eliminate exposure. genai_incidents itself does not hold a UK/EU database right (sole Canada-resident individual maker, established 2026-07-27), so the worst case is bounded to row-level ShareAlike on AIAAIC-derived rows, never dataset-wide. A resolved direction is on record (D11); AIAAIC's own subsistence/substantiality and the headline-copyright question remain open, routed to the same counsel ask. |
| 3 | OECD AIM | **(b) RESOLVED 2026-07-30 (E21) and IMPLEMENTED 2026-07-30 (merged `6f06eaeb`) — `description`-reduction to structural-facts-only, plus per-entry OECD attribution, both shipped; `title` carries a separate, narrower open question, still unresolved** | The "OECD-composed editorial abstract" hypothesis this row briefly carried is disproven: `title`/`summary` are **LLM-generated (OpenAI o3-mini) from the top three source articles per event**, per AIM's own methodology page (E21, direct WebFetch, 2026-07-30) — machine output derived from copyrighted third-party news, not OECD staff prose and not (per the earlier finding) quoted news excerpts either. E21 also newly establishes that AIM explicitly self-incorporates OECD's general terms ("Your use of... AIM... is subject to the terms and conditions found at www.oecd.org/termsandconditions"), so the general-terms question genuinely reaches AIM — but whether that grant extends to LLM output of unresolved ownership is itself ambiguous, and resolves conservatively per this document's own standing rule. **Result: `Redistribute-verbatim: NO` stands for `description`, on this corrected rationale; `title` is tracked as a separate, lower-risk open question at the same posture as AIAAIC's E15/D17 headline question, and remains open — this reduction does not touch `title`.** The code-level fix (reduce `description` to structural facts + link; add OECD attribution) **is implemented**, not merely required — `build_description()` in `scripts/ingest_oecd_aim.py` and the E21 §5.3 attribution mechanism in `scripts/merge_and_dedupe.py`, both verified by direct code read. Scope, as measured post-merge — two different counts, not one: **3,667/3,829** OECD-AIM-sourced rows carry the reduced `description` (the other 162 were merged into an entry whose own description, from a different upstream source, took precedence instead); **3,829/3,829** carry the attribution string regardless of that, plus 368 further AIID-bridge entries carrying the attribution alone. **BOUNCE #1 correction (2026-07-30):** this cell previously conflated the two counts, stating 3,829/3,829 for both and dismissing 3,667 as "the gate's pre-merge dry-run estimate" — that was backwards: **3,667 was, and is, the correct shipped `description` count**; 3,829 is the separate, also-correct, attribution count. See `docs/audits/E21-5.3-oecd-attribution-2026-07-30.md` for the measurement; full reasoning in `docs/audits/E21-oecd-narrative-licence-2026-07-30.md` §5; see §1.5 Action. |
| 4 | MIT AIRI Navigator | **(d) UNKNOWN, narrowed** — own license confirmed CC BY 4.0; only the transitive AIID share-alike question is open | AIRI Navigator's own license is established via a one-hop raw-HTML check: its Terms-of-Use modal names airisk.mit.edu as its data source, and that page's footer carries the CC BY 4.0 grant, re-verified 2026-07-16 and cross-checked independently by red-reviewer and the foreman. What remains genuinely unresolved is only whether AIID's CC-BY-SA share-alike (Section 1.2) applies transitively to the AIID-derived fields this tool wraps; see §1.4. Outreach on this question is now sent (both `docs/outreach/mit-airi-courtesy.md`, 2026-07-27, and `docs/outreach/airi-draft4-export-request.md`, 2026-07-29); the question itself remains open pending MIT's reply. |
| 5 | CSET-AIID Harm Taxonomy | **RESOLVED (2026-07-30, E20)** — closed under current scope with a reopen-on-scope-growth tripwire; no outreach sent or owed | No license file exists upstream, confirmed via the GitHub API's structured `license` field (not a large-page fetch, so not subject to the AIAAIC failure mode). Only one original, hand-authored sentence is currently reproduced, so the upstream's unclear license is moot for what the code does today; see §3.2's Action cell for the exact reopen condition. The "2026-07-15 (drafted; not yet sent)" outreach this row's Action previously implied never existed as an actual file — corrected per E20. |

Three of the five (AIAAIC, MIT AIRI Navigator, CSET-AIID) originally carried
outreach-pending status. AIAAIC's *copyright* share-alike question over its
narrative prose is resolved and its handling decided (D2) — a further,
narrower copyright question over the retained headline specifically is open
(E15) and folded into the counsel ask below (D17), not resolved separately.
AIAAIC separately carries an **EU/UK sui generis database-right question
whose direction is now decided and implemented (D11, 2026-07-27)**:
row-level ShareAlike/attribution containment (the `content_license` marker,
now reaching all 1,517 AIAAIC-citing rows per E16/D18, 2026-07-29) plus
scope-narrowing queued for Phase 2, per E13 (2026-07-18, amended 2026-07-27,
`docs/audits/WS0-E13-database-right-2026-07-18.md`) §6.1. AIAAIC's own
database-right subsistence and this extraction's substantiality (E13 §1–§2),
and the headline-copyright question (E15/D17), remain open, fact-intensive
questions pending qualified counsel if the project chooses to seek it —
AIAAIC is therefore **not** fully closed out, but its residual exposure is
now bounded to row-level obligations on AIAAIC-derived rows, never a
dataset-wide one (E13 §4.1, established 2026-07-27: genai_incidents' sole
maker is a Canada-resident individual, so genai_incidents holds no UK/EU
database right of its own and the §4(b) database-level ShareAlike escalation
is dead). **MIT AIRI Navigator** remains open — outreach is now sent (two
distinct messages: `docs/outreach/mit-airi-courtesy.md`, 2026-07-27, and
`docs/outreach/airi-draft4-export-request.md`, 2026-07-29; D8's 30-day
AIRI-hold clock keys to the latter, decision point 2026-08-28) — but the
underlying transitive-AIID-share-alike question is still unresolved pending
MIT's reply; see §1.4. **CSET-AIID Harm Taxonomy is now RESOLVED (E20,
2026-07-30)**: closed under the current single-reference-entry scope, with a
reopen-on-scope-growth tripwire recorded in §3.2's Action cell — no outreach
was ever drafted, and per the user's ruling none is owed while that scope
holds. **OECD AIM's core reduction question is now RESOLVED and IMPLEMENTED,
not open (E21, 2026-07-30; merged `6f06eaeb`):** `description` reduction to
structural facts + link, and per-entry OECD attribution, are both shipped in
code, on a corrected rationale (`title`/`summary` are LLM-generated from
third-party news, not OECD prose or quoted excerpts) — see §1.5 Action and
`docs/audits/E21-oecd-narrative-licence-2026-07-30.md`. A narrower, separate
`title`-specific question remains open, tracked at the same posture as
AIAAIC's E15/D17 headline question. **What is still genuinely pending is the
outreach send, not the licensing analysis or its implementation:**
`docs/outreach/oecd-aim-terms.md` — corrected as of 2026-07-30, per E20 — is
drafted, awaiting red-reviewer and the user's send; the "2026-07-15 (drafted;
not yet sent)" this section previously recorded for OECD described an
artifact that never existed on any branch. A clarifying AIAAIC outreach was
sent 2026-07-27
(`docs/outreach/aiaaic-facts-link.md`; reply clock 2026-08-26). **The
pending/unresolved count as of 2026-07-30 is two — MIT AIRI Navigator and
OECD AIM — down from three (AIAAIC, MIT AIRI Navigator, CSET-AIID
originally)**: CSET-AIID no longer counts, having resolved with a tripwire
rather than an outreach email. The one outreach draft still awaiting the
user's send is `docs/outreach/oecd-aim-terms.md`; MIT AIRI Navigator's
outreach is sent and awaiting reply.

**AIID (§1.2/§1.2a, updated 2026-07-18; content-licensing question resolved
2026-07-30 — E23):** the *acquisition-method* violation (prohibited
high-volume scrape) is resolved — retired and replaced by the
sanctioned-snapshot channel (WS0-T4 swap-half, D1). **AIID does NOT carry
the same class of open question as AIAAIC's E13 finding — that framing,
carried on this board since 2026-07-18, was never checked against AIID's
own maker domicile and turns out to be wrong.**
`docs/audits/E23-aiid-marking-ruling-2026-07-30.md` establishes AIID's
maker (Responsible AI Collaborative, Inc.) is US-situated — principal place
of business, venue, and arbitration all in Los Angeles, California, per its
own Terms of Use, and US federal tax-exempt status (EIN 88-1046583,
`incidentdatabase.ai/about/`); a specific state of incorporation is not
stated on any AIID-controlled page and is not material, since no US state
satisfies the tests below. Applying E13 §4.1's own maker-qualification
gate (built to test genai_incidents' own UK/EU database-right
qualification) to AIID's maker instead: a US-situated body fails
both the UK reg 18 and EU Art 11 nexus tests, so **no UK or EU sui generis
database right subsists in AIID's `incidents`/`classifications`
collections at all** — a stronger, cleaner result than AIAAIC's, whose UK
maker plausibly *does* qualify and whose database-right question therefore
remains genuinely open. Separately, U.S. copyright law's Circular 33
categorically excludes titles/short phrases from protection — disposing of
the copyright question over AIID's retained `title` field the way UK/EU
law's lack of an equivalent carve-out could **not** dispose of AIAAIC's
parallel headline question (E15/D17, still open, folded into the AIAAIC
counsel ask). **Result: the ~1,463-row population that actually ships
needs no row-level `content_license` marker.** This does **not** extend to
`ingest/aiid_incidents.json`'s 63 hand-curated rows or the 1,457
AIRI-Navigator rows sharing AIID's source-ID convention, which carry
uncleared risk and are kept out of the shipped corpus only by current
merge-order mechanics — a named tripwire, not a clearance, covers that
population: if it ever starts shipping, it reopens for its own review
first. `NOTICE-DATA` and `.reuse/dep5` **were corrected 2026-07-30
(`7c4b4394`, gated PASS)** — they had described AIID and AIAAIC as "the same posture," which this
ruling shows is false in both directions (AIID's shipped population is
lower-risk than AIAAIC's despite AIID's license being the confirmed one;
AIAAIC's remains the genuinely open question). Not touched by this
ruling: AIID's separate transitive-AIRI-wrapper question (§1.4), which
remains open on its own outreach track.
