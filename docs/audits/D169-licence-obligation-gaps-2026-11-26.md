# D169 licence-obligation gaps F1, F2, F3, F5 (WS0 license-auditor)

DATED RECORD, 2026-11-26. DO NOT REGENERATE. Describes what was found on main
5720c248 (worktree branch `d169-licence-obligations`). Where later work changes
a finding, add a dated update; do not rewrite this text. The proposed texts in
section 5 are DRAFTS for the owners to apply to live surfaces, which are
corrected in place.

Method statement. No shell. Everything below rests on: Read and Grep of the
worktree (counts are Grep line counts over pretty-printed JSON, one marker per
row, so they are row counts only on that assumption); WebFetch of the SPDX
CVE-TOU page and of `mitre-atlas/atlas-data` (GitHub API JSON and raw LICENSE
text, both positive findings). Absence findings are labelled with their
method and routed to red-reviewer (section 7). Nothing was fetched from
hackingincidents.ai, AVID or HF this session; their rows are carried from
docs/SOURCE_LICENSES.md.

## 1. VERDICT

| Gap | Gate's premise | Verdict |
|---|---|---|
| F1 HF bundle ships no notice | HF out of compliance | **CONFIRMED, conservative reading.** A pointer "in the source repository" does not satisfy MIT's "included in all copies or substantial portions", the CVE ToU's "reproduce MITRE's copyright designation and this license in any such copy", or Apache-2.0 s4(a) "give ... a copy of this License". The same defect reaches the GitHub release assets, the site's data download and the STIX/TAXII/MISP trees. PyPI wheel is UNVERIFIED (no shell); sdist and Zenodo are compliant by construction. **New, larger than the gate saw:** the Apache-2.0 notice is also deficient everywhere (F6a below). |
| F2 81 ledger-reference rows lack a marker | A marker may be needed | **NOT NEEDED for compliance; do not add one.** The MIT condition is met by the dataset-level notice travelling with the copy (F1), not by a row field. A marker on those rows would also be wrong: `content_license` is a single object, set by the row's surviving description source, and would overwrite or conflict with a real obligation on rows that already carry one (AIAAIC, cve). |
| F3 NOTICE-DATA sentence contradicts the data | Narrow the sentence or extend markers | **NARROW THE SENTENCE NOW. The gate's AVID arithmetic is mostly a mislabel: only 109 AVID rows are truly unmarked.** The 125 "wave12_avid but no marker" rows carry `description_source = cve-cna-via-avid` and, by construction, the `cve` marker (CNA text, CVE ToU), which is the correct marker for them. 79 + 125 + 109 = 313. The CVE gap (about 5,300 rows built from NVD/GHSA/OSV, unmarked) is real, but the obligation there is the dataset-level notice, not a marker. Extending markers to them is optional, large, and needs a ruling (section 3). |
| F5 card summary names neither MIT exception | Add them | **CONFIRMED.** Proposed wording in section 5. Same defect in the card's `Licence:` line only; the Licensing section above it does name both MIT sources. |

[SUPERSEDED IN PART, see Update 2026-11-26 (after gate bounce #1), item B:
the paragraph below mis-sizes the unmarked CVE- rows as CNA text; most carry
GHSA CC BY 4.0 text.]
Premise checks. The gate's idea that CVE text might be public domain does not
hold: NVD's own analysis fields are US-government work, but the descriptions
are CNA-authored text that MITRE licenses under the CVE ToU, which is exactly
the instrument NOTICE-DATA already invokes ("including those obtained via
NVD"). The idea that HF might comply via another route does not hold: the
bundle is built by `scripts/export_huggingface.py` `build()` (L231-282), which
writes `incidents.jsonl`, `README.md`, `build_manifest.json` and `SHA256SUMS`
only, and `main()` pushes that folder with `upload_folder` (L308).

## 2. F1 distribution surfaces

Rule applied: UNKNOWN or unverified is recorded as NO. "Pointer" means a link
to the notice rather than the notice.

| Surface | What it ships (licensed material) | Notice shipped? | Compliant? |
|---|---|---|---|
| Git repository / GitHub source archive (zip/tar on the release page) | Everything, plus ingest snapshots | `NOTICE-DATA`, `LICENSE`, `LICENSE-DATA`, `.reuse/dep5` at root | [SUPERSEDED, Update item C] YES for CVE-ToU, MIT, CC-BY. Apache-2.0: notice present, full licence text absent (F6a). CORRECTED: NO for the GHSA CC BY 4.0 notice (absent from repo and NOTICE-DATA, F6b) and NO for the Apache-2.0 text |
| Hugging Face dataset (export_huggingface.py L231-282) | `incidents.jsonl`: full dump of `stands()` rows: CVE-ToU text, AVID MIT, hackingincidents.ai MIT, ATLAS and garak Apache-2.0 text, AIAAIC titles (BY-SA marker), GHSA/OSV (CC-BY) | Card only; card says `NOTICE-DATA` "in the source repository" (L168, L204-217). The card inlines names ("Copyright (c) 2025 Daniel Miessler") but not the MIT permission text or the CVE ToU text | **NO** |
| PyPI sdist | `data/incidents.min.json`, `src/.../incidents.min.json` | pyproject `[tool.hatch.build.targets.sdist] include` lists `LICENSE`, `LICENSE-DATA`, `NOTICE-DATA` (pyproject.toml L59-71) | YES for notices (Apache text: F6a) |
| PyPI wheel | `src/genai_incidents/data/incidents.min.json` | **UNVERIFIED.** pyproject sets no `license-files`; wheel `include` is `src/genai_incidents/**` (L43-46). Hatchling may add root `LICEN[CS]E*`/`NOTICE*` files to `dist-info/licenses` by default; I could not build a wheel. Also `license = "MIT"` and the MIT classifier describe the package as MIT while it carries CC-BY data | [REFUTED by gate-d169, Update item D: a scratch wheel and the published PyPI 2.13.0 wheel both ship dist-info/licenses/{LICENSE, LICENSE-DATA, NOTICE-DATA}] ~~NO until verified~~; CORRECTED: YES for notices, Apache-2.0 text still absent; the License-Expression MIT mislabel remains |
| GitHub release assets (package_release_assets.py ASSETS L35-40) | `incidents.min.json`, `incidents.stix.json`, `taxii2.zip`, `misp-feed.zip`, manifest, SUMS | None of the six assets is a notice; the notice is on the release's source archive only | **NO** for the assets taken alone |
| Website download `docs/data/incidents.min.json` plus core/shards (pages.yml L38-43) | Same rows | Footer links to the GitHub blob of NOTICE-DATA (index.html L92, L253); `docs/` holds no NOTICE-DATA or LICENSE-DATA (Glob, 2026-11-26) | **NO** (pointer only) |
| STIX bundle (`docs/data/incidents.stix.json`) and TAXII static tree | Row descriptions as SDOs; `x_content_license` on marked rows only (export_stix.py L299-304) | No notice object or file | **NO** |
| MISP feed | Structured tags and links; the schema text says MISP carries no description (schema `content_license` text) | None | NO until red-reviewer checks whether any CVE/AVID/ledger text (titles, links) is in the feed; low exposure |
| Zenodo record | GitHub-integration archive of the tagged source tree | Present if the archive includes the root files; `.zenodo.json` description cites NOTICE-DATA | YES by construction. UNVERIFIED: list the record's files via the Zenodo API |

Minimum fix, per surface class (owner and ruling in section 4):

- Ship the notice files, byte-identical to the repo root, in every served or
  uploaded copy: `NOTICE-DATA`, `LICENSE-DATA`, and (new) `LICENSES/Apache-2.0.txt`.
  For HF: copy them into `out_dir` inside `build()` before `write_manifest` and
  `write_sums`, so they are listed in `build_manifest.json`/`SHA256SUMS` and
  the byte-diff against root is checkable. For release assets: add them to
  `ASSETS`. For Pages: `cp` at the "Mirror data file" step and link the
  site's footer to the relative copy. For taxii2/misp: place one copy at the
  tree root so the existing `deterministic_zip` and `gen_data_integrity.py`
  pick it up. For STIX: ship beside the bundle; optionally also a `note` SDO
  pointing to it (not required).
- Rejected alternative: inlining notices in the card only. It satisfies HF
  readers but not the other surfaces, forks the text (two sources of truth),
  and the card already shows how that drifts (F5). A trimmed generated
  `NOTICE` is acceptable later, but a verbatim copy is the smallest change and
  the only one a byte-diff can gate.
- Previously published copies cannot be repaired in place for PyPI (wheels
  are immutable) or for the Zenodo versions already minted. HF head and the
  site can be fixed on the next push. Record a CORRECTIONS.md entry that
  releases up to and including v2.13.0 shipped HF, wheel (if confirmed) and
  release assets without the notices.

## 3. Per-gap findings

### F1 (see section 2)

Evidence: `scripts/export_huggingface.py` L168 ("`LICENSE-DATA` and
`NOTICE-DATA` in the source repository"), L204-205 (AVID "must likewise
accompany copies" while the bundle does not carry it), L224 (card says
`SHA256SUMS` and `build_manifest.json` ship beside the data, naming no notice
file). CVE ToU confirmed 2026-11-26 from SPDX `cve-tou.html` via WebFetch:
"Any copy you make for such purposes is authorized provided that you
reproduce MITRE's copyright designation and this license in any such copy."
(WebFetch markdown; this is a positive finding, so truncation does not
undermine it.) MIT text (AVID, ledger) in NOTICE-DATA L99-121, L137-159.

### F6a new: Apache-2.0 licence text is not distributed anywhere

Structured finding, GitHub API for `mitre-atlas/atlas-data`: `license`
= `{key: other, spdx_id: NOASSERTION}`, fetched 2026-11-26. Explanation from
the raw `LICENSE` (fetched 2026-11-26, markdown of plain text, 13 lines):
the upstream file is only the short header ("Copyright 2021-2026 MITRE /
Licensed under the Apache License, Version 2.0 ... You may obtain a copy of
the License at http://www.apache.org/licenses/LICENSE-2.0"), without the
full terms, which is why GitHub cannot classify it. Consequences:

1. The Apache-2.0 grant is real (the header is the standard grant notice) but
   SOURCE_LICENSES 3.1's phrase "confirmed via LICENSE file" should say it is
   the header form, and that GitHub reports NOASSERTION.
2. Apache-2.0 s4(a) requires giving recipients "a copy of this License".
   NOTICE-DATA L46-63 gives only a URL; `LICENSES/` holds no Apache-2.0.txt
   (Glob, 2026-11-26: only `CC-BY-SA-4.0.txt`, `LicenseRef-upstream-terms.txt`),
   though dep5 asserts `License: Apache-2.0` for `ingest/atlas/ATLAS-*.yaml`
   (REUSE lint will want the file). garak text is also Apache-2.0.
3. s4(b)/(c): modified ATLAS/garak text should carry a statement of change;
   the notice should say the case-study text is "reproduced verbatim" (it
   does) and the garak docstrings are "concatenated" (a change).

Fix: add `LICENSES/Apache-2.0.txt` (verbatim SPDX), ship it per section 2.
Not previously in the gate's list; found because the question asked what
ATLAS requires. Route to governance (file) and distribution-engineer.

### F6b new: NVD and GHSA/OSV notices

Absence findings, method: Grep over the worktree, tracked text files other
than `docs/audits/`, for the NVD sentence "endorsed or certified by the NVD":
only `docs/SOURCE_LICENSES.md` and `PROGRESS.md` match, so the notice that
SOURCE_LICENSES 2.2 (dated 2026-07-15) calls a "compliance gap" is still not
displayed in README, site or NOTICE-DATA. Grep of NOTICE-DATA for
`GHSA|GitHub Advisory|CC-BY 4.0|PyPI Advisory`: 0 matches, so the CC BY 4.0
licence notice for GitHub Advisory Database and PyPI/Go advisories (rows
built by `ghsa_to_record` and the OSV path) is not in the notice file; the
per-row `ghsa_id` and advisory URL cover creator identification and a link
(CC BY 4.0 s3(a)(1)) but not the licence notice. These are local-tree Grep
findings on text I could read, not web-page absences, but red-reviewer should
repeat them with `git grep` (section 7). Owner: governance to draft, user to
approve wording; pipeline-engineer not involved.

### F2: 81 rows with hackingincidents.ai references

Evidence. dep5 L112-120 covers "the ledger references attached to other rows"
and names the MIT notice in NOTICE-DATA. NOTICE-DATA L129-137 and L383-384
already state the other rows carry "references, facts and links, without
that marker". The HF card L199-200 says the same. The licence text
(NOTICE-DATA L149-150): the copyright and permission notice "shall be
included in all copies or substantial portions". What those 81 rows gained is
a ledger page URL, source URLs, publisher names and publisher headlines used
as link labels: URLs and publisher names are facts, headlines are the
publishers' (ledger says quotes and source text remain under publishers'
terms), and none of it is the operator's selection or arrangement in any
substantial portion. The obligation attaches to the dataset copy that carries
the ledger material, and is discharged by the notice shipping with it (F1).

Why a marker would be wrong, not merely unnecessary: the field is one object
(`incident.schema.json` L92-95: "Set at ingest, by whichever entry survives
dedup as the merge target", "never overwritten by a later merge"). A marker
`hackingincidents` on an existing row would either replace an AIAAIC or `cve`
marker (erasing a real obligation) or be dropped by the merge rule. I could
not count how many of the 81 already carry another marker (no shell); if any
do, that settles it. Recommendation: no marker; keep the dataset-level
notice; the references already point at the ledger URL, which is the
per-row attribution a reader needs.

### F3: NOTICE-DATA claim vs data

What I re-derived (Grep line counts of `"source": "<x>"` in
`data/incidents.json`, 2026-11-26): cve 2,171; avid 79; hackingincidents 186.
These match the gate's marker totals. Could NOT re-derive without a shell:
7,443 CVE- source-id rows, 2,150 marked, 313 AVID- rows, the 125 and 21.

What I could derive that changes the picture:

- `"description_source": "cve-cna-via-avid"` appears 125 times in
  `data/incidents.json` (Grep count). `scripts/ingest_avid.py` L303-307 sets,
  for CVE-class AVID records, BOTH `description_source: cve-cna-via-avid` AND
  `content_license: CVE_TOU_MARKER` on the same row, and merge_and_dedupe.py
  L1086-1104 copies both from the same raw row to the survivor. So the 125
  are expected to carry the `cve` marker. They are not "unmarked"; they are
  marked with the correct instrument. Cross-check: description_source values
  starting `cve` number 2,171, the same as the cve marker total.
- Arithmetic closes: 313 AVID- rows = 79 (avid marker) + 125 (cve marker via
  AVID) + 109 (curated `ingest/avid_owasp_incidents.json`, which has exactly
  109 `AVID-` source ids by Grep and no marker). And 21 = the 125 whose only
  source id is AVID- (125 - 104 also carrying a CVE- id): 2,150 + 21 = 2,171.
  This is consistent, not proven; per-row verification is in section 7.
  Beware (house rule 6d): a closing total proves nothing about the
  distribution inside it, so the per-row check is mandatory.
- Absorbed rows: `merge_into` (merge_and_dedupe.py L4198-4230) takes only
  taxonomy codes, tags, source_ids, cve_ids, cwe_ids, cvss_vector, aiid_id,
  references, severity and date from an absorbed duplicate; description, title
  and markers stay with the survivor. So an unmarked row that merely absorbed
  an AVID or cvelistV5 record gains an id and a URL, not AVID or CNA prose.
  A marker follows the surviving text, which is the schema's stated meaning.

AVID, truly unmarked: the 109 curated `AVID-` rows. SOURCE_LICENSES 6.1 says
(`Not compared`) whether they copy AVID text or are original paraphrase is
unverified. UNKNOWN is not resolved in the project's favour: treat them as
AVID-derived. MIT requires the notice with the text; a marker is how the
data says so row by row, and 109 rows is cheap to mark.

[SUPERSEDED IN PART, Update item B: the sizing and "CNA text" characterisation
in this paragraph are wrong for most rows; use the gate's per-row split.]
CVE, unmarked: the rest of the 7,443 (about 5,300, not re-derived) came in
through `scripts/ingest_cve_nvd_expanded.py` (NVD description verbatim,
`"description": descr.strip()` L600; GHSA node description L819-881; OSV
details L1043-1111), which sets no `content_license` (Grep of the script: no
match for `content_license`). Their text is CVE Program text (NVD path), or
GitHub Advisory/OSV-origin text (CC BY 4.0), so the obligation is real but
differs by origin. Notice, not marker, is what the licences require: the CVE
ToU says reproduce the designation and licence "in any such copy", and
nothing in it asks for a per-record field. Notably the existing `cve` marker
does not itself satisfy the ToU (it carries `license_url` and attribution,
not the licence text), so the marker was never the compliance mechanism, only
a convenience.

Recommendation F3:
1. NOW (no data change): narrow the sentence in NOTICE-DATA (L380-384),
   dep5 L67-69 and any copy. Text in section 5.
2. Mark the 109 curated AVID rows (conservative UNKNOWN reading) with
   `MIT_LICENSE_MARKER` (the same object as `scripts/ingest_avid.py` L86-93),
   by editing `ingest/avid_owasp_incidents.json` (an ingest input, not
   `data/*.json`; same route E16/D18 used for the 95 AIAAIC curated rows), and
   rebuilding. Rule for pipeline-engineer: add `content_license` to every
   row whose `source_id` starts `AVID-` in that file. Gate with the
   field-level delta: the only changed field on any entry is
   `content_license` (added); entries affected are those whose surviving
   record is one of those 109 (at most 109, fewer if some were absorbed into
   another survivor; report the exact number and the IDs); every other
   field of every entry and the entry/ID set unchanged; `incident_count`
   unchanged. Prove the check fires: delete one marker or add one to a
   non-AVID row and watch the delta fail. If a later text comparison (red-reviewer, vs
   `avidml/avid-db`) shows rows are original wording with no AVID expression,
   the marker can be withdrawn by a ruling; it never needs to be added
   speculatively again.
3. Do NOT extend the `cve` marker to the NVD/GHSA/OSV rows now. Reasons:
   not required by any of the licences; ~5,300 rows is a large delta that
   touches `updated` and every export; origin is mixed (CVE ToU vs CC BY
   4.0), so one `cve` marker would be wrong for GHSA/OSV-origin text; the
   one-object field cannot hold two obligations on a row that has both. If
   the user wants it anyway, the rule is: by ingest path, `nvd_to_record`
   rows get `CVE_TOU_MARKER`; `ghsa_to_record` and OSV rows need a new
   `ghsa`/`osv-origin` CC-BY marker, which needs a schema decision first
   (array vs single object). That is a separate ruling, not part of D169.

### F5: card summary line

Evidence: `scripts/export_huggingface.py` L227. Fix text in section 5. The
Licensing section (L165-217) already covers AIAAIC, OECD, ledger, AVID, OWASP.
It does not cover CVE ToU, ATLAS or garak at all (the card's only mention of
CVE is the source list, L154); add them in the same edit, since the summary
line must be true.

## 4. Recommendations

| # | Action | Owner | User ruling? |
|---|---|---|---|
| R1 | Ship `NOTICE-DATA`, `LICENSE-DATA`, `LICENSES/Apache-2.0.txt` byte-identical in the HF bundle, release assets, Pages tree, taxii2/misp trees, STIX download; list them in manifests/SUMS | distribution-engineer (HF build is pipeline code: pipeline-engineer for `export_huggingface.py`, `package_release_assets.py`; workflows: distribution-engineer) | Yes, light: confirms conservative reading as policy |
| R2 | Add `LICENSES/Apache-2.0.txt` (verbatim SPDX) and correct SOURCE_LICENSES 3.1 wording (header-only LICENSE, GitHub NOASSERTION) | governance (file, cell edit) | No |
| R3 | [AMENDED, Update item D: license-files and wheel contents are already fine] Fix only the License-Expression MIT mislabel on PyPI metadata | distribution-engineer | Yes: the expression choice is the user's (SPDX lists `cve-tou`, so a valid expression exists) |
| R4 | Narrow NOTICE-DATA and dep5 sentence (section 5.1) | governance | No |
| R5 | Mark the 109 curated AVID rows (rule in section 3 F3.2) | pipeline-engineer | Yes: data change on shipped rows (delta approval) |
| R6 | No marker for the 81 ledger-reference rows; no extension to NVD/GHSA/OSV rows now | governance (record in SOURCE_LICENSES) | Yes: confirm "no" on both |
| R7 | NOTICE-DATA additions: NVD API notice and GHSA/OSV CC BY 4.0 notice (section 5.2) | governance | Yes: wording is the user's call |
| R8 | Card edits: summary line and Licensing text (section 5.3); card also notes the bundle now ships the notices | pipeline-engineer (card is a string in `export_huggingface.py`) | No |
| R9 | [AMENDED, Update item D: name only HF, release assets, Pages and STIX/TAXII/MISP; NOT the wheel or Zenodo] CORRECTIONS.md entry for releases through v2.13.0 | governance | Yes: public admission is the user's call |
| R10 | Site: serve `docs/NOTICE-DATA` and link relatively from `index.html` footer L92/L253 | distribution-engineer | No |

Pipeline requirement (exact), for the foreman to route: in
`scripts/export_huggingface.py::build`, after the card is written and before
`ei.write_manifest(out_dir)`, copy `NOTICE-DATA`, `LICENSE-DATA` and
`LICENSES/Apache-2.0.txt` from the repo root into `out_dir` unchanged
(`shutil.copyfile`; fail the build if a source file is missing); add a test
that the built folder contains the three names, that each is byte-equal to
the root file, and that `SHA256SUMS` lists them; prove the test fires by
removing one copy line.

## 5. Draft text (for owners to apply to live surfaces)

### 5.1 NOTICE-DATA, replacement for L380-384 (and the same clause in dep5 L67-69)

[SUPERSEDED, Update item A: this draft states "shipped with every distribution"
(false until R1) and that the avid marker covers the curated AVID- rows (false
until R5). Do not apply as written; use the two variants in the Update.]

Current: "the obligation is attribution or a notice that accompanies copies
(CVE- and AVID-derived rows, and the HIAI- rows from the ledger, also carry a
row-level content_license marker; the other rows that cite the ledger carry
its references, facts and links, without that marker)."

Proposed: "the obligation is attribution or a notice that accompanies copies,
and that notice is this file, which is shipped with every distribution of the
dataset. Some rows also carry a row-level content_license marker as a
convenience: rows whose surviving text came from the CVE Program's records
through the cvelistV5 ingest or through AVID's CVE-class records (source
cve), rows whose text came from AVID's own records (source avid, including
the AVID- rows of ingest/avid_owasp_incidents.json), and the HIAI- rows from
the ledger (source hackingincidents). The marker is not the mechanism that
discharges the obligation and its absence does not mean a row is
unencumbered: rows that carry CVE Program text obtained through the NVD API,
or GitHub Advisory Database or OSV text (the CVE- and GHSA- rows built by
scripts/ingest_cve_nvd_expanded.py), and the other rows that cite the
ledger, carry no such marker; the notices in this file apply to them. Counts
are audited in docs/SOURCE_LICENSES.md, not restated here."

### 5.2 NOTICE-DATA, two new paragraphs (wording for user approval)

[AMENDED, Update item E: the PyPA and Go credits cover text the corpus does
not carry; "GitHub, Inc." is unconfirmed; the NVD "requires" framing is
overstated.]

NVD: "NVD data. Rows built from the NVD API use it under the NVD terms of
use, https://nvd.nist.gov/developers/terms-of-use. This product uses the NVD
API but is not endorsed or certified by the NVD." (The sentence in italics
in SOURCE_LICENSES 2.2 is the operative text; NVD also says modified content
must not be attributed to the NVD.)

GHSA/OSV: "GitHub Advisory Database and OSV. Advisory text in rows built from
the GitHub Advisory Database (ids GHSA-...), and from the PyPI Advisory
Database and the Go Vulnerability Database via OSV.dev, is licensed CC BY
4.0, https://creativecommons.org/licenses/by/4.0/ . Credit: GitHub, Inc.
(GitHub Advisory Database), the Python Packaging Authority (PyPI Advisory
Database) and the Go Project (Go Vulnerability Database). Changes: text is
truncated to 1,500 characters. Each row carries the advisory id and URL as
its source link. OpenSSF Malicious Packages records (Apache-2.0) are
excluded."  (Credit-holder names to be confirmed by governance from the
origin pages before this is applied; I have not fetched them this session.
The 1,500-character truncation is from `ingest_cve_nvd_expanded.py`
L881, L1111.)

### 5.3 Hugging Face card (scripts/export_huggingface.py)

Summary line L227, proposed: "**Licence:** data **CC-BY-4.0**, with
exceptions that travel with specific rows or files: AIAAIC-citing rows carry
a CC BY-SA 4.0 attribution/share-alike obligation (row-level
`content_license`); rows or text derived from the CVE Program (CVE Terms of
Use), AVID (MIT), the hackingincidents.ai ledger (MIT) and MITRE ATLAS and
garak (Apache-2.0) carry upstream copyright and permission notices,
reproduced in `NOTICE-DATA` in this repository; the OWASP mapping files
(CC BY-SA 4.0, not part of this dataset) are in the source repository. See
Licensing above. Code MIT."

Licensing section, replace L204-205 sentence on AVID and add before the
OWASP paragraph: "`NOTICE-DATA`, `LICENSE-DATA` and `LICENSES/Apache-2.0.txt`
ship in this repository beside `incidents.jsonl`; they carry the MITRE CVE
Terms of Use notice, the AVID MIT notice, the hackingincidents.ai MIT
notice, and the Apache-2.0 notices for MITRE ATLAS and garak text, which must
accompany any copy of the rows they cover. Row-level `content_license`
markers are a convenience, not the mechanism: rows carrying NVD, GitHub
Advisory Database or OSV text may carry none." (The card must keep saying
what the bundle ships: it lists `build_manifest.json` and `SHA256SUMS` at
L224; add the three files there.)

## 6. User decisions needed

1. Confirm the conservative policy that every distributed copy ships the
   notice files (R1) and approve the CORRECTIONS.md admission (R9).
2. Approve marking the 109 curated AVID rows, with a field-level delta (R5);
   or rule that the text comparison against avid-db comes first.
3. Confirm no marker for the 81 ledger-reference rows and no extension of
   the `cve` marker to NVD/GHSA/OSV rows (R6).
4. Approve the wording of the NVD and GHSA/OSV paragraphs (R7).

No outreach is needed for any of these; nothing was ambiguous at the source.

## 7. Checks for red-reviewer (shell required)

1. Per-row F3 closure. For `data/incidents.json`: let A = rows with an
   `AVID-` source id (expect 313). Report, for A, the counts by
   `content_license.source` (expect avid 79, cve 125, none 109) and confirm
   the 125 are exactly the rows with `description_source ==
   "cve-cna-via-avid"`. Confirm the 109 none-rows are exactly the
   `ingest/avid_owasp_incidents.json` ids. Also: of the 2,171 cve-marked
   rows, 21 lack any `CVE-` source id and all 21 are in the 125. The gate's
   and my numbers should agree per-row, not just in total.
2. Re-derive 7,443 and 2,150, and report the unmarked CVE- rows by ingest
   origin (NVD / GHSA / OSV / curated), by comparing each row's description
   with the `ingest/cve_nvd_expanded.json` row of the same source id.
3. F2: for the 81 ledger-attached rows (ids in
   `ingest/wave13_hackingincidents.attach.json`), count how many already have
   a `content_license`, by `source`. Any non-zero count confirms the
   one-object conflict.
4. PyPI wheel: `python -m build --wheel`; `unzip -l dist/*.whl`; report
   whether `*.dist-info/licenses/` contains LICENSE, LICENSE-DATA,
   NOTICE-DATA. Also run it for the sdist. Prove the check can fail by
   listing a wheel built with `license-files = []`.
5. HF bundle: after R1, run `python scripts/export_huggingface.py` and
   `cmp` each shipped notice file to the root file; confirm `SHA256SUMS`
   lists them.
6. Absence findings in F6b, repeated with `git grep -n "endorsed or
   certified by the NVD"` and `git grep -n -i "GitHub Advisory" NOTICE-DATA`
   over the worktree (raw tracked text, not a rendered view).
7. Apache text: after R2, `diff LICENSES/Apache-2.0.txt` against the SPDX
   `Apache-2.0` text from the REUSE tool or the licenses repo; run
   `reuse lint` and report whether `Apache-2.0` is now resolved.
8. Zenodo (structured): `curl https://zenodo.org/api/records/<id>` and list
   `files`; report whether the latest record's archive contains the root
   notice files (inspect the archive's file list).
9. Raw upstream LICENSE re-check, since this session's reading of the ATLAS
   file went through WebFetch: `curl -s
   https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/LICENSE |
   wc -l` (expect 13) and `grep -c "TERMS AND CONDITIONS"` (expect 0).

## 8. Update 2026-11-26 (after gate bounce #1)

Added after gate-d169 bounced the record on e506d4e0. The original text above
is kept; superseded passages are marked inline. DO NOT REGENERATE. Figures
attributed to the gate below were measured by the gate per row against the
ingest files (exact description match); I did not and could not re-derive them
(no shell). The gate confirmed row by row: F1 (HF, release assets, Pages,
STIX/TAXII/MISP ship no notice), F2 (6 of the 81 rows already carry an
`aiaaic` marker, so the overwrite risk is real), the F3 arithmetic
313 = 79 + 125 + 109, ATLAS NOASSERTION, the NVD notice gap and F5.

### A. NOTICE-DATA sentence: two variants, each with its precondition

Replaces section 5.1, which contradicted my own F3 recommendation 1 ("NOW, no
data change") by asserting two things not yet true.

Variant A1, apply NOW. Precondition: none; true on main today. It claims
neither that the notice ships with every copy (false until R1) nor that the
curated AVID- rows are marked (false until R5):

"the obligation is attribution or a notice that accompanies copies. Some rows
also carry a row-level content_license marker as a convenience: rows whose
surviving text came from the CVE Program's records through the cvelistV5
ingest or through AVID's CVE-class records (source cve), rows whose text came
from AVID's records through the AVID ingest (source avid), and the HIAI- rows
from the ledger (source hackingincidents). The marker is not the mechanism
that discharges the obligation, and its absence does not mean a row is
unencumbered. These rows carry no marker: rows built by
scripts/ingest_cve_nvd_expanded.py from the NVD API, the GitHub Advisory
Database or OSV; the AVID- rows of ingest/avid_owasp_incidents.json; and the
other rows that cite the ledger. The upstream licence of the origin applies to
them, and the notice duty is met only for copies that carry the notices in
this file. Counts are audited in docs/SOURCE_LICENSES.md, not restated here."

Variant A2, apply only after ALL of: R1 has landed and shipped (notice files
in every distribution), R5 has landed (109 curated AVID rows marked), and the
GHSA paragraph of 5.2 is in NOTICE-DATA. Then replace the A1 clauses so: the
notice "is this file, which is shipped with every distribution of the
dataset" (this statement is checkable by R1's byte-equality test); the avid
marker list adds "including the AVID- rows of
ingest/avid_owasp_incidents.json"; the unmarked list drops that file and names
GHSA CC BY 4.0 text as covered by the GitHub Advisory Database paragraph. The
dep5 clause (L67-69) takes the same variant at the same time. Separately and
independent of either variant: dep5 L57-72 says "eleven sources" and "seven of
the other eight", omits the ledger, while NOTICE-DATA says twelve and "eight
of the other nine". Governance should reconcile dep5 to NOTICE-DATA in the same
edit (gate advisory).

The HF-card text in 5.3 that says the three notice files "ship in this
repository" is likewise a post-R1 variant: apply it only with R1.

### B. The unmarked CVE- rows: corrected sizing (supersedes the premise
paragraph after section 1 and the "CVE, unmarked" paragraph of F3)

I called the roughly 5,300 unmarked rows "CNA-authored text ... the instrument
NOTICE-DATA already invokes". That mis-sized them in the project's favour.
The gate's per-row match, by exact description against the ingest files, splits
the 5,293 unmarked `CVE-` source-id rows:

| Origin of the surviving description | Rows | Licence |
|---|---|---|
| NVD (CVE Program) text | 1,903 | CVE Terms of Use (notice-bearing) |
| GHSA advisory text | **3,315** | **CC BY 4.0** (GitHub Advisory Database) |
| `cve_incidents` curated | 43 | unassessed here |
| no match | 31 | unknown, treat as encumbered |
| OWASP | 1 | CC BY-SA 4.0 round-up question (SOURCE_LICENSES 1.6) |

A further 579 GHSA-text rows have no `CVE-` id (828 `GHSA-` id rows, all
unmarked). Total: about 3,894 rows carry GHSA CC BY 4.0 text with no notice
anywhere in the repo or its distributions. By row count that is the largest
uncured obligation in this audit, not a side note: F6b is therefore a main
finding, not an addendum. NVD text is the smaller group (1,903). GitHub is
also a CNA, so a GHSA-text row that is also a CVE may carry both CC BY 4.0
and the CVE Terms of Use.

What stands from my analysis: the licences require a notice with the copy,
not a per-row field, and the existing `cve` marker does not itself reproduce
the licence. What changes: the argument "extension is optional" is weaker, for
three reasons: (1) most unmarked rows are CC BY 4.0 text, which needs a
licence notice and creator credit the corpus does not currently ship at all;
(2) one `cve` marker would be wrong for them; (3) the one-object field cannot
hold both obligations on a GitHub-CNA row.

Decision 3 (R6) is therefore re-presented to the user with this split, not as
a yes/no on "no markers":
- 3a. 81 ledger-reference rows: no marker (6 already carry `aiaaic`; a
  ledger marker would overwrite or conflict). Unchanged.
- 3b. NVD/CVE-ToU-text rows (1,903): marker not required; notice shipping
  (R1) discharges it. Marking is optional and big.
- 3c. GHSA CC BY 4.0 rows (about 3,894): the notice must exist first (5.2),
  in NOTICE-DATA and in every distribution. Whether to add a per-row marker
  needs a schema ruling (single object versus array; a new `ghsa` source;
  GitHub-CNA rows with two obligations). My recommendation: notice now, marker
  only after that schema ruling.
- 3d. 43 + 31 + 1 rows: owner pipeline-engineer to identify, then treat as
  encumbered until assessed.

### C. Surface table, "Git repository" row

Corrected inline: NO for the GHSA CC BY 4.0 notice (absent from the repo and
from NOTICE-DATA) and NO for the Apache-2.0 text. My earlier "YES for CC-BY"
contradicted my own F6b.

### D. Wheel and Zenodo: my wheel finding is REFUTED

The gate built a scratch wheel and inspected the PUBLISHED PyPI 2.13.0 wheel:
both ship `dist-info/licenses/{LICENSE, LICENSE-DATA, NOTICE-DATA}`, and the
published NOTICE-DATA is byte-identical to v2.13.0's (sha256 prefix
2d188ac23da54736). Zenodo record 23328791 also carries NOTICE-DATA. My
"UNVERIFIED, so NO" was the conservative default, and it was wrong; I flagged
it as unverified, but the surface table should not have asserted NO. Effects:
the wheel row is YES for notices (Apache-2.0 text still absent); R3 shrinks to
the `License-Expression: MIT` mislabel only (SPDX lists `cve-tou`, so a valid
expression exists; the choice is the user's); R9's CORRECTIONS entry names
only HF, the release assets, Pages and STIX/TAXII/MISP, not the wheel or
Zenodo. The Zenodo row's "YES by construction, unverified" is now verified by
the gate.

### E. Advisories folded in

- Section 5.2 credits. The OSV path contributes 0 surviving descriptions today
  (304 osv-tagged rows, all carrying NVD or GHSA text, per the gate), so the
  PyPA and Go Project credits would cover text we do not carry: drop them, or
  make them conditional on an OSV-origin description existing. "GitHub, Inc."
  as the credit holder is my inference and is UNCONFIRMED: GHSA's LICENSE.md
  is the bare CC BY 4.0 legal code and its README says only "licensed under the
  terms of the CC-BY 4.0 open source license" (a quote I carried in
  SOURCE_LICENSES 2.3 and did not re-read here). Governance must confirm
  the creator wording from the origin pages before applying.
- NVD. NVD asks for the notice; it is not a licence condition. SOURCE_LICENSES
  2.2 says the terms "require" a displayed notice, which overstates it. That
  is my own 2026-07-15 wording and should be corrected in place on that live
  row. NVD's FAQ uses the variant "uses data from the NVD API". NVD also says
  that if you modify the content you "may not attribute the source as the
  NVD", which is in tension with the 1,500-character truncation at
  `ingest_cve_nvd_expanded.py` L881 and L1111: a truncated description should
  not be presented as NVD's text. This goes to the user as part of R7
  (decision 4): (i) notice or no notice, (ii) which variant, (iii) whether
  truncated NVD-origin descriptions need a "modified" statement.
- R2. `reuse lint` reports Apache-2.0, CC-BY-4.0 and MIT all missing from
  `LICENSES/`, not only Apache-2.0. R2 becomes: add all three verbatim SPDX
  texts. (This also supplies the CC BY 4.0 full text next to the copy in
  LICENSE-DATA, which is already at the root.)
- MISP. The gate reports `export_misp.py` L181-183 exports titles, including
  GHSA summaries and AIAAIC titles. My "NO until red-reviewer checks, low
  exposure" is replaced by a definite NO, and my "MISP carries no description"
  inference from the schema text was too loose (no description, but titles).

### F. Revised decisions for the user

1. Policy: notice files ship in every copy (R1); CORRECTIONS entry naming only
   HF, release assets, Pages and STIX/TAXII/MISP (R9).
2. Mark the 109 curated AVID rows, or compare against avid-db first (R5).
3. Re-presented per B: 3a no marker (81 ledger rows); 3b NVD rows notice only
   or mark; 3c GHSA CC BY 4.0 rows: notice now, schema ruling before any marker;
   3d 75 rows to identify.
4. R7 as in E: NVD wording and the modification question, GHSA creator
   wording, drop the unsupported OSV credits.
5. R3: which SPDX expression for the PyPI metadata.

No outreach is needed.
