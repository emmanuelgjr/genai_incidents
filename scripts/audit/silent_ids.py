"""v2.13.0 item 4: re-derive the published IDs that answer with silence, what
each meant in each release, and the field-level data delta of this change.

Independent of the package: the resolver here is a separate walk over the raw
JSON read from a git ref, not ``genai_incidents.resolve_id``, so it can check
the package rather than echo it (working agreement 6).

    # the 17 at the base, with what each ID meant per release
    python scripts/audit/silent_ids.py silent --ref 816b9271

    # the same walk over the working tree (expect: 6 ambiguous, 0 unrecorded)
    python scripts/audit/silent_ids.py silent --ref WORKTREE

    # field-level delta of data/ + the package copies, base vs working tree
    python scripts/audit/silent_ids.py delta --base 816b9271 \\
        --out-json docs/audits/ID-silent-ids-delta-2026-10-09.json

"Published" = live in ``data/incidents.json`` at any ``v*`` tag. "Silent" =
the single-ID walk ends neither at one live entry nor at an ``into: null``
record: either the chain fans out (``ambiguous``) or the ID has no record at
all (``unrecorded``).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILES = [
    "data/incidents.json",
    "data/incidents.min.json",
    "data/id_deprecations.json",
    "data/stats.json",
    "data/source_freshness.json",
    "data/curation_overrides.json",
    "data/issue88_remediation.json",
    "src/genai_incidents/data/id_deprecations.json",
    "src/genai_incidents/data/incidents.min.json",
    "src/genai_incidents/data/taxonomy_versions.json",
]


def _git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def read(ref: str, path: str) -> bytes | None:
    if ref == "WORKTREE":
        p = ROOT / path
        return p.read_bytes() if p.exists() else None
    try:
        return _git("show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None


def _incidents(raw: bytes) -> list[dict]:
    d = json.loads(raw)
    return d["incidents"] if isinstance(d, dict) else d


def release_tags() -> list[str]:
    tags = _git("tag", "-l", "v*").decode().split()
    return sorted(tags, key=lambda t: tuple(int(x) for x in t[1:].split(".")))


def published() -> dict[str, list[tuple[str, str]]]:
    """id -> [(tag, title), ...] over every release tag."""
    out: dict[str, list[tuple[str, str]]] = {}
    for t in release_tags():
        for e in _incidents(read(t, "data/incidents.json")):
            out.setdefault(e["id"], []).append((t, e.get("title") or ""))
    return out


def walk(inc_id: str, live: set[str], records: list[dict]) -> str:
    """'live' | 'single' | 'withdrawn' | 'ambiguous' | 'unrecorded'.
    Unscoped last-record-wins; a one-element list is a single hop."""
    latest: dict[str, object] = {}
    for r in records:
        if "valid_for_releases" not in r:
            latest[r["from"]] = r.get("into", None)
    if inc_id in live:
        return "live"
    if inc_id not in latest:
        return "unrecorded"
    cur: object = inc_id
    seen: set[str] = set()
    while isinstance(cur, str) and cur not in live:
        if cur in seen or cur not in latest:
            return "ambiguous"
        seen.add(cur)
        nxt = latest[cur]
        if nxt is None:
            return "withdrawn"
        if isinstance(nxt, list):
            if len(nxt) != 1:
                return "ambiguous"
            nxt = nxt[0]
        cur = nxt
    return "single"


def cmd_silent(ref: str) -> int:
    live_rows = _incidents(read(ref, "data/incidents.json"))
    live = {e["id"] for e in live_rows}
    title_holders: dict[str, list[str]] = {}
    for e in live_rows:
        title_holders.setdefault(e.get("title") or "", []).append(e["id"])
    records = json.loads(read(ref, "data/id_deprecations.json"))["deprecations"]
    pub = published()
    froms = {r["from"] for r in records}
    silent = {}
    for i in sorted(set(pub) | froms):
        k = walk(i, live, records)
        if k in ("ambiguous", "unrecorded"):
            silent[i] = k
    print(f"ref {ref}: {len(pub)} published IDs; {len(silent)} silent "
          f"({sum(v == 'ambiguous' for v in silent.values())} ambiguous, "
          f"{sum(v == 'unrecorded' for v in silent.values())} unrecorded)")
    for i, k in silent.items():
        print(f"  {i}  {k}")
        by_title: dict[str, list[str]] = {}
        for tag, title in pub.get(i, []):
            by_title.setdefault(title, []).append(tag)
        for title, tags in by_title.items():
            holders = title_holders.get(title, [])
            print(f"      {tags[0]}..{tags[-1]} ({len(tags)} tags): {title[:70]!r} "
                  f"-> live title holder(s) at {ref}: {holders or 'none'}")
    return 0


def _norm(b: bytes | None):
    return None if b is None else json.loads(b)


def cmd_delta(base: str, out_json: str | None) -> int:
    report: dict = {"base": base, "after": "WORKTREE", "files": {}}
    for path in DATA_FILES:
        before, after = read(base, path), read("WORKTREE", path)
        entry: dict = {"byte_identical": before == after}
        if before != after and path.endswith("id_deprecations.json"):
            b, a = _norm(before)["deprecations"], _norm(after)["deprecations"]
            entry["records_before"] = len(b)
            entry["records_after"] = len(a)
            entry["existing_records_unchanged"] = a[: len(b)] == b
            entry["appended"] = a[len(b):]
            tail = b"\n  ]\n}"
            entry["byte_prefix_preserved"] = bool(
                before.endswith(tail) and after.startswith(before[: -len(tail)])
            )
        elif before != after and path.endswith(("incidents.json", "incidents.min.json")):
            bi = {e["id"]: e for e in _incidents(before)}
            ai = {e["id"]: e for e in _incidents(after)}
            moved = {}
            for i in set(bi) | set(ai):
                x, y = bi.get(i), ai.get(i)
                if x != y:
                    keys = set(x or {}) | set(y or {})
                    moved[i] = sorted(k for k in keys if (x or {}).get(k) != (y or {}).get(k))
            entry["ids_added"] = sorted(set(ai) - set(bi))
            entry["ids_removed"] = sorted(set(bi) - set(ai))
            entry["entries_with_moved_fields"] = moved
            eb, ea = _norm(before), _norm(after)
            if isinstance(eb, dict):
                entry["envelope_keys_changed"] = sorted(
                    k for k in set(eb) | set(ea)
                    if k != "incidents" and eb.get(k) != ea.get(k)
                )
        report["files"][path] = entry
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if out_json:
        Path(ROOT / out_json).write_text(text, encoding="utf-8", newline="\n")
    for path, e in report["files"].items():
        extra = ""
        if "appended" in e:
            extra = (f" records {e['records_before']}->{e['records_after']}, existing "
                     f"unchanged={e['existing_records_unchanged']}, byte prefix "
                     f"preserved={e['byte_prefix_preserved']}")
        if "entries_with_moved_fields" in e:
            extra = f" moved entries={len(e['entries_with_moved_fields'])}"
        print(f"{path}: byte_identical={e['byte_identical']}{extra}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("silent")
    s.add_argument("--ref", default="WORKTREE")
    d = sub.add_parser("delta")
    d.add_argument("--base", required=True)
    d.add_argument("--out-json")
    a = ap.parse_args(argv)
    if a.cmd == "silent":
        return cmd_silent(a.ref)
    return cmd_delta(a.base, a.out_json)


if __name__ == "__main__":
    sys.exit(main())
