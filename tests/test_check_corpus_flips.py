"""D156a: per-entity undeclared corpus-flip check for the refresh PR.

Each test names the input that makes it fail (agreement 6). Hermetic: temp git
repos and synthetic files only; no network."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import aiid_change_report as rep
import check_corpus_flips as c

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "auto-refresh.yml"
TOOL = ROOT / "scripts" / "check_corpus_flips.py"


def _e(iid, sids, corpus="ai-harm"):
    return {"id": iid, "source_ids": sids, "title": f"T {iid}", "corpus": corpus}


BEFORE = {"incidents": [
    _e("INC-1", ["AIID-1"]), _e("INC-2", ["AIID-2"]), _e("INC-3", ["AIAAIC-3"]),
    _e("INC-4", ["OECD-AIM-2026-01-01-aaaa"]), _e("INC-9", ["AIID-9"]),
]}


def _after(**flips):
    rows = [dict(e) for e in BEFORE["incidents"] if e["id"] != "INC-9"]  # INC-9 removed
    for r in rows:
        if r["id"] in flips:
            r["corpus"] = flips[r["id"]]
    rows.append(_e("INC-10", ["AIID-10"], "security"))  # added
    return {"incidents": rows}


def _declared(before, after):
    return {r["id"]: (r["before"], r["after"]) for r in rep.diff(before, after)["listed"]["corpus"]}


def test_undeclared_flip_is_reported():
    a = _after(**{"INC-1": "security"})
    r = c.compare(BEFORE, a, {})
    assert [f["id"] for f in r["undeclared"]] == ["INC-1"]
    assert "INC-1 | ai-harm | security | AIID-1" in c.render_md(r, "main")


def test_declared_flip_is_still_flagged_d158():
    a = _after(**{"INC-1": "security"})
    r = c.compare(BEFORE, a, _declared(BEFORE, a))
    assert len(r["flips"]) == 1 and r["undeclared"] == []
    md = c.render_md(r, "main")
    assert "INC-1 | ai-harm | security | AIID-1 | declared |" in md and "0 UNDECLARED, 1 declared" in md
    assert "needs-ruling" in md


def test_zero_flips_renders_a_one_liner_without_needs_ruling_text():
    md = c.render_md(c.compare(BEFORE, BEFORE, {}), "main")
    assert md.startswith("Corpus flips: 0") and "needs-ruling" not in md


def test_undeclared_rows_are_marked_and_listed_before_declared():
    a = _after(**{"INC-1": "security", "INC-3": "security"})
    md = c.render_md(c.compare(BEFORE, a, _declared(BEFORE, a)), "main")
    assert "| INC-3 | ai-harm | security | AIAAIC-3 | **UNDECLARED** |" in md
    assert md.index("INC-3 |") < md.index("INC-1 |")


@pytest.mark.parametrize("iid", ["INC-3", "INC-4"])
def test_flip_on_a_non_aiid_row_is_undeclared(iid):
    a = _after(**{iid: "security"})
    declared = _declared(BEFORE, a)  # D120 itself never lists a non-AIID row
    assert declared == {}
    assert [f["id"] for f in c.compare(BEFORE, a, declared)["undeclared"]] == [iid]


def test_declared_but_with_different_values_is_undeclared():
    a = _after(**{"INC-1": "security"})
    assert c.compare(BEFORE, a, {"INC-1": ("ai-harm", "other")})["undeclared"]


def test_added_and_removed_rows_are_not_flips_and_are_counted():
    r = c.compare(BEFORE, _after(), {})  # INC-10 added with a different corpus, INC-9 removed
    assert r["flips"] == [] and (r["added"], r["removed"]) == (1, 1)
    assert "added 1 / removed 1 are not flips" in c.render_md(r, "main")


def test_many_flips_render_bounded_and_full_list_is_uncapped():
    big = {"incidents": [_e(f"INC-{i}", ["AIAAIC-1"]) for i in range(c.MAX_ROWS + 30)]}
    after = {"incidents": [dict(e, corpus="security") for e in big["incidents"]]}
    r = c.compare(big, after, {})
    md = c.render_md(r, "main")
    assert f"**{c.MAX_ROWS + 30} existing row(s)" in md and "30 more flips" in md
    assert md.count("| INC-") == c.MAX_ROWS
    assert c.render_md(r, "main", None).count("| INC-") == c.MAX_ROWS + 30


def test_sidecar_is_uncapped():
    n = rep.MAX_ROWS_PER_FIELD + 50
    big = {"incidents": [_e(f"INC-{i}", [f"AIID-{i}"]) for i in range(n)]}
    after = {"incidents": [dict(e, corpus="security") for e in big["incidents"]]}
    sc = rep.sidecar(rep.diff(big, after))
    assert len(sc["listed"]["corpus"]) == n  # the markdown shows only MAX_ROWS_PER_FIELD
    assert len(c.load_declared_obj(sc)) == n


@pytest.mark.parametrize("content", [None, "", "not json", "[]", '{"schema":1}',
                                     '{"schema":2,"listed":{"corpus":[]}}',
                                     '{"schema":1,"listed":{"corpus":[{"id":"X"}]}}'])
def test_malformed_or_missing_sidecar_raises(tmp_path, content):
    p = tmp_path / "s.json"
    if content is not None:
        p.write_text(content, encoding="utf-8")
    with pytest.raises(c.CheckError):
        c.load_declared(str(p))


# ---- CLI end to end against a throwaway git repo ---------------------------------------------
def _run(tmp_path, head, after, sidecar_text):
    """Run the real CLI from a copy placed in a temp git repo (so ROOT is the temp repo)."""
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "scripts").mkdir(exist_ok=True)
    shutil.copy(TOOL, tmp_path / "scripts" / "check_corpus_flips.py")
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data" / "incidents.json").write_text(json.dumps(head), encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e")
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "x"]):
        subprocess.run(["git", *cmd], cwd=tmp_path, check=True, env=env, capture_output=True)
    af = tmp_path / "after.json"
    af.write_text(json.dumps(after), encoding="utf-8")
    sc = tmp_path / "side.json"
    if sidecar_text is not None:
        sc.write_text(sidecar_text, encoding="utf-8")
    return subprocess.run([sys.executable, str(tmp_path / "scripts" / "check_corpus_flips.py"), "--after", str(af),
                           "--declared-json", str(sc), "--out-md", str(tmp_path / "o.md")],
                          cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")


def test_cli_exit_codes(tmp_path):
    undeclared = _after(**{"INC-3": "security"})
    side = json.dumps(rep.sidecar(rep.diff(BEFORE, undeclared)))
    p = _run(tmp_path / "a", BEFORE, undeclared, side)
    assert p.returncode == 1  # flips found, undeclared
    assert "INC-3" in (tmp_path / "a" / "o.md").read_text(encoding="utf-8")
    declared = _after(**{"INC-1": "security"})
    p = _run(tmp_path / "b", BEFORE, declared, json.dumps(rep.sidecar(rep.diff(BEFORE, declared))))
    assert p.returncode == 1  # D158: a declared flip is still a flip
    p = _run(tmp_path / "z", BEFORE, _after(), json.dumps(rep.sidecar(rep.diff(BEFORE, _after()))))
    assert p.returncode == 0  # added/removed rows only: no flips
    p = _run(tmp_path / "c", BEFORE, undeclared, None)  # missing sidecar: the fail-soft path
    assert p.returncode == 2 and "ERROR" in p.stderr
    p = _run(tmp_path / "d", BEFORE, undeclared, "{broken")
    assert p.returncode == 2


def test_any_unexpected_exception_is_exit_2_not_1(tmp_path, monkeypatch):
    """A traceback exits 1, which would read as 'flips found'. main() must map ANY exception to 2."""
    sc = tmp_path / "s.json"
    sc.write_text(json.dumps({"schema": 1, "listed": {"corpus": []}}), encoding="utf-8")
    aft = tmp_path / "a.json"
    aft.write_text(json.dumps(BEFORE), encoding="utf-8")
    monkeypatch.setattr(c, "_git_show", lambda ref: BEFORE)
    assert c.main(["--declared-json", str(sc), "--after", str(aft)]) == 0

    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(c, "compare", boom)
    assert c.main(["--declared-json", str(sc), "--after", str(aft)]) == 2


def test_unwritable_output_path_is_exit_2(tmp_path):
    """Real subprocess, env-only injection: a directory sits where --out-md must be written."""
    undeclared = _after(**{"INC-3": "security"})
    (tmp_path / "o.md").mkdir()
    p = _run(tmp_path, BEFORE, undeclared, json.dumps(rep.sidecar(rep.diff(BEFORE, undeclared))))
    assert p.returncode == 2, p.stderr[-300:]


# ---- workflow wiring (text) -------------------------------------------------------------------
def check_wiring(text: str) -> list[str]:
    if "scripts/check_corpus_flips.py" not in text:
        return ["workflow never runs scripts/check_corpus_flips.py"]
    problems = []
    if "--out-json" not in text[text.index("scripts/aiid_change_report.py"):text.index("scripts/check_corpus_flips.py")]:
        problems.append("D120 report is not asked for its JSON sidecar")
    seg = text[text.index("scripts/check_corpus_flips.py"):]
    seg = seg[:seg.index("Ensure needs-ruling label exists")]
    if "|| flip_rc=$?" not in seg:
        problems.append("checker exit code is not captured with '|| flip_rc=$?' (a non-zero exit would abort under -e)")
    if seg.count('echo "needs_ruling=true" >> "$GITHUB_OUTPUT"') < 2:
        problems.append("flips (1) and could-not-run (2) paths must both set needs_ruling=true")
    if '[ -s "$RUNNER_TEMP/corpus-flips.md" ]' not in seg:
        problems.append("report-file existence is not guarded with -s")
    if "needs_ruling=false" in seg:
        problems.append("must never write needs_ruling=false (would clear an earlier flag)")
    if "::warning::" not in seg:
        problems.append("no ::warning:: annotation")
    if "exit 1" in seg:
        problems.append("aborts the refresh (flag, never block)")
    if re.search("(>>?|tee)[ ]*[^ ]*(data/|ingest/)", seg):
        problems.append("writes under data/ or ingest/")
    return problems


def test_workflow_wiring():
    assert check_wiring(WORKFLOW.read_text(encoding="utf-8")) == []


def test_wiring_check_fires():
    NL = chr(10)
    ANCHOR = '--out-full-md "$RUNNER_TEMP/corpus-flips-full.md" || flip_rc=$?' + NL
    t = WORKFLOW.read_text(encoding="utf-8")
    assert ANCHOR in t
    assert any("sidecar" in p for p in check_wiring(t.replace('--out-json "$RUNNER_TEMP/aiid-change-report.json"', "")))
    assert any("flip_rc" in p for p in check_wiring(t.replace(" || flip_rc=$?", "")))
    nr = 'echo "needs_ruling=true" >> "$GITHUB_OUTPUT"' + NL + '            echo "::warning::check_corpus_flips.py found'
    assert nr in t
    assert any("both set" in p for p in check_wiring(t.replace(nr, "true" + NL + '            echo "::warning::check_corpus_flips.py found')))
    assert any("-s" in p for p in check_wiring(t.replace('[ -s "$RUNNER_TEMP/corpus-flips.md" ]', "true")))
    assert any("false" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          needs_ruling=false" + NL)))
    assert any("aborts" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          exit 1" + NL)))
    assert any("writes under" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          echo x >> data/y" + NL)))


# ---- the workflow step itself, run under bash -eo pipefail with fake env ----------------------
BASH = shutil.which("bash")
UNKNOWN = "corpus-flip check could not be run"
STUB_MD = ('printf "### Corpus flips stub" > "$RUNNER_TEMP/corpus-flips.md"; '
           'printf "full" > "$RUNNER_TEMP/corpus-flips-full.md"; exit 1')


def _step_script(mutate=None) -> str:
    yaml = pytest.importorskip("yaml")
    text = WORKFLOW.read_text(encoding="utf-8")
    if mutate:
        text = mutate(text)
    w = yaml.safe_load(text)
    steps = [st for j in w["jobs"].values() for st in j["steps"] if "check_corpus_flips" in st.get("run", "")]
    assert len(steps) == 1
    return steps[0]["run"]


def _run_step(tmp_path, stub, mutate=None):
    """Run the real step block in the repo root (it only writes under RUNNER_TEMP). `stub` is shell that
    runs INSTEAD of `python ... check_corpus_flips.py` via a PATH wrapper; a stub that does not exit falls
    through to the real checker; None = no wrapper at all."""
    if not BASH:
        pytest.skip("bash not available")
    NL = chr(10)
    tmp_path.mkdir(parents=True)
    bindir, rt = tmp_path / "bin", tmp_path / "rt"
    bindir.mkdir()
    rt.mkdir()
    real = Path(sys.executable).as_posix()
    head = "#!/bin/bash" + NL
    if stub is not None:
        head += 'case "$*" in *check_corpus_flips.py*) ' + stub + " ;; esac" + NL
    (bindir / "python").write_text(head + 'exec "' + real + '" "$@"' + NL, encoding="utf-8", newline=NL)
    step = tmp_path / "step.sh"
    step.write_text(_step_script(mutate), encoding="utf-8", newline=NL)
    out, summ = tmp_path / "out", tmp_path / "summ"
    out.write_text("", encoding="utf-8")
    summ.write_text("", encoding="utf-8")
    env = dict(os.environ, RUNNER_TEMP=rt.as_posix(), GITHUB_OUTPUT=out.as_posix(),
               GITHUB_STEP_SUMMARY=summ.as_posix(), PATH=bindir.as_posix() + os.pathsep + os.environ["PATH"])
    p = subprocess.run([BASH, "--noprofile", "--norc", "-eo", "pipefail", step.as_posix()], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    lines = [x for x in out.read_text(encoding="utf-8").splitlines() if x.startswith("needs_ruling=")]
    body = (rt / "pr-body.md").read_text(encoding="utf-8") if (rt / "pr-body.md").exists() else ""
    return p, lines, body, summ.read_text(encoding="utf-8")


def _flags_unknown(p, lines, body):
    return p.returncode == 0 and bool(lines) and lines[-1] == "needs_ruling=true" and UNKNOWN in body


@pytest.mark.parametrize("stub", ["exit 1", "exit 7", "exit 2"])
def test_step_checker_failure_without_a_report_flags_unknown(tmp_path, stub):
    p, lines, body, _ = _run_step(tmp_path / "r", stub)
    assert _flags_unknown(p, lines, body), (p.returncode, lines, p.stderr[-300:])


def test_step_real_checker_crash_via_unwritable_report_flags_unknown(tmp_path):
    """The gate's env-only injection: a directory sits where the REAL checker must write its report."""
    p, lines, body, _ = _run_step(tmp_path / "r", 'mkdir "$RUNNER_TEMP/corpus-flips.md"')
    assert _flags_unknown(p, lines, body), (p.returncode, lines, p.stderr[-300:])


def test_step_flips_found_flags_needs_ruling_and_appends_body(tmp_path):
    p, lines, body, summ = _run_step(tmp_path / "r", STUB_MD)
    assert p.returncode == 0 and lines[-1] == "needs_ruling=true"
    assert "### Corpus flips stub" in body and "full" in summ and UNKNOWN not in body


def test_step_no_flips_adds_a_note_and_no_needs_ruling_of_its_own(tmp_path):
    stub = 'printf "Corpus flips: 0 (stub)." > "$RUNNER_TEMP/corpus-flips.md"; exit 0'
    p, lines, body, _ = _run_step(tmp_path / "r", stub)
    assert p.returncode == 0 and "Corpus flips: 0 (stub)." in body and UNKNOWN not in body
    assert "check_corpus_flips.py" not in p.stdout  # no ::warning:: from this step


def test_step_real_checker_on_the_committed_tree_reports_zero_flips(tmp_path):
    """Control: the real checker, HEAD against the working tree."""
    dirty = subprocess.run(["git", "status", "--porcelain", "data/incidents.json"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        pytest.skip("data/incidents.json has uncommitted changes")
    p, lines, body, _ = _run_step(tmp_path / "r", None)
    assert p.returncode == 0 and "Corpus flips: 0" in body


def test_step_harness_fires_on_mutants(tmp_path):
    """The bash tests above must FAIL against a broken workflow (agreement 6)."""
    # M1: exit code not captured -> a non-zero checker aborts the step under -e
    r = _run_step(tmp_path / "m1", "exit 1", lambda t: t.replace(" || flip_rc=$?", ""))
    assert not _flags_unknown(r[0], r[1], r[2])
    # M2: no -s guard on the rc=1 branch -> a missing report is not routed to UNKNOWN
    r = _run_step(tmp_path / "m2", "exit 1", lambda t: t.replace(
        'elif [ "$flip_rc" = "1" ] && [ -s "$RUNNER_TEMP/corpus-flips.md" ]', 'elif [ "$flip_rc" = "1" ]'))
    assert not _flags_unknown(r[0], r[1], r[2])
