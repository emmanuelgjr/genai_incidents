"""WS6-T5 -- split the served dataset into a small "core" payload plus
lazy-loaded per-year "detail" shards, so the site's first paint does not
require transferring the entire ~15 MB dataset.

Why: measured against the unmodified page, the ENTIRE first render was
gated on one 15 MB fetch of data/incidents.min.json -- table, charts, and
stats all waited on it, on every device including a phone on a slow link.
A field-level byte audit of that file (see the WS6-T5 report) found that
`description` + `primary_reference` + `tags` + `content_license` +
`nist_ai_rmf` + `mitre_atlas` + `source_freshness` account for roughly 70%
of the JSON's field bytes, and NONE of them are read by the initial
table/filter/chart render in docs/app.js -- they are only needed when a row
is expanded (description, primary_reference, tags) or exported to CSV (all
seven).

This script is READ-ONLY against data/incidents.min.json (never writes
under data/, per the merge freeze) and writes two NEW derived artifacts
under docs/data/, alongside the untouched full mirror that pages.yml
already copies there:

  docs/data/incidents.core.json   -- every entry, core fields only
                                      (what app.js fetches on load)
  docs/data/detail/<year>.json    -- {id: {detail fields}} for that year
                                      (fetched lazily on row-expand / CSV
                                      export, one file per publication
                                      year -- ~44 files today, matching the
                                      existing docs/incidents/<year>.md
                                      shard convention, NOT one file per
                                      incident; pages.yml already documents
                                      why a per-incident file count doesn't
                                      scale under this Jekyll build)

docs/data/incidents.min.json itself is NOT touched by this script -- it
stays the single full-fidelity file for the "JSON" download link, the
STIX/TAXII/MISP export pipeline, and the SHA-256 integrity manifest.

Run: python scripts/gen_docs_core_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "incidents.min.json"
DOCS_DATA = ROOT / "docs" / "data"
CORE_OUT = DOCS_DATA / "incidents.core.json"
DETAIL_DIR = DOCS_DATA / "detail"

# Fields the initial table/filter/chart render actually reads
# (docs/app.js: matches(), renderTable(), renderStats(), renderAllCharts()).
CORE_FIELDS = [
    "id", "date", "year", "title", "severity", "attack_vector",
    "owasp_llm", "owasp_asi", "cve_ids", "affected", "corpus", "quality_tier",
]

# Everything else: only read on row-expand or CSV export, so it is deferred
# to a per-year shard instead of shipping in the initial payload.
DETAIL_FIELDS = [
    "description", "primary_reference", "tags",
    "content_license", "nist_ai_rmf", "mitre_atlas", "source_freshness",
]


def main() -> int:
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    incidents = payload["incidents"]

    core_incidents = []
    detail_by_year: dict[str, dict[str, dict]] = {}

    for e in incidents:
        core = {k: e[k] for k in CORE_FIELDS if k in e}
        core_incidents.append(core)

        detail = {k: e[k] for k in DETAIL_FIELDS if k in e}
        if detail:
            year_key = str(e.get("year", "unknown"))
            detail_by_year.setdefault(year_key, {})[e["id"]] = detail

    core_payload = {
        "version": payload.get("version"),
        "generated": payload.get("generated"),
        "incident_count": payload.get("incident_count", len(core_incidents)),
        "incidents": core_incidents,
    }

    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    # Clear stale year shards from a previous run (e.g. a year that no
    # longer has any entries) so DETAIL_DIR never accumulates orphans.
    for stale in DETAIL_DIR.glob("*.json"):
        stale.unlink()

    CORE_OUT.write_text(
        json.dumps(core_payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    for year_key, id_map in detail_by_year.items():
        (DETAIL_DIR / f"{year_key}.json").write_text(
            json.dumps(id_map, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    src_size = SRC.stat().st_size
    core_size = CORE_OUT.stat().st_size
    detail_total = sum(f.stat().st_size for f in DETAIL_DIR.glob("*.json"))
    print(
        f"[gen-docs-core-data] {len(core_incidents)} incidents, "
        f"{len(detail_by_year)} year shards\n"
        f"  incidents.min.json (unchanged): {src_size:,} bytes\n"
        f"  incidents.core.json (new, initial fetch): {core_size:,} bytes "
        f"({100 * core_size / src_size:.1f}% of full)\n"
        f"  detail/*.json total (lazy, on demand): {detail_total:,} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
