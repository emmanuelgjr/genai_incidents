"""ingest/common.py -- the sole HTTP(S) chokepoint for this repo's ingest
pipeline (invariant 5, MASTER_IMPROVEMENT_PLAN.md: "All HTTP(S) fetching
goes through ingest/common.py", active as of WS0-T4; D22-amended from "all
network fetching" -- non-HTTP egress is registered separately, not here).

Every live HTTP(S) fetch any ``scripts/ingest_*.py`` / ``scrape_*.py``
script performs must route through a function in this module. For every
request that happens, this module enforces:

  - an identifying User-Agent naming the project and a contact address
    (``USER_AGENT`` below) -- see ``fetch_once()``, which strips any
    caller-supplied ``User-Agent`` header so it can never be overridden;
  - a robots.txt check before fetching, per host, FAIL-CLOSED -- see
    ``robots_allowed()``'s docstring for what "fail-closed" means here and
    why, and ``ROBOTS_UNVERIFIABLE_ALLOWLIST`` for the one kind of exception
    that exists (a host whose robots.txt is confirmed unreachable for every
    client, enumerated in code with dated evidence -- never a caller-side
    boolean, and never waiving an explicit Disallow rule);
  - a minimum per-host interval between requests (``DEFAULT_MIN_INTERVAL``),
    overridable per call for a source with its own documented, different
    cadence (e.g. NVD's stated 5-req/30s / 50-req/30s contract -- see
    ``scripts/ingest_cve_nvd_expanded.py``);
  - retry with exponential backoff on transient failures -- ``robust_fetch``/
    ``conditional_fetch`` below implement one such retry policy for the
    common "fetch a whole file, optionally cache it" case; scripts with
    their own retry cadence (again, NVD/OSV) call ``fetch_once()`` directly,
    once per attempt, inside their own loop.

See ``docs/INGESTION_CONDUCT.md`` for the conduct policy this module exists
to enforce, and ``docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md``
for the migration that made this the only module in the repo calling
``urllib.request.urlopen()`` for a *live* fetch. One documented, inert
exception: ``scripts/scrape_aiid.py`` still contains its own ``urlopen()``
call, but that function (and the module's ``main()``) is permanently
disabled -- never invoked by ``make ingest-all`` or anything else that
runs; kept only as an unused historical artifact / a source of pure
taxonomy-classification functions reused by ``ingest_aiid_snapshot.py``.
See that file's own module docstring, ``docs/SOURCE_LICENSES.md`` Section
1.2, and ``tests/test_network_chokepoint.py`` (which asserts this stays
true).

``make build`` never imports this module: ingest scripts are not in the
deterministic build path (``Makefile``'s ``build`` target is
``merge render render-docs-stats validate``, none of which touch the
network) -- see ``MASTER_IMPROVEMENT_PLAN.md``'s "never put model calls in
the deterministic build path" invariant and its network analogue enforced
by ``WS4-T1``'s ``make build`` contract.
"""

from __future__ import annotations

import sys
import threading
import time
import urllib.error
import urllib.request
import urllib.robotparser
from email.message import Message
from pathlib import Path
from urllib.parse import urlparse

# Identifying User-Agent + contact address (docs/INGESTION_CONDUCT.md's
# "identifying User-Agent, contact email" requirement). The contact address
# is this project's already-published security/abuse contact
# (SECURITY.md) -- reused here, not invented for this purpose: no
# ingestion-specific contact channel exists in the repo, and SECURITY.md's
# is the one address a puzzled upstream operator would actually find.
#
# Version number: kept in sync by hand with pyproject.toml's `version`, the
# same hand-synced pattern scripts/merge_and_dedupe.py's own hardcoded
# "version" field already uses (no single source of truth for the project
# version exists yet -- introducing one is a repo-wide decision out of this
# task's scope, flagged as follow-up in
# docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md). If you bump
# pyproject.toml's version, bump this string too.
#
# Project-token-LED, not `Mozilla/5.0`-prefixed (WS0-T4 bounce #1, D3 --
# changed from an earlier `Mozilla/5.0 (genai_incidents/2.8.0; ...)` form).
# `urllib.robotparser.Entry.applies_to()` reduces a UA string to
# `useragent.split("/")[0].lower()` before comparing it against a rule's own
# `User-agent:` token -- so a `Mozilla/5.0`-led string reduces to the single
# token "mozilla", identical to every browser and most bots, meaning an
# operator who reads this UA and writes `User-agent: genai_incidents` would
# have been silently ignored: an identity that cannot be addressed by the
# host reading it is not the "identifying User-Agent" the conduct policy
# promises. Leading with the project token instead makes
# `useragent.split("/")[0].lower()` resolve to "genai_incidents", addressable
# by name, and removes the incidental `mozilla` over-match risk in the same
# move (verified: docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md
# §13 -- a `robotparser` check confirms both directions, and a live probe
# across all 18 real ingest-target URLs found ZERO difference in robots
# verdict or fetch outcome between the two UA shapes, including on CISA,
# the one host with any evidence of UA-sensitive behavior at all -- so the
# earlier WAF-rejection concern that justified keeping `Mozilla/5.0` had no
# supporting measurement and does not hold up against one).
USER_AGENT = (
    "genai_incidents/2.10.0 (+https://github.com/emmanuelgjr; "
    "contact: emmanuelgjr@gmail.com)"
)

# Conservative default spacing (seconds) between requests to the SAME host,
# absent a source-specific documented allowance. Pass min_interval= to
# override -- e.g. NVD's own stated rate-limit contract (5 req/30s public,
# 50 req/30s with an API key; docs/SOURCE_LICENSES.md Section 2.2), which is
# tighter/more nuanced than this flat generic default.
DEFAULT_MIN_INTERVAL = 1.0

# Hosts whose robots.txt is UNVERIFIABLE -- confirmed empirically to refuse
# every client, not merely blocked for this project's identity -- and are
# therefore explicitly, individually waived from robots_allowed()'s
# fail-closed refusal. This is the ONLY way that refusal can ever be waived:
# there is no caller-side parameter (fetch_once() has none; see its
# docstring) -- a new exception requires editing this module, in a reviewed
# commit, with the same evidence standard as the entry below.
#
# The waiver is narrow in two ways:
#   1. It applies ONLY when robots.txt itself could not be fetched at all
#      (the _get_robots_parser() "unverifiable" outcome). A host that DOES
#      serve a robots.txt with an explicit Disallow rule is refused exactly
#      as normal, allowlist or not -- see robots_allowed()'s implementation.
#   2. It waives only the robots-verification refusal. The per-host rate
#      limit (_rate_limit(), DEFAULT_MIN_INTERVAL / a caller's min_interval=)
#      and the identifying USER_AGENT still apply in full to every request,
#      allowlisted host or not -- fetch_once() enforces both unconditionally,
#      after this check, regardless of this dict's contents.
#
# Each entry: why (grounded in evidence, not a guess), the date that evidence
# was collected, the evidence itself (so it can be re-verified or expire),
# and what remains enforced for that host as a reminder of point 2 above.
ROBOTS_UNVERIFIABLE_ALLOWLIST: dict[str, dict[str, str]] = {
    "www.cisa.gov": {
        "reason": (
            "cisa.gov returns HTTP 403 on /robots.txt for every User-Agent "
            "tested -- this project's identifying UA, a plain browser UA, a "
            "bare non-Mozilla token, and urllib's own unmodified default -- "
            "on both the apex (cisa.gov) and www hosts. robots.txt is "
            "unreachable for ANY client here, not specifically blocked for "
            "this project's identity, so the fail-closed refusal this "
            "allowlist waives would otherwise permanently block a source "
            "that has never actually refused US. The KEV feed itself "
            "(known_exploited_vulnerabilities.json) is a published US "
            "federal feed explicitly intended for automated consumption and "
            "returns 200 to the same User-Agents that get 403 on robots.txt."
        ),
        "evidence_date": "2026-07-29",
        "evidence": (
            "https://www.cisa.gov/robots.txt -> HTTP 403 (4 distinct UAs); "
            "https://cisa.gov/robots.txt -> HTTP 403 (4 distinct UAs); "
            "the KEV feed URL -> HTTP 200, 1,567,768 bytes (same 4 UAs). "
            "Independently re-run twice: once for the specialist report this "
            "allowlist entry is based on, once during this task's own "
            "verification. Full detail: "
            "docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md."
        ),
        "still_enforced": (
            "per-host rate limit (DEFAULT_MIN_INTERVAL, no override "
            "requested for this host) and the identifying USER_AGENT -- "
            "unaffected by this entry, enforced unconditionally by "
            "fetch_once() below."
        ),
    },
}

_state_lock = threading.Lock()
_last_request_at: dict[str, float] = {}
# host -> RobotFileParser, cached ONLY on a definitive outcome (a 200 with
# parseable rules, or a confirmed 404 == "no file published" -> an empty,
# allow-everything parser). A check that could not be completed (timeout,
# 5xx, DNS failure, ...) is deliberately NOT cached here, so the next call
# gets a fresh chance rather than being poisoned by one transient failure
# for the rest of the process's lifetime.
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _reset_state_for_tests() -> None:
    """Test-only: clear the rate-limit and robots caches between test cases,
    so state (and, more importantly, an accidental real time.sleep or a real
    network call) never leaks from one test into another. Called from an
    autouse fixture in tests/conftest.py."""
    with _state_lock:
        _last_request_at.clear()
        _robots_cache.clear()


def _rate_limit(host: str, min_interval: float) -> None:
    """Block until at least *min_interval* seconds have passed since the
    last request to *host*, across ALL callers/threads -- not just this one.

    Thread-safe: the next allowed slot is reserved under the lock, then the
    actual sleep happens outside it, so (a) concurrent requests to the SAME
    host queue up correctly (each reserves a slot *min_interval* after the
    previous reservation, not after the previous request's real completion
    time) and (b) requests to OTHER hosts are never blocked by this host's
    spacing.
    """
    if min_interval <= 0:
        return
    with _state_lock:
        now = time.monotonic()
        last = _last_request_at.get(host)
        wait = (min_interval - (now - last)) if last is not None else 0.0
        wait = max(wait, 0.0)
        _last_request_at[host] = now + wait
    if wait > 0:
        time.sleep(wait)


def _get_robots_parser(
    url: str, min_interval: float = DEFAULT_MIN_INTERVAL
) -> urllib.robotparser.RobotFileParser | None:
    """Return a cached RobotFileParser for *url*'s host, fetching and parsing
    it if not already cached. Returns None if the fetch could not be
    completed after a single transient retry (see module note above on why
    that outcome is never cached).

    One retry (with a 1s pause) is deliberate, not decorative: during this
    module's own development, a fast burst of parallel probe requests drew
    one spurious 403 from a host (nvd.nist.gov) whose robots.txt was
    confirmed a clean 404 on the very next try seconds later -- a real,
    observed transient-failure mode, not a hypothetical one.

    *min_interval* paces the robots.txt fetch itself through the SAME
    per-host rate limiter every content fetch uses (WS0-T4 bounce #1, R3):
    this used to call ``urllib.request.urlopen()`` directly, unpaced, so a
    host whose robots.txt was never cached (e.g. one on
    ``ROBOTS_UNVERIFIABLE_ALLOWLIST``, which -- by definition -- never gets a
    definitive answer to cache) would take up to 2 unpaced requests plus a
    1s retry sleep on EVERY call, contradicting a doc claim that the limiter
    applies "for every host, unconditionally." Passing the caller's own
    ``min_interval`` through (``robots_allowed()`` forwards whatever
    ``fetch_once()`` was given) keeps the robots probe and the content fetch
    under one consistent pacing budget for that host, rather than two.
    """
    parsed = urlparse(url)
    host = parsed.netloc
    with _state_lock:
        cached = _robots_cache.get(host)
    if cached is not None:
        return cached

    robots_url = f"{parsed.scheme}://{host}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)

    last_err: Exception | None = None
    for attempt in range(2):
        try:
            _rate_limit(host, min_interval)
            req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            rp.parse(body.splitlines())
            with _state_lock:
                _robots_cache[host] = rp
            return rp
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No robots.txt published == no stated restriction (matches
                # docs/SOURCE_LICENSES.md's existing reading of aiaaic.org's
                # 404). An empty parser (no rules parsed) allows everything.
                rp.parse([])
                with _state_lock:
                    _robots_cache[host] = rp
                return rp
            last_err = e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
        if attempt == 0:
            time.sleep(1)

    print(
        f"  [ingest.common] WARNING: could not verify robots.txt for {host} "
        f"({last_err}) -- refusing to fetch from this host until it can be "
        "verified (fail-closed; see docs/INGESTION_CONDUCT.md)",
        file=sys.stderr,
    )
    return None  # deliberately NOT cached -- see module note above


def robots_allowed(url: str, min_interval: float = DEFAULT_MIN_INTERVAL) -> bool:
    """True iff *url* may be fetched by USER_AGENT per its host's robots.txt.

    FAILS CLOSED: if robots.txt itself could not be verified (anything other
    than a 200 with parseable rules, or a confirmed 404 meaning "no file
    published"), the fetch is refused rather than assumed permitted. This is
    a deliberate conduct choice, not the only defensible one: fail-OPEN
    (proceed when robots.txt is merely unreachable) is arguably kinder to a
    host having a bad moment, but degrading loudly (refuse, and say why) is
    this pipeline's stated design ethos, and a scrape a host's operator would
    have blocked had their server answered is exactly the case fail-closed
    exists to avoid.

    A confirmed 404 (no robots.txt at all) is NOT treated as an unreachable
    check -- it's read as "no stated restriction," consistent with how
    docs/SOURCE_LICENSES.md already reads aiaaic.org's 404. So this function
    does not require an affirmative "yes" from every host; it only refuses
    when the check itself could not be completed at all.

    ONE exception to fail-closed: a host on ``ROBOTS_UNVERIFIABLE_ALLOWLIST``
    is treated as allowed when (and ONLY when) its robots.txt could not be
    verified at all -- see that dict's docstring for the evidence standard
    and what stays enforced regardless. A host that DOES serve a robots.txt
    with an explicit Disallow rule is refused exactly as normal, allowlisted
    or not; the allowlist has no effect on that branch below.

    *min_interval* is forwarded to ``_get_robots_parser()`` to pace the
    robots.txt fetch itself under the same per-host budget as the content
    fetch that follows (WS0-T4 bounce #1, R3) -- see that function's
    docstring.
    """
    rp = _get_robots_parser(url, min_interval)
    if rp is None:
        return urlparse(url).netloc in ROBOTS_UNVERIFIABLE_ALLOWLIST
    return rp.can_fetch(USER_AGENT, url)


def fetch_once(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
    min_interval: float = DEFAULT_MIN_INTERVAL,
) -> tuple[bytes, Message]:
    """Perform exactly ONE conduct-compliant HTTP request.

    Every call is (a) robots-checked (fail-closed -- see ``robots_allowed``,
    including its one explicit, enumerated ``ROBOTS_UNVERIFIABLE_ALLOWLIST``
    exception), (b) rate-limited per host, and (c) sent with the identifying
    ``USER_AGENT`` -- a caller-supplied ``User-Agent`` header is stripped and
    replaced, not merged, so conduct identification is never optional per
    source, even by accident. There is deliberately NO caller-side parameter
    to skip the robots check: the only way to waive it for a specific host is
    to add a reviewed, evidenced entry to ``ROBOTS_UNVERIFIABLE_ALLOWLIST``
    above, not a one-line call-site edit.

    Raises ``PermissionError`` if robots.txt disallows *url*, or could not be
    verified AND the host is not on ``ROBOTS_UNVERIFIABLE_ALLOWLIST``. Raises
    the ordinary ``urllib.error.HTTPError`` / ``URLError`` / ``OSError``
    family on request failures, exactly like a raw ``urlopen()`` call would
    -- callers implement their own retry policy around this function
    (``robust_fetch``/``conditional_fetch`` below do so; scripts with their
    own cadence, e.g. NVD, call this directly per attempt).

    This is the ONLY function in this module -- and the only place in the
    whole ingest pipeline -- that calls ``urllib.request.urlopen()`` for a
    live-content fetch.

    Returns ``(body_bytes, response_headers)``; ``response_headers`` is the
    raw ``email.message.Message`` from the connection, so callers get
    case-insensitive ``.get("ETag")``-style lookups exactly as a raw
    ``urlopen()`` response would provide (a plain ``dict(resp.headers)``
    would silently lose that case-insensitivity).
    """
    if not robots_allowed(url, min_interval):
        raise PermissionError(
            f"refusing to fetch {url}: robots.txt disallows it for "
            f"User-Agent {USER_AGENT!r}, or robots.txt itself could not be "
            "verified and this host is not on ROBOTS_UNVERIFIABLE_ALLOWLIST "
            "(fail-closed -- see docs/INGESTION_CONDUCT.md)"
        )

    host = urlparse(url).netloc
    _rate_limit(host, min_interval)

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update({k: v for k, v in headers.items() if k.lower() != "user-agent"})

    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        resp_headers = resp.headers
    return body, resp_headers


def robust_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
    min_interval: float = DEFAULT_MIN_INTERVAL,
) -> bytes:
    """Fetch URL content with retry logic and disk caching.

    Returns cached content if the cache file exists and is at least
    *min_cache_bytes* large -- this warm-cache path reads local disk only
    and does NOT call ``robots_allowed()`` at all (there is no network
    request to check permission for; the content already sits on disk from
    a prior conduct-checked fetch). Otherwise fetches from *url* with up to
    *max_retries* attempts using exponential backoff (2 s, 4 s, 8 s, ...),
    routed through ``fetch_once()`` (robots/rate-limit/UA enforced on every
    attempt). A robots.txt refusal (``PermissionError``) is NOT retried --
    it propagates immediately and unwrapped, since retrying a confirmed
    policy block wastes backoff time for no chance of success, and since
    ``PermissionError`` is (surprisingly) an ``OSError`` subclass, this
    requires its own ``except`` clause ahead of the broad one below, not
    just careful wording here -- see that clause's comment.
    """
    if cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes:
        return cache_path.read_bytes()

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            data, _ = fetch_once(url, headers=headers, timeout=timeout, min_interval=min_interval)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            return data
        except PermissionError:
            # A robots.txt refusal is a confirmed policy block, not a
            # transient failure. PermissionError is (surprisingly) an
            # OSError subclass, so WITHOUT this clause ahead of the broad
            # OSError catch below, it would be retried with backoff and
            # then re-raised as a generic RuntimeError -- burning up to
            # 2+4=6s against a host that already told us no, AND masking
            # "refusing to fetch: robots.txt disallows it" behind
            # "Failed to fetch after N attempts", making a deliberate
            # policy block indistinguishable from a flaky host. Propagate
            # immediately and unwrapped instead (WS0-T4 bounce #1, D1).
            raise
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                delay = 2 ** attempt
                print(
                    f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}",
                    file=sys.stderr,
                )
                time.sleep(delay)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")


def _read_etag_sidecar(etag_path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not etag_path.exists():
        return result
    for line in etag_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("etag: "):
            result["etag"] = line[6:].strip()
        elif line.startswith("last-modified: "):
            result["last-modified"] = line[15:].strip()
    return result


def _write_etag_sidecar(etag_path: Path, etag: str | None, last_mod: str | None) -> None:
    lines: list[str] = []
    if etag:
        lines.append(f"etag: {etag}")
    if last_mod:
        lines.append(f"last-modified: {last_mod}")
    if lines:
        etag_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def conditional_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
    min_interval: float = DEFAULT_MIN_INTERVAL,
) -> tuple[bytes, bool]:
    """Fetch URL with ETag/Last-Modified conditional request support.

    Returns ``(content, changed)`` where *changed* is False if the server
    returned 304 Not Modified (cache is still valid). Routed through
    ``fetch_once()`` exactly like ``robust_fetch`` above -- same
    robots/rate-limit/UA enforcement and the same fail-fast-on-robots-block
    behavior.
    """
    etag_path = Path(str(cache_path) + ".etag")
    cache_warm = cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes

    hdrs: dict[str, str] = dict(headers) if headers else {}
    if cache_warm:
        saved = _read_etag_sidecar(etag_path)
        if saved.get("etag"):
            hdrs["If-None-Match"] = saved["etag"]
        if saved.get("last-modified"):
            hdrs["If-Modified-Since"] = saved["last-modified"]

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            data, resp_headers = fetch_once(
                url, headers=hdrs, timeout=timeout, min_interval=min_interval
            )
            etag = resp_headers.get("ETag")
            last_mod = resp_headers.get("Last-Modified")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            _write_etag_sidecar(etag_path, etag, last_mod)
            return data, True
        except PermissionError:
            # See the identical clause in robust_fetch() above for why this
            # must precede the OSError-inclusive catch below (WS0-T4 bounce
            # #1, D1): PermissionError IS an OSError, so without this it
            # would be retried with backoff and re-raised as an
            # indistinguishable generic RuntimeError instead of propagating
            # as the specific policy-block signal it is.
            raise
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return cache_path.read_bytes(), False
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")
