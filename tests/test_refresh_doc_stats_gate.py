"""Invariant 6 in the refresh workflow: PR #102 (15,637 -> 15,642) merged with
README/DATASHEET/index.html at the old total because auto-refresh.yml never ran
render_docs_stats.py or check_stats_drift.py. Each check has a mutated-text
counter-case proving it can fail."""

from __future__ import annotations

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"


# `if:` values that do not disable a step. Anything else on the gate step
# (`false`, `github.event_name == ...`, `${{ false }}`, ...) can switch it off.
_NON_DISABLING_IF = {"success()", "${{ success() }}", "always()", "${{ always() }}"}


def problems(text: str) -> list[str]:
    doc = yaml.safe_load(text)
    steps = doc["jobs"]["refresh"]["steps"]
    out = []

    def find(needle):
        """(step index, offset inside that step's run block) of the first hit.
        Comparing the tuple, not the step index alone, makes ORDER INSIDE one
        multi-line `run:` block count (R4a)."""
        for i, s in enumerate(steps):
            r = s.get("run", "")
            if needle in r:
                return (i, r.index(needle))
        return None

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
        gate = steps[drift[0]]
        if docs is not None and drift < docs:
            out.append("drift check runs before the docs are regenerated")
        if cpr is None or drift[0] > cpr:
            out.append("drift check must precede create-pull-request")
        if gate.get("continue-on-error"):
            out.append("drift check must be a hard gate (no continue-on-error)")
        if "if" in gate and str(gate["if"]).strip() not in _NON_DISABLING_IF:
            out.append(f"drift check step carries a disabling `if:` ({gate['if']!r})")
        if doc["jobs"]["refresh"].get("if") is False:
            out.append("refresh job is disabled")
        line = next((ln for ln in gate["run"].splitlines() if "check_stats_drift.py" in ln), "")
        if "||" in line or line.lstrip().startswith("#"):
            out.append("drift check is neutralised in its run line (`|| ...` or a comment)")
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


def test_r4_each_blind_spot_mutation_makes_the_check_fail():
    """R4: (a) render order inside ONE run block, (b) an `if:` that disables the gate."""
    t = WF.read_text(encoding="utf-8")
    gate = "      - name: Doc surfaces match stats.json (invariant 6)\n        run: python scripts/check_stats_drift.py\n"
    assert gate in t
    # (a) drift check placed BEFORE render_docs_stats inside the same run block
    block = "          python scripts/render_docs_stats.py\n"
    assert t.count(block) == 1
    a = t.replace(gate, "").replace(block, "          python scripts/check_stats_drift.py\n" + block)
    assert "drift check runs before the docs are regenerated" in problems(a)
    # control: same block, correct order, passes
    ok = t.replace(gate, "").replace(block, block + "          python scripts/check_stats_drift.py\n")
    assert problems(ok) == []
    # render_docs_stats before render_markdown inside one block is also caught
    md = "          python scripts/render_markdown.py\n"
    assert t.count(md) == 1
    swapped = t.replace(md + block, block + md)
    assert swapped != t and "render_docs_stats.py must run after render_markdown.py" in problems(swapped)
    # (b) disabling `if:` on the gate step
    for cond in ("false", "${{ false }}", "github.event_name == 'never'"):
        b = t.replace(gate, gate.replace("        run:", f"        if: {cond}\n        run:"))
        assert b != t
        assert any("disabling `if:`" in p for p in problems(b)), cond
    # controls: success() does not disable
    c = t.replace(gate, gate.replace("        run:", "        if: success()\n        run:"))
    assert problems(c) == []
    # `|| true` neutralises the gate
    d = t.replace("run: python scripts/check_stats_drift.py", "run: python scripts/check_stats_drift.py || true")
    assert any("neutralised" in p for p in problems(d))
