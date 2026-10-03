# Draft — ENISA: may EUVD API data be redistributed under CC BY 4.0?

**STATUS:** DRAFTED 2026-10-03; **not sent**. The user sends it and logs the
date in `docs/outreach/README.md` and `docs/SOURCE_LICENSES.md` section 6.4.
Do not edit the message body once sent.

**To (UNCONFIRMED):** `info@enisa.europa.eu`, the contact named in ENISA's IPR
policy (source-expansion evaluation, row 1B.2). The user should confirm it is
the right desk for an EUVD data-reuse question before sending; if ENISA
publishes a dedicated EUVD contact, prefer that.

**Suggested subject:** EUVD API data: may it be redistributed with attribution
in an open dataset (CC BY 4.0)?

**What this gates:** nothing is ingested from EUVD until a written answer
exists. EUVD is not needed for CVE coverage (every item is a CVE alias that we
take from the CVE Program). The only EUVD-unique fields we would use are EUVD
ids and EPSS values.

---

Dear ENISA EUVD team,

I maintain **genai_incidents**, an open, machine-readable index of publicly
reported security incidents and vulnerabilities involving generative AI, with
mappings to frameworks such as OWASP and MITRE ATLAS. Our aggregation is
published under CC BY 4.0, and each upstream source's own terms are recorded and
carried through rather than overridden.

We would like to reference the European Vulnerability Database, but we do not
want to reuse its data without being sure we may. We have not copied any EUVD
data into the dataset.

Your Legal Notice (https://www.enisa.europa.eu/about-enisa/legal-notice) says:
"Reproduction of ENISA material published on this website is authorized,
provided the source is acknowledged, unless it is stated otherwise." We could
not establish whether data served by the EUVD API
(euvdservices.enisa.europa.eu) counts as "material published on this website".
We also noticed that the `euvd-docs-public` repository carries a licence that
does not permit reuse of its contents; we read that as covering the
documentation only, and we are not copying it.

Could you tell us:

1. Does the Legal Notice's reproduction clause cover data returned by the EUVD
   API?
2. May we redistribute selected EUVD API fields within an open dataset licensed
   under CC BY 4.0, with attribution to ENISA/EUVD? If CC BY 4.0 is not
   acceptable, what terms would you prefer?
3. Is there a preferred attribution wording?

What we would copy, if you agree: the EUVD identifier and the EPSS score
attached to a CVE, each with a link back to the EUVD entry and a statement of
source and retrieval date. What we would **not** copy: EUVD description text
(we take descriptions from the CVE record itself), anything from the
documentation repository, or any bulk mirror of the database. We would fetch
politely, at no more than one request every three seconds, with an identifying
User-Agent and contact address.

No urgency. If the answer is no, we will simply keep EUVD out of the dataset
and link to it instead.

Thank you for your time,
[Maintainer name]
genai_incidents

---

## Facts behind this draft (internal; not part of the message)

All taken from `docs/specs/source-expansion-evaluation.md` row 1B.2 and
section 5.3 (gated PASS; the legal-notice sentence and the docs-repo LICENSE
were verified by red-reviewer via curl on 2026-10-03). Not re-fetched when
drafting.

- Legal Notice sentence quoted verbatim above.
- `enisaeu/euvd-docs-public` LICENSE: "This repository is made available solely
  for programmatic access by the EUVD frontend. No reuse, redistribution, or
  modification of its contents is permitted without written permission from
  ENISA." The message paraphrases this (docs only) rather than quoting it.
- API fields observed (JSON, no licence or terms field): `id, enisaUuid,
  description, datePublished, dateUpdated, baseScore, baseScoreVersion,
  baseScoreVector, references, aliases, assigner, epss, enisaIdVendor`.
- "Every item is a CVE alias": 3,873 of 3,873 items sampled carried a CVE
  alias, 0 EUVD-only (evaluation section 5.3, measured).
- EPSS is FIRST's data; FIRST's own terms were not checked. The message does not
  claim ENISA can license EPSS; if ENISA says EPSS is FIRST's, a separate check
  of FIRST's terms is owed before any EPSS value is shipped.
- The "3 s spacing, identifying User-Agent" statement describes
  `ingest/common.py`'s conduct (docs/INGESTION_CONDUCT.md), not a new promise.
