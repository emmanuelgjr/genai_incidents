"""v2.13.0 item 8 -- STIX `modified` rule and x_source_freshness (D57).

    modified = <updated date> T00:00:00.<EXPORTER_VERSION:03d>Z, clamped >= created

`updated` moves exactly when an entry's content fields change (the merge), so
an unchanged entry is byte-identical across builds and a changed one moves
forward; EXPORTER_VERSION moves every object when the exporter itself changes.
Design record: docs/audits/ws6-v2130-export-integrity-2026-10-11.md.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import export_stix as s

ROOT = Path(__file__).resolve().parents[1]
_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

_INCIDENTS = [
    {
        "id": "INC-00001", "title": "Example RCE", "description": "A flaw.",
        "date": "2026-01-02", "year": 2026, "severity": "High",
        "attack_vector": "rce", "category": "vulnerability-disclosure",
        "quality_tier": "reviewed", "corpus": "security",
        "owasp_llm": ["LLM10"], "owasp_asi": [], "nist_ai_rmf": ["MEASURE-2.7"],
        "mitre_atlas": ["AML.T0050"], "cve_ids": ["CVE-2026-0001"],
        "references": [{"title": "Advisory", "url": "https://example.com/a", "type": "advisory"}],
        "tags": ["x"], "added": "2026-01-03", "updated": "2026-01-04",
    },
    {
        "id": "INC-00002", "title": "Example harm", "description": "Another.",
        "date": "2025", "year": 2025, "severity": "Medium", "attack_vector": "other",
        "mitre_atlas": ["AML.T0050"], "cve_ids": [], "references": [],
        "added": "2025-06-01", "updated": "2025-06-01",
    },
]


def _real_rows():
    raw = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    return [e for e in raw["incidents"] if e.get("status") != "retracted"]


def _by_incident(bundle, iid):
    """The incident SDO plus its relationships, keyed by id."""
    sdo = next(o for o in bundle["objects"] if o.get("x_incident_id") == iid)
    rels = [o for o in bundle["objects"]
            if o["type"] == "relationship" and o["source_ref"] == sdo["id"]]
    return {o["id"]: o for o in [sdo, *rels]}


def test_modified_is_updated_date_plus_exporter_version():
    sdo = next(o for o in s.build_bundle(_INCIDENTS)["objects"] if o.get("x_incident_id") == "INC-00001")
    assert sdo["modified"] == f"2026-01-04T00:00:00.{s.EXPORTER_VERSION:03d}Z"
    assert sdo["created"] == "2026-01-03T00:00:00.000Z"


def test_unchanged_entry_is_byte_identical_when_a_different_entry_changes():
    before = _by_incident(s.build_bundle(_INCIDENTS), "INC-00001")
    changed = copy.deepcopy(_INCIDENTS)
    changed[1]["description"] = "Another, corrected."
    changed[1]["updated"] = "2026-03-01"          # what the merge does on a content change
    after = _by_incident(s.build_bundle(changed), "INC-00001")
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)


def test_two_builds_of_the_same_input_are_byte_identical():
    a = json.dumps(s.build_bundle(_INCIDENTS), sort_keys=True)
    b = json.dumps(s.build_bundle(copy.deepcopy(_INCIDENTS)), sort_keys=True)
    assert a == b


def test_content_change_bumps_modified_and_only_that_entrys_objects():
    changed = copy.deepcopy(_INCIDENTS)
    changed[1]["description"] = "Another, corrected."
    changed[1]["updated"] = "2026-03-01"
    old = _by_incident(s.build_bundle(_INCIDENTS), "INC-00002")
    new = _by_incident(s.build_bundle(changed), "INC-00002")
    assert old.keys() == new.keys()
    for oid in old:
        assert new[oid]["modified"] > old[oid]["modified"], oid
        assert new[oid]["modified"].startswith("2026-03-01")
        a, b = dict(old[oid]), dict(new[oid])
        for d in (a, b):
            d.pop("modified"); d.pop("description", None)
        assert a == b


def test_exporter_version_bump_moves_every_modified_by_one_ms_and_nothing_else(monkeypatch):
    base = s.build_bundle(_INCIDENTS)
    monkeypatch.setattr(s, "EXPORTER_VERSION", s.EXPORTER_VERSION + 1)
    bumped = s.build_bundle(_INCIDENTS)
    assert [o["id"] for o in base["objects"]] == [o["id"] for o in bumped["objects"]]
    for a, b in zip(base["objects"], bumped["objects"]):
        assert b["modified"] > a["modified"], a["id"]
        assert b["modified"][:20] == a["modified"][:20]
        assert int(b["modified"][20:23]) == int(a["modified"][20:23]) + 1
        a2, b2 = dict(a), dict(b)
        a2.pop("modified"); b2.pop("modified")
        assert a2 == b2


def test_exporter_version_overflowing_the_ms_field_is_refused(monkeypatch):
    monkeypatch.setattr(s, "EXPORTER_VERSION", 1000)
    with pytest.raises(ValueError):
        s.build_bundle(_INCIDENTS)


def test_modified_never_precedes_created_even_when_updated_is_before_added():
    bad = copy.deepcopy(_INCIDENTS[:1])
    bad[0]["added"], bad[0]["updated"] = "2026-05-01", "2026-01-01"
    for o in s.build_bundle(bad)["objects"]:
        assert _TS.match(o["created"]) and _TS.match(o["modified"])
        assert o["modified"] >= o["created"], o["id"]


def test_real_bundle_every_object_has_valid_ordered_timestamps():
    for o in s.build_bundle(_real_rows())["objects"]:
        assert _TS.match(o["created"]) and _TS.match(o["modified"]), o["id"]
        assert o["modified"] >= o["created"], o["id"]


def test_every_exported_entry_field_is_content_or_explicitly_declared():
    """The rule is only as good as `updated`. Mutate each field of a real entry
    in turn; every field that changes the SDO must be one of the merge's
    `_CONTENT_FIELDS` (so `updated` moves with it) or be declared below. A NEW
    exported field that is neither fails here and forces a decision: add it to
    `_CONTENT_FIELDS`, or bump EXPORTER_VERSION whenever it is re-derived."""
    import merge_and_dedupe as md

    structural = {"id", "added", "updated"}
    # Exported, NOT in _CONTENT_FIELDS: re-deriving these does not move
    # `updated`, so a change reaches STIX consumers only through an
    # EXPORTER_VERSION bump (audit note, ruling R1).
    # D73 (2026-10-11) moved tier/quality_tier/corpus/content_license INTO
    # _CONTENT_FIELDS; only source_freshness (describes unchanged content) remains.
    derived_by_exporter_version = {"source_freshness"}
    sample: dict[str, tuple[dict, object]] = {}
    for e in _real_rows():
        for k, v in e.items():
            if k not in sample or (v and not sample[k][1]):
                sample[k] = (e, v)

    def mutate(v):
        if isinstance(v, bool):
            return not v
        if isinstance(v, (int, float)):
            return v + 1
        if isinstance(v, str):
            return v + "~"
        if isinstance(v, list):
            return v + ([{"url": "https://x.test/~", "title": "t", "type": "reference"}]
                        if v and isinstance(v[0], dict) else ["~x"])
        if isinstance(v, dict):
            return {**v, "zz": "~"}
        return "~"

    exported = set()
    for k, (e, v) in sample.items():
        e2 = copy.deepcopy(e)
        e2[k] = mutate(v)
        if s.build_bundle([e]) != s.build_bundle([e2]):
            exported.add(k)
    assert {"title", "description", "cve_ids", "tier"} <= exported, "the probe itself is broken"
    undeclared = exported - set(md._CONTENT_FIELDS) - structural - derived_by_exporter_version
    assert not undeclared, (
        f"fields {sorted(undeclared)} change the STIX SDO but are neither in "
        f"merge_and_dedupe._CONTENT_FIELDS nor declared: `modified` would not move for them")
    # the declared set is not stale either: every declared field really is exported
    assert derived_by_exporter_version <= exported


# --- x_source_freshness (D57) ----------------------------------------------

_MARK = {"status": "stale", "as_of": "2026-05-31", "sources": ["airi_navigator"],
         "review_by": "2027-01-07"}


def _with_marker(marker):
    rows = copy.deepcopy(_INCIDENTS)
    if marker is not None:
        rows[1]["source_freshness"] = marker
    return s.build_bundle(rows)


def test_x_source_freshness_only_on_marked_sdos_with_exact_keys():
    b = _with_marker(_MARK)
    incs = {o["x_incident_id"]: o for o in b["objects"] if o["type"] == "x-genai-incident"}
    assert incs["INC-00002"]["x_source_freshness"] == _MARK
    assert "x_source_freshness" not in incs["INC-00001"]
    assert "stale" not in incs["INC-00002"]["labels"]          # never pushed into labels
    assert "airi_navigator" not in incs["INC-00002"]["labels"]


def test_x_source_freshness_drops_null_keys_rather_than_emitting_them():
    b = _with_marker({**_MARK, "review_by": None})
    sdo = next(o for o in b["objects"] if o.get("x_incident_id") == "INC-00002")
    assert "review_by" not in sdo["x_source_freshness"]
    assert None not in sdo["x_source_freshness"].values()


def test_x_source_freshness_absent_everywhere_when_nothing_is_marked():
    assert not any("x_source_freshness" in o for o in _with_marker(None)["objects"])


def test_real_bundle_x_source_freshness_set_equals_marked_rows():
    rows = _real_rows()
    marked = {e["id"]: e["source_freshness"] for e in rows if e.get("source_freshness")}
    emitted = {o["x_incident_id"]: o["x_source_freshness"]
               for o in s.build_bundle(rows)["objects"]
               if o["type"] == "x-genai-incident" and "x_source_freshness" in o}
    assert emitted == marked
    assert len(marked) > 0
    # independent path: the review date is the registry hold's `until`
    reg = json.loads((ROOT / "data" / "source_freshness.json").read_text(encoding="utf-8"))
    until = {reg["sources"][k]["hold"]["until"] for v in emitted.values() for k in v["sources"]}
    assert {v.get("review_by") for v in emitted.values()} == until
