"""D129 (user ruling 2026-10-14): a corrupt ingest/*.json fails the build closed,
with the job-aware abort sentence, before any output is written."""

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


def _src(tmp_path, body):
    p = tmp_path / "x.json"
    p.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
    return p


@pytest.mark.parametrize("body", ["{ not json", "", '{"incidents": [', "[1, 2,"])
def test_unparseable_file_aborts_naming_file_and_error(tmp_path, body):
    p = _src(tmp_path, body)
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(p)
    msg = str(ei.value)
    assert str(p) in msg and "JSONDecodeError" in msg
    assert m.NON_REFRESH_REFUSED in msg


def test_undecodable_bytes_abort(tmp_path):
    p = tmp_path / "x.json"
    p.write_bytes(b"[\xff\xfe]")
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(p)
    assert "UnicodeDecodeError" in str(ei.value)


def test_refresh_mode_carries_the_full_sentence(tmp_path, monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    with pytest.raises(m.IngestParseError) as ei:
        m.load_source(_src(tmp_path, "{ not json"))
    assert m.REFRESH_DID_NOT_SHIP in str(ei.value)


@pytest.mark.parametrize("body", ["42", '"text"', "null", "true", '{"incidents": "oops"}', '{"data": 5}'])
def test_payload_that_is_not_a_list_of_rows_aborts(tmp_path, body):
    with pytest.raises(m.IngestParseError):
        m.load_source(_src(tmp_path, body))


@pytest.mark.parametrize("body,expect", [
    ([], []),                                    # a legitimately empty list is not an error
    ({}, []),
    ({"incidents": []}, []),
    ({"source": "x", "license": "y"}, []),       # provenance-style side file: no rows, by design
    ({"vulnerabilities": [{"a": 1}]}, []),       # cisa_kev-style side file
    ({"entries": [{"a": 1}]}, [{"a": 1}]),
    ([{"a": 1}], [{"a": 1}]),
])
def test_legitimate_shapes_still_load(tmp_path, body, expect):
    assert m.load_source(_src(tmp_path, body)) == expect


def test_every_ingest_file_in_the_repo_loads():
    """The fix must not break the real build."""
    for p in sorted((REPO / "ingest").glob("*.json")):
        assert isinstance(m.load_source(p), list), p


# ---- end to end: both modes, nothing written ------------------------------
@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("d129_tree")
    shutil.copytree(REPO / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "ingest").mkdir()
    for f in (REPO / "ingest").glob("*.py"):
        shutil.copy(f, root / "ingest" / f.name)
    (root / "data").mkdir()
    return root


def _run(root, refresh):
    env = {k: v for k, v in os.environ.items() if k != FLAG}
    env.update(PYTHONIOENCODING="utf-8", MERGE_ALLOW_MISSING_LEGACY="1")
    if refresh:
        env[FLAG] = "1"
    return subprocess.run([sys.executable, str(root / "scripts" / "merge_and_dedupe.py")], cwd=root, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)


@pytest.mark.parametrize("refresh", [True, False])
def test_e2e_corrupt_ingest_refuses_and_writes_nothing(tree, refresh):
    bad = tree / "ingest" / "broken_source.json"
    bad.write_text('{"incidents": [', encoding="utf-8")
    try:
        r = _run(tree, refresh)
    finally:
        bad.unlink()
    assert r.returncode != 0
    assert "broken_source.json" in r.stderr and "JSONDecodeError" in r.stderr
    want, other = (m.REFRESH_DID_NOT_SHIP, m.NON_REFRESH_REFUSED) if refresh else (m.NON_REFRESH_REFUSED, m.REFRESH_DID_NOT_SHIP)
    assert r.stderr.count(want) == 1 and other not in r.stderr
    assert "failed to parse" not in r.stdout  # the old WARN path is gone
    assert list((tree / "data").iterdir()) == []


def test_e2e_control_clean_ingest_still_builds(tree):
    ok = tree / "ingest" / "empty_source.json"
    ok.write_text("[]", encoding="utf-8")
    try:
        r = _run(tree, False)
    finally:
        ok.unlink()
    # an empty scratch tree may still stop on some LATER, unrelated refusal; it must not be this one
    assert "empty_source.json" not in r.stderr and "cannot parse" not in r.stderr.split("D42")[0]
