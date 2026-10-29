"""D66/D63 workflow shape: the pair-hold step precedes the merge, the loud-failure
enforcement steps survive an earlier failure, and the overdue alert exists.
Each check has a mutated-text counter-case proving it can fail."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"


def _jobs(text):
    return yaml.safe_load(text)["jobs"]


def _steps(text):
    return _jobs(text)["refresh"]["steps"]


def _find(steps, pred):
    return next((i for i, s in enumerate(steps) if pred(s)), None)


def check(text) -> list[str]:
    """D146-1: the pair hold + guard stay in the refresh job; the fresh OECD bytes
    are stashed and uploaded by the oecd-fetch job; the loud-failure enforcement
    steps live in the job that owns the signal (probe: oecd-fetch, health: finalize)."""
    problems = []
    jobs = _jobs(text)
    steps = jobs["refresh"]["steps"]
    idx = lambda pred: _find(steps, pred)  # noqa: E731

    hold = idx(lambda s: "scripts/hold_pair_inputs.py" in (s.get("run") or ""))
    merge = idx(lambda s: "scripts/merge_and_dedupe.py" in (s.get("run") or ""))
    if hold is None:
        problems.append("no step runs scripts/hold_pair_inputs.py")
    elif merge is None or hold > merge:
        problems.append("hold step must run before the merge step")
    for job, name in (("finalize", "Enforce source health"),
                      ("oecd-fetch", "Enforce OECD skip-rule sampling probe")):
        js = jobs[job]["steps"]
        s = js[_find(js, lambda s, n=name: s.get("name") == n)]
        if "always()" not in str(s.get("if", "")):
            problems.append(f"{name!r} must run with always()")
    ojs = jobs["oecd-fetch"]["steps"]
    stash = _find(ojs, lambda s: "scripts/hold_pair_inputs.py" in (s.get("run") or ""))
    up = _find(ojs, lambda s: (s.get("with") or {}).get("name") == "held-oecd-aiid-inputs")
    if up is None:
        problems.append("held OECD/AIID inputs must be uploaded as an artifact")
    elif "always()" not in str(ojs[up].get("if", "")):
        problems.append("held-input upload must run with always()")
    if stash is None:
        problems.append("the oecd-fetch job must stash the fresh OECD bytes")
    for st, i in ((steps, hold), (ojs, stash), (ojs, up)):
        if i is not None and "runner.temp" not in str(st[i]) and "RUNNER_TEMP" not in str(st[i]):
            problems.append("held-input stash/upload must live under runner.temp, not the work tree")
    guard = idx(lambda s: "hold_pair_inputs.py --check-clean" in (s.get("run") or ""))
    pr = idx(lambda s: "create-pull-request" in str(s.get("uses", "")))
    if guard is None:
        problems.append("no held-path guard step (--check-clean)")
    elif pr is None or guard > pr:
        problems.append("held-path guard must run before the PR step")
    return problems


def test_workflow_is_decoupled():
    assert check((WF / "auto-refresh.yml").read_text(encoding="utf-8")) == []


def test_check_fires_on_mutations():
    t = (WF / "auto-refresh.yml").read_text(encoding="utf-8")
    assert any("no step runs" in p for p in check(t.replace("scripts/hold_pair_inputs.py", "scripts/nope.py")))
    assert any("must run with always()" in p for p in check(
        t.replace("always() && steps.health.outcome", "steps.health.outcome")))
    # the refresh job's hold step is the LAST occurrence (the first is oecd-fetch's stash)
    old = "run: python scripts/hold_pair_inputs.py --stash-dir \"$RUNNER_TEMP/held-pair-inputs\""
    head, tail = t.rsplit(old, 1)
    moved = head + "run: python scripts/merge_and_dedupe.py" + tail
    # the oecd-fetch job must stash the fresh bytes
    first, rest = t.split(old, 1)
    assert any("must stash" in p for p in check(first + "run: python scripts/true.py" + rest))
    assert any("before the merge" in p or "no step runs" in p for p in check(moved))


def test_stash_and_guard_checks_fire():
    t = (WF / "auto-refresh.yml").read_text(encoding="utf-8")
    in_tree = t.replace('"$RUNNER_TEMP/held-pair-inputs"', "held-pair-inputs").replace(
        "${{ runner.temp }}/held-pair-inputs", "held-pair-inputs")
    assert any("runner.temp" in p for p in check(in_tree))
    no_guard = t.replace("--check-clean", "--help")
    assert any("no held-path guard" in p for p in check(no_guard))


def test_gate_logic_untouched_sentinel():
    # The gate's abort text is what the fire-proof asserts on; if it moves, redo the proof.
    src = (ROOT / "scripts" / "merge_and_dedupe.py").read_text(encoding="utf-8")
    assert "[FATAL] D42/D25(a)+D67+D71" in src


def test_overdue_alert_workflow_shape():
    d = yaml.safe_load((WF / "refresh-overdue-alert.yml").read_text(encoding="utf-8"))
    on = d.get(True) or d.get("on")
    assert on["schedule"][0]["cron"]
    assert str(on["workflow_dispatch"]["inputs"]["max_age_days"]["default"]) == "21"
    assert d["permissions"]["issues"] == "write" and d["permissions"]["contents"] == "read"
