#!/usr/bin/env bash
# scripts/persist_refresh_state.sh -- persist a small JSON state file (the
# WS4-T9 source-health counter) to the long-lived `refresh-state` branch via
# a throwaway, blobless clone, independent of the working tree that becomes
# the weekly data-review PR. Extracted out of .github/workflows/auto-refresh.yml's
# "Persist source health counters to refresh-state branch" step so it can be
# exercised by tests/test_persist_refresh_state.py without a live GitHub repo.
#
# This is CI/CD, GitHub-talking-to-GitHub-about-its-own-history, not
# ingestion of third-party corpus data -- see docs/INGESTION_CONDUCT.md's
# "Scoping note: excluded from this register" for why this `git clone` is
# not a registered non-HTTP-egress instance under invariant 5's register.
#
# Usage: persist_refresh_state.sh <repo-url> <state-file> <clone-dir>
#
#   <repo-url>   git remote to clone/push (may embed a token, e.g.
#                https://x-access-token:$TOKEN@github.com/owner/repo.git);
#                also accepts a local path or file:// URL for testing.
#   <state-file> path, relative to the CURRENT working directory (the repo
#                checkout the caller is running from), of the JSON file to
#                persist.
#   <clone-dir>  scratch directory for the throwaway clone. Removed before
#                use if it already exists, and removed again on a
#                successful run; on failure (the `set -e` below), it is
#                left behind -- same as before this extraction -- including
#                its `.git/config`, which embeds the token from <repo-url>
#                if the caller passed one that way. The workflow's runner
#                is torn down after each job regardless.
#
# Bug this fixes (regression since D5-impl, 2026-07-17; every scheduled run
# from 2026-07-26 through 2026-09-13 -- 8 runs -- failed here): `git clone
# --depth 1` implies --single-branch, so the clone's `remote.origin.fetch`
# refspec only tracks `main`. A plain `git fetch origin refresh-state` (no
# destination refspec) therefore writes FETCH_HEAD only -- it never
# populates `refs/remotes/origin/refresh-state` -- so the following
# `git checkout -B refresh-state origin/refresh-state` dies with "fatal:
# 'origin/refresh-state' is not a commit and a branch 'refresh-state' cannot
# be created from it" (exit 128). This never fired before D5-impl merged
# because the `refresh-state` branch didn't exist yet: the 2026-07-19 run
# took the `--orphan` path below (creating the branch), never exercised this
# code, and failed later that same run at the unrelated, intended "Enforce
# source health" step (AIRI stale) -- not here. Fixed by fetching into an
# explicit destination refspec, which is honored regardless of the clone's
# configured (single-branch) fetch refspec.
set -euo pipefail

REPO_URL="${1:?usage: persist_refresh_state.sh <repo-url> <state-file> <clone-dir>}"
STATE_FILE="${2:?usage: persist_refresh_state.sh <repo-url> <state-file> <clone-dir>}"
CLONE_DIR="${3:?usage: persist_refresh_state.sh <repo-url> <state-file> <clone-dir>}"

if [ ! -f "$STATE_FILE" ]; then
  echo "::error::$STATE_FILE not found; nothing to persist." >&2
  exit 1
fi

WORKSPACE="$(pwd)"
TMP_STATE="$(mktemp)"
cp "$STATE_FILE" "$TMP_STATE"
trap 'rm -f "$TMP_STATE"' EXIT

rm -rf "$CLONE_DIR"
# --filter=blob:none --no-checkout: this repo's data/*.json blobs are tens
# of MB; a partial, uncheckout'd clone fetches only commit/tree metadata up
# front, and (via the branches below) only the tiny refresh-state tree's
# blobs on demand -- not main's.
git clone --quiet --depth 1 --filter=blob:none --no-checkout "$REPO_URL" "$CLONE_DIR"
cd "$CLONE_DIR"
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

if git ls-remote --exit-code --heads origin refresh-state >/dev/null 2>&1; then
  # Explicit src:dst refspec -- honored even though this clone's configured
  # remote.origin.fetch is single-branch (main-only, from --depth above).
  # This is the fix: a bare `git fetch origin refresh-state` only writes
  # FETCH_HEAD and leaves refs/remotes/origin/refresh-state absent, which is
  # what made the following checkout fail (see the module docstring above).
  git fetch --quiet origin refresh-state:refs/remotes/origin/refresh-state
  git checkout -q -B refresh-state refs/remotes/origin/refresh-state
else
  git checkout -q --orphan refresh-state
  git rm -rf . >/dev/null 2>&1 || true
fi

mkdir -p "$(dirname "$STATE_FILE")"
cp "$TMP_STATE" "$STATE_FILE"
git add "$STATE_FILE"
if git diff --cached --quiet; then
  echo "::notice::$STATE_FILE unchanged this run; refresh-state left as-is."
else
  git commit -q -m "chore(state): update source health counters [skip ci]"
  git push --force origin HEAD:refresh-state
fi

cd "$WORKSPACE"
rm -rf "$CLONE_DIR"
