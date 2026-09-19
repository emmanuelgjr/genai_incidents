"""Tests for the cross-entry integrity invariants in validate.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import merge_and_dedupe as m
import validate as v

ROOT = Path(__file__).resolve().parents[1]


def _data(*incidents):
    # Default a resolvable reference so fixtures pass the evidence gate unless
    # a test is specifically exercising it.
    for e in incidents:
        e.setdefault("references", [{"url": "https://example.com/src"}])
    return {"incidents": list(incidents)}


def test_integrity_clean():
    data = _data(
        {"id": "INC-1", "cve_ids": ["CVE-1"], "source_ids": ["S-1"]},
        {"id": "INC-2", "cve_ids": ["CVE-2"], "source_ids": ["S-2"]},
    )
    assert v.check_integrity(data, []) == []


def test_integrity_duplicate_cve_flagged():
    data = _data(
        {"id": "INC-1", "cve_ids": ["CVE-1"], "source_ids": ["S-1"]},
        {"id": "INC-2", "cve_ids": ["CVE-1"], "source_ids": ["S-2"]},
    )
    problems = v.check_integrity(data, [])
    assert any("CVE-1" in p and "INC-1" in p and "INC-2" in p for p in problems)


def test_integrity_duplicate_source_flagged():
    data = _data(
        {"id": "INC-1", "source_ids": ["S-1"]},
        {"id": "INC-2", "source_ids": ["S-1"]},
    )
    assert any("S-1" in p for p in v.check_integrity(data, []))


def test_integrity_deprecation_resolves_via_chain():
    data = _data({"id": "INC-3", "cve_ids": [], "source_ids": []})
    deps = [
        {"from": "INC-1", "into": "INC-2"},
        {"from": "INC-2", "into": "INC-3"},  # chain INC-1 -> INC-2 -> INC-3 (live)
    ]
    assert v.check_integrity(data, deps) == []


def test_integrity_deprecation_dangling_flagged():
    data = _data({"id": "INC-3"})
    deps = [{"from": "INC-1", "into": "INC-9"}]  # INC-9 not live
    assert any("does not resolve" in p for p in v.check_integrity(data, deps))


def test_integrity_deprecated_id_still_live_flagged():
    data = _data({"id": "INC-1"})
    deps = [{"from": "INC-1", "into": "INC-1"}]
    assert any("still a live entry" in p for p in v.check_integrity(data, deps))


def test_integrity_deprecation_cycle_does_not_hang():
    data = _data({"id": "INC-3"})
    deps = [
        {"from": "INC-1", "into": "INC-2"},
        {"from": "INC-2", "into": "INC-1"},  # cycle, neither resolves to live
    ]
    problems = v.check_integrity(data, deps)
    assert any("does not resolve" in p for p in problems)


def test_integrity_evidence_gate_flags_sourceless():
    data = _data({"id": "INC-1", "references": []})
    assert any("primary source" in p for p in v.check_integrity(data, []))
    ok = _data({"id": "INC-1", "references": [{"url": "https://x.com/a"}]})
    assert not any("primary source" in p for p in v.check_integrity(ok, []))


def test_integrity_reversibility_gate_flags_non_landmark():
    data = _data({"id": "INC-1", "tier": "feed",
                  "reversibility_class": "irreversible"})
    assert any("reversibility_class" in p for p in v.check_integrity(data, []))


# --- WS4-T15: list-valued `into` (split/resplit) and the coverage guard ---

def test_integrity_list_into_resolves_when_every_successor_is_live():
    data = _data({"id": "INC-2"}, {"id": "INC-3"})
    deps = [{"from": "INC-1", "into": ["INC-2", "INC-3"], "reason": "split",
             "date": "2026-01-01"}]
    assert v.check_integrity(data, deps) == []


def test_integrity_list_into_flags_when_one_successor_is_dangling():
    data = _data({"id": "INC-2"})
    deps = [{"from": "INC-1", "into": ["INC-2", "INC-9"], "reason": "split",
             "date": "2026-01-01"}]  # INC-9 not live
    assert any("does not resolve" in p for p in v.check_integrity(data, deps))


def test_integrity_list_into_does_not_crash_check_integrity():
    # Regression for the exact crash the WS4-T10 unmerge design found:
    # `current in into_map` raising TypeError: unhashable type: 'list' the
    # moment a chain hop lands on a list-valued `into`. This must return a
    # problem list, not raise.
    data = _data({"id": "INC-4"})
    deps = [
        {"from": "INC-1", "into": "INC-2", "reason": "merged", "date": "2026-01-01"},
        {"from": "INC-2", "into": ["INC-3", "INC-4"], "reason": "split",
         "date": "2026-01-02"},
        {"from": "INC-3", "into": "INC-4", "reason": "merged", "date": "2026-01-03"},
    ]
    problems = v.check_integrity(data, deps)  # must not raise
    assert problems == []  # INC-1 -> INC-2 -> [INC-3 -> INC-4 (live), INC-4 (live)]


def test_deprecation_coverage_fires_on_a_minority_redirect():
    # Named failing input (agreement 6): a retired id had 92 sources; its
    # recorded target now holds only 2 of them -- the exact shape
    # (INC-08139/INC-08185) that passed a bare non-empty-intersection test
    # in the WS4-T10 unmerge design's own audit.
    data = _data({"id": "INC-A", "source_ids": ["s1", "s2"]})
    retired = [f"s{i}" for i in range(1, 93)]
    deps = [{"from": "INC-OLD", "into": "INC-A", "reason": "merged",
              "date": "2026-01-01", "retired_source_ids": retired}]
    problems = v.check_deprecation_coverage(data, deps)
    assert any("INC-OLD" in p and "2/92" in p for p in problems)


def test_deprecation_coverage_clean_when_target_holds_the_source_ids():
    data = _data({"id": "INC-A", "source_ids": ["s1", "s2"]})
    deps = [{"from": "INC-OLD", "into": "INC-A", "reason": "merged",
              "date": "2026-01-01", "retired_source_ids": ["s1", "s2"]}]
    assert v.check_deprecation_coverage(data, deps) == []


def test_deprecation_coverage_multi_target_unions_successors():
    data = _data(
        {"id": "INC-A", "source_ids": ["s1"]},
        {"id": "INC-B", "source_ids": ["s2"]},
    )
    deps = [{"from": "INC-OLD", "into": ["INC-A", "INC-B"], "reason": "resplit",
              "date": "2026-01-01", "retired_source_ids": ["s1", "s2"]}]
    assert v.check_deprecation_coverage(data, deps) == []


def test_deprecation_coverage_resolves_a_chain_not_the_literal_into():
    # BOUNCE defect 2: the guard must measure against what a redirect
    # CHAIN actually resolves to, not the literal `into` value on the
    # record -- A -> B -> C (live), C holds everything the retired id had.
    # Taking `into` literally reports A -> B (not live) -> held=empty ->
    # 0% coverage on a perfectly healthy redirect.
    data = _data({"id": "INC-C", "source_ids": ["s1", "s2"]})
    deps = [
        {"from": "INC-A", "into": "INC-B", "reason": "merged", "date": "2026-01-01",
         "retired_source_ids": ["s1"]},
        {"from": "INC-B", "into": "INC-C", "reason": "merged", "date": "2026-01-02"},
    ]
    problems = v.check_deprecation_coverage(data, deps)
    assert problems == [], (
        f"a healthy chained redirect must not be flagged as 0% coverage: {problems}"
    )


def test_deprecation_coverage_resolves_a_real_committed_chain():
    # Prove it on a real committed chain, not only a synthetic one
    # (BOUNCE defect 2's explicit ask). `data/id_deprecations.json` has a
    # genuine chain today: INC-08185 -> INC-08139 -> INC-00554 -> [100 live
    # successors] -- INC-00554 was ITSELF retired (WS4-T21/D28: "no
    # survivor keeps the old id" for a continuity-breaking split), so the
    # chain is 4 hops deep, and the resolvable live end is any one of
    # INC-00554's own successors, not INC-00554 itself.
    #
    # [WS4-T21 BOUNCE #1, dated note] The ORIGINAL fixture id here was
    # INC-08146, which chained the SAME way before this bounce's defect-1
    # fix: it turned out D28 approved INC-08146 a single, SPECIFIC
    # successor (INC-14853), not the full 100-way fan-out this multi-hop
    # chain produces -- exactly the bug the fix corrects, by giving
    # INC-08146 its own direct, single-target record. Using INC-08146
    # here after that fix would have locked the wrong resolution in as
    # "expected" (the gate's advisory A2). INC-08185 is a DIFFERENT one of
    # the same 8 inbound redirects, confirmed still genuinely multi-hop
    # post-fix (D28 approved it the full fan-out, matching what this
    # chain already produces -- see docs/audits/WS4-T19-authorized-splits-2026-09-18.json).
    # Read-only: this test never writes to data/.
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    real_deps = json.loads(
        (ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8")
    )["deprecations"]
    live_ids = {e["id"] for e in data["incidents"] if e.get("id")}
    latest = v._latest_by_from(real_deps)
    into_map = {f: r.get("into") for f, r in latest.items()}
    assert "INC-08185" in latest, "fixture assumption (INC-08185 is a recorded redirect) is stale -- update it"
    resolved = v._resolve_live_targets(latest["INC-08185"].get("into"), into_map, live_ids)
    assert len(resolved) > 1, "fixture assumption (INC-08185 chains to MULTIPLE live ids) is stale -- update it"
    id_to_sources = {e["id"]: e.get("source_ids") or [] for e in data["incidents"]}
    a_real_source_a_chain_end_holds = next(
        s for t in sorted(resolved) for s in id_to_sources.get(t, []) if s
    )
    deps = [dict(d) for d in real_deps]
    found = False
    for d in deps:
        if d.get("from") == "INC-08185":
            d["retired_source_ids"] = [a_real_source_a_chain_end_holds]
            found = True
    assert found, "fixture assumption (INC-08185 chains to INC-08139) is stale -- update it"
    problems = v.check_deprecation_coverage(data, deps)
    assert problems == [], (
        f"the real INC-08185 -> INC-08139 -> INC-00554 -> [...] chain must resolve: {problems}"
    )


def test_deprecation_coverage_legacy_record_is_unverifiable_not_passing():
    # A record with no persisted retired_source_ids (every `merged` record
    # written before WS4-T15) must be visibly skipped, not silently counted
    # as a pass -- checks that cannot fail are the failure mode this guards
    # against (working agreement 6).
    data = _data({"id": "INC-A"})
    deps = [{"from": "INC-OLD", "into": "INC-A", "reason": "merged",
              "date": "2026-01-01"}]
    assert v.check_deprecation_coverage(data, deps) == []  # not a failure...
    # ...but check_integrity's own printed accounting (captured via capsys
    # in a real CI log) is what makes "0 checked" visible; see
    # scripts/validate.py's check_deprecation_coverage docstring.


def test_real_resplit_redirects_match_d28_approved_targets():
    """WS4-T21 BOUNCE #2 (the user's third requirement, quoted in the
    ruling): "A committed test must assert this, so redirect-target
    correctness survives the next refactor rather than resting on this
    review." Reads the REAL, marker-verified D28 authorized list and the
    REAL committed corpus + deprecations -- NOT a synthetic fixture (the
    mechanism tests in tests/test_merge_and_dedupe.py cover the mechanism
    on a 2-row fixture; this covers the DATA, which the gate proved a
    passing fixture test does not: it repointed the real INC-08133
    corrective record back to its pre-fix, still-live-but-wrong target
    and got validate.py exit 0 and the full suite green).

    For every `resplit_redirect` entry, asserts what its CURRENT recorded
    `into` chain-resolves to EQUALS what its D28-approved `new_targets`
    resolves to -- both sides via validate.py's own
    `_resolve_live_targets`, exactly the function
    scripts/merge_and_dedupe.py's step 8a uses (expanding any of
    `new_targets`' own elements that are themselves a retired id through
    ITS chain too, same as that step). Asserts the checked count is
    exactly 8, not merely that no mismatch was found -- a loop over an
    empty or mis-filtered list would otherwise report success vacuously.
    Names the four chained-split cases explicitly, since that is the
    regression shape: they regress precisely because they chain into a
    `keep_id` survivor that only holds PART of what it used to."""
    auth_path = ROOT / "docs" / "audits" / "WS4-T19-authorized-splits-2026-09-18.json"
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    assert m._verify_split_authorization_marker(auth, auth_path), (
        "the committed authorized list's D28 marker must verify -- if this "
        "fails, nothing below is a claim about an authorized transition"
    )

    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    deps = json.loads(
        (ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8")
    )["deprecations"]
    live_ids = {e["id"] for e in data["incidents"] if e.get("id")}
    latest = v._latest_by_from(deps)
    into_map = {f: r.get("into") for f, r in latest.items()}

    def resolve(node):
        return v._resolve_live_targets(node, into_map, live_ids)

    resplit_entries = [e for e in auth["entries"] if e.get("decision") == "resplit_redirect"]
    assert len(resplit_entries) == 8, (
        f"expected exactly 8 resplit_redirect entries in the authorized "
        f"list, found {len(resplit_entries)} -- fixture/list assumption is stale"
    )

    checked = 0
    mismatches = []
    for entry in resplit_entries:
        frm = entry["from"]
        approved = entry.get("new_targets") or []
        assert frm in latest, f"{frm} has no recorded deprecation -- corpus assumption is stale"
        current_resolved = resolve(latest[frm].get("into"))
        approved_resolved = resolve(approved)
        checked += 1
        if current_resolved != approved_resolved:
            mismatches.append((frm, sorted(current_resolved), sorted(approved_resolved)))

    # Not vacuous: the loop must actually have visited all 8, not an
    # accidentally-empty or mis-filtered subset.
    assert checked == 8, f"must check all 8 real inbound redirects, checked {checked}"
    assert mismatches == [], f"redirect(s) not matching D28-approved targets: {mismatches}"

    # Named on the four chained-split (BOUNCE #1 defect-1) cases
    # specifically: each must resolve to EXACTLY its one approved id.
    for frm, expected_single in [
        ("INC-07771", "INC-14814"),
        ("INC-08109", "INC-14847"),
        ("INC-08133", "INC-14850"),
        ("INC-08146", "INC-14853"),
    ]:
        assert resolve(latest[frm].get("into")) == {expected_single}, (
            f"{frm} must resolve to exactly {{'{expected_single}'}}"
        )


def test_integrity_reversibility_gate_allows_landmark():
    data = _data({"id": "INC-1", "tier": "landmark",
                  "reversibility_class": "read-only"})
    assert not any("reversibility_class" in p for p in v.check_integrity(data, []))
    # Unlabeled entries are fine on any tier — absence means unassessed.
    unlabeled = _data({"id": "INC-2", "tier": "feed"})
    assert not any("reversibility_class" in p for p in v.check_integrity(unlabeled, []))


def test_integrity_discovery_method_gate_flags_non_landmark():
    data = _data({"id": "INC-1", "tier": "feed",
                  "discovery_method": "security-researcher"})
    assert any("discovery_method" in p for p in v.check_integrity(data, []))


def test_integrity_discovery_method_gate_allows_landmark():
    data = _data({"id": "INC-1", "tier": "landmark",
                  "discovery_method": "actor-disclosure"})
    assert not any("discovery_method" in p for p in v.check_integrity(data, []))


def test_integrity_scope_gate_flags_out_of_scope_malware():
    data = _data({"id": "INC-1", "tags": ["malicious-package"],
                  "affected": "npm/chai-mocks",
                  "references": [{"url": "https://x.com/a"}]})
    assert any("out-of-scope" in p for p in v.check_integrity(data, []))
    ok = _data({"id": "INC-1", "tags": ["malicious-package"],
                "affected": "npm/@langchain/core",
                "references": [{"url": "https://x.com/a"}]})
    assert not any("out-of-scope" in p for p in v.check_integrity(ok, []))


# --- D8: source-freshness completeness gate ----------------------------
# check_source_freshness() (schema-architect) checks markers PRESENT are
# consistent with the registry; check_freshness_completeness() (this task)
# checks markers that SHOULD be present ARE — the gate that makes the
# marking non-optional once it lands. See the D8 application spec §6a.

_STALE_REGISTRY = {
    "sources": {
        "airi_navigator": {
            "status": "stale",
            "last_success": "2026-05-31",
            "row_marker": {"kind": "tag", "value": "airi-navigator"},
        },
        "cisa_kev": {
            "status": "stale",
            "last_success": "2026-05-01",
            "row_marker": None,
            "row_marker_note": "enrichment-only, deliberately non-propagating",
        },
        "oecd_aim": {
            "status": "ok",
            "last_success": "2026-07-12",
            "row_marker": {"kind": "tag", "value": "oecd-aim"},
        },
    }
}


def test_freshness_completeness_flags_unmarked_tagged_row():
    data = _data({"id": "INC-1", "tags": ["airi-navigator"]})
    problems = v.check_freshness_completeness(data, _STALE_REGISTRY)
    assert any("INC-1" in p and "airi_navigator" in p for p in problems)


def test_freshness_completeness_passes_when_marker_present():
    data = _data({
        "id": "INC-1", "tags": ["airi-navigator"],
        "source_freshness": {"status": "stale", "as_of": "2026-05-31",
                              "sources": ["airi_navigator"]},
    })
    assert v.check_freshness_completeness(data, _STALE_REGISTRY) == []


def test_freshness_completeness_ignores_ok_status_source():
    # oecd_aim is `ok` in the registry — a row carrying its tag needs no
    # marker even though the source has a non-null row_marker.
    data = _data({"id": "INC-1", "tags": ["oecd-aim"]})
    assert v.check_freshness_completeness(data, _STALE_REGISTRY) == []


def test_freshness_completeness_ignores_null_row_marker_source():
    # cisa_kev is stale but row_marker is null (enrichment-only) — no row is
    # ever required to carry a marker naming it, because nothing selects
    # "the rows it touched" the way a tag does.
    data = _data({"id": "INC-1", "tags": ["some-other-tag"]})
    assert v.check_freshness_completeness(data, _STALE_REGISTRY) == []


def test_freshness_completeness_partial_marker_still_flagged():
    # Entry carries BOTH a stale-tag and an ok-tag but its marker (correctly)
    # lists only the stale source — completeness must still pass here, since
    # oecd_aim's ok status doesn't require listing.
    data = _data({
        "id": "INC-1", "tags": ["airi-navigator", "oecd-aim"],
        "source_freshness": {"status": "stale", "as_of": "2026-05-31",
                              "sources": ["airi_navigator"]},
    })
    assert v.check_freshness_completeness(data, _STALE_REGISTRY) == []


# --- check_registry_provenance(): the enumerated-context allowlist ---------
# The registry is CURATED, not derived (PROGRESS.md precedent 1), so the one
# machine-checkable thing about it is that it matches the copy its
# `observed_from` names. Before the allowlist, ANY value that failed to name
# the in-repo copy returned zero problems: a typo, an empty string or a
# sentence deleted the comparison, and "checked and matched" was
# indistinguishable from "not checked" in the build output. These tests pin
# the three outcomes and, above all, that an unrecognised claim FAILS.

def _state(tmp_path, **overrides):
    """A minimal source-health counter file, plus the registry that honestly
    matches it. Returns (path, registry)."""
    state = {
        "airi_navigator": {"status": "stale", "last_success": "2026-05-31"},
        "oecd_aim": {"status": "ok", "last_success": "2026-07-12"},
    }
    path = tmp_path / "source_health.json"
    path.write_text(json.dumps(state), encoding="utf-8")
    registry = {
        "observed_at": "2026-07-12",
        "observed_from": v.PROVENANCE_IN_REPO,
        "sources": {
            k: dict(vals, label=k, row_marker=None,
                    row_marker_note="not exercised here")
            for k, vals in state.items()
        },
    }
    registry.update(overrides)
    return path, registry


def test_provenance_verified_when_registry_matches_named_copy(tmp_path):
    path, registry = _state(tmp_path)
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_VERIFIED
    assert res.problems == []
    assert "VERIFIED" in res.summary
    # The bound is stated, not implied: passing is not a currency claim.
    assert "NOT a claim the registry is current" in res.summary


@pytest.mark.parametrize("claimed", [
    "refresh-state:ingest/_state/source_healh.json",  # one-character typo
    "main:ingest/_state/source_health.jsonn",
    "refresh-state",
    "",
    "trust me",
])
def test_provenance_unrecognised_observed_from_fails(tmp_path, claimed):
    # THE regression this suite exists for: every one of these used to return
    # [] — a silent pass reachable by a one-line edit to a hand-authored file.
    path, registry = _state(tmp_path, observed_from=claimed)
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_FAILED
    assert len(res.problems) == 1
    assert "not one of the enumerated provenance contexts" in res.problems[0]
    assert repr(claimed) in res.problems[0]


def test_provenance_missing_observed_from_fails(tmp_path):
    # Absent, not merely wrong — the schema requires the key, but the checker
    # must not treat "no claim at all" as an excuse to skip either.
    path, registry = _state(tmp_path)
    del registry["observed_from"]
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_FAILED


def test_provenance_authoritative_copy_is_not_comparable_never_verified(tmp_path):
    # The one legitimate skip, and it is a NAMED context with a reason — not
    # a value inferred from failing to match something else.
    path, registry = _state(tmp_path, observed_from=v.PROVENANCE_AUTHORITATIVE)
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_NOT_COMPARABLE
    assert res.problems == []
    assert "NOT COMPARABLE" in res.summary
    assert "VERIFIED" not in res.summary


def test_provenance_verified_and_not_comparable_are_distinguishable(tmp_path):
    # Both are clean (empty problems), so the build output MUST NOT be the
    # only place they differ by accident: the outcome token and the summary
    # each distinguish them.
    path, registry = _state(tmp_path)
    verified = v.check_registry_provenance(registry, path)
    offline = v.check_registry_provenance(
        dict(registry, observed_from=v.PROVENANCE_AUTHORITATIVE), path)
    assert verified.problems == offline.problems == []
    assert verified.outcome != offline.outcome
    assert verified.summary != offline.summary


def test_provenance_compare_mode_fails_when_named_copy_unreadable(tmp_path):
    # "Unreadable here" is a FAILURE for a compare-mode claim, not a licence
    # to skip; an offline context has to be claimed, not inferred.
    path, registry = _state(tmp_path)
    res = v.check_registry_provenance(registry, tmp_path / "gone.json")
    assert res.outcome == v.PROV_FAILED
    assert "does not exist" in res.problems[0]


def test_provenance_compare_mode_flags_forged_status(tmp_path):
    path, registry = _state(tmp_path)
    registry["sources"]["airi_navigator"]["status"] = "ok"
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_FAILED
    assert any("airi_navigator.status is 'ok'" in p for p in res.problems)


def test_provenance_compare_mode_flags_backdated_last_success(tmp_path):
    path, registry = _state(tmp_path)
    registry["sources"]["oecd_aim"]["last_success"] = "2026-07-26"
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_FAILED
    assert any("oecd_aim.last_success" in p for p in res.problems)


def test_provenance_compare_mode_flags_unregistered_source(tmp_path):
    # A fifth source appearing in the workflow without being registered.
    path, registry = _state(tmp_path)
    state = json.loads(path.read_text(encoding="utf-8"))
    state["new_feed"] = {"status": "ok", "last_success": "2026-07-12"}
    path.write_text(json.dumps(state), encoding="utf-8")
    res = v.check_registry_provenance(registry, path)
    assert res.outcome == v.PROV_FAILED
    assert any("source keys" in p and "new_feed" in p for p in res.problems)


def test_provenance_contexts_match_the_schema_enum():
    # The allowlist is enforced in two places; this is what stops them
    # drifting. Widening one without the other is the failure mode.
    schema = json.loads(
        (ROOT / "schema" / "source_freshness.schema.json").read_text(encoding="utf-8")
    )
    enum = schema["properties"]["observed_from"]["enum"]
    assert sorted(enum) == sorted(v.PROVENANCE_CONTEXTS)


def test_provenance_every_context_declares_what_it_means_and_does():
    # An enumerated escape hatch is only better than a free-text one if each
    # entry carries its reason. Empty prose here would re-create the defect.
    for claim, ctx in v.PROVENANCE_CONTEXTS.items():
        assert ctx["mode"] in ("compare", "not-comparable"), claim
        assert ctx["means"].strip() and ctx["checker"].strip(), claim


def test_provenance_shipped_registry_is_verified_against_the_copy_it_names():
    # The registry as it actually ships: not merely well-formed, but verified.
    registry = json.loads(
        (ROOT / "data" / "source_freshness.json").read_text(encoding="utf-8")
    )
    res = v.check_registry_provenance(registry, ROOT / v.IN_REPO_STATE_REL)
    assert res.outcome == v.PROV_VERIFIED, res.problems


def test_provenance_printed_summaries_are_ascii(tmp_path):
    # validate.py runs in the build path, and `make build` output lands on
    # consoles that are not always UTF-8. Every summary must survive them.
    path, registry = _state(tmp_path)
    for claimed in [v.PROVENANCE_IN_REPO, v.PROVENANCE_AUTHORITATIVE, "nonsense"]:
        res = v.check_registry_provenance(dict(registry, observed_from=claimed), path)
        res.summary.encode("ascii")
        for p in res.problems:
            p.encode("ascii")
