#!/usr/bin/env python
"""Write the D130-3a entries into data/curation_overrides.json (the durable curation input).

  python -I build_overrides.py            # (re)write; idempotent
  python -I build_overrides.py --check    # exit 1 if the file would change

Computed from the BASE rows and the BASE overrides file (git show 64109452:...), so re-running is idempotent and does not
depend on a previous run. apply_curation_overrides applies only the FIRST key of a row that has an entry (in the row's
source_ids order), so a row that already has an entry reuses that key; otherwise the first source_id is used.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import d1303a_spec as S  # noqa: E402

OV = REPO / "data" / "curation_overrides.json"


def show(path):
    return subprocess.run(["git", "show", f"{S.BASE}:{path}"], cwd=REPO, check=True, capture_output=True).stdout.decode("utf-8")


def key_for(row, ov):
    for s in row["source_ids"]:
        if s in ov:
            return s, True
    return row["source_ids"][0], False


def build():
    rows = {e["id"]: e for e in json.loads(show("data/incidents.json"))["incidents"]}
    doc = json.loads(show("data/curation_overrides.json"))
    ov = doc["overrides"]

    for rid, urls in S.REMOVE.items():
        row = rows[rid]
        key, existing = key_for(row, ov)
        entry = dict(ov.get(key, {}))
        assert "references" not in entry and "references_remove" not in entry, rid
        have = {r["url"] for r in row["references"]}
        assert set(urls) <= have, (rid, set(urls) - have)
        assert len(row["references"]) > len(urls), rid
        note = (f"{S.NOTE_PREFIX} Removed reference(s): {', '.join(urls)}. quality_tier demoted to auto (never promoted). "
                "Evidence: docs/audits/reference-audit-2026-11-11/.")
        if "discovery_method" in entry:
            # D139(b): discovery_method is a landmark-only field (integrity check). The row leaves the landmark tier
            # when demoted (curated -> auto, no aiid_id, corpus not ai-harm), so the override line that supplies the
            # value is dropped; its text is kept in _d130_3a_prior_note.
            assert row["quality_tier"] == "curated" and not row.get("aiid_id") and row.get("corpus") != "ai-harm", rid
            dm = entry.pop("discovery_method")
            ruling = ("(D139(b))" if rid == "INC-04207" else
                      "(same mechanism as D139(b), which named only INC-04207; not separately ruled -- validate.py rejects "
                      "discovery_method outside the landmark tier; flagged for user re-review)")
            entry["_d130_3a_prior_note"] = f"dropped discovery_method={dm!r} {ruling}; the line's note read: " + entry.pop("_note")
            entry["_note"] = note
        else:
            entry["_d130_3a_note" if existing else "_note"] = note
        entry["quality_tier"] = "auto"
        entry["references_remove"] = list(urls)
        ov[key] = entry
    for rid, sp in S.REPLACE.items():
        row = rows[rid]
        key, existing = key_for(row, ov)
        assert not existing, rid
        assert [r["url"] for r in row["references"]] == [sp["old"]], rid
        entry = {"quality_tier": "auto", "references": [dict(sp["ref"])]}
        for f in ("title", "description", "affected"):
            if sp.get(f):
                entry[f] = sp[f]
        entry["_note"] = (f"{S.NOTE_PREFIX} Replaced reference: {sp['old']}. quality_tier demoted to auto (never promoted). "
                          "Evidence: docs/audits/reference-audit-2026-11-11/.")
        ov[key] = entry
    for rid, effort in S.UNVERIFIED.items():
        row = rows[rid]
        key, existing = key_for(row, ov)
        assert not existing, rid
        ov[key] = {"status": "unverified", "status_reason": {"code": "no-confirmed-source", "as_of": S.AS_OF},
                   "_note": ("D130-3a: no confirmed source names this incident after a documented effort "
                             "(agent-suggested; pending user re-review); references left as found, quality_tier untouched. "
                             "Effort: " + " ".join(effort))}
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    out = build()
    cur = OV.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        sys.exit(0 if out == cur else 1)
    OV.write_text(out, encoding="utf-8", newline="\n")
    print("wrote", OV, "changed" if out != cur else "unchanged")
