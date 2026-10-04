# Wave 1-2 ingest PR: red-reviewer re-gate (gate 2): BOUNCE #2, escalated to user

**Dated record, 2026-10-04. Do not regenerate.** This gate ran on `ws4/wave12-ingest` @ `acba9032`, plus the text-only `de36bbb6`. The text below was saved as received and concatenated by shell.

---

VERDICT: BOUNCE. This is BOUNCE #2 on the wave12 ingest, so the protocol requires escalating to the user. The remaining fix is small: one reorder of a block plus one test, and two text cells. Everything else passes, including all seven gate-1 defects.
Gated: acba9032. I also checked de36bbb6, which is on the branch now: it is a text-only change, (CVE) to (CVE™) in NOTICE-DATA and row 6.2. I verified it against cve.org's own `src/views/Legal/TermsOfUse.vue`, which reads `(CVE<sup>&trade;</sup>)`. It is correct and does not affect data.

DEFECTS
1. A1's carry defeats the guard against overwriting the committed file with an empty result (a regression of the gated WS0-T4 A6 guard). In `scripts/ingest_cve_nvd_expanded.py` main(), `out = carry_bare_identifiers(out, prev_rows)` runs BEFORE `if not out:`. A fully blocked run collects 0 rows, the carry appends the MAL-2026-3607 bare row, `out` becomes non-empty, and the committed file is overwritten with 1 row.
PROVEN in a scratch clone: I stubbed every `fetch_*` in the module to return [] and ran `main()`. The file went from 9,263 rows to 1 ("Wrote 1 entries"). Restored afterwards. The pre-change code at d49d9647 refused this case.
FIX: make the carry run only when the fresh collection is non-empty, i.e. replace the block with
```
    if not out:
        print(... existing refusal message ...)
    else:
        try:
            prev_rows = json.loads(OUT_FILE.read_text("utf-8")) if OUT_FILE.exists() else []
        except ValueError:
            prev_rows = []
        out = carry_bare_identifiers(out, prev_rows)
        OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print(...)
```
Add a test that runs `main()` with the fetchers stubbed (to [] and to a small non-MAL set) on a tmp copy of OUT_FILE. Assert the empty case leaves the file byte-unchanged, and the non-empty case writes the set plus the MAL-2026-3607 bare row. That test is also the real regeneration test that (4) asks for (see below).

2. Two live SOURCE_LICENSES 6.2 phrases are wrong. The same figure is also in the dated delta md section 5; add a dated note there rather than editing it.
(a) The "Ingested by" line still says "filtered by the WS4-T4 allowlist", while the Action cell says that allowlist does not exist. Replacement: `*Ingested by:* `scripts/ingest_cvelistv5.py` to `ingest/wave12_cvelistv5.json` (wave 1; CVE JSON 5 records, filtered by `scripts/ai_relevance.py`; the WS4-T4 allowlist does not exist yet; owner pipeline-engineer).`
(b) "Measured: 206 description-only rows (down from 384)" compares two different populations. 384 was the cvelistV5-only entries out of 2,240 (my count). 206 is all 2,502 emitted cvelistV5 rows, including those that fold into AVID entries. The like-for-like pairs are 454/2,705 against 206/2,502 (all emitted rows) and 384/2,240 against 150/2,046 (cvelistV5-only entries). Replacement: `Measured: description-only rows fell from 454 of 2,705 emitted to 206 of 2,502 (cvelistV5-only entries: 384 of 2,240 to 150 of 2,046); a 40-row re-sample of that stratum found 40 plausible, 0 clear false positives, 1 borderline.`
Also "a curated seed of 90 entries": the list has 90 items but 88 unique, because mindsdb and crawl4ai each appear twice. Say "88" or dedupe the list.

CHECKS (1)-(6), all by my own route, in a throwaway clone at acba9032
(1) Gate-1 defects:
- D1: v1_month() is used for date and window. 55 arXiv rows; 0 have a date different from the id's YYMM; 0 are before 2025-10. All 8 out-of-window ids I named are gone.
- D2: AVID+CVE entries (125) are now CVE-TOU / `cve-cna-via-avid`. AVID-only entries (79) are MIT with original prose. cvelistV5 entries (2,046) are CVE-TOU.
- D3: see (2).
- D4: entry 3 now reads "not used, HTTP route taken", with my text.
- D5: (a), (b), (d) and (e) are done; (c) is done apart from defect 2 above.
- D6: none of the 19 named CVEs is held by any entry in the corpus or in the ingest rows; they are now test fixtures. Rules: bounded gpt-N, Linux-CNA rejection, credit stripping, and a second-signal requirement.
- D7: the trademark line now matches cve.org's footer.
(2) Re-sample, cvelistV5-only description-only stratum (150 entries; 206 across all emitted rows), n=40, seed 1004 (not the author's seed 7):
- 0 clear false positives; Wilson 95% CI for precision 91.2-100.
- 4 borderline: AIWU AI-chatbot plugin data exposure; Cognos "Agentic AI assistant" race; TREK SSRF through a configurable LLM base URL; an AI-fundamentals tutorial repo. Strict precision 36/40 = 90% (CI 76.9-96.0).
- The 12 new seed products (nanobot, docling, firecrawl, llava, WeKnora, TensorZero...) are all AI tools in the matches I read.
- D3 prose: on all 87 AVID third-party rows, the longest substring shared with the old verbatim text is 32 characters, and those are product names ("NemoGuard Jailbreak Detect", "ing OpenAI Sora. The "). The text is original template prose that names the disclosure's host and says "its text is not reproduced here". The titles stay verbatim, as the row says; short titles are acceptable.
(3) A4 redirect handler:
- `urllib.request._opener` holds `_CheckedRedirectHandler`, so it is installed process-wide.
- Mutation 1: replacing `install_opener(...)` with a no-op made both redirect tests FAIL.
- Mutation 2: removing `_rate_limit` from the handler made the pacing test FAIL. After restoring: 33 passed.
- Live smoke: fetch_once of api.github.com/repos/avidml/avid-db/tarball/main called robots_allowed for api.github.com AND codeload.github.com, and returned 2,017,520 bytes with sha256 c0d5f5e6..., which matches the provenance file.
- robots_allowed is True for codeload.github.com, release-assets.githubusercontent.com and objects.githubusercontent.com, so existing GitHub-asset ingests are not newly blocked.
(4) A1 durability: the carry itself works. I took the committed rows minus MAL, carried them, wrote the file and rebuilt: exit 0, no split-guard trip, 0 entries changed against acba9032. But the "regeneration" tests do not regenerate:
- `test_bare_identifier_carry_fires_without_it` asserts only its own precondition, so it cannot fail when the carry is removed.
- `test_writer_calls_carry_bare_identifiers` is a source-string grep. It would still pass with the call placed after the write, and it did not catch defect 1. The main()-level test in defect 1 replaces both.
(5) quality_tier change:
- The new line in `normalize_entry` honours only `auto`. Only the three wave12_* files carry an explicit `"quality_tier": "auto"` (55, 270 and 2,502 rows); no pre-existing ingest file does.
- Independent per-field delta 9604752f to acba9032: 13,361 to 15,666, missing 0, new 2,305 (INC-14911..INC-17215, contiguous), 0 existing entries changed. The fire test caught a one-field mutation.
- All new entries: quality_tier auto 2,305, tier feed 2,305.
- The ID numbering differs from d49d9647's, which is harmless: origin/main stats.json is still 13,361, so those IDs were never published.
(6) Build and invariants:
- Full build at acba9032: exit 0, "15666/15666 entries valid", integrity clean, porcelain empty, so it is byte-identical. The base 9604752f snapshot plus the acba9032 inputs reproduces the committed incidents.json (b6dfc2c1...) and min.json (da45ad03...) byte for byte.
- check_stats_drift is clean. pytest: 562 passed, 1 xfailed.
- `git diff --name-status 9604752f acba9032` has no D lines. PROGRESS.md and id_deprecations.json are untouched. merge_and_dedupe changed only by the 5-line `auto` clause.

ADVISORY
- The redirect handler also governs robots.txt fetches, because `_get_robots_parser` uses urlopen. A robots.txt that redirects to another URL on its own host, before that host is cached, re-enters robots_allowed and recurses, and RecursionError is not caught. This is a rare edge and it fails loudly. A guard such as "skip the robots check when newurl's path is /robots.txt" would close it.
- The arXiv window compares at month granularity, so papers from 2025-10-01/02 count as in-window. This is cosmetic.

STATE: the target worktree is attached (refs/heads/ws4/wave12-ingest at de36bbb6) and the main tree is attached (refs/heads/main); both porcelains are empty, which attests to the working trees only. All mutations and builds ran in the scratch clone, which I restored to clean after each run.
