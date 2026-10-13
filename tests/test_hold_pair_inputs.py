"""D66 decouple: scripts/hold_pair_inputs.py restores every frozen OECD/AIID
input to its committed version and stashes the fresh bytes.

Name the input that makes each check fail (agreement 6): a changed byte in a
frozen input must be reported as changed BEFORE the hold (the gate's own
detector says True), restored AFTER (detector False, bytes equal to HEAD), and
the fresh bytes must be in the stash. A hold that does not take must make the
script exit 1.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import hold_pair_inputs as h  # noqa: E402
import merge_and_dedupe as m  # noqa: E402


def _git(root, *a):
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *a],
        cwd=root, check=True, capture_output=True,
    )


@pytest.fixture()
def repo(tmp_path):
    (tmp_path / "ingest").mkdir()
    for name in h.held_files():
        (tmp_path / "ingest" / name).write_text(json.dumps({"committed": name}) + "\n", encoding="utf-8", newline="")
    (tmp_path / "ingest" / "cisa_kev.json").write_text("[]\n", encoding="utf-8", newline="")
    _git(tmp_path, "-c", "core.autocrlf=false", "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def test_held_files_are_the_gates_pair_files_plus_aiid_provenance():
    assert set(m._PAIR_INPUT_FILES) <= set(h.held_files())
    assert "aiid_full.provenance.json" in h.held_files()
    assert "airi_navigator_incidents.json" in h.held_files()  # a revived AIRI is held


def test_hold_restores_changed_inputs_and_stashes_fresh_bytes(repo, tmp_path_factory):
    stash = tmp_path_factory.mktemp("stash")
    oecd = repo / "ingest" / "oecd_aim_full_incidents.json"
    airi = repo / "ingest" / "airi_navigator_incidents.json"
    kev = repo / "ingest" / "cisa_kev.json"
    oecd.write_text('{"fresh": 1}\n', encoding="utf-8", newline="")
    airi.write_text('{"revived": 1}\n', encoding="utf-8", newline="")
    kev.write_text('["new kev"]\n', encoding="utf-8", newline="")
    assert m._pair_inputs_changed(repo) is True  # the gate would fire

    report = h.hold(repo, stash)

    assert m._pair_inputs_changed(repo) is False
    assert json.loads(oecd.read_text()) == {"committed": "oecd_aim_full_incidents.json"}
    assert (stash / "oecd_aim_full_incidents.json").read_text() == '{"fresh": 1}\n'
    assert (stash / "airi_navigator_incidents.json").read_text() == '{"revived": 1}\n'
    assert report["held_count"] == 2
    assert report["files"]["aiid_full.json"]["changed"] is False
    assert kev.read_text() == '["new kev"]\n'  # non-pair sources are NOT held


def test_hold_removes_an_untracked_pair_file(repo, tmp_path_factory):
    stash = tmp_path_factory.mktemp("stash")
    new = repo / "ingest" / "aiid_oecd_relationships.json"
    _git(repo, "rm", "-q", "-f", str(new))
    _git(repo, "commit", "-q", "-m", "drop")
    new.write_text("{}\n", encoding="utf-8", newline="")
    h.hold(repo, stash)
    assert not new.exists()
    assert (stash / "aiid_oecd_relationships.json").exists()


def test_hold_is_a_noop_when_nothing_changed(repo, tmp_path_factory):
    stash = tmp_path_factory.mktemp("stash")
    assert h.hold(repo, stash)["held_count"] == 0
    assert h.main(["--stash-dir", str(stash), "--root", str(repo)]) == 0


def test_postcheck_fails_when_the_restore_does_not_take(repo, tmp_path_factory, monkeypatch):
    stash = tmp_path_factory.mktemp("stash")
    (repo / "ingest" / "aiid_full.json").write_text('{"fresh": 1}\n', encoding="utf-8", newline="")
    # sabotage: pretend the restore happened but leave the fresh bytes in place
    monkeypatch.setattr(h, "hold", lambda root, stash_dir: {"files": {}, "held_count": 0})
    assert h.main(["--stash-dir", str(stash), "--root", str(repo)]) == 1
