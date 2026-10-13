"""D120: the refresh PR body carries a per-field report of AIID-driven changes.

Each check names the input that makes it fail (agreement 6). The workflow-wiring
check is a function over the workflow text so the test can show it firing on a
copy with the append removed."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import aiid_change_report as r

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "auto-refresh.yml"


def _e(iid, sids, **kw):
    base = {"id": iid, "source_ids": sids, "title": f"T {iid}", "severity": "Medium", "date": "2021-05-01",
            "year": 2021, "corpus": "security", "attack_vector": "x", "updated": "2026-01-01"}
    base.update(kw)
    return base


BEFORE = {"incidents": [
    _e("INC-1", ["AIID-1"]),
    _e("INC-2", ["AIID-2", "OECD-AIM-2026-01-01-aaaa"]),
    _e("INC-3", ["CVE-2025-1"]),
    _e("INC-4", ["AIID-4"]),
]}
AFTER = {"incidents": [
    _e("INC-1", ["AIID-1"], title="Reportedly T INC-1", updated="2026-10-13"),
    _e("INC-2", ["AIID-2", "OECD-AIM-2026-01-01-aaaa"], severity="Critical", date="2015-01-01", year=2015),
    _e("INC-3", ["CVE-2025-1"], severity="High"),       # not AIID-carrying: out of scope
    _e("INC-4", ["AIID-4"]),                              # unchanged
    _e("INC-5", ["AIID-5"]),
    _e("INC-6", ["CVE-2026-9"]),
]}


def test_report_lists_rows_fields_counts_and_oecd_flag():
    d = r.diff(BEFORE, AFTER)
    assert d["new_rows_total"] == 2 and d["new_aiid_rows"] == 1
    assert d["changed_rows"] == 2 and d["changed_rows_also_oecd"] == 1
    assert d["field_counts"]["severity"] == 1 and d["field_counts"]["title"] == 1
    assert d["field_counts"]["date"] == 1 and d["field_counts"]["year"] == 1
    sev = d["listed"]["severity"]
    assert sev == [{"id": "INC-2", "before": "Medium", "after": "Critical", "also_oecd": True}]
    assert d["listed"]["title"][0]["id"] == "INC-1" and d["listed"]["title"][0]["also_oecd"] is False
    assert all(x["id"] != "INC-3" for rows in d["listed"].values() for x in rows)  # CVE-only row excluded
    md = r.render_md(d)
    assert "INC-2 | Medium | Critical | yes" in md
    assert "New rows overall: **2**" in md and "new AIID rows: **1**" in md
    assert "`date` changes (1)" in md and "`year` changes (1)" in md and "`corpus` changes" not in md


def test_report_is_empty_when_nothing_aiid_changed():
    d = r.diff(BEFORE, BEFORE)
    assert d["changed_rows"] == 0 and d["new_rows_total"] == 0
    assert "No AIID-driven change" in r.render_md(d)


def test_report_script_runs_against_a_real_baseline(tmp_path):
    after = tmp_path / "after.json"
    after.write_text(json.dumps(AFTER), encoding="utf-8")
    # HEAD's data/incidents.json vs a synthetic after: must run end to end and not crash
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "aiid_change_report.py"), "--after", str(after),
                        "--out-md", str(tmp_path / "o.md")], capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr[-500:]
    assert "AIID-driven changes (D120 change report)" in (tmp_path / "o.md").read_text(encoding="utf-8")


def test_report_script_fails_loudly_on_a_bad_baseline(tmp_path):
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "aiid_change_report.py"),
                        "--before-ref", "no-such-ref-xyz"], capture_output=True, text=True)
    assert p.returncode != 0  # the workflow turns this into needs-ruling, not a silent pass


def check_wiring(text: str) -> list[str]:
    """The workflow must run the report, append its output to pr-body.md, and on
    failure append a notice and set needs_ruling=true without aborting."""
    problems = []
    if "scripts/aiid_change_report.py" not in text:
        return ["workflow never runs scripts/aiid_change_report.py"]
    seg = text[text.index("scripts/aiid_change_report.py"):]
    seg = seg[:seg.index("Ensure needs-ruling label exists")]
    if 'cat "$RUNNER_TEMP/aiid-change-report.md"' not in seg or 'pr-body.md' not in seg:
        problems.append("report output is not appended to pr-body.md")
    if 'needs_ruling=true' not in seg:
        problems.append("failure path does not mark the PR needs-ruling")
    if "exit 1" in seg:
        problems.append("failure path aborts the refresh (D120: fail soft)")
    return problems


def test_workflow_appends_the_report_and_fails_soft():
    assert check_wiring(WORKFLOW.read_text(encoding="utf-8")) == []


def test_wiring_check_fires_when_the_append_or_the_flag_is_removed():
    text = WORKFLOW.read_text(encoding="utf-8")
    no_append = text.replace('{ echo; cat "$RUNNER_TEMP/aiid-change-report.md"; } >> "$RUNNER_TEMP/pr-body.md"', "true")
    assert any("not appended" in p for p in check_wiring(no_append))
    seg_start = text.index("aiid_change_report.py failed")
    no_flag = text[:seg_start] + text[seg_start:].replace('echo "needs_ruling=true" >> "$GITHUB_OUTPUT"', "true", 1)
    assert any("needs-ruling" in p for p in check_wiring(no_flag))
    aborts = text.replace("The refresh was not blocked.\"\n            } >> \"$RUNNER_TEMP/pr-body.md\"\n            echo \"needs_ruling=true\" >> \"$GITHUB_OUTPUT\"\n          fi\n\n      # D123: the full, untruncated",
                          "x\"\n            } >> \"$RUNNER_TEMP/pr-body.md\"\n            exit 1\n          fi\n\n      # D123: the full, untruncated")
    assert aborts != text and any("fail soft" in p for p in check_wiring(aborts))
