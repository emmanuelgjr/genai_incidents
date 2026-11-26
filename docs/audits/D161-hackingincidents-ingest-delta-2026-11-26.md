# D161: hackingincidents.ai ingest, field-level delta (facts + link, D160)

**Date:** 2026-11-26 · **Author:** WS4 pipeline-engineer · **Base:** `main` 9019539d · **Branch:** `d161-hackingincidents-ingest` · **Status:** DATED RECORD, **do-not-regenerate** (supersede with a dated update; do not rewrite). Working agreement 2: every delta below is enumerated; anything not listed is a defect.

## 1. Verdict (first)

The ingest adds **187 new rows** (1.18% of the 15,845-row base) and attaches **110 ledger incidents as references to 80 existing rows**. Those 80 rows change in exactly three fields (`references`, `updated`, `last_seen`); the other 15,765 base rows are byte-identical (per-entity compare, section 4). No row is removed, no ID is reused or re-pointed, `id_deprecations.json` is untouched, there are 0 corpus flips and 0 severity/date/title/attack_vector changes on existing rows. Scale is inside the 1.9% expectation: all 298 ledger rows are accounted for (187 new + 110 attached + 1 collapsed in-ledger twin = 298).

Two things the reviewer should weigh, both stated plainly: (a) **event-level recall of the dedupe is not 100%**: a seeded sample of 30 of the then-remaining new rows contained 2 existing-row duplicates that neither URL nor AIID join found; both are now in the reviewed list, but a residual rate of the same order (roughly 5 to 10% of the new rows, unmeasured) is likely, see section 5.4; (b) **the pinned snapshot is stripped of the ledger's quote and summary text (D162)**, see section 9.

## 2. Entry count and ID set

| | before (base 9019539d) | after | delta |
|---|---|---|---|
| rows in `data/incidents.json` | 15,845 | 16,032 | +187 |
| `incident_count` (stats.json) | 15,804 | 15,991 | +187 |
| new INC IDs | | INC-17395 to INC-17581 (187, contiguous, appended after the previous maximum INC-17394) | |
| removed IDs | | 0 | |
| `data/id_deprecations.json` | 1,084 records | unchanged (git diff empty) | 0 |
| `retracted_count` / `unverified_count` / `disputed_count` | 29 / 12 / 22 | 29 / 12 / 22 | 0 |

IDs are append-only: the new IDs are the next 187 integers after INC-17394; no existing ID moved.

## 3. Stats and derived surfaces

`data/stats.json` changes, complete: `generated` 2026-11-25 -> 2026-11-26; `incident_count` 15804 -> 15991. `landmark_count` is unchanged (the new rows are `tier: feed`).

Derived by the normal build (`render_markdown.py`, `render_docs_stats.py`), nothing hand-edited: `INCIDENTS.md`; `data/incidents.min.json` and its mirrors `docs/data/incidents.min.json` and `src/genai_incidents/data/incidents.min.json`; year shards `docs/incidents/2021.md`, `2023.md`, `2024.md`, `2025.md`, `2026.md` (existing rows whose references grew, plus the new rows by year); `docs/charts/*.svg`; the `stats:incident_count` and `stats:generated` markers in `README.md`, `docs/DATASHEET.md`, `docs/index.html` (`generated` 2026-11-25 -> 2026-11-26 is the build date, not a data change). `scripts/check_stats_drift.py`: clean.

## 4. Existing rows that changed (80), field by field

Per-entity comparison of the two `data/incidents.json` files (every key of every row at both sides): the changed-field sets are `['last_seen', 'references', 'updated']` on 80 rows. The other 15,765 rows compare equal on every field.

**Intended and justified.** `references`: the ledger's own page `https://hackingincidents.ai/incident/<slug>/` plus any ledger source URL not already on the row are appended (the existing references keep their order and are an exact prefix of the new list on every row; checked per row). `updated` and `last_seen` are set to the build date by `_apply_history`, because `references` is a content field (the same mechanism that bumps them on any refresh); no other field is a content change. Severity, date, title, description, attack_vector, corpus, tier, quality_tier, taxonomy fields, tags, source_ids: no change on any of the rows.

References added in total: 212 across 80 rows. Note on two rows (INC-03212, INC-03248): they carry a whole-list `references` curation override (D130-3a); the attachment is applied AFTER curation overrides so it is not silently overwritten (section 8).

| row | refs before -> after | `updated` / `last_seen` before -> after | ledger incidents attached | URLs added |
|---|---|---|---|---|
| INC-00196 | 8 -> 10 | 2026-07-31 -> 2026-11-26 / 2026-07-31 -> 2026-11-26 | grok-bankrbot-morse-code-transfer-2026 | hackingincidents.ai/incident/grok-bankrbot-morse-code-transfer-2026/; dexerto.com/entertainment/x-user-tricks-grok-into-sending-them-200000- |
| INC-00260 | 6 -> 7 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | promptmink-claude-malicious-dependency-2026 | hackingincidents.ai/incident/promptmink-claude-malicious-dependency-20 |
| INC-00265 | 7 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | fortigate-600-devices-ai-augmented-2026 | hackingincidents.ai/incident/fortigate-600-devices-ai-augmented-2026/; aws.amazon.com/blogs/security/ai-augmented-threat-actor-accesses-forti; securityweek.com/hundreds-of-fortigate-firewalls-hacked-in-ai-powered- |
| INC-00266 | 5 -> 7 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | eviltokens-ai-augmented-phaas-bec-2026 | hackingincidents.ai/incident/eviltokens-ai-augmented-phaas-bec-2026/; sekoia.com/blog/eviltokens-an-ai-augmented-phishing-as-a-service-for-a |
| INC-00505 | 5 -> 7 | 2026-07-31 -> 2026-11-26 / 2026-07-31 -> 2026-11-26 | slopoly-hive0163-ransomware | hackingincidents.ai/incident/slopoly-hive0163-ransomware/; ibm.com/think/x-force/slopoly-start-ai-enhanced-ransomware-attacks |
| INC-00520 | 7 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | voidlink-ai-built-linux-malware-framework | hackingincidents.ai/incident/voidlink-ai-built-linux-malware-framework; theregister.com/security/2026/01/20/an-ai-wrote-voidlink-the-cloud-tar; bleepingcomputer.com/news/security/voidlink-cloud-malware-shows-clear- |
| INC-00527 | 7 -> 9 | 2026-07-31 -> 2026-11-26 / 2026-07-31 -> 2026-11-26 | deepload-ai-assisted-evasion-2026 | hackingincidents.ai/incident/deepload-ai-assisted-evasion-2026/; reliaquest.com/blog/threat-spotlight-deepload-malware-pairs-clickfix-d |
| INC-00587 | 7 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | promptspy-android-gemini-agent | hackingincidents.ai/incident/promptspy-android-gemini-agent/; cloud.google.com/blog/topics/threat-intelligence/ai-vulnerability-expl; welivesecurity.com/en/eset-research/promptspy-ushers-in-era-android-th |
| INC-00698 | 5 -> 8 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | bluenoroff-deepfake-zoom-crypto-2025 | hackingincidents.ai/incident/bluenoroff-deepfake-zoom-crypto-2025/; bleepingcomputer.com/news/security/north-korean-hackers-deepfake-execs; huntress.com/blog/inside-bluenoroff-web3-intrusion-analysis |
| INC-01157 | 1 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | hackerbot-claw-github-actions-2026 | hackingincidents.ai/incident/hackerbot-claw-github-actions-2026/; stepsecurity.io/blog/hackerbot-claw-github-actions-exploitation; pillar.security/blog/hackerbot-claw-adversarial-agent-targets-top-gith |
| INC-01365 | 9 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | clawhavoc-malicious-openclaw-skills-2026 | hackingincidents.ai/incident/clawhavoc-malicious-openclaw-skills-2026/ |
| INC-01541 | 7 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | konni-ai-built-powershell-backdoor-2026 | hackingincidents.ai/incident/konni-ai-built-powershell-backdoor-2026/; bleepingcomputer.com/news/security/konni-hackers-target-blockchain-eng; research.checkpoint.com/2026/konni-targets-developers-with-ai-malware/ |
| INC-01697 | 9 -> 10 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | deepfake-applicant-tokyo-it-executive-2026 | hackingincidents.ai/incident/deepfake-applicant-tokyo-it-executive-202 |
| INC-01775 | 7 -> 9 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | singapore-pm-wong-deepfake-zoom-2026 | hackingincidents.ai/incident/singapore-pm-wong-deepfake-zoom-2026/; police.gov.sg/media-hub/news/2026/05/20260516_footage_from_zoom_video_ |
| INC-02219 | 3 -> 6 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | funksec-ai-assisted-ransomware | hackingincidents.ai/incident/funksec-ai-assisted-ransomware/; research.checkpoint.com/2025/funksec-alleged-top-ransomware-group-powe; securityweek.com/emerging-funksec-ransomware-developed-using-ai/ |
| INC-02280 | 3 -> 4 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | aixbt-agent-fraudulent-prompts-2025 | hackingincidents.ai/incident/aixbt-agent-fraudulent-prompts-2025/ |
| INC-02300 | 7 -> 8 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | amazon-q-vscode-wiper-prompt | hackingincidents.ai/incident/amazon-q-vscode-wiper-prompt/ |
| INC-02320 | 1 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | iot-camera-credential-scraping-2025, novice-malware-builder-2025, recruitment-fraud-language-sanitization-2025 | hackingincidents.ai/incident/iot-camera-credential-scraping-2025/; hackingincidents.ai/incident/novice-malware-builder-2025/; hackingincidents.ai/incident/recruitment-fraud-language-sanitization-2 |
| INC-02426 | 4 -> 7 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | gtg-1002-claude-code-espionage-2025 | hackingincidents.ai/incident/gtg-1002-claude-code-espionage-2025/; theregister.com/2025/11/13/chinese_spies_claude_attacks/; cert.europa.eu/blog/threat-landscape-report-2025 |
| INC-02461 | 2 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | crowdstrike-famous-chollima-deepfake-2025 | hackingincidents.ai/incident/crowdstrike-famous-chollima-deepfake-2025; fortune.com/2025/08/04/north-korean-it-worker-infiltrations-exploded/ |
| INC-02637 | 2 -> 14 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | quietvault-ai-credential-stealer-2025, temp-zagros-gemini-malware-2025, unc1069-masan-gemini-crypto-2025, unc4899-pukchong-gemini-2025, apt42-gemini-data-processing-agent-2025, china-nexus-ctf-pretext-gemini-2025, apt41-gemini-osstun-c2-2025, apt28-promptsteal-lamehug-2025, promptflux-gemini-malware-2025 | hackingincidents.ai/incident/quietvault-ai-credential-stealer-2025/; hackingincidents.ai/incident/temp-zagros-gemini-malware-2025/; aithreat.io/cases/gtig-muddywater-gemini-opsec/; hackingincidents.ai/incident/unc1069-masan-gemini-crypto-2025/; hackingincidents.ai/incident/unc4899-pukchong-gemini-2025/; hackingincidents.ai/incident/apt42-gemini-data-processing-agent-2025/; hackingincidents.ai/incident/china-nexus-ctf-pretext-gemini-2025/; hackingincidents.ai/incident/apt41-gemini-osstun-c2-2025/; hackingincidents.ai/incident/apt28-promptsteal-lamehug-2025/; thehackernews.com/2025/07/cert-ua-discovers-lamehug-malware.html; picussecurity.com/resource/blog/lamehug-the-first-publicly-documented-; hackingincidents.ai/incident/promptflux-gemini-malware-2025/ |
| INC-02680 | 1 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | apt42-gemini-phishing-2025, apt43-public-ai-tools-research-2025 | hackingincidents.ai/incident/apt42-gemini-phishing-2025/; hackingincidents.ai/incident/apt43-public-ai-tools-research-2025/ |
| INC-02696 | 3 -> 5 | 2026-10-13 -> 2026-11-26 / 2026-10-13 -> 2026-11-26 | hk-deepfake-dating-crypto-fraud-2025 | hackingincidents.ai/incident/hk-deepfake-dating-crypto-fraud-2025/; thestandard.com.hk/news/article/324116/Police-charge-nine-more-in-34m- |
| INC-02698 | 2 -> 3 | 2026-10-13 -> 2026-11-26 / 2026-10-13 -> 2026-11-26 | hk-ai-facial-composites-bank-checks-2025 | hackingincidents.ai/incident/hk-ai-facial-composites-bank-checks-2025/ |
| INC-02779 | 2 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | kaikatsu-frontier-teen-ai-program-breach-2025 | hackingincidents.ai/incident/kaikatsu-frontier-teen-ai-program-breach- |
| INC-02849 | 2 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | postmark-mcp-malicious-mcp-server-2025 | hackingincidents.ai/incident/postmark-mcp-malicious-mcp-server-2025/ |
| INC-02959 | 9 -> 14 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | kimsuky-chatgpt-fake-military-id | hackingincidents.ai/incident/kimsuky-chatgpt-fake-military-id/; genians.co.kr/en/blog/threat_intelligence/deepfake; therecord.media/north-korea-kimsuky-hackers-phishing-fake-military-ids; infosecurity-magazine.com/news/ai-military-ids-north-korea/; gendigital.com/blog/insights/reports/threat-report-q3-2025 |
| INC-02999 | 1 -> 5 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | cambodia-romance-baiting-chatgpt-2025, kimsuky-bluenoroff-chatgpt-rdp-tooling-2025 | hackingincidents.ai/incident/cambodia-romance-baiting-chatgpt-2025/; aithreat.io/cases/openai-cambodia-romance-baiting/; hackingincidents.ai/incident/kimsuky-bluenoroff-chatgpt-rdp-tooling-20; aithreat.io/cases/openai-kimsuky-bluenoroff-rdp/ |
| INC-03003 | 1 -> 14 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | openai-dprk-deceptive-employment-2025, scopecreep-chatgpt-go-malware-2025, vague-focus-chatgpt-social-engineering-2025, vixen-keyhole-panda-chatgpt-2025, wrong-number-task-scam-chatgpt-2025 | hackingincidents.ai/incident/openai-dprk-deceptive-employment-2025/; koreaherald.com/article/10426133; cdn.openai.com/threat-intelligence-reports/disrupting-malicious-uses-o; aithreat.io/cases/openai-dprk-employment-feb2025/; hackingincidents.ai/incident/scopecreep-chatgpt-go-malware-2025/; aiadoption.org/record/ai-powered-cyber-attacks/; aithreat.io/cases/openai-scopecreep-malware/; hackingincidents.ai/incident/vague-focus-chatgpt-social-engineering-20; aithreat.io/cases/openai-vague-focus/; hackingincidents.ai/incident/vixen-keyhole-panda-chatgpt-2025/; aithreat.io/cases/openai-vixen-keyhole-panda/; hackingincidents.ai/incident/wrong-number-task-scam-chatgpt-2025/; aithreat.io/cases/openai-wrong-number-task-scam/ |
| INC-03006 | 3 -> 10 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | openai-korean-operators-xenorat-2025, openai-russian-malware-tooling-2025, openai-unk-droppitch-2025 | hackingincidents.ai/incident/openai-korean-operators-xenorat-2025/; cdn.openai.com/threat-intelligence-reports/7d662b68-952f-4dfd-a2f2-fe5; hackingincidents.ai/incident/openai-russian-malware-tooling-2025/; hackingincidents.ai/incident/openai-unk-droppitch-2025/; volexity.com/blog/2025/10/08/apt-meets-gpt-targeted-operations-with-un; truesec.com/hub/blog/chinese-cyber-espionage-group-leverage-chatgpt; picussecurity.com/resource/blog/revisiting-voldemort-healthkick-and-go |
| INC-03024 | 4 -> 5 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | youtube-ceo-deepfake-creator-phishing-2025 | hackingincidents.ai/incident/youtube-ceo-deepfake-creator-phishing-202 |
| INC-03043 | 3 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | thai-pm-ai-voice-asean-leader-2025 | hackingincidents.ai/incident/thai-pm-ai-voice-asean-leader-2025/ |
| INC-03114 | 2 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | mimecast-centrelink-ai-phishing-2025 | hackingincidents.ai/incident/mimecast-centrelink-ai-phishing-2025/ |
| INC-03122 | 2 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | dnb-cfo-ceo-deepfake-teams-2025 | hackingincidents.ai/incident/dnb-cfo-ceo-deepfake-teams-2025/ |
| INC-03157 | 2 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | deepfake-zoom-crypto-analyst-takeover-2025 | hackingincidents.ai/incident/deepfake-zoom-crypto-analyst-takeover-202 |
| INC-03212 | 1 -> 3 | 2026-11-11 -> 2026-11-26 / 2026-11-11 -> 2026-11-26 | shai-hulud-npm-worm-llm-script | hackingincidents.ai/incident/shai-hulud-npm-worm-llm-script/; paloaltonetworks.com/resources/research/unit-42-incident-response-repo |
| INC-03248 | 1 -> 2 | 2026-11-11 -> 2026-11-26 / 2026-11-11 -> 2026-11-26 | sysdig-ai-assisted-aws-admin-8-minutes | hackingincidents.ai/incident/sysdig-ai-assisted-aws-admin-8-minutes/ |
| INC-03373 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | wiles-impersonation-ai-voice-2025 | hackingincidents.ai/incident/wiles-impersonation-ai-voice-2025/; yahoo.com/news/us-looking-attempt-impersonate-trump-023644868.html |
| INC-03452 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | brad-pitt-ai-images-romance-scam-2025 | hackingincidents.ai/incident/brad-pitt-ai-images-romance-scam-2025/; theguardian.com/world/2025/jan/14/french-tv-show-pulled-ridicule-woman |
| INC-03588 | 1 -> 5 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | arup-hong-kong-deepfake-video-call-2024 | hackingincidents.ai/incident/arup-hong-kong-deepfake-video-call-2024/; edition.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl; edition.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl; csa.gov.sg/alerts-and-advisories/advisories/ad-2024-006/ |
| INC-03783 | 2 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | ferrari-ceo-voice-clone-attempt-2024 | hackingincidents.ai/incident/ferrari-ceo-voice-clone-attempt-2024/; jalopnik.com/ferrari-exec-nearly-duped-by-deepfake-voice-of-ceo-bene-1 |
| INC-03812 | 10 -> 12 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | storm-2139-azure-openai-llmjacking-2025 | hackingincidents.ai/incident/storm-2139-azure-openai-llmjacking-2025/; blogs.microsoft.com/on-the-issues/2025/02/27/disrupting-cybercrime-abu |
| INC-03874 | 2 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | nomani-deepfake-investment-scam-2024 | hackingincidents.ai/incident/nomani-deepfake-investment-scam-2024/; web-assets.esetstatic.com/wls/en/papers/threat-reports/eset-threat-rep |
| INC-03975 | 2 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | meeten-ai-generated-brand-realst-2024 | hackingincidents.ai/incident/meeten-ai-generated-brand-realst-2024/ |
| INC-04066 | 2 -> 7 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | charcoal-typhoon-chatgpt-2024, crimson-sandstorm-chatgpt-2024, emerald-sleet-chatgpt-2024, forest-blizzard-chatgpt-2024, salmon-typhoon-chatgpt-2024 | hackingincidents.ai/incident/charcoal-typhoon-chatgpt-2024/; hackingincidents.ai/incident/crimson-sandstorm-chatgpt-2024/; hackingincidents.ai/incident/emerald-sleet-chatgpt-2024/; hackingincidents.ai/incident/forest-blizzard-chatgpt-2024/; hackingincidents.ai/incident/salmon-typhoon-chatgpt-2024/ |
| INC-04068 | 1 -> 4 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | cyberav3ngers-chatgpt-plc-research-2024, storm-0817-chatgpt-android-malware-2024, sweetspecter-chatgpt-2024 | hackingincidents.ai/incident/cyberav3ngers-chatgpt-plc-research-2024/; hackingincidents.ai/incident/storm-0817-chatgpt-android-malware-2024/; hackingincidents.ai/incident/sweetspecter-chatgpt-2024/ |
| INC-04154 | 2 -> 5 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | lastpass-deepfake-ceo-voice-attempt-2024 | hackingincidents.ai/incident/lastpass-deepfake-ceo-voice-attempt-2024/; blog.lastpass.com/posts/2024/04/attempted-audio-deepfake-call-targets-; hackread.com/lastpass-deepfake-scam-ceo-impersonation-thwarted/ |
| INC-04196 | 9 -> 11 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | cardin-kuleba-deepfake-zoom-2024 | hackingincidents.ai/incident/cardin-kuleba-deepfake-zoom-2024/; nbcnews.com/politics/congress/ben-cardin-targeted-apparent-deep-fake-c |
| INC-04356 | 2 -> 3 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | wisetech-ceo-deepfake-whatsapp-2024 | hackingincidents.ai/incident/wisetech-ceo-deepfake-whatsapp-2024/ |
| INC-04359 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | wpp-ceo-deepfake-meeting-attempt-2024 | hackingincidents.ai/incident/wpp-ceo-deepfake-meeting-attempt-2024/; theguardian.com/technology/article/2024/may/10/ceo-wpp-deepfake-scam |
| INC-04615 | 3 -> 5 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | retool-deepfake-voice-vishing-2023 | hackingincidents.ai/incident/retool-deepfake-voice-vishing-2023/; retool.com/blog/mfa-isnt-mfa |
| INC-04711 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | kerala-deepfake-whatsapp-video-call-2023 | hackingincidents.ai/incident/kerala-deepfake-whatsapp-video-call-2023/; hindustantimes.com/india-news/deepfake-scammers-trick-indian-man-into- |
| INC-07898 | 7 -> 9 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | kali365-phaas-ai-lures-2026 | hackingincidents.ai/incident/kali365-phaas-ai-lures-2026/; ic3.gov/PSA/2026/PSA260521 |
| INC-07905 | 7 -> 11 | 2026-07-31 -> 2026-11-26 / 2026-07-31 -> 2026-11-26 | mexico-government-claude-code-breach | hackingincidents.ai/incident/mexico-government-claude-code-breach/; gambit.security/ai-assisted-breach-of-mexicos-government-infrastructur; engadget.com/ai/hacker-used-anthropics-claude-chatbot-to-attack-multip; trendmicro.com/en/research/26/e/vibe-hacking-two-ai-augmented-campaign |
| INC-08177 | 12 -> 23 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | carding-store-claude-code-2025, chinese-actor-claude-vietnam-critical-infrastructure-2025, dprk-it-workers-claude-2025, stealer-log-mcp-victim-profiling-2025, claude-code-data-extortion-2025, jasper-sleet-faceswap-voice-changing-2025, no-code-ransomware-as-a-service-2025 | hackingincidents.ai/incident/carding-store-claude-code-2025/; hackingincidents.ai/incident/chinese-actor-claude-vietnam-critical-inf; hackingincidents.ai/incident/dprk-it-workers-claude-2025/; hackingincidents.ai/incident/stealer-log-mcp-victim-profiling-2025/; hackingincidents.ai/incident/claude-code-data-extortion-2025/; thehackernews.com/2025/08/anthropic-disrupts-ai-powered.html; hiddenlayer.com/research/the-first-ai-powered-cyber-attack; hackingincidents.ai/incident/jasper-sleet-faceswap-voice-changing-2025; microsoft.com/en-us/security/blog/2026/03/06/ai-as-tradecraft-how-thre; hackingincidents.ai/incident/no-code-ransomware-as-a-service-2025/; aiadoption.org/record/ai-powered-cyber-attacks/ |
| INC-08183 | 12 -> 13 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | llmjacking-sysdig-bedrock-2024 | hackingincidents.ai/incident/llmjacking-sysdig-bedrock-2024/ |
| INC-13073 | 8 -> 9 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | outsider-enterprise-gemini-smishing-sites-2026 | hackingincidents.ai/incident/outsider-enterprise-gemini-smishing-sites |
| INC-14302 | 8 -> 12 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | jadepuffer-agentic-ransomware-langflow | hackingincidents.ai/incident/jadepuffer-agentic-ransomware-langflow/; infosecurity-magazine.com/news/researchers-first-agentic/; trendmicro.com/en_us/research/26/g/autonomous-ransomware.html; sysdig.com/blog/jadepuffer-agentic-ransomware-for-automated-database-e |
| INC-14465 | 1 -> 2 | 2026-10-06 -> 2026-11-26 / 2026-10-06 -> 2026-11-26 | veriff-ceo-realtime-deepfake-whatsapp-2025 | hackingincidents.ai/incident/veriff-ceo-realtime-deepfake-whatsapp-202 |
| INC-14583 | 6 -> 7 | 2026-07-31 -> 2026-11-26 / 2026-07-31 -> 2026-11-26 | tuxbot-v3-llm-built-botnet-2026 | hackingincidents.ai/incident/tuxbot-v3-llm-built-botnet-2026/ |
| INC-14602 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | meta-ai-support-bot-instagram-takeovers-2026 | hackingincidents.ai/incident/meta-ai-support-bot-instagram-takeovers-2; krebsonsecurity.com/2026/06/hackers-used-metas-ai-support-bot-to-seize |
| INC-14897 | 7 -> 9 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | bandai-channel-teen-chatgpt-program-2025 | hackingincidents.ai/incident/bandai-channel-teen-chatgpt-program-2025/; therecord.media/japanese-teen-arrested-over-attack-disrupted-streaming |
| INC-17227 | 1 -> 2 | 2026-10-13 -> 2026-11-26 / 2026-10-13 -> 2026-11-26 | starmangalsutra-deepfake-director-transfers-2026 | hackingincidents.ai/incident/starmangalsutra-deepfake-director-transfe |
| INC-17261 | 1 -> 5 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | taiwan-government-hermes-openclaw-2026 | hackingincidents.ai/incident/taiwan-government-hermes-openclaw-2026/; cyberscoop.com/near-autonomous-ai-attack-government-target-taiwan/; csis.org/programs/strategic-technologies-program/significant-cyber-inc; dreamgroup.com/blog/inside-a-multi-agent-ai-framework-used-to-compromi |
| INC-17270 | 1 -> 3 | 2026-10-13 -> 2026-11-26 / 2026-10-13 -> 2026-11-26 | aurora-ransomware-cursor-claude-2026 | hackingincidents.ai/incident/aurora-ransomware-cursor-claude-2026/; gambit.security/blog-posts/aurora-ransomware-targets-esxi-abuses-curso |
| INC-17275 | 1 -> 4 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | thailand-finance-ministry-hermes-agent-2026 | hackingincidents.ai/incident/thailand-finance-ministry-hermes-agent-20; bleepingcomputer.com/news/security/hermes-ai-agent-used-to-automate-at; hunt.io/blog/thailand-ministry-finance-targeted-with-hermes-ai-agent |
| INC-17276 | 1 -> 3 | 2026-10-29 -> 2026-11-26 / 2026-10-29 -> 2026-11-26 | marimo-exploit-llm-agent-database-exfil-2026 | hackingincidents.ai/incident/marimo-exploit-llm-agent-database-exfil-2; sysdig.com/blog/ai-agent-at-the-wheel-how-an-attacker-used-llms-to-mov |
| INC-17294 | 1 -> 3 | 2026-10-13 -> 2026-11-26 / 2026-10-13 -> 2026-11-26 | aepd-first-agentic-ai-breach-spain-2026 | hackingincidents.ai/incident/aepd-first-agentic-ai-breach-spain-2026/; securityweek.com/first-agentic-ai-data-breach-reported-to-spanish-regu |
| INC-17334 | 1 -> 2 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | greek-ai-cloned-relatives-voice-fraud-2026 | hackingincidents.ai/incident/greek-ai-cloned-relatives-voice-fraud-202 |
| INC-17335 | 1 -> 4 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | fideuram-intesa-voice-clone-95m-2026 | hackingincidents.ai/incident/fideuram-intesa-voice-clone-95m-2026/; gulfnews.com/world/europe/ai-voice-cloning-scam-hits-italian-bank-fake; ansa.it/sito/notizie/cronaca/2026/09/25/truffa-da-395-milioni-allex-ca |
| INC-17344 | 1 -> 4 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | cairn-ecommerce-intrusion-campaign | hackingincidents.ai/incident/cairn-ecommerce-intrusion-campaign/; techwireasia.com/2026/10/ai-agents-cyberattacks-company-websites/; norforge.com/blog/inside_cairn |
| INC-17356 | 1 -> 3 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | storm-0940-artex-connectwise-2026 | hackingincidents.ai/incident/storm-0940-artex-connectwise-2026/; microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-age |
| INC-17357 | 1 -> 8 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | artex-south-korean-bank-intrusions | hackingincidents.ai/incident/artex-south-korean-bank-intrusions/; flare.io/learn/resources/blog/ai-models-cybercrime-quantitative-analys; securityweek.com/china-apt-uses-ai-pentest-tool-artex-in-connectwise-a; csis.org/programs/strategic-technologies-program/significant-cyber-inc; censys.com/blog/artex-agentic-asbestos/; recordedfuture.com/blog/tag-217-artex-south-korean-banks; crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-s |
| INC-17361 | 1 -> 3 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | dutch-ai-bank-warning-recordings-fraud-2026 | hackingincidents.ai/incident/dutch-ai-bank-warning-recordings-fraud-20; nltimes.nl/2026/10/21/police-arrest-two-suspects-ai-powered-bank-fraud |
| INC-17367 | 1 -> 5 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | vapor-panda-artex-global-espionage | hackingincidents.ai/incident/vapor-panda-artex-global-espionage/; nbcnews.com/tech/security/china-linked-hackers-used-ai-target-200-orga; cyberscoop.com/china-vapor-panda-agentic-ai-artex-campaign-crowdstrike; crowdstrike.com/en-us/blog/vapor-panda-uses-artex-to-scale-global-camp |
| INC-17368 | 1 -> 3 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | chainalysis-offensive-agentic-breach-2026 | hackingincidents.ai/incident/chainalysis-offensive-agentic-breach-2026; bleepingcomputer.com/news/security/chainalysis-discloses-data-breach-f |
| INC-17369 | 1 -> 4 | 2026-11-08 -> 2026-11-26 / 2026-11-08 -> 2026-11-26 | claude-pentestgpt-argentine-healthcare | hackingincidents.ai/incident/claude-pentestgpt-argentine-healthcare/; crowdstrike.com/en-us/blog/crowdstrike-uncovers-new-agentic-ai-campaig; wired.com/story/ai-guardrails-arent-stopping-criminal-hackers/ |
| INC-17384 | 1 -> 5 | 2026-11-22 -> 2026-11-26 / 2026-11-22 -> 2026-11-26 | bossai-ai-agent-campaign | hackingincidents.ai/incident/bossai-ai-agent-campaign/; acronis.com/en/blog/posts/acronis-researchers-uncover-ai-attack-mesh-t; machine.net/news/acronis-bossai-ai-agent-mesh-abliterated-models-gitbo; acronis.com/en/tru/posts/bossai-inside-the-ai-attack-mesh-that-targete |
| INC-17386 | 1 -> 2 | 2026-11-22 -> 2026-11-26 / 2026-11-22 -> 2026-11-26 | binance-hot-wallet-compromised-ai-tool-2026 | hackingincidents.ai/incident/binance-hot-wallet-compromised-ai-tool-20 |
| INC-17391 | 1 -> 3 | 2026-11-22 -> 2026-11-26 / 2026-11-22 -> 2026-11-26 | taiwan-romance-scam-ai-voice-changer-2026 | hackingincidents.ai/incident/taiwan-romance-scam-ai-voice-changer-2026; focustaiwan.tw/society/202609020019 |

## 5. How a ledger row was matched, and what each outcome was

### 5.1 Rules (in order; first hit wins; code: `scripts/ingest_hackingincidents.py`)

1. **AIID join:** a ledger source `incidentdatabase.ai/cite/N` against the corpus `aiid_id` / `AIID-N` source id.
2. **Source URL:** a ledger source URL equal, after the merger's own `normalize_url`, to any corpus reference URL (aggregate pages never count).
3. **Title:** `title_key` equal within +-1 year (0 hits).
4. **Reviewed title matches** (`REVIEWED_MATCHES`): event twins that no key finds because the corpus row cites other articles (an OECD page, an AIAAIC row, another outlet). A candidate list (shared rare title tokens, idf-weighted similarity >= 0.30, year +-1) was generated and **every candidate was adjudicated by reading the ledger row and the corpus row**: 64 candidates in the first pass, 28 accepted and 36 rejected as same-theme-different-event; 12 further matches (4 events and the 3 report-level OpenAI rows from a looser pass over the same rows, 5 events from the seeded sample and scan of section 5.4). The candidates still unmatched after all of that (40) are kept in the provenance file under `title_candidates_not_matched`.

Several candidates: AIID join beats URL, then higher title similarity, then more shared URLs, then lowest INC id; alternates recorded (2 rows: `openai-dprk-deceptive-employment-2025` -> INC-03003 over INC-02999, `storm-2139-azure-openai-llmjacking-2025` -> INC-03812 (AIID join) over INC-02902).

### 5.2 Event-level versus REPORT-LEVEL (written down, as asked)

A match is **EVENT** when it came from an AIID join, a title match, a reviewed event match, or a URL match whose idf-weighted title similarity (ledger title + actor + targets + models against the corpus title) is >= 0.25. It is **REPORT** when the match is URL-only (or reviewed as such) and the similarity is below 0.25, which in practice means the corpus row IS the parent vendor report (`OpenAI June 2025 Disrupting Malicious Uses Report`, `Google GTIG November 2025 AI Threat Tracker`, the Anthropic and OpenAI report rows) and the ledger has split it per actor. **Both attach as a reference to the parent; the level is recorded, not acted on** (D159 U7: default attach, split only under a deliberate granularity decision). Limits: the 0.25 cut is a heuristic and a umbrella row such as INC-08177 can land on either side; it was checked against the gate's named examples (INC-03003 scopecreep, INC-02637 promptflux, INC-03006 xenorat: all REPORT; INC-17386 binance, INC-03122, INC-08175, INC-02680, INC-03248: EVENT).

### 5.3 Outcome of the 298 ledger rows

| outcome | rows |
|---|---|
| new row | 187 |
| attached, AIID join (+ URL) | 22 (all 22 AIID-citing ledger rows) |
| attached, URL only, EVENT | 13 |
| attached, URL only, REPORT | 35 |
| attached, reviewed title match, EVENT | 37 |
| attached, reviewed title match, REPORT | 3 |
| collapsed into the surviving twin (in-ledger near-duplicate) | 1 |
| **total** | **298** |

The D159 gate measured 70 of 298 sharing a URL (or AIID id) with the corpus; this reproduces 70 by keys 1 and 2 (22 AIID + 48 URL-only: 13 EVENT + 35 REPORT), an agreement reached by a different implementation than the gate's but the same normalisation, so it is not independent evidence (agreement 6b); the title stage and the sample in 5.4 are the independent part.

**In-ledger pair:** `cairn-monai-label-university-intrusion` (Cyware) and `...-intrusions` (SecurityWeek) collapse to the plural slug (the richer row: two AI roles, Amazon-attributed source, 48-hour campaign); the survivor keeps both ledger page links and both source URLs. The detector fires on any other slug pair differing by a trailing `s` and aborts the run for review (test `test_new_unreviewed_inledger_near_duplicate_aborts`).

### 5.4 Residual duplicates (recall)

A seeded random sample (`random.Random(161)`) of 30 of the 192 new rows left after the first stages was read against its two closest corpus rows by title similarity: **2 of 30 were existing-row duplicates** (`claude-pentestgpt-argentine-healthcare` = INC-17369, `hk-deepfake-dating-crypto-fraud-2025` = INC-02696); both were added to the reviewed list. A looser scan of the remaining 55 candidates then found 3 more (`wpp-ceo-deepfake-meeting-attempt-2024` = INC-04359, `wiles-impersonation-ai-voice-2025` = INC-03373, `dutch-ai-bank-warning-recordings-fraud-2026` = INC-17361). Reading that as a rate: roughly 2/30 in an unbiased sample, so on the order of 10 further duplicate events may sit among the 187 new rows; the interval on n=30 is wide. These would be two rows for one event, not a data loss; a red-reviewer seeded sample is the right independent check, and the reviewed list is the mechanism for any it finds.

### 5.5 The 110 attachments

| ledger slug | -> INC | level | basis | similarity |
|---|---|---|---|---|
| grok-bankrbot-morse-code-transfer-2026 | INC-00196 | event | reviewed-title | 0.654 |
| promptmink-claude-malicious-dependency-2026 | INC-00260 | report | url | 0.125 |
| fortigate-600-devices-ai-augmented-2026 | INC-00265 | event | reviewed-title | 0.314 |
| eviltokens-ai-augmented-phaas-bec-2026 | INC-00266 | event | reviewed-title | 0.501 |
| slopoly-hive0163-ransomware | INC-00505 | event | reviewed-title | 0.851 |
| voidlink-ai-built-linux-malware-framework | INC-00520 | event | url | 0.302 |
| deepload-ai-assisted-evasion-2026 | INC-00527 | event | reviewed-title | 0.496 |
| promptspy-android-gemini-agent | INC-00587 | event | reviewed-title | 0.505 |
| bluenoroff-deepfake-zoom-crypto-2025 | INC-00698 | event | url | 0.597 |
| hackerbot-claw-github-actions-2026 | INC-01157 | event | url | 0.675 |
| clawhavoc-malicious-openclaw-skills-2026 | INC-01365 | event | aiid+url | 0.642 |
| konni-ai-built-powershell-backdoor-2026 | INC-01541 | event | reviewed-title | 0.429 |
| deepfake-applicant-tokyo-it-executive-2026 | INC-01697 | event | aiid+url | 0.508 |
| singapore-pm-wong-deepfake-zoom-2026 | INC-01775 | event | reviewed-title | 0.49 |
| funksec-ai-assisted-ransomware | INC-02219 | event | reviewed-title | 0.54 |
| aixbt-agent-fraudulent-prompts-2025 | INC-02280 | event | aiid+url | 0.8 |
| amazon-q-vscode-wiper-prompt | INC-02300 | event | url | 0.605 |
| iot-camera-credential-scraping-2025 | INC-02320 | report | url | 0.0 |
| novice-malware-builder-2025 | INC-02320 | report | url | 0.0 |
| recruitment-fraud-language-sanitization-2025 | INC-02320 | report | url | 0.0 |
| gtg-1002-claude-code-espionage-2025 | INC-02426 | event | url | 0.682 |
| crowdstrike-famous-chollima-deepfake-2025 | INC-02461 | event | url | 0.721 |
| apt28-promptsteal-lamehug-2025 | INC-02637 | report | url | 0.0 |
| apt41-gemini-osstun-c2-2025 | INC-02637 | report | url | 0.0 |
| apt42-gemini-data-processing-agent-2025 | INC-02637 | report | url | 0.0 |
| china-nexus-ctf-pretext-gemini-2025 | INC-02637 | report | url | 0.0 |
| promptflux-gemini-malware-2025 | INC-02637 | report | url | 0.0 |
| quietvault-ai-credential-stealer-2025 | INC-02637 | report | url | 0.0 |
| temp-zagros-gemini-malware-2025 | INC-02637 | report | url | 0.0 |
| unc1069-masan-gemini-crypto-2025 | INC-02637 | report | url | 0.0 |
| unc4899-pukchong-gemini-2025 | INC-02637 | report | url | 0.0 |
| apt42-gemini-phishing-2025 | INC-02680 | event | url | 0.273 |
| apt43-public-ai-tools-research-2025 | INC-02680 | report | url | 0.0 |
| hk-deepfake-dating-crypto-fraud-2025 | INC-02696 | event | reviewed-title | 0.532 |
| hk-ai-facial-composites-bank-checks-2025 | INC-02698 | event | aiid+url | 0.761 |
| kaikatsu-frontier-teen-ai-program-breach-2025 | INC-02779 | event | aiid+url | 0.597 |
| postmark-mcp-malicious-mcp-server-2025 | INC-02849 | event | url | 0.643 |
| kimsuky-chatgpt-fake-military-id | INC-02959 | event | reviewed-title | 0.542 |
| cambodia-romance-baiting-chatgpt-2025 | INC-02999 | report | url | 0.156 |
| kimsuky-bluenoroff-chatgpt-rdp-tooling-2025 | INC-02999 | report | url | 0.071 |
| openai-dprk-deceptive-employment-2025 | INC-03003 | report | url | 0.112 |
| scopecreep-chatgpt-go-malware-2025 | INC-03003 | report | url | 0.0 |
| vague-focus-chatgpt-social-engineering-2025 | INC-03003 | report | url | 0.0 |
| vixen-keyhole-panda-chatgpt-2025 | INC-03003 | report | url | 0.0 |
| wrong-number-task-scam-chatgpt-2025 | INC-03003 | report | url | 0.118 |
| openai-korean-operators-xenorat-2025 | INC-03006 | report | reviewed-title | 0.0 |
| openai-russian-malware-tooling-2025 | INC-03006 | report | reviewed-title | 0.0 |
| openai-unk-droppitch-2025 | INC-03006 | report | reviewed-title | 0.0 |
| youtube-ceo-deepfake-creator-phishing-2025 | INC-03024 | event | aiid+url | 0.708 |
| thai-pm-ai-voice-asean-leader-2025 | INC-03043 | event | aiid+url | 0.51 |
| mimecast-centrelink-ai-phishing-2025 | INC-03114 | event | aiid+url | 0.271 |
| dnb-cfo-ceo-deepfake-teams-2025 | INC-03122 | event | aiid+url | 0.792 |
| deepfake-zoom-crypto-analyst-takeover-2025 | INC-03157 | event | aiid+url | 0.544 |
| shai-hulud-npm-worm-llm-script | INC-03212 | event | url | 0.769 |
| sysdig-ai-assisted-aws-admin-8-minutes | INC-03248 | event | url | 0.313 |
| wiles-impersonation-ai-voice-2025 | INC-03373 | event | reviewed-title | 0.296 |
| brad-pitt-ai-images-romance-scam-2025 | INC-03452 | event | reviewed-title | 0.497 |
| arup-hong-kong-deepfake-video-call-2024 | INC-03588 | event | reviewed-title | 0.629 |
| ferrari-ceo-voice-clone-attempt-2024 | INC-03783 | event | reviewed-title | 0.432 |
| storm-2139-azure-openai-llmjacking-2025 | INC-03812 | event | aiid+url | 0.442 |
| nomani-deepfake-investment-scam-2024 | INC-03874 | event | aiid+url | 0.623 |
| meeten-ai-generated-brand-realst-2024 | INC-03975 | event | aiid+url | 0.437 |
| charcoal-typhoon-chatgpt-2024 | INC-04066 | report | url | 0.114 |
| crimson-sandstorm-chatgpt-2024 | INC-04066 | report | url | 0.114 |
| emerald-sleet-chatgpt-2024 | INC-04066 | report | url | 0.114 |
| forest-blizzard-chatgpt-2024 | INC-04066 | report | url | 0.114 |
| salmon-typhoon-chatgpt-2024 | INC-04066 | report | url | 0.114 |
| cyberav3ngers-chatgpt-plc-research-2024 | INC-04068 | report | url | 0.0 |
| storm-0817-chatgpt-android-malware-2024 | INC-04068 | report | url | 0.0 |
| sweetspecter-chatgpt-2024 | INC-04068 | report | url | 0.129 |
| lastpass-deepfake-ceo-voice-attempt-2024 | INC-04154 | event | reviewed-title | 0.371 |
| cardin-kuleba-deepfake-zoom-2024 | INC-04196 | event | reviewed-title | 0.395 |
| wisetech-ceo-deepfake-whatsapp-2024 | INC-04356 | event | aiid+url | 0.634 |
| wpp-ceo-deepfake-meeting-attempt-2024 | INC-04359 | event | reviewed-title | 0.567 |
| retool-deepfake-voice-vishing-2023 | INC-04615 | event | reviewed-title | 0.402 |
| kerala-deepfake-whatsapp-video-call-2023 | INC-04711 | event | reviewed-title | 0.394 |
| kali365-phaas-ai-lures-2026 | INC-07898 | event | reviewed-title | 0.491 |
| mexico-government-claude-code-breach | INC-07905 | event | reviewed-title | 0.351 |
| carding-store-claude-code-2025 | INC-08177 | report | url | 0.0 |
| chinese-actor-claude-vietnam-critical-infrastructure-2025 | INC-08177 | report | url | 0.0 |
| claude-code-data-extortion-2025 | INC-08177 | report | url | 0.0 |
| dprk-it-workers-claude-2025 | INC-08177 | event | url | 0.43 |
| jasper-sleet-faceswap-voice-changing-2025 | INC-08177 | report | url | 0.177 |
| no-code-ransomware-as-a-service-2025 | INC-08177 | report | url | 0.0 |
| stealer-log-mcp-victim-profiling-2025 | INC-08177 | report | url | 0.0 |
| llmjacking-sysdig-bedrock-2024 | INC-08183 | event | aiid+url | 0.0 |
| outsider-enterprise-gemini-smishing-sites-2026 | INC-13073 | event | aiid+url | 0.756 |
| jadepuffer-agentic-ransomware-langflow | INC-14302 | event | url | 0.294 |
| veriff-ceo-realtime-deepfake-whatsapp-2025 | INC-14465 | event | aiid+url | 0.568 |
| tuxbot-v3-llm-built-botnet-2026 | INC-14583 | event | url | 0.523 |
| meta-ai-support-bot-instagram-takeovers-2026 | INC-14602 | event | reviewed-title | 0.729 |
| bandai-channel-teen-chatgpt-program-2025 | INC-14897 | event | reviewed-title | 0.301 |
| starmangalsutra-deepfake-director-transfers-2026 | INC-17227 | event | aiid+url | 0.508 |
| taiwan-government-hermes-openclaw-2026 | INC-17261 | event | reviewed-title | 0.74 |
| aurora-ransomware-cursor-claude-2026 | INC-17270 | event | aiid+url | 0.567 |
| thailand-finance-ministry-hermes-agent-2026 | INC-17275 | event | reviewed-title | 0.539 |
| marimo-exploit-llm-agent-database-exfil-2026 | INC-17276 | event | reviewed-title | 0.847 |
| aepd-first-agentic-ai-breach-spain-2026 | INC-17294 | event | reviewed-title | 0.559 |
| greek-ai-cloned-relatives-voice-fraud-2026 | INC-17334 | event | aiid+url | 0.736 |
| fideuram-intesa-voice-clone-95m-2026 | INC-17335 | event | reviewed-title | 0.425 |
| cairn-ecommerce-intrusion-campaign | INC-17344 | event | reviewed-title | 0.484 |
| storm-0940-artex-connectwise-2026 | INC-17356 | event | aiid+url | 0.506 |
| artex-south-korean-bank-intrusions | INC-17357 | event | reviewed-title | 0.531 |
| dutch-ai-bank-warning-recordings-fraud-2026 | INC-17361 | event | reviewed-title | 0.448 |
| vapor-panda-artex-global-espionage | INC-17367 | event | reviewed-title | 0.532 |
| chainalysis-offensive-agentic-breach-2026 | INC-17368 | event | reviewed-title | 0.383 |
| claude-pentestgpt-argentine-healthcare | INC-17369 | event | reviewed-title | 0.396 |
| bossai-ai-agent-campaign | INC-17384 | event | reviewed-title | 0.386 |
| binance-hot-wallet-compromised-ai-tool-2026 | INC-17386 | event | aiid+url | 0.616 |
| taiwan-romance-scam-ai-voice-changer-2026 | INC-17391 | event | reviewed-title | 0.869 |

## 6. The new rows

187 rows, source id `HIAI-<slug>`, one INC per ledger incident (none folded: 187 distinct `HIAI-` ids on 187 rows; the merger's URL fold is disabled for the 11 report URLs the ledger cites from several incidents, section 8).

| field | distribution |
|---|---|
| `corpus` | security: 187 (set explicitly: the ledger is cyberattacks by scope; the merger's own keyword scan agrees on all 187) |
| `attack_vector` | other: 61, malware: 56, deepfake: 29, phishing: 24, ransomware: 6, agent-hijack: 5, supply-chain: 3, data-exfiltration: 2, jailbreak: 1 |
| `severity` | Medium: 187 (the ledger has none; the schema default, not an assessment) |
| `quality_tier` | auto: 187 (explicit, D43: machine-ingested, third-party grade) |
| `confidence` (rule-derived) | low: 187 |
| `tier` | feed: 187 |
| `category` | real-world: 187 |
| ledger grade (tag `ledger-grade-*`) | confirmed: 86, strong: 75, suspected: 26 |
| `owasp_llm` | LLM07: 29, LLM03: 5, LLM04: 3, LLM02: 2, LLM01: 1 (147 rows have no OWASP code) |
| `owasp_asi` | none |
| `mitre_atlas` | AML.T0115.001: 29, AML.T0053: 5, AML.T0010: 3, AML.T0085.002: 2, AML.T0051: 1 (40 rows have an ATLAS id) |
| `nist_ai_rmf` / `maestro_layers` | 40 rows / 0 rows |
| `description_provenance` / `description_source` / `content_license.source` | original / hackingincidents / hackingincidents (MIT, obligations: attribution), all 187 |
| `disclosure_date` | on 66 rows (the ledger's `disclosed`) |

### 6.1 How the labels were produced, and what is weak

`attack_vector` is set from the ledger's own structured `ai_role` list: the FIRST role that maps to a value already in the corpus vocabulary wins (`deepfake`, `phishing-content` -> phishing, `malware-dev`/`malware-runtime-llm`/`evasion` -> malware, `supply-chain`, `agent-hijack`); social-engineering and fraud are deliberately not mapped to phishing. The 61 rows whose roles map to nothing (agentic intrusion, recon, exploit development, vulnerability research, operations automation, data analysis, LLM-account hijacking: the AI-as-weapon cases that have no value in the vocabulary) stay `other` and then go through the merger's own title/description rules, which gave `ransomware` (6), `data-exfiltration` (2) and `jailbreak` (1) from the row titles and left 61 at `other`. **The corpus vocabulary has no value for "attacker used an AI agent to intrude", so about a third of the new rows are `other`; that is the honest answer, not a label to fix by forcing a value.** Why not let the merger's text rules label everything: run over title + description they would give 17 of the role-mapped rows a different value than their roles imply (phishing, ransomware, supply-chain, model-poisoning or deepfake: e.g. `model-poisoning` from the word "backdoor" in a malware row), where the AI is the weapon and not the target. Where the role-mapped value and the text rule disagree, the role wins (the merger respects an explicit non-`other` vector). OWASP/ATLAS codes come from the merger's existing seed rule keyed on the vector (29 deepfake rows get LLM07 and AML.T0115.001, exactly as the 1,224 existing deepfake rows do; malware/phishing/other rows get none); that is the established rule, not new labelling.

### 6.2 Hand sample, 15 new rows (`random.seed(161)` over the 187)

| id | event | `attack_vector` | verdict |
|---|---|---|---|
| INC-17527 | APT36 vibeware implants | malware | sensible |
| INC-17447 | Seoul police, ARTEX ring, ~90 organisations | other | sensible (no vocabulary value) |
| INC-17535 | APT42 uses Gemini (recon, phishing content, social engineering) | phishing | coarse: four roles, the first mappable one wins |
| INC-17438 | n0n ransomware operator used an AI coding agent | malware | coarse: `ransomware` would be tighter; role mapping gave malware |
| INC-17453 | Volta-Autodoxer infostealer adds LLM victim profiling | other | acceptable (a malware row, one data-analysis role) |
| INC-17558 | GLOBAL GROUP ransomware AI chatbot negotiators | ransomware | sensible (title rule) |
| INC-17546 | COINBAIT crypto-exchange phishing kit | phishing | sensible |
| INC-17517 | Indonesian-speaking operator uses Claude Code against governments | other | sensible |
| INC-17403 | Conti-linked group impersonated IT support with AI voice | deepfake | sensible |
| INC-17574 | KnowBe4 hires North Korean IT worker, AI-enhanced photo | deepfake | sensible |
| INC-17518 | Nimbus Manticore MiniFast backdoor, AI-assisted coding | malware | sensible |
| INC-17519 | Russian-speaking operators use Claude Code for CRM data theft | other | sensible |
| INC-17581 | Mother believes fake kidnappers cloned her daughter's voice | deepfake | sensible |
| INC-17407 | Extortionist uses AI to analyse stolen files | other | sensible (not data-exfiltration: the AI is used after the theft) |
| INC-17512 | DPRK and PRC clusters use Gemini and agent tools for vulnerability research | other | sensible |

12 of 15 fully sensible, 3 coarse (right family, not the tightest value), 0 wrong. Every sampled row has `corpus: security`, `severity: Medium` (default), `quality_tier: auto`, `confidence: low`. The sample is mine and shares the labeller's blind spots; the independent check is the reviewer's own draw.

## 7. What was excluded, measured against each row's own `quote` (all 298 rows, longest run of consecutive shared words)

| ledger field | longest run | rows with a run >= 8 | rows >= 12 | disposition |
|---|---|---|---|---|
| `confidence_reason` | 19 | 15 | 9 | EXCLUDED (embeds publisher text: 111 quoted fragments, the longest 22 words) |
| `outcome` | 14 | 4 | 1 | EXCLUDED (not a D159 kept field; overlaps) |
| `summary` | 24 | 42 | 15 | EXCLUDED (held, D159) |
| `title` | 10 | 3 | 0 | kept (the ledger's own headline; 3 rows share 8-10 words with the quote) |
| `actor` | 5 | 0 | 0 | kept (label) |
| `targets` | 7 | 0 | 0 | kept (label) |
| `nexus` | 2 | 0 | 0 | kept (label) |
| emitted `description` (template) | 7 | 0 | 0 | the longest runs are enumerated model names |

`quote` is never read; `single_source_reason` and `enrichment` are not read. Test: the fixture replaces those fields with SENTINEL strings and asserts none reaches an emitted row, the attach file or the provenance file.

## 8. Merger changes (`scripts/merge_and_dedupe.py`, +92/-1) and what they could touch

1. `*.attach.json` is a recognised ingest side file (a dict by design, loads as zero rows).
2. `_apply_reference_attachments`: appends references to the SURVIVING entry holding one of the target's `source_ids`; touches nothing else; aborts if an attachment resolves to 0 or more than 1 entry. It runs AFTER curation overrides (found during the build: two targets carry a whole-list `references` override and the first attempt silently lost their attachments; the per-entity compare caught it).
3. `_check_attachment_ids`: after INC ids are assigned, aborts if an attachment's target is not the INC id it was written for.
4. `FOLD_EXEMPT_URLS`: the ledger splits one vendor report into several incidents (11 report URLs are cited by 2+ new rows, up to 10 incidents on one Anthropic report; without this the merger URL-folds them, shown by `test_fold_exempt_url_prevents_url_fold_and_default_still_folds`: two entries sharing a URL fold to one). Those normalised URLs, listed in the attach file, are treated like an aggregate page by `is_aggregate_url` (the existing D117 mechanism). Effect on existing rows: none today (the delta above); effect on FUTURE builds: a new row from another source that shares one of those 11 URLs will not URL-fold into the ledger rows.

## 9. Defects found while building, and decisions the user may want to make

1. **Idempotence bug (fixed, tested):** re-running the ingest against the post-build corpus changed the output (227/70 -> 224/73) because URLs the ingest itself attached made later rows look matched. Fixed by re-listing previously attached URLs; test `test_committed_outputs_rebuild_byte_for_byte_from_the_pinned_snapshot`. Output is now identical from the base corpus, from an empty attach file, and from the post-build corpus.
2. **Retained-prior trap:** building over a working tree that already holds an earlier build of these rows keeps the rows no longer emitted (they are retained as priors: 16,072 instead of 16,032). The committed build must be made from the base `data/`; the build here was.
3. **Snapshot stripped (user ruling D162; supersedes the verbatim snapshot of the first D161 commit):** `ingest/snapshots/hackingincidents/incidents.json` keeps only the fields the ingest reads and drops `quote`, `summary`, `confidence_reason`, `outcome`, `single_source_reason`, `enrichment` and the per-source `date`, `verified_on`, `fetch_status`, `quote_found`, `kind`, `archive_url`, `aggregator_only`, `primary_via_party`. The raw download (690,343 bytes, sha256 e1e95518...) is pinned in the provenance file and was never committed in the rewritten branch. The section 7 measurements were taken on the raw bytes at strip time and are carried forward in the provenance file. Emitted rows are byte-identical to those of the verbatim-snapshot commit (`data/incidents.json` and `data/stats.json` compared).
4. **Rows with the ledger's own mis-citations:** none found; the one surprising AIID join (`llmjacking-sysdig-bedrock-2024` -> INC-08183) is correct (AIID 898); INC-08183 is itself an over-merged corpus row (title `Google Bard Conversation Exfiltration`), an existing corpus defect, not touched.

## 10. Checks run

| check | result |
|---|---|
| per-entity compare, base vs head `data/incidents.json` | 80 rows changed, fields `references`, `last_seen`, `updated` only; 187 added; 0 removed |
| `scripts/aiid_change_report.py --before-ref HEAD` | new rows 187 (new AIID rows 0); existing AIID-carrying rows changed 46 (7 also carry OECD ids); fields `last_seen`, `references`, `updated` only |
| `scripts/check_corpus_flips.py --before-ref HEAD` | flips 0, undeclared 0, added 187, removed 0 |
| `python scripts/validate.py` | 16032/16032 entries valid, 0 with errors; integrity: no duplicate keys, all deprecations resolve |
| `python scripts/check_stats_drift.py` | clean |
| `python scripts/lint_atlas_ids.py` | OK |
| `pytest tests` | see the task report for the exact counts |

## 11. Re-derivation

```
git checkout d161-hackingincidents-ingest
python scripts/ingest_hackingincidents.py            # offline, from the pinned snapshot; output identical
python scripts/parse_existing.py && python scripts/merge_and_dedupe.py   # from the BASE data/ (git checkout 9019539d -- data/ first)
python scripts/render_markdown.py && python scripts/render_docs_stats.py && python scripts/validate.py
python scripts/aiid_change_report.py --before-ref 9019539d --out-json /tmp/s.json && python scripts/check_corpus_flips.py --declared-json /tmp/s.json --before-ref 9019539d
python -m pytest tests/test_ingest_hackingincidents.py
```

