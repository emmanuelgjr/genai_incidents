"""v2.13.0 item 9 guard: the OWASP ASI framework name, edition and citation.

The 2026 re-pin (D78-D80, D83-D85; evidence in
docs/audits/item9-owasp-asi-2026-source-check-2026-10-12.md, Correction 2)
renamed the framework on every live surface and moved the edition from "2025"
to "2026". Before this file, neither scripts/validate.py nor
scripts/check_stats_drift.py failed on a stale name, a stale edition literal
(except in data/stats.json), or a Threats-and-Mitigations URL cited for the
ASI codes: a rename with no guard is a check that cannot fail. Every rule
below is derived from mappings/owasp_asi_top10.json where it can be, so the
next re-pin moves the guard with it. Each rule has a planted-input test that
proves it fires.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAPPING = "mappings/owasp_asi_top10.json"
TM_URL = "https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/"

# Records and history, never rewritten (CLAUDE.md agreement 4: audits, dated
# plans), and bulk data. docs/incidents/ is render output of
# scripts/render_markdown.py (scanned at its source, and by
# test_dataset_description_and_pages_renamed below); data/ is build output
# except data/stats.json (scanned).
EXCLUDE_PREFIXES = (
    "legacy/", "docs/audits/", "docs/superpowers/plans/",
    "docs/incidents/", "docs/data/", "data/",
    "ingest/", "src/genai_incidents/data/incidents.min.json",
    "CHANGELOG.md", "PROGRESS.md", "tests/test_owasp_asi_naming.py",
)
INCLUDE_ANYWAY = ("data/stats.json",)

# The retired coinage, whitespace-tolerant so a line wrap cannot hide it.
RETIRED_NAME = re.compile(r"OWASP\s+Agentic\s+Top\s*10", re.I)
# Any other "OWASP Agentic ..." display-name variant (not the Agentic Security
# Initiative, which is the OWASP team's real name).
VARIANT = re.compile(r"OWASP\s+Agentic\b(?!\s+Security\s+Initiative)", re.I)
# Variants still awaiting their writer. D86 (2026-10-12) renamed every other
# held site; the schema pair is schema-architect's (sole writer of schema/)
# and is cleared in its own commit. Exact counts, so a new occurrence fails,
# and fixing one fails too until it is removed from this table.
PENDING_VARIANTS = {
    "schema/incident.schema.json": 2,
    "src/genai_incidents/schema/incident.schema.json": 2,
}
VERSION_LITERAL = re.compile(r"""["']?owasp_asi["']?\s*[:=]\s*["'](\d{4}(?:\.\d+)?)["']""")
EDITION_IN_NAME = re.compile(r"Agentic\s+Applications\W{0,3}(?:for\s+)?(20\d\d)", re.I)


def _mapping(root: Path) -> dict:
    return json.loads((root / MAPPING).read_text(encoding="utf-8"))


def _live_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    files = out.stdout.splitlines()
    return [f for f in files
            if f in INCLUDE_ANYWAY or not f.startswith(EXCLUDE_PREFIXES)]


def scan(root: Path, files: list[str]) -> list[str]:
    """Return one message per violation (empty list = clean)."""
    m = _mapping(root)
    version, framework = m["version"], m["framework"]
    problems: list[str] = []
    if m.get("url") == TM_URL:
        problems.append(f"{MAPPING}: `url` cites Threats and Mitigations, not the Top 10")
    variants: dict[str, int] = {}
    for rel in files:
        p = root / rel
        if not p.is_file():
            continue
        text = p.read_bytes().decode("utf-8", errors="ignore")
        for hit in RETIRED_NAME.finditer(text):
            problems.append(f"{rel}: retired name {hit.group(0)!r}")
        n = len(VARIANT.findall(text))
        if n:
            variants[rel] = n
        for hit in VERSION_LITERAL.finditer(text):
            if hit.group(1) != version:
                problems.append(f"{rel}: owasp_asi version literal {hit.group(1)!r} != pin {version!r}")
        for hit in EDITION_IN_NAME.finditer(text):
            if hit.group(1) != version:
                problems.append(f"{rel}: edition {hit.group(1)!r} in the framework title != pin {version!r}")
        if rel != MAPPING:
            for line in text.splitlines():
                if TM_URL in line and not re.search(r"Threats\s+(?:and|&|&amp;)\s+Mitigations", line, re.I):
                    problems.append(f"{rel}: T&M URL on a line that does not name Threats and Mitigations: {line.strip()[:120]!r}")
    for rel in sorted(set(variants) | (set(PENDING_VARIANTS) & set(files))):
        got, want = variants.get(rel, 0), PENDING_VARIANTS.get(rel, 0)
        if got != want:
            problems.append(f"{rel}: {got} 'OWASP Agentic ...' variant(s), expected {want} (PENDING_VARIANTS)")
    # D85: the headings that introduce the codes carry the pinned name + "(ASI)".
    for rel in ("INCIDENTS.md", "README.md", "docs/TAXONOMIES.md"):
        if rel in files and f"{framework} (ASI)" not in (root / rel).read_text(encoding="utf-8"):
            problems.append(f"{rel}: no heading '{framework} (ASI)' (D85)")
    return problems


def test_live_surfaces_clean():
    problems = scan(ROOT, _live_files(ROOT))
    assert problems == [], "\n".join(problems)


def test_dataset_description_and_pages_renamed():
    """The two build outputs the scan skips for size (D86)."""
    raw = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    desc = raw["description"]
    assert not VARIANT.search(desc), desc
    assert _mapping(ROOT)["framework"] in desc
    for p in sorted((ROOT / "docs" / "incidents").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        assert not VARIANT.search(text), p.name


def test_mapping_pin_is_the_2026_top10():
    m = _mapping(ROOT)
    assert m["framework"] == "OWASP Top 10 for Agentic Applications"
    assert m["version"] == "2026"
    assert m["url"] == "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"
    assert m["related"]["url"] == TM_URL
    assert m["citation"]["title"] == "OWASP Top 10 For Agentic Applications 2026"
    assert m["citation"]["edition"] == "Version 2026 / December 2025"


# ------------------------------------------------- the guard can fail ----

def _scratch(tmp_path: Path) -> Path:
    (tmp_path / "mappings").mkdir()
    (tmp_path / MAPPING).write_text((ROOT / MAPPING).read_text(encoding="utf-8"), encoding="utf-8")
    for rel in ("INCIDENTS.md", "README.md", "docs/TAXONOMIES.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("### OWASP Top 10 for Agentic Applications (ASI)\n", encoding="utf-8")
    return tmp_path


BASE = [MAPPING, "INCIDENTS.md", "README.md", "docs/TAXONOMIES.md"]


@pytest.mark.parametrize("planted, expect", [
    ("mapped to OWASP Agentic Top 10 (ASI)", "retired name"),
    ("mapped to OWASP\n  Agentic Top 10, NIST", "retired name"),          # line-wrapped
    ("OWASP Agentic ASI Top 10", "variant"),
    ('{"owasp_asi": "2025"}', "version literal"),
    ("'owasp_asi': '2025'", "version literal"),
    ('"OWASP Top 10 For Agentic Applications 2025"', "edition"),
    ("OWASP Top 10 for Agentic Applications for 2025", "edition"),
    (f'<a href="{TM_URL}">OWASP Top 10 for Agentic Applications</a>', "T&M URL"),
])
def test_guard_fires_on_planted_input(tmp_path, planted, expect):
    root = _scratch(tmp_path)
    assert scan(root, BASE) == []                                  # control: clean
    (root / "docs" / "planted.md").write_text(planted, encoding="utf-8")
    problems = scan(root, BASE + ["docs/planted.md"])
    assert any(expect in p for p in problems), problems


def test_guard_allows_a_correct_tm_citation(tmp_path):
    root = _scratch(tmp_path)
    (root / "docs" / "ok.md").write_text(
        f'OWASP "Agentic AI - Threats and Mitigations" v1.1: <{TM_URL}>', encoding="utf-8")
    assert scan(root, BASE + ["docs/ok.md"]) == []


def test_guard_fires_on_mapping_url_and_missing_heading(tmp_path):
    root = _scratch(tmp_path)
    m = _mapping(root)
    m["url"] = TM_URL
    (root / MAPPING).write_text(json.dumps(m), encoding="utf-8")
    (root / "README.md").write_text("### OWASP Agentic (ASI)\n", encoding="utf-8")
    problems = scan(root, BASE)
    assert any("cites Threats and Mitigations" in p for p in problems), problems
    assert any("README.md: no heading" in p for p in problems), problems
