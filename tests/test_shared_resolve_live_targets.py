"""WS4-T21 BOUNCE #3: `merge_and_dedupe.resolve_live_targets` and
`validate.py`'s `_resolve_live_targets` must never disagree.

Today they are literally the same function object -- validate.py imports
it rather than keeping its own copy (see the import block near the top of
scripts/validate.py, and `resolve_live_targets`'s own docstring in
scripts/merge_and_dedupe.py for why the canonical copy lives there:
import direction is fixed, not a style choice, since validate.py already
imports FROM merge_and_dedupe.py and the reverse would be circular).

This test does NOT rely on that identity holding forever -- it calls both
module attributes independently, on the same real-shaped multi-hop,
list-fan-out `into_map`, and asserts their OUTPUTS agree. If a future
change ever reintroduces two separate implementations (a de-share), this
is the test that catches the moment they drift, rather than the drift
being discovered the way BOUNCE #2 discovered the last one: a committed
test asserting a property of real data, with nothing checking the two
implementations of the property itself stayed identical.
"""
from __future__ import annotations

import merge_and_dedupe as m
import validate as v


def test_same_function_object_today():
    # Not the load-bearing assertion (see module docstring) -- but if this
    # ever becomes false without the equivalence test below being updated
    # to match, that is itself worth knowing immediately.
    assert v._resolve_live_targets is m.resolve_live_targets


def _build_chain():
    """A real-shaped chain: a scalar hop, a list-fan-out hop where one
    branch is already live and the other chains one more hop, a dangling
    reference (into_map entry pointing nowhere and not live), and a cycle
    (neither node ever live) -- the same shapes `validate.py`'s own
    integrity/coverage checks and `merge_and_dedupe.py`'s step 8a both
    have to handle correctly and identically."""
    live_ids = {"LIVE-1", "LIVE-2"}
    into_map = {
        "SCALAR-A": "SCALAR-B",
        "SCALAR-B": "LIVE-1",
        "FANOUT": ["LIVE-2", "FAN-TAIL"],
        "FAN-TAIL": "LIVE-1",
        "DANGLING": "NOWHERE",
        "CYCLE-1": "CYCLE-2",
        "CYCLE-2": "CYCLE-1",
    }
    return into_map, live_ids


def test_resolvers_agree_on_a_scalar_chain():
    into_map, live_ids = _build_chain()
    a = m.resolve_live_targets("SCALAR-A", into_map, live_ids)
    b = v._resolve_live_targets("SCALAR-A", into_map, live_ids)
    assert a == b == {"LIVE-1"}


def test_resolvers_agree_on_a_list_fanout_with_one_further_hop():
    into_map, live_ids = _build_chain()
    a = m.resolve_live_targets("FANOUT", into_map, live_ids)
    b = v._resolve_live_targets("FANOUT", into_map, live_ids)
    assert a == b == {"LIVE-1", "LIVE-2"}


def test_resolvers_agree_on_a_dangling_reference():
    into_map, live_ids = _build_chain()
    a = m.resolve_live_targets("DANGLING", into_map, live_ids)
    b = v._resolve_live_targets("DANGLING", into_map, live_ids)
    assert a == b == set()


def test_resolvers_agree_on_a_cycle():
    into_map, live_ids = _build_chain()
    a = m.resolve_live_targets("CYCLE-1", into_map, live_ids)
    b = v._resolve_live_targets("CYCLE-1", into_map, live_ids)
    assert a == b == set()


def test_resolvers_agree_a_live_id_resolves_to_itself():
    into_map, live_ids = _build_chain()
    a = m.resolve_live_targets("LIVE-1", into_map, live_ids)
    b = v._resolve_live_targets("LIVE-1", into_map, live_ids)
    assert a == b == {"LIVE-1"}
