"""D161: hackingincidents.ai ingest (facts + link only, D160).

Frozen fixture: tests/fixtures/hackingincidents/ledger_sample.json is a subset of the
2026-11-24 site copy with every free-text field replaced by a SENTINEL string, so the
tests can prove those fields never reach an output, while the facts under test
(slug, title, dates, actor, targets, roles, source URLs) are the real values.

Network safety: ``urllib.request.urlopen`` is replaced by a function that fails the
test; a code path that reached the network would fail here instead of passing because
the host happened to answer.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import pytest

import ingest_hackingincidents as H
import merge_and_dedupe as M

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "hackingincidents" / "ledger_sample.json"
SENTINEL = "SENTINEL-"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("test attempted a real network call")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    monkeypatch.setattr(H, "fetch_snapshot", _boom)


def _ledger() -> list[dict]:
    return copy.deepcopy(json.loads(FIX.read_text(encoding="utf-8"))["incidents"])


def _row(slug: str) -> dict:
    return next(x for x in _ledger() if x["id"] == slug)


def _corpus_row(inc: str, title: str, *, aiid: int | None = None, urls=(), year=2026, sids=None) -> dict:
    e = {"id": inc, "title": title, "year": year, "source_ids": sids or [f"X-{inc}"],
         "references": [{"title": u, "url": u, "type": "reference"} for u in urls]}
    if aiid:
        e["aiid_id"] = aiid
        e["source_ids"] = [f"AIID-{aiid}"]
    return e


# ---------------------------------------------------------------------------
# Extraction (facts), and excluded fields never present
# ---------------------------------------------------------------------------
def test_row_extraction_values():
    x = _row("binance-hot-wallet-compromised-ai-tool-2026")
    r = H.to_row(x)
    assert r["source_id"] == "HIAI-binance-hot-wallet-compromised-ai-tool-2026"
    assert r["title"] == x["title"]
    assert r["date"] == x["date"] and r["year"] == int(x["date"][:4])
    assert r["affected"] == x["targets"]
    assert r["corpus"] == "security" and r["quality_tier"] == "auto"
    assert r["description_provenance"] == "original" and r["description_source"] == "hackingincidents"
    assert r["content_license"]["license"] == "MIT" and r["content_license"]["obligations"] == ["attribution"]
    assert r["references"][0] == {
        "title": "hackingincidents.ai ledger entry binance-hot-wallet-compromised-ai-tool-2026",
        "url": "https://hackingincidents.ai/incident/binance-hot-wallet-compromised-ai-tool-2026/",
        "type": "reference"}
    assert [r2["url"] for r2 in r["references"][1:]] == [s["url"] for s in x["sources"]]
    pub = x["sources"][0]["publisher"]
    assert r["references"][1]["title"].startswith(pub + ": ")
    assert f"ledger-grade-{x['confidence'].lower()}" in r["tags"]
    if x.get("disclosed"):
        assert r["disclosure_date"] == x["disclosed"]


def test_excluded_fields_absent_from_every_output():
    rows, attach, stats, review = H.build(_ledger(), [])
    blob = json.dumps([rows, attach, review], ensure_ascii=False)
    assert SENTINEL not in blob
    for r in rows:
        assert not set(H.EXCLUDED_FIELDS) & set(r)
        assert "quote" not in r and "summary" not in r and "confidence_reason" not in r
        assert SENTINEL not in r["description"]


def test_description_is_template_over_facts():
    x = _row("3am-affiliate-uk-school-suspected-ai-2026")
    d = H.build_description(x)
    assert x["actor"] in d and x["targets"] in d and x["date"] in d
    assert "operations automation" in d and "strong" in d
    assert "not this project's assessment" in d
    assert H.build_description(x) == d            # deterministic


def test_committed_output_has_no_excluded_field_text():
    """On the REAL committed rows: no row's description shares an 8+ word run with
    the ledger quote of the same row. The quote text is not in the stripped snapshot, so this
    is the measurement taken on the raw bytes at strip time and recorded in provenance."""
    prov = json.loads((ROOT / "ingest" / "wave13_hackingincidents.provenance.json").read_text(encoding="utf-8"))
    m = prov["excluded_field_measurements"]
    # Measured 2026-11-26 over the 187 emitted rows: max run 7. Runs near the bound are
    # enumerated model names / actor labels (an 8-word run of "Claude Opus 4.5, Claude Haiku
    # 4.5, ..." was the one row that exceeded it before that row became an attachment), not prose.
    assert m["emitted_description_vs_quote"]["max_run"] < 8
    assert m["confidence_reason"]["rows_ge_8"] > 0     # why it is excluded


# ---------------------------------------------------------------------------
# Dedupe first, by URL / AIID join: attach, never create
# ---------------------------------------------------------------------------
def _binance_corpus():
    x = _row("binance-hot-wallet-compromised-ai-tool-2026")
    cite = next(s["url"] for s in x["sources"] if "incidentdatabase.ai/cite/" in s["url"])
    n = int(cite.rstrip("/").rsplit("/", 1)[1])
    return x, n, [_corpus_row("INC-17386", "Hackers Reportedly Used Internal AI Tool in Breach of Crypto Exchange",
                              aiid=n, urls=[cite])]


def test_aiid_join_attaches_instead_of_creating():
    x, n, corpus = _binance_corpus()
    assert n == 1817        # the ledger row citing AIID 1817 is INC-17386 in the real corpus
    rows, attach, stats, review = H.build([x], corpus)
    assert [r["source_id"] for r in rows] == []                      # NOT a new row
    (a,) = attach["attachments"]
    assert a["target"]["inc_id"] == "INC-17386" and a["level"] == "event" and "aiid" in a["basis"]
    assert a["references"][0]["url"] == "https://hackingincidents.ai/incident/" + x["id"] + "/"
    assert not any("incidentdatabase.ai/cite/" in r["url"] for r in a["references"])  # already on the row


def test_dedupe_check_fires_doctored_copy_creates_a_row():
    """The check can fail: the same ledger row with a different AIID number and no
    shared source URL is NOT a match and becomes a new row."""
    x, n, corpus = _binance_corpus()
    doctored = copy.deepcopy(x)
    doctored["id"] = "doctored-" + x["id"]
    doctored["title"] = "A wholly different event with another title entirely"
    for s in doctored["sources"]:
        s["url"] = s["url"].replace(f"/cite/{n}", "/cite/999999").replace("https://", "https://doctored.example/")
    rows, attach, *_ = H.build([doctored], corpus)
    assert [r["source_id"] for r in rows] == ["HIAI-doctored-" + x["id"]]
    assert attach["attachments"] == []
    # and a corrupted corpus (row removed) turns the real row into a new row too
    rows2, attach2, *_ = H.build([x], [])
    assert len(rows2) == 1 and attach2["attachments"] == []


def test_url_match_report_level_attaches_to_parent():
    x = _row("scopecreep-chatgpt-go-malware-2025")
    shared = x["sources"][0]["url"]
    corpus = [_corpus_row("INC-03003", "OpenAI June 2025 Disrupting Malicious Uses Report", urls=[shared])]
    rows, attach, stats, review = H.build([x], corpus)
    assert rows == [] and stats["attached_report"] == 1
    assert review["report_level"][0]["target"] == "INC-03003"
    assert attach["attachments"][0]["level"] == "report"


def test_url_match_with_similar_title_is_event_level():
    x = _row("binance-hot-wallet-compromised-ai-tool-2026")
    shared = x["sources"][-1]["url"]
    corpus = [_corpus_row("INC-1", x["title"], urls=[shared])]
    _, attach, *_ = H.build([x], corpus)
    assert attach["attachments"][0]["level"] == "event"


def test_aggregate_url_is_never_a_match_key(monkeypatch):
    x = _row("3am-affiliate-uk-school-suspected-ai-2026")
    shared = x["sources"][0]["url"]
    corpus = [_corpus_row("INC-9", "Unrelated roundup", urls=[shared])]
    assert H.build([x], corpus)[0] == []          # a normal shared URL matches (attach)
    monkeypatch.setattr(H, "is_aggregate_url", lambda u: True)
    rows, attach, *_ = H.build([x], corpus)
    assert len(rows) == 1 and attach["attachments"] == []


def test_multi_candidate_prefers_aiid_then_records_alternates():
    x, n, corpus = _binance_corpus()
    other = _corpus_row("INC-5", x["title"], urls=[x["sources"][-1]["url"]])
    _, attach, _, review = H.build([x], corpus + [other])
    assert attach["attachments"][0]["target"]["inc_id"] == "INC-17386"
    assert review["multi_candidate"][0]["alternates"] == ["INC-5"]


# ---------------------------------------------------------------------------
# In-ledger near-duplicate pair
# ---------------------------------------------------------------------------
def test_cairn_pair_collapses_to_one_row_keeping_both_pages_and_sources():
    rows, attach, stats, review = H.build(_ledger(), [])
    cairn = [r for r in rows if "cairn" in r["source_id"]]
    assert [r["source_id"] for r in cairn] == ["HIAI-cairn-monai-label-university-intrusions"]
    urls = [q["url"] for q in cairn[0]["references"]]
    assert "https://hackingincidents.ai/incident/cairn-monai-label-university-intrusion/" in urls
    assert "https://hackingincidents.ai/incident/cairn-monai-label-university-intrusions/" in urls
    assert any("cyware.com" in u for u in urls) and any("securityweek.com" in u for u in urls)
    assert review["collapsed_inledger"] == {
        "cairn-monai-label-university-intrusion": "cairn-monai-label-university-intrusions"}
    assert stats["collapsed_inledger"] == 1


def test_new_unreviewed_inledger_near_duplicate_aborts():
    led = _ledger()
    twin = copy.deepcopy(led[0])
    twin["id"] = led[0]["id"] + "s"
    with pytest.raises(H.LedgerError):
        H.build(led + [twin], [])


def test_shared_report_urls_are_fold_exempt_and_rows_stay_apart():
    rows, attach, *_ = H.build(_ledger(), [])
    gtg = [r for r in rows if r["source_id"].startswith("HIAI-gtg-")]
    assert len(gtg) == 2
    shared = {M.normalize_url(q["url"]) for q in gtg[0]["references"]} & \
             {M.normalize_url(q["url"]) for q in gtg[1]["references"]}
    shared.discard(M.normalize_url(gtg[0]["references"][0]["url"]))
    assert shared and shared <= set(attach["fold_exempt_urls"])


# ---------------------------------------------------------------------------
# The merger side: attach touches only references; exempt URLs do not fold
# ---------------------------------------------------------------------------
def _entry(sid, urls, **kw):
    e = {"id": "", "source_ids": [sid], "title": "T " + sid, "year": 2026, "date": "2026-01",
         "severity": "High", "tags": ["a"], "references": [{"title": u, "url": u} for u in urls]}
    e.update(kw)
    return e


def test_apply_attachments_appends_references_and_changes_nothing_else():
    e = _entry("S-1", ["https://a.example/x"])
    before = copy.deepcopy(e)
    att = [{"from": "HIAI-z", "target": {"inc_id": "INC-1", "source_ids": ["S-1"]},
            "references": [{"title": "t", "url": "https://hackingincidents.ai/incident/z/", "type": "reference"},
                           {"title": "dup", "url": "https://www.a.example/x/", "type": "report"}]}]
    exp = M._apply_reference_attachments([e], att)
    assert [r["url"] for r in e["references"]] == ["https://a.example/x", "https://hackingincidents.ai/incident/z/"]
    e2 = copy.deepcopy(e)
    e2["references"] = before["references"]
    assert e2 == before                                   # severity, tags, date, ... untouched
    assert exp[id(e)] == ("INC-1", "HIAI-z")


def test_dangling_attachment_aborts_loudly():
    att = [{"from": "HIAI-z", "target": {"inc_id": "INC-1", "source_ids": ["GONE"]},
            "references": [{"title": "t", "url": "https://x.example/", "type": "reference"}]}]
    with pytest.raises(SystemExit) as ei:
        M._apply_reference_attachments([_entry("S-1", ["https://a.example/x"])], att)
    assert "resolves to 0" in str(ei.value)


def test_attachment_landing_on_a_different_inc_id_aborts():
    e = _entry("S-1", ["https://a.example/x"])
    e["id"] = "INC-2"
    with pytest.raises(SystemExit):
        M._check_attachment_ids([e], {id(e): ("INC-1", "HIAI-z")})
    e["id"] = "INC-1"
    M._check_attachment_ids([e], {id(e): ("INC-1", "HIAI-z")})


def test_fold_exempt_url_prevents_url_fold_and_default_still_folds(monkeypatch):
    shared = "https://vendor.example/report"
    a = _entry("HIAI-a", [shared])
    b = _entry("HIAI-b", [shared])
    b["title"] = "A different title"
    surv, _ = M.dedupe_entries([copy.deepcopy(a), copy.deepcopy(b)])
    assert len(surv) == 1                                       # the failure the exemption prevents
    monkeypatch.setattr(M, "FOLD_EXEMPT_URLS", frozenset({M.normalize_url(shared)}))
    surv, _ = M.dedupe_entries([copy.deepcopy(a), copy.deepcopy(b)])
    assert len(surv) == 2


def test_attach_file_is_a_recognised_side_file_and_loads_no_rows(tmp_path):
    p = tmp_path / "x.attach.json"
    p.write_text(json.dumps({"attachments": [], "fold_exempt_urls": []}), encoding="utf-8")
    assert M._is_ingest_side_file(p) and M.load_source(p) == []


def test_malformed_attach_file_aborts(tmp_path, monkeypatch):
    (tmp_path / "bad.attach.json").write_text(json.dumps({"attachments": [{"target": {}}]}), encoding="utf-8")
    monkeypatch.setattr(M, "INGEST", tmp_path)
    with pytest.raises(SystemExit):
        M._load_reference_attachments()


# ---------------------------------------------------------------------------
# Provenance pin, offline rebuild
# ---------------------------------------------------------------------------
def test_provenance_pin_matches_committed_snapshot():
    prov = json.loads((ROOT / "ingest" / "wave13_hackingincidents.provenance.json").read_text(encoding="utf-8"))
    snap = prov["snapshot"]
    body = H.SNAPSHOT_FILE.read_bytes()
    assert hashlib.sha256(body).hexdigest() == snap["sha256"]       # the stripped file's own sha256
    assert len(body) == snap["bytes"]
    updated, rows = H.parse_snapshot(body)
    assert updated == snap["updated"] and len(rows) == snap["rows"]
    assert snap["url"] == "https://hackingincidents.ai/incidents.json"
    assert snap["fetched_utc"].endswith("Z") and "MIT" in prov["license"]
    assert snap["stripped"] is True
    assert len(snap["raw_sha256"]) == 64 and snap["raw_bytes"] > snap["bytes"]   # the raw download is pinned, not stored
    assert snap["raw_sha256"] != snap["sha256"]


def test_committed_snapshot_has_none_of_the_dropped_keys():
    data = json.loads(H.SNAPSHOT_FILE.read_text(encoding="utf-8"))
    assert data["stripped"] is True
    assert H.dropped_keys_present(data) == []
    prov = json.loads((ROOT / "ingest" / "wave13_hackingincidents.provenance.json").read_text(encoding="utf-8"))
    dropped = prov["snapshot"]["dropped_fields"]
    for k in ("quote", "summary", "confidence_reason", "outcome", "single_source_reason", "enrichment"):
        assert k in dropped
        assert all(k not in r for r in data["incidents"])
    raw = H.SNAPSHOT_FILE.read_text(encoding="utf-8")
    assert '"quote"' not in raw and '"summary"' not in raw and '"confidence_reason"' not in raw


def test_strip_removes_every_dropped_field_and_the_check_fires_on_the_raw_fixture():
    raw = json.loads(FIX.read_text(encoding="utf-8"))
    assert H.dropped_keys_present(raw)                       # the check FIRES on the raw form
    out = H.stripped_bytes(raw)
    assert SENTINEL.encode() not in out
    stripped = json.loads(out)
    assert H.dropped_keys_present(stripped) == []
    assert [r["id"] for r in stripped["incidents"]] == [r["id"] for r in raw["incidents"]]
    assert stripped["incidents"][0]["actor"] == raw["incidents"][0]["actor"]      # kept facts unchanged
    bad = copy.deepcopy(stripped)
    bad["incidents"][0]["quote"] = "x"                       # and fires on a stripped file that regained one
    assert H.dropped_keys_present(bad) == ["quote"]
    bad2 = copy.deepcopy(stripped)
    bad2["incidents"][0]["sources"][0]["verified_on"] = "2026-01-01"
    assert H.dropped_keys_present(bad2) == ["sources.verified_on"]


def _tmp_paths(monkeypatch, tmp_path):
    for name, f in (("OUT_FILE", "o.json"), ("ATTACH_FILE", "a.json"), ("PROVENANCE_FILE", "p.json"),
                    ("SNAPSHOT_FILE", "snap/incidents.json")):
        monkeypatch.setattr(H, name, tmp_path / f)
    monkeypatch.setattr(H, "SNAPSHOT_DIR", tmp_path / "snap")
    corpus = tmp_path / "corpus.json"
    corpus.write_text(json.dumps({"incidents": [_corpus_row("INC-1", "unrelated")]}), encoding="utf-8")
    return corpus


def test_fetch_path_verifies_raw_then_strips_and_never_writes_raw(monkeypatch, tmp_path):
    corpus = _tmp_paths(monkeypatch, tmp_path)
    raw_bytes = FIX.read_bytes()
    monkeypatch.setattr(H, "fetch_snapshot", lambda: raw_bytes)
    monkeypatch.setattr(sys, "argv", ["x", "--fetch", "--corpus", str(corpus)])
    assert H.main() == 0
    written = H.SNAPSHOT_FILE.read_bytes()
    assert SENTINEL.encode() not in written and H.dropped_keys_present(json.loads(written)) == []
    for f in (H.OUT_FILE, H.ATTACH_FILE, H.PROVENANCE_FILE):
        assert SENTINEL not in f.read_text(encoding="utf-8")
    snap = json.loads(H.PROVENANCE_FILE.read_text(encoding="utf-8"))["snapshot"]
    assert snap["raw_sha256"] == hashlib.sha256(raw_bytes).hexdigest() and snap["raw_bytes"] == len(raw_bytes)
    assert snap["sha256"] == hashlib.sha256(written).hexdigest()
    # --from-file: the stripped snapshot is accepted ...
    monkeypatch.setattr(sys, "argv", ["x", "--from-file", str(H.SNAPSHOT_FILE), "--dry-run", "--corpus", str(corpus)])
    assert H.main() == 0
    # ... and so is the raw download, verified against the pinned raw sha256 and stripped in memory
    rawf = tmp_path / "raw.json"
    rawf.write_bytes(raw_bytes)
    monkeypatch.setattr(sys, "argv", ["x", "--from-file", str(rawf), "--dry-run", "--corpus", str(corpus)])
    assert H.main() == 0
    rawf.write_bytes(raw_bytes + b" ")                          # a raw file that is not the pinned one
    with pytest.raises(H.LedgerError):
        H.main()


def test_tampered_snapshot_is_refused(tmp_path, monkeypatch):
    bad = tmp_path / "incidents.json"
    bad.write_bytes(H.SNAPSHOT_FILE.read_bytes() + b" ")
    monkeypatch.setattr(sys, "argv", ["x", "--from-file", str(bad), "--dry-run"])
    with pytest.raises(H.LedgerError) as ei:
        H.main()
    assert "sha256 does not match the pin" in str(ei.value)


def test_main_offline_from_pinned_snapshot_is_network_free(monkeypatch, tmp_path):
    for name in ("OUT_FILE", "ATTACH_FILE"):
        monkeypatch.setattr(H, name, tmp_path / getattr(H, name).name)
    monkeypatch.setattr(H, "PROVENANCE_FILE", ROOT / "ingest" / "wave13_hackingincidents.provenance.json")
    monkeypatch.setattr(sys, "argv", ["x", "--dry-run"])
    assert H.main() == 0                                          # urlopen + fetch_snapshot both raise


def test_committed_outputs_rebuild_byte_for_byte_from_the_pinned_snapshot():
    _, led = H.parse_snapshot(H.SNAPSHOT_FILE.read_bytes())
    corpus = json.loads(H.CORPUS_FILE.read_text(encoding="utf-8"))["incidents"]
    committed_attach = json.loads(H.ATTACH_FILE.read_text(encoding="utf-8"))
    prev = {(a["target"]["inc_id"], M.normalize_url(r["url"]))
            for a in committed_attach["attachments"] for r in a["references"]}
    rows, attach, *_ = H.build(led, corpus, prev)
    assert rows == json.loads(H.OUT_FILE.read_text(encoding="utf-8"))
    assert attach == committed_attach


# ---------------------------------------------------------------------------
# The built corpus carries exactly what the ingest says
# ---------------------------------------------------------------------------
def test_built_corpus_matches_ingest_outputs():
    inc = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    mine = [e for e in inc if any(s.startswith("HIAI-") for s in e["source_ids"])]
    rows = json.loads(H.OUT_FILE.read_text(encoding="utf-8"))
    assert len(mine) == len(rows) == len({s for e in mine for s in e["source_ids"]})  # one INC per ledger row, none folded
    assert all(e["corpus"] == "security" and e["quality_tier"] == "auto" for e in mine)
    by_id = {e["id"]: e for e in inc}
    for a in json.loads(H.ATTACH_FILE.read_text(encoding="utf-8"))["attachments"]:
        tgt = by_id[a["target"]["inc_id"]]
        assert not any(s.startswith("HIAI-") for s in tgt["source_ids"])      # attached, not created
        assert a["references"][0]["url"] in {r["url"] for r in tgt["references"]}


# ---------------------------------------------------------------------------
# Hand-reviewed title matches (REVIEWED_MATCHES)
# ---------------------------------------------------------------------------
def test_reviewed_match_attaches_when_no_url_or_aiid_matches(monkeypatch):
    x = _row("3am-affiliate-uk-school-suspected-ai-2026")
    corpus = [_corpus_row("INC-777", "Some other title for the same school ransomware event", urls=["https://other.example/a"])]
    assert H.build([x], corpus)[0] != []                           # no key matches: a new row
    monkeypatch.setitem(H.REVIEWED_MATCHES, x["id"], ("INC-777", "event"))
    rows, attach, stats, review = H.build([x], corpus)
    assert rows == [] and attach["attachments"][0]["target"]["inc_id"] == "INC-777"
    assert attach["attachments"][0]["basis"] == ["reviewed-title"]


def test_reviewed_match_to_a_missing_inc_id_aborts(monkeypatch):
    x = _row("3am-affiliate-uk-school-suspected-ai-2026")
    monkeypatch.setitem(H.REVIEWED_MATCHES, x["id"], ("INC-404", "event"))
    with pytest.raises(H.LedgerError) as ei:
        H.build([x], [_corpus_row("INC-1", "unrelated")])
    assert "INC-404" in str(ei.value)


def test_every_reviewed_match_target_exists_in_the_committed_corpus():
    inc = {e["id"] for e in json.loads(H.CORPUS_FILE.read_text(encoding="utf-8"))["incidents"]}
    assert set(t for t, _ in H.REVIEWED_MATCHES.values()) <= inc
    snap = {x["id"] for x in json.loads(H.SNAPSHOT_FILE.read_text(encoding="utf-8"))["incidents"]}
    assert set(H.REVIEWED_MATCHES) <= snap
