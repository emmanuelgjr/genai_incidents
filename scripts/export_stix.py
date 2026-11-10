"""
Export the incident dataset as a STIX 2.1 bundle for ingestion into threat-
intelligence platforms (OpenCTI, MISP-STIX, TAXII servers, etc.).

Output: data/incidents.stix.json (+ mirrored into docs/data/ for download).

Modelling:
  - each incident -> a custom `x-genai-incident` SDO carrying the full
    taxonomy mapping as `x_*` properties + external_references;
  - each distinct MITRE ATLAS technique -> an `attack-pattern` SDO;
  - each distinct CVE -> a `vulnerability` SDO;
  - `relationship` SDOs link incidents to the techniques/CVEs they involve;
  - one `identity` SDO ("genai_incidents") carries `x_taxonomy_versions`, the
    pinned versions of the taxonomies (ATLAS, OWASP Top 10 for LLM Applications, OWASP Top 10 for Agentic Applications, CAPEC, VERIS, OWASP GenAI Data Security, MAESTRO, NIST AI RMF)
    that the x_* mapping properties refer to.

All STIX ids are derived deterministically (UUIDv5 over a fixed namespace),
and object timestamps come from each incident's `added`/`updated` dates — so
the bundle is byte-stable across rebuilds and safe for the CI drift check.

`modified` rule (v2.13.0 item 8; docs/audits/ws6-v2130-export-integrity-2026-10-11.md):

    modified = <updated date> T00:00:00.<EXPORTER_VERSION as 3 digits>Z

`updated` is bumped by the merge exactly when an entry's content fields change
(scripts/merge_and_dedupe.py `_CONTENT_FIELDS`), so an unchanged entry keeps a
byte-identical SDO and a changed one moves forward by >= 1 day. The millisecond
field carries `EXPORTER_VERSION`: bump it whenever the SDO shape or the
mapping from entry to SDO changes (a new `x_` property, a relabelled
`source_name`), and every object moves forward by 1 ms per bump -- a STIX
consumer that dedupes on (id, modified) then re-imports exactly the objects the
exporter changed. `modified >= created` always holds (clamped).
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from entry_status import stands
from taxonomy_versions import taxonomy_versions, tv_revision

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS_DATA = ROOT / "docs" / "data"
MAPPINGS = ROOT / "mappings"

# Fixed namespace so UUIDv5 ids are stable across runs and machines.
NS = uuid.UUID("6f1a9c4e-9b2d-5e7a-8c3f-0a1b2c3d4e5f")
# Constant timestamp for taxonomy objects (techniques/CVEs) that have no own date.
EPOCH = "2024-01-01T00:00:00.000Z"

# STIX `modified` rule (see module docstring). Bump on ANY change to the SDO
# shape or to how an entry maps onto it. History:
#   0 -- (implicit, up to v2.12.0) modified == updated date, ms field .000;
#        exporter changes did not move `modified`.
#   1 -- v2.13.0 item 8: x_source_freshness added (D57); version in the ms field.
# Range 0..999 (it is the millisecond field of an RFC 3339 timestamp).
EXPORTER_VERSION = 1

ATLAS_URL = "https://atlas.mitre.org/techniques/"
OWASP_LLM_URL = "https://genai.owasp.org/llmrisk/"


def _owasp_llm_source_name() -> str:
    """Edition-qualified external_reference source_name for owasp_llm codes.

    The edition is read from the crosswalk's ``to_version`` (the single source
    of truth for which edition the corpus codes belong to, E24 / D26(c)), so a
    future edition migration cannot leave this label stale.
    """
    xwalk = json.loads((MAPPINGS / "owasp_llm_2025_to_2026.json").read_text(encoding="utf-8"))
    return f"owasp-llm-top10-{xwalk['to_version']}"


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


def _ts_v(date_str: str, version: int | None = None) -> str:
    """`_ts` with the exporter version in the millisecond field: the `modified`
    timestamp for a given `updated` date. ``version`` defaults to
    EXPORTER_VERSION; the `identity` object passes EXPORTER_VERSION plus its
    taxonomy revision offset (see `_modified`)."""
    v = EXPORTER_VERSION if version is None else version
    if not 0 <= v <= 999:
        raise ValueError(f"exporter version {v} does not fit in 3 ms digits")
    return _ts(date_str)[:-4] + f"{v:03d}Z"


def _modified(created: str, *date_strs: str, version: int | None = None) -> str:
    """Latest versioned timestamp among ``date_strs``, never earlier than
    ``created`` (STIX 2.1: modified >= created). RFC 3339 UTC strings of fixed
    width compare lexicographically."""
    return max([created] + [_ts_v(d, version) for d in date_strs if d])


def _taxonomy_dates() -> list[str]:
    """Release dates recorded in the pinned mapping files. A re-pin of a dated
    taxonomy moves the shared taxonomy objects' `modified` forward."""
    out = []
    for fname, field in (("mitre_atlas.json", "release_date"),
                         ("owasp_llm_2025_to_2026.json", "published")):
        try:
            v = json.loads((MAPPINGS / fname).read_text(encoding="utf-8")).get(field)
        except (OSError, json.JSONDecodeError):
            v = None
        if v:
            out.append(str(v))
    return out


def _source_freshness(i: dict) -> dict | None:
    """`x_source_freshness` payload (D57): the entry's own `source_freshness`
    marker, keys {status, as_of, sources, review_by}, verbatim. Keys with a
    null value are dropped (never emit null); None when the row is unmarked.
    Same pattern as `_content_license` -- derived from the row, never authored
    here, and deliberately NOT pushed into `labels`."""
    sf = i.get("source_freshness")
    if not sf:
        return None
    return {k: v for k, v in sf.items() if v is not None}


def _atlas_names() -> dict[str, str]:
    try:
        m = json.loads((MAPPINGS / "mitre_atlas.json").read_text(encoding="utf-8"))
        return {k: v.get("name", k) for k, v in (m.get("techniques") or {}).items()}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _live_cves(i: dict) -> list[str]:
    """cve_ids minus those the CVE Program has REJECTED (WS4-T2)."""
    rej = set(i.get("rejected_cve_ids") or [])
    return [c for c in (i.get("cve_ids") or []) if c not in rej]


def build_bundle(incidents: list[dict]) -> dict:
    atlas_names = _atlas_names()
    objects: list[dict] = []
    technique_ids: dict[str, str] = {}
    cve_ids: dict[str, str] = {}

    # 1) Shared taxonomy SDOs: ATLAS techniques + CVEs.
    tax_dates = _taxonomy_dates()
    # attack-pattern content (name) follows the pinned ATLAS release; CVE
    # vulnerability content (the id) never changes; both fall back to EPOCH.
    ap_modified = _modified(EPOCH, *[d for d in tax_dates[:1]])
    vuln_modified = _modified(EPOCH, EPOCH[:10])
    techniques = sorted({t for i in incidents for t in (i.get("mitre_atlas") or [])})
    for t in techniques:
        oid = _sid("attack-pattern", t)
        technique_ids[t] = oid
        base = t.split(".")[0]  # AML.T0051.000 -> AML.T0051 for the URL
        objects.append({
            "type": "attack-pattern", "spec_version": "2.1", "id": oid,
            "created": EPOCH, "modified": ap_modified,
            "name": atlas_names.get(t) or atlas_names.get(base) or t,
            "external_references": [
                {"source_name": "mitre-atlas", "external_id": t,
                 "url": ATLAS_URL + base.replace("AML.", "")},
            ],
        })
    cves = sorted({c for i in incidents for c in _live_cves(i)})
    for c in cves:
        oid = _sid("vulnerability", c)
        cve_ids[c] = oid
        objects.append({
            "type": "vulnerability", "spec_version": "2.1", "id": oid,
            "created": EPOCH, "modified": vuln_modified, "name": c,
            "external_references": [
                {"source_name": "cve", "external_id": c,
                 "url": f"https://www.cve.org/CVERecord?id={c}"},
            ],
        })

    # 1b) Dataset metadata: one `identity` SDO (a standard STIX type that
    #     permits custom x_ properties) carrying the versions of the pinned
    #     taxonomies every x_* mapping on the incident SDOs refers to. Derived
    #     from mappings/*.json (scripts/taxonomy_versions.py). One object, not a
    #     property repeated on ~15k incident SDOs.
    objects.append({
        "type": "identity", "spec_version": "2.1",
        "id": _sid("identity", "genai-incidents"),
        "created": EPOCH,
        # Dataset-level object: moves whenever any incident or pinned taxonomy
        # date moves (over-bumping one object is the safe direction; the ASI /
        # VERIS / CAPEC pins carry no date of their own).
        # Its ms field also carries the taxonomy revision offset
        # (taxonomy_versions.REVISIONS): a change to `x_taxonomy_versions`
        # moves this object's `modified` and no other (tv_revision() raises
        # on an unregistered change).
        "modified": _modified(EPOCH, *tax_dates,
                              *[i.get("updated") or i.get("added") or i.get("date") or ""
                                for i in incidents],
                              version=EXPORTER_VERSION + tv_revision() - 1),
        "name": "genai_incidents", "identity_class": "system",
        "x_taxonomy_versions": taxonomy_versions(),
    })

    # 2) Incident SDOs + relationships.
    owasp_llm_src = _owasp_llm_source_name()
    for i in incidents:
        iid = i["id"]
        oid = _sid("x-genai-incident", iid)
        created = _ts(i.get("added") or i.get("date"))
        modified = _modified(created, i.get("updated") or i.get("added") or i.get("date"))
        ext = [{"source_name": "genai-incidents", "external_id": iid}]
        for r in i.get("references") or []:
            if r.get("url"):
                ext.append({"source_name": r.get("type") or "reference",
                            "description": r.get("title") or "", "url": r["url"]})
        for code in i.get("owasp_llm") or []:
            ext.append({"source_name": owasp_llm_src, "external_id": code})
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
            # a consumer filtering the bundle for the headline-citation (landmark) set needs
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
            # WS4-T2: CVE Program REJECTED ids stay in x_cve_ids for traceability
            # but get no vulnerability/relationship object below.
            "x_rejected_cve_ids": i.get("rejected_cve_ids") or [],
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
        # Upstream-freshness marker (D57): only on rows whose source has stopped
        # refreshing; absent otherwise, never null.
        sf = _source_freshness(i)
        if sf:
            sdo["x_source_freshness"] = sf
        objects.append(sdo)
        for t in i.get("mitre_atlas") or []:
            rid = _sid("relationship", iid, "uses", t)
            objects.append({
                "type": "relationship", "spec_version": "2.1", "id": rid,
                "created": created, "modified": modified,
                "relationship_type": "uses",
                "source_ref": oid, "target_ref": technique_ids[t],
            })
        for c in _live_cves(i):
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
    # WS4-T2/D130: retracted (all CVEs REJECTED) and unverified (no confirmed
    # primary source) entries stay in data/incidents.json so their IDs
    # resolve, but are not published into downstream feeds.
    incidents = [e for e in incidents if stands(e)]
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
