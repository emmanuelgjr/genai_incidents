"""
Ingest the OECD AI Incidents and Hazards Monitor (AIM) corpus.

Source: https://oecd.ai/en/incidents (Angular SPA)
        Sitemap: https://oecd.ai/sitemaps/incident-monitor-sitemap.xml

Each incident page embeds an Angular `<script id="ng-state">` JSON blob with
the full incident record (title, articles, evidences, concepts, aiid_ids,
location, etc.). We scrape pages concurrently with on-disk caching, filter
to security-relevant entries, and emit one ingest file.

Defaults:
  - Fetches the most recent N URLs from the sitemap (newest first).
  - LIMIT defaults to a few thousand; set OECD_AIM_LIMIT=0 to grab all.
  - Pages cached under ingest/_cache/oecd_aim/ so the script is restartable.

Output: ingest/oecd_aim_full_incidents.json
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest.common import fetch_once, robust_fetch  # noqa: E402

# Corpus-classification keyword lists live in merge_and_dedupe.py
# (_SECURITY_KEYWORDS_FOR_CORPUS / _AI_HARM_KEYWORDS) -- imported, not
# duplicated, so this ingest-time classifier and the merge-time one it
# replaces can never drift apart. See classify_corpus_signal() below and
# docs/audits/E21-oecd-narrative-licence-2026-07-30.md §5.1.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_and_dedupe import (  # noqa: E402
    _AI_HARM_KEYWORDS as CORPUS_AI_HARM_KEYWORDS,
    _SECURITY_KEYWORDS_FOR_CORPUS as CORPUS_SECURITY_KEYWORDS,
    classify_attack_vector,
)

INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "oecd_aim"
CACHE.mkdir(parents=True, exist_ok=True)

SITEMAP_URL = "https://oecd.ai/sitemaps/incident-monitor-sitemap.xml"

# Default page cap. Override with OECD_AIM_LIMIT=N (0 = unlimited).
DEFAULT_LIMIT = 3000
MAX_WORKERS = 10

# Security-relevant keyword filter applied to title + summary + evidences.
SECURITY_KEYWORDS = (
    "prompt injection prompt-injection jailbreak jailbroken deepfake voice clone "
    "voice cloning data leak data breach leaked exposed exfiltrat ransomware "
    "phishing vishing smishing rce remote code execution command injection "
    "sandbox escape ssrf sql injection deserialization supply chain model theft "
    "model extraction membership inference adversarial evasion poisoning "
    "backdoor scam fraud imperson spoofed spoofing malware trojan worm "
    "vulnerab exploit hack hijack stole stolen theft unauthorized credential "
    "password api key api-key token hallucina misinform disinform election "
    "influence operation propaganda chatbot fake image fake video synthetic "
    "cyberattack cyber attack cybersecurity csam child sexual abuse "
    "bias discriminat surveillance facial recognition biometric privacy "
    "autonomous weapon killer robot wrongful arrest racial profil "
    "child safety self-harm suicide grooming radicalization weaponize "
    "intellectual property copyright"
).split()

KEYWORD_TO_OWASP: list[tuple[str, list[str], list[str], str]] = [
    ("prompt inject", ["LLM01"], ["ASI01"], "prompt-injection"),
    ("jailbreak", ["LLM01"], ["ASI01"], "jailbreak"),
    ("deepfake", ["LLM07"], ["ASI09"], "deepfake"),
    ("voice clone", ["LLM07"], ["ASI09"], "deepfake"),
    ("imperson", ["LLM07"], ["ASI09"], "other"),
    ("data leak", ["LLM02"], ["ASI03"], "data-exfiltration"),
    ("data breach", ["LLM02"], ["ASI03"], "data-exfiltration"),
    ("exfil", ["LLM02"], ["ASI02"], "data-exfiltration"),
    ("ransomware", [], ["ASI05", "ASI10"], "rce"),
    ("phishing", [], ["ASI09"], "other"),
    ("scam", [], ["ASI09"], "other"),
    ("fraud", [], ["ASI09"], "other"),
    ("rce", ["LLM10"], ["ASI05"], "rce"),
    ("remote code execution", ["LLM10"], ["ASI05"], "rce"),
    ("supply chain", ["LLM04"], ["ASI04"], "supply-chain"),
    ("poisoning", ["LLM05"], ["ASI06"], "model-poisoning"),
    ("model theft", ["LLM02"], [], "model-extraction"),
    ("model extraction", ["LLM02"], [], "model-extraction"),
    ("adversarial", [], [], "adversarial-input"),
    ("hallucina", ["LLM07"], [], "other"),
    ("misinform", ["LLM07"], [], "other"),
    ("disinform", ["LLM07"], [], "other"),
    ("propaganda", ["LLM07"], [], "other"),
    ("election", ["LLM07"], [], "other"),
    ("influence operation", ["LLM07"], [], "other"),
    ("csam", ["LLM07"], [], "other"),
    ("child sexual", ["LLM07"], [], "other"),
    ("wrongful arrest", [], [], "other"),
    ("facial recognition", [], [], "other"),
    ("biometric", [], [], "other"),
    ("surveillance", [], [], "other"),
    ("autonomous weapon", [], ["ASI10"], "other"),
    ("self-harm", ["LLM10"], ["ASI09"], "other"),
    ("suicide", ["LLM10"], ["ASI09"], "other"),
    ("racial profil", ["LLM07"], [], "other"),
]


def load_sitemap() -> list[str]:
    print(f"[aim] fetching sitemap {SITEMAP_URL}")
    body, _ = fetch_once(SITEMAP_URL, timeout=30)
    text = body.decode("utf-8", errors="replace")
    urls = re.findall(r"<loc>([^<]+)</loc>", text)
    # Only /en/incidents/<id> pages, not the landing /en/incidents
    urls = [u for u in urls if re.match(r"https://oecd\.ai/en/incidents/[^/]+$", u)]
    print(f"[aim] sitemap has {len(urls)} incident URLs")
    return urls


def fetch_page(url: str) -> str | None:
    """Fetch and decode one AIM incident page.

    No size cap. The page was previously truncated to the first 800,000
    bytes before decoding -- a page whose `<script id="ng-state">` JSON blob
    starts at or straddles that offset was silently cut mid-tag or mid-JSON,
    extract_state() found no (or a corrupt) match, and the page was folded
    into "unparseable" with no distinguishing signal (gate-measured: 7/250
    date-hash pages over 800 KB in a cached sample, ~38 incidents/run in the
    2026-09-14 full crawl -- see PROGRESS.md "E21 TRIPWIRE FIRED", WS4-T11).

    The cap bought nothing: `robust_fetch()` already downloads and caches
    the FULL response body regardless of this cap (the slice was applied
    only here, after the fetch and the disk write), so removing it changes
    no network or disk-caching behavior -- only whether the bytes actually on
    disk get handed to the parser whole. A raised-but-still-finite cap would
    have the identical failure shape at a different (still arbitrary) byte
    offset, plus it would require a new loud "oversize pages skipped"
    counter to avoid re-introducing a silent drop -- removing the cap avoids
    both. It also removes a real (if narrow) correctness bug: slicing raw
    UTF-8 *bytes* at a fixed offset can land inside a multi-byte character,
    which `errors="replace"` then silently mangles into U+FFFD.

    Memory/CPU: this function alone is cheap -- one page's decoded text
    transiently in memory per call. The real memory cost of removing the cap
    lives in `main()`, NOT here: retaining every fetched page's full decoded
    text in a `pages: dict[url, text]` until the parse loop (the pre-WS4-T11
    BOUNCE #1 shape) would hold up to `len(urls)` pages (default 3000)
    simultaneously -- red-reviewer estimated >=2.8 GB for all-ASCII content,
    5.7-11 GB with non-Latin-1 characters present (Python's internal string
    representation is 1/2/4 bytes/char depending on the widest codepoint in
    the string), an ~19% peak increase versus the 800 KB-capped version.
    `main()` now avoids that entirely: `fetch_and_extract()` below extracts
    the ng-state body (or a failure reason) inside the SAME worker-thread
    call that fetches the page, and only that small extracted result -- not
    the page text -- crosses back to `main()`'s `as_completed` loop. The
    decoded text goes out of scope and is garbage-collected per-worker, so
    peak memory is bounded by `MAX_WORKERS` in-flight pages (~10), not by
    the crawl window size.

    The ng-state regex (`(.+?)</script>`, DOTALL) is a lazy quantifier
    bounded by a literal, fixed terminator -- linear in input length, not
    the ambiguous-alternation shape that causes catastrophic backtracking.
    Measured directly: ~2 ms on a 5,200,203-byte synthetic page, ~5 ms on a
    10,200,203-byte one (see
    tests/test_ingest_oecd_aim.py::test_extract_state_handles_multi_mb_page_without_pathological_backtracking,
    which asserts a generous <5s bound rather than the exact figure, to
    avoid CI flakiness).
    """
    slug = url.rstrip("/").split("/")[-1]
    cache_file = CACHE / f"{slug}.html"
    try:
        data = robust_fetch(url, cache_file, timeout=20, max_retries=3, min_cache_bytes=1000)
        return data.decode("utf-8", errors="replace")
    except RuntimeError as e:
        print(f"  ! {slug}: {e}", file=sys.stderr)
        return None


# Reason codes returned by _extract_state_detail() -- WS4-T11 BOUNCE #1
# defect 3: the previous single ok/"unparseable" split silently folded
# fundamentally different page shapes into one undistinguished bucket. The
# 2026-09-14 E21 audit (docs/audits/E21-tripwire-refresh-2026-09-14.md
# ~:210-262) found that of 2988 crawled pages, ALL carry an ng-state tag and
# ALL parse as JSON -- the 1852 "unparseable" legacy numeric-slug pages fail
# for a THIRD reason entirely: their ng-state blob uses a different
# top-level key shape (hashed keys with `b/h/s/st/u/rt` sub-fields) that
# never satisfies the `isinstance(body, dict) and body.get("id") and
# body.get("title")` shape check below. Distinguishing these three failure
# modes is what makes a future truncation-shaped regression (or any other
# new failure mode) visible again instead of vanishing into the same bucket
# that hid the WS4-T11 800 KB truncation.
REASON_NO_SCRIPT_MATCH = "no_ng_state_script"
REASON_JSON_DECODE_ERROR = "json_decode_error"
REASON_NO_BODY_SHAPE = "no_incident_body_shape"
REASON_OK = "ok"
REASON_FETCH_FAILED = "fetch_failed"

_NG_STATE_RE = re.compile(r'<script[^>]*id="ng-state"[^>]*>(.+?)</script>', re.S)


def _extract_state_detail(text: str) -> tuple[str, dict | None]:
    """Parse the Angular ng-state script JSON blob, returning WHY extraction
    failed (one of the REASON_* constants above), not just whether it did.

    The regex's `(.+?)` is a LAZY quantifier bounded by the literal,
    fixed `</script>` terminator: it matches the FIRST `</script>` after the
    ng-state open tag, never swallowing past it into any later `<script>`
    block that happens to follow on the page (a greedy `(.+)` would, and
    would then typically fail to json.loads() -- see
    tests/test_ingest_oecd_aim.py's trailing-script-tag fixtures).
    """
    m = _NG_STATE_RE.search(text)
    if not m:
        return REASON_NO_SCRIPT_MATCH, None
    try:
        state = json.loads(m.group(1))
    except json.JSONDecodeError:
        return REASON_JSON_DECODE_ERROR, None
    for k, v in state.items():
        if not isinstance(v, dict):
            continue
        body = v.get("b")
        if isinstance(body, dict) and body.get("id") and body.get("title"):
            return REASON_OK, body
    return REASON_NO_BODY_SHAPE, None


def extract_state(text: str) -> dict | None:
    """Parse the Angular ng-state script JSON blob. Thin public wrapper over
    `_extract_state_detail()` that keeps the original dict-or-None contract
    for callers (tests, and any future direct use) that only need the body,
    not the failure reason."""
    return _extract_state_detail(text)[1]


def fetch_and_extract(url: str) -> tuple[str, dict | None]:
    """Fetch one page and extract its ng-state body in the SAME call,
    returning `(reason, body)` -- `body` is non-None iff `reason == REASON_OK`.

    This is the memory-bounded replacement for `main()` previously
    accumulating every fetched page's full decoded text in a `pages` dict
    until a separate parse loop (see fetch_page()'s docstring). Submitting
    THIS function to the thread pool instead of bare `fetch_page()` means
    the page text lives only inside this call's local `text` variable and is
    garbage-collected when this function returns; only the small `(reason,
    body)` result crosses back to `main()`.
    """
    text = fetch_page(url)
    if text is None:
        return REASON_FETCH_FAILED, None
    return _extract_state_detail(text)


def collect_text(body: dict) -> str:
    parts = [
        body.get("title") or "",
        body.get("summary") or "",
        " ".join(body.get("evidences") or []),
    ]
    for art in body.get("articles") or []:
        if not isinstance(art, dict):
            continue
        parts.append(art.get("title") or "")
        ev = art.get("evidences") or []
        if isinstance(ev, list):
            parts.append(" ".join(e for e in ev if isinstance(e, str)))
    return " ".join(parts).lower()


def is_security_relevant(text: str) -> bool:
    return any(kw in text for kw in SECURITY_KEYWORDS)


def map_taxonomy(text: str) -> tuple[list[str], list[str], str]:
    llm: set[str] = set()
    asi: set[str] = set()
    attack_vector = "other"
    for kw, l, a, av in KEYWORD_TO_OWASP:
        if kw in text:
            llm.update(l)
            asi.update(a)
            if attack_vector == "other" and av != "other":
                attack_vector = av
    return sorted(llm), sorted(asi), attack_vector


def classify_corpus_signal(title: str, narrative_text: str, tags: list[str]) -> str:
    """`security` or `ai-harm`, computed from a title+narrative+tags signal
    using the identical keyword lists `merge_and_dedupe.py::_classify_corpus()`
    applies to a corpus entry -- so a persisted OECD `corpus` value is exactly
    what the merge-time classifier would have produced anyway, byte for byte.

    `narrative_text` is deliberately the OLD-style summary/evidences text
    this ingest used to persist wholesale as `description` -- the exact
    signal `_classify_corpus()` reads today (`entry.get("description")`,
    since OECD rows never set `corpus` and fall through the AIAAIC-only
    `_aiaaic_seed_text()` decoupling) -- NOT the broader `full_text` used for
    attack_vector/severity. Matching the narrower, already-shipping signal
    exactly is what makes this a pure decoupling (0 unintended `corpus`
    moves) rather than a reclassification under a new mechanism; see
    docs/audits/E21-oecd-narrative-licence-2026-07-30.md §5.1/§5.6 and
    normalize_body()'s own call site below."""
    text = (title + " " + narrative_text + " " + " ".join(tags)).lower()
    if any(kw in text for kw in CORPUS_SECURITY_KEYWORDS):
        return "security"
    if any(kw in text for kw in CORPUS_AI_HARM_KEYWORDS):
        return "ai-harm"
    return "security"


def reclassify_attack_vector_from_narrative(attack_vector: str, title: str, narrative_text: str) -> str:
    """If `attack_vector` is (still) "other", try one more time against a
    title+narrative signal, using the SAME classifier
    (`merge_and_dedupe.classify_attack_vector` / `_ATTACK_VECTOR_RULES`)
    merge_and_dedupe.py's own normalize_entry()/step-4b finalize apply to
    `title + " " + description` when a raw attack_vector is missing/"other".
    That richer, regex-based rule set is a different, second classifier from
    map_taxonomy()'s KEYWORD_TO_OWASP above -- one this ingest never used to
    invoke itself, relying instead on merge time to do it FROM THE
    PRE-REDUCTION NARRATIVE DESCRIPTION. Reducing that description would
    silently regress every row this fallback used to rescue back to "other"
    (measured: 178/4160 in dry run) -- the identical cascade shape as the
    `corpus` decoupling, on a different merge-time reclassifier. Calling this
    at ingest/migration time instead, on the narrative signal, and persisting
    the result closes it the same way: merge_and_dedupe's own guards
    (`if not vec or vec == "other"`) never fire because there is no longer
    an "other" left to re-derive. Returns `attack_vector` unchanged if it
    isn't "other", or if the narrative yields no match either."""
    if attack_vector != "other":
        return attack_vector
    reclassified = classify_attack_vector((title or "") + " " + (narrative_text or ""))
    return reclassified or attack_vector


def build_description(source_id: str, date: str, url: str, affected: str, attack_vector: str) -> str:
    """An originally-templated sentence built ONLY from structural facts
    already captured on the row (the AIM source id, the incident date, the
    named entities, the classified attack vector, the AIM page link) --
    NEVER from `summary`/`evidences`, which are OECD AIM's own LLM-generated
    (o3-mini) synthesis of third-party news text of uncertain, unresolved
    copyright status (see docs/audits/E21-oecd-narrative-licence-2026-07-30.md
    §2.4/§3, outcome (B): the project's conservative-default rule treats that
    text as not safely redistributable). Mirrors the pattern this codebase
    already uses for exactly this situation, one function away:
    `ingest_external.py::ingest_aiid_oecd_bridge()` builds its description
    from ids/dates/urls alone, never from any source's own narrative prose.
    `summary`/`evidences` continue to feed `is_security_relevant()` /
    `map_taxonomy()` / the severity heuristic / `classify_corpus_signal()`
    above exactly as before -- ephemeral, in-memory signals, never persisted
    themselves."""
    sentence = f"Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as {source_id}"
    sentence += f", dated {date}." if date else "."
    if affected:
        sentence += f" Entities named in the record: {affected}."
    if attack_vector and attack_vector != "other":
        sentence += f" Classified attack vector: {attack_vector}."
    sentence += f" See the AIM incident page ({url}) and its cited news sources for full narrative detail."
    return sentence[:1500]


def normalize_body(body: dict, url: str) -> dict | None:
    full_text = collect_text(body)
    if not is_security_relevant(full_text):
        return None

    title = (body.get("title") or "").strip()
    if len(title) < 5:
        return None

    date = (body.get("date") or "").strip()
    year = None
    m = re.match(r"^(\d{4})", date)
    if m:
        year = int(m.group(1))
    if not year:
        # Fall back to URL slug like 2026-03-22-955e
        m = re.search(r"/(\d{4})-(\d{2})-(\d{2})-", url)
        if m:
            year = int(m.group(1))
            date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    if not year or year < 1980 or year > 2030:
        return None

    # Ephemeral corpus-classification seed ONLY -- the exact summary/evidences
    # text this ingest used to persist wholesale as `description` before the
    # E21 reduction. Fed to classify_corpus_signal() below and then
    # discarded; never itself written to output. See build_description()'s
    # docstring for the replacement description and why summary/evidences
    # never reach it.
    narrative_seed = body.get("summary") or ""
    if not narrative_seed:
        for art in body.get("articles") or []:
            ev = art.get("evidences") or []
            if isinstance(ev, list) and ev:
                narrative_seed = " ".join(e for e in ev if isinstance(e, str))[:1000]
                if narrative_seed:
                    break

    llm, asi, attack_vector = map_taxonomy(full_text)
    attack_vector = reclassify_attack_vector_from_narrative(attack_vector, title, narrative_seed)

    # Severity heuristic
    sev = "Medium"
    if any(k in full_text for k in ("killed", "death", "fatal", "ransom", "billions", "national security")):
        sev = "Critical"
    elif any(k in full_text for k in ("breach", "stolen", "leaked", "exfil", "rce", "arrest")):
        sev = "High"

    # References: page URL + any article URLs.
    references = [{"title": title, "url": url, "type": "report"}]
    for art in (body.get("articles") or [])[:6]:
        au = (art or {}).get("url")
        at = (art or {}).get("title") or au or "news"
        if au:
            references.append({"title": at[:160], "url": au, "type": "news"})

    company = body.get("company") or []
    if isinstance(company, list):
        affected = ", ".join(c for c in company if isinstance(c, str))[:200]
    elif isinstance(company, str):
        affected = company[:200]
    else:
        affected = ""

    tags = ["oecd-aim"]
    if body.get("is_legacy"):
        tags.append("oecd-legacy")
    aiid_ids = body.get("aiid_ids") or []
    source_ids = [f"OECD-AIM-{body['id']}"]
    if isinstance(aiid_ids, list):
        for a in aiid_ids:
            try:
                source_ids.append(f"AIID-{int(a)}")
            except (TypeError, ValueError):
                pass

    # Persist the DERIVED SIGNAL only (a plain security/ai-harm enum) from
    # the pre-reduction narrative seed -- never the seed text itself. This is
    # the decoupling: merge_and_dedupe.py:1442's existing "respect an
    # explicit value" guard then takes effect unmodified, so no future
    # description-wording edit can ever silently move `corpus` again (the
    # WS0-T3 cascade this mirrors and closes for OECD; see
    # docs/audits/WS0-T3-cascade-2026-07-18.md and E21 §5.1).
    corpus = classify_corpus_signal(title, narrative_seed, tags)
    final_date = date or str(year)
    description = build_description(source_ids[0], final_date, url, affected, attack_vector)

    return {
        "source_id": source_ids[0],
        "_extra_source_ids": source_ids[1:],
        "title": title[:300],
        "date": final_date,
        "year": year,
        "category": "real-world",
        "description": description,
        "corpus": corpus,
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": sev,
        "owasp_llm": llm,
        "owasp_asi": asi,
        "mitre_atlas": [],
        "references": references,
        "tags": tags,
    }


def union_with_existing(fresh: list[dict], existing: list[dict]) -> list[dict]:
    """Union the fresh fetch with the previously-committed ingest file so the
    OECD corpus only ever grows. Keyed by ``source_id`` (``OECD-AIM-<id>``):
    fresh wins on conflict (latest content); entries present only in
    ``existing`` (aged out of the newest-N sitemap window) are kept. Output is
    sorted by ``source_id`` so the committed file has stable, deterministic
    ordering (lexicographic by source_id; OECD ids are date/hash-suffixed strings, not bare integers)."""
    by_id: dict[str, dict] = {}
    for e in existing:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    for e in fresh:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    return sorted(by_id.values(), key=lambda e: e.get("source_id") or "")


def _tally_reasons(results: dict[str, tuple[str, dict | None]]) -> dict[str, int]:
    """Pure counting helper, factored out of main() so the accounting is
    directly testable without a network-backed end-to-end run: one bucket
    per REASON_* code. WS4-T11 BOUNCE #1 defect 3."""
    counts: dict[str, int] = {}
    for reason, _body in results.values():
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def main():
    limit_env = os.environ.get("OECD_AIM_LIMIT", str(DEFAULT_LIMIT))
    try:
        limit = int(limit_env)
    except ValueError:
        limit = DEFAULT_LIMIT
    urls = load_sitemap()
    if limit > 0:
        urls = urls[:limit]
        print(f"[aim] capped to {limit} URLs (set OECD_AIM_LIMIT=0 for all)")

    t0 = time.time()
    # (reason, body) per url -- NOT the decoded page text. fetch_and_extract()
    # fetches AND extracts inside the same worker call so the full page text
    # never crosses back into this dict; see fetch_page()'s and
    # fetch_and_extract()'s docstrings (WS4-T11 BOUNCE #1 defect 4).
    results: dict[str, tuple[str, dict | None]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_and_extract, u): u for u in urls}
        for i, fut in enumerate(as_completed(futures), 1):
            u = futures[fut]
            # `results` is keyed by URL, so a duplicate sitemap URL (load_sitemap()
            # does not dedupe) collapses to one entry here -- both submissions did
            # real work, but only one survives to be counted. See the `fetched`
            # derivation below (WS4-T11 re-gate BOUNCE #2 advisory 2).
            #
            # A 0-byte page (`fetch_page()` returns `""`, which is not None) is
            # stored here too, and buckets to REASON_NO_SCRIPT_MATCH below -- an
            # intentional, documented behavior change from the pre-WS4-T11-BOUNCE-1
            # `pages` dict, which used `if text:` (truthy) and so silently dropped
            # an empty-string page from BOTH the fetched and the unparseable counts.
            # It is now counted honestly as fetched-but-unparseable, not vanished.
            results[u] = fut.result()
            if i % 200 == 0:
                elapsed = time.time() - t0
                rate = i / max(elapsed, 0.001)
                print(f"  fetched {i}/{len(urls)} ({rate:.1f} pages/s)")

    counts = _tally_reasons(results)
    # Derived from `results` (deduped by URL), NOT `len(urls)`: `len(urls)` counts
    # a duplicate sitemap URL once per occurrence, which would overcount `fetched`
    # by exactly the duplicate count even though only one result was ever kept per
    # URL. `len(urls)` remains in the printed denominator below as "how many
    # sitemap entries were attempted", which legitimately can exceed the unique
    # fetch count when duplicates are present.
    fetched = len(results) - counts.get(REASON_FETCH_FAILED, 0)
    print(f"[aim] fetched {fetched}/{len(urls)} pages in {time.time()-t0:.0f}s")

    out = []
    for url, (reason, body) in results.items():
        if reason != REASON_OK or body is None:
            continue
        norm = normalize_body(body, url)
        if norm:
            # Flatten the extra AIID source_ids back into the array form
            # the merger expects (it reads a single source_id field).
            extras = norm.pop("_extra_source_ids", [])
            if extras:
                norm["extra_source_ids"] = extras
            out.append(norm)

    ok = counts.get(REASON_OK, 0)
    no_script = counts.get(REASON_NO_SCRIPT_MATCH, 0)
    json_err = counts.get(REASON_JSON_DECODE_ERROR, 0)
    no_shape = counts.get(REASON_NO_BODY_SHAPE, 0)
    unparseable = no_script + json_err + no_shape  # same total this line always meant
    print(
        f"[aim] parsed: {ok} ok, {unparseable} unparseable "
        f"(no ng-state script: {no_script}, JSON decode error: {json_err}, "
        f"ng-state present but no incident-body shape: {no_shape}); "
        f"{len(out)} security-relevant kept"
    )

    out_path = INGEST / "oecd_aim_full_incidents.json"
    existing: list[dict] = []
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except (ValueError, OSError):
            existing = []
    merged = union_with_existing(out, existing)
    print(
        f"[aim] union: {len(out)} kept + {len(existing)} existing "
        f"-> {len(merged)} retained"
    )
    out_path.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"[aim] wrote -> {out_path}")


if __name__ == "__main__":
    main()
