"""E23 recount tool (scripts/audit/e23_recount.py): the marker-absence and
exclusion-tripwire invariants hold on the committed corpus, and each measure is
shown to fire on a corrupted input (agreement 6)."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

import e23_recount as r  # noqa: E402

T = "AI Incident Database (AIID) entry #"
SNAP = [{"source_id": "AIID-1", "title": "Snap one", "description": T + "1: Snap one."},
        {"source_id": "AIID-2", "title": "Snap two", "description": T + "2: Snap two."}]
CUR = [{"source_id": "AIID-1", "title": "Curated one", "description": "Curated narrative of one."}]
AIRI = [{"source_id": "AIID-2", "title": "Airi two", "description": "AIRI narrative of two."}]
INC = [
    {"id": "INC-1", "source_ids": ["AIID-1"], "aiid_id": 1, "tags": ["aiid"], "title": "Snap one",
     "description": T + "1: Snap one.", "references": [{"url": "https://incidentdatabase.ai/cite/1/"}]},
    {"id": "INC-2", "source_ids": ["AIID-2"], "aiid_id": 2, "tags": ["aiid"], "title": "Snap two",
     "description": T + "2: Snap two.", "references": [{"url": "https://incidentdatabase.ai/cite/2/"}]},
    {"id": "INC-3", "source_ids": ["CVE-1"], "title": "x", "description": "y", "references": []},
]


def test_clean_synthetic_corpus_is_clean():
    m = r.measure(INC, SNAP, CUR, AIRI)
    assert m["union_rows"] == 2 and m["union_with_content_license"] == 0
    assert m["aiid_id_description_template"] == 2 and m["aiid_id_link_at_references0"] == 2
    for k in ("tripwire_curated_aiid_incidents", "tripwire_airi_navigator"):
        assert m[k]["own_text_shipped"] == 0 and m[k]["own_title_shipped"] == 0 and m[k]["description_not_template"] == 0


def test_marker_measure_fires_on_a_marked_row():
    inc = copy.deepcopy(INC)
    inc[1]["content_license"] = "CC-BY-SA-4.0"
    assert r.measure(inc, SNAP, CUR, AIRI)["union_with_content_license"] == 1


def test_union_catches_a_row_the_tag_signal_misses():
    inc = copy.deepcopy(INC)
    inc[0]["tags"] = []  # tag-only count would drop it; the other three signals keep it
    assert r.measure(inc, SNAP, CUR, AIRI)["union_rows"] == 2


def test_tripwire_fires_when_a_curated_or_airi_description_ships():
    inc = copy.deepcopy(INC)
    inc[0]["description"] = CUR[0]["description"]
    m = r.measure(inc, SNAP, CUR, AIRI)
    assert m["tripwire_curated_aiid_incidents"]["own_text_shipped"] == 1
    assert m["tripwire_curated_aiid_incidents"]["description_not_template"] == 1
    inc = copy.deepcopy(INC)
    inc[1]["description"] = AIRI[0]["description"]
    inc[1]["title"] = AIRI[0]["title"]
    m = r.measure(inc, SNAP, CUR, AIRI)
    assert m["tripwire_airi_navigator"]["own_text_shipped"] == 1 and m["tripwire_airi_navigator"]["own_title_shipped"] == 1


def test_attribution_measure_fires_on_a_row_without_the_template_or_link():
    inc = copy.deepcopy(INC)
    inc[1]["description"] = "narrative with no attribution"
    inc[1]["references"] = []
    m = r.measure(inc, SNAP, CUR, AIRI)
    assert m["aiid_id_description_template"] == 1 and m["aiid_id_link_anywhere"] == 1


def test_committed_corpus_keeps_the_e23_invariants():
    """Real data: no content_license marker on any AIID row; neither the curated
    aiid_incidents.json nor the AIRI file contributes its own text. The one known
    non-template AIID row is AIID-898 (INC-08183), E23's named exception."""
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    snap = json.loads((ROOT / "ingest" / "aiid_full.json").read_text(encoding="utf-8"))
    cur = json.loads((ROOT / "ingest" / "aiid_incidents.json").read_text(encoding="utf-8"))
    airi = json.loads((ROOT / "ingest" / "airi_navigator_incidents.json").read_text(encoding="utf-8"))
    m = r.measure(inc, snap, cur, airi)
    assert m["union_rows"] > 1500 and m["union_with_content_license"] == 0
    for k in ("tripwire_curated_aiid_incidents", "tripwire_airi_navigator"):
        assert m[k]["own_text_shipped"] == 0 and m[k]["own_title_shipped"] == 0, m[k]["offenders"]
    assert m["tripwire_airi_navigator"]["offenders"] == ["AIID-898: description is not the AIID template"]
    assert m["aiid_id_not_template_ids"] == ["INC-08183"]
