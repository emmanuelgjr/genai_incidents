# Ingestion conduct policy

WS0-T4 (`MASTER_IMPROVEMENT_PLAN.md`). This document states what the code in
`ingest/common.py` **enforces** — not an aspiration, a description. Every
claim below cites the line(s) in `ingest/common.py` that make it true as of
this writing (commit history / `git blame` will drift the exact line numbers
over time; the function names will not). If a claim here and the code
disagree, the code is right and this doc is stale — file that as a defect
against this doc, not against the code.

Invariant 5 (`MASTER_IMPROVEMENT_PLAN.md`, staged-invariants table, Active
from "WS0-T4 done"; **amended by D22, 2026-07-29**): **all HTTP(S) fetching
for this repo's ingest pipeline goes through `ingest/common.py`.**
Non-HTTP egress — a vendor CLI such as `gh api`, `git clone`, or any other
subprocess that reaches the network — is **not exempt by default**: it sits
outside this invariant's *mechanism* (it cannot literally route through
`ingest/common.py`, which only ever speaks HTTP(S)) but inside its
*accounting* — every instance is registered below, with its conduct
properties, and **new non-HTTP egress requires its register entry in the
same PR** that introduces it (the same convention invariant 10 already
uses for new-source rows in `docs/SOURCE_LICENSES.md`). See the
[Non-HTTP egress register](#non-http-egress-register) below.

See `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` for the
completeness proof (every ingest script, its fetch targets, and confirmation
nothing else in the repo performs a live HTTP(S) fetch) and
`tests/test_network_chokepoint.py` for the CI enforcement of that property
going forward — its enumerated `NETWORK_CALL_TARGETS` are all HTTP(S)
primitives (`urlopen`/`requests.*`/`httpx.*`/etc.); it does not, and is not
meant to, catch non-HTTP egress, which is why the register exists as a
separate, deliberately non-code enforcement mechanism.

## What every request through `ingest/common.py` gets

### 1. An identifying User-Agent + contact address

`USER_AGENT` (`ingest/common.py:96-99`) is a single module-level constant:

```
genai_incidents/2.10.0 (+https://github.com/emmanuelgjr; contact: emmanuelgjr@gmail.com)
```

It names the project, links to the repo, and gives a contact address
(`emmanuelgjr@gmail.com`) — the same address already published as this
project's security/abuse contact in `SECURITY.md`, reused rather than
invented for this purpose. `fetch_once()` sends this on every request
(`ingest/common.py:367`) and **strips and replaces** any caller-supplied
`User-Agent` header rather than merging it (`ingest/common.py:368-369`), so
no calling script can accidentally (or deliberately) send an unidentified or
differently-identified request — enforced, not just the default; see
`tests/test_ingest_common.py::test_fetch_once_strips_caller_supplied_user_agent`
for the specific regression this guards (a caller-supplied
`ai-incidents-ingest/1.0` string that `ingest_cve_nvd_expanded.py` hardcoded
before this migration).

**The token leads the string; it is not `Mozilla/5.0`-prefixed** (changed
in WS0-T4 bounce #1, D3, from an earlier `Mozilla/5.0 (genai_incidents/2.8.0;
...)` form). `urllib.robotparser.Entry.applies_to()` — the function every
Python-stdlib robots.txt check ultimately calls — reduces a UA string to
`useragent.split("/")[0].lower()` before comparing it to a rule's own
`User-agent:` token. A `Mozilla/5.0`-led string reduces to the bare token
`"mozilla"`, identical to essentially every browser and most bots: an
operator who read this UA and wrote `User-agent: genai_incidents` in their
robots.txt would have been silently ignored. Leading with the project token
makes that reduction resolve to `"genai_incidents"` — addressable by name —
and removes the incidental `mozilla` over-match risk in the same move. A
live probe across all 18 real ingest-target URLs (robots.txt AND the actual
content endpoint, both UA shapes) found **zero** difference in outcome,
including on `www.cisa.gov` — the one host with any on-record evidence of
UA-sensitive behavior at all — so the WAF-rejection concern that originally
justified the `Mozilla/5.0` prefix had no supporting measurement. Full
evidence: `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`
§13.

Version number (`2.10.0`) and the full reasoning above are in the comment
immediately above the constant (`ingest/common.py:62-95`).

### 2. A robots.txt check before every fetch, fail-closed

`robots_allowed(url, min_interval)` (`ingest/common.py:280-314`) is checked
by `fetch_once()` before every request (`ingest/common.py:356-362`); a
disallowed or unverifiable URL raises `PermissionError` and the request is
never sent.

**Fail-closed, deliberately:** if robots.txt itself cannot be verified —
anything other than a 200 with parseable rules, or a confirmed 404 meaning
"no file published" — the fetch is refused, not assumed permitted
(`ingest/common.py:283-291`, `_get_robots_parser()` at
`ingest/common.py:208-277`). `_get_robots_parser()` retries once (with a 1 s
pause) before giving up, because a fast burst of parallel probe requests
during this module's own development drew one spurious 403 from a host whose
robots.txt was a confirmed clean 404 seconds later — a real, observed
transient-failure mode (`ingest/common.py:216-220`).

A confirmed 404 (no robots.txt at all) is read as "no stated restriction,"
not as an unreachable check — consistent with `docs/SOURCE_LICENSES.md`'s
existing reading of aiaaic.org's own 404 (`ingest/common.py:257-264`).

**There is no caller-side way to skip this check.** `fetch_once()` has no
`check_robots`-style parameter (`ingest/common.py:317-325`) — this was a
deliberate removal: a boolean flag on a shared function is an opt-out
reachable by a one-line edit at any call site, which defeats the point of a
single enforced chokepoint. The only way to waive the robots check for a
specific host is the enumerated allowlist below, which requires editing this
module in a reviewed commit.

**The robots.txt fetch itself is rate-limited too**, not just the content
fetch that follows it (`ingest/common.py:248`, inside
`_get_robots_parser()`'s retry loop) — this was a real gap until WS0-T4
bounce #1 (R3): the probe used to call `urlopen()` directly, unpaced, so a
host whose robots.txt could never be cached (any host on
`ROBOTS_UNVERIFIABLE_ALLOWLIST`, by construction — see the module's
`_robots_cache` comment on why an unverifiable outcome is never cached)
would take unpaced requests on **every single call**. `robots_allowed()`
now forwards its own `min_interval` into the probe, so a host's robots.txt
fetch and its content fetches share one consistent pacing budget, and the
"for every host, unconditionally" claim about the rate limiter (§3 below) is
now literally true, not just true of content fetches.

**Operational exposure of fail-closed (bounce #1, R4b), stated plainly, not
just argued for ethically:** this pipeline currently touches 12 distinct
hosts, mostly once a day, over one network path (the weekly
AIRI/AIAAIC/OECD/KEV run plus the on-demand NVD/GHSA/OSV run). A host that
403s its own robots.txt intermittently, or serves it differently by
geography or CDN edge, now breaks an ingest that worked fine under the
pre-WS0-T4 code, which never checked robots.txt at all. That is the direct,
accepted cost of fail-closed over fail-open — see the ethical case above —
stated here as an exposure, not only defended as a policy. **A refused
fetch is not only a missing update: depending on where in a script it
lands, it may truncate a committed artifact or permanently poison a cache
that later runs trust as complete** (D22 re-gate, A1/A6 — two real
instances found and fixed in `ingest_cve_nvd_expanded.py`'s NVD and OSV
phases; see `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`
§26-27 for the before/after evidence), not merely "no new data this run."

#### Exception: `ROBOTS_UNVERIFIABLE_ALLOWLIST`

One host is currently on this allowlist: **`www.cisa.gov`**
(`ingest/common.py:130-162`). `www.cisa.gov` and `cisa.gov` both return HTTP
403 on `/robots.txt` for **every** User-Agent tested — this project's own,
a plain browser UA, a bare non-Mozilla token, and urllib's unmodified
default — while the KEV feed itself
(`known_exploited_vulnerabilities.json`, ingested by
`scripts/ingest_cisa_kev.py`) returns HTTP 200 to the same set of UAs.
robots.txt is unreachable for any client here, not specifically blocked for
this project — so fail-closed's ordinary justification ("a host's operator
would have blocked this had their server answered") does not apply: the
server never answers robots.txt for anyone, and the actual feed being
fetched is a published US federal feed explicitly built for automated
consumption.

Verified independently three times now — once for the specialist report
this allowlist entry is drawn from, once during this task's initial pass,
once again during bounce #1's re-verification — each time via a raw
`urllib` probe with multiple distinct User-Agent strings against both hosts
plus the KEV feed URL. Full byte counts and the exact commands are in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`.

This is also the ONLY entry currently on the allowlist, and that fact is
itself enforced, not just true today:
`tests/test_ingest_common.py::test_robots_unverifiable_allowlist_is_pinned_and_fully_evidenced`
pins the exact host set and requires every entry to carry non-empty
`reason`/`evidence_date`/`evidence`/`still_enforced` fields — added in
bounce #1 (R1) after red-reviewer pointed out that nothing at runtime
actually read those fields, so a new entry with placeholder values would
otherwise waive fail-closed for a brand-new host with zero real evidence
and pass the rest of this suite unmodified.

**What the waiver does NOT cover:**
- It applies only when robots.txt could not be fetched **at all**. A host
  that serves a robots.txt with an explicit `Disallow` rule is refused
  exactly as normal, allowlisted or not (`ingest/common.py:311-314`,
  `robots_allowed()`'s closing block — the allowlist membership check on
  line 313 is reached only when `_get_robots_parser()` returns `None` on
  line 312; a successful parse instead falls through to `rp.can_fetch()` on
  line 314, bypassing the allowlist entirely).
- The per-host rate limit and the identifying User-Agent still apply in
  full to every request to `www.cisa.gov` — nothing about this entry
  changes pacing or identification, only the robots-verification refusal.

A future exception requires the same standard: a host name, a dated,
reproducible evidence trail, and an explicit statement of what stays
enforced — added to `ROBOTS_UNVERIFIABLE_ALLOWLIST` in a reviewed commit,
never a per-call parameter, and passing the pinned-set test above (which
will fail on the host-set change until deliberately updated).

### 3. A minimum interval between requests to the same host

`_rate_limit(host, min_interval)` (`ingest/common.py:185-205`) is called by
`fetch_once()` before every request (`ingest/common.py:365`), for every host,
unconditionally — and, as of bounce #1 (R3, §2 above), by the robots.txt
probe itself too, not just the content fetch. The default spacing is
`DEFAULT_MIN_INTERVAL = 1.0` second (`ingest/common.py:106`); callers may
pass a tighter or looser `min_interval=` for a source with its own
documented cadence (NVD's stated rate-limit contract is the example this
module was built against — see the per-source table below).

The limiter is thread-safe and global per host, not per caller: the next
allowed slot is reserved under a lock before the actual sleep happens, so
concurrent requests to the *same* host from multiple threads (e.g.
`ingest_oecd_aim.py`'s 10-worker pool) still queue up to the single
per-host cadence, while requests to *other* hosts are never blocked by it
(`ingest/common.py:185-205`, docstring explains the two guarantees
explicitly).

### 4. Retry with backoff, on transient failures

`robust_fetch()` (`ingest/common.py:378-437`) and `conditional_fetch()`
(`ingest/common.py:462-524`) both route every attempt through
`fetch_once()` — so robots/rate-limit/UA are enforced on *every* retry, not
just the first attempt — and use exponential backoff (2 s, 4 s, 8 s, ...)
between attempts. A robots.txt refusal (`PermissionError`) is **not**
retried in either function; it propagates immediately and unwrapped
(`ingest/common.py:414-425`, `:503-510`), since retrying a confirmed policy
block wastes backoff time for no chance of success.

**This required its own `except PermissionError: raise` clause ahead of
each function's broad exception catch, not just careful docstring wording**
(bounce #1, D1): `PermissionError` is, surprisingly, an `OSError` subclass
(`issubclass(PermissionError, OSError) == True`), and both functions' broad
`except` clauses already caught `OSError`. Before this fix, a robots
refusal was silently retried with backoff and re-raised as a generic
`RuntimeError("Failed to fetch ... after N attempts: ...")`,
indistinguishable from an ordinary flaky host — the same bug existed in
`ingest_cve_nvd_expanded.py`'s `http_get()`/`http_post_json()`, fixed
identically.

**Downstream, per script, once the exception is no longer masked** — traced
precisely rather than assumed, in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` §18:
- **CISA** and **OECD** ingests now crash their whole process on a robots
  refusal (no surrounding `try`/`except` catches the now-correctly-typed
  exception). `.github/workflows/auto-refresh.yml` runs both with
  `continue-on-error: true` plus a durable per-source consecutive-failure
  counter, so this is loud immediately (visible per-run) and durable
  (tracked across runs) without hard-failing the whole weekly workflow on a
  single occurrence — only after 3+ consecutive weeks.
  `.github/workflows/cve-enrich.yml` has no such tracking or
  `continue-on-error`.
- **NVD**'s `main()` catches the refusal one level up (a broader
  `except Exception` around each keyword) and, per an added fix in the same
  bounce, aborts the whole NVD phase with one clear message rather than
  silently repeating the same refusal across every remaining keyword — but
  the script still exits 0, so an NVD robots refusal is loud in the console
  log only, with no step-, health-counter-, or workflow-level signal at
  all. This is a real, disclosed, and currently accepted limitation, not
  something bounce #1 closed.
- **OSV** (added at the D22 re-gate, A1): `main()`'s `try`/`except
  PermissionError` around `fetch_osv()` aborts the OSV phase the same way,
  with the same "loud in the console, silent everywhere else" limitation
  as NVD. `fetch_osv()` itself originally had the identical
  trust-cache/swallow/write-unconditionally bug `fetch_nvd_keyword()` had
  before D1 — found one function away by the re-gate, not by a systematic
  search; fixed identically (re-raise before the unconditional cache
  write is ever reached). A systematic sweep for a third instance of this
  shape, across every fetcher, is a named follow-up, not done here.

Scripts with their own retry cadence (NVD, OSV — both inside
`ingest_cve_nvd_expanded.py`) call `fetch_once()` directly, once per
attempt, inside their own loop, rather than using `robust_fetch()`.

**`robust_fetch()`'s warm-cache path performs no robots check at all** —
returning bytes already on disk is a local-disk read, not a network
request, so there is nothing to check permission for
(`ingest/common.py:390-394`). This was previously true but undocumented;
disclosed here per bounce #1 (R5).

### 5. WS4-T17 — the OECD AIM skip-rule sampling probe reintroduces K requests/run

WS4-T13 made `scripts/ingest_oecd_aim.py` skip legacy numeric-slug URLs
(OECD AIM's pre-date-hash incident-ID scheme) **before** they ever reach the
fetch pool, on the measured premise that every one of them fails the
`ng-state` body-shape check (0 exceptions across 1852 pages,
`docs/audits/E21-tripwire-refresh-2026-09-14.md`). That skip is what cut
~59% of requests to `oecd.ai` (≈1,773 of a 3,000-URL crawl window). But a
skip that is never fetched can never be re-checked, so WS4-T17 adds a small,
rotating **sampling probe**: each run, `run_skip_sampling_probe()`
(`scripts/ingest_oecd_aim.py`) fetches `K` (default `DEFAULT_PROBE_SAMPLE_SIZE
= 5`, overridable via `OECD_AIM_PROBE_SAMPLE_SIZE`) of the URLs the budget
skip decided NOT to fetch, and asserts each one still fails the body-shape
check — routed through the exact same `fetch_and_extract()` →
`fetch_page()` → `ingest.common.robust_fetch()` chokepoint the main crawl
uses. **No new egress path**: invariant 5 (this module) still enforces the
identifying User-Agent, the fail-closed robots.txt check, and
`DEFAULT_MIN_INTERVAL` on every one of these K requests, exactly as it does
for every other `oecd.ai` fetch.

**Net conduct effect, with numbers:** on a representative 3,000-URL window
(the 2026-09-14 measurement: 1,852 numeric-slug / 1,148 date-hash-slug),
WS4-T13 cut the crawl from 3,000 requests to ≈1,227 (the fetchable,
non-skipped set) — a reduction of ≈1,773 requests, ~59%. WS4-T17 adds
`K=5` requests back on top of that ≈1,227, landing at ≈1,232 — **still a
~58.9% reduction** versus the pre-WS4-T13 baseline; the probe consumes a
negligible sliver (≈0.4%) of the headroom WS4-T13 recovered. Per-run wall-
clock cost: at `DEFAULT_MIN_INTERVAL = 1.0` s/host (shared across all
worker threads — §3 above) and `K=5` sequential probe fetches, the probe
costs on the order of 5 seconds against the ~36 minutes of workflow-timeout
headroom WS4-T13 recovered (the reviewer's own sizing, used as specified in
the WS4-T17 brief rather than independently re-derived, since actual
per-request latency to `oecd.ai` varies and 5 request-slots' worth of rate-
limiter spacing is the dominant, measurable-in-code term either way).

The probe never fetches the *whole* skipped set — it samples a rotating
slice (`select_probe_sample()`), so coverage of the ~1,852-URL legacy
population accumulates gradually across runs rather than being re-verified
in one shot; see that function's docstring for why rotating (not random)
sampling was chosen. A violation (a legacy numeric-slug URL that now
returns a real incident body — `REASON_OK`) fails the scheduled workflow
run loudly on the first occurrence, via its own dedicated gate (`--check-
probe` / "Check OECD skip-rule sampling probe" + "Enforce OECD skip-rule
sampling probe" in `.github/workflows/auto-refresh.yml`) — deliberately
**not** routed through `ingest/_state/source_health.json`'s 3-consecutive-
failures smoothing (WS4-T9), because a skip-rule violation is a
deterministic correctness signal about data loss, not ordinary third-party
flakiness. See `run_skip_sampling_probe()` and
`check_probe_state_for_violations()`'s docstrings in
`scripts/ingest_oecd_aim.py` for the full design.

## Per-source pacing

Every real ingest target's chokepoint routing, robots verdict, and pacing is
tabulated in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` — this
section is the policy statement; that document is the per-source evidence.

## Non-HTTP egress register

Per invariant 5's D22 amendment (2026-07-29): this section is **not** "out
of scope" — non-HTTP egress is explicitly inside the invariant's
*accounting*, only outside its *mechanism* (it cannot route through
`ingest/common.py`, which is an HTTP(S)-only module). Every known instance
is listed below with its conduct properties. **New non-HTTP egress requires
its register entry in the same PR that introduces it** — the same
convention invariant 10 already uses for `docs/SOURCE_LICENSES.md` rows on
a new source. An incomplete register is treated as worse than none, because
future PRs are checked against what's listed here, not against what
actually exists.

### 1. `gh api graphql` — GHSA advisory data (registered, active)

- **What:** `ingest_cve_nvd_expanded.py`'s GHSA phase (`fetch_ghsa()`)
  shells out to GitHub's official CLI: `subprocess.run(["gh", "api",
  "graphql", "-f", f"query={query}", ...])`
  (`scripts/ingest_cve_nvd_expanded.py:665,670`) — a real, executed,
  in-repo network call, not a Python-level HTTP fetch.
- **What it touches:** GitHub's GraphQL API, `securityAdvisories` (both
  `GENERAL` and `MALWARE` classifications) — the GitHub Security Advisory
  Database.
- **Pacing:** an explicit `time.sleep(1.5)` between pages
  (`scripts/ingest_cve_nvd_expanded.py:693`), on top of whatever GitHub's
  own GraphQL API rate-limit budget (tied to the authenticated token) `gh`
  itself respects — this is the vendor tool's own conduct property, stated
  concretely rather than asserted on trust: `gh` is GitHub's first-party
  CLI, calling GitHub's own API, under GitHub's own documented rate-limit
  contract for authenticated requests.
- **Identification:** authenticated via `GH_TOKEN`
  (`.github/workflows/cve-enrich.yml:39`: `GH_TOKEN: ${{ github.token }}`
  — the workflow's own GitHub Actions token; a maintainer running this
  locally uses their own `gh auth login` session). This is a properly
  authenticated, per-identity API call, not anonymous scraping — `gh`
  itself sends its own standard client identification on every request; it
  does not, and could not, use `ingest.common.USER_AGENT` (a different
  HTTP client entirely, owned by GitHub's own tool).
- **Why outside the chokepoint's mechanism:** there is no robots.txt
  equivalent for an authenticated GraphQL API accessed through its own
  vendor's official CLI — robots.txt governs unauthenticated crawling of
  publicly served pages, which this is not.

### 2. `_external/` repo population (source data for `ingest_external.py`) — DISCLOSED GAP, not a registered instance

`ingest_external.py`'s own docstring and `README.md:62` describe it as
parsing "cloned source repos under `../_external/`" (six repos: MITRE
ATLAS `atlas-data`, NVIDIA `garak`, `promptfoo/promptfoo`,
`ModelOriented/CVE-AI`, `georgetown-cset/CSET-AIID-harm-taxonomy`, and the
`responsible-ai-collaborative/aiid` site repo — the last is also
`scripts/scrape_aiid.py`'s and `ingest_aiid_oecd_bridge()`'s source for
`_external/aiid/site/gatsby-site/migrations/data/oecd_relationships_2025_09_09.json`
and the two `_external/sitemap-*.xml` files).

**Completeness check performed** (per this bounce's instruction — searched,
not assumed): `ingest_external.py`'s own imports are `csv`, `json`, `re`,
`pathlib.Path`, `datetime.date` only — **no `subprocess`, no `os.system`,
no git-library import, nothing network-capable at all.** Grepped
`scripts/*.py` for `subprocess\.|os\.system|os\.popen` — the only hit
anywhere in the directory is `ingest_cve_nvd_expanded.py:670` (Entry 1
above). Grepped `scripts/*.py` and `.github/workflows/*.yml` for `git
clone|git submodule|pygit2|dulwich|GitPython` — **zero hits anywhere.**
There is no `Makefile` target, script, or CI workflow step anywhere in this
repository that clones, updates, or otherwise populates `_external/`.

**Conclusion, stated plainly rather than assumed from the docstring's
wording: populating `_external/` is an undocumented, manual, out-of-band
maintainer step, not code that runs as part of any tracked pipeline.**
There is no non-HTTP-egress *instance* to register in the sense the D22
amendment means (a subprocess that reaches the network) — there is no
subprocess. This corrects an assumption in this document's own prior
draft, and in `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`
§4, that treated `ingest_external.py`'s `git clone` as an existing,
in-repo precedent for the `gh api graphql` scoping call — on inspection,
no such clone exists in code anywhere; only `docs/SOURCE_LICENSES.md`
§3.1's "N/A — local clone of a public repo" line describes the same
informal, out-of-band practice, not a script.

This is registered here anyway, as a **named gap**, because "an
incomplete register is worse than none" cuts both ways: a register that
silently omits the six repos `ingest_external.py` depends on would look
complete while leaving the actual, un-conduct-instrumented network access
(a maintainer's own `git clone` commands, run by hand, with none of this
project's rate-limiting, identification, or fail-closed robots checking)
entirely invisible to a future reader of this document. **No conduct
properties are stated for it because none are enforced for it today** —
that absence is the finding. Whether to script this population step (e.g.
a `make setup-external` target using `git clone --depth 1` under the same
kind of pacing/identification discipline as `ingest/common.py`) is a
design decision for a future task, flagged here, not decided or
implemented in this one.

### Scoping note: excluded from this register

`scripts/persist_refresh_state.sh:66`'s own `git clone` (invoked from
`.github/workflows/auto-refresh.yml`'s "Persist source health counters to
refresh-state branch" step, persisting `ingest/_state/source_health.json`
to the `refresh-state` branch — extracted out of that workflow step into
this script 2026-09-14 so it is testable without a live GitHub repo; see
`tests/test_persist_refresh_state.py`) and
`peter-evans/create-pull-request`'s git operations opening the weekly
refresh PR are **not** registered here. These are CI/CD operations on
this repository's *own* git history — GitHub talking to GitHub via
`${{ github.token }}` — not ingestion of external corpus data from a
third-party source, which is what this invariant and this register are
about. Named here so the exclusion is a stated scoping decision, not a
silent omission.

`make build` never imports `ingest/common.py` at all. Ingest scripts are
not in the deterministic build path (`Makefile`'s `build` target is
`merge render render-docs-stats validate`, none of which touch the
network) — `ingest/common.py`'s own module docstring states this, and
`WS4-T1`'s `make build` contract (no network, no model calls) enforces it
independently of anything in this file.

## Outreach log

The plan's Accept criterion for this task requires outreach emails to AIID,
AIAAIC, and OECD AIM, "drafted, sent (human sends), and logged with dates."
Per `CLAUDE.md`, outreach is drafted by agents and sent by the user; this
project's escalation rule keeps that division intentionally, and the OECD item
below — absent when this file was first written — was drafted separately rather
than by this pipeline-engineer report.

All drafts live under `docs/outreach/`; `docs/outreach/README.md` is the
authoritative index. Status as of 2026-07-30:

| Recipient | Draft(s) | Sent | Notes |
|---|---|---|---|
| AI Incident Database (AIID) | `docs/outreach/aiid-goodwill.md` | **2026-07-27** | Goodwill notice: scraping stopped, per-incident attribution added, attribution-terms question. |
| AIAAIC | `docs/outreach/aiaaic-facts-link.md` | **2026-07-27** | Database-right / ShareAlike question. |
| AIAAIC (correction) | `docs/outreach/aiaaic-correction.md` | **2026-07-29** | E17: corrected an earlier under-description of what fields are retained from AIAAIC records. |
| MIT AIRI Navigator | `docs/outreach/mit-airi-courtesy.md` | **2026-07-27** | Courtesy notice (dead ZIP download) + informal transitive-AIID licensing question. |
| MIT AI Risk Initiative | `docs/outreach/airi-draft4-export-request.md` | **2026-07-29** | Substantive sanctioned-export/API request + the same transitive-AIID question, more precisely stated. Starts the D8 30-day AIRI-hold clock. |
| **OECD AI Incidents and Hazards Monitor (AIM)** | `docs/outreach/oecd-aim-terms.md` | **Not sent** — drafted **2026-07-30** | Reuse-terms question for AIM's own structured data (our own terms fetch 403s) plus a sanctioned-bulk-channel question. Proposed recipient `ai@oecd.org` — **UNCONFIRMED**: what was verified is that it is the sole `mailto:` address in the raw HTML of `oecd.ai/en/contact`, one hop from the site's own nav; whether it is the right desk for a licensing/reuse-terms question rather than a general AI-policy inbox is expressly left to the user to confirm before sending (see the draft's own "To (UNCONFIRMED)" note). Gated PASS; **awaiting the user's send**, who logs the date on `docs/outreach/README.md` and in `docs/SOURCE_LICENSES.md` §1.5. This draft is genuinely the first: no OECD outreach file existed on any branch before it (`git log --all --diff-filter=A -- 'docs/outreach/*'`), which is why §1.5's earlier "Outreach date 2026-07-15 (drafted; not yet sent)" was false and has been corrected there (E20). |

**Conclusion on the Accept criterion's outreach clause.** Per **D21** the
criterion is split, and the two halves track separately:

- **Clause 1 (the code property — all HTTP(S) fetching through
  `ingest/common.py`): DONE and merged** (`8b1e8888`); Invariant 5 is ACTIVE.
- **Clause 2 (outreach): OPEN, on OECD's send alone.** All three recipients the
  criterion names now have a drafted email. Two are **sent** with logged dates
  — AIID `2026-07-27`, AIAAIC `2026-07-27` plus the `2026-07-29` correction —
  and OECD AIM is **drafted 2026-07-30, not yet sent**, so the clause is **not
  yet satisfied**. It closes when that one send happens and its date is logged;
  nothing else is outstanding on it. (MIT AIRI, not named by the criterion, is
  additionally covered: courtesy notice sent `2026-07-27`, export request
  `2026-07-29`.)

See `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` for the
full Accept-criterion verdict as assessed on that date, which covers both the
outreach clause and the grep clause together.
