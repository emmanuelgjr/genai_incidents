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
import json
import os
import re
import shutil
import subprocess
import sys
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


def test_gate_aborts_on_fresh_bridging_input_and_not_on_committed_inputs(tmp_path):
    """Scratch copy of the repo. Control: committed inputs build clean. Fresh
    input: ONE new OECD row cross-referencing two already-published AIID
    entries (the mechanism of the 2026-10-03 diagnosis, constructed because a
    live crawl is out of scope here) must abort with "Nothing was written"
    and leave every data file and both ingest files byte-identical."""
    for d in ("scripts", "data", "ingest", "mappings", "schema"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("__pycache__", "_cache"))
    (tmp_path / "docs" / "audits").mkdir(parents=True)
    shutil.copy(ROOT / "docs/audits/WS4-T19-authorized-splits-2026-09-18.json", tmp_path / "docs/audits")

    control = _run_merge(tmp_path)
    assert control.returncode == 0, control.stdout[-800:] + control.stderr[-800:]
    assert "Nothing was written" not in control.stdout + control.stderr

    inc = json.loads((tmp_path / "data/incidents.json").read_text(encoding="utf-8"))["incidents"]
    pub = [e for e in inc if e.get("status") != "retracted" and e.get("aiid_id")
           and not _oecd_ids(e) and len(e["source_ids"]) == 1 and e["source_ids"][0].startswith("AIID-")]
    a, b = pub[0], pub[1]
    raw_path = tmp_path / "ingest" / "oecd_aim_full_incidents.json"
    rows = json.loads(raw_path.read_text(encoding="utf-8"))
    row = copy.deepcopy(rows[0])
    row.update(source_id="OECD-AIM-2026-10-01-zz01", title="Synthetic bridge row (test)",
               extra_source_ids=[a["source_ids"][0], b["source_ids"][0]],
               references=[{"title": "x", "url": "https://oecd.ai/en/incidents/2026-10-01-zz01", "type": "report"}])
    row["description"] = rebuild_template(row)
    rows.append(row)
    raw_path.write_text(json.dumps(rows, indent=1), encoding="utf-8")

    before = _tree_hash(tmp_path)
    fresh = _run_merge(tmp_path)
    out = fresh.stdout + fresh.stderr
    assert fresh.returncode != 0
    assert "D42/D25(a)" in out and "Nothing was written" in out
    assert _tree_hash(tmp_path) == before, "gate aborted but the data tree changed"


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
