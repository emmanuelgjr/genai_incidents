"""D63 overdue-review alert: decide whether the weekly data refresh is overdue.

"Overdue" = no `Weekly data refresh` PR (head `auto-refresh/data`) has been
MERGED within --max-age-days. Merged, not opened: the refresh workflow can run
green every Sunday and open a PR nobody reviews, and the alert exists to catch
exactly that, as well as a workflow that has stopped producing PRs at all
(which is what 2026-07-19 -> 2026-10-13 looked like).

Pure decision logic: the workflow (.github/workflows/refresh-overdue-alert.yml)
fetches the PR lists with `gh` and pipes them in, so this script makes no
network call. Input (stdin or --input): {"merged": [{number, mergedAt, title}],
"open": [{number, createdAt, title}]}. Exit 0 = on time, 3 = overdue. Writes
`overdue=true|false` and `age_days` to $GITHUB_OUTPUT when set.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def evaluate(doc: dict, now: datetime, max_age_days: float) -> dict:
    merged = [p for p in doc.get("merged") or [] if p.get("mergedAt")]
    last = max(merged, key=lambda p: _ts(p["mergedAt"]), default=None)
    age = (now - _ts(last["mergedAt"])).total_seconds() / 86400 if last else None
    overdue = last is None or age > max_age_days
    return {
        "overdue": overdue,
        "age_days": None if age is None else round(age, 1),
        "last_merged": last,
        "open": list(doc.get("open") or []),
        "max_age_days": max_age_days,
    }


def render(r: dict) -> str:
    if r["last_merged"]:
        last = (f"#{r['last_merged']['number']} merged {r['last_merged']['mergedAt']} "
                f"({r['age_days']} days ago)")
    else:
        last = "none found"
    lines = [
        "### Weekly data refresh is overdue" if r["overdue"] else "### Weekly data refresh is on time",
        "",
        f"- Threshold: no merged `Weekly data refresh` PR in {r['max_age_days']:g} days",
        f"- Last merged refresh PR: {last}",
    ]
    if r["open"]:
        lines.append("- Open refresh PR(s) awaiting review: " + ", ".join(f"#{p['number']}" for p in r["open"]))
    else:
        lines.append("- No open refresh PR: the workflow is not producing one. Check the "
                     "`Weekly auto-refresh` runs.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-age-days", type=float, default=21)
    ap.add_argument("--input", default="-")
    ap.add_argument("--now", help="ISO timestamp override (tests)")
    ap.add_argument("--out-md")
    args = ap.parse_args(argv)
    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    now = _ts(args.now) if args.now else datetime.now(timezone.utc)
    r = evaluate(json.loads(raw), now, args.max_age_days)
    md = render(r)
    print(md)
    if args.out_md:
        open(args.out_md, "w", encoding="utf-8").write(md)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as f:
            f.write(f"overdue={'true' if r['overdue'] else 'false'}\nage_days={r['age_days']}\n")
    return 3 if r["overdue"] else 0


if __name__ == "__main__":
    sys.exit(main())
