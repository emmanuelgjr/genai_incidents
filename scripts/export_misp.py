"""
Export the dataset as a **MISP feed** under ``docs/misp/``, served by GitHub
Pages so a MISP instance can subscribe to it as a remote feed (Sync Actions ->
Feeds -> Add, format "MISP Feed", URL = the docs/misp/ base).

A MISP feed is a directory of:
  manifest.json          {event-uuid: {info, date, analysis, ...}, ...}
  <event-uuid>.json      one {"Event": {...}} per file
  hashes.csv             value-md5,event-uuid  (lets MISP dedupe on pull)

Modelling. Incidents are grouped into **one Event per year** (keeping the file
count small — ~15 events rather than ~12k). Each incident contributes
attributes to its year's Event, all sharing a ``comment`` of "<INC-id> — <title>"
so they stay grouped, and carrying taxonomy as attribute Tags:
  - one ``vulnerability`` attribute per CVE,
  - one ``link`` attribute per reference URL,
  - one ``text`` attribute holding the incident title,
with Tags ``genai-incidents:*`` (incident id, attack vector, severity, OWASP
LLM/ASI, corpus, tier), ``mitre-atlas:technique="…"``, and ``veris:*``
machinetags (VERIS 1.4.1 enum paths derived from ``attack_vector`` via the
hand-curated ``mappings/veris.json``) on the title attribute.

Determinism: event/attribute UUIDs are UUIDv5 and every ``timestamp`` is derived
from the year (fixed epoch), so the feed is byte-stable across rebuilds.
Generated at Pages build time and git-ignored — never committed.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "docs" / "misp"

# attack_vector -> VERIS 1.4.1 enum paths ("<misp-predicate>=<value>"),
# hand-curated in mappings/veris.json. Missing file degrades to no veris tags
# so the exporter stays runnable in isolation.
try:
    _VERIS_MAP: dict[str, list[str]] = json.loads(
        (ROOT / "mappings" / "veris.json").read_text(encoding="utf-8")
    ).get("attack_vector_to_veris", {})
except (OSError, json.JSONDecodeError):
    _VERIS_MAP = {}

# Fixed namespace (shared scheme with the STIX export) so ids are stable.
NS = uuid.UUID("6f1a9c4e-9b2d-5e7a-8c3f-0a1b2c3d4e5f")
ORG_UUID = str(uuid.uuid5(NS, "misp-orgc|genai-incidents"))
ORGC = {"name": "genai_incidents", "uuid": ORG_UUID}


def _uuid(*parts: str) -> str:
    return str(uuid.uuid5(NS, "misp|" + "|".join(parts)))


def _year_epoch(year: int) -> str:
    """Unix timestamp (string) for Jan 1 <year> 00:00:00 UTC — a fixed,
    deterministic stamp so the feed never churns between rebuilds."""
    try:
        return str(calendar.timegm((int(year), 1, 1, 0, 0, 0, 0, 0, 0)))
    except (TypeError, ValueError):
        return "1704067200"  # 2024-01-01


def _tag(name: str) -> dict:
    return {"name": name}


def _incident_tags(e: dict) -> list[dict]:
    tags: list[dict] = [_tag(f'genai-incidents:incident-id="{e["id"]}"')]
    if e.get("attack_vector"):
        tags.append(_tag(f'genai-incidents:attack-vector="{e["attack_vector"]}"'))
    if e.get("severity"):
        tags.append(_tag(f'genai-incidents:severity="{e["severity"]}"'))
    if e.get("corpus"):
        tags.append(_tag(f'genai-incidents:corpus="{e["corpus"]}"'))
    if e.get("tier"):
        tags.append(_tag(f'genai-incidents:tier="{e["tier"]}"'))
    for c in e.get("owasp_llm") or []:
        tags.append(_tag(f'genai-incidents:owasp-llm="{c}"'))
    for c in e.get("owasp_asi") or []:
        tags.append(_tag(f'genai-incidents:owasp-asi="{c}"'))
    for t in e.get("mitre_atlas") or []:
        tags.append(_tag(f'mitre-atlas:technique="{t}"'))
    for mt in _VERIS_MAP.get(e.get("attack_vector") or "", []):
        pred, _, val = mt.partition("=")
        tags.append(_tag(f'veris:{pred}="{val}"'))
    return tags


def _attr(e: dict, atype: str, category: str, value: str,
          to_ids: bool, tags: list[dict] | None = None,
          seq: str = "") -> dict:
    comment = f'{e["id"]} — {e.get("title") or ""}'[:255]
    return {
        "uuid": _uuid("attr", e["id"], atype, seq or value),
        "type": atype,
        "category": category,
        "to_ids": to_ids,
        "value": value,
        "comment": comment,
        "Tag": tags or [],
    }


def _incident_attributes(e: dict) -> list[dict]:
    attrs: list[dict] = []
    tags = _incident_tags(e)
    # Title carries the full taxonomy tag set.
    title = (e.get("title") or e["id"]).strip()
    if title:
        attrs.append(_attr(e, "text", "Other", title[:600], False, tags, seq="title"))
    rejected = set(e.get("rejected_cve_ids") or [])  # WS4-T2: not valid identifiers
    for c in e.get("cve_ids") or []:
        if c in rejected:
            continue
        attrs.append(_attr(e, "vulnerability", "External analysis", c, False,
                           [_tag(f'genai-incidents:incident-id="{e["id"]}"')]))
    seen_urls: set[str] = set()
    for r in e.get("references") or []:
        url = (r.get("url") or "").strip()
        if url.startswith("http") and url not in seen_urls:
            seen_urls.add(url)
            attrs.append(_attr(e, "link", "External analysis", url, False,
                               [_tag(f'genai-incidents:incident-id="{e["id"]}"')],
                               seq=f"link{len(seen_urls)}"))
    return attrs


def _event_meta(year: int) -> dict:
    return {
        "info": f"GenAI / agentic-AI security incidents — {year}",
        "date": f"{year}-01-01",
        "analysis": "2",          # completed
        "threat_level_id": "3",   # low (catalogue, not active campaign)
        "timestamp": _year_epoch(year),
        "published": True,
        "Orgc": ORGC,
        "Tag": [_tag("tlp:clear"), _tag('genai-incidents:feed="dataset"')],
    }


def build(incidents: list[dict]) -> tuple[int, int]:
    by_year: dict[int, list[dict]] = defaultdict(list)
    for e in incidents:
        try:
            y = int(e.get("year") or 0)
        except (TypeError, ValueError):
            y = 0
        by_year[y or 1970].append(e)

    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    hash_lines: list[str] = []
    n_attr = 0

    for year in sorted(by_year):
        ev_uuid = _uuid("event", str(year))
        meta = _event_meta(year)
        attributes: list[dict] = []
        for e in sorted(by_year[year], key=lambda x: x["id"]):
            for a in _incident_attributes(e):
                attributes.append(a)
                # The MISP feed format matches attributes on the MD5 of the
                # value (hashes.csv) — an interop identifier, not a security
                # control.
                md5 = hashlib.md5(
                    a["value"].encode("utf-8"), usedforsecurity=False
                ).hexdigest()
                hash_lines.append(f"{md5},{ev_uuid}")
        n_attr += len(attributes)

        event = {"Event": {
            "uuid": ev_uuid,
            "info": meta["info"],
            "date": meta["date"],
            "analysis": meta["analysis"],
            "threat_level_id": meta["threat_level_id"],
            "timestamp": meta["timestamp"],
            "published": True,
            "Orgc": ORGC,
            "Tag": meta["Tag"],
            "Attribute": attributes,
        }}
        (OUT / f"{ev_uuid}.json").write_text(
            json.dumps(event, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
        # Manifest entry (MISP feed manifest schema).
        manifest[ev_uuid] = {
            "Orgc": ORGC,
            "Tag": meta["Tag"],
            "info": meta["info"],
            "date": meta["date"],
            "analysis": meta["analysis"],
            "threat_level_id": meta["threat_level_id"],
            "timestamp": meta["timestamp"],
        }

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    # hashes.csv — sorted for deterministic output.
    (OUT / "hashes.csv").write_text(
        "\n".join(sorted(hash_lines)) + "\n", encoding="utf-8", newline="\n",
    )
    _write_readme(len(manifest))
    return len(manifest), n_attr


def _write_readme(n_events: int) -> None:
    readme = f"""# MISP feed

A [MISP](https://www.misp-project.org/) feed mirroring the `genai_incidents`
dataset, regenerated on every Pages deploy by `scripts/export_misp.py`.
Incidents are grouped into **one Event per year** ({n_events} events); each
incident's CVEs, reference links and title become tagged attributes
(`genai-incidents:*`, `mitre-atlas:technique="…"`, and `veris:*` machinetags
per the VERIS 1.4.1 crosswalk in `mappings/veris.json`).

## Subscribe (MISP)

Sync Actions → Feeds → Add Feed:

- **Input Source:** Network
- **Format:** MISP Feed
- **URL:** `https://emmanuelgjr.github.io/genai_incidents/misp/`
- **Source Format:** JSON

Then *Fetch and store all feed data*. MISP reads `manifest.json`, pulls each
`<event-uuid>.json`, and uses `hashes.csv` to deduplicate on subsequent pulls.

## Files

| File | Purpose |
|---|---|
| `manifest.json` | event-uuid → event metadata (MISP reads this first) |
| `<event-uuid>.json` | one `{{"Event": …}}` per year |
| `hashes.csv` | `value-md5,event-uuid` for pull-time dedup |

TLP: clear. The dataset is CC-BY-4.0; attributes are catalogue references to
public disclosures, not active-campaign IOCs (threat level: low).
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")


def main() -> None:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    # WS4-T2: retracted entries (all CVEs REJECTED) stay in data/incidents.json so
    # their IDs resolve, but are not published into downstream feeds.
    incidents = [e for e in incidents if e.get("status") != "retracted"]
    n_events, n_attr = build(incidents)
    print(f"[misp] wrote MISP feed: {n_events} year-events, {n_attr} attributes "
          f"-> docs/misp/")


if __name__ == "__main__":
    main()
