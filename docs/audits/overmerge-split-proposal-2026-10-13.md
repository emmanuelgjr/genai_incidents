# Over-merge split proposal: INC-00924, INC-02646, INC-03233 (2026-10-13)

> **Dated record, do-not-regenerate.** This is a PROPOSAL written for user ruling
> D110 on 2026-10-13, measured at `origin/main` `2c1be0b8` (data identical to
> `2e9ba445`; no `ingest/`, `data/` or `scripts/` change between the two). It makes
> NO data change and changes no code. The figures below describe that commit. When
> a ruling is made, supersede with a dated update; do not edit the measurements.
>
> Author: corpus-surgeon (WS1), branch `ws1/overmerge-proposal-2026-10-13`.
> All scratch rebuilds ran in copies of `git archive HEAD` OUTSIDE the worktree
> (the probe patches in section 7 are reproduced there, not committed).

## 0. Summary

| Question | Answer |
|---|---|
| Which rule merges them? | The reference-URL key in `dedupe_entries` (`scripts/merge_and_dedupe.py`, URL branch, `merge_into(url_hit, e)` at line 1857). 17 of the 20 OWASP-involving merges go through it, 2 more through the same URL key's transitive claim (line 1801), 1 through a legitimate CVE key (line 1833). |
| Why does the CVE guard not stop it? | `cve_disjoint` (lines 478-490) returns False unless BOTH sides carry CVE ids. The 18 `OWASP-GENAI-*` ingest rows carry `cve_ids` = [] (even where the title names a CVE), so the guard is vacuous. |
| Proof | Dropping the three round-up URLs as dedupe keys (3 URLs, nothing else) in a scratch copy raises survivors by exactly 15 (15,657 -> 15,672 with the committed ID history; 17,338 -> 17,353 from a fresh state), and the build's own split guard names exactly INC-00924, INC-02646, INC-03233 as the only published IDs that would split. |
| Same rule elsewhere? | Yes. 55 published rows are held together by a URL that bridges 3 or more otherwise-unconnected source groups while at most one group carries a CVE (the OWASP shape). 52 of them are not our three. By my reading of titles, 14 of the 52 are the same shape (one publisher report or roll-up page over distinct findings); 13 of those 14 carry no OECD/AIID id. A second class of 203 rows is the older CVE-disjoint residue that survives only by the grandfather clause. |
| The 18 folded ids | 3 are the surviving incident itself (or its legitimate duplicate); 15 are distinct incidents with no row of their own. 5 of those 15 very probably describe an incident that already has a row under other ids; 10 have none. |
| Recommendation | Do A (rule fix with a grandfather clause) now. Do B (split) later, as its own release, after two blockers are cleared (verbatim round-up text in 6 ingest rows, and an invalid `2026-Q1` date in 3). In B, retire INC-02646 with a `split` tombstone rather than keeping its number. Do not choose C unless the user wants the limitation documented and nothing else. |

## 1. Root cause, with code citations

All line numbers are `scripts/merge_and_dedupe.py` at `2c1be0b8`.

**The input.** `ingest/avid_owasp_incidents.json` holds 18 rows with `source_id`
`OWASP-GENAI-Q1-2025-01..03`, `Q2-2025-01..09`, `Q1-2026-01..06`. Every row's
`references[0]` is the quarter's round-up page (three distinct URLs). None has
`cve_ids`.

**The rule.** `dedupe_entries` (line 1728) keys entries by CVE, then source_id, then
reference URL, then fuzzy title. Reference URLs go through `normalize_url` (line 429),
which strips scheme, `www.`, fragment and trailing slash, keeps the path and any
non-tracking query, and so keys a round-up page the same for every row that cites it.
The URL branch (lines 1845-1858):

- for each reference of the incoming entry, `by_url` is consulted;
- a hit is refused only if `cve_disjoint(candidate, e)` is true and the pair is not
  `_same_prior` (the grandfather clause);
- otherwise `merge_into(url_hit, e)` (line 1857).

`cve_disjoint` (line 478) is `bool(ca) and bool(cb) and not (ca & cb)`. With an empty
CVE set on either side it is False, so the refusal never fires. The transitive claim in
`_reindex._claim` (lines 1786-1806) uses the same guard with the same result, which is
how two more rows fall in (merge at line 1801).

**The trace (a different method from the one that built the corpus).** A harness
(outside the tree) re-ran steps 1-3 of `main()`, wrapped `merge_into`, and recorded the
caller's line number, the dedupe key, and both sides' `source_ids`/`cve_ids` for every
merge that touched an `OWASP-GENAI-*` id. With the committed ID history and from a
fresh state (no history), the result is identical:

| Branch (line) | Merges involving an OWASP id | What it merged |
|---|---:|---|
| URL key, `merge_into(url_hit, e)` (1857) | 17 | 16 OWASP rows into a sibling's or the EchoLeak group, plus the CVE-2025-23254 CVE row into INC-02646's group via the NVD URL |
| URL key, transitive `_claim` (1801) | 2 | legacy `EXT-2025-DEEPSEEK-DB`/`INC-032` (via thehackernews.com) and `EXT-2025-ECHOLEAK` (via arxiv.org/abs/2509.10540) absorbed into the OWASP-led group |
| CVE key (1833) | 1 | CVE-2025-32711 row into the EchoLeak group (legitimate) |
| source_id key, title key | 0 | |

(By quarter: Q1-2025 has 2 URL merges; Q2-2025 has 8, the 9th id being the group's
first row, plus the CVE-2025-23254 CVE row; Q1-2026 has 6, of which Q1-2026-01 joins the
EchoLeak group, which is correct. The 16 OWASP URL merges are therefore 15 wrong plus 1
right; the rule cannot tell them apart.)

**The counterfactual (causal proof).** In a scratch copy, the three
`genai.owasp.org/<date>/...round-up...` URLs were excluded as dedupe keys at the three
`normalize_url` call sites inside `dedupe_entries` only (the references stay on the
rows). Result:

| Build | Survivors | OWASP-involving merges |
|---|---:|---|
| Current rule, committed ID history | 15,657 | 20 |
| Current rule, fresh state | 17,338 | 20 |
| Round-up URLs excluded, committed ID history | 15,672 | 5 |
| Round-up URLs excluded, fresh state | 17,353 | 5 |

20 - 5 = 15 = the survivor delta in both states. The 5 merges that remain are the
legitimate ones (EchoLeak, DeepSeek legacy pair, the CVE row via NVD). In the fresh
state the maximum number of OWASP ids in one survivor falls from 9 to 1 (18 survivors
carry OWASP ids instead of 3).

**Why it stayed hidden.** Before this finding the only checks were the CVE guard
(vacuous here) and the D28 list, whose scope was CMS-article URLs. The three round-up
URLs were not on it.

## 2. Is the same rule over-merging elsewhere?

Yes, with two distinct classes. Method: for each of the 2,616 published rows built from
2 or more input records, group the records by links that are NOT a bare URL (shared
CVE, shared source_id, equal normalized title). Any row whose groups are joined only by
shared reference URLs, with one URL bridging 3 or more groups, is a candidate (258
rows). The input records come from the same loader `main()` uses. The falsifier: a
corpus with no URL-only bridges returns 0; the three target rows return exactly their
known group counts (INC-00924: 10 groups, k=6; INC-02646: 12 groups, k=9; INC-03233: 3
groups, k=3), which they do.

| Class | Definition | Rows | In fresh-state build |
|---|---|---:|---|
| A. CVE-disjoint residue | 2 or more groups carry CVEs (disjoint by construction). Today's `cve_disjoint` guard WOULD refuse this merge; the row exists only because of the grandfather clause (`_same_prior`) | 203 | all 203 split |
| B. Guard-vacuous (the OWASP shape) | at most 1 group carries a CVE, so the guard cannot fire | 55 | 54 stay merged (the 55th, INC-14128, splits into 4) |

Class B, excluding the three targets: 52 rows. Of those, 13 carry OECD/AIID ids (frozen
rows). Two are the garak and promptfoo scanner-probe rows (INC-03798 41 probes,
INC-04106 174 probes) which WS1's corpus split routes to capabilities anyway. Reading the
group titles, I judge these 14 to be the same shape as the OWASP round-ups: one publisher
report or roll-up page over distinct findings (judgment, not an audited classification):

| Row | Bridging URL (host and path) | Groups |
|---|---|---:|
| INC-03006 | openai.com, disrupting-malicious-uses-of-ai-october-2025 | 8 |
| INC-03002 | openai.com, disrupting-malicious-uses-of-ai-june-2025 | 8 |
| INC-02999 | cdn.openai.com threat-intelligence report (Feb 2025) | 5 |
| INC-04068 | cdn.openai.com influence-and-cyber-operations (Oct 2024) | 4 |
| INC-04218 | openai.com, disrupting-deceptive-uses-of-ai-by-covert-influence | 4 |
| INC-02320 | anthropic.com, detecting-and-countering-malicious-uses (Mar 2025) | 4 |
| INC-02680 | cloud.google.com GTIG adversarial-misuse report | 4 |
| INC-02637 | cloud.google.com GTIG threat-actor-usage-of-ai | 6 |
| INC-04066 | microsoft.com security blog, staying-ahead-of-threat-actors | 5 |
| INC-02434 | embracethered.com, wrapping-up-month-of-ai-bugs | 6 |
| INC-03303 | blog.trailofbits.com, categories/machine-learning | 3 |
| INC-03920 | jfrog.com, top-research-discoveries-of-2024 | 3 |
| INC-15048 | mindgard.ai, bypassing-azure-ai-content-safety-guardrails | 6 |
| INC-08177 (OECD/AIID-carrying, frozen) | anthropic.com, detecting-countering-misuse-aug-2025 | 10 |

The remaining class-B rows are mixed: some are distinct GHSA advisories sharing one
commit or release URL (OpenClaw, picklescan, Zend), some are the same incident under
2-3 retitled reports (Sleeper Agents INC-03572, GeminiJack INC-01064, Slack AI
INC-04208, which are legitimate), and 13 are OECD/AIID rows. I did not judge them one by
one; the point for the user is that the OWASP fix does not close the class. Only a
general rule would, and that is a separate, larger decision (section 6, item 6).

Context, not caused by this rule: a fresh-state build would split 598 published rows
into 2,279 survivors (1,681 extra rows) because of grandfathered merges of both classes.
That is the unfinished remainder of WS4-T10/D28 and is out of scope here; it is quoted so
the user can see the three rows are 15 of a much larger set.

## 3. Composition: what each folded id describes

Source: `ingest/avid_owasp_incidents.json` plus a title/CVE keyword search over
`data/incidents.json` (excluding the three rows) for existing rows. "Existing row"
confidence is my reading of titles and descriptions: **high** = same incident named in
both; **probable** = same event, but the OWASP text does not name the vendor or the
link rests on date and theme. None of it is audited; the label-scientist or the user
should confirm before any re-attribution.

### INC-00924 (EchoLeak). Survivor keeps 5 non-OWASP ids; 6 OWASP ids folded.

| Folded id | Incident | Same as survivor? | Row elsewhere? |
|---|---|---|---|
| Q1-2026-01 | EchoLeak, CVE-2025-32711 | **Yes** (legitimate duplicate report) | n/a, stays |
| Q1-2026-02 | Copilot Studio indirect prompt injection, CVE-2026-21520 (Capsule Security, patched 2026-01-15) | No | **High: INC-01434** (CVE-2026-21520, "ShareLeak"; carries OECD-AIM-2026-04-15-d934, so a frozen row). Not linked today because the OWASP row has no `cve_ids` |
| Q1-2026-03 | "Reprompt" single-click exfiltration, Copilot Personal (Varonis, Jan 2026) | No | None found |
| Q1-2026-04 | Multi-agency compromise using Claude/ChatGPT, ~150 GB | No | **High: INC-00806** (legacy, 10 agencies, 150GB), also INC-02682 (AIAAIC), INC-02325 (AIID/OECD), INC-01264 (RES): four rows already, a pre-existing duplicate set |
| Q1-2026-05 | "ASI08" single agentic response causing an access-control incident, no CVE | No | **Probable: Meta internal agent Sev-1** (INC-01411 legacy; INC-01408 AIID/OECD; INC-01395 OECD; INC-01396 AIAAIC). The OWASP text names no vendor; the Meta reading is the board finding A3 |
| Q1-2026-06 | "ASI09" developers targeted via leaked agent tooling | No | **Probable: Claude Code source leak exploited for malware** (INC-00814 OECD, INC-00604 OECD). Text names no vendor |

### INC-02646 ("GPT-4.1 jailbreak via tool poisoning"). Survivor keeps 3 non-OWASP ids; 9 OWASP ids folded.

| Folded id | Incident | Same as survivor? | Row elsewhere? |
|---|---|---|---|
| Q2-2025-01 | GPT-4.1 tool poisoning (April 2025) | **Yes**: this IS the survivor's title/description/date | Related, probably not identical: INC-02874 (Invariant Labs MCP tool poisoning, 2025-04-01). Low confidence |
| Q2-2025-02 | Deepfake voice scam bypassing bank voice authentication, ~$25M | No | None. Arup HK (INC-03588, INC-03484) is a video-call CFO fraud, different |
| Q2-2025-03 | Prompt injection in ChatGPT-based assistants leaks data | No | None (generic) |
| Q2-2025-04 | DeepSeek ClickHouse database exposure and data transfer | No | **High: INC-02499** (AIAAIC1891, same DeepSeek exposure). The legacy `EXT-2025-DEEPSEEK-DB`/`INC-032` records of the same incident are ALSO inside INC-02646 |
| Q2-2025-05 | Sony Music AI deepfake takedowns | No | None |
| Q2-2025-06 | NVIDIA TensorRT-LLM Python-executor RCE, CVE-2025-23254 | No | None. The CVE row itself was folded into INC-02646 (key `CVE-2025-23254` is a source id of INC-02646). The 12 other TensorRT-LLM CVEs each have their own row |
| Q2-2025-07 | CAIN targeted prompt-hijacking attack | No | None |
| Q2-2025-08 | ViKing AI vishing kits | No | None (INC-08819 "OpenViking" is an unrelated product) |
| Q2-2025-09 | Surge in AI-assisted credential stuffing and scanning | No (a trend, category threat-report) | None (INC-02322 is an Anthropic influence-ops report, different) |

### INC-03233 ("Storm-2139 Azure OpenAI account hijack"). 3 OWASP ids, no other source.

| Folded id | Incident | Same as survivor? | Row elsewhere? |
|---|---|---|---|
| Q1-2025-01 | Storm-2139 account hijack and jailbreak resale | **Yes** (this is the survivor) | **High: INC-02902** (Microsoft DCU, same operation, no OECD/AIID id); also INC-03812 (AIID/OECD, same network). So the survivor itself duplicates an existing row |
| Q1-2025-02 | GitHub Copilot "Affirmation" jailbreak (Apex Security) | No | None |
| Q1-2025-03 | Chain-of-thought jailbreak across chatbots | No | None |

**Totals (each from the table above, countable by eye):** 18 ids = 3 same-as-survivor +
15 distinct. Of the 15: 5 very probably have an existing row (Q1-2026-02, -04, -05, -06,
and Q2-2025-04; 3 high, 2 probable) and 10 have none (Q1-2025-02, -03; Q2-2025-02, -03,
-05, -06, -07, -08, -09; Q1-2026-03). Plus one pre-existing duplicate in the survivors
(INC-03233 vs INC-02902).

**What the over-merge has already done to the three rows** (fields of INC-02646 that
come from a different incident than its title): `cve_ids` CVE-2025-23254 and its CVSS
vector, CWE-502 and CAPEC-586 (TensorRT-LLM, not GPT-4.1); `tags` has 35 values (DeepSeek,
voice-cloning, clickhouse, vishing, music, ...); `source_count` 12, hence `confidence`
high; 5 of 7 `owasp_llm`, 7 of 12 `mitre_atlas` codes come from other incidents.
INC-00924's `date` is 2026-01-15 (the Copilot Studio patch date) although EchoLeak's own
record is 2025-05/06; its `year` is 2026 for the same reason.

## 4. The three options, with field-level deltas

All deltas below were produced by actually building in scratch copies and diffing
`data/incidents.json` and `data/id_deprecations.json` before/after. New IDs are minted
by the build from its counter (next free number INC-17216 at this commit); the exact
numbers depend on what else builds first (PR #102's +5 AIAAIC rows, if merged first,
would shift them by 5). The user does not choose numbers; see decision 3.

### 4A. Fix the dedupe rule only

There are two ways to write the rule and they behave very differently.

**A1: aggregate round-up URLs are never keys (no grandfather clause).**
Tested: the next `make build` ABORTS before writing anything:

```
[split-guard] ABORT: this build would silently split 3 previously-single PUBLISHED id(s)
  - INC-00924 -> ['INC-00924', 'INC-17226', ... 'INC-17230']  (6 rows)
  - INC-02646 -> ['INC-02646', 'INC-17218', ... ]              (9 rows)
  - INC-03233 -> ['INC-03233', 'INC-17216', 'INC-17217']       (3 rows)
```

That is `_check_split_authorization` (line 2334) working as designed, called at line 2978
before any write. The files on disk were unchanged after the aborted run (cmp-verified).
So "fix the rule only" in this form is a split by another name and needs the D28-style
authorization of option B. A1 is not a viable option A.

**A2: aggregate URLs are not keys unless both sides already share a published row**
(the same grandfather device `cve_disjoint` already uses, `_same_prior`, line 1748).
Tested in a scratch copy (patch in section 7):

| Check | Result |
|---|---|
| `data/incidents.json` after build | byte-identical to the published file |
| `data/id_deprecations.json` | byte-identical |
| `data/stats.json` | not regenerated by merge; byte-identical when rendered (gate re-derivation, gate-overmerge 2026-10-13) |
| Fresh-state build (no history) | OWASP ids spread over 18 survivors, max 1 per survivor (A2 prevents NEW folding) |
| `pytest -k "dedup or overmerge or split or disjoint"` in the scratch copy | 167 passed |

Delta on next build: **0 rows, 0 fields, 0 new IDs, 0 deprecation records.**
Counts and CORRECTIONS: none are changed by the build, so no CORRECTIONS row is owed;
what is owed is the honest statement that the three rows remain over-merged (see C's
documentation obligation, which A inherits). The rule needs a regex (or a fan-out
threshold) that defines "aggregate URL"; the probe used the OWASP round-up path shape
only, so it does not touch the 14 other candidates in section 2. A2 would also not catch
a future OWASP aggregate whose slug lacks "round-up", nor other publishers' aggregate
pages (those 14 candidates). If A2 is ruled, the WS4 task should add a regression test.

IDs are append-only and tombstones permanent (`docs/ID_POLICY.md` section 4 rules 1-3):
A2 touches neither, which is its main virtue.

### 4B. Fix the rule AND split through an authorized split

Mechanism (verified in the code): `_check_split_authorization` passes only if every
split old id is in the list at `SPLIT_AUTHORIZATION_PATH`
(`docs/audits/WS4-T19-authorized-splits-2026-09-18.json`) AND the list carries an
`authorization.decision` equal to `REQUIRED_SPLIT_AUTHORIZATION_DECISION` (hardcoded
"D28", line 1156) AND the list's `entries` hash equals
`REQUIRED_SPLIT_AUTHORIZATION_ENTRIES_SHA256` (hardcoded, line 1171).
`_verify_split_authorization_marker` (line 1907) enforces all three, fail-closed.
**The machinery is single-list, single-decision and pinned to the D28 hash.** Adding the
three ids to that list changes its hash, so a split needs either a re-ruling that
re-pins the constant (the code comment says exactly this) or a code change to accept a
second dated list. Either is a pipeline task (WS4) and a new dated board decision; the
D28 file is an immutable record and must not be edited in place (agreement 4). In my
scratch builds I appended the three entries and re-pinned the constant in the SCRATCH
copy only, to measure the outcome.

Two variants for INC-02646, because the build gives the old ID to "the first survivor in
build order" (step 6, `chosen = ids_seen[0]`), and the first survivor of INC-02646's keys
is the legacy DeepSeek record, not the GPT-4.1 one:

| | B-keep: all three `keep_id` | B-retire: INC-02646 `retire`, other two `keep_id` |
|---|---|---|
| Live rows | 15,666 -> 15,681 (+15) | 15,666 -> 15,681 (+15) |
| `incident_count` (non-retracted) | 15,637 -> 15,652 | 15,637 -> 15,652 |
| New IDs minted | 15 (INC-17216..17230) | 16 (INC-17216..17231) |
| INC-02646 afterwards | LIVE, but retitled "DeepSeek AI database exposure" (continuity BROKEN: the number changes meaning) | not live; tombstone `reason: split`, `into` a list of 9 successors |
| New deprecation records | 0 | 1 (INC-02646) |
| Existing rows with changed fields | 3 | 2 (INC-00924, INC-03233) |
| ID set removed from live | none | INC-02646 |

Existing-row field deltas (B-keep; B-retire has the INC-00924 and INC-03233 rows only):

| Row | Fields changed (count) | Notable |
|---|---|---|
| INC-00924 | 10: source_ids 11->6, source_count 11->6, tags 26->13, date, year, mitre_atlas 17->15, mitre_atlas_tactics 10->9, owasp_asi 7->6, updated, last_seen | date 2026-01-15 -> 2025-05, year 2026 -> 2025 (EchoLeak's own date) |
| INC-02646 (B-keep only) | 20: title, description, affected, category, date, attack_vector, cve_ids, cvss_vector, cwe_ids, capec_ids, references 5->3, maestro_layers, source_ids 12->3, source_count 12->3, tags 35->12, mitre_atlas 12->5, mitre_atlas_tactics 10->5, nist_ai_rmf 11->7, owasp_asi 5->1, owasp_llm 7->2 | the row becomes a different incident |
| INC-03233 | 7: source_ids 3->1, source_count 3->1, tags 8->4, date 2025-01-31 -> 2025-01, mitre_atlas 5->4, nist_ai_rmf 5->4, owasp_llm 3->2 | |

Per-field counts across the three rows (B-keep): source_ids 3, source_count 3, tags 3, date
3, mitre_atlas 3, mitre_atlas_tactics 2, owasp_asi 2, owasp_llm 2, nist_ai_rmf 2,
updated 1, last_seen 1, year 1, and one each of title, description, affected, category,
attack_vector, cve_ids, cvss_vector, cwe_ids, capec_ids, references, maestro_layers.
(`updated`/`last_seen` change only on INC-00924 because the other two were already
stamped by today's build; the count depends on the build day.)

New rows (15): all `corpus: security`, one source id each except two: INC-17222
(`CVE-2025-23254` + `OWASP-GENAI-Q2-2025-06`) and the DeepSeek row (`EXT-2025-DEEPSEEK-DB`,
`INC-032`, `OWASP-GENAI-Q2-2025-04`), which exists as its own row for the first time.
Titles are the OWASP headings (D111 keeps headline titles).

Re-attribution instead of a new row: the pipeline has no source-id alias mechanism, and
a row is only joined to another by a shared CVE/source_id/URL/title key. For the five
probable-existing cases, re-attribution means giving the OWASP row a key that matches the
existing row. Only one has a clean structured key: Q1-2026-02 should join INC-01434 by the CVE key if
the ingest row carried `cve_ids: ["CVE-2026-21520"]` (the build's CVE branch is the
strongest key; I did not test this edit). But INC-01434 carries an OECD id, so
that would edit a frozen row. The others (INC-00806, INC-01411, INC-02499, INC-02902) are
non-OECD legacy/AIAAIC/VTR rows with no shared key, so a key would have to be invented
(a reference URL), which is a curation judgment. Without re-attribution each of these 5
becomes a new row that duplicates an existing one; the corpus already holds 4 rows for the
150 GB incident, so this adds to a known problem rather than creating one.

Validation (scratch): `validate.py` reports 15,678 of 15,681 valid. The 3 failures are
Q1-2026-04, -05, -06, whose ingest `date` is `2026-Q1`, which the schema pattern rejects.
They were hidden before because the survivor's date won the merge. Fix required before
B: change those three dates in `ingest/avid_owasp_incidents.json` (a data-value call: the
source says only "Q1 2026"; `2026` satisfies the pattern without inventing a month).

Licensing blocker: the board's own measurement (`docs/audits/licensing-overlap-measurements-2026-10-13.md`,
Q2; ad38c61e) measured 8 ingest rows with verbatim or near-verbatim CC BY-SA round-up
text (4 verbatim, 4 near); 2 were since rewritten at the ingest layer under D97
(b130900e: Q1-2025-01 and Q2-2025-01), leaving 6 (verbatim: Q1-2025-03, Q2-2025-02,
Q1-2026-04; near: Q1-2025-02, Q1-2026-05, Q1-2026-06). Today they do not ship as rows. A split would publish them. D97 rewrote only
the two surviving descriptions. I did not re-measure; this is inherited testimony [A].
B must wait for those 6 descriptions to be rewritten at the ingest layer.

Stage-1 freeze: the three rows carry no OECD-AIM-/AIID- source id (checked on each row's
`source_ids`, its `aiid_id`, and its references for `oecd.ai` and `incidentdatabase`
hosts: all empty). Neither the 15 new rows nor the narrowed rows carry any. The scratch
build ran in a directory with no `.git`, so `_pair_inputs_changed()` returned its
conservative True and the content checks of `_check_refresh_merge_authorization` were at
their strictest; the build exited 0. The gate would apply to B only through
re-attribution into a frozen row (INC-01434, INC-01408, INC-00814, INC-02325,
INC-03812), which I recommend against.

Notes and obligations if B proceeds:
- CORRECTIONS row (ID records: 1 appended for B-retire, 0 for B-keep; content narrowed on
  2 or 3 rows; 15 or 16 rows added). B-keep would ALSO be the case ID_POLICY section 4
  rule 1's D70 note describes (a live ID re-pointed at a different incident), which is
  why I recommend B-retire.
- docs-warden: counts 15,666 -> 15,681 and 15,637 -> 15,652 wherever stated (I did not
  run `make build` in scratch, so `stats.json` and the rendered docs were not
  regenerated; `stats.json` is produced by the render step and not by the merge).
- NOTICE-DATA, `.reuse/dep5`, CITATION.cff and README name INC-02646 and INC-03233 as
  the two rows that carried round-up text (a statement about published releases). Under
  B-retire INC-02646 stops being live; those notices need a pointer, not a rewrite of
  history (agreement 4).
- Pipeline task (WS4): generalise the split-authorization input (second dated list or
  re-pinned constant) and a re-ruling decision id.

External citer of INC-02646 under B-retire: `resolve_id_status("INC-02646")` returns the
nine successors with reason `split`, including the GPT-4.1 row, the DeepSeek row and the
CVE-2025-23254 row. Under B-keep the citer silently gets the DeepSeek incident.

### 4C. Leave the rows and document the limitation

Delta: 0 rows, 0 fields, 0 IDs, 0 deprecation records, no freeze interaction, byte-identical
build. Obligations: a CORRECTIONS or known-limitations entry stating that INC-00924,
INC-02646 and INC-03233 each aggregate several distinct incidents, that 15 incidents from
the OWASP round-ups have no row of their own, and that INC-02646's CVE, tags and
framework codes belong to several incidents; plus a line in DATA_DICTIONARY. The
rule-level risk remains (new round-up ids would fold the same way, and the 14 similar rows
stay). External citer of INC-02646: sees a "GPT-4.1 jailbreak" title with 12 source ids,
a TensorRT-LLM CVE, a DeepSeek tag and `confidence: high` from 12 sources. Honest, but
misleading to a casual reader, and a search for DeepSeek, CVE-2025-23254 or Storm-2139's
siblings returns the wrong row.

### Summary of option deltas

| | A (A2 form) | B-keep | B-retire | C |
|---|---|---|---|---|
| Live rows | 0 | +15 | +15 | 0 |
| New IDs | 0 | 15 | 16 | 0 |
| Existing rows touched | 0 | 3 (37 field changes) | 2 (17 field changes) | 0 |
| New deprecation records | 0 | 0 | 1 (`split`, 9 successors) | 0 |
| Build aborts without new authorization | no | n/a (needs it) | n/a (needs it) | no |
| Freeze | not triggered | not triggered | not triggered | not triggered |
| Pending blockers | none | 6 verbatim rows, 3 bad dates, authorization machinery | same | none |

(Field-change totals: 10 + 20 + 7 = 37 for B-keep; 10 + 7 = 17 for B-retire.)

## 5. Recommendation

1. **Ship A2 first.** It costs nothing in data (byte-identical build), it is the same
   device the code already uses for the CVE guard, and it stops the next round-up from
   folding. Do not ship A1: it fails closed.
2. **Do B as its own release, B-retire form, after the blockers clear.** Reasons: 15
   incidents (DeepSeek, CVE-2025-23254, Copilot Studio, Reprompt, Sony, CAIN, ViKing, ...)
   are absent as rows, and INC-02646 is wrong on its CVE, tags, codes and confidence;
   INC-00924's date is the wrong year. B-keep must not be chosen: it is the D70 defect
   shape on a Critical row, and it changes what a 15-release-old citation means.
   Titles of all three rows have been identical in every tag from v2.0.0 to v2.13.0
   (checked by reading `data/incidents.json` at each of the 15 tags), so there are real
   citers of INC-02646 as a GPT-4.1 incident.
3. **Do not bundle the other 14 candidate rows or the 598-row fresh-state residue.** They
   are a separate, larger programme; naming them here is so the user sees the scale.
4. **Order of work for B:** (a) rewrite the 6 verbatim or near-verbatim OWASP ingest
   descriptions (licensing blocker); (b) fix the 3 `2026-Q1` dates; (c) WS4 generalises the
   split authorization and a decision id is ruled; (d) build, field-level delta, gate;
   (e) docs-warden count sweep and CORRECTIONS row.

## 6. Decisions only the user can make

1. Split at all (A only / A then B / C).
2. If B: INC-02646 `retire` (recommended) or `keep_id`; INC-00924 and INC-03233
   `keep_id` (continuity holds for both: same title, same incident).
3. New ID allocation: let the build mint them (recommended, sequential from the counter),
   or pre-reserve a block so numbers are stable across an intervening refresh.
4. The 5 probable-existing incidents: mint a new row for each (simplest, adds duplicates),
   hold them back, or re-attribute (needs a key decision, and four of the five targets are
   frozen OECD/AIID rows or carry no usable key). I recommend minting and listing the five
   as a duplicate follow-up for WS2.
5. Q2-2025-09 (credential-stuffing surge) is a trend, not an incident: mint as
   `threat-report`, or leave unshipped.
6. Whether to extend the rule beyond OWASP round-ups (the 14 similar rows; a fan-out
   threshold would also split legitimate multi-report incidents such as GeminiJack, so it
   needs a precision check first).
7. The `2026-Q1` date value for 3 ids (recommend `2026`) and the licensing rewrite of 6
   ingest descriptions (a license-auditor/user call already open on the board).

## 7. Reproduction and falsifiers (agreement 6)

Everything was run on `git archive` copies outside the worktree (no stray files in the
tree). Recipe: extract `git archive HEAD` to a scratch dir; `python scripts/parse_existing.py`
(regenerates the gitignored `data/legacy_consolidated.json`); then the build.

| Claim | Method | Input that would have made it fail |
|---|---|---|
| Baseline reproduces | scratch `merge_and_dedupe.py` output compared with the committed `data/incidents.json` | any difference: result was byte-identical, so the harness faithfully models the build |
| Which branch merges | wrapper on `merge_into`, recording the caller's line | a non-URL cause would have shown another line; the trace shows 1857/1801/1833 |
| Cause is the URL key | exclude the 3 URLs; survivors +15 and exactly 3 ids split | an unrelated cause would leave the split guard silent, or split other ids; it named only these 3 |
| 20 -> 5 merges equals the +15 | counts from the trace logs of both builds | the arithmetic would not close |
| A2 is byte-stable | `cmp` of incidents.json and id_deprecations.json against the published ones; `stats.json` is not written by merge, so my cmp of it could not fail, and the claim rests on the gate's re-derivation (render_markdown.py on baseline and on the A2 copy, identical stats.json; gate-overmerge 2026-10-13) | any difference; there was none |
| Class A/B counts | graph of non-URL links per published row (258 candidate rows) | the three known rows return their known group counts, which a wrong grouping would not |
| New-row and field deltas | diff of before/after JSON from real scratch builds | n/a (computed from the output, not asserted) |
| "Existing row" claims | keyword/CVE search, my reading | JUDGMENT, flagged as such in section 3 |

The A2 probe (scratch only): add `_AGGREGATE_URL_RE = re.compile("^genai[.]owasp[.]org/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^?]*round-?up", re.IGNORECASE)`
and `_is_aggregate_url(normalized_url)`; in `_claim` change the weak-key test to
`if weak and (cve_disjoint(target, other) or _is_aggregate_url(key)) and not _same_prior(target, other):`;
in the URL branch change it to
`if (not cve_disjoint(candidate, e) and not _is_aggregate_url(u)) or _same_prior(candidate, e):`.
The A1 probe replaces the three `normalize_url(` calls inside `dedupe_entries` with a
wrapper returning an empty key for that regex. The B probe appends
`{"from": "<id>", "decision": "keep_id" | "retire", "reason": "scratch"}` entries to a COPY of
the D28 list and re-pins `REQUIRED_SPLIT_AUTHORIZATION_ENTRIES_SHA256` in the copy.

What I did NOT do: run `make build`/`make test` on the real tree (no data change was made
or needed), re-measure licensing overlap, regenerate `stats.json`, or judge class-B rows
individually.
