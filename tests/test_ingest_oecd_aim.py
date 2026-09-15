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
# These tests exercise the REAL fetch_page() -> extract_state() path via
# robust_fetch()'s warm-cache disk-read branch (ingest/common.py:404-405):
# they write real HTML bytes to a cache file on disk and let fetch_page()
# read it back exactly as it would a page cached from a prior conduct-checked
# network fetch. No network call, no fetch_once()/robust_fetch() monkeypatch
# of the network layer -- robots_allowed()/urlopen() are never even reached,
# because the cache file already exists and is >= min_cache_bytes (the same
# branch a real second run of this ingester takes for every page it already
# has on disk).

NG_STATE_INCIDENT = {"id": "2026-05-01-feed", "title": "Large OECD AIM page parser-integrity test incident"}


def _ng_state_script_html(body: dict) -> str:
    """The exact `<script id="ng-state">...</script>` shape extract_state()
    parses: a dict whose value has a `"b"` key holding the incident body."""
    state = {"AppStateKey_0": {"b": body}}
    return f'<script id="ng-state" type="application/json">{json.dumps(state)}</script>'


def _make_page(script_offset_bytes: int, tail_bytes: int = 2000, body: dict | None = None) -> bytes:
    """Build a synthetic HTML page (as bytes) where the ng-state <script>
    tag begins at approximately `script_offset_bytes` into the page, with
    `tail_bytes` of filler after it (to simulate the rest of a real Angular
    SPA page: footer markup, other scripts, etc.)."""
    body = body or NG_STATE_INCIDENT
    unit = b"<!-- padding-filler-text-for-large-oecd-aim-page-simulation --> "
    before = (unit * (script_offset_bytes // len(unit) + 1))[:script_offset_bytes]
    after = (unit * (tail_bytes // len(unit) + 1))[:tail_bytes]
    script = _ng_state_script_html(body).encode("utf-8")
    return b"<html><head></head><body>" + before + script + after + b"</body></html>"


def _write_cached_page(monkeypatch, tmp_path, url: str, page_bytes: bytes) -> None:
    """Point the module's on-disk cache at tmp_path and pre-seed it with
    `page_bytes` so fetch_page()'s robust_fetch() call takes the warm-cache
    read branch (no network) -- the real code path a second run over an
    already-cached page takes."""
    monkeypatch.setattr(o, "CACHE", tmp_path)
    slug = url.rstrip("/").split("/")[-1]
    (tmp_path / f"{slug}.html").write_bytes(page_bytes)


def test_fetch_page_extracts_ng_state_from_page_well_beyond_800kb(monkeypatch, tmp_path):
    """A page far larger than 800 KB, with the ng-state blob starting well
    past byte 800,000, must still be fully readable and parseable -- this is
    the direct regression case for the gate-measured 7/250 truncated pages."""
    url = "https://oecd.ai/en/incidents/2026-05-01-feed"
    page = _make_page(script_offset_bytes=850_000)
    assert len(page) > 800_000
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    assert len(text) == len(page)  # not truncated

    body = o.extract_state(text)
    assert body is not None
    assert body["id"] == NG_STATE_INCIDENT["id"]
    assert body["title"] == NG_STATE_INCIDENT["title"]


def test_fetch_page_extracts_ng_state_straddling_the_800kb_boundary(monkeypatch, tmp_path):
    """Boundary case: the ng-state <script> tag OPENS just before byte
    800,000 and its JSON payload/closing tag extend past it -- the old
    `data[:800_000]` slice would cut the JSON mid-blob (json.loads failure)
    or cut the closing `</script>` entirely (regex non-match)."""
    url = "https://oecd.ai/en/incidents/2026-05-02-strd"
    body = {"id": "2026-05-02-strd", "title": "Straddling-boundary parser-integrity test incident"}
    page = _make_page(script_offset_bytes=799_970, body=body)
    script_html = _ng_state_script_html(body).encode("utf-8")
    script_start = page.index(script_html)
    script_end = script_start + len(script_html)
    # Confirm this synthetic page actually straddles the old cap -- otherwise
    # the test isn't exercising the boundary condition it claims to.
    assert script_start < 800_000 < script_end
    _write_cached_page(monkeypatch, tmp_path, url, page)

    text = o.fetch_page(url)
    assert text is not None
    assert len(text) == len(page)

    parsed = o.extract_state(text)
    assert parsed is not None
    assert parsed["id"] == body["id"]
    assert parsed["title"] == body["title"]


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
