"""
ingest_avid.py
==============

Pulls the AI Vulnerability Database (``avidml/avid-db``, MIT) over HTTPS and
emits the records that are not already in the corpus.

Output: ingest/wave12_avid.json (+ ingest/wave12_avid.provenance.json)

Channel: the GitHub tarball API (``api.github.com/repos/avidml/avid-db/
tarball/main``, ~2 MB), fetched through ``ingest.common.fetch_once``. No
``git clone``, so no entry in the non-HTTP egress register is needed
(docs/INGESTION_CONDUCT.md, invariant 5); one request replaces ~1,800
per-file raw fetches.

What is emitted, and what is deliberately not (INCLUSION.md):

  * ``CVE Entry`` reports (AVID's CVE-derived reports): kept when the shared
    AI-relevance filter (``scripts/ai_relevance.py``, the same one
    ``ingest_cvelistv5.py`` uses) accepts the affected product or the CVE
    text, AND the CVE is not already in the corpus. Membership is tested on
    cve_ids, source_ids, titles and reference URLs together, never on
    ``CVE-`` source ids alone. A row for a CVE the corpus already holds is
    NOT emitted: folding it in would re-cluster the grandfathered multi-CVE
    entries (INC-13533 and nine others) because an AVID row arrives before
    the NVD rows in merge order, and the WS4-T19 split guard rightly aborts
    such a build (measured 2026-10-03: 10 entries -> 19+ rows). AVID's extra
    value on those rows (an AVID id and link; the SEP taxonomy has no schema
    field) is kept offline as ``avid_cve_crosswalk`` in the provenance file
    for a future, deliberate enrichment mechanism.
  * Any row the merger's own keys (CVE > source id > reference URL > title,
    ``scripts/corpus_overlap.py``) would fold into an existing corpus entry is
    also NOT emitted, for the same reason (measured: AVID-2026-R1535 shares a
    HiddenLayer advisory URL with the grandfathered MindsDB entry INC-03558,
    which the fold would split). Each skipped row is recorded in the
    provenance file with the colliding INC id.
  * ``Third-party Report`` reports (0DIN / Mindgard-style disclosures): kept;
    the description is ORIGINAL deterministic prose from facts, never a sentence
    of the report (not AVID's to license, evaluation section 1B.5 caveat iii).
  * ``LLM Evaluation`` reports: NOT emitted. In the 2026 import these are
    automated per-(model, probe) garak scan results ("The model X was
    evaluated by the Garak LLM Vulnerability scanner using the probe Y"),
    i.e. benchmark runs, which INCLUSION.md section 3 excludes ("Model X
    scores Y on benchmark Z -- not a security event"). ``--include-evaluations``
    opts in.
  * ``reports/review`` (drafts) are never read.

Every emitted row carries the MIT provenance per record
(``content_license`` + ``description_source`` + ``description_provenance``): CVE-class rows
carry the CVE ToU marker (the text is CNA text), the others the MIT marker with original prose.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from ingest.common import fetch_once  # noqa: E402
from ai_relevance import assess  # noqa: E402
from corpus_overlap import CorpusIndex  # noqa: E402
from ingest_cvelistv5 import CVE_TOU_MARKER  # noqa: E402
from merge_and_dedupe import normalize_url  # noqa: E402  (the merger's own URL key)
from ingest_cve_nvd_expanded import infer_attack_vector, map_owasp_and_atlas  # noqa: E402

INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "avid"
OUT_FILE = INGEST / "wave12_avid.json"
PROVENANCE_FILE = INGEST / "wave12_avid.provenance.json"
CORPUS_FILE = ROOT / "data" / "incidents.json"

TARBALL_URL = "https://api.github.com/repos/avidml/avid-db/tarball/main"
AVID_REPO_URL = "https://github.com/avidml/avid-db"
PUBLISHED_DIRS = ("reports/", "vulnerabilities/")
SKIP_DIRS = ("reports/review/", "reports/img/")

MIT_LICENSE_MARKER = {
    "source": "avid",
    "license": "MIT",
    "license_url": "https://github.com/avidml/avid-db/blob/main/LICENSE",
    "attribution": "AI Vulnerability Database (AVID)",
    "attribution_url": "https://avidml.org/",
    "obligations": ["attribution"],
}

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,9}")
AVID_ID_RE = re.compile(r"AVID-\d{4}-[RV]\d{3,4}", re.I)
CLASS_CVE = "CVE Entry"
CLASS_THIRD_PARTY = "Third-party Report"
CLASS_EVAL = "LLM Evaluation"


# ----------------------------------------------------------------------------
# Fetch + unpack
# ----------------------------------------------------------------------------
def fetch_tarball() -> tuple[bytes, str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    body, _ = fetch_once(TARBALL_URL, timeout=120, min_interval=3.0)
    return body, hashlib.sha256(body).hexdigest()


def read_records(tar_bytes: bytes) -> tuple[dict[str, dict], str]:
    """-> ({repo-relative path: parsed JSON}, commit-ish directory suffix)."""
    recs: dict[str, dict] = {}
    commit = ""
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        for m in tar.getmembers():
            if not m.isfile() or "/" not in m.name:
                continue
            top, rel = m.name.split("/", 1)
            commit = commit or top.rsplit("-", 1)[-1]
            if not rel.endswith(".json") or not rel.startswith(PUBLISHED_DIRS):
                continue
            if rel.startswith(SKIP_DIRS):
                continue
            try:
                recs[rel] = json.load(tar.extractfile(m))
            except (ValueError, UnicodeDecodeError):
                print(f"  [warn] unparseable {rel}", flush=True)
    return recs, commit


# ----------------------------------------------------------------------------
# Record -> tolerant-schema row
# ----------------------------------------------------------------------------
def avid_id(rec: dict) -> str:
    md = rec.get("metadata") or {}
    return (md.get("report_id") or md.get("vuln_id") or "").strip()


def classof(rec: dict) -> str:
    return ((rec.get("problemtype") or {}).get("classof") or "").strip()


def _clean(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("‍", "").replace("​", "")).strip()


REASON_RE = re.compile(r"\s*Reason for inclusion in AVID:.*$", re.S | re.I)


def strip_avid_rationale(text: str) -> str:
    """AVID's 2026 bulk import appends a machine-written "Reason for inclusion
    in AVID: ..." paragraph to the CNA text of its CVE reports (213 of the 309
    rows this ingest emits). It is AVID's own after-the-fact justification, not
    part of the CVE record, and not evidence of AI relevance (it argues, for
    example, that Spring4Shell qualifies because Spring may be in a serving
    stack). The description is the CNA text only, and relevance is judged on
    that text and the affected product, never on the rationale."""
    return REASON_RE.sub("", text).strip()


def first_sentences(text: str, limit: int = 300) -> str:
    """Whole sentences up to *limit* chars (at least the first one)."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = parts[0] if parts else text
    for p in parts[1:]:
        if len(out) + 1 + len(p) > limit:
            break
        out += " " + p
    return out if len(out) <= limit + 80 else out[: limit].rsplit(" ", 1)[0] + "..."


def affected_string(rec: dict) -> str:
    aff = rec.get("affects") or {}
    names: list[str] = []
    for a in aff.get("artifacts") or []:
        n = _clean(a.get("name"))
        if n and n.lower() != "n/a" and n not in names:
            names.append(n)
    if not names:
        for d in aff.get("developer") or []:
            d = _clean(d)
            if d and d.lower() != "n/a" and d not in names:
                names.append(d)
    return ", ".join(names[:4])


def product_strings(rec: dict) -> list[str]:
    aff = rec.get("affects") or {}
    out: list[str] = []
    for key in ("developer", "deployer"):
        out += [_clean(x) for x in aff.get(key) or []]
    out += [_clean(a.get("name")) for a in aff.get("artifacts") or []]
    return [x for x in out if x and x.lower() != "n/a"]


def sep_codes(rec: dict) -> list[str]:
    codes = []
    for s in ((rec.get("impact") or {}).get("avid") or {}).get("sep_view") or []:
        m = re.match(r"([SEP]\d{4})", s)
        if m:
            codes.append(m.group(1))
    return sorted(set(codes))


def avid_url(aid: str) -> str:
    return f"https://avidml.org/database/{aid.lower()}/"


def to_row(rec: dict, rel_path: str) -> dict | None:
    aid = avid_id(rec)
    cls = classof(rec)
    if not aid:
        return None
    desc_full = strip_avid_rationale(_clean((rec.get("description") or {}).get("value")))
    ptitle = _clean(((rec.get("problemtype") or {}).get("description") or {}).get("value"))
    cves = sorted(set(CVE_RE.findall(ptitle) + CVE_RE.findall(
        " ".join(r.get("url") or "" for r in rec.get("references") or []))))
    if cls == CLASS_CVE:
        # CVE-derived: the CNA text is the description (CVE ToU permits
        # reproduction); title = its first sentence, like the NVD ingest.
        # AVID's own title when it is informative; for the bulk-imported
        # records it is the generic "Vulnerability CVE-YYYY-N", so fall back
        # to the first sentence of the CNA text.
        if ptitle and not re.match(r"^Vulnerability CVE-\d{4}-\d+$", ptitle):
            title = ptitle
        else:
            title = re.split(r"(?<=[.!?])\s+", desc_full, maxsplit=1)[0] if desc_full else ptitle
        if len(title) > 180:
            title = title[:177] + "..."
        description = desc_full
        category = "vulnerability-disclosure"
    else:
        title = ptitle or desc_full[:120]
        description = "-"   # replaced below by original prose (needs the date)
        category = "vulnerability-disclosure" if cls == CLASS_THIRD_PARTY else "research"
    if not title or not description:
        return None

    published = rec.get("reported_date") or rec.get("published_date") or ""
    year = int(published[:4]) if published[:4].isdigit() else int(rel_path.split("/")[1])
    date_str = published[:7] if len(published) >= 7 else str(year)
    if cls != CLASS_CVE:
        # Third-party report text is not AVID's to license and not ours to
        # copy (docs/SOURCE_LICENSES.md 6.1: facts + link + ORIGINAL summary):
        # deterministic prose from facts only, no sentence of the report.
        host = ""
        for r in rec.get("references") or []:
            m = re.match(r"https?://(?:www\.)?([^/]+)/", (r.get("url") or "") + "/")
            if m:
                host = m.group(1)
                break
        description = (
            f"AVID record {aid} ({cls or 'report'}), reported {date_str}, concerning "
            f"{affected_string(rec) or 'AI systems'}. The disclosure"
            + (f" is published at {host}" if host else " is linked below")
            + "; its text is not reproduced here. The title is the disclosure's own."
        )

    imp = rec.get("impact") or {}
    cvss = imp.get("cvss") or {}
    cwes = sorted({c.get("cweId") for c in imp.get("cwe") or []
                   if (c.get("cweId") or "").startswith("CWE-")})
    vec = infer_attack_vector(f"{title} {description}")
    llm, asi, atlas = ([], [], [])
    if cls == CLASS_CVE:
        llm, asi, atlas = map_owasp_and_atlas(description, vec)

    refs = [{"title": aid, "url": avid_url(aid), "type": "advisory"}]
    seen = {refs[0]["url"]}
    for r in rec.get("references") or []:
        u = (r.get("url") or "").strip()
        if not u.startswith("http") or u in seen:
            continue
        seen.add(u)
        rtype = "cve" if re.search(r"cve\.org|nvd\.nist\.gov", u) else "reference"
        refs.append({"title": _clean(r.get("label")) or u, "url": u, "type": rtype})
        if len(refs) >= 6:
            break

    tags = ["avid", re.sub(r"[^a-z0-9]+", "-", cls.lower()).strip("-") or "avid-record"]
    if cves:
        tags.append("cve")
    if vec != "other":
        tags.append(vec)

    row = {
        "source_id": aid,
        "title": title,
        "date": date_str,
        "year": year,
        "category": category,
        "description": description,
        "attack_vector": vec,
        "affected": affected_string(rec),
        "references": refs,
        "tags": sorted(set(tags)),
        "avid_categories": sep_codes(rec),
    }
    if cls == CLASS_CVE:
        # CNA text, governed by the CVE ToU (SOURCE_LICENSES 6.1/6.2), only
        # delivered via AVID: marker and source say so.
        row.update({"description_provenance": "verbatim", "description_source": "cve-cna-via-avid",
                    "content_license": dict(CVE_TOU_MARKER)})
    else:
        row.update({"description_provenance": "original", "content_license": dict(MIT_LICENSE_MARKER)})
    if cves:
        row["cve_ids"] = cves
    if cvss.get("baseSeverity"):
        row["severity"] = str(cvss["baseSeverity"]).title()
    if isinstance(cvss.get("baseScore"), (int, float)):
        row["cvss_score"] = cvss["baseScore"]
    if isinstance(cvss.get("vectorString"), str):
        row["cvss_vector"] = cvss["vectorString"]
    if cwes:
        row["cwe_ids"] = cwes
    if llm:
        row["owasp_llm"], row["owasp_asi"], row["mitre_atlas"] = llm, asi, atlas
    return row


# ----------------------------------------------------------------------------
# Corpus membership
# ----------------------------------------------------------------------------
def repo_crosswalk(recs: dict[str, dict]) -> dict[str, list[str]]:
    """AVID id -> CVE ids, for EVERY repo record (any class)."""
    out: dict[str, list[str]] = {}
    for rec in recs.values():
        aid = avid_id(rec)
        text = " ".join([_clean(((rec.get("problemtype") or {}).get("description") or {}).get("value"))]
                        + [r.get("url") or "" for r in rec.get("references") or []])
        cves = sorted(set(CVE_RE.findall(text)))
        if aid and cves:
            out[aid] = cves
    return out


def own_page_key(aid: str) -> str:
    return normalize_url(avid_url(aid))


def build(recs: dict[str, dict], corpus: list[dict], *, include_evaluations: bool = False
          ) -> tuple[list[dict], dict, dict]:
    crosswalk_all = repo_crosswalk(recs)
    idx = CorpusIndex(corpus, crosswalk_all)
    stats = {"repo_records": len(recs), "by_class": {}, "skipped_evaluation": 0,
             "skipped_already_in_corpus": 0, "skipped_not_ai_relevant": 0,
             "skipped_unparseable": 0, "skipped_cve_already_in_corpus": 0,
             "skipped_would_merge_into_existing": 0, "emitted": 0,
             "emitted_new_cve": 0, "emitted_no_cve": 0}
    review = {"not_ai_relevant": [], "corpus_avid_ids_absent_from_repo": [],
              "would_merge_into_existing": {}, "avid_cve_crosswalk": {},
              "avid_cve_crosswalk_all": crosswalk_all}
    seen_repo_ids = set()
    rows: list[dict] = []
    for rel in sorted(recs):
        rec = recs[rel]
        aid = avid_id(rec)
        cls = classof(rec)
        seen_repo_ids.add(aid.upper())
        stats["by_class"][cls or "(none)"] = stats["by_class"].get(cls or "(none)", 0) + 1
        if cls == CLASS_EVAL and not include_evaluations:
            stats["skipped_evaluation"] += 1
            continue
        if aid.upper() in idx.avid_ids:
            stats["skipped_already_in_corpus"] += 1
            continue
        row = to_row(rec, rel)
        if row is None:
            stats["skipped_unparseable"] += 1
            continue
        if cls == CLASS_CVE:
            ok, why = assess(row["description"], product_strings(rec))
            if not ok:
                stats["skipped_not_ai_relevant"] += 1
                review["not_ai_relevant"].append({"id": aid, "title": row["title"][:120],
                                                  "affected": row["affected"]})
                continue
        hit = idx.collision(row, skip_urls={own_page_key(aid)})
        if hit:
            kind, inc = hit
            if kind == "cve":
                stats["skipped_cve_already_in_corpus"] += 1
                review["avid_cve_crosswalk"][aid] = {"cves": row.get("cve_ids"), "corpus_entry": inc}
            else:
                stats["skipped_would_merge_into_existing"] += 1
                review["would_merge_into_existing"][aid] = {"key": kind, "corpus_entry": inc}
            continue
        stats["emitted"] += 1
        stats["emitted_new_cve" if row.get("cve_ids") else "emitted_no_cve"] += 1
        rows.append(row)
    review["corpus_avid_ids_absent_from_repo"] = sorted(set(idx.avid_ids) - seen_repo_ids)
    return rows, stats, review


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--include-evaluations", action="store_true",
                    help="also emit the automated garak LLM Evaluation reports (excluded by INCLUSION.md section 3)")
    ap.add_argument("--from-file", metavar="TARBALL", help="use a saved tarball instead of fetching")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.from_file:
        tar_bytes = Path(args.from_file).read_bytes()
        digest = hashlib.sha256(tar_bytes).hexdigest()
    else:
        tar_bytes, digest = fetch_tarball()
    recs, commit = read_records(tar_bytes)
    corpus = json.loads(CORPUS_FILE.read_text(encoding="utf-8"))["incidents"]
    rows, stats, review = build(recs, corpus, include_evaluations=args.include_evaluations)
    print(json.dumps(stats, indent=2))
    print(f"corpus AVID ids absent from the repo: {review['corpus_avid_ids_absent_from_repo']}")
    if args.dry_run:
        return 0
    if not rows:
        print("[error] 0 rows -- refusing to overwrite committed output", flush=True)
        return 1
    OUT_FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PROVENANCE_FILE.write_text(json.dumps({
        "source": AVID_REPO_URL,
        "channel": TARBALL_URL,
        "license": "MIT (Copyright (c) 2022 AI Vulnerability Database (AVID))",
        "repo_commit": commit,
        "tarball_sha256": digest,
        "fetched": date.today().isoformat(),
        "stats": stats,
        "review": review,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows -> {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
