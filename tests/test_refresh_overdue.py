"""D63: scripts/refresh_overdue.py decides on MERGED refresh PRs, not opened ones."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import refresh_overdue as r  # noqa: E402

NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)


def _doc(merged=(), opened=()):
    return {
        "merged": [{"number": n, "mergedAt": t, "title": "Weekly data refresh"} for n, t in merged],
        "open": [{"number": n, "createdAt": t, "title": "Weekly data refresh"} for n, t in opened],
    }


def test_recent_merge_is_on_time():
    assert r.evaluate(_doc([(97, "2026-10-01T00:00:00Z")]), NOW, 21)["overdue"] is False


def test_stale_merge_is_overdue_even_with_an_open_pr():
    out = r.evaluate(_doc([(97, "2026-07-19T06:33:43Z")], [(110, "2026-10-11T11:00:00Z")]), NOW, 21)
    assert out["overdue"] is True and out["age_days"] > 80
    assert "#110" in r.render(out)  # an open PR is reported as awaiting review


def test_no_merged_pr_at_all_is_overdue():
    assert r.evaluate(_doc(), NOW, 21)["overdue"] is True


def test_latest_merge_wins_regardless_of_list_order():
    d = _doc([(1, "2026-01-01T00:00:00Z"), (2, "2026-10-10T00:00:00Z")])
    assert r.evaluate(d, NOW, 21)["overdue"] is False


def test_threshold_zero_forces_the_alert():  # the dispatch fire-proof
    assert r.evaluate(_doc([(97, "2026-10-13T11:59:00Z")]), NOW, 0)["overdue"] is True


def test_exit_codes(tmp_path):
    p = tmp_path / "in.json"
    p.write_text(json.dumps(_doc([(97, "2026-10-12T00:00:00Z")])), encoding="utf-8")
    assert r.main(["--input", str(p), "--now", NOW.isoformat()]) == 0
    assert r.main(["--input", str(p), "--now", NOW.isoformat(), "--max-age-days", "0"]) == 3
