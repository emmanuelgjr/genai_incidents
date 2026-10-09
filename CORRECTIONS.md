# Corrections log

A public, append-only record of accepted data corrections and removals — what
changed, why, and the evidence. An authoritative dataset is one you can
*correct*; this log makes every correction transparent and auditable.

How to propose one: open a [Data correction](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=data_correction.yml)
or [Scope dispute](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=scope_dispute.yml)
issue. Accepted changes are applied via PR and logged here. Removed incident IDs
are also recorded in [`data/id_deprecations.json`](data/id_deprecations.json) so
old citations still resolve.

| Date | Change | Scope | Reason | Evidence / PR |
|------|--------|-------|--------|---------------|
| 2026-10-06 | Corrected the MITRE ATLAS pin: `AML.T0009`, `AML.T0030`, `AML.T0038`, `AML.T0045` marked `deprecated` | mapping fix | The pin had listed these four ids as part of ATLAS "2026.06". ATLAS 2026.06 does not contain them (nor do 2025.12, 2026.01 or 2026.09; checked against the upstream release YAMLs). Retained in `mappings/mitre_atlas.json` as deprecated (never deleted); the corpus carried none of them. | v2.13.0 (`CHANGELOG.md` [Unreleased] → 2.13.0); `docs/audits/atlas-refresh-2026.09-release-diff.md`; `docs/audits/atlas-refresh-delta-2026-10-06.md` |
| 2026-10-06 | `INC-06842` (AVID-2023-V012): ATLAS technique `AML.T0015.001` replaced by `AML.T0015` | mapping fix | `AML.T0015.001` is not defined in ATLAS 2026.06 or 2026.09 (phantom subtechnique id, a pre-existing AVID-ingest defect surfaced by the new `lint_atlas_ids.py`). The entry's `updated`/`last_seen` moved with it; no other field. | v2.13.0 ATLAS refresh; per-entry record in `docs/audits/atlas-refresh-delta-2026-10-06.md` |
| 2026-06-11 | **Removed ~800 out-of-scope `malicious-package` entries** (e.g. `chai-mocks`, `sudo-prompt`, `nemo-reporter`) | bulk removal | Generic npm malware matched on weak substrings (`ai`, `prompt`, `nemo`); not AI incidents per [INCLUSION.md](INCLUSION.md). malicious-package 465 → 61. | PR #63 (v2.3.1); recorded as `out-of-scope` removals in `id_deprecations.json` |
| 2026-06-10 | Removed `CVE-2026-35020` | single removal | CNA-rejected (withdrawn from NVD). | v2.2.0 enrichment |
| 2026-06-10 | Removed MITRE ATLAS technique `AML.T0039` | mapping fix | Phantom technique — never existed in any ATLAS release (duplicated T0048). | PR #26 |

_Newest first. Each row links to the PR and, for removals, the deprecation record._
