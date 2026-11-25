"""D155 offline delta estimate (read-only, no network, writes nothing).

The committed ingest/aiid_full.json stores a TEMPLATED description, not AIID's
text (licence rule), so the classifier's real input (title + AIID description)
is not recoverable offline. Only the TITLE is. This script therefore reports
rows whose TITLE contains `rce` only inside a longer word and no whole-word
rce / remote-code / command-injection / sandbox-escape term. For those rows the
fix removes the rce-rule contribution UNLESS AIID's (unseen) description has a
whole-word match. Output is the per-field candidate ID lists.
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REAL = re.compile(r"\brce\b|remote code|command injection|sandbox escape")
EMB = re.compile(r"rce")
rows = json.loads((ROOT / "ingest" / "aiid_full.json").read_text(encoding="utf-8"))
out = {"n": len(rows), "rce_rows": 0, "title_proven": [], "undecidable_by_title": [],
       "real_in_title": [], "ransom_only_in_title": [], "sev_high_title_proven": [], "contrib_only_nonrce_av": []}
for r in rows:
    t = r["title"].lower()
    is_rce = r["attack_vector"] == "rce"
    emb_only = bool(EMB.search(t)) and not REAL.search(t)
    if is_rce:
        out["rce_rows"] += 1
        if REAL.search(t):
            out["real_in_title"].append(r["source_id"])
        elif "ransom" in t:
            out["ransom_only_in_title"].append(r["source_id"])  # `ransom` rule also sets attack_vector=rce; unaffected by D155
        elif emb_only:
            out["title_proven"].append(r["source_id"])
        else:
            out["undecidable_by_title"].append(r["source_id"])
    elif emb_only:
        out["contrib_only_nonrce_av"].append(
            (r["source_id"], r["owasp_llm"], r["owasp_asi"], r["mitre_atlas"], r["severity"]))
    if emb_only and r["severity"] == "High":
        out["sev_high_title_proven"].append(r["source_id"])
json.dump(out, sys.stdout, indent=1)
