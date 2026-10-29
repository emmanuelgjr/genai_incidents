"""D146-2: MAESTRO and NIST AI RMF are pinned in ``taxonomy_versions``.

Each new key must equal its mapping file's ``version``, read here directly from
the file (not through ``taxonomy_versions.SOURCES``, which is the path under
test), and must reach every surface: stats.json, the package, the manifest
schema (required), ``validate``, the STIX identity and the MISP machinetags.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import taxonomy_versions as tvm
import validate

ROOT = Path(__file__).resolve().parents[1]

# key -> mapping file, fixed here so a SOURCES edit that repoints a key fails.
NEW = {"maestro": "maestro_layers.json", "nist_ai_rmf": "nist_ai_rmf.json"}


def _file_version(fname: str) -> str:
    return json.loads((ROOT / "mappings" / fname).read_text(encoding="utf-8"))["version"]


@pytest.mark.parametrize("key,fname", sorted(NEW.items()))
def test_key_equals_its_mapping_file_version(key, fname):
    v = _file_version(fname)
    assert tvm.taxonomy_versions()[key] == v
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    assert stats["taxonomy_versions"][key] == v
    pkg = json.loads((ROOT / "src" / "genai_incidents" / "data" / "taxonomy_versions.json")
                     .read_text(encoding="utf-8"))
    assert pkg[key] == v


def test_sources_point_at_the_right_files():
    """Both files carry "1.0", so a value check alone cannot tell a key that
    reads the wrong file: pin the (key, file, field) rows themselves."""
    rows = {k: (f, fld) for k, f, fld in tvm.SOURCES if k in NEW}
    assert rows == {k: (f, "version") for k, f in NEW.items()}


def test_pinned_values():
    tv = tvm.taxonomy_versions()
    assert (tv["maestro"], tv["nist_ai_rmf"]) == ("1.0", "1.0")


def test_nist_version_is_machine_short_and_edition_kept():
    """The machinetag value is a plain version; the descriptive edition stays
    in the mapping file, not in the pin."""
    nist = json.loads((ROOT / "mappings" / "nist_ai_rmf.json").read_text(encoding="utf-8"))
    assert nist["version"] == "1.0"
    assert nist["edition"] == "AI 100-1, January 2023"
    for v in tvm.taxonomy_versions().values():
        assert v is None or ('"' not in v and " " not in v), v   # MISP tag well-formed


def test_follows_the_mapping_file(tmp_path):
    m = tmp_path / "mappings"
    m.mkdir()
    for p in (ROOT / "mappings").glob("*.json"):
        (m / p.name).write_bytes(p.read_bytes())
    for key, fname in NEW.items():
        raw = json.loads((m / fname).read_text(encoding="utf-8"))
        raw["version"] = "9.9"
        (m / fname).write_text(json.dumps(raw), encoding="utf-8")
        assert tvm.taxonomy_versions(m)[key] == "9.9"


@pytest.mark.parametrize("key", sorted(NEW))
def test_required_in_manifest_schema_and_validate(key):
    schema = json.loads((ROOT / "schema" / "build_manifest.schema.json").read_text(encoding="utf-8"))
    tv = schema["properties"]["taxonomy_versions"]
    assert key in tv["required"] and key in tv["properties"]
    assert key in validate._TAXONOMY_KEYS
    good = tvm.taxonomy_versions()
    dropped = {k: v for k, v in good.items() if k != key}
    assert validate.check_taxonomy_versions({"taxonomy_versions": dropped}, good)


def test_revision_4_registers_the_new_keys():
    prev, row4 = tvm.REVISIONS[2], tvm.REVISIONS[3]
    assert set(row4) - set(prev) == set(NEW)
    assert {k: row4[k] for k in prev} == prev                # nothing else re-pinned
    assert tvm.tv_revision() == 4 == len(tvm.REVISIONS)


def test_exports_carry_the_new_keys(tmp_path, monkeypatch):
    import export_misp
    import export_stix
    tv = tvm.taxonomy_versions()
    ident = [o for o in export_stix.build_bundle([])["objects"] if o["type"] == "identity"]
    assert {k: ident[0]["x_taxonomy_versions"][k] for k in NEW} == {k: tv[k] for k in NEW}
    monkeypatch.setattr(export_misp, "OUT", tmp_path)
    export_misp.build([{"id": "INC-00001", "title": "t", "year": 2026, "date": "2026-01-01",
                        "cve_ids": [], "references": []}])
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    for ev in manifest.values():
        names = {t["name"] for t in ev["Tag"]}
        assert f'genai-incidents:taxonomy-maestro="{tv["maestro"]}"' in names
        assert f'genai-incidents:taxonomy-nist-ai-rmf="{tv["nist_ai_rmf"]}"' in names


def test_package_exposes_the_new_keys():
    sys.path.insert(0, str(ROOT / "src"))
    import genai_incidents
    assert set(NEW) <= set(genai_incidents.taxonomy_versions())
