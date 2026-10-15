"""Shared marker convention + surface list for WS6-T2 (invariant 6: docs pull
counts from ``data/stats.json``; hardcoded totals fail CI).

Both ``render_docs_stats.py`` (templates the values in) and
``check_stats_drift.py`` (the CI gate) import this module so the marker
syntax, the surface list, and the value formatters can never drift apart
from each other — a mismatch there would be the same class of bug this task
exists to prevent, just one level up.

Marker convention
------------------
Each templated value is wrapped in a matched HTML-comment sentinel pair::

    <!-- stats:incident_count -->12,986<!-- /stats:incident_count -->

HTML comments are invisible when the Markdown/HTML surface renders, and the
pair is trivially greppable (a reviewer can ``git grep 'stats:incident_count'``
and see every surface that claims to derive from it). ``render_docs_stats.py``
rewrites only the text between a matched pair; it never touches anything
outside one, so hand-written prose is untouched unless a maintainer
deliberately wraps it.

A meta ``content="..."`` attribute can't contain an HTML comment (the
browser/crawler would include the comment's literal text since attribute
values aren't parsed as markup) — those surfaces (docs/index.html's
og:description / twitter:description) instead carry the marker as a
standalone comment line immediately before the tag, and the templater
rewrites the first matching number literal on the following line. See
``_MetaLineTarget`` below.

Exact-vs-rounded decision
--------------------------
Published counts are the EXACT value from ``data/stats.json`` (e.g.
``12,986``, not a rounded ``12,900+``). Rationale: rounding was originally a
concession to manual updates going stale between rounding steps: it hid
staleness rather than preventing it. Now that every count is templated by
this script and enforced by ``check_stats_drift.py``, "always exact" is no
harder to keep true than "always round," and it is strictly more honest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
STATS_PATH = ROOT / "data" / "stats.json"

# Matches a marker-wrapped span and captures the key and the current inner
# text: <!-- stats:KEY -->...<!-- /stats:KEY -->  (non-greedy, single line
# or multi-line — DOTALL so a wrapped span can't accidentally swallow a
# sibling marker pair further down the file).
MARKER_RE = re.compile(
    r"<!--\s*stats:(?P<key>[a-z_]+)\s*-->(?P<value>.*?)<!--\s*/stats:(?P=key)\s*-->",
    re.DOTALL,
)

# A standalone "<!-- stats:KEY:line -->" comment on its own line means: on
# the NEXT line, replace the first thousands-grouped number literal (with an
# optional trailing "+") with KEY's formatted value. Used where a marker
# pair can't be embedded directly (HTML attribute values).
LINE_MARKER_RE = re.compile(r"<!--\s*stats:(?P<key>[a-z_]+):line\s*-->")
NUMBER_LITERAL_RE = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+\+?")


def line_marker_key(line: str) -> str | None:
    """If ``line`` (stripped) is a standalone ``<!-- stats:KEY:line -->``
    comment, return KEY; else None. Shared by the templater and the drift
    checker so the two never disagree on what counts as a line marker.
    """
    m = LINE_MARKER_RE.fullmatch(line.strip())
    return m.group("key") if m else None

# Doc surfaces this task owns. Every file here is swept by both the
# templater and the drift checker, even ones with no markers/counts yet, so
# a future hardcoded total added to any of them is caught immediately
# instead of requiring someone to remember to add the file to this list at
# the same time.
DOC_SURFACES: list[Path] = [
    ROOT / "README.md",
    ROOT / "docs" / "DATASHEET.md",
    ROOT / "docs" / "index.html",
    ROOT / "docs" / "_config.yml",
    ROOT / "CITATION.cff",
]


def load_stats() -> dict:
    return json.loads(STATS_PATH.read_text(encoding="utf-8"))


def _comma_int(n: int) -> str:
    return f"{n:,}"


# key -> formatter(stats) -> str. Every marker key used in a doc surface
# MUST have an entry here, or render_docs_stats.py raises loudly rather than
# silently leaving a stale value in place.
FORMATTERS: dict[str, Callable[[dict], str]] = {
    "incident_count": lambda s: _comma_int(s["incident_count"]),
    "landmark_count": lambda s: _comma_int(s["landmark_count"]),
    # v2.13.0 item 8 (D64): subset / excluded counts, registered so a surface
    # that quotes them is templated and drift-checked like the headline count.
    # `disputed_count` is a SUBSET of incident_count (disputed entries stay
    # counted); `retracted_count` and (D130) `unverified_count` are OUTSIDE it.
    # Never sum them (invariant 1).
    "disputed_count": lambda s: _comma_int(s["disputed_count"]),
    "retracted_count": lambda s: _comma_int(s["retracted_count"]),
    "unverified_count": lambda s: _comma_int(s["unverified_count"]),
    "version": lambda s: str(s["version"]),
    "generated": lambda s: str(s["generated"]),
    "year_min": lambda s: str(s["year_min"]),
    "year_max": lambda s: str(s["year_max"]),
}


def render_text(text: str, stats: dict) -> tuple[str, list[tuple[str, str, str]]]:
    """Rewrite every marker-wrapped span in ``text`` to its formatted value.

    Returns (new_text, changes) where changes is a list of
    (key, old_value, new_value) for every span whose value changed.
    """
    changes: list[tuple[str, str, str]] = []

    def _sub(m: re.Match) -> str:
        key = m.group("key")
        if key not in FORMATTERS:
            raise KeyError(
                f"no formatter registered for marker 'stats:{key}' — add one "
                f"to FORMATTERS in scripts/stats_docs_lib.py"
            )
        new_value = FORMATTERS[key](stats)
        old_value = m.group("value")
        if new_value != old_value:
            changes.append((key, old_value, new_value))
        return f"<!-- stats:{key} -->{new_value}<!-- /stats:{key} -->"

    text = MARKER_RE.sub(_sub, text)

    # Line-following markers (meta attribute values): walk the file and
    # rewrite the number literal on the line right after each
    # "<!-- stats:KEY:line -->" comment. A regex can't reach across into an
    # attribute value, so this is a line-oriented pass instead of a single
    # substitution like the marker-pair case above.
    lines = text.split("\n")
    out_lines = []
    pending_key: str | None = None
    for line in lines:
        if pending_key is not None:
            new_value = FORMATTERS[pending_key](stats)
            new_line, n = NUMBER_LITERAL_RE.subn(new_value, line, count=1)
            if n == 0:
                raise ValueError(
                    f"marker 'stats:{pending_key}:line' found no number "
                    f"literal on the following line to replace: {line!r}"
                )
            if new_line != line:
                old_match = NUMBER_LITERAL_RE.search(line)
                changes.append((pending_key, old_match.group(0) if old_match else "", new_value))
            out_lines.append(new_line)
            pending_key = None
            continue
        key = line_marker_key(line)
        if key is not None:
            pending_key = key
        out_lines.append(line)
    text = "\n".join(out_lines)

    return text, changes


def strip_marked_spans(text: str) -> str:
    """Return ``text`` with every marker-wrapped span's VALUE blanked out
    (markers themselves kept, for context in error messages) — used by the
    drift checker to find hardcoded totals living OUTSIDE any marker.
    """
    text = MARKER_RE.sub(lambda m: f"<!-- stats:{m.group('key')} --><!-- /stats:{m.group('key')} -->", text)

    lines = text.split("\n")
    out_lines = []
    blank_next = False
    for line in lines:
        if blank_next:
            out_lines.append(NUMBER_LITERAL_RE.sub("", line, count=1))
            blank_next = False
            continue
        out_lines.append(line)
        if line_marker_key(line) is not None:
            blank_next = True
    return "\n".join(out_lines)
