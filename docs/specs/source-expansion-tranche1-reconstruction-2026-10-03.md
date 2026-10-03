# Source-expansion tranche 1: reconstruction record

**Dated record, 2026-10-03. Do not regenerate.** (Working agreement 4.)

## Why a reconstruction

The user's tranche-2 brief (2026-10-02) referred to "the first ten" sources.
On 2026-10-03 the user asked the foreman to search for those names again and,
if they were not found, to find a solution.

**What was searched, and what turned up.** None of the following holds the
tranche-1 list:

- every local and origin git ref, across all file types;
- all 11 Claude Code transcripts for this project, including subagent transcripts;
- the project memory directory;
- published artifacts;
- Gmail. The only "huntr" hits are an unrelated job-search newsletter (huntr.co). Project mail is limited to AIRI, AIAAIC and the RAI Collaborative outreach.
- Google Drive. The only matches are OWASP documents.

The list was most likely a chat-only deliverable lost at a session boundary,
the failure that working agreement 1 describes.

**The solution adopted.** Reconstruct tranche 1 from evidence internal to the
user's own tranche-2 brief. Label each name with its basis. Evaluate the
reconstructed names under the same discipline as tranche 2.

**The user may amend this list at any time.** A name the user supplies
replaces a reconstructed one. The reconstructed rows are never presented as
the user's original ten.

## Basis

The tranche-2 brief is explicitly the **worldwide** tranche. Each of its
categories is phrased as the non-US or second-route counterpart of something,
which implies tranche 1 held the US, industry-side counterparts:

| Tranche-2 phrasing | Implied tranche-1 counterpart |
|---|---|
| "Government/CERT … NCSC, ACSC, CCCS, ENISA, … CERT-EU" | US government/CERT: CISA beyond KEV (named by the user); CERT/CC Vulnerability Notes |
| "Regulators/courts … BAILII/CanLII for **non-US** AI litigation" | US AI litigation: CourtListener / RECAP |
| "Regulators … Garante, EDPB, ICO, ANPD, OPC" (none US) | US regulator: FTC enforcement actions |
| "Research/disclosure … HackerOne, Bugcrowd" | AI-specific bug-bounty disclosure: huntr (named by the user); 0din (Mozilla GenAI bounty) |
| "VulnCheck KEV (enriches exploited_in_wild)" | exploit-likelihood enrichment: FIRST EPSS |
| "cvelistV5 upstream of NVD" | supply-chain malicious-artifact feeds: OpenSSF malicious-packages (OSV `MAL-` ids) |
| AI model-hub risk (absent from tranche 2) | model-hub security disclosures: Hugging Face security advisories / malicious-model reports |

## Tranche 1, reconstructed (10)

| # | Source | Status |
|---|---|---|
| T1.1 | CISA beyond KEV | **named by the user**; pre-row exists (1E.2) |
| T1.2 | huntr | **named by the user**; pre-row exists (1E.1) |
| T1.3 | CERT/CC Vulnerability Notes (kb.cert.org / VINCE) | reconstructed |
| T1.4 | CourtListener / RECAP (US AI litigation) | reconstructed |
| T1.5 | FTC enforcement actions involving AI | reconstructed |
| T1.6 | 0din (Mozilla GenAI bug-bounty disclosures) | reconstructed |
| T1.7 | FIRST EPSS (enrichment only) | reconstructed |
| T1.8 | OpenSSF malicious-packages (AI/ML ecosystem subset) | reconstructed |
| T1.9 | Hugging Face security advisories / malicious-model disclosures | reconstructed |
| T1.10 | GitHub Security Lab advisories (GHSL, AI/ML repos) | reconstructed |

GHSA, OSV, NVD, CISA KEV, MITRE ATLAS and the vendor threat reports are
already ingested (`docs/SOURCE_LICENSES.md`), so they were excluded as
candidates.

**Waves 1 and 2 (user-approved 2026-10-03) do not depend on this list.** The
reconstructed names are evaluated in parallel and ranked into later waves.
