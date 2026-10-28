"""D132: single source of the "release vs main" version label.

Ruling D132 (2026-10-14): a surface must never pair a RELEASE version with
POST-release counts. Between cuts the build therefore emits ``<last-release>+main``
(e.g. ``2.13.0+main``); at a cut it emits the plain version.

How the build knows, deterministically, with no network, no model, no git:

* ``data/last_release.json`` is a COMMITTED marker written at each cut by
  ``scripts/mark_release.py`` from the tagged ``data/incidents.json``. It holds the
  release version, date, the released counts, and ``rows_sha256`` -- the digest
  of the release's ``incidents`` rows (canonical JSON; the ``version``/``generated``
  header is excluded so the digest does not depend on the label it decides).
* The build hashes the current rows the same way. Equal -> the data IS the
  release's data -> plain version. Different -> ``<version>+main``.

Why not ``git describe``: it depends on tags being fetched (shallow CI clones
have none), so the same commit would build to different bytes on different
machines. The marker is a file in the tree, so the build is a pure function of
the tree. The cost is that a cut must run ``mark_release.py``; ``check_stats_drift``
and ``tests/test_release_label.py`` fail if it was forgotten (marker version must
equal the top released CHANGELOG heading) or if it was hand-edited (the test
re-derives it from the tag when the tag is present).

Hashing ROWS rather than comparing counts is deliberate: a swap that keeps every
count equal still changes the digest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER_PATH = ROOT / "data" / "last_release.json"
SUFFIX = "+main"


def rows_digest(incidents: list[dict]) -> str:
    # round-trip so in-memory rows and re-read rows hash identically
    canon = json.dumps(incidents, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def derive_counts(incidents: list[dict]) -> dict:
    standing = [e for e in incidents if e.get("status") not in ("retracted", "unverified")]
    return {
        "incident_count": len(standing),
        "retracted_count": sum(1 for e in incidents if e.get("status") == "retracted"),
        "unverified_count": sum(1 for e in incidents if e.get("status") == "unverified"),
        "disputed_count": sum(1 for e in standing if e.get("status") == "disputed"),
        "landmark_count": sum(1 for e in standing if e.get("tier") == "landmark"),
    }


def load_marker(path: Path = MARKER_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def version_label(incidents: list[dict], marker: dict | None = None) -> str:
    """Plain release version if ``incidents`` are exactly the last release's rows,
    else ``<release>+main``."""
    marker = marker if marker is not None else load_marker()
    if rows_digest(incidents) == marker["rows_sha256"]:
        return marker["version"]
    return marker["version"] + SUFFIX


def base_version(label: str) -> str:
    return label[: -len(SUFFIX)] if label.endswith(SUFFIX) else label
