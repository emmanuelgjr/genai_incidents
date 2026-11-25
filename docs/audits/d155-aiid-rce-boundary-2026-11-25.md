# D155: AIID `rce` word-boundary fix (dated record, 2026-11-25; do not regenerate)

Branch `ws4/d155-aiid-rce-boundary-2026-11-25`, from main a4776e41. Code + tests + this record only. No data regenerated.

## Change
- `scripts/scrape_aiid.py` TAXONOMY_RULES rce rule: `rce|remote code|...` becomes `\brce\b|remote code|...`.
- `severity_for` (High seeding): bare substring `"rce"` replaced by `re.search(r"\brce\b", text)`.
- Tests: `tests/test_d155_aiid_rce_boundary.py` (11 cases). Fire-proof: against the old `scrape_aiid.py` 6 fail (the 5 negatives: Reinforced, enforcement, source, force, divorce; plus the severity test); against the new code all 11 pass.

## `scrape_aiid.py:33` (SECURITY_KEYWORDS)
It is the **admission filter** (`is_security_relevant`, used by `ingest_aiid_snapshot.build_entry` to decide whether an incident not already in the corpus is kept). It is NOT a label list. Left unchanged: tightening it could stop admitting rows (previously-present ids are preserved by invariant 3, so existing rows would not be dropped, but new-incident admission would change). Effect for a user ruling: "rce" admits any new AIID incident whose title/description contains enforcement, source, force, divorce, etc. Note many other keywords are also bare substrings (e.g. "worm", "hack", "token", "bias", "agent").

## Other alternatives with the same flaw (reported, NOT changed)
- Rules: `election` (matches "selection", "reelection"), `pgd`/`fgsm`, `scam` (low risk), `agent.*hijack`, `tool.*misuse` (cross-word spans), `ransom` (matches "ransomware", intended).
- `severity_for` Critical list: `dead` matches inside "deadline" and similar (unmeasured).

## Offline derivation
The build does not re-classify: `merge_and_dedupe.py` reads `ingest/aiid_full.json` as stored (no `map_taxonomy`/`severity_for` call in the merge path). Only `ingest_aiid_snapshot.py` (networked snapshot download) applies the rules, and its input is title + AIID `description`, which is held only in memory (licence rule). Committed descriptions are templated, so exact re-derivation is impossible offline. A title-only estimate is in `scripts/audit/d155_rce_offline_delta.py`.

Snapshot universe: 1,726 AIID rows, 170 with attack_vector=rce, split 124 (no rce term in title; decided by the description) / 40 (rce only inside a word in the title) / 6 (`ransom` rule only, unaffected by D155). The merged corpus audit's universe is 1,645 INC rows / 161 (118/38/5); both are right, because multi-AIID INC rows explain the gap.

Of the 40 title-only candidates plus AIID-768 (non-rce attack_vector but carries the artifact labels), 34 are **title-reproducible** (the old rules on the title alone reproduce the stored labels and severity) and 7 are not (AIID-444, 1008, 1106, 1204, 1414, 1431, 1588): their stored severity (Critical/High) or extra labels came from description terms, so their post-fix values are not derivable offline. The 124 description-decided rows are likewise not derivable.

**Snapshot-level vs published effect.** At snapshot level the fix would drop attack_vector/LLM10/ASI05/AML.T0050 and lower severity High to Medium for the reproducible rows. That is NOT the published effect: `merge_into` keeps the max severity across co-sources and fills taxonomy from other sources, so held AIRI rows and OECD members mask part of it. Measured corpus-level effect below.

### Measured corpus-level delta (counterfactual, 34 reproducible rows)
Method: scratch clone at e07d302a; baseline = `parse_existing.py` + `GENAI_REFRESH_RUN=1 merge_and_dedupe.py` (reproduces committed data, git status clean); counterfactual = same after rewriting the 34 reproducible rows in `ingest/aiid_full.json` with the fixed rules applied to title only; per-entity diff of `data/incidents.json` (scripts/audit/d155_counterfactual_apply.py and _diff.py). Entity count and ID set unchanged (15,845). No other field moved (corpus, tier, retracted, tags, etc. unchanged).

```
ids same True 15845 15845
attack_vector 32 07518 05776 06995 05636 05656 05085 07706 05063 05456 04942 04429 05447 04040 04734 02287 02965 03246 02839 03111 03109 02369 03155 02724 07737 14317 17226 17292 17300 17319 17321 17358 17387
last_seen 34 07518 05776 06995 05636 05656 05085 07706 05063 05456 07318 04942 04429 05447 04040 04734 04530 02287 02965 03246 02839 03111 03109 02369 03155 02724 07737 14317 17226 17292 17300 17319 17321 17358 17387
mitre_atlas 18 05776 05656 04734 04530 02965 02839 03111 03109 02369 03155 07737 17226 17292 17300 17319 17321 17358 17387
mitre_atlas_tactics 17 05776 04734 04530 02965 02839 03111 03109 02369 03155 07737 17226 17292 17300 17319 17321 17358 17387
nist_ai_rmf 17 05776 04734 04530 02965 02839 03111 03109 02369 03155 07737 17226 17292 17300 17319 17321 17358 17387
owasp_asi 32 07518 05776 06995 05636 05656 05085 07706 05063 07318 04942 04429 05447 04040 04734 04530 02287 02965 03246 02839 03111 03109 02369 03155 02724 07737 17226 17292 17300 17319 17321 17358 17387
owasp_llm 18 05776 05656 04734 04530 02965 02839 03111 03109 02369 03155 07737 17226 17292 17300 17319 17321 17358 17387
severity 12 07518 07318 03246 03111 03155 07737 17226 17292 17300 17319 17321 17387
updated 34 07518 05776 06995 05636 05656 05085 07706 05063 05456 07318 04942 04429 05447 04040 04734 04530 02287 02965 03246 02839 03111 03109 02369 03155 02724 07737 14317 17226 17292 17300 17319 17321 17358 17387
rows changed 34
attack_vector transitions Counter({('rce', 'other'): 23, ('rce', 'privacy-violation'): 3, ('rce', 'algorithmic-bias'): 2, ('rce', 'deepfake'): 2, ('rce', 'unsafe-advice'): 2})
severity Counter({('High', 'Medium'): 12})
```

Rows by changed field (INC ids) are in the lines above. 34 INC rows change in total. Masking: LLM10/AML.T0050 survive on about half the rows (the ones with an AIRI co-source or other fill), which is why owasp_llm/mitre_atlas move on 18 rows while attack_vector/owasp_asi move on 32 and severity on only 12. mitre_atlas_tactics (17) and nist_ai_rmf (17) are derived from mitre_atlas/owasp and follow it. `updated`/`last_seen` change on all 34. Merge step 4b reclassifies an attack_vector of "other", so rows leave `rce` for privacy-violation / deepfake / algorithmic-bias / unsafe-advice (9 of 32), not only "other".

Authority: for the 34 above, this measured delta is the expectation and the refresh D120 report should match it. For the 124 description-decided rows and the 7 non-reproducible rows the D120 report is the only authority. Fields owasp/atlas appear in that report only as counts.

Known, not fixed here: the `ransom` rule's semantic misfire on voice-scam rows (it also sets attack_vector=rce, outside D155's scope); AIRI co-source labels that an AIID refresh can never clear; the D120 report listing owasp/atlas only as counts.

## Merge effect
Merging this branch alone moves no data. The delta appears only in the refresh PR after the next AIID snapshot ingest, via the D120 change report.

## Corrections (gate bounce 1, 2026-11-25)
1. Old text (replaced above, effect paragraph): "40 have rce only inside a word ... the next scheduled refresh changes for these rows: attack_vector (to the next matching rule, else other), owasp_llm LLM10, owasp_asi ASI05, mitre_atlas AML.T0050 ... and severity High to Medium"; "36 would fall to Medium"; "Cascade ... none from this change"; "the refresh's D120 report is the authority". New: stated at snapshot level only; measured corpus-level delta (34 rows; 12 severity, 32 attack_vector) with masking, merge step 4b, nist_ai_rmf, mitre_atlas_tactics, updated, last_seen; D120 is the sole authority only for the 124 + 7 non-derivable rows. No corpus/tier/stats cascade was observed in the counterfactual.
2. Old text: "6 have a real term in the title (AIID-537, 891, 1201, 1578, 1615, 1661; plus ransom rows)". Wrong: all 6 match only `ransom`; none has a whole-word rce / remote code / command injection / sandbox escape, and there are no further ransom rows. The audit script label `real_in_title` now reports 0 and a new `ransom_only_in_title` reports the 6.
3. Old text counted "40 title-proven". New: 34 title-reproducible plus 7 not reproducible by title (AIID-444, 1008, 1106, 1204, 1414, 1431, 1588), with the reason above. 34 matches the gate's independent count. Note the 40 + AIID-768 = 41 candidates, 34 + 7 = 41.
