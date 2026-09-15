# WS4-T10 unmerge design — what happens to PUBLISHED IDs when a fixed
build splits an over-merged row

**Status: RECORD, dated 2026-09-15. DO NOT REGENERATE.** This document lays
out options and a recommendation for the user's decision (D25(b) escalation);
it does not implement any of them. If a later decision changes the
recommendation, add a dated update below naming which half changed — do not
edit the original analysis to make it read as current (working agreement 4).
**Owner of this document:** pipeline-engineer (WS4). **Depends on:**
`docs/audits/E21-tripwire-refresh-2026-09-14.md` (Findings 8/9), D25, and the
WS4-T10 Phase A/B work landed on branch `ws4/t10-normalize-url`
(`75825299` code fix, this commit's predecessor for the Phase B numbers below).

## 1. Why this document exists, not just the code fix

The WS4-T10 code fix (`scripts/merge_and_dedupe.py::normalize_url`) stops
NEW over-merges from happening on a future rebuild. It does **not** by
itself do anything to the corpus already published under the OLD, buggy
`normalize_url` — that corpus ships today with published, cited IDs (e.g.
`INC-00554`) whose 100+ source_ids are mostly unrelated incidents bridged
through collapsed query-string URLs. Applying the code fix to a real build
is a **transformative data operation**: invariant 3 (never delete; status +
tombstone) and invariant 9 (IDs and deprecations append-only, never reused)
both bind here, and a naive "just re-run the build" does something neither
invariant anticipated — an existing PUBLISHED id can end up pointing at
different content than before, not because anyone edited it, but because
dedup's own iteration order picked a different member of a formerly-merged
cluster to keep the id. That is exactly the stable-ID content-swap harm
D25 exists to prevent, demonstrated concretely below (§3).

## 2. Measured facts this design must account for

All figures [R], re-derived 2026-09-15 in a detached scratch worktree pair
(`git worktree add --detach ... eeb7ca9c` for **control**, `... 75825299`
for **fixed**), using the committed ingest inputs only (no network, no
ingest re-runs), running `python scripts/parse_existing.py` then
`python scripts/merge_and_dedupe.py` (Makefile:11-13) in each. **Control
first, and it matters**: the control build (unchanged code) reproduces
committed `data/incidents.json` **byte-identically**
(`sha256 facbf809...e997b14` both sides) — so the fixed-build diff below is
attributable to the code change alone, not to any drift in ingest inputs or
build nondeterminism. The comparison itself
(`diff_corpus.py`, scratchpad-only, not committed) was proven to fire first
on a deliberately corrupted copy (1 title edit + 1 downward severity edit +
1 dropped reference + 1 removed row + 1 injected fake row → all 5 caught,
0 false negatives) before being trusted on the real before/after, per
working agreement 6.

- **Corpus size:** control 13,060 unique rows; fixed 13,361 (**+301**).
  `id_deprecations.json`: control 1,051 entries; fixed 1,052 (**+1**, a
  genuine correction — see §2.3).
- **47 published rows split** under the fix — i.e. 47 old IDs whose member
  source_ids now resolve to more than one new row. Distribution (old row →
  count of new rows its members landed in):

  | splits into | # old rows |
  |---|---|
  | 2 | 17 |
  | 3 | 9 |
  | 4 | 4 |
  | 5 | 4 |
  | 6 | 1 |
  | 7 | 2 |
  | 8 | 2 |
  | 11 | 2 |
  | 12 | 2 |
  | 17 | 1 |
  | 22 | 1 |
  | 31 | 1 |
  | 100 | 1 |

- **48 common rows changed** at least one field (of 13,059 rows common to
  both builds). Per-field change counts (top ones): `references` 48,
  `source_count`/`source_ids` 47, `mitre_atlas` 32, `nist_ai_rmf` 31,
  `mitre_atlas_tactics`/`owasp_asi` 30, `owasp_llm` 29, **`severity` 26**,
  `cve_ids` 11, `tags`/`capec_ids`/`cwe_ids` 9–10, `date`/`description`/
  `title` 5, others ≤3.
- **Severity: 26 changes, all DOWNWARD** (e.g. `Critical`→`High`,
  `Critical`→`Medium`, `High`→`Medium`). Direction is exactly what's
  expected: splitting removes inflated-severity contamination that
  `merge_into`'s "pick higher severity" rule (`merge_into` :1892-1901)
  picked up from unrelated absorbed rows. **This is severity correction,
  not severity loss** — no invariant governs severity direction, but it is
  the same *shape* of harm named in this task's brief (downward severity
  revisions must not be silently dropped) — here the fix is what produces
  the correction, so it must ship WITH its record, not separately.
- **Invariant 4 (`added` immutable; `updated` bumps only on content
  change): 0 violations either direction** — every one of the 48
  content-changed common rows got an `updated` bump, and no row was
  bumped without a content change.
- **Invariant 9 (append-only, never reused): confirmed clean.** Every
  freshly-minted id in the fixed build (302 new-only ids) is numerically
  greater than the prior corpus's max id (`INC-14604`); none reuse a
  `from` id out of control's own 1,051 deprecations. `_load_prev_state`'s
  monotonic counter (scripts/merge_and_dedupe.py:1087-1143) is why this
  holds mechanically, not by luck: it scans the *prior build's own*
  `incidents.json` for the max numeric id ever assigned, and because ids
  are minted monotonically build-over-build, that max is always ≥ any
  id that has ever been deprecated away, however deep the deprecation
  chain.
- **References:** 47 common rows lost references (correctly — the
  references that belonged to now-split-off unrelated content left with
  it); 1 gained (`INC-08183`, see §2.2, a byproduct of that row's own
  anchor changing).

### 2.1 INC-00554's full decomposition

Old `INC-00554` ("Tesla Driver Reportedly Said Driver-Assistance Mode Was
Engaged During Fatal Texas Home Crash", 103 source_ids) splits into **100**
new rows. The two real AIID/OECD sources for the actual Tesla incident
(`AIID-1552`, `OECD-AIM-2026-06-30-4590`) land together on **`INC-14609`** —
a **brand-new id**, not `INC-00554`. The id `INC-00554` itself is claimed by
a **different, unrelated pair** (`AIID-1446` /
`OECD-AIM-2026-04-02-c3bb`, "KBS AI Translation Subtitles Reportedly
Broadcast Profanity During Artemis II Launch Livestream"), because that pair
happened to be earlier in ingest processing order. The other ~97 of the 100
splits are each their own single-source OECD-AIM row — genuinely unrelated
Korean-language stories (bank anti-phishing launches, wildfire drones,
defense-industry MOUs, deepfake-election-law enforcement, …), consistent
with the audit's characterization.

**This is the concrete demonstration of the harm this document exists to
solve**: a naive re-run of the fixed code does not give the real Tesla
incident back its own stable, cited id — it hands that id to an unrelated
story, while the real incident gets a fresh id nobody has ever cited.
Whoever cited `INC-00554` for the Tesla crash (the site's per-incident page,
a STIX/MISP UUID minted from it, an external paper) would silently start
pointing at Korean subtitle-profanity coverage.

### 2.2 Other stable IDs that swap content (the harm in general)

Five common IDs change `title` **and** `description` to unrelated topics
under a naive rebuild:

| ID | old title | new title |
|---|---|---|
| `INC-00311` | AI-Driven Military Targeting Causes Mass Casualties in Middle East Conflicts | Greek Tax Authority Plans AI System to Combat Tax Evasion |
| `INC-00554` | Tesla Driver ... Fatal Texas Home Crash | KBS AI Translation Subtitles ... Profanity ... |
| `INC-00754` | ChatGPT Was Alleged to Have Aided Planning of Florida State University Mass Shooting | Purportedly AI-Generated Jason Momoa Deepfake Used in Romance Scam ... |
| `INC-01897` | The Tag, Category, and Taxonomy Manager — AI Autotagger ... (WordPress) | The Website LLMs.txt plugin for WordPress is vulnerable to Reflected XSS ... |
| `INC-08183` | Google Bard Conversation Exfiltration | Malicious Models on Hugging Face |

These are the exact same class of harm as §2.1, at smaller scale (2–14 old
source_ids each, vs. 103). **Any option below must treat all 47 split rows
uniformly** — §2.1 is not a special case requiring bespoke handling.

### 2.3 The fix also RECOVERS a true duplicate the bug was hiding

Not every population change is a split. `INC-07738` ("Anthropic's Mythos AI
Raises Global Cybersecurity Concerns", `OECD-AIM-2026-04-08-e597`) and
`INC-00623`'s `OECD-AIM-2026-04-27-eb9a` member are two OECD-AIM articles
about the *same* real event that the old code kept apart — apparently
because one of them was captured into an unrelated over-merged cluster
before the two could ever meet in `by_url`/`by_title`. Under the fix they
correctly merge into a single new row (`INC-14757`), and the fixed build's
`id_deprecations.json` correctly records `{"from": "INC-07738", "into":
"INC-14757", "reason": "merged"}` — the **only** new deprecation entry the
fixed build wants to add. **This confirms the fix improves recall as well
as precision**: it is not a blanket "un-merge everything" operation, and
any unmerge design must not assume splitting is the only kind of change a
fixed rebuild produces.

### 2.3b A curation override already mis-keys under the fix — measured, not hypothetical

The board's remediation item F flagged `curation_overrides.json`'s
by-any-member-source_id keying (merge_and_dedupe.py:1498-1507) as a risk
**[A]**. It is now **[R]**, and it already fires on today's 47 splits:
`CVE-2025-10875`'s override (`{"discovery_method": "security-researcher",
"_note": "...Noma Labs discovers and reports the vulnerability to
Salesforce (ForcedLeak)..."}`) was written for old `INC-02590`
("ForcedLeak – Salesforce Agentforce indirect prompt injection exfiltrates
CRM data"). Under the fix, `CVE-2025-10875` splits off onto a **new,
unrelated** row (`INC-14614`, "Improper Neutralization of Input Used for
LLM Prompting ... Mulesoft Anypoint Code Builder ... Code Injection") while
`INC-02590` keeps the ForcedLeak title but loses `CVE-2025-10875` from its
`source_ids`. Result: the override's `discovery_method` (and its
ForcedLeak-referencing `_note`) now silently lands on the Mulesoft
Anypoint row it was never written for, and the real ForcedLeak row
(`INC-02590`) silently loses a label it should keep.
**This is the exact same failure mode as §2.1/§2.2 — a stable identity
resolving to the wrong content — but for override data instead of the
core content fields**, and it is worse in one respect: `curation_overrides.json`
is hand-authored, so nobody re-reviews it on every rebuild the way this
measurement re-derived `data/incidents.json` — a wrong application here
would ship silently. **Every remediation option in §3 must re-key or
re-verify affected overrides, not just re-derive `id_deprecations.json`.**

### 2.4 The fix's precision, confirmed on named megaclusters

The board's own remediation table listed `INC-04106` (174), `INC-04260`
(143), `INC-01015` (120), `INC-08766` (68) as "whether CVE megaclusters are
URL-bridged: [A]" (unmeasured). **Now measured [R]: none of the five named
non-CVE/CVE-shielded megaclusters change at all** —
`INC-04106`/`INC-04260`/`INC-01015`/`INC-08766`/`INC-03798` keep identical
`source_ids` counts and titles in both builds. Their size is real, not a
query-string artifact.

A title-similarity scan (`difflib.SequenceMatcher` > 0.55, a cheap proxy for
"these two split-off rows might actually be the same incident wrongly
separated") over all 47 split groups' sibling pairs found **58 pairs above
threshold and, on manual review of the top matches, zero regressions**:
every high-similarity pair inspected turned out to be **distinct** entities
sharing a templated report format — e.g. two different VS Code extensions
(`SakaDev` / `AI Code`) with disjoint CVEs (`CVE-2026-30306` /
`CVE-2026-30304`) reported through an identical boilerplate sentence and
previously bridged only because both entries' `marketplace.visualstudio.com
/items?itemName=` reference collapsed to the same key under the old
normalizer; similarly for an Apache JSPWiki CVE pair
(`CVE-2022-34158`/`CVE-2022-28731`) bridged via
`jspwiki-wiki.apache.org/Wiki.jsp?page=`. **This means the query-string
collapse bug was never limited to Korean CMS URLs** — any host whose
canonical resource identity lives in the query string (VS Code marketplace
listings, MediaWiki-style `?page=` URLs, `cve.org/cverecord?id=`,
`bugzilla...cgi?id=`, …) was equally exposed. **Caveat, stated plainly: this
was a targeted scan on a similarity proxy, not an exhaustive hand-check of
all 47×(splits) sibling pairs** — it is evidence the fix is precise on the
population it could practically inspect, not a formal proof of zero
regressions corpus-wide. WS4-T5 (P1, dedupe error-rate audit, 100 merges +
100 near-misses hand-verified) is the task that closes that gap
properly and should sample deliberately from this split population when it
runs.

## 3. Options for what a real remediation does to published IDs

All options assume: (a) the code fix ships first (already done, Phase A);
(b) remediation is a **separate, deliberate, reviewed operation**, not an
automatic side effect of the next scheduled rebuild — the fixed code must
not silently rewrite 47 published IDs' content the next time `make build`
runs against real refreshed ingest data. That in turn means: **until
remediation ships, the fixed `normalize_url` must not be allowed to touch
the 47 already-published over-merged rows' identity resolution on a live
rebuild** — see §5 for what this requires structurally (it is more than
"the code is correct now").

### Option 1 — survivor keeps the id; split-off parts get new ids + a `split` deprecation-like record

The row that would be chosen anyway by the rebuild's own tie-break (or,
better, a *curated* choice — see §4) keeps its existing id and all its
existing citations stay valid for whatever content it retains. Every
split-off part gets a brand-new id (mechanically already guaranteed unique
and non-reused, §2 confirms this). A **new record type** is appended to
`id_deprecations.json` — schema-architect's call on shape, but conceptually:
`{"from": "INC-00554", "into": ["INC-14609", "INC-14610", ...],
"reason": "split", "date": "..."}` (an array `into`, unlike today's
single-target `merged` records) — or, if the schema owner prefers to keep
`into` singular, one `reason: "split"` record per (old, new) pair sharing a
`split_group` key. Either shape needs a **third value distinct from
`merged`** so a consumer walking deprecations can tell "this id's content
moved because it was ALWAYS the same incident" (`merged`) from "this id's
content moved because it never should have been one incident"
(`split`) — conflating them would make `merged` retroactively mean
"maybe the same incident, maybe not," undermining every existing reader
that treats `merged` as a same-incident assertion (e21 audit Finding 4's
whole point).

- **Consumer impact:** the split-off ids are wholly new — nothing external
  has ever cited them, so no external break. The **survivor's own citers**
  are the risk: if the survivor is chosen to be whichever piece keeps the
  MOST source_ids (a defensible default), for `INC-00554` that is NOT the
  real Tesla incident (2 sources) but likely one of the singleton or small
  OECD-only pieces — actually for `INC-00554` every split piece has 1–2
  sources, so "most sources" is a near-tie and still arbitrary. **A purely
  mechanical tie-break cannot recover "the real incident" here** — this is
  exactly why §4 recommends a curated choice for at least the
  highest-source-count splits.
- **`id_deprecations.json` schema changes needed** (schema-architect's
  call; listed, not implemented here): a `reason: "split"` enum value; an
  `into` field that is array-valued for this reason (or a `split_group`
  linking key if `into` must stay a scalar); validator support so
  `scripts/validate.py` doesn't reject the new shape.
- **E21 tripwire / `curation_overrides.json` interaction:** the override
  keying at merge_and_dedupe.py:1498-1507 applies by ANY member
  `source_id` — an override keyed to a source_id that ends up on a
  split-off row (not the survivor) silently stops applying to the row it
  was written for and starts applying to whichever unrelated row that
  source_id landed on instead. **Confirmed already happening**: of 176
  current override keys, 1 (`CVE-2025-10875`, §2.3b) collides with today's
  47 splits, misapplying a ForcedLeak-specific `discovery_method` label to
  an unrelated Mulesoft Anypoint row. Every one of the 47 split rows'
  member source_ids must be cross-checked against
  `curation_overrides.json` and re-keyed to the correct successor as part
  of remediation — not merely re-verified at remediation time against a
  fresh snapshot (§2.3b shows this is a live defect today, not a
  theoretical future risk). The **tripwire replacement** (board's item E,
  a stable-ID continuity check: "a common id whose title changes while its
  anchor source did not") should be run as an *acceptance gate* on the
  remediation PR itself, precisely because it would have caught
  §2.1/§2.2's content swaps — but note it would NOT by itself catch
  §2.3b's override mis-keying, which needs its own check (every override
  key still resolves to a row whose content is consistent with the
  override's own `_note`, where one exists).

### Option 2 — retire the over-merged id entirely; mint new ids for every part

`INC-00554` (and all 46 other split ids) get tombstoned with
`reason: "split"`, pointing at ALL successor ids (no survivor keeps the old
id). Summing the distribution table (§2), the 47 old rows resolve to **349
total successor rows** — under today's actual (unremediated) tie-break
behavior 47 of those 349 keep an existing id and 302 are freshly minted
(exactly the measured new-only count); under Option 2 every one of the 349
gets a fresh id, since none of the 47 old ids survive.

- **Consumer impact:** strictly larger break than Option 1 in one narrow
  sense — under Option 1 every one of the 47 old ids keeps resolving
  directly to SOME row (right or wrong content), while under Option 2 all
  47 stop resolving directly and instead point at a deprecation record with
  multiple successors, so every citer of every one of the 47 (not just the
  ones whose "real" content moved) has to follow a disambiguation step
  instead of landing straight on a row. For the site's per-incident pages
  and any STIX/MISP UUIDs minted from these 47 ids, that is 47
  disambiguation targets to publish. **This "break" is honest, though**:
  Option 1's alternative isn't "no break," it's "no VISIBLE break" — a
  citer following `INC-00554` under Option 1 lands on a row instantly, but
  per §2.1 it is very likely the WRONG row, silently. Option 2 trades an
  visible extra click for never silently serving the wrong incident.
- **Cleaner semantically**: no id ever silently starts meaning something
  else — every retirement is unambiguous, so there's no tie-break to get
  wrong and no curated-choice burden. This is the option that makes the
  fewest CLAIMS: it doesn't assert "we know which surviving piece deserves
  the old citation," which for `INC-00554` (§2.1) is honestly not
  mechanically knowable.
- **`id_deprecations.json` schema:** same `reason: "split"` need as Option
  1, but `into` is ALWAYS array-valued (never a single survivor), which is
  a simpler, more uniform shape than Option 1's split personality (some
  `merged`-like single-target records, some `split`-like multi-target
  ones) — arguably easier for schema-architect and easier for consumers
  to reason about ("does this id have one #into or several — that alone
  tells me whether it split").
- **Curation-override / tripwire interaction:** same fix requirement as
  Option 1 (§2.3b's `CVE-2025-10875` override must be re-keyed), but
  simplified to apply — there is no "does the override still land on the
  survivor" question, because there is no survivor; every override's
  source_id must simply be re-resolved to its (single,
  now-guaranteed-correct) new row.

### Option 3 — hybrid: Option 2 by default, Option 1 only where a curated survivor choice exists

Retire every split id (Option 2's clean semantics) UNLESS a human reviewer
has recorded which successor is "the same incident, just correctly
separated from the noise" — which for most of the 47 splits (§2.4: mostly
genuinely-unrelated single-source rows glommed together) there simply
isn't one, but for a handful the old id's title/description plausibly
matches ONE clear successor closely enough that retiring it feels like
pointless churn (e.g. if a future split's survivor keeps ~90% of the
CONTENT-relevant signal and just sheds a few miscategorized source_ids —
none of the 47 measured today are this shape, since even the LEAST
lopsided among them, per §2.1/§2.2, hand the old id to unrelated content
under the mechanical tie-break). **Given what's actually measured, this
degrades to Option 2 for all 47 current splits** — its only advantage
over pure Option 2 is not foreclosing a cheap survivor-keeps-id path for
some *future*, more lopsided split (e.g. a row that splits into one
90-source piece and one 1-source outlier), which Option 2 alone would
also retire needlessly.

## 4. Recommendation

**Option 2** (retire every split id; mint new ids for every successor;
`reason: "split"`, `into` always array-valued), **with Option 3's
opt-in curated-survivor escape hatch reserved for future splits that are
measurably lopsided** (a future split where one successor keeps
>90% of the split id's source_ids AND a human confirms the retained
content is still about the same incident) but **not exercised on any of
today's 47**, because none of them qualify — §2.1 and §2.2 show the
mechanical "biggest piece" tie-break does not track "the real incident"
even once in the sample inspected.

Reasons, weighed against the measurements above:
1. Every one of the 5 titled content-swap examples (§2.2) and the flagship
   `INC-00554` decomposition (§2.1) shows the id-continuity tie-break
   picking the WRONG piece to keep the stable id, not merely an arbitrary
   one. A design that keeps asserting "this id's content is still
   basically the same incident" (Option 1) when the measured evidence is
   the opposite would re-introduce exactly the silent-wrong-redirect harm
   D25 was raised to stop, just with better paperwork around it.
2. Option 2's uniform, unambiguous `reason: "split"` semantics (no id ever
   silently means something else) is what a citer, a STIX consumer, or the
   site's own redirect page needs: "this id doesn't mean one thing anymore,
   here are its N successors" is honest; "this id means something now but
   it used to mean 97 other things too" is not a claim anyone should have
   to parse.
3. The consumer cost Option 2 pays over Option 1 — all 47 old ids requiring
   a disambiguation step instead of resolving straight to a row — is small
   relative to the citation-correctness gain, since Option 1 does not
   actually avoid needing that same disambiguation UI (a survivor still has
   46+ siblings a reader may be looking for); Option 1 just hides the need
   behind a survivor id that, per §2.1/§2.2, is frequently the WRONG one to
   have hidden it behind.

## 5. What must happen before any OECD refresh could merge under D25(a)

D25(a)'s freeze-lift conditions are (i) this fix and (ii) a same-incident
review of new merges. This document adds the structural piece condition
(i) actually implies but doesn't spell out:

1. **The code fix (Phase A, done) must not be allowed to touch the 47
   already-published split rows' identity resolution on an ordinary
   scheduled rebuild** until the chosen remediation option (§4) has run.
   Concretely: a rebuild run today, with no further change, WOULD already
   silently produce §2's content swaps the next time CI runs `make build`
   — the fix being correct is not the same as it being safe to let run
   unattended against the current committed corpus. This needs either (a)
   the remediation (§4) landing in the SAME PR/session as the point where
   the freeze lifts (recommended — keeps the corpus from ever being in the
   swapped state, even transiently, in a published build), or (b) an
   explicit, temporary guard in `merge_and_dedupe.py` that refuses to ship
   a build where a previously-single id's member source_ids now resolve to
   >1 row without a corresponding `reason: "split"` deprecation already on
   file (a mechanical version of the "stable-ID continuity check" the
   board's remediation item E already calls for) — belt-and-suspenders,
   catches the case even if (a)'s ordering is violated by a future change.
2. **Every one of the 47 split rows' member source_ids must be re-keyed
   against `curation_overrides.json`** — §2.3b already found and named a
   live instance (`CVE-2025-10875`) in TODAY's snapshot; remediation must
   fix that one specifically and re-run the same cross-check against
   whatever is committed at remediation time, since a further ingest
   refresh before then could introduce others.
3. **The tripwire replacement (board item E)** should ship as part of the
   same remediation, not after — it is the acceptance gate that proves the
   remediation didn't introduce a NEW silent content swap of its own.
4. **This document's Phase B numbers are a snapshot of the CURRENT
   committed corpus** (`eeb7ca9c` baseline). An OECD refresh landing before
   remediation ships would change which rows are affected and by how much;
   whoever executes remediation must re-run Phase B's measurement against
   whatever is committed at that time, not copy these numbers forward.

## 6. What this document does NOT decide

Per protocol step 8, the following are the user's call, not pre-decided
here: which option (§4 is a recommendation); whether remediation is its own
task/PR separate from the freeze-lift PR or bundled with it; the exact
`id_deprecations.json` schema shape (schema-architect's call, options
listed in §3 only to inform that call, not to preempt it).
