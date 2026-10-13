"""evaluate_ai_relevance.py -- N9 follow-up: score scripts/ai_relevance.py against HUMAN labels.

NOT RUN YET (v2.13.0 item 5): it waits for the user's returned review sheet.
Until human labels exist it prints "no human labels" and exits 3. Agent
suggestions are never read (labels come from ``wilson_ci.read_human_labels``,
which reads the human columns only).

What it will compute, once human labels exist
---------------------------------------------
Population: the sampled rows in the ``*/cve-ghsa`` strata (ai_relevance.py
decides CVE-shaped records only; OECD/AIID/AIAAIC rows are admitted by other
paths and are out of its domain). Rows labelled ``unsure`` are excluded and
counted separately.

For each row: ``assess(description, product_strings)`` from
scripts/ai_relevance.py, where ``description`` is the row's description in
data/incidents.json and ``product_strings`` are the comma/semicolon-separated
parts of its ``affected`` field. Known approximation: the ingest-time call
also receives the CVE record's own vendor/product/package/repo fields and the
assigning CNA; the corpus row keeps only ``affected``, so the Linux-CNA rule
cannot fire and product matching sees less than at ingest. The output states
this; for an exact replay, re-run assess on the cached cvelistV5 records.

Output: the confusion matrix (positive = human in-scope; predicted positive =
assess() admits) with TP/FP/FN/TN, the filter's precision and recall against
the human labels (each with a Wilson 95% interval), and the per-row table of
disagreements. Unweighted: this evaluates the FILTER on the rows it would
judge, not the corpus.

    python scripts/evaluate_ai_relevance.py [--audit-dir DIR] [--data data/incidents.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wilson_ci as w  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def product_strings(entry: dict) -> list[str]:
    return [p.strip() for p in re.split(r"[,;]", entry.get("affected") or "") if p.strip()]


def evaluate(audit_dir: Path, incidents: dict[str, dict], assess=None) -> dict:
    labels = w.read_human_labels(audit_dir / w.SHEET_FILE)
    if not labels:
        return {"status": "no human labels"}
    if assess is None:
        from ai_relevance import assess  # noqa: PLC0415 - heavy import only when labels exist
    sample = json.loads((audit_dir / w.SAMPLE_FILE).read_text(encoding="utf-8"))
    cm = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    disagreements, unsure = [], 0
    for e in sample["entries"]:
        if not e["stratum"].endswith("/cve-ghsa") or e["id"] not in labels:
            continue
        lab = labels[e["id"]]
        if lab == "unsure":
            unsure += 1
            continue
        row = incidents[e["id"]]
        pred, why = assess(row.get("description") or "", product_strings(row))
        truth = lab == "in-scope"
        key = ("T" if pred == truth else "F") + ("P" if pred else "N")
        cm[key] += 1
        if pred != truth:
            disagreements.append({"id": e["id"], "human": lab, "ai_relevance": pred, "why": why})
    out = {"status": "evaluated", "confusion_matrix": cm, "unsure_excluded": unsure,
           "approximation": "product strings from `affected` only; assigner unknown (Linux-CNA rule inactive)",
           "disagreements": disagreements}
    for name, num, den in (("precision", cm["TP"], cm["TP"] + cm["FP"]), ("recall", cm["TP"], cm["TP"] + cm["FN"])):
        out[name] = None if den == 0 else {"value": round(num / den, 4), "n": den,
                                           "ci95": [round(v, 4) for v in w.wilson(num, den)]}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate ai_relevance.py against human precision labels.")
    ap.add_argument("--audit-dir", type=Path, default=None)
    ap.add_argument("--data", type=Path, default=ROOT / "data" / "incidents.json")
    a = ap.parse_args(argv)
    try:
        audit_dir = a.audit_dir or w.sole_audit_dir()
    except w.AuditDirError as exc:
        print(f"[eval-ai-relevance] REFUSED: {exc}")
        return 2
    try:
        labels = w.read_human_labels(audit_dir / w.SHEET_FILE)
    except w.LabelError as exc:
        print(f"[eval-ai-relevance] REFUSED: {exc}")
        return 2
    if not labels:
        print("[eval-ai-relevance] no human labels: evaluation waits for the returned review sheet.")
        return 3
    incidents = {e["id"]: e for e in json.loads(a.data.read_text(encoding="utf-8"))["incidents"]}
    print(json.dumps(evaluate(audit_dir, incidents), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
