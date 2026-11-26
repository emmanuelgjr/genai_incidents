# D159 outreach DRAFT: hackingincidents.ai (NOT SENT; the user sends)

**Date:** 2026-11-25 · DRAFT, do-not-regenerate record. Non-blocking: the audit
recommends ingesting facts + link only whether or not this is answered. Contact
route on the site: `/submit/` says "mention @danielmiessler on X with the source
link"; operator is Daniel Miessler / Unsupervised Learning. Send from the user's
own account and sign it; this draft deliberately carries no personal address.

*Update 2026-11-26 (after gate bounce #1, draft still unsent): question 1 and the
cadence line in question 3 were edited in place, because the site download and the
Substrate repo copy are different datasets (298 rows / 2026-11-24 vs 286 rows /
2026-11-17) and the original wording asked only about the repo copy. See U1 in
`D159-hackingincidents-source-eval-2026-11-25.md`.*

**Subject:** Reusing hackingincidents.ai data in an open incident dataset: licence check

Hello Daniel,

I maintain genai_incidents, an open dataset of GenAI and AI-security incidents
(CC-BY-4.0 for our own data, with third-party licences preserved where we reuse
upstream material). hackingincidents.ai looks like an excellent, carefully sourced
complement, and I would like to include it as a source. Before I do, I would like
to check three things so I honour your terms exactly.

1. Your data page says the data is published under the Substrate repository's MIT
   licence (Copyright (c) 2025 Daniel Miessler). The site's downloads
   (`/incidents.json`, updated 2026-11-24, 298 incidents) are newer than the copy
   in `Data/AI-Hacking-Incidents/` in the Substrate repository (updated
   2026-11-17, 286 incidents), and I see the repo's source.md says it lags the
   site's own repository. Does the MIT grant cover the site's current downloads as
   well as the repo copy? If so, I will fetch the site copy, carry your copyright
   and MIT notice with the ledger-derived fields, and cite it as
   "hackingincidents.ai, Unsupervised Learning, accessed <date>".
2. The `quote` fields are third-party text that "remain under the publishers'
   terms". I plan not to redistribute them. Is the `summary` field your own
   wording, written or edited by you, so it falls under the MIT grant, or is it
   derived from the publishers' text or machine-drafted from it? Until I hear, I
   will keep only structured fields (title, date, actor, targets, models, grade,
   source links) and write my own summaries from the primary sources.
3. Is there any fetch cadence or etiquette you would like me to follow? I plan to
   pull incidents.json no more often than weekly, with an
   identifying User-Agent, and to link back to each incident page.

I will present your grade (Confirmed / Strong / Suspected) as your judgment, not
ours, with a link to your method page. If you would prefer I not use the data, I
will not.

Thank you for building this.

[sender name and project link: to be filled in by the user]
