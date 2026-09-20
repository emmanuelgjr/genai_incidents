"""Validate data/incidents.json against schema/incident.schema.json, and
data/source_freshness.json against schema/source_freshness.schema.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]

try:
    import jsonschema
except ImportError:
    print(
        "jsonschema is required. Run `pip install -r requirements.txt`.",
        file=sys.stderr,
    )
    sys.exit(2)

# Inclusion-policy gate: reuse the one strict matcher (INCLUSION.md §4).
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from merge_and_dedupe import is_out_of_scope_malware
except Exception:  # pragma: no cover - keep validate runnable in isolation
    is_out_of_scope_malware = None  # type: ignore

# WS4-T21 BOUNCE #3: the `from`/`into` deprecation-chain walker is SHARED
# with scripts/merge_and_dedupe.py (its step 8a resplit-redirect
# correction), not duplicated -- see `resolve_live_targets`'s docstring
# there for why the canonical implementation lives in that module (import
# direction: this file already imports FROM merge_and_dedupe above, so the
# reverse would be circular) and for the invariant the two call sites must
# jointly preserve. Unlike `is_out_of_scope_malware` above, there is no
# safe no-op fallback for this one -- every integrity/coverage check below
# depends on it -- so a failed import is fatal here, not swallowed.
from merge_and_dedupe import resolve_live_targets as _resolve_live_targets

_RESOLVABLE_URL = re.compile(r"^(https?://|mailto:)", re.I)


def _has_primary_source(entry: dict) -> bool:
    return any(_RESOLVABLE_URL.match((r.get("url") or "").strip())
              for r in (entry.get("references") or []))


def check_integrity(data: dict, deprecations: list[dict] | None = None) -> list[str]:
    """Cross-entry invariants the JSON schema can't express. Returns a list
    of violation messages (empty == clean).

    1+2. No CVE id or source_id may be held by two live entries. Dedupe
         guarantees each maps to exactly one incident; a duplicate means
         content was silently split across records — the failure mode of the
         2026-06 dedupe tombstone bug. This is the machine check for the
         audit done by hand when that bug was fixed.
    3.   id_deprecations referential integrity: every deprecated `from` id
         must resolve through its `into` chain to a live entry (or be an
         `into:null` removal), and no deprecated id may still be live.
    4.   Evidence gate (INCLUSION.md): every entry must carry at least one
         resolvable http(s)/mailto primary-source reference.
    5.   Scope gate (INCLUSION.md): no out-of-scope malicious-package entry
         may survive — makes the v2.3.1 scope-purge a hard, enforced
         invariant so the generic-malware noise can never return.
    6.   Landmark-label gate (#74): `reversibility_class` and
         `discovery_method` are landmark-tier, evidence-gated labels. `tier`
         is re-derived every build, so an entry drifting out of the landmark
         set must fail loudly rather than ship a stale editorial judgment on
         a feed record.
    """
    problems: list[str] = []
    incidents = data["incidents"]
    live_ids = {e["id"] for e in incidents}

    for field in ("cve_ids", "source_ids"):
        holders: dict[str, str] = {}
        for e in incidents:
            for key in e.get(field) or []:
                if key in holders:
                    problems.append(
                        f"{field} {key!r} held by both {holders[key]} and {e['id']}"
                    )
                else:
                    holders[key] = e["id"]

    # 4) Evidence gate — every entry needs a resolvable primary source.
    no_source = [e["id"] for e in incidents if not _has_primary_source(e)]
    if no_source:
        problems.append(
            f"{len(no_source)} entr(ies) lack a resolvable primary source "
            f"(e.g. {', '.join(no_source[:5])})"
        )

    # 5) Scope gate — no out-of-scope malicious-package entry may survive.
    if is_out_of_scope_malware is not None:
        oos = [e["id"] for e in incidents if is_out_of_scope_malware(e)]
        if oos:
            problems.append(
                f"{len(oos)} out-of-scope malicious-package entr(ies) survived the "
                f"scope purge (e.g. {', '.join(oos[:5])})"
            )

    # 6) Landmark-label gate — evidence-gated labels only on the landmark tier.
    for label_field in ("reversibility_class", "discovery_method"):
        mislabeled = [e["id"] for e in incidents
                      if e.get(label_field) and e.get("tier") != "landmark"]
        if mislabeled:
            problems.append(
                f"{len(mislabeled)} entr(ies) carry {label_field} outside the "
                f"landmark tier (e.g. {', '.join(mislabeled[:5])})"
            )

    if deprecations is not None:
        # Latest-in-file record wins for a repeated `from` (WS4-T15): the
        # build only ever appends, never reorders or collapses, so file
        # order is chronological order and last-in-file is the current,
        # authoritative record for that id. `_latest_by_from` is the ONE
        # place that computes this view -- every consumer below (the
        # referential-integrity walk, the coverage guard, and the
        # issue-88 fixpoint in merge_and_dedupe.py, which mirrors this
        # same rule) must read it from here, not re-derive its own,
        # because a second independent derivation is exactly how the
        # list-`into` crash ended up fixed in two places instead of one.
        latest = _latest_by_from(deprecations)
        into_map = {f: r.get("into") for f, r in latest.items()}
        # 'removal' deprecations (into=null, e.g. reason 'out-of-scope') legitimately
        # don't resolve to a live entry — the incident was dropped, not merged.
        removed_ids = {f for f, r in latest.items() if r.get("into") is None}
        for frm, into in into_map.items():
            if frm in live_ids:
                problems.append(f"deprecated id {frm} is still a live entry")
            if into is None:
                continue  # removal, not a merge — nothing to resolve
            if not _resolves_to_live(into, into_map, live_ids, removed_ids):
                problems.append(
                    f"deprecation {frm} -> {into} does not resolve to a live entry"
                )
        problems.extend(check_deprecation_coverage(data, deprecations, _latest=latest))
    return problems


def _latest_by_from(deprecations: list[dict]) -> dict[str, dict]:
    """The single authoritative (latest-in-file-wins) view over a
    deprecations list, for a given `from`. WS4-T15's persistence fix
    (`scripts/merge_and_dedupe.py`) guarantees file order is append order
    is chronological order, so "latest in the list" is "most recently
    decided" by construction -- every consumer that needs to know which
    record is CURRENTLY authoritative for a `from` (not every record that
    has ever existed for it) must go through this function."""
    latest: dict[str, dict] = {}
    for d in deprecations:
        f = d.get("from")
        if f:
            latest[f] = d
    return latest


# `_resolve_live_targets` -- the `from`/`into` chain-walker used below by
# `_resolves_to_live` and `check_deprecation_coverage` -- is imported from
# `merge_and_dedupe.resolve_live_targets` at module load (see the import
# block near the top of this file for why the shared copy lives there, not
# here). Kept as a module-level name via that import so every existing
# call site in this file (and `tests/test_validate.py`, via `v._resolve_live_targets`)
# is unchanged.


def _resolves_to_live(
    start_into, into_map: dict, live_ids: set[str], removed_ids: set[str],
) -> bool:
    """True if `start_into` (a `from`'s `into` value) transitively
    resolves to a live entry (every element, if list-valued — WS4-T15
    `split`/`resplit`), OR terminates in a recorded `into: null` removal
    (a citation of a withdrawn id is a valid, honest answer, not a
    dangling one — `check_deprecation_coverage` does not need this half;
    it wants live targets only, via `_resolve_live_targets` directly)."""
    if isinstance(start_into, list):
        return bool(start_into) and all(
            _resolves_to_live(t, into_map, live_ids, removed_ids) for t in start_into
        )
    if _resolve_live_targets(start_into, into_map, live_ids):
        return True
    # No live id reached -- still a valid resolution if the walk instead
    # terminates in a node that is ITSELF a recorded removal.
    seen: set[str] = set()
    cur = start_into
    while cur in into_map and cur not in live_ids and cur not in seen:
        seen.add(cur)
        nxt = into_map[cur]
        if isinstance(nxt, list):
            return _resolves_to_live(nxt, into_map, live_ids, removed_ids)
        cur = nxt
    return cur in removed_ids


def check_deprecation_coverage(
    data: dict,
    deprecations: list[dict],
    threshold: float = 0.9,
    _latest: dict[str, dict] | None = None,
) -> list[str]:
    """WS4-T15 guard: for every LIVE (latest-per-`from`) deprecation record
    that carries a persisted `retired_source_ids` (only true for records
    written by a build after WS4-T15 landed — see `_retired_fields` in
    `scripts/merge_and_dedupe.py`), the record's RESOLVED target(s) — the
    live id(s) its `into` chain actually reaches today, via
    `_resolve_live_targets`, not the literal `into` value on the record —
    must still hold at least `threshold` of those source_ids in the
    CURRENT corpus. A record whose `into` chains through one or more
    further redirects before reaching a live id (already present in
    committed data, e.g. `INC-08146 -> INC-08139 -> INC-00554`) is
    measured against the CHAIN'S live end, not the immediate hop — taking
    `into` literally previously reported 0% coverage on a perfectly healthy
    chained redirect, which is exactly the "checks that cannot fail"
    shape working agreement 6 warns about: a guard that fires on its own
    correct input is worse than one that never fires at all.

    Named failing input (working agreement 6): a redirect whose target has
    drifted to hold only a small minority of what the retired id actually
    contained — exactly the shape the WS4-T10 unmerge design's own audit
    found passing a bare "target holds >=1 shared source_id" check
    (`INC-08139`: target held 2 of 92; `INC-08185`: 2 of 65 — both ~2-3%,
    both would PASS a non-empty-intersection test and both FAIL this one).
    The 90% threshold is deliberately far above the failure line, not a
    round number picked for looks: it discriminates only on retired ids
    with enough sources to make a percentage meaningful at all (most
    retired ids carry 1-2 sources, where coverage can only be 0% or 100%
    regardless of threshold); on the population where it CAN discriminate,
    90% permits one dropped source in a 10+ source set while still
    catching every measured pathology (2%, 3%) by roughly a 30x margin —
    headroom against noise, not precision tuned to the two known cases.

    A record with no persisted `retired_source_ids` (every `merged` record
    written before this landed — 288 of them today, none yet carrying the
    field) is counted as `unverifiable`, reported separately, and never
    silently treated as passing — an all-zero-checked run must be visible
    as zero, not indistinguishable from "everything passed". **This guard
    goes live automatically the first time a post-WS4-T15 build retires an
    id** (`checked` becomes nonzero) — nothing today asserts that actually
    happens; the recommended follow-up (§6 of the WS4-T15 design doc) is a
    CI or monitoring assertion that `checked > 0` once the first real
    retirement lands, so this does not quietly stay a guard nobody has
    ever seen fire on real data.
    """
    problems: list[str] = []
    id_to_sources: dict[str, set[str]] = {
        e["id"]: set(e.get("source_ids") or []) for e in data.get("incidents", []) if e.get("id")
    }
    live_ids = set(id_to_sources.keys())
    latest = _latest if _latest is not None else _latest_by_from(deprecations)
    into_map = {f: r.get("into") for f, r in latest.items()}
    checked = 0
    unverifiable = 0
    for frm, rec in latest.items():
        retired = rec.get("retired_source_ids")
        if not retired:
            unverifiable += 1
            continue
        into = rec.get("into")
        targets = _resolve_live_targets(into, into_map, live_ids)
        held: set[str] = set()
        for t in targets:
            held |= id_to_sources.get(t, set())
        retired_set = set(retired)
        overlap = len(retired_set & held)
        coverage = overlap / len(retired_set) if retired_set else 1.0
        checked += 1
        if coverage < threshold:
            problems.append(
                f"deprecation coverage: {frm} -> {into} (resolved: {sorted(targets)}) "
                f"hold(s) only {overlap}/{len(retired_set)} ({coverage:.0%}) of the "
                f"retired id's persisted source_ids (threshold {threshold:.0%})"
            )
    print(
        f"[deprecation-coverage] {checked} checked, {unverifiable} unverifiable "
        "(no persisted retired_source_ids -- pre-WS4-T15 record)"
    )
    return problems


# --- Source-freshness provenance: the enumerated contexts ------------------
#
# `observed_from` in data/source_freshness.json is a claim about WHICH copy of
# the source-health counter the registry's machine-derivable values were
# reconciled against. Every claim that is legitimate is enumerated below,
# together with what it means and what the checker does about it. Anything not
# enumerated FAILS.
#
# Why an allowlist and not "compare when the named copy is readable, skip when
# it isn't": readability is not authorisation. Under the readability rule any
# string that failed to name the in-repo copy made the whole comparison vanish
# and returned zero problems, so a one-line edit to a hand-authored JSON file
# deleted the check, and "checked and matched" was indistinguishable from "not
# checked at all" in the build output. A skip is now something only a named,
# reasoned context can buy — and an unrecognised claim is the failure case, not
# the free-pass case.
#
# Adding a context is a deliberate act: add it here AND to `observed_from`'s
# enum in schema/source_freshness.schema.json (kept in lockstep by
# tests/test_validate.py) AND to the Source freshness section of
# docs/DATA_DICTIONARY.md, in one PR.

IN_REPO_STATE_REL = "ingest/_state/source_health.json"
PROVENANCE_IN_REPO = f"main:{IN_REPO_STATE_REL}"
PROVENANCE_AUTHORITATIVE = f"refresh-state:{IN_REPO_STATE_REL}"

PROVENANCE_CONTEXTS: dict[str, dict[str, str]] = {
    PROVENANCE_IN_REPO: {
        "mode": "compare",
        # `means` is interpolated into printed output: ASCII only, because this
        # script runs in the build path on consoles that are not always UTF-8.
        "means": "the bootstrap copy committed on main: present in every "
                 "checkout, and stale by design per D5",
        "checker": "full comparison: the named copy must exist, its source key "
                   "set must equal the registry's, and every `status` and "
                   "`last_success` must match. Missing file or mismatch fails.",
    },
    PROVENANCE_AUTHORITATIVE: {
        "mode": "not-comparable",
        "means": "the authoritative machine counter, which exists only on the "
                 "refresh-state branch (D5)",
        "checker": "no comparison is possible in this context and none is "
                   "attempted: that copy is not in a main checkout, and "
                   "reaching it needs network, which the build path forbids. "
                   "Reported as NOT COMPARABLE, never as verified. The "
                   "comparison for this claim is the weekly reconciliation "
                   "inside auto-refresh.yml, at the one point where the "
                   "authoritative counter is in the tree (D8 application spec "
                   "§6b — specified, not yet implemented).",
    },
}

# Outcome tokens. `verified` and `not-comparable` are deliberately distinct:
# one is a comparison that ran and passed, the other a comparison that could
# not run here and says so. Conflating them is the defect this replaced.
PROV_VERIFIED = "verified"
PROV_NOT_COMPARABLE = "not-comparable"
PROV_FAILED = "failed"


class ProvenanceResult(NamedTuple):
    """Outcome of the provenance check, kept separate from `problems` so the
    build output can distinguish "checked and matched" from "not checkable in
    this context" — and so neither can be read off an empty problem list."""

    outcome: str          # PROV_VERIFIED | PROV_NOT_COMPARABLE | PROV_FAILED
    summary: str          # one line for build output, states which happened
    problems: list[str]   # non-empty iff outcome is PROV_FAILED


def check_registry_provenance(registry: dict, state_path: Path) -> ProvenanceResult:
    """Hold the registry to the provenance claim it makes about ITSELF.

    data/source_freshness.json is a reviewed publication, not a build output:
    it carries curatorial facts no counter holds (`stale_since` from run-log
    evidence, a dated `hold`, the `row_marker` selectors, the `coverage`
    statement). It is therefore hand-authored in a gated task — and that is
    exactly why its machine-derivable half must not be taken on trust.

    `observed_from` must be one of the contexts enumerated in
    :data:`PROVENANCE_CONTEXTS`, and the outcome is that context's:

    * `main:ingest/_state/source_health.json` — the copy every checkout has.
      Compared in full: source key sets must agree and every `status` /
      `last_success` must match, so a forged status, a back-dated
      `last_success`, a fifth tracked source left unregistered, or a named
      copy that isn't there fails loudly instead of drifting.
    * `refresh-state:ingest/_state/source_health.json` — the authoritative
      counter, which is not in a main checkout and cannot be fetched from the
      build path. Reported NOT COMPARABLE HERE: a registry legitimately
      reconciled against the fresher copy must not be failed by the one D5
      leaves stale, but that outcome is a named context with a stated reason,
      not something inferred from a string failing to match.
    * anything else — FAILS. Unrecognised, misspelt, empty: a provenance claim
      nothing can check is not a weaker check, it is no check.

    Bounded on purpose, and the summary says so: VERIFIED means the registry
    matches the copy it says it read. Because that copy is stale by design it
    does NOT mean the registry is current. Currency is the weekly
    reconciliation against the authoritative counter (D8 application spec §6b);
    this is the offline half.
    """
    claimed = (registry.get("observed_from") or "").strip()
    context = PROVENANCE_CONTEXTS.get(claimed)
    if context is None:
        allowed = ", ".join(repr(k) for k in PROVENANCE_CONTEXTS)
        return ProvenanceResult(
            PROV_FAILED,
            f"FAILED: observed_from {claimed!r} is not a recognised provenance "
            "context, so nothing about this registry's values was checked",
            [f"source_freshness registry: observed_from is {claimed!r}, which is "
             f"not one of the enumerated provenance contexts ({allowed}). An "
             "unrecognised provenance claim FAILS: a claim nothing can check is "
             "not a weaker check, it is no check. If a new context is "
             "legitimate, enumerate it in PROVENANCE_CONTEXTS in "
             "scripts/validate.py (with what it means and what the checker does "
             "for it), in observed_from's enum in "
             "schema/source_freshness.schema.json, and in "
             "docs/DATA_DICTIONARY.md - otherwise correct the claim."],
        )

    if context["mode"] == "not-comparable":
        return ProvenanceResult(
            PROV_NOT_COMPARABLE,
            f"NOT COMPARABLE HERE: the registry names {claimed} ({context['means']}); "
            "its shape was validated and its values were NOT compared against that "
            "copy in this context. A recognised offline context, not a pass",
            [],
        )

    # mode == "compare": the named copy must be here, and must agree.
    if not state_path.exists():
        return ProvenanceResult(
            PROV_FAILED,
            f"FAILED: the registry names {claimed}, which is not readable in this "
            "context; a compare-mode claim whose copy is missing fails rather than "
            "skipping",
            [f"source_freshness registry: observed_from claims {claimed!r} "
             f"but that file does not exist (looked in {state_path})"],
        )

    problems: list[str] = []
    state = json.loads(state_path.read_text(encoding="utf-8"))
    sources = registry.get("sources") or {}
    if sorted(state) != sorted(sources):
        problems.append(
            f"source_freshness registry: observed_from claims {claimed!r}, whose "
            f"source keys are {sorted(state)}, but the registry tracks {sorted(sources)}"
        )
    for key in sorted(set(state) & set(sources)):
        for field in ("status", "last_success"):
            claimed_val, actual = sources[key].get(field), state[key].get(field)
            if claimed_val != actual:
                problems.append(
                    f"source_freshness registry: {key}.{field} is {claimed_val!r} but "
                    f"{claimed} says {actual!r}"
                )
    if problems:
        return ProvenanceResult(
            PROV_FAILED,
            f"FAILED: the registry claims {claimed} but disagrees with it in "
            f"{len(problems)} place(s) (listed below)",
            problems,
        )
    return ProvenanceResult(
        PROV_VERIFIED,
        f"VERIFIED: the registry matches {claimed}, the copy it names "
        f"({len(sources)} source key(s), status + last_success each). Bound: it "
        "matches the copy it read; that is NOT a claim the registry is current, "
        "because that copy is stale by design (D5). Currency is the weekly "
        "reconciliation",
        [],
    )


def check_source_freshness(data: dict, registry: dict) -> list[str]:
    """Cross-check every entry's `source_freshness` marker against the
    published registry (data/source_freshness.json). Returns violation
    messages (empty == clean).

    The marker is DERIVED — inherited by reference from the registry, never
    authored per row — so every part of it must be reconstructable from the
    registry plus the entry's tags. These checks are what make that true
    rather than merely documented:

    1. Registry self-consistency: `coverage.tracked` must be exactly the key
       set of `sources`, so the stated coverage can't drift from the actual.
    2. Every key a row lists must exist in the registry.
    3. Every listed source must be `stale`. `degraded` deliberately does not
       propagate to rows (see the schema), and a source that is `ok` marking
       rows would be a straightforward falsehood.
    4. Every listed source must actually propagate — a row may not claim
       freshness from a source whose `row_marker` is null (enrichment-only).
    5. The row must carry each listed source's `row_marker` tag: a marker on
       an entry the source never touched is a fabricated provenance claim.
    6. `as_of` must equal the EARLIEST `last_success` among the listed
       sources — the conservative choice, and the only deterministic one.
    7. `sources` must be sorted, so the field is byte-stable across builds.

    COMPLETENESS — that every entry carrying a stale source's `row_marker`
    tag actually has the marker — is checked separately, by
    :func:`check_freshness_completeness`, landed in the same PR as the
    marking data (D8 application spec §6a). It was deliberately absent
    before that PR: adding it before the data carried the markers would
    have failed the build on the very state this task exists to fix.
    """
    problems: list[str] = []
    sources = registry.get("sources") or {}

    tracked = registry.get("coverage", {}).get("tracked") or []
    if sorted(tracked) != sorted(sources):
        problems.append(
            "source_freshness registry: coverage.tracked "
            f"{sorted(tracked)} != sources keys {sorted(sources)}"
        )

    for e in data["incidents"]:
        marker = e.get("source_freshness")
        if not marker:
            continue
        listed = list(marker.get("sources") or [])
        if listed != sorted(listed):
            problems.append(f"{e['id']}: source_freshness.sources is not sorted")
        tags = set(e.get("tags") or [])
        last_successes = []
        for key in listed:
            src = sources.get(key)
            if src is None:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, which is not in "
                    "data/source_freshness.json"
                )
                continue
            if src.get("status") != "stale":
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, whose registry "
                    f"status is {src.get('status')!r}, not 'stale'"
                )
            row_marker = src.get("row_marker")
            if row_marker is None:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, which does not "
                    "propagate to rows (row_marker is null)"
                )
            elif row_marker.get("value") not in tags:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r} but the entry does "
                    f"not carry its row_marker tag {row_marker.get('value')!r}"
                )
            if src.get("last_success"):
                last_successes.append(src["last_success"])
        if last_successes:
            expected = min(last_successes)
            if marker.get("as_of") != expected:
                problems.append(
                    f"{e['id']}: source_freshness.as_of is {marker.get('as_of')!r}; "
                    f"earliest last_success of its sources is {expected!r}"
                )
    return problems


def check_freshness_completeness(data: dict, registry: dict) -> list[str]:
    """Completeness gate (D8 application, landed with the marking data —
    see the application spec's §6a).

    :func:`check_source_freshness` only checks that markers PRESENT are
    consistent with the registry. It does not check that markers that
    SHOULD be present ARE — that gate is this function, and it is what
    makes the marking non-optional from here on: for every registry source
    that is `stale` and propagates to rows (`row_marker` is not null),
    every entry carrying that source's `row_marker` tag must list that
    source in its `source_freshness.sources`. A future build that silently
    stopped deriving the marker would fail this loudly, instead of quietly
    reverting to the pre-D8 state where 1,380 AIRI-derived rows read as
    current with nothing in the data being individually false.
    """
    problems: list[str] = []
    sources = registry.get("sources") or {}
    for key, src in sources.items():
        if src.get("status") != "stale":
            continue
        row_marker = src.get("row_marker")
        if row_marker is None:
            continue
        tag = row_marker.get("value")
        for e in data["incidents"]:
            if tag not in (e.get("tags") or []):
                continue
            listed = (e.get("source_freshness") or {}).get("sources") or []
            if key not in listed:
                problems.append(
                    f"{e['id']}: carries tag {tag!r} of stale source {key!r} but its "
                    f"source_freshness marker does not list it (marker: {e.get('source_freshness')!r})"
                )
    return problems


def main():
    schema = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    errors = 0
    for i, entry in enumerate(data["incidents"]):
        errs = list(validator.iter_errors(entry))
        if errs:
            errors += 1
            if errors <= 20:
                print(f"\n{entry.get('id','?')}: {entry.get('title','')[:60]}")
                for e in errs:
                    path = ".".join(str(p) for p in e.path)
                    print(f"  - {path}: {e.message}")
    total = len(data["incidents"])
    print(f"\n{total - errors}/{total} entries valid; {errors} with errors.")

    dep_path = ROOT / "data" / "id_deprecations.json"
    deprecations: list[dict] = []
    if dep_path.exists():
        deprecations = json.loads(dep_path.read_text(encoding="utf-8")).get(
            "deprecations", []
        )
    problems = check_integrity(data, deprecations)

    # Source-freshness registry: shape, then the row markers that inherit
    # from it. Freshness is a property of the SOURCE; the per-row marker is
    # a derived projection, so both halves are validated together.
    fresh_schema_path = ROOT / "schema" / "source_freshness.schema.json"
    fresh_path = ROOT / "data" / "source_freshness.json"
    if fresh_schema_path.exists() and fresh_path.exists():
        fresh_schema = json.loads(fresh_schema_path.read_text(encoding="utf-8"))
        registry = json.loads(fresh_path.read_text(encoding="utf-8"))
        shape_errs = list(
            jsonschema.Draft202012Validator(fresh_schema).iter_errors(registry)
        )
        for err in shape_errs:
            path = ".".join(str(p) for p in err.path)
            problems.append(f"source_freshness registry: {path}: {err.message}")
        if not shape_errs:
            prov = check_registry_provenance(registry, ROOT / IN_REPO_STATE_REL)
            problems.extend(prov.problems)
            problems.extend(check_source_freshness(data, registry))
            problems.extend(check_freshness_completeness(data, registry))
            marked = sum(1 for e in data["incidents"] if e.get("source_freshness"))
            stale = sorted(
                k for k, v in (registry.get("sources") or {}).items()
                if v.get("status") == "stale"
            )
            print(
                f"source freshness: registry valid ({len(registry.get('sources') or {})} "
                f"source(s), observed_at {registry.get('observed_at')}); "
                f"{len(stale)} stale ({', '.join(stale) or 'none'}); "
                f"{marked} entr(ies) carry a source_freshness marker."
            )
            # Separate line, and never silent: a reader of build output must be
            # able to tell a provenance comparison that RAN and passed from one
            # this context could not run. Kept off the line above so the D8
            # delta audit's verbatim quote of it stays accurate.
            print(f"source freshness provenance: {prov.summary}.")
        else:
            print(
                "source freshness provenance: NOT CHECKED: the registry failed "
                "shape validation (see the violations below); provenance is checked "
                "only against a well-formed registry."
            )
    else:
        problems.append(
            "source_freshness: data/source_freshness.json or its schema is missing"
        )

    if problems:
        print(f"\n{len(problems)} integrity violation(s):")
        for p in problems[:20]:
            print(f"  - {p}")
    else:
        print("integrity: no duplicate CVE/source keys; all deprecations resolve.")

    sys.exit(1 if (errors or problems) else 0)


if __name__ == "__main__":
    main()
