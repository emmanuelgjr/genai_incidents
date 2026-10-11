"""WS6-T5 + v2.13.0 item 8 -- CI gate: for every served tree that exists
(docs/data, docs/taxii2, docs/misp) the SHA256SUMS must match the files it
lists byte for byte, must list every file served, and the tree's
build_manifest.json must exist and satisfy schema/build_manifest.schema.json.

Named failing input (Agreement 6): any one byte changed in any listed file
(a bad mirror, a partial write, a build step that ran out of order), a served
file the sums do not mention (a new shard, or an export that ran AFTER the sums
were written), or a manifest that fails its schema. Checked per file, not as an
aggregate, so one bad file among thousands still fails with its own name.

Run: python scripts/verify_data_integrity.py
"""

from __future__ import annotations

import sys

import export_integrity as ei


def main() -> int:
    errors = ei.verify_all()
    if errors:
        print("::error::export integrity check failed (SHA256SUMS / build_manifest.json out of sync):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[verify-data-integrity] clean: " + ei.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
