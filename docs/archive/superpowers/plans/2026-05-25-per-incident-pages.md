# Per-Incident Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a standalone `/incident/INC-XXXXX.html` page for every incident so each has a stable, citable, SEO-indexable URL.

**Architecture:** Extend `scripts/render_markdown.py` to emit one Jekyll-ready markdown file per incident under `docs/incident/`. A new `_layouts/incident.html` layout provides the HTML shell with canonical URLs, Open Graph meta, and JSON-LD Schema.org markup. The main app's JS links are updated to point to per-incident pages instead of year-shard hash anchors.

**Tech Stack:** Python 3.12, Jekyll (GitHub Pages), vanilla JS, JSON-LD

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Modify | `scripts/render_markdown.py` | Extract shared incident renderer; add per-incident page generation |
| Create | `docs/_layouts/incident.html` | Layout for single-incident pages |
| Modify | `docs/app.js` | Update links from year-shard anchors to `/incident/INC-XXXXX.html` |
| Modify | `docs/style.css` | Add breadcrumb styles for incident pages |
| Modify | `.gitattributes` | Mark `docs/incident/*.md` as linguist-generated |
| Modify | `.github/workflows/validate.yml` | Add `docs/incident` to drift-check paths |
| Create | `tests/test_per_incident_pages.py` | Tests for the new rendering function |

---

### Task 1: Extract shared incident rendering helper

**Files:**
- Modify: `scripts/render_markdown.py:265-372`
- Test: `tests/test_render_markdown.py`

- [ ] **Step 1: Write the failing test for the extracted helper**

Add to `tests/test_render_markdown.py`:

```python
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
    assert "https://example.com" in body


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_render_markdown.py::test_render_incident_block_produces_card tests/test_render_markdown.py::test_render_incident_block_handles_minimal_entry -v`
Expected: FAIL with `AttributeError: module 'render_markdown' has no attribute 'render_incident_block'`

- [ ] **Step 3: Extract `render_incident_block` from `render_details_shard`**

In `scripts/render_markdown.py`, extract the inner loop body of `render_details_shard` (lines 284-366) into a new function. The new function returns a `list[str]` of markdown lines for a single incident. `render_details_shard` calls it in its loop.

```python
def render_incident_block(e: dict) -> list[str]:
    """Render a single incident as a markdown card block.

    Returns a list of markdown lines (without trailing newline join).
    Used by both year-shard generation and per-incident page generation.
    """
    lines: list[str] = []
    slug = e["id"].lower()
    lines.append(f'<div class="incident-anchor" id="{slug}" markdown="1">')
    lines.append("")
    lines.append(f"### {e['id']}")
    lines.append("")
    lines.append(f"**{e['title']}**  ")
    meta_bits = [
        e.get("date", ""),
        e.get("category", ""),
        f"Severity: {e.get('severity', '')}",
    ]
    lines.append("_" + " · ".join(b for b in meta_bits if b) + "_")
    if e.get("cve_ids"):
        lines.append("")
        lines.append("CVEs: " + ", ".join(f"`{c}`" for c in e["cve_ids"]))
    if e.get("cwe_ids"):
        lines.append("CWEs: " + ", ".join(f"`{c}`" for c in e["cwe_ids"]))
    if e.get("cvss_score") is not None:
        cvss_line = f"CVSS: **{e['cvss_score']}**"
        if e.get("cvss_vector"):
            cvss_line += f" — `{e['cvss_vector']}`"
        lines.append(cvss_line)
    if e.get("aiid_id"):
        lines.append(
            f"AIID: [`#{e['aiid_id']}`]"
            f"(https://incidentdatabase.ai/cite/{e['aiid_id']}/)"
        )
    if e.get("disclosure_date") and e["disclosure_date"] != e.get("date"):
        lines.append(f"Disclosed: {e['disclosure_date']}")
    lines.append("")
    lines.append(e.get("description", ""))
    lines.append("")
    if e.get("affected"):
        lines.append(f"**Affected:** {e['affected']}  ")
    if e.get("attack_vector"):
        lines.append(f"**Attack vector:** `{e['attack_vector']}`  ")
    if e.get("impact"):
        lines.append(f"**Impact:** {e['impact']}  ")
    lines.append("")
    if e.get("owasp_llm"):
        lines.append(
            f"**OWASP LLM Top 10:** {', '.join(f'`{c}`' for c in e['owasp_llm'])}  "
        )
    if e.get("owasp_asi"):
        lines.append(
            f"**OWASP Agentic (ASI):** {', '.join(f'`{c}`' for c in e['owasp_asi'])}  "
        )
    if e.get("nist_ai_rmf"):
        lines.append(
            f"**NIST AI RMF:** {', '.join(f'`{c}`' for c in e['nist_ai_rmf'])}  "
        )
    if e.get("mitre_atlas"):
        lines.append(
            f"**MITRE ATLAS:** {', '.join(f'`{c}`' for c in e['mitre_atlas'])}  "
        )
    if e.get("maestro_layers"):
        ml = ", ".join(
            f"`{l['layer']} {l.get('label', '')}`" for l in e["maestro_layers"]
        )
        lines.append(f"**MAESTRO layers:** {ml}  ")
    lines.append("")
    if e.get("mitigations"):
        lines.append("**Mitigations:**")
        for m in e["mitigations"]:
            lines.append(f"- {m}")
        lines.append("")
    if e.get("references"):
        lines.append("**References:**")
        for ref in e["references"]:
            title = ref.get("title") or ref["url"]
            suffix = f" _({ref.get('type')})_" if ref.get("type") else ""
            lines.append(f"- [{title}]({ref['url']}){suffix}")
        lines.append("")
    if e.get("tags"):
        lines.append("**Tags:** " + ", ".join(f"`{t}`" for t in e["tags"]))
        lines.append("")
    lines.append("</div>")
    return lines
```

Then update `render_details_shard` to use it:

```python
def render_details_shard(year: int, rows: list[dict]) -> str:
    rows = sorted(rows, key=sort_key)
    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: \"Incident Details — {year}\"")
    lines.append("layout: incident-shard")
    lines.append(f"permalink: /incidents/{year}.html")
    lines.append("---")
    lines.append("")
    lines.append(f"_{len(rows):,} incidents in this year shard._  ")
    lines.append(
        "Use the [searchable web view](../index.html) for filtering across "
        "all years. The raw markdown lives under "
        "[`docs/incidents/`](https://github.com/emmanuelgjr/genai_agentic_incidents/tree/main/docs/incidents)."
    )
    lines.append("")
    for e in rows:
        lines.extend(render_incident_block(e))
        lines.append("")
    lines.append("")
    lines.append(
        f"> Back to [`INCIDENTS.md`](../../INCIDENTS.md). "
        f"Generated by `scripts/render_markdown.py`."
    )
    return "\n".join(lines)
```

- [ ] **Step 4: Run all tests to verify nothing broke**

Run: `pytest tests/test_render_markdown.py -v`
Expected: All tests PASS (existing tests still pass + new tests pass)

- [ ] **Step 5: Commit**

```bash
git add scripts/render_markdown.py tests/test_render_markdown.py
git commit -m "refactor: extract render_incident_block helper for reuse"
```

---

### Task 2: Add per-incident page generation to render_markdown.py

**Files:**
- Modify: `scripts/render_markdown.py`
- Create: `tests/test_per_incident_pages.py`

- [ ] **Step 1: Write the failing test for per-incident page rendering**

Create `tests/test_per_incident_pages.py`:

```python
"""Tests for per-incident page generation."""

from __future__ import annotations

import render_markdown as r


def test_render_incident_page_front_matter():
    """Per-incident page must have correct Jekyll front matter."""
    entry = {
        "id": "INC-04853",
        "title": "Samsung employees leak source code",
        "date": "2023-04",
        "year": 2023,
        "category": "real-world",
        "severity": "High",
        "description": "Samsung employees leaked proprietary code.",
        "tags": ["insider", "data-leak"],
    }
    body = r.render_incident_page(entry)
    assert "layout: incident" in body
    assert "permalink: /incident/INC-04853.html" in body
    assert "incident_id: INC-04853" in body
    assert "year: 2023" in body
    assert "severity: High" in body


def test_render_incident_page_contains_content():
    """Per-incident page must contain the incident content block."""
    entry = {
        "id": "INC-00042",
        "title": "Test incident for page gen",
        "date": "2025-06-01",
        "year": 2025,
        "category": "real-world",
        "severity": "Medium",
        "description": "Description here.",
        "owasp_llm": ["LLM01", "LLM02"],
        "references": [{"title": "Ref", "url": "https://example.com"}],
    }
    body = r.render_incident_page(entry)
    assert "### INC-00042" in body
    assert "Test incident for page gen" in body
    assert "LLM01" in body
    assert "https://example.com" in body


def test_render_incident_page_escapes_title_in_front_matter():
    """Titles with quotes must be safely escaped in YAML front matter."""
    entry = {
        "id": "INC-00099",
        "title": 'Incident with "quotes" and colons: here',
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "Low",
        "description": "Test.",
    }
    body = r.render_incident_page(entry)
    assert "---" in body
    assert "INC-00099" in body
    # Title line should not break YAML — must be quoted
    lines = body.split("\n")
    title_line = [l for l in lines if l.startswith("title:")][0]
    assert '"' in title_line or "'" in title_line


def test_generate_incident_pages_writes_files(tmp_path):
    """generate_incident_pages should write one .md file per incident."""
    entries = [
        {
            "id": "INC-00001",
            "title": "First",
            "date": "2025-01-01",
            "year": 2025,
            "category": "real-world",
            "severity": "High",
            "description": "Desc 1.",
        },
        {
            "id": "INC-00002",
            "title": "Second",
            "date": "2025-02-01",
            "year": 2025,
            "category": "real-world",
            "severity": "Medium",
            "description": "Desc 2.",
        },
    ]
    r.generate_incident_pages(entries, tmp_path)
    assert (tmp_path / "INC-00001.md").exists()
    assert (tmp_path / "INC-00002.md").exists()
    content = (tmp_path / "INC-00001.md").read_text(encoding="utf-8")
    assert "permalink: /incident/INC-00001.html" in content


def test_generate_incident_pages_cleans_stale_files(tmp_path):
    """Stale .md files from previous runs should be removed."""
    stale = tmp_path / "INC-99999.md"
    stale.write_text("stale content", encoding="utf-8")
    entries = [
        {
            "id": "INC-00001",
            "title": "Only",
            "date": "2025",
            "year": 2025,
            "category": "real-world",
            "severity": "Low",
            "description": "Desc.",
        },
    ]
    r.generate_incident_pages(entries, tmp_path)
    assert not stale.exists()
    assert (tmp_path / "INC-00001.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_per_incident_pages.py -v`
Expected: FAIL with `AttributeError: module 'render_markdown' has no attribute 'render_incident_page'`

- [ ] **Step 3: Implement `render_incident_page` and `generate_incident_pages`**

Add to `scripts/render_markdown.py` after `render_incident_block`:

```python
INCIDENT_PAGE_DIR = ROOT / "docs" / "incident"


def _yaml_escape(s: str) -> str:
    """Escape a string for safe use as a YAML scalar value."""
    if not s:
        return '""'
    if any(c in s for c in ':{}[]&*?|->!%@`,"\'#'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def render_incident_page(e: dict) -> str:
    """Render a full per-incident markdown page with Jekyll front matter."""
    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: {_yaml_escape(e['id'] + ' — ' + e['title'])}")
    lines.append("layout: incident")
    lines.append(f"permalink: /incident/{e['id']}.html")
    lines.append(f"incident_id: {e['id']}")
    lines.append(f"year: {e.get('year', '')}")
    lines.append(f"severity: {e.get('severity', '')}")
    desc_preview = (e.get("description") or "")[:200].replace("\n", " ").strip()
    lines.append(f"description_preview: {_yaml_escape(desc_preview)}")
    tags_str = ", ".join(e.get("tags", []))
    lines.append(f"tags_str: {_yaml_escape(tags_str)}")
    lines.append("---")
    lines.append("")
    lines.extend(render_incident_block(e))
    lines.append("")
    return "\n".join(lines)


def generate_incident_pages(entries: list[dict], out_dir: Path | None = None) -> None:
    """Write one markdown file per incident under docs/incident/."""
    out_dir = out_dir or INCIDENT_PAGE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    expected: set[str] = set()
    for e in entries:
        filename = f"{e['id']}.md"
        expected.add(filename)
        body = render_incident_page(e)
        _write_lf(out_dir / filename, body)
    for existing in out_dir.glob("*.md"):
        if existing.name not in expected:
            existing.unlink()
    print(f"wrote {len(entries)} per-incident pages under {out_dir}/")
```

- [ ] **Step 4: Wire `generate_incident_pages` into the `render()` function**

In the `render()` function, after the per-year shard generation block (after line ~596), add:

```python
    # ----- Per-incident pages -----
    generate_incident_pages(entries)
```

- [ ] **Step 5: Run all tests to verify they pass**

Run: `pytest tests/test_per_incident_pages.py tests/test_render_markdown.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/render_markdown.py tests/test_per_incident_pages.py
git commit -m "feat: generate per-incident pages at /incident/INC-XXXXX.html"
```

---

### Task 3: Create the incident page layout

**Files:**
- Create: `docs/_layouts/incident.html`

- [ ] **Step 1: Create `docs/_layouts/incident.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ page.title | default: "Incident" }} · GenAI & Agentic AI Security Incidents</title>
  <meta name="description" content="{{ page.description_preview | default: 'Incident detail from the GenAI & Agentic AI Security Incidents dataset.' | escape }}">
  <link rel="canonical" href="https://emmanuelgjr.github.io/genai_agentic_incidents/incident/{{ page.incident_id }}.html">
  <!-- Open Graph -->
  <meta property="og:title" content="{{ page.title | escape }}">
  <meta property="og:description" content="{{ page.description_preview | default: 'GenAI security incident detail.' | escape }}">
  <meta property="og:url" content="https://emmanuelgjr.github.io/genai_agentic_incidents/incident/{{ page.incident_id }}.html">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="GenAI & Agentic AI Security Incidents">
  <link rel="stylesheet" href="{{ '/style.css' | relative_url }}">
  <!-- JSON-LD -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "DigitalDocument",
    "name": {{ page.title | jsonify }},
    "description": {{ page.description_preview | default: "" | jsonify }},
    "url": "https://emmanuelgjr.github.io/genai_agentic_incidents/incident/{{ page.incident_id }}.html",
    "datePublished": "{{ page.date | default: '' }}",
    "publisher": {
      "@type": "Person",
      "name": "Emmanuel Guilherme Junior"
    },
    "keywords": {{ page.tags_str | default: "" | jsonify }}
  }
  </script>
</head>
<body class="shard-page incident-page">
  <header class="masthead">
    <div class="wrap">
      <div class="title-row">
        <h1>{{ page.incident_id }}</h1>
        <p class="links">
          <a href="{{ '/' | relative_url }}">← All incidents</a>
          {% if page.year %}<a href="{{ '/incidents/' | append: page.year | append: '.html' | relative_url }}">← {{ page.year }} incidents</a>{% endif %}
          <a href="https://github.com/emmanuelgjr/genai_agentic_incidents">GitHub</a>
          <a href="https://doi.org/10.5281/zenodo.20248676">DOI</a>
        </p>
      </div>
    </div>
  </header>

  <main class="wrap shard-body">
    {{ content }}
  </main>

  <footer>
    <div class="wrap">
      <p>
        Curated by <strong>Emmanuel Guilherme Junior</strong> ·
        Data licensed <a href="https://creativecommons.org/licenses/by/4.0/">CC&nbsp;BY&nbsp;4.0</a> ·
        Code licensed <a href="https://opensource.org/licenses/MIT">MIT</a> ·
        Cite with DOI <a href="https://doi.org/10.5281/zenodo.20248676"><code>10.5281/zenodo.20248676</code></a>.
      </p>
    </div>
  </footer>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add docs/_layouts/incident.html
git commit -m "feat: add Jekyll layout for per-incident pages"
```

---

### Task 4: Update app.js links to point to per-incident pages

**Files:**
- Modify: `docs/app.js:238-241,275-277`

- [ ] **Step 1: Update the ID cell link in `renderTable`**

In `docs/app.js`, change lines 238-241 from:

```javascript
    const yearShard = e.year ? `incidents/${e.year}.html#${e.id.toLowerCase()}` : '';
    const idCell = yearShard
      ? `<a href="${yearShard}" onclick="event.stopPropagation()">${escapeHtml(e.id)}</a>`
      : escapeHtml(e.id);
```

To:

```javascript
    const incidentUrl = `incident/${e.id}.html`;
    const idCell = `<a href="${incidentUrl}" onclick="event.stopPropagation()">${escapeHtml(e.id)}</a>`;
```

- [ ] **Step 2: Update the "full details" link in `renderDetail`**

In `docs/app.js`, change lines 275-277 from:

```javascript
  const shardLink = e.year
    ? `<a href="incidents/${e.year}.html#${e.id.toLowerCase()}">full details ↗</a>`
    : '';
```

To:

```javascript
  const shardLink = `<a href="incident/${e.id}.html">full details ↗</a>`;
```

- [ ] **Step 3: Commit**

```bash
git add docs/app.js
git commit -m "feat: update app.js links to point to per-incident pages"
```

---

### Task 5: Add permalink icons in year shards

**Files:**
- Modify: `scripts/render_markdown.py` (inside `render_incident_block`)

- [ ] **Step 1: Write a test for the permalink in year-shard context**

Add to `tests/test_render_markdown.py`:

```python
def test_render_incident_block_contains_permalink():
    """Incident block should include a link to the per-incident page."""
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
    assert "/incident/INC-00001.html" in body
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_render_markdown.py::test_render_incident_block_contains_permalink -v`
Expected: FAIL — no permalink link in the output yet

- [ ] **Step 3: Add the permalink to `render_incident_block`**

In `scripts/render_markdown.py`, in `render_incident_block`, after the `### {e['id']}` line, add a permalink:

Change:

```python
    lines.append(f"### {e['id']}")
```

To:

```python
    lines.append(f"### {e['id']}  [↗](/incident/{e['id']}.html)")
```

This adds a small arrow link after the incident ID heading that points to the canonical per-incident page.

- [ ] **Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/render_markdown.py tests/test_render_markdown.py
git commit -m "feat: add permalink to per-incident page in incident blocks"
```

---

### Task 6: Add breadcrumb CSS

**Files:**
- Modify: `docs/style.css`

- [ ] **Step 1: Add incident-page styles to `docs/style.css`**

Append before the `/* ----------------------------- Mobile ----------------------------- */` section:

```css
/* ----------------------------- Incident pages ----------------------------- */
.incident-page .masthead h1 {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 1.35rem;
  letter-spacing: 0.02em;
  color: var(--muted);
}
```

- [ ] **Step 2: Commit**

```bash
git add docs/style.css
git commit -m "style: add incident-page heading styles"
```

---

### Task 7: Update .gitattributes and CI drift check

**Files:**
- Modify: `.gitattributes`
- Modify: `.github/workflows/validate.yml:36`

- [ ] **Step 1: Add `docs/incident/*.md` to `.gitattributes`**

After the existing `docs/incidents/*.md` line in `.gitattributes`, add:

```
docs/incident/*.md          text eol=lf linguist-generated=true
```

- [ ] **Step 2: Add `docs/incident` to the CI drift check**

In `.github/workflows/validate.yml`, change line 36 from:

```yaml
          paths="INCIDENTS.md data/incidents.json data/incidents.min.json data/id_deprecations.json docs/incidents docs/data docs/charts src/genai_incidents/data src/genai_incidents/schema"
```

To:

```yaml
          paths="INCIDENTS.md data/incidents.json data/incidents.min.json data/id_deprecations.json docs/incidents docs/incident docs/data docs/charts src/genai_incidents/data src/genai_incidents/schema"
```

- [ ] **Step 3: Commit**

```bash
git add .gitattributes .github/workflows/validate.yml
git commit -m "ci: add docs/incident to drift check and gitattributes"
```

---

### Task 8: Run full build and verify

**Files:**
- None (verification only)

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run the full render to generate per-incident pages**

Run: `python scripts/render_markdown.py`
Expected output should include a line like: `wrote 7714 per-incident pages under ...docs/incident/`

- [ ] **Step 3: Spot-check a few generated files**

Check that these files exist and have correct content:
- `docs/incident/INC-04853.md` — Samsung ChatGPT leak
- `docs/incident/INC-04490.md` — Bing Sydney jailbreak
- Verify front matter has `layout: incident`, `permalink: /incident/INC-XXXXX.html`
- Verify the body contains the incident's title, description, and OWASP codes

- [ ] **Step 4: Verify no stale files in docs/incident/**

Run: `python -c "from pathlib import Path; files = list(Path('docs/incident').glob('*.md')); print(f'{len(files)} files')" `
Expected: Count matches total incidents (~7,714)

- [ ] **Step 5: Run the CI drift check locally**

Run: `python scripts/render_markdown.py && git status --porcelain docs/incident docs/incidents`
Expected: Only changes should be the new `docs/incident/` files (untracked) and any year-shard updates from the permalink addition

- [ ] **Step 6: Stage and commit all generated files**

```bash
git add docs/incident/
git commit -m "build: generate per-incident pages for all 7,714 incidents"
```

---

### Task 9: Exclude docs/superpowers from Jekyll build

**Files:**
- Modify: `docs/_config.yml`

- [ ] **Step 1: Add `superpowers` to Jekyll exclude list**

The `docs/superpowers/` directory contains design specs and plans — not site content. Add it to the exclude list in `docs/_config.yml`:

Change:

```yaml
exclude:
  - _site
  - Gemfile
  - Gemfile.lock
```

To:

```yaml
exclude:
  - _site
  - Gemfile
  - Gemfile.lock
  - superpowers
```

- [ ] **Step 2: Commit**

```bash
git add docs/_config.yml
git commit -m "build: exclude superpowers dir from Jekyll build"
```
