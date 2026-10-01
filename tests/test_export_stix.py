"""Tests for the STIX 2.1 exporter."""

from __future__ import annotations

import export_stix as s


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


def _bundle():
    return s.build_bundle(_INCIDENTS)


def test_bundle_shape_and_counts():
    b = _bundle()
    assert b["type"] == "bundle" and b["id"].startswith("bundle--")
    from collections import Counter
    by = Counter(o["type"] for o in b["objects"])
    assert by["x-genai-incident"] == 2
    assert by["attack-pattern"] == 1          # AML.T0050 shared across both
    assert by["vulnerability"] == 1           # one CVE
    assert by["relationship"] == 3            # 2 'uses' + 1 'exploits'


def test_ids_are_deterministic():
    assert s.build_bundle(_INCIDENTS) == s.build_bundle(_INCIDENTS)


def test_incident_sdo_has_required_stix_and_custom_fields():
    b = _bundle()
    inc = next(o for o in b["objects"] if o["type"] == "x-genai-incident")
    for k in ("spec_version", "id", "created", "modified", "name"):
        assert inc.get(k), k
    assert inc["created"] == "2026-01-03T00:00:00.000Z"   # from `added`
    assert inc["x_incident_id"] == "INC-00001"
    assert inc["x_severity"] == "High"
    # year-only date is normalised to a full RFC3339 timestamp
    inc2 = next(o for o in b["objects"]
                if o["type"] == "x-genai-incident" and o["x_incident_id"] == "INC-00002")
    assert inc2["created"] == "2025-06-01T00:00:00.000Z"


def test_relationship_refs_resolve():
    b = _bundle()
    ids = {o["id"] for o in b["objects"]}
    for rel in (o for o in b["objects"] if o["type"] == "relationship"):
        assert rel["source_ref"] in ids and rel["target_ref"] in ids


# --- x_content_license (D14; interim heuristic retired at D15) -------------


def test_non_obligated_sdo_carries_no_content_license():
    b = _bundle()
    for inc in (o for o in b["objects"] if o["type"] == "x-genai-incident"):
        assert "x_content_license" not in inc


def test_content_license_field_emitted_verbatim():
    """A populated `content_license` field is emitted on `x_content_license`
    verbatim, unmodified in any way."""
    real_marker = {
        "source": "aiaaic",
        "license": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution": "AIAAIC Repository",
        "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
        "obligations": ["attribution"],  # a narrowed/waived obligation set
    }
    incidents = _INCIDENTS + [{
        "id": "INC-00005", "title": "Post-rebuild AIAAIC row", "description": "x",
        "date": "2026-02-01", "year": 2026, "severity": "Low",
        "content_license": real_marker,
        "added": "2026-02-01", "updated": "2026-02-01",
    }]
    b = s.build_bundle(incidents)
    inc = next(o for o in b["objects"]
               if o["type"] == "x-genai-incident" and o["x_incident_id"] == "INC-00005")
    assert inc["x_content_license"] == real_marker


def test_source_ids_or_tags_alone_no_longer_trigger_marker():
    """D15: the interim `source_ids`/`tags` AIAAIC-origin heuristic is
    retired. A row that matches those old signals but has no `content_license`
    field must carry no `x_content_license` at all -- proving the field is
    now the sole and authoritative source, with no silent heuristic
    fallback re-adding a marker behind it."""
    incidents = _INCIDENTS + [{
        "id": "INC-00006", "title": "Old heuristic signals, no field", "description": "x",
        "date": "2026-02-01", "year": 2026, "severity": "Low",
        "source_ids": ["AIAAIC-1234"], "tags": ["aiaaic"],
        "added": "2026-02-01", "updated": "2026-02-01",
    }]
    b = s.build_bundle(incidents)
    inc = next(o for o in b["objects"]
               if o["type"] == "x-genai-incident" and o["x_incident_id"] == "INC-00006")
    assert "x_content_license" not in inc


def test_owasp_llm_source_name_matches_corpus_edition():
    """Every owasp_llm code in the corpus is the edition named by the crosswalk's
    to_version (E24 / D26(c)); the STIX source_name must say so. Expected value
    is derived from mappings/owasp_llm_2025_to_2026.json, not hardcoded."""
    import json
    xwalk = json.loads((s.MAPPINGS / "owasp_llm_2025_to_2026.json").read_text(encoding="utf-8"))
    expected = f"owasp-llm-top10-{xwalk['to_version']}"
    assert expected != f"owasp-llm-top10-{xwalk['from_version']}"
    sdo = next(o for o in _bundle()["objects"] if o.get("x_incident_id") == "INC-00001")
    names = [r["source_name"] for r in sdo["external_references"] if r.get("external_id") == "LLM10"]
    assert names == [expected]
    assert not any(r["source_name"] == f"owasp-llm-top10-{xwalk['from_version']}"
                   for o in _bundle()["objects"] for r in o.get("external_references", []))
