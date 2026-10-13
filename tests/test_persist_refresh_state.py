"""Tests for scripts/persist_refresh_state.sh.

Regression coverage for the D5-impl bug that made every scheduled
`auto-refresh.yml` run fail at the "Persist source health counters to
refresh-state branch" step from 2026-07-26 through 2026-09-13 (8 runs):
`git clone --depth 1` implies `--single-branch`, so a bare `git fetch
origin refresh-state` (no destination refspec) only writes FETCH_HEAD --
it never populates `refs/remotes/origin/refresh-state` -- and the following
`git checkout -B refresh-state origin/refresh-state` dies with exit 128
("'origin/refresh-state' is not a commit ..."). The bug only shows up once
the `refresh-state` branch already exists on the remote, which is why it
slipped through review: the 2026-07-19 run that created the branch took the
`--orphan` path, never exercised this code, and failed later that same run
at the unrelated, intended "Enforce source health" step (AIRI stale) --
*not* here.

These tests build a fully local bare-repo fixture (file:// URL, no network)
covering all three states the step must handle:
  (a) `refresh-state` absent on the remote      -- the orphan path
  (b) `refresh-state` present, with a change     -- the buggy path (today)
  (c) `refresh-state` present, content unchanged -- the "left as-is" notice

Working agreement 6 ("a gate nobody has seen fail is a gate nobody should
cite"): test_case_b_fails_against_pre_fix_plain_fetch below mutates a COPY
of the actual on-disk script back to the pre-fix fetch/checkout lines,
asserting each replacement happened exactly once first, runs that copy
(not the git-plumbing steps re-derived by hand -- the script itself) against
the case-(b) fixture, and asserts it reproduces the exact exit-128 failure.
This is what proves the suite would have caught the regression: it fails
when the script's fix-carrying lines are gone, and only passes because the
real script on disk currently has them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "persist_refresh_state.sh"
STATE_REL_PATH = "ingest/_state/source_health.json"


def _find_bash() -> str | None:
    """On Windows, `shutil.which("bash")` frequently resolves to Git for
    Windows' `usr/bin/bash.exe` -- launched directly (bypassing the
    `bin/bash.exe` shim that sets up the MSYS runtime first), its own `/c/…`
    path translation is uninitialized and it can't find files by an
    otherwise-correct path, including its own script argument. Prefer the
    shim explicitly when present; elsewhere (Linux CI) a plain `which` is
    correct and sufficient."""
    for candidate in (r"C:\Program Files\Git\bin\bash.exe",):
        if Path(candidate).exists():
            return candidate
    return shutil.which("bash")


BASH = _find_bash()
pytestmark = pytest.mark.skipif(BASH is None, reason="no usable bash found")


def run(cmd, cwd, **kw):
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, check=False, **kw
    )


def git(*args, cwd):
    result = run(["git", *args], cwd=cwd)
    assert result.returncode == 0, (
        f"git {' '.join(args)} failed in {cwd}:\n{result.stdout}\n{result.stderr}"
    )
    return result.stdout


@pytest.fixture
def origin_repo(tmp_path):
    """A bare 'origin' repo with `main` carrying a large-ish blob, partial
    clones enabled (mirrors real GitHub's own upload-pack support)."""
    origin = tmp_path / "origin.git"
    git("init", "--quiet", "--bare", str(origin), cwd=tmp_path)
    git("config", "uploadpack.allowFilter", "true", cwd=origin)
    git("config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)

    seed = tmp_path / "seed"
    seed.mkdir()
    git("init", "--quiet", cwd=seed)
    git("config", "user.name", "tester", cwd=seed)
    git("config", "user.email", "tester@example.com", cwd=seed)
    # "Large-ish" blob so a real partial clone (--filter=blob:none) would
    # behave differently from a full clone -- not literally tens of MB
    # (that would make the suite slow), just big enough that the fixture
    # exercises the same clone/fetch mechanics as production.
    (seed / "bigfile.bin").write_bytes(b"\0" * (2 * 1024 * 1024))
    git("add", "bigfile.bin", cwd=seed)
    git("commit", "--quiet", "-m", "seed main", cwd=seed)
    git("branch", "-M", "main", cwd=seed)
    git("remote", "add", "origin", str(origin), cwd=seed)
    git("push", "--quiet", "origin", "main", cwd=seed)

    return origin


def seed_refresh_state(origin_repo, tmp_path, content: dict):
    """Pre-populate `refresh-state` on origin, simulating a prior run."""
    seed2 = tmp_path / "seed2"
    seed2.mkdir()
    git("init", "--quiet", cwd=seed2)
    git("config", "user.name", "tester", cwd=seed2)
    git("config", "user.email", "tester@example.com", cwd=seed2)
    git("checkout", "--quiet", "--orphan", "refresh-state", cwd=seed2)
    state_path = seed2 / STATE_REL_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(content), encoding="utf-8")
    git("add", STATE_REL_PATH, cwd=seed2)
    git("commit", "--quiet", "-m", "seed refresh-state", cwd=seed2)
    git("remote", "add", "origin", str(origin_repo), cwd=seed2)
    git("push", "--quiet", "origin", "refresh-state", cwd=seed2)


def refresh_state_sha(origin_repo, tmp_path):
    out = git("ls-remote", str(origin_repo), "refresh-state", cwd=tmp_path)
    return out.split()[0] if out.strip() else None


def read_remote_state_file(origin_repo, tmp_path, rel_path=STATE_REL_PATH):
    peek = tmp_path / "peek"
    if peek.exists():
        shutil.rmtree(peek)
    git("clone", "--quiet", "--branch", "refresh-state", "--single-branch",
        str(origin_repo), str(peek), cwd=tmp_path)
    return json.loads((peek / rel_path).read_text(encoding="utf-8"))


def make_workdir(tmp_path, name, content: dict):
    """A plain directory (not itself a git repo -- mirrors the fact that the
    script only reads/writes STATE_FILE relative to cwd) holding the state
    file the script should persist."""
    workdir = tmp_path / name
    state_path = workdir / STATE_REL_PATH
    state_path.parent.mkdir(parents=True)
    state_path.write_text(json.dumps(content), encoding="utf-8")
    return workdir


def to_posix(path) -> str:
    """Forward-slash form of a path for passing as argv to bash.exe: on
    Windows, a raw backslash path handed straight to bash's argv gets its
    backslashes eaten by the MSYS runtime's argv decoding (they're not
    translated like they are for args passed *through* a shell to a native
    exe) -- forward slashes are accepted by both bash and git on Windows and
    sidestep that entirely."""
    return str(path).replace("\\", "/")


def invoke_script(workdir, repo_url, clone_dir):
    return run(
        [BASH, to_posix(SCRIPT), to_posix(repo_url), STATE_REL_PATH, to_posix(clone_dir)],
        cwd=workdir,
    )


def test_case_a_refresh_state_absent_orphan_path(tmp_path, origin_repo):
    """(a) `refresh-state` does not exist yet -- must create it."""
    assert refresh_state_sha(origin_repo, tmp_path) is None
    main_sha_before = git("rev-parse", "main", cwd=origin_repo).strip()

    workdir = make_workdir(tmp_path, "work_a", {"airi_navigator": {"consecutive_failures": 1}})
    result = invoke_script(workdir, origin_repo.as_uri(), tmp_path / "clone_a")

    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert refresh_state_sha(origin_repo, tmp_path) is not None
    persisted = read_remote_state_file(origin_repo, tmp_path)
    assert persisted == {"airi_navigator": {"consecutive_failures": 1}}
    # main must be untouched by this step (origin_repo IS the remote itself,
    # so its own `main` ref is compared directly -- no fetch needed).
    assert git("rev-parse", "main", cwd=origin_repo).strip() == main_sha_before


def test_case_b_refresh_state_present_with_change(tmp_path, origin_repo):
    """(b) `refresh-state` exists and the counter changed -- this is the
    exact path that has been failing exit-128 in production since
    2026-07-19."""
    seed_refresh_state(origin_repo, tmp_path, {"airi_navigator": {"consecutive_failures": 1}})
    before_sha = refresh_state_sha(origin_repo, tmp_path)

    workdir = make_workdir(tmp_path, "work_b", {"airi_navigator": {"consecutive_failures": 2}})
    result = invoke_script(workdir, origin_repo.as_uri(), tmp_path / "clone_b")

    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    after_sha = refresh_state_sha(origin_repo, tmp_path)
    assert after_sha != before_sha, "refresh-state must advance when content changed"
    persisted = read_remote_state_file(origin_repo, tmp_path)
    assert persisted == {"airi_navigator": {"consecutive_failures": 2}}


def test_case_c_refresh_state_present_unchanged(tmp_path, origin_repo):
    """(c) `refresh-state` exists and the counter is IDENTICAL -- must leave
    the branch as-is (no empty commit, no force-push) and say so."""
    content = {"airi_navigator": {"consecutive_failures": 3}}
    seed_refresh_state(origin_repo, tmp_path, content)
    before_sha = refresh_state_sha(origin_repo, tmp_path)

    workdir = make_workdir(tmp_path, "work_c", content)
    result = invoke_script(workdir, origin_repo.as_uri(), tmp_path / "clone_c")

    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    after_sha = refresh_state_sha(origin_repo, tmp_path)
    assert after_sha == before_sha, "refresh-state must not move when content is unchanged"
    assert "unchanged this run" in result.stdout, result.stdout


FIXED_FETCH_LINE = "git fetch --quiet origin refresh-state:refs/remotes/origin/refresh-state"
FIXED_CHECKOUT_LINE = "git checkout -q -B refresh-state refs/remotes/origin/refresh-state"
PRE_FIX_FETCH_LINE = "git fetch --quiet origin refresh-state"
PRE_FIX_CHECKOUT_LINE = "git checkout -q -B refresh-state origin/refresh-state"


def test_case_b_fails_against_pre_fix_plain_fetch(tmp_path, origin_repo):
    """Working agreement 6 proof-of-fire. Mutates a COPY of the real,
    on-disk scripts/persist_refresh_state.sh back to the pre-fix
    fetch/checkout lines (plain `git fetch origin refresh-state` +
    `checkout -B refresh-state origin/refresh-state`, no destination
    refspec) and RUNS THAT SCRIPT COPY -- not a hand-written re-derivation
    of the git plumbing -- against the same case-(b) fixture used above.
    Asserts each line is present exactly once before swapping it, so a
    future edit to the script can't make this mutation silently a no-op
    (which would make this test pass for the wrong reason no matter what
    the script does). Never touches the real script file on disk."""
    script_text = SCRIPT.read_text(encoding="utf-8")
    assert script_text.count(FIXED_FETCH_LINE) == 1, (
        f"expected exactly one occurrence of the fixed fetch line in {SCRIPT}; "
        "the script changed -- update this mutation to match"
    )
    assert script_text.count(FIXED_CHECKOUT_LINE) == 1, (
        f"expected exactly one occurrence of the fixed checkout line in {SCRIPT}; "
        "the script changed -- update this mutation to match"
    )
    pre_fix_text = script_text.replace(
        FIXED_FETCH_LINE, PRE_FIX_FETCH_LINE, 1
    ).replace(
        FIXED_CHECKOUT_LINE, PRE_FIX_CHECKOUT_LINE, 1
    )

    pre_fix_script = tmp_path / "persist_refresh_state.pre-fix.sh"
    pre_fix_script.write_text(pre_fix_text, encoding="utf-8")
    pre_fix_script.chmod(0o755)

    seed_refresh_state(origin_repo, tmp_path, {"airi_navigator": {"consecutive_failures": 1}})
    workdir = make_workdir(tmp_path, "work_prefix", {"airi_navigator": {"consecutive_failures": 2}})

    result = run(
        [
            BASH,
            to_posix(pre_fix_script),
            to_posix(origin_repo.as_uri()),
            STATE_REL_PATH,
            to_posix(tmp_path / "clone_prefix"),
        ],
        cwd=workdir,
    )
    assert result.returncode == 128, (
        f"expected the pre-fix script copy to die exit 128; got {result.returncode}\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "is not a commit" in result.stderr, result.stderr

    # The real script on disk must be untouched by this test.
    assert SCRIPT.read_text(encoding="utf-8") == script_text


def test_manual_prefix_git_sequence_sanity_check(tmp_path, origin_repo):
    """NOT a regression guard -- does not invoke scripts/persist_refresh_state.sh
    at all, so it passes identically whether that script is fixed or broken;
    it only checks that the underlying git plumbing behaves the way this
    task's diagnosis says it does (plain `git fetch origin refresh-state`
    writes FETCH_HEAD only, and the following `checkout -B refresh-state
    origin/refresh-state` then dies exit 128). Kept as a small, separate,
    honestly-named sanity check of that claim; the actual proof-of-fire is
    test_case_b_fails_against_pre_fix_plain_fetch above, which runs the real
    script (mutated back to this same pre-fix form)."""
    seed_refresh_state(origin_repo, tmp_path, {"airi_navigator": {"consecutive_failures": 1}})

    clone_dir = tmp_path / "clone_sanity"
    git(
        "clone", "--quiet", "--depth", "1", "--filter=blob:none", "--no-checkout",
        origin_repo.as_uri(), str(clone_dir),
        cwd=tmp_path,
    )
    git("config", "user.name", "tester", cwd=clone_dir)
    git("config", "user.email", "tester@example.com", cwd=clone_dir)

    fetch = run(["git", "fetch", "--quiet", "origin", "refresh-state"], cwd=clone_dir)
    assert fetch.returncode == 0, "the fetch itself succeeds -- only writes FETCH_HEAD"

    checkout = run(
        ["git", "checkout", "-q", "-B", "refresh-state", "origin/refresh-state"],
        cwd=clone_dir,
    )
    assert checkout.returncode == 128, (
        f"expected the pre-fix sequence to die exit 128; got {checkout.returncode}\n"
        f"stdout={checkout.stdout}\nstderr={checkout.stderr}"
    )
    assert "is not a commit" in checkout.stderr, checkout.stderr


# ---------------------------------------------------------------------------
# followups b25: the `[skip ci]` commit marker and the `--force` push were
# untested. Tests only -- scripts/persist_refresh_state.sh is not modified.
# ---------------------------------------------------------------------------


def remote_tip_subject(origin_repo) -> str:
    return git("log", "-1", "--format=%s", "refresh-state", cwd=origin_repo).strip()


def test_state_commit_carries_skip_ci_marker(tmp_path, origin_repo):
    """A state-persist commit must say `[skip ci]` so the push to
    refresh-state never triggers a workflow run (both on the orphan-create
    path and the update path)."""
    workdir = make_workdir(tmp_path, "work_skip_a", {"n": 1})
    assert invoke_script(workdir, origin_repo.as_uri(), tmp_path / "clone_skip_a").returncode == 0
    assert remote_tip_subject(origin_repo).endswith("[skip ci]")

    workdir = make_workdir(tmp_path, "work_skip_b", {"n": 2})
    assert invoke_script(workdir, origin_repo.as_uri(), tmp_path / "clone_skip_b").returncode == 0
    assert remote_tip_subject(origin_repo).endswith("[skip ci]")


def test_skip_ci_check_fires_when_marker_removed(tmp_path, origin_repo):
    """Proof of fire for the marker test: a COPY of the script without
    ` [skip ci]` produces a tip subject the marker assertion would reject."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(" [skip ci]\"") == 1
    mutated = tmp_path / "persist_refresh_state.no-skip.sh"
    mutated.write_text(text.replace(" [skip ci]\"", "\"", 1), encoding="utf-8", newline="\n")
    workdir = make_workdir(tmp_path, "work_noskip", {"n": 1})
    result = run([BASH, to_posix(mutated), to_posix(origin_repo.as_uri()), STATE_REL_PATH,
                  to_posix(tmp_path / "clone_noskip")], cwd=workdir)
    assert result.returncode == 0, result.stderr
    assert not remote_tip_subject(origin_repo).endswith("[skip ci]")


def _make_racing_git_env(tmp_path, origin_repo):
    """Env that makes bash define a `git` wrapper function. On the script's `git push` it
    first advances origin's refresh-state with a DIFFERENT commit (prepared in
    a separate clone), so the script's own push is a non-fast-forward. Every
    other git invocation, and the push itself, pass through to the real git."""
    racer = tmp_path / "racer"
    git("clone", "--quiet", "--branch", "refresh-state", "--single-branch",
        origin_repo.as_uri(), str(racer), cwd=tmp_path)
    git("config", "user.name", "racer", cwd=racer)
    git("config", "user.email", "racer@example.com", cwd=racer)
    (racer / STATE_REL_PATH).write_text(json.dumps({"racer": "wrote first"}), encoding="utf-8")
    git("add", STATE_REL_PATH, cwd=racer)
    git("commit", "--quiet", "-m", "concurrent writer", cwd=racer)
    # A bash function (sourced via BASH_ENV) rather than a PATH shim: Git for
    # Windows' bash re-prepends /mingw64/bin to PATH, so a PATH shim never wins.
    shim = tmp_path / "git_race.sh"
    shim.write_text(
        "git() {\n"
        '  if [ "$1" = "push" ] && [ ! -e "$RACE_DONE" ]; then\n'
        '    : > "$RACE_DONE"\n'
        '    command git -C "$RACER" push --quiet origin HEAD:refresh-state || return 97\n'
        "  fi\n"
        '  command git "$@"\n'
        "}\n",
        encoding="utf-8", newline="\n")
    return {
        **os.environ,
        "BASH_ENV": to_posix(shim),
        "RACER": to_posix(racer),
        "RACE_DONE": to_posix(tmp_path / "race_done"),
    }


def _run_with_race(script_path, tmp_path, origin_repo, workdir, clone_name):
    env = _make_racing_git_env(tmp_path, origin_repo)
    return run([BASH, to_posix(script_path), to_posix(origin_repo.as_uri()), STATE_REL_PATH,
                to_posix(tmp_path / clone_name)], cwd=workdir, env=env)


def test_force_push_overwrites_a_non_fast_forward_refresh_state(tmp_path, origin_repo):
    """Non-fast-forward case: another writer advances refresh-state between the
    script's fetch and its push. The script's `--force` makes its push win
    (refresh-state is a single-writer scratch branch holding one counter file;
    last write wins). Checks the race really happened (the racer's commit is no
    longer reachable from the tip) and that the persisted content is the script's."""
    seed_refresh_state(origin_repo, tmp_path, {"n": 0})
    workdir = make_workdir(tmp_path, "work_force", {"n": 5})
    result = _run_with_race(SCRIPT, tmp_path, origin_repo, workdir, "clone_force")
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert (tmp_path / "race_done").exists(), "the racing writer never ran"
    assert read_remote_state_file(origin_repo, tmp_path) == {"n": 5}
    racer_sha = git("rev-parse", "HEAD", cwd=tmp_path / "racer").strip()
    tip = git("rev-parse", "refresh-state", cwd=origin_repo).strip()
    assert tip != racer_sha
    ancestor = run(["git", "merge-base", "--is-ancestor", racer_sha, tip], cwd=origin_repo)
    assert ancestor.returncode == 1, "racer commit is still reachable from the tip, so the push did not overwrite it (not a force-push)"


def test_non_fast_forward_test_fires_without_force(tmp_path, origin_repo):
    """Proof of fire for the test above: a COPY of the real script with
    `--force` removed must be REJECTED by the same race (non-fast-forward),
    exit non-zero, and leave the racer's content on origin. Asserts the
    mutation really removes exactly one `--force` first."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count("git push --force origin HEAD:refresh-state") == 1
    mutated = tmp_path / "persist_refresh_state.no-force.sh"
    mutated.write_text(text.replace("git push --force origin", "git push origin", 1),
                       encoding="utf-8", newline="\n")
    seed_refresh_state(origin_repo, tmp_path, {"n": 0})
    workdir = make_workdir(tmp_path, "work_noforce", {"n": 5})
    result = _run_with_race(mutated, tmp_path, origin_repo, workdir, "clone_noforce")
    assert result.returncode != 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert "rejected" in result.stderr or "non-fast-forward" in result.stderr, result.stderr
    assert read_remote_state_file(origin_repo, tmp_path) == {"racer": "wrote first"}
