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


def test_curated_retitle_without_absorbing_gated_ids_is_not_gated(tmp_path):
    cur = [{"id": "INC-1", "title": "Curated title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    m._check_refresh_merge_authorization(
        PREV, cur, [], tmp_path / NOFILE, curation={"OECD-AIM-2026-01-01-aaaa": {"title": "Curated title"}}
    )


def test_upstream_title_edit_on_gated_row_aborts(tmp_path):
    """D67(b): same title change, but no curation override sets it: held."""
    cur = [{"id": "INC-1", "title": "Curated title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)
    assert "title edit INC-1" in str(ei.value)


def test_title_edit_on_non_oecd_aiid_row_is_not_gated(tmp_path):
    cur = [{"id": "INC-3", "title": "CVE thing, reworded", "source_ids": ["CVE-2025-0001"]}]
    m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)


def test_new_oecd_row_aborts_and_unchanged_set_does_not(tmp_path):
    """D67: a new row carrying an OECD-AIM- id absent from every published row."""
    same = [{"id": "INC-1", "title": "Old title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    m._check_refresh_merge_authorization(PREV, same, [], tmp_path / NOFILE)
    new = same + [{"id": "INC-9", "title": "Brand new", "source_ids": ["OECD-AIM-2026-09-09-zzzz"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, new, [], tmp_path / NOFILE)
    assert "add OECD/AIID source" in str(ei.value) and "INC-9" in str(ei.value) and "D67" in str(ei.value)


def test_mixed_new_row_and_absorbed_new_oecd_id_abort(tmp_path):
    mixed = [{"id": "INC-9", "title": "Mixed", "source_ids": ["AIID-5", "OECD-AIM-2026-09-09-zzzz"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, mixed, [], tmp_path / NOFILE)
    assert "new row" in str(ei.value)
    absorbed = [{"id": "INC-3", "title": "CVE thing", "source_ids": ["CVE-2025-0001", "OECD-AIM-2026-09-09-zzzz"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, absorbed, [], tmp_path / NOFILE)
    assert "absorbed into published row" in str(ei.value)


def test_approved_add_is_allowed(tmp_path):
    entries = [{"kind": "add", "source_id": "OECD-AIM-2026-09-09-zzzz"}]
    p = _approval(tmp_path, entries)
    new = [{"id": "INC-9", "title": "Brand new", "source_ids": ["OECD-AIM-2026-09-09-zzzz"]}]
    m._check_refresh_merge_authorization(PREV, new, [], p)


def test_valid_user_approval_allows_exactly_the_listed_changes(tmp_path):
    entries = [{"kind": "merge", "from": "INC-2", "into": "INC-1"}, {"kind": "retitle", "id": "INC-1"},
               {"kind": "add", "source_id": "AIID-5"}]
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


# ---- D71: AIID additions held; A1 row-keyed curation; A2 content changes; A3 baseline ----


def test_new_aiid_only_row_aborts(tmp_path):
    """D71 (supersedes the D67 scope boundary): a new AIID-only row is held too."""
    cur = [{"id": "INC-9", "title": "AIID only", "source_ids": ["AIID-1700"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)
    assert "AIID-1700" in str(ei.value) and "(new row)" in str(ei.value)


def test_new_aiid_id_absorbed_into_published_row_aborts(tmp_path):
    cur = [{"id": "INC-3", "title": "CVE thing", "source_ids": ["CVE-2025-0001", "AIID-1700"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV, cur, [], tmp_path / NOFILE)
    assert "absorbed into published row" in str(ei.value)


def test_already_published_aiid_id_is_not_an_addition(tmp_path):
    prev = PREV + [_prev("INC-5", "AIID row", ["AIID-5"])]
    cur = [{"id": "INC-5", "title": "AIID row", "source_ids": ["AIID-5"]}]
    m._check_refresh_merge_authorization(prev, cur, [], tmp_path / NOFILE)


def test_curated_title_exemption_is_keyed_to_the_row(tmp_path):
    """A1: an override keyed to an UNRELATED source id that happens to set the same
    title must not exempt this row's upstream title edit."""
    cur = [{"id": "INC-1", "title": "Curated title", "source_ids": ["OECD-AIM-2026-01-01-aaaa"]}]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(
            PREV, cur, [], tmp_path / NOFILE, curation={"CVE-2025-9999": {"title": "Curated title"}}
        )
    assert "title edit INC-1" in str(ei.value)


def _row(**kw):
    base = {"id": "INC-5", "title": "AIID row", "source_ids": ["AIID-5"], "aiid_id": 5,
            "severity": "Medium", "description": "d", "references": [], "tags": []}
    base.update(kw)
    return base


PREV_A2 = PREV + [_row(), _prev("INC-6", "CVE only", ["CVE-2025-0006"]) | {"severity": "Low"}]


@pytest.mark.parametrize("change", [
    {"aiid_id": 1574},                      # the 2026-10-03 aiid_id-gain class
    {"severity": "High"},                   # the 2026-10-03 severity-change class
    {"description": "different"},
    {"description_provenance": "original"},
    {"references": [{"url": "https://x.example/", "title": "t", "type": "report"}]},
])
def test_content_change_on_oecd_aiid_row_aborts_when_inputs_changed(tmp_path, change):
    cur = [_row(**change)]
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._check_refresh_merge_authorization(PREV_A2, cur, [], tmp_path / NOFILE, pair_inputs_changed=True)
    assert "content change INC-5 (D71)" in str(ei.value)


def test_content_change_is_not_held_when_pair_inputs_are_committed(tmp_path):
    cur = [_row(severity="High")]
    m._check_refresh_merge_authorization(PREV_A2, cur, [], tmp_path / NOFILE, pair_inputs_changed=False)


def test_content_change_on_non_oecd_aiid_row_is_not_held(tmp_path):
    cur = [{"id": "INC-6", "title": "CVE only", "source_ids": ["CVE-2025-0006"], "severity": "Critical"}]
    m._check_refresh_merge_authorization(PREV_A2, cur, [], tmp_path / NOFILE, pair_inputs_changed=True)


def test_unchanged_row_is_not_a_content_change(tmp_path):
    m._check_refresh_merge_authorization(PREV_A2, [_row()], [], tmp_path / NOFILE, pair_inputs_changed=True)


def test_approved_content_change_is_allowed(tmp_path):
    p = _approval(tmp_path, [{"kind": "content", "id": "INC-5"}])
    m._check_refresh_merge_authorization(PREV_A2, [_row(severity="High")], [], p, pair_inputs_changed=True)


# A3: the baseline is read from git HEAD and fails closed.

import subprocess


def _git(root, *args):
    return subprocess.run(
        ["git", "-c", "user.email=t@e.x", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True,
    )


def _repo(tmp_path, committed: str | None, working: str | None = None, ingest=None):
    _git(tmp_path, "init", "-q")
    (tmp_path / "data").mkdir()
    (tmp_path / "ingest").mkdir()
    (tmp_path / "README").write_text("x")
    if committed is not None:
        (tmp_path / "data" / "incidents.json").write_text(committed, encoding="utf-8")
    for name, body in (ingest or {}).items():
        (tmp_path / "ingest" / name).write_text(body, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "c")
    if working is None:
        (tmp_path / "data" / "incidents.json").unlink(missing_ok=True)
    else:
        (tmp_path / "data" / "incidents.json").write_text(working, encoding="utf-8")
    return tmp_path


GOOD = json.dumps({"incidents": [{"id": "INC-1", "title": "t", "source_ids": ["CVE-1"]}]})


def test_baseline_is_read_from_head_not_the_working_tree(tmp_path):
    r = _repo(tmp_path, GOOD, working="{ not json")
    inc, first = m._load_gate_baseline(r)
    assert first is False and inc[0]["id"] == "INC-1"


def test_baseline_survives_a_deleted_working_file(tmp_path):
    r = _repo(tmp_path, GOOD, working=None)
    assert m._load_gate_baseline(r)[0][0]["id"] == "INC-1"


def test_corrupt_committed_baseline_fails_closed(tmp_path):
    r = _repo(tmp_path, "{ not json", working=GOOD)
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(r)


def test_empty_committed_baseline_fails_closed(tmp_path):
    r = _repo(tmp_path, json.dumps({"incidents": []}))
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(r)


def test_file_deleted_in_head_but_with_history_fails_closed(tmp_path):
    r = _repo(tmp_path, GOOD, working=None)
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "delete it")
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(r)


def test_genuine_first_build_in_a_git_repo_is_allowed(tmp_path):
    r = _repo(tmp_path, None)
    assert m._load_gate_baseline(r) == ([], True)


def test_no_git_missing_baseline_fails_closed_unless_opted_in(tmp_path, monkeypatch):
    monkeypatch.delenv("MERGE_ALLOW_FIRST_BUILD", raising=False)
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(tmp_path)
    monkeypatch.setenv("MERGE_ALLOW_FIRST_BUILD", "1")
    assert m._load_gate_baseline(tmp_path) == ([], True)


def test_no_git_unparseable_baseline_fails_closed(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "incidents.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(tmp_path)


def test_first_build_skips_the_checks(tmp_path):
    new = [{"id": "INC-9", "title": "x", "source_ids": ["OECD-AIM-2026-09-09-zzzz"]}]
    m._check_refresh_merge_authorization([], new, [], tmp_path / NOFILE, first_build=True)
    with pytest.raises(m.RefreshMergeApprovalError):
        m._check_refresh_merge_authorization([], new, [], tmp_path / NOFILE, first_build=False)


def test_pair_inputs_changed_detects_each_input(tmp_path):
    files = {n: "[]" for n in m._PAIR_INPUT_FILES}
    r = _repo(tmp_path, GOOD, ingest=files)
    assert m._pair_inputs_changed(r) is False
    for n in m._PAIR_INPUT_FILES:
        (r / "ingest" / n).write_text("[1]", encoding="utf-8")
        assert m._pair_inputs_changed(r) is True, n
        (r / "ingest" / n).write_text("[]", encoding="utf-8")
    assert m._pair_inputs_changed(r) is False
    (r / "ingest" / m._PAIR_INPUT_FILES[0]).unlink()
    assert m._pair_inputs_changed(r) is True


def test_pair_inputs_changed_is_conservative_without_git(tmp_path):
    assert m._pair_inputs_changed(tmp_path) is True


@pytest.mark.real_gate
def test_run_refresh_gate_wires_baseline_pair_signal_and_curation(monkeypatch):
    """main() calls _run_refresh_gate; it must feed the HEAD baseline, the pair-input
    signal and the curation map into the checker (the autouse stub is off here)."""
    row = {"id": "INC-5", "title": "AIID row", "source_ids": ["AIID-5"], "severity": "Medium"}
    monkeypatch.setattr(m, "_load_gate_baseline", lambda *a, **k: ([row], False))
    monkeypatch.setattr(m, "_pair_inputs_changed", lambda *a, **k: True)
    with pytest.raises(m.RefreshMergeApprovalError) as ei:
        m._run_refresh_gate([{**row, "severity": "High"}], [], {})
    assert "content change INC-5 (D71)" in str(ei.value)
    monkeypatch.setattr(m, "_pair_inputs_changed", lambda *a, **k: False)
    m._run_refresh_gate([{**row, "severity": "High"}], [], {})  # inputs committed: not held
    monkeypatch.setattr(m, "_load_gate_baseline", lambda *a, **k: ([], True))
    m._run_refresh_gate([{**row, "id": "INC-9"}], [], {})  # first build: skipped


def test_pair_inputs_include_airi_navigator():
    """AIRI rows are keyed by AIID-<n> ids; under D71 they count as the pair."""
    assert "airi_navigator_incidents.json" in m._PAIR_INPUT_FILES


def test_shallow_clone_with_file_deleted_at_head_fails_closed(tmp_path):
    """A2: git log --all is empty in a depth-1 clone, which must not read as a first build."""
    src = _repo(tmp_path / "src", GOOD, working=GOOD) if (tmp_path / "src").mkdir() is None else None
    _git(src, "add", "-A")
    _git(src, "commit", "-q", "--allow-empty", "-m", "keep")
    (src / "data" / "incidents.json").unlink()
    _git(src, "add", "-A")
    _git(src, "commit", "-q", "-m", "delete it")
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", src.as_uri(), str(shallow)], check=True, capture_output=True)
    assert subprocess.run(["git", "log", "--oneline", "-1", "--all", "--", "data/incidents.json"], cwd=shallow,
                          capture_output=True, text=True).stdout.strip() == ""  # the trap: looks like no history
    with pytest.raises(m.RefreshBaselineError):
        m._load_gate_baseline(shallow)


def test_shallow_clone_with_the_file_present_still_builds(tmp_path):
    (tmp_path / "src").mkdir()
    src = _repo(tmp_path / "src", GOOD, working=GOOD)
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", src.as_uri(), str(shallow)], check=True, capture_output=True)
    assert m._load_gate_baseline(shallow)[1] is False
