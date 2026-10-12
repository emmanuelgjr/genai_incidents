# Contributing

Thanks for helping grow this dataset. A few ground rules:

## Every incident needs a source

No exceptions. If you can't link to a public advisory, vendor post, news article, paper, or researcher writeup, the entry doesn't go in. Anonymous tips and "I heard about this" don't belong here — open an issue instead and the maintainer can chase it down.

## Taxonomy mapping

Map each entry to the four core per-incident taxonomy fields below, **where appropriate**. MAESTRO and VERIS are not contributor-set: MAESTRO is inherited only from certain upstream sources, and VERIS is computed automatically at export time — see TAXONOMIES.md. If an incident is purely a generic CVE in an LLM-adjacent component with no agentic dimension, leave `owasp_asi` empty rather than guessing.

- `owasp_llm`: OWASP Top 10 for LLM Applications 2026 — `LLM01`–`LLM10`
- `owasp_asi`: OWASP Top 10 for Agentic Applications (ASI) — `ASI01`–`ASI10`
- `nist_ai_rmf`: AI 100-1 subcategory codes (`GOVERN-1.1`, `MEASURE-2.7`, etc.) — pick the most relevant 1–4
- `mitre_atlas`: ATLAS technique IDs (`AML.T0051`, including subtechniques like `AML.T0051.001`)

## Workflow

1. Fork and branch.
2. Edit `data/incidents.json` directly, or drop a JSON array into `ingest/<your_source>.json` and let the merger normalize it.
3. Run:
   ```bash
   python scripts/merge_and_dedupe.py
   python scripts/validate.py
   python scripts/render_markdown.py
   ```
4. Commit the regenerated `data/incidents.json`, `data/incidents.min.json`, and `INCIDENTS.md` alongside your changes.
5. Open a PR with a one-line summary of what was added/changed.

## Quality bar

- Descriptions: 1–3 sentences, factual, no editorializing.
- Severity should reflect the **demonstrated** impact, not the theoretical worst case. Use `Critical` only for CVSS ≥9.0 or evidence of in-the-wild exploitation with significant blast radius.
- For CVEs, always link the NVD page and the canonical vendor advisory.
- For researcher disclosures, link the original blog post — not just the news writeup.

## Don't

- Don't synthesize incidents you can't source.
- Don't paste long quoted blocks from the source articles — describe the incident in your own words, then link.
- Don't include incidents that are pure fairness/bias harms with no security primitive. Those belong in other databases (AIID, AVID full set) and aren't this dataset's scope.

## License

By contributing, you agree to license your contributions under the project's dual license: code under MIT, data under CC-BY-4.0.
