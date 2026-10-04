"""
corpus_overlap.py
=================

"Is this candidate row already in the corpus?", answered with the SAME keys
``scripts/merge_and_dedupe.py::dedupe_entries`` uses to fold rows together
(CVE > source id > normalized reference URL > fuzzy title +-1 year), so an
ingest script can leave out exactly the rows the merger would otherwise
absorb into an existing entry.

Why this exists (measured 2026-10-03, wave-1/2 ingest): a new CVE-keyed row
that shares a reference URL or a title with an existing entry that carries no
CVE ids (a GHSA-keyed advisory, an AVID-keyed row, a blog write-up) is merged
into that entry by the merger -- changing its title, severity, quality_tier,
even its date -- and a new row sharing a URL with a grandfathered multi-CVE
entry splits it (aborted by the WS4-T19 guard). Both are field changes the
ingest was never meant to make. Instead of tolerating them, the ingest
SKIPS such rows and records the collision (row id -> the existing INC id and
the key kind) in its provenance file, so nothing is lost and the existing
entry is left exactly as it was.

Who can absorb a row (mirrors ``cve_disjoint``): weak keys (URL, title) never
bridge two entries whose CVE sets are both non-empty and disjoint, so a row
WITH CVE ids can only be absorbed by a corpus entry with NO cve_ids; a row
WITHOUT cve_ids can be absorbed by any corpus entry.
"""

from __future__ import annotations

import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_and_dedupe import normalize_url, title_key  # noqa: E402

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,9}")
AVID_ID_RE = re.compile(r"AVID-\d{4}-[RV]\d{3,4}", re.I)


class CorpusIndex:
    def __init__(self, corpus: list[dict], avid_crosswalk: dict[str, list[str]] | None = None):
        self.cves: dict[str, str] = {}       # CVE id (anywhere in the entry) -> INC id
        self.avid_ids: dict[str, str] = {}   # AVID id (anywhere) -> INC id
        self.src_ids: dict[str, str] = {}
        self.urls_all: dict[str, str] = {}   # normalized url -> INC id
        self.urls_nocve: dict[str, str] = {}
        self.titles_all: dict[str, list[tuple[int, str]]] = {}
        self.titles_nocve: dict[str, list[tuple[int, str]]] = {}
        for e in corpus:
            eid = e.get("id", "?")
            text = " ".join([" ".join(e.get("cve_ids") or []), " ".join(e.get("source_ids") or []),
                             e.get("title") or "",
                             " ".join(r.get("url") or "" for r in e.get("references") or [])])
            for m in CVE_RE.findall(text):
                self.cves.setdefault(m.upper(), eid)
            for m in AVID_ID_RE.findall(text):
                self.avid_ids.setdefault(m.upper(), eid)
            for s in e.get("source_ids") or []:
                self.src_ids.setdefault(s, eid)
            has_cve = bool(e.get("cve_ids"))
            tk = title_key(e.get("title") or "")
            self.titles_all.setdefault(tk, []).append((e.get("year") or 0, eid))
            if not has_cve:
                self.titles_nocve.setdefault(tk, []).append((e.get("year") or 0, eid))
            for r in e.get("references") or []:
                u = normalize_url(r.get("url") or "")
                if not u:
                    continue
                self.urls_all.setdefault(u, eid)
                if not has_cve:
                    self.urls_nocve.setdefault(u, eid)
        # An AVID-keyed corpus entry that lacks the CVE in its own text still
        # stands for that CVE: AVID's repo says so.
        for aid, cves in (avid_crosswalk or {}).items():
            eid = self.avid_ids.get(aid.upper())
            if eid:
                for c in cves:
                    self.cves.setdefault(c.upper(), eid)

    def collision(self, row: dict, *, skip_urls: set[str] | None = None) -> tuple[str, str] | None:
        """-> (kind, existing INC id) if the merger would fold *row* into an
        existing entry, else None. *skip_urls* are normalized URLs that are
        the row's own identity (e.g. its AVID page) and never count."""
        skip_urls = skip_urls or set()
        row_cves = {c.upper() for c in ([row["cve_id"]] if row.get("cve_id") else []) + list(row.get("cve_ids") or [])}
        for c in sorted(row_cves):
            if c in self.cves:
                return "cve", self.cves[c]
        if row.get("source_id") and row["source_id"] in self.src_ids:
            return "source_id", self.src_ids[row["source_id"]]
        urls = self.urls_nocve if row_cves else self.urls_all
        for r in row.get("references") or []:
            u = normalize_url(r.get("url") or "")
            if u and u not in skip_urls and u in urls:
                return "url", urls[u]
        titles = self.titles_nocve if row_cves else self.titles_all
        tk = title_key(row.get("title") or "")
        for year, eid in titles.get(tk, []):
            if abs((year or 0) - (row.get("year") or 0)) <= 1:
                return "title", eid
        return None
