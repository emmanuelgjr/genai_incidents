"""D123: the refresh PR body must stay under GitHub's 65,536-character limit.

Each check names the input that makes it fail (agreement 6): an oversized
report / body. The fire-proof is the run with the cap removed (recorded in the
board report); `test_caps_are_what_bound_the_size` also proves it in-process."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import aiid_change_report as r
import cap_pr_body as c

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "auto-refresh.yml"
LIMIT = 65_536


def _huge_report() -> str:
    before = {"incidents": [{"id": f"INC-{i:05d}", "source_ids": [f"AIID-{i}"], "title": "T" * 80,
                             "severity": "Medium", "date": "2020-01-01", "year": 2020, "corpus": "security",
                             "attack_vector": "x"} for i in range(1500)]}
    after = {"incidents": [dict(e, title="U" * 200, severity="Critical", date="2015-01-01", year=2015,
                                corpus="ai-harm", attack_vector="y") for e in before["incidents"]]}
    return r.render_md(r.diff(before, after))


def test_oversized_report_is_capped_below_the_limit_and_carries_the_note():
    full = _huge_report()
    assert len(full) > r.MAX_REPORT_CHARS, "synthetic report is not oversized; the test would pass vacuously"
    capped = r.cap(full)
    assert len(capped) <= r.MAX_REPORT_CHARS < LIMIT
    assert f"truncated at {r.MAX_REPORT_CHARS:,} characters" in capped
    assert "step summary" in capped and "aiid-change-report" in capped
    assert capped.startswith("### AIID-driven changes")  # the head (counts) survives


def test_small_report_is_untouched():
    assert r.cap("short") == "short"


def test_caps_are_what_bound_the_size(monkeypatch):
    """With the cap neutralised the same input exceeds its limit: the assertions
    above are therefore sensitive to the cap, not to the input being small."""
    full = _huge_report()
    assert len(full) > r.MAX_REPORT_CHARS
    monkeypatch.setattr(r, "cap", lambda md, max_chars=0: md)
    assert len(r.cap(full)) > r.MAX_REPORT_CHARS


def test_whole_body_guard_truncates_an_oversized_body():
    body = "fixed head\n" + "\n".join(f"| row {i} | " + "x" * 100 + " |" for i in range(2000))
    assert len(body) > LIMIT
    out = c.cap_body(body)
    assert len(out) <= c.DEFAULT_MAX < LIMIT
    assert out.startswith("fixed head\n") and "PR body truncated at 60,000 characters" in out


def test_whole_body_guard_leaves_a_normal_body_alone():
    body = "normal body\n" * 50
    assert c.cap_body(body) == body


def test_whole_body_guard_script_rewrites_the_file(tmp_path):
    p = tmp_path / "pr-body.md"
    p.write_text("a\n" * 40_000, encoding="utf-8")
    assert p.stat().st_size > LIMIT
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "cap_pr_body.py"), str(p)],
                         capture_output=True, text=True)
    assert res.returncode == 0 and len(p.read_text(encoding="utf-8")) <= c.DEFAULT_MAX


def test_workflow_caps_the_body_before_the_pr_step_and_keeps_the_full_report():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/cap_pr_body.py" in text
    assert text.index("scripts/cap_pr_body.py") < text.index("uses: peter-evans/create-pull-request")
    assert "--out-full-md" in text and "$GITHUB_STEP_SUMMARY" in text and "name: aiid-change-report" in text
