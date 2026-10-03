# Source-expansion tranche 2: licence pre-rows, red-reviewer gate 1 (absence checks)

**Dated record, 2026-10-03. Do not regenerate.** (Working agreements 4 and 5.)
The gate ran on `eval/source-expansion` @ `8ddb7702`, against
`docs/specs/source-expansion-evaluation.md`. The verdict is reproduced below
as the reviewer delivered it, with no edits by the foreman. Raw pages are
held in the reviewer's scratchpad and are not committed.

---

VERDICT: BOUNCE on tranche-2 licence pre-rows (8ddb7702) — five absence findings are refuted by raw HTML, one quoted clause is not on its cited page, and two rows' scores/actions no longer follow from their evidence. First bounce I'm aware of on this task.

DEFECTS
1. 1A.8 JVN — the quoted FAQ Q5-2 text ("please refer to the separately provided guidelines") is NOT on https://jvndb.jvn.jp/nav/jvndb_faq.html (Shift_JIS; 0 hits for "separately provided" and 別途; /en/nav/jvndb_faq.html is 404). Actual Q5-2: 「引用、転載、再配布するにあたり、特に制限は設けておりません。また、ご利用の際はメールでお知らせいただくことをお願いしております。」 ("no particular restrictions on quotation/reprint/redistribution; please notify by email"); Q5-1 same for commercial use under MyJVN API terms. Also /apis/termsofuse.html is the MyJVN API service terms (2010, rev. 2019) — disclaimer + prohibited acts (malware/illegal/defamation), NO reuse restriction; not "tool terms." Score 1/(d) rests on non-existent evidence; row must be rewritten (an FAQ informal permission is not a licence and jvn.jp side is separate, so score is the auditor's call — but "guidelines not located" must go).
2. 1A.9 CSA — missed clause: "Except as set forth below, caching and links to, and the framing of this website or any of the Contents are prohibited. You must secure permission from CSA prior to hyperlinking to, or framing, this website or any of the Contents" (https://www.csa.gov.sg/terms-of-use/). This contests the "link" half of facts+link → per the doc's own scale (score 1 requires that shape uncontested), 1/(c) doesn't follow; reads as 0. (Also: the "Governing Law" cut-off is genuine on the page — "shall be hear." — not a tool artefact.)
3. 1A.7 JPCERT — "No licence/ToS located" REFUTED. Homepage links ご利用にあたって https://www.jpcert.or.jp/guide.html; §2: quotation free with source/title/URL; 転載・再配布 requires notifying office@jpcert.or.jp, JPCERT/CC coordinates third-party rights; individual documents may carry own conditions. Row + outreach target must be rewritten.
4. 1A.4 ENISA — "ToS not located" / "website text not covered" REFUTED. Homepage footer → /about-enisa/legal-notice: "Reproduction of ENISA material published on this website is authorized, provided the source is acknowledged, unless it is stated otherwise." Reproduction permission (not CC BY, no adaptation grant) — (d) for web text must be re-stated against it. (Footer links a 2024-12 IPR path but the PDF there still says "Public version | December 2021" — that citation stands.)
5. 1B.2 EUVD — "None located" REFUTED. EUVD SPA bundle (main.bdd2ef30.js) footer links the same ENISA Legal Notice; official docs repo exists — github.com/enisaeu/euvd-docs-public (pushed 2026-09-18; GitHub spdx NOASSERTION), whose LICENSE reads: "This repository is made available solely for programmatic access by the EUVD frontend. No reuse, redistribution, or modification of its contents is permitted without written permission from ENISA." That covers the docs not the data, but the row must weigh it. Watch item W2's "official docs unreadable / third-party docs only" is also refuted — apidoc.md documents endpoints, "require no authentication", max 8/100 records per request, no versioning/changelog.
6. 1C.5 ICO — "website-terms page not found" REFUTED. Footer → /global/copyright-and-re-use-of-materials/: OGL v3.0 "except where otherwise stated", required attribution "Information Commission's Office, [name and date of publication], licensed under the Open Government Licence"; no automated-access clause. Score 3 stands; row needs the citation.
7. 1B.3 cvelistV5 — check 13 as written cannot be trusted: auditor's grep hits NOTICE-DATA, docs/SOURCE_LICENSES.md and .reuse/dep5, but every hit is the MITRE ATLAS Apache notice — so the row's "grep for 'MITRE Corporation' found nothing" is false (NOTICE-DATA:41, .reuse/dep5:17). The real CVE-ToU gap is CONFIRMED by targeted git grep for "Common Vulnerabilities and Exposures" / "hereby grants you a perpetual" / "cve.org/Legal" — no notice-file hits. Replace check and sentence.

Smaller corrections (not bounce grounds alone): 1A.1 OGL interop "quote" isn't verbatim (actual: "These terms are compatible with the Creative Commons Attribution License 4.0 … when the Information is adapted and licensed under either of those licences, you automatically satisfy the conditions of the OGL when you comply with the other." — same substance). 1A.3 cyber.gc.ca homepage footer links canada.ca/en/transparency/terms.html (same non-commercial wording); CSE terms linked from about page — conclusion unchanged. 1A.10 the legal notice IS CERT-EU's own ("(c) … (CERT-EU), 2023", "CERT-EU maintains this website") — refutes "did not mention CERT-EU"; also the "All rights reserved" footer appears on the legal-notice page itself — contradiction stands, score holds. 1D.2 Finder Terms 2023 are superseded: /terms/finder → /terms/community (Community Member T&C, effective May 11, 2026), same licences-to-HackerOne/Customer-only substance; hackerone.com/robots.txt has only a Sitemap line. 1B.5 AVID site lists up to AVID-2026-R1714, not R0518 (truncated fetch). 1C.3 AP page now read primary (no longer extract-only) and adds: "doorleveren aan derden of commercieel verwerken" requires contacting AP; robots has GPTBot Disallow: / and Allows /documenten/*. 1C.4 data.gouv.fr has dataset "Sanctions prononcées par la CNIL", licence fr-lo (Licence Ouverte) — supports the open-data subset. 1A.5 bsi.bund.de robots has Crawl-delay: 10; wid.cert-bund.de/robots.txt 404; sample CSAF advisory (wid-sec-w-2026-3717) has distribution TLP:WHITE only and liability-only legal_disclaimer, no licence.

RESULTS (C=CONFIRMED · R=REFUTED · U=STILL-UNVERIFIABLE)
1 NCSC · C · robots 404 (HTML "site unavailable" page); T&C only hit "automatically waive"; OGL clause verbatim
2 ACSC · U · cyber.gov.au & asd.gov.au: TLS connects then 0 bytes (Akamai), 4 ways tried; corroboration only: ASD ism-oscal README "provided under a Creative Commons Attribution 4.0 International licence … this licence only applies to material as set out in this document" (per-document)
3 CCCS · C (citation corrected) · robots 404; CSE terms no access clause; non-commercial clause verbatim
4 ENISA · R · legal-notice reproduction clause (D4)
5 BSI/WID · C (no open licence) / U (WID-specific terms: JS app, 28 chunks grepped, route not found)
6 ANSSI · C · no access clause; "Licence ouverte … version 2.0" verbatim; robots as stated
7 JPCERT · R · (D3); robots 404 confirmed
8 JVN · R · (D1); robots 404 confirmed both jvndb.jvn.jp and jvn.jp
9 CSA · R · (D2)
10 CERT-EU · C (contradiction) / R (CERT-EU-not-named)
11 EUVD · R · (D5); API headers no licence/Link/terms; robots empty Disallow
12 cvelistV5 licence · C · /license 404, license null
13 MITRE notice gap · C on substance; check-as-written false-fires (D7)
14 VulnCheck · C — both clauses verbatim at https://www.vulncheck.com/service-terms (rev. April 20, 2026): "Customer may not make the Services Data available for free or under an open source or similar license." and the "developing, training, or fine-tuning any artificial intelligence model" clause; Free/Trial clause explicitly names "community" version. Full (untruncated) FAQ: no redistribution Q&A, only "It's free! We only ask for prominent attribution." Attribution page: "Including VulnCheck KEV in your open source or commercial product is meant to be free" — conflict is real and sharper; 0/(d) follows.
15 AVID site · C · no licence string in 508 KB / 1,785 IDs
16 Garante · C · footer "Regole del sito" no reuse terms; second-hand "fonte + non ufficiale" clause not found on a docweb page either
17 EDPB · C · 1,582 items; zero rss/xml/csv/api/export strings; reuse clause verbatim
18 Dutch AP · C, upgraded to primary (curl 200)
19 CNIL · C · robots only Drupal paths thru line 191; no access clause (one "automat" hit = nav "décision automatisée")
20 ICO · R · (D6); Crawl-delay 6 confirmed
21 ANPD · C · no anpd line; CC BY-ND 3.0 link confirmed
22 OPC · C · robots 404
23 BAILII · C · s12(a)-(d) + "block entire domains" verbatim (page sits behind an Anubis PoW for Mozilla UAs — read with plain curl UA); new: "BAILII has no objection to links from other websites"
24 CanLII · U for clause (403 DataDome) / C for robots "User-agent: * Disallow: /"
25 arXiv · C · footnote "title, abstract, authors, identifiers, and classification terms"; CC0 + 3s verbatim
26 HackerOne · C · no scrape clause in 6 docs; current terms differ (above)
27 Bugcrowd · C · "The copying, redistribution, use or publication by you of any portion of our Website is strictly prohibited." verbatim at https://www.bugcrowd.com/website-terms-and-conditions/; assignment/exclusive-licence sentence verbatim; no scrape clause
28 DEF CON / BH / AIV · U · defcon.org connection reset; blackhat.com/terms 403; BH robots Disallow /errors/ only; AI Village repo licences mostly software (MIT/Apache), awesome-ml-failures none
29 Rejections · Snyk C (2020 clause verbatim; current snyk.io ToS makes Service Data Snyk Confidential Information) · CNVD U (521 JS cookie wall) · CNNVD U (SPA shell) · VulDB U (403)
30 Watch · Art. 73 C — official OJ text via Publications Office Cellar: 0 hits publish/public/database/register; para 11 verbatim (EUR-Lex returned 202/WAF; original 2024 text, not consolidated); Digital Omnibus OJ dates U (not fetched). EUVD apidoc R (D5)

DIFFERENT ROUTES (not the auditor's commands): NCSC homepage footer + own substrings + National Archives OGL page; ACSC GitHub org API + ISM README; ANSSI footer → Conditions générales + live /avis/ page checked for per-item overrides (none); EUVD SPA JS bundle footer links → official docs repo; cvelistV5 API license field + /license endpoint + CVE ToU from cve.org's own source (CVEProject/cve-website src/views/Legal/TermsOfUse.vue — grant verbatim incl. "sublicense" and "reproduce MITRE's copyright designation"); VulnCheck/Bugcrowd script-stripped visible text; also footer routes for JPCERT, ICO, Garante, ENISA, HackerOne; data.gouv.fr API for CNIL.

CHECKS THAT COULD NOT FAIL / FALSE-FIRE: #13 (hits ATLAS notice); #1/#3/#9 'automat'/'robot' hit "automatically waive", CDN/log boilerplate, Next.js route manifests — substituted script-stripped visible text with positive controls; #21 can't see wildcard rules — read whole file; #17 'download' matches per-PDF links — excluded; #3's terms-href test matches the canada.ca global footer.

INVARIANTS: three-dot diff origin/main...HEAD touches only the two docs/specs files (895 insertions); SOURCE_LICENSES.md and data/ 0-line diff. The brief's two-dot `git diff origin/main --stat` additionally shows PROGRESS.md purely because main moved (092822c7 board commit) — not a branch change. Worktree porcelain empty (working-tree only). symbolic-ref refs/heads/eval/source-expansion here, refs/heads/main in main tree; never moved HEAD. Raw pages in my scratchpad\raw.

---

**Dated correction, 2026-10-03 (foreman): this record is NOT byte-verbatim.** The header says the verdict is reproduced "with no edits by the foreman". That is true of substance, and false of punctuation and phrasing. The foreman transcribed this text from the gate's message and introduced em dashes, "→" arrows and some compressed phrasing that the delivered message does not carry. **Found by** license-auditor during the D39 gate-3 application: two of the gate's replacement strings, as quoted here, did not occur literally in the target file. The file had a comma where this record shows an em dash. **Consequence:** do not use this record as an exact-match source for `str.replace` or Edit operations. Locate each target by its content and confirm that it is unambiguous. The defects, figures, quoted page clauses and verdict are unaffected. The original text above is preserved under working agreement 4.
