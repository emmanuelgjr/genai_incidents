#!/usr/bin/env python
"""Render the per-row audit note from the spec, the base corpus (git 589376db), the exported evidence
table and the delta JSON. Deterministic; re-run after any spec change.

  python -I render_audit.py fetch-evidence-2026-10-15.json delta-2026-10-15.json > reference-audit-2026-10-15.md
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import d1302_spec as S  # noqa: E402

ev = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
delta = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
page = {p["url"]: p for p in ev["checked_pages"]}
raw = subprocess.run(["git", "show", "589376db:data/incidents.json"], cwd=REPO, check=True, capture_output=True).stdout
base = {e["id"]: e for e in json.loads(raw.decode("utf-8"))["incidents"]}


def legacy_ids(e):
    return [s for s in e["source_ids"] if re.match(r"^(LEGACY-)?INC-\d+$", s)]


def by_tier(ids):
    c = {}
    for i in ids:
        c[base[i]["quality_tier"]] = c.get(base[i]["quality_tier"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items())) or "-"


L = []
w = L.append
fx, un = S.FIXED, S.UNVERIFIED
w("# D130-2: legacy-seed reference remediation, 2026-10-15")
w("")
w("**Agent-suggested, not human-reviewed.** Every replacement below is pending the user's re-review; every demoted row")
w("carries a curation-override note saying so. Scope: the 30 legacy-seed rows (source_ids `INC-<n>` / `LEGACY-INC-<n>`) that trip")
w("R1 or R2 of `docs/audits/reference-detection-2026-10-14.md` (user ruling D130, 2026-10-14). No third-party page text is copied")
w("here beyond titles and the short tokens used to link a fetched page to the entry.")
w("")
w("Method: each URL written into the corpus was fetched in this session through `ingest/common.fetch_once` (robots, per-host rate")
w("limit, identifying User-Agent) by `fetch_evidence.py`, and its page text was checked for the row-linking tokens listed per row")
w("(`export_evidence.py` re-checks every token and aborts if one is missing; it was seen to fail on a wrong token during this work).")
w("Discovery used web search tools outside the corpus path; discovery results are never written into the corpus unless the page was")
w("then fetched through `common.py`. All changes are `data/curation_overrides.json` entries generated from `d1302_spec.py` by")
w("`build_overrides.py`; `data/incidents.json` is a build output and was not edited.")
w("")
w("## Outcome")
w("")
w("| outcome | rows | by original quality_tier |")
w("|---|---|---|")
w(f"| fixed (reference replaced/removed, description re-derived, demoted to auto) | {len(fx)} | {by_tier(fx)} |")
w(f"| unverified (`status: unverified`, no-confirmed-source) | {len(un)} | {by_tier(un)} |")
w(f"| examined, not changed: false positive / merge artifact | {len(S.UNCHANGED)} | {by_tier(S.UNCHANGED)} |")
w(f"| deferred: mechanism gap (feed-merged CVE/GHSA rows; a whole-list `references` override would freeze them) | {len(S.DEFERRED)} | {by_tier(S.DEFERRED)} |")
w(f"| deferred: ruling (c) demotion collides with the validate.py landmark-label gate | {len(S.DEFERRED_LABEL)} | {by_tier(S.DEFERRED_LABEL)} |")
total = len(fx) + len(un) + len(S.UNCHANGED) + len(S.DEFERRED) + len(S.DEFERRED_LABEL)
w(f"| **total** | **{total}** | |")
w("")
changed_desc = sorted(r for r, d in delta["rows"].items() if "description" in d)
w(f"Rows whose `description` changed ({len(changed_desc)}): " + ", ".join(changed_desc) + ".")
w("")
w("Re-derivation of the 30: the detection report's `r1`/`r2` definitions (its Appendix A) applied to the rows of `data/incidents.json` at")
w("589376db that carry an `INC-<n>`/`LEGACY-INC-<n>` source_id give 30 rows (13 curated, 17 reviewed), equal to the report's count.")
w("The list is the union of the five outcome groups above. Command: `python -I docs/audits/reference-audit-2026-10-15/derive_list.py`.")
w("")
w("## Field-level delta (working agreement 2)")
w("")
w(f"Base 589376db vs this branch's build: entry count {delta['entry_count'][0]} -> {delta['entry_count'][1]}; ID set equal: {delta['id_set_equal']}; "
  f"rows with any difference: {len(delta['rows'])} (= {len(fx)} fixed + {len(un)} unverified); rows outside those with any difference: {len(delta['unintended'])}.")
w("Envelope: " + "; ".join(f"`{k}` {v[0]} -> {v[1]}" for k, v in delta["envelope"].items()) + ". (`generated` is the build date stamp.)")
w("Headline counts in `data/stats.json` (and the doc surfaces templated from it, e.g. the README cells) that moved: " + "; ".join(f"`{k}` {v[0]} -> {v[1]}" for k, v in delta["stats"].items()) + f"; stats keys outside this declared set: {len(delta['unintended_stats'])}.")
unv_n = len(un)
w(f"- `incident_count` -15,755 -> 15,745: exactly the {unv_n} unverified rows ({', '.join(sorted(un))}); `unverified_count` 0 -> {unv_n}.")
dem = sorted(r for r in fx if base[r]['quality_tier'] == 'curated' and delta['rows'][r].get('tier'))
w(f"- `landmark_count` {delta['stats']['landmark_count'][0]} -> {delta['stats']['landmark_count'][1]}: the {len(dem)} curated rows demoted to auto that leave the landmark tier ({', '.join(dem)}); INC-02454 is also demoted but its corpus is pinned to `ai-harm` (base value), which keeps it landmark. No unverified row is landmark.")
w("- `generated` is the build date stamp. `retracted_count`, `disputed_count`, version and year range are unchanged.")
w("")
w("Full per-row before/after: `delta-2026-10-15.json`. Enumerated fields:")
w("")
w("| field | rows | kind | justification |")
w("|---|---|---|---|")
kinds = {
    "references": ("intended", "the D130-2 change itself"),
    "description": ("intended", "re-derived from the fetched source; unsupported figures dropped"),
    "impact": ("intended", "restated the dropped figures/claims; rewritten from the same source"),
    "affected": ("intended", "restated the dropped figures/claims; rewritten from the same source"),
    "title": ("intended", "title asserted claims the confirmed source does not support (bounce #1 defect 3); re-derived from the source so title and description agree"),
    "quality_tier": ("intended", "ruling D130(c): every replaced reference demotes to auto; never promoted"),
    "status": ("intended", "D130(b)/D130-1: unverified"),
    "status_reason": ("intended", "D130-1: {code: no-confirmed-source, as_of: 2026-10-15}"),
    "updated": ("derived", "history stamp: content changed (build date)"),
    "last_seen": ("derived", "history stamp: content changed (build date)"),
    "confidence": ("derived", "`_derive_confidence`: curated/reviewed -> high; a single auto-tier source with no CVE -> low/medium. Follows quality_tier only"),
    "tier": ("derived", "`_derive_tier`: curated -> landmark; demoted curated rows without aiid_id / ai-harm corpus become feed. Follows quality_tier only"),
}
fields = {}
for rid, d in delta["rows"].items():
    for f in d:
        fields.setdefault(f, []).append(rid)
for f in sorted(fields):
    k, j = kinds.get(f, ("UNEXPECTED", "?"))
    ids = sorted(fields[f])
    w(f"| `{f}` | {len(ids)}" + (f" ({', '.join(ids)})" if len(ids) <= 4 else "") + f" | {k} | {j} |")
w("")
w("Derived-field coupling (the WS0-T3 trap, `docs/audits/WS0-T3-cascade-2026-07-18.md`): classifiers that read `description`/`title` run BEFORE the")
w("step-4d curation override, so `attack_vector`, `severity`, `owasp_*`, `nist_ai_rmf`, `mitre_atlas*`, `maestro_layers`, `category` and `tags`")
w("keep their base values for every row (the delta shows none moved). One classifier output is re-derived AFTER the override: `corpus`.")
w("For INC-02454 the corrected text flipped `corpus` from `ai-harm` to `security` in a trial build; that is a classifier artifact of the new wording, not a ruling,")
w("so the override pins it to the base value `ai-harm` (`pin` in the spec) and the delta shows no `corpus` change. Consequence: the mapping fields still describe the")
w("OLD wording on the rows whose description changed; they are not re-derived here (re-labelling is label-scientist's call; listed as a follow-up).")
w("")
w("## Per-row evidence")
w("")
ids_all = sorted(set(fx) | set(un) | set(S.UNCHANGED) | set(S.DEFERRED) | set(S.DEFERRED_LABEL))
for rid in ids_all:
    e = base[rid]
    if rid in fx:
        outcome = "FIXED"
    elif rid in un:
        outcome = "UNVERIFIED"
    elif rid in S.UNCHANGED:
        outcome = "NOT CHANGED (false positive / merge artifact)"
    elif rid in S.DEFERRED:
        outcome = "DEFERRED (mechanism gap)"
    else:
        outcome = "DEFERRED (demotion vs landmark label)"
    w(f"### {rid} - {outcome}")
    w("")
    w(f"- legacy ids: {', '.join(legacy_ids(e))}; quality_tier at base: {e['quality_tier']}; title: {e['title']}")
    spec = fx.get(rid) or un.get(rid) or S.DEFERRED.get(rid) or S.DEFERRED_LABEL.get(rid) or {}
    w("- references at base: " + "; ".join(f"{r['url']} ({r['type']})" for r in e["references"][:6]) + (f"; ... {len(e['references'])} in total" if len(e["references"]) > 6 else ""))
    if spec.get("old_ref_kind"):
        w(f"- flagged reference(s) and what they were: {spec['old_ref_kind']}")
    if rid in fx:
        for q in spec.get("queries", []):
            w(f"- query / discovery: {q}")
        for r in spec.get("rejected", []):
            w(f"- candidate rejected / note: {r}")
        new_urls = [u for olds in spec["replace"].values() for u in olds]
        for u in new_urls:
            p = page[u]
            w(f"- chosen: {u}")
            w(f"  - fetched: HTTP {p['status']}; title \"{p['title']}\"; fetched_at {p['fetched_at']}; sha256 {str(p['sha256'])[:16]}...; publication date is in the reference title")
            w(f"  - matched tokens linking the page to the entry: {', '.join(p['tokens_matched'])}")
        if not [u for u in new_urls]:
            w("- chosen: none needed; the equivalent verified reference(s) already on the row are kept (fetched this session; see the evidence table)")
        w("- references after (each fetched this session; see the evidence table): " + "; ".join(r["url"] for r in delta["rows"][rid]["references"][1]))
        w(f"- description before: {e['description']}")
        w(f"- description after: {spec['description']}")
        w(f"- impact before: {e.get('impact')}")
        w(f"- impact after: {spec['impact']}")
        w(f"- affected before: {e.get('affected')}")
        w(f"- affected after: {spec['affected']}")
        if spec.get("title"):
            w(f"- title after: {spec['title']}")
        w(f"- figures dropped (not found in the source): {'; '.join(spec['figures_dropped']) or 'none'}")
        w(f"- other unsupported claims dropped / residuals: {'; '.join(spec['also_dropped']) or 'none'}")
        w("- quality_tier: " + e["quality_tier"] + " -> auto (ruling D130(c)); the curation-override `_note` reads \"agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review\"")
    elif rid in un:
        for ln in spec["effort"]:
            w(f"- {ln}")
        w("- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).")
    elif rid in S.UNCHANGED:
        w(f"- finding: {S.UNCHANGED[rid]}")
        w("- action: none (row byte-identical to base).")
    elif rid in S.DEFERRED:
        w(f"- reason deferred: {S.DEFERRED_REASON}")
        w("- action: none (row byte-identical to base).")
    else:
        for q in spec.get("queries", []):
            w(f"- query / discovery: {q}")
        for r in spec.get("rejected", []):
            w(f"- candidate rejected / note: {r}")
        w(f"- reason deferred: {S.DEFERRED_LABEL_REASON}")
        w("- action: none (row byte-identical to base).")
    w("")
w("## Other findings (not changed; outside the R1/R2 scope)")
w("")
w("- Broken or unfetchable references seen while checking, left as found: `dataprotection.ie` TikTok press-release URLs (HTTP 404), `atlas.mitre.org/studies/AML.CS0037` and `.../AML.CS0050` (HTTP 404), `invicti.com/blog/web-security/prompt-injection-attacks/` (HTTP 404), `reuters.com/technology/ai-hiring-bias-settlements-2024/` (robots-refused), the Stanford SIO page (HTTP 403 to our UA), `vulncheck.com` Flowise advisory (HTTP 404).")
w("- Titles of the corrected rows were re-derived from the confirmed sources (bounce #1, defect 3); the unverified rows keep their titles.")
w("- `date` fields that disagree with the fetched sources, left as found (outside the intended-delta list; queued): INC-02774 (2025-03; decision announced 2024-12-20), INC-03004 (2025-01; paper 2025-02-18), INC-03972 (2024-10; paper 2024-09-17).")
w("- Discovery note, unverified: a search-result snippet claimed a July 2026 Seventh Circuit vacatur of the Clearview settlement. No fetched source confirms it, so it is not in the description; worth a check before any release statement about INC-02454.")
w("- Legacy over-merges to report for WS4-T19 (not decided here): INC-04142 (AgentDojo merged into RAG poisoning), INC-04067 (Carlini model-stealing merged into a system-prompt-extraction narrative), INC-02454 (INC-036 + INC-039), INC-02774 (INC-035 + INC-050), INC-04179 (INC-044 + INC-048).")
w("- Queued, not in this task: stale classifier labels on the corrected rows (task D130-2L, user-ruled); the five frozen feed-merged rows via a `references_remove` override after D139-M; the `date` mismatches above (follow-up).")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")
print("\n".join(L))
