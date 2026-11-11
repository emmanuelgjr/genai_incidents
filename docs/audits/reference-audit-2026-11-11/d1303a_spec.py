"""D130-3a specification: the 6 rows D130-2 deferred plus batch 1 (32 rows) of the D130-3 list (list.json).

DATA ONLY. build_overrides.py turns it into entries in data/curation_overrides.json; export_evidence.py turns the fetch
cache into the committed evidence file. Nothing in `make build` imports this module.

Every reference WRITTEN into the corpus (REPLACE) was fetched on 2026-11-11 through ingest/common.fetch_once
(fetch_evidence.py) and its page names the incident; the tokens in EVIDENCE are re-checked by export_evidence.py, which
fails on a missing token. References that were only REMOVED, or KEPT, are listed with their fetch status in the audit.
Agent-suggested; not human-reviewed (D130(c): awaiting user re-review).
"""

AS_OF = "2026-11-11"
BASE = "64109452"
NOTE_PREFIX = "agent-suggested D130-3a reference remediation, 2026-11-11; pending user re-review."

# --- references_remove rows: id -> flagged URLs removed (row keeps its other references) ----------------------------
# Reasons (from the 2026-11-11 fetches; see the audit): homepage/product/index page, dead (404), refused, or not
# naming the incident. The 6 deferred rows are marked in DEFERRED6.
REMOVE = {
    "INC-00021": ["http://trezor.com"],
    "INC-01194": ["https://trysixth.com/"],
    "INC-01348": ["https://www.llamaindex.ai/"],
    "INC-01553": ["https://ollama.com/"],
    "INC-01724": ["https://raytha.com"],
    "INC-02076": ["https://www.kxan.com/driverless/"],
    "INC-02150": ["http://openairinterface.com", "https://openairinterface.org/"],
    "INC-02347": ["https://iocharger.com"],
    "INC-02505": ["http://dify.com"],
    "INC-02516": ["https://dify.ai"],
    "INC-02761": ["http://langchain-chatglm-webui.com"],
    "INC-02800": ["https://python.langchain.com/docs/security/"],
    "INC-02864": ["https://mattermost.com/security-updates"],
    "INC-03209": ["https://www.microsoft.com/en-us/security/blog/"],
    "INC-03276": ["https://dotapp.uk"],
    "INC-03292": ["https://phcode.dev/", "https://www.postbox-inc.com/"],
    "INC-03423": ["https://monica.im/desktop"],
    "INC-04285": ["https://premiumaddons.com/change-log/"],
    "INC-04383": ["https://arxiv.org/abs/2103.03874", "https://arxiv.org/abs/2110.14168"],
    "INC-04959": ["https://www.oligo.security/shelltorch"],
    "INC-05009": ["https://docs.dependencytrack.org/changelog/"],
    "INC-05421": ["http://abna24.com/b4xD"],
    "INC-05425": ["http://abna24.com/b8b9"],
    # the 6 deferred by D130-2 (ruling D139): references_remove / fields-clear mechanism
    "INC-01015": ["https://flowiseai.com"],
    "INC-01291": ["https://www.langchain.com/"],
    "INC-01589": ["https://openclaw.ai/blog"],
    "INC-02471": ["https://github.com/MaccariTA"],
    "INC-02871": ["https://github.com/Y4tacker"],
    "INC-04207": ["https://arxiv.org/abs/2402.06627"],
}
DEFERRED6 = ["INC-01015", "INC-01291", "INC-01589", "INC-02471", "INC-02871", "INC-04207"]

# --- single-reference rows whose only reference is a publisher index: whole-list replacement ----------------------
RECO = "https://www.reco.ai/blog/openclaw-the-ai-agent-security-crisis-unfolding-right-now"
PILLAR = "https://www.pillar.security/blog/the-agent-security-paradox-when-trusted-commands-in-cursor-become-attack-vectors"
EMBRACE = "https://embracethered.com/blog/posts/2024/deepseek-ai-prompt-injection-to-xss-and-account-takeover/"
UNIT42 = "https://unit42.paloaltonetworks.com/npm-supply-chain-attack/"
SYSDIG = "https://www.sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes"

REPLACE = {
    "INC-01600": {"old": "https://www.reco.ai/newsroom",
                  "ref": {"title": "OpenClaw Security Risks: AI Agent Threats in SaaS - Reco", "url": RECO, "type": "vendor"}},
    "INC-01641": {"old": "https://www.pillar.security/blog",
                  "ref": {"title": "The Agent Security Paradox: When Trusted Commands in Cursor Become Attack Vectors - Pillar Security (2026-01-14)",
                          "url": PILLAR, "type": "research"}},
    "INC-02498": {"old": "https://embracethered.com/blog/",
                  "ref": {"title": "DeepSeek AI: From Prompt Injection To Account Takeover - Embrace The Red (2024-11-29)",
                          "url": EMBRACE, "type": "research"},
                  "title": "DeepSeek AI prompt injection to XSS and account takeover (Embrace The Red)",
                  "description": ("Embrace The Red showed that DeepSeek's web chat could be driven by prompt injection to execute "
                                  "script in the page (XSS); the script could read the userToken stored in localStorage on "
                                  "chat.deepseek.com, which was all that was needed to take over a user's session.")},
    "INC-03212": {"old": "https://unit42.paloaltonetworks.com/",
                  "ref": {"title": "\"Shai-Hulud\" Worm Compromises npm Ecosystem in Supply Chain Attack - Unit 42", "url": UNIT42,
                          "type": "research"},
                  "title": "Shai-Hulud npm worm: malicious bash script assessed as LLM-generated (Unit 42)",
                  "description": ("Unit 42 investigated the self-replicating Shai-Hulud npm worm, responsible for the compromise of "
                                  "hundreds of software packages, and assessed with moderate confidence that an LLM was used to "
                                  "generate the malicious bash script, based on its comments and emojis."),
                  "affected": "npm ecosystem (hundreds of compromised packages)"},
    "INC-03248": {"old": "https://www.sysdig.com/threat-research",
                  "ref": {"title": "AI-assisted cloud intrusion achieves admin access in 8 minutes - Sysdig (2026-02-03)", "url": SYSDIG,
                          "type": "research"}},
}

# --- no confirmed source: status unverified (D130(b)); references and quality_tier left as found ---------------------
UNVERIFIED = {
    "INC-00570": ["The only reference is the publisher's news index (R1).",
                  "aim.security robots.txt could not be verified (HTTP 403), so ingest/common.fetch_once refuses the host (fail-closed); no page naming 'continuing EchoLeak research and variants' was fetchable, and no other source was found."],
    "INC-03573": ["The only reference is the publisher's research index (R1).",
                  "anthropic.com/research and /news were fetched (200) and name no Frontier Threats Red Team spear-phishing scaling study; no other source was found. The row also carries a second seed id (an election-influence study) with no source."],
}

# --- examined, not changed: the flagged URL is a real source (fetched, names the incident) -------------------------
KEPT = {
    "INC-00864": {"urls": ["https://cybersecuritynews.com/flowise-vulnerability/"],
                  "why": "R1 false positive: an article (one-hyphen slug) on the OX Security finding that Anthropic's MCP SDKs allow command execution; it names the incident."},
    "INC-05052": {"urls": ["https://real-gradients.github.io/", "https://arxiv.org/abs/2212.14315"],
                  "why": "R1/R2 false positive: the dedicated site and paper behind ATLAS case AML.CS0032 (screenshots of 100 evasive phishing webpages, MLSEC anti-phishing analysis); the R2 title-overlap flag is a token artefact of a generic row title."},
}
# INC-02150 also keeps https://cellularsecurity.org/ransacked (names CVE-2024-24426); it is flagged R1 but is not removed.
KEEP_ALSO = {"INC-02150": ["https://cellularsecurity.org/ransacked"]}

# --- pages whose row-linking tokens export_evidence.py re-checks against the fetch cache -------------------------------
EVIDENCE = {
    RECO: ["OpenClaw", "135,000", "first major AI agent security crisis", "21,639", "ClawHub"],
    PILLAR: ["CVE-2026-22708", "Cursor", "prompt injection", "validation", "allowlist"],
    EMBRACE: ["DeepSeek", "userToken", "localStorage", "XSS", "Account Takeover"],
    UNIT42: ["Shai-Hulud", "hundreds of software packages", "LLM was used to generate the malicious bash script"],
    SYSDIG: ["large language models", "8 minutes", "November 28, 2025", "admin"],
    "https://cybersecuritynews.com/flowise-vulnerability/": ["OX Security", "Model Context Protocol", "Anthropic"],
    "https://cellularsecurity.org/ransacked": ["CVE-2024-24426", "OpenAirInterface"],
    "https://real-gradients.github.io/": ["phishing", "evasive"],
}
