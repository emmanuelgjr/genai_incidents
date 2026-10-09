"""D42 / D25(a): the build-time gate on OECD/AIID-driven merges and retitles of
previously-published IDs (merge_and_dedupe._check_refresh_merge_authorization),
and the WS4-T12 provenance stamp.

Each test names the input that makes the gate fail, so the gate has been seen
to fire (agreement 6). The real-data firing (7 merges + 4 retitles, nothing
written) is recorded in docs/audits/refresh-tripwire-2026-10-03.md's addendum.
"""

from __future__ import annotations

import json

import pytest

import ingest_oecd_aim as oecd
import merge_and_dedupe as m


def _prev(iid, title, sids):
    return {"id": iid, "title": title, "source_ids": list(sids)}


def _dep(frm, into, retired, reason="merged"):
    return {"from": frm, "into": into, "reason": reason, "retired_source_ids": retired}


def _approval(tmp_path, entries, **auth):
    doc = {"entries": entries}
    if auth is not None:
        a = {"decision": "DX", "ruled_by": "user", "entries_sha256": m._refresh_merge_entries_sha256(entries)}
        a.update(auth)
        doc["authorization"] = a
    p = tmp_path / "approved.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


NOFILE = "does-not-exist.json"

PREV = [
    _prev("INC-1", "Old title", ["OECD-AIM-2026-01-01-aaaa"]),
    _prev("INC-2", "Other", ["OECD-AIM-2026-02-02-bbbb"]),
    _prev("INC-3", "CVE thing", ["CVE-2025-0001"]),
    _prev("INC-4", "CVE other", ["CVE-2025-0002"]),
]


def test_merge_of_published_oecd_row_without_approval_aborts(tmp_path):
    cur = [{"id": "INC-1", "title": "Old title", "source_ids": ["AIID-5", "OECD-AIM-2026-01-01-aaaa", "OECD-AIM-2026-02-02-bbbb"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(
            PREV, cur, [_dep("INC-2", "INC-1", ["OECD-AIM-2026-02-02-bbbb"])], tmp_path / NOFILE
        )
    assert "INC-2 -> INC-1" in str(ei.value) and "Nothing was written" in str(ei.value)


def test_transitive_merge_reason_is_gated_too(tmp_path):
    cur = [{"id": "INC-1", "title": "Old title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    with pytest.raises(m.RefreshMergeApprovalError):
        m._check_refresh_merge_authorization(
            PREV, cur, [_dep("INC-2", "INC-1", ["OECD-AIM-2026-02-02-bbbb"], "transitive-merge")], tmp_path / NOFILE
        )


def test_non_oecd_aiid_merge_is_not_gated(tmp_path):
    cur = [{"id": "INC-3", "title": "CVE thing", "source_ids": ["CVE-2025-0001", "CVE-2025-0002"]}]
    m._check_refresh_merge_authorization(
        PREV, cur, [_dep("INC-4", "INC-3", ["CVE-2025-0002"])], tmp_path / NOFILE
    )


def test_merge_of_never_published_id_is_not_gated(tmp_path):
    cur = [{"id": "INC-1", "title": "Old title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    m._check_refresh_merge_authorization(
        PREV, cur, [_dep("INC-999", "INC-1", ["OECD-AIM-2099-01-01-zzzz"])], tmp_path / NOFILE
    )


def test_other_deprecation_reasons_are_not_gated(tmp_path):
    cur = [{"id": "INC-1", "title": "Old title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    m._check_refresh_merge_authorization(
        PREV, cur, [_dep("INC-2", "INC-1", ["OECD-AIM-2026-02-02-bbbb"], "split")], tmp_path / NOFILE
    )


def test_retitle_after_absorbing_oecd_aiid_ids_aborts(tmp_path):
    cur = [{"id": "INC-1", "title": "New title", "source_ids": ["AIID-77", "OECD-AIM-2026-01-01-aaaa"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)
    assert "retitle INC-1" in str(ei.value)


def test_retitle_without_absorbing_gated_ids_is_not_gated(tmp_path):
    cur = [{"id": "INC-1", "title": "Curated title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)


def test_valid_user_approval_allows_exactly_the_listed_changes(tmp_path):
    entries = [{"kind": "merge", "from": "INC-2", "into": "INC-1"}, {"kind": "retitle", "id": "INC-1"}]
    path = _approval(tmp_path, entries)
    cur = [{"id": "INC-1", "title": "New title", "source_ids": ["AIID-5", "OECD-AIM-2026-01-01-aaaa", "OECD-AIM-2026-02-02-bbbb"]}]
    m._check_refresh_merge_authorization(
        PREV, cur, [_dep("INC-2", "INC-1", ["OECD-AIM-2026-02-02-bbbb"])], path
    )
    # a different merge is still refused
    with pytest.raises(m.RefreshMergeApprovalError):
        m._check_refresh_merge_authorization(
            PREV, cur, [_dep("INC-3", "INC-1", ["AIID-9"])], path
        )


def test_list_without_user_marker_authorizes_nothing(tmp_path):
    entries = [{"kind": "merge", "from": "INC-2", "into": "INC-1"}]
    p = tmp_path / "approved.json"
    p.write_text(json.dumps({"entries": entries}), encoding="utf-8")
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._load_refresh_merge_approvals(p)
    assert "File presence authorizes nothing" in str(ei.value)


def test_list_edited_after_ruling_is_refused(tmp_path):
    entries = [{"kind": "merge", "from": "INC-2", "into": "INC-1"}]
    path = _approval(tmp_path, entries)
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["entries"].append({"kind": "merge", "from": "INC-3", "into": "INC-1"})
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._load_refresh_merge_approvals(path)
    assert "edited after it was ruled on" in str(ei.value)


def test_committed_approval_list_is_empty_until_the_user_rules():
    """D42(3): no merge is approved until the user rules on the evidence
    list. If this fails, someone committed an approval: check the board for
    the ruling it cites."""
    approved = m._load_refresh_merge_approvals(m.REFRESH_MERGE_APPROVAL_PATH)
    assert approved == set()


# ---- WS4-T12: provenance stamp --------------------------------------------


def test_oecd_ingest_stamps_provenance_on_every_row():
    body = {
        "id": "2026-01-01-dead", "title": "Deepfake voice clone scam targets bank customers",
        "date": "2026-01-01", "summary": "voice clone fraud deepfake", "evidences": [],
        "company": ["Example Bank"], "articles": [], "aiid_ids": [1700],
    }
    row = oecd.normalize_body(body, "https://oecd.ai/en/incidents/2026-01-01-dead")
    assert row["description_provenance"] == "original"
    assert row["description_source"] == "oecd-aim"


def _raw(**kw):
    base = {"source_id": "OECD-AIM-2026-01-01-dead", "title": "A long enough title", "year": 2026,
            "description": "Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as X.",
            "references": [{"title": "t", "url": "https://oecd.ai/en/incidents/2026-01-01-dead", "type": "report"}]}
    base.update(kw)
    return base


def test_merge_backfills_label_for_union_retained_oecd_rows():
    e = m.normalize_entry(_raw())
    assert (e["description_provenance"], e["description_source"]) == ("original", "oecd-aim")


def test_merge_does_not_label_non_oecd_rows():
    e = m.normalize_entry(_raw(source_id="AIID-5", description="AI Incident Database (AIID) entry #5: x."))
    assert not e.get("description_provenance") and not e.get("description_source")


def test_merge_does_not_overwrite_an_explicit_label():
    e = m.normalize_entry(_raw(description_provenance="curated", description_source="manual"))
    assert (e["description_provenance"], e["description_source"]) == ("curated", "manual")


def test_label_survives_dedupe_when_oecd_row_is_the_anchor():
    a = m.normalize_entry(_raw())
    b = m.normalize_entry(_raw(source_id="AIID-1700", description="AI Incident Database (AIID) entry #1700: x.",
                               references=[{"title": "t", "url": "https://incidentdatabase.ai/cite/1700", "type": "report"}],
                               extra_source_ids=[]))
    a["source_ids"] = ["OECD-AIM-2026-01-01-dead", "AIID-1700"]
    surviving, _ = m.dedupe_entries([a, b])
    assert len(surviving) == 1
    assert surviving[0]["description_source"] == "oecd-aim"
    assert surviving[0]["description"].startswith("Tracked by the OECD")


# ---- step 4d: provenance overrides must follow the TEXT, not any member ----

_OV = {"OECD-AIM-2026-04-03-c16a": {"description_provenance": "original", "description_source": "oecd-aim", "_note": "x"}}


def test_override_label_applies_while_description_is_the_oecd_template():
    e = {"source_ids": ["AIID-1574", "OECD-AIM-2026-04-03-c16a"],
         "description": "Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as OECD-AIM-2026-04-03-c16a, dated 2026-04-03."}
    assert m.apply_curation_overrides([e], _OV) == 1
    assert e["description_source"] == "oecd-aim"


def test_override_label_is_skipped_when_anchor_moved_to_aiid_text():
    """The hazard: AIID's snapshot gains aiid_id 1574 and its text wins."""
    e = {"source_ids": ["AIID-1574", "OECD-AIM-2026-04-03-c16a"],
         "description": "AI Incident Database (AIID) entry #1574: Some title. Alleged deployer/developer: X."}
    m.apply_curation_overrides([e], _OV)
    assert "description_source" not in e and "description_provenance" not in e
