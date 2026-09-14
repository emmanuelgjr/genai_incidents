# E21 tripwire refresh investigation — 2026-09-14

**Status: WORKING DOCUMENT, being extended commit-by-commit as findings land.
Do not regenerate the sections marked final; append/amend per working
agreement 4 once this stabilizes.**

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
| Union (fresh + existing → retained) | not logged by CI (job failed before this line prints in my grep window — see below) | 1097 + 4160 existing → **5248 retained** |

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
states the limiter is "thread-safe and global per host, not per caller" —
i.e. after the migration, all 10 workers queue behind ONE shared
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
confirmed by reading that workflow file directly (its three `python
scripts/ingest_*.py` steps are AIRI/AIAAIC/OECD only).

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

*(Sections below — tripwire exception-set repro against the refreshed file,
H2 (i)/(ii)/(iv)/(v), remediation options, and the recommendation — land in
follow-up commits on this same file as they're established.)*
