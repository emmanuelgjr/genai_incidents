"""D130-2L per-row relabel decisions (ruling D139(c), 2026-10-15). Data only; read by build_overrides.py.

Every decision names its basis. Kinds:
  rule        the repo's own deterministic code, run on the D130-2 text (classify_attack_vector,
              parse_existing.derive_atlas_and_nist, seed_frameworks_from_vector, fill_taxonomy,
              merge_into's max-severity) -- computed by build_overrides.py, not typed here
  provenance  the value came only from a merged seed that describes a DIFFERENT incident
              (checked by build_overrides.py: present in the dropped seed, absent from every kept source)
  unsupported the value encodes a claim D130-2 removed from the row's text as unsupported by the
              fetched source (docs/audits/reference-audit-2026-10-15/reference-audit-2026-10-15.md,
              per-row "description before" vs "description after" and "dropped" lines)
  judgement   agent judgement on the new text; agent-suggested, pending user re-review

Removal-only for tags and maestro_layers: nothing is added, no note is rewritten.
"""

AS_OF = "2026-10-16"
BASE = "05ff1e75"
NOTE_PREFIX = ("agent-suggested D130-2L relabel (ruling D139(c)), 2026-10-16; pending user re-review. "
               "Labels re-derived from the D130-2 text; evidence: docs/audits/relabel-d130-2l-2026-10-16.md.")

# Legacy raw attack_vector strings whose ATTACK_VECTOR_HINTS match in scripts/parse_existing.py is a
# substring artifact, not the word in the text: the key "rce" matches inside "enfo-rce-ment".
HINT_ARTIFACT = {
    "INC-035": "'rce' matched inside 'enforcement' (raw text: 'Not adversarial - regulatory enforcement; ...')",
    "INC-043": "'rce' matched inside 'enforcement' (raw text: 'Not adversarial - regulatory enforcement; ...')",
}

ROWS = {
    "INC-02454": {
        "key": "INC-036",
        "drop_sources": {"INC-039": "NYT v OpenAI copyright ruling: a different incident merged into this row (legacy seed title "
                                    "'NYT v OpenAI - copyright training data ruling implications')"},
        "drop_codes": {},
        "vector": None,  # rule
        "tags_remove": {
            "bias": "unsupported: D130-2 dropped the racial-bias findings ('none in the sources; the case is about scraping and BIPA')",
        },
        "maestro_remove": {
            ("L2", "origin"): "unsupported: note asserts 'biased training data ... demographic representation gaps' (bias claims dropped by D130-2)",
            ("L1", "impact"): "unsupported: note asserts 'measurable racial accuracy disparities' (dropped by D130-2)",
            ("L6", "blind-spot"): "unsupported: note asserts 'no bias testing' (bias testing as a settlement term dropped by D130-2)",
        },
    },
    "INC-02774": {
        "key": "INC-035",
        "drop_sources": {"INC-050": "noyb right-to-erasure / data-retention GDPR challenge: a different matter (D130-2 dropped "
                                    "the noyb reference as 'a different matter from the Garante decision')"},
        "drop_codes": {},
        "vector": ("privacy-violation",
                   "judgement: the rule's first hit is 'data breach' (data-exfiltration), from the Garante's finding that "
                   "OpenAI 'had not notified it of the data breach suffered in March 2023'. That is one of four findings and "
                   "describes a notification failure, not an exfiltration; the decision's subject is unlawful processing of "
                   "personal data for training ('without first identifying an adequate legal basis'), transparency and age "
                   "verification -> privacy-violation"),
        "tags_remove": {
            "consent": "unsupported: from the old title 'consent and data minimization failures'; the new text says 'legal basis', not consent",
            "data-minimization": "unsupported: D130-2 dropped the GDPR Article 5 (data minimisation) claim ('the Garante page names no article numbers')",
        },
        "maestro_remove": {},
    },
    "INC-02899": {
        "key": "INC-105",
        "drop_sources": {"LEGACY-INC-00149": "legacy table row whose whole text is the claim D130-2 removed ('Agents were public by "
                                             "default and lacked authentication ... enumerate and access exposed agents')"},
        "drop_codes": {
            "INC-105": {
                "ASI03": "unsupported: assigned for the seed's 'agents publicly accessible without authentication' (raw attack_vector), dropped by D130-2",
                "ASI07": "unsupported: same seed basis as ASI03; the new text has no inter-agent communication",
            },
        },
        "vector": None,  # rule
        "tags_remove": {
            "default-public": "unsupported: 'public by default' dropped by D130-2 (neither Zenity post says it)",
            "authentication": "unsupported: 'lacked authentication' dropped by D130-2",
        },
        "maestro_remove": {
            ("L4", "origin"): "unsupported: note asserts 'Default public exposure with no authentication' (dropped by D130-2)",
        },
    },
    "INC-03004": {"key": "INC-033", "drop_sources": {}, "drop_codes": {}, "vector": None,
                  "tags_remove": {}, "maestro_remove": {}},
    "INC-03472": {
        "key": "INC-074", "drop_sources": {}, "drop_codes": {}, "vector": None, "tags_remove": {},
        "maestro_remove": {
            ("L6", "impact"): "unsupported: note asserts 'Title VII violations; EEOC enforcement; class action settlements'; D130-2 "
                              "dropped 'Several vendors settled with affected candidates' and the new text has EEOC technical "
                              "assistance, not enforcement",
        },
    },
    "INC-03955": {"key": "INC-075", "drop_sources": {}, "drop_codes": {}, "vector": None,
                  "tags_remove": {}, "maestro_remove": {}},
    "INC-03972": {"key": "INC-027", "drop_sources": {}, "drop_codes": {}, "vector": None,
                  "tags_remove": {}, "maestro_remove": {}},
    "INC-04179": {
        "key": "INC-044",
        "drop_sources": {"INC-048": "AI companion apps (Character.AI / Replika) trust exploitation: a different incident merged "
                                    "into this row (D130-2 also dropped the NYT Character.AI reference as 'unrelated to this incident')"},
        "drop_codes": {
            "INC-044": {
                "LLM04": "unsupported: the seed's stated basis (raw attack_vector) is 'annotation workers exposed to sensitive data "
                         "without access controls; worker metadata collected without consent', both dropped by D130-2; the new "
                         "text is pay and working conditions, which no OWASP LLM code covers",
                "DSGAI13": "unsupported: same seed basis as LLM04",
                "DSGAI14": "unsupported: same seed basis as LLM04",
                "DSGAI16": "unsupported: same seed basis as LLM04",
                "DSGAI19": "unsupported: same seed basis as LLM04",
            },
        },
        "vector": ("other",
                   "judgement: the rule's first hit is 'self-harm' (unsafe-advice), which in the new text is a kind of content "
                   "the moderators reviewed ('depicting ... violence, self-harm, murder'), not advice an AI gave; the incident is "
                   "labour conditions (pay, trauma, dismissal), which has no value in the attack_vector vocabulary -> other"),
        "tags_remove": {
            "privacy": "unsupported: D130-2 dropped the data-exposure / metadata-consent claims",
            "rlhf": "unsupported: 'RLHF content moderation labeling' is in the old text only",
        },
        "maestro_remove": {
            ("L2", "origin"): "unsupported: note asserts 'exposed sensitive data to workers without access controls' (dropped by D130-2)",
            ("L6", "blind-spot"): "unsupported: note asserts 'no audit of annotation platform security' (security claims dropped by D130-2)",
            ("L1", "impact"): "unsupported: note asserts the labelling environment affected RLHF quality / model alignment; not in the new text",
        },
    },
    "INC-04221": {
        "key": "INC-049", "drop_sources": {}, "drop_codes": {}, "vector": None,
        "tags_remove": {
            "synthetic-data": "unsupported: synthetic CSAM generation by Stable Diffusion is in the old text only",
            "legal-liability": "unsupported: D130-2 dropped 'the legal-liability conclusion'",
        },
        "maestro_remove": {
            ("L1", "impact"): "unsupported: note asserts 'Model learned to generate CSAM'; the new text reports CSAM in the dataset only",
            ("L6", "impact"): "unsupported: note asserts 'Legal liability for synthetic CSAM' (dropped by D130-2)",
        },
    },
    "INC-04653": {
        "key": "INC-008", "drop_sources": {},
        "drop_codes": {
            "INC-008": {
                "LLM02": "unsupported: Sensitive Information Disclosure was the 'embedded secrets / live API keys' claim, dropped by "
                         "D130-2; the open-source code at issue is public, not confidential",
                "LLM08": "unsupported: Hidden Context Exposure; no hidden context or system prompt in old or new text, and the "
                         "seed's memorisation/secrets basis is dropped",
                "DSGAI07": "unsupported: the repo's own text ties DSGAI07 to secrets ('scan corpus for secrets before ingestion "
                           "(DSGAI07)', this row's mitigation); secrets claim dropped by D130-2",
            },
        },
        "vector": None,  # rule (no hit -> other; base is already other)
        "category": ("real-world",
                     "judgement: the new text is a proposed class action lawsuit (reported by The Verge 2022-11-08), not a "
                     "research demonstration; the 'multiple studies ... researchers at NYU' basis was dropped by D130-2"),
        "tags_remove": {
            "secrets": "unsupported: D130-2 dropped the API key / password / private key claims",
        },
        "maestro_remove": {
            ("L1", "origin"): "unsupported: note asserts the model reproduced 'secrets' (dropped by D130-2)",
            ("L2", "origin"): "unsupported: note asserts 'repositories with embedded credentials' (dropped by D130-2)",
            ("L5", "blind-spot"): "unsupported: note asserts no 'output scanning for secrets' (secrets claim dropped by D130-2)",
        },
    },
    "INC-04955": {
        "key": "INC-043", "drop_sources": {},
        "drop_codes": {
            "INC-043": {
                "DSGAI20": "unsupported: the old text names this row 'the defining case for DSGAI20 - data localization "
                           "violations in AI systems'; Project Clover / data localization dropped by D130-2",
            },
        },
        "vector": ("privacy-violation",
                   "judgement: no rule hit (the privacy rule needs 'privacy violation/breach' phrasing); the DPC found "
                   "TikTok's handling of children's data infringed the GDPR (transparency; accounts of users aged 13-17 "
                   "public by default) -> privacy-violation, consistent with INC-02454 and INC-02774"),
        "tags_remove": {
            "data-localization": "unsupported: Project Clover / data localization dropped by D130-2",
            "project-clover": "unsupported: dropped by D130-2 (EUR 12 billion figure and mandate)",
            "cross-border": "unsupported: the cross-border transfer pressure is in the old text only",
        },
        "maestro_remove": {
            ("L2", "origin"): "unsupported: note asserts data 'transferred across jurisdictions' (old text only)",
            ("L4", "impact"): "unsupported: note asserts 'EUR 12B Project Clover' (dropped by D130-2)",
        },
    },
}
