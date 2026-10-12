"""WS6-T5 + v2.13.0 item 8 -- write ``build_manifest.json`` and ``SHA256SUMS`` for
every served tree that exists: docs/data (site data + the STIX bundle),
docs/taxii2 (the static TAXII collection) and docs/misp (the MISP feed).

GitHub Pages has no published SLA (availability or integrity), so the sums are
the integrity story: ``sha256sum -c SHA256SUMS`` inside any of the three
directories verifies a downloaded copy with no site-specific tooling.
docs/app.js fetches docs/data/SHA256SUMS to show an abbreviated hash in the
footer. ORDER MATTERS: run this AFTER the export steps, or the sums will not
cover the STIX/TAXII/MISP files (the pre-v2.13.0 Pages workflow ran it before
export_stix.py, so the live docs/data/SHA256SUMS never listed the STIX bundle).

All logic lives in ``scripts/export_integrity.py``; this entry point keeps the
historical name used by the Makefile and workflows.

Run: python scripts/gen_data_integrity.py
"""

from __future__ import annotations

import sys

import export_integrity as ei

ROOT = ei.ROOT
DOCS_DATA = ROOT / "docs" / "data"
MANIFEST = DOCS_DATA / ei.SUMS_NAME  # historical name: the SHA256SUMS path
sha256_of = ei.sha256_of


def main() -> int:
    for tree, n in ei.gen_all().items():
        print(f"[gen-data-integrity] {tree}: {ei.MANIFEST_NAME} + {ei.SUMS_NAME} over {n} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
