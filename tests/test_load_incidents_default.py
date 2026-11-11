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


# --- gate bounce #1 additions (D4/A1/A5) ---
import importlib.util


def _is(status):
    return [e for e in ALL if e.get("status") == status]


def test_unverified_row_hidden_by_default_but_found_elsewhere():
    row = _is("unverified")[0]
    assert row["id"] not in {e["id"] for e in gi.load_incidents()}
    assert gi.by_id(row["id"]) == row
    assert any(e["id"] == row["id"] for e in gi.query(text=row["id"]))


def test_by_cve_still_finds_a_retracted_row():
    # All retracted rows carry CVEs and no unverified row does, so by_cve can
    # only be pinned on a retracted row.
    row = next(e for e in _is("retracted") if e.get("cve_ids"))
    assert row["id"] not in {e["id"] for e in gi.load_incidents()}
    assert any(e["id"] == row["id"] for e in gi.by_cve(row["cve_ids"][0]))


def test_returned_lists_are_fresh_copies():
    for kw in ({}, {"include_retracted": True}):
        first = gi.load_incidents(**kw)
        n = len(first)
        first.append({"id": "INC-X"})
        assert len(gi.load_incidents(**kw)) == n
        del first[:5]
        assert len(gi.load_incidents(**kw)) == n


def test_default_order_is_source_order():
    expected = [e for e in ALL if e.get("status") not in {"retracted", "unverified"}]
    assert gi.load_incidents() == expected
    assert gi.load_incidents(include_retracted=True) == ALL


def test_not_standing_matches_the_build_constant():
    spec = importlib.util.spec_from_file_location(
        "entry_status_for_test", ROOT / "scripts" / "entry_status.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert gi._NOT_STANDING == mod.NOT_STANDING
