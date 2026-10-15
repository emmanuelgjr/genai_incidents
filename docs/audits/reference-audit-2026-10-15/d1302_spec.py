"""D130-2 specification: the 30 legacy-seed rows tripping R1/R2 (docs/audits/reference-detection-2026-10-14.md).

This module is DATA ONLY. build_overrides.py turns it into entries in
data/curation_overrides.json (the durable curation mechanism); export_evidence.py turns the
fetch cache into the committed evidence table. Nothing in `make build` imports this file.

Every URL in NEW_REFS was fetched in the 2026-10-15 session through ingest/common.fetch_once
(fetch_evidence.py) and its fetched page names the incident; the per-URL `tokens` are the strings
checked against the fetched text (export_evidence.py re-checks them and fails if one is absent).
Agent-suggested; not human-reviewed.
"""

AS_OF = "2026-10-15"
NOTE_PREFIX = "agent-suggested D130-2 reference replacement, 2026-10-15; pending user re-review."

# --- evidence pages: url -> (row-linking tokens that must appear in the fetched text) -------------
EVIDENCE = {
    "https://www.theverge.com/2022/11/8/23446821/microsoft-openai-github-copilot-class-action-lawsuit-ai-copyright-violation-training-data":
        ["Copilot", "class action", "software piracy on an unprecedented scale", "open-source code can be reproduced by AI"],
    "https://embracethered.com/blog/posts/2024/github-copilot-chat-prompt-injection-data-exfiltration/":
        ["GitHub Copilot Chat", "prompt injection", "exfiltrat", "June 12, 2024 - Fix confirmation"],
    "https://arxiv.org/abs/2409.11445":
        ["MathPrompt", "symbolic mathematics", "73.6", "13 state-of-the-art LLMs"],
    "https://arxiv.org/abs/2502.12893":
        ["H-CoT", "OpenAI o1/o3", "chain-of-thought", "98% to below 2%"],
    "https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10085432":
        ["OpenAI", "ChatGPT", "15 milioni", "20 dicembre 2024", "Tribunale di Roma"],
    "https://natlawreview.com/article/first-bipa-litigation-class-members-receive-equity-clearview-ai":
        ["Clearview", "BIPA", "23% equity stake", "March 20, 2025", "60 billion"],
    "https://www.regulatoryoversight.com/2025/04/51-75m-settlement-in-clearview-ai-biometric-privacy-litigation-illustrates-creative-resolution-for-startups-facing-parallel-litigation-and-enforcement-action/":
        ["Clearview", "$51.75 million", "23% equity stake", "BIPA"],
    "https://www.bbc.com/news/technology-66819174":
        ["TikTok", "345m", "children", "Data Protection Commission", "age verification"],
    "https://www.theguardian.com/technology/2023/aug/02/ai-chatbot-training-human-toll-content-moderator-meta-openai":
        ["Sama", "OpenAI", "Nairobi", "51 moderators", "$1.46 and $3.74"],
    "https://time.com/6247678/openai-chatgpt-kenya-workers/":
        ["Sama", "OpenAI", "Kenya", "$1.32"],
    "https://www.404media.co/laion-datasets-removed-stanford-csam-child-abuse/":
        ["LAION-5B", "Stanford", "3,226", "Stable Diffusion", "1,008"],
    "https://laion.ai/blog/relaion-5b/":
        ["Re-LAION-5B", "Stanford Internet Observatory", "2236 links were removed", "Internet Watch Foundation"],
    "https://www.lawandtheworkplace.com/2023/05/eeoc-releases-technical-document-on-ai-and-title-vii/":
        ["EEOC", "Title VII", "Assessing Adverse Impact", "May 18, 2023"],
    "https://www.bbc.com/news/technology-45809919":
        ["Amazon", "recruitment tool", "women", "2015", "abandoned"],
    "https://www.darkreading.com/endpoint-security/ai-blackmamba-keylogging-edr-security":
        ["BlackMamba", "HYAS", "polymorphic keylogger", "industry leading", "zero alerts"],
    "https://www.csoonline.com/article/575487/chatgpt-creates-mutating-malware-that-evades-detection-by-edr.html":
        ["BlackMamba", "HYAS", "EDR", "polymorphic"],
    "https://www.microsoft.com/en-us/security/blog/2024/06/26/mitigating-skeleton-key-a-new-type-of-generative-ai-jailbreak-technique/":
        ["Skeleton Key", "Llama3-70b-instruct", "GPT 3.5 Turbo", "Claude 3 Opus", "Cohere Commander R Plus"],
    "https://labs.zenity.io/p/a-copilot-studio-story-discovery-phase-in-ai-agents-f917":
        ["Copilot Studio", "Jun 11, 2025", "prompt injection via triggers"],
    "https://labs.zenity.io/p/a-copilot-studio-story-2-when-aijacking-leads-to-full-data-exfiltration-bc4a":
        ["Copilot Studio", "AIjacking", "Jul 7, 2025", "100 rows of data"],
}

# Lines added to a bare reference. type follows the surrounding corpus convention.
def _ref(title, url, typ):
    return {"title": title, "url": url, "type": typ}


VERGE = "https://www.theverge.com/2022/11/8/23446821/microsoft-openai-github-copilot-class-action-lawsuit-ai-copyright-violation-training-data"
EMBRACE = "https://embracethered.com/blog/posts/2024/github-copilot-chat-prompt-injection-data-exfiltration/"
GARANTE = "https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/10085432"
NATLAW = "https://natlawreview.com/article/first-bipa-litigation-class-members-receive-equity-clearview-ai"
REGOV = ("https://www.regulatoryoversight.com/2025/04/51-75m-settlement-in-clearview-ai-biometric-privacy-litigation-"
         "illustrates-creative-resolution-for-startups-facing-parallel-litigation-and-enforcement-action/")
BBC_TIKTOK = "https://www.bbc.com/news/technology-66819174"
GUARDIAN = "https://www.theguardian.com/technology/2023/aug/02/ai-chatbot-training-human-toll-content-moderator-meta-openai"
M404 = "https://www.404media.co/laion-datasets-removed-stanford-csam-child-abuse/"
LAION = "https://laion.ai/blog/relaion-5b/"
EEOC_TA = "https://www.lawandtheworkplace.com/2023/05/eeoc-releases-technical-document-on-ai-and-title-vii/"
BBC_AMZ = "https://www.bbc.com/news/technology-45809919"
DARK = "https://www.darkreading.com/endpoint-security/ai-blackmamba-keylogging-edr-security"
CSO = "https://www.csoonline.com/article/575487/chatgpt-creates-mutating-malware-that-evades-detection-by-edr.html"

NEW_REFS = {
    VERGE: _ref("The lawsuit against Microsoft, GitHub and OpenAI that could change the rules of AI copyright - The Verge (2022-11-08)", VERGE, "news"),
    EMBRACE: _ref("GitHub Copilot Chat: From Prompt Injection to Data Exfiltration - Embrace The Red (2024-06-14)", EMBRACE, "research"),
    "https://arxiv.org/abs/2409.11445": _ref("Jailbreaking Large Language Models with Symbolic Mathematics - arXiv:2409.11445 (2024-09-17)", "https://arxiv.org/abs/2409.11445", "research"),
    "https://arxiv.org/abs/2502.12893": _ref("H-CoT: Hijacking the Chain-of-Thought Safety Reasoning Mechanism to Jailbreak Large Reasoning Models, Including OpenAI o1/o3, DeepSeek-R1, and Gemini 2.0 Flash Thinking - arXiv:2502.12893 (2025-02-18)", "https://arxiv.org/abs/2502.12893", "research"),
    GARANTE: _ref("ChatGPT, il Garante privacy chiude l'istruttoria (press release) - Garante per la protezione dei dati personali (2024-12-20)", GARANTE, "regulatory"),
    NATLAW: _ref("A First in BIPA Litigation: Class Members Receive Equity in Clearview AI - National Law Review (2025-07-22)", NATLAW, "news"),
    REGOV: _ref("$51.75M Settlement in Clearview AI Biometric Privacy Litigation Illustrates Creative Resolution for Startups - Regulatory Oversight (2025-04-30)", REGOV, "news"),
    BBC_TIKTOK: _ref("TikTok fined 345m euro over children's data privacy - BBC News (2023-09-15)", BBC_TIKTOK, "news"),
    GUARDIAN: _ref("'It's destroyed me completely': Kenyan moderators decry toll of training of AI models - The Guardian (2023-08-02)", GUARDIAN, "news"),
    M404: _ref("Largest Dataset Powering AI Images Removed After Discovery of Child Sexual Abuse Material - 404 Media (2023-12-20)", M404, "news"),
    LAION: _ref("Releasing Re-LAION-5B: transparent iteration on LAION-5B with additional safety fixes - LAION (2024-08-30)", LAION, "reference"),
    EEOC_TA: _ref("EEOC Releases Technical Document on AI and Title VII - Law and the Workplace (2023-05-23)", EEOC_TA, "legal"),
    BBC_AMZ: _ref("Amazon scrapped 'sexist AI' tool - BBC News (2018-10-10)", BBC_AMZ, "news"),
    DARK: _ref("AI-Powered 'BlackMamba' Keylogging Attack Evades Modern EDR Security - Dark Reading (2023-03-08)", DARK, "news"),
    CSO: _ref("ChatGPT creates mutating malware that evades detection by EDR - CSO Online (2023-06-06)", CSO, "news"),
}

# --- FIXED rows ---------------------------------------------------------------------------------
# key: curation-override key (a source_id of the row; where the row already has an override entry the
#      existing key is reused, because apply_curation_overrides applies only the FIRST matching key).
# replace: {old_url: [new ref urls]}  ([] = remove: an equivalent verified source is already present).
FIXED = {
    "INC-04653": dict(
        key="INC-008", replace={"https://githubcopilotlitigation.com/": [VERGE]},
        description=("GitHub Copilot, GitHub's AI coding assistant unveiled in June 2021, is trained on public code repositories, "
                     "many of them published with open-source licenses. A proposed class action lawsuit against Microsoft, GitHub "
                     "and OpenAI (reported by The Verge on 2022-11-08) alleges that the creation of Copilot relies on \"software "
                     "piracy on an unprecedented scale\"; the key question in the lawsuit is whether open-source code can be "
                     "reproduced by AI without attached licenses."),
        impact="License compliance questions over open-source code reproduced by an AI coding assistant; proposed class action lawsuit filed",
        affected="GitHub Copilot users and the authors of open-source code used to train it",
        figures_dropped=["~1% of the time (NYU researchers; not in any cited source)"],
        also_dropped=["claims that Copilot reproduced API keys, passwords and private keys (no cited source)"],
        queries=["Doe v. GitHub Copilot class action complaint (Bing via discovery tool: irrelevant results)", "direct candidate URLs fetched: en.wikipedia.org/wiki/GitHub_Copilot, The Verge 2022-11-08"],
        rejected=["en.wikipedia.org/wiki/GitHub_Copilot (secondary encyclopedia; The Verge is a dated news report naming the suit)"],
        old_ref_kind="githubcopilotlitigation.com/: law-firm campaign site homepage (R1 homepage)",
    ),
    "INC-03810": dict(
        key="INC-025", replace={"https://github.com/advisories": [EMBRACE]},
        description=("The security researcher behind the Embrace The Red blog reported that the GitHub Copilot Chat extension for "
                     "VS Code was vulnerable to data exfiltration via prompt injection when analyzing untrusted source code. "
                     "Copilot Chat interpreted and rendered markdown returned by the LLM, including images, so carefully crafted "
                     "instructions in a source code file could make the LLM return image links that are retrieved automatically, "
                     "with information from the chat context appended as a query parameter. Reported to GitHub on 2024-02-25, "
                     "the fix (Copilot Chat no longer renders markdown images) was confirmed on 2024-06-12 and the write-up "
                     "published on 2024-06-14."),
        impact="Chat-context data could be exfiltrated to an attacker-controlled server through automatically retrieved markdown images when a developer analyzed a file containing attacker instructions",
        affected="GitHub Copilot Chat VS Code extension (before the June 2024 fix)",
        figures_dropped=[],
        also_dropped=["Copilot Workspace and README/comment-file delivery claims; \"zero-interaction\" and open-source-contributor risk claims (the source covers Copilot Chat only)"],
        queries=["direct candidate: Embrace The Red 2024-06-14 Copilot Chat post"],
        rejected=["github.com/advisories (global advisory index, names nothing)", "invicti.com/blog/web-security/prompt-injection-attacks/ (the row's other reference: HTTP 404, not changed)"],
        old_ref_kind="github.com/advisories: GitHub global advisory database index (R1 depth1-non-slug)",
    ),
    "INC-03972": dict(
        key="INC-027", replace={"https://arxiv.org/abs/2410.15262": ["https://arxiv.org/abs/2409.11445"]},
        description=("MathPrompt is a jailbreaking technique that encodes harmful natural-language prompts into mathematical problems, "
                     "exploiting LLMs' capabilities in symbolic mathematics to bypass their safety mechanisms. Across 13 "
                     "state-of-the-art LLMs the authors report an average attack success rate of 73.6%, and an analysis of embedding "
                     "vectors shows a substantial semantic shift between original and encoded prompts, which helps explain the "
                     "attack's success. The authors conclude that existing safety training mechanisms do not generalize to "
                     "mathematically encoded inputs."),
        impact="Average attack success rate of 73.6% across 13 LLMs as reported by the authors; indicates a gap between mathematical-reasoning capability and safety-training coverage",
        affected="13 state-of-the-art LLMs evaluated in the paper (the abstract does not enumerate them)",
        figures_dropped=["8 frontier models (source says 13)", "model list GPT-4o/Claude 3.5/Gemini 1.5/Llama 3/Mistral (not in the fetched abstract)", "\"UCSB\" affiliation (not in the fetched abstract)"],
        also_dropped=["LAAF taxonomy E-class sentence (not from this source)"],
        queries=["recalled title \"MathPrompt\" -> arxiv.org/abs/2409.11445 fetched directly"],
        rejected=["arxiv.org/abs/2410.15262 = \"HyQE: Ranking Contexts with Hypothetical Query Embeddings\" (R2 title+no-overlap; wrong paper)"],
        old_ref_kind="arXiv 2410.15262: real paper on a different topic (HyQE)",
    ),
    "INC-04207": dict(
        key="INC-030", replace={"https://arxiv.org/abs/2402.06627": []},
        description=("Microsoft disclosed the Skeleton Key jailbreak technique, which works by using a multi-turn strategy to cause a "
                     "model to ignore its guardrails. It asks the model to augment, rather than change, its behavior guidelines so "
                     "that it responds to any request, providing a warning rather than refusing if the output might be offensive, "
                     "harmful or illegal. Testing from April to May 2024 showed the jailbreak working on Meta Llama3-70b-instruct, "
                     "Google Gemini Pro, OpenAI GPT 3.5 Turbo, OpenAI GPT 4o, Mistral Large, Anthropic Claude 3 Opus and Cohere "
                     "Commander R Plus. Microsoft describes it as an Explicit: forced instruction-following attack that relies "
                     "on the attacker already having legitimate access to the model."),
        impact="The jailbreak bypassed guardrails on all seven models Microsoft tested, allowing ordinarily forbidden behaviors from harmful content to overriding the model's usual decision-making rules",
        affected="Meta Llama3-70b-instruct, Google Gemini Pro, OpenAI GPT 3.5 Turbo, OpenAI GPT 4o, Mistral Large, Anthropic Claude 3 Opus, Cohere Commander R Plus (models tested by Microsoft)",
        figures_dropped=[],
        also_dropped=["GPT-4 (not in the tested list), the omitted Cohere Commander R Plus is added; \"requires no technical skill\" and \"RLHF-trained models\" generalizations (not in the source)"],
        queries=["the Microsoft Security Blog post is the row's other reference (not flagged); re-fetched 2026-10-15"],
        rejected=["no arXiv paper for Skeleton Key identified; arxiv.org/abs/2402.06627 = \"Feedback Loops With Language Models Drive In-Context Reward Hacking\" (R2; wrong paper); removed rather than replaced because the verified Microsoft post is already a reference"],
        old_ref_kind="arXiv 2402.06627: real paper on a different topic (in-context reward hacking)",
    ),
    "INC-03004": dict(
        key="INC-033", replace={"https://arxiv.org/abs/2501.01234": ["https://arxiv.org/abs/2502.12893"]},
        description=("Researchers introduced H-CoT (Hijacking Chain-of-Thought), a jailbreak that leverages a model's own displayed "
                     "intermediate reasoning to jailbreak its chain-of-thought safety reasoning mechanism, together with the "
                     "Malicious-Educator benchmark, which disguises extremely dangerous or malicious requests beneath seemingly "
                     "legitimate educational prompts. They report severe security flaws in commercial large reasoning models "
                     "including OpenAI o1/o3, DeepSeek-R1 and Gemini 2.0 Flash Thinking: OpenAI's o1 initially maintained a "
                     "refusal rate of about 98%, subsequent model updates significantly compromised its safety, and under H-CoT "
                     "refusal rates dropped from 98% to below 2%."),
        impact="Under H-CoT the refusal rate of OpenAI o1 dropped from about 98% to below 2% (authors' report); displaying the safety reasoning makes it available for hijacking",
        affected="Large reasoning models evaluated by the authors: OpenAI o1/o3, DeepSeek-R1, Gemini 2.0 Flash Thinking",
        figures_dropped=[],
        also_dropped=["\"OpenAI acknowledged the attack class\" and o1-mini/o3-mini model list (not in the source)"],
        queries=["recalled candidate H-CoT (Kuo et al.) -> arxiv.org/abs/2502.12893 fetched directly; title names OpenAI o1/o3 and chain-of-thought"],
        rejected=["arxiv.org/abs/2501.01234 = \"Impact of QCD sum rules coupling constants on neutron stars structure\" (R2; placeholder-pattern id, unrelated paper)"],
        old_ref_kind="arXiv 2501.01234: placeholder-pattern id resolving to an unrelated QCD paper",
    ),
    "INC-02774": dict(
        key="INC-035", replace={"https://www.garanteprivacy.it/": [GARANTE], "https://iapp.org/news/": []},
        description=("On 2024-12-20 the Italian data protection authority (Garante per la protezione dei dati personali) announced "
                     "that it had closed its investigation of OpenAI's ChatGPT service, opened in March 2023, with a corrective and "
                     "sanctioning decision and a fine of EUR 15 million, calculated also taking into account the company's "
                     "cooperative attitude. The Garante found that OpenAI had not notified it of the data breach suffered in March "
                     "2023, had processed users' personal data to train ChatGPT without first identifying an adequate legal basis, "
                     "had breached the principle of transparency and the related information obligations, and had provided no "
                     "age-verification mechanism, exposing children under 13 to responses inappropriate to their development. It "
                     "ordered OpenAI to run a six-month institutional communication campaign on radio, television, newspapers and "
                     "the internet, and passed the case file to the Irish DPC as lead supervisory authority. The Garante's page "
                     "now notes that decision No. 755 of 2 November 2024 was temporarily removed from its website after judgment "
                     "No. 4153/2026 of the Tribunal of Rome (published 2026-03-18) upheld OpenAI's opposition to it."),
        impact="EUR 15 million fine and a six-month communication campaign ordered against OpenAI (decision of 2 November 2024, announced 2024-12-20); the decision was later opposed successfully before the Tribunal of Rome",
        affected="OpenAI / ChatGPT (Italy; case referred to the Irish DPC as lead supervisory authority)",
        figures_dropped=["GDPR Articles 5, 6, 13 and 25 list (the Garante page names no article numbers)", "\"opt-out mechanisms\" remedy (the page orders a communication campaign, not an opt-out mechanism)"],
        also_dropped=["\"first major GDPR enforcement action specifically targeting an LLM provider\" (not in the source)"],
        queries=["direct candidate: Garante docweb press release (fetched OK 2026-10-15)", "WebFetch discovery of the same page returned its title/date before the common.py fetch"],
        rejected=["iapp.org/news/ = IAPP news index (R1), removed: the Garante press release is the primary source", "noyb complaint reference kept (not flagged; it concerns the 2024 noyb complaint, not this decision)"],
        old_ref_kind="garanteprivacy.it/: regulator homepage (R1); iapp.org/news/: publisher news index (R1)",
    ),
    "INC-02454": dict(
        key="INC-036", replace={"https://www.reuters.com/legal/": [NATLAW], "https://www.eff.org/": [REGOV]},
        pin={"corpus": "ai-harm"},  # base value; the corpus classifier flips it to "security" on the corrected text (WS0-T3 coupling)
        title="Clearview AI facial-image scraping - BIPA class action settlement for a 23% equity stake",
        description=("Class members in consolidated Illinois Biometric Information Privacy Act (BIPA) litigation against Clearview AI, a "
                     "facial recognition company that built a database of more than 60 billion facial images by scraping photographs "
                     "from the internet, reached a settlement that U.S. District Judge Sharon Johnson Coleman approved on 2025-03-20. "
                     "Unusually, the settlement gives the class a 23% equity stake in Clearview rather than a cash fund; commentary "
                     "values the stake at approximately $51.75 million as of January 2024, with payment triggered by events such as an IPO or a "
                     "liquidation event. State attorneys general objected to the settlement."),
        impact="BIPA class settlement paid as a 23% equity stake in Clearview AI for people whose facial images were collected without consent; first-of-its-kind equity-based resolution of biometric privacy litigation",
        affected="Clearview AI; individuals whose biometric data was scraped (nationwide BIPA settlement class)",
        figures_dropped=["USD 50 million fund / \"$50M\" (sources: 23% equity stake, about $51.75 million)", "\"billions of facial images\" -> sourced figure is more than 60 billion"],
        also_dropped=["racial-bias findings, bias testing, consent for US collection and third-party audits as settlement terms (none in the sources; the case is about scraping and BIPA)", "\"legal precedent that training-data bias creates financial liability\""],
        queries=["Brave via discovery tool: \"Clearview AI BIPA class action settlement approved 2025 equity stake 23%\" -> natlawreview, regulatoryoversight, iclg, constangy, Miami Law Review (first ten results)"],
        rejected=["reuters.com/legal/ = Reuters section index; reuters.com robots.txt refuses our UA, so contents cannot be verified", "eff.org/ = EFF homepage, reference title claimed \"AI copyright training data legal analysis\" (mismatch)", "en.wikipedia.org/wiki/Clearview_AI (fetched; secondary, says 2024 agreement; not needed)", "Discovery note, UNVERIFIED lead: a search-result snippet reported a July 2026 Seventh Circuit vacatur of the settlement; no fetched source in this session confirms it, so it is NOT in the description"],
        old_ref_kind="reuters.com/legal/: Reuters section index (R1; robots-refused); eff.org/: EFF homepage (R1)",
    ),
    "INC-04955": dict(
        key="INC-043", replace={"https://www.reuters.com/technology/": [BBC_TIKTOK]},
        description=("On 2023-09-15 Ireland's Data Protection Commission (DPC) fined TikTok EUR 345 million under the GDPR for how the "
                     "app handled children's data in 2020, particularly around age verification and privacy settings. The DPC found "
                     "that TikTok had not been transparent enough with children about its privacy settings and that accounts made "
                     "by users aged 13 to 17 were public by default on registration, which the Data Protection Commissioner said "
                     "infringed the GDPR's data-protection-by-design-and-by-default requirements. TikTok was given three months to "
                     "bring its data processing into compliance and said it respectfully disagreed with the decision, "
                     "particularly the level of the fine."),
        impact="EUR 345 million GDPR fine, at the time the biggest TikTok had received from regulators; three months to bring data processing into compliance",
        affected="TikTok / ByteDance; users aged 13 to 17 whose accounts were public by default in 2020",
        figures_dropped=["EUR 12 billion Project Clover investment (no fetched source gives it)"],
        also_dropped=["Project Clover mandate and data-localization legal-precedent claims (no fetched source supports them); the row's title still mentions Project Clover"],
        queries=["Brave via discovery tool: \"DPC TikTok 345 million fine children data decision press release\" -> DPC release, Variety, BBC, Matheson, IAPP (first ten)"],
        rejected=["reuters.com/technology/ = Reuters section index (R1)", "dataprotection.ie press-release URLs (the row's own DPC reference and the Brave-listed one): HTTP 404 for our UA, not usable; the row's own DPC reference is unchanged", "en.wikipedia.org/wiki/TikTok (secondary; gives the fine, not Project Clover cost)"],
        old_ref_kind="reuters.com/technology/: Reuters section index (R1)",
    ),
    "INC-04179": dict(
        key="INC-044", replace={"https://www.theguardian.com/technology/": [GUARDIAN]},
        description=("TIME and The Guardian reported on the working conditions of data labelers and content moderators employed by Sama, "
                     "a California-headquartered data annotation company, on OpenAI's behalf in Nairobi, Kenya. TIME (2023-01-18) "
                     "reported that Sama data labelers were paid a take-home wage of between around $1.32 and $2 per hour, depending "
                     "on seniority and performance. The Guardian (2023-08-02) reported that the 51 moderators in Nairobi working on "
                     "Sama's OpenAI account reviewed texts, and some images, depicting graphic scenes of violence, self-harm, "
                     "murder, rape, necrophilia and child abuse, and that in a petition they allege psychological trauma, low pay "
                     "and abrupt dismissal; a Sama spokesperson said workers were paid between $1.46 and $3.74 an hour."),
        impact="Alleged psychological trauma, low pay and abrupt dismissal for annotation workers in an AI training supply chain; pay reported as $1.32-$2/hour (TIME) and $1.46-$3.74/hour (Sama statement to The Guardian)",
        affected="Sama content moderators and data labelers in Nairobi, Kenya working on OpenAI's account",
        figures_dropped=[],
        also_dropped=["Scale AI, India and Philippines workers, medical/legal/private records accessible without need-to-know, annotation-metadata consent claims (no fetched source). The row's title still names Scale AI; the third reference (NYT, Character.AI lawsuit) is unrelated to this incident and is NOT changed (not flagged by R1/R2)"],
        queries=["Brave via discovery tool: \"Guardian Sama Kenya content moderators OpenAI data labelling exploitation\" -> the Guardian 2023-08-02 article (first result)"],
        rejected=["theguardian.com/technology/ = Guardian section index (R1)"],
        old_ref_kind="theguardian.com/technology/: Guardian section index (R1)",
    ),
    "INC-04221": dict(
        key="INC-049", replace={"https://www.bbc.co.uk/news/": [M404, LAION]},
        description=("In December 2023 a Stanford Internet Observatory study, reported by 404 Media, found 3,226 suspected instances of "
                     "child sexual abuse material (CSAM), 1,008 of which were externally validated, in LAION-5B, the machine learning "
                     "dataset used by Stable Diffusion and other major AI products. LAION took LAION-5B and LAION-400M down "
                     "temporarily out of an abundance of caution to ensure they were safe before republishing. On 2024-08-30 LAION "
                     "released Re-LAION-5B, cleaned of known links to suspected CSAM using hash lists from the Internet Watch "
                     "Foundation and the Canadian Center for Child Protection, in which 2236 links were removed."),
        impact="Suspected CSAM links found in a web-scale training dataset used for image-generation models; the dataset was withdrawn and later re-released with known links removed",
        affected="LAION-5B and LAION-400M, and models trained on them such as Stable Diffusion",
        figures_dropped=["\"over 3,000\" (sources: 3,226 suspected instances, 1,008 externally validated)"],
        also_dropped=["Stability AI legal action in the UK and US, negative-prompt/fine-tuning/model-merging filter bypasses, and the legal-liability conclusion (no fetched source). The row's title still names Stability AI and synthetic CSAM generation. The Stanford SIO reference (HTTP 403 to our UA) is unchanged"],
        queries=["Brave via discovery tool: \"LAION-5B CSAM Stanford Internet Observatory report LAION removes datasets\" -> 404 Media, TechCrunch, LAION blog, Ars Technica (first ten)"],
        rejected=["bbc.co.uk/news/ = BBC News front page (R1)", "TechCrunch/Ars Technica 2024-08 items (not fetched; LAION's own post is the primary source)"],
        old_ref_kind="bbc.co.uk/news/: BBC News front page (R1)",
    ),
    "INC-03472": dict(
        key="INC-074", replace={"https://www.eeoc.gov/ai": [BBC_AMZ, EEOC_TA]},
        description=("In 2018 Reuters reported, and the BBC summarized on 2018-10-10, that Amazon had scrapped an experimental machine-learning "
                     "recruitment tool that scored candidates from one to five stars: by 2015 it was clear the system was not rating "
                     "candidates in a gender-neutral way because it was built on CVs submitted to the firm mostly by men, and it "
                     "penalised CVs that included the word \"women\"; the program was edited to be neutral to the term but could not "
                     "be relied on, and the project was abandoned. On 2023-05-18 the US EEOC released technical assistance on "
                     "assessing adverse impact in software, algorithms and AI used in employment selection procedures under Title "
                     "VII, stating that an employer can be held responsible for an algorithmic selection procedure that has an "
                     "adverse impact even if the tool is designed or administered by a software vendor."),
        impact="Gender bias in an automated hiring tool led to its abandonment; EEOC technical assistance (May 2023) on disparate impact of algorithmic selection tools",
        affected="Job candidates, particularly women applying through automated CV screening",
        figures_dropped=[],
        also_dropped=["\"Several vendors settled with affected candidates\" and \"multiple enterprise AI recruiting tools\" (no fetched source). The row's other reference reuters.com/technology/ai-hiring-bias-settlements-2024/ is robots-refused (cannot be verified) and was NOT changed (not flagged by R1/R2)"],
        queries=["Brave via discovery tool: \"EEOC technical assistance artificial intelligence Title VII adverse impact software algorithms employment selection\" -> law-firm summaries of the 2023-05-18 EEOC document (first ten)", "recalled BBC 2018 article on Amazon's recruiting tool fetched directly"],
        rejected=["eeoc.gov/ai = agency topic page (R1); eeoc.gov/laws/guidance/select-issues-... HTTP 404 for our UA (the agency withdrew the document in Jan 2025 per search-result metadata; not asserted here)"],
        old_ref_kind="eeoc.gov/ai: agency topic landing page (R1)",
    ),
    "INC-03955": dict(
        key="INC-075", replace={"https://arxiv.org/abs/2310.07906": [DARK, CSO]},
        description=("Researchers from HYAS Labs demonstrated BlackMamba, a proof-of-concept attack that uses a large language model (the "
                     "technology behind ChatGPT) to synthesize polymorphic keylogger functionality on the fly. The attack is "
                     "\"truly polymorphic\" because it resynthesizes its keylogging capability every time it executes, and it works "
                     "without command-and-control infrastructure. HYAS reported testing it against an EDR system that was not "
                     "identified but was characterized as \"industry leading\", often resulting in zero alerts or detections. "
                     "Captured data such as usernames, passwords and credit card numbers was sent out through a malicious "
                     "Microsoft Teams channel. Reported in March 2023."),
        impact="A proof-of-concept LLM-synthesized polymorphic keylogger evaded an unnamed EDR product in the researchers' tests (often zero alerts), challenging signature and behavioral detection",
        affected="Endpoint detection and response products (one unidentified \"industry leading\" EDR tested)",
        figures_dropped=[],
        also_dropped=["named EDR platforms CrowdStrike, SentinelOne and Microsoft Defender (the sources say the tested EDR was not identified)"],
        queries=["Brave via discovery tool: \"LLM generated polymorphic malware evades EDR research ChatGPT BlackMamba CyberArk\" -> Reddit, SentinelOne, CSO Online, Dark Reading (first ten)"],
        rejected=["arxiv.org/abs/2310.07906 = \"Power Tracking Control of Heterogeneous Populations of TCLs with Partial Observations\" (R2; unrelated paper)", "sentinelone.com/blog/blackmamba-... (listed, not fetched; commentary rather than the finding)"],
        old_ref_kind="arXiv 2310.07906: real paper on an unrelated topic (thermostatically controlled loads)",
    ),
    "INC-01589": dict(
        key="INC-102", replace={"https://openclaw.ai/blog": []},
        title="OpenClaw AI agent security crisis - one-click RCE (CVE-2026-25253) and 341 malicious marketplace skills",
        description=("OpenClaw (previously Clawdbot and Moltbot), an open-source AI agent, amassed over 135,000 GitHub stars within weeks "
                     "and became the subject of a security crisis in early 2026. CVE-2026-25253, a one-click remote code execution "
                     "through authentication token exfiltration from gatewayUrl (CVSS 8.8 in the GitHub advisory), was patched in "
                     "version 2026.1.29 before public disclosure. Censys identified 21,639 publicly exposed instances on 2026-01-31, "
                     "and researchers later confirmed 341 malicious skills out of 2,857 on the ClawHub marketplace, roughly 12% of "
                     "the registry, which instructed users to run external code that installed keyloggers on Windows or Atomic "
                     "Stealer malware on macOS."),
        impact="One-click remote code execution (CVE-2026-25253); 341 malicious ClawHub skills installing infostealers; 21,639 exposed instances identified by Censys",
        affected="OpenClaw users and instances; the ClawHub skills marketplace",
        figures_dropped=["138 CVEs in 63 days (in title and description; not in any fetched source)"],
        also_dropped=["\"credential theft and lateral movement across connected enterprise SaaS apps\" (no fetched source); \"over 21,000\" is replaced by the sourced 21,639; the ATLAS reference atlas.mitre.org/studies/AML.CS0050 returns 404 and is NOT changed"],
        queries=["figure check against the row's other references: reco.ai blog and the openclaw GHSA advisory fetched 2026-10-15"],
        rejected=["openclaw.ai/blog = project blog index (R1); fetched title \"Blog - OpenClaw\"; no post named; removed because the reco.ai write-up and the GHSA advisory are already references"],
        old_ref_kind="openclaw.ai/blog: project blog index (R1)",
    ),
    "INC-02899": dict(
        key="INC-105", replace={"https://labs.zenity.io/": []},
        description=("Zenity Labs researchers reported that Microsoft Copilot Studio agents were vulnerable to prompt injection via "
                     "triggers (reported to MSRC on 2025-02-21; Microsoft confirmed the behaviour on 2025-03-13 and issued a fix on "
                     "2025-04-24). In a two-part write-up (2025-06-11 discovery phase, 2025-07-07 exfiltration phase) they showed "
                     "how an attacker could discover a customer-service agent's knowledge sources and tools and then use "
                     "prompt injection (\"AIjacking\") to exfiltrate the agent's knowledge-source data, about 100 rows of data in a "
                     "single iteration, and customer records reachable through the agent's connected tools."),
        impact="Data exfiltration from a Copilot Studio agent's knowledge sources and connected customer-data tools through prompt injection",
        affected="Microsoft Copilot Studio agents with knowledge sources and customer-data tools",
        figures_dropped=[],
        also_dropped=["\"public by default\", \"lacked authentication\" and attacker enumeration of exposed agents (neither Zenity post says this); the row's title still says \"public by default\". The ATLAS reference AML.CS0037 returns 404 and is NOT changed"],
        queries=["figure/claim check against the row's two Zenity references, fetched 2026-10-15"],
        rejected=["labs.zenity.io/ = Zenity Labs blog homepage (R1); removed because the two specific Zenity posts are already references"],
        old_ref_kind="labs.zenity.io/: vendor blog homepage (R1)",
    ),
    "INC-02471": dict(
        key="CVE-2025-61590", replace={"https://github.com/MaccariTA": []},
        description=None, impact=None, affected=None,
        figures_dropped=[], also_dropped=[],
        queries=["claim check against the row's own Cursor advisory GHSA-xg6w-rmh5-r77r (\"RCE via .code-workspace files using Prompt Injection\"), fetched 2026-10-15"],
        rejected=["github.com/MaccariTA = a GitHub user profile (R1), cited as \"research\"; it credits the reporter, it is not a source for the incident. The reporter credit is already carried by the row's existing curation note"],
        old_ref_kind="github.com/MaccariTA: personal GitHub profile (R1)",
    ),
    "INC-02871": dict(
        key="CVE-2025-61591", replace={"https://github.com/Y4tacker": []},
        description=None, impact=None, affected=None,
        figures_dropped=[], also_dropped=[],
        queries=["claim check against the row's own Cursor advisory GHSA-wj33-264c-j9cq (\"Remote Code Execution in Cursor CLI via Cursor Agent MCP OAuth2 Communication\"), fetched 2026-10-15"],
        rejected=["github.com/Y4tacker = a GitHub user profile (R1), cited as \"research\"; credits the reporter, not a source"],
        old_ref_kind="github.com/Y4tacker: personal GitHub profile (R1)",
    ),
    "INC-01291": dict(
        key="INC-012", replace={"https://www.langchain.com/": []},
        description=None, impact=None, affected=None,
        figures_dropped=[], also_dropped=[],
        queries=["claim check against the row's own references: langchain issue #814 and PR #1119 (LLMMathChain exec), fetched 2026-10-15; the description is the CVE record text"],
        rejected=["langchain.com/ = vendor homepage (R1); removed because specific advisory/issue/PR references (many) are already present"],
        old_ref_kind="langchain.com/: vendor homepage (R1)",
    ),
    "INC-01015": dict(
        key="INC-113", replace={"https://flowiseai.com": []},
        description=None, impact=None, affected=None,
        figures_dropped=[], also_dropped=[],
        queries=["claim check against the row's own Flowise advisory GHSA-5w3r-f6gm-c25w (\"Authenticated Command Execution and Sandbox Bypass via Puppeteer and Playwright Packages\"), fetched 2026-10-15; the description is the CVE record text"],
        rejected=["flowiseai.com = vendor homepage (R1); removed because the GHSA advisory, PR and NVD references are already present"],
        old_ref_kind="flowiseai.com: vendor homepage (R1)",
    ),
}

# Rows examined and deliberately NOT changed.
UNCHANGED = {
    "INC-04142": ("R2 is a merge artifact, not a fabricated reference. The row's source_ids include ARXIV-2406.13352 and REDTEAM-agentdojo, "
                  "so the AgentDojo arXiv paper IS the genuine reference of a source merged into this RAG-poisoning row; the description "
                  "(PoisonedRAG, Chaudhari et al. = Phantom) is supported by the row's other two arXiv references (fetched 2026-10-15: "
                  "PoisonedRAG abstract says five malicious texts per target question; Phantom authors are Chaudhari et al.). The defect is an "
                  "over-merge of an AgentDojo source into this row (a WS4-T19 split question), which this task may not decide. The "
                  "description's \"1-5 documents\" is therefore also left (PoisonedRAG says five)."),
    "INC-08181": ("R1 false positive. https://greshake.github.io/ is a project page, fetched title \"Prompt Injections are bad, mkay?\", whose text "
                  "names Bing Chat and indirect prompt injection, matching the reference title \"Indirect Prompt Injection Threats: Bing Chat Data "
                  "Pirate\". The incident itself (Rehberger's ChatGPT plugin exfiltration) is sourced by the row's two Embrace The Red posts "
                  "(fetched 2026-10-15, both name the incident). Nothing replaced."),
}

# --- UNVERIFIED rows (D130 ruling b; D130-1 mechanism) ---------------------------------------------
UNVERIFIED = {
    "INC-03447": dict(key="INC-019", effort=[
        "Row cites Wiz (\"AI agents and privilege escalation risks in cloud environments\") and USENIX Security '24 (conference landing page).",
        "https://www.wiz.io/blog/the-urgent-need-for-ai-security-guardrails fetched via common.py 2026-10-15: HTTP 404. USENIX '24 landing page (R1) names no paper.",
        "Discovery queries: Brave \"Wiz AI agent cloud IAM privilege escalation prompt injection read-only administrator\" - rate-limited (HTTP 429), no result obtained (tried twice); arXiv API all:\"privilege escalation\" AND all:agents AND all:IAM AND all:cloud -> 0 results. The attack chain (iam:AttachRolePolicy from a read-only role in AWS, Azure and GCP) is not named by any fetched page.",
        "Outcome: no confirmed source names this incident."]),
    "INC-02353": dict(key="INC-037", effort=[
        "Row cites msrc.microsoft.com/ (MSRC portal homepage, fetched 2026-10-14 title \"MSRC - Microsoft Security Response Center\").",
        "Discovery query (Brave): \"Azure OpenAI structured outputs content filter bypass JSON schema jailbreak\" -> Microsoft Learn structured-outputs/content-filter documentation and two Microsoft Q&A threads about structured responses being blocked by the content filter (the opposite of a bypass); none describes a bypass via JSON-schema field names such as weapon_instructions.",
        "Outcome: no confirmed source names this incident."]),
    "INC-02703": dict(key="INC-038", effort=[
        "Row cites jfrog.com/blog/ (blog index) and huggingface.co/blog/security (index-segments).",
        "Fetched https://jfrog.com/blog/data-scientists-targeted-by-malicious-hugging-face-ml-models-with-silent-backdoor/ (2026-10-15): JFrog's malicious-model research. It concerns code execution on model LOAD (pickle payload) and mentions a model card only in passing (a card warning not to download a model); it does not describe code execution on model-card rendering or unverifiable self-reported safety claims, so it is a different finding and was not substituted.",
        "Discovery query (arXiv API): all:\"model card\" AND all:\"code execution\" AND all:\"Hugging Face\" -> 0 results; Brave query on the same topic was rate-limited (HTTP 429).",
        "Outcome: no confirmed source names the described model-card attack."]),
    "INC-03247": dict(key="INC-040", effort=[
        "Row cites the USENIX Security '25 conference landing page (R1; title \"USENIX Security '25 / USENIX\").",
        "Discovery query (Brave): \"synthetic health records re-identification membership inference 23% USENIX Security 2025\" -> general synthetic-data MIA papers (Annamalai 2024, Stadler 2022, others); none reports re-identifying 23% of patients using voter rolls and social media. The result page itself noted it could not confirm the 23% figure.",
        "Outcome: no confirmed source names this incident."]),
    "INC-02922": dict(key="INC-041", effort=[
        "Row cites risk.net homepage (R1; fetched title \"Risk.net - Financial Risk Management News Analysis\").",
        "Discovery query (Brave): \"multi-agent AI trading system cascading failure 340 milliseconds $8M loss flash crash\" -> ainvest, Lawfare \"Selling Spirals\", MDPI taxonomy of AI-driven flash crashes, AIID incident 28 (2010 flash crash); none matches a quantitative firm losing over $8M in 340 ms; the result page noted neither figure appears.",
        "Outcome: no confirmed source names this incident."]),
    "INC-04310": dict(key="INC-042", effort=[
        "Row cites uber.com/blog/engineering/ (blog section index; fetch returns HTTP 406 for our UA).",
        "Candidate https://www.uber.com/blog/michelangelo-machine-learning-platform/ also returns HTTP 406 via common.py (2026-10-15), so no Uber page can be fetched and none can be confirmed to name an audit of 30+ feature stores; no URL may be written without a fetch.",
        "Discovery query (Brave): \"Uber Michelangelo audit 30 feature stores data lineage fragmentation\" - rate-limited (HTTP 429), no result obtained.",
        "Outcome: no confirmed source names this incident."]),
    "INC-03570": dict(key="INC-045", effort=[
        "Row cites arxiv.org/abs/2408.00000: HTTP 404 (no such paper; placeholder-pattern id).",
        "Discovery queries (arXiv API): all:\"denial-of-wallet\" AND all:LLM -> only 2026 papers (2609.28585, 2608.25276), which post-date this 2024 incident; all:\"long-context\" AND all:\"resource exhaustion\" AND all:LLM AND all:prompts -> 0 results.",
        "Outcome: no confirmed source names a 200K-token Claude context-flooding attack with 10-50x cost. The nonexistent arXiv reference is left in place (D130: do not replace with guesses); the unverified status flags it.",]),
    "INC-03444": dict(key="INC-046", effort=[
        "Row cites arxiv.org/abs/2407.00000: HTTP 404 (no such paper; placeholder-pattern id).",
        "Discovery query (arXiv API): all:adversarial AND all:RAG AND all:embedding AND all:ada-002 -> 0 results. Nearest real work, Zhong et al. \"Poisoning Retrieval Corpora by Injecting Adversarial Passages\" (arXiv 2310.19156, fetched), attacks dense retrievers with perturbed passages but does not test OpenAI text-embedding-ada-002 or Cohere embed-v3 as the row states, so substituting it would describe a different incident.",
        "Outcome: no confirmed source names this incident. The nonexistent arXiv reference is left in place; the unverified status flags it."]),
    "INC-03491": dict(key="INC-063", effort=[
        "Row cites arxiv.org/abs/2311.16090 = \"Self-correcting LLM-controlled Diffusion Models\" (R2 title-no-overlap; wrong paper).",
        "Discovery queries (arXiv API): all:\"safety checker\" AND all:\"text-to-image\" AND all:bypass -> adversarial/jailbreak papers on text-to-image safeguards (e.g. MMA-Diffusion 2311.17516, 2404.02928) none of which concern CSAM-classifier evasion; all:CSAM AND all:classifier AND all:adversarial -> 0 results.",
        "Outcome: no confirmed source names adversarial evasion of CSAM-detection classifiers via negative prompts and LoRA models."]),
    "INC-04067": dict(key="INC-065", effort=[
        "Row cites arxiv.org/abs/2403.06634 = \"Stealing Part of a Production Language Model\" (a model-extraction paper). That paper is the genuine reference of the row's merged source ARXIV-2403.06634, not of the invented \"GPT-4 system prompt extraction toolkit\" (Base64/ROT13/role-play) narrative of INC-065, so the row is an over-merge in addition to an unsupported description.",
        "Discovery query (Brave): \"system prompt extraction attacks GPT-4 arxiv prompt leakage multi-turn Base64\" -> Zhang & Ippolito 2307.06865 \"Effective Prompt Extraction from Language Models\" (fetched: no GPT-4, no toolkit) and Agarwal et al. 2404.16251 (fetched: no GPT-4); neither describes a published toolkit.",
        "Outcome: no confirmed source names the described toolkit. References left unchanged (the arXiv paper remains the reference of source ARXIV-2403.06634). Over-merge reported for WS4-T19."]),
}

# --- DEFERRED: mechanism gap (STOP-and-report per the task brief) ----------------------------------
# curation_overrides supports `references`, but only as a WHOLE-LIST replacement, which every build
# re-applies over whatever the feeds produced. For rows whose references are continuously merged from
# CVE/GHSA feeds that freezes the list (INC-01015 would carry 442 hard-coded references, INC-01291 177) and
# silently masks every later upstream reference addition. A remove-by-URL override would be a new
# mechanism, which this task may not invent. The five rows stay byte-identical.
_DEFERRED_IDS = ("INC-01589", "INC-02471", "INC-02871", "INC-01291", "INC-01015")
DEFERRED = {rid: FIXED.pop(rid) for rid in _DEFERRED_IDS}
DEFERRED_REASON = ("flagged reference is incidental to a feed-merged (CVE/GHSA) row; removing it with the existing mechanism would "
                   "freeze the entire reference list (whole-list replacement) and mask later upstream additions; a remove-by-URL "
                   "override is a new mechanism and was not invented. Row left unchanged.")

# --- DEFERRED: ruling (c) demotion collides with a validate.py invariant ---------------------------
# INC-04207 carries a landmark-only label (discovery_method, curation entry INC-030). tier=landmark is
# derived from quality_tier=curated (_derive_tier), so demoting the row to auto removes the landmark tier
# and scripts/validate.py check 6 ("evidence-gated labels only on the landmark tier") then fails the
# build. The override mechanism can set a field but not delete one, and discovery_method has no null
# value. Neither dropping the label nor skipping the demotion is this task's call; the row is unchanged.
DEFERRED_LABEL = {"INC-04207": FIXED.pop("INC-04207")}
DEFERRED_LABEL_REASON = ("ruling D130(c) demotion to auto removes tier=landmark; the row's landmark-only discovery_method label "
                         "(curation entry INC-030) then fails validate.py check 6, and the override mechanism cannot delete the label. "
                         "Row left unchanged; the planned change (remove the arXiv 2402.06627 reference, correct the model list from the "
                         "Microsoft post) is recorded in the spec for when the conflict is ruled on.")
