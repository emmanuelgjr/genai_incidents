"""User ruling D130(b): ``status: unverified`` is treated exactly like
``retracted`` everywhere downstream, counted in its own ``unverified_count``,
and kept in the full JSON with its ``status_reason``.

No committed row is unverified when this lands (``unverified_count`` is 0), so
every claim is proved on a fixture: one merge build from a tmp corpus whose
curation overrides mark rows unverified, then each producer run over THAT
build's output. Each producer test carries a standing control row, so an
export that drops everything (or nothing) fails too.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

import merge_and_dedupe as m
import validate
from tests.test_cve_rejections import _cve_row
from tests.test_merge_and_dedupe import _setup_tmp_repo

ROOT = Path(__file__).resolve().parents[1]
REASON = {"code": "no-confirmed-source", "as_of": "2026-10-14"}
SNAP = {"CVE-2099-0001": {"state": "REJECTED", "checked": "2026-10-03"},
        "CVE-2099-0002": {"state": "PUBLISHED", "disputed": True, "checked": "2026-10-03"}}
STANDING_CVE, UNVERIFIED_CVE = "CVE-2025-0003", "CVE-2025-0004"
RETRACTED_CVE, DISPUTED_CVE = "CVE-2099-0001", "CVE-2099-0002"
# Distinct titles, so no fixture row can be mistaken for another.
TITLES = {STANDING_CVE: "Prompt injection in Alpha agent framework",
          UNVERIFIED_CVE: "Bravo vector store leaks tenant embeddings",
          RETRACTED_CVE: "Charlie plugin sandbox escape",
          DISPUTED_CVE: "Delta model server path traversal"}


def _row(c):
    return _cve_row(c, {"title": TITLES[c]})


def _override(**extra):
    return {"status": "unverified", "status_reason": dict(REASON), "_note": "fixture", **extra}


def _build(tmp_path, monkeypatch, overrides=None):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    # The real issue-#88 exclude list names INC-00004, which a 4-row tmp build
    # allocates; it would be scope-purged and the fixture would lose a row.
    monkeypatch.setattr(m, "ISSUE88_EXCLUDE", set())
    snap = tmp_path / "cve_rejections.json"
    snap.write_text(json.dumps({"states": SNAP}), encoding="utf-8")
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", snap)
    (ingest / "src.json").write_text(json.dumps(
        [_row(c) for c in (STANDING_CVE, UNVERIFIED_CVE, RETRACTED_CVE, DISPUTED_CVE)]),
        encoding="utf-8")
    if overrides is None:
        # The retracted and disputed rows also ask for unverified, to pin the
        # precedence: retracted wins, unverified replaces disputed.
        overrides = {c: _override() for c in (UNVERIFIED_CVE, RETRACTED_CVE, DISPUTED_CVE)}
    (data / "curation_overrides.json").write_text(
        json.dumps({"overrides": overrides}), encoding="utf-8")
    m.main()
    return data


@pytest.fixture
def built(tmp_path, monkeypatch):
    data = _build(tmp_path, monkeypatch)
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    ids = {e["cve_ids"][0]: e["id"] for e in full["incidents"]}
    return data, full, ids


# ----- schema -----

def _schema():
    return json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))


def test_schema_accepts_unverified_and_pairs_it_with_its_code(built):
    _, full, _ = built
    v = jsonschema.Draft202012Validator(_schema())
    row = next(e for e in full["incidents"] if e.get("status") == "unverified")
    assert list(v.iter_errors(row)) == []
    wrong = {**row, "status_reason": {"code": "cve-rejected", "as_of": "2026-10-14"}}
    assert list(v.iter_errors(wrong)), "unverified must carry no-confirmed-source"
    bare = {k: val for k, val in row.items() if k != "status_reason"}
    assert list(v.iter_errors(bare)), "status without status_reason"
    retr = {**row, "status": "retracted"}
    assert list(v.iter_errors(retr)), "no-confirmed-source cannot ride on retracted"


def test_packaged_schema_matches():
    a = (ROOT / "schema" / "incident.schema.json").read_bytes()
    b = (ROOT / "src" / "genai_incidents" / "schema" / "incident.schema.json").read_bytes()
    assert a == b


# ----- the merge (the only way a row becomes unverified) -----

def test_build_marks_keeps_and_excludes(built):
    _, full, ids = built
    by = {e["cve_ids"][0]: e for e in full["incidents"]}
    assert len(full["incidents"]) == 4, "never deleted"
    assert by[UNVERIFIED_CVE]["status"] == "unverified"
    assert by[UNVERIFIED_CVE]["status_reason"] == REASON
    assert by[RETRACTED_CVE]["status"] == "retracted", "retracted wins over unverified"
    assert by[DISPUTED_CVE]["status"] == "unverified", "unverified replaces disputed"
    assert "status" not in by[STANDING_CVE]
    assert (full["incident_count"], full["retracted_count"], full["unverified_count"]) == (1, 1, 2)
    assert validate.check_status(full, {RETRACTED_CVE}, {DISPUTED_CVE}) == []


def test_slim_envelope_and_rows_carry_unverified(built):
    data, full, ids = built
    slim = json.loads((data / "incidents.min.json").read_text(encoding="utf-8"))
    assert (slim["incident_count"], slim["unverified_count"]) == (1, 2)
    assert {e["id"]: e.get("status") for e in slim["incidents"]}[ids[UNVERIFIED_CVE]] == "unverified"
    assert validate.check_envelope(slim) == []


def test_rebuild_is_byte_stable(tmp_path, monkeypatch):
    data = _build(tmp_path, monkeypatch)
    first = (data / "incidents.json").read_bytes()
    m.main()
    assert (data / "incidents.json").read_bytes() == first


def test_removing_the_override_restores_the_entry(tmp_path, monkeypatch):
    data = _build(tmp_path, monkeypatch)
    (data / "curation_overrides.json").write_text(json.dumps({"overrides": {}}), encoding="utf-8")
    m.main()
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    by = {e["cve_ids"][0]: e for e in full["incidents"]}
    assert "status" not in by[UNVERIFIED_CVE]
    assert by[DISPUTED_CVE]["status"] == "disputed"
    assert "unverified_count" not in full, "emitted only when non-zero"
    assert (full["incident_count"], full["retracted_count"]) == (3, 1)


def test_no_unverified_rows_leaves_envelope_shape_unchanged(tmp_path, monkeypatch):
    data = _build(tmp_path, monkeypatch, overrides={})
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    assert list(full) == ["version", "generated", "description", "schema",
                          "incident_count", "retracted_count", "incidents"]


@pytest.mark.parametrize("bad", [
    {"status": "retracted", "status_reason": {"code": "cve-rejected", "as_of": "2026-10-14"}},
    {"status": "unverified", "status_reason": {"code": "cve-disputed", "as_of": "2026-10-14"}},
    {"status": "unverified", "status_reason": {"code": "no-confirmed-source", "as_of": "14 Oct"}},
    {"status": "unverified", "status_reason": {"code": "no-confirmed-source"}},
    {"status": "unverified"},
    {"status_reason": dict(REASON)},
])
def test_malformed_status_override_fails_the_build(tmp_path, monkeypatch, bad):
    with pytest.raises(SystemExit, match="status override"):
        _build(tmp_path, monkeypatch, overrides={UNVERIFIED_CVE: {**bad, "_note": "x"}})


def test_generic_override_step_never_writes_status():
    e = {"source_ids": ["S-1"], "quality_tier": "reviewed"}
    m.apply_curation_overrides([e], {"S-1": _override(quality_tier="auto")})
    assert "status" not in e and "status_reason" not in e
    assert e["quality_tier"] == "auto"


def test_unverified_does_not_touch_quality_tier():
    e = {"source_ids": ["S-1"], "quality_tier": "curated"}
    assert m._apply_unverified_override(e, {"S-1": _override()}) is True
    assert e["quality_tier"] == "curated"


def test_retained_prior_gets_the_decision_too(tmp_path, monkeypatch):
    """Retained priors bypass step 4g; the step-6 re-derivation must reach them."""
    data = _build(tmp_path, monkeypatch, overrides={})
    ingest = m.INGEST
    # Drop the row from every input so it is carried forward as `retained`.
    (ingest / "src.json").write_text(json.dumps(
        [_row(c) for c in (STANDING_CVE, RETRACTED_CVE, DISPUTED_CVE)]), encoding="utf-8")
    (data / "curation_overrides.json").write_text(
        json.dumps({"overrides": {UNVERIFIED_CVE: _override()}}), encoding="utf-8")
    m.main()
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    row = next(e for e in full["incidents"] if e["cve_ids"] == [UNVERIFIED_CVE])
    assert row["source_status"] == "retained"
    assert row["status"] == "unverified"


def test_retained_prior_sheds_a_withdrawn_decision(tmp_path, monkeypatch):
    """A retained prior is carried verbatim; with no CVE snapshot nothing else
    pops its `status`, so step 6 must drop a stale `unverified` itself."""
    data = _build(tmp_path, monkeypatch)
    (m.INGEST / "src.json").write_text(json.dumps([_row(STANDING_CVE)]), encoding="utf-8")
    (data / "curation_overrides.json").write_text(json.dumps({"overrides": {}}), encoding="utf-8")
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", tmp_path / "absent.json")
    m.main()
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    row = next(e for e in full["incidents"] if e["cve_ids"] == [UNVERIFIED_CVE])
    assert row["source_status"] == "retained"
    assert "status" not in row and "status_reason" not in row


# ----- validate.py -----

def test_validator_counts_and_code():
    row = {"id": "INC-1", "status": "unverified", "status_reason": dict(REASON)}
    ok = {"incident_count": 1, "retracted_count": 0, "unverified_count": 1,
          "incidents": [row, {"id": "INC-2"}]}
    assert validate.check_status(ok) == []
    assert validate.check_envelope({**ok, "unverified_count": 0})
    assert validate.check_envelope({k: v for k, v in ok.items() if k != "unverified_count"})
    assert validate.check_envelope({**ok, "incident_count": 2}), "unverified row counted"
    assert validate.check_envelope({"incident_count": 1, "unverified_count": 0, "incidents": [{"id": "x"}]})
    bad = {**ok, "incidents": [{**row, "status_reason": {"code": "cve-rejected", "as_of": "2026-10-14"}}]}
    assert any("no-confirmed-source" in p for p in validate.check_status(bad))


# ----- producers, each over the fixture build -----

def _texts(root: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(root.rglob("*")) if p.is_file())


def _assert_excluded(text: str, ids: dict):
    assert ids[STANDING_CVE] in text, "control: the standing row must be exported"
    for c in (UNVERIFIED_CVE, DISPUTED_CVE, RETRACTED_CVE):
        assert ids[c] not in text, f"{c} ({ids[c]}) leaked into the export"


def test_stix_excludes_unverified(built, tmp_path, monkeypatch):
    import export_stix
    data, _, ids = built
    monkeypatch.setattr(export_stix, "DATA", data)
    monkeypatch.setattr(export_stix, "DOCS_DATA", tmp_path / "docs_data")
    export_stix.main()
    _assert_excluded((data / "incidents.stix.json").read_text(encoding="utf-8"), ids)


def test_taxii_excludes_unverified(built, tmp_path, monkeypatch):
    import export_taxii
    data, _, ids = built
    out = tmp_path / "taxii2"
    monkeypatch.setattr(export_taxii, "DATA", data)
    monkeypatch.setattr(export_taxii, "OUT", out)
    export_taxii.main()
    _assert_excluded(_texts(out), ids)


def test_misp_excludes_unverified(built, tmp_path, monkeypatch):
    import export_misp
    data, _, ids = built
    out = tmp_path / "misp"
    monkeypatch.setattr(export_misp, "DATA", data)
    monkeypatch.setattr(export_misp, "OUT", out)
    export_misp.main()
    _assert_excluded(_texts(out), ids)


def test_huggingface_excludes_unverified(built, tmp_path, monkeypatch):
    import export_huggingface as hf
    data, _, ids = built
    monkeypatch.setattr(hf, "DATA", data)
    n, jsonl = hf.build(tmp_path / "hf")
    assert n == 1
    _assert_excluded(jsonl.read_text(encoding="utf-8"), ids)


def test_site_payload_excludes_unverified(built, tmp_path, monkeypatch):
    import gen_docs_core_data as g
    data, _, ids = built
    docs = tmp_path / "docs_data"
    monkeypatch.setattr(g, "SRC", data / "incidents.min.json")
    monkeypatch.setattr(g, "DOCS_DATA", docs)
    monkeypatch.setattr(g, "CORE_OUT", docs / "incidents.core.json")
    monkeypatch.setattr(g, "DETAIL_DIR", docs / "detail")
    g.main()
    core = json.loads((docs / "incidents.core.json").read_text(encoding="utf-8"))
    assert core["incident_count"] == 1
    _assert_excluded(_texts(docs), ids)


def _render(data: Path, tmp_path: Path, monkeypatch):
    import render_markdown as r
    monkeypatch.setattr(r, "DATA", data)
    monkeypatch.setattr(r, "OUT", tmp_path / "INCIDENTS.md")
    for name in ("SHARD_DIR", "SITE_DATA_DIR", "CHART_DIR", "PKG_DATA_DIR",
                 "PKG_SCHEMA_DIR", "INCIDENT_PAGE_DIR"):
        monkeypatch.setattr(r, name, tmp_path / name.lower())
    r.render()
    return json.loads((data / "stats.json").read_text(encoding="utf-8"))


def test_stats_and_incidents_md_exclude_and_count_unverified(built, tmp_path, monkeypatch):
    data, full, ids = built
    stats = _render(data, tmp_path, monkeypatch)
    assert (stats["incident_count"], stats["retracted_count"], stats["unverified_count"],
            stats["disputed_count"]) == (1, 1, 2, 0)
    md = (tmp_path / "INCIDENTS.md").read_text(encoding="utf-8")
    assert "- **Total incidents:** **1**" in md
    assert "unverified (NOT counted; no confirmed primary source): 2" in md
    shards = _texts(tmp_path / "shard_dir")
    assert ids[UNVERIFIED_CVE] in shards, "the ID keeps a card"
    assert "**UNVERIFIED**" in shards and "reviewed 2026-10-14" in shards


def test_check_stats_drift_rederives_unverified(built, tmp_path, monkeypatch):
    import check_stats_drift as c
    data, full, _ = built
    stats = _render(data, tmp_path, monkeypatch)
    slim = json.loads((data / "incidents.min.json").read_text(encoding="utf-8"))["incidents"]
    assert c.derive_counts(full["incidents"])["unverified_count"] == 2
    assert c.check_stats_vs_corpus(stats, full["incidents"], slim) == []
    stale = {**stats, "unverified_count": 0, "incident_count": 3}
    errs = c.check_stats_vs_corpus(stale, full["incidents"], slim)
    assert any("unverified_count" in e for e in errs) and any("incident_count" in e for e in errs)


def test_build_manifest_carries_unverified_count(built, tmp_path, monkeypatch):
    import export_integrity as ei
    data, _, _ = built
    stats = _render(data, tmp_path, monkeypatch)
    man = ei.build_manifest(stats=stats, commit="0" * 40,
                            built=("2026-10-14T00:00:00Z", "commit-date"), dirty=False)
    assert man["unverified_count"] == 2
    assert ei.validate_manifest(man) == []
    missing = {k: v for k, v in man.items() if k != "unverified_count"}
    assert ei.validate_manifest(missing), "manifest schema requires unverified_count"


def test_stats_docs_formatter_registered():
    import stats_docs_lib as lib
    assert lib.FORMATTERS["unverified_count"]({"unverified_count": 1234}) == "1,234"
