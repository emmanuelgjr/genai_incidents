# D130-3a: reference remediation, 2026-11-11 (the 6 deferred rows + batch 1 of the D130-3 list)

**Agent-suggested, not human-reviewed.** Every change below awaits the user's re-review (ruling D130(c)); every demoted
row carries a curation-override note saying so. Scope: the 6 rows D130-2 deferred (INC-01015, INC-01291, INC-01589,
INC-02471, INC-02871, INC-04207; ruling D139) plus batch 1 (32 rows) of the D130-3 target list, `list.json`. Batches 2-4 (94 rows) are
NOT done here. No third-party page text is copied here beyond page titles and the short tokens that link a fetched page to a
row.

Method (the D130-2 method, `docs/audits/reference-audit-2026-10-15/`): a URL is written into the corpus only if this session
fetched it through `ingest/common.fetch_once` (robots.txt, per-host rate limit, identifying User-Agent; `fetch_evidence.py`) and
the fetched page names the incident; `export_evidence.py` re-checks every token and aborts on a missing one. Discovery used
direct URL guesses and the publishers' own index pages, fetched the same way; no search engine was available (the one tried
served a bot challenge, not results). References that are only REMOVED need no replacement when the row keeps other
references; references the row keeps untouched were not re-fetched (the audit covers the flagged URLs). All changes are
`data/curation_overrides.json` entries generated from `d1303a_spec.py` by `build_overrides.py`; `data/incidents.json` and every other
`data/*.json` is build output and was not edited.

## The target list (`list.json`) and its reconciliation

`python -I docs/audits/reference-audit-2026-11-11/derive_list.py` (offline, deterministic, reads `data/incidents.json` at base
64109452 via `git show`; exits 1 unless it derives 126 + 6).

| step | rows |
|---|---|
| R1 or R2 rows in the detection report, at 589376db (re-derived: `r1()` verbatim + the report's 11 R2 rows) | 156 |
| minus D130-2's legacy-seed rows (`INC-<n>` / `LEGACY-INC-<n>`) | -30 |
| = non-legacy R1/R2 rows | 126 |
| same rule run on 64109452 | 126 non-legacy (125 trip R1; INC-04383 trips R2 only) |
| plus the 6 rows D130-2 deferred | +6 |
| **list.json** | **132** (batch 0 = the 6 deferred; batches 1-4 = 32, 32, 31, 31 in stable ID order) |

Reconciliation: the numbers agree exactly (156 - 30 = 126), with two clarifications. (1) The 126 are the rows whose
source_ids carry no legacy `INC-<n>` id; INC-04383 (ATLAS case AML.CS0016) is the one R2-only row among them (its arXiv
reference is a background citation, title-no-overlap), the other non-legacy R2 row, INC-05052, also trips R1. (2) Of the 30
legacy rows, 8 left the R1/R2 set because D130-2 replaced their references; the other 22 still trip the rule at 64109452
(10 unverified, 3 unchanged, 6 deferred, 3 fixed rows whose R2 flag is a static row list), so a naive rerun of R1 over current data
gives 148 = 126 + 22, not 132. The 6 deferred rows are in this batch; the 3 D130-2 "unchanged" rows (INC-04067, INC-04142,
INC-08181: two over-merges and one false positive) stay out. No refresh added or removed a target. Batch 1 contains INC-04383 and
INC-05052 (the two non-legacy R2 rows) by ID order.

## Outcome (the 6 deferred rows + batch 1 of the D130-3 list = 38 rows)

| outcome | rows | ids |
|---|---|---|
| fixed (flagged reference removed) | 29 | INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207, INC-00021, INC-01194, INC-01348, INC-01553, INC-01724, INC-02076, INC-02150, INC-02347, INC-02505, INC-02516, INC-02761, INC-02800, INC-02864, INC-03209, INC-03276, INC-03292, INC-03423, INC-04285, INC-04383, INC-04959, INC-05009, INC-05421, INC-05425 |
| fixed (replaced) | 5 | INC-01600, INC-01641, INC-02498, INC-03212, INC-03248 |
| unverified | 2 | INC-00570, INC-03573 |
| unchanged (false positive) | 2 | INC-00864, INC-05052 |
| **total** | **38** | |

## Per-row outcomes

| id | batch | tier before | outcome | flagged URL (rule) -> fetch result 2026-11-11 | change |
|---|---|---|---|---|---|
| INC-01015 | 0 | curated | fixed (flagged reference removed) | `https://flowiseai.com` (homepage) -> HTTP 200, title "Flowise - Build AI Agents, Visually" | reference(s) removed; demoted to auto |
| INC-01291 | 0 | curated | fixed (flagged reference removed) | `https://www.langchain.com/` (homepage) -> HTTP 200, title "LangChain: the open agent platform to own your intelligence" | reference(s) removed; demoted to auto |
| INC-01589 | 0 | curated | fixed (flagged reference removed) | `https://openclaw.ai/blog` (depth1-non-slug) -> HTTP 200, title "Blog - OpenClaw" | reference(s) removed; demoted to auto |
| INC-02471 | 0 | curated | fixed (flagged reference removed) | `https://github.com/MaccariTA` (depth1-non-slug) -> HTTP 200, title "MaccariTA (MaccariTA) · GitHub" | reference(s) removed; demoted to auto |
| INC-02871 | 0 | curated | fixed (flagged reference removed) | `https://github.com/Y4tacker` (depth1-non-slug) -> HTTP 200, title "Y4tacker (Y4tacker) · GitHub" | reference(s) removed; demoted to auto |
| INC-04207 | 0 | curated | fixed (flagged reference removed) | `https://arxiv.org/abs/2402.06627` (R2 arXiv id/title mismatch) -> HTTP 200, title "[2402.06627] Feedback Loops With Language Models Drive In-Context Rewa" | reference(s) removed; demoted to auto |
| INC-00021 | 1 | reviewed | fixed (flagged reference removed) | `http://trezor.com` (homepage) -> HTTP 200, title "Сейфы: лучшие модели и новинки ТРЕЗОР" | reference(s) removed; demoted to auto |
| INC-00570 | 1 | reviewed | unverified | `https://www.aim.security/news` (depth1-non-slug) -> refused (robots.txt disallowed or unverifiable; fail-closed) | `status: unverified` (`no-confirmed-source`); references, title, tier untouched. The only reference is the publisher's news index (R1). aim.security robots.txt could not be verified (HTTP 403), so ingest/common.fetch_once refuses the host (fail-closed); no page naming 'continuing EchoLeak research and variants' was fetchable, and no other source was found. |
| INC-00864 | 1 | reviewed | unchanged (false positive) | `https://cybersecuritynews.com/flowise-vulnerability/` -> HTTP 200, title "Critical Vulnerability In Flowise Allows Remote Command Execution Via " | R1 false positive: an article (one-hyphen slug) on the OX Security finding that Anthropic's MCP SDKs allow command execution; it names the incident. |
| INC-01194 | 1 | reviewed | fixed (flagged reference removed) | `https://trysixth.com/` (homepage) -> HTTP 200, title "Sixth" | reference(s) removed; demoted to auto |
| INC-01348 | 1 | reviewed | fixed (flagged reference removed) | `https://www.llamaindex.ai/` (homepage) -> HTTP 200, title "LlamaIndex / AI Agents for Document OCR + Workflows" | reference(s) removed; demoted to auto |
| INC-01553 | 1 | reviewed | fixed (flagged reference removed) | `https://ollama.com/` (homepage) -> HTTP 200, title "Ollama · Run AI models locally and in the cloud" | reference(s) removed; demoted to auto |
| INC-01600 | 1 | reviewed | fixed (replaced) | `https://www.reco.ai/newsroom` (depth1-non-slug) -> HTTP 200, title "Reco Newsroom: AI Security News & Updates" | reference -> `https://www.reco.ai/blog/openclaw-the-ai-agent-security-crisis-unfolding-right-now` (fetched 200, names the incident); description kept (supported by the page); demoted to auto |
| INC-01641 | 1 | reviewed | fixed (replaced) | `https://www.pillar.security/blog` (depth1-non-slug) -> HTTP 200, title "Pillar Blog / Latest stories about AI Security" | reference -> `https://www.pillar.security/blog/the-agent-security-paradox-when-trusted-commands-in-cursor-become-attack-vectors` (fetched 200, names the incident); description kept (supported by the page); demoted to auto |
| INC-01724 | 1 | reviewed | fixed (flagged reference removed) | `https://raytha.com` (homepage) -> HTTP 200, title "Raytha: the open source .NET CMS for developers who ship" | reference(s) removed; demoted to auto |
| INC-02076 | 1 | reviewed | fixed (flagged reference removed) | `https://www.kxan.com/driverless/` (depth1-non-slug) -> HTTP 403 | reference(s) removed; demoted to auto |
| INC-02150 | 1 | reviewed | fixed (flagged reference removed) | `http://openairinterface.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed); `https://cellularsecurity.org/ransacked` (depth1-non-slug) -> HTTP 200, title "Cellular Security / Florida Institute for Cybersecurity Research"; `https://openairinterface.org/` (homepage) -> HTTP 200, title "OpenAirInterface"; kept: `https://cellularsecurity.org/ransacked` -> HTTP 200, title "Cellular Security / Florida Institute for Cybersecurity Research" | reference(s) removed; demoted to auto |
| INC-02347 | 1 | reviewed | fixed (flagged reference removed) | `https://iocharger.com` (homepage) -> HTTP 200, title "OCPP EV Charger Manufacturer / Iocharger / Fleet Charging" | reference(s) removed; demoted to auto |
| INC-02498 | 1 | reviewed | fixed (replaced) | `https://embracethered.com/blog/` (depth1-non-slug) -> HTTP 200, title "Embrace The Red · Embrace The Red" | reference -> `https://embracethered.com/blog/posts/2024/deepseek-ai-prompt-injection-to-xss-and-account-takeover/` (fetched 200, names the incident); title, description re-derived; demoted to auto |
| INC-02505 | 1 | reviewed | fixed (flagged reference removed) | `http://dify.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed) | reference(s) removed; demoted to auto |
| INC-02516 | 1 | reviewed | fixed (flagged reference removed) | `https://dify.ai` (homepage) -> HTTP 200, title "Dify - The Platform for Production-Ready Agentic Workflows" | reference(s) removed; demoted to auto |
| INC-02761 | 1 | reviewed | fixed (flagged reference removed) | `http://langchain-chatglm-webui.com` (homepage) -> refused (robots.txt disallowed or unverifiable; fail-closed) | reference(s) removed; demoted to auto |
| INC-02800 | 1 | reviewed | fixed (flagged reference removed) | `https://python.langchain.com/docs/security/` (index-segments) -> HTTP 200, title "LangChain overview - Docs by LangChain" | reference(s) removed; demoted to auto |
| INC-02864 | 1 | reviewed | fixed (flagged reference removed) | `https://mattermost.com/security-updates` (depth1-non-slug) -> HTTP 200, title "Security Updates / Mattermost Documentation" | reference(s) removed; demoted to auto |
| INC-03209 | 1 | reviewed | fixed (flagged reference removed) | `https://www.microsoft.com/en-us/security/blog/` (index-segments) -> HTTP 200, title "Microsoft Security Blog" | reference(s) removed; demoted to auto |
| INC-03212 | 1 | reviewed | fixed (replaced) | `https://unit42.paloaltonetworks.com/` (homepage) -> HTTP 200, title "Unit 42 - Latest Cybersecurity Research / Palo Alto Networks" | reference -> `https://unit42.paloaltonetworks.com/npm-supply-chain-attack/` (fetched 200, names the incident); title, description, affected re-derived; demoted to auto |
| INC-03248 | 1 | reviewed | fixed (replaced) | `https://www.sysdig.com/threat-research` (depth1-non-slug) -> HTTP 200, title "Threat Research / Sysdig" | reference -> `https://www.sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes` (fetched 200, names the incident); description kept (supported by the page); demoted to auto |
| INC-03276 | 1 | reviewed | fixed (flagged reference removed) | `https://dotapp.uk` (homepage) -> HTTP 200, title "Try out the Dot beta" | reference(s) removed; demoted to auto |
| INC-03292 | 1 | auto | fixed (flagged reference removed) | `https://phcode.dev/` (homepage) -> HTTP 200, title "Phoenix Code - Free Open Source Code Editor / Successor to Brackets"; `https://www.postbox-inc.com/` (homepage) -> HTTP 200, title "The Power Email App - Postbox" | reference(s) removed; already auto |
| INC-03423 | 1 | reviewed | fixed (flagged reference removed) | `https://monica.im/desktop` (depth1-non-slug) -> HTTP 200, title "Monica - Your GPT AI Assistant Chrome Extension" | reference(s) removed; demoted to auto |
| INC-03573 | 1 | reviewed | unverified | `https://www.anthropic.com/research` (depth1-non-slug) -> HTTP 200, title "Research \ Anthropic" | `status: unverified` (`no-confirmed-source`); references, title, tier untouched. The only reference is the publisher's research index (R1). anthropic.com/research and /news were fetched (200) and name no Frontier Threats Red Team spear-phishing scaling study; no other source was found. The row also carries a second seed id (an election-influence study) with no source. |
| INC-04285 | 1 | reviewed | fixed (flagged reference removed) | `https://premiumaddons.com/change-log/` (depth1-non-slug) -> HTTP 200, title "Premium Addons PRO Changelog / Premium Addons for Elementor" | reference(s) removed; demoted to auto |
| INC-04383 | 1 | reviewed | fixed (flagged reference removed) | `https://arxiv.org/abs/2103.03874` -> HTTP 200, title "[2103.03874] Measuring Mathematical Problem Solving With the MATH Data"; `https://arxiv.org/abs/2110.14168` -> HTTP 200, title "[2110.14168] Training Verifiers to Solve Math Word Problems" | reference(s) removed; demoted to auto |
| INC-04959 | 1 | reviewed | fixed (flagged reference removed) | `https://www.oligo.security/shelltorch` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |
| INC-05009 | 1 | reviewed | fixed (flagged reference removed) | `https://docs.dependencytrack.org/changelog/` (depth1-non-slug) -> HTTP 200, title "Change Log / Dependency-Track" | reference(s) removed; demoted to auto |
| INC-05052 | 1 | reviewed | unchanged (false positive) | `https://real-gradients.github.io/` -> HTTP 200, title "Real Attackers Don't Compute Gradients"; `https://arxiv.org/abs/2212.14315` -> HTTP 200, title "[2212.14315] "Real Attackers Don't Compute Gradients": Bridging the Ga" | R1/R2 false positive: the dedicated site and paper behind ATLAS case AML.CS0032 (screenshots of 100 evasive phishing webpages, MLSEC anti-phishing analysis); the R2 title-overlap flag is a token artefact of a generic row title. |
| INC-05421 | 1 | reviewed | fixed (flagged reference removed) | `http://abna24.com/b4xD` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |
| INC-05425 | 1 | reviewed | fixed (flagged reference removed) | `http://abna24.com/b8b9` (depth1-non-slug) -> HTTP 404 | reference(s) removed; demoted to auto |

## Field-level delta (working agreement 2)

Control = committed data at base 64109452; new = this branch's build. Entry count 15821 -> 15821; ID set equal: True; ID order equal: True; rows with any difference: 36 (= the 29 remove rows + 5 replace rows + 2 unverified rows); rows outside them with any difference: 0; unintended field moves: 0.

Envelope / `data/stats.json` keys that moved (declared set; any other key would be a defect, and none moved):

| key | before | after | cause |
|---|---|---|---|
| `generated` | 2026-11-08 | 2026-11-11 | build date stamp |
| `incident_count` | 15782 | 15780 | the 2 newly unverified rows leave the count |
| `landmark_count` | 2062 | 2056 | the 6 curated deferred rows leave the landmark tier by demotion (D130(c)) |
| `unverified_count` | 10 | 12 | the 2 newly unverified rows |

| field | rows | kind | justification |
|---|---|---|---|
| `affected` | 1 (INC-03212) | intended | INC-03212: package names the source does not name dropped |
| `confidence` | 21 | derived | `_derive_confidence`: curated/reviewed -> high; 2+ sources with a CVE stay high, 2+ sources or a CVE/CVSS give medium. Follows quality_tier only |
| `description` | 2 (INC-02498, INC-03212) | intended | re-derived from the confirmed source; claims the source does not support dropped |
| `discovery_method` | 3 (INC-02471, INC-02871, INC-04207) | intended | landmark-only label (integrity check): its override line is dropped for INC-04207 (D139(b)) and for INC-02471, INC-02871 (same mechanism, same reason; see Declared knock-ons) |
| `last_seen` | 36 | derived | history stamp: content changed (build date) |
| `quality_tier` | 33 | intended | ruling D130(c): every row whose reference is replaced or removed demotes to auto; never promoted. INC-03292 was already auto |
| `references` | 34 | intended | the D130-3a change itself |
| `status` | 2 (INC-00570, INC-03573) | intended | D130(b): unverified |
| `status_reason` | 2 (INC-00570, INC-03573) | intended | {code: no-confirmed-source, as_of: 2026-11-11} |
| `tier` | 6 (INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207) | derived | `_derive_tier`: curated -> landmark, so the 6 curated deferred rows (no aiid_id, corpus not ai-harm) become feed. Follows quality_tier only |
| `title` | 2 (INC-02498, INC-03212) | intended | re-derived from the confirmed source so title and description agree (bounce lesson iii) |
| `updated` | 36 | derived | history stamp: content changed (build date) |

`tier` landmark -> feed on 6 rows: INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207. `landmark_count` 2062 -> 2056. INC-02076 (reviewed) is demoted but stays landmark through its `aiid_id`.

`confidence` moved on 21 rows (INC-00021 high->medium, INC-01194 high->medium, INC-01600 high->medium, INC-01641 high->low, INC-02076 high->medium, INC-02498 high->medium, INC-02505 high->medium, INC-02516 high->medium, INC-02761 high->medium, INC-02800 medium->low, INC-03209 high->low, INC-03212 high->low, INC-03248 high->low, INC-03276 high->medium, INC-04207 high->medium, INC-04285 high->medium, INC-04383 high->low, INC-04959 high->medium, INC-05009 high->medium, INC-05421 high->low, INC-05425 high->low).

Full per-row before/after: `delta-2026-11-11.json`.


## Declared knock-ons and headline deltas (bounce lesson iv)

- `incident_count` 15,782 -> 15,780: exactly the 2 newly unverified rows (INC-00570, INC-03573); `unverified_count` 10 -> 12.
- `landmark_count` 2,062 -> 2,056: the 6 curated deferred rows (INC-01015, INC-01291, INC-01589, INC-02471, INC-02871, INC-04207) are
  demoted to `quality_tier: auto`, which makes them `tier: feed` (`_derive_tier`: curated -> landmark; no `aiid_id`, corpus not `ai-harm`).
  INC-04207: tier landmark -> feed and confidence high -> medium, as the D139 gate advised.
- `confidence` moves on 21 rows (`_derive_confidence`, follows the demotion only; the list is in the delta table).
- **`discovery_method` on 3 rows, one more than the D139 premise.** The integrity check refuses `discovery_method` outside the
  landmark tier. INC-04207's value came only from its INC-030 override line (dropped, per D139(b)). INC-02471 and INC-02871 (both curated
  landmark, demoted) carried the same kind of label from their own CVE override entries ("Advisory credits ... as the finder"); once
  demoted they would fail the check, so the `discovery_method` key is dropped from those two entries as well and its text is kept in
  `_d130_3a_prior_note`. This is the same mechanism and reason as D139(b) but names two rows the ruling did not; it is flagged for the
  user's re-review. Nothing else in those entries changed. `fields_clear` was not needed (no other source supplies the value).
- No row was deleted; no ID changed; entry count 15,821 and the ID set and order are unchanged.

## Rows whose description (or affected) changed: queue for a SEPARATE WS2 re-label (bounce lesson v; NOT done here)

INC-02498 (title, description) and INC-03212 (title, description, affected). The classifier-derived labels (`attack_vector`, `severity`,
`owasp_*`, `nist_ai_rmf`, `mitre_atlas*`, `category`, `tags`, ...) keep their base values on these two rows (the delta shows none moved)
and may reflect the old wording: INC-02498 (was "session/token handling weakness", now prompt injection to XSS to token theft) and
INC-03212 (was "LLM generated malicious scripts ... Crowdstrike, Postman, Zapier", now one bash script assessed LLM-generated). The other 34 changed
rows kept their text; their labels are unaffected.

## Observations and follow-ups (not actioned)

- **ATLAS case pages return 404 to our fetcher** (`atlas.mitre.org/studies/AML.CS0016`, `/AML.CS0032`, and `/studies`), although they are
  the canonical first reference of every ATLAS-sourced row. Not an R1/R2 flag; reported for the WS4 link-health task.
- **Over-merge stubs on single-incident rows.** INC-02498's source_ids include `RES-bing-copilot-zero-click-2024`, INC-01600's include
  `RES-reco-cursor-bg-2025`, and INC-03573's include `VTR-anthropic-election-influence-study-2024`: separate incidents, apparently merged on a shared
  index URL. The rows' titles and text describe only one incident each, so they were fixed/marked on that incident; the merge itself is a WS4-T19 item.
- **Date lag.** INC-02498 is dated 2025-01 but the confirmed page is dated 2024-11-29; left as found (a date change is outside D130-3a, like
  the D130-2 follow-up g).
- INC-00864's cybersecuritynews.com article and INC-05052's paper site were kept (R1/R2 false positives); INC-02150 keeps
  `https://cellularsecurity.org/ransacked` (fetched, names CVE-2024-24426) while its two homepages were removed.
- INC-00570 is unverified only because aim.security is unfetchable under the fail-closed robots rule (HTTP 403 on robots.txt); it may be
  re-checked if that host's robots.txt becomes verifiable.
- Existing refs the audit did not flag but met in passing: `research.nccgroup.com/2022/12/05/exploring-prompt-injection-attacks` (INC-04383) now
  serves an index page without the article; `lspace.swyx.io` could not be verified. Untouched.

## Reproduce

```
python -I docs/audits/reference-audit-2026-11-11/derive_list.py            # 126 + 6 = 132, exit 0
python -I docs/audits/reference-audit-2026-11-11/build_overrides.py --check # overrides file == spec (exit 0)
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py && python scripts/render_markdown.py \
  && python scripts/render_docs_stats.py && python scripts/validate.py && python scripts/lint_atlas_ids.py   # build; git status clean afterwards
python -I docs/audits/reference-audit-2026-11-11/verify.py                  # per-ID spec check, OK 0
python -I docs/audits/reference-audit-2026-11-11/delta.py                   # delta vs 64109452, unintended []
```
