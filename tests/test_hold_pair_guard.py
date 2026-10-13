"""The work-tree guard (refresh PR #101, 2026-10-13: a stash dir INSIDE the work
tree was committed by create-pull-request, ~385k lines of fresh OECD/AIID bytes).

Each check is paired with the input that makes it fail (agreement 6)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import hold_pair_inputs as h  # noqa: E402


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


def _fresh(repo, name="oecd_aim_full_incidents.json"):
    (repo / "ingest" / name).write_text('{"fresh": 1}\n', encoding="utf-8", newline="")


def test_guard_passes_on_a_held_tree_with_stash_outside(repo, tmp_path_factory):
    outside = tmp_path_factory.mktemp("stash") / "held-pair-inputs"
    _fresh(repo)
    h.hold(repo, outside)
    assert h.check_held_paths_clean(repo, outside) == []
    assert h.main(["--check-clean", "--root", str(repo), "--stash-dir", str(outside)]) == 0


def test_guard_fires_on_stash_inside_tree(repo):
    inside = repo / "held-pair-inputs"
    _fresh(repo)
    h.hold(repo, inside)  # the old workflow's layout
    problems = h.check_held_paths_clean(repo, inside)
    assert any("inside the work tree" in p for p in problems)
    assert any("stash content in work tree" in p for p in problems)
    assert h.main(["--check-clean", "--root", str(repo), "--stash-dir", str(inside)]) == 1


def test_guard_fires_on_unrestored_held_path_then_passes_once_restored(repo, tmp_path_factory):
    outside = tmp_path_factory.mktemp("stash2") / "held-pair-inputs"
    _fresh(repo, "aiid_oecd_relationships.json")
    assert any("held path differs" in x for x in h.check_held_paths_clean(repo, outside))
    assert h.main(["--check-clean", "--root", str(repo), "--stash-dir", str(outside)]) == 1
    _git(repo, "checkout", "--", "ingest/aiid_oecd_relationships.json")
    assert h.check_held_paths_clean(repo, outside) == []


def test_guard_ignores_the_lifted_aiid_snapshot(repo, tmp_path_factory):
    """D114: a fresh AIID snapshot in the tree is expected (it is committed by the
    refresh PR) and must not trip the held-path guard."""
    outside = tmp_path_factory.mktemp("stash4") / "held-pair-inputs"
    _fresh(repo, "aiid_full.json")
    assert h.check_held_paths_clean(repo, outside) == []


def test_guard_ignores_non_held_ingest_changes(repo, tmp_path_factory):
    outside = tmp_path_factory.mktemp("stash3") / "held-pair-inputs"
    (repo / "ingest" / "cisa_kev.json").write_text("[1]\n", encoding="utf-8", newline="")
    assert h.check_held_paths_clean(repo, outside) == []
