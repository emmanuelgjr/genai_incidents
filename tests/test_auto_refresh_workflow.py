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
        "      - name: Refresh AIID snapshot (sanctioned bulk channel)\n        id: ingest_aiid\n        run: python scripts/ingest_aiid_snapshot.py\n        continue-on-error: true\n",
        "",
    ) + "\n      - name: late\n        id: ingest_aiid\n        run: python scripts/ingest_aiid_snapshot.py\n        continue-on-error: true\n"
    assert any("before the merge" in p for p in check_aiid_step(moved))
