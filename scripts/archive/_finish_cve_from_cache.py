"""Recover ingest/cve_nvd_expanded.json from cached NVD responses when the
full pipeline crashed mid-run (e.g. on a Windows subprocess encoding issue
in the GHSA phase). Loads ingest/_cache/nvd/*.json, applies the AI-context
filter via the existing nvd_to_record() function, dedupes by CVE id, writes
the final JSON.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "nvd"
OUT = INGEST / "cve_nvd_expanded.json"

# Import the sibling module by file path
SCRIPT = ROOT / "scripts" / "ingest_cve_nvd_expanded.py"
spec = importlib.util.spec_from_file_location("ingest_cve_nvd_expanded", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules["ingest_cve_nvd_expanded"] = mod
spec.loader.exec_module(mod)

records: dict[str, dict] = {}
seen_cves: set[str] = set()
files = sorted(CACHE.glob("*.json"))
print(f"Loading {len(files)} cached NVD keyword files...")

for f in files:
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: {f.name}: {e}")
        continue
    if isinstance(data, dict):
        vulns = data.get("vulnerabilities") or []
    elif isinstance(data, list):
        vulns = data
    else:
        continue
    for v in vulns:
        cve_id = ((v.get("cve") or v).get("id"))
        if not cve_id or cve_id in seen_cves:
            continue
        seen_cves.add(cve_id)
        rec = mod.nvd_to_record(v)
        if rec:
            records[rec["source_id"]] = rec

print(f"Total unique NVD CVEs: {len(seen_cves)}")
print(f"Passed AI-context filter: {len(records)}")

out = sorted(records.values(), key=lambda r: (r.get("year") or 0, r.get("date") or ""), reverse=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(out)} entries -> {OUT}")
