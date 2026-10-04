# Wave 1-2 ingest PR: red-reviewer gate 1: BOUNCE #1

**Dated record, 2026-10-03. Do not regenerate.** This gate ran on `ws4/wave12-ingest` @ `d49d9647`. Part 1 below was saved as received and concatenated by shell. Part 2 (the evidence) will be appended the same way when it arrives.

---

## Part 1: verdict and defects

VERDICT: BOUNCE (first bounce on this PR). Gate on ws4/wave12-ingest @ d49d9647. Evidence follows in a second message.

On your precision criterion: the PR does NOT fail it. cvelistV5 precision is about 97% (clear false positives only) or about 91% (borderline cases counted as misses). The existing corpus's own CVE/GHSA feed measured about 48% by the same method. So the bounce is not for precision. It is for row-vs-code licence mismatches, a date bug, and a small set of false positives that can be removed now and will be permanent once released. The delta is true: 0 existing entries changed, which I re-derived independently. Reproducibility is byte-exact, tests pass, and the guard tests fire when mutated.

DEFECTS
1. arXiv dates are wrong, and 8 papers fall outside the declared window. `scripts/ingest_arxiv_oaipmh.py:268/405/413` uses the OAI `arXiv` `<created>` field, which in this harvest is the LATEST version date, not first submission. Proof by a different route (arXivRaw version history): 2411.16769 has v1 Mon 25 Nov 2024, but OAI `created` is 2026-09-26 and the row date is 2026-09. 20 of 63 rows have a date that differs from the id's YYMM. 8 were first submitted before the 2025-10-03 window: 2411.16769, 2504.19373, 2507.16329, 2508.14070, 2508.20083, 2508.20863, 2508.21669, 2509.05755. Violates: field correctness of the new entries, and the stated 12-month window (delta section 6). FIX: take date/year from the v1 date (metadataPrefix=arXivRaw, version v1, same oaipmh host through common.py), or for new-style ids from the id's YYMM. Apply the window to that date. Either drop the 8 or keep them correctly dated, and say which. Add a fixture test where created and v1 differ.

2. AVID CVE-class rows carry CNA text under an MIT/AVID licence marker. 105 of the new AVID+CVE entries (for example INC-14974 for CVE-2024-10109, INC-14975 for CVE-2024-10273) have `content_license.license` MIT, source avid, `description_source` avid, but the description is the CVE CNA text. SOURCE_LICENSES 6.1 itself says: "Records classed CVE Entry carry CNA text, which is governed by the CVE ToU (section 6.2), not by MIT." Violates invariant 10 (the code disagrees with its own row). FIX: in `scripts/ingest_avid.py`, for CVE Entry class rows, set `content_license` to the same dict as `ingest_cvelistv5.CVE_TOU_MARKER`. Set `description_source` to a value that shows the text is CNA text via AVID. Then rebuild and re-delta.

3. AVID third-party report text (87 rows, for example 0din disclosures such as INC-15011) ships as verbatim first sentences, marked `description_provenance: verbatim` under MIT. Row 6.1's Action requires "facts + link + original summary where the record text is third-party-derived", and the delta itself says this text is "not AVID's to license". Cutting to one sentence is still verbatim. FIX: generate original deterministic prose for third-party rows, as was done for arXiv. If the preferred fix is instead to keep the verbatim sentence and amend 6.1, that is a licensing call to escalate to the user (protocol step 8). The agents should not decide it.

4. `docs/INGESTION_CONDUCT.md` entry 3 still says PENDING. No `git clone` or subprocess egress exists in the three ingest scripts (only `wave12_delta.py`, which runs a local `git show`). Following the entry's own instruction, replace ONLY its heading and status line:
heading: `### 3. git clone of avidml/avid-db and CVEProject/cvelistV5 (NOT USED, HTTP route taken; added 2026-10-03, status updated 2026-10-03)`
status line: `**Status: not used, HTTP route taken.** The wave 1/2 ingest (branch ws4/wave12-ingest) fetches AVID as the GitHub tarball (api.github.com/repos/avidml/avid-db/tarball/main, ingest/common.py fetch_once) and cvelistV5 as the daily baseline release asset (ingest/common.py fetch_to_file: fail-closed robots check, per-host rate limit, project User-Agent). scripts/ingest_avid.py, scripts/ingest_cvelistv5.py and scripts/ingest_arxiv_oaipmh.py contain no git clone, subprocess or other non-HTTP egress (red-reviewer grep, 2026-10-03). The text below is kept as the record of the conditional decision.`

5. SOURCE_LICENSES cells contradict the shipped code. These are live cells, so correct them in place.
(a) 6.1, 6.2 and 6.3 say "Ingested by: **pending**". Replace with `scripts/ingest_avid.py` to `ingest/wave12_avid.json`, `scripts/ingest_cvelistv5.py` to `ingest/wave12_cvelistv5.json`, and `scripts/ingest_arxiv_oaipmh.py` to `ingest/wave12_arxiv.json` respectively.
(b) 6.1 and 6.2 Scrape-permitted say "(pending entry 3)". Replace with "not used: HTTP tarball / release asset through ingest/common.py; INGESTION_CONDUCT.md entry 3 records the decision".
(c) 6.2 Action says "Filter by allowlist (WS4-T4), not by keyword alone". The WS4-T4 allowlist does not exist (`ai_relevance.py` says so), and 384 of the 2,240 rows were admitted on a description keyword alone (`match_evidence` product=None). Either the code adds the INCLUSION.md section 6 second signal for description-only matches, or license-auditor rewrites the cell to describe the real filter (inherited vocabulary plus the 78-entry `ECOSYSTEM_SEED` plus word-bounded description tokens).
(d) 6.3 says selection is "deterministic ... plus a committed human-approved list". No such list exists, and the rows say "not by human review". Either add the list or amend the row. This changes the approved D40 design, so route it to the user.
(e) Row 2.4 says "excluded from ingest by a pipeline filter (being implemented ... on the ingest branch)" and "no MAL content is kept". Replace that sentence with: `**Handling: MAL- records are excluded from the OSV path by scripts/ingest_cve_nvd_expanded.py::is_openssf_malicious (id/alias prefix MAL- or an ossf/malicious-packages source marker). The two committed MAL rows were purged by scripts/audit/purge_openssf_mal.py: MAL-2026-2144 dropped; MAL-2026-3607 kept as a bare identifier only (id, OSV template title, affected package, tags, reference links; description replaced by an original sentence) because it holds INC-08450 together (board N7). No OpenSSF report text is kept, so no Apache-2.0 notice is added.**`

6. Mechanically identifiable out-of-scope entries are about to get permanent IDs. Your precision bar is met (see above). This is a defect anyway, for two reasons. It violates INCLUSION.md section 1 gate 1 ("incidental mention is not an AI-nexus") and row 6.2's "not by keyword alone". And IDs are append-only, so each of these becomes a permanent tombstone after release, while removing it before the merge costs nothing. All are description-only matches. Definite FPs found:
- Linux kernel CNA: CVE-2022-49590 matched "llm" in `sysctl_igmp_llm_reports`; CVE-2026-53378 matched a "Claude Sonnet" patch trailer; CVE-2026-74630 matched "OpenAI" in a discovery credit; CVE-2026-89519 matched "autogen"; CVE-2026-97620 matched "Llama.cpp" in passing.
- MitraStar GPT-xxxx routers, matched by the `gpt-\d\w*` regex: CVE-2024-9977, CVE-2025-50753, CVE-2026-52483, CVE-2026-52484.
- Others: Quotes Llama (CVE-2026-12512), Snowflake JDBC (CVE-2025-27496, marketing phrase), LifterLMS (CVE-2024-12596, "llms"), weDocs (CVE-2025-13921, CVE-2026-12729, CVE-2026-12731, CVE-2026-12734), Support Genix (CVE-2026-19806), Trigger.dev (CVE-2026-73655, CVE-2026-73657). In these, "AI Chatbot" or "AI agents" appears only in the product's self-description and the bug has nothing to do with AI.
FIX (deterministic, each with a test):
(i) Replace `gpt-\d\w*` in `_EXTRA_DESC_RE` with a bounded model form, for example `gpt-\d(?:\.\d+)?(?:o|-turbo|-mini|-oss)?`.
(ii) Reject description-only matches on Linux-kernel-CNA records (assignerShortName Linux).
(iii) Strip credit and trailer clauses ("found/reported/triaged/discovered by ...", "Assisted-by:") before the description match.
(iv) Add an explicit, commented exclusion list in `ai_relevance.py` for the remaining named product-name-only cases, or implement the section 6 second signal for description-only rows.
I tried making `_` a word character: it drops sysctl_igmp_llm_reports but also ruby_llm, a true positive. Report the recall cost of each rule.
Then rebuild, re-delta and re-sample the description-only stratum.

7. NOTICE-DATA misstates MITRE's trademark line. NOTICE-DATA says "CVE and the CVE logo are registered trademarks of The MITRE Corporation." cve.org's own source (CVEProject/cve-website `src/components/FooterModule.vue`, curl 2026-10-03, line 134) reads: "CVE is a trademark and the CVE logo is a registered trademark of The MITRE Corporation." Replace with exactly that sentence. The copyright line `Copyright © 1999-2026, The MITRE Corporation.` is correct: it matches line 128 `Copyright © 1999-{{currentYear}}`.

Routing: 1, 2, 4, 6 and the code half of 5(c) go to pipeline-engineer. 5(a), 5(b), 5(e) and 7 go to license-auditor. 3 and 5(d) go to the user if the fix is anything other than "make the code match the row".


## Part 2: evidence and advisories

wave12 gate, part 2: evidence and advisories (the verdict is BOUNCE, sent in part 1).

PRECISION: my own seeded samples, judged against INCLUSION.md sections 1, 2, 3 and 6
- cvelistV5-only, general sample, n=80 (random.Random(20261003)): 0 clear FPs (95% Wilson CI for precision 95.4-100). 5 borderline: Moodle's AI image-generation capability check, n8n x3, and Hatchet ("orchestrating ... AI agents"). Counting borderline as misses: 75/80 = 93.8% (CI 86.2-97.3). n8n is consistent with corpus practice: n8n-io is in the inherited vocabulary and the base corpus has 102 n8n entries.
- Stratified, using the author's own `match_evidence`: 1,856 rows matched on a product field and 384 on a description token only.
  - Product stratum (66 of my 80): 0 clear FPs, 3 borderline (all n8n).
  - Description-only stratum, n=40 (seed 7): 29 TP, 5 borderline (Kibana ML x2, Discourse AI, Moodle AI, a .claude skill script), 6 clear FPs. That is 85% excluding borderline (CI 70.9-92.9) and 72.5% strict (CI 57.2-83.9).
- Weighted over all 2,240: about 97.4% excluding borderline (about 58 FP entries); about 91.5% strict (about 190).
- FP patterns: AI words in discovery credits or patch trailers (Linux kernel); `gpt-` plus digits in router model numbers; tokens inside identifiers (`_llm_`, LifterLMS); "AI Chatbot" or "AI-powered" in WordPress product names while the bug is generic; vendor marketing self-descriptions (Snowflake "a platform for using artificial intelligence", Trigger.dev "for building AI agents"). No ML-library non-security bugs were seen; CVE status already gates that.
- AVID-only, n=20: 20/20 TP (1 borderline: Chain Sea "ai chatbot system", 2021).
- arXiv, n=15: 15/15 TP (attack demonstrations on GenAI systems).
- Baseline, a different route: existing pre-PR CVE/GHSA-only, non-curated vulnerability entries, n=40 (seed 99, pool 5,725). About 21 of 40 have no AI nexus: Apache FOP, Liferay x2, Magento, Jenkins x2, Jetty, .NET, Nuxt, Umbraco, Kimai, Fleet, kube-router, Mailpit, i18next, browsershot, publify, Artifact Hub, scratch-svg-renderer and others. That is about 48% precision (CI about 33-63). The new ingest is far ABOVE the corpus standard.
- The 78-entry seed lives in `scripts/ai_relevance.py` (`ECOSYSTEM_SEED`), not under `data/`, so it is not a hand-edit of `data/*.json`. It is acceptable as an interim stand-in for WS4-T4. I did not re-verify the author's claim that each entry was "measured as a miss".

WHY THE YIELD DEVIATES FROM THE ESTIMATE (your premise needed refining)
- The 1,521 post-June rows are mostly the corpus's stalled NVD refresh, not coverage unique to cvelistV5. CVE entries by month in the base corpus: 2026-03 443, 2026-04 429, 2026-05 553, 2026-06 504, 2026-07 15, 2026-08 0, 2026-09 0. The new rows fill 2026-07 to 2026-09 at 453, 469 and 554, which is the corpus's established run rate. The evaluation's ~165/yr was cvelistV5's marginal yield over an up-to-date NVD path.
- Backlog 927 against the "at least 416" figure: that figure was explicitly a lower bound from 26 EUVD queries plus the huntr slice, and the new rows are spread at about 10-86 per month.
- AVID 208 against about 1,070: 556 garak scan results are excluded under INCLUSION section 3, and 519 CVEs are already in the corpus.
- Any release note must not present the 1,521 as new-source coverage.

DELTA, re-derived from git blobs with my own per-ID, per-field script (not `wave12_delta.py`)
- 9604752f to d49d9647: 13,361 to 15,872. Missing 0, new 2,511 (INC-14911..INC-17421, contiguous). Existing entries changed: 0, comparing every field including added and updated. Top-level fields that moved: `generated` and `incident_count` only.
- Fire test: appending " x" to INC-00001's title was caught ("CHANGED INC-00001 ['title']").
- 48065e66 to d49d9647: the corpus DID change. 63 new arXiv entries changed in description, `description_provenance`, `description_source`, and in some cases attack_vector, mitre_atlas, owasp_llm and nist_ai_rmf. 0 existing entries changed.
- The delta md was edited in 690e39a1 (it now mentions the MAL step); the JSON twin was not edited. I checked the twin's aggregates against d49d9647 and they are correct.
- So the delta is not stale on its claims. Small leftovers: the md header still says "code commit 48065e66 (the data commit follows it)"; the "rebuilt twice, byte-identical" claim in section 3 was measured at 48065e66; and the JSON `meta` is an empty `{}`. A dated note would fix all three.

INVARIANTS AND REPRODUCIBILITY (throwaway clone in the scratchpad; the repo tree was never touched)
- Build steps (no `make` on this shell, so I ran `parse_existing`, `merge_and_dedupe`, `render_markdown`, `render_docs_stats` and `validate` directly): exit 0, "15872/15872 entries valid", porcelain empty. sha256 of `incidents.json` is 944cc9ff..., of min.json d28f042e..., of stats.json df9ac363...; all byte-identical to the committed files. A second merge run gave the same hashes (deterministic).
- Base snapshot plus base ingest inputs (wave12 files removed, base `cve_nvd_expanded.json`): output byte-identical to 9604752f (f1698f7d...).
- Base snapshot plus the d49d9647 inputs: output byte-identical to the committed d49d9647 corpus and min.json. So the corpus is build output, not hand-edited, and `ingest/wave12_*.json` plus the build reproduce it.
- `check_stats_drift`: "clean: 5 doc surfaces match". Invariant 1: README and index show only `incident_count`; no combined headline was added.
- `id_deprecations.json` untouched. `merge_and_dedupe.py` and `parse_existing.py` unchanged, and no model calls are on the build path.
- Egress grep of the three ingest scripts plus `ai_relevance`, `corpus_overlap` and the audit scripts for requests, urllib, httpx, subprocess, socket and git clone: no egress. The only hits are docstrings, plus `wave12_delta.py`'s local `git show`. `url_with_query` keeps urlencode inside common.py.
- `fetch_to_file`: fail-closed robots check, `_rate_limit` per host, forced USER_AGENT, and a .part file renamed only on success.
- Tests: `python -m pytest -q` gave 524 passed, 1 xfailed.
- Mutation checks:
  - Disabled the robots check in `fetch_to_file`: `test_fetch_to_file_honours_robots_refusal` FAILED.
  - Disabled the `state != "PUBLISHED"` guard: `test_cvelistv5_build_never_emits_rejected_even_when_it_would_match` and `test_cvelistv5_real_rejected_huntr_record_is_not_emitted` FAILED.
  - After restoring both, 76 passed.

LICENSING CHECKS
- arXiv: I fetched 3 abstracts through oaipmh (2510.10281, 2606.06244, 2608.04741). The longest common substring with our descriptions is 22, 15 and 17 characters ("Large Language Models", "commercial LLMs", "end-to-end attack"). No abstract is reproduced, and the provenance file stores none.
- AVID: "Reason for inclusion" appears 0 times in data/, ingest/, docs/incidents and src. NOTICE-DATA's MIT text matches the raw avid-db LICENSE exactly after whitespace normalisation (I fetched it with curl, 200, 1,110 bytes); this closes the "diff it against the raw LICENSE" check that row 6.1 asks of red-reviewer.
- CVE ToU: verbatim CNA text is allowed under the grant (reproduce and sublicense, provided the designation and licence travel). NOTICE-DATA and dep5 carry both, and the copyright line is correct. The trademark line is wrong (defect 7).
- `git grep "Per source details"`: the only hit is `tests/test_ingest_wave12.py` (a negative assertion).
- MAL-2026-3607 as a bare identifier (the OSV template title "Malicious code in guardrails-ai (PyPI)" plus id, links and package) is acceptable: these are facts, not Apache prose.

ADVISORIES
A1. The MAL-2026-3607 keep is not durable. `BARE_IDENTIFIER` exists only in the one-off purge script. The next `ingest_cve_nvd_expanded.py` run (the manual cve-enrich workflow) regenerates the file and drops the row. I reproduced this in the clone: the build exits 1 with "[split-guard] ABORT: this build would silently split 1 previously-single PUBLISHED id(s)". It fails closed, so it is safe, but it is a trap. Either carry the bare row in the NVD writer or resolve N7.
A2. quality_tier: 2,226 cvelistV5 rows become "reviewed" under the rule that a CVSS-scored CVE counts as NVD analyst review, but cvelistV5 CVSS comes from the CNA or ADP. The 63 arXiv rows are "reviewed" via the ARXIV- prefix while their own text says "not by human review". The "reviewed" count goes from 11,131 to 13,627 (tier/landmark unaffected). Needs a decision; proposed task.
A3. Proposed task: a scope audit of the existing CVE/GHSA feed (the 48% baseline above; related to #88). This is a bigger precision problem than anything in this PR.
A4. `fetch_to_file` and `fetch_once` robots-check and pace only the first host. urlopen follows the GitHub 302 to the asset CDN host unchecked.
A5. INCLUSION.md section 4 cites `scripts/precision_sample.py`, which does not exist.
A6. Some AVID titles carry a concatenated "NSFW" prefix (INC-15009 "NSFWOpenAI DALL-E3 ...", INC-15011 "NSFWOpenAI Sora ...").
A7. Scope: the `ingest_cve_nvd_expanded.py` edit is only the MAL filter. `tests/test_landmark_distribution.py` +3 registers the new corpus-reading producers, which that guard requires, so it is justified. Makefile targets, ingest/README and the outreach README row are in scope. No unexplained changes.

STATE AND STRAYS
- Target worktree: `git symbolic-ref -q HEAD` = refs/heads/ws4/wave12-ingest, porcelain empty. Main tree: refs/heads/main, porcelain empty. Porcelain attests only to the working trees.
- My scratch files are all outside the repo: the clone, before/mid/after JSON and the oai_*.xml files under the session scratchpad, plus `lic.txt` in the session temp directory.
