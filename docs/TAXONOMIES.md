# Taxonomies

This dataset maps incidents to six taxonomies: four core (OWASP LLM Top 10 2026, OWASP Agentic ASI Top 10, NIST AI RMF, MITRE ATLAS), a companion MAESTRO architectural-layer mapping, and an experimental VERIS 1.4.1 crosswalk. They don't compete — they describe **different facets** of the same incident.

## Quick chooser

| Question | Use |
|---|---|
| What kind of failure is this at the LLM layer? | **OWASP LLM Top 10** |
| What kind of failure is this at the agent layer? | **OWASP Agentic Top 10 (ASI)** |
| What organizational risk function should respond? | **NIST AI RMF** |
| What adversary tactic/technique was used? | **MITRE ATLAS** |
| Where in the architecture did it originate / impact? | **MAESTRO** (companion) |
| Does response get paged or queued — could the closing action be undone? | **Reversibility class** (landmark tier) |
| Which detection investment surfaced it? | **Discovery method** (landmark tier) |

---

## OWASP Top 10 for LLM Applications (2026)

Source: <https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/> · canonical text: <https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final>

Failure-mode catalog focused on LLM-based applications regardless of agency.

| Code | Name | 2025 code |
|---|---|---|
| LLM01 | Prompt Injection | LLM01 |
| LLM02 | Sensitive Information Disclosure | LLM02 |
| LLM03 | Excessive Agency | LLM06 |
| LLM04 | Supply Chain | LLM03 |
| LLM05 | Data and Model Poisoning | LLM04 |
| LLM06 | Unbounded Consumption | LLM10 |
| LLM07 | Misinformation | LLM09 |
| LLM08 | Hidden Context Exposure | LLM07 (*System Prompt Leakage*) |
| LLM09 | Vector and Embedding Weaknesses | LLM08 |
| LLM10 | Improper Output Handling | LLM05 |

**Use it when:** the incident involves an LLM API, RAG system, or LLM-backed feature — even if the system has no agent loop.

> **Reading data published before 2026-08-17.** The 2026 edition reuses the same
> code space (`LLM01`–`LLM10`) with **different meanings**, so a bare `LLM03` is
> ambiguous unless you know which edition produced it. Releases up to and
> including **v2.9.0** (and their Zenodo DOIs) carry **2025** codes; every release
> after that carries 2026 codes. The third column above is the crosswalk, also
> available machine-readable at
> [`mappings/owasp_llm_2025_to_2026.json`](../mappings/owasp_llm_2025_to_2026.json),
> with the retired catalog kept at
> [`mappings/owasp_llm_top10_2025.json`](../mappings/owasp_llm_top10_2025.json).
>
> The migration renumbered codes only. Several 2026 entries **widened their
> scope** (LLM08 now covers all non-user-facing context, not just the system
> prompt; LLM01 covers cross-modal injection; LLM10 covers insecure generated
> code). Incidents that would newly qualify under a widened entry were **not**
> added — that is annotation work, not renumbering. See
> [the migration delta](audits/owasp-llm-2026-migration-delta-2026-08-17.md).

---

## OWASP Agentic Top 10 (ASI)

Source: <https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/>

Failure-mode catalog focused on **agentic** systems — agents with planning loops, tool use, memory, and inter-agent communication.

| Code | Name |
|---|---|
| ASI01 | Agent Goal Hijack |
| ASI02 | Tool Misuse & Exploitation |
| ASI03 | Identity & Privilege Abuse |
| ASI04 | Agentic Supply Chain Vulnerabilities |
| ASI05 | Unexpected Code Execution (RCE) |
| ASI06 | Memory & Context Poisoning |
| ASI07 | Insecure Inter-Agent Communication |
| ASI08 | Cascading Failures |
| ASI09 | Human-Agent Trust Exploitation |
| ASI10 | Rogue Agents |

**Use it when:** the system exhibits agentic properties — tool invocation, autonomous planning, memory, or multi-agent orchestration. Don't force-fit ASI codes onto purely-LLM incidents.

---

## NIST AI Risk Management Framework (AI 100-1)

Source: <https://www.nist.gov/itl/ai-risk-management-framework>

Risk-management framework, not a failure catalog. Four functions:

| Function | Description |
|---|---|
| GOVERN | A culture of risk management is cultivated and present |
| MAP | Context and risks related to context are identified |
| MEASURE | Risks are assessed, analyzed, or tracked |
| MANAGE | Risks are prioritized and acted upon |

Each function has subcategories with stable identifiers (e.g., `MEASURE-2.7` "AI system security and resilience are evaluated and documented").

**Use it when:** you want to surface **which control area should have caught or contained** the incident. For an indirect prompt injection that exfiltrates data: `MEASURE-2.7` (security testing missed this), `MAP-2.1` (the deployment context wasn't well-understood), `MANAGE-2.3` (no incident-response procedure).

A companion **AI 600-1 Generative AI Profile** maps GenAI-specific risks to the same subcategory IDs — see <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>.

---

## MITRE ATLAS

Source: <https://atlas.mitre.org/>

Adversary-centric taxonomy of tactics and techniques against ML/AI systems, modeled after MITRE ATT&CK. Tactics use `AML.TA00xx` IDs; techniques use `AML.T00xx` (with optional `.NNN` subtechnique suffix).

Key LLM-era techniques used heavily in this dataset:

| Technique | Name |
|---|---|
| `AML.T0010` | AI Supply Chain Compromise |
| `AML.T0018` | Manipulate AI Model |
| `AML.T0020` | Poison Training Data |
| `AML.T0024` | Exfiltration via AI Inference API |
| `AML.T0048` | External Harms |
| `AML.T0051` | LLM Prompt Injection (`.000` Direct, `.001` Indirect, `.002` Triggered) |
| `AML.T0053` | AI Agent Tool Invocation |
| `AML.T0054` | LLM Jailbreak |
| `AML.T0056` | Extract LLM System Prompt |
| `AML.T0057` | LLM Data Leakage |
| `AML.T0066` | Retrieval Content Crafting |
| `AML.T0070` | RAG Poisoning |

**Use it when:** you want to communicate the incident in adversarial-emulation terms — what an attacker is **doing**, not what is **broken**.

See `mappings/mitre_atlas.json` (pinned at ATLAS v2026.09; the machine-readable value is `taxonomy_versions.atlas` in `data/stats.json`) for the full technique list used here.

---

## MAESTRO architectural layers (companion)

Source: <https://genai.owasp.org/resource/genai-security-project-maestro/>

Companion model that describes **where in the AI/agent architecture** an incident originates, impacts, or could be controlled. Used by the legacy `incidents.json` source and preserved on those entries.

| Layer | Name |
|---|---|
| L1 | Foundation Models |
| L2 | Data Operations |
| L3 | Agent Frameworks & Tooling |
| L4 | Deployment & Infrastructure |
| L5 | Evaluation & Observability |
| L6 | Security & Compliance |
| L7 | Human Factors & UX |

The `role` field on a MAESTRO mapping indicates whether the layer was the `origin`, `impact`, `blind-spot`, `control`, `amplifier`, or `propagation` vector.

---

## Reversibility class

Proposed in [#74](https://github.com/emmanuelgjr/genai_incidents/issues/74) (lineage: OWASP AISVS C09-02 reversibility-classification gating). Severity says how bad; `reversibility_class` says whether incident response gets **paged or queued** — the same attack vector routes very differently depending on what the closing action could undo.

Four **ordered** classes, least → most severe:

| Rank | Class | Meaning |
|---|---|---|
| 1 | `read-only` | No state mutation — the agent observed, read, summarized, or inferred but did not act on external systems. |
| 2 | `reversible` | Mutation undoable in-session or by trivial in-system action (file recoverable from trash, internal-only draft). |
| 3 | `external-reversible` | Mutation undoable only via an external compensating action (refund, retraction, correction outreach, manual cleanup). |
| 4 | `irreversible` | No compensating action possible (unrecoverable deletion, funds transferred, content published and indexed). |

Scope rules (precision-over-coverage):
- **Landmark tier only** — enforced as a `validate.py` integrity invariant. `tier` is re-derived each build, so a labeled entry drifting out of the landmark set fails CI rather than shipping a stale judgment.
- **Evidence-gated** — assigned via `data/curation_overrides.json` only where the source evidence describes the closing action, with evidence and review date in the override `_note`. Feed/auto entries stay empty rather than guessing.
- **Absence means unassessed, not `read-only`.**
- The JSON-schema enum carries no order — consumers must rank explicitly (alphabetical sorting puts `irreversible` between the two reversible classes).

Boundary rules (settled in [#74](https://github.com/emmanuelgjr/genai_incidents/issues/74) on INC-03152, the Replit prod-DB deletion):
- **Realized outcome, not intrinsic risk.** Classes describe what the closing action could actually undo per the documented outcome: `irreversible` requires that *no compensating action was possible* — an action that succeeded rules it out, however catastrophic the mutation could have been. Counterfactual severity is already carried by `severity` and `attack_vector`; misleading recoverability claims by the agent belong in the `_note` evidence.
- **Vantage point is the acting agent's session, not the vendor's infrastructure.** `reversible` is reserved for undo available within the acting system's own session or controls and trivially exercised (trash restore, unsent internal draft). Ask **"who had to act?"** — if recovery needed anyone or anything outside the acting agent's session (a human operator, vendor tooling, backups), it is `external-reversible`, even when the tooling is platform-native.

---

## Discovery method

Lineage: [VERIS 1.4.1](https://github.com/vz-risk/veris) `discovery_method`, flattened from its external/internal/partner varieties and AI-adapted (`media-report` has no VERIS parent — journalist investigations surface many AI incidents). Severity says how bad, reversibility says paged-or-queued; `discovery_method` says **which detection investments actually surface GenAI incidents** — e.g. how many landmark incidents were found by external researchers versus the operator's own telemetry.

| Value | Meaning (VERIS parent) |
|---|---|
| `security-researcher` | External researcher / bug bounty (Ext — Security researcher) |
| `actor-disclosure` | The attacker announced, leaked, or extorted (Ext — Actor disclosure) |
| `customer-report` | Affected user or customer reported it (Ext — Customer) |
| `media-report` | Journalist or media investigation surfaced it (AI adaptation) |
| `law-enforcement` | Law enforcement or regulator notified the operator (Ext — Law enforcement) |
| `internal-monitoring` | Operator telemetry: logs, guardrails, anomaly detection (Int — Log review / monitoring) |
| `internal-report` | Reported by an employee or insider (Int — Reported by employee) |
| `vendor-monitoring` | Platform or model-provider abuse detection (Partner — Monitoring service) |
| `other` | Known channel not listed above |

Scope rules — identical to [Reversibility class](#reversibility-class): **landmark tier only** (validate.py integrity invariant), **evidence-gated** via `data/curation_overrides.json` (the source must state the discovery channel; evidence + review date in the override `_note`), and **absence means unassessed, not internally detected**.

---

## VERIS crosswalk (export-only)

Source: <https://github.com/vz-risk/veris> (VERIS 1.4.1 — the incident vocabulary behind the Verizon DBIR and VCDB)

Not a per-incident schema field: a hand-curated crosswalk in [`mappings/veris.json`](../mappings/veris.json) from the controlled `attack_vector` vocabulary to VERIS enum paths, emitted as `veris:*` machinetags in the MISP feed (`scripts/export_misp.py`). Anchored on VERIS 1.4.1's GenAI enums (`action.hacking.variety` "Prompt injection", asset "S - LLM application"). It makes incidents legible to DBIR-contributor and risk-quantification consumers without adding schema surface.

Curation rules: closest defensible enum only — values with no honest VERIS equivalent (`algorithmic-bias`, `adversarial-input`, `other`) stay unmapped; the LLM-application asset tag is attached only to vectors that by definition target an LLM/agent app. Deliberately **not** derived by chaining ATLAS→ATT&CK→VERIS: only ~20% of ATLAS techniques have ATT&CK anchors, and none of the AI-native ones do.

**Use it when:** consuming the MISP feed alongside VERIS-coded corpora (DBIR, VCDB) or FAIR-style risk tooling. Note MISP's bundled `veris` taxonomy predates VERIS 1.4.1, so the AI-specific tags render as plain tags until upstream refreshes it.

---

## How they map to each other

The frameworks overlap deliberately. A single incident often hits **several** codes across taxonomies. Example: ShadowLeak (zero-click ChatGPT Deep Research data exfiltration).

| Taxonomy | Mapping for ShadowLeak |
|---|---|
| OWASP LLM | `LLM01` (indirect prompt injection), `LLM02` (sensitive info disclosure), `LLM03` (excessive agency through connectors) |
| OWASP ASI | `ASI01` (goal hijack), `ASI02` (tool misuse — connectors), `ASI09` (human-agent trust exploitation) |
| NIST AI RMF | `MEASURE-2.7` (security testing gap), `MAP-3.5` (human oversight), `GOVERN-6.1` (third-party connector risk) |
| MITRE ATLAS | `AML.T0051.001` (LLM Prompt Injection — indirect), `AML.T0057` (LLM Data Leakage), `AML.T0048` (External Harms) |
| MAESTRO | `L3` origin (connectors), `L5` blind-spot (no telemetry to catch this), `L6` impact (compliance/data) |

Don't pick favorites. Use them together.
