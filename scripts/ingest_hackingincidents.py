"""
ingest_hackingincidents.py
==========================

Ingests the hackingincidents.ai ledger (Daniel Miessler / Unsupervised Learning,
MIT, D159 evaluation, user ruling D160 "Facts + link") from a PINNED snapshot of
``https://hackingincidents.ai/incidents.json`` (the site copy, not the lagging
Substrate repo copy: docs/audits/D159-hackingincidents-source-eval-2026-11-25.md
U1).

Outputs (all committed; ``make build`` reads only these, never the network):

  ingest/snapshots/hackingincidents/incidents.json   the STRIPPED snapshot (D162): only the fields this ingest reads
  ingest/wave13_hackingincidents.provenance.json     the pin: url, sha256, fetched
                                                     (UTC), ``updated``, rows,
                                                     licence string, run stats, review
  ingest/wave13_hackingincidents.json                NEW incident rows only
  ingest/wave13_hackingincidents.attach.json         reference attachments for ledger
                                                     rows that match an EXISTING row,
                                                     plus the fold-exempt URL list

Snapshot (D162, user ruling: strip): the committed snapshot holds only the fields this ingest
reads. The raw download is verified by sha256 on ``--fetch``, stripped, and never written to
the repository; the raw sha256/size are in the provenance file. ``--from-file`` accepts the
stripped snapshot (verifying its own sha256) and also a raw download, for re-verification: it
is checked against the pinned raw sha256, stripped in memory and must reproduce the pinned
stripped sha256.

Network: ``--from-file`` (the default when the pinned snapshot exists and
``--fetch`` is not given) rebuilds offline. ``--fetch`` is the only path that
touches the network, through ``ingest.common.fetch_once`` (robots check, rate
limit, identifying User-Agent). Not part of ``make ingest-all`` or the weekly
auto-refresh.

What is kept (facts): slug, title, date, ``disclosed``, ``activity``, actor,
actor type, nexus label, targets, AI role(s), model(s) + basis, autonomy, the
ledger's confidence GRADE (a third-party label, never ours), and every source
URL with its publisher and primary flag. Plus a link to the ledger's own page.

What is NOT kept: ``quote`` (verbatim vendor text: 7 of 7 checked by the D159
gate), ``summary`` (held), ``confidence_reason`` (MEASURED: 15 of 298 rows share
an 8+ word run with their own quote and it embeds 111 quoted publisher
fragments, longest 22 words), ``outcome`` (4 rows share an 8+ word run with the
quote; not a D159 kept field), ``single_source_reason``, ``enrichment``.
``description`` is a deterministic template over the kept facts: no model call,
no copied sentence.

Dedupe FIRST (the merger folds by CVE > source id > reference URL > title, and a
fold changes fields on the surviving row, severity/date/tags included):

  * a ledger row that already exists in the corpus is NOT emitted as a row. It
    becomes a REFERENCE ATTACHMENT on the existing row (merge_and_dedupe
    ``_apply_reference_attachments``), which adds references and changes nothing
    else on that row.
  * match keys: (1) AIID join, a ledger source ``incidentdatabase.ai/cite/N``
    against the corpus ``aiid_id``/``AIID-N``; (2) normalised source URL against
    every corpus reference (the merger's own ``normalize_url``; aggregate URLs
    never count); (3) normalised title +-1 year.
  * (4) REVIEWED_MATCHES: event matches no key can find (the corpus row cites other
    articles for the same event) that a person confirmed by reading both rows; applies
    only when keys (1)-(3) found nothing. Recall of this stage is unmeasured.
  * level: EVENT when matched by AIID join or title, or by URL with an
    idf-weighted title similarity >= ``EVENT_SIM`` (0.25); REPORT when the match is
    URL-only and the corpus row is evidently the parent vendor report (low
    similarity). Both attach; the level is recorded for review, not used to split.
  * several candidates: AIID join beats URL; then higher title similarity; then
    more shared URLs; then lowest INC id. Alternates are recorded.

The ledger splits one vendor report into several incidents (26 URLs are cited by
2 to 10 ledger rows). Emitted rows keep that granularity: URLs shared by 2+ emitted
rows are written to the attach file as ``fold_exempt_urls`` so the merger does not
URL-fold them into one row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from merge_and_dedupe import is_aggregate_url, normalize_url, title_key  # noqa: E402

INGEST = ROOT / "ingest"
SNAPSHOT_DIR = INGEST / "snapshots" / "hackingincidents"
SNAPSHOT_FILE = SNAPSHOT_DIR / "incidents.json"
OUT_FILE = INGEST / "wave13_hackingincidents.json"
ATTACH_FILE = INGEST / "wave13_hackingincidents.attach.json"
PROVENANCE_FILE = INGEST / "wave13_hackingincidents.provenance.json"
CORPUS_FILE = ROOT / "data" / "incidents.json"

LEDGER_URL = "https://hackingincidents.ai/incidents.json"
LEDGER_PAGE = "https://hackingincidents.ai/incident/{slug}/"
SOURCE_PREFIX = "HIAI-"
EVENT_SIM = 0.25
LICENSE_STRING = ("MIT License, Copyright (c) 2025 Daniel Miessler "
                  "(stated at https://hackingincidents.ai/data/; third-party quotes remain "
                  "under their publishers' terms)")
CITATION = "hackingincidents.ai, Unsupervised Learning, accessed <date>"

MIT_MARKER = {
    "source": "hackingincidents",
    "license": "MIT",
    "license_url": "https://github.com/danielmiessler/Substrate/blob/main/LICENSE",
    "attribution": "hackingincidents.ai, Unsupervised Learning (Daniel Miessler)",
    "attribution_url": "https://hackingincidents.ai/",
    "obligations": ["attribution"],
}

# Ledger fields that are deliberately never read into an output row.
EXCLUDED_FIELDS = ("quote", "summary", "confidence_reason", "outcome",
                   "single_source_reason", "enrichment")

# In-ledger near-duplicates, reviewed (D159 A5). key = collapsed slug, value =
# surviving slug. The detector below must find exactly these: a NEW near-duplicate
# pair in a later snapshot aborts the run for review instead of passing silently.
KNOWN_INLEDGER_DUPLICATES = {
    "cairn-monai-label-university-intrusion": "cairn-monai-label-university-intrusions",
}

# Event matches that neither the AIID join nor a shared source URL can find (the corpus row
# cites another article, or an OECD/AIAAIC page, for the same event) but a person reading both
# rows confirmed. Hand-adjudicated 2026-11-26 (pipeline-engineer) from the title/entity-token
# candidate list (``CorpusMatcher.title_candidates``: shared RARE title tokens, df<=4 in the
# corpus, idf-weighted similarity >= 0.30, year +-1) by reading the ledger row and the corpus
# row (title, date, actors, targets) for all 64 candidates of the first pass: 28 accepted, 36 rejected (same
# theme, different event; listed in the provenance ``title_candidates_not_matched``). Four
# more events and the three report-level rows came from a looser pass (idf-weighted title
# similarity without the rare-token requirement) over the same rows, read the same way.
# Applies ONLY when neither URL nor AIID matched; the INC id must exist or the run aborts.
# level "report" = the corpus row is the parent vendor report. Not exhaustive: a ledger row
# with no rare title token in common with its corpus twin is not found (recall unmeasured).
REVIEWED_MATCHES = {
    "aepd-first-agentic-ai-breach-spain-2026": ("INC-17294", "event"),
    "artex-south-korean-bank-intrusions": ("INC-17357", "event"),
    "arup-hong-kong-deepfake-video-call-2024": ("INC-03588", "event"),
    "bandai-channel-teen-chatgpt-program-2025": ("INC-14897", "event"),
    "bossai-ai-agent-campaign": ("INC-17384", "event"),
    "brad-pitt-ai-images-romance-scam-2025": ("INC-03452", "event"),
    "cairn-ecommerce-intrusion-campaign": ("INC-17344", "event"),
    "cardin-kuleba-deepfake-zoom-2024": ("INC-04196", "event"),
    "chainalysis-offensive-agentic-breach-2026": ("INC-17368", "event"),
    "deepload-ai-assisted-evasion-2026": ("INC-00527", "event"),
    "eviltokens-ai-augmented-phaas-bec-2026": ("INC-00266", "event"),
    "ferrari-ceo-voice-clone-attempt-2024": ("INC-03783", "event"),
    "fideuram-intesa-voice-clone-95m-2026": ("INC-17335", "event"),
    "fortigate-600-devices-ai-augmented-2026": ("INC-00265", "event"),
    "funksec-ai-assisted-ransomware": ("INC-02219", "event"),
    "grok-bankrbot-morse-code-transfer-2026": ("INC-00196", "event"),
    "kali365-phaas-ai-lures-2026": ("INC-07898", "event"),
    "kerala-deepfake-whatsapp-video-call-2023": ("INC-04711", "event"),
    "kimsuky-chatgpt-fake-military-id": ("INC-02959", "event"),
    "konni-ai-built-powershell-backdoor-2026": ("INC-01541", "event"),
    "lastpass-deepfake-ceo-voice-attempt-2024": ("INC-04154", "event"),
    "marimo-exploit-llm-agent-database-exfil-2026": ("INC-17276", "event"),
    "meta-ai-support-bot-instagram-takeovers-2026": ("INC-14602", "event"),
    "mexico-government-claude-code-breach": ("INC-07905", "event"),
    "promptspy-android-gemini-agent": ("INC-00587", "event"),
    "retool-deepfake-voice-vishing-2023": ("INC-04615", "event"),
    "singapore-pm-wong-deepfake-zoom-2026": ("INC-01775", "event"),
    "slopoly-hive0163-ransomware": ("INC-00505", "event"),
    "taiwan-government-hermes-openclaw-2026": ("INC-17261", "event"),
    "taiwan-romance-scam-ai-voice-changer-2026": ("INC-17391", "event"),
    "thailand-finance-ministry-hermes-agent-2026": ("INC-17275", "event"),
    "vapor-panda-artex-global-espionage": ("INC-17367", "event"),
    # found afterwards by a seeded random sample (30 of the remaining new rows) and a loose
    # scan of the rest, not by the candidate list; read the same way
    "claude-pentestgpt-argentine-healthcare": ("INC-17369", "event"),
    "hk-deepfake-dating-crypto-fraud-2025": ("INC-02696", "event"),
    "wpp-ceo-deepfake-meeting-attempt-2024": ("INC-04359", "event"),
    "wiles-impersonation-ai-voice-2025": ("INC-03373", "event"),
    "s1ngularity-nx-ai-cli-weaponized": ("INC-02850", "event"),  # Nx npm "AI coding agents" event, AIID 1210, 2025-08-21 (gate sample; INC-10278 is the GHSA row for the same event)
    "dutch-ai-bank-warning-recordings-fraud-2026": ("INC-17361", "event"),  # EUR 380,000, Netherlands, 2026-10 (second candidate pass)
    # the corpus holds the OpenAI October 2025 report as one row (INC-03006); the ledger
    # splits it per operation but cites the cdn PDF, not the page INC-03006 cites
    "openai-korean-operators-xenorat-2025": ("INC-03006", "report"),
    "openai-russian-malware-tooling-2025": ("INC-03006", "report"),
    "openai-unk-droppitch-2025": ("INC-03006", "report"),
}

ROLE_WORDS = {
    "malware-dev": "malware development",
    "agentic-intrusion": "agentic intrusion",
    "social-engineering": "social engineering",
    "recon": "reconnaissance",
    "fraud": "fraud",
    "ops-automation": "operations automation",
    "deepfake": "deepfake media",
    "phishing-content": "phishing content",
    "exploit-dev": "exploit development",
    "evasion": "defence evasion",
    "data-analysis": "data analysis",
    "vuln-research": "vulnerability research",
    "llmjacking": "LLM account hijacking",
    "supply-chain": "supply-chain compromise",
    "agent-hijack": "agent hijack",
    "malware-runtime-llm": "malware that calls an LLM at runtime",
}
# Only roles that name an attack mechanism the corpus vocabulary already has. Social
# engineering and fraud are deliberately NOT mapped to "phishing" (they cover scams,
# personas and extortion calls that are not phishing). First mappable role wins; the rest
# stay "other" and fall through to the merger's own text rules over title + description.
ROLE_VECTOR = {
    "deepfake": "deepfake",
    "phishing-content": "phishing",
    "malware-dev": "malware",
    "malware-runtime-llm": "malware",
    "evasion": "malware",
    "supply-chain": "supply-chain",
    "agent-hijack": "agent-hijack",
}
BASIS_WORDS = {
    "stated-by-researcher": "as stated by the researchers",
    "stated-by-vendor": "as stated by the vendor",
    "stated-by-victim": "as stated by the victim",
    "inferred": "inferred, not stated",
    "unknown": "basis not established",
}


class LedgerError(SystemExit):
    pass


# ----------------------------------------------------------------------------
# Snapshot + pin
# ----------------------------------------------------------------------------
def fetch_snapshot() -> bytes:
    from ingest.common import fetch_once  # only imported on the network path
    body, _ = fetch_once(LEDGER_URL, timeout=120, min_interval=3.0)
    return body


def parse_snapshot(body: bytes) -> tuple[str, list[dict]]:
    try:
        data = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise LedgerError(f"[FATAL] ledger snapshot is not JSON: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("incidents"), list) or not data["incidents"]:
        raise LedgerError("[FATAL] ledger snapshot has no non-empty 'incidents' list; refusing to proceed")
    rows = data["incidents"]
    ids = [r.get("id") for r in rows]
    if len(set(ids)) != len(ids) or not all(isinstance(i, str) and i for i in ids):
        raise LedgerError("[FATAL] ledger snapshot ids are missing or not unique")
    return str(data.get("updated") or ""), rows


# D162: the committed snapshot is STRIPPED. Only the fields this ingest reads are kept;
# everything else (the verbatim quote, the summary, the confidence-reason and outcome text,
# the single-source note, the enrichment block, and per-source fetch bookkeeping) is dropped
# before anything is written to the repository. The raw download's sha256, size and `updated`
# stay in the provenance file, so a reviewer can re-fetch and verify the raw bytes.
KEPT_ROW_FIELDS = ("id", "title", "date", "disclosed", "activity", "actor", "actor_type", "nexus",
                   "targets", "ai_role", "models", "model_basis", "autonomy", "confidence", "sources")
KEPT_SOURCE_FIELDS = ("title", "publisher", "url", "primary")


def dropped_keys_present(data: dict) -> list[str]:
    """Keys in a snapshot object that the stripped form must not contain (empty for a
    stripped snapshot, non-empty for a raw download)."""
    found = set()
    for r in data.get("incidents") or []:
        found |= {k for k in r if k not in KEPT_ROW_FIELDS}
        for src in r.get("sources") or []:
            found |= {"sources." + k for k in src if k not in KEPT_SOURCE_FIELDS}
    return sorted(found)


def strip_snapshot(data: dict) -> dict:
    """Pure: the raw ledger object -> the stripped object (kept fields only, same order)."""
    rows = []
    for r in data["incidents"]:
        o = {k: r[k] for k in KEPT_ROW_FIELDS if k in r and k != "sources"}
        o["sources"] = [{k: src[k] for k in KEPT_SOURCE_FIELDS if k in src} for src in r.get("sources") or []]
        rows.append(o)
    return {"updated": data.get("updated"), "stripped": True, "incidents": rows}


def stripped_bytes(data: dict) -> bytes:
    return (json.dumps(strip_snapshot(data), indent=1, ensure_ascii=False) + chr(10)).encode("utf-8")


# ----------------------------------------------------------------------------
# Row construction (facts only)
# ----------------------------------------------------------------------------
def _clean(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


_AIID_CITE_RE = re.compile(r"^https?://(?:[a-z0-9-]+[.])*incidentdatabase[.]ai(?::[0-9]+)?/cite/([0-9]+)", re.I)


def _aiid_cite_number(url: str):
    """Match object (group 1 = the AIID number) for an AI Incident Database cite URL: anchored at
    the scheme and host (the host must be incidentdatabase.ai or a subdomain), not a substring."""
    return _AIID_CITE_RE.match((url or "").strip())


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace(chr(92), "/")
    except ValueError:
        return path.name


def ledger_page(slug: str) -> str:
    return LEDGER_PAGE.format(slug=slug)


def vector_for(roles: list[str]) -> str:
    for r in roles:
        if r in ROLE_VECTOR:
            return ROLE_VECTOR[r]
    return "other"


def _placeholder(v: str) -> bool:
    return not v or bool(re.match(r"(?i)^(not stated|unspecified|unnamed|unknown|n/a|none)(?![a-z])", v))


def build_description(x: dict) -> str:
    """Deterministic template over kept facts. No ledger sentence is copied; the
    free-text fields it interpolates (actor, targets, nexus) are short labels."""
    roles = [ROLE_WORDS.get(r, r.replace("-", " ")) for r in x.get("ai_role") or []]
    named = [_clean(m) for m in x.get("models") or [] if not _placeholder(_clean(m))]
    actor, targets = _clean(x.get("actor")), _clean(x.get("targets"))
    parts = [
        f"Ledger entry {x['id']} (hackingincidents.ai). Actor per the ledger: "
        f"{actor if not _placeholder(actor) else 'not identified'}; actor type "
        f"{_clean(x.get('actor_type')) or 'unknown'}. Targets per the ledger: "
        f"{targets if not _placeholder(targets) else 'not specified'}."
    ]
    when = f"Dated {x.get('date')}"
    if x.get("disclosed"):
        when += f", disclosed {x['disclosed']}"
    if x.get("activity"):
        when += f", activity period {x['activity']}"
    parts.append(when + ".")
    ai = "AI use per the ledger: " + (", ".join(roles) or "not specified") + "; "
    if named:
        ai += ("models named: " + ", ".join(named) + " ("
               + BASIS_WORDS.get(x.get("model_basis"), "basis not established") + ")")
    else:
        ai += "no model named"
    parts.append(ai + f"; autonomy level {_clean(x.get('autonomy')) or 'unspecified'}.")
    if x.get("nexus"):
        parts.append(f"Nexus label from the cited sources: {_clean(x['nexus'])}.")
    parts.append(
        f"The ledger grades the evidence {str(x.get('confidence') or 'unknown').lower()}; "
        "that grade is the ledger operator's label, not this project's assessment."
        " Facts and source links only: the ledger's narrative text and quotations are not reproduced."
    )
    return " ".join(parts)


def ref_type(s: dict) -> str:
    return "report" if s.get("primary") else "reference"


def source_refs(x: dict) -> list[dict]:
    refs = []
    for s in x.get("sources") or []:
        u = _clean(s.get("url"))
        if not u.startswith("http"):
            continue
        pub, title = _clean(s.get("publisher")), _clean(s.get("title"))
        refs.append({"title": (f"{pub}: {title}" if pub and title else (title or pub or u))[:240],
                     "url": u, "type": ref_type(s)})
    return refs


def page_ref(slug: str) -> dict:
    return {"title": f"hackingincidents.ai ledger entry {slug}", "url": ledger_page(slug), "type": "reference"}


def to_row(x: dict, extra_slugs: tuple[str, ...] = (), extra_sources: list[dict] | None = None) -> dict:
    slug = x["id"]
    refs = [page_ref(slug)] + [page_ref(s) for s in extra_slugs]
    seen = {r["url"] for r in refs}
    for r in source_refs(x) + list(extra_sources or []):
        if r["url"] not in seen:
            seen.add(r["url"])
            refs.append(r)
    date = _clean(x.get("date"))
    year = int(date[:4]) if date[:4].isdigit() else 0
    roles = list(x.get("ai_role") or [])
    tags = ["hackingincidents", f"ledger-grade-{str(x.get('confidence') or 'unknown').lower()}",
            f"actor-{_clean(x.get('actor_type')) or 'unknown'}"] + [f"ai-role-{r}" for r in roles]
    row = {
        "source_id": SOURCE_PREFIX + slug,
        "title": _clean(x.get("title")),
        "date": date,
        "year": year,
        "category": "real-world",
        "description": build_description(x),
        "attack_vector": vector_for(roles),
        "affected": _clean(x.get("targets")),
        "references": refs,
        "tags": sorted(set(tags)),
        # the ledger is a security ledger by scope (cyberattacks where AI was used by
        # the attacker); set explicitly so the corpus label never depends on the
        # merger's keyword scan over our own template text
        "corpus": "security",
        # machine-ingested, third-party grade, no review by us (D43)
        "quality_tier": "auto",
        "description_provenance": "original",
        "description_source": "hackingincidents",
        "content_license": dict(MIT_MARKER),
    }
    disclosed = _clean(x.get("disclosed"))
    if re.match(r"^\d{4}-\d{2}-\d{2}$", disclosed):
        row["disclosure_date"] = disclosed
    return row


# ----------------------------------------------------------------------------
# In-ledger near-duplicates
# ----------------------------------------------------------------------------
def find_slug_near_duplicates(rows: list[dict]) -> dict[str, str]:
    """{collapsed slug: surviving slug} for slugs that differ only by a trailing 's'
    on the last token (a plural). The singular is collapsed into the plural."""
    ids = {r["id"] for r in rows}
    out = {}
    for s in sorted(ids):
        if s + "s" in ids:
            out[s] = s + "s"
    return out


def collapse_inledger(rows: list[dict]) -> tuple[list[dict], dict[str, str]]:
    found = find_slug_near_duplicates(rows)
    if set(found.items()) - set(KNOWN_INLEDGER_DUPLICATES.items()):
        raise LedgerError(
            f"[FATAL] in-ledger near-duplicate slugs {found} include pairs outside the reviewed set "
            f"{KNOWN_INLEDGER_DUPLICATES}; review them (D159 A5) and update "
            "KNOWN_INLEDGER_DUPLICATES before re-running.")
    by = {r["id"]: r for r in rows}
    kept = [r for r in rows if r["id"] not in found]
    return kept, {c: s for c, s in found.items() if c in by and s in by}


# ----------------------------------------------------------------------------
# Matching against the existing corpus
# ----------------------------------------------------------------------------
STOP = set("the a an of in to and for by with on at from as is was used ai using attack attacks campaign "
           "agent agents against via new reportedly threat actor actors incident intrusion intrusions "
           "group operation operations use llm model models generative gen genai".split())


def _toks(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 2}


class CorpusMatcher:
    def __init__(self, corpus: list[dict], prev_attached: set[tuple[str, str]] | None = None):
        prev_attached = prev_attached or set()
        self.by_id: dict[str, dict] = {}
        self.urls: dict[str, set[str]] = defaultdict(set)
        self.aiid: dict[str, set[str]] = defaultdict(set)
        self.titles: dict[str, list[tuple[int, str]]] = defaultdict(list)
        self.df: Counter = Counter()
        self.n = 0
        for e in corpus:
            sids = e.get("source_ids") or []
            if any(str(s).startswith(SOURCE_PREFIX) for s in sids):
                continue  # our own earlier output is not "the corpus" (idempotent reruns)
            eid = e["id"]
            self.by_id[eid] = e
            self.n += 1
            self.df.update(_toks(e.get("title") or ""))
            for r in e.get("references") or []:
                u = normalize_url(r.get("url") or "")
                if u and (eid, u) not in prev_attached:
                    self.urls[u].add(eid)
            if e.get("aiid_id"):
                self.aiid[str(e["aiid_id"])].add(eid)
            for s in sids:
                m = re.match(r"AIID-(\d+)$", str(s))
                if m:
                    self.aiid[m.group(1)].add(eid)
            self.titles[title_key(e.get("title") or "")].append((e.get("year") or 0, eid))

    def _idf(self, t: str) -> float:
        return math.log((self.n + 1) / (self.df[t] + 1))

    def similarity(self, x: dict, e: dict) -> float:
        a = _toks(" ".join([x.get("title") or "", x.get("actor") or "", x.get("targets") or "",
                            " ".join(x.get("models") or [])]))
        b = _toks(e.get("title") or "")
        denom = min(sum(self._idf(t) for t in a), sum(self._idf(t) for t in b))
        return sum(self._idf(t) for t in a & b) / denom if denom > 0 else 0.0

    def title_candidates(self, x: dict, limit: int = 2) -> list[tuple[float, str]]:
        """Candidate event twins by shared RARE title tokens (a person decides; see
        REVIEWED_MATCHES). Not used to attach anything by itself."""
        lt = _toks(" ".join([x.get("title") or "", x.get("actor") or "", x.get("targets") or ""]))
        year = int(str(x.get("date") or "0")[:4] or 0)
        out = []
        for eid, e in self.by_id.items():
            if abs((e.get("year") or 0) - year) > 1:
                continue
            et = _toks(e.get("title") or "")
            sh = lt & et
            if not any(self.df[t] <= 4 and len(t) >= 3 for t in sh):
                continue
            denom = min(sum(self._idf(t) for t in lt), sum(self._idf(t) for t in et))
            sim = sum(self._idf(t) for t in sh) / denom if denom > 0 else 0.0
            if sim >= 0.30:
                out.append((round(sim, 2), eid))
        return sorted(out, reverse=True)[:limit]

    def match(self, x: dict) -> dict | None:
        cands: dict[str, dict] = {}

        def slot(eid):
            return cands.setdefault(eid, {"aiid": False, "urls": set(), "title": False})

        for s in x.get("sources") or []:
            url = s.get("url") or ""
            m = _aiid_cite_number(url)
            if m:
                for eid in self.aiid.get(m.group(1), ()):
                    slot(eid)["aiid"] = True
            u = normalize_url(url)
            if u and not is_aggregate_url(u):
                for eid in self.urls.get(u, ()):
                    slot(eid)["urls"].add(u)
        year = int(str(x.get("date") or "0")[:4] or 0)
        for y, eid in self.titles.get(title_key(x.get("title") or ""), ()):
            if abs((y or 0) - year) <= 1:
                slot(eid)["title"] = True
        if not cands:
            return None
        scored = []
        for eid, c in cands.items():
            sim = self.similarity(x, self.by_id[eid])
            scored.append((not c["aiid"], -round(sim, 4), -len(c["urls"]), eid, sim, c))
        scored.sort(key=lambda t: t[:4])
        _, _, _, eid, sim, c = scored[0]
        basis = [k for k in ("aiid", "title") if c[k]] + (["url"] if c["urls"] else [])
        level = "event" if (c["aiid"] or c["title"] or sim >= EVENT_SIM) else "report"
        return {"target": eid, "basis": basis, "level": level, "similarity": round(sim, 3),
                "shared_urls": sorted(c["urls"]),
                "alternates": [t[3] for t in scored[1:]]}


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def longest_common_run(a: str, b: str) -> int:
    wa, wb = re.findall(r"[a-z0-9]+", a.lower()), re.findall(r"[a-z0-9]+", b.lower())
    best, prev = 0, [0] * (len(wb) + 1)
    for i in range(1, len(wa) + 1):
        cur = [0] * (len(wb) + 1)
        for j in range(1, len(wb) + 1):
            if wa[i - 1] == wb[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def build(ledger_rows: list[dict], corpus: list[dict], prev_attached: set[tuple[str, str]] | None = None
          ) -> tuple[list[dict], dict, dict, dict]:
    """-> (new rows, attach payload, stats, review)"""
    rows, collapsed = collapse_inledger(ledger_rows)
    all_by = {r["id"]: r for r in ledger_rows}
    matcher = CorpusMatcher(corpus, prev_attached)
    new_rows: list[dict] = []
    attachments: list[dict] = []
    review = {"collapsed_inledger": {}, "matches": [], "multi_candidate": [],
              "report_level": [], "title_candidates_not_matched": [],
              "reviewed_but_url_matched_elsewhere": []}
    stats = Counter()
    for x in rows:
        absorbed = [c for c, s in collapsed.items() if s == x["id"]]
        # the collapsed singular's sources and page ride along on the survivor
        extra_src = [r for c in absorbed for r in source_refs(all_by[c])]
        m = matcher.match(x)
        if m is None and absorbed:
            for c in absorbed:           # a collapsed twin that matches the corpus pulls the pair in
                m = matcher.match(all_by[c])
                if m:
                    break
        rv = REVIEWED_MATCHES.get(x["id"])
        if rv and m is not None and m["target"] != rv[0]:
            review["reviewed_but_url_matched_elsewhere"].append({"ledger": x["id"], "reviewed": rv[0], "matched": m["target"]})
        if m is None and rv:
            if rv[0] not in matcher.by_id:
                raise LedgerError(f"[FATAL] reviewed match {x['id']} -> {rv[0]}: that INC id is not in the corpus; "
                                  "re-review REVIEWED_MATCHES (the corpus changed under it).")
            m = {"target": rv[0], "basis": ["reviewed-title"], "level": rv[1],
                 "similarity": round(matcher.similarity(x, matcher.by_id[rv[0]]), 3),
                 "shared_urls": [], "alternates": []}
        elif m is None:
            cands = matcher.title_candidates(x)
            if cands:
                review["title_candidates_not_matched"].append(
                    {"ledger": x["id"], "candidates": [{"inc_id": i, "similarity": s_} for s_, i in cands]})
        if m is None:
            new_rows.append(to_row(x, tuple(absorbed), extra_src))
            stats["new"] += 1
            for c in absorbed:
                review["collapsed_inledger"][c] = x["id"]
            continue
        target = matcher.by_id[m["target"]]
        # a reference this ingest attached on an earlier run is not "already there": it
        # must be re-listed, or the next run would lose it from prev_attached and re-match
        # the rows that share that URL (idempotence; found 2026-11-26, 227/70 -> 224/73)
        have = {normalize_url(r.get("url") or "") for r in target.get("references") or []
                if (m["target"], normalize_url(r.get("url") or "")) not in (prev_attached or set())}
        refs = [page_ref(x["id"])] + [page_ref(c) for c in absorbed]
        for r in source_refs(x) + extra_src:
            nu = normalize_url(r["url"])
            if nu and nu not in have and not _aiid_cite_number(r["url"]):
                have.add(nu)
                refs.append(r)
        attachments.append({
            "from": SOURCE_PREFIX + x["id"],
            "target": {"inc_id": m["target"], "source_ids": list(target.get("source_ids") or [])[:6]},
            "level": m["level"], "basis": m["basis"],
            "references": refs,
        })
        stats["attached"] += 1
        stats[f"attached_{m['level']}"] += 1
        review["matches"].append({"ledger": x["id"], **m})
        if m["alternates"]:
            review["multi_candidate"].append({"ledger": x["id"], "chosen": m["target"], "alternates": m["alternates"]})
        if m["level"] == "report":
            review["report_level"].append({"ledger": x["id"], "target": m["target"], "similarity": m["similarity"]})
        for c in absorbed:
            review["collapsed_inledger"][c] = x["id"]
    # URLs cited by 2+ emitted rows: the ledger's own report-level split. Keep the rows apart.
    cnt: Counter = Counter()
    for r in new_rows:
        for u in {normalize_url(q["url"]) for q in r["references"]}:
            cnt[u] += 1
    fold_exempt = sorted(u for u, n in cnt.items() if n >= 2 and u)
    attach = {"version": 1, "source": "hackingincidents", "attachments": attachments,
              "fold_exempt_urls": fold_exempt}
    stats.update({"ledger_rows": len(ledger_rows), "collapsed_inledger": len(collapsed),
                  "fold_exempt_urls": len(fold_exempt)})
    return new_rows, attach, dict(stats), review


def excluded_field_measurements(ledger_rows: list[dict], out_rows: list[dict]) -> dict:
    # needs the RAW rows (quote text); main() only calls it on a raw download
    """Per-field longest verbatim word run against the row's own quote (the
    verbatim vendor text), for the excluded fields (why they are excluded) and for
    the kept free-text fields (proof they are clean) -- all 298 rows, no sample."""
    def runs(field):
        return [longest_common_run(str(x.get(field) or ""), x.get("quote") or "") for x in ledger_rows]
    out = {}
    for f in ("confidence_reason", "outcome", "summary", "title", "actor", "targets", "nexus"):
        v = runs(f)
        out[f] = {"max_run": max(v), "rows_ge_8": sum(k >= 8 for k in v), "rows_ge_12": sum(k >= 12 for k in v)}
    by = {x["id"]: x for x in ledger_rows}
    desc = [longest_common_run(r["description"], by[r["source_id"][len(SOURCE_PREFIX):]].get("quote") or "")
            for r in out_rows]
    out["emitted_description_vs_quote"] = {"rows": len(desc), "max_run": max(desc) if desc else 0}
    return out


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="NETWORK: fetch the site copy through ingest/common.py and re-pin the snapshot")
    ap.add_argument("--from-file", metavar="PATH", default=str(SNAPSHOT_FILE),
                    help="offline rebuild from a saved snapshot (default: the pinned snapshot)")
    ap.add_argument("--corpus", metavar="PATH", default=str(CORPUS_FILE),
                    help="corpus to dedupe against (default data/incidents.json)")
    ap.add_argument("--record-pin", metavar="FETCHED_UTC",
                    help="record the --from-file bytes as the new pin with this fetch time "
                         "(YYYY-MM-DDTHH:MM:SSZ, from the response Date header); offline")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prev_prov = json.loads(PROVENANCE_FILE.read_text(encoding="utf-8")) if PROVENANCE_FILE.exists() else {}
    pin = dict(prev_prov.get("snapshot") or {})
    if args.fetch:
        body = fetch_snapshot()
        fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        body = Path(args.from_file).read_bytes()
        fetched = pin.get("fetched_utc")
    digest = hashlib.sha256(body).hexdigest()
    try:
        obj = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise LedgerError(f"[FATAL] ledger snapshot is not JSON: {e}")
    is_raw = bool(dropped_keys_present(obj))
    if args.fetch:
        if not is_raw:
            raise LedgerError("[FATAL] the fetched ledger has none of the fields the strip drops; the site format "
                              "changed, review before re-pinning.")
    elif args.record_pin:
        if not is_raw:
            raise LedgerError("[FATAL] --record-pin needs the RAW download (it records the raw sha256).")
        fetched = args.record_pin
    elif is_raw:
        # a raw download is accepted for verification only: its sha256 must be the pinned raw
        # sha256, and it is stripped in memory; the raw bytes are never written anywhere.
        if pin.get("raw_sha256") != digest:
            raise LedgerError(f"[FATAL] {args.from_file} is a raw download whose sha256 does not match the "
                              f"pinned raw_sha256 in {PROVENANCE_FILE.name}; re-pin with --fetch, never silently.")
    else:
        if pin.get("sha256") != digest:
            raise LedgerError(
                f"[FATAL] {args.from_file} sha256 does not match the pin in {PROVENANCE_FILE.name}; "
                "re-pin with --fetch (a deliberate, reviewed refresh), never silently.")
    sbytes = stripped_bytes(obj) if is_raw else body
    sdigest = hashlib.sha256(sbytes).hexdigest()
    if is_raw and not (args.fetch or args.record_pin) and pin.get("sha256") != sdigest:
        raise LedgerError("[FATAL] stripping the raw download did not reproduce the pinned stripped sha256")
    updated, led = parse_snapshot(sbytes)
    raw_led = parse_snapshot(body)[1] if is_raw else None

    corpus = json.loads(Path(args.corpus).read_text(encoding="utf-8"))["incidents"]
    prev_attached = set()
    if ATTACH_FILE.exists():
        for a in json.loads(ATTACH_FILE.read_text(encoding="utf-8")).get("attachments", []):
            for r in a["references"]:
                prev_attached.add((a["target"]["inc_id"], normalize_url(r["url"])))
    new_rows, attach, stats, review = build(led, corpus, prev_attached)
    if is_raw:
        measure = excluded_field_measurements(raw_led, new_rows)
    else:
        # the quote text is not in the stripped snapshot: carry the measurements taken
        # on the raw bytes at strip time forward unchanged (they describe those bytes)
        measure = prev_prov.get("excluded_field_measurements")
        if not measure:
            raise LedgerError("[FATAL] no prior excluded_field_measurements to carry forward")
    print(json.dumps(stats, indent=2))
    print("level:", Counter(a["level"] for a in attach["attachments"]))
    if args.dry_run:
        return 0
    if not new_rows:
        print("[error] 0 new rows -- refusing to overwrite committed output", flush=True)
        return 1
    if args.fetch or args.record_pin:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_FILE.write_bytes(sbytes)
    OUT_FILE.write_text(json.dumps(new_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ATTACH_FILE.write_text(json.dumps(attach, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PROVENANCE_FILE.write_text(json.dumps({
        "source": "https://hackingincidents.ai/",
        "snapshot": {
            "url": LEDGER_URL,
            "copy": "site copy (not the lagging Substrate repo copy, D159 U1)",
            "fetched_utc": fetched,
            "updated": updated,
            "rows": len(led),
            "raw_sha256": digest if is_raw else pin.get("raw_sha256"),
            "raw_bytes": len(body) if is_raw else pin.get("raw_bytes"),
            "file": _rel(SNAPSHOT_FILE),
            "sha256": sdigest,
            "bytes": len(sbytes),
            "stripped": True,
            "kept_fields": list(KEPT_ROW_FIELDS),
            "kept_source_fields": list(KEPT_SOURCE_FIELDS),
            "dropped_fields": pin.get("dropped_fields") if not is_raw else dropped_keys_present(obj),
        },
        "license": LICENSE_STRING,
        "citation": CITATION,
        "excluded_fields": list(EXCLUDED_FIELDS),
        "excluded_field_measurements": measure,
        "stats": stats,
        "review": review,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(new_rows)} rows, {len(attach['attachments'])} attachments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
