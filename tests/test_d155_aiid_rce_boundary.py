"""D155: AIID attack-vector `rce` and severity-High seeding must match `rce`
as a whole word, not inside "Reinforced" / "enforcement" / "source".
Hermetic: pure functions, no network.
"""
from __future__ import annotations

import pytest

from scrape_aiid import is_security_relevant, map_taxonomy, severity_for


def _e(title, desc=""):
    return {"title": title, "description": desc}


@pytest.mark.parametrize("title", [
    "RCE in Acme agent framework",
    "Remote code execution via chatbot plugin",
    "Command injection in LLM tool",
    "Sandbox escape from code interpreter",
])
def test_real_rce_terms_still_label_rce(title):
    tx = map_taxonomy(_e(title))
    assert tx["attack_vector"] == "rce"
    assert tx["owasp_llm"] == ["LLM10"]
    assert tx["owasp_asi"] == ["ASI05"]
    assert tx["mitre_atlas"] == ["AML.T0050"]


@pytest.mark.parametrize("title", [
    "ChatGPT Reinforced Bad Rent Advice",   # INC-17387 shape
    "Law enforcement used chatbot",
    "Open source model misused",
    "Police force deploys tool",
    "Divorce advice from an AI",
])
def test_rce_inside_words_does_not_label_rce(title):
    tx = map_taxonomy(_e(title))
    assert tx["attack_vector"] == "other"
    assert tx["owasp_llm"] == [] and tx["owasp_asi"] == [] and tx["mitre_atlas"] == []


def test_severity_rce_word_is_high_substring_is_medium():
    assert severity_for(_e("RCE in X")) == "High"
    assert severity_for(_e("Remote code execution")) == "High"
    assert severity_for(_e("Reinforced enforcement of source")) == "Medium"


def test_admission_filter_unchanged():
    # scrape_aiid.py:33 SECURITY_KEYWORDS is the ADMISSION filter and is
    # deliberately left substring-based (entries are never dropped).
    assert is_security_relevant(_e("Law enforcement"))
