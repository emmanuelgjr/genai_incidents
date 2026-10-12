"""Tests for the Hugging Face exporter."""

from __future__ import annotations

import json

import export_huggingface as hf


def test_build_emits_jsonl_and_card(tmp_path):
    n, jsonl = hf.build(tmp_path)
    assert jsonl.exists() and n > 0
    lines = [l for l in jsonl.read_text(encoding="utf-8").split("\n") if l]
    assert len(lines) == n
    # every newline-delimited line is a valid JSON object with an id
    ids = {json.loads(l)["id"] for l in lines}
    assert len(ids) == n
    # dataset card has the required HF front matter
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert card.startswith("---")
    assert "license: cc-by-4.0" in card
    assert "configs:" in card and "incidents.jsonl" in card


def test_card_defines_source_freshness_because_the_jsonl_ships_it(tmp_path):
    """Defined where it is shipped. The JSONL is a verbatim projection of
    data/incidents.json, so a `source_freshness` marker reaches every HF
    consumer; a card silent about a field it ships hands them a freshness
    signal with no definition. Keyed to the DATA — if no row carries the
    marker there is nothing to define, and this test says so rather than
    demanding boilerplate.
    """
    n, jsonl = hf.build(tmp_path)
    # split("\n"), not splitlines(): the JSONL contract is newline-delimited,
    # and ensure_ascii=False leaves raw U+0085 (NEL) in a handful of
    # `references[].title` values, which splitlines() would treat as line
    # breaks and shred those records.
    lines = [l for l in jsonl.read_text(encoding="utf-8").split("\n") if l]
    marked = [r for r in map(json.loads, lines) if "source_freshness" in r]
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    if not marked:
        assert True  # nothing shipped, nothing to document
        return
    assert "`source_freshness`" in card
    # The three things the definition must contain, per the user's ruling:
    # what the field means, that `active` is emitted-not-live, and where the
    # as-of date comes from.
    assert "stopped refreshing" in card
    assert "emitted on the latest build" in card
    assert "`as_of`" in card and "data/source_freshness.json" in card
    # Cited, not duplicated: the dictionary section stays authoritative.
    assert "DATA_DICTIONARY.md#source-freshness" in card


def test_card_states_review_by_and_that_disputed_rows_stay_counted(tmp_path):
    """D57 + D64. `review_by` rides in the verbatim rows; the card must define it.
    The disputed count comes from data/stats.json (invariant 6) and must equal the
    exported rows' own count, an independent path."""
    stats = json.loads((hf.DATA / "stats.json").read_text(encoding="utf-8"))
    n, jsonl = hf.build(tmp_path)
    rows = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").split("\n") if l]
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "{status, as_of, sources, review_by}" in card
    assert "`review_by` is the date a human is due to re-decide" in card
    assert all("review_by" in r["source_freshness"] for r in rows if "source_freshness" in r)
    disputed = [r for r in rows if r.get("status") == "disputed"]
    assert len(disputed) == stats["disputed_count"] > 0
    assert f"{stats['disputed_count']:,} of the rows above carry `status: disputed`" in card
    assert f"**counted** in the {stats['incident_count']:,}" in card


def test_build_refuses_when_stats_json_disagrees_with_the_rows(tmp_path, monkeypatch):
    import pytest
    bad = tmp_path / "data"
    bad.mkdir()
    (bad / "incidents.json").write_text(
        json.dumps({"version": "9.9.9", "incidents": [{"id": "INC-1", "status": "disputed"}]}),
        encoding="utf-8")
    (bad / "stats.json").write_text(json.dumps({"incident_count": 1, "disputed_count": 0}), encoding="utf-8")
    monkeypatch.setattr(hf, "DATA", bad)
    with pytest.raises(SystemExit):
        hf.build(tmp_path / "out")
