"""D95 (superseded for AIRI by D108, 2026-10-13: AIRI is RETIRED, see the last test).

The generic NOT_ATTEMPTED semantics D95 added to check_source_health.py still
hold and are kept under a neutral source name: a not-attempted week changes
nothing, a bare GitHub "skipped" still counts as a failure, a failed attempt
still goes loud. The AIRI-specific monthly gate and the try_airi input are gone.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_source_health as h  # noqa: E402

STALE = {"example_source": {"consecutive_failures": 14, "last_attempt": "2026-10-11",
                            "last_outcome": "failure", "last_success": "2026-05-31", "status": "stale"}}


def test_skipped_week_changes_nothing_and_is_not_stale():
    new, stale, degraded, notices = h.update_source_health(
        STALE, {"example_source": "not-attempted"}, today="2026-10-18")
    assert new["example_source"] == STALE["example_source"] and stale == [] and degraded == [] and notices == {}


def test_control_a_failure_does_increment_and_goes_loud():
    # the control: the same state with outcome "failure" is what skipped must NOT behave like
    new, stale, _d, _n = h.update_source_health(STALE, {"example_source": "failure"}, today="2026-10-18")
    assert new["example_source"]["consecutive_failures"] == 15 and stale == ["example_source"]


def test_three_skipped_weeks_then_failed_monthly_attempt_is_loud(tmp_path):
    f = tmp_path / "s.json"
    f.write_text(json.dumps({"example_source": {"consecutive_failures": 2, "status": "degraded"}}), encoding="utf-8")
    for day in ("2026-11-08", "2026-11-15", "2026-11-22"):
        assert h.main(["--outcomes-json", '{"example_source": "not-attempted"}', "--state-file", str(f), "--today", day]) == 0
    assert json.loads(f.read_text())["example_source"]["consecutive_failures"] == 2  # not inflated
    rc = h.main(["--outcomes-json", '{"example_source": "failure"}', "--state-file", str(f), "--today", "2026-12-06"])
    assert rc == 1  # the monthly attempt reaches the threshold of 3 and fails the run


def test_a_successful_monthly_attempt_recovers_the_source(tmp_path):
    f = tmp_path / "s.json"
    f.write_text(json.dumps(STALE), encoding="utf-8")
    assert h.main(["--outcomes-json", '{"example_source": "success"}', "--state-file", str(f), "--today", "2026-11-01"]) == 0
    assert json.loads(f.read_text())["example_source"]["status"] == "ok"


def test_a_bare_github_skipped_still_counts_as_a_failure():
    new, _s, degraded, _n = h.update_source_health({}, {"example_source": "skipped"}, today="2026-10-18")
    assert new["example_source"]["consecutive_failures"] == 1 and degraded == ["example_source"]


def test_other_sources_are_still_judged_when_airi_is_skipped():
    new, stale, _d, _n = h.update_source_health(
        {}, {"example_source": "not-attempted", "oecd_aim": "failure"}, today="2026-10-18")
    assert "example_source" not in new and new["oecd_aim"]["consecutive_failures"] == 1


AIRI_LIVE = {"airi_navigator": {"consecutive_failures": 14, "last_attempt": "2026-10-11",
                                "last_outcome": "failure", "last_success": "2026-05-31", "status": "stale"}}


def test_simulated_sundays_airi_retired_never_alerts_and_counter_is_frozen(tmp_path):
    """The old D95 Sunday simulation (14 failures, stale, red on 2026-11-01 and
    2026-12-06) under D108: the same live state, the same Sundays, and the run
    never goes red for AIRI whether the workflow passes no outcome at all (what it
    does now) or a failure (what an old workflow copy would pass)."""
    from datetime import date, timedelta

    state = tmp_path / "s.json"
    state.write_text(json.dumps(AIRI_LIVE), encoding="utf-8")
    d, rcs = date(2026, 10, 18), []
    while d <= date(2026, 12, 6):
        outcomes = {"aiaaic_sheet": "success"}
        if d.day <= 7:
            outcomes["airi_navigator"] = "failure"  # the old monthly attempt
        rcs.append(h.main(["--outcomes-json", json.dumps(outcomes),
                           "--state-file", str(state), "--today", d.isoformat()]))
        d += timedelta(days=7)
    assert rcs == [0] * 8
    airi = json.loads(state.read_text())["airi_navigator"]
    assert airi["status"] == "retired" and airi["consecutive_failures"] == 14
