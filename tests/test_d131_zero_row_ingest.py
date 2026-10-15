"""D131 (user ruling 2026-10-14): an ingest file that parses but yields 0 rows from
a dict (renamed row key, falsy non-list) refuses; known side files are allowlisted;
a real [] still loads. Also covers gate-d129 A1: the OSError branch."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import merge_and_dedupe as m

REPO = Path(m.__file__).resolve().parent.parent
FLAG = m.REFRESH_RUN_ENV


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    monkeypatch.delenv(FLAG, raising=False)
    m._WRITTEN.clear()
    yield
    m._WRITTEN.clear()


def _src(tmp_path, body, name="x.json"):
    p = tmp_path / name
    p.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
    return p


@pytest.mark.parametrize("body", [
    {"items": [{"a": 1}]},                       # renamed row key
    {},                                          # empty dict, no key
    {"source": "x", "license": "y"},
    {"incidents": {}}, {"incidents": ""}, {"incidents": 0}, {"incidents": None},
    {"entries": {}}, {"data": ""},
    {"incidents": [], "entries": "oops"},        # a non-list under ANY present row key
])
def test_zero_row_or_falsy_non_list_dict_refuses(tmp_path, body):
    p = _src(tmp_path, body)
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(p)
    msg = str(ei.value)
    assert str(p) in msg and "D131" in msg and m.NON_REFRESH_REFUSED in msg


def test_refresh_mode_carries_the_full_sentence(tmp_path, monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(_src(tmp_path, {"items": [1]}))
    assert m.REFRESH_DID_NOT_SHIP in str(ei.value)


@pytest.mark.parametrize("name", [
    "aiid_full.provenance.json", "wave12_arxiv.provenance.json", "some_new.provenance.json",
    "cisa_kev.json", "cve_rejections.json",
])
def test_allowlisted_side_files_load_as_no_rows(tmp_path, name):
    assert m.load_source(_src(tmp_path, {"source": "x", "vulnerabilities": [{"a": 1}]}, name)) == []


@pytest.mark.parametrize("name", ["cisa_kev_v2.json", "my_cisa_kev.json", "provenance.json", "x.provenance.json.bak.json"])
def test_allowlist_is_exact_not_a_substring(tmp_path, name):
    with pytest.raises(m.IngestParseError):
        m.load_source(_src(tmp_path, {"items": []}, name))


@pytest.mark.parametrize("body,expect", [
    ([], []), ({"incidents": []}, []), ({"data": []}, []),
    ({"incidents": [], "entries": [{"a": 1}]}, [{"a": 1}]),
    ({"data": [{"a": 1}]}, [{"a": 1}]),
])
def test_real_empty_and_row_keys_load(tmp_path, body, expect):
    assert m.load_source(_src(tmp_path, body)) == expect


def test_oserror_branch_aborts(tmp_path):
    """gate-d129 A1: a directory named x.json is an OSError on read, not a JSON error."""
    d = tmp_path / "x.json"
    d.mkdir()
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(d)
    msg = str(ei.value)
    assert str(d) in msg and "cannot parse" in msg and ("PermissionError" in msg or "IsADirectoryError" in msg)


def test_real_ingest_files_all_load():
    files = sorted((REPO / "ingest").glob("*.json"))
    assert len(files) >= 28
    sides = [p for p in files if m._is_ingest_side_file(p)]
    assert {p.name for p in sides} >= {"cisa_kev.json", "cve_rejections.json"}
    for p in files:
        assert isinstance(m.load_source(p), list), p
    for p in sides:
        assert m.load_source(p) == []


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("d131_tree")
    shutil.copytree(REPO / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "ingest").mkdir()
    for f in (REPO / "ingest").glob("*.py"):
        shutil.copy(f, root / "ingest" / f.name)
    (root / "data").mkdir()
    return root


@pytest.mark.parametrize("refresh", [True, False])
def test_e2e_renamed_row_key_refuses_and_writes_nothing(tree, refresh):
    bad = tree / "ingest" / "drifted.json"
    bad.write_text(json.dumps({"items": [{"title": "t"}]}), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != FLAG}
    env.update(PYTHONIOENCODING="utf-8", MERGE_ALLOW_MISSING_LEGACY="1")
    if refresh:
        env[FLAG] = "1"
    try:
        r = subprocess.run([sys.executable, str(tree / "scripts" / "merge_and_dedupe.py")], cwd=tree, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    finally:
        bad.unlink()
    assert r.returncode != 0 and "drifted.json" in r.stderr and "D131" in r.stderr
    want = m.REFRESH_DID_NOT_SHIP if refresh else m.NON_REFRESH_REFUSED
    assert r.stderr.count(want) == 1
    assert list((tree / "data").iterdir()) == []
