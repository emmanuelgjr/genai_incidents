"""Parser contract tests for the wave-1/wave-2 ingests (WS4-T6 style):
``scripts/ingest_avid.py``, ``scripts/ingest_cvelistv5.py`` and the shared
``scripts/ai_relevance.py`` filter, each against RECORDED upstream records
under tests/fixtures/wave12/ and asserting field EXTRACTION (values), not
merely "does not crash".

Network safety: every test in this module runs with
``urllib.request.urlopen`` replaced by a function that fails the test, on top
of conftest.py's robots/rate-limit reset. A parser that reached the network
would fail loudly here rather than pass because the host happened to answer.
"""

from __future__ import annotations

import io
import json
import tarfile
import urllib.request
from pathlib import Path

import pytest

import ai_relevance as R
from corpus_overlap import CorpusIndex
import ingest_avid as AV
import ingest_cvelistv5 as CV

FIX = Path(__file__).parent / "fixtures" / "wave12"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("test attempted a real network call")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)


def _load(sub: str, name: str) -> dict:
    return json.loads((FIX / sub / name).read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------
# ai_relevance
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("desc,prods,expect", [
    ("x", ["langchain-ai/langchain"], True),                      # product segment
    ("x", ["Langflow OSS"], True),                                # product, spaced name
    ("x", ["mervinpraison/praisonai"], True),                     # curated seed
    ("A flaw in large language models handling", [], True),       # plural phrase
    ("Claude Code executes untrusted hooks", [], True),           # product form
    ("Assisted-by: Claude", [], False),                           # bare name = credit
    ("x", ["rhoai/odh-mlflow-rhel9"], False),                     # image name is not evidence
    ("The agent user prompt was displayed", [], False),           # weak words (INCLUSION s4)
    ("Use after free in libtiff", ["tiff"], False),
    ("Heap overflow in the Windows kernel", ["microsoft/windows"], False),
])
def test_assess_decisions(desc, prods, expect):
    assert R.assess(desc, prods)[0] is expect


def test_assess_reports_the_evidence():
    ok, why = R.assess("x", ["ollama/ollama"])
    assert ok and why["product"] == "ollama/ollama"


def test_filter_fires_on_corrupted_vocabulary(monkeypatch):
    """The check must be able to fail: with the product vocabulary emptied,
    a known AI product is no longer accepted."""
    assert R.assess("x", ["ollama/ollama"])[0]
    monkeypatch.setattr(R, "PRODUCT_FRAGMENTS", [])
    monkeypatch.setattr(R, "package_is_strongly_ai", lambda n: False)
    assert not R.assess("x", ["ollama/ollama"])[0]


# ----------------------------------------------------------------------------
# AVID
# ----------------------------------------------------------------------------
def test_avid_cve_entry_extraction():
    row = AV.to_row(_load("avid", "AVID-2026-R0045.json"), "reports/2026/AVID-2026-R0045.json")
    assert row["source_id"] == "AVID-2026-R0045"
    assert row["cve_ids"] == ["CVE-2025-27520"]
    assert row["title"] == ("BentoML Allows Remote Code Execution (RCE) via Insecure "
                            "Deserialization (CVE-2025-27520)")
    assert row["category"] == "vulnerability-disclosure"
    assert row["date"] == "2025-04" and row["year"] == 2025
    assert row["cvss_score"] == 9.8 and row["severity"] == "Critical"
    assert row["cvss_vector"].startswith("CVSS:3.1/")
    assert row["cwe_ids"] == ["CWE-502"]
    assert row["affected"] == "BentoML"
    assert row["avid_categories"] == ["S0100"]
    assert row["description"].startswith("BentoML is a Python library for building online serving")
    assert row["references"][0] == {
        "title": "AVID-2026-R0045", "url": "https://avidml.org/database/avid-2026-r0045/",
        "type": "advisory"}
    # MIT provenance travels on the row
    # CNA text delivered via AVID: the CVE ToU marker, not MIT (SOURCE_LICENSES 6.1)
    assert row["content_license"] == CV.CVE_TOU_MARKER
    assert row["description_source"] == "cve-cna-via-avid" and row["description_provenance"] == "verbatim"


def test_avid_third_party_report_description_is_original_prose_not_report_text():
    rec = _load("avid", "AVID-2026-R0420.json")
    row = AV.to_row(rec, "reports/2026/AVID-2026-R0420.json")
    assert row["title"] == "Google Gemini CLI Tool Discovery Code Execution"
    assert row["description_provenance"] == "original" and "description_source" not in row
    assert row["content_license"]["license"] == "MIT"
    body = AV._clean(rec["description"]["value"])
    assert not any(sent in row["description"] for sent in body.split(". ") if len(sent) > 25)
    assert "AVID-2026-R0420" in row["description"] and "mindgard.ai" in row["description"]
    assert row["description"] == AV.to_row(rec, "reports/2026/AVID-2026-R0420.json")["description"]
    assert "cve_ids" not in row


def test_avid_third_party_text_fires_if_verbatim_leaks(monkeypatch):
    """Prove the check can fail: re-introducing the verbatim first sentence breaks it."""
    rec = _load("avid", "AVID-2026-R0420.json")
    body = AV._clean(rec["description"]["value"])
    leaked = dict(AV.to_row(rec, "reports/2026/AVID-2026-R0420.json"), description=AV.first_sentences(body))
    assert any(sent in leaked["description"] for sent in body.split(". ") if len(sent) > 25)


def _tar(records: dict[str, dict]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for rel, d in records.items():
            data = json.dumps(d).encode()
            ti = tarfile.TarInfo(f"avidml-avid-db-abc1234/{rel}")
            ti.size = len(data)
            tar.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def _fixture_repo() -> dict[str, dict]:
    return {
        "reports/2026/AVID-2026-R0045.json": _load("avid", "AVID-2026-R0045.json"),
        "reports/2026/AVID-2026-R0420.json": _load("avid", "AVID-2026-R0420.json"),
        "reports/2026/AVID-2026-R0409.json": _load("avid", "AVID-2026-R0409.json"),
        "reports/2026/AVID-2026-R1127.json": _load("avid", "AVID-2026-R1127.json"),
        "vulnerabilities/2022/AVID-2022-V002.json": _load("avid", "AVID-2022-V002.json"),
        "reports/review/AVID-2023-R0004.json": {"metadata": {"report_id": "AVID-2023-R0004"}},
    }


def test_avid_build_applies_class_scope_and_relevance_rules():
    recs, commit = AV.read_records(_tar(_fixture_repo()))
    assert commit == "abc1234"
    assert "reports/review/AVID-2023-R0004.json" not in recs   # drafts never read
    rows, stats, review = AV.build(recs, corpus=[])
    ids = {r["source_id"] for r in rows}
    assert "AVID-2026-R0409" not in ids        # garak scan result: benchmark, not an incident
    assert "AVID-2026-R1127" not in ids        # d8s-strings backdoor: not AI-relevant
    assert {"AVID-2026-R0045", "AVID-2026-R0420"} <= ids
    assert stats["skipped_evaluation"] >= 1 and stats["skipped_not_ai_relevant"] == 1
    assert review["not_ai_relevant"][0]["id"] == "AVID-2026-R1127"


def test_avid_include_evaluations_flag_emits_scan_results():
    recs, _ = AV.read_records(_tar(_fixture_repo()))
    rows, _, _ = AV.build(recs, corpus=[], include_evaluations=True)
    assert "AVID-2026-R0409" in {r["source_id"] for r in rows}


def test_avid_dedupes_on_id_held_in_a_reference_url_not_only_source_ids():
    """The gate's finding in AVID form: membership must look past source_ids."""
    recs, _ = AV.read_records(_tar(_fixture_repo()))
    corpus = [{"source_ids": ["OTHER-1"], "title": "t", "references": [
        {"url": "https://avidml.org/database/avid-2026-r0420/"}]}]
    rows, stats, _ = AV.build(recs, corpus)
    assert "AVID-2026-R0420" not in {r["source_id"] for r in rows}
    assert stats["skipped_already_in_corpus"] == 1


def test_avid_cve_already_in_corpus_is_not_emitted_but_crosswalked():
    """Emitting it would make the merger re-cluster grandfathered multi-CVE
    entries (WS4-T19 split guard); the AVID<->CVE mapping is kept offline."""
    recs, _ = AV.read_records(_tar(_fixture_repo()))
    corpus = [{"id": "INC-00007", "source_ids": ["CVE-2025-27520"], "cve_ids": ["CVE-2025-27520"],
               "title": "x", "references": []}]
    rows, stats, review = AV.build(recs, corpus)
    assert "AVID-2026-R0045" not in {r["source_id"] for r in rows}
    assert stats["skipped_cve_already_in_corpus"] == 1 and stats["emitted_new_cve"] == 0
    assert review["avid_cve_crosswalk"] == {
        "AVID-2026-R0045": {"cves": ["CVE-2025-27520"], "corpus_entry": "INC-00007"}}


def test_avid_row_sharing_a_reference_url_with_the_corpus_is_not_emitted():
    """The merger's URL key would fold it into that entry (measured on
    AVID-2026-R1535 / INC-03558: a split the WS4-T19 guard aborts on)."""
    recs, _ = AV.read_records(_tar(_fixture_repo()))
    corpus = [{"id": "INC-00001", "source_ids": ["X"], "title": "t", "references": [
        {"url": "https://github.com/bentoml/BentoML/security/advisories/GHSA-33xw-247w-6hmc"}]}]
    rows, stats, review = AV.build(recs, corpus)
    assert "AVID-2026-R0045" not in {r["source_id"] for r in rows}
    assert stats["skipped_would_merge_into_existing"] == 1
    assert review["would_merge_into_existing"]["AVID-2026-R0045"] == {
        "key": "url", "corpus_entry": "INC-00001"}


def test_avid_cve_held_under_an_avid_keyed_entry_counts_as_present():
    """AVID-keyed corpus entry whose own text never names the CVE: AVID's
    repo (the crosswalk) says which CVE it stands for."""
    idx = CorpusIndex([{"id": "INC-00002", "source_ids": ["AVID-2026-R0045"], "title": "Foo",
                        "references": []}], {"AVID-2026-R0045": ["CVE-2025-27520"]})
    assert idx.cves["CVE-2025-27520"] == "INC-00002"
    assert "CVE-2025-27520" not in CorpusIndex([{"id": "INC-00002", "source_ids": ["AVID-2026-R0045"],
                                                 "title": "Foo", "references": []}]).cves


# ----------------------------------------------------------------------------
# cvelistV5
# ----------------------------------------------------------------------------
def test_cvelistv5_huntr_record_extraction():
    rec = _load("cvelistv5", "CVE-2024-2928.json")
    ok, why = R.assess(CV._en(rec["containers"]["cna"]["descriptions"]), CV.product_strings(rec))
    assert ok
    row = CV.to_row(rec, why)
    assert row["source_id"] == row["cve_id"] == "CVE-2024-2928"
    assert row["category"] == "vulnerability-disclosure"
    assert row["date"] == "2024-06" and row["year"] == 2024
    assert row["description"].startswith("A Local File Inclusion (LFI) vulnerability")
    assert "huntr" in row["tags"] and "cvelistv5" in row["tags"]
    assert row["cvss_score"] == 7.5 and row["severity"] == "High"
    assert row["cwe_ids"] == ["CWE-29"]
    urls = [r["url"] for r in row["references"]]
    assert urls[0] == "https://nvd.nist.gov/vuln/detail/CVE-2024-2928"
    assert any("huntr.com/bounties/" in u for u in urls)           # bounty URL kept as a link
    assert [r for r in row["references"] if "huntr.com" in r["url"]][0]["type"] == "disclosure"
    assert row["content_license"]["license"] == "CVE-TOU"
    assert row["description_source"] == "cvelistv5"


def test_cvelistv5_description_only_match():
    rec = _load("cvelistv5", "CVE-2026-85740.json")
    ok, why = R.assess(CV._en(rec["containers"]["cna"]["descriptions"]), CV.product_strings(rec))
    assert ok and why["description"] == "retrieval-augmented"
    assert "huntr" not in CV.to_row(rec, why)["tags"]


def test_cvelistv5_rejects_non_ai_and_image_name_noise():
    for name in ("CVE-2024-44088.json", "CVE-2026-4775.json"):
        rec = _load("cvelistv5", name)
        assert not R.assess(CV._en(rec["containers"]["cna"]["descriptions"]),
                            CV.product_strings(rec))[0], name


def test_huntr_cna_match_is_exact():
    assert CV.is_huntr({"cveMetadata": {"assignerShortName": "@huntr_ai"}})
    assert CV.is_huntr({"cveMetadata": {"assignerShortName": "huntr_ai"}})
    assert not CV.is_huntr({"cveMetadata": {"assignerShortName": "Huntress"}})


def _build(records, corpus=()):
    return CV.build(iter(records), CorpusIndex(list(corpus)), since="2024-01-01",
                    backlog_end="2026-06-30")


def test_cvelistv5_build_never_emits_rejected_even_when_it_would_match():
    rec = _load("cvelistv5", "CVE-2024-2928.json")
    rejected = json.loads(json.dumps(rec))
    rejected["cveMetadata"]["state"] = "REJECTED"
    rows, stats, *_ = _build([rejected])
    assert rows == [] and stats["not_published"] == 1 and stats["rejected_ai_match"] == 1


def test_cvelistv5_real_rejected_huntr_record_is_not_emitted():
    rows, stats, *_ = _build([_load("cvelistv5", "CVE-2024-12534.json")])
    assert rows == [] and stats["not_published"] == 1


def test_cvelistv5_build_skips_cves_already_in_corpus_and_splits_windows():
    recs = [_load("cvelistv5", "CVE-2024-2928.json"), _load("cvelistv5", "CVE-2026-85740.json")]
    corpus = [{"id": "INC-00003", "source_ids": ["CVE-2024-2928"], "cve_ids": ["CVE-2024-2928"],
               "title": "x", "references": []}]
    rows, stats, window, huntr_total, *_ = _build(recs, corpus)
    assert [r["source_id"] for r in rows] == ["CVE-2026-85740"]
    assert stats["already_in_corpus"] == 1
    assert huntr_total["backlog_already_in_corpus"] == 1
    assert window["backlog"]["already_in_corpus"] == 1       # published 2024-06
    assert window["post_backlog"]["emitted"] == 1            # published after 2026-06-30


def test_cvelistv5_skips_a_record_the_merger_would_fold_into_a_cve_less_entry():
    """A GHSA-only corpus entry that shares the advisory URL would absorb the
    CVE record (changing its title/severity/quality_tier): leave it alone."""
    rec = _load("cvelistv5", "CVE-2026-85740.json")
    adv = next(r["url"] for r in rec["containers"]["cna"]["references"] if "github.com" in r["url"])
    corpus = [{"id": "INC-00004", "source_ids": ["GHSA-aaaa-bbbb-cccc"], "title": "Something else",
               "year": 2026, "references": [{"url": adv}]}]
    rows, stats, _, _, _, _, merges = _build([rec], corpus)
    assert rows == [] and stats["would_merge_into_existing"] == 1
    assert merges["CVE-2026-85740"] == {"key": "url", "corpus_entry": "INC-00004"}


def test_cvelistv5_does_not_skip_on_a_url_shared_with_a_different_cve_entry():
    """Weak keys never bridge disjoint CVE sets (cve_disjoint): such a record
    is a legitimate NEW entry, not a merge."""
    rec = _load("cvelistv5", "CVE-2026-85740.json")
    adv = next(r["url"] for r in rec["containers"]["cna"]["references"] if "github.com" in r["url"])
    corpus = [{"id": "INC-00005", "source_ids": ["CVE-2026-00001"], "cve_ids": ["CVE-2026-00001"],
               "title": "Other", "year": 2026, "references": [{"url": adv}]}]
    rows, stats, *_ = _build([rec], corpus)
    assert len(rows) == 1 and stats["would_merge_into_existing"] == 0


def test_cvelistv5_membership_looks_past_cve_source_ids():
    corpus = [{"id": "INC-00006", "source_ids": ["AVID-2026-R0006"], "title": "Foo (CVE-2024-10513)",
               "references": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2024-99999"}]}]
    idx = CorpusIndex(corpus)
    assert {"CVE-2024-10513", "CVE-2024-99999"} <= set(idx.cves)


def test_cvelistv5_membership_check_fires_on_corruption():
    """Corrupting the corpus (removing the title mention) makes the
    AVID-keyed CVE invisible -- the check can fail."""
    corpus = [{"id": "INC-00006", "source_ids": ["AVID-2026-R0006"], "title": "Foo (CVE-2024-10513)",
               "references": []}]
    assert "CVE-2024-10513" in CorpusIndex(corpus).cves
    broken = [dict(corpus[0], title="Foo")]
    assert "CVE-2024-10513" not in CorpusIndex(broken).cves


def test_fetch_helpers_refuse_the_network_in_tests():
    with pytest.raises(AssertionError):
        urllib.request.urlopen("https://example.com")


# ----------------------------------------------------------------------------
# arXiv OAI-PMH
# ----------------------------------------------------------------------------
import ingest_arxiv_oaipmh as AX  # noqa: E402


def _arxiv_records():
    return AX.parse_page((FIX / "arxiv" / "listrecords_sample.xml").read_bytes())


def test_arxiv_parse_extracts_metadata_fields():
    recs, token = _arxiv_records()
    assert token == "TOKEN123|1001"
    by_id = {r["id"]: r for r in recs}
    r = by_id["2510.10271"]
    assert r["title"].startswith("MetaBreak: Jailbreaking Online LLM Services")
    assert r["authors"][:2] == ["Wentian Zhu", "Zhen Xiang"]
    assert r["categories"] == ["cs.CR", "cs.AI"]
    assert r["created"] == "2026-06-26" and r["abstract"].startswith("Unlike regular tokens")
    assert by_id["2501.00001"] == {"id": "2501.00001", "deleted": True}


def test_arxiv_parse_refuses_a_dtd():
    evil = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"/>'
    with pytest.raises(ValueError):
        AX.parse_page(evil)


def test_arxiv_select_keeps_attacks_on_genai_and_drops_defenses_and_non_genai():
    recs, _ = _arxiv_records()
    by_id = {r["id"]: r for r in recs if not r.get("deleted")}
    assert AX.select(by_id["2510.10271"])[0]        # jailbreak of online LLM services
    assert AX.select(by_id["2511.16709"])[0]        # backdoor attacks via LLM agents
    assert not AX.select(by_id["2510.20768"])[0]    # RAGRank: a defense ("Counter")
    assert not AX.select(by_id["2601.10173"])[0]    # alignment defense
    assert not AX.select(by_id["2509.16950"])[0]    # backdoor on RL driving agents: not GenAI


def test_arxiv_selection_reasons_are_recorded():
    recs, _ = _arxiv_records()
    r = next(x for x in recs if x["id"] == "2510.10271")
    ok, why = AX.select(r)
    assert ok and why["headline"].startswith("jailbreak") and why["concrete"]


def test_arxiv_filter_fires_on_corruption():
    """Remove the concrete-evidence sentence and the paper must drop out."""
    recs, _ = _arxiv_records()
    r = dict(next(x for x in recs if x["id"] == "2510.10271"))
    assert AX.select(r)[0]
    r["abstract"] = "A new method for generating adversarial prompts."
    assert not AX.select(r)[0]


def test_arxiv_row_is_metadata_only_with_cc0_provenance():
    recs, _ = _arxiv_records()
    r = next(x for x in recs if x["id"] == "2510.10271")
    row = AX.to_row(r, AX.select(r)[1])
    assert row["source_id"] == "ARXIV-2510.10271"
    assert row["category"] == "research"
    # OAI created is the LATEST version date (2026-06); v1 month comes from the id
    assert r["created"] == "2026-06-26" and AX.v1_month(r) == "2025-10"
    assert row["date"] == "2025-10" and row["year"] == 2025
    assert row["references"][0]["url"] == "https://arxiv.org/abs/2510.10271"
    assert row["references"][0]["type"] == "paper"
    # description is original, deterministic prose and never the abstract
    assert row["description"] != r["abstract"]
    assert r["abstract"][:80] not in row["description"]
    assert "arXiv:2510.10271" in row["description"] and "jailbreak" in row["description"].lower()
    assert row["description_provenance"] == "original" and "description_source" not in row
    assert row == AX.to_row(r, AX.select(r)[1])      # deterministic
    assert not any("/pdf/" in x["url"] or "e-print" in x["url"] for x in row["references"])


def test_arxiv_build_dedupes_against_corpus_by_id_in_urls_and_source_ids():
    recs, _ = _arxiv_records()
    known = AX.known_arxiv_ids(
        [{"source_ids": [], "references": [{"url": "https://arxiv.org/pdf/2511.16709v2"}]}],
        [{"source_id": "ARXIV-2510.10271"}])
    assert known == {"2511.16709", "2510.10271"}
    rows, stats, _ = AX.build(recs, since=__import__("datetime").date(2025, 10, 1), known=known)
    assert rows == [] and stats["already_in_corpus"] == 2 and stats["deleted"] == 1


def test_arxiv_build_skips_a_paper_the_merger_would_fold_into_an_existing_entry():
    recs, _ = _arxiv_records()
    r = next(x for x in recs if x["id"] == "2510.10271")
    corpus = [{"id": "INC-00009", "source_ids": ["X"], "title": r["title"], "year": 2026,
               "references": []}]
    rows, stats, _ = AX.build([r], since=__import__("datetime").date(2025, 10, 1), known=set(),
                              idx=CorpusIndex(corpus))
    assert rows == [] and stats["would_merge_into_existing"] == 1
    assert stats["_merges"]["2510.10271"] == {"key": "title", "corpus_entry": "INC-00009"}


# ----------------------------------------------------------------------------
# OSV path: OpenSSF Malicious Packages (MAL-, Apache-2.0) are never admitted
# ----------------------------------------------------------------------------
import ingest_cve_nvd_expanded as NVD  # noqa: E402


def test_osv_path_excludes_openssf_malicious_packages_records():
    mal = _load("osv", "MAL-2026-2144.json")
    ok = _load("osv", "GHSA-ordinary.json")
    assert NVD.is_openssf_malicious(mal) and NVD.osv_to_record(mal) is None
    assert not NVD.is_openssf_malicious(ok)
    rec = NVD.osv_to_record(ok)
    assert rec and rec["source_id"] == "CVE-2025-00001"


def test_openssf_filter_catches_alias_and_source_marker():
    assert NVD.is_openssf_malicious({"id": "GHSA-x", "aliases": ["MAL-2026-1"]})
    assert NVD.is_openssf_malicious({"id": "X", "database_specific": {
        "source": "https://github.com/ossf/malicious-packages/x.json"}})


def test_openssf_filter_fires_without_the_guard(monkeypatch):
    """Prove the test can fail: with the predicate neutered the MAL record is
    converted and its verbatim text would be carried."""
    mal = _load("osv", "MAL-2026-2144.json")
    monkeypatch.setattr(NVD, "is_openssf_malicious", lambda v: False)
    rec = NVD.osv_to_record(mal)
    assert rec is not None and "exfiltrate credentials" in rec["description"]


def test_committed_nvd_expanded_file_carries_no_openssf_report_text():
    """MAL rows survive only as bare identifiers (facts + links); no row may
    carry the Apache-2.0 report text."""
    rows = json.loads((Path(__file__).parents[1] / "ingest" / "cve_nvd_expanded.json").read_text(encoding="utf-8"))
    mal = [r for r in rows if NVD.is_openssf_malicious_row(r)]
    assert [r["source_id"] for r in mal] == ["MAL-2026-3607"]
    for r in mal:
        assert r["description"].startswith("Bare identifier for OpenSSF") and r["description_provenance"] == "original"
        assert "Per source details" not in r["description"] and "google-open-source-security" not in r["description"]


# ----------------------------------------------------------------------------
# Gate BOUNCE #1 (D6): named description-only false positives must stay out
# ----------------------------------------------------------------------------
_GATE_FPS = json.loads((FIX / "cvelistv5" / "gate1_false_positives.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("cve", sorted(_GATE_FPS))
def test_gate_named_false_positives_are_out_and_ruby_llm_stays_in(cve):
    f = _GATE_FPS[cve]
    ok, _ = R.assess(f["description"], f["products"], f["assigner"])
    assert ok is (f["expect"] == "in"), cve


def test_gpt_regex_is_bounded_to_model_names():
    assert not R.assess("The MitraStar GPT-2742GX router has a flaw", [], "twcert")[0]
    assert R.assess("Prompt handling in GPT-4o and gpt-4-turbo deployments is unsafe. The LLM leaks", [], "x")[0]


def test_credit_and_trailer_clauses_are_stripped_before_matching():
    assert not R.assess("Bug in the scheduler. Reported by Claude Code.", [], "x")[0]
    assert not R.assess("Bug in the scheduler.\nAssisted-by: Claude Sonnet 4", [], "x")[0]


def test_linux_cna_description_only_matches_are_rejected():
    assert not R.assess("sysctl_igmp_llm_reports is read without a lock", [], "Linux")[0]


def test_description_only_match_needs_a_second_signal():
    assert not R.assess("Foo is an AI chatbot builder. CSRF in the settings page.", [], "x")[0]
    assert R.assess("Foo is an AI chatbot builder. Prompt injection reaches the model.", [], "x")[0]
    assert R.assess("Bar MCP server allows path traversal.", [], "x")[0]


@pytest.mark.parametrize("rule", ["credits", "linux_cna", "second_signal"])
def test_each_rule_fires_when_enabled_and_not_when_disabled(rule, monkeypatch):
    cases = {
        "credits": ("Bug in the scheduler. Reported by Claude Code.", [], "x"),
        "linux_cna": ("sysctl_igmp_llm_reports is read without a lock. The LLM and language model.", [], "Linux"),
        "second_signal": ("Foo is an AI chatbot builder. CSRF in the settings page.", [], "x"),
    }
    for other in R.RULES:                       # isolate the rule under test
        monkeypatch.setitem(R.RULES, other, other == rule)
    assert not R.assess(*cases[rule])[0]      # enabled: it is caught
    monkeypatch.setitem(R.RULES, rule, False)
    assert R.assess(*cases[rule])[0]          # disabled: the false positive gets through


def test_arxiv_window_applies_to_v1_month_not_latest_version_date():
    """2411.16769 was first submitted 2024-11 but its OAI created is 2026-09:
    it must be dropped from a 2025-10 window and must not be dated 2026-09."""
    rec = {"id": "2411.16769", "created": "2026-09-26", "title":
           "Jailbreaking ChatGPT via X", "abstract": "We demonstrate on commercial models.",
           "authors": ["A B"], "categories": ["cs.CR"]}
    assert AX.select(rec)[0]
    rows, stats, _ = AX.build([rec], since=__import__("datetime").date(2025, 10, 1), known=set())
    assert rows == [] and stats["v1_before_window"] == 1
    rows, _, _ = AX.build([dict(rec, id="2510.00001")], since=__import__("datetime").date(2025, 10, 1), known=set())
    assert rows[0]["date"] == "2025-10"


def test_arxiv_rows_are_machine_selected_and_reach_the_corpus_as_auto():
    import merge_and_dedupe as M
    recs, _ = _arxiv_records()
    r = next(x for x in recs if x["id"] == "2510.10271")
    row = AX.to_row(r, AX.select(r)[1])
    assert row["quality_tier"] == "auto"
    assert M.normalize_entry(row)["quality_tier"] == "auto"
    # a source cannot self-promote
    assert "quality_tier" not in M.normalize_entry(dict(row, quality_tier="curated"))


def test_avid_and_cvelistv5_rows_are_machine_ingested_auto():
    import merge_and_dedupe as M
    a = AV.to_row(_load("avid", "AVID-2026-R0045.json"), "reports/2026/AVID-2026-R0045.json")
    rec = _load("cvelistv5", "CVE-2024-2928.json")
    c = CV.to_row(rec, {})
    for row in (a, c):
        assert row["quality_tier"] == "auto"
        assert M.normalize_entry(row)["quality_tier"] == "auto"
