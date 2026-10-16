#!/usr/bin/env python
"""D130-2 field-level before/after delta: base 589376db vs the working tree's data/incidents.json.

  python -I delta.py [--json out.json] [--md out.md]

Per entity (every id present in either side) every top-level field that differs is listed with
before/after; ids outside the 23 targeted rows must show NO difference (any such row is printed as
UNINTENDED and the exit code is 1). Also compares entry count, id set and the envelope.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import d1302_spec as S  # noqa: E402

BASE = "589376db"
EXPECTED_FIXED = set(S.FIXED)
EXPECTED_UNV = set(S.UNVERIFIED)
TARGET = EXPECTED_FIXED | EXPECTED_UNV


def load_base():
    raw = subprocess.run(["git", "show", f"{BASE}:data/incidents.json"], cwd=REPO, check=True, capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    b = load_base()
    a = json.loads((REPO / "data" / "incidents.json").read_text(encoding="utf-8"))
    bi = {e["id"]: e for e in b["incidents"]}
    ai = {e["id"]: e for e in a["incidents"]}
    out = {"base": BASE, "entry_count": [len(bi), len(ai)], "id_set_equal": set(bi) == set(ai),
           "ids_only_in_base": sorted(set(bi) - set(ai)), "ids_only_in_new": sorted(set(ai) - set(bi)),
           "envelope": {}, "rows": {}, "unintended": []}
    for k in sorted(set(b) | set(a)):
        if k != "incidents" and b.get(k) != a.get(k):
            out["envelope"][k] = [b.get(k), a.get(k)]
    for rid in sorted(set(bi) & set(ai)):
        x, y = bi[rid], ai[rid]
        diff = {f: [x.get(f), y.get(f)] for f in sorted(set(x) | set(y)) if x.get(f) != y.get(f)}
        if diff:
            out["rows"][rid] = diff
            if rid not in TARGET:
                out["unintended"].append(rid)
    sb = json.loads(subprocess.run(["git", "show", f"{BASE}:data/stats.json"], cwd=REPO, check=True, capture_output=True).stdout.decode("utf-8"))
    sa = json.loads((REPO / "data" / "stats.json").read_text(encoding="utf-8"))
    out["stats"] = {k: [sb.get(k), sa.get(k)] for k in sorted(set(sb) | set(sa)) if sb.get(k) != sa.get(k)}
    expected_stats = {"generated", "incident_count", "unverified_count", "landmark_count"}
    out["unintended_stats"] = sorted(set(out["stats"]) - expected_stats)
    text = json.dumps(out, indent=1, ensure_ascii=False)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(text + "\n", encoding="utf-8", newline="\n")
    print("entries", out["entry_count"], "id_set_equal", out["id_set_equal"], "rows changed", len(out["rows"]),
          "unintended", out["unintended"], "stats", {k: v for k, v in out["stats"].items() if not isinstance(v[0], (dict, list))},
          "unintended_stats", out["unintended_stats"])
    print("envelope", {k: v for k, v in out["envelope"].items()})
    fields = {}
    for rid, d in out["rows"].items():
        for f in d:
            fields.setdefault(f, []).append(rid)
    for f, ids in sorted(fields.items()):
        print(f, len(ids))
    return 1 if out["unintended"] or out["unintended_stats"] or not out["id_set_equal"] else 0


if __name__ == "__main__":
    sys.exit(main())
