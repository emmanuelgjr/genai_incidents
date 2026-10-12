# Inclusion Policy — what belongs in this dataset

This document defines, precisely, what counts as an entry in
`genai_incidents`. It is the authoritative scope contract: ingesters,
filters, reviewers, and contributors all decide in/out against **this page**,
not against keyword lists. It exists because a permissive keyword filter once
admitted ~330 generic-malware records that were not AI incidents — scope must
be a written definition, not an accident of substring matching.

/ status: **active** · applies from v2.3.1 · changes require a PR + changelog entry /

---

## 1. Definition

> A **GenAI / agentic-AI security incident** is a real-world event, disclosed
> vulnerability, or documented attack technique in which an **artificial
> intelligence system — generative model, agent, or its supporting ML
> infrastructure — is the target, the vector, or a material enabler of harm.**

An entry must satisfy **all three** gates:

1. **AI-nexus.** The incident materially involves an AI/ML system: an LLM or
   generative model; an autonomous/agentic system; or the AI/ML
   infrastructure that builds, serves, or secures them (training pipelines,
   model registries, inference servers, vector stores, agent frameworks, MCP
   servers, RAG stacks). *Incidental* mention of "AI" is not an AI-nexus.
2. **Security or safety relevance.** It describes a vulnerability, exploit,
   attack, misuse, or real-world harm — not a feature, benchmark, or routine
   release.
3. **Evidence.** It resolves to **at least one primary source** (advisory,
   CVE/GHSA record, vendor report, paper, news article, court/regulatory
   filing). No entry without a citable source.

If any gate fails, the record is **out of scope** regardless of how many
keywords it matched.

---

## 2. In scope (with examples)

| Class | Example |
|---|---|
| Attacks on/through LLMs | Prompt injection, jailbreaks, indirect injection via RAG, data exfiltration through a model |
| Agentic-AI exploits | Tool/function-call abuse, autonomous-agent privilege escalation, MCP-server vulns |
| AI/ML supply-chain | A CVE/GHSA in `langchain`, `vllm`, `ollama`, `mlflow`, `comfyui`, `transformers`, an MCP server, etc. |
| **AI-ecosystem malicious packages** | A typosquat of `openai`/`langchain`/`@huggingface/*` (must match a real AI package — see §4) |
| Model/data poisoning | Backdoored model on a hub, poisoned training/RAG corpus |
| Real-world AI harms | Deepfake fraud, model-driven disinformation, harmful generated content, biased automated decisions causing harm |
| AI-relevant CVEs | A CVE whose affected product is an AI/ML tool, or whose vector is AI-specific |

## 3. Out of scope (with examples)

| Not included | Why / example |
|---|---|
| Generic software vulns with no AI nexus | A CVE in a logging lib, even if used by an AI app |
| **Generic malicious packages** | `chai-mocks`, `sudo-prompt`, `nemo-reporter` — npm malware matched only by an incidental substring (`ai`, `prompt`, `nemo`); **not** AI tooling |
| AI *capabilities/benchmarks* | "Model X scores Y on benchmark Z" — not a security event |
| Routine releases / advisories without an incident | A model launch, a non-security advisory |
| Pure policy/opinion with no incident | Op-eds about AI risk that don't describe an event |
| Impersonation-by-name only | A package literally named `claude`/`gpt` with no evidence it targets that ecosystem |

---

## 4. The relevance bar filters MUST enforce

Automated ingest is **precision-first**. Specific rules:

- **Malicious-package (GHSA MALWARE) advisories** are admitted **only** when
  the package name strongly matches a curated AI package/scope as a
  **delimited segment** — never a raw substring, and never via description
  text alone. (`@langchain/x`, `vllm`, `comfyui-x` → in; `chai-mocks`,
  `breezeai-frontend` → out.) Implemented as `package_is_strongly_ai` /
  `ghsa_malware_is_ai` in `scripts/ingest_cve_nvd_expanded.py`.
- **CVE / GENERAL advisories** may use the broader AI package + context-token
  match, because a real CVE with an affected AI product carries its own
  evidence.
- Weak, dictionary-word, or short tokens (`ai`, `ml`, `nemo`, `ray`,
  `prompt`, `agent`, `guidance`) must **never** be used as standalone
  substring matches — they are the documented cause of false positives.
- **Relevance is measured by a dated precision audit, not by a per-change
  gate.** No CI check samples or audits the entries an ingest change adds.
  For relevance, CI runs the filter rules' unit tests (e.g.
  `tests/test_ingest_cve.py`, `tests/test_ingest_wave12.py`); the rest of CI
  checks schema, count and dedup integrity, not relevance. What exists is one
  pinned, dated audit: `scripts/precision_sample.py` draws a seeded,
  stratified sample of the published corpus, a human labels it in scope
  or out of scope against §1, and `scripts/wilson_ci.py` computes precision
  with a Wilson interval
  ([`docs/audits/precision/2026-10-11/`](docs/audits/precision/2026-10-11/)).
  `scripts/validate.py::check_precision_audit` checks that audit's integrity:
  pinned sample and frame, published figure derived from human labels only,
  and a user authorisation while the measurement is pending. It does not
  look at new ingest changes and sets no precision floor. A new ingest
  source should still be sample-audited for relevance by its reviewer before
  merge; that is review practice, not an enforced gate.

  *Corrected 2026-10-11 (ruling D75): this bullet previously said every ingest
  change that adds entries "must be sample-audited for relevance before
  merge" and pointed to "the CI gate". No such gate has existed, and
  `scripts/precision_sample.py` did not exist until 2026-10-11. See
  [CORRECTIONS.md](CORRECTIONS.md).*

---

## 5. Tiers

The dataset has two layers, surfaced explicitly so consumers can choose. The
layer is the **`tier`** field. It is derived on every build by
`scripts/merge_and_dedupe.py::_derive_tier`, which is the definition of
record:

- **Landmark** (`tier: landmark`) is the notable headline set. A row is
  landmark if it is hand-curated (`quality_tier: curated`), **or** is
  catalogued in the AI Incident Database (`aiid_id` present), **or** is an
  AI-harm case (`corpus: ai-harm`).
- **Comprehensive feed** (`tier: feed`) is every other row. It is mainly the
  broad CVE/GHSA/OSV vulnerability and advisory stream, plus `security`-corpus
  rows from other sources such as OECD. High recall, lighter review.

**`tier` is not `quality_tier`.** `quality_tier` (`curated` / `reviewed` /
`auto`) is a separate vetting axis, defined in
[`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md), and neither field can
be reconstructed from the other. The feed is **not** the `auto` layer: most
feed rows are `quality_tier: reviewed` (for example, NVD-scored CVEs are
labelled `reviewed`), and some landmark rows are `quality_tier: auto`. In the
data as published at v2.12.0, excluding the 29 `status: retracted` rows:

| `tier` | `auto` | `reviewed` | `curated` | Total |
|---|---:|---:|---:|---:|
| feed | 4,227 | 9,495 | 0 | 13,722 |
| landmark | 185 | 1,611 | 119 | 1,915 |

So 69% of the feed is `reviewed`. `reviewed` means a maintained catalogue,
an NVD-scored CVE, a hand-picked row or a human/assisted review; it does not
mean that a human checked each row against §1. Re-derive the table:

```
python -c "import json,collections; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; c=collections.Counter((e.get('tier'),e.get('quality_tier')) for e in d if e.get('status')!='retracted'); print(sorted(c.items(), key=str))"
```

Headline claims should cite the landmark count (`landmark_count` in
[`data/stats.json`](data/stats.json)), not the raw total. Conflating the two
is how a count can look larger than the dataset's true authority.

*Corrected 2026-10-11 (ruling D75): this section previously defined landmark
as `quality_tier: curated` / `reviewed` and the feed as `quality_tier: auto`.
That was false: the split is `tier`, and most of the feed is `reviewed`. It
also said to cite "the curated set", which is 119 rows, not the landmark
count. See [CORRECTIONS.md](CORRECTIONS.md).*

---

## 6. Edge cases & judgement

- **Dual-use tools** (e.g. a CVE in `gradio`, used well beyond AI): in scope —
  it is AI/ML infrastructure.
- **Pre-LLM algorithmic harms** (AIAAIC/OECD): in scope as *AI harms* but
  flagged via `corpus: ai-harm`; don't conflate with `security`.
- **Borderline AI-nexus**: when unsure, require a **second** signal (e.g. a
  real AI product in `affected` **and** an AI-specific attack vector) before
  admitting at `quality_tier: auto`; otherwise exclude and open a discussion.

Disagreements are resolved by PR against this document — the policy is
versioned, public, and correctable like the data itself.
