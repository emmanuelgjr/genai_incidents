"""Validate data/incidents.json against schema/incident.schema.json, and
data/source_freshness.json against schema/source_freshness.schema.json."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
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


def _check_counts(data: dict) -> list[str]:
    """``incident_count + retracted_count + unverified_count == len(incidents)``
    (WS4-T2; D130). ``unverified_count`` is a required envelope key, 0
    included (user ruling D135)."""
    incidents = data["incidents"]
    n_ret = sum(1 for e in incidents if e.get("status") == "retracted")
    n_unv = sum(1 for e in incidents if e.get("status") == "unverified")
    problems = []
    if data.get("retracted_count", 0) != n_ret:
        problems.append(f"retracted_count {data.get('retracted_count', 0)} != {n_ret} retracted entries")
    if "unverified_count" not in data:
        problems.append("envelope lacks unverified_count (required, 0 included; D135)")
    elif data["unverified_count"] != n_unv:
        problems.append(f"unverified_count {data['unverified_count']} != {n_unv} unverified entries")
    if data.get("incident_count", len(incidents)) + n_ret + n_unv != len(incidents):
        problems.append(
            f"incident_count {data.get('incident_count')} + {n_ret} retracted + {n_unv} unverified "
            f"!= {len(incidents)} entries")
    return problems


def check_envelope(data: dict) -> list[str]:
    """``incident_count + retracted_count + unverified_count == len(incidents)``."""
    return _check_counts(data)


def _schema_allows_disputed(schema: dict) -> bool:
    try:
        return "cve-disputed" in schema["properties"]["status_reason"]["properties"]["code"]["enum"]
    except KeyError:
        return False


def check_status(data: dict, rejected: set[str] | None = None,
                 disputed: set[str] | None = None) -> list[str]:
    """WS4-T2 status/retraction invariants (never-delete: a retracted entry
    stays, marked). Returns violation messages (empty == clean).

    * ``status`` and ``status_reason`` appear together.
    * ``rejected_cve_ids`` is a subset of ``cve_ids``; a retracted entry's
      equals its ``cve_ids`` (retraction means ALL its CVEs are rejected).
    * ``incident_count + retracted_count + unverified_count == len(incidents)``
      and each count equals the number of entries with that status.
    * ``unverified`` (D130) carries ``status_reason.code ==
      "no-confirmed-source"``; it may replace ``disputed`` (see below).
    * Against the committed CVE-state snapshot (``rejected``): every REJECTED
      CVE carried by any entry is flagged on it. This is the check that fails
      when the merge rule is skipped or an entry ships a rejected CVE unmarked.
    * ``disputed`` (v2.13.0 item 3): ``status: disputed`` carries
      ``status_reason.code == "cve-disputed"`` (and ``retracted`` carries
      ``cve-rejected``); a disputed entry is never ``confidence: high`` (the
      merge lowers it one level, and the unlowered rule would be high only at
      the top); against the snapshot's disputed set, a ``disputed`` entry has
      at least one disputed CVE, and an entry resting only on disputed/rejected
      CVEs that is neither retracted, disputed nor unverified is a violation.
      An ``unverified`` entry that would otherwise be disputed keeps the
      disputed confidence lowering (never ``high``).
    """
    problems: list[str] = []
    incidents = data["incidents"]
    for e in incidents:
        has_s, has_r = "status" in e, "status_reason" in e
        if has_s != has_r:
            problems.append(f"{e['id']}: status and status_reason must appear together")
        cves = set(e.get("cve_ids") or [])
        flagged = set(e.get("rejected_cve_ids") or [])
        if not flagged <= cves:
            problems.append(f"{e['id']}: rejected_cve_ids {sorted(flagged - cves)} not in cve_ids")
        if e.get("status") == "retracted" and flagged != cves:
            problems.append(f"{e['id']}: retracted but rejected_cve_ids != cve_ids")
        want_code = {"retracted": "cve-rejected", "disputed": "cve-disputed",
                     "unverified": "no-confirmed-source"}.get(e.get("status"))
        if want_code and (e.get("status_reason") or {}).get("code") != want_code:
            problems.append(f"{e['id']}: status {e['status']!r} must carry status_reason.code {want_code!r}")
        if e.get("status") == "disputed" and e.get("confidence") == "high":
            problems.append(f"{e['id']}: disputed entry still has confidence 'high' (must be lowered)")
        if disputed is not None:
            standing = (rejected or set()) | disputed
            if e.get("status") == "disputed" and not cves & disputed:
                problems.append(f"{e['id']}: status disputed but none of its CVEs is disputed in the snapshot")
            if (cves & disputed and cves <= standing and set(e.get("source_ids") or []) <= standing
                    and e.get("status") not in ("retracted", "disputed", "unverified")):
                problems.append(f"{e['id']}: rests only on disputed CVE(s) {sorted(cves & disputed)} but is not marked disputed")
            if (e.get("status") == "unverified" and e.get("confidence") == "high"
                    and cves & disputed and cves <= standing and set(e.get("source_ids") or []) <= standing):
                # D130 advisory E: unverified replaces disputed but keeps its lowering.
                problems.append(f"{e['id']}: unverified entry resting on disputed CVE(s) has confidence 'high'")
        if rejected is not None:
            missed = sorted((cves & rejected) - flagged)
            if missed:
                problems.append(f"{e['id']}: carries REJECTED CVE(s) {missed} without a rejected_cve_ids flag")
            if (cves and cves <= rejected and set(e.get("source_ids") or []) <= rejected
                    and e.get("status") != "retracted"):
                problems.append(f"{e['id']}: rests only on REJECTED CVE(s) {sorted(cves)} but is not retracted")
    problems += _check_counts(data)
    return problems


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
        problems.extend(check_release_scoped_deprecations(data, deprecations, _latest=latest))
    return problems


def check_release_scoped_deprecations(
    data: dict, deprecations: list[dict], _latest: dict[str, dict] | None = None,
) -> list[str]:
    """v2.13.0 / D49: cross-record rules for release-scoped records (those
    carrying `valid_for_releases`). The per-record shape is
    schema/id_deprecations.schema.json's job; these are the rules a
    per-record schema cannot express.

    (a) The LAST record for a `from` that has scoped records must itself be
        unscoped. This is what keeps every last-record-wins reader (the
        v2.11.0/v2.12.0 packages, `_latest_by_from` above, a direct JSON
        reader following the published rule) from mistaking a scoped answer
        for the release-independent one.
    (b) A `from`'s scoped records cover disjoint release sets, so a
        (id, release) pair has exactly one answer.
    (c) Every scoped `into` resolves to a live entry (or an `into: null`
        removal) through the authoritative chain.

    Named failing inputs (agreement 6): append a scoped record after the
    restatement (a); give two scoped records of one `from` a shared
    release (b); point a scoped record at a nonexistent ID (c)."""
    problems: list[str] = []
    live_ids = {e["id"] for e in data["incidents"]}
    latest = _latest if _latest is not None else _latest_by_from(deprecations)
    into_map = {f: r.get("into") for f, r in latest.items()}
    removed_ids = {f for f, r in latest.items() if r.get("into") is None}
    seen_releases: dict[str, dict[str, int]] = {}
    for n, d in enumerate(deprecations):
        if "valid_for_releases" not in d:
            continue
        frm = d.get("from")
        if "valid_for_releases" in latest.get(frm, {}):
            problems.append(
                f"release-scoped record #{n} ({frm}): the last record for {frm} is "
                "release-scoped; it must be followed by an unscoped record"
            )
        for rel in d.get("valid_for_releases") or []:
            prev = seen_releases.setdefault(frm, {}).get(rel)
            if prev is not None:
                problems.append(
                    f"release-scoped records #{prev} and #{n} ({frm}) both claim {rel}"
                )
            seen_releases[frm][rel] = n
        into = d.get("into")
        if not isinstance(into, str) or not _resolves_to_live(
            into, into_map, live_ids, removed_ids
        ):
            problems.append(
                f"release-scoped record #{n} ({frm} -> {into!r}) does not resolve "
                "to a live entry"
            )
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
    8. `review_by` (v2.13.0, D57) must equal the EARLIEST `hold.until`
       among the listed sources, and be absent iff none carries a hold.
       That every `stale` source carries a hold is the registry schema's
       job (its stale-requires-hold rule), checked by the shape pass.

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
        # 8. (v2.13.0, D57) `review_by` must equal the EARLIEST registry
        #    `hold.until` among the listed sources, and be absent iff none of
        #    them carries a hold. Registry content only; no date maths against
        #    today (deterministic build path).
        untils = [
            ((sources.get(k) or {}).get("hold") or {}).get("until")
            for k in listed
        ]
        untils = [u for u in untils if u]
        expected_rb = min(untils) if untils else None
        if marker.get("review_by") != expected_rb:
            problems.append(
                f"{e['id']}: source_freshness.review_by is {marker.get('review_by')!r}; "
                f"earliest hold.until of its sources is {expected_rb!r}"
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


_TAXONOMY_KEYS = ("atlas", "owasp_llm", "owasp_asi", "capec", "veris")


def check_taxonomy_versions(stats: dict, derived: dict) -> list[str]:
    """data/stats.json must carry ``taxonomy_versions`` (the five pinned
    taxonomies, additive key) and it must equal the value derived from
    mappings/*.json right now -- a stale stats.json (mapping re-pinned, build
    not re-run) fails here instead of publishing the wrong version."""
    tv = stats.get("taxonomy_versions")
    if not isinstance(tv, dict):
        return ["stats.json: missing `taxonomy_versions` object"]
    problems: list[str] = []
    if set(tv) != set(_TAXONOMY_KEYS):
        problems.append(f"stats.json: taxonomy_versions keys {sorted(tv)} != {sorted(_TAXONOMY_KEYS)}")
    for k in _TAXONOMY_KEYS:
        v = tv.get(k)
        if v is not None and not isinstance(v, str):
            problems.append(f"stats.json: taxonomy_versions.{k} must be a string or null, got {v!r}")
    if tv != derived:
        problems.append(f"stats.json: taxonomy_versions {tv} != derived from mappings/ {derived}")
    return problems


# ---------------------------------------------------------------------------
# N9 precision-audit gate (v2.13.0 item 5). What it enforces, in EVERY status
# (pending, partial and measured alike -- the measured state is the one that
# publishes a figure, so it is the one the pins matter most for; BOUNCE #1):
#   (a) the audit directory is the pinned one, and no other directory of
#       ANY name exists under docs/audits/precision/ (a newer self-consistent
#       directory cannot quietly take over; b17 advisory 1: a variant such as
#       "2026-10-11b" escaped the old date-shaped glob, so the rule is now
#       "exactly one subdirectory", which scripts/wilson_ci.py's default
#       directory choice also enforces);
#   (b) the sample is untampered: sample.json's entries hash to its own
#       declared entries_sha256 AND to the value pinned in code, and the
#       review sheet lists exactly the sampled ids in order;
#   (c) the sampling frame is untampered: the canonical hash of frame.json
#       (strata, populations, allocation, seed, data hash) equals the value
#       pinned in code -- the populations are the estimator's weights, so an
#       edited population moves the published figure;
#   (d) results.json equals a fresh computation from the sheet's HUMAN
#       columns (scripts/wilson_ci.py), and the DATASHEET "Measured
#       precision" block equals the rendering of those results, so a figure
#       cannot be hand-typed into either; and (b17 advisory 3) no precision
#       figure sits in the DATASHEET OUTSIDE that block
#       (wilson_ci.stray_precision_figures; its docstring lists the known
#       limits it does not detect);
#   (e) while the measurement is not complete (pending/partial), the pending
#       state must be AUTHORISED by a D28-form marker
#       (pending_authorization.json: decision id, decided_by "user", and an
#       entries_sha256 matching the sample).
# The user's decision id is a PLACEHOLDER until the user rules. In that state
# ("unratified") the gate passes with a warning only through dataset version
# 2.13.x (PRECISION_UNRATIFIED_GRACE_THROUGH); from 2.14.0 it fails until the
# user either ratifies the pending state or the human labels land. No ruling
# is recorded or implied by this code.
# Update 2026-10-11: the user ratified the pending state by ruling D76
# (decided 2026-10-11, recorded on the board), accepting that the "100 auto"
# frame was drawn from tier=feed. REQUIRED_PRECISION_PENDING_DECISION is set
# to "D76" below and the marker carries the same id, so the UNRATIFIED grace
# path no longer applies: a placeholder or any other id now fails at every
# version. The measurement itself stays pending until the sheet is labelled.
# Re-derive the pinned hashes (canonical JSON, sort_keys, no whitespace):
#   python -c "import sys,json; sys.path.insert(0,'scripts'); import precision_sample as p; d='docs/audits/precision/2026-10-11/'; print(p.canonical_sha256(json.load(open(d+'sample.json',encoding='utf-8'))['entries'])); print(p.canonical_sha256(json.load(open(d+'frame.json',encoding='utf-8'))))"
# Changing any of these constants is itself a change that needs the user's
# dated board decision -- it is not something a routine PR should touch.
PRECISION_PENDING_PLACEHOLDER = "<USER-DECISION-ID>"
REQUIRED_PRECISION_PENDING_DECISION: str | None = "D76"  # user ruling D76, decided 2026-10-11 (board)
PRECISION_AUDIT_DIR_REL = "docs/audits/precision/2026-10-11"
REQUIRED_PRECISION_SAMPLE_ENTRIES_SHA256 = (
    "4fb93c0581a40de290799d9a5b36fe894ee6ccad67089c970813c9f9190cc189"
)
REQUIRED_PRECISION_FRAME_SHA256 = (
    "190855d7fbfb654293a16a0655d51c92849dc503b9844a164a572ff9805bf6e4"
)
PRECISION_UNRATIFIED_GRACE_THROUGH = (2, 13)
PRECISION_AUTH_FILE = "pending_authorization.json"


def _version_tuple(version: str | None) -> tuple[int, int]:
    m = re.match(r"^(\d+)\.(\d+)", version or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def _is_iso_date(value: object) -> bool:
    """True for a real calendar date written exactly YYYY-MM-DD."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_precision_audit(version: str | None, root: Path = ROOT,
                          required_decision: str | None = None,
                          required_sha: str | None = None,
                          required_frame_sha: str | None = None,
                          audit_rel: str | None = None) -> tuple[list[str], str]:
    """-> (problems, one-line status). Never raises on bad inputs; every
    failure is a problem string. `required_*` / `audit_rel` default to the
    pinned module constants (overridable for tests only)."""
    import wilson_ci as w
    from precision_sample import canonical_sha256

    required_decision = REQUIRED_PRECISION_PENDING_DECISION if required_decision is None else required_decision
    required_sha = REQUIRED_PRECISION_SAMPLE_ENTRIES_SHA256 if required_sha is None else required_sha
    required_frame_sha = REQUIRED_PRECISION_FRAME_SHA256 if required_frame_sha is None else required_frame_sha
    rel = PRECISION_AUDIT_DIR_REL if audit_rel is None else audit_rel
    problems: list[str] = []
    audit_dir = root / rel
    if not audit_dir.is_dir():
        return [f"precision: pinned audit directory {rel}/ is missing"], "precision: MISSING"
    others = sorted(
        p.relative_to(root).as_posix()
        for p in (root / "docs" / "audits" / "precision").iterdir()
        if p.is_dir() and p.resolve() != audit_dir.resolve()
    )
    if others:
        problems.append(f"precision: audit director(ies) {others} exist besides the pinned {rel}/ -- only the "
                        "pinned directory may exist; a new audit needs its own user decision and new pins in "
                        "scripts/validate.py")
    try:
        sample = json.loads((audit_dir / w.SAMPLE_FILE).read_text(encoding="utf-8"))
        frame = json.loads((audit_dir / w.FRAME_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return problems + [f"precision: {rel} sample/frame unreadable: {exc}"], "precision: BROKEN"
    fresh_sha = canonical_sha256(sample.get("entries", []))
    if sample.get("entries_sha256") != fresh_sha:
        problems.append(f"precision: {rel}/{w.SAMPLE_FILE} entries do not hash to its declared "
                        f"entries_sha256 ({sample.get('entries_sha256')!r} vs {fresh_sha!r}) -- sample edited")
    if fresh_sha != required_sha:
        problems.append(f"precision: the sample's entries hash ({fresh_sha!r}) does not match the value pinned "
                        f"in code ({required_sha!r}) -- a re-drawn or edited sample needs a new user decision")
    frame_sha = canonical_sha256(frame)
    if frame_sha != required_frame_sha:
        problems.append(f"precision: {rel}/{w.FRAME_FILE} hashes to {frame_sha!r}, not the value pinned in code "
                        f"({required_frame_sha!r}) -- the sampling frame (stratum populations = estimator "
                        "weights) was edited")
    try:
        ids = w.sheet_ids(audit_dir / w.SHEET_FILE)
    except OSError as exc:
        return problems + [f"precision: {rel}/{w.SHEET_FILE} unreadable: {exc}"], "precision: BROKEN"
    if ids != [e.get("id") for e in sample.get("entries", [])]:
        problems.append(f"precision: {rel}/{w.SHEET_FILE} ids differ from the sample's ids (rows swapped, "
                        "added or dropped)")
    try:
        res = w.compute(audit_dir, root)
    except (w.LabelError, OSError, ValueError, KeyError) as exc:
        return problems + [f"precision: cannot compute results: {exc}"], "precision: BROKEN"
    rpath = audit_dir / w.RESULTS_FILE
    if not rpath.exists() or rpath.read_text(encoding="utf-8").replace("\r\n", "\n") != w.dump(res):
        problems.append(f"precision: {rel}/{w.RESULTS_FILE} differs from a fresh computation from the "
                        "sheet's human labels -- run `python scripts/wilson_ci.py --render-datasheet`")
    ds_path = root / "docs" / "DATASHEET.md"
    ds = ds_path.read_text(encoding="utf-8").replace("\r\n", "\n") if ds_path.exists() else ""
    if w.datasheet_block(ds) != w.render_block(res):
        problems.append("precision: docs/DATASHEET.md 'Measured precision' block is missing or differs from "
                        "the rendering of results.json (hand-edited or stale) -- run "
                        "`python scripts/wilson_ci.py --render-datasheet`")
    problems.extend(f"precision: {s}" for s in w.stray_precision_figures(ds))
    status = res["status"]
    if status == "measured":
        line = f"precision: measured ({res['human_labelled']} human-labelled rows, {rel})"
        return problems, (line + f" -- FAILING ({len(problems)} problem(s))" if problems else line)

    # Pending/partial: the D28-form authorisation is required (on top of the
    # unconditional pins above).
    apath = audit_dir / PRECISION_AUTH_FILE
    try:
        auth = json.loads(apath.read_text(encoding="utf-8")).get("authorization")
    except (OSError, ValueError):
        auth = None
    if not isinstance(auth, dict):
        problems.append(f"precision: status {status} but {rel}/{PRECISION_AUTH_FILE} carries no "
                        "`authorization` marker -- a pending measurement must be authorised")
        return problems, f"precision: {status}, UNAUTHORISED"
    if auth.get("decided_by") != "user":
        problems.append(f"precision: {PRECISION_AUTH_FILE} decided_by is {auth.get('decided_by')!r}, not 'user'")
    if auth.get("entries_sha256") != fresh_sha:
        problems.append(f"precision: {PRECISION_AUTH_FILE} entries_sha256 ({auth.get('entries_sha256')!r}) "
                        f"does not match the sample on disk ({fresh_sha!r})")
    decision = auth.get("decision")
    if decision == PRECISION_PENDING_PLACEHOLDER and not required_decision:
        if _version_tuple(version) > PRECISION_UNRATIFIED_GRACE_THROUGH:
            problems.append(
                f"precision: pending state is still UNRATIFIED (decision placeholder) at dataset version "
                f"{version}; the grace ran through {'.'.join(map(str, PRECISION_UNRATIFIED_GRACE_THROUGH))}.x. "
                "The user must rule (fill the decision id in the marker and in "
                "REQUIRED_PRECISION_PENDING_DECISION) or return the labelled sheet.")
        line = (f"precision: {status} -- WARNING: pending state UNRATIFIED (decision id is a placeholder; "
                f"passes only through {'.'.join(map(str, PRECISION_UNRATIFIED_GRACE_THROUGH))}.x)")
        return problems, line
    # A ruling carries a real ISO date (D75/D76 gate advisory 3): the
    # "<YYYY-MM-DD>" placeholder, or any non-date, is not a decision date.
    # Only the UNRATIFIED grace path above may still carry the placeholder.
    if not _is_iso_date(auth.get("decided")):
        problems.append(f"precision: {PRECISION_AUTH_FILE} decided is {auth.get('decided')!r}, "
                        "not an ISO YYYY-MM-DD date")
    if not required_decision or decision != required_decision:
        problems.append(f"precision: {PRECISION_AUTH_FILE} names decision {decision!r} but the decision pinned "
                        f"in code is {required_decision!r}")
        return problems, f"precision: {status}, NOT authorised (marker {decision!r} vs code {required_decision!r})"
    # b4: the marker names the pinned decision, but any other problem (a non-ISO
    # date, a wrong decided_by, a broken pin...) means the pending state is NOT
    # authorised -- the status line must not say it is.
    if problems:
        return problems, (f"precision: {status}, NOT authorised ({len(problems)} problem(s); marker names "
                          f"{decision!r})")
    return problems, f"precision: {status}, authorised by {decision}"

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
    # Per-record shape of the deprecations file (v2.13.0 / D49). The
    # cross-record rules live in check_integrity above.
    dep_schema_path = ROOT / "schema" / "id_deprecations.schema.json"
    if dep_path.exists():
        dep_schema = json.loads(dep_schema_path.read_text(encoding="utf-8"))
        for err in jsonschema.Draft202012Validator(dep_schema).iter_errors(
            json.loads(dep_path.read_text(encoding="utf-8"))
        ):
            path = ".".join(str(p) for p in err.path)
            problems.append(f"id_deprecations.json: {path}: {err.message[:200]}")
    rej_path = ROOT / "ingest" / "cve_rejections.json"
    rejected = disputed = None
    if rej_path.exists():
        snap_states = json.loads(rej_path.read_text(encoding="utf-8"))["states"]
        rejected = {c for c, r in snap_states.items() if r.get("state") == "REJECTED"}
        disputed = {c for c, r in snap_states.items()
                    if r.get("state") == "PUBLISHED" and r.get("disputed")}
    if disputed and not _schema_allows_disputed(schema):
        print(f"disputed: {len(disputed)} disputed CVE(s) in the snapshot are not applied until the schema "
              "carries status_reason code 'cve-disputed' (schema-architect); dispute checks skipped")
        disputed = None
    problems += check_status(data, rejected, disputed)
    from taxonomy_versions import taxonomy_versions as _derive_tv
    problems += check_taxonomy_versions(
        json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8")), _derive_tv()
    )
    # The slim file carries the same envelope; its count must agree too.
    slim_path = ROOT / "data" / "incidents.min.json"
    if slim_path.exists():
        slim = json.loads(slim_path.read_text(encoding="utf-8"))
        problems += [f"incidents.min.json: {p}" for p in check_envelope(slim)]
        if (slim.get("incident_count"), slim.get("retracted_count", 0), slim.get("unverified_count")) != (
                data.get("incident_count"), data.get("retracted_count", 0), data.get("unverified_count")):
            problems.append("incidents.min.json: count envelope differs from incidents.json")

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

    prec_problems, prec_line = check_precision_audit(data.get("version"))
    problems.extend(prec_problems)
    print(prec_line)

    if problems:
        print(f"\n{len(problems)} integrity violation(s):")
        for p in problems[:20]:
            print(f"  - {p}")
    else:
        print("integrity: no duplicate CVE/source keys; all deprecations resolve.")

    sys.exit(1 if (errors or problems) else 0)


if __name__ == "__main__":
    main()
