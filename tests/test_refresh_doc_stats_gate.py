"""Invariant 6 in the refresh workflow: PR #102 (15,637 -> 15,642) merged with
README/DATASHEET/index.html at the old total because auto-refresh.yml never ran
render_docs_stats.py or check_stats_drift.py. Each check has a mutated-text
counter-case proving it can fail."""

from __future__ import annotations

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"


def problems(text: str) -> list[str]:
    steps = yaml.safe_load(text)["jobs"]["refresh"]["steps"]
    run = lambda i: steps[i].get("run", "")
    out = []
    find = lambda needle: next((i for i, s in enumerate(steps) if needle in s.get("run", "")), None)
    render, merge = find("render_markdown.py"), find("merge_and_dedupe.py")
    docs, drift = find("render_docs_stats.py"), find("check_stats_drift.py")
    cpr = next((i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith("peter-evans/create-pull-request")), None)
    if docs is None:
        out.append("render_docs_stats.py never runs")
    elif render is None or docs < render:
        out.append("render_docs_stats.py must run after render_markdown.py")
    if drift is None:
        out.append("check_stats_drift.py never runs")
    else:
        if docs is not None and drift < docs:
            out.append("drift check runs before the docs are regenerated")
        if cpr is None or drift > cpr:
            out.append("drift check must precede create-pull-request")
        if steps[drift].get("continue-on-error"):
            out.append("drift check must be a hard gate (no continue-on-error)")
    return out


def test_workflow_regenerates_doc_stats_and_gates_on_drift_before_the_pr():
    assert problems(WF.read_text(encoding="utf-8")) == []


def test_deleting_the_steps_makes_the_check_fail():
    t = WF.read_text(encoding="utf-8")
    assert "python scripts/render_docs_stats.py\n" in t
    assert problems(t.replace("          python scripts/render_docs_stats.py\n", "")) == ["render_docs_stats.py never runs"]
    gate = "      - name: Doc surfaces match stats.json (invariant 6)\n        run: python scripts/check_stats_drift.py\n"
    assert gate in t
    assert "check_stats_drift.py never runs" in problems(t.replace(gate, ""))
    assert problems(t.replace(gate, "").replace("pytest tests -q", "pytest tests -q\n          python scripts/check_stats_drift.py")) == []  # control: a step before the PR passes
    assert "drift check must be a hard gate (no continue-on-error)" in problems(t.replace(gate, gate + "        continue-on-error: true\n"))
