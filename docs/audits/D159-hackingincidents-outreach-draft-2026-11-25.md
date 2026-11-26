# D159 outreach DRAFT: hackingincidents.ai (NOT SENT; the user sends)

**Date:** 2026-11-25 · DRAFT, do-not-regenerate record. Non-blocking: the audit
recommends ingesting facts + link only whether or not this is answered. Contact
route on the site: `/submit/` says "mention @danielmiessler on X with the source
link"; operator is Daniel Miessler / Unsupervised Learning. Send from the user's
own account and sign it; this draft deliberately carries no personal address.

**Subject:** Reusing hackingincidents.ai data in an open incident dataset: licence check

Hello Daniel,

I maintain genai_incidents, an open dataset of GenAI and AI-security incidents
(CC-BY-4.0 for our own data, with third-party licences preserved where we reuse
upstream material). hackingincidents.ai looks like an excellent, carefully sourced
complement, and I would like to include it as a source. Before I do, I would like
to check three things so I honour your terms exactly.

1. Your data page says the data is published under the Substrate repository's MIT
   licence (Copyright (c) 2025 Daniel Miessler). Does that cover the dataset in
   `Data/AI-Hacking-Incidents/` (incidents.json, incidents.csv, sources.json)?
   If so, I will carry your copyright and MIT notice with the ledger-derived fields
   and cite it as "hackingincidents.ai, Unsupervised Learning, accessed <date>".
2. The `quote` fields are third-party text that "remain under the publishers'
   terms". I plan not to redistribute them. Is the `summary` field your own
   wording, written or edited by you, so it falls under the MIT grant, or is it
   derived from the publishers' text or machine-drafted from it? Until I hear, I
   will keep only structured fields (title, date, actor, targets, models, grade,
   source links) and write my own summaries from the primary sources.
3. Is there any fetch cadence or etiquette you would like me to follow? I plan to
   pull the repository copy of incidents.json no more often than weekly, with an
   identifying User-Agent, and to link back to each incident page.

I will present your grade (Confirmed / Strong / Suspected) as your judgment, not
ours, with a link to your method page. If you would prefer I not use the data, I
will not.

Thank you for building this.

[sender name and project link: to be filled in by the user]
