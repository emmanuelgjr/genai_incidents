# User re-review package: D130-2 and D130-2L agent-suggested changes, 2026-10-16

**Agent-assembled, 2026-10-16; decisions are the user's.** Nothing in this file or in the 21 changes it lists has been
reviewed by a human. The package assembler (governance-scribe) did not re-fetch any page; every claim below is read from the
files named in the legend and can be wrong where those files are. Third-party pages are referred to by title and short
tokens only.

## 0. Legend and how to use this file

Citations are `<source>:<line>` against the tree at `9f4e1cae` (main). `A` = `docs/audits/reference-audit-2026-10-15/reference-audit-2026-10-15.md`;
`E` = `docs/audits/reference-audit-2026-10-15/fetch-evidence-2026-10-15.json` (looked up by URL); `R` = `docs/audits/relabel-d130-2l-2026-10-16.md`;
`C` = `CORRECTIONS.md`; `O` = `data/curation_overrides.json` (keyed by legacy source id); `D` = `data/incidents.json`; `P` = `PROGRESS.md`.

**What is being reviewed.** Ruling D130(c) (user, 2026-10-14): every replaced reference demotes the row to `quality_tier: auto`
with a curation-override note "pending user re-review" (A:3, A:126 etc.). Two agent changes landed under it:

- **D130-2** (merged to main as `05ff1e75`, A:1-13, P:113-117): 11 rows had a flagged reference replaced and the title/description/impact/affected re-derived from fetched sources ("fixed"); 10 rows were given `status: unverified` (`no-confirmed-source`) because no source naming the incident was found.
- **D130-2L** (merged as `bc6d1c43`, R:1-8, P:89-92): labels (attack_vector, OWASP, NIST, ATLAS, tags, MAESTRO, one severity, one category) on 9 of the 11 fixed rows re-derived from the new text.

**What a decision means (one per row; record it on the "User decision:" line).**

| decision | effect |
|---|---|
| accept | the agent change stands as built. **It does not promote `quality_tier`**: the rows stay `auto` (fixed rows) or keep their prior `reviewed`/`curated` tier (unverified rows). Promotion is a separate user act, never an agent act and not implied by "accept". |
| reject | the foreman dispatches a revert of that row's override entries (the `_note` / `_d130_2l_note` keys in `O`); `data/*.json` is never hand-edited. Rejecting restores the pre-D130-2 build output, including the reference(s) the audit found wrong. For an unverified row it returns the row to `incident_count`. |
| amend | the user supplies the correction (a source, a wording, a label); the foreman routes it to the owning specialist as a new gated task. |

Decisions on the fixed rows are independent for D130-2 (references/text) and D130-2L (labels); the decision line has a slot for each.

## 1. Summary table (21 rows)

"Old → new refs" lists hosts or arXiv ids; the full URLs and fetch timestamps are in section 3. "Labels" = fields changed by D130-2L (R:261-280); "none" = recomputation equalled the base (R:282-283); "n/a" = D130-2L did not touch the row.

| INC | legacy id(s) | outcome | old refs → new refs | title before → after | labels changed (D130-2L) | decision |
|---|---|---|---|---|---|---|
| INC-02454 | INC-036, INC-039 | fixed | reuters.com/legal/, eff.org/ → natlawreview.com, regulatoryoversight.com | "Clearview AI biometric bias - $50M class action settlement" → "...BIPA class action settlement for a 23% equity stake" | owasp_dsgai, tags, maestro_layers | |
| INC-02774 | INC-035, INC-050 | fixed | garanteprivacy.it/, iapp.org/news/, noyb.eu complaint → garanteprivacy.it docweb 10085432 | "Italy Garante orders ChatGPT GDPR enforcement - consent and data minimization failures" → "Italy Garante closes ChatGPT investigation: EUR 15 million fine and six-month communication campaign for OpenAI" | attack_vector, owasp_dsgai, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics, tags | |
| INC-02899 | INC-105, LEGACY-INC-00149 | fixed | labs.zenity.io/, atlas.mitre.org AML.CS0037 (404) removed; two Zenity posts kept | "Microsoft Copilot Studio agents public by default - unauthorized data exfiltration" → "Microsoft Copilot Studio agent hijacked through prompt injection (AIjacking): ... (Zenity Labs)" | attack_vector, owasp_asi, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics, tags, maestro_layers | |
| INC-03004 | INC-033 | fixed | arxiv 2501.01234 → arxiv 2502.12893 | unchanged ("OpenAI o1/o3 reasoning chain jailbreak via chain-of-thought manipulation") | attack_vector | |
| INC-03472 | INC-074 | fixed | eeoc.gov/ai, reuters.com (ai-hiring-bias-settlements-2024) → bbc.com, lawandtheworkplace.com | unchanged ("AI recruiting tool gender bias - Amazon scraps internal ML hiring tool") | maestro_layers | |
| INC-03955 | INC-075 | fixed | arxiv 2310.07906 → darkreading.com, csoonline.com | unchanged ("LLM-generated malware evades endpoint detection - AI-assisted polymorphic code") | none | |
| INC-03972 | INC-027 | fixed | arxiv 2410.15262 → arxiv 2409.11445 | unchanged ("MathPrompt: symbolic mathematics jailbreak attack") | none | |
| INC-04179 | INC-044, INC-048 | fixed | theguardian.com/technology/, nytimes.com Character.AI removed; time.com kept; Guardian 2023-08-02 article added | "Scale AI / Sama contractor data exposure - third-party AI labeling workforce privacy violations" → "Sama data labelers and content moderators in Kenya on OpenAI's account: low pay and trauma allegations" | attack_vector, severity, owasp_llm, owasp_asi, owasp_dsgai, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics, tags, maestro_layers | |
| INC-04221 | INC-049 | fixed | bbc.co.uk/news/, cyber.fsi.stanford.edu (403) removed → 404media.co, laion.ai | "Stability AI synthetic CSAM generation - training data and output safety failures" → "LAION-5B training dataset withdrawn after Stanford study finds suspected CSAM; Re-LAION-5B released" | tags, maestro_layers | |
| INC-04653 | INC-008 | fixed | githubcopilotlitigation.com/, arxiv 2211.03622 → theverge.com 2022-11-08 | "GitHub Copilot reproduces verbatim licensed code and embedded secrets" → "GitHub Copilot: proposed class action over reproduction of open-source code without attached licenses" | category, owasp_llm, owasp_dsgai, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics, tags, maestro_layers | |
| INC-04955 | INC-043 | fixed | reuters.com/technology/, dataprotection.ie release (404) removed → bbc.com 2023-09 article | "TikTok EU data localization enforcement - Project Clover + EUR 345M GDPR fine" → "TikTok fined EUR 345 million by Ireland's Data Protection Commission over children's data handling" | attack_vector, owasp_dsgai, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics, tags, maestro_layers | |
| INC-02353 | INC-037 | unverified | msrc.microsoft.com/ → unchanged | unchanged | n/a | |
| INC-02703 | INC-038 | unverified | jfrog.com/blog/, huggingface.co/blog/security → unchanged | unchanged | n/a | |
| INC-02922 | INC-041 | unverified | risk.net/ → unchanged | unchanged | n/a | |
| INC-03247 | INC-040 | unverified | usenix.org USENIX Security '25 landing page → unchanged | unchanged | n/a | |
| INC-03444 | INC-046 | unverified | arxiv 2407.00000 (404, nonexistent) → unchanged | unchanged | n/a | |
| INC-03447 | INC-019 | unverified (thin effort) | wiz.io blog (404), usenix.org '24 landing page → unchanged | unchanged | n/a | |
| INC-03491 | INC-063 | unverified | arxiv 2311.16090 (wrong paper) → unchanged | unchanged | n/a | |
| INC-03570 | INC-045 | unverified | arxiv 2408.00000 (404, nonexistent) → unchanged | unchanged | n/a | |
| INC-03810 | INC-025 | unverified | github.com/advisories, invicti.com (404) → unchanged | unchanged | n/a | |
| INC-04310 | INC-042 | unverified (thin effort; unfetchable by us) | uber.com/blog/engineering/ → unchanged | unchanged | n/a | |

Sources for the table: outcomes A:15-30, A:34-37; titles A (per-row "title after"; base titles in each "title:" line); labels R:261-280, C:15; legacy ids D (source_ids, e.g. D:3020-3023, D:9388-9392).

## 2. Cross-cutting facts for the reviewer

- All 11 fixed rows are `quality_tier: auto` now (curated 4 → auto, reviewed 7 → auto; A:17-19). The 10 unverified rows kept `reviewed` (A:20, A:98). Derived `confidence` fell with quality_tier (A:46).
- Tier: INC-02774, INC-02899, INC-04179 left `landmark` for `feed`; INC-02454 stayed `landmark` only because its `corpus` is pinned to `ai-harm` in the override (O:867; A:38, A:60-62; see 5.1). Headline counts moved: incident_count 15,755 → 15,745, unverified 0 → 10, landmark 2,028 → 2,025 (A:36-38).
- D130-2L froze 9 rows' labels by override; a later change to the classifier or OWASP→ATLAS tables will not reach those fields (R:312-318). `lint_atlas_ids.py` still catches an ATLAS re-pin.
- The rejected-or-amended path is mechanical for the foreman: each row has its own override key in `O` (fixed rows: INC-008 O:748, INC-027 O:779, INC-033 O:793, INC-035 O:809, INC-036 O:849, INC-043 O:887, INC-044 O:929, INC-049 O:967, INC-074 O:1011, INC-075 O:1045, INC-105 O:1064; unverified: INC-019 O:1133, INC-037 O:1141, INC-038 O:1149, INC-040 O:1157, INC-041 O:1165, INC-042 O:1173, INC-045 O:1181, INC-046 O:1189, INC-063 O:1197, INC-025 O:1205).

## 3. Fixed rows (11)

Common to every fixed row: `quality_tier` → `auto` (D130(c)); override `_note` reads "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review" (A: last line of each row section); each URL added was fetched through `ingest/common.fetch_once` with HTTP 200 and its row-linking tokens checked (A:9-10; `E` entry per URL). Where a section says "removed", the URL is no longer in the row's `references`.

### INC-02454 (legacy INC-036 + INC-039) - Clearview AI BIPA settlement

- **Sources:** A:100-126; R:82-96; O:849-886; C:16; D:3019-3088.
- **Old refs:** reuters.com/legal/ (Reuters section index; robots-refused, unverifiable); eff.org/ (EFF homepage, titled as "AI copyright training data legal analysis", a mismatch) (A:103, A:106-107).
- **New refs:** natlawreview.com "BIPA Litigation Class Members Receive Equity in Clearview AI", fetched_at 2026-10-15T11:31:00Z (E, url `.../first-bipa-litigation-class-members-receive-equity-clearview-ai`); regulatoryoversight.com "$51.75M Settlement in Clearview AI Biometric Privacy Litigation ...", fetched_at 2026-10-15T11:31:06Z (A:111-116). Tokens: Clearview, BIPA, 23% equity stake, 60 billion, $51.75 million.
- **Text (A:117-125):** before = $50M fund, racial-bias findings, mandated bias testing/consent/audits, "precedent that training-data bias creates liability". After = settlement approved 2025-03-20 paying the class a 23% equity stake (about $51.75M by commentary), state attorneys general objected, 60 billion images. Title changed.
- **Figures dropped:** "USD 50 million fund"; "billions of images" (sourced figure: more than 60 billion) (A:124). Also dropped: racial-bias findings, bias-testing/consent/audit settlement terms, the "legal precedent" sentence (A:125).
- **Labels (R:82-96):** DSGAI05, DSGAI12, DSGAI21 removed (INC-039 provenance); 8 tags removed (7 from INC-039, plus `bias` as unsupported); all 3 MAESTRO layers removed (bias claims dropped). `consent` tag kept (see 5.4).
- **Open items:** corpus pin (5.1); a search-result snippet about a July 2026 Seventh Circuit vacatur is **unverified and not in the text** (A:109, A:499); `mitigations` and `source_ids` still carry the copyright incident's content (R:331-334; D:3047-3056 still lists bias-testing and copyright mitigations); `date` 2025-01 vs approval 2025-03-20 (agent observation, not in the audit's list).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-02774 (legacy INC-035 + INC-050) - Italy Garante / OpenAI

- **Sources:** A:147-169; R:98-112; O:809-848; C:17; D:2929.
- **Old refs:** garanteprivacy.it/ (regulator homepage, R1), iapp.org/news/ (publisher news index, R1), noyb.eu complaint about false information in ChatGPT (a 2024 complaint, "a different matter from the Garante decision"; removed as unconfirmed) (A:150-155, A:168).
- **New ref:** garanteprivacy.it docweb 10085432, press release "ChatGPT, il Garante privacy chiude l'istruttoria", fetched_at 2026-10-15T11:27:42Z (A:157). Tokens: OpenAI, ChatGPT, 15 milioni, 20 dicembre 2024, Tribunale di Roma.
- **Text (A:160-166):** before = Articles 5/6/13/25 violations, EUR 15M, opt-out and age-verification remedies, "first major GDPR enforcement against an LLM provider". After = decision announced 2024-12-20, EUR 15M, six-month communication campaign, file passed to the Irish DPC, and a note that the decision was later opposed successfully before the Tribunal of Rome (judgment published 2026-03-18). Title changed.
- **Figures/claims dropped:** GDPR article numbers list; "opt-out mechanisms" remedy; "first major GDPR enforcement action ..." (A:167-168).
- **Labels (R:98-112):** attack_vector `rce` → `privacy-violation` (**judgement call 1**, below); OWASP DSGAI11 removed; NIST MANAGE-2.3, MEASURE-2.7 → MAP-4.1, MEASURE-2.10; ATLAS AML.T0049/T0050 and tactics TA0004/TA0005 removed (these came from the `rce`-inside-"enforcement" substring artifact, R:27-30); 7 tags removed.
- **Judgement call 1 (R:103):** rule output = first hit "data breach" → `data-exfiltration`, from the Garante's finding that a March 2023 breach was not notified. Agent chose `privacy-violation` because the decision's subject is unlawful processing for training, transparency and age verification. The `data-exfiltration` alternative is the literal rule result.
- **Open items:** `date` 2025-03 vs 2024-12-20 (A:498; R:335-336); over-merge with the noyb matter (5.6); decision-opposed note relies on one page (the Garante's own).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-02899 (legacy INC-105 + LEGACY-INC-00149 + ATLAS-AML.CS0037) - Copilot Studio AIjacking

- **Sources:** A:179-197; R:114-128; O:1064-1132; C:18; D:9387-9485.
- **Old refs:** two Zenity posts (kept); labs.zenity.io/ (blog homepage, R1, removed); atlas.mitre.org/studies/AML.CS0037 (HTTP 404 via our fetcher, removed) (A:182-183, A:196).
- **Kept refs (fetched):** "A Copilot Studio Story 2: When AIjacking Leads to Full Data Exfiltration | Zenity Labs", fetched_at 2026-10-15T11:32:15Z; "A Copilot Studio Story: Discovery Phase in AI Agents | Zenity Labs", fetched_at 2026-10-15T11:32:17Z (E, both URLs). No new URL added (A:186-187).
- **Text (A:188-195):** before = "agents public by default, lacked authentication, attackers enumerate exposed agents". After = prompt injection via triggers (reported to MSRC 2025-02-21, fixed 2025-04-24), two-part write-up 2025-06-11 and 2025-07-07, knowledge-source and customer-data exfiltration. Title changed.
- **Figures dropped:** none (A:195). **Claims dropped:** "public by default", "lacked authentication", attacker enumeration (A:196).
- **Labels (R:114-128):** attack_vector `auth-bypass` → `prompt-injection` (rule output, R:119); ASI03, ASI07 removed; NIST GOVERN-1.1, GOVERN-1.4, MAP-4.1 removed; ATLAS T0012, T0024, T0055 and tactics TA0004, TA0013 removed; tags `authentication`, `default-public` removed; MAESTRO L4/origin removed, L2/impact kept.
- **Open items:** the kept L2/impact note and the three `mitigations` still echo the dropped claim (5.3); `source_ids` still lists ATLAS-AML.CS0037 and LEGACY-INC-00149 although the 404 reference and the "public by default" claim were dropped (D:9388-9392); severity `Critical` was set against the old claim (R:63-68, waits for WS2-T5); tier landmark → feed.
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-03004 (legacy INC-033) - H-CoT jailbreak

- **Sources:** A:208-227; R:130-144; O:793-808; C:19; D:2725.
- **Old ref:** arXiv 2501.01234, a placeholder-pattern id that resolves to an unrelated QCD paper (A:214).
- **New ref:** arXiv 2502.12893 "H-CoT: Hijacking the Chain-of-Thought Safety Reasoning Mechanism to Jailbreak Large Reasoning Models ...", fetched_at 2026-10-15T11:27:00Z (E). Tokens: H-CoT, OpenAI o1/o3, chain-of-thought, 98% to below 2% (A:215-217).
- **Text (A:219-226):** before = unnamed "multiple researchers", o1/o3 chain-of-thought jailbreak, "OpenAI acknowledged". After = the H-CoT paper and its Malicious-Educator benchmark, o1 refusal rate about 98% falling to below 2% (authors' report). Title unchanged. **Dropped:** "OpenAI acknowledged the attack class"; o1-mini/o3-mini list (A:226). Figures dropped: none.
- **Labels (R:130-135):** attack_vector `adversarial-input` → `jailbreak` (rule output).
- **Open items:** `date` 2025-01 vs paper 2025-02-18 (A:498).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-03472 (legacy INC-074) - Amazon recruiting tool and EEOC

- **Sources:** A:258-281; R:146-160; O:1011-1044; C:20; D:6268.
- **Old refs:** eeoc.gov/ai (agency topic page, R1, removed); reuters.com/technology/ai-hiring-bias-settlements-2024/ (robots-refused, cannot be verified; removed as unconfirmed, not because it was shown false) (A:261-262, A:280).
- **New refs:** bbc.com/news/technology-45809919 "Amazon scrapped 'sexist AI' tool", fetched_at 2026-10-15T11:34:59Z; lawandtheworkplace.com "EEOC Releases Technical Document on AI and Title VII", fetched_at 2026-10-15T11:31:11Z (A:266-272).
- **Text (A:273-279):** before = "multiple enterprise AI recruiting tools", EEOC enforcement guidance, "several vendors settled". After = Amazon's experimental tool scored CVs, penalised the word "women", abandoned (2018 reporting; BBC summary 2018-10-10), plus the EEOC technical assistance of 2023-05-18. Title unchanged (still "...Amazon scraps internal ML hiring tool"). **Dropped:** "Several vendors settled", "multiple enterprise AI recruiting tools" (A:280). Figures dropped: none.
- **Labels (R:146-160):** MAESTRO L6/impact removed (note asserted Title VII violations, EEOC enforcement, settlements); all other label fields unchanged.
- **Open items:** `date` 2024-08 vs 2018 reporting and a 2023-05-18 EEOC document (R:335-336); the EEOC document was reported withdrawn Jan 2025 per search metadata, not asserted (A:265).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-03955 (legacy INC-075) - BlackMamba

- **Sources:** A:311-334; R:162-176; O:1045-1063; C:21; D:6360.
- **Old ref:** arXiv 2310.07906, a real paper on an unrelated topic (thermostatically controlled loads) (A:314-317).
- **New refs:** darkreading.com "AI-Powered 'BlackMamba' Keylogging Attack Evades Modern EDR Security", fetched_at 2026-10-15T11:32:07Z; csoonline.com "ChatGPT creates mutating malware that evades detection by EDR", fetched_at 2026-10-15T11:32:10Z (A:319-325).
- **Text (A:326-333):** before = generic "researchers showed LLM polymorphic malware evades CrowdStrike, SentinelOne, Microsoft Defender". After = HYAS Labs' BlackMamba proof of concept, one unidentified "industry leading" EDR, often zero alerts, March 2023. Title unchanged (still "LLM-generated malware evades endpoint detection - AI-assisted polymorphic code"). **Dropped:** the three named EDR products (A:333). Figures dropped: none.
- **Labels:** none changed (recomputation equals base, R:282-283).
- **Open items:** `date` 2024-04 vs March 2023 (R:335-336).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** n/a (unchanged)

### INC-03972 (legacy INC-027) - MathPrompt

- **Sources:** A:336-355; R:178-192; O:779-792; C:22; D:2180.
- **Old ref:** arXiv 2410.15262, a real paper on a different topic (HyQE ranking) (A:339-342).
- **New ref:** arXiv 2409.11445 "Jailbreaking Large Language Models with Symbolic Mathematics", fetched_at 2026-10-15T11:26:59Z (E). Tokens: MathPrompt, symbolic mathematics, 73.6, 13 state-of-the-art LLMs (A:343-345).
- **Text (A:347-354):** before = "8 frontier models", a named model list, UCSB, a LAAF-taxonomy sentence. After = 13 LLMs, 73.6% average attack success (authors' report). Title unchanged. **Figures dropped:** "8 frontier models" (source says 13); model list and "UCSB" (not in the fetched abstract) (A:353). Claim dropped: LAAF E-class sentence (A:354).
- **Labels:** none changed.
- **Open items:** `date` 2024-10 vs paper 2024-09-17 (A:498).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** n/a (unchanged)

### INC-04179 (legacy INC-044 + INC-048) - Sama data labelers

- **Sources:** A:371-391; R:194-208; O:929-966; C:23; D:3660.
- **Old refs:** time.com TIME 2023-01-18 (kept); theguardian.com/technology/ (section index, R1, removed); nytimes.com Character.AI lawsuit (unrelated to this incident; removed) (A:374-377, A:390).
- **New ref:** theguardian.com 2023-08-02 "'It's destroyed me completely': Kenyan moderators decry toll of training of AI models", fetched_at 2026-10-15T11:31:07Z. Kept TIME ref "OpenAI Used Kenyan Workers on Less Than $2 Per Hour: Exclusive", fetched_at 2026-10-15T11:27:53Z (E). Tokens: Sama, OpenAI, Nairobi, 51 moderators, $1.46 and $3.74 (A:379-381).
- **Text (A:382-389):** before = privacy/data-security violations in AI labeling supply chains, Kenya/India/Philippines, access-control and consent-metadata claims, "Scale AI". After = Sama workers' pay ($1.32-$2/hour per TIME; $1.46-$3.74 per a Sama statement) and alleged trauma, low pay and dismissal. Title changed. Figures dropped: none. **Claims dropped:** Scale AI, India and Philippines workers, accessible medical/legal/private records, metadata-consent claims (A:390).
- **Labels (R:194-208):** attack_vector `supply-chain` → `other` (**judgement call 2**, below); severity Critical → High (max over kept sources; Critical came from dropped INC-048); owasp_llm, owasp_asi, owasp_dsgai, nist_ai_rmf, mitre_atlas, mitre_atlas_tactics all emptied; 10 tags removed; all 3 MAESTRO layers removed. After D130-2L the row carries no framework mappings at all.
- **Judgement call 2 (R:199):** rule output = first hit "self-harm" → `unsafe-advice`, which in the new text is content the moderators reviewed, not advice an AI gave. Agent chose `other` (labour conditions have no attack_vector value). The `unsafe-advice` alternative is the literal rule result.
- **Open items:** over-merge residue (AI-companion mitigations incl. a suicide hotline, R:331-334); `date` 2024-01 vs TIME 2023-01-18 and Guardian 2023-08-02 (agent observation, not in the audit's list); title in the old state named Scale AI, now removed; tier landmark → feed.
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-04221 (legacy INC-049) - LAION-5B CSAM

- **Sources:** A:403-427; R:210-224; O:967-1010; C:24; D:4044.
- **Old refs:** cyber.fsi.stanford.edu SIO page (HTTP 403 to our UA; removed as unconfirmable, not shown false); bbc.co.uk/news/ (BBC front page, R1, removed) (A:406-407, A:426).
- **New refs:** 404media.co "Largest Dataset Powering AI Images Removed After Discovery of Child Sexual Abuse Material", fetched_at 2026-10-15T11:31:10Z; laion.ai/blog/relaion-5b "Releasing Re-LAION-5B ...", fetched_at 2026-10-15T11:31:09Z (A:411-417).
- **Text (A:418-425):** before = Stable Diffusion "could generate CSAM", filter bypasses by negative prompts/fine-tuning/model merging, legal-liability conclusion. After = Stanford Internet Observatory study (Dec 2023) found 3,226 suspected instances (1,008 externally validated) in LAION-5B; takedown; Re-LAION-5B released 2024-08-30 with 2236 links removed. Title changed (no longer names Stability AI or synthetic generation). **Figures dropped:** "over 3,000" (replaced by 3,226 / 1,008). **Claims dropped:** Stability AI legal action in UK/US, filter-bypass methods, legal-liability conclusion (A:426).
- **Labels (R:210-224):** tags `synthetic-data`, `legal-liability` removed; MAESTRO L1/impact and L6/impact removed. `attack_vector: csam-generation` **kept** though the new text reports CSAM in a dataset, not generation (R:70-72); `stability-ai` tag kept.
- **Open items:** `date` 2024-04 vs December 2023 study (R:335-336); severity `Critical` was set for synthetic CSAM generation (R:63-68, awaits WS2-T5).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-04653 (legacy INC-008) - GitHub Copilot lawsuit

- **Sources:** A:440-461; R:226-240; O:748-778; C:25; D:480.
- **Old refs:** githubcopilotlitigation.com/ (law-firm campaign homepage, R1, removed); arXiv 2211.03622 "Do Users Write More Insecure Code with AI Assistants?" (fetched; a user study that does not name this incident; removed) (A:443-444, A:460).
- **New ref:** theverge.com 2022-11-08 "The lawsuit against Microsoft, GitHub and OpenAI that could change the rules of AI copyright", fetched_at 2026-10-15T11:35:02Z (E line 5-9). Tokens: Copilot, class action, software piracy on an unprecedented scale, open-source code can be reproduced by AI (A:448-450).
- **Text (A:452-459):** before = verbatim code, hardcoded API keys/passwords/private keys, NYU researchers, ~1%. After = proposed class action against Microsoft, GitHub and OpenAI alleging unlicensed reproduction of open-source code. Title changed (no longer says "embedded secrets"). **Figures dropped:** "~1% of the time" (A:459). **Claims dropped:** Copilot reproduced keys/passwords/private keys; NYU study (A:460).
- **Labels (R:226-240):** category `research-demonstrated` → `real-world` (**judgement call 3**, below); owasp_llm LLM02, LLM08 removed; DSGAI07 removed, **DSGAI01 kept** (see 5.2); NIST, ATLAS, ATLAS tactics emptied; tag `secrets` removed; all MAESTRO layers removed.
- **Judgement call 3 (R:230):** no rule output; agent chose `real-world` because the new text is a proposed class action reported 2022-11-08, not a research demonstration.
- **Open items:** `date` 2023-01 vs 2022-11-08 (R:335-336); severity `High` was set for leaked secrets (R:63-68).
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

### INC-04955 (legacy INC-043) - TikTok DPC fine

- **Sources:** A:463-485; R:242-256; O:887-928; C:26; D:3595.
- **Old refs:** dataprotection.ie DPC press release (HTTP 404 to our UA; removed as unconfirmable, not shown false); reuters.com/technology/ (section index, R1, removed) (A:466-470, A:484).
- **New ref:** bbc.com/news/technology-66819174 "TikTok fined EUR 345m over children's data privacy", fetched_at 2026-10-15T11:30:58Z (A:472-474). Tokens: TikTok, 345m, children, Data Protection Commission, age verification.
- **Text (A:476-482):** before = EUR 345M fine plus "Project Clover, a EUR 12 billion data-localization program", "the defining case for DSGAI20". After = the 2023-09-15 DPC fine over children's data in 2020 (accounts of 13-17 year olds public by default; three months to comply). Title changed (no longer names Project Clover). **Figures dropped:** EUR 12 billion Project Clover (A:483). **Claims dropped:** Project Clover mandate and the data-localization precedent claim (A:484).
- **Labels (R:242-256):** attack_vector `rce` → `privacy-violation` (**judgement call 4**, below); DSGAI20 removed; NIST MANAGE-2.3, MEASURE-2.7 → MAP-4.1, MEASURE-2.10; ATLAS and tactics emptied (the `rce` substring artifact); tags `data-localization`, `project-clover`, `cross-border` removed; MAESTRO L2/origin and L4/impact removed (L6/origin kept).
- **Judgement call 4 (R:247):** no rule hit (the privacy rule needs "privacy violation/breach" phrasing). Agent chose `privacy-violation` (consistent with INC-02454 and INC-02774) because the DPC found the children's-data handling infringed the GDPR.
- **Open items:** severity `Critical` was set with the EUR 12B context (R:63-68); only one reference remains and the primary DPC page is unfetchable by us.
- **User decision (references/text):** accept / reject / amend ______  **(labels):** accept / reject / amend ______

## 4. Unverified rows (10)

Common to all ten: override sets `status: unverified` and `status_reason: {code: no-confirmed-source, as_of: 2026-10-15}`; references, title and `quality_tier` are untouched (A:98 etc.; D:1459-1463, D:2051-2055, D:3175-3179). The row leaves `incident_count` and stays in the full JSON (A:37). Because `quality_tier` is untouched, filtering on quality_tier alone still includes these rows (P:104, finding F6). Accept = stays unverified; reject = status override removed, row returns to the count with its unsourced references; amend = user names a source.

Discovery tools recorded: Brave search (outside the corpus path; rate-limited with HTTP 429 on several retries) and the arXiv API; neither is written into the corpus (A:9-12).

### INC-02353 (INC-037) - Azure OpenAI content filter bypass via structured output
- **Source:** A:91-98; O:1141; C:27. **Cited ref:** msrc.microsoft.com/ (portal homepage, title "MSRC - Microsoft Security Response Center").
- **Searched:** one recorded Brave query (structured outputs / content filter bypass / JSON schema). Results were Microsoft Learn documentation and Q&A threads about structured responses *blocked* by the content filter, the opposite of a bypass; none describes the field-name bypass (A:96).
- **Why nothing qualified:** no fetched page describes this attack.
- **User decision:** accept / reject / amend ______

### INC-02703 (INC-038) - Hugging Face model card supply chain manipulation
- **Source:** A:136-145; O:1149; C:28. **Cited refs:** jfrog.com/blog/ (blog index), huggingface.co/blog/security (HTTP 404 on retry).
- **Searched:** fetched a JFrog post on malicious models with a silent backdoor: it concerns code execution on model load, mentions model cards only in passing, so it is a different finding and was not substituted (A:141). arXiv API query on model card + code execution + Hugging Face: 0 results. Brave: HTTP 429 (A:142-144).
- **Why nothing qualified:** no page describes code execution via model-card rendering or unverifiable self-reported safety claims.
- **THIN EFFORT:** the search side rests on one arXiv query (0 results) and a Brave query that never returned.
- **User decision:** accept / reject / amend ______

### INC-02922 (INC-041) - Multi-agent trading system flash crash
- **Source:** A:199-206; O:1165; C:29. **Cited ref:** risk.net/ (homepage).
- **Searched:** one recorded Brave query (340 ms, $8M loss, multi-agent flash crash). Results: ainvest, a Lawfare piece, an MDPI taxonomy of AI-driven flash crashes, AIID incident 28 (the 2010 flash crash). None matches a quantitative firm losing over $8M in 340 ms (A:204).
- **Why nothing qualified:** neither the loss figure nor the timing appears in any result.
- **User decision:** accept / reject / amend ______

### INC-03247 (INC-040) - Synthetic data re-identification
- **Source:** A:229-236; O:1157; C:30. **Cited ref:** USENIX Security '25 conference landing page (names no paper).
- **Searched:** one recorded Brave query (synthetic health records, re-identification, membership inference, "23%"). Results were general synthetic-data membership-inference papers; none reports re-identifying 23% of patients using voter rolls and social media (A:234).
- **Why nothing qualified:** the specific finding was not found.
- **User decision:** accept / reject / amend ______

### INC-03444 (INC-046) - Adversarial embedding attacks on production RAG
- **Source:** A:238-245; O:1189; C:31. **Cited ref:** arxiv.org/abs/2407.00000 (HTTP 404; no such paper).
- **Searched:** arXiv API (adversarial + RAG + embedding + ada-002): 0 results. Nearest real work fetched: Zhong et al., arXiv 2310.19156 (retriever corpus poisoning); it does not test the OpenAI ada-002 or Cohere embed-v3 models the row states, so substituting it would describe a different incident (A:243).
- **Why nothing qualified:** nothing matches the stated attack and targets.
- **Note:** the nonexistent arXiv reference is **left in the row** (A:245); the unverified status is the only flag on it.
- **User decision:** accept / reject / amend ______

### INC-03447 (INC-019) - Agentic AI privilege escalation via tool chain manipulation  **(THIN EFFORT)**
- **Source:** A:247-256; O:1133; C:32. **Cited refs:** wiz.io blog post (HTTP 404 on fetch), USENIX Security '24 landing page (HTTP 200, contains neither "privilege" nor "agent").
- **Searched:** Brave (read-only role to administrator via IAM policy attachment): HTTP 429, tried twice, **no result obtained**. arXiv API: 0 results. USENIX page re-fetched once (A:252-255).
- **Why nothing qualified:** nothing was found, but the main discovery tool never answered; "no confirmed source" here means "no source found by an effort that was largely rate-limited". A human or a later retry could reasonably find one.
- **User decision:** accept / reject / amend ______

### INC-03491 (INC-063) - AI-generated CSAM detection evasion
- **Source:** A:283-290; O:1197; C:33. **Cited ref:** arxiv.org/abs/2311.16090 = "Self-correcting LLM-controlled Diffusion Models" (wrong paper).
- **Searched:** arXiv API queries on text-to-image safety-checker bypass (adversarial/jailbreak papers on text-to-image safeguards, none about CSAM-classifier evasion) and on CSAM + classifier + adversarial (0 results) (A:288).
- **Why nothing qualified:** no paper concerns evasion of CSAM-detection classifiers via negative prompts and LoRA models.
- **Note:** the wrong-paper reference stays in the row.
- **User decision:** accept / reject / amend ______

### INC-03570 (INC-045) - Claude context flooding
- **Source:** A:292-299; O:1181; C:34. **Cited ref:** arxiv.org/abs/2408.00000 (HTTP 404; no such paper).
- **Searched:** arXiv API: "denial-of-wallet" + LLM returned only 2026 papers that post-date a 2024 incident; "long-context" + "resource exhaustion" + LLM + prompts: 0 results (A:297).
- **Why nothing qualified:** no source names a 200K-token Claude flooding attack with the stated cost multiple.
- **Note:** the nonexistent arXiv reference stays in the row (A:298).
- **User decision:** accept / reject / amend ______

### INC-03810 (INC-025) - GitHub Copilot Workspace prompt injection
- **Source:** A:301-309; O:1205; C:35. **Cited refs:** github.com/advisories (global index, R1), invicti.com blog (HTTP 404).
- **Searched:** one Brave retry (Copilot Workspace + README + secrets): CSO Online, an Orca "RoguePilot" finding on Copilot in Codespaces (later and different), forum threads, vendor guides (A:307). The Embrace The Red Copilot Chat post was fetched and rejected: it is already the sole reference of INC-03808 and the word "Workspace" is absent from it (A:306). The first D130-2 tranche had re-pointed this row at it; that was reverted after gate bounce #1 (P:125).
- **Why nothing qualified:** no page documents a Copilot Workspace injection via repository files in 2024.
- **User decision:** accept / reject / amend ______

### INC-04310 (INC-042) - Uber ML platform lineage audit  **(THIN EFFORT; "unverified" = unfetchable by us)**
- **Source:** A:429-438; O:1173; C:36. **Cited ref:** uber.com/blog/engineering/ (blog index; HTTP 406 to our UA).
- **Searched:** a candidate Uber Michelangelo post also returned HTTP 406, so **no Uber page can be fetched by this project's fetcher at all**; Brave: HTTP 429, no result. A Wayback copy of the 2017 Michelangelo post was read for discovery only (not written to the corpus); it mentions feature stores but not "audit", "lineage" or "30" (A:434-437).
- **Why nothing qualified:** this is not evidence that the incident is false. The only authoritative host cannot be read by us, so the row cannot be confirmed or refuted by the current tooling. A human with a normal browser could settle it.
- **User decision:** accept / reject / amend ______

## 5. Specific items the gates asked the user to see

**5.1 INC-02454 stays `landmark` only through the corpus pin.** In a trial build the corrected text flipped `corpus` from `ai-harm` to `security`; the override pins it to the base value `ai-harm` (O:867; A:60-62). The row was demoted to `auto` (D:3080) but keeps `tier: landmark` (D:3082) only because of that pin (A:38; P:117 item c, P:111). The pin is an agent decision to preserve the base value, not a ruling.

**5.2 INC-04653 keeps DSGAI01.** The agent could drop DSGAI07 because the repo's own text ties it to secrets; DSGAI01 could not be checked against anything because no DSGAI vocabulary is committed in the repo (R:73-75, R:233-235; P:92 item 3). Related: D133 would document `owasp_dsgai` (P:236). Until then every DSGAI code kept on any of these rows (e.g. DSGAI09/13/14/17 on INC-02454, DSGAI14/15/16/21 on INC-02774) is unverified in the same way.

**5.3 INC-02899 MAESTRO note echoes the dropped claim.** The kept `L2/impact` note reads "Confidential business data exfiltrated via exposed agents" (O:1128; D:9436), and the three `mitigations` presuppose the dropped claim: agent enumeration protection, default-deny access, mandatory authentication (D:9439-9443; R:333-334). The gate asked that the user see this (P:92 item 3). Nothing rewrote the note: D130-2L's rule for MAESTRO was removal-only (R:52-55).

**5.4 `consent` tag: kept on INC-02454, dropped on INC-02774.** On INC-02774 it came from the old title ("consent and data minimization failures"); the new text says "legal basis", so it was removed (R:111). On INC-02454 the new text says images were collected "without consent" (the impact line), so it was kept (O:880; D:3074). The two outcomes follow one rule but look inconsistent; the gate asked that the user see it (P:92 item 3).

**5.5 `date`/`year` lag the re-derived text** (left as found; year tags follow `date`; R:335-337, A:498). From the audit: INC-02774 date 2025-03 vs decision announced 2024-12-20; INC-03004 2025-01 vs paper 2025-02-18; INC-03972 2024-10 vs paper 2024-09-17; INC-03472 2024-08 vs 2018 reporting and a 2023-05-18 EEOC document; INC-03955 2024-04 vs March 2023; INC-04221 2024-04 vs December 2023; INC-04653 2023-01 vs 2022-11-08. Agent observations not in those lists, from `D` dates against the audit text: INC-02454 2025-01 vs approval 2025-03-20; INC-04179 2024-01 vs reporting 2023-01-18 and 2023-08-02. Decision needed on whether a date correction is a separate task.

**5.6 Over-merges queued for WS4-T19** (the second legacy incident's `source_ids` and `mitigations` are still in the row; A:500, R:331-334): INC-02454 (INC-036 Clearview + INC-039 NYT v OpenAI), INC-02774 (INC-035 Garante + INC-050 noyb), INC-04179 (INC-044 Sama + INC-048 AI companion apps), INC-04142 (an AgentDojo source merged into RAG poisoning, A:364-369), INC-04067 (the model-stealing source merged into a system-prompt-extraction narrative, A:357-362). D130-2L removed the second incident's labels but not its ids or mitigations. A review decision on the over-merged rows is partly a decision about those splits.

**5.7 Other items the user may want to see (agent-observed, not gate-flagged).**
- **References dropped because our fetcher could not read them, not because they were shown wrong:** reuters.com ai-hiring (robots-refused, INC-03472), cyber.fsi.stanford.edu (403, INC-04221), dataprotection.ie DPC press release (404, INC-04955), atlas.mitre.org AML.CS0037 (404, INC-02899). All four are plausibly genuine primary sources; the rule applied was "every kept URL needs this-session fetch evidence" (P:116, P:129). The user may prefer to keep a primary source that cannot be fetched.
- **Severity left as the seed author set it** on INC-04955 (Critical), INC-04221 (Critical), INC-04653 (High), INC-02899 (Critical) although each was set against text since changed; the rubric (WS2-T5) is not built (R:63-68).
- **`rce` substring artifact** remains on three rows outside this review (INC-02549, INC-04263, INC-02186; R:326-330). Not part of this package.
- **LLM07 → AML.T0058/T0115.001 mapping** looks like a 2025-numbering leftover, corpus-wide (R:339-340). Not part of this package.
- INC-02454: the unverified Seventh Circuit lead (A:109, A:499) is worth a check before any release statement.
- **`[]` vs absent:** INC-02454, INC-04179, INC-04653 now have `maestro_layers: []`; INC-02774, INC-04179, INC-04653, INC-04955 have `mitre_atlas_tactics: []`; consumers treat them identically (R:291-294).

## 6. The 9 unchanged rows (examined in D130-2, not modified)

All nine are byte-identical to base (A:22-23, P:115). Listed so the reviewer can see what the audit looked at and did not touch. No decision is needed on them in this package.

| INC | legacy ids | why unchanged | where it goes next |
|---|---|---|---|
| INC-04142 | INC-016, INC-020 | R2 hit is a merge artifact: the AgentDojo arXiv paper is the genuine reference of a source merged into this RAG-poisoning row; the description is supported by the row's other two arXiv references (A:364-369) | WS4-T19 split question |
| INC-04067 | INC-065 | not unverified: row is sourced (ARXIV-2403.06634 and the Carlini model-stealing source); the defect is an over-merge with a legacy system-prompt-extraction narrative that no source supports (A:357-362). The first tranche's unverified override was removed after bounce #1 (P:126) | WS4-T19 split question |
| INC-08181 | INC-003, INC-007, INC-022 | R1 false positive: greshake.github.io is a project page whose fetched text names Bing Chat and indirect prompt injection, matching its reference title; the incident is sourced by two Embrace The Red posts (A:487-492) | none |
| INC-01015 | INC-113, LEGACY-INC-00159, LEGACY-INC-00218 | **deferred (mechanism gap):** flagged ref flowiseai.com is incidental to a feed-merged CVE/GHSA row with 443 references; a whole-list references override would freeze them (A:67-74) | D130-3 after D139-M `references_remove` |
| INC-01291 | INC-012, LEGACY-INC-00239 | **deferred (mechanism gap):** flagged ref langchain.com/; 178 references (A:75-81) | D130-3 after D139-M |
| INC-01589 | INC-102, LEGACY-INC-00195 | **deferred (mechanism gap):** flagged ref openclaw.ai/blog; 10 references (A:83-89) | D130-3 after D139-M |
| INC-02471 | LEGACY-INC-00130 | **deferred (mechanism gap):** flagged ref a personal GitHub profile (A:128-134) | D130-3 after D139-M |
| INC-02871 | LEGACY-INC-00131 | **deferred (mechanism gap):** flagged ref a personal GitHub profile (A:171-177) | D130-3 after D139-M |
| INC-04207 | INC-030 | **deferred (demotion vs landmark label):** removing the wrong arXiv 2402.06627 reference demotes the row under D130(c); its landmark-only `discovery_method` then fails `validate.py` check 6, and an override cannot delete the label. The planned change is recorded in the spec (A:393-401) | D139(b) field-clear mechanism, then D130-3 |

The six deferred rows are the ones ruled in D139(a) and (b) (P:135-139): D139-M builds `references_remove` and field-clear, then D130-3 handles them together with the remaining 126 rows. D139-M was dispatched 2026-10-16 (P:86). The remaining 126 rows of the D130 scope are not in this package either.

## 7. Recording decisions

Fill each "User decision:" line (accept / reject / amend, with a note if amend) and give the filled file or a list of `INC-id: decision` back to the foreman. The foreman records the decisions on the board (P), dispatches reverts or amendments as gated tasks, and updates the `pending user re-review` notes only through those tasks. No agent changes any `quality_tier` on the strength of an "accept".
