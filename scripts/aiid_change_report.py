#!/usr/bin/env python3
"""Per-field change report for AIID-driven changes, for the refresh PR body.

D120 (user ruling 2026-10-13). After the D114 lift the weekly refresh admits
upstream AIID changes through a standing class with no per-item approval, so the
PR must show what moved. This report FLAGS, it never blocks (same posture as
scripts/newly_retracted_report.py, D60). Deterministic: a per-entity diff of the
committed baseline (``git show <ref>:data/incidents.json``) against the rebuilt
``data/incidents.json``. No network, no model call.

"AIID-driven" = a row that carries an ``AIID-`` source id (before or after) and
whose fields differ from the baseline. Rows are listed for the fields a reader
would object to: severity, date/year, corpus, title, attack_vector. Each listed
row says whether it also carries OECD ids (a mixed row).

    python scripts/aiid_change_report.py [--before-ref HEAD] \
        [--after data/incidents.json] [--out-md FILE]

Exit 0 on success; any error propagates (non-zero) so the workflow can mark the
PR ``needs-ruling`` instead of passing an unknown state as clean.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTED_FIELDS = ("severity", "date", "year", "corpus", "title", "attack_vector")
MAX_ROWS_PER_FIELD = 150
# D123: GitHub caps a PR body at 65,536 characters. The report shares the body
# with the rest of it, so the copy that goes into the PR body is capped here and
# the untruncated report goes to the step summary / an artifact.
MAX_REPORT_CHARS = 40_000


def cap(md: str, max_chars: int = MAX_REPORT_CHARS) -> str:
    """Pure. Truncate *md* at a line boundary so the result, note included, is at
    most *max_chars*; append a note saying where the full report is."""
    if len(md) <= max_chars:
        return md
    nl = chr(10)
    note = (nl + nl + f"**Report truncated at {max_chars:,} characters** (it was {len(md):,}); the full report is in "
            "the workflow run's step summary and in the `aiid-change-report` run artifact." + nl)
    cut = md[: max_chars - len(note)]
    cut = cut[: cut.rfind(nl)] if nl in cut else cut
    return cut + note


def _is_aiid(e: dict) -> bool:
    return any(str(s).startswith("AIID-") for s in e.get("source_ids") or [])


def _has_oecd(e: dict) -> bool:
    return any(str(s).startswith("OECD-AIM-") for s in e.get("source_ids") or [])


def diff(before: dict, after: dict) -> dict:
    """Pure. Per-entity diff; see module docstring for scope."""
    b = {e["id"]: e for e in before.get("incidents", [])}
    a = {e["id"]: e for e in after.get("incidents", [])}
    new_ids = sorted(set(a) - set(b))
    new_rows = [a[i] for i in new_ids]
    changed: list[dict] = []
    field_counts: Counter = Counter()
    listed: dict[str, list[dict]] = {f: [] for f in LISTED_FIELDS}
    for iid in sorted(set(a) & set(b)):
        old, new = b[iid], a[iid]
        if old == new or not (_is_aiid(old) or _is_aiid(new)):
            continue
        fields = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        changed.append({"id": iid, "fields": fields})
        field_counts.update(fields)
        for f in LISTED_FIELDS:
            if f in fields:
                listed[f].append({
                    "id": iid, "before": old.get(f), "after": new.get(f),
                    "also_oecd": _has_oecd(new) or _has_oecd(old),
                })
    return {
        "new_rows_total": len(new_rows),
        "new_aiid_rows": sum(1 for e in new_rows if _is_aiid(e)),
        "new_ids": new_ids,
        "removed_ids": sorted(set(b) - set(a)),
        "changed_rows": len(changed),
        "changed_rows_also_oecd": sum(1 for c in changed if _has_oecd(a[c["id"]]) or _has_oecd(b[c["id"]])),
        "field_counts": dict(sorted(field_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "listed": listed,
    }


def _cell(v) -> str:
    s = "-" if v in (None, "") else str(v)
    s = s.replace("|", "/").replace("\n", " ")
    return s if len(s) <= 90 else s[:87] + "..."


def render_md(d: dict) -> str:
    L = ["### AIID-driven changes (D120 change report)", "",
         "A flag, not a gate: the AIID snapshot is admitted by the D114 standing class with no per-item "
         "approval, so this lists what moved relative to `main`. Rows are those carrying an `AIID-` source id.", "",
         f"- New rows overall: **{d['new_rows_total']}** (of which new AIID rows: **{d['new_aiid_rows']}**)",
         f"- Existing AIID-carrying rows changed: **{d['changed_rows']}** "
         f"(of which also carry OECD ids: **{d['changed_rows_also_oecd']}**)",
         f"- Rows removed: **{len(d['removed_ids'])}**", ""]
    if d["field_counts"]:
        L += ["| field | rows changed |", "|---|---|"]
        L += [f"| {k} | {v} |" for k, v in d["field_counts"].items()]
        L += [""]
    for f in LISTED_FIELDS:
        rows = d["listed"][f]
        if not rows:
            continue
        L += [f"#### `{f}` changes ({len(rows)})", "", "| entry | before | after | also OECD |", "|---|---|---|---|"]
        L += [f"| {r['id']} | {_cell(r['before'])} | {_cell(r['after'])} | {'yes' if r['also_oecd'] else 'no'} |"
              for r in rows[:MAX_ROWS_PER_FIELD]]
        if len(rows) > MAX_ROWS_PER_FIELD:
            L += [f"| ... {len(rows) - MAX_ROWS_PER_FIELD} more (full diff in the PR files) | | | |"]
        L += [""]
    if not d["changed_rows"] and not d["new_rows_total"]:
        L += ["No AIID-driven change and no new rows relative to `main`.", ""]
    return "\n".join(L)


def _git_show(ref: str) -> dict:
    p = subprocess.run(["git", "show", f"{ref}:data/incidents.json"], cwd=ROOT, capture_output=True, check=True)
    return json.loads(p.stdout.decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="HEAD")
    ap.add_argument("--after", default=str(ROOT / "data" / "incidents.json"))
    ap.add_argument("--out-md", help="the report as it goes into the PR body (capped, D123)")
    ap.add_argument("--out-full-md", help="the untruncated report (step summary / artifact)")
    a = ap.parse_args()
    d = diff(_git_show(a.before_ref), json.loads(Path(a.after).read_text(encoding="utf-8")))
    md = render_md(d)
    if a.out_full_md:
        Path(a.out_full_md).write_text(md, encoding="utf-8", newline="\n")
    if a.out_md:
        Path(a.out_md).write_text(cap(md), encoding="utf-8", newline="\n")
    print(md)
    print(f"[aiid-change-report] new={d['new_rows_total']} (aiid {d['new_aiid_rows']}) changed={d['changed_rows']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
