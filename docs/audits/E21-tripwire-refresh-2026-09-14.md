# E21 tripwire refresh investigation — 2026-09-14

**Status (2026-09-15, defect 12): FINAL — dated investigation record. Do
not regenerate.** Corrected in place, original text preserved, per working
agreement 4, after red-reviewer's BOUNCE #1 (2026-09-15) on the `ef9ce6fb`
version of this file. Corrections are marked `⚠ CORRECTION 2026-09-15
(red-reviewer BOUNCE #1, defect N)` inline at each affected passage; small
in-place factual fixes (defects 1, 10, 11) are listed in the "Corrections
log" section near the end. See `PROGRESS.md` ("E21 TRIPWIRE FIRED …audit
BOUNCE #1") for the full gate verdict this file is responding to.

> Original header, preserved for the record (superseded by the status line
> above): ~~**Status: WORKING DOCUMENT, being extended commit-by-commit as
> findings land. Do not regenerate the sections marked final; append/amend
> per working agreement 4 once this stabilizes.**~~

**Trigger:** the refresh-state persist fix (`05f536ff`) merged and, for the
first time in 8 weeks, `.github/workflows/auto-refresh.yml` run
`34858279213` got past Persist and through "Re-merge + render + validate,"
then failed at "Unit tests" — 1 failed / 318 passed, no refresh PR opened.
The failing test:
`tests/test_e21_partA_inc00437_provenance.py::test_oecd_aiid_content_disagreement_is_unique_to_inc00437`,
which found **29** aiid_id-bearing rows whose description doesn't match
AIID's template, not the expected 1 (`aiid_id` 1574 / INC-00437):
`[1552, 1574, 1584, 1604, 1610, 1612, 1616, 1622, 1641, 1642, 1643, 1644,
1646, 1647, 1650, 1654, 1656, 1658, 1659, 1660, 1661, 1662, 1665, 1666, 1668,
1669, 1671, 1673, 1674]`.

Method throughout: an in-process, read-only repro of the merge pipeline
(`merge_and_dedupe.normalize_entry`/`dedupe_entries`), run against a locally
re-fetched `ingest/oecd_aim_full_incidents.json` in a scratch git worktree
(`git worktree add --detach <scratch> ae05019a`), never against the main
working tree. Every live fetch went through `ingest/common.py` (invariant
5), same as `.github/workflows/auto-refresh.yml`'s own invocation:
`OECD_AIM_LIMIT=3000 python scripts/ingest_oecd_aim.py`.

---

## Finding 1 — local repro matches CI exactly [R]

```
cd <scratch>; OECD_AIM_LIMIT=3000 python scripts/ingest_oecd_aim.py
```

| | CI (`34858279213`) | Local repro |
|---|---|---|
| Fetched | 2988/3000 | 2988/3000 |
| Fetch wall time | 3026s | 3088s |
| Parsed ok | 1098 | 1098 |
| Parsed unparseable | 1890 | 1890 |
| Security-relevant kept | 1097 | 1097 |
| Union (fresh + existing → retained) | **logged** (defect 1, fixed in place — CI's own log has the line): `[aim] union: 1097 kept + 4160 existing -> 5248 retained` | 1097 + 4160 existing → **5248 retained** |

The four count fields that matter (fetched, parsed ok, unparseable,
security-relevant kept) are **byte-identical** between CI and the local
repro, run ~1h45m apart on the same day. The fetch order also matches:
the same three URLs (`2026-08-26-0132`, `2026-08-06-0af1`, `2026-08-06-16ac`)
404 first in both runs. **Match: exact, both runs against the same live
sitemap window on 2026-09-14.**

The existing-file baseline (4160) is the currently-committed
`ingest/oecd_aim_full_incidents.json` row count — confirmed by direct read
of that file (`len(json.load(...)) == 4160`).

## Finding on the fetch-time regression (iii) — explained, not hypothesized [R]

292s (07-12 run `29182692358`) → 358s (07-19 run `29676405074`) → 3026s/3088s
(09-14). `git log` on `ingest/common.py` / `scripts/ingest_oecd_aim.py`:

```
fbb61ff7 2026-07-29 18:47  WS0-T4 conduct-half: promote ingest_utils.py to
                            ingest/common.py, migrate all network scripts
                            through it
5937653e 2026-07-29 19:53  WS0-T4 bounce #1 (D1,D3,R1,R3,R5): ... rate-limit
                            robots.txt, pin the allowlist
```

Both the 07-12 and 07-19 runs **predate** this migration (2026-07-29). Before
it, `ingest_oecd_aim.py`'s 10-worker pool evidently paced independently
(~10 req/s aggregate against `oecd.ai`, matching 3000 pages in ~300s in both
pre-migration runs). `ingest/common.py::_rate_limit()`'s own docstring
states the limiter blocks "across ALL callers/threads -- not just this one"
(defect 10, quote fixed in place — the actual text, `ingest/common.py:187`;
no docstring reading "thread-safe and global per host, not per caller"
exists in that file) — i.e. after the migration, all 10 workers queue behind ONE shared
`DEFAULT_MIN_INTERVAL = 1.0`s budget for `oecd.ai`, collapsing aggregate
throughput to ~1 req/s regardless of worker count. 3000 pages / 1 req/s ≈
3000s — matches both the CI run (3026s) and the local repro (3088s) almost
exactly. **This is a real, dated, confirmed code change, not retries**: CI's
own log shows only 40 total HTTP errors this run (39×404 + 1×403) — nowhere
near enough failed/retried requests to account for a 10x slowdown.

**Operational flag, not asked for but worth recording:** a full
`OECD_AIM_LIMIT=3000` crawl now costs ~50 minutes of the workflow's 60-minute
timeout. There is little headroom left before this specific step alone
blows the job timeout on a slower day.

## Finding — 40 HTTP errors vs. 1890 "unparseable" [R]

```
gh run view 34858279213 --log | grep -oE "HTTP Error [0-9]+: [A-Za-z ]+" | sort | uniq -c
#   1 HTTP Error 403: Forbidden
#  39 HTTP Error 404: Not Found
```

Only 40 of 2988 fetches failed at the HTTP layer. The other ~1850
"unparseable" pages fetched successfully (implicitly 200 — `robust_fetch`
raises/logs on any non-2xx after retries, and none of those log lines
appear for these pages) but did not yield a parseable incident record. Part
A of the H2 investigation (below) traces this to the page's *content*, not
its transport status.

## Finding — AIID snapshot dates [R]

`ingest/aiid_full.provenance.json` (committed): `fetched_at: "2026-07-18"`,
`snapshot_filename: "backup-20260713110347.tar.bz2"`. A live, sanctioned,
single-GET discovery call (`scripts/ingest_aiid_snapshot.discover_latest_snapshot()`,
routed through `ingest/common.py`, run once in the scratch worktree) finds:

```
LATEST: backup-20260907101103.tar.bz2
https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-20260907101103.tar.bz2
```

A newer AIID snapshot (2026-09-07) exists and has not been ingested — the
committed `ingest/aiid_full.json` reflects AIID's own database as of
2026-07-13/18, ~2 months stale relative to today (2026-09-14).
`scripts/ingest_aiid_snapshot.py` is a `make ingest-aiid`-only, manual step
(`Makefile:90`) — it is **not** part of `.github/workflows/auto-refresh.yml`,
confirmed by reading that workflow file directly (its **four** — not three,
defect 11, fixed in place — `python scripts/ingest_*.py` steps are
AIRI/AIAAIC/OECD/CISA-KEV only; `.github/workflows/auto-refresh.yml:39,44,51,56`).

## Finding — the tripwire has a pre-existing blind spot: `aiid_id` 898 / INC-08183 [R]

The currently-committed `data/incidents.json` (13,060 rows, `generated:
"2026-07-31"`) already carries a **second** AIID-template exception besides
1574, found by running the full-corpus version of the same check directly:

```python
aiid_rows = [e for e in entries if e.get("aiid_id")]        # 1465
exceptions = [e for e in aiid_rows if not TEMPLATE.match(e["description"])]
# [('INC-08183', 898), ('INC-00437', 1574)]
```

`INC-08183`'s `source_ids` are `AIID-898`/`ATLAS-*`/
`EXT-2024-HF-MALICIOUS-MODELS`/`RES-etr-bard-exfil-2023` — no `OECD-AIM-*`
id at all (confirmed by E21 Part A §4 already; re-confirmed here directly
against the live committed file). The tripwire test's `_RELEVANT_FILES`
scope is deliberately `("aiid_full.json", "oecd_aim_full_incidents.json")`
only, so it **cannot see INC-08183 at all** — not a bug in the test (its own
docstring explains the restriction), but a real, named blind spot: this
tripwire only ever covers the AIID-vs-OECD disagreement class, not
AIID-vs-anything-else. See "Tripwire evolution" below.

## Finding — `aiid_id` 1552, initial observations [R, partial]

- `aiid_full.json` **does** contain `AIID-1552` (unlike the 28 other tripwire
  rows, which are all `> 1581`, `aiid_full.json`'s max id — 1552 is well
  inside its range: 1548 ids present out of a possible 1581, i.e. 33 gaps).
- In the **current, committed, full corpus**, `aiid_id` 1552 already lands on
  a large pre-existing merge cluster, `INC-00554`: 103 `source_ids`, 512
  `references`. Its description **does** match the AIID template exactly
  today — `description_provenance`/`description_source` are both null,
  consistent with an AIID-authored survivor, and there is **no mislabeling
  in the currently-shipped corpus** for this id.
- The **2-file-restricted tripwire repro against the CURRENT (pre-refresh,
  committed) `oecd_aim_full_incidents.json`** also does *not* flag 1552 (the
  baseline 3-test run passes cleanly: `python -m pytest
  tests/test_e21_partA_inc00437_provenance.py -q` → `3 passed`). The
  committed file already has a row cross-referencing `AIID-1552`
  (`OECD-AIM-2026-06-30-4590`, dated 2026-06-30) and it merges correctly
  into the AIID-1552 entry via the source-ID dedup key
  (`dedupe_entries`'s `by_src` index, checked before any weak title/URL key).
- **Not yet established:** why the *refreshed* 2-file repro flags 1552 as an
  exception. Pending the exception-set repro against the refreshed file
  (next commit) and the H2 new-vs-existing source_id analysis the foreman
  requested.

---

---

## Finding 2 — the tripwire exception-set repro against the refreshed file, exact [R]

`_build_surviving()`'s own logic, run in-process against `ingest/aiid_full.json`
+ the refreshed `ingest/oecd_aim_full_incidents.json` (scratch worktree):

```
surviving: 6183  aiid_rows: 1549  exceptions: 29
exception aiid_ids: [1552, 1574, 1584, 1604, 1610, 1612, 1616, 1622, 1641,
  1642, 1643, 1644, 1646, 1647, 1650, 1654, 1656, 1658, 1659, 1660, 1661,
  1662, 1665, 1666, 1668, 1669, 1671, 1673, 1674]
matches CI's 29? True  (diff both directions: [])
```

Exact match to CI's failure. **The 29-row population is fully reproduced
locally, from a live re-fetch, not assumed from the CI log.**

## Finding 5 (mechanism) — H2 literally refuted for the new-source_id question; a THIRD mechanism (H3) found instead [R]

### (ii) What the "1890 unparseable" pages actually are

Every one of the 2988 cached pages **does** carry an `<script id="ng-state">`
tag (0/2988 missing it) — so "unparseable" is not a fetch/transport problem,
confirmed directly rather than inferred:

```
has ng-state tag: 2988  no tag: 0
of those with tag: body extracted (oecd.extract_state() succeeds): 1136
                    body NOT extracted (wrong shape): 1852
```

(1136 vs. the ingest run's own "1098 ok" — the ~38-row gap is later-stage
filtering inside `normalize_body`/`main()`, e.g. year-range rejection; not
investigated further, immaterial to the finding.)

> **⚠ CORRECTION 2026-09-15 (red-reviewer BOUNCE #1, defect 6):** the ~38-row
> gap above is **not** immaterial and **not** `normalize_body` filtering.
> **[R] by red-reviewer, gate 2026-09-15, recorded PROGRESS.md; not
> re-derived by the author:** it is `fetch_page()`'s own 800 KB truncation —
> `data[:800_000]` at `scripts/ingest_oecd_aim.py:129` (line confirmed by the
> author directly: `data = robust_fetch(...); return data[:800_000]...`).
> The gate found **7/7** sampled cached date-hash pages over 800 KB fail to
> parse after truncation, and **0** other pages fail this way — i.e. the
> 1,890 "unparseable" figure decomposes as **1,852 numeric-slug pages (this
> finding's own H2-refutation, still correct) + 38 truncated date-hash
> pages**, not 1,852 + an unexplained residual. **This means ~38 new
> incidents are silently dropped on every run that hits a >800 KB page** —
> gate-recommended new task WS4-T6 (a parser contract test on a >800 KB
> fixture, and removing or raising the truncation).

**The sitemap itself explains the 1852 figure exactly.** Re-fetching the
sitemap live and inspecting the URL shape of the crawled window:

```
sitemap total incident URLs: 10000
first 3000 (crawled window): numeric-slug=1852  date-hash-slug=1148  other=0
first 5 numeric-slug URLs: /en/incidents/256, /321, /281, /342, /359
first 5 date-hash-slug URLs: /en/incidents/2026-09-10-1de6, /2026-09-07-e398, ...
numeric-slug URL positions in the newest-first window: min=1148, max=2999
```

**1852 numeric-slug URLs in the crawl window == 1852 "wrong shape" pages,
exactly.** OECD AIM's sitemap now lists two ID schemes: a modern
`YYYY-MM-DD-<hex>` scheme (1148 URLs, genuinely the newest, sorted first)
and an old, small-integer legacy scheme (`/en/incidents/256` etc. — visibly
OECD's own original sequential numbering, unrelated to AIID's numbering) —
**and the legacy-scheme pages now occupy slots 1148-2999 of the "newest
3000" window**, i.e. inside the crawl budget the ingest script spends on
"the most recent N." Pulled one open sample: the legacy page's own
`ng-state` blob has a different top-level key shape (hashed keys, `b/h/s/
st/u/rt` sub-fields) that never satisfies `extract_state()`'s
`isinstance(v, dict) and body.get("id") and body.get("title")` check — a
real, page-content-level shape difference, not a fetch failure.

**Consequence for (i)/H2-as-literally-asked ("are the new source_ids
re-keyed duplicates"):** they cannot be — **zero** of the 1852 legacy-slug
pages produce a parseable body at all, so none of them can contribute a
`source_id` to the output, duplicate or otherwise. The ~1088 new
`OECD-AIM-<date-hash>` source_ids in the refreshed file are **entirely** the
product of the 1148 (minus ~50 fetch failures) genuinely-new,
date-hash-slugged pages — each carrying a real, distinct, date-stamped id
never fetched before. **H2 (re-keying/duplication via the legacy scheme) is
refuted as the explanation for the new source_ids.**

**But the legacy-scheme resurfacing is real and matters on its own:** it
burns roughly 60% of a rate-limited, ~1 req/s crawl budget on pages that can
never parse, which — combined with Finding 1's rate-limiter change —
compounds the timeout-headroom risk already flagged. If OECD's sitemap
keeps growing the legacy-scheme block forward in "newest first" position,
future weekly crawls capture progressively *less* of the genuinely new
1148-and-growing date-hash population within the same 3000-page/~50-minute
budget.

### H3 — cluster-target reassignment (the actual mechanism behind 1552, and worse than either H1 or H2)

Tracing `aiid_id` 1552 directly: `AIID-1552` **is** in `aiid_full.json` (as
established in Finding — "1552 observations"), and only **one** raw OECD row
(`OECD-AIM-2026-06-30-4590`) explicitly cross-references `AIID-1552`. That
row is present, unchanged, in *both* the baseline and refreshed files. Yet:

```
BASELINE (committed .orig, pre-refresh):
  exceptions: [1574]
  1552-cluster: aiid_id=1552, source_ids=103, description = AIID's own
    template ("AI Incident Database (AIID) entry #1552: Tesla Driver...")
  OECD-AIM-2026-06-10-3f61 present in baseline file: True (already there!)

REFRESHED:
  exceptions: [... 1552 ...]
  1552-cluster: aiid_id=1552, source_ids=141 (+38), description = OECD's
    own template, sourced from OECD-AIM-2026-06-10-3f61
```

**`OECD-AIM-2026-06-10-3f61` was already present in the baseline file and
already a member of this same 103-row cluster — it just wasn't the
*surviving target* until 38 more rows joined the cluster.** This is not
re-keying and not simple staleness: `dedupe_entries()` is a **single-pass,
order-dependent** algorithm. Weak-key (title/URL) transitive merges
(`_reindex`'s `_claim`) always make *whichever entry is currently being
reindexed* the absorbing "target," regardless of which side carries
higher-trust (AIID-sourced) content — `merge_into()` never touches
`description`/`title`, so whichever entry happened to become the anchor
first keeps its own text forever, until a later reindex pass makes a
*different* entry the anchor instead. Adding new rows to an existing large
weak-key cluster can flip which pre-existing member is the anchor, silently
discarding the previously-shipped content of whichever member loses anchor
status — even though nothing about that content itself changed.

**This is corpus-wide, not AIID-specific**, and not limited to the 29
tripwire rows. Confirmed independently, per agreement 6, by a full pipeline
rebuild (Finding — full rebuild, below): of 58 common corpus IDs whose
`description` changed between the committed corpus and the refreshed-input
rebuild, only **3** are in the 30-row AIID exception population — **55 are
completely unrelated rows**, several with a **severity regression**
(`Critical` → `High` on `INC-00627`, `INC-00813`; source_id counts
*shrinking*, e.g. `INC-00627` 5→1, `INC-00746` 4→2 — the mirror image of
1552's growth, i.e. some clusters split apart, not just merged). A downward
severity revision from silent cluster churn is exactly what WS4-T2's
reconciliation charter (propagate downward severity revisions via status +
conflicts, never silently) is meant to prevent, and this mechanism bypasses
it entirely.

### (iii) already answered in Finding 1 (rate limiter migration, dated commits, not retries).

### Per-row (iv) attribution — all 29 tripwire rows + the 898/INC-08183 blind spot

| class | count | aiid_ids | description |
|---|---|---|---|
| **H1 — simple** (single new `aiid_id` > snapshot max 1581, 2-source_id row, no competing content, `in_baseline_exceptions=False`) | 20 | 1574\*, 1584, 1610, 1612, 1616, 1622, 1641, 1642, 1644, 1650, 1654, 1656, 1658, 1660, 1661, 1662, 1665, 1666, 1668, 1673 | Nothing in `aiid_full.json` competes; OECD's own row becomes the corpus target outright. Textbook staleness (Finding — AIID snapshot dates). \*1574/INC-00437 is the one row with an existing, correct override. |
| **H3 — cluster churn, no real content displaced** (multiple *new* `aiid_id`s, none in the snapshot, merged into one row by weak keys) | 7 | 1604, 1643, 1646, 1647, 1669, 1671, 1674 | Several genuinely-new OECD/AIID incidents about the same story arc get weak-key-bridged into one corpus row — order-sensitive, but there is no pre-existing AIID content being overwritten (none of the bridged ids are in the snapshot). |
| **H3 — cluster churn, real AIID content displaced** (cluster contains ≥1 `aiid_id` that **is** in the snapshot, previously template-matching, now flipped to OECD's text) | 2 | 1552, 1659 | The severe subclass: `INC-00554`/1552 (141 source_ids, was 103) and `INC-00699`/1659 (33 source_ids) both had real, correct AIID-template content before the refresh and ship OECD's own synthesized text after it, purely from new rows joining the cluster. |
| **Pre-existing blind spot**, not caused by this refresh | 1 | 898 (`INC-08183`) | No `OECD-AIM-*` source at all — a research-blog-sourced entry, unrelated mechanism, invisible to the 2-file-scoped tripwire (Finding — blind spot, above). Unchanged by this refresh (byte-identical old vs. new). |

20 + 7 + 2 + 1(pre-existing) = 30, matching the full-rebuild corpus-level
exception count exactly (Finding — full rebuild, below).

## Finding — full rebuild, entry-count and ID-set delta, per agreement 6 (form d) [R]

`python scripts/merge_and_dedupe.py` run to completion **inside the scratch
worktree only** (its own `ROOT`/`DATA` resolve to the scratch tree; nothing
touched the main working tree or `C:\repos\genai_incidents\data\*.json`),
with the refreshed `oecd_aim_full_incidents.json` as the only ingest-file
difference from the currently-committed input set:

```
[oecd_aim_full_incidents.json] 5248 raw -> 5248 normalized   (was 4160)
[total] 19517 input -> 14063 unique                          (was 13060)
```

Per-ID, not just totals:

| | Value |
|---|---|
| Old corpus (committed) | 13,060 |
| New corpus (rebuilt from refreshed input) | 14,063 |
| New-only IDs (genuinely new corpus rows) | 1,011 |
| Old IDs no longer present | 8 |
| Common IDs (both revisions) | 13,052 |
| Common IDs with a changed `description` | 58 |

**The 8 "missing" IDs are not silent deletions — invariant 3 held
mechanically**: every one has a same-day `data/id_deprecations.json` entry,
`reason: "merged"`, naming the surviving ID it was folded into:

```
INC-01271 -> INC-00487   INC-01469 -> INC-00699   INC-01787 -> INC-00554
INC-02381 -> INC-01579   INC-05013 -> INC-00699   INC-08148 -> INC-01628
INC-13037 -> INC-00554   INC-14317 -> INC-13066
```

Two of these land on the SAME two IDs the H3 per-row table already named as
content-displaced (`INC-00554`/1552, `INC-00699`/1659) — independent
confirmation, via a completely different signal (ID consolidation records,
not description-text comparison), that those two clusters are actively
being restructured by this refresh, not merely relabeled.

**Corpus-level AIID-template-exception count**: 2 today (898, 1574) → **30**
after a full rebuild with the refreshed input — exactly `29 (2-file scope)
+ 1 (898, the pre-existing blind spot, unaffected by the refresh)`. The
full-pipeline run **independently reproduces the 2-file test's entire
population**, with no new full-corpus-only cases beyond what the 2-file
scope already found — the restriction to `("aiid_full.json",
"oecd_aim_full_incidents.json")` is not hiding a larger population.

**Not investigated further (flagged, not resolved):** the other 55
description-changed rows, and whether any severity/field changes among
them beyond the two spot-checked (`INC-00627`, `INC-00746`, `INC-00813`)
are downward severity revisions. This is squarely WS4-T2/WS4-T5 territory
and is named as a follow-up in Finding 6, not resolved here — it is beyond
this task's brief (the E21/AIID tripwire), but was found in the course of
answering (v) and would be a defect to hide by omission.

## Finding 3 — mislabeling count [R]

Of the 29 tripwire rows (2-file scope): **1** (1574/INC-00437) has a correct,
existing `curation_overrides.json` entry (`description_provenance:
"original"`, `description_source: "oecd-aim"`). **The other 28 are
unlabeled** — `description_provenance`/`description_source` both
null/absent on the raw ingest row and nothing overrides them — despite
shipping OECD's own authored text under an `aiid_id`/`AIID-<n>` signal.
**28/29 mislabeled, 1/29 correctly labeled.** At the full-corpus level
(Finding — full rebuild), the same ratio holds for the 30-row population
minus 1574: 29/30 mislabeled.

## Finding 4 — licensing surface [R]

Every one of the 29 exception descriptions was checked against
`build_description()`'s own template shape (a compiled regex matching
"Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as
`<source_id>`[, dated `<date>`][. Entities named...][. Classified attack
vector...]. See the AIM incident page (`<url>`) and its cited news sources
for full narrative detail."). **0/29 rows ship any text outside that
structural template** — no `summary`/`evidences`/narrative prose reaches
any of the 29 rows checked. The H3 mechanism changes *which* row's
structural-template text ships, and mislabels its provenance, but does not
by itself introduce any narrative/copyright exposure beyond what E21
already assessed and reduced. **Count only, no legal opinion, per brief.**

---

## Finding 6 — remediation options (propose only, implement nothing)

**(a) Per-row `curation_overrides.json` entries, INC-00437-style.**
Blast radius: 28 new entries now, an unknown but nonzero number every week
(H1 alone guarantees this keeps recurring as long as the AIID snapshot
channel stays 2+ months behind OECD's own cross-references — Finding, AIID
snapshot dates). **H3 makes this worse than originally scoped**: a row can
move *into or out of* the mislabeled population on any refresh that adds a
single new member to an existing cluster, without that row's own OECD
source_id ever changing — a per-source_id override keyed the INC-00437 way
cannot track a row whose identity migrates between clusters week to week.
Touches: invariant 2 (field-level delta — each new override needs its own
justification paragraph, as INC-00437's does), no invariant conflicts
otherwise. **Not recommended as the primary fix** — treadmill, and provably
insufficient given H3.

**(b) Class fix: derive `description_provenance`/`description_source` from
the text actually shipped, at ingest time, unconditionally.**
`ingest_oecd_aim.py::normalize_body()` already knows, for every row it
emits, that `description` is `build_description()`'s own synthesized
template — **100% of the time**, never AIID's or any other source's prose
(Finding 4: 0/29 exceed the template shape). Setting
`description_provenance: "original"`, `description_source: "oecd-aim"`
unconditionally on every OECD AIM row (mirroring
`ingest_aiaaic_sheet.py:540-541`'s existing pattern for AIAAIC, confirmed —
`merge_and_dedupe.py:869-872` already copies these fields straight through
`normalize_entry()` if present on the raw row) closes the defect **for
every mechanism, including H3**: whichever row ends up as a cluster's
surviving target, if that row is OECD-authored, its own
`description_provenance`/`description_source` travel with it (these fields
are not in `merge_into()`'s single-value-fields list, so a target's own
ingest-time-set value is never clobbered by an absorbed row — verified
against `merge_and_dedupe.py:1882`). Blast radius: 2 new fields added to
every one of the (currently) 4,160/5,248 OECD rows' normalized output — a
field-level delta that is uniform, mechanical, and fully explained by one
sentence, not 28 separate hand-justified entries. Removes the need for
future per-row overrides of this specific class entirely (INC-00437's
existing override becomes redundant but harmless — could be retired in the
same change, foreman's call). **Recommended as the required, immediate fix
for the mislabeling defect** — it is small, safe, self-maintaining, and
correct regardless of which mechanism (H1 or H3) produces the next
disagreement.

**(c) Add the AIID snapshot ingest to `auto-refresh.yml`.**
Reduces (does not eliminate) the H1 population by keeping
`ingest/aiid_full.json` current — a newer snapshot already exists
(`backup-20260907101103.tar.bz2`, Finding — AIID snapshot dates) and the
fetch mechanism (`ingest_aiid_snapshot.py`) already routes through
`ingest/common.py`, so it is mechanically invariant-5-compliant with no new
register entry needed. Does **not** touch H3 at all — a fully-fresh AIID
snapshot would still be subject to cluster-target churn on any row whose
`aiid_id` is inside a large weak-key cluster (1552 and 1659 are *both*
already in the snapshot; H1-staleness is not why they broke). Cost: a new
weekly network step (a full snapshot download, larger than the OECD crawl
in bytes though far fewer requests), added workflow runtime, and a scope
decision squarely inside the foreman's/user's remit (D1's sanctioned
channel, weekly cadence, conduct review) — not decided here.

**(d) Fix or mitigate the dedup algorithm's order-sensitivity (H3) —
NEW, not in the original brief, found in the course of answering (v).**
The root defect is that `dedupe_entries()`'s transitive weak-key merge has
no notion of "this content is higher-trust, keep it as the anchor even if a
different entry is being reindexed when the clusters collide." A minimal
version: when a transitive absorption (`_claim`'s `merge_into(target,
other)` path) would replace an anchor that has a *real* AIID-sourced
description (matches the template, backed by an `aiid_full.json` row) with
one that does not, prefer the AIID-sourced side as `target` regardless of
which one is structurally "being reindexed." A fuller version routes any
such ambiguous weak-key merge to `data/merge_review_queue.json` for human
review instead of auto-merging — which is WS4-T5's own charter
(`audit_dedupe.py`, ambiguous fuzzy-title merges to the review queue) and
should not be built ad hoc inside this task. **Blast radius is large and
not fully mapped**: 58 rows moved on this single trial rebuild, only 3 of
them in the AIID population; at least 2 carry severity regressions.
Touches: WS4-T2 (reconciliation must see downward severity revisions, not
have them silently produced by this path), WS4-T5 (this *is* the audit
target), invariant 3 (currently holds mechanically via
`id_deprecations.json`, but the "merged" reason string doesn't distinguish
"this is genuinely one incident" from "the algorithm's anchor flipped" —
worth a distinct reason code). **Not a small fix; scope and priority is a
board decision, not this task's to make.**

**Recommendation:** do **(b) now** — it is cheap, safe, general, and closes
the actual defect this task was dispatched to investigate (mislabeled
provenance) regardless of mechanism. Treat **(d) as a new, higher-priority
finding for the board**: the H3 evidence (58 rows reshuffled including
severity drops, from one refresh, on data that has not even merged yet) is
reason enough to **not merge any OECD refresh PR — this one or a future
one — until (d) is at least scoped**, independent of whatever this task's
own remediation timeline turns out to be. **(a)** is not recommended as
the primary mechanism (superseded by (b), and provably insufficient under
H3). **(c)** is a separate, valid scope decision for the user/foreman,
complementary to (b)/(d), not a substitute for either.

## Finding 7 — tripwire evolution

**The right invariant is "zero mislabeled," not "population size stays at
1."** Once (b) ships, the correct replacement for
`test_oecd_aiid_content_disagreement_is_unique_to_inc00437` is: *every*
`aiid_id`-bearing corpus row either (i) matches AIID's own template, or
(ii) carries a non-null `description_provenance`/`description_source`
explaining what it actually ships — asserting **zero** unlabeled
disagreements, not counting the disagreement population (which Finding
5/6 shows is expected to keep growing under H1 and can move under H3, and
neither growth nor movement is itself a defect once (b) is in place).

**Name the input that would make the new check fail (agreement 6):** any
ingest path that ships non-AIID content under an `aiid_id`/`AIID-<n>`
signal *without* setting `description_provenance`/`description_source` —
concretely, a bug in (b)'s implementation, a new non-OECD ingest source
that also cross-references AIID without adopting the same convention, or a
regression that clears these fields somewhere in the merge pipeline
(`merge_into`, `_reindex`, or `normalize_entry` itself).

**Scope must widen past the 2-file restriction to close the 898/INC-08183
blind spot** (Finding — blind spot): the corpus-level check
(Finding — full rebuild's method: read `data/incidents.json` directly, no
2-file restriction) already covers both the OECD-content class and the
research-blog class 898 belongs to, at zero extra cost — the 2-file
scoping was only ever a *speed* optimization for isolating the OECD-AIM
mechanism specifically, per the current test's own docstring; the general
"zero mislabeled" property does not need that restriction and should not
inherit its blind spot. Recommend: keep the fast 2-file test as a
regression guard on the (b)-fix specifically, and add a second, full-corpus
test asserting the general "zero unlabeled `aiid_id` disagreement"
property (covering 898/INC-08183-class exceptions too) — both land in the
same PR that ships (b), a decision for whoever implements the remediation,
not made here.

**A distinct, separate tripwire is recommended for H3** (not a
replacement for the above): a rebuild-stability check that fails when a
refresh changes the *anchor* (description/title/aiid_id) of an
already-existing large weak-key cluster without the anchor's own content
changing — concretely, something like "for any corpus ID present in both
the pre- and post-refresh trial builds, if `description` changed, either
the row's own primary `source_id`'s content changed, or the change is
flagged for review" — this is a proposal for WS4-T5's charter to absorb,
not a spec to implement here.

---

## Cleanup

Scratch worktree removed after this investigation
(`git worktree remove <scratch>; git worktree prune`); `git status
--porcelain` and `git worktree list` in the main tree confirmed clean
before the final commit (see the report message for the exact output).
