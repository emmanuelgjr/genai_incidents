"""
Merge legacy consolidated entries with all ingest/*.json source feeds, dedupe
by canonical reference URLs / CVE IDs / fuzzy title match, validate against the
incident schema, and emit the consolidated dataset:

  data/incidents.json        (full structured dataset)
  data/incidents.min.json    (slim version: id, title, date, taxonomy mappings)

Run after the per-source aggregators have written into ingest/.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from datetime import date, datetime, timezone
from collections import defaultdict

# Reuse the ingest layer's strict AI-package matcher so the inclusion policy
# is enforced in exactly one place (INCLUSION.md §4).
try:
    from ingest_cve_nvd_expanded import package_is_strongly_ai
except ImportError:  # pragma: no cover - script path fallback
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingest_cve_nvd_expanded import package_is_strongly_ai

_AFFECTED_SPLIT = re.compile(r"[,\s]+")


def is_out_of_scope_malware(entry: dict) -> bool:
    """An entry is out-of-scope per the inclusion policy when it is a
    malicious-package advisory whose affected package(s) do NOT strongly match
    an AI/ML/agent identifier (INCLUSION.md §3/§4). This is what purges the
    generic-npm-malware noise (chai-mocks, sudo-prompt, …) that a substring
    filter let in — including already-committed entries that retain-on-drop
    would otherwise resurrect."""
    if "malicious-package" not in (entry.get("tags") or []):
        return False
    affected = entry.get("affected") or ""
    pkgs = [p for p in _AFFECTED_SPLIT.split(affected) if p]
    if not pkgs:
        return False  # can't assess → keep (don't drop on missing data)
    return not any(package_is_strongly_ai(p) for p in pkgs)


# --- Issue #88 remediation --------------------------------------------------
# data/issue88_remediation.json records maintainer decisions for the
# high-confidence CVE-bridge over-merges surfaced by scripts/audit_cve_bridge.py.
#   exclude  primary incident is NOT GenAI (scope contamination) -> drop the
#            bucket via an out-of-scope removal. Always active; idempotent.
# The manifest's `split` section records the 19 reviewed GenAI over-merge
# decisions for the v3.0 one-way re-baseline #88 describes; the split is NOT
# executed here (un-grandfathering it live is not byte-stable — it cascades into
# unrelated merges — so it belongs in a dedicated re-baseline, not this build).
# `exclude_suppress_source_ids` is the static, enumerated key list that makes
# the exclusion idempotent. Empty manifest -> no-op -> byte-identical build.
_ISSUE88_PATH = Path(__file__).resolve().parents[1] / "data" / "issue88_remediation.json"


def _load_issue88() -> tuple[set[str], set[str]]:
    try:
        m = json.loads(_ISSUE88_PATH.read_text(encoding="utf-8"))
        return (set(m.get("exclude") or {}),
                set(m.get("exclude_suppress_source_ids") or []))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return set(), set()


ISSUE88_EXCLUDE, ISSUE88_SUPPRESS = _load_issue88()


def _is_out_of_scope(entry: dict) -> bool:
    """Malware scope gate OR an issue-#88 exclude bucket (non-GenAI product's
    CVEs bridged into one entry)."""
    return is_out_of_scope_malware(entry) or entry.get("id") in ISSUE88_EXCLUDE


_CWE_CAPEC_PATH = Path(__file__).resolve().parents[1] / "mappings" / "cwe_capec.json"

# GHSA ecosystem token -> Package-URL (purl) type. Only ecosystems with an
# official purl `type` are mapped; anything else (e.g. GitHub Actions) yields
# no purl rather than an invented identifier.
_ECO_TO_PURL = {
    "pip": "pypi", "npm": "npm", "go": "golang", "composer": "composer",
    "maven": "maven", "nuget": "nuget", "rust": "cargo", "rubygems": "gem",
    "swift": "swift", "pub": "pub", "erlang": "hex",
}
# A structured `affected` fragment looks like "<ecosystem>/<package[/subpath]>"
# (the GHSA ecosystem/name form). The package part may itself contain slashes
# (Go module paths) and a trailing version expression we strip.
_PKG_RE = re.compile(r"^([a-z][a-z0-9+.\-]*)/(.+)$")


def _load_cwe_capec() -> dict[str, list[str]]:
    """Authoritative CWE -> [CAPEC, ...] map (mappings/cwe_capec.json, built by
    scripts/build_cwe_capec.py from MITRE's CAPEC corpus). Reading the committed
    map keeps the build deterministic. Returns {} if absent."""
    try:
        raw = json.loads(_CWE_CAPEC_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw.get("cwe_to_capec", {}) if isinstance(raw, dict) else {}


def _derive_capec_ids(entry: dict, cwe_capec: dict[str, list[str]]) -> list[str]:
    """Complete CAPEC set implied by the entry's CWEs, via the authoritative
    CWE->CAPEC map. The union is faithful (not capped): a record tagged with a
    broad CWE legitimately relates to many attack patterns. Fully reconstructable
    from `cwe_ids` + mappings/cwe_capec.json — it is a denormalised convenience,
    documented in DATA_DICTIONARY.md."""
    if not cwe_capec:
        return []
    caps: set[str] = set()
    for c in entry.get("cwe_ids") or []:
        caps.update(cwe_capec.get(c, ()))
    return sorted(caps, key=lambda c: int(c.split("-")[1]))


def _affected_to_purl(fragment: str) -> str | None:
    """Convert one GHSA-style "<ecosystem>/<package>" fragment to a purl, or
    None if the ecosystem has no official purl type or the fragment isn't the
    structured form."""
    m = _PKG_RE.match(fragment.strip())
    if not m:
        return None
    ptype = _ECO_TO_PURL.get(m.group(1).lower())
    if not ptype:
        return None
    # Drop any trailing version expression ("foo < 1.2", "foo <= 1.2.1").
    name = re.split(r"\s+[<>=]", m.group(2).strip())[0].strip()
    if not name:
        return None
    if ptype == "maven" and ":" in name:  # group:artifact -> group/artifact
        ns, _, art = name.partition(":")
        name = f"{ns}/{art}"
    if ptype == "npm" and name.startswith("@"):  # scoped pkg: @scope -> %40scope
        scope, _, pkg = name[1:].partition("/")
        if pkg:
            name = f"%40{scope}/{pkg}"
    return f"pkg:{ptype}/{name}"


def _derive_purls(entry: dict) -> list[str]:
    """Package-URLs for an entry whose `affected` carries structured
    "<ecosystem>/<package>" identifiers (the GHSA/OSV form). Comma-separated
    fragments are each resolved; free-text `affected` (a product sentence) yields
    nothing. Deterministic entity-resolution anchor (INCLUSION.md coverage)."""
    aff = (entry.get("affected") or "").strip()
    if not aff:
        return []
    out: set[str] = set()
    for frag in aff.split(","):
        p = _affected_to_purl(frag)
        if p:
            out.add(p)
    return sorted(out)


def _derive_tier(entry: dict) -> str:
    """Two-tier split (INCLUSION.md §5): the curated/notable LANDMARK set vs
    the comprehensive vulnerability/advisory FEED. landmark = hand-curated, a
    real-world incident catalogued in the AI Incident Database (`aiid_id`), or
    an AI-harm case; feed = the CVE/GHSA/OSV bulk. (The `real-world` *category*
    is deliberately NOT used — it also tags exploited CVEs, which belong in the
    feed.) Headline claims should cite the landmark count, not the raw total."""
    if (entry.get("quality_tier") == "curated"
            or entry.get("aiid_id")
            or entry.get("corpus") == "ai-harm"):
        return "landmark"
    return "feed"


def _derive_confidence(entry: dict) -> str:
    """Transparent, rule-based confidence (documented in DATA_DICTIONARY.md):
      high   = curated/reviewed tier, OR 2+ distinct sources AND a CVE;
      medium = 2+ distinct sources, OR has a CVE / CVSS score;
      low    = a single auto-tier source with no CVE.
    A rule, not an opinion — disputable via the corrections process."""
    n_src = len(entry.get("source_ids") or [])
    has_cve = bool(entry.get("cve_ids"))
    has_cvss = entry.get("cvss_score") is not None
    tier = entry.get("quality_tier")
    if tier in ("curated", "reviewed") or (n_src >= 2 and has_cve):
        return "high"
    if n_src >= 2 or has_cve or has_cvss:
        return "medium"
    return "low"


def utc_today() -> date:
    """Calendar date in UTC. CI builds run in UTC; a contributor whose local
    clock lags UTC must stamp the same dates as a same-UTC-day CI build, or
    the deterministic drift check flaps."""
    return datetime.now(timezone.utc).date()

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
DATA = ROOT / "data"
MAPPINGS = ROOT / "mappings"
DATA.mkdir(parents=True, exist_ok=True)


def _load_atlas_technique_tactics() -> dict[str, list[str]]:
    """technique-id -> [tactic-id, ...] from the committed ATLAS reference."""
    try:
        m = json.loads((MAPPINGS / "mitre_atlas.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return {tid: e["tactics"] for tid, e in (m.get("techniques") or {}).items()
            if isinstance(e, dict) and e.get("tactics")}


_ATLAS_TECHNIQUE_TACTICS = _load_atlas_technique_tactics()

CANONICAL_HOSTS = {
    "nvd.nist.gov": "advisory",
    "cve.org": "advisory",
    "github.com": "advisory",
    "atlas.mitre.org": "research",
    "incidentdatabase.ai": "report",
    "avidml.org": "report",
    "owasp.org": "research",
    "genai.owasp.org": "research",
}

# Heuristic mapping for completing taxonomy mappings on incoming entries
LLM_TO_ATLAS = {
    "LLM01": ["AML.T0051"], "LLM02": ["AML.T0057"], "LLM03": ["AML.T0053"],
    "LLM04": ["AML.T0010"], "LLM05": ["AML.T0020"], "LLM06": ["AML.T0029"],
    "LLM07": ["AML.T0058"], "LLM08": ["AML.T0056"], "LLM09": ["AML.T0066"],
    "LLM10": ["AML.T0050"],
}
ASI_TO_ATLAS = {
    "ASI01": ["AML.T0051"], "ASI02": ["AML.T0053"], "ASI03": ["AML.T0012"],
    "ASI04": ["AML.T0010"], "ASI05": ["AML.T0050"], "ASI06": ["AML.T0066"],
    "ASI07": ["AML.T0053"], "ASI08": ["AML.T0048"], "ASI09": ["AML.T0048.003"],
    "ASI10": ["AML.T0048"],
}
LLM_TO_NIST = {
    "LLM01": ["MEASURE-2.7"], "LLM02": ["MEASURE-2.10"], "LLM03": ["MAP-3.5"],
    "LLM04": ["GOVERN-6.1"], "LLM05": ["MAP-4.2"], "LLM06": ["MEASURE-2.4"],
    "LLM07": ["MEASURE-2.8"], "LLM08": ["MEASURE-2.7"], "LLM09": ["MEASURE-2.7"],
    "LLM10": ["MEASURE-2.7"],
}
ASI_TO_NIST = {
    "ASI01": ["MEASURE-2.7"], "ASI02": ["MAP-3.5"], "ASI03": ["GOVERN-1.4"],
    "ASI04": ["GOVERN-6.1"], "ASI05": ["MEASURE-2.7"], "ASI06": ["MEASURE-2.7"],
    "ASI07": ["MAP-4.1"], "ASI08": ["MANAGE-4.1"], "ASI09": ["MAP-3.5"],
    "ASI10": ["GOVERN-1.4"],
}

# Seed a framework mapping from the attack_vector for entries that arrive
# with no OWASP/NIST/ATLAS at all. Security exploits (and OWASP's own
# LLM07 "Misinformation" category) map to OWASP LLM codes, which then
# cascade through fill_taxonomy() to ATLAS + NIST. Societal-harm vectors
# (privacy, bias, CSAM, self-harm) have no clean OWASP fit, so they seed
# the appropriate NIST AI RMF control directly.
_VECTOR_TO_OWASP_LLM = {
    "prompt-injection": ["LLM01"], "indirect-prompt-injection": ["LLM01"], "jailbreak": ["LLM01"],
    "data-exfiltration": ["LLM02"], "info-disclosure": ["LLM02"],
    "membership-inference": ["LLM02"], "model-inversion": ["LLM02"],
    "supply-chain": ["LLM04"],
    "model-poisoning": ["LLM05"], "memory-poisoning": ["LLM05"], "backdoor": ["LLM05"],
    "rce": ["LLM10"], "xss": ["LLM10"], "sql-injection": ["LLM10"],
    "command-injection": ["LLM10"], "ssrf": ["LLM10"], "path-traversal": ["LLM10"],
    "deserialization": ["LLM10"],
    "agent-hijack": ["LLM03"], "tool-abuse": ["LLM03"],
    "misinformation": ["LLM07"], "hallucination": ["LLM07"], "deepfake": ["LLM07"],
    "dos": ["LLM06"], "model-extraction": ["LLM06"], "model-theft": ["LLM06"],
}
_VECTOR_TO_NIST_SEED = {
    "privacy-violation": ["MAP-4.1", "MEASURE-2.10"],
    "algorithmic-bias": ["MEASURE-2.11"],
    "csam-generation": ["MEASURE-2.6"],
    "unsafe-advice": ["MEASURE-2.6"],
    "adversarial-input": ["MEASURE-2.7"],
    "evasion": ["MEASURE-2.7"],
}
_VECTOR_TO_ATLAS_SEED = {
    "adversarial-input": ["AML.T0015"],
    "evasion": ["AML.T0015"],
}


def seed_frameworks_from_vector(entry: dict) -> None:
    """Seed OWASP/NIST/ATLAS from the (finalized) attack_vector, but only for
    entries that have no framework mapping at all. Never overrides an existing
    mapping; the seeded OWASP code then cascades through fill_taxonomy()."""
    if (entry.get("owasp_llm") or entry.get("owasp_asi")
            or entry.get("mitre_atlas") or entry.get("nist_ai_rmf")):
        return
    av = (entry.get("attack_vector") or "").strip()
    llm = _VECTOR_TO_OWASP_LLM.get(av)
    if llm:
        entry["owasp_llm"] = list(llm)
    nist = _VECTOR_TO_NIST_SEED.get(av)
    if nist:
        entry["nist_ai_rmf"] = sorted(set((entry.get("nist_ai_rmf") or []) + list(nist)))
    atlas = _VECTOR_TO_ATLAS_SEED.get(av)
    if atlas:
        entry["mitre_atlas"] = sorted(set((entry.get("mitre_atlas") or []) + list(atlas)))


# WS4-T10: params that carry no identifying information — campaign/referrer
# tracking cruft appended by CMSes, email clients and ad platforms. Anything
# NOT in this set is assumed to identify the resource (e.g. CMS query-string
# article IDs like `idxno=`, `id=`, `p=`, `itemName=`, `page=`) and is KEPT
# in the dedup key. Approach (i) from the WS4-T10 brief: keep the query
# string, normalized (sorted, tracking params dropped), rather than an
# allowlist of identifying params (ii, brittle — a param an ingest source
# doesn't yet know about would silently collapse again) or refusing
# ambiguous keys outright (iii, would also refuse true duplicates that
# differ only by a tracking param). The false-merge risk this leaves is the
# SAME kind of query param appearing on both a tracking blocklist miss and
# an identifying role, which WS4-T5's later dedupe-error-rate audit
# measures — not over-engineered here.
#
# WS4-T10 BOUNCE #1 (red-reviewer, 2026-09-15) named 9 real-data blocklist
# misses. Classified against ingest/*.json evidence, each on whether the
# param disambiguates the RESOURCE or is presentational/session noise —
# not by name pattern alone, since a param name that is tracking cruft on
# one host (`category=` on a Shopware advisory-listing page, `research=`
# on an NCC Group search page — both a fixed/generic value, not a per-page
# id) could in principle be an identifying id on another. Kept where a
# clean counter-example wasn't found, per the same "assume identifying
# unless clearly not" default the blocklist itself embodies — dropping a
# borderline param is a false-merge risk (the harm this fix exists to
# close), keeping one is at worst a missed-dedup, which is the safe
# direction:
#   - `iref` (Asahi Shimbun, e.g. `?iref=ogimage_rek`) — BLOCKLIST. Constant
#     literal value across every sampled URL; the article slug in the path
#     already fully identifies the page.
#   - `edtsign`, `edtcode`, `scm` (Sohu CMS, e.g.
#     `?edtsign=...&edtcode=...&scm=10001...`) — BLOCKLIST. CMS
#     analytics/signature cruft; the numeric article id is in the path
#     (`/a/<id>_<n>`), so these add nothing identifying.
#   - `web_view` (e.g. a blog URL with `?&web_view=true`) — BLOCKLIST.
#     Presentational rendering flag. THIS is the WS4-T10 BOUNCE #1 fix:
#     its absence let a bare URL and its `?&web_view=true` twin key apart,
#     producing a false split on INC-08183 (see
#     tests/test_normalize_url_overmerge.py and the committed Phase B
#     delta) even though both reference the identical resource.
#   - Liferay portlet plumbing (e.g.
#     `p_r_p_assetEntryId=...&_com_liferay_asset_publisher_..._redirect=
#     https%3A%2F%2F...`) — the `_com_liferay_*` family is BLOCKLISTED,
#     matched by prefix since the portlet-instance id varies (57 real
#     occurrences in ingest/cve_nvd_expanded.json, e.g.
#     `_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_
#     INSTANCE_jekt_redirect`): framework session/navigation state, and the
#     `..._redirect` value is itself a huge percent-encoded return-to URL
#     that would make near-identical page fetches key apart, a
#     missed-dedup risk in the OTHER direction. `p_r_p_assetEntryId` is
#     KEPT (genuinely identifying, a per-CVE numeric id) even though it's
#     redundant with the path's own CVE slug.
#     WS4-T10 ATTEMPT 3 (advisory A2) removed the earlier `p_p_id`/
#     `p_p_lifecycle`/`p_p_state`/`p_p_mode`/`p_r_p_resetcur` entries: **0
#     occurrences anywhere in `ingest/*.json`**, so they were speculative,
#     not evidenced — this blocklist only adds params with a real sample
#     backing the call, per this comment's opening paragraph. Any of them
#     reappearing with the classic Liferay portlet-parameter shape would
#     already be covered by `_com_liferay_.*`'s prefix match if it starts
#     that way; a genuinely new, differently-named Liferay framework param
#     would need its own justified addition, not a speculative one.
#   - `category` (e.g. a Shopware docs URL) and `research` (e.g. an NCC
#     Group search URL) — KEPT. Both sampled uses are coarse/generic
#     values on index-style pages, not per-article ids, so blocklisting
#     wouldn't help disambiguate the sampled cases — but neither name is
#     implausible as a genuine per-article category id on some other CMS,
#     and no counter-example forces the call either way, so the
#     conservative default (keep, i.e. treat as potentially identifying)
#     applies per this comment's opening paragraph.
_URL_TRACKING_PARAMS = re.compile(
    r"^(utm(_[a-z]+)?|fbclid|gclid|msclkid|dclid|mc_[a-z]+|igshid|"
    r"ref_src|referrer|spm|cmpid|icid|yclid|_ga|_gl|s_cid|cmp|"
    r"iref|edtsign|edtcode|scm|web_view|"
    r"_com_liferay_.*)$",
    re.IGNORECASE,
)
# `ref` (bare) is deliberately NOT in the blocklist above (WS4-T10 BOUNCE #1
# advisory A4): on some hosts `ref=` is pure referrer tracking, but on
# others (e.g. a GitHub raw/blob URL's `?ref=<branch>`) it identifies which
# branch/tag the content came from — collapsing it would re-introduce a
# false-merge risk for the sake of deduping an ambiguous tracking param.
# Measured 0 collisions from keeping `ref` today; if that changes, prefer
# host-scoping `ref` (block it only on hosts confirmed tracking-only) over
# a blanket drop.


def normalize_url(url: str) -> str:
    """Canonicalize a reference URL into a dedup key.

    Strips scheme/``www.``/fragment/trailing-slash and lowercases the
    scheme+host+path as before, but — unlike the pre-WS4-T10 version —
    keeps the query string (sorted, with tracking params dropped) instead
    of discarding it outright. Dropping the query string entirely
    collapsed distinct CMS articles that share a path and differ only by
    an `?idxno=`/`?id=` query param onto one dedup key (E21 tripwire
    investigation, docs/audits/E21-tripwire-refresh-2026-09-14.md Finding
    8/9) — e.g. INC-00554 accreted ~100 unrelated source rows this way.

    WS4-T10 BOUNCE #1 (advisory A4): query-parameter VALUES are no longer
    lowercased (only the scheme/host/path and the parameter KEYS are) —
    some identifying values are case-significant (e.g. a mixed-case CMS
    slug or token), and folding their case was a latent false-merge risk
    of the same shape this task exists to close, just not yet observed in
    the committed corpus. See tests/test_normalize_url_overmerge.py.
    """
    if not url:
        return ""
    u = url.strip()
    u = re.sub(r"^https?://(www\.)?", "", u, flags=re.IGNORECASE)
    u = u.split("#", 1)[0]
    path, _, query = u.partition("?")
    path = path.lower().rstrip("/")
    if query:
        kept = sorted(
            (k.lower(), v) for k, v in
            (pair.split("=", 1) if "=" in pair else (pair, "")
             for pair in query.split("&") if pair)
            if not _URL_TRACKING_PARAMS.match(k)
        )
        if kept:
            return path + "?" + "&".join(f"{k}={v}" if v else k for k, v in kept)
    return path


def title_key(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t[:80]


def slug_to_id(n: int) -> str:
    return f"INC-{n:05d}"


def cve_disjoint(a: dict, b: dict) -> bool:
    """True when both entries carry CVE ids and the sets share nothing.

    Two advisories about *different* CVEs are different incidents no matter
    how similar their reference URLs or templated titles look — weak-key
    (URL / fuzzy-title) merges must never bridge them (#36). CVE-key and
    source_id-key merges are unaffected: a shared identity key implies the
    sets are not disjoint or the rows are the same upstream record.
    """
    ca, cb = set(a.get("cve_ids") or []), set(b.get("cve_ids") or [])
    return bool(ca) and bool(cb) and not (ca & cb)


_ATTACK_VECTOR_NORMALIZE: dict[str, str] = {
    "supply": "supply-chain",
    "prompt": "prompt-injection",
    "direct": "prompt-injection",
    "indirect": "indirect-prompt-injection",
    "adversarial": "adversarial-input",
    "poisoning": "model-poisoning",
    "membership": "membership-inference",
    "agent": "agent-hijack",
    "credential": "auth-bypass",
    "authentication": "auth-bypass",
    "oauth": "auth-bypass",
    "hardcoded": "auth-bypass",
    "insecure": "auth-bypass",
    "cross": "xss",
    "code": "rce",
    "fraud": "deepfake",
    "no": "other",
    "not": "other",
    "multi": "other",
    "mass": "other",
    "ai": "other",
    "data": "other",
    "self": "other",
    "real": "other",
    "harmful": "other",
    "json": "other",
    "dual": "other",
    "zero": "other",
    "training": "other",
    "autonomous": "other",
    "persistent": "other",
    "user": "other",
    "infrastructure": "other",
    "multimodal": "other",
    "corpus": "other",
    "gradual": "other",
    "design": "other",
    "documents": "other",
    "maximum": "other",
    "systemic": "other",
    "knowledge": "other",
    "mcp": "other",
    "100–256": "other",
}

# Keyword -> attack_vector classifier. Order matters: first hit wins.
# Used to replace the catch-all "other" on entries that have no explicit
# attack_vector field but whose title/description contains an obvious one.
_ATTACK_VECTOR_RULES: list[tuple[str, str]] = [
    (r"indirect[\s-]*prompt", "indirect-prompt-injection"),
    (r"prompt[\s-]*inject", "prompt-injection"),
    (r"jailbreak|jailbroken", "jailbreak"),
    (r"deepfake|voice clon|face swap|face[\s-]*generat", "deepfake"),
    (r"impersonat|fake (?:ceo|cfo|executive|employee)|vishing", "deepfake"),
    (r"command injection|cmd injection|os command", "command-injection"),
    (r"path traversal|directory traversal|\\.\\./", "path-traversal"),
    (r"\bSSRF\b|server[\s-]*side request forgery", "ssrf"),
    (r"\bSQL\b injection|sqli\b", "sql-injection"),
    (r"\bXSS\b|cross[\s-]*site scripting", "xss"),
    (r"\bRCE\b|remote code execution|sandbox escape", "rce"),
    (r"arbitrary code|code execution|arbitrary command", "rce"),
    (r"deserializ|insecure deserial", "deserialization"),
    (r"auth(?:entication|orization)? bypass|missing auth|improper auth", "auth-bypass"),
    (r"hardcoded (?:key|secret|credential|password|token)", "auth-bypass"),
    (r"data exfil|exfiltrat|data breach|data leak", "data-exfiltration"),
    (r"model theft|model extract", "model-extraction"),
    (r"model invers", "model-inversion"),
    (r"membership inference", "membership-inference"),
    (r"adversarial (?:example|input|patch|attack)|evasion attack", "adversarial-input"),
    (r"data poisoning|backdoor|model poisoning", "model-poisoning"),
    (r"memory poison|context poison|rag[\s-]*poison|corpus[\s-]*poison", "memory-poisoning"),
    (r"agent (?:goal )?hijack|goal hijack", "agent-hijack"),
    (r"tool (?:misuse|abuse)|plugin compromise", "tool-abuse"),
    (r"supply[\s-]*chain|typosquat|malicious package|dependency confusion", "supply-chain"),
    (r"denial[\s-]*of[\s-]*service|\bDoS\b|\bDDoS\b|resource[\s-]*exhaust", "dos"),
    (r"info(?:rmation)?[\s-]*disclos|sensitive data exposure", "info-disclosure"),
    (r"insider threat|insider attack", "insider"),
    (r"hallucina|confabula", "hallucination"),
    (r"misinform|disinform", "misinformation"),
    (r"phishing|spear[\s-]*phish|smishing", "phishing"),
    (r"ransomware|ransom[\s-]*attack", "ransomware"),
    (r"malware|trojan|worm", "malware"),
    (r"(?:privacy|surveillance)[\s-]*(?:violat|breach|invasion)", "privacy-violation"),
    (r"bias(?:ed)?[\s-]*(?:algorithm|model|output|decision)", "algorithmic-bias"),
    # AI-harm vectors. These run after the security rules above, so an entry
    # is only labelled with a harm vector when no security exploit matched —
    # this is what pulls the AIAAIC ai-harm corpus out of the "other" bucket.
    # Patterns are deliberately high-precision (demographic/decision context
    # for bias, generative-AI context for misinformation, etc.) so a fuzzy
    # keyword in a description doesn't mislabel a record.
    (r"\bcsam\b|\bcsae\b|child sexual abuse|child (?:porn|sexual abuse)"
     r"|sexualis\w+ (?:a |the )?(?:child|minor)"
     r"|ai[\s-]generated .{0,20}(?:child|minor).{0,12}(?:sexual|porn|nude|abuse)"
     r"|generat\w+ .{0,24}child (?:porn|sexual)"
     r"|nudif\w+ .{0,20}(?:child|minor|student|girl|teen)"
     r"|(?:sexual|nude|explicit|pornographic) .{0,30}minors?\b"
     r"|minors?\b.{0,20}(?:sexual abuse|sexual image|explicit image|nude image|porn)",
     "csam-generation"),
    (r"\bsuicid\w+|self[\s-]harm|encourag\w+ .{0,20}(?:suicide|self-harm|kill)"
     r"|incit\w+ .{0,20}(?:self-harm|violence|suicide|terror)|bomb[\s-]?making"
     r"|how to (?:make|build|create|synthesize) .{0,20}(?:bomb|weapon|explosive|nerve agent|meth)"
     r"|coach\w* .{0,15}suicide|promot\w+ .{0,10}(?:suicide|self-harm|eating disorder)",
     "unsafe-advice"),
    (r"deepfake|voice clon\w+|face[\s-]?swap\w*|nudif\w+"
     r"|ai[\s-]generated (?:nude|porn|explicit|intimate|sexual)"
     r"|synthetic (?:nude|porn|intimate)"
     r"|non[\s-]consensual (?:intimate|sexual|nude|porn)|fake nude",
     "deepfake"),
    (r"facial recognition|mass surveillance"
     r"|biometric (?:surveillance|tracking|database|data|privacy|information)"
     r"|covert(?:ly)? .{0,12}(?:record|track|monitor|surveil)|location tracking"
     r"|scrap\w+ .{0,24}(?:faces|photos|profiles|personal data|biometric)"
     r"|secretly (?:record|collect|track|monitor)|invasive .{0,10}surveillance",
     "privacy-violation"),
    (r"\b(?:racial|racism|gender|sexis\w+|ethnic|caste|religious|disabilit\w+|\bage\b|demographic) "
     r"(?:bias|discriminat\w+|stereotyp\w+)"
     r"|discriminat\w+ (?:against|based on|toward|by)|biased against"
     r"|\bbias(?:ed)?\b.{0,30}(?:hiring|recruit|loan|credit|sentenc|arrest|police|policing|grading|admission|healthcare|transplant|welfare|mortgage|housing|insurance)"
     r"|perpetuat\w+ .{0,18}(?:racial|gender|sexis|racis|stereotype|inequal)",
     "algorithmic-bias"),
    (r"defam\w+|\blibel\w*|\bslander"
     r"|fabricat\w+ .{0,20}(?:quote|stor|claim|source|case|citation|legal)"
     r"|false (?:legal )?citation|hallucinat\w+ .{0,20}(?:case|citation|source|legal)"
     r"|made[\s-]up .{0,12}(?:case|citation|legal)"
     r"|(?:chatbot|chatgpt|\bai\b|\bllm\b|gemini|copilot|\bbard\b|grok) .{0,40}(?:false (?:claim|information|accusation)|spread\w* (?:false|misinfo))",
     "misinformation"),
]


_VALID_SEVERITIES = ("Critical", "High", "Medium", "Low", "Info")


# Sources we consider "auto-ingested" — present in bulk feeds but not
# individually vetted by a maintainer. Anything else (legacy/, hand-curated
# JSON, researcher-blog ingest) starts as "reviewed".
def _classify_quality_tier(entry: dict) -> str:
    """Heuristic quality tier:

      - ``curated``  — legacy hand-written entries (always source_id LEGACY-*),
        or entries with a populated `mitigations` list and >=2 source_ids.
      - ``reviewed`` — sourced from a maintained research catalogue
        (ATLAS, AIID hand-pick, OWASP, AVID, AIRI, researcher blogs), a
        hand-picked AIAAIC slug entry, or an NVD-analyst-scored CVE.
      - ``auto``     — bulk-ingested from the NVD CVE feed (unscored), the
        AIAAIC numeric sheet, OECD AIM, promptfoo, or garak.
    """
    src_ids = entry.get("source_ids") or []
    if any(s.startswith("LEGACY-") for s in src_ids):
        return "curated"
    if entry.get("mitigations") and len(src_ids) >= 2:
        return "curated"
    has_curated_source = any(
        s.startswith(("ATLAS-", "AIID-", "AVID-", "OWASP-", "RES-", "EXT-", "OECD-",
                      "USENIX-", "NDSS-", "CCS-", "ARXIV-", "INC-", "VTR-"))
        for s in src_ids
    )
    # Hand-picked AIAAIC entries use slug IDs (AIAAIC-<slug>); the bulk sheet
    # uses numeric IDs (AIAAIC<n>). Only the numeric bulk form is "auto".
    has_aiaaic_slug = any(re.match(r"^AIAAIC-[a-z]", s) for s in src_ids)
    if has_curated_source or has_aiaaic_slug:
        return "reviewed"
    # NVD assigns CVSS/CWE to CVEs — that analyst scoring is catalogue review,
    # so a CVSS-scored CVE is "reviewed". Unscored/raw CVE pulls stay "auto".
    if any(s.startswith("CVE-") for s in src_ids) and entry.get("cvss_score") is not None:
        return "reviewed"
    has_bulk = any(
        s.startswith(("OECD-AIM-", "CVE-", "PROMPTFOO-", "GARAK-")) or re.match(r"^AIAAIC\d", s)
        for s in src_ids
    )
    if has_bulk:
        return "auto"
    return "reviewed"


# Tag rules that move an entry to the `ai-harm` corpus instead of the
# default `security` corpus. The split is deliberate: a deepfake fraud is
# `security`; a hiring-algorithm-discriminates story is `ai-harm`.
_AI_HARM_KEYWORDS = (
    "discriminat", "racial bias", "gender bias", "hiring algorithm",
    "wrongful arrest", "wrongful denial", "credit scoring", "welfare benefit",
    "social scoring", "predictive policing", "biased recommendation",
    "biased recidivism", "biased loan", "biased medical", "algorithmic bias",
    "fairness", "demographic parity",
)
_SECURITY_KEYWORDS_FOR_CORPUS = (
    "deepfake", "voice clone", "voice-clone", "prompt inject", "jailbreak",
    "exfil", "data breach", "data leak", "rce", "remote code execution",
    "command injection", "ssrf", "supply chain", "supply-chain", "csam",
    "malware", "ransomware", "phishing", "scam", "fraud", "exploit", "cve-",
    "vulnerability", "auth bypass", "sandbox escape", "poisoning", "backdoor",
)


def _aiaaic_seed_text(entry: dict) -> str | None:
    """Text used for keyword-based label derivation (attack_vector reclassify,
    corpus classification), for AIAAIC-origin entries only.

    WS0-T3 spec Sec 2(a) label-seed decoupling: for `description_source ==
    "aiaaic"` entries, reads TWO structured fields captured at ingest, before
    description composition -- `aiaaic_seed_facts` (system/technology/sector/
    jurisdiction, the same kept categorical cells the reduced description is
    built from) and `aiaaic_ethical_tags` (the normalized ethical-issue
    vocabulary) -- NEVER the published `description` string itself, in either
    its old prose form or its new facts-only form. That is deliberate even
    though the new `description` is safe content: the seed must not depend on
    the *composed* description in any form, so a future formatting change to
    that string can never silently move a label. This coupling is exactly
    what silently relabelled 372 AIAAIC entries when the description was
    first reduced (docs/audits/WS0-T3-cascade-2026-07-18.md): the classifiers
    below used to read the published description, which used to carry
    AIAAIC's Ethical issues/Purpose prose verbatim.

    `aiaaic_seed_facts` was added after an ethical-tags-only first cut of this
    function (2026-07-27) caused a *second*, narrower regression, caught by
    the WS0-T3 Phase-A dry-run delta preview before any batch ran: the old
    merge-time reclassify picked up keyword signal from the System/Technology/
    Sector/Jurisdiction facts sentences embedded in the old (pre-reduction)
    description text -- e.g. "Technology: Deepfake" driving
    attack_vector=deepfake -- which the ethical-tags-only seed dropped
    entirely, silently downgrading attack_vector/OWASP/ATLAS/NIST/corpus for
    103+ entries with no dropped-prose involved at all. See
    docs/audits/WS0-T3-validation-sample-2026-07-27.md for the full
    before/after evidence.

    Returns None for non-AIAAIC entries so callers fall back to their
    existing title+description behavior unchanged."""
    if entry.get("description_source") != "aiaaic":
        return None
    facts = " ".join(entry.get("aiaaic_seed_facts") or [])
    tags = " ".join(entry.get("aiaaic_ethical_tags") or [])
    return (facts + " " + tags).strip()


def _classify_corpus(entry: dict) -> str:
    """`security` or `ai-harm`. Security wins ties — a deepfake scam is
    a security incident even if it also has a fairness angle."""
    if entry.get("cve_ids"):
        return "security"
    seed_text = _aiaaic_seed_text(entry)
    desc_text = seed_text if seed_text is not None else (entry.get("description") or "")
    text = (
        (entry.get("title") or "")
        + " "
        + desc_text
        + " "
        + " ".join(entry.get("tags") or [])
    ).lower()
    has_security = any(kw in text for kw in _SECURITY_KEYWORDS_FOR_CORPUS)
    if has_security:
        return "security"
    has_harm = any(kw in text for kw in _AI_HARM_KEYWORDS)
    if has_harm:
        return "ai-harm"
    return "security"


def _normalise_severity(value: object) -> str:
    """Coerce assorted severity inputs (None, 'None', '', invalid strings)
    into a schema-valid value. Defaults to Medium."""
    if value is None:
        return "Medium"
    s = str(value).strip().capitalize()
    if s in _VALID_SEVERITIES:
        return s
    return "Medium"


def classify_attack_vector(text: str) -> str | None:
    """Return the first matching attack vector keyword, or None."""
    if not text:
        return None
    lower = text.lower()
    for pattern, vec in _ATTACK_VECTOR_RULES:
        if re.search(pattern, lower, re.I):
            return vec
    return None


# CVE-style titles like "A flaw has been found in X." get rewritten when we
# can identify the affected product + a vulnerability class. The full
# original sentence stays in the description.
_CVE_TITLE_PREFIXES = (
    "A flaw has been found in ",
    "A vulnerability has been found in ",
    "A vulnerability was detected in ",
    "A security flaw has been discovered in ",
    "A security flaw has been found in ",
    "A weakness has been identified in ",
    "A weakness was discovered in ",
)


def maybe_rewrite_cve_title(entry: dict) -> None:
    """Rewrite generic CVE/product-blurb titles into '<product> — <vector> (CVE-...)'.

    Handles two common shapes coming out of NVD/GHSA:
      1. "A flaw has been found in X up to 3.4."   → boilerplate prefix
      2. "X is an open-source Python package..."    → product description blurb
    A single canonical title makes title-key dedup actually work for the
    same-product/same-year cluster of CVEs.
    """
    title = (entry.get("title") or "").strip()
    cve_ids = entry.get("cve_ids") or []
    cve_suffix = f" ({cve_ids[0]})" if cve_ids else ""
    vec = entry.get("attack_vector") or "other"
    if vec == "other":
        vec = classify_attack_vector(entry.get("description") or title) or "vulnerability"
    pretty_vec = vec.replace("-", " ").title()

    body: str | None = None

    # Shape 1: boilerplate CVE prefix.
    for p in _CVE_TITLE_PREFIXES:
        if title.startswith(p):
            body = title[len(p):]
            break

    # Shape 2: "<Product> is a/an <description>." — extract the product name.
    if body is None:
        m = re.match(
            r"^([A-Za-z0-9@/_+.\-]{2,40}(?:\s+[A-Za-z0-9@/_+.\-]{1,20}){0,3})\s+is\s+(?:a|an|the)\s+",
            title,
        )
        if m and cve_ids:
            # Only rewrite product blurbs when we have a CVE to anchor on —
            # otherwise we'd be inventing a vague title with no provenance.
            body = m.group(1)
            entry["title"] = f"{body.strip()} — {pretty_vec}{cve_suffix}"[:200]
            return

    if body is None:
        return

    product = re.split(
        r"\s+up to\s+|\s+versions? prior to\s+|\s+before\s+|[.,;]", body, maxsplit=1
    )[0].strip()
    if not product or len(product) > 80:
        return
    entry["title"] = f"{product} — {pretty_vec}{cve_suffix}"[:200]


def fill_taxonomy(entry: dict) -> dict:
    """Backfill MITRE ATLAS / NIST mappings if missing but OWASP codes present."""
    atlas = set(entry.get("mitre_atlas") or [])
    nist = set(entry.get("nist_ai_rmf") or [])
    for c in entry.get("owasp_llm", []) or []:
        for t in LLM_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in LLM_TO_NIST.get(c, []):
            nist.add(n)
    for c in entry.get("owasp_asi", []) or []:
        for t in ASI_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in ASI_TO_NIST.get(c, []):
            nist.add(n)
    entry["mitre_atlas"] = sorted(atlas)
    entry["nist_ai_rmf"] = sorted(nist)
    # Derive ATLAS tactics from the (final) technique set — subtechniques
    # (AML.Txxxx.yyy) inherit their parent technique's tactics.
    tactics = set(entry.get("mitre_atlas_tactics") or [])
    for t in atlas:
        tac = _ATLAS_TECHNIQUE_TACTICS.get(t)
        if not tac and t.count(".") >= 2:  # subtechnique AML.Txxxx.yyy -> parent
            tac = _ATLAS_TECHNIQUE_TACTICS.get(t.rsplit(".", 1)[0])
        if tac:
            tactics.update(tac)
    if tactics:
        entry["mitre_atlas_tactics"] = sorted(tactics)
    return entry


def normalize_entry(raw: dict) -> dict | None:
    """Coerce a raw ingest entry into the unified schema."""
    if not raw:
        return None

    # references is required
    refs = raw.get("references") or []
    refs = [r for r in refs if r and (r.get("url") or "").startswith("http")]
    if not refs:
        return None

    def _clean(s: str) -> str:
        """Strip stray carriage returns and collapse runs of whitespace.
        Some NVD CVE descriptions carry literal ``\\r\\n`` sequences from
        the source HTML; keeping them produces mixed line endings in the
        rendered markdown and confuses the CI drift check."""
        return re.sub(r"\s+", " ", (s or "").replace("\r", " ")).strip()

    title = _clean(raw.get("title"))
    if len(title) < 5:
        return None

    desc = _clean(raw.get("description"))
    if len(desc) < 20:
        # tolerate short descriptions by padding from title+impact
        desc = _clean(desc + " " + (raw.get("impact") or "") + " " + title)
        if len(desc) < 20:
            return None

    # Normalize OWASP codes
    llm = [c[:5] for c in (raw.get("owasp_llm") or []) if isinstance(c, str) and c.upper().startswith("LLM")]
    asi = [c[:5] for c in (raw.get("owasp_asi") or []) if isinstance(c, str) and c.upper().startswith("ASI")]
    llm = sorted(set(c.upper() for c in llm if re.match(r"^LLM\d{2}$", c.upper())))
    asi = sorted(set(c.upper() for c in asi if re.match(r"^ASI\d{2}$", c.upper())))

    year = raw.get("year")
    if not year:
        m = re.match(r"(\d{4})", str(raw.get("date") or ""))
        if m:
            year = int(m.group(1))
    if not year:
        return None

    cves = raw.get("cve_ids") or []
    if isinstance(cves, str):
        cves = [cves]
    if "cve_id" in raw and raw["cve_id"]:
        cves = list(cves) + [raw["cve_id"]]
    cves = sorted(set(c for c in cves if isinstance(c, str) and re.match(r"^CVE-\d{4}-\d{4,9}$", c)))

    # source IDs may arrive as a single `source_id` string OR as a
    # `source_ids` array (some ingest scripts emit multiple upstream IDs
    # per row, e.g. OECD AIM rows that cross-reference AIID).
    src_ids: list[str] = []
    if raw.get("source_id"):
        src_ids.append(raw["source_id"])
    if isinstance(raw.get("source_ids"), list):
        src_ids.extend(s for s in raw["source_ids"] if isinstance(s, str))
    if isinstance(raw.get("extra_source_ids"), list):
        src_ids.extend(s for s in raw["extra_source_ids"] if isinstance(s, str))
    # Canonicalise: `AIID-1234-OECD` (from the legacy OECD bridge file) and
    # `AIID-1234` (from scrape_aiid + ingest_oecd_aim) reference the same
    # AIID incident — collapse to a single canonical form so dedup matches.
    src_ids = [
        re.sub(r"^AIID-(\d+)-OECD$", r"AIID-\1", s) for s in src_ids
    ]

    raw_vec = (raw.get("attack_vector") or "").lower().strip()
    raw_vec = _ATTACK_VECTOR_NORMALIZE.get(raw_vec, raw_vec)
    if not raw_vec or raw_vec == "other":
        # WS0-T3 label-seed decoupling (spec Sec 2(a)): AIAAIC-origin entries
        # classify from the structured `aiaaic_ethical_tags` seed, never the
        # published `description` -- see _aiaaic_seed_text.
        seed_text = _aiaaic_seed_text(raw)
        classify_text = (title or "") + " " + (seed_text if seed_text is not None else (desc or ""))
        classified = classify_attack_vector(classify_text)
        if classified:
            raw_vec = classified
        else:
            raw_vec = "other"

    entry = {
        "id": "",  # assigned later
        "source_ids": sorted(set(src_ids)),
        "title": title,
        "date": raw.get("date") or str(year),
        "year": int(year),
        "category": raw.get("category") or "real-world",
        "description": desc,
        "attack_vector": raw_vec,
        "affected": (raw.get("affected") or "").strip(),
        "severity": _normalise_severity(raw.get("severity")),
        "owasp_llm": llm,
        "owasp_asi": asi,
        "nist_ai_rmf": sorted(set(raw.get("nist_ai_rmf") or [])),
        "mitre_atlas": sorted(set(raw.get("mitre_atlas") or [])),
        "references": refs,
        "tags": list(raw.get("tags") or []),
        # added/updated stamped in main() after dedupe, using the previous
        # output as the source of truth for `added` so CI runs stay stable.
        "added": raw.get("added") or "",
        "updated": raw.get("updated") or "",
    }
    if cves:
        entry["cve_ids"] = cves
    cwes_raw = raw.get("cwe_ids") or raw.get("cwe") or []
    if isinstance(cwes_raw, str):
        cwes_raw = [cwes_raw]
    cwes = sorted(
        {
            c.upper()
            for c in cwes_raw
            if isinstance(c, str) and re.match(r"^CWE-\d{1,4}$", c.upper())
        }
    )
    if cwes:
        entry["cwe_ids"] = cwes
    if raw.get("cvss_score"):
        try:
            entry["cvss_score"] = float(raw["cvss_score"])
        except (TypeError, ValueError):
            pass
    if isinstance(raw.get("cvss_vector"), str) and raw["cvss_vector"].startswith("CVSS:"):
        entry["cvss_vector"] = raw["cvss_vector"]
    # Surface the canonical AIID numeric id as a first-class field when we
    # have one (either explicitly, or parsed from an AIID-<n> source_id).
    aiid_id = raw.get("aiid_id")
    if not aiid_id:
        for sid in src_ids:
            m = re.match(r"^AIID-(\d+)$", sid)
            if m:
                aiid_id = int(m.group(1))
                break
    if aiid_id:
        try:
            entry["aiid_id"] = int(aiid_id)
        except (TypeError, ValueError):
            pass
    if isinstance(raw.get("disclosure_date"), str) and re.match(
        r"^\d{4}(-\d{2}(-\d{2})?)?$", raw["disclosure_date"]
    ):
        entry["disclosure_date"] = raw["disclosure_date"]
    if raw.get("mitigations"):
        entry["mitigations"] = raw["mitigations"]
    if raw.get("impact"):
        entry["impact"] = raw["impact"]
    if raw.get("maestro_layers"):
        entry["maestro_layers"] = raw["maestro_layers"]
    if raw.get("owasp_dsgai"):
        entry["owasp_dsgai"] = raw["owasp_dsgai"]
    if raw.get("mitre_atlas_tactics"):
        entry["mitre_atlas_tactics"] = raw["mitre_atlas_tactics"]
    # WS0-T3 (D9/D11(b)): description provenance/source + the row-level
    # attribution/ShareAlike marker. All three are set at a single ingest
    # code path (ingest_aiaaic_sheet.py) and excluded from merge_into's key
    # lists by omission, so they stay sticky to whichever entry survives as
    # the dedup target — same mechanism as description itself (spec Sec 3).
    if raw.get("description_provenance"):
        entry["description_provenance"] = raw["description_provenance"]
    if raw.get("description_source"):
        entry["description_source"] = raw["description_source"]
    if raw.get("content_license"):
        entry["content_license"] = raw["content_license"]
    # E21/WS4 OECD-reduction corpus decoupling (2026-07-30): `corpus` IS a
    # real schema field (unlike aiaaic_ethical_tags/aiaaic_seed_facts below),
    # so unlike those two this needs no strip-before-output step -- only this
    # pass-through. Without it, a source-set `corpus` was silently discarded
    # here (the whitelist above has no `corpus` key) and step 5's `if not
    # e.get("corpus")` guard (~:1442) recomputed it from `description` on
    # every build -- exactly the coupling that already relabelled 372 AIAAIC
    # entries once (WS0-T3-cascade-2026-07-18.md) and was live for OECD
    # (ingest_oecd_aim.py::classify_corpus_signal() now sets it from a
    # derived security/ai-harm signal, never the narrative text itself; see
    # docs/audits/E21-oecd-narrative-licence-2026-07-30.md §5.1). Validated
    # against the schema enum here so a malformed value fails loudly at
    # validate() rather than reaching the same guard's else-branch silently.
    if raw.get("corpus") in ("security", "ai-harm"):
        entry["corpus"] = raw["corpus"]
    # `aiaaic_ethical_tags` / `aiaaic_seed_facts` are INTERNAL classification-
    # seed fields only — neither has a schema entry and both must never reach
    # data/incidents.json (root schema is additionalProperties:false). They
    # ride the entry through dedupe/merge with the same sticky-by-omission
    # semantics as the fields above, and are stripped in main() right before
    # the output is assembled (see the `deduped = surviving` stripping loop).
    if raw.get("aiaaic_ethical_tags"):
        entry["aiaaic_ethical_tags"] = raw["aiaaic_ethical_tags"]
    if raw.get("aiaaic_seed_facts"):
        entry["aiaaic_seed_facts"] = raw["aiaaic_seed_facts"]

    fill_taxonomy(entry)
    maybe_rewrite_cve_title(entry)
    return entry


def load_source(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: failed to parse {path}: {e}")
        return []
    if isinstance(data, dict):
        return data.get("incidents") or data.get("entries") or data.get("data") or []
    if isinstance(data, list):
        return data
    return []


DEPRECATIONS_PATH = DATA / "id_deprecations.json"
CURATION_OVERRIDES_PATH = DATA / "curation_overrides.json"
CISA_KEV_PATH = INGEST / "cisa_kev.json"
CWE_VECTOR_PATH = MAPPINGS / "cwe_attack_vector.json"
SOURCE_FRESHNESS_PATH = DATA / "source_freshness.json"
# WS4-T19: the pre-authorization guard's input. A committed, docs/-only
# list (never data/, never schema/) of which previously-single published
# ids are authorized to newly resolve to more than one row on the
# transition that lands WS4-T10's normalize_url fix. See
# docs/audits/WS4-T19-split-evidence-2026-09-18.md and
# docs/audits/WS4-T19-authorized-splits-2026-09-18.json (the file this
# constant points at).
SPLIT_AUTHORIZATION_PATH = ROOT / "docs" / "audits" / "WS4-T19-authorized-splits-2026-09-18.json"
# WS4-T21 / board decision D28: the ONLY board decision this guard accepts
# as authorization. A guard that treats the authorized list's mere
# presence-on-main as consent is not a guard -- the list was committed
# BEFORE the ruling and is read by filename, so once both the list and
# the WS4-T10 fix are on main, a filename-only check is already satisfied
# for the very transition it exists to gate (red-reviewer's finding on
# WS4-T19, carried into D28's board record). The list must therefore
# carry an explicit `authorization` marker naming this exact decision id,
# and the entries it approved must hash-match the entries actually
# present -- see `_verify_split_authorization_marker`.
REQUIRED_SPLIT_AUTHORIZATION_DECISION = "D28"


def load_cwe_vector_map() -> dict[str, str]:
    """CWE id -> attack_vector for entries stuck at "other".

    Only unambiguous CWE classes are listed (see the mapping's ``_doc``); the
    caller must apply the unanimity rule — reclassify only when every mappable
    CWE on the entry agrees on a single vector.
    """
    if not CWE_VECTOR_PATH.exists():
        return {}
    data = json.loads(CWE_VECTOR_PATH.read_text(encoding="utf-8"))
    return data.get("cwe_to_vector", {})


def vector_from_cwes(cwe_ids: list[str] | None, cwe_map: dict[str, str]) -> str | None:
    """Return the unanimous vector for the entry's CWEs, else None."""
    if not cwe_ids or not cwe_map:
        return None
    vectors = {cwe_map[c] for c in set(cwe_ids) if c in cwe_map}
    if len(vectors) == 1:
        return next(iter(vectors))
    return None


def _load_cisa_kev() -> dict[str, dict]:
    """Load the committed CISA KEV snapshot as ``{cve_id: {dateAdded,
    knownRansomwareCampaignUse}}``. Reading the committed snapshot (refreshed
    by the data workflows) rather than the live CISA feed keeps the build
    deterministic. Returns ``{}`` if the snapshot is absent."""
    if not CISA_KEV_PATH.exists():
        return {}
    try:
        raw = json.loads(CISA_KEV_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw.get("vulnerabilities", {}) if isinstance(raw, dict) else {}


def _load_curation_overrides() -> dict[str, dict]:
    """Load explicit, durable curation decisions keyed by source_id.

    Format: ``{"overrides": {"<source_id>": {"quality_tier": "reviewed",
    "severity": "High", "_note": "..."}, ...}}``. These are human/assisted
    review decisions that override the heuristic classifiers and survive
    rebuilds. Keys starting with ``_`` (e.g. ``_note``) are metadata and are
    not written onto the entry.
    """
    if not CURATION_OVERRIDES_PATH.exists():
        return {}
    try:
        raw = json.loads(CURATION_OVERRIDES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw.get("overrides", {}) if isinstance(raw, dict) else {}


def _load_source_freshness_registry() -> dict[str, dict]:
    """Load the published source-freshness registry (data/source_freshness.json),
    keyed by source slug -> its record (``status``, ``last_success``,
    ``row_marker``, ...). Same class of input as ``_load_curation_overrides()``:
    curated, hand-authored, reviewed, read by the build, written by nothing
    (D8; see docs/specs/D8-source-freshness-2026-07-29.md).

    Deliberately never reads ``ingest/_state/source_health.json`` instead:
    on a `main` checkout that counter is stale by design (D5), so deriving
    freshness from it here would republish a deliberately-stale artifact as
    current on every build — the exact failure class this registry exists
    to close. Returns ``{}`` if the registry is absent or malformed, which
    degrades to "mark nothing" rather than failing the build.
    """
    if not SOURCE_FRESHNESS_PATH.exists():
        return {}
    try:
        raw = json.loads(SOURCE_FRESHNESS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw.get("sources", {}) if isinstance(raw, dict) else {}


def _load_prev_incidents() -> list[dict]:
    """Read the previously-published incidents list (empty if none yet)."""
    prev_path = DATA / "incidents.json"
    if not prev_path.exists():
        return []
    try:
        data = json.loads(prev_path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return data.get("incidents", []) if isinstance(data, dict) else []


def _load_deprecated_ids() -> set[str]:
    """Ids that were explicitly retired via merge/dedupe. These must never be
    resurrected by retention."""
    if not DEPRECATIONS_PATH.exists():
        return set()
    try:
        deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return set()
    if not isinstance(deprec, dict):
        return set()
    return {d.get("from") for d in deprec.get("deprecations", []) if d.get("from")}


def load_retained_priors(
    prev_incidents: list[dict], deprecated_ids: set[str]
) -> list[dict]:
    """Return previously-published incidents eligible for retention: all priors
    that have an id and were NOT explicitly deprecated. This applies only the
    deprecation filter; the caller (the step 6c top-up in main) decides which of
    these the fresh build no longer covers and appends those verbatim."""
    out: list[dict] = []
    for e in prev_incidents:
        eid = e.get("id")
        if not eid or eid in deprecated_ids:
            continue
        out.append(e)
    return out


def _load_prev_state() -> tuple[
    dict[str, tuple[str, str, dict]],
    dict[str, str],
    int,
]:
    """Read the previous output so the build can:

      - Preserve `added` and gate `updated` (timestamps).
      - Reuse stable `id` strings via CVE / source_id keys.
      - Carry the monotonic ID counter forward so freshly-introduced rows
        get IDs above every ID we've ever used.

    Returns ``(timestamps, id_by_key, next_id)``.
    """
    timestamps: dict[str, tuple[str, str, dict]] = {}
    id_by_key: dict[str, str] = {}
    next_id = 1
    prev_path = DATA / "incidents.json"
    if not prev_path.exists():
        return timestamps, id_by_key, next_id
    try:
        prev = json.loads(prev_path.read_text(encoding="utf-8")).get("incidents", [])
    except (json.JSONDecodeError, OSError):
        return timestamps, id_by_key, next_id
    seen_ids = set()
    for e in prev:
        added = e.get("added") or ""
        updated = e.get("updated") or added
        snap = _content_snapshot(e)
        eid = e.get("id", "")
        if eid:
            seen_ids.add(eid)
            for c in e.get("cve_ids") or []:
                id_by_key.setdefault(c, eid)
            for s in e.get("source_ids") or []:
                id_by_key.setdefault(s, eid)
        if not added:
            continue
        for c in e.get("cve_ids") or []:
            timestamps.setdefault(c, (added, updated, snap))
        for s in e.get("source_ids") or []:
            timestamps.setdefault(s, (added, updated, snap))
    # Also walk previously-tombstoned IDs so we never accidentally reuse one.
    if DEPRECATIONS_PATH.exists():
        try:
            deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8"))
            for dep in deprec.get("deprecations", []):
                seen_ids.add(dep.get("from", ""))
        except (json.JSONDecodeError, OSError):
            pass
    max_n = 0
    for i in seen_ids:
        m = re.match(r"^INC-(\d+)$", i)
        if m:
            max_n = max(max_n, int(m.group(1)))
    next_id = max_n + 1
    return timestamps, id_by_key, next_id


# Backwards-compatibility shim — earlier code paths read just the timestamps.
def _load_prev_timestamps() -> dict[str, tuple[str, str, dict]]:
    return _load_prev_state()[0]


# Fields that count as "content" for the purposes of bumping `updated`.
# `references` is intentionally included so that gaining a new news link
# bumps the timestamp, but `added`/`updated` themselves obviously do not.
_CONTENT_FIELDS = (
    "title", "date", "year", "category", "description", "attack_vector",
    "affected", "impact", "reversibility_class", "discovery_method", "severity",
    "owasp_llm", "owasp_asi", "owasp_dsgai",
    "nist_ai_rmf", "mitre_atlas", "mitre_atlas_tactics", "cve_ids", "cwe_ids",
    "cvss_score", "cvss_vector", "aiid_id", "disclosure_date",
    "exploited_in_wild", "kev_date_added",
    "mitigations", "references", "tags",
)


def _content_snapshot(entry: dict) -> dict:
    """Return a hashable-equivalent snapshot of the entry's content fields."""
    snap = {}
    for k in _CONTENT_FIELDS:
        v = entry.get(k)
        if isinstance(v, list):
            # Sort lists so cosmetic reordering doesn't bump updated.
            try:
                snap[k] = sorted(
                    v,
                    key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False),
                )
            except TypeError:
                snap[k] = v
        else:
            snap[k] = v
    return snap


# OECD AIM (oecd.ai/en/incidents/<slug>) attribution -- E21 §5.3
# (docs/audits/E21-oecd-narrative-licence-2026-07-30.md, "owed regardless of
# how the narrative question resolves"). OECD's own general Data-reuse
# clause conditions reuse of its structural facts on a citation in the
# format `OECD (year), (dataset name), (data source) DOI or URL (accessed
# on (date))` -- see docs/SOURCE_LICENSES.md §1.5. Two separate regexes,
# deliberately: `_OECD_PAGE_URL_RE` alone decides whether a reference IS an
# OECD AIM page (broad -- any oecd.ai/en/incidents/ URL, robust to a future
# slug-format change on OECD's end); `_OECD_PAGE_URL_DATE_RE` only refines
# the citation's `year` when today's YYYY-MM-DD-prefixed slug is present,
# falling back to the entry's own `year` field otherwise -- a row is never
# silently skipped just because its slug doesn't parse. The per-slug date is
# preferred over the entry's own `year` when available because a single
# surviving entry can carry more than one oecd.ai page reference (67
# measured in the committed corpus, e.g. INC-07482 absorbing three distinct
# OECD-AIM source rows via a shared AIID cross-reference) and each page's
# own date is the more accurate one to cite for THAT link, not whichever
# date the merge picked for the entry as a whole.
_OECD_PAGE_URL_RE = re.compile(r"^https://oecd\.ai/en/incidents/")
_OECD_PAGE_URL_DATE_RE = re.compile(r"^https://oecd\.ai/en/incidents/(\d{4})-\d{2}-\d{2}-")


def _oecd_citation_title(url: str, fallback_year, accessed_on: str) -> str:
    m = _OECD_PAGE_URL_DATE_RE.match(url)
    year = int(m.group(1)) if m else fallback_year
    return f"OECD ({year}), AI Incidents and Hazards Monitor, {url} (accessed on {accessed_on})"


def _apply_oecd_attribution(entry: dict) -> None:
    """Retitle every oecd.ai AIM page reference already on this entry, in
    place, to OECD's specified citation string -- never append a NEW
    reference pointing at the same URL. Two reasons, not one:

    1. `merge_into()`'s own reference union (below) dedupes by URL (a dict
       keyed on `normalize_url`, last write wins) -- a second reference
       entry citing the identical oecd.ai URL is not guaranteed to survive
       a future cross-entry merge, silently collapsing back to whichever of
       the two titles happened to iterate last. Retitling the ONE reference
       that already carries that URL sidesteps the collision structurally,
       not by observation of today's merge order.
    2. `render_markdown.py`'s "Cite this incident" line reads
       `references[0]` -- but the OECD page reference is NOT always at
       index 0 (measured: 3,667/3,829 OECD-AIM-sourced entries; the other
       162 were merged into an AIID entry whose own citation link claimed
       slot 0 first -- see the E23 AIID-attribution measurement this must
       not perturb). Matching by URL, not position, finds the right
       reference either way and never reorders the list.

    Deliberately gated on URL pattern alone, not on `OECD-AIM-` appearing in
    `source_ids`: `ingest_external.py::ingest_aiid_oecd_bridge()` also
    places an oecd.ai page URL directly onto AIID entries it cross-links
    (source_id `AIID-<id>-OECD`, canonicalised to `AIID-<id>` and merged
    into the AIID entry proper) without ever adding an `OECD-AIM-` source
    id -- gating on `source_ids` would silently miss those. `entry["added"]`
    (this project's own first-ingest date, already committed for every
    existing row and stamped once, immutably, for a brand-new one -- never
    "today" as a per-run recomputation) is the `(accessed on (date))` value:
    the one committed, deterministic fact this pipeline holds for when it
    actually pulled the page, satisfying the "must come from committed
    data, never invented at build/migrate time" constraint. Called from
    `_apply_history()`, immediately after `entry["added"]` is set and before
    `_content_snapshot()` is taken, so the retitled reference is exactly
    what gets compared against the previous build's snapshot -- one
    deliberate `updated` bump per row the first time this runs, then stable
    forever after (the same `added` value regenerates the same title on
    every subsequent rebuild)."""
    accessed_on = entry.get("added")
    if not accessed_on:
        return
    for r in entry.get("references") or []:
        if isinstance(r, dict) and _OECD_PAGE_URL_RE.match(r.get("url") or ""):
            r["title"] = _oecd_citation_title(r["url"], entry.get("year"), accessed_on)
            r["type"] = "reference"


def _apply_history(entry: dict, prev_ts: dict[str, tuple[str, str, dict]]) -> None:
    """Look up the entry's previous timestamps by any matching CVE/source ID
    and apply them. Bump `updated` only when content actually changed."""
    today = str(utc_today())
    keys = list(entry.get("cve_ids") or []) + list(entry.get("source_ids") or [])
    prev = next((prev_ts[k] for k in keys if k in prev_ts), None)
    if prev is None:
        # Brand-new row — stamp it with today's date.
        entry["added"] = entry.get("added") or today
        entry["updated"] = today
        _apply_oecd_attribution(entry)
        return
    prev_added, prev_updated, prev_snap = prev
    entry["added"] = prev_added
    _apply_oecd_attribution(entry)
    if _content_snapshot(entry) == prev_snap:
        entry["updated"] = prev_updated
    else:
        entry["updated"] = today


def dedupe_entries(
    all_entries: list[dict],
    prior_id_by_key: dict[str, str] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Dedupe normalized entries (first hit wins: CVE > source_id > URL >
    fuzzy title ±1 year). Returns ``(surviving, tombstoned)`` — tombstoned
    entries were transitively absorbed into a survivor during reindexing.

    Every index hit and every transitive claim is resolved through
    ``_live`` so a merge can never target a tombstoned entry: content
    merged into a dead entry would be silently dropped with it (see
    docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md).

    Weak keys (URL / fuzzy title) refuse to merge two entries whose CVE
    sets are disjoint (#36) — UNLESS both sides already co-resided in the
    same previously-published entry (``prior_id_by_key``: cve/source_id →
    previous INC id). The grandfather clause keeps rebuilds of committed
    data byte-stable; only *new* URL/title bridges are blocked."""
    prior_id_by_key = prior_id_by_key or {}

    def _same_prior(a: dict, b: dict) -> bool:
        ka = list(a.get("cve_ids") or []) + list(a.get("source_ids") or [])
        kb = list(b.get("cve_ids") or []) + list(b.get("source_ids") or [])
        ia = {prior_id_by_key[k] for k in ka if k in prior_id_by_key}
        if not ia:
            return False
        ib = {prior_id_by_key[k] for k in kb if k in prior_id_by_key}
        return bool(ia & ib)
    by_cve: dict[str, dict] = {}
    by_url: dict[str, dict] = {}
    by_title: dict[str, dict] = {}
    by_src: dict[str, dict] = {}
    deduped: list[dict] = []

    def _live(entry: dict) -> dict:
        """Follow ``_merged_into`` links from a tombstoned entry to the live
        entry that absorbed it (cycle-guarded)."""
        seen: set[int] = set()
        while entry.get("_tombstoned") and id(entry) not in seen:
            seen.add(id(entry))
            absorber = entry.get("_merged_into")
            if absorber is None:
                break
            entry = absorber
        return entry

    def _reindex(target: dict) -> None:
        """Refresh every dedup index for ``target`` after a merge. If a key
        (CVE / source_id / reference URL) already maps to a *different*
        previously-deduped entry, that other entry is transitively absorbed
        into ``target`` and tombstoned so we don't end up with two records
        for what is really one incident.

        Claims loop until ``target``'s key set stops changing: merge_into
        reassigns the key lists, so keys absorbed from a claimed entry
        mid-pass would otherwise never be re-pointed at ``target`` and
        would keep referencing the tombstoned entry."""

        def _claim(idx: dict, key: str, weak: bool = False) -> None:
            other = idx.get(key)
            if other is None:
                idx[key] = target
                return
            other = _live(other)
            if other is target or other.get("_tombstoned"):
                idx[key] = target
                return
            if weak and cve_disjoint(target, other) and not _same_prior(target, other):
                # Shared weak key (reference URL) between entries with
                # disjoint CVE sets — different incidents. Leave the key
                # with its first owner instead of bridging them (#36).
                return
            # Transitive merge: pull other's content into target and retire it.
            merge_into(target, other)
            other["_tombstoned"] = True
            other["_merged_into"] = target
            idx[key] = target

        while True:
            cves = list(target.get("cve_ids") or [])
            srcs = list(target.get("source_ids") or [])
            urls = [normalize_url(r.get("url", ""))
                    for r in target.get("references", []) or []]
            for c in cves:
                _claim(by_cve, c)
            for s in srcs:
                _claim(by_src, s)
            for u in urls:
                if u:
                    _claim(by_url, u, weak=True)
            unchanged = (
                list(target.get("cve_ids") or []) == cves
                and list(target.get("source_ids") or []) == srcs
                and [normalize_url(r.get("url", ""))
                     for r in target.get("references", []) or []] == urls
            )
            if unchanged:
                break

    for e in all_entries:
        # CVE-key dedupe (strongest signal)
        cve_keys = e.get("cve_ids") or []
        cve_hit = next((by_cve[c] for c in cve_keys if c in by_cve), None)
        if cve_hit:
            cve_hit = _live(cve_hit)
            merge_into(cve_hit, e)
            _reindex(cve_hit)
            continue
        # Source-ID dedupe (e.g. AIID-1234 referenced from both AIID scrape
        # and OECD AIM's aiid_ids cross-reference).
        src_keys = e.get("source_ids") or []
        src_hit = next((by_src[s] for s in src_keys if s in by_src), None)
        if src_hit:
            src_hit = _live(src_hit)
            merge_into(src_hit, e)
            _reindex(src_hit)
            continue
        # URL-key dedupe. A URL hit is refused when the CVE sets are
        # disjoint and the pair isn't grandfathered (#36) — keep scanning,
        # another reference may point at the right entry.
        url_hit = None
        for r in e.get("references", []):
            u = normalize_url(r.get("url", ""))
            if u and u in by_url:
                candidate = _live(by_url[u])
                if not cve_disjoint(candidate, e) or _same_prior(candidate, e):
                    url_hit = candidate
                    break
        if url_hit:
            merge_into(url_hit, e)
            _reindex(url_hit)
            continue
        # Title-key dedupe. _reindex never updates by_title, so resolve the
        # hit (and refresh the pointer) before the year check — the stale
        # pointer was the original trigger for the tombstone-merge bug.
        tk = title_key(e["title"])
        if tk in by_title:
            title_hit = _live(by_title[tk])
            by_title[tk] = title_hit
            if abs(title_hit["year"] - e["year"]) <= 1 and (
                    not cve_disjoint(title_hit, e) or _same_prior(title_hit, e)):
                merge_into(title_hit, e)
                _reindex(title_hit)
                continue

        # New entry
        deduped.append(e)
        _reindex(e)
        by_title.setdefault(tk, e)

    # Split out entries that got transitively absorbed during reindex.
    # _merged_into holds object references (cyclic) — strip before the
    # entries are serialized.
    surviving: list[dict] = []
    tombstones: list[dict] = []
    for e in deduped:
        e.pop("_merged_into", None)
        if e.pop("_tombstoned", False):
            tombstones.append(e)
        else:
            surviving.append(e)
    return surviving, tombstones


class SplitAuthorizationError(SystemExit):
    """Raised by :func:`_check_split_authorization` to abort the build
    BEFORE any output file is written. Subclasses SystemExit so a plain
    ``make build`` run stops with a nonzero exit and the message below,
    without a Python traceback obscuring it."""


def _entries_sha256(entries: list[dict]) -> str:
    """Canonical (sort_keys, no whitespace) sha256 of an `entries` array,
    so the hash is stable regardless of formatting and detects ANY change
    to the approved content -- added, removed, or edited entries alike."""
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _verify_split_authorization_marker(data: dict, path: Path) -> bool:
    """WS4-T21 / D28: a guard that authorizes on file-presence alone is
    not a guard (see REQUIRED_SPLIT_AUTHORIZATION_DECISION's comment).
    Requires an `authorization` object naming EXACTLY the board decision
    that ruled on this list, plus a content hash proving the `entries`
    array is byte-for-byte what that decision approved. Fails closed
    (returns False, never raises) on every deviation:
      - no `authorization` key at all (an unmarked list),
      - `authorization.decision` missing or naming a different decision,
      - `authorization.entries_sha256` missing or not matching a fresh
        hash of this file's own `entries` array (entries edited, added,
        or removed after the marker was written -- including the case
        where someone bumps `entries_sha256` to match tampered entries
        without a NEW dated board decision approving the new content,
        which this check cannot distinguish from a legitimate re-ruling
        and does not try to -- that distinction is the board's job, not
        this function's; this function's job is only to refuse an
        entries/marker mismatch).
    Prints a specific reason to stderr in every failure case so a bad
    marker is diagnosable, not just silently empty."""
    auth = data.get("authorization")
    if not isinstance(auth, dict):
        print(
            f"[split-guard] {path.name} carries no `authorization` marker "
            "-- file presence alone does not authorize any split.",
        )
        return False
    decision = auth.get("decision")
    if decision != REQUIRED_SPLIT_AUTHORIZATION_DECISION:
        print(
            f"[split-guard] {path.name}'s authorization marker names "
            f"decision {decision!r}, not the required "
            f"{REQUIRED_SPLIT_AUTHORIZATION_DECISION!r} -- refusing to "
            "authorize any split.",
        )
        return False
    expected_hash = auth.get("entries_sha256")
    actual_hash = _entries_sha256(data.get("entries", []))
    if not expected_hash or expected_hash != actual_hash:
        print(
            f"[split-guard] {path.name}'s authorization marker's "
            f"entries_sha256 ({expected_hash!r}) does not match a fresh "
            f"hash of its own `entries` array ({actual_hash!r}) -- the "
            "approved entries and the entries on disk have diverged; "
            "refusing to authorize any split.",
        )
        return False
    return True


def _load_split_authorization(path: Path) -> set[str]:
    """Read the WS4-T19 pre-authorization list's `from` ids, gated on the
    D28 authorization marker (`_verify_split_authorization_marker`).
    Missing file, unparseable JSON, or a marker that fails verification
    all mean "nothing is authorized" (the safe default: a guard that
    treats a missing/corrupt/unmarked allowlist as authorizing everything
    is not a guard) -- returns an empty set, not an exception, so a build
    with zero detected splits (today's normal case, pre-WS4-T10-merge)
    never even looks at this file's presence."""
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if not _verify_split_authorization_marker(data, path):
        return set()
    return {
        e.get("from") for e in data.get("entries", []) if e.get("from")
    }


def _check_split_authorization(
    prev_id_by_key: dict[str, str],
    deduped: list[dict],
    authorized_path: Path = SPLIT_AUTHORIZATION_PATH,
) -> None:
    """WS4-T19 build-time pre-authorization guard.

    Aborts LOUDLY, before any output file is written (call this before
    step 8's `id_deprecations.json` write and step 9's `incidents.json`
    write), if this build's own dedupe logic would cause a previously
    single PUBLISHED id's member keys (the union of `source_ids` +
    `cve_ids` it held in the last committed build) to newly resolve onto
    MORE THAN ONE row of `deduped` -- i.e. would silently produce a
    `split`/`resplit`-shaped change -- unless that id is present in the
    authorized list at `authorized_path` (the `from` field of a
    docs/-committed, human-reviewed, PROPOSED list; see
    docs/audits/WS4-T19-split-evidence-2026-09-18.md and D25(b): the user
    rules on the list, not this function).

    This is the mechanical form of D25(a) condition (2) and the
    "deliberate guard" named in board entry `8d1b241f` / WS4-T15 spec §7(b)
    -- until now the project had three ACCIDENTAL barriers (a mis-keyed
    curation override that made `validate.py` fail closed, CI running
    `make build` before `validate.py`, and nothing else) and no
    DELIBERATE one. Name the input that makes this fail: any build whose
    dedupe output would split a previously-single published id's own
    historical member keys across >1 new row, where that id is NOT on the
    authorized list -- including the empty-list case (nothing is
    authorized) and the case where exactly one of several detected splits
    is missing from an otherwise-complete list (this function reports
    every unauthorized id, not just the first, so a partially-correct list
    cannot hide behind an early return).
    """
    new_key_to_id: dict[str, str] = {}
    for e in deduped:
        eid = e.get("id")
        if not eid:
            continue
        for k in list(e.get("source_ids") or []) + list(e.get("cve_ids") or []):
            new_key_to_id[k] = eid

    split_map: dict[str, set[str]] = {}
    for key, old_id in prev_id_by_key.items():
        new_id = new_key_to_id.get(key)
        if new_id is None:
            continue
        split_map.setdefault(old_id, set()).add(new_id)
    detected_splits = {
        old_id: ids for old_id, ids in split_map.items() if len(ids) > 1
    }
    if not detected_splits:
        return

    authorized = _load_split_authorization(authorized_path)
    unauthorized = {
        old_id: ids for old_id, ids in detected_splits.items()
        if old_id not in authorized
    }
    if not unauthorized:
        print(
            f"[split-guard] {len(detected_splits)} previously-single "
            f"published id(s) resolve to >1 row this build; all are on "
            f"the authorized list ({authorized_path.name}) -- proceeding."
        )
        return

    lines = [
        "[split-guard] ABORT: this build would silently split "
        f"{len(unauthorized)} previously-single PUBLISHED id(s) into "
        "more than one row, and no authorization for them was found at "
        f"{authorized_path}.",
        "No output file was written.",
        "",
        "Unauthorized split(s) detected (old id -> new row ids):",
    ]
    for old_id in sorted(unauthorized):
        new_ids = sorted(unauthorized[old_id])
        shown = new_ids[:8]
        suffix = f" ... (+{len(new_ids) - 8} more)" if len(new_ids) > 8 else ""
        lines.append(f"  - {old_id} -> {shown}{suffix}  ({len(new_ids)} rows)")
    lines.append("")
    lines.append(
        "This is the WS4-T19 pre-authorization guard (D25(b): the user "
        "rules on which splits are authorized for a one-time transition; "
        "the build never decides this for itself). Authorizing a split "
        "requires BOTH an entry ({\"from\": \"<old-id>\", \"reason\": "
        "\"<...>\"} in " + str(authorized_path) + ") AND a valid "
        f"`authorization` marker naming decision "
        f"{REQUIRED_SPLIT_AUTHORIZATION_DECISION!r} whose entries_sha256 "
        "matches the file's own entries -- file presence alone does not "
        "authorize anything (see _verify_split_authorization_marker). "
        "See docs/audits/WS4-T19-split-evidence-2026-09-18.md and D28 "
        "in PROGRESS.md."
    )
    raise SplitAuthorizationError("\n".join(lines))


def main():
    # 0) Load the previous output: timestamps, the id-by-key map (so stable
    #    INC-* IDs survive a rebuild), and the monotonic ID counter.
    prev_ts, prev_id_by_key, next_id = _load_prev_state()

    all_entries: list[dict] = []

    # 1) Legacy consolidated first (highest priority — already curated)
    legacy_path = DATA / "legacy_consolidated.json"
    if not legacy_path.exists() and os.environ.get("MERGE_ALLOW_MISSING_LEGACY") != "1":
        # WS4-T10 build guard. This used to silently proceed without the
        # legacy corpus, which is exactly how the E21 tripwire audit's first
        # rebuild delta went wrong: run standalone (skipping
        # parse_existing.py, which regenerates this gitignored file — see
        # `make merge`), it produced a corpus 5,675 rows short with
        # fabricated severity regressions that were reported as real
        # (docs/audits/E21-tripwire-refresh-2026-09-14.md Finding 3). Fail
        # loudly instead of yielding a materially wrong corpus with no
        # indication anything is missing.
        raise SystemExit(
            f"[FATAL] {legacy_path} not found.\n"
            "merge_and_dedupe.py must run after `python scripts/parse_existing.py`\n"
            "(which regenerates this gitignored file), not standalone — see\n"
            "`make merge` / Makefile:11-13. Running it alone silently drops the\n"
            "legacy corpus and yields a materially wrong build.\n"
            "If this is deliberate (e.g. a test harness building its own tmp\n"
            "corpus from ingest/ alone), set MERGE_ALLOW_MISSING_LEGACY=1."
        )
    if legacy_path.exists():
        legacy = json.loads(legacy_path.read_text(encoding="utf-8")).get("incidents", [])
        # Legacy already in unified shape — backfill taxonomy and stamp a
        # synthetic source_id on entries that never had one (table-parsed
        # rows from the original markdown trackers).
        for e in legacy:
            fill_taxonomy(e)
            if not e.get("source_ids"):
                slug = e.get("id") or e.get("title", "legacy")
                e["source_ids"] = [f"LEGACY-{slug}"]
            maybe_rewrite_cve_title(e)
        all_entries.extend(legacy)
        print(f"[legacy] loaded {len(legacy)} entries")

    # 2) Each ingest/*.json (from subagents)
    if INGEST.exists():
        for src in sorted(INGEST.glob("*.json")):
            raw = load_source(src)
            kept = []
            for r in raw:
                norm = normalize_entry(r)
                if norm is not None:
                    kept.append(norm)
            all_entries.extend(kept)
            print(f"[{src.name:40s}] {len(raw):4d} raw -> {len(kept):4d} normalized")

    # 3+4) Dedupe; entries transitively absorbed during reindexing come back
    #      as tombstones so their old IDs can be recorded for citation
    #      resolution below.
    #      Issue #88 exclude: drop out-of-scope source records (non-GenAI
    #      buckets' enumerated keys) BEFORE dedupe, so those buckets never form
    #      and cannot resurrect on rebuild once their merged entry is gone. The
    #      key list is static (captured in the manifest), so this is idempotent.
    if ISSUE88_SUPPRESS:
        _before = len(all_entries)
        all_entries = [e for e in all_entries
                       if not ((set(e.get("source_ids") or []) | set(e.get("cve_ids") or []))
                               & ISSUE88_SUPPRESS)]
        print(f"[issue88-exclude] suppressed {_before - len(all_entries)} "
              f"out-of-scope source record(s) across {len(ISSUE88_EXCLUDE)} bucket(s)")

    surviving, tombstones = dedupe_entries(all_entries, prev_id_by_key)
    today_str = str(utc_today())

    # 4b) Finalize attack_vector (normalize fragments + reclassify "other")
    #     BEFORE stamping history. attack_vector is part of the content
    #     snapshot, so finalizing it afterwards would make _apply_history
    #     compare a stale value against the previous output and spuriously
    #     bump `updated` (and therefore `generated`) on every rebuild —
    #     breaking the drift check whenever CI runs on a later calendar day.
    cwe_vector_map = load_cwe_vector_map()
    cwe_reclassified = 0
    for e in surviving:
        vec = (e.get("attack_vector") or "other").lower().strip()
        vec = _ATTACK_VECTOR_NORMALIZE.get(vec, vec)
        if not vec or vec == "other":
            # WS0-T3 label-seed decoupling (spec Sec 2(a)) — see _aiaaic_seed_text.
            seed_text = _aiaaic_seed_text(e)
            classify_text = (e.get("title") or "") + " " + (
                seed_text if seed_text is not None else (e.get("description") or "")
            )
            classified = classify_attack_vector(classify_text)
            vec = classified or "other"
        if vec == "other":
            # Text gave nothing — fall back to unanimous CWE evidence
            # (mappings/cwe_attack_vector.json; mixed signals stay "other").
            from_cwe = vector_from_cwes(e.get("cwe_ids"), cwe_vector_map)
            if from_cwe:
                vec = from_cwe
                cwe_reclassified += 1
        e["attack_vector"] = vec
    if cwe_reclassified:
        print(f"[cwe-vector] reclassified {cwe_reclassified} 'other' entries "
              "from unanimous CWE evidence")

    # 4c) Backfill framework mappings for entries that arrived with no
    #     OWASP/NIST/ATLAS at all, seeding from the now-final attack_vector
    #     (then cascading OWASP -> ATLAS/NIST via fill_taxonomy). Runs before
    #     history stamping so the seeded mappings are part of the snapshot.
    for e in surviving:
        seed_frameworks_from_vector(e)
        fill_taxonomy(e)

    # 4d) Apply curation overrides (durable human/assisted review decisions)
    #     before history stamping, so overridden content fields are part of
    #     the snapshot and an override-set quality_tier is respected in step 5.
    curation = _load_curation_overrides()
    if curation:
        applied = 0
        for e in surviving:
            ov = next((curation[s] for s in (e.get("source_ids") or []) if s in curation), None)
            if ov:
                for k, v in ov.items():
                    if not k.startswith("_"):
                        e[k] = v
                applied += 1
        print(f"[curation] applied {applied} override(s) from {CURATION_OVERRIDES_PATH.name}")

    # 4e) Flag CISA KEV (known-exploited) CVEs from the committed snapshot.
    #     Content fields, so set before history stamping. Deterministic:
    #     reads the snapshot, never the live CISA feed.
    kev = _load_cisa_kev()
    if kev:
        flagged = 0
        for e in surviving:
            matches = [kev[c] for c in (e.get("cve_ids") or []) if c in kev]
            if matches:
                e["exploited_in_wild"] = True
                # Earliest KEV listing date among the entry's CVEs.
                dates = sorted(m.get("dateAdded", "") for m in matches if m.get("dateAdded"))
                if dates:
                    e["kev_date_added"] = dates[0]
                flagged += 1
        print(f"[cisa-kev] flagged {flagged} incident(s) as exploited-in-the-wild")

    # 5) Apply stable timestamps + classifiers (quality_tier, corpus).
    for e in surviving:
        _apply_history(e, prev_ts)
        # Respect any explicit value the source carried; only classify
        # when the entry doesn't already declare one.
        if not e.get("quality_tier"):
            e["quality_tier"] = _classify_quality_tier(e)
        if not e.get("corpus"):
            e["corpus"] = _classify_corpus(e)

    # 6) Assign stable INC-* IDs. Reuse the previous ID for any entry whose
    #    CVE / source_id appeared before; otherwise allocate from the
    #    monotonic counter that survives across builds.
    # WS4-T15 item 3: capture retired IDs' own `source_ids`/`cve_ids` as of
    # the LAST committed build, so a `merged`/`transitive-merge` deprecation
    # can carry what the retired id actually held at retirement time. Without
    # this, verifying a redirect later requires manual git archaeology (the
    # WS4-T10 unmerge design's own audit had to do exactly that for 8 ids;
    # 280 further `merged` records have no other way to recover it at all).
    # Read once, from the same previously-published `incidents.json` that
    # `_load_prev_state`/`prev_id_by_key` above are already derived from.
    prev_by_id: dict[str, dict] = {
        p["id"]: p for p in _load_prev_incidents() if p.get("id")
    }

    def _retired_fields(old_id: str) -> dict:
        """Best-effort snapshot of `old_id`'s own source_ids/cve_ids from the
        last committed build, for a deprecation record's `retired_source_ids`
        / `retired_cve_ids`. Empty dict (no fields added) if `old_id` wasn't
        in the previous build at all -- this must never invent data."""
        prev = prev_by_id.get(old_id)
        if prev is None:
            return {}
        out: dict = {}
        src = sorted(set(prev.get("source_ids") or []))
        cve = sorted(set(prev.get("cve_ids") or []))
        if src:
            out["retired_source_ids"] = src
        if cve:
            out["retired_cve_ids"] = cve
        return out

    deprecations_new: list[dict] = []
    used_ids: set[str] = set()
    for e in surviving:
        keys = list(e.get("cve_ids") or []) + list(e.get("source_ids") or [])
        old_id = next((prev_id_by_key[k] for k in keys if k in prev_id_by_key), None)
        # If multiple previous IDs collide into one new row, keep the
        # smallest and record the rest as deprecations pointing at the
        # survivor — this protects citations of merged-away IDs.
        ids_seen = sorted({prev_id_by_key[k] for k in keys if k in prev_id_by_key})
        chosen = ids_seen[0] if ids_seen else None
        if chosen and chosen not in used_ids:
            e["id"] = chosen
            used_ids.add(chosen)
        else:
            e["id"] = slug_to_id(next_id)
            used_ids.add(e["id"])
            next_id += 1
        for extra in ids_seen[1:]:
            if extra != e["id"]:
                deprecations_new.append(
                    {"from": extra, "into": e["id"], "reason": "merged", "date": today_str,
                     **_retired_fields(extra)}
                )

    # 6b) Record entries that lost a fight to a transitive merge.
    for ts_entry in tombstones:
        # Find which surviving entry absorbed it via shared CVE/source_id.
        keys = list(ts_entry.get("cve_ids") or []) + list(ts_entry.get("source_ids") or [])
        target_id = next(
            (s["id"] for s in surviving if (set(s.get("cve_ids") or []) | set(s.get("source_ids") or [])) & set(keys)),
            None,
        )
        if not target_id:
            continue
        old_id = next((prev_id_by_key[k] for k in keys if k in prev_id_by_key), None)
        if old_id and old_id != target_id:
            deprecations_new.append(
                {"from": old_id, "into": target_id, "reason": "transitive-merge", "date": today_str,
                 **_retired_fields(old_id)}
            )

    # 6c) Retention top-up: restore previously-published incidents that the
    #     fresh build no longer covers (their upstream source dropped them), so
    #     the dataset is archival and never silently loses an incident. A prior
    #     is restored only if it was not explicitly deprecated AND none of its
    #     source_ids / cve_ids are already represented in the fresh build. It is
    #     carried VERBATIM — keeping its id / added / updated and bypassing
    #     dedupe — because re-feeding already-built records through the
    #     raw-ingest dedupe is non-idempotent (it re-canonicalises and can
    #     oscillate). See docs/superpowers/specs/2026-06-01-retain-on-drop-design.md
    # 6a) Scope purge: drop out-of-scope malicious-package entries (failed the
    #     inclusion policy) from freshly-built survivors. Dropped SILENTLY here —
    #     these carry ephemeral, build-local IDs, so recording deprecations from
    #     them is non-deterministic. Stable removal deprecations are derived
    #     below (step 6f) purely from previously-published data vs the final
    #     output. Also bars retention (below) from resurrecting committed noise.
    purged_scope = 0
    kept_surviving = [e for e in surviving if not _is_out_of_scope(e)]
    purged_scope += len(surviving) - len(kept_surviving)
    surviving = kept_surviving

    covered_keys: set[str] = set()
    for e in surviving:
        covered_keys.update(e.get("cve_ids") or [])
        covered_keys.update(e.get("source_ids") or [])
    eligible = load_retained_priors(_load_prev_incidents(), _load_deprecated_ids())
    carried = 0
    no_keys = 0
    for prior in eligible:
        pid = prior.get("id")
        # Never retain an entry the inclusion policy now excludes.
        if _is_out_of_scope(prior):
            purged_scope += 1
            continue
        keys = set(prior.get("cve_ids") or []) | set(prior.get("source_ids") or [])
        if not keys:
            # No source_id/cve_id anchor → can't test coverage. This should
            # never happen for committed output (normalize_entry rejects keyless
            # rows), so surface it loudly rather than dropping it silently.
            no_keys += 1
            continue
        if (keys & covered_keys) or pid in used_ids:
            continue
        prior["source_status"] = "retained"  # carried after all sources dropped it
        surviving.append(prior)
        covered_keys.update(keys)
        used_ids.add(pid)
        carried += 1

    # 6f) Stable out-of-scope removal deprecations. Derived only from the
    #     PREVIOUSLY-PUBLISHED data and the final live id set — no dependence on
    #     ephemeral build IDs — so the deprecation list is deterministic and
    #     idempotent. A previously-published, out-of-scope entry that is no
    #     longer live gets a `reason: out-of-scope`, `into: null` removal.
    live_ids_final = {e["id"] for e in surviving}
    for prev in _load_prev_incidents():
        if (prev.get("id") not in live_ids_final
                and _is_out_of_scope(prev)):
            deprecations_new.append({
                "from": prev["id"], "into": None, "reason": "out-of-scope",
                "date": str(utc_today()),
            })
    if purged_scope:
        print(f"[scope-purge] dropped {purged_scope} out-of-scope malicious-package entr(ies)")
    print(f"[retention] carried {carried}/{len(eligible)} eligible prior(s) no longer in any source")
    if no_keys:
        print(f"[retention] WARNING: {no_keys} eligible prior(s) had no source_id/cve_id and could not be retained")

    deduped = surviving
    # `aiaaic_ethical_tags` / `aiaaic_seed_facts` are classification-seed
    # fields only (no schema entry; the root schema is
    # additionalProperties:false) — strip them here, after every classifier
    # that needs them (_classify_corpus, the attack_vector finalize block
    # above) has already run, and before assembly into data/incidents.json /
    # incidents.min.json below.
    for e in deduped:
        e.pop("aiaaic_ethical_tags", None)
        e.pop("aiaaic_seed_facts", None)

    # 6g) Provenance fields (INCLUSION.md trust layer). Pure, deterministic
    #     derivations of already-finalised fields — set AFTER history stamping
    #     and kept OUT of the content snapshot, so they never perturb the
    #     `updated`/drift logic. See DATA_DICTIONARY.md for the confidence rule.
    cwe_capec = _load_cwe_capec()
    freshness_sources = _load_source_freshness_registry()
    n_capec = n_purl = n_freshness = 0
    for e in deduped:
        e["tier"] = _derive_tier(e)
        e["source_count"] = len(e.get("source_ids") or [])
        e["confidence"] = _derive_confidence(e)
        e.setdefault("source_status", "active")
        if e.get("added"):
            e["first_seen"] = e["added"]
        if e.get("updated"):
            e["last_seen"] = e["updated"]
        # Linkage graph (INCLUSION.md coverage layer). Derived denormalisations
        # of cwe_ids/affected; like the other provenance fields they are set
        # here, AFTER history stamping, and kept OUT of the content snapshot so
        # they never perturb the `updated`/drift logic.
        capec = _derive_capec_ids(e, cwe_capec)
        if capec:
            e["capec_ids"] = capec
            n_capec += 1
        purl = _derive_purls(e)
        if purl:
            e["purl"] = purl
            n_purl += 1
        # D8: source-freshness marker, inherited by reference from the
        # published registry (data/source_freshness.json), never authored
        # per row. `pop` first, then re-derive from scratch: retained priors
        # (step 6e) are carried VERBATIM from the previous data/incidents.json
        # and bypass dedupe, so a retained row can arrive already carrying a
        # marker from an earlier build. Re-deriving (not `setdefault`) is what
        # lets a recovered source shed its rows' markers on the next build,
        # exactly as a newly-stale source picks up markers on ITS next build
        # with no schema change. Kept OUT of _CONTENT_FIELDS (see that
        # allowlist above) so this never bumps `updated`/`last_seen` — no
        # content changed; this describes content that hasn't changed since
        # the source's last success.
        e.pop("source_freshness", None)
        entry_tags = set(e.get("tags") or [])
        stale = sorted(
            key for key, src in freshness_sources.items()
            if src.get("status") == "stale"
            and src.get("row_marker") is not None
            and src["row_marker"].get("value") in entry_tags
        )
        if stale:
            e["source_freshness"] = {
                "status": "stale",
                "as_of": min(freshness_sources[k]["last_success"] for k in stale),
                "sources": stale,
            }
            n_freshness += 1
    print(f"[linkage] capec_ids on {n_capec} entr(ies); purl on {n_purl} entr(ies)")
    print(f"[freshness] source_freshness marker on {n_freshness} entr(ies)")

    print(f"\n[total]  {len(all_entries)} input -> {len(deduped)} unique")

    # 7) Compute `generated`: today only if anything actually changed since
    #    the previous output; otherwise preserve the previous timestamp so
    #    CI drift checks don't flap on every daily re-run.
    today = str(utc_today())
    any_change = any((e.get("updated") or "") == today for e in deduped)
    prev_generated = ""
    try:
        prev_generated = (
            json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
            .get("generated", "")
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        prev_generated = ""
    generated = today if any_change or not prev_generated else prev_generated

    # 7b) WS4-T19 pre-authorization guard. Must run AFTER id assignment
    #     (deduped rows already carry their final `id`) and BEFORE any
    #     output write below -- both the id_deprecations.json write in
    #     step 8 and the incidents.json write in step 9. Raises
    #     SplitAuthorizationError (a SystemExit subclass) and writes
    #     nothing if an unauthorized split is detected.
    _check_split_authorization(prev_id_by_key, deduped, SPLIT_AUTHORIZATION_PATH)

    # 8) Merge deprecations with the on-disk history and persist.
    prev_deprec: list[dict] = []
    if DEPRECATIONS_PATH.exists():
        try:
            prev_deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8")).get(
                "deprecations", []
            )
        except (json.JSONDecodeError, OSError):
            prev_deprec = []
    # WS4-T15: `prev_deprec` IS the append-only history on disk. It is
    # carried through VERBATIM and IN ORDER -- never re-derived, never
    # collapsed, never re-sorted. This build only APPENDS a fresh record
    # for a `from` id this build's own dedupe logic newly retires (matching
    # the *old* code's `setdefault` refusal to double-write an id that
    # already has some record); it never touches an id that already has a
    # record on disk **in THIS block**.
    # [CORRECTION, dated 2026-09-18] "It never touches an id that already
    # has a record on disk" was FALSE as a claim about the build overall —
    # the issue-88 fixpoint immediately below used to iterate every record
    # in `deprecations_all` (not just the authoritative one per `from`)
    # and MUTATE whichever it visited in place, so a stale, superseded
    # record could be rewritten and its `from` wrongly propagated into
    # `removed_terminal`, breaking a third party's live redirect. Fixed
    # there (not here) to operate on the authoritative view only and to
    # APPEND rather than mutate. See
    # docs/specs/WS4-T15-redirect-persistence-2026-09-18.md §"Defect 1".
    # This block's own claim -- appends only, for genuinely new `from`
    # ids -- stands unchanged. That distinction matters: a plain
    # `{d.get("from"): d for d in prev_deprec}` dict comprehension here
    # previously collapsed EVERY prior record down to (whichever happened to
    # be LAST when iterating `prev_deprec`) on every single rebuild, despite
    # the removed comment above this claiming "keep the earliest" -- neither
    # was true, and it silently deleted a deliberately-appended superseding
    # record on the very next `make build` (invariant-9 violation,
    # demonstrated: appending a `resplit` record for INC-07771 and
    # rebuilding took 1,051 records to 1,050). See
    # docs/specs/WS4-T15-redirect-persistence-2026-09-18.md.
    #
    # Precedence when a `from` has more than one record: LAST-IN-FILE wins,
    # matching `_load_deprecations()` in `src/genai_incidents/__init__.py`
    # (an unconditional `out[f] = t` walking the file in order) and
    # `validate.py`'s `check_integrity` (same pattern). Because this build
    # never reorders `prev_deprec` and only ever appends, file order IS
    # append order IS chronological order, by construction -- nothing
    # upstream of this point may sort or otherwise reorder the list, or that
    # equivalence (and therefore precedence) breaks silently.
    already_deprecated = {d.get("from") for d in prev_deprec if d.get("from")}
    fresh: list[dict] = []
    seen_fresh_from: set[str] = set()
    for d in deprecations_new:
        f = d.get("from")
        if f and f not in already_deprecated and f not in seen_fresh_from:
            seen_fresh_from.add(f)
            fresh.append(d)
    deprecations_all = list(prev_deprec) + fresh
    # Issue #88: an EXCLUDE bucket leaves the dataset, so any historical
    # deprecation whose CURRENTLY AUTHORITATIVE `into` was that bucket (or
    # transitively resolves to it) now dangles. Redirect it to a terminal
    # out-of-scope removal so every citation still resolves (`into: null`).
    # Fixpoint for A->B-><removed>. `into` can now be list-valued (WS4-T15
    # `split`/`resplit` records) -- skip those here rather than crash; a
    # multi-successor record dangling into an EXCLUDE bucket is not fixed
    # up automatically by this loop.
    #
    # WS4-T15 fix (BOUNCE defect 1): this loop used to iterate EVERY
    # record in `deprecations_all` and MUTATE whichever it visited in
    # place. Once a `from` could carry more than one record (the whole
    # point of §2.1's persistence fix), that meant a STALE, superseded
    # record could be rewritten even though a LATER, authoritative record
    # for the same `from` already pointed somewhere live -- and the bogus
    # rewrite then propagated that `from` into `removed_terminal`,
    # wrongly nulling any THIRD PARTY's redirect that cited the
    # now-superseded id. Demonstrated: seed `INC-09999 -> INC-00004`
    # (stale, into a real EXCLUDE bucket) + `INC-09999 -> INC-00001`
    # (later, authoritative, live) + `INC-09998 -> INC-09999` (a citer of
    # the retired id); the old loop nulled BOTH the harmless stale
    # INC-09999 record AND INC-09998's live redirect. Fixed to (a) operate
    # only on the AUTHORITATIVE (latest-per-`from`) view, mirroring the
    # same last-in-file-wins rule as `_latest_by_from` in
    # `scripts/validate.py` and `_load_deprecations()` in
    # `src/genai_incidents/__init__.py` (a separate, small implementation
    # here -- importing validate.py would be circular, since it already
    # imports from this module -- but it MUST stay behaviourally
    # identical to both); and (b) APPEND a new terminal record instead of
    # mutating an existing one in place, since editing a committed
    # record's `into`/`reason` to change its meaning is itself the kind
    # of history-rewrite `docs/ID_POLICY.md` rule 2 forbids.
    if ISSUE88_EXCLUDE:
        authoritative: dict[str, dict] = {}
        for d in deprecations_all:
            f = d.get("from")
            if f:
                authoritative[f] = d
        removed_terminal = set(ISSUE88_EXCLUDE)
        fixed_from: set[str] = set()
        changed = True
        while changed:
            changed = False
            for f, d in list(authoritative.items()):
                if f in fixed_from:
                    continue
                into = d.get("into")
                if isinstance(into, list):
                    continue
                if into in removed_terminal:
                    fix = {
                        "from": f, "into": None, "reason": "out-of-scope",
                        "date": today_str,
                    }
                    deprecations_all.append(fix)
                    authoritative[f] = fix
                    fixed_from.add(f)
                    if f not in removed_terminal:
                        removed_terminal.add(f)
                        changed = True
    if deprecations_all:
        DEPRECATIONS_PATH.write_text(
            json.dumps(
                {"deprecations": deprecations_all},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
            newline="\n",
        )
        print(f"[output] wrote {DEPRECATIONS_PATH.name} ({len(deprecations_all)} entries)")

    # 9) Write outputs
    out = {
        "version": "2.10.0",
        "generated": generated,
        "description": (
            "A consolidated, machine-readable index of GenAI and agentic AI security "
            "incidents. Every applicable entry is mapped to four core taxonomies: "
            "OWASP LLM Top 10 (2026), OWASP Agentic ASI Top 10, NIST AI RMF (AI 100-1), "
            "and MITRE ATLAS. A companion MAESTRO architectural-layer mapping is carried "
            "where the source provides it, and an experimental VERIS 1.4.1 crosswalk is "
            "computed at export time (see docs/TAXONOMIES.md)."
        ),
        "schema": "schema/incident.schema.json",
        "incident_count": len(deduped),
        "incidents": deduped,
    }
    (DATA / "incidents.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    print(f"[output] wrote data/incidents.json")

    # Slim variant — used by the static site for filtering and inline
    # row expansion. Description is truncated so the JSON stays under
    # ~5 MB, the soft limit for snappy first-paint over typical home
    # broadband, while still showing enough context to triage an entry.
    def _short(text: str, limit: int = 280) -> str:
        text = (text or "").strip()
        if len(text) <= limit:
            return text
        cut = text[: limit - 1]
        # Don't break a word mid-token.
        sp = cut.rfind(" ")
        if sp > limit * 0.6:
            cut = cut[:sp]
        return cut.rstrip() + "…"

    def _slim_entry(e: dict) -> dict:
        item = {
            "id": e["id"],
            "title": e["title"],
            "date": e.get("date"),
            "year": e.get("year"),
            "severity": e.get("severity"),
            "attack_vector": e.get("attack_vector"),
            "owasp_llm": e.get("owasp_llm", []),
            "owasp_asi": e.get("owasp_asi", []),
            "nist_ai_rmf": e.get("nist_ai_rmf", []),
            "mitre_atlas": e.get("mitre_atlas", []),
            "cve_ids": e.get("cve_ids", []),
            "primary_reference": e["references"][0]["url"] if e.get("references") else None,
            "description": _short(e.get("description")),
            "affected": _short(e.get("affected"), limit=120),
            "tags": (e.get("tags") or [])[:8],
            "quality_tier": e.get("quality_tier"),
            "corpus": e.get("corpus"),
        }
        # D12(a): min.json carries the D11(b) marker on affected rows ONLY —
        # added conditionally (never as a null) so the slim shape stays slim
        # on every unmarked row (schema-architect memo Sec 4 item 3).
        if e.get("content_license"):
            item["content_license"] = e["content_license"]
        # D8: same conditional-carry treatment for source_freshness. The slim
        # shape truncates `tags` to 8 (above), so a min.json consumer may not
        # see the row's `airi-navigator` tag at all — the marker is the only
        # freshness signal that reliably reaches them (D8 application spec §4).
        if e.get("source_freshness"):
            item["source_freshness"] = e["source_freshness"]
        return item

    slim = {
        "version": out["version"],
        "generated": out["generated"],
        "incident_count": len(deduped),
        "incidents": [_slim_entry(e) for e in deduped],
    }
    (DATA / "incidents.min.json").write_text(
        json.dumps(slim, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    print(f"[output] wrote data/incidents.min.json")

    # 6) Print taxonomy coverage summary
    counts = defaultdict(int)
    for e in deduped:
        for c in e.get("owasp_llm", []):
            counts[f"OWASP {c}"] += 1
        for c in e.get("owasp_asi", []):
            counts[c] += 1
    print("\n[coverage]")
    for k in sorted(counts):
        print(f"  {k:12s} {counts[k]}")


def merge_into(target: dict, src: dict):
    """Merge taxonomies, references, tags from src into target."""
    for key in ("owasp_llm", "owasp_asi", "owasp_dsgai", "nist_ai_rmf",
                "mitre_atlas", "mitre_atlas_tactics", "tags", "source_ids",
                "cve_ids", "cwe_ids", "mitigations"):
        merged = sorted(set((target.get(key) or []) + (src.get(key) or [])))
        if merged:
            target[key] = merged
    # Single-value fields: take src's value when target doesn't have one.
    for key in ("cvss_vector", "aiid_id", "disclosure_date", "impact"):
        if not target.get(key) and src.get(key):
            target[key] = src[key]
    # References — dedupe by url. WS4-T10: deliberately reuses the SAME
    # normalize_url as the dedup-key indexes above, not a stricter variant —
    # a reference is a genuine duplicate under exactly the same identity
    # rule that says two rows are the same incident, so splitting the
    # definitions would only let two references for the very row being
    # merged disagree with each other about whether they're duplicates.
    seen = {normalize_url(r["url"]): r for r in target.get("references", [])}
    for r in src.get("references", []):
        u = normalize_url(r.get("url", ""))
        if u and u not in seen:
            seen[u] = r
    target["references"] = list(seen.values())
    # Pick higher severity
    order = ["Info", "Low", "Medium", "High", "Critical"]
    src_sev = src.get("severity") or "Medium"
    tgt_sev = target.get("severity") or "Medium"
    if src_sev not in order:
        src_sev = "Medium"
    if tgt_sev not in order:
        tgt_sev = "Medium"
    if order.index(src_sev) > order.index(tgt_sev):
        target["severity"] = src_sev
    # Prefer the more specific / more plausible date.
    # Specificity: YYYY-MM-DD > YYYY-MM > YYYY. A future-year date should be
    # overridden by a same-or-earlier date from any other source.
    current_year = utc_today().year
    src_date = (src.get("date") or "").strip()
    tgt_date = (target.get("date") or "").strip()

    def _date_score(d: str) -> tuple[int, int]:
        if re.match(r"^\d{4}-\d{2}-\d{2}", d):
            return (3, int(d[:4]))
        if re.match(r"^\d{4}-\d{2}", d):
            return (2, int(d[:4]))
        if re.match(r"^\d{4}", d):
            return (1, int(d[:4]))
        return (0, 0)

    src_score, src_year = _date_score(src_date)
    tgt_score, tgt_year = _date_score(tgt_date)
    tgt_future = tgt_year > current_year
    src_future = src_year > current_year
    if src_score and (
        (tgt_future and not src_future)
        or (not tgt_future and src_score > tgt_score and not src_future)
    ):
        target["date"] = src_date
        target["year"] = src_year or target.get("year")
    fill_taxonomy(target)


if __name__ == "__main__":
    main()
