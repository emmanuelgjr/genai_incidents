"""Standing test (user ruling D136(b)): ``status: unverified`` on REAL rows of
every class, through the real build chain, against the real-corpus checks.

``unverified_count`` is 0 in the committed corpus, so every real-corpus test
that derives "standing" rows passes whether or not it excludes unverified.
That is how D130-1 shipped two such tests unfixed (bounce #1, bounce #2).
This test closes that gap. In a scratch copy of the committed tree (never
the real data/), it marks one real row of each class unverified through
data/curation_overrides.json, the only mechanism, and rebuilds. It then
re-runs the existing real-corpus tests against the scratch root, by pointing
their module ``ROOT``/``STATS`` at it rather than copying their logic.

Rows are chosen by a deterministic query over the scratch build, never by
hardcoded ID (except the legacy seed, which prefers INC-045 when present).
A class with no candidate fails loudly.

Marked ``slow`` (one full merge, about two minutes). Like the other slow
scratch-repo tests, it runs by default, including in CI (validate.yml runs
``pytest tests -q``).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

import tests.test_export_integrity as tei
import tests.test_export_modified as tem
import tests.test_landmark_distribution as tld
from tests.test_oecd_stage1_freeze import _extract_head, _published_aiid_only

pytestmark = pytest.mark.slow

AS_OF = "2026-10-15"
_LEGACY = re.compile(r"^INC-\d+$")


def _run(root: Path, script: str) -> None:
    r = subprocess.run([sys.executable, str(root / "scripts" / script)], cwd=root,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"{script} failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"


def _rows(root: Path) -> list[dict]:
    return json.loads((root / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]


# class -> predicate over a row of the control build. Order matters only for
# tie-breaking: a row already picked for an earlier class is not reused.
CLASSES = {
    "landmark": lambda e: e.get("tier") == "landmark",
    "oecd": lambda e: any(s.startswith("OECD-AIM-") for s in e.get("source_ids") or []),
    # AIID-only and single-source, so the row is one _published_aiid_only()
    # would return if it did not exclude unverified rows.
    "aiid": lambda e: bool(e.get("aiid_id")) and len(e.get("source_ids") or []) == 1
    and e["source_ids"][0].startswith("AIID-"),
    "retained": lambda e: e.get("source_status") == "retained",
    "disputed": lambda e: e.get("status") == "disputed",
    "cve": lambda e: bool(e.get("source_ids")) and all(s.startswith("CVE-") for s in e["source_ids"]),
    "legacy_seed": lambda e: any(_LEGACY.match(s) for s in e.get("source_ids") or []),
}


def pick_rows(rows: list[dict]) -> dict[str, tuple[str, str]]:
    """``{class: (row id, override key)}``. Deterministic: lowest ID first.
    The key must be a source_id carried by exactly one row, so the override
    marks that row and nothing else. Retracted rows are never picked (retracted
    wins over unverified, so marking one would prove nothing)."""
    owners = Counter(s for e in rows for s in e.get("source_ids") or [])
    picked: dict[str, tuple[str, str]] = {}
    used: set[str] = set()
    ordered = sorted(rows, key=lambda e: e["id"])
    for cls, pred in CLASSES.items():
        cands = [e for e in ordered if pred(e) and e["id"] not in used and e.get("status") != "retracted"]
        if cls == "legacy_seed":
            cands.sort(key=lambda e: "INC-045" not in (e.get("source_ids") or []))
        for e in cands:
            keys = [s for s in e.get("source_ids") or [] if owners[s] == 1]
            if keys:
                picked[cls] = (e["id"], keys[0])
                used.add(e["id"])
                break
        else:
            raise AssertionError(f"no candidate row for class {cls!r}: the standing test would be vacuous")
    return picked


@pytest.fixture(scope="module")
def marked(tmp_path_factory):
    root = tmp_path_factory.mktemp("unverified_real")
    # The freeze tests' default extraction, plus the pinned precision audit
    # and the DATASHEET block that validate.py checks.
    _extract_head(root, specs=[
        "scripts", "data", "ingest", "mappings", "schema", "legacy", "docs/audits/precision", "docs/DATASHEET.md",
        "docs/audits/WS4-T19-authorized-splits-2026-09-18.json",
        "docs/audits/ID-silent-ids-appends-2026-10-09.json",
        "docs/audits/ID-group-ids-appends-2026-10-10.json"])
    _run(root, "parse_existing.py")
    # The D71 refresh gate reads its baseline from git HEAD: make the scratch
    # tree a real repo whose HEAD is the committed tree.
    for args in (("init", "-q"), ("add", "-A"),
                 ("-c", "user.email=t@e.x", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                  "commit", "-q", "-m", "baseline")):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    control = _rows(root)  # the committed build (byte-reproducible; D130-1 evidence)
    picks = pick_rows(control)
    co_path = root / "data" / "curation_overrides.json"
    co = json.loads(co_path.read_text(encoding="utf-8"))
    for cls, (_, key) in picks.items():
        ov = co["overrides"].setdefault(key, {})
        ov.update(status="unverified", status_reason={"code": "no-confirmed-source", "as_of": AS_OF})
        ov.setdefault("_note", f"D136 standing test ({cls})")
    co_path.write_text(json.dumps(co, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for script in ("merge_and_dedupe.py", "render_markdown.py", "validate.py"):
        _run(root, script)
    return root, picks, {e["id"]: e for e in control}


def test_every_class_is_marked_and_kept(marked):
    root, picks, control = marked
    by_id = {e["id"]: e for e in _rows(root)}
    assert by_id.keys() == control.keys(), "never deleted, no ID moves"
    for cls, (iid, _) in picks.items():
        assert by_id[iid]["status"] == "unverified", cls
    assert control[picks["landmark"][0]]["tier"] == "landmark"
    assert control[picks["retained"][0]]["source_status"] == "retained"
    assert control[picks["disputed"][0]]["status"] == "disputed"
    n = sum(1 for e in by_id.values() if e.get("status") == "unverified")
    assert n == len(picks) == len(CLASSES)
    full = json.loads((root / "data" / "incidents.json").read_text(encoding="utf-8"))
    slim = json.loads((root / "data" / "incidents.min.json").read_text(encoding="utf-8"))
    stats = json.loads((root / "data" / "stats.json").read_text(encoding="utf-8"))
    assert full["unverified_count"] == slim["unverified_count"] == stats["unverified_count"] == n


# ---- the existing real-corpus tests, re-pointed at the scratch root ----------


def test_landmark_count_reproducible_from_min_json(marked, monkeypatch):
    monkeypatch.setattr(tld, "ROOT", marked[0])
    tld.test_shipped_landmark_count_reproducible_from_min_json()


def test_landmark_count_reproducible_from_full_file(marked, monkeypatch):
    monkeypatch.setattr(tld, "ROOT", marked[0])
    tld.test_shipped_landmark_count_is_reproducible_from_the_full_file()


def _point_integrity(root: Path, monkeypatch) -> None:
    monkeypatch.setattr(tei, "ROOT", root)
    monkeypatch.setattr(tei, "STATS", json.loads((root / "data" / "stats.json").read_text(encoding="utf-8")))


def test_manifest_counts_agree_with_the_corpus(marked, monkeypatch):
    _point_integrity(marked[0], monkeypatch)
    tei.test_manifest_counts_agree_with_the_corpus_by_an_independent_path()
    tei.test_manifest_matches_stats_json_field_for_field()


def test_misp_real_feed_marked_set(marked, tmp_path, monkeypatch):
    _point_integrity(marked[0], monkeypatch)
    tei.test_misp_real_feed_marked_incident_set_equals_marked_rows(tmp_path, monkeypatch)


def test_stix_real_rows(marked, monkeypatch):
    monkeypatch.setattr(tem, "ROOT", marked[0])
    ids = {e["id"] for e in tem._real_rows()}
    assert not {iid for iid, _ in marked[1].values()} & ids, "_real_rows kept an unverified row"
    tem.test_real_bundle_every_object_has_valid_ordered_timestamps()
    tem.test_real_bundle_x_source_freshness_set_equals_marked_rows()


def test_published_aiid_only_excludes_unverified(marked):
    root, picks, _ = marked
    pub = {e["id"] for e in _published_aiid_only(root)}
    assert pub, "no published AIID-only rows: the check would be vacuous"
    assert not {iid for iid, _ in picks.values()} & pub


def test_stats_drift_rederivation_agrees(marked):
    import check_stats_drift as c
    root = marked[0]
    stats = json.loads((root / "data" / "stats.json").read_text(encoding="utf-8"))
    slim = json.loads((root / "data" / "incidents.min.json").read_text(encoding="utf-8"))["incidents"]
    assert c.check_stats_vs_corpus(stats, _rows(root), slim) == []


def test_real_exports_drop_every_class(marked, tmp_path, monkeypatch):
    """The exporters themselves, over the real rows: no marked row of any class
    reaches STIX, TAXII, MISP, Hugging Face or the site payload; a standing row
    does (control). (The MISP freshness test above cannot catch this: it builds
    the feed from its own filtered rows, so it is self-consistent either way.)"""
    import export_huggingface as hf
    import export_misp
    import export_stix
    import export_taxii
    import gen_docs_core_data as g
    root, picks, control = marked
    data = root / "data"
    standing = next(i for i in sorted(control) if not control[i].get("status")
                    and i not in {iid for iid, _ in picks.values()})
    monkeypatch.setattr(export_stix, "DATA", data)
    monkeypatch.setattr(export_stix, "DOCS_DATA", tmp_path / "docs_data")
    monkeypatch.setattr(export_taxii, "DATA", data)
    monkeypatch.setattr(export_taxii, "OUT", tmp_path / "taxii2")
    monkeypatch.setattr(export_misp, "DATA", data)
    monkeypatch.setattr(export_misp, "OUT", tmp_path / "misp")
    monkeypatch.setattr(hf, "DATA", data)
    monkeypatch.setattr(g, "SRC", data / "incidents.min.json")
    monkeypatch.setattr(g, "DOCS_DATA", tmp_path / "site")
    monkeypatch.setattr(g, "CORE_OUT", tmp_path / "site" / "incidents.core.json")
    monkeypatch.setattr(g, "DETAIL_DIR", tmp_path / "site" / "detail")
    export_stix.main()
    export_taxii.main()
    export_misp.main()
    hf.build(tmp_path / "hf")
    g.main()
    outputs = {
        # ID matched as a whole token: "LEGACY-INC-00131" is another row's source_id.
        "stix": (data / "incidents.stix.json").read_text(encoding="utf-8"),
        **{name: "\n".join(p.read_text(encoding="utf-8") for p in sorted((tmp_path / name).rglob("*.json*")))
           for name in ("taxii2", "misp", "hf", "site")},
    }
    for name, text in outputs.items():
        assert re.search(rf"(?<![\w-]){standing}(?!\d)", text), f"control {standing} missing from {name}"
        for cls, (iid, _) in picks.items():
            assert not re.search(rf"(?<![\w-]){iid}(?!\d)", text), f"{cls} row {iid} leaked into {name}"
