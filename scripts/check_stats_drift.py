"""CI gate for invariant 6: docs pull counts from ``data/stats.json``;
hardcoded totals fail CI (WS6-T2).

Two independent failure modes, both checked:

1. **Marked drift** — a ``<!-- stats:KEY -->...<!-- /stats:KEY -->`` span (or
   a ``<!-- stats:KEY:line -->`` line marker) whose current value no longer
   matches what ``data/stats.json`` says it should be. This is what happens
   if ``data/stats.json`` changes but nobody re-ran ``render_docs_stats.py``
   (equivalently: ``make build``).
2. **Unmarked hardcoded total** — a thousands-grouped number literal
   (``12,986``, ``12,500+`` — the shape a published dataset total takes)
   sitting in a doc surface OUTSIDE any marker span. This is the case
   ``render_docs_stats.py`` structurally cannot catch on its own: it only
   ever rewrites text it already owns (inside a marker), so a stale count
   hand-typed straight into prose would sail through a "no diff after
   re-render" check with zero changes. This sweep is what actually
   satisfies "CI greps docs for hardcoded totals."

Run: ``python scripts/check_stats_drift.py``. Exits 1 with every offending
line printed on any failure; exits 0 (silent, one summary line) if every
surface is clean.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib

from stats_docs_lib import (
    DOC_SURFACES,
    FORMATTERS,
    MARKER_RE,
    NUMBER_LITERAL_RE,
    ROOT,
    line_marker_key,
    load_stats,
    strip_marked_spans,
)


def check_marked_drift(path, text: str, stats: dict) -> list[str]:
    errors = []
    for m in MARKER_RE.finditer(text):
        key = m.group("key")
        if key not in FORMATTERS:
            errors.append(
                f"{path}: <!-- stats:{key} --> has no registered formatter "
                f"in scripts/stats_docs_lib.py (typo in the marker key?)"
            )
            continue
        expected = FORMATTERS[key](stats)
        actual = m.group("value")
        if actual != expected:
            errors.append(
                f"{path}: stats:{key} is {actual!r} but data/stats.json says "
                f"it should be {expected!r} — run `python "
                f"scripts/render_docs_stats.py` and commit the result"
            )

    lines = text.split("\n")
    for i, line in enumerate(lines):
        key = line_marker_key(line)
        if key is None:
            continue
        if key not in FORMATTERS:
            errors.append(
                f"{path}:{i + 1}: <!-- stats:{key}:line --> has no "
                f"registered formatter in scripts/stats_docs_lib.py"
            )
            continue
        if i + 1 >= len(lines):
            errors.append(f"{path}:{i + 1}: stats:{key}:line marker has no following line")
            continue
        expected = FORMATTERS[key](stats)
        found = NUMBER_LITERAL_RE.search(lines[i + 1])
        if found is None:
            errors.append(
                f"{path}:{i + 2}: no number literal found on the line "
                f"after stats:{key}:line — nothing to check"
            )
        elif found.group(0) != expected:
            errors.append(
                f"{path}:{i + 2}: stats:{key}:line following value is "
                f"{found.group(0)!r} but data/stats.json says it should "
                f"be {expected!r} — run `python "
                f"scripts/render_docs_stats.py` and commit the result"
            )
    return errors


def check_unmarked_totals(path, text: str) -> list[str]:
    stripped = strip_marked_spans(text)
    errors = []
    for i, line in enumerate(stripped.split("\n")):
        for m in NUMBER_LITERAL_RE.finditer(line):
            errors.append(
                f"{path}:{i + 1}: hardcoded total {m.group(0)!r} found "
                f"outside any <!-- stats:KEY --> marker — wrap it in a "
                f"marker (see scripts/stats_docs_lib.py) so it derives from "
                f"data/stats.json instead of drifting"
            )
    return errors


LATEST_HEADING_RE = re.compile(r"^##\s+\S*\s*Latest release\s*$", re.MULTILINE)
LATEST_LINE_RE = re.compile(
    r"\*\*(?:<!--\s*stats:version\s*-->)?(?P<version>\d+\.\d+\.\d+)"
    r"(?:<!--\s*/stats:version\s*-->)?\s*[—–-]+\s*released\s+(?P<date>\d{4}-\d{2}-\d{2})"
)
CHANGELOG_TOP_RE = re.compile(
    r"^##\s+\[(?P<version>\d+\.\d+\.\d+)\]\s*[—–-]+\s*(?P<date>\d{4}-\d{2}-\d{2})",
    re.MULTILINE,
)


def changelog_top_release(changelog: str) -> tuple[str, str] | None:
    """(version, date) of the first released heading; ``[Unreleased]`` has no
    date and so never matches."""
    m = CHANGELOG_TOP_RE.search(changelog)
    return (m.group("version"), m.group("date")) if m else None


def check_latest_release(readme: str, stats: dict, changelog: str) -> list[str]:
    """The README ``## Latest release`` lead line must name the same version as
    ``stats.json`` and the same version+date as the top released CHANGELOG
    heading. Fails on: heading/lead line missing (renamed away), a stale
    version, or a stale date. A ``stats:version`` marker alone passes when the
    marker's own text is current but the sentence around it (the date) is not."""
    top = changelog_top_release(changelog)
    if top is None:
        return ["CHANGELOG.md: no released '## [X.Y.Z] - YYYY-MM-DD' heading found"]
    cl_version, cl_date = top
    errors = []
    if str(stats["version"]) != cl_version:
        errors.append(
            f"data/stats.json version {stats['version']!r} != top released "
            f"CHANGELOG heading {cl_version!r}"
        )
    h = LATEST_HEADING_RE.search(readme)
    if h is None:
        return errors + ["README.md: '## Latest release' heading not found"]
    m = LATEST_LINE_RE.search(readme, h.end())
    if m is None or readme.count("\n", h.end(), m.start()) > 4:
        return errors + [
            "README.md: Latest-release section has no '**X.Y.Z - released YYYY-MM-DD.**' lead line"
        ]
    if m.group("version") != cl_version:
        errors.append(
            f"README.md Latest release names version {m.group('version')!r} but "
            f"CHANGELOG/stats say {cl_version!r}"
        )
    if m.group("date") != cl_date:
        errors.append(
            f"README.md Latest release says released {m.group('date')!r} but "
            f"CHANGELOG top heading says {cl_date!r}"
        )
    return errors


def check_version_metadata(stats: dict, pyproject: str, zenodo: str, citation: str,
                           changelog: str) -> list[str]:
    """Version/date literals in packaging + citation metadata must equal stats.json
    (and CITATION date-released the top CHANGELOG date)."""
    want = str(stats["version"])
    errors = []
    try:
        pv = tomllib.loads(pyproject).get("project", {}).get("version")
    except tomllib.TOMLDecodeError as exc:
        pv = f"<unparseable: {exc}>"
    if pv != want:
        errors.append(f"pyproject.toml [project] version {pv!r} != stats {want!r}")
    zv = json.loads(zenodo).get("version")
    if zv != want:
        errors.append(f".zenodo.json version {zv!r} != stats {want!r}")
    # top-level `version:` (column 0) and preferred-citation's (indented) must both exist
    top_v = re.findall(r'^version:\s*"([^"]+)"', citation, re.MULTILINE)
    nested_v = re.findall(r'^[ \t]+version:\s*"([^"]+)"', citation, re.MULTILINE)
    if not top_v:
        errors.append("CITATION.cff has no top-level version: line")
    if not nested_v:
        errors.append("CITATION.cff has no preferred-citation version: line")
    for v in top_v + nested_v:
        if v != want:
            errors.append(f"CITATION.cff version {v!r} != stats {want!r}")
    d = re.search(r'^date-released:\s*"([^"]+)"', citation, re.MULTILINE)
    top = changelog_top_release(changelog)
    if top and (not d or d.group(1) != top[1]):
        errors.append(
            f"CITATION.cff date-released {d.group(1) if d else None!r} != top CHANGELOG date {top[1]!r}"
        )
    return errors


def check_hf_card_template(card: str) -> list[str]:
    """The HF card template must take count/version from the build, never carry a
    literal: needs the {count} and {version} placeholders and no grouped totals."""
    errors = [f"scripts/export_huggingface.py CARD lacks {{{p}}} placeholder"
              for p in ("count", "version") if "{" + p + "}" not in card]
    for m in NUMBER_LITERAL_RE.finditer(card):
        errors.append(f"scripts/export_huggingface.py CARD hardcodes total {m.group(0)!r}")
    # ungrouped integers of 4+ digits (a total typed without commas); bare years excluded
    for m in re.finditer(r"(?<![\w.])(?!(?:19|20)\d\d\b)\d{4,}\b", card):
        errors.append(f"scripts/export_huggingface.py CARD hardcodes ungrouped number {m.group(0)!r}")
    # any X.Y.Z literal, except third-party taxonomy versions written 'VERIS X.Y.Z'
    for m in re.finditer(r"(?<![\d.])\d+\.\d+\.\d+(?!\w|\.\d)", card):
        if not card[:m.start()].endswith("VERIS "):
            errors.append(f"scripts/export_huggingface.py CARD hardcodes version literal {m.group(0)!r}")
    return errors


def check_other_version_literals(stats: dict, common_src: str, incidents_md: str) -> list[str]:
    """ingest/common.py's USER_AGENT and INCIDENTS.md's ``**Version:**`` line both
    carry the dataset version as a literal and must equal stats.json."""
    want = str(stats["version"])
    errors = []
    # anchored to the assignment: comments elsewhere quote historical versions
    m = re.search(r'^USER_AGENT\s*=\s*\(?\s*"genai_incidents/(\d+\.\d+\.\d+)', common_src, re.MULTILINE)
    if not m or m.group(1) != want:
        errors.append(f"ingest/common.py USER_AGENT version {m.group(1) if m else None!r} != stats {want!r}")
    m = re.search(r"^- \*\*Version:\*\*\s*(\S+)", incidents_md, re.MULTILINE)
    if not m or m.group(1) != want:
        errors.append(f"INCIDENTS.md **Version:** {m.group(1) if m else None!r} != stats {want!r}")
    return errors


def main() -> int:
    stats = load_stats()
    all_errors: list[str] = []

    for path in DOC_SURFACES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        all_errors.extend(check_marked_drift(rel, text, stats))
        all_errors.extend(check_unmarked_totals(rel, text))

    def read(rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    changelog = read("CHANGELOG.md")
    all_errors.extend(check_latest_release(read("README.md"), stats, changelog))
    all_errors.extend(check_version_metadata(
        stats, read("pyproject.toml"), read(".zenodo.json"), read("CITATION.cff"), changelog))
    all_errors.extend(check_other_version_literals(
        stats, read("ingest/common.py"), read("INCIDENTS.md")))
    import export_huggingface
    all_errors.extend(check_hf_card_template(export_huggingface.CARD))

    if all_errors:
        print("::error::Doc surfaces have drifted from data/stats.json (invariant 6):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"[check-stats-drift] clean: {len(DOC_SURFACES)} doc surfaces match data/stats.json, "
          f"no unmarked hardcoded totals; Latest-release line, version metadata and "
          f"HF card template consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
