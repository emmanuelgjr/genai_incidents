"""Smoke + behaviour tests for the genai_incidents pip package."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src/ layout importable without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import genai_incidents as gi


def test_load_incidents_returns_nonempty_list():
    rows = gi.load_incidents()
    assert isinstance(rows, list)
    assert len(rows) > 100


def test_load_schema_round_trips():
    s = gi.load_schema()
    assert s.get("title", "").lower().startswith("genai")
    assert "properties" in s


def test_query_filters_combine():
    crit = list(gi.query(severity="Critical"))
    assert all(e.get("severity") == "Critical" for e in crit)

    crit_2026 = list(gi.query(severity="Critical", year=2026))
    assert all(e.get("year") == 2026 for e in crit_2026)
    assert len(crit_2026) <= len(crit)


def test_query_owasp_membership():
    rows = list(gi.query(owasp_llm="LLM01"))
    assert all("LLM01" in (e.get("owasp_llm") or []) for e in rows)


def test_query_has_cve_flag():
    with_cve = list(gi.query(has_cve=True))
    assert all(e.get("cve_ids") for e in with_cve)
    no_cve = list(gi.query(has_cve=False))
    assert all(not e.get("cve_ids") for e in no_cve)


def test_query_text_match_case_insensitive():
    rows = list(gi.query(text="copilot"))
    assert rows, "expected at least one 'copilot' hit"


def test_by_id_and_by_cve():
    rows = gi.load_incidents()
    sample = rows[0]
    assert gi.by_id(sample["id"]) == sample
    assert gi.by_id("INC-99999999") is None
    for cve in sample.get("cve_ids") or []:
        hits = gi.by_cve(cve)
        assert sample in hits
        break


def test_resolve_id_returns_active_unchanged():
    rows = gi.load_incidents()
    sample = rows[0]
    assert gi.resolve_id(sample["id"]) == sample["id"]


def test_resolve_id_unknown_returns_none():
    assert gi.resolve_id("INC-99999999") is None


def test_load_deprecations_dict_shape():
    d = gi.load_deprecations()
    assert isinstance(d, dict)
    for k, v in list(d.items())[:5]:
        assert k.startswith("INC-")
        assert v.startswith("INC-")


# --- WS4-T15: resolve_id must degrade, not crash, on a list-valued `into` --

def test_resolve_id_list_into_returns_none_not_typeerror(monkeypatch):
    # Verified crash today: `current in deprec` with `current` bound to a
    # list raises TypeError: unhashable type: 'list'. A `split`/`resplit`
    # record (WS4-T15) is list-valued by design, so this must degrade
    # safely rather than blow up every caller's first hop into one.
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": ["INC-2", "INC-3"]})
    monkeypatch.setattr(gi, "by_id", lambda x: None)
    assert gi.resolve_id("INC-1") is None


def test_resolve_id_group_scalar_chain(monkeypatch):
    targets = {"INC-1": "INC-2", "INC-2": "INC-3"}
    live = {"INC-3"}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: targets)
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x in live else None)
    assert gi.resolve_id_group("INC-1") == ["INC-3"]
    assert gi.resolve_id_group("INC-3") == ["INC-3"]
    assert gi.resolve_id_group("INC-99999999") == []


def test_resolve_id_group_multi_successor(monkeypatch):
    deprec = {"INC-1": ["INC-2", "INC-3"]}
    live = {"INC-2", "INC-3"}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: deprec)
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x in live else None)
    assert set(gi.resolve_id_group("INC-1")) == {"INC-2", "INC-3"}


# --- WS4-T22: a one-element `into` list IS a single canonical successor,
# and resolve_id must walk it rather than bailing like it does for a
# two-or-more-element list. Twelve real published IDs, measured by a
# red-reviewer sweep of the v2.10.0 -> 2f7bba1d resolver behaviour, anchor
# this: 4 regressed from a usable answer to None and must resolve again;
# 8 are genuinely ambiguous (8-100 successors) and must keep returning
# None. ---

_WS4T22_TWELVE = {
    # regressed by the WS4-T15 list guard, fixed by WS4-T22 (each of
    # these carries an older `merged` tombstone AND a later `resplit`
    # tombstone with a single-element `into` -- see
    # test_load_deprecations_prefers_latest_date_for_known_duplicates).
    "INC-07771": "INC-14814",
    "INC-08109": "INC-14847",
    "INC-08133": "INC-14850",
    "INC-08146": "INC-14853",
    # genuinely ambiguous multi-successor `split` records (or records
    # that chain into one) -- correct behaviour is None, not a bug.
    "INC-00311": None,
    "INC-00554": None,
    "INC-00754": None,
    "INC-01897": None,
    "INC-00497": None,
    "INC-03128": None,
    "INC-08139": None,
    "INC-08185": None,
}


def test_resolve_id_ws4t22_named_twelve():
    # Input that makes this fail: reverting resolve_id's list-length
    # check to the pre-WS4-T22 uniform `isinstance(current, list): return
    # None` bail. Verified live below in
    # test_resolve_id_ws4t22_proof_the_regression_test_fires.
    for inc_id, expected in _WS4T22_TWELVE.items():
        assert gi.resolve_id(inc_id) == expected, (inc_id, gi.resolve_id(inc_id))


def test_resolve_id_ws4t22_proof_the_regression_test_fires():
    """Working agreement 6: prove the regression test above actually can
    fail, by running it against a frozen copy of the pre-WS4-T22
    resolve_id (the one that shipped in dcec1602 / WS4-T15) instead of
    the current one. All four of the named non-None IDs must flip to
    None under the old algorithm -- if they didn't, the test above would
    not be checking what this docstring claims it checks."""

    def pre_ws4t22_resolve_id(inc_id):
        if gi.by_id(inc_id) is not None:
            return inc_id
        deprec = gi._load_deprecations()
        seen = set()
        current = inc_id
        while current in deprec and current not in seen:
            seen.add(current)
            current = deprec[current]
            if isinstance(current, list):
                return None
            if gi.by_id(current) is not None:
                return current
        return None

    regressed = {
        inc_id: pre_ws4t22_resolve_id(inc_id)
        for inc_id, expected in _WS4T22_TWELVE.items()
        if expected is not None
    }
    assert regressed == {
        "INC-07771": None,
        "INC-08109": None,
        "INC-08133": None,
        "INC-08146": None,
    }, regressed


def _pre_ws4t22_resolve_id(inc_id, deprec, by_id_fn):
    """Frozen, independent copy of resolve_id() as it shipped in WS4-T15
    (dcec1602), before WS4-T22: ANY list-valued hop, including a
    one-element list, returns None. Used only as a comparison oracle
    below, never as production behaviour -- see
    test_resolve_id_ws4t22_proof_the_regression_test_fires for the
    identical logic exercised directly against live gi.by_id."""
    if by_id_fn(inc_id) is not None:
        return inc_id
    seen = set()
    current = inc_id
    while current in deprec and current not in seen:
        seen.add(current)
        current = deprec[current]
        if isinstance(current, list):
            return None
        if by_id_fn(current) is not None:
            return current
    return None


def test_resolve_id_no_collateral_change_across_full_corpus():
    """WS4-T22 / reviewer's "0 changed target" sweep, re-derived here
    independently (working agreement 6) rather than trusted from the
    brief: every tombstoned ID in the shipped data/id_deprecations.json
    must get the SAME answer from the fixed resolve_id as from the
    frozen pre-fix oracle above, except for exactly the 4 IDs WS4-T22 is
    for. A collateral change anywhere else means the fix reached beyond
    its declared scope.

    Input that makes this fail: any change to resolve_id's walk that
    alters an answer for an ID outside the named 4 (e.g. changing how
    scalar hops or cycles are handled, not just the list-length check).
    """
    import json

    raw = json.loads((ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8"))
    # Sweep every distinct tombstoned `from`, not just the ~293 with a
    # non-null `into` (gi._load_deprecations() drops out-of-scope
    # null-into rows -- they trivially return None either way, but the
    # point of this test is corpus-wide coverage, not a narrowed one).
    all_from_ids = sorted({d["from"] for d in raw.get("deprecations", []) if d.get("from")})
    assert len(all_from_ids) >= 1000  # sanity: this is a real, large sweep

    deprec = gi._load_deprecations()
    expected_to_change = {k for k, v in _WS4T22_TWELVE.items() if v is not None}
    changed = {}
    for inc_id in all_from_ids:
        old = _pre_ws4t22_resolve_id(inc_id, deprec, gi.by_id)
        new = gi.resolve_id(inc_id)
        if old != new:
            changed[inc_id] = (old, new)

    assert set(changed) == expected_to_change, changed
    for inc_id in expected_to_change:
        old, new = changed[inc_id]
        assert old is None, (inc_id, "oracle expected to have returned None pre-fix")
        assert new == _WS4T22_TWELVE[inc_id]


def test_resolve_id_no_collateral_change_proof_it_fires():
    """Working agreement 6, second half: prove the no-collateral test
    above can catch an over-broad fix, by simulating one that resolves
    ANY non-empty list to its first element (not just one-element
    lists). This must disagree with the frozen oracle on the 8
    genuinely-ambiguous IDs, which is exactly what the real
    no-collateral test would flag as an unexpected change."""

    def over_broad_resolve_id(inc_id, deprec, by_id_fn):
        if by_id_fn(inc_id) is not None:
            return inc_id
        seen = set()
        current = inc_id
        while current in deprec and current not in seen:
            seen.add(current)
            current = deprec[current]
            if isinstance(current, list):
                if not current:
                    return None
                current = current[0]  # BUG: picks first of N, not just 1
            if by_id_fn(current) is not None:
                return current
        return None

    deprec = gi._load_deprecations()
    ambiguous_eight = [k for k, v in _WS4T22_TWELVE.items() if v is None]
    disagreements = 0
    for inc_id in ambiguous_eight:
        old = _pre_ws4t22_resolve_id(inc_id, deprec, gi.by_id)
        broad = over_broad_resolve_id(inc_id, deprec, gi.by_id)
        if old != broad:
            disagreements += 1
    assert disagreements > 0, (
        "the over-broad simulation should have invented answers for at "
        "least some of the ambiguous IDs -- if it didn't, this proof "
        "doesn't demonstrate the no-collateral test has teeth"
    )


def test_load_deprecations_prefers_latest_date_for_known_duplicates():
    # INC-07771/08109/08133/08146 each carry both an older `merged`
    # tombstone and a later `resplit` tombstone (WS4-T15 -> WS4-T22).
    # The loader must select by explicit `date` comparison, not by
    # "whichever the JSON array happens to list last" -- the trap this
    # guards against already bit merge_and_dedupe.py once (a `seen_from`
    # dict that kept the LAST record under a comment claiming
    # "earliest").
    import json

    raw = json.loads((ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8"))
    dup_froms = ["INC-07771", "INC-08109", "INC-08133", "INC-08146"]
    deprec = gi._load_deprecations()
    for f in dup_froms:
        entries = [d for d in raw["deprecations"] if d["from"] == f]
        assert len(entries) >= 2, f"fixture assumption broken for {f}: only {len(entries)} entries"
        newest = max(entries, key=lambda d: d["date"])
        assert deprec[f] == newest["into"], (f, deprec[f], newest)


# --- WS4-T22: boundary/unit tests for the list-length check itself ---


def test_resolve_id_one_element_list_resolves_to_its_element(monkeypatch):
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": ["INC-2"]})
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x == "INC-2" else None)
    assert gi.resolve_id("INC-1") == "INC-2"


def test_resolve_id_two_element_list_still_returns_none(monkeypatch):
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": ["INC-2", "INC-3"]})
    monkeypatch.setattr(
        gi, "by_id", lambda x: {"id": x} if x in ("INC-2", "INC-3") else None
    )
    assert gi.resolve_id("INC-1") is None


def test_resolve_id_zero_element_list_returns_none_not_indexerror(monkeypatch):
    # Shouldn't occur in real data, but the length check must not assume
    # at least one element.
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": []})
    monkeypatch.setattr(gi, "by_id", lambda x: None)
    assert gi.resolve_id("INC-1") is None


def test_resolve_id_one_element_list_to_dangling_id_returns_none(monkeypatch):
    # INC-1 -> [INC-2], but INC-2 is neither live nor itself in the
    # deprecation map: a dangling reference, not a resolvable chain.
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": ["INC-2"]})
    monkeypatch.setattr(gi, "by_id", lambda x: None)
    assert gi.resolve_id("INC-1") is None


def test_resolve_id_one_element_list_chains_through_further_deprecation(monkeypatch):
    # INC-1 -> [INC-2] (one-element list), INC-2 -> INC-3 (scalar hop,
    # itself deprecated), INC-3 is live. The chain must keep walking
    # past the unwrapped list element.
    deprec = {"INC-1": ["INC-2"], "INC-2": "INC-3"}
    live = {"INC-3"}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: deprec)
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x in live else None)
    assert gi.resolve_id("INC-1") == "INC-3"


def test_resolve_id_cycle_through_one_element_lists_terminates(monkeypatch):
    # INC-1 -> [INC-2], INC-2 -> [INC-1]: neither ever live. Must return
    # None promptly rather than looping forever.
    deprec = {"INC-1": ["INC-2"], "INC-2": ["INC-1"]}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: deprec)
    monkeypatch.setattr(gi, "by_id", lambda x: None)
    assert gi.resolve_id("INC-1") is None
