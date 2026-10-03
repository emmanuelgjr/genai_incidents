# Source-expansion tranche 2 — licence pre-rows, string re-check (gate 4): PASS

**Dated record, 2026-10-03. Do not regenerate.** Gate on `eval/source-expansion` @ `5163c10b` (diff `e2b1c988..5163c10b`). Verdict text pasted as delivered (not retyped — see the dated corrections on the gate 1–3 records).

---

VERDICT: PASS — string re-check of e2b1c988..5163c10b on eval/source-expansion. DEFECTS: none.

(1) Gate-3 fixes landed; the two non-literal targets were content-matched and the right text was replaced:
- Line 665 (huntr Retrieval method): now "(all 404 — confirmed genuine by red-reviewer via curl, 2026-10-03)" and "superseded for the quoted clauses, the 404s, the FAQ and the PANW Terms of Use by red-reviewer's curl of raw HTML, 2026-10-03 (gate 2)"; "method-suspect" and "Not shell-verified" are gone from that cell.
- D1 a/b/c landed at line 659; D3 b–e at lines 685, 946, 641, 96 (Key now defines "gate-2 fixed").
- D2 item 33: I ran both commands exactly as extracted from the file text on data/incidents.json (identical at 5163c10b) → 284 and 277, matching the printed figures.
- Cosmetic-only deltas (meaning intact): §7.x for s7.x; "scrape/crawl/automated-access"; em dashes where I had commas/colon; "drops huntr.dev's trailing slash".
- Stale-string sweep of the 5163c10b file: "not yet gated", "not yet run", "need raw-HTML confirmation", "Not shell-verified.**", "not been through red-reviewer", "if the extract is right" — 0 hits.

(2) Nothing else moved: 1 file, 7 in / 7 out; every hunk is one of the targets above.

(3) Line 238 is the ANSSI/CERT-FR Retrieval method — outside the D39 defects; correct to leave for this gate. Advisory for a later tidy (not a defect here): gate-1 item 6 CONFIRMED no access clause on CERT-FR's mentions légales (curl, positive control "Licence ouverte" hit), so that cell's "method-suspect" could become "gate-confirmed (curl, 2026-10-03)"; the status table already says ANSSI is gate-confirmed.

(4) Invariants PASS: origin/main...5163c10b → only the two specs files (1,060 insertions); SOURCE_LICENSES.md and data/ 0 lines; remote ref = 5163c10b; symbolic-ref refs/heads/eval/source-expansion; worktree porcelain empty (working tree only); no HEAD moves, no web requests.
