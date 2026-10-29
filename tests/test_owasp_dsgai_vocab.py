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


# --- docs/TAXONOMIES.md coverage figures must match a recount -----------------

DOC = ROOT / "docs" / "TAXONOMIES.md"
INCIDENTS = ROOT / "data" / "incidents.json"


def recount(rows: list[dict]) -> tuple[int, int, dict[str, int]]:
    """(rows carrying any code, total assignments, rows per code)."""
    per: dict[str, int] = {}
    carrying = 0
    for r in rows:
        codes = r.get("owasp_dsgai") or []
        carrying += bool(codes)
        for c in codes:
            per[c] = per.get(c, 0) + 1
    return carrying, sum(per.values()), per


def doc_figures(text: str) -> tuple[int, int, dict[str, int]]:
    import re

    m = re.search(r"(\d+) rows carry at least one code \((\d+) code assignments", text)
    assert m, "coverage sentence not found in docs/TAXONOMIES.md"
    per = {c: int(n) for c, n in re.findall(r"^\| `(DSGAI\d\d)` \|[^|]*\| (\d+) \|$", text, re.M)}
    return int(m.group(1)), int(m.group(2)), per


def _rows() -> list[dict]:
    raw = json.loads(INCIDENTS.read_text(encoding="utf-8"))
    return raw["incidents"] if isinstance(raw, dict) else raw


def test_taxonomies_doc_dsgai_figures_match_corpus():
    doc = doc_figures(DOC.read_text(encoding="utf-8"))
    assert len(doc[2]) == 21
    got = recount(_rows())
    # codes with zero rows are absent from the recount; the doc lists them as 0
    got_per = {c: got[2].get(c, 0) for c in doc[2]}
    assert (doc[0], doc[1], doc[2]) == (got[0], got[1], got_per)


def test_taxonomies_doc_figures_check_fires_on_drift():
    """Planted drift: one altered count in the doc text must not match the recount."""
    text = DOC.read_text(encoding="utf-8")
    drifted = text.replace("| `DSGAI01` | Sensitive Data Leakage | 29 |", "| `DSGAI01` | Sensitive Data Leakage | 28 |")
    assert drifted != text
    got = recount(_rows())
    d = doc_figures(drifted)
    assert d[2]["DSGAI01"] != got[2]["DSGAI01"]
