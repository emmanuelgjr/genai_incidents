"""Smoke tests for the renderer's helpers."""

from __future__ import annotations

import re

import render_markdown as r


def test_sort_key_full_date_beats_year_only():
    a = {"date": "2026-05-10", "year": 2026, "title": "a"}
    b = {"date": "2026", "year": 2026, "title": "b"}
    assert r.sort_key(a) < r.sort_key(b)


def test_sort_key_newer_first():
    a = {"date": "2026-04-01", "year": 2026, "title": "a"}
    b = {"date": "2025-12-31", "year": 2025, "title": "b"}
    assert r.sort_key(a) < r.sort_key(b)


def test_truncate_title_short():
    assert r.truncate_title("short title", limit=80) == "short title"


def test_truncate_title_long():
    out = r.truncate_title("A" * 200, limit=80)
    assert len(out) == 80
    assert out.endswith("…")


def test_md_escape_pipes_and_newlines():
    assert r.md_escape("a|b\nc") == "a\\|b c"


def test_shard_rel_format():
    assert r.shard_rel(2026) == "docs/incidents/2026.md"


def test_year_bar_chart_produces_svg(tmp_path):
    from collections import Counter
    out = tmp_path / "year.svg"
    r.render_year_bar_chart(Counter({2024: 5, 2025: 8, 2026: 12}), out)
    body = out.read_text(encoding="utf-8")
    assert body.startswith("<svg")
    assert body.rstrip().endswith("</svg>")
    assert "2024" in body and "2026" in body


def test_owasp_bar_chart_uses_codes(tmp_path):
    from collections import Counter
    out = tmp_path / "owasp.svg"
    r.render_owasp_bar_chart(
        Counter({"LLM01": 10, "LLM10": 4}),
        {"LLM01": "Prompt Injection", "LLM10": "Improper Output Handling"},
        "OWASP LLM coverage",
        out,
    )
    body = out.read_text(encoding="utf-8")
    assert "LLM01" in body and "LLM10" in body
    assert "Prompt Injection" in body


def test_render_incident_block_produces_card():
    """The shared helper should produce an incident card with anchor div."""
    entry = {
        "id": "INC-00001",
        "title": "Test incident",
        "date": "2025-01-15",
        "year": 2025,
        "category": "real-world",
        "severity": "High",
        "description": "A test description.",
        "attack_vector": "prompt-injection",
        "owasp_llm": ["LLM01"],
        "references": [{"title": "Source", "url": "https://example.com", "type": "news"}],
        "tags": ["test"],
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert 'id="inc-00001"' in body
    assert "### INC-00001" in body
    assert "Test incident" in body
    assert "prompt-injection" in body
    assert "LLM01" in body
    assert "**Cite this incident:**" in body
    rendered_urls = re.findall(r"https?://[^\s)\"']+", body)
    # WS0-T6: with a single, non-AIID reference, that URL legitimately appears
    # twice — once in the References list, once in the "Cite this incident"
    # line (which points readers at the primary source, not this site).
    assert rendered_urls.count("https://example.com") == 2


def test_render_incident_block_cite_line_uses_primary_reference_by_default():
    """WS0-T6: no genai_incidents entry should ever be cited by pointing at
    this site — the default target is references[0] (the established
    'primary_reference' convention, merge_and_dedupe.py:1607)."""
    entry = {
        "id": "INC-00002", "title": "T", "date": "2025", "year": 2025,
        "category": "real-world", "severity": "High", "description": "d",
        "references": [
            {"title": "First source", "url": "https://first.example/a", "type": "news"},
            {"title": "Second source", "url": "https://second.example/b", "type": "news"},
        ],
    }
    body = "\n".join(r.render_incident_block(entry))
    assert "**Cite this incident:** [First source](https://first.example/a)" in body
    assert "https://second.example/b" not in body.split("**Cite this incident:**")[1]


def test_render_incident_block_cite_line_uses_aiid_cite_page_when_aiid_id_present():
    """AIID-derived entries cite AIID's own /cite/<id>/ page — one hop closer
    to the source than citing us, and AIID's page then links onward to the
    actual primary source."""
    entry = {
        "id": "INC-00003", "title": "T", "date": "2025", "year": 2025,
        "category": "real-world", "severity": "High", "description": "d",
        "aiid_id": 123,
        "references": [{"title": "Original news story", "url": "https://news.example/x", "type": "news"}],
    }
    body = "\n".join(r.render_incident_block(entry))
    assert "**Cite this incident:** [AI Incident Database](https://incidentdatabase.ai/cite/123/)" in body
    # The raw reference URL still appears once, in the References list — just
    # not as the cite target.
    assert body.count("https://news.example/x") == 1


def test_render_incident_block_handles_minimal_entry():
    """Minimal entry with only required fields should not crash."""
    entry = {
        "id": "INC-99999",
        "title": "Minimal",
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "Medium",
        "description": "",
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert "### INC-99999" in body
    assert "Minimal" in body


def test_render_incident_block_contains_self_anchor():
    """Incident block self-links to its #<slug> anchor (standalone per-incident
    pages were retired; the shard block is the canonical detail target)."""
    entry = {
        "id": "INC-00001",
        "title": "Test",
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "High",
        "description": "Desc.",
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert 'id="inc-00001"' in body
    assert "(#inc-00001)" in body
    assert "/incident/INC-00001.html" not in body


def test_severity_stack_renders_legend(tmp_path):
    from collections import Counter
    out = tmp_path / "sev.svg"
    r.render_severity_stack_chart(
        {2025: Counter({"Critical": 3, "High": 5, "Low": 1}),
         2026: Counter({"High": 7, "Medium": 4})},
        out,
    )
    body = out.read_text(encoding="utf-8")
    assert "Critical" in body and "High" in body
    assert "2025" in body and "2026" in body


def test_liquid_raw_block_wraps_and_defangs_endraw():
    body = [
        "Advisory text with {{ user.input }} and {% for x in y %} examples",
        "attempt to break out: {% endraw %} and {%- endraw -%}",
    ]
    wrapped = r.liquid_raw_block(body)
    assert wrapped[0] == "{% raw %}"
    assert wrapped[-1] == "{% endraw %}"
    inner = "\n".join(wrapped[1:-1])
    assert "{{ user.input }}" in inner          # benign Liquid left as-is
    assert "{% endraw %}" not in inner          # break-out sequences defanged
    assert "{ % endraw %}" in inner


def test_shard_body_is_liquid_safe():
    # Year shards wrap incident content (which can contain template-injection
    # advisory text like {{ }} / {% %}) in {% raw %} so Jekyll never parses it.
    e = {
        "id": "INC-99999", "title": "SSTI demo {{ 7*7 }}", "year": 2026,
        "severity": "High", "date": "2026-01-01",
        "description": "Exploit uses {% for i in (1..9) %} loops.",
        "source_ids": ["TEST-1"], "references": [], "tags": [],
    }
    shard = r.render_details_shard(2026, [e])
    _, _, body = shard.partition("---\n\n")
    assert "{% raw %}" in body
    assert body.rstrip().endswith("{% endraw %}")


# ---------------------------------------------------------------------------
# Stored-XSS hardening on shard markdown
# ---------------------------------------------------------------------------

def test_md_safe_text_escapes_prose_html():
    assert r.md_safe_text("<img src=x onerror=alert(1)>") == \
        "&lt;img src=x onerror=alert(1)&gt;"


def test_md_safe_text_escapes_unconditionally_incl_inline_code():
    # The bypass was an inline ```...``` payload mid-prose. Escape everything
    # so no parser divergence can let raw HTML through.
    assert r.md_safe_text("set to: ``` <img src=x onerror=alert(1)> ``` save") == \
        "set to: ``` &lt;img src=x onerror=alert(1)&gt; ``` save"
    assert "<script>" not in r.md_safe_text("```\n<script>a</script>\n```")
    assert "<img onerror" not in r.md_safe_text("see `<img onerror=x>` here")


def test_safe_url_blocks_dangerous_schemes():
    assert r.safe_url("javascript:alert(1)") == "#"
    assert r.safe_url("data:text/html,<script>") == "#"
    assert r.safe_url("https://example.com") == "https://example.com"
    assert r.safe_url("mailto:a@b.com") == "mailto:a@b.com"


def test_render_incident_block_neutralises_xss_description():
    block = "\n".join(r.render_incident_block({
        "id": "INC-08243", "title": "AVideo stored XSS", "year": 2026,
        "date": "2026-01-01", "severity": "High", "references": [], "tags": [],
        "description": "Save the category description to <img src=x onerror=alert(document.domain)> and trigger.",
    }))
    assert "<img src=x onerror=" not in block
    assert "&lt;img src=x onerror=" in block


def test_safe_url_rejects_embedded_html_and_whitespace():
    # Malformed scraped URL that swallowed an HTML tag must not pass through.
    assert r.safe_url('https://x.com/news/221899/ /> <meta property=') == "#"
    assert r.safe_url('https://ok.com/a?b=1&c=2') == 'https://ok.com/a?b=1&c=2'


# --- D64 (v2.13.0 item 8): DISPUTED card note --------------------------------


def _card(**extra):
    e = {"id": "INC-00001", "title": "t", "date": "2026-01-01",
         "category": "vulnerability-disclosure", "severity": "High",
         "description": "d", "cve_ids": ["CVE-2026-0001"]}
    e.update(extra)
    return "\n".join(r.render_incident_block(e))


def test_disputed_card_has_banner_and_says_it_stays_counted():
    card = _card(status="disputed",
                 status_reason={"code": "cve-disputed", "as_of": "2026-10-09"})
    assert "**DISPUTED**" in card and "checked 2026-10-09" in card
    assert "stays counted" in card
    assert "RETRACTED" not in card


def test_retracted_card_banner_unchanged_and_not_disputed():
    card = _card(status="retracted",
                 status_reason={"code": "cve-rejected", "as_of": "2026-10-09"})
    assert "**RETRACTED**" in card and "DISPUTED" not in card


def test_standing_card_has_neither_banner():
    card = _card()
    assert "DISPUTED" not in card and "RETRACTED" not in card
