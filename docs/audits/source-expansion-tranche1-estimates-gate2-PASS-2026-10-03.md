# Source-expansion tranche 1: estimates and ranking, string re-check (gate 2): PASS

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on
`ws0/tranche1-reconstructed` @ `80d8b840`, scope `85deb30d..80d8b840`. The
text below is the gate's message copied as it arrived.

---

VERDICT: PASS on the string re-check of ws0/tranche1-reconstructed at 80d8b840. DEFECTS: none. One optional wording tweak is in advisory 1 below.

(1) D1-D4 landed verbatim, checked by word-diff of 85deb30d..80d8b840:
- D1-a is at E.0-3; D1-b at the T1.8 Overlap; D1-c at the end of the R.2 Basis cell ("excluded; dominated by GHSA: ..."); D1-d in the R.3 Why cell.
- D2-a is at E.1; D2-b replaces the Wave 4 bullet in full; D2-c is in R.5 item 1.
- D3 is the Sensitivity sentence; D4 is the FTC Volume scope.
(2) A1 is at L43 (verbatim, including the gate-3 audit path) and A2 ("Nothing here changes the sections above.") is verbatim.
(3) The E.0-1 quote matches my Part-2 FTC bullet word for word; only the inner double quotes became single quotes. The cited file docs/audits/source-expansion-tranche1-estimates-gate1-verdict-2026-10-03.md exists on origin/main (a9065c1c), and line 45 holds the quoted text. It is not on the branch itself, so the link resolves once the branch is merged to main. The author's own sentence is substantively within what I measured: curl/8.0 and curl/8.4.0 get 403 today, so the earlier curl read does not reproduce. The following "Not every client is refused, so ... does not meet the evidence standard" is also right, on the strength of the other UAs that got 200.
(4) The evidence .md change is a single appended hunk at its end (@@ -182,3 +182,5); line 157 is untouched. The note says only what I measured.
(5) Scope: 2 files, 14 insertions and 21 deletions, all accounted for by D1-D4, A1, A2, the E.0-1 rewrite and the evidence note. origin/main...80d8b840 touches only docs/specs; data, scripts, ingest and SOURCE_LICENSES.md have 0 diff. merge-tree of origin/main with 80d8b840 gives rc=0 (tree 485cff06). HEAD is attached (refs/heads/ws0/tranche1-reconstructed). I made no web requests.

ADVISORY
1. Optional precision tweak to the author's sentence, which is ambiguous. It can read as if the past curl read never happened, but I measured only today's behaviour. If you want it exact:
OLD: The pre-row's earlier reading (that the gate read the file with curl and a default UA) no longer holds for curl/8.x.
NEW: The earlier gate's curl read with a default UA does not reproduce today: curl/8.0 and curl/8.4.0 now get 403.
This does not block the merge.

---

**Foreman note:** advisory 1 is non-blocking and was not applied before the merge. The ambiguity it names is recorded here, next to the sentence's own source.
