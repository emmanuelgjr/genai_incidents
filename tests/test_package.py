"""Smoke + behaviour tests for the genai_incidents pip package."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src/ layout importable without installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import genai_incidents as gi


def test_load_incidents_returns_nonempty_list():
    rows = gi.load_incidents()
    assert isinstance(rows, list)
    assert len(rows) > 100


def test_load_schema_round_trips():
    s = gi.load_schema()
    assert s.get("title", "").lower().startswith("genai")
    assert "properties" in s


def test_query_filters_combine():
    crit = list(gi.query(severity="Critical"))
    assert all(e.get("severity") == "Critical" for e in crit)

    crit_2026 = list(gi.query(severity="Critical", year=2026))
    assert all(e.get("year") == 2026 for e in crit_2026)
    assert len(crit_2026) <= len(crit)


def test_query_owasp_membership():
    rows = list(gi.query(owasp_llm="LLM01"))
    assert all("LLM01" in (e.get("owasp_llm") or []) for e in rows)


def test_query_has_cve_flag():
    with_cve = list(gi.query(has_cve=True))
    assert all(e.get("cve_ids") for e in with_cve)
    no_cve = list(gi.query(has_cve=False))
    assert all(not e.get("cve_ids") for e in no_cve)


def test_query_text_match_case_insensitive():
    rows = list(gi.query(text="copilot"))
    assert rows, "expected at least one 'copilot' hit"


def test_by_id_and_by_cve():
    rows = gi.load_incidents()
    sample = rows[0]
    assert gi.by_id(sample["id"]) == sample
    assert gi.by_id("INC-99999999") is None
    for cve in sample.get("cve_ids") or []:
        hits = gi.by_cve(cve)
        assert sample in hits
        break


def test_resolve_id_returns_active_unchanged():
    rows = gi.load_incidents()
    sample = rows[0]
    assert gi.resolve_id(sample["id"]) == sample["id"]


def test_resolve_id_unknown_returns_none():
    assert gi.resolve_id("INC-99999999") is None


def test_load_deprecations_dict_shape():
    d = gi.load_deprecations()
    assert isinstance(d, dict)
    for k, v in list(d.items())[:5]:
        assert k.startswith("INC-")
        assert v.startswith("INC-")


# --- WS4-T15: resolve_id must degrade, not crash, on a list-valued `into` --

def test_resolve_id_list_into_returns_none_not_typeerror(monkeypatch):
    # Verified crash today: `current in deprec` with `current` bound to a
    # list raises TypeError: unhashable type: 'list'. A `split`/`resplit`
    # record (WS4-T15) is list-valued by design, so this must degrade
    # safely rather than blow up every caller's first hop into one.
    monkeypatch.setattr(gi, "_load_deprecations", lambda: {"INC-1": ["INC-2", "INC-3"]})
    monkeypatch.setattr(gi, "by_id", lambda x: None)
    assert gi.resolve_id("INC-1") is None


def test_resolve_id_group_scalar_chain(monkeypatch):
    targets = {"INC-1": "INC-2", "INC-2": "INC-3"}
    live = {"INC-3"}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: targets)
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x in live else None)
    assert gi.resolve_id_group("INC-1") == ["INC-3"]
    assert gi.resolve_id_group("INC-3") == ["INC-3"]
    assert gi.resolve_id_group("INC-99999999") == []


def test_resolve_id_group_multi_successor(monkeypatch):
    deprec = {"INC-1": ["INC-2", "INC-3"]}
    live = {"INC-2", "INC-3"}
    monkeypatch.setattr(gi, "_load_deprecations", lambda: deprec)
    monkeypatch.setattr(gi, "by_id", lambda x: {"id": x} if x in live else None)
    assert set(gi.resolve_id_group("INC-1")) == {"INC-2", "INC-3"}
