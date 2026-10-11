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


def test_committed_sample_reproduces_byte_for_byte():
    """The committed sample re-derives exactly from the data it was drawn
    from. Skipped (with the reason) once data/incidents.json moves past the
    pinned hash -- reproduction is anchored to that data, see frame.json."""
    frame = json.loads((AUDIT / "frame.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    if ps.canonical_sha256(data["incidents"]) != frame["data_incidents_sha256"]:
        pytest.skip("data/incidents.json changed since the 2026-10-11 draw; reproduce against the pinned blob")
    assert ps.main(["--check"]) == 0
    assert ps.main(["--check", "--seed", "7"]) == 1  # a different seed does NOT reproduce


def test_check_fires_on_tampered_copy(tmp_path):
    frame = json.loads((AUDIT / "frame.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    if ps.canonical_sha256(data["incidents"]) != frame["data_incidents_sha256"]:
        pytest.skip("data/incidents.json changed since the 2026-10-11 draw")
    d = tmp_path / "a"
    shutil.copytree(AUDIT, d)
    assert ps.main(["--check", "--out-dir", str(d)]) == 0
    p = d / "sample.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"INC-07644"', '"INC-07645"', 1), encoding="utf-8")
    assert ps.main(["--check", "--out-dir", str(d)]) == 1


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
def test_gate_passes_on_committed_tree_with_unratified_warning():
    problems, line = v.check_precision_audit("2.12.0")
    assert problems == []
    assert "UNRATIFIED" in line


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


def test_gate_fires_on_unratified_past_grace(tmp_path):
    root = _copy_root(tmp_path)
    assert v.check_precision_audit("2.13.9", root)[0] == []
    assert any("UNRATIFIED" in p for p in v.check_precision_audit("2.14.0", root)[0])
    assert any("UNRATIFIED" in p for p in v.check_precision_audit("3.0.0", root)[0])


def test_gate_ratified_marker(tmp_path):
    root = _copy_root(tmp_path)
    _edit(_audit(root) / "pending_authorization.json", '"<USER-DECISION-ID>"', '"D99"')
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
