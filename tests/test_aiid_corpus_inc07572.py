"""INC-07572 corpus pin (label-scientist, 2026-11-24).

Refresh PR #110 flipped INC-07572 (AIID-195 + 2 OECD ids, a predictive-policing
civil-rights incident) from `ai-harm` to `security`. The only upstream change was
AIID's deployer string, which gained "Law Enforcement"; `_classify_corpus` keyword
"rce" substring-matches "enfo-rce-ment", and security wins ties. The fix is a
curation override keyed on AIID-195. Evidence:
docs/audits/aiid-corpus-classifier-2026-11-24.md.

Per-entity checks on the committed build, not aggregates. What makes each one fail:
* test_inc07572_is_ai_harm: removing the override and rebuilding (the row goes back
  to `security`), or any later change that moves the row's corpus.
* test_override_is_still_load_bearing: fixing the "rce" substring match in
  `_classify_corpus` (option O2). When that happens the override is redundant:
  retire it and this test together, through the curation-override process.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import merge_and_dedupe as m  # noqa: E402


def _row(rid: str) -> dict:
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    return next(r for r in data["incidents"] if r["id"] == rid)


def test_inc07572_is_ai_harm():
    r = _row("INC-07572")
    assert "AIID-195" in r["source_ids"]
    assert r["corpus"] == "ai-harm"
    ov = json.loads((ROOT / "data" / "curation_overrides.json").read_text(encoding="utf-8"))
    assert ov["overrides"]["AIID-195"]["corpus"] == "ai-harm"


def test_override_is_still_load_bearing():
    r = _row("INC-07572")
    entry = {k: r.get(k) for k in ("title", "description", "tags", "cve_ids")}
    text = (entry["title"] + " " + entry["description"] + " " + " ".join(entry["tags"])).lower()
    assert "law enforcement" in text
    # Without the override, the classifier labels this row `security`, through "rce"
    # inside "enforcement" and not through any real security keyword.
    assert m._classify_corpus(entry) == "security"
    hits = [k for k in m._SECURITY_KEYWORDS_FOR_CORPUS if k in text]
    assert hits == ["rce"], hits
