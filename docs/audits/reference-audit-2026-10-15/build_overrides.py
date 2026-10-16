#!/usr/bin/env python
"""Write the D130-2 entries into data/curation_overrides.json (the durable curation input).

  python -I build_overrides.py            # (re)write; idempotent
  python -I build_overrides.py --check    # exit 1 if the file would change

The output is computed from the BASE rows AND the BASE overrides file (so re-running is idempotent). New references are computed from the BASE rows (git show 589376db:data/incidents.json), never
from the current build output, so the result does not depend on a previous run of this script.
Existing keys keep their content; D130-2 fields are added alongside (apply_curation_overrides
applies only the FIRST matching key of a row, so a row that already has an entry reuses its key).
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import d1302_spec as S  # noqa: E402

BASE = "589376db"
OV = REPO / "data" / "curation_overrides.json"


def base_rows():
    raw = subprocess.run(["git", "show", f"{BASE}:data/incidents.json"], cwd=REPO, check=True,
                         capture_output=True).stdout.decode("utf-8")
    return {e["id"]: e for e in json.loads(raw)["incidents"]}


def build():
    rows = base_rows()
    doc = json.loads(subprocess.run(["git", "show", f"{BASE}:data/curation_overrides.json"], cwd=REPO, check=True,
                                    capture_output=True).stdout.decode("utf-8"))
    ov = doc["overrides"]
    for rid, spec in S.FIXED.items():
        row = rows[rid]
        assert spec["key"] in row["source_ids"], (rid, spec["key"])
        refs, seen = [], set()
        for r in row["references"]:
            if r["url"] in spec["replace"]:
                for nu in spec["replace"][r["url"]]:
                    if nu not in seen:
                        refs.append(dict(S.NEW_REFS[nu])); seen.add(nu)
            else:
                refs.append(dict(r))
        assert {u for u in spec["replace"]} <= {r["url"] for r in row["references"]}, rid
        assert refs, rid
        entry = ov.get(spec["key"], {})
        existing = bool(entry)
        entry = dict(entry)
        entry["quality_tier"] = "auto"
        entry["references"] = refs
        for f in ("title", "description", "impact", "affected"):
            if spec.get(f):
                entry[f] = spec[f]
        for f, v in spec.get("pin", {}).items():
            entry[f] = v
        removed = ", ".join(u for u in spec["replace"])
        note = (f"{S.NOTE_PREFIX} Replaced/removed reference(s): {removed}. "
                "quality_tier demoted to auto (never promoted). Evidence: docs/audits/reference-audit-2026-10-15/.")
        entry["_d130_2_note" if existing else "_note"] = note
        ov[spec["key"]] = entry
    for rid, spec in S.UNVERIFIED.items():
        row = rows[rid]
        assert spec["key"] in row["source_ids"], (rid, spec["key"])
        entry = dict(ov.get(spec["key"], {}))
        existing = bool(entry)
        entry["status"] = "unverified"
        entry["status_reason"] = {"code": "no-confirmed-source", "as_of": S.AS_OF}
        note = ("D130-2: no confirmed source names this incident after a documented effort "
                "(agent-suggested; pending user re-review); references left as found, quality_tier untouched. "
                "Effort: " + " ".join(spec["effort"]))
        entry["_d130_2_note" if existing else "_note"] = note
        ov[spec["key"]] = entry
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    out = build()
    cur = OV.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        sys.exit(0 if out == cur else 1)
    OV.write_text(out, encoding="utf-8", newline="\n")
    print("wrote", OV, "changed" if out != cur else "unchanged")
