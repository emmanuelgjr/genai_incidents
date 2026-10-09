"""scripts/fetch_atlas.py -- pull the latest MITRE ATLAS release (the ONE network
step of the ATLAS refresh; everything downstream is offline).

All HTTP goes through ``ingest/common.py`` (robots.txt check, per-host rate
limit, identifying User-Agent) -- nothing here opens a socket itself.

Upstream layout (``mitre-atlas/atlas-data``, verified 2026-10-06):

* ``dist/ATLAS-latest.yaml`` is NOT the release: it is a ~20-byte text pointer
  (``v6/ATLAS-latest.yaml``), which in turn points at ``ATLAS-<release>.yaml``
  inside ``dist/v6/``. This script resolves that chain and fetches the real
  file. (``dist/ATLAS.yaml`` is frozen at format 5.6.0 and is not used.)
* The release's own ``collection.version`` is authoritative; the filename must
  agree with it or the run fails.

Writes (only these):

* ``ingest/atlas/ATLAS-<version>.yaml`` -- the verbatim release (Apache-2.0,
  redistribution covered by docs/SOURCE_LICENSES.md section 3.1; MITRE's
  notice stays attached via NOTICE-DATA).
* ``ingest/atlas/ATLAS.provenance.json`` -- sha256, URLs, pointer chain,
  collection.version / modified-date, retrieval date.

Exactly one release file is kept in ``ingest/atlas/``; a newer pull replaces the
older file (git history is the archive, and the previous release's ids live on
in ``mappings/mitre_atlas.json`` as deprecated records, never deleted).

Usage::

    python scripts/fetch_atlas.py            # fetch latest, write snapshot
    python scripts/fetch_atlas.py --check    # fetch + report only, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from ingest.common import fetch_once  # noqa: E402

SNAPSHOT_DIR = ROOT / "ingest" / "atlas"
PROVENANCE = SNAPSHOT_DIR / "ATLAS.provenance.json"
RAW_BASE = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/"
POINTER = "ATLAS-latest.yaml"
RELEASE_FILE_RE = re.compile(r"^ATLAS-(\d{4}\.\d{2}(?:\.\d+)?)\.yaml$")


def resolve_pointer(fetch=fetch_once) -> tuple[list[str], str]:
    """Follow the text-pointer chain from dist/ATLAS-latest.yaml to a release
    path relative to dist/. Returns (chain, release_relpath)."""
    path = POINTER
    chain: list[str] = []
    for _ in range(4):
        body, _h = fetch(RAW_BASE + path, timeout=60)
        text = body.decode("utf-8", "replace").strip()
        chain.append(f"{path} -> {text if len(text) < 80 else '<content>'}")
        # A pointer is one short line naming a path; the release itself is large.
        if len(body) < 200 and "\n" not in text:
            base = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
            path = base + text
            if RELEASE_FILE_RE.match(path.rsplit("/", 1)[-1]):
                return chain, path
            continue
        return chain, path
    raise RuntimeError(f"ATLAS pointer chain did not terminate: {chain}")


def is_unchanged(sha: str, name: str, snapshot_dir: Path | None = None) -> bool:
    """True when the committed provenance already records this exact release
    (same file name, same sha256) AND the committed file still hashes to it."""
    d = snapshot_dir or SNAPSHOT_DIR
    prov_path = d / PROVENANCE.name
    if not prov_path.is_file() or not (d / name).is_file():
        return False
    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
    except ValueError:
        return False
    on_disk = hashlib.sha256((d / name).read_bytes()).hexdigest()
    return prov.get("file") == name and prov.get("sha256") == sha == on_disk


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fetch and report; write nothing")
    args = ap.parse_args()

    chain, rel = resolve_pointer()
    print("[atlas-fetch] pointer chain:", *chain, sep="\n  ")
    body, _ = fetch_once(RAW_BASE + rel, timeout=180)
    sha = hashlib.sha256(body).hexdigest()

    import yaml
    root = yaml.safe_load(body.decode("utf-8"))
    coll = root["collection"]
    version = str(coll["version"])
    name = rel.rsplit("/", 1)[-1]
    m = RELEASE_FILE_RE.match(name)
    if not m or m.group(1) != version:
        raise SystemExit(f"[atlas-fetch] FAIL: filename {name!r} disagrees with "
                         f"collection.version {version!r}")
    print(f"[atlas-fetch] collection.version={version} modified={coll.get('modified-date')} "
          f"bytes={len(body):,} sha256={sha}")
    if args.check:
        return 0

    if is_unchanged(sha, name):
        # Same release, same bytes as the committed snapshot: write NOTHING (not
        # even a new `fetched` date) so the workflow's change detection sees a
        # clean tree and opens no PR. Dated audits are never regenerated.
        print(f"[atlas-fetch] NO-OP: {name} sha256 matches the committed snapshot; nothing written")
        return 0

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for old in SNAPSHOT_DIR.glob("ATLAS-*.yaml"):
        if old.name != name:
            old.unlink()  # replaced by the newer release; history keeps it
    (SNAPSHOT_DIR / name).write_bytes(body)
    prov = {
        "source": "https://github.com/mitre-atlas/atlas-data",
        "license": "Apache-2.0 (see docs/SOURCE_LICENSES.md section 3.1)",
        "file": name,
        "url": RAW_BASE + rel,
        "sha256": sha,
        "bytes": len(body),
        "collection_version": version,
        "collection_modified_date": str(coll.get("modified-date", "")),
        "format_version": str(root.get("format-version", "")),
        "pointer_chain": chain,
        "fetched": datetime.now(timezone.utc).date().isoformat(),
    }
    PROVENANCE.write_text(json.dumps(prov, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[atlas-fetch] wrote ingest/atlas/{name} + ATLAS.provenance.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
