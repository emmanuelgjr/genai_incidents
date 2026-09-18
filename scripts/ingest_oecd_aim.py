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
from datetime import datetime, timezone
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


# WS4-T13: OECD AIM's sitemap carries TWO incident-ID schemes. The modern one
# is always `YYYY-MM-DD-<hex>` (e.g. `2026-09-10-1de6`) -- it can never
# fullmatch this pattern because of its hyphens. The legacy one is OECD's own
# original small-integer sequential numbering (e.g. `256`, `321`) and now
# resurfaces inside the newest-N crawl window because the two schemes are
# sorted together in the sitemap (see docs/audits/E21-tripwire-refresh-
# 2026-09-14.md, "Finding 5", 2026-09-14 live measurement: 1852 numeric-slug
# / 1148 date-hash-slug / 0 other, in the newest 3000). Every legacy-slug page
# fetched so far has failed `_extract_state_detail()`'s body-shape check
# (`REASON_NO_BODY_SHAPE`, 0 exceptions observed) because its `ng-state` blob
# uses a different top-level key shape (hashed keys with `b/h/s/st/u/rt`
# sub-fields) -- fetching it always spends one rate-limited request (see
# `ingest/common.py::DEFAULT_MIN_INTERVAL`, 1.0s/host, shared across ALL
# worker threads) for zero possible yield. Skipping it BEFORE the fetch
# (not after, the way the REASON_NO_BODY_SHAPE bucket already silently
# absorbed it) turns wasted requests into headroom against the workflow's
# `timeout-minutes: 60` (`.github/workflows/auto-refresh.yml`) and, in the
# same direction, reduces load on a third-party host (Invariant 5 conduct).
#
# The rule is deliberately narrow -- match ONLY a slug that is entirely
# digits, never a prefix/substring test -- because that is the one shape a
# genuine modern-scheme slug can never take (it always contains a hyphen).
# A slug that mixes digits with anything else (a hex suffix, a stray letter)
# is treated as unknown and IS fetched: this rule skips only what is
# unambiguous, never guesses. See `is_numeric_slug()`'s docstring for the
# boundary cases this was checked against (leading zeros, a bare year).
_NUMERIC_SLUG_RE = re.compile(r"^\d+$")


def is_numeric_slug(url: str) -> bool:
    """True iff `url`'s final path segment is composed ENTIRELY of digits --
    OECD AIM's legacy incident-ID scheme. Examples observed live in the
    sitemap (docs/audits/E21-tripwire-refresh-2026-09-14.md): `/en/
    incidents/256`, `/321`, `/281`, `/342`, `/359`.

    Boundary cases, checked directly (tests/test_ingest_oecd_aim.py::
    test_is_numeric_slug_classifies_legacy_vs_modern):
      - Leading zeros (`007`): still all-digits -> True (still legacy-shaped;
        OECD's own sequential counter, not reinterpreted).
      - A bare slug that happens to look like a year (`2026`): all-digits ->
        True. No such URL shape exists in OECD AIM's sitemap today (the
        2026-09-14 audit found `other=0` in the crawled window -- only the
        two schemes above appear), and the modern scheme NEVER emits a bare
        year with no hyphen/hex suffix, so this cannot misclassify a real
        modern-scheme URL. Flagged here, not silently assumed away, in case
        OECD ever introduces a URL shape this project hasn't seen.
      - Numeric-with-suffix (`256a`, `256-x`): NOT a full match -> False.
        Treated as an unknown shape and fetched normally -- the rule never
        skips on a partial/ambiguous match.
    """
    slug = url.rstrip("/").split("/")[-1]
    return bool(_NUMERIC_SLUG_RE.fullmatch(slug))


def partition_fetchable(urls: list[str]) -> tuple[list[str], list[str]]:
    """Split `urls` into `(fetchable, skipped_numeric_slug)`, preserving
    input order in both. Pure / no network call -- so it's testable directly
    (`tests/test_ingest_oecd_aim.py::test_partition_fetchable_skips_only_
    numeric_slugs`), independent of `main()`'s network-shaped flow."""
    fetchable = [u for u in urls if not is_numeric_slug(u)]
    skipped = [u for u in urls if is_numeric_slug(u)]
    return fetchable, skipped


# --- WS4-T17: the sampling probe that restores the tripwire WS4-T13's skip
# erased. -------------------------------------------------------------------
#
# is_numeric_slug()'s skip rule rests on a premise that was TRUE when
# measured (docs/audits/E21-tripwire-refresh-2026-09-14.md, "Finding 5": 1852
# legacy numeric-slug pages fetched, ALL 1852 failed the ng-state body-shape
# check, 0 exceptions) -- but the whole point of the skip is to stop fetching
# those pages. The moment it does, the evidence that would ever show OECD
# changed the legacy page's shape (or that the "always fails" premise was
# simply wrong for some slug this project never sampled) stops being
# collected -- silently, and permanently. The in-window legacy population has
# since been RE-MEASURED at 1,773 (WS4-T13's own re-gate: "today 1773/1227",
# PROGRESS.md -- moving equal-and-opposite against the 2026-09-14 E21
# baseline as the window's date-hash head grows). Its exact size SHIFTS run
# to run as the newest-N window slides -- currently shrinking, as more
# modern-scheme content claims a larger share of a fixed-size window, not
# growing -- and this probe's design does not depend on which direction it
# moves. This is the one advisory that gets WORSE by merging the skip:
# reviewer finding, WS4-T17 brief.
#
# The fix is a small, real (network) sample of the skipped set, every run,
# through the SAME conduct-checked fetch path (fetch_and_extract() ->
# fetch_page() -> ingest.common.robust_fetch()) the main crawl already uses
# -- no new egress path, see docs/INGESTION_CONDUCT.md.
#
# WS4-T17 BOUNCE #1 (resize): k=5 was theatre against a ~1,773-URL
# population -- a full cycle would have taken ceil(1773/5) = 355 runs, ~6.8
# years at this workflow's weekly cadence, against a population that never
# stops shifting. DEFAULT_PROBE_SAMPLE_SIZE is now 50, split evenly into a
# ROTATING half (guarantees monotonic full coverage -- select_probe_sample())
# and a RECENCY-BIASED half (select_recent_biased_sample(), below) that
# prioritizes the legacy slugs most likely to show a shape change first.
# Measured at the default split (25/25):
#   cycle length (rotating half) = ceil(1773 / 25) = 71 runs (~1.4 years at
#     this workflow's weekly cadence)
#   time cost    = 50 sequential fetches * ~1s DEFAULT_MIN_INTERVAL ~= 50s,
#                  ~2.3% of the ~36-minute headroom WS4-T13 recovered
#   request cost = 50 / 1773 ~= 2.8% of the request-count headroom WS4-T13
#                  recovered; the rotating half alone (25/1773 ~= 1.4%) is
#                  the portion carrying the guaranteed-coverage property
# See docs/INGESTION_CONDUCT.md's WS4-T17 section for the same figures
# re-derived against the population as measured there, and this task's
# report for the command used to measure them. No single source of truth
# for a live third-party count exists (same caveat as USER_AGENT's version
# string in ingest/common.py) -- these are point-in-time, hand-kept in sync.

DEFAULT_PROBE_SAMPLE_SIZE = 50  # total per run, split 50/50 rotating+recency-biased -- see the module comment above for the cycle-length/cost math this was chosen against.
PROBE_STATE_PATH = ROOT / "ingest" / "_state" / "skip_probe_state.json"


def _numeric_slug_value(url: str) -> int:
    """Integer value of a numeric-slug URL's final path segment. Callers must
    only pass URLs that satisfy is_numeric_slug(url) -- this is NOT
    defensive against a non-numeric slug (ValueError propagates), by design:
    every caller below only ever calls this on the `skipped_numeric` half of
    partition_fetchable()'s output, which is already guaranteed all-digit."""
    slug = url.rstrip("/").split("/")[-1]
    return int(slug)


def select_probe_sample(
    skipped: list[str], cursor: int | None, k: int
) -> tuple[list[str], int | None]:
    """Pick up to `k` URLs from `skipped` (this run's legacy numeric-slug
    population that partition_fetchable() decided NOT to fetch) to
    sample-probe this run. Returns `(sample, new_cursor)`.

    DESIGN DECISION -- rotating, not random, and why: `skipped` is sorted by
    its numeric slug VALUE ascending, and the sample is the next `k` entries
    strictly after `cursor` (wrapping to the start once the cursor runs off
    the end). Each run therefore advances through a DIFFERENT slice of the
    skipped population instead of a fresh random draw every time. A purely
    random per-run sample covers only `1 - (1 - k/n)^N` of a size-`n`
    population in expectation after `N` runs, and can -- by chance -- keep
    re-sampling the same handful of URLs indefinitely while leaving others
    completely untouched forever; a rotating cursor instead guarantees
    monotonic progress through the whole population, turning a per-run
    spot-check into EVENTUAL FULL COVERAGE deterministically. That is the
    property the reviewer asked for explicitly ("coverage accumulates across
    runs") and it is why this is not `random.sample()`.

    DESIGN DECISION -- advance by VALUE, not list position: the skipped
    population is not fixed between runs (the crawl window slides; which
    numeric slugs even appear in `skipped` shifts week to week as the newest-
    N window's tail moves). A position-based index (`state["i"] += k`) would
    silently skip or re-visit entries whenever the population's size or
    membership changes between runs. Comparing the next candidate's VALUE
    against the last value actually probed is robust to that: it always
    resumes just past the last real URL this rule confirmed, regardless of
    how the surrounding population reshuffled meanwhile.

    `cursor=None` (no prior state, e.g. first run ever, or state lost) starts
    from the beginning. `k<=0` or an empty `skipped` returns `([], cursor)`
    unchanged -- nothing to sample, state carries over untouched.

    MEASURED CYCLE LENGTH (WS4-T17 BOUNCE #1, agreement 6(c) -- a design
    argument alone is not a measured claim): `run_skip_sampling_probe()`
    calls this with `k = DEFAULT_PROBE_SAMPLE_SIZE // 2 = 25` (the rotating
    half of the default 50-URL sample). Against the population as measured
    at WS4-T13's own re-gate (1,773 in-window legacy numeric-slug URLs,
    PROGRESS.md), a full guaranteed-coverage cycle is
    `ceil(1773 / 25) = 71` runs -- about 1.4 years at this workflow's weekly
    cadence. This number moves if the population size moves (it is
    recomputed from `len(skipped)` every run, never hardcoded) or if `k`
    changes; it is NOT re-derived automatically anywhere -- see
    docs/INGESTION_CONDUCT.md's WS4-T17 section, kept in sync by hand.
    """
    if not skipped or k <= 0:
        return [], cursor
    ordered = sorted(skipped, key=_numeric_slug_value)
    n = len(ordered)
    k = min(k, n)
    if cursor is None:
        start = 0
    else:
        start = next(
            (i for i, u in enumerate(ordered) if _numeric_slug_value(u) > cursor), 0
        )
    sample = [ordered[(start + i) % n] for i in range(k)]
    new_cursor = _numeric_slug_value(sample[-1])
    return sample, new_cursor


def select_recent_biased_sample(
    skipped: list[str], exclude: set[str], k: int
) -> list[str]:
    """Return up to `k` URLs from `skipped`, preferring entries EARLIEST in
    `skipped`'s OWN order -- i.e. `partition_fetchable()`'s output order,
    which preserves the raw sitemap order (that function's own docstring:
    "preserving input order in both"), and `load_sitemap()` lists newest-
    first by the sitemap's own ordering. A legacy numeric-slug page that was
    recently touched -- an edit, a re-publish, a migration -- sorts CLOSER
    TO THE FRONT of the numeric-slug block (nearer the date-hash/numeric-
    slug boundary) than an untouched one, even though its URL is still
    legacy-numbered. This is the half of the sample biased toward where a
    shape change is MOST LIKELY to appear first: recently-active pages, not
    an arbitrary numeric-value-sorted slice (that guaranteed, eventual-full-
    coverage property is what the ROTATING half, `select_probe_sample()`
    above, already provides on its own fixed schedule).

    `exclude` (typically this run's rotating-half sample, as a set of URLs)
    is skipped so the two halves of a combined sample don't waste probe
    budget re-fetching the same URL twice in one run; remaining entries are
    still taken in `skipped`'s own order once the excluded ones are filtered
    out, so this stays a pure front-of-population bias, not a second
    rotation with its own guarantee.

    `k<=0` returns `[]`.
    """
    if k <= 0:
        return []
    out: list[str] = []
    for u in skipped:
        if u in exclude:
            continue
        out.append(u)
        if len(out) >= k:
            break
    return out


def _load_probe_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


def _save_probe_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _coverage_ledger(observed_values: list[int], population: list[str]) -> dict:
    """A MEASURED coverage number, not a design argument (WS4-T17 BOUNCE #1:
    "ship a coverage ledger with it so the coverage claim is a measured
    number rather than a design argument"). How much of the CURRENT skipped
    population has this probe directly OBSERVED (fetched with a
    determinate, non-`REASON_FETCH_FAILED` outcome) at least once, ever,
    across its whole lifetime -- not just this run.

    `observed_values` is the full lifetime set persisted in state
    (`observed_slugs`, numeric slug values); `population` is THIS run's
    `skipped` list. A value observed historically that has since aged out
    of the window (no longer in `population`, e.g. that page fell off the
    tail of the newest-N crawl) doesn't count toward coverage of the
    CURRENT population -- it's a claim about what's true of the population
    as it stands right now, not a lifetime total that can outlive the URLs
    it was measured against.
    """
    population_values = {_numeric_slug_value(u) for u in population}
    covered = population_values & set(observed_values)
    total = len(population_values)
    return {
        "observed_of_current_population": len(covered),
        "current_population_size": total,
        "coverage_fraction": (len(covered) / total) if total else None,
    }


def run_skip_sampling_probe(
    skipped: list[str],
    *,
    k: int = DEFAULT_PROBE_SAMPLE_SIZE,
    state_path: Path | None = None,
    fetch_fn=None,
) -> dict:
    """The WS4-T17 tripwire itself: fetch a real sample of `skipped` --
    HALF rotating (`select_probe_sample()`, guaranteed eventual full
    coverage on a fixed schedule) and HALF recency-biased
    (`select_recent_biased_sample()`, prioritizing the legacy slugs most
    likely to show a shape change first) -- through the same conduct-
    checked path the main crawl uses, and assert each OBSERVED one still
    fails the ng-state body-shape check -- i.e. the skip rule's premise
    still holds for what was actually observed this run.

    `fetch_fn` defaults to `fetch_and_extract` (the real, network-touching
    path); tests inject a stub returning canned `(reason, body)` pairs so
    this function's SELECTION/ACCOUNTING/PERSISTENCE logic is fully testable
    offline, while `fetch_and_extract` itself is exercised by its own
    (also-offline, cache-seeded) tests elsewhere in this suite.

    `state_path` resolves to the module-level `PROBE_STATE_PATH` at CALL
    time if not given (not bound as an early default), so tests can
    monkeypatch `PROBE_STATE_PATH` and have it take effect here exactly like
    `CACHE`/`INGEST` already do elsewhere in this module.

    Returns (and persists to `state_path`) a result dict:
      - "sample": the URLs probed this run (rotating half then recent half)
      - "findings": [{"url", "reason"}] per probed URL
      - "violations": URLs that came back REASON_OK -- a legacy numeric-slug
        page that NOW parses as a real incident body. This is the ONLY
        outcome treated as a hard failure: it means is_numeric_slug()'s skip
        rule is CURRENTLY DROPPING REAL INCIDENTS.
      - "soft_anomalies": URLs that still failed the body-shape check, but
        via a reason OTHER than REASON_NO_BODY_SHAPE (i.e.
        REASON_NO_SCRIPT_MATCH / REASON_JSON_DECODE_ERROR) -- not itself
        evidence of data loss (no incident body was ever extracted), but a
        deviation from the SPECIFIC 100%-NO_BODY_SHAPE pattern the
        2026-09-14 measurement found for every legacy page it fetched.
        Logged for visibility; never fatal on its own.
      - "fetch_failed": URLs that hit REASON_FETCH_FAILED -- ordinary
        network flakiness, carrying NO information either way about whether
        the skip rule's premise holds. WS4-T17 BOUNCE #1 defect 1:
        excluding these from "violations"/"soft_anomalies" is correct
        (counting them there would make the probe noisy for a reason
        unrelated to what it exists to catch), but the ORIGINAL version of
        this function ALSO excluded them from all reporting, which meant a
        run where every probed URL failed to fetch still printed "0
        violations -- premise still holds" -- an affirmative attestation
        having observed nothing, the exact failure shape this probe exists
        to close, one layer up, inside its own remedy. This key exists so
        callers can distinguish "checked and clean" from "checked nothing".
      - "observed": `len(sample) - len(fetch_failed)` -- how many URLs this
        run ACTUALLY produced a determinate signal for. Callers (main()'s
        wiring) must not print an affirmative "premise holds" attestation
        when this is 0.
      - "population_size": len(skipped) this run
      - "coverage_ledger": see `_coverage_ledger()` -- a measured, lifetime,
        current-population-relative coverage fraction, persisted and
        returned every run.

    Lifetime state persisted (not just this run's numbers): `cursor` (the
    rotating half's own progress marker), `total_sampled_lifetime` (every
    URL ever handed to `fetch_fn`, regardless of outcome) and
    `total_observed_lifetime` (only those that produced a determinate
    signal -- WS4-T17 BOUNCE #1: "track lifetime observed separately from
    sampled", since conflating them is exactly what let a
    fetch-failure-only run silently count as if real evidence had been
    collected). `last_run_id` stamps `GITHUB_RUN_ID` (or a `local-<utc
    timestamp>` fallback outside CI) so a caller can tell whether the state
    it's reading was actually produced by the run checking it -- see
    `check_probe_state_for_violations()`'s docstring (WS4-T17 BOUNCE #1
    advisory 2).
    """
    if fetch_fn is None:
        fetch_fn = fetch_and_extract
    path = state_path if state_path is not None else PROBE_STATE_PATH

    state = _load_probe_state(path)
    cursor = state.get("cursor")

    k_rotate = k // 2
    k_recent = k - k_rotate
    rotate_sample, new_cursor = select_probe_sample(skipped, cursor, k_rotate)
    recent_sample = select_recent_biased_sample(skipped, set(rotate_sample), k_recent)
    sample = rotate_sample + recent_sample

    findings: list[dict] = []
    violations: list[str] = []
    soft_anomalies: list[str] = []
    fetch_failed: list[str] = []
    for url in sample:
        reason, _body = fetch_fn(url)
        findings.append({"url": url, "reason": reason})
        if reason == REASON_FETCH_FAILED:
            fetch_failed.append(url)
        elif reason == REASON_OK:
            violations.append(url)
        elif reason != REASON_NO_BODY_SHAPE:
            soft_anomalies.append(url)

    fetch_failed_set = set(fetch_failed)
    observed_urls = [u for u in sample if u not in fetch_failed_set]
    observed_count = len(observed_urls)

    observed_values_lifetime = set(state.get("observed_slugs") or [])
    observed_values_lifetime.update(_numeric_slug_value(u) for u in observed_urls)
    coverage = _coverage_ledger(sorted(observed_values_lifetime), skipped)

    run_id = os.environ.get("GITHUB_RUN_ID") or f"local-{datetime.now(timezone.utc).isoformat()}"

    state["cursor"] = new_cursor if new_cursor is not None else cursor
    state["last_run_utc"] = datetime.now(timezone.utc).isoformat()
    state["last_run_id"] = run_id
    state["last_sample"] = sample
    state["last_findings"] = findings
    state["last_violations"] = violations
    state["last_soft_anomalies"] = soft_anomalies
    state["last_fetch_failed"] = fetch_failed
    state["last_observed_count"] = observed_count
    state["total_sampled_lifetime"] = int(state.get("total_sampled_lifetime", 0)) + len(sample)
    state["total_observed_lifetime"] = int(state.get("total_observed_lifetime", 0)) + observed_count
    state["observed_slugs"] = sorted(observed_values_lifetime)
    state["population_size_last_run"] = len(skipped)
    state["coverage_ledger"] = coverage
    _save_probe_state(path, state)

    return {
        "sample": sample,
        "findings": findings,
        "violations": violations,
        "soft_anomalies": soft_anomalies,
        "fetch_failed": fetch_failed,
        "observed": observed_count,
        "population_size": len(skipped),
        "coverage_ledger": coverage,
    }


def check_probe_state_for_violations(state_path: Path | None = None) -> int:
    """Read the LAST-persisted probe state and return a process exit code:
    1 if that run recorded any violations, 0 otherwise (including "no probe
    has ever run" -- a fresh checkout never fails this check).

    Deliberately a SEPARATE gate from the "Refresh OECD AI Incidents
    Monitor" ingest step's own outcome (see .github/workflows/auto-
    refresh.yml): that step is `continue-on-error: true` and its outcome
    feeds ingest/_state/source_health.json's CONSECUTIVE-failure counter,
    which exists specifically to smooth over ordinary third-party
    flakiness over several weeks before alerting loudly (WS4-T9). A skip-
    rule violation is not that kind of failure -- it is a deterministic
    correctness signal (a real incident is being silently dropped RIGHT
    NOW) that must fail the run loudly on the FIRST occurrence, not the
    third. Conflating the two would either mute a real-incident-loss signal
    for up to two extra weeks (if routed through source_health's threshold)
    or pollute source_health's flakiness counter with a correctness
    finding unrelated to source availability -- so this is its own gate,
    wired as its own workflow step, invoked via `--check-probe`.

    WS4-T17 BOUNCE #1 advisory 2 -- freshness: the workflow's OWN `if:
    steps.ingest_oecd.outcome == 'success'` step-ordering guard is, today,
    the only thing preventing this function from checking STALE state (a
    prior run's leftovers, never refreshed this run). That guard is correct
    for the production workflow but gives no protection to a manual, local,
    or future differently-wired call to this function -- so
    `run_skip_sampling_probe()` stamps `last_run_id` (from `GITHUB_RUN_ID`,
    or a `local-<timestamp>` fallback) into the state on every write, and
    this function compares it against the CURRENT `GITHUB_RUN_ID` (when one
    is set, i.e. we're actually inside a CI run) as a second, independent
    check. A mismatch is surfaced loudly as a warning -- not hard-failed,
    since a legitimate reason can still exist -- rather than silently
    trusting unverified-fresh state, which is exactly the failure shape
    this whole task exists to close.
    """
    path = state_path if state_path is not None else PROBE_STATE_PATH
    state = _load_probe_state(path)

    current_run_id = os.environ.get("GITHUB_RUN_ID")
    stamped_run_id = state.get("last_run_id")
    if current_run_id and stamped_run_id and stamped_run_id != current_run_id:
        print(
            f"::warning::WS4-T17 skip-rule probe state at {path} is stamped "
            f"last_run_id={stamped_run_id!r}, which does not match this CI "
            f"run's GITHUB_RUN_ID={current_run_id!r} -- the state being "
            "checked may not be from THIS run. Verify the workflow's step "
            "ordering (the probe state must be written by the SAME run that "
            "checks it) before trusting a clean result.",
            file=sys.stderr,
        )

    violations = state.get("last_violations") or []
    if violations:
        print(
            f"::error::WS4-T17 skip-rule sampling probe recorded {len(violations)} "
            f"violation(s) in its last run: {violations}. A legacy numeric-slug OECD "
            "AIM URL now returns a real incident body (REASON_OK) -- is_numeric_slug()'s "
            f"skip rule is DROPPING REAL INCIDENTS. See {path} ('last_findings') and the "
            "'Refresh OECD AI Incidents Monitor' step's own log for the fetched detail. "
            "Fix the rule (or the underlying page-shape assumption) before the next "
            "scheduled crawl.",
            file=sys.stderr,
        )
        return 1
    return 0


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

    # WS4-T13: drop legacy numeric-slug URLs from the fetch set BEFORE any
    # request is made -- see is_numeric_slug()'s docstring above for why this
    # is safe (the modern scheme can never fullmatch the all-digits pattern)
    # and docs/audits/E21-tripwire-refresh-2026-09-14.md for the population
    # this was measured against. `urls` (the full window, including the
    # skipped ones) is retained for the printed denominator below.
    fetch_urls, skipped_numeric = partition_fetchable(urls)
    print(
        f"[aim] skipping {len(skipped_numeric)}/{len(urls)} legacy numeric-slug "
        "URLs (OECD AIM's pre-date-hash ID scheme; ng-state shape never "
        f"parses -- see REASON_NO_BODY_SHAPE); fetching {len(fetch_urls)}"
    )

    t0 = time.time()
    # (reason, body) per url -- NOT the decoded page text. fetch_and_extract()
    # fetches AND extracts inside the same worker call so the full page text
    # never crosses back into this dict; see fetch_page()'s and
    # fetch_and_extract()'s docstrings (WS4-T11 BOUNCE #1 defect 4).
    results: dict[str, tuple[str, dict | None]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_and_extract, u): u for u in fetch_urls}
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
                print(f"  fetched {i}/{len(fetch_urls)} ({rate:.1f} pages/s)")

    counts = _tally_reasons(results)
    # Derived from `results` (deduped by URL), NOT `len(fetch_urls)`:
    # `len(fetch_urls)` counts a duplicate sitemap URL once per occurrence,
    # which would overcount `fetched` by exactly the duplicate count even
    # though only one result was ever kept per URL. `len(fetch_urls)` remains
    # in the printed denominator below as "how many URLs were actually
    # attempted" (i.e. the window minus the numeric-slug skips above), which
    # legitimately can exceed the unique fetch count when duplicates are
    # present.
    fetched = len(results) - counts.get(REASON_FETCH_FAILED, 0)
    print(f"[aim] fetched {fetched}/{len(fetch_urls)} pages in {time.time()-t0:.0f}s")

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

    # WS4-T17: sample-probe a rotating slice of the numeric-slug URLs the
    # budget skip (WS4-T13, above) decided NOT to fetch, to confirm the
    # skip rule's premise still holds -- see run_skip_sampling_probe()'s
    # docstring. Deliberately does NOT raise/exit here: this function's own
    # exit status feeds ingest/_state/source_health.json's THIRD-PARTY-
    # flakiness counter (via the "Refresh OECD AI Incidents Monitor" step's
    # outcome), and a skip-rule violation is a different, more urgent kind
    # of signal that must fail loudly on the FIRST occurrence -- see
    # check_probe_state_for_violations()'s docstring for the separate gate
    # that enforces that, and .github/workflows/auto-refresh.yml for how
    # it's wired as its own step.
    probe_k_env = os.environ.get("OECD_AIM_PROBE_SAMPLE_SIZE", str(DEFAULT_PROBE_SAMPLE_SIZE))
    try:
        probe_k = int(probe_k_env)
    except ValueError:
        probe_k = DEFAULT_PROBE_SAMPLE_SIZE

    if probe_k <= 0:
        print("[aim] skip-rule sampling probe disabled (OECD_AIM_PROBE_SAMPLE_SIZE<=0)")
    elif not skipped_numeric:
        print("[aim] skip-rule sampling probe: nothing skipped this run, nothing to sample")
    else:
        n_sample = min(probe_k, len(skipped_numeric))
        print(
            f"[aim] skip-rule sampling probe: fetching up to {n_sample}/{len(skipped_numeric)} "
            "skipped legacy numeric-slug URLs (rotating + recency-biased halves) to confirm "
            "the body-shape-check premise still holds (WS4-T17)"
        )
        probe_result = run_skip_sampling_probe(skipped_numeric, k=probe_k)
        n_failed = len(probe_result["fetch_failed"])
        n_observed = probe_result["observed"]
        ledger = probe_result["coverage_ledger"]
        if probe_result["violations"]:
            print(
                "::error::WS4-T17 skip-rule sampling probe found "
                f"{len(probe_result['violations'])} legacy numeric-slug URL(s) that now "
                f"return a real incident body: {probe_result['violations']} -- the "
                "is_numeric_slug() skip rule is DROPPING REAL INCIDENTS. See "
                "run_skip_sampling_probe()'s docstring / docs/INGESTION_CONDUCT.md.",
                file=sys.stderr,
            )
        elif probe_result["soft_anomalies"]:
            print(
                "::warning::WS4-T17 skip-rule sampling probe: "
                f"{len(probe_result['soft_anomalies'])} legacy numeric-slug URL(s) failed "
                f"the body-shape check via an unexpected reason: {probe_result['soft_anomalies']} "
                "-- not a confirmed data-loss case (no REASON_OK), but a deviation from the "
                "measured 100%-NO_BODY_SHAPE pattern; worth a look.",
                file=sys.stderr,
            )
        elif n_observed == 0:
            # WS4-T17 BOUNCE #1 defect 1: do NOT print an affirmative "premise
            # still holds" attestation when nothing was actually observed --
            # a run where every probed URL hits REASON_FETCH_FAILED carries
            # zero information either way, and the correlated-failure case
            # this matters for (OECD starting to 403/404 specifically on
            # legacy pages, a plausible retirement path) would otherwise make
            # this probe report green forever while seeing nothing.
            print(
                "::warning::WS4-T17 skip-rule sampling probe observed NOTHING this run -- "
                f"all {len(probe_result['sample'])} sampled URL(s) hit REASON_FETCH_FAILED "
                f"({probe_result['fetch_failed']}). This is NOT an attestation that the "
                "skip-rule premise holds -- no evidence was collected either way this run. "
                "If this persists across runs, the premise could silently become false while "
                "this probe keeps reporting green elsewhere.",
                file=sys.stderr,
            )
        else:
            print(
                f"[aim] skip-rule sampling probe: {n_observed}/{len(probe_result['sample'])} "
                f"observed ({n_failed} fetch failure(s) excluded), 0 violations -- premise "
                "still holds for what was observed this run"
            )
        print(
            f"[aim] skip-rule sampling probe coverage ledger: "
            f"{ledger['observed_of_current_population']}/{ledger['current_population_size']} "
            f"({(ledger['coverage_fraction'] or 0) * 100:.1f}%) of the current skipped "
            "population directly observed at least once (lifetime)"
        )


if __name__ == "__main__":
    if "--check-probe" in sys.argv[1:]:
        # WS4-T17: separate CLI mode, wired as its own workflow step (see
        # check_probe_state_for_violations()'s docstring for why this is
        # not folded into main()'s own exit status).
        sys.exit(check_probe_state_for_violations())
    main()
