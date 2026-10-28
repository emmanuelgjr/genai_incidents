"""Write ``data/last_release.json`` for a cut (see scripts/release_label.py).

Usage: python scripts/mark_release.py --tag v2.13.0 [--date YYYY-MM-DD] [--rev HEAD]
Reads the TAGGED ``data/incidents.json`` via ``git show`` (local, offline) and the
release date from the matching CHANGELOG heading unless --date is given. Run at
every cut, then ``make build`` so stats.json drops the ``+main`` suffix. Not part
of the build path.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from release_label import MARKER_PATH, ROOT, derive_counts, rows_digest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--date")
    ap.add_argument("--rev", help="git rev to read data/incidents.json from "
                    "(default: the tag; use HEAD at step 3 of the cut, before the tag exists)")
    a = ap.parse_args()
    version = a.tag.removeprefix("v")
    raw = subprocess.check_output(["git", "show", f"{a.rev or a.tag + '^{}'}:data/incidents.json"], cwd=ROOT)
    data = json.loads(raw.decode("utf-8"))
    if data["version"] != version:
        sys.exit(f"tag {a.tag} data/incidents.json says version {data['version']!r}")
    date = a.date
    if not date:
        m = re.search(rf"^##\s+\[{re.escape(version)}\]\s*[—–-]+\s*(\d{{4}}-\d{{2}}-\d{{2}})",
                      (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.MULTILINE)
        if not m:
            sys.exit(f"no CHANGELOG heading for {version}; pass --date")
        date = m.group(1)
    rows = data["incidents"]
    marker = {"version": version, "released": date, "tag": a.tag,
              "rows_sha256": rows_digest(rows), **derive_counts(rows)}
    MARKER_PATH.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[mark-release] {MARKER_PATH.name}: {marker}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
