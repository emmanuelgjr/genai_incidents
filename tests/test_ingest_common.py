"""Tests for ingest/common.py -- the repo's single network chokepoint
(WS0-T4 / invariant 5). Covers the original retry/conditional-fetch
mechanics (carried over from the pre-promotion scripts/ingest_utils.py) plus
the new conduct behaviour this module adds: identifying User-Agent, robots.txt
allow/deny (fail-closed), and per-host rate limiting.
"""

from __future__ import annotations

import urllib.error
from unittest.mock import patch, MagicMock

import pytest

import ingest.common as u


# ----------------------------------------------------------------------------
# robust_fetch / conditional_fetch retry mechanics (carried over as-is; the
# autouse fixture in conftest.py stubs robots_allowed() to True so these
# don't also need to model a robots.txt sub-fetch through the same mock).
# ----------------------------------------------------------------------------
def test_robust_fetch_returns_cached_content(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"x" * 2000)
    result = u.robust_fetch("https://example.com/data", cache, min_cache_bytes=1000)
    assert result == b"x" * 2000


def test_robust_fetch_skips_small_cache(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"tiny")
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"fresh data"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = u.robust_fetch("https://example.com/d", cache, min_cache_bytes=1000)
    assert result == b"fresh data"
    assert cache.read_bytes() == b"fresh data"


def test_robust_fetch_retries_on_failure(tmp_path):
    cache = tmp_path / "data.bin"
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("connection refused")
        try:
            u.robust_fetch("https://example.com/x", cache, max_retries=3)
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "connection refused" in str(e)
        assert mock_open.call_count == 3


def test_robust_fetch_succeeds_on_second_try(tmp_path):
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"ok"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = [urllib.error.URLError("timeout"), mock_resp]
        result = u.robust_fetch("https://example.com/x", cache, max_retries=3)
    assert result == b"ok"
    assert mock_open.call_count == 2


def test_conditional_fetch_cold_cache(tmp_path):
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"payload"
    mock_resp.headers.get.side_effect = lambda h, d=None: {
        "ETag": '"abc123"', "Last-Modified": "Sun, 25 May 2026 00:00:00 GMT"
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"payload"
    assert changed is True
    etag_file = tmp_path / "data.bin.etag"
    assert etag_file.exists()
    assert '"abc123"' in etag_file.read_text(encoding="utf-8")


def test_conditional_fetch_304_not_modified(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"cached payload")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "abc123"\n', encoding="utf-8")
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/d", 304, "Not Modified", {}, None
        )
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"cached payload"
    assert changed is False


def test_conditional_fetch_200_with_new_etag(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"old")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "old"\n', encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"new data"
    mock_resp.headers.get.side_effect = lambda h, d=None: {
        "ETag": '"new456"'
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"new data"
    assert changed is True
    assert '"new456"' in etag_file.read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# Identifying User-Agent (docs/INGESTION_CONDUCT.md)
# ----------------------------------------------------------------------------
def test_user_agent_names_project_and_contact():
    assert "genai_incidents" in u.USER_AGENT
    assert "emmanuelgjr@gmail.com" in u.USER_AGENT


def test_fetch_once_sends_identifying_user_agent():
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"body"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        u.fetch_once("https://example.com/x", min_interval=0)
    sent_req = mock_open.call_args[0][0]
    assert sent_req.get_header("User-agent") == u.USER_AGENT


def test_fetch_once_strips_caller_supplied_user_agent():
    """A caller passing its own User-Agent header must NOT reach the wire --
    conduct identification is not optional per source (this is the exact
    bypass ingest_cve_nvd_expanded.py had before WS0-T4: a hardcoded
    'ai-incidents-ingest/1.0' string)."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"body"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        u.fetch_once(
            "https://example.com/x",
            headers={"User-Agent": "some-other-agent/9.0"},
            min_interval=0,
        )
    sent_req = mock_open.call_args[0][0]
    assert sent_req.get_header("User-agent") == u.USER_AGENT


# ----------------------------------------------------------------------------
# robots.txt: fail-closed. These opt out of the autouse allow-everything
# stub to exercise the real robots_allowed()/_get_robots_parser() logic.
# ----------------------------------------------------------------------------
@pytest.mark.real_robots
def test_robots_allowed_true_on_permissive_rules():
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nAllow: /\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        assert u.robots_allowed("https://example.com/anything") is True


@pytest.mark.real_robots
def test_robots_allowed_false_on_disallow_rule():
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nDisallow: /private/\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        assert u.robots_allowed("https://example.com/private/data") is False
        assert u.robots_allowed("https://example.com/public/data") is True


@pytest.mark.real_robots
def test_robots_allowed_true_on_404_no_file_published():
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/robots.txt", 404, "Not Found", {}, None
        )
        assert u.robots_allowed("https://example.com/anything") is True


@pytest.mark.real_robots
def test_robots_allowed_false_when_unreachable_fail_closed():
    """A robots.txt that can't be verified at all (not 200, not 404) refuses
    the fetch -- fail CLOSED, not fail open."""
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("connection refused")
        assert u.robots_allowed("https://example.com/anything") is False


@pytest.mark.real_robots
def test_robots_denial_is_not_cached_so_a_later_check_can_recover():
    """A transient robots.txt failure must not poison the cache -- the very
    next check should get a fresh attempt, not a stale refusal.

    Both calls target the same host and pass min_interval=0 (WS0-T4 bounce
    #1, R3 follow-up): now that the robots.txt fetch itself is paced through
    the same per-host rate limiter as content fetches, two real
    robots_allowed() calls this close together for the SAME host would
    otherwise burn a real ~1s DEFAULT_MIN_INTERVAL sleep in the second call
    -- this test is about cache-poisoning, not pacing, so it opts out of
    pacing explicitly rather than re-introduce the accidental-real-sleep
    problem this task's D1 pass already removed elsewhere.
    """
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nAllow: /\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("connection refused")
        assert u.robots_allowed("https://example.com/x", min_interval=0) is False
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        assert u.robots_allowed("https://example.com/x", min_interval=0) is True


@pytest.mark.real_robots
def test_fetch_once_raises_permission_error_when_robots_unverifiable():
    """A robots.txt fetch that itself fails (e.g. a 403 on /robots.txt) is
    the COULD-NOT-VERIFY / fail-closed path, not a genuine Disallow -- see
    test_fetch_once_raises_permission_error_when_robots_disallows below for
    that. _get_robots_parser() retries once on a transient-looking failure
    (module docstring), so this exercises exactly 2 urlopen calls -- both
    against robots.txt, never the content URL itself."""
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/robots.txt", 403, "Forbidden", {}, None
        )
        with pytest.raises(PermissionError):
            u.fetch_once("https://example.com/x", min_interval=0)
    # Both calls were the robots.txt retry pair -- the disallowed content
    # fetch itself must never have been attempted.
    assert mock_open.call_count == 2
    for call in mock_open.call_args_list:
        assert call[0][0].full_url == "https://example.com/robots.txt"


@pytest.mark.real_robots
def test_fetch_once_raises_permission_error_when_robots_disallows():
    """The genuine-disallow path, distinct from the unverifiable path above:
    robots.txt is fetched successfully (one call, no retry needed) and its
    rules explicitly forbid the URL."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nDisallow: /x\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp) as mock_open:
        with pytest.raises(PermissionError):
            u.fetch_once("https://example.com/x", min_interval=0)
    # Only the robots.txt check ran -- the disallowed content fetch itself
    # must never have been attempted.
    assert mock_open.call_count == 1
    assert mock_open.call_args[0][0].full_url == "https://example.com/robots.txt"


# ----------------------------------------------------------------------------
# ROBOTS_UNVERIFIABLE_ALLOWLIST: the ONLY way the fail-closed refusal above
# can be waived (finding 2/3, WS0-T4 conduct-half report). No caller-side
# parameter exists -- see fetch_once()'s signature/docstring -- so these
# tests exercise the allowlist dict directly rather than a call-site flag.
# ----------------------------------------------------------------------------
@pytest.mark.real_robots
def test_robots_allowed_true_for_allowlisted_unverifiable_host(monkeypatch):
    """A host on the allowlist whose robots.txt cannot be fetched at all is
    treated as allowed -- the CISA case this allowlist exists for."""
    monkeypatch.setitem(
        u.ROBOTS_UNVERIFIABLE_ALLOWLIST, "example.com",
        {"reason": "test", "evidence_date": "2026-07-29", "evidence": "test",
         "still_enforced": "rate limit and UA"},
    )
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/robots.txt", 403, "Forbidden", {}, None
        )
        assert u.robots_allowed("https://example.com/anything") is True


@pytest.mark.real_robots
def test_robots_allowed_false_for_non_allowlisted_unverifiable_host():
    """The allowlist is per-host, not a global fail-open switch -- a host NOT
    on it still refuses when unverifiable, exactly as before this dict
    existed."""
    assert "not-on-the-allowlist.example.com" not in u.ROBOTS_UNVERIFIABLE_ALLOWLIST
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.HTTPError(
            "https://not-on-the-allowlist.example.com/robots.txt", 403, "Forbidden", {}, None
        )
        assert u.robots_allowed("https://not-on-the-allowlist.example.com/x") is False


@pytest.mark.real_robots
def test_robots_allowlist_does_not_override_an_explicit_disallow(monkeypatch):
    """The allowlist waives only the UNVERIFIABLE outcome, never a genuine
    Disallow rule -- an allowlisted host whose robots.txt actually loads and
    says no is still refused."""
    monkeypatch.setitem(
        u.ROBOTS_UNVERIFIABLE_ALLOWLIST, "example.com",
        {"reason": "test", "evidence_date": "2026-07-29", "evidence": "test",
         "still_enforced": "rate limit and UA"},
    )
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nDisallow: /private/\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        assert u.robots_allowed("https://example.com/private/data") is False
        assert u.robots_allowed("https://example.com/public/data") is True


def test_robots_unverifiable_allowlist_is_pinned_and_fully_evidenced():
    """WS0-T4 bounce #1, R1: ROBOTS_UNVERIFIABLE_ALLOWLIST waives a real
    conduct safeguard (fail-closed robots checking) for a named host, but
    nothing at runtime reads its 'reason'/'evidence_date'/'evidence'/
    'still_enforced' fields -- robots_allowed() only checks dict
    MEMBERSHIP. A one-line edit
    (``ROBOTS_UNVERIFIABLE_ALLOWLIST["evil.example.com"] = {}``) waives
    fail-closed for a new host with zero evidence and passes the rest of
    this suite -- the exact anti-pattern (an opt-out reachable by a one-line
    edit) the check_robots parameter was removed for. This test is the
    enforcement those fields don't otherwise get: it pins the exact host set
    (mirroring test_literal_accept_criterion_grep_is_documented_not_silently_clean's
    pinned-set pattern in test_network_chokepoint.py -- a new entry requires
    a deliberate update here, not a silent pass) and requires every entry to
    carry all four fields as non-empty strings."""
    assert set(u.ROBOTS_UNVERIFIABLE_ALLOWLIST.keys()) == {"www.cisa.gov"}, (
        "ROBOTS_UNVERIFIABLE_ALLOWLIST's host set changed. This test doesn't "
        "block a deliberate, evidenced addition -- but nothing else in the "
        "codebase checks that a new entry's evidence meets the same bar as "
        "www.cisa.gov's (dated, reproducible, multi-UA verification; see "
        "docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md), so "
        "update this assertion only after confirming that by hand."
    )
    required_fields = {"reason", "evidence_date", "evidence", "still_enforced"}
    for host, entry in u.ROBOTS_UNVERIFIABLE_ALLOWLIST.items():
        missing = required_fields - entry.keys()
        assert not missing, f"{host}: missing required allowlist field(s) {missing}"
        for field in required_fields:
            value = entry[field]
            assert isinstance(value, str) and value.strip(), (
                f"{host}: field {field!r} must be a non-empty string, got {value!r}"
            )


@pytest.mark.real_robots
def test_fetch_once_succeeds_for_allowlisted_unverifiable_host(monkeypatch):
    """End-to-end: fetch_once() itself (not just robots_allowed()) proceeds
    for an allowlisted host whose robots.txt is unverifiable, and rate
    limiting / the identifying User-Agent still apply to the content fetch
    that follows."""
    monkeypatch.setitem(
        u.ROBOTS_UNVERIFIABLE_ALLOWLIST, "example.com",
        {"reason": "test", "evidence_date": "2026-07-29", "evidence": "test",
         "still_enforced": "rate limit and UA"},
    )
    content_resp = MagicMock()
    content_resp.read.return_value = b"payload"
    content_resp.__enter__ = lambda s: s
    content_resp.__exit__ = MagicMock(return_value=False)

    def fake_urlopen(req, timeout=None):
        if "robots.txt" in req.full_url:
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)
        assert req.get_header("User-agent") == u.USER_AGENT
        return content_resp

    with patch("ingest.common.urllib.request.urlopen", side_effect=fake_urlopen), \
         patch("ingest.common.time.sleep"):
        body, _ = u.fetch_once("https://example.com/x", min_interval=0)
    assert body == b"payload"


def test_fetch_once_has_no_check_robots_bypass_parameter():
    """The robots check must not be a caller-settable opt-out (finding 3) --
    the only waiver mechanism is the reviewed, evidenced
    ROBOTS_UNVERIFIABLE_ALLOWLIST dict above."""
    import inspect
    params = inspect.signature(u.fetch_once).parameters
    assert "check_robots" not in params


# ----------------------------------------------------------------------------
# WS0-T4 bounce #1, R3: the robots.txt fetch itself must share the SAME
# per-host rate limiter as the content fetch, not bypass it via a direct
# unpaced urlopen() call.
# ----------------------------------------------------------------------------
@pytest.mark.real_robots
def test_get_robots_parser_routes_through_the_shared_rate_limiter(monkeypatch):
    """_get_robots_parser() must call the SAME _rate_limit() function
    content fetches use, with the host and the min_interval it was given --
    not an unpaced urlopen() call. Verified by interaction (mocking
    _rate_limit itself) rather than by timing, so the test stays fast and
    deterministic."""
    calls: list[tuple[str, float]] = []

    def fake_rate_limit(host: str, min_interval: float) -> None:
        calls.append((host, min_interval))

    monkeypatch.setattr(u, "_rate_limit", fake_rate_limit)

    mock_resp = MagicMock()
    mock_resp.read.return_value = b"User-agent: *\nAllow: /\n"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        assert u.robots_allowed("https://example.com/x", min_interval=2.5) is True
    assert calls == [("example.com", 2.5)]


def test_fetch_once_forwards_its_min_interval_to_the_robots_check(monkeypatch):
    """The robots probe and the content fetch must share ONE pacing budget
    for a host, not two independent ones -- fetch_once() must forward the
    min_interval a caller gave it into robots_allowed(), rather than always
    using the module default regardless of what the caller asked for (e.g.
    NVD's tighter documented cadence)."""
    seen: dict[str, float] = {}

    def fake_robots_allowed(url: str, min_interval: float = u.DEFAULT_MIN_INTERVAL) -> bool:
        seen["min_interval"] = min_interval
        return True

    monkeypatch.setattr(u, "robots_allowed", fake_robots_allowed)
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"body"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest.common.urllib.request.urlopen", return_value=mock_resp):
        u.fetch_once("https://example.com/x", min_interval=3.3)
    assert seen["min_interval"] == 3.3


# ----------------------------------------------------------------------------
# Per-host rate limiting
# ----------------------------------------------------------------------------
def test_rate_limit_waits_for_minimum_interval(monkeypatch):
    times = iter([100.0, 100.2])
    monkeypatch.setattr(u.time, "monotonic", lambda: next(times))
    sleeps: list[float] = []
    monkeypatch.setattr(u.time, "sleep", lambda s: sleeps.append(s))

    u._rate_limit("example.com", min_interval=1.0)
    u._rate_limit("example.com", min_interval=1.0)

    assert sleeps == pytest.approx([0.8])


def test_rate_limit_does_not_block_a_different_host(monkeypatch):
    monkeypatch.setattr(u.time, "monotonic", lambda: 100.0)
    sleeps: list[float] = []
    monkeypatch.setattr(u.time, "sleep", lambda s: sleeps.append(s))

    u._rate_limit("a.example.com", min_interval=5.0)
    u._rate_limit("b.example.com", min_interval=5.0)

    assert sleeps == []


def test_rate_limit_zero_interval_is_a_no_op(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(u.time, "sleep", lambda s: sleeps.append(s))
    u._rate_limit("example.com", min_interval=0)
    u._rate_limit("example.com", min_interval=0)
    assert sleeps == []


# ----------------------------------------------------------------------------
# fetch_to_file (streamed download for multi-hundred-MB release assets)
# ----------------------------------------------------------------------------
def _stream_resp(chunks):
    resp = MagicMock()
    resp.read.side_effect = list(chunks) + [b""]
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_fetch_to_file_streams_hashes_and_renames(tmp_path):
    import hashlib

    dest = tmp_path / "sub" / "asset.zip"
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        mock_open.return_value = _stream_resp([b"abc", b"def"])
        digest, size = u.fetch_to_file("https://example.com/a.zip", dest, chunk_size=3)
    assert size == 6 and dest.read_bytes() == b"abcdef"
    assert digest == hashlib.sha256(b"abcdef").hexdigest()
    assert not (tmp_path / "sub" / "asset.zip.part").exists()
    sent = mock_open.call_args[0][0]
    assert sent.get_header("User-agent") == u.USER_AGENT


def test_fetch_to_file_never_leaves_a_partial_file_as_the_result(tmp_path):
    dest = tmp_path / "asset.zip"
    with patch("ingest.common.urllib.request.urlopen") as mock_open, \
         patch("ingest.common.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("reset")
        with pytest.raises(RuntimeError):
            u.fetch_to_file("https://example.com/a.zip", dest, max_retries=2)
    assert not dest.exists()


@pytest.mark.real_robots
def test_fetch_to_file_honours_robots_refusal(tmp_path, monkeypatch):
    monkeypatch.setattr(u, "robots_allowed", lambda url, min_interval=1.0: False)
    with patch("ingest.common.urllib.request.urlopen") as mock_open:
        with pytest.raises(PermissionError):
            u.fetch_to_file("https://example.com/a.zip", tmp_path / "x")
    mock_open.assert_not_called()


# ----------------------------------------------------------------------------
# Redirect targets get the same robots check and pacing (gate A4)
# ----------------------------------------------------------------------------
import http.server
import threading


def _serve(handler_cls):
    srv = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _two_hosts():
    hits = {"cdn": 0}

    class Cdn(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            hits["cdn"] += 1
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"asset-bytes")

        def log_message(self, *a):
            pass

    cdn = _serve(Cdn)

    class Origin(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{cdn.server_port}/asset")
            self.end_headers()

        def log_message(self, *a):
            pass

    return _serve(Origin), cdn, hits


def test_redirect_to_a_disallowed_host_is_refused_before_any_request(monkeypatch, tmp_path):
    origin, cdn, hits = _two_hosts()
    try:
        checked = []

        def robots(url, min_interval=1.0):
            checked.append(url)
            return f":{cdn.server_port}" not in url      # the CDN host disallows us

        monkeypatch.setattr(u, "robots_allowed", robots)
        with pytest.raises(PermissionError, match="redirect"):
            u.fetch_once(f"http://127.0.0.1:{origin.server_port}/dl", min_interval=0)
        assert hits["cdn"] == 0                           # never contacted
        assert any(f":{cdn.server_port}" in c for c in checked)
        with pytest.raises(PermissionError):              # same for the streaming path
            u.fetch_to_file(f"http://127.0.0.1:{origin.server_port}/dl", tmp_path / "a", min_interval=0)
        assert hits["cdn"] == 0 and not (tmp_path / "a").exists()
    finally:
        origin.shutdown(); cdn.shutdown()


def test_redirect_to_an_allowed_host_is_followed_and_paced(monkeypatch):
    origin, cdn, hits = _two_hosts()
    try:
        paced = []
        monkeypatch.setattr(u, "_rate_limit", lambda host, mi: paced.append(host))
        body, _ = u.fetch_once(f"http://127.0.0.1:{origin.server_port}/dl", min_interval=0)
        assert body == b"asset-bytes" and hits["cdn"] == 1
        assert f"127.0.0.1:{cdn.server_port}" in paced     # the redirect target was paced too
    finally:
        origin.shutdown(); cdn.shutdown()
