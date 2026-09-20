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

def _schema_tier() -> dict:
    return json.loads(
        (ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8")
    )["properties"]["tier"]


def _predicate_from(criteria: list[dict]):
    """Turn `x-derivation`'s criteria list into a callable.

    The published definition is READ, not transcribed. An earlier version of
    this file hand-copied `_derive_tier` into a `_documented_rule` function
    and called the comparison bidirectional; it was not. A hand-copy only
    ever detects changes to the code -- the doc side of the comparison is
    whatever the test author typed, so a criterion ADDED to the published
    definition (the direction that inflated this field's definition 3.6x for
    three months) could never fail it. Driving the predicate from the schema
    makes both directions real: code-only changes and schema-only changes
    each break the equality below.
    """
    def predicate(entry: dict) -> str:
        for c in criteria:
            value = entry.get(c["field"])
            if "equals" in c:
                if value == c["equals"]:
                    return "landmark"
            elif c.get("present") and value:
                return "landmark"
        return "feed"
    return predicate


# Every field any criterion (live or retired) can read, so the truth table
# below is exhaustive over the inputs the definition actually depends on.
_TRUTH_TABLE_DOMAIN = {
    "quality_tier": ["curated", "reviewed", "auto", None],
    "aiid_id": [None, 1234],
    "corpus": ["security", "ai-harm", None],
    "category": ["real-world", "vulnerability-disclosure", None],
}


def _truth_table() -> list[dict]:
    keys = sorted(_TRUTH_TABLE_DOMAIN)
    return [dict(zip(keys, combo))
            for combo in itertools.product(*(_TRUTH_TABLE_DOMAIN[k] for k in keys))]


def test_truth_table_covers_every_field_the_definition_reads():
    """Guard on the guard: a criterion naming a field outside the domain
    would be compared only at that field's default, which is how an
    exhaustive-looking table stops being exhaustive."""
    derivation = _schema_tier()["x-derivation"]
    named = {c["field"] for c in derivation["landmark_if_any"]}
    named |= {c["field"] for c in derivation["retired_criteria"]}
    assert named <= set(_TRUTH_TABLE_DOMAIN), (
        f"x-derivation reads {sorted(named - set(_TRUTH_TABLE_DOMAIN))}, which "
        f"_TRUTH_TABLE_DOMAIN does not vary -- extend the domain"
    )


def test_derive_tier_matches_the_published_definition_in_both_directions():
    derivation = _schema_tier()["x-derivation"]
    documented = _predicate_from(derivation["landmark_if_any"])
    assert derivation["otherwise"] == "feed"
    for entry in _truth_table():
        assert m._derive_tier(entry) == documented(entry), entry


def test_retired_criteria_are_genuinely_retired_and_the_check_is_not_vacuous():
    """Each entry in `retired_criteria` must (a) still change the outcome if
    re-applied -- otherwise listing it proves nothing -- and (b) not be
    honoured by the code.

    (a) is the part that matters: a retired criterion nobody can distinguish
    from the live rule is an assertion dressed as a test.
    """
    derivation = _schema_tier()["x-derivation"]
    live = _predicate_from(derivation["landmark_if_any"])
    assert derivation["retired_criteria"], "nothing listed as retired"
    for retired in derivation["retired_criteria"]:
        inflated = _predicate_from(derivation["landmark_if_any"] + [retired])
        differing = [e for e in _truth_table() if inflated(e) != live(e)]
        assert differing, (
            f"re-applying retired criterion {retired['field']}="
            f"{retired.get('equals')} changes nothing -- it is not actually a "
            f"distinct criterion, so listing it as retired is unfalsifiable"
        )
        # The code must side with the live rule on every row where they differ.
        for entry in differing:
            assert m._derive_tier(entry) == live(entry) != inflated(entry), entry


@pytest.mark.parametrize("doc", [
    ROOT / "docs" / "DATA_DICTIONARY.md",
    ROOT / "schema" / "incident.schema.json",
    ROOT / "src" / "genai_incidents" / "schema" / "incident.schema.json",
])
def test_prose_definition_names_the_live_criteria(doc):
    """Token presence only -- and that limit is the point of the test above.

    This catches a criterion DELETED from the prose. It cannot catch one
    ADDED, because prose has no structure to check an addition against; that
    is exactly why `x-derivation` exists and why the bidirectional gate is
    `test_derive_tier_matches_the_published_definition_in_both_directions`,
    not this. Stated rather than implied, because the earlier version of this
    module claimed a bidirectionality it did not have.
    """
    derivation = _schema_tier()["x-derivation"]
    text = doc.read_text(encoding="utf-8")
    # Narrow the window to the `tier` definition so unrelated prose (the
    # `category` field's own row, for instance) cannot satisfy or trip this.
    start = text.index("landmark")
    window = text[max(0, start - 2000): start + 4000]
    for c in derivation["landmark_if_any"]:
        needle = c.get("equals") or c["field"]
        assert needle in window, f"{doc.name}: tier definition omits {needle!r}"
        assert c["field"] in window, f"{doc.name}: tier definition omits {c['field']}"


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
    # WS4-T21 BOUNCE #4: this fixture builds a tmp corpus from ingest/
    # alone -- exactly the shape WS4-T10's legacy_consolidated.json build
    # guard (merge_and_dedupe.py) exists to catch, and it fires here on
    # every run without this opt-in. The guard's own message prescribes
    # the fix: "If this is deliberate (e.g. a test harness building its
    # own tmp corpus from ingest/ alone), set MERGE_ALLOW_MISSING_LEGACY=1."
    # This fixture predates that guard; it is deliberate.
    monkeypatch.setenv("MERGE_ALLOW_MISSING_LEGACY", "1")
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
# artifacts, so "reads data/incidents.json or data/incidents.min.json (or a
# file derived from them)" is a precise, greppable definition of "is a
# distribution producer". Discovery is by scan, not by a hand-maintained list
# that nothing forces to grow; the list below only records the DISPOSITION of
# each producer, and a new one fails the gate until somebody states its
# disposition.
#
# The scan covers `scripts/*.py` AND `docs/*.js`. The .js half was added
# after review: the first version globbed only `scripts/*.py`, and the
# registry's own stated definition -- "derived from one of the two root
# artifacts" -- plainly covers `docs/app.js`, which fetches
# `data/incidents.core.json` and writes the CSV a site visitor downloads.
# Scoping discovery to the language the author happened to be working in is
# how a gate against "the fix reached some variants and not others" misses a
# variant. It missed the CSV export.
#
# CARRIES  -- emits `tier` (or x_tier / a MISP tag) into a distributed file.
# INHERITS -- distributes it, but by reusing another producer's builder
#             rather than naming the field itself.
# PENDING  -- a distributed variant that does NOT carry it yet, with the
#             blocking reason named and a test holding the gap open.
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
    # -- a distributed variant still missing the field --
    "app.js": (
        "PENDING (the site's CSV export: CSV_COLUMNS is a hardcoded list and "
        "has no `tier` row. Deferred to WS6 and sequenced AFTER the first "
        "post-freeze rebuild -- adding the column now would ship a blank "
        "column, because the payload it reads will not carry the field until "
        "then. Held open by test_site_csv_export_carries_tier below.)"
    ),
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

# `incidents.core.json` / `detail/<year>.json` are in the pattern because the
# site was split into those two payloads by WS6-T5 -- a producer reading them
# is reading min.json's content one hop removed, and excluding them would
# re-open the hole in the language the site is actually written in.
# `data/detail/` is anchored on the `data/` prefix on purpose: an unanchored
# `detail/` matches NVD advisory URLs (`nvd.nist.gov/vuln/detail/CVE-...`) and
# pulled two ingest scripts in as false positives. A discovery rule that
# over-matches gets loosened by the next person until it under-matches.
_ROOT_ARTIFACT_RE = re.compile(r"incidents(\.min|\.core)?\.json|data/detail/")

_DISCOVERY_GLOBS = (("scripts", "*.py"), ("docs", "*.js"))


def _discover_producers() -> set[str]:
    found = set()
    for subdir, pattern in _DISCOVERY_GLOBS:
        for path in sorted((ROOT / subdir).glob(pattern)):
            if _ROOT_ARTIFACT_RE.search(path.read_text(encoding="utf-8")):
                found.add(path.name)
    return found


def test_discovery_covers_the_site_as_well_as_the_scripts():
    """The gap that let the CSV export through. Named as its own assertion so
    narrowing discovery back to Python fails here rather than silently."""
    assert ("docs", "*.js") in _DISCOVERY_GLOBS
    assert "app.js" in _discover_producers()


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


# `quality_tier` and `x_tier` both CONTAIN the substring "tier". The first
# version of the check below tested `"tier" in src` and was therefore vacuous
# for four of its seven scripts: stripping every standalone `tier` token from
# gen_docs_core_data.py left the test passing, because `quality_tier` in
# CORE_FIELDS satisfied it. That is agreement 6(a) -- a check whose output is
# the same whether or not the thing it guards is present -- inside the gate
# written to enforce agreement 6. Masking the compound names first is what
# makes it a check.
_COMPOUND_TIER_RE = re.compile(r"\b(?:quality|x)_tier\b")


def _names_tier_standalone(src: str) -> bool:
    return '"tier"' in _COMPOUND_TIER_RE.sub("", src)


def test_every_carrying_producer_actually_names_the_tier_field():
    """Cheap, but non-vacuous: deleting the `tier` line from any CARRIES
    producer (exactly how this defect was introduced) fails here even if that
    producer has no behavioural test of its own."""
    for name, disposition in REGISTERED_PRODUCERS.items():
        if not disposition.startswith("CARRIES"):
            continue
        src = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        assert _names_tier_standalone(src), (
            f"{name} is registered as CARRIES but names no standalone `tier` "
            f"field -- `quality_tier` does not count, it is a different axis"
        )


def test_the_carries_check_is_not_satisfied_by_quality_tier():
    """Prove the check above can fail, rather than asserting that it can.

    This is the exact input that silently passed before review: a source that
    mentions `quality_tier` and nothing else.
    """
    assert not _names_tier_standalone('CORE_FIELDS = ["corpus", "quality_tier"]')
    assert not _names_tier_standalone('sdo = {"x_tier": i.get("x_tier")}')
    assert _names_tier_standalone('item = {"quality_tier": q, "tier": e.get("tier")}')


# ---------------------------------------------------------------------------
# 3b. The site's CSV export -- a distributed variant, still PENDING
# ---------------------------------------------------------------------------

_APP_JS = ROOT / "docs" / "app.js"


def _csv_columns() -> list[str]:
    """Parse CSV_COLUMNS out of docs/app.js (a hardcoded [field, header] list)."""
    src = _APP_JS.read_text(encoding="utf-8")
    block = src[src.index("const CSV_COLUMNS = ["):]
    block = block[: block.index("];")]
    return re.findall(r"\[\s*'([^']+)'", block)


def test_csv_columns_parse_is_not_vacuous():
    """If the parse silently returned [], every assertion over it would pass."""
    cols = _csv_columns()
    assert len(cols) > 10 and "id" in cols and "quality_tier" in cols


@pytest.mark.xfail(
    strict=True,
    reason="WS6-T9 defect 3: docs/app.js CSV_COLUMNS has no `tier` row, so the "
           "file a site visitor downloads would be the one distributed variant "
           "without the selector. Deferred to WS6 and sequenced AFTER the first "
           "post-freeze rebuild -- adding the column before the payload carries "
           "the field ships a blank column. When WS6 adds it this XPASSes and "
           "the marker must go (see "
           "docs/specs/WS6-T9-landmark-distribution-2026-09-18.md sec 5).",
)
def test_site_csv_export_carries_tier():
    assert "tier" in _csv_columns()


def test_csv_columns_cover_every_core_field_that_is_a_filter_selector():
    """Consistency check between the payload and the CSV built from it.

    A selector the site can filter on but cannot export is a silent gap of
    the same family as the original defect. `tier` is the known exception
    while it is PENDING above; anything else is a new one.
    """
    cols = set(_csv_columns())
    selectors = {"severity", "attack_vector", "corpus", "quality_tier", "year"}
    missing = (selectors & set(core.CORE_FIELDS)) - cols
    assert not missing, f"filterable core fields absent from CSV_COLUMNS: {sorted(missing)}"


def test_csv_columns_reference_no_field_the_payload_cannot_supply():
    """The other direction: a CSV column naming a field that is in neither
    CORE_FIELDS nor DETAIL_FIELDS exports blank cells forever -- the dead-
    filter defect wearing a different hat."""
    known = set(core.CORE_FIELDS) | set(core.DETAIL_FIELDS)
    orphans = [c for c in _csv_columns() if c not in known]
    assert not orphans, f"CSV columns with no field in the served payload: {orphans}"


# ---------------------------------------------------------------------------
# 4. The committed artifacts -- WERE strict-xfail until the D25(a) freeze
#    lifted; both markers are now deleted, per their own text.
# ---------------------------------------------------------------------------
#
# These assert the property consumers actually experience: the files in this
# repository, as shipped. They fail while `data/` is frozen and the slim
# artifacts predate the builder change above. They were NOT skipped -- a
# skipped test is a check that cannot fail, which is the failure shape this
# project keeps producing. `strict=True` meant that when the first
# post-freeze rebuild landed and these started passing, pytest would report
# XPASS as a FAILURE and force the marker's removal. The gate rearmed itself.
#
# [WS4-T21 BOUNCE #4, dated 2026-09-19] It fired correctly, at the moment it
# was built for. WS4-T21's own rebuild (the D28-authorized 47-split
# remediation, merged with WS6-T9 while WS4-T21 was in review) is the first
# post-freeze rebuild: `tier` is now populated on all 13,361 rows, both
# markers below turned XPASS under `strict=True`, and per their own reason
# text -- "Rebuilding populates `tier` and turns this XPASS -> delete this
# marker then" -- both markers are deleted here, and the two tests they
# guarded are now committed as ordinary passing assertions on the shipped
# artifacts. Nobody had to remember to do this by prose alone; the tripwire
# is what forced it.

_SHIPPED_SLIM = [
    ROOT / "data" / "incidents.min.json",
    ROOT / "docs" / "data" / "incidents.min.json",
    ROOT / "src" / "genai_incidents" / "data" / "incidents.min.json",
]


@pytest.mark.parametrize("path", _SHIPPED_SLIM, ids=lambda p: p.parent.as_posix()[-24:])
def test_shipped_slim_variants_carry_tier(path):
    rows = json.loads(path.read_text(encoding="utf-8"))["incidents"]
    assert rows
    assert all(r.get("tier") in ("landmark", "feed") for r in rows)


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
