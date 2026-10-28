"""D132: no surface pairs a release version with post-release counts.

Each test names the input that makes the check fail (CLAUDE.md agreement 6).
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_stats_drift as checker  # noqa: E402
import release_label as rl  # noqa: E402

ROWS = [{"id": "INC-1", "status": None, "tier": "landmark"}, {"id": "INC-2", "status": "retracted"}]
MARK = {"version": "2.13.0", "released": "2026-10-13", "tag": "v2.13.0",
        "rows_sha256": rl.rows_digest(ROWS), **rl.derive_counts(ROWS)}
CL = "## [Unreleased]\n\n## [2.13.0] — 2026-10-13\n"


def _stats(label, rows=ROWS):
    return {"version": label, **rl.derive_counts(rows), "last_release": MARK}


def _surf(label):
    return {"slim version_label": label}


def test_label_plain_when_rows_equal_release():
    assert rl.version_label(ROWS, MARK) == "2.13.0"


def test_label_main_when_one_row_differs_even_if_counts_equal():
    # input: same counts, one row's tier swapped -- an aggregate cannot see it
    rows = copy.deepcopy(ROWS)
    rows[0]["tier"] = "feed"; rows[1]["tier"] = "landmark"
    assert rl.version_label(rows, MARK) == "2.13.0+main"


def test_clean_main_and_clean_release_pass():
    new = ROWS + [{"id": "INC-3", "status": None}]
    assert checker.check_release_label(_stats("2.13.0+main", new), new, CL, _surf("2.13.0+main")) == []
    assert checker.check_release_label(_stats("2.13.0"), ROWS, CL, _surf("2.13.0")) == []


def test_plain_version_beside_post_release_counts_fails():
    # input: the pre-D132 state -- plain 2.13.0 with grown rows/counts
    new = ROWS + [{"id": "INC-3", "status": None, "tier": "landmark"}]
    errs = checker.check_release_label(_stats("2.13.0", new), new, CL, _surf("2.13.0"))
    assert any("plain release version but the rows differ" in e for e in errs)
    assert any("incident_count" in e and "D132" in e for e in errs)


def test_surface_with_plain_version_fails():
    # input: one surface (e.g. the slim file the site reads) still plain
    new = ROWS + [{"id": "INC-3", "status": None}]
    errs = checker.check_release_label(_stats("2.13.0+main", new), new, CL, _surf("2.13.0"))
    assert any("slim version_label" in e for e in errs)


def test_main_label_on_release_rows_fails():
    assert checker.check_release_label(_stats("2.13.0+main"), ROWS, CL, _surf("2.13.0+main"))


def test_forgotten_mark_release_fails():
    # input: CHANGELOG cut 2.14.0 but the marker still names 2.13.0
    cl = "## [2.14.0] — 2026-11-01\n" + CL
    assert any("mark_release" in e for e in checker.check_release_label(
        _stats("2.13.0"), ROWS, cl, _surf("2.13.0")))


def test_marker_matches_tag_when_tag_present():
    """Independent re-derivation from the tag; skipped where tags are not fetched."""
    m = rl.load_marker()
    tag = m["tag"]
    r = subprocess.run(["git", "show", f"{tag}^{{}}:data/incidents.json"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        pytest.skip(f"tag {tag} not present (shallow clone)")
    rows = json.loads(r.stdout.decode("utf-8"))["incidents"]
    assert rl.rows_digest(rows) == m["rows_sha256"]
    for k, v in rl.derive_counts(rows).items():
        assert m[k] == v, k


def test_committed_tree_label_matches_build():
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    rows = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    assert stats["version"] == rl.version_label(rows)
