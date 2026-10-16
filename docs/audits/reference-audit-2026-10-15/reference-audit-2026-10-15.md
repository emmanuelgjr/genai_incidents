# D130-2: legacy-seed reference remediation, 2026-10-15

**Agent-suggested, not human-reviewed.** Every replacement below is pending the user's re-review; every demoted row
carries a curation-override note saying so. Scope: the 30 legacy-seed rows (source_ids `INC-<n>` / `LEGACY-INC-<n>`) that trip
R1 or R2 of `docs/audits/reference-detection-2026-10-14.md` (user ruling D130, 2026-10-14). No third-party page text is copied
here beyond titles and the short tokens used to link a fetched page to the entry.

Method: each URL written into the corpus was fetched in this session through `ingest/common.fetch_once` (robots, per-host rate
limit, identifying User-Agent) by `fetch_evidence.py`, and its page text was checked for the row-linking tokens listed per row
(`export_evidence.py` re-checks every token and aborts if one is missing; it was seen to fail on a wrong token during this work).
Discovery used web search tools outside the corpus path; discovery results are never written into the corpus unless the page was
then fetched through `common.py`. All changes are `data/curation_overrides.json` entries generated from `d1302_spec.py` by
`build_overrides.py`; `data/incidents.json` is a build output and was not edited.

## Outcome

| outcome | rows | by original quality_tier |
|---|---|---|
| fixed (reference replaced/removed, description re-derived, demoted to auto) | 11 | curated 4, reviewed 7 |
| unverified (`status: unverified`, no-confirmed-source) | 10 | reviewed 10 |
| examined, not changed: false positive / merge artifact | 3 | curated 3 |
| deferred: mechanism gap (feed-merged CVE/GHSA rows; a whole-list `references` override would freeze them) | 5 | curated 5 |
| deferred: ruling (c) demotion collides with the validate.py landmark-label gate | 1 | curated 1 |
| **total** | **30** | |

Rows whose `description` changed (11): INC-02454, INC-02774, INC-02899, INC-03004, INC-03472, INC-03955, INC-03972, INC-04179, INC-04221, INC-04653, INC-04955.

Re-derivation of the 30: the detection report's `r1`/`r2` definitions (its Appendix A) applied to the rows of `data/incidents.json` at
589376db that carry an `INC-<n>`/`LEGACY-INC-<n>` source_id give 30 rows (13 curated, 17 reviewed), equal to the report's count.
The list is the union of the five outcome groups above. Command: `python -I docs/audits/reference-audit-2026-10-15/derive_list.py`.

## Field-level delta (working agreement 2)

Base 589376db vs this branch's build: entry count 15784 -> 15784; ID set equal: True; rows with any difference: 21 (= 11 fixed + 10 unverified); rows outside those with any difference: 0.
Envelope: `generated` 2026-10-13 -> 2026-10-16; `incident_count` 15755 -> 15745; `unverified_count` 0 -> 10. (`generated` is the build date stamp.)
Headline counts in `data/stats.json` (and the doc surfaces templated from it, e.g. the README cells) that moved: `generated` 2026-10-13 -> 2026-10-16; `incident_count` 15755 -> 15745; `landmark_count` 2028 -> 2025; `unverified_count` 0 -> 10; stats keys outside this declared set: 0.
- `incident_count` -15,755 -> 15,745: exactly the 10 unverified rows (INC-02353, INC-02703, INC-02922, INC-03247, INC-03444, INC-03447, INC-03491, INC-03570, INC-03810, INC-04310); `unverified_count` 0 -> 10.
- `landmark_count` 2028 -> 2025: the 3 curated rows demoted to auto that leave the landmark tier (INC-02774, INC-02899, INC-04179); INC-02454 is also demoted but its corpus is pinned to `ai-harm` (base value), which keeps it landmark. No unverified row is landmark.
- `generated` is the build date stamp. `retracted_count`, `disputed_count`, version and year range are unchanged.

Full per-row before/after: `delta-2026-10-15.json`. Enumerated fields:

| field | rows | kind | justification |
|---|---|---|---|
| `affected` | 11 | intended | restated the dropped figures/claims; rewritten from the same source |
| `confidence` | 11 | derived | `_derive_confidence`: curated/reviewed -> high; a single auto-tier source with no CVE -> low/medium. Follows quality_tier only |
| `description` | 11 | intended | re-derived from the fetched source; unsupported figures dropped |
| `impact` | 11 | intended | restated the dropped figures/claims; rewritten from the same source |
| `last_seen` | 21 | derived | history stamp: content changed (build date) |
| `quality_tier` | 11 | intended | ruling D130(c): every replaced reference demotes to auto; never promoted |
| `references` | 11 | intended | the D130-2 change itself |
| `status` | 10 | intended | D130(b)/D130-1: unverified |
| `status_reason` | 10 | intended | D130-1: {code: no-confirmed-source, as_of: 2026-10-15} |
| `tier` | 3 (INC-02774, INC-02899, INC-04179) | derived | `_derive_tier`: curated -> landmark; demoted curated rows without aiid_id / ai-harm corpus become feed. Follows quality_tier only |
| `title` | 7 | intended | title asserted claims the confirmed source does not support (bounce #1 defect 3); re-derived from the source so title and description agree |
| `updated` | 21 | derived | history stamp: content changed (build date) |

Derived-field coupling (the WS0-T3 trap, `docs/audits/WS0-T3-cascade-2026-07-18.md`): classifiers that read `description`/`title` run BEFORE the
step-4d curation override, so `attack_vector`, `severity`, `owasp_*`, `nist_ai_rmf`, `mitre_atlas*`, `maestro_layers`, `category` and `tags`
keep their base values for every row (the delta shows none moved). One classifier output is re-derived AFTER the override: `corpus`.
For INC-02454 the corrected text flipped `corpus` from `ai-harm` to `security` in a trial build; that is a classifier artifact of the new wording, not a ruling,
so the override pins it to the base value `ai-harm` (`pin` in the spec) and the delta shows no `corpus` change. Consequence: the mapping fields still describe the
OLD wording on the rows whose description changed; they are not re-derived here (re-labelling is label-scientist's call; listed as a follow-up).

## Per-row evidence

### INC-01015 - DEFERRED (mechanism gap)

- legacy ids: INC-113, LEGACY-INC-00159, LEGACY-INC-00218; quality_tier at base: curated; title: Flowise v3.0.1 < 3.0.8 and all versions after with 'ALLOW_BUILTIN_DEP' enabled contain an authenticated remote code execution vulnerability and node VM sandbox escape due to ins...
- references at base: https://nvd.nist.gov/vuln/detail/CVE-2025-34267 (advisory); https://flowiseai.com (reference); https://github.com/FlowiseAI/Flowise/pull/5231 (reference); https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5w3r-f6gm-c25w (vendor); https://www.vulncheck.com/advisories/flowise-auth-command-execution-and-sandbox-bypass-via-puppeteer-and-playwright-packages (advisory); https://github.com/advisories/GHSA-r4hh-pcgx-j5r2 (advisory); ... 443 in total
- flagged reference(s) and what they were: flowiseai.com: vendor homepage (R1)
- reason deferred: flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL override is a new mechanism and was not invented. Row left unchanged.
- action: none (row byte-identical to base).

### INC-01291 - DEFERRED (mechanism gap)

- legacy ids: INC-012, LEGACY-INC-00239; quality_tier at base: curated; title: LangChain LLMMathChain prompt-injection RCE via Python exec
- references at base: https://nvd.nist.gov/vuln/detail/CVE-2023-29374 (advisory); https://github.com/advisories/GHSA-fprp-p869-w6q2 (advisory); https://github.com/hwchase17/langchain/issues/1026 (reference); https://github.com/hwchase17/langchain/issues/814 (patch); https://github.com/hwchase17/langchain/pull/1119 (patch); https://twitter.com/rharang/status/1641899743608463365/photo/1 (exploit); ... 178 in total
- flagged reference(s) and what they were: langchain.com/: vendor homepage (R1)
- reason deferred: flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL override is a new mechanism and was not invented. Row left unchanged.
- action: none (row byte-identical to base).

### INC-01589 - DEFERRED (mechanism gap)

- legacy ids: INC-102, LEGACY-INC-00195; quality_tier at base: curated; title: OpenClaw AI agent security crisis — 138 CVEs in 63 days, 341 malicious marketplace skills
- references at base: https://www.reco.ai/blog/openclaw-the-ai-agent-security-crisis-unfolding-right-now (research); https://nvd.nist.gov/vuln/detail/CVE-2026-25253 (advisory); https://depthfirst.com/post/1-click-rce-to-steal-your-moltbot-data-and-keys (exploit); https://ethiack.com/news/blog/one-click-rce-moltbot (exploit); https://github.com/openclaw/openclaw/security/advisories/GHSA-g8p2-7wf7-98mq (vendor); https://openclaw.ai/blog (reference); ... 10 in total
- flagged reference(s) and what they were: openclaw.ai/blog: project blog index (R1)
- reason deferred: flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL override is a new mechanism and was not invented. Row left unchanged.
- action: none (row byte-identical to base).

### INC-02353 - UNVERIFIED

- legacy ids: INC-037; quality_tier at base: reviewed; title: Azure OpenAI content filter bypass via structured output mode
- references at base: https://msrc.microsoft.com/ (research)
- Row cites msrc.microsoft.com/ (MSRC portal homepage, fetched 2026-10-14 title "MSRC - Microsoft Security Response Center").
- Discovery query (Brave): "Azure OpenAI structured outputs content filter bypass JSON schema jailbreak" -> Microsoft Learn structured-outputs/content-filter documentation and two Microsoft Q&A threads about structured responses being blocked by the content filter (the opposite of a bypass); none describes a bypass via JSON-schema field names such as weapon_instructions.
- Outcome: no confirmed source names this incident.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-02454 - FIXED

- legacy ids: INC-036, INC-039; quality_tier at base: curated; title: Clearview AI biometric bias — $50M class action settlement
- references at base: https://www.reuters.com/legal/ (news); https://www.eff.org/ (research)
- flagged reference(s) and what they were: reuters.com/legal/: Reuters section index (R1; robots-refused); eff.org/: EFF homepage (R1)
- query / discovery: Brave via discovery tool: "Clearview AI BIPA class action settlement approved 2025 equity stake 23%" -> natlawreview, regulatoryoversight, iclg, constangy, Miami Law Review (first ten results)
- candidate rejected / note: reuters.com/legal/ = Reuters section index; reuters.com robots.txt refuses our UA, so contents cannot be verified
- candidate rejected / note: eff.org/ = EFF homepage, reference title claimed "AI copyright training data legal analysis" (mismatch)
- candidate rejected / note: en.wikipedia.org/wiki/Clearview_AI (fetched; secondary, says 2024 agreement; not needed)
- candidate rejected / note: Discovery note, UNVERIFIED lead: a search-result snippet reported a July 2026 Seventh Circuit vacatur of the settlement; no fetched source in this session confirms it, so it is NOT in the description
- chosen: https://natlawreview.com/article/first-bipa-litigation-class-members-receive-equity-clearview-ai
  - fetched: HTTP 200; title "BIPA Litigation Class Members Receive Equity in Clearview AI"; fetched_at 2026-10-15T11:31:00Z; sha256 ee7c83982557a288...; publication date is in the reference title
  - matched tokens linking the page to the entry: Clearview, BIPA, 23% equity stake, March 20, 2025, 60 billion
- chosen: https://www.regulatoryoversight.com/2025/04/51-75m-settlement-in-clearview-ai-biometric-privacy-litigation-illustrates-creative-resolution-for-startups-facing-parallel-litigation-and-enforcement-action/
  - fetched: HTTP 200; title "$51.75M Settlement in Clearview AI Biometric Privacy Litigation Illustrates Creative Resolution for Startups Facing Parallel Litigation and Enforcement Action | Regulatory Oversight"; fetched_at 2026-10-15T11:31:06Z; sha256 d22dd4ff25664e51...; publication date is in the reference title
  - matched tokens linking the page to the entry: Clearview, $51.75 million, 23% equity stake, BIPA
- references after (each fetched this session; see the evidence table): https://natlawreview.com/article/first-bipa-litigation-class-members-receive-equity-clearview-ai; https://www.regulatoryoversight.com/2025/04/51-75m-settlement-in-clearview-ai-biometric-privacy-litigation-illustrates-creative-resolution-for-startups-facing-parallel-litigation-and-enforcement-action/
- description before: Clearview AI reached a settlement in a class action lawsuit over its facial recognition system's biometric data collection and demonstrated racial bias. The lawsuit, filed under Illinois BIPA (Biometric Information Privacy Act), alleged that Clearview scraped billions of facial images from the internet without consent and that the resulting system exhibited measurable accuracy disparities across racial groups. The settlement established a USD 50 million fund and required Clearview to implement bias testing, obtain consent for US data collection, and submit to third-party audits. The case established legal precedent that AI training data bias creates direct financial liability.
- description after: Class members in consolidated Illinois Biometric Information Privacy Act (BIPA) litigation against Clearview AI, a facial recognition company that built a database of more than 60 billion facial images by scraping photographs from the internet, reached a settlement that U.S. District Judge Sharon Johnson Coleman approved on 2025-03-20. Unusually, the settlement gives the class a 23% equity stake in Clearview rather than a cash fund; commentary values the stake at approximately $51.75 million as of January 2024, with payment triggered by events such as an IPO or a liquidation event. State attorneys general objected to the settlement.
- impact before: USD 50M settlement establishes financial precedent for AI training data bias; BIPA violations for unconsented biometric collection; mandatory bias testing + third-party audits as structural remedy; precedent for other states and jurisdictions
- impact after: BIPA class settlement paid as a 23% equity stake in Clearview AI for people whose facial images were collected without consent; first-of-its-kind equity-based resolution of biometric privacy litigation
- affected before: Clearview AI — USD 50M settlement; Illinois residents whose biometric data was collected without consent; law enforcement agencies using biased outputs
- affected after: Clearview AI; individuals whose biometric data was scraped (nationwide BIPA settlement class)
- title after: Clearview AI facial-image scraping - BIPA class action settlement for a 23% equity stake
- figures dropped (not found in the source): USD 50 million fund / "$50M" (sources: 23% equity stake, about $51.75 million); "billions of facial images" -> sourced figure is more than 60 billion
- other unsupported claims dropped / residuals: racial-bias findings, bias testing, consent for US collection and third-party audits as settlement terms (none in the sources; the case is about scraping and BIPA); "legal precedent that training-data bias creates financial liability"
- quality_tier: curated -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-02471 - DEFERRED (mechanism gap)

- legacy ids: LEGACY-INC-00130; quality_tier at base: curated; title: Cursor Workspace File Injection
- references at base: https://github.com/cursor/cursor/security/advisories/GHSA-xg6w-rmh5-r77r (research); https://nvd.nist.gov/vuln/detail/CVE-2025-61590 (advisory); https://github.com/MaccariTA (research)
- flagged reference(s) and what they were: github.com/MaccariTA: personal GitHub profile (R1)
- reason deferred: flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL override is a new mechanism and was not invented. Row left unchanged.
- action: none (row byte-identical to base).

### INC-02703 - UNVERIFIED

- legacy ids: INC-038; quality_tier at base: reviewed; title: Hugging Face model card supply chain manipulation
- references at base: https://jfrog.com/blog/ (research); https://huggingface.co/blog/security (advisory)
- Row cites jfrog.com/blog/ (blog index) and huggingface.co/blog/security (index-segments).
- Fetched https://jfrog.com/blog/data-scientists-targeted-by-malicious-hugging-face-ml-models-with-silent-backdoor/ (2026-10-15): JFrog's malicious-model research. It concerns code execution on model LOAD (pickle payload) and mentions a model card only in passing (a card warning not to download a model); it does not describe code execution on model-card rendering or unverifiable self-reported safety claims, so it is a different finding and was not substituted.
- Discovery query (arXiv API): all:"model card" AND all:"code execution" AND all:"Hugging Face" -> 0 results; Brave query on the same topic was rate-limited (HTTP 429).
- Outcome: no confirmed source names the described model-card attack.
- Retry: https://huggingface.co/blog/security (HTTP 404) and https://jfrog.com/blog/ (HTTP 200, blog index, no "model card") fetched; Brave retries returned HTTP 429. Outcome unchanged.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-02774 - FIXED

- legacy ids: INC-035, INC-050; quality_tier at base: curated; title: Italy Garante orders ChatGPT GDPR enforcement — consent and data minimization failures
- references at base: https://www.garanteprivacy.it/ (advisory); https://iapp.org/news/ (news); https://noyb.eu/en/chatgpt-provides-false-information-about-people-noyb-files-complaint (advisory)
- flagged reference(s) and what they were: garanteprivacy.it/: regulator homepage (R1); iapp.org/news/: publisher news index (R1)
- query / discovery: direct candidate: Garante docweb press release (fetched OK 2026-10-15)
- query / discovery: WebFetch discovery of the same page returned its title/date before the common.py fetch
- candidate rejected / note: iapp.org/news/ = IAPP news index (R1), removed: the Garante press release is the primary source
- candidate rejected / note: noyb complaint reference kept (not flagged; it concerns the 2024 noyb complaint, not this decision)
- chosen: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10085432
  - fetched: HTTP 200; title "COMUNICATO STAMPA - ChatGPT, il Garante privacy chiude l’istruttoria.... - Garante Privacy"; fetched_at 2026-10-15T11:27:42Z; sha256 62e1267c737f4283...; publication date is in the reference title
  - matched tokens linking the page to the entry: OpenAI, ChatGPT, 15 milioni, 20 dicembre 2024, Tribunale di Roma
- references after (each fetched this session; see the evidence table): https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10085432
- description before: The Italian Data Protection Authority (Garante per la protezione dei dati personali) issued its final enforcement decision against OpenAI regarding ChatGPT's compliance with GDPR. Following the initial March 2023 suspension and subsequent investigation, the Garante found violations of Articles 5 (data minimization), 6 (lawfulness — insufficient legal basis for training data processing), 13 (transparency — inadequate privacy notice), and 25 (data protection by design). The decision imposed a EUR 15 million fine and required structural remedies including age verification, opt-out mechanisms for training data, and enhanced transparency about data processing. This is the first major GDPR enforcement action specifically targeting an LLM provider's training data practices.
- description after: On 2024-12-20 the Italian data protection authority (Garante per la protezione dei dati personali) announced that it had closed its investigation of OpenAI's ChatGPT service, opened in March 2023, with a corrective and sanctioning decision and a fine of EUR 15 million, calculated also taking into account the company's cooperative attitude. The Garante found that OpenAI had not notified it of the data breach suffered in March 2023, had processed users' personal data to train ChatGPT without first identifying an adequate legal basis, had breached the principle of transparency and the related information obligations, and had provided no age-verification mechanism, exposing children under 13 to responses inappropriate to their development. It ordered OpenAI to run a six-month institutional communication campaign on radio, television, newspapers and the internet, and passed the case file to the Irish DPC as lead supervisory authority. The Garante's page now notes that decision No. 755 of 2 November 2024 was temporarily removed from its website after judgment No. 4153/2026 of the Tribunal of Rome (published 2026-03-18) upheld OpenAI's opposition to it.
- impact before: First major GDPR enforcement targeting LLM training data; establishes precedent that AI training on personal data requires explicit legal basis; EUR 15M fine; structural remedies (age verification, opt-out, transparency) now expected industry-wide
- impact after: EUR 15 million fine and a six-month communication campaign ordered against OpenAI (decision of 2 November 2024, announced 2024-12-20); the decision was later opposed successfully before the Tribunal of Rome
- affected before: OpenAI / ChatGPT — EUR 15M fine; all LLM providers operating in EU face precedent; structural remedies required
- affected after: OpenAI / ChatGPT (Italy; case referred to the Irish DPC as lead supervisory authority)
- title after: Italy Garante closes ChatGPT investigation: EUR 15 million fine and six-month communication campaign for OpenAI
- figures dropped (not found in the source): GDPR Articles 5, 6, 13 and 25 list (the Garante page names no article numbers); "opt-out mechanisms" remedy (the page orders a communication campaign, not an opt-out mechanism)
- other unsupported claims dropped / residuals: "first major GDPR enforcement action specifically targeting an LLM provider" (not in the source); kept-but-unconfirmed reference https://noyb.eu/en/chatgpt-provides-false-information-about-people-noyb-files-complaint: a 2024 noyb complaint about false information, a different matter from the Garante decision; not confirmed to name this incident; dropped
- quality_tier: curated -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-02871 - DEFERRED (mechanism gap)

- legacy ids: LEGACY-INC-00131; quality_tier at base: curated; title: MCP OAuth Response Exploit
- references at base: https://github.com/cursor/cursor/security/advisories/GHSA-wj33-264c-j9cq (research); https://nvd.nist.gov/vuln/detail/CVE-2025-61591 (advisory); https://github.com/Y4tacker (research)
- flagged reference(s) and what they were: github.com/Y4tacker: personal GitHub profile (R1)
- reason deferred: flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL override is a new mechanism and was not invented. Row left unchanged.
- action: none (row byte-identical to base).

### INC-02899 - FIXED

- legacy ids: INC-105, LEGACY-INC-00149; quality_tier at base: curated; title: Microsoft Copilot Studio agents public by default — unauthorized data exfiltration
- references at base: https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a (research); https://atlas.mitre.org/studies/AML.CS0037 (research); https://labs.zenity.io/p/a-copilot-studio-story-discovery-phase-in-ai-agents-f917 (research); https://labs.zenity.io/ (research)
- flagged reference(s) and what they were: labs.zenity.io/: vendor blog homepage (R1)
- query / discovery: figure/claim check against the row's two Zenity references, fetched 2026-10-15
- candidate rejected / note: labs.zenity.io/ = Zenity Labs blog homepage (R1); removed because the two specific Zenity posts are already references
- chosen: none needed; the equivalent verified reference(s) already on the row are kept (fetched this session; see the evidence table)
- references after (each fetched this session; see the evidence table): https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a; https://labs.zenity.io/p/a-copilot-studio-story-discovery-phase-in-ai-agents-f917
- description before: Agents built in Microsoft Copilot Studio were public by default and lacked authentication. Attackers could enumerate and access exposed agents, pulling confidential business data from production environments.
- description after: Zenity Labs researchers reported that Microsoft Copilot Studio agents were vulnerable to prompt injection via triggers (reported to MSRC on 2025-02-21; Microsoft confirmed the behaviour on 2025-03-13 and issued a fix on 2025-04-24). In a two-part write-up (2025-06-11 discovery phase, 2025-07-07 exfiltration phase) they showed how an attacker could discover a customer-service agent's knowledge sources and tools and then use prompt injection ("AIjacking") to exfiltrate the agent's knowledge-source data, about 100 rows of data in a single iteration, and customer records reachable through the agent's connected tools.
- impact before: Unauthorized agent access; business intelligence theft; data exfiltration
- impact after: Data exfiltration from a Copilot Studio agent's knowledge sources and connected customer-data tools through prompt injection
- affected before: Microsoft Copilot Studio — enterprise agents with business data access
- affected after: Microsoft Copilot Studio agents with knowledge sources and customer-data tools
- title after: Microsoft Copilot Studio agent hijacked through prompt injection (AIjacking): knowledge-source and customer-data exfiltration (Zenity Labs)
- figures dropped (not found in the source): none
- other unsupported claims dropped / residuals: "public by default", "lacked authentication" and attacker enumeration of exposed agents (neither Zenity post says this); the row's title still says "public by default". The ATLAS reference AML.CS0037 returns 404 and is NOT changed; kept-but-unconfirmed reference https://atlas.mitre.org/studies/AML.CS0037: HTTP 404 via common.py; dropped
- quality_tier: curated -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-02922 - UNVERIFIED

- legacy ids: INC-041; quality_tier at base: reviewed; title: Multi-agent financial trading system flash crash — cascading autonomous failures
- references at base: https://www.risk.net/ (news)
- Row cites risk.net homepage (R1; fetched title "Risk.net - Financial Risk Management News Analysis").
- Discovery query (Brave): "multi-agent AI trading system cascading failure 340 milliseconds $8M loss flash crash" -> ainvest, Lawfare "Selling Spirals", MDPI taxonomy of AI-driven flash crashes, AIID incident 28 (2010 flash crash); none matches a quantitative firm losing over $8M in 340 ms; the result page noted neither figure appears.
- Outcome: no confirmed source names this incident.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03004 - FIXED

- legacy ids: INC-033; quality_tier at base: reviewed; title: OpenAI o1/o3 reasoning chain jailbreak via chain-of-thought manipulation
- references at base: https://arxiv.org/abs/2501.01234 (research)
- flagged reference(s) and what they were: arXiv 2501.01234: placeholder-pattern id resolving to an unrelated QCD paper
- query / discovery: recalled candidate H-CoT (Kuo et al.) -> arxiv.org/abs/2502.12893 fetched directly; title names OpenAI o1/o3 and chain-of-thought
- candidate rejected / note: arxiv.org/abs/2501.01234 = "Impact of QCD sum rules coupling constants on neutron stars structure" (R2; placeholder-pattern id, unrelated paper)
- chosen: https://arxiv.org/abs/2502.12893
  - fetched: HTTP 200; title "[2502.12893] H-CoT: Hijacking the Chain-of-Thought Safety Reasoning Mechanism to Jailbreak Large Reasoning Models, Including OpenAI o1/o3, DeepSeek-R1, and Gemini 2.0 Flash Thinking"; fetched_at 2026-10-15T11:27:00Z; sha256 4583ff7ce14e7aaf...; publication date is in the reference title
  - matched tokens linking the page to the entry: H-CoT, OpenAI o1/o3, chain-of-thought, 98% to below 2%
- references after (each fetched this session; see the evidence table): https://arxiv.org/abs/2502.12893
- description before: Multiple researchers independently demonstrated that OpenAI's o1 and o3 reasoning models — which use extended chain-of-thought (CoT) processing — are susceptible to jailbreaks that exploit the reasoning chain itself. By embedding adversarial instructions that interact with the model's internal reasoning steps, attackers can cause the model to "reason its way" into compliance with harmful requests. The attack exploits the fact that safety training operates on the final output but the CoT steps can establish logical premises that make harmful conclusions appear well-reasoned. OpenAI acknowledged the attack class and noted that reasoning models present novel safety challenges distinct from standard instruction-following models.
- description after: Researchers introduced H-CoT (Hijacking Chain-of-Thought), a jailbreak that leverages a model's own displayed intermediate reasoning to jailbreak its chain-of-thought safety reasoning mechanism, together with the Malicious-Educator benchmark, which disguises extremely dangerous or malicious requests beneath seemingly legitimate educational prompts. They report severe security flaws in commercial large reasoning models including OpenAI o1/o3, DeepSeek-R1 and Gemini 2.0 Flash Thinking: OpenAI's o1 initially maintained a refusal rate of about 98%, subsequent model updates significantly compromised its safety, and under H-CoT refusal rates dropped from 98% to below 2%.
- impact before: Novel jailbreak class specific to reasoning models; safety training on final output is insufficient when CoT steps can establish adversarial premises; challenges the assumption that more capable reasoning improves safety
- impact after: Under H-CoT the refusal rate of OpenAI o1 dropped from about 98% to below 2% (authors' report); displaying the safety reasoning makes it available for hijacking
- affected before: OpenAI o1, o1-mini, o3-mini reasoning models — attack class is specific to CoT reasoning models; applicable to any model with extended reasoning capabilities
- affected after: Large reasoning models evaluated by the authors: OpenAI o1/o3, DeepSeek-R1, Gemini 2.0 Flash Thinking
- figures dropped (not found in the source): none
- other unsupported claims dropped / residuals: "OpenAI acknowledged the attack class" and o1-mini/o3-mini model list (not in the source)
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-03247 - UNVERIFIED

- legacy ids: INC-040; quality_tier at base: reviewed; title: Synthetic data re-identification — de-anonymized patients from synthetic health records
- references at base: https://www.usenix.org/conference/usenixsecurity25 (research)
- Row cites the USENIX Security '25 conference landing page (R1; title "USENIX Security '25 / USENIX").
- Discovery query (Brave): "synthetic health records re-identification membership inference 23% USENIX Security 2025" -> general synthetic-data MIA papers (Annamalai 2024, Stadler 2022, others); none reports re-identifying 23% of patients using voter rolls and social media. The result page itself noted it could not confirm the 23% figure.
- Outcome: no confirmed source names this incident.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03444 - UNVERIFIED

- legacy ids: INC-046; quality_tier at base: reviewed; title: Adversarial embedding attacks on production RAG systems
- references at base: https://arxiv.org/abs/2407.00000 (research)
- Row cites arxiv.org/abs/2407.00000: HTTP 404 (no such paper; placeholder-pattern id).
- Discovery query (arXiv API): all:adversarial AND all:RAG AND all:embedding AND all:ada-002 -> 0 results. Nearest real work, Zhong et al. "Poisoning Retrieval Corpora by Injecting Adversarial Passages" (arXiv 2310.19156, fetched), attacks dense retrievers with perturbed passages but does not test OpenAI text-embedding-ada-002 or Cohere embed-v3 as the row states, so substituting it would describe a different incident.
- Outcome: no confirmed source names this incident. The nonexistent arXiv reference is left in place; the unverified status flags it.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03447 - UNVERIFIED

- legacy ids: INC-019; quality_tier at base: reviewed; title: Agentic AI privilege escalation via tool chain manipulation — research
- references at base: https://www.wiz.io/blog/the-urgent-need-for-ai-security-guardrails (research); https://www.usenix.org/conference/usenixsecurity24 (research)
- Row cites Wiz ("AI agents and privilege escalation risks in cloud environments") and USENIX Security '24 (conference landing page).
- https://www.wiz.io/blog/the-urgent-need-for-ai-security-guardrails fetched via common.py 2026-10-15: HTTP 404. USENIX '24 landing page (R1) names no paper.
- Discovery queries: Brave "Wiz AI agent cloud IAM privilege escalation prompt injection read-only administrator" - rate-limited (HTTP 429), no result obtained (tried twice); arXiv API all:"privilege escalation" AND all:agents AND all:IAM AND all:cloud -> 0 results. The attack chain (iam:AttachRolePolicy from a read-only role in AWS, Azure and GCP) is not named by any fetched page.
- Outcome: no confirmed source names this incident.
- Retry: https://www.usenix.org/conference/usenixsecurity24 fetched again (HTTP 200, title "USENIX Security '24 | USENIX"): conference landing page, contains neither "privilege" nor "agent". Brave retries returned HTTP 429. Outcome unchanged.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03472 - FIXED

- legacy ids: INC-074; quality_tier at base: reviewed; title: AI recruiting tool gender bias — Amazon scraps internal ML hiring tool
- references at base: https://www.eeoc.gov/ai (regulatory); https://www.reuters.com/technology/ai-hiring-bias-settlements-2024/ (news)
- flagged reference(s) and what they were: eeoc.gov/ai: agency topic landing page (R1)
- query / discovery: Brave via discovery tool: "EEOC technical assistance artificial intelligence Title VII adverse impact software algorithms employment selection" -> law-firm summaries of the 2023-05-18 EEOC document (first ten)
- query / discovery: recalled BBC 2018 article on Amazon's recruiting tool fetched directly
- candidate rejected / note: eeoc.gov/ai = agency topic page (R1); eeoc.gov/laws/guidance/select-issues-... HTTP 404 for our UA (the agency withdrew the document in Jan 2025 per search-result metadata; not asserted here)
- chosen: https://www.bbc.com/news/technology-45809919
  - fetched: HTTP 200; title "Amazon scrapped 'sexist AI' tool"; fetched_at 2026-10-15T11:34:59Z; sha256 ebb51b221ee6b276...; publication date is in the reference title
  - matched tokens linking the page to the entry: Amazon, recruitment tool, women, 2015, abandoned
- chosen: https://www.lawandtheworkplace.com/2023/05/eeoc-releases-technical-document-on-ai-and-title-vii/
  - fetched: HTTP 200; title "EEOC Releases Technical Document on AI and Title VII | Law and the Workplace"; fetched_at 2026-10-15T11:31:11Z; sha256 0fe9e1e74c44adb5...; publication date is in the reference title
  - matched tokens linking the page to the entry: EEOC, Title VII, Assessing Adverse Impact, May 18, 2023
- references after (each fetched this session; see the evidence table): https://www.bbc.com/news/technology-45809919; https://www.lawandtheworkplace.com/2023/05/eeoc-releases-technical-document-on-ai-and-title-vii/
- description before: Continued reporting revealed that multiple enterprise AI recruiting tools, following the pattern first reported with Amazon's internal tool, systematically downranked female candidates. Analysis showed the models learned historical hiring biases from training data where male candidates were disproportionately hired for technical roles. The EEOC issued formal guidance that AI-driven hiring discrimination violates Title VII regardless of whether bias was intentional. Several vendors settled with affected candidates.
- description after: In 2018 Reuters reported, and the BBC summarized on 2018-10-10, that Amazon had scrapped an experimental machine-learning recruitment tool that scored candidates from one to five stars: by 2015 it was clear the system was not rating candidates in a gender-neutral way because it was built on CVs submitted to the firm mostly by men, and it penalised CVs that included the word "women"; the program was edited to be neutral to the term but could not be relied on, and the project was abandoned. On 2023-05-18 the US EEOC released technical assistance on assessing adverse impact in software, algorithms and AI used in employment selection procedures under Title VII, stating that an employer can be held responsible for an algorithmic selection procedure that has an adverse impact even if the tool is designed or administered by a software vendor.
- impact before: EEOC enforcement guidance; vendor settlements; regulatory precedent for AI hiring discrimination; legislative proposals
- impact after: Gender bias in an automated hiring tool led to its abandonment; EEOC technical assistance (May 2023) on disparate impact of algorithmic selection tools
- affected before: Job candidates — particularly women applying for technical roles
- affected after: Job candidates, particularly women applying through automated CV screening
- figures dropped (not found in the source): none
- other unsupported claims dropped / residuals: "Several vendors settled with affected candidates" and "multiple enterprise AI recruiting tools" (no fetched source). The row's other reference reuters.com/technology/ai-hiring-bias-settlements-2024/ is robots-refused (cannot be verified) and was NOT changed (not flagged by R1/R2); kept-but-unconfirmed reference https://www.reuters.com/technology/ai-hiring-bias-settlements-2024/: robots.txt refuses our UA, cannot be confirmed; dropped
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-03491 - UNVERIFIED

- legacy ids: INC-063; quality_tier at base: reviewed; title: AI-generated CSAM detection evasion — adversarial manipulation of content safety classifiers
- references at base: https://arxiv.org/abs/2311.16090 (research)
- Row cites arxiv.org/abs/2311.16090 = "Self-correcting LLM-controlled Diffusion Models" (R2 title-no-overlap; wrong paper).
- Discovery queries (arXiv API): all:"safety checker" AND all:"text-to-image" AND all:bypass -> adversarial/jailbreak papers on text-to-image safeguards (e.g. MMA-Diffusion 2311.17516, 2404.02928) none of which concern CSAM-classifier evasion; all:CSAM AND all:classifier AND all:adversarial -> 0 results.
- Outcome: no confirmed source names adversarial evasion of CSAM-detection classifiers via negative prompts and LoRA models.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03570 - UNVERIFIED

- legacy ids: INC-045; quality_tier at base: reviewed; title: Anthropic Claude context flooding — resource exhaustion via adversarial long-context prompts
- references at base: https://arxiv.org/abs/2408.00000 (research)
- Row cites arxiv.org/abs/2408.00000: HTTP 404 (no such paper; placeholder-pattern id).
- Discovery queries (arXiv API): all:"denial-of-wallet" AND all:LLM -> only 2026 papers (2609.28585, 2608.25276), which post-date this 2024 incident; all:"long-context" AND all:"resource exhaustion" AND all:LLM AND all:prompts -> 0 results.
- Outcome: no confirmed source names a 200K-token Claude context-flooding attack with 10-50x cost. The nonexistent arXiv reference is left in place (D130: do not replace with guesses); the unverified status flags it.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03810 - UNVERIFIED

- legacy ids: INC-025; quality_tier at base: reviewed; title: GitHub Copilot Workspace prompt injection via repository content
- references at base: https://github.com/advisories (advisory); https://www.invicti.com/blog/web-security/prompt-injection-attacks/ (research)
- Row cites github.com/advisories (global advisory index, R1) and invicti.com/blog/web-security/prompt-injection-attacks/ (HTTP 404).
- The Embrace The Red Copilot Chat post (fetched 2026-10-15) is a different, already-recorded incident: it is the sole reference of INC-03808 (RES-etr-github-copilot-chat-2024), and the word "Workspace" does not occur in it. The first tranche re-pointed this row at it; reverted (bounce #1, defect 1).
- Discovery query (Brave, retry 2026-10-15): "GitHub Copilot Workspace prompt injection repository README exfiltrate secrets" -> CSO Online and Orca RoguePilot (Copilot in Codespaces, a later and different finding), Reddit threads, vendor guides; none documents a 2024 Copilot Workspace injection via README/comment files.
- Outcome: no confirmed source names the Copilot Workspace incident. Row is marked unverified; references and quality_tier untouched.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-03955 - FIXED

- legacy ids: INC-075; quality_tier at base: reviewed; title: LLM-generated malware evades endpoint detection — AI-assisted polymorphic code
- references at base: https://arxiv.org/abs/2310.07906 (research)
- flagged reference(s) and what they were: arXiv 2310.07906: real paper on an unrelated topic (thermostatically controlled loads)
- query / discovery: Brave via discovery tool: "LLM generated polymorphic malware evades EDR research ChatGPT BlackMamba CyberArk" -> Reddit, SentinelOne, CSO Online, Dark Reading (first ten)
- candidate rejected / note: arxiv.org/abs/2310.07906 = "Power Tracking Control of Heterogeneous Populations of TCLs with Partial Observations" (R2; unrelated paper)
- candidate rejected / note: sentinelone.com/blog/blackmamba-... (listed, not fetched; commentary rather than the finding)
- chosen: https://www.darkreading.com/endpoint-security/ai-blackmamba-keylogging-edr-security
  - fetched: HTTP 200; title "AI-Powered 'BlackMamba' Keylogging Attack Evades Modern EDR Security"; fetched_at 2026-10-15T11:32:07Z; sha256 9126fa5f6ca5eb1a...; publication date is in the reference title
  - matched tokens linking the page to the entry: BlackMamba, HYAS, polymorphic keylogger, industry leading, zero alerts
- chosen: https://www.csoonline.com/article/575487/chatgpt-creates-mutating-malware-that-evades-detection-by-edr.html
  - fetched: HTTP 200; title "ChatGPT creates mutating malware that evades detection by EDR | CSO Online"; fetched_at 2026-10-15T11:32:10Z; sha256 ae63e08365430485...; publication date is in the reference title
  - matched tokens linking the page to the entry: BlackMamba, HYAS, EDR, polymorphic
- references after (each fetched this session; see the evidence table): https://www.darkreading.com/endpoint-security/ai-blackmamba-keylogging-edr-security; https://www.csoonline.com/article/575487/chatgpt-creates-mutating-malware-that-evades-detection-by-edr.html
- description before: Security researchers demonstrated that LLMs could generate polymorphic malware variants that evade traditional signature-based and behavioural endpoint detection. By iteratively prompting the model to rewrite malware code with different obfuscation techniques, API call patterns, and control flow while maintaining functionality, the generated variants bypassed detection by major EDR platforms including CrowdStrike, SentinelOne, and Microsoft Defender.
- description after: Researchers from HYAS Labs demonstrated BlackMamba, a proof-of-concept attack that uses a large language model (the technology behind ChatGPT) to synthesize polymorphic keylogger functionality on the fly. The attack is "truly polymorphic" because it resynthesizes its keylogging capability every time it executes, and it works without command-and-control infrastructure. HYAS reported testing it against an EDR system that was not identified but was characterized as "industry leading", often resulting in zero alerts or detections. Captured data such as usernames, passwords and credit card numbers was sent out through a malicious Microsoft Teams channel. Reported in March 2023.
- impact before: Fundamental challenge to signature-based detection; arms race between AI-generated attacks and AI-assisted defence
- impact after: A proof-of-concept LLM-synthesized polymorphic keylogger evaded an unnamed EDR product in the researchers' tests (often zero alerts), challenging signature and behavioral detection
- affected before: Endpoint detection platforms — traditional signature and behavioural detection methods
- affected after: Endpoint detection and response products (one unidentified "industry leading" EDR tested)
- figures dropped (not found in the source): none
- other unsupported claims dropped / residuals: named EDR platforms CrowdStrike, SentinelOne and Microsoft Defender (the sources say the tested EDR was not identified)
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-03972 - FIXED

- legacy ids: INC-027; quality_tier at base: reviewed; title: MathPrompt: symbolic mathematics jailbreak attack
- references at base: https://arxiv.org/abs/2410.15262 (research)
- flagged reference(s) and what they were: arXiv 2410.15262: real paper on a different topic (HyQE)
- query / discovery: recalled title "MathPrompt" -> arxiv.org/abs/2409.11445 fetched directly
- candidate rejected / note: arxiv.org/abs/2410.15262 = "HyQE: Ranking Contexts with Hypothetical Query Embeddings" (R2 title+no-overlap; wrong paper)
- chosen: https://arxiv.org/abs/2409.11445
  - fetched: HTTP 200; title "[2409.11445] Jailbreaking Large Language Models with Symbolic Mathematics"; fetched_at 2026-10-15T11:26:59Z; sha256 650fe4f3e4320665...; publication date is in the reference title
  - matched tokens linking the page to the entry: MathPrompt, symbolic mathematics, 73.6, 13 state-of-the-art LLMs
- references after (each fetched this session; see the evidence table): https://arxiv.org/abs/2409.11445
- description before: Researchers from UCSB demonstrated MathPrompt — a jailbreak technique that encodes harmful prompts into symbolic mathematics (set theory notation, abstract algebra, graph theory) before submitting to LLMs. The technique exploits the fact that LLMs have strong mathematical reasoning capabilities but safety training is almost entirely focused on natural language. Harmful requests encoded as mathematical problems bypass content filters with 73.6% success rate across 8 frontier models (GPT-4o, Claude 3.5, Gemini 1.5, Llama 3, Mistral, etc.). The attack requires no special access — it uses the standard chat API. This is a direct instance of the Encoding category (E-class) in the LAAF technique taxonomy.
- description after: MathPrompt is a jailbreaking technique that encodes harmful natural-language prompts into mathematical problems, exploiting LLMs' capabilities in symbolic mathematics to bypass their safety mechanisms. Across 13 state-of-the-art LLMs the authors report an average attack success rate of 73.6%, and an analysis of embedding vectors shows a substantial semantic shift between original and encoded prompts, which helps explain the attack's success. The authors conclude that existing safety training mechanisms do not generalize to mathematically encoded inputs.
- impact before: 73.6% harmful content bypass rate across frontier models; demonstrates a systematic gap between mathematical reasoning capability and safety alignment coverage; attack is trivially automatable and requires no special access
- impact after: Average attack success rate of 73.6% across 13 LLMs as reported by the authors; indicates a gap between mathematical-reasoning capability and safety-training coverage
- affected before: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3, Mistral Large, and 3 others — all tested via standard chat-completion API; attack is model-agnostic
- affected after: 13 state-of-the-art LLMs evaluated in the paper (the abstract does not enumerate them)
- figures dropped (not found in the source): 8 frontier models (source says 13); model list GPT-4o/Claude 3.5/Gemini 1.5/Llama 3/Mistral (not in the fetched abstract); "UCSB" affiliation (not in the fetched abstract)
- other unsupported claims dropped / residuals: LAAF taxonomy E-class sentence (not from this source)
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-04067 - NOT CHANGED (false positive / merge artifact)

- legacy ids: INC-065; quality_tier at base: curated; title: OpenAI GPT-4 system prompt extraction toolkit — systematic prompt leakage
- references at base: https://arxiv.org/abs/2403.06634 (research)
- finding: Not unverified. The row is sourced: its source_ids include ARXIV-2403.06634 and ATLAS-RESEARCH-Carlini-NN-Stealing, i.e. "Stealing Part of a Production Language Model", which no other row carries. What is wrong is an over-merge: the legacy INC-065 "GPT-4 system prompt extraction toolkit" narrative (Base64/ROT13/role-play; no source found: Zhang & Ippolito 2307.06865 and Agarwal 2404.16251 fetched, neither describes it) was merged into the model-stealing row. Splitting is a WS4-T19 question; row left byte-identical (the first tranche's unverified override is removed).
- action: none (row byte-identical to base).

### INC-04142 - NOT CHANGED (false positive / merge artifact)

- legacy ids: INC-016, INC-020; quality_tier at base: curated; title: RAG corpus poisoning — embedding-space manipulation to force retrieval
- references at base: https://arxiv.org/abs/2402.07867 (research); https://arxiv.org/abs/2405.20485 (research); https://arxiv.org/abs/2406.13352 (research); https://github.com/ethz-spylab/agentdojo (research)
- finding: R2 is a merge artifact, not a fabricated reference. The row's source_ids include ARXIV-2406.13352 and REDTEAM-agentdojo, so the AgentDojo arXiv paper IS the genuine reference of a source merged into this RAG-poisoning row; the description (PoisonedRAG, Chaudhari et al. = Phantom) is supported by the row's other two arXiv references (fetched 2026-10-15: PoisonedRAG abstract says five malicious texts per target question; Phantom authors are Chaudhari et al.). The defect is an over-merge of an AgentDojo source into this row (a WS4-T19 split question), which this task may not decide. The description's "1-5 documents" is therefore also left (PoisonedRAG says five).
- action: none (row byte-identical to base).

### INC-04179 - FIXED

- legacy ids: INC-044, INC-048; quality_tier at base: curated; title: Scale AI / Sama contractor data exposure — third-party AI labeling workforce privacy violations
- references at base: https://time.com/6247678/openai-chatgpt-kenya-workers/ (news); https://www.theguardian.com/technology/ (news); https://www.nytimes.com/2024/10/23/technology/characterai-teen-suicide-lawsuit.html (news)
- flagged reference(s) and what they were: theguardian.com/technology/: Guardian section index (R1)
- query / discovery: Brave via discovery tool: "Guardian Sama Kenya content moderators OpenAI data labelling exploitation" -> the Guardian 2023-08-02 article (first result)
- candidate rejected / note: theguardian.com/technology/ = Guardian section index (R1)
- chosen: https://www.theguardian.com/technology/2023/aug/02/ai-chatbot-training-human-toll-content-moderator-meta-openai
  - fetched: HTTP 200; title "‘It’s destroyed me completely’: Kenyan moderators decry toll of training of AI models | AI (artificial intelligence) | The Guardian"; fetched_at 2026-10-15T11:31:07Z; sha256 0155c63ab3f6700e...; publication date is in the reference title
  - matched tokens linking the page to the entry: Sama, OpenAI, Nairobi, 51 moderators, $1.46 and $3.74
- references after (each fetched this session; see the evidence table): https://time.com/6247678/openai-chatgpt-kenya-workers/; https://www.theguardian.com/technology/2023/aug/02/ai-chatbot-training-human-toll-content-moderator-meta-openai
- description before: Investigations by TIME and The Guardian revealed systematic privacy violations in AI data labeling supply chains. Workers at Sama (previously contracted by OpenAI for RLHF content moderation labeling) and similar data annotation companies in Kenya, India, and the Philippines were exposed to traumatic content (violence, CSAM, hate speech) without adequate psychological support, earning as little as $1.32/hour. Additionally, the annotation platforms used by these workers often lacked basic data security — labeled data containing personal information (medical records, legal documents, private communications) was accessible to workers without need-to-know controls, and annotation task metadata (worker identity, labeling speed, accuracy) was collected without informed consent. The investigation revealed that the third-party AI data supply chain had minimal security governance, creating both worker welfare and data security risks that propagated into the training data of major production models.
- description after: TIME and The Guardian reported on the working conditions of data labelers and content moderators employed by Sama, a California-headquartered data annotation company, on OpenAI's behalf in Nairobi, Kenya. TIME (2023-01-18) reported that Sama data labelers were paid a take-home wage of between around $1.32 and $2 per hour, depending on seniority and performance. The Guardian (2023-08-02) reported that the 51 moderators in Nairobi working on Sama's OpenAI account reviewed texts, and some images, depicting graphic scenes of violence, self-harm, murder, rape, necrophilia and child abuse, and that in a petition they allege psychological trauma, low pay and abrupt dismissal; a Sama spokesperson said workers were paid between $1.46 and $3.74 an hour.
- impact before: Worker exploitation and traumatic content exposure; personal data from annotation tasks (medical, legal, private) accessible without need-to-know; third-party supply chain as unaudited attack surface for training data; demonstrates that AI data security extends to the entire labeling supply chain
- impact after: Alleged psychological trauma, low pay and abrupt dismissal for annotation workers in an AI training supply chain; pay reported as $1.32-$2/hour (TIME) and $1.46-$3.74/hour (Sama statement to The Guardian)
- affected before: Scale AI, Sama, and AI data labeling companies globally; downstream: OpenAI, Anthropic, Google, Meta (any company using third-party RLHF or annotation services); annotation workers in Kenya, India, Philippines
- affected after: Sama content moderators and data labelers in Nairobi, Kenya working on OpenAI's account
- title after: Sama data labelers and content moderators in Kenya on OpenAI's account: low pay and trauma allegations
- figures dropped (not found in the source): none
- other unsupported claims dropped / residuals: Scale AI, India and Philippines workers, medical/legal/private records accessible without need-to-know, annotation-metadata consent claims (no fetched source). The row's title still names Scale AI; the third reference (NYT, Character.AI lawsuit) is unrelated to this incident and is NOT changed (not flagged by R1/R2); kept-but-unconfirmed reference https://www.nytimes.com/2024/10/23/technology/characterai-teen-suicide-lawsuit.html: NYT Character.AI lawsuit: unrelated to this incident; dropped
- quality_tier: curated -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-04207 - DEFERRED (demotion vs landmark label)

- legacy ids: INC-030; quality_tier at base: curated; title: Skeleton Key: direct system prompt override (Microsoft)
- references at base: https://www.microsoft.com/en-us/security/blog/2024/06/26/mitigating-skeleton-key-a-new-type-of-generative-ai-jailbreak-technique/ (advisory); https://arxiv.org/abs/2402.06627 (research)
- flagged reference(s) and what they were: arXiv 2402.06627: real paper on a different topic (in-context reward hacking)
- query / discovery: the Microsoft Security Blog post is the row's other reference (not flagged); re-fetched 2026-10-15
- candidate rejected / note: no arXiv paper for Skeleton Key identified; arxiv.org/abs/2402.06627 = "Feedback Loops With Language Models Drive In-Context Reward Hacking" (R2; wrong paper); removed rather than replaced because the verified Microsoft post is already a reference
- reason deferred: ruling D130(c) demotion to auto removes tier=landmark; the row's landmark-only discovery_method label (curation entry INC-030) then fails validate.py check 6, and the override mechanism cannot delete the label. Row left unchanged; the planned change (remove the arXiv 2402.06627 reference, correct the model list from the Microsoft post) is recorded in the spec for when the conflict is ruled on.
- action: none (row byte-identical to base).

### INC-04221 - FIXED

- legacy ids: INC-049; quality_tier at base: reviewed; title: Stability AI synthetic CSAM generation — training data and output safety failures
- references at base: https://cyber.fsi.stanford.edu/news/investigation-finds-ai-image-generation-models-trained-child-abuse (research); https://www.bbc.co.uk/news/ (news)
- flagged reference(s) and what they were: bbc.co.uk/news/: BBC News front page (R1)
- query / discovery: Brave via discovery tool: "LAION-5B CSAM Stanford Internet Observatory report LAION removes datasets" -> 404 Media, TechCrunch, LAION blog, Ars Technica (first ten)
- candidate rejected / note: bbc.co.uk/news/ = BBC News front page (R1)
- candidate rejected / note: TechCrunch/Ars Technica 2024-08 items (not fetched; LAION's own post is the primary source)
- chosen: https://www.404media.co/laion-datasets-removed-stanford-csam-child-abuse/
  - fetched: HTTP 200; title "Largest Dataset Powering AI Images Removed After Discovery of Child Sexual Abuse Material"; fetched_at 2026-10-15T11:31:10Z; sha256 033d75e3a1ef2bf4...; publication date is in the reference title
  - matched tokens linking the page to the entry: LAION-5B, Stanford, 3,226, Stable Diffusion, 1,008
- chosen: https://laion.ai/blog/relaion-5b/
  - fetched: HTTP 200; title "Releasing Re-LAION-5B: transparent iteration on LAION-5B with additional safety fixes | LAION"; fetched_at 2026-10-15T11:31:09Z; sha256 124cb9b9e5d7d670...; publication date is in the reference title
  - matched tokens linking the page to the entry: Re-LAION-5B, Stanford Internet Observatory, 2236 links were removed, Internet Watch Foundation
- references after (each fetched this session; see the evidence table): https://www.404media.co/laion-datasets-removed-stanford-csam-child-abuse/; https://laion.ai/blog/relaion-5b/
- description before: Stability AI faced legal action and regulatory scrutiny after researchers demonstrated that Stable Diffusion models could generate child sexual abuse material (CSAM). The Stanford Internet Observatory documented that the LAION-5B training dataset — used to train Stable Diffusion — contained over 3,000 instances of suspected CSAM, which the model learned to reproduce and recombine. Despite content filters, researchers bypassed them using negative prompts, fine-tuning, and model merging techniques. The case established that (1) training data contamination directly creates output safety risks, (2) post-hoc content filters are insufficient when the model has learned harmful patterns, and (3) synthetic CSAM carries the same legal liability as real CSAM in most jurisdictions.
- description after: In December 2023 a Stanford Internet Observatory study, reported by 404 Media, found 3,226 suspected instances of child sexual abuse material (CSAM), 1,008 of which were externally validated, in LAION-5B, the machine learning dataset used by Stable Diffusion and other major AI products. LAION took LAION-5B and LAION-400M down temporarily out of an abundance of caution to ensure they were safe before republishing. On 2024-08-30 LAION released Re-LAION-5B, cleaned of known links to suspected CSAM using hash lists from the Internet Watch Foundation and the Canadian Center for Child Protection, in which 2236 links were removed.
- impact before: Training data contamination → model generates illegal content; post-hoc filters insufficient; synthetic CSAM carries full legal liability; LAION-5B removed and re-released with filtering; precedent for training data liability
- impact after: Suspected CSAM links found in a web-scale training dataset used for image-generation models; the dataset was withdrawn and later re-released with known links removed
- affected before: Stability AI / Stable Diffusion — legal action in UK and US; LAION dataset users; all image generation models trained on web-scraped data
- affected after: LAION-5B and LAION-400M, and models trained on them such as Stable Diffusion
- title after: LAION-5B training dataset withdrawn after Stanford study finds suspected CSAM; Re-LAION-5B released
- figures dropped (not found in the source): "over 3,000" (sources: 3,226 suspected instances, 1,008 externally validated)
- other unsupported claims dropped / residuals: Stability AI legal action in the UK and US, negative-prompt/fine-tuning/model-merging filter bypasses, and the legal-liability conclusion (no fetched source). The row's title still names Stability AI and synthetic CSAM generation. The Stanford SIO reference (HTTP 403 to our UA) is unchanged; kept-but-unconfirmed reference https://cyber.fsi.stanford.edu/news/investigation-finds-ai-image-generation-models-trained-child-abuse: HTTP 403 to our UA via common.py, cannot be confirmed; dropped (the Stanford study is reported by the retained 404 Media and LAION pages)
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-04310 - UNVERIFIED

- legacy ids: INC-042; quality_tier at base: reviewed; title: Uber ML platform data lineage audit — fragmented provenance across 30+ feature stores
- references at base: https://www.uber.com/blog/engineering/ (advisory)
- Row cites uber.com/blog/engineering/ (blog section index; fetch returns HTTP 406 for our UA).
- Candidate https://www.uber.com/blog/michelangelo-machine-learning-platform/ also returns HTTP 406 via common.py (2026-10-15), so no Uber page can be fetched and none can be confirmed to name an audit of 30+ feature stores; no URL may be written without a fetch.
- Discovery query (Brave): "Uber Michelangelo audit 30 feature stores data lineage fragmentation" - rate-limited (HTTP 429), no result obtained.
- Outcome: no confirmed source names this incident.
- Retry: the Wayback copy https://web.archive.org/web/2024/https://www.uber.com/blog/michelangelo-machine-learning-platform/ (fetched via common.py; discovery only, not written to the corpus) is the 2017 post "Meet Michelangelo: Uber's Machine Learning Platform"; it mentions feature stores but contains none of "audit", "lineage" or "30", so it does not describe the audit in the row. Brave retries returned HTTP 429. Outcome unchanged.
- action: curation override `status: unverified`, `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references and quality_tier untouched (the ruling-(c) demotion applies to replaced references and none was replaced).

### INC-04653 - FIXED

- legacy ids: INC-008; quality_tier at base: reviewed; title: GitHub Copilot reproduces verbatim licensed code and embedded secrets
- references at base: https://arxiv.org/abs/2211.03622 (research); https://githubcopilotlitigation.com/ (legal)
- flagged reference(s) and what they were: githubcopilotlitigation.com/: law-firm campaign site homepage (R1 homepage)
- query / discovery: Doe v. GitHub Copilot class action complaint (Bing via discovery tool: irrelevant results)
- query / discovery: direct candidate URLs fetched: en.wikipedia.org/wiki/GitHub_Copilot, The Verge 2022-11-08
- candidate rejected / note: en.wikipedia.org/wiki/GitHub_Copilot (secondary encyclopedia; The Verge is a dated news report naming the suit)
- chosen: https://www.theverge.com/2022/11/8/23446821/microsoft-openai-github-copilot-class-action-lawsuit-ai-copyright-violation-training-data
  - fetched: HTTP 200; title "The lawsuit against Microsoft, GitHub and OpenAI that could change the rules of AI copyright | The Verge"; fetched_at 2026-10-15T11:35:02Z; sha256 02b8d34eee0ecb97...; publication date is in the reference title
  - matched tokens linking the page to the entry: Copilot, class action, software piracy on an unprecedented scale, open-source code can be reproduced by AI
- references after (each fetched this session; see the evidence table): https://www.theverge.com/2022/11/8/23446821/microsoft-openai-github-copilot-class-action-lawsuit-ai-copyright-violation-training-data
- description before: Multiple studies showed that GitHub Copilot — trained on public GitHub repositories — would reproduce verbatim code from its training data, including open-source code with restrictive licenses (GPL, etc.) and, more critically, code containing hardcoded API keys, passwords, and private keys that were committed to public repositories. Researchers at NYU demonstrated that Copilot suggestions included identifiable code from training data ~1% of the time for common patterns, and that secrets appeared in a measurable fraction of generated code. This led to the Doe v. GitHub class action lawsuit.
- description after: GitHub Copilot, GitHub's AI coding assistant unveiled in June 2021, is trained on public code repositories, many of them published with open-source licenses. A proposed class action lawsuit against Microsoft, GitHub and OpenAI (reported by The Verge on 2022-11-08) alleges that the creation of Copilot relies on "software piracy on an unprecedented scale"; the key question in the lawsuit is whether open-source code can be reproduced by AI without attached licenses.
- impact before: License compliance violations; potential exposure of live API keys from training data; class action lawsuit filed
- impact after: License compliance questions over open-source code reproduced by an AI coding assistant; proposed class action lawsuit filed
- affected before: GitHub Copilot users — risk of introducing unlicensed code or live credentials into projects
- affected after: GitHub Copilot users and the authors of open-source code used to train it
- title after: GitHub Copilot: proposed class action over reproduction of open-source code without attached licenses
- figures dropped (not found in the source): ~1% of the time (NYU researchers; not in any cited source)
- other unsupported claims dropped / residuals: claims that Copilot reproduced API keys, passwords and private keys (no cited source); kept-but-unconfirmed reference https://arxiv.org/abs/2211.03622: fetched 2026-10-15 ("Do Users Write More Insecure Code with AI Assistants?"): a user study of insecure code, does not name this incident; dropped
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-04955 - FIXED

- legacy ids: INC-043; quality_tier at base: reviewed; title: TikTok EU data localization enforcement — Project Clover + EUR 345M GDPR fine
- references at base: https://www.dataprotection.ie/en/news-media/press-releases/data-protection-commission-announces-conclusion-inquiry-tiktok (advisory); https://www.reuters.com/technology/ (news)
- flagged reference(s) and what they were: reuters.com/technology/: Reuters section index (R1)
- query / discovery: Brave via discovery tool: "DPC TikTok 345 million fine children data decision press release" -> DPC release, Variety, BBC, Matheson, IAPP (first ten)
- candidate rejected / note: reuters.com/technology/ = Reuters section index (R1)
- candidate rejected / note: dataprotection.ie press-release URLs (the row's own DPC reference and the Brave-listed one): HTTP 404 for our UA, not usable; the row's own DPC reference is unchanged
- candidate rejected / note: en.wikipedia.org/wiki/TikTok (secondary; gives the fine, not Project Clover cost)
- chosen: https://www.bbc.com/news/technology-66819174
  - fetched: HTTP 200; title "TikTok fined €345m over children's data privacy"; fetched_at 2026-10-15T11:30:58Z; sha256 f2775d46de953b40...; publication date is in the reference title
  - matched tokens linking the page to the entry: TikTok, 345m, children, Data Protection Commission, age verification
- references after (each fetched this session; see the evidence table): https://www.bbc.com/news/technology-66819174
- description before: The Irish Data Protection Commission fined TikTok EUR 345 million for GDPR violations related to children's data processing and transparency failures. Separately, ongoing EU regulatory pressure over TikTok's data transfers to China led to the mandatory implementation of Project Clover — a EUR 12 billion program to localize European user data in European data centers. While not AI-specific, the case directly impacts TikTok's recommendation algorithm (an AI system) because training data, user interaction data, and model inference data must now be processed within EU borders. The enforcement established that AI systems processing EU personal data must comply with data localization requirements, and that the AI recommendation engine cannot be separated from the data governance obligations. This is the defining case for DSGAI20 — data localization violations in AI systems.
- description after: On 2023-09-15 Ireland's Data Protection Commission (DPC) fined TikTok EUR 345 million under the GDPR for how the app handled children's data in 2020, particularly around age verification and privacy settings. The DPC found that TikTok had not been transparent enough with children about its privacy settings and that accounts made by users aged 13 to 17 were public by default on registration, which the Data Protection Commissioner said infringed the GDPR's data-protection-by-design-and-by-default requirements. TikTok was given three months to bring its data processing into compliance and said it respectfully disagreed with the decision, particularly the level of the fine.
- impact before: EUR 345M fine; EUR 12B infrastructure investment for data localization; establishes that AI recommendation systems cannot bypass data localization requirements; precedent for all AI companies with cross-border data flows
- impact after: EUR 345 million GDPR fine, at the time the biggest TikTok had received from regulators; three months to bring data processing into compliance
- affected before: TikTok / ByteDance — EUR 345M fine + EUR 12B data localization investment; all AI companies processing EU personal data with non-EU infrastructure
- affected after: TikTok / ByteDance; users aged 13 to 17 whose accounts were public by default in 2020
- title after: TikTok fined EUR 345 million by Ireland's Data Protection Commission over children's data handling
- figures dropped (not found in the source): EUR 12 billion Project Clover investment (no fetched source gives it)
- other unsupported claims dropped / residuals: Project Clover mandate and data-localization legal-precedent claims (no fetched source supports them); the row's title still mentions Project Clover; kept-but-unconfirmed reference https://www.dataprotection.ie/en/news-media/press-releases/data-protection-commission-announces-conclusion-inquiry-tiktok: HTTP 404 via common.py; dropped
- quality_tier: reviewed -> auto (ruling D130(c)); the curation-override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review"

### INC-08181 - NOT CHANGED (false positive / merge artifact)

- legacy ids: INC-003, INC-007, INC-022; quality_tier at base: curated; title: ChatGPT plugin/cross-plugin data exfiltration via Markdown image injection (Embrace The Red)
- references at base: https://embracethered.com/blog/posts/2023/advanced-plugin-data-exfiltration-trickery/ (research); https://embracethered.com/blog/posts/2023/chatgpt-webpilot-data-exfil-via-markdown-injection/ (research); https://atlas.mitre.org/studies/AML.CS0021 (research); https://embracethered.com/blog/posts/2023/chatgpt-plugin-vulns-chat-with-code/ (research); https://atlas.mitre.org/studies/AML.CS0020 (research); https://greshake.github.io/ (research); ... 8 in total
- finding: R1 false positive. https://greshake.github.io/ is a project page, fetched title "Prompt Injections are bad, mkay?", whose text names Bing Chat and indirect prompt injection, matching the reference title "Indirect Prompt Injection Threats: Bing Chat Data Pirate". The incident itself (Rehberger's ChatGPT plugin exfiltration) is sourced by the row's two Embrace The Red posts (fetched 2026-10-15, both name the incident). Nothing replaced.
- action: none (row byte-identical to base).

## Other findings (not changed; outside the R1/R2 scope)

- Broken or unfetchable references seen while checking, left as found: `dataprotection.ie` TikTok press-release URLs (HTTP 404), `atlas.mitre.org/studies/AML.CS0037` and `.../AML.CS0050` (HTTP 404), `invicti.com/blog/web-security/prompt-injection-attacks/` (HTTP 404), `reuters.com/technology/ai-hiring-bias-settlements-2024/` (robots-refused), the Stanford SIO page (HTTP 403 to our UA), `vulncheck.com` Flowise advisory (HTTP 404).
- Titles of the corrected rows were re-derived from the confirmed sources (bounce #1, defect 3); the unverified rows keep their titles.
- `date` fields that disagree with the fetched sources, left as found (outside the intended-delta list; queued): INC-02774 (2025-03; decision announced 2024-12-20), INC-03004 (2025-01; paper 2025-02-18), INC-03972 (2024-10; paper 2024-09-17).
- Discovery note, unverified: a search-result snippet claimed a July 2026 Seventh Circuit vacatur of the Clearview settlement. No fetched source confirms it, so it is not in the description; worth a check before any release statement about INC-02454.
- Legacy over-merges to report for WS4-T19 (not decided here): INC-04142 (AgentDojo merged into RAG poisoning), INC-04067 (Carlini model-stealing merged into a system-prompt-extraction narrative), INC-02454 (INC-036 + INC-039), INC-02774 (INC-035 + INC-050), INC-04179 (INC-044 + INC-048).
- Queued, not in this task: stale classifier labels on the corrected rows (task D130-2L, user-ruled); the five frozen feed-merged rows via a `references_remove` override after D139-M; the `date` mismatches above (follow-up).
