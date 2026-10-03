# Source-expansion tranche 2: final string re-check (gate 6): PASS

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on
`eval/source-expansion` @ `946a7e55`, covering the diff `fb64ea10..946a7e55`,
by the same fresh red-reviewer that ran gate 5. The text below is the gate's
message copied as it arrived.

---

VERDICT: PASS on the string re-check of eval/source-expansion at 946a7e55. DEFECTS: none.
(1) All of D1-D9 landed verbatim. I checked every NEW string against 946a7e55 with whitespace normalised: each appears exactly once. The R sentence appears 5 times, at the BSI, JPCERT, AP, CNIL and ANPD anchors, and the Garante variant is present. Every stale string is gone, with 0 hits each: "(302 not in", "~120/yr", "rule order", "(placeholder)", "`status: active", "single digits", "6,986 CVE entries", "911 of 1,213", "**233 (63%)", "63% of". D1-h was inserted after the blank line that follows L33 ("@@ -34,0 +35,2"), so L30-33 are untouched. D7: the JSON diff is one line, with byte F6 replaced by C3 B6, and json.loads of the strict-UTF-8 decode of `git show 946a7e55:` now succeeds (28,820 bytes).
(2) Scope: `git diff --stat fb64ea10 946a7e55` shows 3 files, 27 insertions and 31 deletions. The word-diff shows only the D1-D9 edits; nothing else moved.
(3) Invariants: origin/main...946a7e55 touches only the 4 docs/specs files. SOURCE_LICENSES.md, data, scripts and ingest have 0 diff. `git merge-tree --write-tree origin/main 946a7e55` returns rc=0 (tree d94ff54d). The worktree HEAD is still attached at refs/heads/eval/source-expansion, and I made no web requests.
