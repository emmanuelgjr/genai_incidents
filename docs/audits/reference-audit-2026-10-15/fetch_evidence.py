#!/usr/bin/env python
"""D130-2 evidence fetcher. NOT part of the build path: nothing in `make build`
reads its output. Every request goes through ingest.common.fetch_once (robots,
per-host rate limit, identifying UA). Usage:

  python -I fetch_evidence.py <evidence.json> <url> [<token> ...]   # one URL, tokens to look for
  python -I fetch_evidence.py --grep <evidence.json> <regex>        # print short context for a regex (reading aid only)

Results accumulate in <evidence.json> (outside the repo for page text; only
title, fetched_at, sha256, status and matched tokens are committed -- see
`export`).
"""
import hashlib, html, json, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from ingest import common  # noqa: E402


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def text_of(body: bytes):
    t = body.decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    title = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip() if m else None
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return title, re.sub(r"\s+", " ", html.unescape(t))


def fetch(url, tokens, store: Path):
    db = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    rec = {"url": url, "fetched_at": now()}
    try:
        body, hdr = common.fetch_once(url, timeout=40)
        ctype = (hdr.get("Content-Type") or "").lower()
        rec.update(status=200, content_type=ctype, sha256=hashlib.sha256(body).hexdigest())
        if "pdf" in ctype or body[:4] == b"%PDF":
            rec.update(title=None, text="", kind="pdf-not-parsed")
        else:
            title, text = text_of(body)
            rec.update(title=title, text=text[:3_000_000], kind="html")
    except PermissionError as ex:
        rec.update(status="robots-refused", error=str(ex)[:100])
    except Exception as ex:  # noqa: BLE001
        rec.update(status=getattr(ex, "code", None) or "error", error=f"{type(ex).__name__}: {ex}"[:140])
    low = (rec.get("text") or "").lower()
    rec["matched"] = [t for t in tokens if t.lower() in low]
    rec["unmatched"] = [t for t in tokens if t.lower() not in low]
    db[url] = rec
    store.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
    return rec


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "--grep":
        db = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        rx = re.compile(sys.argv[3], re.I)
        for u, r in db.items():
            for m in list(rx.finditer(r.get("text") or ""))[:4]:
                s = r["text"]
                print(u, "::", s[max(0, m.start() - 90): m.end() + 90])
        sys.exit()
    store, url, *tokens = sys.argv[1:]
    r = fetch(url, tokens, Path(store))
    print(r["status"], "|", r.get("title"), "| matched", r["matched"], "| unmatched", r["unmatched"], "|", r.get("error", ""))
