"""precision_sample.py -- N9 precision audit: stratified, seeded sampler.

Draws the N9 precision-audit sample (v2.13.0 item 5; INCLUSION.md section 4
"sample-audited for relevance"): 100 rows from the FEED tier and 50 from the
LANDMARK tier, and writes the review sheet a human fills in.

Question being measured
-----------------------
Precision = the share of published rows that are genuinely in scope under
INCLUSION.md section 1 (AI-nexus AND security/safety relevance AND evidence).
It is a property of the rows, judged by a human against INCLUSION.md.

Sampling frame (documented in frame.json, re-derivable)
-------------------------------------------------------
* Unit: one row of ``data/incidents.json``.
* Excluded: ``status == "retracted"`` rows (D44: they are not counted in
  ``incident_count`` and leave every feed export; they are not published
  claims of inclusion).
* Two frames, partitioned by ``tier`` -- the derived field of record
  (``merge_and_dedupe._derive_tier``; DATA_DICTIONARY.md): ``feed`` and
  ``landmark``. The user's brief says "auto" for the first frame. ``tier`` is
  used instead of ``quality_tier == "auto"`` because (a) the two
  ``quality_tier``/``tier`` sets overlap (``landmark`` rows can be
  ``quality_tier: auto``), so a ``quality_tier`` frame and a ``tier`` frame
  are not disjoint; and (b) the N9 finding (about 48%, n=40) was measured on
  CVE/GHSA rows that are mostly ``quality_tier: reviewed`` (the NVD/GHSA path
  labels NVD-scored CVEs ``reviewed``), so a ``quality_tier == "auto"`` frame
  would leave most of the N9 population out of the audit. ``quality_tier``
  is kept as an implicit stratifier inside each stratum (below), so the
  sample still spreads over it and per-``quality_tier`` breakdowns can be
  reported.

Strata
------
Explicit: ``tier x source_family``. ``source_family`` is a fixed priority
function of the ``source_ids`` prefixes (``source_family`` below). Families
holding less than ``POOL_BELOW`` (2%) of their tier are pooled into
``<tier>/other`` so no explicit stratum is a near-empty cell.

Implicit: inside each stratum, rows are sorted by
``(quality_tier, year, id)`` and drawn by seeded SYSTEMATIC sampling (random
start, fixed interval). This spreads the sample over quality_tier and year in
proportion to the stratum, without making tier x family x quality_tier x year
explicit cells that 150 draws cannot fill.

Allocation: PROPORTIONAL to stratum population within each tier (largest
remainder rounding). Reasons: the estimands are tier-level and overall
precision; proportional allocation makes each tier's sample (near)
self-weighting and is never less efficient than simple random sampling;
Neyman allocation needs per-stratum variances we do not have (only the
CVE/GHSA one, from n=40); equal allocation would put as many draws in a
small family as in a family 20x its size and widen the tier interval. The
two tiers are sampled at DIFFERENT fractions (100 of the feed, 50 of the
landmark set), so the OVERALL estimate must be weighted back to the
population -- ``scripts/wilson_ci.py`` does that from frame.json.

Determinism
-----------
``random.Random(f"{seed}|{stratum}")`` per stratum (string seeds are hashed
with SHA-512 by CPython's version-2 seeding, stable across platforms and
runs). Inputs are hashed (canonical JSON of the incidents array) into
frame.json, so a re-run against different data is detected, not silently
different. ``--check`` re-derives everything in memory and compares it
byte-for-byte with the committed files.

Raw text
--------
Descriptions are NOT copied into the sample: a reviewer opens the row by id
in ``data/incidents.json`` (the pointer is in every row). Invariant 7 is not
active yet (WS3-T6 not done) but is advisory for new work, the DATASHEET warns
that free text can carry payloads, and OECD/AIAAIC narrative text has its own
licence constraints. Titles, ``affected`` and reference URLs are copied
because a reviewer needs them to find the row and its sources.

Usage
-----
    python scripts/precision_sample.py                    # write sample + frame (+ sheet if absent)
    python scripts/precision_sample.py --check            # byte-for-byte reproduction check
    python scripts/precision_sample.py --seed 7 --out-dir <tmp>   # a different seed
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUDIT_DATE = "2026-10-11"
DEFAULT_OUT_DIR = ROOT / "docs" / "audits" / "precision" / AUDIT_DATE
DEFAULT_SEED = 20261011
ALLOCATION = {"feed": 100, "landmark": 50}
POOL_BELOW = 0.02  # families under 2% of their tier are pooled into <tier>/other
MAX_REFS = 5

SAMPLE_FILE = "sample.json"
FRAME_FILE = "frame.json"
SHEET_FILE = "review_sheet.csv"
SUGGESTIONS_FILE = "agent_suggestions.json"

# Fixed priority: the first family whose prefixes intersect the row's
# source-id prefixes wins. CVE/GHSA first so every row carrying a CVE/GHSA
# record is in the N9 stratum.
FAMILY_PRIORITY: list[tuple[str, tuple[str, ...]]] = [
    ("cve-ghsa", ("CVE", "GHSA", "MAL")),
    ("aiid", ("AIID",)),
    ("oecd", ("OECD",)),
    ("aiaaic", ("AIAAIC",)),
    ("avid", ("AVID",)),
    ("arxiv", ("ARXIV",)),
    ("legacy-curated", ("INC", "LEGACY")),
]

SHEET_COLUMNS = [
    "sheet_row", "id", "tier", "stratum", "quality_tier", "year", "corpus",
    "title", "pointer",
    "suggested_label", "suggested_reason", "suggested_by",
    "human_label", "human_by", "human_note",
]
LABELS = ("in-scope", "out-of-scope", "unsure")


def source_family(entry: dict) -> str:
    prefixes = set()
    for s in entry.get("source_ids") or []:
        m = re.match(r"[A-Z]+", s or "")
        if m:
            prefixes.add(m.group(0))
    for fam, pre in FAMILY_PRIORITY:
        if prefixes & set(pre):
            return fam
    return "other"


def canonical_sha256(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def build_frame(incidents: list[dict]) -> tuple[dict, dict[str, list[dict]]]:
    """-> (frame description, stratum -> sorted member rows)."""
    standing = [e for e in incidents if e.get("status") != "retracted"]
    excluded = len(incidents) - len(standing)
    by_tier: dict[str, list[dict]] = {}
    for e in standing:
        by_tier.setdefault(e.get("tier"), []).append(e)
    unknown = sorted(t for t in by_tier if t not in ALLOCATION)
    if unknown:
        raise SystemExit(f"[precision-sample] rows with unexpected tier values {unknown!r}")

    strata: dict[str, list[dict]] = {}
    for tier in ALLOCATION:
        rows = by_tier.get(tier, [])
        fam_counts: dict[str, int] = {}
        for e in rows:
            fam_counts[source_family(e)] = fam_counts.get(source_family(e), 0) + 1
        pooled = {f for f, c in fam_counts.items() if c < POOL_BELOW * len(rows)}
        for e in rows:
            fam = source_family(e)
            key = f"{tier}/{'other' if fam in pooled else fam}"
            strata.setdefault(key, []).append(e)
    for key in strata:
        strata[key].sort(key=lambda e: (str(e.get("quality_tier")), int(e.get("year") or 0), e["id"]))

    allocation = {}
    for tier, n in ALLOCATION.items():
        keys = sorted(k for k in strata if k.split("/")[0] == tier)
        pop = sum(len(strata[k]) for k in keys)
        quotas = {k: n * len(strata[k]) / pop for k in keys}
        alloc = {k: int(q) for k, q in quotas.items()}
        short = n - sum(alloc.values())
        # largest remainder; ties broken by larger population, then key
        order = sorted(keys, key=lambda k: (-(quotas[k] - alloc[k]), -len(strata[k]), k))
        for k in order[:short]:
            alloc[k] += 1
        allocation.update(alloc)

    def _qt_year(rows):
        qt, yr = {}, {}
        for e in rows:
            qt[str(e.get("quality_tier"))] = qt.get(str(e.get("quality_tier")), 0) + 1
            y = int(e.get("year") or 0)
            band = "<=2022" if y <= 2022 else str(y)
            yr[band] = yr.get(band, 0) + 1
        return dict(sorted(qt.items())), dict(sorted(yr.items()))

    strata_desc = []
    for k in sorted(strata):
        qt, yr = _qt_year(strata[k])
        strata_desc.append({
            "stratum": k,
            "tier": k.split("/")[0],
            "population": len(strata[k]),
            "allocated": allocation[k],
            "population_by_quality_tier": qt,
            "population_by_year_band": yr,
        })
    frame = {
        "unit": "one row of data/incidents.json",
        "exclusions": {"status == retracted": excluded},
        "frame_population": len(standing),
        "tier_population": {t: len(by_tier.get(t, [])) for t in ALLOCATION},
        "tier_allocation": dict(ALLOCATION),
        "explicit_strata": "tier x source_family (families < 2% of their tier pooled into <tier>/other)",
        "implicit_strata": "within a stratum: sorted by (quality_tier, year, id), seeded systematic draw",
        "allocation_rule": "proportional to stratum population within tier, largest-remainder rounding",
        "source_family_priority": [[f, list(p)] for f, p in FAMILY_PRIORITY] + [["other", []]],
        "pool_below_share_of_tier": POOL_BELOW,
        "strata": strata_desc,
    }
    return frame, strata


def systematic_draw(rows: list[dict], n: int, rng: random.Random) -> list[dict]:
    if n <= 0:
        return []
    if n >= len(rows):
        return list(rows)
    step = len(rows) / n
    start = rng.random() * step
    return [rows[int(start + i * step)] for i in range(n)]


def sample_row(e: dict, stratum: str) -> dict:
    refs = [r.get("url") for r in (e.get("references") or []) if r.get("url")]
    return {
        "id": e["id"],
        "stratum": stratum,
        "tier": e.get("tier"),
        "source_family": stratum.split("/")[1],
        "quality_tier": e.get("quality_tier"),
        "corpus": e.get("corpus"),
        "status": e.get("status"),
        "year": e.get("year"),
        "category": e.get("category"),
        "source_ids": e.get("source_ids") or [],
        "title": e.get("title") or "",
        "affected": e.get("affected") or "",
        "reference_urls": refs[:MAX_REFS],
        "reference_count": len(refs),
        "pointer": f"data/incidents.json -> incidents[id == {e['id']}] (description and full record)",
    }


def draw(incidents: list[dict], seed: int) -> tuple[dict, dict]:
    frame, strata = build_frame(incidents)
    alloc = {s["stratum"]: s["allocated"] for s in frame["strata"]}
    rows = []
    for k in sorted(strata):
        rng = random.Random(f"{seed}|{k}")
        rows += [sample_row(e, k) for e in systematic_draw(strata[k], alloc[k], rng)]
    for s in frame["strata"]:
        drawn = [r for r in rows if r["stratum"] == s["stratum"]]
        s["drawn"] = len(drawn)
    frame["seed"] = seed
    frame["rng"] = "random.Random(f'{seed}|{stratum}') per stratum; systematic draw (random start in [0, N/n))"
    frame["data_incidents_sha256"] = canonical_sha256(incidents)
    frame["data_hash_recipe"] = (
        "sha256 of json.dumps(data['incidents'], sort_keys=True, separators=(',',':'), "
        "ensure_ascii=False).encode('utf-8')"
    )
    frame["audit_date"] = AUDIT_DATE
    sample = {
        "$note": ("N9 precision-audit sample. Ids plus reviewer-facing fields; descriptions are "
                  "by pointer to data/incidents.json. Generated by scripts/precision_sample.py; "
                  "never hand-edit -- re-derive with --check."),
        "seed": seed,
        "audit_date": AUDIT_DATE,
        "data_incidents_sha256": frame["data_incidents_sha256"],
        "entries": rows,
    }
    sample["entries_sha256"] = canonical_sha256(rows)
    return frame, sample


def dump_json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def build_sheet(sample: dict, suggestions: dict | None) -> str:
    """The review sheet. suggested_* come ONLY from agent_suggestions.json;
    human_* columns are always written EMPTY by this function."""
    sug = (suggestions or {}).get("suggestions", {})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=SHEET_COLUMNS, lineterminator="\n")
    w.writeheader()
    for i, r in enumerate(sample["entries"], 1):
        s = sug.get(r["id"], {})
        label = s.get("label", "")
        if label and label not in LABELS:
            raise SystemExit(f"[precision-sample] bad suggested label {label!r} for {r['id']}")
        w.writerow({
            "sheet_row": i,
            "id": r["id"],
            "tier": r["tier"],
            "stratum": r["stratum"],
            "quality_tier": r["quality_tier"],
            "year": r["year"],
            "corpus": r["corpus"],
            "title": r["title"],
            "pointer": f"data/incidents.json#{r['id']}",
            "suggested_label": label,
            "suggested_reason": s.get("reason", ""),
            "suggested_by": "agent" if label else "",
            "human_label": "",
            "human_by": "",
            "human_note": "",
        })
    return buf.getvalue()


def sheet_has_human_labels(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8", newline="") as f:
        return any((row.get("human_label") or "").strip() or (row.get("human_by") or "").strip()
                   for row in csv.DictReader(f))


AGENT_SUMMARY_FILE = "agent_suggested_precision.json"


def agent_summary(frame: dict, sample: dict, suggestions: dict) -> dict:
    """Precision implied by the AGENT'S suggested labels -- an estimate of what
    the measurement might show, explicitly NOT the measurement. Uses the same
    stratified estimator as scripts/wilson_ci.py so the two are comparable,
    but lives here so that wilson_ci.py has no code path that reads a
    suggestion."""
    from wilson_ci import _estimate  # noqa: PLC0415 - local import keeps the module standalone

    sug = suggestions["suggestions"]
    pops = {s["stratum"]: s["population"] for s in frame["strata"]}
    rows = [(e["stratum"], sug[e["id"]]["label"]) for e in sample["entries"] if e["id"] in sug]
    out = {
        "$warning": ("AGENT-SUGGESTED, NOT MEASURED. Derived from agent_suggestions.json (suggested_by: agent). "
                     "It is the agent's reading, not a human measurement; do not quote it as the dataset's "
                     "precision. The measured figure comes only from human labels via scripts/wilson_ci.py."),
        "suggested_by": "agent",
        "label_counts": {lab: sum(1 for _, x in rows if x == lab) for lab in LABELS},
        "estimates": {},
    }
    for treatment, strict in (("excluding_unsure", False), ("strict", True)):
        t = {"overall": _estimate(rows, pops, strict)}
        for tier in ALLOCATION:
            tp = {h: p for h, p in pops.items() if h.split("/")[0] == tier}
            t[tier] = _estimate([r for r in rows if r[0] in tp], tp, strict)
        t["per_stratum"] = {h: _estimate([r for r in rows if r[0] == h], {h: pops[h]}, strict)
                            for h in sorted(pops)}
        out["estimates"][treatment] = t
    return out


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", type=Path, default=ROOT / "data" / "incidents.json")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--check", action="store_true",
                    help="re-derive and compare byte-for-byte with the files in --out-dir")
    ap.add_argument("--rebuild-sheet", action="store_true",
                    help="rewrite review_sheet.csv from agent_suggestions.json (refused once any human label exists)")
    a = ap.parse_args(argv)

    data = json.loads(a.data.read_text(encoding="utf-8"))
    frame, sample = draw(data["incidents"], a.seed)
    out = a.out_dir
    sug_path = out / SUGGESTIONS_FILE
    suggestions = json.loads(_read(sug_path)) if sug_path.exists() else None

    produced = {FRAME_FILE: dump_json(frame), SAMPLE_FILE: dump_json(sample)}
    if suggestions is not None:
        if [i for i in suggestions.get("suggestions", {})] != [e["id"] for e in sample["entries"]]:
            print(f"[precision-sample] {SUGGESTIONS_FILE} ids do not match the drawn sample (seed {a.seed}); "
                  "agent summary and sheet not produced from it.")
            suggestions = None
        else:
            produced[AGENT_SUMMARY_FILE] = dump_json(agent_summary(frame, sample, suggestions))

    if a.check:
        committed_frame = out / FRAME_FILE
        if committed_frame.exists():
            pinned = json.loads(_read(committed_frame)).get("data_incidents_sha256")
            if pinned != frame["data_incidents_sha256"]:
                print(f"[precision-sample] --data hashes to {frame['data_incidents_sha256']}, "
                      f"but the sample was drawn from {pinned}. Reproduce against the pinned data, e.g. "
                      "`git show <commit>:data/incidents.json > /tmp/inc.json` and pass --data.")
                return 1
        bad = []
        for name, text in produced.items():
            p = out / name
            if not p.exists() or _read(p) != text:
                bad.append(name)
        sheet = out / SHEET_FILE
        if sheet.exists() and not sheet_has_human_labels(sheet):
            if _read(sheet) != build_sheet(sample, suggestions):
                bad.append(SHEET_FILE)
        if bad:
            print(f"[precision-sample] NOT reproduced: {', '.join(bad)} differ from a fresh draw (seed {a.seed}).")
            return 1
        print(f"[precision-sample] reproduced byte-for-byte: {', '.join(sorted(produced))}"
              f"{' + ' + SHEET_FILE if sheet.exists() and not sheet_has_human_labels(sheet) else ''}"
              f" (seed {a.seed}, entries_sha256 {sample['entries_sha256']}).")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    for name, text in produced.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
    sheet = out / SHEET_FILE
    if not sheet.exists() or a.rebuild_sheet:
        if sheet_has_human_labels(sheet):
            print(f"[precision-sample] refusing to overwrite {sheet}: it carries human labels.")
            return 1
        sheet.write_text(build_sheet(sample, suggestions), encoding="utf-8", newline="\n")
    print(f"[precision-sample] seed {a.seed}: {len(sample['entries'])} rows -> {out} "
          f"(entries_sha256 {sample['entries_sha256']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
