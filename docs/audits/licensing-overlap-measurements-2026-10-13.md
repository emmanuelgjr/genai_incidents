# Licensing overlap measurements (2026-10-13)

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4).
>
> - **Who measured:** red-reviewer (gate on `ws0/followups-licensing-2026-10-13` @ `ef4ad825`), using raw page text: curl, pdftotext.
> - **Method:** 5-gram overlap plus longest common token run, then a side-by-side read.
> - **Verdict thresholds:**
>   - verbatim: run ≥ 20 or ≥ 50% of 5-grams shared;
>   - near-verbatim: run ≥ 8 or ≥ 10%;
>   - own: anything below that.
> - **Controls:**
>   - a verbatim excerpt scores 100%;
>   - the reviewer's own paraphrase scores 0%;
>   - a cross-source comparison scores 0%.
> - **Purpose:** these figures feed user rulings. The foreman transcribed them; see the gate verdict on the board.

## Q1: OWASP Top 10 for LLM Applications mapping files (licence CC BY-SA 4.0)

**Licence evidence:**
- The 2026 PDF licence page reads "This document is licensed under Creative Commons, CC BY-SA 4.0."
- Zenodo record 22109015 gives `cc-by-sa-4.0`.
- The repository README states CC BY-SA 4.0.
- The 2025 pages carry the site footer "Creative Commons Attribution-ShareAlike v4.0".

### `mappings/owasp_llm_top10_2026.json` vs `2026/final/*.md` (cross-checked against the PDF text; same verdicts)

| Code | 5-gram hit | Run | Verdict |
|---|---|---|---|
| LLM01 | 57% | 24 | VERBATIM |
| LLM02 | 50% | 12 | VERBATIM |
| LLM03 | 19% | 8 | near-verbatim |
| LLM04 | 50% | 12 | VERBATIM |
| LLM05 | 73% | 18 | VERBATIM |
| LLM06 | 36% | 9 | near-verbatim |
| LLM07 | 43% | 14 | near-verbatim |
| LLM08 | 48% | 15 | near-verbatim |
| LLM09 | 42% | 12 | near-verbatim |
| LLM10 | 19% | 7 | near-verbatim |

**Total: 4 verbatim, 6 near-verbatim, 0 own.** The descriptions appear only in the mapping file; a repo-wide grep finds no other copy.

### `mappings/owasp_llm_top10_2025.json` vs the genai.owasp.org 2025 pages

| Verdict | Codes |
|---|---|
| VERBATIM | LLM01 (68%), LLM04 (100%), LLM08 (50%) |
| near-verbatim | LLM09 (43%) |
| own | LLM02, LLM03, LLM05, LLM06, LLM07, LLM10 (0% each) |

## Q2: the 21 `OWASP-*` source ids in `ingest/avid_owasp_incidents.json` (round-up pages carry CC BY-SA 4.0)

### Ingest rows

**18 GENAI ids:**
- VERBATIM (4): Q1-2025-03, Q2-2025-01 (81%), Q2-2025-02, Q1-2026-04 (69%, run 24).
- near-verbatim (4): Q1-2025-01, Q1-2025-02, Q1-2026-05, Q1-2026-06.
- own (10): the rest.

**3 AIX ids:** all own wording. Each incident was likely selected from a reference list on an OWASP LLM Top 10 2025 page:
- Slack: LLM06;
- Air Canada: LLM09;
- Sourcegraph: LLM10.

**Provenance:**
- Q1-2026-04, -05 and -06 appear on the cited Q1-2026 page.
- Q1-2026-01, -02 and -03 appear on no cited round-up page.
- The page was modified 2026-05-20, after our rows were committed on 05-12. No earlier version is recoverable.

### Shipped rows in `data/incidents.json`

| Row | OWASP ids folded in | Description | Title |
|---|---|---|---|
| INC-02646 | 9 Q2-2025 | **VERBATIM, 81%, run 17** | matches the page heading (7/7 tokens) |
| INC-03233 | 3 Q1-2025 | **near-verbatim, 31%, run 11** | own |
| INC-00924 | 6 Q1-2026 | own (text from another source) | own |
| INC-04208 | Slack | own | own |
| INC-03530 | Air Canada | own | own |
| INC-04875 | Sourcegraph | own | own |

**2 of the 6 shipped rows carry OWASP round-up text.**

## Q3: `research_incidents.json` (135) and `threat_reports_incidents.json` (82)

**Sample:**
- 113 rows stratified by host and vendor.
- 102 measured. Of the other 11: 9 fetches failed (403, 404 or timeout), and 2 pages were JavaScript shells.

| File | Measured | own | near-verbatim | verbatim |
|---|---|---|---|---|
| research (RES) | 78 | 69 | 9 | 0 |
| threat reports (VTR) | 24 | 23 | 1 | 0 |

**Real copied spans (run ≥ 8):**
- RES-tenable-camoleak-2025 (run 10)
- RES-claude-code-unauthorized-cmds-2025 (run 9)
- RES-ox-mcp-systemic-2025 (run 9)
- RES-anthropic-aug2025 (run 8)

**Weak (run 6-7, a close paraphrase of the source's first sentence):**
- RES-protectai-intel-nc-2024
- RES-aesir-trendmicro-2025
- RES-layerx-atlas-tainted-2025
- RES-zenity-copilot-rce-2024
- RES-appomni-copilot-flaws-2026
- VTR-google-gtig-promptsteal-apt28-2025

**Titles identical to the post headline (5):**
- RES-etr-amazonq-rce
- RES-etr-github-copilot-rce
- RES-etr-ai-clickfix
- RES-token-mcpwned-azure
- RES-tenable-copilot-filename

**By host:** all embracethered rows are own wording. All vendor threat-report rows are own wording except the one above.

## Raw-text confirmations (red-reviewer, first gate, 2026-10-13)

> Appended 2026-10-13 by license-auditor from the foreman's transcription of the first gate's testimony (CLAUDE.md agreement 5: the verdict text lands in the commit). Nothing above this heading is edited. These are the gate's findings, not re-measured by the author, who has no shell. Dated record, do-not-regenerate.

These confirm, from raw text (curl, `pdftotext`), the points `docs/SOURCE_LICENSES.md` previously carried as WebFetch readings (method-suspect):

1. **OWASP footer.** The CC BY-SA sentence ("Unless otherwise specified, all content on the site is Creative Commons Attribution-ShareAlike v4.0") is verbatim in the raw HTML of all 5 `genai.owasp.org` pages checked.
2. **embracethered.com absence (checked).** A grep for `licen`, `creative commons`, `cc-by` and `reuse` finds nothing on the post or on `/blog/`. The footer "(c) WUNDERWUZZI 2018-2026" is present. This is the raw-HTML check the SOURCE_LICENSES absence finding required.
3. **GenAI-LLM-Top10 README.** The licence line is verbatim. The GitHub API `license` field returns null.
4. **OWASP AI Exchange.** The CC0 sentence is verbatim.
5. **`oecd.ai/robots.txt`.** 7 Disallow rules plus a `Sitemap:` line; no Allow, no Crawl-delay.
6. **OECD sitemap** (`oecd.ai/sitemaps/incident-monitor-sitemap.xml`): HEAD returns 405 (`allow: GET`); GET returns 200 with 0 redirects.
7. **OECD incident page** `2026-10-06-3049`: HEAD 200, GET 200.
8. **OECD methodology page.** The terms sentence ("Your use of the OECD AI incidents and hazards monitor ... is subject to the terms and conditions found at www.oecd.org/termsandconditions") appears twice. There is no bot or scraping language.
9. **Crosswalk `mappings/owasp_llm_2025_to_2026.json`** against the 2026 `LLM00_Preface.md`: it holds all 20 risk names (`name_2025` / `name_2026`). Its `scope_change` strings: LLM03 verbatim (60%, run 18); LLM04 shares the phrase "absorbs fine-tuning subversion"; LLM08 verbatim (56%, run 9); LLM05 and LLM06 near-verbatim (run 7); the other 5 own. The code labels are as the gate reported them; the author did not re-derive which crosswalk key each belongs to.
