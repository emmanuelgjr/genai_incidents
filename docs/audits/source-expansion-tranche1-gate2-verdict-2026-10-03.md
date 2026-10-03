# Source-expansion tranche 1: string re-check (gate 2): BOUNCE #2, escalated to user

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on `ws0/tranche1-reconstructed` @ `6608869a`. The text below is the gate's message saved as received and concatenated by shell.

---

VERDICT: BOUNCE. This is bounce #2 on this task, so under protocol step 6 it goes to the user. Every defect below is string-level: no score, action letter or quote is wrong, and one more application pass with the text below should clear it. I made no web requests and wrote no repo files.

What passed:
(1) D1-D8 landed verbatim. I checked 23 applied quotes with grep -cF against my raw captures from gate 1 and every one matched. The CourtListener robots quote joins two "#" comment lines, which is acceptable.
(2b), (2c), (2e), (2f): each says only what I measured.
The T1.3 summary blocker, the T1.5 robots paraphrase, and Brief-vs-found items #4 and #6 are accurate. Those Brief-vs-found edits were not in your declared list; I checked them anyway.
(4) Scope is clean. 06c7d561..6608869a touches only the evaluation file. The data/ and docs/SOURCE_LICENSES.md diff against origin/main is empty. HEAD is refs/heads/ws0/tranche1-reconstructed, which matches origin at 6608869a. The working tree is clean (porcelain empty; that covers the working tree only).

DEFECTS

1. The 17 U.S.C. 403 notice is stated as unconditional, which goes beyond what I measured. The FTC clause applies only to "any copyrighted work that consists predominantly of material produced by the FTC or other U.S. government agency".
Summary T1.5: REPLACE "17 U.S.C. 403 notice required" WITH "17 U.S.C. 403 notice applies to a work consisting predominantly of US government material".
Brief vs found #5: REPLACE "and 17 U.S.C. 403 notice applies." WITH "and a 17 U.S.C. 403 notice is required only for a work consisting predominantly of US government material."

2. (2a) fails. T1.6 keeps first-pass claims that contradict the gate text in the same cell, under a header saying that text still describes the site.
License: REPLACE "**`/terms`, `/services-agreement` and `/legal` returned 404 and the Services Agreement was not read**" WITH "**`/terms`, `/services-agreement` and `/legal` returned 404 (guessed paths; the gate found and read the MSA at `/services_agreement`, above)**".
License: REPLACE "the \"0DIN Intel\" docs path `/docs/threat-feed/introduction` was not read, so whether published advisories are free to reuse is **unknown**, and a commercial feed raises the chance that bulk copying is contested" WITH "the \"0DIN Intel\" docs (read by the gate, above) restrict Intel content to licensed users; published disclosures are reusable through the CC BY 4.0 HF corpus, and the site pages themselves carry no licence (gate: one `/disclosures/` page, raw, no licence or copyright text)".
Scrape-permitted: REPLACE "Public advisory pages are not disallowed (path not identified)" WITH "Public advisory pages (`/disclosures/`, 82 URLs in the sitemap; gate) are not disallowed".
Scrape-permitted: REPLACE "**ToS:** no automated-access clause in the policy extract (**ABSENCE FINDING, method-suspect**); Services Agreement unread" WITH "**ToS:** `/policy` has no automated-access clause (gate, raw grep, 0 hits); the MSA's no-scraping term binds Customers of ordered Services (see License)".

3. T1.7 contradicts itself.
Scrape-permitted: REPLACE "**`api.first.org` robots.txt was not fetched.**" WITH "**`api.first.org` robots.txt was not fetched in the first pass (the gate's result follows).**"
Action: REPLACE "If the user rules to proceed on the \"freely and openly accessible\" statement, record the score with its as-of date and the attribution line \"EPSS, FIRST.org\"" WITH "If the user rules to proceed anyway, the ruling must account for the FIRST Services Terms of Use (purpose-limited, revocable), not only the \"freely and openly accessible\" statement; record the score with its as-of date and the attribution line \"EPSS, FIRST.org\"".

4. Statuses that still say "pending" after the gate measured them.
Summary preamble: REPLACE "Scores are pre-gate (this is the specialist's first pass; red-reviewer has not yet checked any row)." WITH "Scores are the specialist's first pass as corrected by red-reviewer gate 1 (BOUNCE #1, 2026-10-03, corrections applied verbatim); no gate has passed them yet."
T1.3 Scrape-permitted: REPLACE "The SEI terms in (4) may restrict automated mirroring. Status: **UNKNOWN pending shell check**" WITH "The SEI TOU in (4) bars mirroring of results but has no automated-access clause (gate, raw; grep for robot, spider, scrap, crawl, automated: 0 hits). Status: **no robots rules; no automated-access ban found; reproduction barred by the TOU**".
T1.8 summary: REPLACE "sentence looks stale" WITH "sentence is false (gate-measured)".
T1.8 Action: REPLACE "Row 2.4's sentence is therefore **likely stale for the MAL- subset** and needs a shell check of what the existing ingest actually stored (red-reviewer item below)." WITH "Row 2.4's sentence is **false** (gate 2026-10-03): the tracked `ingest/cve_nvd_expanded.json` holds 2 OSV records sourced from `MAL-` ids (MAL-2026-3607, MAL-2026-2144) with verbatim OpenSSF report text; the published `data/incidents.json` carries no such text (MAL-2026-3607 appears only as a source id and OSV link on INC-08450, whose description is GHSA text)."
T1.10 Action: REPLACE "Do not crawl `securitylab.github.com` before the shell checks below." WITH "robots.txt declares no restriction, but AUP s6 bars reproducing any portion of the Service; take only facts and links from the site."

5. (3) A14 and A24 do need marking, and so do A19 and A20. Also add a line recording the confirmed items.
A14: PREPEND "**REFUTED in substance by gate 2026-10-03:** the Intel docs say \"0DIN Intel content for licensed users only\"; the sitemap lists 82 `/disclosures/` pages, and the CC BY 4.0 HF corpus was found from it (see T1.6). Original: "
A24: PREPEND "**ANSWERED by gate 2026-10-03:** the GitHub ToS \"Website\" includes GitHub-owned subdomains, so the AUP governs; GHSA twin GHSA-rggg-jp6v-h52j exists for CVE-2025-33214 (see T1.10). Original: "
A19: PREPEND "**ANSWERED by gate 2026-10-03:** see T1.8 Action. Original: "
A20: PREPEND "**CONFIRMED by gate 2026-10-03:** all 469 org repos (API pages 1-5) checked; only `security-workflows` (CI tooling) and `atif-scan` (no description) match secur or scan; no advisory repo. Original: "
INSERT directly under the "## Absence findings for shell verification" heading: "**Gate 2026-10-03 results (raw curl):** A1, A2, A3, A5, A6, A8, A9, A10, A13, A17, A18, A20, A21 and A22 CONFIRMED; the items marked below were refuted or answered."
Consequential, in the same pass:
- T1.9 bullet: REPLACE "Only the first 100 repos by recency were examined (**method-limited absence**)." WITH "The gate later checked all 469 org repos (see A20); no advisory repo."
- Brief vs found #1: REPLACE "no advisory repo in the first 100 HF repos" WITH "no advisory repo among all 469 HF org repos (gate)".

ADVISORY (not blocking)
- These retrieval-method cells still describe only the first pass: T1.4 (it says robots returned 403), T1.6 and T1.7 (T1.7 says "the central finding here is an absence"). Consider appending "Gate 2026-10-03: raw curl re-reads; see the cells above."
- The "S105 reference" bullet says "no re-fetch". At gate 1 I verified 17 U.S.C. §105(a) verbatim at law.cornell.edu, a different host from the earlier gate.

Escalation: two bounces on the same task means the protocol stops and goes to the user. The substance is settled, so a third pass is wording only; whether to run it or override is the user's call.
