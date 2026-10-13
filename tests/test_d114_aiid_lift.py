"""D114/D115/D116 (user rulings 2026-10-13): the AIID side of the stage-1 freeze
is lifted; OECD stays held; suppression (A3) is a BINDING PRECONDITION for any
later OECD lift; the D42 per-item rulings are recorded as inert data.

Each check names the input that makes it fail and a test shows it fail
(agreement 6).
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import merge_and_dedupe as m

ROOT = Path(__file__).resolve().parents[1]
D115 = ROOT / "docs" / "audits" / "D115-d42-per-item-rulings-2026-10-13.json"


def _row(iid, title, sids, **kw):
    return {"id": iid, "title": title, "source_ids": list(sids), **kw}


PREV = [
    _row("INC-1", "Old AIID title", ["AIID-1"]),
    _row("INC-2", "Other AIID", ["AIID-2"]),
    _row("INC-3", "OECD row", ["OECD-AIM-2026-01-01-aaaa"]),
]
NOFILE = Path("does-not-exist.json")


def _check(deduped, fresh=(), aiid_class=True, titles=None, **kw):
    m._check_refresh_merge_authorization(
        copy.deepcopy(PREV), deduped, list(fresh), approval_path=NOFILE,
        pair_inputs_changed=False, aiid_class=aiid_class, aiid_titles=titles or {}, **kw,
    )


# ---- the standing AIID class: what it waives ------------------------------


def test_class_passes_a_new_aiid_only_row_and_without_it_the_same_build_aborts():
    new = PREV + [_row("INC-9", "New AIID", ["AIID-9"])]
    _check(new)  # class on: passes
    assert m._LAST_AIID_CLASS_USE["add"] == 1
    with pytest.raises(m.RefreshMergeApprovalError, match="add OECD/AIID"):
        _check(new, aiid_class=False)  # control: the pre-D114 gate


def test_class_does_not_waive_a_new_oecd_row():
    new = PREV + [_row("INC-9", "New OECD", ["OECD-AIM-2026-09-09-zzzz"])]
    with pytest.raises(m.RefreshMergeApprovalError, match="OECD-AIM-2026-09-09-zzzz"):
        _check(new)


def test_class_does_not_waive_a_new_row_that_mixes_aiid_and_oecd_ids():
    new = PREV + [_row("INC-9", "Mixed", ["AIID-9", "OECD-AIM-2026-09-09-zzzz"])]
    with pytest.raises(m.RefreshMergeApprovalError, match="OECD-AIM-2026-09-09-zzzz"):
        _check(new)


def test_class_does_not_waive_an_aiid_id_absorbed_into_a_published_row():
    new = [PREV[0] | {"source_ids": ["AIID-1", "AIID-9"]}, *PREV[1:]]
    with pytest.raises(m.RefreshMergeApprovalError, match="absorbed into published row"):
        _check(new)


def test_class_does_not_waive_a_merge_touching_an_aiid_id():
    new = [PREV[0] | {"source_ids": ["AIID-1", "AIID-2"]}, PREV[2]]
    dep = [{"from": "INC-2", "into": "INC-1", "reason": "merged", "retired_source_ids": ["AIID-2"]}]
    with pytest.raises(m.RefreshMergeApprovalError, match=r"merge INC-2 -> INC-1"):
        _check(new, dep)


def test_class_does_not_waive_a_retitle_that_absorbs_ids():
    new = [PREV[0] | {"title": "AIID-1 and 9 title", "source_ids": ["AIID-1", "AIID-9"]}, *PREV[1:]]
    with pytest.raises(m.RefreshMergeApprovalError, match="retitle INC-1"):
        _check(new, titles={"AIID-1": "AIID-1 and 9 title"})


def test_title_edit_passes_only_when_it_is_the_snapshots_own_title():
    edited = [PREV[0] | {"title": "Reportedly Old AIID title"}, *PREV[1:]]
    _check(edited, titles={"AIID-1": "Reportedly Old AIID title"})
    assert m._LAST_AIID_CLASS_USE["title_edit"] == 1
    # input that makes it fail: a title the snapshot does not carry for this row
    with pytest.raises(m.RefreshMergeApprovalError, match="title edit INC-1"):
        _check(edited, titles={"AIID-1": "A different upstream title"})
    # ... or the same edit with the class off (the pre-D114 gate)
    with pytest.raises(m.RefreshMergeApprovalError, match="title edit INC-1"):
        _check(edited, titles={"AIID-1": "Reportedly Old AIID title"}, aiid_class=False)


def test_title_edit_on_an_oecd_titled_row_is_not_waived():
    """A title edit on a row whose source ids are OECD-only is never waived by the
    class (the snapshot cannot supply its title). Scope: OECD-ONLY rows. Mixed
    AIID+OECD rows are covered by the 3,935 pin below (D116/D119)."""
    edited = [PREV[0], PREV[1], PREV[2] | {"title": "New OECD title"}]
    with pytest.raises(m.RefreshMergeApprovalError, match="title edit INC-3"):
        _check(edited, titles={"AIID-1": "New OECD title"})


# ---- the D114 binding precondition on any OECD lift ------------------------


def _marker(tmp_path, **auth):
    doc = {"authorization": {"decision": "D114", "ruled_by": "user", **auth}, "suppression": "built+gated"}
    p = tmp_path / "marker.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    import hashlib
    h = hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return p, h


def test_precondition_is_dormant_while_oecd_is_held():
    m._check_oecd_lift_precondition(False)


def test_precondition_refuses_an_oecd_lift_with_no_registered_suppression():
    assert m.REQUIRED_SUPPRESSION_MARKER_SHA256 is None, (
        "a suppression mechanism was registered: this test, the marker and the gate "
        "review must change together (D114)")
    with pytest.raises(m.OecdLiftPreconditionError, match="D114 binding precondition"):
        m._check_oecd_lift_precondition(True)


def test_precondition_refuses_even_a_well_formed_marker_when_no_hash_is_pinned(tmp_path):
    p, _h = _marker(tmp_path)
    with pytest.raises(m.OecdLiftPreconditionError, match="REQUIRED_SUPPRESSION_MARKER_SHA256 is None"):
        m._check_oecd_lift_precondition(True, marker_path=p)


def test_precondition_passes_only_with_pinned_hash_and_user_authorization(tmp_path):
    p, h = _marker(tmp_path)
    m._check_oecd_lift_precondition(True, marker_path=p, required_sha256=h)  # control: passes
    with pytest.raises(m.OecdLiftPreconditionError, match="not the one pinned"):
        m._check_oecd_lift_precondition(True, marker_path=p, required_sha256="0" * 64)
    p2, h2 = _marker(tmp_path, ruled_by="agent")
    with pytest.raises(m.OecdLiftPreconditionError, match="ruled_by == 'user'"):
        m._check_oecd_lift_precondition(True, marker_path=p2, required_sha256=h2)
    with pytest.raises(m.OecdLiftPreconditionError, match="does not exist"):
        m._check_oecd_lift_precondition(True, marker_path=tmp_path / "absent.json", required_sha256=h)


def test_committed_marker_path_is_absent():
    assert not m.SUPPRESSION_GATE_MARKER_PATH.exists()


@pytest.mark.real_gate
def test_run_refresh_gate_refuses_a_held_input_change_before_any_approval(monkeypatch):
    """The gate entry point itself: a changed held input aborts on the precondition
    even if the per-item checker would have passed; with held inputs at HEAD the
    standing class engages."""
    monkeypatch.setattr(m, "_load_gate_baseline", lambda *a, **k: (copy.deepcopy(PREV), False))
    monkeypatch.setattr(m, "_aiid_snapshot_titles", lambda *a, **k: {})
    monkeypatch.setattr(m, "_pair_inputs_changed", lambda *a, **k: True)
    with pytest.raises(m.OecdLiftPreconditionError):
        m._run_refresh_gate(copy.deepcopy(PREV), [], {})  # no change at all, still refused
    monkeypatch.setattr(m, "_pair_inputs_changed", lambda *a, **k: False)
    m._run_refresh_gate(PREV + [_row("INC-9", "New AIID", ["AIID-9"])], [], {})


# ---- (e): the per-item approval hash is pinned in code ---------------------


def test_default_approval_path_entries_hash_is_pinned_in_code(tmp_path, monkeypatch):
    entries = [{"kind": "merge", "from": "INC-00002", "into": "INC-00001"}]
    doc = {"entries": entries, "authorization": {
        "decision": "DX", "ruled_by": "user", "entries_sha256": m._refresh_merge_entries_sha256(entries)}}
    p = tmp_path / "D42-approved-refresh-merges.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    assert m._load_refresh_merge_approvals(p) != set()  # a non-default path keeps the old behaviour
    monkeypatch.setattr(m, "REFRESH_MERGE_APPROVAL_PATH", p)
    # signed, self-consistent file at the default path, but nothing pinned: refused
    with pytest.raises(m.RefreshMergeApprovalError, match="pinned in code"):
        m._load_refresh_merge_approvals(p)
    # tamper-plus-recompute: pin the ORIGINAL hash, then edit the entries and recompute
    monkeypatch.setattr(m, "REQUIRED_REFRESH_APPROVAL_ENTRIES_SHA256", m._refresh_merge_entries_sha256(entries))
    assert m._load_refresh_merge_approvals(p) == {("merge", "INC-00002", "INC-00001")}  # control
    tampered = entries + [{"kind": "merge", "from": "INC-00004", "into": "INC-00003"}]
    doc2 = {"entries": tampered, "authorization": {
        "decision": "DX", "ruled_by": "user", "entries_sha256": m._refresh_merge_entries_sha256(tampered)}}
    p.write_text(json.dumps(doc2), encoding="utf-8")
    with pytest.raises(m.RefreshMergeApprovalError, match="pinned in code"):
        m._load_refresh_merge_approvals(p)


def test_pin_is_none_and_default_approval_file_absent_until_a_ruling_is_recorded():
    assert m.REQUIRED_REFRESH_APPROVAL_ENTRIES_SHA256 is None
    p = m.REFRESH_MERGE_APPROVAL_PATH
    assert not p.exists() or json.loads(p.read_text(encoding="utf-8")).get("entries") == []


# ---- D115: the per-item rulings are recorded and INERT ---------------------


def test_d115_record_holds_the_ruled_items():
    doc = json.loads(D115.read_text(encoding="utf-8"))
    by = {r["item"]: r["ruling"] for r in doc["rulings"]}
    assert doc["decision"] == "D115" and doc["ruled_by"] == "user"
    for k in ("M1", "M2", "M5", "R1", "R2", "R3", "R4", "R5", "R6"):
        assert by[k] == "approve-in-principle", k
    for k in ("M3", "M4", "M6", "M7", "R7", "R8", "R9", "R10"):
        assert by[k] == "reject", k
    for k in ("R11", "R12"):
        assert by[k] == "pending-raw-record-read", k
    assert len(by) == 19


def test_d115_record_is_inert_to_the_approval_loader(tmp_path):
    doc = json.loads(D115.read_text(encoding="utf-8"))
    assert "entries" not in doc  # the loader's key
    assert m._load_refresh_merge_approvals(D115) == set()
    # input that would make it operative: the same content under the loader's key
    # with no signed authorization -> refused loudly, not silently accepted
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"entries": [{"kind": "merge", "from": r["from"], "into": r["into"]}
                                           for r in doc["rulings"] if r["kind"] == "merge"]}), encoding="utf-8")
    with pytest.raises(m.RefreshMergeApprovalError, match="authorizes nothing"):
        m._load_refresh_merge_approvals(bad)


def test_nothing_in_scripts_reads_the_d115_record():
    hits = [p.name for p in (ROOT / "scripts").rglob("*.py")
            if re.search(r"D115-d42|per-item-rulings", p.read_text(encoding="utf-8", errors="replace"))]
    assert hits == [], f"{hits} reference the D115 record; it must stay inert until suppression exists"


# ---- the lift as shipped ----------------------------------------------------


def test_the_aiid_snapshot_is_not_held_but_oecd_is():
    import hold_pair_inputs as h
    assert "aiid_full.json" not in h.held_files() and "oecd_aim_full_incidents.json" in h.held_files()


def test_the_12_hub_aiid_ids_ship_as_standalone_rows():
    """D114/(c): lifting AIID alone ships the 12 hub ids as single-source AIID rows;
    a later OECD lift would turn them into the bridges behind R2-R5, R9-R12 and
    M3/M6/M7. If this fails because they merged, an OECD lift happened: that needs
    the D114 suppression precondition."""
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    by_sid: dict[str, list[dict]] = {}
    for e in inc:
        for s in e["source_ids"]:
            by_sid.setdefault(s, []).append(e)
    hubs = [1595, 1713, 1609, 1644, 1657, 1671, 1672, 1673, 1679, 1680, 1684, 1723]
    for n in hubs:
        rows = by_sid.get(f"AIID-{n}", [])
        assert len(rows) == 1 and rows[0]["source_ids"] == [f"AIID-{n}"], n


def _oecd_titled_count(rows, oecd_titles):
    return sum(1 for e in rows if any(oecd_titles.get(s) == e["title"]
                                      for s in e["source_ids"] if s.startswith("OECD-AIM-")))


def _oecd_titles():
    return {r["source_id"]: r["title"] for r in json.loads(
        (ROOT / "ingest" / "oecd_aim_full_incidents.json").read_text(encoding="utf-8"))}


def test_oecd_titled_row_count_is_pinned_at_3935():
    """D116/D119: rows whose title equals the committed OECD ingest title for one
    of their own OECD ids. 3,937 on main before the AIID lift; 3,935 after, the
    two being INC-00437 and INC-14682 (D119 accepted the switch). Any further drop
    must be a deliberate, declared change to this number."""
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    assert _oecd_titled_count(inc, _oecd_titles()) == 3935
    by = {e["id"]: e for e in inc}
    for iid in ("INC-00437", "INC-14682"):
        assert _oecd_titled_count([by[iid]], _oecd_titles()) == 0, iid


def test_oecd_title_count_check_fires_on_a_retitled_row():
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    titles = _oecd_titles()
    base = _oecd_titled_count(inc, titles)
    victim = next(e for e in inc if any(titles.get(s) == e["title"] for s in e["source_ids"] if s.startswith("OECD-AIM-")))
    mutated = [dict(e, title="Mutated title") if e["id"] == victim["id"] else e for e in inc]
    assert _oecd_titled_count(mutated, titles) == base - 1 != 3935


def test_no_oecd_row_beyond_the_committed_oecd_ingest_is_in_the_corpus():
    """D116: add no new OECD rows. Every OECD-AIM id in the corpus is in the
    committed OECD ingest file (so none came from a lifted fresh crawl)."""
    ing = {r["source_id"] for r in json.loads((ROOT / "ingest" / "oecd_aim_full_incidents.json").read_text(encoding="utf-8"))}
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    corpus = {s for e in inc for s in e["source_ids"] if s.startswith("OECD-AIM-")}
    assert corpus <= ing and len(corpus) > 3000
