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
(`75825299` code fix, this commit's predecessor for the Phase B numbers below
— **[Revision 2 dated note] superseded as the Phase A commit by `883707c7`;
see §7**).

> ## ⚠ REVISION 2 — 2026-09-15 (red-reviewer BOUNCE #1 on `c9424935`)
> **Revision 2 (§7, at the end of this document) SUPERSEDES the
> recommendation in §4 and several figures in §2 below.** Red-reviewer's
> gate found the original Option 2 recommendation was measured only on
> the 5 rows that already looked like content swaps — selection bias — and
> that the FULL 47-row population tells a different story (43/47 keep
> title continuity; only 4 break it). It also found `INC-08183` was a
> **false split the code itself introduced** (a `web_view` blocklist
> miss), corpus-wide reference restoration was undercounted, and
> `validate.py` **already fails closed today** via one mis-keyed
> `curation_overrides.json` entry. §1 is preserved as written and still
> correct on the mechanism/why; §2, §3 and §4 below are preserved
> VERBATIM as the ORIGINAL analysis and are marked in place at each
> refuted passage — **read them as history, not as current** for anything
> a Revision-2 marker flags; §7 has the corrected figures and
> recommendation. `docs/audits/WS4-T10-phaseB-delta-2026-09-15.json` /
> `.md` are the re-derived, committed evidence behind Revision 2.

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
  **[Revision 2, dated note]** This count was **48** against the ORIGINAL
  `c9424935` code. After the BOUNCE #1 `web_view` blocklist fix (§7),
  `INC-08183` no longer changes at all, so the figure is **47** as of
  `883707c7` — see `docs/audits/WS4-T10-phaseB-delta-2026-09-15.md`.
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
  **[Revision 2, dated note — this whole bullet is superseded, not just
  refined.]** "1 gained" was a **per-row reference-COUNT** comparison,
  which undercounts: it misses same-count swaps and doesn't measure the
  corpus-wide picture. Red-reviewer's gate, measuring at the distinct-URL
  level, found **7 common rows gain 8 never-shipped URLs; corpus-wide 379
  distinct reference URLs newly shipped, 0 lost.** Re-derived against the
  BOUNCE #1-fixed code (`883707c7`): **377 distinct, 0 lost** (the -2 is
  the web_view fix removing `INC-08183`'s own false extra reference plus
  one further blocklist-driven shift; see
  `docs/audits/WS4-T10-phaseB-delta-2026-09-15.md`'s defect-4 section for
  the full accounting). `INC-08183` itself no longer gains a reference at
  all post-fix (§7, §2.2's note below).

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

**[Revision 2, dated note.]** `INC-08183` in this table is a **different
kind of bug than the other four, and is now fixed.** Its `source_ids` were
IDENTICAL in both builds (it was never a split at all) — the swap was
caused by a `?&web_view=true`-tagged reference keying apart from its bare
twin (a blocklist miss the code fix itself introduced, since `web_view`
wasn't yet on the tracking-param blocklist when this table was written),
which split the row's own references across two dedup keys and flipped
its anchor. BOUNCE #1 fixed this (`883707c7`, blocklists `web_view`);
`INC-08183` no longer appears in the delta at all as of that commit — see
`docs/audits/WS4-T10-phaseB-delta-2026-09-15.md`'s defect-2 section. It
stays in this table, struck through in spirit but not in text (agreement
4: this is the original analysis, preserved), as the found-then-fixed
example of the DISTINCT harm class §7 discusses: a **non-split** stable-ID
content swap, which is why the design's guard (§5.1(b)) must cover ALL
common IDs' title/anchor continuity, not just IDs the split-detection
logic flags.

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

**[Revision 2, advisory A5.]** Note what this merge does to `INC-07738`
specifically: it is an **intact, previously-published id that gets
retired into a fresh id (`INC-14757`) even though nothing was wrong with
its own content** — it simply stops being its own row because a genuine
duplicate was found. This is avoidable churn from the citer's perspective
(a working id disappears for a reason that has nothing to do with THAT
id being wrong), and neither this document's split-focused options (§3)
nor §5's guard proposal originally covered it, because it isn't a split.
**The design must also cover this shape**: any remediation/guard built
for splits should treat a "merge that retires an intact id" the same
way — flag it for the same D25(a)(2) same-incident human review a refresh
merge gets, precisely because `merged` is supposed to be a same-incident
assertion (§3, Option 1's discussion) and this is the first concrete case
of the FIX itself producing one, not a refresh. No committed data changes
under this decision; it's a scope note for whoever executes remediation
and for D25(a)(2) review generally.

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

> **[Revision 2, dated note — this ENTIRE section is SUPERSEDED, not
> refined.]** This recommendation was built on a claim — "the mechanical
> tie-break does not track the real incident even once" — that turned out
> to be measured only on the 5 title-swap rows themselves (selection
> bias), not the full 47-row population. Measured on all 47: **43 keep
> title continuity, only 4 break it.** §4 as originally written below is
> preserved verbatim for the record; **§7 has the corrected recommendation
> (a hybrid, not pure Option 2) and is the one to act on.**

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
   scheduled rebuild** until the chosen remediation option (§4, superseded
   by §7) has run.
   Concretely: a rebuild run today, with no further change, WOULD already
   silently produce §2's content swaps the next time CI runs `make build`
   — the fix being correct is not the same as it being safe to let run
   unattended against the current committed corpus.
   **[Revision 2, dated note — the mechanism was right, the described
   FAILURE MODE was wrong; corrected in §7.]** This originally said the
   risk was a FUTURE, hypothetical "next `make build`" silently shipping
   swaps. Measured instead: `python scripts/validate.py` on the
   BOUNCE #1-fixed build **already exits 1 TODAY** — "1 entr(ies) carry
   discovery_method outside the landmark tier (e.g. `INC-14614`)", the
   `CVE-2025-10875` mis-keyed override from §2.3b. That means
   `.github/workflows/validate.yml` ("Validate incidents.json against
   schema"), `auto-refresh.yml` and `cve-enrich.yml` (both "Re-merge +
   render + validate") all **fail closed right now** if this branch's
   code runs — a real safety net, but a single point of failure: it is
   exactly the ONE override item 2 below tells remediation to re-key, and
   once THAT alone is done with no continuity guard in place, an ordinary
   rebuild would ship §2.1/§2.2's swaps with `validate.py` passing clean.
   §7 restates this requirement with the override re-keying and the
   continuity guard sequenced to land together, not the override first.
   This needs either (a)
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
here: which option (§4 is a recommendation, superseded by §7); whether
remediation is its own task/PR separate from the freeze-lift PR or bundled
with it; the exact `id_deprecations.json` schema shape (schema-architect's
call, options listed in §3 only to inform that call, not to preempt it).

## 7. Revision 2 — 2026-09-15 (red-reviewer BOUNCE #1 on `c9424935`)

**This section supersedes §4's recommendation and the figures §2/§5.1
mark above.** Evidence: `docs/audits/WS4-T10-phaseB-delta-2026-09-15.json`
/ `.md`, re-derived against the BOUNCE #1-fixed code (`883707c7`), full
47-row split population (not a sample), committed and re-runnable.

### 7.1 What changed and why the recommendation flips

§4's Option 2 rested on: "the mechanical tie-break does not track the real
incident even once in the sample inspected." That sample was the 5 rows
that already looked like swaps (§2.2's table) — a selection-biased sample
BY CONSTRUCTION, since it was drawn by looking for swaps. Measured on the
full 47-row split population (`splits.rows` in the JSON, every row, not a
sample):

- **43 of 47 splits keep title continuity**: the successor that keeps the
  old id also keeps the old title — i.e. the CURRENTLY PUBLISHED content
  matches what the fixed code's own tie-break naturally produces for that
  id. `INC-02671` (Grok NCII, keeps 17/18 source_ids, sheds one unrelated
  robotic-lawnmower row) is the representative case, not an outlier.
- **Only 4 break continuity**: `INC-00311`, `INC-00554`, `INC-00754`,
  `INC-01897` — the same four from §2.2's table (`INC-08183` is NOT one of
  these four; it was never a split — §2.2's dated note).
- **Continuity does not correlate with source-count retention.**
  `INC-00861` keeps only 2/32 (6%) of its source_ids yet keeps the right
  title; `INC-00554` similarly keeps only 2/103 (2%) but picks the WRONG
  content. Source-count share is not the signal; **title continuity
  between the currently-published row and the fixed code's own natural
  output for that id IS the signal**, and it is directly measurable, once,
  for a one-time remediation — see 7.2.

### 7.2 Corrected recommendation: a measured hybrid, not blanket Option 2

**For each of the 47 (and, in a future remediation, however many) split
ids, compare the CURRENTLY PUBLISHED title/content to what the fixed
code's own mechanical tie-break naturally produces for that same id**
(exactly what the committed delta's `survivor_title_continuity` field
measures). This single, one-time, per-id comparison decides the option:

- **Where continuity holds (43/47 today): Option 1, and — this is the
  simplification the original §3 discussion missed — it needs NO special
  `id_deprecations.json` schema entry at all.** The split-off members
  never had a separate published id of their own; they were always
  embedded inside the single over-merged row. There is nothing to
  "deprecate FROM" for them — they simply appear as ordinary new rows on
  the next build, exactly like any newly-ingested content would. The old
  id keeps its id, its title, and every existing citation resolves
  correctly, because the content genuinely didn't change. **This is not
  Option 1 as originally scoped ("keep IDs and hope a mechanical tie-break
  picked right, or curate a choice") — it's a MEASURED confirmation that
  the tie-break's choice matches today's published content**, which
  removes the "purely mechanical tie-break cannot recover the real
  incident" objection §3's Option 1 discussion raised, for exactly these
  43 rows.
- **Where continuity breaks (4/47 today: `INC-00311`, `INC-00554`,
  `INC-00754`, `INC-01897`): Option 2.** These are the rows where the
  measured evidence directly shows the mechanical tie-break picks WRONG
  content — retire the old id with a NEW `reason: "split"` deprecation
  record pointing at every successor (`into` array-valued, per §3's
  Option 2 schema discussion, which stands unchanged), and mint a fresh
  id for every one of that old id's successors, INCLUDING the piece that
  would otherwise have mechanically inherited the old id. No survivor
  keeps the old id for these four.
- **`INC-08183`-shaped non-split swaps (§2.2's dated note): covered by the
  SAME continuity check, run over ALL common ids, not just ids the
  split-detector flags.** This is what closes BOUNCE #1 defect 2d: the
  design's guard (§5.1(b), restated below) checks title/anchor continuity
  on every common id every build, independent of whether that id's
  source_ids changed at all — `INC-08183` had UNCHANGED source_ids and
  still needed exactly this check to catch its swap (it's already fixed
  as a bug, but the class of harm it represents needs the general guard,
  not just the specific `web_view` blocklist entry).

**This recommendation needs less schema work than §4's blanket Option 2,
not more**: only 4 rows (today) need a `reason: "split"` deprecation
record at all; 43 need nothing beyond what an ordinary rebuild already
does correctly. The `reason: "split"` enum value and array-valued `into`
are still needed (schema-architect's call on exact shape, per §3/§6) —
just for a much smaller, precisely-identified population.

### 7.3 Sequencing (supersedes §5's item order)

The override re-keying (§5 item 2, `CVE-2025-10875`) and the continuity
guard (§5 item 1(b)) **must land in the same change, not the override
first.** §5.1's dated note above shows why: `validate.py` failing today is
a real but SINGLE-POINT safety net — re-keying that one override without
the guard removes the only thing currently standing between an ordinary
rebuild and shipping §2.1/§2.2's swaps clean. Concretely, before the
freeze can lift under D25(a):
1. Apply 7.2's per-id decision to today's 47 (4 retirements + 349 total
   successor rows, 43 of them needing no deprecation record).
2. Re-key or fix the `CVE-2025-10875` override (§2.3b) as part of the same
   change.
3. Land the continuity guard (checks ALL common ids' title/anchor
   consistency across a rebuild, not just split-flagged ones) in the same
   PR, so `validate.py` (or an equivalent gate) would catch a FUTURE
   instance of either harm class before it ships, not just the two
   instances already found and fixed by hand.
4. Then the freeze-lift conditions in D25(a) apply as originally stated.

### 7.4 Advisory A5 — restated (see §2.3's dated note for the finding)

The design must also treat a **merge that retires an intact published
id** (the Mythos case, `INC-07738` → `INC-14757`) as needing the same
D25(a)(2) same-incident human review a refresh merge gets — it is a
`merged` deprecation, so the existing same-incident review already
nominally covers it, but this document did not originally call it out as
a case that review needs to specifically look for (an id disappearing not
because it was wrong, but because a genuine duplicate was found). No
schema change needed; a scope note for whoever runs D25(a)(2) review.

### 7.5 What this section still escalates to the user (unchanged from §6)

The hybrid in 7.2 is a recommendation, not a decision: the user still
rules on (a) whether to adopt 7.2's per-id continuity-based hybrid over a
blanket option, (b) remediation sequencing/PR structure, and (c) the exact
`id_deprecations.json` schema shape for the `reason: "split"` records the
4 continuity-breaking rows need (schema-architect's call).
