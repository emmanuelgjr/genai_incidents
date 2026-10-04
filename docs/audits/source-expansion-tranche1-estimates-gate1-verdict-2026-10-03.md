# Source-expansion tranche 1: estimates and ranking, gate 1: BOUNCE #1

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on `ws0/tranche1-reconstructed` @ `85deb30d`. Both parts below were saved as received and concatenated by shell.

---

## Part 1: verdict and defects

VERDICT: BOUNCE on the tranche-1 estimates and ranking, ws0/tranche1-reconstructed at 85deb30d. This is the first bounce on this deliverable. File: docs/specs/source-expansion-tranche1-evaluation.md. Apply each NEW verbatim; OLD strings may span a line wrap, so match them ignoring the wrap.

D1. OpenSSF: "a CVE or GHSA key does not exist" is refuted (class (b): membership keyed on the wrong thing). By my route, the GitHub advisory API with type=malware and affects=<name>, filtered to an exact package-name match, 72 of the 73 pypi and 85 of the 85 unscoped npm strict names have an upstream GHSA malware advisory. 17 of those GHSA ids are in the corpus (all npm, the same 17 as the author's), and 0 pypi. The OpenSSF records' null aliases are true, but the packages are reachable through the CC BY 4.0 GHSA route the corpus already ingests. Like EUVD against cvelistV5 in tranche 2, OpenSSF is dominated.
D1-a (L339-340) OLD: because the sampled OpenSSF records have `aliases: null` (14 of 14).
NEW: because the sampled OpenSSF records have `aliases: null` (14 of 14). The packages are not GHSA-less: GitHub's advisory database has a `type=malware` GHSA for 72 of the 73 pypi and 85 of the 85 unscoped npm strict names (gate 2026-10-03, GHSA API `affects=` per name), of which 17 (all npm) are in the corpus today. Most of OpenSSF's AI/ML gap is therefore reachable through the CC BY 4.0 GHSA route the corpus already ingests, by widening its malware filter.
D1-b (L459-460) OLD: `aliases` is null in 14 of 14 sampled records, so a CVE or GHSA key does not exist.
NEW: `aliases` is null in 14 of 14 sampled records, so the OpenSSF record carries no CVE or GHSA key; upstream, a `type=malware` GHSA exists for 157 of the 158 unscoped pypi and npm candidates (E.0-3), so a GHSA crosswalk by (ecosystem, package name) is available.
D1-c (L565, end of the OpenSSF Basis cell) APPEND before the closing pipe: ; dominated by GHSA: 157 of 158 candidates have a CC BY 4.0 GHSA malware twin (E.0-3)
D1-d (L589, Why cell) OLD: duplicates part of the GHSA malware stream
NEW: 157 of 158 candidates have a GHSA malware twin (17 in the corpus), so the cheaper route is the existing GHSA ingest

D2. N6 handling is stale. Your premise is right on substance. The board recorded the exclusion at 0641ec1e (11:52:44), 52 seconds after 85deb30d (11:51:52); the author read 77e04846, where the choice was still open. So the text was accurate when written and is wrong now. My judgement on your question: exclusion via OSV does NOT force T1.8 to 0. The decision is scoped to the OSV route, and L for a direct, attributed Apache-2.0 ingest stays at 2 on the scale. But the decision records that the project declined the per-record Apache cost once, so a direct route needs the user to accept that cost. The text "If the ruling is to exclude MAL-, the product is 0" conflates the two. The MAL-2026-3607 bare-identifier-plus-links handling is the facts+link shape of E.1 item 5, which is consistent.
D2-a (after L487, ending "with no decision recorded.") INSERT a new sentence: **Update 2026-10-03 (gate):** the board recorded the decision at `0641ec1e`, after this section was committed: `MAL-` records are EXCLUDED from the OSV route (`is_openssf_malicious` in `scripts/ingest_cve_nvd_expanded.py`, branch `ws4/wave12-ingest`, not yet on `main`; `SOURCE_LICENSES` row 2.4 states it), with MAL-2026-3607 kept as a bare identifier plus links. The decision is scoped to the OSV route and does not by itself zero a direct, per-record-attributed OpenSSF ingest; it does record that the project declined the per-record Apache cost once, so T1.8 at L=2 needs the user to accept that cost for this route.
D2-b (L619-621) OLD: - **Wave 4: OpenSSF AI/ML subset**, after the N6 ruling (exclude, or attribute per record) and the WS3 decisions (one licence object per row, the obligations enum). If the ruling is to exclude `MAL-`, the product is 0 and this row closes.
NEW: - **Wave 4: OpenSSF AI/ML subset**, only if the user accepts per-record Apache-2.0 attribution for a direct route (N6 excluded `MAL-` from the OSV route at `0641ec1e`; that exclusion does not by itself close this row), and after the WS3 decisions (one licence object per row, the obligations enum). Because 157 of 158 candidates have a CC BY 4.0 GHSA malware twin (E.0-3), the cheaper alternative is to widen the existing GHSA malware filter, which needs neither.
D2-c (L629, after "I treated it as undecided.") APPEND: **Update 2026-10-03 (gate):** the brief was right on substance; the board recorded the exclusion at `0641ec1e`, after this section was written (see the T1.8 update in E.1).

D3. The sensitivity sentence is wrong. CourtListener's V is [E] "plus or minus one step" (L369-370), and at V=3 it is also 24.
(L597-598) OLD: None of the tranche-1 estimates exceeds 24, and 24 is reached only by 0din at its optimistic V.
NEW: None of the tranche-1 estimates exceeds 24, and 24 is reached only at an optimistic V: 0din at V=2, or CourtListener at V=3 (its V is [E], plus or minus one step).

D4. The FTC [M] count omits its field scope (class (b), the label/scope of [M]). The evidence .md L160 scopes the count to title, description, affected and impact; a whole-record count gives 10.
(L400-401) OLD: [M] 6 entries mention FTC or the Federal Trade Commission
NEW: [M] 6 entries mention FTC or the Federal Trade Commission in title, description, affected or impact (10 anywhere in the record, references included)

Evidence and advisories follow in a second message.


## Part 2: evidence and advisories

Evidence and advisories for the tranche-1 estimates gate at 85deb30d (the defects are in my previous message).

WHAT I RE-DERIVED, BY ROUTE
- CourtListener, 1 AI-company defendant in 98,837 dockets. I used a DIFFERENT 8 MB window (bytes L-16M to L-8M of dockets-2026-09-30.csv.bz2), with my own bit-aligned bz2 recovery and my own regex. Result: 102,363 rows, of which 1 has a core AI-company defendant ("State v. Clearview Ai", 2025-12-16), and 121 are NOS 820. The density reproduces. My window is NOT in id order (ids 19,703 to 74.3M, created 2014 to 2026), so the "ids 70.7M-72.05M" describes the author's window only. Product 16 = 2x2x2x2 is correct. V is an honest [E] guess.
- 0din. I shallow-cloned avid-db (HEAD 8eda5f4) and fetched the HF JSONL at revision 9c75d830, in memory only. Result: 80 uuids; 66 AVID reports cite 0din (R0059 to R0124), and all 66 are in HF. The corpus holds AVID-2026-R0059 and R0060 and none of the uuids. The 14 records left are published 2026-02 (3), 2026-03 (1) and 2026-04 (10). reference_urls is empty in all 80. Confirmed. Product 12 is correct.
- OpenSSF: 166 = 73 + 91 + 1 + 1; 0 of 73 pypi and 17 of 91 npm have a GHSA twin in the corpus. My route was the GitHub advisory API per name with GHSA-id membership, not title. It gives 0 pypi and 17 npm (the same 17 names), so the corpus counts are confirmed. The check fires: it returned the 17. The new finding is that 157 of 158 names have an upstream GHSA twin (D1). Product 8 is correct.
- FTC. I ran curl on robots.txt only, with 8 requests at 6 s spacing and no content path. The project UA gets 403 (454 B). "genai_incidents/2.11.0" alone, a browser UA, and the bare contact string each get 200 (3,056 B). The UA with "+https://github.com/emmanuelgjr" alone gets 403, and so do curl/8.0 and curl/8.4.0. So the 403 is UA-pattern-specific: an edge rule that apparently rejects UAs containing a URL, and curl. It is not a robots rule. The served file is User-agent: * with Crawl-delay 5, and /legal-library/ is not disallowed. What that means for conduct: "unreachable via common.py" is true and fail-closed is correct; robots does NOT disallow, so this is not a licence-0 or a robots-0 finding. The refusal is an operator access control aimed at this client. Changing the UA to get past it (for example, dropping the URL) would be evasion, whether done per host or globally for this reason. The only honest routes are an FTC reply (the user sends) or a user ruling. R.4's hold is right. Advisory: E.0-1 says the tranche-1 gate read the file "with curl and a default UA", but curl/8.x now gets 403, so "not every client is refused" still holds only via other UAs.
- CERT/CC 19 / GHSL 18 / EPSS 0. I counted per entry over all fields, case-insensitive for EPSS. kb.cert.org: 19 entries; VU#: 1 (19 if vuls/id/N is counted); securitylab: 18; GHSL- ids: 27 (28 with either); EPSS, epss and first.org/epss: 0 each. Confirmed. Also confirmed: ftc.gov URL in 2 entries; "Malware in" titles 79; research-demonstrated 41; content_license 1,517; MAL- in 1 entry. data/incidents.json is identical to origin/main.

CHECKS
- (a) The cross-tranche ordering cites the tranche-2 section 5.2 products correctly: AVID 54, cvelistV5 36, huntr 36, arXiv 24, EUVD/ANSSI 12, BSI 9, NCSC/JVN/ICO 6, ENISA/EDPB 4, CCCS 3, Garante/CISA/BH 2, zero rows 0. Competition ranks 1,2,2,4,5,6,6,6,9,10,11,14,16,17,20 are right. E.2 uses the corrected huntr 228. Tranche-1 products 16, 12, 8 and 0 are arithmetically correct.
- (b) Classes:
  - Membership keyed on CVE alone: avoided (uuid; ecosystem+name). The GHSA-key claim is wrong (D1).
  - ids vs entries: E.3 explicitly converts line counts to entry counts, correctly.
  - [M] vs [E]: CourtListener V, FTC volume and the OpenSSF ~80 are all [E]. The scope of one [M] is missing (D4).
  - Non-English: E.5 states the rule, and all four sources are English.
  - UTF-8: both evidence files decode as strict UTF-8 (JSON 21,593 B).
- (c) N6: see D2. Exclusion does not force T1.8 to 0, but it makes T1.8 conditional on the user accepting the cost. D1 suggests a better route than either option.
- (d) Invariants: d1a6774b..85deb30d changes 3 docs/specs files (1,391 insertions, 2 deletions: the two placeholder lines). The hunks touch only the Estimates and Ranking sections. origin/main...85deb30d touches only docs/specs; SOURCE_LICENSES.md, data, scripts and ingest have 0 diff. merge-tree of origin/main with 85deb30d gives rc=0 (tree b963cb4b). HEAD is attached (refs/heads/ws0/tranche1-reconstructed); porcelain is empty, which covers the working tree only.

ADVISORY
1. L43, "no gate has passed them yet", is stale now that gate 3 has PASSED. It is outside this diff, but it is the same class as tranche-2 D8. NEW: Scores are the specialist's first pass as corrected by red-reviewer gate 1 (BOUNCE #1, 2026-10-03, corrections applied verbatim) and passed at gate 3 (docs/audits/source-expansion-tranche1-gate3-PASS-2026-10-03.md).
2. L291, "Nothing here changes sections 1 to 6 above": the file has only a numbered section 1. Suggest "Nothing here changes the sections above."
3. The AVID upstream has had no commit since 2026-03-26. That fits 0din's 14 uncovered records all being dated 2026-02 to 2026-04, so the "at most 14" will not shrink unless AVID resumes.
4. My own conduct: the FTC UA diagnosis used non-project UAs, on robots.txt only, at 6 s spacing; I fetched no content path. The CourtListener 8 MB range read and the HF JSONL were processed in memory; nothing was written to the repo. Scratch: the avid-db shallow clone in my session scratchpad.
