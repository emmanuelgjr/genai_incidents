"""D133: a change to ``taxonomy_versions`` must move the timestamp of exactly the
exported objects whose content it changes.

STIX: only the ``identity`` object carries ``x_taxonomy_versions`` -> only its
``modified`` may move. MISP: every event carries the version machinetags ->
every event ``timestamp`` must move. Before this fix both stayed put when
``owasp_dsgai`` was added (a client deduping on (id, modified) never saw it).
"""

from __future__ import annotations

import pytest

import export_misp as misp
import export_stix as s
import taxonomy_versions as tvm

_INC = [{"id": "INC-00001", "title": "t", "description": "d", "date": "2026-01", "year": 2026,
         "added": "2026-01-02", "updated": "2026-01-04", "references": [], "tags": []}]


def _use(monkeypatch, tv):
    for mod in (tvm, misp, s):
        monkeypatch.setattr(mod, "taxonomy_versions", lambda *a, **k: dict(tv))


def _stix(monkeypatch, tv):
    _use(monkeypatch, tv)
    return {o["id"]: o for o in s.build_bundle(_INC)["objects"]}


# Every registered transition (rows 1->2 D133, 2->3 ATLAS 2026.10, 3->4 D146-2).
_PAIRS = list(zip(tvm.REVISIONS, tvm.REVISIONS[1:]))


@pytest.mark.parametrize("old,new", _PAIRS)
def test_stix_only_identity_modified_moves(monkeypatch, old, new):
    a, b = _stix(monkeypatch, old), _stix(monkeypatch, new)
    moved = {k for k in a if a[k]["modified"] != b[k]["modified"]}
    changed = {k for k in a if {x: y for x, y in a[k].items() if x != "modified"}
               != {x: y for x, y in b[k].items() if x != "modified"}}
    assert moved == changed
    assert len(moved) == 1 and next(iter(moved)).startswith("identity--")
    ident = next(iter(moved))
    assert b[ident]["modified"] > a[ident]["modified"]


def test_stix_build_twice_identical(monkeypatch):
    _use(monkeypatch, tvm.REVISIONS[-1])
    assert s.build_bundle(_INC) == s.build_bundle(_INC)


@pytest.mark.parametrize("old_tv,new_tv", _PAIRS)
def test_misp_every_event_timestamp_moves(monkeypatch, old_tv, new_tv):
    _use(monkeypatch, old_tv)
    old = misp._event_meta(2026, _INC)
    _use(monkeypatch, new_tv)
    new = misp._event_meta(2026, _INC)
    assert old["Tag"] != new["Tag"]
    assert int(new["timestamp"]) > int(old["timestamp"])


def test_unregistered_change_fails_the_build(monkeypatch):
    """A re-pin not appended to REVISIONS must raise, not publish silently."""
    _use(monkeypatch, {**tvm.REVISIONS[-1], "veris": "9.9"})
    with pytest.raises(ValueError, match="REVISIONS"):
        s.build_bundle(_INC)
    with pytest.raises(ValueError, match="REVISIONS"):
        misp._event_meta(2026, _INC)


def test_current_pins_are_registered():
    assert tvm.REVISIONS[-1] == tvm.taxonomy_versions()
    assert tvm.tv_revision() == len(tvm.REVISIONS)
