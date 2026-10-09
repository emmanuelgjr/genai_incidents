#!/usr/bin/env python3
"""List the entries a refresh build NEWLY retracts, for the refresh PR body.

v2.13.0 item 3, user ruling D60 ("flag in the PR, don't block"). "Newly
retracted" = ``status == "retracted"`` in this build's ``data/incidents.json``
and not retracted in the baseline (main's committed copy; an entry absent from
the baseline counts as newly retracted). The report lists entry id, CVE id(s)
and tier, and decides ``needs_ruling``: any newly retracted LANDMARK entry, or
more than ``MAX_UNFLAGGED`` (10) newly retracted entries. It never fails the
build: the label is a flag for the reviewer, not a gate.

This is a build-side step (after the merge) rather than a sweep-log field
because only the merge knows which ENTRIES a rejected CVE retracts (an entry
retracts only when every CVE on it is rejected and it has no other evidence);
the sweep sees CVE states, not entries.

    python scripts/newly_retracted_report.py [--before-ref HEAD] \
        [--after data/incidents.json] [--out-md FILE] [--github-output FILE]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_UNFLAGGED = 10


def newly_retracted(before: dict, after: dict) -> list[dict]:
    """Pure. Entries retracted in *after* and not retracted in *before*."""
    b = {e["id"]: e for e in before.get("incidents", [])}
    out = []
    for e in after.get("incidents", []):
        if e.get("status") == "retracted" and b.get(e["id"], {}).get("status") != "retracted":
            out.append({"id": e["id"], "cve_ids": list(e.get("cve_ids") or []),
                        "tier": e.get("tier"), "rejected_cve_ids": list(e.get("rejected_cve_ids") or [])})
    return sorted(out, key=lambda r: r["id"])


def decide(rows: list[dict]) -> tuple[bool, list[str]]:
    reasons = []
    land = [r["id"] for r in rows if r["tier"] == "landmark"]
    if land:
        reasons.append(f"{len(land)} newly retracted landmark entr{'y' if len(land) == 1 else 'ies'}: {', '.join(land)}")
    if len(rows) > MAX_UNFLAGGED:
        reasons.append(f"{len(rows)} newly retracted entries (more than {MAX_UNFLAGGED})")
    return bool(reasons), reasons


def render_md(rows: list[dict], needs: bool, reasons: list[str]) -> str:
    L = ["### Newly retracted entries (CVE rejection sweep)", ""]
    if not rows:
        return "\n".join(L + ["None: no entry is retracted in this build that is not already retracted on `main`.", ""])
    L += [f"{len(rows)} entr{'y is' if len(rows) == 1 else 'ies are'} retracted in this build and not on `main` "
          "(status `retracted`; nothing is deleted, the IDs still resolve). This is a flag, not a gate: the refresh was not blocked.", ""]
    if needs:
        L += ["**Needs a ruling** (label `needs-ruling`): " + "; ".join(reasons) + ".", ""]
    L += ["| entry | CVE id(s) | tier |", "|---|---|---|"]
    L += [f"| {r['id']} | {', '.join(r['cve_ids']) or '-'} | {r['tier']} |" for r in rows]
    return "\n".join(L + [""])


def _git_show(ref: str) -> dict:
    p = subprocess.run(["git", "show", f"{ref}:data/incidents.json"], cwd=ROOT, capture_output=True, check=True)
    return json.loads(p.stdout.decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="HEAD")
    ap.add_argument("--after", default=str(ROOT / "data" / "incidents.json"))
    ap.add_argument("--out-md")
    ap.add_argument("--github-output")
    a = ap.parse_args()
    rows = newly_retracted(_git_show(a.before_ref), json.loads(Path(a.after).read_text(encoding="utf-8")))
    needs, reasons = decide(rows)
    md = render_md(rows, needs, reasons)
    if a.out_md:
        Path(a.out_md).write_text(md, encoding="utf-8", newline="\n")
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"count={len(rows)}\nneeds_ruling={'true' if needs else 'false'}\n")
    print(md)
    print(f"[newly-retracted] {len(rows)} newly retracted; needs-ruling={needs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
