"""WS4-T14 (D25(c), D42): the weekly refresh must keep the AIID snapshot
current, ahead of the merge, loudly and without blocking the other sources."""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"


def _steps(text: str) -> list[str]:
    # split on the "- name:" / "- uses:" step markers at the steps indent
    return re.split(r"(?m)^      - (?=name:|uses:)", text)[1:]


def check_aiid_step(text: str) -> list[str]:
    problems = []
    steps = _steps(text)
    idx = next((i for i, s in enumerate(steps) if "scripts/ingest_aiid_snapshot.py" in s), None)
    if idx is None:
        return ["no step runs scripts/ingest_aiid_snapshot.py"]
    step = steps[idx]
    if "continue-on-error: true" not in step:
        problems.append("AIID step must be continue-on-error (it must not block the other sources)")
    if "id: ingest_aiid" not in step:
        problems.append("AIID step needs id: ingest_aiid so its outcome is reported")
    merge = next((i for i, s in enumerate(steps) if "scripts/merge_and_dedupe.py" in s), None)
    if merge is None or idx > merge:
        problems.append("AIID step must run before the merge step")
    if "steps.ingest_aiid.outcome" not in text:
        problems.append("AIID outcome must be reported in the ingest summary")
    return problems


def test_weekly_refresh_runs_the_aiid_snapshot_before_merge():
    assert check_aiid_step(WORKFLOW.read_text(encoding="utf-8")) == []


def test_check_fires_when_step_missing_or_misplaced_or_blocking():
    good = WORKFLOW.read_text(encoding="utf-8")
    assert check_aiid_step(good.replace("scripts/ingest_aiid_snapshot.py", "scripts/true.py"))
    assert check_aiid_step(good.replace("id: ingest_aiid", "id: other"))
    # blocking: strip continue-on-error from the AIID step only
    head, tail = good.split("id: ingest_aiid", 1)
    blocking = head + "id: ingest_aiid" + tail.replace("continue-on-error: true", "", 1)
    assert any("continue-on-error" in p for p in check_aiid_step(blocking))
    # misplaced: AIID step after the merge step
    moved = good.replace(
        "      - name: Refresh AIID snapshot (sanctioned bulk channel)\n        timeout-minutes: 15\n        id: ingest_aiid\n        run: python scripts/ingest_aiid_snapshot.py\n        continue-on-error: true\n",
        "",
    ) + "\n      - name: late\n        id: ingest_aiid\n        run: python scripts/ingest_aiid_snapshot.py\n        continue-on-error: true\n"
    assert any("before the merge" in p for p in check_aiid_step(moved))


# ---------------------------------------------------------------------------
# D142 (2026-10-28): the scheduled refresh was cancelled at the 60-minute job
# limit on 2026-10-18 and 2026-10-25. D146-1 (2026-10-29) then moved the OECD
# fetch into its own `oecd-fetch` job. These checks pin the budget arithmetic of
# BOTH jobs and the "a hang fails at its own step" rule.

REFRESH_MEASURED_NEED_MIN = 12   # 2026-10-25 job total 63 min minus the OECD step 50.8
OECD_MEASURED_MIN = 51           # 2026-10-18 / 10-25
OECD_JOB_OTHER_MIN = 3           # install + restore + probe + stash + uploads
TESTS_MEASURED_MIN = 8           # 2026-10-25 (7.6) and 10-18 (>=7.8)
HEADROOM = 1.5
OTHER_MEASURED_MIN = 4.5         # refresh job total minus tests (12.1 - 7.6)
OECD_STEP = "Refresh OECD AI Incidents Monitor"


def _missing_step_caps(job: dict, label: str) -> list[str]:
    out = []
    for s in job["steps"]:
        name = s.get("name")
        if name is None:
            continue  # unnamed `uses:` steps: checkout, setup-python (seconds; the job cap covers them)
        if "timeout-minutes" not in s:
            out.append(f"{label}: step {name!r} has no step-level timeout-minutes")
    return out


def check_refresh_budget(text: str) -> list[str]:
    import yaml

    wf = yaml.safe_load(text)
    problems = []
    # --- refresh job: must not contain the OECD fetch, and must fit its own work
    job = wf["jobs"]["refresh"]
    if job.get("timeout-minutes", 0) < REFRESH_MEASURED_NEED_MIN * HEADROOM:
        problems.append(
            f"refresh job timeout {job.get('timeout-minutes')} min is under {HEADROOM}x the "
            f"measured {REFRESH_MEASURED_NEED_MIN} min need")
    problems += _missing_step_caps(job, "refresh")
    by = {s.get("name"): s for s in job["steps"]}
    if OECD_STEP in by or any("ingest_oecd_aim.py" in (s.get("run") or "") for s in job["steps"]):
        problems.append("the OECD fetch must not run in the refresh job (D146-1)")
    tests = by.get("Unit tests", {})
    if tests.get("timeout-minutes", 0) < TESTS_MEASURED_MIN * 2:
        problems.append("Unit tests step timeout is under 2x its measured duration")
    if (tests.get("run") or "").strip() != "pytest tests -q":
        problems.append("the refresh path must run exactly `pytest tests -q` (no -k / --deselect / -m / --ignore / path selectors)")
    # A1/A2 (D142 gate advisory): the step cap that dominates the job plus the
    # measured remainder must fit inside the job cap, so bumping one step cap
    # later cannot silently invert the budget.
    if tests.get("timeout-minutes", 0) + OTHER_MEASURED_MIN >= job.get("timeout-minutes", 0):
        problems.append("tests cap + measured other time must be below the refresh job cap")
    # --- oecd-fetch job: owns the fetch and its own budget
    oj = wf["jobs"].get("oecd-fetch")
    if oj is None:
        return problems + ["no oecd-fetch job"]
    problems += _missing_step_caps(oj, "oecd-fetch")
    oecd = {s.get("name"): s for s in oj["steps"]}.get(OECD_STEP, {})
    if oecd.get("timeout-minutes", 0) < OECD_MEASURED_MIN * 1.2:
        problems.append("OECD step timeout is under 1.2x its measured duration")
    if oecd.get("timeout-minutes", 0) + OECD_JOB_OTHER_MIN >= oj.get("timeout-minutes", 0):
        problems.append("OECD cap + measured other time must be below the oecd-fetch job cap")
    # --- finalize job: only needs a cap on every step
    if "finalize" in wf["jobs"]:
        problems += _missing_step_caps(wf["jobs"]["finalize"], "finalize")
    return problems


def test_refresh_job_budget_and_step_timeouts():
    assert check_refresh_budget(WORKFLOW.read_text(encoding="utf-8")) == []


def test_refresh_budget_check_fires():
    good = WORKFLOW.read_text(encoding="utf-8")
    nl = "\n"
    refresh_cap = "    timeout-minutes: 40" + nl + "    needs: cve-sweep" + nl
    assert refresh_cap in good

    def with_refresh_cap(n):
        return good.replace(refresh_cap, f"    timeout-minutes: {n}" + nl + "    needs: cve-sweep" + nl, 1)

    # a refresh cap under 1.5x the measured need
    assert check_refresh_budget(with_refresh_cap(15))
    # tests cap + other no longer fits: 40 -> 29
    assert any("below the refresh job cap" in x for x in check_refresh_budget(with_refresh_cap(29)))
    # a step with its cap stripped (the PR step, where the 10-25 run was killed)
    marker = "      - name: Open / update refresh PR" + nl + "        timeout-minutes: 10" + nl
    head, tail = good.split(marker, 1)
    assert check_refresh_budget(head + "      - name: Open / update refresh PR" + nl + tail)
    # ... and in the finalize job
    marker = "      - name: Enforce source health" + nl + "        timeout-minutes: 5" + nl
    head, tail = good.split(marker, 1)
    assert any("finalize" in x for x in check_refresh_budget(head + "      - name: Enforce source health" + nl + tail))
    # tests narrowed
    assert check_refresh_budget(good.replace("run: pytest tests -q", "run: pytest tests/test_x.py", 1))
    # narrowing variants must each fire (the old substring guard passed the first two)
    for narrowed in ("pytest tests -q -k aiid", "pytest tests -q --deselect tests/test_x.py::t",
                     "pytest tests -q -m fast", "pytest tests -q --ignore=tests/slow"):
        assert check_refresh_budget(good.replace("run: pytest tests -q", "run: " + narrowed, 1)), narrowed
    # OECD job: raising the step cap 65 -> 80 inverts that job's budget (80 + 3 >= 80)
    oecd_hdr = "name: Refresh OECD AI Incidents Monitor" + nl + "        timeout-minutes: "
    head, tail = good.split(oecd_hdr + "65", 1)
    assert any("oecd-fetch job cap" in x for x in check_refresh_budget(head + oecd_hdr + "80" + tail))
    # lowering the OECD step cap below 1.2x the measured fetch
    assert any("1.2x" in x for x in check_refresh_budget(head + oecd_hdr + "55" + tail))
    # putting the fetch back into the refresh job
    kev = "      - name: Refresh CISA KEV catalog" + nl
    back = good.replace(
        kev,
        "      - name: Refresh OECD AI Incidents Monitor" + nl + "        timeout-minutes: 65" + nl
        + "        run: python scripts/ingest_oecd_aim.py" + nl + kev, 1)
    assert any("must not run in the refresh job" in x for x in check_refresh_budget(back))
