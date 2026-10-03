# Source-expansion evaluation — tranche 2 (worldwide): scope record

**Dated record, 2026-10-02. Do not regenerate.** (Working agreement 4.) This
file records the user's tranche-2 brief verbatim in substance, plus what the
foreman found when it set the work up. The deliverable is a separate file,
`docs/specs/source-expansion-evaluation.md`, written by the specialists.

## Foreman finding at setup: the tranche-1 record does not exist

The brief says "same discipline as the first ten" and asks for a first-wave
recommendation "across BOTH tranches". **No tranche-1 evaluation exists in the
repository.** The foreman checked on 2026-10-02:

- `git grep -i huntr` across every local and origin ref, `*.md`. The only hit
  outside generated incident pages is `ingest/README.md:40`, a line about the
  `bounty_incidents.json` filename.
- All 21 worktrees under `.claude/worktrees/` have clean trees, and none holds
  an evaluation file.
- `PROGRESS.md` and `MASTER_IMPROVEMENT_PLAN.md` have no entry for "tranche",
  "source expansion", "first ten" or "wave one".

The known tranche-1 names come from the user's prior: **CISA** and **huntr**.
CISA KEV is already an ingested source (`SOURCE_LICENSES.md` §2.1), so
tranche-1 "CISA" presumably means CISA advisory surfaces beyond KEV. That is a
foreman inference and has not been confirmed. **The other eight names are
unknown.** This has the same shape as working agreement 1's lost
deliverables: a chat-only artifact that a session boundary erased. The
cross-tranche ranking cannot be built until the user supplies the ten names
and they are re-evaluated under this same discipline.

## Discipline (both tranches)

1. **license-auditor pre-row first.** Each candidate gets a pre-row in the
   `SOURCE_LICENSES.md` column format: license (operative clause quoted, plus
   URL and date checked) · scrape-permitted (robots.txt and ToS) ·
   redistribute-verbatim · relicense-compatible (CC BY 4.0 data) · action
   (a/b/c/d) · date-checked. This applies invariant 10 at evaluation time.
   The pre-rows live in the evaluation file. They move into
   `SOURCE_LICENSES.md` only inside the ingest PR for that source.
2. **Absence findings follow the standing rule.** State the retrieval method
   in the row, presume the finding method-suspect, and route it to
   red-reviewer for a raw-HTML shell check before it is recorded as a
   negative or UNKNOWN.
3. **pipeline-engineer then estimates**, for each candidate that is not
   licence-blocked:
   - AI-relevant volume (backlog and per-year rate) and how it was estimated
   - overlap and dedupe load against the existing corpus
   - ingest shape (API, feed, bulk dump or HTML; pagination; filter method)
   - corpus fit (incidents, vulnerabilities or capabilities)
   - reconciliation cost: WS4-T2 retraction and revision handling applies to
     every source forever
   - non-English handling, named in every non-English row. Translated
     summaries count as original prose: they are generated offline and
     committed, per the WS0-T3 determinism rule, and never produced by a
     model call in the build path.
4. **Ranking** = licensing-cleanliness × volume × corpus fit × inverse
   maintenance cost. The method and every factor score are shown.
5. **Output:** one committed ranked file, with waves of 2–3 sources for the
   user's approval. **No ingest code is written before a ruling.**

## Tranche-2 candidates

- **Government/CERT (incidents + vulnerabilities, each filtered to
  AI-relevant advisories):** UK NCSC (OGL), ACSC Australia (CC BY 4.0), CCCS
  Canada, ENISA, BSI/CERT-Bund, ANSSI/CERT-FR, JPCERT + JVN, SingCERT/CSA,
  CERT-EU.
- **Vulnerability databases:**
  - EUVD (ENISA, NIS2)
  - cvelistV5 (upstream of NVD)
  - VulnCheck KEV (enriches `exploited_in_wild`)
  - AVID. Its row needs the WS7-T1 neighbour-positioning sentence.
- **Regulators and courts (incidents):** Italy Garante; EDPB registry, the
  Dutch DPA and CNIL; UK ICO; Brazil ANPD; Canada OPC; BAILII and CanLII for
  non-US AI litigation.
- **Research and disclosure (capabilities):**
  - arXiv cs.CR, filtered (CC0 metadata)
  - HackerOne hacktivity and Bugcrowd AI-program disclosures. Platform ToS
    needs the full WS0-T1 treatment before anything else.
  - DEF CON AI Village and Black Hat archives

## Deliberate rejections (record with reasons)

- **CNNVD / CNVD:** access and reuse terms are unclear.
- **Snyk / VulDB:** restrictive terms.
- **Any news aggregator or newsletter:** discovery feeders only. OECD AIM
  already supplies news-derived coverage, so a second aggregator adds dedupe
  load, not coverage.

## Dated watch items

- EU AI Act **Article 73** serious-incident register: its existence, access
  and reuse terms, and the expected date it opens.
- **EUVD API maturation**: stability, versioning, bulk export and terms.

## Decision owed to the user

One first-wave recommendation across both tranches. The user's prior is
CISA + huntr + EUVD for wave one, and the permissive-licence government-CERT
trio (NCSC/ACSC/CCCS) for wave two. **The measured evaluation rules over the
prior.**
