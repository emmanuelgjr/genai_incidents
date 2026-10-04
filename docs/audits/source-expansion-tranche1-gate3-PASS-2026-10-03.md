# Source-expansion tranche 1: D41 narrow string check (gate 3): PASS

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on
`ws0/tranche1-reconstructed` @ `d1a6774b`, scope `6608869a..d1a6774b`. The
text below is the gate's message copied as it arrived.

---

VERDICT: PASS (D41 narrow string check of ws0/tranche1-reconstructed @ d1a6774b, scope 6608869a..d1a6774b). No web requests and no repo writes.

DEFECTS: none.

EVIDENCE
(1) All gate-2 replacement text landed verbatim. With whitespace normalised (so the T1.9 wrap-matched target counts), each of the 20 gate-2 replacement strings, Consequential bullets included, appears exactly once in the file. Both ADVISORY items landed: "Gate 2026-10-03: raw curl re-reads; see the cells above." is appended to the T1.4, T1.6 and T1.7 retrieval-method cells, and the S105 bullet now cites the law.cornell.edu verification.
(2) Nothing else moved. git diff --stat shows 1 file, 24 lines in and 24 out. I mapped every changed word in the word diff (porcelain mode) to a declared target; the 2-into-1 hunk at old line 43 is the preamble rewrap. The data/ and docs/SOURCE_LICENSES.md diff against origin/main is empty. HEAD is attached at refs/heads/ws0/tranche1-reconstructed and matches origin at d1a6774b. The working tree is clean (porcelain empty; that covers the working tree only).
(3) No stale text contradicts a gate finding. I searched for the 15 old strings ("pre-gate", "pending shell check", "looks stale", "likely stale", "Services Agreement unread", "first 100 repos" and the others); each returns 0. A scan for "not read", "pending", "not fetched", "unread", "not obtained" and "re-fetch" finds only these, all of which are true or are labelled as the original wording:
- T1.3: "not read from a primary page, provisional", immediately followed by the gate note.
- T1.7: "first.org contact page not read".
- T1.7: "/epss/data_stats was not fetched"; the gate read /epss/data, not data_stats.
- A14 and A16: "Original: ..." clauses.
- T1.5: "not re-fetched here", which describes the specialist's own pass; the S105 bullet records the gate's re-fetch.

ADVISORY (non-blocking): a few first-pass ABSENCE FINDING tags that the gate confirmed are not annotated in their cells: T1.9 ToS (A21) and T1.6's "policy does not specify copyright" (A13). The new results line covers them, so nothing contradicts.

The rows are ready for pipeline-engineer.
