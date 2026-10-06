"""
Render data/incidents.json -> INCIDENTS.md (human-readable SoT).

Layout:
  - INCIDENTS.md
      * Header with metadata + taxonomy coverage summary
      * Single unified incidents table, newest-first
      * Per-year shards table linking to docs/incidents/<year>.md
  - docs/incidents/<year>.md
      * Detail blocks for every incident in that year

Splitting the per-incident detail blocks into per-year shards keeps
INCIDENTS.md well under GitHub's 5 MB soft cap so the file renders
cleanly in the web UI.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from taxonomy_versions import taxonomy_versions


def utc_today() -> date:
    """Calendar date in UTC. CI builds run in UTC; a contributor whose local
    clock lags UTC must stamp the same dates as a same-UTC-day CI build, or
    the deterministic drift check flaps."""
    return datetime.now(timezone.utc).date()

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMA = ROOT / "schema"
SHARD_DIR = ROOT / "docs" / "incidents"
SITE_DATA_DIR = ROOT / "docs" / "data"
CHART_DIR = ROOT / "docs" / "charts"
PKG_DATA_DIR = ROOT / "src" / "genai_incidents" / "data"
PKG_SCHEMA_DIR = ROOT / "src" / "genai_incidents" / "schema"
OUT = ROOT / "INCIDENTS.md"


def _write_lf(path: Path, text: str, add_newline: bool = True) -> None:
    """Write ``text`` to ``path`` with explicit LF line endings, regardless
    of platform. Source descriptions (especially NVD CVE blurbs) sometimes
    carry embedded ``\\r`` characters; strip them so we never emit mixed
    line endings into a generated file."""
    text = text.replace("\r\n", "\n").replace("\r", "")
    if add_newline and not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


_ENDRAW_RE = re.compile(r"\{%-?\s*endraw\s*-?%\}")

_SAFE_URL_SCHEME = re.compile(r"^(https?:|mailto:|/|\#|\.{0,2}/)", re.I)


def md_safe_text(text: str) -> str:
    """Neutralise raw HTML in untrusted free text (incident descriptions,
    titles, etc.) before it is emitted into a Markdown shard. kramdown passes
    raw inline/block HTML straight through to the page, so an advisory
    description containing ``<img src=x onerror=...>`` would execute as stored
    XSS on the rendered shard.

    Escape ``& < >`` over the WHOLE string, unconditionally. An earlier version
    exempted code spans/fences (kramdown escapes those for display), but the
    exemption only held if our notion of "code" matched kramdown's exactly —
    and an inline ```...``` payload mid-prose slipped through that gap. On a
    security dataset, any parser divergence is a bypass, so we escape
    everything. The only cost is that HTML inside code examples shows as
    entities (`&lt;img&gt;`), which for payload listings is if anything
    clearer."""
    if not text:
        return text
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def safe_url(url: str) -> str:
    """Only allow http(s)/mailto/relative URLs in generated links; everything
    else (javascript:, data:, vbscript:, …) collapses to '#'. Also reject URLs
    containing whitespace or angle brackets/quotes — a valid URL has none, and
    scraped 'URLs' that do are typically malformed HTML (e.g. a news title that
    swallowed '/> <meta property=...'), which would inject raw tags into the
    Markdown link. Defence in depth for URLs ingested from external sources."""
    u = (url or "").strip()
    if not _SAFE_URL_SCHEME.match(u):
        return "#"
    if re.search(r'[\s<>"\']', u):
        return "#"
    return u


def liquid_raw_block(body_lines: list[str]) -> list[str]:
    """Wrap generated page content in ``{% raw %}`` so Jekyll never parses
    incident text as Liquid. Advisory descriptions legitimately contain
    ``{{ ... }}`` / ``{% for ... %}`` (e.g. template-injection writeups),
    which otherwise crash the Pages build with a Liquid syntax error.
    Any literal ``{% endraw %}`` inside the content is defanged so text
    can't break out of the raw block."""
    safe = [_ENDRAW_RE.sub(lambda m: m.group(0).replace("{%", "{ %"), ln)
            for ln in body_lines]
    return ["{% raw %}", *safe, "{% endraw %}"]


# --- Tiny pure-Python SVG generator for trend charts -----------------------

SEV_COLOURS = {
    "Critical": "#b40000",
    "High":     "#cc4400",
    "Medium":   "#8a6d00",
    "Low":      "#2a7f2a",
    "Info":     "#555555",
}


def _svg_open(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_xml_escape(title)}" '
        'font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="11">'
    ]


def _xml_escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_year_bar_chart(year_counts: Counter, out_path: Path) -> None:
    """Bar chart of incidents per year, oldest -> newest, x-axis labels."""
    years = sorted(year_counts.keys())
    if not years:
        return
    counts = [year_counts[y] for y in years]
    max_n = max(counts)

    W, H = 760, 240
    M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 44, 12, 30, 36
    chart_w = W - M_LEFT - M_RIGHT
    chart_h = H - M_TOP - M_BOTTOM
    bar_w = chart_w / max(len(years), 1)

    parts = _svg_open(W, H, f"Incidents per year, {years[0]}–{years[-1]}")
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    parts.append(
        f'<text x="{M_LEFT}" y="18" font-weight="600">Incidents per year '
        f'({sum(counts):,} total)</text>'
    )

    # 5 y-axis gridlines
    for i in range(5 + 1):
        y_val = int(max_n * (5 - i) / 5)
        y_px = M_TOP + (chart_h * i / 5)
        parts.append(
            f'<line x1="{M_LEFT}" y1="{y_px:.1f}" x2="{W - M_RIGHT}" y2="{y_px:.1f}" '
            'stroke="#e5e5e5" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{M_LEFT - 6}" y="{y_px + 3:.1f}" text-anchor="end" fill="#666">'
            f'{y_val:,}</text>'
        )

    # Bars
    for i, (y, c) in enumerate(zip(years, counts)):
        bh = (c / max_n) * chart_h if max_n else 0
        x = M_LEFT + i * bar_w + bar_w * 0.1
        bw = bar_w * 0.8
        bar_y = M_TOP + (chart_h - bh)
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'fill="#0a58ca" rx="1"><title>{y}: {c:,}</title></rect>'
        )
        # Label every other year to avoid crowding when range is wide
        if (years[-1] - y) % 2 == 0 or i in (0, len(years) - 1):
            parts.append(
                f'<text x="{x + bw / 2:.1f}" y="{H - M_BOTTOM + 14}" text-anchor="middle" '
                f'fill="#666">{y}</text>'
            )

    parts.append("</svg>")
    _write_lf(out_path, "\n".join(parts))


def render_owasp_bar_chart(
    counts: Counter, names: dict[str, str], title: str, out_path: Path
) -> None:
    """Horizontal bar chart for OWASP code distribution."""
    codes = sorted(names.keys())
    vals = [counts.get(c, 0) for c in codes]
    max_n = max(vals) if vals else 1

    W = 760
    row_h = 22
    M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 220, 60, 30, 12
    chart_w = W - M_LEFT - M_RIGHT
    H = M_TOP + M_BOTTOM + row_h * len(codes)

    parts = _svg_open(W, H, title)
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    parts.append(f'<text x="12" y="18" font-weight="600">{_xml_escape(title)}</text>')

    for i, code in enumerate(codes):
        y = M_TOP + i * row_h + 6
        bw = (vals[i] / max_n) * chart_w if max_n else 0
        parts.append(
            f'<text x="{M_LEFT - 8}" y="{y + 11}" text-anchor="end" fill="#333">'
            f'{_xml_escape(code)} · {_xml_escape(names[code])}</text>'
        )
        parts.append(
            f'<rect x="{M_LEFT}" y="{y}" width="{bw:.1f}" height="14" fill="#0a58ca" rx="2">'
            f'<title>{_xml_escape(names[code])}: {vals[i]:,}</title></rect>'
        )
        parts.append(
            f'<text x="{M_LEFT + bw + 6:.1f}" y="{y + 11}" fill="#666">'
            f'{vals[i]:,}</text>'
        )

    parts.append("</svg>")
    _write_lf(out_path, "\n".join(parts))


def render_severity_stack_chart(
    by_year_sev: dict[int, Counter], out_path: Path
) -> None:
    """Stacked bar of severity composition per year (last 12 years)."""
    years = sorted(by_year_sev.keys())[-12:]
    if not years:
        return
    sev_order = ["Critical", "High", "Medium", "Low", "Info"]
    totals = {y: sum(by_year_sev[y].values()) for y in years}
    max_n = max(totals.values()) if totals else 1

    W, H = 760, 240
    M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 44, 130, 30, 36
    chart_w = W - M_LEFT - M_RIGHT
    chart_h = H - M_TOP - M_BOTTOM
    bar_w = chart_w / max(len(years), 1)

    parts = _svg_open(W, H, "Severity composition per year")
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    parts.append(
        f'<text x="{M_LEFT}" y="18" font-weight="600">'
        f'Severity composition, last {len(years)} years</text>'
    )

    for i, y in enumerate(years):
        x = M_LEFT + i * bar_w + bar_w * 0.1
        bw = bar_w * 0.8
        cumulative = 0
        for sev in sev_order:
            c = by_year_sev[y].get(sev, 0)
            if c == 0:
                continue
            bh = (c / max_n) * chart_h
            bar_y = M_TOP + (chart_h - cumulative - bh)
            parts.append(
                f'<rect x="{x:.1f}" y="{bar_y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                f'fill="{SEV_COLOURS[sev]}"><title>{y} {sev}: {c:,}</title></rect>'
            )
            cumulative += bh
        parts.append(
            f'<text x="{x + bw / 2:.1f}" y="{H - M_BOTTOM + 14}" text-anchor="middle" '
            f'fill="#666">{y}</text>'
        )

    # Legend
    lx = W - M_RIGHT + 8
    for i, sev in enumerate(sev_order):
        ly = M_TOP + i * 18
        parts.append(
            f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{SEV_COLOURS[sev]}"/>'
        )
        parts.append(
            f'<text x="{lx + 18}" y="{ly + 10}" fill="#333">{sev}</text>'
        )

    parts.append("</svg>")
    _write_lf(out_path, "\n".join(parts))


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def sort_key(e: dict) -> tuple:
    """Newest-first sort. Falls back to year when no full date is present."""
    d = (e.get("date") or "").strip()
    year = e.get("year") or 0
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", d)
    if m:
        y, mo, da = (int(x) for x in m.groups())
        return (-y, -mo, -da, e.get("title", "").lower())
    m = re.match(r"^(\d{4})-(\d{2})", d)
    if m:
        y, mo = (int(x) for x in m.groups())
        return (-y, -mo, 0, e.get("title", "").lower())
    m = re.match(r"^(\d{4})", d)
    if m:
        return (-int(m.group(1)), 0, 0, e.get("title", "").lower())
    return (-year, 0, 0, e.get("title", "").lower())


def truncate_title(title: str, limit: int = 110) -> str:
    title = title or ""
    if len(title) <= limit:
        return title
    return title[: limit - 1].rstrip() + "…"


def shard_path(year: int) -> Path:
    return SHARD_DIR / f"{year}.md"


def shard_rel(year: int) -> str:
    return f"docs/incidents/{year}.md"


def render_incident_block(e: dict) -> list[str]:
    """Return a list of markdown lines for one incident card.

    Reusable by both year-shard generation and per-incident page generation.
    """
    lines: list[str] = []
    # Each incident is wrapped in a `<div class="incident-anchor">`
    # with an id matching the lowercase INC-* slug. The layout's
    # JS highlights `.target` when the URL hash matches, so links
    # arriving from the main app land on a visibly-marked card.
    slug = e["id"].lower()
    lines.append(f'<div class="incident-anchor" id="{slug}" markdown="1">')
    lines.append("")
    # Self-anchor permalink (copy a stable deep link to this incident). The
    # per-incident standalone pages were removed — this shard block, reachable
    # at #<slug>, is the canonical detail target.
    lines.append(f"### {e['id']}  [#](#{slug})")
    lines.append("")
    lines.append(f"**{md_safe_text(e['title'])}**  ")
    meta_bits = [
        e.get("date", ""),
        e.get("category", ""),
        f"Severity: {e.get('severity','')}",
    ]
    lines.append("_" + " · ".join(b for b in meta_bits if b) + "_")
    if e.get("status") == "retracted":
        reason = e.get("status_reason") or {}
        lines.append("")
        lines.append(
            "**RETRACTED** -- every CVE id on this entry is REJECTED by the CVE "
            f"Program (checked {reason.get('as_of', 'n/a')}). Kept so this ID keeps "
            "resolving; not counted as an incident."
        )
    elif e.get("rejected_cve_ids"):
        lines.append("")
        lines.append(
            "**Note:** the CVE Program marks "
            + ", ".join(f"`{c}`" for c in e["rejected_cve_ids"])
            + " as REJECTED; this entry stands on its other sources."
        )
    if e.get("exploited_in_wild"):
        kev = "**🚨 Exploited in the wild** (CISA KEV"
        if e.get("kev_date_added"):
            kev += f", added {e['kev_date_added']}"
        kev += ")"
        lines.append("")
        lines.append(kev)
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
    lines.append(md_safe_text(e.get("description", "")))
    lines.append("")
    if e.get("affected"):
        lines.append(f"**Affected:** {md_safe_text(e['affected'])}  ")
    if e.get("attack_vector"):
        lines.append(f"**Attack vector:** `{e['attack_vector']}`  ")
    if e.get("impact"):
        lines.append(f"**Impact:** {md_safe_text(e['impact'])}  ")
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
            f"`{l['layer']} {l.get('label','')}`" for l in e["maestro_layers"]
        )
        lines.append(f"**MAESTRO layers:** {ml}  ")
    lines.append("")
    if e.get("mitigations"):
        lines.append("**Mitigations:**")
        for m in e["mitigations"]:
            lines.append(f"- {md_safe_text(m)}")
        lines.append("")
    if e.get("references"):
        lines.append("**References:**")
        for ref in e["references"]:
            url = safe_url(ref["url"])
            title = md_safe_text(ref.get("title") or ref["url"])
            suffix = f" _({md_safe_text(ref.get('type'))})_" if ref.get("type") else ""
            lines.append(f"- [{title}]({url}){suffix}")
        lines.append("")
        primary = e["references"][0]
        if e.get("aiid_id"):
            cite_url = f"https://incidentdatabase.ai/cite/{e['aiid_id']}/"
            cite_label = "AI Incident Database"
        else:
            cite_url = safe_url(primary["url"])
            cite_label = md_safe_text(primary.get("title") or primary["url"])
        lines.append(f"**Cite this incident:** [{cite_label}]({cite_url})")
        lines.append("")
    if e.get("tags"):
        lines.append("**Tags:** " + ", ".join(f"`{t}`" for t in e["tags"]))
        lines.append("")
    lines.append("</div>")
    lines.append("")
    return lines


INCIDENT_PAGE_DIR = ROOT / "docs" / "incident"


def _yaml_escape(s: str) -> str:
    """Escape a string for safe use as a YAML scalar value."""
    if not s:
        return '""'
    if any(c in s for c in ':{}[]&*?|->!%@`,"\'#'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def prune_incident_pages(out_dir: Path | None = None) -> int:
    """Remove the legacy per-incident pages under docs/incident/.

    These standalone pages (one markdown file per incident) were dropped:
    at 12k+ incidents the Jekyll build of that many files was the deploy
    bottleneck, and the year-shard blocks (reachable at #<slug>) plus the
    client-side detail view in app.js already cover the same content. The
    directory is removed entirely so it stays out of the build. Returns the
    number of files removed."""
    out_dir = out_dir or INCIDENT_PAGE_DIR
    if not out_dir.exists():
        return 0
    removed = 0
    for existing in out_dir.glob("*.md"):
        existing.unlink()
        removed += 1
    try:
        out_dir.rmdir()
    except OSError:
        pass
    if removed:
        print(f"pruned {removed} legacy per-incident pages under {out_dir}/")
    return removed


def render_details_shard(year: int, rows: list[dict]) -> str:
    rows = sorted(rows, key=sort_key)
    lines: list[str] = []
    # Jekyll front matter — picks the custom layout that brings the main
    # app's chrome / styling onto each year shard and provides a
    # back-to-search link plus highlight-on-hash behaviour.
    lines.append("---")
    lines.append(f"title: \"Incident Details — {year}\"")
    lines.append("layout: incident-shard")
    lines.append(f"permalink: /incidents/{year}.html")
    lines.append("---")
    lines.append("")
    body: list[str] = []
    body.append(f"_{len(rows):,} incidents in this year shard._  ")
    body.append(
        "Use the [searchable web view](../index.html) for filtering across "
        "all years. The raw markdown lives under "
        "[`docs/incidents/`](https://github.com/emmanuelgjr/genai_incidents/tree/main/docs/incidents)."
    )
    body.append("")
    for e in rows:
        body.extend(render_incident_block(e))
    body.append("")
    body.append(
        f"> Back to [`INCIDENTS.md`](../../INCIDENTS.md). "
        f"Generated by `scripts/render_markdown.py`."
    )
    lines.extend(liquid_raw_block(body))
    return "\n".join(lines)


def render():
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    entries = list(raw["incidents"])
    entries.sort(key=sort_key)
    # WS4-T2: retracted entries (e.g. every CVE REJECTED) are never deleted, so
    # their IDs keep resolving and they keep a (bannered) card in the year
    # shards -- but they are not incidents that stand, so they are excluded
    # from every count, chart and table. `all_entries` feeds only the shards.
    all_entries = entries
    entries = [e for e in all_entries if e.get("status") != "retracted"]
    n_retracted = len(all_entries) - len(entries)

    # Tiny stats file for the README's live incident-count badge (shields.io
    # dynamic JSON reads it). Kept small so the badge endpoint is fast, and
    # regenerated every build so it never drifts from the dataset.
    years = sorted({e.get("year") for e in entries if e.get("year")})
    stats = {
        "incident_count": len(entries),
        "retracted_count": n_retracted,
        "landmark_count": sum(1 for e in entries if e.get("tier") == "landmark"),
        "version": raw.get("version", ""),
        "generated": raw.get("generated", ""),
        "year_min": years[0] if years else None,
        "year_max": years[-1] if years else None,
        # Versions of the pinned taxonomies the corpus codes belong to, derived
        # from mappings/*.json by scripts/taxonomy_versions.py (never literals).
        "taxonomy_versions": taxonomy_versions(),
    }
    _write_lf(DATA / "stats.json", json.dumps(stats, indent=2))

    llm_counts: Counter = Counter()
    asi_counts: Counter = Counter()
    atlas_counts: Counter = Counter()
    sev_counts: Counter = Counter()
    year_counts: Counter = Counter()
    by_year_sev: dict[int, Counter] = defaultdict(Counter)
    cve_count = 0
    by_year: dict[int, list[dict]] = defaultdict(list)
    shard_by_year: dict[int, list[dict]] = defaultdict(list)
    for e in all_entries:
        if e.get("year"):
            shard_by_year[e["year"]].append(e)
    for e in entries:
        for c in e.get("owasp_llm", []):
            llm_counts[c] += 1
        for c in e.get("owasp_asi", []):
            asi_counts[c] += 1
        for c in e.get("mitre_atlas", []):
            atlas_counts[c] += 1
        sev_counts[e.get("severity", "Medium")] += 1
        if e.get("year"):
            year_counts[e["year"]] += 1
            by_year[e["year"]].append(e)
            by_year_sev[e["year"]][e.get("severity", "Medium")] += 1
        if e.get("cve_ids"):
            cve_count += 1

    lines: list[str] = []
    lines.append("# GenAI & Agentic AI Security Incidents")
    lines.append("")
    lines.append(
        "A consolidated, machine-readable index of GenAI and agentic AI security incidents."
    )
    lines.append(
        "Every applicable entry is mapped to four core taxonomies — **OWASP LLM Top 10 (2026)**, "
        "**OWASP Agentic Top 10 (ASI)**, **NIST AI RMF**, and **MITRE ATLAS** — plus a companion "
        "**MAESTRO** mapping where the source provides it and an experimental **VERIS 1.4.1** "
        "crosswalk computed at export time. See docs/TAXONOMIES.md for the full picture."
    )
    lines.append("")
    lines.append(f"- **Version:** {raw.get('version','1.0.0')}")
    lines.append(f"- **Generated:** {raw.get('generated', str(utc_today()))}")
    lines.append(f"- **Total incidents:** **{len(entries):,}**")
    if year_counts:
        latest = max(year_counts)
        earliest = min(year_counts)
        lines.append(f"- **Date range:** {earliest} – {latest}")
    lines.append(f"- **With CVE:** {cve_count:,}")
    lines.append(
        "- **Machine-readable:** [`data/incidents.json`](data/incidents.json) · "
        "[`data/incidents.min.json`](data/incidents.min.json)"
    )
    lines.append("- **Schema:** [`schema/incident.schema.json`](schema/incident.schema.json)")
    lines.append("")
    lines.append(
        "> Sorted newest-first. Click any `INC-*****` to open the year's "
        "detail shard. Use **Ctrl/Cmd-F** to filter by vendor, CVE, OWASP code, "
        "or year."
    )
    lines.append("")

    # ----- Charts -----
    # OWASP Top 10 for LLM Applications 2026 (mappings/owasp_llm_top10_2026.json).
    # Rank order matters: the chart renders in insertion order.
    llm_names = {
        "LLM01": "Prompt Injection",
        "LLM02": "Sensitive Information Disclosure",
        "LLM03": "Excessive Agency",
        "LLM04": "Supply Chain",
        "LLM05": "Data and Model Poisoning",
        "LLM06": "Unbounded Consumption",
        "LLM07": "Misinformation",
        "LLM08": "Hidden Context Exposure",
        "LLM09": "Vector and Embedding Weaknesses",
        "LLM10": "Improper Output Handling",
    }
    asi_names = {
        "ASI01": "Agent Goal Hijack",
        "ASI02": "Tool Misuse & Exploitation",
        "ASI03": "Identity & Privilege Abuse",
        "ASI04": "Agentic Supply Chain Vulnerabilities",
        "ASI05": "Unexpected Code Execution (RCE)",
        "ASI06": "Memory & Context Poisoning",
        "ASI07": "Insecure Inter-Agent Communication",
        "ASI08": "Cascading Failures",
        "ASI09": "Human-Agent Trust Exploitation",
        "ASI10": "Rogue Agents",
    }
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    render_year_bar_chart(year_counts, CHART_DIR / "year_bar.svg")
    render_severity_stack_chart(by_year_sev, CHART_DIR / "severity_stack.svg")
    render_owasp_bar_chart(
        llm_counts, llm_names, "OWASP LLM Top 10 (2026) — incident coverage",
        CHART_DIR / "owasp_llm.svg",
    )
    render_owasp_bar_chart(
        asi_counts, asi_names, "OWASP Agentic Top 10 (ASI) — incident coverage",
        CHART_DIR / "owasp_asi.svg",
    )

    lines.append("## Trends")
    lines.append("")
    lines.append(
        "Auto-generated from the current dataset. SVGs live under "
        "[`docs/charts/`](docs/charts/)."
    )
    lines.append("")
    lines.append("![Incidents per year](docs/charts/year_bar.svg)")
    lines.append("")
    lines.append("![Severity composition per year](docs/charts/severity_stack.svg)")
    lines.append("")
    lines.append("![OWASP LLM coverage](docs/charts/owasp_llm.svg)")
    lines.append("")
    lines.append("![OWASP ASI coverage](docs/charts/owasp_asi.svg)")
    lines.append("")

    # ----- Coverage -----
    lines.append("## Coverage")
    lines.append("")
    lines.append("### Severity")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---:|")
    for s in ["Critical", "High", "Medium", "Low", "Info"]:
        if sev_counts.get(s):
            lines.append(f"| {s} | {sev_counts[s]:,} |")
    lines.append("")

    lines.append("### Incidents per Year")
    lines.append("")
    lines.append("| Year | Count | Details |")
    lines.append("|---|---:|---|")
    for y in sorted(year_counts.keys(), reverse=True):
        lines.append(
            f"| {y} | {year_counts[y]:,} | [{shard_rel(y)}]({shard_rel(y)}) |"
        )
    lines.append("")

    lines.append("### OWASP LLM Top 10 (2026)")
    lines.append("")
    lines.append("| Code | Name | Count |")
    lines.append("|---|---|---:|")
    for code, name in llm_names.items():
        lines.append(f"| {code} | {name} | {llm_counts.get(code,0):,} |")
    lines.append("")

    lines.append("### OWASP Agentic Top 10 (ASI)")
    lines.append("")
    lines.append("| Code | Name | Count |")
    lines.append("|---|---|---:|")
    for code, name in asi_names.items():
        lines.append(f"| {code} | {name} | {asi_counts.get(code,0):,} |")
    lines.append("")

    lines.append("### Top MITRE ATLAS Techniques")
    lines.append("")
    lines.append("| Technique | Count |")
    lines.append("|---|---:|")
    for tech, count in atlas_counts.most_common(15):
        lines.append(f"| `{tech}` | {count:,} |")
    lines.append("")

    # ----- Unified incidents table -----
    lines.append("## Incidents")
    lines.append("")
    lines.append(
        f"All **{len(entries):,}** incidents in a single table, newest-first. "
        "Each `INC-*****` link opens that year's detail shard. Severity is the "
        "maximum reported across sources for that incident."
    )
    lines.append("")
    lines.append(
        "| # | Date | ID | Title | Severity | OWASP LLM | OWASP ASI | CVEs |"
    )
    lines.append(
        "|---:|---|---|---|---|---|---|---|"
    )
    for idx, e in enumerate(entries, start=1):
        llm = ", ".join(e.get("owasp_llm", []))
        asi = ", ".join(e.get("owasp_asi", []))
        cves = e.get("cve_ids") or []
        cve_cell = ""
        if cves:
            if len(cves) <= 2:
                cve_cell = ", ".join(f"`{c}`" for c in cves)
            else:
                cve_cell = f"`{cves[0]}` (+{len(cves) - 1})"
        date_cell = md_escape(e.get("date", "") or str(e.get("year", "")))
        title_cell = md_escape(truncate_title(e["title"]))
        year = e.get("year") or 0
        id_link = f"[`{e['id']}`]({shard_rel(year)}#{e['id'].lower()})"
        lines.append(
            f"| {idx:,} | {date_cell} | {id_link} "
            f"| {title_cell} | {md_escape(e.get('severity',''))} "
            f"| {llm} | {asi} | {cve_cell} |"
        )
    lines.append("")
    lines.append(
        "> Generated by `scripts/render_markdown.py`. Do not edit by hand — "
        "edit `data/incidents.json` or the ingest scripts and re-run "
        "`make build`."
    )

    _write_lf(OUT, "\n".join(lines))
    print(f"wrote {OUT} ({len(entries)} incidents)")

    # ----- Per-year shards -----
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    # Wipe any stale shards from previous renders (years that vanished
    # after a dedupe pass) so the directory mirrors the current dataset.
    expected = {shard_path(y).name for y in shard_by_year}
    for existing in SHARD_DIR.glob("*.md"):
        if existing.name not in expected:
            existing.unlink()
    for year, rows in shard_by_year.items():
        body = render_details_shard(year, rows)
        _write_lf(shard_path(year), body)
    total_shard_chars = sum(
        len((SHARD_DIR / f"{y}.md").read_text(encoding="utf-8"))
        for y in shard_by_year
    )
    print(
        f"wrote {len(shard_by_year)} year shards under docs/incidents/ "
        f"({total_shard_chars:,} chars total)"
    )

    # ----- Legacy per-incident pages: removed (see prune_incident_pages) -----
    prune_incident_pages()

    # Mirror the slim JSON under docs/data/ so the static site can fetch it
    # without leaving the Pages origin; and into the pip package source
    # tree so wheels built from this checkout ship the current data.
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PKG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PKG_SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    slim_src = DATA / "incidents.min.json"
    if slim_src.exists():
        body = slim_src.read_text(encoding="utf-8")
        _write_lf(SITE_DATA_DIR / "incidents.min.json", body, add_newline=False)
        _write_lf(PKG_DATA_DIR / "incidents.min.json", body, add_newline=False)
        print(f"copied {slim_src.name} -> docs/data/ + src/genai_incidents/data/")
    # Package metadata: genai_incidents.taxonomy_versions() reads this file.
    _write_lf(
        PKG_DATA_DIR / "taxonomy_versions.json",
        json.dumps(stats["taxonomy_versions"], indent=2, sort_keys=True),
    )
    deprec_src = DATA / "id_deprecations.json"
    if deprec_src.exists():
        _write_lf(
            PKG_DATA_DIR / "id_deprecations.json",
            deprec_src.read_text(encoding="utf-8"),
            add_newline=False,
        )
    schema_src = SCHEMA / "incident.schema.json"
    if schema_src.exists():
        _write_lf(
            PKG_SCHEMA_DIR / "incident.schema.json",
            schema_src.read_text(encoding="utf-8"),
            add_newline=False,
        )


if __name__ == "__main__":
    render()
