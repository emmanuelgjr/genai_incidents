# Repo cleanup plan (2026-10-13)

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4).
> - **Source:** a read-only clutter inventory (an Explore agent, scanned around 21:05 local on 2026-10-12, transcribed by the foreman).
> - **Status:** nothing has been deleted. Every deletion waits for the user's confirmation.
> - **Before acting:** re-run the classification commands, because agents were active during the scan.

## Inventory summary

| Category | SAFE | NEEDS-CONFIRM | NEEDS-RESCUE | KEEP |
|---|---|---|---|---|
| Worktrees (60 linked + 1 orphan dir; ~10-11 GB) | 54 | 4 | 1 (`C:/repos/gi-wt-decouple`, actively in use by the D66 repair) | 3 (main + 2 locked by a live session) |
| Local branches (142 now) | 130 merged, incl. 38 `worktree-agent-*` | 5 unmerged but pushed | 3 unpushed: `release/v2.10.0-cut`, `wip/cut-attempt2`, `docs/readme-refresh` (all look superseded) | main |
| Remote branches (81) | 72 merged | 6 unmerged | 0 | main, `refresh-state` (read by auto-refresh), `auto-refresh/data` (the refresh PR branch) |
| Ignored/generated files | `__pycache__`, `.pytest_cache`, stale `dist/` (31 MB, July) | `data/legacy_consolidated.json`, `ingest/_cache/` | — | `.claude/settings.local.json`, the generated site and STIX outputs |
| Temp scratch directories (~26 GB) | 1 tiny directory | ~13 GB of older sessions (about 95 nested clones; could hold unpushed commits) | — | the current session |
| Stashes | none | — | — | — |

**Unmerged remote branches (NEEDS-CONFIRM):**

| Branch | Last commit | Note |
|---|---|---|
| `ecc-tools/genai_incidents-1781143522258` | 07-19 | Bot/tool bundle |
| `ws0/v2130-item9-asi-source` | 10-12 | Its record file was merged via item 9, so the branch is superseded |
| `ws3/headroom-remeasure` | 09-20 | — |
| `ws4/refresh-tripwire-42` | 10-03 | **The D42 evidence. Relevant to stage 2.** |
| `ws4/t19-split-remediation` | 09-18 | — |
| `ws4/t22-abandoned-wip-2026-09-20` | 09-30 | A deliberate WIP archive |

**Tracked clutter (NEEDS-CONFIRM):**
- `PROGRESS.md`: 1.05 MB, 4,727 lines. Candidate to archive older sections.
- `legacy/` (3 files, 400 KB).
- `docs/superpowers/` (7 plans and specs from May and June).
- `AGENT_TEAM.md` and the planning documents from July.
- Two one-off scripts: `scripts/_finish_cve_from_cache.py` and `scripts/strip_presigned_urls.py`.
- The three byte-identical `incidents.min.json` copies (data, docs and src). These are probably intentional.
- Every other unreferenced script is cited as reproduction evidence in audits, so KEEP.

## Proposed order (nothing irreversible before a rescue)

1. Wait for active agents to go idle, then re-classify.
2. **Rescue:**
   - push the 3 unpushed local branches to `archive/*` names;
   - let the D66 repair branch commit and push;
   - optionally scan the Temp clones for commits that exist on no remote.
3. **User decisions:** the NEEDS-CONFIRM items above.
4. **Remove the SAFE worktrees** with `git worktree remove` (no `--force`, so a dirty tree is refused). Delete the empty orphan directory, then run `git worktree prune`.
5. **Delete merged local branches** with `git branch -d` (no `-D`, so an unmerged branch is refused).
6. **Delete merged remote branches,** keeping main, `refresh-state` and `auto-refresh/data` (and `release/*` if the user wants).
7. **Remove regenerable ignored files.**
8. **Last:** delete the old Temp session directories.
