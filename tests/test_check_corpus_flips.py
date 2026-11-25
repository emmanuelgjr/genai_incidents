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


def test_declared_flip_is_clean():
    a = _after(**{"INC-1": "security"})
    r = c.compare(BEFORE, a, _declared(BEFORE, a))
    assert len(r["flips"]) == 1 and r["undeclared"] == []
    assert c.render_md(r, "main").startswith("Corpus flips: 1, all declared in the D120 report")


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


def test_many_undeclared_flips_render_bounded():
    big = {"incidents": [_e(f"INC-{i}", ["AIAAIC-1"]) for i in range(c.MAX_ROWS + 30)]}
    after = {"incidents": [dict(e, corpus="security") for e in big["incidents"]]}
    md = c.render_md(c.compare(big, after, {}), "main")
    assert f"**{c.MAX_ROWS + 30} existing row(s)" in md and "30 more undeclared flips" in md
    assert md.count("| INC-") == c.MAX_ROWS


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
    assert p.returncode == 1
    assert "INC-3" in (tmp_path / "a" / "o.md").read_text(encoding="utf-8")
    declared = _after(**{"INC-1": "security"})
    p = _run(tmp_path / "b", BEFORE, declared, json.dumps(rep.sidecar(rep.diff(BEFORE, declared))))
    assert p.returncode == 0
    p = _run(tmp_path / "c", BEFORE, undeclared, None)  # missing sidecar: the fail-soft path
    assert p.returncode == 2 and "ERROR" in p.stderr
    p = _run(tmp_path / "d", BEFORE, undeclared, "{broken")
    assert p.returncode == 2


# ---- workflow wiring --------------------------------------------------------------------------
def check_wiring(text: str) -> list[str]:
    if "scripts/check_corpus_flips.py" not in text:
        return ["workflow never runs scripts/check_corpus_flips.py"]
    problems = []
    if "--out-json" not in text[text.index("scripts/aiid_change_report.py"):text.index("scripts/check_corpus_flips.py")]:
        problems.append("D120 report is not asked for its JSON sidecar")
    seg = text[text.index("scripts/check_corpus_flips.py"):]
    seg = seg[:seg.index("Ensure needs-ruling label exists")]
    if seg.count('echo "needs_ruling=true" >> "$GITHUB_OUTPUT"') < 2:
        problems.append("undeclared (1) and could-not-run (2) paths must both set needs_ruling=true")
    if "needs_ruling=false" in seg:
        problems.append("must never write needs_ruling=false (would clear an earlier flag)")
    if "::warning::" not in seg:
        problems.append("no ::warning:: annotation")
    if "exit 1" in seg:
        problems.append("aborts the refresh (flag, never block)")
    if re.search(r"(>>?|tee)\s*\S*(data/|ingest/)", seg):
        problems.append("writes under data/ or ingest/")
    return problems


def test_workflow_wiring():
    assert check_wiring(WORKFLOW.read_text(encoding="utf-8")) == []


def test_wiring_check_fires():
    ANCHOR = '--out-md "$RUNNER_TEMP/corpus-flips.md" || flip_rc=$?' + chr(10)
    t = WORKFLOW.read_text(encoding="utf-8")
    assert any("sidecar" in p for p in check_wiring(t.replace('--out-json "$RUNNER_TEMP/aiid-change-report.json"', "")))
    assert any("needs_ruling=true" in p for p in check_wiring(t.replace(
        'echo "needs_ruling=true" >> "$GITHUB_OUTPUT"\n          else', "true\n          else")))
    assert any("false" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          needs_ruling=false" + chr(10))))
    assert any("aborts" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          exit 1" + chr(10))))
    assert any("writes under" in p for p in check_wiring(t.replace(ANCHOR, ANCHOR + "          echo x >> data/y" + chr(10))))
