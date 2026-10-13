# Board archive: PROGRESS.md dated log to 2026-10-04

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4). Moved verbatim from `PROGRESS.md` on 2026-10-13 under user ruling D94 (repo cleanup), at main `b31e2e3f`-era content. Nothing was edited; part 1 and part 2 are byte-identical slices of the original file, in their original order. The live board keeps the task table, Phase-1 declaration, escalations, decisions, precedents and corrections.

---

## Part 1 (original PROGRESS.md lines 2137-3804)

## 🎉 v2.12.0 PUBLISHED 2026-10-04: all VERSIONING steps done and independently verified

- **Count:** **`incident_count` 15,637 (from 13,361, +2,276); `retracted_count` 29; 15,666 entries in the file** (D44 semantics). Landmark count 1,915, unchanged.
- **What ships:**
  - wave 1–2 sources (AVID, cvelistV5 with the huntr CNA, arXiv cs.CR metadata): 2,305 new entries, all `auto`/`feed`;
  - WS4-T2: 29 retracted and 6 flagged for REJECTED CVEs;
  - schema `status`, `status_reason` and `rejected_cve_ids`;
  - licence rows 2.4 (corrected), 2.5 and 6.1–6.4; CVE ToU and AVID MIT notices;
  - redirect-checked conduct.
- **Gates (all records in `docs/audits/`):**
  - wave12: BOUNCE ×2 under D45, then PASS (`29e98fee`);
  - WS4-T2: BOUNCE ×3 under D46, then PASS (`1600178f`);
  - integration: PASS (`07532bb6`);
  - notes: BOUNCE ×2 under D47, then PASS (`47781e06`);
  - pre-publish: BOUNCE ×1, then PASS (`9962ae44`).
- **Step 6 [R]:** `--no-ff` merge `1813599f` on main. Tag `v2.12.0` (`8e3a6ad0`) is pushed, and `git ls-remote origin 'refs/tags/v2.12.0*'` shows `^{}` = `1813599f`, the merge commit. The merged tree has 0 deletions vs the previous main and `PROGRESS.md` is unchanged.
- **Step 7 [R]:** Release published, not a draft. The body is byte-identical to `docs/releases/v2.12.0.md` (19,743 B, API with UTF-8 decode).
- **Step 8 [R]:** Zenodo version DOI **`10.5281/zenodo.23144567`**. doi.org returns 302; the record has version 2.12.0, concept DOI 10.5281/zenodo.20248675, published 2026-10-04.
- **Step 8b [R]:** the DOI is filled into the notes (`36f760fd`). The Release body was re-synced and re-verified byte-identical (20,074 B).
- **Step 9 [R]:** `publish.yml` and `huggingface.yml` both show event `release`, headBranch `v2.12.0`, completed/success.
  - **PyPI** latest is 2.12.0, with wheel and sdist.
  - **HF card** (`emmanuelgjr/genai-incidents`): "Dataset version `2.12.0`", 15,637.
  - **Live STIX/TAXII [R]** (after Pages run `def08cdf` completed/success): the STIX bundle has 65,141 objects / 15,637 incidents, and the TAXII collection objects have 65,141 / 15,637. That matches the gated notes.
- **The goal's tranche-names item:** not found on any surface, so the list was reconstructed, gated and merged (`docs/specs/source-expansion-tranche1-*`). The user may amend it.
- **Open for the user:**
  - wave 3 (CourtListener bulk + 0din) and wave 4 (OpenSSF, or widen the GHSA filter);
  - the D42 review of 17 OECD/AIID refresh changes;
  - the duplicate-rejection policy (3 entries);
  - N11, the issue-#88 suppression review (410 rows);
  - sending the ENISA/EUVD outreach.
- **Follow-ups:**
  - N9 (CVE/GHSA feed precision);
  - N10 (21 AVID-only CVEs need their first rejection check);
  - STIX `revoked`;
  - the `load_incidents` doc;
  - the refresh branch (WS4-T12/T14) gate and merge;
  - the HF card template phrase "real-world and research incidents".

## 🚚 2026-10-03 — USER GOAL: waves 1+2 APPROVED · count update · release if it bumps · tranche-1 names · push and merge

- **⚖ D40, USER RULING 2026-10-03: waves 1 and 2 are APPROVED.**
  - **Wave 1:** AVID + cvelistV5, with huntr as a CNA filter inside cvelistV5.
  - **Wave 2:** arXiv cs.CR via OAI-PMH, metadata only, with EUVD as enrichment.
  - **EUVD is NOT ingested until outreach settles its licence (d).** Its outreach email is drafted for the user to send (protocol step 8).
  - **Release:** the user directed checking the count, updating it, and cutting a release if it bumps.
- **Tranche-1 names, searched again by new routes:** Gmail (the only "huntr" hits are the unrelated huntr.co job newsletter), Google Drive (OWASP documents only), and every earlier route. **Not found.**
  - **Solution, at the user's direction:** a reconstruction from the tranche-2 brief's own phrasing, which is the US and industry counterpart of each worldwide category. It is recorded with each name's basis in `docs/specs/source-expansion-tranche1-reconstruction-2026-10-03.md` (`8699cc35` on `ws0/tranche1-reconstructed`, pushed).
  - The 8 reconstructed names: CERT/CC VU, CourtListener, FTC, 0din, EPSS, OpenSSF malicious-packages, HF security, GHSL. **The user may amend them.**
- **Count-update finding: the weekly auto-refresh has FAILED on every run since the unfreeze.**
  - The failing runs are 09-20 and 09-27. Both fail on the E21 tripwire `test_oecd_aiid_content_disagreement_is_unique_to_inc00437`, which found 42 rows against an expected 2.
  - As a result no refresh PR has opened, and `incident_count` has been 13,361 since 2026-09-18.
  - The AIRI download URL also returns 404.
- **Dispatched in parallel, one worktree each.** The deviation from serial execution is deliberate: the tasks are independent, and integration happens by rebuild.
  - license-auditor: wave 1–2 `SOURCE_LICENSES` rows, the CVE ToU and AVID MIT notices, and the EUVD outreach draft (`ws0/wave12-licence-rows`).
  - license-auditor: reconstructed tranche-1 pre-rows (`ws0/tranche1-reconstructed`).
  - pipeline-engineer: refresh-tripwire diagnosis, measurement only (`ws4/refresh-tripwire-42`).
  - pipeline-engineer: N1, the 17 entries still active for rejected CVEs, reconciled under invariant 3 with a field-level delta (`ws4/rejected-cve-reconcile`).
  - pipeline-engineer: wave 1–2 ingest (AVID, cvelistV5 + huntr CNA + the post-2026-06 CVE catch-up, arXiv OAI-PMH), with a field-level delta (`ws4/wave12-ingest`).
- **Delivered so far:**
  - **Wave 1–2 licence rows:** `ad8ddfb5` on `ws0/wave12-licence-rows`, pushed. Not gated alone; they gate together with the ingest PR (invariant 10). The AVID MIT text was foreman-verified word-identical to upstream.
  - **Foreman correction to the auditor's draft:** the MITRE copyright line was written from memory with "All rights reserved". Per cve.org's own `FooterModule.vue` it is "Copyright © 1999-{currentYear}, The MITRE Corporation.", and it has been fixed.
  - **Tranche-1 pre-rows:** `06c7d561` on `ws0/tranche1-reconstructed`, pushed.
    - **Foreman refuted:** T1.9 (Hugging Face advisories) does not exist as a source and is to be dropped.
    - T1.8 and T1.10 largely duplicate ingested OSV and GHSA.
    - red-reviewer has been dispatched to run the 24 absence checks.
- **⛔ Tranche-1 pre-rows: BOUNCE #1 (red-reviewer, 2026-10-03, on `06c7d561`). 8 defects.** The verdict is in `docs/audits/source-expansion-tranche1-gate1-verdict-2026-10-03.md`, both parts saved as received and concatenated by shell.
  - **Refuted by shell:**
    - T1.6 0din: a CC BY 4.0 HF corpus exists, so 1 → 2.
    - T1.7 EPSS: FIRST's terms exist and are purpose-limited; it stays 1, no longer provisional.
  - **T1.4 CourtListener splits:** 2 for bulk S3, 0 for crawling, because robots.txt says `Disallow: /`.
  - **Text corrections:** T1.3, T1.5, T1.8, T1.9 and T1.10.
  - **Gate measurements [R]:** of the 24 checks, 13 confirmed, 6 refuted, 4 resolved.
  - **The foreman's framing was confirmed** on T1.9 (drop it) and on the OSV question.
  - Fixes have gone to license-auditor for verbatim application.
- **N6 CONFIRMED by gate [R], and now RELEASE-BLOCKING.**
  - `SOURCE_LICENSES.md` row 2.4's "every reachable OSV database is CC-BY 4.0" is FALSE. OSV lists "OpenSSF Malicious Packages (Apache 2.0)".
  - **The committed `ingest/cve_nvd_expanded.json` carries 2 `MAL-` records with verbatim Apache-2.0 OpenSSF text under a CC BY claim**: MAL-2026-3607 and MAL-2026-2144. The repo itself is a distribution channel.
  - The published `data/incidents.json` carries no MAL text today. INC-08450's description comes from GHSA.
  - **The fix rides the wave-1/2 licence PR:** correct row 2.4 in place, as a live surface, and either filter `MAL-` in the OSV ingest or attribute those records per record as Apache-2.0.
- **Tranche-1 gate-1 fixes applied, `6608869a`.** Foreman-verified: 10 gate phrases present. Then **⛔ BOUNCE #2 (string re-check, 2026-10-03), escalated.**
  - **What passed:** no score, action letter or quote is wrong. The 23 applied quotes match the gate's raw captures.
  - **What failed:** leftover first-pass text contradicts the corrections, and statuses still say "pending". The verdict is in `docs/audits/source-expansion-tranche1-gate2-verdict-2026-10-03.md`, saved as received.
- **⚖ D41, USER RULING 2026-10-03:** apply the gate's text verbatim, then a narrow string check (the D39 pattern). The fixes went to license-auditor.
- **✅ Tranche-1 licence pre-rows PASS (D41 string check, red-reviewer, 2026-10-03, on `d1a6774b`). No defects.** The verdict is in `docs/audits/source-expansion-tranche1-gate3-PASS-2026-10-03.md`.
  - **Gated scores:** CERT/CC 1 · CourtListener 2 (bulk) / 0 (crawl) · FTC 2 · 0din 2 (via the HF CC BY corpus) · EPSS 1 · OpenSSF 2 · HF drop · GHSL 1.
  - **Next:** tranche-1 estimates go to a fresh pipeline-engineer.
- **Refresh-tripwire diagnosis DELIVERED (pipeline-engineer, `9ef355f5` on `ws4/refresh-tripwire-42`, pushed).** Record: `docs/audits/refresh-tripwire-2026-10-03.md`. Not yet gated.
  - **The 42 rows:** 2 known + 30 new + 7 existing that gained an `aiid_id` + 3 mixed.
  - **One mechanism:** OECD's `aiid_ids` act as merge keys while the AIID snapshot is stale.
  - **No OECD narrative ships:** 42/42 descriptions are `build_description()`.
  - **Only one fatal failure:** the tripwire is it. The AIRI download is `continue-on-error`; AIRI was relaunched as Next.js, its zip is gone and `/api/` is robots-disallowed. Last successful refresh: 2026-05-31.
  - **Unblocking would write** 7 new `merged` deprecations (permanent; 3–4 look wrong on a title-only read), retitle 4 published IDs, and add `aiid_id` to 11 rows.
- **⚖ D42, USER RULING 2026-10-03: keep D25(a) in force for OECD/AIID refresh merges.**
  - The release ships waves 1–2 plus the rejected-CVE fix on today's committed OECD/AIID data.
  - **Build WS4-T12** (OECD description provenance) and **WS4-T14** (an AIID snapshot step in the refresh) next.
  - The 7 merges come back to the user as a reviewed list (D28 pattern) before any refresh merges.
- **NEW BOARD NOTE N8 → WS0 + WS4.** The AIRI Navigator ingest is dead since 2026-05-31: the site was relaunched, the data zip is gone, and `/api/` is disallowed. It needs a redesign: find whether the bulk data is published elsewhere, and get a licence re-read.
- **Wave 1–2 ingest DELIVERED** (pipeline-engineer, `ws4/wave12-ingest`, pushed). The licence rows were merged in under invariant 10 → `d49d9647`.
  - **Claimed:** 13,361 → **15,872 (+2,511)**, 0 changes to existing entries, IDs INC-14911..17421. By source: cvelistV5-only 2,240, AVID 103 + 105, arXiv 63. Tests 520 pass.
  - **Design choices the engineer made:**
    - AVID enrichment of existing CVE entries was dropped on purpose: it would have tripped the split guard, and it rewrote 79 fields.
    - `scripts/corpus_overlap.py` skips any row that would fold into an existing entry.
    - The cvelistV5 bulk asset comes in via the new `fetch_to_file`, not `git clone`.
    - The OpenSSF `MAL-` text is purged by `scripts/audit/purge_openssf_mal.py` (verified: "Per source details" now has 0 hits).
  - **⚠ Deviation the foreman flagged for the gate:** cvelistV5's 2,240 is about 5× the gated estimate (≥416 + ~165/yr). **Filter precision is the crux.**
  - **red-reviewer dispatched** with a precision sample of ≥60 + 20 + 15, delta re-derivation, invariants and licensing.
- **N6 handling, recorded as a decision (it was implemented before it was recorded; a specialist caught the gap):** `MAL-` (OpenSSF, Apache-2.0) records are **EXCLUDED** from the OSV route, via `is_openssf_malicious` in `scripts/ingest_cve_nvd_expanded.py`. `SOURCE_LICENSES` row 2.4 now states this.
  - **Open, for the gate and possibly the user:** MAL-2026-3607 is kept as a bare identifier plus links, so that INC-08450 does not split.
- **Tranche-1 estimates DELIVERED** (`85deb30d`, pushed).
  - **Proposed waves:** CourtListener (bulk) and 0din → wave 3; OpenSSF → wave 4; FTC on hold (robots 403 to the project UA); CERT/CC, EPSS and GHSL held.
  - **Gate dispatched** to the tranche-2 §4–5 reviewer.
- **⛔ Tranche-1 estimates: BOUNCE #1** (red-reviewer, on `85deb30d`). The verdict is in `docs/audits/source-expansion-tranche1-estimates-gate1-verdict-2026-10-03.md`, saved as received.
  - **D1:** OpenSSF is dominated by GHSA. 157 of its 158 candidates have a CC BY GHSA malware twin.
  - **D2:** the N6 text was stale; exclusion via OSV does not zero T1.8.
  - **D3:** the sensitivity sentence. **D4:** an FTC [M] scope.
  - **Products confirmed:** 16, 12, 8, 0.
  - **FTC 403 diagnosis:** an edge rule rejects UAs containing a URL, which includes the project UA. It is not robots.
    - Bypassing it would be evasion.
    - **The only routes are FTC outreach (the user sends it) or a user ruling.**
  - The fixes went to pipeline-engineer for verbatim application.
- **✅ Tranche 1 (reconstructed): DONE and MERGED to main** (`80d8b840`, merged `--no-ff`).
  - **Gates:** licence pre-rows PASS at `d1a6774b`; estimates and ranking BOUNCE #1, then PASS at `80d8b840` (`docs/audits/source-expansion-tranche1-estimates-gate2-PASS-2026-10-03.md`).
  - **Gate evidence [R]:** products 16 / 12 / 8 / 0 re-derived by independent routes; merge-tree rc=0; only `docs/specs/` touched.
  - **Proposed waves (decision owed to the user):**
    - **Wave 3:** CourtListener (bulk S3 only; needs a curated docket list and a privacy review) + 0din (HF CC BY corpus; at most 14 new records beyond AVID).
    - **Wave 4:** OpenSSF only if the user accepts per-record Apache attribution. The cheaper route is to widen the GHSA malware filter, since 157 of 158 candidates have a GHSA twin.
    - **Hold:** FTC (an edge rule returns 403 to the project UA; route is FTC outreach or a user ruling), plus CERT/CC, EPSS and GHSL.
  - **Advisory 1 (wording) was not applied;** it is recorded in the PASS file.
- **⛔ Wave 1–2 ingest PR: BOUNCE #1** (red-reviewer, on `d49d9647`). The verdict is in `docs/audits/wave12-ingest-gate1-verdict-2026-10-03.md`.
  - **NOT a precision failure [R]:** cvelistV5 precision is about 97% counting only clear false positives, about 91% counting borderline cases as misses. The corpus's existing CVE/GHSA feed measures about 48% by the same method.
  - **Delta confirmed [R]:** 0 existing entries changed, rebuild byte-exact, guard tests fire when mutated.
  - **The 7 defects:**
    - D1: arXiv dates use the latest-version date; 8 papers are pre-window.
    - D2: AVID CVE-class rows carry CNA text under an MIT marker.
    - D3: 87 AVID third-party rows ship verbatim text.
    - D4: `INGESTION_CONDUCT` entry 3 still says pending.
    - D5: `SOURCE_LICENSES` cells contradict the code.
    - D6: about 20 clear false positives that would become permanent IDs (Linux-kernel `llm`, MitraStar GPT routers, product self-descriptions).
    - D7: the NOTICE-DATA MITRE trademark line.
  - **Foreman routing:**
    - D3 is resolved by making the code match row 6.1 (original prose); this is not a licensing change.
    - D1, D2, D4, D6 and the code half of D5(c) → pipeline-engineer.
    - D5(a), (b), (e) and D7 → license-auditor.
    - D5(c) row text follows the code.
- **⚖ D43, USER RULING 2026-10-04 (gate defect 5(d)):** arXiv selection is deterministic only.
  - Ship the filter-selected papers as quality_tier `auto`.
  - license-auditor amends row 6.3 to describe the real filter.
  - A human curation pass may follow later.
- **2026-10-04, foreman found by reading the tree (agreement 3): all three engineer branches finished on 10-03 and never reported.** That is the idle-without-report failure shape.
  - **Wave 1–2:** `12f58dd9`, rebuilt at 15,666 (+2,305), with the BOUNCE #1 fixes applied. The licence edits for 5(a), (b), (e) and D7 were committed by the foreman as `394b35ac`.
  - **Rejected CVEs:** `50ce7dbe`. A full sweep of 6,998 corpus CVEs found **37 REJECTED**, so **29 entries are retracted** (`status: retracted`) and 6 flagged. `incident_count` 13,361 → 13,332 with `retracted_count` 29. 163 fields changed, 0 unintended, nothing deleted. A schema change sits in its own commit, `e9092586`.
  - **Refresh:** `586f40c8`, containing WS4-T12, WS4-T14, the tripwire replacement and the per-merge evidence.
- **⚠ STALE-TREE DAMAGE in `50ce7dbe` (found by foreman, fixed `11706b11`).** The commit's tree predated the tranche-1 merge, so it silently **deleted 9 merged tranche-1 spec and gate-verdict records and 98 lines of `PROGRESS.md` board entries** (the D40 block onward).
  - It was restored byte-for-byte from its own parent, `6957df48`, in a separate commit.
  - The other two branches were checked the same way and are clean.
  - **This is the same shape as the earlier revert that deleted board records.** The control was a `--diff-filter=D` and `PROGRESS.md` check against the merge base before gating. Make that a standing pre-gate step.
- **⚖ D44, USER RULING 2026-10-04:** `incident_count` counts only entries that stand, and **retracted entries are excluded**. A new `retracted_count` is published beside it.
  - Retracted entries stay in the file with resolvable IDs, but leave the STIX/MISP/TAXII/HF feeds.
  - The release notes must warn that `len(file) = incident_count + retracted_count`.
- **Wave 1–2 status:**
  - Gate part 2 is appended verbatim to the gate-1 record.
  - **Gate measurements [R]:** precision about 97% (91% strict) against a corpus baseline of about 48%. Rebuild is byte-exact; mutation tests fire.
  - The 1,521 post-June rows are mostly the stalled NVD refresh, **not new-source coverage**. The release notes must not claim them as new-source coverage.
  - Gate-1 defects are fixed at `941868e6`, and arXiv now ships `auto` per D43.
  - **Routed to pipeline-engineer:** A2 (cvelistV5 rows `reviewed` → `auto`; the CNA's CVSS is not analyst review), A1 (make the MAL bare row durable in the NVD writer), A4 (`common.py` follows redirects to an unchecked host: an invariant-5 conduct fix), A6 (the NSFW title prefix), and the delta leftovers.
  - **NEW BOARD NOTE N9 (A3) → pipeline-engineer + label-scientist.** A scope audit of the existing CVE/GHSA feed: the gate measured about 48% precision (n=40). This is a bigger precision issue than the PR itself; related to #88.
- **Refresh (`586f40c8`) is NOT in this release.** It is built: T12 labels 3,936 rows' provenance, and T14 adds the AIID snapshot step. Its merge needs a rebuilt `data/` plus the D42 review of 17 proposed changes (7 merges, 10 retitles; evidence in `docs/audits/D42-refresh-merge-review-2026-10-03.md` on that branch). It follows the release.
- **Rejected-CVE (WS4-T2):** gate-1 BOUNCE #1, re-scoped to `2fad3865` (D1–D6). The verdict is in `docs/audits/rejected-cve-gate1-verdict-2026-10-04.md`, saved as received.
  - **Gate measurements [R]:** 37/29/6 confirmed against the cvelistV5 bulk asset over all 6,998 CVEs; 0 of wave12's 2,525 CVEs is REJECTED.
  - **schema-architect ADOPTED** the schema with four tightenings (`2fad3865`).
  - **Fixes delivered:**
    - `6780dfe2`: D1–D4.
    - `e22b04ee`: row 2.5 quotes the CVE ToU, committed by the foreman.
    - `11a16eea`: A6 and A7.
    - `2fcc659a`: D5 and D6.
  - **Re-gate dispatched.**
- **Wave 1–2:** gate-2 **BOUNCE #2 (escalated)**. The verdict is in `docs/audits/wave12-ingest-gate2-verdict-2026-10-04.md`.
  - **What passed:** all 7 gate-1 defects; precision ≥91% strict on a fresh sample; byte-exact rebuild; 15,666 with 0 existing entries changed.
  - **The one real defect:** the MAL carry runs before the empty-write guard, so a blocked refresh would overwrite the ingest file with 1 row.
- **⚖ D45, USER RULING 2026-10-04:** apply the gate's fix verbatim, then a narrow check. The code goes to pipeline-engineer; the 6.2 text and the "88" count go to license-auditor.
- **Open policy question for later (not blocking):** should CVEs rejected as DUPLICATES be re-pointed to their canonical CVE instead of retracted? This covers 3 entries whose canonical CVE is absent.
- **Follow-ups logged:**
  - retracted STIX objects to be emitted as `revoked` rather than dropped;
  - a `load_incidents()` docstring or filter;
  - N9, the CVE/GHSA feed precision audit.
- **WS4-T2 re-gate: BOUNCE #2, escalated.** The verdict is in `docs/audits/rejected-cve-gate2-verdict-2026-10-04.md`.
  - **What passed:** D1–D6 fixed and failing-first verified, including A6, which the author had not run; STIX 54,318 with 0 rejected CVEs emitted; delta 35/163 unchanged; byte-exact rebuild; 496 tests.
  - **The remaining defect, D7:** row 2.5 cites the NOTICE-DATA §6.2 CVE notice, which exists only on the wave 1–2 branch.
  - **⚠ Gate refuted in part, by the record:** D7(b) said no reviewer checked the ToU by curl on 10-03. The tranche-2 gate-1 record shows a different red-reviewer instance did. The record's foreman note cites it.
- **⚖ D46, USER RULING 2026-10-04:** ship both branches in ONE release merge, so the §6.2 reference and the notice reach main together, and apply the precise attribution wording (citing the 10-03 gate record plus the 10-04 re-fetch).
- **Replacements, per agreement 3:** the wave-12 D45 specialists stalled for 4 h with work unstarted and were replaced with fresh `pe-wave12-d45` and `la-wave12-d45`.
- **D45 fixes delivered.** `69fde622` is the row 6.2 text, committed by the foreman (it had been left uncommitted by the stalled instance; verified verbatim). `29e98fee` (fresh pipeline-engineer) covers the empty-run guard before the carry, a `main()`-level test with failing-first proof, the seed deduped to 88, the robots-redirect guard and the delta note. `data/` is byte-identical.
- **D46 fix delivered:** `4dc80b77`, the row 2.5 attribution.
- **Narrow checks dispatched on both branches.**
- **✅ BOTH DATA BRANCHES PASS (2026-10-04).**
  - **Wave 1–2 (`ws4/wave12-ingest` @ `29e98fee`):** D45 narrow check PASS (`docs/audits/wave12-ingest-gate3-PASS-2026-10-04.md`).
    - **Gate measurements [R]:** the empty-run guard was verified through the real `main()`; the mutation fails the new test; byte-identical rebuild; 15,666; 563 tests.
  - **Rejected CVEs (`ws4/rejected-cve-reconcile` @ `1600178f`):** D8 string check PASS (`docs/audits/rejected-cve-gate3-PASS-2026-10-04.md`).
    - **Gate measurements [R]:** D1–D6 were verified failing-first at gate 2, and the D46 single-merge plan was confirmed by `git merge-tree`.
    - **Escalation path:** 3 bounces were taken under D46 rulings; the last was a 2-word attribution fix.
  - **Next: integration.** pipeline-engineer merges both branches onto `release/v2.12.0`, hand-resolves the Makefile (keeping both targets), rebuilds and publishes one field-level delta against main. The stale-tree check is mandatory because both branches are based on `9604752f`.
- **v2.12.0 INTEGRATION DELIVERED** (`release/v2.12.0` @ `9aed2a4a`, pushed).
  - **Counts:** **15,666 entries; `incident_count` 15,637 (+2,276 vs main); `retracted_count` 29;** landmark 1,915 (unchanged).
  - **Delta:** 2,305 new (wave12) + 163 field changes on 35 entries (WS4-T2), **0 unintended** (`docs/audits/v2.12.0-integration-delta-2026-10-04.md`).
  - **Build and checks:** double rebuild byte-identical; 583 tests; no stale-tree deletions.
  - **Foreman checks [R]:** licence surfaces are singular (row 2.5, §6.2, CVE grant with ™).
  - **The engineer correctly refused one part of the foreman's brief:** the wave12 targets stay OUT of `ingest-all`, per the gated design note.
  - **In parallel:** the integration gate (fresh red-reviewer) and the release-notes draft (distribution-engineer, VERSIONING step 1).
- **Integration gate 1 (`9aed2a4a`): data PASS, 2 doc defects** (`docs/audits/v2.12.0-integration-gate1-verdict-2026-10-04.md`).
  - **Gate measurements [R]:** the 3-way per-field delta has 0 mismatches; exporters re-run show 15,637 incidents and 0 rejected CVEs emitted; byte-identical rebuild.
  - **The 2 defects:** the README count attribution, and the sweep scope (21 AVID-only CVEs on new entries are unchecked).
  - **Fixes:** release notes `7a4614b0` (distribution-engineer); D1 and D2 fixed at `07532bb6`. The README omits the bare 2,305 because `check_stats_drift` forbids it.
  - **Dispatched:** a combined pass, the integration re-check plus the release-notes gate (VERSIONING step 1).
- **NEW BOARD NOTE N10 → pipeline-engineer:** 21 AVID-only CVEs on new wave-12 entries have no rejection state. The next rejection refresh should pick them up (never-checked first); verify after the first run.
- **v2.12.0 gates so far:**
  - **Integration (`release/v2.12.0`): CLOSED, PASS** (re-check at `07532bb6`).
  - **Release notes, BOUNCE #1** (`docs/audits/v2.12.0-notes-gate1-verdict-2026-10-04.md`): confidence split, the issue-#88 suppression of 410 rows (not folding), backlog dates, carried-figure labels.
  - **Fixes at `9f00cf6c`.** **BOUNCE #2** (`...-notes-gate2-...`): a 14% share misattributed to the 410, and the 112 figure unlabelled. **The foreman's brief repeated the author's wrong 14% sentence; the gate refuted it.**
- **⚖ D47, USER RULING 2026-10-04:** apply verbatim, then a string check. Next: the cut.
- **NEW BOARD NOTE N11 → maintainer (user):** 410 of the wave-12 emitted rows (352 cvelistV5, 58 AVID, 79 of them huntr) are suppressed by the issue-#88 out-of-scope list (`data/issue88_remediation.json`). Some may be wrongly listed, for example CVE-2023-7215 (chatgpt-web). This is a maintainer review, not settled by v2.12.0.
- **✅ v2.12.0 RELEASE NOTES PASS** (D47 string check, `47781e06`). VERSIONING step 1 is complete.
- **THE CUT BEGINS (VERSIONING steps 2–9) on `release/v2.12.0`:**
  - pipeline-engineer: the `USER_AGENT` bump in `ingest/common.py` plus the `INGESTION_CONDUCT` literal.
  - distribution-engineer: the four other version strings; rebuild; step-4 render; step-5 prose sweep and CHANGELOG re-tense.
  - Then a pre-publish gate, the `--no-ff` merge, and a tag on the merge commit.
- **NEW BOARD NOTE N7 → corpus-surgeon (WS1).** INC-08450 merges three unrelated packages (beproduct GHSA-6xwp, mistralai GHSA-wx9m / CVE-2026-46412, guardrails-ai MAL-2026-3607) under one ID. It is a possible over-merge, not investigated.
- **NEW BOARD NOTE N6 → license-auditor (WS0, shipped data).** `SOURCE_LICENSES.md` row 2.4 says every reachable OSV database is CC BY 4.0. OSV lists OpenSSF malicious-packages (`MAL-`) as **Apache-2.0**, and `MAL-` aliases are in the corpus. The red-reviewer advisory is pending.
- **Integration plan:**
  1. Merge the licence rows into the ingest branch (invariant 10).
  2. red-reviewer gates each data branch.
  3. Integrate on a release branch and rebuild.
  4. Run the VERSIONING.md cut if the count bumps.

## ✅ Source-expansion evaluation (tranche 2 + partial tranche 1): **DONE and MERGED to main `2504fb89` (2026-10-03)**

- **Final gate: PASS (fresh red-reviewer, gate 6, 2026-10-03, on `946a7e55`), no defects.** Verdict text in `docs/audits/source-expansion-tranche2-gate6-final-PASS-2026-10-03.md`.
  - D1–D9 landed verbatim, and every stale string is gone.
  - The evidence JSON loads as strict UTF-8.
  - The diff is 3 files, +27/−31.
  - `merge-tree` against origin/main returned rc=0.
  - `SOURCE_LICENSES.md`, `data/`, `scripts/` and `ingest/` have 0 diff.
- **Licence half PASSED at gate 4** (`5163c10b`). The full gate trail is gates 1–6 in `docs/audits/source-expansion-tranche2-*`.
- **Deliverable:** `docs/specs/source-expansion-evaluation.md`, plus `docs/specs/source-expansion-estimates-evidence-2026-10-03.{md,json}` and the scope record.
- **Foreman stray check:** the only untracked file was the gate-6 record, created deliberately. The merge touches 4 `docs/specs/` files, +3,190 lines.
- **docs-warden (protocol step 7): not dispatched.** The merge changes no counts, public claims, licensing text, taxonomy lists or version strings; it adds internal evaluation specs only. `SOURCE_LICENSES.md` is untouched by design (invariant 10).
- **⚖ DECISION OWED TO THE USER: first-wave approval.** The waves as gated:
  - **Wave 1: AVID + cvelistV5**, with huntr as a CNA filter inside cvelistV5. cvelistV5's floor is ≥416 backlog and about 165/yr; AVID is about 1,070 net-new.
  - **Wave 2: arXiv cs.CR (OAI-PMH metadata) + EUVD as enrichment.** EUVD needs ENISA outreach, which the user sends.
  - **Wave 3 (optional):** hand-curated ICO/EDPB.
  - The user's prior is "mostly not supported" (§5.4).
  - The ranking covers 29 of about 37 candidates. **The other eight tranche-1 names are still needed from the user.**
  - No ingest code until a ruling.
- **NEW BOARD NOTES from this evaluation. These are routed to their owners but not yet dispatched; each needs its own task.**
  - **N1 → pipeline-engineer (WS4, data integrity, highest priority).** **17 corpus entries (18 CVE ids) are `source_status: active` for CVEs that cve.org/NVD mark REJECTED.** Measured by pipeline-engineer and re-derived by gate 5 via cve.org (18/18). This is a WS4-T2 reconciliation gap on the shipped corpus.
  - **N2 → pipeline-engineer (WS4).** **The CVE refresh is stale:** the newest corpus CVE month is 2026-07. pipeline-engineer estimated about 515 proxy-AI CVEs missing; gate 5 found an independent NVD lower bound of 334.
  - **N3 → pipeline-engineer (WS4, invariant 5 machinery).**
    - `ingest/common.py` never parses Crawl-delay; ICO 6, BSI 10 and arXiv 15 must be passed by callers today.
    - stdlib `robotparser` has no RFC 9309 wildcard or longest-match support, so it wrongly refuses the Dutch AP's `/documenten/*`.
  - **N4 → license-auditor (WS0).** The hand-curated inputs `ingest/avid_owasp_incidents.json` (130), `arxiv_incidents.json` (123), `research_incidents.json` (135) and `threat_reports_incidents.json` (82) have **no `SOURCE_LICENSES.md` row naming them**. AVID wave 1 would close the AVID part. The 21 OWASP rows and the other two files remain.
  - **N5 → license-auditor (WS0).** The repo carries **no CVE Terms of Use notice** (gate 1 D7, confirmed). It is owed for cvelistV5 and arguably for the existing NVD-derived CVE text.
- **Process lessons, recorded:**
  - (a) The foreman retyped gate verdicts into "verbatim" records **twice**. The fix that worked was saving messages to disk as received and concatenating them by shell.
  - (b) Requesting long verdicts in parts ("defects 1–5, then 6–9") delivered complete text with no truncation.
  - (c) A stalled applier was replaced rather than re-prompted, per agreement 3, and the replacement finished in minutes.

## 🌍 Source-expansion evaluation, tranche 2 (worldwide): **license-auditor DISPATCHED 2026-10-02** on `eval/source-expansion` (pushed, `83da7445`) · ⚠ **the tranche-1 record does not exist**

- **User brief, 2026-10-02.** Evaluate about 30 worldwide candidates under the same discipline as tranche 1:
  - license-auditor writes a pre-row for each candidate first (invariant 10 applied at evaluation time; absence findings follow the standing rule);
  - pipeline-engineer then estimates volume, overlap and dedupe load, ingest shape, corpus fit, reconciliation cost (WS4-T2) and non-English handling;
  - the output is one committed ranked file, with waves of 2–3 sources for the user's approval;
  - **no ingest code is written before a ruling.**
  The scope record is `docs/specs/source-expansion-tranche2-scope-2026-10-02.md`. The deliverable will be `docs/specs/source-expansion-evaluation.md`.
- **⚠ Foreman finding: the "first ten" evaluation exists nowhere.**
  - `git grep -i huntr` across every local and origin ref, all 21 worktrees, and this board found no evaluation file.
  - The only names known are the user's priors, CISA and huntr. CISA KEV is already ingested (`SOURCE_LICENSES.md` §2.1), so tranche-1 "CISA" presumably means a CISA surface beyond KEV. That is an unconfirmed inference.
  - This has the working-agreement-1 shape: a chat-only deliverable lost at a session boundary.
  - **Consequence:** the cross-tranche first-wave decision the user asked for cannot be ranked until the user supplies the ten names and they are re-evaluated under the same discipline. **Escalated to the user 2026-10-02.**
- **Second search for the first ten (user asked, 2026-10-02), run by different routes. Still not found.**
  - **Git:** every local and origin ref, all file types. `huntr` appears only in `ingest/README.md:40` and in NVD reference URLs.
  - **Commit messages:** nothing relevant.
  - **Transcripts:** all 11 Claude Code session transcripts for this project, subagent transcripts included. Only the current session mentions huntr or "tranche".
  - **Memory directory:** nothing.
  - **Published artifacts:** the only one is unrelated.
  The record is gone or was never written.
- **Foreman correction, found during that search: two tranche-2 "new" candidates are already corpus inputs.**
  - `ingest/avid_owasp_incidents.json` (130 rows) and `ingest/arxiv_incidents.json` (123 rows) are hand-curated files with no ingest script.
  - `research_incidents.json` (135) and `threat_reports_incidents.json` (82) are in the same position.
  - None of the four is named in `docs/SOURCE_LICENSES.md`. §4's arXiv text covers only the ten red-team benchmarks.
  - license-auditor has been told to note this in the AVID and arXiv rows. Whether these four files need rows of their own (WS0-T1 accept criterion wording: "every source in `scripts/ingest_*.py`") is **open, and not yet routed**.
- **In flight:** license-auditor is writing tranche-2 pre-rows, rejections (CNNVD/CNVD, Snyk/VulDB, news aggregators) and watch items (EU AI Act Art. 73 register, EUVD API maturation). Its absence findings route to red-reviewer for a curl check.
- **2026-10-03: license-auditor DELIVERED. Verified by reading the tree; all of it is committed and pushed on `eval/source-expansion`.**
  - `62890512`: 27 pre-row tables, 4 rejections, 2 dated watch items.
  - `8ddb7702`: the AVID and arXiv existing-subset lines, plus section 6, which lists 30 checks for "not found" results, each with its curl/grep.
  - **14 of the 27 rows rest partly on search extracts or on sites that blocked the fetch.**
  - **Auditor's preliminary scores, not yet verified:**
    - NCSC 3, ANSSI 3, ICO 3, arXiv metadata 3.
    - ACSC 2 (search extract only), cvelistV5 2 (MITRE notice required), AVID 2.
    - **CCCS 1: non-commercial only, which breaks the user's "permissive trio" prior.**
    - **EUVD 1 (d):** no terms found, and the docs page is a JS app the fetch tool could not render.
    - VulnCheck KEV 0, BAILII 0, CanLII 0, Bugcrowd 0.
  - **Auditor error, caught by the foreman:** its chat report said `ingest/README.md` does not name the curated files. It does, at lines 37 and 41; the grep's escaped `\|` probably failed. The file's wording was correct, so no edit was needed.
- **red-reviewer DISPATCHED 2026-10-03** to run the 30 checks against raw HTML. Its brief requires a different route for NCSC, ACSC, ANSSI, EUVD and cvelistV5, plus a re-check of the VulnCheck and Bugcrowd prohibitions.
- **⛔ BOUNCE #1 (red-reviewer, 2026-10-03, on `8ddb7702`). The full verdict text is in `docs/audits/source-expansion-tranche2-gate1-verdict-2026-10-03.md`.**
  - **Seven defects:**
    - D1, JVN: the quoted FAQ text is not on the page. The page actually says "no particular restrictions… please notify by email".
    - D2, CSA: the row missed a clause prohibiting links without permission, so its score reads as 0, not 1.
    - D3, JPCERT: "no ToS" is refuted. `jpcert.or.jp/guide.html` allows quotation freely and requires notification for redistribution.
    - D4, ENISA: "ToS not located" is refuted. The legal notice authorises reproduction with acknowledgement.
    - D5, EUVD: "none located" is refuted. The ENISA legal notice applies, and the official docs repo's LICENSE bars reuse of the docs. Watch item W2 is refuted too.
    - D6, ICO: "terms page not found" is refuted. OGL v3.0 is confirmed, so score 3 stands but the citation is owed.
    - D7, cvelistV5: check 13 false-fires on the MITRE ATLAS notice. The CVE ToU notice gap itself is confirmed by a targeted grep.
  - **Measured by the gate [R]:**
    - Results on the 30 checks: 19 confirmed, 7 refuted, 4 still unverifiable (ACSC behind Akamai, CanLII behind DataDome, DEF CON/Black Hat, CNVD/CNNVD/VulDB).
    - VulnCheck's open-licence prohibition is verbatim on the April 2026 Service Terms, so 0/(d) stands. Bugcrowd's prohibition is verbatim.
    - The gate took a different route on all five high-weight rows.
    - Invariants hold: only the two specs files changed (895 insertions); `SOURCE_LICENSES.md` and `data/` diffs are 0.
  - **Foreman stray check:** main tree porcelain was clean.
- **Redispatched to license-auditor with D1–D7 and the gate's smaller corrections.** The brief also adds pre-rows for the two tranche-1 names the user did give: huntr and CISA beyond KEV.
- **2026-10-03: rework DELIVERED, verified in the tree and committed as `6d77a194` (pushed).**
  - Each fix was confirmed by grep for its distinguishing content: JVN 引用、転載、再配布, CSA "caching and links to", `guide.html`, the ENISA reproduction clause, `euvd-docs-public`, ICO copyright-and-re-use, the CVE ToU grep, AVID-2026-R1714, fr-lo, Crawl-delay 10, §1E, and section-6 items 31–33. The withdrawn JVN phrases survive only inside the withdrawal notes.
  - **Score changes:** CSA 1→0; ACSC 2→1 provisional; ENISA split 2 for PDFs and 1 for web text.
  - **New rows:** huntr 1 (c); CISA beyond KEV 2 (CISA-authored text) and 1 (co-sealed material).
  - The huntr terms quotes came through a converter and are unverified.
- **red-reviewer RE-GATE (attempt 2) DISPATCHED. A second bounce goes to the user.**
- **⛔ BOUNCE #2 (red-reviewer, 2026-10-03, on `6d77a194`). This is the SECOND bounce, so it is ESCALATED TO THE USER (protocol step 6).** The full verdict text is in `docs/audits/source-expansion-tranche2-gate2-verdict-2026-10-03.md`.
  - **What passed:** all gate-1 fixes D1–D7 landed correctly. Every changed score follows from its row except ACSC. Invariants PASS.
  - **Defects in the new 1E rows:**
    - D1: huntr §7.1 is misquoted. "irrevokable" was a converter artefact.
    - D2: huntr's "tool unreliability" claim is refuted. The 404s were genuine. The PANW Terms of Use bar reproduction; score 1 (c) still follows.
    - D3: the huntr corpus count. Measured [R]: 284 distinct bounty URLs (216 huntr.com + 68 huntr.dev; 277 distinct IDs) in 210 of 13,361 entries.
    - D4: CISA "ToS not located" is refuted. The `/site-links` policy pages are found; §105 is now verified verbatim; the 2/1 split follows.
  - **Gate-1 imprecision the reviewer carried forward itself:**
    - D5: the CSA quote is truncated.
    - D6: the "MITRE Corporation" line reference.
  - **Smaller items:** D7 (AP Dutch verbatim), D8 (JPCERT quotation notice).
  - **D9: ACSC score 1 contradicts the scale's own score-2 definition.** This needs a choice.
  - **Every defect comes with replacement wording to apply verbatim** (D37 precedent).
  - **Foreman stray check:** main porcelain clean.
- **⚖ D39, USER RULING 2026-10-03, on BOUNCE #2:**
  - **(a) Apply the gate's replacement text verbatim, then a narrow string-check gate** (D37 precedent). The specialist applies each replacement with an occurs-once replace (Edit's unique-match), without re-deriving. The narrow gate then confirms the strings landed and that nothing else moved.
  - **(b) ACSC stays at 1, and the scale is amended.** The score-1 definition gains "or a grant known only from a search extract whose primary page could not be reached (provisional)". ACSC returns to 2 once its primary page is read.
  - **Then:** pipeline-engineer estimates → final gate → merge.
- **2026-10-03:**
  - **Replacement and redispatch.** The D39 applier stalled after one partial edit and was REPLACED per agreement 3: stopped, and a fresh license-auditor dispatched. Its fixes were verified by foreman grep and committed as `e2b1c988` (pushed): 9 must-be-present strings were present, 4 must-be-absent strings were absent, and the stale section-6 status line was fixed.
  - **Narrow string-check gate:** dispatched to red-reviewer on `6d77a194..e2b1c988`.
  - **pipeline-engineer dispatched in parallel** on `eval/source-expansion-estimates` (from `e2b1c988`, its own worktree). It fills sections 4–5 only, which are disjoint from the gated licence rows, and gets merged after. **The deviation from serial execution is deliberate**, because the two sections do not overlap.
- **Gate 3, the D39 narrow string-check (red-reviewer, 2026-10-03, on `e2b1c988`): BOUNCE on 3 text-only defects.** The verdict text is in `docs/audits/source-expansion-tranche2-gate3-D39-stringcheck-2026-10-03.md`.
  - **The 3 defects:**
    - D1: the stale "need raw-HTML confirmation" header in the huntr cell.
    - D2: item 33's command returns 277, not 284. The pattern was partly the gate's own omission; corrected commands were re-run and give 284 and 277.
    - D3: five stale "not gated / method-suspect" status lines.
  - **What passed:** everything else, including verbatim landing of D1–D9, no undeclared moves, ACSC at 1 with the new scale clause cited, and invariants.
  - **⚖ Foreman call, surfaced to the user:** this is treated as falling WITHIN D39 (apply the gate's text verbatim, then a string-check), not as a third bounce. Every defect is the gate's own exact text and needs no re-measure. **The user may overrule.**
  - **Next:** the fixes went to the same fresh license-auditor for verbatim application, followed by a string re-check.
- **Gate-3 fixes APPLIED and verified by the foreman, then committed as `5163c10b` (pushed).**
  - All 6 must-be-0 strings are at 0, and all 4 must-be-≥1 strings are present.
  - **Huntr figures re-derived by a different route [R]:**
    - the gate's two commands give **284** URLs and **277** IDs;
    - an independent per-entry Python scan gives **210 of 13,361** entries.
- **⚠ Foreman defect, found by license-auditor: the three gate-verdict records are not byte-verbatim.**
  - The foreman's transcription introduced em dashes, arrows and some compressed phrasing.
  - As a result, two of the gate's replacement strings did not match literally. The auditor matched them by content instead and disclosed that it had done so.
  - A dated correction has been added to all three records, with the originals preserved under agreement 4.
  - **Lesson:** a record that calls itself verbatim must be pasted, not retyped.
- **✅ LICENCE HALF PASS (red-reviewer, gate 4 string re-check, 2026-10-03, on `5163c10b`). No defects.**
  - The verdict is in `docs/audits/source-expansion-tranche2-gate4-recheck-PASS-2026-10-03.md`, pasted rather than retyped.
  - **Gate evidence [R]:** item-33 commands re-run, 284 / 277; stale-string sweep 0 hits; diff 7/7 with every hunk declared; invariants PASS.
  - **Advisory, routed to the final merge pass:** the ANSSI Retrieval-method cell (line 238) still says "method-suspect" although gate 1 confirmed it. Change it to "gate-confirmed (curl, 2026-10-03)".
  - **Remaining:** pipeline-engineer sections 4–5 → merge into `eval/source-expansion` → final red-reviewer gate on 4–5 → merge to main.
- **2026-10-03: pipeline-engineer DELIVERED sections 4–5.**
  - **Verification and merge:** confirmed by foreman diff. There are exactly two hunks, at the section-4 and section-5 placeholders, plus two evidence files: `docs/specs/source-expansion-estimates-evidence-2026-10-03.{md,json}`. It was merged into `eval/source-expansion` as `6d9e0038` (`--no-ff`, pushed). The ANSSI advisory went to license-auditor.
  - **Proposed waves:**
    - **Wave 1:** AVID + cvelistV5, with huntr as a CNA filter inside cvelistV5. About 1,200–1,600 net-new entries, estimated.
    - **Wave 2:** arXiv cs.CR via OAI-PMH, plus EUVD as enrichment only. EUVD needs ENISA outreach, which the user sends.
    - **Wave 3, optional:** hand-curated ICO/EDPB.
  - **On the user's prior: "mostly not supported."**
    - CISA beyond KEV scores product 2, and `cisa.gov` feeds return 403 to our UA.
    - huntr pages are client-rendered shells, so huntr is reached through the CVE route instead.
    - EUVD: 3,873 of 3,873 items carry a CVE alias.
    - NCSC publishes guidance, not incidents.
    - CCCS is non-commercial, with 0 AI items in a sample of 50.
    - ACSC is unreachable through `common.py`.
  - **Cross-cutting findings, NOT yet routed:**
    - (a) `ingest/common.py` never parses Crawl-delay.
    - (b) Stdlib robotparser uses first-match order, so it wrongly refuses the AP's `/documenten/*`. Fixing this needs an RFC 9309 parser.
    - (c) `export.arxiv.org` robots says `Disallow: /`, so the route must be OAI-PMH.
    - (d) The CNIL open-data host disallows `/resources`.
    - (e) **The corpus CVE refresh is stale.** The newest CVE entry is from 2026-07, and about 515 proxy-AI CVEs are missing. That is a refresh gap, not a new-source gain.
    - (f) **17 corpus entries (18 CVE ids) are `active` although NVD marks those CVEs Rejected.** This is a measured WS4-T2 case.
    - (e) and (f) are data-integrity findings on the shipped corpus and need routing to pipeline-engineer as board notes after this task merges.
- **Next:** ANSSI tidy → final red-reviewer gate on sections 4–5 → merge to main.
- **ANSSI tidy committed `fb64ea10`** (a 1-line diff, verified).
- **⛔ Final gate on sections 4–5: BOUNCE #1 on 4–5 (fresh red-reviewer, 2026-10-03, on `fb64ea10`). 9 defects.** The verdict is in `docs/audits/source-expansion-tranche2-gate5-final-sections45-2026-10-03.md`; its defect sections were shell-concatenated from files saved as received, not retyped.
  - **Defects:**
    - D1: the "not in corpus" lists are refuted. 9 of 302 EUVD ids and 5 of 233 huntr ids are already present as AVID-keyed entries. Corrected to 293 and 228, union 416.
    - D2: the wave-1 yield floor rises to 416 (about 165/yr).
    - D3: CVE ids vs entries (5,293 entries).
    - D4: the AP robots cause. stdlib robotparser has no wildcard support.
    - D5: the non-English rule is missing on 5 rows and partial on 1.
    - D6: `source_status`.
    - D7: the evidence JSON has one Latin-1 byte.
    - D8: a stale placeholder line.
    - D9: CCCS extrapolation unlabelled; Garante contradiction.
  - **Confirmed by a different route [R]:**
    - AVID 1,790 / 109 / V025;
    - huntr 2,496 / 111;
    - **(e) max CVE month is 2026-07, with an independent NVD lower bound of 334 missing;**
    - **(f) 18/18 REJECTED via cve.org, 17 entries active;**
    - Crawl-delay never parsed; the arXiv and data.gouv robots facts;
    - arithmetic, sort and licence factors;
    - scope, and a clean merge-tree.
  - **Not re-derivable:** arXiv 2/535 (no ID list).
  - **Foreman stray check:** clean.
- **Next:** pipeline-engineer applies D1–D9 verbatim → string re-check → merge to main. on the rows not licence-blocked → ranked waves to the user. Still blocked on the user's tranche-1 names for the cross-tranche ranking.

## 🖼 README PR #100 — **MERGED `e1260900` (2026-10-01)** · D32 post-cut queue COMPLETE

**Rebase.** A squash-rebase of `docs/readme-refresh` (5 commits, base `528d5936`) onto post-v2.11.0 main produced `0c4b51cc`. main had changed only README:33 and README:71 since the branch point; **both were carried byte-identical from main** (D37-verified :33, emoji prefix kept; gated `50e42bbe` :71, now a plain paragraph under "Latest release" instead of the old callout). `render_docs_stats` moved the At-a-glance tile to 2.11.0. Pushed with `--force-with-lease` pinned to `8e23d6e6`. The first attempt used a wrong SHA and was **correctly rejected (stale info)**, so nothing was overwritten.

**CodeQL caught my own code: 2 new alerts on `scripts/readme_assets/shot.mjs`.**
- HIGH `js/unvalidated-dynamic-method-call`: CDP reply ids indexed a plain object.
- MED `js/bad-code-sanitization`: the selector was spliced into an evaluated expression.

**Fixed, not dismissed** (`67de4f3f`): a Map plus a function-type check, and `Runtime.callFunctionOn` with the selector passed as an argument. Functionally re-tested: both screenshots re-capture with the same element bounds. **CodeQL then passed, with 0 open alerts on the PR.**

**Checks:**
- CI: all 7 passed (CodeQL ×4, a11y, validate 3.12 and 3.13).
- pytest 476/1; no link from main's README dropped; all relative links resolve.

**Post-merge [R], with the working tree now on `main`:**
- README:71 and :33 verbatim on main;
- the drift check is clean;
- all 11 README image URLs (raw `main`) return 200.

**Process note:** this PR did not get its own red-reviewer gate, because the user directed "rebase, push and merge". The controls were byte-equality of the two gated lines against main, CI including CodeQL (which found real defects), and the drift check. **Advisory:** a docs-warden pass on the new README is cheap if wanted.

**Housekeeping:** a stale worktree from the 2026-09-20 session held `main` and blocked switching. It was inspected first: 283 deletions, 0 files present (temp cleanup), HEAD on origin/main, no stash. It was removed. **The main tree is now on `main`**, which ends the branch-confusion condition behind D29.

**D32 queue: STIX fix ✅ · docs-warden ✅ · D38 disclosure ✅ · README PR #100 ✅.**

## ✅ D38 disclosure — **PASS (red-reviewer, second gate, 2026-10-01, on `802ab95c`) — MERGED `43591dcd` — v2.11.0 Release body re-synced and byte-verified**

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: PASS … All four BOUNCE #1 defects and advisory A4 are closed in all four files. I re-measured every timestamp myself … The new 11,753 figure holds on the LIVE bundle."*

**Evidence [R]:**
- **Timestamps, re-measured:** deploy-pages completed 13:43:56Z; live Last-Modified is 13:43:53 GMT; the Release was published 06:17:47Z.
- **11,753, by two routes:** on the live bundle and TAXII, every relabelled object is an `x-genai-incident`; from the corpus, Σ len(owasp_llm) = 17,750 and 11,753 entries have a non-empty `owasp_llm`.
- **Tag build against live:** the ids, order and `modified` are equal. Reversing the relabel leaves a residual of 0, and a **fire control** gives 1.
- **MISP:** 34/34 files byte-identical.
- **`export_taxii.py`:** the AST with str constants blanked is equal, and **both fire controls trip**.
- The generated README differs from live only by the new section.
- 476/1; the drift check is clean; merge-tree is clean.

**Merge:** `43591dcd` on origin, with the merged tree re-tested (476/1, drift clean).

**Release re-sync:** `gh release edit v2.11.0`, then byte-verify via the API with an explicit UTF-8 decode (the gate's recipe; jq appends a newline, and cp1252 decoding gives a false mismatch). Result: **`True 35324 35324`**. The addendum and the DOI are both present, and the Release is not a draft.
- **The tag's copy of the notes (34,137 B) and the Zenodo record do not carry the addendum.** That is expected (A5).

**Follow-ups:**
- The CHANGELOG `[Unreleased]` does not mention the site UI fixes (Years tile, ASI wrap) shipped in the same deploy.
- "(the corpus)" is a loose gloss.
- The `export_taxii.py:9` docstring mentions OpenCTI.
- Template "currently -2026" is hardcoded.
- The STIX bundle has no published checksum.
- The `modified`-bump policy is undecided (user).
- README:18 / DATASHEET:115 `source_name` docs (warden finding 3, partly open).

**D32 post-cut queue: step 1 (STIX) and step 2 (docs-warden) are DONE, and D38 disclosure is DONE. Remaining: step 3, the README PR #100 rebase.**

### ⛔ D38 disclosure — **BOUNCE #1 (red-reviewer, 2026-10-01, on `476c9f5d`)** — four false or overclaimed sentences; re-dispatched to WS6 with the gate's own scoped wording

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … first gate on this task."*

**DEFECTS:**
1. **HIGH.** The CHANGELOG says "the STIX line of `docs/data/SHA256SUMS` changed". That is **false**: SHA256SUMS has **no STIX line**, because `pages.yml` runs `gen_data_integrity.py` **before** `export_stix.py`. The live file has 33 lines and 0 stix; a v2.11.0-tag reproduction of the deploy order equals the live file. **The claim originated in an earlier gate's "Published surfaces on merge" list on this board, which is testimony refuted by a different route (agreement 5/6).**
2. **MED.** "Before 2026-10-01" (DATA_DICTIONARY:205 and the TAXII template) is misleading. The deploy of `7dc80602` completed at **13:43:57Z** (Last-Modified 13:43:53 GMT); `-2025` was live during the v2.11.0 publication at 06:17Z.
3. **MED.** OpenCTI is overclaimed. The earlier advisory said consumers "may" miss the change; the text says "will not", stated as fact about a third party, and is untested. **Scope it** to consumers that treat an unchanged (`id`, `modified`) as an already-seen version, as STIX 2.1 versioning permits, and say they **may not** pick up the change. Drop "OpenCTI for example" unless it is verified.
4. **LOW.** "Every `data/*.json` unchanged" includes the gitignored STIX bundle at `data/incidents.stix.json`. Make it "every **committed** `data/*.json`".

**Evidence [R]:**
- Live STIX and TAXII: 54,485 objects with 17,750 `-2026`. The **v2.11.0-tag build has 17,750 `-2025`**. An independent Σ len(owasp_llm) gives 17,750.
- **Per-object delta, tag against live:** the id sets are equal, `modified` is equal on every object, and the ONLY differing path is `.external_references[].source_name`, with 17,750 changes on **11,753 `x-genai-incident` SDOs**. The TAXII manifest is byte-identical.
- The branch build is byte-identical to the live files.
- **MISP:** 34 live files, `diff -r` against the tag build is empty.
- PyPI and HF last changed at 06:18Z, before the deploy.
- Migration applied 2026-08-17. LLM03 is Supply Chain under 2025 and Excessive Agency under 2026.
- `export_taxii.py`: the AST with str constants blanked is equal, **proven to fire** with a mutated control.
- 476/1; the drift check is clean; merge-tree is clean.

**Advisories:**
- A1: the template hardcodes "currently -2026" (WS6 follow-up: interpolate the derived label).
- A2: **the STIX bundle has no published checksum**, because of the step order (WS6 follow-up; a change would need its own disclosure).
- A3: the relabel changed content without bumping `modified`, which breaks STIX 2.1 versioning; the policy is still open.
- A4: "query for old and new" is ambiguous.
- **A5: re-syncing the Release body with the addendum is consistent with agreement 4 and step 8b** after the fixes. Note that the tag's copy of the notes, and so the Zenodo archive, will NOT carry the addendum.

> **Dated correction, 2026-10-01 (gate A6):** the "🛰 WS6 STIX OWASP-edition + site fixes — PASS" entry's advisory A3 says "The 17,750 SDOs change content". **The measured figure is 11,753 SDOs carrying 17,750 references.** *Dated record; the entry above is not rewritten.*

## ⚖ D38 — USER RULING, 2026-10-01: **disclose the live STIX relabel now**, not at the next release (amends D32's timing)

**One WS6 pass, then a gate:**
- a CHANGELOG `[Unreleased]` entry with the re-import instruction (warden finding 1);
- a **dated, do-not-regenerate addendum** to `docs/releases/v2.11.0.md`'s consumer-impact section (finding 2; agreement 4);
- one sentence in DATA_DICTIONARY, plus the `scripts/export_taxii.py` README template, saying the STIX OWASP `source_name` is edition-qualified (finding 3).

**Under D38, WS6 is authorized for the template-text edit in `export_taxii.py`, and that edit only.** The next release notes still repeat the disclosure.

### 📋 docs-warden sweep after the STIX merge (origin/main `f6398c75`, 2026-10-01) — findings ROUTED (protocol step 7)

The warden confirmed the diff matches the foreman's description (4 files).
- **Clean [R]:**
  - no live surface asserts `-2025` or "unbroken";
  - all OWASP prose says 2026;
  - all 2.11.0 version strings agree;
  - the concept DOI is consistent;
  - the drift check is clean (run against a `git archive` extract).

| # | Sev | Where | Finding | Owner |
|---|---|---|---|---|
| 1 | HIGH | `CHANGELOG.md` (no `[Unreleased]`) | **Nothing discloses the live STIX/TAXII `source_name` relabel, or the re-import instruction.** This is the D32 notice that is owed. | WS6 (the timing is the user's call) |
| 2 | MED | `docs/releases/v2.11.0.md` 197-215 | "Consumer impact, stated without hedging" is now incomplete for STIX consumers. It is a dated record, so it needs a **dated addendum** with a do-not-regenerate marker, not a rewrite (agreement 4). | WS6 |
| 3 | MED | README:18, DATASHEET:115, DATA_DICTIONARY:205; the `export_taxii.py` README template | No surface documents that the STIX OWASP `source_name` is edition-qualified (`owasp-llm-top10-2026`). | WS6 docs + WS4 `export_taxii.py` |
| 4 | LOW | `docs/taxii2/README.md` | Generated at deploy and not in git, so it cannot be audited from the repo. Its text makes no edition claim. | — |
| 5 | LOW | README:88-95 file tree | Lists only `owasp_llm_top10_2025.json`. **Already fixed in README PR #100** (`426ed817`/`3be697c4` add the 2026 file and the crosswalk). | — via PR #100 |
| 6 | INFO | `export_stix.py:39-47` | The docstring calls the crosswalk "the single source of truth" for the edition. It is scoped to one field, so acceptable; reword if zero tolerance is wanted. | WS4 |

## 🛰 STIX OWASP-edition fix — **MERGED to main `7dc80602` and LIVE (2026-10-01)** · D32 post-cut step 1 done

**Merge.** `ws6/stix-owasp-edition-and-site-fixes` (`a2be3364`, gate PASS, board `70e72155`) was merged `--no-ff` onto post-cut main.
- **The merged tree was re-verified [R], not inherited from the gate:**
  - merge-tree is clean, and no branch file changed on main since the branch base `528d5936`;
  - pytest is **476 passed, 1 xfailed** (v2.11.0's 475 plus the new STIX test);
  - a bundle rebuilt from the merged tree has **17,750 `-2026` labels and 0 `-2025`**, equal to an independent Σ len(owasp_llm) = 17,750; 54,485 objects, unchanged.
- **Live verification [R], after the Pages run `36870624095` succeeded:**
  - the live STIX bundle has 17,750/17,750 `owasp-llm-top10-2026`, with 54,485 objects;
  - the live TAXII collection `05bbe2e9…/objects.json` is the same, 17,750/17,750;
  - the live `app.js` serves the "Years with entries" tile.

**⚠ The disclosure is owed in the next release notes (D32).** The corrective relabel is now public with no notice until the next release. The notes must state the `source_name` change and tell **STIX consumers to re-import**: SDO `id` and `modified` are unchanged, so (id, modified) dedupe such as OpenCTI's will not pick it up (gate advisory A3). The foreman offered the user an immediate CHANGELOG `[Unreleased]` entry; that is pending the user's answer.

**Next (D32):** docs-warden on the site text change, then the README PR #100 rebase (keep the `50e42bbe` README:71 text).

## 🎉 v2.11.0 PUBLISHED 2026-10-01 — all nine VERSIONING.md steps done and independently verified

| Step | Result | Evidence [R] |
|---|---|---|
| Merge | `release/v2.11.0-cut` → main as **`632f227b`** | The tree equals the gated `50e42bbe` except PROGRESS.md (`git diff --quiet`) |
| 6 Tag | **`v2.11.0` → `632f227b`** (annotated) | `git ls-remote --tags origin` shows `^{}` = `632f227b`. **No secret-scanning block** |
| 7 Release | [published](https://github.com/emmanuelgjr/genai_incidents/releases/tag/v2.11.0) 06:17:47Z, isDraft=false, not a prerelease | Body byte-identical to `docs/releases/v2.11.0.md` (normalized for gh's trailing newline) |
| 8 Zenodo | **Version DOI `10.5281/zenodo.23076162`** | doi.org returns 302. The API record shows version 2.11.0, 2026-10-01, under concept `10.5281/zenodo.20248675`, linked to the repo |
| 8b DOI sync | Notes paragraph filled (WS6, `7af549db`, fast-forwarded to main); Release body re-synced | Re-verified byte-identical; the DOI is present in the published body |
| 9 PyPI | `publish.yml`, event=release, headBranch=v2.11.0: **success** | **pypi.org JSON: latest 2.11.0**, with wheel and sdist |
| 9 HF | `huggingface.yml`, event=release, headBranch=v2.11.0: **success** | The dataset card reads "Dataset version `2.11.0`"; lastModified 06:18:08Z |

**Gate trail for this release:**
- notes: B#1 → B#2 (D33/D34) → D35 → B#3 (D36) → B#4 (D37) → PASS `c9ff5b49`;
- WS4-T22: B#1 → PASS `934a6348`;
- cut: B#1 → PASS `50e42bbe`.
**The foreman's premises were refuted 5 times** (D33 "delivery gap", "old targets still live", "audit title = independent", the D36 dictated wording, "8 ambiguous by design"). Each was caught by a specialist or a gate.

**Post-cut queue (D32 order):**
1. Merge `ws6/stix-owasp-edition-and-site-fixes` (`a2be3364`, PASS). Its notes must tell STIX consumers to **re-import** ((id, modified) unchanged).
2. docs-warden, because the site's Years-tile text changes.
3. Rebase README PR #100. **Hand-resolve README:71 so it keeps the `50e42bbe` v2.11.0 text.**

**Follow-ups:**
- D35: narrow D28 for 03128→14909 and 08185→14742 (WS4, gated).
- Package/validator null-`into` parity (WS4+WS3).
- STIX edition test independence (WS6 A1).
- VERSIONING.md: step-2 UA scope is stale, and the step-3 script should use `tier`.
- **A mechanical check for the step-5 failure shape.** Three cuts in a row shipped a stale "Latest release" paragraph next to a correct marker.
- ID_POLICY §3 / D31 rider (WS3).
- 2 high Dependabot alerts.

## 🛰 WS6 STIX OWASP-edition + site fixes — **✅ PASS (red-reviewer, 2026-09-30, on `a2be3364`) — NO DEFECTS — merge QUEUED behind the v2.11.0 cut per D32**

**Branch** `ws6/stix-owasp-edition-and-site-fixes` @ `a2be3364` (base `528d5936`). 4 files, +34/−3, all in scope. Foreman stray check: `git status --porcelain` is empty, and the SHA is confirmed on origin.

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: PASS … No defects against the acceptance criteria."* The gate worked in two throwaway clones and confirmed the main-tree HEAD unchanged before and after.

**Evidence the gate measured, all [R]:**
- **Failing-first.** The branch test on the base code gives `1 failed, 7 passed`. On the branch, the full suite gives `460 passed, 1 xfailed`. `check_stats_drift` is clean.
- **Delta, by a different route from the specialist's.** One `sed` substitution of `-2025`→`-2026` on the base bundle makes it **byte-identical** to the branch bundle (`cmp`; both 61,215,761 B, 54,485 objects). The `--numstat` diff is 17,750/17,750. **An independent count of Σ len(owasp_llm) over 13,361 incidents gives 17,750.**
- **Other surfaces.** In TAXII only `objects.json` changes (the same 17,750 lines); manifest and discovery are unchanged. **MISP is byte-identical** (86,784 attributes). Two runs give the same sha256, so the build is deterministic.
- **Edition anchored on sources the fix does not read.** These all say 2026: the corpus metadata description, `owasp_llm_top10_2025.json` `superseded_by`, `data/.owasp_llm_migration.json` (applied 2026-08-17), and CHANGELOG [2.10.0].
- **Years tile.** The rendered text reads "31 / YEARS WITH ENTRIES / of 44 in 1983–2026" (13 empty years confirmed), with no hardcoded number.
- **Table.** `.table-wrap` scroll/client at 1440, 1280 and 1024 now fits exactly, against base overflow of 1316. At 900 there is a 6 px residual. At 640 px and below the columns are hidden by the existing rule, so mobile is unaffected.
- **a11y.** axe gives **0 violations on base and branch** (two URLs, two viewports, both themes). The 380 px check passes. Lighthouse accessibility is 100.

**Advisories, routed:**
- **A1 (→ WS6, new follow-up).** The test checks the fix against its own source (agreement 6 form (b)). Both the exporter and the test read the fixed filename `owasp_llm_2025_to_2026.json`, so a 2027 migration would leave both saying 2026 and the test green. Fix: anchor on the newest applied entry in `data/.owasp_llm_migration.json` or the end of the `superseded_by` chain, and have the exporter resolve the current catalog the same way.
- **A2.** The specialist's axe claim was **not reproduced**: 0 violations on both trees. See the dated correction under D32.
- **A3 (→ user/WS3+WS6, schema/versioning call).** The 17,750 SDOs change content with the same `id` and `modified`, because `modified` derives from entry dates. STIX consumers that dedupe on (id, modified), such as OpenCTI, may never pick up the corrected label. **The post-cut release notes must tell STIX consumers to re-import**, or a `modified`-bump policy must be decided.
- **A4.** A 6 px residual horizontal scroll remains at 641–900 px. This is polish, not a regression.
- **A5.** `x_owasp_llm_edition` is a schema decision and was correctly not added.

**Published surfaces on merge (for the post-cut notes):**
- These change: STIX bundle, TAXII `objects.json`, `docs/data/SHA256SUMS` (STIX line), the Years tile, and the LLM/ASI CSS.
- These do not: MISP, PyPI, HF, and every `data/*.json`.

## ⚖ D32 — USER RULING, 2026-09-30: the STIX OWASP-edition fix ships AFTER the v2.11.0 cut, not in it

**Ruling:** `ws6/stix-owasp-edition-and-site-fixes` (`a2be3364`) does **not** fold into v2.11.0. The v2.11.0 scope and sequencing (D30/D31) are unchanged.

**Why it mattered:** Pages rebuilds STIX/TAXII and the site on any `main` push that touches `scripts/export_stix.py` or `docs/**`. Merging before the cut would change 17,750 published `source_name` values under an unchanged version label, which is the D30 root-cause class.

**Consequences:**
- Merge after the cut, and only on a gate PASS. The red-reviewer gate was dispatched 2026-09-30 and its verdict is pending.
- The next release's notes must disclose the corrective relabel: STIX `source_name` `owasp-llm-top10-2025` becomes `-2026` on every OWASP-LLM reference. That is a corrective break for any consumer keying on the old string.
- PR #100 (README) is also queued after the cut.
- **Post-cut merge order: v2.11.0 cut → this fix branch → rebase PR #100** onto the corrected "Latest release" paragraph.

**Also found by the specialist (unrouted, pre-existing):** axe reports 1 serious `aria-prohibited-attr` at 1280px and 380px on **unmodified main**. The site's a11y gate may be red on `main` today. It is outside this task's scope, and the owner is WS6. It is pending the gate's own confirmation.

> **Update 2026-09-30, red-reviewer (the "found by the specialist" half is superseded; the ruling half stands):** the gate re-ran axe on base `528d5936` and branch `a2be3364` across both URLs, both viewports and both themes, and measured **0 violations on both**. The specialist's `aria-prohibited-attr` was **testimony that a re-run contradicts**. It is **not** a known violation on `main`, and nothing is routed. *Dated record; do not regenerate the paragraph above.*

## 🖼 2026-09-30 — README refresh (PR #100, DRAFT, held for v2.11.0) · three defects found while building it, routed to WS6

**User request, ad hoc (not a plan task):** make the README more appealing, then add images. The foreman implemented it directly on `docs/readme-refresh` (`8e23d6e6`). It is presentation only: licensing, citation, caveat and release prose is carried verbatim, counts stay inside `stats:` markers, and **no image carries a corpus count**. The site screenshot was cropped to keep the total out, and the image generators are in `scripts/readme_assets/`. `check_stats_drift` is clean and was shown to fire on a corrupted marker. docs-warden ran one pass with 12 findings; the 8 actionable ones were fixed in `426ed817`.

**⛔ PR #100 is HELD until after the v2.11.0 cut.** `git merge-tree` shows a `README.md` conflict with `release/v2.11.0-notes` (`2f7bba1d`): both rewrite "Latest release". The D30/D31 sequencing must not be reordered.
- **Docs-warden miss, form (b) of agreement 6.** It called the "exactly one corpus row changed / refresh frozen" paragraph "accurate today". It verified the paragraph against the v2.10.0 notes, the same source the paragraph came from. That paragraph is the Critical stale claim the D30 sweep already found.
- **After the cut:** rebase #100 and take the corrected paragraph into its callout.

**Defects found (foreman, 2026-09-30), dispatched to distribution-engineer, worktree branch `ws6/stix-owasp-edition-and-site-fixes`, NO MERGE until the user rules on timing:**
1. **HIGH, live.** `scripts/export_stix.py:128` labels every `owasp_llm` external_reference `owasp-llm-top10-2025`, but codes are the 2026 edition since v2.10.0. The live bundle has 17,750 such refs. A STIX/TAXII consumer reads `LLM03` as *Supply Chain*, not *Excessive Agency*. This is the **E24 class surviving in one exporter**: the v2.10.0 migration relabelled the data but not this export's edition string, and no check covered it.
   - **Merge-timing question for the user:** Pages rebuilds STIX on exporter pushes. Merging before the cut changes a published surface under an unchanged version label (the D30 root-cause class) unless the v2.11.0 notes disclose it.
2. **MEDIUM, false site claim.** `docs/app.js:293` shows "31 YEARS — unbroken since 1983". That is 31 distinct years over a 44-year span, so it is not unbroken.
3. **LOW.** The site table's ASI column overflows on long code lists (INC-00924 renders "ASI0" cut off).

Acceptance given to WS6: a test that fails on the old code, run first; a field-level STIX before/after delta where only that `source_name` moves; a full pytest count; branch confirmed on origin. **red-reviewer gates on return.**

## 🎉 D28 REMEDIATION MERGED 2026-09-20 (`8f74b035`) — **THE CORPUS IS UNFROZEN** · and ⚖ D30: cut **v2.11.0**

**Published state on origin:** `incident_count` **13,361** · `landmark_count` **1,915** · `generated` **2026-09-18** · deprecations **1,060 records over 1,056 distinct `from` IDs**. **Four** IDs were retired under D28's authorization (`reason: "split"`); **five** IDs in total stopped resolving to themselves, the fifth being `INC-07738` via an ordinary `merged` tombstone into `INC-14757`. Both figures are true and they answer different questions — see the dated correction below. **The count had not moved since 2026-07-27.**

**PASS (red-reviewer, 2026-09-20, on `a997ca57`) after four bounces — each with a different and progressively smaller cause, and none of the last three about the corpus.** Bounce 1: four inbound redirects landing wrong, three of them a fresh regression. Bounce 2: the committed regression test the user's ruling required was missing — proved by repointing a real record and watching `validate.py` exit 0 and 418 tests pass on a corpus carrying the defect. Bounce 3 (foreman-found): a comment asserting the very claim bounce 1 falsified, plus a duplicated chain-resolver. Bounce 4: **the merge itself produced a red `main`** — found only because the gate performed the merge rather than reading the diff.

**Why the remediation existed, in the gate's own example:** with the over-merge fix alone, `INC-00311`'s military-targeting incident inherited a **Greek tax authority AI** story and `INC-00754`'s ChatGPT case inherited a **Jason Momoa deepfake scam** — the query-string bug had absorbed unrelated incidents, and the smallest-ID tie-break handed the published ID to whichever row won mechanically.

**The `landmark_count` movement, decomposed per entity — this is what made it safe to publish:** **−2** retired landmark rows, **+12** new landmark rows among the 306 new IDs, **+0 / −0** existing rows flipped in either direction. **Zero existing rows changed tier.** Entirely a consequence of the authorized split, not a re-classification.

**Two checks proved themselves at the moment they were built for:**
- **WS6-T9's self-disarming tripwire fired on exactly this rebuild.** Its marker read *"Rebuilding populates `tier` and turns this XPASS → delete this marker then"*; its docstring, *"The gate disarms itself; nobody has to remember."* The remediation was that rebuild. The markers were deleted **with a dated note recording that it fired correctly**, rather than silently. The gate then broke the now-unmarked tests **six ways** and confirmed they discriminate: flipping every landmark→feed fails *only* the count test, and stripping `tier` from one variant fails *only* that variant's case.
- **The deliberate barrier this project never had now exists:** a build-time guard aborting before any write when a previously-single published ID would newly resolve to more than one row unless authorized by a list carrying the D28 marker. **23 attack shapes, all abort**, including tamper-plus-recompute — closed by pinning the expected hash in code. **File presence authorizes nothing.**

**⚖ D30 — USER RULING, 2026-09-20: cut `v2.11.0`.** A minor bump: `tier` newly ships in the distributed variants (a schema-field addition) and the corpus gained 301 rows with four permanent retirements. **Root cause the docs sweep identified: the cut checklist was never run for this merge** — `main` carried the new corpus while every version string still read 2.10.0, and the `v2.10.0` tag points at 13,060 rows with zero retirements. **Published data changed materially under an unchanged label — the E24 defect class, recurring.**

**Docs sweep findings, routed:** README's "exactly one corpus row changed / refresh frozen" prose (Critical, live surface, correct in place) · no CHANGELOG entry for a 301-row change (Critical) · `DATA_DICTIONARY`'s "slim artifacts do not carry `tier` yet" (High, now false) · `v2.10.0.md` owed a **superseding dated note**, not an edit, since it is a dated record (Medium) · **`ID_POLICY.md`'s headroom table is stale input to the open WS3-T5 ruling** — measured 2026-07-27, states 992 deprecations against the actual **1,060**, and this remediation allocated ~306 new IDs (Medium, routed to schema-architect).

**The sweep also recorded what it verified CLEAN, re-derived rather than re-read** — AIAAIC attribution counts exact at 1,422/1,517, six-taxonomy language consistent, no banned "TAXII endpoint" phrasing, HF card templated rather than hardcoded. Recording a clean result stops the next sweep re-checking it.


### ⛔ v2.11.0 RELEASE NOTES — BOUNCE #1 (red-reviewer, 2026-09-20, on `2f7bba1d`) — **the cut is held**

**Every headline figure re-derived exactly [R]** — by diffing the `v2.10.0` tag blob (`0c778ced`) against `2f7bba1d`, a different route from the one that produced them. 13,060→13,361 (+301) · 306 added / 5 removed, sum exact · the five IDs by name · landmark 1,905→1,915 with **−2 named per-entity** (`INC-00554`, `INC-00754`), **+12** new, **0 flips in either direction** · `INC-07738` was `feed` · 1,051→1,060 records over 1,056 distinct `from` · the four dual-tombstone IDs by name, with **0 such IDs at v2.10.0**, so "first time in the file's history" holds · **append-only proved structurally: the old 1,051 records are an exact byte-prefix of the new 1,060** · `tier` in all three slim variants, 13,361 rows each, landmark 1,915 each · pinned hash = list `entries_sha256`, independently recomputed · 55 = 43 keep_id + 4 retire + 8 resplit_redirect · **459 passed, 1 xfailed** · drift clean. **All three of today's late corrections confirmed correct**, and the gate independently reproduced the **13** by two routes (their `-k` selection, and a parse attributing guard-symbol references to enclosing test functions), including the 9/4 split — 9 `split_guard_*` of which **7 assert abort and 2 assert no-fire**.

**The gate corrected my brief's repo-state premise** — it assumed the shared tree was on the release branch; it is on `ws4/t10-normalize-url`. The gate worked in a throwaway clone, moved no HEAD, and checked `git symbolic-ref -q HEAD` at both ends. **That is the same branch-confusion condition that stranded eight board commits this session** (agreement 1b), caught here by a reviewer's own hygiene rather than by the foreman.

**DEFECT 1 — the central consumer promise is false as written, and strips a hedge off the source it cites.** In 4 of 5 changed files (`docs/releases/v2.11.0.md`, `CHANGELOG.md`, `README.md:71`, and the new dated note in `docs/releases/v2.10.0.md`), new text asserts the universal *"No citation of any ID this project has published ever breaks"* — and the v2.11.0 notes add *"This is not a softened claim — it is the promise `docs/ID_POLICY.md` makes."*

- **`docs/ID_POLICY.md:271-275` does not make that claim unqualified.** The same sentence carries a parenthetical carve-out: *"(Current compliance: 9 known exceptions — see §1.4(a) — to be repaired in Phase 2.)"*, and §1.4(a) calls them **"a live violation of the 'merged IDs redirect forever' rule."**
- **The nine counterexamples, named:** `INC-00522`, `INC-00609`, `INC-00951`, `INC-00952`, `INC-00955`, `INC-00956`, `INC-00957`, `INC-01355`, `INC-01660` — published in `v2.0.0`, gone in `v2.1.0`, in **neither** `incidents.json` nor `id_deprecations.json`. Gate probed all nine on `2f7bba1d`: **nine for nine** not live, no tombstone, `resolve_id → None`, `resolve_id_group → []`. Resolving to silence, the one outcome §3 forbids.
- **Two errors, not one:** asserting the strong form, *and* attributing the strong form to a source that states the weak form.
- **Routing — the fix is to the WORDING, not the data.** Nothing this release did is wrong; the nine predate the tombstone machinery (2026-05-16), are already documented, and are already Phase-2 work. Appending nine records would also make the sentence true but **must not be smuggled into a release-notes task**. Remedy: scope the claim to every ID **that carries a tombstone** — still strong, and true — and name §1.4(a)'s nine as the known pre-existing exception, restoring the hedge.
- This is **D13 rider (b)** — the nine dangling v2.0.0 IDs — surfacing as a consumer-facing claim. It was already boarded as open work with no owner.

**DEFECT 2 — the notes tell consumers to re-resolve but never say how, and the resolver this release ships returns `None` for 12 of the IDs it touched.** `docs/releases/v2.11.0.md`, "Consumer impact, stated without hedging", final paragraph:

> **Anyone joining or diffing on incident IDs across versions must re-resolve through `data/id_deprecations.json`** — an ID that was valid and singular in `v2.10.0` may now be a retirement record pointing at up to 100 successor rows (`INC-00554`'s case), and a naive join on the literal ID string will silently under-count or mis-attribute.

Three failures:
1. **Omits the API.** This release ships to PyPI. The package a v2.10.0 consumer holds exposes one resolver, `resolve_id()`, which now returns `None` for 12 IDs — **including all four this very section names by hand.** The document never names `resolve_id_group()`, never says `resolve_id()` declines multi-successor records by design, never flags that four of those returns are a **bug** rather than design, and never notes that `resolve_id_group()` **does not exist in the release the reader is migrating from.**
2. **Narrower than the truth, in the reassuring direction — the worst direction.** "An ID that was valid and singular in v2.10.0 may now be a retirement record" covers **only the four retirements**. The eight further IDs — `INC-00497`, `INC-03128`, `INC-07771`, `INC-08109`, `INC-08133`, `INC-08139`, `INC-08146`, `INC-08185` — were **already tombstones, already resolving correctly, and went silent.** They appear in **no** disclosure surface: not the notes, CHANGELOG, README paragraph, or v2.10.0 dated note. **A consumer auditing their ID list against this disclosure clears all eight as unaffected.** That is the line between a document that is incomplete and one that actively misleads.
3. **Collides with the promise.** Two paragraphs after *"No citation of any ID this project has published ever breaks"*, it instructs the reader to re-resolve — and **the only tool they have returns `None`.**

Remedy (three sentences, no code changes beyond D31's): name `resolve_id_group()`, state `resolve_id()` declines multi-successor records by design, and state that reading `data/id_deprecations.json` directly is the path that works **without upgrading** · disclose that **12** previously-resolving IDs now return `None`, **naming the eight not named elsewhere**, and that all 12 resolve correctly through the file or `resolve_id_group()` · per D31, state the four single-successor cases are **fixed in this release**, not folded into the by-design set, **because the docstring's rationale is false for them.**

**Defects 1 and 2 converge rather than duplicating:** defect 1 is a promise too strong for the data; defect 2 is an instruction the shipped tool cannot carry out. Both are fixed by the same passage, and fixing either alone leaves the document self-contradictory.

**ADVISORIES 1–4** (5 and 6 held by forward-reference: Phase-2 ghost repair stays out of a notes task; the resolver fix needs its regression test):

**A1 — ⚠ the sharpest of the four: supersession correctness depends on file ORDER, not on `date`.** `src/genai_incidents/__init__.py:61-65` — `_load_deprecations()` does `out[f] = t` in file order, so **last record wins**. Today that is correct and verified per-entity. **The hazard: `INC-07771`'s superseded target `INC-01271` is still live**, so a first-wins loader, or a record appended out of date order, would return a **plausible, live, WRONG ID** and pass every existing check in silence — not a crash, not a `None`, a believable wrong incident. **Agreement 6 form (d) in waiting.** Guarded today only by `test_deprecations_file_order_is_never_resorted_even_with_date_inversions` — **an order invariant standing in for a correctness property nobody has ever stated.** → **Routed live into `ws4-resolve-id-fix`'s brief**: state the rule in code, test it directly with a two-live-target fixture in both orders, and prove it fires by flipping the loader. Explicitly **not** authorized to change the storage shape (no `supersedes` field, no date sort) — invariant 9 makes it append-only. Also worth a sentence at the mechanism in `docs/ID_POLICY.md` (→ WS3).

**A2 — `docs/releases/v2.10.0.md` passes agreement 4's verbatim half exactly and misses the other half.** The diff is a **single 24-line pure `insert` at line 187 — zero deletes, zero replaces** — so the original §1 survives byte-for-byte beneath the dated note. But it carries **no literal do-not-regenerate marker**, which agreement 4 itself names as the load-bearing part. A dated release note is exactly the artifact a future pass mistakes for a source. → notes-fix brief.

**A3 — the Zenodo paragraph declares an in-place edit to a dated record.** `docs/releases/v2.11.0.md` says the DOI paragraph "is edited in place and the published Release body re-synced to match it (step 8b)" at redeposit. **Correctly declared and effectively unavoidable** — a release body must carry a resolvable DOI — but it is a live-surface correction inside a record artifact and should be flagged rather than pass unremarked.

**A4 — the STIX `x_tier` row is the only claim in the document not inspectable from a committed artifact. [A]** `data/incidents.stix.json` is gitignored as a generated artifact (`.gitignore:52-55`), so the cell rests on `scripts/export_stix.py:149` plus `tests/test_landmark_distribution.py::test_stix_sdo_carries_x_tier`. Adequate coverage, but **attested, not re-derived — the single [A] in this review**, and the one row a phase-exit checklist could not mark met on this evidence alone (agreement 5).

**The cut stays held.** The verdict truncated in transit **five times**; both defects and these advisories had to be extracted by asking for each in isolation. **Process note for future gates: a long verdict is a durability risk, not just an inconvenience** — the defects are the only actionable part and they were last in the message every time.

**⚠ FOREMAN FINDING, independently measured [R], sent to the gate for adjudication — `resolve_id()` returns silence for 8 of the 9 IDs this release touched.** Measured against the shipped package on `origin/main` @ `4861afd7`: the four **split** IDs and the four **dual-tombstone** IDs all return `None`; only `INC-07738` resolves (`→ INC-14757`). **`resolve_id_group()` resolves all nine correctly, so the data is sound — the single-successor accessor is what breaks.** Two sub-cases with different severities:
- **(a) The four split IDs look like design** — 100 successors has no single canonical answer, and the docstring redirects callers to `resolve_id_group`. If so the gap is a **missing migration instruction** in the notes, likely part of defect 1's remedy.
- **(b) The four dual-tombstone IDs look like a genuine behavioural regression in code.** Their `resplit` record's `into` is a list of **exactly one element** — an unambiguous successor exists — but `resolve_id` bails on `isinstance(current, list)` **before testing length** and returns `None`, where v2.10.0 returned a usable single ID. If confirmed, **defect 1's "this release introduces zero new breaks" is too generous** and the remedy is not purely editorial. **Open — the gate was asked to take its own route and to say plainly if the foreman has this wrong.**

## ✅ v2.11.0 CUT — **PASS (red-reviewer, narrow re-gate, 2026-10-01, on `50e42bbe`) — GO for steps 6–9 — MERGED to main**

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: PASS … All three BOUNCE #1 defects are closed, and every sentence I checked is true. GO for steps 6–9."*

**Evidence [R]:**
- `data`/`src`/`scripts` are unchanged from the cleared `be559587` (0 bytes of diff).
- Every figure and ID in README:71's v2.11.0 part matches the gated notes, item by item.
- The v2.10.0 part matches `docs/releases/v2.10.0.md`. "Roughly eight times" was **re-derived on v2.11.0 data: 6,162 / 783 = 7.87**.
- There are no orphaned referents. Dropping the OECD-freeze sentence loses nothing, because the notes and CHANGELOG still record that state.
- The drift check is clean and **was shown to fire** (exit 1 on the 2.10.0 marker).
- pytest 475/1.
- The release body has 0 anchors and 0 relative links, with the grep validated against README's 44 relative links.
- The step-5 sweep is clean on live surfaces.
- merge-tree is clean, and main moved only through board commits.

**Advisory 1 (README on PyPI): already settled by D32.** README PR #100 is queued after the cut, so v2.11.0's PyPI long_description is the gated cut-branch README. **When #100 merges, hand-resolve README:71 so it keeps the `50e42bbe` text**, or the BOUNCE #1 defect-2 wording can come back through the conflict.

Advisories 2–3: README:71 "still resolves" can be read two ways but is accurate; "eight weeks" versus "eight consecutive runs" is consistent.

**Merged:** `release/v2.11.0-cut` → `main` as `632f227b`. **The merge commit is the v2.11.0 tag target.** Step 6 (tag) follows.

### ⛔ v2.11.0 CUT — **BOUNCE #1 (red-reviewer, pre-publish gate, 2026-10-01, on `be559587`)** — step-5 prose only; the data is fully clean; re-dispatched to WS6

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … The data, the version strings, the resolver, the tests and the secret scan are all clean … The bounce is about step-5 prose only."*

**DEFECTS:**
1. **HIGH: `CHANGELOG.md:8-11`.** The header still reads "gated pre-cut", and the body says "a release gated but not yet cut … Version strings still read 2.10.0". The cut did not touch CHANGELOG. Precedent: v2.10.0's cut `0c778ced` set its header to `## [2.10.0] — 2026-09-18`.
2. **HIGH: `README.md:71`.** "2.11.0 — released 2026-10-01" now heads v2.10.0's paragraph, crediting v2.11.0 with the OWASP migration and the refresh fixes; "The v2.10.0 notes above" points nowhere. **This is the third cut in a row with this exact step-5 failure shape** (v2.9.0, v2.10.0, v2.11.0).
3. **LOW: `docs/releases/v2.11.0.md:392-393`.** "every version string … still reads 2.10.0 as of this writing" is inconsistent with the re-tensed banner.

**Evidence that the data is clean [R]:**
- **Two routes:** per-ID canonical-JSON sha256 shows 0 differences across all 4 incident files (fire-tested), and each file differs by **exactly one byte** ("0" becoming "1").
- `id_deprecations` is byte-identical (both copies).
- **A rebuild reproduces the committed outputs byte for byte, and is deterministic over 2 runs.**
- The built **wheel** reports `metadata.version` 2.11.0, and the resolver gives 13/13. The behaviour hash `87cd5547…` is identical for the wheel and for base src, and was fire-tested.
- pytest 475/1. The drift check is clean and was fire-tested.
- merge-tree is clean.
- **Secret scan: 0 hits in data**; the only hits are prose mentions already on main.

**Advisories:**
- **A1.** PR #100's branch is based on stale `528d5936` and conflicts in README. Rebase after the cut, per D32. Local `main` is also behind.
- **A2.** `docs/releases/v2.10.0.md:222` "gated as v2.11.0" is a dated record; consider a dated one-line update after the cut.
- **A3.** Cosmetic line wrap at `v2.11.0.md:9`.

**Route:** a prose-only WS6 pass on `release/v2.11.0-cut`. README:71 rewords gated text, so it goes through the D36/D37 narrow-gate path, and the lesson applies: the specialist DERIVES the wording from the gated notes; the foreman does not dictate it. Then a narrow gate, then steps 6–9.

## 🚀 v2.11.0 CUT — VERSIONING.md steps 2–5 delivered on `release/v2.11.0-cut` @ `be559587` (pushed) — **pre-publish gate in flight**

- **Step 2a, WS4 (`f341ecd5`).** `USER_AGENT` is now `genai_incidents/2.11.0`, and the current-UA literal plus the version cross-reference in INGESTION_CONDUCT.md were updated to match. The historical 2.8.0 quotes are untouched.
- **Step 2b, WS6 (`be559587`).** `merge_and_dedupe` `out["version"]`, pyproject, CITATION.cff (version, preferred-citation.version, `date-released` 2026-10-01) and .zenodo.json are all at 2.11.0.
- **Step 3, specialist-reported.** The full build ran (parse, merge, render, render-docs-stats, validate: 13361/13361 valid). `top_diff` = {version}. The ID set is equal at 13,361, 0 entries changed, landmark (`tier`) is 1,915, `generated` did not move, and `id_deprecations.json` is byte-identical. The 3 min.json copies read 2.11.0. The resolver spot-check gives 13/13 as expected.
- **Step 4.** The drift check is clean, and INCIDENTS.md reads Version 2.11.0.
- **Step 5.** Four prose edits:
  - README "released 2026-10-01";
  - README "was cut as v2.11.0 on 2026-10-01";
  - two tense edits in the notes banner.
- pytest `475 passed, 1 xfailed`.
- **Foreman pre-checks:**
  - The release body is 34,147 B, with 0 in-body anchors and 0 relative links.
  - No `v2.11.0` tag or Release exists on origin.
  - The PyPI metadata-2.5 failure from the v2.10.0 cut is fixed on main (`71c8ad6c`).
- **Follow-ups (post-cut, WS6):** VERSIONING.md step 2's UA-scope text is stale and quotes 2.9.0, and its step-3 script should use `tier == "landmark"`. `genai_incidents.VERSION` = 2.0.0 is the schema version, not a release string (WS6-T1).

## ✅ v2.11.0 NOTES — **PASS (red-reviewer, D37 string-check gate, 2026-10-01, on `c9ff5b49`) — NO DEFECTS — MERGED to `main`** · the cut proceeds (VERSIONING.md steps 2–9)

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: PASS … all 4 checks met on `release/v2.11.0-notes` @ c9ff5b49."*

**Evidence [R]:**
- The diff is exactly 2 lines in 2 files, checked byte-level (U+2014).
- README:33 matches verbatim.
- **The claim is true by the gate's own redirect walker over the raw JSON, not the package's:**
  - exactly 8 deprecated IDs have more than one live leaf, with sizes 12/12/100/11/8/11/100/100;
  - the package's `resolve_id` returns None for 771, of which 763 are terminations with empty groups, leaving the 8;
  - "three reasons" matches README:71 and the notes' A/B/C sections.
- The v2.10.0.md:188 marker matches, and the file is still 41/0.
- `475 passed, 1 xfailed`; the drift check is clean; merge-tree is clean.

**Release-branch gate history:**
- notes BOUNCE #1 (`2f7bba1d`);
- WS4-T22 BOUNCE #1 (`af9601fa`), then PASS (`934a6348`);
- notes BOUNCE #2 (`1977515e`), which produced D33/D34; WS4-T23 refuted D33's premise, which produced D35;
- BOUNCE #3 (`d27bcae2`), which produced D36;
- BOUNCE #4 (`59dd995b`), caused by wording the foreman supplied in the brief, which produced D37;
- **PASS (`c9ff5b49`)**.

**Merged** into `main` as a `--no-ff` merge commit (this push). **Next is VERSIONING.md step 2:** WS4 bumps `USER_AGENT` plus its INGESTION_CONDUCT literal, then WS6 bumps the other four strings and builds. The step-3 field-level expectations are recorded under BOUNCE #3.

## ⚖ D37 — USER RULING, 2026-10-01, on BOUNCE #4: **apply the gate-verified text verbatim, then a string-check gate**

- A specialist inserts the gate's exact README:33 sentence and its A1 marker wording, **verbatim, with no new wording**.
- A short gate confirms only that the two strings match exactly, that nothing else in the diff moved, and that pytest and the drift check still pass.
- **On PASS, the cut starts.**

### ⛔ v2.11.0 — **D36 narrow gate: BOUNCE #4 (red-reviewer, 2026-10-01, on `59dd995b`) — ESCALATED TO USER** · one clause on one line

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … Only one wording defect is left: one clause on one line. Nothing else is wrong."*

**DEFECT 1.** The new README:33 says `resolve_id()` returns None for "8 IDs whose record lists more than one successor".
- Only the 4 retirements have such a record.
- 00497, 03128, 08139 and 08185 each have a single-successor `merged` record whose **chain ends** in a retired split. `load_deprecations()` gives `str` for them.
- This is the same 4 IDs as BOUNCE #3. **The foreman's D36 brief supplied the wrong wording, and the specialist used it.**
- The line ships as the PyPI page (`pyproject.toml:9`).
- **Gate-verified replacement [R]:** "`resolve_id()` returns `None` for 8 IDs whose redirect chain ends in more than one live successor, for three different reasons — see the v2.11.0 release notes". All 8 have group sizes of 8–100, and they are exactly the 8 deprecated IDs that return None.

**Evidence that the rest is clean [R]:**
- The docstring sentence is TRUE: all 12 tags' `query()` lack `tier`, and `git tag --contains 4c09dcb1` is empty.
- The paper is correctly classified as a live document.
- The marker is relabelled.
- The docstring-stripped AST is equal, so there is no code change.
- The behaviour hash is **`c322f3fa…` on both trees, and it was proved to fire** (one monkeypatched answer gives `b7bda274…`).
- `475 passed, 1 xfailed`; the drift check is clean; the dated note is 41/0.
- merge-tree is clean, and the version strings are still 2.10.0.

**Advisory A1.** The marker's "revised … before publication; added post-publication" uses "publication" for two different events. The gate suggests "added 2026-09-18 after v2.10.0's publication; revised 2026-10-01 before this note was published".

## ⚖ D36 — USER RULING, 2026-10-01, on BOUNCE #3: **narrow fix + narrow gate, then cut**

**One WS6 specialist pass.** Under this ruling it is authorized to make **the docstring-only** `src/` edit. It edits exactly these:
- README:33 (drop "by design" for all 8 and point to the per-ID breakdown);
- the false `query()` docstring sentence, plus the hardcoded 1,915 (A1);
- the dated-note marker label (A3);
- `docs/paper/genai-incidents-methods.md:74`, the unscoped "citations always resolve" (A4).

**Then a gate limited to that diff:**
- re-run the suite;
- the behaviour hash `c322f3fa…` (proves no behaviour change);
- the drift check;
- a surface sweep for "by design" / "would match nothing" / unscoped resolution claims.

**On PASS → the cut** (VERSIONING.md steps 2–9). A2, the DATA_DICTIONARY:9 lead-in and ID_POLICY §3 stay as follow-ups.

### ⛔⛔⛔ v2.11.0 RELEASE NOTES — **BOUNCE #3 (red-reviewer, 2026-10-01, on `d27bcae2`) — ESCALATED TO USER** · two wording defects, about 2 lines, no data or behaviour change

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … Both defects are wording only, about 2 lines in total. No data change and no behaviour change is needed. Everything else re-derives exactly."*

**DEFECTS:**
1. **README.md:33** still applies "by design" to all 8 None IDs. The line came in with `1977515e`. It was missed by d27bcae2, by BOUNCE #2, and by the foreman. It contradicts D35, notes:313-314, and README:71.
2. **The `query()` docstring** ends with "Releases built before the field existed would match nothing; this one does not." That is false: v2.10.0's `query()` has no `tier` kwarg and **raises TypeError** (the kwarg arrived in 4c09dcb1). The sentence ships on PyPI and cannot be corrected after the cut.

**Evidence [R], all clean apart from the two defects:**
- The surface sweep found only these two plus allowed quotes.
- **Per-ID successors were confirmed by a THIRD route**: per-tag tombstone state, incident `date` matched within each group, and upstream `ingest/` snapshot titles for each successor's source ID. 14909, 14742, 14907, 14789 and 14852 are all correct. The per-release boundaries are exact, including v2.3.1.
- T23's type test fails on the `1977515e` annotation (8 violations).
- A **behaviour sweep, old module against new, gives the identical hash `c322f3fa…`**, so there is no behaviour change.
- pytest `475 passed, 1 xfailed`.
- **The drift check was proven to fire**: a planted "13,060 incidents" gave exit 1, and it was clean after restore.
- The whole notes verification block (413–574) runs on this host with every value matching.
- Exactly 12 IDs raise TypeError under v2.10.0's package on v2.11.0 data.
- The `data` tree hash is 540a66ba, unchanged. merge-tree is clean. D32 is respected. All 5 version strings still read 2.10.0.

**Advisories:**
- A1: drop the hardcoded "1,915" from the docstring.
- A2: the "stable keys, not titles" wording does not single out 14742 (three group members' keys are fully inside the old row). The pick is decided by headline/`date`, and the answers are correct.
- A3: the dated-note marker should read "2026-09-18, revised 2026-10-01 pre-publication".
- A4: DATA_DICTIONARY:9 lead-in; ID_POLICY §3 (WS3); **`docs/paper/genai-incidents-methods.md:74` "so citations always resolve" (unscoped)**.
- A5: STIX `x_tier` still [A].

**Cut-time expectations, recorded:**
- top_diff `{version}`; ID set unchanged at 13,361; 0 entries changed; landmark 1,915; deprecations byte-identical.
- Resolver spot-check: 07771/08109/08133/08146 → 14814/14847/14850/14853 (group 1). The 8 give None with groups 12/100/11/8/12/11/100/100. 07738→14757.
- Behaviour hash `c322f3fa…` if `src/` is unchanged apart from the docstring.

## ⚖ D35 — USER RULINGS, 2026-10-01, on WS4-T23's escalation: **no data change in v2.11.0; disclose per ID**

1. **INC-03128 and INC-08185: NO authorization change for v2.11.0.**
   - D28's data ships exactly as authorized and gated.
   - The notes name the stable-key successors, **INC-14909** and **INC-14742**.
   - Narrowing D28's authorized fan-out for these two, which means editing the audit entries and re-pinning `REQUIRED_SPLIT_AUTHORIZATION_ENTRIES_SHA256`, becomes a **separate gated task after the cut**, owned by WS4.
2. **INC-00497 and INC-08139: no single answer.**
   - The fan-out stays, so `resolve_id` returns None.
   - The notes carry a **per-release successor table**:
     - 00497: 14789 for v2.0–2.1, 14907 for v2.2–2.8;
     - 08139: 14852 for v2.2–2.5, 14742 for v2.6–2.7.

**Consequence: "8 ambiguous by design" is replaced by an exact per-ID disclosure** of the 8 IDs that return None:
- 4 retirements, split into real groups;
- 2 with an identified successor not yet written as a record;
- 2 whose meaning changed between releases.

**Branch movement.** `release/v2.11.0-notes` was fast-forwarded `1977515e..c7b5fe8f` (WS4-T23's `src/`+tests commit). **That commit is UNGATED.** It is covered explicitly by the final gate rather than by its own gate, which is a foreman decision recorded here. WS6 notes pass dispatched next.

### 🔎 WS4-T23 — D33 investigation delivered `c7b5fe8f` (pushed) — **NO DATA WRITTEN: an authorization change is needed → ESCALATED TO USER**

**Phase A.** Content checked per tag from v2.0.0 to v2.10.0, with the successor matched by **stable keys** (source IDs plus reference-URL overlap), not titles:

| ID | Content by release | Stable-key successor | Determination |
|---|---|---|---|
| INC-03128 | Momoa deepfake (v2.0–2.1), tombstoned v2.2 | **INC-14909** (AIID-1285 + OECD 1cd0 unique to it; 6/6 refs) | UNAMBIGUOUS |
| INC-08185 | Wolf Robots (v2.2–2.5), tombstoned v2.6 | **INC-14742** (OECD 2510 unique; 7/7 refs) | UNAMBIGUOUS (headline of a ~65-source over-merge) |
| INC-00497 | Saint Paisios scam (v2.0–2.1) → Greek tax AI (v2.2–2.8) | 14789 *or* 14907 | **CONFLICTED** |
| INC-08139 | Robotic endoscope (v2.2–2.5) → Wolf Robots (v2.6–2.7) | 14852 *or* 14742 | **CONFLICTED** |

**Phase B: nothing written, correctly.**
- The only pipeline route to single-element records is step 8a, driven by audit `new_targets` pinned by `REQUIRED_SPLIT_AUTHORIZATION_ENTRIES_SHA256` (873c29a2…).
- Narrowing any ID means editing D28's authorized entries and re-pinning that SHA, which is a **user authorization change**.
- The data delta is empty.

**Committed (`src/` + tests only):**
- BOUNCE #2 defect 5: the `query()` `tier=` caveat is corrected as a dated correction in the docstring.
- D34: `load_deprecations()` is typed `dict[str, str | list[str]]` with a docstring disclosure, and a new test pins the type against the real bundled data. It was shown failing on the old annotation (8 violations).
- Suite: `475 passed, 1 xfailed`. Drift check clean. `validate.py` passes.
- Not yet gated.

**Open for the user:**
1. Authorize single-target records for 03128→14909 and 08185→14742?
2. Choose a successor, or none, for the two contested IDs.

## ⚖ D33 + D34 — USER RULINGS, 2026-10-01, on the v2.11.0 notes BOUNCE #2 escalation

**Foreman finding behind D33, measured [R] by a route the gate did not take.**
- `docs/audits/WS4-T19-authorized-splits-2026-09-18.json` records `decision: resplit_redirect` (`eventual_deprecation_reason: resplit`) for **8** IDs.
- `data/id_deprecations.json` carries resplit records for only **4** of them (07771, 08109, 08133, 08146).
- **INC-00497, INC-03128, INC-08139 and INC-08185 have only their original `merged` records.** This is a **delivery gap against D28's own audit decision**, not a new policy question.
- **The history check disagrees with the audit on one ID.** Titles in tagged releases:
  - INC-08139 was a *robotic endoscope* story in v2.5.0, but the audit recovers "Wolf Robots" for it. (INC-08185 *was* Wolf Robots in v2.5.0.)
  - INC-00497 changed content between v2.0.0 (Saint Paisios scam) and v2.5.0 (Greek tax AI).
  - INC-03128 is consistent (Momoa).
- So the fix needs investigation, not just four appended records.

**D33 — fix the data first; the cut stays HELD.** WS4 investigates all 4 IDs and states a per-ID determination with evidence **before writing anything**. It appends records under invariant 9, through the pipeline and never by hand-editing, only for IDs whose determination is unambiguous, with a field-level delta (agreement 2). Any ID where the audit and history disagree and cannot be reconciled **stops and comes back** to the foreman and user. Then the notes are corrected and gated, then the cut.

**D34 — disclose the `load_deprecations()` type change; no API change in v2.11.0.** Document `str | list[str]` in the docstring, the notes and the CHANGELOG as a consumer-impact item, including that v2.10.0's `resolve_id` raises `TypeError` on v2.11.0 data. A stable accessor is a follow-up.

**Routing for the rest of BOUNCE #2:**
- Defect 5 (the false `query()` `tier=` docstring) and the D34 docstring go with the WS4 task, because they touch `src/`.
- Defects 2 and 4, the D34 notes and CHANGELOG text, and the corrected 12-ID figures go to a WS6 notes pass after WS4 lands.
- A final gate follows.

> **Update 2026-10-01, WS4-T23 Phase A (the "delivery gap" half of the finding is WRONG; the "fix needs investigation" half stands).**
> - D28's audit `new_targets` for INC-00497, 03128, 08139 and 08185 are the **full fan-outs** (8/9/~90/63), and step 8a (`merge_and_dedupe.py` ~2397-2437) correctly appended nothing. It was **neither a bug nor a narrowing**: D28 authorized the fan-out, and the data matches it.
> - The "single successor" idea came from `recovered_title` (`scripts/audit/ws4t10_inbound_deprecations.py` `LOOKUPS`), which reads a title at **one hand-picked commit per ID**. That is a title-match route, so it was not the independent evidence BOUNCE #2 defect 1 took it for.
> - The foreman's history check **was** right about INC-08139. *Dated record; do not regenerate the paragraph above.*

### ⛔⛔ v2.11.0 RELEASE NOTES — **BOUNCE #2 (red-reviewer, exhaustive pre-cut gate, 2026-09-30, on `1977515e`) — ESCALATED TO USER** (protocol: two bounces; defect 1 also needs a data ruling). **The cut stays held.**

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … Both BOUNCE #1 defects are fixed in the notes body itself, and every figure in docs/releases/v2.11.0.md re-derives exactly. The bounce is for five problems."*

**What passed [R]:**
- The promise is scoped on every surface except DATA_DICTIONARY:9.
- The 12-ID table matches a v2.10.0-package-on-v2.10.0-data run exactly.
- A release-to-release sweep over INC-00000..19999 shows an answer becoming None for 8 IDs and changing for 5 (07738 plus the 4 fixed). 306 IDs are new, and nothing else moves.
- The pytest count is `474 passed, 1 xfailed`, and the drift check is clean.
- Both verification blocks run as written.
- The v2.10.0 note is pure-insert (29/0) and carries the marker.
- The release body has absolute links and no anchors.
- The `data/` tree hash is unchanged (540a66ba), and version strings are not yet bumped.
- merge-tree with main is clean.

**DEFECTS:**
1. **Four of the "8 ambiguous" IDs are not ambiguous, according to the project's own D28 audit.**
   - `docs/audits/WS4-T19-authorized-splits-2026-09-18.json` `recovered_title` gives exactly one matching row inside each group:
     - INC-00497 → INC-14907 (Greek tax AI; group of 12);
     - INC-03128 → INC-14909 (Momoa deepfake; group of 11);
     - INC-08139 and INC-08185 → INC-14742 ("Wolf Robots"; groups of 100).
   - This is the same title-match proof the delta audit uses to call the 4 fixed targets right. So "None means ambiguity" is false for them, and `resolve_id_group` hands consumers 11–99 unrelated rows (agreement 6 form (d)).
   - The data matches what D28 authorized. **DATA QUESTION → user:** should these 4 get single-element resplit records, like the other 4?
2. **README:71 and the dated v2.10.0 note say "twelve … return None in this release — four fixed".** That is false for 4: no published package ever returned None for them. v2.10.0 returned the wrong over-merged targets 01271, 01412, 07736 and 00554. Consumers who cached those mappings need to be told to re-resolve, not told the IDs are "fixed".
3. **Undisclosed public API change.**
   - `load_deprecations()` is still typed `dict[str,str]`, but 8 of 293 values are now lists. v2.10.0 had 0.
   - v2.10.0's own `resolve_id`, run on v2.11.0 data, raises `TypeError: unhashable type: 'list'` for all 12 IDs.
   - Neither the notes nor the CHANGELOG mentions it.
4. **DATA_DICTIONARY:9** carries an unscoped "recorded … and resolvable via resolve_id()", and line 203 omits `resolve_id_group`.
5. **A false docstring ships in the PyPI package.** `query()` (src `__init__.py:137-142`) says `tier=` "matches nothing until the dataset is rebuilt", but `query(tier='landmark')` returns 1,915. Fixing it touches `src/`, so it needs a small re-gate.

**Advisories:**
- **A1.** `ID_POLICY.md:3` still says "DRAFT — decision pending (E4)". The fix is on the ungated `ws3/headroom-remeasure` (`79101d81`). §3 still claims resolve_id terminates on any chain and omits the 8 None cases (the D31 rider, WS3).
- **A2.** The notes' hash-grep needs `-A1`, and its `/tmp` steps break on Windows.
- **A3.** README:71 still conflicts with PR #100 (known).
- **A4.** STIX `x_tier` is still [A].

**Cut-time expectations, recorded for step 3:**
- top-level diff `{version}` (± `generated`);
- the ID set is unchanged at 13,361, with 0 changed entries;
- landmark 1,915;
- deprecations byte-identical (1,060 / 1,056; reasons 704/289/59/4/4);
- the five version strings at 2.11.0;
- the resolver spot-check as in the table (unless defect 1's data ruling changes it).

### ✅ WS4-T22 — **PASS (red-reviewer, second gate, 2026-09-30, on `934a6348`) — NO DEFECTS — MERGED (fast-forward) into `release/v2.11.0-notes`, `2f7bba1d..934a6348`, origin verified**

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: PASS … All three BOUNCE #1 defects are closed, and I confirmed that with my own mutation runs. The null-`into` divergence … was already in the package at 2f7bba1d … not a defect of this branch and does not block the release."*

The rework came from a fresh pipeline-engineer (agreement 3: replace, don't re-prompt). Before it ran, an orphaned uncommitted 2026-09-20 follow-up in the T22 worktree, which went the max-date way, was rescued to `ws4/t22-abandoned-wip-2026-09-20` (`f764d2d2`) and marked not for merge.

**Evidence [R]:**
- **Loader.** The loader is back to last-in-file wins.
  - On real data, `gi._load_deprecations()` against `validate._latest_by_from` shows 0 mismatches.
  - A subprocess sweep of the real 2f7bba1d module against the branch module over INC-00000..19999 shows:
    - an identical deprecations map (293 keys);
    - `resolve_id` changed for **exactly 4**, each from None (07771→14814, 08109→14847, 08133→14850, 08146→14853);
    - `resolve_id_group` changed for 0;
    - **8 stay None**.
  - **A second route, through the build code** (`merge_and_dedupe.resolve_live_targets`) over all 1,056 `from`s, gives 0 disagreements.
- **Fire-proofs reproduced by the gate:**
  - max-date loader: 3 failed;
  - first-wins loader: 9 failed;
  - fix reverted: 4 failed;
  - over-broad fix: 3 failed.
- **Cannot-fail tests.** Both are deleted.
- **Fixture leak.** Forward and reverse file order both pass. Adversarial adjacency passes, and the gate **proved that adjacency check can fire** by removing the teardown, which gave 2 failures. A plain file-order run cannot catch a broken teardown.
- **Suite: `474 passed, 1 xfailed`** (base 459; +15 = 1+1+1+6+6, accounted for). **This is the figure the notes publish**, and the notes specialist is to re-derive it, not copy it.

**Advisories, routed:**
- **A1 (→ new follow-up, WS4 + WS3, not a release blocker).** Package/validator parity on null-`into` supersession.
  - The shape `[F→live, F→null]` gives package = live and validator = None, identically at 2f7bba1d, so it is pre-existing.
  - It is unreachable through automated paths: step 6f is fresh-filtered, and the #88 fixpoint only nulls removed targets. No such record exists in the data.
  - Fix later: either the loader honours a later null, or `validate.py` rejects a removal appended over a live target. Add a null case to the fixture.
- **A2.** `named_twelve` and `no_collateral` are pinned to the current corpus and act as tripwires. The next legitimate `data/` rebuild that touches these IDs should expect to update them.
- **A3.** Cosmetic: a duplicate assert, and mid-module imports.

**→ Next on the v2.11.0 path:** the WS6 notes pass on BOUNCE #1 (`2f7bba1d`) defects 1 and 2, run against `934a6348`.

### ⛔ WS4-T22 — **BOUNCE #1 (red-reviewer, 2026-09-30, on `af9601fa`)** — the first RECORDED verdict; the gate a prior session dispatched never filed one (agreement 3), so this gate was re-dispatched from scratch. **Status: in-progress; re-dispatched to a fresh pipeline-engineer.** The user ordered "cut v2.11.0" on 2026-09-30, and this is the first blocker on that path.

**─── GATE VERDICT TEXT (agreement 5) ───** *"VERDICT: BOUNCE … The D31 core is correct … It bounces because the loader-rule change introduces a split-brain between the package and the build/validator. Two of the 11 new tests also cannot fail."*

**Evidence measured [R]:**
- **The core passes.** The real pre-fix module and the real branch module were each run in its own subprocess over INC-00000..19999, comparing per-ID results:
  - `resolve_id` changes for **exactly 4**, all from None to an answer (07771→14814, 08109→14847, 08133→14850, 08146→14853);
  - `resolve_id_group` changes for 0;
  - the deprecations map is identical.
- **The 8 stay None**, with group sizes of 11–100.
- The suite runs `470 passed, 1 xfailed` on the branch and 459 on the base.
- The branch merges clean into `release/v2.11.0-notes`; a fast-forward is possible.
- **"Output-identical today" is TRUE.** For all 4 duplicated `from`s, the merged record (2026-06-28, at index ~436) and the resplit record (2026-09-18, at index 1056–1059) agree under both rules. The file has 57 adjacent date inversions.

**DEFECTS:**
1. **Split-brain between the loader and the validator.**
   - **What changed:** `_load_deprecations()` now picks max-`date`.
   - **The repo's existing contract is last-in-file:**
     - `scripts/validate.py` `_latest_by_from` says "every consumer … must go through this function";
     - `merge_and_dedupe.py:2346-2353, 2460-2468` must stay "behaviourally identical";
     - `tests/test_merge_and_dedupe.py:552` asserts the last record stays authoritative even with an earlier date.
   - **How the rules disagree:**
     - (A) the inversion test's own seed: the package returns INC-00002, the validator INC-00001;
     - (B) a dateless second record also gives INC-00002 vs INC-00001.
     - Both answers are live, believable IDs.
   - **Remedy:** restore last-in-file wins and state it explicitly. Date precedence would be a separate policy question that moves three files in lockstep. **The foreman does NOT escalate it now**, because the repo's recorded decision is last-in-file and the D31 scope was the list hop only.
2. **The A1-required supersession test is missing.**
   - **Required:** a fixture with both targets live, run in both file orders, with proof that it fires.
   - **What exists instead:** the duplicate test uses only real data, where the two rules agree. Mutation M3 (reverting to last-in-file) still gives 470 passed.
3. **Two proof-of-fire tests cannot fail (agreement 6 form a).**
   - **The tests:** `test_resolve_id_ws4t22_proof_the_regression_test_fires` and `test_resolve_id_no_collateral_change_proof_it_fires` never call `gi.resolve_id`.
   - **The evidence:** both still PASS under M1 (bug restored) and M2 (over-broad fix).
   - **Also:** the no-collateral oracle shares the new loader (form b).
   - **Remedy:** remove these two tests or make them exercise `gi.resolve_id` against fixtures, and point the oracle at the raw file with last-in-file semantics.

**Keep:**
- the `len(current) != 1` unwrap;
- the docstring rewrite;
- the 0/1/2-element, dangling, chain and cycle unit tests.

**Re-derive the pytest figure** after the rework; it will not be 470. **A second bounce goes to the user.**

### 🔧 WS4-T22 — `resolve_id` single-successor fix (D31) — delivered `af9601fa`, **pushed**, gate dispatched

Branch `ws4/t22-resolve-id-single-successor` off `release/v2.11.0-notes` @ `2f7bba1d`. Two files: `src/genai_incidents/__init__.py`, `tests/test_package.py`. No `data/`, no version strings, `resolve_id_group()` byte-identical. Suite **459 → 470 passed, 1 xfailed** (+11), baseline confirmed at `2f7bba1d` first.

**The fix:** the list guard now tests length before bailing — `len(current) != 1 → None`, else `current = current[0]` and the walk continues. Docstring rewritten, since **its old rationale was false for the one-element case** and that falseness was half the defect.

**All twelve behave as D31 specifies**, per the specialist's own run: the 4 resolve to `INC-14814`/`INC-14847`/`INC-14850`/`INC-14853`, the 8 stay `None`.

**⚠ UNAUTHORIZED SEMANTIC CHANGE, SELF-DISCLOSED — the reason this gate is not a formality.** The foreman's A1 addendum said to make the supersession rule explicit **as "last record wins"** and forbade changing the storage shape. **The specialist instead changed the selection rule to max `date`** and said so plainly. It argues this is output-identical today because file order already matches date order for all four duplicated IDs — **true, but it does not cover the general case.** File-order and date-order are **different contracts**, and `test_deprecations_file_order_is_never_resorted_even_with_date_inversions` exists precisely because **date inversions are a real, tested-for condition in this file**. Open questions routed to the gate: which rule is correct when a later-appended record carries an earlier date; what max-date does with a missing/null/malformed `date` (**the old file-order rule was total — it always had an answer**); and whether the semantics may now depend on a field whose ordering the project deliberately refuses to guarantee. **The gate was told not to bounce it merely for exceeding the brief, nor wave it through merely because it is disclosed and plausible — and that the foreman's brief may have been wrong to specify file-order.**

**Proof-of-fire, done twice and live** (agreement 6): restoring the old unconditional bail fails the named-12 test on `INC-07771` (`None != 'INC-14814'`); making the fix over-broad (`current[0]` on any non-empty list) fails **both** tests from independent angles — the named-12 via a **wrong answer** (`INC-00311 → INC-14660`, an invented successor) and the no-collateral test via an **unexpected changed-set**. Both restored, diff verified clean. Two of the 11 tests embed the fire-proof permanently rather than leaving it a one-off — **the gate was asked whether those are genuine or assert against a reimplementation of the bug and therefore pass regardless.**

**The no-collateral sweep used an inline reimplementation of the pre-fix algorithm, not a stored baseline** — deliberately, citing agreement 6's independent-derivation requirement. Exactly 4 changed, all `None`→resolved, nothing else moved. **The gate was asked to judge whether that oracle is genuinely independent or reproduces the same mistake.**

**✅ FOREMAN-RECONCILED — the specialist flagged a 1,051 vs 1,056 discrepancy in the brief rather than silently reconciling it, which was the right call. Both figures are correct for their release:** v2.10.0 had **1,051 records / 1,051 distinct** `from` (zero duplicates); v2.11.0 has **1,060 / 1,056**. The 9 new records = **5 new `from` IDs** (4 `split` + `INC-07738` `merged`) **+ 4 `resplit` records landing on already-tombstoned IDs**; `5 + 4 = 9`, exact. The specialist's sweep is the superset, so the result stands either way.

**→ The notes pass is now unblocked and its `pytest` figure is `470 passed, 1 xfailed`** — to be **re-derived by the specialist after the merge, not copied from this board.**

### 🗣 WHAT THE 8 AMBIGUOUS IDs MUST BE TOLD — drafting constraints for the notes fix (red-reviewer, 2026-09-20)

**The inversion that makes this more than a documentation nicety:** a consumer on v2.10.0 **cannot call `resolve_id_group`, because it does not exist in the package they hold.** Normally you tell people how to translate their old identifiers *before* they move; here the translation tool only exists *after* they move. Any migration line that just says "use `resolve_id_group`" is advice the affected reader cannot take.

Required, in this order:
1. **That it happened.** The ID resolved to a live single successor under the v2.10.0 package and now returns `None`. Not "may now be a retirement record" — **it went silent.** Eight of these were already tombstones that were working fine, so **they appear in none of the "which IDs changed" lists the document currently gives** — they are invisible precisely to the reader who needs them.
2. **That `None` here means ambiguity, not loss** — the ID has 8–100 real successors and `resolve_id` declines rather than picking one, which is the honest answer; the content is all still there. **The single most important sentence for this reader, because `None` from a resolver reads as "your data is gone" and it is not.**
3. **Two ways to act, and the first needs no upgrade:** read `data/id_deprecations.json` directly — `into` is the full successor array, a plain JSON document joinable **without any of this project's code**. Only the second path requires upgrading.

### 📐 D31 SCOPING — the patch measured before it was written (red-reviewer, 2026-09-20) [R]

The gate **implemented the proposed patch itself and swept 1,056 published IDs** — every tombstoned `from` plus the five that left the live set — comparing patched against current behaviour **per-entity**, then reported before the specialist was dispatched.

- **(i) Exactly 4 would newly resolve:** `INC-07771 → INC-14814` · `INC-08109 → INC-14847` · `INC-08133 → INC-14850` · `INC-08146 → INC-14853`, **all four targets live**. The other 8 stay `None` — their chains terminate on lists of 8–100 elements, so the unwrap never applies. **The patch fixes the bug and does not touch the by-design case.**
- **(ii) Currently-resolving IDs whose answer changes: 0. Currently-resolving IDs that lose their answer: 0.** Strictly additive. **The structural reason, worth keeping:** anything that resolves today never encountered a list hop, because today a list hop returns `None` unconditionally; the patch only alters behaviour *at that hop*, so every working path is untouched **by construction — and the sweep confirms it rather than assuming it.** That is agreement 6 done properly: a structural argument *and* an independent per-entity measurement, neither leaning on the other.
- **(iii) One published figure is invalidated — and it is not a data figure.** No corpus, deprecation, landmark or taxonomy number depends on `resolve_id`; the patch changes no data file, and the four successor targets are already live rows already inside the 13,361. **But the notes' Verification block publishes `python -m pytest -q # 459 passed, 1 xfailed` as a reproduction expectation.** Shipping the resolver fix with its regression test **makes that line stale the day it lands**, in a document whose entire credibility rests on every figure reproducing. **Promoted from advisory to a required edit in the notes-fix brief.**

### ⚖ D31 — USER RULING, 2026-09-20: **narrow code fix + disclose.** v2.11.0 carries a resolver fix, not notes alone.

`resolve_id()` resolves an `into` list of **exactly one** element to that single live successor; **multi-successor records keep returning `None` as designed.** The four bugged IDs are repaired; the eight ambiguous ones keep today's behaviour but are **named in the notes** with a `resolve_id_group` migration line. Ships as **v2.11.0** with a regression test covering **all twelve**.

**Why this option and not the others.** Option "fix all 12" was rejected on the merits recorded above: choosing one of 100 successors **invents a canonical answer the data does not support** — the opposite of what the split was for. Notes-only was rejected because it knowingly ships a guard whose **own docstring justification is false** for four IDs. Holding the release was rejected because `main` already carries the new corpus under a 2.10.0 label, so the **E24 defect the cut exists to fix would stay live** while scope grew to include the nine Phase-2 ghosts.

**Rider — the eight ambiguous IDs remain a known, disclosed deviation from `ID_POLICY.md` §3's "never to silence".** D31 does not resolve that; it scopes it. The honest position is that `None` for a 100-successor record is silence, and the policy sentence or the API owes a reconciliation. **Boarded as open, owner WS3** — do not let the disclosure line be read as closing it.

### ⚠ ADJUDICATION, 2026-09-20 — the foreman finding is UPHELD, the gate WITHDRAWS "zero new breaks", and the blast radius is **12 published IDs, not 4**

**The gate chose a better route than the foreman's and said so.** The foreman ran today's code against old data. The gate **cloned the `v2.10.0` tag into a throwaway clone and ran the package exactly as it shipped — its own resolver against its own data** — making the comparison release-to-release rather than code-against-data. That difference is the whole finding: it surfaced four IDs the foreman's method could not have seen.

**The finding that decides the matter: `resolve_id_group` DID NOT EXIST at v2.10.0.** The import fails. Both it and the `isinstance(current, list)` bail were introduced together by `dcec1602` (WS4-T15), *after* the tag. **So a v2.10.0 consumer holds exactly one resolver, and it is the one that now returns `None` — "use `resolve_id_group`" is not advice they could have taken.**

**v2.10.0 as shipped, all four returning a usable live single ID:** `INC-07771 → INC-01271` · `INC-08109 → INC-01412` · `INC-08133 → INC-07736` · `INC-08146 → INC-00554`. All four return `None` at `2f7bba1d`.

**Sized properly rather than trusting the four already known** — all 1,051 tombstoned IDs swept through the v2.10.0 resolver, the same 1,051 through the `2f7bba1d` resolver, diffed **per-entity**:

```
REGRESSED (live single ID at v2.10.0 -> None now): 8
  INC-00497  gave INC-00311  -> None   (group now: 12 successors)
  INC-03128  gave INC-00754  -> None   (group now: 11)
  INC-07771  gave INC-01271  -> None   (group now: 1 -> INC-14814)
  INC-08109  gave INC-01412  -> None   (group now: 1 -> INC-14847)
  INC-08133  gave INC-07736  -> None   (group now: 1 -> INC-14850)
  INC-08139  gave INC-00554  -> None   (group now: 100)
  INC-08146  gave INC-00554  -> None   (group now: 1 -> INC-14853)
  INC-08185  gave INC-00554  -> None   (group now: 100)
NEWLY-RESOLVING (None -> live): 0
CHANGED TARGET (live -> different live): 0
```

`INC-00497`, `INC-03128`, `INC-08139`, `INC-08185` regress because they **chain through** a now-retired ID and land on a list. **Plus the four D28-retired IDs themselves**, live entries resolving to themselves at v2.10.0 and now `None` = **12 published IDs that went from a usable answer to silence.** The sweep is complete by construction: {live at v2.10.0} ∪ {tombstoned at v2.10.0} is that release's whole published universe, minus §1.4(a)'s nine ghosts, already broken.

**The 12 split into two kinds and only one is a bug:**
- **8 are ambiguous** (`INC-00311`, `INC-00554`, `INC-00754`, `INC-01897`, `INC-00497`, `INC-03128`, `INC-08139`, `INC-08185`) — 8 to 100 successors each. `None` is defensible and matches the docstring. **Still silence, which `ID_POLICY.md` forbids, and undisclosed.**
- **4 are an outright bug** (`INC-07771`, `INC-08109`, `INC-08133`, `INC-08146`) — `resplit` `into` is a list of **exactly one live element**. `resolve_id` bails on `isinstance(current, list)` **before testing length**, so the docstring's justification — *"no single canonical successor to walk to"* — **is simply false for these four.** An unambiguous, live successor exists and is discarded. **An over-broad guard, not a design decision.**

**The gate's withdrawal, in its own words:** *"So: no, you are not wrong, and I was. I told you 'this release introduces zero new breaks' and that the fix is 'purely editorial.' Both are too generous and I withdraw them."* The **data** is sound; the **shipped API** regressed, and v2.11.0 is the release that would carry it to consumers.

**→ ESCALATED TO THE USER (protocol step 8): fixing `resolve_id` is a published-API behaviour change.** Notes-only vs notes-plus-code-fix is not the foreman's call. **DEFECT 2 and the advisories are still outstanding; the cut remains held.**

### 📝 `docs/ID_POLICY.md` stale-banner fix — schema-architect, `79101d81` on `ws3/headroom-remeasure` (parent `0babb2de`) — **ungated, unmerged, PUSHED `0babb2de..79101d81`**

Routed from today's correction 3. One file, `125 +/17 −`, tree clean, no strays, `data/`/`schema/`/code untouched. **Re-derived independently via §7.7 route A, with `data/` confirmed identical to `origin/main` @ `4861afd7`:** `live 13361 · records 1060 · distinct_dep 1056 · high_water 14910 · headroom 85089` — agrees with today's measurements and with §7.1.

**The specialist solved the hard half the way agreement 4 wants and said why.** It refused to cut §2 (Option A), because that would delete the only record of *why* the universal-break option lost and leave §5's argument — *"Option A is Option B plus a rewrite"* — unreadable. It also refused to rewrite §§1–6 to sound decided, because §7's dated addendum states on the record that those sections are "unaffected in substance" and the old banner said not to edit them: **rewriting them would have falsified both.** So it removed the still-choosing framing by **surrounding** the memo rather than editing it — new `DECIDED AND IN FORCE — D13, 2026-07-27` banner quoting D13 from `PROGRESS.md:1030`; a **banner-history** paragraph (without which §7.4's "does not edit the banner's original wording" becomes a dangling reference); a new **§0 "The policy in force"** carrying the commitment verbatim as *the copy in force*, an implemented-vs-owed table, the riders, and dated figures; a **do-not-regenerate record marker** over §§1–6 naming §2 REJECTED and §3 ADOPTED and **naming the three surviving future-tense phrases explicitly**, so a future grepper landing on one knows what it is; and **heading labels only** on §2/§3/§4/§5. **§7 is byte-identical.**

Two details worth keeping: `(proposed policy text)` under §3 was "the last word reading as undecided", and §4's `(not part of the decision — published either way)` implied a live choice when §4 is simply live policy.

### ✏️ DATED CORRECTION, 2026-09-20 (foreman) — three figures in the block above did not survive re-derivation

Per agreement 4 the original text above stands where it is a **record** (the D30 ruling, the gate's PASS narrative); this note names exactly which half changed. The **live** "Published state on origin" line was corrected in place, because a state line that hedges its own currency is not a state line. **Two of these three I had also stated to the user in chat, so the chat record is wrong where this board is now right.**

1. **"All four authorized IDs retired" undercounted what left the corpus — five IDs stopped resolving to themselves. [R]** Four is right *for D28's authorization* (`reason: "split"`: `INC-00311`, `INC-00554`, `INC-00754`, `INC-01897`). The fifth, **`INC-07738`**, left via an ordinary `merged` tombstone into `INC-14757` and was never part of D28's authorized set — which is why the authorization guard, correctly, has nothing to say about it. **The consumer's question is the five, not the four**, so the release notes must state both distinctly. The arithmetic only closes on five: `13,060 + 306 − 5 = 13,361`, exact. Found by a parallel WS3 measurement, **not** by the party that produced the four. Re-derived here by direct measurement of the committed tree: all five absent from `data/incidents.json` (13,361 rows), reasons `split 4 · merged 289 · out-of-scope 704 · orphaned 59 · resplit 4`.
   - **Does not disturb the landmark decomposition:** `INC-07738`'s pre-removal tier was `feed`, not `landmark`, so **−2 / +12 / 0 flips** stands unchanged.
2. **"23 attack shapes, all abort" was gate testimony recorded as though re-derived — [A], not [R], and the committed number is 13.** Agreement 5 violated at the moment of recording, by me. The suite contains **9** `split_guard_*` tests (empty list · missing pair · passes once authorized · unmarked list · marker naming the wrong decision · entries diverging from the pinned hash · tamper-plus-recompute · ignores ordinary merges · reports every unauthorized ID), plus 3 retirement/resplit tests and `test_validate.py::test_real_resplit_redirects_match_d28_approved_targets` = **13**. Re-derived by enumerating `def test_` definitions — deliberately **not** by re-running the selection that produced the claim, per agreement 6(b). **23 was a count of scenarios explored, which is not a count of barriers that exist.** The specialist drafting the release notes **refused to carry the 23 forward** and substituted its own count; that refusal was correct and is why this was caught before publication.
3. **WS3-T5 / E4 is not an open ruling — D13 decided it.** The docs sweep routed the stale headroom table as "stale input to the **open** WS3-T5 ruling"; that premise is wrong. D13 adopted **Option B, padding-agnostic IDs, with two riders**. The re-measurement remains worth merging on its own merits (the table really did state 992 deprecations against an actual 1,060), but it informs a **decided** policy, not a pending one. **`docs/ID_POLICY.md:3` still carries `STATUS: DRAFT — decision pending (E4)`** — a live surface contradicting a decision taken long ago, and exactly the kind of retired banner agreement 4 warns a future pass will mistake for a source. **Routed to schema-architect on `ws3/headroom-remeasure` (`0babb2de`), not fixed here** — the foreman does not implement, and that branch already owns the file.

**What the three share:** each was a number that arrived from a party with an interest in it and was written down without a second route. Agreement 6's counterweight worked in all three cases and in none of them was the check a re-run: a different measurement found the fifth ID, a different party refused the 23, and a different decision record contradicted the "open ruling".

## 🔁 WS4-T17 — the skipped-URL sampling probe — **⛔ BOUNCE #1 (red-reviewer, 2026-09-18, on `1a0fa5a5`), fixes in flight**

**Why the task exists:** WS4-T13's crawl budget skips ~1,773 legacy numeric-slug URLs per run. The rule rests on a premise — *every such page fails the body-shape check*, measured with zero exceptions — and **skipping those URLs makes the premise unobservable.** It was the one advisory that **gets worse by merging**.

**The hard gate genuinely fires — the reviewer proved all three links itself, with a control:** a poisoned fixture through the real `main()` (violation recorded, `::error::` raised), the CLI as a **real subprocess** exiting 1, and the workflow's step ordering parsed from YAML — `Restore → ingest → skip_probe → Persist → Open PR → Enforce`, keyed on **`outcome` not `conclusion`**, which is correct under `continue-on-error` and mirrors the in-production `Enforce source health` step. A violation still lets the refresh PR open and still reddens the run. Invariant 5 clean (no new egress; the chokepoint test rglobs `scripts/`), scope exactly 4 files, suite 371.

**Defect 1 — THE PROBE ATTESTS ON ZERO OBSERVATIONS.** Driving the real `main()` with all probed URLs returning `REASON_FETCH_FAILED` printed **`3 sampled, 0 violations -- premise still holds`**, incremented the lifetime counter, advanced the cursor and exited 0. **Excluding fetch failures from the verdict buckets is correct** — a failed fetch carries no information. **Excluding them from all *reporting* is the defect:** nothing prints the fetch-failed count, nothing suppresses the attestation at zero observations, and the one durable metric conflates *sampled* with *observed*. **This probe exists because another check stopped being able to fail, and it emits an affirmative attestation having observed nothing — the same failure shape, one layer up, inside its own remedy.** The failure mode that makes it matter is **correlated, not random**: OECD serving 403/404 on legacy pages specifically — a plausible retirement path — would keep the probe green forever while it saw nothing.

**A foreman suspicion, refuted with evidence [R] — recorded because being wrong in the open is the point.** I briefed the gate that a fetch-failed URL might become *permanently* unprobed, since the cursor advances past it. **It does advance unconditionally — and the fraction permanently unprobed is 0%**, because `cursor > max` falls back to `start=0`, so a passed-over URL returns on the next wrap. Latency is one cycle, not "never". **The gate corrected the brief rather than confirming it.**

**Resizing — k=5 is theatre at this population, and the deliverable never said so.** Measured: **355 runs per cycle ≈ 6.8 years of weekly refreshes** (n=1,773, k=5), against a population that **grows as the window slides, so the cycle never closes.** §5 said only that coverage "accumulates gradually" — **agreement 6(c): the claim survives, the ability to check it does not.** Adopted from the gate: raise k to **25–50** (k=25 → ~71 runs ≈ 1.4 years, still only ~1.4% of recovered headroom), **split the sample** half-rotating for the monotonic guarantee and half biased toward **recently-arrived slugs**, where a shape change would first appear; keep rotation — the mechanism is right, the sizing was wrong — and ship a **coverage ledger** so the claim is a measured number.

**Defect 2 — the rename removed a false name and installed a false docstring.** The new `test_is_numeric_slug_minimal_baseline_pin` claims three mutants kill it; measured, the **hyphen-inclusive mutant passes**, as do all five plausible readings, against both it and the fuller test above it. **The board carried the same false claim and has been corrected separately** — see the dated correction on the WS4-T13 entry. Same sin the rename was meant to cure.

**Defect 3 — `INGESTION_CONDUCT.md` §5 splices a superseded breakdown into current arithmetic**, citing the 2026-09-14 "1,852 numeric / 1,148 date-hash" beside today's figures. The **1,773 / 1,227 / ~58.9% numbers are correct** (gate re-derived 58.93%); the parenthetical is stale, and the honest headroom cost is **≈0.3%**, not 0.4% — 0.4% divides by the fetchable set, not the headroom.

**Advisories dispatched:** state the measured cycle length in §5 and in `select_probe_sample()`'s docstring; **stamp the run id into the probe state** so stale state cannot read clean (guarded in the workflow today, unguarded anywhere else).

## ⏸ SESSION INTERRUPTION #2 — 2026-09-18, three agents killed mid-task by the session rate limit

WS6-T9 (landmark distribution), WS4-T17's fix round, and the WS4-T19 gate all died on HTTP 429. **All three were resumed rather than restarted**, and nothing was redone.

**What survived, and the lesson repeated:** WS6-T9's deliverable — a spec, a `schema/` change and two exporter edits — was **staged but uncommitted**, on no branch, on origin nowhere. **An agent idle with an uncommitted deliverable is indistinguishable from one that finished cleanly**, which is working agreement 3's known failure shape arriving by a second route (the first was interruption #1). Instruction on resume: commit and push *before* anything else, and push coherent increments rather than holding everything to the end.

**Worth recording about the WS4-T19 gate's last act before it died:** it caught **its own** instrument failing — a malformed path had silently turned a guard-attack into a re-test of the missing-file case, which *would have reported "the guard fires" for entirely the wrong reason*. **Agreement 6 form (a), in the tooling of the review whose job is finding that shape**, caught by the reviewer itself and disclosed rather than buried.


## 🎨 ARCHIVE REDESIGN — **✅ PASS on `f3a648c5` — MERGED `00b889c7`, DEPLOYED**

**Both foreman prescriptions in this task were refuted by measurement.** Recorded because the pattern matters more than either instance: an instruction from the board is a hypothesis, and a specialist or gate that tests it beats one that complies.
1. **The tick labels.** The brief pre-authorised `--faint` (3.62:1) as "decorative". The gate checked what those labels *are* — the y-axis values and the x-axis year labels, i.e. what a reader uses to know which year a bar is — and **sent the call back rather than inheriting a pre-authorisation.** Ruled: raise it. Now `#6f6a5d` = **5.30 panel / 4.91 bg**, and the gate confirmed it is the **only** hex token that moved in the whole stylesheet.
2. **The glyph fix.** The foreman prescribed CSS generated-content alt text (`content: "x" / ""`). The specialist **tested it against Chromium's accessibility tree via CDP and found the StaticText node still exposed**; `aria-hidden` on a `::before`-only span also failed. It moved the glyphs to real DOM text with `aria-hidden`, proven against the page's own row-toggle span. **The gate then re-verified with a before/after control rather than rerunning that method:** a real severity cell's accessible name was literally `"▲ HIGH"` before and is `"HIGH"` after; **whole-tree glyph-named AX nodes 1028 → 0**, agreeing across two independent routes.

**The 250× markup question the foreman could not answer — measured:** +250 DOM nodes (+6.4%), **+0.12% transfer** (and that is an `app.js` comment block, not per-row data — the glyph comes from `SEV_GLYPH` at render time), re-render median 10.9ms → 12.8ms with overlapping ranges, **CSV export byte-identical at 7,510,196 bytes** (captured as a real blob, not inferred from code), row-expand unaffected, and **accessibility-tree nodes 8078 → 6784 — a 16% reduction**, because 1,028 pseudo-element nodes disappeared. **Net positive for assistive tech**, not a cost.

**A pre-existing bug the redesign exposed**, confirmed by the gate against `main`'s own stylesheet rather than accepted as the finder's account: `.sev-badge.sev-Critical { background: rgba(255, 77, 99, 0.12) }` — `#ff4d63` is the **dark** theme's `--critical`, in a flat unscoped rule, so **light-theme severity badges were tinted with dark-theme hues regardless of active theme.**

**Floors on the merged tree:** axe **0 violations at critical and serious across both themes × both viewports**; Lighthouse accessibility **100**; 380px last-cell edge **byte-identical** at 363.796875 (the extra spans cost zero layout); `WRAP_TOLERANCE_PX` still 0 with `tests/` untouched; drift, integrity, dead-filters all clean. The gate **made the drift check fire on README line 3 specifically** rather than trusting a clean run, and **test-merged in a throwaway clone** because `main` had advanced mid-review — confirming the 12-file diff was `main`'s own new files, not scope creep.

**TWO NEAR-MISSES THE GATE DISCLOSED IN ITS OWN METHOD — both are working-agreement-6 shapes, inside a single review:**
- **Form (a):** its first glyph probe returned a clean "0 glyph nodes" — **against an empty page**, because its server was 404ing. It would have read as a pass for entirely the wrong reason. Caught only because it also printed the badge count (0). **Every probe after that asserts `badges == 250` first.**
- **Form (d):** an aggregate nearly convinced it the severity *word* had been suppressed — "10 severity-word StaticText nodes on a 250-badge page" — when its regex was simply case-sensitive against the CSS-uppercased "HIGH". **Per-entity inspection of one real cell settled it.**

**Design judgement, on the merits:** *"it reads as a serious reference work… serif titles against mono IDs and taxonomy codes is genuinely the card-catalogue logic the header claims, and it makes 13,060 rows scannable. Dark reads as a deliberate counterpart, not an inversion. Nothing reads as decoration at the cost of legibility"* — the one place that did, the tick labels, is now fixed.


## ⚖ D27 — TWO USER RULINGS, 2026-09-18, on the WS4-T15 design and the frozen corpus

**(a) IDENTITY KEY: Option A now, Option B as separately-scheduled hardening.** A deprecation record stays identified by its `from`, with precedence = **last in file order**. Already implemented, zero schema cost, and — the part that makes it defensible — the "file order = append order" invariant is now **enforced by a mutation test rather than assumed** (re-adding a sort fails three tests). **The caveat is recorded in the design's own words, not softened:** Option A *"requires every future consumer to remember to do that, and one already didn't."* That consumer — the issue-88 fixpoint — is fixed and tested; **the failure mode is not gone.** Option B (explicit `active`) is immune to it *by construction*, and the gate confirmed §8 presents that evidence as strongly as the case for A. **Neither option delays the remediation** — §3 is explicit that §2's persistence fix does not need B to be correct.

**(b) THE 47-SPLIT REVIEW IS AUTHORIZED, WITH THE LIST COMING BACK TO THE USER BEFORE ANY DATA MOVES.** → **NEW TASK WS4-T19 (P0)**. A specialist assembles the per-split evidence, proposes an authorized `(from, reason)` list, and builds the pre-authorization guard; **the user approves the list; only then does the unmerge execute.** D25(b) is satisfied by the user ruling on the list, not by delegating the judgement.

**Sequencing (foreman):** WS4-T19 delivers evidence + proposed list + guard + a **dry-run** delta. **No data change until the user approves.** Then list, guard and unmerge land in **one PR** so the corpus is never transiently half-changed, and WS4-T10 remerges in that same PR or immediately after. **This is the last thing standing between the project and an unfrozen corpus** — the count has been 13,060 since 2026-07-27.

## ✅ WS4-T15 — **PASS (red-reviewer, 2026-09-18, on `a571a923`) — MERGED `8c9307c4`**

**Root cause, smaller and worse than the predecessor assumed:** the build collapsed `id_deprecations.json` to one record per `from` via a dict comprehension keeping whichever came last — so a superseding record could never survive a rebuild. Records now carry through verbatim and in order.

**What the bounce caught, and why it generalises:** removing the collapse **removed a guarantee the issue-88 fixpoint had silently depended on for its whole life** — exactly one record per `from`. With duplicates possible it began reading **stale** records, rewriting committed records in place and propagating removal to unrelated citers, so a citation resolved to "removed, out of scope" instead of a live ID. **A second-order dependency, not a coding slip** — and precisely what a rebuild-based proof of the primary mechanism could not surface, because it tested the thing that changed rather than the things depending on it. The specialist's own summary of the lesson: *"I proved the mechanism I changed, not everything downstream of it."* Fixed by computing the authoritative view first and **appending** a terminal record, since mutating a committed record to change its meaning is itself the append-only violation.

**Gate evidence [R], re-derived rather than re-run — five adversarial shapes, each through three real rebuilds:** the original repro (3 records in, 3 out, byte-identical across all builds); two stale records with the authoritative one dangling; a chain through a bucket that is **itself a `from`**; a **cycle**; and a citer appended *after* the fix. All idempotent. It also established *why* the fix composes: the appended `into: null` is the latest, and `None` is never in `removed_terminal`, so the next build finds nothing to do.
- **The coverage guard was verified on the REAL committed chain** `INC-08146 → INC-08139 → INC-00554` (live, 103 source_ids), reproducing the old literal-`into` logic reporting **0%** on a healthy chain before confirming the fix reports clean. **Cycle-safety proven, not asserted:** `{A→B, B→A}` resolves to an empty set.
- **The ordering mutant is stronger than claimed:** re-adding `sorted(..., key=(from, date))` fails **three** tests, because reordering also changes which record is authoritative.
- **Real data unmoved:** full build twice, byte-identical to each other **and to the committed tree**; deprecations unchanged at 1,051; `validate.py` clean.

**Advisories → follow-up (not blocking, merged as-is):** (1) `_resolves_to_live`'s `cur in removed_ids` terminal is **effectively unreachable**, so `INC-CITER → INC-GONE(into:null)` reports as not resolving — the opposite of what the refactor's new docstring asserts; pre-existing and unreachable on today's data, but **agreement 6 form (a)** and now asserted in prose, so fix it or soften the docstring. (2) A **second implementation of latest-per-`from`** in the fixpoint (the circular-import justification is true and flagged in-comment, and the two currently agree) — **nothing tests them for divergence**; a shared helper both import would close it. (3) `_resolves_to_live` judges a partially-dangling list `False` at top level and `True` mid-chain.

**Foreman note on the merge commit:** its message is **garbled** — I used backticks inside a double-quoted `git commit -m`, so the shell substituted them and three words were eaten (`from` ×2, `into` ×1). `main` was not force-pushed to repair a message; **this board entry carries the authoritative text.** Heredoc (`-F -`) for every message containing backticks, which is what the other commits used.


## 🎨 SITE REDESIGN — "Archive" palette (user-chosen, 2026-09-18) — **✅ PASS (red-reviewer, `e933d2df`) — BOUNCE ZERO — four pre-merge fixes dispatched**

**User's words:** *"webapp needs a revamp redesign to look better also propose new colors"* → they chose direction **B, "Archive": paper and ink, one rust accent**, from three proposed with foreman-measured contrast ratios.

**Why a palette change rather than a repaint:** the outgoing amber `#ffb000` measured **9.98:1 on dark but 4.27:1 in light** — below the 4.5 AA floor for text — which is why the active-sort indicator had been forced to be underline-only. The new accent clears AA in both themes, so that constraint is gone and accent is now used as text in three places.

**Gate evidence [R], by its own derivation path:**
- **All 38 claimed contrast ratios re-derived** with a from-scratch sRGB luminance calculator — **every one matching to 2 d.p.** The ten badge tints were recomputed as alpha composites: severity colour at 12% over *that theme's own* panel, **max channel delta 0**.
- **Accent-as-text checked against the background the elements actually sit on**, not the token cited: `#9a3412` on `--panel-2 #f2ede1` = **6.25**, dark = **5.90**. That distinction is the whole reason the old palette failed.
- **The deliberate-break proof reproduced**, with a detail the specialist did not draw out: widening the Title column gave `363/348` and exit 1, but **`docScrollWidth` stayed 380 in BOTH cases** — so the wrap assertion is the only discriminating check. That is *why* `WRAP_TOLERANCE_PX = 0` matters, and `tests/` is untouched by the branch.
- **The drift checker was made to fire** on the variable-axis font URL (`hardcoded total '60,400'`), then restored — and `check_stats_drift.py` is not in the branch's file list at all, so it was not weakened.
- axe **0 violations at critical and serious across both themes × both viewports**; Lighthouse accessibility **100**; invariant-6 markers intact in the same form; dead-filters PASS; integrity clean over 33 files; pre-paint script, `theme` localStorage key, 11 OG/Twitter tags and the JSON download link all survive. Scope: exactly 4 files, nothing under `data/`/`schema/`/`ingest/`.

**A PRE-EXISTING BUG THE REDESIGN EXPOSED, confirmed as fact by the gate rather than accepted as the finder's account [R]:** `git show main:docs/style.css:730-734` contains `.sev-badge.sev-Critical { background: rgba(255, 77, 99, 0.12) }` — `#ff4d63` is **main's DARK-theme `--critical`**, in a flat unscoped rule. **Light-theme severity badges were tinted with dark-theme hues regardless of the active theme**, and had been since that rule was written. Replaced with pre-blended, theme-scoped tokens.

**Design judgement, requested explicitly because a compliance PASS is not the same as looking better:** *"it reads as a serious reference work, and it is a clear improvement… The table is the strongest part: serif titles against mono IDs and taxonomy codes is genuinely the card-catalogue logic the header claims, and it makes 13,060 rows scannable. Dark reads as a deliberate counterpart, not an inversion. Nothing reads as decoration at the cost of legibility."*

**Four pre-merge fixes dispatched:**
1. **The colour-blind fix charged a different accessibility axis.** The gate **queried Chromium's accessibility tree** rather than reasoning: 261 exposed `StaticText` nodes on a 250-badge page, `::before` content `"▲"` with **no `/ ""` alt-text component** — every badge announces as "black square, Critical". Not a WCAG failure, but the glyphs exist for *sighted* colour-blind readers, so the cost is avoidable. One line: `content: "A0" / ""`. **axe structurally cannot see this**, so no rerun would have caught it.
2. **A foreman error, reversed.** The brief pre-authorised `--faint` (3.62:1 light) for "decorative" chart tick labels. The gate checked what they are — `app.js:658,673,698,719` — and they are **the y-axis values and the x-axis YEAR labels**, i.e. what a reader uses to know which year a bar is. **Informational, not decorative.** Defensible under WCAG 1.4.3's in-picture exception and better than main's 3.06/2.93, but "arguably exempt" is not this project's standard. **The gate refused to inherit the call and put it back to the foreman rather than quietly accepting a pre-authorisation** — the right instinct. Ruled: raise it to ~4.6:1.
3. `README.md:3` still hardcodes `color=ffb000` in the shields.io badge — an inconsistency this pass created. (`CHANGELOG.md:414`'s "amber threat console" is a dated record, correctly left alone.)
4. The stylesheet header cites a `check_badges.py` and a "branch report" that **exist nowhere in the tree** — a pointer to nothing, which agreements 1 and 5 exist to prevent. Commit the script or drop the citation.


## ⚠ THE REVERT ALSO REMOVED THE BOARD — records must not ride a feature merge to `main`

**Found by the WS4-T15 specialist, not by the foreman** (`git merge-base --is-ancestor 9493ba22 0c778ced` → `no`): reverting the WS4-T10 merge deleted **386 lines of `PROGRESS.md`** plus the WS4-T10 design doc and its three audit artifacts, because those records reached `main` **only** as part of that merge. Meanwhile `8d1b241f`, the newest commit on `main`, cited "D26(b)" and "WS4-T15" as if both still stood — **the board referenced rulings that its own file no longer contained.**

**Restored here:** the pre-revert board plus this section, and the four record artifacts — **without** restoring `scripts/merge_and_dedupe.py`'s fix, `scripts/audit/ws4t10_*.py` or `tests/test_normalize_url_overmerge.py`, which are the armed parts and stay off `main` until WS4-T15's guard lands.

**The lesson, and it is a foreman lesson:** agreement 1a says push board records so a crash cannot erase them. That is necessary but **not sufficient** — a record that reaches `main` only inside a feature merge is erased by reverting that merge, which is a routine operation. **Board records and gate verdicts belong in commits that touch nothing but the board**, landed on `main` directly, so a revert of the work cannot take the record of the work with it.

## 🎯 USER GOAL set 2026-09-17 — finish the dispatch queue · refresh the webapp · cut a release

**Standing directive from the user:** *"finish task dispatch and also work to make the webapp more appealing and updated, once all is done cut a release."* Running under it: WS6-T5 and WS4-T13 dispatched in parallel worktrees (below); the release is the endpoint and **collides with the open E24 version ruling** — see that entry. The foreman will not pick the version number unilaterally; it goes to the user as a single narrow question at the point of cutting, per E24's own terms.

**Parallel execution, foreman decision:** two specialists in isolated worktrees on **disjoint files** — WS6-T5 owns `docs/*.{html,css,js}` and `pages.yml`; WS4-T13 owns `scripts/ingest_oecd_aim.py`, its tests and `auto-refresh.yml`. Neither touches `data/`, `schema/` or `ingest/`. The main tree stays on the escalated `ws4/t10-normalize-url` branch, untouched. Precedent: the user's 2026-09-15 authorization for WS4-T11 to run parallel with WS4-T10 under AGENT_TEAM.md §7.

- **WS6-T5 · Website: scale, accessibility, integrity** (P2, L) → distribution-engineer, branch `ws6/t5-website`. Plan criteria verbatim, **with one criterion deferred by foreman ruling: "per-corpus pages" depends on the WS1 corpus split, which is Phase-2 work that has not started — there is one corpus today, and inventing a split would be undeclared scope.** The brief requires the page to be built so per-corpus routing can be added later. The user's "more appealing" half is scoped as a real design pass (`frontend-design` skill) over a no-build static page, under invariant 6: every published count stays inside its `<!-- stats:… -->` marker pair, which `scripts/stats_docs_lib.py` rewrites.
- **WS4-T13 · OECD crawl budget** (D25c) → pipeline-engineer, branch `ws4/t13-crawl-budget`. **Foreman scope ruling: the build-guard half of D25(c) is ALREADY IMPLEMENTED** in WS4-T10 Phase A (`75825299`, unmerged) and must **not** be rebuilt — the specialist is instead asked to read it, confirm it satisfies D25(c)'s clause, and report any merge conflict. Scope is the crawl budget only: skip numeric slugs (~1,852 of the 3,000-URL window per D25c), evidenced per-URL against the real population rather than assumed, with a measured — not estimated — headroom change against `timeout-minutes: 60`, and a contract test proven to fire.

**Both briefs carry agreement 6 explicitly** (name the input that makes each check fail; prove it fires by corrupting the input) and the active invariants. Both are code/site-only: **no published data moves while D25(a)'s freeze holds.**

## ⚠ ORDERING HAZARD found by the foreman 2026-09-18 — merging the WS4-T10 fix ARMS an unauthorized 301-row data change; the release cut is what would fire it

**The hazard, stated plainly.** D26(b) merges WS4-T10's `normalize_url` fix to `main`. The fix changes how the build keys URLs, so **the next `make build` on `main` produces 13,361 rows instead of 13,060** — the 301-row unmerge. That is exactly the data change **D25(b) reserved to the user** ("the unmerge design for already-published rows … comes back to the user before any data change"), and WS4-T15 has not been designed, let alone ruled on.

**Why this surfaces now and not later:** the **release cut procedure itself rebuilds.** The v2.9.0 cut (`be020058`) bumped the version constant in `scripts/merge_and_dedupe.py` and then **rebuilt so `data/stats.json` was regenerated rather than hand-edited**, per the standing never-hand-edit rule. Run that same procedure on a `main` that already carries the fix and the cut silently performs the unmerge — a release that changes 301 rows while its notes describe a version bump. **Every check in the cut procedure would pass**, because the v2.9.0 recipe verifies "0 corpus rows changed by the cut" against the *post-rebuild* tree: the aggregate form of agreement 6(d), on the exact procedure this project uses to publish.

**Foreman sequencing decision, to keep both rulings intact:**
1. Merge **WS6-T5** (site only) and **WS4-T13** (ingest code only — a rebuild does not re-crawl, so data cannot move) once each is gated.
2. **Cut `v2.10.0` while a rebuild is still a no-op**, i.e. **before** WS4-T10's fix reaches `main`. Verified today that a full build on `main` is reproducible and moves nothing (WS4-T13's specialist ran `parse_existing → merge_and_dedupe → render_markdown → validate` and got a clean `git status` at 13,060/13,060 valid).
3. **Merge WS4-T10's fix after the cut** — satisfying D26(b) — and treat the armed unmerge as WS4-T15's opening condition.

**What still stands between an armed `main` and a published unmerge**, recorded so nobody mistakes the barrier for a design: the fixed build **fails `validate.py` (exit 1, INC-14614)** [R, gate BOUNCE #1 defect 3], the E21 tripwire fails closed, and D25(a) is policy. That is **three accidental barriers and no deliberate one.** WS4-T15 owes a deliberate guard; until then, **no rebuild is to be committed on `main` after the fix merges** except by a task that names the unmerge as its subject.

## 🔁 WS4-T10 CORRECTION PASS (per D26a) — **✅ FINAL PASS (red-reviewer, 2026-09-18, on `9324cdf7` — the merge SHA) — HELD FOR MERGE UNTIL AFTER THE v2.10.0 CUT (ordering hazard above)**

**─── FINAL VERDICT — red-reviewer, 2026-09-18, on `9324cdf7`: PASS, no defects, no outstanding advisories ───** The gate was asked to attach its verdict to the exact SHA that merges, rather than to `53556e3d`, because **a PASS on a superseded commit is not a PASS on what ships.**

**What the last two fixes corrected** (the gate's own disclosed advisories, closed in the artifact rather than deferred to the board — *"a WS4-T15 reader inherits an accurate document instead of an accurate board note about an inaccurate document"*):
1. **§8.2's advisory-2 note no longer overclaims.** It said nothing in `validate.py` "or elsewhere" catches a silently-deleted deprecation record, which contradicted §8.3's own preserved text twelve lines below. Now: *"nothing in the build or CI path to catch it"*, naming `ws4t10_phaseb_delta.py`'s `deprecations_deleted_or_modified` as catching it **only in a manual two-tree audit**. **Gate verified on three independent points [R]:** that script appears nowhere in `Makefile` or `.github/workflows/`; CI *does* run `validate.py`, but its `check_integrity` is referential-only and never compares against a prior build, so a deleted record simply vanishes while survivors still resolve; and the script's own docstring says it reads two already-built trees "from two detached scratch worktrees". **The claim correctly does not overclaim that CI is empty — it says nothing there catches *this*.**
2. **§8.4's retraction no longer oversweeps.** "Nothing about §8.2 is currently correct as specified" became a retraction of the **persistence/precedence mechanics only**, explicitly exempting the `reason: "resplit"` record type and the `resolve_id` list-valued-`into` crash finding as standing findings WS4-T15 inherits. **Gate [R]: the characterisation matches §8.2's note verbatim, no more and no less.** This mattered — a blanket retraction would have told the successor task to discard its own starting material.

**NEW PRECEDENT — relative pointers, not line numbers, in dated correction notes.** The specialist used "above" / "below" / "§8.3's preserved text" rather than line references, because an earlier edit had already made a hardcoded reference drift. **The gate agreed and went further, against its own text:** *"my own BOUNCE #4 defect list cited `:812-815` and `:787`, and those line numbers had already drifted by the time the fix landed — the same hazard, in my own text. A document under append-only correction re-numbers itself every pass; a hardcoded line reference is a check that silently stops pointing at what it names."* **Adopt for dated correction notes generally.**

**Evidence [R] (gate):** `difflib` opcodes `53556e3d→9324cdf7` = exactly **two** hunks, both inside the 2026-09-18 notes; the five removed lines are precisely the two overstatements and nothing else. Protected originals unchanged **at the merge SHA**: §8.2/§8.3 preserved bodies byte-identical to `be0d037f` once only the correction blockquotes are removed; §7.3 item 1 still verbatim from `9c24d181`. **Frozen code still frozen** — `git diff --stat be0d037f..9324cdf7 -- scripts/ tests/ data/ schema/ ingest/ .github/` **empty**. **Suite re-run by the gate itself, not taken from the report: 341 passed in 18.51s** (the specialist's 326s wall-clock was environmental). No strays; origin at `9324cdf7`.

**Merge ordering reaffirmed by the gate in its own words:** merging arms the 301-row unmerge and the cut rebuilds, so **WS6-T5 → v2.10.0 cut → this branch. D26(b) is satisfied by merging it, not by merging it first.** Standing instruction it repeated: **re-run `git status --porcelain` at the moment of merge** — a pre-gate check attests to a moment, not to the merge.

## 🔍 THE BLOCKED STRING, CLASSIFIED 2026-09-18 [R] — a GitHub pre-signed URL, not a credential → **NEW TASK WS4-T18 (P3)**

**What it actually is.** The `AKIA…` match sits inside a URL pasted into the **upstream CVE-2023-36464 description**, in `INC-11516`'s `description` field:
`https://objects.githubusercontent.com/github-production-repository-file-…?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA…%2F20230627%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230627T201018Z&X-Amz-Expires=300`

**Four measured facts, each independently checkable:**
1. **`X-Amz-Credential` carries an access key *ID* — a public identifier, not a secret.** The secret never appears in a pre-signed URL; only a signature derived from it does. **Verified: no 40-character secret-key pattern exists anywhere in that description.**
2. **It is GitHub's key ID, not this project's** — host `objects.githubusercontent.com`, a GitHub attachment-download link for a PoC file referenced by the advisory.
3. **It expired on 2023-06-27.** `X-Amz-Expires=300` (five minutes) from `X-Amz-Date=20230627T201018Z`.
4. **It has been public since 2026-06-10** (`afea57e8`, PR #50) and **is present in the published `v2.9.0` tag**, hence in that release's Zenodo deposit. **Blocking this push protects nothing that is not already published.**

**Conclusion:** push protection is working correctly on a pattern that in this instance carries no secret. **The unblock decision is the user's** — it is their repository's security control and the judgement belongs on their record, not the foreman's.

**NEW TASK WS4-T18 (P3) — strip query strings from imported reference URLs in descriptions.** Owner **pipeline-engineer**. Pre-signed and tracking-laden URLs are noise in a published dataset and **will re-block every future push touching `data/incidents.json`** until allowlisted or removed. **This is a data change under the D25(a) freeze and needs its own ruling before execution** — boarded, not actioned. Note the overlap with WS4-T10's `normalize_url` work: both concern query strings in URLs, but this one is about *stored description text*, not merge keys.

## 🛑 v2.10.0 CUT COMPLETE THROUGH STEP 5 — **PUBLISH BLOCKED BY GITHUB SECRET SCANNING, ESCALATED TO THE USER 2026-09-18**

**Recorded on this branch, not `main`, deliberately:** any push to `main` now carries the blocked cut commit `967fc04b`, so `main` cannot receive board records until the block is resolved. This entry moves to `main` with the rest.

**What is blocked.** `git push origin main` was rejected by **GitHub push protection (GH013)**: an **Amazon AWS Access Key ID** pattern at `data/incidents.json:711837`. **No tag exists** — the command chain stopped at the failed push, so `git tag` never ran; `git tag -l v2.10.0` is empty. **Nothing was published.**

**Established before escalating [R]:**
- **The cut did NOT introduce it.** `git diff origin/main HEAD --numstat -- data/incidents.json` = **1 line changed** (the version string). The same pattern count (1) exists on `origin/main` today.
- It sits in **INC-11516**, inside the imported description for **CVE-2023-36464** (pypdf infinite loop), `added: 2026-06-10`, sourced from upstream CVE data.
- **It is not a placeholder:** not the canonical AWS documentation example key and does not end in `EXAMPLE`. Masked: `AKIA************H53A`.
- **It is confined to the full file.** Present in `data/incidents.json`; **absent** from `data/incidents.min.json`, `docs/data/incidents.min.json`, and **`src/genai_incidents/data/incidents.min.json` — the PyPI-packaged copy.** So it is **not** in the artifacts this release would publish to PyPI or Hugging Face.

**Why the foreman stopped rather than resolving it.** Three independent reasons, any one sufficient: bypassing secret scanning is a **security control on the user's repository**; the string may be a **third party's live credential** republished from upstream, which is a disclosure matter belonging to WS5's PII/redaction policy; and redacting it edits **published data under the D25(a) freeze**. Options put to the user: allow via the GitHub unblock URL, research the upstream CVE record first, or redact as its own ruled task.

**Everything else in the cut is done and verified [R]** — see commit `967fc04b`. Highlights: all **five** version strings moved together; full `make build`; `validate` exit 0; suite 339; and the field-level check **matched the gate's expectation recorded BEFORE the run** — only `version` changed, `generated` stayed `2026-07-31`, 13,060 entries, ID set unchanged, **zero** entries differing.

**Two checks proved themselves during this cut, which is the point of having them:**
1. **Checklist step 5 caught the exact failure it was written for, on its first use.** README's `stats:version` marker had auto-updated to `2.10.0` while the paragraph around it still described v2.9.0's licensing work, dated it 2026-07-31, and linked to v2.9.0's notes — **the v2.9.0 cut's documented mistake, reproduced verbatim.** Rewritten to describe this release.
2. **Invariant 6's drift check then fired on the foreman's own rewrite.** `6,162` is a comma-formatted number outside a `stats:` marker, and `NUMBER_LITERAL_RE` cannot distinguish a historical taxonomy count from a corpus total. **The check was right.** The sentence now states the ratio (7.87×, "roughly eight times") and routes readers to the notes for both exact figures. **That check has now been seen to fail — the only basis on which agreement 6 permits citing it.**

## 🎨 WS6-T5 — **✅ PASS (red-reviewer, 2026-09-18, on `52e3a530`) — NO DEFECTS — merge QUEUED behind the v2.10.0 publish, deliberately**

**Why it is queued rather than merged:** the v2.10.0 release notes state this work *"has not merged"* — true now, and it must stay true until the Release body is published, which was the notes gate's own blocking condition. Merging first would ship a false sentence in a permanent public artifact. **Order: user rules on the secret-scanning block → publish → merge this (which deploys the site) → merge WS4-T10.**

**All four BOUNCE #2 defects fixed, verified by the gate's own measurement:**
- **D1:** root cause was `th.sortable > .caret` overflowing its own header cell. Fixed by **containing** it — `position: relative; overflow: hidden` on the `<th>` plus the caret positioned absolutely inside already-reserved padding — **not** by widening the column, which would have re-opened the width budget the fixed layout exists to close. `.table-wrap` **355/348 → 348/348**; sorted-by-Severity caret `visibleFraction: 1, fullyContained: true` (was 0.196); `overflowCount: 0` in both themes. **`WRAP_TOLERANCE_PX = 0`, and the gate proved it fires rather than accepting the specialist's probe:** +1px → exit 1, +2px → exit 1, +0 → exit 0. Both false comments corrected in place, naming the real cause and stating the old claims were false, with the superseded wording preserved.
- **D2:** discovery rewritten to parse the markup itself. **8 selects discovered, up from 3 checkable.** The gate ran **ten adversarial mutations**: the original repro (bare `<select>`, markup only) now **exits 1** where it previously passed; multiline attributes, single quotes, whitespace, empty values and the comment-then-real-select shape are all caught; a commented-out select correctly passes.
- **D3:** focus retained in **both** directions — Enter expands, Enter again collapses, `sameNode: true` throughout; Space likewise; last-row-on-page likewise. The keyboard-only retry path works and returns focus to the row toggle, which is the right destination since Retry is destroyed in the re-render.
- **D4:** the dialog text is **derived** from `DETAIL_FIELDS`/`CSV_COLUMNS`. The gate proved it by **moving the field in a scratch copy** and watching the message follow — it cannot drift.

**Advisories (a)(b)(e) all verified:** the trust strip now says *"every entry carries a source reference"* with the 13,060/13,060 figure **and** the 51%-aggregator caveat recorded together (oecd.ai 3,667, aiaaic.org 1,516, incidentdatabase.ai 1,464). The axe gate emulates both themes with a guard asserting the resolved `data-theme` against the request, and gates on `critical` **or** `serious`. **One test proves both:** reintroducing the accent sort header gives 0 in dark and **1 serious in light**, both viewports, exit 1 — a no-op emulation would make all four rows read alike, so the light-only split shows the emulation is real, and `serious` catches what the critical-only gate shipped clean the first time.

**Invariant 6 verified NON-VACUOUSLY:** all three `stats:` markers survive in identical form; planting a bare `13,060` in the **new** trust strip produced `::error::docs\index.html:74: hardcoded total … outside any marker`, exit 1; restored, exit 0.

**TWO METHODS WORTH ADOPTING, both from this gate:**
1. **Verify a merge commit by recomputing it, not by reading its diff.** `git merge-tree --write-tree 1d04578d ab19718f` → `4bd8fa6f…`, and `git rev-parse 52e3a530^{tree}` → the same hash. **Identical trees prove the merge contains no hand edits** — something a diff read cannot establish.
   **Why it discriminates, in the gate's own words, because this is the generalisable part:** *"Reading a merge diff tells you what the merge contains; it cannot tell you whether a human edited a file mid-merge, because a hand edit and a legitimate incoming change look identical in the diff. Recomputing the tree from the two parents and comparing hashes fails loudly if anything was touched."* It then named the property that makes it a check at all — **its output differs between the passing and the failing case** — and tied it to the same reason this project's gates use `git symbolic-ref` rather than `rev-parse` to assert HEAD. That is agreement 6's test ("name the input that would make it fail") applied to a verification method rather than to a script. Everything from `main` is byte-identical; the only main-side path the branch touches is `pages.yml`, which is WS6-T5's declared ownership.
2. **A gate disclosing the limits of its own instrument.** Its `th.scrollWidth > th.clientWidth` sweep flagged Severity at 6px; instead of filing it, it chased it to ground and **reported it as a false positive of its own heuristic** — the text legitimately extends into reserved `padding-right`, which registers as scroll overflow while rendering perfectly (confirmed on pixels at 5× DPR: full label, caret visible, underline present). Recorded here explicitly so nobody re-raises the 6px later.

**Advisories → NEW TASK WS6-T10 (P3), not amended into a gated commit:** (1) `check_dead_filters.py` discovery is **case-sensitive** — `<SELECT ID="tier">` unannotated passes; `re.I` is a one-character fix. (2) `data-filter-field="none"` can silence a genuinely dead filter — it needs deliberate mislabelling and prints a visible skip line, so the design stands, but **the hatch exists**. (3) Discovery is window-bounded by the `.filters` div through `id="filter-chips"`; a select added after the chips container would not be found (all 9 are inside today). (4) Focus drops to `BODY` when a filter change removes the row holding focus — default browser behaviour, not reachable in a real flow, not a regression. (5) `.table-wrap` still overflows at desktop (1352/1176) under `overflow-x: auto` — by design and scrollable; the 380px gate does not run there.

## 🎨 WS6-T5 — BOUNCE #2 history (superseded by the PASS above) — on `f5f88795`

**Defect 1 — the 16px tolerance was sized on a MISDIAGNOSIS, and the fix's own comments assert a falsifiable claim that is false.** The specialist attributed a 7px `.table-wrap` overhang to Chromium `table-layout:fixed` column rounding. The gate enumerated **every** element overflowing the wrapper: **exactly one — `span.caret` in the Severity `<th>`**, overhanging by precisely that 7px, while the visible cells sum to **347.6** inside `clientWidth` 348. **The cells fit; the glyph does not.**
- **The comments' supporting claim is directly falsified [R]:** both files state `wrap.scrollLeft(7)` "shifts no rendered pixel (verified with a screenshot diff)". Measured: `rowLeftBefore 16.203 → rowLeftAfter 9.203, moved: 7`.
- **User-visible [R]:** clicking Severity at 380px puts the caret at `l:362.5 r:371.2` against a clip edge of `364.2` — `caretVisibleFraction 0.196`, ~80% cut off, with `overflow-x: hidden` leaving nothing to scroll to. **Sorting by severity on a phone loses the direction indicator.**
- **Why the wrong cause survived:** the specialist's three controls — `border-collapse: separate`, hidden columns removed, thead de-stickied — **all vary table layout**, so none could discriminate a caret hypothesis. **Agreement 6's "a different route, not a more careful one", demonstrated by counter-example.**
- **The gate quantified rather than merely condemned:** the check still fires above ~9px of additional overflow (exit 1 at +15, +17, +50, +100). *"The defect is not the width of the window — it is that a real clipped glyph is sitting inside it right now, documented as noise."*
- **PROVENANCE [R] — this branch introduced it, so it blocks the merge:** `origin/main:docs/style.css` has no `table-layout: fixed`, no fixed column percentages, and `overflow-x` only at `:549` with no `hidden`; the caret rules at `:571-573` are byte-identical. **On `main` the caret is auto-sized and reachable by scrolling.**
- **Ruling (gate, foreman concurring):** contain the caret, do **not** widen the column — widening re-opens the width budget the fixed layout exists to close and fixes one glyph rather than the class. Then **`WRAP_TOLERANCE_PX = 0`**, because the measured noise floor is **0**; after the real fix a tolerance absorbs nothing and is purely a blind window. **Demonstrate 0 by injecting +1px, not by asserting it.**

**Defect 2 — `check_dead_filters.py` does not fire on the defect it was written for.** Discovery is a hand-maintained dict of three ids. **Reintroducing the dead Tier control as markup only — what a contributor would actually do — gives `PASS, exit 0`** [R]; it exits 1 only when the map entry is *also* added by hand. The failure path works; **discovery is the hole.** Its docstring at `:16` claims a `data-filter-field` mechanism that **exists nowhere** — `git grep` returns one hit, the docstring itself. WARN/FAIL split could not be inverted and is kept.

**Defect 3 — keyboard users can expand a row but never collapse it [R].** The toggle re-renders the table and replaces the button node, so after the first Enter `sameNode:false` and `activeElement` is `BODY`; every later Enter is a no-op and the user needs **23 Tab hops** to return. Mouse works. **axe reports 0 violations because axe cannot observe focus loss on activation** — fails A4's "keyboard-operable" and WCAG 2.4.3.

**Defect 4 — the CSV failure dialog states something the same commit's own A2 fix made false.** It promises blank *Primary Reference* cells; A2 moved that field into `CORE_FIELDS`. Real export with a shard aborted: `rows 972 | blankDesc 972 | blankTags 972 | **blankRef 0**`.

**Advisories:** **(a)** the trust strip's "every entry cites a primary source" is **measured and true** (13,060/13,060 carry a non-empty http(s) reference) **but 51% (6,647) resolve to aggregators this project treats as upstream** — oecd.ai 3,667, aiaaic.org 1,516, incidentdatabase.ai 1,464. **Foreman requiring the softer "carries a source reference"**, keeping the 100%, given this project's overclaim history. **(b)** `check_axe.js` never forces a theme, so **CI only ever scans the headless default** — the "both themes" result is a manual claim CI will not hold (the gate verified all four combinations itself: clean). **(e)** the axe gate fires only on `critical`, matching the plan verbatim — **but the one real regression this task hit was `[serious]` and would have shipped.** Foreman requiring `serious`. **(c)** the active-sort underline is genuinely a non-text component under 1.4.11; the specialist's self-caught revert was correct. **(d)** branch is behind `main` with zero file overlap — merge, do not rebase.

**Note for the record:** the specialist reported the `Skill` tool absent from its tool set and located the design skill file with a bounded `find`, reading it directly rather than skipping the guidance — a worked-around capability gap, not a shortcut.

## 🔢 WS4-T15 INHERITS AN UNRECONCILED ±1 — found 2026-09-18 by the release-notes gate (its advisory A9), **must be settled BEFORE WS4-T15 designs against either number**

**The conflict, inside `docs/specs/WS4-T10-unmerge-design-2026-09-15.md`:**
- `:103` — **"control 13,060 unique rows; fixed 13,361 (+301)"**, the measured corpus delta.
- `:408-411` — the §2 distribution table sums to **349 successor rows from 47 old rows**, and states "47 of those 349 keep an existing id and **302** are freshly minted (exactly the measured new-only count)". 47 old rows resolving to 349 is a net **+302**.

**Both cannot be right, and Option 2's consumer-impact arithmetic is built directly on 349.** The document *does* reconcile a different confusion at `:676-687` (that 349 is a count of successor rows, not of IDs needing no deprecation record) — **but it never reconciles +302 against +301.**

**Foreman hypothesis, UNVERIFIED — offered as a lead, not a finding [A]:** the gap is probably **INC-07738**, which the fixed build retires into a fresh ID (`INC-14757`) **without adding a row** — a replacement rather than an addition. Earlier gate measurements are consistent with this: "changed rows 48 → 47" and exactly one new deprecation record, `INC-07738 → INC-14757`. If INC-14757 is among the 302 "freshly minted" rows while INC-07738 leaves, the net is +301 with 349 successors intact and both figures survive. **WS4-T15 must verify or refute this per-entity, not by re-running either aggregate** — it is exactly the shape agreement 6(d) warns about, a total that balances while the composition inside it is described two ways.

**Not a defect in the v2.10.0 release notes**, and the gate said so explicitly: the notes cite `+301` correctly and the load-bearing distinction survives in the published prose — *"the size of the population a future unmerge would split back out"*, plus *"Published IDs and redirects are unchanged by v2.10.0."*

## ⏸ SESSION INTERRUPTION 2026-09-18 — both specialists killed mid-task by a session rate limit

Recorded because the recovery shape matters and the tree looked misleading afterwards. The **website design/fix specialist** and the **release-notes drafter** both terminated on an API session limit (HTTP 429), the drafter mid-research and the designer one edit into `docs/index.html`. **Neither had committed anything**, so nothing reached origin and the only trace was an uncommitted ` M docs/index.html` in an orphaned worktree — *which reads exactly like a specialist idling with work in progress rather than a dead one* (working agreement 3's known failure shape, arriving by a new route). Both were re-dispatched from scratch with full self-sufficient briefs once the limit reset; no partial work was salvaged, and none was worth salvaging. **WS4-T10's and WS4-T13's completed work was unaffected — both were committed and pushed before the interruption**, which is agreement 1a doing precisely the job it exists for.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer, 2026-09-18, on `53556e3d`: PASS ───**

**⚠ The gate corrected the foreman's process, and the correction is kept because it generalises.** The foreman's pre-gate check reported a clean tree; **when the gate looked, the tree was dirty** — the specialist was actively writing the same file (mtime 14 seconds earlier), and those edits landed as `53556e3d` mid-review. The gate verified the branch **tip** rather than the SHA it was handed. Its instruction, now standing practice: *"a pre-gate check taken before an agent goes idle attests to a moment, not to the merge — re-run `git status --porcelain` before merging."* **Foreman re-verified at merge time [R]:** tip `53556e3d`, porcelain empty, frozen-code diff empty, origin matches.

**Three judgement calls the gate was asked to rule on, all ruled, all recorded as precedent:**
1. **Bucket 1 — the two live §7.2 references are CORRECTLY left unflagged**, verified against the note rather than accepted: §8.2's superseding note at `:823` says verbatim that *"§8.2's proposed record type (`reason: \"resplit\"`) and the `resolve_id` list-valued-`into` crash finding below **both stand as findings**"*, and `:627` references precisely that exempted half. `:616` ("corrected in §8.1/§8.2") is true because §8.1 is live and corrected.
2. **In-place amendment of a same-day, unmerged, self-authored dated note is NOT an agreement-4 violation** when it refines only the routing pointer and retracts no claim — *"that is agreement 4's live-surface half"*. The protected pre-2026-09-18 originals were verified untouched, not assumed.
3. **D4's inline parentheticals** interpolate into preserved sentences rather than appending, which is acceptable: they add no claim, retract nothing, and match `:771`'s established form.

**Evidence [R] (gate):**
- **All four defects fixed as pure appends** except D4's two inline flags — `difflib` opcodes over `efd72c51→17be38b9` = 3 inserts (banner `:58-65`, §8.4 `:1029-1035`, §8.5 `:1047-1056`) + 2 one-line replaces. **Nothing above any note rewritten.**
- **Protected originals byte-unchanged at the tip:** §8.2/§8.3 preserved bodies byte-identical to `be0d037f` once only the new `> **[2026-09-18 correction` blockquotes are removed; §7.3 item 1 still verbatim from `9c24d181`; `53556e3d`'s two hunks removed **only** lines beginning `>`.
- **The sweep is now real** — the gate enumerated **every** §8.2/§8.3 reference at the tip with section attribution (**23 hits**); every live one is flagged or immediately followed by a dated correction, and the only unflagged live ones are bucket 1's two, ruled correct.
- **Independent vocabulary sweep by a different route** (`chronological` / `latest-dated` / `zero code change` outside §8.2–§8.3): 2 hits, both inside the new correction notes. Clean.
- **Bucket 4 confirmed and corrected upward:** the audit doc has **5** `resplit` mentions, not the specialist's 4 (`:146,148,151,152,218`); all assert only that a record is *needed*, none asserts the retracted mechanics, so leaving that file unchanged was right.
- **§8.5 now reads correctly as a decision surface — the defect that mattered.** A user arriving to rule reads (d)/(e) and immediately below that the rule is false, why (file order not date; 57 inversions), that nothing is left to ratify, and that WS4-T15 decides. **Leaving (f) unaffected is correct**: §8.4's INC-07738 diagnosis is untouched by the supersession.
- **Frozen code still frozen:** `git diff --stat be0d037f..53556e3d -- scripts/ tests/ data/ schema/ ingest/ .github/` **empty**. Suite **341**. Scope: 1 file in both commits. No strays.

**MERGE STATUS — deliberately NOT merged yet.** The branch is PASS-clean and pushed, but merging it **arms the 301-row unmerge** (see the ordering-hazard entry above), and the v2.10.0 cut rebuilds. **Merge order: WS6-T5 → cut v2.10.0 → then this branch.** D26(b) is satisfied by merging it, not by merging it first.

## 🔁 WS4-T10 CORRECTION PASS (per D26a) — `efd72c51` — BOUNCE #4 history (superseded by the PASS above)

**Pass scope:** prose-only, two committed artifacts, so the branch merges without carrying false claims onto `main`. **Code and tests frozen** — the prior gate's byte-identical-build evidence is only valid while they are untouched. Specialist: a **fresh** pipeline-engineer (agreement 3's replace-over-re-prompt).

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-18, on `efd72c51`: BOUNCE #4 ───** *"Everything the brief explicitly required is done, and done correctly — I verified every number, every restoration, and every byte. The bounce is for a sibling of the exact claim the pass existed to remove, surviving in live (non-superseded) text, including on the user-decision surface."* Remedy ≈10 lines of appended dated notes.

**Defects — all the same shape, all in `docs/specs/WS4-T10-unmerge-design-2026-09-15.md`:**
1. **:1019-1022 (§8.5) ASKS THE USER TO RATIFY THE FALSIFIED RULE** — "(d) whether to accept the `reason: \"resplit\"` record type and its precedence rule (§8.2) **as specified**". §8.5 carries no supersession marker **and is the document's escalation surface to the human lead**; the same commit proves at :807-811 that precedence is "file order, not date" and the file is "not chronological (57 date inversions)". No pointer between them. **Had this merged, the surface asking for the user's ruling would have carried the claim the pass existed to remove.**
2. **:1012-1015 (§8.4)** — "so it **remains correct** either way" about the superseded §8.2 model. §8.4 is live and is exactly where WS4-T15's `ids_seen` follow-up is specified, so a WS4-T15 reader lands there and reads that §8.2 stands. The narrow independence claim may survive; those words do not.
3. **:49, the top-of-file Revision-3 banner** — still presents §8.2/§8.3 as the live specification, using the exact "append-only redirect model" characterization :812-815 retracts. First thing a WS4-T15 reader sees.
4. **:787** — a live present-tense "§8.2 **recommends**…" sixteen lines after :771's correctly flagged "§8.3's guard design **(superseded below)**"; same shape weaker at :675 and :617. **The gate's inference, which the foreman shares: one flagged and its sibling not is the evidence this was a targeted fix rather than a sweep** — the failure the brief named.

**Ruling the gate was asked for and gave — the table-cell substring question (agreement 4):** **the specialist is right and the test passes.** The gate applied containment of the original **cell body** with the trailing `|` stripped, not of the full line, reasoning that *"requiring pure-context diff shape would forbid marked corrections inside single-line markdown rows entirely … pushing future correctors toward restructuring the table, which destroys more of the record than it preserves. The load-bearing test is that the original assertion survives character-for-character with the addendum visibly marked and dated."* Only byte delta per cell is the trailing `|` giving way to `.` before the note. **Precedent for future correction passes.** The specialist raised this caveat itself rather than hoping nobody checked.

**Evidence [R] (gate):**
- **Corrected claims are TRUE, re-derived per-row not by aggregate:** INC-08139 92 sources / 90 rows, histogram `{1:88, 2:2}`; INC-08185 65 / 63, `{1:61, 2:2}`; both multi-rows are INC-00554 and INC-14607; INC-00497 1-of-8; INC-03128 2-of-10. All four published figures reproduce exactly.
- **No overcorrection:** exactly 4 of 8 carry `current_target_still_holds_any_sources: true`, and exactly those 4 have their target in `lands_on_new_rows`. `WRONG_AFTER_FIX` correctly left standing for all 8, with an accurate stated reason.
- **§8.2/§8.3 originals byte-unchanged:** removing only the new blockquote (27 / 19 lines) leaves both bodies byte-identical to `be0d037f`. §7.3 item 1's two-line original is contained in HEAD and absent from `be0d037f`.
- **Frozen code holds:** `git diff --stat be0d037f..HEAD -- scripts/ tests/` **empty** — the gate checked both whole trees, broader than the two named files. Suite **341**.
- **Superseding notes verified by READING CODE, not rerunning the build:** `:1874-1875`'s comment says "earliest" while the comprehension keeps the **last**; selection precedes the `sorted((from,date))` rewrite at `:1894-1897`, so precedence is file order; the committed file has 1,051 records / 1,051 distinct `from` / 0 duplicates, **so a second record for an existing `from` must delete one — the 1,053→1,052 result is entailed, not incidental**; `{out-of-scope 704, merged 288, orphaned 59}` → 288−8 = **280**; **57** date inversions. Notes accurate, neither overstated nor softened.
- **The list-`into` crash finding is not buried:** at `:876-892` inside superseded §8.2 but explicitly exempted by `:812-813`, and independently on this board.
- **Audit doc swept to the same depth and CLEAN** — the gate did not stop once it had four: it ran a formulation sweep across **both** files and enumerated every §8.2/§8.3 cross-reference.

**Advisories:** (1) neither doc names **WS4-T15** — fold the ID into the same notes so the successor is findable from the record *(dispatched)*; (2) because the build rewrites `id_deprecations.json` from a one-record-per-`from` map, **invariant 9 has no enforcement machinery today** — a colliding record is deleted silently with nothing to catch it *(routed to WS4-T15 item 1, and into the §8.2 note)*; (3) merging now and correcting later would be legitimate **but is the user's call, made knowing §8.5(d) currently asks them to ratify a rule this same commit disproves.**

**Foreman action:** fix dispatched to the same specialist (short, precise, early in its context — re-prompt, not replace), **plus the document-wide sweep it skipped**, with instructions to justify anything left unflagged rather than flagging reflexively. **User informed rather than silently redispatched**, per protocol step 6 and the gate's own request; the user's standing goal directs the queue to keep moving, and this is execution of D26(a), not a new decision.

## ⚖ D26 — THREE USER RULINGS, 2026-09-17, on the WS4-T10 BOUNCE #3 escalation and the open E24 version question

**(a) WS4-T10: SPLIT THE DESIGN OUT.** WS4-T10 keeps the code fix and corrects its false claims; the remediation design for already-published rows becomes **a new task**. Rationale as put to the user: the gate established that defect 1 cannot be fixed inside WS4-T10 — it needs a deprecation-persistence change in `merge_and_dedupe.py` **plus a schema decision on the superseding-record identity key** — and defect 2's guard cannot exist in any form until retired IDs' `source_ids` are persisted in the repo (advisory A-g: **280 other `merged` records need that same artifact**). A fourth attempt was explicitly rejected as spending another cycle to reach the same escalation.

**(b) WS4-T10's Phase A code fix MERGES ON ITS OWN**, ahead of the remediation design. It is gate-clean across three attempts and is **condition (1) of the D25(a) freeze lift**. Published data does not move: the fix changes future builds only, and **condition (2) — reviewing every new `merged` deprecation a refresh would write — still holds the freeze shut.**

**(c) E24 RULED: cut `v2.10.0`, with loud release notes.** Treats the stable `LLM01`–`LLM10` code space as not an API break, **which is defensible only because the notes are unmissable about the semantic break** — that condition is part of the ruling, not a style note. `v3.0.0-beta` and `v3.0.0` stay reserved for Phase 2 and Phase 3 as the plan commits them. This closes the version half of E24 and resolves the label contradiction recorded below (`data/incidents.json` carrying 2026 codes while labelled v2.9.0).

**Foreman consequences, recorded so they are not re-litigated:**
- **New task WS4-T15 · superseding-redirect design and persistence** (P0, owner **pipeline-engineer + schema-architect**, the latter as sole writer of `schema/`). Scope: (1) a deprecation-persistence change so a superseding record survives a rebuild — today `merge_and_dedupe.py:1875` collapses to one record per `from`; (2) the record identity key, **a schema decision that goes to the user**; (3) persisting retired IDs' `source_ids` at deprecation time, without which no integrity guard can run in CI; (4) the `resolve_id` multi-successor gap — a list-valued `into` raises `TypeError: unhashable type: 'list'` today, which breaks Revision 2's own array-valued proposal. **Blocked-by:** WS4-T10's correction pass merging first. Plan task count +1; `MASTER_IMPROVEMENT_PLAN.md` text owed at the next amendment, with WS4-T10…T14.
- **WS4-T10 correction pass dispatched to a FRESH pipeline-engineer instance** (agreement 3's replace-over-re-prompt heuristic — the prior instance is three attempts deep in a long context). Scope is **prose only**, in the two committed artifacts: correct defect 3's false "none still land" claim, restore the text defect 4 rewrote in place, and mark §8.2 and §8.3 **superseded with dated notes rather than deleted or softened**, carrying the two findings WS4-T15 will need. **The code and tests are frozen for that pass** — the gate's byte-identical-build evidence is only valid while they are untouched.

## 🔧 WS4-T13 — OECD AIM crawl budget (D25c) — opened 2026-09-17 — **delivered `35ac4eec`, UNDER GATE**

**Specialist:** pipeline-engineer, isolated worktree, branch `ws4/t13-crawl-budget` off `main` `45d05f4b`. Two files: `scripts/ingest_oecd_aim.py`, `tests/test_ingest_oecd_aim.py`. `git diff main..HEAD -- data/ schema/ ingest/` = 0 lines. Build guard **not** touched, per the foreman's scope ruling.

**Claims to be verified by the gate (dispatched 2026-09-17, read-only):**
- Skip rule `^\d+$` full-matched against the URL's final path segment, partitioned **before** the thread pool, so a skipped URL never opens a socket or spends a rate-limit slot.
- **Measured 1,773 skipped / 1,227 fetchable / 0 other — NOT the ruling's ~1,852.** The specialist reported the real number and explained the gap rather than bending to the figure: the date-hash portion of the top-3,000 window grew in the three days since the E21 audit measured 1852/1148, so **the skip count tracks sitemap growth and is not a constant.** Reporting the measurement over the expectation is the behaviour this board wants; the gate will confirm the number independently.
- Headroom: 0.8210 req/s measured over 20 real fetches → old full window ~60.9 min (**already over `timeout-minutes: 60`**), new ~24.9 min, **~36 min recovered**. Disclosed as a linear extrapolation.
- Test proven to fire (agreement 6): corrupting the regex to `^NEVERMATCH$` gave 5 failures including an end-to-end trap — an uncached fixture URL whose fetch attempt raises through the production path — restored to 35 passed. Suite 339.
- Conduct: ~59% fewer requests to `oecd.ai`, no new egress mechanism, so no `INGESTION_CONDUCT.md` register entry under invariant 5. The specialist deliberately did not edit that doc or the dated WS0-T4 audit (agreement 4).
- **Residual risk the specialist volunteered, unprompted:** the rule assumes what E21 measured — every legacy numeric-slug page has failed the body-shape check with **0 exceptions**. If OECD ever serves a numeric-slug page with the modern body shape, this silently skips it. Recorded as a live assumption, not a guarantee.

**⚠ CROSS-TASK FINDING — `ws4/t10-normalize-url` IS STALE, and the hazard is procedural, not textual.** The WS4-T13 specialist traced it rather than reporting it at face value: `git diff main..ws4/t10-normalize-url -- scripts/ingest_oecd_aim.py` *looks* like T10 reverting WS4-T11's 800 KB-truncation fix, but **none of T10's own commits touch that file** — its last commit there is `3c1e3e9e`, predating WS4-T11's merge (`45d05f4b`). The branch was cut before WS4-T11 landed and never rebased.
- **Foreman merge plan, decided:** merge T10 with a normal `--no-ff` merge, which three-way-merges and keeps `main`'s newer file because T10 never edited it. **Do NOT rebase, reconstruct, or force-push that branch's tree** — that is the route the specialist correctly identified as silently reintroducing the 800 KB bug and dropping WS4-T13's skip logic, with **no conflict marker to catch it**, since there is nothing to conflict with.
- **Post-merge verification is mandatory [R]:** confirm `scripts/ingest_oecd_aim.py` and `tests/test_ingest_oecd_aim.py` on `main` after the merge are byte-identical to their pre-merge `main` versions.

## 🔍 FOREMAN VERIFICATION 2026-09-17 — "is the incident count stale at 13,060?" (user question) — **the count is CORRECT; the corpus is FROZEN; the metadata around it is NOT correct**

**13,060 is accurate [R], by three independent reads:** `len(data/incidents.json["incidents"])` = 13,060; that file's own `incident_count` field = 13,060; `data/stats.json` = 13,060. README renders from `stats.json` through the invariant-6 markers, so no doc drift. **17,498 is a different unit** — OWASP code assignments across 11,556 entries, re-counted in the current file as exactly 17,498, not an entry count.

**Why the count has not moved in 52 days (last data-adding refresh `fe732a14`, 2026-07-27) — two unrelated causes, back to back:**
1. **2026-07-26 → 2026-09-13, a silent CI failure.** `auto-refresh`'s Persist step shallow-cloned with `--depth 1`, so `origin/refresh-state` never existed and the checkout died exit 128 on every run, skipping rebuild, tests and the refresh PR. **8 weekly refreshes produced nothing, invisibly.** Fixed 2026-09-14 (`05f536ff`).
2. **2026-09-14 → now, a deliberate freeze.** The first working refresh tripped the E21 tripwire; the audit found the URL over-merge; D25(a) froze OECD refresh merges until WS4-T10's fix lands and every new `merged` deprecation is reviewed. **The count is frozen by policy, and WS4-T10 is the thaw condition** — which is currently escalated at BOUNCE #3.

**NEW FINDING — freshness metadata did not move with the OWASP migration [R].** The 2026-08-17 migration (`19fa2986`) rewrote 17,498 code assignments across 11,556 entries, yet:
- **no entry carries an `updated` value at or after 2026-08-01** — the corpus maximum is 2026-07-31;
- **`generated` is still 2026-07-31**, although the build defines it as today-if-anything-changed (`scripts/merge_and_dedupe.py:1863`, `generated = today if any_change or not prev_generated else prev_generated`);
- README therefore tells readers "as of the 2026-07-31 build" while the corpus last changed 2026-08-17.

**This no-bump decision is not declared anywhere [R]:** `docs/audits/owasp-llm-2026-migration-delta-2026-08-17.md` discusses superseded releases (:190) but states no decision about `updated`, `generated`, or the version field. Contrast WS4-T12, where "no `updated` bump" is an explicit boarded decision. **Undeclared field-level non-delta under agreement 2**, and an agreement-6(d) shape: every aggregate check passed precisely because no total moved.

**Sharper form, and it is consumer-facing:** `data/incidents.json` self-identifies as `version: 2.9.0` while carrying 2026 codes, and CHANGELOG states that data "published up to and including v2.9.0 … carries 2025 codes." **The file's own label contradicts its contents.** This is the practical edge of the open **E24** version ruling — recorded there, not duplicated as a new escalation. Routing: the `updated`/`generated` question belongs with the version cut; the delta doc's missing declaration is a docs-warden item for the sweep that accompanies the release.

## 🔧 WS4-T10 — query-string URL over-merge (P0, D25b) — opened 2026-09-15 — **⛔ BOUNCE #3 — ESCALATED TO USER (protocol step 6; third bounce, past the two-bounce limit — NOT redispatched)**

**Attempt 3** (pipeline-engineer), HEAD `be0d037f` (pushed) — gated 2026-09-17:
- **`8c25c659`** (part 1/2) — BOUNCE #2 defect 1(a) measurement plus advisories A1–A4:
  - new `scripts/audit/ws4t10_inbound_deprecations.py` + `docs/audits/WS4-T10-inbound-deprecations-2026-09-15.json` (8 inbound deprecations, all classified `WRONG_AFTER_FIX`), recovering each retired ID's original `source_ids` through a human-supplied commit-SHA table and `git show <sha>:data/incidents.json`;
  - the delta MD rows for INC-07736 and INC-01271 corrected with dated notes;
  - **A1** delta script now compares full deprecation records both directions and adds a gained-`source_ids` check; **A2** the N5 mutant test now uses the real `_com_liferay_…_redirect` shape and the unevidenced `p_p_*` entries were removed; **A3** control pinned to `eeb7ca9c`; **A4** build-clock dates documented.
- **`be0d037f`** (part 2/2) — design-doc **Revision 3** (§8): §8.1 the measurement; §8.2 an append-only `reason: "resplit"` record claimed to need **zero `resolve_id` change**; §8.3 a deprecation-integrity guard; §8.4 the INC-07738 root cause (the `ids_seen[0]`-already-claimed fallback, blast radius 1, deliberately not fixed); §8.5 what remains a user decision.
- **Suite:** 341.
- **Foreman pre-gate check [R]:** clean tree, no stash; `git diff eeb7ca9c..HEAD -- data/ schema/ ingest/ .github/` empty; 341 passed; §8.1–8.5 present; inbound JSON is a list of 8.
- **Board gap, recorded honestly:** the user's authorization to run a third attempt after the BOUNCE #2 escalation is **not captured in any commit** — the session that carried it ended. The attempt-3 commits are the only evidence it was given. Not reconstructed here; if the wording matters later it must come from the user.

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-17, on `be0d037f`: BOUNCE #3 ───** *"The code fix is fine… The redirect design in §8 is what fails. Its main claim (append a `resplit` record, change no code) breaks on the first rebuild, and the new guard in §8.3 cannot catch half of the cases it was written for."* The gate itself ruled: **third bounce → escalate, do not redispatch.**

**Defects:**
1. **§8.2's redirect model makes the build DELETE the original record — an active-invariant-9 violation** (design doc :785-799, against `scripts/merge_and_dedupe.py:1874-1897`). It is specified as append-only with "ZERO `resolve_id` code change", resting on the file being "append-only and chronological".
   - **Gate [R]:** in a throwaway worktree at `96ce135e`, appending `{"from":"INC-07771","into":"INC-14814","reason":"resplit"}` and running `merge_and_dedupe.py` left **one** record for INC-07771 (the new one) and 1,052 total, down from 2 and 1,053. The original `merged` record dated 2026-06-28 was **deleted**. The specialist's own new A1 check flags it: `deprecations DELETED or MODIFIED (invariant 9 check): 1`.
   - **Gate [R]:** the file is **not** chronological — 57 date inversions in file order; and precedence is **file order, not date** (records A-then-B → B wins; B-then-A → **A wins**; same-date ties → last wins). Last-dated only appears to win because the build sorts, and that same step drops the older record.
   - **Foreman re-derived [R], independent route — read the code, did not rerun the gate's build:** `scripts/merge_and_dedupe.py:1875` is `seen_from = {d.get("from"): d for d in prev_deprec if d.get("from")}`. A dict comprehension over a list keeps the **last** occurrence per key, while the comment directly above it says *"keep the earliest record for each `from` id (preserves history)"*. The code and its comment disagree; the comment is wrong. `deprecations_new` is then merged with `setdefault`, and the whole dict is re-serialized sorted by `(from, date)` — so a second record for an existing `from` cannot survive, whatever its date.
   - **Consequence:** any working version of §8.2 requires a deprecation-**persistence** change in `merge_and_dedupe.py`, which Revision 3 routes nowhere.
2. **§8.3's guard cannot fire on 4 of the 8 cases it was written for, and its own failure claim is false** (design doc :857-867). It passes when a target holds *"at least one"* of the retired ID's sources; BOUNCE #2 required that the target still hold *the retired ID's sources*.
   - **Gate [R]:** INC-00497→INC-00311 holds 1 of 8; INC-03128→INC-00754 2 of 10; INC-08139→INC-00554 **2 of 92**; INC-08185→INC-00554 **2 of 65**. All four **pass** the guard. §8.3's claim that "the 8 records in §8.1 would each fail this check" is false for exactly the megacluster cases.
   - **Gate [R]:** the guard's input does not exist in the repo — a retired ID's source list is stored nowhere, and the inbound script's own docstring says recovering it takes manual git archaeology. **As specified the guard cannot run in CI.**
   - **Violates** agreement 6 (a check that cannot fail on its named population) and the BOUNCE #2 defect-1 requirement.
3. **Committed artifacts contradict their own JSON** (agreement 2, and agreement 6(c)).
   - `docs/audits/WS4-T10-phaseB-delta-2026-09-15.md:196,197` say of INC-08139 and INC-08185: "90 / 63 different rows, 1 each — **none is `INC-00554`**". The inbound JSON for both records `INC-00554` among `lands_on_new_rows` with `current_target_still_holds_any_sources: true`.
   - The same false summary sits at design doc :732 and in commit message `be0d037f` ("none still land, even partially") — **false for 4 of 8** (INC-00497, INC-03128, INC-08139, INC-08185).
   - **Foreman re-derived [R], independent route — read the committed JSON directly, did not rerun the gate's mapping:** INC-08139's entry carries `'INC-00554': ['AIID-1446', 'OECD-AIM-2026-04-02-c3bb']` and `current_target_still_holds_any_sources: True`; INC-08185's carries the same two; INC-00497 and INC-03128 likewise have their own target in `lands_on_new_rows` with the flag `True`. Four of the eight JSON records set the flag `True` while the prose says none land at all. **The `WRONG_AFTER_FIX` classification may still be defensible — the bulk of the sources moved — but the sentence asserting it is not.**
4. **Agreement 4 violated — original text rewritten, not superseded.** Design doc §7.3 item 1's original "(4 retirements + 349 total successor rows, 43 of them needing no deprecation record)" was rewritten **in place** under a "[dated note]" label; `git diff 9c24d181..HEAD -- docs/specs/WS4-T10-unmerge-design-2026-09-15.md` shows it only as a removed line. The delta-MD cells for INC-02671, INC-00754, INC-05013 and INC-00311 were edited in place with no dated marker. *(The two the bounce named — INC-07736, INC-01271 — were done correctly.)*

**Advisories:**
- **A-a (§8.4 / INC-07738):** root cause and blast radius 1 both **confirmed [R]**; the "why not fix now" answer is adequate. Missing: retirement is irreversible under invariant 9, so shipping remediation before the fallback fix makes INC-07738's churn **permanent**. That ordering belongs in the user decision, and "churn cost of leaving it unfixed is small" understates it.
- **A-b:** the list-valued `into` TypeError is **real [R]** — `resolve_id` raises `TypeError: unhashable type: 'list'`. §8.2's finding stands, and it also breaks Revision 2's own array-valued `into` for the 4 continuity-breaking splits.
- **A-c:** a `resplit` whose `from` is still live would be ignored by `resolve_id`; **does not bite here** — none of the 8 retired IDs is live in the fixed build [R]; the 4 breaking IDs are live and need Option 2 retirement first.
- **A-d:** the "57 corpus occurrences" of `_com_liferay_…_redirect` (code comment, test comment, commit message) **did not reproduce — two routes give 40** [R].
- **A-e:** the regenerated delta JSON records `fixed_commit: 9c24d181` (pre-blocklist-change) while the MD says it includes the attempt-3 hygiene fix. Harmless — the builds are identical — but the label is inaccurate.
- **A-f:** invariant 8 is **not active** (no WS2-T1 done row); the attempt-3 build is byte-identical to attempt 2, so ATLAS F1 cannot have moved.
- **A-g (proposed task):** **280 other `merged` records are unverifiable by any guard** until retired-ID `source_ids` are captured at deprecation time.
- **A-h (pre-existing, outside this task):** the Issue #88 fixpoint at `merge_and_dedupe.py:1882-1893` **edits existing deprecation records in place** (`into`, `reason`) — latent invariant-9 exposure independent of WS4-T10.

**Evidence [R] (gate):**
- **Repo state:** HEAD `be0d037f` on `ws4/t10-normalize-url` before and after; `git status --porcelain --untracked-files=all` empty at end; `git stash list` 0. *(Gate's own scope note: working tree only — refs/index/reflog not covered.)*
- **Worktrees:** `git worktree add --detach <scratch>/{wt_ctl,wt_a2,wt_a3} {eeb7ca9c,96ce135e,be0d037f}`, each `parse_existing.py && merge_and_dedupe.py`; all removed afterwards, `git worktree list` clean.
- **Build equivalence (sha256):** **attempt 2 == attempt 3** (`incidents.json` `f6694f8b…`, `id_deprecations.json` `d2879e90…`); control == committed `data/` (`facbf809…` / `f24f38f3…`). **The attempt-3 blocklist change moved nothing.**
- **Delta control→attempt 3:** 13,060 → 13,361; 47 splits / 349 successors; 43 hold / 4 break; references +377 / −0; 26 severity changes; 0 rows gained `source_ids`; 0 deprecations deleted or modified; 1 new record INC-07738 → INC-14757 (build-clock dated 2026-09-17, per A4).
- **Inbound completeness, the gate's OWN reverse-edge walk** over published and fixed `id_deprecations.json` (not the specialist's script): **exactly 8**, none dropped — INC-00311←00497; INC-00554←08139/08146/08185; INC-00754←03128; INC-01271←07771; INC-01412←08109; INC-07736←08133; **none into INC-07738**. The specialist's human-supplied SHA table checks out: `git log -S'"from": "<id>"' -- data/id_deprecations.json` puts each ID absent at that commit and present at its parent, and each parent's `source_ids` equals the lookup SHA's for all 8 (counts 8/10/1/1/1/92/1/65); 0 unmapped.
- **A1 fires (gate's own corruption test, superseding the specialist's [A] claim):** `FAKE-SRC-1` on INC-02671 → `common rows gained source_ids: 1`; the resplit tree → `deprecations DELETED or MODIFIED: 1`.
- **Guard blind spot:** control targets held **100%** of their sources; in the fixed build INC-00311 1/8, INC-00754 2/10, INC-00554 2/92 (08139) and 2/65 (08185) — all four pass an "at least one" guard.
- **Blast radius (§8.4), independent replay** of the build's key→ID `setdefault` rule over the fixed output: **exactly one** fresh mint with more than one candidate — `('INC-14757', ['INC-00623','INC-07738'])`; 301 single-candidate mints, 302 total.
- **Mutants:** removing `_com_liferay_.*` now fails **2** tests (`test_normalize_url_drops_other_bounce1_tracking_misses`, `test_normalize_url_liferay_redirect_mutant_n5_fails_without_prefix_match`); unmutated 20 pass; no live `p_p_*` claim remains.
- **Suite** `pytest -q` → 341 passed. **Scope:** the diff since `9c24d181` is 8 files, all explained; nothing under `data/`, `schema/`, `ingest/`, `.github/`.

**Gate's scoping answers (asked by the foreman, 2026-09-17, because they decide what goes to the user):**
1. **All four defects are confined to the §8 design text, the §8.3 guard spec and audit wording.** Gate, verbatim: *"No defect touches the Phase A code fix, its tests, or the delta measurement numbers — the fixed build is byte-identical to the gated attempt-2 build (sha256 on `incidents.json` and `id_deprecations.json`), the delta JSON figures re-derive exactly, mutant N5 is now killed, and 341 tests pass. Defect 3 is false prose in the delta MD contradicting its own correct JSON."*
2. **Defect 1 is NOT fixable inside WS4-T10.** It needs a `merge_and_dedupe.py` deprecation-persistence change (the `seen_from` map is keyed on `from`, so it collapses any second record) **plus a schema decision on the record identity key** — its own task for **pipeline-engineer + schema-architect with a user call**. WS4-T10 can only correct the claim and route it.
3. **Defect 2's guard cannot work in ANY form** until retired IDs' source lists are **persisted in the repo** (today they exist only through manual git archaeology) — and even then *"at least one"* must become *"all / enumerated successor set"*.

**Escalation, awaiting the user.** Options put to the user, 2026-09-17: (a) split the design out as its own task, since defect 1 needs a `merge_and_dedupe.py` deprecation-persistence change and defect 2 needs a new persisted artifact (retired-ID `source_ids` captured at deprecation time — which A-g says 280 other records also need), while the code fix is gate-clean and could merge on its own; (b) a fourth attempt on the same task; (c) neither, and the branch holds.

**Attempt 2** (same instance), HEAD `96ce135e`:
- **`883707c7`** — blocklist changes, then A2 / A4 / A7:
  - **Added:** `web_view`, `iref`, `edtsign`, `edtcode`, `scm`, and the Liferay `_com_liferay_*` / `p_p_*` families.
  - **Kept as identifying:** `p_r_p_assetEntryId`, `category`, `research`.
  - **Also:** query values no longer lowercased; bare `ref` no longer blocklisted.
- **`92fb9975`** — committed delta: `scripts/audit/ws4t10_phaseb_delta.py` plus `docs/audits/WS4-T10-phaseB-delta-2026-09-15.{json,md}`.
- **`96ce135e`** — design-doc Revision 2, a hybrid:
  - Option 1 for the 43 continuity-holding splits, claimed to need "zero new deprecation entries";
  - Option 2 for the 4 continuity-breaking splits.
- **Suite:** 340.
- **Foreman pre-gate check [R]:** clean tree; stash empty; protected-paths diff 0 lines; delta JSON counts as claimed; top supersede notice present.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer, 2026-09-15, on `96ce135e`: BOUNCE #2 ───** *"Five of my six bounce-1 defects are properly fixed. The revised recommendation adds a new invariant-9 error."* (All six gate-1 defects are verified fixed by the gate's own route; see evidence.)

**New defects:**
1. **§7.2's "Option 1 needs NO `id_deprecations.json` entry" rests on a false premise** (doc :572-577: split-off members "never had a separate published id"). **[R] 8 control deprecations redirect into split IDs (6 directly, 2 by chain).** Each retired ID's sources were recovered from `git show <sha>:data/incidents.json` history:
   - INC-07771 "Japan Considers Financial System Shutdowns" → merged into INC-01271 (EU Grok, continuity HOLDS); its source now lands on fresh INC-14814.
   - INC-08109 (Meta smart-glasses facial recognition) → INC-01412 (holds) → content on INC-14847.
   - INC-08133 (AI robots, China) → INC-07736 (Luda, holds) → INC-14850.
   - Breaking rows: INC-08146 and INC-08185 chain through INC-08139 → INC-00554.

   Under the hybrid, the 43 rows get no new records, so **`resolve_id("INC-07771")` (`src/genai_incidents/__init__.py:167`; ID_POLICY rule 3 "Merged IDs redirect forever") keeps returning the EU Grok row, which no longer contains the Japan story, and the real successor has no inbound link.** This is **the silent wrong redirect D25 exists to prevent**, on the Option 1 population. The §7.3 continuity guard cannot see it (the targets keep their titles). The MD compounds it: `WS4-T10-phaseB-delta-2026-09-15.md:132,138` call INC-07736 and INC-01271 "safe under Option 1".
   **Fix:**
   - measure inbound deprecations into all 47 split IDs;
   - route a superseding-redirect record type to schema-architect for the 43 as well as the 4 (invariant 9 forbids editing the existing `merged` records);
   - extend the guard to check that every deprecation target still holds the retired ID's sources;
   - correct the MD rows.

   **Foreman re-derived [R]:** `data/id_deprecations.json` contains `INC-07771→INC-01271`, `INC-08109→INC-01412`, `INC-08133→INC-07736`, `INC-08139→INC-00554`, `INC-08146→INC-08139`, `INC-08185→INC-08139`, all `merged`; `resolve_id` follows chains while the ID is absent.
2. **§7.4 / A5 is incoherent with the hybrid.** By its own continuity test INC-07738 should keep its ID: its title equals INC-14757's exactly, and the donor INC-00623 also holds. Yet the fixed build retires it into a fresh ID and §7.4 only "flags" it. **Fix:** state whether remediation keeps INC-07738, or why not.

**Evidence [R] (gate):**
- **Gate-1 defects 1–6 all fixed by the gate's own route:**
  - **Continuity:** 43/4. The title-equality definition hides nothing: no case/punctuation-only differences; each breaking row's old title lands on exactly one successor; the 43 change only `cve_ids` / `cvss_vector` (+1 `attack_vector`).
  - **INC-08183:** byte-equal between control and fixed.
  - **Blocklist additions:** collapse exactly 3 URL groups of 72,431, all true duplicates (asahi iref, sohu edtsign/edtcode/scm, reversinglabs web_view).
  - **validate.py:** still exits 1 (INC-14614).
  - **References:** 377 gained, 0 lost. The −2 from 379 is the web_view URL on INC-08183 plus the asahi iref URL on INC-02671.
  - **Committed JSON:** reproduces except `fixed_commit`.
- **Builds:** control equals main. Fixed deprecations are byte-identical to gate 1: 1,051 kept, +1 (INC-07738 → INC-14757).
- **Re-run delta:** 47 → 349 with an identical split map; 302 new; 0 rows gained source_ids; changed rows 48 → 47; 26 severity changes, all down; swaps 5 → 4; invariant 4 clean.
- **Normalizer:** 0 new-key groups span more than one old key, so there are still no URL-level merges from the fix. Value case and keeping `ref` split nothing.
- **Tests:** the 4 new tests fail on `c9424935`; 340 pass.
- **Mutants:** N1–N4 and N6–N8 caught. **N5 (remove `_com_liferay_.*`) survives.**
- **Committed script:** fires on title, severity, both invariant-4 directions and a modified deprecation. **Silent on a DELETED deprecation and a reorder-only change.**
- **Agreement 4 on the design doc:** original text preserved (deletions are re-wraps with inline dated notes); the top notice is unmissable.

**Advisories:**
- **A1** The delta script has no deleted/modified check on existing deprecations (`dep_key` ignores date; one-directional), so it cannot evidence invariant 9. It also has no "row gained source_ids" check.
- **A2** N5 survives: the Liferay test uses `p_p_*` (0 corpus occurrences) instead of the `_com_liferay_…_redirect` param 20 real URLs carry. The `p_p_*` entries have no corpus evidence.
- **A3** The regeneration instructions say `git worktree add … main`; after merge that is meaningless. Pin to `eeb7ca9c`.
- **A4** The new deprecation `date` comes from the build clock, so the JSON reproduces only on the same UTC day.
- **A5** 59 vs 58 similarity pairs (MD vs doc).
- **A6** §7.3 item 1 miscounts ("43 of [349 successor rows]" should refer to split IDs).
- **A7** For the user: the Phase A code, tests and committed delta are sound; what is wrong is the §7 invariant-9 logic and the A5 coherence. Neither touches code or data.

**Escalation, awaiting the user.**

**Branch** `ws4/t10-normalize-url` (pushed) · owner pipeline-engineer.
- **Phase A** `75825299`: `normalize_url` keeps a sorted query and drops `_URL_TRACKING_PARAMS`; `merge_into` uses the same normalizer; a build guard fails loudly without `data/legacy_consolidated.json` (opt-out `MERGE_ALLOW_MISSING_LEGACY=1`); the E21 tripwire is widened to [1574, 1575]. Suite 332.
- **Phase B/C** `c9424935`: measurement plus `docs/specs/WS4-T10-unmerge-design-2026-09-15.md`, which recommends Option 2 (retire every split ID, fresh IDs for all successors).
- **Parallel with WS4-T11** (user-authorized; disjoint files). A board note on that branch covers the authorization.

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-15, on `c9424935`: BOUNCE #1 ───** *"The Phase A code is sound; the defects are in the Phase B/C record the user will rule on… the Phase C recommendation rests on a claim its own data contradicts."*

**Defects:**
1. **Option 2's rationale is contradicted by the full population** (doc :345-348, :362-365, :368-374: "does not track the real incident even once"). **[R] 43 of the 47 split rows keep their title on the old ID**; only INC-00311, -00554, -00754 and -01897 swap. The "sample" was the swaps themselves, i.e. selection bias. INC-02671 (Grok NCII) keeps 17 of 18 source_ids and sheds one German lawnmower-robot row. **Option 2 would retire 43 IDs whose content doesn't change.** Fix: restate on the full population and re-weigh Options 1/3.
2. **INC-08183 is a false split the FIX introduced, not a split.** Its source_ids are identical in both builds, yet title, description, date, year and category flip ("Google Bard Conversation Exfiltration" → "Malicious Models on Hugging Face"). Cause: a `?&web_view=true` reference now keys apart from the bare URL (`web_view` is not in the blocklist), the row ships both copies, and the anchor changes. **This is an unintended delta (agreement 2).** Neither Option 2 nor the §5.1(b) guard catches it. Fix: record it as a regression, fix the blocklist miss with a test, and extend the design and guard to non-split stable-ID content swaps (a continuity check).
3. **The §5.1 hazard is misstated** ("would silently produce content swaps next `make build`"). **[R] The fixed build FAILS `validate.py` (exit 1)**: "discovery_method outside the landmark tier (INC-14614)", which is the mis-keyed CVE-2025-10875 override. So `make build`, validate.yml, auto-refresh.yml "Re-merge + render + validate" and cve-enrich.yml all **fail closed today**. **But that one mis-keyed override is the only barrier, and §5.2 tells remediation to re-key it first**, removing it before any continuity guard exists. Merging this branch alone would also turn validate.yml on main red. Fix: state the measured behaviour, and require the continuity guard to land before or with the override re-keying.
4. **Reference restoration under-reported** (doc :103, "1 gained"). **[R] 7 common rows gain 8 never-shipped URLs; corpus-wide 379 distinct reference URLs newly shipped, 0 lost** (66,025 → 66,404 distinct; 66,048 → 66,427 entries).
5. **The per-entity delta and top-10 classification exist in NO committed artifact.** The doc has aggregates only (agreement 6 form d); `diff_corpus.py` and `phaseB_*.txt` are in the session scratchpad only (agreements 1/2). Fix: commit the 47 split IDs with successors, the 26 severity changes by ID and direction, the 48 changed IDs by field, and the top-10 classification with INC-08183 marked as a regression.
6. **False docstring** at `tests/test_e21_partA_inc00437_provenance.py:173`: "1575 still ships the disagreement in the committed corpus". **[R]** In committed data, AIID-1575 and OECD-AIM-2026-01-21-eb71 sit **inside INC-05013** (TruDi, AIID-1436 template), masked. The full-corpus template exceptions today are only [898, 1574]. 1575 first ships as the new INC-14682 on a fixed rebuild. **The widening itself is justified.**

**Evidence [R] (gate):**
- **Builds.** Control incidents sha256 `facbf809…` and id_deprecations `f24f38f3…` both equal main. Fixed build is deterministic: 3 builds, identical incidents / deprecations / min.json.
- **Gate's own delta** (keyed per source_id membership; proven to fire):
  - rows 13,060 → 13,361 · 13,059 common · 1 control-only (INC-07738) · 302 fixed-only (INC-14605…14906);
  - source_id universe 16,348 both sides; 47 split into 349; **0 common rows gained source_ids**;
  - INC-14757 is the only new row drawn from >1 old row (INC-00623 + INC-07738, Mythos);
  - 48 common rows changed (includes `last_seen`); 26 severity changes, all downward (C→H 12, H→M 8, C→M 5, M→L 1);
  - invariant 4 clean;
  - title+description changed on exactly 5 IDs: INC-00311, -00554, -00754, -01897, -08183;
  - INC-00554 → 100 rows. INC-14609 = AIID-1552 + OECD-…4590 (Tesla); INC-00554 = AIID-1446 + OECD-…c3bb (KBS subtitles).
- **Invariant 9.** All 1,051 deprecations verbatim, +1 (INC-07738 → INC-14757, merged); no revival.
- **Override.** CVE-2025-10875 moves INC-02590 → INC-14614 (the NVD Mulesoft CVE). It is the only one of 176 override keys whose row changes.
- **Megaclusters and splits.** CVE megaclusters untouched. 6 of the 58 similarity pairs sampled: all distinct. Splits INC-05013, -02671 and -02590 spot-checked as correct.
- **Tests on pre-fix code** (a worktree, not stash): 6 failed / 120 passed. Tests (b) pass on pre-fix by construction; mutant M1 proves them.
- **Mutants M1–M8 all caught.** M3 (an idxno-only allowlist) is caught **only** by the E21 real-data tripwire.
- **E21 widening proven to fire:** a synthetic AIID-99999 row gives "found 3".
- **Build guard.** Real CLI exit 1; the opt-out exists only in tests; all three workflows run parse_existing first.
- **Normalizer over 72,430 distinct raw URLs:** 0 new-key groups span >1 old key (the fix creates no URL-level merges); 0 lowercase-only collisions; 9 `ref=` URLs with 0 collisions.

**Advisories:**
- **A1** (b) cannot fail on pre-fix code; say so.
- **A2** Unit-test other identifying params (`itemName=`, `page=`, `id=`, `p=`); M3 is caught only incidentally.
- **A3** 9 blocklist misses split query variants from bare URLs: `iref`, `research`, `edtsign`/`edtcode`/`scm`, a liferay `_redirect`, `p_r_p_assetentryid`, `category`, `web_view`. Only `web_view` swapped content.
- **A4** Latent: lowercasing case-significant values; dropping `ref` globally.
- **A5** The Mythos merge retires an intact published ID (INC-07738) into a fresh one: avoidable churn, and uncovered by the design.
- **A6** The guard catches a missing legacy file, not a stale one (WS4-T13).
- **A7** Test comment at `test_normalize_url_overmerge.py:14` cites `git stash`; reword.
- **A8** STIX revocation and redirect stubs are thin; for schema-architect / distribution-engineer later.
- **A9** No `benchmark_atlas.py`, so invariant 8 is N/A.
- **A10** Phase A can stand. Redo doc defects 1–5 and docstring defect 6; if the blocklist changes, **Phase B must be re-run** (the INC-08183 figures move).

**Next:** redispatch the same pipeline-engineer with defects 1–6 and advisories A1–A5 and A7. Commit the per-entity delta. The user rules on the design only after a PASS.


## 🔴 CI WENT RED ON `main` WITHIN THE HOUR OF MERGING WS4-T10 — the armed unmerge, firing — **REVERTED 2026-09-18, `fe3a4845`**

**Reported by the user as "dataset is failing", and they were right.** `Validate dataset` failed on two consecutive pushes (`c5c3402e`, `71c8ad6c`).

**The mechanism, confirmed [R]:** `.github/workflows/validate.yml:33-37` runs `parse_existing.py` **and `merge_and_dedupe.py`** before `validate.py` — **CI rebuilds, then validates.** With WS4-T10's `normalize_url` fix on `main`, that rebuild produced **`13361/13361 entries valid`** against a committed corpus of **13,060**, then failed: `1 integrity violation(s): 1 entr(ies) carry discovery_method outside the landmark tier (e.g. INC-14614)`.

**So the red WAS the 301-row unmerge, executing in CI on every push.** This is the ordering hazard boarded before the cut, arriving exactly as described — the difference being that it fires in CI, not only in a release rebuild, which the hazard entry did not spell out.

**The trap worth recording:** the obvious "fix" is to re-key the mis-keyed `CVE-2025-10875` override so `INC-14614` validates. **That would have removed the last barrier rather than the problem** — the board already noted three accidental barriers (validate's failure, the E21 tripwire, D25(a) policy) and **no deliberate one**. Making CI green that way would have left an automated refresh free to publish a 301-row data change that D25(b) reserves to the user.

**Action: the MERGE was reverted, not the work.** `ws4/t10-normalize-url`, its FINAL PASS on `9324cdf7` and every artifact are intact. **Verified after the revert [R]:** rebuild returns **13,060**, `validate.py` exits **0**, and `git status --porcelain` is empty after a full rebuild — the build is a no-op against committed data again. `Validate dataset` on `fe3a4845`: **success**.

**D26(b) is not violated by this.** That ruling makes the fix merge on its own rather than wait for the design; it does not require `main` to carry an armed data change while the design that makes it safe is still unwritten. **WS4-T15 must land the deliberate guard before this merges again.**


## ⚖ D28 — **USER APPROVES THE 47-SPLIT REMEDIATION, 2026-09-18** — the corpus unfreezes

**The authorization D25(b) reserved to the user, now given.** Approved: the **43 keep-ID splits**, the **4 retirements** (`INC-00311`, `INC-00554`, `INC-00754`, `INC-01897`), and the **8 inbound redirect corrections** — the list at `docs/audits/WS4-T19-authorized-splits-2026-09-18.json` (55 entries). **Published effect: 13,060 → 13,361 rows (+301), four published IDs retired, eight existing redirects corrected. Irreversible** — deprecations are append-only under invariant 9.

**Ruling on how it lands: ONE PR.** The authorized list, the pre-authorization guard, the `CVE-2025-10875` re-key and the unmerge itself land together, so **the corpus is never transiently half-changed**.

**What the approval rests on, recorded so a future reader can weigh it:**
- **Two independent parties agree on all 47 split decisions.** The gate rebuilt the corpus itself and examined **15 groups it chose**, including the corpus's most similar pair (`INC-01192`, **0.969** — four distinct VS Code extension CVEs collapsed by a `?itemName=` query string) and the specialist's own `INC-12120` worked example, which checked out exactly.
- **Three successor-PAIR questions are flagged, not resolved** — `INC-14745`/`INC-14871` (0.914), `INC-14808`/`INC-14838` (0.809), and the Mythos pair — and the gate established *why* they are unresolvable: **299 of the 312 OECD-AIM rows involved carry boilerplate descriptions with no narrative text.** *"That is a limit of the source data, not of this review."* They are **merge** questions between two new rows, logically independent of whether the ID splits, and routed to WS4-T5.
- **The document earned the approval only on its second version.** The gate's judgement, quoted: *"The first version… offered three supporting checks of which one could not fail and one was false in 51 pairs, and then reported zero uncertainty across 47 editorial judgements. A careful reader would have concluded distinctness was structurally established, when for 89% of the affected rows it rested on reading headlines."* The corrected version *"names its own tautology inside the check list, says which check does not hold universally, identifies which check is the real evidence, and states plainly where the author cannot tell. That is the difference between being handed a conclusion and being handed evidence."*

**⚠ A GUARD THAT IS PRE-SATISFIED IS NOT A GUARD — carried into the remediation brief.** The gate's advisory: the authorized list was committed **pre-ruling**, and the guard reads it **by filename**, so once the list and the fix are both on `main` the guard is **already satisfied for the very transition it gates**. **The remediation must make the authorization explicit** — the list carries an approval marker naming **D28**, and the guard requires that marker rather than treating file-presence as consent. Otherwise the deliberate barrier this project lacked degenerates into the accidental ones it was built to replace.

**Also required in the same PR:** `CVE-2025-10875` is still mis-keyed onto `INC-14614` — outside the split judgement, but it **ships wrong** unless re-keyed alongside. And the delta doc's "no field outside this list changed" is literally inaccurate: `updated` moves on all 47 rows, declared under invariant 4 rather than in the 25-field table.



---

## Part 2 (original PROGRESS.md lines 3939-4532)

## 🎨 WS6-T5 — Website: scale, accessibility, integrity (P2) — opened 2026-09-17 under the user's 2026-09-18 goal — **⛔ BOUNCE #1, fixes in flight on `ws6/t5-design`**

**Two branches, one writer.** `ws6/t5-website` (`c2ec7347`, distribution-engineer) carried the engineering pass; `ws6/t5-design` branches from it and now carries **both** the visual pass and the bounce fixes, so only one agent writes these files. **Merge target is `ws6/t5-design`**, which contains the other.

**Why a design pass exists at all:** the engineering half landed hard and the **visual half did not**. The foreman found the first specialist had left a filesystem-wide `find` running, hunting for the `frontend-design` skill it never loaded — and its report was almost entirely payload, timings and audit scores. The user asked for the site to be *"more appealing and updated"*; the second half was under-delivered, so a dedicated pass was dispatched with the skill named explicitly rather than left to be discovered.

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-18, on `c2ec7347`: BOUNCE #1 ───** *"The scale work is real and the numbers check out exactly."* Four defects; **two are this project's dominant failure mode, caught with proof.**

**Defect 1 — THE 380px GATE IS STRUCTURALLY INCAPABLE OF FAILING, and it guards the plan's ONLY literal accept criterion.** `tests/a11y/check_narrow_viewport.js:39,58` asserts on `document.documentElement.scrollWidth`, but `docs/style.css:557-560` wraps the table in `.table-wrap { overflow-x: auto }`, so **any** table overflow is absorbed by a nested scroller the document never sees. **Proved [R]:** forcing the table to `min-width: 1200px` and re-running the committed check **unmodified** gives `docScrollWidth 380, tableScrollWidth 1200, severityCellRight 1216, severityVisible false` → **"PASS", exit 0**. Removing only the `table-layout:fixed` fix — the exact pre-fix defect this task exists to cure — also exits 0. **Agreement 6 forms (a)/(d).** The sting: *the specialist's own report says `scrollWidth === 380` "would have missed the real defect", and then committed exactly that assertion.* Its claim that the check "fired for real during development" is true only of the touch-target assertion; **the overflow assertion has never fired and cannot.**
**Fix:** assert `wrap.scrollWidth <= wrap.clientWidth` **and** last-cell `getBoundingClientRect().right <= innerWidth`, then **prove it fires by restoring the pre-fix CSS.** The gate's instruction, kept verbatim: *"the current gate's transcript looked like proof and was not."*

**Defect 2 — a silent, state-dependent search regression.** `docs/app.js:217` searches `primary_reference`, but `scripts/gen_docs_core_data.py:53-63` puts that field in `DETAIL_FIELDS`, not `CORE_FIELDS`. **Measured against a pre-change control built from `main`** (an independent derivation path, not a re-run of the branch's harness): searching `reuters.com` gives **3 of 13,060 on `main`, 0 on the branch, and 2 after expanding one unrelated row** — same query, three answers, no error, results depending on what the user happened to click. All 3 matches are reachable only via that field. **Also an agreement-2 violation:** a transformative data operation that changed a field's availability without declaring the behaviour delta.
**Resolution (gate-measured, foreman-accepted):** restore the field to `CORE_FIELDS`. Cost **4,382,780 → 5,410,055 bytes (+1,027,275, +23.4%)**, moving the initial fetch from 29.2% to **36.0%** of the full file — still a **2.8× reduction from 15 MB**, so the headline survives with a corrected number. Removing it from `matches()` was cheaper and rejected: it narrows search silently, which is the same failure shape as the bug. **No siblings — the gate enumerated every entry-field read in `app.js` against `DETAIL_FIELDS`; `primary_reference` is the only overlap.**

**Defect 3 — detail-shard failure is silent in BOTH user paths.** A 404 shard leaves the panel reading "Loading details…" indefinitely (no error, no retry). **CSV export is worse:** `Promise.allSettled` (`app.js:112`) swallows shard failures, so the same 5,401-row export with one shard missing yields **empty Description 5,377 vs 39**, **empty Primary Reference 5,216 vs 71**, **empty NIST AI RMF 4,509 vs 607** against control — and the button returns to its normal state with no error. The user gets a silently gutted file.

**Defect 4 — the `display:none` justification is FALSE for assistive technology.** The in-code comment justifies hiding three columns below 640px as "already-visible via the existing row-expand detail panel". That panel is **mouse-only**: rows carry `tabIndex -1`, no role, no `aria-expanded`; 60 Tab presses never focus a data row; programmatic focus + Enter opens nothing. **axe reports 0 violations because the click handler sits on a semantically inert `<tr>`.** Mouse-only expand is pre-existing on `main`, **but this task made it load-bearing** — those values used to be in the table and reachable by AT at any width. **Mitigating and verified:** the data is not lost; the ID cell is a focusable link to the per-year page, which carries the same fields. Lowest severity of the four; *the wrong claim in the comment is the substantive part.*

**The architecture is SOUND — gate's ruling, and it names the change that stops the symptoms recurring.** The core/detail split is correct and the boundary was drawn in the right place but for one field; mutating `DATA` in place is also right, since it keeps later reads synchronous. The real weakness is that **completeness is implicit** — `hasDetail()` infers "loaded" from the presence of `description`, and nothing distinguishes "not fetched yet" from "fetch failed". **Track explicit per-year status (unloaded/loading/failed) instead of sniffing a field, and defects 3 and 4's symptom class stops regenerating.** Contained change inside ~50 lines; **no rework, focused fix on the existing branch.**

**Evidence [R] (gate):** generator re-run on a clean worktree reproduces **every** size figure exactly (13,060 incidents, 31 shards, `incidents.min.json` 15,018,089 unchanged, core 4,382,860 = 29.2%, largest shard 2,609,427) and is deterministic under `sha256sum -c`. **Timings NOT re-derived — the 6,811→1,449 ms figures are [A] attested, not measured by the gate.** Invariant 6: marker inventory **byte-identical to `main`** (1 × `stats:incident_count`, 2 × `:line` above the OG and Twitter tags); every `13,060` in `index.html` sits inside a marker; drift check clean, renderer a no-op. Scope: 21 files, nothing under `data/`, `schema/`, `ingest/`; board and plan untouched. **The axe gate fires for the right reason** — the gate extracted the 21 critical-impact rules from the installed axe-core 4.13.0 **itself** and injected an unnamed `<button>` plus an alt-less `<img>` (a rule the specialist did not use): 2 critical at both viewports, real exit 1. Theme toggle, pre-paint script, `localStorage` key, OG/Twitter tags and the full-file download link all verified intact. Suite 335.

**Advisories:** (1) **both accessibility gates pass a genuine WCAG AA failure** — reverting only the four light-theme severity colours gives axe `[serious] color-contrast` on **113 nodes** and Lighthouse 95.0, and **both still exit 0**; implemented as the plan words it and disclosed honestly, so not a defect, but **the plan's own ≥90 criterion is the weaker check** and a follow-up should gate axe on `serious`. (2) No runtime fallback if the core file is missing, but structurally contained — `pages.yml` generates before upload and `deploy` has `needs: build`; **residual risk is configuration**: switching Pages to deploy-from-branch would break the site permanently, since the artifact is uncommitted. Worth a deploy-doc line. (3) `pages.yml` never runs `verify_data_integrity.py`, so **the deploy path itself is unverified** — that gate lives only in `a11y.yml`. (4) `hasDetail()`'s `description !== undefined` key is a latent trap. (5) Per-corpus extensibility holds (`corpus` is in `CORE_FIELDS`); the specialist's flag is accurate — `Counter({'security': 12519, 'ai-harm': 541})`, two values, not three. (6) Committed diagnostics under `tests/a11y/` are not gates and will rot. (7) Branch based on `45d05f4b` while `main` advanced to `f9e45ef7`.

**🐛 PRE-EXISTING BUG found in passing, NOT a WS6-T5 defect — boarded so it is not lost:** `docs/app.js:207` tests `e.tier`, **a field that does not exist in the data** — the real field is `quality_tier` — so that filter predicate **can never match**. Present on `main` today. Owner WS6; no task yet.

> **[CORRECTION, dated 2026-09-18 — the diagnosis above is WRONG, the conclusion is right. Foreman, re-derived [R]; preserved per agreement 4.]**
> `tier` and `quality_tier` are **two different fields, not a renaming**, and the paragraph above misstates the cause:
> - **`tier`** → `feed` **11,155** / `landmark` **1,905**. Exists in `data/incidents.json` **only**.
> - **`quality_tier`** → `reviewed` **10,835** / `auto` **2,106** / `curated` **119**. Exists in the full file **and** in `data/incidents.min.json`.
>
> Measured: `collections.Counter` over both fields in both files. **The predicate is indeed dead, but because `tier` is stripped from every served variant — not because it was misnamed.** `gen_docs_core_data.py` derives the core bundle from `incidents.min.json`, so no `CORE_FIELDS` change can make it reachable.
>
> **It is worse than a dead predicate, and it is user-visible.** `docs/index.html:161-164` offers a **"Tier" filter with a `landmark` option**, and `docs/app.js:161` filters on `e.tier`. **Selecting "landmark" on the live site returns zero rows, today.** Routed to the WS6-T5 design specialist as a Part-A item: make the control honest (remove it, or repoint it to a field that reaches the page) **without touching frozen data or the generator's source**, plus a check that fails when a filter's option set cannot be satisfied by the loaded data.

## 📦 WS6-T9 (NEW, P1) — the `landmark` subset is not identifiable in ANY distributed variant, while the README tells consumers to cite it

**Found 2026-09-18 by the foreman while verifying a release-notes figure, [R] by direct measurement.** `tier` (`feed`/`landmark`) is present in `data/incidents.json` and **absent from every variant we distribute**: `data/incidents.min.json` (the site's source), the generated site bundles, and `src/genai_incidents/data/incidents.min.json` — **the copy shipped in the PyPI package**.

**Why this matters more than a missing field.** `README.md:26` instructs readers: *"cite the landmark count, not the full corpus, when you mean 'notable incidents.'"* We publish the count (**1,905**) on every surface through the invariant-6 markers, and we publish data in which **no consumer can select those 1,905 rows.** A figure that cannot be reproduced from the artifact it describes is the agreement-6(c) shape — the claim survives, the ability to check it does not.

**Scope for WS6-T9:** decide whether `tier` belongs in the distributed variants (a schema/distribution question for **schema-architect** with **corpus-surgeon**, under invariant 7's full-vs-sanitized split — note `quality_tier` already crosses that boundary, so the exclusion of `tier` looks accidental rather than principled), or whether the README's instruction must change. **Do not assume the first.** Either way the site's dead control is fixed separately, under WS6-T5.

**Deliberately NOT blocking the v2.10.0 cut:** this is pre-existing — v2.9.0 shipped the same way — and fixing it means changing distributed data while the corpus is frozen under D25(a). **But the release notes must not claim or imply the landmark subset is usable by consumers**; that constraint was given to the notes gate.

## 🔧 WS4-T13 — OECD AIM crawl budget (D25c) — opened 2026-09-17 — **✅ done — PASS (red-reviewer, 2026-09-18) — MERGED to main**

**Specialist:** pipeline-engineer in an isolated worktree, branch `ws4/t13-crawl-budget`, commit `35ac4eec` off `main` `45d05f4b`. Two files: `scripts/ingest_oecd_aim.py`, `tests/test_ingest_oecd_aim.py`. **Foreman scope ruling applied:** D25(c)'s build-guard half already exists in WS4-T10 Phase A (`75825299`, unmerged) and was explicitly out of scope — the gate confirmed `git diff main..35ac4eec -- scripts/merge_and_dedupe.py` is **0 lines**, so it was not silently rebuilt.

**Delivered:** `_NUMERIC_SLUG_RE` full-matched against each URL's final path segment, partitioned **before** the thread pool, so a skipped URL never opens a socket or spends a rate-limit slot. **~59% fewer requests to `oecd.ai` per run; ~36 minutes of headroom recovered against `timeout-minutes: 60`.** Suite 339 on merged `main` [R, foreman].

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-18, on `35ac4eec`: PASS ───** No defects. Six advisories.

**The gate's method, worth recording because it is the behaviour we want:** it **discarded two of its own checks mid-review as vacuous** rather than cite them — one keyed on `e['url']` (entries have no `url` key) and one on `e['source_id']` (published entries use `source_ids`, plural), so it had scanned 13,060 empty strings and "found 0". Both are **agreement 6 form (a)**: output identical whether or not the condition held. It replaced them with checks that return a nonzero denominator it could show. **A gate applying agreement 6 to itself, unprompted.**

**Evidence [R] (gate), by routes the specialist did not use:**
- **Population re-derived with its own two regexes**, never calling `is_numeric_slug`: 10,000 incident URLs; window[:3000] → 1,227 date-hash / 1,773 numeric / **0 other**; numeric block contiguous at positions 1227–2999. Then a **per-URL disagreement check across all 10,000** between its classifier and the specialist's: **0 disagreements**, and `other=0` holds across the entire corpus, not just the window.
- **On 1,773 vs D25(c)'s "~1,852":** corroborated by the *shape* of the delta, not merely its existence — E21 measured 1852/1148 on 2026-09-14, today 1773/1227, moving **equal and opposite (−79/+79)** against a window pinned at 3,000. That is the signature of a fixed-size window sliding over a growing date-hash head, **not a miscount**. The code prints the count rather than hardcoding it, so no stale total exists anywhere.
- **Boundary behaviour beyond what the specialist claimed** (22 cases): trailing slash → skip; `?query`, `#frag`, percent-encoded `%32%35%36`, trailing whitespace/newline → **fetch**; uppercase path → skip. `re.fullmatch(r"^\d+$", "256\n")` is `False` — the `^`/`$`-inside-`fullmatch` trailing-newline hole does **not** exist here. **Every ambiguous shape falls to the fetch side**, so the failure mode is a wasted request, never a dropped incident.
- **Skip really prevents the fetch** (`:582/594`): only `fetch_urls` is submitted; `skipped_numeric` is used solely in the printed line.
- **Headroom model validated at the source** (`ingest/common.py:106,198-205`): 1.0s per host under one global lock, so `MAX_WORKERS=10` buys nothing above 1.0 req/s and the measured 0.8210 req/s sits just under the ceiling — **linear-by-count is the correct model**, and the estimate is understated if anything (two live legacy 404s cost 7.5s and 8.6s through retry backoff).
- **Three in-memory mutants** (never-match / match-all / `search` instead of `fullmatch`) → 5, 4 and 4 failures against a 35-passed baseline; the end-to-end trap fires verbatim at `tests/test_ingest_oecd_aim.py:833`.
- **Scope:** exactly 2 files; no `data/`, `schema/`, `ingest/`, `docs/`, board or plan paths; **D25(a) verified by rebuilding twice**, porcelain empty after each, `13060/13060 valid`, drift clean.
- **Invariant 5:** no new HTTP primitive in the diff; `test_network_chokepoint.py:155` rglobs `scripts/`, so coverage is automatic.
- **Invariants 3/4/9:** live probe (`/256`, `/9915` → `no_incident_body_shape`; control `/2026-09-01-dee9` → `ok`) plus a **non-vacuous** corpus scan — 4,160 OECD-AIM IDs / 4,755 `oecd.ai` refs, **0** bare-numeric in either; `union_with_existing` never removes, so a skip can only fail to refresh, never delete.

**Advisories, and what each became:**
- **A1 Unicode over-match → NEW TASK WS4-T16 (P3).** `^\d+$` matches fullwidth `２５６`, Arabic-Indic `٤٤٤`, Devanagari; `load_sitemap()`'s `[^/]+$` does **not** block raw non-ASCII, so the path is reachable and its consequence is an **over-skip — a silently missed incident, not a wasted request**. **Foreman re-derived independently [R]:** `\d` matches both shapes where `[0-9]` does not, and such a URL passes the sitemap filter. Zero instances across all 10,000 live URLs; the modern scheme is always hyphenated, so this needs a third URL scheme OECD has never emitted. Fix is one character (`[0-9]+` or `re.ASCII`) plus a test.
  **The foreman asked whether to amend the gated commit and re-gate just that delta; the gate said no, and its reasoning is recorded because it generalises:** *"the one character is not the risk; re-gating 'just that delta' is, because the delta's whole effect is on inputs my population sweep found zero of, so a narrow re-gate would be a check that cannot fail (agreement 6 form (a)) and would retire the advisory without ever testing it."* **Gate it properly or not at all.** WS4-T16 must prove its fire by reverting to `\d` and watching a fullwidth/Arabic-Indic-slug test fail.
- **A3 the skip erases its own tripwire → NEW TASK WS4-T17 (P1), SEQUENCED BEFORE THE NEXT SCHEDULED CRAWL.** The rule's premise — every legacy numeric slug fails the body-shape check — becomes **unobservable** once those 1,773 URLs are never fetched. Counterweight: sample K of `skipped_numeric` per run (K=5 ≈ 5s against 36 min recovered), assert `REASON_NO_BODY_SHAPE`, fail loudly otherwise. **The gate chose A3 over A1 as the pre-crawl follow-up for a reason worth keeping: A3 is the only advisory that gets WORSE by merging** — the evidence that would falsify its premise stops being collected the moment this lands, silently and permanently, over a legacy block that grows as the window slides. It is a separate task because the probe **reintroduces live network into a task whose delivered value is removing it**, needs its own invariant-5 conduct reasoning, and needs its own proof-it-fires (a seeded modern-body fixture on a numeric slug).
- **A2 misnamed test.** `tests/test_ingest_oecd_aim.py:652` `test_is_numeric_slug_rule_fires_when_corrupted` **corrupts nothing** — its assertions duplicate the test above it. It does discriminate (it failed under all three mutants), so it is a real test with a false name, and *"a name asserting a property the test lacks is what agreement 6 warns about; a future reader will cite it instead of re-deriving."* Rename to a baseline-pin name; **the proof of fire belongs in this board record, not in a docstring pointing at a transcript.** Routed to WS4-T17 as a carry-along.
  > **[CORRECTION, dated 2026-09-18 — WS4-T17 gate. Original preserved above per agreement 4.]** The clause *"it failed under all three mutants"* — carried into this board entry from the WS4-T13 gate's own advisory — **is false, and the board repeated it without re-deriving it.** Measured by the WS4-T17 gate: the **hyphen-inclusive mutant passes** that test, and passes the fuller test above it too; **all five readings** (`^[0-9-]+$`, `^[\d-]+$`, `^[\d\-]*$`, `\d+`, `^[-\d]+$`) are invisible to both. The test is sound and still discriminates real regressions — only the three-mutant claim goes.
  >
  > **Worth naming, because it is this board's own failure and not a specialist's:** the entry above says *"the proof of fire belongs in this board record, not in a docstring pointing at a transcript"* — and then recorded, as that proof, a claim it had not measured. **A board record inherits its evidence's warrant, not the evidence itself.** The rename that followed then installed the same false claim in a docstring, so the error propagated from an advisory, into the board, into the code, and was caught only when a second gate measured it. Where a figure arrives from another agent's advisory, it is attested `[A]` until this board re-derives it.
- **A4 branch not on origin — RESOLVED.** The gate found `ws4/t13-crawl-budget` absent from origin. **The foreman pushed it**; `git ls-remote` now returns `35ac4eec…`. **This is agreement 1a caught by a gate rather than by the foreman, which is the wrong way round** — the durability check is the foreman's job at the end of every run.
- **A5 build guard absent and untouched**, per the scope ruling. Board note the gate volunteered: **`data/legacy_consolidated.json` is gitignored and therefore absent from a fresh checkout** — the gate had to copy it in to build at all. That is exactly the condition WS4-T10's guard exists to catch, so it **corroborates that guard's value** independently.
- **A6 pre-activation invariant sweep clean:** no unified headline counts, no mappings lacking `{method, confidence}`, no deletions where status/tombstone was required, no hardcoded totals, no raw payload text in `min.json`/HF outputs, no source owed a `SOURCE_LICENSES.md` row, no model or network call added to the `make build` path.

**Merged** `--no-ff` to `main` as `eb9788ab` from a temporary worktree; the main tree stayed on `ws4/t10-normalize-url` throughout. Suite 339 on the merge commit [R, foreman]. **Published data does not move:** this changes the crawl only, and the D25(a) freeze is untouched.

## 🔧 WS4-T11 — OECD AIM 800 KB page truncation (D25c) — opened 2026-09-15 — **✅ done — foreman spot-check PASS per user ruling (one recorded test gap) — MERGED to main (user-approved 2026-09-15)**

**User ruling on bounce #2 (2026-09-15):** narrow third attempt, test-only plus advisory 2, verified by a foreman spot-check rather than a third full gate.

**Attempt 3** `19fa9fa3` (same instance):
- The multi-MB, straddle and cold-path tests now also assert `fetch_and_extract(url) == (REASON_OK, body)` through the real `fetch_page`.
- New `test_main_end_to_end_offline` covers normal, ≥949 KB with the blob past 900 KB, numeric shell, no-script, broken JSON, fetch failure, empty page, a duplicate URL, and an OK-but-not-security-relevant page. It asserts the output id set exactly, plus the summary line.
- `fetched` is now derived from `results`, fixing duplicate-URL double-counting.
- An empty-page accounting comment is added.
- The specialist caught its own coincidence: `ok == len(out)` in the first fixture, so mutant (d) passed. It added a divergent fixture.
- Suite 335.

**─── FOREMAN SPOT-CHECK (testimony-class, on the user's ruling) — 2026-09-15, on `19fa9fa3`: PASS, with one recorded gap ───**
- **Scope [R]:** only `scripts/ingest_oecd_aim.py` + `tests/test_ingest_oecd_aim.py` (+ board); protected-paths diff 0 lines; porcelain empty (untracked-all).
- **Different route from the author's proof [R]:** `git archive 19fa9fa3` into temp; COMMITTED test file; mutants **at the production entry point**, per the bounce-#2 lesson. Baseline 31 passed.
  - **M-A** (the reviewer's defect) `fetch_and_extract` → `_extract_state_detail(text[:800_000])`: **4 failed**, including `test_main_end_to_end_offline`. **Caught.**
  - **M-B** (the foreman's own) `fetch_and_extract` slices `text[:950_000]`, above the 949 KB fixture: **2 failed** (multi-MB, cold-path). **Caught.**
  - **M-C** (the foreman's own) `main()` silently omits no-ng-state-script pages from `results`: **1 failed** (end-to-end). **Caught.**
  - **M-D** (the foreman's own) the summary line swaps the "JSON decode error" and "no incident-body shape" values: **31 passed. SURVIVES.**
- **Recorded gap (follow-up, WS4-T13 accounting scope).** The end-to-end fixture has one page in each of those two buckets, so a label swap is invisible. It is the same coincidental-equality shape the specialist fixed for `ok`, one bucket over. **Impact:** the printed summary mislabels two sub-counts; output data and totals are unaffected. **Fix:** give the two buckets different counts in the fixture. **Why not a fourth round:** this is a cosmetic log label after two bounces, and the user ruled spot-check. Recorded here so nobody cites the summary sub-counts as fully guarded.
- **Carried reviewer advisories (not blocking):** `errors="ignore"` survives (no invalid-byte fixture); a cap above the largest fixture survives (inherent).

**Merge status:** the branch is pushed. **Not merged.** This is a code-only change with no data, and scheduled refreshes stay fail-closed at the E21 tripwire under the D25(a) freeze, so merging is safe. Holding for the user's word, because the foreman previously told the user it would stay unmerged under the freeze. Expect a PROGRESS.md conflict with WS4-T10's branch, which adds a section at the same spot.
**UPDATE 2026-09-15 — the user approved the merge.** Merged `--no-ff` to main from the WS4-T11 worktree; the main tree (WS4-T10) was left untouched. Scheduled refreshes remain fail-closed at the E21 tripwire (D25a), so no published data is affected.

**Attempt 2** `95ca8ca1` (same instance) changed three things:
- **Reason-coded extraction:** `_extract_state_detail` / `fetch_and_extract` / `_tally_reasons`, with `main()` printing three unparseable sub-buckets.
- **Memory fixed at the root:** `main()` submits `fetch_and_extract`, so only `(reason, body)` is retained.
- **Test hardening:** >5 MB through `fetch_page`, a true straddle with a CJK character across byte 800,000, a network guard, a cold path, non-ASCII, and trailing script tags. Suite 334.

**Foreman pre-gate check [R]:** `git archive` into temp, COMMITTED tests. A `fetch_page` `[:900_000]` cap → 2 fail; latin-1 → 2 fail.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer, 2026-09-15, on `95ca8ca1`: BOUNCE #2 ───** *"The production code in 95ca8ca1 is correct… The single defect is again the guard, and it is new: the refactor moved the production entry point out from under the size tests."*

**Defect 1.** The original bug, reinserted at the entry point `main()` actually calls, **passes all 30 committed tests**.
- **Mutant:** `fetch_and_extract()` → `return _extract_state_detail(text[:800_000])` (and the `[:900_000]` variant).
- **Why it survives:** every size test calls `o.fetch_page()` then `o.extract_state()`, a sequence production no longer runs. The two `fetch_and_extract` tests stub `fetch_page` to None or a small string.
- **Offline `main()` with the mutant:** the 949 KB incident is silently dropped, and the suite stays green. Mitigation: it would surface as a nonzero "no ng-state script" count, which is 0 in all 2,988 real pages.
- **Violates** criterion 2 and agreement 6.
- **Fix (test-only):** assert `fetch_and_extract(url) == (REASON_OK, body)` in the multi-MB, straddle and cold-path tests; better, add an offline `main()` test.
- **Foreman re-derived [R]:** `git archive 95ca8ca1` into temp, the sed mutant at :255, the committed OECD test file → `30 passed`.

**Evidence [R] (gate):**
- **Suite and mutant table:** 334 passed. Of 24 mutants against the COMMITTED tests, these survive:
  - `fetch_and_extract` cap 800k / 900k (the defect)
  - three `main()` summary lies (advisory 1)
  - `fetch_page` cap 6 MB
  - `errors="ignore"`
  - `if not text`

  All earlier survivors (853k / 900k / 1 MB caps, M8, M9, M10) are now caught.
- **D2 straddle geometry verified by byte indexing:** JSON 799,925–800,051; the CJK character spans 799,999–800,001, and byte 800,000 is a continuation byte (0xB8).
- **Offline end-to-end `main()`, old vs new** (9 stubbed URLs covering every case):
  - **Output:** identical except the one intended delta (the 949 KB page is now kept). Same ok set, filtering, union and retention; the UTF-8 title round-trips; the buckets sum to the fetched total.
  - **Undeclared benign delta:** an empty page now counts as fetched plus "no ng-state script". Previously it was excluded by `if text`.
  - **Worker exceptions** still abort `main()` loudly, as before.
- **Network guard fires** (cache-bypass mutant → the test's own guard message). Scope is 2 files; the protected-paths diff is 0; invariant 5 holds.

**Advisories:**
1. No test covers `main()`, so summary-line lies survive. An offline `main()` test would kill those and defect 1 together.
2. `fetched = len(urls) − fetch_failed` double-counts duplicate sitemap URLs (`load_sitemap` doesn't dedupe; the old `len(pages)` did).
3. `errors="ignore"` survives: no invalid-byte fixture.
4. A cap above the largest fixture survives (inherent to fixtures).
5. The memory docstring is now accurate.

**⚠ FOREMAN CORRECTION — the foreman's pre-gate spot-check had the gate's defect as its own blind spot.** The foreman mutated `fetch_page` only, the function the tests exercise, not the entry point production calls. So it "confirmed" the guard on the same path the guard already covered: agreement 6 form (b), rerunning the author's route. **Lesson:** after a refactor, mutate at the production entry point (`main()` and whatever it submits), not at the function the tests happen to import.

**Escalation.** The gate states the fix is correct and ready; the remaining gap is a small test-only change. Options put to the user: (a) a narrow third attempt (the `fetch_and_extract` assertions plus an offline `main()` test, plus advisory 2), then re-gate or foreman spot-check; (b) accept now with the test gap recorded as a follow-up.

**User authorization (2026-09-15): parallel execution.** WS4-T11 runs in an isolated worktree (`.claude/worktrees/agent-aa29a4fb974279b69`, gitignored), concurrently with WS4-T10 in the main tree, under AGENT_TEAM.md §7. Disjoint files only: WS4-T11 may touch `scripts/ingest_oecd_aim.py` and `tests/test_ingest_oecd_aim.py`. The foreman remains the only board writer. This board record lives on WS4-T11's branch so it does not move WS4-T10's branch while that branch is under gate.

**Branch** `ws4/t11-oecd-800kb` (pushed) · owner pipeline-engineer · attempt 1 `9bbec137`:
- Removed the `data[:800_000]` cap in `fetch_page`.
- Added 4 tests that seed the warm cache and go through `fetch_page`.
- Suite 323.

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-15, on `9bbec137`: BOUNCE #1 ───** *"The fix itself is correct… The bounce is about the guard: it does not protect against the regression it exists to prevent. That is agreement 6 in its purest form."*

**Defects:**
1. **The contract test only pins a cap below ~852 KB.** Mutants `data[:853_000]`, `[:900_000]` and `[:1_000_000]` in `fetch_page` pass all 19 tests. The largest page sent through `fetch_page` is 852,208 bytes; the multi-MB test (:282) calls `extract_state` directly. With a 900 KB cap, pages of 0.95, 1.5 and 5.2 MB are silently dropped [R], and real shell pages are ~949,653 bytes. **Fix:** send a ≥5 MB page through `fetch_page` and assert full length plus id and title.
2. **The "straddle" test doesn't straddle the blob** (:237-260). The script tag starts at 799,995 and the JSON spans 800,041–800,155, so byte 800,000 falls inside the opening tag. The self-check at :249 is too loose to catch this. **Fix:** place the JSON across 800,000 and assert that span; ideally also put a multibyte UTF-8 character across the boundary.
3. **Criterion 3 (honest accounting) is not met, and the stated reason is wrong.** "parse_fail now reflects only malformed pages" is false: ~1,852 numeric shell pages carry ng-state with the wrong shape and are still counted "unparseable" (`main()` :449-453). That is the same mixed bucket the 38 hid in. **Fix:** count no-ng-state-match, JSON decode error, and state-without-incident-body separately.
4. **The committed memory justification is false** (`ingest_oecd_aim.py:147-148`, "10 threads holding a few pages"). `main()` (:432-439) retains **every** decoded page until the parse loop: ≥2.8 GB ASCII, ~5.7–11 GB if non-Latin-1. The fix adds ~+19% peak. The retention design is pre-existing; the false statement is the defect. **Fix:** correct the docstring; optionally parse inside the `as_completed` loop and drop the text.

**Evidence [R]** (git archive of `9bbec137` into scratch, netguard plugin, mutants swapped one at a time; scratch hash-verified and deleted):
- Suite 323. Chokepoint + OECD file 24.
- The new tests against origin/main's script fail 2 (`800000 == 852208`, `800000 == 802178`), matching the specialist.
- **Mutants:**
  - Survive: M1 `fetch_page[:900_000]` · M2 `[:1_000_000]` · M3 `[:853_000]` · M8 latin-1 decode · M9 greedy `(.+)` · M10 cap on `robust_fetch` cold branch.
  - Caught: M4 `extract_state[:800_000]` (3 fail) · M5 `extract_state[:900_000]` (1 fail) · M6 cache bypass (3 fail, netguard) · M7 decode-then-slice (2 fail).
- Cold path: `robust_fetch` returns the full data (common.py:410-413) and `fetch_once` does `resp.read()` with no size (:373). `min_cache_bytes` is only a refetch threshold. The fixed code parses 0.95, 1.5 and 5.2 MB cold.
- Regex cost is linear: 2.2 ms at 5.2 MB, 4.1 ms at 10.2 MB, 6.3 ms at 10.4 MB with 200k script tags.
- Scope: only the 2 allowed files; the protected-paths diff is 0 lines; trailers present; invariant 5 holds. The main tree was untouched.

**Advisories:**
1. The new tests have no network guard; if cache seeding misses, a real request would hit oecd.ai. Monkeypatch `fetch_once` to raise.
2. CI always takes the cold branch (no actions/cache), so add one cold-path test with `fetch_once` monkeypatched (this would catch M10).
3. Use a non-ASCII title (catches M8, and backs the UTF-8 claim).
4. Add script tags after ng-state (catches M9).
5. The timing test is a smoke check only (no pytest-timeout installed).
6. `errors="replace"` gives silent U+FFFD inside JSON strings; a non-UTF-8 page is undistinguished in parse_fail (pre-existing; covered by defect 3's split).
7. Real-page validation is [A] by design.

**Next:** redispatch the same pipeline-engineer instance with defects 1–4 and advisories 1–4.

## 🚨 E21 TRIPWIRE FIRED on the first real refresh in 8 weeks — 28 new AIID-signal/OECD-content rows — opened 2026-09-14 — **✅ audit done — foreman spot-check PASS per user ruling (2026-09-15) — MERGED to main · OECD refresh merges FROZEN (D25a) · remediation = WS4-T10…T14**

**User ruling on BOUNCE #2 (2026-09-15):** a narrow fix scoped to exactly the 4 re-gate defects plus advisories a–c, **verified by a foreman spot-check instead of a third full gate.**

**Fix:** pipeline-engineer (same instance as round 2), `8a03fff0` / `980a4339` / `0bc65688`.
- Its own fix-up commit `980a4339` caught that three edits in `8a03fff0` had *replaced* original sentences instead of appending. It restored them verbatim and appended the corrections after.

**─── FOREMAN SPOT-CHECK (agreement 5: this is testimony-class, a foreman check rather than an independent gate, on the user's explicit ruling) — 2026-09-15, on `0bc65688`: PASS ───**
- **Scope [R].** `git diff --stat a79caa13 HEAD -- . ':!<audit>'` is empty. `git status --porcelain` is empty; one worktree.
- **No original text lost [R], by a different route than the author's line-by-line reading.** Punctuation-stripped word alignment (`difflib.SequenceMatcher`) of the audit at `a79caa13` vs `0bc65688`: **0 original words removed.** The single flagged run is `nondeterminism.` → `nondeterminism` plus an inline pointer (punctuation only). The defect-2 clause is preserved struck-through at :917-918.
  - **The check was proven to fire:** deleting "is deterministic" from a copy flagged removed text (3 words).
  - **Foreman's first attempt was itself a check that could not discriminate.** A greedy token-subsequence scan cascaded after a punctuation change and gave the same count (6,506) on the corrupted copy and the real file. It was discarded and replaced; noted per agreement 6.
- **Item markers present [R]:** BOUNCE #2 defect 1 ×1, 2 ×1, 3 ×2, 4 ×4; advisory a ×2, b ×2, c ×4.
- **Content [R]:**
  - D25(a)'s two lift conditions present (:874-876); WS4-T10 ×6, T11 ×3, T12 ×1, T13 ×1, T14 ×2.
  - Finding 5 heading flagged as refuted (:202-206); corpus-level "30" marked UNVERIFIED (:499, :691).
  - Defect-1 note narrows the author's [R] to count and title, with the real `python -c` (:1052+).
  - Advisory-b fixture reproducible with the query-string URL shapes (:364) and distinct-path control.
- **Underlying facts [R]** against committed files: INC-05013 `aiid_id` **1436**; 1659 ∉ `ingest/aiid_full.json`; 1436 ∈; INC-00554 has 103 source_ids.

**Board clarification (gate advisory e):** "7/7 pages" = the gate's 250-page cached sample, where all 7 pages over 800 KB failed after truncation. "~38 truncated" = the full crawl (1,136 extractable − 1,098 ok). Two populations.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer (fresh instance), 2026-09-15, on `b18713ef`: BOUNCE #2 ───** *"This is not a bounce on substance. Every one of defects 1–12 is actually corrected… What remains are four defects introduced or left behind by the corrections."*

**Corrections author:** a fresh pipeline-engineer. Commits `db00e877` / `eccb1dd3` / `b18713ef` touch only the audit.

**Defects:**
1. **:885-888 — a fabricated evidence pointer on an author [R] (agreement 6 form b).** It cites "the `git show` output quoted under defect 2's singleton check", but no `git show` output exists in the file (foreman [R]: `grep -n "git show"` hits only that line). Defect 2's check is a `python -c` on INC-13037, not INC-00554. The [R] sits on the "~100 unrelated" composition, which is the gate's measurement. Fix: narrow the author's [R] to "103 source_ids + title", with the real command.
2. **:774-776 — an invented mechanism:** the IDs "cannot be un-published without a distinct deprecation reason code". This is false. A "merged" redirect is permanent under invariant 9; a reason code is only hygiene for *future* bridges. Fix: a dated note striking the clause.
3. **:763-821 (+ :230, :802, :806, :909) — the revised recommendation ignores D25**, which was committed before it (`761310a7` precedes `b18713ef`). It still says "not yet on the plan — user's call" and "WS4-T5, P0/P1" (D25: **WS4-T10, P0**). It says WS4-T6 for the 800 KB cut (D25: **WS4-T11**); the build guard and crawl budget are WS4-T13; item C "not decided" (D25: **WS4-T14**). Item A omits D25(a)'s two freeze-lift conditions. Fix: one dated D25 cross-reference note at the top of the block.
4. **Refuted figures still read as current outside the correction blocks:**
   - :200, the Finding 5 heading, still says "H3 found instead [R]" unflagged;
   - :429, the H3 table's 1552 half, restates the refuted mechanism;
   - :432-433 and :593-594 cite the corpus-level "30" from the misconfigured build as corroboration. The correct build did not measure it, so it is **unverified**.

   Fix: one-line dated notes at each.

**Evidence [R] (gate):**
- **Deletions:** exactly 4 deleted hunks. The header was re-added struck through at :12-15, so the author's claim holds; 1, 10 and 11 are logged.
- **Code citations:** all exact. `common.py:187` is right; the board's ":186" is the docstring opener, a minor board slip.
- **Committed-corpus facts confirmed:** INC-13037 is a singleton; INC-00699 is BMG with 1 OECD source; INC-00554 has 103 src and aiid 1552; **INC-05013 is aiid 1436** (1659 is not in the snapshot).
- **The author's synthetic-fixture claim is TRUE, rebuilt independently:** A-then-B vs B-then-A flips the survivor. **Control:** the same bridge with *distinct* URL paths gives 3 survivors and 0 tombstones, so the flip **requires the query-string collapse** (the check fires).
- **Arithmetic consistent.** Gate-attributed figures match this board verbatim. No refreshed-build figure is claimed as the author's own [R], except defect 1.

**Gate advisories:**
- **(a)** :316-318 gives the determinism result without gate attribution.
- **(b)** The fixture description omits the query-string URL shapes, which are load-bearing, so it is not exactly reproducible.
- **(c)** :454-456 says "moved AIID content off 1659/INC-00699"; INC-00699 never had it (the AIID content was INC-05013 / 1436). Also :781-782.
- **(d)** The corrections log says "immediately after" where some blocks are correctly at the top.
- **(e)** :228-229 over-conditions "~38 per run". The **board's own "7/7 pages" vs "38 truncated" pairing is unclear. Foreman clarification:** 7 of the gate's 250-page cached sample were >800 KB, and all 7 failed after truncation. The ~38 is the full-crawl count (1,136 − 1,098 extractable). Two different populations.
- **(f)** :652 still cites "0/29" in the original (b) text; a pointer to the :610 block would help.
- **(g)** No egress by the gate.

**⚠ FOREMAN CORRECTION — defect 3 is substantially the foreman's.** The correction brief was dispatched **before** the user ruled D25, and **the foreman committed D25 while the author was mid-task without sending it an update.** The brief told the author to follow "the gate's remediation table", which is exactly what it did. **Lesson:** a decision landing mid-task must be pushed to the in-flight agent, not just committed to the board it was told to read at start.

**Escalation (protocol step 6), awaiting the user.** The gate recommends a narrow fix pre-scoped to exactly these 4 defects (plus advisories a–c), with a foreman spot-check instead of a full third gate.

**─── VERDICT (agreement 5) — red-reviewer (fresh instance), 2026-09-15, on `docs/audits/E21-tripwire-refresh-2026-09-14.md` @ `ef9ce6fb`: BOUNCE #1 ───** *"The recommendations mostly survive. But the load-bearing evidence behind H3 and the rebuild delta is wrong, and one material harm is missing."*

**Defects** (line numbers are the audit's own):
1. **:42** — says CI didn't log the union line. It did: `[aim] union: 1097 kept + 4160 existing -> 5248 retained`.
2. **:250-281** — the H3 mechanism for 1552 is **false**. `OECD-AIM-2026-06-10-3f61` is a **singleton**, INC-13037, not a cluster member; the author's own scratch output says `in cluster: False`.
   - **Real mechanism [R]:** new row `OECD-AIM-2026-09-07-53bc` (wild-mushroom AI warning) has two refs whose **query-stripped** keys (`domin.co.kr/news/articleview.html` → 3f61; `m-i.kr/news/articleview.html` → INC-00554) bridge the two. Its URL hit (`merge_and_dedupe.py:1359-1370`) lands on 3f61 first, and `_reindex`/`_claim` (:1297-1315) absorb the megacluster into it.
   - **Root cause:** `merge_and_dedupe.py:311` `normalize_url` drops query strings.
3. **:283-295, :311-365, :466-468, :480-483** — **the full-rebuild delta came from a misconfigured build.** `merge_and_dedupe.py` was run without `parse_existing.py` (Makefile:11-13), so the gitignored `data/legacy_consolidated.json` was absent and merge **silently skips legacy** (:1411-1424). Reproduced exactly without legacy: `19517 → 14063`, 58 description changes, "severity regressions". **Correct build:** `19738 input → 14048`, 996 new IDs, 24 changed common rows, 4 description changes, **5 severity changes, all UPWARD**, 0 rows losing source_ids. **"55 unrelated rows" and "severity regressions" are REFUTED.**
4. **:335-349** — presents the 8 deprecations as benign without checking identity. **≥4 of 8 join unrelated incidents:**
   - INC-01271 (EU Grok deepfake probe) → INC-00487 (post-Trump-assassination-attempt misinformation)
   - INC-01787 (Korean fake-news crackdown) → INC-00554 (Tesla Texas crash)
   - INC-05013 (TruDi navigation) → INC-00699 (BMG v Anthropic)
   - INC-13037 (robot hub) → INC-00554

   **Stable IDs swap content:** INC-00554 retitles to the Korean robot hub; INC-00699 retitles to "Israel Funds AI Chatbot Manipulation Campaign…". **With append-only deprecations, merging writes permanent wrong redirects. This, not severity drops, is the freeze rationale.**
5. **:305** — "INC-00699 / 1659 had real AIID content" is false. Committed INC-00699 is BMG v Anthropic (1 OECD source, OECD template); the AIID content was on INC-05013.
6. **:201-203** — the 1136 vs 1098 gap is **`ingest_oecd_aim.py:129` `data[:800_000]`**, not normalize_body filtering. 7/7 cached date-hash pages >800 KB fail after truncation and 0 others fail: **~38 new incidents silently dropped per run.** 1890 = 1852 numeric + 38 truncated.
7. **:187, :271-281, :455-457** — "order-dependent" overstates. The **build is deterministic**: the control rebuild of committed inputs, run twice, is byte-identical to committed. The anchor = whichever existing entry the bridging row hits first (CVE, then source_id, then URL, then title, then the bridging row's ref order). The stable ID follows the minimum prior ID (:1548-1552) while content follows the anchor. Synthetic fixture: swapping the bridge's two refs flips the surviving description.
8. **:381-391** — the licensing check **cannot fail**: `( Entities named in the record: .*?\.)?` accepts prose (agreement 6 form a). The gate's **exact reconstruction** via `build_description()` gives **0/4,658** OECD-template corpus rows differing. **Conclusion holds on the gate's check, not the author's.**
9. **:428-431** — (b)'s blast radius is given in raw ingest rows. **Published:** 3,666 rows move null → original/oecd-aim now (4,657 after this refresh); 162 OECD-sourced rows shipping AIID text correctly stay null; `description_provenance` is not in `_CONTENT_FIELDS` (:1113-1121), so there is **no `updated` bump**.
10. **:72-73** — quoted docstring does not exist in `ingest/common.py`; the real text at :186 is "across ALL callers/threads".
11. **:117-119** — the workflow has **four** ingest steps, not three.
12. **:3-5** — still "WORKING DOCUMENT", with no do-not-regenerate marker. The file is pushed, so correct 2-9 as **dated corrections preserving the original text** (agreement 4).

**Per-claim verdicts:**
- **Claim 1 (repro): confirmed [R].** Gate's 3rd crawl 20:54-21:46Z: identical counts; the real tripwire test lists the identical 29.
- **Claim 2 (rate limiter): confirmed [R] by a different route.** 07-26 run `30191177187` fetched in 261s (pre-`fbb61ff7`); 08-02 run `30735956140` in 3000s (first post-migration run).
- **Claim 3 (legacy pages): partly confirmed, partly overstated.** "Never yield a source_id" is confirmed by code (:418-421). All 5 sampled numeric pages are exactly 949,653 bytes, which points to a generic shell page [A]. **Parse-collapse onset [R]:** 73 unparseable on 08-16 (`31926736331`), 2,213 on 08-30 (`33304582907`).
- **Claim 4 (H3): refuted as stated.** The phenomenon (anchor change discards AIID text) is confirmed, via defect 2's mechanism.
- **Claim 5 (rebuild delta): mostly refuted** (defect 3).
- **Claim 6 (mislabel/licensing):** mislabel confirmed; licensing conclusion confirmed but method defective.
- **Claim 7 (AIID snapshot): confirmed [R].**
- **Claim 8 (recommendation (b)): mechanism confirmed [R].** `merge_into` (:1873-1884) never touches description or provenance, so they travel together. **Caveat:** step-4d curation overrides (:1498-1507) apply by ANY member source_id, so the INC-00437 override mislabels if 1574 stops being the anchor. Freeze: right conclusion, wrong evidence.

**Gate's per-field rebuild delta [R]** (own script, proven to fire on a corrupted control; correct build `parse_existing` → `merge_and_dedupe`; control run twice is byte-identical to committed):
- **ID sets:** old 13,060 · new **14,048** · new-only 996 · gone 8 (INC-01271, -01469, -01787, -02381, -05013, -08148, -13037, -14317) · common 13,052. Input 19,738 = 18,650 + 1,088 new OECD rows.
- **24 common rows changed.** source_ids / updated / last_seen / source_count 24 each · references 20 · mitre_atlas 14 · mitre_atlas_tactics / owasp_llm / nist_ai_rmf 13 · owasp_asi 12 · aiid_id / tier 6 · severity 5 · description / tags 4 · attack_vector / date / title 3 · affected / source_freshness / corpus 2 · year 1. `added` and quality_tier: 0.
- **Severity: 5, all upward** (INC-14517 M→H, INC-00487 M→C, INC-05170 M→H, INC-00699 H→C, INC-14332 H→C).
- **Invariant 4 HOLDS:** 24 content changes = 24 `updated` bumps, no mismatch.
- **Invariant 9 HOLDS:** 1,051 prior deprecations preserved; 8 new, all "merged".
- **Sitemap tolerance:** CI, the author and the gate agree exactly at count level and on the 29-ID population. Not measured: min.json / STIX / HF deltas.

**⚠ Published over-merge, independent of the refresh [R]:**
- **INC-00554:** only AIID-1552 and OECD-AIM-2026-06-30-4590 are the Tesla crash; ~100 of 103 source_ids are unrelated (Korean defence MOUs, wildfire drones, bank anti-phishing launches…).
- **Bridge keys:** wowtv read 16, asiatoday view.php 15, m-i.kr articleview 13, hankooki articleview 13, it.chosun articleview 11.
- **Corpus-wide:** **151 normalized URL keys collapse distinct raw URLs across >1 source row, touching 1,225 source rows.** Top keys: bugzilla.redhat.com/show_bug.cgi 215, cve.org/cverecord 87, vuldb.com 83, github.com/mlflow/mlflow 74, moodle discuss.php 63. CVE rows are partly shielded by `cve_disjoint` (:1306).
- **Top no-CVE clusters:** INC-04106 174 · INC-00554 103 · INC-03798 41 · INC-00861 32 · INC-00134 24. Whether the CVE megaclusters (INC-04260 143, INC-01015 120, INC-08766 68) are URL-bridged is [A].

**Gate's remediation table:**
- **A. Freeze OECD refresh merges: APPROVE**, on the wrong-merge / content-swap / permanent-redirect rationale.
- **B. Option (b): APPROVE in principle.** Same PR should revisit the INC-00437 override and ship the tripwire replacement.
- **C. AIID snapshot in the weekly workflow:** user scope call under D1.
- **D. Per-row overrides: REJECT.**
- **E. Tripwire evolution: APPROVE**, plus a **stable-ID continuity check** (a common ID whose title changes while its anchor source did not; it would have caught INC-00554 and INC-00699).
- **F. Option (d): RE-SCOPE** to the `normalize_url` query-string collapse (WS4-T5).

**Gate's proposed new tasks (not yet on the plan; the user's call):**
1. **WS4-T5, P0/P1:** fix `normalize_url` (keep identifying query params, or refuse URL keys shared by distinct raw URLs), then audit megaclusters, INC-00554 first. **Unmerging published rows touches invariants 3 and 9; escalate the design.**
2. **WS4-T6:** stop the 800 KB truncation, with a parser contract test using a >800 KB page.
3. **WS4-T6/ops:** numeric slugs fill ~1,852 of the 3,000-URL window since late August. Skip them or budget by date-hash URLs, and check for a coverage gap. The job runs 51-52 min against a 60-min timeout.
4. **Build guard:** `merge_and_dedupe.py` silently proceeds without `data/legacy_consolidated.json`. Fail loudly or run `parse_existing` itself. **This is exactly how the audit's delta went wrong.**
5. **Deprecation hygiene:** before any refresh PR merges, review each new "merged" deprecation for same-incident identity; consider a distinct reason code for weak-key bridges.
6. **Curation-override keying:** step 4d applies by any member source_id; key overrides to the anchor, or assert it.

**Gate's advisories:**
- Scope clean: foreman commits touch PROGRESS.md only; author commits touch the audit only.
- Gate cleanup verified: worktrees removed, tree clean, its own process killed.
- **Egress today:** three full OECD crawls (CI, author, gate), all via `ingest/common.py`. Any further verification must reuse measurements, not re-crawl.

**⚠ FOREMAN CORRECTION 2026-09-15 — the foreman relayed the refuted figures to the user.** In chat on 2026-09-14 the foreman presented the author's "58 existing entries change description, 55 unrelated, ≥2 drop Critical→High" as the audit's findings, flagged as not yet gated. It also recorded "severity regressions" as a reason to freeze in the interim board entries below, which are kept as written per agreement 4. **Both came from a misconfigured build and are refuted** (defect 3). The foreman's own independent spot-checks that day (the 800 KB cut, the wrong-merge titles, `normalize_url:311`, INC-00554's composition) all **survive**. **Lesson:** a scratch rebuild that silently skips an input is agreement 6 form (a) at build level. Nobody could tell it from a correct build by its output. The different route (a control build proven byte-identical to committed) caught it.

**Next:** audit corrections → a fresh pipeline-engineer (the prior instance went idle twice; agreement 3 says replace). Remediation and new tasks → the user.

**The manual `workflow_dispatch` (user-authorized) worked as a test of the persist fix.**
- Run [`34858279213`](https://github.com/emmanuelgjr/genai_incidents/actions/runs/34858279213) on `main` @ `05f536ff`. **Persist ✅** for the first time since 2026-07-19; `origin/refresh-state` moved `f41ad68e` → **`bfbdec57`** (aiaaic, oecd and kev all `ok` / last_success 2026-09-14). Re-merge + render + validate ✅.
- It then **failed at Unit tests (1 failed, 318 passed)**, a step no run had reached in 8 weeks, so **no refresh PR opened and nothing reached main.** The gate failed closed, as designed.

**What fired:** `tests/test_e21_partA_inc00437_provenance.py::test_oecd_aiid_content_disagreement_is_unique_to_inc00437`. The E21 Part A invariant says exactly one aiid_id-bearing row (1574 / INC-00437) ships a description that is not AIID's template. The refreshed inputs produce **29**: `[1552, 1574, 1584, 1604, 1610, 1612, 1616, 1622, 1641, 1642, 1643, 1644, 1646, 1647, 1650, 1654, 1656, 1658, 1659, 1660, 1661, 1662, 1665, 1666, 1668, 1669, 1671, 1673, 1674]`.

**Foreman's working hypothesis (NOT yet established; that is the investigation's job):**
- `ingest/aiid_full.json` (the D1 sanctioned AIID snapshot) holds **1,548 rows, max aiid_id 1581**. Its last commit is `19fa2986` (OWASP migration); its last *content* refresh has not been checked.
- `ingest_aiid_snapshot.py` runs from the **Makefile only, not from auto-refresh**. The weekly OECD AIM refresh therefore brings in rows cross-referencing AIID incidents newer than the snapshot. No AIID row competes for those `AIID-<n>` keys, so OECD's row wins the merge. That is INC-00437's exact mechanism, now at scale.
- **1552 < 1581 does not fit this story** and needs its own explanation.
- **Why it matters beyond a test:** these rows would ship OECD-template text under an AIID cross-reference signal. Whether that also mislabels `description_provenance` / `description_source` is the provenance question E21/E23 ruled on.

**Note for next Sunday:** the scheduled 2026-09-20 run will fail at the same place, fail-closed with no PR. That is safe, but it means the refresh stays blocked until this is resolved.

**AIRI:** still HTTP 404 (`consecutive_failures` 9). Its step's "success" label is `continue-on-error`, not a recovery.

**Dispatched:** pipeline-engineer (fresh instance), investigation only, deliverable `docs/audits/E21-tripwire-refresh-2026-09-14.md` on branch `ws4/e21-tripwire-oecd-aiid`. **No data or override changes until the user rules on the options.**
- **The first instance died on a session limit with nothing committed.** The foreman checked the tree (clean, one worktree) and redispatched a fresh instance with a commit-early instruction.

**⚠ UPDATE 2026-09-14 — the OECD AIM ingest has COLLAPSED, and the tripwire may be its symptom, not the disease. [R] from CI logs** (`gh run view <id> --log | grep -E "\] (fetched|parsed|union|wrote)"`):

| Run | Fetched | Parsed ok / unparseable | Time | Kept + existing → retained |
|---|---|---|---|---|
| 07-12 `29182692358` | 3000/3000 | 2,939 / 61 | 292s | 2,924 + 3,792 → 4,049 |
| 07-19 `29676405074` | 3000/3000 | 2,940 / 60 | 358s | 2,926 + 4,049 → 4,160 |
| **09-14 `34858279213`** | 2988/3000 | **1,098 / 1,890** | **3,026s** | 1,097 + 4,160 → **5,248** |

- **The union column is the alarm.** In July ~2,815 of ~2,926 parsed rows overlapped existing source_ids. On 09-14 only **~9 of 1,097** did, so **~1,088 source_ids were never seen before**, while most known URLs return 404 (the local repro shows the same 404s).
- **Hypothesis H2: OECD re-keyed its incident URLs/IDs.** If true, the refresh would add ~1,000 **duplicates** of held incidents under new source_ids. The 28 new tripwire rows, including the unexplained 1552, may be those duplicates rather than new AIID incidents (H1). The investigator has been told to separate H1 from H2 per row and to compare IDs, not totals (agreement 6 form d).
- **Why this matters:** without the E21 tripwire, this would have reached a refresh PR as "+1,088 rows". A tripwire built for one provenance row caught what may be a source-wide re-keying. **The persist bug had been hiding all of this since 07-26.**
- **⚠ CORRECTION, same day — "most known URLs return 404" above is WRONG. Kept as written per agreement 4.**
  - **What was wrong.** The foreman inferred it from the *tail* of the local repro log, which is a sample of the failures, not the population. CI logged only **40 HTTP errors in total (39×404, 1×403)**. So the 1,890 "unparseable" pages overwhelmingly fetched fine and then failed to yield a parseable `ng-state` blob. That points to a **site-side page-structure change or parser breakage (WS4-T6 territory)**, not dead URLs.
  - **What stands, and what it now means.** The union-overlap collapse (~9 of 1,097) still stands. H2 is **not refuted, but re-framed**: if old-template pages no longer parse, the ~1,097 that do may be a *different page population* (new template), not re-keyed IDs. That is still open.
  - **The slowdown is explained, and it is not retries.** 292s → 3,026s traces to the WS0-T4 chokepoint migration (`fbb61ff7` / `5937653e`, 2026-07-29), which moved `ingest_oecd_aim.py` onto `ingest/common.py`'s **global per-host 1 req/s limiter**. All 10 workers now share one budget. That is **intended conduct (invariant 5), not a bug.**
  - **⚠ Consequence: timeout headroom.** A 3,000-page crawl is now ~50 min inside `auto-refresh.yml:27`'s `timeout-minutes: 60`. The 8 failed runs each took ~51 min in total. **One slow week times the whole refresh out.**
  - [R] for the timeout line; the rest is investigator testimony pending the audit.
  - **Lesson.** The same aggregate-over-sample error as the 9-vs-8 correction, twice in one session, both caught by a party using a different route.

**Interim findings from the investigator (testimony until the audit lands):**
- **AIID snapshot** fetched 2026-07-18; a newer official one exists (`backup-20260907101103.tar.bz2`). Update is Makefile-only.
- **The committed corpus already has a second AIID-template exception, 898 / INC-08183, outside the tripwire's two-file scope.** The tripwire cannot see it (a scope gap; route to tripwire evolution).

**Audit landed:** `docs/audits/E21-tripwire-refresh-2026-09-14.md` (`fd1dc409`, `ef9ce6fb`; pushed). Gate is in progress (red-reviewer, fresh instance). **The gate's interim message leans BOUNCE; that is not the final verdict, which is pending its OECD re-fetch.** Its load-bearing interim points:
- **(1)** The audit's H3 story for 1552 is false.
- **(2)** Of the rebuild's 8 "merged" IDs, **≥4 join unrelated incidents.**
- **(3)** ~38 new incidents per run are silently dropped by an 800 KB page cut.
- **(4)** "Order-dependent" overstates it: identical inputs rebuilt twice are **byte-identical to the committed data**. The build IS deterministic; anchors flip when inputs change.
- **(5)** Recommendation (b)'s blast radius is **3,666 published rows**, not raw-ingest rows.

**Foreman re-derived two of these independently [R]:**
- **The 800 KB cut is real:** `scripts/ingest_oecd_aim.py:129` → `return data[:800_000].decode("utf-8", errors="replace")`.
- **The wrong-merge targets are real, per `data/incidents.json` titles:**
  - INC-13037 "South Korea Launches AI-Enabled Construction Robot Research Hub" (1 source_id) → merged into INC-00554 "Tesla Driver … Fatal Texas Home Crash" (**103 source_ids**).
  - INC-05013 "AI-Enabled TruDi Navigation System … Patient's Stroke" → INC-00699 "BMG Sues Anthropic Over AI Training …".

**⚠ Why this outranks the tripwire.** `id_deprecations.json` is append-only (invariant 9). **A refresh PR merged in this state would PERMANENTLY redirect unrelated incident IDs into each other**, with no way to undo it short of a new ruling. **The foreman is treating "no OECD refresh merges" as in force, pending the user's ruling.** The 09-20 scheduled run stays fail-closed at the tripwire, so nothing can reach main in the meantime. A 103-source_id cluster on a single crash also suggests over-merge chaining **already in the published corpus**; the gate has been asked to size it.

**🚨 CONFIRMED 2026-09-14 — the published corpus contains a query-string over-merge, and its cause is a one-line URL normaliser.**
- **Gate status message** (not the final verdict): INC-00554 is a published over-merge today, with ~100 of its 103 source_ids being unrelated Korean-news OECD rows. Root cause: `merge_and_dedupe.py:311`, `normalize_url`, strips query strings, so every `articleView.html?idxno=N` on one site collapses to one weak dedup key.
- **Foreman re-derived it independently [R]:**
  - `scripts/merge_and_dedupe.py:311` → `u = u.split("?")[0].split("#")[0]`.
  - Published INC-00554 "Tesla Driver Reportedly Said Driver-Assistance Mode Was Engaged During Fatal Texas Home Crash" carries **103 source_ids: OECD 100 / AIID 3**, and **512 references**. Top hosts: oecd.ai 100 · yna.co.kr 54 · mk.co.kr 34 · asiae.co.kr 31. 34 of the references are `articleView` URLs.
- **Other clusters in the published corpus's top 6 by source_id count** (not yet assessed; may be legitimate vendor-feed grouping or the same defect):
  - INC-04106 promptfoo plugin agentic:memory-poisoning (174)
  - INC-04260 TensorFlow CVE-2023-33976 (143)
  - INC-01015 Flowise (120)
  - INC-08766 OpenClaw (68)
  - INC-08911 OpenClaw (47)
- **Consequences, not yet quantified:**
  - Published incident counts are understated by however many distinct incidents are collapsed.
  - Per-incident fields (title, description, severity) on over-merged rows describe one incident while carrying another's sources.
  - Any past tombstone produced by this chaining is a permanent wrong redirect.
- **This is a WS4-T5 (dedupe audit) defect that is live in shipped data, not a refresh-only risk.** It predates this session and was caught only because a tripwire built for one provenance row fired.

## 🔧 WS4 REGRESSION — refresh-state persist fix (D5-impl) — opened 2026-09-14 — **✅ done — PASS (attempt 3) — MERGED to main**

**Post-merge `workflow_dispatch` result [R]:** Persist succeeded and refresh-state advanced to `bfbdec57`. The fix is confirmed against real GitHub. See the E21 tripwire entry above for why no PR opened.

**User ruling on the escalation, 2026-09-14:**
- Keep the line-number citation: `:59` becomes `:66`, not a content-based cite.
- A third attempt, scoped to that one line. Advisory B (unguarded `--force` / `[skip ci]`) is deliberately not in scope and stays a follow-up.
- **The user authorized one manual `workflow_dispatch` of auto-refresh after merge.**

**Attempt 3** `99a0f8fe` (pipeline-engineer): `docs/INGESTION_CONDUCT.md:369` `:59` → `:66`, a one-line diff.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer, 2026-09-14, on `99a0f8fe`: PASS ───** *"The register citation now resolves to the git clone, the scope is one line, and the script and tests are byte-unchanged, so the gate-2 mutation evidence still holds."* **Defects: none.**

**Evidence the gate measured [R]:**
- **Refs.** HEAD = origin branch = `99a0f8fe`.
- **Scope.** `56f6ce77..4779459c` touches PROGRESS.md only. `4779459c..99a0f8fe` touches INGESTION_CONDUCT.md only (1/1).
- **The citation resolves, and this check can fail.** `git show 99a0f8fe:scripts/persist_refresh_state.sh | sed -n 66p` prints the `git clone` line. At gate 2 the same command showed `:59` was the trap line.
- **Script and tests unchanged.** `git diff --quiet 56f6ce77 99a0f8fe -- scripts tests .github .gitattributes` exits 0, so the gate-2 mutation matrix carries over unchanged.
- **Data untouched.** `git diff --stat 56702426 99a0f8fe -- data schema mappings ingest src legacy docs/data` is empty.
- **Suite and tree.** 319 passed; tree clean; one worktree.

**Advisories:**
- **(A) Testimony miscount.** The specialist reported 3 hits for the citation grep; there are **4**, because `PROGRESS.md:143` was omitted. All PROGRESS hits are dated records, so the conclusion is unaffected. Do not repeat "three".
- **(B) Carried, not bounced, per the user's ruling:**
  - `--force` and `[skip ci]` are unguarded by tests. **Follow-up owed to WS4:** assert `[skip ci]` in case (b), and add a diverged / non-fast-forward case.
  - Notice text and the commit-message inaccuracy are already corrected on this board.
  - **Drift-stale first refresh PR** (render_docs_stats is not in the refresh workflow): re-render before merging it.
  - `workflow_dispatch` once after merge (user-authorized, above).
- **(C) The line-number citation will go stale again** on any comment edit above script line 66, the same failure as bounce #2. Whoever next edits the script header must re-resolve `INGESTION_CONDUCT.md:369`.

**Foreman step-6 stray check:** `git status --porcelain --untracked-files=all` is empty before recording. **Step 7:** no counts, public claims, licensing text, taxonomy lists or version strings changed (a workflow step, a script, tests, and one register line cite), so docs-warden is not dispatched.

**─── RE-GATE VERDICT (agreement 5) — red-reviewer, 2026-09-14, on `56f6ce77`: BOUNCE #2 ───** *"The only defect is a one-token stale line citation in the invariant-5 register. D1 and D2 are both genuinely fixed, and the new mutation test is load-bearing."*

**Defect 1.** `docs/INGESTION_CONDUCT.md:369` cites `scripts/persist_refresh_state.sh:59`. At `56f6ce77`, line 59 is `trap 'rm -f "$TMP_STATE"' EXIT`; the `git clone` is now **line 66**. The bounce-fix commit grew the header comment by 7 lines and did not update the register (criterion 3, active invariant 5 / D22). **Foreman re-derived [R]:** `git show 56f6ce77:scripts/persist_refresh_state.sh | sed -n '59p;66p'` → trap, clone. Suggested fix: `:66`, or cite by content ("the `git clone` in `scripts/persist_refresh_state.sh`") so comment edits cannot break it again.

**Evidence the gate measured [R]:**
- **Scope.** `930e6045` touches PROGRESS.md only. `56f6ce77` touches only the script and the test. data, schema, mappings, ingest, src, legacy and docs/data are untouched across `56702426..56f6ce77`.
- **Script diff is comments only.** The non-comment lines of `8debf617` and `56f6ce77` are identical.
- **Cases a/b/c unchanged.** Their bodies and docstrings are untouched.
- **Mutation test is load-bearing, by a different route.** Pre-fix inline shell from `56702426`: 3 fail. Fetch-only revert: 3 fail. Decoy (fixed lines kept as comments, real code broken): b and c fail. Clone without `--depth 1` (bug premise gone): the mutation test fails, so it detects when its own premise stops holding. **No mutant that breaks the fetch/checkout path passes the 5-test file.**
- **Suite and D2.** Suite 319. D2 dates now match the run logs. Clean finish.

**Advisories:**
- **(A)** Ruling on the foreman's candidate: an **advisory, not a defect.** **Board correction, since commit messages are immutable:** `56f6ce77`'s message lists four of the five extraction changes. It omits the notice-text change (`source_health.json unchanged` → `ingest/_state/source_health.json unchanged`, ~:88), and its sentence *"None of these change what a correctly-configured caller observes"* is inaccurate, because log text is observable. No consumer parses it, and test (c)'s substring still matches.
- **(B)** Two criterion-1 properties are **unguarded**: mutants dropping `--force` or `[skip ci]` pass all 5 tests. Proposed follow-up: assert `[skip ci]` in case (b), and add a diverged (non-fast-forward) case.
- **(C)** The mutation-test precondition is exact-text, so rewording the fix lines will turn it red on purpose.
- **(D)** Carried from gate 1: the drift-stale first refresh PR (render_docs_stats not in the refresh workflow), and a `workflow_dispatch` after merge.

**Foreman correction.** Before the re-gate, the foreman spot-checked `56f6ce77` for the off-by-one phrasing but did not re-resolve the register's line citation, which it had checked at attempt 1. A line-number citation is invalidated by any edit above it. The check the foreman ran could not have caught this.

**Escalation, awaiting the user.** Two bounces on the same task → stop, per step 6. Options put to the user:
- (a) Authorize a third attempt limited to the one-line register fix plus advisory B, with a narrow re-gate.
- (b) Accept with the defect routed as a follow-up note.
- (c) Other.

---

**History: attempt 1 and BOUNCE #1** (preserved as written):

**Why this exists: the corpus has been frozen at 13,060 since v2.9.0, because the weekly refresh has not opened a PR since #97.**
`auto-refresh.yml` has gone red on **9 consecutive scheduled runs, 2026-07-19 → 2026-09-13**. They are **not all the same failure**:
- **2026-07-19** (run `29676405074`) took the `--orphan` path, created `refresh-state` (`f41ad68e`), opened the PR, and failed at the **intended** "Enforce source health" step (AIRI stale).
- **The 8 runs 2026-07-26 → 2026-09-13** (e.g. `30191177187`, `34748318826`) failed at **"Persist source health counters to refresh-state branch"**: `fatal: 'origin/refresh-state' is not a commit` (exit 128).

**Mechanism:** `git clone --depth 1` implies `--single-branch`, so `git fetch origin refresh-state` writes only FETCH_HEAD and the checkout of `origin/refresh-state` dies. `set -e` then skips rebuild, tests, and the PR step. That throws away ~50 minutes of successful ingest every week. The "branch exists" path was never exercised before D5-impl merged. **Why nobody noticed:** the board had pre-announced the run would go RED by design (AIRI), so a *different* red read as the expected one. The Restore step is **not** affected: actions/checkout sets a wildcard refspec, and its logs say "Restored".

**Branch** `ws4/refresh-state-persist-fix` (pushed) · owner pipeline-engineer · attempt 1 `8debf617`: extract the step to `scripts/persist_refresh_state.sh` with an explicit `refresh-state:refs/remotes/origin/refresh-state` refspec; `tests/test_persist_refresh_state.py` (local bare-repo fixture, cases a/b/c); INGESTION_CONDUCT register repointed to `scripts/persist_refresh_state.sh:59`; `.gitattributes` `*.sh text eol=lf`. Suite 318 (314 + 4).

**─── VERDICT (agreement 5) — red-reviewer, 2026-09-14: BOUNCE #1 ───** *"The functional fix is verified correct … Both defects are committed-text fixes, so a narrow re-gate is enough."*

**Evidence the gate measured [R]:**
- It copied the **pre-fix inline shell mechanically from `56702426`** (not the specialist's revert) and ran the new tests against it: cases (b) and (c) failed, exit 128.
- Committed script: 4/4 pass. Mutants: push-removed fails (a)(b); notice-changed fails (c); half-revert fails (b)(c).
- Line-by-line equivalence with the old inline shell checked. Token exposure unchanged. Register line resolves. `git diff 56702426 8debf617 -- data schema mappings ingest src legacy` is empty.
- Offline rebuild in a separate clone gave **every** generated file byte-identical (`data/incidents.json` MD5 `d5fedf96…`), 13060/13060 valid. The code reading shows the WS0-T3, E21 and OWASP-2026 forms live in the fetch scripts.
- **[A]:** the live network re-ingest cannot be re-run offline, so "the first PR won't revert gated work" is partly verified.
- 5.i confirmed from run `29676405074`'s log: **the PR opens, then the run ends red on AIRI** (refresh-state shows airi_navigator stale, 8 failures, no `paused_until`).

**Defects:**
1. **Test 4 (`test_case_b_fails_against_pre_fix_plain_fetch`, `tests/test_persist_refresh_state.py:212`; module docstring `:22-25`) never invokes the script.** It PASSED against the pre-fix shell. Its docstrings claim it "reverts the fetch/checkout lines" and "proves this suite would have caught the regression", and both claims are false: agreement-6 form (a)/(b). Fix, preferred: make it load-bearing. Swap the fixed lines in a copy of SCRIPT, asserting each replacement happened exactly once, run the copy on the case-(b) fixture, and assert exit 128. Otherwise: reword the docstrings to what it actually checks.
2. **Wrong date range** at `scripts/persist_refresh_state.sh:25-26` and `tests/test_persist_refresh_state.py:5-6`. The text says every run 07-19 → 09-13 failed at Persist; 07-19 did not. It is 8 runs, 07-26 → 09-13. The script contradicts its own `:34`.

**Advisories:**
- **(A)** Undeclared but benign extraction changes; name them in the fix commit: `set -euo pipefail`, the state-file existence check, `mktemp` + trap, full-path notice text, `$WORKSPACE` via `pwd`.
- **(B)** "removed again on exit" (`:23`) is true only on success.
- **(C) ⚠ first-run risk:** the refresh workflow's rebuild step does not run `render_docs_stats.py`, and `check_stats_drift` runs only in validate.yml. GITHUB_TOKEN-opened PRs normally don't trigger pull_request workflows. So the first count-changing refresh PR can open drift-stale with no failing check, and merging it **recreates the post-#97 drift-red-main incident** (the CLASS fix owed to WS4 is still unlanded).
- **(D)** Fixture portability low risk.
- **(E)** History growth: no action.
- **(F)** After merge, `workflow_dispatch` once to exercise the real-GitHub fetch.

**Foreman routing:**
- Defects 1–2 plus advisories A–B go to pipeline-engineer (same instance; small, well-defined scope).
- **Advisory C is recorded here as an open item that must be closed before the first post-fix refresh PR is merged.** It is not folded into this task; its scope is the owed drift CLASS fix. The next scheduled run is **2026-09-20**.
- **(F) is an outward action; it needs the user's go.**

## 🔤 OWASP LLM TOP 10 → 2026 EDITION — user-directed, OUT OF PLAN, landed 2026-08-17, **NOT GATED**

**Not a WS task.** Direct user request during the Phase-1/Phase-2 interval, executed
by the main session rather than dispatched — so **no specialist owned it and no
red-reviewer verdict exists.** Recorded here because it changed a core taxonomy on
every published surface, and a change of that size with no board row is exactly the
archaeology this file exists to prevent.

**Branch** `taxonomy/owasp-llm-top10-2026` · **PR #99** (open, 5/5 checks green,
MERGEABLE, unmerged) · commits `19fa2986` (migration), `3f634a05` (verify gate),
`19dc8f66` (site link). Record: `docs/audits/owasp-llm-2026-migration-delta-2026-08-17.md`.

**What changed.** OWASP published the 2026 edition 2026-08-03. It is a **renumbering
plus one rename** — no entry added, none removed — so 2025→2026 is a **bijection**
over `LLM01`–`LLM10`. **17,498 code assignments across 11,556 of 13,060 entries**
rewritten. `LLM07` System Prompt Leakage → `LLM08` **Hidden Context Exposure**
(renamed and widened). Largest moves: Excessive Agency `LLM06`→`LLM03`, Improper
Output Handling `LLM05`→`LLM10`, Unbounded Consumption `LLM10`→`LLM06`.
Crosswalk: `mappings/owasp_llm_2025_to_2026.json`; 2025 catalog **retained and
marked superseded**, because every release ≤ v2.9.0 and its DOIs carry 2025 codes
and cannot be read without it.

**Sourcing note, because it nearly went wrong.** `genai.owasp.org/llm-top-10/` still
serves the **2025** list, and the top-ranked "2026" secondary writeup recycles it;
a second syndicated source published an ordering that contradicted both itself and
the primary. The list was taken from the **official PDF (122 pp.) and the
`GenAI-Security-Project/GenAI-LLM-Top10` repo**, and the two agree exactly.

**⚠ This is a SILENT breaking change.** The code space is **identical before and
after**, so `schema/incident.schema.json` validates a correct migration, a partial
one, and a **doubly-applied** one equally happily. `LLM03` stays valid and changes
meaning. Nothing in CI could have caught a wrong permutation — hence the permutation
lives in data and is asserted bijective at load, the migration fails closed on any
undeclared field change, and two independent guards block double-apply.

**Evidence — [R] re-derived, but SELF-verified, not independently gated.** A control
build was made in a clean worktree at `HEAD` (pre-migration code AND inputs) and
compared entry-by-entry with the migrated build: **ID sets identical (13,060,
symmetric difference 0) · entries whose `owasp_llm` ≠ crosswalk image of the control:
0 · entries with ANY other field changed: 0 · 17,498 → 17,498.** Plus
`validate.py` 13060/13060 valid 0 errors, `check_stats_drift` clean, 314 tests.
**The measurements are [R]; the absence of a gate is the gap.** Under agreement 5
the verdict is testimony — here there is no verdict to testify to. **`docs-warden`
has NOT run** despite protocol step 7 applying (taxonomy lists changed); the
cross-surface sweep was the foreman's own and is therefore `[A]`-class on the one
question that matters, *did an independent party check this*.

**The control build earned its cost — it caught a real defect.** See PRECEDENT 4
below: retain-on-drop rows are a build **input**, an inputs-only migration missed 9
of them, **and the totals still matched exactly** while the distribution was wrong.

**Scope limit, stated so nobody later reads completeness into it: renumbered, NOT
re-classified.** Several 2026 entries widened their scope (LLM08 now covers all
non-user-facing context, not just the system prompt; LLM01 cross-modal injection;
LLM10 insecure generated code). Incidents that would **newly qualify** were **not**
added — that means re-running classifiers over descriptions, i.e. the WS0-T3 cascade
hazard. **Mappings are complete w.r.t. the 2025 labelling and conservative w.r.t.
2026 scope.** Closing that gap is WS2 annotation work, routed below.

**Open:** E24 (version ruling — the CHANGELOG entry sits under `[Unreleased]`
deliberately). **Deployment:** `pages.yml` fires only on push to `main`, so the live
site still serves 2025 until #99 merges; HuggingFace and PyPI trigger on
`release: published`, so published artifacts stay on 2025 until a release is cut.

## ⛔ SUPERSEDED — the pending-exit block below is the record of the state before the declaration above (2026-07-31)

PHASE-1 EXIT — PROJECT-SIDE COMPLETE, AWAITING ONE USER ACTION (2026-07-31)

**Phase 1 is NOT declared. It cannot be declared by the foreman, and this entry
records why rather than leaving a gap.**

**Everything in the project's hands is done and gated.** `main` at `983485f6`,
local == origin. **Zero unmerged branches.** Tree clean, no strays.
`check_stats_drift.py` exit 0, `pytest` 314 passed. Seven gated merges, thirteen
gate verdicts, four user escalations. The packet is at
`docs/audits/PHASE1-PACKET-2026-07-31.md`; the checklist at
`docs/audits/PHASE1-EXIT-2026-07-31.md` with **all ten criteria `[R]`-backed**.

**What remains is ONE action, and it is the user's by this project's own rule.**
**Criterion 9 clause 2: the OECD outreach email** — drafted at
`docs/outreach/oecd-aim-terms.md`, gated PASS, **not sent**; recipient
`ai@oecd.org`, **unconfirmed as to desk**. Three of four sent and logged
(AIAAIC, AIID, MIT AIRI, all 2026-07-27).

**Why the foreman does not close it:** `CLAUDE.md` escalation rule 8 reserves
**"any outreach email (agents draft, the user sends)"** to the user, and the
user has separately reserved outreach to themselves personally. **This is a
boundary, not a blocker to work around.** Sending it, or marking the criterion
met without it, would be the E18/E20 failure — a criterion satisfied by a claim
nobody checked — committed **on the exit checklist itself**, which is the one
document where it would do the most damage.

**Why the foreman does not declare Phase 1:** the user's stated sequence is
*"I review the packet, cut v2.9.0, and Phase 1 is declared on the board."*
**The declaration follows the user's review and version cut, neither of which
has happened.** The board is the foreman's to write; the ruling is not the
foreman's to make.

**Two honest outcomes, both already prepared for:**
- **User sends the email** → criterion 9 closes 4-of-4, **FLAG 3 disappears**,
  and Phase 1 exits with **no open criteria** (FLAGS 2 and 5 remain disclosed,
  but they are statements about history, not defects).
- **User declares with clause 2 open** → the checklist already reports it
  open, in plain language, in three places, **and nothing anywhere contradicts
  it**. It closes whenever the email is sent and logged.

**When the user rules, the declaration is a one-line board change.** Nothing
else is waiting on anything.

