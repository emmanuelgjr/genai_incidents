"""N9 precision audit (v2.13.0 item 5): sampler, Wilson script, DATASHEET
hook, validate.py gate, and the ai_relevance evaluation stub.

Every guard here has a test that makes it FIRE (agreement 6): a guard is
only cited once it has been seen to fail on a corrupted input.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path

import pytest

import evaluate_ai_relevance as ev
import precision_sample as ps
import validate as v
import wilson_ci as w

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "audits" / "precision" / "2026-10-11"


# --------------------------------------------------------------------------- Wilson
@pytest.mark.parametrize("x,n,lo,hi", [
    # Newcombe (1998), Stat Med 17:857-872, Table I, method 3 (Wilson score, no CC)
    (81, 263, 0.2553, 0.3662),
    (15, 148, 0.0624, 0.1605),
    (0, 20, 0.0, 0.1611),
    (1, 29, 0.0061, 0.1718),
    (29, 29, 0.8830, 1.0),
    # the 2026-10-03 gate's published intervals (wave12 gate-1 verdict, PRECISION)
    (75, 80, 0.862, 0.973),
    (80, 80, 0.954, 1.0),
])
def test_wilson_known_values(x, n, lo, hi):
    got = w.wilson(x, n)
    places = 3 if n == 80 else 4
    assert round(got[0], places) == pytest.approx(lo, abs=10 ** -places)
    assert round(got[1], places) == pytest.approx(hi, abs=10 ** -places)


def test_wilson_fires_on_wrong_value():
    # a deliberately wrong expectation must not match (the check is not vacuous)
    assert round(w.wilson(81, 263)[0], 4) != 0.2600


def test_stratified_estimate_equal_weights_is_plain_wilson():
    rows = [("a", "in-scope")] * 7 + [("a", "out-of-scope")] * 3 + [("b", "in-scope")] * 7 + [("b", "out-of-scope")] * 3
    est = w._estimate(rows, {"a": 100, "b": 100}, strict=False)
    assert est["precision"] == 0.7 and est["n_eff"] == 20.0
    assert est["ci95"] == [round(x, 6) for x in w.wilson(14, 20)]


def test_stratified_estimate_weights_by_population():
    # stratum a: 10/10 in, population 900; b: 0/10 in, population 100 -> 0.9, not the raw 0.5
    rows = [("a", "in-scope")] * 10 + [("b", "out-of-scope")] * 10
    est = w._estimate(rows, {"a": 900, "b": 100}, strict=False)
    assert est["precision"] == 0.9 and est["unweighted_precision"] == 0.5
    assert est["n_eff"] < 20  # unequal weights cost effective sample size


def test_unsure_treatments():
    rows = [("a", "in-scope")] * 6 + [("a", "unsure")] * 2 + [("a", "out-of-scope")] * 2
    assert w._estimate(rows, {"a": 50}, strict=False)["precision"] == 0.75
    assert w._estimate(rows, {"a": 50}, strict=True)["precision"] == 0.6


def test_unrepresented_strata_reported_not_imputed():
    est = w._estimate([("a", "in-scope")], {"a": 10, "b": 40}, strict=False)
    assert est["unrepresented_population"] == 40 and est["precision"] == 1.0


# --------------------------------------------------------------------------- sampler
def _synthetic(n_feed=900, n_land=150):
    rows = []
    fams = ["CVE-", "OECD-AIM-", "AIAAIC", "ARXIV-"]
    for i in range(n_feed):
        rows.append({"id": f"INC-{i:05d}", "tier": "feed", "quality_tier": "auto" if i % 3 else "reviewed",
                     "year": 2018 + i % 9, "source_ids": [fams[i % 4 if i % 50 else 3] + str(i)],
                     "title": f"t{i}", "references": [{"url": f"https://x/{i}"}]})
    for i in range(n_land):
        rows.append({"id": f"INC-9{i:04d}", "tier": "landmark", "quality_tier": "reviewed",
                     "year": 2020 + i % 6, "source_ids": [("AIID-" if i % 5 else "INC-") + str(i)],
                     "title": f"l{i}"})
    rows.append({"id": "INC-RETR", "tier": "feed", "status": "retracted", "quality_tier": "auto",
                 "year": 2024, "source_ids": ["CVE-X"]})
    return rows


def test_draw_is_deterministic_and_seed_sensitive():
    inc = _synthetic()
    f1, s1 = ps.draw(inc, 123)
    f2, s2 = ps.draw(inc, 123)
    assert ps.dump_json(s1) == ps.dump_json(s2) and ps.dump_json(f1) == ps.dump_json(f2)
    _, s3 = ps.draw(inc, 124)
    assert [e["id"] for e in s3["entries"]] != [e["id"] for e in s1["entries"]]


def test_allocation_and_frame():
    frame, sample = ps.draw(_synthetic(), 1)
    tiers = [e["tier"] for e in sample["entries"]]
    assert tiers.count("feed") == 100 and tiers.count("landmark") == 50
    assert frame["exclusions"] == {"status == retracted": 1}
    assert "INC-RETR" not in {e["id"] for e in sample["entries"]}
    for s in frame["strata"]:
        tier_pop = frame["tier_population"][s["tier"]]
        assert abs(s["allocated"] - ps.ALLOCATION[s["tier"]] * s["population"] / tier_pop) < 1
        assert s["drawn"] == s["allocated"]
    # ARXIV is 1/4 of feed except every 50th -> 2% pooling does not trigger; nothing is lost
    assert sum(s["population"] for s in frame["strata"]) == frame["frame_population"]


def test_small_family_is_pooled():
    inc = _synthetic()
    inc.append({"id": "INC-AVID1", "tier": "feed", "quality_tier": "auto", "year": 2025, "source_ids": ["AVID-1"]})
    frame, _ = ps.draw(inc, 1)
    assert "feed/avid" not in {s["stratum"] for s in frame["strata"]}


def test_sample_rows_carry_no_description():
    inc = _synthetic()
    inc[0]["description"] = "<img src=x onerror=alert(1)> RAW"
    _, s = ps.draw(inc, 1)
    assert "RAW" not in ps.dump_json(s)


def test_sheet_prefill_marks_agent_and_leaves_human_empty():
    _, s = ps.draw(_synthetic(), 1)
    sug = {"suggestions": {e["id"]: {"label": "in-scope", "reason": "r"} for e in s["entries"]}}
    rows = list(csv.DictReader(io.StringIO(ps.build_sheet(s, sug))))
    assert len(rows) == 150
    assert all(r["suggested_by"] == "agent" for r in rows)
    assert all(r["human_label"] == r["human_by"] == "" for r in rows)


def test_sheet_rejects_bad_suggested_label():
    _, s = ps.draw(_synthetic(), 1)
    with pytest.raises(SystemExit):
        ps.build_sheet(s, {"suggestions": {s["entries"][0]["id"]: {"label": "maybe"}}})


def test_default_check_on_working_data_never_passes_moved_data(capsys):
    """`--check` with the DEFAULT --data (the working data/incidents.json).
    Never skips: while the working data still hashes to the pin it must
    reproduce (and seed 7 must not); once the data has moved past the pin it
    must REFUSE with the pinned-data message rather than compare against moved
    data. Byte-for-byte reproduction against the pin itself is covered on
    every run by test_reproduces_from_pinned_blob (A1 follow-up, 2026-10-12)."""
    frame = json.loads((AUDIT / "frame.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    if ps.canonical_sha256(data["incidents"]) == frame["data_incidents_sha256"]:
        assert ps.main(["--check"]) == 0
        assert ps.main(["--check", "--seed", "7"]) == 1  # a different seed does NOT reproduce
    else:
        assert ps.main(["--check"]) == 1
        assert "but the sample was drawn from" in capsys.readouterr().out


def test_check_refuses_data_that_moved_past_the_pin(tmp_path, capsys):
    """Fire proof for --check's data-pin guard, independent of what the
    working tree holds: the pinned blob with one incident edited is refused."""
    data = _pinned_data(tmp_path)
    if data is None:
        pytest.skip(f"neither {PINNED_COMMIT} (shallow clone?) nor matching working data is available")
    doc = json.loads(data.read_text(encoding="utf-8"))
    doc["incidents"][0]["title"] = str(doc["incidents"][0].get("title", "")) + " (moved)"
    moved = tmp_path / "moved_incidents.json"
    moved.write_text(json.dumps(doc), encoding="utf-8")
    assert ps.main(["--check", "--data", str(moved)]) == 1
    assert "but the sample was drawn from" in capsys.readouterr().out


def test_check_fires_on_tampered_copy(tmp_path, capsys):
    """--check rejects a tampered copy of the committed sample. Runs against
    the PINNED blob (as test_reproduces_from_pinned_blob does), so it keeps
    running after data/incidents.json moves (A1 follow-up, 2026-10-12). The
    untampered copy must pass first, and the tampered one must fail for the
    TAMPER reason, not the data-pin guard."""
    data = _pinned_data(tmp_path)
    if data is None:
        pytest.skip(f"neither {PINNED_COMMIT} (shallow clone?) nor matching working data is available")
    d = tmp_path / "a"
    shutil.copytree(AUDIT, d)
    assert ps.main(["--check", "--data", str(data), "--out-dir", str(d)]) == 0
    assert "reproduced byte-for-byte" in capsys.readouterr().out
    p = d / "sample.json"
    text = p.read_text(encoding="utf-8")
    assert '"INC-07644"' in text  # the tamper below must really change the file
    p.write_text(text.replace('"INC-07644"', '"INC-07645"', 1), encoding="utf-8")
    assert ps.main(["--check", "--data", str(data), "--out-dir", str(d)]) == 1
    out = capsys.readouterr().out
    assert "NOT reproduced: sample.json" in out and "but the sample was drawn from" not in out


def test_rebuild_sheet_refuses_to_overwrite_human_labels(tmp_path):
    inc = _synthetic()
    data = tmp_path / "inc.json"
    data.write_text(json.dumps({"incidents": inc}), encoding="utf-8")
    out = tmp_path / "out"
    assert ps.main(["--data", str(data), "--out-dir", str(out), "--seed", "5"]) == 0
    sheet = out / "review_sheet.csv"
    rows = list(csv.DictReader(sheet.open(encoding="utf-8", newline="")))
    rows[0]["human_label"], rows[0]["human_by"] = "in-scope", "Jane Reviewer"
    with sheet.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=ps.SHEET_COLUMNS, lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)
    assert ps.main(["--data", str(data), "--out-dir", str(out), "--seed", "5", "--rebuild-sheet"]) == 1
    assert "Jane Reviewer" in sheet.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- human-only labels
def _copy_root(tmp_path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(AUDIT, root / "docs" / "audits" / "precision" / "2026-10-11")
    shutil.copy(ROOT / "docs" / "DATASHEET.md", root / "docs" / "DATASHEET.md")
    return root


def _audit(root: Path) -> Path:
    return root / "docs" / "audits" / "precision" / "2026-10-11"


def _fill_human(root: Path, fn) -> None:
    sheet = _audit(root) / "review_sheet.csv"
    rows = list(csv.DictReader(sheet.open(encoding="utf-8", newline="")))
    for i, r in enumerate(rows):
        fn(i, r)
    with sheet.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=ps.SHEET_COLUMNS, lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


def test_committed_sheet_has_suggestions_but_no_human_labels():
    rows = list(csv.DictReader((AUDIT / "review_sheet.csv").open(encoding="utf-8", newline="")))
    assert len(rows) == 150
    assert all(r["suggested_by"] == "agent" and r["suggested_label"] in ps.LABELS for r in rows)
    assert all(not r["human_label"] and not r["human_by"] for r in rows)


def test_wilson_ignores_agent_suggestions(tmp_path, capsys):
    root = _copy_root(tmp_path)
    res = w.compute(_audit(root), root)
    assert res["status"] == "pending" and res["human_labelled"] == 0 and "estimates" not in res
    assert w.main(["--audit-dir", str(_audit(root)), "--datasheet", str(root / "docs" / "DATASHEET.md")]) == 0
    assert "no human labels" in capsys.readouterr().out


@pytest.mark.parametrize("by", ["agent", "Claude", "label-scientist agent", "GPT reviewer", "ai"])
def test_agent_named_reviewer_is_refused(tmp_path, by):
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label=r["suggested_label"], human_by=by) if i == 0 else None)
    with pytest.raises(w.LabelError):
        w.compute(_audit(root), root)


def test_label_without_reviewer_is_refused(tmp_path):
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label="in-scope") if i == 0 else None)
    with pytest.raises(w.LabelError):
        w.compute(_audit(root), root)


def test_human_labels_are_counted(tmp_path):
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label="in-scope" if i % 2 else "out-of-scope",
                                            human_by="Jane Reviewer"))
    res = w.compute(_audit(root), root)
    assert res["status"] == "measured" and res["human_labelled"] == 150
    assert res["label_counts"] == {"in-scope": 75, "out-of-scope": 75, "unsure": 0}
    assert "**Status: measured**" in w.render_block(res)


# --------------------------------------------------------------------------- validate gate
def test_gate_passes_on_committed_tree_ratified_by_d76():
    """User ruling D76 (2026-10-11) ratified the pending state: marker and code
    agree, so the gate passes WITHOUT the UNRATIFIED warning at any version."""
    assert v.REQUIRED_PRECISION_PENDING_DECISION == "D76"
    auth = json.loads((v.ROOT / v.PRECISION_AUDIT_DIR_REL / v.PRECISION_AUTH_FILE)
                      .read_text(encoding="utf-8"))["authorization"]
    assert (auth["decision"], auth["decided"], auth["decided_by"]) == ("D76", "2026-10-11", "user")
    for version in ("2.12.0", "2.13.0", "2.13.9", "2.14.0", "3.0.0"):
        problems, line = v.check_precision_audit(version)
        assert problems == [], (version, problems)
        assert "UNRATIFIED" not in line and "authorised by D76" in line, (version, line)


def test_gate_passes_on_copy(tmp_path):
    root = _copy_root(tmp_path)
    assert v.check_precision_audit("2.13.0", root)[0] == []


def _edit(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert old in t, old
    path.write_text(t.replace(old, new, 1), encoding="utf-8")


def test_gate_fires_on_hand_typed_datasheet_figure(tmp_path):
    root = _copy_root(tmp_path)
    _edit(root / "docs" / "DATASHEET.md", "**Status: measurement pending.**", "**Precision: 92%.**")
    assert any("DATASHEET" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_missing_datasheet_block(tmp_path):
    root = _copy_root(tmp_path)
    _edit(root / "docs" / "DATASHEET.md", w.BLOCK_END, "")
    assert any("DATASHEET" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_hand_typed_results(tmp_path):
    root = _copy_root(tmp_path)
    _edit(_audit(root) / "results.json", '"status": "pending"', '"status": "measured"')
    assert any("results.json" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_sample_edit(tmp_path):
    root = _copy_root(tmp_path)
    _edit(_audit(root) / "sample.json", '"stratum": "feed/aiaaic"', '"stratum": "feed/oecd"')
    assert any("declared entries_sha256" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_sample_edit_with_recomputed_hashes(tmp_path):
    """Tamper the entries AND rewrite both the sample's and the marker's
    declared hash: only the value pinned in code catches it (the D28 lesson)."""
    root = _copy_root(tmp_path)
    sp = _audit(root) / "sample.json"
    s = json.loads(sp.read_text(encoding="utf-8"))
    s["entries"][0]["title"] = "swapped"
    s["entries_sha256"] = ps.canonical_sha256(s["entries"])
    sp.write_text(ps.dump_json(s), encoding="utf-8")
    ap = _audit(root) / "pending_authorization.json"
    m = json.loads(ap.read_text(encoding="utf-8"))
    m["authorization"]["entries_sha256"] = s["entries_sha256"]
    ap.write_text(json.dumps(m), encoding="utf-8")
    w.main(["--audit-dir", str(_audit(root)), "--datasheet", str(root / "docs" / "DATASHEET.md"),
            "--render-datasheet"])
    problems = v.check_precision_audit("2.13.0", root)[0]
    assert len(problems) == 1 and "pinned in code" in problems[0]


def test_gate_fires_on_dropped_sheet_row(tmp_path):
    root = _copy_root(tmp_path)
    sheet = _audit(root) / "review_sheet.csv"
    lines = sheet.read_text(encoding="utf-8").splitlines(keepends=True)
    sheet.write_text("".join(lines[:-1]), encoding="utf-8")
    assert any("ids differ" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_missing_marker(tmp_path):
    root = _copy_root(tmp_path)
    (_audit(root) / "pending_authorization.json").unlink()
    assert any("must be authorised" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_gate_fires_on_non_user_marker(tmp_path):
    root = _copy_root(tmp_path)
    _edit(_audit(root) / "pending_authorization.json", '"decided_by": "user"', '"decided_by": "agent"')
    assert any("decided_by" in p for p in v.check_precision_audit("2.13.0", root)[0])


def _set_marker_decision(root: Path, decision: str) -> None:
    ap = _audit(root) / "pending_authorization.json"
    m = json.loads(ap.read_text(encoding="utf-8"))
    m["authorization"]["decision"] = decision
    ap.write_text(json.dumps(m), encoding="utf-8")


def test_gate_fires_on_unratified_past_grace(tmp_path):
    """The grace path as it stood before D76: placeholder marker AND no id pinned
    in code (required_decision="" simulates the pre-D76 constant)."""
    root = _copy_root(tmp_path)
    _set_marker_decision(root, v.PRECISION_PENDING_PLACEHOLDER)
    problems, line = v.check_precision_audit("2.13.9", root, required_decision="")
    assert problems == [] and "UNRATIFIED" in line
    assert any("UNRATIFIED" in p for p in v.check_precision_audit("2.14.0", root, required_decision="")[0])
    assert any("UNRATIFIED" in p for p in v.check_precision_audit("3.0.0", root, required_decision="")[0])


def test_gate_fires_on_placeholder_marker_once_code_pins_d76(tmp_path):
    """D76 fire proof: with the code constant set, a placeholder marker is no
    longer tolerated -- not even inside the old 2.13.x grace."""
    root = _copy_root(tmp_path)
    _set_marker_decision(root, v.PRECISION_PENDING_PLACEHOLDER)
    for version in ("2.12.0", "2.13.0", "2.14.0"):
        problems = v.check_precision_audit(version, root)[0]
        assert any("pinned in code is 'D76'" in p for p in problems), (version, problems)


def test_gate_fires_on_wrong_decision_id(tmp_path):
    """D76 fire proof: a marker naming any other id fails against the D76 pin."""
    root = _copy_root(tmp_path)
    _set_marker_decision(root, "D77")
    for version in ("2.13.0", "2.14.0"):
        problems, line = v.check_precision_audit(version, root)
        assert any("names decision 'D77'" in p for p in problems), (version, problems)
        assert "NOT authorised" in line and "authorised by" not in line


@pytest.mark.parametrize("decided", ["<YYYY-MM-DD>", "2026-13-01", "2026-02-30", "11/10/2026",
                                     "20261011", "2026-10-11T00:00", "", None, 20261011])
def test_gate_fires_on_non_iso_decided(tmp_path, decided):
    """D75/D76 gate advisory 3: a ruling must carry a real ISO date."""
    root = _copy_root(tmp_path)
    ap = _audit(root) / "pending_authorization.json"
    m = json.loads(ap.read_text(encoding="utf-8"))
    m["authorization"]["decided"] = decided
    ap.write_text(json.dumps(m), encoding="utf-8")
    problems, line = v.check_precision_audit("2.13.0", root)
    assert any("decided is" in p and "ISO YYYY-MM-DD" in p for p in problems), problems
    # b4: the status line must not call a failing marker "authorised"
    assert "NOT authorised" in line and "authorised by" not in line, line


def test_unratified_grace_path_still_accepts_placeholder_date(tmp_path):
    """The date check applies to a RULING only: the pre-ruling marker shape
    (both placeholders, no id pinned in code) keeps its 2.13.x grace."""
    root = _copy_root(tmp_path)
    ap = _audit(root) / "pending_authorization.json"
    m = json.loads(ap.read_text(encoding="utf-8"))
    m["authorization"].update(decision=v.PRECISION_PENDING_PLACEHOLDER, decided="<YYYY-MM-DD>")
    ap.write_text(json.dumps(m), encoding="utf-8")
    problems, line = v.check_precision_audit("2.13.0", root, required_decision="")
    assert problems == [] and "UNRATIFIED" in line


def test_committed_d76_decided_date_passes():
    """Control for the test above: the committed D76 marker's date is valid."""
    auth = json.loads((AUDIT / "pending_authorization.json").read_text(encoding="utf-8"))["authorization"]
    assert auth["decided"] == "2026-10-11" and v._is_iso_date(auth["decided"])
    assert not any("decided is" in p for p in v.check_precision_audit("2.13.0")[0])


def test_gate_ratified_marker(tmp_path):
    root = _copy_root(tmp_path)
    # committed copy: marker D76 and code D76 agree
    problems, line = v.check_precision_audit("2.14.0", root)
    assert problems == [] and "authorised by D76" in line
    _set_marker_decision(root, "D99")
    # a filled marker without the matching pin in code is NOT a ruling
    assert any("pinned in code" in p for p in v.check_precision_audit("2.14.0", root)[0])
    problems, line = v.check_precision_audit("2.14.0", root, required_decision="D99")
    assert problems == [] and "authorised by D99" in line
    assert v.check_precision_audit("2.14.0", root, required_decision="D98")[0]


def test_gate_measured_needs_no_marker_but_needs_rerender(tmp_path):
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label="in-scope", human_by="Jane Reviewer"))
    (_audit(root) / "pending_authorization.json").unlink()
    stale = v.check_precision_audit("2.14.0", root)[0]
    assert any("results.json" in p for p in stale) and any("DATASHEET" in p for p in stale)
    assert w.main(["--audit-dir", str(_audit(root)), "--datasheet", str(root / "docs" / "DATASHEET.md"),
                   "--render-datasheet"]) == 0
    problems, line = v.check_precision_audit("2.14.0", root)
    assert problems == [] and line.startswith("precision: measured")


def test_gate_fires_on_agent_filled_human_column(tmp_path):
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label=r["suggested_label"], human_by="agent"))
    assert any("cannot compute" in p for p in v.check_precision_audit("2.13.0", root)[0])


def test_datasheet_pending_block_quotes_no_agent_figure():
    block = w.datasheet_block((ROOT / "docs" / "DATASHEET.md").read_text(encoding="utf-8"))
    summary = json.loads((AUDIT / "agent_suggested_precision.json").read_text(encoding="utf-8"))
    assert block and "measurement pending" in block
    for t in summary["estimates"].values():
        for k in ("feed", "landmark", "overall"):
            assert f"{100 * t[k]['precision']:.1f}%" not in block


# --------------------------------------------------------------------------- ai_relevance evaluation stub
def test_evaluation_waits_for_human_labels(capsys):
    assert ev.main(["--audit-dir", str(AUDIT)]) == 3
    assert "no human labels" in capsys.readouterr().out


def test_evaluation_confusion_matrix(tmp_path):
    root = _copy_root(tmp_path)
    sample = json.loads((_audit(root) / "sample.json").read_text(encoding="utf-8"))
    cve = [e["id"] for e in sample["entries"] if e["stratum"].endswith("/cve-ghsa")]
    truth = {i: ("in-scope" if k % 2 else "out-of-scope") for k, i in enumerate(cve)}
    truth[cve[0]] = "unsure"
    _fill_human(root, lambda i, r: r.update(human_label=truth.get(r["id"], "in-scope"), human_by="Jane Reviewer"))
    incidents = {i: {"id": i, "description": "d", "affected": ""} for i in [e["id"] for e in sample["entries"]]}
    out = ev.evaluate(_audit(root), incidents, assess=lambda d, p: (True, {}))  # admits everything
    cm = out["confusion_matrix"]
    pos = sum(1 for x in truth.values() if x == "in-scope")
    assert cm == {"TP": pos, "FP": len(cve) - 1 - pos, "FN": 0, "TN": 0}
    assert out["unsure_excluded"] == 1 and out["recall"]["value"] == 1.0


# --------------------------------------------------------------------------- BOUNCE #1: pins in EVERY status
def _rerender(root: Path) -> None:
    assert w.main(["--audit-dir", str(_audit(root)), "--datasheet", str(root / "docs" / "DATASHEET.md"),
                   "--render-datasheet"]) == 0


def _measured_copy(tmp_path) -> Path:
    root = _copy_root(tmp_path)
    _fill_human(root, lambda i, r: r.update(human_label="in-scope" if i % 3 else "out-of-scope",
                                            human_by="Jane Reviewer"))
    _rerender(root)
    problems, line = v.check_precision_audit("2.14.0", root)
    assert problems == [] and line.startswith("precision: measured")
    return root


def test_measured_bypass_b_swapped_sample_id_is_caught(tmp_path):
    """Reviewer's bypass B, in the MEASURED state: swap a sampled id in the
    sample AND the sheet, recompute entries_sha256, re-render. Only the code
    pin can catch it."""
    root = _measured_copy(tmp_path)
    sp = _audit(root) / "sample.json"
    s = json.loads(sp.read_text(encoding="utf-8"))
    old_id = s["entries"][0]["id"]
    s["entries"][0]["id"] = "INC-99999"
    s["entries_sha256"] = ps.canonical_sha256(s["entries"])
    sp.write_text(ps.dump_json(s), encoding="utf-8")
    _fill_human(root, lambda i, r: r.update(id="INC-99999") if r["id"] == old_id else None)
    _rerender(root)
    problems, line = v.check_precision_audit("2.14.0", root)
    assert line.startswith("precision: measured")
    assert len(problems) == 1 and "sample's entries hash" in problems[0] and "pinned in code" in problems[0]


def test_measured_bypass_c_edited_population_is_caught(tmp_path):
    """Reviewer's bypass C, in the MEASURED state: shrink a stratum's
    population (an estimator weight) and re-render. The figure moves; the
    frame pin must catch it."""
    root = _measured_copy(tmp_path)
    before = w.compute(_audit(root), root)["estimates"]["excluding_unsure"]["feed"]["precision"]
    fp = _audit(root) / "frame.json"
    f = json.loads(fp.read_text(encoding="utf-8"))
    for s in f["strata"]:
        if s["stratum"] == "feed/oecd":
            s["population"] = 10
    fp.write_text(ps.dump_json(f), encoding="utf-8")
    _rerender(root)
    after = w.compute(_audit(root), root)["estimates"]["excluding_unsure"]["feed"]["precision"]
    assert after != before  # the edit really moves the published figure
    problems, line = v.check_precision_audit("2.14.0", root)
    assert line.startswith("precision: measured")
    assert len(problems) == 1 and "frame.json" in problems[0] and "pinned in code" in problems[0]


def test_extra_dated_audit_dir_is_caught(tmp_path):
    """A newer, fully self-consistent dated directory must not take over."""
    root = _measured_copy(tmp_path)
    shutil.copytree(_audit(root), root / "docs" / "audits" / "precision" / "2026-12-01")
    problems = v.check_precision_audit("2.14.0", root)[0]
    assert len(problems) == 1 and "2026-12-01" in problems[0]
    # b17 advisory 2: wilson_ci no longer follows the newest directory; it refuses to guess
    with pytest.raises(w.AuditDirError, match="refusing to guess"):
        w.sole_audit_dir(root / "docs" / "audits" / "precision")


def test_missing_pinned_dir_is_caught(tmp_path):
    root = _copy_root(tmp_path)
    shutil.move(str(_audit(root)), str(root / "docs" / "audits" / "precision" / "2026-12-01"))
    problems = v.check_precision_audit("2.13.0", root)[0]
    assert problems and "pinned audit directory" in problems[0]


# --------------------------------------------------------------------------- A1: quality_tier domains
def test_domain_estimate_by_quality_tier():
    # stratum a (N=300): 2 auto rows both in, 2 reviewed rows both out; stratum b (N=100): 2 auto, 1 in
    rows = [("a", "auto", "in-scope"), ("a", "auto", "in-scope"), ("a", "reviewed", "out-of-scope"),
            ("a", "reviewed", "out-of-scope"), ("b", "auto", "in-scope"), ("b", "auto", "out-of-scope")]
    pops = {"a": 300, "b": 100}
    est = w._domain_estimate(rows, pops, "auto", strict=False)
    # weights: a rows 75 each, b rows 50 each -> (75+75+50)/(75+75+50+50) = 0.8
    assert est["precision"] == 0.8 and est["n"] == 4 and est["small_n"] is True
    assert w._domain_estimate(rows, pops, "reviewed", strict=False)["precision"] == 0.0
    assert w._domain_estimate(rows, pops, "curated", strict=False)["n"] == 0


def test_measured_results_carry_quality_tier_domains(tmp_path):
    root = _measured_copy(tmp_path)
    res = w.compute(_audit(root), root)
    dom = res["estimates"]["strict"]["by_quality_tier"]
    assert {"feed/auto", "feed/reviewed", "landmark/reviewed"} <= set(dom)
    assert sum(d["n"] for k, d in dom.items() if k.startswith("feed/")) == 100


# --------------------------------------------------------------------------- A10: Excel round-trip
def test_sheet_saved_by_excel_bom_crlf_quoted_is_read(tmp_path):
    root = _copy_root(tmp_path)
    sheet = _audit(root) / "review_sheet.csv"
    rows = list(csv.DictReader(sheet.open(encoding="utf-8", newline="")))
    for r in rows:
        r.update(human_label="in-scope", human_by="Jane Reviewer")
    buf = io.StringIO()
    wr = csv.DictWriter(buf, fieldnames=ps.SHEET_COLUMNS, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    wr.writeheader()
    wr.writerows(rows)
    sheet.write_bytes(b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8"))
    assert w.read_sheet(sheet)[0][0] == "sheet_row"  # BOM not glued onto the first header
    assert w.sheet_ids(sheet)[0] == rows[0]["id"]
    assert len(w.read_human_labels(sheet)) == 150
    _rerender(root)
    problems, line = v.check_precision_audit("2.14.0", root)
    assert problems == [] and line.startswith("precision: measured")


def test_bom_would_break_a_plain_utf8_reader(tmp_path):
    """Control for the test above: without utf-8-sig the first header gains a
    BOM -- proves the BOM case is a real input, not a no-op."""
    p = tmp_path / "s.csv"
    p.write_bytes(b"\xef\xbb\xbfid,human_label\r\nINC-1,in-scope\r\n")
    assert list(csv.DictReader(p.open(encoding="utf-8", newline="")))[0].get("id") is None
    assert list(csv.DictReader(p.open(encoding="utf-8-sig", newline="")))[0]["id"] == "INC-1"


# --------------------------------------------------------------------------- A5: reproduce against the pinned blob
PINNED_COMMIT = "6da13032"


def _pinned_data(tmp_path) -> Path | None:
    import subprocess

    out = tmp_path / "pinned_incidents.json"
    try:
        blob = subprocess.run(["git", "show", f"{PINNED_COMMIT}:data/incidents.json"], cwd=ROOT,
                              capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        blob = None
    if blob:
        out.write_bytes(blob)
        return out
    # shallow CI clones lack the commit; the working copy serves while its content still matches the pin
    frame = json.loads((AUDIT / "frame.json").read_text(encoding="utf-8"))
    cur = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    if ps.canonical_sha256(cur["incidents"]) == frame["data_incidents_sha256"]:
        return ROOT / "data" / "incidents.json"
    return None


def test_reproduces_from_pinned_blob(tmp_path):
    data = _pinned_data(tmp_path)
    if data is None:
        pytest.skip(f"neither {PINNED_COMMIT} (shallow clone?) nor matching working data is available")
    frame = json.loads((AUDIT / "frame.json").read_text(encoding="utf-8"))
    inc = json.loads(data.read_text(encoding="utf-8"))["incidents"]
    assert ps.canonical_sha256(inc) == frame["data_incidents_sha256"]
    assert ps.main(["--check", "--data", str(data)]) == 0
    assert ps.main(["--check", "--data", str(data), "--seed", "7"]) == 1


def test_double_bom_or_missing_column_is_refused(tmp_path):
    p = tmp_path / "review_sheet.csv"
    p.write_bytes(b"\xef\xbb\xbf\xef\xbb\xbfid,human_label,human_by\r\nINC-1,in-scope,Jane\r\n")
    with pytest.raises(w.LabelError, match="byte-order mark"):
        w.read_human_labels(p)
    p.write_bytes(b"id,label,human_by\nINC-1,in-scope,Jane\n")
    with pytest.raises(w.LabelError, match="required column"):
        w.read_human_labels(p)


# --------------------------------------------------------------------------- b4: status line
def test_status_line_on_committed_tree_is_exactly_authorised_by_d76():
    """Control for the b4 tests: the real tree's line is unchanged."""
    problems, line = v.check_precision_audit("2.13.0")
    assert problems == [] and line == "precision: pending, authorised by D76"


@pytest.mark.parametrize("corrupt", ["decided", "decided_by", "entries_sha256", "extra_dir", "stray_figure"])
def test_status_line_says_not_authorised_whenever_problems(tmp_path, corrupt):
    """b4: with the marker naming the pinned D76 but ANY problem present, the
    line used to read "authorised by D76". It must now say NOT authorised."""
    root = _copy_root(tmp_path)
    ap = _audit(root) / "pending_authorization.json"
    m = json.loads(ap.read_text(encoding="utf-8"))
    if corrupt == "extra_dir":
        (root / "docs" / "audits" / "precision" / "2026-10-11b").mkdir()
    elif corrupt == "stray_figure":
        _edit(root / "docs" / "DATASHEET.md", "it is never hand-typed.", "it is never hand-typed. Precision is 92%.")
    else:
        m["authorization"][corrupt] = {"decided": "2026/10/11", "decided_by": "agent",
                                       "entries_sha256": "0" * 64}[corrupt]
        ap.write_text(json.dumps(m), encoding="utf-8")
    problems, line = v.check_precision_audit("2.13.0", root)
    assert problems, corrupt
    assert m["authorization"]["decision"] == "D76"  # the marker still names the pinned decision
    assert line.startswith("precision: pending, NOT authorised") and "authorised by" not in line, line


def test_measured_line_flags_problems(tmp_path):
    root = _measured_copy(tmp_path)
    (root / "docs" / "audits" / "precision" / "2026-10-11b").mkdir()
    problems, line = v.check_precision_audit("2.14.0", root)
    assert problems and line.startswith("precision: measured") and "FAILING (1 problem(s))" in line


# --------------------------------------------------------------------------- b17.1: directory pin
@pytest.mark.parametrize("name", ["2026-10-11b", "2026-10-11 copy", "2026-10-12", "20261011", "scratch"])
def test_any_extra_audit_dir_is_caught(tmp_path, name):
    """b17 advisory 1: the old date-shaped glob did not see '2026-10-11b'.
    Every directory besides the pinned one now fails, empty or full."""
    root = _copy_root(tmp_path)
    assert v.check_precision_audit("2.13.0", root)[0] == []  # control
    (root / "docs" / "audits" / "precision" / name).mkdir()
    problems = v.check_precision_audit("2.13.0", root)[0]
    assert len(problems) == 1 and name in problems[0] and "besides the pinned" in problems[0]


def test_loose_file_in_precision_root_is_not_flagged(tmp_path):
    """Only directories are audits; a loose file is not flagged (scope note)."""
    root = _copy_root(tmp_path)
    (root / "docs" / "audits" / "precision" / "NOTES.txt").write_text("x", encoding="utf-8")
    assert v.check_precision_audit("2.13.0", root)[0] == []


# --------------------------------------------------------------------------- b17.2: CLI directory choice
def test_cli_uses_the_sole_dir_and_refuses_when_two_exist(tmp_path, monkeypatch, capsys):
    root = _copy_root(tmp_path)
    prec = root / "docs" / "audits" / "precision"
    monkeypatch.setattr(w, "PRECISION_ROOT", prec)
    ds = str(root / "docs" / "DATASHEET.md")
    assert w.sole_audit_dir() == _audit(root)  # control: one dir -> that dir
    assert w.main(["--datasheet", ds, "--check"]) == 0
    shutil.copytree(_audit(root), prec / "2026-10-11b")  # a self-consistent variant, sorts last
    with pytest.raises(w.AuditDirError):
        w.sole_audit_dir()
    capsys.readouterr()
    assert w.main(["--datasheet", ds, "--check"]) == 2
    assert "refusing to guess" in capsys.readouterr().out
    assert ev.main([]) == 2  # the evaluation stub shares the rule
    # an explicit --audit-dir is still honoured
    assert w.main(["--audit-dir", str(_audit(root)), "--datasheet", ds, "--check"]) == 0


def test_cli_refuses_when_no_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(w, "PRECISION_ROOT", tmp_path / "none")
    with pytest.raises(w.AuditDirError, match="no audit directory"):
        w.sole_audit_dir()


# --------------------------------------------------------------------------- b17.3: stray figures
NL = chr(10)
BULLET = "precision-first heuristics; `quality_tier` records vetting level."


def test_committed_datasheet_has_no_stray_precision_figure():
    """Control: the real DATASHEET passes (it also carries an unrelated '~36%')."""
    text = (ROOT / "docs" / "DATASHEET.md").read_text(encoding="utf-8")
    assert "36%" in text
    assert w.stray_precision_figures(text) == []


@pytest.mark.parametrize("old,new", [
    # in the Measured-precision section, next to the word
    ("it is never hand-typed.", "it is never hand-typed. Precision is 92%."),
    # in the Measured-precision section, WITHOUT the word (rule 3)
    ("it is never hand-typed.", "it is never hand-typed." + NL + NL + "Pilot result: 91.5 %."),
    # a proportion rather than a percentage
    ("it is never hand-typed.", "it is never hand-typed. Precision was 0.93 on the pilot."),
    # elsewhere in the DATASHEET, in a list item that names precision
    (BULLET, BULLET + NL + "- Precision on the feed: 95 percent."),
    # a full-width percent sign, built numerically
    (BULLET, BULLET + NL + "- Precision on the feed: 97" + chr(0xFF05) + "."),
    # a no-break space between number and sign
    (BULLET, BULLET + NL + "- Precision on the feed: 97" + chr(0xA0) + "%."),
    # gate BOUNCE 1 (defect 1): sentence-final proportions, near the word ...
    (BULLET, BULLET + NL + "- Precision: 0.92."),
    (BULLET, BULLET + NL + "- Precision is .92."),
    (BULLET, BULLET + NL + "- precision was 0.9."),
    # ... and in the Measured-precision section without the word
    ("it is never hand-typed.", "it is never hand-typed." + NL + NL + "In-scope share: 0.92."),
    # foreman ruling (a), should-fire half: a genuine mention next to a percentage
    (BULLET, BULLET + NL + "- Measured precision on the feed was 64%."),
    # ruling (b): explanatory figures in the section stay flagged
    ("it is never hand-typed.", "it is never hand-typed. Intervals are Wilson 95% score intervals."),
    ("it is never hand-typed.", "it is never hand-typed. Unsure rows are under 1% of the corpus."),
    # a table whose header names precision and whose row carries the number
    ("## Uses", "| Tier | Precision |" + NL + "|---|---|" + NL + "| feed | 88% |" + NL + NL + "## Uses"),
    # a second, hand-made block after the generated one
    (w.BLOCK_END, w.BLOCK_END + NL + NL + w.BLOCK_BEGIN + NL + "92" + NL + w.BLOCK_END),
])
def test_stray_precision_figure_fires(tmp_path, old, new):
    root = _copy_root(tmp_path)
    dsp = root / "docs" / "DATASHEET.md"
    assert v.check_precision_audit("2.13.0", root)[0] == []  # control
    _edit(dsp, old, new)
    assert w.stray_precision_figures(dsp.read_text(encoding="utf-8"))
    problems, line = v.check_precision_audit("2.13.0", root)
    assert any("DATASHEET" in p for p in problems) and "NOT authorised" in line
    assert w.main(["--audit-dir", str(_audit(root)), "--datasheet", str(dsp), "--check"]) == 1


@pytest.mark.parametrize("old,new", [
    # a percentage in a DIFFERENT bullet from the one naming precision
    (BULLET, BULLET + NL + "- **Coverage:** 40% of rows."),
    # version strings, dates and file names next to the word are not figures
    ("it is never hand-typed.", "it is never hand-typed (precision gate since v2.13.0, 2026-10-11, INCLUSION.md)."),
    # gate BOUNCE 1 controls: sentence-final non-proportions next to a real mention
    (BULLET, BULLET + NL + "- Precision gate since v2.13.0."),
    (BULLET, BULLET + NL + "- Precision tooling 0.13.0."),
    (BULLET, BULLET + NL + "- Precision of CVSS 9.8."),
    (BULLET, BULLET + NL + "- Precision sample drawn 2026-10-11."),
    # foreman ruling (a), should-pass half: the REAL "precision-first" bullet plus a percentage
    ("precision-first heuristics;", "precision-first heuristics (64% of rows);"),
    ("precision-first heuristics;", "precision-oriented heuristics (64% of rows);"),
])
def test_stray_precision_figure_does_not_misfire(tmp_path, old, new):
    root = _copy_root(tmp_path)
    dsp = root / "docs" / "DATASHEET.md"
    _edit(dsp, old, new)
    assert w.stray_precision_figures(dsp.read_text(encoding="utf-8")) == []


def test_stray_figure_known_limit_bare_integer(tmp_path):
    """Documented known limit (stray_precision_figures docstring): a bare
    integer outside the Measured-precision section is NOT detected. Pinned so
    that a future tightening shows up as a deliberate test change."""
    root = _copy_root(tmp_path)
    dsp = root / "docs" / "DATASHEET.md"
    _edit(dsp, BULLET, BULLET + NL + "- Precision score 92.")
    assert w.stray_precision_figures(dsp.read_text(encoding="utf-8")) == []


def test_section_rule_message_says_figures_must_be_generated(tmp_path):
    root = _copy_root(tmp_path)
    dsp = root / "docs" / "DATASHEET.md"
    _edit(dsp, "it is never hand-typed.", "it is never hand-typed. Intervals are Wilson 95% score intervals.")
    probs = w.stray_precision_figures(dsp.read_text(encoding="utf-8"))
    assert any("figures in this section must be generated" in p and "outside the section or inside the generated "
               "block" in p for p in probs), probs


def test_generated_block_already_states_interval_wording():
    """Ruling (b): the interval method is covered by the generator, so the
    section's prose has no need to type it."""
    res = json.loads((AUDIT / "results.json").read_text(encoding="utf-8"))
    assert "Wilson score 95% interval" in w.render_block(res)


@pytest.mark.parametrize("text,mention", [
    ("precision-first heuristics", False), ("precision-oriented design", False), ("imprecision", False),
    ("Measured precision", True), ("precision: 0.9", True), ("Precision.", True), ("| Precision |", True),
])
def test_mention_rule(text, mention):
    assert bool(w.MENTION_RE.search(text)) is mention


@pytest.mark.parametrize("s,figs", [
    ("Precision: 0.92.", ["0.92"]), ("is .92.", [".92"]), ("was 0.9.", ["0.9"]), ("0.92, then", ["0.92"]),
    ("v2.13.0", []), ("0.13.0.", []), ("CVSS 9.8.", []), ("2026-10-11", []), ("92%.", ["92%"]),
])
def test_figure_regex_sentence_final(s, figs):
    assert [m.group(0) for m in w.FIGURE_RE.finditer(s)] == figs
