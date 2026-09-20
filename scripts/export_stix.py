"""
Export the incident dataset as a STIX 2.1 bundle for ingestion into threat-
intelligence platforms (OpenCTI, MISP-STIX, TAXII servers, etc.).

Output: data/incidents.stix.json (+ mirrored into docs/data/ for download).

Modelling:
  - each incident -> a custom `x-genai-incident` SDO carrying the full
    taxonomy mapping as `x_*` properties + external_references;
  - each distinct MITRE ATLAS technique -> an `attack-pattern` SDO;
  - each distinct CVE -> a `vulnerability` SDO;
  - `relationship` SDOs link incidents to the techniques/CVEs they involve.

All STIX ids are derived deterministically (UUIDv5 over a fixed namespace),
and object timestamps come from each incident's `added`/`updated` dates — so
the bundle is byte-stable across rebuilds and safe for the CI drift check.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS_DATA = ROOT / "docs" / "data"
MAPPINGS = ROOT / "mappings"

# Fixed namespace so UUIDv5 ids are stable across runs and machines.
NS = uuid.UUID("6f1a9c4e-9b2d-5e7a-8c3f-0a1b2c3d4e5f")
# Constant timestamp for taxonomy objects (techniques/CVEs) that have no own date.
EPOCH = "2024-01-01T00:00:00.000Z"

ATLAS_URL = "https://atlas.mitre.org/techniques/"
OWASP_LLM_URL = "https://genai.owasp.org/llmrisk/"


def _content_license(i: dict) -> dict | None:
    """Row-level license-obligation marker for `x_content_license` (D14,
    retired to this form by D15). Emits the entry's own `content_license`
    object verbatim -- authoritative since the WS0-T3 Phase B rebuild
    populated it on every AIAAIC-derived entry (sheet-derived and the 95
    hand-curated rows alike, E16/D18). The interim pre-rebuild fallback
    (`source_ids`/`tags` substring heuristic) is retired: measured on the
    2026-07-29 corpus its output was exact-equal to this field on all 1,517
    affected rows -- zero divergence in either direction -- so retirement is
    a provable no-op, per D15's directional criterion (zero under-
    attribution required; over-attribution merely adds caution). See D15
    (PROGRESS.md) for why no fallback is kept: a heuristic left in place
    would silently mask any future gap between this field and the rows it
    should cover, rather than surfacing it. Returns None when the field is
    absent -- the row carries no known obligation.
    """
    return i.get("content_license")


def _sid(prefix: str, *parts: str) -> str:
    return f"{prefix}--{uuid.uuid5(NS, prefix + '|' + '|'.join(parts))}"


def _ts(date_str: str) -> str:
    """A YYYY-MM-DD / YYYY-MM / YYYY date -> RFC3339 timestamp (UTC midnight)."""
    s = (date_str or "").strip()
    if len(s) == 4:
        s += "-01-01"
    elif len(s) == 7:
        s += "-01"
    if len(s) != 10:
        s = "2024-01-01"
    return f"{s}T00:00:00.000Z"


def _atlas_names() -> dict[str, str]:
    try:
        m = json.loads((MAPPINGS / "mitre_atlas.json").read_text(encoding="utf-8"))
        return {k: v.get("name", k) for k, v in (m.get("techniques") or {}).items()}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def build_bundle(incidents: list[dict]) -> dict:
    atlas_names = _atlas_names()
    objects: list[dict] = []
    technique_ids: dict[str, str] = {}
    cve_ids: dict[str, str] = {}

    # 1) Shared taxonomy SDOs: ATLAS techniques + CVEs.
    techniques = sorted({t for i in incidents for t in (i.get("mitre_atlas") or [])})
    for t in techniques:
        oid = _sid("attack-pattern", t)
        technique_ids[t] = oid
        base = t.split(".")[0]  # AML.T0051.000 -> AML.T0051 for the URL
        objects.append({
            "type": "attack-pattern", "spec_version": "2.1", "id": oid,
            "created": EPOCH, "modified": EPOCH,
            "name": atlas_names.get(t) or atlas_names.get(base) or t,
            "external_references": [
                {"source_name": "mitre-atlas", "external_id": t,
                 "url": ATLAS_URL + base.replace("AML.", "")},
            ],
        })
    cves = sorted({c for i in incidents for c in (i.get("cve_ids") or [])})
    for c in cves:
        oid = _sid("vulnerability", c)
        cve_ids[c] = oid
        objects.append({
            "type": "vulnerability", "spec_version": "2.1", "id": oid,
            "created": EPOCH, "modified": EPOCH, "name": c,
            "external_references": [
                {"source_name": "cve", "external_id": c,
                 "url": f"https://www.cve.org/CVERecord?id={c}"},
            ],
        })

    # 2) Incident SDOs + relationships.
    for i in incidents:
        iid = i["id"]
        oid = _sid("x-genai-incident", iid)
        created = _ts(i.get("added") or i.get("date"))
        modified = _ts(i.get("updated") or i.get("added") or i.get("date"))
        ext = [{"source_name": "genai-incidents", "external_id": iid}]
        for r in i.get("references") or []:
            if r.get("url"):
                ext.append({"source_name": r.get("type") or "reference",
                            "description": r.get("title") or "", "url": r["url"]})
        for code in i.get("owasp_llm") or []:
            ext.append({"source_name": "owasp-llm-top10-2025", "external_id": code})
        for code in i.get("owasp_asi") or []:
            ext.append({"source_name": "owasp-asi-top10", "external_id": code})
        sdo = {
            "type": "x-genai-incident", "spec_version": "2.1", "id": oid,
            "created": created, "modified": modified,
            "name": i.get("title") or iid,
            "description": i.get("description") or "",
            "external_references": ext,
            "labels": i.get("tags") or [],
            "x_incident_id": iid,
            "x_date": i.get("date"), "x_year": i.get("year"),
            "x_severity": i.get("severity"),
            "x_attack_vector": i.get("attack_vector"),
            "x_category": i.get("category"),
            "x_quality_tier": i.get("quality_tier"),
            # WS6-T9: x_tier is the landmark/feed selector. x_quality_tier is
            # a different axis (vetting level) and cannot stand in for it --
            # a consumer filtering the bundle for the notable subset needs
            # this one. Emitted unconditionally, like x_quality_tier and
            # unlike the optional landmark-only labels below.
            "x_tier": i.get("tier"),
            "x_corpus": i.get("corpus"),
            "x_owasp_llm": i.get("owasp_llm") or [],
            "x_owasp_asi": i.get("owasp_asi") or [],
            "x_nist_ai_rmf": i.get("nist_ai_rmf") or [],
            "x_mitre_atlas": i.get("mitre_atlas") or [],
            "x_mitre_atlas_tactics": i.get("mitre_atlas_tactics") or [],
            "x_cve_ids": i.get("cve_ids") or [],
        }
        # Landmark-tier labels are optional and unassessed-by-absence: emit
        # only when present so unlabeled entries carry no null/empty claim.
        for opt in ("reversibility_class", "discovery_method"):
            if i.get(opt):
                sdo[f"x_{opt}"] = i[opt]
        # Row-level license-obligation marker (D14; heuristic fallback
        # retired D15) -- mirrors the entry's own `content_license` field
        # verbatim; absent otherwise. See `_content_license()` above.
        cl = _content_license(i)
        if cl:
            sdo["x_content_license"] = cl
        objects.append(sdo)
        for t in i.get("mitre_atlas") or []:
            rid = _sid("relationship", iid, "uses", t)
            objects.append({
                "type": "relationship", "spec_version": "2.1", "id": rid,
                "created": created, "modified": modified,
                "relationship_type": "uses",
                "source_ref": oid, "target_ref": technique_ids[t],
            })
        for c in i.get("cve_ids") or []:
            rid = _sid("relationship", iid, "exploits", c)
            objects.append({
                "type": "relationship", "spec_version": "2.1", "id": rid,
                "created": created, "modified": modified,
                "relationship_type": "exploits",
                "source_ref": oid, "target_ref": cve_ids[c],
            })

    return {"type": "bundle", "id": _sid("bundle", "genai-incidents"), "objects": objects}


def main() -> None:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    bundle = build_bundle(incidents)
    out = json.dumps(bundle, indent=2, ensure_ascii=False) + "\n"
    (DATA / "incidents.stix.json").write_text(out, encoding="utf-8", newline="\n")
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    (DOCS_DATA / "incidents.stix.json").write_text(out, encoding="utf-8", newline="\n")
    n_obj = len(bundle["objects"])
    print(f"[stix] wrote {n_obj} STIX objects for {len(incidents)} incidents "
          f"-> data/incidents.stix.json (+ docs/data/)")


if __name__ == "__main__":
    main()
