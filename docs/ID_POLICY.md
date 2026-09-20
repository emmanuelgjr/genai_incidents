# Incident ID policy — headroom and stability

> **STATUS: DRAFT — decision pending (E4).** This document presents two
> options for the ID-width question with a recommendation. The human lead
> decides in Phase 1 (`MASTER_IMPROVEMENT_PLAN.md` §WS3-T5); implementation
> lands in Phase 2 with the other breaking changes. The **Stability policy**
> section (§4) is not part of the decision — it restates rules the project
> already follows and is published as policy either way.
>
> Owner: schema-architect (WS3). Related: WS6-T8 (v3.0 migration guide),
> WS1-T2 (corpus split), WS6-T3 (STIX).
>
> **SUPERSEDED IN PART — see §7 (addendum, 2026-09-19).** Sections 1–6 below
> are preserved verbatim as the record of what was measured on 2026-07-27.
> The headroom figures in §1 and §1.3 are stale; §7 re-measures them and says
> what changed. §7 also records that the E4 decision this banner calls
> "pending" **was subsequently made** (D13, 2026-07-27, Option B). Do not edit
> §§1–6 to make them current.

---

## 1. Current state (measured 2026-07-27, at `main` @ 66b973ca)

### 1.1 Format

Every published incident carries an ID of the form `INC-` followed by a
zero-padded decimal number. As of the measurement date all 13,115 live IDs
match `INC-#####` exactly — one format, no variants, no gaps in the pattern:

| Property | Value |
|---|---|
| Distinct ID patterns in `data/incidents.json` | 1 (`INC-#####`) |
| ID string length | 9 characters, all entries |
| Live entries | 13,115 (`data/stats.json` → `incident_count`) |
| Lowest number in use | `INC-00001` |
| Highest number in use | `INC-14600` |
| Duplicate IDs | 0 |

The format is minted in two places, both as a **minimum**-width format, not a
fixed-width one:

- `scripts/merge_and_dedupe.py:324` — `def slug_to_id(n): return f"INC-{n:05d}"`
- `scripts/parse_existing.py:110` — identical

Python's `:05d` pads to five digits but does not truncate: `slug_to_id(100000)`
returns `INC-100000`. **The allocator therefore does not break at 99,999 — it
silently starts emitting six-digit IDs.** The width cap is enforced only by the
JSON Schema (`schema/incident.schema.json:12`, `"pattern": "^INC-[0-9]{5}$"`),
which means the first ID past 99,999 fails validation in CI rather than
corrupting data. That is a good failure mode, but it is an unplanned one.

### 1.2 ID-space consumption, including burn

The allocator's high-water mark is computed over live IDs **and** every ID ever
recorded in `data/id_deprecations.json` (`merge_and_dedupe.py`, `_load_prev_state`),
so a number is never handed out twice. Consumption is therefore strictly
greater than the live entry count:

| Quantity | Count | Share of numbers issued |
|---|---:|---:|
| Numbers issued (high-water `INC-14600`) | 14,600 | 100.0% |
| Live entries | 13,115 | 89.8% |
| Deprecated (tombstoned) IDs | 992 | 6.8% |
| Numbers issued but recorded nowhere ("silent burn") | 493 | 3.4% |

Deprecations break down as 704 `out-of-scope` (`into: null` — a terminal
tombstone, `resolve_id()` returns `None`) and 288 `merged` (redirects to a
surviving entry). The 493 silent-burn numbers are the arithmetic remainder
(14,600 − 13,115 − 992 = 493) and are explained in §1.4.

**Roughly one in ten numbers issued does not correspond to a live entry.** Any
runway estimate must be made against numbers *issued*, not against corpus size.

### 1.3 Burn rate and runway

Numbers issued over time, read from git history of `data/incidents.json`:

| Date | Live entries | High-water | Note |
|---|---:|---:|---|
| 2026-05-12 | 578 | — | first commit; project is 76 days old |
| 2026-06-10 | 9,209 | 9,630 | |
| 2026-06-10 | 12,062 | 12,571 | v2.3.0 bulk backfill (+2,941 in one day) |
| 2026-07-02 | 12,770 | 14,215 | v2.5.0→v2.6.0 CVE/NVD expansion (+788) |
| 2026-07-12 | 12,986 | 14,458 | |
| 2026-07-18 | 13,025 | 14,497 | +39 |
| 2026-07-27 | 13,115 | 14,600 | +103 (weekly auto-refresh #97) |

85,399 numbers remain below the `[0-9]{5}` ceiling. Runway depends entirely on
which regime you believe:

| Regime | Rate | Runway | Ceiling hit |
|---|---:|---:|---|
| Project-lifetime average (2026-05-12 → today) | 192/day | 445 days | late 2027 |
| Bulk-inclusive (2026-06-10 → today) | 106/day | 2.2 years | late 2028 |
| Post-backfill mixed (2026-06-11 → today) | 44/day | 5.3 years | mid-2031 |
| Recent weekly drip only (2026-07-02 → today) | 15/day | 15.2 years | 2041 |

The honest reading: **the weekly refresh will never exhaust the space; bulk
source onboardings might.** A single ingest expansion has cost up to 2,941
numbers. The space absorbs roughly 29 more events of that size. The plan
contemplates further source onboarding (WS1, WS4) and the WS1-T1 corpus split,
so "a few more bulk events per year" is the realistic planning assumption —
which puts the ceiling somewhere between 2031 and 2041, not this decade's
early years, but also not comfortably beyond the project's expected life.

Note also that the deprecation file's own growth is modest: 979 → 992 entries
in the 2026-07-27 refresh (+13). The large deprecation blocks (500 on
2026-06-10, 404 on 2026-06-11) came from one-off scope cleanups, not from
routine operation.

### 1.4 Two measured defects this document surfaces

Neither blocks the decision; both belong in the Phase-2 implementation task
whichever option wins.

**(a) 9 published IDs have no redirect.** Numbers 522, 609, 951, 952, 955, 956,
957, 1355 and 1660 were published in the `v2.0.0` release, disappeared in
`v2.1.0`, and appear in neither `data/incidents.json` nor
`data/id_deprecations.json` today. `resolve_id("INC-00522")` returns `None`
rather than a successor or a documented tombstone. This is a live violation of
the "merged IDs redirect forever" rule the policy below states — the rule
predates the tombstone machinery, which landed 2026-05-16. Fix: append nine
records with an honest reason (`unrecorded-drop-v2.1.0`), pointing at a
successor where one can be identified and `into: null` where it cannot.

**(b) 484 numbers were issued but never published.** The remaining silent burn
never appeared in any committed `incidents.json`, so no citation can exist for
them and no redirect is owed. They are allocator slack: numbers consumed by
rows that were dropped later in the same build. Harmless, but it means issued
≈ live × 1.11 and the runway table must use issued, not live.

---

## 2. Option A — widen to 7 digits in the v3.0 break

`INC-04853` becomes `INC-0004853`. Numbers are preserved; only padding changes.
(The alternative — renumbering — is not on the table: it would destroy every
external citation and is inconsistent with §4.)

### What changes

| Surface | Change |
|---|---|
| `schema/incident.schema.json:12` | `^INC-[0-9]{5}$` → `^INC-[0-9]{7}$` |
| `src/genai_incidents/schema/incident.schema.json:12-13` | same pattern + "Stable 5-digit…" description |
| `scripts/merge_and_dedupe.py:324`, `scripts/parse_existing.py:110` | `{n:05d}` → `{n:07d}` |
| `data/incidents.json` (+ `.min.json`, `docs/data/`, package copy) | every `id` rewritten — 13,115 values |
| `data/id_deprecations.json` | every `from`/`into` rewritten **and** 14,107 old→new records appended (the plan's "complete map") |
| `docs/404.html:26` | `/\/incident\/(INC-\d{5})\.html$/i` → variable width |
| `docs/DATA_DICTIONARY.md:9`, `README.md:103` | `INC-#####` / "stable 5-digit ID" wording |
| `docs/incidents/*.md`, site shards | regenerated; every in-page anchor changes |
| STIX / TAXII export | see blast radius below |
| MISP export | attribute and event UUIDs, plus `incident-id` tags and comments |
| HF export | the `id` column of every row |

File *names* are unaffected: per-incident standalone pages were withdrawn (see
`docs/404.html`), and the corpus files are named by corpus, not by ID.

### Blast radius (the part that is easy to underestimate)

The STIX exporter derives object identity from the ID string:
`export_stix.py:39-40` computes `uuid.uuid5(NS, prefix + "|" + parts)` and
`export_stix.py:100` calls `_sid("x-genai-incident", iid)`. Re-padding the ID
therefore **rotates the UUID of every incident object** (13,115 objects) and
every `relationship` object referencing them. `export_misp.py:57,101` has the
same property for attribute and event UUIDs. To a TAXII or MISP consumer this
is not a rename — it is a full replacement of the collection, with no
machine-readable link from the old object to the new one unless the migration
guide supplies the mapping out of band. WS6-T3's "real relationship objects"
and WS6-T4's TAXII work would land on top of a one-time identity rotation.

`resolve_id()` (`src/genai_incidents/__init__.py:167`) already follows chains
over an opaque dict, so a 14,107-entry old→new map works without code change —
at the cost of growing `id_deprecations.json` roughly fifteen-fold (992 →
~15,100 records), which is shipped inside the pip package
(`src/genai_incidents/data/id_deprecations.json`) and loaded on first call.

### Risks

1. **Every stored literal breaks.** Anyone who saved `INC-04853` in a
   spreadsheet, a paper, an issue tracker or a database column now holds a
   string that matches no entry. `resolve_id()` fixes it for pip users; for
   everyone else the fix is "read the migration guide".
2. **The map must be provably complete**, covering all 14,107 recorded numbers
   including deprecated ones (a citation of a merged-away ID must survive two
   hops: old-padded → new-padded → canonical successor). Defect (a) above must
   be fixed first or nine IDs migrate into a dead end.
3. **It buys headroom the project may not need** (9,999,999) at the cost of a
   break that lands on 100% of consumers — including the ~90% of the space
   that is nowhere near the cap.
4. **It does not remove the need for parsing tolerance.** During and after the
   transition, consumers must accept that `INC-04853` and `INC-0004853` denote
   the same incident. That is exactly the commitment Option B asks for — so
   Option A is Option B *plus* a rewrite of every published identifier.

---

## 3. Option B — a written padding-agnostic-parsing commitment

Keep `INC-` + five-digit minimum padding. Publish a commitment that the digit
run is a **variable-width decimal number**, and that when the counter passes
99,999 IDs organically become six digits (`INC-100000`), then seven, and so on.

### Exact wording of the commitment (proposed policy text)

> **Incident IDs are `INC-` followed by a decimal number with no upper bound
> on digit count.** IDs issued to date are zero-padded to a minimum of five
> digits; that padding is presentational and is not part of the identifier's
> meaning. Consumers MUST treat an ID as an opaque string for equality and
> lookup, and MUST NOT assume a fixed length, a five-digit width, or that
> lexicographic order equals issue order. Consumers that need numeric order
> MUST parse the digit run as an integer. The project will not re-pad,
> re-number, or otherwise rewrite an ID that has been published.

### What consumers must do

- **Equality/lookup:** nothing. Compare the full string. `by_id()` and
  `resolve_id()` already do exactly this.
- **Regex:** replace `INC-\d{5}` with `INC-\d+`. In this repo that is exactly
  two places: `schema/incident.schema.json:12` (and its package copy) and
  `docs/404.html:26`.
- **Sorting:** sort by the parsed integer, or by `added`/`date`, not by string.
  Today string order and numeric order agree; past 99,999 they diverge
  (`INC-100000` sorts before `INC-99999`).
- **Fixed-width storage:** a `CHAR(9)` column will truncate a six-digit ID. Use
  a variable-width text column.

### How new IDs are issued past 99,999

No code change. `f"INC-{n:05d}"` emits `INC-100000` for n = 100000; the
high-water scan in `_load_prev_state` already parses `^INC-(\d+)$`. The
allocator, `by_id()`, `resolve_id()`, the exporters and the search UI are
already width-agnostic. **Option B's implementation cost is two regex literals,
a schema description string, and documentation.** No data file changes, no ID
rewrites, no UUID rotation.

### Risks

1. **Consumers who zero-pad-assume today get a surprise later** — but at the
   moment the corpus crosses 99,999, not at v3.0, and only for entries above
   that line. Old IDs never change. Failure is localized and late rather than
   universal and immediate.
2. **Sort-order breakage** past 99,999 for anyone sorting IDs as strings. This
   is real and worth stating loudly in the commitment; it is also the only
   functional regression the option carries.
3. **Cosmetic inconsistency** — the corpus would eventually contain a mix of
   5- and 6-digit IDs. Ugly in a table; harmless to machines.
4. **The commitment must be enforced, not just written.** If the schema keeps a
   fixed-width pattern, the promise is a lie the first time it is tested. The
   Phase-2 task must widen the pattern to `^INC-[0-9]{5,}$` and add a
   validate.py test that a six-digit ID passes.

---

## 4. Stability policy (not part of the decision — published either way)

These three rules hold under both options and are stated here as project
policy. They align with the always-active board invariants in `CLAUDE.md`
("never delete entries — status + tombstone instead" and "IDs/tombstones are
append-only") and with plan invariants 3 and 4.

1. **IDs are never reused.** A number issued to an entry is retired with that
   entry. The allocator computes its high-water mark over live entries *and*
   every ID recorded in `data/id_deprecations.json`, so a retired number can
   never be handed to a different incident, even if the original entry is
   removed from the corpus entirely.

2. **Tombstones are append-only.** A record in `data/id_deprecations.json` is
   never edited to change its meaning and never deleted. Corrections are made
   by appending, not by rewriting history. A tombstone with `into: null` is
   terminal: the ID was withdrawn (out of scope) and resolves to nothing, which
   is a different and more honest answer than "not found".

3. **Merged IDs redirect forever.** When two entries merge, the surviving entry
   keeps the lower-numbered ID and every absorbed ID gains a record pointing at
   the survivor. Those redirects are permanent and transitively resolvable:
   `resolve_id()` follows a chain of any length and terminates. A citation of
   any ID this project has ever published must always resolve to either the
   current canonical entry or an explicit withdrawal — never to silence.
   *(Current compliance: 9 known exceptions — see §1.4(a) — to be repaired in
   Phase 2.)*

---

## 5. Recommendation

**Adopt Option B: publish the padding-agnostic-parsing commitment, widen the
schema pattern to `^INC-[0-9]{5,}$`, and do not re-pad any published ID.**

The rationale in one line: Option A costs a universal break — 13,115 rewritten
identifiers, a 15,000-record migration map, and a rotation of every STIX and
MISP object UUID — and still requires consumers to accept that two differently
padded strings mean the same incident, which is the entirety of what Option B
asks for. Option A is Option B plus a rewrite. The runway measurement says the
cap is 5 to 15 years out at observed rates and is threatened only by bulk
onboarding events, not by the weekly refresh; that is enough headroom to make
paying a universal-break cost now the wrong trade. If the corpus does approach
99,999, the transition to six digits is already implemented in the allocator
and affects only newly issued IDs.

Two conditions attach to this recommendation:

- **Enforce the commitment in the schema.** `^INC-[0-9]{5}$` must become
  `^INC-[0-9]{5,}$` in both schema copies in the v3.0 break, with a validate.py
  test proving a six-digit ID passes and `INC-1234` (four digits) fails. A
  written promise contradicted by the validator is worse than no promise.
- **Monitor the burn.** Publish numbers-issued alongside entry count (a
  `high_water_id` key in `data/stats.json` is the cheap version) so the runway
  is a measured number in CI rather than a thing someone re-derives by hand in
  three years. Revisit this decision if issued IDs pass 50,000.

**If the lead prefers Option A anyway** — the defensible reason is
presentational: fixed width keeps lexicographic sort equal to issue order
forever and keeps dumb `\d{7}` regexes working. If so, v3.0 is the only
acceptable moment for it, defect §1.4(a) must be repaired before the map is
generated, and WS6-T8 must carry a worked STIX/MISP UUID-rotation example, not
just a JSON before/after.

### What the decision unblocks

The choice is a direct input to **WS6-T8** (`docs/MIGRATING_TO_V3.md`), whose
acceptance criterion is that it covers every breaking change in the v3.0.0-beta
diff: under Option A that guide needs an ID-mapping section, a `resolve_id()`
worked example, and a warning that STIX/MISP object identities rotate; under
Option B it needs a short "IDs are unchanged; stop assuming five digits"
section and a regex-fix note. It also determines the size and shape of the
Phase-2 ID task — under Option A a data migration with a 14,107-entry map, a
fixture-backed migration script in `scripts/migrations/`, and `resolve_id()`
tests over every historical ID; under Option B a two-line schema change plus
those same `resolve_id()` tests, which are owed regardless (WS3-T5's third
acceptance clause). Until it is decided, WS6-T8 cannot be drafted to
completion and the Phase-2 breaking-change set is not fully enumerable.

---

## 6. Verification recipe

Every number in §1 is reproducible from the repository at `main`:

```bash
# 1.1 format, count, high-water, duplicates
python -c "import json,re,collections; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; ids=[e['id'] for e in d]; print(len(ids), len(set(ids)), collections.Counter(re.sub(r'[0-9]','#',i) for i in ids), max(int(i[4:]) for i in ids))"

# 1.2 deprecations, reasons, silent burn
python -c "import json; dep=json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']; import collections; print(len(dep), collections.Counter(d['reason'] for d in dep), sum(1 for d in dep if not d.get('into')))"

# 1.3 high-water over history (one line per revision of the data file)
git log --format=%H -- data/incidents.json

# 1.4(a) the nine unrecorded drops
git show v2.0.0:data/incidents.json    # contains INC-00522 et al.
python -c "import json; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; print(any(e['id']=='INC-00522' for e in d))"   # False

# allocator overflow behaviour
python -c "print(f'INC-{100000:05d}')"   # INC-100000
```

Corpus totals quoted in this document are as of 2026-07-27 and are stated with
their measurement date rather than templated, because this file is a
point-in-time decision record and is not on the `stats_docs_lib.DOC_SURFACES`
list.

---

## 7. Addendum — headroom re-measured 2026-09-19

> **DATED RECORD — DO NOT REGENERATE, DO NOT MERGE INTO §§1–6.**
> Measured 2026-09-19 at `main` @ `0fb0d969`. This section supersedes the
> **numbers** in §1 and §1.3 and nothing else: §2, §3, §4 and §5 are
> unaffected in substance, and §§1–6 stay as written because they are the
> record of what the runway looked like when it was last assessed. Written by
> schema-architect (WS3). A later re-measurement appends §8; it does not edit
> this section.
>
> **Why this was run:** `docs/ID_POLICY.md` exists to inform the ID-width
> question, and the D28 remediation (WS4-T21, the 47-split unmerge, merged
> 2026-09-18) minted roughly three hundred IDs in a single transaction. A
> runway table dated eight weeks earlier is stale input to that question.

### 7.1 What moved, and what did not

| Quantity | §1 (2026-07-27) | Now (2026-09-19) | Δ |
|---|---:|---:|---:|
| Live entries | 13,115 | **13,361** | +246 |
| High-water number issued | 14,600 | **14,910** | +310 |
| Deprecation **records** | 992 | **1,060** | +68 |
| Deprecation **distinct IDs** | 992 | **1,056** | +64 |
| Silent burn (issued, recorded nowhere) | 493 | **493** | 0 |
| Numbers remaining below `[0-9]{5}` | 85,399 | **85,089** | −310 |
| Issued ÷ live | 1.113 | **1.116** | +0.003 |
| Distinct ID patterns / ID length | 1 / 9 chars | **1 / 9 chars** | unchanged |
| Duplicate IDs | 0 | **0** | 0 |

**Records ≠ distinct IDs, for the first time in this file's history.** Four IDs
(`INC-07771`, `INC-08109`, `INC-08133`, `INC-08146`) now carry **two**
tombstones each: a `merged` record from 2026-06-28 and a `resplit` record from
2026-09-18 that un-does it. Every runway figure below is computed against
*distinct* IDs, because that is what the allocator's high-water scan consumes.
A reader reconciling 1,060 against 1,056 is not looking at an error.

Two vocabulary items postdate §1 entirely: the `reason` values `split` (4
records) and `resplit` (4 records), and an `into` field that may hold a **list**
of successors rather than a string. §1's reason breakdown (704 `out-of-scope` /
288 `merged`) is now 704 `out-of-scope` / 289 `merged` / 59
`orphaned-ingest-source-retired` / 4 `split` / 4 `resplit`, and 763 records are
terminal (`into: null`) rather than 704.

**§1.4(a) is still open.** All nine IDs — 522, 609, 951, 952, 955, 956, 957,
1355, 1660 — remain in neither `data/incidents.json` nor
`data/id_deprecations.json` as of this measurement. D13's rider (b) is
unimplemented.

### 7.2 The runway, stated the way §1.3 states it

Extending §1.3's series with every revision of `data/incidents.json` since:

| Date | Live entries | High-water | Note |
|---|---:|---:|---|
| 2026-07-27 | 13,115 | 14,600 | §1.3's last row (weekly auto-refresh #97) |
| 2026-07-28 | 13,119 | 14,604 | WS0-T3 Phase B rebuild (+4) |
| 2026-07-30 | 13,060 | 14,604 | E21 OECD reduction — **live −59, no numbers issued** |
| 2026-08-17 | 13,060 | 14,604 | OWASP 2026 migration — **no numbers issued** |
| 2026-09-18 | 13,060 | 14,604 | v2.10.0 cut — **no numbers issued** |
| 2026-09-18 | 13,361 | 14,910 | **D28 remediation: +306 in one transaction** |

85,089 numbers remain below the `[0-9]{5}` ceiling. The same four regimes §1.3
uses, recomputed to today:

| Regime | §1.3 rate | Now | §1.3 runway | Now | Ceiling hit |
|---|---:|---:|---:|---:|---|
| Project-lifetime average (2026-05-12 →) | 192/day | **115/day** | 445 days | **742 days** | late 2028 |
| Bulk-inclusive (2026-06-10 →) | 106/day | **52/day** | 2.2 years | **4.5 years** | early 2031 |
| Post-backfill mixed (2026-06-11 →) | 44/day | **23/day** | 5.3 years | **10.0 years** | 2036 |
| Recent drip only (2026-07-02 →) | 15/day | **8.8/day** | 15.2 years | **26.5 years** | 2053 |

Every regime got **slower**, and every runway got **longer**. The reason is in
the series above: between refresh #97 and the D28 merge the corpus issued
**zero** new numbers for 52 days — an unusually long idle stretch (the corpus
was frozen for the WS4-T21 remediation), which dilutes every rate whose window
overlaps it. Strip the D28 event out of the newest window and the organic drip
since 2026-07-02 is 389 numbers over 79 days = **4.9/day**, a ~47-year runway.

Read the widening with suspicion, not relief: it is a measurement of a period
in which the project was deliberately not ingesting. It is evidence that the
drip is slow; it is not evidence that the project got safer.

### 7.3 What D28 did to the runway specifically

Field-level, from the tombstones and the corpus (not from prose):

- **306 numbers minted**, `INC-14605` … `INC-14910`, one contiguous block, in
  one merge.
- **5 IDs left live service**: four `split` parents (`INC-00311`, `INC-00554`,
  `INC-00754`, `INC-01897`) plus `INC-07738`, merged into `INC-14757`. All five
  carry tombstones. Four already-tombstoned IDs gained `resplit` records.
  (The routing brief's "four retirements" undercounts by one: `INC-07738` is a
  retirement too, just a `merged` one rather than a `split` one.)
- **Net live 13,060 → 13,361** = +306 − 5. The arithmetic closes exactly.
- **Zero burn inside the block.** All 306 numbers are live entries today;
  135 of them are named as `into` targets of a D28 tombstone, the other 171
  are rows unmerged from parents that were never tombstoned.

That last point is the interesting one for the model. Ordinary ingestion runs
at issued ≈ live × 1.11 — roughly one number in ten is consumed by a row that
never survives the build. **D28 consumed 306 numbers and produced 306 live
entries: 100% efficiency, the cleanest allocation event in the project's
history.** A remediation knows exactly how many rows it is creating; an ingest
does not.

**Does it change the shape of the projection, or only its position?** Position
only, and by −310 numbers out of 85,399 — 0.36% of the remaining space. The
shape argument is addressed in §7.5.

### 7.4 Has the answer changed? No.

Stated plainly, because "no change" is the result and should not have to be
inferred:

1. **The ID width question was already decided.** E4 was resolved on
   2026-07-27 by **D13** — Option B, the padding-agnostic-parsing commitment,
   with two riders. The DRAFT banner at the top of this file, which says
   "decision pending", was true when written and has been stale since the day
   after. What remains open is the *implementation* task and the two riders,
   not the ruling. (This addendum does not edit the banner's original wording;
   see the supersession note beside it.)
2. **Nothing measured here disturbs that ruling.** Option B's case never
   rested on the runway being long — it rested on Option A being Option B plus
   a rewrite of every published identifier (§5). That argument is unaffected by
   any count in §7.1, and the cost side of it got *larger*: Option A would now
   rewrite 13,361 IDs rather than 13,115, and the "complete old→new map" would
   cover 14,910 numbers rather than 14,107.
3. **Neither of D13's own revisit triggers is near firing.** Issued numbers are
   14,910 — **29.8%** of the way to the 50,000 revisit trigger, and headroom is
   **85.1%** of the space against a 20% floor.
4. **The runway is comfortable and got more so**, on every regime §1.3 defined.

If the lead is re-reading this file to make a ruling: the ruling was made, and
the fresh numbers support it more strongly than the stale ones did.

### 7.5 The bulk-consumption question — judgement

**The model does not need a rate term for bulk events. It needs the reopen
trigger D13 already ordered, and D28 is the event that lets us set its
threshold honestly.**

Averaging bulk events into a per-day rate is the wrong instrument and always
was. §1.3's four regimes differ by a factor of thirteen purely in how much bulk
they average in, which is another way of saying the average is not measuring
anything stable. Adding a fifth "bulk term" fitted to one 306-number event
would be over-fitting with extra steps — and it would over-fit to the *smallest*
bulk event on record, which is worse than useless. The three bulk events this
project has actually had were 2,941 (v2.3.0 backfill), 788 (v2.6.0 CVE
expansion) and 306 (D28). The space absorbs 28, 107 or 278 more of them
respectively. The honest statement is the one §1.3 already makes: the drip will
never exhaust the space, bulk events might, and the number of bulk events per
year is not a measured quantity — it is a planning decision the project makes
one remediation at a time.

The right instrument for a variable nobody can forecast is a **threshold that
escalates before the fact**, which is exactly what D13's rider (a) asked
schema-architect to propose. D28 gives it a calibration point. Proposed:

> **ID-headroom reopen trigger.** The Option-B ruling (D13) reopens
> automatically as an escalation to the human lead when **any one** of these
> holds:
> **(a)** a single planned operation would mint **more than 2,000 numbers**
> — roughly 2.5% of remaining headroom at the time of writing, and about
> two-thirds of the largest event on record;
> **(b)** **more than 5,000 numbers** are issued across any rolling 90-day
> window, whatever the mix of drip and bulk;
> **(c)** cumulative numbers issued pass **50,000** (D13's own figure); or
> **(d)** remaining headroom below the current width falls under **20%**
> (D13's own figure — 20,000 numbers).
> Condition (a) is checked by the operation's own design review, before it
> runs. Conditions (b)–(d) are checked in CI against a `high_water_id` key
> published in `data/stats.json`.

Why those two new numbers. **(a) 2,000** is set so that the *largest event this
project has ever run* would have tripped it and D28 would not — a threshold
that no historical event trips is form (a) of working agreement 6, a check that
cannot fail; a threshold that every event trips is noise. 2,000 sits between
306 and 2,941 and closer to the top, which is the correct asymmetry: we want to
hear about the rare large one, not the routine remediation. **(b) 5,000 per 90
days** exists because the failure mode the drip regimes hide is not one large
event, it is several medium ones in quick succession — WS4-T5's successor-pair
merges and the three flagged pairs are exactly that population, and each is
individually far under (a). Condition (b) is the term that catches what a
per-event threshold cannot, without pretending to forecast a rate. At today's
organic rate a 90-day window carries ~440 numbers, so (b) has roughly 11×
slack against the drip alone — it fires on accumulation, not on business as
usual.

**Blocking prerequisite.** Conditions (b)–(d) are unenforceable today:
`data/stats.json` has keys `incident_count`, `landmark_count`, `generated`,
`version`, `year_min`, `year_max` — **no `high_water_id`**. §5's second
condition asked for that key on 2026-07-27, D13 folded it into rider (a), and
the board still carries it as a follow-up with no owner. Until it exists, every
number in this addendum is something a human re-derives by hand, which is how
the table in §1 went stale in the first place. **This addendum recommends the
`high_water_id` key be given an owner as the first piece of rider (a)'s
machinery**; the threshold above is prose until something computes it.

### 7.6 No schema change is required by this addendum

The `pattern` on the `id` property in both `schema/incident.schema.json` and
`src/genai_incidents/schema/incident.schema.json` is still `^INC-[0-9]{5}$`,
and at a high-water of 14,910 it will not be tested for a long time. Widening
it to `^INC-[0-9]{5,}$` remains D13's v3.0/Phase-2 implementation work, not
something this re-measurement triggers. **This is a documentation-only change.**

### 7.7 Verification recipe for §7

Every figure above is reproducible from the repository at `main` @ `0fb0d969`.
Two independent derivation paths are given, because a re-run of a single method
is not a check (working agreement 6).

```bash
# ROUTE A - current state, straight from the two data files
python -c "import json; \
inc=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; \
dep=json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']; \
live={int(e['id'][4:]) for e in inc}; d={int(x['from'][4:]) for x in dep}; \
print('live',len(live),'records',len(dep),'distinct_dep',len(d), \
'high_water',max(live|d),'burn',max(live|d)-len(live)-len(d-live), \
'headroom',99999-max(live|d))"
# -> live 13361 records 1060 distinct_dep 1056 high_water 14910 burn 493 headroom 85089

# ROUTE B - the same three totals derived WITHOUT reading git history, from
# each entry's own `added` stamp and each tombstone's own `date`. Agrees with A
# on all three. It confirms the TOTALS only: D28's split children inherit their
# parents' `added` date, so `added` is not an issuance date and Route B cannot
# reconstruct the curve. That limitation is itself a finding - any future
# consumption model built on `added` would be blind to bulk remediations.
python -c "import json,collections; \
inc=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; \
dep=json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']; \
p=[(e['added'][:10],int(e['id'][4:])) for e in inc]+[(x['date'][:10],int(x['from'][4:])) for x in dep]; \
print('high_water',max(n for _,n in p),'live',len(inc),'distinct_dep',len({x['from'] for x in dep}))"
# -> high_water 14910 live 13361 distinct_dep 1056

# The D28 delta, per-ID rather than per-aggregate (form (d) of agreement 6 is
# exactly what an aggregate hides). 0c778ced is the v2.10.0 cut, pre-D28:
git show 0c778ced:data/incidents.json > pre.json
python -c "import json; \
pre={e['id'] for e in json.load(open('pre.json',encoding='utf-8'))['incidents']}; \
now={e['id'] for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']}; \
print('added',len(now-pre),'removed',sorted(pre-now))"
# -> added 306 removed ['INC-00311','INC-00554','INC-00754','INC-01897','INC-07738']

# The high-water series in 7.2 - one row per revision of the data file:
git log --format='%H %ad' --date=short -- data/incidents.json

# 1.4(a): the nine are still dangling
python -c "import json; \
inc={e['id'] for e in json.load(open('data/incidents.json',encoding='utf-8'))['incidents']}; \
dep={x['from'] for x in json.load(open('data/id_deprecations.json',encoding='utf-8'))['deprecations']}; \
print([i for i in ['INC-00522','INC-00609','INC-00951','INC-00952','INC-00955', \
'INC-00956','INC-00957','INC-01355','INC-01660'] if i not in inc and i not in dep])"
# -> all nine
```

**Proof the Route-B check can fail** (a gate nobody has seen fail is a gate
nobody should cite): deleting the single highest-numbered entry from a *copy*
of `data/incidents.json` moves Route B's output from `high_water 14910 live
13361` to `high_water 14909 live 13360`. Run against a scratch copy; nothing
under `data/` was modified by this measurement.

Corpus totals quoted in this section are as of **2026-09-19** and are stated
with their measurement date rather than templated, for the same reason §6 gives:
this file is a point-in-time decision record and is not on the
`stats_docs_lib.DOC_SURFACES` list.
