"""Unit tests for the OECD AIM ingester's union-with-existing behaviour."""

from __future__ import annotations

import json
import time

import ingest_oecd_aim as o


def _entry(sid, title):
    return {"source_id": sid, "title": title, "year": 2026,
            "references": [{"url": "https://oecd.ai/en/incidents/x"}]}


def test_union_keeps_aged_out_existing_entries():
    # Fresh fetch lost OLD-2 (it aged out of the 3000-URL window).
    fresh = [_entry("OECD-AIM-NEW-1", "new one")]
    existing = [_entry("OECD-AIM-OLD-2", "old two")]
    out = o.union_with_existing(fresh, existing)
    ids = {e["source_id"] for e in out}
    assert ids == {"OECD-AIM-NEW-1", "OECD-AIM-OLD-2"}


def test_union_fresh_wins_on_conflict():
    fresh = [_entry("OECD-AIM-1", "fresh title")]
    existing = [_entry("OECD-AIM-1", "stale title")]
    out = o.union_with_existing(fresh, existing)
    assert len(out) == 1
    assert out[0]["title"] == "fresh title"


def test_union_output_sorted_by_source_id():
    fresh = [_entry("OECD-AIM-3", "c"), _entry("OECD-AIM-1", "a")]
    existing = [_entry("OECD-AIM-2", "b")]
    out = o.union_with_existing(fresh, existing)
    assert [e["source_id"] for e in out] == [
        "OECD-AIM-1", "OECD-AIM-2", "OECD-AIM-3"
    ]


def test_union_drops_entries_without_source_id():
    fresh = [{"title": "no id", "references": []}]
    existing = [{"title": "also no id"}]
    assert o.union_with_existing(fresh, existing) == []


# --- E21 narrative-reduction: build_description() / classify_corpus_signal() /
# --- reclassify_attack_vector_from_narrative() ------------------------------


def test_build_description_never_contains_narrative_text():
    """The whole point of the reduction: no summary/evidences text reaches
    the template, only structural facts."""
    narrative = "This scandalous incident shocked regulators worldwide."
    desc = o.build_description(
        "OECD-AIM-2026-01-01-aaaa", "2026-01-01",
        "https://oecd.ai/en/incidents/2026-01-01-aaaa",
        "Acme Corp", "deepfake",
    )
    assert narrative not in desc
    assert "OECD-AIM-2026-01-01-aaaa" in desc
    assert "2026-01-01" in desc
    assert "Acme Corp" in desc
    assert "deepfake" in desc
    assert "https://oecd.ai/en/incidents/2026-01-01-aaaa" in desc


def test_build_description_omits_optional_fields_when_absent():
    desc = o.build_description(
        "OECD-AIM-2026-01-01-bbbb", "", "https://oecd.ai/en/incidents/2026-01-01-bbbb", "", "other"
    )
    assert "Classified attack vector" not in desc  # "other" is not informative
    assert "Entities named" not in desc
    assert "OECD-AIM-2026-01-01-bbbb" in desc


def test_build_description_respects_length_cap():
    desc = o.build_description(
        "OECD-AIM-x", "2026-01-01", "https://oecd.ai/en/incidents/x",
        "A" * 2000, "deepfake",
    )
    assert len(desc) <= 1500


def test_classify_corpus_signal_security_keyword_wins():
    assert o.classify_corpus_signal(
        "Voice clone scam", "Fraudsters used an AI voice clone to steal money.", ["oecd-aim"]
    ) == "security"


def test_classify_corpus_signal_ai_harm_when_no_security_keyword():
    assert o.classify_corpus_signal(
        "Biased hiring tool", "The AI system showed discriminatory bias against candidates.", ["oecd-aim"]
    ) == "ai-harm"


def test_classify_corpus_signal_defaults_to_security():
    assert o.classify_corpus_signal("Neutral incident", "Nothing keyword-worthy here.", ["oecd-aim"]) == "security"


def test_classify_corpus_signal_matches_merge_and_dedupe_classifier():
    """classify_corpus_signal() must agree with merge_and_dedupe.py's own
    _classify_corpus() on the identical text -- this IS the decoupling
    guarantee (0 unintended corpus moves): the persisted ingest-time value
    must be exactly what the merge-time classifier would have produced from
    the same pre-reduction narrative."""
    import merge_and_dedupe as m

    title = "Deepfake voice clone targets bank"
    narrative = "Scammers used an AI-generated voice clone to authorize a fraudulent wire transfer."
    tags = ["oecd-aim"]
    signal_result = o.classify_corpus_signal(title, narrative, tags)
    merge_result = m._classify_corpus({"title": title, "description": narrative, "tags": tags})
    assert signal_result == merge_result == "security"


def test_reclassify_attack_vector_from_narrative_rescues_other():
    rescued = o.reclassify_attack_vector_from_narrative(
        "other", "AI incident", "The chatbot spread misinformation about a public figure."
    )
    assert rescued == "misinformation"


def test_reclassify_attack_vector_from_narrative_leaves_non_other_untouched():
    assert o.reclassify_attack_vector_from_narrative(
        "deepfake", "AI incident", "Completely unrelated narrative text."
    ) == "deepfake"


def test_reclassify_attack_vector_from_narrative_stays_other_with_no_match():
    assert o.reclassify_attack_vector_from_narrative(
        "other", "AI incident", "Nothing keyword-worthy in this narrative at all."
    ) == "other"


def test_normalize_body_description_never_contains_summary_or_evidences():
    """End-to-end normalize_body(): summary/evidences text must never reach
    the persisted description, and corpus must be set from that same
    (discarded) narrative signal."""
    body = {
        "id": "2026-01-01-dead",
        "title": "Deepfake voice clone scam targets bank customers",
        "date": "2026-01-01",
        "summary": (
            "Fraudsters used an AI-generated voice clone to impersonate a "
            "bank executive and authorize a fraudulent wire transfer of "
            "USD 500,000, exploiting deepfake technology and stolen credentials."
        ),
        "evidences": ["A police report confirmed the scam."],
        "company": ["Example Bank"],
        "articles": [],
        "aiid_ids": [],
    }
    entry = o.normalize_body(body, "https://oecd.ai/en/incidents/2026-01-01-dead")
    assert entry is not None
    assert "Fraudsters used an AI-generated voice clone" not in entry["description"]
    assert "police report" not in entry["description"]
    assert entry["source_id"] in entry["description"]
    assert entry["corpus"] == "security"  # "voice clone" is a security keyword
    assert entry["attack_vector"] == "deepfake"


# --- WS4-T11: the 800 KB page-truncation parser-integrity bug ---------------
# --- (BOUNCE #1 hardened: cap-size coverage, a real byte-level straddle, ---
# --- honest per-reason accounting, and mutant-resistant fixtures) ----------
#
# Gate-measured defect (E21 tripwire, PROGRESS.md "E21 TRIPWIRE FIRED"):
# scripts/ingest_oecd_aim.py's old fetch_page() did
# `return data[:800_000].decode("utf-8", errors="replace")`, which silently
# truncates any page whose <script id="ng-state"> JSON blob starts at or
# straddles byte 800,000. extract_state() then finds no (or a corrupt) match
# and the page is folded into "unparseable" -- indistinguishable from a
# genuinely broken page. In the 2026-09-14 full crawl this silently dropped
# ~38 real incidents on every run.
#
# BOUNCE #1 (red-reviewer) found the fix correct but the guard too weak:
# defect 1) the only large-page test topped out at ~852 KB, so mutant caps at
#    853 KB/900 KB/1 MB (real OECD shell pages run ~949,653 bytes) passed
#    all 19 tests undetected;
# defect 2) the "straddle" test's own numbers put the ENTIRE JSON blob past
#    byte 800,000 (script opens at 799,995; JSON spans 800,041-800,155), so
#    it wasn't testing a straddle at all;
# defect 3) `main()`'s single ok/"unparseable" split still folds three
#    distinct failure modes into one bucket, including the 1852 real
#    legacy-numeric-slug pages the E21 audit found (a wrong ng-state shape,
#    not absence) -- the same undistinguished-bucket shape that hid the 38
#    truncated pages in the first place;
# defect 4) the committed memory docstring claimed threads hold "a few pages
#    ... negligible", false: `main()` retained ALL fetched pages
#    simultaneously in a `pages` dict (multi-GB at the real crawl window).
#
# All four are addressed below: `fetch_and_extract()` (memory), the
# `REASON_*` / `_extract_state_detail()` / `_tally_reasons()` accounting
# machinery (honesty), and this file's rebuilt fixtures (cap coverage +
# geometrically-verified straddle), plus the advisories (network guard,
# a simulated cold-fetch-branch test, a dedicated non-ASCII codec pin, and
# trailing-`<script>`-tag fixtures proving the regex's laziness is
# load-bearing).
#
# These tests exercise the REAL fetch_page() -> extract_state() path via
# robust_fetch()'s warm-cache disk-read branch (ingest/common.py:404-405)
# by default: they write real HTML bytes to a cache file on disk and let
# fetch_page() read it back exactly as it would a page cached from a prior
# conduct-checked network fetch. `_write_cached_page()` additionally patches
# `ingest.common.fetch_once` to raise if it's ever reached, so a broken
# cache-seeding assumption fails loudly instead of silently attempting a
# real fetch against oecd.ai. One test (`test_fetch_page_cold_path_does_not_
# truncate`) deliberately exercises the COLD branch instead, via a
# monkeypatched `fetch_once` returning synthetic bytes -- still no network.

import ingest.common as _common


NG_STATE_INCIDENT = {"id": "2026-05-01-feed", "title": "Large OECD AIM page parser-integrity test incident"}


def _ng_state_script_html(body: dict) -> str:
    """The exact `<script id="ng-state">...</script>` shape extract_state()
    parses: a dict whose value has a `"b"` key holding the incident body.

    `ensure_ascii=False` is deliberate, not cosmetic: `json.dumps()`
    defaults to escaping every non-ASCII character to a `\\uXXXX` sequence,
    which is pure ASCII on the wire either way -- a fixture built with the
    default would silently never exercise a raw multi-byte UTF-8 decode at
    all, no matter what codec `fetch_page()` used, defeating the whole
    point of `test_fetch_page_decodes_non_ascii_title_exactly` (advisory 3).
    Real Angular `JSON.stringify()` output (what an actual OECD AIM page
    emits) does not escape non-ASCII either, so this also matches the real
    wire format more closely."""
    state = {"AppStateKey_0": {"b": body}}
    return f'<script id="ng-state" type="application/json">{json.dumps(state, ensure_ascii=False)}</script>'


def _make_page(
    script_offset_bytes: int,
    tail_bytes: int = 2000,
    body: dict | None = None,
    trailing_script_html: bytes = b"",
) -> bytes:
    """Build a synthetic HTML page (as bytes) where the ng-state <script>
    tag begins at approximately `script_offset_bytes` into the page, with
    `tail_bytes` of filler after it (to simulate the rest of a real Angular
    SPA page: footer markup, other scripts, etc.).

    `trailing_script_html`, if given, is inserted immediately after the
    ng-state script's own closing `</script>` tag (advisory 4, WS4-T11
    BOUNCE #1): further `<script>` blocks on the page, which a correctly
    LAZY extraction regex must not swallow into."""
    body = body or NG_STATE_INCIDENT
    unit = b"<!-- padding-filler-text-for-large-oecd-aim-page-simulation --> "
    before = (unit * (script_offset_bytes // len(unit) + 1))[:script_offset_bytes]
    after = (unit * (tail_bytes // len(unit) + 1))[:tail_bytes]
    script = _ng_state_script_html(body).encode("utf-8")
    return (
        b"<html><head></head><body>" + before + script + trailing_script_html
        + after + b"</body></html>"
    )


def _guard_no_network(monkeypatch) -> None:
    """Advisory 1 (WS4-T11 BOUNCE #1): fail loudly, not silently reach
    oecd.ai, if cache seeding ever fails to engage robust_fetch()'s
    warm-cache branch and falls through toward a real fetch."""
    def _raise(*_args, **_kwargs):
        raise AssertionError(
            "test attempted a real network fetch via ingest.common.fetch_once() "
            "-- cache seeding did not engage the warm-cache branch as expected"
        )
    monkeypatch.setattr(_common, "fetch_once", _raise)


def _write_cached_page(monkeypatch, tmp_path, url: str, page_bytes: bytes) -> None:
    """Point the module's on-disk cache at tmp_path, pre-seed it with
    `page_bytes` so fetch_page()'s robust_fetch() call takes the warm-cache
    read branch (no network -- the real code path a second run over an
    already-cached page takes), and install the network guard above."""
    _guard_no_network(monkeypatch)
    monkeypatch.setattr(o, "CACHE", tmp_path)
    slug = url.rstrip("/").split("/")[-1]
    (tmp_path / f"{slug}.html").write_bytes(page_bytes)


def test_fetch_page_extracts_ng_state_from_a_multi_mb_page(monkeypatch, tmp_path):
    """BOUNCE #1 defect 1: the pre-bounce version of this test only sent an
    ~852 KB page through fetch_page(), which a cap anywhere below ~852 KB
    would fail but a cap at 853 KB/900 KB/1 MB would silently still pass --
    and real OECD AIM shell pages run ~949,653 bytes, well inside that gap.
    Send a page far larger than any of those (>5 MB) through the REAL
    fetch_page() and assert the FULL returned length plus the extracted
    id/title -- this is the direct regression case for the gate-measured
    7/250 truncated pages, made robust against a raised-not-removed cap."""
    url = "https://oecd.ai/en/incidents/2026-05-01-feed"
    body = {"id": "2026-05-01-feed", "title": "Multi-megabyte page parser-integrity test incident"}
    page = _make_page(script_offset_bytes=5_000_000, tail_bytes=200_000, body=body)
    assert len(page) > 5_000_000
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    assert len(text) == len(page)  # not truncated at any cap up to 5 MB+

    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert parsed["title"] == body["title"]


def _build_straddle_page() -> tuple[bytes, dict, int, int, int, int]:
    """BOUNCE #1 defect 2: construct a page where the ng-state JSON BODY
    itself (not merely the outer `<script>` tag) starts before byte 800,000
    and ends after it, AND where a 3-byte UTF-8 CJK character inside that
    JSON straddles byte 800,000 precisely (its own byte range includes
    800,000 as a non-leading byte). This is the exact scenario the old
    `data[:800_000]` byte-slice would either cut the JSON mid-object
    (json.loads failure) or split a multi-byte character mid-sequence,
    silently mangled by `errors="replace"`.

    Returns (page_bytes, expected_body, json_start, json_end, char_start,
    char_end) -- all byte offsets INTO page_bytes -- so callers can assert
    the straddle geometry directly rather than trust the docstring."""
    incident_id = "2026-05-02-strd"
    prefix = b"<html><head></head><body>"
    script_open = b'<script id="ng-state" type="application/json">'
    json_head = '{"AppStateKey_0": {"b": {"id": "%s", "title": "Straddle test ' % incident_id
    char = "中"  # CJK "middle" -- 3 bytes in UTF-8 (E4 B8 AD)
    json_tail = ' more title text after the boundary character"}}}'
    title = "Straddle test " + char + " more title text after the boundary character"

    json_head_bytes = json_head.encode("utf-8")
    char_bytes = char.encode("utf-8")
    assert len(char_bytes) == 3
    json_tail_bytes = json_tail.encode("utf-8")
    script_close = b"</script>"
    tail = b"<!-- tail padding --> " * 100

    # Choose filler so the CJK character starts at byte 799_999: its 3 bytes
    # occupy 799_999/800_000/800_001, so byte 800_000 -- the old cut point --
    # falls on its SECOND byte, strictly inside it.
    target_char_start = 799_999
    fixed_len_before_char = len(prefix) + len(script_open) + len(json_head_bytes)
    filler_len = target_char_start - fixed_len_before_char
    assert filler_len > 0, "test construction error: fixed prefix already exceeds target offset"
    filler = b"A" * filler_len

    page = (
        prefix + filler + script_open
        + json_head_bytes + char_bytes + json_tail_bytes
        + script_close + tail
    )

    json_start = len(prefix) + len(filler) + len(script_open)
    char_start = json_start + len(json_head_bytes)
    char_end = char_start + len(char_bytes)
    json_end = char_end + len(json_tail_bytes)

    body = {"id": incident_id, "title": title}
    return page, body, json_start, json_end, char_start, char_end


def test_fetch_page_extracts_ng_state_straddling_the_800kb_boundary(monkeypatch, tmp_path):
    """Boundary case, geometrically self-verified: the ng-state JSON body
    starts before byte 800,000 and ends after it, and a multi-byte UTF-8
    character inside it straddles byte 800,000 exactly -- and it round-trips
    intact through fetch_page() + extract_state()."""
    url = "https://oecd.ai/en/incidents/2026-05-02-strd"
    page, body, json_start, json_end, char_start, char_end = _build_straddle_page()

    # Self-check: prove this fixture actually straddles the boundary it
    # claims to, in bytes, before trusting the parse assertions below --
    # this is exactly the check BOUNCE #1 defect 2 found missing.
    assert json_start < 800_000 < json_end, (json_start, json_end)
    assert char_start < 800_000 < char_end, (char_start, char_end)

    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    # Byte-length, not char-length: the CJK character is 1 codepoint but 3
    # UTF-8 bytes, so `len(text)` (chars) legitimately differs from
    # `len(page)` (bytes) even with zero truncation.
    assert len(text.encode("utf-8")) == len(page)

    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert parsed["title"] == body["title"]  # the CJK character round-trips intact


def test_fetch_page_still_works_on_a_normal_small_page(monkeypatch, tmp_path):
    """No behavior change for the common case: a small, ordinary page below
    the old cap must still parse exactly as before."""
    url = "https://oecd.ai/en/incidents/2026-05-03-tiny"
    body = {"id": "2026-05-03-tiny", "title": "Ordinary small page"}
    page = _make_page(script_offset_bytes=500, tail_bytes=500, body=body)
    assert len(page) < 800_000
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]


def test_fetch_page_decodes_non_ascii_title_exactly(monkeypatch, tmp_path):
    """Advisory 3: a dedicated, SMALL, non-size-related fixture pinning the
    decode codec specifically. A wrong-codec regression (e.g. accidentally
    decoding with latin-1 instead of utf-8) would mangle this multi-byte
    content even on a page nowhere near any size cap -- so this test still
    catches it even if the cap-related tests above somehow didn't."""
    url = "https://oecd.ai/en/incidents/2026-05-05-utf8"
    body = {"id": "2026-05-05-utf8", "title": "Café 北京 incident résumé"}
    # >=1000 bytes total so robust_fetch()'s min_cache_bytes threshold is met
    # and the warm-cache branch actually engages (below that, robust_fetch
    # falls through to the cold branch and the network guard fires).
    page = _make_page(script_offset_bytes=700, tail_bytes=700, body=body)
    assert len(page) >= 1000
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["title"] == body["title"]


def test_fetch_page_extracts_ng_state_when_later_script_tags_follow(monkeypatch, tmp_path):
    """Advisory 4: proves the extraction regex's laziness is load-bearing,
    not incidental -- append further, unrelated `<script>` blocks AFTER the
    ng-state tag's own closing tag. A greedy `(.+)</script>` regression
    would swallow past the real close into these, breaking json.loads()."""
    url = "https://oecd.ai/en/incidents/2026-05-06-trail"
    body = {"id": "2026-05-06-trail", "title": "Trailing script tags parser-integrity test"}
    trailing = (
        b'<script>console.log("unrelated analytics payload");</script>'
        b'<script src="/assets/runtime.js"></script>'
    )
    # >=1000 bytes total so robust_fetch()'s min_cache_bytes threshold is met
    # and the warm-cache branch actually engages.
    page = _make_page(script_offset_bytes=700, tail_bytes=700, body=body, trailing_script_html=trailing)
    assert len(page) >= 1000
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert parsed["title"] == body["title"]


def test_fetch_page_cold_path_does_not_truncate(monkeypatch, tmp_path):
    """Advisory 2: CI has no warm ingest/_cache/oecd_aim cache (no
    actions/cache configured for it), so every warm-cache test above never
    exercises robust_fetch()'s COLD fetch branch. Simulate it directly:
    point CACHE at an empty tmp_path (no pre-seeded file -> robust_fetch()
    takes the cold branch) and monkeypatch `ingest.common.fetch_once` --
    the actual call robust_fetch()'s cold branch invokes -- to return a
    >5 MB page synthetically, with no real network access. Catches a cap
    reintroduced anywhere on this branch (reviewer mutant M10)."""
    url = "https://oecd.ai/en/incidents/2026-05-07-cold"
    body = {"id": "2026-05-07-cold", "title": "Cold-path parser-integrity test incident"}
    page = _make_page(script_offset_bytes=5_000_000, tail_bytes=200_000, body=body)
    assert len(page) > 5_000_000

    monkeypatch.setattr(o, "CACHE", tmp_path)  # empty: no cache file -> cold branch

    def _fake_fetch_once(url_, headers=None, timeout=60, min_interval=None):
        return page, {}

    monkeypatch.setattr(_common, "fetch_once", _fake_fetch_once)

    text = o.fetch_page(url)
    assert text is not None
    assert len(text) == len(page)

    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert parsed["title"] == body["title"]


def test_extract_state_handles_multi_mb_page_without_pathological_backtracking():
    """Performance/DoS sanity check: extract_state()'s
    `<script[^>]*id="ng-state"[^>]*>(.+?)</script>` regex, run with re.S over
    a several-megabyte body, must stay linear-time (a lazy `.+?` bounded by a
    literal terminator has no catastrophic-backtracking shape), not the
    exponential blowup pathological patterns can trigger. Generous 5s bound
    to avoid CI flakiness; a pathological blowup would be orders of
    magnitude slower than that, not merely over it."""
    body = {"id": "2026-05-04-perf", "title": "Multi-megabyte page performance test incident"}
    page_bytes = _make_page(script_offset_bytes=5_000_000, tail_bytes=200_000, body=body)
    assert len(page_bytes) > 5_000_000
    text = page_bytes.decode("utf-8")

    t0 = time.time()
    parsed = o.extract_state(text)
    elapsed = time.time() - t0

    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert elapsed < 5.0, f"extract_state() took {elapsed:.2f}s on a {len(page_bytes)}-byte page"


# --- WS4-T11 BOUNCE #1 defect 3: honest per-reason accounting --------------
#
# extract_state()'s old dict-or-None contract folded three distinct failure
# modes into a single "unparseable" bucket: no ng-state tag at all, a tag
# whose JSON fails to decode, and (the real-world dominant case per the E21
# audit: 1852/2988 crawled pages) a tag whose JSON decodes fine but uses a
# different top-level key shape that never satisfies the id+title body
# check. `_extract_state_detail()` / `REASON_*` / `_tally_reasons()` make
# these three (plus REASON_OK and REASON_FETCH_FAILED) independently
# countable and printable from `main()`, without changing what "ok" means.


def test_extract_state_detail_buckets_no_script_match():
    reason, body = o._extract_state_detail("<html><body>no ng-state script here at all</body></html>")
    assert reason == o.REASON_NO_SCRIPT_MATCH
    assert body is None


def test_extract_state_detail_buckets_json_decode_error():
    html = '<script id="ng-state">{this is not valid json</script>'
    reason, body = o._extract_state_detail(html)
    assert reason == o.REASON_JSON_DECODE_ERROR
    assert body is None


def test_extract_state_detail_buckets_no_body_shape():
    """The real-world dominant case (E21 audit): the 1852 legacy
    numeric-slug pages carry a valid, JSON-decodable ng-state blob whose
    top-level value uses a different key shape (hashed `b/h/s/st/u/rt`
    sub-fields per the audit's sampled page) that never satisfies the
    id+title body-shape check -- a real page-content-level shape
    difference, not a JSON or fetch failure."""
    legacy_shape = {"AppStateKey_0": {"h": "somehash", "s": "somestatus", "st": 1, "u": "/x", "rt": True}}
    html = f'<script id="ng-state">{json.dumps(legacy_shape)}</script>'
    reason, body = o._extract_state_detail(html)
    assert reason == o.REASON_NO_BODY_SHAPE
    assert body is None


def test_extract_state_detail_buckets_ok():
    html = _ng_state_script_html(NG_STATE_INCIDENT)
    reason, body = o._extract_state_detail(html)
    assert reason == o.REASON_OK
    assert body == NG_STATE_INCIDENT


def test_extract_state_public_wrapper_still_returns_dict_or_none():
    """extract_state() keeps its original dict-or-None contract for
    existing callers (this test file's other fixtures, and any future
    direct use) that only need the body, not the failure reason."""
    assert o.extract_state("<html><body>nothing here</body></html>") is None
    assert o.extract_state(_ng_state_script_html(NG_STATE_INCIDENT)) == NG_STATE_INCIDENT


def test_fetch_and_extract_buckets_fetch_failed(monkeypatch):
    monkeypatch.setattr(o, "fetch_page", lambda url: None)
    reason, body = o.fetch_and_extract("https://oecd.ai/en/incidents/whatever-fails")
    assert reason == o.REASON_FETCH_FAILED
    assert body is None


def test_fetch_and_extract_buckets_ok(monkeypatch):
    monkeypatch.setattr(o, "fetch_page", lambda url: _ng_state_script_html(NG_STATE_INCIDENT))
    reason, body = o.fetch_and_extract("https://oecd.ai/en/incidents/2026-05-01-feed")
    assert reason == o.REASON_OK
    assert body == NG_STATE_INCIDENT


def test_tally_reasons_counts_each_bucket_independently():
    """Pure accounting-logic test (no network, no fixtures): _tally_reasons()
    must count each REASON_* bucket independently and exhaustively -- the
    property that makes the printed summary in main() honest."""
    results = {
        "u1": (o.REASON_OK, {"id": "1", "title": "t1"}),
        "u2": (o.REASON_OK, {"id": "2", "title": "t2"}),
        "u3": (o.REASON_NO_SCRIPT_MATCH, None),
        "u4": (o.REASON_JSON_DECODE_ERROR, None),
        "u5": (o.REASON_NO_BODY_SHAPE, None),
        "u6": (o.REASON_NO_BODY_SHAPE, None),
        "u7": (o.REASON_FETCH_FAILED, None),
    }
    counts = o._tally_reasons(results)
    assert counts == {
        o.REASON_OK: 2,
        o.REASON_NO_SCRIPT_MATCH: 1,
        o.REASON_JSON_DECODE_ERROR: 1,
        o.REASON_NO_BODY_SHAPE: 2,
        o.REASON_FETCH_FAILED: 1,
    }
    # "ok" + the three unparseable buckets + fetch-failed must exhaust every
    # url exactly once -- the same total the old single ok/parse_fail split
    # always had, just no longer collapsed into an undifferentiated bucket.
    assert sum(counts.values()) == len(results)
