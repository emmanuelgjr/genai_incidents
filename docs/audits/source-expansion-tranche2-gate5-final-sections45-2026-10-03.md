# Source-expansion tranche 2: final gate on sections 4–5 (gate 5): BOUNCE #1 on 4–5

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on
`eval/source-expansion` @ `fb64ea10`, using a fresh red-reviewer.

**Provenance:** the gate delivered its verdict in three messages: a summary,
then DEFECTS 1–5, then DEFECTS 6–9. The foreman asked for the last two
separately so they would not be truncated. **The defect sections below were
concatenated by shell from files saved as received; they were not retyped.**
The summary section was copied by hand from the gate's first message.

---

## Summary (gate message 1)

VERDICT: BOUNCE on sections 4-5 at fb64ea10 (first bounce on 4-5). The full report with every replacement text verbatim is in my final output. Defects in brief:
1. "Not in corpus" lists refuted: 9 of the 302 EUVD ids and 5 of the 233 huntr ids are already in the corpus as AVID-keyed entries titled with the CVE (e.g. INC-04083 AVID-2026-R0006 = CVE-2024-10513). Corrected: 293 (24%), 920 in corpus; 228 (62%), 140 in corpus. Membership was tested on CVE- source_ids only.
2. Wave-1 yield: huntr's 228 is NOT inside the ~300. The two lists share only 105 ids, so the cvelistV5 lower bound is 416 (~165/yr). V=2 and the ranking are unchanged.
3. 6,986 is CVE ids, not entries: 5,293 entries carry a CVE source id. The 254 huntr figure is ids, in 199 entries (L845, L927, L1317).
4. The AP robots cause is wrong: stdlib robotparser has no wildcard support (it stores Allow /documenten/* as literal /documenten/%2A). Reordering alone still refuses (L879, L1186, L1267).
5. Non-English rule missing on the BSI, JPCERT, AP, CNIL, ANPD rows; partial on Garante.
6. "status: active" should be "source_status: active" (L866).
7. Evidence JSON has one Latin-1 byte (0xF6 at offset 25913) and fails strict UTF-8 parsing.
8. Stale "(placeholder)" line at L135.
9. CCCS ~1,800/yr is unlabelled extrapolation under [M]; Wave 3 says Garante is "single digits/yr" but its row says 8-12.
Confirmed by a different route: AVID 1,790/109/1,681/V025 (shallow clone); huntr 2,496/111 (NVD noRejected); (e) max CVE month 2026-07 plus an independent NVD lower bound of 334 missing; (f) 18 of 18 REJECTED via cve.org, 17 entries active; Crawl-delay never parsed; arXiv and data.gouv robots. arXiv 2/535 cannot be re-derived (no ID list). Arithmetic, sort, licence factors, scope (4 docs/specs files, 0 diff in data/scripts/ingest/SOURCE_LICENSES), sections 1-3 unchanged except ANSSI at the merged tip, and a clean merge-tree all pass.

## Defects 1–5 (gate message 2)

DEFECTS 1-5: replacement text to apply verbatim. File: docs/specs/source-expansion-evaluation.md at fb64ea10, unless noted. OLD/NEW strings are phrases that may span a line wrap; match them ignoring the wrap.

D1-a (L861-862)
OLD: 25% of EUVD's proxy-AI CVEs (302 of 1,213) are not in the corpus, and 63% of huntr's (233 of 368).
NEW: 24% of EUVD's proxy-AI CVEs (293 of 1,213) are not in the corpus, and 62% of huntr's (228 of 368); the two sets share 105 ids, so their union is 416. (The evidence lists hold 302 and 233 ids; gate 2026-10-03 found 9 and 5 of them already in the corpus as AVID-keyed entries whose title names the CVE, e.g. INC-04083 `AVID-2026-R0006` for CVE-2024-10513, because membership was keyed on `CVE-` source ids only.)

D1-b (L896-897)
OLD: of which 302 are not in the corpus [M].
NEW: of which 293 are not in the corpus [M]; the huntr CNA route adds 123 more outside that set (union 416 [M]).

D1-c (L898)
OLD: Steady state ~120 new/yr (302 over 30 months)
NEW: Steady state ~165 new/yr (416 over 30 months)

D1-d (L902)
OLD: ~75% already in the corpus (911 of 1,213 [M], window)
NEW: ~76% already in the corpus (920 of 1,213 [M], window)

D1-e (L928)
OLD: 135 are in the corpus and **233 (63%) are not** [M]
NEW: 140 are in the corpus and **228 (62%) are not** [M]

D1-f (L1007)
OLD: (302 not in the corpus)
NEW: (293 not in the corpus)

D1-g (L1339)
OLD: 233 AI-relevant CVEs missing (63% of its window set)
NEW: 228 AI-relevant CVEs missing (62% of its window set)

D1-h (docs/specs/source-expansion-estimates-evidence-2026-10-03.md: insert a new paragraph after L33; leave L30-33 unedited, since it is a dated record)
INSERT: **Gate update 2026-10-03 (do not regenerate):** the membership test keyed on `CVE-` ids in `source_ids` only. 9 of the 302 EUVD ids and 5 of the 233 huntr ids are in the corpus as AVID-keyed entries whose title names the CVE. Corrected: 293 and 228; union 416. The input that makes this check fail is a CVE held under a non-CVE source id.

D2 (L1296-1298)
OLD: cvelistV5 ~300 backlog in the 30-month window [M, lower bound] plus ~120/yr [E], inside which huntr is 233 backlog [M] and ~40-70/yr [E]
NEW: cvelistV5 ≥416 backlog in the 30-month window [M, lower bound: union of the EUVD-route 293 and the huntr-route 228, which share 105 ids] plus ~165/yr [E], of which the huntr CNA slice is 228 backlog [M] and ~40-70/yr [E]

D3-a (L845)
OLD: of which 6,986 carry a `CVE-` source id.
NEW: of which 5,293 carry a `CVE-` source id (6,986 distinct CVE ids).

D3-b (L927)
OLD: 254 corpus entries are huntr-CNA CVEs (3.6% of the 6,986 CVE entries)
NEW: 254 corpus CVE ids are huntr-CNA CVEs, in 199 entries (3.6% of the 6,986 CVE ids)

D3-c (L1317)
OLD: 6,986 CVE-keyed corpus entries
NEW: 5,293 CVE-keyed corpus entries (6,986 CVE ids)

D4-a (L879, inside the table cell)
OLD: The AP result is stdlib `robotparser` taking the **first** matching rule in file order, where the AP file lists `Disallow: /documenten` and `Allow: /documenten/*`; RFC 9309 would take the longest match. A parser fix, not a robots change, is the issue.
NEW: The AP result is stdlib `robotparser`, which does not implement RFC 9309 wildcards: it stores `Allow: /documenten/*` as the literal prefix `/documenten/%2A`, which no real path matches, so `Disallow: /documenten` applies. (It also takes the first match in file order rather than RFC 9309's longest match, but reordering alone does not change the result: gate experiment 2026-10-03.) A parser fix (wildcards and longest match), not a robots change, is the issue.

D4-b (L1186-1187)
OLD: because of rule order (4.1) [M]
NEW: because stdlib `robotparser` ignores the `*` wildcard in `Allow: /documenten/*` (4.1) [M]

D4-c (L1267, Note column)
OLD: refused by `common.py` rule order
NEW: refused by `common.py` (stdlib robotparser, no wildcard support)

D5: append sentence R immediately after each anchor below.
R = " Rule: translated summaries are original prose, generated offline and committed (WS0-T3), never by a model call in `make build`."
D5-a BSI (L1059), after: from the vendor advisory (1A.5).
D5-b JPCERT (L1181), after: translation volume ≤2/yr.
D5-c Dutch AP (L1187), after: English pages exist.
D5-d CNIL (L1191), after: (including AI guidance).
D5-e ANPD (L1193), after: Translation ~1-3/yr.
D5-f Garante (L1162), after "~50 for the backlog." append: " They count as original prose; never generated by a model call in `make build` (WS0-T3)."

## Defects 6–9 (gate message 3)

DEFECTS 6-9: replacement text to apply verbatim. File: docs/specs/source-expansion-evaluation.md at fb64ea10, unless noted.

D6 (L866-867)
OLD: `status: active` with no rejection marker
NEW: `source_status: active` with no rejection marker

D7 (docs/specs/source-expansion-estimates-evidence-2026-10-03.json, L1446, byte offset 25913)
Offending context: "[UPDATE] [mittel] Red Hat OpenShift und OpenShift AI (urllib3): Schwachstelle erm<0xF6>glicht Denial of Service"
The single byte 0xF6 (Latin-1 o-umlaut) sits between "erm" and "glicht".
Fix: replace that one byte with the UTF-8 encoding of U+00F6, the character ö (bytes C3 B6), so the word reads "ermöglicht". Change nothing else.
Check: python -c "import json;json.load(open(PATH,encoding='utf-8'))" must succeed afterwards; it fails today. Replace PATH with the file path.

D8 (L134-135)
OLD: Pipeline estimates: section 4 (placeholder). Ranking: section 5 (placeholder).
NEW: Pipeline estimates: section 4. Ranking and waves: section 5 (pipeline-engineer, 2026-10-03).

D9-a CCCS label (L1144)
OLD: [M] RSS 50 items in 9 days (≈1,800/yr, vendor advisories), 0 AI
NEW: [M] RSS 50 items in 9 days (vendor advisories; ≈1,800/yr if annualised from those 9 days [E]), 0 AI

D9-b Garante contradiction (L1321-1322, Wave 3)
OLD: ICO and Garante single digits per year
NEW: ICO ~3-8/yr, Garante ~8-12/yr [E]
