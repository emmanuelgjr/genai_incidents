"""Hold the OECD/AIID pair's ingest inputs at their committed versions.

v2.13.0 item 7 stage 1 freezes everything the OECD/AIID pair drives (D58/D67/
D71); D66 says the weekly refresh must still land AIAAIC, KEV, the CVE sweep
and the D60 retractions while that freeze holds. The fetchers for the pair keep
running every week, so this step runs AFTER them and BEFORE the merge:

  1. every file in merge_and_dedupe._PAIR_INPUT_FILES (plus the AIID snapshot's
     provenance sidecar, which must stay consistent with its snapshot) that
     differs from git HEAD is copied to --stash-dir, then restored to HEAD (or
     removed if it is not tracked);
  2. HOLD_REPORT.json in --stash-dir records, per file, whether it changed and
     the sha256 of the held (fresh) and committed bytes. The workflow uploads
     the directory as the artifact the D42 review path reads;
  3. merge_and_dedupe._pair_inputs_changed() is called on the result and the
     script exits 1 if it still reports a difference. That is the gate's own
     detector, so a restore that did not take cannot reach the merge.

Why a restore and not a flag in the merge: the gate (_run_refresh_gate) is not
touched, the list of frozen files stays single-sourced in merge_and_dedupe.py,
and the held tree is byte-identical to main for every frozen input, which is
the precondition under which the gate's A2 content-change check is vacuous.

AIRI: airi_navigator_incidents.json is in _PAIR_INPUT_FILES (D71 reading: AIID-
keyed AIRI rows count as the pair), so a revived AIRI is held too. Its fresh
file goes to the artifact and is not merged until the user rules; it does not
turn the run red.

No network, no model calls; git only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import merge_and_dedupe as m  # noqa: E402

EXTRA_HELD = ("aiid_full.provenance.json",)


def held_files() -> tuple[str, ...]:
    return tuple(m._PAIR_INPUT_FILES) + tuple(
        f for f in EXTRA_HELD if f not in m._PAIR_INPUT_FILES
    )


def _sha(b: bytes | None) -> str | None:
    return hashlib.sha256(b).hexdigest() if b is not None else None


def hold(root: Path, stash_dir: Path) -> dict:
    stash_dir.mkdir(parents=True, exist_ok=True)
    report: dict = {"files": {}}
    for name in held_files():
        rel = f"ingest/{name}"
        path = root / rel
        shown = m._git(root, "show", f"HEAD:{rel}")
        committed = shown.stdout if shown.returncode == 0 else None
        fresh = path.read_bytes() if path.exists() else None
        changed = fresh != committed
        report["files"][name] = {
            "changed": changed,
            "fresh_sha256": _sha(fresh),
            "committed_sha256": _sha(committed),
        }
        if not changed:
            continue
        if fresh is not None:
            shutil.copyfile(path, stash_dir / name)
        if committed is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(committed)
    report["held_count"] = sum(1 for v in report["files"].values() if v["changed"])
    (stash_dir / "HOLD_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stash-dir", required=True, type=Path)
    ap.add_argument("--root", type=Path, default=m.ROOT)
    args = ap.parse_args(argv)
    report = hold(args.root, args.stash_dir)
    for name, v in sorted(report["files"].items()):
        print(f"  {'HELD   ' if v['changed'] else 'same   '} ingest/{name}")
    print(f"held {report['held_count']} of {len(report['files'])} frozen input file(s)")
    if m._pair_inputs_changed(args.root):
        print("[FATAL] hold did not take: a frozen input still differs from HEAD.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
