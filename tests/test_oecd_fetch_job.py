"""D146-1 (2026-10-29): the OECD fetch lives in its own `oecd-fetch` job so the
refresh job is neither blocked nor bounded by it. Every duty the fetch step used
to serve inside the refresh job must still have its input. This file pins the
consumer inventory; each check has a mutated-workflow counter-case proving it
can fail (the mutations edit the parsed YAML and re-dump it).

Consumers of the OECD step's outputs/outcome/files, and where each lives now:

  1. D42 review artifact (held-oecd-aiid-inputs)   -> oecd-fetch: stash + upload
  2. skip-probe check (--check-probe) + enforcement -> oecd-fetch
  3. skip-probe rotation cursor restore             -> oecd-fetch (before the fetch)
  4. skip-probe cursor persist to refresh-state     -> finalize, via artifact
  5. source-health `oecd_aim` outcome               -> finalize, via job output
  6. ingest summary / all-failed abort predicate    -> finalize "Abort check"
  7. D114 hold + guard (OECD pair inputs at HEAD)   -> refresh (unchanged)
"""

from __future__ import annotations

from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"


def _doc():
    return yaml.safe_load(WF.read_text(encoding="utf-8"))


def _idx(steps, pred):
    return next((i for i, s in enumerate(steps) if pred(s)), None)


def _runs(step):
    return str(step.get("run", ""))


def problems(doc: dict) -> list[str]:
    out = []
    jobs = doc["jobs"]
    refresh, oecd, fin = jobs["refresh"], jobs.get("oecd-fetch"), jobs.get("finalize")
    if oecd is None or fin is None:
        return ["oecd-fetch and finalize jobs must both exist"]

    # --- the fetch is NOT in the refresh job, and the refresh job is not blocked on it
    for s in refresh["steps"]:
        if "ingest_oecd_aim.py" in _runs(s):
            out.append(f"refresh job still runs ingest_oecd_aim.py ({s.get('name')!r})")
    needs = refresh.get("needs", [])
    needs = [needs] if isinstance(needs, str) else list(needs)
    if "oecd-fetch" in needs or "finalize" in needs:
        out.append("the refresh job must not need oecd-fetch/finalize (it would be blocked by the fetch)")
    if "steps.ingest_oecd" in str(refresh) or "needs.oecd-fetch" in str(refresh):
        out.append("a refresh-job step still reads the OECD step/job outcome")

    # --- oecd-fetch: fetch, restore-before-fetch, probe check + enforce, stash + upload, cursor upload
    os_ = oecd["steps"]
    fetch = _idx(os_, lambda s: s.get("id") == "ingest_oecd" and "scripts/ingest_oecd_aim.py" in _runs(s)
                 and "--check-probe" not in _runs(s))
    restore = _idx(os_, lambda s: "skip_probe_state.json" in _runs(s) and "refresh-state" in _runs(s))
    probe = _idx(os_, lambda s: s.get("id") == "skip_probe" and "--check-probe" in _runs(s))
    enforce = _idx(os_, lambda s: s.get("name") == "Enforce OECD skip-rule sampling probe")
    stash = _idx(os_, lambda s: "hold_pair_inputs.py --stash-dir" in _runs(s))
    up_held = _idx(os_, lambda s: (s.get("with") or {}).get("name") == "held-oecd-aiid-inputs")
    up_cursor = _idx(os_, lambda s: (s.get("with") or {}).get("name") == "oecd-skip-probe-state")
    for label, i in (("fetch step (id ingest_oecd)", fetch), ("cursor restore", restore),
                     ("probe check (id skip_probe)", probe), ("probe enforcement", enforce),
                     ("held-bytes stash", stash), ("held-bytes upload", up_held),
                     ("cursor upload", up_cursor)):
        if i is None:
            out.append(f"oecd-fetch lacks the {label}")
    if None in (fetch, restore, probe, enforce, stash, up_held, up_cursor):
        return out
    if not restore < fetch:
        out.append("the cursor must be restored BEFORE the fetch advances it")
    if not fetch < probe < stash < up_held:
        out.append("order must be fetch, probe check, stash, held upload")
    if not os_[fetch].get("continue-on-error"):
        out.append("the fetch step must be continue-on-error (failure is an outcome, not a job abort)")
    if "steps.ingest_oecd.outcome == 'success'" not in str(os_[probe].get("if", "")):
        out.append("the probe check must run only when the fetch succeeded")
    if not os_[probe].get("continue-on-error"):
        out.append("the probe check must be continue-on-error so the uploads still run")
    for label, i in (("stash", stash), ("held upload", up_held), ("cursor upload", up_cursor)):
        if "always()" not in str(os_[i].get("if", "")):
            out.append(f"the {label} step must run with always()")
    if "always()" not in str(os_[enforce].get("if", "")) or "steps.skip_probe.outcome == 'failure'" not in str(os_[enforce].get("if", "")):
        out.append("probe enforcement must be always() and keyed on steps.skip_probe.outcome == 'failure'")
    if "exit 1" not in _runs(os_[enforce]):
        out.append("probe enforcement must exit 1")
    if "runner.temp" not in str(os_[up_held]):
        out.append("the held-bytes upload must read from runner.temp, not the work tree")
    if oecd.get("outputs", {}).get("oecd_outcome") != "${{ steps.ingest_oecd.outcome }}":
        out.append("oecd-fetch must export the fetch STEP outcome (the job result would hide a failure)")
    if (oecd.get("permissions") or {}).get("contents") != "read":
        out.append("oecd-fetch must not hold write scope")

    # --- finalize: waits for both, runs even if either failed, and consumes each hand-off
    fneeds = fin.get("needs", [])
    if not {"refresh", "oecd-fetch"} <= set([fneeds] if isinstance(fneeds, str) else fneeds):
        out.append("finalize must need both refresh and oecd-fetch")
    if "cancelled()" not in str(fin.get("if", "")) and "always()" not in str(fin.get("if", "")):
        out.append("finalize must run even when an upstream job failed")
    fs = fin["steps"]
    health = _idx(fs, lambda s: "check_source_health.py" in _runs(s))
    if health is None:
        return out + ["finalize lacks the source-health check"]
    h = fs[health]
    if "needs.oecd-fetch.outputs.oecd_outcome" not in str(h.get("env", {}).get("OECD")):
        out.append("source health must read the OECD outcome from oecd-fetch's job output")
    if "'failure'" not in str(h["env"].get("OECD")):
        out.append("a missing OECD output (job died) must count as a failure")
    if '\\"oecd_aim\\": \\"$OECD\\"' not in _runs(h):
        out.append("source health outcomes-json must still include oecd_aim")
    dl = _idx(fs, lambda s: (s.get("with") or {}).get("name") == "oecd-skip-probe-state")
    pp = _idx(fs, lambda s: "persist_refresh_state.sh" in _runs(s) and "skip_probe_state.json" in _runs(s))
    if dl is None or pp is None or not dl < pp:
        out.append("finalize must download the cursor artifact and then persist skip_probe_state.json")
    ab = _idx(fs, lambda s: "needs.oecd-fetch.outputs.oecd_outcome" in str(s.get("env", {}))
              and "Every source refresh failed" in _runs(s))
    if ab is None:
        out.append("finalize lacks the all-sources-failed abort predicate on the OECD outcome")
    elif "always()" not in str(fs[ab].get("if", "")):
        out.append("the abort check must run with always()")

    # --- the refresh job's D114 hold + guard are untouched
    rs = refresh["steps"]
    hold = _idx(rs, lambda s: "hold_pair_inputs.py --stash-dir" in _runs(s))
    merge = _idx(rs, lambda s: "merge_and_dedupe.py" in _runs(s))
    guard = _idx(rs, lambda s: "hold_pair_inputs.py --check-clean" in _runs(s))
    if hold is None or merge is None or not hold < merge:
        out.append("the refresh job must still hold the pair inputs before the merge (D114)")
    if guard is None:
        out.append("the refresh job must still run the --check-clean guard before the PR")
    # the artifact names must not collide (upload-artifact v4 fails on a duplicate)
    names = [(s.get("with") or {}).get("name") for j in jobs.values() for s in j.get("steps", [])
             if "upload-artifact" in str(s.get("uses", ""))]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        out.append(f"duplicate artifact names across jobs: {sorted(dup)}")
    return out


def test_oecd_fetch_is_its_own_job_and_every_consumer_still_has_its_input():
    assert problems(_doc()) == []


def _mutate(fn):
    doc = _doc()
    fn(doc)
    return problems(yaml.safe_load(yaml.safe_dump(doc)))


def _step(doc, job, pred):
    steps = doc["jobs"][job]["steps"]
    return steps, next(i for i, s in enumerate(steps) if pred(s))


def test_each_consumer_check_fires():
    def fetch_back(d):  # fetch step copied back into the refresh job
        _, i = _step(d, "oecd-fetch", lambda s: s.get("id") == "ingest_oecd")
        d["jobs"]["refresh"]["steps"].insert(5, dict(d["jobs"]["oecd-fetch"]["steps"][i]))
    assert any("still runs ingest_oecd_aim.py" in p for p in _mutate(fetch_back))

    def blocked(d):
        d["jobs"]["refresh"]["needs"] = ["cve-sweep", "oecd-fetch"]
    assert any("blocked by the fetch" in p for p in _mutate(blocked))

    def refresh_reads_outcome(d):
        d["jobs"]["refresh"]["steps"][5]["env"] = {"X": "${{ steps.ingest_oecd.outcome }}"}
    assert any("still reads the OECD" in p for p in _mutate(refresh_reads_outcome))

    def no_enforce(d):
        steps, i = _step(d, "oecd-fetch", lambda s: s.get("name") == "Enforce OECD skip-rule sampling probe")
        steps[i]["if"] = "steps.skip_probe.outcome == 'failure'"
    assert any("always()" in p for p in _mutate(no_enforce))

    def cursor_after_fetch(d):
        steps, r = _step(d, "oecd-fetch", lambda s: "skip_probe_state.json" in str(s.get("run", ""))
                         and "refresh-state" in str(s.get("run", "")))
        steps.append(steps.pop(r))
    assert any("BEFORE the fetch" in p or "order must be" in p for p in _mutate(cursor_after_fetch))

    def drop_cursor_upload(d):
        steps, i = _step(d, "oecd-fetch", lambda s: (s.get("with") or {}).get("name") == "oecd-skip-probe-state")
        del steps[i]
    assert any("cursor upload" in p for p in _mutate(drop_cursor_upload))

    def drop_held_upload(d):
        steps, i = _step(d, "oecd-fetch", lambda s: (s.get("with") or {}).get("name") == "held-oecd-aiid-inputs")
        del steps[i]
    assert any("held-bytes upload" in p for p in _mutate(drop_held_upload))

    def health_ignores_oecd(d):
        steps, i = _step(d, "finalize", lambda s: "check_source_health.py" in str(s.get("run", "")))
        steps[i]["env"]["OECD"] = "success"
    assert any("job output" in p for p in _mutate(health_ignores_oecd))

    def missing_output_is_success(d):
        steps, i = _step(d, "finalize", lambda s: "check_source_health.py" in str(s.get("run", "")))
        steps[i]["env"]["OECD"] = "${{ needs.oecd-fetch.outputs.oecd_outcome }}"
    assert any("must count as a failure" in p for p in _mutate(missing_output_is_success))

    def job_result_not_step(d):
        d["jobs"]["oecd-fetch"]["outputs"]["oecd_outcome"] = "${{ job.status }}"
    assert any("STEP outcome" in p for p in _mutate(job_result_not_step))

    def finalize_not_waiting(d):
        d["jobs"]["finalize"]["needs"] = ["refresh"]
    assert any("need both" in p for p in _mutate(finalize_not_waiting))

    def no_persist_cursor(d):
        steps, i = _step(d, "finalize", lambda s: "skip_probe_state.json" in str(s.get("run", ""))
                         and "persist_refresh_state.sh" in str(s.get("run", "")))
        del steps[i]
    assert any("persist skip_probe_state.json" in p for p in _mutate(no_persist_cursor))

    def hold_removed(d):
        steps, i = _step(d, "refresh", lambda s: "hold_pair_inputs.py --stash-dir" in str(s.get("run", "")))
        del steps[i]
    assert any("D114" in p for p in _mutate(hold_removed))

    def guard_removed(d):
        steps, i = _step(d, "refresh", lambda s: "--check-clean" in str(s.get("run", "")))
        del steps[i]
    assert any("--check-clean" in p for p in _mutate(guard_removed))

    def dup_artifact(d):
        steps, i = _step(d, "refresh", lambda s: "hold_pair_inputs.py --stash-dir" in str(s.get("run", "")))
        up = next(s for s in d["jobs"]["refresh"]["steps"] if "upload-artifact" in str(s.get("uses", ""))
                  and "held" in str((s.get("with") or {}).get("name")))
        up["with"]["name"] = "held-oecd-aiid-inputs"
    assert any("duplicate artifact names" in p for p in _mutate(dup_artifact))


# ---- gate-d146 bounce 1: the refresh -> finalize hand-off and the refresh-state writer ----


def handoff_problems(doc: dict) -> list[str]:
    out = []
    jobs = doc["jobs"]
    refresh, oecd, fin = jobs["refresh"], jobs["oecd-fetch"], jobs["finalize"]
    # M1: the refresh job must export the outcomes finalize feeds to the health counter
    outs = refresh.get("outputs") or {}
    for k, step_id in (("aiaaic_outcome", "ingest_aiaaic"), ("kev_outcome", "ingest_kev")):
        if outs.get(k) != "${{ steps.%s.outcome }}" % step_id:
            out.append(f"refresh output {k} must be the STEP outcome of {step_id}")
    # M2: parse the exact expression, not a substring
    if str(fin.get("if", "")).strip() != "${{ !cancelled() }}":
        out.append("finalize must run with exactly `${{ !cancelled() }}`")
    # M3: every hand-off value finalize reads must default to failure
    seen = 0
    for s in fin["steps"]:
        for k, v in (s.get("env") or {}).items():
            v = str(v)
            if "needs." in v and ".outputs." in v:
                seen += 1
                if not v.rstrip().rstrip("}").rstrip().endswith("|| 'failure'"):
                    out.append(f"finalize env {k} reads a job output without `|| 'failure'`: {v}")
    if seen < 5:  # health: AIAAIC, OECD, KEV; abort check: AIAAIC, OECD
        out.append(f"finalize reads only {seen} job outputs; expected the 5 hand-offs")
    # M4: no raw push to refresh-state (or any push) outside finalize
    for jn, job in jobs.items():
        for s in job.get("steps", []):
            r = str(s.get("run", ""))
            if jn != "finalize" and ("git push" in r or "persist_refresh_state.sh" in r):
                out.append(f"job {jn!r} step {s.get('name')!r} pushes; finalize must be the only writer")
    # M5: the cursor download must not fail the job when the artifact is missing
    dl = next((s for s in fin["steps"] if (s.get("with") or {}).get("name") == "oecd-skip-probe-state"), None)
    if dl is None or dl.get("continue-on-error") is not True:
        out.append("the cursor download must be continue-on-error (no artifact is a normal week)")
    # M6: a missing cursor file (nothing skipped) must not fail the upload
    up = next((s for s in oecd["steps"] if (s.get("with") or {}).get("name") == "oecd-skip-probe-state"), None)
    if up is None or (up.get("with") or {}).get("if-no-files-found") != "ignore":
        out.append("the cursor upload must be if-no-files-found: ignore")
    return out


def test_handoff_from_refresh_and_oecd_to_finalize_is_pinned():
    assert handoff_problems(_doc()) == []


def test_handoff_checks_fire():
    def mut(fn):
        doc = _doc()
        fn(doc)
        return handoff_problems(yaml.safe_load(yaml.safe_dump(doc)))

    def fin_steps(d):
        return d["jobs"]["finalize"]["steps"]

    def health(d):
        return next(s for s in fin_steps(d) if "check_source_health.py" in str(s.get("run", "")))

    # M1: refresh outputs deleted
    assert mut(lambda d: d["jobs"]["refresh"].pop("outputs"))
    assert mut(lambda d: d["jobs"]["refresh"]["outputs"].pop("kev_outcome"))
    # M2: finalize `if: cancelled()` (the substring the old check accepted)
    assert mut(lambda d: d["jobs"]["finalize"].__setitem__("if", "${{ cancelled() }}"))
    assert mut(lambda d: d["jobs"]["finalize"].pop("if"))
    # M3: AIAAIC / KEV defaults dropped (health step and abort step)
    assert mut(lambda d: health(d)["env"].__setitem__("AIAAIC", "${{ needs.refresh.outputs.aiaaic_outcome }}"))
    assert mut(lambda d: health(d)["env"].__setitem__("KEV", "${{ needs.refresh.outputs.kev_outcome }}"))
    abort = lambda d: next(s for s in fin_steps(d) if "Every source refresh failed" in str(s.get("run", "")))  # noqa: E731
    assert mut(lambda d: abort(d)["env"].__setitem__("AIAAIC", "${{ needs.refresh.outputs.aiaaic_outcome }}"))
    # M4: a raw git push to refresh-state in another job
    assert mut(lambda d: d["jobs"]["oecd-fetch"]["steps"].append(
        {"name": "p", "run": "git push --force origin HEAD:refresh-state"}))
    assert mut(lambda d: d["jobs"]["refresh"]["steps"].append(
        {"name": "p", "run": "git push origin HEAD:refresh-state"}))
    # M5: cursor download loses continue-on-error
    def m5(d):
        next(s for s in fin_steps(d) if (s.get("with") or {}).get("name") == "oecd-skip-probe-state").pop("continue-on-error")
    assert mut(m5)
    # M6: cursor upload fails when the file is absent
    def m6(d):
        next(s for s in d["jobs"]["oecd-fetch"]["steps"]
             if (s.get("with") or {}).get("name") == "oecd-skip-probe-state")["with"]["if-no-files-found"] = "error"
    assert mut(m6)


# ---- D147: the PR body warns at the TOP when the AIAAIC step did not succeed ----

WARN_STEP = "PR body warning - AIAAIC refresh failed"
WARN_FILE = "aiaaic-failed-warning.md"
WARN_TEXT = (
    "> **WARNING: the AIAAIC sheet refresh FAILED this week.** The AIAAIC data in this PR is last week's. The other sources (KEV, CVE sweep, AIID, retractions) refreshed separately; check this run's summary for their outcomes before merging. An AIAAIC failure turns the run red only once it has failed 3 weeks running or OECD also failed this week; other checks can turn it red for their own reasons."
)


def warning_problems(doc: dict) -> list[str]:
    out = []
    steps = doc["jobs"]["refresh"]["steps"]
    wi = _idx(steps, lambda s: s.get("name") == WARN_STEP)
    bi = _idx(steps, lambda s: s.get("id") == "retracted")
    if wi is None or bi is None:
        return ["missing the warning step or the PR-body step (id retracted)"]
    if not wi < bi:
        out.append("the warning step must run before the PR-body step")
    w = steps[wi]
    cond = str(w.get("if", ""))
    if "steps.ingest_aiaaic.outcome" not in cond or "!= 'success'" not in cond:
        out.append("the warning must be conditional on the refresh job's own AIAAIC outcome != success")
    if f'echo "{WARN_TEXT}"' not in str(w.get("run", "")):
        out.append("the warning step must echo EXACTLY the ruled text (D150)")
    if f'> "$RUNNER_TEMP/{WARN_FILE}"' not in str(w.get("run", "")):
        out.append("the warning file must be written under $RUNNER_TEMP, not the work tree (N3)")
    run = str(steps[bi].get("run", ""))
    first = run.find('cat "$RUNNER_TEMP/' + WARN_FILE + '" > "$RUNNER_TEMP/pr-body.md"')
    body = run.find("Automated weekly refresh of external sources.")
    if first < 0 or not first < run.find("<<'BODY'") < body:
        out.append("the PR-body step must start the body from the warning file, before the body text")
    if '2>/dev/null || : > "$RUNNER_TEMP/pr-body.md"' not in run:
        out.append("the PR-body step must fall back to an empty body when no warning file exists (N4)")
    if 'cat >> "$RUNNER_TEMP/pr-body.md" <<' not in run:
        out.append("the body text must APPEND, or it would overwrite the warning")
    return out


def test_pr_body_warns_at_the_top_when_aiaac_failed():
    assert warning_problems(_doc()) == []


def test_warning_checks_fire():
    def mut(fn):
        doc = _doc()
        steps = doc["jobs"]["refresh"]["steps"]
        fn(steps, next(s for s in steps if s.get("name") == WARN_STEP),
           next(s for s in steps if s.get("id") == "retracted"))
        return warning_problems(yaml.safe_load(yaml.safe_dump(doc)))

    # condition inverted: the warning would show on SUCCESS
    assert mut(lambda st, w, b: w.__setitem__("if", w["if"].replace("!=", "==")))
    # condition removed
    assert mut(lambda st, w, b: w.pop("if"))
    # wired to another step's outcome
    assert mut(lambda st, w, b: w.__setitem__("if", "${{ steps.ingest_kev.outcome != 'success' }}"))
    # warning step after the body step
    assert mut(lambda st, w, b: (st.remove(w), st.append(w)))
    # body text overwrites the warning
    assert mut(lambda st, w, b: b.__setitem__("run", b["run"].replace('cat >> "$RUNNER_TEMP/pr-body.md" <<', 'cat > "$RUNNER_TEMP/pr-body.md" <<', 1)))
    # body step does not start from the warning file
    assert mut(lambda st, w, b: b.__setitem__("run", b["run"].replace(WARN_FILE, "other.md", 1)))
    # warning text hollowed out
    assert mut(lambda st, w, b: w.__setitem__("run", w["run"].replace("check this run's summary", "x", 1)))
    # N4: the missing-file fallback deleted (every successful week would fail the step)
    assert mut(lambda st, w, b: b.__setitem__("run", b["run"].replace(' 2>/dev/null || : > "$RUNNER_TEMP/pr-body.md"', "", 1)))
    # N3: the warning file written into the work tree instead of $RUNNER_TEMP
    assert mut(lambda st, w, b: w.__setitem__("run", w["run"].replace('> "$RUNNER_TEMP/aiaaic-failed-warning.md"', '> aiaaic-failed-warning.md', 1)))


def test_pr_body_says_the_held_artifact_is_attached_by_the_oecd_job_and_may_come_later():
    text = WF.read_text(encoding="utf-8")
    body = text.split("Automated weekly refresh of external sources.", 1)[1].split("BODY", 1)[0]
    assert "held-oecd-aiid-inputs" in body
    flat = " ".join(body.split())
    assert "attached by the oecd-fetch job" in flat and "may appear after this PR opens" in flat
