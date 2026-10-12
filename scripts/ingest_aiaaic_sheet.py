"""
Ingest the public AIAAIC Repository spreadsheet.

Source: the canonical Google Sheet linked from
        https://www.aiaaic.org/aiaaic-repository
        (sheet id 1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI,
        Incidents tab gid 888071280)

AIAAIC's spreadsheet is the curated, maintainer-managed source — the
slug-style entries in ingest/aiaaic_incidents.json were hand-picked and
use vanity IDs (e.g. AIAAIC-wpp-ceo-deepfake). The sheet uses canonical
`AIAAIC{N}` integer IDs and currently lists 2,244 incidents.

Output: ingest/aiaaic_sheet_incidents.json — picked up by
scripts/merge_and_dedupe.py and deduped by AIAAIC URL when present.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingest.common import conditional_fetch  # noqa: E402


def _is_aiaaic_host(url: str) -> bool:
    """True only when the URL's host is aiaaic.org or a subdomain.

    Summary cells are untrusted upstream content; a plain substring test
    would also match e.g. https://evil.example/aiaaic.org or
    https://aiaaic.org.evil.example.
    """
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return False
    return host == "aiaaic.org" or host.endswith(".aiaaic.org")

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

SHEET_ID = "1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI"
SHEET_GID = "888071280"  # "Incidents" tab
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
    f"?format=csv&gid={SHEET_GID}"
)
CACHE_FILE = CACHE / "aiaaic_sheet.csv"

EXPECTED_COLUMNS: dict[str, list[str]] = {
    "id":          ["aiaaic id#", "#", "id"],
    "headline":    ["headline", "headline/title", "title"],
    "occurred":    ["occurred", "date"],
    "deployer":    ["deployer", "deployer(s)"],
    "developer":   ["developer", "developer(s)"],
    "system":      ["system name", "system(s)", "system"],
    "technology":  ["technology", "technology(ies)"],
    "purpose":     ["purpose", "purpose(s)"],
    "trigger":     ["news trigger (taxonomy)", "issue trigger", "trigger"],
    "ethical":     ["ethical issue (taxonomy)", "issue(s)", "ethical issue(s)", "issue"],
    "jurisdiction": ["jurisdiction", "country"],
    "sector":      ["sector", "sector(s)"],
    "harm_indiv":  ["individual", "ind. harm(s)", "individual harm(s)", "individual harm"],
    "harm_societal": ["societal", "soc. harm(s)", "societal harm(s)", "societal harm"],
    "harm_env":    ["environmental", "env. harm(s)", "environmental harm(s)", "environmental harm"],
    "consequence": ["consequence (taxonomy)", "consequence(s)", "consequence"],
    "response":    ["response (taxonomy)", "response(s)", "response"],
    "summary":     ["summary/links", "summary", "links"],
}


def build_column_map(header_rows: list[list[str]]) -> dict[str, int]:
    """Map logical column names to indices based on header rows.

    The AIAAIC CSV uses a two-row header: row 1 has the main column
    names and row 2 has sub-headers for split columns (e.g. Impacted
    area → Jurisdiction, Sector; External harm → Individual, Societal,
    Environmental).  We merge both rows so that sub-headers are found.
    """
    merged = []
    main = header_rows[0] if header_rows else []
    sub = header_rows[1] if len(header_rows) > 1 else []
    for i in range(max(len(main), len(sub))):
        m = (main[i] if i < len(main) else "").strip().lower()
        s = (sub[i] if i < len(sub) else "").strip().lower()
        merged.append(s if s else m)

    col_map: dict[str, int] = {}
    for key, aliases in EXPECTED_COLUMNS.items():
        for alias in aliases:
            if alias in merged:
                col_map[key] = merged.index(alias)
                break
        else:
            print(f"  [aiaaic] WARNING: column '{key}' not found (tried {aliases})", file=sys.stderr)
            col_map[key] = -1
    return col_map

# Security-relevant ethical-issue / news-trigger / technology values.
# We keep an entry if it touches security, privacy, or trustworthiness OR
# the technology is GenAI/agentic. AIAAIC has many fairness/bias-only
# entries that we explicitly want to exclude per the project policy.
SECURITY_ETHICAL_ISSUES = {
    "security",
    "privacy/surveillance",
    "robustness",
    "safety",
    "accountability",
    "human/civil rights",
    "child sexual abuse material",
    "misinformation",
    "disinformation",
    "deepfake",
}

# Technology keywords that automatically qualify (generative / agentic /
# LLM-adjacent capabilities — out of scope is purely-classical ML).
GENAI_TECH_KEYWORDS = (
    "generative ai",
    "large language model",
    "llm",
    "agentic",
    "voice clone",
    "voice-clone",
    "deepfake",
    "chatbot",
    "diffusion",
    "text-to-image",
    "image generation",
    "video generation",
    "code generation",
)

SECURITY_HEADLINE_KEYWORDS = (
    "deepfake jailbreak prompt injection exfiltrat ransomware phishing scam "
    "fraud breach leak hack exploit hijack rce remote code malware impersonat "
    "spoofed credential stolen unauthorized backdoor poisoning csam "
    "child sexual"
).split()

# Map AIAAIC ethical issue → OWASP LLM and ASI codes.
ETHICAL_TO_OWASP_LLM = {
    "Security": ["LLM02", "LLM04"],
    "Privacy/surveillance": ["LLM02"],
    "Accuracy/reliability": ["LLM10", "LLM07"],
    "Anthropomorphism": ["LLM07"],
    "Safety": ["LLM10"],
    "Robustness": ["LLM05", "LLM10"],
    "Transparency": ["LLM08"],
    "Accountability": ["LLM03"],
    "Misinformation": ["LLM07"],
    "Disinformation": ["LLM07"],
}
ETHICAL_TO_OWASP_ASI = {
    "Security": ["ASI02", "ASI03"],
    "Privacy/surveillance": ["ASI03"],
    "Safety": ["ASI08"],
    "Accountability": ["ASI09"],
    "Accuracy/reliability": ["ASI09"],
    "Misinformation": ["ASI09"],
    "Disinformation": ["ASI09"],
    "Anthropomorphism": ["ASI09"],
}

CONSEQUENCE_TO_SEVERITY = {
    "Loss of life": "Critical",
    "Significant financial damage": "High",
    "Litigation": "Medium",
    "System termination": "Medium",
    "Imprisonment": "Critical",
    "Injury": "High",
    "Defamation": "Medium",
}

# --- WS0-T3 (D9/D10/D11(b)) -------------------------------------------------
# AIAAIC's per-row `description` is reduced to categorical facts only
# (system/technology/sector/jurisdiction); the editorial-prose cells
# (purpose/ethical/consequence/response -- CC BY-SA-protected expression) are
# consumed transiently for classification below and written nowhere.
#
# The `ethical` cell is the one exception with a persisted trace: it is
# extracted here into a controlled-vocabulary tag list (`aiaaic_ethical_tags`)
# -- normalized categorical values drawn from AIAAIC's own closed "ethical
# issue (taxonomy)" column, never free prose -- so the label seed
# (merge_and_dedupe.py's attack_vector/corpus classifiers) can read AIAAIC's
# categorical signal without ever touching the published description text.
# See docs/audits/WS0-T3-cascade-2026-07-18.md for the failure mode this
# exists to prevent (description-text classifiers silently relabelling the
# corpus when the prose they read is cut).
AIAAIC_ETHICAL_TAG_VOCAB: dict[str, str] = {
    "security": "security",
    "privacy/surveillance": "privacy surveillance",
    "robustness": "robustness",
    "safety": "safety",
    "accountability": "accountability",
    "human/civil rights": "human civil rights",
    "child sexual abuse material": "child sexual abuse material",
    "misinformation": "misinformation",
    "disinformation": "disinformation",
    "mis/disinformation": "mis disinformation",
    "deepfake": "deepfake",
    "bias/discrimination": "bias discrimination",
    "discrimination": "discrimination",
    "bias": "bias",
    "consent": "consent",
    "employment/labour": "employment labour",
    "employment/labor": "employment labour",
    "normalisation": "normalisation",
    "normalization": "normalisation",
    "proportionality": "proportionality",
    "transparency": "transparency",
    "representation": "representation",
    "anthropomorphism": "anthropomorphism",
    "accuracy/reliability": "accuracy reliability",
    "autonomy/agency": "autonomy agency",
    "automation bias": "automation bias",
    "environment": "environment",
    "environmental": "environment",
    "sustainability": "sustainability",
    "governance": "governance",
    "legal": "legal",
    "trust": "trust",
    "wellbeing": "wellbeing",
    "manipulation": "manipulation",
    "exploitation": "exploitation",
    "unclear": "unclear",
    "appropriation": "appropriation",
    "accessibility": "accessibility",
    "authenticity/integrity": "authenticity integrity",
    "autonomous weapons": "autonomous weapons",
    "cheating/plagiarism": "cheating plagiarism",
    "plagiarism": "plagiarism",
    "competition/monopolisation": "competition monopolisation",
    "competition/monopolization": "competition monopolisation",
    "confidentiality": "confidentiality",
    "copyright": "copyright",
    "diversity/inclusivity": "diversity inclusivity",
    "dual use": "dual use",
    "dual/multi-use": "dual multi use",
    "fairness": "fairness",
    "freedom of expression": "freedom of expression",
    "human rights/civil liberties": "human rights civil liberties",
    "liability": "liability",
    "oversight": "oversight",
    "power inbalance": "power imbalance",
    "power imbalance": "power imbalance",
    "prioritisation": "prioritisation",
    "prioritization": "prioritisation",
    "privacy": "privacy",
    "revisionism": "revisionism",
    "robot rights": "robot rights",
    "alignment": "alignment",
    # Known upstream misspellings (AIAAIC's own sheet) -- mapped to the
    # correctly-spelled canonical tag rather than left to the fallback
    # slugifier, purely for classification fidelity; the fallback path below
    # would handle any of these (or a future typo) safely regardless.
    "accountabiilty": "accountability",
    "accuracy/reliabiity": "accuracy reliability",
    "accuracy/reliablity": "accuracy reliability",
    "accuracy/relibaility": "accuracy reliability",
    "appropropriation": "appropriation",
    "compeititon/monopolisation": "competition monopolisation",
    "privacy/surveillamce": "privacy surveillance",
    "privacy/surveillance/surveillance": "privacy surveillance",
    "transaprency": "transparency",
}


def normalize_ethical_tag(label: str) -> str:
    """Fallback normalizer for an ethical-issue label not in the fixed
    vocabulary above. Still a categorical slug derived only from AIAAIC's own
    taxonomy label -- never prose -- so persisting it is safe; a warning is
    printed so the vocabulary can be extended."""
    return re.sub(r"[/_]+", " ", label.strip().lower())


def aiaaic_ethical_tags(ethical_cell: str) -> list[str]:
    """Extract AIAAIC's `ethical issue (taxonomy)` cell into a controlled,
    normalized tag list -- categorical facts only, consumed internally by the
    label seed (WS0-T3 spec Sec 2(a)); never the published description, and
    never persisted as prose. Splits on ';' or ',' -- AIAAIC's sheet mixes
    both as the item separator -- but NOT '/', because '/' appears WITHIN
    compound category names (e.g. "Employment/labour", "Privacy/
    surveillance"), not between items."""
    items = [p.strip() for p in re.split(r"[;,]\s*", ethical_cell or "") if p.strip()]
    tags: list[str] = []
    for item in items:
        slug = AIAAIC_ETHICAL_TAG_VOCAB.get(item.lower())
        if slug is None:
            slug = normalize_ethical_tag(item)
            print(
                f"  [aiaaic] WARNING: ethical tag '{item}' not in controlled "
                f"vocabulary; using derived tag '{slug}'",
                file=sys.stderr,
            )
        if slug not in tags:
            tags.append(slug)
    return tags


def aiaaic_content_license() -> dict:
    """D11(b) row-level attribution/ShareAlike marker (schema shape:
    docs/specs/WS0-T3-marker-shape-2026-07-27.md). Attribution string and
    license URL verified 2026-07-27 against the live aiaaic.org/aiaaic-repository
    footer: "AIAAIC content is available to use, copy, adapt, and redistribute
    under a CC BY-SA 4.0 licence.", linking to
    creativecommons.org/licenses/by-sa/4.0/. The footer states only the
    license grant, not a separate prescribed credit line; "AIAAIC Repository"
    (the page's own title/H1) is used as the attribution name."""
    return {
        "source": "aiaaic",
        "license": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution": "AIAAIC Repository",
        "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
        "obligations": ["attribution", "share-alike"],
    }


def download_csv() -> tuple[str, bool]:
    """Fetch the sheet CSV with conditional fetch (ETag support)."""
    data, changed = conditional_fetch(CSV_URL, CACHE_FILE, min_cache_bytes=100_000)
    if not changed:
        print("[aiaaic] CSV unchanged (304), using cache")
    else:
        print(f"[aiaaic] downloaded {len(data):,} bytes -> {CACHE_FILE.name}")
    return data.decode("utf-8", errors="replace"), changed


def parse_year(occurred: str) -> int | None:
    m = re.search(r"\b(19|20)\d{2}\b", occurred or "")
    return int(m.group(0)) if m else None


def split_taxonomy(cell: str) -> list[str]:
    if not cell:
        return []
    return [p.strip() for p in re.split(r"[;,/]\s*", cell) if p.strip()]


def is_security_relevant(row: dict) -> bool:
    ethical = {e.lower() for e in split_taxonomy(row.get("ethical", ""))}
    if ethical & SECURITY_ETHICAL_ISSUES:
        return True
    headline = (row.get("headline") or "").lower()
    if any(kw in headline for kw in SECURITY_HEADLINE_KEYWORDS):
        return True
    tech = (row.get("technology") or "").lower()
    if any(kw in tech for kw in GENAI_TECH_KEYWORDS):
        # Generative/agentic tech: include even without explicit security framing
        # (downstream merge will dedupe against AIID/other sources).
        return True
    return False


def detect_attack_vector(row: dict) -> str:
    text = (
        (row.get("headline") or "")
        + " "
        + (row.get("ethical") or "")
        + " "
        + (row.get("purpose") or "")
    ).lower()
    if "deepfake" in text or "voice clone" in text:
        return "deepfake"
    if "prompt inject" in text or "jailbreak" in text:
        return "prompt-injection"
    if "exfil" in text or "data leak" in text or "data breach" in text:
        return "data-exfiltration"
    # NB: match "rce" only as a whole word — a substring check matches
    # "pe(rce)nt", "(rce)" in "reinforce/source/commerce/force", etc., and
    # mislabels harm incidents as remote-code-execution.
    if "ransom" in text or re.search(r"\brce\b", text) or "remote code" in text:
        return "rce"
    if "phishing" in text or "scam" in text or "fraud" in text or "imperson" in text:
        return "other"  # social engineering → keep generic
    if "csam" in text or "child sexual" in text:
        return "other"
    if "misinform" in text or "disinform" in text:
        return "other"
    return "other"


def detect_severity(row: dict) -> str:
    conseq = split_taxonomy(row.get("consequence", ""))
    harm_indiv = split_taxonomy(row.get("harm_indiv", ""))
    all_harms = conseq + harm_indiv
    # Walk from worst to least
    for label in ("Loss of life", "Imprisonment", "Injury",
                  "Significant financial damage", "Defamation",
                  "Litigation", "System termination"):
        if label in all_harms:
            return CONSEQUENCE_TO_SEVERITY[label]
    return "Medium"


def _cell(raw_row: list[str], col: dict[str, int], key: str) -> str:
    """Safely get a cell value by logical column name."""
    idx = col.get(key, -1)
    if idx < 0 or idx >= len(raw_row):
        return ""
    return (raw_row[idx] or "").strip()


def normalize_row(raw_row: list[str], col: dict[str, int]) -> dict | None:
    max_idx = max((v for v in col.values() if v >= 0), default=0)
    while len(raw_row) <= max_idx:
        raw_row.append("")
    row_id = _cell(raw_row, col, "id")
    if not row_id.startswith("AIAAIC"):
        return None
    if row_id == "AIAAIC ID#":
        return None

    row = {
        "id": row_id,
        "headline": _cell(raw_row, col, "headline"),
        "occurred": _cell(raw_row, col, "occurred"),
        "deployer": _cell(raw_row, col, "deployer"),
        "developer": _cell(raw_row, col, "developer"),
        "system": _cell(raw_row, col, "system"),
        "technology": _cell(raw_row, col, "technology"),
        "purpose": _cell(raw_row, col, "purpose"),
        "trigger": _cell(raw_row, col, "trigger"),
        "ethical": _cell(raw_row, col, "ethical"),
        "jurisdiction": _cell(raw_row, col, "jurisdiction"),
        "sector": _cell(raw_row, col, "sector"),
        "harm_indiv": _cell(raw_row, col, "harm_indiv"),
        "harm_societal": _cell(raw_row, col, "harm_societal"),
        "harm_env": _cell(raw_row, col, "harm_env"),
        "consequence": _cell(raw_row, col, "consequence"),
        "response": _cell(raw_row, col, "response"),
        "summary": _cell(raw_row, col, "summary"),
    }
    if not row["headline"] or len(row["headline"]) < 5:
        return None
    year = parse_year(row["occurred"])
    if not year or year < 1980 or year > 2030:
        return None
    if not is_security_relevant(row):
        return None

    ethical_items = split_taxonomy(row["ethical"])
    owasp_llm: set[str] = set()
    owasp_asi: set[str] = set()
    for item in ethical_items:
        owasp_llm.update(ETHICAL_TO_OWASP_LLM.get(item, []))
        owasp_asi.update(ETHICAL_TO_OWASP_ASI.get(item, []))

    # Headline pattern fallbacks
    h = row["headline"].lower()
    if "deepfake" in h or "voice clone" in h or "imperson" in h:
        owasp_llm.add("LLM07")
        owasp_asi.add("ASI09")
    if "prompt inject" in h or "jailbreak" in h:
        owasp_llm.add("LLM01")
        owasp_asi.add("ASI01")
    if "data leak" in h or "data breach" in h or "exfil" in h:
        owasp_llm.add("LLM02")
        owasp_asi.add("ASI03")

    affected = (row["developer"] or row["deployer"] or row["system"]).strip()
    if not affected and row["sector"]:
        affected = row["sector"]

    # The summary cell often has multiple URLs separated by spaces / newlines
    urls = re.findall(r"https?://[^\s,;]+", row["summary"])
    aiaaic_slug = None
    references = []
    for u in urls[:8]:
        u_clean = u.strip(",.;")
        is_aiaaic = _is_aiaaic_host(u_clean)
        rtype = "report" if is_aiaaic else "news"
        ref_title = "AIAAIC entry" if is_aiaaic else u_clean
        references.append({"title": ref_title, "url": u_clean, "type": rtype})
        if is_aiaaic and "/aiaaic-repository/" in u_clean:
            slug = u_clean.rstrip("/").split("/")[-1]
            aiaaic_slug = slug

    if not references:
        # Synthesise a placeholder using the canonical entry URL form.
        slug = re.sub(r"[^a-z0-9]+", "-", row["headline"].lower()).strip("-")
        references.append({
            "title": "AIAAIC entry",
            "url": f"https://www.aiaaic.org/aiaaic-repository/ai-algorithmic-and-automation-incidents/{slug}",
            "type": "report",
        })

    # WS0-T3 (D9): categorical facts only -- system/technology/sector/
    # jurisdiction. Drops AIAAIC's editorial-prose cells (purpose/ethical/
    # consequence/response, the CC BY-SA-protected expression); those cells
    # are consumed above (attack_vector/severity/OWASP detection,
    # aiaaic_ethical_tags) and written nowhere in this returned dict.
    description = (
        "AIAAIC-tracked incident. "
        + (f"System: {row['system']}. " if row["system"] else "")
        + (f"Technology: {row['technology']}. " if row["technology"] else "")
        + (f"Sector: {row['sector']}. " if row["sector"] else "")
        + (f"Jurisdiction: {row['jurisdiction']}." if row["jurisdiction"] else "")
    ).strip()

    ethical_tags = aiaaic_ethical_tags(row["ethical"])

    # WS0-T3 label-seed decoupling (spec Sec 2(a)): the classifiers' seed text
    # must come from "AIAAIC's structured cells captured at ingest, before
    # description composition" -- not from the published description string,
    # even in its new facts-only form. The kept categorical cells
    # (system/technology/sector/jurisdiction) are the SAME facts the
    # description is built from, captured here as their own internal
    # classification-seed field so the seed never has to read `description`.
    # Restores classification signal that used to reach the old merge-time
    # reclassify via the full old description string (e.g. "Technology:
    # Deepfake" driving attack_vector=deepfake) -- lost when the first cut of
    # this decoupling used aiaaic_ethical_tags alone (see
    # docs/audits/WS0-T3-cascade-2026-07-18.md and the dry-run delta that
    # caught the regression, docs/audits/WS0-T3-validation-sample-2026-07-27.md).
    seed_facts = [c for c in (row["system"], row["technology"], row["sector"], row["jurisdiction"]) if c]

    tags = ["aiaaic", "aiaaic-sheet"]
    if row["sector"]:
        tags.append("sector-" + re.sub(r"\s+", "-", row["sector"].lower()))
    if row["jurisdiction"]:
        tags.append("juris-" + re.sub(r"\s+", "-", row["jurisdiction"].lower())[:24])

    return {
        "source_id": row["id"],
        "title": row["headline"][:300],
        "date": str(year),
        "year": year,
        "category": "real-world",
        "description": description[:1500],
        "description_provenance": "original",
        "description_source": "aiaaic",
        "content_license": aiaaic_content_license(),
        "aiaaic_ethical_tags": ethical_tags,
        "aiaaic_seed_facts": seed_facts,
        "attack_vector": detect_attack_vector(row),
        "affected": affected[:200],
        "severity": detect_severity(row),
        "owasp_llm": sorted(owasp_llm),
        "owasp_asi": sorted(owasp_asi),
        "mitre_atlas": [],
        "references": references,
        "tags": tags,
    }


def main():
    body, _ = download_csv()
    rows = list(csv.reader(io.StringIO(body)))
    print(f"[aiaaic] {len(rows)} raw rows")

    col = None
    header_idx = 0
    for i, row in enumerate(rows[:5]):
        joined = " ".join(row).lower()
        if "headline" in joined or "aiaaic id" in joined:
            sub_row = rows[i + 1] if i + 1 < len(rows) else []
            col = build_column_map([row, sub_row])
            header_idx = i + 1  # skip both header rows
            break
    if col is None:
        print("[aiaaic] ERROR: could not find header row", file=sys.stderr)
        return

    out = []
    skipped = 0
    for row in rows[header_idx + 1:]:
        norm = normalize_row(row, col)
        if norm:
            out.append(norm)
        else:
            skipped += 1

    out_path = INGEST / "aiaaic_sheet_incidents.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[aiaaic] wrote {len(out)} security-relevant entries -> {out_path} (skipped {skipped})")


if __name__ == "__main__":
    main()
