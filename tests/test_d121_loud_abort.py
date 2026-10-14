"""D121 (user ruling 2026-10-13): fail-closed stays, as a LOUD abort. A gate
refusal must say the whole refresh did not ship, and why."""

from __future__ import annotations

import pytest

import merge_and_dedupe as m

PREV = [
    {"id": "INC-1", "title": "A", "source_ids": ["AIID-1"]},
    {"id": "INC-2", "title": "B", "source_ids": ["AIID-2"]},
]


def test_aiid_side_refusal_says_the_whole_refresh_did_not_ship():
    new = [PREV[0] | {"source_ids": ["AIID-1", "AIID-2"]}]
    dep = [{"from": "INC-2", "into": "INC-1", "reason": "merged", "retired_source_ids": ["AIID-2"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(
            PREV, new, dep, approval_path=m.Path("none.json"), pair_inputs_changed=False,
            aiid_class=True, aiid_titles={})
    msg = str(ei.value)
    assert "THE WHOLE REFRESH DID NOT SHIP" in msg
    for src in ("AIAAIC", "CISA KEV", "CVE rejection sweep"):
        assert src in msg
    assert "merge INC-2 -> INC-1" in msg  # the cause is listed with it


def test_oecd_lift_refusal_says_the_whole_refresh_did_not_ship():
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    assert "THE WHOLE REFRESH DID NOT SHIP" in str(ei.value) and "AIAAIC" in str(ei.value)


def test_the_check_fires_if_the_sentence_is_dropped(monkeypatch):
    monkeypatch.setattr(m, "REFRESH_DID_NOT_SHIP", "")
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    assert "THE WHOLE REFRESH DID NOT SHIP" not in str(ei.value)


# ---- hardening batch (advisory A1): EVERY refresh-gate refusal says it ----
import ast
import json
import subprocess
from pathlib import Path

SENTENCE = "THE WHOLE REFRESH DID NOT SHIP"
_REFUSALS = ("RefreshMergeApprovalError", "RefreshBaselineError", "OecdLiftPreconditionError")


def test_every_refusal_raise_site_in_source_carries_the_sentence():
    """Structural: a NEW refusal raised without REFRESH_DID_NOT_SHIP fails here."""
    src = Path(m.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            f = node.exc.func
            if isinstance(f, ast.Name) and f.id in _REFUSALS:
                sites.append((node.lineno, "REFRESH_DID_NOT_SHIP" in ast.get_source_segment(src, node)))
    assert len(sites) >= 10, sites  # 2 scoped + 4 approval + 4 baseline
    assert [ln for ln, ok in sites if not ok] == []


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                   env={**__import__("os").environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def _repo(tmp_path, committed):
    _git(tmp_path, "init", "-q")
    (tmp_path / "data").mkdir()
    (tmp_path / "x").write_text("x")
    if committed is not None:
        (tmp_path / "data" / "incidents.json").write_text(committed, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "c")
    return tmp_path


def _approval(tmp_path, doc):
    p = tmp_path / "a.json"
    p.write_text(doc if isinstance(doc, str) else json.dumps(doc), encoding="utf-8")
    return p


ENTRIES = [{"kind": "merge", "from": "INC-2", "into": "INC-1"}]


def _trigger_approval_unreadable(tmp_path, mp):
    m._load_refresh_merge_approvals(_approval(tmp_path, "{ not json"))


def _trigger_approval_unsigned(tmp_path, mp):
    m._load_refresh_merge_approvals(_approval(tmp_path, {"entries": ENTRIES}))


def _trigger_approval_hash_mismatch(tmp_path, mp):
    auth = {"decision": "DX", "ruled_by": "user", "entries_sha256": "0" * 64}
    m._load_refresh_merge_approvals(_approval(tmp_path, {"entries": ENTRIES, "authorization": auth}))


def _trigger_approval_not_pinned(tmp_path, mp):
    auth = {"decision": "DX", "ruled_by": "user", "entries_sha256": m._refresh_merge_entries_sha256(ENTRIES)}
    p = _approval(tmp_path, {"entries": ENTRIES, "authorization": auth})
    mp.setattr(m, "REFRESH_MERGE_APPROVAL_PATH", p)
    m._load_refresh_merge_approvals(p)


def _trigger_baseline_unparseable(tmp_path, mp):
    m._load_gate_baseline(_repo(tmp_path, "{ not json"))


def _trigger_baseline_shallow(tmp_path, mp):
    r = _repo(tmp_path, None)
    real = m._git

    def fake(root, *a):
        if a[:1] == ("rev-parse",):
            return subprocess.CompletedProcess(a, 0, stdout=b"true\n", stderr=b"")
        return real(root, *a)
    mp.setattr(m, "_git", fake)
    m._load_gate_baseline(r)


def _trigger_baseline_history_but_no_head(tmp_path, mp):
    r = _repo(tmp_path, json.dumps({"incidents": [{"id": "INC-1"}]}))
    (r / "data" / "incidents.json").unlink()
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "delete")
    m._load_gate_baseline(r)


def _trigger_baseline_no_git_missing(tmp_path, mp):
    mp.delenv("MERGE_ALLOW_FIRST_BUILD", raising=False)
    m._load_gate_baseline(tmp_path)


def _trigger_gate_merge(tmp_path, mp):
    new = [PREV[0] | {"source_ids": ["AIID-1", "AIID-2"]}]
    dep = [{"from": "INC-2", "into": "INC-1", "reason": "merged", "retired_source_ids": ["AIID-2"]}]
    m._check_refresh_merge_authorization(PREV, new, dep, approval_path=tmp_path / "none.json",
                                         pair_inputs_changed=False, aiid_class=True, aiid_titles={})


def _trigger_oecd_precondition(tmp_path, mp):
    m._check_oecd_lift_precondition(True)


TRIGGERS = [
    _trigger_approval_unreadable, _trigger_approval_unsigned, _trigger_approval_hash_mismatch,
    _trigger_approval_not_pinned, _trigger_baseline_unparseable, _trigger_baseline_shallow,
    _trigger_baseline_history_but_no_head, _trigger_baseline_no_git_missing,
    _trigger_gate_merge, _trigger_oecd_precondition,
]


@pytest.mark.parametrize("trigger", TRIGGERS, ids=lambda f: f.__name__)
def test_each_refusal_path_says_whole_refresh_did_not_ship(trigger, tmp_path, monkeypatch):
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        trigger(tmp_path, monkeypatch)
    msg = str(ei.value)
    assert SENTENCE in msg, f"{trigger.__name__}: {msg[:200]}"
    for src in ("AIAAIC", "CISA KEV", "CVE rejection sweep"):
        assert src in msg


@pytest.mark.parametrize("trigger", TRIGGERS, ids=lambda f: f.__name__)
def test_each_trigger_really_reaches_its_refusal_when_sentence_blanked(trigger, tmp_path, monkeypatch):
    """The trigger must reach a refusal (not some other error): with the sentence
    blanked it still raises, and the sentence is gone."""
    monkeypatch.setattr(m, "REFRESH_DID_NOT_SHIP", "")
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        trigger(tmp_path, monkeypatch)
    assert SENTENCE not in str(ei.value)
