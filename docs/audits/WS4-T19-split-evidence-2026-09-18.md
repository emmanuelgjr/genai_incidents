# WS4-T19 — the 47-split remediation review: evidence and proposed authorization

**Status: RECORD, dated 2026-09-18. DO NOT REGENERATE.** Later work that
overtakes any claim here must add a dated update naming which half
changed, per working agreement 4 — not edit this text in place. Machine-
readable companion: `docs/audits/WS4-T19-split-evidence-2026-09-18.json`
(full per-split successor lists, reference URLs, inbound-deprecation
detail). Proposed authorized list (consumed directly by the build-time
guard): `docs/audits/WS4-T19-authorized-splits-2026-09-18.json`.

**Owner:** pipeline-engineer (WS4). **Boarded by:** D26/D27, following
`docs/specs/WS4-T15-redirect-persistence-2026-09-18.md` §7's sequencing
plan (item (a): "A human-reviewed remediation of the 47 splits... a
judgement call, not a computation").

## THE HARD BOUNDARY, restated

**This document and its companions propose; they do not apply.** No file
under `data/` or `schema/` was touched to produce this evidence. **D25(b):
the user rules on the authorized list below; that judgement is not
delegated to this document, to the build, or to any script.** Once the
user rules, a separate, later change executes the unmerge and lands it in
the same PR as the fix and the guard (per WS4-T15 spec §7(c)) — not this
one.

## How this evidence was derived

All figures **[R] re-derived 2026-09-18**, independently of (but matching)
`docs/specs/WS4-T10-unmerge-design-2026-09-15.md` and
`docs/audits/WS4-T10-phaseB-delta-2026-09-15.{md,json}` (both on branch
`ws4/t10-normalize-url`, not yet on `main` — the merge to `main` of that
fix was reverted 2026-09-18, `fe3a4845`, pending exactly this
remediation). Two detached scratch worktrees, never committed to and never
pushed:

- **control**: `origin/main` HEAD (`00b889c7`) — today's committed
  13,060-row corpus, unchanged `normalize_url`.
- **fixed**: `origin/main` HEAD with commit `fe3a4845` ("Revert 'Merge
  WS4-T10'") itself reverted — i.e. WS4-T10's `normalize_url` fix
  reapplied on top of everything currently on `main`, **including WS4-T15's
  deprecation-persistence machinery** (so this evidence reflects the
  codebase as it stands today, not the 2026-09-15 snapshot).

Both built via `python scripts/parse_existing.py && python
scripts/merge_and_dedupe.py` (the guard described in Deliverable 3 below
was added to `merge_and_dedupe.py` for this to prove itself against — see
that section). `scripts/audit/ws4t10_phaseb_delta.py` and
`scripts/audit/ws4t10_inbound_deprecations.py` (both already committed on
the `ws4/t10-normalize-url` branch, reused verbatim, not modified) produced
the underlying JSON. **Sanity check requested by the brief, not a
re-litigation**: the re-derived numbers match the 2026-09-15 audit exactly
— 13,060 → 13,361 (+301), 47 splits / 349 successors / 43 continuity-holds
/ 4 continuity-breaks, 26 downward severity changes, 8 inbound
deprecations all `WRONG_AFTER_FIX` — confirming WS4-T15's persistence
changes did not alter the split population or its classification.

## Summary: 47 splits, my judgement

**All 47 are judged DISTINCT — genuinely separate incidents that the old
`normalize_url`'s query-string collapse wrongly united, not incidents that
belong together.** Zero were found ambiguous enough to mark unsure on the
distinctness question itself (see "Confidence and its limits" below for
what this claim does and does not cover). 43 keep title continuity (the
row that would naturally keep the old id already has the old id's
content) and need **no new deprecation record** for the split id's own
identity. 4 break continuity (the mechanical mechanism hands the old id to
unrelated content) and should be **retired**, with a fresh id minted for
every successor including the piece that would otherwise have inherited
the old id.

| decision | count |
|---|---|
| keep_id (continuity holds) | 43 |
| retire (continuity breaks) | 4 |
| **total splits** | **47** |
| inbound resplit corrections (separate population, see below) | 8 |

## Full per-split table

`split_into` = number of successor rows. `continuity` = does the id that
keeps the old number also keep the old title. `inbound` = count of
historically-retired ids whose current `id_deprecations.json` record
points at this old id (detail below the table). Full successor lists,
titles, source_ids and reference URLs for every row are in the JSON
companion.

| old id | old title | split_into | continuity | inbound | decision |
|---|---|---|---|---|---|
| INC-00128 | Google's FLoC AI Ad Tracking Raises Privacy and Discrim... | 5 | HOLDS | 0 | keep_id |
| INC-00134 | City of Zhuzhou in Hunan Suspended Hellobike Robotaxi S... | 22 | HOLDS | 0 | keep_id |
| INC-00311 | AI-Driven Military Targeting Causes Mass Casualties in ... | 12 | **BREAKS** | 1 | **retire** |
| INC-00477 | AI-Generated Images Used in Fraudulent 'Case Fixing' Sc... | 2 | HOLDS | 0 | keep_id |
| INC-00554 | Tesla Driver Reportedly Said Driver-Assistance Mode Was... | 100 | **BREAKS** | 3 | **retire** |
| INC-00620 | Anthropic's Mythos AI Model Sparks Global Cybersecurity... | 3 | HOLDS | 0 | keep_id |
| INC-00623 | French Army Tests Boston Dynamics' Spot Robot in Combat... | 4 | HOLDS | 0 | keep_id |
| INC-00679 | AI-Generated Fake Crime Scene Image Causes Public Misin... | 5 | HOLDS | 0 | keep_id |
| INC-00754 | ChatGPT Was Alleged to Have Aided Planning of Florida S... | 11 | **BREAKS** | 1 | **retire** |
| INC-00774 | China Removes 39,000 Accounts for AI-Generated Harmful ... | 3 | HOLDS | 0 | keep_id |
| INC-00861 | Purported AI-Generated Advertisements Reportedly Falsel... | 31 | HOLDS | 0 | keep_id |
| INC-00891 | AI-Cloned Image of Peter Obi Used in N230 Million Forex... | 8 | HOLDS | 0 | keep_id |
| INC-00927 | Turkish Armed Drone Operation Neutralizes Six in Bitlis | 7 | HOLDS | 0 | keep_id |
| INC-00964 | New York Lawmakers Propose Ban on Armed Police Robots A... | 4 | HOLDS | 0 | keep_id |
| INC-01054 | Frontier AI Models Exhibit Peer-Preservation, Defy Shut... | 4 | HOLDS | 0 | keep_id |
| INC-01192 | In its design for automatic terminal command execution,... | 4 | HOLDS | 0 | keep_id |
| INC-01221 | India and Israel Advance AI-Enabled Missile Defense Col... | 3 | HOLDS | 0 | keep_id |
| INC-01269 | AI-Powered CT Diagnostics Aid COVID-19 Detection and Mi... | 5 | HOLDS | 0 | keep_id |
| INC-01271 | EU Investigates X's Grok AI for Generating and Spreadin... | 12 | HOLDS | 1 | keep_id |
| INC-01412 | Meta Sued Over AI-Enhanced Fraudulent Ads on Facebook a... | 6 | HOLDS | 1 | keep_id |
| INC-01535 | AI Hiring Tools Lead to Discriminatory Outcomes in US R... | 3 | HOLDS | 0 | keep_id |
| INC-01664 | Chinese AI Startup Publishes Satellite Intelligence on ... | 2 | HOLDS | 0 | keep_id |
| INC-01696 | Purported AI-Generated War Footage Reportedly Circulate... | 2 | HOLDS | 0 | keep_id |
| INC-01787 | South Korean Authorities Crack Down on AI-Generated Fak... | 2 | HOLDS | 0 | keep_id |
| INC-01791 | SpaceX and xAI Pursue AI-Driven Military Drones and Lun... | 2 | HOLDS | 0 | keep_id |
| INC-01897 | The Tag, Category, and Taxonomy Manager – AI Autotagger... | 8 | **BREAKS** | 0 | **retire** |
| INC-02590 | ForcedLeak — Salesforce Agentforce indirect prompt inje... | 2 | HOLDS | 0 | keep_id |
| INC-02671 | Grok Reportedly Generated and Distributed Nonconsensual... | 2 | HOLDS | 0 | keep_id |
| INC-05013 | AI-Enabled TruDi Navigation System Was Alleged to Have ... | 11 | HOLDS | 0 | keep_id |
| INC-05663 | Google Ads AI Enabled Discrimination Against Nonbinary ... | 2 | HOLDS | 0 | keep_id |
| INC-06264 | AI Uses Smartphone Data to Predict Schizophrenia Relaps... | 2 | HOLDS | 0 | keep_id |
| INC-06329 | AI-Powered Workplace Harassment Detection Raises Privac... | 3 | HOLDS | 0 | keep_id |
| INC-06518 | Dutch Court Rules AI Welfare Fraud Detection System Vio... | 2 | HOLDS | 0 | keep_id |
| INC-06527 | Elon Musk's Neuralink Plans Human Brain Implant Within ... | 3 | HOLDS | 0 | keep_id |
| INC-06558 | Facebook Bans Israeli AI Firm for Subconscious Manipula... | 3 | HOLDS | 0 | keep_id |
| INC-06729 | Israel Deploys AI-Driven Technology to Detect Hezbollah... | 5 | HOLDS | 0 | keep_id |
| INC-06778 | Mexican Government Plans Nationwide Biometric Data Coll... | 2 | HOLDS | 0 | keep_id |
| INC-06896 | Russian Railways Begin Testing AI-Equipped Trains to Re... | 2 | HOLDS | 0 | keep_id |
| INC-07224 | ProofPoint Evasion | 7 | HOLDS | 0 | keep_id |
| INC-07657 | Cobbler vulnerable to code injection via unsafe YAML lo... | 3 | HOLDS | 0 | keep_id |
| INC-07688 | Unspecified vulnerability in the Resource Manager compo... | 2 | HOLDS | 0 | keep_id |
| INC-07736 | Korean Chatbot Luda Reportedly Made Offensive Remarks T... | 17 | HOLDS | 1 | keep_id |
| INC-11452 | Apache Ivy External Entity Reference vulnerability | 2 | HOLDS | 0 | keep_id |
| INC-11831 | Apache JSPWiki CSRF due to crafted invocation on the Im... | 2 | HOLDS | 0 | keep_id |
| INC-12064 | phpBB Cross-Site Request Forgery (CSRF) | 2 | HOLDS | 0 | keep_id |
| INC-12120 | phpMyAdmin Cross-site Scripting vulnerability | 3 | HOLDS | 0 | keep_id |
| INC-12180 | Cross-site Scripting in Apache ActiveMQ | 2 | HOLDS | 0 | keep_id |

## Judgement method, and what confirms it per-row

Every split's successors were bridged by ONE specific query-string-bearing
URL family (computed mechanically by running the OLD, buggy `normalize_url`
over every successor's own reference URLs and grouping by key — the JSON
companion's `bridging_url_keys` per row). Three independent lines of
evidence, checked for every row, not asserted from a sample:

1. **Distinct source identity.** Every successor traces to a distinct
   `source_id` (a distinct OECD-AIM dated article, AIID entry, or CVE) —
   never the same source_id split across two rows.
2. **Distinct dates / distinct CVEs.** Where successors are OECD-AIM news
   items, their underlying dates differ (often by weeks or months — e.g.
   INC-00554's decomposition spans 2020–2026); where they are CVE/security
   advisories, their CVE numbers are always disjoint, including in every
   case where titles are near-identical boilerplate (confirmed directly:
   `INC-12120`/`INC-14628`/`INC-14629`, three "phpMyAdmin ... Cross-Site
   Scripting"-shaped titles, carry `CVE-2010-2958`/`CVE-2011-1940`/
   `CVE-2011-2505` and their paired CVEs — three different advisories, one
   templated report format).
3. **Title-similarity cross-check.** An independent `difflib` scan across
   every split's own successor-title pairs (not reused from the 2026-09-15
   audit's own scan, run fresh here) found 49 pairs above a 0.55
   similarity threshold; every one manually checked resolves to (1) or (2)
   above — distinct source_ids, distinct dates, or distinct CVEs. This
   corroborates, via a different derivation path, the 2026-09-15 audit's
   own 59-pair scan (design doc §2.4 / phaseB.md), which found zero
   regressions.

### Confidence and its limits

**Confident, not merely asserted**, for the distinctness call itself: it
rests on structural evidence (distinct source_ids + dates/CVEs + reference
URLs) checked for all 47 splits, not a read of every one of the 349
successors' full source article text — that would not scale to a
one-time, 349-row remediation, and is not what the three checks above
need in order to be conclusive (a duplicate incident cannot share zero
source_ids, zero CVEs, and a different date). Where this document is
NOT confident, it says so explicitly below rather than rolling it into
the 47/47 "distinct" figure:

- **Not this document's call, flagged for a separate fix**: `INC-02590`
  (ForcedLeak/Salesforce Agentforce) — the split itself is confidently
  distinct from `INC-14614` (Mulesoft Anypoint Code Builder, disjoint
  CVEs), but `data/curation_overrides.json`'s `CVE-2025-10875` entry
  (written for ForcedLeak) currently mis-keys onto `INC-14614` under the
  fix, per `docs/specs/WS4-T10-unmerge-design-2026-09-15.md` §2.3b. This
  needs re-keying as part of remediation, independent of the split
  decision.
- **A cross-split observation, not a per-split judgement, routed to
  WS4-T5**: `INC-00620`'s survivor ("Anthropic's Mythos AI Model Sparks
  Global Cybersecurity and Financial System Fears", 1 source, dated
  2026-04-18, Taiwanese/Singaporean press) and `INC-00623`'s successor
  `INC-14757` ("Anthropic's Mythos AI Raises Global Cybersecurity
  Concerns", 2 sources, dated 2026-04-08, Swedish/French/Belgian press)
  cover the same underlying "Mythos AI model" story from different
  regional press cycles on different dates. Checked directly: different
  OECD-AIM source_ids, different dates, disjoint reference-URL sets — by
  this document's own distinctness test they ARE distinct, and neither is
  a member of the OTHER's split group (the query-string bug never bridged
  them to each other), so this is not a defect in either split judgement
  above. It is flagged here because it is exactly the shape of question
  WS4-T5 (P1, dedupe error-rate audit, 100 merges + 100 near-misses) is
  scoped to answer for the corpus generally — whether OECD-AIM's
  per-dated-article granularity should ever collapse near-simultaneous
  coverage of one product story across different split groups. Out of
  this document's scope; not an "unsure" on the 47 splits themselves.

No other case surfaced ambiguity worth flagging: every high-similarity
title pair inspected under check 3 resolved cleanly to distinct
source_ids/dates/CVEs, and no successor within any of the 47 groups shares
a source_id, CVE, or reference URL with a sibling in the same group.

## The 4 continuity-breaking splits, in detail

- **`INC-00311`** — AI-Driven Military Targeting Causes Mass Casualties in
  Middle East Conflicts. The old id's real content moves to `INC-14726`;
  `INC-00311` itself is mechanically claimed by an unrelated Greek
  tax-authority story (12 total successors, Greek/Cypriot regional press
  bridged via `bankingnews.gr/index.php` and `ikypros.com` query-string
  ids).
- **`INC-00554`** — the flagship case (see
  `docs/specs/WS4-T10-unmerge-design-2026-09-15.md` §2.1 for the full
  decomposition). 103 source_ids resolve to 100 rows; the two real
  Tesla-crash sources land together on a brand-new id (`INC-14609`);
  `INC-00554` itself is claimed by an unrelated KBS-subtitle story.
- **`INC-00754`** — ChatGPT/FSU mass-shooting allegation moves to
  `INC-14608`; `INC-00754` itself is claimed by an unrelated Jason Momoa
  deepfake romance-scam story.
- **`INC-01897`** — every successor is a different WordPress plugin CVE
  (BetterDocs, S2B AI Assistant, Text Prompter, Quotes llama, LLMs.txt,
  Contest Gallery, ...), confirmed via disjoint CVEs, bridged only by
  `plugins.trac.wordpress.org/changeset`.

All four: genuinely distinct incidents: **split correctly**; the mechanical
"keep the id" tie-break happens to hand the old id to the WRONG piece.
**Recommendation: retire (Option 2)** — mint a fresh id for every
successor including the piece that would otherwise inherit the old
number, per `docs/specs/WS4-T10-unmerge-design-2026-09-15.md` §7.2.

## Inbound deprecations: 8 records, all landing wrong after the fix

Re-derived today against `data/id_deprecations.json` as committed
(unchanged, 1,051 entries) and the fixed build: **the same 8 records
found on 2026-09-15** in
`docs/audits/WS4-T10-inbound-deprecations-2026-09-15.json` (branch
`ws4/t10-normalize-url`), same classification (`WRONG_AFTER_FIX` for all
8 — none is fully, exclusively correct as a redirect after the fix, though
4 of the 8 retain a *partial* overlap with their recorded target, per that
artifact's own dated correction).

| retired id | recorded target (chain) | recovered sources | lands on | classification |
|---|---|---|---|---|
| INC-07771 | → INC-01271 (holds) | 1 | INC-14814 (1) | WRONG_AFTER_FIX |
| INC-08109 | → INC-01412 (holds) | 1 | INC-14847 (1) | WRONG_AFTER_FIX |
| INC-08133 | → INC-07736 (holds) | 1 | INC-14850 (1) | WRONG_AFTER_FIX |
| INC-08146 | → INC-08139 → INC-00554 (breaks) | 1 | INC-14853 (1) | WRONG_AFTER_FIX |
| INC-00497 | → INC-00311 (breaks) | 8 | 8 rows (1 still on INC-00311) | WRONG_AFTER_FIX |
| INC-03128 | → INC-00754 (breaks) | 10 | 9 rows (2 still on INC-00754) | WRONG_AFTER_FIX |
| INC-08139 | → INC-00554 (breaks) | 92 | 90 rows (2 still on INC-00554) | WRONG_AFTER_FIX |
| INC-08185 | → INC-08139 → INC-00554 (breaks) | 65 | 63 rows (2 still on INC-00554) | WRONG_AFTER_FIX |

**Note the two that redirect into CONTINUITY-HOLDING splits**
(`INC-08133`→`INC-07736`, `INC-07771`→`INC-01271`): a split id's own
title/content staying correct (HOLDS) does not mean every historical
record that redirects INTO it is still correct — these two demonstrate
that directly. All 8 need their own direct `resplit` record (per
`docs/specs/WS4-T10-unmerge-design-2026-09-15.md` §8.2's proposed record
type, exempted from that section's supersession) pointing at their
CURRENT recovered landing row(s), independent of whatever happens to the
47 split ids.

**My judgement on all 8: confident, `resplit`, not a same-incident
question.** Each of the 8 is a mechanical redirect-staleness finding, not
a distinctness judgement — the retired id's own recovered content
(recovered from git history, SHAs in the inbound-deprecations JSON) is
compared against where it lands today; there is no ambiguity about
whether the retired id and its current landing spot(s) are "the same
incident" the way there is for a fresh split.

## Deliverable 2 — what is being proposed for authorization

`docs/audits/WS4-T19-authorized-splits-2026-09-18.json`: 55 `(from,
reason)` pairs — 43 `split_continuity_holds_keep_id`, 4
`split_continuity_breaks_retire`, 8 `inbound_resplit_correction`. **Status:
PROPOSED.** No code in this task applies it to `data/`; it exists so (a) a
human can read it beside this evidence and (b) the guard below can be
tested against it in a scratch tree, per the brief.

## Deliverable 3 — the pre-authorization guard

Implemented in `scripts/merge_and_dedupe.py`
(`_check_split_authorization`, called from `main()` immediately before
any output file is written — both the `id_deprecations.json` write and
the `incidents.json` write). It aborts (raises
`SplitAuthorizationError`, a `SystemExit` subclass, nonzero exit, no
traceback) if this build's own dedupe would cause a previously-single
PUBLISHED id's historical member keys (`source_ids` + `cve_ids` from the
last committed build) to resolve onto more than one row this build,
**unless that id's `from` is present in
`docs/audits/WS4-T19-authorized-splits-2026-09-18.json`**. Reports EVERY
unauthorized id found, not just the first (proven by test — see below),
and no file is written until the check passes.

**Name the input that makes it fail** (working agreement 6): any build
whose dedupe output would newly resolve a previously-single published
id's own historical member keys across >1 row, where that id is not on
the authorized list — including the empty-list case, and the
partial-list case (some real splits authorized, at least one not).

**Proof of fire, against the REAL transition** (not merely a unit-test
fixture — done in the `fixed` scratch worktree described above, never
committed):

1. **Empty list** (no `docs/audits/WS4-T19-authorized-splits-2026-09-18.json`
   in the scratch tree): `python scripts/merge_and_dedupe.py` exits
   **1**, prints `[split-guard] ABORT: this build would silently split 47
   previously-single PUBLISHED id(s)...`, enumerates all 47 old ids and
   their new row sets, and `git status --porcelain -- data` in that
   worktree shows **zero changes** — nothing was written.
2. **Full list added** (the 55-entry proposed list from Deliverable 2,
   copied into the scratch tree only): the same build now prints
   `[split-guard] 47 previously-single published id(s) resolve to >1 row
   this build; all are on the authorized list ... -- proceeding.`, exits
   **0**, and writes `data/incidents.json` (13,361 rows) /
   `data/id_deprecations.json` (1,052 entries) — matching the design
   doc's and this document's own independently re-derived numbers exactly.

**Proof it discriminates, not merely toggles** (the predecessor's
integrity guard, per the brief, passed on only 4 of the 8 cases it was
written for — this guard is proven against a case that specifically tests
partial authorization, both in a scratch build and as a committed unit
test): `tests/test_merge_and_dedupe.py`'s
`test_split_guard_reports_every_unauthorized_id_not_just_the_first`
authorizes ONE of two independent, fabricated splits and asserts the
guard still aborts, naming only the unauthorized one. Four more guard
tests (`test_split_guard_fires_with_empty_authorization_list`,
`test_split_guard_fires_when_authorization_list_is_missing_this_pair`,
`test_split_guard_passes_once_the_pair_is_authorized`,
`test_split_guard_ignores_ordinary_merges_and_retention`) cover the
empty-list abort, the wrong-entry abort, the successful pass with output
verification, and a check that the guard does NOT fire on the
already-tested ordinary-merge/retention shapes. All 5 pass; the full
suite (362 tests) passes unchanged.

## Deliverable 4 — the dry-run delta

Produced entirely in the scratch trees above; no `data/` file in this
repository was written. Full JSON:
`docs/audits/WS4-T19-dryrun-delta-2026-09-18.json`, explainer:
`docs/audits/WS4-T19-dryrun-delta-2026-09-18.md`.

## What the user is being asked to approve

1. **The 47-split decision table above**: 43 ids keep their number
   (nothing to authorize beyond "yes, let this split happen" — no new
   deprecation record is written for these), 4 ids (`INC-00311`,
   `INC-00554`, `INC-00754`, `INC-01897`) retire, with every successor
   (including the piece that would otherwise inherit the old number)
   getting a fresh id and the old id getting a new `reason: "split"`
   deprecation record pointing at all of them.
2. **The 8 inbound-redirect corrections**: each retired id listed above
   gets a new, additional `reason: "resplit"` record pointing at its
   actual current landing row(s) (append-only — the original `merged`
   record is preserved, per invariant 9 / `docs/ID_POLICY.md` rule 2).
3. **Two flagged follow-ups, not part of this authorization**: re-key
   `curation_overrides.json`'s `CVE-2025-10875` entry from `INC-14614` to
   `INC-02590` (§2.3b of the T10 design doc); and a WS4-T5 cross-check on
   the `INC-00620`/`INC-14757` Mythos-coverage observation.
4. **Net effect if approved and executed**: corpus 13,060 → 13,361
   (+301), `id_deprecations.json` 1,051 → at least 1,061 (+4 `split`
   records for the retirements, +8 `resplit` records for the inbound
   corrections — schema-architect's call on exact shape), zero deletions,
   zero id reuse.

This document does not execute any of the above. It is the evidence and
proposal D25(b) reserves the user's ruling for.
