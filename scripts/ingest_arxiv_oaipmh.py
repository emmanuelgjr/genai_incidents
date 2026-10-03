"""
ingest_arxiv_oaipmh.py
======================

Pulls arXiv cs.CR descriptive METADATA (title, authors, ids, abstract,
classification -- CC0 under the arXiv API Terms of Use, footnote 1; never
full text, never e-prints) through arXiv's OAI-PMH endpoint and keeps only the
small subset of papers that demonstrate a concrete attack on a generative-AI
or agentic system, via a deterministic, conservative filter.

Output: ingest/wave12_arxiv.json (+ ingest/wave12_arxiv.provenance.json)

Why OAI-PMH and not the API the Terms of Use name: ``export.arxiv.org``
serves ``User-agent: * / Disallow: /`` and ``ingest.common`` fail-closes on it
(docs/specs/source-expansion-evaluation.md, section 1D.1). ``oaipmh.arxiv.org``
serves no robots.txt (404 == no stated restriction, ingest.common's reading)
and is the sanctioned bulk-metadata channel (info.arxiv.org/help/bulk_data).
The API Terms ask for no more than one request every three seconds on a single
connection; ``ingest.common`` has no Crawl-delay parser, so the interval is
passed explicitly (``MIN_INTERVAL``).

The yield is a CURATION decision, not a pipeline one: unfiltered, cs.CR is
thousands of papers a year and would swamp every statistic. ``select()`` below
is the deterministic feeder; it is deliberately precision-first (see the
module-level vocabulary and docs/audits/wave12-ingest-delta-2026-10-03.md for
the measured yield, the 30-item spot-read and the recall check against the
123 hand-curated rows in ingest/arxiv_incidents.json). Per-paper human
approval is not in this path; the filter's output is committed as the
reviewable artifact and ``make build`` only ever reads that committed file.

Restartable: every OAI-PMH response page is cached under
ingest/_cache/arxiv/ (gitignored).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from ingest.common import fetch_once, url_with_query  # noqa: E402
from corpus_overlap import CorpusIndex  # noqa: E402

INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "arxiv"
OUT_FILE = INGEST / "wave12_arxiv.json"
PROVENANCE_FILE = INGEST / "wave12_arxiv.provenance.json"
CURATED_FILE = INGEST / "arxiv_incidents.json"
CORPUS_FILE = ROOT / "data" / "incidents.json"

OAI_BASE = "https://oaipmh.arxiv.org/oai"
SET_SPEC = "cs:cs:CR"
# arXiv API Terms of Use: "no more than one request every three seconds,
# limit requests to a single connection at a time". This process is single
# threaded; the interval is the documented one.
MIN_INTERVAL = 3.0
NS = {"o": "http://www.openarchives.org/OAI/2.0/", "a": "http://arxiv.org/OAI/arXiv/"}
SOURCE_PREFIX = "ARXIV-"

# ----------------------------------------------------------------------------
# Deterministic selection filter: "a concrete attack on a GenAI/agentic system"
# ----------------------------------------------------------------------------
# A paper is selected only when ALL of:
#   (1) ATTACK IS THE HEADLINE -- the TITLE carries either an unambiguous
#       GenAI-attack term (jailbreak, prompt injection, tool poisoning...) or
#       an attack term TOGETHER WITH a GenAI target term (so "LLMs for
#       vulnerability discovery" -- AI used as a tool -- does not qualify);
#   (2) TARGET -- title+abstract name a generative-AI / agentic system class;
#   (3) CONCRETE -- the ABSTRACT carries real-world evidence: a disclosure /
#       CVE / in-the-wild / bug-bounty statement, a named commercial or
#       production system, remote code execution, or an end-to-end /
#       proof-of-concept attack. This is the clause that cuts ~800 "attack on
#       an LLM" papers a year (measured) to the order of the hand-curated
#       rate; a pure benchmark-setting attack with no real-world claim is
#       exactly what the curated list does not contain.
# and NONE of the exclusions fires (defense / detection / benchmark / survey /
# position / evaluation-only titles, withdrawn papers). Every term list is
# word-bounded. Yield, a 30-item spot-read and recall against the 123
# hand-curated rows are in docs/audits/wave12-ingest-delta-2026-10-03.md.
def _compile(terms: list[str]) -> re.Pattern:
    return re.compile(r"(?<![\w-])(?:" + "|".join(terms) + r")(?![\w-])", re.I)


_UNAMBIGUOUS_TITLE = [
    r"jailbreak\w*", r"prompt[- ]injection\w*", r"injection attacks?",
    r"indirect injection", r"tool[- ]poisoning", r"memory (?:injection|poisoning)",
    r"context poisoning", r"(?:agent|goal) hijack\w*",
]
_ATTACK_TITLE = [
    r"attacks?", r"attacking", r"backdoor\w*", r"poison\w*", r"hijack\w*",
    r"exfiltrat\w*", r"leak\w*", r"steal\w*", r"bypass\w*", r"evad\w+",
    r"trojan\w*", r"takeover", r"exploit\w*", r"red[- ]team\w*", r"hack\w*",
    r"compromis\w+", r"smuggl\w+", r"worm", r"abus\w+", r"misus\w+",
    r"subvert\w*", r"injection",
    r"(?:data|model|training[- ]data|prompt|system[- ]prompt|memorization|privacy|private\w*) extraction",
]
_TARGET = [
    r"llms?", r"large language models?", r"language models?", r"chatgpt",
    r"gpt-?[345]\w*", r"claude", r"gemini", r"copilot", r"cursor", r"codex",
    r"(?:llm|ai|language[- ]model|autonomous|coding|web|gui|computer[- ]use|multimodal|"
    r"multi-agent|tool[- ]using|software|browsing|browser)[- ]agents?",
    r"agentic", r"mcp", r"model context protocol", r"rag",
    r"retrieval[- ]augmented", r"multi-?modal", r"vision[- ]language",
    r"vlms?", r"mllms?", r"lvlms?", r"text-to-image", r"diffusion",
    r"generative", r"chatbots?", r"assistants?", r"coding", r"openclaw",
    r"computer[- ]use",
]
_EXCLUDE_TITLE = [
    r"survey", r"a review", r"systemati[sz]ation", r"sok", r"position",
    r"vision paper", r"taxonomy", r"roadmap", r"landscape", r"tutorial",
    r"benchmark\w*", r"dataset", r"defen[cs]\w*", r"defending", r"mitigat\w+",
    r"detect(?:ing|ion|or|ors)?", r"safeguard\w*", r"protect\w*", r"preventing",
    r"guardrails?", r"certified", r"watermark\w*", r"privacy[- ]preserving",
    r"differential\w*", r"federated", r"authenticat\w+", r"fingerprint\w*",
    r"firewall", r"towards? (?:secure|safe|trustworthy)", r"secur(?:e|ing)",
    r"robust\w*", r"purif\w+", r"unlearning", r"evaluat\w+ (?:of|the)",
    r"measur\w+", r"toolkit", r"framework", r"counter\w*", r"alignment",
    r"formali[sz]\w+", r"threat model\w*", r"prevent\w*", r"hardening",
    r"attribution", r"improving", r"evaluating", r"hackworld",
    # AI used as the attacker's tool against non-AI targets, not an attack on AI
    r"smart[- ]contracts?", r"blockchain", r"defi",
]
# Named systems, recorded in the row's ``affected`` field (not a gate).
_NAMED_SYSTEMS = [
    r"chatgpt", r"gpt-?[345]\w*", r"claude", r"gemini", r"copilot", r"cursor",
    r"bard", r"bing chat", r"llama-?\d*", r"deepseek-?\w*", r"mistral", r"qwen",
    r"midjourney", r"dall-?e", r"stable diffusion", r"openai", r"anthropic",
    r"perplexity", r"langchain", r"autogpt", r"mcp servers?", r"openclaw",
    r"windsurf", r"grok",
]
_CONCRETE_ABSTRACT = (
    r"responsibly disclos|coordinated disclosure|cves?|in the wild|bug bounty|"
    r"vendors? (?:confirmed|acknowledged|patched|fixed|responded)|"
    r"real-world (?:systems|deployments?|applications?|products?|agents?|attacks?)|"
    r"commercial (?:llm|model|system|product|agent)s?|"
    r"production (?:llm|system|agent|deploy)\w*|deployed (?:llm|system|agent)s?|"
    r"zero-day|0-day|proof[- ]of[- ]concept|end-to-end (?:attack|exploit)|"
    r"remote code execution|rce"
)
_EXCLUDE_ABSTRACT = r"^(?:this paper has been )?withdrawn"

UNAMBIGUOUS_RE = _compile(_UNAMBIGUOUS_TITLE)
ATTACK_TITLE_RE = _compile(_ATTACK_TITLE)
TARGET_RE = _compile(_TARGET)
EXCLUDE_TITLE_RE = _compile(_EXCLUDE_TITLE)
NAMED_RE = _compile(_NAMED_SYSTEMS)
CONCRETE_RE = re.compile(_CONCRETE_ABSTRACT, re.I)
EXCLUDE_ABSTRACT_RE = re.compile(_EXCLUDE_ABSTRACT, re.I)


def select(rec: dict) -> tuple[bool, dict]:
    """Deterministic selection. Returns (selected, reasons); *reasons* is
    recorded in the provenance file for every selected paper."""
    title = rec.get("title") or ""
    abstract = rec.get("abstract") or ""
    if EXCLUDE_ABSTRACT_RE.search(abstract[:200]):
        return False, {"excluded": "withdrawn"}
    ex = EXCLUDE_TITLE_RE.search(title)
    if ex:
        return False, {"excluded": f"title:{ex.group(0).lower()}"}
    unamb = UNAMBIGUOUS_RE.search(title)
    attack = ATTACK_TITLE_RE.search(title)
    target_title = TARGET_RE.search(title)
    headline = unamb or (attack and target_title)
    if not headline:
        return False, {"headline": False}
    target = TARGET_RE.findall(f"{title} {abstract}")
    if not target:
        return False, {"target": False}
    concrete = CONCRETE_RE.search(abstract)
    if not concrete:
        return False, {"concrete": False}
    return True, {
        "headline": (unamb or attack).group(0).lower(),
        "target_terms": sorted({x.lower() for x in target})[:6],
        "concrete": concrete.group(0).lower(),
    }


# ----------------------------------------------------------------------------
# OAI-PMH fetch + parse
# ----------------------------------------------------------------------------
def _cache_name(params: dict[str, str]) -> Path:
    key = json.dumps(params, sort_keys=True)
    h = hashlib.sha256(key.encode()).hexdigest()[:12]
    label = params.get("from", "tok") + "_" + h
    return CACHE / f"{label}.xml"


def fetch_page(params: dict[str, str], *, retries: int = 6) -> bytes:
    """One OAI-PMH request (cached). arXiv answers 503 + Retry-After when it
    wants us to slow down; honour it rather than retrying blindly."""
    cache = _cache_name(params)
    if cache.exists() and cache.stat().st_size > 200:
        return cache.read_bytes()
    url = url_with_query(OAI_BASE, params, safe=":")
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            body, _ = fetch_once(url, timeout=120, min_interval=MIN_INTERVAL)
            if b"<error" in body[:2000] and b"noRecordsMatch" not in body[:2000]:
                raise RuntimeError(f"OAI-PMH error response: {body[:400]!r}")
            CACHE.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(body)
            return body
        except PermissionError:
            raise
        except OSError as e:
            # HTTPError and URLError are OSError subclasses; only an HTTP
            # status carries a Retry-After worth honouring.
            last = e
            code = getattr(e, "code", None)
            wait = 10 * attempt
            if code is not None:
                wait = 30
                if code == 503:
                    try:
                        wait = max(int(e.headers.get("Retry-After", "30")), MIN_INTERVAL)
                    except (AttributeError, TypeError, ValueError):
                        wait = 30
                print(f"  [warn] HTTP {code}; waiting {wait}s (attempt {attempt}/{retries})", flush=True)
            else:
                print(f"  [warn] {e}; retry {attempt}/{retries}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"OAI-PMH fetch failed after {retries} attempts: {last}")


def _text(el: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", (el.text or "") if el is not None else "").strip()


def parse_page(xml_bytes: bytes) -> tuple[list[dict], str | None]:
    """Parse one ListRecords page -> (records, resumptionToken|None).
    Deleted headers come back as ``{"id":..., "deleted": True}``."""
    # stdlib ElementTree is not hardened against entity-expansion payloads; a
    # legitimate OAI-PMH response never carries a DTD, so refuse any that does
    # (defusedxml is not a project dependency).
    if b"<!DOCTYPE" in xml_bytes[:4096] or b"<!ENTITY" in xml_bytes[:4096]:
        raise ValueError("OAI-PMH response carries a DTD/entity declaration; refusing to parse")
    root = ET.fromstring(xml_bytes)
    out: list[dict] = []
    for r in root.findall(".//o:record", NS):
        header = r.find("o:header", NS)
        ident = _text(header.find("o:identifier", NS)) if header is not None else ""
        arxiv_id = ident.split("oai:arXiv.org:", 1)[-1]
        if header is not None and header.get("status") == "deleted":
            out.append({"id": arxiv_id, "deleted": True})
            continue
        meta = r.find(".//a:arXiv", NS)
        if meta is None:
            continue
        authors = []
        for au in meta.findall("a:authors/a:author", NS):
            name = f"{_text(au.find('a:forenames', NS))} {_text(au.find('a:keyname', NS))}".strip()
            if name:
                authors.append(name)
        out.append({
            "id": _text(meta.find("a:id", NS)) or arxiv_id,
            "created": _text(meta.find("a:created", NS)),
            "updated": _text(meta.find("a:updated", NS)),
            "title": _text(meta.find("a:title", NS)),
            "abstract": _text(meta.find("a:abstract", NS)),
            "authors": authors,
            "categories": _text(meta.find("a:categories", NS)).split(),
            "license": _text(meta.find("a:license", NS)),
            "doi": _text(meta.find("a:doi", NS)),
        })
    tok = root.find(".//o:resumptionToken", NS)
    token = _text(tok) if tok is not None else ""
    return out, (token or None)


def fetch_record(arxiv_id: str) -> dict | None:
    """One GetRecord (cached). Used only by ``--recall-check``."""
    params = {"verb": "GetRecord", "metadataPrefix": "arXiv", "identifier": f"oai:arXiv.org:{arxiv_id}"}
    try:
        body = fetch_page(params)
    except RuntimeError:
        return None
    recs, _ = parse_page(body.replace(b"<GetRecord>", b"<ListRecords>").replace(b"</GetRecord>", b"</ListRecords>"))
    return recs[0] if recs else None


def recall_check() -> int:
    """Independent-route check of the filter: run ``select`` over the paper
    records of the hand-curated rows in ingest/arxiv_incidents.json (which
    were chosen by a human, not by this filter) and report how many pass."""
    curated = json.loads(CURATED_FILE.read_text(encoding="utf-8"))
    ids = []
    for e in curated:
        m = _SRC_ARXIV_RE.match(e.get("source_id") or "")
        if m:
            ids.append(_strip_version(m.group(1)))
    passed, failed, missing = [], [], []
    for i in ids:
        rec = fetch_record(i)
        if rec is None or rec.get("deleted"):
            missing.append(i)
            continue
        ok, why = select(rec)
        (passed if ok else failed).append((i, rec["title"], why))
    print(f"curated arXiv rows: {len(ids)}; fetched {len(passed) + len(failed)}; "
          f"not in cs.CR set / unavailable {len(missing)}")
    print(f"filter accepts {len(passed)} / {len(passed) + len(failed)} "
          f"= {100 * len(passed) / max(1, len(passed) + len(failed)):.1f}%")
    for i, t, why in failed:
        print(f"  MISS {i} {t[:80]!r} {why}")
    return 0


def harvest(date_from: str, date_until: str | None) -> list[dict]:
    """All cs.CR records with datestamp in [date_from, date_until]."""
    params = {"verb": "ListRecords", "metadataPrefix": "arXiv", "set": SET_SPEC, "from": date_from}
    if date_until:
        params["until"] = date_until
    records: list[dict] = []
    page = 0
    while True:
        body = fetch_page(params)
        recs, token = parse_page(body)
        records.extend(recs)
        page += 1
        print(f"  [oai] page {page}: +{len(recs)} (total {len(records)})", flush=True)
        if not token:
            break
        params = {"verb": "ListRecords", "resumptionToken": token}
    return records


def harvest_chunked(date_from: date, date_until: date, step_days: int = 30) -> list[dict]:
    """Chunked harvest so a failure costs one chunk, and the cache keys stay
    stable across reruns. Chunks overlap by nothing; duplicates are removed
    by id (a record re-datestamped across chunks keeps its latest copy)."""
    by_id: dict[str, dict] = {}
    cur = date_from
    while cur <= date_until:
        end = min(cur + timedelta(days=step_days - 1), date_until)
        print(f"== datestamp {cur} .. {end}", flush=True)
        for rec in harvest(cur.isoformat(), end.isoformat()):
            by_id[rec["id"]] = rec
        cur = end + timedelta(days=1)
    return list(by_id.values())


# ----------------------------------------------------------------------------
# Corpus dedupe + row construction
# ----------------------------------------------------------------------------
_ARXIV_ID_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([a-z\-]+/\d{7}|\d{4}\.\d{4,5})", re.I)
_SRC_ARXIV_RE = re.compile(r"^ARXIV-(.+)$", re.I)


def _strip_version(s: str) -> str:
    return re.sub(r"v\d+$", "", s)


def known_arxiv_ids(corpus: list[dict] | None, curated: list[dict] | None) -> set[str]:
    """arXiv ids already present anywhere in the corpus: source_ids
    (``ARXIV-<id>``), reference URLs and titles -- not source_ids alone (the
    evaluation's gate found CVEs held under non-CVE ids by exactly that
    shortcut)."""
    ids: set[str] = set()
    for e in (corpus or []) + (curated or []):
        for s in (e.get("source_ids") or []) + ([e["source_id"]] if e.get("source_id") else []):
            m = _SRC_ARXIV_RE.match(s)
            if m:
                ids.add(_strip_version(m.group(1)).lower())
        for r in e.get("references") or []:
            for m in _ARXIV_ID_RE.finditer(r.get("url") or ""):
                ids.add(_strip_version(m.group(1)).lower())
    return ids


def _named_systems(text: str) -> list[str]:
    seen: list[str] = []
    for m in NAMED_RE.findall(text):
        k = m.lower()
        if k not in seen:
            seen.append(k)
    return seen[:5]


def to_row(rec: dict, reasons: dict) -> dict:
    created = rec["created"]
    arxiv_id = rec["id"]
    systems = _named_systems(f"{rec['title']} {rec['abstract']}")
    authors = rec.get("authors") or []
    cite = authors[0] + (" et al." if len(authors) > 1 else "") if authors else ""
    return {
        "source_id": f"{SOURCE_PREFIX}{arxiv_id}",
        "title": rec["title"],
        "date": created[:7],
        "year": int(created[:4]),
        "category": "research",
        "description": rec["abstract"],
        "affected": ", ".join(systems),
        "references": [{
            "title": rec["title"] + (f" ({cite})" if cite else ""),
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "type": "paper",
        }],
        "tags": ["arxiv", "auto-selected", "paper"],
        # abstract = arXiv descriptive metadata, CC0 1.0 (API ToU fn. 1)
        "description_provenance": "verbatim",
        "description_source": "arxiv",
    }


def build(records: list[dict], *, since: date, known: set[str], idx: CorpusIndex | None = None
          ) -> tuple[list[dict], dict, list[dict]]:
    rows: list[dict] = []
    selected_log: list[dict] = []
    stats = {"harvested": len(records), "deleted": 0, "created_before_window": 0,
             "not_selected": 0, "already_in_corpus": 0, "would_merge_into_existing": 0,
             "selected_new": 0}
    merges: dict[str, dict] = {}
    for rec in sorted(records, key=lambda r: r["id"]):
        if rec.get("deleted"):
            stats["deleted"] += 1
            continue
        if not rec.get("created") or rec["created"] < since.isoformat():
            stats["created_before_window"] += 1
            continue
        ok, reasons = select(rec)
        if not ok:
            stats["not_selected"] += 1
            continue
        if _strip_version(rec["id"]).lower() in known:
            stats["already_in_corpus"] += 1
            continue
        row = to_row(rec, reasons)
        hit = idx.collision(row) if idx else None
        if hit:
            stats["would_merge_into_existing"] += 1
            merges[rec["id"]] = {"key": hit[0], "corpus_entry": hit[1]}
            continue
        stats["selected_new"] += 1
        rows.append(row)
        selected_log.append({"id": rec["id"], "created": rec["created"], "title": rec["title"],
                             "reasons": reasons})
    stats["_merges"] = merges
    return rows, stats, selected_log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    today = date.today()
    ap.add_argument("--since", default=(today - timedelta(days=365)).isoformat(),
                    help="keep papers CREATED on/after this date (default: 365 days ago); "
                         "also the OAI-PMH datestamp lower bound")
    ap.add_argument("--until", default=today.isoformat(), help="OAI-PMH datestamp upper bound")
    ap.add_argument("--dry-run", action="store_true", help="report yield, write nothing")
    ap.add_argument("--recall-check", action="store_true",
                    help="run the filter over the hand-curated rows' own records and report the pass rate")
    args = ap.parse_args()
    if args.recall_check:
        return recall_check()

    since = date.fromisoformat(args.since)
    until = date.fromisoformat(args.until)
    records = harvest_chunked(since, until)

    corpus = None
    if CORPUS_FILE.exists():
        corpus = json.loads(CORPUS_FILE.read_text(encoding="utf-8")).get("incidents")
    curated = json.loads(CURATED_FILE.read_text(encoding="utf-8")) if CURATED_FILE.exists() else []
    known = known_arxiv_ids(corpus, curated)
    rows, stats, selected_log = build(records, since=since, known=known,
                                      idx=CorpusIndex(corpus or []))
    merges = stats.pop("_merges")
    print(json.dumps(stats, indent=2))

    if args.dry_run:
        return 0
    if not rows:
        print("[error] 0 rows selected -- refusing to overwrite committed output", flush=True)
        return 1
    OUT_FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PROVENANCE_FILE.write_text(json.dumps({
        "source": "arXiv OAI-PMH (oaipmh.arxiv.org), set cs:cs:CR, metadataPrefix=arXiv",
        "licence_of_metadata": "CC0 1.0 (info.arxiv.org/help/api/tou.html, footnote 1)",
        "window": {"created_since": since.isoformat(), "datestamp_until": until.isoformat()},
        "min_interval_seconds": MIN_INTERVAL,
        "stats": stats,
        "would_merge_into_existing": merges,
        "selected": selected_log,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows -> {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
