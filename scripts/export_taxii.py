"""
Export the dataset as a **static TAXII-compatible discovery document** under ``docs/taxii2/``,
served by GitHub Pages alongside the site.

TAXII 2.1 is normally a live HTTP API. A static mirror cannot set the
``application/taxii+json;version=2.1`` response media type or honour query-string
pagination, but it CAN publish every resource a client needs as a plain JSON
file at a predictable path. Point a TAXII-aware tool (or plain ``curl``) at the
files below; OpenCTI/other importers that accept a STIX bundle can also just pull
the collection ``objects.json`` directly.

Layout (all relative to the Pages root, e.g.
https://emmanuelgjr.github.io/genai_incidents):

  taxii2/discovery.json                         TAXII Discovery
  taxii2/api/root.json                          API Root
  taxii2/api/collections.json                   Collections list
  taxii2/api/collections/<id>.json              Collection resource
  taxii2/api/collections/<id>/objects.json      STIX envelope {more,objects}
  taxii2/api/collections/<id>/manifest.json     Manifest envelope
  taxii2/README.md                              consumption guide + caveats

Determinism: the collection id is a fixed UUIDv5 and every STIX object is built
by ``export_stix.build_bundle`` (UUIDv5 ids, date-derived timestamps), so the
output is byte-stable across rebuilds. Generated at Pages build time and
git-ignored — never committed — exactly like the STIX bundle.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from export_stix import build_bundle, NS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs" / "taxii2"

# Public base URL of the Pages site (used to build absolute api_root URLs the
# TAXII discovery document must advertise).
BASE_URL = "https://emmanuelgjr.github.io/genai_incidents"
TAXII_MEDIA = "application/taxii+json;version=2.1"
STIX_MEDIA = "application/stix+json;version=2.1"

# Stable collection id (UUIDv5 over the export namespace).
COLLECTION_ID = str(uuid.uuid5(NS, "taxii-collection|genai-incidents"))


def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def build(incidents: list[dict]) -> int:
    bundle = build_bundle(incidents)
    objects = bundle["objects"]

    api_root = f"{BASE_URL}/taxii2/api/"
    discovery = {
        "title": "genai_incidents — static TAXII 2.1",
        "description": (
            "Read-only static TAXII 2.1 mirror of the genai_incidents dataset "
            "(GenAI/agentic-AI security incidents mapped to OWASP LLM/ASI, NIST "
            "AI RMF and MITRE ATLAS). Served as static JSON files over GitHub "
            "Pages; see taxii2/README.md for the media-type caveat."
        ),
        "contact": "https://github.com/emmanuelgjr/genai_incidents",
        "default": api_root,
        "api_roots": [api_root],
    }
    _write(OUT / "discovery.json", discovery)

    root = {
        "title": "genai_incidents API root",
        "description": "Single API root exposing the genai_incidents collection.",
        "versions": [TAXII_MEDIA],
        # 100 MiB, matching GitHub Pages' per-file ceiling.
        "max_content_length": 104857600,
    }
    _write(OUT / "api" / "root.json", root)

    collection = {
        "id": COLLECTION_ID,
        "title": "GenAI & Agentic-AI Security Incidents",
        "description": (
            "Every incident as an x-genai-incident SDO with full taxonomy "
            "mappings, plus attack-pattern (MITRE ATLAS) and vulnerability (CVE) "
            "SDOs and the relationships linking them."
        ),
        "can_read": True,
        "can_write": False,
        "media_types": [STIX_MEDIA],
    }
    _write(OUT / "api" / "collections.json", {"collections": [collection]})
    _write(OUT / "api" / "collections" / f"{COLLECTION_ID}.json", collection)

    # Objects envelope (full collection in one page — static hosting can't
    # paginate on query strings, so `more` is always false).
    _write(
        OUT / "api" / "collections" / COLLECTION_ID / "objects.json",
        {"more": False, "objects": objects},
    )

    # Manifest envelope: one record per object (id, date_added, version, media).
    manifest = [
        {
            "id": o["id"],
            "date_added": o.get("created", o.get("modified", "")),
            "version": o.get("modified", o.get("created", "")),
            "media_type": STIX_MEDIA,
        }
        for o in objects
    ]
    _write(
        OUT / "api" / "collections" / COLLECTION_ID / "manifest.json",
        {"more": False, "objects": manifest},
    )

    _write_readme(api_root)
    return len(objects)


def _write_readme(api_root: str) -> None:
    readme = f"""# Static TAXII-compatible discovery document

This directory is a **read-only, static** TAXII 2.1 mirror of the
`genai_incidents` dataset, regenerated on every Pages deploy by
`scripts/export_taxii.py`.

## Endpoints

| TAXII 2.1 resource | URL |
|---|---|
| Discovery | `{api_root.rsplit('/api/', 1)[0]}/discovery.json` |
| API Root | `{api_root}root.json` |
| Collections | `{api_root}collections.json` |
| Collection | `{api_root}collections/{COLLECTION_ID}.json` |
| Objects | `{api_root}collections/{COLLECTION_ID}/objects.json` |
| Manifest | `{api_root}collections/{COLLECTION_ID}/manifest.json` |

## OWASP edition label

OWASP LLM `external_references` in these objects carry an edition-qualified
`source_name`, currently `owasp-llm-top10-2026` (until 2026-10-01 13:43 UTC,
the Pages deploy of `7dc80602`, it read `owasp-llm-top10-2025`, which was the
wrong edition for these codes). The edition is derived from the crosswalk
`mappings/owasp_llm_2025_to_2026.json`. The relabel changed object content
without changing `id` or `modified`, so consumers that treat an unchanged
(`id`, `modified`) as an already-seen object version, as STIX 2.1 versioning
permits, may not pick up the corrected label; prefer delete-then-import.

## Caveat: media type & pagination

GitHub Pages serves these files as `application/json`, **not** the
`{TAXII_MEDIA}` media type a strict TAXII 2.1 client expects, and it cannot
honour `?added_after=`/pagination query strings. Tools that tolerate the generic
JSON type (or that accept a STIX bundle directly) can consume the collection
`objects.json` as-is — it is a valid STIX 2.1 envelope. For a fully
conformant live API, mirror these objects behind a real TAXII server
(e.g. Medallion) or import the STIX bundle at `data/incidents.stix.json`.

## Quick start

```bash
base="{api_root.rsplit('/api/', 1)[0]}"
curl -s "$base/discovery.json" | jq .
curl -s "{api_root}collections/{COLLECTION_ID}/objects.json" \\
  | jq '.objects | group_by(.type) | map({{type: .[0].type, n: length}})'
```
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")


def main() -> None:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    # WS4-T2: retracted entries (all CVEs REJECTED) stay in data/incidents.json so
    # their IDs resolve, but are not published into downstream feeds.
    incidents = [e for e in incidents if e.get("status") != "retracted"]
    n = build(incidents)
    print(f"[taxii] wrote static TAXII-compatible discovery document ({n} objects, 1 collection) "
          f"-> docs/taxii2/  [collection {COLLECTION_ID}]")


if __name__ == "__main__":
    main()
