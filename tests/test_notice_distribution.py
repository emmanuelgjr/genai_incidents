"""D172 (licence-notice compliance): every distributed copy of the dataset ships
NOTICE-DATA, LICENSE-DATA and LICENSES/Apache-2.0.txt, byte-identical to the
repo root, and lists them in its checksums where it has any.

Each surface that can be built offline is built here and checked per file for
presence AND byte equality (never an aggregate). The `*_fires_*` tests are the
inputs that make the checks fail (working agreement 6): a build that skips the
copy step, a missing source, an altered copy.
"""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import export_huggingface as hf
import export_integrity as ei
import export_misp as misp
import export_stix as stix
import export_taxii as taxii
import package_release_assets as pra

ROOT = Path(__file__).resolve().parents[1]
NOTICES = ei.NOTICE_FILES
SHA = "0123456789abcdef0123456789abcdef01234567"
BUILT = ("2026-10-09T12:00:00Z", "commit-date")
STATS = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
ROWS = [{"id": "INC-00001", "title": "Example", "description": "A flaw.", "date": "2026-01-02",
         "year": 2026, "severity": "High", "attack_vector": "rce", "corpus": "security", "tier": "feed",
         "cve_ids": ["CVE-2026-0001"], "references": [{"url": "https://example.com/a", "type": "advisory"}],
         "added": "2026-01-03", "updated": "2026-01-04"}]


def _equal(tree: Path, rel: str, name: str | None = None) -> None:
    p = tree / (name or rel)
    assert p.is_file(), f"{p} missing"
    assert p.read_bytes() == (ROOT / rel).read_bytes(), f"{p} differs from repo-root {rel}"


def test_the_three_source_files_exist_and_the_apache_text_is_the_licence():
    for rel in NOTICES:
        assert (ROOT / rel).stat().st_size > 0, rel
    apache = (ROOT / "LICENSES" / "Apache-2.0.txt").read_text(encoding="utf-8")
    assert "Apache License" in apache and "Version 2.0, January 2004" in apache
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in apache
    # reuse lint's complaint: used SPDX ids need their texts
    for lic in ("MIT", "CC-BY-4.0", "Apache-2.0"):
        assert (ROOT / "LICENSES" / f"{lic}.txt").is_file(), lic


# --- Hugging Face bundle ---------------------------------------------------------


def test_huggingface_bundle_ships_the_notices_byte_identical_and_lists_them(tmp_path):
    hf.build(tmp_path)
    listed = ei.parse_sums((tmp_path / "SHA256SUMS").read_text(encoding="utf-8"))
    for rel in NOTICES:
        _equal(tmp_path, rel)
        assert rel in listed, rel
        assert listed[rel] == ei.sha256_of(ROOT / rel)
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    for rel in NOTICES:
        assert rel in card, f"card does not name {rel}"


def test_huggingface_build_fires_when_a_notice_source_is_missing(tmp_path, monkeypatch):
    fake_root = tmp_path / "root"
    (fake_root / "LICENSES").mkdir(parents=True)
    (fake_root / "NOTICE-DATA").write_text("x", encoding="utf-8")
    (fake_root / "LICENSE-DATA").write_text("y", encoding="utf-8")   # Apache text deliberately absent
    monkeypatch.setattr(ei, "ROOT", fake_root)
    with pytest.raises(SystemExit, match="Apache-2.0.txt is missing"):
        hf.build(tmp_path / "out")


def test_huggingface_build_fires_without_the_copy_step(tmp_path, monkeypatch):
    """Input that makes the byte-equality check fail: the copy step removed."""
    monkeypatch.setattr(ei, "copy_notices", lambda *a, **k: [])
    hf.build(tmp_path)
    assert ei.notice_errors(tmp_path), "notice_errors must fire on a bundle without the notices"
    with pytest.raises(AssertionError):
        _equal(tmp_path, "NOTICE-DATA")


# --- served trees (docs/data incl. STIX, docs/taxii2, docs/misp) and release assets ----


@pytest.fixture
def site(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    (docs / "data").mkdir(parents=True)
    (docs / "data" / "incidents.stix.json").write_text(json.dumps(stix.build_bundle(ROWS)) + "\n", encoding="utf-8")
    (docs / "data" / "incidents.min.json").write_text('{"incidents": []}', encoding="utf-8")
    monkeypatch.setattr(taxii, "OUT", docs / "taxii2")
    taxii.build(ROWS)
    monkeypatch.setattr(misp, "OUT", docs / "misp")
    misp.build(ROWS)
    ei.gen_all(tmp_path, stats=STATS, commit=SHA, built=BUILT, dirty=False)
    return tmp_path


@pytest.mark.parametrize("tree", ["data", "taxii2", "misp"])
def test_each_served_tree_ships_the_notices_and_lists_them(site, tree):
    d = site / "docs" / tree
    listed = ei.parse_sums((d / "SHA256SUMS").read_text(encoding="utf-8"))
    for rel in NOTICES:
        _equal(d, rel)
        assert rel in listed, f"{tree}/SHA256SUMS does not list {rel}"
    assert ei.verify_all(site) == []


def test_stix_download_has_the_notices_beside_it(site):
    assert (site / "docs" / "data" / "incidents.stix.json").is_file()
    for rel in NOTICES:
        _equal(site / "docs" / "data", rel)


def test_release_assets_ship_flat_notices_and_zips_carry_them(site, tmp_path):
    assets = [("incidents.stix.json", site / "docs" / "data" / "incidents.stix.json"),
              ("incidents.min.json", site / "docs" / "data" / "incidents.min.json"),
              ("taxii2.zip", site / "docs" / "taxii2"), ("misp-feed.zip", site / "docs" / "misp")]
    out = tmp_path / "rel"
    lines = pra.package(out, assets, stats=STATS, commit=SHA, built=BUILT, dirty=False)
    listed = {l.split("  ", 1)[1] for l in lines}
    for rel, name in ei.RELEASE_NOTICE_NAMES.items():
        _equal(out, rel, name)
        assert name in listed, name
    assert ei.notice_errors(out, flat=True) == []
    for z_name in ("taxii2.zip", "misp-feed.zip"):
        with zipfile.ZipFile(out / z_name) as z:
            for rel in NOTICES:
                assert z.read(rel) == (ROOT / rel).read_bytes(), f"{z_name}:{rel}"


def test_release_package_fires_when_a_zipped_tree_lacks_the_notices(site, tmp_path):
    (site / "docs" / "misp" / "NOTICE-DATA").unlink()
    assets = [("misp-feed.zip", site / "docs" / "misp")]
    with pytest.raises(SystemExit, match="misp-feed.zip/NOTICE-DATA: licence notice file missing"):
        pra.package(tmp_path / "rel", assets, stats=STATS, commit=SHA, built=BUILT, dirty=False)


def test_verify_fires_on_a_missing_or_altered_notice_in_a_served_tree(site):
    p = site / "docs" / "taxii2" / "NOTICE-DATA"
    p.write_bytes(p.read_bytes() + b" ")
    ei.write_sums(site / "docs" / "taxii2")            # sums agree; only the byte-equality check can see it
    errs = ei.verify_all(site)
    assert len(errs) == 1 and "taxii2/NOTICE-DATA" in errs[0] and "not byte-identical" in errs[0], errs
    p.unlink()
    ei.write_sums(site / "docs" / "taxii2")
    assert any("taxii2/NOTICE-DATA: licence notice file missing" in e for e in ei.verify_all(site))


# --- Pages root ---------------------------------------------------------------------


def test_pages_root_notices_come_from_the_cli_step_the_workflow_runs(tmp_path):
    out = tmp_path / "docs"
    cli = [sys.executable, str(ROOT / "scripts" / "export_integrity.py")]
    r = subprocess.run(cli + ["notices", "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for rel in NOTICES:
        _equal(out, rel)
    v = cli + ["verify-notices", "--out", str(out)]
    assert subprocess.run(v, capture_output=True).returncode == 0
    (out / "NOTICE-DATA").write_bytes(b"stale")
    assert subprocess.run(v, capture_output=True).returncode == 1


def test_pages_workflow_copies_and_verifies_the_notices_and_footers_link_relatively():
    wf = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "export_integrity.py notices --out docs" in wf
    assert "verify-notices --out _site" in wf and '"_site/$d"' in wf
    rel = (ROOT / ".github" / "workflows" / "release-assets.yml").read_text(encoding="utf-8")
    assert "verify-notices --out dist/release --flat" in rel
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    shard = (ROOT / "docs" / "_layouts" / "incident-shard.html").read_text(encoding="utf-8")
    assert index.count('href="NOTICE-DATA"') == 2
    assert 'href="../NOTICE-DATA"' in shard
    for html in (index, shard):
        assert "blob/main/NOTICE-DATA" not in html


def test_docs_copies_of_the_notices_are_build_products_not_second_sources():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for g in ("docs/NOTICE-DATA", "docs/LICENSE-DATA", "docs/LICENSES/"):
        assert g in ignored, g
    tracked = subprocess.run(["git", "ls-files", "docs/NOTICE-DATA", "docs/LICENSE-DATA", "docs/LICENSES"],
                             cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert tracked == ""


# --- package metadata ----------------------------------------------------------------


def test_pyproject_declares_mit_and_cc_by_and_ships_the_apache_text():
    tomllib = pytest.importorskip("tomllib")              # Python 3.11+
    proj = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert proj["license"] == "MIT AND CC-BY-4.0"
    assert "NOTICE-DATA" in proj["license-files"] and "LICENSES/Apache-2.0.txt" in proj["license-files"]
    assert not any(c.startswith("License ::") for c in proj["classifiers"])
