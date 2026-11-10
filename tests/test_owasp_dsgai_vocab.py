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


def doc_mismatches(doc_text: str, rows: list[dict]) -> list[str]:
    """The real comparison: docs/TAXONOMIES.md figures vs a recount of ``rows``.
    Returns one line per mismatch; empty means the doc matches the corpus."""
    doc = doc_figures(doc_text)
    got = recount(rows)
    out = []
    if doc[0] != got[0]:
        out.append(f"rows carrying a code: doc {doc[0]} != recount {got[0]}")
    if doc[1] != got[1]:
        out.append(f"code assignments: doc {doc[1]} != recount {got[1]}")
    # codes with zero rows are absent from the recount; the doc lists them as 0
    for c, n in doc[2].items():
        if n != got[2].get(c, 0):
            out.append(f"{c}: doc {n} != recount {got[2].get(c, 0)}")
    for c in got[2]:
        if c not in doc[2]:
            out.append(f"{c}: in the corpus but not in the doc table")
    return out


def test_taxonomies_doc_dsgai_figures_match_corpus():
    doc = doc_figures(DOC.read_text(encoding="utf-8"))
    assert len(doc[2]) == 21
    assert doc_mismatches(DOC.read_text(encoding="utf-8"), _rows()) == []


def test_taxonomies_doc_figures_check_fires_on_drift():
    """Planted drift runs the REAL comparison; expected values are derived, not pinned.
    Control first: the undrifted doc matches. Then each mutation must be reported."""
    import re

    text = DOC.read_text(encoding="utf-8")
    rows = _rows()
    assert doc_mismatches(text, rows) == []
    # (1) bump the table count of the most-used code in the doc text (value read from the doc)
    per = doc_figures(text)[2]
    code = max(per, key=per.get)
    row_re = re.compile(rf"^(\| `{code}` \|[^|]*\| )(\d+)( \|)$", re.M)
    m = row_re.search(text)
    assert m and int(m.group(2)) == per[code] > 0
    drifted = row_re.sub(lambda mm: f"{mm.group(1)}{int(mm.group(2)) + 1}{mm.group(3)}", text, count=1)
    assert drifted != text
    assert doc_mismatches(drifted, rows) == [f"{code}: doc {per[code] + 1} != recount {per[code]}"]
    # (2) corpus drift: drop that code from one carrying row; the unchanged doc must now disagree
    import copy

    rows2 = copy.deepcopy(rows)
    victim = next(r for r in rows2 if code in (r.get("owasp_dsgai") or []))
    victim["owasp_dsgai"] = [c for c in victim["owasp_dsgai"] if c != code]
    out = doc_mismatches(text, rows2)
    assert any(line.startswith(f"{code}:") for line in out) and len(out) >= 2  # per-code + assignments
    # (3) coverage-sentence drift
    sent = re.search(r"(\d+)( rows carry at least one code)", text)
    assert sent
    bumped = text.replace(sent.group(0), f"{int(sent.group(1)) + 1}{sent.group(2)}", 1)
    assert any(line.startswith("rows carrying a code") for line in doc_mismatches(bumped, rows))
