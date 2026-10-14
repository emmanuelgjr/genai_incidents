"""R5 (red-reviewer advisory): validate.py's registry provenance check passes
inside the refresh job ONLY because the "Persist source health counters" step
resets ingest/_state/source_health.json to main's committed copy BEFORE the
"Re-merge + render + validate" step runs (the freshly stamped working copy
would otherwise claim a provenance context validate does not accept in-tree).
That reset was load-bearing and untested. This test pins it.

Inputs that make it fail (each exercised below on mutated workflow text):
  * the `git checkout -- "$STATE_FILE"` reset deleted from the persist step
  * the reset present but placed BEFORE the persist call (no longer a reset of
    the counter that persist just read)
  * the persist/reset step moved AFTER the validate step
  * persist step renamed away / validate step missing
"""

from __future__ import annotations

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"
RESET = 'git checkout -- "$STATE_FILE"'


def problems(text: str) -> list[str]:
    steps = yaml.safe_load(text)["jobs"]["refresh"]["steps"]
    persist = next((i for i, s in enumerate(steps)
                    if "persist_refresh_state.sh" in s.get("run", "")
                    and "ingest/_state/source_health.json" in s.get("run", "")), None)
    validate = next((i for i, s in enumerate(steps) if "scripts/validate.py" in s.get("run", "")), None)
    out = []
    if persist is None:
        return ["no step persists ingest/_state/source_health.json"]
    if validate is None:
        return ["no step runs scripts/validate.py"]
    run = steps[persist]["run"]
    if RESET not in run:
        out.append("the persist step no longer resets source_health.json to main's copy")
    elif run.index(RESET) < run.index("persist_refresh_state.sh"):
        out.append("the reset runs before the persist call")
    if persist >= validate:
        out.append("the persist/reset step runs at or after validate")
    if steps[persist].get("continue-on-error"):
        out.append("the persist/reset step must not be continue-on-error")
    if "if" in steps[persist]:
        out.append("the persist/reset step must be unconditional")
    # nothing between the reset and validate may re-stamp the state file
    for i in range(persist + 1, validate):
        r = steps[i].get("run", "")
        if "check_source_health.py" in r:
            out.append(f"step {i} re-runs check_source_health.py between the reset and validate")
    return out


def test_persist_resets_provenance_state_before_validate():
    assert problems(WF.read_text(encoding="utf-8")) == []


def test_each_mutation_makes_the_check_fail():
    t = WF.read_text(encoding="utf-8")
    reset_line = "          git checkout -- \"$STATE_FILE\" 2>/dev/null || rm -f \"$STATE_FILE\"\n"
    assert t.count(reset_line) == 2  # source-health step + skip-probe step (indented differently)
    # 1. reset removed from the source-health persist step (first occurrence)
    m1 = t.replace(reset_line, "", 1)
    assert "the persist step no longer resets source_health.json to main's copy" in problems(m1)
    # 2. reset placed before the persist call
    persist_call = 'bash scripts/persist_refresh_state.sh ' + chr(92) + chr(10)
    assert persist_call in t
    m2 = t.replace(reset_line, "", 1).replace(persist_call, reset_line.lstrip() + "          " + persist_call, 1)
    assert "the reset runs before the persist call" in problems(m2)
    # 3. persist step moved after validate: swap names of the order by cutting/pasting
    doc = yaml.safe_load(t)
    steps = doc["jobs"]["refresh"]["steps"]
    pi = next(i for i, s in enumerate(steps) if "persist_refresh_state.sh" in s.get("run", "")
              and "source_health.json" in s["run"])
    vi = next(i for i, s in enumerate(steps) if "scripts/validate.py" in s.get("run", ""))
    steps.insert(vi, steps.pop(pi))  # persist now immediately after validate
    assert any("at or after validate" in p for p in problems(yaml.safe_dump(doc)))
    # 4. conditional / continue-on-error persist step
    doc = yaml.safe_load(t)
    doc["jobs"]["refresh"]["steps"][pi]["if"] = "false"
    assert any("unconditional" in p for p in problems(yaml.safe_dump(doc)))
    doc = yaml.safe_load(t)
    doc["jobs"]["refresh"]["steps"][pi]["continue-on-error"] = True
    assert any("continue-on-error" in p for p in problems(yaml.safe_dump(doc)))
    # 5. a health re-run between reset and validate
    doc = yaml.safe_load(t)
    doc["jobs"]["refresh"]["steps"].insert(vi, {"name": "x", "run": "python scripts/check_source_health.py"})
    assert any("re-runs check_source_health" in p for p in problems(yaml.safe_dump(doc)))
