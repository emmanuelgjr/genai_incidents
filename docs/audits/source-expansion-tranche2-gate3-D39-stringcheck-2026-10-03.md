# Source-expansion tranche 2: D39 narrow string-check gate (gate 3)

**Dated record, 2026-10-03. Do not regenerate.** (Working agreements 4 and 5.)
This gate ran on `eval/source-expansion` @ `e2b1c988`, covering the diff
`6d77a194..e2b1c988`. The verdict below is reproduced as the reviewer
delivered it, with no edits by the foreman.

**Foreman's classification:** this gate falls within user ruling D39, which
said to apply the gate's text verbatim and then run a string-check gate. All
three defects are text-only, each carries the gate's exact replacement, and
none needs a web re-measure. The foreman is therefore applying them under D39
rather than escalating them as a third bounce. The reviewer flagged that this
classification is the user's call, and it is surfaced to the user.

---

VERDICT: BOUNCE (narrow D39 string-check, eval/source-expansion @ e2b1c988) — 3 text-only defects, each with exact replacement text; no web re-measure needed. (Post-escalation gate under D39 — your call whether this counts as a third bounce.) Everything else in the diff PASSES.

DEFECTS
1. D1 only partly landed — 1E.1 License cell (line 659): the §7.1 quote is now marked verified, but the cell's own header still says the §7.2/§7.3/§4.4 quotes "need raw-HTML confirmation" — my gate-2 D1 stated those three are CONFIRMED verbatim. Replace:
   a. "(WebFetch 2026-10-03, **summarising converter — quotes below are its output and need raw-HTML confirmation**)" → "(WebFetch 2026-10-03; §7.1, §7.2, §7.3 and §4.4 below verified verbatim against raw HTML by red-reviewer via curl, 2026-10-03)"
   b. "The tool reported no clause on public reuse of published reports and none on automated access." → "No clause on public reuse of published reports and no scrape/crawl/automated-access clause appears in the terms (red-reviewer, curl, 2026-10-03)."
   c. "Consequence if the extract is right:" → "Consequence:"
2. Item 33's command does not produce the number printed next to it (line 958). The applied `grep -oE 'huntr\.(com|dev)/bounties/[0-9a-f-]*' data/incidents.json | sort -u | wc -l` returns 277, not 284 (re-run locally on data/incidents.json; identical at HEAD) — the hex-only class drops huntr.dev's trailing slash, so it counts host+ID, not URLs. My gate-2 D3 said only "match (com|dev)" without giving the pattern, so the gap is partly mine. Replace the clause from "and `grep -oE" through "in 210 of 13,361 entries." with:
   and `grep -oE 'https?://(www\.)?huntr\.(com|dev)/bounties/[^"[:space:]\\]*' data/incidents.json | sort -u | wc -l` for the distinct-URL count (284 at 6d77a194 and e2b1c988), and `grep -oE 'huntr\.(com|dev)/bounties/[^"[:space:]\\/?#]+' data/incidents.json | sed -E 's#.*/bounties/##' | sort -u | wc -l` for distinct bounty IDs (277); 210 of 13,361 entries carry one. (The hex-only form `[0-9a-f-]*` also returns 277 because it drops huntr.dev's trailing slash.)
   (Both commands re-run now: 284 and 277.)
3. Stale "not gated / method-suspect" status text contradicts the applied D2/D4 text (5 lines):
   a. Line 665 huntr Retrieval method: "`/guidelines` (all 404, method-suspect)" → "`/guidelines` (all 404 — confirmed genuine by red-reviewer via curl, 2026-10-03)"; and "Source kind: **rendered HTML via a summarising converter — weak tier. Not shell-verified.**" → "Source kind: rendered HTML via a summarising converter — superseded for the quoted clauses, the 404s, the FAQ and the PANW Terms of Use by red-reviewer's curl of raw HTML, 2026-10-03 (gate 2)."
   b. Line 685 CISA Retrieval method: "**Not shell-verified.**" → "Shell-verified by red-reviewer at gate 2 (2026-10-03) for §105, the website-policies 404 and the /site-links policy pages; the CSI PDF (403) and its co-sealer list remain unverified."
   c. Line 946: "(tranche 1, section 1E; **not yet run**)" → "(tranche 1, section 1E; run by red-reviewer at gate 2, 2026-10-03)"
   d. Line 641: "and have **not been through red-reviewer**." → "and were checked by red-reviewer at gate 2 (2026-10-03); results folded in per D39."
   e. Line 96 Key: "*not yet gated* — added after the gate (section 1E)." → "*gate-2 fixed* — added after gate 1 (section 1E); checked and corrected at gate 2 (2026-10-03)." (The status table uses "gate-2 fixed", which the Key never defines; "not yet gated" is now unused.)

PASSED
(1) Verbatim landing: D1 §7.1 text + "Vulnearability" note + added §7.2 sentence exact (ellipsis rendered as Unicode "…" — fine); D2 PANW ToU quote, crawling-context, FAQ quote, "Score 1 (c) still follows", deletion of the "no 404 from this tool" sentence — two harmless rewordings ("also genuine 404s" dropped "are"; "No automated-access clause in code of conduct or participation terms") with meaning intact; D3 count text; D4 §105 exact + both sources, TLP quote exact, site-links pages, IP-policy list, CSI 403 unverified, false huntr cross-ref removed; D5 CSA full sentence; D6 both places incl. line-41/42 note; D7 both Dutch sentences exact, gloss labelled, Disallow /documenten; D8 present (placed after the redistribution clause — acceptable); D9 scale clause; JVN image/inferred advisory.
(2) No undeclared moves — the only other changes are the declared ones (status tables, Gate-2 line, status sentence, gloss, items 31/32 rewrites). Item 31 now says what I measured: all three genuine 404s, WebSearch listing stale; item 32 likewise.
(3) ACSC = 1 in summary and row; both cite the new scale clause "a grant known only from a search extract whose primary page could not be reached (provisional)" (D39).
(4) Invariants: 6d77a194..e2b1c988 = 1 file, 27/27 lines; origin/main...e2b1c988 = two specs files only; SOURCE_LICENSES.md and data/ 0 lines; remote ref = e2b1c988; HEAD refs/heads/eval/source-expansion; worktree porcelain empty (working tree only); I did not move HEAD and made no web requests.

---

**Dated correction, 2026-10-03 (foreman): this record is NOT byte-verbatim.** The header says the verdict is reproduced "with no edits by the foreman". That is true of substance, and false of punctuation and phrasing. The foreman transcribed this text from the gate's message and introduced em dashes, "→" arrows and some compressed phrasing that the delivered message does not carry. **Found by** license-auditor during the D39 gate-3 application: two of the gate's replacement strings, as quoted here, did not occur literally in the target file. The file had a comma where this record shows an em dash. **Consequence:** do not use this record as an exact-match source for `str.replace` or Edit operations. Locate each target by its content and confirm that it is unambiguous. The defects, figures, quoted page clauses and verdict are unaffected. The original text above is preserved under working agreement 4.
