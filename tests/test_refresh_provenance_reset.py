"""R5 (red-reviewer advisory) / D146-1: validate.py's registry provenance check
passes inside the refresh job ONLY if ingest/_state/source_health.json in its
tree is main's committed copy (a freshly stamped working copy would claim a
provenance context validate does not accept in-tree).

Before D146-1 that was achieved by a persist step that reset the file BEFORE
"Re-merge + render + validate". The counter now lives entirely in the `finalize`
job (the single writer of the refresh-state branch), so the invariant is
stronger and simpler: NO step of the refresh job restores, stamps or persists
the counter or the skip-probe cursor, so validate always sees the committed
copy. This test pins both halves.

Inputs that make it fail (each exercised below on mutated workflow text):
  * the refresh job restores / checks / persists source health or the cursor
  * the finalize job's persist runs before the check, or is conditional or
    continue-on-error, or is missing
  * persist_refresh_state.sh is invoked from any job other than finalize (two
    writers could race on the refresh-state branch)
"""

from __future__ import annotations

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"
STATE_TOKENS = ("source_health.json", "check_source_health.py", "persist_refresh_state.sh",
                "skip_probe_state", "refresh-state")


def problems(text: str) -> list[str]:
    jobs = yaml.safe_load(text)["jobs"]
    out = []
    for i, s in enumerate(jobs["refresh"]["steps"]):
        blob = str(s.get("run", "")) + str(s.get("with", ""))
        hit = [t for t in STATE_TOKENS if t in blob]
        if hit:
            out.append(f"refresh step {i} ({s.get('name')!r}) touches the refresh-state counters: {hit}")
    for jn, job in jobs.items():
        if jn == "finalize":
            continue
        for s in job.get("steps", []):
            if "persist_refresh_state.sh" in str(s.get("run", "")):
                out.append(f"job {jn!r} persists to refresh-state; finalize must be the only writer")
    fin = jobs.get("finalize")
    if fin is None:
        return out + ["no finalize job"]
    steps = fin["steps"]

    def find(pred):
        return next((i for i, s in enumerate(steps) if pred(s)), None)

    check = find(lambda s: "check_source_health.py" in str(s.get("run", "")))
    persist = find(lambda s: "persist_refresh_state.sh" in str(s.get("run", ""))
                   and "source_health.json" in str(s.get("run", "")))
    if check is None:
        out.append("finalize does not run check_source_health.py")
    if persist is None:
        return out + ["finalize does not persist ingest/_state/source_health.json"]
    if check is not None and persist < check:
        out.append("finalize persists the counter before checking it")
    if steps[persist].get("continue-on-error"):
        out.append("the persist step must not be continue-on-error")
    if "if" in steps[persist]:
        out.append("the persist step must be unconditional")
    return out


def test_refresh_job_never_touches_the_counters_and_finalize_is_the_single_writer():
    assert problems(WF.read_text(encoding="utf-8")) == []


def _doc():
    return yaml.safe_load(WF.read_text(encoding="utf-8"))


def test_each_mutation_makes_the_check_fail():
    # 1. a source-health step creeps back into the refresh job
    doc = _doc()
    doc["jobs"]["refresh"]["steps"].insert(
        5, {"name": "x", "run": "python scripts/check_source_health.py --outcomes-json {}"})
    assert any("touches the refresh-state counters" in p for p in problems(yaml.safe_dump(doc)))
    # 2. the skip-probe cursor is restored in the refresh job
    doc = _doc()
    doc["jobs"]["refresh"]["steps"].insert(
        5, {"name": "y", "run": "git show origin/refresh-state:ingest/_state/skip_probe_state.json"})
    assert any("touches the refresh-state counters" in p for p in problems(yaml.safe_dump(doc)))
    # 3. a second writer: the OECD job persists
    doc = _doc()
    doc["jobs"]["oecd-fetch"]["steps"].append(
        {"name": "z", "run": "bash scripts/persist_refresh_state.sh u f d"})
    assert any("only writer" in p for p in problems(yaml.safe_dump(doc)))
    # 4. finalize: persist before check
    doc = _doc()
    steps = doc["jobs"]["finalize"]["steps"]
    pi = next(i for i, s in enumerate(steps) if "persist_refresh_state.sh" in s.get("run", "")
              and "source_health.json" in s["run"])
    ci = next(i for i, s in enumerate(steps) if "check_source_health.py" in s.get("run", ""))
    steps.insert(ci, steps.pop(pi))
    assert any("before checking" in p for p in problems(yaml.safe_dump(doc)))
    # 5. conditional / continue-on-error persist
    doc = _doc()
    doc["jobs"]["finalize"]["steps"][pi]["if"] = "false"
    assert any("unconditional" in p for p in problems(yaml.safe_dump(doc)))
    doc = _doc()
    doc["jobs"]["finalize"]["steps"][pi]["continue-on-error"] = True
    assert any("continue-on-error" in p for p in problems(yaml.safe_dump(doc)))
    # 6. persist removed from finalize
    doc = _doc()
    del doc["jobs"]["finalize"]["steps"][pi]
    assert any("does not persist" in p for p in problems(yaml.safe_dump(doc)))
