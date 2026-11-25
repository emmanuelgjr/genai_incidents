# AIID corpus classifier audit, 2026-11-24 (label-scientist, WS2)

Dated record. Do not regenerate. If later work overtakes this, add a dated update below and leave the original text as written.

- **Base:** `main` at `8753a7fe`. That is refresh PR #110 merged plus Dependabot. The classifier code is unchanged since `6a4d8261`: `git diff --stat 6a4d8261 8753a7fe -- scripts/` is empty.
- **Scope of this run:** diagnosis and an option menu. The only data change is the single-row INC-07572 fix (option O1, §5). No mass relabel was made, and the AIID default is unchanged.
- **Evidence:** `scripts/audit/aiid_corpus_audit.py` regenerates every number below from committed inputs, with no network and no model calls. Its files are in `docs/audits/aiid-corpus-classifier-2026-11-24/`:
  - `sample.csv`, `adjudication.csv`: main sample.
  - `holdout.csv`, `holdout_adjudication.csv`: held-out sample.
  - `new24.csv`: census of the 24 new rows.
  - `dryrun-*.json`: full per-option ID lists.

## 0. Foreman premises, measured

| premise | verdict |
|---|---|
| INC-07572's flip comes from description→classifier coupling (WS0-T3 shape) | **Holds.** The AIID description is a template that embeds AIID's deployer/developer entity list, and `_classify_corpus` reads it. |
| The new label is wrong | **Holds.** Predictive policing is the repo's own `ai-harm` example keyword, and the row has no security primitive. |
| A keyword like "law enforcement" or "enforcement" sits in `_SECURITY_KEYWORDS_FOR_CORPUS` | **Refuted.** No such keyword exists. The match is **`"rce"`**, a substring of "enfo**rce**ment" (§1). |
| `_classify_corpus` returns `security` when no keyword matches | **Holds.** 786 of the 1,645 AIID rows are `security` only through this fallthrough. |
| 1,411 of 1,621 AIID rows on main are `security` | **Stale ref.** Those are the counts at `6a4d8261`, before PR #110. On `main` `8753a7fe` the figure is **1,436 of 1,645**. |
| OECD rows use a separate classifier, `ingest_oecd_aim.py:808` | **Half right.** It is a separate function, but it imports the *same keyword tuples* (`ingest_oecd_aim.py:42-43`), so it has the same `rce` bug. It also did not decide INC-07572: `merge_into` (`merge_and_dedupe.py:4108`) does not carry `corpus`, so the two OECD members' persisted `ai-harm` was discarded. |
| All 24 new rows defaulting to `security` is the error | **Mostly refuted.** Under the repo's own definitions, **16 of 24 are correctly `security`**: they are agent credential/unauthorized-access incidents, frauds and a breach. 8 are wrong. The deepfake-nudes row (INC-17388) is `security` under the corpus classifier's stated definition. See §3.1 for the conflict this exposes. |
| INC-17387's `rce` attack_vector is wrong | **Holds, and the cause is proven.** `scrape_aiid.py:156` has regex `rce` with no word boundary, and it matches "Reinfo**rce**d" in the title. The same artifact also gave the row LLM10, ASI05, AML.T0050 and severity High (`scrape_aiid.py:202`). |

## 1. Root cause of the INC-07572 flip [R]

Command: `python scripts/audit/aiid_corpus_audit.py flip`

```
[before 6a4d8261] INC-07572 stored corpus=ai-harm reclassified=ai-harm
   affected="Pasco Sheriff's Office, Unknown"
   security-keyword hits: none
   ai-harm-keyword hits: ['predictive policing']
[after 8753a7fe] INC-07572 stored corpus=security reclassified=security
   affected="Law Enforcement, Pasco Sheriff's Office"
   security-keyword hits: [('rce', "/developer: law enforcement, pasco sheriff'")]
   ai-harm-keyword hits: ['predictive policing']
```

Code path:

1. `ingest_aiid_snapshot.py::build_entry` templates `description = "... Alleged deployer/developer: <entities>."` from AIID's entity slugs. AIID added the `law-enforcement` entity upstream.
2. In dedupe, the AIID row is the merge target. `merge_into` (`merge_and_dedupe.py:4108`) unions lists and a few single-value fields, but **not `corpus`**. The `ai-harm` value persisted on `OECD-AIM-2020-09-08-af6a` and `OECD-AIM-2021-03-15-9271` is therefore dropped.
3. Step 5 (`merge_and_dedupe.py:3396`, `if not e.get("corpus")`) calls `_classify_corpus`. That function lowercases title + description + tags and tests `any(kw in text for kw in _SECURITY_KEYWORDS_FOR_CORPUS)` at `:771`, a **substring** test. `"rce"` (`:710`) is found inside "enforcement".
4. Security is tested before ai-harm ("Security wins ties"), so the `predictive policing` hit is never consulted.

This is a known bug class reaching a new site.
- D130-2L found the same `rce`-in-"enforcement" artifact in `parse_existing`'s attack-vector hint (`docs/audits/relabel-d130-2l-2026-10-16.md` §1).
- `ingest_aiaaic_sheet.py:439` already fixed it for AIAAIC with `\brce\b`.
- It is still live in:
  - `_classify_corpus`, and through the shared tuple in OECD `classify_corpus_signal`;
  - `scrape_aiid.TAXONOMY_RULES` (`:156`) and `severity_for` (`:202`), which the AIID ingest reuses;
  - `ingest_oecd_aim.KEYWORD_TO_OWASP` (`:88`). INC-07572's two OECD members carry `attack_vector: rce` from it.

## 2. What decides corpus on AIID rows [R]

Command: `python scripts/audit/aiid_corpus_audit.py paths`

```
ref 8753a7fe: 15845 rows, 1645 carry an AIID- source_id; stored corpus != re-run classifier on 0 []
corpus on AIID rows: {'ai-harm': 209, 'security': 1436}
  path=default       corpus=security n=786
  path=harm          corpus=ai-harm  n=209
  path=rce-artifact  corpus=security n=77
  path=sec-keyword   corpus=security n=573
rce-artifact rows that ALSO carry an ai-harm keyword (suppressed ai-harm): 14 ['INC-01371', 'INC-02287', 'INC-03311', 'INC-04040', 'INC-04094', 'INC-04801', 'INC-05063', 'INC-05085', 'INC-06995', 'INC-07170', 'INC-07572', 'INC-07706', 'INC-08167', 'INC-08169']
```

The four paths are:

| path | meaning |
|---|---|
| `default` | No keyword of either list matches, so the row falls through to `return "security"`. |
| `sec-keyword` | A real security keyword matches. |
| `rce-artifact` | The only security hit is `rce` inside a longer word. |
| `harm` | No security hit, and an ai-harm keyword matches. |

No AIID row has `cve_ids`. The stored value equals a re-run of the classifier on all 1,645 rows, so the stored labels are fully explained by this function.

**Most `ai-harm` labels come from a tag, not from prose.** The `harm` path is driven mostly by `discriminat`. That keyword usually matches AIID's MIT tag `mit-risk-domain:1-discrimination-and-toxicity`, not any prose. The entity list also drives `sec-keyword` hits: for example, "Deepfake Technology Developers" puts `deepfake` on INC-02286.

## 3. Error rate on AIID rows [R for counts, A for labels: single annotator]

### 3.1 Adjudication criteria, from the repo's own definitions

- `docs/DATA_DICTIONARY.md:20` defines the two values: "`security` (exploit/vuln/misuse) or `ai-harm` (societal harm without a security primitive)". `export_huggingface.py:116` says only "`security` or `ai-harm`".
- The `merge_and_dedupe.py` comments add: "a deepfake fraud is `security`; a hiring-algorithm-discriminates story is `ai-harm`" (`:699`) and "Security wins ties" (`:758`). The keyword list counts deepfake, voice clone, csam, scam and fraud as security.

The repo states two readings, and they conflict:

- **R1, primary.** `security` covers an exploit, a vulnerability or another security primitive: unauthorized access, credential or data exposure, authentication bypass, malware, attacking or jailbreaking a system. It also covers *misuse*, meaning a human actor deliberately using AI against third parties: fraud, scams, impersonation, deepfakes including sexual deepfakes, CSAM, influence operations and AI-enabled attacks. Everything else is `ai-harm`: system error, bias, unsafe output, safety failure, negligent reliance, and deployer surveillance or privacy practice with no breach. Ties go to security. This follows `_SECURITY_KEYWORDS_FOR_CORPUS` and the DATA_DICTIONARY "misuse".
- **R2, sensitivity.** As R1, except that synthetic-media, CSAM and disinformation harms are `ai-harm` when they involve **no** fraud, extortion or security primitive. This follows the "AI-harm vectors" block of `_ATTACK_VECTOR_RULES` (`merge_and_dedupe.py:608-612`). That block lists `csam-generation`, `deepfake` and `misinformation` as harm vectors "that pull the AIAAIC ai-harm corpus".

**The repo does not say which reading is meant. That is a user/foreman definition ruling, and it comes before any mass relabel** (§4).

Limits of the labels:
- One annotator (me), working from title plus entity list. AIID narrative is not in the repo.
- 15 of the 130 sample rows are flagged `borderline=y`.
- This is **not** a WS2-T2 measurement: there is no second annotator and no kappa.

### 3.2 Main sample: seed 20261124, ref 8753a7fe, stratified by path

Command: `python scripts/audit/aiid_corpus_audit.py score` (R1), adding `--column r2_corpus` for R2.

```
column=adjudicated_corpus; borderline rows in sample: 15
Confusion over the whole sample (rows=stored label, cols=adjudicated):
  stored security: adj security= 41  adj ai-harm= 59
  stored ai-harm : adj security=  2  adj ai-harm= 28
  unweighted sample accuracy 69/130
Per stratum (population-weighted estimate of wrong labels):
  default       pop= 786 drawn= 40 wrong= 33 (82.5%, Wilson 95% 68%-91%) -> est. 648 wrong rows
  sec-keyword   pop= 573 drawn= 30 wrong=  1 (3.3%, Wilson 95% 1%-17%) -> est. 19 wrong rows
  harm          pop= 209 drawn= 30 wrong=  2 (6.7%, Wilson 95% 2%-21%) -> est. 14 wrong rows
  rce-artifact  pop=  77 drawn= 30 wrong= 25 (83.3%, Wilson 95% 66%-93%) -> est. 64 wrong rows
Estimated wrong corpus labels across the 1645 AIID rows: 746 (45.3%)
Weighted: security precision 49.0%; ai-harm precision 93.3%; ai-harm recall 21.0%
```

Under R2 the estimate is 1,019 wrong (62.0%). Most of the extra errors (about 248 of the net 273) come from `sec-keyword`: 14 of 30 rows there are non-fraud deepfake, CSAM or disinformation. `default` adds about 39 and `harm` removes about 14.

The per-class confusion, population-weighted, R1:

| | adjudicated security | adjudicated ai-harm |
|---|---|---|
| stored security (1,436) | ≈ 704 | ≈ 732 |
| stored ai-harm (209) | ≈ 14 | ≈ 195 |

- **Security precision is about 49%:** half of the AIID rows labelled `security` are not security incidents under the repo's own definition.
- **ai-harm precision is high, about 93%, but recall is about 21%.**
- Almost all the error sits in two paths: the `default` fallthrough and the `rce` artifact.

### 3.3 Held-out replication: seed 20261125, disjoint from sample.csv

`holdout.csv` holds 30 rows from `default` and 10 from `rce-artifact`. It was drawn **after** the O5 vocabulary in §4 was written. It is out-of-sample for O5, except INC-17377 and INC-17384, which are also in the new-24 census read beforehand.

Command: `python scripts/audit/aiid_corpus_audit.py score --sample docs/audits/aiid-corpus-classifier-2026-11-24/holdout.csv --adjudication docs/audits/aiid-corpus-classifier-2026-11-24/holdout_adjudication.csv`

```
  default       pop= 746 drawn= 30 wrong= 24 (80.0%, Wilson 95% 63%-90%) -> est. 597 wrong rows
  rce-artifact  pop=  47 drawn= 10 wrong= 10 (100.0%, Wilson 95% 72%-100%) -> est. 47 wrong rows
```

The default-path error replicates: 82.5% in the main sample and 80.0% held out. The two draws use different rows, but the same annotator. That makes this a replication of the draw, not of the labels.

### 3.4 The 24 new rows (census, `new24.csv`)

Corpus, R1:
- **16 correct.** INC-17371, 17372–17381, 17384, 17386, 17388, 17391, 17394: agent credential exposure, unauthorized access, fraud, a breach, and a deepfake.
- **8 wrong.** INC-17382 and 17383 (unsafe medical/suicide advice), INC-17385 and 17389 (facial-recognition misidentification), INC-17387 (rent advice), INC-17390 (unauthorized patient-data use by a deployer), INC-17392 and 17393 (autonomous-vehicle crashes).
- 6 of the wrong 8 are `default`. 2 (INC-17385, 17387) are the `rce` artifact.
- R2 adds INC-17388 as wrong.

attack_vector:

| verdict | rows | detail |
|---|---|---|
| **wrong, cause proven** | INC-17387 | `rce`, from "Reinforced" (§0). |
| **wrong** | INC-17390 | `tool-abuse` (LLM03, ASI02, AML.T0053). It is the agent tool-misuse vector, but this is a deployer privacy violation. |
| **wrong** | INC-17394 | `deepfake`. The merge rule `impersonat→deepfake` fires, but the agents impersonated staff with no synthetic media. |
| **unverifiable** | INC-17386 | `rce`. The title has no rce, remote-code or ransom term. The value came from AIID's description, which the ingest uses only in memory and never stores (licence rule), so it cannot be re-derived offline. |
| **generic** | 10 rows | `other` where a specific vector exists. That is a missed label, not a wrong one. |

Scale beyond the 24 new rows (`python scripts/audit/aiid_corpus_audit.py avscan`):

```
ref 8753a7fe: 161 AIID rows with attack_vector=rce
   118  title has neither (decided by AIID's ephemeral description; not re-derivable offline)
    38  title has 'rce' ONLY inside a word (artifact proven from committed text)
     5  title has a real rce/ransom term
  host words: {'reinforced': 10, 'enforcement': 4, 'source': 3, 'forced': 3, 'force': 2, 'divorce': 2, ...}
```

At least 38 of the 161 AIID `rce` labels are proven artifacts. The 118 rows decided by the description are likely mostly artifacts too, but this cannot be shown offline. Fixing them means fixing `scrape_aiid.py:156`/`:202` with `\brce\b` and re-running the AIID snapshot ingest, which needs network. That re-ingest would also move the `owasp_llm`, `owasp_asi`, `mitre_atlas` and `severity` values seeded by the same rule. It is not done here.

## 4. Option menu (baseline-first)

### 4.1 How each option was measured

Each option was built, not simulated:
- `dryrun --option X` creates a detached worktree at `8753a7fe` and applies the option's patch or override (code in the script).
- It then runs `parse_existing.py` and `merge_and_dedupe.py` and compares every row and every field against the committed `data/incidents.json`. Full ID lists are in `dryrun-X.json`.
- Published counts are **derived from the rows**. `stats.json` is written by the render step, so comparing that file after a merge-only build could not fail: my first draft did exactly that and reported "stats unchanged" for an option that moves `landmark_count`.
- **Control O0** (no patch) gives 0 deltas in every field, so the build reproduces the base.

Two cross-checks:
- **Rule against build.** `python scripts/audit/aiid_corpus_audit.py crosscheck` compares, for each option, the set of AIID rows the rule predicts (§2 paths) with the set the real build moved:

  ```
  O1     rule=   1 build=   1 equal=True
  O2     rule=  14 build=  14 equal=True
  O3     rule= 786 build= 786 equal=True
  O2+O3  rule= 863 build= 863 equal=True
  ```
- **Projected error.** `python scripts/audit/aiid_corpus_audit.py project` takes the stored label, flips it on the rows the option's build moved, and compares the result with the adjudicated label.

### 4.2 Options

Every option below that is a build changes `updated`/`last_seen` on each row whose `corpus` moves. That cascade is intended: `corpus` is a D73 content field (`_CONTENT_FIELDS`). Every build also restamps `generated`. No option changes the row count, the ID set, the ID order, `incident_count` or any field other than those listed.

| option | what | rows moved: field (count) | other cascade | published counts | est. wrong AIID labels, R1 (sample / holdout†) | new-24 wrong, R1 | needs |
|---|---|---|---|---|---|---|---|
| **O0** do nothing | none | none | none | none | 746 (45.3%) / 644† | 8/24 | none |
| **O1** narrow override | `data/curation_overrides.json` key `AIID-195` sets `corpus: ai-harm` (D139-M / INC-02454 precedent) | corpus 1, updated 1, last_seen 1: INC-07572 | key order on INC-07572 (corpus now before quality_tier; bytes only) | none | 745 in fact; the sample estimate prints 743 because of stratum weight | 8/24 | this run (§5) |
| **O2** keyword fix | `rce` matched as `\brce\b` in `_classify_corpus` only | corpus 26, updated 26, last_seen 26, **tier 12** | 12 non-AIID rows (10 AIAAIC, 1 legacy, 1 AVID; listed below) go security→ai-harm **and feed→landmark** | **landmark_count 2,080 → 2,092** (README/DATASHEET/site/CITATION via render_docs_stats) | 728 (44.2%) / 639† | 8/24 | user ruling, since a published count moves |
| **O3** AIID no-match default → ai-harm | in `_classify_corpus`, `aiid_id` and no keyword gives `ai-harm` | corpus 786, updated 786, last_seen 786 | tier 0 (AIID rows are landmark through `aiid_id`) | none | **235 (14.3%) / 196†** | **14/24, worse**: it flips 11 agent-security rows plus the INC-17386 breach | user ruling |
| **O2+O3** | both | corpus 875 (863 AIID + 12), updated/last_seen 875, tier 12 | as O2 | landmark +12 | **183 (11.1%) / 149†** | **12/24, worse** | user ruling |
| **O5** candidate | O2, plus AIID no-match → `ai-harm` unless the text has a security term (breach, hack, credential, unauthori…, token, attacker, cyber…, spyware, malicious, steal/stolen, compromis…, exposed, extort…, impersonat…, exploit…, threat actor) | corpus 688 (676 AIID + 12), updated/last_seen 688, tier 12 | as O2 | landmark +12 | 225 (13.7%) / **124 (15.7%)†** | **3/24** (in-sample: the terms were written after reading these rows) | WS2-T4 vocabulary approval + user ruling |
| **O6** candidate | decouple AIID corpus from the description: MIT risk-domain tag 2 or 4 → security, other domains → ai-harm; untagged rows keep the keyword path | corpus 577 (574 security→ai-harm, 3 ai-harm→security), updated/last_seen 577 | tier 0 | none | 315 (19.2%) / 183† | 8/24 (the new rows have no MIT tag) | user ruling |

† The holdout covers only the `default` and `rce-artifact` paths (793 rows), and its percentage is over those 793 rows. Its absolute counts are not comparable with the whole-population column.

Under R2 the ranking is the same except that O2+O3 leads: sample 378 (23.0%) for O2+O3 against 499 (30.3%) for O5. The full table is in the `project` output (§7).

O2's 26 rows are INC-01371, 02287, 02549, 03311, 04040, 04094, 04313, 04505, 04801, 05063, 05085, 05103, 05455, 05573, 06995, 07158, 07170, 07219, 07420, 07516, 07543, 07572, 07613, 07706, 08167 and 08169. The 12 non-AIID rows among them are INC-02549 (legacy INC-071, one of D130-2L's three leftover `rce` rows), 04313, 04505, 05103, 05455, 05573, 07158, 07219, 07420, 07516 (AVID), 07543 and 07613. By title, all 12 look like ai-harm, but I did not adjudicate them.

O2 has a latent cascade. The OECD `classify_corpus_signal` shares the keyword tuple, and its docstring promises byte-identical output to `_classify_corpus`. A complete O2 would therefore also change OECD corpus at the next OECD ingest. That delta cannot be computed offline, because the OECD narrative signal is not stored (E21). The O2 dry-run above patches only the merge-time match, which leaves the two classifiers divergent. Decide that before adopting O2.

Surfaces any corpus move reaches:
- `data/incidents.json`, `data/incidents.min.json`, `docs/data/incidents.min.json` and `src/genai_incidents/data/incidents.min.json`.
- At deploy: the site core data (the corpus filter in `docs/index.html`), STIX `x_corpus` plus `modified` (through `updated`), the MISP `genai-incidents:corpus` tag, the HF `corpus` column and TAXII.
- No live doc publishes a per-corpus count (grep for 538 / 1,436 / "ai-harm corpus" outside the audits and board finds nothing).

## 5. Recommendation

**O1 now, implemented on this branch. The mass relabel is held for the user, with two rulings needed first.**

1. **Definition ruling, R1 or R2.** The repo states both (§3.1). The choice moves the estimated error between 45% and 62%, and it changes which mass option is best.
2. **Then a mass option, from O5 or O6 or a combination, not O3.**
   - **O3 is the trap.** It has the best-looking sample estimate, but the most recent AIID intake is mostly agent-security incidents, and O3 makes the new-24 cohort *worse* (8 → 14 wrong). The default path's composition is drifting, so a fixed default cannot track it.
   - **O5** has the best held-out result under R1 (15.7%), but its vocabulary is mine, written after reading the data. WS2-T4 rules require approval before implementing it, and it needs a second annotator.
   - **O6** is the WS0-T3-style structural fix. It reads AIID's closed upstream vocabulary instead of templated prose, so no future entity-list edit can move a label, though it is less accurate (23.1% held out).
   - **A likely best design is O6 for tagged rows plus O5's guarded default for untagged rows.** It is not measured here.
3. **O2 on its own is low value** (an estimated 18 of about 746 errors) and moves `landmark_count`. Fold it into whichever mass option is chosen, together with the OECD-side decision above.

## 6. A check that can fail (agreement 6)

Command: `python scripts/audit/aiid_corpus_audit.py flipguard --base <ref> (--head <ref> | --head-file <path>) [--allow ID,…]`

This is a per-entity check. Every row present at both refs whose `corpus` differs must appear in `--allow`, and any undeclared flip exits 1. **The input that makes it fail** is a refresh whose upstream text edit moves a label nobody declared, which is exactly PR #110.

Proof that it fires:

| step | input | result |
|---|---|---|
| 1 | PR #110 pair `6a4d8261`→`f6f3e36c`, nothing declared | rc=1, `UNDECLARED INC-07572: ai-harm -> security` |
| 2 | same pair, `--allow INC-07572` | rc=0 |
| 3 | control `8753a7fe` against itself | 0 flips, rc=0 |
| 4 | this branch's built `data/incidents.json` against `8753a7fe`, `--allow INC-07572` | 1 declared flip, rc=0 |
| 5 | same, undeclared | rc=1 |
| 6 | corrupt: scratch copy of step 4's file with INC-05107 flipped ai-harm→security | rc=1, `UNDECLARED INC-05107`, while INC-07572 stays declared |
| 7 | restore: step 4 rerun on the uncorrupted file | rc=0 |

The same bounded ID-list comparison would catch the WS0-T3 cascade and this flip. It is not wired into CI here. **Suggestion for the foreman:** run it in `auto-refresh` against the PR base, with the declared list taken from the D120 change report.

The pinned tests are in `tests/test_aiid_corpus_inc07572.py`:
- `test_inc07572_is_ai_harm` fails on base data (seen: pointing `data/incidents.json` at `8753a7fe` fails it; restoring passes, sha1 `a415d610…` before and after).
- `test_override_is_still_load_bearing` fails once O2 is applied (seen: applying the O2 patch fails it; restoring passes). That failure is the signal to retire the override.

## 7. O1 as implemented: field-level delta [R]

- **Input change:** `python scripts/audit/aiid_corpus_audit.py apply-o1` adds one key to `data/curation_overrides.json`. It is written by code, LF line endings, 4 added lines and no other line changed. The override's `_note` says it is agent-suggested and pending user re-review.
- **Rebuild:** `parse_existing.py`, `merge_and_dedupe.py`, `render_markdown.py`, `render_docs_stats.py`, `validate.py` and `lint_atlas_ids.py`, the same chain as `make build`.

Independent route, the existing `scripts/audit/field_delta_vs_ref.py --ref 8753a7fe` rather than this audit's own dry-run code:

```
rows: 15845 -> 15845; ids added=0 removed=0
id_deprecations.json byte-identical: True
top-level keys changed: ['generated']
rows with any change: 1
rows whose key ORDER changed with an identical key set (byte-level only): 1 ['INC-07572']
  field corpus: 1 rows  by source {'OECD': 1}
  field last_seen: 1 rows  by source {'OECD': 1}
  field updated: 1 rows  by source {'OECD': 1}
```

Every delta is enumerated and intended:

| delta | detail |
|---|---|
| INC-07572 `corpus` | security → ai-harm, the fix. |
| INC-07572 `updated` and `last_seen` | 2026-11-22 → the build's UTC date, 2026-11-25. This is the D73 content-field cascade. |
| INC-07572 key order | `corpus` is now set at step 4d, before `quality_tier`. Bytes only. |
| `generated` restamp | In `incidents.json`, `incidents.min.json`, `stats.json`, `README.md` and `INCIDENTS.md`. Every build does this. |
| `tier` | Unchanged: the row is already landmark through `aiid_id`. |
| `stats` | No count changes. |

Files changed: `INCIDENTS.md`, `README.md`, `data/curation_overrides.json`, `data/incidents.json`, `data/incidents.min.json`, `data/stats.json`, `docs/data/incidents.min.json` and `src/genai_incidents/data/incidents.min.json`. The first build of this tree with no override gave an empty porcelain, so the base reproduces.

Aside, not acted on: the 164 AIID+OECD rows ignore the OECD-persisted corpus because `merge_into` does not carry it. 14 of them disagree with their OECD members after O1, and 15 did at base.

## Corrections (gate bounce 1, 2026-11-25)

The red-reviewer gate found two text errors before merge. Both were re-derived from the committed evidence and fixed in place. No data, script or test changed.

1. §3.2. Old: "All of the extra errors come from `sec-keyword`: 14 of 30 rows there are non-fraud deepfake, CSAM or disinformation." New: "Most of the extra errors (about 248 of the net 273) come from `sec-keyword`: 14 of 30 rows there are non-fraud deepfake, CSAM or disinformation. `default` adds about 39 and `harm` removes about 14." Basis: from R1 to R2, the sample's wrong counts per stratum in `adjudication.csv` are sec-keyword 1→14 (+248.3 population-weighted), default 33→35 (+39.3), harm 2→0 (−13.9) and rce-artifact 25→25 (0). The unrounded net is +273.7, which matches 746→1,019 on the rounded totals.
2. §3.4 attack_vector table. Old: "| **generic** | 11 rows |". New: "| **generic** | 10 rows |". Basis: `new24.csv` has 10 generic rows (INC-17372, 17373, 17374, 17375, 17378, 17379, 17380, 17381, 17383, 17384). The verdict tally is ok 10, generic 10, wrong 3, unverifiable 1, for a total of 24.
