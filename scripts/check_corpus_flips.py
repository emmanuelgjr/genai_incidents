#!/usr/bin/env python3
"""Per-entity undeclared corpus-flip check for the refresh PR (D156a).

Motivation: refresh PR #110 flipped INC-07572 ai-harm -> security through an
upstream text edit (the `rce` substring inside "enforcement") and nothing flagged
it until a manual per-row review.

Compares data/incidents.json at a base ref against the rebuilt tree PER ENTITY and
lists every row present at BOTH whose `corpus` changed. A flip is DECLARED when the
D120 report (scripts/aiid_change_report.py --out-json) lists it in its `corpus`
table with the same before/after values; every other flip is UNDECLARED. D120 only
covers rows carrying an `AIID-` source id, so every flip on a non-AIID row
(AIAAIC, OECD-only, legacy, AVID...) is undeclared by construction.

Rows present at only one side (added / removed) are not flips: they are counted and
printed but never reported as flips. (Additions and removals are covered by the
D120 report's row counts and by the retraction report.)

Flags, never blocks (D120 posture): the workflow turns exit 1 into needs-ruling.
Exit 0 = no undeclared flip; 1 = at least one undeclared flip; 2 = the check could
not run (bad/missing D120 JSON, unreadable base). Read-only: writes only --out-md.
No network, no model call.

    python scripts/check_corpus_flips.py --declared-json FILE [--before-ref HEAD]
        [--after data/incidents.json] [--out-md FILE]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


MAX_ROWS = 100


class CheckError(Exception):
    pass


def _sources(e: dict) -> str:
    return ", ".join(str(s) for s in (e.get("source_ids") or [])) or "-"


def load_declared_obj(d) -> dict[str, tuple]:
    """Pure. id -> (before, after) from a parsed D120 sidecar."""
    try:
        rows = d["listed"]["corpus"]
        if d.get("schema") != 1 or not isinstance(rows, list):
            raise ValueError("unexpected schema")
        return {r["id"]: (r["before"], r["after"]) for r in rows}
    except (AttributeError, ValueError, KeyError, TypeError) as ex:
        raise CheckError(f"D120 sidecar unusable: {type(ex).__name__}: {ex}") from ex


def load_declared(path: str) -> dict[str, tuple]:
    """Declared flips from the D120 sidecar file. A missing/malformed sidecar raises
    CheckError; it must never read as 'no declared flips' silently."""
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        raise CheckError(f"D120 sidecar {path} unreadable: {type(ex).__name__}") from ex
    return load_declared_obj(d)


def compare(before: dict, after: dict, declared: dict[str, tuple]) -> dict:
    """Pure. Per-entity flip comparison."""
    b = {e["id"]: e for e in before.get("incidents", [])}
    a = {e["id"]: e for e in after.get("incidents", [])}
    flips = []
    for iid in sorted(set(a) & set(b)):
        old, new = b[iid].get("corpus"), a[iid].get("corpus")
        if old == new:
            continue
        # declared only if D120 listed it AND agrees on the before/after values
        ok = declared.get(iid) == (old, new)
        flips.append({"id": iid, "before": old, "after": new, "declared": ok,
                      "sources": _sources(a[iid])})
    return {"flips": flips, "undeclared": [f for f in flips if not f["declared"]],
            "added": len(set(a) - set(b)), "removed": len(set(b) - set(a))}


def render_md(r: dict, ref: str) -> str:
    n, bad = len(r["flips"]), r["undeclared"]
    if not bad:
        return (f"Corpus flips: {n}, all declared in the D120 report "
                f"(rows added {r['added']} / removed {r['removed']} are not flips and are not checked here).\n")
    L = ["### Undeclared corpus flips (D156a)", "",
         f"**{len(bad)} existing row(s) changed `corpus` relative to `{ref}` without being declared in the D120 "
         f"report** (of {n} flip(s) total). Per-entity check; the PR is labelled `needs-ruling`. The refresh was not "
         "blocked. Review each row's title/description change before merging "
         "(PR #110's INC-07572 flipped through an upstream text edit).", "",
         "| entry | before | after | source ids |", "|---|---|---|---|"]
    L += [f"| {f['id']} | {f['before']} | {f['after']} | {f['sources'].replace('|', '/')} |"
          for f in bad[:MAX_ROWS]]
    if len(bad) > MAX_ROWS:  # keep the PR body bounded (D123); the exact list is in the step summary / logs
        L += [f"| ... {len(bad) - MAX_ROWS} more undeclared flips (compare `corpus` against `{ref}`) | | | |"]
    L += ["", f"Declared flips: {n - len(bad)}. Rows added {r['added']} / removed {r['removed']} are not flips "
          "and are not checked here.", ""]
    return "\n".join(L)


def _git_show(ref: str) -> dict:
    try:
        p = subprocess.run(["git", "show", f"{ref}:data/incidents.json"], cwd=ROOT, capture_output=True, check=True)
        return json.loads(p.stdout.decode("utf-8"))
    except (subprocess.CalledProcessError, ValueError, OSError) as ex:
        raise CheckError(f"cannot read data/incidents.json at {ref}: {type(ex).__name__}") from ex


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="HEAD")
    ap.add_argument("--after", default=str(ROOT / "data" / "incidents.json"))
    ap.add_argument("--declared-json", required=True, help="sidecar from aiid_change_report.py --out-json")
    ap.add_argument("--out-md")
    a = ap.parse_args(argv)
    try:
        declared = load_declared(a.declared_json)
        try:
            after = json.loads(Path(a.after).read_text(encoding="utf-8"))
        except (OSError, ValueError) as ex:
            raise CheckError(f"cannot read {a.after}: {type(ex).__name__}") from ex
        r = compare(_git_show(a.before_ref), after, declared)
    except CheckError as ex:
        print(f"[corpus-flips] ERROR: {ex}", file=sys.stderr)
        return 2
    md = render_md(r, a.before_ref)
    if a.out_md:
        Path(a.out_md).write_text(md, encoding="utf-8", newline="\n")
    print(md)
    print(f"[corpus-flips] flips={len(r['flips'])} undeclared={len(r['undeclared'])} "
          f"added={r['added']} removed={r['removed']}")
    return 1 if r["undeclared"] else 0


if __name__ == "__main__":
    sys.exit(main())
