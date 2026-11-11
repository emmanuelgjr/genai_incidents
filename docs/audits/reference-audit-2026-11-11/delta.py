#!/usr/bin/env python
"""D130-3a field-level before/after delta: control = base 64109452's committed data, new = the working tree.

  python -I delta.py [--json out.json]

Per entity (every id in either side) every top-level field that differs is listed with before/after. Each row has a DECLARED
set of fields allowed to move; any other moved field, any row outside the 38 targets that moved, any stats key outside the
declared set, or an ID-set / entry-count change is UNINTENDED and makes the exit code 1.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import d1303a_spec as S  # noqa: E402

DERIVED = {"updated", "last_seen"}                 # history stamps: content changed
KNOCKON = {"confidence", "tier"}                   # derived from quality_tier by _derive_confidence / _derive_tier


def allowed(rid):
    if rid in S.UNVERIFIED:
        return DERIVED | {"status", "status_reason"}
    f = DERIVED | KNOCKON | {"quality_tier", "references"}
    if rid in S.REPLACE:
        f |= {k for k in ("title", "description", "affected") if S.REPLACE[rid].get(k)}
    if rid == "INC-04207" or rid in ("INC-02471", "INC-02871"):
        f |= {"discovery_method"}
    return f


def git_json(path):
    return json.loads(subprocess.run(["git", "show", f"{S.BASE}:{path}"], cwd=REPO, check=True, capture_output=True).stdout.decode("utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    b = git_json("data/incidents.json")
    a = json.loads((REPO / "data" / "incidents.json").read_text(encoding="utf-8"))
    bi = {e["id"]: e for e in b["incidents"]}
    ai = {e["id"]: e for e in a["incidents"]}
    targets = set(S.REMOVE) | set(S.REPLACE) | set(S.UNVERIFIED)
    out = {"base": S.BASE, "entry_count": [len(bi), len(ai)], "id_set_equal": set(bi) == set(ai),
           "id_order_equal": [e["id"] for e in b["incidents"]] == [e["id"] for e in a["incidents"]],
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
            if rid not in targets or set(diff) - allowed(rid):
                out["unintended"].append([rid, sorted(set(diff) - allowed(rid))] if rid in targets else [rid, "not a target"])
    for rid in targets:
        if rid not in out["rows"]:
            out["unintended"].append([rid, "target row did not change"])
    sb, sa = git_json("data/stats.json"), json.loads((REPO / "data" / "stats.json").read_text(encoding="utf-8"))
    out["stats"] = {k: [sb.get(k), sa.get(k)] for k in sorted(set(sb) | set(sa)) if sb.get(k) != sa.get(k)}
    declared = {"generated", "incident_count", "unverified_count", "landmark_count"}
    out["unintended_stats"] = sorted(set(out["stats"]) - declared)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                                 encoding="utf-8", newline="\n")
    print("entries", out["entry_count"], "id_set_equal", out["id_set_equal"], "id_order_equal", out["id_order_equal"],
          "rows changed", len(out["rows"]), "unintended", out["unintended"], "unintended_stats", out["unintended_stats"])
    print("envelope", out["envelope"])
    print("stats", {k: v for k, v in out["stats"].items() if not isinstance(v[0], (dict, list))})
    fields = {}
    for rid, d in out["rows"].items():
        for f in d:
            fields.setdefault(f, []).append(rid)
    for f, ids in sorted(fields.items()):
        print(f, len(ids))
    bad = out["unintended"] or out["unintended_stats"] or not out["id_set_equal"] or not out["id_order_equal"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
