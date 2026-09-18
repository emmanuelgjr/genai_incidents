"""WS6-T9 -- the landmark subset must be selectable in everything we ship.

README tells readers to cite the `landmark` count rather than the corpus
total when they mean "notable incidents", and the invariant-6 stats markers
publish that count on every surface. For three months no consumer could
select those rows from anything but `data/incidents.json`: the commit that
introduced `tier` (#68) shipped the schema entry, the dictionary row,
`stats.landmark_count`, the site's Tier `<select>` and app.js's `e.tier`
filter -- and never added the field to `_slim_entry`, so the slim JSON, the
site bundle and the PyPI package copy all lacked it. The site filter matched
zero rows from the day it shipped; it was removed under WS6-T5 as dead.

This module is the gate that keeps that from recurring. It has four jobs:

  1. **Per-variant carry.** Each distributed variant is checked to carry
     `tier` (as `tier`, `x_tier` or a MISP tag, per its own conventions).
     Checks are per-entity where possible -- slim rows are compared to full
     rows id-by-id, not by comparing two totals, because an aggregate that
     still balances while the rows inside it are wrong is this project's
     documented failure shape (working agreement 6(d)).

  2. **The definition matches the code.** `_derive_tier` is re-implemented
     here from the DOCUMENTED rule and compared against the real function
     over an exhaustive truth table. This is deliberately a second,
     independent derivation rather than a re-run of the first: it fires if
     the code rule and the published definition drift apart in either
     direction. It would have caught the defect WS6-T9 found, where the
     dictionary and schema both still listed a `category == "real-world"`
     criterion that was dropped from the code before #68 merged -- read
     literally, the published definition described ~3.6x the rows the code
     actually marks.

  3. **New variants cannot appear silently.** The producer registry below
     fails when a script starts reading `incidents.json` /
     `incidents.min.json` without being registered with a stated disposition
     for `tier`. A fix that lands in some variants and not others recreates
     the original defect in a subtler form, and a hand-maintained list that
     nothing forces to grow is exactly the hole it pretends to close (the
     same mistake `check_dead_filters.py` was bounced for).

  4. **The freeze does not become permanent silence.** `data/` is frozen
     under D25(a), so the committed slim artifacts still lack `tier`; they
     gain it on the first rebuild. Those assertions are `xfail(strict=True)`
     rather than skipped -- a skipped test is a check that cannot fail. On
     the rebuild they XPASS, strict mode turns that into a failure, and
     whoever rebuilds is forced to delete the marker. The gate disarms
     itself; nobody has to remember.

Proving it fires (working agreement 6): each carry assertion was confirmed
to fail by deleting the corresponding field from the producer and re-running
-- see the "measured" notes in
docs/specs/WS6-T9-landmark-distribution-2026-09-18.md.
"""

from __future__ import annotations

import inspect
import itertools
import json
import re
from pathlib import Path

import pytest

import export_huggingface as hf
import export_misp as misp
import export_stix as stix
import gen_docs_core_data as core
import merge_and_dedupe as m

ROOT = Path(__file__).resolve().parents[1]

# Make the src/ layout importable without installing the package (same
# preamble as tests/test_package.py).
import sys  # noqa: E402

sys.path.insert(0, str(ROOT / "src"))

import genai_incidents as gi  # noqa: E402


# ---------------------------------------------------------------------------
# 1. The definition of record, re-derived independently
# ---------------------------------------------------------------------------

def _documented_rule(entry: dict) -> str:
    """The rule as published in docs/DATA_DICTIONARY.md and the schema.

    Written from the prose, not copied from `_derive_tier`: copying would
    make this a rerun of the path that produced the artifact, which cannot
    fail (working agreement 6(b)).
    """
    if (entry.get("quality_tier") == "curated"
            or entry.get("aiid_id")
            or entry.get("corpus") == "ai-harm"):
        return "landmark"
    return "feed"


def test_derive_tier_matches_the_published_definition():
    quality = ["curated", "reviewed", "auto", None]
    aiid = [None, 1234]
    corpora = ["security", "ai-harm", None]
    # `category` is in the matrix on purpose: the retired wording made
    # category == "real-world" a landmark criterion, so if anyone restores
    # it in code this comparison fails instead of silently re-inflating the
    # published count.
    categories = ["real-world", "vulnerability-disclosure", None]
    for q, a, c, cat in itertools.product(quality, aiid, corpora, categories):
        entry = {"quality_tier": q, "aiid_id": a, "corpus": c, "category": cat}
        assert m._derive_tier(entry) == _documented_rule(entry), entry


def test_category_real_world_is_not_a_landmark_criterion():
    """The specific regression the published definition claimed for months."""
    entry = {"quality_tier": "auto", "corpus": "security", "category": "real-world"}
    assert m._derive_tier(entry) == "feed"


@pytest.mark.parametrize("doc", [
    ROOT / "docs" / "DATA_DICTIONARY.md",
    ROOT / "schema" / "incident.schema.json",
    ROOT / "src" / "genai_incidents" / "schema" / "incident.schema.json",
])
def test_published_definition_names_the_three_real_criteria(doc):
    text = doc.read_text(encoding="utf-8")
    # Narrow the window to the `tier` definition so unrelated prose (the
    # `category` field's own row, for instance) cannot satisfy or trip this.
    start = text.index("landmark")
    window = text[max(0, start - 2000): start + 4000]
    for needle in ("quality_tier", "aiid_id", "ai-harm"):
        assert needle in window, f"{doc.name}: tier definition omits {needle}"


def test_schema_copies_are_byte_identical():
    """The PyPI package ships its own schema copy, synced by hand.

    A drifted copy is the same defect one level up: the distributed artifact
    no longer describes the field the way the source of truth does.
    """
    a = (ROOT / "schema" / "incident.schema.json").read_bytes()
    b = (ROOT / "src" / "genai_incidents" / "schema" / "incident.schema.json").read_bytes()
    assert a == b, "schema/ and src/genai_incidents/schema/ have drifted"


def test_schema_permits_tier_and_pins_the_enum():
    schema = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["tier"]["enum"] == ["landmark", "feed"]


# ---------------------------------------------------------------------------
# 2. Per-variant carry, measured against a real rebuild
# ---------------------------------------------------------------------------

def _setup_tmp_repo(tmp_path, monkeypatch):
    data = tmp_path / "data"
    ingest = tmp_path / "ingest"
    data.mkdir()
    ingest.mkdir()
    monkeypatch.setattr(m, "DATA", data)
    monkeypatch.setattr(m, "INGEST", ingest)
    monkeypatch.setattr(m, "DEPRECATIONS_PATH", data / "id_deprecations.json")
    monkeypatch.setattr(m, "CURATION_OVERRIDES_PATH", data / "curation_overrides.json")
    monkeypatch.setattr(m, "SOURCE_FRESHNESS_PATH", data / "source_freshness.json")
    return data, ingest


def _mixed_corpus():
    """Two rows that land on opposite sides of the tier split.

    A single-tier fixture would let a builder that hardcodes one value pass.
    """
    return [
        {
            "source_id": "AIID-4242",
            "aiid_id": 4242,
            "title": "A catalogued real-world AI harm",
            "description": "A description long enough to pass the minimum length filter.",
            "year": 2026, "date": "2026-04-01",
            "attack_vector": "deepfake", "severity": "High",
            "references": [{"url": "https://incidentdatabase.ai/cite/4242"}],
            "tags": ["aiid"],
        },
        {
            "source_id": "CVE-2026-9999",
            "title": "Arbitrary code execution in an inference server",
            "description": "A description long enough to pass the minimum length filter.",
            "year": 2026, "date": "2026-05-02",
            "attack_vector": "rce", "severity": "High",
            "cve_ids": ["CVE-2026-9999"],
            "references": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2026-9999"}],
            "tags": ["nvd"],
        },
    ]


@pytest.fixture()
def rebuilt(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    (ingest / "src.json").write_text(json.dumps(_mixed_corpus()), encoding="utf-8")
    m.main()
    full = json.loads((data / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    slim = json.loads((data / "incidents.min.json").read_text(encoding="utf-8"))["incidents"]
    return data, full, slim


def test_fixture_spans_both_tiers(rebuilt):
    """Guard on the guard: if the fixture collapses to one tier, the carry
    tests below stop being able to catch a hardcoded value."""
    _, full, _ = rebuilt
    assert {e["tier"] for e in full} == {"landmark", "feed"}


def test_min_json_carries_tier_for_every_row(rebuilt):
    _, full, slim = rebuilt
    full_by_id = {e["id"]: e for e in full}
    assert slim, "no rows built"
    for row in slim:
        assert "tier" in row, f"{row['id']}: min.json dropped `tier`"
        # Per-entity, not a count comparison: two totals can agree while the
        # rows behind them disagree.
        assert row["tier"] == full_by_id[row["id"]]["tier"], row["id"]


def test_min_json_tier_is_never_null(rebuilt):
    _, _, slim = rebuilt
    assert all(r["tier"] in ("landmark", "feed") for r in slim)


def test_landmark_count_reproducible_from_min_json(rebuilt):
    """The property README's instruction actually needs."""
    _, full, slim = rebuilt
    assert (sum(1 for e in slim if e["tier"] == "landmark")
            == sum(1 for e in full if e["tier"] == "landmark") >= 1)


def test_site_core_bundle_carries_tier(rebuilt, tmp_path, monkeypatch):
    data, full, _ = rebuilt
    docs_data = tmp_path / "docs_data"
    monkeypatch.setattr(core, "SRC", data / "incidents.min.json")
    monkeypatch.setattr(core, "DOCS_DATA", docs_data)
    monkeypatch.setattr(core, "CORE_OUT", docs_data / "incidents.core.json")
    monkeypatch.setattr(core, "DETAIL_DIR", docs_data / "detail")
    assert core.main() == 0
    payload = json.loads((docs_data / "incidents.core.json").read_text(encoding="utf-8"))
    full_by_id = {e["id"]: e for e in full}
    assert payload["incidents"]
    for row in payload["incidents"]:
        assert row["tier"] == full_by_id[row["id"]]["tier"], row["id"]


def test_tier_is_a_core_field_not_a_lazy_detail_shard():
    # The site's filter/stats path reads only the core payload on first load.
    assert "tier" in core.CORE_FIELDS
    assert "tier" not in core.DETAIL_FIELDS


def test_huggingface_jsonl_carries_tier(rebuilt, tmp_path, monkeypatch):
    data, full, _ = rebuilt
    monkeypatch.setattr(hf, "DATA", data)
    n, jsonl = hf.build(tmp_path / "hf")
    rows = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == n == len(full)
    full_by_id = {e["id"]: e for e in full}
    for row in rows:
        assert row["tier"] == full_by_id[row["id"]]["tier"], row["id"]


def test_huggingface_card_documents_tier():
    card = hf.CARD
    assert "`tier`" in card
    assert "landmark" in card


def test_stix_sdo_carries_x_tier(rebuilt):
    _, full, _ = rebuilt
    bundle = stix.build_bundle(full)
    sdos = [o for o in bundle["objects"] if o["type"] == "x-genai-incident"]
    by_id = {o["x_incident_id"]: o for o in sdos}
    full_by_id = {e["id"]: e for e in full}
    assert by_id
    for iid, sdo in by_id.items():
        assert sdo["x_tier"] == full_by_id[iid]["tier"], iid


def test_taxii_mirror_inherits_the_stix_bundle():
    """TAXII has no field list of its own -- it imports build_bundle.

    Asserted structurally so a future refactor that copy-pastes the SDO
    shape into export_taxii.py (and forgets x_tier) fails here.
    """
    src = (ROOT / "scripts" / "export_taxii.py").read_text(encoding="utf-8")
    assert "from export_stix import build_bundle" in src
    assert "x_genai_incident" not in src and '"x-genai-incident"' not in src


def test_misp_feed_tags_tier(rebuilt):
    _, full, _ = rebuilt
    for entry in full:
        tags = {t["name"] for t in misp._incident_tags(entry)}
        assert f'genai-incidents:tier="{entry["tier"]}"' in tags, entry["id"]


def test_package_query_filters_on_tier(monkeypatch):
    fake = {"incidents": [
        {"id": "INC-00001", "tier": "landmark", "quality_tier": "auto"},
        {"id": "INC-00002", "tier": "feed", "quality_tier": "curated"},
    ]}
    monkeypatch.setattr(gi, "_load_raw", lambda: fake)
    assert [e["id"] for e in gi.query(tier="landmark")] == ["INC-00001"]
    assert [e["id"] for e in gi.query(tier="feed")] == ["INC-00002"]
    # tier and quality_tier are independent axes; the fixture crosses them
    # so a filter wired to the wrong key cannot pass.
    assert [e["id"] for e in gi.query(quality_tier="curated")] == ["INC-00002"]


def test_package_query_exposes_tier_keyword():
    assert "tier" in inspect.signature(gi.query).parameters


# ---------------------------------------------------------------------------
# 3. New distribution producers cannot appear silently
# ---------------------------------------------------------------------------
#
# Every distributed variant is ultimately derived from one of the two root
# artifacts, so "reads data/incidents.json or data/incidents.min.json" is a
# precise, greppable definition of "is a distribution producer (or a
# consumer close enough to matter)". Discovery is by scan, not by a
# hand-maintained list that nothing forces to grow; the list below only
# records the DISPOSITION of each script, and a new one fails the gate until
# somebody states its disposition.
#
# CARRIES  -- emits `tier` (or x_tier / a MISP tag) into a distributed file.
# INHERITS -- distributes it, but by reusing another producer's builder
#             rather than naming the field itself.
# INTERNAL -- reads the corpus but distributes nothing derived from it
#             (validators, audits, build inputs, one-shot migrations).
REGISTERED_PRODUCERS = {
    # -- carry `tier` into something a consumer receives --
    "merge_and_dedupe.py": "CARRIES (incidents.json + incidents.min.json)",
    "render_markdown.py": "CARRIES (copies min.json to docs/data + the PyPI package)",
    "gen_docs_core_data.py": "CARRIES (incidents.core.json, via CORE_FIELDS)",
    "export_huggingface.py": "CARRIES (verbatim row dump to incidents.jsonl)",
    "export_stix.py": "CARRIES (x_tier on each x-genai-incident SDO)",
    "export_taxii.py": "INHERITS (imports build_bundle from export_stix; asserted structurally by test_taxii_mirror_inherits_the_stix_bundle)",
    "export_misp.py": "CARRIES (genai-incidents:tier tag)",
    # -- read the corpus, distribute nothing derived from it --
    "validate.py": "INTERNAL (schema + landmark-label gate)",
    "check_dead_filters.py": "INTERNAL (CI gate over the served payload)",
    "audit_cve_bridge.py": "INTERNAL (audit report)",
    "make_og_image.py": "INTERNAL (renders counts into an image, no per-row fields)",
    "parse_existing.py": "INTERNAL (build input)",
    "ingest_aiaaic_sheet.py": "INTERNAL (ingest, reads the corpus for cross-reference)",
    "ingest_aiid_snapshot.py": "INTERNAL (ingest)",
    "ingest_airi_navigator.py": "INTERNAL (ingest)",
    "ingest_oecd_aim.py": "INTERNAL (ingest)",
    "migrate_oecd_description_reduction.py": "INTERNAL (one-shot migration over build inputs)",
    "migrate_owasp_llm_2026.py": "INTERNAL (one-shot migration over build inputs)",
}

_ROOT_ARTIFACT_RE = re.compile(r"incidents(\.min)?\.json")


def _discover_producers() -> set[str]:
    found = set()
    for path in sorted((ROOT / "scripts").glob("*.py")):
        if _ROOT_ARTIFACT_RE.search(path.read_text(encoding="utf-8")):
            found.add(path.name)
    return found


def test_no_unregistered_distribution_producer():
    found = _discover_producers()
    registered = set(REGISTERED_PRODUCERS)
    new = found - registered
    assert not new, (
        "unregistered script(s) reading the corpus: "
        + ", ".join(sorted(new))
        + " -- add each to REGISTERED_PRODUCERS in this file, stating whether "
          "it CARRIES `tier` into a distributed artifact or is INTERNAL. A fix "
          "that lands in some variants and not others is the WS6-T9 defect "
          "with extra steps."
    )


def test_registry_has_no_stale_entries():
    """A registry that outlives its scripts stops describing the tree."""
    gone = set(REGISTERED_PRODUCERS) - _discover_producers()
    assert not gone, f"registered but no longer reading the corpus: {sorted(gone)}"


def test_every_carrying_producer_actually_mentions_tier():
    """Cheap, but it fires: deleting the `tier` line from any CARRIES script
    (which is exactly how this defect was introduced) fails here even if that
    script has no behavioural test of its own."""
    for name, disposition in REGISTERED_PRODUCERS.items():
        if not disposition.startswith("CARRIES"):
            continue
        src = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        assert "tier" in src, f"{name} is registered as CARRIES but never names `tier`"


# ---------------------------------------------------------------------------
# 4. The committed artifacts -- strict-xfail until the D25(a) freeze lifts
# ---------------------------------------------------------------------------
#
# These assert the property consumers actually experience: the files in this
# repository, as shipped. They fail today because `data/` is frozen and the
# slim artifacts predate the builder change above. They are NOT skipped -- a
# skipped test is a check that cannot fail, which is the failure shape this
# project keeps producing. `strict=True` means that when the first post-freeze
# rebuild lands and these start passing, pytest reports XPASS as a FAILURE and
# forces the marker's removal. The gate re-arms itself.

_SHIPPED_SLIM = [
    ROOT / "data" / "incidents.min.json",
    ROOT / "docs" / "data" / "incidents.min.json",
    ROOT / "src" / "genai_incidents" / "data" / "incidents.min.json",
]


@pytest.mark.parametrize("path", _SHIPPED_SLIM, ids=lambda p: p.parent.as_posix()[-24:])
@pytest.mark.xfail(
    strict=True,
    reason="D25(a): data/ is frozen, so the committed slim artifacts predate "
           "the WS6-T9 builder change. Rebuilding populates `tier` and turns "
           "this XPASS -> delete this marker then (see "
           "docs/specs/WS6-T9-landmark-distribution-2026-09-18.md).",
)
def test_shipped_slim_variants_carry_tier(path):
    rows = json.loads(path.read_text(encoding="utf-8"))["incidents"]
    assert rows
    assert all(r.get("tier") in ("landmark", "feed") for r in rows)


@pytest.mark.xfail(
    strict=True,
    reason="D25(a): same freeze. The shipped landmark count becomes "
           "reproducible from the slim file on the first rebuild.",
)
def test_shipped_landmark_count_reproducible_from_min_json():
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    rows = json.loads((ROOT / "data" / "incidents.min.json").read_text(encoding="utf-8"))["incidents"]
    assert sum(1 for r in rows if r.get("tier") == "landmark") == stats["landmark_count"]


def test_shipped_landmark_count_is_reproducible_from_the_full_file():
    """The one variant that has always worked -- kept as the control.

    If this ever fails, the problem is the published figure itself, not the
    distribution mechanism, and the xfails above would be misleading.
    """
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    rows = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    assert sum(1 for r in rows if r.get("tier") == "landmark") == stats["landmark_count"]
