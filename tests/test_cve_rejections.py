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
    assert {"status", "rejected_cve_ids"} <= set(m._CONTENT_FIELDS)
    # ...but a re-check date is not content (it would churn `updated` weekly)
    assert "status_reason" not in m._CONTENT_FIELDS


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


# ----- gate 1 fixes -----

def test_stix_and_misp_do_not_emit_rejected_cves_as_vulnerabilities():
    import export_misp
    import export_stix
    inc = {"id": "INC-00001", "title": "t", "date": "2026-01", "year": 2026,
           "severity": "High", "description": "d", "category": "x",
           "cve_ids": ["CVE-2099-0001", "CVE-2025-1"],
           "rejected_cve_ids": ["CVE-2099-0001"],
           "references": [{"url": "https://example.com/a"}], "tags": []}
    bundle = export_stix.build_bundle([inc])
    names = {o["name"] for o in bundle["objects"] if o["type"] == "vulnerability"}
    assert names == {"CVE-2025-1"}
    sdo = next(o for o in bundle["objects"] if o["type"] == "x-genai-incident")
    assert sdo["x_rejected_cve_ids"] == ["CVE-2099-0001"]
    assert sdo["x_cve_ids"] == ["CVE-2099-0001", "CVE-2025-1"]
    vuln_ids = {o["id"] for o in bundle["objects"] if o["type"] == "vulnerability"}
    assert all(o["target_ref"] in vuln_ids
               for o in bundle["objects"] if o.get("relationship_type") == "exploits")
    vals = {a["value"] for a in export_misp._incident_attributes(inc) if a["type"] == "vulnerability"}
    assert vals == {"CVE-2025-1"}


def test_recheck_with_unchanged_verdict_does_not_bump_updated(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    snap = tmp_path / "cve_rejections.json"
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", snap)
    (ingest / "src.json").write_text(json.dumps([_cve_row("CVE-2099-0001")]), encoding="utf-8")

    class _D(m.date):
        _pinned = None

        @classmethod
        def today(cls):
            return cls._pinned
    import datetime
    monkeypatch.setattr(m, "date", _D)
    monkeypatch.setattr(m, "utc_today", lambda: _D._pinned)

    def build(day, checked):
        _D._pinned = datetime.date(*day)
        snap.write_text(json.dumps({"states": {"CVE-2099-0001": {"state": "REJECTED", "checked": checked}}}),
                        encoding="utf-8")
        m.main()
        return json.loads((data / "incidents.json").read_text(encoding="utf-8"))["incidents"][0]

    a = build((2099, 6, 1), "2099-06-01")
    b = build((2099, 6, 8), "2099-06-08")
    assert a["status"] == b["status"] == "retracted"
    assert b["status_reason"]["as_of"] == "2099-06-08", "the re-check date is still recorded"
    assert (b["updated"], b["last_seen"]) == (a["updated"], a["last_seen"]), "...without churning updated"


def test_ingest_survives_nvd_error_on_a_rejected_hit(tmp_path, monkeypatch, capsys):
    import sys
    import ingest_cve_rejections as ing
    inc = tmp_path / "incidents.json"
    inc.write_text(json.dumps({"incidents": [
        {"cve_ids": ["CVE-2099-0001"]}, {"cve_ids": ["CVE-2099-0002"]}]}), encoding="utf-8")
    out = tmp_path / "cve_rejections.json"
    monkeypatch.setattr(ing, "INCIDENTS", inc)
    monkeypatch.setattr(ing, "OUT_FILE", out)
    monkeypatch.setattr(ing, "LOG_DIR", tmp_path / "sweep-log")
    monkeypatch.setattr(ing, "check_cvelist", lambda c: {"state": "REJECTED" if c.endswith("1") else "PUBLISHED"})

    def boom(c):
        raise OSError("NVD 503")
    monkeypatch.setattr(ing, "check_nvd", boom)
    monkeypatch.setattr(sys, "argv", ["x"])
    ing.main()
    st = json.loads(out.read_text(encoding="utf-8"))["states"]
    assert st["CVE-2099-0001"]["state"] == "REJECTED" and st["CVE-2099-0001"]["nvd_vuln_status"] is None
    assert st["CVE-2099-0002"]["state"] == "PUBLISHED", "the sweep continued past the NVD error"


def test_slim_envelope_corruption_is_caught():
    slim = {"incident_count": 1, "retracted_count": 1,
            "incidents": [{"id": "INC-1", "status": "retracted"}, {"id": "INC-2"}]}
    assert validate.check_envelope(slim) == []
    slim["incident_count"] = 2  # stale count: retracted entry counted
    assert validate.check_envelope(slim)
    slim.update(incident_count=1, retracted_count=0)
    assert validate.check_envelope(slim)


def test_committed_slim_file_envelope_is_consistent():
    slim = json.loads((ROOT / "data" / "incidents.min.json").read_text(encoding="utf-8"))
    assert validate.check_envelope(slim) == []
