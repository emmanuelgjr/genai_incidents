"""AIAAIC sheet ingest fails loudly (2026-10-13: a renamed header column wrote []
over 1,504 rows and the step reported success). Each test names the input that
makes the check fail and asserts the committed file is left untouched."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest
import yaml

import ingest_aiaaic_sheet as a

WF = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-refresh.yml"

HEADER = [
    "AIAAIC ID#", "Incident headline", "Occurred", "Deployer", "Developer", "System name",
    "Technology", "Purpose", "News trigger (taxonomy)", "Ethical issue (taxonomy)",
    "Impacted area", "", "External harm (taxonomy)", "", "", "Harm status",
    "Consequence (taxonomy)", "Response (taxonomy)", "Summary/links", "",
]
SUB = ["", "", "", "", "", "", "", "", "", "", "Jurisdiction", "Sector", "Individual",
       "Societal ", "Environmental", "", "", "", "", ""]


def _data_row(n):
    r = [""] * 20
    r[0] = f"AIAAIC{n:04d}"
    r[1] = f"Deepfake voice clone scam number {n}"
    r[2] = "2025"
    r[6] = "Generative AI"
    r[9] = "Security; Privacy/surveillance"
    r[16] = "Litigation"
    r[18] = f"https://www.aiaaic.org/x/{n}"
    return r


def _csv(header=HEADER, n=10):
    rows = [["Incidents"] + [""] * 19, header, SUB] + [_data_row(i) for i in range(n)]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue()


@pytest.fixture()
def sheet(monkeypatch, tmp_path):
    out = tmp_path / "aiaaic_sheet_incidents.json"
    committed = json.dumps([{"source_id": f"AIAAIC{i}"} for i in range(10)])
    out.write_text(committed, encoding="utf-8")
    monkeypatch.setattr(a, "OUT_PATH", out)

    def feed(body):
        monkeypatch.setattr(a, "download_csv", lambda: (body, True))

    return out, committed, feed


def test_current_header_parses_every_row(sheet):
    out, _, feed = sheet
    feed(_csv(n=10))
    assert a.main() == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 10


def test_old_headline_alias_still_maps():
    hdr = ["Headline" if c == "Incident headline" else c for c in HEADER]
    assert a.build_column_map([hdr, SUB])["headline"] == 1


@pytest.mark.parametrize("renamed", ["Incident headline", "Occurred", "Summary/links", "AIAAIC ID#"])
def test_missing_required_column_exits_nonzero_and_keeps_file(sheet, capsys, renamed):
    out, committed, feed = sheet
    hdr = ["Renamed by upstream" if c == renamed else c for c in HEADER]
    feed(_csv(header=hdr))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed
    assert "ERROR" in capsys.readouterr().err


def test_zero_rows_fails_without_overwriting(sheet):
    out, committed, feed = sheet
    feed(_csv(n=0))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_yield_collapse_below_floor_fails_without_overwriting(sheet):
    out, committed, feed = sheet  # committed has 10 rows; floor is 50% -> 5
    feed(_csv(n=4))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_yield_at_floor_is_accepted(sheet):
    out, _, feed = sheet
    feed(_csv(n=5))
    assert a.main() == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 5


def test_missing_header_row_is_a_failure(sheet):
    out, committed, feed = sheet
    feed("a,b\n1,2\n")
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_workflow_records_a_nonzero_exit_as_failure_outcome():
    # continue-on-error keeps the job going but steps.<id>.outcome is `failure`
    # for a non-zero exit; source health is fed from that outcome.
    text = WF.read_text(encoding="utf-8")
    step = next(s for s in yaml.safe_load(text)["jobs"]["refresh"]["steps"] if s.get("id") == "ingest_aiaaic")
    assert step["run"] == "python scripts/ingest_aiaaic_sheet.py"
    assert step["continue-on-error"] is True
    assert "AIAAIC: ${{ steps.ingest_aiaaic.outcome }}" in text
