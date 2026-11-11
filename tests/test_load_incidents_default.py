"""D134(i): load_incidents() default excludes retracted + unverified rows.

Expectations are derived from the packaged slim file and data/stats.json,
never hard-coded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import genai_incidents as gi

STATS = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
ALL = json.loads(
    (ROOT / "src" / "genai_incidents" / "data" / "incidents.min.json").read_text(encoding="utf-8")
)["incidents"]


def test_default_length_equals_published_incident_count():
    assert len(gi.load_incidents()) == STATS["incident_count"]


def test_include_retracted_true_returns_every_row():
    rows = gi.load_incidents(include_retracted=True)
    assert rows == ALL
    assert len(rows) == (
        STATS["incident_count"] + STATS["retracted_count"] + STATS["unverified_count"]
    )


def test_default_has_no_retracted_or_unverified_and_keeps_disputed():
    rows = gi.load_incidents()
    statuses = {e.get("status") for e in rows}
    assert not statuses & {"retracted", "unverified"}
    n_disputed = sum(1 for e in rows if e.get("status") == "disputed")
    assert n_disputed == STATS["disputed_count"] > 0


def test_default_drops_exactly_the_non_standing_rows():
    kept = {e["id"] for e in gi.load_incidents()}
    dropped = {e["id"] for e in ALL} - kept
    assert dropped == {e["id"] for e in ALL if e.get("status") in ("retracted", "unverified")}
    assert len(dropped) == STATS["retracted_count"] + STATS["unverified_count"]


def test_other_accessors_still_see_every_row():
    hidden = next(e for e in ALL if e.get("status") == "retracted")
    assert hidden["id"] not in {e["id"] for e in gi.load_incidents()}
    assert gi.by_id(hidden["id"]) == hidden
    assert any(e["id"] == hidden["id"] for e in gi.query(text=hidden["id"]))
