"""D121 (user ruling 2026-10-13): fail-closed stays, as a LOUD abort. A gate
refusal must say the whole refresh did not ship, and why."""

from __future__ import annotations

import pytest

import merge_and_dedupe as m

@pytest.fixture(autouse=True)
def _refresh_mode(monkeypatch):
    """This file pins the REFRESH wording; the other mode is tested in test_d127_*."""
    monkeypatch.setenv(m.REFRESH_RUN_ENV, "1")


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
    monkeypatch.setattr(m, "abort_sentence", lambda: "")
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
                sites.append((node.lineno, "abort_sentence()" in ast.get_source_segment(src, node)))
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
    monkeypatch.setattr(m, "abort_sentence", lambda: "")
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        trigger(tmp_path, monkeypatch)
    assert SENTENCE not in str(ei.value)

# ---- D126 (user ruling 2026-10-13): EVERY abort in the build carries the sentence ----
# Every abort in merge_and_dedupe.py is reachable from main(), which is the
# refresh path (the weekly refresh runs this same script); each aborts the whole
# build before any output write, so the sentence is true for all of them and is
# carried unconditionally (no refresh-mode conditional to get wrong).
_EXIT_CALLS = {"exit", "quit", "_exit", "abort"}  # sys.exit / exit / quit / os._exit / os.abort
# Explicit, justified allowlist of aborts exempt from the sentence, keyed by
# (enclosing function, "raise"|"assert"|exit-call name). EMPTY today: there is no
# non-refresh abort in the file. Adding an entry needs a written justification.
ABORT_ALLOWLIST: dict[tuple[str, str], str] = {}


def _has_sentence_name(node) -> bool:
    """True iff a CALL to abort_sentence() occurs under `node`. Comments,
    docstrings and string text are NOT nodes of that kind, so they never count; the
    bare REFRESH_DID_NOT_SHIP constant does not count either (D127: it is the
    refresh-only wording, so using it directly would lie in every other job)."""
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "abort_sentence"
               for n in ast.walk(node))


def _returns_of(fn):
    """Return statements of `fn` itself (not of functions nested inside it)."""
    out, stack = [], list(fn.body)
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Return):
            out.append(n)
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            stack.extend(ast.iter_child_nodes(n))
    return out


def _handler_converts(h: ast.ExceptHandler) -> bool:
    """A handler that can catch AssertionError (bare/Exception/BaseException/
    AssertionError) and converts it (contains a raise that is not a bare re-raise)."""
    t = h.type
    names = ([] if t is None else [e.id for e in t.elts if isinstance(e, ast.Name)] if isinstance(t, ast.Tuple)
             else [t.id] if isinstance(t, ast.Name) else [])
    catches = t is None or bool({"Exception", "BaseException", "AssertionError"} & set(names))
    raises = [n for s in h.body for n in ast.walk(s) if isinstance(n, ast.Raise)]
    return catches and any(r.exc is not None for r in raises) and not any(r.exc is None for r in raises)


def _abort_findings(src: str) -> list[str]:
    """Return a description of every abort in `src` that lacks the sentence.
    All matching is on AST nodes, never on source text."""
    tree = ast.parse(src)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}

    def enclosing_func(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return n.name
        return "<module>"

    # a helper is compliant only if it returns something and EVERY return carries the Name
    # (G3) ...and a NAME is a compliant helper only if EVERY def with that name is
    # compliant: a non-compliant nested def sharing the name must not borrow it.
    defs: dict[str, list[bool]] = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rets = [r for r in _returns_of(n) if r.value is not None]
            defs.setdefault(n.name, []).append(bool(rets) and all(_has_sentence_name(r.value) for r in rets))
    helpers = {name for name, oks in defs.items() if all(oks)}

    def guarded(node) -> bool:
        child, p = node, parents.get(node)
        while p is not None:
            if isinstance(p, ast.Try) and child in p.body and any(_handler_converts(h) for h in p.handlers):
                return True
            child, p = p, parents.get(p)
        return False

    bad = []
    for node in ast.walk(tree):
        seg = ast.get_source_segment(src, node) or ""
        where = f"line {getattr(node, 'lineno', '?')} in {enclosing_func(node)}"
        if isinstance(node, ast.Raise):
            if (enclosing_func(node), "raise") in ABORT_ALLOWLIST:
                continue
            exc = node.exc
            # a bare `raise`, `raise err`, `raise SomeName` fail by design
            ok = (isinstance(exc, ast.Call)
                  and (_has_sentence_name(exc)
                       or (isinstance(exc.func, ast.Name) and exc.func.id in helpers)))
            if not ok:
                bad.append(f"raise without sentence: {where}: {seg[:60]!r}")
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if (name in _EXIT_CALLS and not _has_sentence_name(node)
                    and (enclosing_func(node), name) not in ABORT_ALLOWLIST):
                bad.append(f"exit call without sentence: {where}: {seg[:60]!r}")
        elif isinstance(node, ast.Assert):
            # only legal inside a try BODY whose handler catches AssertionError and converts it
            if not guarded(node) and (enclosing_func(node), "assert") not in ABORT_ALLOWLIST:
                bad.append(f"unguarded assert: {where}")
    return bad


def test_every_abort_in_the_file_carries_the_sentence():
    src = Path(m.__file__).read_text(encoding="utf-8")
    assert _abort_findings(src) == []


@pytest.mark.parametrize("snippet,expect", [
    ('def f():\n    raise SystemExit("x")\n', "raise without sentence"),
    ('def f():\n    raise SomeNewError("x")\n', "raise without sentence"),
    ('def f():\n    err = RuntimeError("x")\n    raise err\n', "raise without sentence"),
    ('def f():\n    try:\n        pass\n    except Exception:\n        raise\n', "raise without sentence"),
    ('import sys\ndef f():\n    sys.exit("x")\n', "exit call without sentence"),
    ('def f():\n    assert 1 == 2\n', "unguarded assert"),
    ('REFRESH_DID_NOT_SHIP = "x"\ndef f():\n    raise SystemExit("x " + REFRESH_DID_NOT_SHIP)\n', "raise without sentence"),
])
def test_the_abort_scanner_fires_on_a_new_abort_without_the_sentence(snippet, expect):
    """Mutation proof: the scanner flags each new un-sentenced abort shape."""
    assert any(expect in b for b in _abort_findings(snippet))


def test_the_abort_scanner_accepts_a_sentenced_abort_and_a_guarded_assert():
    ok = ('def f():\n    raise SomeNewError("x " + abort_sentence())\n'
          'def g():\n    try:\n        assert 1\n    except Exception:\n        raise SystemExit(abort_sentence())\n')
    assert _abort_findings(ok) == []


def _ruled(tmp_path, body):
    p = tmp_path / "ruled.json"
    p.write_text(body if isinstance(body, str) else json.dumps(body), encoding="utf-8")
    return p


def _trigger_ruled_unreadable(tmp_path, mp):
    m._load_ruled_deprecation_appends(_ruled(tmp_path, "{ not json"))


def _trigger_ruled_bad_entry(tmp_path, mp):
    m._load_ruled_deprecation_appends(_ruled(tmp_path, {"entries": [{"record": {"from": "INC-1"}}]}))


def _trigger_ruled_not_object(tmp_path, mp):
    m._load_ruled_deprecation_appends(_ruled(tmp_path, "[1, 2]"))


def _trigger_split_unauthorized(tmp_path, mp):
    m._check_split_authorization({"k1": "INC-1", "k2": "INC-1"},
                                 [{"id": "INC-1", "source_ids": ["k1"]}, {"id": "INC-9", "source_ids": ["k2"]}],
                                 tmp_path / "none.json")


def _trigger_legacy_missing(tmp_path, mp):
    mp.setattr(m, "DATA", tmp_path)
    mp.setattr(m, "_load_prev_state", lambda: ({}, {}, 1))
    mp.delenv("MERGE_ALLOW_MISSING_LEGACY", raising=False)
    m.main()


def _signed(entries):
    return {"entries": entries, "authorization": {
        "decision": "DX", "ruled_by": "user", "entries_sha256": m._refresh_merge_entries_sha256(entries)}}


def _malformed(entries):
    def trig(tmp_path, mp):
        m._load_refresh_merge_approvals(_approval(tmp_path, _signed(entries)))
    return trig


_MALFORMED = {
    "missing_from": [{"kind": "merge", "into": "INC-1"}],
    "missing_into": [{"kind": "merge", "from": "INC-2"}],
    "retitle_no_id": [{"kind": "retitle"}],
    "add_no_source_id": [{"kind": "add"}],
    "content_no_id": [{"kind": "content"}],
    "non_dict_entry": ["INC-1"],
    "null_entry": [None],
    "wrong_type_value": [{"kind": "merge", "from": ["INC-2"], "into": "INC-1"}],
}

D126_TRIGGERS = [
    pytest.param(f, id=f.__name__) for f in (
        _trigger_ruled_unreadable, _trigger_ruled_bad_entry, _trigger_ruled_not_object,
        _trigger_split_unauthorized, _trigger_legacy_missing)
] + [pytest.param(_malformed(v), id=f"malformed_{k}") for k, v in _MALFORMED.items()]


@pytest.mark.parametrize("trigger", D126_TRIGGERS)
def test_d126_each_newly_covered_abort_says_whole_refresh_did_not_ship(trigger, tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as ei:
        trigger(tmp_path, monkeypatch)
    msg = str(ei.value)
    assert SENTENCE in msg, msg[:200]
    for src in ("AIAAIC", "CISA KEV", "CVE rejection sweep"):
        assert src in msg


@pytest.mark.parametrize("trigger", D126_TRIGGERS)
def test_d126_triggers_reach_the_abort_when_sentence_blanked(trigger, tmp_path, monkeypatch):
    monkeypatch.setattr(m, "abort_sentence", lambda: "")
    with pytest.raises(SystemExit) as ei:
        trigger(tmp_path, monkeypatch)
    assert SENTENCE not in str(ei.value)


@pytest.mark.parametrize("k", list(_MALFORMED))
def test_malformed_signed_entry_is_a_refusal_not_a_raw_exception(k, tmp_path):
    with pytest.raises(m.RefreshMergeApprovalError):
        _malformed(_MALFORMED[k])(tmp_path, None)


def test_wellformed_approvals_and_unknown_kinds_unchanged(tmp_path):
    ents = [{"kind": "merge", "from": "A", "into": "B"}, {"kind": "retitle", "id": "C"},
            {"kind": "add", "source_id": "S"}, {"kind": "content", "id": "D"},
            {"kind": "future-kind", "x": 1}]
    got = m._load_refresh_merge_approvals(_approval(tmp_path, _signed(ents)))
    assert got == {("merge", "A", "B"), ("retitle", "C"), ("add", "S"), ("content", "D")}


_PROBES = {
    "helper_docstring_mentions_sentence": (
        'def _r(why):\n    """Plain refusal; NOT the abort_sentence() wording."""\n    return SystemExit(why)\n'
        'def f():\n    raise _r("x")\n', "raise without sentence"),
    "helper_dead_branch": (
        'def _r(why):\n    if False:\n        return SystemExit(abort_sentence())\n    return SystemExit(why)\n'
        'def f():\n    raise _r("x")\n', "raise without sentence"),
    "raise_main_call": (
        'def main():\n    raise SystemExit(abort_sentence())\ndef f():\n    raise main()\n', "raise without sentence"),
    "assert_wrong_handler": (
        'def f(d):\n    try:\n        assert d, "no"\n    except KeyError:\n        pass\n', "unguarded assert"),
    "assert_in_handler": (
        'def f(d):\n    try:\n        pass\n    except Exception:\n        assert d\n'
        '        raise SystemExit(abort_sentence())\n', "unguarded assert"),
    "assert_handler_plain_reraises": (
        'def f(d):\n    try:\n        assert d\n    except Exception:\n        raise\n', "unguarded assert"),
    "comment_inside_raise": (
        'def f():\n    raise SystemExit(\n        "x"  # REFRESH_DID_NOT_SHIP\n    )\n', "raise without sentence"),
    "same_name_noncompliant_nested_helper": (
        'def _r(why):\n    return SystemExit(why + abort_sentence())\n'
        'def outer():\n    def _r(why):\n        return SystemExit(why)\n    raise _r("x")\n',
        "raise without sentence"),
    "os_abort": ('import os\ndef f():\n    os.abort()\n', "exit call without sentence"),
}


@pytest.mark.parametrize("name", list(_PROBES))
def test_the_abort_scanner_flags_each_gate_probe(name):
    snippet, expect = _PROBES[name]
    assert any(expect in b for b in _abort_findings(snippet)), name


def test_a_compliant_helper_and_a_converting_assert_are_accepted():
    ok = ('def _r(why):\n    return SystemExit(why + abort_sentence())\n'
          'def f():\n    raise _r("x")\n'
          'def g(d):\n    try:\n        assert d\n    except AssertionError:\n'
          '        raise SystemExit("y" + abort_sentence())\n')
    assert _abort_findings(ok) == []
