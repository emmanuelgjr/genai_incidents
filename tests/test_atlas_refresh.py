"""WS4 / v2.13.0 item 2: ATLAS refresh tooling, the id lint, and taxonomy_versions.

The lint tests PLANT bad ids in a scratch copy and require rc=1 -- a lint nobody
has seen fail is not a check.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

import atlas_pin
import fetch_atlas
import lint_atlas_ids
import taxonomy_versions as tvmod
import validate

ROOT = Path(__file__).resolve().parents[1]


# ----------------------------------------------------------------- lint ----

def _scratch(tmp_path: Path) -> Path:
    """Minimal scratch checkout: incidents + mappings (no snapshot)."""
    (tmp_path / "data").mkdir()
    (tmp_path / "mappings").mkdir()
    shutil.copy(ROOT / "data" / "incidents.json", tmp_path / "data" / "incidents.json")
    for p in (ROOT / "mappings").glob("*.json"):
        shutil.copy(p, tmp_path / "mappings" / p.name)
    return tmp_path


def _plant(root: Path, **fields) -> None:
    p = root / "data" / "incidents.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["incidents"][0].update(fields)
    p.write_text(json.dumps(d), encoding="utf-8")


def test_lint_clean_on_repo(capsys):
    assert lint_atlas_ids.main([]) == 0
    assert "none absent or deprecated" in capsys.readouterr().out


def test_lint_fires_on_fake_id(tmp_path, capsys):
    root = _scratch(tmp_path)
    _plant(root, mitre_atlas=["AML.T9999"])
    assert lint_atlas_ids.main(["--root", str(root), "--skip-pin-integrity"]) == 1
    out = capsys.readouterr().out
    assert "AML.T9999" in out and "absent from pinned ATLAS" in out


def test_lint_fires_on_deprecated_id(tmp_path, capsys):
    root = _scratch(tmp_path)
    _plant(root, mitre_atlas=["AML.T0058"])  # retired upstream, retained in the pin as deprecated
    assert lint_atlas_ids.main(["--root", str(root), "--skip-pin-integrity"]) == 1
    out = capsys.readouterr().out
    assert "AML.T0058" in out and "deprecated in pinned ATLAS" in out


def test_lint_fires_on_fake_tactic_and_on_mapping_files(tmp_path, capsys):
    root = _scratch(tmp_path)
    _plant(root, mitre_atlas_tactics=["AML.TA9999"])
    (root / "mappings" / "extra.json").write_text(json.dumps({"x": ["AML.T0019"]}), encoding="utf-8")
    assert lint_atlas_ids.main(["--root", str(root), "--skip-pin-integrity"]) == 1
    out = capsys.readouterr().out
    assert "AML.TA9999" in out and "AML.T0019" in out and "mappings/extra.json" in out


def test_lint_fires_when_translation_target_is_invalid(tmp_path, capsys):
    root = _scratch(tmp_path)
    p = root / "mappings" / "atlas_id_translations.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["translations"]["AML.T0058"]["to"] = "AML.T0019"  # deprecated target
    p.write_text(json.dumps(d), encoding="utf-8")
    assert lint_atlas_ids.main(["--root", str(root), "--skip-pin-integrity"]) == 1
    assert "AML.T0019" in capsys.readouterr().out


def test_lint_cannot_run_is_not_a_pass(tmp_path):
    assert lint_atlas_ids.main(["--root", str(tmp_path)]) == 2


def test_lint_pin_integrity_catches_hand_edited_pin(tmp_path, capsys):
    root = _scratch(tmp_path)
    shutil.copytree(ROOT / "ingest" / "atlas", root / "ingest" / "atlas")
    p = root / "mappings" / "mitre_atlas.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["techniques"]["AML.T0000"]["name"] = "Hand Edited"
    p.write_text(json.dumps(d), encoding="utf-8")
    assert lint_atlas_ids.main(["--root", str(root)]) == 1
    assert "not what scripts/atlas_pin.py" in capsys.readouterr().out


def test_lint_pin_integrity_catches_snapshot_tamper(tmp_path, capsys):
    root = _scratch(tmp_path)
    shutil.copytree(ROOT / "ingest" / "atlas", root / "ingest" / "atlas")
    snap = next((root / "ingest" / "atlas").glob("ATLAS-*.yaml"))
    snap.write_bytes(snap.read_bytes() + b"\n# tampered\n")
    assert lint_atlas_ids.main(["--root", str(root)]) == 1
    assert "sha256" in capsys.readouterr().out


# --------------------------------------------------- pin / diff / merge ----

def _release(version, techs, tactics=None, rels=None):
    return {
        "collection": {"version": version, "modified-date": "2026-01-01"},
        "tactics": {t: {"name": n} for t, n in (tactics or {"AML.TA0001": "Stage"}).items()},
        "techniques": {t: {"name": n} for t, n in techs.items()},
        "relationships": rels or {},
    }


def _achieves(tid, tac):
    return {tid: {"achieves": [{"source": tid, "target": tac, "relationship-type": "achieves"}]}}


def test_build_pin_retains_removed_ids_as_deprecated_and_never_deletes():
    r1 = _release("2026.01", {"AML.T0001": "A", "AML.T0002": "B"},
                  rels={**_achieves("AML.T0001", "AML.TA0001")})
    pin1 = atlas_pin.build_pin(r1, None)
    r2 = _release("2026.02", {"AML.T0001": "A2", "AML.T0003": "C"},
                  rels={**_achieves("AML.T0001", "AML.TA0001")})
    pin2 = atlas_pin.build_pin(r2, pin1)
    assert set(pin2["techniques"]) == {"AML.T0001", "AML.T0002", "AML.T0003"}
    assert pin2["techniques"]["AML.T0002"]["deprecated"]["since"] == "2026.02"
    assert "deprecated" not in pin2["techniques"]["AML.T0001"]
    d = atlas_pin.diff_pins(pin1, pin2)
    assert d["techniques_added"] == ["AML.T0003"]
    assert d["techniques_removed"] == ["AML.T0002"]
    assert d["techniques_renamed"] == [("AML.T0001", "A", "A2")]
    # idempotent: rebuilding from the same release with the new pin as prior is a no-op
    assert atlas_pin.build_pin(r2, pin2) == pin2


def test_diff_detects_tactic_rename_and_link_change():
    r1 = _release("1", {"AML.T0001": "A"}, {"AML.TA0001": "Staging"}, _achieves("AML.T0001", "AML.TA0001"))
    r2 = _release("2", {"AML.T0001": "A"}, {"AML.TA0001": "Adaptation", "AML.TA0002": "Recon"},
                  {"AML.T0001": {"achieves": [{"target": "AML.TA0001"}, {"target": "AML.TA0002"}]}})
    d = atlas_pin.diff_pins(atlas_pin.build_pin(r1, None), atlas_pin.build_pin(r2, None))
    assert d["tactics_renamed"] == [("AML.TA0001", "Staging", "Adaptation")]
    assert d["tactics_added"] == ["AML.TA0002"]
    assert d["technique_tactic_links_changed"][0][0] == "AML.T0001"


def test_committed_pin_is_derived_from_committed_snapshot():
    """The pin is not hand-maintained: rebuilding it from the committed raw YAML
    (with the pin itself as prior, for deprecated records) reproduces it."""
    pin = atlas_pin.load_pin()
    release = atlas_pin.load_release(atlas_pin.snapshot_path())
    assert pin["version"] == str(release["collection"]["version"])
    assert json.dumps(atlas_pin.build_pin(release, pin), sort_keys=True) == json.dumps(pin, sort_keys=True)


def test_translations_target_live_ids_and_sources_are_not_live():
    pin = atlas_pin.load_pin()
    for old, new in atlas_pin.load_translations().items():
        assert new in pin["techniques"] and not pin["techniques"][new].get("deprecated"), new
        assert old not in pin["techniques"] or pin["techniques"][old].get("deprecated"), old


def test_fill_taxonomy_translates_superseded_heuristic_output():
    """LLM07 -> AML.T0058 is emitted by the (unchanged) heuristic table; the
    merge must deliver the pinned-release id instead, with its tactic."""
    import merge_and_dedupe as md
    e = md.fill_taxonomy({"owasp_llm": ["LLM07"], "owasp_asi": [], "mitre_atlas": ["AML.T0019"]})
    assert "AML.T0058" not in e["mitre_atlas"] and "AML.T0019" not in e["mitre_atlas"]
    assert {"AML.T0115.001", "AML.T0115.000"} <= set(e["mitre_atlas"])
    assert "AML.TA0003" in e["mitre_atlas_tactics"]


def test_corpus_has_no_superseded_ids():
    d = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    old = set(atlas_pin.load_translations())
    hits = [e["id"] for e in d["incidents"] if old & set(e.get("mitre_atlas") or [])]
    assert hits == []


# --------------------------------------------------------- fetch pointer ----

def test_resolve_pointer_follows_text_pointer_chain():
    bodies = {
        fetch_atlas.RAW_BASE + "ATLAS-latest.yaml": b"v6/ATLAS-latest.yaml",
        fetch_atlas.RAW_BASE + "v6/ATLAS-latest.yaml": b"ATLAS-2026.09.yaml",
    }
    chain, rel = fetch_atlas.resolve_pointer(lambda url, timeout=60: (bodies[url], None))
    assert rel == "v6/ATLAS-2026.09.yaml" and len(chain) == 2


def test_fetch_atlas_has_no_direct_network_calls():
    src = (ROOT / "scripts" / "fetch_atlas.py").read_text(encoding="utf-8")
    assert "urlopen" not in src and "requests" not in src and "from ingest.common import fetch_once" in src


def _fake_upstream(monkeypatch, tmp_path, body: bytes):
    """Point fetch_atlas at a scratch snapshot dir and a fake upstream serving `body`."""
    snap = tmp_path / "atlas"
    monkeypatch.setattr(fetch_atlas, "SNAPSHOT_DIR", snap)
    monkeypatch.setattr(fetch_atlas, "PROVENANCE", snap / "ATLAS.provenance.json")
    bodies = {
        fetch_atlas.RAW_BASE + "ATLAS-latest.yaml": b"v6/ATLAS-latest.yaml",
        fetch_atlas.RAW_BASE + "v6/ATLAS-latest.yaml": b"ATLAS-2026.09.yaml",
        fetch_atlas.RAW_BASE + "v6/ATLAS-2026.09.yaml": body,
    }
    monkeypatch.setattr(fetch_atlas, "fetch_once", lambda url, timeout=60: (bodies[url], None))
    monkeypatch.setattr(sys, "argv", ["fetch_atlas.py"])
    return snap


def _snapshot_state(snap: Path) -> dict:
    return {p.name: p.read_bytes() for p in sorted(snap.iterdir())}


def test_fetch_same_release_is_a_true_noop(tmp_path, monkeypatch, capsys):
    """Unchanged upstream => nothing written, not even a fresh `fetched` date."""
    body = (ROOT / "ingest" / "atlas" / "ATLAS-2026.09.yaml").read_bytes()
    snap = _fake_upstream(monkeypatch, tmp_path, body)
    assert fetch_atlas.main() == 0                      # first pull writes
    prov = json.loads((snap / "ATLAS.provenance.json").read_text(encoding="utf-8"))
    prov["fetched"] = "2000-01-01"                       # a stale date a rewrite would clobber
    (snap / "ATLAS.provenance.json").write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8")
    before = _snapshot_state(snap)
    assert fetch_atlas.main() == 0                      # same release again
    assert _snapshot_state(snap) == before              # byte-identical: no rewrite
    assert "NO-OP" in capsys.readouterr().out


def test_fetch_changed_bytes_same_version_is_not_a_noop(tmp_path, monkeypatch):
    """The no-op must fire only on a matching sha: a re-issued file is rewritten."""
    body = (ROOT / "ingest" / "atlas" / "ATLAS-2026.09.yaml").read_bytes()
    snap = _fake_upstream(monkeypatch, tmp_path, body)
    assert fetch_atlas.main() == 0
    before = _snapshot_state(snap)
    _fake_upstream(monkeypatch, tmp_path, body + b"\n# re-issued\n")
    assert fetch_atlas.main() == 0
    assert _snapshot_state(snap) != before


def test_fetch_noop_requires_snapshot_file_intact(tmp_path, monkeypatch):
    """Provenance sha matching is not enough if the committed file was altered."""
    body = (ROOT / "ingest" / "atlas" / "ATLAS-2026.09.yaml").read_bytes()
    snap = _fake_upstream(monkeypatch, tmp_path, body)
    assert fetch_atlas.main() == 0
    (snap / "ATLAS-2026.09.yaml").write_bytes(body + b"#tamper\n")
    assert fetch_atlas.main() == 0
    assert (snap / "ATLAS-2026.09.yaml").read_bytes() == body   # restored from upstream


def test_atlas_pin_refuses_to_overwrite_existing_report(tmp_path, monkeypatch, capsys):
    """Dated audits are do-not-regenerate: --report onto an existing file fails."""
    rep = tmp_path / "audit.md"
    rep.write_text("COMMITTED AUDIT\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["atlas_pin.py", "build", "--report", str(rep)])
    assert atlas_pin._main() == 2
    assert rep.read_text(encoding="utf-8") == "COMMITTED AUDIT\n"
    assert "REFUSING" in capsys.readouterr().err
    rep.unlink()                                          # absent -> written
    assert atlas_pin._main() == 0 and rep.is_file()


# ------------------------------------------------------ taxonomy_versions ----

def test_taxonomy_versions_derived_from_mappings_not_literals(tmp_path):
    m = tmp_path / "mappings"
    m.mkdir()
    for p in (ROOT / "mappings").glob("*.json"):
        shutil.copy(p, m / p.name)
    asi = json.loads((m / "owasp_asi_top10.json").read_text(encoding="utf-8"))
    asi["version"] = "2026"
    (m / "owasp_asi_top10.json").write_text(json.dumps(asi), encoding="utf-8")
    assert tvmod.taxonomy_versions(m)["owasp_asi"] == "2026"       # follows the pin
    assert tvmod.taxonomy_versions()["owasp_asi"] == "2025"        # repo unchanged


def test_stats_json_carries_taxonomy_versions():
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    assert stats["taxonomy_versions"] == tvmod.taxonomy_versions()
    assert set(stats["taxonomy_versions"]) == {"atlas", "owasp_llm", "owasp_asi", "capec", "veris"}
    assert stats["taxonomy_versions"]["atlas"] == atlas_pin.load_pin()["version"]


def test_validate_check_taxonomy_versions_fires():
    good = tvmod.taxonomy_versions()
    assert validate.check_taxonomy_versions({"taxonomy_versions": good}, good) == []
    assert validate.check_taxonomy_versions({}, good)                                  # missing
    stale = dict(good, atlas="2026.06")
    assert validate.check_taxonomy_versions({"taxonomy_versions": stale}, good)        # stale
    assert validate.check_taxonomy_versions({"taxonomy_versions": dict(good, extra="x")}, good)


def test_stix_bundle_carries_x_taxonomy_versions():
    import export_stix
    b = export_stix.build_bundle([])
    ids = [o for o in b["objects"] if o["type"] == "identity"]
    assert len(ids) == 1 and ids[0]["x_taxonomy_versions"] == tvmod.taxonomy_versions()
    assert ids[0]["spec_version"] == "2.1" and ids[0]["identity_class"] == "system"


def test_misp_manifest_and_events_carry_taxonomy_tags(tmp_path, monkeypatch):
    import export_misp
    monkeypatch.setattr(export_misp, "OUT", tmp_path)
    export_misp.build([{"id": "INC-00001", "title": "t", "year": 2026, "date": "2026-01-01",
                        "cve_ids": [], "references": []}])
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    tv = tvmod.taxonomy_versions()
    for ev in manifest.values():
        names = {t["name"] for t in ev["Tag"]}
        assert f'genai-incidents:taxonomy-atlas="{tv["atlas"]}"' in names
        assert f'genai-incidents:taxonomy-owasp-asi="{tv["owasp_asi"]}"' in names
        assert not any("taxonomy-capec" in n for n in names)  # unversioned -> omitted, not guessed


def test_hf_card_states_taxonomy_versions_via_placeholder(tmp_path):
    import export_huggingface as hf
    assert "{taxonomy_versions}" in hf.CARD          # template placeholder, not a literal
    hf.build(tmp_path)
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert f"atlas {atlas_pin.load_pin()['version']}" in card
    assert "{taxonomy_versions}" not in card


def test_package_exposes_taxonomy_versions():
    sys.path.insert(0, str(ROOT / "src"))
    import genai_incidents
    assert genai_incidents.taxonomy_versions() == tvmod.taxonomy_versions()
    assert "taxonomy_versions" in genai_incidents.__all__


def test_veris_version_matches_its_source_string():
    v = json.loads((ROOT / "mappings" / "veris.json").read_text(encoding="utf-8"))
    assert v["version"] in v["_source"]


# ------------------------------------------------------- poisoning guard ----

def test_build_pin_rejects_markup_in_names_and_malformed_ids():
    atlas_pin.build_pin(_release("2026.01", {"AML.T0001": "Plain Name"}), None)
    for bad_name in ("<script>alert(1)</script>", "x`y", "line\x01ctl", ""):
        with pytest.raises(ValueError):
            atlas_pin.build_pin(_release("2026.01", {"AML.T0001": bad_name}), None)
    with pytest.raises(ValueError):
        atlas_pin.build_pin(_release("2026.01", {"AML.T0001; DROP": "n"}), None)


def test_scan_suspicious_counts_known_patterns_and_is_clean_on_snapshot():
    hit = atlas_pin.scan_suspicious('<script>x</script> javascript:void(0) <img onerror="x"> '
                                    'data:text/html;base64,AAAA <iframe src=x>')
    assert all(v >= 1 for v in hit.values()), hit
    clean = atlas_pin.scan_suspicious(atlas_pin.snapshot_path().read_text(encoding="utf-8"))
    assert not any(clean.values()), clean


def test_refresh_atlas_codes_updates_retained_priors_and_touches_only_atlas_fields():
    """Retained priors are carried verbatim (they bypass fill_taxonomy); the
    narrow refresh must translate ids and add pin-linked tactics, and nothing
    else (it must NOT re-run the OWASP->ATLAS backfill heuristics)."""
    import merge_and_dedupe as md
    e = {"owasp_llm": ["LLM07"], "mitre_atlas": ["AML.T0058", "AML.T0012"],
         "mitre_atlas_tactics": ["AML.TA0004", "AML.TA0012"], "title": "t", "nist_ai_rmf": []}
    snap = json.dumps({k: v for k, v in e.items() if k not in ("mitre_atlas", "mitre_atlas_tactics")})
    assert md.refresh_atlas_codes(e) is True
    assert e["mitre_atlas"] == ["AML.T0012", "AML.T0115.001"]
    assert "AML.TA0015" in e["mitre_atlas_tactics"] and "AML.TA0003" in e["mitre_atlas_tactics"]
    assert json.dumps({k: v for k, v in e.items() if k not in ("mitre_atlas", "mitre_atlas_tactics")}) == snap
    assert md.refresh_atlas_codes(e) is False                    # idempotent
    bare = {"owasp_llm": ["LLM07"]}                              # no atlas codes -> no backfill here
    assert md.refresh_atlas_codes(bare) is False and "mitre_atlas" not in bare
