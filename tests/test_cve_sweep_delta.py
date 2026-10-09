"""The sweep delta check must be seen to FIRE (working agreement 6): clean input
passes; each deliberate corruption is caught."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cve_sweep_delta", ROOT / "scripts/audit/cve_sweep_delta.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

REJ = {"CVE-2099-0001", "CVE-2099-0005"}
DISP = {"CVE-2099-0002"}


def _ent(i, cves, src, **kw):
    e = {"id": i, "cve_ids": cves, "source_ids": src, "severity": "High", "confidence": "medium",
         "updated": "2026-06-10", "last_seen": "2026-06-10"}
    e.update(kw)
    return e


def _before():
    return {"incident_count": 4, "retracted_count": 1, "generated": "2026-10-04", "incidents": [
        _ent("INC-1", ["CVE-2099-0001"], ["CVE-2099-0001"]),                      # newly retracted
        _ent("INC-2", ["CVE-2099-0002"], ["CVE-2099-0002"]),                      # newly disputed
        _ent("INC-3", ["CVE-2025-9"], ["CVE-2025-9"]),                            # untouched
        _ent("INC-4", ["CVE-2099-0005"], ["CVE-2099-0005"], status="retracted",   # steady (as_of moves)
             status_reason={"code": "cve-rejected", "as_of": "2026-10-03"},
             rejected_cve_ids=["CVE-2099-0005"]),
        _ent("INC-5", ["CVE-2099-0002"], ["CVE-2099-0002", "AIID-1"]),            # corroborated: stands
    ]}


def _after():
    a = copy.deepcopy(_before())
    i = {e["id"]: e for e in a["incidents"]}
    i["INC-1"].update(status="retracted", status_reason={"code": "cve-rejected", "as_of": "2026-10-09"},
                      rejected_cve_ids=["CVE-2099-0001"], updated="2026-10-09", last_seen="2026-10-09")
    i["INC-2"].update(status="disputed", status_reason={"code": "cve-disputed", "as_of": "2026-10-09"},
                      confidence="low", updated="2026-10-09", last_seen="2026-10-09")
    i["INC-4"]["status_reason"]["as_of"] = "2026-10-09"
    a.update(incident_count=3, retracted_count=2, generated="2026-10-09")
    return a


def _run(a):
    return d.compute(_before(), a, REJ, DISP)


def test_clean_delta_has_no_defects_and_classifies_correctly():
    r = _run(_after())
    assert r["defects"] == []
    assert r["classes"]["newly"]["retracted"] == ["INC-1"]
    assert r["classes"]["newly"]["disputed"] == ["INC-2"]
    assert r["classes"]["steady_as_of_moved"] == ["INC-4"]
    assert set(r["entries"]) == {"INC-1", "INC-2", "INC-4"}


def test_unrelated_entry_change_is_caught():
    a = _after(); a["incidents"][2]["severity"] = "Low"
    assert any("INC-3" in x and "steady" in x for x in _run(a)["defects"])


def test_confidence_not_lowered_is_caught():
    a = _after(); a["incidents"][1]["confidence"] = "medium"
    assert any("INC-2" in x and "one level down" in x for x in _run(a)["defects"])


def test_confidence_lowered_twice_is_caught():
    a = _after(); a["incidents"][1]["confidence"] = "low"; a["incidents"][1]["confidence"] = "low"
    b = _before(); b["incidents"][1]["confidence"] = "high"
    r = d.compute(b, a, REJ, DISP)
    assert any("INC-2" in x and "one level down" in x for x in r["defects"])


def test_corroborated_entry_wrongly_marked_disputed_is_caught():
    a = _after(); a["incidents"][4].update(status="disputed",
                                           status_reason={"code": "cve-disputed", "as_of": "x"})
    assert any("INC-5" in x for x in _run(a)["defects"])


def test_missed_dispute_is_caught():
    a = _after()
    for k in ("status", "status_reason"):
        a["incidents"][1].pop(k)
    assert any("INC-2" in x and "marker" in x for x in _run(a)["defects"])


def test_wrong_code_is_caught():
    a = _after(); a["incidents"][1]["status_reason"]["code"] = "cve-rejected"
    assert any("INC-2" in x for x in _run(a)["defects"])


def test_steady_entry_losing_its_marker_is_caught():
    a = _after(); a["incidents"][3].pop("status"); a["incidents"][3].pop("status_reason")
    assert _run(a)["defects"], "an already-retracted entry that silently un-retracts is a defect"


def test_deleted_entry_is_caught():
    a = _after(); del a["incidents"][0]
    assert any("INC-1" in x and "added/removed" in x for x in _run(a)["defects"])


def test_unexpected_field_on_transition_is_caught():
    a = _after(); a["incidents"][0]["severity"] = "Low"
    assert any("INC-1" in x and "severity" in x for x in _run(a)["defects"])


def test_header_change_is_caught():
    a = _after(); a["title"] = "x"
    assert any("header field" in x for x in _run(a)["defects"])


def test_entry_hashes_see_a_single_byte_change():
    h1 = d.entry_hashes(_before())
    b = _before(); b["incidents"][2]["severity"] = "Hig"
    h2 = d.entry_hashes(b)
    assert [i for i in h1 if h1[i] != h2[i]] == ["INC-3"]



# --- v2.13.0 (D57): review_by propagation declared as an intended delta ---

_FR = {"airi_navigator": {"status": "stale", "last_success": "2026-05-31",
                          "hold": {"decision": "D57", "until": "2027-01-07", "note": "n"}}}


def _with_marker(doc, review_by=None):
    doc = copy.deepcopy(doc)
    m = {"status": "stale", "as_of": "2026-05-31", "sources": ["airi_navigator"]}
    if review_by:
        m["review_by"] = review_by
    {e["id"]: e for e in doc["incidents"]}["INC-3"]["source_freshness"] = m
    return doc


def test_review_by_addition_is_classified_not_a_defect_when_declared():
    r = d.compute(_with_marker(_before()), _with_marker(_after(), "2027-01-07"), REJ, DISP, _FR)
    assert r["defects"] == []
    assert r["classes"]["freshness_review_by_added"] == ["INC-3"]


def test_review_by_change_fires_when_undeclared_wrong_or_missing():
    before = _with_marker(_before())
    assert d.compute(before, _with_marker(_after(), "2027-01-07"), REJ, DISP)["defects"]       # undeclared
    assert d.compute(before, _with_marker(_after(), "2027-02-01"), REJ, DISP, _FR)["defects"]  # wrong date
    assert d.compute(before, _with_marker(_after()), REJ, DISP, _FR)["defects"]                # not added
