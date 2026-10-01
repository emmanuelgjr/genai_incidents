# README image sources

The images under `docs/assets/readme/` are hand-run presentation assets, not build outputs: nothing in `make build` touches them, and they carry **no corpus counts** on purpose (a count in an image can't be templated from `data/stats.json` and would drift silently).

| Image | Source | Regenerate |
|---|---|---|
| `banner-{light,dark}.svg` | hand-authored SVG | edit directly |
| `how-it-works-{light,dark}.svg` | `flow.py` | `python scripts/readme_assets/flow.py` (from repo root) |
| `taxonomy-map-{light,dark}.svg` | `tax.py` — reads INC-00924 from `data/incidents.json` | `python scripts/readme_assets/tax.py` |
| `site-search.png` | live site, via `shot.mjs` (headless Chrome over CDP) | `CLICK=".row-toggle" node scripts/readme_assets/shot.mjs "https://emmanuelgjr.github.io/genai_incidents/#q=EchoLeak" docs/assets/readme/site-search.png "#incidents-table" 1440 1100 light 24 545 82` |
| `stix-excerpt.png` | `stix.html` — a real excerpt of INC-00924 from the published STIX bundle (2026-09-30) | `node scripts/readme_assets/shot.mjs "file:///<abs path>/scripts/readme_assets/stix.html" docs/assets/readme/stix-excerpt.png "#card" 1500 1000 dark` |

The taxonomy map and STIX excerpt are labelled as of v2.10.0 / 2026-09-30. They are snapshots of one real entry, and that entry's labels can change in later builds.
