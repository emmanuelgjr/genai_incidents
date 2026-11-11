#!/usr/bin/env python
"""Export the committed evidence file from the (uncommitted) fetch cache.

  python -I export_evidence.py <cache evidence.json> > fetch-evidence-2026-11-11.json

For every page in d1303a_spec.EVIDENCE the row-linking tokens are RE-CHECKED against the cached page text
(case-insensitive substring); a token that is absent, or a non-200 status, aborts the export (exit 2). `other_fetches` lists
every other URL fetched in the session (flagged pages removed, searched index pages, refused hosts) with status/title only.
Only titles, timestamps, hashes, statuses and matched tokens are written - never page text.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import d1303a_spec as S  # noqa: E402

cache = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = {"fetched_via": "ingest/common.fetch_once (robots, rate limit, identifying User-Agent)",
       "session": "2026-11-11", "checked_pages": [], "other_fetches": []}
bad = []
for url, toks in S.EVIDENCE.items():
    r = cache[url]
    text = (r.get("text") or "").lower()
    miss = [t for t in toks if t.lower() not in text]
    if r.get("status") != 200 or miss:
        bad.append((url, r.get("status"), miss))
    out["checked_pages"].append({"url": url, "status": r.get("status"), "title": r.get("title"),
                                 "fetched_at": r.get("fetched_at"), "sha256": r.get("sha256"),
                                 "tokens_matched": [t for t in toks if t.lower() in text]})
for url, r in sorted(cache.items()):
    if url in S.EVIDENCE:
        continue
    out["other_fetches"].append({"url": url, "status": r.get("status"), "title": r.get("title"),
                                 "fetched_at": r.get("fetched_at"), "sha256": r.get("sha256"),
                                 "error": r.get("error"), "tokens_matched": r.get("matched", []),
                                 "tokens_unmatched": r.get("unmatched", [])})
if bad:
    print("TOKEN/STATUS FAILURES:", json.dumps(bad, indent=1), file=sys.stderr)
    sys.exit(2)
sys.stdout.reconfigure(encoding="utf-8", newline="\n")
print(json.dumps(out, indent=1, ensure_ascii=False))
