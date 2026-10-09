"""v2.13.0 item 3 / D60: the refresh PR lists newly retracted entries and is labelled
`needs-ruling` for a landmark or more than 10 retractions. Flag, never block.

Plants a newly REJECTED CVE through the real merge rule (`_apply_cve_rejections`) and
feeds the before/after corpora to the report, so the listing is judged against what the
merge would actually do, not against a hand-written status."""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import newly_retracted_report as nr  # noqa: E402

_spec = importlib.util.spec_from_file_location("merge_and_dedupe_nr", ROOT / "scripts" / "merge_and_dedupe.py")
merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge)


def _entry(n: int, tier: str = "feed", status: str | None = None) -> dict:
    cve = f"CVE-2030-{n:04d}"
    e = {"id": f"INC-9{n:04d}", "tier": tier, "cve_ids": [cve], "source_ids": [cve]}
    if status:
        e["status"] = status
    return e


def _build(before_entries: list[dict], rejected_cves: set[str]):
    """(before, after) corpora where *after* is the merge rule applied with *rejected_cves*."""
    rejected = {c: {"state": "REJECTED", "checked": "2026-10-09"} for c in rejected_cves}
    after = []
    for e in before_entries:
        a = copy.deepcopy(e)
        merge._apply_cve_rejections(a, rejected)
        after.append(a)
    return {"incidents": before_entries}, {"incidents": after}


def test_one_non_landmark_retraction_is_listed_without_the_label():
    ents = [_entry(i) for i in range(1, 6)]
    b, a = _build(ents, {"CVE-2030-0003"})
    rows = nr.newly_retracted(b, a)
    needs, reasons = nr.decide(rows)
    assert rows == [{"id": "INC-90003", "cve_ids": ["CVE-2030-0003"], "tier": "feed",
                     "rejected_cve_ids": ["CVE-2030-0003"]}]
    assert needs is False and reasons == []
    md = nr.render_md(rows, needs, reasons)
    assert "INC-90003 | CVE-2030-0003 | feed" in md and "needs-ruling" not in md


def test_a_landmark_retraction_is_listed_and_labelled():
    ents = [_entry(1), _entry(2, tier="landmark"), _entry(3)]
    b, a = _build(ents, {"CVE-2030-0002"})
    rows = nr.newly_retracted(b, a)
    needs, reasons = nr.decide(rows)
    assert [r["id"] for r in rows] == ["INC-90002"] and rows[0]["tier"] == "landmark"
    assert needs is True and "landmark" in reasons[0] and "INC-90002" in reasons[0]
    assert "needs-ruling" in nr.render_md(rows, needs, reasons)


def test_eleven_retractions_are_labelled_and_ten_are_not():
    ents = [_entry(i) for i in range(1, 13)]
    b, a = _build(ents, {f"CVE-2030-{i:04d}" for i in range(1, 12)})   # 11
    rows = nr.newly_retracted(b, a)
    needs, reasons = nr.decide(rows)
    assert len(rows) == 11 and needs is True and "11 newly retracted" in reasons[0]
    b, a = _build(ents, {f"CVE-2030-{i:04d}" for i in range(1, 11)})   # 10
    rows = nr.newly_retracted(b, a)
    assert len(rows) == 10 and nr.decide(rows) == (False, [])


def test_already_retracted_on_main_is_not_newly_retracted():
    ents = [_entry(1, tier="landmark", status="retracted"), _entry(2)]
    b, a = _build(ents, {"CVE-2030-0001", "CVE-2030-0002"})
    assert [r["id"] for r in nr.newly_retracted(b, a)] == ["INC-90002"]
    assert nr.newly_retracted(b, b) == []


def test_corroborated_entry_is_not_retracted_so_not_listed():
    e = _entry(1)
    e["source_ids"] = ["CVE-2030-0001", "aiid-1"]   # other evidence: stands, flagged only
    b, a = _build([e], {"CVE-2030-0001"})
    assert nr.newly_retracted(b, a) == []


def test_committed_data_has_no_newly_retracted_against_itself():
    import json
    d = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    assert nr.newly_retracted(d, d) == []


# ----- workflow wiring -----

def _wf():
    return yaml.safe_load((ROOT / ".github" / "workflows" / "auto-refresh.yml").read_text(encoding="utf-8"))


def test_summary_reads_the_sweep_step_outcome_via_the_job_output_not_the_job_result():
    wf = _wf()
    sweep = wf["jobs"]["cve-sweep"]
    step = next(s for s in sweep["steps"] if "ingest_cve_rejections.py" in str(s.get("run", "")))
    assert step.get("continue-on-error") is True, "premise: the step is continue-on-error, so job.result is always success"
    assert sweep["outputs"]["sweep_outcome"] == "${{ steps.%s.outcome }}" % step["id"]
    summ = next(s for s in wf["jobs"]["refresh"]["steps"] if s.get("name") == "Ingest result summary")
    expr = summ["env"]["CVE_SWEEP"]
    assert "needs.cve-sweep.outputs.sweep_outcome" in expr
    assert expr.strip() != "${{ needs.cve-sweep.result }}", "the job result can never show the step's failure"


def test_sweep_job_is_read_only():
    assert _wf()["jobs"]["cve-sweep"]["permissions"] == {"contents": "read"}


def test_pr_step_uses_the_report_body_and_the_label_decision_and_is_not_blocked():
    steps = _wf()["jobs"]["refresh"]["steps"]
    names = [s.get("name") for s in steps]
    rep = steps[names.index("Newly retracted entries report")]
    pr = steps[names.index("Open / update refresh PR")]
    lab = steps[names.index("Ensure needs-ruling label exists")]
    assert names.index("Newly retracted entries report") < names.index("Open / update refresh PR")
    assert "needs-ruling" in pr["with"]["labels"] and "steps.retracted.outputs.needs_ruling" in pr["with"]["labels"]
    assert "pr-body.md" in pr["with"]["body-path"]
    assert lab["run"].rstrip().endswith("|| true") and "gh label create needs-ruling" in lab["run"]
    for s in (rep, lab):   # never blocks: no exit-1 path of its own
        assert "exit 1" not in s["run"]


# ----- fail-safe (D60 "never block") and stale-label removal -----

def _report_step() -> dict:
    return next(s for s in _wf()["jobs"]["refresh"]["steps"] if s.get("id") == "retracted")


def _run_report_step(cwd: Path, tmp: Path) -> tuple[int, dict, str]:
    import shutil
    import subprocess
    bash = shutil.which("bash")
    if not bash:
        import pytest
        pytest.skip("bash not available")
    script = tmp / "step.sh"
    script.write_text(_report_step()["run"], encoding="utf-8", newline="\n")
    out = tmp / "gh_output"
    out.write_text("", encoding="utf-8")
    env = {**__import__("os").environ, "RUNNER_TEMP": str(tmp), "GITHUB_OUTPUT": str(out)}
    r = subprocess.run([bash, str(script)], cwd=cwd, env=env, capture_output=True)
    kv = dict(l.split("=", 1) for l in out.read_text(encoding="utf-8").splitlines() if "=" in l)
    return r.returncode, kv, (tmp / "pr-body.md").read_text(encoding="utf-8")


def test_report_step_is_non_blocking_and_a_failed_report_flags_needs_ruling(tmp_path):
    assert _report_step().get("continue-on-error") is True
    empty = tmp_path / "empty"      # no scripts/newly_retracted_report.py here: python exits non-zero
    empty.mkdir()
    rc, kv, body = _run_report_step(empty, tmp_path)
    assert rc == 0, "the step itself must succeed even when the report script fails"
    assert kv["needs_ruling"] == "true", "unknown retraction state is flagged, not passed as clean"
    assert "could not be produced" in body and "Automated weekly refresh" in body, "static body plus a visible line"


def test_report_step_success_path_reports_clean_with_the_static_body(tmp_path):
    work = tmp_path / "w"
    work.mkdir()
    rc, kv, body = _run_report_step(ROOT, work)
    assert rc == 0 and kv == {"count": "0", "needs_ruling": "false"}
    assert "Automated weekly refresh" in body and "None: no entry is retracted" in body


def test_unknown_state_gets_the_label_and_only_an_explicit_false_removes_it():
    steps = _wf()["jobs"]["refresh"]["steps"]
    by = {s.get("name"): s for s in steps}
    assert "!= 'false'" in by["Open / update refresh PR"]["with"]["labels"]
    assert "!= 'false'" in by["Ensure needs-ruling label exists"]["if"]
    rm = by["Remove stale needs-ruling label"]
    assert "needs_ruling == 'false'" in rm["if"] and "pull-request-number" in rm["if"]
    assert "--remove-label needs-ruling" in rm["run"] and rm["run"].rstrip().endswith("|| true")
    assert "steps.cpr.outputs.pull-request-number" in rm["env"]["PR"]
    names = [s.get("name") for s in steps]
    assert names.index("Remove stale needs-ruling label") > names.index("Open / update refresh PR")
    assert by["Open / update refresh PR"]["id"] == "cpr"
