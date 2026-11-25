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

Snapshot (1,726 rows): 170 have attack_vector=rce.
- 40 have `rce` only inside a longer word in the title and no real term: **candidate artifacts, title-proven**. If the description has no whole-word `rce`/remote-code/etc., the next scheduled refresh changes for these rows: attack_vector (to the next matching rule, else `other`), owasp_llm LLM10, owasp_asi ASI05, mitre_atlas AML.T0050 (each unless another rule supplies it), and severity High to Medium (unless another High/Critical term).
- 124 have no rce term at all in the title; the value came from the description. Not derivable offline.
- 6 have a real term in the title (AIID-537, 891, 1201, 1578, 1615, 1661; plus ransom rows): unchanged.
- AIID-768 has a non-rce attack_vector but carries LLM10, ASI05, AML.T0050 and High from the artifact (title-only); its LLM02/ASI03/AML.T0057 come from another rule.

Title-proven attack_vector/LLM10/ASI05/AML.T0050 candidates (AIID-n): 65, 98, 117, 143, 240, 262, 274, 385, 395, 444, 472, 538, 578, 603, 633, 659, 896, 923, 993, 1001, 1008, 1009, 1106, 1204, 1286, 1299, 1327, 1353, 1414, 1431, 1506, 1569, 1588, 1595, 1689, 1701, 1727, 1731, 1783, 1818 , plus 768 for LLM10/ASI05/AML.T0050.

Severity High to Medium candidates (title-proven, 36): 65, 98, 117, 143, 240, 262, 274, 385, 395, 472, 538, 578, 603, 633, 659, 768, 896, 923, 993, 1001, 1008, 1009, 1286, 1299, 1327, 1353, 1414, 1506, 1569, 1588, 1595, 1689, 1701, 1727, 1731, 1818.

Cascade into `corpus`, `tier`, stats: none from this change. Corpus classification is `merge_and_dedupe._classify_corpus`, a separate substring keyword test (option O2, held under D154); whether attack_vector feeds it was not measured here; the refresh's D120 report is the authority.

## Merge effect
Merging this branch alone moves no data. The delta appears only in the refresh PR after the next AIID snapshot ingest, via the D120 change report.
