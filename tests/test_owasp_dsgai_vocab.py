"""D133: every DSGAI code on a corpus row must be in the committed OWASP vocabulary.

Before this, ``owasp_dsgai`` was a field with no controlled vocabulary: the
schema accepted any ``DSGAInn``, so ``DSGAI99`` would have shipped. The
vocabulary is mappings/owasp_dsgai_2026.json (21 codes, OWASP GenAI Data
Security Risks and Mitigations 2026). The fire proof is the planted-input test.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "mappings" / "owasp_dsgai_2026.json"


def _vocab_ids() -> set[str]:
    raw = json.loads(VOCAB.read_text(encoding="utf-8"))
    return {e["id"] for e in raw["entries"]}


def unknown_codes(rows: list[dict], vocab: set[str]) -> dict[str, list[str]]:
    """Map each out-of-vocabulary DSGAI code to the ids of the rows carrying it."""
    bad: dict[str, list[str]] = {}
    for r in rows:
        for c in r.get("owasp_dsgai") or []:
            if c not in vocab:
                bad.setdefault(c, []).append(r.get("id", "?"))
    return bad


def test_vocab_shape():
    raw = json.loads(VOCAB.read_text(encoding="utf-8"))
    ids = [e["id"] for e in raw["entries"]]
    assert ids == [f"DSGAI{n:02d}" for n in range(1, 22)]
    assert all(e["name"].strip() for e in raw["entries"])
    assert raw["version"] == "2026"
    assert raw["citation"]["status_in_this_dataset"] == "companion"


def test_every_corpus_dsgai_code_is_in_the_vocabulary():
    rows = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    rows = rows.get("incidents", rows) if isinstance(rows, dict) else rows
    assert unknown_codes(rows, _vocab_ids()) == {}


def test_unknown_code_is_caught():
    """Planted input: the check must fail on DSGAI99 (a valid pattern, not a real code)."""
    rows = [{"id": "INC-TEST", "owasp_dsgai": ["DSGAI01", "DSGAI99"]}]
    assert unknown_codes(rows, _vocab_ids()) == {"DSGAI99": ["INC-TEST"]}
