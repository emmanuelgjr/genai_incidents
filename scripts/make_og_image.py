"""
make_og_image.py
================

Generate the 1200x630 Open Graph / Twitter social card at docs/og-image.png
from the live dataset (incident count + year range). Run at Pages-build time
(pages.yml), so the shared-link preview always reflects the current dataset.
Not committed / not drift-checked — it's a build artifact.

Pure Pillow; no network. Mirrors the site's "Archive" palette (paper and
ink, one rust accent) — updated alongside the WS6 colour-direction redesign
so a shared link preview never shows the retired "amber threat console"
look after the page itself has moved on. Renders on the LIGHT (paper)
surface: it's the primary theme in this direction, and a static image can't
follow the visitor's stored theme preference the way the page itself does.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "incidents.min.json"
OUT = ROOT / "docs" / "og-image.png"

CANVAS = (255, 253, 248)  # --panel (light) #fffdf8 -- outer card surface
PANEL = (247, 244, 237)   # --bg (light) #f7f4ed -- deeper paper tone, inset rect
RUST = (154, 52, 18)      # --accent (light) #9a3412
INK = (27, 26, 23)        # --ink (light) #1b1a17
MUTED = (93, 90, 82)      # --muted (light) #5d5a52
W, H = 1200, 630


_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",          # Debian/Ubuntu CI runners
    "/usr/share/fonts/dejavu",                    # Fedora
    "/Library/Fonts", "/System/Library/Fonts/Supplemental",  # macOS
    "C:/Windows/Fonts",                           # Windows
]


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"]
        if bold else
        ["DejaVuSans.ttf", "Arial.ttf", "arial.ttf"]
    )
    for d in _FONT_DIRS:
        for name in candidates:
            p = Path(d) / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    for name in candidates:  # bare name (relies on system font search)
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    # Pillow 10+ scalable bitmap fallback so text still sizes correctly.
    return ImageFont.load_default(size)


def main() -> None:
    count = 0
    years: list[int] = []
    if DATA.exists():
        d = json.loads(DATA.read_text(encoding="utf-8"))
        incidents = d.get("incidents", [])
        count = d.get("incident_count", len(incidents))
        years = sorted({e.get("year") for e in incidents if e.get("year")})
    yr_range = f"{years[0]}–{years[-1]}" if years else ""

    img = Image.new("RGB", (W, H), CANVAS)
    draw = ImageDraw.Draw(img)

    # Rust top rule + a deeper-paper inset panel for the count.
    draw.rectangle([0, 0, W, 8], fill=RUST)
    draw.rectangle([64, 360, 1136, 566], fill=PANEL)

    draw.text((64, 70), "GenAI & Agentic AI", font=_font(72, bold=True), fill=INK)
    draw.text((64, 150), "Security Incidents", font=_font(72, bold=True), fill=RUST)

    # Big number.
    draw.text((64, 384), f"{count:,}", font=_font(132, bold=True), fill=INK)
    draw.text((70, 532), "incidents" + (f"  ·  {yr_range}" if yr_range else ""),
              font=_font(30), fill=MUTED)

    draw.text((64, 280),
              "Mapped to OWASP LLM Top 10 · OWASP Agentic · NIST AI RMF · MITRE ATLAS",
              font=_font(28), fill=MUTED)
    draw.text((760, 470), "open data · CC-BY-4.0", font=_font(26), fill=RUST)
    draw.text((760, 510), "emmanuelgjr.github.io/genai_incidents",
              font=_font(24), fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"[og] wrote {OUT} ({count:,} incidents)")


if __name__ == "__main__":
    main()
