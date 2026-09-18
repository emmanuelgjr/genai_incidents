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

    # BOUNCE #2: production's main() no longer calls fetch_page()/
    # extract_state() as a sequence -- it submits fetch_and_extract() to the
    # thread pool. A test that only exercises fetch_page()+extract_state()
    # cannot see a regression reintroduced solely at fetch_and_extract()'s
    # entry point (e.g. `_extract_state_detail(text[:800_000])`). Go through
    # the REAL fetch_page() here too (no stub) with the SAME cache seeding.
    assert o.fetch_and_extract(url) == (o.REASON_OK, body)


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

    # BOUNCE #2: also exercise fetch_and_extract(), production's real entry
    # point, through the REAL fetch_page() (no stub) -- see the multi-MB
    # test above for why this is required, not redundant.
    assert o.fetch_and_extract(url) == (o.REASON_OK, body)


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

    # BOUNCE #2: also exercise fetch_and_extract() on the COLD branch --
    # production's real entry point, through the REAL fetch_page() (no stub).
    assert o.fetch_and_extract(url) == (o.REASON_OK, body)


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


# --- WS4-T13: OECD AIM crawl budget -- skip legacy numeric-slug URLs -------
# The parser contract this task asks for: is_numeric_slug()/partition_
# fetchable() must skip ONLY the legacy all-digits slug shape, never the
# modern YYYY-MM-DD-<hex> shape, and never guess on an ambiguous partial
# match. See scripts/ingest_oecd_aim.py's _NUMERIC_SLUG_RE comment block for
# the population this was measured against
# (docs/audits/E21-tripwire-refresh-2026-09-14.md).


def test_is_numeric_slug_classifies_legacy_vs_modern():
    # Legacy scheme: real examples observed live in the OECD AIM sitemap
    # (E21 audit, 2026-09-14): /en/incidents/256, /321, /281, /342, /359.
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/256") is True
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/321") is True
    # Leading zeros: still all-digits -- still the legacy shape.
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/007") is True
    # Trailing slash tolerated (matches load_sitemap()'s own URL shape).
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/256/") is True
    # Modern scheme: NEVER purely numeric (always carries hyphens) -- real
    # example: /en/incidents/2026-09-10-1de6.
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/2026-09-10-1de6") is False
    # A bare slug that merely LOOKS like a year: all-digits -> treated as
    # legacy/skippable. No such shape exists in OECD AIM's sitemap today
    # (the E21 audit found `other=0` in the crawled window: only the legacy
    # all-digits and modern date-hash shapes appear) -- documented here as a
    # named boundary rather than silently assumed away.
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/2026") is True
    # Numeric WITH a non-digit suffix: NOT a full match -> conservative
    # default is to fetch it (unknown shape), never guess-skip.
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/256a") is False
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/256-x") is False
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/x256") is False


def test_is_numeric_slug_minimal_baseline_pin():
    """WS4-T17 carry-along rename (was `test_is_numeric_slug_rule_fires_
    when_corrupted`): its OWN two assertions are a strict subset of
    `test_is_numeric_slug_classifies_legacy_vs_modern` above (same two
    URLs, same expected values) -- it does not corrupt anything, and never
    did; the "fires when corrupted" name asserted a property (agreement-6
    style, hand-mutate-and-watch-it-fail evidence) that this test itself
    does not produce. It still discriminates a real regression in
    `is_numeric_slug()` (confirmed: fails under all three of the
    boundary-flipping mutants `_NUMERIC_SLUG_RE` could plausibly take --
    always-True, always-False, and hyphen-inclusive), so it is kept, not
    deleted -- just renamed to describe what it actually is: a minimal,
    fast, two-assertion baseline pin, redundant with the fuller test above
    on purpose (cheap early-fail signal in a long file), not a corruption
    exercise. The corruption exercise itself (temporarily replacing
    `_NUMERIC_SLUG_RE` with a pattern that never matches and re-running this
    suite) was performed by hand for WS4-T13 per working agreement 6 -- see
    that task's report for the exact command/output -- and is not
    re-enacted here, to avoid mutating shared module state mid-suite. See
    `test_run_skip_sampling_probe_flags_violation_when_body_shape_present`
    below for WS4-T17's OWN "prove it fires" exercise, which the reviewer
    asked for on the PROBE itself, not on `is_numeric_slug()`."""
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/256") is True
    assert o.is_numeric_slug("https://oecd.ai/en/incidents/2026-09-10-1de6") is False


def test_partition_fetchable_skips_only_numeric_slugs():
    urls = [
        "https://oecd.ai/en/incidents/256",
        "https://oecd.ai/en/incidents/2026-09-10-1de6",
        "https://oecd.ai/en/incidents/321",
        "https://oecd.ai/en/incidents/2026-09-07-e398",
        "https://oecd.ai/en/incidents/256a",  # ambiguous -- must NOT be skipped
    ]
    fetchable, skipped = o.partition_fetchable(urls)
    assert fetchable == [
        "https://oecd.ai/en/incidents/2026-09-10-1de6",
        "https://oecd.ai/en/incidents/2026-09-07-e398",
        "https://oecd.ai/en/incidents/256a",
    ]
    assert skipped == [
        "https://oecd.ai/en/incidents/256",
        "https://oecd.ai/en/incidents/321",
    ]
    # Every input URL lands in exactly one bucket.
    assert len(fetchable) + len(skipped) == len(urls)


def test_partition_fetchable_empty_and_all_numeric():
    assert o.partition_fetchable([]) == ([], [])
    all_numeric = ["https://oecd.ai/en/incidents/1", "https://oecd.ai/en/incidents/2"]
    assert o.partition_fetchable(all_numeric) == ([], all_numeric)


# --- WS4-T11 re-gate BOUNCE #2: offline end-to-end main() ------------------
#
# The gap BOUNCE #2 found: every test above calls fetch_page()+extract_state()
# as a sequence, or stubs fetch_page() entirely -- neither is the sequence
# production actually runs. main() submits fetch_and_extract() to the thread
# pool and reads its (reason, body) result straight from `results`. A
# regression planted solely at fetch_and_extract()'s own entry point (e.g.
# `_extract_state_detail(text[:800_000])` at scripts/ingest_oecd_aim.py:255)
# passed all 30 previously-committed tests and silently dropped a >800 KB
# incident in an offline main() run. This test exercises main() itself, with
# no network: load_sitemap() and ingest.common.fetch_once() are both
# monkeypatched, CACHE and INGEST are redirected under tmp_path, and every
# REASON_* bucket, a duplicate sitemap URL (advisory 2), and a 0-byte page
# (point 4's benign accounting delta) are all present in one run.


def test_main_end_to_end_offline(monkeypatch, tmp_path, capsys):
    """No network. Asserts on (i) the written output file's exact id set and
    (ii) the exact printed summary numbers (fetched/ok/each unparseable
    sub-bucket), which must sum to the fetched total. This is what kills the
    reviewer's surviving main()-level mutants: dropping `no_shape` from the
    unparseable total, computing `ok` wrongly, and printing `fetched` as
    `len(urls)` (which would also be wrong here purely from the duplicate
    URL, independent of the fetch failure)."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    ingest_dir = tmp_path / "ingest"
    ingest_dir.mkdir()
    monkeypatch.setattr(o, "CACHE", cache_dir)
    monkeypatch.setattr(o, "INGEST", ingest_dir)
    monkeypatch.delenv("OECD_AIM_LIMIT", raising=False)  # use the real default (3000), deterministic
    # WS4-T17: disable the skip-rule sampling probe for THIS test. It is
    # covered by its own dedicated tests below (test_run_skip_sampling_probe_*
    # / test_main_invokes_skip_sampling_probe_when_enabled) with a stubbed
    # fetch_fn; left enabled here it would attempt a REAL fetch for
    # url_legacy_numeric (deliberately uncached/unhandled below, see that
    # URL's own comment), which is exactly the "unexpected live fetch"
    # AssertionError trap this test relies on for the skip rule itself --
    # this test's job is main()'s pre-existing accounting, not the probe.
    monkeypatch.setenv("OECD_AIM_PROBE_SAMPLE_SIZE", "0")
    # Skip real exponential-backoff sleeps on the simulated fetch failure
    # below (2s + 4s otherwise) -- this test asserts no real network call is
    # ever reached, so there is nothing to legitimately wait out.
    monkeypatch.setattr(_common.time, "sleep", lambda *_a, **_k: None)

    url_normal = "https://oecd.ai/en/incidents/2026-01-10-norm"
    url_big = "https://oecd.ai/en/incidents/2026-01-11-big"
    # Non-numeric on purpose (WS4-T13): still exercises REASON_NO_BODY_SHAPE
    # for the (rare, non-legacy-scheme) case where a modern-shaped slug
    # nonetheless carries the shell/hashed-key body shape.
    url_shell = "https://oecd.ai/en/incidents/2026-01-12-shel"
    url_noscript = "https://oecd.ai/en/incidents/2026-01-13-nosc"
    url_badjson = "https://oecd.ai/en/incidents/2026-01-14-badj"
    url_fetchfail = "https://oecd.ai/en/incidents/2026-01-15-fail"
    url_empty = "https://oecd.ai/en/incidents/2026-01-16-empty"
    url_ok_not_relevant = "https://oecd.ai/en/incidents/2026-01-17-filt"
    # WS4-T13: a legacy numeric-slug URL. Deliberately NOT cached and NOT
    # handled by the fake fetch_once below -- if partition_fetchable() ever
    # stops skipping it, robust_fetch() falls through to the cold branch,
    # _fake_fetch_once()'s catch-all fires ("unexpected live fetch attempted"),
    # and this test fails loudly instead of silently passing. This is the
    # "prove it fires" check for the skip rule at the main()-integration level
    # (see also test_is_numeric_slug_classifies_legacy_vs_modern and
    # test_partition_fetchable_skips_only_numeric_slugs for the unit-level
    # contract tests).
    url_legacy_numeric = "https://oecd.ai/en/incidents/447"

    # url_normal appears TWICE -- load_sitemap() does not dedupe; proves
    # advisory 2 (fetched must come from `results`, not `len(urls)`).
    urls = [
        url_normal, url_big, url_shell, url_noscript, url_badjson,
        url_fetchfail, url_empty, url_ok_not_relevant, url_normal,
        url_legacy_numeric,
    ]
    monkeypatch.setattr(o, "load_sitemap", lambda: list(urls))

    normal_body = {
        "id": "2026-01-10-norm",
        "title": "Deepfake voice clone scam empties retiree's bank account",
        "date": "2026-01-10",
        "summary": "Fraudsters used a deepfake voice clone to steal funds.",
        "company": ["Example Bank"], "articles": [], "aiid_ids": [],
    }
    big_body = {
        "id": "2026-01-11-big",
        "title": "Ransomware attack cripples AI-driven hospital triage system",
        "date": "2026-01-11",
        "summary": "A ransomware gang crippled an AI-driven triage system.",
        "company": ["Example Hospital"], "articles": [], "aiid_ids": [],
    }
    # Parses cleanly (REASON_OK -- has a valid id+title+date) but contains no
    # SECURITY_KEYWORDS match, so normalize_body() filters it out of `out`.
    # Without this fixture, `ok` (REASON_OK count) and `len(out)`
    # (security-relevant-kept count) are numerically identical by
    # coincidence, and a `main()` mutant that computes `ok` as `len(out)`
    # instead of the real REASON_OK tally passes undetected.
    ok_not_relevant_body = {
        "id": "2026-01-17-filt",
        "title": "AI system helps farmers optimize crop irrigation schedules",
        "date": "2026-01-17",
        "summary": "Researchers report improved yields using an AI irrigation planner.",
        "company": ["AgriCo"], "articles": [], "aiid_ids": [],
    }

    # >=1000 bytes so robust_fetch()'s min_cache_bytes threshold is met and
    # the warm-cache branch actually engages (below that it falls through to
    # the cold branch, which for this URL isn't handled by the fake
    # fetch_once below and would fail loudly instead of silently).
    normal_page = _make_page(script_offset_bytes=700, tail_bytes=700, body=normal_body)
    assert len(normal_page) >= 1000
    # >=949 KB, ng-state blob starting beyond byte 900,000 -- real OECD AIM
    # shell pages run ~949,653 bytes (BOUNCE #1 defect 1's own figure).
    big_page = _make_page(script_offset_bytes=900_500, tail_bytes=50_000, body=big_body)
    assert len(big_page) >= 949_000
    ok_not_relevant_page = _make_page(script_offset_bytes=700, tail_bytes=700, body=ok_not_relevant_body)
    assert len(ok_not_relevant_page) >= 1000

    shell_shape = {"AppStateKey_0": {"h": "somehash", "s": "somestatus", "st": 1, "u": "/2026-01-12-shel", "rt": True}}
    shell_page = (
        f'<script id="ng-state">{json.dumps(shell_shape)}</script>'.encode("utf-8")
        + b"<!-- padding --> " * 100
    )
    noscript_page = (
        b"<html><body>no ng-state script here at all, just ordinary page content</body></html>"
        + b"<!-- padding --> " * 100
    )
    badjson_page = (
        b'<script id="ng-state">{this is not valid json at all</script>'
        + b"<!-- padding --> " * 100
    )

    for url, page_bytes in (
        (url_normal, normal_page),
        (url_big, big_page),
        (url_shell, shell_page),
        (url_noscript, noscript_page),
        (url_badjson, badjson_page),
        (url_ok_not_relevant, ok_not_relevant_page),
    ):
        slug = url.rstrip("/").split("/")[-1]
        (cache_dir / f"{slug}.html").write_bytes(page_bytes)
    # url_fetchfail and url_empty are deliberately left UNcached -- they go
    # through robust_fetch()'s cold branch, handled by the fake fetch_once
    # below.

    def _fake_fetch_once(url_, headers=None, timeout=60, min_interval=None):
        if url_ == url_fetchfail:
            raise ConnectionError("simulated fetch failure -- no real network reached")
        if url_ == url_empty:
            return b"", {}
        raise AssertionError(f"unexpected live fetch attempted for {url_} -- cache seeding gap")

    monkeypatch.setattr(_common, "fetch_once", _fake_fetch_once)

    o.main()

    captured = capsys.readouterr()
    out_text = captured.out

    # (i) the written output file: exact id set, large incident present.
    # ok_not_relevant_body parsed fine but is correctly EXCLUDED here (not
    # security-relevant) -- this is what makes it distinguish `ok` from
    # `len(out)` below rather than merely testing the same thing twice.
    out_path = ingest_dir / "oecd_aim_full_incidents.json"
    written = json.loads(out_path.read_text(encoding="utf-8"))
    ids = {e["source_id"] for e in written}
    assert ids == {
        f"OECD-AIM-{normal_body['id']}",
        f"OECD-AIM-{big_body['id']}",
    }
    assert f"OECD-AIM-{big_body['id']}" in ids  # the >=949 KB incident specifically
    assert f"OECD-AIM-{ok_not_relevant_body['id']}" not in ids

    # (ii) the summary line via capsys, exact numbers.
    # 8 unique urls (url_normal's duplicate collapses in `results`):
    #   ok: normal, big, ok_not_relevant                = 3
    #   no_ng_state_script: noscript, empty              = 2
    #   json_decode_error: badjson                       = 1
    #   no_incident_body_shape: shell                    = 1
    #   fetch_failed: fetchfail                           = 1
    # WS4-T13: `urls` now has 10 entries (9 original + url_legacy_numeric).
    # partition_fetchable() skips exactly url_legacy_numeric (1/10), leaving
    # a 9-entry fetch_urls list (the duplicate url_normal still counted twice
    # here -- partition happens before dedup). If the skip rule regresses
    # (e.g. stops matching, or over-matches url_shell/url_normal/etc.), this
    # exact line changes and the test fails.
    assert (
        "[aim] skipping 1/10 legacy numeric-slug URLs "
        "(OECD AIM's pre-date-hash ID scheme; ng-state shape never parses "
        "-- see REASON_NO_BODY_SHAPE); fetching 9"
    ) in out_text
    # fetched = 8 unique fetchable - 1 fetch_failed = 7 (NOT 9 = len(fetch_urls),
    # which double-counts the duplicate url_normal -- this is what kills the
    # `fetched = len(fetch_urls)` mutant on THIS fixture, independent of any
    # fetch failure). url_legacy_numeric contributes to neither figure: it
    # was removed from fetch_urls before the loop ever ran (see the
    # AssertionError-on-live-fetch trap on its own definition above).
    # ok(3) + unparseable(2+1+1=4) == fetched(7).
    # "2 security-relevant kept" (NOT 3): ok_not_relevant_body parsed fine
    # (REASON_OK) but was filtered by normalize_body() -- this is what kills
    # a `main()` mutant computing `ok` as `len(out)` instead of the real
    # REASON_OK tally (the two would otherwise coincide at 2 and pass
    # undetected).
    assert "[aim] fetched 7/9 pages in" in out_text
    assert (
        "[aim] parsed: 3 ok, 4 unparseable "
        "(no ng-state script: 2, JSON decode error: 1, "
        "ng-state present but no incident-body shape: 1); "
        "2 security-relevant kept"
    ) in out_text


# --- WS4-T17: skip-rule sampling probe --------------------------------------
#
# WS4-T13's crawl-budget skip erases its own evidence: is_numeric_slug()'s
# premise (every legacy numeric-slug page fails the body-shape check) was
# TRUE when measured, but stops being observable once those URLs are never
# fetched. This probe samples a small, rotating slice of the skipped set
# every run, fetches it for REAL through the same conduct-checked path the
# main crawl uses, and fails loudly if the premise no longer holds. See
# scripts/ingest_oecd_aim.py's own "WS4-T17" comment block for the full
# design rationale (rotating-not-random sampling, value-based cursor,
# REASON_OK-only hard failure, REASON_FETCH_FAILED exclusion).


def _numeric_urls(*ns: int) -> list[str]:
    return [f"https://oecd.ai/en/incidents/{n}" for n in ns]


def test_select_probe_sample_first_run_starts_from_beginning():
    skipped = _numeric_urls(30, 10, 20, 5, 15)  # deliberately unsorted input
    sample, new_cursor = o.select_probe_sample(skipped, None, 3)
    assert sample == _numeric_urls(5, 10, 15)  # sorted ascending, first 3
    assert new_cursor == 15


def test_select_probe_sample_rotates_across_runs_without_overlap():
    skipped = _numeric_urls(*range(1, 11))  # 1..10
    sample1, cursor1 = o.select_probe_sample(skipped, None, 3)
    assert sample1 == _numeric_urls(1, 2, 3)
    assert cursor1 == 3
    sample2, cursor2 = o.select_probe_sample(skipped, cursor1, 3)
    assert sample2 == _numeric_urls(4, 5, 6)
    assert cursor2 == 6
    sample3, cursor3 = o.select_probe_sample(skipped, cursor2, 3)
    assert sample3 == _numeric_urls(7, 8, 9)
    assert cursor3 == 9
    # Coverage accumulates: after 3 rotating runs over a 10-item population
    # with k=3, 9 DISTINCT items have been probed -- a random per-run draw
    # has no such guarantee.
    covered = set(sample1) | set(sample2) | set(sample3)
    assert len(covered) == 9


def test_select_probe_sample_wraps_around_at_the_end():
    skipped = _numeric_urls(*range(1, 11))  # 1..10
    # Cursor at 9 (near the end) with k=3 must wrap: 10, then back to 1, 2.
    sample, new_cursor = o.select_probe_sample(skipped, 9, 3)
    assert sample == _numeric_urls(10, 1, 2)
    assert new_cursor == 2


def test_select_probe_sample_caps_k_to_population_size():
    skipped = _numeric_urls(1, 2)
    sample, new_cursor = o.select_probe_sample(skipped, None, 5)
    assert sample == _numeric_urls(1, 2)
    assert new_cursor == 2


def test_select_probe_sample_empty_population_returns_cursor_unchanged():
    assert o.select_probe_sample([], None, 5) == ([], None)
    assert o.select_probe_sample([], 42, 5) == ([], 42)


def test_select_probe_sample_k_zero_or_negative_is_a_noop():
    skipped = _numeric_urls(1, 2, 3)
    assert o.select_probe_sample(skipped, None, 0) == ([], None)
    assert o.select_probe_sample(skipped, 7, -1) == ([], 7)


def test_select_probe_sample_cursor_stale_against_a_changed_population():
    # The crawl window slid: the old cursor's value (50) no longer appears
    # in `skipped` at all, and everything left is SMALLER than it (the
    # population aged further down, e.g. new URLs pushed the largest legacy
    # slugs out of the newest-N window entirely). No entry is > cursor, so
    # this must fall back to the start rather than sampling nothing forever.
    skipped = _numeric_urls(5, 10, 15)
    sample, new_cursor = o.select_probe_sample(skipped, 50, 2)
    assert sample == _numeric_urls(5, 10)
    assert new_cursor == 10


# --- WS4-T17 BOUNCE #1: select_recent_biased_sample() -----------------------


def test_select_recent_biased_sample_prefers_front_of_original_order():
    skipped = _numeric_urls(30, 10, 20, 5, 15)  # deliberately unsorted
    sample = o.select_recent_biased_sample(skipped, set(), 3)
    # First 3 in the GIVEN (sitemap) order, NOT numeric-value-sorted order --
    # this is what distinguishes it from select_probe_sample() above.
    assert sample == _numeric_urls(30, 10, 20)


def test_select_recent_biased_sample_excludes_given_set():
    skipped = _numeric_urls(30, 10, 20, 5, 15)
    sample = o.select_recent_biased_sample(skipped, {"https://oecd.ai/en/incidents/30"}, 3)
    assert sample == _numeric_urls(10, 20, 5)


def test_select_recent_biased_sample_caps_at_available_after_exclusions():
    skipped = _numeric_urls(30, 10, 20)
    sample = o.select_recent_biased_sample(skipped, set(skipped[:2]), 5)
    assert sample == _numeric_urls(20)  # only one left after excluding two of three


def test_select_recent_biased_sample_k_zero_or_negative_is_a_noop():
    skipped = _numeric_urls(30, 10, 20)
    assert o.select_recent_biased_sample(skipped, set(), 0) == []
    assert o.select_recent_biased_sample(skipped, set(), -1) == []


def test_select_recent_biased_sample_empty_population():
    assert o.select_recent_biased_sample([], set(), 3) == []


# --- WS4-T17 BOUNCE #1: _coverage_ledger() -----------------------------------


def test_coverage_ledger_measures_current_population_only():
    population = _numeric_urls(1, 2, 3, 4, 5)
    # Observed 1,2,3 ever (lifetime) plus 99, which has since aged OUT of the
    # current population -- must not inflate coverage of what's live now.
    ledger = o._coverage_ledger([1, 2, 3, 99], population)
    assert ledger["observed_of_current_population"] == 3
    assert ledger["current_population_size"] == 5
    assert ledger["coverage_fraction"] == 3 / 5


def test_coverage_ledger_empty_population_is_none_fraction():
    ledger = o._coverage_ledger([1, 2], [])
    assert ledger["current_population_size"] == 0
    assert ledger["coverage_fraction"] is None


# --- WS4-T17 BOUNCE #1: run_skip_sampling_probe() combines both halves,
# reports fetch failures honestly, and ships a measured coverage ledger -----


def test_run_skip_sampling_probe_combines_rotating_and_recent_biased_halves(tmp_path):
    state_path = tmp_path / "skip_probe_state.json"
    # Deliberately unsorted -- mirrors sitemap order, NOT numeric-value
    # order, so the two halves are provably picking different things.
    skipped = _numeric_urls(30, 10, 20, 5, 15, 25, 1, 40, 8, 12)  # 10 items

    def _fake_fetch(_url):
        return o.REASON_NO_BODY_SHAPE, None

    result = o.run_skip_sampling_probe(skipped, k=4, state_path=state_path, fetch_fn=_fake_fetch)
    # k=4 -> k_rotate=2, k_recent=2.
    # Rotating half: sorted ascending [1,5,8,10,12,15,20,25,30,40], cursor
    # None -> first 2 -> [1, 5].
    rotate_expected = _numeric_urls(1, 5)
    # Recency-biased half: first 2 entries of `skipped` in ITS OWN order not
    # already in the rotating set -> 30, 10.
    recent_expected = _numeric_urls(30, 10)
    assert result["sample"] == rotate_expected + recent_expected
    assert result["observed"] == 4
    assert result["fetch_failed"] == []


def test_run_skip_sampling_probe_no_violations_persists_rotating_state(tmp_path):
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(*range(1, 21))  # 20 items

    def _fake_fetch(_url):
        return o.REASON_NO_BODY_SHAPE, None

    result1 = o.run_skip_sampling_probe(
        skipped, k=6, state_path=state_path, fetch_fn=_fake_fetch
    )
    # k=6 -> k_rotate=3, k_recent=3: rotate=[1,2,3] (cursor->3); recent
    # (excluding 1,2,3) walks original order 1..20 and picks [4,5,6].
    assert result1["sample"] == _numeric_urls(1, 2, 3, 4, 5, 6)
    assert result1["violations"] == []
    assert result1["soft_anomalies"] == []
    assert result1["fetch_failed"] == []
    assert result1["observed"] == 6
    assert result1["population_size"] == 20

    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted["cursor"] == 3  # rotating half's OWN cursor (3 items rotated)
    assert persisted["last_violations"] == []
    assert persisted["total_sampled_lifetime"] == 6
    assert persisted["total_observed_lifetime"] == 6

    # Second run: rotation continues from the persisted cursor, and the
    # lifetime counters accumulate rather than resetting.
    result2 = o.run_skip_sampling_probe(
        skipped, k=6, state_path=state_path, fetch_fn=_fake_fetch
    )
    assert result2["sample"] == _numeric_urls(4, 5, 6, 1, 2, 3)
    persisted2 = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted2["cursor"] == 6
    assert persisted2["total_sampled_lifetime"] == 12
    assert persisted2["total_observed_lifetime"] == 12


def test_run_skip_sampling_probe_coverage_ledger_grows_as_cursor_advances(tmp_path):
    """A MEASURED number, not a design argument (WS4-T17 BOUNCE #1): the
    lifetime coverage ledger must not double-count a slug re-observed on a
    later run, and must grow once the rotating cursor reaches genuinely new
    territory."""
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(*range(1, 21))  # 20 items

    def _fake_fetch(_url):
        return o.REASON_NO_BODY_SHAPE, None

    r1 = o.run_skip_sampling_probe(skipped, k=6, state_path=state_path, fetch_fn=_fake_fetch)
    assert r1["coverage_ledger"] == {
        "observed_of_current_population": 6,
        "current_population_size": 20,
        "coverage_fraction": 6 / 20,
    }

    r2 = o.run_skip_sampling_probe(skipped, k=6, state_path=state_path, fetch_fn=_fake_fetch)
    # Run 2's sample is [4,5,6,1,2,3] -- every one of those slugs was
    # ALREADY observed in run 1, so lifetime coverage must NOT grow yet.
    assert r2["coverage_ledger"]["observed_of_current_population"] == 6

    r3 = o.run_skip_sampling_probe(skipped, k=6, state_path=state_path, fetch_fn=_fake_fetch)
    # The rotating cursor has now moved past slug 6 into [7,8,9] -- genuinely
    # new territory -- so lifetime coverage grows for the first time.
    assert r3["coverage_ledger"]["observed_of_current_population"] == 9


def test_run_skip_sampling_probe_flags_violation_when_body_shape_present(tmp_path, capsys):
    """THE "prove it fires" exercise agreement 6 requires of this specific
    task: seed a fixture where a numeric-slug URL returns a MODERN body
    shape (REASON_OK, as if OECD's legacy page now parses like a real
    incident) and watch the probe fail -- i.e. report it as a violation,
    not silently pass. See this task's report for the same scenario run as
    a standalone command."""
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(256, 321, 447)
    poisoned_body = {"id": "256", "title": "A modern-shaped body now sits behind a legacy numeric slug"}

    def _fake_fetch(url):
        if url == "https://oecd.ai/en/incidents/256":
            # The exact regression this probe exists to catch: a legacy
            # numeric-slug URL that NOW extracts a valid incident body.
            return o.REASON_OK, poisoned_body
        return o.REASON_NO_BODY_SHAPE, None

    result = o.run_skip_sampling_probe(
        skipped, k=3, state_path=state_path, fetch_fn=_fake_fetch
    )
    assert result["violations"] == ["https://oecd.ai/en/incidents/256"]
    assert result["soft_anomalies"] == []

    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted["last_violations"] == ["https://oecd.ai/en/incidents/256"]

    # And the separate enforcement gate must fail loudly on it.
    exit_code = o.check_probe_state_for_violations(state_path)
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "::error::" in err
    assert "DROPPING REAL INCIDENTS" in err
    assert "https://oecd.ai/en/incidents/256" in err


def test_run_skip_sampling_probe_soft_anomaly_does_not_trip_hard_gate(tmp_path):
    """A reason other than REASON_OK / REASON_NO_BODY_SHAPE / REASON_
    FETCH_FAILED (e.g. REASON_JSON_DECODE_ERROR) is logged as a soft
    anomaly -- a deviation from the measured 100%-NO_BODY_SHAPE pattern --
    but is NOT itself evidence of data loss, so it must NOT trip the hard
    "::error::" gate the way an actual REASON_OK violation does."""
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(256)

    def _fake_fetch(_url):
        return o.REASON_JSON_DECODE_ERROR, None

    result = o.run_skip_sampling_probe(
        skipped, k=1, state_path=state_path, fetch_fn=_fake_fetch
    )
    assert result["violations"] == []
    assert result["soft_anomalies"] == ["https://oecd.ai/en/incidents/256"]
    assert o.check_probe_state_for_violations(state_path) == 0


def test_run_skip_sampling_probe_excludes_fetch_failed_from_verdict_buckets(tmp_path):
    """Ordinary network flakiness (REASON_FETCH_FAILED) says nothing about
    whether the skip rule's premise still holds -- counting it as a
    violation or even a soft anomaly would make this probe noisy for a
    reason unrelated to what it exists to catch. WS4-T17 BOUNCE #1: this
    exclusion from the VERDICT buckets is correct and unchanged; what was
    wrong (fixed below and in test_run_skip_sampling_probe_reports_fetch_
    failures_honestly) was excluding it from REPORTING too."""
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(256)

    def _fake_fetch(_url):
        return o.REASON_FETCH_FAILED, None

    result = o.run_skip_sampling_probe(
        skipped, k=1, state_path=state_path, fetch_fn=_fake_fetch
    )
    assert result["violations"] == []
    assert result["soft_anomalies"] == []
    assert o.check_probe_state_for_violations(state_path) == 0


def test_run_skip_sampling_probe_reports_fetch_failures_honestly(tmp_path):
    """WS4-T17 BOUNCE #1 defect 1, at the pure-function level: a run where
    EVERY sampled URL hits REASON_FETCH_FAILED must report `fetch_failed`
    populated and `observed == 0` -- distinguishable from "checked and
    clean" by any caller, not silently folded away."""
    state_path = tmp_path / "skip_probe_state.json"
    skipped = _numeric_urls(100, 200, 300)

    def _fake_fetch(_url):
        return o.REASON_FETCH_FAILED, None

    result = o.run_skip_sampling_probe(
        skipped, k=3, state_path=state_path, fetch_fn=_fake_fetch
    )
    assert result["violations"] == []
    assert result["soft_anomalies"] == []
    assert sorted(result["fetch_failed"]) == sorted(result["sample"])
    assert result["observed"] == 0

    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted["last_observed_count"] == 0
    assert len(persisted["last_fetch_failed"]) == len(persisted["last_sample"])
    assert persisted["total_sampled_lifetime"] == len(persisted["last_sample"])
    assert persisted["total_observed_lifetime"] == 0
    # A 0-observation run must not inflate the coverage ledger either.
    assert persisted["coverage_ledger"]["observed_of_current_population"] == 0


def test_check_probe_state_for_violations_no_state_file_is_clean(tmp_path):
    # A fresh checkout / a repo where the probe has never run yet must not
    # fail this check -- "no evidence of a problem" is not "a problem".
    missing = tmp_path / "does_not_exist.json"
    assert o.check_probe_state_for_violations(missing) == 0


def test_check_probe_state_for_violations_clean_last_run(tmp_path):
    state_path = tmp_path / "skip_probe_state.json"
    state_path.write_text(json.dumps({"last_violations": []}), encoding="utf-8")
    assert o.check_probe_state_for_violations(state_path) == 0


def test_main_invokes_skip_sampling_probe_when_enabled(monkeypatch, tmp_path, capsys):
    """Integration-level check that main() actually wires the probe up using
    the real skipped_numeric partition it already computed -- not just that
    the probe function works in isolation. No network: fetch_and_extract is
    monkeypatched directly (both the main crawl's ThreadPoolExecutor and the
    probe route through the same module-level name), so this exercises
    main()'s OWN call to run_skip_sampling_probe(), the env var parsing, and
    end-to-end wiring through to the persisted state file."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    ingest_dir = tmp_path / "ingest"
    ingest_dir.mkdir()
    probe_state_path = tmp_path / "skip_probe_state.json"
    monkeypatch.setattr(o, "CACHE", cache_dir)
    monkeypatch.setattr(o, "INGEST", ingest_dir)
    monkeypatch.setattr(o, "PROBE_STATE_PATH", probe_state_path)
    monkeypatch.delenv("OECD_AIM_LIMIT", raising=False)
    # k=2 (not 1): k_rotate = 2//2 = 1 keeps the rotating half active even
    # against a 1-URL population -- k=1 would zero out k_rotate (1//2=0) and
    # this test would only ever exercise the recency-biased half.
    monkeypatch.setenv("OECD_AIM_PROBE_SAMPLE_SIZE", "2")
    monkeypatch.setattr(_common.time, "sleep", lambda *_a, **_k: None)

    url_normal = "https://oecd.ai/en/incidents/2026-02-01-abcd"
    url_legacy = "https://oecd.ai/en/incidents/991"  # the only skipped URL
    monkeypatch.setattr(o, "load_sitemap", lambda: [url_normal, url_legacy])

    normal_body = {
        "id": "2026-02-01-abcd",
        "title": "Ransomware attack disrupts AI-driven logistics platform",
        "date": "2026-02-01",
        "summary": "A ransomware attack disrupted an AI logistics platform.",
        "company": [], "articles": [], "aiid_ids": [],
    }
    normal_page = _make_page(script_offset_bytes=700, tail_bytes=700, body=normal_body)
    (cache_dir / "abcd.html").write_bytes(normal_page)

    def _fake_fetch_and_extract(url):
        if url == url_normal:
            return o._extract_state_detail(normal_page.decode("utf-8"))
        if url == url_legacy:
            # The probe fetches this "for real" -- still fails the
            # body-shape check, as the premise predicts.
            return o.REASON_NO_BODY_SHAPE, None
        raise AssertionError(f"unexpected fetch_and_extract call for {url}")

    monkeypatch.setattr(o, "fetch_and_extract", _fake_fetch_and_extract)

    o.main()

    out_text = capsys.readouterr().out
    assert "skip-rule sampling probe: fetching up to 1/1" in out_text
    assert "0 violations -- premise still holds" in out_text
    assert "coverage ledger: 1/1 (100.0%)" in out_text

    persisted = json.loads(probe_state_path.read_text(encoding="utf-8"))
    assert persisted["last_sample"] == [url_legacy]
    assert persisted["last_violations"] == []
    assert persisted["last_fetch_failed"] == []
    assert persisted["last_observed_count"] == 1
    assert persisted["cursor"] == 991
    assert persisted["last_run_id"]  # WS4-T17 BOUNCE #1 advisory 2: freshness stamp always present


def test_main_probe_all_fetch_failures_does_not_attest_premise_holds(monkeypatch, tmp_path, capsys):
    """WS4-T17 BOUNCE #1 defect 1, reproduced at the exact level the
    reviewer drove it: main() with EVERY probed URL returning
    REASON_FETCH_FAILED must NOT print the "premise still holds"
    attestation (0 observations is not evidence the premise holds), must
    surface the fetch-failure count/URLs, and must not silently fold a
    0-observed run into the lifetime "observed" counter as if real evidence
    had been collected."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    ingest_dir = tmp_path / "ingest"
    ingest_dir.mkdir()
    probe_state_path = tmp_path / "skip_probe_state.json"
    monkeypatch.setattr(o, "CACHE", cache_dir)
    monkeypatch.setattr(o, "INGEST", ingest_dir)
    monkeypatch.setattr(o, "PROBE_STATE_PATH", probe_state_path)
    monkeypatch.delenv("OECD_AIM_LIMIT", raising=False)
    monkeypatch.setenv("OECD_AIM_PROBE_SAMPLE_SIZE", "3")
    monkeypatch.setattr(_common.time, "sleep", lambda *_a, **_k: None)

    url_normal = "https://oecd.ai/en/incidents/2026-03-01-feed"
    legacy_urls = [f"https://oecd.ai/en/incidents/{n}" for n in (100, 200, 300)]
    monkeypatch.setattr(o, "load_sitemap", lambda: [url_normal] + legacy_urls)

    normal_body = {
        "id": "2026-03-01-feed",
        "title": "Prompt injection attack breaches AI customer support bot",
        "date": "2026-03-01",
        "summary": "A prompt injection attack breached a support bot.",
        "company": [], "articles": [], "aiid_ids": [],
    }
    normal_page = _make_page(script_offset_bytes=700, tail_bytes=700, body=normal_body)
    (cache_dir / "feed.html").write_bytes(normal_page)

    def _fake_fetch_and_extract(url):
        if url == url_normal:
            return o._extract_state_detail(normal_page.decode("utf-8"))
        if url in legacy_urls:
            # The exact scenario the reviewer drove: every probed legacy URL
            # fails to fetch at all -- zero observations, not zero violations.
            return o.REASON_FETCH_FAILED, None
        raise AssertionError(f"unexpected fetch_and_extract call for {url}")

    monkeypatch.setattr(o, "fetch_and_extract", _fake_fetch_and_extract)

    o.main()
    captured = capsys.readouterr()
    out_text = captured.out
    err_text = captured.err

    # The announcement line ("...to confirm the body-shape-check premise
    # still holds (WS4-T17)") is printed unconditionally before the probe
    # runs and legitimately contains this substring -- what must NEVER
    # appear is the AFFIRMATIVE ATTESTATION phrase specific to the "checked
    # and clean" branch.
    assert "0 violations -- premise still holds" not in out_text
    assert "0 violations -- premise still holds" not in err_text
    assert "observed NOTHING this run" in err_text
    for u in legacy_urls:
        assert u in err_text

    persisted = json.loads(probe_state_path.read_text(encoding="utf-8"))
    assert persisted["last_observed_count"] == 0
    assert sorted(persisted["last_fetch_failed"]) == sorted(legacy_urls)
    assert persisted["total_observed_lifetime"] == 0
    assert persisted["total_sampled_lifetime"] == 3
    assert persisted["coverage_ledger"]["observed_of_current_population"] == 0
