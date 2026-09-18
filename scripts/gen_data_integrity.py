"""WS6-T5 -- publish SHA-256 checksums for every data file the site serves.

GitHub Pages has no published SLA (availability or integrity) -- see the
plan's acceptance criterion "publish SHA-256 of served data files (integrity
on Pages, since SLA isn't fixable)". This script computes SHA-256 over every
JSON data file under docs/data/ (the full dataset, the trimmed core payload,
and every lazy-loaded per-year detail shard -- see gen_docs_core_data.py)
and writes a standard `sha256sum`-compatible manifest:

    docs/data/SHA256SUMS

Format is exactly what `sha256sum -c SHA256SUMS` expects (hex digest, two
spaces, path relative to the manifest's own directory), so a user can verify
a downloaded copy with a single standard command -- no site-specific tooling
required. docs/app.js also fetches this file to surface an abbreviated hash
+ verify link in the page footer.

Run: python scripts/gen_data_integrity.py  (after gen_docs_core_data.py and
the data mirror step -- see .github/workflows/pages.yml)
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DATA = ROOT / "docs" / "data"
MANIFEST = DOCS_DATA / "SHA256SUMS"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not DOCS_DATA.is_dir():
        raise SystemExit(f"{DOCS_DATA} does not exist -- run the data mirror step first")

    files = sorted(p for p in DOCS_DATA.rglob("*.json") if p.is_file())
    if not files:
        raise SystemExit(f"no .json files found under {DOCS_DATA} -- nothing to hash")

    lines = []
    for f in files:
        rel = f.relative_to(DOCS_DATA).as_posix()
        lines.append(f"{sha256_of(f)}  {rel}")

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[gen-data-integrity] wrote {len(files)} checksum(s) to {MANIFEST.relative_to(ROOT)}")
    for line in lines:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
