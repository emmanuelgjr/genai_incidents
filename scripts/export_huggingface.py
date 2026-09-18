"""
Build a Hugging Face Datasets package for the incident corpus:

  dist/hf/incidents.jsonl   one incident per line (load_dataset-friendly)
  dist/hf/README.md         dataset card (YAML front matter + usage)

Then optionally push to the Hub:

  HF_TOKEN=...  python scripts/export_huggingface.py --push --repo <user>/genai-incidents

`dist/` is a build artifact (gitignored). The JSONL is a flat projection of
data/incidents.json["incidents"], so `datasets.load_dataset("json", ...)`
and `load_dataset("<repo>")` both work.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "dist" / "hf"

CARD = """\
---
license: cc-by-4.0
language:
  - en
pretty_name: GenAI & Agentic AI Security Incidents
tags:
  - security
  - cybersecurity
  - ai-safety
  - ai-security
  - llm
  - agentic-ai
  - incidents
  - threat-intelligence
  - prompt-injection
  - owasp
  - mitre-atlas
  - nist-ai-rmf
task_categories:
  - text-classification
  - text-retrieval
size_categories:
  - {size_cat}
configs:
  - config_name: default
    data_files: incidents.jsonl
---

# GenAI & Agentic AI Security Incidents

**{count} real-world and research incidents** involving generative-AI and agentic-AI
systems — prompt injection, jailbreaks, data exfiltration, deepfakes, model and
supply-chain compromise, agent hijacking, and AI-enabled harms — cross-mapped to six
taxonomies. Dataset version `{version}`.

Every applicable incident is tagged with four core taxonomies:

- **OWASP Top 10 for LLM Applications (2026)** — `LLM01`–`LLM10`
- **OWASP Agentic Top 10 (ASI)** — `ASI01`–`ASI10`
- **NIST AI RMF (AI 100-1)** — `GOVERN` / `MAP` / `MEASURE` / `MANAGE`
- **MITRE ATLAS** — techniques (`AML.T00xx`) and tactics (`AML.TA00xx`)

Plus, where available:

- **MAESTRO** architectural layers (`L1`–`L7`) — companion, carried where the upstream source provides it
- **VERIS 1.4.1** crosswalk (`veris:*` tags) — experimental, computed at export time from `attack_vector`, not a stored per-incident field

## Quickstart

```python
from datasets import load_dataset
ds = load_dataset("{repo}", split="train")

# prompt-injection incidents
ds.filter(lambda r: "LLM01" in (r["owasp_llm"] or []))

# only maintainer-reviewed entries
ds.filter(lambda r: r["quality_tier"] in ("reviewed", "curated"))

# the landmark subset -- the "notable incidents" figure this project asks
# you to cite, rather than the full corpus (which is mostly CVE/advisory bulk)
ds.filter(lambda r: r["tier"] == "landmark")
```

## What's inside

Key fields per record (full reference in the data dictionary):

- `id`, `title`, `description`, `date`, `year`, `severity`
- `attack_vector` — normalised exploit/harm class (e.g. `prompt-injection`, `deepfake`, `rce`)
- `owasp_llm`, `owasp_asi`, `nist_ai_rmf`, `mitre_atlas`, `mitre_atlas_tactics` — framework mappings
- `cve_ids`, `cwe_ids`, `cvss_score` — where applicable
- `references` — source URLs · `source_ids` — upstream provenance
- `quality_tier` — `curated` / `reviewed` / `auto` (filter by vetting level)
- `tier` — `landmark` (the curated, notable subset) or `feed` (the comprehensive
  CVE/GHSA/OSV stream). A **different axis** from `quality_tier`, not a rename of it:
  most landmark rows qualify by being catalogued in the AI Incident Database, which
  says nothing about vetting level. Cite the landmark count, not the corpus total,
  when you mean "notable incidents"
- `corpus` — `security` or `ai-harm`
- `source_freshness` — present only on rows whose upstream source has stopped refreshing (see below)

### Source freshness

Some rows carry a `source_freshness` object (`{{status, as_of, sources}}`). It says that
the **upstream source that supplied the row has stopped refreshing** — not that the row
was withdrawn, superseded, or is wrong. The two are independent facts, and the field
exists because conflating them is how a dataset comes to mislead without any single
value being false: this corpus is rebuilt from committed ingest snapshots, so a row keeps
being emitted long after its upstream download disappears. In particular
**`source_status: "active"` means *emitted on the latest build*, never *re-checked
against a live source*.** `sources` names the stale sources by their key in the
repository's published freshness registry (`data/source_freshness.json`), and `as_of` is
the earliest `last_success` date recorded there for those sources — a date taken from the
registry, **not** the build date. Everything that source contributed to the row,
including any taxonomy or risk-tier tags it supplied, is current through `as_of` and no
further. Absence of the field means no *tracked* source feeding the row is known to be
stale — not that the row has been verified current. Full definition, the registry's own
fields, and what the registry does and does not cover:
[`docs/DATA_DICTIONARY.md` → Source freshness](https://github.com/emmanuelgjr/genai_incidents/blob/main/docs/DATA_DICTIONARY.md#source-freshness),
which is authoritative; this is a summary of it.

## Sources & provenance

Aggregated and de-duplicated from AIID, OECD AI Incidents Monitor, AIAAIC, MITRE ATLAS,
AVID, MIT FutureTech AI Risk Repository, NVD / GitHub Security Advisories / OSV, garak,
promptfoo, red-team benchmark catalogues, and researcher blogs / vendor threat reports.

## Intended uses & limitations

Built for security research, red-team scenario design, taxonomy / benchmark work, and
trend analysis. It is **not** an exhaustive census: coverage skews toward
English-language, publicly-reported events, and `auto`-tier rows are bulk-ingested
without individual review — filter on `quality_tier` for higher-confidence subsets. See
the datasheet for full scope, collection method, and limitations.

## Licensing

Data is released under **CC BY 4.0** overall (`license: cc-by-4.0` above; see
`LICENSE-DATA` and `NOTICE-DATA` in the source repository). A subset of entries that
cite the **AIAAIC Repository** — those whose description derives from
AIAAIC's sheet (`description_source == "aiaaic"`) plus a smaller set of hand-curated
rows whose title and categorical facts derive from AIAAIC directly (current count
audited in `docs/SOURCE_LICENSES.md` §1.1, not restated here to avoid drift) —
carries an *additional*, row-level **CC BY-SA 4.0** attribution/share-alike obligation — this
does not apply project-wide, only to those specific rows. Each such row carries a
machine-readable `content_license` field (`source`, `license`, `attribution`,
`obligations`) naming AIAAIC as the attribution target; redistributing or adapting
one of those rows' content should honor that row's attribution and share-alike
obligation. A separate, open question about an EU/UK *sui generis* database right
over the AIAAIC extraction is tracked in the source repository's `NOTICE-DATA` and
`docs/SOURCE_LICENSES.md` (§1.1) and is **not** resolved by this row-level marker.

Rows sourced from the **OECD AI Incidents and Hazards Monitor (AIM)** carry a
narrower, separate obligation: `description` on those rows is reduced to
structural facts and a source link only (never AIM's LLM-generated
`summary`/`evidences`, machine output derived from copyrighted third-party
news of unresolved ownership). A small number of rows instead ship another
source's description, where that source won the merge; every OECD AIM-sourced
row carries a per-entry citation (`OECD (year), AI Incidents and Hazards
Monitor, url (accessed on date)`) regardless of which description it ships.
The `title` field is not covered by the reduction and remains an open
question, tracked at the same posture as the AIAAIC headline question above.
Exact per-row counts and the merge-precedence exceptions: `title`'s in
`NOTICE-DATA`; `description`'s in `docs/SOURCE_LICENSES.md`'s OECD AIM
summary-of-outcomes row (§1.5 covers the full licensing analysis), in the
source repository.

## Links

- **Code & issues:** <https://github.com/emmanuelgjr/genai_incidents>
- **Field reference:** [`docs/DATA_DICTIONARY.md`](https://github.com/emmanuelgjr/genai_incidents/blob/main/docs/DATA_DICTIONARY.md)
- **Provenance, scope & limitations:** [`docs/DATASHEET.md`](https://github.com/emmanuelgjr/genai_incidents/blob/main/docs/DATASHEET.md)
- **Citation:** [`CITATION.cff`](https://github.com/emmanuelgjr/genai_incidents/blob/main/CITATION.cff) · DOI [10.5281/zenodo.20248675](https://doi.org/10.5281/zenodo.20248675) (Zenodo concept DOI, always resolves to the latest release)

**Licence:** data **CC-BY-4.0** (see Licensing above for row-level AIAAIC obligations), code MIT.
"""


def build(out_dir: Path) -> tuple[int, Path]:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "incidents.jsonl"
    with jsonl.open("w", encoding="utf-8", newline="\n") as fh:
        for inc in incidents:
            fh.write(json.dumps(inc, ensure_ascii=False, sort_keys=True) + "\n")
    n = len(incidents)
    size_cat = ("n<1K" if n < 1_000 else "1K<n<10K" if n < 10_000
                else "10K<n<100K" if n < 100_000 else "100K<n<1M")
    card = CARD.format(count=f"{n:,}", version=raw.get("version", "?"),
                       size_cat=size_cat, repo="emmanuelgjr/genai-incidents")
    (out_dir / "README.md").write_text(card, encoding="utf-8", newline="\n")
    return len(incidents), jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="upload to the Hugging Face Hub")
    ap.add_argument("--repo", default="emmanuelgjr/genai-incidents")
    args = ap.parse_args()

    n, jsonl = build(OUT)
    print(f"[hf] wrote {n} records -> {jsonl} (+ README.md)")

    if args.push:
        import os
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("[hf] HF_TOKEN not set; skipping upload", file=sys.stderr)
            sys.exit(1)
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        # Only create the repo if it doesn't exist yet. Calling create_repo on
        # every publish (even with exist_ok=True) hits HF's repo-create rate
        # limit and 429s on repeated/automated runs; the lightweight existence
        # check avoids that. upload_folder uses separate, higher limits.
        if not api.repo_exists(args.repo, repo_type="dataset"):
            api.create_repo(args.repo, repo_type="dataset")
        api.upload_folder(folder_path=str(OUT), repo_id=args.repo, repo_type="dataset")
        print(f"[hf] pushed to https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()
