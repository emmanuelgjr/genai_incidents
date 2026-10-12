# Weekly-refresh E21 tripwire, 42-row failure: diagnosis and recommendation, 2026-10-03

**Status: dated investigation record. Do not regenerate.** Measurement and
recommendation only. No data, test, or merge-heuristic change was made, and no
user decision is taken here. Author: pipeline-engineer (WS4). Work was done in
scratch worktree `ws4-refresh-tripwire-42` off `origin/main` `9604752f`. Every
live fetch went through `ingest/common.py` (invariant 5), invoked exactly as
`.github/workflows/auto-refresh.yml` invokes it. The tracked tree was restored to
clean (`git status --porcelain` empty) after each step that wrote data.

## 0. Summary

- **The tripwire is the only fatal failure.** Runs `35501009911` (2026-09-20) and
  `36310267841` (2026-09-27) both end `1 failed, 458 passed, 1 xfailed`; the one
  failure is `test_oecd_aiid_content_disagreement_is_unique_to_inc00437`. The AIRI 404
  and the OECD page 404s are not fatal (section 1).
- **The 42 rows reproduce exactly** from a fresh crawl today (identical list to the
  09-27 CI assertion, compared programmatically). 2 are the known pair (1574, 1575). The
  other 40 are **one mechanism**: OECD AIM rows carry AIID cross-references
  (`aiid_ids` -> `extra_source_ids`) for AIID ids newer than the committed AIID snapshot
  (max id 1581), so OECD's structural-template text ships under an `aiid_id`.
  **No AIID id in any of the 42 clusters is in the snapshot, so no AIID content is
  displaced.** 42/42 descriptions are byte-identical to `build_description()` rebuilt from
  the raw row's fields.
- **Classification of the 40 beyond the known pair:** N 30 (only new OECD rows) · E 7 (OECD
  rows already published, which gained an AIID cross-reference on re-fetch) · M 3 (mixed).
- **The tripwire is a symptom of two separate things.** (1) Unlabelled provenance, which
  WS4-T12 was approved to fix and has not been built. (2) A merge-side effect the tripwire
  does not measure: the same refresh writes **7 new `merged` deprecations**, retitles **4
  published stable IDs**, and adds `aiid_id` to **11 published rows**. That is D25(a)
  condition (2). I find **no board entry recording it satisfied or D25(a) rescinded**
  (section 5). The mechanism is AIID-id cross-reference bridging, not the URL query-string
  mechanism WS4-T10 fixed.
- **Recommendation: (a), in two parts; not (b).** WS4-T12 (user-approved in D25(c), not
  built) closes the provenance half. The merge half needs the user's review of the 7 merges
  before any refresh merges. Section 6.

## 1. Failing runs [R]

```
gh run view 36310267841 --log-failed ; gh run view 35501009911 --log-failed
gh run list --workflow auto-refresh.yml --limit 6 --json databaseId,conclusion,createdAt,event
```

| run | date | AIRI | OECD ingest | tests |
|---|---|---|---|---|
| 34858279213 | 09-14 | 404 | ok | 1 failed (29 rows) |
| 35501009911 | 09-20 | 404 | ok, 1429 kept | 1 failed, **30 rows** |
| 36310267841 | 09-27 | 404 | ok, 1429 kept | 1 failed, **42 rows** |

All six runs listed (back to 2026-08-30) concluded `failure`. The exception population is
**growing**, 30 on 09-20 and 42 on 09-27, and the 09-27 list is a strict superset of the
09-20 list (checked: no 09-20 id is missing from 09-27). Two data points are not a trend
line; the cause (a stale AIID snapshot) is measured, the rate is not.

Other failures in the logs, and whether each is fatal:

- **AIRI `https://www.airi-navigator.com/downloads/airi-data.zip`, HTTP 404: not fatal to
  the data path.** The step has `continue-on-error: true`. It feeds `source_health.json`:
  `origin/refresh-state` shows `airi_navigator.consecutive_failures: 11`, last success
  2026-05-31. If the job reached its end, `Enforce source health` would turn the run red; it
  never gets there because `Unit tests` fails first. See section 7.
- **OECD page 404s: not fatal.** 15 distinct date-hash slugs on 09-20 and 18 on 09-27 (for
  example `2026-09-12-7a0e`, `2026-08-06-0af1`), each retried 3 times and dropped; the step
  ends `success`. Many repeat on every run, so they are dead sitemap entries, not a
  regression.
- **`www.cisa.gov` robots.txt HTTP 403:** a conduct warning ("refusing to fetch ... until it
  can be verified") but the KEV step still wrote 1726 entries. Not fatal.
- `Ingest result summary` and `Re-merge + render + validate` pass; the D28 build guard did
  not abort. Only `Unit tests` is red.

## 2. Reproduction [R]

```
cd .claude/worktrees/ws4-refresh-tripwire-42
OECD_AIM_LIMIT=3000 python scripts/ingest_oecd_aim.py
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
python scripts/render_markdown.py && python scripts/validate.py
python -m pytest tests -q
```

| | CI 09-27 | local 10-03 |
|---|---|---|
| Sitemap URLs / cap | 10000 / 3000 | 10000 / 3000 |
| Numeric slugs skipped (WS4-T13) | 1552 | 1380 |
| Pages fetched | 1430 of 1448 | 1599 of 1620 |
| Security-relevant kept | 1429 | 1598 |
| Fetch time | 1484 s | 1668 s |
| Union with 4160 existing | 5573 | 5742 |

The columns are a week apart and the sitemap moved, so the counts differ; the comparable
quantity is the exception set. The T13 crawl budget works: 1668 s against a 60-minute job
limit, down from 3088 s on 09-14.

The tripwire population, using the test's own `_build_surviving()` logic restricted to
`aiid_full.json` + `oecd_aim_full_incidents.json`:

```
BASELINE (committed ingest):  aiid_rows 1530  exceptions [1574, 1575]
REFRESHED (today's crawl):    aiid_rows 1569  exceptions 42
  [1574, 1575, 1583, 1584, 1604, 1610, 1612, 1616, 1621, 1622, 1641, 1642, 1643, 1644, 1646,
   1647, 1650, 1654, 1655, 1658, 1659, 1660, 1661, 1662, 1665, 1666, 1668, 1669, 1671, 1673,
   1674, 1677, 1679, 1680, 1683, 1686, 1687, 1688, 1689, 1693, 1700, 1702]
```

Parsed from the 09-27 CI assertion message and compared as lists: **equal**. The local full
suite on today's rebuild: `1 failed, 475 passed, 1 xfailed`, the same single test. Full-corpus
view (rebuilt `data/incidents.json`, not the two-file scope): 43 `aiid_id` rows with a
non-AIID-template description = the 42 plus `aiid_id` 898 / `INC-08183`, the known out-of-scope
blind spot from the 09-14 audit. The published corpus today has 3 (898, 1574, 1575).

## 3. Classification of the 42 rows [R]

Method: for each exception, take the OECD source ids in its cluster and compare them with the
committed `oecd_aim_full_incidents.json` (`git show HEAD:`) and the published
`data/incidents.json`.

| class | n | meaning |
|---|---|---|
| K | 2 | Known pair: 1574 / INC-00437 (has a curation override), 1575 / INC-14682 (the WS4-T10 split, expected by the test). |
| N | 30 | Every OECD row in the cluster is new this refresh and cites AIID ids newer than the snapshot. New corpus rows. |
| E | 7 | OECD row **already in the committed ingest and already published** with no `aiid_id`. On re-fetch OECD had added an AIID cross-reference, so the published row would gain `aiid_id` and an `AIID-n` source id. 16 existing OECD rows gained a cross-reference in this refresh; 7 of them surface here. |
| M | 3 | Mixed: some OECD rows new, some pre-existing, landing on an existing published ID: 1655 (INC-00699), 1677 (INC-01514), 1686 (INC-01994). |

Against the 09-14 audit's categories: the **URL-bridge** mechanism (H3, `INC-00554`) is gone,
since WS4-T10; no row here has a non-OECD/AIID source. N is H1 (staleness) in the audit's
terms. E and M are a new shape, "existing published row retro-linked to an AIID id", that the
09-14 audit did not see because the baseline then had no OECD re-fetch of old rows.

Findings that apply to all 40:

1. **Every AIID id in every one of the 42 clusters is absent from `aiid_full.json`**
   (snapshot `backup-20260713110347`, fetched 2026-07-18, max id 1581). The audit's severe
   subclass, "real AIID-template content displaced by OECD text", has **zero** members.
2. **Licensing surface, by an independent route.** The 09-14 regex check cannot fail (its
   optional "Entities named" group accepts any prose). The route used here rebuilds each
   description with `ingest_oecd_aim.build_description(source_id, date, url, affected,
   attack_vector)` from the raw OECD row and compares **byte for byte** with the shipped
   description. **42/42 equal.** The input that would make it fail: any description containing
   a character `build_description()` did not produce, such as summary or evidence prose. So no
   OECD narrative text is on any AIID-keyed row; what ships under the AIID signal is the
   project's own template sentence (source id, date, entities, attack vector, link). OECD's
   headline also ships as `title`; titles are not covered by this check and are not assessed
   here.
3. **Provenance is not labelled.** Of the 43 full-corpus exceptions, 1 has
   `description_provenance` set (INC-00437). `grep description_provenance
   scripts/ingest_oecd_aim.py` returns nothing, so WS4-T12 (option (b), approved in D25(c)) is
   **not implemented**. WS4-T14 (add the AIID snapshot ingest to the weekly job, also approved
   in D25(c)) is not in `auto-refresh.yml` either.
4. **The driver is snapshot staleness.** OECD cites AIID ids up to 1702; the snapshot stops
   at 1581. A newer snapshot existed on 09-14 (`backup-20260907101103`). A fresh snapshot
   would shrink N and part of M, but not remove the class: whatever snapshot is current, OECD
   will cite newer ids.

### Per-row table

| aiid_id | class | OECD rows (new/pre-existing) | AIID ids in cluster | published ID |
|---|---|---|---|---|
| 1574 | K | 1 (0/1) | 1574 | INC-00437 |
| 1575 | K | 1 (0/1) | 1575 | INC-14682 |
| 1583 | E | 1 (0/1) | 1583 | INC-14362 |
| 1584 | N | 2 (2/0) | 1584 | (new row) |
| 1604 | N | 12 (12/0) | 1604,1627,1628,1629,1633,1649,1685 | (new row) |
| 1610 | N | 1 (1/0) | 1610 | (new row) |
| 1612 | N | 1 (1/0) | 1612 | (new row) |
| 1616 | N | 1 (1/0) | 1616 | (new row) |
| 1621 | N | 1 (1/0) | 1621 | (new row) |
| 1622 | N | 1 (1/0) | 1622 | (new row) |
| 1641 | N | 1 (1/0) | 1641 | (new row) |
| 1642 | N | 1 (1/0) | 1642 | (new row) |
| 1643 | N | 6 (6/0) | 1619,1643 | (new row) |
| 1644 | E | 1 (0/1) | 1644 | INC-13321 |
| 1646 | N | 2 (2/0) | 1646 | (new row) |
| 1647 | N | 2 (2/0) | 1647 | (new row) |
| 1650 | N | 1 (1/0) | 1650 | (new row) |
| 1654 | N | 1 (1/0) | 1654 | (new row) |
| 1655 | M | 12 (9/3) | 1655,1656,1657 | INC-00699 |
| 1658 | N | 1 (1/0) | 1658 | (new row) |
| 1659 | N | 2 (2/0) | 1659 | (new row) |
| 1660 | N | 1 (1/0) | 1660 | (new row) |
| 1661 | N | 1 (1/0) | 1661 | (new row) |
| 1662 | E | 1 (0/1) | 1662 | INC-07864 |
| 1665 | N | 1 (1/0) | 1665 | (new row) |
| 1666 | N | 1 (1/0) | 1666 | (new row) |
| 1668 | N | 3 (3/0) | 1668 | (new row) |
| 1669 | N | 2 (2/0) | 1669 | (new row) |
| 1671 | E | 1 (0/1) | 1671,1672 | INC-14517 |
| 1673 | E | 1 (0/1) | 1673 | INC-07910 |
| 1674 | N | 1 (1/0) | 1674,1675 | (new row) |
| 1677 | M | 3 (1/2) | 1677 | INC-01514 |
| 1679 | E | 1 (0/1) | 1679 | INC-07783 |
| 1680 | E | 1 (0/1) | 1680 | INC-00813 |
| 1683 | N | 1 (1/0) | 1683 | (new row) |
| 1686 | M | 6 (4/2) | 1686 | INC-01994 |
| 1687 | N | 1 (1/0) | 1687 | (new row) |
| 1688 | N | 1 (1/0) | 1688 | (new row) |
| 1689 | N | 2 (2/0) | 1689,1690 | (new row) |
| 1693 | N | 1 (1/0) | 1693 | (new row) |
| 1700 | N | 2 (2/0) | 1700 | (new row) |
| 1702 | N | 2 (2/0) | 1702 | (new row) |

"published ID" is the ID the row already holds in the published 13,361-row corpus; "(new row)"
means that ID does not exist there. 10 of the 40 (7 E and 3 M) sit on existing published IDs.

## 4. Is each row a real E21 licensing concern?

- **A false positive for narrative copying: all 42.** No OECD narrative ships (finding 2). The
  E21 decision (`docs/audits/E21-oecd-narrative-licence-2026-07-30.md`) reduced OECD's text to
  the project's own template; nothing here reintroduces it.
- **Real, but of a different kind: mislabelled provenance and attribution.** A row carrying
  `aiid_id` and `AIID-n` implies AIID origin. `docs/SOURCE_LICENSES.md` records attribution as
  adequate for the 1,463 to 1,464 of 1,465 AIID rows that ship AIID text and says "the two
  exceptions ship no AIID text and so owe no AIID attribution". This refresh would turn "two"
  into 42 (43 in the full corpus), so that published claim would be wrong. Whether the
  distinction needs a visible label is a licensing and public-claims question: routed, not
  decided (section 6).
- The E23 tripwire runs the other way: it reopens review if AIID's *own* text reaches the
  corpus through a merge change. Not the case here (finding 1).

## 5. Merge-side effects of the same refresh (D25(a) condition 2) [R]

Rebuilt with the refreshed ingest (`parse_existing`, `merge_and_dedupe`), compared with
`git show HEAD:data/incidents.json` and `HEAD:data/id_deprecations.json`; tree then restored.

| | published (`HEAD`) | rebuilt |
|---|---|---|
| `incident_count` | 13,361 | 14,887 |
| new-only IDs / gone | | 1,533 / 7 |
| common rows changed | | 20 (all 20 bump `updated`; invariant 4 holds) |
| `id_deprecations` records | 1,060 | 1,067 (**7 new, all `merged`**) |
| severity changes | | 4, all upward: INC-05170 M>H, INC-14517 M>H, INC-00699 H>C, INC-01514 H>C |
| `aiid_id` gained on existing rows | | 11 |
| `title` changed on published IDs | | **4** |

The four retitled stable IDs, the D25 rationale ("swaps content on stable IDs"):

| ID | published title | rebuilt title |
|---|---|---|
| INC-00699 | BMG Sues Anthropic Over AI Training With Copyrighted Song Lyrics | Record Labels Sue AI Music Generators for Copyright Infringement |
| INC-01514 | NAACP Sues xAI Over Illegal Gas Turbine Use for AI Data Center ... | xAI Data Centers Linked to Unpermitted Pollution in Mississippi and Tennessee |
| INC-01579 | OpenAI Sued After ChatGPT Advice Allegedly Leads to Fatal Overdose | California Teen Reportedly Died of Overdose After Repeatedly Seeking Drug-Use Guidance ... |
| INC-01994 | US Court Upholds $243 Million Verdict Against Tesla Over Fatal Autopilot Crash | Tesla Faces Trial Over Fatal Autopilot Crash in Florida |

The 7 new `merged` records, with my reading of each. **This is the author's judgment from
titles only. It is not the D25(a)(2) review; a human decides.**

| retired -> into | retired title | into (published title) | my reading |
|---|---|---|---|
| INC-02381 -> INC-01579 | CA teen overdose, drug-use guidance (AIID-1370) | OpenAI sued after fatal overdose | probably the same incident |
| INC-14310 -> INC-01994 | Tesla Autopilot failure and data suppression, fatal crash | $243M verdict upheld against Tesla | probably the same case, but the target is then retitled to a different case (Florida trial) |
| INC-01469 -> INC-00699 | Music publishers sue Anthropic | BMG sues Anthropic | related lawsuits; target is then retitled and absorbs 11 further OECD rows |
| INC-08148 -> INC-01628 | AI chatbots pose as licensed doctors, Pennsylvania | Digital rights groups accuse Meta and Character.AI of unlicensed therapy | doubtful: different event |
| INC-13241 -> INC-01514 | AI data centers, pollution and military operations | NAACP sues xAI over gas turbines | doubtful |
| INC-14317 -> INC-13066 | GPT-4o and Michael Lines (California) | ChatGPT and a Montreal web developer | no: different people and events (the same pair is in the 09-15 gate's "unrelated" list) |
| INC-14902 -> INC-00699 | Suno AI scraping and data breach | BMG sues Anthropic (becomes a music-lawsuit hub) | no: unrelated to the lawsuits |

**Mechanism, traced per merge rather than inferred.** For each of the 7 pairs, the retired
row's raw OECD record and the target's `source_ids` were compared. Zero of the 7 pairs share
a query-stripped reference URL. Each merge is produced by an **AIID id on an OECD row's
`extra_source_ids` acting as a dedup key**. Example: `OECD-AIM-2026-07-11-995f` (Suno) cites
`AIID-1655`, the id cited by 11 other OECD rows now clustered under `INC-00699`. OECD's own
cross-reference ("this AIID incident, many news stories") becomes a merge key across
already-published entries. This is a different mechanism from the one WS4-T10 fixed, which is
why T10 being merged does not close D25(a)(2).

**Is the freeze still in force?** The brief says the corpus unfroze at D28. What `PROGRESS.md`
says: D25(a) lists two lift conditions. D26(b) (`PROGRESS.md:1202`) records condition (1)
met (the `normalize_url` fix merging) and says "condition (2) ... still holds the freeze shut".
D28 (`PROGRESS.md:405`, `:1424`) approves the 47-split remediation and calls the corpus
unfrozen. I found **no entry recording condition (2) satisfied or D25(a) rescinded** for OECD
refresh merges. Whether D28's "unfrozen" covers refresh merges is the foreman's or user's
call, not mine.

## 6. Tripwire design and recommendation

**Name the input that makes the tripwire fail (agreement 6), and prove it fires [R]:**

```
control (committed inputs):                          [1574, 1575]          test passes
control + 1 synthetic OECD row citing AIID-9999:     [1574, 1575, 9999]    fires
```

It also fired in CI three times and locally. Inputs it **cannot** see, shown by construction:
the same synthetic row with a description beginning `AI Incident Database (AIID) entry #9999: `
followed by any prose returns `[1574, 1575]` (passes silently); rows outside the two-file scope
(`aiid_id` 898 / `INC-08183`); and the `title` field.

**Is the exact-list design right?** No. It pins a population that grew from 2 to 42 in two
weeks. It is an alarm that can only be cleared by editing the test, so it invites reflexive
edits, which is the agreement 6 failure in the other direction. The 09-14 audit (Finding 7)
already recommended replacing it with "zero unlabelled".

**Options**

- **(a) Fix in code: recommended, in two parts.**
  1. **WS4-T12 as approved in D25(c).** Set `description_provenance` / `description_source` at
     ingest on every OECD row; replace the test with a full-corpus assertion that every
     `aiid_id` row either matches the AIID template or carries a provenance label (this also
     covers 898); key the INC-00437 override to the anchor (the step-4d hazard). Add an exact
     reconstruction check as in finding 2, because a regex cannot fail. This closes the
     provenance half and makes the weekly job green on this class permanently. The 09-15 gate
     measured 3,666 published rows moving from null to a label with no `updated` bump.
  2. **A design question for the merge side, not mine to decide:** should an OECD row's AIID
     cross-reference be allowed to merge two already-published entries? Today it does, and it
     caused the 7 merges and 4 retitles above.
- **(b) Reviewed allowlist (the D28 pattern): not recommended.** 40 entries today, a user
  approval each week, and it does nothing about section 5.
- **(c) Escalation: yes, for the user-reserved items below.** Not a licensing emergency.

### What the user must decide (I decide none of these)

1. **D25(a) condition (2): review the 7 new `merged` deprecations** in section 5, or rule on
   a rule that replaces the review. Deprecations are append-only (invariant 9) and IDs are
   cited externally, so a wrong merge is permanent. Three or four of the seven look wrong to
   me.
2. **Whether D25(a) is still in force** for OECD refresh merges (section 5), because the
   record I can read does not say.
3. **Licensing and public-claims routing** (license-auditor, then the user; docs-warden for any
   README/NOTICE restatement): whether 40 more rows with an `aiid_id` and OECD-template text
   need a visible label, and what the "two exceptions" statement in `SOURCE_LICENSES` should
   say. No narrative copying is involved. CLAUDE.md protocol step 8 lists WS0-T1 outcomes
   requiring data drops or summarisation; **none arises from this finding.**
4. **Scheduling WS4-T12 and WS4-T14.** Both are approved (D25(c)) and neither is built. The
   weekly job stays red, and no refresh PR can open, until at least T12 lands.

## 7. AIRI download URL: needs a redesign, not a URL fix [R]

```
fetch_once("https://www.airi-navigator.com/downloads/airi-data.zip")                      -> HTTP 404
fetch_once("https://www.airi-navigator.com/")                                             -> 200, Next.js app
fetch_once(".../datasets"), (".../incidents/browse"), (".../about"), (".../sitemap.xml")  -> 200
```

The site has been relaunched as the "MIT AI Risk Navigator" (research-prototype banner). On
`/`, `/datasets`, `/about` and `/incidents/browse` I found **no `.zip`, `.csv` or `.xlsx`
link and no download endpoint** (pattern search over the HTML, plus a read of the `/datasets`
text: five datasets, "AI Incident Tracker, 1,497 incidents", Browse links only).
`robots.txt` allows `/` and disallows `/api/`. The incident data is embedded in a 5.2 MB
server-rendered page. The existing parser (`scripts/ingest_airi_navigator.py`, `load_incidents`
at line 85) opens a zip, so it has nothing to read; the replacement is a new ingest (page
parsing or an upstream dataset) plus a licence re-review of the new surface under AIRI's
WS0-T1 row. Data impact is limited: AIRI last succeeded 2026-05-31, `SOURCE_LICENSES` says
its rows are kept out of the shipped corpus by merge-order mechanics, and the health
registry already reports it `stale` (11 consecutive failures). **I recommend recording it as
"source relaunched; ingest needs redesign" and routing it to WS0 and WS4, not patching the
URL.** Not fixed here. I did not check whether the bulk data is published elsewhere
(for example an MIT repository), which is the first thing the redesign should settle.

## 8. Measured vs estimated

Measured [R]: all counts above (CI log excerpts; local crawl and rebuild; deltas by
`git show HEAD:` comparison; the exact-reconstruction check; the control and synthetic-row
runs; the per-merge mechanism trace; the AIRI fetches).

Judgment, not measured: the "my reading" column in section 5 (titles only, and D25(a)(2)
requires a human review); the weekly growth rate (two data points, 30 then 42, with a
measured cause but an extrapolated trend).

Not measured: the title field's licensing posture; the downstream effect of the 11 `aiid_id`
gains on the slim and STIX artifacts; `aiid_id` 898 / `INC-08183` beyond confirming it still
exists; whether AIRI's bulk data exists elsewhere.

## 9. Verification recipe for the reviewer

```
git fetch origin ws4/refresh-tripwire-42 && git worktree add <tmp> origin/ws4/refresh-tripwire-42
cd <tmp>
OECD_AIM_LIMIT=3000 python scripts/ingest_oecd_aim.py          # about 28 minutes
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
python -m pytest tests/test_e21_partA_inc00437_provenance.py -q   # fails with the exception list
git checkout -- data ingest src docs INCIDENTS.md; rm -f ingest/_state/skip_probe_state.json
```

Expect the failing list to match section 2 plus or minus rows the live sitemap has added
since 2026-10-03 (the list should only grow). To audit the 7 merges, diff
`data/id_deprecations.json` against `git show HEAD:data/id_deprecations.json`.
