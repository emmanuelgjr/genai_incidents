"""scripts/taxonomy_versions.py -- the single derivation of ``taxonomy_versions``.

One dict, derived ONLY from the pinned mapping files under ``mappings/`` (never
a literal in an exporter), so a re-pin of any taxonomy (e.g. the queued OWASP
ASI 2026 re-pin) flows into stats.json, the STIX bundle, the MISP manifest, the
Hugging Face card and the pip package without touching any of them.

    {"atlas": "2026.09", "owasp_llm": "2026", "owasp_asi": "2025",
     "capec": null, "veris": "1.4.1"}

Sources:

* atlas      -- ``mappings/mitre_atlas.json``            ``version``
* owasp_llm  -- ``mappings/owasp_llm_2025_to_2026.json`` ``to_version`` (the
                crosswalk is the single source of truth for which edition the
                corpus codes belong to; same rule as export_stix, E24/D26(c))
* owasp_asi  -- ``mappings/owasp_asi_top10.json``        ``version``
* capec      -- ``mappings/cwe_capec.json``              ``capec_version`` --
                ``null`` when the file does not record one. The CWE->CAPEC map
                predates version recording (``_source`` names the view, not a
                release), so the honest value today is ``null``, not a guess;
                ``scripts/build_cwe_capec.py`` is the place to start recording it.
* veris      -- ``mappings/veris.json``                  ``version``

Offline, stdlib-only: imported by the deterministic build.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "mappings"

# (key, file, field)
SOURCES = (
    ("atlas", "mitre_atlas.json", "version"),
    ("owasp_llm", "owasp_llm_2025_to_2026.json", "to_version"),
    ("owasp_asi", "owasp_asi_top10.json", "version"),
    ("capec", "cwe_capec.json", "capec_version"),
    ("veris", "veris.json", "version"),
)


def taxonomy_versions(mappings: Path = MAPPINGS) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for key, fname, field in SOURCES:
        raw = json.loads((mappings / fname).read_text(encoding="utf-8"))
        v = raw.get(field)
        out[key] = None if v is None else str(v)
    return out


def as_text(tv: dict[str, str | None] | None = None) -> str:
    """Human-readable single line, e.g. for the Hugging Face card."""
    tv = tv if tv is not None else taxonomy_versions()
    return ", ".join(f"{k} {v if v is not None else 'unversioned'}" for k, v in tv.items())


if __name__ == "__main__":
    print(json.dumps(taxonomy_versions(), indent=2))
