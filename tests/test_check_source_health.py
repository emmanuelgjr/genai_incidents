"""Tests for scripts/check_source_health.py (WS4-T9).

The load-bearing assertion (test_source_fails_loudly_after_threshold_consecutive_failures)
is the one the plan asks for explicitly: a source that has 404'd every week
for N consecutive refreshes must no longer be able to pass a refresh as a
mere ``::warning::`` — the check must return a failing exit status. This is
exactly the AIRI Navigator situation (dead since 2026-06-07, 7 consecutive
failures as of 2026-07-12 — see ingest/_state/source_health.json) that a
same-run ``continue-on-error`` + all-three-must-fail abort threshold could
not catch.

Also covers red-reviewer's bounce-#1 advisory (a): a pause must carry a
non-empty reason AND an unexpired ``paused_until``, or it is not honored —
"paused: true" alone, or a stale expiry, must not silence the gate.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_source_health as h  # noqa: E402


def test_single_failure_is_only_degraded_not_stale():
    state, stale, degraded, notices = h.update_source_health(
        {}, {"example_source": "failure"}, today="2026-06-07", threshold=3
    )
    assert state["example_source"]["consecutive_failures"] == 1
    assert state["example_source"]["status"] == "degraded"
    assert stale == []
    assert degraded == ["example_source"]
    assert notices == {}


def test_source_fails_loudly_after_threshold_consecutive_failures():
    """The core WS4-T9 fix: N consecutive failures can no longer pass as a warning."""
    state: dict = {}
    dates = ["2026-06-07", "2026-06-14", "2026-06-21"]
    stale: list[str] = []
    for d in dates:
        state, stale, _degraded, _notices = h.update_source_health(
            state, {"example_source": "failure"}, today=d, threshold=3
        )
    assert state["example_source"]["consecutive_failures"] == 3
    assert state["example_source"]["status"] == "stale"
    assert stale == ["example_source"], (
        "a source at/above the consecutive-failure threshold must be reported "
        "as stale (loud), not silently folded into a warning"
    )


def test_success_resets_consecutive_failures():
    state, _, _, _ = h.update_source_health(
        {"example_source": {"consecutive_failures": 5, "status": "stale"}},
        {"example_source": "success"},
        today="2026-07-19",
        threshold=3,
    )
    assert state["example_source"]["consecutive_failures"] == 0
    assert state["example_source"]["status"] == "ok"
    assert state["example_source"]["last_success"] == "2026-07-19"


def test_active_pause_does_not_report_as_newly_stale():
    """A reasoned, time-boxed pause silences the loud gate without hiding status."""
    prior = {
        "example_source": {
            "consecutive_failures": 6,
            "status": "stale",
            "paused": True,
            "paused_reason": "WS4-T9 triage in progress, retire-or-replace decision pending",
            "paused_until": "2026-08-01",
        }
    }
    state, stale, degraded, notices = h.update_source_health(
        prior, {"example_source": "failure"}, today="2026-07-19", threshold=3
    )
    assert state["example_source"]["status"] == "stale"
    assert state["example_source"]["consecutive_failures"] == 7
    assert stale == [], "an active pause must not trip the loud-failure gate"
    assert degraded == []
    assert notices == {"example_source": "active"}


@pytest.mark.parametrize(
    "entry_extra",
    [
        {"paused": True},  # no reason, no expiry at all
        {"paused": True, "paused_reason": "  "},  # blank reason
        {"paused": True, "paused_reason": "investigating"},  # reason but no paused_until
        {"paused": True, "paused_until": "2026-08-01"},  # expiry but no reason
        # Dropped-zero typo of a PAST date — the fail-open regression: a raw
        # string compare sorted this as > "2026-07-19" and returned "active".
        {"paused": True, "paused_reason": "investigating", "paused_until": "2026-7-1"},
    ],
)
def test_invalid_pause_is_not_honored(entry_extra):
    """paused: true alone (or with a blank/missing reason or expiry) must NOT silence
    the gate — that is exactly the one-line bypass advisory (a) warned about."""
    prior = {"example_source": {"consecutive_failures": 6, "status": "stale", **entry_extra}}
    state, stale, degraded, notices = h.update_source_health(
        prior, {"example_source": "failure"}, today="2026-07-19", threshold=3
    )
    assert stale == ["example_source"], "an invalid pause must not stop the source from being loud"
    assert notices == {"example_source": "invalid"}


def test_expired_pause_is_not_honored():
    """A pause with a paused_until in the past must expire back to loud, not stay silenced."""
    prior = {
        "example_source": {
            "consecutive_failures": 6,
            "status": "stale",
            "paused": True,
            "paused_reason": "WS4-T9 triage",
            "paused_until": "2026-07-01",  # in the past relative to "today" below
        }
    }
    state, stale, degraded, notices = h.update_source_health(
        prior, {"example_source": "failure"}, today="2026-07-19", threshold=3
    )
    assert stale == ["example_source"], "an expired pause must not stop the source from being loud"
    assert notices == {"example_source": "expired"}


def test_pause_status_helper_classifies_correctly():
    today = "2026-07-19"
    assert h.pause_status({}, today) == "none"
    assert h.pause_status({"paused": False}, today) == "none"
    assert h.pause_status({"paused": True}, today) == "invalid"
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "2026-07-01"}, today
    ) == "expired"
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "2026-07-19"}, today
    ) == "active", "paused_until == today should still count as active (inclusive)"
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "2026-12-31"}, today
    ) == "active"


def test_pause_status_rejects_unpadded_date_typo():
    """MANDATORY regression case (rider): "2026-7-1" is a realistic
    dropped-zero typo of a PAST date. Under the old raw-string compare it
    sorted as > "2026-07-19" and returned "active", silencing the loud-
    failure gate forever. Parsing as a real, canonically-formatted date
    closes that — this must be "invalid" (not "active")."""
    today = "2026-07-19"
    result = h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "2026-7-1"}, today
    )
    assert result != "active", "the fail-open must be closed"
    assert result == "invalid"


@pytest.mark.parametrize("until", ["forever", "TBD", "not-a-date", "2026/07/19"])
def test_pause_status_rejects_non_date_strings(until):
    today = "2026-07-19"
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": until}, today
    ) == "invalid"


def test_pause_status_caps_far_future_pause_as_invalid():
    """A validly-formatted but absurdly-far-future paused_until (e.g.
    "9999-12-31") is a permanent silence wearing a time-box costume — cap
    it at MAX_PAUSE_HORIZON_DAYS so it must be periodically re-justified."""
    today = "2026-07-19"
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "9999-12-31"}, today
    ) == "invalid"
    # Sanity: a pause comfortably inside the horizon is unaffected.
    assert h.pause_status(
        {"paused": True, "paused_reason": "x", "paused_until": "2026-10-01"}, today
    ) == "active"


def test_independent_sources_tracked_independently():
    state, stale, degraded, notices = h.update_source_health(
        {}, {"example_source": "failure", "aiaaic_sheet": "success", "oecd_aim": "failure"},
        today="2026-06-07", threshold=3,
    )
    assert state["aiaaic_sheet"]["status"] == "ok"
    assert state["example_source"]["status"] == "degraded"
    assert state["oecd_aim"]["status"] == "degraded"
    assert stale == []
    assert set(degraded) == {"example_source", "oecd_aim"}
    assert notices == {}


def test_state_round_trips_through_disk(tmp_path):
    state_file = tmp_path / "source_health.json"
    state, _, _, _ = h.update_source_health({}, {"kev": "failure"}, today="2026-06-07")
    h.save_state(state_file, state)
    reloaded = h.load_state(state_file)
    assert reloaded == state
    assert json.loads(state_file.read_text(encoding="utf-8")) == state


def test_cli_exits_nonzero_when_a_source_crosses_threshold(tmp_path):
    state_file = tmp_path / "source_health.json"
    # Prime the state file with 2 prior consecutive failures, then feed a 3rd.
    h.save_state(
        state_file,
        {"example_source": {"consecutive_failures": 2, "status": "degraded"}},
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"example_source": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-06-21",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "::error::" in result.stdout
    new_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert new_state["example_source"]["status"] == "stale"


def test_cli_exits_zero_and_warns_when_below_threshold(tmp_path):
    state_file = tmp_path / "source_health.json"
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"aiaaic_sheet": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-06-07",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "::warning::" in result.stdout
    assert "::error::" not in result.stdout


def test_cli_exits_nonzero_when_pause_has_expired(tmp_path):
    """End-to-end: an expired pause must not keep a persistently-dead source quiet."""
    state_file = tmp_path / "source_health.json"
    h.save_state(
        state_file,
        {
            "example_source": {
                "consecutive_failures": 6,
                "status": "stale",
                "paused": True,
                "paused_reason": "WS4-T9 triage",
                "paused_until": "2026-07-01",
            }
        },
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"example_source": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-07-19",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "EXPIRED" in result.stdout


def test_cli_exits_nonzero_when_pause_is_an_unpadded_date_typo(tmp_path):
    """End-to-end regression for the exact fail-open bug: an unpadded PAST
    date typo (a realistic dropped-zero mistake) must not silently keep a
    persistently-dead source's loud-failure gate quiet forever."""
    state_file = tmp_path / "source_health.json"
    h.save_state(
        state_file,
        {
            "example_source": {
                "consecutive_failures": 6,
                "status": "stale",
                "paused": True,
                "paused_reason": "WS4-T9 triage",
                "paused_until": "2026-7-1",
            }
        },
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"example_source": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-07-19",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "INVALID" in result.stdout


@pytest.mark.parametrize("outcome", ["failure", "cancelled", "skipped"])
def test_any_non_success_outcome_counts_as_a_failure(outcome):
    state, _, degraded, _ = h.update_source_health(
        {}, {"src": outcome}, today="2026-06-07", threshold=3
    )
    assert state["src"]["consecutive_failures"] == 1
    assert degraded == ["src"]


# --- D108: retired sources (AIRI Navigator, 2026-10-13) ---------------------

LIVE_AIRI_STATE = {  # the shape restored from the refresh-state branch
    "airi_navigator": {"consecutive_failures": 15, "last_attempt": "2026-10-04",
                       "last_outcome": "failure", "last_success": "2026-05-31", "status": "stale"},
}


def test_retired_source_is_stamped_over_a_stale_live_state_and_never_alerts():
    # The retired status reaches the live run from CODE, not from the restored state.
    for outcome in ("failure", "skipped", "success", h.NOT_ATTEMPTED):
        state, stale, degraded, notices = h.update_source_health(
            LIVE_AIRI_STATE, {"airi_navigator": outcome}, today="2026-10-18", threshold=3)
        assert state["airi_navigator"]["status"] == "retired"
        assert stale == [] and degraded == [] and notices == {}
        assert state["airi_navigator"]["consecutive_failures"] == 15  # history kept, frozen
        assert state["airi_navigator"]["last_success"] == "2026-05-31"
        assert state["airi_navigator"]["retired_on"] == "2026-10-13"


def test_retired_source_is_stamped_even_when_the_workflow_passes_no_outcome():
    state, stale, degraded, _ = h.update_source_health(
        LIVE_AIRI_STATE, {"aiaaic_sheet": "success"}, today="2026-10-18")
    assert state["airi_navigator"]["status"] == "retired"
    assert stale == [] and degraded == []
    assert state["aiaaic_sheet"]["status"] == "ok"


def test_retirement_does_not_silence_other_sources():
    _, stale, _, _ = h.update_source_health(
        {"example_source": {"consecutive_failures": 5, "status": "stale"}, **LIVE_AIRI_STATE},
        {"example_source": "failure", "airi_navigator": "failure"}, today="2026-10-18")
    assert stale == ["example_source"]


def test_cli_exits_zero_for_a_failing_retired_source(tmp_path):
    sf = tmp_path / "s.json"
    sf.write_text(json.dumps(LIVE_AIRI_STATE), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(Path(h.__file__)), "--state-file", str(sf), "--today", "2026-10-18",
         "--outcomes-json", json.dumps({"airi_navigator": "failure"})],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "::error::" not in r.stdout
    assert json.loads(sf.read_text(encoding="utf-8"))["airi_navigator"]["status"] == "retired"
    assert "| airi_navigator | retired 2026-10-13 (not attempted)" in r.stdout


def test_airi_retirement_is_wired_in_the_workflow_and_data_is_kept():
    import yaml
    root = Path(h.__file__).resolve().parents[1]
    text = (root / ".github" / "workflows" / "auto-refresh.yml").read_text(encoding="utf-8")
    wf = yaml.safe_load(text)
    on = wf.get(True) or wf.get("on")
    assert "try_airi" not in on["workflow_dispatch"]["inputs"]
    ids = {s.get("id") for s in wf["jobs"]["refresh"]["steps"]}
    assert not ids & {"airi_gate", "ingest_airi"}
    assert "ingest_airi_navigator" not in text
    assert 'airi_navigator\\"' not in text  # not passed to the health checker
    # existing rows are retained and still held as a pair input
    assert (root / "ingest" / "airi_navigator_incidents.json").exists()
    import hold_pair_inputs as hp
    assert "airi_navigator_incidents.json" in hp.held_files()
