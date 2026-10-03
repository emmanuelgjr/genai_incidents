# Source-expansion tranche 2: licence pre-rows, string re-check (gate 4): PASS

**Dated record, 2026-10-03. Do not regenerate.** The gate ran on
`eval/source-expansion` @ `5163c10b`, covering the diff `e2b1c988..5163c10b`.

**Provenance:** the text below is the gate's message as it reached the
foreman, copied character for character. The first commit of this file
(`b2e05aff`) said "pasted as delivered" over a retyped and compressed copy.
That repeated the very defect the dated corrections on the gate 1–3 records
describe, so it was replaced within minutes, before anything relied on it.

---

VERDICT: PASS (string re-check of e2b1c988..5163c10b on eval/source-expansion). DEFECTS: none.

(1) Gate-3 fixes landed. The two targets that did not match literally were matched by content, and the correct text was replaced in both:
- Line 665 (huntr Retrieval method) now reads "(all 404 — confirmed genuine by red-reviewer via curl, 2026-10-03)" and "superseded for the quoted clauses, the 404s, the FAQ and the PANW Terms of Use by red-reviewer's curl of raw HTML, 2026-10-03 (gate 2)". "method-suspect" and "Not shell-verified" are gone from that cell.
- D1 a/b/c landed at line 659.
- D3 b-e landed at lines 685, 946, 641 and 96. The Key now defines "gate-2 fixed".
- D2, item 33: I ran both commands exactly as extracted from the file text on data/incidents.json (identical at 5163c10b). They return 284 and 277, which matches the printed figures.
- Cosmetic only, meaning intact: §7.x instead of s7.x; "scrape/crawl/automated-access"; em dashes where I had commas or a colon; "drops huntr.dev's trailing slash".
- Stale-string sweep of the 5163c10b file for "not yet gated", "not yet run", "need raw-HTML confirmation", "Not shell-verified.**", "not been through red-reviewer" and "if the extract is right": 0 hits.

(2) Nothing else moved. The diff is 1 file, 7 lines in and 7 out, and every hunk is one of the targets above.

(3) Line 238 is the ANSSI/CERT-FR Retrieval method. It is outside the D39 defects, and it is correct to leave it for this gate. Advisory for a later tidy, not a defect here: at gate 1, item 6 CONFIRMED there is no access clause on CERT-FR's mentions légales (curl, positive control "Licence ouverte" hit), so that cell's "method-suspect" could become "gate-confirmed (curl, 2026-10-03)". The status table already says ANSSI is gate-confirmed.

(4) Invariants: PASS.
- origin/main...5163c10b touches only the two specs files (1,060 insertions).
- SOURCE_LICENSES.md and data/ diffs are 0 lines.
- The remote ref is 5163c10b.
- symbolic-ref is refs/heads/eval/source-expansion.
- Worktree porcelain is empty (working tree only).
- No HEAD moves and no web requests.
