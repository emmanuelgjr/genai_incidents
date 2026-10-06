"""scripts/atlas_pin.py -- OFFLINE tooling for the pinned MITRE ATLAS release.

Everything here reads committed files only. Nothing in this module touches the
network (the one network step is ``scripts/fetch_atlas.py``, which goes through
``ingest/common.py``), so it is safe to import from the deterministic build path
and from tests.

Three jobs:

``build_pin(release, prior_pin, version)``
    Derive ``mappings/mitre_atlas.json`` from an ATLAS dist YAML (format 6.x,
    ``mitre-atlas/atlas-data``). Tactic names, technique names and the
    technique->tactic links (``achieves`` relationships on top-level
    techniques; subtechniques inherit their parent's, the pre-existing pin
    convention) come from the YAML. Ids that the previous pin knew and the new
    release no longer carries are RETAINED and marked ``"deprecated"`` -- never
    deleted -- because corpus entries may still reference them until the
    mechanical translation in ``mappings/atlas_id_translations.json`` has been
    applied.

``diff_pins(old, new)``
    Added / removed(deprecated) / renamed technique and tactic ids plus changed
    technique->tactic links, for the refresh PR's diff report.

``lint_ids(pin, ids)``
    The rule behind ``scripts/lint_atlas_ids.py``: an ``AML.*`` id is a
    violation if it is ABSENT from the pin or DEPRECATED in it.

CLI::

    python scripts/atlas_pin.py build  [--yaml PATH] [--write]
    python scripts/atlas_pin.py diff   [--yaml PATH]
    python scripts/atlas_pin.py scan   [--yaml PATH]   # suspicious-content counts, rc=1 if any
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "mappings"
PIN_PATH = MAPPINGS / "mitre_atlas.json"
TRANSLATIONS_PATH = MAPPINGS / "atlas_id_translations.json"
SNAPSHOT_DIR = ROOT / "ingest" / "atlas"
PROVENANCE_PATH = SNAPSHOT_DIR / "ATLAS.provenance.json"

# Retired upstream before 2026.06; the 2026.06 pin kept them without a marker
# (verified: absent from dist/v6/ATLAS-2026.06.yaml, 2026-10-06).
RETIRED_BEFORE_2026_06 = frozenset({"AML.T0009", "AML.T0030", "AML.T0038", "AML.T0045"})

ATLAS_ID_RE = re.compile(r"\bAML\.(?:TA\d{4}|T\d{4}(?:\.\d{3})?)\b")


def _yaml_load(text: str) -> dict:
    import yaml  # PyYAML (requirements.txt); imported lazily so lint stays light

    return yaml.safe_load(text)


def load_release(path: Path) -> dict:
    root = _yaml_load(path.read_text(encoding="utf-8"))
    if not isinstance(root, dict) or "techniques" not in root or "tactics" not in root:
        raise ValueError(f"{path}: not an ATLAS dist release (no techniques/tactics)")
    return root


def load_pin(path: Path = PIN_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_path() -> Path:
    """The committed raw release YAML named by ingest/atlas/ATLAS.provenance.json."""
    prov = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    return SNAPSHOT_DIR / prov["file"]


def _tactic_links(release: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    rels = release.get("relationships") or {}
    for tid in release["techniques"]:
        ach = (rels.get(tid) or {}).get("achieves") or []
        tacs = sorted({a["target"] for a in ach if str(a.get("target", "")).startswith("AML.TA")})
        if tacs:
            out[tid] = tacs
    return out


_SAFE_NAME_RE = re.compile(r"^[^<>`\x00-\x1f]{1,200}$")
_ID_RE = re.compile(r"^AML\.(?:TA\d{4}|T\d{4}(?:\.\d{3})?)$")


def _check_release_shape(release: dict) -> None:
    """Refresh-PR poisoning guard: ids must be well-formed and names plain text.
    Names flow into the pin and from there into STIX attack-pattern names, MISP
    and the site; markup, backticks or control characters in a name is not an
    ATLAS rename, it is a defect (or an attack) -- fail the build loudly."""
    for kind, table in (("tactic", release["tactics"]), ("technique", release["techniques"])):
        for tid, rec in table.items():
            if not _ID_RE.match(str(tid)):
                raise ValueError(f"{kind} id {tid!r} is not a well-formed ATLAS id")
            name = rec.get("name") if isinstance(rec, dict) else None
            if not isinstance(name, str) or not _SAFE_NAME_RE.match(name):
                raise ValueError(f"{kind} {tid}: name {name!r} is empty/non-text/contains markup or control chars")


SUSPICIOUS_PATTERNS = {
    "script tag": re.compile(r"<\s*script", re.I),
    "javascript: URI": re.compile(r"javascript\s*:", re.I),
    "data: URI": re.compile(r"\bdata:[a-z]+/[a-z0-9.+-]+[;,]", re.I),
    "inline event handler": re.compile(r"\bon[a-z]{3,12}\s*=\s*[\"']", re.I),
    "iframe/object/embed": re.compile(r"<\s*(iframe|object|embed)\b", re.I),
}


def scan_suspicious(raw_text: str) -> dict[str, int]:
    """Counts of suspicious-content patterns in the raw release text (informational,
    for the refresh PR body; the hard gate is _check_release_shape)."""
    return {k: len(rx.findall(raw_text)) for k, rx in SUSPICIOUS_PATTERNS.items()}


def build_pin(release: dict, prior_pin: dict | None, version: str | None = None) -> dict:
    """Derive the pin dict from a release YAML (see module docstring)."""
    _check_release_shape(release)
    version = version or str(release["collection"]["version"])
    prior_pin = prior_pin or {}
    prior_tech = prior_pin.get("techniques") or {}
    links = _tactic_links(release)

    tactics = {tid: {"name": t["name"]} for tid, t in sorted(release["tactics"].items())}
    techniques: dict[str, dict] = {}
    for tid, t in sorted(release["techniques"].items()):
        rec: dict = {"name": t["name"]}
        # Subtechniques (AML.Txxxx.yyy) inherit the parent's tactics and carry
        # none themselves -- the convention the merge step already relies on.
        if tid.count(".") == 1 and tid in links:
            rec["tactics"] = links[tid]
        techniques[tid] = rec

    # Retained-but-deprecated: known to the previous pin, gone from this release.
    for tid, rec in sorted(prior_tech.items()):
        if tid in techniques:
            continue
        kept = dict(rec)
        prev_dep = rec.get("deprecated")
        if prev_dep:
            kept["deprecated"] = prev_dep
        elif tid in RETIRED_BEFORE_2026_06:
            kept["deprecated"] = {"since": "<=2026.06",
                                  "note": "absent from ATLAS 2026.06 and later (the 2026.06 pin "
                                          "retained it unmarked)"}
        else:
            kept["deprecated"] = {
                "since": version,
                "note": f"absent from ATLAS {version}; retained so entries that still "
                        "reference it resolve, until translated "
                        "(mappings/atlas_id_translations.json)",
            }
        techniques[tid] = kept

    coll = release["collection"]
    return {
        "framework": prior_pin.get("framework", "MITRE ATLAS (Adversarial Threat Landscape for AI Systems)"),
        "version": version,
        "release_date": str(coll.get("modified-date", "")),
        "url": prior_pin.get("url", "https://atlas.mitre.org/"),
        "tactics": dict(sorted(tactics.items())),
        "techniques": dict(sorted(techniques.items())),
        "case_studies_url": prior_pin.get("case_studies_url", "https://atlas.mitre.org/studies"),
        "note": (
            f"Technique list is current as of MITRE ATLAS v{version} "
            f"(mitre-atlas/atlas-data dist/v6/ATLAS-{version}.yaml, committed verbatim under "
            "ingest/atlas/ with a sha256 in ingest/atlas/ATLAS.provenance.json); "
            "subtechniques use the .NNN suffix. Derived by scripts/atlas_pin.py -- do not "
            "hand-edit. Ids absent from the release are RETAINED with a `deprecated` marker "
            "(never deleted); scripts/lint_atlas_ids.py fails on any corpus/mapping id that is "
            "absent from or deprecated in this pin. Mechanical id translations for superseded "
            "ids live in mappings/atlas_id_translations.json."
        ),
        "technique_tactics_note": (
            "Each top-level technique entry carries its ATLAS tactic id(s) under `tactics` "
            "(the release's `achieves` relationships); subtechniques inherit the parent's."
        ),
        "atlas_data_version": version,
    }


def diff_pins(old: dict, new: dict) -> dict:
    """Structured diff between two pins (live ids only; deprecated == removed)."""
    def live(p: dict) -> dict:
        # The 2026.06 pin retained four long-retired ids without a marker; they
        # were not live in 2026.06 and must not read as "removed in this refresh".
        return {k: v for k, v in (p.get("techniques") or {}).items()
                if not v.get("deprecated") and k not in RETIRED_BEFORE_2026_06}

    ot, nt = live(old), live(new)
    otac, ntac = old.get("tactics") or {}, new.get("tactics") or {}
    d = {
        "old_version": old.get("version"), "new_version": new.get("version"),
        "techniques_added": sorted(set(nt) - set(ot)),
        "techniques_removed": sorted(set(ot) - set(nt)),
        "techniques_renamed": [(k, ot[k]["name"], nt[k]["name"]) for k in sorted(set(ot) & set(nt))
                               if ot[k]["name"] != nt[k]["name"]],
        "technique_tactic_links_changed": [
            (k, ot[k].get("tactics"), nt[k].get("tactics")) for k in sorted(set(ot) & set(nt))
            if ot[k].get("tactics") != nt[k].get("tactics")],
        "tactics_added": sorted(set(ntac) - set(otac)),
        "tactics_removed": sorted(set(otac) - set(ntac)),
        "tactics_renamed": [(k, otac[k]["name"], ntac[k]["name"]) for k in sorted(set(otac) & set(ntac))
                            if otac[k]["name"] != ntac[k]["name"]],
    }
    d["names"] = {k: (nt.get(k) or ot.get(k) or {}).get("name", "") for k in
                  d["techniques_added"] + d["techniques_removed"]}
    return d


def render_diff_md(d: dict) -> str:
    def row(k: str) -> str:
        return f"| `{k}` | {d['names'].get(k, '')} |"

    lines = [f"## Release diff: ATLAS {d['old_version']} -> {d['new_version']}", ""]
    lines += [f"### Techniques added ({len(d['techniques_added'])})", "", "| id | name |", "|---|---|"]
    lines += [row(k) for k in d["techniques_added"]] or ["| (none) | |"]
    lines += ["", f"### Techniques removed / deprecated ({len(d['techniques_removed'])})", "",
              "| id | name (in old release) |", "|---|---|"]
    lines += [row(k) for k in d["techniques_removed"]] or ["| (none) | |"]
    lines += ["", f"### Techniques renamed ({len(d['techniques_renamed'])})", "",
              "| id | old name | new name |", "|---|---|---|"]
    lines += [f"| `{k}` | {a} | {b} |" for k, a, b in d["techniques_renamed"]] or ["| (none) | | |"]
    lines += ["", f"### Technique -> tactic links changed ({len(d['technique_tactic_links_changed'])})", "",
              "| id | old tactics | new tactics |", "|---|---|---|"]
    lines += [f"| `{k}` | {a} | {b} |" for k, a, b in d["technique_tactic_links_changed"]] or ["| (none) | | |"]
    lines += ["", "### Tactics", "",
              f"- added: {d['tactics_added'] or 'none'}",
              f"- removed / deprecated: {d['tactics_removed'] or 'none'}",
              "- renamed: " + ("; ".join(f"`{k}` {a!r} -> {b!r}" for k, a, b in d["tactics_renamed"])
                              or "none"), ""]
    return "\n".join(lines)


def load_translations(path: Path = TRANSLATIONS_PATH) -> dict[str, str]:
    """old id -> replacement id (single, mechanical). Missing file -> {}."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return {k: v["to"] for k, v in (raw.get("translations") or {}).items()}


def lint_ids(pin: dict, ids: set[str]) -> list[tuple[str, str]]:
    """(id, reason) for every id that is absent from or deprecated in ``pin``."""
    tech, tac = pin.get("techniques") or {}, pin.get("tactics") or {}
    bad: list[tuple[str, str]] = []
    for i in sorted(ids):
        known = tac if i.startswith("AML.TA") else tech
        if i not in known:
            bad.append((i, f"absent from pinned ATLAS {pin.get('version')}"))
        elif known[i].get("deprecated"):
            bad.append((i, f"deprecated in pinned ATLAS {pin.get('version')}"))
    return bad


def _main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["build", "diff", "scan"])
    ap.add_argument("--yaml", type=Path, default=None, help="release YAML (default: committed snapshot)")
    ap.add_argument("--write", action="store_true", help="build: write mappings/mitre_atlas.json")
    ap.add_argument("--report", type=Path, default=None, help="write the diff report markdown here")
    ap.add_argument("--prior", type=Path, default=None,
                    help="previous pin to diff against (default: the committed mappings/mitre_atlas.json)")
    a = ap.parse_args()
    if a.cmd == "scan":
        counts = scan_suspicious((a.yaml or snapshot_path()).read_text(encoding="utf-8"))
        print(json.dumps(counts))
        return 1 if any(counts.values()) else 0
    release = load_release(a.yaml or snapshot_path())
    prior = load_pin(a.prior) if a.prior else load_pin()
    new = build_pin(release, prior)
    d = diff_pins(prior, new)
    md = render_diff_md(d)
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(md, encoding="utf-8", newline="\n")
    if a.cmd == "diff" or not a.write:
        sys.stdout.buffer.write((md + "\n").encode("utf-8"))
    if a.cmd == "build" and a.write:
        PIN_PATH.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8", newline="\n")
        print(f"[atlas-pin] wrote {PIN_PATH.relative_to(ROOT)} (version {new['version']}, "
              f"{len(new['techniques'])} techniques incl. deprecated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
