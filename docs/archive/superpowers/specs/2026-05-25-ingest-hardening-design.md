# Ingest Pipeline Hardening — Design Spec

**Date:** 2026-05-25
**Status:** Approved
**Author:** Emmanuel Guilherme Junior + Claude

## Goal

Make the weekly auto-refresh ingest pipeline robust, efficient, and resilient by adding retry logic, conditional fetching, header-based column parsing, and removing dead code.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Code organization | Shared `scripts/ingest_utils.py` module | DRY — all three scripts reuse the same retry/fetch logic |
| Retry strategy | Exponential backoff (2s, 4s, 8s), max 3 retries | Standard pattern; fast enough for CI, resilient to transient failures |
| Bandwidth optimization | ETag/Last-Modified conditional fetch for AIRI + AIAAIC | Avoids re-downloading unchanged data every week |
| AIAAIC column parsing | Header-based lookup instead of positional indices | Survives Google Sheet schema changes |
| AIRI dead code | Remove vestigial `is_security_relevant()` filter | All entries are kept anyway; dead code is confusing |
| CVE script | No changes, stays out of weekly workflow | Too slow (20 min) for weekly automation |

## Architecture

### 1. Shared utility module: `scripts/ingest_utils.py`

Two public functions, no new dependencies (uses stdlib `urllib.request`).

**`robust_fetch(url, cache_path, *, timeout=60, max_retries=3, min_cache_bytes=1000, headers=None) -> bytes`**
- If `cache_path` exists and `size >= min_cache_bytes`, return cached content immediately
- Otherwise fetch from URL with up to `max_retries` attempts
- Backoff: `2 ** attempt` seconds (2s, 4s, 8s)
- Catches: `urllib.error.URLError`, `urllib.error.HTTPError`, `TimeoutError`, `ConnectionError`, `OSError`
- Logs each retry to stderr: `[retry] attempt N/M for <url>: <error>`
- On success: writes to `cache_path`, returns content
- On final failure: raises `RuntimeError` with last error message

**`conditional_fetch(url, cache_path, *, timeout=60, max_retries=3, min_cache_bytes=1000, headers=None) -> tuple[bytes, bool]`**
- If cache is cold (no file or too small): delegates to `robust_fetch`, returns `(content, True)`
- If cache is warm: reads ETag/Last-Modified from `<cache_path>.etag` sidecar file
- Sends `If-None-Match` and/or `If-Modified-Since` headers
- If server returns 304 Not Modified: returns `(cached_content, False)`
- If server returns 200: stores new ETag/Last-Modified in sidecar, writes cache, returns `(content, True)`
- If server doesn't support conditional requests (no ETag header in response): falls back to full fetch
- Uses same retry/backoff logic as `robust_fetch` for the fetch itself

**Sidecar file format** (`<cache_path>.etag`):
```
etag: "abc123"
last-modified: Sun, 25 May 2026 04:00:00 GMT
```

### 2. AIRI Navigator updates

- Replace `download_zip()` body with call to `conditional_fetch(ZIP_URL, ZIP_PATH)`
- Remove `is_security_relevant()` function (lines 111-113) and the no-op filter block that calls it (lines 137-140)
- Log whether the ZIP was re-downloaded or served from cache

### 3. AIAAIC Sheet updates

**Conditional fetch:**
- Replace `download_csv()` body with call to `conditional_fetch(CSV_URL, CACHE_FILE)`

**Header-based column parsing:**
- Remove the 7 `COL_*` constant lines (lines 42-48)
- After reading CSV, parse first row as headers
- Build a mapping dict: `{header_text.strip().lower(): index}`
- Define expected column names as constants:
  ```python
  EXPECTED_COLUMNS = {
      "id": ["#", "id"],
      "headline": ["headline/title", "headline", "title"],
      "occurred": ["occurred", "date"],
      "deployer": ["deployer(s)", "deployer"],
      "developer": ["developer(s)", "developer"],
      "system": ["system(s)", "system"],
      "technology": ["technology(ies)", "technology"],
      "purpose": ["purpose(s)", "purpose"],
      "trigger": ["trigger", "issue trigger"],
      "ethical": ["issue(s)", "ethical issue(s)", "issue"],
      "jurisdiction": ["jurisdiction", "country"],
      "sector": ["sector(s)", "sector"],
      "harm_individual": ["ind. harm(s)", "individual harm"],
      "harm_societal": ["soc. harm(s)", "societal harm"],
      "harm_environment": ["env. harm(s)", "environmental harm"],
      "consequence": ["consequence", "consequence(s)"],
      "response": ["response", "response(s)"],
      "summary": ["summary", "links"],
  }
  ```
- Lookup function tries each alias in order; raises clear error if a required column can't be found
- Access in code: `row[col["headline"]]` instead of `row[COL_HEADLINE]`

### 4. OECD AIM updates

- Replace the inline `try/except` in `fetch_page()` with a call to `robust_fetch(url, cache_file, timeout=20, min_cache_bytes=1000)`
- Keep the ThreadPoolExecutor, progress logging, and 800KB read cap as-is
- The 800KB read cap stays inline in the OECD script (only user of this constraint) — `robust_fetch` handles the retry/cache logic, then OECD truncates the result

### 5. Workflow — no changes

The `auto-refresh.yml` workflow stays the same. Each script already has `continue-on-error: true`. The retry logic inside the scripts handles transient failures; `continue-on-error` handles total source outages.

## Scope Boundaries

**In scope:**
- `scripts/ingest_utils.py` (new)
- `scripts/ingest_airi_navigator.py` (update fetch, remove dead filter)
- `scripts/ingest_aiaaic_sheet.py` (update fetch, header-based columns)
- `scripts/ingest_oecd_aim.py` (update fetch to use shared module)
- Tests for the shared utility module

**Out of scope:**
- CVE/NVD script changes
- Workflow YAML changes
- New ingest sources
- Changes to merge_and_dedupe.py

## Tradeoffs

- **ETag sidecar files** add `.etag` files next to each cache file. Minimal clutter since they're in `ingest/_cache/` which is already gitignored.
- **Header-based parsing** is slightly slower than positional (dict lookup vs index), but negligible for ~2,000 rows and eliminates a class of silent failures.
- **Retry with backoff** adds up to 14s worst-case delay per script (2+4+8). Acceptable in a 60-minute timeout CI job.
