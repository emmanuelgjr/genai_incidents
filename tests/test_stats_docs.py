"""Tests for scripts/stats_docs_lib.py, scripts/render_docs_stats.py, and
scripts/check_stats_drift.py (WS6-T2, invariant 6).

Covers both halves of the acceptance criterion: templating a marker to the
current data/stats.json value, and the CI check catching a planted stale
count (both the "marker says the wrong thing" and the "hardcoded literal
with no marker at all" shapes of drift).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_stats_drift as checker  # noqa: E402
import stats_docs_lib as lib  # noqa: E402

STATS = {
    "incident_count": 12986,
    "landmark_count": 1865,
    "version": "2.8.0",
    "generated": "2026-07-12",
    "year_min": 1983,
    "year_max": 2026,
}


def test_render_text_fills_matching_marker():
    text = "index of <!-- stats:incident_count -->OLD<!-- /stats:incident_count --> incidents"
    new_text, changes = lib.render_text(text, STATS)
    assert "12,986" in new_text
    assert changes == [("incident_count", "OLD", "12,986")]


def test_render_text_no_diff_when_already_current():
    text = "index of <!-- stats:incident_count -->12,986<!-- /stats:incident_count --> incidents"
    new_text, changes = lib.render_text(text, STATS)
    assert new_text == text
    assert changes == []


def test_render_text_is_idempotent():
    text = "stale <!-- stats:incident_count -->1<!-- /stats:incident_count --> incidents"
    once, _ = lib.render_text(text, STATS)
    twice, changes_second_pass = lib.render_text(once, STATS)
    assert once == twice
    assert changes_second_pass == []


def test_render_text_line_marker_rewrites_following_line():
    text = (
        "<!-- stats:incident_count:line -->\n"
        '  <meta property="og:description" content="12,500+ incidents.">\n'
    )
    new_text, changes = lib.render_text(text, STATS)
    assert "12,986" in new_text
    assert "12,500+" not in new_text
    assert changes == [("incident_count", "12,500+", "12,986")]


def test_render_text_unknown_marker_key_raises():
    text = "<!-- stats:not_a_real_key -->x<!-- /stats:not_a_real_key -->"
    try:
        lib.render_text(text, STATS)
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for an unregistered marker key")


def test_check_marked_drift_flags_stale_marker():
    text = "<!-- stats:incident_count -->99,999<!-- /stats:incident_count -->"
    errors = checker.check_marked_drift("fake.md", text, STATS)
    assert len(errors) == 1
    assert "99,999" in errors[0]
    assert "12,986" in errors[0]


def test_check_marked_drift_clean_when_current():
    text = "<!-- stats:incident_count -->12,986<!-- /stats:incident_count -->"
    assert checker.check_marked_drift("fake.md", text, STATS) == []


def test_check_unmarked_totals_flags_bare_literal():
    text = "over 12,770 incidents so far, hand-typed and forgotten"
    errors = checker.check_unmarked_totals("fake.md", text)
    assert len(errors) == 1
    assert "12,770" in errors[0]


def test_check_unmarked_totals_ignores_marked_span():
    text = "<!-- stats:incident_count -->12,986<!-- /stats:incident_count -->"
    assert checker.check_unmarked_totals("fake.md", text) == []


def test_check_unmarked_totals_ignores_line_marker_target():
    text = (
        "<!-- stats:incident_count:line -->\n"
        '  <meta content="12,986 incidents.">\n'
    )
    assert checker.check_unmarked_totals("fake.md", text) == []


def test_planted_stale_count_is_caught_end_to_end(tmp_path, monkeypatch):
    """The scenario red-reviewer is asked to reproduce: plant a stale count
    on a doc surface, confirm the checker fails, confirm the templater fixes
    it, confirm re-running the checker then passes.
    """
    stats_path = tmp_path / "stats.json"
    stats_path.write_text(
        '{"incident_count": 12986, "landmark_count": 1865, "version": "2.8.0", '
        '"generated": "2026-07-12", "year_min": 1983, "year_max": 2026}',
        encoding="utf-8",
    )
    surface = tmp_path / "SURFACE.md"
    surface.write_text(
        "consolidated incidents (<!-- stats:incident_count -->99999<!-- /stats:incident_count -->)\n",
        encoding="utf-8",
    )
    # Release-consistency fixtures (all at 2.8.0) so only the planted count can fail.
    (tmp_path / "CHANGELOG.md").write_text("## [2.8.0] - 2026-07-12\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "## Latest release\n\n**2.8.0 - released 2026-07-12.** x\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('version = "2.8.0"\n', encoding="utf-8")
    (tmp_path / ".zenodo.json").write_text('{"version": "2.8.0"}', encoding="utf-8")
    (tmp_path / "CITATION.cff").write_text(
        'version: "2.8.0"\ndate-released: "2026-07-12"\n', encoding="utf-8")
    monkeypatch.setattr(lib, "STATS_PATH", stats_path)
    monkeypatch.setattr(lib, "DOC_SURFACES", [surface])
    monkeypatch.setattr(checker, "DOC_SURFACES", [surface])
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 1  # stale marker value: caught

    import render_docs_stats

    monkeypatch.setattr(render_docs_stats, "DOC_SURFACES", [surface])
    monkeypatch.setattr(render_docs_stats, "ROOT", tmp_path)
    assert render_docs_stats.main() == 0
    assert "12,986" in surface.read_text(encoding="utf-8")

    assert checker.main() == 0  # fixed: passes now
