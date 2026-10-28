"""D127 (user ruling 2026-10-13): a catch-all around main() and job-aware abort
wording. The weekly refresh (auto-refresh.yml sets GENAI_REFRESH_RUN=1) keeps the
full D121 sentence; every other job says the build was refused and nothing was
written, and must not claim a refresh (or AIAAIC / KEV / the CVE sweep) did not ship."""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import merge_and_dedupe as m

REPO = Path(__file__).resolve().parents[1]
FLAG = "GENAI_REFRESH_RUN"
FULL = "THE WHOLE REFRESH DID NOT SHIP"
NON = "Build refused; nothing was written."
REFRESH_ONLY = ("AIAAIC", "CISA KEV", "CVE rejection sweep", FULL)


def _env(monkeypatch, refresh: bool):
    if refresh:
        monkeypatch.setenv(FLAG, "1")
    else:
        monkeypatch.delenv(FLAG, raising=False)


# ---- abort_sentence(): the mode switch ------------------------------------
def test_sentence_by_mode(monkeypatch):
    _env(monkeypatch, True)
    assert m.abort_sentence() == m.REFRESH_DID_NOT_SHIP and FULL in m.abort_sentence()
    _env(monkeypatch, False)
    assert m.abort_sentence() == m.NON_REFRESH_REFUSED and NON in m.abort_sentence()
    monkeypatch.setenv(FLAG, "0")  # only an explicit "1" is refresh mode
    assert m.abort_sentence() == m.NON_REFRESH_REFUSED


def test_non_refresh_wording_makes_no_refresh_claim():
    for word in REFRESH_ONLY:
        assert word not in m.NON_REFRESH_REFUSED


@pytest.mark.parametrize("refresh", [True, False])
def test_explicit_refusal_wording_follows_the_flag(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    msg = str(ei.value)
    if refresh:
        assert FULL in msg and "AIAAIC" in msg
    else:
        assert NON in msg and not any(w in msg for w in ("AIAAIC", "CISA KEV", "CVE rejection sweep", FULL))
        assert "OECD" in msg  # the refusal's own cause is still there


# ---- _run_main(): the catch-all (in-process) ------------------------------
def _run_with(monkeypatch, exc_or_none):
    def fake():
        if exc_or_none is not None:
            raise exc_or_none
    monkeypatch.setattr(m, "main", fake)
    return m._run_main()


@pytest.mark.parametrize("refresh", [True, False])
def test_unexpected_exception_exits_with_the_job_sentence(refresh, monkeypatch, capsys):
    _env(monkeypatch, refresh)
    for exc in (KeyError("zzz"), ValueError("boom"), json.JSONDecodeError("bad", "x", 0)):
        with pytest.raises(SystemExit) as ei:
            _run_with(monkeypatch, exc)
        msg = str(ei.value.code)
        assert type(exc).__name__ in msg  # diagnostic kept
        assert msg.count(m.abort_sentence()) == 1
        assert (FULL in msg) is refresh
        assert "Traceback" in capsys.readouterr().err  # traceback not swallowed


@pytest.mark.parametrize("refresh", [True, False])
def test_systemexit_str_and_nonzero_int_get_the_sentence(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    with pytest.raises(SystemExit) as ei:
        _run_with(monkeypatch, SystemExit("plain refusal text"))
    assert "plain refusal text" in ei.value.code and m.abort_sentence() in ei.value.code
    with pytest.raises(SystemExit) as ei:
        _run_with(monkeypatch, SystemExit(3))
    assert ei.value.code not in (0, None) and m.abort_sentence() in str(ei.value.code)


@pytest.mark.parametrize("refresh", [True, False])
def test_systemexit_already_carrying_the_sentence_is_not_doubled(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    text = "cause. " + m.abort_sentence()
    with pytest.raises(SystemExit) as ei:
        _run_with(monkeypatch, SystemExit(text))
    assert ei.value.code == text


@pytest.mark.parametrize("exc", [None, SystemExit(0), SystemExit(None)])
def test_success_is_unchanged(exc, monkeypatch, capsys):
    _env(monkeypatch, True)
    assert _run_with(monkeypatch, exc) is None
    assert capsys.readouterr().err == ""


# ---- end to end: run the script as a subprocess in both modes -------------
@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    """A tiny scratch copy of scripts/ + ingest/*.py with an empty data/ dir (the
    script resolves ROOT from its own path), so nothing in the repo can change."""
    root = tmp_path_factory.mktemp("d127_tree")
    shutil.copytree(REPO / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "ingest").mkdir()
    for f in (REPO / "ingest").glob("*.py"):
        shutil.copy(f, root / "ingest" / f.name)
    (root / "data").mkdir()
    shutil.copy(REPO / "data" / "last_release.json", root / "data" / "last_release.json")  # D132
    return root


def _run(root, refresh: bool):
    env = {k: v for k, v in os.environ.items() if k not in (FLAG, "MERGE_ALLOW_MISSING_LEGACY")}
    env["PYTHONIOENCODING"] = "utf-8"
    if refresh:
        env[FLAG] = "1"
    return subprocess.run([sys.executable, str(root / "scripts" / "merge_and_dedupe.py")], cwd=root, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)


@pytest.mark.parametrize("refresh", [True, False])
def test_e2e_explicit_refusal(tree, refresh):
    (tree / "data" / "legacy_consolidated.json").unlink(missing_ok=True)
    r = _run(tree, refresh)
    assert r.returncode != 0
    assert "legacy_consolidated.json not found" in r.stderr  # original text kept
    assert (FULL in r.stderr) is refresh and (NON in r.stderr) is (not refresh)
    assert r.stderr.count(m.REFRESH_DID_NOT_SHIP if refresh else NON) == 1
    assert not (tree / "data" / "incidents.json").exists()


@pytest.mark.parametrize("refresh", [True, False])
def test_e2e_unexpected_exception(tree, refresh):
    bad = tree / "data" / "legacy_consolidated.json"
    bad.write_text("{ not json", encoding="utf-8")
    try:
        r = _run(tree, refresh)
    finally:
        bad.unlink()
    assert r.returncode != 0
    assert "Traceback" in r.stderr and "JSONDecodeError" in r.stderr  # diagnostic kept
    assert (FULL in r.stderr) is refresh and (NON in r.stderr) is (not refresh)
    assert not (tree / "data" / "incidents.json").exists()


# ---- the flag lives on the weekly refresh's merge step and nowhere else ----
WF = REPO / ".github" / "workflows"


def _merge_steps(doc):
    for jname, job in (doc.get("jobs") or {}).items():
        for step in job.get("steps") or []:
            if "merge_and_dedupe.py" in str(step.get("run", "")):
                yield jname, step


def _flag_anywhere(node) -> bool:
    """True iff the flag is a KEY anywhere in the parsed workflow (comments are not
    parsed, so prose mentioning it never counts)."""
    if isinstance(node, dict):
        return any((k == FLAG) or _flag_anywhere(v) for k, v in node.items())
    if isinstance(node, list):
        return any(_flag_anywhere(v) for v in node)
    return False


def check_flag_placement(name: str, text: str) -> list[str]:
    doc = yaml.safe_load(text)
    problems = []
    if name == "auto-refresh.yml":
        steps = list(_merge_steps(doc))
        if not steps:
            problems.append("auto-refresh has no merge_and_dedupe step")
        for jn, st in steps:
            if str((st.get("env") or {}).get(FLAG)) != "1":
                problems.append(f"{jn}: merge step lacks env {FLAG}=1")
        if FLAG in (doc.get("env") or {}):
            problems.append("flag set at workflow level")
        for jn, job in doc["jobs"].items():
            if FLAG in (job.get("env") or {}):
                problems.append(f"{jn}: flag set at job level")
            for st in job.get("steps") or []:
                if FLAG in (st.get("env") or {}) and "merge_and_dedupe.py" not in str(st.get("run", "")):
                    problems.append(f"{jn}: flag on a non-merge step {st.get('name')}")
    elif _flag_anywhere(doc):
        problems.append(f"{name} must not set {FLAG}")
    return problems


def test_workflow_flag_placement():
    for f in sorted(WF.glob("*.yml")):
        assert check_flag_placement(f.name, f.read_text(encoding="utf-8")) == [], f.name
    for needed in ("validate.yml", "cve-enrich.yml", "atlas-refresh.yml"):
        assert "merge_and_dedupe.py" in (WF / needed).read_text(encoding="utf-8")  # the guard covers real users


def test_flag_check_fires_on_removal_and_on_other_workflows():
    auto = (WF / "auto-refresh.yml").read_text(encoding="utf-8")
    removed = auto.replace(FLAG + ': "1"', 'X: "1"')
    assert removed != auto
    assert any("lacks env" in p for p in check_flag_placement("auto-refresh.yml", removed))
    inject = "\nenv:\n  " + FLAG + ': "1"\njobs:'
    for other in ("validate.yml", "cve-enrich.yml", "atlas-refresh.yml"):
        t = (WF / other).read_text(encoding="utf-8")
        injected = t.replace("\njobs:", inject, 1)
        assert injected != t
        assert check_flag_placement(other, injected), other
    wide = auto.replace("\njobs:", inject, 1)
    assert wide != auto
    assert any("workflow level" in p for p in check_flag_placement("auto-refresh.yml", wide))


# ---- G5: the "before any output write" claim, checked ---------------------
_WRITE_ATTRS = {"write_text", "write_bytes", "write", "dump", "replace", "rename"}
_EXITS = {"exit", "quit", "_exit", "abort"}


def _abort_capable(tree) -> set[str]:
    """Names of module functions that contain an abort, directly or via a call to
    another such function (bare-name call graph, transitive)."""
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    direct = set()
    for name, fn in funcs.items():
        for n in ast.walk(fn):
            if (isinstance(n, ast.Raise) and n.exc is not None) or isinstance(n, ast.Assert):
                direct.add(name)
            elif isinstance(n, ast.Call):
                f = n.func
                if (f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")) in _EXITS:
                    direct.add(name)
    capable = set(direct)
    changed = True
    while changed:
        changed = False
        for name, fn in funcs.items():
            if name not in capable and any(
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in capable
                    for n in ast.walk(fn)):
                capable.add(name)
                changed = True
    return capable


def abort_after_write(src: str, entry: str = "main") -> list[str]:
    """Abort sites in `entry` (a direct raise/assert, or a call to an abort-capable
    function) located AFTER its first output write. An output write is a
    .write_text/.write_bytes/.write/.dump/.replace/.rename call or open(.., 'w')."""
    tree = ast.parse(src)
    capable = _abort_capable(tree)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == entry)
    writes, aborts = [], []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in _WRITE_ATTRS:
                writes.append(n.lineno)
            elif isinstance(f, ast.Name) and f.id == "open" and any(
                    isinstance(a, ast.Constant) and isinstance(a.value, str) and set(a.value) & set("wax+")
                    for a in n.args[1:2] + [k.value for k in n.keywords if k.arg == "mode"]):
                writes.append(n.lineno)
            elif isinstance(f, ast.Name) and f.id == "_write_output":
                writes.append(n.lineno)
            elif isinstance(f, ast.Name) and f.id in capable and f.id != entry:
                aborts.append((n.lineno, f"call to abort-capable {f.id}()"))
            if (f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")) in _EXITS:
                aborts.append((n.lineno, "direct exit call"))
        elif (isinstance(n, ast.Raise) and n.exc is not None) or isinstance(n, ast.Assert):
            aborts.append((n.lineno, "direct raise/assert"))
    if not writes:
        return ["no output write found in " + entry]  # the claim would be untested
    first = min(writes)
    return [f"line {ln}: {what} after first write at line {first}" for ln, what in aborts if ln > first]


def test_every_abort_is_ordered_before_the_first_output_write():
    src = Path(m.__file__).read_text(encoding="utf-8")
    assert abort_after_write(src) == []


_G5_PROBES = {
    "call_after_write": (
        'def _check():\n    raise SystemExit("x")\n'
        'def main():\n    P.write_text("a")\n    _check()\n'),
    "direct_raise_after_write": (
        'def main():\n    P.write_text("a")\n    raise SystemExit("x")\n'),
    "transitive_after_write": (
        'def _inner():\n    raise SystemExit("x")\ndef _outer():\n    _inner()\n'
        'def main():\n    json.dump(1, f)\n    _outer()\n'),
    "sys_exit_after_write": (
        'def main():\n    P.write_text("a")\n    sys.exit(2)\n'),
    "write_output_then_exit": (
        'def main():\n    _write_output(P, "a")\n    quit()\n'),
    "assert_after_open_w": (
        'def main():\n    open("p", "w")\n    assert 1\n'),
}


@pytest.mark.parametrize("name", list(_G5_PROBES))
def test_the_write_ordering_check_fires(name):
    assert any("after first write" in b for b in abort_after_write(_G5_PROBES[name])), name


def test_the_write_ordering_check_accepts_abort_before_write():
    ok = 'def _check():\n    raise SystemExit("x")\ndef main():\n    _check()\n    P.write_text("a")\n'
    assert abort_after_write(ok) == []


# ---- D128 (user ruling): a stop after any write names what was written ----
@pytest.fixture(autouse=True)
def _fresh_written(monkeypatch):
    monkeypatch.setattr(m, "_WRITTEN", [])


PATHS = ["data/incidents.json", "data/incidents.min.json"]


@pytest.mark.parametrize("refresh", [True, False])
def test_catch_all_also_catches_a_non_exception_baseexception(refresh, monkeypatch):
    """KeyboardInterrupt is a BaseException, not an Exception: `except Exception`
    would let it escape the sentence."""
    _env(monkeypatch, refresh)
    try:
        with pytest.raises(SystemExit) as ei:
            _run_with(monkeypatch, KeyboardInterrupt())
    except KeyboardInterrupt:
        pytest.fail("KeyboardInterrupt escaped the catch-all")
    assert "KeyboardInterrupt" in str(ei.value.code) and m.abort_sentence() in str(ei.value.code)


@pytest.mark.parametrize("refresh", [True, False])
def test_sentence_before_any_write_is_the_d127_wording(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    assert m.abort_sentence() == (m.REFRESH_DID_NOT_SHIP if refresh else m.NON_REFRESH_REFUSED)


@pytest.mark.parametrize("refresh", [True, False])
def test_sentence_after_a_write_names_files_and_restore_hint(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    monkeypatch.setattr(m, "_WRITTEN", list(PATHS))
    msg = m.abort_sentence()
    assert "nothing was written" not in msg.lower() and "nothing from this run was written" not in msg
    assert all(p in msg for p in PATHS)
    assert "git checkout -- " + " ".join(PATHS) in msg
    if refresh:
        assert FULL in msg and "nothing from this run was published" in msg and "AIAAIC" in msg
    else:
        assert "PARTIALLY written" in msg
        assert not any(w in msg for w in ("AIAAIC", "CISA KEV", "CVE rejection sweep", FULL))


@pytest.mark.parametrize("refresh", [True, False])
def test_explicit_refusal_and_catch_all_use_the_write_aware_sentence(refresh, monkeypatch):
    _env(monkeypatch, refresh)
    monkeypatch.setattr(m, "_WRITTEN", ["data/incidents.json"])
    with pytest.raises(m.OecdLiftPreconditionError) as ei:
        m._check_oecd_lift_precondition(True)
    assert "data/incidents.json" in str(ei.value) and "nothing was written" not in str(ei.value).lower()
    with pytest.raises(SystemExit) as ei:
        _run_with(monkeypatch, KeyError("k"))
    assert "data/incidents.json" in str(ei.value.code) and "nothing was written" not in str(ei.value.code).lower()


def test_write_output_records_before_it_writes(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "ROOT", tmp_path)
    target = tmp_path / "d"
    target.mkdir()
    with pytest.raises(OSError):
        m._write_output(target, "x")  # a directory: the write itself fails
    assert m._WRITTEN == ["d"]  # ...and it is still listed (a failed write can leave a partial file)
    m._write_output(tmp_path / "f.json", "x")
    m._write_output(tmp_path / "f.json", "y")
    assert m._WRITTEN == ["d", "f.json"]  # no duplicates
    assert (tmp_path / "f.json").read_text() == "y"


def raw_writes_in_main(src: str) -> tuple[list[int], int]:
    """(line numbers of raw write calls in main(), count of _write_output calls)."""
    main = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "main")
    raw, tracked = [], 0
    for n in ast.walk(main):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in {"write_text", "write_bytes", "write", "dump"}:
                raw.append(n.lineno)
            if isinstance(f, ast.Name) and f.id == "open":
                raw.append(n.lineno)
            if isinstance(f, ast.Name) and f.id == "_write_output":
                tracked += 1
    return raw, tracked


def test_main_writes_only_through_write_output():
    """Make it impossible to add an untracked write: main() contains no raw write
    call, and every output goes through _write_output, which records first."""
    src = Path(m.__file__).read_text(encoding="utf-8")
    raw, tracked = raw_writes_in_main(src)
    assert raw == []
    assert tracked >= 3  # id_deprecations.json, incidents.json, incidents.min.json
    wo = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == "_write_output")
    appends = [n.lineno for n in ast.walk(wo) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Attribute) and n.func.attr == "append"]
    writes = [n.lineno for n in ast.walk(wo) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Attribute) and n.func.attr == "write_text"]
    assert appends and writes and max(appends) < min(writes)  # recorded BEFORE the write


@pytest.mark.parametrize("snippet", [
    'def main():\n    P.write_text("a")\n',
    'def main():\n    json.dump(1, f)\n',
    'def main():\n    open("p", "w")\n',
])
def test_raw_write_probe_is_detected(snippet):
    assert raw_writes_in_main(snippet)[0] != []


@pytest.fixture(scope="module")
def full_tree(tmp_path_factory):
    """A scratch repo built from the COMMITTED tree (git archive HEAD) with this
    working tree's scripts/ copied over it, a baseline commit, and legacy rebuilt --
    so merge_and_dedupe.py runs a real build. data/incidents.min.json is then
    replaced by a DIRECTORY so the third output write fails (the gate's repro)."""
    root = tmp_path_factory.mktemp("d128_full")
    specs = ["scripts", "data", "ingest", "mappings", "schema", "legacy",
             "docs/audits/WS4-T19-authorized-splits-2026-09-18.json",
             "docs/audits/ID-silent-ids-appends-2026-10-09.json",
             "docs/audits/ID-group-ids-appends-2026-10-10.json"]
    import io
    import tarfile
    present = [sp for sp in specs if subprocess.run(["git", "ls-tree", "--name-only", "HEAD", "--", sp],
                                                    cwd=REPO, capture_output=True).stdout.strip()]
    tar = subprocess.run(["git", "archive", "--format=tar", "HEAD", "--", *present], cwd=REPO,
                         check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        tf.extractall(root, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    shutil.rmtree(root / "scripts")
    shutil.copytree(REPO / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "data").mkdir(exist_ok=True)
    shutil.copy(REPO / "data" / "last_release.json", root / "data" / "last_release.json")  # D132
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(root / "scripts" / "parse_existing.py")], cwd=root, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr[-500:]
    for args in (("init", "-q"), ("add", "-A"),
                 ("-c", "user.email=t@e.x", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                  "commit", "-q", "-m", "baseline")):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / "data" / "incidents.min.json").unlink()
    (root / "data" / "incidents.min.json").mkdir()
    return root


@pytest.mark.parametrize("refresh", [True, False])
def test_e2e_stop_after_writes_lists_the_files(full_tree, refresh):
    r = _run(full_tree, refresh)
    err = r.stderr
    assert r.returncode != 0
    assert "wrote data/incidents.json" in r.stdout  # the premise: writes really happened first
    assert "PermissionError" in err or "IsADirectoryError" in err  # original diagnostic kept
    assert "data/incidents.json" in err and "data/incidents.min.json" in err
    assert "git checkout -- " in err
    assert "nothing was written" not in err.lower() and "nothing from this run was written" not in err
    if refresh:
        assert FULL in err and "nothing from this run was published" in err
    else:
        assert "PARTIALLY written" in err and FULL not in err


def test_no_hardcoded_nothing_was_written_claim_outside_the_sentence_helpers():
    """A literal 'nothing was written' at an abort site would be false after a write."""
    tree = ast.parse(Path(m.__file__).read_text(encoding="utf-8"))
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    bad = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "nothing was written" in n.value.lower():
            p = n
            owner = None
            while p in parents:
                p = parents[p]
                if isinstance(p, ast.FunctionDef):
                    owner = p.name
                    break
                if isinstance(p, ast.Assign) and isinstance(p.targets[0], ast.Name):
                    owner = p.targets[0].id
                    break
            if owner not in {"NON_REFRESH_REFUSED", "_nothing_written", "abort_sentence"}:
                bad.append((n.lineno, owner))
    assert bad == []


def test_main_starts_a_run_with_nothing_written(tmp_path, monkeypatch):
    """_WRITTEN is module state: an earlier in-process main() must not make a later
    refusal claim files were written."""
    _env(monkeypatch, False)
    monkeypatch.setattr(m, "_WRITTEN", ["stale/from/an/earlier/run.json"])
    monkeypatch.setattr(m, "DATA", tmp_path)
    monkeypatch.setattr(m, "_load_prev_state", lambda: ({}, {}, 1))
    monkeypatch.delenv("MERGE_ALLOW_MISSING_LEGACY", raising=False)
    with pytest.raises(SystemExit) as ei:
        m.main()
    assert "stale/from" not in str(ei.value) and NON in str(ei.value)
