"""AIID corpus-classifier audit (label-scientist, 2026-11-24).

Evidence script for docs/audits/aiid-corpus-classifier-2026-11-24.md. Read-only
against data/ except `dryrun`, which builds inside a throw-away detached git
worktree under --scratch and removes it afterwards. No network, no model calls.

    python scripts/audit/aiid_corpus_audit.py flip      [--before 6a4d8261 --after 8753a7fe]
    python scripts/audit/aiid_corpus_audit.py paths     [--ref 8753a7fe]
    python scripts/audit/aiid_corpus_audit.py sample    [--ref 8753a7fe --seed 20261124 --out CSV]
    python scripts/audit/aiid_corpus_audit.py score     [--sample CSV --adjudication CSV]
    python scripts/audit/aiid_corpus_audit.py avscan    [--ref 8753a7fe]
    python scripts/audit/aiid_corpus_audit.py apply-o1    (writes the AIID-195 corpus override; then rebuild)
    python scripts/audit/aiid_corpus_audit.py crosscheck  (rule-predicted vs built AIID move sets, per option)
    python scripts/audit/aiid_corpus_audit.py project   (projected error of each option, from the adjudicated sample)
    python scripts/audit/aiid_corpus_audit.py dryrun    --option {O0,O1,O2,O3,O2+O3} --scratch DIR [--ref 8753a7fe] [--json OUT]
    python scripts/audit/aiid_corpus_audit.py flipguard --base REF --head REF [--allow ID,ID] [--head-file PATH]

The corpus classifier is imported from the CURRENT tree's scripts/merge_and_dedupe.py
(unchanged between 6a4d8261 and 8753a7fe: `git diff --stat 6a4d8261 8753a7fe -- scripts/` is empty).
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import merge_and_dedupe as m  # noqa: E402

AUDIT_DIR = ROOT / "docs" / "audits" / "aiid-corpus-classifier-2026-11-24"
DEFAULT_REF = "8753a7fe"
DEFAULT_SEED = 20261124
STRATUM_N = {"default": 40, "sec-keyword": 30, "harm": 30, "rce-artifact": 30}
RCE_WORD = re.compile(r"\brce\b")


def git_show(ref: str, path: str, cwd: Path = ROOT) -> bytes:
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=cwd, check=True,
                          capture_output=True).stdout


def load_rows(ref: str) -> list[dict]:
    return json.loads(git_show(ref, "data/incidents.json").decode("utf-8"))["incidents"]


def is_aiid(r: dict) -> bool:
    return any(str(s).startswith("AIID-") for s in r.get("source_ids") or [])


def corpus_text(r: dict) -> str:
    """The exact text _classify_corpus reads for a non-AIAAIC row."""
    return ((r.get("title") or "") + " " + (r.get("description") or "") + " "
            + " ".join(r.get("tags") or [])).lower()


def reclassify(r: dict) -> str:
    e = {k: r.get(k) for k in ("title", "description", "tags", "cve_ids", "description_source",
                               "aiaaic_seed_facts", "aiaaic_ethical_tags")}
    return m._classify_corpus(e)


def path_of(r: dict) -> tuple[str, list[str], list[str]]:
    """Which branch of _classify_corpus decides this row."""
    if r.get("cve_ids"):
        return "cve", [], []
    t = corpus_text(r)
    sec = [k for k in m._SECURITY_KEYWORDS_FOR_CORPUS if k in t]
    harm = [k for k in m._AI_HARM_KEYWORDS if k in t]
    real_sec = [k for k in sec if k != "rce" or RCE_WORD.search(t)]
    if real_sec:
        return "sec-keyword", sec, harm
    if sec:  # only "rce", and only inside a longer word
        return "rce-artifact", sec, harm
    if harm:
        return "harm", sec, harm
    return "default", sec, harm


# ---------------------------------------------------------------- flip
def cmd_flip(a):
    for label, ref in (("before", a.before), ("after", a.after)):
        r = next(x for x in load_rows(ref) if x["id"] == a.id)
        t = corpus_text(r)
        hits = [(k, t[max(0, mm.start() - 20):mm.end() + 20])
                for k in m._SECURITY_KEYWORDS_FOR_CORPUS for mm in re.finditer(re.escape(k), t)]
        print(f"[{label} {ref}] {a.id} stored corpus={r.get('corpus')} reclassified={reclassify(r)}")
        print(f"   affected={r.get('affected')!r}")
        print(f"   security-keyword hits: {hits or 'none'}")
        print(f"   ai-harm-keyword hits: {[k for k in m._AI_HARM_KEYWORDS if k in t] or 'none'}")


# ---------------------------------------------------------------- paths
def cmd_paths(a):
    rows = load_rows(a.ref)
    A = [r for r in rows if is_aiid(r)]
    mism = [r["id"] for r in A if reclassify(r) != r.get("corpus")]
    print(f"ref {a.ref}: {len(rows)} rows, {len(A)} carry an AIID- source_id; "
          f"stored corpus != re-run classifier on {len(mism)} {mism[:5]}")
    print("corpus on AIID rows:", dict(collections.Counter(r.get("corpus") for r in A)))
    tab = collections.Counter((path_of(r)[0], r.get("corpus")) for r in A)
    for (p, c), n in sorted(tab.items()):
        print(f"  path={p:<13} corpus={c:<8} n={n}")
    harm_suppressed = sorted(r["id"] for r in A if path_of(r)[0] == "rce-artifact" and path_of(r)[2])
    print(f"rce-artifact rows that ALSO carry an ai-harm keyword (suppressed ai-harm): "
          f"{len(harm_suppressed)} {harm_suppressed}")


# ---------------------------------------------------------------- sample
def cmd_sample(a):
    rows = load_rows(a.ref)
    A = sorted((r for r in rows if is_aiid(r)), key=lambda r: r["id"])
    by = collections.defaultdict(list)
    for r in A:
        by[path_of(r)[0]].append(r)
    out = []
    plan = dict(STRATUM_N)
    if a.strata:  # held-out draw: "default=30,rce-artifact=10"
        plan = {k: int(v) for k, v in (x.split("=") for x in a.strata.split(","))}
    excl = {r["id"] for r in _read_csv(a.exclude)} if a.exclude else set()
    for stratum, n in plan.items():
        pool = [r for r in by.get(stratum, []) if r["id"] not in excl]
        rng = random.Random(f"{a.seed}|{stratum}")
        pick = sorted(rng.sample(pool, min(n, len(pool))), key=lambda r: r["id"])
        print(f"stratum {stratum}: population {len(pool)}, drawn {len(pick)}")
        for r in pick:
            p, sec, harm = path_of(r)
            out.append({"id": r["id"], "stratum": stratum, "population": len(pool),
                        "source_ids": " ".join(r["source_ids"]), "stored_corpus": r.get("corpus"),
                        "attack_vector": r.get("attack_vector"), "sec_hits": " ".join(sec),
                        "harm_hits": " ".join(harm), "title": r.get("title"),
                        "affected": r.get("affected")})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        f.write(f"# AIID corpus sample: ref={a.ref} seed={a.seed} strata={plan} exclude={a.exclude and Path(a.exclude).name} "
                f"method=random.Random(f'{{seed}}|{{stratum}}').sample over id-sorted pool\n")
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows -> {a.out}")


# ---------------------------------------------------------------- score
def _read_csv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / den
    return max(0.0, c - h), min(1.0, c + h)


def cmd_score(a):
    sample = {r["id"]: r for r in _read_csv(a.sample)}
    adj = {r["id"]: r for r in _read_csv(a.adjudication)}
    missing = sorted(set(sample) - set(adj))
    extra = sorted(set(adj) - set(sample))
    if missing or extra:
        sys.exit(f"adjudication does not cover the sample: missing={missing} extra={extra}")
    conf = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    pop = {}
    for i, s in sample.items():
        gold = adj[i][a.column]
        assert gold in ("security", "ai-harm"), (i, gold)
        conf[(s["stored_corpus"], gold)] += 1
        per[s["stratum"]][(s["stored_corpus"], gold)] += 1
        pop[s["stratum"]] = int(s["population"])
    print(f"column={a.column}; borderline rows in sample: "
          f"{sum(1 for i in sample if adj[i].get('borderline') == 'y')}")
    print("Confusion over the whole sample (rows=stored label, cols=adjudicated):")
    for st in ("security", "ai-harm"):
        print(f"  stored {st:<8}: adj security={conf[(st,'security')]:>3}  adj ai-harm={conf[(st,'ai-harm')]:>3}")
    n = sum(conf.values())
    print(f"  unweighted sample accuracy {sum(v for (x, y), v in conf.items() if x == y)}/{n}")
    print("Per stratum (population-weighted estimate of wrong labels):")
    est_wrong = 0.0
    tot = 0
    for st in STRATUM_N:
        c = per.get(st)
        if not c:
            continue
        k = sum(c.values())
        wrong = sum(v for (x, y), v in c.items() if x != y)
        est = wrong / k * pop[st]
        est_wrong += est
        tot += pop[st]
        print(f"  {st:<13} pop={pop[st]:>4} drawn={k:>3} wrong={wrong:>3} "
              f"({wrong / k:.1%}, Wilson 95% {wilson(wrong, k)[0]:.0%}-{wilson(wrong, k)[1]:.0%}) "
              f"-> est. {est:.0f} wrong rows; {dict(c)}")
    print(f"Estimated wrong corpus labels across the {tot} AIID rows: {est_wrong:.0f} "
          f"({est_wrong / tot:.1%})")
    # security-class precision / ai-harm recall, population weighted
    w = collections.Counter()
    for st in STRATUM_N:
        c = per.get(st)
        if not c:
            continue
        k = sum(c.values())
        for key, v in c.items():
            w[key] += v / k * pop[st]
    tp_s, fp_s = w[("security", "security")], w[("security", "ai-harm")]
    tp_h, fp_h = w[("ai-harm", "ai-harm")], w[("ai-harm", "security")]
    def pct(x, y):
        return f"{x / y:.1%}" if y else "n/a (no rows)"
    print(f"Weighted: security precision {pct(tp_s, tp_s + fp_s)}; ai-harm precision "
          f"{pct(tp_h, tp_h + fp_h)}; ai-harm recall {pct(tp_h, tp_h + fp_s)}")


# ---------------------------------------------------------------- avscan
def cmd_avscan(a):
    rows = load_rows(a.ref)
    raw = {r["source_id"]: r for r in json.loads(git_show(a.ref, "ingest/aiid_full.json"))}
    A = [r for r in rows if is_aiid(r) and r.get("attack_vector") == "rce"]
    cls = collections.Counter()
    lists = collections.defaultdict(list)
    real = re.compile(r"\brce\b|remote code|command injection|sandbox escape|ransom")
    for r in A:
        sid = next(s for s in r["source_ids"] if s.startswith("AIID-"))
        title = (raw.get(sid, {}).get("title") or r.get("title") or "").lower()
        if real.search(title):
            k = "title has a real rce/ransom term"
        elif "rce" in title:
            k = "title has 'rce' ONLY inside a word (artifact proven from committed text)"
        else:
            k = "title has neither (decided by AIID's ephemeral description; not re-derivable offline)"
        cls[k] += 1
        lists[k].append(r["id"])
    print(f"ref {a.ref}: {len(A)} AIID rows with attack_vector=rce")
    for k, n in cls.most_common():
        print(f"  {n:>4}  {k}")
    for k in lists:
        if "ONLY inside" in k:
            words = collections.Counter()
            for i in lists[k]:
                r = next(x for x in A if x["id"] == i)
                words.update(w for w in re.findall(r"[a-z]*rce[a-z]*", (r["title"] or "").lower()))
            print("  host words:", dict(words.most_common(12)))
            print("  ids:", " ".join(lists[k]))
    for i in ("INC-17386", "INC-17387"):
        r = next((x for x in A if x["id"] == i), None)
        if r:
            print(f"  {i}: {r['title']!r} owasp_llm={r.get('owasp_llm')} owasp_asi={r.get('owasp_asi')} "
                  f"mitre_atlas={r.get('mitre_atlas')} severity={r.get('severity')}")


# ---------------------------------------------------------------- project
OPTIONS = ("O0", "O1", "O2", "O3", "O2+O3", "O5", "O6")


def built_moves(option: str) -> set[str]:
    """IDs whose corpus the REAL build of `option` moves (dryrun JSON; O0 = none)."""
    if option == "O0":
        return set()
    d = json.loads((AUDIT_DIR / f"dryrun-{option.replace('+', '_')}.json").read_text(encoding="utf-8"))
    return set(d["fields"].get("corpus", []))


def _flip(c: str) -> str:
    return "ai-harm" if c == "security" else "security"


def cmd_project(a):
    """Error of each option = stored label, flipped on the rows the option's real build
    moved, compared with the adjudicated label. Sample: stratum-weighted estimate over the
    AIID rows. new24: exact count over the 24-row census."""
    sample = _read_csv(a.sample)
    adj = {r["id"]: r for r in _read_csv(a.adjudication)}
    new24 = _read_csv(AUDIT_DIR / "new24.csv")
    stored24 = {r["id"]: r.get("corpus") for r in load_rows(a.ref)
                if r["id"] in {x["id"] for x in new24}}
    pop = {r["stratum"]: int(r["population"]) for r in sample}
    moves = {o: built_moves(o) for o in OPTIONS}
    for col in ("adjudicated_corpus", "r2_corpus"):
        print(f"reading {'R1' if col == 'adjudicated_corpus' else 'R2'} ({col}):")
        for opt in OPTIONS:
            est = 0.0
            for st in STRATUM_N:
                rows = [r for r in sample if r["stratum"] == st]
                if not rows:
                    continue
                wrong = sum(1 for r in rows if (_flip(r["stored_corpus"]) if r["id"] in moves[opt]
                                                else r["stored_corpus"]) != adj[r["id"]][col])
                est += wrong / len(rows) * pop[st]
            w24 = sum(1 for r in new24 if (_flip(stored24[r["id"]]) if r["id"] in moves[opt]
                                           else stored24[r["id"]]) != r[col])
            print(f"   {opt:<6} moves {len(moves[opt]):>4} rows; est. wrong AIID corpus labels "
                  f"{est:5.0f} ({est / sum(pop.values()):.1%}); new-24 census wrong {w24}/24")


# ---------------------------------------------------------------- crosscheck
def cmd_crosscheck(a):
    """Route 1 (rule over the committed rows, path_of) vs route 2 (a real build with the
    option's patch, dryrun JSON): the AIID rows each option moves must be the same SET."""
    rows = load_rows(a.ref)
    A = {r["id"]: r for r in rows if is_aiid(r)}
    rule = {
        "O1": {"INC-07572"},
        "O2": {i for i, r in A.items() if path_of(r)[0] == "rce-artifact" and path_of(r)[2]},
        "O3": {i for i, r in A.items() if path_of(r)[0] == "default"},
        "O2+O3": {i for i, r in A.items() if path_of(r)[0] in ("default", "rce-artifact")},
    }
    bad = 0
    for opt, want in rule.items():
        d = json.loads((AUDIT_DIR / f"dryrun-{opt.replace('+', '_')}.json").read_text(encoding="utf-8"))
        got = {i for i in d["fields"].get("corpus", []) if i in A}
        ok = got == want
        bad += not ok
        print(f"{opt:<6} rule={len(want):>4} build={len(got):>4} equal={ok} "
              f"only-rule={sorted(want - got)[:5]} only-build={sorted(got - want)[:5]}")
    sys.exit(1 if bad else 0)


# ---------------------------------------------------------------- dryrun
O1_KEY = "AIID-195"
O1_OVERRIDE = {
    "corpus": "ai-harm",
    "_note": ("label-scientist 2026-11-24: pins INC-07572's base corpus (ai-harm). Refresh PR #110 "
              "flipped it to security only because the AIID deployer string gained 'Law Enforcement', "
              "and _classify_corpus's keyword 'rce' substring-matches 'enfo-rce-ment'. Agent-suggested, "
              "pending user re-review. Evidence: docs/audits/aiid-corpus-classifier-2026-11-24.md"),
}

_O2_OLD = "    has_security = any(kw in text for kw in _SECURITY_KEYWORDS_FOR_CORPUS)\n"
_O2_NEW = ("    has_security = any((re.search(r\"\\brce\\b\", text) if kw == \"rce\" else kw in text)\n"
           "                       for kw in _SECURITY_KEYWORDS_FOR_CORPUS)\n")
_O3_OLD = "    if has_harm:\n        return \"ai-harm\"\n    return \"security\"\n"
_O3_NEW = ("    if has_harm:\n        return \"ai-harm\"\n"
           "    if entry.get(\"aiid_id\"):\n        return \"ai-harm\"\n    return \"security\"\n")

# O5 (CANDIDATE vocabulary, not approved; measured only): O2 + an AIID no-match default of
# ai-harm UNLESS the row's text carries one of these security terms. The terms are new
# vocabulary, so under WS2-T4 rules they need foreman/user approval before any adoption.
O5_TERMS = (r"\b(?:breach\w*|hack\w*|credential\w*|unauthori[sz]\w*|without (?:authori[sz]ation|permission)"
            r"|api keys?|tokens?\b|attacker\w*|cyber\w*|spyware|malicious|stole\b|steal\w*|stolen"
            r"|compromis\w*|exposed|extort\w*|impersonat\w*|exploit\w*|threat actors?)")
_NL = chr(10)
_O5_NEW = _NL.join([
    '    if has_harm:',
    '        return "ai-harm"',
    '    if entry.get("aiid_id"):',
    '        return "security" if re.search(' + repr(O5_TERMS) + ', text) else "ai-harm"',
    '    return "security"',
    ''])

# O6 (CANDIDATE, measured only): decouple AIID corpus from the description entirely, the
# WS0-T3 way. Use AIID's own structured MIT AI Risk Repository domain tag (a closed
# upstream vocabulary carried as `mit-risk-domain:*`): domains 2 (privacy & security) and
# 4 (malicious actors & misuse) -> security, any other domain -> ai-harm. Rows with no MIT
# tag keep today's keyword path unchanged. Inserted before the keyword logic.
_O6_OLD = "    seed_text = _aiaaic_seed_text(entry)" + _NL
_O6_NEW = _NL.join([
    '    _mit = [t.split(":", 1)[1] for t in (entry.get("tags") or []) if t.startswith("mit-risk-domain:")]',
    '    if entry.get("aiid_id") and _mit:',
    '        return "security" if any(d.startswith(("2-", "4-")) for d in _mit) else "ai-harm"',
    '    seed_text = _aiaaic_seed_text(entry)',
    ''])


def write_o1_override(path: Path) -> None:
    """The O1 input change, written by code (never by hand): one key added."""
    data = json.loads(path.read_text(encoding="utf-8"))
    ov = data["overrides"]
    if O1_KEY in ov and ov[O1_KEY] != O1_OVERRIDE:
        sys.exit(f"{O1_KEY} already has a different override: {ov[O1_KEY]}")
    ov[O1_KEY] = O1_OVERRIDE
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # LF, as committed
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _patch(path: Path, old: str, new: str) -> None:
    s = path.read_text(encoding="utf-8")
    if s.count(old) != 1:
        sys.exit(f"patch anchor not found exactly once in {path}")
    path.write_bytes(s.replace(old, new).encode("utf-8"))


def entity_delta(before: list[dict], after: list[dict]) -> dict:
    b = {e["id"]: e for e in before}
    a = {e["id"]: e for e in after}
    fields = collections.defaultdict(list)
    moves = collections.Counter()
    for i in sorted(set(a) & set(b)):
        for k in sorted(set(a[i]) | set(b[i])):
            if a[i].get(k, "<absent>") != b[i].get(k, "<absent>"):
                fields[k].append(i)
        if a[i].get("corpus") != b[i].get("corpus"):
            moves[f"{b[i].get('corpus')}->{a[i].get('corpus')}"] += 1
    return {"rows_before": len(b), "rows_after": len(a),
            "ids_added": sorted(set(a) - set(b)), "ids_removed": sorted(set(b) - set(a)),
            "id_order_equal": [e["id"] for e in before] == [e["id"] for e in after],
            "fields": {k: v for k, v in sorted(fields.items())}, "corpus_moves": dict(moves)}


def cmd_dryrun(a):
    scratch = Path(a.scratch).resolve()
    wt = scratch / f"wt-{a.option.replace('+', '_')}"
    if wt.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT)
    subprocess.run(["git", "worktree", "add", "--detach", str(wt), a.ref], cwd=ROOT, check=True,
                   capture_output=True)
    try:
        if "O1" in a.option:
            write_o1_override(wt / "data" / "curation_overrides.json")
        if "O2" in a.option:
            _patch(wt / "scripts" / "merge_and_dedupe.py", _O2_OLD, _O2_NEW)
        if "O3" in a.option:
            _patch(wt / "scripts" / "merge_and_dedupe.py", _O3_OLD, _O3_NEW)
        if a.option == "O6":
            _patch(wt / "scripts" / "merge_and_dedupe.py", _O6_OLD, _O6_NEW)
        if a.option == "O5":
            _patch(wt / "scripts" / "merge_and_dedupe.py", _O2_OLD, _O2_NEW)
            _patch(wt / "scripts" / "merge_and_dedupe.py", _O3_OLD, _O5_NEW)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for s in ("parse_existing.py", "merge_and_dedupe.py"):
            p = subprocess.run([sys.executable, f"scripts/{s}"], cwd=wt, env=env, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            if p.returncode:
                sys.exit(f"{s} failed:\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
        before = json.loads(git_show(a.ref, "data/incidents.json").decode("utf-8"))
        after = json.loads((wt / "data" / "incidents.json").read_text(encoding="utf-8"))
        d = entity_delta(before["incidents"], after["incidents"])
        # data/stats.json is written by the render step, not by merge, so comparing the file
        # here could never fail (it is untouched by this build). Derive the published counts
        # from the rows instead, with the same standing rule entry_status.stands() uses.
        def counts(rows):
            st = [e for e in rows if e.get("status") not in ("retracted", "unverified")]
            return {"incident_count": len(st),
                    "landmark_count": sum(1 for e in st if e.get("tier") == "landmark")}
        cb, ca = counts(before["incidents"]), counts(after["incidents"])
        d["derived_counts"] = {"before": cb, "after": ca}
        d["stats_changed"] = {k: [cb[k], ca[k]] for k in cb if cb[k] != ca[k]}
        changed = subprocess.run(["git", "status", "--porcelain"], cwd=wt, capture_output=True,
                                 text=True).stdout.split("\n")
        d["files_changed"] = sorted(x[3:] for x in changed if x.strip())
        rowsA = {e["id"]: e for e in after["incidents"]}
        d["corpus_moved_aiid"] = sum(1 for i in d["fields"].get("corpus", []) if is_aiid(rowsA[i]))
        d["corpus_moved_non_aiid"] = [i for i in d["fields"].get("corpus", []) if not is_aiid(rowsA[i])]
        d["standing_corpus_after"] = dict(collections.Counter(
            e.get("corpus") for e in after["incidents"] if e.get("status") not in ("retracted", "unverified")))
        d["option"], d["ref"] = a.option, a.ref
        print(f"== dryrun {a.option} on {a.ref}: rows {d['rows_before']}->{d['rows_after']}, "
              f"added {len(d['ids_added'])}, removed {len(d['ids_removed'])}, id order equal {d['id_order_equal']}")
        for k, ids in d["fields"].items():
            print(f"   field {k:<22} {len(ids):>5} rows  {' '.join(ids[:8])}{' ...' if len(ids) > 8 else ''}")
        print(f"   corpus moves {d['corpus_moves']}  (AIID rows {d['corpus_moved_aiid']}, "
              f"non-AIID {len(d['corpus_moved_non_aiid'])} {d['corpus_moved_non_aiid'][:10]})")
        print(f"   published counts (derived from rows) changed {d['stats_changed']} {d['derived_counts']['after']}")
        print(f"   files changed by the build {d['files_changed']}")
        print(f"   standing corpus after {d['standing_corpus_after']}")
        if a.json:
            Path(a.json).write_bytes((json.dumps(d, indent=1) + "\n").encode("utf-8"))
            print(f"   full ID lists -> {a.json}")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT, capture_output=True)


# ---------------------------------------------------------------- flipguard
def cmd_flipguard(a):
    """Per-entity check: every row present at BASE and HEAD whose `corpus`
    differs must be declared in --allow. Fails (exit 1) on any undeclared flip."""
    base = {e["id"]: e for e in load_rows(a.base)}
    if a.head_file:
        head_rows = json.loads(Path(a.head_file).read_text(encoding="utf-8"))["incidents"]
    else:
        head_rows = load_rows(a.head)
    allow = {x for x in (a.allow or "").split(",") if x}
    flips = [(e["id"], base[e["id"]].get("corpus"), e.get("corpus"))
             for e in head_rows if e["id"] in base and base[e["id"]].get("corpus") != e.get("corpus")]
    bad = [f for f in flips if f[0] not in allow]
    print(f"flipguard base={a.base} head={a.head_file or a.head}: {len(flips)} corpus flip(s), "
          f"{len(bad)} undeclared")
    for i, b, h in flips:
        print(f"   {'DECLARED  ' if i in allow else 'UNDECLARED'} {i}: {b} -> {h}")
    sys.exit(1 if bad else 0)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("flip")
    f.add_argument("--before", default="6a4d8261")
    f.add_argument("--after", default=DEFAULT_REF)
    f.add_argument("--id", default="INC-07572")
    for name in ("paths", "avscan"):
        q = sub.add_parser(name)
        q.add_argument("--ref", default=DEFAULT_REF)
    s = sub.add_parser("sample")
    s.add_argument("--ref", default=DEFAULT_REF)
    s.add_argument("--seed", type=int, default=DEFAULT_SEED)
    s.add_argument("--out", default=str(AUDIT_DIR / "sample.csv"))
    s.add_argument("--strata", help="override per-stratum n, e.g. default=30,rce-artifact=10")
    s.add_argument("--exclude", help="CSV whose ids are excluded from the pools (held-out draw)")
    sc = sub.add_parser("score")
    sc.add_argument("--sample", default=str(AUDIT_DIR / "sample.csv"))
    sc.add_argument("--adjudication", default=str(AUDIT_DIR / "adjudication.csv"))
    sc.add_argument("--column", default="adjudicated_corpus",
                    help="adjudicated_corpus (reading R1) or r2_corpus (reading R2)")
    sub.add_parser("apply-o1", help="write the O1 override into THIS tree's data/curation_overrides.json")
    cc = sub.add_parser("crosscheck")
    cc.add_argument("--ref", default=DEFAULT_REF)
    pj = sub.add_parser("project")
    pj.add_argument("--ref", default=DEFAULT_REF)
    pj.add_argument("--sample", default=str(AUDIT_DIR / "sample.csv"))
    pj.add_argument("--adjudication", default=str(AUDIT_DIR / "adjudication.csv"))
    d = sub.add_parser("dryrun")
    d.add_argument("--option", required=True, choices=list(OPTIONS))
    d.add_argument("--ref", default=DEFAULT_REF)
    d.add_argument("--scratch", required=True)
    d.add_argument("--json")
    g = sub.add_parser("flipguard")
    g.add_argument("--base", required=True)
    g.add_argument("--head", default=DEFAULT_REF)
    g.add_argument("--head-file")
    g.add_argument("--allow")
    a = p.parse_args()
    {"flip": cmd_flip, "paths": cmd_paths, "sample": cmd_sample, "score": cmd_score,
     "avscan": cmd_avscan, "project": cmd_project, "crosscheck": cmd_crosscheck,
     "apply-o1": lambda a: write_o1_override(ROOT / "data" / "curation_overrides.json"), "dryrun": cmd_dryrun, "flipguard": cmd_flipguard}[a.cmd](a)


if __name__ == "__main__":
    main()
