# Versioning

> **Scope note.** This document is WS6-T1's deliverable, and only one part
> of it exists here today: the **release-cut checklist** below. WS6-T1 also
> covers `__version__` / `data_version` / `data_date` exposure in the
> Python package, `fetch_latest()` with SHA-256 verification and caching,
> and an explicit "what bumps what" policy (what triggers major / minor /
> patch). **None of that is written yet.** Do not treat this file as the
> finished WS6-T1 deliverable — it answers one question only: the exact,
> numbered sequence of steps to cut a release, because the last cut
> (`v2.9.0`) skipped one of them silently and nothing caught it.

## Why this checklist exists

`v2.9.0`'s tag reached `origin`, its Zenodo deposit landed, and its gated
release notes landed — but **no GitHub Release object was ever published.**
The repository's Releases page kept showing `v2.8.0` as "Latest" for an
already-shipped version until someone noticed and published it by hand.
Nothing in the cut process failed loudly; the step that would have created
the Release object was simply never executed, and every other artifact
looked complete without it. **The cut was not under-executed — it was
under-specified: no document enumerated the steps, so there was nothing to
check off and notice a gap in.** This checklist exists so that gap has a
name and a position in a numbered sequence, and so a future cut can be
verified against it rather than against memory.

## Two structural defects of GitHub Release bodies, so nobody rediscovers them mid-cut

1. **Relative links 404 on a rendered release page.** A release body is
   displayed outside the repository's file-tree context, so a link like
   `../../mappings/owasp_llm_2025_to_2026.json` or `docs/foo.md` resolves
   against the wrong base and 404s. Every link in a release body must be an
   absolute URL:
   `https://github.com/emmanuelgjr/genai_incidents/blob/main/<path>`.
2. **GitHub emits no heading anchors in release bodies.** Unlike a rendered
   Markdown file in the repository (where `## Foo` gets `#foo`), a release
   body's own headings are not anchorable, so an in-body link like
   `[see below](#verification)` is dead on the release page even though the
   identical file renders that anchor correctly everywhere else (README,
   the repo's own file view). Any release-notes document that intends to be
   published verbatim as a Release body must not rely on its own anchors.

`docs/releases/v2.10.0.md` is published as the Release body verbatim (step
7), so it must hold to both constraints — and "must hold to" is a claim
worth checking rather than asserting: `grep -n '](#' docs/releases/v2.10.0.md`
should return no matches (no in-body anchor links), and `grep -n '](\.\./\|](docs/\|](\./' docs/releases/v2.10.0.md`
should also return none (no relative links). A prior draft of this
checklist asserted compliance here without running either check, and the
release notes at the time contained exactly one live in-body anchor link in
their own opening paragraph — caught at gate review, not by this file. Run
both greps as part of step 1's gate, not just once at drafting time.

## The release-cut checklist

1. **Release notes written and gated *before* the cut.** The notes file
   (`docs/releases/v<version>.md`) is drafted, its figures independently
   re-derived against the pre-cut tree (not copied from the board or the
   CHANGELOG), and it passes red-reviewer gate review — all **before** any
   version string in the repository changes. This ordering exists so the
   disclosure is reviewable while the decision to cut is still open, and so
   every number in the notes is checked against the tree a reader will
   actually receive, not against a tree that no longer exists by the time
   anyone reads the notes.

2. **Bump the five version strings this project maintains.** All five must
   agree, and none is derived from another automatically — this is a
   manual, checklist-verified step. **A prior draft of this checklist named
   only four; the fifth (the User-Agent) is easy to miss precisely because
   it lives in code that runs at ingest time, not at build or cut time:**
   - `scripts/merge_and_dedupe.py` — the `"version"` key in the `out` dict
     written to `data/incidents.json`. Find it with
     `grep -n '"version": "2\.' scripts/merge_and_dedupe.py` rather than a
     hardcoded line number — this file's own line count moves as other
     work lands (it is currently mid-migration on an unmerged branch that
     will shift it by roughly 150 lines the day after this cut), and a
     line reference here would silently stop pointing at the right line by
     the next release.
   - `pyproject.toml` — the top-level `version = "..."` field.
   - `CITATION.cff` — **three** separate fields, all of which must move
     together: the top-level `version:`, the `preferred-citation.version:`,
     and `date-released:` (set to the actual cut date, not the notes'
     drafting date if they differ).
   - `.zenodo.json` — the top-level `"version"` field.
   - `ingest/common.py`'s `USER_AGENT` constant — the literal version
     string every ingest HTTP request sends to every upstream host
     (`genai_incidents/2.9.0 (+https://github.com/emmanuelgjr; ...)`), also
     quoted verbatim in `docs/INGESTION_CONDUCT.md`. The code comment
     directly above it already states the policy — *"If you bump
     `pyproject.toml`'s version, bump this string too"* — because no single
     source of truth for the project version exists yet across these five
     locations. **This is a code change, so it is out of scope for
     whoever executes this checklist under WS6's file restrictions to make
     unilaterally here; route it to whoever owns `ingest/common.py` for
     this cut, and update the matching literal in
     `docs/INGESTION_CONDUCT.md` in the same change.** Do not skip this
     bullet silently — either the string moves with the rest, or this
     checklist records why it didn't for this specific cut.

3. **Rebuild with `make build` — never hand-edit `data/stats.json` or
   `data/incidents.json`, and never run only half the pipeline.** The
   `Makefile` target is `build: merge render render-docs-stats validate` —
   `merge` alone (`parse_existing.py` + `merge_and_dedupe.py`) is **not**
   equivalent to `make build` and must not be treated as such: `render`
   (`scripts/render_markdown.py`) is what writes `INCIDENTS.md`'s own
   `**Version:**`/`**Generated:**` lines, and `validate` is the schema/ID
   gate. Running only `merge` ships `INCIDENTS.md` at the old version with
   nothing downstream able to catch it — see step 4's note on why the
   drift checker specifically cannot see that file. Run `make build` in
   full.

   **Verify the rebuild changed no corpus row**, at the field level, not
   just a line count (`git diff --stat` reports lines changed in the
   pretty-printed JSON, which is not the same claim as "only one field
   changed" — a single value edit can move surrounding line boundaries
   depending on formatting, and conversely a large `--stat` count can still
   be confined to one JSON key repeated many times):
   ```bash
   git show HEAD~1:data/incidents.json > /tmp/before.json   # or the pre-rebuild commit
   python - <<'EOF'
   import json
   before = json.load(open("/tmp/before.json", encoding="utf-8"))
   after = json.load(open("data/incidents.json", encoding="utf-8"))
   top_diff = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
   print("top-level keys changed:", top_diff)   # expect {"version"}, or {"version", "generated"}
   b_ids = {e["id"] for e in before["incidents"]}
   a_ids = {e["id"] for e in after["incidents"]}
   print("ID set changed:", b_ids != a_ids)      # expect False
   changed_entries = [e["id"] for e in after["incidents"]
                      if e != next((x for x in before["incidents"] if x["id"] == e["id"]), None)]
   print("entries with any field changed:", len(changed_entries))  # expect 0
   EOF
   ```
   If `top_diff` contains anything besides `version` (and `generated`, only
   when the build ran on a day some entry's `updated` also legitimately
   changed — see `docs/releases/v2.10.0.md`'s `generated`-semantics
   disclosure), or if the ID set or any entry differs, stop — a
   version-string cut must not be a silent data cut. The same `version`
   string also lands in `data/incidents.min.json` and, once the site
   deploy runs, `docs/data/incidents.min.json` — spot-check both, since
   they are downstream copies of the same field and a rebuild that updates
   `data/incidents.json` but not its derived artifacts is its own kind of
   silent gap.

4. **Run the docs-stats renderer and confirm its actual boundary.**
   `make build` (step 3) already ran `render-docs-stats`
   (`python scripts/render_docs_stats.py`), which templates
   `data/stats.json`'s counts into the **five** doc surfaces
   `scripts/stats_docs_lib.py`'s `DOC_SURFACES` names — `README.md`,
   `docs/DATASHEET.md`, `docs/index.html`, `docs/_config.yml`,
   `CITATION.cff` — not "every" surface. `python scripts/check_stats_drift.py`
   must exit 0 against those five.

   **Two surfaces this step does not cover, so they need their own check:**
   - **`INCIDENTS.md`** is not in `DOC_SURFACES` at all. Its version line
     is written by `render_markdown.py` (part of `make render`, already
     run in step 3), but the drift checker never reads it — a stale line
     there would not fail this step or step 3. Confirm it by eye
     (`grep -n '^- \*\*Version:\*\*' INCIDENTS.md`) as part of step 5.
   - **The Hugging Face card** is *not* templated by `render_docs_stats.py`
     despite reading like one of "the" doc surfaces — it is generated
     separately, at export time, by `scripts/export_huggingface.py`, which
     reads `data/incidents.json`'s own `"version"` field directly (already
     correct after step 2/3, by a different mechanism than invariant 6's
     marker sweep). Confirm the card's own output
     (`dist/hf/README.md`'s `Dataset version <x>` line, after running the
     export) rather than assuming step 4 covers it.

5. **Sweep live surfaces for prose the bump just made false.** The
   drift check in step 4 catches stale *numbers* inside markers; it does
   not read English. The `v2.9.0` cut hit exactly this: after the version
   marker updated to read `2.9.0`, an adjacent paragraph still claimed *no
   version had been bumped or tagged yet* — true when it was written, false
   the moment the marker next to it changed, and nothing failed because the
   marker itself was correct. Before tagging, grep the live surfaces
   (README, `docs/DATASHEET.md`, the site, the HF card, `NOTICE-DATA`) for
   version-relative language — "not yet bumped," "still unreleased,"
   "current version" used as a fixed description rather than a marker —
   and fix any sentence the bump itself just made false. This is a human
   read-through, not a script; it is the step most likely to be skipped
   under time pressure, which is exactly why it has its own numbered line
   here rather than being folded into step 4.

6. **Tag, and push the tag.** `git tag -a v<version> -m "v<version>"` on
   the commit that carries the bumped strings, then `git push origin
   v<version>`. Confirm with `git ls-remote --tags origin v<version>` —
   local-only is not done, per this project's standing push discipline.

7. **Publish the GitHub Release object against the existing tag — its own
   numbered step, because this is the exact step `v2.9.0` skipped.** The
   tag existing on `origin` does **not** create a Release object; those are
   two different things GitHub happens to let you conflate, and the gap
   between them is invisible unless someone visits the Releases page.
   `gh release create v<version> --title "v<version>" --notes-file
   docs/releases/v<version>.md` (or `gh release create v<version> --tag
   v<version>` against the already-pushed tag, then `--notes-file`).
   **Byte-verify the published body against the source file** — `gh
   release view v<version> --json body -q .body` compared against
   `docs/releases/v<version>.md` — because a release body is a copy GitHub
   stores independently of the repository file, and the two can drift the
   moment either is edited post-hoc without the other. Remember the two
   structural defects above: the body must already use absolute links and
   no in-body anchors, or it will render broken on the page this step
   creates.

8. **The Zenodo deposit / redeposit step.** Cross-references WS6-T7's
   redeposit workflow in full; not restated here. In brief: a new
   **version-DOI** deposit is minted for this release (concept DOI
   `10.5281/zenodo.20248675` stays fixed across every version and is what
   every citation surface carries — `CITATION.cff`, README, the datasheet,
   the site, the HF card — per the existing concept-vs-version convention
   documented at `README.md#how-to-cite`). `.zenodo.json`'s version field
   (bumped in step 2) is what Zenodo's GitHub integration reads to label
   the new deposit; confirm it matches `CITATION.cff` before the deposit
   fires, since a mismatch here would publish an incorrectly labeled
   archival record that cannot be un-published, only superseded by another
   deposit.

   **8b. Re-sync the published Release body with the new DOI.** Step 7
   published the Release body **before** this step minted the version DOI
   — necessarily, since the DOI does not exist until the deposit fires —
   so if the release notes file promises a version-DOI line that "will be
   updated in place once it exists" (as `docs/releases/v2.10.0.md` does),
   that promise is only kept if this sub-step actually runs. Edit the
   source file first (`docs/releases/v<version>.md`, filling in the real
   version DOI), then push the published Release into agreement with it:
   `gh release edit v<version> --notes-file docs/releases/v<version>.md`.
   **Re-run step 7's byte-verify** (`gh release view v<version> --json
   body -q .body` against the file) after this edit — a Release body is a
   copy GitHub stores independently of the repository file, so editing the
   file alone does not touch the already-published page, and skipping this
   re-verify is exactly how the two would drift.

9. **Post-cut verification.** `gh release view v<version>` must return a
   **published, non-draft** release (check the absence of a `"draft":
   true` marker in `gh release view v<version> --json isDraft`). This is
   the step that would have caught `v2.9.0`'s gap immediately if it had
   existed then: a release that is tagged, deposited, and gate-passed but
   never actually published as a Release object is exactly the state this
   step is designed to detect and refuse to call "done."

   Also confirm `huggingface.yml` and `publish.yml` both fired **for this
   release specifically**, not merely recently — `gh run list --limit 1`
   with no filter returns the newest run of *any* trigger and would pass
   whether or not this cut fired anything, which is not a check. Filter by
   branch/tag and inspect the triggering event:
   ```bash
   gh run list --workflow=huggingface.yml -b v<version> \
     --json headBranch,event,status,conclusion,createdAt --limit 5
   gh run list --workflow=publish.yml -b v<version> \
     --json headBranch,event,status,conclusion,createdAt --limit 5
   ```
   Each must show at least one run with `event: "release"` and
   `conclusion: "success"` against `headBranch: "v<version>"` — anything
   else (no rows, or rows with a different event) means the release
   silently failed to trigger its downstream publications and step 9 is
   not satisfied by a green `gh run list` alone.
