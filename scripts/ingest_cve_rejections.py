"""
ingest_cve_rejections.py
========================

Record the CVE Program's lifecycle state (PUBLISHED / REJECTED / RESERVED)
for every CVE id the corpus carries, and write a deterministic snapshot to
``ingest/cve_rejections.json``. ``merge_and_dedupe.py`` reads that snapshot
(never the live feeds) to retract entries whose CVEs are REJECTED (WS4-T2,
board note N1), so ``make build`` stays offline and reproducible.

Authoritative source: the CVE record itself, ``cveMetadata.state`` in
``CVEProject/cvelistV5`` (fetched per CVE from raw.githubusercontent.com).
Every REJECTED hit is then cross-checked against the NVD API's ``vulnStatus``
(an independent service that republishes the CVE List); the snapshot keeps
both so a disagreement is visible rather than silently resolved.

    {
      "fetched": "2026-10-03",
      "states": {"CVE-2024-7033": {"state": "REJECTED", "checked": "2026-10-03",
                                    "date_rejected": "...", "nvd_vuln_status": "Rejected"},
                 "CVE-2024-1234": {"state": "PUBLISHED", "checked": "2026-10-03"}, ...}
    }

All HTTP goes through ``ingest.common.fetch_once`` (invariant 5). The sweep is
restartable and budgeted: ids never checked go first, then the stalest check,
so a bounded ``--max-requests`` run per refresh still rotates through the whole
corpus. A CVE can be rejected after it was last seen PUBLISHED, which is why
the stalest-first rotation matters.

``--nvd-modified-days N`` is the cheap weekly path: ask NVD for every CVE
modified in the last N days (a rejection is a modification), keep those that
are Rejected AND in the corpus, and confirm each against the CVE record. A few
requests instead of thousands; it relies on NVD's modified-date index, so it is
a FEEDER for the stalest-first rotation, not a substitute for it.

Usage:
    python scripts/ingest_cve_rejections.py                  # full sweep
    python scripts/ingest_cve_rejections.py --max-requests 500
    python scripts/ingest_cve_rejections.py --nvd-modified-days 10 --max-requests 0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest.common import fetch_once  # noqa: E402

INGEST = ROOT / "ingest"
OUT_FILE = INGEST / "cve_rejections.json"
INCIDENTS = ROOT / "data" / "incidents.json"

CVELIST_RAW = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="
NVD_INTERVAL = 6.5  # NVD public (keyless) contract: 5 requests / 30 s

CVE_RE = re.compile(r"^CVE-(\d{4})-(\d{4,})$")


def cvelist_url(cve_id: str) -> str:
    m = CVE_RE.match(cve_id)
    if not m:
        raise ValueError(cve_id)
    year, num = m.group(1), int(m.group(2))
    return f"{CVELIST_RAW}/{year}/{num // 1000}xxx/{cve_id}.json"


def corpus_cve_ids() -> list[str]:
    inc = json.loads(INCIDENTS.read_text(encoding="utf-8"))["incidents"]
    return sorted({c for e in inc for c in (e.get("cve_ids") or []) if CVE_RE.match(c)})


def check_cvelist(cve_id: str) -> dict:
    """State from the CVE record. A 404 is recorded as state NOT_IN_CVELIST."""
    try:
        body, _ = fetch_once(cvelist_url(cve_id), timeout=30)
    except OSError as e:  # HTTP errors are OSErrors carrying .code
        if getattr(e, "code", None) == 404:
            return {"state": "NOT_IN_CVELIST"}
        raise
    meta = json.loads(body.decode("utf-8")).get("cveMetadata", {})
    rec = {"state": meta.get("state", "UNKNOWN")}
    if rec["state"] == "REJECTED" and meta.get("dateRejected"):
        rec["date_rejected"] = meta["dateRejected"]
    return rec


def check_nvd(cve_id: str) -> str | None:
    body, _ = fetch_once(NVD_URL + cve_id, timeout=60, min_interval=NVD_INTERVAL)
    vulns = json.loads(body.decode("utf-8")).get("vulnerabilities") or []
    return vulns[0]["cve"].get("vulnStatus") if vulns else None


def nvd_recently_rejected(days: int, corpus: set[str]) -> set[str]:
    """Corpus CVEs that NVD reports Rejected among those modified in the last
    *days* days (NVD caps a window at 120 days)."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=min(days, 120))
    fmt = "%Y-%m-%dT%H:%M:%S.000"
    hits: set[str] = set()
    idx = 0
    while True:
        qs = "&".join([
            f"lastModStartDate={start.strftime(fmt).replace(':', '%3A')}",
            f"lastModEndDate={end.strftime(fmt).replace(':', '%3A')}",
            f"startIndex={idx}", "resultsPerPage=2000",
        ])
        body, _ = fetch_once(NVD_URL.replace("?cveId=", "?") + qs, timeout=120,
                             min_interval=NVD_INTERVAL)
        page = json.loads(body.decode("utf-8"))
        for v in page.get("vulnerabilities") or []:
            cve = v["cve"]
            if cve.get("vulnStatus") == "Rejected" and cve.get("id") in corpus:
                hits.add(cve["id"])
        idx += page.get("resultsPerPage", 0) or 2000
        if idx >= page.get("totalResults", 0):
            return hits


def write(states: dict, fetched: str) -> None:
    snap = {"fetched": fetched, "count": len(states), "states": dict(sorted(states.items()))}
    OUT_FILE.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=-1,
                    help="rotation budget; 0 = none (only --nvd-modified-days); default unlimited")
    ap.add_argument("--nvd-modified-days", type=int, default=0)
    args = ap.parse_args()

    today = date.today().isoformat()
    prev = json.loads(OUT_FILE.read_text(encoding="utf-8"))["states"] if OUT_FILE.exists() else {}
    ids = corpus_cve_ids()
    # Never-checked first, then stalest; ids no longer in the corpus drop out.
    order = sorted(ids, key=lambda c: (prev.get(c, {}).get("checked", ""), c))
    states = {c: prev[c] for c in ids if c in prev}
    budget = len(order) if args.max_requests < 0 else args.max_requests

    done = 0
    if args.nvd_modified_days:
        for cve_id in sorted(nvd_recently_rejected(args.nvd_modified_days, set(ids))):
            rec = check_cvelist(cve_id)
            rec["checked"] = today
            if rec["state"] == "REJECTED":
                rec["nvd_vuln_status"] = "Rejected"
            states[cve_id] = rec
            print(f"[cve-rejections] NVD-modified feeder: {cve_id} -> {rec['state']}", flush=True)
    for cve_id in order:
        if done >= budget:
            break
        if states.get(cve_id, {}).get("checked") == today:
            continue
        try:
            rec = check_cvelist(cve_id)
            rec["checked"] = today
            if rec["state"] == "REJECTED":
                # The CVE record is authoritative; the NVD cross-check is
                # corroboration. If NVD errors, keep the verdict (status None).
                try:
                    rec["nvd_vuln_status"] = check_nvd(cve_id)
                except Exception as e:  # noqa: BLE001
                    rec["nvd_vuln_status"] = None
                    print(f"  [warn] NVD cross-check {cve_id}: {e}", file=sys.stderr, flush=True)
        except Exception as e:  # noqa: BLE001 - keep the sweep alive, retry next run
            print(f"  [warn] {cve_id}: {e}", file=sys.stderr, flush=True)
            continue
        states[cve_id] = rec
        done += 1
        if done % 200 == 0:
            write(states, today)
            print(f"[cve-rejections] {done}/{budget}", flush=True)

    write(states, today)
    rejected = sorted(c for c, r in states.items() if r["state"] == "REJECTED")
    print(f"[cve-rejections] checked {done} this run; {len(states)}/{len(ids)} corpus CVEs "
          f"have a state; {len(rejected)} REJECTED -> {OUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
