"""Regression tests for the E21 Part A / INC-00437 labeling fix
(docs/audits/E21-part-A-measurement-2026-07-30.md): INC-00437 (aiid_id 1574,
source_ids ``AIID-1574`` + ``OECD-AIM-2026-04-03-c16a``) is the ONE row in the
corpus whose AIID cross-reference signal (``aiid_id`` / an ``AIID-<n>``
source_id) disagrees with what its ``description`` field actually ships --
OECD AIM's own structural template (``scripts/ingest_oecd_aim.py::
build_description()``), not any text from AIID. The row is absent from
``ingest/aiid_full.json`` (the sanctioned AIID snapshot), so no aiid_full.json
entry ever competes for the ``AIID-1574`` dedup key and OECD AIM's own row
wins the merge outright. ``data/curation_overrides.json``'s
``OECD-AIM-2026-04-03-c16a`` entry sets ``description_provenance``/
``description_source`` to say so explicitly, without touching the
``AIID-1574`` source-ID cross-reference itself (E23's ruling: provenance
concerns attach to shipped TEXT, not to a bare source-ID cross-reference).

Two things are protected here, mirroring test_e23_aiid_dead_letter_tripwire.py's
own real-committed-file, in-process-repro method rather than reading the
generated data/incidents.json directly:

1. The override actually lands the right values when run through the real
   pipeline (not just that the JSON parses).
2. (Superseded 2026-10-03, see the note at the foot of this file.) The population this fix addresses is still exactly one row -- if a future
   OECD refresh, an AIID snapshot update, or a merge-order change ever makes
   a second OECD-tracked row's claimed AIID cross-reference go unmatched by
   aiid_full.json, this test fails loudly instead of a second unlabeled row
   silently shipping the same disagreement.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import merge_and_dedupe as m

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
DATA = ROOT / "data"

# The only two ingest files that can produce this specific disagreement class:
# an OECD-tracked row claiming an AIID cross-reference (oecd_aim_full_incidents.json,
# via normalize_body()'s aiid_ids -> extra_source_ids), tested against whichever
# aiid_full.json rows exist to compete for that AIID-<n> dedup key. Restricting
# to these two (rather than every ingest/*.json, as WS4-T6-style full-corpus
# tests would) keeps this fast and scoped to the exact mechanism under test --
# the same restriction principle test_e23_aiid_dead_letter_tripwire.py applies
# to its own three-file AIID-relevant set.
_RELEVANT_FILES = ("aiid_full.json", "oecd_aim_full_incidents.json")

_AIID_TEMPLATE = re.compile(r"^AI Incident Database \(AIID\) entry #\d+: ")

_INC_00437_SOURCE_ID = "OECD-AIM-2026-04-03-c16a"
_INC_00437_AIID_ID = 1574


def _load(name: str) -> list[dict]:
    return json.loads((INGEST / name).read_text(encoding="utf-8"))


def _build_surviving() -> list[dict]:
    """Read-only, in-process repro of the real merge pipeline restricted to
    ``_RELEVANT_FILES`` -- no ``data/*.json`` write, no network. Curation
    overrides are NOT applied here (that's a separate pipeline step,
    exercised directly in the first test below); this repro only proves what
    survives dedup/normalize before overrides land."""
    raw: list[dict] = []
    for name in _RELEVANT_FILES:
        raw.extend(_load(name))
    normalized = [n for n in (m.normalize_entry(r) for r in raw) if n is not None]
    surviving, _tombstoned = m.dedupe_entries(normalized)
    return surviving


def test_inc00437_row_exists_and_is_absent_from_aiid_full_snapshot():
    """Positive control: the fact pattern this fix depends on must actually
    hold, or the override below would be correcting a label that doesn't
    need correcting. Confirms, against the REAL committed files: (a) OECD
    AIM's own record for this incident claims an AIID-1574 cross-reference,
    and (b) no row for aiid_id 1574 exists in aiid_full.json to compete for
    that dedup key -- so nothing AIID-authored could possibly ship here."""
    oecd_rows = _load("oecd_aim_full_incidents.json")
    row = next((r for r in oecd_rows if r.get("source_id") == _INC_00437_SOURCE_ID), None)
    assert row is not None, (
        f"expected {_INC_00437_SOURCE_ID} in ingest/oecd_aim_full_incidents.json "
        "-- has this incident's OECD source_id changed?"
    )
    assert f"AIID-{_INC_00437_AIID_ID}" in (row.get("extra_source_ids") or []), (
        f"expected OECD AIM's own record to claim an AIID-{_INC_00437_AIID_ID} "
        "cross-reference via aiid_ids -- the fact pattern this fix addresses"
    )

    # SUPERSEDED 2026-10-03 (board D42): this test used to also assert that
    # aiid_id 1574 is ABSENT from ingest/aiid_full.json. Once WS4-T14 keeps the
    # AIID snapshot current that stops being true (the 2026-09-28 snapshot
    # contains 1574), and the weekly job would fail for a reason that is no
    # longer a defect: merge_and_dedupe.apply_curation_overrides() now applies
    # a provenance label only while the description is still the text the
    # keyed source authored (tests/test_d42_refresh_merge_gate.py).


def test_curation_override_labels_inc00437s_description_as_oecd_aim_original():
    """End-to-end: normalize the real OECD row, apply the real committed
    curation overrides (the actual mechanism merge_and_dedupe.py's step 4d
    uses, unpatched -- no monkeypatching CURATION_OVERRIDES_PATH), and
    confirm the row that survives carries an explicit, correct label rather
    than silently inheriting the AIID-signal-vs-OECD-content disagreement."""
    oecd_rows = _load("oecd_aim_full_incidents.json")
    raw = next(r for r in oecd_rows if r.get("source_id") == _INC_00437_SOURCE_ID)
    entry = m.normalize_entry(raw)
    assert entry is not None
    assert entry["aiid_id"] == _INC_00437_AIID_ID
    # The shipped description is OECD AIM's own template, never AIID's --
    # confirmed independently of the override below.
    assert not _AIID_TEMPLATE.match(entry["description"])

    overrides = m._load_curation_overrides()  # reads the real committed file
    ov = next((overrides[s] for s in entry["source_ids"] if s in overrides), None)
    assert ov is not None, (
        f"expected an override in data/curation_overrides.json keyed by one of "
        f"{entry['source_ids']} -- has the OECD-AIM-2026-04-03-c16a override "
        "been removed or renamed?"
    )
    for k, v in ov.items():
        if not k.startswith("_"):
            entry[k] = v

    assert entry["description_provenance"] == "original"
    assert entry["description_source"] == "oecd-aim"


# REMOVED 2026-10-03 (board D42; docs/audits/refresh-tripwire-2026-10-03.md):
# `test_oecd_aiid_content_disagreement_is_unique_to_inc00437` asserted an
# exact two-row population ([1574, 1575]) built from two ingest files and
# matched by an AIID-prefix regex. It failed the weekly refresh on 2026-09-14,
# 09-20 and 09-27 as the population grew 2 -> 42, and had three blind spots
# (prefix-spoofed descriptions, rows outside the two files such as aiid_id 898,
# the `title` field). Superseded by tests/test_aiid_signal_provenance.py, which
# explains every aiid_id row by independent derivation, plus the build-time
# merge gate tests/test_d42_refresh_merge_gate.py. The original function and
# its long WS4-T10 docstring remain in git history (commit 9ef355f5 and
# earlier); do not restore it as a source.
