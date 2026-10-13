"""
Ingest the MIT FutureTech AI Risk Navigator (AIRI) incident dataset.

Source: https://www.airi-navigator.com/downloads/airi-data.zip
The AIRI Navigator wraps the AI Incident Database (AIID) with a richer
taxonomy (risk subdomain, causal entity/intent/timing, EU AI Act level,
severity scoring, harmed populations). Each row carries the authoritative
AIID `incident_date`, so AIRI is also our best source of truth for AIID
dates (the static-HTML scrape in scripts/scrape_aiid.py often falls back
to title-mentioned years).

Output: ingest/airi_navigator_incidents.json — picked up by
scripts/merge_and_dedupe.py and deduped by the AIID URL.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingest.common import conditional_fetch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)
ZIP_PATH = CACHE / "airi-data.zip"
ZIP_URL = "https://www.airi-navigator.com/downloads/airi-data.zip"

# AIRI subdomain → (OWASP LLM, OWASP ASI, attack_vector). Derived from the
# AIRI risk taxonomy and OWASP mappings.
SUBDOMAIN_MAP: dict[str, tuple[list[str], list[str], str]] = {
    # 1. Discrimination & Toxicity
    "1.1": (["LLM10", "LLM07"], ["ASI09"], "other"),
    "1.2": (["LLM10", "LLM07"], ["ASI09"], "other"),
    "1.3": (["LLM10", "LLM07"], ["ASI09"], "other"),
    # 2. Privacy & Security
    "2.1": (["LLM02"], ["ASI03"], "data-exfiltration"),
    "2.2": (["LLM02"], ["ASI03"], "data-exfiltration"),
    "2.3": (["LLM04", "LLM10"], ["ASI04", "ASI05"], "rce"),
    "2.4": (["LLM02", "LLM04"], ["ASI03", "ASI04"], "data-exfiltration"),
    # 3. Misinformation
    "3.1": (["LLM07"], ["ASI09"], "other"),
    "3.2": (["LLM07"], ["ASI09"], "other"),
    # 4. Malicious Actors & Misuse
    "4.1": (["LLM07"], ["ASI09"], "other"),
    "4.2": (["LLM10", "LLM03"], ["ASI02", "ASI10"], "tool-abuse"),
    "4.3": (["LLM07"], ["ASI09"], "other"),
    # 5. Human-Computer Interaction
    "5.1": (["LLM07"], ["ASI09"], "other"),
    "5.2": (["LLM03"], ["ASI09"], "other"),
    # 6. Socioeconomic & Environmental
    "6.1": ([], [], "other"),
    "6.2": ([], [], "other"),
    "6.3": ([], [], "other"),
    "6.4": (["LLM06"], [], "other"),
    "6.5": ([], [], "other"),
    # 7. AI System Safety, Failures & Limitations
    "7.1": (["LLM10"], ["ASI08"], "other"),
    "7.2": (["LLM03"], ["ASI01", "ASI10"], "agent-hijack"),
    "7.3": (["LLM10"], ["ASI08"], "other"),
    "7.4": (["LLM03"], ["ASI01", "ASI10"], "agent-hijack"),
}

# Map AIRI's `severity_highest` (0-3) to our severity label.
SEVERITY_MAP = {"0": "Low", "1": "Medium", "2": "High", "3": "Critical"}


def download_zip() -> tuple[Path, bool]:
    """Download the AIRI ZIP with conditional fetch (ETag support)."""
    data, changed = conditional_fetch(ZIP_URL, ZIP_PATH, min_cache_bytes=100_000)
    if not changed:
        print("[airi] ZIP unchanged (304), using cache")
    else:
        print(f"[airi] downloaded {len(data):,} bytes -> {ZIP_PATH.name}")
    return ZIP_PATH, changed


def load_incidents(zip_path: Path) -> list[dict]:
    rows: list[dict] = []
    with zipfile.ZipFile(zip_path) as z:
        with z.open("airi-data/incidents.csv") as f:
            text = io.TextIOWrapper(f, encoding="utf-8", newline="")
            rows = list(csv.DictReader(text))
    return rows


def normalize_row(row: dict) -> dict | None:
    aiid_id = row.get("id", "").strip()
    if not aiid_id.isdigit():
        return None

    raw_title = (row.get("title") or "").strip()
    title = re.sub(r"^\d+\.\s*", "", raw_title)  # strip the "1468. " prefix
    if len(title) < 5:
        return None

    desc = (row.get("description") or row.get("summary") or "").strip()
    if len(desc) < 20:
        desc = (desc + " " + title).strip()

    date = (row.get("date") or "").strip()
    year = None
    if re.match(r"^\d{4}", date):
        year = int(date[:4])
    if not year:
        return None

    sub = (row.get("subdomain_id") or "").strip()
    llm, asi, attack_vector = SUBDOMAIN_MAP.get(sub, ([], [], "other"))

    sev = SEVERITY_MAP.get((row.get("severity_highest") or "").strip(), "Medium")

    aiid_url = (row.get("aiid_url") or "").strip() or f"https://incidentdatabase.ai/cite/{aiid_id}"
    if not aiid_url.endswith("/"):
        aiid_url += "/"

    deployers = [d.strip() for d in (row.get("deployers") or "").split("|") if d.strip()]
    developers = [d.strip() for d in (row.get("developers") or "").split("|") if d.strip()]
    affected = ", ".join(developers[:3] + deployers[:3])[:200]

    tags = ["aiid", "airi-navigator"]
    if row.get("eu_ai_act_risk_level"):
        tags.append(
            "eu-ai-act-" + re.sub(r"\s+", "-", row["eu_ai_act_risk_level"].strip().lower())
        )
    if row.get("causal_intent") == "Intentional":
        tags.append("intentional")
    if row.get("causal_timing"):
        tags.append("ai-" + row["causal_timing"].strip().lower().replace(" ", "-"))

    return {
        "source_id": f"AIID-{aiid_id}",
        "title": title,
        "date": date,
        "year": year,
        "category": "real-world",
        "description": desc[:1500],
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": sev,
        "owasp_llm": llm,
        "owasp_asi": asi,
        "mitre_atlas": [],
        "references": [
            {"title": f"AIID incident #{aiid_id}", "url": aiid_url, "type": "report"},
            {
                "title": f"AIRI Navigator — incident {aiid_id}",
                "url": f"https://www.airi-navigator.com/incidents/{aiid_id}",
                "type": "research",
            },
        ],
        "tags": tags,
    }


def main():
    zip_path, _ = download_zip()
    rows = load_incidents(zip_path)
    print(f"[airi] loaded {len(rows)} rows from {zip_path.name}")

    out = []
    skipped = 0
    for row in rows:
        norm = normalize_row(row)
        if norm:
            out.append(norm)
        else:
            skipped += 1

    out_path = INGEST / "airi_navigator_incidents.json"
    if not out:
        sys.exit("[airi] ERROR: parsed 0 entries; committed file left untouched")
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[airi] wrote {len(out)} entries -> {out_path} (skipped {skipped})")


if __name__ == "__main__":
    main()
