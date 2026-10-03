"""WS4-T2 / board note N1: a CVE the CVE Program has REJECTED must not ship as a
standing incident. Entries are never deleted (invariant 3): they are marked
``status: retracted`` (ID still resolves) or, when they stand on other
evidence, flagged with ``rejected_cve_ids``.

Three layers, each able to fail independently:
  * the pure rule (_apply_cve_rejections),
  * the build (merge_and_dedupe.main) from a fixture snapshot,
  * the COMMITTED corpus against the COMMITTED snapshot -- the regression test
    for the 17-entry defect. GENAI_INCIDENTS_JSON points it at other data (used
    to show it failing on the pre-fix corpus).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import merge_and_dedupe as m
import validate
from tests.test_merge_and_dedupe import _oecd_entry, _setup_tmp_repo

ROOT = Path(__file__).resolve().parents[1]
REJ = {"CVE-2099-0001": {"state": "REJECTED", "checked": "2026-10-03"},
       "CVE-2099-0002": {"state": "REJECTED", "checked": "2026-10-03"}}


def _e(cves, sources):
    return {"cve_ids": list(cves), "source_ids": list(sources), "title": "t"}


# ----- the rule -----

def test_only_cve_rejected_is_retracted():
    e = _e(["CVE-2099-0001"], ["CVE-2099-0001"])
    assert m._apply_cve_rejections(e, REJ) is True
    assert e["status"] == "retracted"
    assert e["status_reason"] == {"code": "cve-rejected", "as_of": "2026-10-03"}
    assert e["rejected_cve_ids"] == ["CVE-2099-0001"]
    assert e["cve_ids"] == ["CVE-2099-0001"], "ids are flagged, never dropped"


def test_corroborated_entry_is_flagged_not_retracted():
    # one rejected CVE among live ones, and a non-CVE source: it stands.
    e = _e(["CVE-2099-0001", "CVE-2025-1"], ["CVE-2099-0001", "GHSA-xxxx-yyyy-zzzz"])
    assert m._apply_cve_rejections(e, REJ) is False
    assert "status" not in e
    assert e["rejected_cve_ids"] == ["CVE-2099-0001"]


def test_all_cves_rejected_but_other_source_still_stands():
    e = _e(["CVE-2099-0001"], ["CVE-2099-0001", "AIID-123"])
    assert m._apply_cve_rejections(e, REJ) is False
    assert "status" not in e and e["rejected_cve_ids"] == ["CVE-2099-0001"]


def test_marker_is_shed_when_cve_no_longer_rejected():
    e = _e(["CVE-2099-0001"], ["CVE-2099-0001"])
    m._apply_cve_rejections(e, REJ)
    assert m._apply_cve_rejections(e, {}) is False
    assert not ({"status", "status_reason", "rejected_cve_ids"} & e.keys())


def test_status_fields_are_content_fields():
    # so a retraction bumps `updated` exactly once (invariant 4)
    assert {"status", "status_reason", "rejected_cve_ids"} <= set(m._CONTENT_FIELDS)


# ----- the build -----

def _cve_row(cve, extra=None):
    r = _oecd_entry(cve, f"Vuln {cve}")
    r.update({"cve_id": cve, "tags": ["cve", "nvd"],
              "category": "vulnerability-disclosure"})
    r["references"] = [{"url": f"https://nvd.nist.gov/vuln/detail/{cve}"}]
    r.update(extra or {})
    return r


def test_build_retracts_keeps_entry_and_excludes_it_from_count(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    snap = tmp_path / "cve_rejections.json"
    snap.write_text(json.dumps({"states": REJ}), encoding="utf-8")
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", snap)
    (ingest / "src.json").write_text(json.dumps(
        [_cve_row("CVE-2099-0001"), _cve_row("CVE-2025-0003")]), encoding="utf-8")
    m.main()
    d = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    by = {e["cve_ids"][0]: e for e in d["incidents"]}
    assert by["CVE-2099-0001"]["status"] == "retracted", "entry kept, not deleted"
    assert "status" not in by["CVE-2025-0003"]
    assert len(d["incidents"]) == 2
    assert d["incident_count"] == 1 and d["retracted_count"] == 1
    assert validate.check_status(d, set(REJ)) == []
    # a second build is byte-stable (no oscillation, no repeated `updated` bump)
    first = (data / "incidents.json").read_text(encoding="utf-8")
    m.main()
    assert (data / "incidents.json").read_text(encoding="utf-8") == first


def test_validator_fires_on_unretracted_rejected_entry():
    ok = {"id": "INC-1", "cve_ids": ["CVE-2099-0001"], "source_ids": ["CVE-2099-0001"],
          "status": "retracted", "status_reason": {"code": "cve-rejected", "as_of": "2026-10-03"},
          "rejected_cve_ids": ["CVE-2099-0001"]}
    data = {"incident_count": 0, "retracted_count": 1, "incidents": [ok]}
    assert validate.check_status(data, set(REJ)) == []
    bad = {k: v for k, v in ok.items() if k not in ("status", "status_reason", "rejected_cve_ids")}
    data = {"incident_count": 1, "incidents": [bad]}
    problems = validate.check_status(data, set(REJ))
    assert any("without a rejected_cve_ids flag" in p for p in problems)
    assert any("not retracted" in p for p in problems)


# ----- the committed corpus (the N1 regression) -----

def _committed():
    path = Path(os.environ.get("GENAI_INCIDENTS_JSON", ROOT / "data" / "incidents.json"))
    data = json.loads(path.read_text(encoding="utf-8"))
    snap = json.loads((ROOT / "ingest" / "cve_rejections.json").read_text(encoding="utf-8"))
    rejected = {c for c, r in snap["states"].items() if r["state"] == "REJECTED"}
    return data, rejected


def test_no_entry_resting_only_on_rejected_cves_ships_active():
    data, rejected = _committed()
    assert rejected, "snapshot lists no REJECTED CVE: the check below would be vacuous"
    shipped = [
        e["id"] for e in data["incidents"]
        if e.get("cve_ids") and set(e["cve_ids"]) <= rejected
        and set(e.get("source_ids") or []) <= rejected
        and e.get("status") != "retracted"
    ]
    assert shipped == [], f"entries resting only on REJECTED CVEs ship as active: {shipped}"


def test_every_rejected_cve_on_any_entry_is_flagged():
    data, rejected = _committed()
    assert validate.check_status(data, rejected) == []
