#!/usr/bin/env python
"""D130-3a: this-session fetch evidence for the references the 29 remove-rows KEEP (foreman rule C).

  python -I kept_refs.py fetch  <cache.json>                 # NETWORK: fetch via ingest.common.fetch_once, accumulate in cache
  python -I kept_refs.py export <cache.json> > kept-evidence-2026-11-11.json   # offline: classify + write committed file
  python -I kept_refs.py plan                                 # offline: print what would be fetched

Rule as applied: on a changed row with <= 15 kept references, EVERY kept reference is fetched; on a larger row a deterministic
sample is fetched: the first 5 and the last 5 references in row order plus 5 chosen from the rest by random.Random(<row id>).sample.
nvd.nist.gov/vuln/detail/<CVE> and osv.dev/vulnerability/<ID> are JavaScript shells, so the same record is fetched from the NVD
2.0 API (7 s per request, the unauthenticated NVD limit) / the OSV API; the committed record names both URLs.
Outcome per reference: evidenced (HTTP 200 and an identifying token is in the page; match_kind id|keyword), dead-or-blocked
(non-200, robots refusal or error: kept, listed for WS4 link-health), page-without-token (HTTP 200, no token: kept, listed
for review). Only titles, statuses, hashes and matched tokens are committed, never page text.
"""
import hashlib, json, random, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE.parent / "reference-audit-2026-10-15"))
import d1303a_spec as S  # noqa: E402

KEYWORDS = {
    "INC-00021": ["Trezor"], "INC-01194": ["Sixth"], "INC-01348": ["LlamaIndex", "llama_index", "llama-index"],
    "INC-01553": ["Ollama"], "INC-01724": ["Raytha"], "INC-02076": ["Waymo"], "INC-02150": ["OpenAirInterface"],
    "INC-02347": ["Iocharger"], "INC-02505": ["Dify"], "INC-02516": ["Dify"], "INC-02761": ["ChatGLM"],
    "INC-02800": ["LangChain"], "INC-02864": ["Mattermost"], "INC-03209": ["SesameOp"], "INC-03276": ["Dot"],
    "INC-03292": ["Phoenix"], "INC-03423": ["Monica"], "INC-04285": ["Premium Addons"], "INC-04383": ["MathGPT"],
    "INC-04959": ["TorchServe"], "INC-05009": ["Dependency-Track", "DependencyTrack", "dependency-track"],
    "INC-05421": ["سعود", "خالد"], "INC-05425": ["سعود", "نجران"], "INC-01015": ["Flowise"], "INC-01291": ["LangChain"],
    "INC-01589": ["OpenClaw"], "INC-02471": ["Cursor"], "INC-02871": ["MCP"], "INC-04207": ["Skeleton Key"],
}
ID_RE = re.compile(r"(CVE-\d{4}-\d{4,7}|GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}|PYSEC-\d{4}-\d+)", re.I)


def rows():
    d = json.loads((REPO / "data" / "incidents.json").read_text(encoding="utf-8"))
    return {e["id"]: e for e in d["incidents"]}


def selection(rid, refs):
    urls = [r["url"] for r in refs]
    n = len(urls)
    if n <= 15:
        return "all", list(range(n))
    mid = sorted(random.Random(rid).sample(range(5, n - 5), 5))
    return "sample(first5+last5+5 seeded by row id)", list(range(5)) + mid + list(range(n - 5, n))


def tokens_for(rid, row, url):
    ids = {m.upper() for m in ID_RE.findall(url)} | {c.upper() for c in (row.get("cve_ids") or [])}
    return sorted(ids), KEYWORDS.get(rid, [])


def api_url(url):
    m = re.match(r"https://nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)$", url)
    if m:
        return f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={m.group(1)}", 7.0
    m = re.match(r"https://osv\.dev/vulnerability/([^/?#]+)$", url)
    if m:
        return f"https://api.osv.dev/v1/vulns/{m.group(1)}", 1.0
    return url, 1.0


def plan():
    rs = rows()
    out = []
    for rid in S.REMOVE:
        refs = rs[rid]["references"]
        how, idx = selection(rid, refs)
        out.append((rid, len(refs), how, [refs[i]["url"] for i in idx]))
    return out


def do_fetch(cache_path):
    from ingest import common
    import fetch_evidence as fe  # noqa: E402  (text_of only)
    cache = json.loads(Path(cache_path).read_text(encoding="utf-8")) if Path(cache_path).exists() else {}
    for rid, n, how, urls in plan():
        for u in urls:
            if u in cache:
                continue
            via, gap = api_url(u)
            rec = {"url": u, "fetched_via": via, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                body, hdr = common.fetch_once(via, timeout=40, min_interval=gap)
                ctype = (hdr.get("Content-Type") or "").lower()
                rec.update(status=200, sha256=hashlib.sha256(body).hexdigest())
                if "pdf" in ctype or body[:4] == b"%PDF":
                    rec.update(title=None, text="")
                else:
                    t, text = fe.text_of(body)
                    rec.update(title=t, text=text[:2_000_000])
            except PermissionError as ex:
                rec.update(status="robots-refused", error=str(ex)[:90])
            except Exception as ex:  # noqa: BLE001
                rec.update(status=getattr(ex, "code", None) or "error", error=f"{type(ex).__name__}: {ex}"[:120])
            cache[u] = rec
            Path(cache_path).write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(rid, rec["status"], ascii(u[:100]), flush=True)


def classify(rid, row, url, rec):
    ids, kws = tokens_for(rid, row, url)
    text = (rec.get("text") or "")
    low = text.lower()
    if rec.get("status") != 200:
        return "dead-or-blocked", [], None
    got_id = [t for t in ids if t.lower() in low]
    if got_id:
        return "evidenced", got_id[:3], "id"
    got_kw = [k for k in kws if k.lower() in low]
    if got_kw:
        return "evidenced", got_kw[:3], "keyword"
    return "page-without-token", [], None


def export(cache_path):
    cache = json.loads(Path(cache_path).read_text(encoding="utf-8"))
    rs = rows()
    out = {"fetched_via": "ingest/common.fetch_once (robots, rate limit, identifying User-Agent)", "session": "2026-11-11",
           "rule": ("untouched (kept) references were fetched in full on rows with <= 15 kept references and sampled on larger rows "
                    "(first 5 + last 5 + 5 chosen by random.Random(row id).sample over the rest)"),
           "tally": {}, "rows": {}}
    tally = {"evidenced": 0, "dead-or-blocked": 0, "page-without-token": 0}
    kinds = {"id": 0, "keyword": 0}
    for rid, n, how, urls in plan():
        recs = []
        for u in urls:
            rec = cache[u]
            outc, matched, kind = classify(rid, rs[rid], u, rec)
            tally[outc] += 1
            if kind:
                kinds[kind] += 1
            recs.append({"url": u, "fetched_via": rec["fetched_via"], "status": rec["status"], "title": rec.get("title"),
                         "fetched_at": rec["fetched_at"], "sha256": rec.get("sha256"), "error": rec.get("error"),
                         "outcome": outc, "tokens_matched": matched, "match_kind": kind})
        out["rows"][rid] = {"kept_references": n, "method": how, "fetched": len(recs), "references": recs}
    out["tally"] = {**tally, "match_kind": kinds, "fetched_total": sum(tally.values()),
                    "rows_fully_fetched": sum(1 for r in out["rows"].values() if r["method"] == "all"),
                    "rows_sampled": sorted(k for k, r in out["rows"].items() if r["method"] != "all")}
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "plan":
        for rid, n, how, urls in plan():
            print(rid, n, how[:12], len(urls))
        print(sum(len(u) for *_, u in plan()), "fetches")
    elif cmd == "fetch":
        do_fetch(sys.argv[2])
    elif cmd == "export":
        export(sys.argv[2])
