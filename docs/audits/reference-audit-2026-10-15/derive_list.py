#!/usr/bin/env python
"""Re-derive the 30 legacy-seed rows of D130-2: rows with an INC-<n>/LEGACY-INC-<n> source_id that trip R1 or R2.

R1 is the detection report's r1() verbatim (docs/audits/reference-detection-2026-10-14.md, Appendix A), run
offline on data/incidents.json at the base commit. R2 needs the arXiv abs-page metadata the report fetched
(network, 12 minutes); its 11 flagged rows are the report's section 8 table "R2 all", reproduced here, so this
script is offline and deterministic. Prints the count and the list; exit 1 if the count is not 30.
"""
import json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[3]
LEGACY_RE = re.compile(r"^(LEGACY-)?INC-\d+$")
INDEX_SEGMENTS = {
    "blog", "blogs", "news", "newsroom", "press", "advisories", "advisory", "security-advisories",
    "issues", "research", "resources", "articles", "insights", "engineering", "publications",
    "papers", "security", "legal", "about", "company", "products", "events", "conference",
    "conferences", "docs", "documentation", "home", "index", "en", "en-us", "us", "stories",
    "updates", "archive", "archives", "bulletins", "releases", "reports", "library", "learn",
}
CONF_INDEX_RE = re.compile(r"^/(conference|event|events)/[a-z0-9\-]+/?$", re.I)
R2_ROWS = {"INC-04142", "INC-03972", "INC-04207", "INC-03004", "INC-03570", "INC-03444",
           "INC-03491", "INC-04067", "INC-03955", "INC-04383", "INC-05052"}


def segs(url):
    return [s for s in urlparse(url).path.split("/") if s]


def slug_like(seg):
    return (seg.count("-") >= 2 or len(seg) >= 24 or bool(re.search(r"\.(html?|shtml|aspx?|php)$", seg, re.I))
            or bool(re.search(r"\d{5,}", seg)))


def r1(url):
    p = urlparse(url)
    if p.query or p.fragment:
        return None
    s = segs(url)
    if len(s) == 0:
        return "homepage"
    if len(s) == 1 and not slug_like(s[0]):
        return "depth1-non-slug"
    if CONF_INDEX_RE.match(p.path):
        return "conference-index"
    if s[-1].lower() in INDEX_SEGMENTS and all(x.lower() in INDEX_SEGMENTS for x in s):
        return "index-segments"
    return None


raw = subprocess.run(["git", "show", "589376db:data/incidents.json"], cwd=REPO, check=True, capture_output=True).stdout
rows = json.loads(raw.decode("utf-8"))["incidents"]
hit = []
for e in rows:
    if not any(LEGACY_RE.match(s) for s in e["source_ids"]):
        continue
    if e["id"] in R2_ROWS or any(r1(r["url"]) for r in e["references"]):
        hit.append(e)
tiers = {}
for e in hit:
    tiers[e["quality_tier"]] = tiers.get(e["quality_tier"], 0) + 1
print(len(hit), tiers)
for e in sorted(hit, key=lambda e: e["id"]):
    print(e["id"], e["quality_tier"], [s for s in e["source_ids"] if LEGACY_RE.match(s)])
sys.exit(0 if len(hit) == 30 else 1)
