"""v2.13.0 item 7, stage 1 (user ruling D58, option C): the OECD/AIID refresh
freeze is a DELIBERATE, fail-closed gate, and every OECD-template description
carries its provenance label.

Each check below names the input that makes it fail and a test shows it fail
(working agreement 6). Derivation paths are independent of the code under test:
the label checks rebuild the OECD template from the RAW ingest row with
``ingest_oecd_aim.build_description`` (the pipeline's own function, applied to
raw fields the merge never touches) and compare to the shipped description; the
gate check runs the real ``scripts/merge_and_dedupe.py`` in a scratch copy of
the repo, so nothing in the committed tree is touched.

Spec: docs/audits/oecd-aiid-unfreeze-decision-memo-2026-10-09.md section 7
(S2, S5); build record docs/audits/oecd-stage1-build-2026-10-09.md.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

import ingest_oecd_aim as oecd
import merge_and_dedupe as m

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "auto-refresh.yml"

OECD_PREFIX = "Tracked by the OECD AI Incidents and Hazards Monitor (AIM) as"
AIID_PREFIX = "AI Incident Database (AIID) entry #"
CITATION = re.compile(
    r"^OECD \((\d{4})\), AI Incidents and Hazards Monitor, (https://oecd\.ai/en/incidents/\S+) "
    r"\(accessed on (\d{4}-\d{2}-\d{2})\)$"
)

# OECD-AIM-sourced rows that legitimately ship neither the OECD template nor
# the AIID template: a merge survivor whose description was authored by another
# source (verified by reading each row, 2026-10-09). A stale entry fails.
KNOWN_NON_OECD_DESCRIPTION = {
    "INC-01435": "LEGACY-INC-00173 text",
    "INC-00813": "CVE/RES text",
    "INC-00602": "EXT-2025-MEXICO-WATER text",
    "INC-06470": "ATLAS-AML.CS0006 text",
    "INC-01434": "CVE-2026-21520 text",
}


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _raw_oecd() -> dict[str, dict]:
    return {r["source_id"]: r for r in _load("ingest/oecd_aim_full_incidents.json")}


def rebuild_template(raw: dict) -> str:
    """The OECD template, rebuilt from a RAW ingest row's structural fields."""
    sid = raw["source_id"]
    slug = sid[len("OECD-AIM-"):]
    return oecd.build_description(
        sid, raw["date"], f"https://oecd.ai/en/incidents/{slug}", raw["affected"], raw["attack_vector"]
    )


def _oecd_ids(e: dict) -> list[str]:
    return [s for s in e.get("source_ids", []) if s.startswith("OECD-AIM-")]


def check_labels(incidents: list[dict], raw: dict[str, dict]) -> list[str]:
    """S2, both directions. A: every row labelled oecd-aim ships the template
    rebuilt from one of its own raw rows. B: every row whose description is
    that rebuilt template, or merely LOOKS like it (prefix), is labelled."""
    problems = []
    for e in incidents:
        rebuilt = {rebuild_template(raw[s]) for s in _oecd_ids(e) if s in raw}
        labelled = (e.get("description_provenance"), e.get("description_source")) == ("original", "oecd-aim")
        desc = e.get("description") or ""
        if e.get("description_source") == "oecd-aim" and desc not in rebuilt:
            problems.append(f"{e['id']}: labelled oecd-aim but description is not the rebuilt OECD template")
        if (desc in rebuilt or desc.startswith(OECD_PREFIX)) and not labelled:
            problems.append(f"{e['id']}: OECD-template description is not labelled original/oecd-aim")
        if desc.startswith(AIID_PREFIX) and e.get("description_source") == "oecd-aim":
            problems.append(f"{e['id']}: AIID-template description carries an oecd-aim label")
    return problems


def check_partition(incidents: list[dict], raw: dict[str, dict], exempt=KNOWN_NON_OECD_DESCRIPTION) -> list[str]:
    """Full-corpus: every OECD-AIM-sourced row's description is exactly one of
    (a) the rebuilt OECD template, (b) AIID's template (AIID won the merge),
    (c) a named non-OECD-authored description. Nothing else."""
    problems, seen_exempt = [], set()
    for e in incidents:
        ids = _oecd_ids(e)
        if not ids:
            continue
        desc = e.get("description") or ""
        if any(s not in raw for s in ids):
            problems.append(f"{e['id']}: OECD source id absent from ingest/oecd_aim_full_incidents.json")
        elif desc in {rebuild_template(raw[s]) for s in ids}:
            pass
        elif desc.startswith(AIID_PREFIX):
            pass
        elif e["id"] in exempt:
            seen_exempt.add(e["id"])
        else:
            problems.append(f"{e['id']}: description is neither the OECD template, AIID's template nor a named exemption")
    for stale in sorted(set(exempt) - seen_exempt):
        problems.append(f"exemption {stale} is stale (row is now explained or gone)")
    return problems


def check_attribution(incidents: list[dict]) -> list[str]:
    """100% of OECD-AIM-sourced rows carry
    `OECD (<year>), AI Incidents and Hazards Monitor, <url> (accessed on <date>)`
    on an oecd.ai reference whose URL is the one in the title, dated `added`."""
    problems = []
    for e in incidents:
        if not _oecd_ids(e):
            continue
        ok = False
        for r in e.get("references") or []:
            mt = CITATION.match(r.get("title") or "")
            if mt and mt.group(2) == r.get("url") and mt.group(3) == e.get("added"):
                ok = True
        if not ok:
            problems.append(f"{e['id']}: no OECD attribution reference")
    return problems


@pytest.fixture(scope="module")
def corpus():
    return _load("data/incidents.json")["incidents"], _raw_oecd()


# ---- the derivation itself is sound (positive control) --------------------


def test_template_rebuild_reproduces_every_raw_row(corpus):
    _, raw = corpus
    assert len(raw) > 4000, "OECD raw ingest looks empty; every check below would pass vacuously"
    bad = [sid for sid, r in raw.items() if rebuild_template(r) != r["description"]]
    assert bad == [], f"rebuild disagrees with raw description for {len(bad)} rows, e.g. {bad[:3]}"


# ---- S2: labels, both directions ------------------------------------------


def test_every_oecd_template_row_is_labelled_and_every_label_is_earned(corpus):
    inc, raw = corpus
    labelled = [e for e in inc if e.get("description_source") == "oecd-aim"]
    assert len(labelled) > 3900  # not vacuous: the OECD population is ~3.9k rows
    assert check_labels(inc, raw) == []


def test_s2_fires_when_a_template_row_is_unlabelled(corpus):
    inc, raw = corpus
    rows = copy.deepcopy(inc)
    victim = next(e for e in rows if e.get("description_source") == "oecd-aim")
    victim.pop("description_provenance")
    victim.pop("description_source")
    assert any(victim["id"] in p and "not labelled" in p for p in check_labels(rows, raw))


def test_s2_fires_when_an_aiid_template_row_is_relabelled(corpus):
    inc, raw = corpus
    rows = copy.deepcopy(inc)
    victim = next(e for e in rows if (e.get("description") or "").startswith(AIID_PREFIX) and _oecd_ids(e))
    victim["description_provenance"], victim["description_source"] = "original", "oecd-aim"
    probs = check_labels(rows, raw)
    assert any(victim["id"] in p and "AIID-template" in p for p in probs)


def test_s2_fires_on_a_label_over_edited_template_text(corpus):
    inc, raw = corpus
    rows = copy.deepcopy(inc)
    victim = next(e for e in rows if e.get("description_source") == "oecd-aim")
    victim["description"] = victim["description"] + " (edited)"
    assert any(victim["id"] in p and "not the rebuilt" in p for p in check_labels(rows, raw))


def test_s2_fires_on_a_prefix_spoof_without_label(corpus):
    inc, raw = corpus
    rows = copy.deepcopy(inc)
    victim = next(e for e in rows if not _oecd_ids(e) and not e.get("description_source"))
    victim["description"] = OECD_PREFIX + " X. spoofed"
    assert any(victim["id"] in p and "not labelled" in p for p in check_labels(rows, raw))


# ---- S5: full-corpus template partition + attribution ---------------------


def test_every_oecd_sourced_row_description_is_explained(corpus):
    inc, raw = corpus
    assert check_partition(inc, raw) == []


def test_partition_fires_on_oecd_narrative_like_text(corpus):
    inc, raw = corpus
    rows = copy.deepcopy(inc)
    victim = next(e for e in rows if e.get("description_source") == "oecd-aim")
    victim["description"] = "Free-form narrative that is not the template."
    assert any(victim["id"] in p for p in check_partition(rows, raw))


def test_partition_fires_on_stale_exemption(corpus):
    inc, raw = corpus
    assert any("stale" in p for p in check_partition(inc, raw, exempt={**KNOWN_NON_OECD_DESCRIPTION, "INC-00001": "x"}))


def test_every_oecd_row_carries_the_attribution_reference(corpus):
    inc, _ = corpus
    n = sum(1 for e in inc if _oecd_ids(e))
    assert n > 4000
    assert check_attribution(inc) == []


def test_attribution_fires_when_citation_is_removed_or_misdated(corpus):
    inc, _ = corpus
    rows = copy.deepcopy(inc)
    a, b = [e for e in rows if _oecd_ids(e)][:2]
    a["references"] = [r for r in a["references"] if not CITATION.match(r.get("title") or "")]
    b["added"] = "1999-01-01"
    probs = check_attribution(rows)
    assert any(a["id"] in p for p in probs) and any(b["id"] in p for p in probs)


# ---- S5: the approval set is empty ----------------------------------------


def test_committed_approval_set_is_empty():
    p = m.REFRESH_MERGE_APPROVAL_PATH
    assert not p.exists() or json.loads(p.read_text(encoding="utf-8")).get("entries") == []
    assert m._load_refresh_merge_approvals(p) == set()


def test_emptiness_check_fires_on_a_signed_nonempty_list(tmp_path):
    entries = [{"kind": "merge", "from": "INC-00002", "into": "INC-00001"}]
    p = tmp_path / "approved.json"
    p.write_text(json.dumps({
        "entries": entries,
        "authorization": {"decision": "DX", "ruled_by": "user",
                          "entries_sha256": m._refresh_merge_entries_sha256(entries)},
    }), encoding="utf-8")
    assert m._load_refresh_merge_approvals(p) != set()  # the assertion above would fail on this


# ---- S5: the gate on fresh inputs vs committed inputs ----------------------


def _tree_hash(root: Path) -> dict[str, str]:
    out = {}
    for sub in ("data", "ingest/aiid_full.json", "ingest/oecd_aim_full_incidents.json"):
        base = root / sub
        files = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.is_file())
        for f in files:
            out[str(f.relative_to(root)).replace("\\", "/")] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def _run_merge(root: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(root / "scripts" / "merge_and_dedupe.py")],
                          cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _extract_head(root: Path, repo: Path = ROOT, specs: list[str] | None = None) -> None:
    """Populate `root` from the COMMITTED tree (git HEAD via `git archive`).
    Extracted so a fast test can pin the no-leak property (followups b10)."""
    # Build from COMMITTED content only, read out of git HEAD (`git archive`),
    # never from the caller's working tree. A copy of working-tree bytes would
    # leak (i) gitignored/untracked files (e.g. data/legacy_consolidated.json,
    # which exists only after parse_existing.py has run) and (ii) any
    # uncommitted edit to a tracked file, so the suite could pass or fail
    # depending on what the caller's tree happens to contain (followups b10).
    if specs is None:
        specs = ["scripts", "data", "ingest", "mappings", "schema", "legacy",
                 "docs/audits/WS4-T19-authorized-splits-2026-09-18.json",
                 # v2.13.0 item 4 / D69: step 8b reads the ruled deprecation appends from
                 # docs/audits; without them the control build would not reproduce the
                 # committed id_deprecations.json (it would drop the ruled records).
                 "docs/audits/ID-silent-ids-appends-2026-10-09.json",
                 "docs/audits/ID-group-ids-appends-2026-10-10.json"]
    in_head = [sp for sp in specs
               if subprocess.run(["git", "ls-tree", "--name-only", "HEAD", "--", sp],
                                 cwd=repo, check=True, capture_output=True).stdout.strip()]
    archive = subprocess.run(["git", "archive", "--format=tar", "HEAD", "--", *in_head],
                             cwd=repo, check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        tf.extractall(root, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))


@pytest.fixture(scope="module")
def scratch(tmp_path_factory):
    """Scratch copy of the repo after a CONTROL build on committed inputs."""
    root = tmp_path_factory.mktemp("scratch_repo")
    _extract_head(root)
    # the merge reads data/legacy_consolidated.json (gitignored), so build it
    # here exactly as CI's "Re-merge" step does
    legacy = subprocess.run([sys.executable, str(root / "scripts" / "parse_existing.py")], cwd=root,
                            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert legacy.returncode == 0, legacy.stdout[-800:] + legacy.stderr[-800:]
    # D71: the gate reads its baseline and the "OECD/AIID inputs changed" signal
    # from git HEAD, so the scratch repo is a real one with the committed tree.
    for args in (("init", "-q"), ("add", "-A"),
                 ("-c", "user.email=t@e.x", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                  "commit", "-q", "-m", "baseline")):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    control = _run_merge(root)
    assert control.returncode == 0, control.stdout[-800:] + control.stderr[-800:]
    assert "Nothing was written" not in control.stdout + control.stderr
    # A4: pristine copy of the post-control data tree, so every test can restore
    # it and stand alone (a build that wrongly succeeds writes data/).
    shutil.copytree(root / "data", root.parent / (root.name + "_pristine_data"))
    return root


def test_scratch_inputs_come_from_head_not_the_working_tree(tmp_path):
    """b10, self-contained (works in a clean CI checkout): a tiny temporary git
    repo with a committed file, a dirty edit to it, and an untracked file.
    `_extract_head` must return the committed bytes and omit the untracked one."""
    repo, out = tmp_path / "repo", tmp_path / "out"
    (repo / "data").mkdir(parents=True)
    out.mkdir()
    tracked = repo / "data" / "x.json"
    tracked.write_bytes(b'{"committed": true}\n')
    for args in (("init", "-q"), ("config", "core.autocrlf", "false"), ("add", "-A"),
                 ("-c", "user.email=t@e.x", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                  "commit", "-q", "-m", "c")):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
    tracked.write_bytes(b'{"DIRTY": true}\n')                      # uncommitted edit
    (repo / "data" / "legacy_consolidated.json").write_bytes(b"{}")  # untracked
    _extract_head(out, repo=repo, specs=["data"])
    assert (out / "data" / "x.json").read_bytes() == b'{"committed": true}\n'
    assert not (out / "data" / "legacy_consolidated.json").exists()


def _restore_data(root: Path) -> None:
    pristine = root.parent / (root.name + "_pristine_data")
    shutil.rmtree(root / "data")
    shutil.copytree(pristine, root / "data")


D114_PRECONDITION = ("D114 binding precondition",)
GATE_MARKERS = ("D42/D25(a)", "D58/D67/D71")


def _fresh_input_aborts(root: Path, ingest_name: str, mutate, expect: str,
                        markers: tuple[str, ...] = GATE_MARKERS) -> str:
    """Apply `mutate` to an ingest file's rows, run the real merge, require an
    abort that wrote nothing, then restore the file."""
    path = root / "ingest" / ingest_name
    original_bytes = path.read_bytes()  # byte-exact restore (Windows write_text would rewrite newlines)
    original = original_bytes.decode("utf-8")
    try:
        rows = json.loads(original)
        mutate(rows)
        path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        before = _tree_hash(root)
        before[f"ingest/{ingest_name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
        res = _run_merge(root)
        out = res.stdout + res.stderr
        assert res.returncode != 0, out[-600:]
        assert "Nothing was written" in out and all(mk in out for mk in markers)
        assert expect in out, out[-1200:]
        after = _tree_hash(root)
        after[f"ingest/{ingest_name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert after == before, "gate aborted but the data tree changed"
        return out
    finally:
        path.write_bytes(original_bytes)
        _restore_data(root)


def _fresh_input_passes(root: Path, ingest_name: str, mutate) -> tuple[str, list[dict]]:
    """Counterpart for the LIFTED side: apply `mutate`, run the real merge, require
    exit 0 through the D114 standing class, return (stdout, rebuilt incidents),
    then restore the file and the data tree."""
    path = root / "ingest" / ingest_name
    original_bytes = path.read_bytes()  # byte-exact restore (Windows write_text would rewrite newlines)
    original = original_bytes.decode("utf-8")
    try:
        rows = json.loads(original)
        mutate(rows)
        path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        res = _run_merge(root)
        out = res.stdout + res.stderr
        assert res.returncode == 0, out[-1200:]
        assert "D114 standing AIID class" in out
        return out, json.loads((root / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
    finally:
        path.write_bytes(original_bytes)
        _restore_data(root)


def _published_aiid_only(root: Path) -> list[dict]:
    inc = json.loads((root / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
    return [e for e in inc if e.get("status") != "retracted" and e.get("aiid_id")
            and not _oecd_ids(e) and len(e["source_ids"]) == 1 and e["source_ids"][0].startswith("AIID-")]


def _synthetic_oecd_row(rows: list[dict], sid: str, extra: list[str]) -> dict:
    row = copy.deepcopy(rows[0])
    row.update(source_id=sid, title="Synthetic row (test)", extra_source_ids=extra,
               references=[{"title": "x", "url": f"https://oecd.ai/en/incidents/{sid[len('OECD-AIM-'):]}", "type": "report"}])
    row["description"] = rebuild_template(row)
    return row


@pytest.mark.slow
def test_committed_inputs_do_not_abort(scratch):
    """The control build in the fixture exited 0 on the committed inputs; the
    committed data tree is also unchanged by it (rebuild is a fixed point)."""
    for rel in ("data/incidents.json", "data/id_deprecations.json"):
        # Compare against the COMMITTED bytes (same source as the fixture's inputs),
        # not the working tree: the refresh workflows run this suite on an
        # uncommitted, freshly re-merged tree.
        head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, check=True,
                              capture_output=True).stdout
        assert (scratch / rel).read_bytes() == head, rel


@pytest.mark.slow
def test_gate_aborts_on_fresh_bridging_input(scratch):
    """ONE new OECD row cross-referencing two already-published AIID entries
    (the 2026-10-03 mechanism, constructed: a live crawl is out of scope)."""
    a, b = _published_aiid_only(scratch)[:2]
    _fresh_input_aborts(
        scratch, "oecd_aim_full_incidents.json",
        lambda rows: rows.append(_synthetic_oecd_row(
            rows, "OECD-AIM-2026-10-01-zz01", [a["source_ids"][0], b["source_ids"][0]])),
        "suppression (A3) has not been built and gated",
        markers=D114_PRECONDITION,
    )


@pytest.mark.slow
def test_d67_gate_aborts_on_a_new_oecd_row(scratch):
    """D67: a purely ADDED OECD row (no AIID cross-reference, no merge)."""
    out = _fresh_input_aborts(
        scratch, "oecd_aim_full_incidents.json",
        lambda rows: rows.append(_synthetic_oecd_row(rows, "OECD-AIM-2026-10-02-zz02", [])),
        "suppression (A3) has not been built and gated",
        markers=D114_PRECONDITION,
    )
    # D116: no new OECD rows reach the corpus while OECD is held
    assert "merge INC-" not in out and "title edit INC-" not in out


@pytest.mark.slow
def test_d114_aiid_title_edit_passes_the_standing_class(scratch):
    """D114: AIID edits the title of an already-published, AIID-only row. Before
    the lift this aborted ("title edit INC-", D67(b)); the standing AIID class now
    passes it because the new title is exactly the snapshot's own title for one
    of the row's AIID ids."""
    pub = _published_aiid_only(scratch)[0]
    victim = pub["source_ids"][0]

    def edit(rows):
        row = next(r for r in rows if r.get("source_id") == victim)
        row["title"] = row["title"] + " (edited upstream)"

    out, rebuilt = _fresh_input_passes(scratch, "aiid_full.json", edit)
    assert "1 AIID title edit(s)" in out
    assert next(e for e in rebuilt if e["id"] == pub["id"])["title"].endswith("(edited upstream)")


# ---- S5: weekly workflow fails closed at the merge step --------------------


def _steps(text: str) -> list[str]:
    return re.split(r"(?m)^      - (?=name:|uses:)", text)[1:]


def check_fail_closed(text: str) -> list[str]:
    """The merge step must be able to fail the job, and no step that opens or
    edits the PR may run after a failure of it."""
    steps = _steps(text)
    idx = next((i for i, s in enumerate(steps) if "scripts/merge_and_dedupe.py" in s), None)
    if idx is None:
        return ["no step runs scripts/merge_and_dedupe.py"]
    problems = []
    if "continue-on-error" in steps[idx]:
        problems.append("merge step must not be continue-on-error (the D42 gate would be advisory)")
    cpr = next((i for i, s in enumerate(steps) if "uses: peter-evans/create-pull-request" in s), None)
    if cpr is None or cpr < idx:
        problems.append("PR step must come after the merge step")
    for s in steps[idx + 1:]:
        head = s.split("\n", 1)[0]
        if re.search(r"(?m)^        if:.*\b(always|failure)\(\)", s) and ("uses: peter-evans/create-pull-request" in s or "gh pr" in s):
            problems.append(f"step {head!r} could open or edit a PR after a gate abort")
    return problems


def test_weekly_workflow_fails_closed_at_the_merge_step():
    assert check_fail_closed(WORKFLOW.read_text(encoding="utf-8")) == []


def test_fail_closed_check_fires():
    text = WORKFLOW.read_text(encoding="utf-8")
    steps = _steps(text)
    merge = next(s for s in steps if "scripts/merge_and_dedupe.py" in s)
    assert check_fail_closed(text.replace(merge, merge.rstrip("\n") + "\n        continue-on-error: true\n"))
    cpr = next(s for s in steps if "uses: peter-evans/create-pull-request" in s)
    assert check_fail_closed(text.replace(cpr, cpr.replace("        uses:", "        if: always()\n        uses:", 1)))


@pytest.mark.slow
def test_d114_new_aiid_only_row_passes_and_ships_as_a_standalone_row(scratch):
    """D114: a purely ADDED AIID row (the weekly snapshot gains new incidents).
    Before the lift this aborted ("add OECD/AIID source(s) ['AIID-99999']")."""
    def add(rows):
        row = copy.deepcopy(rows[0])
        row.update(source_id="AIID-99999", aiid_id=99999, title="Synthetic AIID row (test)")
        row["references"] = [{"title": "AIID incident #99999", "url": "https://incidentdatabase.ai/cite/99999/",
                              "type": "report"}]
        row["description"] = "AI Incident Database (AIID) entry #99999: Synthetic AIID row (test)."
        rows.append(row)

    out, rebuilt = _fresh_input_passes(scratch, "aiid_full.json", add)
    assert "1 AIID source row(s) added" in out
    new = [e for e in rebuilt if "AIID-99999" in e["source_ids"]]
    assert len(new) == 1 and new[0]["source_ids"] == ["AIID-99999"]


@pytest.mark.slow
def test_d114_snapshot_gaining_an_id_a_published_row_cites_passes(scratch):
    """The former A2 abort case: INC-00437 cites AIID-1574, which the committed
    snapshot lacks; a snapshot that gains it rewrites INC-00437's content. This is
    AIID-driven content on a published row with no merge and no absorbed id, the
    exact shape the D114 class covers (and the same shape as the 2 real rows
    INC-00437/INC-14682 in the lift's own delta)."""
    def add(rows):
        if any(r.get("source_id") == "AIID-1574" for r in rows):
            return
        base = copy.deepcopy(rows[0])
        base.update(source_id="AIID-1574", aiid_id=1574, title="Snapshot title for 1574", severity="Critical",
                    date="2026-04-03", year=2026,
                    references=[{"title": "AIID incident #1574", "url": "https://incidentdatabase.ai/cite/1574/",
                                 "type": "report"}])
        base["description"] = "AI Incident Database (AIID) entry #1574: Snapshot title for 1574."
        rows.append(base)

    _out, rebuilt = _fresh_input_passes(scratch, "aiid_full.json", add)
    assert any("AIID-1574" in e["source_ids"] for e in rebuilt)


@pytest.mark.slow
def test_a2_content_change_is_not_held_when_pair_inputs_are_committed(scratch):
    """Counterpart: a content change driven by a NON-pair input (here a CVE-only
    row's severity edited in the CVE ingest file) is not held, because no
    OECD/AIID input differs from HEAD. Proves the rule does not over-hold."""
    _restore_data(scratch)
    path = scratch / "ingest" / "cve_incidents.json"
    original_bytes = path.read_bytes()  # byte-exact restore (Windows write_text would rewrite newlines)
    original = original_bytes.decode("utf-8")
    rows = json.loads(original)
    inc = json.loads((scratch / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
    cve_only = {e["source_ids"][0]: e for e in inc if len(e["source_ids"]) == 1 and e["source_ids"][0].startswith("CVE-")}
    victim = next(r for r in rows if r.get("source_id") in cve_only and r.get("severity") != "Critical")
    victim["severity"] = "Critical"
    try:
        path.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        res = _run_merge(scratch)
        assert res.returncode == 0, (res.stdout + res.stderr)[-800:]
        new = json.loads((scratch / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
        assert next(e for e in new if e["source_ids"] == [victim["source_id"]])["severity"] == "Critical"
    finally:
        path.write_bytes(original_bytes)
        _restore_data(scratch)


@pytest.mark.slow
def test_a1_gate_aborts_on_an_airi_only_change_to_an_aiid_linked_row(scratch):
    """AIRI rows are keyed AIID-<n>; an AIRI-only edit (tags here) of a row that
    is published under that AIID id moves the published row. With airi_navigator
    in the pair inputs and the four other pair files at HEAD, it must abort."""
    airi = json.loads((scratch / "ingest/airi_navigator_incidents.json").read_text(encoding="utf-8"))
    inc = json.loads((scratch / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
    by_sid = {s: e for e in inc for s in e["source_ids"]}
    victim = next(r["source_id"] for r in airi
                  if r["source_id"].startswith("AIID-") and r["source_id"] in by_sid
                  and not _oecd_ids(by_sid[r["source_id"]]))

    def edit(rows):
        row = next(r for r in rows if r.get("source_id") == victim)
        row["tags"] = list(row.get("tags") or []) + ["airi-edit-test"]

    # D114: AIRI is a held input, so the OECD-lift precondition fires first
    out = _fresh_input_aborts(scratch, "airi_navigator_incidents.json", edit,
                              "suppression (A3) has not been built and gated",
                              markers=D114_PRECONDITION)
    assert "add OECD/AIID" not in out
