"""
Fetch all AI Incident Database incident pages in parallel, extract og:title /
og:description from the static HTML, filter for security-relevant entries, and
write them to ingest/aiid_full.json.

Each AIID page has its title and description in static HTML meta tags, so we
don't need the GraphQL API.
"""

from __future__ import annotations

import json
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT.parent / "_external"
INGEST = ROOT / "ingest"

# OECD bridge gives us dates for many AIID incidents
OECD_REL = EXTERNAL / "aiid" / "site" / "gatsby-site" / "migrations" / "data" / "oecd_relationships_2025_09_09.json"
SITEMAP_FILES = [EXTERNAL / "sitemap-0.xml", EXTERNAL / "sitemap-1.xml"]

# Security-relevant keyword filter (case-insensitive)
SECURITY_KEYWORDS = [
    "prompt injection", "prompt-injection", "jailbreak", "jailbroken",
    "deepfake", "voice clone", "voice-clone", "voice cloning",
    "data leak", "data breach", "leaked", "exposed", "exfiltrat",
    "ransomware", "phishing", "vishing", "smishing",
    "rce", "remote code execution", "command injection", "sandbox escape",
    "ssrf", "sql injection", "deserialization", "supply chain",
    "model theft", "model extraction", "membership inference",
    "adversarial", "evasion", "poisoning", "backdoor",
    "scam", "fraud", "imperson", "spoofed", "spoofing",
    "malware", "trojan", "worm", "vulnerab", "exploit",
    "hack", "hijack", "stole", "stolen", "theft",
    "unauthorized", "without consent", "without authorization",
    "credential", "password", "api key", "token",
    "agent", "autonomous", "copilot",
    "openai", "anthropic", "google ai", "gemini", "chatgpt", "claude",
    "hallucina", "misinform", "disinform",
    "election", "influence operation", "propaganda",
    "chatbot", "llm", "language model",
    "facial recognition", "face recognition",
    "surveillance", "biometric", "privacy",
    "weapon", "csam", "child sexual",
    "racist", "discriminat", "bias",
    "deepseek", "mistral", "huggingface", "hugging face",
    "killer robot", "autonomous weapon",
    "cyberattack", "cyber attack", "cybersecurity",
]


def load_aiid_urls() -> set[str]:
    urls = set()
    # First, OECD bridge has 446 AIID IDs
    if OECD_REL.exists():
        data = json.loads(OECD_REL.read_text(encoding="utf-8"))
        for row in data:
            inc_id = row.get("incident_id")
            if inc_id:
                urls.add(f"https://incidentdatabase.ai/cite/{inc_id}/")
    # Sitemaps: extract all /cite/N/ URLs
    for sm in SITEMAP_FILES:
        if sm.exists():
            text = sm.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"https://incidentdatabase\.ai/cite/(\d+)/?", text):
                urls.add(f"https://incidentdatabase.ai/cite/{m.group(1)}/")
    return urls


def fetch_one(url: str, timeout: int = 12) -> dict | None:
    inc_id_match = re.search(r"/cite/(\d+)", url)
    inc_id = inc_id_match.group(1) if inc_id_match else None
    if not inc_id:
        return None
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; genai_incidents/1.0)",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(80000).decode("utf-8", errors="replace")  # first 80KB is enough for <head>
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return None

    title_m = re.search(r'og:title"\s+content="([^"]+)"', data)
    desc_m = re.search(r'og:description"\s+content="([^"]+)"', data)
    if not title_m or not desc_m:
        return None
    title = title_m.group(1).strip()
    desc = desc_m.group(1).strip()

    # Try to extract a date from the page (look for "YYYY-MM-DD" or "Month YYYY")
    date_m = re.search(r'"incident_date":\s*"(\d{4}-\d{2}-\d{2})"', data)
    if not date_m:
        date_m = re.search(r'<meta[^>]+article:published_time"\s+content="(\d{4}-\d{2}-\d{2})', data)
    inc_date = date_m.group(1) if date_m else ""
    year = int(inc_date[:4]) if inc_date else None
    # Cap year at current year — AIID can't have published an incident from the future.
    current_year = __import__("datetime").date.today().year
    if not year:
        # Pick the earliest plausible year mentioned, ignoring future dates (e.g. "2027 election").
        years_found = [
            int(m.group(1))
            for m in re.finditer(r"\b(20[0-2]\d)\b", title + " " + desc)
            if int(m.group(1)) <= current_year
        ]
        if years_found:
            year = min(years_found)
    elif year > current_year:
        year = current_year
        inc_date = ""
    if not year:
        # Final fallback: AIID incident_id ranges (rough heuristic — first id of each year)
        # Calibrated against AIID history: id<200 mostly 2014-2020, 200-500 2021-2022, 500-1000 2022-2024, 1000+ 2024-2026
        iid = int(inc_id)
        if iid < 200:
            year = 2018
        elif iid < 500:
            year = 2022
        elif iid < 1000:
            year = 2023
        elif iid < 1300:
            year = 2024
        else:
            year = 2025

    return {
        "incident_id": int(inc_id),
        "url": url,
        "title": title,
        "description": desc,
        "date": inc_date,
        "year": year,
    }


def is_security_relevant(entry: dict) -> bool:
    text = (entry["title"] + " " + entry["description"]).lower()
    return any(kw in text for kw in SECURITY_KEYWORDS)


# --- Taxonomy mapping heuristics ---
TAXONOMY_RULES = [
    # (keyword regex, owasp_llm, owasp_asi, mitre_atlas, attack_vector)
    (r"prompt[\s-]*inject", ["LLM01"], ["ASI01"], ["AML.T0051"], "prompt-injection"),
    (r"jailbreak|jailbroken", ["LLM01"], ["ASI01"], ["AML.T0054"], "jailbreak"),
    (r"data\s+exfil|exfiltrat", ["LLM02"], ["ASI02"], ["AML.T0024", "AML.T0057"], "data-exfiltration"),
    (r"deepfake|voice clone|voice cloning|impersonat", ["LLM07"], ["ASI09"], ["AML.T0048"], "other"),
    (r"data\s+(leak|breach)|leaked.*data|exposed.*data|api\s+key", ["LLM02"], ["ASI03"], ["AML.T0057"], "data-exfiltration"),
    (r"ransom", [], ["ASI05", "ASI10"], ["AML.T0048"], "rce"),
    (r"\brce\b|remote code|command injection|sandbox escape", ["LLM10"], ["ASI05"], ["AML.T0050"], "rce"),
    (r"ssrf", ["LLM10"], ["ASI02"], ["AML.T0049"], "ssrf"),
    (r"supply chain", ["LLM04"], ["ASI04"], ["AML.T0010"], "supply-chain"),
    (r"model (theft|extract)|model extraction", ["LLM02"], [], ["AML.T0024.002"], "model-extraction"),
    (r"membership inference", ["LLM02"], [], ["AML.T0024.000"], "membership-inference"),
    (r"adversarial example|adversarial input|evasion attack|fgsm|pgd", [], [], ["AML.T0043"], "adversarial-input"),
    (r"poisoning|backdoor", ["LLM05"], ["ASI06"], ["AML.T0020", "AML.T0018"], "model-poisoning"),
    (r"hallucinat", ["LLM07"], [], ["AML.T0058"], "other"),
    (r"misinform|disinform|propaganda|influence operation", ["LLM07"], [], ["AML.T0048"], "other"),
    (r"election", ["LLM07"], [], ["AML.T0048"], "other"),
    (r"agent.*hijack|agent goal", ["LLM03"], ["ASI01"], ["AML.T0051"], "agent-hijack"),
    (r"tool.*misuse|tool.*abuse|plugin.*compromise", ["LLM03"], ["ASI02"], ["AML.T0053"], "tool-abuse"),
    (r"memory.*poison|context.*poison", ["LLM05"], ["ASI06"], ["AML.T0066"], "memory-poisoning"),
    (r"chatbot|virtual assistant", [], [], [], "other"),
    (r"copilot|autopilot", ["LLM03"], ["ASI01"], [], "other"),
    (r"surveillance|facial recogn|face recogn", [], [], ["AML.T0048"], "other"),
    (r"csam|child sexual", ["LLM07"], [], ["AML.T0048"], "other"),
    (r"scam|fraud|phishing|vishing", [], [], ["AML.T0048"], "other"),
]


def map_taxonomy(entry: dict) -> dict:
    text = (entry["title"] + " " + entry["description"]).lower()
    llm = set()
    asi = set()
    atlas = set()
    av = "other"
    for pattern, l, a, m, vec in TAXONOMY_RULES:
        if re.search(pattern, text):
            llm.update(l)
            asi.update(a)
            atlas.update(m)
            if av == "other" and vec != "other":
                av = vec
    return {
        "owasp_llm": sorted(llm),
        "owasp_asi": sorted(asi),
        "mitre_atlas": sorted(atlas),
        "attack_vector": av,
    }


def severity_for(entry: dict) -> str:
    text = (entry["title"] + " " + entry["description"]).lower()
    if any(k in text for k in ["killed", "dead", "fatal", "death", "ransom", "$1m", "millions", "billion"]):
        return "Critical"
    # D155: bare "rce" matched inside "Reinforced"/"enforcement"/"source"; whole word only.
    if any(k in text for k in ["breach", "stolen", "leaked", "remote code", "exfiltrat"]) or re.search(r"\brce\b", text):
        return "High"
    return "Medium"


def main():
    urls = sorted(load_aiid_urls(), key=lambda u: int(re.search(r"/cite/(\d+)", u).group(1)))
    print(f"AIID URLs to fetch: {len(urls)}")

    results: list[dict] = []
    errs = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(fetch_one, u): u for u in urls}
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r is None:
                errs += 1
            else:
                results.append(r)
            if i % 100 == 0:
                print(f"  fetched {i}/{len(urls)} (errors: {errs})")

    print(f"Fetched OK: {len(results)}; errors: {errs}")

    # Filter to security-relevant
    security = [r for r in results if is_security_relevant(r)]
    print(f"Security-relevant: {len(security)}")

    out = []
    for r in security:
        tx = map_taxonomy(r)
        year = r["year"] or 2024
        date_str = r["date"] or str(year)
        sev = severity_for(r)
        out.append({
            "source_id": f"AIID-{r['incident_id']}",
            "title": re.sub(r"^Incident\s+\d+:\s*", "", r["title"]).strip(),
            "date": date_str,
            "year": year,
            "category": "real-world",
            "description": r["description"][:1500],
            "attack_vector": tx["attack_vector"],
            "affected": "",
            "severity": sev,
            "owasp_llm": tx["owasp_llm"],
            "owasp_asi": tx["owasp_asi"],
            "mitre_atlas": tx["mitre_atlas"],
            "references": [
                {"title": f"AIID incident #{r['incident_id']}", "url": r["url"], "type": "report"},
            ],
            "tags": ["aiid"],
        })

    out_path = INGEST / "aiid_full.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} security-relevant AIID entries -> {out_path}")


if __name__ == "__main__":
    main()
