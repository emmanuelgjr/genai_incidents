"""
ingest_cisa_kev.py
==================

Download the CISA Known Exploited Vulnerabilities (KEV) catalog and write a
slim, deterministic snapshot to ``ingest/cisa_kev.json``:

    {
      "catalogVersion": "2026.06.09",
      "count": 1617,
      "vulnerabilities": {
        "CVE-2025-3248": {"dateAdded": "2025-05-12",
                          "knownRansomwareCampaignUse": "Unknown"},
        ...
      }
    }

``merge_and_dedupe.py`` reads this snapshot (never the live feed) to flag
incidents whose CVEs are known-exploited, so the build stays reproducible.
Refreshed by the weekly auto-refresh and CVE enrichment workflows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest.common import fetch_once  # noqa: E402

INGEST = ROOT / "ingest"
OUT_FILE = INGEST / "cisa_kev.json"

KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)


def main() -> None:
    INGEST.mkdir(parents=True, exist_ok=True)
    print(f"[kev] downloading {KEV_URL}", flush=True)
    body, _ = fetch_once(KEV_URL, timeout=60)
    raw = json.loads(body.decode("utf-8"))

    vulns = {}
    for v in raw.get("vulnerabilities", []):
        cve = v.get("cveID")
        if not cve:
            continue
        vulns[cve] = {
            "dateAdded": v.get("dateAdded", ""),
            "knownRansomwareCampaignUse": v.get("knownRansomwareCampaignUse", ""),
        }

    if not vulns:
        # An empty/renamed feed must not overwrite the committed snapshot and
        # report success (the AIAAIC 2026-10-13 silent-empty shape).
        sys.exit("[kev] ERROR: feed parsed to 0 CVEs; committed snapshot left untouched")

    snapshot = {
        "catalogVersion": raw.get("catalogVersion", ""),
        "count": len(vulns),
        # Sorted keys → byte-stable snapshot regardless of feed ordering.
        "vulnerabilities": dict(sorted(vulns.items())),
    }
    OUT_FILE.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[kev] wrote {len(vulns)} entries -> {OUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
