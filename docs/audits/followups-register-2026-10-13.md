# Follow-up register (2026-10-13, after the v2.13.0 release)

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4).
> - **How it was built:** a read-only sweep of PROGRESS.md at `ca3777b6`, MASTER_IMPROVEMENT_PLAN.md, the v2.13.0 cut package, `docs/releases/v2.13.0.md` and `docs/outreach/README.md`.
> - **Compiled by:** an Explore agent, transcribed by the foreman.
> - **Line numbers:** PROGRESS.md at `ca3777b6`. "notes" means `docs/releases/v2.13.0.md`. "CP" means the cut package.
> - **Exclusions:** items closed later on the board are left out. All v2.13.0 cut obligations (CP §5, §4R) are closed.
> - **Reliability:** everything here is testimony. Re-measure an item before acting on it.

## (a) User decisions and actions

| # | Item | Origin | Why open | Depends on |
|---|---|---|---|---|
| a1 | Label the 150-row precision sheet (`human_label` and `human_by`). Then run `wilson_ci.py --render-datasheet` and `evaluate_ai_relevance.py`. | 132, 1175; CP §5; notes :351-355 | D76 ratified "pending". No precision figure exists. | — |
| a2 | OECD/AIID freeze stage 2: lift or narrow it. Includes the 17 D42 changes (7 merges + 10 retitles) and about 94 AIID-only rows + 6 AIID-authored retitles. | 86, 133, 1477-1481; notes :356-361 | D71 holds everything until stage 2. The `ws4/refresh-tripwire-42` evidence is not on origin. | Then b9 |
| a3 | Licence position on the OECD `title` text (LLM output; 3,937 rows) | notes :362-366 | Unresolved | Part of a2 |
| a4 | AIRI: skip, pause or retire the dead ingest (14 consecutive 404s). A review is committed for 2027-01-07. | 85; D63; notes :367-370 | Needs the user | b2 |
| a5 | Go or no-go for the first `atlas-refresh` dispatch. It has never run; its first cron run is 2026-11-03. | 89 | Needs the user's go | — |
| a6 | Confirm the repo-cleanup plan | 92-100 | The inventory is in flight | — |
| a7 | Approve source waves 3 (CourtListener bulk + 0din) and 4 (OpenSSF or a wider GHSA filter). FTC is on hold. | 2131, 2224, 2232 | Owed since v2.12.0 | e2 for FTC |
| a8 | Policy for duplicate-rejected CVEs (3 entries): re-point or retract? | 2133 | No ruling | — |
| a9 | N11: review the 410 wave-12 rows suppressed by the issue-#88 list | 2134, 2325 | No review | — |
| a10 | E5 / WS1-T4: rename the scope, or add `ai_system_type` tagging (the plan recommends tagging) | 4516 | Pending | Gates WS1-T4 |
| a11 | WS6-T4: a real TAXII server or honest labelling. Also: `CHANGELOG.md:1008`, "Static TAXII 2.1 endpoint", needs to be superseded or corrected. | 4688, 3852 | Undecided | Gates WS6-T4 |
| a12 | MAL-2026-3607 kept as a bare identifier so INC-08450 does not split | 2213 | Open | b20 |
| a13 | E8: `main` has no branch protection | 4510 | Routed to Phase 3 | WS4-T7 |
| a14 | Two high Dependabot alerts | 2679 | No closure | — |

## (b) Engineering follow-ups

| # | Item | Owner | Origin | Status |
|---|---|---|---|---|
| b1 | Weekly refresh repair: D66 decouple, `if: always()` on source-health enforcement, keep the cve-sweep output | WS4 | D66; 66-84 | **IN FLIGHT** (`ws4/v2130-refresh-decouple`) |
| b2 | D63 overdue-review alert | WS4 | D63 | **IN FLIGHT** (same branch) |
| b3 | a11y workflow fails on main (axe critical/serious) | WS6 | 88-90; 3930 | **IN FLIGHT** (`ws6/v2130-a11y-fix`) |
| b4 | The precision status line says "authorised" even when `problems` is non-empty | WS2 | 47; `validate.py:920-929` | open |
| b5 | OECD AIM rename, data part: `ingest_external.py:233/:241` | WS4 | 324, 127 | Needs a field-level delta |
| b6 | `VERSION = "2.0.0"`; WS6-T1 `data_version` / `fetch_latest()` are absent | WS6 | 130, 4689 | open |
| b7 | WS3 ID-reuse audit: 591 multi-title IDs | WS3 | D70 | Spec in docs/audits |
| b8 | ATLAS N-d: `ingest_external.py:68` parses `ATLAS-2026.06.yaml` | WS4 | 1896 | Moves data, so needs a delta |
| b9 | Stage-2 machinery (S7/S8/S9; A6, A7) | WS4 / WS0 | 1462-1481 | After a2 |
| b10 | Stage-1 test fixture should use `git archive HEAD` (low priority) | WS4 | 951 | open |
| b11 | Slow marker for the stage-1 test file (~412 s) | WS4 | 988 | open |
| b12 | INCLUSION §5 counts sit outside the drift surfaces | WS6 | 1034 | open |
| b13 | The "26 new DISPUTED" log line counts existing disputes | WS4 | 1520; `ingest_cve_rejections.py:396` | open |
| b14 | 8 NOT_IN_CVELIST ids are not flagged; `cve-enrich` has no concurrency group | WS4 | 1612 | open |
| b15 | Single-source the ASI names: render_markdown.py and app.js | WS2 / WS6 | 870 | open |
| b16 | D73 advisories: retained rows bypass `_apply_history`; the later-day test is thin | WS4 | 776-777 | open |
| b17 | Item 5 advisories (dated-dir pin, newest-dir CLI, hand-typed figure) | WS2 | ~1229-1236 | open |
| b18 | Drift-check advisories (tomllib on 3.10, id false positives, VERIS case) | WS6 | 2004-2080 | open |
| b19 | ATLAS advisories (STIX validator, lint scope, tactic removal, validate.yml on bot PRs, guard inputs) | WS4 / WS2 | ~1915-1979 | open |
| b20 | N7: possible over-merge in INC-08450 | WS1 | 2331 | open |
| b21 | N3: no Crawl-delay parsing; no RFC 9309 wildcard support | WS4 | 2361 | open |
| b22 | WS4-T16: `^\d+$` over-matches Unicode digits (`ingest_oecd_aim.py:151`) | WS4 | 3975 | open |
| b23 | WS4-T18: strip query strings from reference URLs (data change) | WS4 | 3406 | Needs a ruling |
| b24 | WS6-T10: `check_dead_filters.py` is case-sensitive | WS6 | 3447 | open |
| b25 | `persist_refresh_state.sh`: `--force` and `[skip ci]` are untested | WS4 | 4321 | open |
| b26 | WS4-T11 fixture: bucket counts are equal | WS4 | 4007 | open |
| b27 | Package/validator parity on null-`into` supersession | WS4 + WS3 | 2674 | open |
| b28 | STIX edition test independence | WS6 | 2675 | open |
| b29 | TAXII template hard-codes "currently `-2026`" | WS6 | 2569 | open |
| b30 | WS2-T5: `"fatal" in text` matches "non-fatal" | WS2 / WS4 | 4714 | open |
| b31 | Publish `high_water_id` in stats.json | WS6 / WS4 | 4713 | open |
| b32 | Generate NOTICE-DATA from a manifest | WS4 + WS0 | 4690 | Phase 2 |

## (c) Docs follow-ups

| # | Item | Owner | Origin |
|---|---|---|---|
| c1 | OECD AIM rename sweep, docs part: README:203/:302, DATASHEET:38, paper:60, flow.py:17, auto-refresh.yml, Makefile | WS6 | 324, 127 |
| c2 | Older README "Previous release" paragraphs use relative links, which break on PyPI | WS6 | 151, 128 |
| c3 | Supersession note for `ws6-v2130-export-integrity-2026-10-11.md:177-178` | WS6 | 211 |
| c4 | WS2 taxonomy-card guard docs (the assertion already exists at `tests/test_owasp_asi_naming.py:433-440`) | WS2 | 130 |
| c5 | SOURCE_LICENSES row for the 21 `OWASP-*` ids (18 GENAI + 3 AIX, 6 rows) | WS0 | CP §7 |
| c6 | SOURCE_LICENSES row for the OWASP LLM Top 10 (CC BY-SA) | WS0 | 871 |
| c7 | N4: no rows for `research_incidents.json` / `threat_reports_incidents.json`; the arXiv full-text check | WS0 | 2364 |
| c8 | F2: SOURCE_LICENSES §2.5 "one lifecycle fact per CVE" now omits `disputed` | WS0 | 1562 |
| c9 | S6 OECD docs: INGESTION_CONDUCT:122, SOURCE_LICENSES §1.2a, the HF card | WS0 | 1461 |
| c10 | OECD memo :342 `ruled_by` → `decided_by` (needs a dated correction) | WS0 | 1251 |
| c11 | Re-check the SOURCE_LICENSES §1.5 "Scrape-permitted" cell | WS0 | 1747 |
| c12 | Item-2 warden notes N-a, N-b, N-e, N-f, N-g, N-h | WS6 / WS5 / WS0 / WS3 | 1897-2007 |
| c13 | ATLAS docs advisories (CORRECTIONS row 1 citations, "up to four" requests, build-target line) | WS4 / WS5 | 1913-1979 |
| c14 | VERSIONING fixes: the step-3 min.json claim; the step-2 UA example still says 2.9.0; the step-5 literals list | WS6 | 2003, 2676, 2033 |
| c15 | README banner SVGs say "CC-BY-4.0 data" despite the ASI carve-out | WS6 / WS0 | 511 |
| c16 | HF card says "real-world and research incidents" | WS6 | 2142 |
| c17 | v2.11.0 leftovers (OpenCTI docstring, "(the corpus)" gloss, `source_name` docs, site UI fixes missing from the CHANGELOG) | WS6 | 2566-2572 |
| c18 | ID_POLICY §3 / D31 rider | WS3 | 2678 |
| c19 | D15 directional criterion not propagated | WS6 / WS0 | 4701 |
| c20 | Reuse lint incomplete (CC-BY-4.0, MIT and Apache texts missing; 109 files without licence info) | WS0 | notes :375-379 |
| c21 | Cosmetic visuals (og URL clip, runner font, ASI07 label clip, banner padding) | WS6 | ~548-577 |

## (d) Plan tasks not done (`MASTER_IMPROVEMENT_PLAN.md`; Phase 1 was declared complete on 2026-07-31)

- **d1, Phase 2 exit:** WS1-T1, T2, T3 and T4; WS3-T1, T2 and T6; WS2-T3; WS6-T8. **None is done.** WS1-T4 needs a10.
- **d2, Phase 3 exit:** WS2-T1, T2, T4 and T5; WS4-T1, T4 and T5; WS1-T5 and T6; WS7-T3; WS6-T7; WS5-T5. WS2-T2 is blocked on e4.
- **d3, Phase 4 and others:** WS3-T3 and T4; WS4-T3, T6, T7 and T8 (cosign); WS5-T1, T2b, T3, T4 and T6; WS6-T3, T4 (see a11) and T6; WS7-T1, T2 and T4.
- **d4, partly done:**
  - WS6-T1: VERSION, `data_version` and `fetch_latest` are not done.
  - WS6-T5: the per-corpus pages are deferred.
  - WS4-T2: CVSS rescores and the AIID re-diff are not done.

## (e) Outreach (the user sends)

| # | Item | Status |
|---|---|---|
| e1 | ENISA/EUVD reuse email | Drafted 2026-10-03, **not sent** |
| e2 | FTC outreach about the 403 rule on the project UA | **Not drafted** |
| e3 | OECD AIM | Sent 2026-07-31. The follow-up window (2026-08-21) passed with no reply recorded. |
| e4 | Annotator (Mayur021) | Sent 2026-07-27. The follow-up was due around 2026-08-03, and no annotator has committed. This blocks WS2-T2. |

## Items the compiler was unsure are still open

- **U1, WS0-T4 clause 2.** The task-table cell is probably stale: outreach README:21 says the OECD send closed it.
- **U2, the AIRI-hold "todo" row.** Probably stale: superseded by D57.
- **U3, escalation cells E6, E20, E21, E22, E23 and E24.** Each has later closing evidence, so the cells are stale.
- **U4, the E13 counsel step.** It is unclear whether counsel is still intended.
- **U5, auto-refresh not running `render_docs_stats`.** Pytest may already catch the resulting drift.
- **U6, WS4-T18 as a class task.** 0 pre-signed URLs exist today.
- **U7, older entries with no recorded closure:**
  - the `modified`-bump policy;
  - N10;
  - N2;
  - the `load_incidents` doc;
  - the cache-write audit;
  - the STIX marker CI check;
  - AIRI causal intent;
  - the Dependabot count.
- **U8, D66 wording mismatch.** The board says "carry AIRI/AIAAIC/KEV/cve-sweep while OECD/AIID held". The notes :360 say "decouple the AIID step from the OECD step".
- **U9, WS6-T7 Zenodo redeposit.** It is effectively done (every release mints a version DOI) but is not marked.
- **U10, the precision sheet.** It is no longer CI-forcing, since D76 defused the 2.14.0 tripwire.
- **U11, STIX `revoked` / R5.** Excluded by the D75 ruling. It remains a disclosed limitation.
- **U12, "card guard docs".** The assertion already exists. What remains is unspecified.

---

## Update, 2026-10-13 (later the same day): added after the licensing, rewrite, precision and refresh work

> Appended under agreement 4. Nothing above was edited. Items that were *closed* today are listed first, so a reader does not act on a stale line above. Each item cites the board entry that records it.

### Closed today (do not act on these lines above)
- **Refresh repair, all merged.** The weekly refresh had not landed since #97 (2026-07-27). The repair (merge `2e60e395`) includes:
  - D66 OECD/AIID hold;
  - D63 overdue alert;
  - D95 AIRI monthly retry;
  - the AIAAIC loud-fail fix, for the renamed `Incident headline` column;
  - D107 0.9 yield floor;
  - held inputs moved outside the tree, behind a guard.

  Test refresh run 38366793761 was dispatched from main.
- **Licensing follow-ups c5-c11 and D96-D104.** Merged.
- **D97/D98 description rewrites** (INC-02646, INC-03233, INC-02436) and the **INC-02382 wrong-CVE fix**. Merged, with CORRECTIONS rows.
- **Licensing-surfaces sweep**: 14 of the docs-warden's 15 findings. Merged.
- **WS2 precision follow-ups** (D105/D106). Merged.
- **c17** (the released [2.11.0] CHANGELOG): closed won't-fix, D102.

### (a) New user decisions
- **A1. Over-merge split.** INC-00924 absorbs 6 unrelated Q1-2026 OWASP ids, INC-02646 absorbs 9 Q2-2025 ids, and INC-03233 absorbs 3 Q1-2025 ids. Incidents such as the DeepSeek breach, CVE-2025-23254 and the Meta agent leak therefore have no row of their own. Splitting them is an ID-policy and data change, using the WS4-T19/D28 split machinery.
- **A2. Copied headlines.** INC-02646's title still equals the OWASP round-up heading (7 of 7 tokens). D97 rewrote descriptions only. Five RES titles equal post headlines and were kept under D98. Should titles be paraphrased too?
- **A3. AIRI.** It has been dead since 2026-05-31, with 15 consecutive failures. It will go red on the first Sunday of each month, starting 2026-11-01. Retire it, or keep retrying?
- **A4. The six non-shipped OWASP ingest rows** in `ingest/avid_owasp_incidents.json` that still hold OWASP text: Q1-2025-03, Q2-2025-02 and Q1-2026-04 verbatim; Q1-2025-02, Q1-2026-05 and Q1-2026-06 near-verbatim. They are covered by the NOTICE attribution and by D101 (upstream terms). Rewrite them, or leave them?

### (b) New engineering follow-ups
- **B1. D96 is due next release.** Paraphrase the OWASP LLM descriptions and scope text in the 2026 and 2025 mapping files and the crosswalk, then narrow the carve-out to codes and names.
- **B2. Refresh A1.** `check_headline_system_sanity` filters on `r[0]` rather than `r[col["id"]]`, so it is blind if the ID column moves. The 0.9 floor backstops it, except under the override. One-line fix.
- **B3. Refresh A2.** Surface the yield-drop override in `GITHUB_STEP_SUMMARY` and in the PR body.
- **B4. CVE sweep yield floor.** This needs a design decision. Also, the non-weekly ingesters (cvelistv5, nvd_expanded, avid, arxiv, redteam, external) have no empty-result guard.
- **B5. The OX MCP row's date.** The row says 2025-09, but the OX post is dated 2026-04-15 (owner WS2).
- **B6. Trailing space** in the `RES-tenable-camoleak-2025` ingest title. It is ingest-only and reaches no output.
- **B7. U+FFFD mojibake** in `owasp_llm_top10_2025.json` LLM08 and in 4 avid_owasp rows.
- **B8. The arXiv abstract sample** proposed in SOURCE_LICENSES §6.1/§6.3 was never run.
- **B9. Licence keys inside the mapping JSON files** (docs-warden #15). Optional; needs the mapping tooling (schema-architect).
- **B10. REUSE missing licence texts.** `LICENSES/` lacks Apache-2.0, CC-BY-4.0 and MIT, so `reuse lint` shows 377/454.
- **B11. INGESTION_CONDUCT host count.** It reads "at least 10" as a floor. Count it exactly from the rate limiter's per-host keys in a run log.
- **B12. "precision-over-coverage"** (TAXONOMIES:167) may be another design compound. TAXONOMIES is not scanned today.

### (c) New docs follow-ups
- **C1. CONTRIBUTING:20** says "Edit `data/incidents.json` directly", which conflicts with the no-hand-edit rule.

### Expected alerts (not defects)
- **The D63 overdue alert fires on its first Monday after merge** and stays red weekly until a refresh PR merges. The last merged refresh is #97, from 2026-07-27.

---

## Update, 2026-10-13 (end of session): decisions D108-D125 and what is still open

> Appended under agreement 4. Nothing above was edited. The board (PROGRESS.md) holds the verdicts.

### Closed this session (do not act on the lines above for these)
- **a4 / A3, AIRI: retired.** D108 records the retirement and D124 resolves the D57 hold. The rows are kept and marked stale. `ingest-all` no longer runs AIRI.
- **a5, the ATLAS refresh: closed.** The first dispatch (D109) succeeded as a no-op, because upstream is still 2026.09.
- **A1, the over-merge.** D117 fixes the dedupe rule with byte-identical output. **The split itself is deferred** (D118, retire INC-02646); see the open items below.
- **A2, copied headlines: kept** (D111). The position is documented. Only 2 of the 5 RES headlines ship as titles.
- **a2 / a3, stage 2.** D114 lifts the AIID side, and that lift has merged: +113 rows, 169 updated, 0 merges. D115 records the per-item D42 rulings in inert form. D116 keeps the OECD titles; the count is now 3,935 after D119.
- **The weekly refresh is working.** PR #102 merged (D112). The drift gate (render_docs_stats plus a hard check) is in. The D120 per-field AIID change report is in, with D123 size caps. D121 makes aborts loud.
- **Refresh follow-ups B2 and B3** (swap check on the id column; override surfaced): done.

### Still open
- **OECD side of the freeze.** BINDING (D114): suppression (option A3) must be built and gated before any OECD lift. The D115 rulings stay inert until it exists.
- **The OECD follow-up email** (D116). The draft is in `docs/audits/stage2-ruling-package-2026-10-13.md` §5. **The user sends it.**
- **The over-merge split** (D118, retire INC-02646). It has three blockers:
  - 3 rows dated "2026-Q1", which is not a valid date;
  - 6 ingest rows that still hold OWASP round-up text;
  - the split authorization has to be generalised beyond the hard-coded D28 list.

  New IDs start at INC-17334 or later.
- **D96, due next release:** paraphrase the OWASP LLM mapping descriptions, then narrow the carve-out.
- **R11/R12 (D115):** these need a raw-record read.
- **Engineering follow-ups:**
  - A1 (D121): the approval-file and baseline refusals lack the "did not ship" sentence.
  - R4: blind spots in the drift-gate test.
  - R5: the load-bearing provenance reset is untested.
  - D117 A1: stale docstrings.
  - The original register's (b) list, B4-B12.
- **Decisions from the original register (a) that are still the user's:**
  - a7, waves 3/4;
  - a8, duplicate-rejected CVEs;
  - a9, N11;
  - a10, E5;
  - a11, TAXII;
  - a12, MAL-2026-3607;
  - a13, branch protection;
  - a14, Dependabot;
  - outreach: ENISA, FTC and the annotator follow-ups.

### Expect
- **Sun 2026-10-18 04:00 UTC: the first scheduled refresh under D114.**
  - A new AIID snapshot ships through the PR, with the D120 change report. OECD stays held.
  - **A human merges the PR.**
  - If AIID drops an id or a new row would merge into a published one, the whole refresh aborts loudly (D121).
