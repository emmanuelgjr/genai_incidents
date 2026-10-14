# Brief triage: the user's 17-item brief, candidates 2-17 (2026-10-14)

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4).
> **Triage only. No data changed. Agent-suggested.** Nothing here is a ruling.
> - **Tree:** `main` @ `c80b7e61` (v2.13.0 tag peels to `9cdaf5e5`; 167 commits since).
> - **Inputs:** the brief (appendix), `PROGRESS.md` (v2.13.0 queue, 2026-10-06), and
>   `docs/audits/v2.13.0-premise-check-2026-10-06.md`. Every verdict below was re-measured
>   against code, data or a live surface. The board and the CHANGELOG were used only to find
>   things, never as evidence.
> - **Live fetches:** 2026-10-14 between 10:31 and 10:34 UTC.
> - **You may be wrong, and so may this file.** Every figure carries its re-derivation command.
>   All commands run from the repo root. `python` means the repo's interpreter.
>   `$L` is any scratch directory that holds the live downloads.

## Summary

| # | Candidate | Verdict | Evidence | What remains |
|---|---|---|---|---|
| 1 | Legacy-seed reference audit | **see separate file** | `docs/audits/reference-detection-2026-10-14.md` (another agent's run, in progress) | not triaged here |
| 2 | Docs/README sync + drift-check extensions | **partly done** | CHANGELOG `## [2.13.0]` exists. README Latest release = 2.13.0 / 2026-10-13. Drift check covers the Latest-release line, version metadata and the HF card template (CHANGELOG 2.13.0, "drift check now covers..."). The ASI link is the 2026 Top 10 on every surface that links it. | (a) `owasp_dsgai` is exported (HF JSONL, 103 rows) but is missing from `TAXONOMIES.md`, the HF card, `taxonomy_versions` and `mappings/`. (b) The drift check does **not** catch a stale mapping filename or an exported-but-undocumented field. (c) **New finding:** the site's `build_manifest.json` and `data/stats.json` say `version: 2.13.0` with `incident_count: 15755`, a figure no v2.13.0 artifact carries. |
| 3 | Reconstruct changelog + v2.13.0 notes | **done** (overtaken) | CHANGELOG `## [2.13.0] — 2026-10-13` (CHANGELOG.md:125); `docs/releases/v2.13.0.md`; the disputed state is documented in two 2.13.0 sections and DATA_DICTIONARY.md:17-18. The "+118" now sits in `[Unreleased]` (113 AIID + 5 AIAAIC). | Nothing for v2.13.0. A v2.14.0 notes draft does not exist yet. That is future cut work, not this item. |
| 4 | Root clutter / split PROGRESS.md | **partly done** | `AGENT_TEAM.md` is now `docs/archive/AGENT_TEAM.md`. One archive slice exists: `docs/board-archive/PROGRESS-log-to-2026-10-04.md`. | `PROGRESS.md` is still 842,437 B, and **GitHub does not render it** (measured). `MASTER_IMPROVEMENT_PLAN.md` is still at root. **Premise conflict:** CLAUDE.md's Foreman Protocol step 1, `.claude/agents/red-reviewer.md` and 7 scripts/tests name the root paths. Moving them needs a user decision. |
| 5 | `load_incidents()` excludes retracted by default | **still valid** | `load_incidents()` takes no arguments (`src/genai_incidents/__init__.py:113`). Packaged slim JSON: 15,784 rows, of which 29 are retracted and 22 disputed. | All of it: `include_retracted=False`, a package/PyPI first-paragraph note and a changelog behaviour-change entry. Premise correction: no `unverified` status exists in the schema or data. |
| 6 | ATLAS refresh + lint + taxonomy_versions + monthly workflow | **done** | Pin 2026.09 = upstream `dist/v6/ATLAS-latest.yaml` → `ATLAS-2026.09.yaml` (fetched). `scripts/lint_atlas_ids.py` runs in Makefile:37, validate.yml:50 and auto-refresh.yml:411 (rc 0, 71 ids). `.github/workflows/atlas-refresh.yml` runs on cron `0 5 3 * *`. `taxonomy_versions` is in stats.json, the live STIX identity, the package and the HF card. CHANGELOG 2.13.0 "MITRE ATLAS pin refreshed". | none. `capec: null` is disclosed. |
| 7 | Rejected/disputed CVE weekly gate | **done** | The `cve-sweep` job in auto-refresh.yml:50-90 runs `ingest_cve_rejections.py --max-requests 1200 --max-seconds 2400`. Dated logs: `docs/audits/cve-sweep/2026-10-09.*`, `2026-10-13.*`. 22 disputed rows: `status_reason.code=cve-disputed`, confidence 17 medium / 5 low, 0 high. The state is documented in DATA_DICTIONARY.md:17-18. | none. The full sweep covered the 21 AVID-only CVEs (CHANGELOG 2.13.0). |
| 8 | Ids that resolve to None | **done, premise false** | Re-run today: `resolve_id_status()` returns `unknown` for **0** of 16,849 IDs ever published. INC-03128 → INC-14909 and INC-08185 → INC-14742 (successor). `resolve_id()` still returns `None` for 776 IDs, all with a named status (below). `valid_for_releases` and `docs/ID_POLICY.md` are in place. | none for the brief's scope. `resolve_id()` keeps `str \| None` by design (D49). The typed answer is `resolve_id_status()`. |
| 9 | N9 precision audit + standing measure | **partly done** | Sampler, sheet, Wilson script, DATASHEET section and validate gate shipped in v2.13.0. `docs/audits/precision/2026-10-11/review_sheet.csv` has 150 rows, **0 human labels**. Pending state ratified (D76). | Human labelling (user). Then a measured figure, the DATASHEET and release-notes figure, and the `evaluate_ai_relevance.py` run. Deviation (ratified): the frame is `tier: feed`, not `quality_tier: auto`. |
| 10 | AIRI Navigator sunset | **done** (decided) | Memo `docs/audits/airi-navigator-sunset-memo-2026-10-09.md`. Retired 2026-10-13 under D108; D124 resolved the D57 hold. Live STIX: 1,382 objects carry `x_source_freshness`. MISP tags and the HF card `review_by` are in place (CHANGELOG 2.13.0). | none. Premise off by two: 1,382 rows, not 1,380. |
| 11 | OECD/AIID unfreeze memo | **partly done / overtaken** | Memo `docs/audits/oecd-aiid-unfreeze-decision-memo-2026-10-09.md`. The AIID side was lifted under D114 (CHANGELOG `[Unreleased]`, +113 rows). The OECD side is held until suppression is built. | The OECD half: the suppression build, then a user decision. No unfreeze branch exists on origin (`git ls-remote` empty). |
| 12 | Export integrity | **done** | Live `data/SHA256SUMS` lists `incidents.stix.json`, and its hash `a4f6eb70…` equals the sha256 of the served bundle. `taxii2/SHA256SUMS` and `misp/SHA256SUMS` are present. `build_manifest.json` is served on the site, HF and the Release assets. STIX `modified` follows `updated` + `EXPORTER_VERSION`. | Shape deviation: the manifest has `disputed_count` instead of `unverified_count`, because no `unverified` status exists. See also finding 2(c). |
| 13 | ASI mapping = 2026 Top 10 | **done** | `mappings/owasp_asi_top10.json`: version `2026`, url `…/owasp-top-10-for-agentic-applications-for-2026/`, codes ASI01 Agent Goal Hijack … ASI10 Rogue Agents (all ten match). No live surface links the 2025 T&M doc as the source of the codes; T&M is cited separately as "related". | none. The HF card names the framework but has no link (not wrong, but thin). |
| 14 | `docs/RELATED_WORK.md` | **still valid** | The file does not exist. README.md:150 still reads "A full side-by-side positioning comparison is planned but not yet written." | All of it (WS7-T1). |
| 15 | MISP/OpenCTI import re-test | **still valid** | No `docs/audits/feed-import-*` file exists. `docs/taxii2/README.md:18` still carries the old caveat. | All of it (needs a MISP and an OpenCTI instance). |
| 16 | Hygiene bundle | **partly done** | Done: Zenodo concept `20248675` → record 23328791 v2.13.0 (API). The redeposit step is in VERSIONING.md:295 (step 8). PyPI trusted publishing (`id-token: write`, publish.yml:15). Provenance attestations exist for both 2.13.0 files (PyPI integrity API returns 200). SECURITY.md:7 has a contact. | **33 of 37** `uses:` lines are not SHA-pinned. No `.github/dependabot.yml` (register a14 is the user's call). `CORRECTIONS.md` has **no row** for the 29 retractions or the OSV licence correction. Issue #88 is open with no v3.0 re-baseline plan (last update 2026-07-04). The `attack_vector: other` count (4,371 standing) is in no release notes. |
| 17 | Cut prep v2.13.0 | **done** (overtaken) | Tag `v2.13.0` → `9cdaf5e5`. GitHub Release published 2026-10-13T00:32:37Z with 6 assets. PyPI 2.13.0, HF manifest 2.13.0 and Zenodo v2.13.0 are all live. | none. The next cut (v2.14.0) carries the `[Unreleased]` +118. |

---

## Candidate 1

See `docs/audits/reference-detection-2026-10-14.md`. Another agent is running the detection.
Not investigated here.

## Candidate 2: docs and README sync

**Done:**
- **CHANGELOG.** `CHANGELOG.md` on main has `## [2.13.0] — 2026-10-13` (line 125) under `[Unreleased]`.
  - `grep -n '^## ' CHANGELOG.md | head -3`
- **README "Latest release".** It reads "2.13.0 — released 2026-10-13" (README.md:144). It also says, in-line, that counts have since risen (+5 AIAAIC, +113 AIID).
  - `grep -n 'Latest release' -A2 README.md`
- **Drift check.** `python scripts/check_stats_drift.py` → rc 0, "clean: 5 doc surfaces …".
- **Layout block.** The brief claimed it "still lists owasp_llm_top10_2025.json as current". **Stale:** README.md:282-286 lists `owasp_llm_top10_2026.json` first, then 2025, then the crosswalk. Nothing labels 2025 as current.
  - `sed -n 282,290p README.md`

**Standing-entry number per surface** (fetched 2026-10-14 10:31-10:34 UTC):

| Surface | Figure | Version label | Command |
|---|---|---|---|
| README (main) | 15,755 incidents / 2,028 landmark | 2.13.0 | `grep -n 'stats:incident_count\|stats:landmark_count' README.md` |
| `data/stats.json` (main) | 15,755 / 2,028 / 29 retracted / 22 disputed | `"version": "2.13.0"` | `cat data/stats.json` |
| Site hero | 15,755 | — | `curl -sL https://emmanuelgjr.github.io/genai_incidents/ \| grep -o 'stats:incident_count -->[0-9,]*'` |
| Site `data/build_manifest.json` | 15,755 / 2,028, commit `e288712f` | **`"version": "2.13.0"`** | `curl -sL https://emmanuelgjr.github.io/genai_incidents/data/build_manifest.json` |
| PyPI `genai-incidents` 2.13.0 description | 15,637 / 1,915 | 2.13.0 | `curl -s https://pypi.org/pypi/genai-incidents/json \| python -c "import json,sys,re;d=json.load(sys.stdin)['info'];print(d['version'],re.findall(r'[0-9]{1,2},[0-9]{3}',d['description'])[:2])"` |
| HF `emmanuelgjr/genai-incidents` card + manifest | 15,637 / 1,915, commit `9cdaf5e5` | 2.13.0 | `curl -sL https://huggingface.co/datasets/emmanuelgjr/genai-incidents/raw/main/README.md \| grep -n '15,6'`; `…/raw/main/build_manifest.json` |

**The surfaces do not agree, and this is by design.** The Pages workflow runs on push to main (`pages.yml:3-11`). The HF workflow (`huggingface.yml`, `on: release`) and PyPI publish only on a release. So released channels show 15,637 and main-tracking channels show 15,755.

**The real defect (new finding 2(c)):** main's `data/stats.json` and the site's served `build_manifest.json` pair `version: "2.13.0"` with `incident_count: 15755`, but **no v2.13.0 artifact has 15,755 rows.**
- Re-derive: `git show v2.13.0:data/stats.json` → 15,637.
- A consumer who reads the site manifest gets a wrong version/count pair.
- A `-dev` or "post-2.13.0" version marker on main-tracking surfaces would fix it. That is a design decision for WS6 and the user.

**ASI link.** Every link to the ASI codes' source points to the 2026 Top 10 for Agentic Applications: README.md:373, TAXONOMIES.md:61, `docs/index.html:86`, NOTICE-DATA:130, `.reuse/dep5`:120, SOURCE_LICENSES.md:405, `mappings/owasp_asi_top10.json` `url`, and the live PyPI description.
- The T&M document (`agentic-ai-threats-and-mitigations`) appears only where it is cited separately as "related": README.md:374, TAXONOMIES.md:63, the mapping's `related.url`, and PyPI.
- The live site links only the 2026 Top 10. The live HF card names "OWASP Top 10 for Agentic Applications (ASI)" but carries **no link at all**.
- Command: `git grep -n "agentic-ai-threats-and-mitigations\|owasp-top-10-for-agentic-applications" -- ':!PROGRESS.md' ':!docs/audits/*' ':!docs/archive/*' ':!CHANGELOG.md' ':!docs/releases/*' ':!docs/board-archive/*'`

**`owasp_dsgai`. Still valid; this half of the item is undone.**

| Where | Present? |
|---|---|
| `data/incidents.json` | 103 standing rows carry the key, 76 non-empty, codes DSGAI01-DSGAI21 |
| HF JSONL export | yes. `scripts/export_huggingface.py` `build()` dumps every non-retracted row verbatim |
| `incidents.min.json` | no (0 rows) |
| STIX | no field |
| Schema | `schema/incident.schema.json:307` |
| `docs/DATA_DICTIONARY.md:46` | documented ("OWASP Data Security for GenAI codes (`DSGAInn`, companion)") |
| `docs/TAXONOMIES.md` | **no** |
| HF card field list (export_huggingface.py:102) | **no** |
| `taxonomy_versions` | **no** |
| a `mappings/` file | **no** |

So the brief's premise "no document names it" is **half false**: DATA_DICTIONARY names it. The gap is real for TAXONOMIES.md, the HF card and the version pin.

Commands:
- `python -c "import json;F=[e for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents'] if e.get('status')!='retracted'];print(sum('owasp_dsgai' in e for e in F),sum(bool(e.get('owasp_dsgai')) for e in F))"`
- `git grep -n -i dsgai -- scripts src schema docs/TAXONOMIES.md docs/DATA_DICTIONARY.md README.md`

**Drift-check coverage.** Read from the code: the docstring in `scripts/check_stats_drift.py` lists six failure modes and `main()` at :271 runs them.

| Brief's extension | Covered? |
|---|---|
| Stale Latest release line | **yes** (`check_latest_release`, :134) |
| Stale mapping filename | **no**. No check compares names under `mappings/` to doc references. |
| Exported-but-undocumented taxonomy field | **no**. Nothing compares exported keys to TAXONOMIES.md or the HF card. |
| Live PyPI/HF/site figures | **no**. It is offline only, by design. |

## Candidate 3: Unreleased changelog + v2.13.0 notes

**Done, and overtaken by the cut.**
- `CHANGELOG.md` `## [2.13.0]` has 12 sections. Two cover the disputed state: "rejected-CVE sweep … DISPUTED CVEs are detected" and "22 CVE-disputed entries marked". They give the field (`status: disputed`, `status_reason.code: cve-disputed`), the rule, the count (22) and the export treatment (counted; HF/STIX/MISP carry it).
- `docs/releases/v2.13.0.md` exists.
- The brief's "+118" is the post-cut delta: 15,755 − 15,637. It is fully itemised in `[Unreleased]` (113 AIID under D114, 5 AIAAIC under D112).

Commands:
- `sed -n 8,124p CHANGELOG.md | grep '^### '`
- `git show v2.13.0:data/stats.json | head -3`

## Candidate 4: root clutter

**Measured:**
- `PROGRESS.md` is 842,437 bytes (`wc -c PROGRESS.md`).
- GitHub does **not** render it as Markdown. The blob page for `main/PROGRESS.md` (fetched 10:33 UTC) has `"richText":null`. Control: `docs/board-archive/PROGRESS-log-to-2026-10-04.md` (318,286 B) and `CORRECTIONS.md` both have a rendered `"richText":"<article …"`.
- Command: `curl -sL -A Mozilla/5.0 https://github.com/emmanuelgjr/genai_incidents/blob/main/PROGRESS.md | grep -o '"richText":.\{0,12\}'`
- **Limit figure used:** about 512 KiB. It comes from the brief and is not verified against GitHub documentation here. The measurement brackets the real limit between 318 KB (renders) and 842 KB (does not), which is consistent with 512 KiB.

**Done:**
- `AGENT_TEAM.md` is at `docs/archive/AGENT_TEAM.md`.
- One PROGRESS slice has been archived (`docs/board-archive/`).

**Remains:**
- `PROGRESS.md` and `MASTER_IMPROVEMENT_PLAN.md` are at root.
- 64 tracked files mention `PROGRESS.md` and 28 mention `MASTER_IMPROVEMENT_PLAN.md`. They include `CLAUDE.md` (Foreman Protocol step 1, "Read MASTER_IMPROVEMENT_PLAN.md … and PROGRESS.md"), `.claude/agents/red-reviewer.md`, 4 scripts and 4 tests.
- Command: `git grep -l PROGRESS.md | wc -l`

**Premise conflict:** moving these files changes the protocol text in CLAUDE.md. Under CLAUDE.md step 8 ("any invariant/task conflict") that goes to the user, not to an agent. Splitting PROGRESS.md by month below about 500 KB does not conflict with anything.

## Candidate 5: retracted rows in `load_incidents()`

**Still valid.**
- `def load_incidents() -> list[dict[str, Any]]` takes no parameter and returns every row of the bundled slim JSON (`src/genai_incidents/__init__.py:113-115`).
- `src/genai_incidents/data/incidents.min.json` and `data/incidents.min.json` each hold 15,784 rows: 29 `retracted`, 22 `disputed`, 15,733 without status.
- The README's v2.12.0 paragraph tells consumers to "filter on `status`", which documents the gap without closing it.
- **Premise correction:** there is no `unverified` status. Schema and data have only `retracted` and `disputed` (`grep -n -i unverified schema/incident.schema.json` is empty).
- Command: `python -c "import json,collections;I=json.load(open('src/genai_incidents/data/incidents.min.json',encoding='utf-8'))['incidents'];print(len(I),collections.Counter(e.get('status','-') for e in I))"`

## Candidate 6: ATLAS

**Done.**
- **Pin.** `python -c "import json;print(json.load(open('mappings/mitre_atlas.json',encoding='utf-8'))['version'])"` → `2026.09`.
- **Upstream.** `curl -sL https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-latest.yaml` → `ATLAS-2026.09.yaml` (10:31 UTC). The newest file in `dist/v6` is 2026.09 (GitHub contents API). **The pin is current; "a release behind" is false today.**
- **Snapshot.** `ingest/atlas/ATLAS-2026.09.yaml` plus a provenance file.
- **Lint.** `python scripts/lint_atlas_ids.py` → "OK: 71 distinct AML.* ids … none absent or deprecated; pin matches committed snapshot" (rc 0). It is wired into Makefile:37, validate.yml:50 and auto-refresh.yml:411.
- **taxonomy_versions.** `data/stats.json` `taxonomy_versions`. The live STIX bundle has one `identity` with `x_taxonomy_versions` = `{atlas 2026.09, owasp_llm 2026, owasp_asi 2026, capec null, veris 1.4.1}`. Also present in `src/genai_incidents/data/taxonomy_versions.json`, the MISP tags (`scripts/export_misp.py:192`) and the live HF card (lines 71-72).
- **Monthly workflow.** `.github/workflows/atlas-refresh.yml`, cron `0 5 3 * *`.
- Note: the local `data/incidents.stix.json` (Aug 17, gitignored) is stale and has no identity. Use the live or Release bundle.

## Candidate 7: rejected and disputed CVEs

**Done.**
- Weekly job `cve-sweep` (auto-refresh.yml:50, step at :73-75: `--max-requests 1200 --max-seconds 2400`). It writes `docs/audits/cve-sweep/<date>.{md,json}`. Logs exist for 2026-10-09 and 2026-10-13.
- **Field and rule:** `status: disputed`, `status_reason {code: cve-disputed, as_of}`, confidence lowered one level. It stays counted. Documented in DATA_DICTIONARY.md:13,17,18.
- **Data:** 22 disputed rows, all `tier: feed`, confidence 17 medium and 5 low (0 high). `as_of` is 2026-10-09 on 19 rows and 2026-10-13 on 3.
- **Exports:** in HF and STIX (counted). `stats.json` and `build_manifest.json` carry `disputed_count`.
- Command: `python -c "import json,collections;D=[e for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents'] if e.get('status')=='disputed'];print(len(D),collections.Counter(e['confidence'] for e in D),collections.Counter(e['status_reason']['code'] for e in D))"`
- Never-checked first: the 2026-10-09 full sweep covered all 9,169 corpus CVEs, including the 21 AVID-only ones (CHANGELOG 2.13.0, testimony). The current sweep log is the artifact.

## Candidate 8: ids resolving to None

**Done; the premise "eight ids resolve to nothing" is false today.**

I took an independent route rather than `scripts/audit/silent_ids.py`. The universe is the union of:
- every `INC-*` id in `data/incidents.json` at all 15 release tags (v2.0.0-v2.13.0),
- the current file,
- every `from` in `data/id_deprecations.json`.

That gives **16,849 IDs**. Results over all 16,849 (`PYTHONPATH=src`):

| `resolve_id_status().status` | IDs |
|---|---|
| live | 15,784 |
| successor | 289 |
| withdrawn | 763 |
| pre-tombstone | 9 |
| release-dependent | 3 |
| group | 1 |
| **unknown** | **0** |

**`resolve_id()` returns `None` for 776 IDs:**

| Group | Count | IDs and answers |
|---|---|---|
| withdrawn | 763 | Deliberate `into: null` tombstones: 704 `out-of-scope` + 59 `orphaned-ingest-source-retired`. Re-derive: `python -c "import json,collections;d=json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations'];print(collections.Counter(r['reason'] for r in d if r['into'] is None))"` → 704 / 59 / 9. |
| pre-tombstone | 9 | `INC-00522`, `INC-00609`, `INC-00951`, `INC-00952`, `INC-00955`, `INC-00956`, `INC-00957`, `INC-01355`, `INC-01660` (reason `unrecorded-drop-v2.1.0`); `resolve_id_group()` = []. |
| release-dependent | 3 | `INC-00497` (group of 12), `INC-00554` (group of 100), `INC-08139` (group of 100). |
| group | 1 | `INC-00754` (group of 11). |

**The two named IDs:**
- `resolve_id('INC-03128')` → `INC-14909`; `resolve_id_group` → `['INC-14909']`; status `successor`.
- `resolve_id('INC-08185')` → `INC-14742`; `resolve_id_group` → `['INC-14742']`; status `successor`.

**Also in place:**
- `valid_for_releases` (on release-scoped records)
- `schema/id_deprecations.schema.json`
- `docs/ID_POLICY.md`
- `resolve_id_status()` (`__init__.py:439`)

`resolve_id()` keeps `str | None` (D49), so "returns a group marker instead of None" was answered with a new function, not a return-type change.

Command: the script below (`$SCR/ids.py` in the triage scratchpad), reproduced here.
```python
import json,subprocess,re,sys,collections; sys.path.insert(0,'src'); import genai_incidents as g
ids=set()
for t in subprocess.run(['git','tag'],capture_output=True,text=True).stdout.split():
    r=subprocess.run(['git','show',f'{t}:data/incidents.json'],capture_output=True)
    ids|={x.decode() for x in re.findall(rb'"id":\s*"(INC-\d+)"',r.stdout)}
ids|={e['id'] for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']}
ids|={d['from'] for d in json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']}
print(len(ids), collections.Counter(g.resolve_id_status(i).status for i in ids), sum(g.resolve_id(i) is None for i in ids))
```

## Candidate 9: precision audit

**Partly done.** The machinery shipped in v2.13.0 (CHANGELOG 2.13.0 "N9 precision audit"):
- `scripts/precision_sample.py`, seed 20261011, 100 feed + 50 landmark
- `scripts/wilson_ci.py`
- the DATASHEET "Measured precision" block ("measurement pending")
- the validate gate with the D76-ratified pending marker
- `scripts/evaluate_ai_relevance.py`

**Measured:** 150 sheet rows, **0 with `human_label`**.
- Command: `python -c "import csv;R=list(csv.DictReader(open('docs/audits/precision/2026-10-11/review_sheet.csv',encoding='utf-8-sig')));print(len(R),sum(bool(r.get('human_label','').strip()) for r in R))"`

**Remains:**
- the human review (the user's)
- then the Wilson figure into the DATASHEET and the release notes
- the ai_relevance evaluation
- the brief's "for any new source" gate. The current gate pins one audit directory; it is not keyed per source.

**Deviations:**
- The frame is `tier: feed`, not `quality_tier: auto` (ratified D76).
- The strata are tier × source family, with quality_tier only ordering the within-stratum draw. The brief asked for source × quality_tier × tier.

## Candidate 10: AIRI Navigator

**Done, and decided by the user.**
- Memo `docs/audits/airi-navigator-sunset-memo-2026-10-09.md` (options A/B1/B2/R/C).
- Retired 2026-10-13 under D108; D124 resolved the hold (CHANGELOG `[Unreleased]`). `RETIRED_SOURCES` is in `scripts/check_source_health.py`.
- **Rows:** 1,382 carry the `airi-navigator` tag, all with `source_freshness`.
  - Command: `python -c "import json;F=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];print(sum('airi-navigator' in e.get('tags',[]) for e in F),sum(bool(e.get('source_freshness')) for e in F))"`
- **Live STIX:** 1,382 objects carry `x_source_freshness`.
  - Command: `python -c "import json;o=json.load(open('$L/stix.json',encoding='utf-8'))['objects'];print(sum('x_source_freshness' in x for x in o))"`
- The premise said 1,380. The true figure is 1,382.

## Candidate 11: OECD/AIID

**Partly done, and overtaken.**
- The decision memo exists: `docs/audits/oecd-aiid-unfreeze-decision-memo-2026-10-09.md`.
- The AIID half was lifted (D114; +113 AIID rows and 169 updated on main, unreleased). The brief's "do not unfreeze" is overtaken for AIID by a user ruling.
- OECD stays held until suppression is built (D114 precondition; memory note "binding: OECD suppression first").
- No unfreeze branch exists on origin: `git ls-remote --heads origin | grep -i -E 'unfreeze|oecd'` is empty.
- **Remains:** the OECD suppression build, then the user's OECD decision.

## Candidate 12: export integrity

**Done.**
- **SHA256SUMS:**
  - Live `data/SHA256SUMS` (35 lines) lists `incidents.stix.json` with `a4f6eb70a73d…cd8d`. That equals the sha256 of the bundle served at 10:31 UTC: `sha256sum $L/stix.json`.
  - `taxii2/SHA256SUMS` (8 lines) lists the collection `objects.json` and `manifest.json`.
  - `misp/SHA256SUMS` (35 lines) is present.
- **build_manifest:** served on the site (`data/`, `misp/`), on HF, and as a Release asset (`gh release view v2.13.0 --json assets`).
- **STIX `modified`:** derived as `updated` + `EXPORTER_VERSION` ms (CHANGELOG 2.13.0, export-integrity section; `scripts/export_stix.py`).
- **Deviation from the brief:** `unverified_count` → `disputed_count`, because no `unverified` status exists.

## Candidate 13: ASI mapping

**Done** (v2.13.0 item 9, merged as `4284b127`).
- `mappings/owasp_asi_top10.json`: `version: "2026"`, `url: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/`, `citation` and `related` keys.
- The codes match the brief's list exactly:
  - ASI01 Agent Goal Hijack
  - ASI02 Tool Misuse & Exploitation
  - ASI03 Identity & Privilege Abuse
  - ASI04 Agentic Supply Chain Vulnerabilities
  - ASI05 Unexpected Code Execution (RCE)
  - ASI06 Memory & Context Poisoning
  - ASI07 Insecure Inter-Agent Communication
  - ASI08 Cascading Failures
  - ASI09 Human-Agent Trust Exploitation
  - ASI10 Rogue Agents
- Command: `python -c "import json;m=json.load(open('mappings/owasp_asi_top10.json',encoding='utf-8'));print(m['version'],m['url']);[print(k,v['name']) for k,v in m['entries'].items()]"`
- The surface sweep is in candidate 2: no surface cites T&M as the codes' source.

## Candidate 14: RELATED_WORK.md

**Still valid.**
- `ls docs/RELATED_WORK.md` → no such file.
- README.md:150: "A full side-by-side positioning comparison is planned but not yet written."
- This is plan task WS7-T1 (MASTER_IMPROVEMENT_PLAN.md:312).
- The brief adds three neighbours the plan lacks: the OWASP GenAI Threat Intelligence Initiative, `basitalisandhu/ai-agent-incidents` and `cybergemchick/ai-threat-intel`.

## Candidate 15: feed re-test

**Still valid.**
- No `docs/audits/feed-import-*` file: `ls docs/audits | grep -i feed` is empty.
- `docs/taxii2/README.md:18` "Caveat: media type & pagination" has not been revisited against the v2.13.0 artifacts.
- It needs live MISP and OpenCTI instances, so it was not attempted here.

## Candidate 16: hygiene

| Sub-item | Verdict | Evidence / command |
|---|---|---|
| CORRECTIONS.md rows for the 29 retractions | **still valid** | `grep -n -i retract CORRECTIONS.md` is empty. 14 data rows (`grep -c '^| 20' CORRECTIONS.md`), none about retractions. |
| CORRECTIONS.md row for the OSV licence correction | **still valid** | The correction is in CHANGELOG.md:641 (v2.12.0, "Row 2.4 (OSV.dev) corrected in place") and SOURCE_LICENSES.md §2.4. `grep -n -i osv CORRECTIONS.md` is empty. |
| Seed-reference corrections | depends on candidate 1 | — |
| Zenodo concept DOI holds the latest | **done** | `curl -s https://zenodo.org/api/records/20248675` → record 23328791, `version 2.13.0`, published 2026-10-13 (10:33 UTC). |
| Redeposit on the cut checklist | **done** | `docs/VERSIONING.md:295` step 8 |
| Actions pinned by SHA | **still valid** | 37 `uses:` lines, **33 unpinned** (only the 4 others are pinned, e.g. `pypa/gh-action-pypi-publish@dc37677…`). `grep -n -E '^\s*-?\s*uses:' .github/workflows/*.yml \| grep -v -E '@[0-9a-f]{40}' \| wc -l` → 33. publish.yml:36 calls SHA-pinning "this repo's supply-chain convention", which 33 lines do not follow. |
| PyPI trusted publishing + attestations | **done** | publish.yml:15 `id-token: write`, no token. `curl -s -o /dev/null -w '%{http_code}' -H 'Accept: application/vnd.pypi.integrity.v1+json' https://pypi.org/integrity/genai-incidents/2.13.0/genai_incidents-2.13.0.tar.gz/provenance` → 200, and the same for the wheel. |
| Dependabot enabled | **still valid** (user's call) | No `.github/dependabot.yml`. Alerts are on: 8 open per `docs/audits/dependabot-triage-2026-10-13.md`. Version-update config is register a14, the user's decision. |
| SECURITY.md contact | **done** | SECURITY.md:7 (an email contact) |
| v3.0 re-baseline plan on issue #88 | **still valid** | `gh issue view 88` → "Audit ~3,057 historical URL-bridge dedupe merges…", OPEN, updatedAt 2026-07-04, 1 comment, no re-baseline plan. |
| `attack_vector: other` count in release notes | **still valid** | It appears in no `docs/releases/*.md`. Today 4,374 rows, of which 4,371 standing. `python -c "import json;F=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];print(sum(e.get('attack_vector')=='other' for e in F),sum(e.get('attack_vector')=='other' and e.get('status')!='retracted' for e in F))"` |

## Candidate 17: cut preparation

**Done** (the cut happened 2026-10-13):
- **Tag:** `git rev-parse v2.13.0^{commit}` → `9cdaf5e5` ("Merge release/v2.13.0-cut").
- **GitHub Release:** `gh release view v2.13.0 --json publishedAt,assets` → published 2026-10-13T00:32:37Z with 6 assets (STIX, min.json, taxii2.zip, misp-feed.zip, build_manifest.json, SHA256SUMS).
- **PyPI:** 2.13.0.
- **HF:** manifest version 2.13.0, commit `9cdaf5e5`.
- **Zenodo:** v2.13.0.
- **Site:** tracks main.

---

## Closing claim check (the brief's announcement claims, against `main` @ `c80b7e61`)

| Claim | Verdict | Today | Re-derive |
|---|---|---|---|
| 15,637 standing entries | **true at v2.13.0; changed on main** | 15,755 (+113 AIID, +5 AIAAIC) | `git show v2.13.0:data/stats.json \| head -3`; `python -c "import json;print(json.load(open('data/stats.json'))['incident_count'])"` |
| 1,915 landmark | **true at v2.13.0; changed** | 2,028 | same two files, `landmark_count`; `python -c "import json;print(sum(e.get('tier')=='landmark' for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']))"` |
| 29 retracted | **true** | 29 | `python -c "import json;print(sum(e.get('status')=='retracted' for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']))"` |
| 410 rows blocked at merge | **true as a v2.12.0 build figure [A]; not re-derived** | Not re-measured; it would need a merge run. Source: CHANGELOG.md:628, `docs/releases/v2.12.0.md:128` ("352 cvelistV5, 58 AVID"). | `grep -n '410 emitted' CHANGELOG.md` |
| 21,017 OWASP LLM refs across 14,004 STIX objects | **true at v2.13.0; changed** | v2.13.0 Release bundle: 21,017 / 14,004. Live site (main): 21,078 / 14,055 | `gh release download v2.13.0 -p incidents.stix.json -D $L/rel`, then `python -c "import json;o=json.load(open('$L/rel/incidents.stix.json',encoding='utf-8'))['objects'];n=[sum(r.get('source_name','').startswith('owasp-llm') for r in x.get('external_references',[])) for x in o];print(sum(n),sum(1 for k in n if k))"` |
| EUVD not ingested | **true** | No ingest code mentions EUVD | `git grep -il euvd -- scripts ingest src \| wc -l` → 0 |
| OSV licence claim corrected | **true** (but not logged in CORRECTIONS.md) | CHANGELOG.md:641; SOURCE_LICENSES.md:288-292 | `grep -n 'Row 2.4' CHANGELOG.md` |
| OECD/AIID refresh frozen | **changed** | AIID side lifted (D114, unreleased); OECD held | `sed -n 10,25p CHANGELOG.md` |
| One source dead since May | **changed** (true but superseded) | AIRI Navigator: last success 2026-05-31, retired 2026-10-13 (D108) | `grep -n -A3 'AIRI Navigator retired' CHANGELOG.md`; `cat data/source_freshness.json` |
| CVE/GHSA audit open | **true** | Issue #88 OPEN; N9 precision has 0 human labels | `gh issue view 88 --json state`; the candidate 9 command |
| ATLAS mapping a release behind | **false** | Pin 2026.09 = upstream latest | the candidate 6 commands |
| Eight ids resolve to nothing | **false** | 0 IDs answer `unknown` from `resolve_id_status()`. `resolve_id()` is `None` for 776 IDs, each with a named status (763 withdrawn, 9 pre-tombstone, 3 release-dependent, 1 group). | the candidate 8 script |
| 11,658 → 15,637 since v2.5.0 | **true for v2.5.0 → v2.13.0; changed on main** (→ 15,755) | — | `git show v2.5.0:data/stats.json \| head -3` → 11658 |
| 47 over-merged incidents split | **true** (v2.11.0, D28) | — | `grep -n '47-split' README.md CHANGELOG.md \| head -3` |
| Row-level content licences and source-freshness flags | **true** | `content_license` on 3,772 rows (3,767 at v2.13.0, +5 AIAAIC); `source_freshness` on 1,382 | `python -c "import json;F=json.load(open('data/incidents.json',encoding='utf-8'))['incidents'];print(sum(bool(e.get('content_license')) for e in F),sum(bool(e.get('source_freshness')) for e in F))"` |

Also in the brief's preamble: "site shows 15,755 standing entries and a 'CVE-disputed' state that no changelog entry describes".
- **The 15,755 is true** today on the site.
- **"No changelog entry describes" is false.** Two `## [2.13.0]` sections describe it (see candidate 3). At v2.12.0, when the brief was written, the state was not yet released, which is probably why it read that way.

---

## Appendix: the brief, verbatim

# The user's 17-item brief (written against v2.12.0 from outside the repo) — CANDIDATES, not instructions

Brief's stated baseline: v2.12.0 + main; "site shows 15,755 standing entries and a 'CVE-disputed' state that no changelog entry describes".

1. Legacy-seed reference audit. Hand-curated seed (source_ids INC-001 onward; ~3,200 v1.0 rows, many reviewed/curated) has references that are not sources. Examples: INC-033 cites arxiv.org/abs/2501.01234 (a neutron-star physics paper); INC-045, INC-046 cite arXiv 2408.00000 and 2407.00000 (placeholders); INC-041 cites the risk.net homepage; INC-036/037/040/042 cite reuters.com/legal, the MSRC root, a USENIX index page and a blog root. Wants scripts/audit_references.py flagging: path depth <=1 or index pages (/blog/, /news/, /advisories, /issues, conference indexes); arXiv/DOI ids whose fetched title shares no content tokens with entry title/affected; one generic URL reused across many rows; "research"-typed refs resolving to non-paper pages; descriptions with a specific figure (dollar, %, duration, count) not in any cited source. Then replacement, status: unverified enum, demotion to quality_tier auto, validate.py hardening.
2. Docs and README sync: docs-stats renderer + drift check; README, DATASHEET, HF card, PyPI metadata, CITATION.cff, site: entry and landmark counts, "Latest release" paragraph (claimed still 2.9.0 / 13,060), layout block (claimed still lists owasp_llm_top10_2025.json as current), ASI link (must be OWASP Top 10 for Agentic Applications 2026), taxonomy list. HF schema exports an owasp_dsgai code family no document names (document in TAXONOMIES.md or drop). Extend check_stats_drift to fail on stale Latest release line, stale mapping filename, exported-but-undocumented taxonomy field.
3. Reconstruct the Unreleased changelog from git log v2.12.0..main (+118 entries, disputed-CVE state: field, rule, count, export treatment); draft docs/releases/v2.13.0.md with consumer impact + re-derivation recipe.
4. Root clutter: git mv PROGRESS.md, AGENT_TEAM.md, MASTER_IMPROVEMENT_PLAN.md to docs/project/, fix inbound links, split PROGRESS.md by month below GitHub render limit. CLAUDE.md stays at root.
5. pip agrees with headline: load_incidents() and slim JSON return retracted (and unverified) rows; add include_retracted=False default; state in package README/PyPI description first paragraph; changelog behaviour change.
6. MITRE ATLAS refresh and lint: pull ATLAS-latest.yaml, record version, diff vs pinned 2026.06, re-map, report changed entries; CI lint fails on AML.* id absent/deprecated in pinned release; taxonomy_versions (atlas, owasp_llm, owasp_asi, capec, veris) in stats.json and every export (STIX x_ property, MISP manifest, HF card, package metadata); monthly scheduled ATLAS re-pull workflow opening a PR.
7. Rejected and disputed CVEs as a standing gate in weekly refresh: never-checked ids first (21 AVID-only CVEs), then full re-check; DISPUTED writes status_reason and lowers confidence; dated sweep log per run; document the disputed state already live on the site.
8. The eight ids that resolve to None: successor records INC-03128 -> INC-14909, INC-08185 -> INC-14742; resolve_id_group() for four ambiguous retirements, resolve_id() returns a group marker instead of None; valid_for_releases on two release-dependent ids; ID_POLICY.md + tests; close disclosed deviation in release notes.
9. Precision audit N9 + standing precision measure: seeded stratified sampler (source x quality_tier x tier) 100 auto + 50 landmark into docs/audits/precision/<date>/ with review sheet; agent pre-fill marked suggested_by: agent; Wilson 95% precision from human-confirmed rows; "Measured precision" in DATASHEET + release notes; validate.py gate (threshold, D28-style override) refusing release with no confirmed sample for any new source; evaluate scripts/ai_relevance.py after sheet returns.
10. AIRI Navigator: confirm bulk channel withdrawn, check replacement, tag the 1,380 rows stale in every export (x_source_freshness in STIX, MISP tag, HF card), review_by in source_freshness.json, sunset memo with both options, stop for decision.
11. OECD/AIID refresh: do not unfreeze; decision memo (what D25(a) blocked, whether E23 + title-only shipping removes it, what first unfrozen run changes, residual licence risk); prepare unfreeze branch; stop.
12. Export integrity: STIX content change bumps modified (from entry updated + exporter version); SHA256SUMS covers STIX, TAXII, MISP; emit data/build_manifest.json (commit, built_at, incident_count, retracted_count, unverified_count, landmark_count, taxonomy_versions) carried in every channel.
13. ASI mapping: mappings/owasp_asi_top10.json derived from 2026 Top 10 for Agentic Applications (ASI01 Agent Goal Hijack ... ASI10 Rogue Agents); pin edition: 2026; fix any surface linking the 2025 threats-and-mitigations doc.
14. Positioning doc docs/RELATED_WORK.md: sourced table vs AIID, AIAAIC, OECD AIM, MIT AI Risk Repository, AVID, MITRE ATLAS case studies, OWASP GenAI Threat Intelligence Initiative, basitalisandhu/ai-agent-incidents, cybergemchick/ai-threat-intel; coverage, curation model, taxonomy mappings, exports, licence; README differentiator must survive; replace README's "planned but not yet written" line with the link.
15. Feed re-test: clean MISP and OpenCTI imports against current artifacts; object counts/errors in docs/audits/feed-import-<date>.md; refresh TAXII README caveats.
16. Hygiene: CORRECTIONS.md entries for the 29 retractions, the OSV licence correction, seed-reference corrections; Zenodo concept DOI holds latest release + redeposit on cut checklist; pin every GitHub Action by SHA; PyPI trusted publishing with attestations; Dependabot enabled; SECURITY.md contact; v3.0 re-baseline plan on issue #88; publish current attack_vector: other count in release notes.
17. Cut preparation for v2.13.0 (tag, GitHub Release, PyPI, HF, Zenodo, site), stop before tagging.

Brief's closing claim-check list (announcement claims): 15,637 standing entries; 1,915 landmark; 29 retracted; 410 rows blocked at merge; 21,017 OWASP LLM references across 14,004 STIX objects; EUVD not ingested; OSV licence claim corrected; OECD/AIID refresh frozen; one source dead since May; CVE/GHSA audit open; ATLAS mapping a release behind; eight ids resolve to nothing; 11,658 -> 15,637 since v2.5.0; 47 over-merged incidents split; row-level content licences and source-freshness flags.
