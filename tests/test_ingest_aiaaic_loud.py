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
    r[3] = "Some Deployer"
    r[4] = "Some Developer Inc."
    r[5] = "Sys"
    r[6] = "Generative AI"
    r[7] = "Do things"
    r[10] = "Germany"
    r[11] = "Technology"
    r[12] = "Privacy loss"
    r[9] = "Security; Privacy/surveillance"
    r[16] = "Litigation"
    r[18] = f"https://www.aiaaic.org/x/{n}"
    return r


def _csv(header=HEADER, n=10, sub=SUB):
    rows = [["Incidents"] + [""] * 19, header, sub] + [_data_row(i) for i in range(n)]
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


def _rename(name):
    """Rename `name` wherever it appears in the main header row or sub-header row."""
    hdr = ["Renamed by upstream" if c.strip() == name else c for c in HEADER]
    sub = ["Renamed by upstream" if c.strip() == name else c for c in SUB]
    return hdr, sub


# Every column that feeds a published field (REQUIRED_COLUMNS), by its CSV header.
REQUIRED_HEADERS = [
    "AIAAIC ID#", "Incident headline", "Occurred", "Deployer", "Developer", "System name",
    "Technology", "Purpose", "Ethical issue (taxonomy)", "Jurisdiction", "Sector",
    "Individual", "Consequence (taxonomy)", "Summary/links",
]


def test_required_headers_cover_required_columns():
    assert len(REQUIRED_HEADERS) == len(a.REQUIRED_COLUMNS)
    col = a.build_column_map([HEADER, SUB])
    assert sorted(col[k] for k in a.REQUIRED_COLUMNS) == sorted(set(col[k] for k in a.REQUIRED_COLUMNS))


@pytest.mark.parametrize("renamed", REQUIRED_HEADERS)
def test_missing_required_column_exits_nonzero_and_keeps_file(sheet, capsys, renamed):
    out, committed, feed = sheet
    hdr, sub = _rename(renamed)
    feed(_csv(header=hdr, sub=sub))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed
    assert "ERROR" in capsys.readouterr().err


@pytest.mark.parametrize("renamed", ["News trigger (taxonomy)", "Societal", "Environmental", "Response (taxonomy)"])
def test_unpublished_column_rename_only_warns(sheet, capsys, renamed):
    # These feed nothing published (a.WARN_ONLY_COLUMNS): a rename is a warning, not a failure.
    out, _, feed = sheet
    hdr, sub = _rename(renamed)
    feed(_csv(header=hdr, sub=sub))
    assert a.main() == 0
    assert "WARNING" in capsys.readouterr().err
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 10


def test_every_mapped_column_is_required_or_explicitly_warn_only():
    assert set(a.REQUIRED_COLUMNS) | set(a.WARN_ONLY_COLUMNS) == set(a.EXPECTED_COLUMNS)
    assert not set(a.REQUIRED_COLUMNS) & set(a.WARN_ONLY_COLUMNS)


def test_headline_system_header_swap_is_caught(sheet, capsys):
    out, committed, feed = sheet
    hdr = ["System name" if c == "Incident headline" else "Incident headline" if c == "System name" else c
           for c in HEADER]
    feed(_csv(header=hdr))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed
    assert "swapped" in capsys.readouterr().err


def test_zero_rows_fails_without_overwriting(sheet):
    out, committed, feed = sheet
    feed(_csv(n=0))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_yield_below_floor_fails_without_overwriting(sheet):
    out, committed, feed = sheet  # committed has 10 rows; floor is 90% -> 9
    assert a.MIN_YIELD_RATIO == 0.9
    feed(_csv(n=8))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_yield_at_floor_is_accepted(sheet):
    out, _, feed = sheet
    feed(_csv(n=9))
    assert a.main() == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 9


def test_override_accepts_a_large_drop_and_logs_loudly(sheet, monkeypatch, capsys):
    out, _, feed = sheet
    monkeypatch.setenv(a.YIELD_OVERRIDE_ENV, "1")
    feed(_csv(n=4))
    assert a.main() == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 4
    assert "ACCEPTING a yield drop" in capsys.readouterr().err


def test_override_never_rescues_zero_rows_or_schema_drift(sheet, monkeypatch):
    out, committed, feed = sheet
    monkeypatch.setenv(a.YIELD_OVERRIDE_ENV, "1")
    feed(_csv(n=0))
    assert a.main() == 1
    hdr, sub = _rename("Individual")
    feed(_csv(header=hdr, sub=sub))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_override_requires_exactly_1(sheet, monkeypatch):
    out, committed, feed = sheet
    monkeypatch.setenv(a.YIELD_OVERRIDE_ENV, "true")
    feed(_csv(n=4))
    assert a.main() == 1
    assert out.read_text(encoding="utf-8") == committed


def test_workflow_override_is_a_dispatch_input_wired_to_the_step():
    text = WF.read_text(encoding="utf-8")
    wf = yaml.safe_load(text)
    on = wf.get(True) or wf.get("on")
    assert "accept_aiaaic_yield_drop" in on["workflow_dispatch"]["inputs"]
    step = next(s for s in wf["jobs"]["refresh"]["steps"] if s.get("id") == "ingest_aiaaic")
    assert "accept_aiaaic_yield_drop" in step["env"]["AIAAIC_ACCEPT_YIELD_DROP"]


def test_pr_body_names_what_the_pr_carries_and_what_is_held():
    text = WF.read_text(encoding="utf-8")
    first = text.split("Automated weekly refresh of external sources.", 1)[1].split("\n\n", 1)[0]
    for carried in ("AIAAIC", "KEV", "CVE rejection sweep"):
        assert carried in first
    assert "held out" in first
    assert "AIRI Navigator, AIAAIC sheet, AIID snapshot, OECD AI Incidents Monitor." not in text


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
