# WS4-T10 BOUNCE #1 — committed per-entity Phase B delta (explainer)

**Status: dated record, 2026-09-15. DO NOT REGENERATE this narrative** (the
JSON artifact it explains IS meant to be regenerated — see below). This
file explains `docs/audits/WS4-T10-phaseB-delta-2026-09-15.json`, generated
by `scripts/audit/ws4t10_phaseb_delta.py`, comparing:

- **control**: `main` @ `eeb7ca9c` (unchanged `normalize_url`)
- **fixed**: this branch @ `883707c7` (post-BOUNCE #1 `normalize_url` —
  the web_view blocklist fix and related BOUNCE #1 corrections; NOT the
  original `c9424935` Phase B commit, whose numbers this supersedes)

Both built via `python scripts/parse_existing.py && python
scripts/merge_and_dedupe.py` in detached scratch worktrees (never `git
stash` — the stash stack is shared with other worktrees in this session).
Control reproduces committed `data/incidents.json`/`data/id_deprecations.json`
byte-identically (sha256 `facbf809...` / `f24f38f3...`, matching both `main`
and red-reviewer's BOUNCE #1 gate measurement) — confirming the delta below
is attributable to the code change alone. `ws4t10_phaseb_delta.py` was
itself proven to fire on a deliberately corrupted copy (6 injected defects,
6 caught, 0 false negatives) before being trusted here; rerun it any time
the normalizer changes (its own docstring has the exact commands).

## Top-line numbers (superseding `c9424935`'s Phase B — say what moved)

| metric | `c9424935` (pre-BOUNCE#1) | this delta (post-BOUNCE#1 fix) | moved because |
|---|---|---|---|
| corpus size | 13,060 → 13,361 (+301) | 13,060 → 13,361 (+301) | unchanged |
| common rows changed | 48 | **47** | INC-08183 no longer changes — the web_view fix (defect 2) closed its false split |
| title/description swaps | 5 | **4** | same reason — INC-08183 dropped out |
| splits | 47 | 47 | unchanged (INC-08183 was never a split — same source_ids both builds — see below) |
| **survivor title continuity** | not measured | **43 hold / 4 break** | new measurement (defect 1) |
| severity changes (all downward) | 26 | 26 | unchanged |
| reference URLs gained corpus-wide | "1 gained" (undercounted, defect 4) | **377 distinct, 0 lost** (entries 66,048 → 66,425) | re-measured at the URL-set level, not the per-row-count level |
| new deprecations | 1 (`INC-07738`→`INC-14757`, merged) | 1 (same) | unchanged |
| invariant 4 violations | 0 | 0 | unchanged |
| `validate.py` on the fixed build | not run | **exit 1**, 1 integrity violation | newly measured (defect 3) |

## Defect 1: full split population, not a sample — the recommendation changes

The prior doc's Option 2 recommendation ("the tie-break does not track the
real incident even once") was measured **only on the 5 rows that already
looked like swaps — selection bias.** Measured on **all 47** splits:

- **43 of 47 keep title continuity**: the successor that keeps the old id
  has the SAME title as the currently-published row. `INC-02671` (Grok
  NCII) keeps 17 of 18 source_ids and sheds one unrelated
  robotic-lawnmower/hedgehog row — this is Option 1's ideal case, not a
  counter-example.
- **Only 4 break continuity**: `INC-00311`, `INC-00554`, `INC-00754`,
  `INC-01897` — full old/new titles in `title_or_description_changes` in
  the JSON.
- Continuity does **not** correlate with source-count retention fraction —
  `INC-00861` keeps only 2/32 (6%) of its old source_ids yet keeps the
  right title; `INC-00554` similarly keeps only 2/103 (2%) but picks the
  WRONG content. The signal that matters is title continuity itself
  (comparing the currently-published row to what the fixed code's own
  mechanical tie-break naturally produces for that id), not source-count
  share.

See `docs/specs/WS4-T10-unmerge-design-2026-09-15.md`'s Revision 2 section
for the re-weighed recommendation this drives.

## Defect 2: INC-08183 — found as a false split, now fixed

Red-reviewer's gate measured, on the ORIGINAL `c9424935` code: `INC-08183`
had **identical source_ids in both builds** yet its title/description/date/
year/category all flipped ("Google Bard Conversation Exfiltration" →
"Malicious Models on Hugging Face"), caused by a
`?&web_view=true`-tagged ReversingLabs URL keying apart from its bare
twin, splitting the row's own references across two dedup keys and
flipping which reference anchored the row's content. **This delta (built
against `883707c7`, which blocklists `web_view`) confirms it is fixed**:
`INC-08183`'s source_ids, title, description and reference count (12) are
now identical in both builds — it no longer appears anywhere in this
delta's `common_rows_changed` or `splits`. Recorded here per BOUNCE #1
defect 2c as a **regression the gate found and this fix closed**, not
swept under the rug by its absence from the current numbers.

## Defect 3: `validate.py` fails closed on the fixed build TODAY

Running `python scripts/validate.py` against the fixed build's output
(same worktree as this delta) exits **1**:

```
13361/13361 entries valid; 0 with errors.
...
1 integrity violation(s):
  - 1 entr(ies) carry discovery_method outside the landmark tier (e.g. INC-14614)
```

`INC-14614` is the CVE-2025-10875-mis-keyed `curation_overrides.json`
override (see Phase C's §2.3b). This means, **as measured, not
hypothesized**: `.github/workflows/validate.yml` ("Validate incidents.json
against schema"), `.github/workflows/auto-refresh.yml` ("Re-merge + render
+ validate"), and `.github/workflows/cve-enrich.yml` ("Re-merge + render +
validate") would all **fail closed today** if this branch's code ran
against the current committed corpus. That is a real, working safety net
— but it is a **single point of failure**: it is exactly the one override
Phase C's §5(2) tells remediation to re-key, and once that's done with
nothing else in place, an ordinary rebuild would ship §2.1/§2.2's silent
content swaps with `validate.py` passing clean. Phase C's Revision 2
sequences the continuity guard to land WITH or BEFORE that re-keying, not
after.

## Defect 4: reference restoration, corpus-wide

`c9424935`'s doc said "references: 47 dropped ... 1 gained" — a
**per-row reference COUNT** comparison, which misses same-count swaps and
undercounts net corpus-wide restoration. Measured at the **distinct-URL
level** across the whole corpus: **377 distinct reference URLs newly
shipped, 0 lost** (66,025 → 66,402 distinct URLs; 66,048 → 66,425 total
reference entries). Full URL lists are in the JSON's `references` block. Red-reviewer's gate
measured 379/0 against the pre-BOUNCE#1 code (`c9424935`); this
measurement (377/0, against `883707c7`) supersedes it, as directed — the
BOUNCE #1 code changes (the web_view/iref/edtsign/edtcode/scm/Liferay
blocklist additions, `ref` removed from the blocklist, query-value case
preservation) all touch which reference-URL pairs collapse onto the same
dedup key, so a small residual difference between the two counts is
expected. This delta does not further decompose which specific code
change accounts for which unit of the -2 difference — the corpus-wide
distinct-URL figure (not a per-change attribution) is what both this and
the gate's measurement report.

## Top-10 split rows by old source_id count, classified

| old id | old source_ids | splits into | continuity | classification |
|---|---|---|---|---|
| `INC-00554` | 103 | 100 | **BREAKS** | split itself plausibly correct (100 genuinely distinct Korean-language stories); **ID-continuity regression** — Option 2 needed |
| `INC-00861` | 32 | 31 | holds | plausibly correct, safe under Option 1 |
| `INC-00134` | 24 | 22 | holds | plausibly correct, safe under Option 1 |
| `INC-07736` | 20 | 17 | holds | plausibly correct (Korean chatbot Luda vs Naver algorithm manipulation vs an EasyMile shuttle injury vs unrelated surveillance/facial-recognition stories — all distinct), safe under Option 1 |
| `INC-02671` | 18 | 2 | holds | plausibly correct (Grok NCII vs an unrelated robotic-lawnmower/hedgehog story), safe under Option 1 |
| `INC-00754` | 14 | 11 | **BREAKS** | split itself plausibly correct (FSU shooting vs Jason Momoa deepfake romance scam, clearly unrelated); **ID-continuity regression** |
| `INC-01897` | 14 | 8 | **BREAKS** | split itself plausibly correct (distinct WordPress plugin CVEs); **ID-continuity regression** |
| `INC-05013` | 14 | 11 | holds | plausibly correct (TruDi navigation system keeps its identity; sheds the AIID-1575/Eightfold-AI row that was masking a second AIID/OECD content disagreement — see `tests/test_e21_partA_inc00437_provenance.py`), safe under Option 1 |
| `INC-00311` | 12 | 12 | **BREAKS** | split itself plausibly correct (12 genuinely distinct stories); **ID-continuity regression** |
| `INC-01271` | 12 | 12 | holds | plausibly correct (EU Grok deepfake investigation keeps its identity), safe under Option 1 |

**`INC-08183`** is listed separately, not in this table, because it is not
a split (identical source_ids both builds) — see defect 2 above. It was a
**regression found by the gate and fixed by this commit**, the one
concrete example this task has of the non-split "stable-ID content swap"
harm class defect 2d asks the design to cover generically.

**No regression among the 47 splits' content separation itself** was found
in a targeted scan (title-similarity `>0.55` across all 47 groups' sibling
pairs: 59 pairs, top matches manually reviewed, all confirmed distinct
entities sharing a boilerplate report template with disjoint CVEs — e.g.
two VS Code extensions `SakaDev`/`AI Code`, two ONOS XSS CVEs, several
WordPress plugin CVE pairs). This is a scan on a similarity proxy, not an
exhaustive check — WS4-T5 (P1) is the task that closes that gap properly.

## Named CVE megaclusters — still unaffected

`INC-04106` (174), `INC-04260` (143), `INC-01015` (120), `INC-08766` (68),
`INC-03798` (41) are **identical in both builds** (same source_id counts,
same titles) — confirms they were never URL-bridged, unaffected by the
BOUNCE #1 blocklist changes too.

## Regenerating this artifact

```
git worktree add --detach <control_dir> main
git worktree add --detach <fixed_dir> <this-branch-HEAD>
# in each worktree:
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
# from the main checkout:
python scripts/audit/ws4t10_phaseb_delta.py <control_dir> <fixed_dir> \
    docs/audits/WS4-T10-phaseB-delta-2026-09-15.json
git worktree remove <control_dir> --force
git worktree remove <fixed_dir> --force
```
