"""WS4-T10: the query-string URL over-merge (P0, user decision D25(b)).

``normalize_url`` used to do ``u.split("?")[0].split("#")[0]`` — dropping the
whole query string, so every ``articleView.html?idxno=N`` on a Korean CMS
(and every ``show_bug.cgi?id=N``, ``?p=N`` etc. elsewhere) collapsed onto one
weak dedup key. That silently bridged unrelated incidents through
``by_url``/``_reindex`` in ``dedupe_entries`` — e.g. INC-00554 accreted ~100
unrelated source rows this way. See
docs/audits/E21-tripwire-refresh-2026-09-14.md Findings 8/9 and PROGRESS.md's
E21 tripwire entry.

Most of these tests fail on the pre-WS4-T10 ``normalize_url`` and pass on
the fixed one — proven by running them against a detached scratch worktree
checked out at the pre-fix commit (``eeb7ca9c``), never via ``git stash``
(the stash stack is shared across this session's worktrees). See
``PROGRESS.md``'s WS4-T10 board entry and the committed Phase B delta
artifact (``docs/audits/WS4-T10-phaseB-delta-2026-09-15.json``) for the
paired failing/passing output and re-derivable evidence.

**Advisory A1 (BOUNCE #1):** the "true duplicate still merges" cases (b)
below CANNOT fail on pre-fix code by construction — the old
``normalize_url`` dropped the whole query string unconditionally, so any
two URLs differing only by query string (tracking param or otherwise)
already collapsed onto the same key. They are regression guards, not
before/after proofs. What DOES discriminate a too-narrow fix from a correct
one is a mutant that keeps the query string but never drops tracking
params (or only recognizes one CMS's identifying param, e.g. an
``idxno``-only allowlist) — such a mutant fails (a)/(b) or the E21
full-corpus tripwire respectively, which is what BOUNCE #1's gate used to
prove these tests actually discriminate.
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
# WS4-T10 BOUNCE #1 defect 2: `web_view` false-split fix (INC-08183)
# ---------------------------------------------------------------------------

def test_normalize_url_drops_web_view_presentational_flag():
    """The exact INC-08183 shape: a bare URL and its `?&web_view=true` twin
    reference the SAME ReversingLabs blog post and must key identically --
    on pre-BOUNCE#1 code `web_view` wasn't blocklisted, so the two keyed
    apart, split the row's references across two dedup keys, and flipped
    the row's anchor to unrelated content (see the committed Phase B delta
    for the measured before/after)."""
    bare = m.normalize_url(
        "https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face"
    )
    tagged = m.normalize_url(
        "https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face?&web_view=true"
    )
    assert bare == tagged


def test_normalize_url_drops_other_bounce1_tracking_misses():
    """The other confirmed-presentational/tracking blocklist misses named
    in BOUNCE #1's advisory A3, each backed by a real ingest/*.json URL
    (see the classification comment above `_URL_TRACKING_PARAMS`)."""
    # Asahi Shimbun: constant `iref=ogimage_rek` referrer tag.
    assert (
        m.normalize_url("https://www.asahi.com/articles/ASV170TDGV17UTIL004M.html")
        == m.normalize_url("https://www.asahi.com/articles/ASV170TDGV17UTIL004M.html?iref=ogimage_rek")
    )
    # Sohu CMS: edtsign/edtcode/scm tracking cruft, path already unique.
    assert (
        m.normalize_url("http://news.sohu.com/a/989338739_119659")
        == m.normalize_url(
            "http://news.sohu.com/a/989338739_119659"
            "?edtsign=C985E43453F9FD552BC8CE887E7496B82A788452"
            "&edtcode=xW5WLWm834RlWgB9uxAiFw%3D%3D&scm=10001.663_14-200000.0.0-0-0-0-0."
        )
    )
    # Liferay portlet plumbing: framework navigation state, not identity.
    # WS4-T10 ATTEMPT 3 (advisory A2 / mutant N5): uses the REAL
    # `_com_liferay_..._redirect` shape (57 occurrences in
    # ingest/cve_nvd_expanded.json), not a synthetic `p_p_*` shape -- a
    # mutant that removes `_com_liferay_.*` from the blocklist must fail
    # this test. `p_p_id`/`p_p_lifecycle`/`p_p_state`/`p_p_mode` were
    # removed from the blocklist entirely (0 corpus occurrences, so they
    # were speculative, not evidenced) -- see the classification comment.
    assert (
        m.normalize_url(
            "https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/"
            "jekt/content/cve-2021-33326-xss-with-the-title-of-a-modal-window"
            "?p_r_p_assetEntryId=121610771"
            "&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect="
            "https%3A%2F%2Fliferay.dev%3A443%2Fportal%2Fsecurity%2Fknown-vulnerabilities"
        )
        == m.normalize_url(
            "https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/"
            "jekt/content/cve-2021-33326-xss-with-the-title-of-a-modal-window"
            "?p_r_p_assetEntryId=121610771"
        )
    )


def test_normalize_url_liferay_redirect_mutant_n5_fails_without_prefix_match():
    """Direct regression guard for mutant N5 (BOUNCE #2): if
    `_com_liferay_.*` were ever removed from `_URL_TRACKING_PARAMS`, this
    fails -- the redirect param's own value is a huge percent-encoded URL
    that would otherwise key two fetches of the identical Liferay page
    apart."""
    assert m._URL_TRACKING_PARAMS.match(
        "_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_jekt_redirect"
    )


def test_normalize_url_keeps_liferay_asset_entry_id_as_identifying():
    """`p_r_p_assetEntryId` IS kept (genuinely identifying, even though
    redundant with the path's own CVE slug) -- only the `_com_liferay_*`
    portlet-instance/redirect plumbing and the generic `p_p_*` state params
    are dropped."""
    a = m.normalize_url("https://liferay.dev/x/y?p_r_p_assetEntryId=121610771")
    b = m.normalize_url("https://liferay.dev/x/y?p_r_p_assetEntryId=121611661")
    assert a != b


# ---------------------------------------------------------------------------
# WS4-T10 BOUNCE #1 advisory A4: query-VALUE case is preserved; bare `ref`
# is deliberately kept (not blocklisted)
# ---------------------------------------------------------------------------

def test_normalize_url_preserves_query_value_case():
    """Only the scheme/host/path and query KEYS are lowercased -- a
    case-significant identifying VALUE (e.g. a mixed-case token or slug)
    must not fold two distinct resources onto one key."""
    a = m.normalize_url("https://example.com/x?token=AbC123")
    b = m.normalize_url("https://example.com/x?token=abc123")
    assert a != b
    # the key itself is still lowercased for stable sorting/matching
    assert m.normalize_url("https://example.com/x?TOKEN=AbC123") == a


def test_normalize_url_keeps_bare_ref_as_potentially_identifying():
    """`ref=` is deliberately NOT blocklisted (advisory A4): on GitHub it
    identifies a branch/tag (`?ref=main` vs `?ref=release-1.0`), so folding
    it would risk a false merge, the exact harm this task exists to close."""
    a = m.normalize_url("https://github.com/org/repo/blob/x/y.py?ref=main")
    b = m.normalize_url("https://github.com/org/repo/blob/x/y.py?ref=release-1.0")
    assert a != b
    # `ref_src` and `referrer` (unambiguous tracking) are still dropped.
    assert (
        m.normalize_url("https://example.com/story")
        == m.normalize_url("https://example.com/story?ref_src=twitter&referrer=fb")
    )


# ---------------------------------------------------------------------------
# WS4-T10 BOUNCE #1 advisory A2: other real identifying query-param shapes
# beyond the Korean-CMS `idxno=` case, so the general (not allowlisted)
# design is exercised explicitly, not just incidentally via the E21 tripwire
# ---------------------------------------------------------------------------

def test_normalize_url_keeps_vscode_marketplace_item_name():
    a = m.normalize_url("https://marketplace.visualstudio.com/items?itemName=rahmanazhar.saka-dev")
    b = m.normalize_url("https://marketplace.visualstudio.com/items?itemName=tianguaduizhang.claude-dev-china")
    assert a != b


def test_normalize_url_keeps_mediawiki_page_param():
    a = m.normalize_url("https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-34158")
    b = m.normalize_url("https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-28731")
    assert a != b


def test_normalize_url_keeps_bare_id_and_p_params():
    a = m.normalize_url("https://cve.org/CVERecord?id=CVE-2025-0001")
    b = m.normalize_url("https://cve.org/CVERecord?id=CVE-2025-0002")
    assert a != b
    c = m.normalize_url("https://bugzilla.example.org/show_bug.cgi?id=111")
    d = m.normalize_url("https://bugzilla.example.org/show_bug.cgi?id=222")
    assert c != d
    e = m.normalize_url("https://forum.example.org/viewtopic.php?p=111")
    f = m.normalize_url("https://forum.example.org/viewtopic.php?p=222")
    assert e != f


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
