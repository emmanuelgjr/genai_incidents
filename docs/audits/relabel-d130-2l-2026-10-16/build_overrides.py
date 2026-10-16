#!/usr/bin/env python
"""Write the D130-2L label overrides into data/curation_overrides.json (ruling D139(c)).

  python docs/audits/relabel-d130-2l-2026-10-16/build_overrides.py           # (re)write; idempotent
  python docs/audits/relabel-d130-2l-2026-10-16/build_overrides.py --check   # exit 1 if the file would change
  python docs/audits/relabel-d130-2l-2026-10-16/build_overrides.py --table   # print the per-row/per-field table
  python docs/audits/relabel-d130-2l-2026-10-16/build_overrides.py --control # control only (see below)

Offline and deterministic: reads BASE (05ff1e75) data/incidents.json + data/curation_overrides.json via git,
legacy/*.{json,md} and ingest/*.json from the tree. No network, no model calls.

Method. For each row the label fields are recomputed by re-running the build's own label code on the row's
contributing sources: scripts/parse_existing.py (OWASP split, derive_atlas_and_nist incl. the attack-vector
hint), scripts/merge_and_dedupe.py (normalize_entry, fill_taxonomy, merge_into's union + max severity,
classify_attack_vector, seed_frameworks_from_vector). relabel_spec.py declares which sources/codes are dropped
and why. CONTROL: the same computation with nothing dropped and the seeds' original attack_vector text must
reproduce BASE's owasp_*/nist/atlas/tactics/severity/tags for all 11 rows -- otherwise the recomputation is not
the build's and the script aborts. Only fields whose recomputed value differs from BASE are written.
"""
import copy, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "scripts"))
import relabel_spec as S  # noqa: E402
import parse_existing as P  # noqa: E402
import merge_and_dedupe as M  # noqa: E402

OV = REPO / "data" / "curation_overrides.json"
FRAMEWORK = ("owasp_llm", "owasp_asi", "owasp_dsgai", "nist_ai_rmf", "mitre_atlas", "mitre_atlas_tactics")
FIELDS = ("category", "attack_vector", "severity") + FRAMEWORK + ("tags", "maestro_layers")


def git_json(path):
    raw = subprocess.run(["git", "show", f"{S.BASE}:{path}"], cwd=REPO, check=True, capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def base_rows():
    return {e["id"]: e for e in git_json("data/incidents.json")["incidents"]}


def legacy_sources():
    """sid -> (raw legacy/incidents.json entry or None, parse_existing output entry), as the build sees them."""
    raw_json = {e["id"]: e for e in json.loads((REPO / "legacy" / "incidents.json").read_text(encoding="utf-8"))["incidents"]}
    out, nid = {}, 1
    entries, nid = P.parse_json_source(REPO / "legacy" / "incidents.json", nid)
    for e in entries:
        out[e["source_ids"][0]] = (raw_json[e["source_ids"][0]], e, len(out))
    for md in ("ASI_Agentic_Exploits_Incidents.md", "additional-exploits-incidents.md"):
        entries, nid = P.parse_md_table(REPO / "legacy" / md, nid)
        for e in entries:
            sid = (e.get("source_ids") or [f"LEGACY-{e['id']}"])[0]
            e["source_ids"] = [sid]
            out[sid] = (None, e, len(out))
    return out


def ingest_sources(wanted):
    out = {}
    for src in sorted((REPO / "ingest").glob("*.json")):
        for r in M.load_source(src):
            n = M.normalize_entry(r)
            if n and set(n["source_ids"]) & wanted:
                for s in set(n["source_ids"]) & wanted:
                    out.setdefault(s, []).append((src.name, n))
    return out


def av_hint_key(raw_av):
    """parse_existing.parse_json_source's attack_vector -> hint-key step, verbatim logic."""
    av_lower = raw_av.lower()
    for k in P.ATTACK_VECTOR_HINTS:
        if k in av_lower:
            return k
    return av_lower.split("—")[0].split("-")[0].strip().split()[0] if av_lower else ""


def legacy_entry(sid, raw, parsed, drop_codes, suppress_hint):
    """A legacy-json seed re-parsed with `drop_codes` removed from owasp_entries; md seeds pass through."""
    e = copy.deepcopy(parsed)
    if raw is not None:
        codes = [c for c in raw.get("owasp_entries", []) if c.strip().upper() not in drop_codes]
        llm, asi, dsgai = P.normalize_owasp(codes)
        hint = "" if suppress_hint else av_hint_key(raw.get("attack_vector", ""))
        atlas, nist = P.derive_atlas_and_nist(llm, asi, hint)
        e.update(owasp_llm=llm, owasp_asi=asi, owasp_dsgai=dsgai, nist_ai_rmf=nist, mitre_atlas=atlas)
    M.fill_taxonomy(e)  # merge main() step 1, legacy path
    return e


def compute(rid, row, spec, legacy, ingest, control):
    """Recompute the label fields of one row from its contributing sources."""
    srcs, later = [], []  # build order: legacy (json, then md) first, then ingest/*.json sorted
    for sid in sorted(row["source_ids"], key=lambda s: legacy[s][2] if s in legacy else 10**6):
        if not control and sid in spec["drop_sources"]:
            continue
        if sid in legacy:
            raw, parsed, _ = legacy[sid]
            drop = set() if control else set(spec["drop_codes"].get(sid, {}))
            srcs.append(("legacy", sid, legacy_entry(sid, raw, parsed, drop, (not control) and sid in S.HINT_ARTIFACT)))
        for fname, n in ingest.get(sid, []):
            later.append((fname, sid, copy.deepcopy(n)))
    srcs += sorted(later, key=lambda x: x[0])
    assert srcs and srcs[0][0] == "legacy", (rid, [s[:2] for s in srcs])
    target = srcs[0][2]
    for _, _, e in srcs[1:]:
        M.merge_into(target, e)
    target["severity"] = M._normalise_severity(target.get("severity"))
    if control:
        vec = (target.get("attack_vector") or "other").lower().strip()
        vec = M._ATTACK_VECTOR_NORMALIZE.get(vec, vec)
        if not vec or vec == "other":
            vec = M.classify_attack_vector((target.get("title") or "") + " " + (target.get("description") or "")) or "other"
    else:
        vec = M.classify_attack_vector(row["title"] + " " + row["description"]) or "other"
        if spec.get("vector"):
            vec = spec["vector"][0]
    target["attack_vector"] = vec
    M.seed_frameworks_from_vector(target)
    M.fill_taxonomy(target)
    return target, srcs


def norm(v):
    return v if v is not None else []


def derive(control=False):
    rows, legacy = base_rows(), legacy_sources()
    wanted = {s for rid in S.ROWS for s in rows[rid]["source_ids"]}
    ingest = ingest_sources(wanted)
    result = {}
    for rid, spec in S.ROWS.items():
        row = rows[rid]
        assert spec["key"] in row["source_ids"], (rid, spec["key"])
        t, srcs = compute(rid, row, spec, legacy, ingest, control)
        if control:
            bad = {f: (norm(row.get(f)), norm(t.get(f))) for f in FRAMEWORK + ("severity", "attack_vector")
                   if sorted(norm(row.get(f))) != sorted(norm(t.get(f))) and not (f in ("severity", "attack_vector") and row.get(f) == t.get(f))}
            if sorted(row["tags"]) != sorted(t.get("tags") or []):
                bad["tags"] = (row["tags"], t.get("tags"))
            result[rid] = bad
            continue
        new, why = {}, {}
        new["attack_vector"] = t["attack_vector"]
        rule_hit = M.classify_attack_vector(row["title"] + " " + row["description"])
        why["attack_vector"] = spec["vector"][1] if spec.get("vector") else (
            f"rule: classify_attack_vector(new title + description) -> {rule_hit or 'no hit -> other'}")
        new["severity"] = t["severity"]
        why["severity"] = "rule: merge_into max-severity over the kept sources (" + ", ".join(
            f"{sid} {e.get('severity')}" for _, sid, e in srcs) + ")"
        new["category"] = spec["category"][0] if spec.get("category") else row["category"]
        why["category"] = spec["category"][1] if spec.get("category") else "unchanged"
        for f in FRAMEWORK:
            new[f] = sorted(set(norm(t.get(f))))
        fw_why = ["rule: parse_existing + fill_taxonomy + seed_frameworks_from_vector re-run on the kept sources"]
        for sid, r in spec["drop_sources"].items():
            fw_why.append(f"provenance: {sid} dropped ({r})")
        for sid, codes in spec["drop_codes"].items():
            for c, r in codes.items():
                fw_why.append(f"{c} dropped ({r})")
        for sid in row["source_ids"]:
            if sid in S.HINT_ARTIFACT:
                fw_why.append(f"{sid}: attack-vector hint suppressed: {S.HINT_ARTIFACT[sid]}")
        for f in FRAMEWORK:
            why[f] = "; ".join(fw_why)
        # tags: removal only, base order kept
        kept_tags = {tg for _, sid, e in srcs for tg in (e.get("tags") or [])}
        dropped_tags = {tg for sid in spec["drop_sources"] for tg in (legacy[sid][1].get("tags") or [])}
        prov = [tg for tg in row["tags"] if tg in dropped_tags and tg not in kept_tags]
        for tg, r in spec["tags_remove"].items():
            assert tg in row["tags"] and tg in kept_tags, (rid, tg, "not a kept-source tag on the base row")
        removed_t = {tg: f"provenance: only in dropped seed {', '.join(spec['drop_sources'])}" for tg in prov}
        removed_t.update(spec["tags_remove"])
        new["tags"] = [tg for tg in row["tags"] if tg not in removed_t]
        why["tags"] = "; ".join(f"-{tg}: {r}" for tg, r in removed_t.items()) or "unchanged"
        # maestro_layers: removal only, by (layer, role)
        ml = row.get("maestro_layers") or []
        for k in spec["maestro_remove"]:
            assert sum((m["layer"], m.get("role")) == k for m in ml) == 1, (rid, k)
        new["maestro_layers"] = [m for m in ml if (m["layer"], m.get("role")) not in spec["maestro_remove"]]
        why["maestro_layers"] = "; ".join(f"-{l}/{ro}: {r}" for (l, ro), r in spec["maestro_remove"].items()) or "unchanged"
        before = {f: (norm(row.get(f)) if f not in ("category", "attack_vector", "severity") else row.get(f)) for f in FIELDS}
        changed = {f for f in FIELDS if (sorted(map(json.dumps, before[f])) if isinstance(before[f], list) else before[f])
                   != (sorted(map(json.dumps, new[f])) if isinstance(new[f], list) else new[f])}
        result[rid] = {"key": spec["key"], "before": before, "after": new, "why": why, "changed": sorted(changed)}
    return result


def build():
    res = derive()
    doc = git_json("data/curation_overrides.json")
    ov = doc["overrides"]
    for rid, r in res.items():
        entry = dict(ov[r["key"]])
        assert not any(f in entry for f in FIELDS), (rid, "base override already sets a label field")
        for f in FIELDS:
            if f in r["changed"]:
                entry[f] = r["after"][f]
        if r["changed"]:
            groups = {}  # identical reasons are stated once, naming every field they cover
            for f in r["changed"]:
                groups.setdefault(r["why"][f], []).append(f)
            entry["_d130_2l_note"] = (S.NOTE_PREFIX + " Fields set: " + ", ".join(r["changed"]) + ". " +
                                      " | ".join(f"{'/'.join(fs)}: {w}" for w, fs in groups.items()))
        ov[r["key"]] = entry
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def table():
    res = derive()
    out = []
    for rid, r in res.items():
        out.append(f"\n### {rid} (override key `{r['key']}`)\n")
        out.append("| field | before | after | reason |\n|---|---|---|---|")
        for f in FIELDS:
            b, a = r["before"][f], r["after"][f]
            if f not in r["changed"]:
                out.append(f"| `{f}` | unchanged | | |")
                continue
            if f == "maestro_layers":
                fmt = lambda v: ", ".join(f"{m['layer']}/{m.get('role')}" for m in v) or "[]"
                b, a = fmt(b), fmt(a)
            elif isinstance(b, list):
                rm, ad = [x for x in b if x not in a], [x for x in a if x not in b]
                b = ", ".join(b) or "[]"
                a = (", ".join(a) or "[]") + f" (-{len(rm)}: {', '.join(rm) or 'none'}; +{len(ad)}: {', '.join(ad) or 'none'})"
            out.append(f"| `{f}` | {b} | {a} | {r['why'][f].replace('|', '/')} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ctl = derive(control=True)
    bad = {k: v for k, v in ctl.items() if v}
    if bad:
        print("[control] FAILED: recomputation does not reproduce BASE:", json.dumps(bad, indent=1, ensure_ascii=False))
        sys.exit(2)
    print(f"[control] OK: recomputation with nothing dropped reproduces BASE labels on all {len(ctl)} rows", file=sys.stderr)
    if "--control" in sys.argv:
        sys.exit(0)
    if "--table" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        print(table())
        sys.exit(0)
    out = build()
    cur = OV.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        print("up to date" if cur == out else "WOULD CHANGE")
        sys.exit(0 if cur == out else 1)
    OV.write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {OV}")
