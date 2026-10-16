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
    with pytest.raises(SystemExit) as ei:
        m.apply_curation_overrides([_row()], {"CVE-9999-0000": {"references_remove": [A]}})
    assert "matched no entry" in str(ei.value)


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


def test_build_clear_removes_field_from_output(tmp_path, monkeypatch):
    row = _build(tmp_path, monkeypatch, [NVD], {"fields_clear": ["discovery_method"]})
    assert "discovery_method" not in row


def test_instruction_keys_are_not_copied_onto_the_row():
    r = _row(discovery_method="other")
    _apply([r], {"references_remove": [A], "fields_clear": ["discovery_method"]})
    assert "references_remove" not in r and "fields_clear" not in r
