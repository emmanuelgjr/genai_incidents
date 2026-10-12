"""v2.13.0 item 9 guard: the OWASP ASI framework name, edition and citation.

The 2026 re-pin (D78-D80, D83-D88; evidence in
docs/audits/item9-owasp-asi-2026-source-check-2026-10-12.md, Correction 2)
renamed the framework on every live surface and moved the edition from "2025"
to "2026". Before this file, neither scripts/validate.py nor
scripts/check_stats_drift.py failed on a stale name, a stale edition literal
(except in data/stats.json), or a Threats-and-Mitigations URL cited for the
ASI codes: a rename with no guard is a check that cannot fail. Every rule
below is derived from mappings/owasp_asi_top10.json where it can be, so the
next re-pin moves the guard with it. Each rule has a planted-input test that
proves it fires.

Known limits (each would need a parser, not a pattern, to close):
- The D88 rule reads one line at a time, so a label whose name is split over
  two lines or two SVG <text> elements is checked only where the full name
  sits on one line. The one known split label, the README taxonomy-map card,
  has its own check (test_taxonomy_map_asi_card_carries_asi_label).
- A bare T&M URL is attributed to the text just before it on its line, back
  to the nearest framework name, ASI code or other URL; a sentence that names
  Threats and Mitigations and then cites its URL for the ASI codes without
  naming either again passes.
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

# What may sit between the words of a name and still read as one name:
# whitespace (including a no-break space), &nbsp;, <br>, and hyphens.
_HYPHENS = "-" + chr(0x2010) + chr(0x2011)
_APOSTROPHES = "'" + chr(0x2019)
# The pinned name itself (D88) is matched over spacing only, not hyphens, so a
# URL slug of it is not read as the name.
_SPACE = r"(?:\s|&nbsp;|&#160;|&#xa0;|<br\s*/?>)+"
SEP = rf"(?:\s|&nbsp;|&#160;|&#xa0;|<br\s*/?>|[{_HYPHENS}])+"
_POSS = rf"(?:[{_APOSTROPHES}]s)?"
# The retired coinage, with or without "OWASP" ("OWASP's" too), however the
# words are separated, so a line wrap or markup cannot hide it.
RETIRED_NAME = re.compile(rf"(?:OWASP{_POSS}{SEP})?Agentic{SEP}Top{SEP}?10\b", re.I)
# Any other "OWASP Agentic ..." display-name variant (not the Agentic Security
# Initiative, which is the OWASP team's real name).
VARIANT = re.compile(rf"OWASP{_POSS}{SEP}Agentic\b(?!{SEP}Security{SEP}Initiative)", re.I)
# "ASI Top 10", "LLM/ASI Top 10" (D87): shorthand for a title OWASP never used.
SHORTHAND = re.compile(rf"\bASI{SEP}Top{SEP}?10\b", re.I)
# D90: the bare "OWASP LLM/ASI" used as a name for the two frameworks (the
# "... Top 10" form is SHORTHAND's). D90 keeps the short label "OWASP ASI"
# next to the codes (app.js, the filter, the INCIDENTS.md column header, an
# image alt, TAXONOMIES), so only the slash pair is matched.
_SLASH = r"(?:\s|&nbsp;|&#160;|&#xa0;)*/(?:\s|&nbsp;|&#160;|&#xa0;)*"
BARE_LLM_ASI = re.compile(rf"\bOWASP{_POSS}{SEP}LLM{_SLASH}ASI\b(?!{SEP}Top{SEP}?10\b)", re.I)
# Sent correspondence quotes what the recipient was told (each file says "do
# not edit the message body"), so D90 does not apply there.
D90_EXEMPT = ("docs/outreach/",)
# The correction log may quote the retired name as a former name (ruling
# 2026-10-12 on the item 9 row); see _quoted_former_names.
CORRECTIONS = "CORRECTIONS.md"
QUOTE_PAIRS = ('""', "''", chr(0x201C) + chr(0x201D), chr(0x2018) + chr(0x2019))
# Variants still awaiting their writer. D86 (2026-10-12) renamed every held
# site, the schema pair (schema-architect, sole writer of schema/) last, so
# the table is empty and any live variant fails. Exact counts: should a site
# ever be held again, a new occurrence fails, and fixing one fails too until
# it is removed from this table.
PENDING_VARIANTS: dict[str, int] = {}
# `owasp_asi` (JSON, Python) and `owasp-asi` (the MISP taxonomy-owasp-asi tag).
VERSION_LITERAL = re.compile(r"""["']?owasp[_-]asi["']?\s*[:=]\s*["'](\d{4}(?:\.\d+)?)["']""", re.I)
# Prose: "owasp_asi 2025", "OWASP ASI (2025)". Not inside a path or slug
# (item9-owasp-asi-2026-source-check), which names a record, not the pin.
PROSE_EDITION = re.compile(rf"(?<![\w/-])(?:owasp[_-]asi|OWASP{SEP}ASI)\W{{0,3}}(20\d\d)(?![\w-])", re.I)
EDITION_IN_NAME = re.compile(r"Agentic\s+Applications\W{0,3}(?:for\s+)?(20\d\d)", re.I)
TM_NAME = re.compile(r"Threats\s+(?:and|&|&amp;)\s+Mitigations", re.I)
ASI_CODE = re.compile(r"\bASI(?:0[1-9]|10)\b")
# D88: "(ASI)" follows the name on every label that introduces or labels the
# codes. A label is: a run of text that also carries an ASI code (a line, or on
# a markup line the text node or tag it sits in), a Markdown table cell that is
# the name, the text of one of these elements, or a Markdown heading whose
# section carries an ASI code. Prose lists of the frameworks are not labels.
LABEL_TAGS = "figcaption|text|tspan|th|td|label|option|caption|legend|summary|dt|h[1-6]"
HEADING = re.compile(r"#{1,6}\s")
FOLLOWED_BY_ASI = re.compile(r"(?:\*\*|</(?:strong|b|a)>)?\s*\(ASI\)")


def _mapping(root: Path) -> dict:
    return json.loads((root / MAPPING).read_text(encoding="utf-8"))


def _live_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    files = out.stdout.splitlines()
    return [f for f in files
            if f in INCLUDE_ANYWAY or not f.startswith(EXCLUDE_PREFIXES)]


def _name_re(framework: str) -> re.Pattern:
    """The pinned name, any spacing; not the dated citation title, not a URL slug."""
    words = _SPACE.join(re.escape(w) for w in framework.split())
    return re.compile(r"(?<![\w/-])" + words + r"(?!\W{0,3}(?:for\s+)?20\d\d)", re.I)


def _segment(line: str, start: int, end: int) -> str:
    """The text node or tag an occurrence sits in (the whole line if no markup)."""
    lo = max(line.rfind("<", 0, start), line.rfind(">", 0, start)) + 1
    ends = [i for i in (line.find("<", end), line.find(">", end)) if i >= 0]
    return line[lo:min(ends, default=len(line))]


def _missing_asi_labels(rel: str, text: str, name: re.Pattern) -> list[str]:
    lines = text.splitlines()
    headings = [i for i, line in enumerate(lines) if HEADING.match(line)]
    out = []
    for i, line in enumerate(lines):
        for hit in name.finditer(line):
            if FOLLOWED_BY_ASI.match(line, hit.end()):
                continue
            why = ""
            if ASI_CODE.search(_segment(line, hit.start(), hit.end())):
                why = "an ASI code in the same text"
            elif re.search(r"\|\s*(?:\*\*)?$", line[:hit.start()]) and re.match(r"(?:\*\*)?\s*\|", line[hit.end():]):
                why = "a table cell"
            elif re.search(rf"<(?:{LABEL_TAGS})\b[^>]*>[^<]*$", line[:hit.start()], re.I):
                why = "a label element"
            elif HEADING.match(line):
                end = next((j for j in headings if j > i), len(lines))
                if any(ASI_CODE.search(x) for x in lines[i + 1:end]):
                    why = "a heading over the codes"
            if why:
                out.append(f"{rel}:{i + 1}: D88 '(ASI)' missing after the name ({why}): {line.strip()[:120]!r}")
    return out


def _quoted_former_names(rel: str, text: str) -> set[tuple[int, int]]:
    """Spans of the retired name quoted as a former name in CORRECTIONS.md.

    A correction row records what was corrected away, so there (only) the
    retired name may appear inside quotation marks. Unquoted, it still fails.
    """
    if rel != CORRECTIONS:
        return set()
    return {hit.span() for hit in RETIRED_NAME.finditer(text)
            if hit.start() > 0 and hit.end() < len(text)
            and text[hit.start() - 1] + text[hit.end()] in QUOTE_PAIRS}


def _tm_label(line: str, start: int, end: int, name: re.Pattern) -> str:
    """The text a T&M URL occurrence is cited for."""
    before = line[:start]
    if re.search(r"<a\b[^>]*$", before, re.I):                    # <a href="URL">label</a>
        m = re.match(r"[^>]*>(.*?)</a>", line[end:], re.I)
        return m.group(1) if m else ""
    m = re.search(r"\[([^\]]*)\]\(<?$", before)                    # [label](URL)
    if m:
        return m.group(1)
    cut = max((h.end() for h in (*name.finditer(before), *ASI_CODE.finditer(before),
                                 *re.finditer(r"https?://\S+", before))), default=0)
    return before[cut:]                                           # bare: the text just before it


def scan(root: Path, files: list[str]) -> list[str]:
    """Return one message per violation (empty list = clean)."""
    m = _mapping(root)
    version, framework = m["version"], m["framework"]
    name = _name_re(framework)
    problems: list[str] = []
    if m.get("url") == TM_URL:
        problems.append(f"{MAPPING}: `url` cites Threats and Mitigations, not the Top 10")
    variants: dict[str, int] = {}
    for rel in files:
        p = root / rel
        if not p.is_file():
            continue
        text = p.read_bytes().decode("utf-8", errors="ignore")
        quoted = _quoted_former_names(rel, text)
        for hit in RETIRED_NAME.finditer(text):
            if hit.span() not in quoted:
                problems.append(f"{rel}: retired name {hit.group(0)!r}")
        for hit in SHORTHAND.finditer(text):
            problems.append(f"{rel}: shorthand {hit.group(0)!r} (D87: use the official names)")
        if not rel.startswith(D90_EXEMPT):
            for hit in BARE_LLM_ASI.finditer(text):
                problems.append(f"{rel}: bare {hit.group(0)!r} (D90: use the official names)")
        n = sum(not any(a <= hit.start() < b for a, b in quoted) for hit in VARIANT.finditer(text))
        if n:
            variants[rel] = n
        for hit in VERSION_LITERAL.finditer(text):
            if hit.group(1) != version:
                problems.append(f"{rel}: owasp_asi version literal {hit.group(1)!r} != pin {version!r}")
        for hit in PROSE_EDITION.finditer(text):
            if hit.group(1) != version:
                problems.append(f"{rel}: prose edition {hit.group(0)!r} != pin {version!r}")
        for hit in EDITION_IN_NAME.finditer(text):
            if hit.group(1) != version:
                problems.append(f"{rel}: edition {hit.group(1)!r} in the framework title != pin {version!r}")
        if rel != MAPPING:
            problems += _missing_asi_labels(rel, text, name)
            for line in text.splitlines():
                for hit in re.finditer(re.escape(TM_URL), line):
                    if not TM_NAME.search(_tm_label(line, hit.start(), hit.end(), name)):
                        problems.append(f"{rel}: T&M URL cited for something other than Threats and Mitigations: {line.strip()[:120]!r}")
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


TAX_PY = "scripts/readme_assets/tax.py"
TAX_SVGS = ("docs/assets/readme/taxonomy-map-dark.svg", "docs/assets/readme/taxonomy-map-light.svg")
# A card title: tax.py wraps it over consecutive 15 px bold <text> lines, 19 px apart.
CARD_TITLE_LINE = re.compile(r'<text x="([\d.]+)" y="([\d.]+)" font-size="15" font-weight="700"[^>]*>([^<]*)</text>')


def _tax_labels(source: str) -> list[str]:
    """The card titles in tax.py's `T` tuple list (read, not run: tax.py writes files)."""
    import ast
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "T" for t in node.targets):
            return [elt.elts[0].value for elt in node.value.elts]
    return []


def _svg_card_titles(svg: str) -> list[str]:
    """Each card's title, its wrapped <text> lines joined with a space."""
    titles: list[tuple[str, float, str]] = []
    for x, y, words in CARD_TITLE_LINE.findall(svg):
        if titles and titles[-1][0] == x and float(y) - titles[-1][1] == 19:
            titles[-1] = (x, float(y), titles[-1][2] + " " + words)
        else:
            titles.append((x, float(y), words))
    return [t[2] for t in titles]


def _asi_card_problems(labels: list[str], where: str, framework: str) -> list[str]:
    cards = [label for label in labels if framework in label]
    if len(cards) != 1:
        return [f"{where}: {len(cards)} card(s) titled {framework!r}, expected 1: {labels}"]
    if f"{framework} (ASI)" not in cards[0]:
        return [f"{where}: ASI card title {cards[0]!r} lacks '(ASI)' (D88)"]
    return []


def test_taxonomy_map_asi_card_carries_asi_label():
    """Item 9 re-gate A1: the card title is split over two <text> elements, which
    the line-based D88 rule cannot see, so the source tuple and both generated
    SVGs are checked on the joined title."""
    framework = _mapping(ROOT)["framework"]
    problems = _asi_card_problems(_tax_labels((ROOT / TAX_PY).read_text(encoding="utf-8")), TAX_PY, framework)
    for rel in TAX_SVGS:
        problems += _asi_card_problems(_svg_card_titles((ROOT / rel).read_text(encoding="utf-8")), rel, framework)
    assert problems == [], "\n".join(problems)


def test_taxonomy_map_check_fires():
    framework = "OWASP Top 10 for Agentic Applications"
    source = (ROOT / TAX_PY).read_text(encoding="utf-8")
    assert _asi_card_problems(_tax_labels(source), "tax", framework) == []
    planted = source.replace(f"'{framework} (ASI)'", f"'{framework}'")
    assert planted != source
    assert "lacks '(ASI)'" in _asi_card_problems(_tax_labels(planted), "tax", framework)[0]
    svg = ('<text x="58" y="280" font-size="15" font-weight="700" fill="#000">OWASP Top 10 for Agentic</text>'
           '<text x="58" y="299" font-size="15" font-weight="700" fill="#000">Applications</text>')
    assert "lacks '(ASI)'" in _asi_card_problems(_svg_card_titles(svg), "svg", framework)[0]
    assert _asi_card_problems(_svg_card_titles(svg.replace("Applications<", "Applications (ASI)<")), "svg", framework) == []


# ------------------------------------------------- the guard can fail ----

def _scratch(tmp_path: Path) -> Path:
    (tmp_path / "mappings").mkdir()
    (tmp_path / MAPPING).write_text((ROOT / MAPPING).read_text(encoding="utf-8"), encoding="utf-8")
    for rel in ("INCIDENTS.md", "README.md", "docs/TAXONOMIES.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("### OWASP Top 10 for Agentic Applications (ASI)\n", encoding="utf-8")
    return tmp_path


BASE = [MAPPING, "INCIDENTS.md", "README.md", "docs/TAXONOMIES.md"]
NBSP = chr(0xA0)


@pytest.mark.parametrize("planted, expect", [
    ("mapped to OWASP Agentic Top 10 (ASI)", "retired name"),
    ("mapped to OWASP\n  Agentic Top 10, NIST", "retired name"),          # line-wrapped
    ("OWASP's Agentic Top-10", "retired name"),                            # A3
    ("OWASP" + chr(0x2019) + "s Agentic Top 10", "retired name"),
    ("OWASP&nbsp;Agentic&nbsp;Top&nbsp;10", "retired name"),
    (f"OWASP{NBSP}Agentic{NBSP}Top{NBSP}10", "retired name"),
    ("OWASP<br>Agentic Top 10", "retired name"),
    ("the Agentic Top 10", "retired name"),
    ("OWASP Agentic ASI Top 10", "variant"),
    ("OWASP LLM/ASI Top 10", "shorthand"),                                 # D87
    ("the Agentic ASI Top 10", "shorthand"),
    ("all entries mapped to OWASP LLM/ASI", "D90"),                        # D90
    ("(OWASP LLM/ASI, NIST AI RMF, MITRE ATLAS)", "D90"),
    ("OWASP LLM / ASI codes", "D90"),
    ("owasp llm/asi", "D90"),
    ("OWASP's LLM/ASI mappings", "D90"),
    ("OWASP&nbsp;LLM/ASI", "D90"),
    ("frameworks (OWASP\n  LLM/ASI, NIST AI RMF)", "D90"),                 # line-wrapped
    ('description="Incidents mapped to OWASP LLM/ASI."', "D90"),           # served text
    ('{"owasp_asi": "2025"}', "version literal"),
    ("'owasp_asi': '2025'", "version literal"),
    ('genai-incidents:taxonomy-owasp-asi="2025"', "version literal"),      # MISP tag
    ("taxonomy_versions pins owasp_asi 2025", "prose edition"),
    ("the OWASP ASI (2025) list", "prose edition"),
    ('"OWASP Top 10 For Agentic Applications 2025"', "edition"),
    ("OWASP Top 10 for Agentic Applications for 2025", "edition"),
    (f'<a href="{TM_URL}">OWASP Top 10 for Agentic Applications</a>', "T&M URL"),
    (f'<a href="{TM_URL}">OWASP Top 10 for Agentic Applications</a>, see Threats and Mitigations', "T&M URL"),
    (f"[the ASI codes]({TM_URL}), unlike Threats and Mitigations", "T&M URL"),
    (f"Unlike Threats and Mitigations, the codes ASI01-ASI10 come from <{TM_URL}>", "T&M URL"),
    ("<figcaption>OWASP Top 10 for Agentic Applications</figcaption>", "D88"),         # D88
    ('<text x="12" y="18">OWASP Top 10 for Agentic Applications — incident coverage</text>', "D88"),
    ("<th>OWASP Top 10 for Agentic Applications</th>", "D88"),
    ("- `owasp_asi`: OWASP Top 10 for Agentic Applications — `ASI01`–`ASI10`", "D88"),
    ("| agent layer? | **OWASP Top 10 for Agentic Applications** |", "D88"),
    ("## OWASP Top 10 for Agentic Applications\n\nThe codes ASI01-ASI10.\n", "D88"),
    ("OWASP Top 10 for Agentic Applications. The risk codes ASI01-ASI10", "D88"),
])
def test_guard_fires_on_planted_input(tmp_path, planted, expect):
    root = _scratch(tmp_path)
    assert scan(root, BASE) == []                                  # control: clean
    (root / "docs" / "planted.md").write_text(planted, encoding="utf-8")
    problems = scan(root, BASE + ["docs/planted.md"])
    assert any(expect in p for p in problems), problems


@pytest.mark.parametrize("legit", [
    f'OWASP "Agentic AI - Threats and Mitigations" v1.1: <{TM_URL}>',
    f"[Agentic AI - Threats and Mitigations]({TM_URL}) is separate from ASI01-ASI10",
    f'<a href="{TM_URL}">Agentic AI &amp; Threats and Mitigations</a>',
    "mapped to the OWASP Top 10 for Agentic Applications, NIST AI RMF and MITRE ATLAS",
    '"OWASP Top 10 For Agentic Applications 2026" (Version 2026 / December 2025); codes ASI01-ASI10',
    "the OWASP Agentic Security Initiative",
    "see docs/audits/item9-owasp-asi-2025-source-check-2026-10-12.md",
    "## OWASP Top 10 for Agentic Applications\n\nNo codes in this section.\n## Next\n\nASI01\n",
    "<figcaption>OWASP Top 10 for Agentic Applications (ASI)</figcaption>",
    "| **OWASP Top 10 for Agentic Applications (ASI)** | `ASI01`–`ASI10` | core |",
    "- `owasp_asi`: OWASP Top 10 for Agentic Applications (ASI) — `ASI01`–`ASI10`",
    "the OWASP Top 10 for LLM Applications and the OWASP Top 10 for Agentic Applications",
    "OWASP ASI",                                                           # D90 keeps the UI label
    '<label for="f-asi">OWASP ASI</label>',
    "| Date | ID | Title | Severity | OWASP LLM | OWASP ASI | CVE |",
    "OWASP LLM and ASI codes",
    "the LLM/ASI/CVE columns",
    "dynamically-populated selects (year/llm/asi/vector)",
])
def test_guard_allows_legitimate_text(tmp_path, legit):
    root = _scratch(tmp_path)
    (root / "docs" / "ok.md").write_text(legit, encoding="utf-8")
    assert scan(root, BASE + ["docs/ok.md"]) == []


@pytest.mark.parametrize("rel, planted, clean", [
    (CORRECTIONS, 'The display name "OWASP Agentic Top 10" was unofficial.', True),
    (CORRECTIONS, "The display name " + chr(0x201C) + "OWASP Agentic Top 10" + chr(0x201D) + " was unofficial.", True),
    (CORRECTIONS, "The display name OWASP Agentic Top 10 was unofficial.", False),       # unquoted
    (CORRECTIONS, 'Corrected the "OWASP Agentic Top 10 mapping".', False),               # not the whole quote
    (CORRECTIONS, 'Corrected the "OWASP Agentic Applications" mapping.', False),         # a variant, not the retired name
    ("docs/planted.md", 'The display name "OWASP Agentic Top 10" was unofficial.', False),  # CORRECTIONS only
])
def test_corrections_may_quote_the_retired_name(tmp_path, rel, planted, clean):
    root = _scratch(tmp_path)
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(planted, encoding="utf-8")
    problems = scan(root, BASE + [rel])
    assert (problems == []) is clean, problems


def test_d90_exempts_sent_correspondence_only(tmp_path):
    root = _scratch(tmp_path)
    for rel in ("docs/outreach/sent.md", "docs/live.md"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("frameworks (OWASP LLM/ASI, NIST AI RMF)", encoding="utf-8")
    problems = scan(root, BASE + ["docs/outreach/sent.md", "docs/live.md"])
    assert [p.split(":")[0] for p in problems] == ["docs/live.md"], problems


def test_guard_fires_on_mapping_url_and_missing_heading(tmp_path):
    root = _scratch(tmp_path)
    m = _mapping(root)
    m["url"] = TM_URL
    (root / MAPPING).write_text(json.dumps(m), encoding="utf-8")
    (root / "README.md").write_text("### OWASP Agentic (ASI)\n", encoding="utf-8")
    problems = scan(root, BASE)
    assert any("cites Threats and Mitigations" in p for p in problems), problems
    assert any("README.md: no heading" in p for p in problems), problems
