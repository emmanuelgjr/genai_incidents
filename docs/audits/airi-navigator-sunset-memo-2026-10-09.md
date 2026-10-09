# AIRI Navigator sunset memo (v2.13.0 item 6)

> **Status: AGENT-SUGGESTED, 2026-10-09. DO NOT REGENERATE.** Author:
> license-auditor (WS0). This is a dated record of what was true on
> 2026-10-09, not a source. If later work overtakes it, add a dated update
> beneath this header (CLAUDE.md working agreement 4); do not rewrite the
> findings. **The retire-or-keep question is the USER'S decision. This memo
> presents options A, B1, B2 and R and recommends; it decides nothing.**
>
> Branch `ws0/v2130-airi-sunset-memo`. No data, export, schema, or licence file
> was edited. Tool constraint: this author has WebFetch (markdown-converted,
> possibly truncated) and Grep; no shell. Every count below is a ripgrep count
> over `data/incidents.json`, with an exact Python re-derivation given for the
> reviewer to run.
>
> ### Corrections before freeze (2026-10-09, gate bounce #1)
> Corrected in place because the record was not yet frozen. What changed:
> 1. Tombstone field: retraction is `status`, not `source_status`
>    (section 6; section 2 command and sentence). Added the cost that no
>    AIRI retraction reason exists today.
> 2. AIRI-sole / AIID-shared split is 0 / 1,382, not ~280 / ~1,100
>    (sections 3, 6, 8, 9, 10). B1 as defined tombstones 0 rows.
> 3. "No replacement channel" was wrong: the Navigator's own pages embed the
>    full set, and a CSV button and a ZIP link exist behind compiled-out
>    flags (section 1; new option C in section 6).
> 4. Advisories: ZIP check is one endpoint (apex 307 to www 404); the 274
>    July rows are 201 on 2026-07-18 and 73 on 2026-07-31, plus 2 September
>    rows (the first wording, "the 274 non-October rows are all July", was
>    wrong: there are 276 non-October rows; fixed at bounce #2, see below);
>    NOTICE-DATA 1,457 is the ingest-file
>    row count, accurate; CC BY no-termination clause is 6(c); no TAXII
>    landmark collection exists; HF export dumps rows verbatim so no
>    features list; hold lapsed 42 days; Terms of Use read; airisk
>    robots.txt has no Disallow; eu-ai-act-* rows today are 1,382, all AIRI.
>
> ### Corrections at gate bounce #2 (2026-10-09, D54, fresh author)
> Gate bounce #1's note above listed corrections that the body did not all
> carry. A fresh author (license-auditor, no shell) re-read the whole memo and
> made these changes in place (record not yet frozen). Line numbers are those
> of the file at tip 3e8ed477 (before this pass); section numbers are stable.
> 1. `tier: landmark` is not AIRI-derived (was lines ~171, 241-248, 446;
>    now sections 2, 3, 6, 9 check 6, 10 item 2). `_derive_tier`
>    (`scripts/merge_and_dedupe.py:163-187`) returns landmark iff
>    `quality_tier == "curated"` OR `aiid_id` present OR `corpus == "ai-harm"`;
>    all 1,382 AIRI rows carry `aiid_id` via `ingest/aiid_full.json`. B1 moves
>    0 rows out of landmark (stays 1,915); the former "1,915 -> as low as 533"
>    for B1 is deleted. B2 re-checked: 1,915 - 1,382 = 533 is correct because
>    the rows are tombstoned, and is kept (arithmetic from the 1,382 landmark
>    rows and the 1,915 corpus figure; reviewer to confirm with the section 2
>    Python). The "is tier AIRI-derived?" user question is removed.
> 2. Option C gap (was lines ~61, 67-70, 302, and section 9 check 4): the
>    "~41 rows" is withdrawn. red-reviewer measured (curl + node, 2026-10-09):
>    1,497 record objects, 1,496 distinct ids (id 1378 duplicated); 40 ids not
>    among the 1,456 AIRI ingest keys; 39 of those already in the corpus via
>    `ingest/aiid_full.json`; only AIID-1474 absent. C adds at most 1 row plus
>    the AIRI overlay on 39 existing rows.
> 3. Section 1 (was lines 52-55, 46, 35, 49): the "found none; the only
>    adjacent public channel is AIID's snapshots" sentence is rewritten
>    (consistent with the browse-page conclusion; the mirror search is marked
>    absence-based and method-suspect); the Privacy & Terms row no longer says
>    "not retrieved" (it is the Terms chunk quoted above it); the "NOT raw
>    HTML" blanket statement now says which rows are rendered, which raw JS;
>    the airisk robots row states it rests on the foreman's raw check.
> 4. Attributions: "never hand-authored" is cited to DATA_DICTIONARY line 17
>    and also schema line 216 (both carry the sentence; was schema only);
>    the 0 / 1,382 split is credited to red-reviewer at gate #1, re-checked by
>    the foreman (was "the foreman measured").
> 5. Bounce #1 note item 4 itself corrected: "274 non-October rows are all
>    July" was false (276 non-October rows: 274 July, 2 September).
>
> ### Corrections at gate bounce #3 (2026-10-09, D56)
> Made in place by the same no-shell author, scoped to the gate's defects.
> Line numbers are those of the file at tip cac1724c (before this pass).
> Note on naming: the earlier logs above (bounce #1 item 3, bounce #2 item 2)
> still say "option C"; that is the option now named **R (re-ingest)**. It was
> renamed because PROGRESS.md records D8 as "AIRI: HOLD (option C)", a
> different thing. The old logs are left as written.
> 1. `last_seen`/`updated` is the content-change date, not the rebuild date
>    (was line 165 table header "build/refresh date"; lines 173-174 "touched
>    by a rebuild"; lines 291-292 Option A risk "re-emitting with last_seen =
>    rebuild date"). Sources read: DATA_DICTIONARY.md:21 ("last-content-change
>    dates (content-gated, so unchanged entries don't churn)"); `_apply_history`
>    `scripts/merge_and_dedupe.py:1484-1502` (keeps `prev_updated` when the
>    content snapshot is unchanged); `last_seen = updated` at :2363. Conclusion
>    kept: 1,106 rows carry a date after the feed died and can be read as fresh.
> 2. `intentional` is a tag, not a field (was lines 219, 236, 306). Now
>    "`intentional` tag (672 rows today, all AIRI; ~667 by E18)", 0 rows have an
>    `intentional` key (foreman-measured, not re-run by me). Deployment-stage
>    tag now "1,382 rows today: ai-post-deployment 1,348, ai-pre-deployment 26,
>    ai-other 9 (tag occurrences, total 1,383, one row carries two); 1,380 at
>    E18". B1's strip list (line 305-306 and §3 line 235-236) now also names
>    the `airi-navigator` tag, the `source_freshness` marker and the
>    airi-navigator.com references, with `severity` marked "possibly; the dry
>    run decides". "Subject to the dry run" kept.
> 3. Advisories: §7 item 6 lists all three min mirrors (adds
>    `data/incidents.min.json`); the header says options A, B1, B2 and R (was
>    "both options"); §3 and §9 check 6 use `source_id` for the ingest files
>    and `source_ids` for corpus rows (checked in the ingest files and
>    `scripts/ingest_airi_navigator.py:139`); §7 selector and the §2 Python use
>    `eu-ai-act-` with the hyphen, because INC-02549 (feed tier, non-AIRI)
>    carries a bare `eu-ai-act` tag (foreman-confirmed, not re-checked by me);
>    §2 now names the axes for "active 15,657" (`source_status`) versus
>    "15,637 active" (`status` / `incident_count`); changelog and
>    `ALLOW_DOWNLOAD` claims are labelled foreman testimony, unconfirmed on the
>    live site 2026-10-09 (`/changelog` returns 404; flag name in no chunk),
>    with the compiled-out gates stated as the verified part.

## 1. Channel status (evidence)

All fetches 2026-10-09 via WebFetch, whose output is markdown-converted and
possibly truncated. What that means per row is stated in the "Kind of source"
column: HTML pages are rendered/markdown text (NOT raw HTML); the three
`/_next/static/chunks/` rows are raw JS source; robots.txt is plain text; the
ZIP row is a status line; the `/incidents/browse` row is not my fetch.

| URL | What was seen | Kind of source |
|---|---|---|
| `https://airi-navigator.com/robots.txt` | `User-Agent: *`, `Allow: /`; `Disallow:` `/embed/`, `/admin`, `/login`, `/design-system`, `/api/`; `Sitemap: https://www.airi-navigator.com/sitemap.xml`. Identical to the rule set recorded in SOURCE_LICENSES 1.4 (2026-07-16). | text file, low truncation risk |
| `https://airi-navigator.com/downloads/airi-data.zip` and `https://www.airi-navigator.com/downloads/airi-data.zip` (the `ZIP_URL` in `scripts/ingest_airi_navigator.py:34`) | HTTP 404. This is ONE endpoint, not two: the apex redirects (307) to www, which 404s. | status line |
| `https://www.airi-navigator.com/datasets` | Lists "AI Incident Tracker: 1,497 incidents" (AIID-derived), v1.3.2; no download or licence text. | rendered fetch |
| `https://www.airi-navigator.com/incidents/browse` (robots-allowed) | Not re-fetched by me (5 MB, beyond my tool). Foreman-reproduced and red-reviewer-measured (curl + node, 2026-10-09): HTTP 200, 5,262,949 bytes, embeds the full set (1,497 `euAiActRiskLevel` occurrences = 1,497 record objects, 1,496 distinct ids with id 1378 duplicated; latest date 2026-05-31). | raw HTML, foreman/red-reviewer measurement |
| JS chunk `/_next/static/chunks/b5439732ff8b66e8.js` | Contains `DownloadResultsButton` ("Download results as CSV", client-side Blob, filename `airi-<key>-...csv`). **I read it: the component is gated by `u="FALSE".toUpperCase()!=="FALSE"` and returns null when false, so as shipped the CSV button renders nothing.** Changelog v1.2.9 (2026-04-29) introduced it (foreman testimony; unconfirmed on the live site 2026-10-09: `/changelog` returns 404). | raw JS via WebFetch |
| JS chunk `/_next/static/chunks/906798798b22d561.js` | Footer "Download data" links to `/downloads/airi-data.zip`, wrapped in the same compiled-out `"FALSE".toUpperCase()!=="FALSE"` comparison (both mobile and desktop). The flag NAME `ALLOW_DOWNLOAD` did not appear in my fetch and the reviewer found it in no chunk; the foreman reports it from the changelog (0.29.1), foreman testimony, unconfirmed on the live site 2026-10-09 (`/changelog` returns 404). The compiled-out gates themselves are verified; that they are a deliberate switch-off is an inference from them. | raw JS via WebFetch |
| JS chunk `/_next/static/chunks/fdfcd250c3d32eb2.js` (Terms of Use) | "The data presented on this site is drawn from the MIT AI Risk Repository and related research datasets. It is provided as-is for informational and research purposes. While we strive for accuracy, we make no guarantees regarding completeness or timeliness." No licence clause. | raw JS via WebFetch |
| `https://www.airi-navigator.com/` | "MIT AI Risk Navigator", described as a research prototype whose "data and analyses are preliminary and not yet validated"; v1.3.2; latest listed incident dated 2026-05-31; no download/export/API link, no GitHub/HF/Zenodo link; a "Privacy & Terms" link, whose content is the Terms chunk quoted in the row above. | rendered fetch, absence-based (method-suspect; the footer and browse-page findings above show a rendered fetch missed channels) |
| `https://airisk.mit.edu/` | No data-download, Google Sheet, HF, Zenodo or GitHub link. Footer: "Data from the MIT AI Risk Initiative is licensed under CC BY 4.0" (link `creativecommons.org/licenses/by/4.0/`). | rendered fetch; the licence line matches the raw-HTML finding in SOURCE_LICENSES 1.4 |
| `https://airisk.mit.edu/ai-incident-tracker` | Dashboards only ("classifies 1,600 real-world report incidents"); links to AIID; no download/export link. A path `/old-ai-incident-tracker/incident-view` also exists (search result; not fetched). | rendered fetch, absence-based |
| `https://airisk.mit.edu/robots.txt` | My fetch summary reported only `Sitemap: https://airisk.mit.edu/sitemap.xml` (no Disallow). The no-Disallow finding was closed by the foreman's raw check (not mine), which matched. | my fetch: rendered summary; closing check: raw, foreman |
| `https://www.airi-navigator.com/api/*` | **Not fetched: robots-disallowed.** Recorded as disallowed, per instruction. | -- |

Web search for a third-party mirror (HF / Zenodo / GitHub / Google Sheets)
found none; this is search-engine based and absence-based, so it is
method-suspect (section 9, check 3). It does NOT mean no channel exists: the
Navigator's own `/incidents/browse` page embeds the data (row above;
conclusion below), and the CSV button exists behind a compiled-out flag. AIID's
own weekly snapshots (`incidentdatabase.ai/research/snapshots`,
JSON/MongoDB/CSV) are a separate source that carries the AIID fields, not
AIRI's taxonomy overlay.

**Conclusion (corrected): the advertised ZIP is withdrawn and was switched off
on purpose (404; the footer link and the CSV button are both compiled out by a
build-time flag). It is NOT true that no other channel exists.** The
Navigator's own robots-allowed page `/incidents/browse` ships the entire
incident set embedded in its HTML/JS payload (5.26 MB; 1,497 record objects,
1,496 distinct ids; latest
date 2026-05-31, so the dataset itself looks frozen at the same date as our
`last_success`). My first version of this memo said "no replacement bulk
channel" from rendered fetches; that was the absence-based false negative the
standing rule warns about, and raw HTML refuted it.

Gap (corrected at gate bounce #2): the page embeds 1,497 record objects
(1,496 distinct ids; id 1378 appears twice); our committed ingest holds 1,456
distinct AIID keys (1,457 rows). red-reviewer measured (curl + node over the
embedded data, 2026-10-09): 40 ids are not among the ingest keys; 39 of those
40 are already in the corpus via `ingest/aiid_full.json`; only AIID-1474 is
absent from the corpus. The earlier "about 41 incidents we never ingested" was
the raw 1,497 - 1,456 subtraction, which ignores the duplicate id and the
AIID-sourced coverage, and is withdrawn. (Not derived by me; reviewer's
figure. Reviewer: re-run by a different method.)

What this channel is NOT: not a licensed, sanctioned bulk export. Whether
reading data out of a page payload, or the (currently hidden) per-view CSV
button, is within the Terms ("provided as-is for informational and research
purposes", no licence clause) or the maintainers' evident intent (they
withdrew the ZIP deliberately) is a conduct/licence question for the user, not
a technical one. The data licence is CC BY 4.0 at airisk.mit.edu either way.
The robots rules allow `/incidents/browse` and disallow only `/api/`. I do not
recommend scraping; I only record the channel exists.

Closed items from the first version: (b) the Terms of Use text is read (above;
no licence clause); (c) the airisk.mit.edu robots.txt has no Disallow (per the
foreman's raw check, matching my summarised one). Still method-suspect and
routed to red-reviewer (section 9): any claim of absence of a GitHub / HF /
Zenodo / Google Sheets mirror (search-engine based).

## 2. Count and distribution

**1,382 rows** carry the `airi-navigator` tag in `data/incidents.json`
(corpus 15,637 active at v2.12.0). Not 1,380. The 1,380 figure is the
v2.9.0-era count (CHANGELOG line 392; the E18 BOUNCE note computes it as the
`eu-ai-act-*` tier-tag set; it was right then). The premise check
(`docs/audits/v2.13.0-premise-check-2026-10-06.md`, row 6) already found 1,382.
Count by ripgrep: tag `"airi-navigator"` 1,382 lines; per-row marker
`"airi_navigator"` 1,382 lines (marker and tag coincide).

Re-derivation (reviewer to run, from repo root):

```
python -I -c "import json,collections as C;d=json.load(open('data/incidents.json',encoding='utf-8'));r=[e for e in d['incidents'] if 'airi-navigator' in (e.get('tags') or [])];print(len(r));print(sum(1 for e in r if 'airi_navigator' in (e.get('source_freshness') or {}).get('sources',[])));print(C.Counter(e.get('tier') for e in r));print(C.Counter(e.get('last_seen') for e in r).most_common());print(C.Counter(e.get('source_status') for e in r));print(C.Counter(e.get('status') for e in r));print(sum(1 for e in r if any(t.startswith('eu-ai-act-') for t in e['tags'])))"
```

(If the top-level key is not `incidents`, the first line of the file is a
dict with `version`, `generated`, `incident_count`; use the list key that
follows.) Expected: 1382; 1382; `{'landmark': 1382}`; `source_status` all
`active` or `retained` (corpus-wide per the foreman, on the `source_status`
axis: active 15,657, retained 9, which sums to 15,666 = 15,637 active +
29 retracted on the separate `status` / `incident_count` axis); `status` `{None: 1382}` (retraction is the `status` field, corpus-wide 29
`retracted`, 0 on AIRI rows); eu-ai-act-* rows 1382.

Distribution (ripgrep, multiline over the tags-to-`last_seen` span of each
entry, equal totals as a cross-check):

| `last_seen` (= `updated`, the content-change date: content-gated, bumps when any field changes in a rebuild, not when the upstream source supplies data) | Rows |
|---|---|
| 2026-10-06 | 1,106 |
| 2026-09-xx | 2 |
| 2026-07-xx | 274 (foreman: 201 on 2026-07-18, 73 on 2026-07-31) |
| total | 1,382 |

**Observation that matters for the tagging spec:** `last_seen` is documented
as an alias of `updated` (DATA_DICTIONARY line 22). `updated` is the
content-change date (DATA_DICTIONARY line 21: "last-content-change dates
(content-gated, so unchanged entries don't churn)"; `_apply_history`,
`scripts/merge_and_dedupe.py:1484-1502`, keeps the previous `updated` when the
content snapshot is unchanged and sets today otherwise; `last_seen = updated`
at :2363). It bumps when any field of the row changes in a rebuild, not when
the upstream source supplies data. 1,106 of these frozen rows nonetheless
carry a date (`2026-10-06`) after the feed died, four months after
`as_of`, so consumers filtering on `last_seen` can read them as fresh. The only truthful date is
`source_freshness.as_of = 2026-05-31`.

**Landmarks:** all 1,382 carry `"tier": "landmark"` (ripgrep: 1,382 matches for
tag-then-landmark within the entry; 0 matches for tag-then-non-landmark;
whole-corpus landmark count 1,915). So the frozen AIRI rows are about 72% of
the landmark tier (1,382 of 1,915). **Any landmark feed (`x_tier`, Pages
landmark view; TAXII has a single collection, `export_taxii.py:48`, so no
separate TAXII landmark feed exists) is therefore predominantly
stale-source data.** This raises the stakes of removing the rows (B2), not of
stripping the overlay (B1). Reviewer must confirm with the Python above.

**Why they are landmark (corrected at gate bounce #2): not because of AIRI.**
`tier` is derived by `_derive_tier` (`scripts/merge_and_dedupe.py:163-187`,
the definition of record; machine-readable twin in
`schema/incident.schema.json` `tier` `x-derivation`, ~line 182): landmark iff
`quality_tier == "curated"` OR `aiid_id` is present OR `corpus == "ai-harm"`.
All 1,382 AIRI rows carry `aiid_id`, supplied by `ingest/aiid_full.json`
(`aiid_id` on 1,548 of 1,548 rows); `ingest/airi_navigator_incidents.json`
carries it on 0 of 1,457. The AIRI overlay therefore contributes nothing to
the tier, and the AIRI rows are landmark for the same reason every AIID row
is. Source of this finding: the code and ingest files read by this author
(Read/Grep); the 0/1,457 and 1,548/1,548 counts are the foreman's
confirmed figures, not re-run by me (no shell); reviewer: re-run.

Retraction: none of the AIRI rows is retracted. The field to test is
`status` (DATA_DICTIONARY line 17: "this is not `source_status`"), which is
absent on all 1,382. My first version tested `source_status`, an
emission enum `{active, retained}` that cannot hold "retracted", so that check
could not fail; replaced.

## 3. What the rows are and how they are used

- Source file: `ingest/airi_navigator_incidents.json`, a COMMITTED SNAPSHOT
  re-fed on every build (registry note). Frozen, not broken.
- They are mostly AIID incidents wrapped by AIRI: the AIID #1 row (`aiid_id: 1`) has tag
  `aiid` plus `airi-navigator`, `source_ids: ["AIID-n"]`, a reference to
  `airi-navigator.com/incidents/<n>`, and AIRI-derived tags
  (`eu-ai-act-*`, `mit-risk-domain:*`, deployment-stage tags). Titles are
  AIID's own (E23 tripwire test: AIRI's composed title must not ship;
  `tests/test_e23_aiid_dead_letter_tripwire.py`); AIRI descriptions match on 0
  rows and `affected` on 0 (E18 BOUNCE note).
- AIRI-derived content that ships: EU AI Act tier tags (1,382 rows today,
  all AIRI; 1,380 by the older E18 measure), deployment-stage tag (1,382 rows
  today: `ai-post-deployment` 1,348, `ai-pre-deployment` 26, `ai-other` 9, as
  tag occurrences, which total 1,383, so one row carries two of them; 1,380 at
  E18), `intentional` tag (672 rows today, all AIRI; ~667 by E18; it is a tag,
  not a field: 0 rows have an `intentional` key), `severity` (798) -- the 672,
  the 0 and the per-tag counts are foreman-measured; the E18 figures and 798
  are E10 / E18 testimony; none re-measured here.
- AIRI-sole vs AIID-shared (corrected): **0 AIRI-sole / 1,382 AIID-shared
  today.** red-reviewer measured at gate #1 (and the foreman re-checked) that all 1,456 distinct AIRI `source_id` values in
  `ingest/airi_navigator_incidents.json` (1,457 rows; ids are `AIID-n`; ingest
  rows use the singular `source_id`, corpus rows the list `source_ids`) are
  present in `ingest/aiid_full.json` union `ingest/aiid_incidents.json`
  (`len(airi_keys - aiid_keys) == 0`). The earlier "~280 AIRI-sole / ~1,100
  shared" (PROGRESS line 1953) predates the 2026-07-18 official AIID snapshot
  replacing `aiid_full` (commit 8e624ba7); I repeated that testimony in my
  first version without re-measuring and it is superseded. I read the
  retention code (`scripts/merge_and_dedupe.py:2205-2233`): a prior entry is
  carried only if none of its keys is covered by fresh entries, so AIRI-keyed
  priors covered by AIID are not retained. Command (reviewer): load both
  ingest files, collect `source_id`, assert the set difference is empty; the
  logic is key coverage, **not a simulated build** -- a real dry-run of the
  merge without the AIRI file is the stronger check and should be run.
  Consequence: removing AIRI would remove the AIRI OVERLAY (`eu-ai-act-*` tags,
  deployment-stage tags, the `intentional` tag, the `airi-navigator` tag, the
  `source_freshness` marker, the airi-navigator.com references, and possibly
  `severity` -- the dry run decides) from all 1,382 rows and tombstone none
  (subject to that dry run). `tier: landmark` is
  NOT part of the overlay (section 2).
- Surfaces carrying them: `data/incidents.json`, the three min mirrors,
  `INCIDENTS.md` / `docs/incidents/*`, STIX bundle, TAXII static files, MISP
  feed, HF dataset, Pages site. HF already emits the per-row `source_freshness`
  object (`scripts/export_huggingface.py`, card text lines ~111-130); STIX and
  MISP carry nothing (confirmed by premise check and a grep of
  `scripts/export_stix.py` / `export_misp.py`).

## 4. Licence position

Facts from `docs/SOURCE_LICENSES.md` section 1.4 (not re-fetched in full by me;
airisk.mit.edu footer re-seen today in rendered form):

- AIRI's own data: **CC BY 4.0**, established at `airisk.mit.edu` footer and
  JSON-LD (raw-HTML confirmed 2026-07-16 and again by red-reviewer 2026-07-29).
  Today's fetch shows the same sentence. Caveat: the grant is stated on the
  MIT AI Risk Initiative site; the link to the Navigator's former ZIP is a
  one-hop inference via the Navigator's Terms-of-Use modal.
- Scrape/crawl: robots.txt permits everything except `/api/` and four admin
  paths. The ZIP path was never disallowed; it is simply gone.
- Redistribute/relicense: compatible for AIRI's own CC BY 4.0 data with
  attribution. **UNKNOWN** for AIID-derived fields AIRI wraps (does AIID's
  CC BY-SA share-alike apply transitively). Outreach sent 2026-07-27
  (courtesy, Spencer Michaels) and 2026-07-29 (`airisk@mit.edu`, substantive).
  I found no recorded MIT reply in the files read; the user knows whether one
  arrived.
- NOTICE-DATA lines 198-207 cite **1,457** AIRI rows. That is the ingest-file
  row count (1,457 rows merging into 1,382 corpus entries), so it is accurate;
  no discrepancy. (Earlier flagged as unresolved; withdrawn.)
- Navigator Terms of Use (read from JS chunk, section 1): "provided as-is for
  informational and research purposes"; no licence clause. The licence rests
  on the airisk.mit.edu CC BY 4.0 statement, not on the Navigator's own terms.

**May frozen rows stay?** On the licence record, yes: a CC BY 4.0 grant
already exercised does not depend on the licensor continuing to host the file
(my understanding, from CC's published position that CC licences are
irrevocable for recipients who comply; **not re-fetched today -- reviewer to
confirm from the legalcode, section 6(c), the no-termination/no-revocation clause**). Attribution is already
carried (reference to airi-navigator.com/incidents/n; NOTICE-DATA). The only
open licence risk is the transitive-AIID question, which is independent of
frozen-vs-refreshed and is the same under both options. **No licence fact
found forces retirement.** Conservative note: the Navigator now labels its
data "preliminary and not yet validated", a quality statement, not a licence
term.

## 5. Option A: keep rows frozen, tagged stale, with a review_by date

- Counts: unchanged (15,637 active; 1,382 AIRI-tagged). Nothing tombstoned.
- Exports: STIX/MISP gain the stale marker (spec section 7); HF already has
  it, gains `review_by`. Landmark feed continues to include these rows, now
  visibly marked.
- Citations: unchanged; per-row AIRI reference stays. No ID change.
- Downstream consumers: no breakage. New optional fields are additive.
- Risks: 1,106 of the rows carry a `last_seen` (content-change date) of
  2026-10-06, after the feed died, so non-marker-aware consumers can read them
  as fresh. The marker is the only
  signal. Frozen EU-AI-Act tags age silently. A review_by date turns an
  indefinite hold into a dated one (the D8 hold, `until 2026-08-28`, has
  already lapsed 42 days, 2026-08-28 to 2026-10-09 counting the lapse date
  as day 0, with no recorded decision; the registry is currently internally
  stale on its own hold).
- Reversible: yes, completely.

## 6. Option B: sunset / retire (status + tombstone; never delete; IDs append-only)

Sub-options (corrected: the population is 0 AIRI-sole / 1,382 AIID-shared, so
the earlier "tombstone ~280, strip ~1,100" split does not exist):

- **B1 (overlay strip):** remove the AIRI overlay only (`eu-ai-act-*` tags,
  deployment-stage tags, the `intentional` tag, the `airi-navigator` tag, the
  `source_freshness` marker, the airi-navigator.com references, and possibly
  `severity` where AIRI-supplied -- the dry run decides) from all 1,382 rows; keep the rows, which the AIID snapshot path still serves. **As
  defined this tombstones 0 rows** (subject to the dry-run in section 3). The
  rows stay `active`, the count is unchanged, and the cost is a field-level
  change on 1,382 rows. **Landmark: B1 moves 0 rows out of the landmark tier
  (stays 1,915).** `tier` is not AIRI-derived: `_derive_tier`
  (`scripts/merge_and_dedupe.py:163-187`, the definition of record; schema
  `tier` `x-derivation`, `schema/incident.schema.json` ~line 182) returns
  landmark iff `quality_tier == "curated"` OR `aiid_id` present OR
  `corpus == "ai-harm"`. All 1,382 AIRI rows carry `aiid_id` (supplied by
  `ingest/aiid_full.json`, which has it on 1,548 of 1,548 rows;
  `ingest/airi_navigator_incidents.json` has it on 0 of 1,457), so stripping
  the AIRI overlay leaves the condition true on every row.
- **B2 (full):** tombstone all 1,382 rows. Because every row is also an AIID
  row, B2 additionally discards AIID-served incidents; that goes beyond
  "sunsetting AIRI" and is the harshest reading. Landmark: unlike B1, B2 does
  remove 1,382 rows from the active landmark tier (1,915 -> 533), because the
  rows themselves are gone, not because their tier changed.
- **R (re-ingest via the Navigator's embedded data; formerly "Option C",
  renamed at bounce #3 to avoid confusion with PROGRESS.md's D8 "AIRI: HOLD
  (option C)", a different thing):** see below.

Consequences:

- Counts: B2 drops the active count by up to 1,382 (15,637 -> 14,255) and
  adds 1,382 retracted (29 -> 1,411); B1 changes no count. The retracted figure
  in docs (15,637 + 29 retracted at v2.12.0) must be restated everywhere counts
  are claimed (README, site, DATASHEET, HF card, Zenodo, CITATION). Counts are
  a load-bearing public claim; docs-warden sweep required.
- Landmarks: B2 removes 1,382 of 1,915 landmarks (72%). The landmark feed
  would shrink to 533. This is the largest consumer-visible effect and weighs
  heavily against B2.
- Tombstone mechanics (Invariant 3), B2 only: retraction is the `status`
  field, NOT `source_status` (DATA_DICTIONARY line 17; `source_status` is the
  emission enum `{active, retained}` and `schema/incident.schema.json:209-213`
  forbids a third value). **Missing cost: `status: retracted` is defined today
  only as "every CVE the entry carries is REJECTED", derived from
  `ingest/cve_rejections.json` and "never hand-authored"
  (DATA_DICTIONARY line 17; the same sentence is at
  `schema/incident.schema.json:216`). Retiring AIRI rows needs a NEW retraction reason and a
  new derivation (a `status_reason.code` value added together with its schema
  enum, DATA_DICTIONARY row and a `validate.py` rule, per the vocabulary rule
  at DATA_DICTIONARY line 18), plus the `incident_count`/`retracted_count`
  and feed-omission behaviour that rides on `status`. That is schema-architect
  plus pipeline-engineer work, not a data edit.** IDs stay allocated; no row
  deleted; `ingest/airi_navigator_incidents.json` stays committed. The merge
  must not re-activate them (the committed ingest file re-feeds the rows every
  build), so retirement needs an explicit mechanism, a pipeline requirement.
- Field-level changes on the 1,382 rows (B1) are a transformative data
  operation: full before/after delta required (working agreement 2).
- Citations: any external citation of an INC id keeps resolving (tombstone),
  but its content is gone from active views. Consumers who joined on AIRI
  tags (`eu-ai-act-*`) lose the tag on every affected row (all 1,382, all
  AIRI).
- Downstream: STIX consumers see revoked/absent objects; TAXII static files
  and MISP events change; HF row counts change and need a new dataset
  version. All are breaking for pinned consumers, and a major/minor release
  decision (user).
- Licence: retirement does not reduce licence risk on AIID-sourced text, which
  stays via the AIID snapshot path either way.
- Reversible: tombstones are reversible only by a deliberate un-retraction;
  the public-record effect (DOI'd Zenodo versions, HF revisions) is not.

### Option R (re-ingest): refresh from the Navigator's embedded data (sub-option; user's call)

What it is: re-ingest from the data the robots-allowed `/incidents/browse`
page embeds (1,497 record objects, 1,496 distinct ids, latest 2026-05-31), or
from the CSV button if it is ever re-enabled, instead of the dead ZIP.
Effects (red-reviewer measurement, curl + node over the page's embedded data,
2026-10-09): 40 of the 1,496 ids are not among our 1,456 AIRI ingest keys; 39
of those 40 are already in the corpus via `ingest/aiid_full.json`; only
AIID-1474 is absent. So R would add **at most 1 new row**, plus the AIRI
overlay (`eu-ai-act-*` tags and the like) on the 39 existing rows. Nothing
newer exists (the source looks frozen at 2026-05-31), so `last_success` would
barely move and the rows would still be correctly `stale`-eligible; a new
ingest script and a new test set are needed (pipeline-engineer) for a gain of
one row and 39 overlays, and the count change is at most 1 row (docs-warden
sweep). Conduct and licence questions I cannot resolve and
will not resolve in the project's favour:
- Extracting a 5 MB page payload is not the sanctioned export the maintainers
  withdrew; they switched off both the ZIP link and the CSV button by build
  flag, which reads as intent. Our outreach to MIT (2026-07-29) asked for a
  sanctioned export and has no recorded reply.
- Terms of Use give no licence and say "as-is for informational and research
  purposes"; the CC BY 4.0 statement is on airisk.mit.edu, one hop away.
- robots.txt allows `/incidents/browse` and disallows `/api/`; allowed is not
  the same as invited.
- The transitive-AIID share-alike question (open since 2026-07) would apply
  to the new rows as well.
I make no recommendation to scrape. Whether Option R is acceptable, or should
wait for MIT's reply, is the user's decision. Options A and B1 do not depend on
it; if R were taken, A's wording changes from "frozen" to "refreshed once, then
frozen at 2026-05-31".

## 7. Implementation spec for stale tagging and review_by (for the later specialist; applies to Option A, and to Option B1/B2 for any surviving rows)

Which rows: exactly the entries whose `source_freshness.sources` contains
`airi_navigator` (today 1,382; selector is the registry `row_marker`
`{kind: tag, value: airi-navigator}`). Do not select by `last_seen`. Do not
select by title text. Do not select by tag prefix with
`startswith('eu-ai-act')`: INC-02549 (feed tier, non-AIRI) carries a bare
`eu-ai-act` tag (foreman-confirmed); use the row marker, or the prefix
`eu-ai-act-` WITH the hyphen. Derive from the per-row marker, never author per
row.

Tag values:
- status: `stale` (marker `status`)
- as_of: `2026-05-31` (marker `as_of`, from `last_success`)
- sources: `["airi_navigator"]`
- review_by: the date the user picks (section 10); until chosen, omit.

Surfaces:

1. **Registry `data/source_freshness.json` + `schema/source_freshness.schema.json`
   (+ `docs/DATA_DICTIONARY.md` Source freshness section):** add optional
   `review_by` (string, pattern `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`) to the `source`
   `$def`, sibling of `hold`. Meaning: date by which a human must re-decide
   this stale source; distinct from `hold.until` (decision deadline for a
   named decision). Description must say it is declarative and never
   wall-clock-evaluated by the build. Set it on `airi_navigator`. Also
   refresh the lapsed `hold.until` text with a dated note, since it passed on
   2026-08-28. Rule for the pipeline engineer: **no wall-clock comparison in
   `make build`** (deterministic path); an overdue `review_by` is checked by a
   separate scheduled workflow/script that opens an alert, mirroring
   `check_source_health.py`. Require `review_by` whenever `status == stale`
   (a validate.py check that uses only registry content, no date maths).
2. **Per-row marker (`schema/incident.schema.json` `source_freshness`, 
   `merge_and_dedupe.py` ~2349-2404, slim item ~2721):** propagate
   `review_by` as the minimum `review_by` among the entry's stale sources
   (parallel to `as_of` = min `last_success`), because STIX/MISP consumers
   cannot see the registry. Update the `validate.py` marker cross-check
   (~line 552-595) to verify it.
3. **STIX (`scripts/export_stix.py`, SDO dict ~lines 173-207):** on each
   incident SDO whose entry has a marker, emit
   `x_source_freshness: {"status": ..., "as_of": ..., "sources": [...], "review_by": ...}`
   conditionally (absent on unmarked rows, never `null`), the same pattern as
   `x_content_license`. Do not push it into `labels`. Exact set match with the
   data file (add a test asserting emitted count == marked count == 1,382).
   Regenerate TAXII static files (`export_taxii.py` re-serves the bundle) and
   confirm the objects carry the property. The identity SDO may additionally
   state the registry summary, optional.
4. **MISP (`scripts/export_misp.py`, `_incident_tags` ~76-95):** add
   machinetags `genai-incidents:source-freshness="stale"` and
   `genai-incidents:source-as-of="2026-05-31"` (and
   `genai-incidents:source-review-by="<date>"` when set) on the incident
   attributes of marked rows only. Rows are attributes within per-year
   events, so tag at attribute level, not event level. Update the feed README
   string (~231-250).
5. **HF (`scripts/export_huggingface.py`, card text ~108-130):** the export
   dumps rows verbatim (lines ~194-214), so there is no features list and
   `review_by` carries through automatically once the per-row marker has it.
   Work is limited to the card paragraph (add `review_by` to the
   `{status, as_of, sources}` description) and a test that the HF row carries
   it. Confirm the card says rows are frozen as of `as_of`. HF repo is `genai-incidents` (hyphen).
6. **Docs/mirrors:** the three min mirrors, `data/incidents.min.json`,
   `docs/data/incidents.min.json` and
   `src/genai_incidents/data/incidents.min.json`, already carry the marker via
   the slim path; confirm `review_by` rides along. README/DATASHEET wording
   about freshness and the landmark feed note.
7. **Tests that must fail on corruption** (working agreement 6): drop the
   marker from one AIRI row in a fixture -> STIX/MISP count test fails;
   mark one non-AIRI row -> fails; mismatched `as_of` -> fails.

Field-level delta (agreement 2): intended delta is additive only (STIX
`x_source_freshness`, MISP tags, `review_by` in registry and marker); entry
count and ID set must be identical before/after; any other field change is a
defect.

## 8. Recommendation (agent-suggested; the decision is the user's)

Choose **Option A now**, set a `review_by` of roughly 90 days out (a
user-set date; suggestion 2027-01-07), and keep B1 as a pre-scoped
alternative for the next review. Option R is raised for the user's decision,
not recommended; nothing in A depends on it. Reasons: (1) no licence fact
forces retirement; (2) 72% of the landmark tier is AIRI-tagged, so B2 would
gut the landmark feed, while stale-marking is reversible and honest; (3) every
AIRI row is also an AIID row (0 AIRI-sole), so the incident identities are
served regardless and what is at stake is the AIRI overlay, which a marker
plus an as-of date already flags; B2 would also need a new retraction reason
(schema work) to remove incidents that are not AIRI's; (4) the lapsed 2026-08-28 hold shows an undated
"hold" decays, so the fix is a dated `review_by`, not retirement; (5) the real
open licence question (transitive AIID share-alike) is orthogonal to
the choice and should be chased with MIT regardless. Revisit toward B1 if MIT
replies adversely on the AIID question, or if the user decides the frozen
overlay (EU AI Act tags and the like) is too stale to keep publishing; B1 then
strips the overlay from all 1,382 rows and tombstones none. (The earlier
trigger, "AIRI-sole count confirmed ~280", is withdrawn: the count is 0.)

## 9. Checks for red-reviewer (shell, raw HTML)

1. Run the Python in section 2; expect 1382 / 1382 / landmark 1382. Corrupt
   test: add a fake row tagged `airi-navigator` in a scratch copy and confirm
   the count moves to 1383.
2. `curl -sI https://www.airi-navigator.com/downloads/airi-data.zip` and the
   apex form; expect apex 307 then www 404 (one endpoint). `curl -s https://www.airi-navigator.com/robots.txt`
   and diff against section 1.
3. Raw-HTML absence checks (curl + grep, not rendered text), on
   `https://www.airi-navigator.com/`, `https://airisk.mit.edu/`,
   `https://airisk.mit.edu/ai-incident-tracker`, `.../old-ai-incident-tracker/incident-view`,
   plus the Next.js bundles for the Navigator: grep case-insensitively for
   `download`, `\.zip`, `\.csv`, `docs.google.com/spreadsheets`,
   `huggingface.co`, `zenodo`, `github.com`, `api` hrefs; record any hit.
   Look specifically at tag-split text.
4. Re-confirm the Terms text in chunk `fdfcd250c3d32eb2.js` (no licence
   clause) and that both `"FALSE".toUpperCase()!=="FALSE"` gates are present in
   chunks `b5439732ff8b66e8.js` and `906798798b22d561.js` (CSV button and ZIP
   link compiled out); count `euAiActRiskLevel` in `/incidents/browse` (1,497
   record objects, 1,496 distinct ids, id 1378 duplicated) and re-derive the
   gap against the ingest file's keys: expected 40 ids not among the 1,456
   AIRI ingest keys, 39 of those already in the corpus via
   `ingest/aiid_full.json`, only AIID-1474 absent (red-reviewer's gate #1
   measurement; this is a re-run of it, ideally by a different method).
5. Confirm CC BY 4.0 irrevocability from the legalcode (section 6) and that
   the airisk footer sentence is still present in raw HTML.
6. Re-derive the AIRI-sole vs AIID-shared split (expected 0 / 1,382) by set
   difference of `source_id` (singular in the ingest files) between `ingest/airi_navigator_incidents.json`
   and `ingest/aiid_full.json` plus `ingest/aiid_incidents.json`; then the
   stronger check, a merge dry-run with the AIRI file removed, listing which
   of the 1,382 ids survive and which fields change. The expected result is
   that `tier` does NOT change on any row (section 2: `_derive_tier` keys on
   `aiid_id`, not on the AIRI overlay); a dry-run showing any `tier` change is
   a surprise to report.
7. Confirm `export_stix.py` / `export_misp.py` contain no freshness handling
   today (`grep -n freshness scripts/export_stix.py scripts/export_misp.py`).

## 10. Open questions for the user (decisions are yours)

1. Option A (keep, stale-tagged, review_by), B1 (strip overlay, tombstone
   none), B2 (tombstone all 1,382; needs a new retraction reason), or R
   (re-ingest from the Navigator's embedded data)? Recommendation is A.
2. If B: authorise the merge dry-run (section 9, check 6) first. (The earlier
   open question "is `tier: landmark` AIRI-derived?" is removed: it is a code
   fact, answered in section 2: no.)
3. Which `review_by` date? (Suggestion 2027-01-07.)
4. Did MIT reply to either outreach (2026-07-27 / 2026-07-29)? None found in
   the files read. The D8 hold lapsed 2026-08-28 with no recorded decision;
   should the registry hold be closed by this decision?
5. Should the transitive-AIID question be re-chased now (agents draft, you
   send)?
