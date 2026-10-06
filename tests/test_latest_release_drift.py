"""v2.13.0 item 1: the drift check fails on a stale README "Latest release"
line, stale version metadata, and a hardcoded HF card template.

Each test names the input that makes the check fail (CLAUDE.md agreement 6).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_stats_drift as checker  # noqa: E402

_CL = "## [Unreleased]\n\n## [2.12.0] — 2026-10-04\n\n## [2.11.0] — 2026-10-01\n"
_RM = ("## \U0001f6a8 Latest release\n\n**<!-- stats:version -->2.12.0<!-- /stats:version -->"
       " — released 2026-10-04.** notes\n")
_ST = {"version": "2.12.0"}


def test_latest_release_clean():
    assert checker.check_latest_release(_RM, _ST, _CL) == []


def test_latest_release_stale_version_and_date_fail():
    # input: the 2.9.0 / 2026-09-01 line the user thought they saw
    stale = _RM.replace("<!-- stats:version -->2.12.0<!-- /stats:version -->", "2.9.0").replace(
        "2026-10-04", "2026-09-01")
    errs = checker.check_latest_release(stale, _ST, _CL)
    assert any("'2.9.0'" in e for e in errs) and any("'2026-09-01'" in e for e in errs)


def test_latest_release_stale_date_alone_fails_even_with_current_marker():
    # input: current version marker, stale date -- the case the marker machinery passes
    errs = checker.check_latest_release(_RM.replace("2026-10-04", "2026-09-01"), _ST, _CL)
    assert len(errs) == 1 and "2026-09-01" in errs[0]


def test_latest_release_missing_heading_or_line_fails():
    # input: heading renamed / lead line reworded away from the pattern
    assert checker.check_latest_release("# nothing\n", _ST, _CL)
    assert checker.check_latest_release("## Latest release\n\nprose only\n", _ST, _CL)


def test_stats_version_ahead_of_changelog_fails():
    # input: stats.json bumped to 2.13.0 with no released CHANGELOG heading
    assert checker.check_latest_release(_RM, {"version": "2.13.0"}, _CL)


def test_version_metadata_stale_fails_and_current_passes():
    py = '[project]\nversion = "2.12.0"\n'
    zen = '{"version": "2.12.0"}'
    cff = 'version: "2.12.0"\ndate-released: "2026-10-04"\npreferred-citation:\n  version: "2.12.0"\n'
    assert checker.check_version_metadata(_ST, py, zen, cff, _CL) == []
    assert checker.check_version_metadata(_ST, py.replace("2.12", "2.9"), zen, cff, _CL)
    assert checker.check_version_metadata(_ST, py, zen.replace("2.12", "2.9"), cff, _CL)
    assert checker.check_version_metadata(_ST, py, zen, cff.replace("2026-10-04", "2026-09-01"), _CL)
    assert checker.check_version_metadata(
        _ST, py, zen, cff.replace('  version: "2.12.0"', '  version: "2.9.0"'), _CL)


def test_hf_card_template_real_is_clean_and_planted_literals_fail():
    import export_huggingface
    assert checker.check_hf_card_template(export_huggingface.CARD) == []
    planted = export_huggingface.CARD.replace("{count}", "13,060").replace("`{version}`", "`2.9.0`")
    assert len(checker.check_hf_card_template(planted)) >= 3
