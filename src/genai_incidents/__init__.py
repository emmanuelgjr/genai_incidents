"""Python API for the GenAI & Agentic AI Security Incidents dataset.

The dataset is shipped as package data (``incidents.min.json``); no
network calls are made at import time. Use :func:`load_incidents` for
the full slim dataset, or :func:`query` for filtered access.

Example::

    from genai_incidents import query, by_cve, resolve_id

    # All Critical entries with a prompt-injection vector in 2026
    for inc in query(severity="Critical", attack_vector="prompt-injection", year=2026):
        print(inc["id"], inc["title"])

    # Look up a CVE
    print(by_cve("CVE-2026-21520"))

    # Resolve an old / merged-away ID
    print(resolve_id("INC-00139"))   # -> current canonical INC-* or None
"""

from __future__ import annotations

from importlib.resources import files
from functools import lru_cache
from typing import Any, Iterable, Iterator

__all__ = [
    "VERSION",
    "load_incidents",
    "load_schema",
    "load_deprecations",
    "query",
    "by_id",
    "by_cve",
    "resolve_id",
]

VERSION = "2.0.0"


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    import json

    text = files(__name__).joinpath("data/incidents.min.json").read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _load_deprecations() -> dict[str, str]:
    import json

    try:
        text = files(__name__).joinpath("data/id_deprecations.json").read_text(
            encoding="utf-8"
        )
    except FileNotFoundError:
        return {}
    data = json.loads(text)
    out: dict[str, str] = {}
    # A `from` ID can carry more than one tombstone record — e.g. an
    # older `merged` entry later superseded by a `resplit` (WS4-T15/
    # WS4-T22: INC-07771, INC-08109, INC-08133, INC-08146 each have
    # both). The most recent `date` wins, selected explicitly rather
    # than by "whichever the JSON array lists last" — the latter is an
    # accident of file order, not a decision, and this codebase has
    # already shipped that exact accident once (merge_and_dedupe.py's
    # `seen_from` kept the LAST record under a comment claiming
    # "earliest"). Ties (same date) fall back to file order for
    # determinism, matching the append-only convention that later
    # entries are written after earlier ones.
    latest_date: dict[str, str] = {}
    for entry in data.get("deprecations", []):
        f, t, date = entry.get("from"), entry.get("into"), entry.get("date") or ""
        if not f or not t:
            continue
        if f in out and date < latest_date[f]:
            continue
        out[f] = t
        latest_date[f] = date
    return out


def load_incidents() -> list[dict[str, Any]]:
    """Return the full list of (slim) incident records."""
    return list(_load_raw().get("incidents", []))


def load_schema() -> dict[str, Any]:
    """Return the JSON Schema as a Python dict."""
    import json

    text = files(__name__).joinpath("schema/incident.schema.json").read_text(
        encoding="utf-8"
    )
    return json.loads(text)


def load_deprecations() -> dict[str, str]:
    """Return ``{deprecated_id: canonical_id}`` mappings for retired IDs."""
    return dict(_load_deprecations())


def _matches(entry: dict, filters: dict) -> bool:
    for k, v in filters.items():
        if v is None:
            continue
        ev = entry.get(k)
        if isinstance(ev, list):
            if v not in ev:
                return False
        else:
            if ev != v:
                return False
    return True


def query(
    *,
    year: int | None = None,
    severity: str | None = None,
    attack_vector: str | None = None,
    owasp_llm: str | None = None,
    owasp_asi: str | None = None,
    corpus: str | None = None,
    quality_tier: str | None = None,
    tier: str | None = None,
    has_cve: bool | None = None,
    text: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Iterate over incidents matching all the given filters.

    All keyword arguments are ANDed together. ``owasp_llm``/``owasp_asi``
    accept a single code (e.g. ``"LLM01"``) and test membership in the
    entry's list. ``text`` does a case-insensitive substring match
    against ``id`` + ``title`` + ``cve_ids`` + ``primary_reference``.

    ``tier`` (``"landmark"`` / ``"feed"``) selects the notable subset the
    project's README asks consumers to cite, and is a different axis from
    ``quality_tier`` (vetting level) — neither substitutes for the other.

    **Carry-in caveat (WS6-T9, 2026-09-18):** the packaged
    ``incidents.min.json`` gained ``tier`` in the build code but the
    committed copy predates that change, so ``tier=`` matches nothing until
    the dataset is rebuilt and re-shipped. This filter is wired now, with the
    field, rather than after — a kwarg that silently ignores an argument is
    worse than one that is explicitly not yet populated.
    """
    filters = {
        "year": year,
        "severity": severity,
        "attack_vector": attack_vector,
        "owasp_llm": owasp_llm,
        "owasp_asi": owasp_asi,
        "corpus": corpus,
        "quality_tier": quality_tier,
        "tier": tier,
    }
    needle = text.lower().strip() if text else None
    for e in _load_raw().get("incidents", []):
        if not _matches(e, filters):
            continue
        if has_cve is True and not e.get("cve_ids"):
            continue
        if has_cve is False and e.get("cve_ids"):
            continue
        if needle:
            hay = " ".join(
                str(x) for x in (
                    e.get("id", ""),
                    e.get("title", ""),
                    " ".join(e.get("cve_ids") or []),
                    e.get("primary_reference") or "",
                )
            ).lower()
            if needle not in hay:
                continue
        yield e


def by_id(inc_id: str) -> dict[str, Any] | None:
    """Return the incident with the given ``INC-NNNNN`` id, or ``None``."""
    for e in _load_raw().get("incidents", []):
        if e.get("id") == inc_id:
            return e
    return None


def by_cve(cve: str) -> list[dict[str, Any]]:
    """Return every incident that lists ``cve`` in ``cve_ids``."""
    cve_u = cve.strip().upper()
    return [e for e in _load_raw().get("incidents", []) if cve_u in (e.get("cve_ids") or [])]


def resolve_id(inc_id: str) -> str | None:
    """Map a (possibly deprecated) ``INC-NNNNN`` ID to its current
    canonical ID. Returns the input unchanged if it's still active,
    follows the deprecation chain otherwise, and returns ``None`` if
    the chain doesn't terminate in a single, unambiguous existing entry.

    A record whose ``into`` is a list (a multi-successor ``split``/
    ``resplit`` record — WS4-T15) is walked like any other hop *when it
    has exactly one element*: a one-element list is an unambiguous,
    live successor, and there is nothing to disambiguate. It is only a
    list of TWO OR MORE elements that has no single canonical successor
    to walk to — for that case (and only that case) this function
    treats the record the same as a dangling/unknown ID and returns
    ``None`` rather than inventing an answer the data doesn't support
    (WS4-T22 / user ruling D31: picking one of N successors, even
    "the first", would fabricate a canonical answer). Before WS4-T22,
    this function discarded ALL list-valued hops uniformly — including
    the one-element case — on the false premise that any list means "no
    single successor"; that premise only holds for length >= 2, and the
    length == 1 case was a live, resolvable successor being silently
    dropped (12 published IDs affected across the corpus at the time of
    the fix, 4 of which had a single-element resplit target).

    Before the WS4-T15 fix that added the list check at all, the next
    chain hop did ``current in deprec`` with ``current`` bound to a
    list, which raises ``TypeError: unhashable type: 'list'`` — verified
    against WS4-T10's own array-valued ``split``/``resplit`` proposal.

    Callers that need every successor of a multi-target (two-or-more)
    record — i.e. the case this function still returns ``None`` for —
    should use :func:`resolve_id_group`, not this function."""
    if by_id(inc_id) is not None:
        return inc_id
    deprec = _load_deprecations()
    seen: set[str] = set()
    current = inc_id
    while current in deprec and current not in seen:
        seen.add(current)
        current = deprec[current]
        if isinstance(current, list):
            if len(current) != 1:
                return None
            current = current[0]
        if by_id(current) is not None:
            return current
    return None


def resolve_id_group(inc_id: str) -> list[str]:
    """Like :func:`resolve_id`, but returns EVERY successor a chain walk
    reaches, handling list-valued (multi-successor) ``into`` records.
    Returns ``[inc_id]`` if it's still active, ``[]`` if no live
    successor is reachable at all, and otherwise every currently-live ID
    the chain (fanning out through any list-valued hop) resolves to.
    Cycle-safe: a ``from`` visited twice on any branch is not re-walked."""
    if by_id(inc_id) is not None:
        return [inc_id]
    deprec = _load_deprecations()

    def _walk(node: str, seen: set[str]) -> list[str]:
        if node in seen:
            return []
        seen = seen | {node}
        if by_id(node) is not None:
            return [node]
        target = deprec.get(node)
        if target is None:
            return []
        targets = target if isinstance(target, list) else [target]
        out: list[str] = []
        for t in targets:
            out.extend(_walk(t, seen))
        return out

    # dict.fromkeys preserves first-seen order while de-duplicating.
    return list(dict.fromkeys(_walk(inc_id, set())))
