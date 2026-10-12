"""Assemble the GitHub-release channel of the export set (v2.13.0 item 8).

Reads the already-generated exports (``make stix taxii misp``) and writes to
``dist/release/``::

    incidents.stix.json   the STIX 2.1 bundle (byte-identical to docs/data/)
    incidents.min.json    the slim dataset (byte-identical to data/)
    taxii2.zip            the static TAXII collection (docs/taxii2/)
    misp-feed.zip         the MISP feed (docs/misp/)
    build_manifest.json   commit, built_at, counts, taxonomy_versions
    SHA256SUMS            ``sha256sum -c`` over every file above

The two zips are deterministic for a given zlib: entries sorted by path, fixed
1980-01-01 timestamps, fixed permissions, fixed compression level. The
SHA256SUMS in the release is the only place those archives are checksummed.
``.github/workflows/release-assets.yml`` uploads the directory to the Release.

Run: python scripts/package_release_assets.py [--out DIR]
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

import export_integrity as ei

ROOT = ei.ROOT
OUT = ROOT / "dist" / "release"

# (asset name, source) -- files are copied, directories are zipped.
ASSETS: list[tuple[str, Path]] = [
    ("incidents.stix.json", ROOT / "docs" / "data" / "incidents.stix.json"),
    ("incidents.min.json", ROOT / "data" / "incidents.min.json"),
    ("taxii2.zip", ROOT / "docs" / "taxii2"),
    ("misp-feed.zip", ROOT / "docs" / "misp"),
]
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def deterministic_zip(src_dir: Path, dest: Path) -> int:
    """Zip ``src_dir`` (entries relative to it, SHA256SUMS/build_manifest.json
    of that tree included -- they are part of what a subscriber fetches)."""
    files = sorted(p for p in src_dir.rglob("*") if p.is_file())
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in files:
            zi = zipfile.ZipInfo(f.relative_to(src_dir).as_posix(), ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, f.read_bytes(), compresslevel=6)
    return len(files)


def package(out: Path = OUT, assets: list[tuple[str, Path]] | None = None, **manifest_kw) -> list[str]:
    assets = assets if assets is not None else ASSETS
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name, src in assets:
        if not src.exists():
            raise SystemExit(f"{src} does not exist -- run `make stix taxii misp` first")
        if src.is_dir():
            deterministic_zip(src, out / name)
        else:
            shutil.copyfile(src, out / name)
    ei.write_manifest(out, **manifest_kw)
    return ei.write_sums(out, "*")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    lines = package(args.out)
    print(f"[release-assets] {len(lines)} file(s) in {args.out}:")
    for line in lines:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
