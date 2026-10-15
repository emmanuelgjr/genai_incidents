"""v2.13.0 item 8 -- SHA256SUMS over STIX/TAXII/MISP, build_manifest.json on every
channel, and the D57 MISP / D64 count surfaces.

Each check names the input that makes it fail (working agreement 6); the
`*_fires_*` tests are those inputs.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import export_integrity as ei
import export_misp as misp
import export_stix as stix
import export_taxii as taxii
import package_release_assets as pra

ROOT = Path(__file__).resolve().parents[1]
STATS = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
SHA = "0123456789abcdef0123456789abcdef01234567"
BUILT = ("2026-10-09T12:00:00Z", "commit-date")

ROWS = [
    {"id": "INC-00001", "title": "Example RCE", "description": "A flaw.", "date": "2026-01-02",
     "year": 2026, "severity": "High", "attack_vector": "rce", "corpus": "security", "tier": "feed",
     "mitre_atlas": ["AML.T0050"], "cve_ids": ["CVE-2026-0001"],
     "references": [{"title": "A", "url": "https://example.com/a", "type": "advisory"}],
     "added": "2026-01-03", "updated": "2026-01-04"},
    {"id": "INC-00002", "title": "Frozen row", "description": "x", "date": "2025-02-02", "year": 2025,
     "severity": "Medium", "attack_vector": "other", "corpus": "ai-harm", "tier": "landmark",
     "cve_ids": [], "references": [{"url": "https://example.com/b", "type": "news"}],
     "added": "2025-06-01", "updated": "2025-06-05",
     "source_freshness": {"status": "stale", "as_of": "2026-05-31",
                          "sources": ["airi_navigator"], "review_by": "2027-01-07"}},
]


def _manifest(**kw):
    kw.setdefault("commit", SHA)
    kw.setdefault("built", BUILT)
    kw.setdefault("dirty", False)
    return ei.build_manifest(STATS, **kw)


# --- build_manifest.json -----------------------------------------------------


def test_manifest_matches_stats_json_field_for_field():
    m = _manifest()
    assert ei.validate_manifest(m) == []
    for k in ("version", "incident_count", "retracted_count", "unverified_count",
              "disputed_count", "landmark_count", "taxonomy_versions"):
        assert m[k] == STATS[k], k
    assert list(m) == list(ei.MANIFEST_KEYS)


def test_manifest_counts_agree_with_the_corpus_by_an_independent_path():
    """Not stats.json -> manifest again: re-derive from the rows."""
    raw = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    # Spelled out, not imported from scripts/entry_status.py: this is the
    # independent path. D130: unverified is outside incident_count too.
    standing = [e for e in raw if e.get("status") not in ("retracted", "unverified")]
    m = _manifest()
    assert m["incident_count"] == len(standing)
    assert m["retracted_count"] == sum(1 for e in raw if e.get("status") == "retracted")
    assert m["unverified_count"] == sum(1 for e in raw if e.get("status") == "unverified")
    assert m["incident_count"] + m["retracted_count"] + m["unverified_count"] == len(raw)
    assert m["disputed_count"] == sum(1 for e in standing if e.get("status") == "disputed")
    assert m["landmark_count"] == sum(1 for e in standing if e.get("tier") == "landmark")
    # D64: disputed stays counted -- it is inside incident_count, not beside it
    assert m["disputed_count"] <= m["incident_count"]


def test_manifest_schema_fires_on_a_bad_manifest():
    good = _manifest()
    for mutate, needle in (
        (lambda m: m.pop("commit"), "commit"),
        (lambda m: m.update(commit="abc"), "commit"),
        (lambda m: m.update(built_at="yesterday"), "built_at"),
        (lambda m: m.update(built_at_basis="wall-clock"), "built_at_basis"),
        (lambda m: m.update(disputed_count=-1), "disputed_count"),
        (lambda m: m.update(extra=1), "extra"),
        (lambda m: m["taxonomy_versions"].pop("atlas"), "atlas"),
    ):
        bad = copy.deepcopy(good)
        mutate(bad)
        errs = ei.validate_manifest(bad)
        assert errs and any(needle in e for e in errs), (needle, errs)


def test_built_at_is_never_the_wall_clock(monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    assert ei.built_at() == ("2023-11-14T22:13:20Z", "source-date-epoch")
    monkeypatch.delenv("SOURCE_DATE_EPOCH")
    ts, basis = ei.built_at()
    head = subprocess.run(["git", "show", "-s", "--format=%cI", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()
    assert basis == "commit-date"
    from datetime import datetime, timezone
    assert datetime.fromisoformat(head).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") == ts


def test_manifest_is_byte_reproducible(tmp_path):
    for _ in range(2):
        ei.write_manifest(tmp_path / "x", stats=STATS, commit=SHA, built=BUILT, dirty=False)
    a = (tmp_path / "x" / ei.MANIFEST_NAME).read_bytes()
    ei.write_manifest(tmp_path / "y", stats=STATS, commit=SHA, built=BUILT, dirty=False)
    assert a == (tmp_path / "y" / ei.MANIFEST_NAME).read_bytes()


# --- SHA256SUMS ---------------------------------------------------------------


@pytest.fixture
def site(tmp_path, monkeypatch):
    """A miniature docs/ with all three served trees built by the real exporters."""
    docs = tmp_path / "docs"
    (docs / "data").mkdir(parents=True)
    bundle = stix.build_bundle(ROWS)
    (docs / "data" / "incidents.stix.json").write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    (docs / "data" / "incidents.min.json").write_text('{"incidents": []}', encoding="utf-8")
    monkeypatch.setattr(taxii, "OUT", docs / "taxii2")
    taxii.build(ROWS)
    monkeypatch.setattr(misp, "OUT", docs / "misp")
    misp.build(ROWS)
    monkeypatch.setattr(ei, "STATS_PATH", ROOT / "data" / "stats.json")
    ei.gen_all(tmp_path, stats=STATS, commit=SHA, built=BUILT, dirty=False)
    return tmp_path


def test_sums_cover_stix_taxii_and_misp_files(site):
    data = ei.parse_sums((site / "docs" / "data" / "SHA256SUMS").read_text(encoding="utf-8"))
    assert "incidents.stix.json" in data and "build_manifest.json" in data
    tx = ei.parse_sums((site / "docs" / "taxii2" / "SHA256SUMS").read_text(encoding="utf-8"))
    assert f"api/collections/{taxii.COLLECTION_ID}/objects.json" in tx
    assert f"api/collections/{taxii.COLLECTION_ID}/manifest.json" in tx
    assert "discovery.json" in tx and "build_manifest.json" in tx
    mp = ei.parse_sums((site / "docs" / "misp" / "SHA256SUMS").read_text(encoding="utf-8"))
    assert {"manifest.json", "hashes.csv", "README.md", "build_manifest.json"} <= set(mp)
    events = [k for k in mp if re.fullmatch(r"[0-9a-f-]{36}\.json", k)]
    assert len(events) == 2 and len(mp) == 6


def test_sums_are_standard_sha256sum_format_and_correct(site):
    tree = site / "docs" / "taxii2"
    for line in (tree / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        assert hashlib.sha256((tree / rel).read_bytes()).hexdigest() == digest
    assert ei.verify_all(site) == []


@pytest.mark.parametrize("tree,victim", [
    ("data", "incidents.stix.json"),
    ("taxii2", "discovery.json"),
    ("misp", "hashes.csv"),
])
def test_verify_fires_on_one_changed_byte_in_each_served_tree(site, tree, victim):
    p = site / "docs" / tree / victim
    p.write_bytes(p.read_bytes() + b" ")
    errs = ei.verify_all(site)
    assert len(errs) == 1 and victim in errs[0] and "mismatch" in errs[0]


def test_verify_fires_on_an_export_that_ran_after_the_sums(site):
    """The pre-v2.13.0 Pages bug: sums written, then the STIX bundle exported."""
    (site / "docs" / "data" / "late.json").write_text("{}", encoding="utf-8")
    errs = ei.verify_all(site)
    assert errs == ["data/late.json: served but not listed in SHA256SUMS -- run scripts/export_integrity.py gen"]


def test_verify_fires_on_a_missing_listed_file_and_a_missing_sums_file(site):
    (site / "docs" / "misp" / "hashes.csv").unlink()
    assert any("hashes.csv" in e and "missing" in e for e in ei.verify_all(site))
    (site / "docs" / "taxii2" / "SHA256SUMS").unlink()
    assert any("taxii2/SHA256SUMS does not exist" in e for e in ei.verify_all(site))


def test_verify_fires_on_a_manifest_that_fails_its_schema(site):
    p = site / "docs" / "misp" / ei.MANIFEST_NAME
    m = json.loads(p.read_text(encoding="utf-8"))
    m["disputed_count"] = "22"
    p.write_text(json.dumps(m), encoding="utf-8")
    ei.write_sums(site / "docs" / "misp")        # sums now agree; the SCHEMA must still fire
    errs = ei.verify_all(site)
    assert any("build_manifest.json: disputed_count" in e and "not of type" in e for e in errs), errs


def test_verify_fires_on_a_manifest_whose_counts_disagree_with_stats_json(site):
    """Sums regenerated over a tampered manifest still agree with themselves;
    only the stats.json comparison can see this."""
    p = site / "docs" / "taxii2" / ei.MANIFEST_NAME
    m = json.loads(p.read_text(encoding="utf-8"))
    m["incident_count"] += 1
    p.write_text(json.dumps(m), encoding="utf-8")
    ei.write_sums(site / "docs" / "taxii2")
    errs = ei.verify_all(site)
    assert len(errs) == 1 and "incident_count" in errs[0] and "stats.json" in errs[0]


def test_every_served_tree_gets_a_manifest(site):
    for tree in ("data", "taxii2", "misp"):
        m = json.loads((site / "docs" / tree / ei.MANIFEST_NAME).read_text(encoding="utf-8"))
        assert m["commit"] == SHA and ei.validate_manifest(m) == []


def test_cli_verify_exits_nonzero_on_corruption(tmp_path):
    """The shipped gate, end to end, in a subprocess against a copy of the layout."""
    (tmp_path / "docs" / "data").mkdir(parents=True)
    (tmp_path / "docs" / "data" / "a.json").write_text("{}", encoding="utf-8")
    ei.gen_all(tmp_path, stats=STATS, commit=SHA, built=BUILT, dirty=False)
    code = ("import sys, pathlib; sys.path.insert(0, %r); import export_integrity as e; "
            "sys.exit(1 if e.verify_all(pathlib.Path(%r)) else 0)" % (str(ROOT / "scripts"), str(tmp_path)))
    assert subprocess.run([sys.executable, "-c", code]).returncode == 0
    (tmp_path / "docs" / "data" / "a.json").write_text("{ }", encoding="utf-8")
    assert subprocess.run([sys.executable, "-c", code]).returncode == 1


# --- release assets / HF / package channels -------------------------------------


def test_release_assets_package_is_complete_verifiable_and_reproducible(site, tmp_path):
    assets = [("incidents.stix.json", site / "docs" / "data" / "incidents.stix.json"),
              ("incidents.min.json", site / "docs" / "data" / "incidents.min.json"),
              ("taxii2.zip", site / "docs" / "taxii2"), ("misp-feed.zip", site / "docs" / "misp")]
    kw = dict(stats=STATS, commit=SHA, built=BUILT, dirty=False)
    lines = pra.package(tmp_path / "r1", assets, **kw)
    names = {l.split("  ")[1] for l in lines}
    assert names == {"incidents.stix.json", "incidents.min.json", "taxii2.zip",
                     "misp-feed.zip", "build_manifest.json"}
    assert ei.verify_sums(tmp_path / "r1") == []
    assert ei.validate_manifest(json.loads((tmp_path / "r1" / "build_manifest.json").read_text(encoding="utf-8"))) == []
    pra.package(tmp_path / "r2", assets, **kw)
    assert (tmp_path / "r1" / "SHA256SUMS").read_bytes() == (tmp_path / "r2" / "SHA256SUMS").read_bytes()
    with zipfile.ZipFile(tmp_path / "r1" / "misp-feed.zip") as z:
        assert "SHA256SUMS" in z.namelist() and "build_manifest.json" in z.namelist()
        assert all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist())


def test_release_assets_min_json_is_a_byte_copy_so_it_carries_tier():
    """The release's incidents.min.json is `data/incidents.min.json` verbatim (WS6-T9:
    `tier` must survive into every distributed variant), asserted on the real asset list."""
    src = dict(pra.ASSETS)["incidents.min.json"]
    assert src == ROOT / "data" / "incidents.min.json"
    rows = json.loads(src.read_text(encoding="utf-8"))["incidents"]
    assert any(r.get("tier") == "landmark" for r in rows)


def test_huggingface_build_ships_manifest_and_sums(tmp_path):
    import export_huggingface as hf
    n, jsonl = hf.build(tmp_path)
    assert ei.verify_sums(tmp_path) == []
    m = json.loads((tmp_path / ei.MANIFEST_NAME).read_text(encoding="utf-8"))
    assert ei.validate_manifest(m) == [] and m["incident_count"] == n == STATS["incident_count"]
    listed = ei.parse_sums((tmp_path / "SHA256SUMS").read_text(encoding="utf-8"))
    assert set(listed) == {"incidents.jsonl", "README.md", "build_manifest.json"}


def test_package_build_manifest_is_none_when_unstamped_and_a_dict_when_stamped(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT / "src"))   # src/ layout, no install needed
    import genai_incidents as g
    real = tmp_path / "pkg"
    (real / "data").mkdir(parents=True)

    class _Files:
        def __init__(self, base): self.base = base
        def joinpath(self, rel): return self.base / rel

    monkeypatch.setattr(g, "files", lambda _name: _Files(real))
    assert g.build_manifest() is None
    ei.write_manifest(real / "data" / "build_manifest.json", stats=STATS, commit=SHA, built=BUILT, dirty=False)
    got = g.build_manifest()
    assert got["commit"] == SHA and got["disputed_count"] == STATS["disputed_count"]
    assert ei.validate_manifest(got) == []


# --- D57: MISP machinetags --------------------------------------------------------


def _misp_attrs(tmp_path, monkeypatch, rows):
    monkeypatch.setattr(misp, "OUT", tmp_path)
    misp.build(rows)
    out = []
    for p in tmp_path.glob("*.json"):
        if p.name != "manifest.json":
            out += json.loads(p.read_text(encoding="utf-8"))["Event"]["Attribute"]
    return out


def test_misp_freshness_machinetags_only_on_marked_rows(tmp_path, monkeypatch):
    attrs = _misp_attrs(tmp_path, monkeypatch, ROWS)
    fresh = lambda a: {t["name"] for t in a["Tag"] if t["name"].startswith(
        ("genai-incidents:source-freshness", "genai-incidents:source-as-of",
         "genai-incidents:source-review-by"))}
    marked = [a for a in attrs if a["comment"].startswith("INC-00002")]
    unmarked = [a for a in attrs if a["comment"].startswith("INC-00001")]
    assert marked and unmarked
    for a in marked:        # every attribute of the marked row (title and link)
        assert fresh(a) == {'genai-incidents:source-freshness="stale"',
                            'genai-incidents:source-as-of="2026-05-31"',
                            'genai-incidents:source-review-by="2027-01-07"'}
    assert all(not fresh(a) for a in unmarked)


def test_misp_omits_review_by_tag_when_the_marker_has_none(tmp_path, monkeypatch):
    rows = copy.deepcopy(ROWS)
    del rows[1]["source_freshness"]["review_by"]
    attrs = _misp_attrs(tmp_path, monkeypatch, rows)
    names = {t["name"] for a in attrs for t in a["Tag"]}
    assert not any(n.startswith("genai-incidents:source-review-by") for n in names)
    assert 'genai-incidents:source-as-of="2026-05-31"' in names


def test_misp_real_feed_marked_incident_set_equals_marked_rows(tmp_path, monkeypatch):
    raw = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    rows = [e for e in raw if e.get("status") not in ("retracted", "unverified")]
    marked = {e["id"] for e in rows if e.get("source_freshness")}
    attrs = _misp_attrs(tmp_path, monkeypatch, rows)
    tagged = {t["name"].split('"')[1] for a in attrs for t in a["Tag"]
              if t["name"].startswith("genai-incidents:incident-id=") and
              any(x["name"].startswith("genai-incidents:source-freshness=") for x in a["Tag"])}
    assert tagged == marked and len(marked) > 0


# --- MISP event timestamps derive from `updated` ---------------------------------


def test_misp_event_timestamp_moves_when_an_event_changes_and_only_that_event(tmp_path, monkeypatch):
    def stamps(rows, sub):
        monkeypatch.setattr(misp, "OUT", tmp_path / sub)
        misp.build(rows)
        man = json.loads((tmp_path / sub / "manifest.json").read_text(encoding="utf-8"))
        return {v["info"][-4:]: int(v["timestamp"]) for v in man.values()}
    base = stamps(ROWS, "a")
    changed = copy.deepcopy(ROWS)
    changed[1]["updated"] = "2026-03-01"
    after = stamps(changed, "b")
    assert after["2026"] == base["2026"]            # the other event is untouched
    assert after["2025"] > base["2025"]
    monkeypatch.setattr(misp, "EXPORTER_VERSION", misp.EXPORTER_VERSION + 1)
    bumped = stamps(ROWS, "c")
    assert all(bumped[y] == base[y] + 1 for y in base)


# --- TAXII ----------------------------------------------------------------------------


def test_taxii_manifest_version_is_the_objects_modified(tmp_path, monkeypatch):
    monkeypatch.setattr(taxii, "OUT", tmp_path)
    taxii.build(ROWS)
    coll = tmp_path / "api" / "collections" / taxii.COLLECTION_ID
    objs = {o["id"]: o for o in json.loads((coll / "objects.json").read_text(encoding="utf-8"))["objects"]}
    for rec in json.loads((coll / "manifest.json").read_text(encoding="utf-8"))["objects"]:
        assert rec["version"] == objs[rec["id"]]["modified"]
        assert rec["date_added"] == objs[rec["id"]]["created"]
        assert rec["version"] >= rec["date_added"]
