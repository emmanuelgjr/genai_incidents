# OECD/AIID freeze, stage 2: ruling package (follow-ups a2, a3; engineering b9), 2026-10-13

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4). Author: pipeline-engineer (WS4). **Nothing here is approved, ruled or human-reviewed. I decide nothing**; every "recommendation" below is an agent suggestion for the user to accept, change or reject. Edits no `data/*.json`, ingest file, script, workflow or test. The earlier memo `docs/audits/oecd-aiid-unfreeze-decision-memo-2026-10-09.md` is a record and is not edited; where today's measurement differs from it, the difference is stated here and the memo stands as written.
>
> Base: `main` @ `9c646d36`. Measured on 2026-10-13 against the `held-oecd-aiid-inputs` artifacts of weekly-refresh runs **38366793761** (today, dispatched from `main`, concluded success) and **38330687613** (2026-10-13 01:08Z, branch `ws4/v2130-refresh-decouple`). Artifacts expire 2026-11-12 (30-day retention); the hashes in section 0 pin what was measured.

## Ruling card (the five decisions; detail in section 2)

| # | Decision | Options | My recommendation (suggestion only) |
|---|---|---|---|
| (a) | Lift, narrow or keep stage 1 | A1 keep unchanged / A2 lift the AIID side only, keep OECD held / A3 lift everything except the doubtful bridges (needs new machinery) / A4 lift everything | **A2** now; A3 as a later design task; do not do A4 |
| (b) | The D42 17 changes (7 merges + 10 retitles; today re-derived as 7 + 12) | approve all / reject all / partly approve | **Partly: record a per-item ruling now, but understand it publishes nothing until machinery exists.** Following the D42 evidence: approve-in-principle 3 merges (M1, M2, M5) and 6 retitles (R1-R6); reject 4 merges (M3, M4, M6, M7) and 4 retitles (R7-R10); R11 and R12 (new since D42) need a raw-record read first (table in 2.b) |
| (c) | AIID-only new rows | hold / ship 113 / ship a subset | **Ship, as part of A2** (113 rows when OECD stays held; 61 if OECD is lifted too) |
| (d) | OECD `title` licence position | D1 ship incl. growth / D2 keep the existing 3,937, add no new OECD rows / D3 project-composed titles for new rows / D4 retract existing OECD titles | **D2 as the safe default**, plus the follow-up email in section 5 (user sends) |
| (e) | How approvals are recorded | one signed file of per-item entries / bulk or class approvals / both | Per-item file for the merges and retitles; **a bulk form is needed for adds** (1,935 source rows) |

**The single most important fact for ruling order:** the gate as built is all-or-nothing. A partial approval list publishes nothing, and today there is no way to say "reject and continue" (no suppression list, S7). So rulings that *reject* anything (b, parts of a) have no operative effect until engineering builds that. Rulings that *approve* everything the gate flags are operative but would ship items the evidence marks wrong. Section 3 sets out what each choice leaves for engineering.

---

## 0. Method, and what each count would catch

**Inputs pinned.** `gh run download <run> -n held-oecd-aiid-inputs` for both runs. sha256 of the fresh bytes (identical to each run's `HOLD_REPORT.json`):

| file | run 38366793761 (10-13 today) | run 38330687613 (10-13 01:08Z) |
|---|---|---|
| `aiid_full.json` | `620bbb6363b969e4ac711c48d31dac1772e7024c285017de80b2431b18e759be` | same |
| `aiid_full.provenance.json` | `34d37aa10402b4025c88ab0694f54d43dd6528fbed72c8ee2f996c3785ffffbc` (snapshot `backup-20261012101643.tar.bz2`, sha256 `01d0ae55...c218683`) | same |
| `oecd_aim_full_incidents.json` | `ef493045656944b7086ee0d54fe5d7827c961cda1d266dd710ec25eb523ba5c4` | `4b2b702038ae0a03fdeae7919752b41df15259ab59ed1c89b038094415584edd` |

Both runs' reports say `aiid_incidents.json`, `aiid_oecd_relationships.json` and `airi_navigator_incidents.json` did **not** change (`changed: false`), so only these three files are overlaid. Today's figures use run 38366793761.

**Builds (all in scratch clones outside the worktree; no committed file other than this package).**
1. **Control**: a clone of `main` @ `9c646d36`, no overlay, `parse_existing.py` then `merge_and_dedupe.py`. Result: `data/incidents.json` (49,150,699 bytes) and `data/id_deprecations.json` (142,136 bytes) **byte-identical to `git show HEAD:`**. This is what proves the later deltas come from the overlay and not from clock or environment drift. Input that would have made it fail: any non-determinism in the build.
2. **Gated build**: control + the three fresh files, with the single edit `problems[:25]` to `problems` in the scratch copy of `merge_and_dedupe.py` so the abort message lists every held change. Result: `[FATAL] D42/D25(a)+D67+D71 ... (2066)`, "Nothing was written" (exit 1). The gate fires on fresh inputs and, per the control, does not on committed ones. Input that would change the number: any different overlay (the OECD-only and AIID-only runs below give different counts).
3. **Ungated builds** (same scratch edit replaced the gate call by `pass`) for four overlays: both sources, OECD only, AIID only. Each output compared **per entity** with HEAD (row by row, field by field, not by aggregate). The independent route: the gate's class counts (step 2) and the per-entity comparison (step 3) are separate code paths over the same data; they agree (7 merges; 12 + 25 = 37 retitled rows; 190 changed rows = 190 content problems; 1,832 entries with a new gated source id = 1,811 new rows + 21 published rows).

**Not done, and why it matters.** I did not read the raw OECD or AIID pages behind any merge. The same-incident review D25(a)(2) asks for is a human's; every statement below about whether two rows are one incident is a title-level reading or the D42 evidence file's testimony, labelled as such.

---

## 1. What stage 1 holds today, and what it costs

### 1.1 The classes the gate holds (read from `scripts/merge_and_dedupe.py` `_check_refresh_merge_authorization`, line numbers at `9c646d36`: function ~2210-2322, `_run_refresh_gate` 2325)

| Class | Trigger | Approval kind in `D42-approved-refresh-merges.json` |
|---|---|---|
| merge | a published ID retired into another by a `merged`/`transitive-merge` deprecation touching an `OECD-AIM-`/`AIID-` source id | `{"kind":"merge","from","into"}` |
| retitle | a published ID's title changes after it absorbs `OECD-AIM-`/`AIID-` source ids it did not hold | `{"kind":"retitle","id"}` |
| title edit (D67) | a published OECD/AIID-sourced row's title changes with no id absorbed (exempt only if a curation override keyed to the row's own source id sets exactly that title) | `{"kind":"retitle","id"}` (same kind) |
| content change (D71/A2) | any other `_CONTENT_FIELDS` change (plus `description_provenance`/`description_source`) on a published OECD/AIID row, **only while a pair input differs from HEAD** | `{"kind":"content","id"}` |
| add (D67/D71) | any `OECD-AIM-`/`AIID-` source id no published entry carried, whether it becomes a new row or is absorbed | `{"kind":"add","source_id"}` |

The pair inputs are `_PAIR_INPUT_FILES`: `aiid_full.json`, `aiid_incidents.json`, `aiid_oecd_relationships.json`, `oecd_aim_full_incidents.json`, `airi_navigator_incidents.json`. Separately, in the weekly workflow `scripts/hold_pair_inputs.py` restores those files (plus the AIID provenance sidecar) to HEAD before the merge and uploads the fresh bytes as the artifact (D66). So in practice **the gate never sees fresh pair bytes in the weekly run**; the artifact is the only place they land. The gate itself is the second lock, hit only by a manual run like the ones in this package.

### 1.2 What is held NOW, re-derived (fresh inputs of 2026-10-13 vs `main`)

Gate output, full list: **2,066 held changes** (7 + 12 + 25 + 190 + 1,832):

| Class | Held now | Memo (2026-10-09, figures from 2026-10-03) | Note |
|---|---|---|---|
| merges (new `merged` deprecations) | **7** | 7 | The same 7 retired IDs (`INC-01469, -02381, -08148, -13241, -14310, -14317, -14902`). All 7 come from OECD alone: an OECD-only overlay also gives 7. |
| retitles (absorbing OECD/AIID ids) | **12** | 10 | The 10 D42 IDs are all still there; 2 are new since 2026-10-03: `INC-14284`, `INC-14407`. OECD-only gives 4 (`INC-00699, -01514, -01579, -01994`), AIID-only gives 0, so the other 8 need both fresh sources. |
| title edits, no id absorbed | **25** | "24 upstream AIID title edits, not gated" (the D67 gate holds them now; the memo's figure was from the D42 review file, section C) | All 25 new titles equal AIID's own current title for the row. Typical edits: "Reportedly/Allegedly" insertions, curly to straight apostrophes. One is `INC-00437`. AIID-only overlay gives 25. |
| content changes | **190** rows | "20 common rows changed" (2026-10-03, OECD only) | Every one is a row that carries an OECD/AIID id. Per-field table in 1.3. OECD-only gives 23, AIID-only gives 169. |
| adds (source rows) | **1,935** source ids on **1,832** entries (1,811 new rows + 21 published rows that absorb a new source) | +1,533 new-only IDs and "about 94 AIID rows by subtraction, unmeasured" | See 1.4. The gate counts one problem per entry (1,832); an approval file needs one `add` per source id (1,935). |

Total approval entries a full lift would need under today's kinds: **7 + 37 + 190 + 1,935 = 2,169.**

Accounting for rows: HEAD 15,666 rows in `incidents.json` (15,637 non-retracted + 29 retracted). Ungated, both sources: 15,666 + 1,811 new - 7 retired = **17,470** rows (`incident_count` 15,637 to 17,441, `retracted_count` stays 29); `id_deprecations.json` 1,084 to 1,091 records, 0 existing records changed or dropped.

### 1.3 Field-level delta preview, "lift everything" (both sources, ungated)

Existing rows changed: **190** (all carry an OECD/AIID id; none without one). Field counts across those 190 rows (one row appears in several): `last_seen` 190, `updated` 190 (every changed row is stamped), `description` 180, `affected` 163, `title` 37, `references` 25, `source_ids` 23, `source_count` 23, `date` 14, `aiid_id` 14, `tags` 14, `tier` 12, `attack_vector` 11, `mitre_atlas` 10, `mitre_atlas_tactics` 10, `nist_ai_rmf` 10, `owasp_llm` 10, `corpus` 7, `owasp_asi` 8, `description_provenance` 9, `description_source` 9, `year` 4, `severity` 4, `source_freshness` 1. Shape: 132 rows change only `affected` + `description` (+ the two stamps), 21 more change title as well, 21 change other fields without title, 16 change title and other fields. 153 rows change nothing outside title/description/affected.

Intended-versus-unintended notes (agreement 2): (i) `description` changes on 180 rows, but in every case the new description is still one of the two project templates (0 of 180 are non-template), so no OECD/AIID narrative enters; the change is the template's own "Alleged deployer/developer" list following AIID's updated deployer/developer data (`affected`). (ii) `severity` moves on 4 rows, all upward (`INC-05170` Medium to High, `INC-00699` High to Critical, `INC-01514` High to Critical, `INC-14517` Medium to High); the memo said 4 upward severity changes, same count. (iii) `corpus` moves on 7 rows: 6 `ai-harm` to `security`, and `INC-01579` `security` to `ai-harm` (it takes AIID's title and template). (iv) `date` moves earlier on 14 rows, because a retitled/merged entry now holds an older source row (largest: `INC-00699` 2026-03-18 to 2024-06-24, `INC-01994` 2026-02-20 to 2025-06-27, `INC-01579` 2026-05-12 to 2025-05-31). (v) `aiid_id` is set or changed on 14 published rows: 13 gains from none (all from OECD alone) and one **changed value**, `INC-03717` 687 to 1684 (R10, an evidence-marked do-not-approve retitle). (vi) Nothing outside the pair's rows changes: control shows 0 diff for everything else.

New rows: **1,811**, IDs `INC-17216` to `INC-19026` (contiguous, none reused; the high-water mark moves to 19,026). Mix: **1,712 OECD-only, 61 AIID-only, 38 both**. Corpus 1,781 `security` and 30 `ai-harm`. Severity High 1,004, Medium 410, Critical 397. IDs and tombstones: 7 IDs leave `incidents.json` and gain `merged` records (append-only; permanent); no deletion, no ID reuse; the full-file `id_deprecations.json` grows by exactly those 7.

### 1.4 Per-source decomposition (what each fresh source does alone)

| Overlay | rows | merges | retitles (absorb) | title edits | content-changed rows | new rows | new gated source ids |
|---|---|---|---|---|---|---|---|
| both (above) | 17,470 | 7 | 12 | 25 | 190 | 1,811 (1,712 / 61 / 38) | 1,935 |
| OECD only (AIID held) | 17,409 | 7 | 4 | 0 | 23 | 1,750 (1,712 OECD-only + 38 both) | 1,874 (OECD 1,806, AIID 68) |
| AIID only (OECD held) | 15,779 | **0** | **0** | 25 | 169 | **113** (all AIID-only) | 113 |

Readings: the merges and the doubtful bridges are an **OECD-side** phenomenon (7 of 7 from OECD alone). The AIID snapshot alone produces **no merges and no absorbing retitles**; its held change is 113 new AIID-only rows, 25 title edits and 169 rows with refreshed `affected`/`description`. The "AIID-only rows" figure is 113 if OECD stays held and 61 if OECD is lifted too (52 of the 113 are then cited by a new OECD row and become "both" rows). The memo's "about 94" was a subtraction of two unlike measurements; it is not reproduced (113 measured, with `entries_security_relevant` 1,099 to 1,211 = +112 in the provenance sidecar as a cross-check; the one-row difference is not explained and is not needed for the ruling).

### 1.5 Staleness cost (what is not in the corpus because of the hold)

| Source | In the corpus now | Upstream (artifact, 2026-10-13) | Gap |
|---|---|---|---|
| OECD AIM raw rows | 4,160 raw rows, newest event date **2026-07-16**, 0 rows dated 2026-08-01 or later | 5,966 rows, newest 2026-10-12 | **1,806 OECD source ids not ingested (30.3% of upstream)**, of which 1,537 dated 2026-08-01 or later and 269 dated earlier. 0 committed ids are missing upstream. 0 titles differ for the 4,160 common ids. About 20 new rows per day (1,806 over 88 days; the two 10-13 runs differ by 20 new and 2 vanished ids). |
| AIID snapshot | `backup-20260713110347` (1,548 entries, max AIID id 1581, fetched 2026-07-18, committed 2026-08-17) | `backup-20261012101643` (1,665 entries, max id 1747) | 117 new AIID ids (113 become rows), 27 existing AIID titles edited upstream, 0 ids lost. |
| Published rows | 4,104 carry an `OECD-AIM-` id | | An unfrozen corpus would carry 5,851 |

Cost reading: the committed OECD view is **88 days behind** (newest event 2026-07-16 vs 2026-10-12) and the AIID view **91 days behind** (snapshots 2026-07-13 vs 2026-10-12); the gap grows by roughly 140 OECD rows and a few AIID rows per week. Every weekly run uploads the fresh bytes as an artifact retained 30 days, so recent weeks are recoverable from artifacts; older ones would need a re-crawl (not checked here). Other costs of the hold: the weekly PR is meant to carry the other sources (D66); PR #102 "Weekly data refresh" is open from `auto-refresh/data`, which I did not inspect (open fact 10). Retitles that the hold keeps from shipping include 5 that D42 itself marked approve (R1-R5). The hold also keeps 25 AIID corrections (mostly hedged "Reportedly/Allegedly" wording) off published titles.

---

## 2. The decisions

### (a) Lift, narrow or keep stage 1

**A1. Keep stage 1 unchanged.**
- Consequence: nothing changes in the corpus; staleness grows as in 1.5; `hold_pair_inputs.py` and the gate keep working; no engineering.
- Risk: the corpus drifts further from its sources, so the later unfreeze delta only gets bigger (about +140 OECD rows/week) and the reviewed 17 get staler (2 new retitles appeared in 10 days); the user's review burden rises with time. The 30-day artifact retention means reviewed evidence must be regenerated.

**A2. Narrow: lift the AIID side only; OECD (and AIRI) stay held.**
- Consequence (measured, AIID-only overlay): +113 AIID-only rows (`INC-17216..INC-17328`; all `security`, all tier `landmark`, description is the project template "AI Incident Database (AIID) entry #n ..."; severity Medium 76 / High 30 / Critical 7; years 2020:1, 2022:2, 2023:6, 2024:11, 2025:14, 2026:79); 25 published-title edits (table 2.a-1); 169 content-changed rows (168 `description`, 154 `affected`, 25 `title`, 6 `corpus`, 5 `attack_vector`, 4 `references`, 3 `date`, 2 `tags`, 2 each of the provenance labels, 1 `year`; plus `updated`/`last_seen` on all 169). 0 merges, 0 tombstones, 0 retired IDs. 39 of the 169 changed rows also carry an OECD id (they are mixed rows; their AIID-driven fields change, their OECD fields do not).
- E23 fit: E23's ruling is shape-based (the only AIID-authored text kept is a bare title; Layer 1 rests on U.S. situs; Layer 2 on the U.S. maker). 113 new titles and 25 edited titles are the same shape. But E23's published counts (1,463 of 1,465 etc.) and the "marker absence" measurement must be re-run (memo R4/R3), and the `aiid_incidents.json` (63 rows) / AIRI exclusion tripwire must still hold; I did not re-run those.
- Risks: still rests on E23's uncertified situs (unchanged in kind, memo R5); AIID's own sentence "report contents are subject to their own intellectual property rights" applies to report text, which does not ship; 113 + 25 is about 7 percent growth in the AIID-titled population.
- Recommendation: **A2.** Reasons: it is the only slice with 0 merges and 0 deprecations, so nothing permanent is written; it is covered by an existing ruling in kind; it recovers the 25 corrections and 113 current incidents; it leaves the OECD title question (d) and the bridge question (b) untouched. Cost: engineering in section 3 (the hold script and the gate treat the pair as one).

**A3. Lift both sources, but suppress the bridges the user rejects.**
- Consequence: depends on (b). Needs a suppression capability that does not exist (memo S7). My scratch emulation shows it is not trivial: stripping the doubtful AIID ids only from **fresh** OECD rows removed 2 of the 7 merges (M6, M7) and 1 of 12 retitles (`INC-03717`), leaving 5 merges and 11 retitles; the bridges M3, M4 and the `INC-00699`, `INC-00813` retitles still formed, because the published OECD rows already cite those AIID ids and the arriving AIID rows complete the key. Stripping the ids from **all** OECD rows (published ones too) made the build abort with the WS4-T19 split guard: it would split `INC-01628`, `INC-13066` and `INC-14317` into more rows (no D28 authorization for them). So a suppression must be keyed on the AIID id at the dedup-key level, and each suppression of an already-published bridge probably needs a split authorization or a different mechanism. This is design work, not a flag.
- Risk: the heuristic problem (an AIID id on an OECD row acts as a dedup key) is only moved, not solved; a new bridge appears weekly. A heuristic change (one OECD row's cross-references cannot bridge two published entries) is the durable fix and affects all future builds.
- Recommendation: a design task after (b)/(d), not a ruling now.

**A4. Lift everything (approve all).**
- Consequence: 2,169 approval entries; 7 permanent tombstones; the 4 evidence-marked do-not-approve merges M3, M4, M6, M7 and retitles R7-R10 ship; 1,720 more OECD LLM titles ship (section (d)).
- Risk: permanent wrong redirects; broader licence exposure; no way to un-merge except the D28-style split machinery.
- Recommendation: do not choose A4.

**Table 2.a-1: the 25 published-title edits (all AIID's current title; ID unchanged; the gate class "title edit")**

| id | before | after |
|---|---|---|
| INC-00437 | AI-Generated Explicit Images of Students Spark Investigation at Lake Zurich High School | Purportedly AI-Generated Explicit Images of Students Allegedly Circulated at Lake Zurich High School in Illinois |
| INC-01400 | Meta AI Smart Glasses Reportedly Exposed Intimate User Imagery and Video to Human Reviewers in Kenya | Meta AI Smart Glasses Reportedly Routed Intimate Imagery to Reviewers at Kenyan Contractor Sama Before Meta Ended Contract |
| INC-03399 | 1 in 6 Congresswomen Have Reportedly Been Targeted by AI-Generated Nonconsensual Intimate Imagery | One in Six Congresswomen Have Reportedly Been Targeted by AI-Generated Nonconsensual Intimate Imagery |
| INC-03462 | AI Firm Lovo Accused of Illegally Replicating Voice Actors' Voices | AI Firm Lovo Reportedly Accused of Illegally Replicating Voice Actors' Voices |
| INC-03757 | ESPN's AI Coverage Overlooks Alex Morgan in Her Final Match Recap | ESPN's AI Coverage Reportedly Overlooks Alex Morgan in Her Final Match Recap |
| INC-04259 | Teenager Makes Deepfake Pornography of 50 Girls at Bacchus Marsh Grammar School in Australia | Teenager Reportedly Makes Deepfake Pornography of 50 Girls at Bacchus Marsh Grammar School in Australia |
| INC-04469 | Australian Terrorism Prediction Tool Disparately Impacts Persons with Autism | Australian Terrorism Prediction Tool Reportedly Disparately Impacts Persons with Autism |
| INC-05126 | Google Search Returned Fewer Results for Abortion Services in Rural Areas | Google Search Reportedly Returned Fewer Results for Abortion Services in Rural Areas |
| INC-05195 | Stable Diffusion Exhibited Biases for Prompts Featuring Professions | Stable Diffusion Reportedly Exhibited Biases for Prompts Featuring Professions |
| INC-05456 | Amazon Forced Deployment of AI-Powered Cameras on Delivery Drivers | Amazon Allegedly Forced Deployment of AI-Powered Cameras on Delivery Drivers |
| INC-05734 | Kenyan Data Annotators Allegedly Exposed to Graphic Content for OpenAI's AI | Kenyan Data Annotators Reported Psychological Trauma from Labeling Graphic Text for ChatGPT Safety Systems |
| INC-06762 | Live facial recognition is tracking kids suspected of being criminals | Buenos Aires Government Reportedly Used Children's Personal Data in Facial Recognition System for Fugitives |
| INC-07137 | YouTube Auto-Moderation Mistakenly Banned Women of Sex Tech Conference | YouTube Auto-Moderation Reportedly Banned Women of Sex Tech Conference |
| INC-07280 | Calgary Malls Deployed Facial Recognition without Customer Consent | Calgary Malls Reportedly Deployed Facial Recognition Without Customer Consent |
| INC-07304 | Facial Recognition Program in São Paulo Metro Stations Suspended for Illegal and Disproportionate Violation of Citizens’ Right to Privacy | Facial Recognition Program in São Paulo Metro Stations Suspended for Illegal and Disproportionate Violation of Citizens' Right to Privacy |
| INC-07366 | Instagram's Exposure of Harmful Content Contributed to Teenage Girl’s Suicide | Instagram's Exposure of Harmful Content Allegedly Contributed to Teenage Girl's Suicide |
| INC-07429 | New York Detective Misused Woody Harrelson's Face to Perform Face Recognition Search | New York Detective Reportedly Misused Woody Harrelson's Face to Perform Face Recognition Search |
| INC-07436 | Researchers' Homosexual-Men Detection Model Denounced as a Threat to LGBTQ People’s Safety and Privacy | Researchers' Homosexual-Men Detection Model Denounced as a Threat to LGBTQ People's Safety and Privacy |
| INC-07476 | Amazon’s Experimental Hiring Tool Allegedly Displayed Gender Bias in Candidate Rankings | Amazon's Experimental Hiring Tool Allegedly Displayed Gender Bias in Candidate Rankings |
| INC-07494 | Facial Recognition Smart Phone App "Blue Wolf" Monitored Palestinians in West Bank | Facial Recognition Smart Phone App 'Blue Wolf' Reportedly Monitored Palestinians in the West Bank |
| INC-07497 | Google Image Showed Racially Biased Results for “Professional” Hairstyles | Google Images Showed Racially Biased Results for 'Professional' Hairstyles |
| INC-07558 | Facebook’s "Tag Suggestions" Allegedly Stored Biometric Data without User Consent | Facebook's 'Tag Suggestions' Allegedly Stored Biometric Data without User Consent |
| INC-07565 | Google’s Face Grouping Allegedly Collected and Analyzed Users’ Facial Structure without Consent, Violated BIPA | Google's Face Grouping Allegedly Collected and Analyzed Users' Facial Structure without Consent, Violated BIPA |
| INC-07621 | Facial Recognition Researchers Used YouTube Videos of Transgender People without Consent | Facial Recognition Researchers Allegedly Used YouTube Videos of Transgender People Without Consent |
| INC-14682 | Eightfold AI Sued for Secretly Profiling Job Applicants with AI | Eightfold AI Hiring Tools Allegedly Secretly Scored Job Applicants for Employers |

### (b) The D42 17 (today: 7 merges + 12 retitles), item by item

How to read: "D42 evidence" is the 2026-10-03 file `docs/audits/D42-proposed-refresh-merges.json` (testimony, not re-read by me); "survivor" is the row that stays. Before/after are today's measurement. Raw OECD/AIID rows were not opened by me. Merges are permanent (append-only `id_deprecations.json`); retitles are editable later.

**Merges**

| # | retired -> into | retired row title (published today) | survivor title today -> after | ids the survivor gains | D42 evidence recommendation (2026-10-03, testimony) |
|---|---|---|---|---|---|
| M1 | INC-02381 -> INC-01579 | California Teen Reportedly Died of Overdose After Repeatedly Seeking Drug-Use Guidance Allegedly from ChatGPT | OpenAI Sued After ChatGPT Advice Allegedly Leads to Fatal Overdose -> California Teen Reportedly Died of Overdose After Repeatedly Seeking Drug-Use Guidance Allegedly from ChatGPT | AIID-1370 | APPROVE |
| M2 | INC-14310 -> INC-01994 | Tesla Autopilot Failure and Data Suppression Lead to Fatal Crash and Legal Defeat | US Court Upholds $243 Million Verdict Against Tesla Over Fatal Autopilot Crash -> Tesla Faces Trial Over Fatal Autopilot Crash in Florida | AIID-1686, OECD-AIM-2025-06-27-892e, OECD-AIM-2025-08-01-b7fe, OECD-AIM-2025-09-01-dc79, OECD-AIM-2026-07-01-6cd1, OECD-AIM-2026-09-01-dee9 | APPROVE |
| M3 | INC-01469 -> INC-00699 | Music Publishers Sue Anthropic Over AI Copyright Infringement | BMG Sues Anthropic Over AI Training With Copyrighted Song Lyrics -> Record Labels Sue AI Music Generators for Copyright Infringement | AIID-1655, AIID-1656, AIID-1657, OECD-AIM-2023-10-18-a6f8, OECD-AIM-2024-06-24-413e, OECD-AIM-2024-08-02-4bed, OECD-AIM-2025-01-04-c501, OECD-AIM-2025-09-22-8350, OECD-AIM-2026-03-24-ed03, OECD-AIM-2026-07-11-995f, OECD-AIM-2026-07-17-9a57, OECD-AIM-2026-07-30-2c05, OECD-AIM-2026-08-05-9a62, OECD-AIM-2026-08-17-8fdd | UNSURE, lean DO NOT APPROVE |
| M4 | INC-08148 -> INC-01628 | AI Chatbots Falsely Pose as Licensed Doctors in Pennsylvania | Digital Rights Groups Accuse Meta and Character.AI of Facilitating Unlicensed Therapy via Chatbots -> Digital Rights Groups Accuse Meta and Character.AI of Facilitating Unlicensed Therapy via Chatbots | OECD-AIM-2026-06-08-113e | UNSURE, lean DO NOT APPROVE |
| M5 | INC-13241 -> INC-01514 | AI-Powered Data Centers Linked to Pollution and Military Operations Spark Legal Battle | NAACP Sues xAI Over Illegal Gas Turbine Use for AI Data Center, Citing Pollution and Health Risks -> xAI Data Centers Linked to Unpermitted Pollution in Mississippi and Tennessee | AIID-1677, OECD-AIM-2026-02-12-e766, OECD-AIM-2026-06-21-bcb5 | APPROVE (with retitle decision) |
| M6 | INC-14317 -> INC-13066 | GPT-4o Allegedly Reinforced California Man Michael Lines's Delusions Before Suicide Attempt | OpenAI Allegedly Failed to Intervene in ChatGPT Conversations Preceding Montreal Web Developer Alice Carrier's Suicide -> OpenAI Allegedly Failed to Intervene in ChatGPT Conversations Preceding Montreal Web Developer Alice Carrier's Suicide | AIID-1569, AIID-1609, OECD-AIM-2026-07-01-994d, OECD-AIM-2026-07-20-7ddf, OECD-AIM-2026-07-20-8a17 | DO NOT APPROVE |
| M7 | INC-14902 -> INC-00699 | Suno AI Exposed for Scraping Copyrighted Music and User Data Breach | BMG Sues Anthropic Over AI Training With Copyrighted Song Lyrics -> Record Labels Sue AI Music Generators for Copyright Infringement | AIID-1655, AIID-1656, AIID-1657, OECD-AIM-2023-10-18-a6f8, OECD-AIM-2024-06-24-413e, OECD-AIM-2024-08-02-4bed, OECD-AIM-2025-01-04-c501, OECD-AIM-2025-09-22-8350, OECD-AIM-2026-03-24-ed03, OECD-AIM-2026-07-11-995f, OECD-AIM-2026-07-17-9a57, OECD-AIM-2026-07-30-2c05, OECD-AIM-2026-08-05-9a62, OECD-AIM-2026-08-17-8fdd | DO NOT APPROVE |

**Retitles of published IDs**

| # | id | before | after | new title is | absorbs (AIID ids with AIID's own title) | date before -> after | severity before -> after | D42 evidence recommendation |
|---|---|---|---|---|---|---|---|---|
| R1 | INC-01579 | OpenAI Sued After ChatGPT Advice Allegedly Leads to Fatal Overdose | California Teen Reportedly Died of Overdose After Repeatedly Seeking Drug-Use Guidance Allegedly from ChatGPT | AIID title | AIID-1370: California Teen Reportedly Died of Overdose After Repeatedly Seeking D | 2026-05-12 -> 2025-05-31 | unchanged | APPROVE |
| R2 | INC-13321 | DuckDuckGo AI Spreads False Trump Death Story After Reddit Data Poisoning | DuckDuckGo Search Assist Reportedly Falsely Claimed Donald Trump and JD Vance Died of Rabies | AIID title | AIID-1644: DuckDuckGo Search Assist Reportedly Falsely Claimed Donald Trump and J | unchanged | unchanged | APPROVE |
| R3 | INC-14517 | OpenAI GPT-5.6 AI Model Deletes User Files and Databases, Causing Data Loss | OpenAI GPT-5.6 Sol Agent Reportedly Deleted Most Files in AI Startup Founder's Mac Home Directory | AIID title | AIID-1671: OpenAI GPT-5.6 Sol Agent Reportedly Deleted Most Files in AI Startup F; AIID-1672: OpenAI GPT-5.6 Sol Reportedly Deleted Software Engineer's Production D | 2026-07-12 -> 2026-07-10 | Medium -> High | APPROVE |
| R4 | INC-07910 | Google Gemini AI Deletes 28,745 Lines of Code, Causes 33-Minute Outage and Fakes Recovery Reports | Google Gemini 3.5 Coding Agent Reportedly Caused Production Portal Outage and Generated Fabricated Recovery Records | AIID title | AIID-1673: Google Gemini 3.5 Coding Agent Reportedly Caused Production Portal Out | 2026-05-26 -> 2026-05-20 | unchanged | APPROVE |
| R5 | INC-07783 | Lyft Driver Uses AI-Generated Images for Fraudulent Damage Claims in Florida | Lyft Driver in Boca Raton, Florida, Allegedly Used Purported Google Gemini-Generated Image to Support False $75 Damage Fee | AIID title | AIID-1679: Lyft Driver in Boca Raton, Florida, Allegedly Used Purported Google Ge | 2026-05-18 -> 2026-05-16 | unchanged | APPROVE |
| R6 | INC-01514 | NAACP Sues xAI Over Illegal Gas Turbine Use for AI Data Center, Citing Pollution and Health Risks | xAI Data Centers Linked to Unpermitted Pollution in Mississippi and Tennessee | OECD LLM headline | AIID-1677: (no row in AIID extract); +2 OECD row(s) | 2026-04-14 -> 2026-02-12 | High -> Critical | APPROVE if the merge is approved |
| R7 | INC-01994 | US Court Upholds $243 Million Verdict Against Tesla Over Fatal Autopilot Crash | Tesla Faces Trial Over Fatal Autopilot Crash in Florida | OECD LLM headline | AIID-1686: (no row in AIID extract); +5 OECD row(s) | 2026-02-20 -> 2025-06-27 | unchanged | DO NOT APPROVE |
| R8 | INC-00699 | BMG Sues Anthropic Over AI Training With Copyrighted Song Lyrics | Record Labels Sue AI Music Generators for Copyright Infringement | OECD LLM headline | AIID-1655: (no row in AIID extract); AIID-1656: (no row in AIID extract); AIID-1657: Anthropic Allegedly Copied Copyrighted Song Lyrics Without Permission ; +11 OECD row(s) | 2026-03-18 -> 2024-06-24 | High -> Critical | DO NOT APPROVE |
| R9 | INC-00813 | Claude Code Project Files RCE & API Token Exfiltration (CVE-2025-59536 & CVE-2026-21852) | Unknown Actor Reportedly Exploited Cline's Claude-Powered GitHub Issue-Triage Workflow and Published an Unauthorized Cline CLI Package | AIID title | AIID-1680: Unknown Actor Reportedly Exploited Cline's Claude-Powered GitHub Issue | 2026-02-25 -> 2026-02-17 | unchanged | DO NOT APPROVE |
| R10 | INC-03717 | Deepfake Porn Sites Use Breeze Liu's Image Without Consent | Dozens of Dutch Women, Including Politicians and Public Figures, Were Reportedly Targeted With AI-Manipulated Deepfake Pornography | AIID title | AIID-1684: Dozens of Dutch Women, Including Politicians and Public Figures, Were ; +1 OECD row(s) | 2024-04-08 -> 2024-03-19 | unchanged | DO NOT APPROVE |
| R11 | INC-14284 | Anthropic's Claude Code Accused of Covertly Identifying China-Linked Users | Anthropic's Claude Code AI Coding Tool Reportedly Used Hidden Unicode Markers to Classify Custom API Routing | AIID title | AIID-1723: Anthropic's Claude Code AI Coding Tool Reportedly Used Hidden Unicode  | 2026-06-30 -> 2026-04-02 | unchanged | not in the D42 files (new since 2026-10-03) |
| R12 | INC-14407 | Police Misuse of Flock AI License Plate Cameras Sparks Legal and Privacy Concerns | Deputies in Cherokee County, Georgia, Allegedly Misused Automated License Plate Reader Data for Non-Law-Enforcement Purposes | AIID title | AIID-1595: Deputies in Cherokee County, Georgia, Allegedly Misused Automated Lice; AIID-1713: York County, South Carolina, Deputies Reportedly Held Local Motorist a | 2026-07-07 -> 2026-06-12 | unchanged | not in the D42 files (new since 2026-10-03) |

Per-item observations I can add from today's data (not in the D42 file):
- **M2 and R7 share the key AIID-1686.** D42 says approve the merge and reject the retitle; the file records them as separate approvals, but both are produced by the same cross-reference. I did not test whether the gate can keep the merge and refuse the retitle; it can only if a title-pin override (the gate's `curated` exemption) pins `INC-01994` to its present title.
- **M3, M7 and R8 form one hub**: `INC-00699` gains 14 gated source ids (AIID-1655/1656/1657 and 11 OECD rows). R8 also moves its date back 2 years (2026-03-18 to 2024-06-24) and raises severity High to Critical, which a reader of the corpus would see as a different incident.
- **R6 / M5**: the merge and retitle are both "approve if the other is"; D42 and the 2026-10-03 tripwire audit disagreed about M5 (approve vs doubtful).
- **R11 (`INC-14284`) and R12 (`INC-14407`) are new** since D42. R12 absorbs two AIID ids with visibly different incidents ("Cherokee County, Georgia" and "York County, South Carolina") and takes the first's title; I read this as a probable over-merge but it is a title-level reading only. R11 absorbs one AIID id (AIID-1723) whose title is about a different subject from the old title ("covertly identifying China-linked users" vs "hidden Unicode markers to classify custom API routing") and needs a raw read.
- Both `severity` raises (R3, R6, R8) and the `corpus` flip (R1) are listed in 1.3.

**Options.**
- B1 approve all 19 (the D42 17 plus the 2 new retitles): consequence = A4's merge part. 7 tombstones, 12 retitles.
- B2 reject all: consequence = needs the suppression machinery (3.x) to take effect; until then it equals A1.
- B3 partly approve, per item. I suggest the ruling be recorded per item even though no list is operative until engineering exists (so the work is not repeated when it is built).

**Recommendation (suggestion).** B3, following the D42 evidence for the ten items it covers: approve-in-principle M1, M2 (merge only), M5, R1-R5, R6 (conditional on M5); reject M3, M4, M6, M7, R7, R8, R9, R10; **do not rule R11, R12 and the M5 same-incident question without a raw-record read** (a human step; D25(a)(2)). Reasons: M3/M4/M6/M7 are marked lean-no or do-not-approve by D42 and are permanent; R9 and R10 retitle a CVE-keyed row and a deepfake row to unrelated incidents (D42's own words); 5 of the 12 retitles (R1-R5) are AIID's own title for the same story. Caveat: this recommendation inherits the D42 evidence and a title-level reading, nothing more.

### (c) The AIID-only new rows

- C1 hold (A1 behaviour): rows stay out; cost = 113 current incidents missing, growing.
- C2 ship all: **113 rows** if OECD stays held (A2), **61** if OECD is lifted too (52 become "both" rows). IDs `INC-17216..INC-17328` (AIID alone). Row shape: tier `landmark`, `security`, `aiid_id` set on all, description a project template, no `content_license` marker (as for the existing AIID rows). AIID-authored text shipping: the 113 bare titles plus `affected` names. A sample of the AIID-only rows (as they appear under the both-source overlay, 61 rows) follows.
- C3 ship a subset: no natural cut exists (all 113 are one shape); a subset by year (79 are 2026) would just be a time-based hold.
- Risk: E23 situs dependency (above); reversible only by a status/tombstone path (invariant: never delete).
- Recommendation: **C2 under A2.**

61 AIID-only new rows; ids INC-17217..INC-17306; severity {'Medium': 34, 'High': 21, 'Critical': 6}; corpus {'security': 61}; year {2020: 1, 2022: 1, 2023: 5, 2024: 9, 2025: 10, 2026: 35}
sample (first 8): INC-17217 AIID-1586 Threat Actor Reportedly Used AI-Assisted Workflows to Compro; INC-17218 AIID-1588 Purportedly AI-Powered KT Platform Reportedly Used in Forced; INC-17219 AIID-1589 Purportedly AI-Powered 007TG Platform Reportedly Used by Sca; INC-17220 AIID-1592 Purportedly AI-Generated Images Reportedly Used During Four-; INC-17221 AIID-1596 Purported Deepfake Impersonation of Starmangalsutra Director; INC-17222 AIID-1599 Waymo Robotaxi Reportedly Remained Immobilized While Vandals; INC-17223 AIID-1602 Zoox Autonomous Vehicle Reportedly Entered Smoke-Obscured Fi; INC-17225 AIID-1605 Purportedly AI-Generated Image Prompted Emergency Investigat

### (d) The OECD `title` licence position

**Known.**
- AIM's methodology page says event title, summary, harm type, severity, stakeholders and country are "LLM-generated (OpenAI's o3-mini) from the top three articles of each event" (E21 section 2.4, WebFetch 2026-07-30; red-reviewer raw-HTML check of related text 2026-10-13). The same page disclaims third-party copyrights and says AIM use is subject to `www.oecd.org/termsandconditions`.
- OECD general terms (as corroborated by search; the page itself returns 403 to every project tool): Data may be extracted, copied, adapted, distributed "for any purpose, even for commercial use" with attribution; written content published from 2024-07-01 defaults to CC BY 4.0 where OECD owns it. E21 judged the AIM metadata closer to "Data" than to "written content", and "Data" is the more permissive clause.
- E21 resolved `description` conservatively (reduced to a template) and left `title` as "a separate, narrower open question", lower per-item risk (a short label), same posture as AIAAIC's retained headline (E15/D17). Per-entry OECD attribution is on every OECD-sourced row.
- Today **3,937 of 4,104** OECD-id rows ship a title identical to OECD's raw title (re-derived: per-row comparison against the committed raw file; this is the same 3,937 as the register). An unfrozen corpus would be **5,643 of 5,851** (+1,706 net: +1,720 on new rows, less 14 published rows: 5 retired by merges and 9 retitled to an AIID title; 0 published rows gain an OECD title). Of the 1,811 new rows, 1,720 carry an OECD title and 91 carry an AIID title.
- The outreach to `ai@oecd.org` was sent 2026-07-31; the follow-up window (2026-08-21) passed 53 days ago and **no reply is recorded**. The sent message asked about reuse terms for AIM's structured data and a bulk channel. **It did not ask about LLM-generated metadata or titles.**

**Unknown.**
- Whether OECD claims any right in the LLM-generated titles, or considers them "Data" under its general terms. No document I can read says so.
- Whether copyright subsists in a short machine-generated headline in the jurisdictions that matter (US, UK, EU); E21 judged two readings competing and neither frivolous. I am not counsel and offer no legal conclusion.
- Whether an **EU/UK sui generis database right** in AIM (an OECD-operated database, OECD being Paris-based) is engaged by the extraction of titles, dates and IDs. I found no analysis of this for OECD anywhere in `SOURCE_LICENSES` or E21 (the database-right work covers AIAAIC and AIID, where the maker is Canadian/U.S.). This is an open question, not a finding.
- Whether any counsel step (U4 in the register) is still intended.

**What would settle it.** A reply from OECD to a narrower question than the one sent: (1) are AIM's LLM-generated event titles and metadata covered by OECD's general Data-reuse clause, including for redistribution under CC BY 4.0 with OECD attribution; (2) does OECD assert any rights in them; (3) is there a sanctioned bulk channel (repeated from the first message). Draft in section 5; the user sends. A counsel read on the sui generis point would settle the database-level exposure separately.

**Options and consequences.**
- **D1 ship, including growth** (A4 or an OECD lift): +1,720 OECD-title rows; exposure scales by 1,720/3,937 = 43.7% of the existing OECD-title population with the question unanswered. Reversible only by retitling (editable, no tombstone).
- **D2 keep the existing 3,937, add no new OECD rows until OECD answers** (A2): exposure unchanged; staleness grows (1.5); the 7 OECD merges and 4 OECD retitles are not applied; no engineering beyond A2's.
- **D3 project-composed titles for new OECD rows**, e.g. built from `affected` + attack vector + date (no OECD text): removes new exposure; but changes identity and dedupe behaviour (OECD titles feed the merge key), needs a design and a field delta, and produces weak titles for 1,720 rows.
- **D4 also replace the existing 3,937 OECD titles**: retracts a published field on 3,937 rows (title change, no deletion), changes `references[0].title` too, and moves ids' sort/search surface; a large delta for a lower-risk field. Not suggested without counsel input.

**Safe default (suggestion):** D2, because it keeps today's state (which the user has lived with since E21) and expands nothing; it is also exactly what A2 does. The follow-up email is the cheap way to move this off the default.

### (e) How approvals are recorded; what the first post-ruling refresh does

**The file.** `docs/audits/D42-approved-refresh-merges.json` (absent today). Format read by `_load_refresh_merge_approvals`:
- `entries`: list of `{"kind":"merge","from","into"}`, `{"kind":"retitle","id"}`, `{"kind":"add","source_id"}`, `{"kind":"content","id"}`.
- `authorization`: `{"decision":"<D id>","ruled_by":"user","entries_sha256":"<sha256 of json.dumps(entries, sort_keys=True, separators=(',',':'))>"}`.
- A non-empty `entries` with no `ruled_by == "user"` marker, or a hash that does not match, raises and the build aborts ("File presence authorizes nothing"). An empty or missing file approves nothing. `ruled_by` is the D42 field name (the D28 split file uses `decided_by`, which nothing enforces; the memo's dated note of 2026-10-12 sets this out and is not repeated here).
- **Gap:** the hash is not pinned in code, so a deliberate edit that also recomputes `entries_sha256` passes (memo S7/A7; WS4-T21 closed the same gap for D28 by pinning in code). The commit that records a ruling should pin the hash.
- **Two tests assert the committed set is empty** and must change in the same commit: `tests/test_oecd_stage1_freeze.py::test_committed_approval_set_is_empty` and `tests/test_d42_refresh_merge_gate.py::test_committed_approval_list_is_empty_until_the_user_rules`.

**Why the file alone does nothing in the weekly run.** `scripts/hold_pair_inputs.py` restores the pair inputs to HEAD before the merge (`.github/workflows/auto-refresh.yml`, steps "Hold OECD/AIID pair inputs..." and the post-hold guard). An approval file is read only after fresh pair bytes reach the merge, which never happens while that step runs. So the first post-ruling refresh **does exactly what today's does** (opens the PR with AIAAIC/KEV/CVE sweep, uploads the artifact) unless the workflow is changed too.

**What the first refresh does after the engineering in section 3 is done (predicted).**
- It will not publish "the reviewed delta" as measured here. The reviewed delta was measured at 2026-10-13; the OECD sitemap adds about 20 rows/day, so a run after N days carries about 20 x N source rows the approval file does not name, and the gate aborts on them ("add OECD-AIM-..."). Per-source-id `add` approvals therefore cannot be a standing mechanism. Two designs: (i) a **pinned crawl**: commit the reviewed ingest bytes in a ruling PR (S8: filename + sha256 recorded), hold everything newer, and treat each later batch as a new ruling; (ii) a **standing class approval** for additions that match a stated shape (e.g. AIID-only rows from the sanctioned snapshot per E23; OECD rows only after (d) is answered), pinned in code like the D28 hash. Under A2 the AIID class is the natural first one.
- Retitles/merges that are rejected must be unreachable (suppression or heuristic change) or the run aborts every week.

---

## 3. What each choice leaves for engineering

(Sizes are my estimates, not measured; none is started.)

| Choice | Engineering left |
|---|---|
| A1 keep | None. Optional: a monthly auto-regenerated hold report (the artifact expires in 30 days). |
| A2 AIID only | (1) Split the hold: `hold_pair_inputs.py` and `_PAIR_INPUT_FILES` treat the pair as one; the AIID files (`aiid_full.json`, its provenance sidecar) must stop being held while OECD, AIRI, `aiid_incidents.json` and `aiid_oecd_relationships.json` stay held. (2) Narrow or class-approve the gate for AIID: 113 adds, 25 title edits and 169 content changes in this snapshot are 307 entries, but the next snapshot differs, so a standing AIID class is needed (pinned in code). Mixed rows (39 of the 169) carry OECD ids and are gated by prefix, so the gate must distinguish which input drove the change (it currently only asks whether any pair input differs). (3) Update `test_committed_approval_*`, the stage-1 freeze tests, the hold-guard tests. (4) Re-run E23 counts and the exclusion tripwire; docs (S6): `SOURCE_LICENSES` 1.2a counts, `NOTICE-DATA`, the "AIID-only rows" operational-status row, README/stats counts. (5) The corpus-pinned tests will fail on a row-count change; I grepped only for the literals 15637/15666/4104/3937 (found in `tests/test_latest_release_drift.py` only) and did not enumerate others. |
| A3 suppression | The S7 design (memo): hash-pinned suppression list or a heuristic change so one OECD row's AIID cross-references cannot bridge two published entries; interacts with the WS4-T19 split guard (section 2.a, A3). Tests: tamper-plus-recompute fires, a suppressed bridge stays separate, an unapproved unsuppressed change still aborts. Also the S8 pinned-crawl delta and S9 licence assertions (b9). Largest item. |
| A4 lift all | Workflow change (stop holding), a 2,169-entry approval file or bulk kinds, pinned hash, test updates, S8/S9, counts and docs (S6). Plus the consequences in (b). |
| (b) per-item rulings | The rulings themselves need a record file (a dated ruling record, then the approval file above). Rejections need A3's machinery to take effect. A title-pin override can hold a retitle (the gate exempts a curation override that sets exactly that title) and is data, not code, but it is a hand-curated data edit per row and needs its own delta. |
| (c) AIID-only rows | With A2: nothing beyond A2. |
| (d) D2 | None. D3: design + delta (OECD titles feed identity). D4: a data migration with its own field delta. |
| (e) recording | Pin the hash in code; add bulk or class approval kinds; change the two empty-set tests; document the pinned-crawl procedure; consider extending artifact retention. |

---

## 4. Open facts I could not establish, and how to establish them

1. **Same-incident status of any merge or retitle.** Needs the raw OECD pages and AIID records (D25(a)(2)). How: a human (or a labelled agent read) of each row named in the tables, starting with M5, R11, R12.
2. **Whether the gate can approve M2 and refuse R7 (same AIID-1686 key).** How: a scratch run with a title-pin curation override for `INC-01994`.
3. **Whether OECD replied / OECD's position on LLM-generated titles.** How: the user's inbox for `ai@oecd.org` since 2026-07-31; send the section 5 draft.
4. **EU/UK sui generis right in AIM.** No analysis exists. How: a counsel read, or a license-auditor memo extending the E13 method to OECD (maker, nexus, "substantial part" of extractions); the first needs the user.
5. **E23 recount after any AIID lift** (marker-absence under the four-signal union; the 63-row `aiid_incidents.json` and AIRI exclusion). How: license-auditor re-runs E23's measurement on the AIID-only scratch output (the scratch clone is gone; the recipe in section 6 rebuilds it).
6. **Which corpus-pinned tests break on a row-count change.** How: run the full suite on the ungated scratch output (not done here; the suite takes several minutes and needs the data tree committed).
7. **Whether downstream exports change beyond `incidents.json`** (min.json, STIX, MISP, HF, TAXII, docs pages). How: run `make build` on the ungated output; I ran only `merge` (the scratch builds also wrote `incidents.min.json`).
8. **Why `entries_security_relevant` rose by 112 while 113 rows were added** (AIID-only overlay). Small; how: diff the AIID extract's security-relevant set against the rows added.
9. **Rate of upstream change beyond one day.** I have two OECD crawls 11 hours apart (20 new, 2 vanished ids); the 2 vanished ids are not examined. How: compare the next weekly artifact against this one.
10. **Whether the open PR #102 (weekly data refresh) carries anything pair-driven.** It is outside this package; the D66 hold says no. How: `gh pr diff 102 --name-only` against the pair paths.

---

## 5. Draft follow-up to OECD (for the user to send; not sent; the first message stays as sent)

> **To:** ai@oecd.org (as in the first message; still unconfirmed as the right desk)
> **Subject:** Follow-up: AI Incidents and Hazards Monitor (AIM), reuse of LLM-generated event titles
>
> Hello OECD.AI / AIM team,
>
> I wrote on 2026-07-31 about reuse terms for AIM's structured data and about a bulk channel. I have not seen a reply and am following up with a narrower question that I did not ask the first time.
>
> The AIM methodology page says each event's title, summary and other metadata are LLM-generated from the top three news articles. Our index (genai_incidents, published under CC BY 4.0, each upstream's terms carried through) reuses, with an OECD attribution on every entry, AIM's incident identifier, date, taxonomy tags, a link to the AIM page and the event title. We do not reuse the summary or the article text.
>
> 1. Do you consider the LLM-generated event titles and metadata to fall under OECD's general Data-reuse terms (extract, copy, adapt, distribute for any purpose, with attribution), and may we redistribute them under CC BY 4.0 while crediting OECD in the format your terms ask for?
> 2. Does OECD assert any copyright or database right in those titles or in the AIM database as a whole that we should account for?
> 3. If there is a bulk export or API you would prefer indexes like ours to use instead of reading incident pages one by one, we would use it.
>
> We are holding further additions from AIM until we hear from you, so a reply either way helps us decide.
>
> Thank you,
> [Maintainer name]

---

## 6. Verification recipe (reproduce every count)

```
# 1. pin the inputs (artifacts expire 2026-11-12)
gh run download 38366793761 -n held-oecd-aiid-inputs -D <scratch>/artA
gh run download 38330687613 -n held-oecd-aiid-inputs -D <scratch>/artB
sha256sum <scratch>/artA/*.json     # compare with section 0
# 2. control
git clone <repo> <scratch>/ctl && (cd <scratch>/ctl && git checkout 9c646d36)
cd <scratch>/ctl && python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
git -C <scratch>/ctl status --porcelain       # expect: data/incidents.json and id_deprecations.json NOT listed (byte-identical)
# 3. gated build (the 2,066 list)
git clone <repo> <scratch>/fA && cp <scratch>/artA/{aiid_full.json,aiid_full.provenance.json,oecd_aim_full_incidents.json} <scratch>/fA/ingest/
sed -i 's/problems\[:25\]/problems/' <scratch>/fA/scripts/merge_and_dedupe.py     # scratch copy only
(cd <scratch>/fA && python scripts/parse_existing.py && python scripts/merge_and_dedupe.py)   # expect exit 1, "(2066)"
# 4. ungated: replace the line `    _run_refresh_gate(deduped, fresh, curation)` by `    pass` in the scratch copy, rebuild, then compare
#    data/incidents.json and id_deprecations.json per entity (id -> dict) against the control's.
#    Expected: 15666 -> 17470 rows; 1811 added (INC-17216..INC-19026); 7 removed; 190 changed; 7 new deprecations (1084 -> 1091).
# 5. variants: overlay only oecd_aim_full_incidents.json  -> expect 17409 rows, 7 merges, 4 retitles
#              overlay only aiid_full.json + its provenance -> expect 15779 rows, 0 merges, 113 added, 169 changed, 25 title edits
```

Fire proof: the control (committed inputs) builds clean and byte-identical, while the same build with fresh inputs aborts at the gate; the gate's class counts match the per-entity comparison class by class. The OECD-only and AIID-only overlays give different counts, so the counts are not invariant to the overlay (agreement 6, form d).
