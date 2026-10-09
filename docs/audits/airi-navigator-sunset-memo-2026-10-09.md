# AIRI Navigator sunset memo (v2.13.0 item 6)

> **Status: AGENT-SUGGESTED, 2026-10-09. DO NOT REGENERATE.** Author:
> license-auditor (WS0). This is a dated record of what was true on
> 2026-10-09, not a source. If later work overtakes it, add a dated update
> beneath this header (CLAUDE.md working agreement 4); do not rewrite the
> findings. **The retire-or-keep question is the USER'S decision. This memo
> presents both options and recommends; it decides nothing.**
>
> Branch `ws0/v2130-airi-sunset-memo`. No data, export, schema, or licence file
> was edited. Tool constraint: this author has WebFetch (markdown-converted,
> possibly truncated) and Grep; no shell. Every count below is a ripgrep count
> over `data/incidents.json`, with an exact Python re-derivation given for the
> reviewer to run.

## 1. Channel status (evidence)

All fetches 2026-10-09, WebFetch (rendered/markdown, NOT raw HTML).

| URL | What was seen | Kind of source |
|---|---|---|
| `https://airi-navigator.com/robots.txt` | `User-Agent: *`, `Allow: /`; `Disallow:` `/embed/`, `/admin`, `/login`, `/design-system`, `/api/`; `Sitemap: https://www.airi-navigator.com/sitemap.xml`. Identical to the rule set recorded in SOURCE_LICENSES 1.4 (2026-07-16). | text file, low truncation risk |
| `https://airi-navigator.com/downloads/airi-data.zip` | HTTP 404 | status line |
| `https://www.airi-navigator.com/downloads/airi-data.zip` (the `ZIP_URL` in `scripts/ingest_airi_navigator.py:34`) | HTTP 404 | status line |
| `https://www.airi-navigator.com/` | "MIT AI Risk Navigator", described as a research prototype whose "data and analyses are preliminary and not yet validated"; v1.3.2; latest listed incident dated 2026-05-31; no download/export/API link, no GitHub/HF/Zenodo link; a "Privacy & Terms" link whose text I did not retrieve. | rendered fetch, absence-based |
| `https://airisk.mit.edu/` | No data-download, Google Sheet, HF, Zenodo or GitHub link. Footer: "Data from the MIT AI Risk Initiative is licensed under CC BY 4.0" (link `creativecommons.org/licenses/by/4.0/`). | rendered fetch; the licence line matches the raw-HTML finding in SOURCE_LICENSES 1.4 |
| `https://airisk.mit.edu/ai-incident-tracker` | Dashboards only ("classifies 1,600 real-world report incidents"); links to AIID; no download/export link. A path `/old-ai-incident-tracker/incident-view` also exists (search result; not fetched). | rendered fetch, absence-based |
| `https://airisk.mit.edu/robots.txt` | Fetch summary reported only `Sitemap: https://airisk.mit.edu/sitemap.xml` (no Disallow). | rendered fetch |
| `https://www.airi-navigator.com/api/*` | **Not fetched: robots-disallowed.** Recorded as disallowed, per instruction. | -- |

Web search for a mirror (HF / Zenodo / GitHub / Google Sheets) found none; the
only adjacent public channel is AIID's own weekly snapshots
(`incidentdatabase.ai/research/snapshots`, JSON/MongoDB/CSV), which carries the
AIID fields, not AIRI's taxonomy overlay.

**Conclusion: the bulk channel is withdrawn (confirmed, status-line evidence,
two hosts, 404).** The withdrawal has now persisted from the first failed
refresh (2026-06-07, `data/source_freshness.json` `stale_since`) to today, 4
months, across both the July and October checks.

**Absence-based findings, method-suspect, routed to red-reviewer (section 9):**
(a) "no replacement bulk channel exists" rests on rendered pages and a
search engine; (b) I did not read airi-navigator.com's Privacy & Terms text
(SOURCE_LICENSES 1.4 records that it lives only in a JS bundle); (c) airisk
robots.txt "no Disallow" rests on a summarising fetch. None of these may be
recorded as a negative until the raw-HTML check passes.

**If a replacement channel is later found, the options change**: Option A
becomes "refresh, do not freeze" and Option B loses its main rationale.

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
python -I -c "import json,collections as C;d=json.load(open('data/incidents.json',encoding='utf-8'));r=[e for e in d['incidents'] if 'airi-navigator' in (e.get('tags') or [])];print(len(r));print(sum(1 for e in r if 'airi_navigator' in (e.get('source_freshness') or {}).get('sources',[])));print(C.Counter(e.get('tier') for e in r));print(C.Counter(e.get('last_seen') for e in r).most_common());print(C.Counter(e.get('source_status') for e in r))"
```

(If the top-level key is not `incidents`, the first line of the file is a
dict with `version`, `generated`, `incident_count`; use the list key that
follows.) Expected: 1382; 1382; `{'landmark': 1382}`.

Distribution (ripgrep, multiline over the tags-to-`last_seen` span of each
entry, equal totals as a cross-check):

| `last_seen` (= `updated`, i.e. build/refresh date) | Rows |
|---|---|
| 2026-10-06 | 1,106 |
| 2026-09-xx | 2 |
| 2026-05-xx to 2026-08-xx | 274 |
| total | 1,382 |

**Observation that matters for the tagging spec:** `last_seen` is documented
as an alias of `updated` (DATA_DICTIONARY line 22), the date the row was last
touched by a rebuild, not when the upstream source last supplied it. 1,106 of
these frozen rows read `last_seen 2026-10-06`, four months after the feed died.
Consumers filtering on `last_seen` see them as fresh. The only truthful date is
`source_freshness.as_of = 2026-05-31`.

**Landmarks:** all 1,382 carry `"tier": "landmark"` (ripgrep: 1,382 matches for
tag-then-landmark within the entry; 0 matches for tag-then-non-landmark;
whole-corpus landmark count 1,915). So the frozen AIRI rows are about 72% of
the landmark tier (1,382 of 1,915). **Any landmark feed (`x_tier`, Pages
landmark view, TAXII landmark collection) is therefore predominantly
stale-source data.** This raises the stakes of either option. Reviewer must
confirm with the Python above.

`source_status`: none retracted per the premise check (not re-derived here;
included in the command above).

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
- AIRI-derived content that ships: EU AI Act tier tags (1,380 by the E18
  measure), deployment-stage tag (1,380), `intentional` field (~667
  AIRI-unique), `severity` (798) -- E10 / E18 testimony, not re-measured here.
- Board testimony (PROGRESS line 1953, not re-measured): only about 280 of the
  AIRI rows are AIRI-sole (retained by the merge); about 1,100 are also
  carried by the sanctioned AIID snapshot path, so retiring AIRI would strip
  AIRI-derived fields from those rather than remove the rows. **This split
  decides the real cost of Option B and must be re-derived before the user
  chooses** (see open question 2).
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
- NOTICE-DATA lines 198-207: the AIRI population "reopens for its own review
  before it ships" if its own text reaches the corpus, and cites **1,457** AIRI
  rows. Current tag count is 1,382. **Discrepancy not resolved here**: the two
  numbers may measure different populations (ingest-file rows vs surviving
  rows). Flag for docs-warden/red-reviewer; the live surface needs correcting
  or explaining.

**May frozen rows stay?** On the licence record, yes: a CC BY 4.0 grant
already exercised does not depend on the licensor continuing to host the file
(my understanding, from CC's published position that CC licences are
irrevocable for recipients who comply; **not re-fetched today -- reviewer to
confirm from the legalcode, section 6(a)/(b)**). Attribution is already
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
- Risks: the rows keep re-emitting with `last_seen` = rebuild date, so
  non-marker-aware consumers still see fresh dates. The marker is the only
  signal. Frozen EU-AI-Act tags age silently. A review_by date turns an
  indefinite hold into a dated one (the D8 hold, `until 2026-08-28`, has
  already lapsed 41 days with no recorded decision; the registry is currently
  internally stale on its own hold).
- Reversible: yes, completely.

## 6. Option B: sunset / retire (status + tombstone; never delete; IDs append-only)

Two sub-options, because the population has two parts:

- **B1 (narrow):** tombstone only AIRI-sole rows (~280 by board testimony, to
  be re-derived); on the ~1,100 AIID-shared rows, strip the AIRI-derived
  fields (EU AI Act tags, deployment-stage tag, `intentional`, `severity`
  where AIRI-supplied) and keep the rows (served by the AIID snapshot path).
- **B2 (full):** tombstone all 1,382 rows.

Consequences:

- Counts: B2 drops the active count by up to 1,382 (15,637 -> 14,255) and
  adds 1,382 retracted; B1 drops about 280. The retracted figure in docs
  (15,637 + 29 retracted at v2.12.0) must be restated everywhere counts are
  claimed (README, site, DATASHEET, HF card, Zenodo, CITATION). Counts are a
  load-bearing public claim; docs-warden sweep required.
- Landmarks: B2 removes 1,382 of 1,915 landmarks (72%). The landmark feed
  would shrink to 533. This is the largest consumer-visible effect and weighs
  heavily against B2.
- Tombstone mechanics (Invariant 3): `source_status` set to a retracted state
  plus tombstone record; IDs stay allocated; no row deleted from
  `data/incidents.json`; `ingest/airi_navigator_incidents.json` stays
  committed so history is reproducible. The merge must not re-activate them
  on the next build (the committed ingest file re-feeds the rows every
  build, so retirement needs an explicit override, the same discipline as
  the curation overrides -- a pipeline requirement, not a docs one).
- Field-level changes on the ~1,100 shared rows (B1) are a transformative data
  operation: full before/after delta required (working agreement 2).
- Citations: any external citation of an INC id keeps resolving (tombstone),
  but its content is gone from active views. Consumers who joined on AIRI
  tags (`eu-ai-act-*`) lose the tag on shared rows.
- Downstream: STIX consumers see revoked/absent objects; TAXII static files
  and MISP events change; HF row counts change and need a new dataset
  version. All are breaking for pinned consumers, and a major/minor release
  decision (user).
- Licence: retirement does not reduce licence risk on AIID-sourced text, which
  stays via the AIID snapshot path either way.
- Reversible: tombstones are reversible only by a deliberate un-retraction;
  the public-record effect (DOI'd Zenodo versions, HF revisions) is not.

## 7. Implementation spec for stale tagging and review_by (for the later specialist; applies to Option A, and to Option B1/B2 for any surviving rows)

Which rows: exactly the entries whose `source_freshness.sources` contains
`airi_navigator` (today 1,382; selector is the registry `row_marker`
`{kind: tag, value: airi-navigator}`). Do not select by `last_seen`. Do not
select by title text. Derive from the per-row marker, never author per row.

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
5. **HF (`scripts/export_huggingface.py`, card text ~108-130; features list):**
   already emits `source_freshness {status, as_of, sources}`; add
   `review_by` to the schema/features and the card paragraph. Confirm the card
   says rows are frozen as of `as_of`. HF repo is `genai-incidents` (hyphen).
6. **Docs/mirrors:** `docs/data/incidents.min.json` and
   `src/genai_incidents/data/incidents.min.json` already carry the marker via
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
alternative for the next review. Reasons: (1) no licence fact forces
retirement; (2) 72% of the landmark tier is AIRI-tagged, so B2 would gut the
landmark feed, while stale-marking is reversible and honest; (3) the
sanctioned AIID path already carries the incident identities, so the
distinctive thing at stake is the AIRI overlay, which a marker plus an
as-of date already flags; (4) the lapsed 2026-08-28 hold shows an undated
"hold" decays, so the fix is a dated `review_by`, not retirement; (5) the real
open licence question (transitive AIID share-alike) is orthogonal to
the choice and should be chased with MIT regardless. Revisit toward B1 if MIT
replies adversely on the AIID question, or if the AIRI-sole row count is
confirmed ~280 and the user wants to shed the unrefreshable remainder.

## 9. Checks for red-reviewer (shell, raw HTML)

1. Run the Python in section 2; expect 1382 / 1382 / landmark 1382. Corrupt
   test: add a fake row tagged `airi-navigator` in a scratch copy and confirm
   the count moves to 1383.
2. `curl -sI https://www.airi-navigator.com/downloads/airi-data.zip` and the
   apex form; expect 404. `curl -s https://www.airi-navigator.com/robots.txt`
   and diff against section 1.
3. Raw-HTML absence checks (curl + grep, not rendered text), on
   `https://www.airi-navigator.com/`, `https://airisk.mit.edu/`,
   `https://airisk.mit.edu/ai-incident-tracker`, `.../old-ai-incident-tracker/incident-view`,
   plus the Next.js bundles for the Navigator: grep case-insensitively for
   `download`, `\.zip`, `\.csv`, `docs.google.com/spreadsheets`,
   `huggingface.co`, `zenodo`, `github.com`, `api` hrefs; record any hit.
   Look specifically at tag-split text.
4. Fetch the Navigator's Privacy & Terms text (JS bundle) and grep for the
   licence/reuse clause, as 1.4 did in July.
5. Confirm CC BY 4.0 irrevocability from the legalcode (section 6) and that
   the airisk footer sentence is still present in raw HTML.
6. Resolve NOTICE-DATA 1,457 vs 1,382; and re-derive the AIRI-sole vs
   AIID-shared split (~280 / ~1,100) independently of the board's number
   (set operations over `source_ids` and tags).
7. Confirm `export_stix.py` / `export_misp.py` contain no freshness handling
   today (`grep -n freshness scripts/export_stix.py scripts/export_misp.py`).

## 10. Open questions for the user (decisions are yours)

1. Option A (keep, stale-tagged, review_by), B1, or B2? Recommendation is A.
2. If B: authorise the AIRI-sole vs shared split to be re-derived first.
3. Which `review_by` date? (Suggestion 2027-01-07.)
4. Did MIT reply to either outreach (2026-07-27 / 2026-07-29)? None found in
   the files read. The D8 hold lapsed 2026-08-28 with no recorded decision;
   should the registry hold be closed by this decision?
5. Should the transitive-AIID question be re-chased now (agents draft, you
   send)?
