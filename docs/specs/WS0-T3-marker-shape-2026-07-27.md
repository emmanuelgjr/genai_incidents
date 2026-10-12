# WS0-T3 — D11(b) row-level marker: schema shape

**Date:** 2026-07-27
**Author:** schema-architect (sole writer of `schema/`)
**Implements:** `docs/specs/WS0-T3-rescoped-2026-07-18.md` §6.1(i)/(ii); PROGRESS.md
decisions D9, D11, D12.
**Status:** shape decided; schema landed. Propagation, notice prose, and the
STIX/MISP CI assertion belong to pipeline-engineer (§4 of the rescoped spec) —
see §4 below for the exact handoff list.

> **Escalation raised by this task — see §4.5.** The rescoped spec's §6.1(ii)
> states it verified that the STIX exporter does not read `description`. It
> does: `export_stix.py:116` emits the full `description` for every entry, with
> no row filter. D12(b)'s "STIX/MISP carry no license-obligated row content"
> premise is therefore true for MISP and **false for STIX**, and the CI
> assertion D12(b) calls for would fail once the rebuild lands. Needs a
> licensing call before pipeline-engineer implements it. The schema shape below
> is unaffected either way.

---

## 1. The chosen shape

A dedicated, optional, **source-generic object field** on the incident record:

```
content_license: {
  source          (required)  slug of the source imposing the obligation
  license         (required)  SPDX identifier
  license_url     (optional)  canonical deed/legal-code URL
  attribution     (required)  human-readable party to credit
  attribution_url (optional)  URL to credit alongside it
  obligations     (required)  non-empty subset of ["attribution", "share-alike"]
}
```

`additionalProperties: false` on the object, matching the schema's existing
house style for structured fields (`references`, `maestro_layers`).

Plus a top-level conditional that makes §6.2's first acceptance criterion
**schema-enforced** rather than only jq-checked:

```json
"allOf": [
  {
    "if": {
      "required": ["description_source"],
      "properties": { "description_source": { "const": "aiaaic" } }
    },
    "then": { "required": ["content_license"] }
  }
]
```

## 2. Rationale

**Why a field and not a tag.** `tags` is the wrong carrier on three independent
counts, each verifiable in code today. It **unions across merges** rather than
staying sticky (`merge_into`, `merge_and_dedupe.py:1636-1691`), so a tag would
spread from an AIAAIC row to every entry that absorbed it — the exact opposite
of row-level containment. It is **truncated to the first 8 entries** in the slim
projection (`merge_and_dedupe.py`'s `slim` dict: `(e.get("tags") or [])[:8]`), so
the marker could be silently dropped from the most-redistributed artifact
precisely when a row is tag-rich. And a bare tag string cannot carry a machine-
readable license identity *and* an attribution target *and* the obligation set;
flattening those into one token invents a micro-format the schema cannot check.

**Why an object and not a bare string.** CC BY-SA 4.0 §3(a) requires the
attribution target and a link to the license, not merely the license's name. A
consumer holding only `data/incidents.min.json` — which after D12(a) is a
carrier of this marker, and which is also what ships inside the pip package via
`render_markdown.py:755` — may have no other license surface in hand. The object
makes that row self-sufficient.

**Why `obligations` is explicit rather than derived from `license`.** The
rescoped spec §6.4 records a concrete, near-term possibility: an AIAAIC reply, or
a waiver, could downgrade this from a ShareAlike-implying notice to an
attribution-only one. With obligations stated explicitly, that downgrade is a
**value** change (drop `"share-alike"`) on the existing shape. If obligations
were inferred from the SPDX identifier there would be no honest way to express
"CC-BY-SA-4.0 content, share-alike waived by the licensor" — no SPDX identifier
means that — and the downgrade would force a shape change instead.

**Why the field name carries no source.** §6.1(i) requires source-generic naming:
the source lives in the `source` **value**, so a future source with row-level
obligations reuses the mechanism unchanged. The *conditional* in §1 is
deliberately AIAAIC-keyed, because the obligation itself is source-specific
today; its `$comment` instructs the next editor to extend it per source rather
than delete it, mirroring §6.2's "re-scoped per-source, not dropped."

**Why `source` duplicates information also in `description_source`.** It does not
duplicate it where it matters. `description_source` is not carried in
`incidents.min.json` at all, so a min.json consumer would otherwise see an
obligation with no machine-readable statement of whose it is. It also gives
assertions a stable slug to key on instead of the display prose in
`attribution`.

## 3. Example of a marked row

Full record (`data/incidents.json`, and the HuggingFace export, which is a flat
projection of it):

```json
{
  "id": "INC-0XXXX",
  "title": "…",
  "description": "AIAAIC-tracked incident. System: … Technology: … Sector: … Jurisdiction: …",
  "description_provenance": "original",
  "description_source": "aiaaic",
  "content_license": {
    "source": "aiaaic",
    "license": "CC-BY-SA-4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution": "AIAAIC Repository",
    "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
    "obligations": ["attribution", "share-alike"]
  },
  "…": "…"
}
```

Slim projection (`data/incidents.min.json`) — the marker is the **only** added
key, present on marked rows and **absent** on every other row; the object is
carried whole, not re-shaped, so there is exactly one marker format across
surfaces:

```json
{
  "id": "INC-0XXXX",
  "title": "…",
  "description": "AIAAIC-tracked incident. System: …",
  "…": "…",
  "content_license": {
    "source": "aiaaic",
    "license": "CC-BY-SA-4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution": "AIAAIC Repository",
    "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
    "obligations": ["attribution", "share-alike"]
  }
}
```

The literal `attribution` / `attribution_url` / `license_url` values above are
the shape's expectation, not a licensing ruling; pipeline-engineer should
confirm the attribution string and repository URL against the live AIAAIC
footer at implementation time, and license-auditor owns any change to what the
obligation set should say.

## 4. Handoff to pipeline-engineer

1. **Ingest set-point.** Set `content_license` at the same place and time as
   `description_source == "aiaaic"` in `ingest_aiaaic_sheet.py` — one code path,
   so the two can never disagree. The schema conditional now fails the build if
   they do.
2. **`merge_into` exclusion — the mechanism is omission, not an exclusion list.**
   Verified 2026-07-27: `description_provenance` and `description_source` appear
   **nowhere in `scripts/`** (`grep -rn "description_source\|description_provenance"
   --include=*.py` returns nothing); they are schema-only fields today. So
   "excluded from `merge_into`" does not name any deny-list — `merge_into`
   (`merge_and_dedupe.py:1636-1692`) is a **allow-list** that touches only the
   keys it explicitly names: the union list (`owasp_llm`, `owasp_asi`,
   `owasp_dsgai`, `nist_ai_rmf`, `mitre_atlas`, `mitre_atlas_tactics`, `tags`,
   `source_ids`, `cve_ids`, `cwe_ids`, `mitigations`), the fill-if-empty list
   (`cvss_vector`, `aiid_id`, `disclosure_date`, `impact`), plus `references`,
   `severity`, and `date`/`year`. It mutates `target` in place, so every
   unnamed field — `description` included — keeps the merge target's own value
   automatically.
   **The requirement on pipeline-engineer is therefore purely negative: do not
   add `content_license` to any of those lists.** Stickiness is the default and
   needs no code; writing code is the only way to break it.
   Separately, and easy to conflate: `_CONTENT_FIELDS`
   (`merge_and_dedupe.py:1006`) is **not** the merge list — it is the snapshot
   that decides when `updated` bumps (invariant 4). Recommendation: **leave
   `content_license` out of it.** Including it changes nothing in this build
   (`description` is already in that tuple, so every marked row's `updated`
   bumps from the D9 rewrite anyway), but it would later make a pure licensing
   correction — an AIAAIC waiver downgrading `obligations`, per §6.4 — present
   itself as a change to the incident's content. pipeline-engineer/foreman own
   the final call; this is the shape owner's reasoning, not a ruling.
   **Update 2026-10-12 (user ruling D81, which knowingly reverses this
   recommendation and the WS0-T3 link-1 gate ruling of 2026-07-27):**
   `content_license` IS now in `_CONTENT_FIELDS`, together with `tier`,
   `quality_tier` and `corpus`, because the field is exported (min.json, STIX,
   HF) and a consumer keyed on `updated`/STIX `modified` would otherwise miss a
   licence relabel. The paragraph above is preserved as the record of the
   2026-07-27 reasoning. **Do not regenerate it as current guidance.**
3. **min.json conditional carry (D12(a)).** In the `slim` dict
   (`merge_and_dedupe.py:1590-1613`), add the key **only when present** on the
   source entry — not `e.get("content_license")`, which would emit `null` on
   every unmarked row and defeat "slim otherwise". min.json has **no schema and
   no validator** (`schema/` holds only `incident.schema.json`; the slim shape
   is code-only), so this requirement is the only specification of it — hence
   its being written here. Note that the same bytes are copied into the pip
   package and the site (`render_markdown.py:751-755`), so this reaches the
   package automatically.
4. **HuggingFace export.** No code change needed — `export_huggingface.py:11-13`
   is a flat projection of the full record. The dataset-card prose is separate
   and is requirement §6.1(iii).
5. **STIX/MISP (D12(b)) — the spec's premise for STIX is factually wrong; read
   this before implementing.** D12(b) rules that STIX/MISP carry no marker,
   resting on rescoped-spec §6.1(ii)'s claim that it "**verified neither
   currently reads `description`, `description_source`, or
   `description_provenance`**". That claim holds for MISP and **fails for
   STIX**:

   - **MISP — confirmed marker-free.** `_incident_attributes`
     (`export_misp.py:111`) emits only CVE / reference-URL / title attributes.
     No description reaches the feed. D12(b) is sound here.
   - **STIX — already carries `description` verbatim.** `export_stix.py:116`
     sets the incident SDO's `"description": i.get("description") or ""`, and
     the exporter applies **no filter at all** (`incidents = raw.get("incidents", [])`,
     `export_stix.py:161`) — every entry in the corpus becomes an SDO.

   So §6.1(ii)'s stated trigger — "unless and until either export is changed to
   carry `description` or equivalent AIAAIC-derived content" — is **already met
   for STIX today**; it is not the future contingency the spec treats it as.
   The consequence is that a CI assertion phrased as *"the STIX export contains
   zero AIAAIC-derived rows"* will **fail** the moment the WS0-T3 rebuild lands,
   because the AIAAIC rows are in the corpus and STIX exports the corpus
   unfiltered, descriptions included.

   This is flagged, not resolved: the shape owner does not own exporters, and
   the choice among the live options — filter AIAAIC rows out of STIX, carry the
   marker in STIX after all (e.g. as an `x_content_license` custom property,
   which the SDO's existing `x_`-prefixed extension style accommodates), or
   re-scope the assertion to something true — is a **licensing call for
   license-auditor plus a D12(b) revision by the foreman**, not an
   implementation detail. pipeline-engineer should not write the assertion until
   that is settled.

   **Update, 2026-07-27 (D14 discharge, interim exporter path landed).** The
   user resolved this as D14, option (ii): carry the marker in STIX as
   `x_content_license`, decoupled from and ahead of the WS0-T3 Phase B
   rebuild (every Pages deploy re-publishes unattributed AIAAIC prose until
   Phase B lands). distribution-engineer landed the interim exporter on
   `e14/stix-interim`: `_content_license()` in `scripts/export_stix.py`
   reads the entry's own `content_license` field verbatim when present (the
   post-Phase-B path) and otherwise falls back to `_is_aiaaic_derived()`, an
   interim heuristic over `source_ids` (prefix `aiaaic`, case-insensitive)
   unioned with `tags` (substring `aiaaic`). Measured against the live
   corpus (13,115 entries, 0 with `content_license` populated pre-Phase-B):
   `source_ids` alone hits 1,513; `tags` alone hits 1,495, a strict subset
   (0 tag-only rows); the union is exactly 1,513, matching the corpus's
   known AIAAIC-origin scale. The live rebuilt bundle carries
   `x_content_license` on exactly 1,513 of 13,115 `x-genai-incident` SDOs
   (e.g. `INC-04359`, the WPP deepfake case cited in the E14 escalation) and
   on zero others; the interim object mirrors this memo's §1/§3 shape
   key-for-key. Exporter stays network-free and byte-deterministic (two-run
   SHA-256 identical, `data/incidents.stix.json` and its `docs/data/`
   mirror). **Retirement condition, as amended by D15:** the heuristic is
   retired iff a Phase-B delta shows **zero under-attribution** — no row the
   heuristic would have marked is left unmarked by the field (over-
   attribution, a row the heuristic marks that the field does not, is the
   safe direction and does not block retirement; it was never observed
   anyway). Directional, not "identical on every affected row" as originally
   written here — the original non-directional wording predated knowing
   which divergence direction is unsafe and was unsatisfiable by design.

   **Update, 2026-07-29 (D15, heuristic retired).** Measured on the
   post-Phase-B corpus (13,119 entries): the field-derived set and the
   heuristic-derived set are both exactly 1,517 rows and **set-equal** —
   zero divergence in either direction, so retirement passes under the
   amended directional criterion *and* under the original non-directional
   one it superseded. `_is_aiaaic_derived()` and `_aiaaic_interim_license()`
   are removed from `scripts/export_stix.py`; `_content_license()` now
   returns the entry's own `content_license` field with no fallback.
   Verified byte-for-byte: the STIX bundle generated before and after the
   change is SHA-256-identical, and `x_content_license` coverage is 1,517
   both before and after. No fallback is kept going forward (see D15 for the
   reasoning: a fallback would silently mask, rather than surface, any
   future gap between this field and the rows it should cover).
6. **Notice-surface prose** (`NOTICE-DATA`, `.reuse/dep5`, README, and the
   `.zenodo.json` check D12(c) routed to implementation) is pipeline-engineer's
   per spec §4 — not touched here.
7. **Documentation debt this PR does not discharge:** `docs/DATA_DICTIONARY.md`
   documents neither `content_license` nor, as of today, the two D9 fields
   `description_provenance` / `description_source` — those shipped to schema
   only at `a2d7a26e`. All three need dictionary entries. This is flagged, not
   fixed, because this branch is scoped to `schema/` alone; it should land with
   the implementation PR that touches the other doc surfaces anyway.

## 5. Verification recipe

Files changed: `schema/incident.schema.json` and its packaged copy
`src/genai_incidents/schema/incident.schema.json`, kept byte-identical. The
packaged copy is regenerated from the canonical one by
`render_markdown.py:767`, so the two stay in sync on the next build regardless.

```
python -m pytest -q                 # full suite
python scripts/validate.py          # schema + cross-entry integrity gates
```

`validate.py` loads `schema/incident.schema.json` at runtime
(`validate.py:124`), so the new field and its conditional are enforced with no
change to the validator. Because the root schema sets
`additionalProperties: false`, the field addition is **load-bearing rather than
merely descriptive**: without it, a marker written by the pipeline would fail
validation outright.

**Measured on this branch, 2026-07-27** (exact, not approximate):

| Check | Result |
|---|---|
| `python -m pytest -q` | **203 passed**, 0 failed |
| `python scripts/validate.py` | **13115/13115 entries valid; 0 with errors**; integrity clean |
| Meta-schema (`Draft202012Validator.check_schema`) | PASS |
| Entries carrying `description_source` | **0 of 13115** |
| Entries carrying `description_provenance` | **0 of 13115** |
| Entries carrying `content_license` | **0 of 13115** |
| `schema/` vs `src/genai_incidents/schema/` | byte-identical, 16163 bytes, LF, sha256 `9f0793715adfbf81…` |

The conditional therefore passes **vacuously** today — no entry carries
`description_source`, because the D9 rebuild was reverted and only its schema
fields were kept. It becomes binding the moment pipeline-engineer's rebuild sets
that field, which is the intent. That also means **the corpus run cannot
demonstrate the conditional works**; it must be exercised directly.

Direct check of the conditional, independent of the corpus:

```
python - <<'PY'
import json, jsonschema
v = jsonschema.Draft202012Validator(
    json.load(open('schema/incident.schema.json', encoding='utf-8')))
base = {'id':'INC-00001','title':'Test entry title','date':'2025-01-01','year':2025,
        'category':'real-world','description':'x'*30,'severity':'Low',
        'references':[{'url':'https://example.org'}]}
print('marker missing on an aiaaic row ->',
      [e.message for e in v.iter_errors(dict(base, description_source='aiaaic'))])
PY
```

Expected: `["'content_license' is a required property"]`.

A 13-case matrix was run against the landed schema on 2026-07-27; all 13 gave
the intended verdict. The cases that carry design weight:

- an `aiaaic` row **without** the marker is **rejected** (the §6.2 acceptance
  criterion is schema-enforced, not merely jq-checked);
- an `aiaaic` row **with** a well-formed marker validates;
- a plain entry and a non-`aiaaic` row without the marker both still validate —
  **this is the no-regression case for all 13115 existing entries**;
- a non-`aiaaic` row **with** the marker is schema-**legal**. The schema
  deliberately does not enforce §6.2's second criterion (zero non-AIAAIC rows
  carry the marker), because that criterion is explicitly re-scopable per source;
  enforcing it here would have to be edited every time a source is added. **It
  stays a jq assertion**, per §6.2 as written;
- `obligations: ["attribution"]` alone validates — the §6.4 **waiver downgrade
  is a value change on the existing shape**, which is the whole argument for the
  obligations-enum in §2, now demonstrated rather than asserted;
- rejected as intended: a bare-string `content_license`, an unknown subfield, a
  missing required subfield, an empty `obligations` array, a non-enum obligation
  (`"copyleft"`), and duplicate obligations.
