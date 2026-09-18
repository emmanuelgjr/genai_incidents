#!/usr/bin/env python3
"""Strip AWS SigV4 query parameters from URLs embedded in ingested text.

WHY THIS EXISTS
---------------
Upstream CVE descriptions sometimes quote a GitHub attachment link verbatim,
and those links are S3 pre-signed URLs carrying `X-Amz-*` query parameters:

    https://objects.githubusercontent.com/...?X-Amz-Algorithm=AWS4-HMAC-SHA256
      &X-Amz-Credential=AKIA...%2F20230627%2Fus-east-1%2Fs3%2Faws4_request
      &X-Amz-Date=20230627T201018Z&X-Amz-Expires=300&X-Amz-Signature=...

`X-Amz-Credential` contains an AWS *access key ID*. That is a public
identifier, not a secret -- the secret never appears in a pre-signed URL,
only a signature derived from it -- and these particular links expired five
minutes after they were issued in 2023. But secret scanners match the
`AKIA` pattern regardless, so GitHub push protection rejects any push that
rewrites a file containing one. That blocked the v2.10.0 release cut.

The query string is also worthless to a reader: a pre-signed URL that has
expired resolves to nothing, and the parameters are noise in a published
dataset. Stripping them keeps the useful part of the link (the object path)
and removes the part that is both dead and scanner-hostile.

SCOPE
-----
Rewrites `ingest/cve_nvd_expanded.json` in place -- the ingest snapshot, so
the cleaned text survives a rebuild rather than being reintroduced from
source on the next `make build`. Only `X-Amz-*` parameters are removed; any
other query parameters on the same URL are preserved, and a URL left with
an empty query string loses its trailing `?`.

Idempotent: running it twice changes nothing the second time.

Usage:
    python scripts/strip_presigned_urls.py            # rewrite in place
    python scripts/strip_presigned_urls.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [ROOT / "ingest" / "cve_nvd_expanded.json"]

# A URL query string containing at least one X-Amz-* parameter. Matched
# against the raw text, which may be markdown, so the URL ends at the first
# character that cannot appear unescaped in one.
_URL_WITH_AMZ = re.compile(
    r"(https?://[^\s<>\"'\)\]]+?)"          # the URL up to its query string
    r"\?([^\s<>\"'\)\]]*X-Amz-[^\s<>\"'\)\]]*)"  # a query containing X-Amz-*
)


def _strip_amz(query: str) -> str:
    """Drop every X-Amz-* parameter, preserving any others in order."""
    kept = [
        part
        for part in query.split("&")
        if part and not part.split("=", 1)[0].startswith("X-Amz-")
    ]
    return "&".join(kept)


def scrub(text: str) -> tuple[str, int]:
    """Return (cleaned_text, number_of_urls_changed)."""
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        base, query = m.group(1), m.group(2)
        remaining = _strip_amz(query)
        count += 1
        return f"{base}?{remaining}" if remaining else base

    return _URL_WITH_AMZ.sub(_sub, text), count


def walk(obj):
    """Recursively scrub every string in a JSON structure."""
    total = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k], n = walk(v)
            total += n
        return obj, total
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i], n = walk(v)
            total += n
        return obj, total
    if isinstance(obj, str):
        return scrub(obj)
    return obj, 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report, do not write")
    args = ap.parse_args()

    grand_total = 0
    for path in TARGETS:
        if not path.exists():
            print(f"[strip-presigned] {path.name}: not present, skipped")
            continue
        original = path.read_text(encoding="utf-8")
        data = json.loads(original)
        data, changed = walk(data)
        grand_total += changed
        if changed and not args.dry_run:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        verb = "would strip" if args.dry_run else "stripped"
        print(f"[strip-presigned] {path.name}: {verb} {changed} pre-signed URL(s)")

    if grand_total == 0:
        print("[strip-presigned] nothing to do (already clean)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
