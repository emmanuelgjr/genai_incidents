# WS4-T15 — superseding-redirect design and persistence

**Status: RECORD, dated 2026-09-18. DO NOT REGENERATE.** Later work that
overtakes any claim here must add a dated update naming which half
changed, per working agreement 4 — not edit this text in place.
**Owner:** pipeline-engineer (code/design) + schema-architect (the one
schema decision this document routes, §3). **Boarded by:** D26 (user,
2026-09-17), blocked-by WS4-T10's correction pass merging first (it has:
`docs/specs/WS4-T10-unmerge-design-2026-09-15.md` FINAL PASS on
`9324cdf7`, per that branch's own board record — WS4-T10's *merge to
main* is separately blocked by this document's sequencing analysis, §7).
**Depends on:**
`docs/specs/WS4-T10-unmerge-design-2026-09-15.md` §8.1's measurement and
§8.4's `INC-07738` diagnosis (both stand); §8.2 and §8.3 of that document
are SUPERSEDED and not built on here except for the two findings their own
superseding notes explicitly exempt (the `resplit` record-type proposal
and the `resolve_id` crash finding).

**Constraints honoured throughout:** nothing under `data/` or `schema/` is
touched by this document or its proof-of-concept code (verified: `git diff
--stat main..HEAD -- data/ schema/` is empty on this branch). No unmerge is
executed and no published data changes — every demonstration below runs
against `tmp_path` fixtures or hand-built in-memory fixtures, never against
the committed corpus, except where explicitly marked "read-only against
committed data" (those calls only *read* `data/incidents.json` and
`data/id_deprecations.json`; none write to them).

---

## 0. The core decision, up front

The demonstrated bug (WS4-T10's own audit) was **not** that superseding
records are hard to write — it's that the build **silently deletes
history on every rebuild** because it identifies a deprecation record by
`from` alone and collapses to one record per `from` every time it
rewrites the file. The fix implemented here does **not** change what a
record's identity key is; it changes the build so that **the file it
already has that identity is never collapsed, reordered, or rewritten
away.** `prev_deprec` — the on-disk history — is now carried through
**verbatim and in order**; the build only ever **appends**. A second,
independent question (should `from` *stay* the identity key, or should the
project adopt an explicit, order-independent one) is real, separable, and
routed to the user in §3 — but it does not block landing the persistence
fix, because the persistence fix does not depend on its answer.

**Addendum, dated 2026-09-18 (red-reviewer BOUNCE):** the persistence fix
above was correct, but two of its *consumers* were not updated to match
it, and its own "by construction" ordering claim was untested. §2.3 fixes
the issue-88 fixpoint (it mutated stale, superseded records in place and
mis-propagated their state to third-party citers); §2.4 adds the mutation
test that actually guards the ordering claim; §6 fixes the coverage
guard (it measured a literal `into` value instead of a resolved chain).
All three are fixed, tested, and proven by mutant against the real bug
shape below — not merely argued.

---

## 1. The inherited ±1 discrepancy — resolved per-entity, hypothesis CONFIRMED and refined

**The conflict** (board note `9bc99cc0`): `docs/specs/WS4-T10-unmerge-design-2026-09-15.md:103`
reports the corpus delta as control 13,060 → fixed 13,361 (**+301**),
while its §2 distribution table sums to **349 successor rows from 47 old
rows** and states "47 of those 349 keep an existing id and 302 are freshly
minted (exactly the measured new-only count)" — 47 rows becoming 349 is a
local net of **+302**.

**Verified against `docs/audits/WS4-T10-phaseB-delta-2026-09-15.json`
(the committed, re-runnable evidence), per-entity, not by re-running either
aggregate** (per the brief's explicit instruction and working agreement 6d
— an aggregate that balances while its composition is misdescribed is
exactly the failure shape this project keeps producing):

```
id_sets: old_count=13060, new_count=13361, common_count=13059,
         new_only_count=302, gone_count=1, gone=["INC-07738"]
new_deprecations: [{"from": "INC-07738", "into": "INC-14757", "reason": "merged", ...}]
splits.rows: 47 entries, total_successor_rows=349, all 349 successor ids
  DISTINCT within splits.rows itself (47 survivor ids + 302 freshly-minted
  ones, zero internal duplicates — checked directly: `Counter` over every
  group's flattened successor list gives 349 entries, 349 distinct keys).
new_deprecations: exactly ONE record, `{"from": "INC-07738", "into":
  "INC-14757", "reason": "merged"}` -- a SEPARATE data structure from
  splits.rows.
```

**`INC-14757` is the sole point of overlap BETWEEN these two separate
structures, and it explains the whole gap.** It is one of `INC-00623`'s
("French Army Tests Boston Dynamics' Spot Robot in Combat Training") four
split successors — one of that row's four source_ids
(`OECD-AIM-2026-04-08-e597`) does not land on its own new row; it lands on
`INC-14757` **together with** `OECD-AIM-2026-04-27-eb9a`, the sole
source_id that used to belong to old `INC-07738` (a completely separate,
un-split, 1-source old row, not one of the 47). `INC-14757` was therefore
already counted once among `INC-00623`'s split successors — the
`new_deprecations` record for `INC-07738` names the SAME id as its target,
not a different, additional one. That is the exact §2.3/§8.4 "the fix
also recovers a true duplicate" story, confirmed directly by
cross-referencing the two committed data structures rather than argued
from the row-count aggregates that were merely consistent with it before.

**The reconciliation:** the 47-split population's own internal net
(+302: 47 old ids survive, 302 new ids appear) is a measure of the split
population **in isolation**. It does not include `INC-07738`, which is not
one of the 47 split old-rows — it is a separate row that **disappears**
(`gone_count=1`) with **no row of its own appearing to replace it**,
because the one row its content flows into (`INC-14757`) **was already
going to exist** as `INC-00623`'s split successor, with or without
`INC-07738`'s content ever joining it. So:

- Net from the 47 splits, taken alone: +302 (47 survive, 302 new).
- Net from the `INC-07738` merge, taken alone: −1 (`INC-07738` disappears;
  `INC-14757`, the row its content joins, is **not** an additional row —
  it's already counted in the 302).
- Corpus-wide net: **+302 − 1 = +301.** Exactly `id_sets`'s measured
  `new_only_count(302) − gone_count(1) = 301`, and exactly the `:103`
  figure.

**The foreman's hypothesis is CONFIRMED, refined from "consistent with
aggregate signals" to "directly verified in the successor-membership
data": `INC-07738` retires into a fresh id without adding a row, because
that fresh id was already being created by an unrelated split, and its
own content simply piggybacks onto it.** Both figures survive; Option 2's
349-successor arithmetic in the T10 spec is not wrong, it just isn't the
whole corpus-level story, which needed this one cross-reference to close.
**Not a defect in the v2.10.0 release notes** (already noted by the board:
they cite `+301` correctly).

---

## 2. Item 1 — deprecation persistence (implemented, tested, proven by mutant)

### 2.1 The mechanism

`scripts/merge_and_dedupe.py`'s deprecation-merge step (the block
immediately following `# 8) Merge deprecations with the on-disk history
and persist.`) previously did:

```python
seen_from = {d.get("from"): d for d in prev_deprec if d.get("from")}
for d in deprecations_new:
    seen_from.setdefault(d["from"], d)
deprecations_all = sorted(
    seen_from.values(), key=lambda x: (x.get("from") or "", x.get("date") or ""),
)
```

`{d.get("from"): d for d in prev_deprec}` is a plain dict comprehension
keyed on `from` — Python keeps whichever record for a repeated key occurs
**last** while iterating `prev_deprec`, i.e. it collapses every prior
record for that `from` down to one, **every single rebuild**, regardless
of whether the file legitimately carried two records for the same id. The
removed comment above it said "keep the earliest," which was also false.

**Fixed to:**

```python
already_deprecated = {d.get("from") for d in prev_deprec if d.get("from")}
fresh: list[dict] = []
seen_fresh_from: set[str] = set()
for d in deprecations_new:
    f = d.get("from")
    if f and f not in already_deprecated and f not in seen_fresh_from:
        seen_fresh_from.add(f)
        fresh.append(d)
deprecations_all = list(prev_deprec) + fresh
```

`prev_deprec` — the on-disk history — is carried through **verbatim and
in order**, never re-derived, never collapsed, never re-sorted. The build
only ever **appends**: a fresh record from *this build's own* dedupe pass
is added only for a `from` id that has **no** existing record on disk at
all (this preserves the old code's one real protective behaviour — an
ordinary rebuild refusing to double-write an id that's already
deprecated). A **deliberately appended** superseding record (e.g. a future
`reason: "resplit"` record written by a remediation script, not by an
ordinary `make build`) is not `deprecations_new` from this build's
perspective — it is already sitting in `prev_deprec` from a previous
commit, and the new code carries it through unchanged.

**Precedence:** last-in-file wins for a repeated `from`. This was already
true of `_load_deprecations()` in `src/genai_incidents/__init__.py`
(`out[f] = t`, unconditional overwrite, file order) and is now also true
of `check_integrity`'s `into_map` in `scripts/validate.py` (same pattern).
Because the build never reorders or re-sorts `prev_deprec` and only
appends, **file order IS append order IS chronological order, by
construction** — this is now an invariant the code enforces, not an
accident of a sort key that happened to agree with date most of the time
(the T10 audit found 57 date inversions in the *old*, sorted-every-build
file — sorting by `(from, date)` is exactly what could silently reorder
two same-`from` records if their dates were ever out of order, which is
also now moot: nothing sorts the file at all anymore).

A related, pre-existing crash was fixed in the same block: the issue #88
EXCLUDE-bucket fixpoint loop (`if d.get("into") in removed_terminal`) now
skips list-valued `into` records rather than raising `TypeError:
unhashable type: 'list'` on `in` against a `set` — reachable the moment a
future `split`/`resplit` record exists, previously reachable by nothing in
the committed data.

> **[CORRECTION, dated 2026-09-18 — red-reviewer BOUNCE.]** The paragraph
> above this ("The build only ever appends... it never touches an id that
> already has a record on disk") and the code comment at
> `scripts/merge_and_dedupe.py` it was drawn from were **FALSE as a claim
> about this build overall**, though true of the persistence block in
> isolation. The very next block in the same function — the issue #88
> fixpoint just described — iterated EVERY record and MUTATED whichever
> it visited in place; the persistence fix in §2.1 removed the only thing
> (the one-record-per-`from` collapse) that had been keeping that loop
> from ever seeing more than one record for a `from` and getting it
> wrong. **This is BOUNCE defect 1, not a separate task — see §2.3.**
> Preserved above per agreement 4 (the original claim, and the finding
> that falsified it, are both part of the record); read §2.3 for what is
> actually true today.

### 2.2 Proven by mutant, not just argued

Per working agreement 6 ("test your design against an actual rebuild
before writing it down as workable" — the previous attempt's fatal
mistake): `tests/test_merge_and_dedupe.py::test_second_deprecation_record_survives_rebuild`
seeds two on-disk records for the same `from` (an original `merged`
record and a later `resplit`-shaped correction, exactly the scenario the
T10 audit demonstrated breaking) and asserts both survive a `m.main()`
rebuild, in order, with the last one authoritative.

**Verified to fail on the old code, not just pass on the new one.** I
temporarily reintroduced the exact old collapse logic in place of the
fix, reran the test, and it failed with:

```
AssertionError: an ordinary rebuild must not collapse a superseding record
away (invariant 9) -- got [{'from': 'INC-09999', 'into': 'INC-00001',
'reason': 'resplit', 'date': '2026-02-01', ...}]
assert 1 == 2
```

— the exact 2→1 collapse the T10 audit found (there: 1,051→1,050 on a
real `INC-07771` resplit append). The fix was restored immediately after
(`git diff --stat` on `scripts/merge_and_dedupe.py` returned empty,
confirming an exact restore); the full suite (352 tests) passes clean on
the restored code.

`tests/test_merge_and_dedupe.py::test_ordinary_rebuild_still_refuses_second_record_for_new_from`
locks in the complementary property the old `setdefault` behaviour
protected and that the fix must not weaken: an ordinary rebuild run twice
against unchanged inputs still writes **exactly one** record for a
newly-retired id, not two.

### 2.3 Defect 1 (BOUNCE, 2026-09-18) — the issue #88 fixpoint mutated stale records and mis-propagated

**Found by red-reviewer's gate, with a repro script
(`probe_issue88.py`), not by anything in this task's own verification —
the persistence proof in §2.2 tested the thing this task changed, not the
things that depended on what it changed.** §2.1's fix made `prev_deprec`
carry through with **more than one record per `from` now possible** for
the first time. The issue #88 EXCLUDE-bucket fixpoint (the block
immediately after §2.1's, unwinding when an OECD "not on the OECD.AI
platform anymore" bucket withdraws source content) was written when the
old collapse guaranteed **exactly one** record per `from` always existed
— so it iterated `deprecations_all` directly, with no notion of "which
record is the authoritative one," and **mutated whichever record it
visited in place**:

```python
for d in deprecations_all:
    if d.get("into") in removed_terminal:
        d["into"] = None
        d["reason"] = "out-of-scope"
        ...
```

**Demonstrated against the committed WS4-T15 code, with a real EXCLUDE
bucket (`INC-00004`; 25 buckets exist today):** seed `INC-09999 ->
INC-00004` (a STALE record, into the bucket) + `INC-09999 -> INC-00001`
(the AUTHORITATIVE, later, live `resplit` record — exactly the shape §2
exists to make possible) + `INC-09998 -> INC-09999` (a third party citing
the retired id). Output: the stale record was rewritten to `into: null,
reason: "out-of-scope"` **and** `INC-09998`'s record was nulled too,
because the loop read the stale record first, decided `INC-09999` was
terminally removed, and propagated that into `removed_terminal` before
ever consulting the authoritative record that said otherwise. A citation
of `INC-09998` would now resolve to "removed, out of scope" instead of
the live `INC-00001`.

**Two failures in one run**, both now fixed:

1. **`prev_deprec` was not, in fact, carried through verbatim** the
   moment this second block ran — §2.1's own claim ("never touches an id
   that already has a record on disk") was true of the persistence block
   alone and false of the build overall (§2.1's correction note, above).
2. **The wrong-propagation is new with this task**, not a pre-existing
   bug this task merely inherited: the old one-record-per-`from` collapse
   meant the fixpoint's `deprecations_all` could never contain a stale
   record shadowed by a live authoritative one, so it only ever saw the
   authoritative record and the bug was unreachable. **Removing the
   collapse removed a guarantee this downstream consumer silently
   depended on, without updating that consumer.**

**Fixed** (`scripts/merge_and_dedupe.py`) to (a) compute the same
authoritative (latest-per-`from`) view every other consumer uses before
reasoning about anything, and (b) **append** a new terminal record for a
`from` that genuinely needs one, never mutate an existing record — editing
a committed record's `into`/`reason` to change its meaning is itself the
append-only violation `docs/ID_POLICY.md` rule 2 forbids, independent of
whether it also mis-propagates. Re-running the exact repro above against
the fix: the stale record and the third-party citation both survive
**unmutated**, and — separately verified — when the authoritative record
for a `from` genuinely does point into an EXCLUDE bucket, the fixpoint
still correctly appends a terminal fix for it and for anything
transitively citing it, and does so **idempotently** across repeated
rebuilds (verified: 3 consecutive `m.main()` calls hold at 4 records, not
growing).

**Proven by mutant**, the same way as §2.2: reintroduced the exact old
mutate-in-place loop, reran the two new regression tests
(`test_issue88_fixpoint_ignores_a_superseded_record_and_never_mutates_it`,
`test_issue88_fixpoint_appends_a_fix_for_a_genuinely_dangling_authoritative_record`),
both failed reproducing exactly the bogus rewrite described above; restored
the fix, both pass, full suite green.

### 2.4 Defect 3 (BOUNCE, 2026-09-18) — the append-only ordering claim needed a test, not an argument

§2.1 asserted "file order IS append order IS chronological order, by
construction" and named that as the reason precedence is safe without an
explicit ordering field (§3). **That claim is about code, and code can be
edited — asserting it is not the same as guarding it.** Red-reviewer's
gate reintroduced `sorted(deprecations_all, key=lambda x: (x.get("from")
or "", x.get("date") or ""))` immediately after the concatenation in
§2.1, and **the full 356-test suite still passed.** Only a test that
specifically seeds a **date-inverted pair** — a later-appended
(authoritative) record with an *earlier* date than the one it supersedes,
exactly the shape **57 real records in `data/id_deprecations.json`**
already have — catches it: the record **count** stays balanced at 2 while
**which record is authoritative flips** to the stale one. This is working
agreement 6's form (d) precisely: an aggregate (the count) that is
invariant under the error.

**Fixed by adding the missing test**, not by arguing harder:
`tests/test_merge_and_dedupe.py::test_deprecations_file_order_is_never_resorted_even_with_date_inversions`
seeds exactly that date-inverted pair and asserts the file is written in
append order, unchanged, with the later-appended record still last (and
still authoritative) regardless of its date. **Proven to fire**:
reintroducing the same `sorted(...)` mutant against the fixed code makes
this test fail with the authoritative record flipped to the stale
`merged` one; removing the mutant restores a pass. This is the mutation
test §3's Option A discussion originally deferred as "testing §2.1 a
second way" — that reasoning was inverted: **the mutation test is what
makes "by construction" a checked property instead of an assumption**,
and it is now permanent, not deferred.

---

## 3. Item 2 — the record identity key (routed to the user)

**Today:** a deprecation record's identity is `from` alone (a plain
string key). There is **no `schema/id_deprecations.schema.json` today at
all** — the only shape enforcement is `scripts/validate.py`'s referential
check (`check_integrity`), which is structural (does the chain resolve?),
not a schema (there is no enum on `reason`, no type constraint on `into`,
nothing stopping a future record from being malformed in a way JSON
Schema would normally catch). Whatever the user decides below, **schema-architect
is creating this file for the first time**, not amending one.

### Option A — keep `from` as the identity key; formalize last-in-file precedence (implemented)

What §2 already does. A `from` id can have any number of historical
records; the **latest one in file order is authoritative**, and file
order is guaranteed append-only by the code change in §2.1.

- **Cost:** zero schema change, zero data migration, lands with this task.
- **Risk, named honestly:** precedence is **positional** (last in the
  list), not carried by an explicit field on the record itself. It is
  robust *as long as nothing between here and every future reader ever
  reorders the file* — which is exactly the invariant the code now
  enforces mechanically (§2.1) **and now tests directly (§2.4)**, not
  merely argues.
  > **[CORRECTION, dated 2026-09-18 — red-reviewer BOUNCE.]** This bullet
  > originally ended here: *"A recommended, not-yet-implemented
  > hardening: add a mutation test locking `deprecations_all =
  > list(prev_deprec) + fresh` in as intentional... (Not added here
  > because it would be testing the exact code in §2.1 a second way
  > rather than adding new coverage; flagged for whoever next touches
  > this block.)"* **That reasoning was inverted, and the gate said so
  > directly: the mutation test IS the check.** "By construction" is a
  > claim about code that can be edited; without a test that fails when
  > someone re-adds a sort, the construction is an assumption, not an
  > invariant. §2.4 adds exactly this test and proves it fires. Preserved
  > here per agreement 4; treat §2.4 as current, not this parenthetical.
- **Defect 1 (§2.3) is Option A's first real consumer, and it got
  precedence wrong immediately** — not because "latest in file order"
  was the wrong rule, but because a second piece of code (the issue #88
  fixpoint) reasoned about `deprecations_all` without going through that
  rule at all. This is evidence about Option A's fragility, stated here
  for the Recommendation and §8 to weigh, not softened: **Option B is
  immune to this specific failure by construction** — an explicit
  `active: true` field lets any consumer ask "is this record
  authoritative?" locally, per-record, without needing to know it must
  first compute a latest-per-`from` view at all; Option A requires every
  future consumer to remember to do that, and one already didn't.

### Option B — explicit, order-independent identity

Add a synthetic key (e.g. `record_id`, a UUID or monotonically increasing
integer distinct from `from`) to every record, plus an explicit
`active: true`/`superseded_by: "<record_id>"` marker so precedence is
carried **on the record**, not inferred from list position. Resolution
becomes "find the record for this `from` with `active: true`" rather than
"find the last record for this `from`."

- **Cost:** a real schema addition (new required fields), a one-time,
  reviewed migration script touching all 1,051 existing records (not a
  hand-edit — an authored, deterministic migration, same category as the
  §1.4(a) "append nine records" precedent already in `docs/ID_POLICY.md`),
  and `validate.py` gaining a new structural check ("exactly one active
  record per `from`"). None of this is data/schema work I can do in this
  task (routed).
- **Benefit:** precedence survives *any* future reordering, a hand
  migration, a merge-tool combining two branches' deprecation files, or a
  human "cleaning up" the file for readability — none of which Option A
  can promise beyond "the code doesn't do it today."

### Recommendation

**Option A, now — it is what unblocks WS4-T10's remerge with zero schema
risk added to an already time-pressured sequencing (§7) — with Option B
recommended as a deliberate, separately-scheduled hardening task once the
immediate remediation is off the critical path.** The persistence fix in
§2 does not need Option B to be correct; it needs Option A's invariant
(file order = append order) enforced in code, which is now the case and
is tested (§2.4). **This recommendation is unchanged from before the
gate's bounce, and it is not switched quietly: it is weighed against
evidence that cuts against it, not around that evidence.** §2.3's defect
is real, it is Option A's first real consumer getting precedence wrong,
and it would not have been structurally possible under Option B (an
explicit `active` field needs no "which view is authoritative" step at
all). What changed is that Option A is now backed by a fixed and tested
second consumer plus a mutation-tested ordering invariant, not by an
untested argument — which is evidence for the recommendation, but the
recommendation itself is a judgement call about cost-versus-risk, and
**this is my recommendation, not a decision**: the user rules on whether
Option B's extra schema/migration cost is worth taking on now, given that
Option A already produced one real, found-by-review defect, versus later
as a hardening task once the immediate remediation is off the critical
path. Schema-architect is the one who would design and land either
option's schema shape (a fresh `schema/id_deprecations.schema.json`
either way).

**Proposed `docs/ID_POLICY.md` amendment (text only, not committed to that
file by this task — routed to its owner):** append a `§1.4(c)` alongside
the existing `§1.4(a)`/`(b)` precedent, and qualify rule 3 ("the surviving
entry keeps the lower-numbered ID") for the multi-successor case:

> **(c) A retired id may point at more than one successor.** `reason:
> "split"` (a previously over-merged id, corrected) and `reason:
> "resplit"` (a correction to an EARLIER redirect whose target's content
> has since moved) both use an array-valued `into`. Rule 3's "the
> surviving entry keeps the lower-numbered ID" describes the ordinary
> `merged` case only; a split/resplit's retired id keeps **no** id — every
> successor, including whichever one would mechanically have inherited the
> old number, is freshly minted. `resolve_id()` returns `None` for a
> multi-successor record (it has no single canonical successor);
> `resolve_id_group()` returns every live successor a chain (including any
> list-valued hop) reaches.

---

## 4. Item 3 — persisting retired IDs' `source_ids` at deprecation time (implemented, tested)

**Why this blocks any guard:** the WS4-T10 audit's own §8.1 measurement
needed manual `git show <sha>:data/incidents.json` archaeology to recover
8 retired ids' original `source_ids` — and named that **280 of 288**
`merged` records have no other way to recover this at all. A guard that
needs input recoverable only by git archaeology cannot run in CI (agreement
6: "a check whose input does not exist is not a guard").

**Implemented in `scripts/merge_and_dedupe.py`:** a `prev_by_id` map
(built once from `_load_prev_incidents()`, the same previously-published
`incidents.json` `_load_prev_state`/`prev_id_by_key` already derive from)
and a `_retired_fields(old_id)` helper that looks up `old_id`'s own
`source_ids`/`cve_ids` **as of the last committed build** and returns them
as `retired_source_ids`/`retired_cve_ids` — additive fields, omitted
entirely (not written as empty lists) when the prior build has no record
of `old_id` at all, so the field never invents data. Wired into **both**
record-creation sites that retire a previously-published id:
`reason: "merged"` (step 6, `ids_seen[1:]`) and `reason: "transitive-merge"`
(step 6b). `reason: "out-of-scope"` removals (step 6f) are not touched —
those are derived purely from a prior entry no longer being live at all,
so the "does the target still hold my content" question this field exists
to answer does not apply to them (there is no target).

**Tested:** `test_merged_deprecation_persists_retired_source_ids` builds a
two-row prior corpus that merges under a shared CVE and asserts the
surviving deprecation record for the losing id carries exactly its own
prior `source_ids` (`["OECD-AIM-OLD-B"]`), not the survivor's.

**Scope note, stated plainly:** this captures the field **going forward**.
It does nothing for the 288 already-committed `merged` records (0 of them
carry it) — those remain exactly as unverifiable as the T10 audit found
them, until someone runs the same git-archaeology recovery the audit did
and appends the data as a deliberate, reviewed backfill (a `data/` change,
out of this task's scope, and its own decision about whether it's worth
doing retroactively for 280 records versus just going forward from here).

---

## 5. Item 4 — the `resolve_id` multi-successor gap (implemented, tested)

**Verified crash, today, on `main`:**

```
current = deprec[current]   # current is now a list, e.g. ["INC-2", "INC-3"]
while current in deprec ...  # TypeError: unhashable type: 'list'
```

**Fixed** in `src/genai_incidents/__init__.py`: `resolve_id` now checks
`isinstance(current, list)` after each hop and returns `None` immediately
— a list-valued `into` has no single canonical successor, so this is
treated the same as a dangling/unknown id, not a crash. Every existing
single-target chain's behaviour is unchanged (verified: `test_package.py`'s
existing `resolve_id` tests all still pass unmodified).

**Added `resolve_id_group(inc_id) -> list[str]`** for callers that need
every successor of a multi-target record: a recursive walk that fans out
through list-valued hops, is cycle-safe (a node revisited on any branch of
the walk is not re-walked), and de-duplicates while preserving first-seen
order. Returns `[inc_id]` if still active, `[]` if nothing live is
reachable, and every live id a chain (including any list-valued hop)
reaches otherwise.

`scripts/validate.py`'s `check_integrity` had the **identical** latent
crash in its own independent chain-walk (`cur = into_map[cur]` then `cur
in into_map`) — not named in the original brief but found while fixing
item 4, since it's the same shape of bug in a second, independent
implementation. Replaced with `_resolves_to_live()`, a generalization of
the exact original scalar algorithm (verified to preserve all 4 existing
`test_integrity_deprecation_*` tests unmodified) that also resolves a
list-valued `into` (resolves only if **every** element resolves) and
carries cycle-protection across list branches. Three new tests exercise
this directly, including a chain that hops through BOTH a scalar record
and a list-valued one without raising.

**Proven by direct reproduction, not just inference:** ran the pre-fix
chain-walk logic standalone against `deprec = {"INC-1": ["INC-2",
"INC-3"]}` — raises `TypeError: unhashable type: 'list'` exactly as
predicted. Ran `resolve_id`/`resolve_id_group` against the same input
(monkeypatched) — returns `None` / `[]` respectively, no crash.

---

## 6. The guard — named failing input, proven to fire, proven safe on real data today

**`check_deprecation_coverage(data, deprecations, threshold=0.9)`**,
added to `scripts/validate.py` and wired into `check_integrity` (so it
runs as part of the same `python scripts/validate.py` CI already calls).

**What it checks:** for every LIVE (latest-per-`from`) deprecation record
carrying a persisted `retired_source_ids` (§4), the record's resolved
target(s) — unioned across every element if `into` is list-valued — must
hold at least 90% of those source_ids in the CURRENT corpus.

> **[CORRECTION, dated 2026-09-18 — red-reviewer BOUNCE defect 2.]** "The
> record's resolved target(s)" was **not what the first version of this
> guard measured** — it took `into` **literally**
> (`targets = into if isinstance(into, list) else ([into] if into else
> [])`), contradicting its own docstring and this line, while
> `_resolves_to_live` (a chain-resolving walk) already existed in the
> same file, unused for this purpose. On a chained record — `A -> B ->
> C`, `C` live and holding everything `A` had — this reported `0/N` (0%)
> coverage on a perfectly healthy redirect, wired into the path that
> reaches `sys.exit(1)`: **a guard that fires on its own correct input,
> which is the same class of failure as a guard that never fires at all**
> (working agreement 6). Chained records already exist in committed data
> (`INC-08146 -> INC-08139 -> INC-00554`, live). **Fixed** by adding
> `_resolve_live_targets`, a single shared recursive walk (fanning out
> through list-valued hops, cycle-safe) that both `_resolves_to_live` and
> `check_deprecation_coverage` now call — reusing the existing resolution
> logic rather than adding a second independent one, which is exactly how
> the list-`into` `TypeError` ended up needing a fix in two places
> earlier in this same task. **Proven on the real committed chain, not
> only a synthetic one**
> (`tests/test_validate.py::test_deprecation_coverage_resolves_a_real_committed_chain`,
> read-only against `data/incidents.json`/`data/id_deprecations.json`):
> fabricating `retired_source_ids` on `INC-08146`'s real record with a
> source `INC-00554` (the chain's live end) actually holds, the fixed
> guard reports zero problems; reproducing the OLD literal-`into` logic
> against the same real record reports `0.0` coverage — verified directly,
> both ways. `check_integrity` and `check_deprecation_coverage` now also
> share ONE authoritative (latest-per-`from`) view, `_latest_by_from`,
> instead of each building its own — the same fix pattern as §2.3's
> issue-88 fixpoint: one canonical "what does this `from` currently mean"
> answer, computed once, not re-derived per consumer.

**On the 90% threshold — not a round number picked for looks.** It
discriminates only on retired ids with enough sources to make a
percentage meaningful at all: most retired ids carry 1-2 sources, where
coverage can only be 0% or 100% regardless of where the threshold is set.
On the population where it CAN discriminate, **90% permits one dropped
source in a 10+ source set while catching every measured pathology by
30x** — `INC-08139` (2/92 ≈ 2%) and `INC-08185` (2/65 ≈ 3%) are both
caught by any threshold above ~3%, so 90% is chosen for margin against
noise in a not-yet-observed real population, not because it was tuned to
the two known cases; a threshold of 5% would have caught both known
pathologies just as well and bought no headroom against anything else.

**The guard goes live automatically the first time a post-WS4-T15 build
retires an id** (`checked` becomes nonzero in its own printed line) — but
**nothing today asserts that actually happens**, so it could in principle
stay a guard nobody has ever seen fire on real data indefinitely, which is
exactly the "checks that cannot fail" shape working agreement 6 warns
against, from a different angle than defect 2's own false-negative. Coded
recommendation, not implemented in this task: add a follow-up assertion
(CI step or a monitoring check, owner's call) that `checked > 0` once the
first real post-WS4-T15 retirement has landed, so a guard that has never
actually fired on real data cannot be mistaken for one that has, or for
one that never needs to.

**Named failing input (working agreement 6):** the previous guard attempt
(T10 audit §8.3, now superseded) tested "the target holds **at least
one** shared source_id" and was shown to PASS on 4 of 8 measured cases —
`INC-08139` (target held 2 of 92, ≈2%) and `INC-08185` (2 of 65, ≈3%)
among them — because a bare non-empty intersection is satisfied by a
tiny, wrong minority. **Reproduced directly**, not just cited: a crafted
input with a retired id's 92 persisted `retired_source_ids` and a target
holding exactly 2 of them fires this guard —
`"deprecation coverage: INC-OLD -> INC-A resolved target(s) hold only
2/92 (2%) of the retired id's persisted source_ids (threshold 90%)"` —
while a healthy redirect (target holds all of a small retired set) and a
multi-target `resplit` record whose UNION of successors covers the full
retired set both come back clean, and a record with **no** persisted
`retired_source_ids` (every one of today's 288 `merged` records) is
counted separately as `unverifiable`, never silently folded into "0
problems = everything passed."

**Proven safe to land today, read-only against the real committed
data**, not merely argued:

```
$ python scripts/validate.py
13060/13060 entries valid; 0 with errors.
[deprecation-coverage] 0 checked, 1051 unverifiable (no persisted retired_source_ids -- pre-WS4-T15 record)
...
integrity: no duplicate CVE/source keys; all deprecations resolve.
```

Zero of the 1,051 committed records carry `retired_source_ids` yet (the
field is new, populated only going forward per §4), so the guard checks
zero and fails zero — **CI stays green today**, and starts doing real work
the moment the first post-WS4-T15 `merged`/`transitive-merge` record is
written by a future refresh.

**Eight permanent regression tests** (`tests/test_validate.py`) cover: a
list-`into` record resolving when every successor is live; one flagged
when a successor is dangling; the exact crash-shape input surviving
without raising; the coverage guard firing on the 2/92 shape; staying
clean on a healthy redirect and a multi-target union; a legacy
(no-persisted-field) record being reported as unverifiable, not silently
passing; a synthetic chained redirect (`A -> B -> C`) NOT being
misreported as 0% coverage; and the real committed
`INC-08146 -> INC-08139 -> INC-00554` chain resolving cleanly. Two more in
`tests/test_merge_and_dedupe.py` cover the issue-88 fixpoint (§2.3): a
stale record shadowed by a live authoritative one is never mutated and
never wrongly propagated; a genuinely-dangling authoritative record still
gets a correct, idempotent, append-only fix. One more locks in §2.4's
ordering invariant against a date-inverted pair.

---

## 7. Sequencing — getting WS4-T10 onto `main` without CI going red again

This is the practical test the brief names, and it is **not fully solved
by this task alone** — the remaining piece is a deliberate remediation
decision this task is explicitly barred from executing (§0 constraints;
D25(b) reserves the unmerge to the user).

**What CI actually does, confirmed by reading `.github/workflows/validate.yml`:**
`Re-merge from ingest sources` runs `parse_existing.py` +
`merge_and_dedupe.py` **against the committed corpus**, then `Validate
incidents.json against schema` runs `python scripts/validate.py` against
whatever that rebuild just produced **in the checkout, not against
`data/incidents.json` as committed**. This is exactly the mechanism board
entry `8d1b241f` diagnosed: merging WS4-T10's `normalize_url` fix alone
makes this step silently produce 13,361 rows from a 13,060-row commit,
and `validate.py` catches the *symptom* (a mis-keyed override on one of
the new rows) rather than the cause.

**This task's code (§2–§6) changes what happens *after* such a rebuild —
it does not stop the rebuild from happening.** Landing §2–§6 alone and
then remerging WS4-T10 as-is would still silently rebuild to 13,361 rows
every CI run; the only difference is the new rows' deprecation records
would now correctly persist and would, if any of them were malformed,
be caught more precisely by `check_deprecation_coverage`. **It would not
prevent the 301-row change from shipping** — the guard has nothing to
check against yet, because nothing has decided which of the 47 splits are
authorized.

**What actually closes the loop — the "deliberate guard" `8d1b241f`
calls for — is a pre-authorization allowlist enforced at build time,
not just at validate time.** Stated in plain terms, this is everything
that must still happen before WS4-T10 can merge without turning `main`
red:

**(a) A human-reviewed remediation of the 47 splits.** A separate
task/PR, not this one, applies the T10 spec's own hybrid method (§7.2/§8
of that document: per-id title/content continuity comparison between the
currently-published row and the fixed code's natural output) to today's
47 splits, producing a reviewed, committed list of exactly which
`(from, reason)` pairs are AUTHORIZED for this one-time 301-row
transition, alongside the actual data change. **This is a judgement
call, not a computation** — it is the thing actually standing between
the user and an unfrozen corpus, and no code this task or its follow-up
writes substitutes for it.

**(b) A build-time pre-authorization guard.** Not implemented here — it
can only be proven correct by running it against the real 47-split
transition, which this task must not execute. It aborts the build
loudly (nonzero exit, before any file is written) if this build's own
dedupe logic would newly resolve a previously-single published id's
member source_ids to more than one row — i.e. would silently produce a
`split`/`resplit` deprecation — unless that `(from, reason)` pair is on
(a)'s authorized list. This is the mechanical form of D25(a) condition
(2) ("every new `merged` deprecation a refresh would write has been
reviewed") — turning a policy into something CI itself enforces, so a
*future* unreviewed OECD refresh cannot silently re-arm the same trap the
one this document exists because of just did. **Correctly not built
here**: building it blind, without the real transition to test the abort
path against, would itself be a guard nobody has seen fire — exactly the
failure mode this task keeps naming in everything else it built.

**(c) The actual unmerge, in the same PR as (a) and (b).** Reserved to
the user under D25(b). Landing WS4-T10 in the same PR as (a) and (b), per
the T10 spec's own §5.1 option (a) ("keeps the corpus from ever being in
the swapped state, even transiently, in a published build"). Landing
WS4-T10 alone, even with §2–§6's fixes, does not satisfy this — it only
makes the *next* silent rebuild's records survive and resolve correctly,
it does not stop that rebuild from happening unauthorized.

**What §2–§6 omitted, and what this bounce found:** landing this task's
code alone does not merely leave (a)/(b)/(c) undone — **defects 1 and 2
land on exactly the records (a)'s remediation writes.** The remediation
in (a) is precisely what produces the first `split`/`resplit` records
with more than one entry per `from` (a stale `merged` record shadowed by
an authoritative correction) and the first genuine multi-hop chains
through them — the exact shapes §2.3 and §6's corrected guard exist to
handle. Had (a) run against the code as it stood before this bounce, its
own remediation records would have been the first real input to both
bugs: the issue-88 fixpoint could have wrongly nulled a live redirect the
remediation had just written, and the coverage guard would have reported
0% on the remediation's own healthy chained corrections, potentially
blocking a legitimate, reviewed merge on a bug in the code meant to
protect it. Fixing both here, before (a) ever runs, is what makes this
task's code actually load-bearing for (a)/(b)/(c) rather than merely
adjacent to them.

---

## 8. What goes to the user

1. **Item 2, §3: Option A (keep `from`, formalized append-only
   precedence — implemented, zero schema cost) vs. Option B (explicit
   `record_id`/`active` field, schema + migration cost).** Recommendation:
   Option A now, Option B as a separately-scheduled hardening task — but
   **put fairly, not as a foregone conclusion**: §2.3's defect 1 is
   Option A's first real consumer (the issue-88 fixpoint) getting
   precedence wrong immediately, because it reasoned about
   `deprecations_all` without going through the "which record is
   authoritative" rule at all. **Option B is immune to this specific
   failure by construction** — an explicit `active: true` field lets any
   consumer ask "is this record authoritative?" locally and per-record,
   with no dependency on first computing a latest-per-`from` view
   correctly; Option A requires every future consumer to remember to do
   that, and one already didn't. This evidence is presented for the
   user's own weighing, not resolved by this document: Option A is
   recommended because it is cheaper and because the one place it broke
   is now fixed and tested, not because the failure mode it's exposed to
   has gone away.
2. **The `docs/ID_POLICY.md §1.4(c)` amendment text in §3** — policy
   language, not this task's file to edit.
3. **§7's sequencing plan** — specifically, authorizing a follow-up task
   (owner pipeline-engineer, or split further if the user prefers) to (a)
   run the reviewed per-id remediation the T10 spec's §7.2/§8 hybrid
   describes, (b) implement and prove the build-time pre-authorization
   guard against that real data, and (c) remerge WS4-T10 in the same PR.
   This is the piece that actually unblocks D25(a)'s freeze-lift condition
   (2); nothing in this document does that by itself.
4. **A finding for the board, not a decision:** `PROGRESS.md` on `main`
   currently contains **no D26 section and no WS4-T15 task entry** —
   `git merge-base --is-ancestor 9493ba22 0c778ced` (the commit that added
   D26) is `no`; D26 was written only on the (subsequently reverted)
   `ws4/t10-normalize-url` merge, so `fe3a4845`'s revert of `c5c3402e`
   took the D26 ruling and the WS4-T15 board entry out of `main` along
   with the code. `8d1b241f` (the newest commit on `main`, which
   references "D26(b)" and "WS4-T15" as if both are on the board) was
   written *after* that revert without re-adding them. This document does
   not edit `PROGRESS.md` (not this task's file), but the foreman should
   know the board's own record of authorizing this task is not currently
   present on `main`.

---

## 9. Verification recipe

```bash
git fetch origin && git checkout ws4/t15-redirect-persistence
pip install -r requirements.txt

# Full suite — 357 passed (339 on main before this branch).
pytest -q

# The persistence fix, retired-source capture, refusal-to-duplicate guard,
# the date-inversion ordering proof, and the issue-88 fixpoint fix, isolated:
pytest tests/test_merge_and_dedupe.py -q -k "deprecat or retired_source or issue88 or date_inversion"

# resolve_id / resolve_id_group crash fix, isolated:
pytest tests/test_package.py -q -k "resolve_id"

# list-into resolution + coverage guard (including the real-chain proof), isolated:
pytest tests/test_validate.py -q -k "integrity_list_into or deprecation_coverage"

# Guard is a true no-op on today's real committed data (read-only --
# writes nothing under data/):
python scripts/validate.py
#   -> "13060/13060 entries valid; 0 with errors."
#   -> "[deprecation-coverage] 0 checked, 1051 unverifiable ..."
#   -> "integrity: no duplicate CVE/source keys; all deprecations resolve."

# Confirm no data/ or schema/ file was touched by this branch:
git diff --stat origin/main..HEAD -- data/ schema/
#   -> (empty)

# Re-derive the ±1 reconciliation in §1 directly (needs the WS4-T10
# branch's committed audit artifact; does not modify anything):
git fetch origin ws4/t10-normalize-url
git show origin/ws4/t10-normalize-url:docs/audits/WS4-T10-phaseB-delta-2026-09-15.json \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['id_sets']['new_only_count'] - d['id_sets']['gone_count'] == 301
rows = d['splits']['rows']
succ = [s['id'] for r in rows for s in r['successors']]
assert len(succ) == len(set(succ)) == 349  # no internal duplicate in splits.rows
merge_targets = {x['into'] for x in d['new_deprecations']}
assert merge_targets == {'INC-14757'}
assert merge_targets <= set(succ)  # the merge target IS one of the split successors
print('±1 reconciliation re-derived: OK')
"
```
