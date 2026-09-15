"""WS4-T10: the query-string URL over-merge (P0, user decision D25(b)).

``normalize_url`` used to do ``u.split("?")[0].split("#")[0]`` — dropping the
whole query string, so every ``articleView.html?idxno=N`` on a Korean CMS
(and every ``show_bug.cgi?id=N``, ``?p=N`` etc. elsewhere) collapsed onto one
weak dedup key. That silently bridged unrelated incidents through
``by_url``/``_reindex`` in ``dedupe_entries`` — e.g. INC-00554 accreted ~100
unrelated source rows this way. See
docs/audits/E21-tripwire-refresh-2026-09-14.md Findings 8/9 and PROGRESS.md's
E21 tripwire entry.

These tests fail on the pre-WS4-T10 ``normalize_url`` and pass on the fixed
one — proven by running them with the pre-fix implementation restored via
``git stash`` (see the WS4-T10 report for the paired failing/passing output).
"""

from __future__ import annotations

import merge_and_dedupe as m


def _mk(title, year=2026, cves=None, srcs=None, urls=None):
    return {
        "title": title, "year": year, "date": str(year),
        "cve_ids": cves or [], "source_ids": srcs or [],
        "references": [{"url": u, "type": "advisory"} for u in (urls or [])],
        "tags": [],
    }


# ---------------------------------------------------------------------------
# normalize_url unit-level behaviour
# ---------------------------------------------------------------------------

def test_normalize_url_keeps_distinct_query_ids():
    a = m.normalize_url("https://domin.co.kr/news/articleView.html?idxno=111")
    b = m.normalize_url("https://domin.co.kr/news/articleView.html?idxno=222")
    assert a != b


def test_normalize_url_drops_tracking_params_only():
    bare = m.normalize_url("https://example.com/story")
    tracked = m.normalize_url(
        "https://example.com/story?utm_source=twitter&utm_medium=social&fbclid=abc123"
    )
    assert bare == tracked == "example.com/story"


def test_normalize_url_fragment_and_trailing_slash_still_collapse():
    a = m.normalize_url("https://example.com/story/")
    b = m.normalize_url("https://example.com/story#read-more")
    c = m.normalize_url("https://example.com/story")
    assert a == b == c


def test_normalize_url_sorts_identifying_params_for_stable_key():
    a = m.normalize_url("https://example.com/x?b=2&a=1")
    b = m.normalize_url("https://example.com/x?a=1&b=2")
    assert a == b


# ---------------------------------------------------------------------------
# (a) the Korean-CMS shape: two unrelated entries must NOT merge
# ---------------------------------------------------------------------------

def test_cms_query_string_distinct_articles_do_not_merge():
    a = _mk("Korean defence ministry AI MOU", srcs=["OECD-AIM-A"],
            urls=["https://domin.co.kr/news/articleView.html?idxno=111"])
    b = _mk("Wildfire drone deployment", srcs=["OECD-AIM-B"],
            urls=["https://domin.co.kr/news/articleView.html?idxno=222"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 2
    assert not tombstones


# ---------------------------------------------------------------------------
# (b) true duplicates (tracking param / fragment / trailing slash) MUST
#     still merge
# ---------------------------------------------------------------------------

def test_true_duplicate_differing_by_tracking_param_still_merges():
    a = _mk("Tesla driver assist fatal crash", srcs=["AIID-1552"],
            urls=["https://example.com/tesla-crash-report"])
    b = _mk("Tesla driver assist fatal crash (syndicated)", srcs=["OECD-AIM-4590"],
            urls=["https://example.com/tesla-crash-report?utm_source=newsletter"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 1
    assert sorted(surviving[0]["source_ids"]) == ["AIID-1552", "OECD-AIM-4590"]


def test_true_duplicate_differing_by_fragment_and_slash_still_merges():
    a = _mk("Tesla driver assist fatal crash", srcs=["AIID-1552"],
            urls=["https://example.com/tesla-crash-report/"])
    b = _mk("Tesla driver assist fatal crash (syndicated)", srcs=["OECD-AIM-4590"],
            urls=["https://example.com/tesla-crash-report#section-2"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 1
    assert sorted(surviving[0]["source_ids"]) == ["AIID-1552", "OECD-AIM-4590"]


# ---------------------------------------------------------------------------
# (c) the 3-entry bridge fixture from the E21 audit / WS4-T10 brief
# ---------------------------------------------------------------------------

def test_cms_bridge_no_longer_collapses_three_incidents_into_one():
    # A: Korean defence-ministry MOU, on domin.co.kr idxno=111.
    a = _mk("Korean defence ministry AI MOU", srcs=["OECD-AIM-A"],
            urls=["https://domin.co.kr/news/articleView.html?idxno=111"])
    # B: unrelated bank anti-phishing launch, on m-i.kr idxno=222.
    b = _mk("Bank anti-phishing AI launch", srcs=["OECD-AIM-B"],
            urls=["https://m-i.kr/news/articleview.html?idxno=222"])
    # Bridge: a genuinely different story that happens to link both CMSes,
    # at DIFFERENT article ids (333 / 444) — the pre-fix collapse bridged A
    # and B through this row purely because the query strings were dropped.
    bridge = _mk("Roundup of regional AI deployments", srcs=["OECD-AIM-C"],
                 urls=["https://domin.co.kr/news/articleView.html?idxno=333",
                       "https://m-i.kr/news/articleview.html?idxno=444"])
    surviving, tombstones = m.dedupe_entries([a, b, bridge])
    assert len(surviving) == 3, [s["title"] for s in surviving]
    assert not tombstones, [t["title"] for t in tombstones]


def test_cms_bridge_collapses_on_prefix_normalize_url(monkeypatch):
    """Same fixture, with normalize_url monkeypatched back to the pre-fix
    query-dropping behaviour — demonstrates the bridge mechanism the fix
    closes, without relying on git state."""

    def _prefix_normalize_url(url: str) -> str:
        if not url:
            return ""
        u = url.strip().lower()
        import re as _re
        u = _re.sub(r"^https?://(www\.)?", "", u)
        u = u.split("?")[0].split("#")[0]
        u = u.rstrip("/")
        return u

    monkeypatch.setattr(m, "normalize_url", _prefix_normalize_url)

    a = _mk("Korean defence ministry AI MOU", srcs=["OECD-AIM-A"],
            urls=["https://domin.co.kr/news/articleView.html?idxno=111"])
    b = _mk("Bank anti-phishing AI launch", srcs=["OECD-AIM-B"],
            urls=["https://m-i.kr/news/articleview.html?idxno=222"])
    bridge = _mk("Roundup of regional AI deployments", srcs=["OECD-AIM-C"],
                 urls=["https://domin.co.kr/news/articleView.html?idxno=333",
                       "https://m-i.kr/news/articleview.html?idxno=444"])
    surviving, tombstones = m.dedupe_entries([a, b, bridge])
    assert len(surviving) == 1, [s["title"] for s in surviving]
    assert len(tombstones) == 1, [t["title"] for t in tombstones]


# ---------------------------------------------------------------------------
# (d) merge_into must not drop references that are distinct under the new
#     normalizer
# ---------------------------------------------------------------------------

def test_merge_into_keeps_distinct_query_string_references():
    target = _mk("Anchor incident", srcs=["OECD-AIM-A"],
                  urls=["https://domin.co.kr/news/articleView.html?idxno=111"])
    src = _mk("Absorbed row", srcs=["OECD-AIM-B"],
              urls=["https://domin.co.kr/news/articleView.html?idxno=222"])
    m.merge_into(target, src)
    urls = {r["url"] for r in target["references"]}
    assert "https://domin.co.kr/news/articleView.html?idxno=111" in urls
    assert "https://domin.co.kr/news/articleView.html?idxno=222" in urls
    assert len(target["references"]) == 2


def test_merge_into_still_dedupes_true_duplicate_references():
    target = _mk("Anchor incident", srcs=["OECD-AIM-A"],
                  urls=["https://example.com/story"])
    src = _mk("Syndicated copy", srcs=["OECD-AIM-B"],
              urls=["https://example.com/story?utm_source=newsletter"])
    m.merge_into(target, src)
    assert len(target["references"]) == 1
