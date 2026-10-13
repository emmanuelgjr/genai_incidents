#!/usr/bin/env python3
"""E23 recount (D114 follow-up): re-measure E23's marker-absence, attribution and
exclusion-tripwire figures on a given incidents.json. Read-only, offline, no
model calls. It states numbers; it edits no licensing text.

Method (docs/audits/E23-aiid-scope-measurement-2026-07-30.md section 4 and
docs/audits/E23-aiid-marking-ruling-2026-07-30.md section 4, section 5):

  union      rows carrying ANY of four AIID signals: tags contains "aiid"; an
             aiid_id field; a source id matching ^AIID-\\d+; a references[].url
             containing incidentdatabase.ai
  marker     rows in the union with a content_license marker (E23: 0)
  attrib     rows with an aiid_id whose description starts with the AIID
             template "AI Incident Database (AIID) entry #"; rows with a working
             incidentdatabase.ai link anywhere in references; at references[0]
  tripwire   for every AIID-<n> source id in ingest/aiid_incidents.json (the
             hand-curated rows) and ingest/airi_navigator_incidents.json: the
             shipped row for that id must carry the SNAPSHOT's template
             description, never the curated/AIRI file's own description text,
             and its title must not be the file's own title unless a snapshot title of one of the
             row's AIID ids equals it (merged rows legitimately ship another member's
             snapshot title)

Usage:  python scripts/audit/e23_recount.py [--ref origin/main | --incidents PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = "AI Incident Database (AIID) entry #"
AIID_SID = re.compile(r"^AIID-\d+")


def norm(s) -> str:
    return " ".join(str(s or "").replace("\xa0", " ").split())


def is_union(e: dict) -> bool:
    return ("aiid" in (e.get("tags") or []) or bool(e.get("aiid_id"))
            or any(AIID_SID.match(str(s)) for s in e.get("source_ids") or [])
            or any("incidentdatabase.ai" in (r.get("url") or "") for r in e.get("references") or []))


def measure(incidents: list[dict], snapshot: list[dict], curated: list[dict], airi: list[dict]) -> dict:
    union = [e for e in incidents if is_union(e)]
    with_id = [e for e in incidents if e.get("aiid_id")]
    snap = {r["source_id"]: r for r in snapshot}
    by_sid: dict[str, list[dict]] = {}
    for e in incidents:
        for s in e.get("source_ids") or []:
            by_sid.setdefault(s, []).append(e)

    def tripwire(rows: list[dict]) -> dict:
        ids = sorted({r["source_id"] for r in rows if AIID_SID.match(str(r.get("source_id", "")))})
        own = {r["source_id"]: norm(r.get("description")) for r in rows}
        missing_row = no_snapshot = bad_desc = bad_title = own_text_shipped = 0
        offenders: list[str] = []
        for sid in ids:
            shipped = by_sid.get(sid) or []
            if not shipped:
                missing_row += 1
                continue
            e = shipped[0]
            if sid not in snap:
                no_snapshot += 1
                offenders.append(f"{sid}: no snapshot row")
                continue
            if norm(e.get("description")) == own[sid] and own[sid] != norm(snap[sid].get("description")):
                own_text_shipped += 1
                offenders.append(f"{sid}: ships the file's own description")
            if not norm(e.get("description")).startswith(norm(TEMPLATE)) and "oecd-aim" != e.get("description_source"):
                bad_desc += 1
                offenders.append(f"{sid}: description is not the AIID template")
            members = {norm(snap[x].get("title")) for x in e.get("source_ids") or [] if x in snap}
            own_title = norm(next(r for r in rows if r["source_id"] == sid).get("title"))
            if norm(e.get("title")) == own_title and own_title not in members:
                bad_title += 1
                offenders.append(f"{sid}: ships the file's own title, not any member snapshot title")
        return {"ids": len(ids), "no_row_in_corpus": missing_row, "no_snapshot_row": no_snapshot,
                "own_text_shipped": own_text_shipped, "description_not_template": bad_desc,
                "own_title_shipped": bad_title, "offenders": offenders[:20]}

    return {
        "rows_total": len(incidents),
        "union_rows": len(union),
        "union_with_content_license": sum(1 for e in union if e.get("content_license")),
        "aiid_id_rows": len(with_id),
        "aiid_id_description_template": sum(1 for e in with_id if str(e.get("description", "")).startswith(TEMPLATE)),
        "aiid_id_link_anywhere": sum(1 for e in with_id if any("incidentdatabase.ai" in (r.get("url") or "")
                                                               for r in e.get("references") or [])),
        "aiid_id_link_at_references0": sum(1 for e in with_id if (e.get("references") or [{}])[0].get("url", "")
                                           .find("incidentdatabase.ai") >= 0),
        "aiid_id_not_template_ids": sorted(e["id"] for e in with_id if not str(e.get("description", "")).startswith(TEMPLATE)),
        "tripwire_curated_aiid_incidents": tripwire(curated),
        "tripwire_airi_navigator": tripwire(airi),
    }


def _load(rel: str) -> list[dict]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", help="measure data/incidents.json at this git ref instead of the work tree")
    ap.add_argument("--incidents")
    a = ap.parse_args()
    if a.ref:
        raw = subprocess.run(["git", "show", f"{a.ref}:data/incidents.json"], cwd=ROOT, capture_output=True,
                             check=True).stdout
        inc = json.loads(raw.decode("utf-8"))["incidents"]
        snap = json.loads(subprocess.run(["git", "show", f"{a.ref}:ingest/aiid_full.json"], cwd=ROOT,
                                         capture_output=True, check=True).stdout.decode("utf-8"))
    else:
        inc = json.loads(Path(a.incidents or ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
        snap = _load("ingest/aiid_full.json")
    m = measure(inc, snap, _load("ingest/aiid_incidents.json"), _load("ingest/airi_navigator_incidents.json"))
    print(json.dumps(m, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
