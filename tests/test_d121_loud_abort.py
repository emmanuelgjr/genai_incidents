"""D121 (user ruling 2026-10-13): fail-closed stays, as a LOUD abort. A gate
refusal must say the whole refresh did not ship, and why."""

from __future__ import annotations

import pytest

import merge_and_dedupe as m

PREV = [
    {"id": "INC-1", "title": "A", "source_ids": ["AIID-1"]},
    {"id": "INC-2", "title": "B", "source_ids": ["AIID-2"]},
]


def test_aiid_side_refusal_says_the_whole_refresh_did_not_ship():
    new = [PREV[0] | {"source_ids": ["AIID-1", "AIID-2"]}]
    dep = [{"from": "INC-2", "into": "INC-1", "reason": "merged", "retired_source_ids": ["AIID-2"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(
            PREV, new, dep, approval_path=m.Path("none.json"), pair_inputs_changed=False,
            aiid_class=True, aiid_titles={})
    msg = str(ei.value)
    assert "THE WHOLE REFRESH DID NOT SHIP" in msg
    for src in ("AIAAIC", "CISA KEV", "CVE rejection sweep"):
        assert src in msg
    assert "merge INC-2 -> INC-1" in msg  # the cause is listed with it


def test_oecd_lift_refusal_says_the_whole_refresh_did_not_ship():
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    assert "THE WHOLE REFRESH DID NOT SHIP" in str(ei.value) and "AIAAIC" in str(ei.value)


def test_the_check_fires_if_the_sentence_is_dropped(monkeypatch):
    monkeypatch.setattr(m, "REFRESH_DID_NOT_SHIP", "")
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    assert "THE WHOLE REFRESH DID NOT SHIP" not in str(ei.value)
