"""Export integrity (v2.13.0 item 8): SHA256SUMS over every served tree and a
``build_manifest.json`` on every distribution channel.

Two artifacts, one module, so the producers cannot drift apart:

* ``build_manifest.json`` -- which build this copy of the data came from::

      {"commit", "built_at", "built_at_basis", "dirty", "version",
       "incident_count", "retracted_count", "disputed_count",
       "landmark_count", "taxonomy_versions"}

  Every count and the taxonomy versions are copied from ``data/stats.json``
  (invariant 6: the one count source); only ``commit``/``built_at``/``dirty``
  come from outside it. Schema: ``schema/build_manifest.schema.json``.

* ``SHA256SUMS`` -- standard ``sha256sum -c`` format, one per served tree,
  covering the STIX bundle (docs/data/incidents.stix.json), the TAXII
  collection files (docs/taxii2/) and the MISP feed (docs/misp/) as well as
  the site data. The manifest is written into the tree BEFORE its sums are
  computed, so the sums cover it too.

DETERMINISM. ``built_at`` is NOT wall-clock time. It is the committer date of
``commit`` (or ``SOURCE_DATE_EPOCH`` when set), with ``built_at_basis`` saying
which. A rebuild of the same commit therefore yields a byte-identical manifest
and byte-identical SHA256SUMS, which is what the byte-exact drift gates need.
The manifest is written only in the export/release steps (Pages deploy,
release-assets, publish, the HF export, ``make integrity``), never by
``make build``: it would otherwise put the commit hash (which cannot contain
itself) into committed files and fail the drift check on every commit.

Usage::

    python scripts/export_integrity.py gen            # every existing served tree
    python scripts/export_integrity.py verify         # fail on any mismatch
    python scripts/export_integrity.py manifest --out PATH
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATS_PATH = ROOT / "data" / "stats.json"
SCHEMA_PATH = ROOT / "schema" / "build_manifest.schema.json"

MANIFEST_NAME = "build_manifest.json"
SUMS_NAME = "SHA256SUMS"

# Served trees and which files each SHA256SUMS covers. docs/data keeps its
# historical "*.json only" rule (the site fetches JSON); the TAXII and MISP
# trees are hashed whole (JSON, csv, README) because a subscriber pulls all of it.
TREES: dict[str, str] = {
    "docs/data": "*.json",
    "docs/taxii2": "*",
    "docs/misp": "*",
}

MANIFEST_KEYS = (
    "commit", "built_at", "built_at_basis", "dirty", "version",
    "incident_count", "retracted_count", "disputed_count", "landmark_count",
    "taxonomy_versions",
)
# Copied verbatim from data/stats.json (everything in the manifest but the
# three build-origin fields).
STATS_KEYS = ("version", "incident_count", "retracted_count", "disputed_count",
              "landmark_count", "taxonomy_versions")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- build_manifest.json ----------------------------------------------------


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def git_commit() -> str | None:
    return _git("rev-parse", "HEAD") or os.environ.get("GITHUB_SHA")


def git_dirty() -> bool:
    """True when a TRACKED file differs from HEAD. Untracked/ignored files are
    the build artifacts themselves, so they do not count."""
    out = _git("status", "--porcelain", "--untracked-files=no")
    return bool(out)


def built_at() -> tuple[str, str]:
    """(RFC 3339 UTC timestamp, basis). Never the wall clock."""
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    if sde:
        ts = dt.datetime.fromtimestamp(int(sde), dt.timezone.utc)
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "source-date-epoch"
    ct = _git("show", "-s", "--format=%ct", "HEAD")
    if ct:
        ts = dt.datetime.fromtimestamp(int(ct), dt.timezone.utc)
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "commit-date"
    raise RuntimeError("cannot determine built_at: no SOURCE_DATE_EPOCH and no git history")


def build_manifest(stats: dict | None = None, commit: str | None = None,
                   built: tuple[str, str] | None = None, dirty: bool | None = None) -> dict:
    stats = stats if stats is not None else json.loads(STATS_PATH.read_text(encoding="utf-8"))
    commit = commit or git_commit()
    if not commit:
        raise RuntimeError("cannot determine commit: not a git checkout and GITHUB_SHA unset")
    ts, basis = built or built_at()
    m = {"commit": commit, "built_at": ts, "built_at_basis": basis,
         "dirty": git_dirty() if dirty is None else dirty}
    for k in STATS_KEYS:
        m[k] = stats[k]
    return {k: m[k] for k in MANIFEST_KEYS}


def write_manifest(path: Path, **kw) -> dict:
    """Write ``build_manifest.json`` (to ``path``, or ``path/build_manifest.json``
    when ``path`` is a directory or has no suffix)."""
    if path.is_dir() or path.suffix == "":
        path.mkdir(parents=True, exist_ok=True)
        path = path / MANIFEST_NAME
    m = build_manifest(**kw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8", newline="\n")
    return m


def validate_manifest(m: dict) -> list[str]:
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(v.iter_errors(m), key=lambda e: list(map(str, e.absolute_path)))]


# --- SHA256SUMS -------------------------------------------------------------


def covered_files(tree: Path, pattern: str) -> list[Path]:
    return sorted(p for p in tree.rglob(pattern) if p.is_file() and p.name != SUMS_NAME)


def write_sums(tree: Path, pattern: str = "*") -> list[str]:
    files = covered_files(tree, pattern)
    if not files:
        raise SystemExit(f"no files matching {pattern!r} under {tree} -- nothing to hash")
    lines = [f"{sha256_of(f)}  {f.relative_to(tree).as_posix()}" for f in files]
    (tree / SUMS_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return lines


def parse_sums(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if line:
            digest, rel = line.split(None, 1)
            out[rel.lstrip("*")] = digest
    return out


def verify_sums(tree: Path, pattern: str = "*") -> list[str]:
    """Per-file errors (never an aggregate): a mismatching digest, a listed file
    that is missing, or a served file the sums do not list."""
    sums = tree / SUMS_NAME
    if not sums.exists():
        return [f"{tree.name}/{SUMS_NAME} does not exist -- run scripts/export_integrity.py gen"]
    listed = parse_sums(sums.read_text(encoding="utf-8"))
    on_disk = {p.relative_to(tree).as_posix() for p in covered_files(tree, pattern)}
    errors = []
    for rel, want in sorted(listed.items()):
        p = tree / rel
        if not p.is_file():
            errors.append(f"{tree.name}/{rel}: listed in {SUMS_NAME} but the file is missing")
        elif (got := sha256_of(p)) != want:
            errors.append(f"{tree.name}/{rel}: SHA-256 mismatch -- sums say {want}, file hashes to {got}")
    for rel in sorted(on_disk - set(listed)):
        errors.append(f"{tree.name}/{rel}: served but not listed in {SUMS_NAME} -- run scripts/export_integrity.py gen")
    return errors


# --- orchestration ----------------------------------------------------------


def existing_trees(root: Path = ROOT) -> list[tuple[Path, str]]:
    return [(root / rel, pat) for rel, pat in TREES.items() if (root / rel).is_dir()]


def gen_all(root: Path = ROOT, **manifest_kw) -> dict[str, int]:
    """Manifest then sums for every served tree that exists. Returns files hashed per tree."""
    out = {}
    for tree, pat in existing_trees(root):
        write_manifest(tree, **manifest_kw)
        out[tree.relative_to(root).as_posix()] = len(write_sums(tree, pat))
    if not out:
        raise SystemExit("none of docs/data, docs/taxii2, docs/misp exists -- run the export steps first")
    return out


def verify_all(root: Path = ROOT) -> list[str]:
    errors = []
    trees = existing_trees(root)
    if not trees:
        return ["none of docs/data, docs/taxii2, docs/misp exists -- run the export steps first"]
    for tree, pat in trees:
        errors.extend(verify_sums(tree, pat))
        mp = tree / MANIFEST_NAME
        if not mp.exists():
            errors.append(f"{tree.name}/{MANIFEST_NAME} does not exist")
        else:
            m = json.loads(mp.read_text(encoding="utf-8"))
            errors.extend(f"{tree.name}/{MANIFEST_NAME}: {e}" for e in validate_manifest(m))
            errors.extend(f"{tree.name}/{MANIFEST_NAME}: {e}" for e in manifest_vs_stats(m))
    return errors


def manifest_vs_stats(m: dict, stats: dict | None = None) -> list[str]:
    """A shipped manifest's counts and taxonomy versions must equal data/stats.json
    (invariant 6). Sums prove the file is the one that was generated; this proves
    what was generated still says what stats.json says."""
    stats = stats if stats is not None else json.loads(STATS_PATH.read_text(encoding="utf-8"))
    return [f"{k} is {m.get(k)!r} but data/stats.json says {stats.get(k)!r}"
            for k in STATS_KEYS if m.get(k) != stats.get(k)]


def summary(root: Path = ROOT) -> str:
    return ", ".join(
        f"{t.relative_to(root).as_posix()} ({len(parse_sums((t / SUMS_NAME).read_text(encoding='utf-8')))} files)"
        for t, _ in existing_trees(root))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gen")
    sub.add_parser("verify")
    mp = sub.add_parser("manifest")
    mp.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "gen":
        for tree, n in gen_all().items():
            print(f"[export-integrity] {tree}: {MANIFEST_NAME} + {SUMS_NAME} over {n} file(s)")
        return 0
    if args.cmd == "manifest":
        m = write_manifest(args.out)
        print(f"[export-integrity] wrote {args.out}: commit {m['commit'][:12]} built_at {m['built_at']}")
        return 0
    errors = verify_all()
    if errors:
        print("::error::export integrity check failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[export-integrity] clean: " + summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
