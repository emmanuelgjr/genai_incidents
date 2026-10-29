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
LLM and ASI codes, corpus, tier), ``mitre-atlas:technique="…"``, and ``veris:*``
machinetags (VERIS 1.4.1 enum paths derived from ``attack_vector`` via the
hand-curated ``mappings/veris.json``) on the title attribute.

Rows whose upstream source has stopped refreshing (`source_freshness`, D57)
carry three more machinetags on every attribute of the row:
``genai-incidents:source-freshness``, ``genai-incidents:source-as-of`` and
``genai-incidents:source-review-by`` (omitted when the row has no review date).
Attribute-level because events are per-year: an event-level tag would mark ~15
unrelated incidents per row.

Determinism: event/attribute UUIDs are UUIDv5 and every ``timestamp`` is derived
from the data -- an event's timestamp is the newest `updated` date among its
incidents (UTC midnight, unix seconds) plus ``EXPORTER_VERSION`` seconds -- so
the feed is byte-stable across rebuilds. MISP decides whether to re-pull an
event by comparing the manifest timestamp with its stored copy, so the stamp
MUST move when an event's content moves: it does, because `updated` moves
exactly when an entry's content fields change (merge_and_dedupe.py
`_CONTENT_FIELDS`), and EXPORTER_VERSION covers exporter-side changes (a new
machinetag). Before v2.13.0 the stamp was the fixed Jan 1 of the event's year,
which meant no content change ever reached a subscribed instance.
Generated at Pages build time and git-ignored — never committed.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import uuid
from collections import defaultdict
from pathlib import Path

from entry_status import stands
from taxonomy_versions import taxonomy_versions, tv_revision

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

# Bump when the event/attribute shape or the entry -> attribute mapping changes
# (a new machinetag, a changed comment). Added, in seconds, to every event
# timestamp so a subscribed MISP re-pulls. History: 0 = implicit up to v2.12.0
# (fixed Jan-1-of-year stamps); 1 = v2.13.0 item 8 (source-freshness machinetags;
# stamps derived from `updated`).
EXPORTER_VERSION = 1

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


def _event_timestamp(year: int, incidents: list[dict]) -> str:
    """Unix-seconds stamp (string): newest `updated` among the event's incidents
    (falling back to `added`, then the year's Jan 1) + EXPORTER_VERSION seconds
    + (taxonomy revision - 1) seconds."""
    best = 0
    for e in incidents:
        d = (e.get("updated") or e.get("added") or "").strip()
        try:
            y, m, dd = (int(x) for x in d[:10].split("-"))
            best = max(best, calendar.timegm((y, m, dd, 0, 0, 0, 0, 0, 0)))
        except (ValueError, TypeError):
            continue
    if not best:
        best = int(_year_epoch(year))
    # + (taxonomy revision - 1): the version machinetags are on every event,
    # so a change to taxonomy_versions must move every timestamp (REVISIONS).
    return str(best + EXPORTER_VERSION + tv_revision() - 1)


def _freshness_tags(e: dict) -> list[dict]:
    """D57 machinetags for a row whose upstream source has stopped refreshing:
    from the row's own `source_freshness` marker, only on marked rows, with
    `source-review-by` only when the marker carries a review date."""
    sf = e.get("source_freshness")
    if not sf:
        return []
    tags = []
    for pred, key in (("source-freshness", "status"), ("source-as-of", "as_of"),
                      ("source-review-by", "review_by")):
        if sf.get(key):
            tags.append(_tag(f'genai-incidents:{pred}="{sf[key]}"'))
    return tags


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
    return tags + _freshness_tags(e)


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
                           [_tag(f'genai-incidents:incident-id="{e["id"]}"')]
                           + _freshness_tags(e)))
    seen_urls: set[str] = set()
    for r in e.get("references") or []:
        url = (r.get("url") or "").strip()
        if url.startswith("http") and url not in seen_urls:
            seen_urls.add(url)
            attrs.append(_attr(e, "link", "External analysis", url, False,
                               [_tag(f'genai-incidents:incident-id="{e["id"]}"')]
                               + _freshness_tags(e),
                               seq=f"link{len(seen_urls)}"))
    return attrs


def _taxonomy_version_tags() -> list[dict]:
    """One `genai-incidents:taxonomy-<name>="<version>"` tag per pinned taxonomy
    on every event (and so on every manifest entry, which copies the event's
    Tag list). Derived from mappings/*.json via scripts/taxonomy_versions.py.
    Tags rather than a new top-level manifest key: MISP's feed reader treats
    every manifest key as an event uuid, so a non-uuid key could break pulls.
    Unversioned taxonomies (None) are omitted rather than tagged with a guess."""
    return [_tag(f'genai-incidents:taxonomy-{k.replace("_", "-")}="{v}"')
            for k, v in taxonomy_versions().items() if v is not None]


def _event_meta(year: int, incidents: list[dict] | None = None) -> dict:
    return {
        "info": f"GenAI / agentic-AI security incidents — {year}",
        "date": f"{year}-01-01",
        "analysis": "2",          # completed
        "threat_level_id": "3",   # low (catalogue, not active campaign)
        "timestamp": _event_timestamp(year, incidents or []),
        "published": True,
        "Orgc": ORGC,
        "Tag": [_tag("tlp:clear"), _tag('genai-incidents:feed="dataset"')]
               + _taxonomy_version_tags(),
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
        meta = _event_meta(year, by_year[year])
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
per the VERIS 1.4.1 crosswalk in `mappings/veris.json`). Every event (and its
`manifest.json` entry) carries `genai-incidents:taxonomy-<name>="<version>"`
tags (atlas, owasp-llm, owasp-asi, veris, owasp-dsgai, maestro, nist-ai-rmf;
capec once versioned) naming the
pinned taxonomy releases the tags refer to. Attributes of rows whose upstream
source has stopped refreshing additionally carry
`genai-incidents:source-freshness="stale"`, `genai-incidents:source-as-of="<date>"`
and `genai-incidents:source-review-by="<date>"` (the row's own `source_freshness`
marker; absent on every other row). Each event's `timestamp` is the newest
`updated` date among its incidents, so MISP re-pulls an event when its
content fields changed (changes to `tier`, `quality_tier`, `corpus`, `content_license`
or `source_freshness` alone surface only via an `EXPORTER_VERSION` bump).

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
| `build_manifest.json`, `SHA256SUMS` | build provenance and `sha256sum -c` checksums for every file here (MISP ignores them) |

TLP: clear. The dataset is CC-BY-4.0; attributes are catalogue references to
public disclosures, not active-campaign IOCs (threat level: low).
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")


def main() -> None:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    # WS4-T2/D130: retracted (all CVEs REJECTED) and unverified (no confirmed
    # primary source) entries stay in data/incidents.json so their IDs
    # resolve, but are not published into downstream feeds.
    incidents = [e for e in incidents if stands(e)]
    n_events, n_attr = build(incidents)
    print(f"[misp] wrote MISP feed: {n_events} year-events, {n_attr} attributes "
          f"-> docs/misp/")


if __name__ == "__main__":
    main()
