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
      "states": {"CVE-2024-7033": {"state": "REJECTED", "checked": "2026-10-03", "v": 2,
                                    "date_rejected": "...", "nvd_vuln_status": "Rejected"},
                 "CVE-2024-1234": {"state": "PUBLISHED", "checked": "2026-10-03", "v": 2},
                 "CVE-2023-1111": {"state": "PUBLISHED", "checked": "...", "v": 2,
                                    "disputed": true, "dispute_signals": ["cna-tag"]}, ...}
    }

DISPUTED is NOT a ``cveMetadata.state`` (CVE JSON 5: the state enum is
PUBLISHED | REJECTED). It is a CNA tag (``containers.cna.tags`` contains
"disputed"), an ADP tag (``containers.adp[].tags``), or, on older records, a
CNA description that begins ``** DISPUTED **``. All three are in the one JSON
this sweep already fetches, so the dispute check costs no extra request. A
disputed CVE keeps ``state: PUBLISHED`` and gains ``disputed: true`` plus
``dispute_signals``; the merge turns that into ``status: disputed``.

Every record written by this version carries ``v: 2`` ("dispute-aware"). A
record without it was checked before dispute detection existed, so the
rotation sorts it right after the never-checked ids.

All HTTP goes through ``ingest.common.fetch_once`` (invariant 5). The sweep is
restartable and budgeted: ids never checked go first, then pre-v2 records, then
the stalest check, so a bounded ``--max-requests`` run per refresh still
rotates through the whole corpus within ceil(corpus / budget) runs. A CVE can
be rejected after it was last seen PUBLISHED, which is why the rotation matters.

``--nvd-modified-days N`` is the cheap weekly path: ask NVD for every CVE
modified in the last N days (a rejection is a modification), keep those that
are Rejected AND in the corpus, and confirm each against the CVE record. A few
requests instead of thousands; it relies on NVD's modified-date index, so it is
a FEEDER for the rotation, not a substitute for it.

Each run writes a dated sweep log, ``docs/audits/cve-sweep/<date>.json`` and
``.md`` (ids checked, state changes, NVD disagreements, new REJECTED / new
DISPUTED, fetch failures, coverage). A same-day restart extends that day's log.
The process exits 1 when more than ``MAX_FAIL_RATE`` of the attempted fetches
failed, so a dead feed cannot pass as a quiet week.

Usage:
    python scripts/ingest_cve_rejections.py                  # full sweep
    python scripts/ingest_cve_rejections.py --max-requests 500
    python scripts/ingest_cve_rejections.py --nvd-modified-days 10 --max-requests 0
    python scripts/ingest_cve_rejections.py --max-requests 1200 --max-seconds 2400   # the weekly job
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest.common import fetch_once  # noqa: E402

INGEST = ROOT / "ingest"
OUT_FILE = INGEST / "cve_rejections.json"
INCIDENTS = ROOT / "data" / "incidents.json"
LOG_DIR = ROOT / "docs" / "audits" / "cve-sweep"
RECORD_VERSION = 2       # 2 = dispute-aware (see module docstring)
MAX_FAIL_RATE = 0.10     # exit non-zero above this share of failed fetches
_now = time.monotonic    # indirection so tests can drive the wall-clock budget
FEEDER_KEY = "nvd-feeder"  # failures key for the NVD feeder query (not a CVE id)

CVELIST_RAW = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="
NVD_INTERVAL = 6.5  # NVD public (keyless) contract: 5 requests / 30 s

CVE_RE = re.compile(r"^CVE-(\d{4})-(\d{4,})$")
DISPUTED_PREFIX = re.compile(r"^\s*\*\*\s*DISPUTED\s*\*\*", re.I)


def cvelist_url(cve_id: str) -> str:
    m = CVE_RE.match(cve_id)
    if not m:
        raise ValueError(cve_id)
    year, num = m.group(1), int(m.group(2))
    return f"{CVELIST_RAW}/{year}/{num // 1000}xxx/{cve_id}.json"


def corpus_cve_ids() -> list[str]:
    inc = json.loads(INCIDENTS.read_text(encoding="utf-8"))["incidents"]
    return sorted({c for e in inc for c in (e.get("cve_ids") or []) if CVE_RE.match(c)})


def dispute_signals(doc: dict) -> list[str]:
    """Where (if anywhere) a CVE JSON 5 record says it is disputed. Pure."""
    c = doc.get("containers") or {}
    cna = c.get("cna") or {}
    out = []
    if "disputed" in (cna.get("tags") or []):
        out.append("cna-tag")
    if any("disputed" in (a.get("tags") or []) for a in (c.get("adp") or []) if isinstance(a, dict)):
        out.append("adp-tag")
    for d in cna.get("descriptions") or []:
        if str(d.get("lang", "en")).lower().startswith("en") and DISPUTED_PREFIX.match(d.get("value") or ""):
            out.append("description-prefix")
            break
    return out


def parse_cve_record(doc: dict) -> dict:
    """Snapshot record (without ``checked``) from a CVE JSON 5 document. Pure."""
    meta = doc.get("cveMetadata", {})
    rec = {"state": meta.get("state", "UNKNOWN"), "v": RECORD_VERSION}
    if rec["state"] == "REJECTED" and meta.get("dateRejected"):
        rec["date_rejected"] = meta["dateRejected"]
    if rec["state"] == "PUBLISHED":
        sig = dispute_signals(doc)
        if sig:
            rec["disputed"] = True
            rec["dispute_signals"] = sig
    return rec


def check_cvelist(cve_id: str) -> dict:
    """State from the CVE record. A 404 is recorded as state NOT_IN_CVELIST."""
    try:
        body, _ = fetch_once(cvelist_url(cve_id), timeout=30)
    except OSError as e:  # HTTP errors are OSErrors carrying .code
        if getattr(e, "code", None) == 404:
            return {"state": "NOT_IN_CVELIST", "v": RECORD_VERSION}
        raise
    return parse_cve_record(json.loads(body.decode("utf-8")))


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


def rotation_order(ids: list[str], prev: dict) -> list[str]:
    """Never-checked first, then records that predate dispute detection
    (``v`` < 2, oldest check first), then the stalest dispute-aware check."""
    def key(c: str):
        r = prev.get(c)
        if r is None:
            return (0, "", c)
        if r.get("v", 1) < RECORD_VERSION:
            return (1, r.get("checked", ""), c)
        return (2, r.get("checked", ""), c)
    return sorted(ids, key=key)


def write(states: dict, fetched: str) -> None:
    snap = {"fetched": fetched, "count": len(states), "states": dict(sorted(states.items()))}
    OUT_FILE.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")


def compact(r: dict | None) -> dict | None:
    """The part of a prior record the log needs (state, dispute flag, version)."""
    if r is None:
        return None
    return {"state": r["state"], "disputed": bool(r.get("disputed")), "v": r.get("v", 1)}


def build_log(today: str, args: dict, ids: list[str], before: dict, states: dict,
              checked: dict[str, str], failures: dict[str, str], attempted: int,
              stopped_by: str = "") -> dict:
    """The dated sweep log (pure; unit-tested). ``before`` maps each checked id
    to ``compact()`` of its record before its first check today; ``checked``
    maps id -> "rotation" | "nvd-feeder"."""
    changes, new_rej, new_disp, disagree = [], [], [], []
    for c in sorted(checked):
        old, new = before.get(c), states[c]
        if old is None or old["state"] != new["state"]:
            changes.append({"id": c, "before": old["state"] if old else None, "after": new["state"]})
        if new["state"] == "REJECTED" and (old is None or old["state"] != "REJECTED"):
            new_rej.append(c)
        if new.get("disputed") and not (old and old["disputed"]):
            new_disp.append({"id": c, "signals": new["dispute_signals"],
                             "first_dispute_aware_check": old is None or old["v"] < RECORD_VERSION})
    for c, r in sorted(states.items()):
        if r["state"] == "REJECTED" and r.get("nvd_vuln_status") != "Rejected":
            disagree.append({"id": c, "cve_list": "REJECTED", "nvd": r.get("nvd_vuln_status")})
    dates = [states[c].get("checked", "") for c in ids if c in states]
    cnt: dict[str, int] = {}
    for c in checked:
        cnt[states[c]["state"]] = cnt.get(states[c]["state"], 0) + 1
    return {
        "date": today, "args": args, "stopped_by": stopped_by, "corpus_cve_count": len(ids),
        "checked_count": len(checked), "attempted": attempted, "failed_count": len(failures),
        "checked_ids": {c: checked[c] for c in sorted(checked)},
        "before": {c: before.get(c) for c in sorted(checked)},
        "state_counts_checked": dict(sorted(cnt.items())),
        "state_changes": changes, "new_rejected": new_rej, "new_disputed": new_disp,
        "nvd_disagreements": disagree,
        "failures": dict(sorted(failures.items())),
        "coverage": {
            "ids_with_dispute_aware_state": sum(1 for c in ids if states.get(c, {}).get("v", 1) >= RECORD_VERSION),
            "ids_never_checked": sum(1 for c in ids if c not in states),
            "ids_checked_before_dispute_detection": sum(
                1 for c in ids if c in states and states[c].get("v", 1) < RECORD_VERSION),
            "oldest_checked": min(dates) if dates else None,
            "currently_rejected": sum(1 for r in states.values() if r["state"] == "REJECTED"),
            "currently_disputed": sum(1 for r in states.values() if r.get("disputed")),
        },
    }


def render_log_md(log: dict) -> str:
    cov = log["coverage"]
    L = [f"# CVE rejection / dispute sweep: {log['date']}", "",
         "Generated by `scripts/ingest_cve_rejections.py`; the machine-readable twin is "
         f"`{log['date']}.json` (full id list and prior states). Snapshot: `ingest/cve_rejections.json`.", "",
         f"- Run arguments: `{json.dumps(log['args'], sort_keys=True)}`; stopped by: {log.get('stopped_by') or 'n/a'}",
         f"- Corpus CVE ids: {log['corpus_cve_count']}",
         f"- Checked on this date: {log['checked_count']} ({log['attempted']} fetch attempts, {log['failed_count']} failed)",
         f"- States found: {json.dumps(log['state_counts_checked'], sort_keys=True)}",
         f"- State changes vs the previous snapshot (including a first-ever state): {len(log['state_changes'])}",
         f"- New REJECTED: {len(log['new_rejected'])}",
         f"- New DISPUTED: {len(log['new_disputed'])}",
         f"- NVD disagreements (CVE List REJECTED, NVD not `Rejected`): {len(log['nvd_disagreements'])}",
         f"- Coverage after the run: dispute-aware {cov['ids_with_dispute_aware_state']}, "
         f"never checked {cov['ids_never_checked']}, checked before dispute detection "
         f"{cov['ids_checked_before_dispute_detection']}; oldest check {cov['oldest_checked']}",
         f"- Currently REJECTED: {cov['currently_rejected']}; currently DISPUTED: {cov['currently_disputed']}", ""]
    if log["new_rejected"]:
        L += ["## New REJECTED", ""] + [f"- {c}" for c in log["new_rejected"]] + [""]
    if log["new_disputed"]:
        L += ["## New DISPUTED", "", "| CVE | signals | first dispute-aware check |", "|---|---|---|"]
        L += [f"| {d['id']} | {', '.join(d['signals'])} | {d['first_dispute_aware_check']} |"
              for d in log["new_disputed"]] + [""]
    if log["nvd_disagreements"]:
        L += ["## NVD disagreements", "", "| CVE | CVE List | NVD |", "|---|---|---|"]
        L += [f"| {d['id']} | {d['cve_list']} | {d['nvd']} |" for d in log["nvd_disagreements"]] + [""]
    if log["failures"]:
        L += ["## Fetch failures (retried next run)", ""] + [f"- {c}: {m}" for c, m in log["failures"].items()] + [""]
    return "\n".join(L) + "\n"


def write_log(log: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{log['date']}.json").write_text(
        json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (LOG_DIR / f"{log['date']}.md").write_text(render_log_md(log), encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=-1,
                    help="rotation budget; 0 = none (only --nvd-modified-days); default unlimited")
    ap.add_argument("--nvd-modified-days", type=int, default=0)
    ap.add_argument("--max-seconds", type=float, default=0,
                    help="wall-clock budget for the rotation (0 = none). When it is spent the run "
                         "stops cleanly between fetches and writes the snapshot and the day's log, "
                         "so a CI job limit can never cancel the sweep with its output unsaved")
    args = ap.parse_args()
    started = _now()
    run_args = {"max_requests": args.max_requests, "nvd_modified_days": args.nvd_modified_days,
                "max_seconds": args.max_seconds}

    today = date.today().isoformat()
    prev = json.loads(OUT_FILE.read_text(encoding="utf-8"))["states"] if OUT_FILE.exists() else {}
    day_log = LOG_DIR / f"{today}.json"
    prior = json.loads(day_log.read_text(encoding="utf-8")) if day_log.exists() else None
    ids = corpus_cve_ids()
    order = rotation_order(ids, prev)
    states = {c: prev[c] for c in ids if c in prev}
    budget = len(order) if args.max_requests < 0 else args.max_requests

    checked: dict[str, str] = dict(prior["checked_ids"]) if prior else {}
    before: dict = dict(prior["before"]) if prior else {}
    attempted = prior["attempted"] if prior else 0
    # A same-day restart carries the day's failures over with `attempted`, so the
    # fail rate is not understated; an id that succeeds below is dropped again.
    failures: dict[str, str] = dict(prior.get("failures") or {}) if prior else {}

    def mark(cve_id: str, how: str) -> None:
        before.setdefault(cve_id, compact(prev.get(cve_id)))
        checked[cve_id] = how

    done = 0
    if args.nvd_modified_days:
        # An NVD outage must not abort the run before the rotation: it is recorded
        # as a failure (so the >10% rule can still turn the step red) and the
        # rotation proceeds.
        attempted += 1
        try:
            feeder_ids = sorted(nvd_recently_rejected(args.nvd_modified_days, set(ids)))
            failures.pop(FEEDER_KEY, None)
        except Exception as e:  # noqa: BLE001
            feeder_ids = []
            failures[FEEDER_KEY] = f"{type(e).__name__}: {e}"[:200]
            print(f"  [warn] NVD feeder: {e}", file=sys.stderr, flush=True)
        for cve_id in feeder_ids:
            attempted += 1
            try:
                rec = check_cvelist(cve_id)
            except Exception as e:  # noqa: BLE001
                failures[cve_id] = f"{type(e).__name__}: {e}"[:200]
                print(f"  [warn] {cve_id}: {e}", file=sys.stderr, flush=True)
                continue
            failures.pop(cve_id, None)
            rec["checked"] = today
            if rec["state"] == "REJECTED":
                rec["nvd_vuln_status"] = "Rejected"
            states[cve_id] = rec
            mark(cve_id, "nvd-feeder")
            print(f"[cve-rejections] NVD-modified feeder: {cve_id} -> {rec['state']}", flush=True)
    stopped_by = "exhausted"
    for cve_id in order:
        if done >= budget:
            stopped_by = "max-requests"
            break
        if args.max_seconds and _now() - started >= args.max_seconds:
            stopped_by = "max-seconds"
            print(f"[cve-rejections] wall-clock budget of {args.max_seconds:.0f}s spent after "
                  f"{done} checks; stopping cleanly", flush=True)
            break
        cur = states.get(cve_id, {})
        if cur.get("checked") == today and cur.get("v", 1) >= RECORD_VERSION:
            continue
        attempted += 1
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
            failures[cve_id] = f"{type(e).__name__}: {e}"[:200]
            print(f"  [warn] {cve_id}: {e}", file=sys.stderr, flush=True)
            continue
        failures.pop(cve_id, None)
        states[cve_id] = rec
        mark(cve_id, "rotation")
        done += 1
        if done % 200 == 0:
            # Checkpoint the snapshot AND the day's log together, so a killed
            # run restarts with an accurate `before` for what it already did.
            write(states, today)
            write_log(build_log(today, run_args, ids, before, states, checked, failures,
                                attempted, "checkpoint"))
            print(f"[cve-rejections] {done}/{budget}", flush=True)

    write(states, today)
    log = build_log(today, run_args, ids, before, states, checked, failures, attempted, stopped_by)
    write_log(log)
    rejected = sorted(c for c, r in states.items() if r["state"] == "REJECTED")
    print(f"[cve-rejections] checked {done} this run; {len(states)}/{len(ids)} corpus CVEs "
          f"have a state; {len(rejected)} REJECTED; {len(log['new_disputed'])} new DISPUTED; "
          f"{len(failures)} failed -> {OUT_FILE}", flush=True)
    if attempted and len(failures) / attempted > MAX_FAIL_RATE:
        print(f"[cve-rejections] FAIL: {len(failures)}/{attempted} fetches failed "
              f"(> {MAX_FAIL_RATE:.0%})", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
