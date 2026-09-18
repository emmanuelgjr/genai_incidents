"""WS6-T5 -- CI gate: docs/data/SHA256SUMS must match the files it lists,
byte for byte, and must list every JSON file actually served under
docs/data/.

Named failing input (Agreement 6): any one byte changed in any file listed
in the manifest (a bad mirror, a partial write, truncation, a build step
that ran out of order) -- OR a data file present under docs/data/ that the
manifest doesn't mention (a new shard added to gen_docs_core_data.py without
regenerating the manifest). Both are checked per-file, not as an aggregate,
so one bad file among thousands still fails the build with its own name in
the output rather than being averaged away.

Run: python scripts/verify_data_integrity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from gen_data_integrity import DOCS_DATA, MANIFEST, sha256_of


def main() -> int:
    if not MANIFEST.exists():
        print(f"::error::{MANIFEST} does not exist -- run scripts/gen_data_integrity.py")
        return 1

    manifest_entries: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(None, 1)
        manifest_entries[rel] = digest

    errors: list[str] = []

    on_disk = {p.relative_to(DOCS_DATA).as_posix() for p in DOCS_DATA.rglob("*.json") if p.is_file()}
    on_disk.discard(MANIFEST.name)  # the manifest doesn't hash itself

    for rel, expected in sorted(manifest_entries.items()):
        path = DOCS_DATA / rel
        if not path.exists():
            errors.append(f"{rel}: listed in SHA256SUMS but the file is missing")
            continue
        actual = sha256_of(path)
        if actual != expected:
            errors.append(f"{rel}: SHA-256 mismatch -- manifest says {expected}, file hashes to {actual}")

    missing_from_manifest = on_disk - set(manifest_entries)
    for rel in sorted(missing_from_manifest):
        errors.append(f"{rel}: served under docs/data/ but not listed in SHA256SUMS -- run scripts/gen_data_integrity.py")

    if errors:
        print("::error::docs/data/SHA256SUMS is out of sync with the files it should cover:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"[verify-data-integrity] clean: {len(manifest_entries)} file(s) match their published SHA-256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
