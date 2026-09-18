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

`docs/releases/v2.10.0.md` was written under both constraints (absolute
links throughout, no in-body anchor links) specifically because it is
published as the Release body verbatim — see step 7.

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

2. **Bump the four version strings this project maintains.** All four must
   agree, and none is derived from another automatically — this is a
   manual, checklist-verified step:
   - `scripts/merge_and_dedupe.py` — the `"version"` key in the `out` dict
     written to `data/incidents.json` (currently the literal string
     `"2.9.0"` at line 1779; grep `"version": "2\.` if the file has moved).
   - `pyproject.toml` — the top-level `version = "..."` field.
   - `CITATION.cff` — **three** separate fields, all of which must move
     together: the top-level `version:`, the `preferred-citation.version:`,
     and `date-released:` (set to the actual cut date, not the notes'
     drafting date if they differ).
   - `.zenodo.json` — the top-level `"version"` field.

3. **Rebuild — never hand-edit `data/stats.json` or `data/incidents.json`.**
   Run the real build (`python scripts/parse_existing.py && python
   scripts/merge_and_dedupe.py`, or the equivalent `make build` target) so
   `data/stats.json` picks up the new version string through the pipeline,
   per the standing never-hand-edit-`data/*.json` rule. **Verify the
   rebuild changed no corpus row:** `git diff --stat -- data/incidents.json`
   should show only the `version` field changing (and `generated`, only if
   the build actually ran on a day some entry's `updated` also changed —
   see `docs/releases/v2.10.0.md`'s `generated`-semantics disclosure for
   why that field can lag real content changes). If the diff touches
   `incident_count`, any entry's other fields, or `id_deprecations.json`,
   stop — a version-string cut must not be a silent data cut.

4. **Run the docs-stats renderer.** `python scripts/render_docs_stats.py`
   propagates the new version (and any count that changed in step 3,
   though step 3 should show none) into every marker-wrapped surface —
   README, the datasheet, the site, the Hugging Face card — per invariant
   6. Then `python scripts/check_stats_drift.py` must exit 0: it greps
   every doc surface for a hardcoded total that disagrees with
   `data/stats.json` and fails the build if it finds one. This is the
   mechanical half of invariant 6; step 5 is the half it cannot catch.

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

9. **Post-cut verification.** `gh release view v<version>` must return a
   **published, non-draft** release (check the absence of a `"draft":
   true` marker in `gh release view v<version> --json isDraft`). This is
   the step that would have caught `v2.9.0`'s gap immediately if it had
   existed then: a release that is tagged, deposited, and gate-passed but
   never actually published as a Release object is exactly the state this
   step is designed to detect and refuse to call "done." Also confirm
   `huggingface.yml` and `publish.yml` both fired (they trigger on
   `release: published`, so a release that silently stayed a draft would
   silently skip both downstream publications too) — `gh run list
   --workflow=huggingface.yml --limit 1` and `gh run list
   --workflow=publish.yml --limit 1`, both showing a run against this tag.
