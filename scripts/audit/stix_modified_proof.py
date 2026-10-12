"""Real-corpus proof of the STIX `modified` rule (read-only; writes nothing).

    python -X utf8 scripts/audit/stix_modified_proof.py

See docs/audits/ws6-v2130-export-integrity-2026-10-11.md section 1.2."""
import copy, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import export_stix as s

rows = [e for e in json.load(open(ROOT / "data" / "incidents.json", encoding="utf-8"))["incidents"] if e.get("status") != "retracted"]


def h(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:12]


def per_obj(bundle):
    return {o["id"]: h(o) for o in bundle["objects"]}


b1 = s.build_bundle(rows)
b2 = s.build_bundle(copy.deepcopy(rows))
print("build A == build B, whole bundle:", json.dumps(b1, sort_keys=True) == json.dumps(b2, sort_keys=True), f"({len(b1['objects'])} objects)")

# content change on ONE entry, the way the merge records it: content edit + updated bump
tgt = next(e for e in rows if e["id"] == "INC-02800")
rows2 = copy.deepcopy(rows)
t2 = next(e for e in rows2 if e["id"] == "INC-02800")
t2["description"] += " (corrected)"
t2["updated"] = "2026-10-12"
b3 = s.build_bundle(rows2)
p1, p3 = per_obj(b1), per_obj(b3)
changed = sorted(i for i in p1 if p1[i] != p3.get(i))
byid = {o["id"]: o for o in b3["objects"]}
byid1 = {o["id"]: o for o in b1["objects"]}
print("objects whose bytes changed after editing INC-02800:", len(changed))
for i in changed:
    print("  ", byid1[i]["type"], i[-12:], byid1[i]["modified"], "->", byid[i]["modified"])
others = [i for i in p1 if i not in set(changed)]
print("all other objects byte-identical:", all(p1[i] == p3[i] for i in others), f"({len(others)} objects)")
print("identity moved (dataset-level, expected):", [byid1[i]["type"] for i in changed if byid1[i]["type"] == "identity"])

# no `updated` bump (content edited but merge did not bump) -> modified does not move: the documented dependency
rows3 = copy.deepcopy(rows)
next(e for e in rows3 if e["id"] == "INC-02800")["description"] += " (silent)"
b4 = s.build_bundle(rows3)
sd = lambda b: next(o for o in b["objects"] if o.get("x_incident_id") == "INC-02800")
print("description edited WITHOUT updated bump -> modified unchanged:", sd(b1)["modified"] == sd(b4)["modified"], "(this is why merge's _CONTENT_FIELDS is the contract)")

# exporter version bump
s.EXPORTER_VERSION += 1
b5 = s.build_bundle(rows)
moved = sum(1 for a, b in zip(b1["objects"], b5["objects"]) if a["modified"] != b["modified"])
rest = all({k: v for k, v in a.items() if k != "modified"} == {k: v for k, v in b.items() if k != "modified"} for a, b in zip(b1["objects"], b5["objects"]))
print(f"EXPORTER_VERSION+1: modified moved on {moved}/{len(b1['objects'])} objects, every other field identical: {rest}")
