"""D117 / A2: aggregate round-up URLs are not reference-URL dedupe keys.

Guards the over-merge shape of INC-00924 / INC-02646 / INC-03233, where 15
distinct OWASP GenAI round-up incidents (no cve_ids) folded together because
they cite the same round-up page. See
docs/audits/overmerge-split-proposal-2026-10-13.md.
"""

from __future__ import annotations

import merge_and_dedupe as m

ROUNDUP = "https://genai.owasp.org/2025/07/14/owasp-gen-ai-incident-exploit-round-up-q225/"
ARTICLE = "https://example.com/news/one-specific-incident"


def _mk(title, srcs, urls, year=2025):
    return {
        "title": title, "year": year, "date": str(year),
        "cve_ids": [], "source_ids": srcs,
        "references": [{"url": u, "type": "article"} for u in urls],
        "tags": [],
    }


def test_is_aggregate_url_definition():
    k = m.normalize_url
    assert m.is_aggregate_url(k(ROUNDUP))
    assert m.is_aggregate_url(k("https://genai.owasp.org/2025/03/06/owasp-gen-ai-incident-exploit-round-up-jan-feb-2025/"))
    assert m.is_aggregate_url(k("https://genai.owasp.org/2026/04/14/owasp-genai-exploit-round-up-report-q1-2026/"))
    # Non-aggregate OWASP pages and ordinary articles are not.
    assert not m.is_aggregate_url(k("https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/"))
    assert not m.is_aggregate_url(k(ARTICLE))
    assert not m.is_aggregate_url("")


def test_shared_roundup_url_without_cve_does_not_merge():
    a = _mk("Incident alpha in agent runtime", ["OWASP-1"], [ROUNDUP])
    b = _mk("Totally different beta jailbreak", ["OWASP-2"], [ROUNDUP])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 2 and not tombstones


def test_transitive_claim_does_not_bridge_through_roundup():
    x = _mk("Incident alpha", ["S-x"], [ROUNDUP])
    y = _mk("Incident beta", ["S-y"], [ARTICLE])
    z = _mk("Incident beta follow-up", ["S-z"], [ROUNDUP, ARTICLE])
    surviving, tombstones = m.dedupe_entries([x, y, z])
    assert len(surviving) == 2 and not tombstones
    assert any("S-x" in s["source_ids"] and "S-y" not in s["source_ids"] for s in surviving)


def test_grandfathered_roundup_pair_still_merges():
    a = _mk("Incident alpha", ["OWASP-1"], [ROUNDUP])
    b = _mk("Incident beta", ["OWASP-2"], [ROUNDUP])
    prior = {"OWASP-1": "INC-00924", "OWASP-2": "INC-00924"}
    surviving, tombstones = m.dedupe_entries([a, b], prior)
    assert len(surviving) == 1
    assert sorted(surviving[0]["source_ids"]) == ["OWASP-1", "OWASP-2"]


def test_one_sided_prior_does_not_grandfather():
    a = _mk("Incident alpha", ["OWASP-1"], [ROUNDUP])
    b = _mk("Incident beta", ["OWASP-NEW"], [ROUNDUP])
    surviving, _ = m.dedupe_entries([a, b], {"OWASP-1": "INC-00924"})
    assert len(surviving) == 2


def test_non_aggregate_shared_article_url_still_merges():
    a = _mk("Incident alpha reported", ["S-a"], [ARTICLE])
    b = _mk("A different headline entirely", ["S-b"], [ARTICLE])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 1
    assert sorted(surviving[0]["source_ids"]) == ["S-a", "S-b"]
