#!/usr/bin/env python
"""Field-level delta (working agreement 2): BASE 05ff1e75 vs the working tree's build output.

  python docs/audits/relabel-d130-2l-2026-10-16/delta.py          # summary to stdout
  python docs/audits/relabel-d130-2l-2026-10-16/delta.py --json   # also write delta-2026-10-16.json here

Compares EVERY field of EVERY row (ID-set, entry count, envelope, data/stats.json), not only the fields this
task meant to move; exits 1 if any row outside the 11 changed or any changed field is not declared below.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import relabel_spec as S  # noqa: E402

DECLARED = {"category", "attack_vector", "severity", "owasp_llm", "owasp_asi", "owasp_dsgai", "nist_ai_rmf",
            "mitre_atlas", "mitre_atlas_tactics", "tags", "maestro_layers", "updated", "last_seen"}


def load(rev, path):
    if rev is None:
        return json.loads((REPO / path).read_text(encoding="utf-8"))
    raw = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO, check=True, capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def main():
    b, a = load(S.BASE, "data/incidents.json"), load(None, "data/incidents.json")
    B, A = {e["id"]: e for e in b["incidents"]}, {e["id"]: e for e in a["incidents"]}
    out = {"base": S.BASE, "entry_count": [len(B), len(A)], "id_set_equal": set(B) == set(A),
           "envelope": {k: [b.get(k), a.get(k)] for k in sorted(set(b) | set(a)) if k != "incidents" and b.get(k) != a.get(k)},
           "rows": {}}
    for rid in sorted(set(B) | set(A)):
        eb, ea = B.get(rid, {}), A.get(rid, {})
        d = {k: [eb.get(k), ea.get(k)] for k in sorted(set(eb) | set(ea)) if eb.get(k) != ea.get(k)}
        if d:
            out["rows"][rid] = d
    sb, sa = load(S.BASE, "data/stats.json"), load(None, "data/stats.json")
    out["stats_changed"] = {k: [sb.get(k), sa.get(k)] for k in sorted(set(sb) | set(sa)) if sb.get(k) != sa.get(k)}
    outside = sorted(set(out["rows"]) - set(S.ROWS))
    fields = {}
    for rid, d in out["rows"].items():
        for k in d:
            fields.setdefault(k, []).append(rid)
    undeclared = sorted(set(fields) - DECLARED)
    print(f"entries {out['entry_count'][0]} -> {out['entry_count'][1]}; ID set equal: {out['id_set_equal']}")
    print(f"envelope changes: {out['envelope'] or 'none'}")
    print(f"stats.json changes: {out['stats_changed'] or 'none'}")
    print(f"rows with any difference: {len(out['rows'])}; outside the 11: {len(outside)} {outside}")
    for k in sorted(fields):
        print(f"  {k}: {len(fields[k])} row(s) {' '.join(fields[k])}")
    print(f"undeclared fields: {undeclared or 'none'}")
    if "--json" in sys.argv:
        (HERE / "delta-2026-10-16.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8", newline="\n")
    return 1 if (outside or undeclared or not out["id_set_equal"]) else 0


if __name__ == "__main__":
    sys.exit(main())
