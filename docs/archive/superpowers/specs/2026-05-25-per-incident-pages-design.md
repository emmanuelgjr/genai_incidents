# Per-Incident Pages — Design Spec

**Date:** 2026-05-25
**Status:** Approved
**Author:** Emmanuel Guilherme Junior + Claude

## Goal

Generate a standalone HTML page for every incident at `/incident/INC-XXXXX.html` so each incident has a stable, citable, SEO-indexable URL.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Canonical URL | `/incident/INC-XXXXX.html` replaces year-shard hash links | Clean, citable, SEO-friendly |
| URL structure | Flat `/incident/` namespace | INC-* IDs are globally unique; hierarchy adds no value |
| Rendering approach | Static Jekyll markdown files | Same pattern as year shards; full SEO; no JS dependency |
| Year shards | Kept as browsing surface | Still useful for "all 2023 incidents" view; not canonical for individual citations |

## Architecture

### 1. File Generation (`scripts/render_markdown.py`)

A new function generates one `docs/incident/<INC-XXXXX>.md` per incident.

**Front matter:**
```yaml
---
title: "INC-04853 — Samsung employees leak source code..."
layout: incident
permalink: /incident/INC-04853.html
incident_id: INC-04853
year: 2023
severity: High
---
```

**Body:** Full incident detail block (description, affected, attack vector, impact, OWASP/NIST/MITRE mappings, mitigations, references, tags). Uses the same rendering logic as year-shard incident blocks — extract a shared helper function to avoid duplication.

**Lifecycle:**
- `docs/incident/` is cleared (all `.md` files removed) before regeneration to handle deleted/merged incidents.
- Deterministic output: same data produces same files.

### 2. Jekyll Layout (`docs/_layouts/incident.html`)

New layout for single-incident pages, reusing `style.css` and the site masthead.

**Head:**
- `<title>{{ page.title }} · GenAI & Agentic AI Security Incidents</title>`
- `<link rel="canonical" href="https://emmanuelgjr.github.io/genai_agentic_incidents/incident/{{ page.incident_id }}.html">`
- Open Graph meta tags: `og:title`, `og:description` (truncated to 200 chars), `og:url`, `og:type=article`
- JSON-LD `<script type="application/ld+json">` with Schema.org `DigitalDocument`: name, description, datePublished, url, publisher (Emmanuel Guilherme Junior), keywords (from tags)

**Body:**
- Masthead with site title
- Breadcrumb: `← All incidents` | `← <year> incidents`
- `{{ content }}` — the incident detail block
- Footer with attribution (same as main site)

**Styling:** Reuses `.incident-anchor` / `.incident-detail` card styles from `style.css`. May need minor additions for breadcrumb and single-page layout.

### 3. Link Updates (`docs/app.js`)

Two link patterns change:

| Location | Old | New |
|---|---|---|
| ID cell in table row | `incidents/<year>.html#inc-XXXXX` | `incident/<INC-XXXXX>.html` |
| "full details ↗" in expanded detail row | `incidents/<year>.html#inc-XXXXX` | `incident/<INC-XXXXX>.html` |

### 4. Year Shard Cross-links (`render_markdown.py`)

Each incident heading in year shards gets a permalink link (e.g., `[↗](/incident/INC-XXXXX.html)`) after the ID, pointing to the canonical per-incident page.

### 5. CI & Repo Hygiene

**Drift check (`.github/workflows/validate.yml`):**
Add `docs/incident` to the list of regenerated paths validated by the drift check.

**`.gitattributes`:**
Add `docs/incident/*.md linguist-generated=true` so GitHub excludes these from diffs and language stats.

## Scope Boundaries

**In scope:**
- File generation in `render_markdown.py`
- New `_layouts/incident.html` layout
- `app.js` link updates
- Year shard permalink icons
- CI drift check update
- `.gitattributes` update

**Out of scope:**
- Sitemap generation (future enhancement)
- robots.txt changes (GitHub Pages default is fine)
- Next/prev navigation between incidents
- Search within per-incident pages (use the main app)
- Any new data fields or schema changes

## Tradeoffs

- **~7,700 markdown files** added to `docs/incident/`. Each ~2-4 KB. Total ~25 MB. Well under GitHub's limits.
- **Jekyll build time** increases from ~1 min to ~3-5 min.
- **Git history** gets one large initial commit for all incident files, then incremental diffs on rebuilds.
- **`linguist-generated`** flag prevents these from inflating repo language stats or cluttering PRs.
