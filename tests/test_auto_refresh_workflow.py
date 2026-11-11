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

REFRESH_MEASURED_NEED_MIN = 15   # tests 10.8 (CI-measured) + other ~4.5
OECD_MEASURED_MIN = 51           # 2026-10-18 / 10-25
OECD_JOB_OTHER_MIN = 3           # install + restore + probe + stash + uploads
TESTS_MEASURED_MIN = 10.8        # CI-measured: Validate on main, run 40921156247, py3.12 (was 7.6 on 10-25)
HEADROOM = 1.5
OTHER_MEASURED_MIN = 4.5         # refresh job total minus tests (63 - 50.8 OECD - 7.6 tests on 10-25, rounded up)
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
    """Budget arithmetic for the refresh, oecd-fetch and finalize jobs.

    NOT checked, because it cannot be known offline (A1): whether the finalize
    job's `!cancelled()` still runs after a NEEDED job hits its job-level
    timeout. On 2026-10-25 a job-level timeout skipped even always() steps and
    the run concluded "cancelled". If so, a job-level timeout of oecd-fetch or
    refresh means finalize (counter, cursor persist) does not run that week.
    The step caps below exist so a hang fails at its step first; the job caps
    are only backstops. Unverified until a needed job actually hits its job-level
    timeout; no scheduled or dispatched run exercises this (no live dispatch, D148-2).
    """
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


# ---------------------------------------------------------------------------
# Independent CI for the refresh PR. A PR opened with GITHUB_TOKEN does not
# trigger pull_request workflows (runs stay action_required), so the refresh job
# dispatches them (workflow_dispatch is the documented GITHUB_TOKEN exception).

DISPATCHED = ("validate.yml", "a11y.yml")
WF_DIR = WORKFLOW.parent


def strip_shell_comments(text: str) -> str:
    """Drop `# ...` comments (own-line and trailing) from shell text, honouring quotes,
    so substring checks cannot be satisfied by a comment."""
    out = []
    for line in text.splitlines():
        quote = None
        cut = len(line)
        for i, ch in enumerate(line):
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "#" and (i == 0 or line[i - 1].isspace()):
                cut = i
                break
        out.append(line[:cut])
    return chr(10).join(out)


def check_ci_dispatch(text: str, validate_text: str, a11y_text: str) -> list[str]:
    import yaml

    problems = []
    jobs = yaml.safe_load(text)["jobs"]
    refresh = jobs["refresh"]
    top = yaml.safe_load(text)
    # a string value (write-all, read-all, ...) is a violation: it grants every scope,
    # including actions, and `"actions" in "write-all"` is False
    for label, perms in (("the refresh job", refresh.get("permissions")), ("the workflow level", top.get("permissions"))):
        if perms is not None and not isinstance(perms, dict):
            problems.append(f"{label} permissions must be a mapping, not {perms!r}")
        elif "actions" in (perms or {}):
            problems.append(f"{label} must not hold an actions permission")
    if "steps.cpr.outputs.pull-request-number" not in str((refresh.get("outputs") or {}).get("pr_number", "")):
        problems.append("refresh must expose outputs.pr_number from the cpr step")
    # whole-workflow rule: ONLY dispatch-pr-ci may hold an actions permission, and no
    # other job may carry a string permission (write-all) that implies one
    for name, j in jobs.items():
        if name in ("refresh", "dispatch-pr-ci"):
            continue  # refresh is checked above; dispatch-pr-ci is checked exactly below
        jp = j.get("permissions")
        if jp is not None and not isinstance(jp, dict):
            problems.append(f"job {name} permissions must be a mapping, not {jp!r}")
        elif "actions" in (jp or {}):
            problems.append(f"job {name} must not hold an actions permission (only dispatch-pr-ci may)")
    job = jobs.get("dispatch-pr-ci")
    if job is None:
        return problems + ["no dispatch-pr-ci job"]
    if job.get("needs") != "refresh":
        problems.append("dispatch job must need refresh")
    cond = str(job.get("if", "")).strip()
    cond = re.sub(r"^\$\{\{|\}\}$", "", cond).strip()
    terms = [t.strip() for t in cond.split("&&")]
    if "||" in cond:
        problems.append("dispatch job if: must be a pure AND (an OR lets it run without a PR)")
    if "needs.refresh.outputs.pr_number != ''" not in terms:
        problems.append("dispatch job must be guarded on a non-empty pr_number")
    if "!cancelled()" not in terms:
        problems.append("dispatch job if: needs !cancelled() (implicit success() would skip it when cve-sweep fails)")
    if job.get("permissions") != {"actions": "write"}:
        problems.append("dispatch job permissions must be exactly actions: write")
    if not job.get("timeout-minutes"):
        problems.append("dispatch job needs timeout-minutes")
    steps = job["steps"]
    if any("uses" in s for s in steps):
        problems.append("dispatch job must have no uses: steps (no checkout, no third-party action)")
    run = strip_shell_comments(chr(10).join(s.get("run", "") for s in steps))
    if "gh workflow run" not in run:
        problems.append("dispatch job does not run `gh workflow run`")
    elif any(not re.match("[ " + BS + "t]*gh workflow run" + BS + "b", ln) for ln in run.splitlines() if "gh workflow run" in ln):
        # conservative and lexical: every line naming the command must START with it
        problems.append("`gh workflow run` must be at command position (line must start with the command)")
        problems.append("`gh workflow run` must be at command position (no echo/:/printf/true prefix)")
    for wf in DISPATCHED:
        if wf not in run:
            problems.append(f"{wf} not in the dispatch loop")
    if '-R "$GITHUB_REPOSITORY"' not in run:
        problems.append('dispatch must pass -R "$GITHUB_REPOSITORY" (no checkout, so gh has no repo context)')
    for s_ in steps:
        if "gh workflow run" in s_.get("run", ""):
            tok = str((s_.get("env") or {}).get("GH_TOKEN", "")).strip()
            if not re.fullmatch(r"[$][{][{]\s*(github[.]token|secrets[.]GITHUB_TOKEN)\s*[}][}]", tok):
                problems.append("the dispatch step GH_TOKEN must be exactly ${{ github.token }} or ${{ secrets.GITHUB_TOKEN }}")
    if "--ref auto-refresh/data" not in run:
        problems.append("dispatch must target --ref auto-refresh/data")
    if '|| echo "::warning::' not in run:
        problems.append("a failed dispatch must warn, not fail")
    if not all(s.get("continue-on-error") is True for s in steps):
        problems.append("dispatch steps must be continue-on-error")
    for name, j in jobs.items():
        if "dispatch-pr-ci" in (j.get("needs") if isinstance(j.get("needs"), list) else [j.get("needs")]):
            problems.append(f"{name} must not depend on dispatch-pr-ci")
    for label, body in (("validate.yml", validate_text), ("a11y.yml", a11y_text)):
        if "workflow_dispatch" not in (yaml.safe_load(body).get(True) or {}):  # PyYAML parses `on` as True
            problems.append(f"{label} has no workflow_dispatch trigger")
    remerge = strip_shell_comments(validate_text.split("Re-merge from ingest sources", 1)[1].split("Validate incidents.json", 1)[0])
    if '"$EVENT_NAME" = "workflow_dispatch"' not in remerge:
        problems.append("validate.yml re-merge baseline does not handle workflow_dispatch (would fail closed)")
    else:
        branch = remerge.split('"$EVENT_NAME" = "workflow_dispatch"', 1)[1].split("else", 1)[0]
        if "origin/main" not in branch or not re.search(r"base=.*origin/main", branch):
            problems.append("the workflow_dispatch baseline must be assigned from origin/main")
        if "exit 1" not in branch:
            problems.append("the workflow_dispatch baseline must fail closed (exit 1)")
    return problems


def test_refresh_dispatches_independent_ci():
    v = (WF_DIR / "validate.yml").read_text(encoding="utf-8")
    a = (WF_DIR / "a11y.yml").read_text(encoding="utf-8")
    assert check_ci_dispatch(WORKFLOW.read_text(encoding="utf-8"), v, a) == []


def test_ci_dispatch_check_fires():
    nl = chr(10)
    good = WORKFLOW.read_text(encoding="utf-8").replace(chr(13) + nl, nl)
    v = (WF_DIR / "validate.yml").read_text(encoding="utf-8")
    a = (WF_DIR / "a11y.yml").read_text(encoding="utf-8")

    def fires(text, needle):
        assert any(needle in p for p in check_ci_dispatch(text, v, a)), needle

    marker = "    needs: cve-sweep" + nl
    assert marker in good
    fires(good.replace(marker, marker + "    permissions:" + nl + "      actions: write" + nl, 1), "must not hold an actions")
    fires(good.replace("gh workflow run", "gh echo"), "gh workflow run")
    fires(good.replace("    if: ${{ !cancelled() && needs.refresh.outputs.pr_number != '' }}" + nl, ""), "guarded")
    perm = "    permissions:" + nl + "      actions: write" + nl
    assert perm in good
    fires(good.replace(perm, perm + "      contents: read" + nl, 1), "exactly actions: write")
    step = "      - name: Dispatch validate and a11y on the refresh branch" + nl
    assert step in good
    fires(good.replace(step, "      - uses: actions/checkout@v6" + nl + step, 1), "no uses")
    fires(good.replace(' || echo "::warning::could not dispatch', " # could not dispatch"), "warn")
    fires(good.replace("      pr_number: ${{ steps.cpr.outputs.pull-request-number }}" + nl, ""), "pr_number")
    fires(good.replace("    needs: [refresh, oecd-fetch]" + nl, "    needs: [refresh, oecd-fetch, dispatch-pr-ci]" + nl), "must not depend")
    fires(good.replace("if: ${{ !cancelled() && needs.refresh", "if: ${{ needs.refresh"), "!cancelled()")
    # string permissions (write-all) at the refresh job and at the workflow level
    fires(good.replace(marker, marker + "    permissions: write-all" + nl, 1), "must be a mapping")
    top = "permissions:" + nl + "  contents: write" + nl + "  pull-requests: write" + nl
    assert top in good
    fires(good.replace(top, "permissions: write-all" + nl, 1), "must be a mapping")
    fires(good.replace(top, "permissions: read-all" + nl, 1), "must be a mapping")
    fires(good.replace(' -R "$GITHUB_REPOSITORY"', "", 1), "GITHUB_REPOSITORY")
    tok = "        env:" + nl + "          GH_TOKEN: ${{ github.token }}" + nl + "        run: |" + nl + "          for wf"
    assert tok in good
    fires(good.replace(tok, "        run: |" + nl + "          for wf", 1), "GH_TOKEN")
    # validate.yml baseline mutations
    assert any("workflow_dispatch" in p for p in check_ci_dispatch(good, v.replace("  workflow_dispatch:" + nl, ""), a))
    assert any("workflow_dispatch" in p for p in check_ci_dispatch(good, v, a.replace("  workflow_dispatch:" + nl, "")))
    vn = v.replace(chr(13) + nl, nl)
    vbase = "base=" + chr(34) + "$(git rev-parse --verify --quiet 'origin/main^{commit}')" + chr(34)
    assert vbase in vn
    assert any("origin/main" in p for p in check_ci_dispatch(good, vn.replace(vbase, 'base="HEAD"', 1), a))
    vexit = "exit 1" + nl + "            }" + nl
    assert vexit in vn
    assert any("fail closed" in p for p in check_ci_dispatch(good, vn.replace(vexit, ":" + nl + "            }" + nl, 1), a))
    assert any("workflow_dispatch" in p for p in check_ci_dispatch(good, vn.replace('"$EVENT_NAME" = "workflow_dispatch"', '"$EVENT_NAME" = "other"'), a))


# ---- threshold <-> PR-warning text -------------------------------------------------
SOURCE_HEALTH = Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"
BS = chr(92)


def check_threshold_text(workflow_text: str, health_text: str) -> list[str]:
    """The PR warning says "failed N weeks running". N must equal the effective
    consecutive-failure threshold (the --threshold the workflow passes to
    check_source_health.py, else its DEFAULT_THRESHOLD) and the cron must be weekly,
    otherwise one failed refresh is not one week."""
    import yaml

    problems = []
    said = re.findall(r"failed (\d+) weeks running", workflow_text)
    if len(said) != 1:
        return [f"expected exactly one 'failed N weeks running' sentence, found {len(said)}"]
    d = re.search(r"(?m)^DEFAULT_THRESHOLD\s*=\s*(\d+)", health_text)
    if not d:
        return ["DEFAULT_THRESHOLD not found in check_source_health.py"]
    call = re.search(r"python scripts/check_source_health[.]py((?:[^\n]*" + re.escape(BS) + r"\n)*[^\n]*)", workflow_text)
    if not call:
        return ["workflow does not invoke check_source_health.py"]
    passed = re.search(r"--threshold[ =](\d+)", call.group(1))
    effective = int(passed.group(1)) if passed else int(d.group(1))
    if int(said[0]) != effective:
        problems.append(f"PR text says {said[0]} weeks but the effective threshold is {effective}")
    crons = [c["cron"] for c in (yaml.safe_load(workflow_text).get(True) or {}).get("schedule", [])]
    if len(crons) != 1:
        problems.append(f"expected one cron entry, found {len(crons)}")
    else:
        f = crons[0].split()
        if not (len(f) == 5 and f[2] == "*" and f[3] == "*" and re.fullmatch(r"[0-6]", f[4])):
            problems.append(f"cron {crons[0]!r} is not weekly, so 'N weeks' != N consecutive failures")
    return problems


def test_pr_text_weeks_match_effective_threshold():
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert check_threshold_text(wf, SOURCE_HEALTH.read_text(encoding="utf-8")) == []


def test_threshold_text_check_fires():
    wf = WORKFLOW.read_text(encoding="utf-8").replace(chr(13) + chr(10), chr(10))
    h = SOURCE_HEALTH.read_text(encoding="utf-8")
    assert "DEFAULT_THRESHOLD = 3" in h and "failed 3 weeks running" in wf and 'cron: "0 4 * * 0"' in wf
    assert any("effective threshold" in p for p in check_threshold_text(wf.replace("failed 3 weeks", "failed 4 weeks"), h))
    assert any("effective threshold" in p for p in check_threshold_text(wf, h.replace("DEFAULT_THRESHOLD = 3", "DEFAULT_THRESHOLD = 2")))
    call = "python scripts/check_source_health.py " + BS + chr(10)
    assert call in wf
    pad = "            "
    assert any("effective threshold" in p for p in check_threshold_text(wf.replace(call, call + pad + "--threshold 5 " + BS + chr(10)), h))
    # an explicit threshold equal to the text is fine (control: the check is not just always-red)
    assert check_threshold_text(wf.replace(call, call + pad + "--threshold 3 " + BS + chr(10)), h) == []
    assert any("not weekly" in p for p in check_threshold_text(wf.replace('"0 4 * * 0"', '"0 4 * * *"'), h))


def test_ci_dispatch_check_fires_comment_or_and_token_and_new_job():
    """Gate advisories (a)-(d) on check_ci_dispatch: each mutation must produce a problem."""
    import yaml

    nl = chr(10)
    good = WORKFLOW.read_text(encoding="utf-8").replace(chr(13) + nl, nl)
    v = (WF_DIR / "validate.yml").read_text(encoding="utf-8").replace(chr(13) + nl, nl)
    a = (WF_DIR / "a11y.yml").read_text(encoding="utf-8")
    assert check_ci_dispatch(good, v, a) == []  # control: the unmutated pair is clean

    def fires(text, vt, needle):
        assert any(needle in p for p in check_ci_dispatch(text, vt, a)), needle

    # (a) OR in place of AND
    cond = "!cancelled() && needs.refresh.outputs.pr_number != ''"
    assert cond in good
    fires(good.replace(cond, "!cancelled() || needs.refresh.outputs.pr_number != ''"), v, "pure AND")
    # (M6) neutered command: a prefix token makes `gh workflow run` an argument, not a command
    gwr = 'gh workflow run "$wf"'
    assert good.count(gwr) == 1
    for prefix in ("echo ", ": ", "printf '%s' ", "true ", "cat <<< ", "echo do ", "echo then ", "echo " + BS + "; "):
        fires(good.replace(gwr, prefix + gwr), v, "command position")
    fires(good.replace(gwr, "echo '; " + gwr.replace(chr(34), "") + "'"), v, "command position")
    # (b) empty token
    tok = "GH_TOKEN: ${{ github.token }}" + nl + "        run: |" + nl + "          for wf"
    assert good.count(tok) == 1
    tail_ = nl + "        run: |" + nl + "          for wf"
    for bad in ('""', '"github.token"', "${{ secrets.PAT || github.token }}", "${{ github.token }}x"):
        fires(good.replace(tok, "GH_TOKEN: " + bad + tail_), v, "GH_TOKEN")
    assert check_ci_dispatch(good.replace(tok, "GH_TOKEN: ${{secrets.GITHUB_TOKEN}}" + tail_), v, a) == []  # tolerated forms stay clean
    # (c) text only in a comment
    loop = "for wf in validate.yml a11y.yml; do"
    assert loop in good
    fires(good.replace(loop, "for wf in validate.yml; do # a11y.yml"), v, "a11y.yml not in the dispatch loop")
    ref = ' --ref auto-refresh/data'
    assert ref in good
    fires(good.replace(ref, "", 1).replace(loop, "# --ref auto-refresh/data" + nl + "          " + loop), v, "--ref auto-refresh/data")
    vbase = "base=" + chr(34) + "$(git rev-parse --verify --quiet 'origin/main^{commit}')" + chr(34)
    assert vbase in v
    fires(good, v.replace(vbase, "base=HEAD # base=origin/main", 1), "origin/main")
    vexit = "exit 1" + nl + "            }" + nl
    assert vexit in v
    fires(good, v.replace(vexit, "# exit 1" + nl + "            }" + nl, 1), "fail closed")
    # (d) a new job holding actions: write, with a checkout
    extra = nl + "  sneaky:" + nl + "    runs-on: ubuntu-latest" + nl + "    permissions:" + nl + "      actions: write" + nl + "    steps:" + nl + "      - uses: actions/checkout@v6" + nl
    mutated = good.rstrip(nl) + nl + extra
    assert "sneaky" in yaml.safe_load(mutated)["jobs"]
    fires(mutated, v, "only dispatch-pr-ci may")
    fires(good.rstrip(nl) + nl + extra.replace("actions: write", "x: y").replace("    permissions:" + nl + "      x: y" + nl, "    permissions: write-all" + nl), v, "must be a mapping")


# ---- execute the workflow_dispatch / push / pull_request baseline shell block ------
def _baseline_script(validate_text: str) -> str:
    """The `run:` of validate.yml's re-merge step up to (excluding) the export, with the
    resolved baseline printed instead of running the python scripts."""
    import yaml

    steps = yaml.safe_load(validate_text)["jobs"]["validate"]["steps"]
    run = next(s["run"] for s in steps if s.get("name") == "Re-merge from ingest sources")
    head = run.split('export GENAI_OVERRIDE_BASELINE="$base"', 1)[0]
    return head + 'printf %s "$base"' + chr(10)


def _run_baseline(script: str, cwd, env_extra: dict):
    import os
    import subprocess

    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid", **env_extra}
    r = subprocess.run([_find_bash(), "-e", "-s"], input=script.encode(), cwd=cwd, env=env, capture_output=True)
    r.stdout = r.stdout.decode()  # bytes in/out: text mode would turn LF into CRLF on Windows and break bash
    return r


def _find_bash():
    """A bash that forwards the environment (on Windows `bash` on PATH is often WSL, which
    does not, so prefer the bash next to Git for Windows). None if there is no usable one."""
    import os
    import shutil
    import subprocess

    cands = []
    git = shutil.which("git")
    if git:
        root = os.path.dirname(os.path.dirname(git))
        cands += [os.path.join(root, "bin", "bash.exe"), os.path.join(root, "usr", "bin", "bash.exe")]
    cands.append(shutil.which("bash"))
    for c in cands:
        if not c or not os.path.exists(c):
            continue
        try:
            r = subprocess.run([c, "-c", 'echo "$GI_PROBE"; git --version'], capture_output=True, text=True,
                               timeout=30, env={**os.environ, "GI_PROBE": "ok"})
        except Exception:
            continue
        if r.returncode == 0 and r.stdout.startswith("ok"):
            return c
    return None


def _git_repo(path, with_origin_main: bool):
    import subprocess

    def g(*args):
        subprocess.run(["git", *args], cwd=path, check=True, capture_output=True,
                       env={**__import__("os").environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e.invalid",
                            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e.invalid"})

    g("init", "-q")
    for n in ("one", "two"):
        (path / n).write_text(n)
        g("add", n)
        g("-c", "commit.gpgsign=false", "commit", "-qm", n)
    if with_origin_main:
        g("update-ref", "refs/remotes/origin/main", "HEAD")
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True).stdout.strip()


def test_baseline_shell_block_executes(tmp_path):
    import pytest

    if _find_bash() is None:
        pytest.skip("no usable bash+git available")
    v = (WF_DIR / "validate.yml").read_text(encoding="utf-8").replace(chr(13) + chr(10), chr(10))
    script = _baseline_script(v)
    no_origin = tmp_path / "no_origin"
    with_origin = tmp_path / "with_origin"
    no_origin.mkdir()
    with_origin.mkdir()
    _git_repo(no_origin, False)
    tip = _git_repo(with_origin, True)

    # workflow_dispatch: fail closed without origin/main, resolve it with
    def fails_closed(sc):
        r_ = _run_baseline(sc, no_origin, {"EVENT_NAME": "workflow_dispatch", "PUSH_BEFORE": ""})
        return r_.returncode != 0 and "workflow_dispatch baseline" in r_.stdout

    assert fails_closed(script)
    r = _run_baseline(script, with_origin, {"EVENT_NAME": "workflow_dispatch", "PUSH_BEFORE": ""})
    assert r.returncode == 0 and r.stdout.strip() == tip, (r.returncode, r.stdout, r.stderr)

    # push: valid before-SHA resolves; empty / all-zero / unknown SHA fail closed
    first = __import__("subprocess").run(["git", "rev-parse", "HEAD^1"], cwd=with_origin, capture_output=True, text=True).stdout.strip()
    r = _run_baseline(script, with_origin, {"EVENT_NAME": "push", "PUSH_BEFORE": first})
    assert r.returncode == 0 and r.stdout.strip() == first, (r.returncode, r.stdout, r.stderr)
    for bad in ("", "0" * 40, "1" * 40):
        r = _run_baseline(script, with_origin, {"EVENT_NAME": "push", "PUSH_BEFORE": bad})
        assert r.returncode != 0 and "D141" in r.stdout, (bad, r.returncode, r.stdout)

    # pull_request: HEAD^1
    r = _run_baseline(script, with_origin, {"EVENT_NAME": "pull_request", "PUSH_BEFORE": ""})
    assert r.returncode == 0 and r.stdout == "HEAD^1"

    # m1 (`|| base=HEAD; true || {`) passed the old grep-based check; m2
    # (`exit 1` -> `true`) was already caught by it. Executing the block catches both.
    vbase = "base=" + chr(34) + "$(git rev-parse --verify --quiet 'origin/main^{commit}')" + chr(34) + " || {"
    assert vbase in script
    for mutated in (script.replace(vbase, vbase.replace(" || {", " || base=HEAD; true || {"), 1),
                    script.replace("exit 1", "true")):
        assert not fails_closed(mutated)  # the fail-open mutant is detected by the executed check
