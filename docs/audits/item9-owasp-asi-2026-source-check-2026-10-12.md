# v2.13.0 item 9 - OWASP ASI 2026 edition: primary-source record (STEP 1)

Date: 2026-10-12. Author: license-auditor (WS0). Dated record: do not regenerate; supersede with a dated update.

## Method and its limits (read first)

Retrieval was by WebFetch (HTML converted to markdown, then summarised by a small model) and WebSearch. I have no shell. Consequences:

- Every "quote" below is the fetch tool's rendering of the page, NOT raw bytes. Names and clauses are reported as the tool returned them. Treat each as **method-suspect** until red-reviewer confirms against raw HTML/PDF text (checks listed at the end).
- The official PDF (https://genai.owasp.org/download/52117/?tmstv=1765059207, 1.2 MB, application/pdf) was fetched but arrived as compressed binary and could not be read. Nothing below comes from the PDF. The descriptions, any in-PDF version label and any in-PDF licence/copyright page are **UNVERIFIED**.
- The landing page returned no ASI01-ASI10 list; names come from OWASP's launch blog post and an OWASP GitHub play file. Descriptions: not retrieved from any primary source. No comparison to our description strings is possible beyond what is stated in section 4.

## 1. The official publication

| Item | Finding | Source / access (2026-10-12) |
|---|---|---|
| Title | "OWASP Top 10 for Agentic Applications for 2026" | Landing page https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (fetched OK). Launch post title: "OWASP Top 10 for Agentic Applications - The Benchmark for Agentic Security in the Age of Autonomous AI". |
| Publisher | OWASP GenAI Security Project (site is genai.owasp.org; search result titles read "OWASP Gen AI Security Project") | Landing page and launch post (fetched OK). |
| Publication date | December 9, 2025 | Landing page states "December 9, 2025"; launch post URL path is /2025/12/09/ and the post "is dated December 9, 2025" (both fetch-rendered). Agree. |
| Version label | **None stated by OWASP in what I could read.** "2026" is the edition label in the title. The landing page cover filename contains "12.6" (OWASP-Top-10-for-Agentic-Applications-2026-12.6-Cover.jpg), unexplained and not evidence of a version. "v1.0" is NOT attested. | Landing page; launch post "does not give a version number". PDF in-document label UNVERIFIED. |
| Canonical URLs | Landing: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ . Download (PDF by content-type): https://genai.owasp.org/download/52117/?tmstv=1765059207 . Launch post: https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ . Initiative page lists it: https://genai.owasp.org/initiatives/agentic-security-initiative/ | All fetched OK 2026-10-12. The download URL carries a timestamp query (`tmstv`) and may rotate; the landing page is the stable citation. |
| GitHub repo | https://github.com/OWASP/www-project-top-10-for-agentic-applications returned HTTP 404 (a guessed name; not evidence no repo exists). Not located. | UNVERIFIED |

Sources agree on title, publisher and date. No disagreement found. "Published Dec 2025, titled 2026" is OWASP's own convention: **cite as "OWASP Top 10 for Agentic Applications for 2026 (published 2025-12-09)".** Do not write "v1.0" or "2025" as the edition.

## 2. Codes and names vs our mapping file

Official names as rendered from the launch post (https://genai.owasp.org/2025/12/09/...) and independently from OWASP's own play file https://github.com/OWASP/secure-agent-playbook/blob/main/plugins/ai-security-skills/plays/agentic-ai-risk-assess.md (which cites "OWASP Top 10 for Agentic Applications 2026"). The two renderings agree on all ten.

| Code | Our current name (mappings/owasp_asi_top10.json) | Official 2026 name (fetch-rendered) | Status |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | Agent Goal Hijack | identical |
| ASI02 | Tool Misuse & Exploitation | Tool Misuse | **renamed** (old -> new), suspect: see note |
| ASI03 | Identity & Privilege Abuse | Identity & Privilege Abuse | identical |
| ASI04 | Agentic Supply Chain Vulnerabilities | Agentic Supply Chain Vulnerabilities (play-file risk matrix shortens to "Agentic Supply Chain") | identical |
| ASI05 | Unexpected Code Execution (RCE) | Unexpected Code Execution | **renamed**: our "(RCE)" suffix not in official name |
| ASI06 | Memory & Context Poisoning | Memory & Context Poisoning | identical |
| ASI07 | Insecure Inter-Agent Communication | Insecure Inter-Agent Communication | identical |
| ASI08 | Cascading Failures | Cascading Failures | identical |
| ASI09 | Human-Agent Trust Exploitation | Human-Agent Trust Exploitation | identical |
| ASI10 | Rogue Agents | Rogue Agents | identical |

Counts (fetch-rendered): 8 identical, 2 renamed (ASI02, ASI05), 0 different risk.

**Code set: unchanged (ASI01-ASI10). Order: unchanged.** Every code keeps the same risk subject by name. Verdict: **item 9 is a metadata relabel (version, url, possibly two display names, description review), not a per-entry data re-mapping**, on the evidence retrieved. The one caveat is that I could not read the PDF, so "same risk meaning" rests on names only.

Note on ASI02: the blog-post rendering gives "Tool Misuse" with no "& Exploitation". I recall the PDF heading possibly being longer, but that is memory and is **UNVERIFIED**. The summariser may also have dropped words. This row must be settled by raw-text check before the implementer renames it. Same for the ASI05 suffix. If the PDF heading differs from the blog name, record both and use the PDF heading (the normative document).

## 3. Relationship to the 2025 Threats and Mitigations document

Fetch-rendered from the launch post: the Threats and Mitigations taxonomy is "the first of its kind, released in February 2025"; the Top 10 entries were "designed explicitly to respond to these risks"; the release comes with "a minor update on our Threat and Mitigations 1.1 taxonomy synchronised with our Top 10."

Reading: **derives from and sits alongside; does not supersede.** T&M (v1.1 after the sync) remains a separate, longer taxonomy (T-codes). The ASI01-ASI10 codes belong to the Top 10, not to T&M. Our file's `url` points to the T&M doc, which is the wrong artifact for ASI codes. It is a mis-citation, not merely stale. (Our "2025" version is likewise unattested for ASI: the ASI list was first published 2025-12-09 as the "2026" edition.) Whether T&M itself carries ASI-numbered entries was not checked.

## 4. Licence

- Operative clause, landing page and site footer (fetch-rendered, 2026-10-12, via https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ and https://genai.owasp.org/llm-top-10/): "Unless otherwise specified, all content on the site is Creative Commons Attribution-ShareAlike v4.0 and provided without warranty of service or accuracy." Disclaimer link: https://owasp.org/www-policy/operational/general-disclaimer.html (not read).
- Source kind: rendered HTML footer. Not a structured endpoint. "Unless otherwise specified" means the PDF could carry a different licence page: UNVERIFIED. Per standing rule, an in-PDF clause I could not read must not be recorded as absent.
- Our descriptions vs official: I could not retrieve the official description text (landing page has none; PDF unreadable). Our strings read like paraphrase/summary with our own enumerations (e.g. "agent card poisoning, replay, impersonation, and broadcast amplification"; "(e.g., autonomous offensive agents)"), and the file predates the Top 10 (cites T&M). Whether any are near-verbatim from T&M or the Top 10 is **UNKNOWN**. Do not assert either way.
- Repo coverage (Grep 2026-10-12): `NOTICE-DATA` has **no** OWASP match. `docs/SOURCE_LICENSES.md` mentions OWASP only on line 386, the AVID row, which expressly says the 21 `OWASP-GENAI-*` rows in `ingest/avid_owasp_incidents.json` have "no row in this document" and stay OPEN. There is **no row for the OWASP GenAI Security Project / ASI taxonomy**. (Grep limited to those two files; `.reuse/dep5` and TAXONOMIES.md not checked.)
- Obligations if text is reused (CC BY-SA 4.0): attribution (creator, title, licence link, indication of changes) and ShareAlike for adapted material. Names/codes alone (short titles of risks) are likely not copyrightable subject matter, but that is a legal judgement for the user, not mine. Conservative recommendation:
  1. Keep ASI codes and official names (identifiers, cited as such).
  2. Write `description` strings as our own short paraphrase, not copied from OWASP; do not import OWASP prose. If any official sentence is quoted, mark it as a quote with attribution.
  3. Add to `mappings/owasp_asi_top10.json` a `source`/`license` note: "Risk names (c) OWASP GenAI Security Project, CC BY-SA 4.0, https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/; descriptions are project paraphrase".
  4. Add a SOURCE_LICENSES.md row (OWASP GenAI Security Project - Top 10 for Agentic Applications 2026): license CC BY-SA 4.0 (site footer; PDF-level terms UNVERIFIED), scrape n/a (names only), redistribute-verbatim: attribution required, relicense-compatible: **NO for any verbatim/near-verbatim prose** (SA conflicts with the repo CC-BY data licence; the same issue as AIAAIC), YES for names/codes only if the user rules them non-copyrightable identifiers; date-checked 2026-10-12. This row is for the foreman/WS0 to write; I do not edit other files here.
  5. Add an OWASP attribution line to NOTICE-DATA.
  6. The 21 `OWASP-GENAI-*` incident rows remain a separate open item (different upstream: the exploit round-up). Not resolved by this record.

## 5. Implications for the implementation brief

Fields in `mappings/owasp_asi_top10.json` that change:
- `version`: "2025" -> "2026" (edition label per title; add note "published 2025-12-09").
- `url`: -> https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (and optionally a `related` key for the T&M URL).
- `entries.ASI02.name` and `entries.ASI05.name`: change only after the raw-text check in section 7 settles the exact official strings.
- `entries.*.description`: no required change from this record (paraphrase is the safe position); review only if the user wants descriptions aligned to the official text, which would trigger the share-alike analysis above.
- `framework`: see open question 1.

Per-entry data: **no change on this evidence** (codes and order unchanged). Per-entry `owasp_asi` and TAXII `x_owasp_asi` hold codes; renames do not touch them. If the ASI02/ASI05 rename lands, name-bearing exports (STIX/MISP/HF, stats.json taxonomy_versions, `taxonomy_versions.json`, the ~30 prose mentions) change by string only. Apply the field-level delta rule: expected deltas are version, url, two names; anything else is a defect.

Premise correction to the brief: item 9 as framed ("2026 edition") is largely a version/URL correction. The brief's "code-set change would touch per-entry data" scenario is not indicated.

## 6. Open questions for the user

1. Framework display name: keep "OWASP Agentic Top 10 (ASI)" or adopt the official "OWASP Top 10 for Agentic Applications for 2026"? (Affects the ~30 prose mentions and exports.)
2. Is "(c) OWASP, CC BY-SA 4.0" attribution on names/codes sufficient, or do you rule risk names as non-copyrightable identifiers needing only a citation? (Legal call, yours.)
3. Version string: "2026" (OWASP's label, recommended) versus "2025-12" (publication date). 

## 7. Checks for red-reviewer (shell, raw bytes)

1. `curl -sL https://genai.owasp.org/download/52117/?tmstv=1765059207 -o asi.pdf; pdftotext -layout asi.pdf asi.txt` then `grep -nE "ASI0[1-9]|ASI10" asi.txt`. Confirm the exact heading strings for ASI02 ("Tool Misuse" vs longer) and ASI05 ("(RCE)" suffix or not). Also `grep -niE "creative commons|licen[cs]e|copyright|version|v1\.|1\.0" asi.txt` for the in-PDF licence and version label. If the `tmstv` URL fails, take the PDF link from the landing page's raw HTML (`curl -sL <landing> | grep -oE 'https://genai.owasp.org/download/[^"]+'`).
2. `curl -sL <launch post URL> | grep -oE "ASI(0[1-9]|10)[^<]{0,60}"` to check names in raw HTML (tag splits possible; also try `sed 's/<[^>]*>//g'` first).
3. `curl -sL <landing page> | sed 's/<[^>]*>//g' | grep -niE "ShareAlike|Creative Commons|December 9"` for the footer licence and date.
4. Compare official ASI descriptions against our `description` strings (e.g. 5-gram overlap) to settle the near-verbatim question left UNKNOWN in section 4.
5. `git ls-remote`-style check for an official GitHub repo (`gh search repos "top 10 agentic applications" --owner OWASP`).
