"""scripts/lint_atlas_ids.py -- CI lint: no ATLAS id may be absent from, or
deprecated in, the PINNED ATLAS release (``mappings/mitre_atlas.json``).

Exit 0 = clean, exit 1 = at least one violation (listed), exit 2 = lint could
not run (missing/corrupt input -- never a silent pass).

Checked, in order:

1. ``data/incidents.json`` -- every id in every entry's ``mitre_atlas`` and
   ``mitre_atlas_tactics`` (the structured fields; free-text mentions of
   ``AML.CS*`` case-study ids in prose are not ATLAS technique/tactic claims).
2. ``mappings/*.json`` -- every ``AML.T*`` / ``AML.TA*`` id anywhere in the file,
   except ``mitre_atlas.json`` (the pin itself, whose deprecated records are the
   point) and ``atlas_id_translations.json`` (whose KEYS are deliberately old
   ids; its ``to`` targets are linted instead).
3. Pin integrity -- the pin is derived, not hand-edited: its ``version`` must
   equal the committed snapshot's ``collection.version``, the snapshot's sha256
   must match ``ingest/atlas/ATLAS.provenance.json``, and rebuilding the pin
   from the snapshot must reproduce ``mitre_atlas.json`` exactly.

``--root DIR`` lints another checkout/scratch copy (used by the tests).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import atlas_pin  # noqa: E402

SKIP_MAPPINGS = {"mitre_atlas.json", "atlas_id_translations.json"}


def collect_ids(root: Path) -> dict[str, list[str]]:
    """id -> list of places it was found."""
    found: dict[str, list[str]] = {}

    def add(i: str, where: str) -> None:
        found.setdefault(i, []).append(where)

    inc = json.loads((root / "data" / "incidents.json").read_text(encoding="utf-8"))["incidents"]
    for e in inc:
        for fld in ("mitre_atlas", "mitre_atlas_tactics"):
            for i in e.get(fld) or []:
                if isinstance(i, str) and i.startswith("AML."):
                    add(i, f"data/incidents.json:{e.get('id', '?')}.{fld}")
    mdir = root / "mappings"
    for p in sorted(mdir.glob("*.json")):
        text = p.read_text(encoding="utf-8")
        if p.name == "atlas_id_translations.json":
            for old, rec in (json.loads(text).get("translations") or {}).items():
                add(rec["to"], f"mappings/{p.name}:translations[{old}].to")
            continue
        if p.name in SKIP_MAPPINGS:
            continue
        for m in atlas_pin.ATLAS_ID_RE.finditer(text):
            add(m.group(0), f"mappings/{p.name}")
    return found


def pin_integrity(root: Path, pin: dict) -> list[str]:
    problems: list[str] = []
    prov_path = root / "ingest" / "atlas" / "ATLAS.provenance.json"
    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
        snap = root / "ingest" / "atlas" / prov["file"]
        raw = snap.read_bytes()
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        return [f"pin integrity: cannot read committed snapshot/provenance ({exc})"]
    if hashlib.sha256(raw).hexdigest() != prov.get("sha256"):
        problems.append(f"pin integrity: sha256 of {snap.name} != ATLAS.provenance.json sha256")
    release = atlas_pin._yaml_load(raw.decode("utf-8"))
    ver = str(release["collection"]["version"])
    if pin.get("version") != ver:
        problems.append(f"pin integrity: pin version {pin.get('version')!r} != snapshot collection.version {ver!r}")
    rebuilt = atlas_pin.build_pin(release, pin, ver)
    if json.dumps(rebuilt, sort_keys=True) != json.dumps(pin, sort_keys=True):
        problems.append("pin integrity: mappings/mitre_atlas.json is not what scripts/atlas_pin.py "
                        "derives from the committed snapshot (hand-edited, or snapshot/pin out of sync)")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=atlas_pin.ROOT)
    ap.add_argument("--skip-pin-integrity", action="store_true",
                    help="skip check 3 (tests that plant ids in a scratch copy without a snapshot)")
    a = ap.parse_args(argv)
    try:
        pin = atlas_pin.load_pin(a.root / "mappings" / "mitre_atlas.json")
        found = collect_ids(a.root)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"[lint-atlas] CANNOT RUN: {exc}", file=sys.stderr)
        return 2
    bad = atlas_pin.lint_ids(pin, set(found))
    problems = [f"{i}: {why} (at {', '.join(found[i][:3])}{' ...' if len(found[i]) > 3 else ''}; "
                f"{len(found[i])} occurrence(s))" for i, why in bad]
    if not a.skip_pin_integrity:
        problems += pin_integrity(a.root, pin)
    if problems:
        print(f"[lint-atlas] FAIL: {len(problems)} problem(s) against pinned ATLAS {pin.get('version')}:")
        for p in problems:
            print("  - " + p)
        return 1
    print(f"[lint-atlas] OK: {len(found)} distinct AML.* ids checked against pinned ATLAS "
          f"{pin.get('version')}; none absent or deprecated; pin matches committed snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
