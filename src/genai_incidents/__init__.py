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

    # Why an ID resolves the way it does (never silence)
    print(resolve_id_status("INC-00497", release="v2.1.0"))
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.resources import files
from functools import lru_cache
import re
from typing import Any, Iterable, Iterator, Literal

__all__ = [
    "VERSION",
    "load_incidents",
    "load_schema",
    "load_deprecations",
    "taxonomy_versions",
    "query",
    "by_id",
    "by_cve",
    "resolve_id",
    "resolve_id_group",
    "resolve_id_status",
    "IdStatus",
]

VERSION = "2.0.0"


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    import json

    text = files(__name__).joinpath("data/incidents.min.json").read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _load_deprecations() -> dict[str, str | list[str]]:
    import json

    try:
        text = files(__name__).joinpath("data/id_deprecations.json").read_text(
            encoding="utf-8"
        )
    except FileNotFoundError:
        return {}
    data = json.loads(text)
    out: dict[str, str] = {}
    # A `from` ID can carry more than one tombstone record (e.g. an older
    # `merged` entry later superseded by a `resplit`: INC-07771, INC-08109,
    # INC-08133, INC-08146). RULE: the LAST record in file order wins.
    # Why: the deprecations file is append-only, so file order is decision
    # order; this is the repo-wide contract and it must stay identical to
    # `scripts/validate.py::_latest_by_from` (and the fixpoint in
    # `scripts/merge_and_dedupe.py`). Do NOT select by `date` here: dates
    # can be absent or out of order, and a package that disagrees with the
    # validator returns a live-but-wrong ID. tests/test_package.py
    # cross-checks this loader against `_latest_by_from`.
    #
    # Release-scoped records (carrying `valid_for_releases`, v2.13.0 / D49)
    # answer "what did this ID mean in release X" and are NOT part of this
    # unscoped view; only `resolve_id_status(..., release=)` reads them.
    # The data never makes this skip load-bearing: every scoped record is
    # followed by an unscoped record for the same `from`
    # (scripts/validate.py enforces it), so last-in-file-wins over ALL
    # records gives the same answer. The skip is defence in depth.
    for entry in data.get("deprecations", []):
        if "valid_for_releases" in entry:
            continue
        f, t = entry.get("from"), entry.get("into")
        if f and t:
            out[f] = t
    return out


@lru_cache(maxsize=1)
def _load_deprecation_records() -> tuple[dict[str, Any], ...]:
    """Every record in ``data/id_deprecations.json``, in file order."""
    import json

    try:
        text = files(__name__).joinpath("data/id_deprecations.json").read_text(
            encoding="utf-8"
        )
    except FileNotFoundError:
        return ()
    return tuple(json.loads(text).get("deprecations", []))


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


def load_deprecations() -> dict[str, str | list[str]]:
    """Return ``{deprecated_id: into}`` mappings for retired IDs.

    The value is ``str | list[str]``: a single canonical id for a merge or
    rename, or a LIST of successor ids for a ``split``/``resplit`` record.
    v2.11.0 is the first release whose bundled data carries list values (8 of
    293 records); every earlier release shipped strings only, so a consumer
    written against ``dict[str, str]`` (including v2.10.0's own
    ``resolve_id``) can raise ``TypeError`` on v2.11.0 data. Use
    ``resolve_id`` / ``resolve_id_group`` rather than indexing the mapping.

    Release-scoped records (``valid_for_releases``, v2.13.0) are not in this
    mapping; it is the release-independent view. Use
    ``resolve_id_status(id, release=...)`` for a per-release answer.
    """
    return dict(_load_deprecations())


def _canonical_release(release: str) -> str:
    """``"2.3.0"`` or ``"v2.3.0"`` -> ``"v2.3.0"``; anything else raises."""
    r = release.strip()
    if not r.startswith("v"):
        r = "v" + r
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", r):
        raise ValueError(f"release must look like 'v2.3.0', got {release!r}")
    return r


def taxonomy_versions() -> dict[str, str | None]:
    """Return the versions of the pinned taxonomies this release's framework
    codes belong to, e.g. ``{"atlas": "2026.09", "owasp_llm": "2026",
    "owasp_asi": "2025", "capec": None, "veris": "1.4.1"}``.

    Same dict as ``taxonomy_versions`` in the repository's ``data/stats.json``
    (derived from the pinned ``mappings/*.json`` at build time). A value of
    ``None`` means that taxonomy's pin does not record a version (CAPEC today).
    """
    import json

    text = files(__name__).joinpath("data/taxonomy_versions.json").read_text(
        encoding="utf-8"
    )
    return dict(json.loads(text))


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

    **Carry-in caveat (WS6-T9, 2026-09-18; corrected 2026-10-01):** this
    note originally said ``tier=`` matched nothing until the dataset was
    rebuilt. That is no longer true: the packaged ``incidents.min.json`` now
    carries ``tier``, and ``query(tier="landmark")`` returns the landmark
    set. Releases before v2.11.0 do not accept ``tier=``.
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
    should use :func:`resolve_id_group`, not this function. To learn WHY
    this function returned ``None`` (a split group, a release-dependent ID,
    a pre-tombstone drop, a withdrawal), use :func:`resolve_id_status`."""
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


# --- v2.13.0 / user ruling D49: resolve_id_status ----------------------

IdStatusKind = Literal[
    "live",
    "successor",
    "group",
    "release-dependent",
    "pre-tombstone",
    "withdrawn",
    "unknown",
]

# Deprecation `reason` values that mark an ID published before the
# tombstone machinery existed (2026-05-16) and dropped without a record;
# the record was appended later (docs/ID_POLICY.md section 1.4(a)).
_PRE_TOMBSTONE_REASONS = frozenset({"unrecorded-drop-v2.1.0"})


@dataclass(frozen=True)
class IdStatus:
    """Typed answer from :func:`resolve_id_status`. Never silence: every
    input gets a ``status`` naming why it resolves the way it does.

    ``status`` is one of:

    - ``"live"``: the ID is a current entry; ``successor`` is the ID.
    - ``"successor"``: retired, with exactly one live successor
      (``successor``). With ``release=``, also the answer for an ID whose
      meaning depended on the release, when that release is covered.
    - ``"group"``: retired and split; no single successor exists.
      ``successor`` is ``None``; ``group`` holds every live successor.
    - ``"release-dependent"``: the ID named different incidents in
      different releases and no ``release=`` was given, so no single
      answer exists; ``by_release`` maps each release to its successor.
      Pass ``release=`` to get one.
    - ``"pre-tombstone"``: published in v2.0.0, dropped in v2.1.0 before
      tombstones existed; no successor exists in the corpus.
    - ``"withdrawn"``: retired with no successor (e.g. out of scope).
    - ``"unknown"``: this project has no record of the ID.

    ``group`` is :func:`resolve_id_group` for the same input (for a
    covered ``release=``, for that release's successor), empty when
    nothing live is reachable. ``by_release`` is filled only for IDs that
    carry release-scoped records (``valid_for_releases``). ``reason`` is
    the deciding deprecation record's ``reason`` (``None`` for live and
    unknown IDs). ``release`` echoes the normalised ``release=``."""

    id: str
    status: IdStatusKind
    successor: str | None = None
    group: tuple[str, ...] = ()
    by_release: dict[str, str] = field(default_factory=dict, hash=False)
    reason: str | None = None
    release: str | None = None


def _scoped_records(inc_id: str) -> list[dict[str, Any]]:
    return [
        r for r in _load_deprecation_records()
        if r.get("from") == inc_id and "valid_for_releases" in r
    ]


def _latest_unscoped_record(inc_id: str) -> dict[str, Any] | None:
    latest = None
    for r in _load_deprecation_records():
        if r.get("from") == inc_id and "valid_for_releases" not in r:
            latest = r
    return latest


def resolve_id_status(inc_id: str, release: str | None = None) -> IdStatus:
    """Explain how ``inc_id`` resolves, as a typed :class:`IdStatus`.

    Unlike :func:`resolve_id` (unchanged, ``str | None``), this never
    answers with silence: a split ID is ``"group"`` with its set, an ID
    whose meaning changed between releases is ``"release-dependent"``, an
    ID dropped before tombstones existed is ``"pre-tombstone"``.

    ``release`` (``"v2.3.0"`` or ``"2.3.0"``) is the release the citation
    came from. ``None`` means "current": the release-independent answer.
    It only matters for an ID that carries release-scoped deprecation
    records (``valid_for_releases``, e.g. ``INC-00497``, ``INC-08139``):
    when the release is listed on one of them, that record's successor is
    the answer (status ``"successor"``). A release not listed on any of
    them (including one in which the ID was already a tombstone) gets the
    release-independent answer. For every other ID ``release`` is ignored:
    a live ID's meaning is not re-checked against old releases.
    Raises ``ValueError`` for a malformed ``release``."""
    rel = _canonical_release(release) if release is not None else None
    if by_id(inc_id) is not None:
        return IdStatus(inc_id, "live", inc_id, (inc_id,), release=rel)

    scoped = _scoped_records(inc_id)
    by_release: dict[str, str] = {}
    for r in scoped:
        for v in r.get("valid_for_releases") or []:
            by_release[v] = r.get("into")
    if rel is not None and rel in by_release:
        rec = [r for r in scoped if rel in (r.get("valid_for_releases") or [])][-1]
        target = rec.get("into")
        live = resolve_id(target)
        tgroup = tuple(resolve_id_group(target))
        if live is not None:
            kind: IdStatusKind = "successor"
        else:
            kind = "group" if tgroup else "withdrawn"
        return IdStatus(inc_id, kind, live, tgroup, by_release, rec.get("reason"), rel)

    group = tuple(resolve_id_group(inc_id))
    latest = _latest_unscoped_record(inc_id)
    reason = latest.get("reason") if latest else None
    if scoped and rel is None:
        return IdStatus(inc_id, "release-dependent", None, group, by_release, reason, rel)
    if reason in _PRE_TOMBSTONE_REASONS:
        return IdStatus(inc_id, "pre-tombstone", None, group, by_release, reason, rel)
    single = resolve_id(inc_id)
    if single is not None:
        return IdStatus(inc_id, "successor", single, group, by_release, reason, rel)
    if group:
        return IdStatus(inc_id, "group", None, group, by_release, reason, rel)
    if latest is None:
        return IdStatus(inc_id, "unknown", None, (), by_release, None, rel)
    # A record exists but nothing live is reachable: scripts/validate.py
    # guarantees such a chain ends at an explicit `into: null` record.
    return IdStatus(inc_id, "withdrawn", None, (), by_release, reason, rel)
