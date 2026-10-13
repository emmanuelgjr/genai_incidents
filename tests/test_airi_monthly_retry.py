"""D95: the AIRI fetch is retried monthly. Not-attempted weeks must not count as
failures, a failed monthly attempt must still go loud, and the workflow must
only attempt AIRI on the first scheduled run of the month or a try_airi dispatch.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_source_health as h  # noqa: E402

STALE = {"airi_navigator": {"consecutive_failures": 14, "last_attempt": "2026-10-11",
                            "last_outcome": "failure", "last_success": "2026-05-31", "status": "stale"}}


def test_skipped_week_changes_nothing_and_is_not_stale():
    new, stale, degraded, notices = h.update_source_health(
        STALE, {"airi_navigator": "not-attempted"}, today="2026-10-18")
    assert new == STALE and stale == [] and degraded == [] and notices == {}


def test_control_a_failure_does_increment_and_goes_loud():
    # the control: the same state with outcome "failure" is what skipped must NOT behave like
    new, stale, _d, _n = h.update_source_health(STALE, {"airi_navigator": "failure"}, today="2026-10-18")
    assert new["airi_navigator"]["consecutive_failures"] == 15 and stale == ["airi_navigator"]


def test_three_skipped_weeks_then_failed_monthly_attempt_is_loud(tmp_path):
    f = tmp_path / "s.json"
    f.write_text(json.dumps({"airi_navigator": {"consecutive_failures": 2, "status": "degraded"}}), encoding="utf-8")
    for day in ("2026-11-08", "2026-11-15", "2026-11-22"):
        assert h.main(["--outcomes-json", '{"airi_navigator": "not-attempted"}', "--state-file", str(f), "--today", day]) == 0
    assert json.loads(f.read_text())["airi_navigator"]["consecutive_failures"] == 2  # not inflated
    rc = h.main(["--outcomes-json", '{"airi_navigator": "failure"}', "--state-file", str(f), "--today", "2026-12-06"])
    assert rc == 1  # the monthly attempt reaches the threshold of 3 and fails the run


def test_a_successful_monthly_attempt_recovers_the_source(tmp_path):
    f = tmp_path / "s.json"
    f.write_text(json.dumps(STALE), encoding="utf-8")
    assert h.main(["--outcomes-json", '{"airi_navigator": "success"}', "--state-file", str(f), "--today", "2026-11-01"]) == 0
    assert json.loads(f.read_text())["airi_navigator"]["status"] == "ok"


def test_a_bare_github_skipped_still_counts_as_a_failure():
    new, _s, degraded, _n = h.update_source_health({}, {"airi_navigator": "skipped"}, today="2026-10-18")
    assert new["airi_navigator"]["consecutive_failures"] == 1 and degraded == ["airi_navigator"]


def test_other_sources_are_still_judged_when_airi_is_skipped():
    new, stale, _d, _n = h.update_source_health(
        {}, {"airi_navigator": "not-attempted", "oecd_aim": "failure"}, today="2026-10-18")
    assert "airi_navigator" not in new and new["oecd_aim"]["consecutive_failures"] == 1


def _wf():
    return yaml.safe_load((ROOT / ".github" / "workflows" / "auto-refresh.yml").read_text(encoding="utf-8"))


def test_workflow_only_attempts_airi_when_gated():
    wf = _wf()
    steps = wf["jobs"]["refresh"]["steps"]
    airi = next(s for s in steps if s.get("id") == "ingest_airi")
    gate = next(s for s in steps if s.get("id") == "airi_gate")
    assert airi["if"] == "steps.airi_gate.outputs.attempt == 'true'"
    assert steps.index(gate) < steps.index(airi)
    assert airi.get("continue-on-error") is True
    health = next(s for s in steps if s.get("id") == "health")
    assert "'not-attempted'" in health["env"]["AIRI"] and "airi_gate.outputs.attempt" in health["env"]["AIRI"]
    assert "try_airi" in (wf.get(True) or wf.get("on"))["workflow_dispatch"]["inputs"]


def test_gate_script_decisions():
    """Run the gate's shell logic for the cases that matter (bash only)."""
    script = next(s for s in _wf()["jobs"]["refresh"]["steps"] if s.get("id") == "airi_gate")["run"]
    import os, shutil
    # On Windows plain `bash` can be WSL's, which drops the environment; prefer Git Bash.
    git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git" / "bin" / "bash.exe"
    bash = str(git_bash) if git_bash.exists() else shutil.which("bash")

    def run(event, try_airi, day, tmp=[None]):
        import os, tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out"
            out.write_text("", encoding="utf-8")
            env = dict(os.environ, EVENT=event, TRY_AIRI=try_airi, GITHUB_OUTPUT=out.as_posix())
            # shadow `date` so the day-of-month is controlled
            fn = "date() { echo " + str(day) + "; }"
            subprocess.run([bash, "-c", fn + chr(10) + script], env=env, capture_output=True, text=True, check=True)
            return "attempt=true" in out.read_text(encoding="utf-8")

    assert run("schedule", "", 4) is True       # first Sunday of the month
    assert run("schedule", "", 7) is True
    assert run("schedule", "", 8) is False      # not-attempted week
    assert run("schedule", "", 28) is False
    assert run("workflow_dispatch", "false", 3) is False   # a test dispatch does not pollute the counter
    assert run("workflow_dispatch", "true", 20) is True
