"""
ingest_cvelistv5.py
===================

Pulls AI/ML/LLM/agent CVEs from the CVE Program's own record dump
(``CVEProject/cvelistV5``, CVE JSON 5; CVE Terms of Use) and emits those that
pass the shared AI-relevance filter and are not already in the corpus.

Output: ingest/wave12_cvelistv5.json (+ ingest/wave12_cvelistv5.provenance.json)

Channel: the daily baseline asset of the repository's GitHub release
(``*_all_CVEs_at_midnight.zip.zip``, ~620 MB), streamed to disk through
``ingest.common.fetch_to_file`` -- HTTP only, so no ``git clone`` and no entry
in the non-HTTP egress register. The release is discovered through
``api.github.com`` (also ``fetch_once``). The asset is cached under
ingest/_cache/cvelistv5/ (gitignored); its sha256 and the release tag are
recorded in the provenance file, so a committed output can be tied to the
exact dump it came from.

The AI-relevance decision is ``scripts/ai_relevance.py::assess`` -- the same
shared, precision-first filter ``ingest_avid.py`` uses, built on this repo's
existing vocabularies (INCLUSION.md section 4). huntr (``assignerShortName``
``huntr_ai`` / ``@huntr_ai``; the CNA behind the huntr bounty platform) is a
FILTER-AND-TAG inside this script, not a separate source: huntr.com itself
serves no report fields. A huntr-CNA record has to pass the same AI-relevance
test (huntr covers all open-source software, not only AI), and is then tagged
``huntr`` with its bounty URL kept as a reference. Only CVE-record text is
taken.

REJECTED records are never emitted. They are counted (and the AI-matching
ones listed in the provenance file) so the rejected-CVE reconciliation work
can consume them; recording CVE state for existing entries is not done here.

CVEs already in the corpus (cve_ids, source_ids, titles or reference URLs --
not ``CVE-`` source ids alone -- plus the CVEs of AVID-keyed entries per AVID's
repo) are skipped, and so is any record the merger's own keys (reference URL,
title; ``scripts/corpus_overlap.py``) would fold into an existing entry that
holds no CVE: this ingest adds new entries only and changes no existing one.
Skipped-for-merge records are listed with the colliding INC id in the
provenance file.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from ingest.common import fetch_once, fetch_to_file  # noqa: E402
from ai_relevance import assess, WEAK_TOKENS  # noqa: E402
from corpus_overlap import CorpusIndex  # noqa: E402
from ingest_cve_nvd_expanded import infer_attack_vector, map_owasp_and_atlas  # noqa: E402

INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "cvelistv5"
OUT_FILE = INGEST / "wave12_cvelistv5.json"
PROVENANCE_FILE = INGEST / "wave12_cvelistv5.provenance.json"
CORPUS_FILE = ROOT / "data" / "incidents.json"

RELEASES_URL = "https://api.github.com/repos/CVEProject/cvelistV5/releases?per_page=30"
BASELINE_MARKER = "_all_CVEs_at_midnight.zip"

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,9}")
HUNTR_RE = re.compile(r"^(?:@|security@)?huntr(?:_ai|\.dev)?$", re.I)  # exact: "Huntress" is a different CNA
GH_SLUG_RE = re.compile(r"https?://(?:www\.)?github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)")

CVE_TOU_MARKER = {
    "source": "cve",
    "license": "CVE-TOU",
    "license_url": "https://www.cve.org/Legal/TermsOfUse",
    "attribution": "The MITRE Corporation (CVE Program)",
    "attribution_url": "https://www.cve.org/",
    "obligations": ["attribution"],
}


# ----------------------------------------------------------------------------
# Fetch
# ----------------------------------------------------------------------------
def latest_baseline() -> dict:
    body, _ = fetch_once(RELEASES_URL, timeout=60, min_interval=3.0)
    for rel in json.loads(body):
        for a in rel.get("assets") or []:
            if BASELINE_MARKER in a["name"]:
                return {"tag": rel["tag_name"], "published_at": rel["published_at"],
                        "name": a["name"], "url": a["browser_download_url"], "size": a["size"]}
    raise RuntimeError("no *_all_CVEs_at_midnight asset in the latest 30 releases")


def ensure_baseline(info: dict) -> tuple[Path, str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / info["name"]
    if dest.exists() and dest.stat().st_size == info["size"]:
        print(f"  [cache] {dest.name}", flush=True)
        h = hashlib.sha256()
        with dest.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return dest, h.hexdigest()
    print(f"  [fetch] {info['url']} ({info['size']:,} bytes)", flush=True)
    digest, size = fetch_to_file(info["url"], dest, timeout=600, min_interval=3.0)
    if size != info["size"]:
        raise RuntimeError(f"size mismatch: got {size}, release says {info['size']}")
    return dest, digest


def open_inner(outer: Path) -> zipfile.ZipFile:
    """The baseline asset is a zip holding ``cves.zip``; extract it once."""
    inner = CACHE / (outer.name + ".cves.zip")
    if not inner.exists():
        with zipfile.ZipFile(outer) as z, z.open("cves.zip") as src, inner.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    return zipfile.ZipFile(inner)


def iter_records(z: zipfile.ZipFile, min_id_year: int):
    for name in z.namelist():
        m = re.search(r"/CVE-(\d{4})-\d+\.json$", name)
        if not m or int(m.group(1)) < min_id_year:
            continue
        try:
            yield json.loads(z.read(name))
        except ValueError:
            print(f"  [warn] unparseable {name}", flush=True)


# ----------------------------------------------------------------------------
# CVE JSON 5 -> features
# ----------------------------------------------------------------------------
def _en(descs: list[dict] | None) -> str:
    for d in descs or []:
        if str(d.get("lang", "")).lower().startswith("en") and d.get("value"):
            return d["value"]
    return ""


def _cpe_products(cpes: list[str] | None) -> list[str]:
    out = []
    for c in cpes or []:
        bits = c.split(":")
        if len(bits) > 4:
            out += [bits[3], bits[4]]
    return out


def product_strings(rec: dict) -> list[str]:
    cont = rec.get("containers") or {}
    out: list[str] = []
    affected = list((cont.get("cna") or {}).get("affected") or [])
    for adp in cont.get("adp") or []:
        affected += adp.get("affected") or []
    for a in affected:
        out += [a.get("vendor"), a.get("product"), a.get("packageName"), a.get("repo")]
        coll = a.get("collectionURL") or ""
        if coll:
            out.append(re.sub(r"^https?://[^/]+/", "", coll))
        out += _cpe_products(a.get("cpes"))
    for r in (cont.get("cna") or {}).get("references") or []:
        m = GH_SLUG_RE.match(r.get("url") or "")
        if m:
            out.append(f"{m.group(1)}/{m.group(2)}")
    seen, uniq = set(), []
    for s in out:
        s = (s or "").strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            uniq.append(s)
    return uniq


def cvss_of(rec: dict) -> dict:
    cont = rec.get("containers") or {}
    blocks = [(cont.get("cna") or {}).get("metrics") or []]
    for adp in cont.get("adp") or []:
        blocks.append(adp.get("metrics") or [])
    for metrics in blocks:
        for m in metrics:
            for key in ("cvssV3_1", "cvssV3_0", "cvssV4_0"):
                c = m.get(key)
                if c and isinstance(c.get("baseScore"), (int, float)):
                    return {"score": c["baseScore"], "vector": c.get("vectorString"),
                            "severity": str(c.get("baseSeverity") or "").title() or None}
    return {}


def cwes_of(rec: dict) -> list[str]:
    out = set()
    for pt in ((rec.get("containers") or {}).get("cna") or {}).get("problemTypes") or []:
        for d in pt.get("descriptions") or []:
            cid = d.get("cweId") or ""
            if re.match(r"^CWE-\d{1,4}$", cid):
                out.add(cid)
    return sorted(out)


def affected_string(rec: dict) -> str:
    parts: list[str] = []
    for a in ((rec.get("containers") or {}).get("cna") or {}).get("affected") or []:
        v, p = (a.get("vendor") or "").strip(), (a.get("product") or a.get("packageName") or "").strip()
        if not p or p.lower() in ("n/a", "unspecified"):
            continue
        s = f"{v}/{p}" if v and v.lower() not in ("n/a", "unspecified") and v.lower() != p.lower() else p
        if s not in parts:
            parts.append(s)
        if len(parts) >= 4:
            break
    return ", ".join(parts)


def is_huntr(rec: dict) -> bool:
    meta = rec.get("cveMetadata") or {}
    return bool(HUNTR_RE.search(meta.get("assignerShortName") or ""))


def to_row(rec: dict, why: dict) -> dict | None:
    meta = rec["cveMetadata"]
    cve_id = meta["cveId"]
    cna = (rec.get("containers") or {}).get("cna") or {}
    desc = re.sub(r"\s+", " ", _en(cna.get("descriptions"))).strip()
    if not desc:
        return None
    first = re.split(r"(?<=[.!?])\s+", desc, maxsplit=1)[0]
    title = re.sub(r"\s+", " ", cna.get("title") or "").strip() or first
    if len(title) > 180:
        title = title[:177] + "..."
    published = meta.get("datePublished") or ""
    year = int(published[:4]) if published[:4].isdigit() else int(cve_id.split("-")[1])

    vec = infer_attack_vector(desc)
    llm, asi, atlas = map_owasp_and_atlas(desc, vec)
    huntr = is_huntr(rec)

    refs = [{"title": "NVD", "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}", "type": "advisory"},
            {"title": "CVE Record", "url": f"https://www.cve.org/CVERecord?id={cve_id}", "type": "cve"}]
    seen = {r["url"] for r in refs}
    cna_refs = cna.get("references") or []
    # keep the huntr bounty link first among the CNA references
    cna_refs = sorted(cna_refs, key=lambda r: 0 if "huntr." in (r.get("url") or "") else 1)
    for r in cna_refs:
        u = (r.get("url") or "").strip()
        if not u.startswith("http") or u in seen:
            continue
        seen.add(u)
        tags = [t.lower() for t in (r.get("tags") or [])]
        if "huntr." in u:
            rtype = "disclosure"
        elif "vendor-advisory" in tags:
            rtype = "vendor"
        elif "patch" in tags:
            rtype = "patch"
        elif "exploit" in tags:
            rtype = "exploit"
        else:
            rtype = "reference"
        refs.append({"title": r.get("name") or u, "url": u, "type": rtype})
        if len(refs) >= 7:
            break

    tag_set = {"cve", "cvelistv5"}
    if huntr:
        tag_set.add("huntr")
    if vec != "other":
        tag_set.add(vec)

    row = {
        "source_id": cve_id,
        "cve_id": cve_id,
        "title": title,
        "date": published[:7],
        "year": year,
        "category": "vulnerability-disclosure",
        "description": desc,
        "attack_vector": vec,
        "affected": affected_string(rec),
        "owasp_llm": llm,
        "owasp_asi": asi,
        "mitre_atlas": atlas,
        "references": refs,
        "tags": sorted(tag_set),
        "description_provenance": "verbatim",
        "description_source": "cvelistv5",
        # machine-ingested, no human review (D43): explicit `auto`; the merger would
        # otherwise class it `reviewed` (AVID- prefix / CVSS-scored CVE rule)
        "quality_tier": "auto",
        "content_license": dict(CVE_TOU_MARKER),
    }
    cv = cvss_of(rec)
    if cv.get("score") is not None:
        row["cvss_score"] = cv["score"]
        if cv.get("vector"):
            row["cvss_vector"] = cv["vector"]
        if cv.get("severity"):
            row["severity"] = cv["severity"]
    cw = cwes_of(rec)
    if cw:
        row["cwe_ids"] = cw
    return row


# ----------------------------------------------------------------------------
# Corpus membership
# ----------------------------------------------------------------------------
def load_avid_crosswalk() -> dict[str, list[str]]:
    """AVID id -> CVE ids from the AVID ingest's provenance file (run
    ``make ingest-avid`` first); lets an AVID-keyed corpus entry stand for its
    CVE even when the entry's own text never names it."""
    p = INGEST / "wave12_avid.provenance.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("review", {}).get("avid_cve_crosswalk_all", {})


_WEAK_RES = [re.compile(r"(?<![A-Za-z0-9])" + re.escape(t.strip()) + r"(?![A-Za-z0-9])", re.I)
             for t in WEAK_TOKENS if t.strip()]


def weak_signal(desc: str) -> bool:
    return any(r.search(desc) for r in _WEAK_RES)


def build(records, idx: CorpusIndex, *, since: str, backlog_end: str):
    stats = collections.Counter()
    window = {"backlog": collections.Counter(), "post_backlog": collections.Counter()}
    rows: list[dict] = []
    rejected_ai: list[dict] = []
    candidates: collections.Counter = collections.Counter()
    huntr_total = collections.Counter()
    merges: dict[str, dict] = {}
    for rec in records:
        meta = rec.get("cveMetadata") or {}
        cve_id = meta.get("cveId") or ""
        pub = meta.get("datePublished") or ""
        state = meta.get("state")
        if not cve_id or not pub or pub[:10] < since:
            stats["outside_window"] += 1
            continue
        w = "backlog" if pub[:10] <= backlog_end else "post_backlog"
        stats["in_window"] += 1
        window[w]["in_window"] += 1
        huntr = is_huntr(rec)
        if huntr:
            huntr_total[w + "_in_window"] += 1
        cna = (rec.get("containers") or {}).get("cna") or {}
        desc = _en(cna.get("descriptions"))
        prods = product_strings(rec)
        ok, why = assess(desc, prods, meta.get("assignerShortName"))
        if state != "PUBLISHED":
            stats["not_published"] += 1
            if ok:
                stats["rejected_ai_match"] += 1
                rejected_ai.append({"cve": cve_id, "state": state, "assigner": meta.get("assignerShortName")})
            continue
        if not ok:
            if weak_signal(desc):
                key = next((p for p in prods if p.lower() not in ("n/a", "unspecified")), "(no product)")
                candidates[key.lower()] += 1
            continue
        stats["ai_relevant_published"] += 1
        window[w]["ai_relevant"] += 1
        if huntr:
            huntr_total[w + "_ai_relevant"] += 1
        row = to_row(rec, why)
        if row is None:
            stats["no_english_description"] += 1
            continue
        hit = idx.collision(row)
        if hit and hit[0] == "cve":
            stats["already_in_corpus"] += 1
            window[w]["already_in_corpus"] += 1
            if huntr:
                huntr_total[w + "_already_in_corpus"] += 1
            continue
        if hit:
            # the merger would fold this CVE record into an existing entry
            # that holds no CVE (a GHSA-only advisory, an AVID row, a write-up)
            stats["would_merge_into_existing"] += 1
            window[w]["would_merge_into_existing"] += 1
            merges[cve_id] = {"key": hit[0], "corpus_entry": hit[1]}
            continue
        rows.append(row)
        stats["emitted"] += 1
        window[w]["emitted"] += 1
        if huntr:
            huntr_total[w + "_emitted"] += 1
        row["_why"] = why
    return rows, stats, window, huntr_total, rejected_ai, candidates, merges


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default="2024-01-01", help="datePublished lower bound (default 2024-01-01)")
    ap.add_argument("--backlog-end", default="2026-06-30",
                    help="last day of the evaluated backlog window; later records are reported as post-window")
    ap.add_argument("--from-file", metavar="OUTER_ZIP", help="use a saved baseline asset instead of fetching")
    ap.add_argument("--release-tag", default="(local file)", help="release tag to record with --from-file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.from_file:
        outer = Path(args.from_file)
        h = hashlib.sha256()
        with outer.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        info, digest = {"tag": args.release_tag, "name": outer.name, "published_at": ""}, h.hexdigest()
    else:
        info = latest_baseline()
        outer, digest = ensure_baseline(info)
    z = open_inner(outer)
    corpus = json.loads(CORPUS_FILE.read_text(encoding="utf-8"))["incidents"]
    rows, stats, window, huntr_total, rejected_ai, candidates, merges = build(
        iter_records(z, int(args.since[:4]) - 2),
        CorpusIndex(corpus, load_avid_crosswalk()),
        since=args.since, backlog_end=args.backlog_end)
    report = {"stats": dict(stats), "window": {k: dict(v) for k, v in window.items()},
              "huntr": dict(huntr_total)}
    print(json.dumps(report, indent=2))
    if args.dry_run:
        return 0
    why_by_cve = {r["source_id"]: r.pop("_why") for r in rows}
    if not rows:
        print("[error] 0 rows -- refusing to overwrite committed output", flush=True)
        return 1
    rows.sort(key=lambda r: r["source_id"])
    OUT_FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PROVENANCE_FILE.write_text(json.dumps({
        "source": "https://github.com/CVEProject/cvelistV5 (release baseline asset)",
        "license": "CVE Terms of Use (SPDX CVE-TOU), https://www.cve.org/Legal/TermsOfUse",
        "release_tag": info["tag"], "asset": info["name"], "asset_sha256": digest,
        "fetched": date.today().isoformat(),
        "window": {"since": args.since, "backlog_end": args.backlog_end},
        **report,
        "rejected_ai_matching": rejected_ai,
        "would_merge_into_existing": merges,
        "candidates_for_curation": candidates.most_common(80),
        "match_evidence": why_by_cve,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows -> {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
