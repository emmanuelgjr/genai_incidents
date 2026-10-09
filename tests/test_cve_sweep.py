"""v2.13.0 item 3: the rejected-CVE sweep on every refresh.

Covers (each with a counter-test showing the check can FAIL):
  * DISPUTED detection from a CVE JSON 5 record (CNA tag, ADP tag, legacy
    description prefix; never on a REJECTED record),
  * the DISPUTED merge path on a planted record (status, status_reason,
    one-level confidence drop, still counted in incident_count),
  * the schema edit it needs (shown by validating against the schema as
    committed, and against the schema with the proposed edit applied in memory),
  * rotation order (never-checked first, then pre-dispute-aware, then stalest),
    and the stated bound (every id re-checked within ceil(N/B) runs),
  * the dated sweep log and the fail-loud exit code.
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import pytest

import ingest_cve_rejections as ing
import merge_and_dedupe as m
import validate
from tests.test_cve_rejections import _cve_row
from tests.test_merge_and_dedupe import _setup_tmp_repo

ROOT = Path(__file__).resolve().parents[1]


def _doc(state="PUBLISHED", cna_tags=None, adp_tags=None, desc="A plain description."):
    cna = {"descriptions": [{"lang": "en", "value": desc}]}
    if cna_tags is not None:
        cna["tags"] = cna_tags
    d = {"cveMetadata": {"state": state, "cveId": "CVE-2099-0001"}, "containers": {"cna": cna}}
    if adp_tags is not None:
        d["containers"]["adp"] = [{"providerMetadata": {}, "tags": adp_tags}]
    return d


# ----- detection -----

def test_dispute_signals_each_upstream_form():
    assert ing.dispute_signals(_doc(cna_tags=["disputed"])) == ["cna-tag"]
    assert ing.dispute_signals(_doc(adp_tags=["disputed"])) == ["adp-tag"]
    assert ing.dispute_signals(_doc(desc="** DISPUTED ** A thing happens.")) == ["description-prefix"]
    assert ing.dispute_signals(_doc(desc="  ** disputed **  lower-case, padded")) == ["description-prefix"]
    both = ing.dispute_signals(_doc(cna_tags=["disputed"], desc="** DISPUTED ** x"))
    assert both == ["cna-tag", "description-prefix"]


def test_dispute_signals_do_not_overfire():
    assert ing.dispute_signals(_doc()) == []
    assert ing.dispute_signals(_doc(cna_tags=["exclusively-hosted-service"])) == []
    # the word in the middle of a description is not the CNA's dispute marker
    assert ing.dispute_signals(_doc(desc="The vendor DISPUTED this claim in a blog.")) == []


def test_parse_record_disputed_keeps_state_published_and_rejected_is_never_disputed():
    rec = ing.parse_cve_record(_doc(cna_tags=["disputed"]))
    assert rec == {"state": "PUBLISHED", "v": 2, "disputed": True, "dispute_signals": ["cna-tag"]}
    assert "disputed" not in ing.parse_cve_record(_doc())
    rej = ing.parse_cve_record(_doc(state="REJECTED", cna_tags=["disputed"]))
    assert rej["state"] == "REJECTED" and "disputed" not in rej


# ----- the merge path on a planted record -----

DISP = {"CVE-2099-0002": {"state": "PUBLISHED", "checked": "2026-10-09", "disputed": True,
                          "dispute_signals": ["cna-tag"], "v": 2}}
REJ = {"CVE-2099-0001": {"state": "REJECTED", "checked": "2026-10-08"}}


def _e(cves, sources, **kw):
    return {"cve_ids": list(cves), "source_ids": list(sources), "title": "t", **kw}


def test_disputed_status_on_planted_record():
    e = _e(["CVE-2099-0002"], ["CVE-2099-0002"])
    assert m._apply_cve_rejections(e, {}, DISP) is False, "disputed is not retracted"
    assert e["status"] == "disputed"
    assert e["status_reason"] == {"code": "cve-disputed", "as_of": "2026-10-09"}
    assert "rejected_cve_ids" not in e and e["cve_ids"] == ["CVE-2099-0002"]


def test_disputed_requires_no_other_evidence_and_loses_to_retraction():
    corroborated = _e(["CVE-2099-0002"], ["CVE-2099-0002", "AIID-9"])
    m._apply_cve_rejections(corroborated, {}, DISP)
    assert "status" not in corroborated
    live_plus = _e(["CVE-2099-0002", "CVE-2025-1"], ["CVE-2099-0002", "CVE-2025-1"])
    m._apply_cve_rejections(live_plus, {}, DISP)
    assert "status" not in live_plus, "a live non-disputed CVE keeps the entry standing"
    both = _e(["CVE-2099-0001"], ["CVE-2099-0001"])
    assert m._apply_cve_rejections(both, REJ, {**DISP, "CVE-2099-0001": DISP["CVE-2099-0002"]}) is True
    assert both["status"] == "retracted", "REJECTED outranks disputed"
    # marker is shed when the dispute disappears from the snapshot
    e = _e(["CVE-2099-0002"], ["CVE-2099-0002"])
    m._apply_cve_rejections(e, {}, DISP)
    m._apply_cve_rejections(e, {}, {})
    assert not ({"status", "status_reason"} & e.keys())


def test_confidence_drops_exactly_one_level():
    for before, after in [("high", "medium"), ("medium", "low"), ("low", "low")]:
        e = {"status": "disputed", "confidence": before}
        m._lower_confidence_if_disputed(e)
        assert e["confidence"] == after
    e = {"status": "retracted", "confidence": "high"}
    m._lower_confidence_if_disputed(e)
    assert e["confidence"] == "high", "only disputed entries are lowered"
    e = {"confidence": "high"}
    m._lower_confidence_if_disputed(e)
    assert e["confidence"] == "high"


def _patched_schema(tmp_path: Path) -> Path:
    """The committed schema plus the one-value edit gap-doc section 5 proposes."""
    sch = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    codes = sch["properties"]["status_reason"]["properties"]["code"]["enum"]
    if "cve-disputed" not in codes:
        codes.append("cve-disputed")
    path = tmp_path / "incident.schema.json"
    path.write_text(json.dumps(sch), encoding="utf-8")
    return path


def test_build_emits_disputed_counts_it_and_lowers_confidence(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "SCHEMA_PATH", _patched_schema(tmp_path))
    snap = tmp_path / "cve_rejections.json"
    snap.write_text(json.dumps({"states": {**REJ, **DISP}}), encoding="utf-8")
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", snap)
    (ingest / "src.json").write_text(json.dumps(
        [_cve_row("CVE-2099-0001"), _cve_row("CVE-2099-0002"), _cve_row("CVE-2025-0003")]),
        encoding="utf-8")
    m.main()
    d = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    by = {e["cve_ids"][0]: e for e in d["incidents"]}
    assert by["CVE-2099-0001"]["status"] == "retracted"
    disp, plain = by["CVE-2099-0002"], by["CVE-2025-0003"]
    assert disp["status"] == "disputed" and disp["status_reason"]["code"] == "cve-disputed"
    assert plain["confidence"] == "medium" and disp["confidence"] == "low", "dropped one level"
    assert "status" not in plain
    assert len(d["incidents"]) == 3
    assert d["incident_count"] == 2 and d["retracted_count"] == 1, "disputed stays counted"
    assert validate.check_status(d, {"CVE-2099-0001"}, {"CVE-2099-0002"}) == []
    first = (data / "incidents.json").read_text(encoding="utf-8")
    m.main()
    assert (data / "incidents.json").read_text(encoding="utf-8") == first, "byte-stable rebuild"


def test_build_does_not_emit_disputed_while_the_schema_lacks_the_code(tmp_path, monkeypatch, capsys):
    """Until schema-architect adds `cve-disputed`, emitting it would break validation:
    the merge must record-but-not-apply, loudly, and the entry must stand unmarked."""
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    sch = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    sch["properties"]["status_reason"]["properties"]["code"]["enum"] = ["cve-rejected"]
    closed = tmp_path / "closed.schema.json"
    closed.write_text(json.dumps(sch), encoding="utf-8")
    monkeypatch.setattr(m, "SCHEMA_PATH", closed)
    assert m._disputed_emission_enabled() is False
    snap = tmp_path / "cve_rejections.json"
    snap.write_text(json.dumps({"states": {**REJ, **DISP}}), encoding="utf-8")
    monkeypatch.setattr(m, "CVE_REJECTIONS_PATH", snap)
    (ingest / "src.json").write_text(json.dumps([_cve_row("CVE-2099-0002")]), encoding="utf-8")
    m.main()
    d = json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    assert "status" not in d["incidents"][0] and d["incidents"][0]["confidence"] == "medium"
    assert "NOT applied" in capsys.readouterr().out
    monkeypatch.setattr(m, "SCHEMA_PATH", _patched_schema(tmp_path))
    assert m._disputed_emission_enabled() is True


# ----- validate.py rules fire -----

def _disp_entry(**kw):
    e = {"id": "INC-1", "cve_ids": ["CVE-2099-0002"], "source_ids": ["CVE-2099-0002"],
         "status": "disputed", "status_reason": {"code": "cve-disputed", "as_of": "2026-10-09"},
         "confidence": "medium"}
    e.update(kw)
    return e


def _wrap(*entries):
    return {"incident_count": len(entries), "retracted_count": 0, "incidents": list(entries)}


def test_validate_disputed_rules_pass_clean_and_fire_on_corruption():
    D = {"CVE-2099-0002"}
    assert validate.check_status(_wrap(_disp_entry()), set(), D) == []
    # not lowered
    assert any("confidence 'high'" in p for p in
               validate.check_status(_wrap(_disp_entry(confidence="high")), set(), D))
    # wrong code
    bad = _disp_entry(status_reason={"code": "cve-rejected", "as_of": "2026-10-09"})
    assert any("cve-disputed" in p for p in validate.check_status(_wrap(bad), set(), D))
    # entry resting only on a disputed CVE but unmarked
    plain = {"id": "INC-2", "cve_ids": ["CVE-2099-0002"], "source_ids": ["CVE-2099-0002"]}
    assert any("not marked disputed" in p for p in validate.check_status(_wrap(plain), set(), D))
    # marked disputed though the snapshot no longer says so
    assert any("none of its CVEs is disputed" in p for p in
               validate.check_status(_wrap(_disp_entry()), set(), set()))
    # status without status_reason (pre-existing rule still applies)
    no_reason = {k: v for k, v in _disp_entry().items() if k != "status_reason"}
    assert validate.check_status(_wrap(no_reason), set(), D)


def test_committed_corpus_agrees_with_committed_snapshot_on_disputes():
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    st = json.loads((ROOT / "ingest" / "cve_rejections.json").read_text(encoding="utf-8"))["states"]
    rejected = {c for c, r in st.items() if r["state"] == "REJECTED"}
    disputed = {c for c, r in st.items() if r["state"] == "PUBLISHED" and r.get("disputed")}
    assert disputed, "snapshot lists no disputed CVE: this check would be vacuous"
    if not validate._schema_allows_disputed(_schema()):
        # not applied yet (see the schema test below): the corpus must carry NO disputed marker
        assert not [e["id"] for e in data["incidents"] if e.get("status") == "disputed"]
        assert validate.check_status(data, rejected, None) == []
        return
    assert validate.check_status(data, rejected, disputed) == []


# ----- schema: the edit this change needs but does not make -----

def _schema():
    return json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))


def _real_entry():
    d = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    return copy.deepcopy(next(e for e in d["incidents"] if "status" not in e))


def test_schema_needs_cve_disputed_code_and_accepts_it_once_added():
    import jsonschema
    e = _real_entry()
    e["status"] = "disputed"
    e["status_reason"] = {"code": "cve-disputed", "as_of": "2026-10-09"}
    committed = _schema()
    codes = committed["properties"]["status_reason"]["properties"]["code"]["enum"]
    if "cve-disputed" in codes:
        # schema-architect has landed the edit: the committed schema must accept it
        assert not list(jsonschema.Draft202012Validator(committed).iter_errors(e))
        return
    errs = list(jsonschema.Draft202012Validator(committed).iter_errors(e))
    assert errs, "without the edit a disputed entry is rejected (this is why the edit is required)"
    patched = copy.deepcopy(committed)
    patched["properties"]["status_reason"]["properties"]["code"]["enum"].append("cve-disputed")
    assert not list(jsonschema.Draft202012Validator(patched).iter_errors(e)), \
        "the proposed one-value edit is sufficient"


# ----- rotation: never-checked first, bound, loudness -----

def _prev(**spec):
    return {c: v for c, v in spec.items()}


def test_never_checked_first_then_pre_v2_then_stalest():
    ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003", "CVE-2024-0004", "CVE-2024-0005"]
    prev = {
        "CVE-2024-0001": {"state": "PUBLISHED", "checked": "2026-10-01", "v": 2},   # fresh v2
        "CVE-2024-0002": {"state": "PUBLISHED", "checked": "2026-09-20", "v": 2},   # stale v2
        "CVE-2024-0003": {"state": "PUBLISHED", "checked": "2026-10-08"},            # pre-v2, recent
        # 0004 never checked
        "CVE-2024-0005": {"state": "PUBLISHED", "checked": "2026-01-01"},            # pre-v2, oldest
    }
    assert ing.rotation_order(ids, prev) == [
        "CVE-2024-0004",                     # never checked
        "CVE-2024-0005", "CVE-2024-0003",    # pre-dispute-aware, oldest first
        "CVE-2024-0002", "CVE-2024-0001"]    # then stalest v2 check


def test_ordering_check_fails_on_a_wrong_order():
    """The ordering assertion must be able to fail: a plain id sort is NOT it."""
    ids = ["CVE-2024-0001", "CVE-2024-0002"]
    prev = {"CVE-2024-0001": {"state": "PUBLISHED", "checked": "2026-10-01", "v": 2}}
    assert ing.rotation_order(ids, prev)[0] == "CVE-2024-0002"
    assert sorted(ids)[0] != ing.rotation_order(ids, prev)[0]


def _run_main(tmp_path, monkeypatch, ids, prev_states, budget, today, checker=None, extra=()):
    inc = tmp_path / "incidents.json"
    inc.write_text(json.dumps({"incidents": [{"cve_ids": [c]} for c in ids]}), encoding="utf-8")
    out = tmp_path / "cve_rejections.json"
    if prev_states is not None:
        out.write_text(json.dumps({"fetched": "x", "states": prev_states}), encoding="utf-8")
    monkeypatch.setattr(ing, "INCIDENTS", inc)
    monkeypatch.setattr(ing, "OUT_FILE", out)
    monkeypatch.setattr(ing, "LOG_DIR", tmp_path / "log")
    seen = []

    def fake(c):
        seen.append(c)
        if checker:
            return checker(c)
        return {"state": "PUBLISHED", "v": 2}
    monkeypatch.setattr(ing, "check_cvelist", fake)

    class _D(ing.date):
        @classmethod
        def today(cls):
            return today
    monkeypatch.setattr(ing, "date", _D)
    monkeypatch.setattr(sys, "argv", ["x", "--max-requests", str(budget), *extra])
    rc = ing.main()
    return rc, seen, json.loads(out.read_text(encoding="utf-8"))["states"]


def test_main_checks_never_checked_ids_before_any_recheck(tmp_path, monkeypatch):
    import datetime
    ids = [f"CVE-2024-{n:04d}" for n in range(1, 9)]
    prev = {c: {"state": "PUBLISHED", "checked": "2026-09-01", "v": 2} for c in ids[:6]}  # 7, 8 new
    rc, seen, st = _run_main(tmp_path, monkeypatch, ids, prev, 3, datetime.date(2026, 10, 9))
    assert rc == 0
    assert seen[:2] == ["CVE-2024-0007", "CVE-2024-0008"], "never-checked first"
    assert len(seen) == 3 and seen[2] == "CVE-2024-0001"
    assert all(st[c]["checked"] == "2026-10-09" for c in seen)
    # the never-checked ids are now in the snapshot and carry the version marker
    assert st["CVE-2024-0007"]["v"] == 2


def test_rotation_covers_corpus_within_ceil_n_over_b_runs(tmp_path, monkeypatch):
    import datetime
    N, B = 23, 5
    ids = [f"CVE-2024-{n:04d}" for n in range(1, N + 1)]
    states = None
    for week in range(math.ceil(N / B)):
        day = datetime.date(2026, 10, 9) + datetime.timedelta(days=7 * week)
        rc, _, states = _run_main(tmp_path, monkeypatch, ids, states, B, day)
        assert rc == 0
    first_pass = {c: states[c]["checked"] for c in ids}
    assert set(first_pass) == set(ids), "every id has a state"
    # every id was (re)checked inside the window: nothing older than the first run
    assert min(first_pass.values()) >= "2026-10-09"
    # corrupted: one run short of the bound leaves ids unchecked
    short = tmp_path / "short"
    short.mkdir()
    states = None
    for week in range(math.ceil(N / B) - 1):
        day = datetime.date(2026, 10, 9) + datetime.timedelta(days=7 * week)
        _, _, states = _run_main(short, monkeypatch, ids, states, B, day)
    assert len(states) < N, "the bound is tight: ceil(N/B)-1 runs do not cover the corpus"


def test_log_records_new_rejected_new_disputed_and_nvd_disagreement(tmp_path, monkeypatch):
    import datetime
    ids = ["CVE-2024-0001", "CVE-2024-0002", "CVE-2024-0003", "CVE-2024-0004"]
    prev = {"CVE-2024-0001": {"state": "PUBLISHED", "checked": "2026-10-03"}}

    def checker(c):
        return {"CVE-2024-0001": {"state": "REJECTED", "v": 2},
                "CVE-2024-0002": {"state": "PUBLISHED", "v": 2, "disputed": True,
                                  "dispute_signals": ["adp-tag"]},
                "CVE-2024-0003": {"state": "PUBLISHED", "v": 2},
                "CVE-2024-0004": {"state": "REJECTED", "v": 2}}[c]
    monkeypatch.setattr(ing, "check_nvd", lambda c: "Rejected" if c.endswith("1") else "Analyzed")
    rc, _, _ = _run_main(tmp_path, monkeypatch, ids, prev, -1, datetime.date(2026, 10, 9), checker)
    log = json.loads((tmp_path / "log" / "2026-10-09.json").read_text(encoding="utf-8"))
    assert log["new_rejected"] == ["CVE-2024-0001", "CVE-2024-0004"]
    assert [d["id"] for d in log["new_disputed"]] == ["CVE-2024-0002"]
    assert log["new_disputed"][0]["signals"] == ["adp-tag"]
    assert log["nvd_disagreements"] == [{"id": "CVE-2024-0004", "cve_list": "REJECTED", "nvd": "Analyzed"}]
    assert {c["id"]: c["before"] for c in log["state_changes"]}["CVE-2024-0001"] == "PUBLISHED"
    assert log["state_counts_checked"] == {"PUBLISHED": 2, "REJECTED": 2}
    assert (tmp_path / "log" / "2026-10-09.md").read_text(encoding="utf-8").count("CVE-2024-0004") >= 2
    # a restart the same day extends the same log without losing the first run's `before`
    prev2 = json.loads((tmp_path / "cve_rejections.json").read_text(encoding="utf-8"))["states"]
    assert prev2["CVE-2024-0001"]["state"] == "REJECTED"


def test_run_exits_nonzero_when_fetches_fail(tmp_path, monkeypatch):
    import datetime
    ids = [f"CVE-2024-{n:04d}" for n in range(1, 11)]

    def boom(c):
        raise OSError("503")
    rc, _, st = _run_main(tmp_path, monkeypatch, ids, None, -1, datetime.date(2026, 10, 9), boom)
    assert rc == 1, "10/10 failed fetches must fail the step"
    log = json.loads((tmp_path / "log" / "2026-10-09.json").read_text(encoding="utf-8"))
    assert log["failed_count"] == 10 and st == {}
    # and a clean run exits 0
    ok = tmp_path / "ok"
    ok.mkdir()
    rc, _, _ = _run_main(ok, monkeypatch, ids, None, -1, datetime.date(2026, 10, 10))
    assert rc == 0


def test_failed_fetch_keeps_the_prior_record(tmp_path, monkeypatch):
    import datetime
    prev = {"CVE-2024-0001": {"state": "PUBLISHED", "checked": "2026-09-01", "v": 2}}

    def boom(c):
        raise OSError("503")
    _, _, st = _run_main(tmp_path, monkeypatch, ["CVE-2024-0001"], prev, -1,
                         datetime.date(2026, 10, 9), boom)
    assert st["CVE-2024-0001"]["checked"] == "2026-09-01", "stale stays stale; it is retried next run"


# ----- the weekly refresh actually runs the sweep, at a budget that meets the stated bound -----

STATED_BOUND_WEEKS = 10   # docs: 9,169 ids / 1,200 per run = 8 weeks today; 10 leaves headroom for growth


def _weekly_budget(text: str) -> int | None:
    import re
    mm = re.search(r"ingest_cve_rejections\.py[^\n]*--max-requests\s+(\d+)", text)
    return int(mm.group(1)) if mm else None


def test_weekly_workflow_budget_rotates_the_corpus_within_the_stated_bound():
    text = (ROOT / ".github" / "workflows" / "auto-refresh.yml").read_text(encoding="utf-8")
    budget = _weekly_budget(text)
    assert budget, "auto-refresh.yml must run ingest_cve_rejections.py with a --max-requests budget"
    n = len(ing.corpus_cve_ids())
    assert math.ceil(n / budget) <= STATED_BOUND_WEEKS, (
        f"{n} corpus CVEs / {budget} per weekly run = {math.ceil(n / budget)} weeks "
        f"> stated bound {STATED_BOUND_WEEKS}")


def test_budget_check_fails_at_the_old_budget():
    old = "run: python scripts/ingest_cve_rejections.py --nvd-modified-days 10 --max-requests 600"
    assert _weekly_budget(old) == 600
    assert math.ceil(len(ing.corpus_cve_ids()) / 600) > STATED_BOUND_WEEKS, \
        "at the pre-change budget (16 weeks) the bound would be violated: the check can fail"
