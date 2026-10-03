"""
ai_relevance.py
===============

One shared, precision-first AI-relevance decision for CVE-shaped records,
used by ``ingest_cvelistv5.py`` and ``ingest_avid.py`` so the inclusion policy
is enforced in one place (INCLUSION.md section 4).

It REUSES the project's existing vocabularies from
``scripts/ingest_cve_nvd_expanded.py`` rather than inventing a regex:

  * ``package_is_strongly_ai`` / ``STRONG_AI_PACKAGE_TOKENS`` -- the delimited-
    segment matcher INCLUSION.md section 4 already mandates for packages;
  * ``AI_PRODUCT_CPE_FRAGMENTS`` -- the product list the NVD sweep matches
    against CPE strings;
  * ``AI_CONTEXT_TOKENS`` -- the description-token list the NVD sweep applies
    after a keyword search.

What it changes, and why: the NVD path matches ``AI_CONTEXT_TOKENS`` as raw
substrings (``"agent"``, ``"prompt"``, ``"ai "``, ``"ml "``, ``"nemo"``...),
which INCLUSION.md section 4 forbids as standalone matches ("they are the
documented cause of false positives") and which is tolerable there only
because an NVD keyword search runs first. A full CVE dump has no such first
stage, so this module (a) drops the tokens INCLUSION.md names as weak, and
the other dictionary-word tokens of the same kind, from the description test
(``WEAK_TOKENS``), (b) matches the remainder on word boundaries, and (c)
matches product fields (vendor / product / packageName / repo / collection
URL / CPE) as delimited segments, never as substrings.

``data/ai_package_allowlist.json`` (WS4-T4) does not exist yet. When it does,
``PRODUCT_FRAGMENTS`` should be sourced from it; the decision API
(``assess``) will not change.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_cve_nvd_expanded import (  # noqa: E402
    AI_CONTEXT_TOKENS,
    AI_PRODUCT_CPE_FRAGMENTS,
    package_is_strongly_ai,
)

# Description tokens that must never decide relevance on their own
# (INCLUSION.md section 4 names ai / ml / nemo / ray / prompt / agent /
# guidance; the rest are the same kind: dictionary words or names of
# non-AI products that the NVD list carried because a keyword search had
# already narrowed the field).
WEAK_TOKENS = {
    "agent", "prompt", "ai ", " ai-", "ml ", "rag ", "nemo", "guardrails",
    "embedding", "transformer", "neural", "triton", "cursor", "copilot",
    "cody", "sourcegraph", "mistral", "haystack", "rasa", "mcp ",
    "fine-tuning", "model serving", "inference server", "ray.io", "claude",
}
# The weak words stay available to the PRODUCT-field test below, which
# matches them as whole segments of a vendor/product name rather than as
# words in prose.

# Fragments of AI_PRODUCT_CPE_FRAGMENTS that are not AI-specific as a
# vendor/product SEGMENT (a big non-AI vendor, a generic word, an unrelated
# parser) and therefore may not decide relevance alone.
WEAK_FRAGMENTS = {
    "google", "cursor", "cody", "sourcegraph", "binplist", "ray_project",
    "transformers", "guidance", "haystack", "rasa",
}


# Curated ecosystem seed (WS4-T4 coverage criterion (b)): AI/ML products whose
# names the inherited vocabulary lacks, each one MEASURED as a miss in the
# 2024-2026 cvelistV5 window (docs/audits/wave12-ingest-delta-2026-10-03.md,
# "filter recall"). Matched as whole segment runs of a vendor / product /
# package / repo name, like every other fragment. The WS4-T4
# ``data/ai_package_allowlist.json`` is the intended home for this list.
ECOSYSTEM_SEED = [
    "nemo-framework", "nemo-speech", "nemoclaw", "bionemo", "ai-infra-guard",
    "picklescan", "paddlepaddle", "fastdeploy", "mmdetection", "open-mmlab",
    "gluonts", "gluon-cv", "superagi", "lollms", "sillytavern", "keras",
    "langroid", "pydantic-ai", "lightrag", "ragflow", "maxkb", "mindsdb",
    "crawl4ai", "lavague", "toolhive", "nextchat", "fastgpt", "chuanhuchatgpt",
    "gpt-academic", "db-gpt", "praisonai", "praisonaiagents", "lunary",
    "hermes-agent", "hermes-webui", "9router", "vanna-ai", "roo-code",
    "roocodeinc", "danswer", "cowagent", "astrbot", "nanoclaw", "xinference",
    "llamafactory", "fastchat", "ragas", "scikit-learn", "lightgbm", "mlx",
    "smolagents", "agno-agi", "mem0", "letta", "dspy", "invoke-ai",
    "kohya-ss", "whisper-cpp", "claude", "vertex-ai", "gemini-cli",
    "copilot-studio", "microsoft-365-copilot", "copilot-chat", "ollama-mcp",
    "cohere-terrarium", "qwen-agent", "autogpt", "mindsdb", "ray-project",
    "aimhubio", "applio", "embedai", "apache-submarine", "odh-dashboard",
    "openshift-data-science", "cvat", "watson-studio",
]

# Red Hat container-image names (``rhoai/odh-...-rhel9``, ``rhaiis/vllm-...``)
# list every CVE of every library baked into the image; the image name is not
# evidence that the CVE is about AI (INCLUSION.md section 3: "a CVE in a
# logging lib, even if used by an AI app").
_IMAGE_NAME_RE = re.compile(r"-rhel\d", re.I)


def _norm_segments(s: str) -> str:
    segs = [x for x in re.split(r"[^a-z0-9]+", (s or "").lower()) if x]
    return "-" + "-".join(segs) + "-" if segs else ""


# Strong description phrases: AI_CONTEXT_TOKENS minus WEAK_TOKENS, word-bounded.
_DESC_TOKENS = sorted({t.strip() for t in AI_CONTEXT_TOKENS if t not in WEAK_TOKENS and t.strip()})
_DESC_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(t) for t in _DESC_TOKENS) + r")s?(?![A-Za-z0-9])",
    re.I,
)
# A few unambiguous standalone words the token list spells with a trailing
# space or hyphen ("llm", "gpt-"), handled explicitly.
_EXTRA_DESC_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:llms?|gpt-\d\w*|mcp servers?|ai agents?|ai models?|ml models?|"
    r"machine-learning|vector stores?|prompt injection|"
    # "Claude" alone also names a person / appears in patch trailers and
    # discovery credits; only the product forms count.
    r"claude(?:[ -](?:code|desktop|ai|api|sdk|agent|opus|sonnet|haiku|\d)|\.md))(?![A-Za-z0-9])"
    r"|\.claude/", re.I)

PRODUCT_FRAGMENTS = sorted(
    {_norm_segments(f) for f in list(AI_PRODUCT_CPE_FRAGMENTS) + ECOSYSTEM_SEED
     if f not in WEAK_FRAGMENTS} - {""}
)


def product_match(product_strings: list[str]) -> str | None:
    """First product string that strongly matches an AI identifier as a
    delimited segment (or segment run), else None."""
    for s in product_strings:
        if not s or s.strip().lower() in ("n/a", "unspecified", "unknown"):
            continue
        if _IMAGE_NAME_RE.search(s):
            continue
        if package_is_strongly_ai(s):
            return s
        hay = _norm_segments(s)
        for frag in PRODUCT_FRAGMENTS:
            if frag in hay:
                return s
    return None


def description_match(description: str) -> str | None:
    m = _DESC_RE.search(description or "") or _EXTRA_DESC_RE.search(description or "")
    return m.group(0).lower() if m else None


def assess(description: str, product_strings: list[str]) -> tuple[bool, dict]:
    """-> (is_ai_relevant, why). Accepts when a product field strongly matches
    an AI identifier, OR the description carries a strong (non-weak) AI
    phrase. *why* names the matching evidence, for the audit trail."""
    p = product_match(product_strings)
    d = description_match(description)
    if p or d:
        return True, {"product": p, "description": d}
    return False, {}
