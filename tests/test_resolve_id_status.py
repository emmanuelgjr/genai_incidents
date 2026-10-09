"""v2.13.0 item 4 / user ruling D49: resolve_id_status(), the appended
deprecation records, and the proof that resolve_id() did not change beyond
the two declared successors.

Every test names the input that makes it fail (working agreement 6)."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import genai_incidents as gi  # noqa: E402
import validate as v  # noqa: E402

DEP_PATH = ROOT / "data" / "id_deprecations.json"
PKG_DEP_PATH = ROOT / "src" / "genai_incidents" / "data" / "id_deprecations.json"
APPENDS_PATH = ROOT / "docs" / "audits" / "ID-silent-ids-appends-2026-10-09.json"
GOLDEN_PATH = ROOT / "tests" / "fixtures" / "resolve_id_golden_816b9271.json"
DEP_SCHEMA_PATH = ROOT / "schema" / "id_deprecations.schema.json"

# main @ 816b9271's data/id_deprecations.json (1,060 records), minus its
# closing "\n  ]\n}" (6 bytes): the bytes every later file must start with.
# Re-derive:
#   git show 816b9271:data/id_deprecations.json | python -c "import sys,hashlib; b=sys.stdin.buffer.read()[:-6]; print(len(b), hashlib.sha256(b).hexdigest())"
MAIN_PREFIX_LEN = 135878
MAIN_PREFIX_SHA256 = "392c45a54204a6d3588558bac435be94cc66f1aac91d1032f3531553a5e2e18d"
MAIN_RECORD_COUNT = 1060

# The 17 published IDs that answered with silence at 816b9271, with the
# status class each must now report (release=None) and its single answer.
# Re-derivation of the 17: docs/ID_POLICY.md section 8.5.
SILENT_17 = {
    "INC-03128": ("successor", "INC-14909"),
    "INC-08185": ("successor", "INC-14742"),
    "INC-00311": ("group", None),
    "INC-00554": ("group", None),
    "INC-00754": ("group", None),
    "INC-01897": ("group", None),
    "INC-00497": ("release-dependent", None),
    "INC-08139": ("release-dependent", None),
    **{i: ("pre-tombstone", None) for i in (
        "INC-00522", "INC-00609", "INC-00951", "INC-00952", "INC-00955",
        "INC-00956", "INC-00957", "INC-01355", "INC-01660",
    )},
}
GROUP_SIZES = {"INC-00311": 12, "INC-00554": 100, "INC-00754": 11, "INC-01897": 8}

# What a citation from each release means (derived from each tag's own
# data/incidents.json by title; docs/ID_POLICY.md section 8.5).
BY_RELEASE = {
    "INC-00497": {
        **{r: "INC-14789" for r in ("v2.0.0", "v2.1.0")},
        **{r: "INC-14907" for r in ("v2.2.0", "v2.3.0", "v2.3.1", "v2.4.0",
                                    "v2.5.0", "v2.6.0", "v2.7.0", "v2.8.0")},
    },
    "INC-08139": {
        **{r: "INC-14852" for r in ("v2.2.0", "v2.3.0", "v2.3.1", "v2.4.0", "v2.5.0")},
        **{r: "INC-14742" for r in ("v2.6.0", "v2.7.0")},
    },
}

# The ONLY resolve_id()/resolve_id_group() answers allowed to differ from
# main @ 816b9271: the two successor records the user's item asked for.
DECLARED_CHANGES = {"INC-03128": "INC-14909", "INC-08185": "INC-14742"}


def _records():
    return json.loads(DEP_PATH.read_text(encoding="utf-8"))["deprecations"]


# --- 1. each of the 17 returns its status class --------------------------

@pytest.mark.parametrize("inc_id", sorted(SILENT_17))
def test_each_silent_id_has_its_status_class(inc_id):
    # Fails if a record is missing/reverted (e.g. drop the INC-03128 record
    # and it reads "group"; drop a pre-tombstone record and it reads
    # "unknown"), or if the classifier's branch order changes.
    want_status, want_successor = SILENT_17[inc_id]
    st = gi.resolve_id_status(inc_id)
    assert (st.status, st.successor) == (want_status, want_successor), st
    assert st.id == inc_id and st.release is None
    if want_status == "group":
        assert len(st.group) == GROUP_SIZES[inc_id]
        assert gi.resolve_id(inc_id) is None
    if want_status == "release-dependent":
        assert st.by_release == BY_RELEASE[inc_id]
        assert len(st.group) >= 2  # the release-independent fan-out survives
    if want_status == "pre-tombstone":
        assert st.group == () and st.reason == "unrecorded-drop-v2.1.0"


def test_no_silent_id_is_unknown_any_more():
    # The whole point: none of the 17 may come back "unknown" (silence).
    assert all(gi.resolve_id_status(i).status != "unknown" for i in SILENT_17)


@pytest.mark.parametrize("inc_id", sorted(BY_RELEASE))
def test_release_dependent_ids_resolve_per_release(inc_id):
    # Fails if a valid_for_releases list is wrong or the release lookup
    # picks the wrong record.
    for rel, want in BY_RELEASE[inc_id].items():
        st = gi.resolve_id_status(inc_id, release=rel)
        assert (st.status, st.successor, st.release) == ("successor", want, rel), (rel, st)
        assert st.group == (want,)
        # "2.3.0" and "v2.3.0" are the same release.
        assert gi.resolve_id_status(inc_id, release=rel[1:]) == st
    # A release not covered (the ID was already a tombstone then) gets the
    # release-independent answer, not a guess.
    for rel in ("v2.9.0", "v2.12.0", "v9.9.9"):
        assert gi.resolve_id_status(inc_id, release=rel).status == "group"


def test_release_is_ignored_for_ids_without_scoped_records():
    for inc_id in ("INC-03128", "INC-00311", "INC-00522"):
        assert gi.resolve_id_status(inc_id, release="v2.0.0").status == SILENT_17[inc_id][0]


def test_live_withdrawn_unknown_and_bad_release():
    live = gi.load_incidents()[0]["id"]
    assert gi.resolve_id_status(live) == gi.IdStatus(live, "live", live, (live,))
    assert gi.resolve_id_status("INC-00004").status == "withdrawn"  # out-of-scope
    assert gi.resolve_id_status("INC-00004").reason == "out-of-scope"
    assert gi.resolve_id_status("INC-99999999").status == "unknown"
    with pytest.raises(ValueError):
        gi.resolve_id_status("INC-00497", release="latest")


def test_every_published_status_is_one_of_the_documented_kinds():
    import typing
    kinds = set(typing.get_args(gi.IdStatusKind))
    assert kinds == {"live", "successor", "group", "release-dependent",
                     "pre-tombstone", "withdrawn", "unknown"}
    froms = {d["from"] for d in _records()}
    assert {gi.resolve_id_status(i).status for i in froms} <= kinds


def test_exported_in_package_api():
    for name in ("resolve_id_status", "IdStatus", "resolve_id", "resolve_id_group"):
        assert name in gi.__all__
    assert hash(gi.resolve_id_status("INC-00497")) is not None  # frozen + hashable


# --- 2. resolve_id() unchanged: golden comparison against main ----------

def _golden():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_golden_covers_every_id_in_the_file():
    # A golden that silently skipped IDs would pass vacuously.
    assert set(_golden()["golden"]) == {d["from"] for d in _records()}


def test_resolve_id_unchanged_from_main_except_declared():
    # Golden = main 816b9271's OWN package run on its OWN data (generated
    # from a git-archive extract, not this branch's code). Fails on any
    # answer change other than the two declared successors, and fails if a
    # declared change does not happen.
    changed = {}
    for inc_id, g in _golden()["golden"].items():
        now = gi.resolve_id(inc_id)
        if now != g["resolve_id"]:
            changed[inc_id] = (g["resolve_id"], now)
    assert changed == {k: (None, t) for k, t in DECLARED_CHANGES.items()}, changed


def test_resolve_id_group_unchanged_from_main_except_declared():
    changed = {}
    for inc_id, g in _golden()["golden"].items():
        now = sorted(gi.resolve_id_group(inc_id))
        if now != g["resolve_id_group"]:
            changed[inc_id] = now
    assert changed == {k: [t] for k, t in DECLARED_CHANGES.items()}, changed


def test_resolve_id_signature_unchanged():
    import inspect
    sig = inspect.signature(gi.resolve_id)
    assert list(sig.parameters) == ["inc_id"]
    assert sig.return_annotation in ("str | None",)


# --- 3. append-only: byte prefix + record prefix -----------------------

def test_deprecations_file_is_a_byte_extension_of_main():
    # Fails on ANY edit, reorder or removal of the 1,060 records main had,
    # including whitespace: the first 135,878 bytes must be main's bytes.
    b = DEP_PATH.read_bytes()
    assert len(b) > MAIN_PREFIX_LEN
    assert hashlib.sha256(b[:MAIN_PREFIX_LEN]).hexdigest() == MAIN_PREFIX_SHA256
    assert b[MAIN_PREFIX_LEN:MAIN_PREFIX_LEN + 2] == b",\n"


def test_appended_records_are_exactly_the_ruled_input_in_order():
    ruled = [e["record"] for e in json.loads(APPENDS_PATH.read_text(encoding="utf-8"))["entries"]]
    assert _records()[MAIN_RECORD_COUNT:MAIN_RECORD_COUNT + len(ruled)] == ruled


def test_package_copy_is_byte_identical():
    assert PKG_DEP_PATH.read_bytes() == DEP_PATH.read_bytes()


# --- 4. the file's shape and cross-record rules (validate.py) ----------

def _schema_errors(doc):
    import jsonschema
    schema = json.loads(DEP_SCHEMA_PATH.read_text(encoding="utf-8"))
    return list(jsonschema.Draft202012Validator(schema).iter_errors(doc))


def test_real_file_matches_schema():
    assert _schema_errors({"deprecations": _records()}) == []


@pytest.mark.parametrize("bad", [
    {"from": "INC-00497", "into": "INC-14789", "reason": "merged", "date": "2026-10-09",
     "valid_for_releases": ["v2.0.0"]},                       # scoped but not release-scoped
    {"from": "INC-00497", "into": "INC-14789", "reason": "release-scoped", "date": "2026-10-09"},
    {"from": "INC-00497", "into": "INC-14789", "reason": "release-scoped", "date": "2026-10-09",
     "valid_for_releases": ["2.0.0"]},                         # missing the v
    {"from": "INC-00497", "into": ["INC-14789"], "reason": "release-scoped",
     "date": "2026-10-09", "valid_for_releases": ["v2.0.0"]},  # scoped into must be one id
    {"from": "INC-00522", "into": "INC-14789", "reason": "unrecorded-drop-v2.1.0",
     "date": "2026-10-09"},
    {"from": "INC-00522", "into": None, "reason": "typo", "date": "2026-10-09"},
    {"from": "INC-00522", "into": None, "reason": "merged", "date": "2026-10-09", "extra": 1},
])
def test_schema_rejects(bad):
    assert _schema_errors({"deprecations": _records() + [bad]})


def _data():
    return json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))


def test_validate_release_scoped_rules_clean_on_real_data():
    assert v.check_release_scoped_deprecations(_data(), _records()) == []


def test_validate_fires_when_scoped_record_is_last():
    recs = _records() + [{"from": "INC-00497", "into": "INC-14789", "reason": "release-scoped",
                          "date": "2026-10-10", "valid_for_releases": ["v2.12.0"]}]
    probs = v.check_release_scoped_deprecations(_data(), recs)
    assert any("must be followed by an unscoped record" in p for p in probs), probs


def test_validate_fires_on_overlapping_releases():
    recs = copy.deepcopy(_records())
    i = next(n for n, d in enumerate(recs)
             if d["from"] == "INC-00497" and d.get("valid_for_releases") == ["v2.0.0", "v2.1.0"])
    recs.insert(i + 1, {"from": "INC-00497", "into": "INC-14907", "reason": "release-scoped",
                        "date": "2026-10-09", "valid_for_releases": ["v2.1.0"]})
    probs = v.check_release_scoped_deprecations(_data(), recs)
    assert any("both claim v2.1.0" in p for p in probs), probs


def test_validate_fires_on_dangling_scoped_target():
    recs = copy.deepcopy(_records())
    for d in recs:
        if d.get("valid_for_releases") == ["v2.6.0", "v2.7.0"]:
            d["into"] = "INC-99998"
    probs = v.check_release_scoped_deprecations(_data(), recs)
    assert any("does not resolve" in p for p in probs), probs
    assert any("does not resolve" in p for p in v.check_integrity(_data(), recs))


# --- 5. the package loader agrees with validate.py's authoritative view --

def test_loader_skip_of_scoped_records_matches_last_record_wins():
    # The loader skips scoped records; validate's _latest_by_from does not.
    # Because every scoped record is followed by an unscoped one, the two
    # views must be identical on the real data. Fails if a scoped record
    # ever becomes the last one for its `from`.
    latest = v._latest_by_from(_records())
    want = {f: r["into"] for f, r in latest.items() if r.get("into")}
    assert gi._load_deprecations() == want
