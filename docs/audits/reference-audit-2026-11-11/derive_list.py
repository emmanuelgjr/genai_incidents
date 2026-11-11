#!/usr/bin/env python
"""Derive the D130-3 target list: the R1 rows that D130-2 did not cover, plus the 6 rows it deferred.

Offline and deterministic. Input: data/incidents.json at the base commit 64109452 (git show), never the working tree.
R1 is r1() verbatim from docs/audits/reference-detection-2026-10-14.md (Appendix A), as reused by
docs/audits/reference-audit-2026-10-15/derive_list.py. R2 (arXiv title/id mismatch) needs network text; its 11 flagged
rows are the report's section 8 table "R2 all", reproduced as R2_ROWS. 9 of them are legacy rows (D130-2's); the two
non-legacy ones are INC-04383 (R2 only) and INC-05052 (R2 and R1).

Reconciliation (see reference-audit-2026-11-11.md): the report counted 156 R1-or-R2 rows at 589376db; 30 legacy rows were D130-2's.
156 - 30 = 126 non-legacy rows (125 trip R1, plus INC-04383 which trips R2 only). At 64109452 the same 126 rows are
still flagged (no refresh added or fixed any), so the list
holds 126 + the 6 deferred (INC-01015, 01291, 01589, 02471, 02871, 04207) = 132 rows. Batches: 0 = the 6 deferred;
1..4 = the 126 split in stable ID order (32, 32, 31, 31).

  python -I derive_list.py            # print; exit 1 unless 126 + 6 = 132 rows
  python -I derive_list.py --write    # (re)write list.json
"""
import json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = "64109452"
LEGACY_RE = re.compile(r"^(LEGACY-)?INC-\d+$")
R2_ROWS = {"INC-04142", "INC-03972", "INC-04207", "INC-03004", "INC-03570", "INC-03444",
           "INC-03491", "INC-04067", "INC-03955", "INC-04383", "INC-05052"}
DEFERRED = ["INC-01015", "INC-01291", "INC-01589", "INC-02471", "INC-02871", "INC-04207"]
INDEX_SEGMENTS = {
    "blog", "blogs", "news", "newsroom", "press", "advisories", "advisory", "security-advisories",
    "issues", "research", "resources", "articles", "insights", "engineering", "publications",
    "papers", "security", "legal", "about", "company", "products", "events", "conference",
    "conferences", "docs", "documentation", "home", "index", "en", "en-us", "us", "stories",
    "updates", "archive", "archives", "bulletins", "releases", "reports", "library", "learn",
}
CONF_INDEX_RE = re.compile(r"^/(conference|event|events)/[a-z0-9\-]+/?$", re.I)


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


def derive():
    raw = subprocess.run(["git", "show", f"{BASE}:data/incidents.json"], cwd=REPO, check=True, capture_output=True).stdout
    rows = json.loads(raw.decode("utf-8"))["incidents"]
    by = {e["id"]: e for e in rows}
    out = []
    for e in rows:
        if any(LEGACY_RE.match(s) for s in e["source_ids"]):
            continue
        flagged = [[r["url"], r1(r["url"])] for r in e["references"] if r1(r["url"])]
        if flagged or e["id"] in R2_ROWS:
            rule = "R1+R2" if flagged and e["id"] in R2_ROWS else ("R2" if e["id"] in R2_ROWS else "R1")
            out.append({"id": e["id"], "rule": rule, "flagged": flagged, "quality_tier": e["quality_tier"],
                        "status": e.get("status")})
    out.sort(key=lambda x: x["id"])
    sizes = [32, 32, 31, 31]  # 126 rows
    i = 0
    for b, n in enumerate(sizes, 1):
        for x in out[i:i + n]:
            x["batch"] = b
        i += n
    d = []
    for rid in DEFERRED:
        e = by[rid]
        flagged = [[r["url"], r1(r["url"])] for r in e["references"] if r1(r["url"])]
        d.append({"id": rid, "rule": "R1" if flagged else "R2", "flagged": flagged, "quality_tier": e["quality_tier"],
                  "status": e.get("status"), "batch": 0})
    return d + out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    lst = derive()
    n1 = sum(1 for x in lst if x["batch"] > 0)
    print(len(lst), "rows;", n1, "non-legacy R1/R2;", len(lst) - n1, "deferred;",
          {b: sum(1 for x in lst if x["batch"] == b) for b in range(5)})
    if "--write" in sys.argv:
        (HERE / "list.json").write_text(json.dumps({"base": BASE, "rows": lst}, indent=1, ensure_ascii=False) + "\n",
                                        encoding="utf-8", newline="\n")
    sys.exit(0 if (n1 == 126 and len(lst) == 132) else 1)
