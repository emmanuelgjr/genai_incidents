"""``taxonomy_versions.REVISIONS`` is append-only: a published row never changes.

A row's 1-based position is the *taxonomy revision* added to the STIX
``identity`` ``modified`` and every MISP event ``timestamp``
(``scripts/taxonomy_versions.py``). Editing, reordering or deleting a published
row silently changes what revision N meant, so a consumer deduping on
(id, modified) / timestamp can miss a change or see one that never happened.
Before this test nothing caught that: the D146-2 gate rewrote row 2 (mutation
M3) and every other test still passed.

How it works: ``_FROZEN`` holds one sha256 per published row, in order (the
digest of the row as canonical JSON, keys sorted). Every frozen row must still
be present, unchanged, at its position. At most ONE row past the frozen ones
is allowed (the newest, possibly not yet published), so:

* appending row 5 needs no edit here;
* appending row 6 fails until row 5's digest is added to ``_FROZEN`` -- the
  failure message prints the exact line to paste.

Frozen digests were checked against git history on 2026-11-10: each row's
digest is identical in every commit since that row was introduced (67bb0480,
c456ae3f, f54f9b88, 7d9fc282), and row 1 equals the ``taxonomy_versions`` in
``data/stats.json`` at tag v2.13.0.
"""

from __future__ import annotations

import hashlib
import json

import taxonomy_versions as tvm

# One entry per published REVISIONS row, oldest first. APPEND ONLY.
_FROZEN = (
    "e536081a75be7b17c05438df5fe010624db234d6f02f3232baaf4c36f2179744",  # 1 v2.13.0
    "70e3f3a176cda68a2bec4a02f7d9a32362eae7923c98a11d8e5140dc422d1c08",  # 2 D133 owasp_dsgai
    "8d74c826f3d0f7b71497de72063382aefe9929ca3d6bea9e71d50f8327f7768b",  # 3 ATLAS 2026.10
    "d374465c67e1aa0c73e114bd9c3090a1e7b14c4a815f05e2d5637a0b67b599b9",  # 4 D146-2 maestro, nist_ai_rmf
)


def _digest(row: dict) -> str:
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def test_published_rows_are_unchanged_and_in_place():
    rows = tvm.REVISIONS
    assert len(rows) >= len(_FROZEN), (
        f"REVISIONS has {len(rows)} rows but {len(_FROZEN)} are published and frozen: "
        "a published row was deleted. REVISIONS is append-only; restore it.")
    bad = [n for n, (row, want) in enumerate(zip(rows, _FROZEN), 1) if _digest(row) != want]
    assert not bad, (
        f"published REVISIONS row(s) {bad} changed (edited, reordered or a row was "
        "removed before them). REVISIONS is append-only: restore the published rows "
        "and append any new pin set as a new last row.")


def test_at_most_one_unfrozen_row():
    extra = tvm.REVISIONS[len(_FROZEN):]
    if len(extra) <= 1:
        return
    lines = "\n".join(
        f'    "{_digest(r)}",  # {n}'
        for n, r in enumerate(extra[:-1], len(_FROZEN) + 1))
    raise AssertionError(
        f"REVISIONS has {len(extra)} rows past the frozen ones; only the newest may be "
        "unfrozen. Freeze the earlier one(s) by appending these lines to _FROZEN in "
        f"tests/test_taxonomy_revisions_frozen.py (after checking the row(s) were not "
        f"edited since they were added -- `git log -p scripts/taxonomy_versions.py`):\n{lines}")


def test_rows_are_distinct():
    # tv_revision() returns the FIRST match, so a duplicated row would never be
    # reached and its revision bump would silently not happen.
    digests = [_digest(r) for r in tvm.REVISIONS]
    dup = sorted({n for n, d in enumerate(digests, 1) if digests.count(d) > 1})
    assert not dup, f"REVISIONS rows {dup} are identical; each row must be a distinct pin set"
