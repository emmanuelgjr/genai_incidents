"""D138: closes the three gate-d131 advisories (A1/A2/A3) in load_source."""
from __future__ import annotations

import json

import pytest

import merge_and_dedupe as m

ROW = {"id": "r"}


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    monkeypatch.delenv(m.REFRESH_RUN_ENV, raising=False)
    m._WRITTEN.clear()
    yield
    m._WRITTEN.clear()


def _src(tmp_path, body, name="x.json"):
    p = tmp_path / name
    p.write_text(json.dumps(body), encoding="utf-8")
    return p


def _refuses(p, needle):
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(p)
    msg = str(ei.value)
    assert "[FATAL]" in msg and str(p) in msg and "D138" in msg and needle in msg
    assert msg.count(m.NON_REFRESH_REFUSED) == 1


@pytest.mark.parametrize("body", [
    {"incidents": [], "items": [ROW]},
    {"entries": [], "data": [], "rows": [ROW]},
])
def test_a1_empty_row_key_plus_drifted_list_refuses(tmp_path, body):
    _refuses(_src(tmp_path, body), "non-row key")


@pytest.mark.parametrize("name", ["cisa_kev.json", "cve_rejections.json", "a.provenance.json"])
@pytest.mark.parametrize("key", ["incidents", "entries", "data"])
def test_a2_side_file_with_nonempty_row_key_refuses(tmp_path, name, key):
    _refuses(_src(tmp_path, {key: [ROW]}, name), "side file")


def test_a3_two_nonempty_row_keys_refuse(tmp_path):
    _refuses(_src(tmp_path, {"incidents": [ROW], "entries": [ROW]}), "more than one row key")


@pytest.mark.parametrize("name", ["cisa_kev.json", "cve_rejections.json", "a.provenance.json"])
def test_a3_side_file_name_with_list_payload_refuses(tmp_path, name):
    _refuses(_src(tmp_path, [ROW], name), "payload is a list")


# controls: legitimate shapes still load
def test_controls_legit_shapes_load(tmp_path):
    assert m.load_source(_src(tmp_path, [ROW])) == [ROW]
    assert m.load_source(_src(tmp_path, [], "e.json")) == []
    assert m.load_source(_src(tmp_path, {"incidents": [ROW]}, "b.json")) == [ROW]
    assert m.load_source(_src(tmp_path, {"entries": [ROW], "meta": ["a"]}, "c.json")) == [ROW]
    assert m.load_source(_src(tmp_path, {"incidents": [], "entries": [ROW]}, "d.json")) == [ROW]
    assert m.load_source(_src(tmp_path, {"incidents": [], "note": "x", "meta": []}, "f.json")) == []
    # side files with their own metadata lists, and empty row keys
    kev = {"vulnerabilities": [{"cveID": "CVE-1"}], "count": 1}
    assert m.load_source(_src(tmp_path, kev, "cisa_kev.json")) == []
    assert m.load_source(_src(tmp_path, {"states": ["x"], "incidents": []}, "cve_rejections.json")) == []
    assert m.load_source(_src(tmp_path, {"selected": [1], "entries_written": 3}, "w.provenance.json")) == []
