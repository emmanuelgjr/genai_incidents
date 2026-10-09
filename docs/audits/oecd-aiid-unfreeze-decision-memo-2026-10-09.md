# OECD/AIID refresh unfreeze: decision memo (v2.13.0 item 7), 2026-10-09

**Status: agent-suggested. Dated decision record. Do not regenerate.** Nothing in
this memo is approved, ruled or human-reviewed. Author: license-auditor (WS0), no
shell. Base: `main` @ `07f22c09`. The unfreeze itself is a governance decision
reserved to the user (protocol step 8). This memo does not unfreeze anything and
edits no `data/*.json`, ingest code or `SOURCE_LICENSES`.

**Retrieval method, stated per the standing rule.** Every figure below was read from
the committed tree with Grep (line-count mode over pretty-printed JSON, one field per
line) or by reading files; nothing was run. Counts marked **[G]** are Grep counts and
carry that caveat; each has a shell command for red-reviewer in section 8. Absence
findings (no `D25` in the workflow, no OECD reply on the board) are local-file greps
only, not web reads, and are listed in section 8 for shell confirmation. Board text
is testimony; where it disagrees with the tree, the tree is reported.

---

## 0. Bottom line

1. WS4-T12 and WS4-T14 **were built**. They are on `ws4/refresh-tripwire-42` @
   `586f40c8` (in `.git/packed-refs`, local and `origin`), **not on `main`**.
   The board's own PROGRESS.md:277 still lists "the refresh branch (WS4-T12/T14)
   gate and merge" as open; no gate verdict exists for it.
2. The "7 merges" are not 7 reviewed items. The D42 evidence file
   (`docs/audits/D42-refresh-merge-review-2026-10-03.md` on that branch) lists **17
   changes (7 merges + 10 retitles)**, and the built gate aborts the build on
   **any** unapproved one. **A partial approval list therefore publishes nothing.**
   Approving only the sound ones is not an available option on the branch as built.
3. Recommendation (section 7): **staged option C.** Merge the machinery now with an
   empty approval set (this makes the freeze deliberate instead of accidental),
   decline the data unfreeze, and open one new task for the merge-heuristic /
   suppression design that a partial approval needs before any refresh PR can open.

---

## 1. What D25(a) is, what it blocked, and how it is enforced

**Text of the ruling** (as quoted in
`docs/audits/E21-tripwire-refresh-2026-09-14.md:874-878`, D25 of 2026-09-15): "No
OECD AIM refresh PR merges until BOTH (1) the `normalize_url` query-string over-merge
fix lands AND (2) every new `"merged"` deprecation a refresh would write has been
reviewed and confirmed to be the same incident." D42 (PROGRESS.md:334-337, 2026-10-03)
kept it in force and added: "The 7 merges come back to the user as a reviewed list
(D28 pattern) before any refresh merges."

**Condition status.**
- (1) met: WS4-T10's fix merged; D28 (PROGRESS.md:875, 2026-09-20) unfroze the corpus
  after the 301-row unmerge. The corpus has moved since (15,637 + 29 retracted,
  `data/incidents.json:6-7` [G]).
- (2) **not met.** The tripwire diagnosis found no board entry recording it satisfied
  (`refresh-tripwire-2026-10-03.md:266-272`).

**How it is enforced: by accident, not by design.** `grep -n 'D25'
.github/workflows/auto-refresh.yml` returns nothing [G, absence, local file]. The
workflow has no freeze step. What stops a refresh PR is that the `Unit tests` step
(`auto-refresh.yml:260-261`) runs the E21 tripwire
`tests/test_e21_partA_inc00437_provenance.py:143`
`test_oecd_aiid_content_disagreement_is_unique_to_inc00437`, which fails, so the
`Open / update refresh PR` step (`auto-refresh.yml:272`) is never reached. So the
premise that D25(a) is "enforced in auto-refresh.yml" is wrong: it is enforced by an
unrelated test that happens to fail. This is the same "accidental barrier, no
deliberate one" shape the board recorded at PROGRESS.md:1513.

**What it blocked (from the diagnosis, `refresh-tripwire-2026-10-03.md:38-54`).**

| run | date | tripwire rows | PR opened |
|---|---|---|---|
| 34858279213 | 2026-09-14 | 29 | no |
| 35501009911 | 2026-09-20 | 30 | no |
| 36310267841 | 2026-09-27 | 42 | no |

The diagnosis states all six runs listed (back to 2026-08-30) concluded `failure`.
**Dated note (2026-10-09, per gate bounce #1):** auto-refresh run 37195068024
(2026-10-04) failed on the same tripwire test with 42 rows, same as 09-27; its AIRI 404
is in a continue-on-error step. Runs after 10-04 are not in any file I can read
(command in section 8). Last successful refresh with data: committed OECD
ingest still holds the OECD rows crawled before the freeze (4,160 `OECD-AIM-` id
occurrences in `data/incidents.json` [G], in 4,104 rows); the AIRI download has been dead since
2026-05-31 (N8, unrelated to D25).

**Rows held back (as measured 2026-10-03, against the then 13,361-row corpus).**
Rebuild with the refreshed OECD crawl: 13,361 -> 14,887 (**+1,533 new-only IDs**, 7
gone, 20 common rows changed, 7 new `merged` deprecations, 4 retitles of published
IDs, 11 `aiid_id` gains, 4 upward severity changes; `refresh-tripwire:222-233`).
**These are not current.** They predate wave 1-2 (+2,305 rows) and the rejected-CVE
retraction, and the live OECD sitemap moves weekly (the diagnosis itself says the
exception set "should only grow", `:374`). The first unfrozen run on today's `main`
has not been measured. See spec requirement S1.

---

## 2. E23, E21 and the title-only exposure: what ships today

**What the rulings say.**
- E23 (`E23-aiid-marking-ruling-2026-07-30.md`, "Outcome"): no row-level marker is
  required for the ~1,463 AIID rows that ship, because the only AIID-authored text
  kept is a bare title. Layer 1: U.S. Circular 33 excludes titles and short phrases,
  the connecting factor being AIID's U.S. situs. Layer 2: a U.S.-situated maker fails
  the UK and EU database-right qualification tests. **Both must hold.** The ruling
  says it does **not** clear `ingest/aiid_incidents.json` (63 rows) or the 1,457 AIRI
  rows sharing the `AIID-<n>` convention: those are kept out only by merge order, with
  a tripwire (E23 section 5) that reopens review if their text ever ships. The ruling
  also records that AIID titles are not demonstrably less editorial than AIAAIC's
  (median 13 words, 925/1,548 hedged), so Layer 1 rests on situs alone.
- E21 (`E21-oecd-narrative-licence-2026-07-30.md` section 4, outcome B): OECD
  `title`/`summary` are "LLM-generated (OpenAI's o3-mini) from the top three articles";
  OECD's methodology page says it "cannot and do not grant any rights" over the
  protected materials. `description` was reduced to a template. **`title` was left
  open** (section 5.1: "tracked as a parallel open question, same posture as
  E15/D17").
- `NOTICE-DATA:249-255` repeats that: the OECD title "still ships the same
  LLM-generated text verbatim" and is "a separate, open question".

**What ships today** (`data/incidents.json` @ main, [G] counts):

| Thing | Count | Basis |
|---|---|---|
| rows with `aiid_id` | 1,471 | `"aiid_id": <n>` lines |
| of which `description` starts "AI Incident Database (AIID) entry #" (project template over AIID title) | 1,468 | 3 `aiid_id` rows are non-template: 898, 1574, 1575 |
| rows whose `description` starts "Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as" (project template, no OECD narrative) | 3,937 | |
| rows carrying `description_source: "oecd-aim"` | 1 (INC-00437) | the other 3,936 are unlabelled, which is what T12 labels |
| OECD attribution references `"OECD (20yy), AI Incidents and Hazards Monitor` | 4,755 | matches `SOURCE_LICENSES` 1.5 "4,755 citation-shaped references" |
| `OECD-AIM-` source-id occurrences (lines) | 4,160 | occurrences, not rows: 4,104 rows carry at least one (27 carry more than one) |

So today the corpus ships, from OECD: a project-written template sentence, a link,
an attribution string, structural facts, **and OECD's LLM-generated headline as
`title`**. From AIID: a project template over the **AIID-authored title verbatim**,
plus ids and structured facts. No OECD or AIID narrative ships. The INC-00437 row
(`data/incidents.json:1003835-1003844`) is the worked example: `AIID-1574` source id,
OECD title, OECD template description.

Two published-claim figures will be wrong after an unfreeze and are live surfaces:
`NOTICE-DATA:249-251` ("3,667 of 3,829 OECD-AIM-sourced rows") is already stale
against the figures above (like-for-like replacement: 3,937 of 4,104), and `SOURCE_LICENSES` 1.2a / `NOTICE-DATA:195-198`
("0 of 1,466", "1,463-1,464 of 1,465", "the two exceptions") are measurements the
refresh changes (section 4, R3).

---

## 3. What the first unfrozen run would change

Source: the branch's own evidence, not re-run by me. Branch `ws4/refresh-tripwire-42`
@ `586f40c8`, merge-base `a7343274` (2026-10-03; 106 commits behind main @ `07f22c09` (the memo's base), 3 ahead); fork point `9604752f`. Files: `docs/audits/refresh-tripwire-2026-10-03.md`,
`D42-refresh-merge-review-2026-10-03.md`, `D42-proposed-refresh-merges.json`,
`D42-t12-t14-implementation-2026-10-03.md`.

**What the branch contains** (implementation record, "What changed"):
`scripts/ingest_oecd_aim.py:986` stamps `description_provenance` on new OECD rows
(WS4-T12); `merge_and_dedupe.py:997-1012` backfills the label on retained
`OECD-AIM-*` rows without an `updated` bump; `:1158` guards the INC-00437 override
(step-4d hazard); `.github/workflows/auto-refresh.yml:58-60` adds
`Refresh AIID snapshot (sanctioned bulk channel)` (WS4-T14, `continue-on-error`);
`merge_and_dedupe.py:1752-1831` and `:2531` add `_check_refresh_merge_authorization`
reading `docs/audits/D42-approved-refresh-merges.json`; `tests/test_aiid_signal_provenance.py`
replaces the exact-list tripwire.

**Stage 1 effect (labels only).** Measured on the old 13,361 corpus: 13,361 -> 13,361,
ID set identical, changed fields `description_provenance` 3,936 and `description_source`
3,936, nothing else; labelled-but-not-template 0, template-but-unlabelled 0; only
`data/incidents.json` drifts (7,874 inserted lines). On today's `main` the expected
count is 3,936 (3,937 template rows minus INC-00437 [G]) but is unmeasured.
**The branch is red on `validate.yml`'s drift check until that rebuild is committed**
(implementation record, Measurements).

**Stage 2 effect (the data unfreeze), 2026-10-03 figures on the 13,361 corpus:**
- Rows: +1,533 new-only IDs; the AIID snapshot step also pulls `backup-20260928101247`
  (1,642 incidents written vs 1,548 titles in E23's measurement, so roughly +94 AIID
  rows by subtraction, **unmeasured**).
- 17 gated changes (7 merges + 10 retitles) with the fresh snapshot; 11 with OECD
  alone (7 merges + 4 retitles). 24 further upstream AIID title edits are not gated
  (review file section C).
- **Permanently irreversible part: the 7 `merged` records.** `data/id_deprecations.json`
  is append-only (invariant 9). All seven retired IDs are live published entries today
  (`"id": "INC-02381"`, `-14310`, `-01469`, `-08148`, `-13241`, `-14317`, `-14902`
  each present in `data/incidents.json` [G]). Retitles, `aiid_id` gains and severity
  changes are editable later; deprecations are not.
- Mechanism (review file, "Mechanism common to every item"): none of the 7 pairs
  shares a reference URL. An AIID id on an OECD row's `extra_source_ids` acts as a
  dedup key; two OECD rows cite several AIID ids (`...-7ddf` cites 1535, 1569, 1609).
  Cross-references become merge keys while the AIID snapshot is stale. T10 did not
  fix this mechanism, and **a fresh snapshot shrinks the class but does not remove it**
  (`refresh-tripwire:150-153`).

**The 7 merges, with my read.** My read is from the current published titles above
(read from `data/incidents.json` this session) plus the board's cited evidence; I did
not open the raw OECD/AIID records. It is a licence-and-sanity read, not the D25(a)(2)
same-incident review, which a human does.

| # | retired -> into | Published titles today | D42 review | tripwire audit | My read |
|---|---|---|---|---|---|
| 1 | INC-02381 -> INC-01579 | AIID-1370 "California Teen Reportedly Died of Overdose..." -> "OpenAI Sued After ChatGPT Advice Allegedly Leads to Fatal Overdose" | approve | probably same | Plausible same death. Note it retires an **AIID-keyed** row into an OECD-keyed one and retitles the survivor to AIID's title (covered by E23). |
| 2 | INC-14310 -> INC-01994 | "Tesla Autopilot Failure and Data Suppression..." -> "US Court Upholds $243 Million Verdict Against Tesla..." | approve merge, decline retitle | probably same case | Plausible same case. Cannot be taken without the retitle: see section 5 gate point. |
| 3 | INC-01469 -> INC-00699 | "Music Publishers Sue Anthropic..." -> "BMG Sues Anthropic..." | unsure, lean no | related suits | Two different filers on title alone. Lean no. |
| 4 | INC-08148 -> INC-01628 | "AI Chatbots Falsely Pose as Licensed Doctors in Pennsylvania" -> AIID-1108 "Digital Rights Groups Accuse Meta and Character.AI..." | unsure, lean no | doubtful | Different event on title. Lean no. |
| 5 | INC-13241 -> INC-01514 | "AI-Powered Data Centers Linked to Pollution and Military Operations Spark Legal Battle" -> "NAACP Sues xAI Over Illegal Gas Turbine Use..." | **approve** | **doubtful** | **The two board records disagree.** The title alone does not name xAI. The D42 file read raw records and is later, but I cannot confirm. Needs a human look at the raw OECD row. |
| 6 | INC-14317 -> INC-13066 | "GPT-4o Allegedly Reinforced California Man Michael Lines's Delusions..." -> "...Montreal Web Developer Alice Carrier's Suicide" | do not approve | no | Different people. No. |
| 7 | INC-14902 -> INC-00699 | "Suno AI Exposed for Scraping Copyrighted Music and User Data Breach" -> "BMG Sues Anthropic..." | do not approve | no | Different subject. No. |

Reading across the table: of 7, the evidence supports at most 2 clear (1, 2) and 1
contested (5). Four (3, 4, 6, 7) are doubtful or wrong: 2 lean-no (3, 4) and 2
do-not-approve (6, 7). **A fully approved list would
therefore write at least 4 permanent deprecations that the board's own evidence marks
lean-no (3, 4) or do-not-approve (6, 7).** The 10 retitles split, per the D42 files: 5 approve (`INC-01579`, `-13321`, `-14517`,
`-07910`, `-07783`; each takes AIID's own title, which E23 covers), 1 conditional on
merge 5 (`INC-01514`, an OECD headline), and 4 "do not approve" (`INC-01994`,
`INC-00699`, `INC-00813`, `INC-03717`; the last two are retitles with no deprecation,
which a deprecation-only gate would miss, review file section B).

---

## 4. Residual licence risk if the refresh runs

Ratings are mine and agent-suggested; none resolves an ambiguity in the project's
favour.

| # | Risk | Size | Status |
|---|---|---|---|
| R1 | **OECD `title` exposure grows.** Titles are LLM output from third-party news (E21 section 2.4), the OECD non-grant clause applies, and the question is open. Today 3,937 rows ship a title exactly equal to a raw OECD title (the same set as the OECD-template descriptions), out of 4,104 rows carrying at least one `OECD-AIM-` id (4,160 is the id occurrences, 27 rows carry more than one; 4,104 foreman-confirmed). The first run adds up to ~+1,533 rows: 1533/4104 = 37.4% of OECD-id rows, 1533/3937 = 38.9% of the title-exposure base. It retitles 4 published IDs, 3 to OECD-origin headlines (`INC-01514`, `INC-01994`, `INC-00699`) and 1 to an AIID title (`INC-01579` = AIID-1370's title; tripwire audit table `:236-242`, D42 review section B). Commands in section 8 (row-count block). The refresh did not create the question, but it scales it by a measurable factor and ships it on new stable IDs. | Medium, scaling | **Open, not resolved by any file I read.** UNKNOWN pending the OECD reply (R6). |
| R2 | **Description narrative leaks back.** Today's controls: `build_description()` only (`SOURCE_LICENSES` 1.5). The new branch test explains every `aiid_id` row by exact derivation and the 42/42 reconstruction passed; it covers `aiid_id` rows and the `title`, **not every OECD row** (`D42-t12-t14:83-97`, "Known limits"). New OECD rows with no `aiid_id` are covered only by the earlier E21 gate tests, which I did not re-read. | Low if the full-corpus reconstruction is added (S5) | Spec S5 |
| R3 | **Published numbers go stale.** `SOURCE_LICENSES` 1.2a and `NOTICE-DATA:195-198` state "0 of 1,466", "1,463-1,464 of 1,465", "the two exceptions ship no AIID text". The tripwire diagnosis notes the refresh turns "two" into 42-43 (`refresh-tripwire:211-216`), though those rows ship OECD template text, not AIID text, so no AIID attribution is owed; the claim, not the compliance, breaks. `NOTICE-DATA:249-251` is already wrong (3,667/3,829 vs 3,937/4,104). | Misstatement risk | Live surfaces: correct in place after the data lands (S6) |
| R4 | **AIID shipped population grows** by roughly the new snapshot rows (~+94 by subtraction, plus 6 retitles to AIID titles). E23's ruling is shape-based (bare title, U.S. situs) so it extends in kind, but its counts (1,463) and its "0 marker" measurement must be re-run, and its reopen tripwire must be re-checked: the AIRI/`aiid_incidents.json` population must still not reach `data/incidents.json`. | Low in kind | S5, S6 |
| R5 | **E23 Layer-1 uncertainty is unchanged and unaffected.** It rests on E13's uncertified situs method; the E23 ruling says so itself. An unfreeze enlarges the dependency by ~100 rows, not its character. | Low | none |
| R6 | **OECD terms question is still unanswered on this record.** Outreach to `ai@oecd.org` was sent 2026-07-31; follow-up window 2026-08-21 (`docs/outreach/README.md:21`); no follow-up send recorded and no reply found (local grep of PROGRESS.md, outreach README, oecd-aim-terms.md, which shows absence only on this tree). Primary terms pages still 403 to every tool. Ask the user. | UNKNOWN | Open question to user |
| R7 | **Sitemap redirect / robots gap**: the sitemap URL 302s to `incidents-server.oecdai.org`, whose robots.txt the shared limiter never checks (`SOURCE_LICENSES:140`, a 2026-07-30 WebFetch observation). **Dated note (2026-10-09):** on 2026-10-09 a foreman curl HEAD returned 405 and GET -L returned 200 with no redirect, so the 302 is not reproduced today; treat R7 as unconfirmed as of 2026-10-09. Individual incident pages do not redirect (7/7, 2026-07-30). One fetch per run; unchanged by the unfreeze, but a resumed weekly crawl resumes it. | Low | Check in section 8 |
| R8 | **Label wording.** T12's `description_provenance: original` / `description_source: oecd-aim` is a provenance label, not a content-licence marker. `NOTICE-DATA:256-258` says no marker "is emitted for OECD-derived rows today; whether one is warranted is a separate, not-yet-scoped question". Shipping the label must not be described as that marker. | Low | S6 wording |

**Not a licence risk of the unfreeze, but a trap:** the board's D42 line treats the
decision as "review 7 merges". The legal exposure is mainly R1 (titles on ~1,500 new
rows). The merges are an integrity risk (wrong permanent redirects), not a licence one.

---

## 5. Options

**A. Merge the full unfreeze.** Rebase the branch on `main`, rebuild, approve a list,
run the refresh. Consequence: the gate is all-or-nothing
(`D42-refresh-merge-review:43-46`: "approving nothing for it keeps the build failing
closed... The gate cannot 'reject and continue' by itself"). To publish, **every one
of the 17 changes must be approved**, including 2 do-not-approve merges (6, 7), 2
lean-no merges (3, 4), 1 contested merge (5), and 4 retitles the evidence marks
do-not-approve, plus 1 retitle (`INC-01514`) that is conditional on merge 5. Not recommended. Alternatively approve only the good ones,
in which case nothing publishes.

**B. Decline: leave the branch unmerged, keep D25(a) as is.** Consequences, all
measured above: the weekly refresh stays red at the old tripwire; the tripwire's
fixed expected list (2 rows) is exceeded by 29 (09-14), 30 (09-20), 42 (09-27) and 42 (10-04, run 37195068024); growth has stalled at 42 for the two most recent runs, but the count has not fallen; T12 labels never
ship (3,936 rows unlabelled); the AIID snapshot stays at max id 1581 against 1714
upstream; and the barrier remains accidental. Cheapest, but it keeps the "no
deliberate guard" state and the work already built idle.

**C. Conditional / staged (recommended).**
- **Stage 1, now:** merge the machinery with an **empty approval set** and commit the
  label-only rebuild. D25(a) becomes a deliberate mechanism: the D42 gate refuses any
  OECD/AIID-driven merge or retitle of a published ID until the user writes the
  approval file, and a test asserts the committed set is empty. No refresh rows enter,
  no deprecation is written, no title changes. Stage 1 is the only part within existing
  authorisation (D25(c) approved T12/T14; D42 said "Build WS4-T12 and WS4-T14").
- **Stage 2, only after a user ruling:** the actual data unfreeze. It needs one thing
  the branch does not have: a way to refuse a specific cross-reference bridge (spec S7),
  so declined items do not abort every run. It also needs the user's decision on R1
  (OECD titles at ~+1,500 rows), and an answer on R6 if one exists.

**Recommendation: C, and decline A.** Reasons: (i) it converts an accidental barrier
into a deliberate one without moving any title or deprecation; (ii) it does not ship
anything the evidence calls wrong; (iii) it keeps the two decisions the user has
reserved (D25(b)-style list approval, OECD-title posture) with the user; (iv) stage 1
is the smallest delta that makes the next weekly run mean something. Counterweight,
stated plainly: stage 1 does not make the weekly refresh green; it will fail closed at
the gate each week until stage 2, with no new OECD content, so the OECD corpus stays
at its July state. That is the cost of C, and it is the same cost the user already
accepted under D42.

---

## 6. What decisions this memo asks the user to make

1. A, B or C.
2. If C: authorise commit of the label-only rebuild on `main` (the branch's drift
   check fails until it is committed).
3. For any later stage 2: ruling on R1 (OECD titles) and on each of the 17 items (the
   D42 files carry my read and the engineer's).
4. Whether the OECD terms outreach (sent 2026-07-31) got a reply.

I send no email and draft none here: the outreach exists, and a follow-up would be the
user's to send (`SOURCE_LICENSES` 1.5, Follow-up date).

---

## 7. Spec for the unfreeze branch (for pipeline-engineer, gated by red-reviewer)

Binding on whichever option is chosen; S1-S6 are stage 1, S7-S9 are stage 2.
The branch must be rebuilt on `main` @ `07f22c09` (or later); the old base
`a7343274` (merge-base; fork point `9604752f`) predates wave 1-2, rejected-CVE retraction and the schema change, and
`data/incidents.json` will conflict.

**Stage 1 (machinery + label-only data)**

- **S1. Re-measure everything on current `main`, do not copy the board's numbers.**
  Publish the field-level delta against `git show main:data/incidents.json` and
  `main:data/id_deprecations.json`: row count (expected 15,637 + 29 retracted, unchanged),
  ID set identical, `id_deprecations.json` byte-identical (0 new records), per-field
  changed-row counts for **every** field. Expected and only expected: `description_provenance`
  and `description_source` on exactly the OECD-template rows not already labelled
  (3,936 expected, to be re-derived; this is OECD rows only: 3,728 rows on main already carry `description_provenance` (foreman-measured, Counter over `(description_provenance, description_source)`: verbatim/cvelistv5 2,046; original/aiaaic 1,422; original/None 134; verbatim/cve-cna-via-avid 125; original/oecd-aim 1, INC-00437), so the per-field count must be reported by source, not as one total). `updated`, `title`, `severity`, `aiid_id`, `tags`,
  `references`, `corpus` and all other fields: 0. Any other moved field is a defect
  (agreement 2).
- **S2. Per-row label check, both directions** (agreement 6 form d): every row labelled
  `oecd-aim` has a description equal to `build_description()` rebuilt from its raw
  row, and every row whose description is the OECD template is labelled. Prove it
  fires: unlabel one row, relabel an AIID-template row, restore, show both fail.
- **S3. Derived artifacts declared.** State, per artifact, whether the new fields reach
  it: `incidents.min.json`, `docs/data/*` slim files, HF export, STIX bundle, MISP,
  TAXII collection, `INCIDENTS.md`, `docs/incidents/*.md`, `stats.json`. The prior
  branch said only `incidents.json` drifts; re-verify. No `version`, `incident_count`
  or `generated` change is made by this task; if the rebuild stamps `generated`, say
  so as a declared delta.
- **S4. Ingest files unchanged.** `ingest/aiid_full.json`, `ingest/aiid_full.provenance.json`,
  `ingest/oecd_aim_full_incidents.json` byte-identical to `main`. The snapshot step is
  wired but its output is not committed in stage 1.
- **S5. The deliberate guard.** `D42-approved-refresh-merges.json` absent or an empty
  list with a test asserting the committed set is empty; the gate, run against a fresh
  OECD crawl plus fresh snapshot, aborts with "Nothing was written" and a data tree
  unchanged (the engineer's 11/17 reproduction; cite the new counts); against committed
  inputs it does not abort. Add: a **full-corpus** assertion (not only `aiid_id` rows)
  that every `OECD-AIM-`-sourced row's description equals the rebuilt template and
  carries the attribution reference; 100% of OECD rows carry
  `OECD (<year>), AI Incidents and Hazards Monitor, <url> (accessed on <date>)`.
  Name the failing input for each check and show it fire. Weekly workflow: the test
  asserting step presence, `continue-on-error`, and ordering before merge
  (`auto-refresh.yml:58-60` on the branch).
- **S6. Docs (WS0 does these after the data lands; live surfaces corrected in place).**
  `SOURCE_LICENSES` 1.5 and 1.2a counts, `NOTICE-DATA:195-198` and `:249-251`,
  `.reuse/dep5` AIID lines, CHANGELOG. Wording must say the T12 label is a provenance
  label, not a licence marker (R8). Correct the stale `3,667/3,829` figure with a
  re-derived number.

**Stage 2 (data unfreeze; only after user rulings)**

- **S7. Design requirement the branch lacks.** A hash-pinned *suppression* list, keyed
  on `(OECD source_id, aiid_id)`, authorised in the same marker form as the approval
  file (decision id, `ruled_by: "user"`, `entries_sha256` pinned **in code**, as
  WS4-T21 did for D28), so a declined bridge is not merged and not retitled, and the
  run proceeds. A durable alternative is changing the heuristic so one OECD row's AIID
  cross-reference cannot bridge two already-published entries
  (`D42-review:43-46`; `refresh-tripwire:300-305`). That is a design choice for
  pipeline-engineer and the user; this memo specifies the capability, not the
  mechanism. Required tests: tamper-plus-recompute fires; a suppressed bridge stays
  separate; an unapproved, unsuppressed change still aborts.
- **S8. The delta, on `main`, from a pinned crawl.** The crawl output, snapshot
  filename + sha256 (`ingest/aiid_full.provenance.json`) and `OECD_AIM_LIMIT` are
  recorded so the delta is reproducible. Report: rows added split by source
  (OECD-only, AIID-only, mixed), rows retitled (each with before/after and the source
  of the new title), rows merged (the full list with raw-record read), `aiid_id`
  gained, severity changes, every changed field across all rows, deprecation records
  appended (exactly the approved merges, no others), 0 deletions, ID set only grows.
  The 7+10 board items must be re-derived on current `main`, not carried; items the
  board lists but the run does not reproduce are reported, as are new ones.
- **S9. Licence assertions in the gate.**
  (a) 0 rows ship OECD narrative (exact reconstruction, all OECD rows).
  (b) AIID-authored text only as `title` and only from `ingest/aiid_full.json`;
  `description` is the project template; the 63 `aiid_incidents.json` rows and AIRI
  rows still do not reach `data/incidents.json` (E23 tripwire; per-row, not aggregate).
  (c) `content_license` marker absence on AIID rows recounted under E23's four-signal
  union and published as the new denominator.
  (d) OECD titles: list every row whose title is OECD's LLM headline and is new or
  changed, so R1 is a number the user rules on, not an estimate.
  (e) Attribution on every new OECD row.

**Gate that must pass (red-reviewer), either stage:** rebuild is byte-exact from the
committed inputs; the field-level delta in S1/S8 is reproduced by an independent route
(per-row comparison against `git show main:`, not a re-run of the engineer's script);
each new check is shown to fail on a corrupted input; `git diff --diff-filter=D` and
`PROGRESS.md` unchanged against the merge base (the stale-tree check, PROGRESS.md:394);
`git status --porcelain` clean at merge time; drift check clean after the rebuild is
committed.

---

## 8. Checks for red-reviewer (shell), including re-derivation of every [G]

```
# main @ 07f22c09
python -c "import json;d=json.load(open('data/incidents.json',encoding='utf-8'));I=d['incidents'];print(d['incident_count'],d.get('retracted_count'),len(I));
import re;print(sum(1 for e in I if e.get('aiid_id') is not None),
 sum(1 for e in I if (e.get('description') or '').startswith('AI Incident Database (AIID) entry #')),
 sum(1 for e in I if (e.get('description') or '').startswith('Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as')),
 sum(1 for e in I if e.get('description_source')=='oecd-aim'),
 sum(1 for e in I if any(s.startswith('OECD-AIM-') for s in e.get('source_ids',[]))))"
# expected from [G] counts: 15637 29 15666 / 1471 1468 3937 1 / 4104 (rows; the 4,160 Grep figure is id occurrences, not rows)
python -c "import json;I=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];\
print([e['id'] for e in I if e.get('aiid_id') and not (e['description'] or '').startswith('AI Incident Database (AIID) entry #')])"   # expect INC-00437, INC-08183, 1575's row
python -c "import json;D=json.load(open('data/id_deprecations.json',encoding='utf-8'));print(len(D) if isinstance(D,list) else {k:len(v) if hasattr(v,'__len__') else v for k,v in D.items()})"
git branch -a --contains 586f40c8            # expect only ws4/refresh-tripwire-42 and its origin ref
git merge-base --is-ancestor 586f40c8 main; echo $?   # expect 1 (not merged)
grep -n "D25" .github/workflows/auto-refresh.yml       # absence: expect empty
gh run list --workflow auto-refresh.yml --limit 12 --json databaseId,conclusion,createdAt   # runs after 2026-09-27; confirm still all failure
curl -sL https://oecd.ai/robots.txt | head -40
curl -s -o /dev/null -w "%{http_code} %{num_redirects} %{url_effective}" -L https://oecd.ai/sitemaps/incident-monitor-sitemap.xml   # R7 (HEAD returns 405; do not grep a Location header)
git rev-list --count 586f40c8..07f22c09   # 106
git rev-list --count 07f22c09..586f40c8   # 3
grep -n -i "oecd" PROGRESS.md | grep -i -E "repl|respon|answer"                            # R6 absence
```

Row-count block (R1 figures; added at gate bounce #1):

```
python -c "import json;I=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];\
print(sum(1 for e in I if any(s.startswith('OECD-AIM-') for s in e.get('source_ids',[]))))"  # 4,104 rows with an OECD-AIM- source id
python -c "import json;I=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];\
print(sum(1 for e in I if sum(s.startswith('OECD-AIM-') for s in e.get('source_ids',[]))>1))"  # 27 multi-id rows
python -c "import json;I=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];\
R={r['source_id']:r['title'] for r in json.load(open('ingest/oecd_aim_full_incidents.json',encoding='utf-8'))};\
print(sum(1 for e in I if any(R.get(s)==e['title'] for s in e.get('source_ids',[]))))"  # 3,937: title equals the row's own OECD source title
python -c "print(1533/4104, 1533/3937)"                                             # 0.3735, 0.3894
python -c "import json;I=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];\
print(sum(1 for e in I if e.get('description_provenance')))"                       # A5: 3,728 already labelled on main
```

Premise-style checks on the 7 merges: for each `from`/`into` pair, open the raw
`ingest/oecd_aim_full_incidents.json` rows and `ingest/aiid_full.json` rows named in
`D42-refresh-merge-review-2026-10-03.md` section A and confirm the cited AIID ids; in
particular row 5 (`OECD-AIM-2026-06-21-bcb5` vs `OECD-AIM-2026-04-14-1df3`, AIID-1677),
where the two board records disagree.

**Not measured by me:** the first-run delta on today's `main`; the exact post-snapshot
AIID row gain (~+94 is by subtraction from two different measurements); whether any
export other than `incidents.json` carries the new fields; any run after 2026-09-27;
whether OECD replied; the raw records behind the merge reads.

---

## Corrections before freeze (2026-10-09, gate bounce #1)

Corrected in place (memo not yet frozen). Figures from the gate/foreman are attributed
and each has a command in section 8; I re-checked the cited files where I could.
1. Section 1 and the section 2 table, R1, R3: 4,160 is `OECD-AIM-` id occurrences, not
   rows. Rows: 4,104 (27 with more than one id). 3,937 titles equal a raw OECD title;
   like-for-like replacement for NOTICE-DATA's "3,667 of 3,829" is 3,937 of 4,104.
   Growth restated: 1533/4104 = 37.4%, 1533/3937 = 38.9% (previous "+37%" was
   against the wrong base).
2. R1: the retitles to OECD-origin headlines are 3 (INC-01514, -01994, -00699), not 4;
   INC-01579 takes AIID-1370's title (tripwire audit `:236-242`, D42 review section B).
3. R6: "follow-up" was ambiguous; only a follow-up window (2026-08-21) is recorded
   (`docs/outreach/README.md:21`), no send.
4. Advisories: base is merge-base `a7343274` (fork point `9604752f`); run 37195068024
   (2026-10-04) noted in section 1; option A wording made consistent (4 do-not-approve
   merges + 4 retitles, plus 1 conditional merge + 1 conditional retitle; the "4
   do-not-approve merges" was wrong, see bounce #3); S1 now notes
   3,728 rows already carry `description_provenance`, so the 3,936 is OECD rows only.
   A4 (spec vs branch) left to the foreman.

## Corrections at gate bounce #2 (2026-10-09, D53)

- R3 cell corrected at bounce #2 (it had been listed as corrected at bounce #1 but was
  not): now "(3,667/3,829 vs 3,937/4,104)".
- Section 8 comment "reconcile with 4160 line count" replaced: 4,104 rows, 4,160 is id
  occurrences.
- Section 8 commands made sturdier per the gate: the 4,104 count uses
  `source_ids` `startswith('OECD-AIM-')` (not a `json.dumps` substring); the 3,937 count
  matches each row against its own OECD source title by `source_id`. Not run by me.
- Re-read of the whole memo for occurrence-as-row-count uses: lines 78-79, 124, 134-135,
  218 and 220 now say rows or occurrences correctly; no other use found. Caveat added
  here: the +1,533 is the 2026-10-03 "new-only IDs" count on the 13,361 corpus and may
  include non-OECD IDs, so the 37.4% / 38.9% ratios are an upper-bound style estimate,
  not a measured OECD-row growth.

## Corrections at gate bounce #3 (2026-10-09, D55, fresh author)

Corrected in place (memo not yet frozen). Old -> new, by section:
1. R8 (section 4): citation for "is emitted for OECD-derived rows today; whether one
   is warranted is a separate, not-yet-scoped question" changed from `SOURCE_LICENSES`
   1.5 to `NOTICE-DATA:256-258`.
2. Section 3 header: "109 commits behind main, 3 ahead" -> "106 commits behind main @
   `07f22c09` (the memo's base), 3 ahead" (foreman-measured). Section 8 gains
   `git rev-list --count 586f40c8..07f22c09   # 106` and `07f22c09..586f40c8   # 3`.
3. S1 (section 7): the 3,728 already-labelled rows now broken down in full: verbatim/
   cvelistv5 2,046; original/aiaaic 1,422; original/None 134; verbatim/cve-cna-via-avid
   125 (previously missing); original/oecd-aim 1 (INC-00437). Foreman-measured.
4. Merge counts: the D42 review section A marks merges 3 and 4 "Unsure, lean no" and
   6 and 7 "Do not approve"; 5 is "Approve" (contested by the tripwire audit, "doubtful").
   Option A, the section 3 "Reading across the table" paragraph, and the bounce #1
   item 4 above now read "2 do-not-approve merges (6, 7), 2 lean-no (3, 4), 1 contested
   (5)", consistent with the section 3 table. The earlier "4 do-not-approve merges" was
   wrong.
5. Option B (section 5): "fails more every week (2 -> 30 -> 42)" -> 29 (09-14), 30
   (09-20), 42 (09-27), 42 (10-04, run 37195068024); growth stalled at 42. Table checked
   against `refresh-tripwire-2026-10-03.md:47-49`; the 10-04 figure is from the foreman
   per the dated note in section 1.
6. R7 (section 4): the sitemap 302 is dated as a 2026-07-30 WebFetch observation
   (`SOURCE_LICENSES:140`); on 2026-10-09 foreman curl HEAD returned 405 and GET -L
   returned 200 with no redirect, so R7 is unconfirmed today. Section 8's
   `curl -sI ... | grep -i location` (which cannot fire on a 405) replaced by a GET-based
   check: `curl -s -o /dev/null -w "%{http_code} %{num_redirects} %{url_effective}" -L <url>`.
7. Cite range `refresh-tripwire:236-241` -> `236-242` (the INC-01994 row is at 242), in
   R1 and in bounce #1 item 2.

*Agent-suggested; do not regenerate. Supersede by a dated addendum, not by rewriting
(CLAUDE.md working agreement 4).*
