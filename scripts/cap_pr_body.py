#!/usr/bin/env python3
"""Whole-body guard for the refresh PR (D123).

GitHub rejects a pull-request body over 65,536 characters, and
peter-evans/create-pull-request would then fail the run instead of opening the
PR. If the assembled body is over --max (default 60,000, a safe margin), keep
the head (the fixed text and the retraction report come first) and truncate the
appended sections at a line boundary with a note. Never fails on size.

    python scripts/cap_pr_body.py FILE [--max 60000]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

GITHUB_LIMIT = 65_536
DEFAULT_MAX = 60_000


def cap_body(text: str, max_chars: int = DEFAULT_MAX) -> str:
    if len(text) <= max_chars:
        return text
    note = (f"\n\n**PR body truncated at {max_chars:,} characters** (it was {len(text):,}; GitHub's limit is "
            f"{GITHUB_LIMIT:,}). The sections after this point were cut; the full AIID change report is in the "
            "run's step summary and the `aiid-change-report` artifact, and `git diff` against `main` shows the data.\n")
    cut = text[: max_chars - len(note)]
    cut = cut[: cut.rfind("\n")] if "\n" in cut else cut
    return cut + note


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--max", type=int, default=DEFAULT_MAX)
    a = ap.parse_args()
    p = Path(a.file)
    text = p.read_text(encoding="utf-8")
    out = cap_body(text, a.max)
    if out != text:
        p.write_text(out, encoding="utf-8", newline="\n")
        print(f"[cap-pr-body] truncated {len(text):,} -> {len(out):,} characters")
    else:
        print(f"[cap-pr-body] {len(text):,} characters, within {a.max:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
