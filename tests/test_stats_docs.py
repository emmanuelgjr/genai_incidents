"""Tests for scripts/stats_docs_lib.py, scripts/render_docs_stats.py, and
scripts/check_stats_drift.py (WS6-T2, invariant 6).

Covers both halves of the acceptance criterion: templating a marker to the
current data/stats.json value, and the CI check catching a planted stale
count (both the "marker says the wrong thing" and the "hardcoded literal
with no marker at all" shapes of drift).
"""

from __future__ import annotations

import json
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
        '{"incident_count": 12986, "retracted_count": 0, "disputed_count": 0, '
        '"landmark_count": 1865, "version": "2.8.0", '
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
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "2.8.0"\n', encoding="utf-8")
    (tmp_path / "ingest").mkdir()
    (tmp_path / "ingest" / "common.py").write_text('USER_AGENT = (\n    "genai_incidents/2.8.0 (x)"\n)\n', encoding="utf-8")
    (tmp_path / "INCIDENTS.md").write_text("- **Version:** 2.8.0\n", encoding="utf-8")
    (tmp_path / ".zenodo.json").write_text('{"version": "2.8.0"}', encoding="utf-8")
    (tmp_path / "CITATION.cff").write_text(
        'version: "2.8.0"\ndate-released: "2026-07-12"\npreferred-citation:\n  version: "2.8.0"\n',
        encoding="utf-8")
    # Corpus fixtures for the stats-vs-corpus check (v2.13.0 item 8): 12,986
    # standing rows, 1,865 landmark, 0 retracted/disputed, in both file shapes.
    rows = [{"id": f"INC-{n:05d}", "tier": "landmark" if n < 1865 else "feed"}
            for n in range(12986)]
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "incidents.json").write_text(
        json.dumps({"incidents": rows}), encoding="utf-8")
    (tmp_path / "src" / "genai_incidents" / "data").mkdir(parents=True)
    (tmp_path / "src" / "genai_incidents" / "data" / "incidents.min.json").write_text(
        json.dumps({"incidents": rows}), encoding="utf-8")
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


# --- v2.13.0 item 8 / D64: disputed_count is a SUBSET of incident_count -----


def _rows():
    return [
        {"id": "INC-1", "tier": "landmark"},
        {"id": "INC-2", "status": "disputed", "status_reason": {"code": "cve-disputed"}},
        {"id": "INC-3", "status": "retracted", "status_reason": {"code": "cve-rejected"}},
        {"id": "INC-4"},
    ]


def test_derive_counts_keeps_disputed_inside_incident_count():
    c = checker.derive_counts(_rows())
    assert c == {"incident_count": 3, "retracted_count": 1,
                 "disputed_count": 1, "landmark_count": 1}
    # invariant 1: no combined headline -- the three are never summed anywhere
    assert "standing_count" not in c and "total_count" not in c


def test_stats_vs_corpus_clean_when_equal():
    stats = checker.derive_counts(_rows())
    assert checker.check_stats_vs_corpus(stats, _rows(), _rows()) == []


def test_stats_vs_corpus_fires_on_wrong_disputed_count():
    stats = checker.derive_counts(_rows())
    stats["disputed_count"] = 0
    errs = checker.check_stats_vs_corpus(stats, _rows(), _rows())
    assert len(errs) == 2 and all("disputed_count" in e for e in errs)


def test_stats_vs_corpus_fires_when_only_the_slim_mirror_disagrees():
    stats = checker.derive_counts(_rows())
    slim = [r for r in _rows() if r["id"] != "INC-2"]  # mirror lost a disputed row
    errs = checker.check_stats_vs_corpus(stats, _rows(), slim)
    assert errs and all("incidents.min.json" in e for e in errs)


def test_disputed_and_retracted_markers_are_templated():
    stats = {**STATS, "disputed_count": 22, "retracted_count": 29}
    text = "<!-- stats:disputed_count -->1<!-- /stats:disputed_count -->"
    new, changes = lib.render_text(text, stats)
    assert "22" in new and changes


def test_disputed_count_marker_is_present_on_every_headline_surface():
    """D64: README headline, DATASHEET Instances line and the site hero each carry a
    templated disputed subset figure, so check_stats_drift guards it on a doc surface."""
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    for rel in ("README.md", "docs/DATASHEET.md", "docs/index.html"):
        text = (root / rel).read_text(encoding="utf-8")
        assert re.search(r"<!--\s*stats:disputed_count\s*-->", text), rel


def test_stats_panel_shows_disputed_figure_computed_from_rows():
    """D64: the live panel in docs/app.js carries 'of which N disputed (still counted)',
    computed from rows' status == "disputed", and the core payload carries `status`."""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    js = (root / "docs" / "app.js").read_text(encoding="utf-8")
    assert "r.status === 'disputed'" in js
    assert "of which ${fmtNum(disputed)} disputed (still counted)" in js
    sys.path.insert(0, str(root / "scripts"))
    import gen_docs_core_data as core
    assert "status" in core.CORE_FIELDS
