"""
Pull AI Incident Database (AIID) data from AIID's own **sanctioned bulk
channel** -- the official weekly snapshot published at
incidentdatabase.ai/research/snapshots/ (served from the Cloudflare R2
bucket pub-72b2b2fc36ec423189843747af98f80e.r2.dev) -- instead of the
prohibited high-volume per-page HTML scrape in scripts/scrape_aiid.py.

Swap-half of WS0-T4 / decision D1 (2026-07-16). The stop-half (disabling
scrape_aiid.py in `make ingest-all`) already landed; this is the
replacement channel. See docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md
for the full implementation note this script follows.

Output: ingest/aiid_full.json (SAME filename as the retired scrape's
output -- a deliberate drop-in replacement so scripts/merge_and_dedupe.py's
`ingest/*.json` glob needs no change) plus a small committed provenance
sidecar, ingest/aiid_full.provenance.json (snapshot URL/filename/sha256/
fetched-at/counts -- a pinned record of what this file was built from,
short of the full WS4-T1 snapshot-manifest infrastructure, which is a
separate, later task).

--- License handling (docs/SOURCE_LICENSES.md Section 1.2) ---

AIID's own terms-of-use license the `incidents`, `quickadd`, `duplicates`,
`taxa`, `classifications`, `entities`, and `entity_relationships`
collections under CC BY-SA 4.0, and EXPLICITLY EXCLUDE the `text` field of
the `reports` collection from that grant (the snapshot's own
`license.txt` corroborates this: "Report contents are subject to their
own intellectual property rights."). This script:

  1. Never extracts reports.csv / reports.bson / translations/reports.bson
     from the snapshot archive at all -- not "extracts but discards the
     text field", literally never opens that member.
  2. Never extracts any image/video binary or the *source* of an image or
     video (the snapshot ships none as first-class members; nothing here
     fabricates one) -- per the board note (PROGRESS.md:112) on AIID's
     stated exclusion for "the source of images and videos."
  3. Treats AIID's own free-text `description` field (part of the
     `incidents` collection, itself CC-BY-SA and NOT excluded) as an
     EPHEMERAL, in-memory classification signal only -- used to decide
     security-relevance / attack_vector / severity heuristics -- and NEVER
     writes it to the output file. The persisted `description` is always
     an ORIGINAL templated sentence built from structured facts (id,
     title, entities). This is *more* conservative than the retired
     scrape, which persisted a truncated verbatim `og:description`.
  4. Persists AIID's own incident `title` verbatim (a short headline, the
     same category of content the AIAAIC D2 reduction treats as safe to
     keep) plus structured, non-narrative facts: incident id, date,
     canonical AIID URL, and alleged-deployer/developer/harmed-party
     entity slugs (single-word identifiers, not prose) drawn from the
     `incidents` collection, and the MIT AI Risk Repository taxonomy
     classification (Risk Domain / Risk Subdomain -- a closed, fixed
     vocabulary, not free text) drawn from the `classifications`
     collection's MIT namespace. CSETv1/CSETv0/GMF classification tables
     are deliberately NOT used here: CSETv1/CSETv0 mix categorical fields
     with free-text "Notes"/"Full Description" columns, and GMF embeds
     literal quoted excerpts from report text in its "Snippets" columns --
     exactly the kind of narrative/report prose this script exists to
     keep out. Extending coverage to those tables is future work that
     needs its own per-column narrative-vs-categorical audit; flagged in
     the implementation note, not attempted here.

This does NOT resolve AIID's CC-BY-SA share-alike question in full (that
parallels the still-open AIAAIC database-right question, E13) -- it is
flagged as a distinct open item in docs/SOURCE_LICENSES.md Section 1.2 and
in the swap's implementation note. This script only fixes the *acquisition
method* (sanctioned snapshot vs. prohibited high-volume scrape) and keeps
the *content* at least as conservative as what was there before.

--- Invariant 3 (never delete; status + tombstone instead) ---

The security-relevant keyword filter that gates which *new* AIID incidents
enter the corpus is reused from scrape_aiid.py's TAXONOMY_RULES machinery.
But an incident_id that is ALREADY referenced by a corpus entry in
data/incidents.json (via `aiid_id` or an `AIID-<n>` / `AIID-<n>-OECD`
source_id, from ANY ingest file, not just this one) is unconditionally
carried forward regardless of what the fresh security-relevance filter
would decide today -- so a swap-driven change in filter behavior can never
silently drop a previously-present entry. See the delta report,
docs/audits/WS0-T4-aiid-snapshot-swap-delta-2026-07-18.md, for the actual
before/after entry-count and field-level diff.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import re
import sys
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
DATA = ROOT / "data"
CACHE = INGEST / "_cache" / "aiid_snapshot"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest.common import robust_fetch  # noqa: E402
from scrape_aiid import (  # noqa: E402  (deliberately reused per Makefile's D1/E1 note)
    TAXONOMY_RULES,
    is_security_relevant,
    map_taxonomy,
    severity_for,
)

SNAPSHOTS_INDEX_URL = "https://incidentdatabase.ai/research/snapshots/"
R2_BASE = "https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev"
BACKUP_RE = re.compile(r"backup-(\d{14})\.tar\.bz2")

OUT_PATH = INGEST / "aiid_full.json"
PROVENANCE_PATH = INGEST / "aiid_full.provenance.json"


def discover_latest_snapshot() -> tuple[str, str]:
    """Return (filename, full_url) for the most recent weekly snapshot,
    by parsing the snapshots index page for every backup-<timestamp>.tar.bz2
    link and taking the lexicographically (== chronologically, fixed-width
    YYYYMMDDHHMMSS) greatest one."""
    # Cache key includes today's date so a re-run always re-checks for a
    # newer weekly snapshot (robust_fetch's cache is otherwise "forever" --
    # fine for the immutable tar.bz2 below, wrong for this index page).
    html = robust_fetch(
        SNAPSHOTS_INDEX_URL,
        CACHE / f"snapshots_index_{date.today()}.html",
        min_cache_bytes=1000,
    ).decode("utf-8", errors="replace")
    matches = sorted(set(BACKUP_RE.findall(html)))
    if not matches:
        raise RuntimeError(
            f"No backup-*.tar.bz2 links found on {SNAPSHOTS_INDEX_URL} -- "
            "the sanctioned-channel page shape may have changed; refusing "
            "to guess a URL. Fix the discovery regex, don't hardcode a stale one."
        )
    latest_ts = matches[-1]
    filename = f"backup-{latest_ts}.tar.bz2"
    return filename, f"{R2_BASE}/{filename}"


def load_existing_aiid_ids() -> set[int]:
    """Every AIID incident_id already referenced by any corpus entry
    (via aiid_id or an AIID-<n>[-OECD] source_id), from the CURRENT build
    output. Guarantees this swap never silently drops a previously-present
    AIID incident -- invariant 3."""
    ids: set[int] = set()
    path = DATA / "incidents.json"
    if not path.exists():
        return ids
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ids
    entries = data.get("incidents", []) if isinstance(data, dict) else data
    for e in entries:
        aid = e.get("aiid_id")
        if aid:
            try:
                ids.add(int(aid))
            except (TypeError, ValueError):
                pass
        for s in e.get("source_ids") or []:
            m = re.match(r"^AIID-(\d+)(?:-OECD)?$", str(s))
            if m:
                ids.add(int(m.group(1)))
    return ids


def _parse_json_list(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except json.JSONDecodeError:
        try:
            val = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return []
    if isinstance(val, list):
        return [str(v) for v in val]
    return []


def _prettify_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in re.split(r"[-_]", slug) if w)


def extract_members(tar_bytes: bytes) -> dict[str, bytes]:
    """Pull ONLY the members this script is allowed to touch out of the
    archive. reports.csv / reports.bson / translations/reports.bson are
    never named here and therefore never read -- see the module docstring's
    license-handling point 1."""
    wanted = {
        "mongodump_full_snapshot/incidents.csv",
        "mongodump_full_snapshot/duplicates.csv",
        "mongodump_full_snapshot/classifications_MIT.csv",
        "mongodump_full_snapshot/license.txt",
    }
    out: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:bz2") as tf:
        for member in tf.getmembers():
            if member.name in wanted:
                f = tf.extractfile(member)
                if f is not None:
                    out[member.name] = f.read()
    missing = wanted - out.keys() - {"mongodump_full_snapshot/license.txt"}
    if missing:
        raise RuntimeError(
            f"Snapshot archive is missing expected member(s): {sorted(missing)} "
            "-- the upstream archive layout may have changed; refusing to "
            "proceed with a partial/guessed parse."
        )
    return out


def parse_csv_bytes(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text)))


def index_duplicates(duplicates_rows: list[dict]) -> dict[int, int]:
    dup_true_by_dup: dict[int, int] = {}
    for row in duplicates_rows:
        try:
            dup_true_by_dup[int(row["duplicate_incident_number"])] = int(
                row["true_incident_number"]
            )
        except (KeyError, ValueError):
            continue
    return dup_true_by_dup


def index_mit_classifications(mit_rows: list[dict]) -> dict[int, dict]:
    mit_by_id: dict[int, dict] = {}
    for row in mit_rows:
        try:
            iid = int(row["Incident ID"])
        except (KeyError, ValueError):
            continue
        mit_by_id[iid] = row
    return mit_by_id


def build_entry(
    row: dict,
    mit_by_id: dict[int, dict],
    dup_true_by_dup: dict[int, int],
    existing_ids: set[int],
) -> tuple[dict | None, bool, bool]:
    """Transform one `incidents.csv` row into an output entry (facts + link
    only -- see the module docstring's license-handling points 3/4).

    Returns ``(entry_or_None, is_security_relevant, kept_for_preservation)``.
    ``entry`` is None if the row is dropped (missing required fields, or
    neither security-relevant nor already present in the corpus -- see the
    module docstring's invariant-3 section).

    ``row["description"]`` (AIID's own free-text field) is used ONLY as an
    ephemeral classification signal inside this function and is never
    copied into the returned entry.
    """
    try:
        iid = int(row["incident_id"])
    except (KeyError, ValueError):
        return None, False, False
    title = (row.get("title") or "").strip()
    if not title:
        return None, False, False
    aiid_description = (row.get("description") or "").strip()  # EPHEMERAL: signal only, never persisted below

    date_str = (row.get("date") or "").strip()
    m = re.match(r"^(\d{4})", date_str)
    year = int(m.group(1)) if m else None
    if not year:
        return None, False, False

    signal_entry = {"title": title, "description": aiid_description}
    relevant = is_security_relevant(signal_entry)
    preserved = False
    if relevant:
        keep = True
    elif iid in existing_ids:
        preserved = True
        keep = True
    else:
        keep = False
    if not keep:
        return None, relevant, preserved

    tx = map_taxonomy(signal_entry)
    sev = severity_for(signal_entry)

    deployer = _parse_json_list(row.get("Alleged deployer of AI system", ""))
    developer = _parse_json_list(row.get("Alleged developer of AI system", ""))
    entities = sorted(set(deployer) | set(developer))
    affected = ", ".join(_prettify_slug(e) for e in entities)

    desc_parts = [f"AI Incident Database (AIID) entry #{iid}: {title}."]
    if affected:
        desc_parts.append(f"Alleged deployer/developer: {affected}.")
    desc_parts.append(
        "See the linked AIID entry for full narrative, sourcing, and classification."
    )
    description = " ".join(desc_parts)

    tags = ["aiid"]
    mit_row = mit_by_id.get(iid)
    if mit_row:
        domain = (mit_row.get("Risk Domain") or "").strip()
        if domain:
            slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")
            tags.append(f"mit-risk-domain:{slug}")
    dup_true = dup_true_by_dup.get(iid)
    if dup_true:
        tags.append(f"aiid-duplicate-of:{dup_true}")

    entry = {
        "source_id": f"AIID-{iid}",
        "aiid_id": iid,
        "title": title,
        "date": date_str or str(year),
        "year": year,
        "category": "real-world",
        "description": description,
        "attack_vector": tx["attack_vector"],
        "affected": affected,
        "severity": sev,
        "owasp_llm": tx["owasp_llm"],
        "owasp_asi": tx["owasp_asi"],
        "mitre_atlas": tx["mitre_atlas"],
        "references": [
            {
                "title": f"AIID incident #{iid}",
                "url": f"https://incidentdatabase.ai/cite/{iid}/",
                "type": "report",
            }
        ],
        "tags": tags,
    }
    return entry, relevant, preserved


def main() -> None:
    filename, url = discover_latest_snapshot()
    print(f"AIID sanctioned snapshot: {filename} <- {url}")

    tar_bytes = robust_fetch(url, CACHE / filename, min_cache_bytes=1_000_000, timeout=180)
    sha256 = hashlib.sha256(tar_bytes).hexdigest()
    print(f"  {len(tar_bytes):,} bytes, sha256={sha256}")

    members = extract_members(tar_bytes)
    license_text = members.get("mongodump_full_snapshot/license.txt", b"").decode(
        "utf-8", errors="replace"
    ).strip()
    print(f"  snapshot license.txt: {license_text!r}")

    incidents_rows = parse_csv_bytes(members["mongodump_full_snapshot/incidents.csv"])
    duplicates_rows = parse_csv_bytes(members["mongodump_full_snapshot/duplicates.csv"])
    mit_rows = parse_csv_bytes(members["mongodump_full_snapshot/classifications_MIT.csv"])
    print(
        f"  parsed: {len(incidents_rows)} incidents, "
        f"{len(duplicates_rows)} duplicate-pairs, {len(mit_rows)} MIT classifications"
    )

    dup_true_by_dup = index_duplicates(duplicates_rows)
    mit_by_id = index_mit_classifications(mit_rows)

    existing_ids = load_existing_aiid_ids()
    print(f"  {len(existing_ids)} AIID incident_ids already present in the corpus")

    out: list[dict] = []
    n_security_relevant = 0
    n_kept_for_preservation = 0
    for row in incidents_rows:
        entry, relevant, preserved = build_entry(row, mit_by_id, dup_true_by_dup, existing_ids)
        if relevant:
            n_security_relevant += 1
        if preserved:
            n_kept_for_preservation += 1
        if entry is not None:
            out.append(entry)

    out.sort(key=lambda e: e["aiid_id"])
    if not out:
        sys.exit("[aiid] ERROR: parsed 0 entries; committed snapshot left untouched")
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"Wrote {len(out)} AIID entries -> {OUT_PATH} "
        f"({n_security_relevant} security-relevant, "
        f"{n_kept_for_preservation} preserved-for-continuity)"
    )

    provenance = {
        "source": "AIID official weekly snapshot",
        "snapshots_index_url": SNAPSHOTS_INDEX_URL,
        "snapshot_filename": filename,
        "snapshot_url": url,
        "snapshot_sha256": sha256,
        "snapshot_license_txt": license_text,
        "fetched_at": str(date.today()),
        "members_extracted": sorted(members.keys()),
        "reports_collection_extracted": False,
        "entries_written": len(out),
        "entries_security_relevant": n_security_relevant,
        "entries_preserved_for_continuity": n_kept_for_preservation,
    }
    PROVENANCE_PATH.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote provenance -> {PROVENANCE_PATH}")


if __name__ == "__main__":
    main()
