"""D139(a)/(b): the `references_remove` and `fields_clear` curation-override
keys. Mechanisms only; no committed data row uses them yet (D130-3 will)."""
from __future__ import annotations

import copy
import json

import pytest

import merge_and_dedupe as m
from tests.test_cve_rejections import _cve_row
from tests.test_merge_and_dedupe import _setup_tmp_repo

A, B, C, D = (f"https://example.test/{x}" for x in "abcd")
SID = "CVE-2025-0001"


def _row(refs=(A, B, C), **extra):
    return {"id": "INC-09999", "source_ids": [SID],
            "references": [{"title": u[-1], "url": u, "type": "reference"} for u in refs], **extra}


def _urls(row):
    return [r["url"] for r in row["references"]]


def _apply(rows, ov):
    return m.apply_curation_overrides(rows, {SID: ov})


def _refuses(rows, ov, match):
    with pytest.raises(SystemExit) as ei:
        _apply(rows, ov)
    assert match in str(ei.value)
    assert str(ei.value).endswith(m.abort_sentence()), "abort must carry the abort sentence"


def test_removal_drops_named_url_and_keeps_order():
    r = _row((A, B, C, D))
    assert _apply([r], {"references_remove": [C, A]}) == 1
    assert _urls(r) == [B, D]


def test_removal_removes_every_duplicate_occurrence():
    r = _row((A, B, A))
    _apply([r], {"references_remove": [A]})
    assert _urls(r) == [B]


def test_missing_url_refuses():
    r = _row()
    _refuses([r], {"references_remove": [B, "https://example.test/zzz"]}, "not on the row")


def test_near_miss_url_is_not_matched():
    # Exact match: a trailing slash is a different string.
    _refuses([_row()], {"references_remove": [A + "/"]}, "not on the row")


def test_removal_to_empty_refuses():
    _refuses([_row((A, B))], {"references_remove": [A, B]}, "no references")


def test_references_plus_references_remove_refuses():
    _refuses([_row()], {"references": [{"url": D}], "references_remove": [A]}, "cannot be combined")


@pytest.mark.parametrize("bad", [[], "https://x", [A, A], [""], [" " + A], [1]])
def test_malformed_references_remove_refuses(bad):
    _refuses([_row()], {"references_remove": bad}, "references_remove must be")


def test_clear_removes_field():
    r = _row(discovery_method="security-researcher", severity="High")
    _apply([r], {"fields_clear": ["discovery_method"]})
    assert "discovery_method" not in r and r["severity"] == "High"


def test_clear_of_absent_field_is_a_noop():
    r = _row()
    assert _apply([r], {"fields_clear": ["discovery_method"]}) == 1
    assert "discovery_method" not in r


@pytest.mark.parametrize("field", ["id", "title", "date", "references", "status",
                                   "quality_tier", "severity", "no_such_field", "maestro_layers"])
def test_clear_of_non_allowlisted_field_refuses(field):
    r = _row(**{field: "x"} if field not in ("references",) else {})
    before = copy.deepcopy(r)
    _refuses([r], {"fields_clear": [field]}, "may only name")
    assert r == before


def test_clear_and_set_same_field_refuses():
    _refuses([_row()], {"fields_clear": ["discovery_method"], "discovery_method": "other"}, "also sets")


def test_every_clearable_field_is_a_content_field():
    # Otherwise clearing it would not bump `updated`.
    assert m._CLEARABLE_FIELDS <= set(m._CONTENT_FIELDS)


def test_removal_and_clear_change_the_content_snapshot():
    before = _row(discovery_method="other")
    after = copy.deepcopy(before)
    _apply([after], {"references_remove": [A], "fields_clear": ["discovery_method"]})
    assert m._content_snapshot(before) != m._content_snapshot(after)


def test_dangling_key_refuses():
    cur = {"CVE-9999-0000": {"references_remove": [A]}}
    with pytest.raises(SystemExit) as ei:
        m._check_delete_overrides_matched(m._check_delete_overrides(cur), cur, [_row()])
    assert "matched no entry" in str(ei.value)


def test_key_matching_a_row_is_not_dangling():
    cur = {SID: {"references_remove": [A]}}
    m._check_delete_overrides_matched(m._check_delete_overrides(cur), cur, [_row()])


def test_malformed_override_refuses_even_when_unmatched():
    with pytest.raises(SystemExit):
        m.apply_curation_overrides([_row()], {"CVE-9999-0000": {"fields_clear": ["id"]}})


def test_ordinary_overrides_are_unchanged():
    r = _row()
    m.apply_curation_overrides([r], {SID: {"severity": "Low", "_note": "x"}})
    assert r["severity"] == "Low" and "_note" not in r and _urls(r) == [A, B, C]


# ----- through the real build: an upstream addition survives a removal -----

NVD = "https://nvd.nist.gov/vuln/detail/CVE-2025-0003"
BAD, NEW = "https://bad.example.test/home", "https://new.example.test/advisory"


def _build(tmp_path, monkeypatch, refs, override):
    tmp_path.mkdir(parents=True, exist_ok=True)
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "ISSUE88_EXCLUDE", set())
    (ingest / "src.json").write_text(json.dumps(
        [_cve_row("CVE-2025-0003", {"references": [{"url": u} for u in refs]})]), encoding="utf-8")
    (data / "curation_overrides.json").write_text(
        json.dumps({"overrides": {"CVE-2025-0003": override}}), encoding="utf-8")
    m.main()
    return json.loads((data / "incidents.json").read_text(encoding="utf-8"))["incidents"][0]


def test_upstream_addition_survives_removal_override(tmp_path, monkeypatch):
    ov = {"references_remove": [BAD], "_note": "fixture"}
    first = _build(tmp_path / "1", monkeypatch, [NVD, BAD], ov)
    assert _urls(first) == [NVD]
    # upstream gains a reference; the override still removes only BAD
    second = _build(tmp_path / "2", monkeypatch, [NVD, BAD, NEW], ov)
    assert _urls(second) == [NVD, NEW]


def test_build_aborts_when_upstream_stops_carrying_the_url(tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as ei:
        _build(tmp_path, monkeypatch, [NVD, NEW], {"references_remove": [BAD]})
    assert "not on the row" in str(ei.value)


# ----- field clear through the build, on a field the source really carries -----

TECH = "AML.T0000"
TAC = m._ATLAS_TECHNIQUE_TACTICS[TECH]


def _tactic_row(cve="CVE-2025-0003"):
    return _cve_row(cve, {"mitre_atlas": [TECH], "mitre_atlas_tactics": list(TAC)})


def _build_rows(tmp_path, monkeypatch, rows, override):
    tmp_path.mkdir(parents=True, exist_ok=True)
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "ISSUE88_EXCLUDE", set())
    (ingest / "src.json").write_text(json.dumps(rows), encoding="utf-8")
    if override is not None:
        (data / "curation_overrides.json").write_text(
            json.dumps({"overrides": {"CVE-2025-0003": override}}), encoding="utf-8")
    m.main()
    return data, ingest


def _by_cve(data):
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    return {e["cve_ids"][0]: e for e in full}


def test_build_clear_removes_a_field_the_source_carries(tmp_path, monkeypatch):
    control = _by_cve(_build_rows(tmp_path / "c", monkeypatch, [_tactic_row()], None)[0])
    assert control["CVE-2025-0003"]["mitre_atlas_tactics"], "control: the source row carries the field"
    row = _by_cve(_build_rows(tmp_path / "o", monkeypatch, [_tactic_row()],
                              {"fields_clear": ["mitre_atlas_tactics"]})[0])["CVE-2025-0003"]
    assert "mitre_atlas_tactics" not in row and row["mitre_atlas"] == [TECH]


# ----- retained rows: upstream drops a row that carries a delete override -----

def _drop_upstream(data, ingest):
    (ingest / "src.json").write_text(json.dumps([_cve_row("CVE-2025-0004")]), encoding="utf-8")
    m.main()
    return _by_cve(data)


def test_retained_row_keeps_url_removed_and_build_passes(tmp_path, monkeypatch):
    refs = [{"url": NVD}, {"url": BAD}]
    data, ingest = _build_rows(tmp_path, monkeypatch, [_cve_row("CVE-2025-0003", {"references": refs})],
                               {"references_remove": [BAD]})
    assert _urls(_by_cve(data)["CVE-2025-0003"]) == [NVD]
    after = _drop_upstream(data, ingest)
    assert after["CVE-2025-0003"]["source_status"] == "retained"
    assert _urls(after["CVE-2025-0003"]) == [NVD]


def test_retained_row_removes_a_url_it_still_carries(tmp_path, monkeypatch):
    # Override added after the row went retained: still-present URL is removed.
    refs = [{"url": NVD}, {"url": BAD}]
    data, ingest = _build_rows(tmp_path, monkeypatch, [_cve_row("CVE-2025-0003", {"references": refs})], None)
    (data / "curation_overrides.json").write_text(json.dumps(
        {"overrides": {"CVE-2025-0003": {"references_remove": [BAD]}}}), encoding="utf-8")
    assert _urls(_drop_upstream(data, ingest)["CVE-2025-0003"]) == [NVD]


def test_retained_row_cannot_be_emptied(tmp_path, monkeypatch):
    data, ingest = _build_rows(tmp_path, monkeypatch, [_cve_row("CVE-2025-0003", {"references": [{"url": NVD}]})], None)
    (data / "curation_overrides.json").write_text(json.dumps(
        {"overrides": {"CVE-2025-0003": {"references_remove": [NVD]}}}), encoding="utf-8")
    with pytest.raises(SystemExit) as ei:
        _drop_upstream(data, ingest)
    assert "no references" in str(ei.value)


def test_retained_tactics_clear_survives_refresh_atlas_codes(tmp_path, monkeypatch):
    import datetime
    day = {"d": datetime.date(2026, 1, 1)}
    monkeypatch.setattr(m, "utc_today", lambda: day["d"])
    ov = {"fields_clear": ["mitre_atlas_tactics"]}
    data, ingest = _build_rows(tmp_path, monkeypatch, [_tactic_row()], ov)
    built = _by_cve(data)["CVE-2025-0003"]
    assert "mitre_atlas_tactics" not in built
    day["d"] = datetime.date(2026, 1, 2)
    after = _drop_upstream(data, ingest)["CVE-2025-0003"]
    assert after["source_status"] == "retained" and after["mitre_atlas"] == [TECH]
    assert "mitre_atlas_tactics" not in after, "refresh_atlas_codes re-added the cleared tactics"
    # refresh adds and the clear removes: the NET change is nothing, so a later
    # day's build must not bump `updated` (or it would churn on every build).
    day["d"] = datetime.date(2026, 1, 3)
    m.main()
    again = _by_cve(data)["CVE-2025-0003"]
    assert after["updated"] == again["updated"] == built["updated"]


def test_retained_discovery_method_clear(tmp_path, monkeypatch):
    # discovery_method reaches a row only via an override, so build 1 SETS it;
    # the override is then rewritten to clear it, and the carried prior loses it.
    data, ingest = _build_rows(tmp_path, monkeypatch, [_cve_row("CVE-2025-0003")],
                               {"discovery_method": "security-researcher"})
    assert _by_cve(data)["CVE-2025-0003"]["discovery_method"] == "security-researcher"
    (data / "curation_overrides.json").write_text(json.dumps(
        {"overrides": {"CVE-2025-0003": {"fields_clear": ["discovery_method"]}}}), encoding="utf-8")
    after = _drop_upstream(data, ingest)["CVE-2025-0003"]
    assert after["source_status"] == "retained" and "discovery_method" not in after


def test_override_matching_no_row_even_after_retention_still_refuses(tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as ei:
        _build_rows(tmp_path, monkeypatch, [_cve_row("CVE-2025-0004")],
                    {"references_remove": [BAD]})
    assert "matched no entry" in str(ei.value)


# ----- removal applies after the dedupe union of several sources -----

def test_removal_applies_after_union_of_two_sources(tmp_path, monkeypatch):
    tmp_path.mkdir(parents=True, exist_ok=True)
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "ISSUE88_EXCLUDE", set())
    # Two sources, distinct source_ids, same CVE; BOTH carry BAD. The override is
    # keyed to the first source's id, so a removal applied per source before the
    # union would leave the second source's copy of BAD in the merged row.
    for name, sid, extra in (("a.json", "CVE-2025-0003", NEW),
                             ("b.json", "ALT-0003", "https://other.example.test/x")):
        (ingest / name).write_text(json.dumps([_cve_row("CVE-2025-0003", {
            "source_id": sid, "references": [{"url": NVD}, {"url": BAD}, {"url": extra}]})]), encoding="utf-8")
    (data / "curation_overrides.json").write_text(json.dumps(
        {"overrides": {"CVE-2025-0003": {"references_remove": [BAD]}}}), encoding="utf-8")
    m.main()
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    assert len(full) == 1 and set(full[0]["source_ids"]) == {"CVE-2025-0003", "ALT-0003"}
    urls = _urls(full[0])
    assert BAD not in urls and NEW in urls and "https://other.example.test/x" in urls
