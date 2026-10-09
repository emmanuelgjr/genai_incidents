"""Field-level before/after delta for the v2.13.0 rejected/disputed CVE sweep
(working agreement 2). Every changed field on every entry is enumerated and
judged against an expectation derived INDEPENDENTLY of the merge rule: plain
set logic over the BEFORE entries and the committed CVE-state snapshot, not
``merge_and_dedupe._apply_cve_rejections``. A delta outside the expectation is
a DEFECT, not noise.

Differs from ``rejected_cve_delta.py`` (the WS4-T2 record, kept as is) in that
the BEFORE data already carries the 29 retractions, so an entry already in its
expected state is "steady" and may change only ``status_reason.as_of``, and
that ``disputed`` entries are expected to lose exactly one confidence level.

    python scripts/audit/cve_sweep_delta.py --before-ref origin/main \
        --out-json docs/audits/cve-sweep/delta-2026-10-09.json \
        --out-md docs/audits/cve-sweep/delta-2026-10-09.md

``compute(before, after, rejected, disputed)`` is pure and tested, including
against corrupted input, in tests/test_cve_sweep_delta.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRANSITION_ALLOWED = {"status", "status_reason", "rejected_cve_ids", "updated", "last_seen", "confidence"}
HEADER_ALLOWED = {"generated", "incident_count", "retracted_count"}
DOWN = {"high": "medium", "medium": "low", "low": "low"}


def expected_marker(e: dict, rejected: set[str], disputed: set[str]) -> dict:
    """Expected (status, rejected_cve_ids, code) for a BEFORE entry by set logic."""
    cves = set(e.get("cve_ids") or [])
    sources = set(e.get("source_ids") or [])
    rej_hit = sorted(cves & rejected)
    out = {"status": None, "rejected_cve_ids": rej_hit or None, "code": None}
    if rej_hit and cves <= rejected and sources <= rejected:
        out.update(status="retracted", code="cve-rejected")
        return out
    standing = rejected | disputed
    if cves & disputed and cves <= standing and sources <= standing:
        out.update(status="disputed", code="cve-disputed")
    return out


def _marker(e: dict) -> tuple:
    return (e.get("status"), (e.get("status_reason") or {}).get("code"),
            tuple(e.get("rejected_cve_ids") or ()))


def expected_review_by_marker(e: dict, registry_sources: dict) -> dict | None:
    """Expected AFTER ``source_freshness`` for a BEFORE entry when the only
    intended freshness change is the v2.13.0 (D57) ``review_by`` addition: the
    BEFORE marker unchanged, plus ``review_by`` = earliest ``hold.until`` of its
    listed sources in the given registry. Set logic over the BEFORE row and the
    registry file, not the merge code path."""
    m = e.get("source_freshness")
    if not m:
        return None
    m = {k: v for k, v in m.items() if k != "review_by"}
    untils = [((registry_sources.get(k) or {}).get("hold") or {}).get("until") for k in m.get("sources") or []]
    untils = [u for u in untils if u]
    if untils:
        m["review_by"] = min(untils)
    return m


def compute(before: dict, after: dict, rejected: set[str], disputed: set[str],
            freshness_registry: dict | None = None) -> dict:
    """``freshness_registry`` (optional, the ``sources`` object of
    data/source_freshness.json): declares the D57 ``review_by`` propagation an
    intended delta. A ``source_freshness`` change equal to
    :func:`expected_review_by_marker` is then classed ``freshness_review_by``
    and allowed on any entry; any other ``source_freshness`` change, or an
    expected one that did not happen, is a defect. Omitted: any
    ``source_freshness`` change is a defect, as before."""
    b = {e["id"]: e for e in before["incidents"]}
    a = {e["id"]: e for e in after["incidents"]}
    out: dict = {"defects": [], "entries": {}, "id_set": {}, "header": {}, "classes": {}}
    out["id_set"] = {"before": len(b), "after": len(a),
                     "added": sorted(set(a) - set(b)), "removed": sorted(set(b) - set(a))}
    for i in out["id_set"]["added"] + out["id_set"]["removed"]:
        out["defects"].append(f"{i}: entry added/removed (nothing may be deleted or minted here)")
    for k in sorted((set(before) | set(after)) - {"incidents"}):
        if before.get(k) != after.get(k):
            out["header"][k] = {"before": before.get(k), "after": after.get(k)}
            if k not in HEADER_ALLOWED:
                out["defects"].append(f"header field {k!r} changed unexpectedly")

    transitions, steady_asof, fresh_rb = [], [], []
    newly = {"retracted": [], "disputed": [], "flag_only": [], "cleared": []}
    for i in sorted(set(b) & set(a)):
        exp = expected_marker(b[i], rejected, disputed)
        want = (exp["status"], exp["code"], tuple(exp["rejected_cve_ids"] or ()))
        is_transition = _marker(b[i]) != want
        changed = {f: {"before": b[i].get(f), "after": a[i].get(f)}
                   for f in sorted(set(b[i]) | set(a[i])) if b[i].get(f) != a[i].get(f)}
        judged = dict(changed)  # the fields the sweep rules below must account for
        if freshness_registry is not None:
            want_fm = expected_review_by_marker(b[i], freshness_registry)
            if a[i].get("source_freshness") != want_fm:
                out["defects"].append(f"{i}: source_freshness {a[i].get('source_freshness')!r} "
                                      f"!= expected {want_fm!r}")
            elif "source_freshness" in changed:
                fresh_rb.append(i)
                judged.pop("source_freshness")
        if is_transition:
            transitions.append(i)
            if exp["status"] == "retracted":
                newly["retracted"].append(i)
            elif exp["status"] == "disputed":
                newly["disputed"].append(i)
            elif exp["rejected_cve_ids"]:
                newly["flag_only"].append(i)
            else:
                newly["cleared"].append(i)
            if _marker(a[i]) != want:
                out["defects"].append(f"{i}: marker after build {_marker(a[i])} != expected {want}")
            extra = set(judged) - TRANSITION_ALLOWED
            if extra:
                out["defects"].append(f"{i}: unexpected field(s) changed {sorted(extra)}")
            conf_b, conf_a = b[i].get("confidence"), a[i].get("confidence")
            if exp["status"] == "disputed":
                if conf_a != DOWN.get(conf_b, conf_b):
                    out["defects"].append(f"{i}: confidence {conf_b!r} -> {conf_a!r}, expected one level down")
            elif "confidence" in changed:
                out["defects"].append(f"{i}: confidence changed without a disputed status")
            if "status_reason" in changed and exp["status"]:
                sr = a[i].get("status_reason") or {}
                if sr.get("code") != exp["code"]:
                    out["defects"].append(f"{i}: status_reason.code {sr.get('code')!r}, expected {exp['code']!r}")
            if not judged:
                out["defects"].append(f"{i}: expected to change but did not")
        else:
            # steady: already in the expected state. Only the re-check date may move.
            extra = {f for f in judged if f != "status_reason"}
            if extra:
                out["defects"].append(f"{i}: steady entry changed {sorted(extra)}")
            if "status_reason" in changed:
                sb, sa = b[i].get("status_reason") or {}, a[i].get("status_reason") or {}
                if {k: v for k, v in sb.items() if k != "as_of"} != {k: v for k, v in sa.items() if k != "as_of"}:
                    out["defects"].append(f"{i}: steady entry's status_reason changed beyond as_of")
                steady_asof.append(i)
        if changed:
            out["entries"][i] = changed
    out["classes"] = {"transitions": transitions, "newly": newly, "steady_as_of_moved": steady_asof,
                      "freshness_review_by_added": fresh_rb}

    n_ret = sum(1 for e in a.values() if e.get("status") == "retracted")
    n_dis = sum(1 for e in a.values() if e.get("status") == "disputed")
    out["counts"] = {
        "entries_before": len(b), "entries_after": len(a),
        "newly_retracted": len(newly["retracted"]), "newly_disputed": len(newly["disputed"]),
        "newly_flag_only": len(newly["flag_only"]), "markers_cleared": len(newly["cleared"]),
        "steady_as_of_moved": len(steady_asof),
        "freshness_review_by_added": len(fresh_rb),
        "retracted_after": n_ret, "disputed_after": n_dis,
        "incident_count_before": before.get("incident_count"), "incident_count_after": after.get("incident_count"),
        "retracted_count_after": after.get("retracted_count"),
        "entries_changed": len(out["entries"]),
        "fields_changed": sum(len(v) for v in out["entries"].values()),
    }
    if after.get("incident_count", 0) + n_ret != len(a):
        out["defects"].append("incident_count + retracted != len(incidents)")
    return out


def entry_hashes(doc: dict) -> dict[str, str]:
    """sha256 of each entry's canonical JSON: a per-entity identity check that
    does not go through ``compute``'s field walk."""
    return {e["id"]: hashlib.sha256(json.dumps(e, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
            for e in doc["incidents"]}


def _git_show(ref: str, path: str) -> dict:
    raw = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def render_md(res: dict, date: str) -> str:
    c, nw = res["counts"], res["classes"]["newly"]
    L = [f"# CVE sweep delta vs main: {date}", "",
         "Generated by `scripts/audit/cve_sweep_delta.py`; twin JSON carries every changed field. "
         "Expectations come from set logic over the BEFORE entries and `ingest/cve_rejections.json`, "
         "not from the merge rule.", "",
         f"- Entries before/after: {c['entries_before']} / {c['entries_after']}; ID set: "
         f"+{len(res['id_set']['added'])} / -{len(res['id_set']['removed'])}",
         f"- Entries changed: {c['entries_changed']}; fields changed: {c['fields_changed']}",
         f"- Newly retracted: {c['newly_retracted']}; newly disputed: {c['newly_disputed']}; "
         f"newly flagged-only: {c['newly_flag_only']}; markers cleared: {c['markers_cleared']}",
         f"- Steady entries whose `status_reason.as_of` moved with the re-check: {c['steady_as_of_moved']}",
         f"- Entries whose `source_freshness` gained the registry-derived `review_by` (D57; judged only "
         f"when `--freshness-registry` is given): {c['freshness_review_by_added']}",
         f"- incident_count {c['incident_count_before']} -> {c['incident_count_after']}; "
         f"retracted_count after {c['retracted_count_after']}; disputed after {c['disputed_after']}",
         f"- Defects: {len(res['defects'])}", ""]
    for d in res["defects"]:
        L.append(f"  - DEFECT: {d}")
    for label in ("retracted", "disputed", "flag_only", "cleared"):
        if nw[label]:
            L += ["", f"## Newly {label}", "", "| entry | field | before | after |", "|---|---|---|---|"]
            for i in nw[label]:
                for f, v in res["entries"].get(i, {}).items():
                    L.append(f"| {i} | {f} | `{json.dumps(v['before'], ensure_ascii=False)}` | "
                             f"`{json.dumps(v['after'], ensure_ascii=False)}` |")
    fr = res["classes"].get("freshness_review_by_added") or []
    if fr:
        pairs: dict[tuple, list] = {}
        for i in fr:
            v = res["entries"][i]["source_freshness"]
            pairs.setdefault((json.dumps(v["before"], sort_keys=True),
                              json.dumps(v["after"], sort_keys=True)), []).append(i)
        L += ["", "## `source_freshness` gained `review_by` (D57)", "",
              "Every distinct before/after value pair, with its entry count and first/last id "
              "(the twin JSON lists every entry).", "",
              "| entries | first | last | before | after |", "|---|---|---|---|---|"]
        for (bv, av), ids in sorted(pairs.items()):
            L.append(f"| {len(ids)} | {ids[0]} | {ids[-1]} | `{bv}` | `{av}` |")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-ref", default="origin/main")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md")
    ap.add_argument("--date", default="")
    ap.add_argument("--after-json", help="data/incidents.json to judge (default: the working tree's); "
                    "used for a scratch build made with the proposed schema edit")
    ap.add_argument("--freshness-registry", help="data/source_freshness.json whose hold.until dates are the "
                    "intended source_freshness.review_by (v2.13.0 D57); omit and any source_freshness change "
                    "is a defect")
    ap.add_argument("--dispute-emission", choices=["auto", "on", "off"], default="auto",
                    help="auto: on iff schema/incident.schema.json lists status_reason code cve-disputed")
    args = ap.parse_args()
    st = json.loads((ROOT / "ingest" / "cve_rejections.json").read_text(encoding="utf-8"))["states"]
    rejected = {c for c, r in st.items() if r["state"] == "REJECTED"}
    disputed = {c for c, r in st.items() if r["state"] == "PUBLISHED" and r.get("disputed")}
    sch = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    schema_ok = "cve-disputed" in sch["properties"]["status_reason"]["properties"]["code"]["enum"]
    emission = schema_ok if args.dispute_emission == "auto" else args.dispute_emission == "on"
    if not emission:
        disputed = set()  # not applied: disputed-CVE entries are expected to stand unmarked
    before = _git_show(args.before_ref, "data/incidents.json")
    after_path = Path(args.after_json) if args.after_json else ROOT / "data" / "incidents.json"
    after = json.loads(after_path.read_text(encoding="utf-8"))
    fr = None
    if args.freshness_registry:
        fr = json.loads(Path(args.freshness_registry).read_text(encoding="utf-8"))["sources"]
    res = compute(before, after, rejected, disputed, fr)
    res["dispute_emission_expected"] = emission
    res["after_source"] = str(after_path.relative_to(ROOT)) if after_path.is_relative_to(ROOT) else "scratch build"

    hb, ha = entry_hashes(before), entry_hashes(after)
    res["per_entity_hash_check"] = {
        "entries_byte_identical": sum(1 for i in hb if ha.get(i) == hb[i]),
        "entries_differing": sorted(i for i in hb if ha.get(i) != hb[i]),
    }
    if set(res["per_entity_hash_check"]["entries_differing"]) != set(res["entries"]):
        res["defects"].append("per-entity hash check and field walk disagree on which entries changed")

    if args.after_json:
        Path(args.out_json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        if args.out_md:
            Path(args.out_md).write_text(render_md(res, args.date), encoding="utf-8", newline="\n")
        print(f"[scratch] entries changed {res['counts']['entries_changed']}, newly disputed "
              f"{res['counts']['newly_disputed']}, defects {len(res['defects'])}")
        for d in res["defects"]:
            print("  DEFECT:", d)
        return 1 if res["defects"] else 0
    sb = _git_show(args.before_ref, "data/stats.json")
    sa = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    res["stats_json"] = {k: {"before": sb.get(k), "after": sa.get(k)}
                         for k in sorted(set(sb) | set(sa)) if sb.get(k) != sa.get(k)}
    mb = _git_show(args.before_ref, "data/incidents.min.json")
    ma = json.loads((ROOT / "data" / "incidents.min.json").read_text(encoding="utf-8"))
    res["min_json_id_set_equal"] = {e["id"] for e in mb["incidents"]} == {e["id"] for e in ma["incidents"]}
    db = _git_show(args.before_ref, "data/id_deprecations.json")
    da = json.loads((ROOT / "data" / "id_deprecations.json").read_text(encoding="utf-8"))
    res["id_deprecations_unchanged"] = db == da
    if not res["min_json_id_set_equal"]:
        res["defects"].append("incidents.min.json id set changed")
    if not res["id_deprecations_unchanged"]:
        res["defects"].append("id_deprecations.json changed (no ID is retired or minted here)")
    Path(args.out_json).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.out_md:
        Path(args.out_md).write_text(render_md(res, args.date), encoding="utf-8", newline="\n")
    c = res["counts"]
    print(f"entries changed {c['entries_changed']}, fields changed {c['fields_changed']}, "
          f"newly retracted {c['newly_retracted']}, newly disputed {c['newly_disputed']}, "
          f"defects {len(res['defects'])}")
    for d in res["defects"]:
        print("  DEFECT:", d)
    return 1 if res["defects"] else 0


if __name__ == "__main__":
    sys.exit(main())
