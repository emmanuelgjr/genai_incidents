"""The reconciliation delta check must be seen to FIRE (working agreement 6):
clean input passes; each deliberate corruption is caught."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rejected_cve_delta", ROOT / "scripts/audit/rejected_cve_delta.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

REJ = {"CVE-2099-0001"}


def _before():
    ent = lambda i, cves, src: {"id": i, "cve_ids": cves, "source_ids": src, "severity": "High",
                                "updated": "2026-06-10", "last_seen": "2026-06-10"}
    return {"incident_count": 3, "generated": "2026-09-18", "incidents": [
        ent("INC-1", ["CVE-2099-0001"], ["CVE-2099-0001"]),               # retract
        ent("INC-2", ["CVE-2099-0001", "CVE-2025-1"], ["CVE-2099-0001", "GHSA-a"]),  # flag only
        ent("INC-3", ["CVE-2025-9"], ["CVE-2025-9"]),                     # untouched
    ]}


def _after():
    a = copy.deepcopy(_before())
    i1, i2 = a["incidents"][0], a["incidents"][1]
    i1.update(status="retracted", status_reason={"code": "cve-rejected", "as_of": "2026-10-03"},
              rejected_cve_ids=["CVE-2099-0001"], updated="2026-10-03", last_seen="2026-10-03")
    i2.update(rejected_cve_ids=["CVE-2099-0001"], updated="2026-10-03", last_seen="2026-10-03")
    a.update(incident_count=2, retracted_count=1, generated="2026-10-03")
    return a


def test_clean_delta_has_no_defects():
    assert d.compute(_before(), _after(), REJ)["defects"] == []


def test_unrelated_entry_change_is_caught():
    a = _after(); a["incidents"][2]["severity"] = "Low"
    assert any("INC-3" in x and "unaffected" in x for x in d.compute(_before(), a, REJ)["defects"])


def test_unexpected_field_on_affected_entry_is_caught():
    a = _after(); a["incidents"][0]["severity"] = "Low"
    assert any("INC-1" in x and "severity" in x for x in d.compute(_before(), a, REJ)["defects"])


def test_deleted_entry_is_caught():
    a = _after(); del a["incidents"][0]
    assert any("INC-1" in x and "added/removed" in x for x in d.compute(_before(), a, REJ)["defects"])


def test_missed_retraction_is_caught():
    a = _after(); a["incidents"][0].pop("status"); a["incidents"][0].pop("status_reason")
    assert any("INC-1" in x and "status" in x for x in d.compute(_before(), a, REJ)["defects"])


def test_wrongly_retracted_corroborated_entry_is_caught():
    a = _after(); a["incidents"][1].update(status="retracted", status_reason={"code": "cve-rejected", "as_of": "x"})
    assert any("INC-2" in x for x in d.compute(_before(), a, REJ)["defects"])
