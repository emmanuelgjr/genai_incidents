"""Which entry `status` values take a row OUT of the standing incident count.

One list, read by every producer that counts or exports rows (merge envelope,
stats.json, INCIDENTS.md, the site payload, STIX/TAXII/MISP/Hugging Face,
validate.py and the drift check), so a new excluded status cannot reach some
surfaces and not others.

* ``retracted`` (WS4-T2): every CVE the entry rests on is REJECTED upstream.
* ``unverified`` (user ruling D130): the entry's references could not be
  replaced by a confirmed primary source after a documented effort. Set only
  through ``data/curation_overrides.json`` (see merge_and_dedupe.py,
  ``_apply_unverified_override``), never derived and never hand-edited.

Both stay in ``data/incidents.json`` (invariant 3: never deleted; the ID keeps
resolving) and are counted in their own ``<status>_count``. ``disputed`` is
NOT here: a disputed entry stands and stays counted (D61/D64).
"""
from __future__ import annotations

NOT_STANDING: frozenset[str] = frozenset({"retracted", "unverified"})


def stands(entry: dict) -> bool:
    """True when the entry counts as an incident (no excluding status)."""
    return entry.get("status") not in NOT_STANDING
