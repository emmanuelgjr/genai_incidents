# Wave 1-2 ingest PR: D45 narrow check (gate 3): PASS

**Dated record, 2026-10-04. Do not regenerate.** This gate ran on
`ws4/wave12-ingest` @ `29e98fee`, scope `de36bbb6..29e98fee`. The text below is
the gate's message copied as it arrived. Earlier gates:
`wave12-ingest-gate1-verdict-2026-10-03.md` and
`wave12-ingest-gate2-verdict-2026-10-04.md`.

---

VERDICT: PASS. Narrow check under D45 on ws4/wave12-ingest @ 29e98fee, scope de36bbb6..29e98fee. Both gate-2 defects are closed and I found nothing new. On this evidence the branch is ready to merge.

DEFECTS: none.

EVIDENCE (throwaway clone at 29e98fee; repo trees not touched)
(1) Empty-result guard and carry, checked through main() with my own stubs, not the author's tests:
- Empty run: I stubbed every module fetch_* to return [] and ran the real main(). It printed the refusal, "[error] 0 entries collected across all phases -- refusing to overwrite". The file stayed byte-identical (sha256 before and after equal) at 9,263 rows.
- Non-empty run: I ran main() on a temporary copy of the output file, with fetch_osv fed the real fixtures GHSA-ordinary.json and MAL-2026-2144.json through the real OSV conversion path. The written file has 2 rows: CVE-2025-00001, the ordinary record converted, and MAL-2026-3607, the bare row ("Bare identifier for OpenSSF..."). MAL-2026-2144 was excluded.
- Mutation: I restored only scripts/ingest_cve_nvd_expanded.py to its de36bbb6 version, which is the old ordering. test_main_refuses_to_overwrite_committed_file_with_an_empty_run FAILED; the non-empty test passed, as expected. After restoring: clean. So the new test genuinely guards the reorder.
(2) D2 text: both of my sentences are present verbatim in docs/SOURCE_LICENSES.md after whitespace normalisation: the Ingested-by line (True) and the Measured sentence (True). The old "filtered by the WS4-T4 allowlist" phrase is gone, and so is "(down from 384)". The cell reads "curated seed of 88 entries". The delta md gets a dated note in section 5, with the original text kept, as working agreement 4 requires.
(3) Seed: I parsed ECOSYSTEM_SEED at both revisions. de36bbb6 has 90 items and 88 unique; 29e98fee has 88 items and 88 unique; the sets are equal. `git diff --quiet de36bbb6 29e98fee -- data/` exits 0, and a full rebuild at 29e98fee is byte-identical (porcelain empty after the build).
(4) Redirect guard: the only change is `urlparse(newurl).path != "/robots.txt" and not robots_allowed(...)`. The check is skipped only when the redirect target IS a robots.txt file, which is always fetchable by convention, and pacing still applies to it. Every other redirect target is robots-checked as before. All three redirect tests pass:
- refused-before-any-request: disallowed host, never contacted;
- followed-and-paced;
- the new robots-txt skip test.
(5) Tests and invariants:
- pytest: 563 passed, 1 xfailed.
- Build: exit 0, "15666/15666 entries valid".
- check_stats_drift: clean.
- No D lines in `git diff --name-status 9604752f 29e98fee`. PROGRESS.md is not in the diff.
- The ingest-script egress profile is unchanged (no new network or subprocess calls in this diff).
- Existing-entry delta is unchanged from my gate-2 measurement (0 changed), because data/ is byte-identical to de36bbb6.

ADVISORY
- One row in the author's re-sample table, CVE-2026-94486 (vercel/next.js), looked like a false positive. I read it: the vulnerability is in Next.js's dev-server Model Context Protocol endpoint, so it is in scope as an MCP endpoint vulnerability. Not an issue.

STATE: target worktree refs/heads/ws4/wave12-ingest @ 29e98fee, main tree refs/heads/main; both attached, both porcelains empty (working trees only).
