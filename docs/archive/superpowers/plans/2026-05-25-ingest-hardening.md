# Ingest Pipeline Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the weekly auto-refresh ingest pipeline robust with retry logic, conditional fetching, header-based column parsing, and dead code removal.

**Architecture:** A new shared `scripts/ingest_utils.py` module provides `robust_fetch()` and `conditional_fetch()` with exponential backoff. All three ingest scripts are updated to use these instead of inline urllib calls. AIAAIC additionally switches from positional column indices to header-based lookup.

**Tech Stack:** Python 3.12, stdlib `urllib.request`, pytest

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `scripts/ingest_utils.py` | Shared retry/conditional-fetch utilities |
| Create | `tests/test_ingest_utils.py` | Tests for the shared module |
| Modify | `scripts/ingest_airi_navigator.py` | Use conditional_fetch, remove dead filter |
| Modify | `scripts/ingest_aiaaic_sheet.py` | Use conditional_fetch, header-based columns |
| Modify | `scripts/ingest_oecd_aim.py` | Use robust_fetch in fetch_page |

---

### Task 1: Create shared ingest_utils module with robust_fetch

**Files:**
- Create: `scripts/ingest_utils.py`
- Create: `tests/test_ingest_utils.py`

- [ ] **Step 1: Write the failing tests for robust_fetch**

Create `tests/test_ingest_utils.py`:

```python
"""Tests for shared ingest utilities."""

from __future__ import annotations

import urllib.error
from unittest.mock import patch, MagicMock

import ingest_utils as u


def test_robust_fetch_returns_cached_content(tmp_path):
    """If cache file exists and is large enough, return it without fetching."""
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"x" * 2000)
    result = u.robust_fetch("https://example.com/data", cache, min_cache_bytes=1000)
    assert result == b"x" * 2000


def test_robust_fetch_skips_small_cache(tmp_path):
    """Cache file below min_cache_bytes should be ignored."""
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"tiny")
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"fresh data"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = u.robust_fetch("https://example.com/d", cache, min_cache_bytes=1000)
    assert result == b"fresh data"
    assert cache.read_bytes() == b"fresh data"


def test_robust_fetch_retries_on_failure(tmp_path):
    """Should retry up to max_retries times before raising."""
    cache = tmp_path / "data.bin"
    with patch("ingest_utils.urllib.request.urlopen") as mock_open, \
         patch("ingest_utils.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("connection refused")
        try:
            u.robust_fetch("https://example.com/x", cache, max_retries=3)
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "connection refused" in str(e)
        assert mock_open.call_count == 3


def test_robust_fetch_succeeds_on_second_try(tmp_path):
    """Should return data if a retry succeeds."""
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"ok"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open, \
         patch("ingest_utils.time.sleep"):
        mock_open.side_effect = [urllib.error.URLError("timeout"), mock_resp]
        result = u.robust_fetch("https://example.com/x", cache, max_retries=3)
    assert result == b"ok"
    assert mock_open.call_count == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ingest_utils.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ingest_utils'`

- [ ] **Step 3: Implement robust_fetch**

Create `scripts/ingest_utils.py`:

```python
"""Shared utilities for ingest scripts: retry logic and conditional fetching."""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (genai_agentic_incidents/2.0; +https://github.com/emmanuelgjr)"


def robust_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
) -> bytes:
    """Fetch URL content with retry logic and disk caching.

    Returns cached content if the cache file exists and is at least
    ``min_cache_bytes`` large. Otherwise fetches from *url* with up to
    *max_retries* attempts using exponential backoff (2s, 4s, 8s, ...).
    """
    if cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes:
        return cache_path.read_bytes()

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            return data
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                delay = 2 ** attempt
                print(
                    f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}",
                    file=sys.stderr,
                )
                time.sleep(delay)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ingest_utils.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/ingest_utils.py tests/test_ingest_utils.py
git commit -m "feat: add ingest_utils module with robust_fetch"
```

---

### Task 2: Add conditional_fetch to ingest_utils

**Files:**
- Modify: `scripts/ingest_utils.py`
- Modify: `tests/test_ingest_utils.py`

- [ ] **Step 1: Write the failing tests for conditional_fetch**

Append to `tests/test_ingest_utils.py`:

```python
def test_conditional_fetch_cold_cache(tmp_path):
    """Cold cache should do a full fetch and save ETag sidecar."""
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"payload"
    mock_resp.getheader.side_effect = lambda h, d=None: {
        "ETag": '"abc123"', "Last-Modified": "Sun, 25 May 2026 00:00:00 GMT"
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"payload"
    assert changed is True
    etag_file = tmp_path / "data.bin.etag"
    assert etag_file.exists()
    assert '"abc123"' in etag_file.read_text(encoding="utf-8")


def test_conditional_fetch_304_not_modified(tmp_path):
    """Warm cache + 304 response should return cached content, changed=False."""
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"cached payload")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "abc123"\n', encoding="utf-8")
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/d", 304, "Not Modified", {}, None
        )
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"cached payload"
    assert changed is False


def test_conditional_fetch_200_with_new_etag(tmp_path):
    """Warm cache but server returns 200 → update cache and sidecar."""
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"old")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "old"\n', encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"new data"
    mock_resp.getheader.side_effect = lambda h, d=None: {
        "ETag": '"new456"'
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"new data"
    assert changed is True
    assert '"new456"' in etag_file.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ingest_utils.py::test_conditional_fetch_cold_cache -v`
Expected: FAIL with `AttributeError: module 'ingest_utils' has no attribute 'conditional_fetch'`

- [ ] **Step 3: Implement conditional_fetch**

Append to `scripts/ingest_utils.py`:

```python
def conditional_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
) -> tuple[bytes, bool]:
    """Fetch URL with ETag/Last-Modified conditional request support.

    Returns ``(content, changed)`` where *changed* is False if the server
    returned 304 Not Modified (cache is still valid).
    """
    etag_path = Path(str(cache_path) + ".etag")
    cache_warm = cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)

    if cache_warm:
        saved = _read_etag_sidecar(etag_path)
        if saved.get("etag"):
            hdrs["If-None-Match"] = saved["etag"]
        if saved.get("last-modified"):
            hdrs["If-Modified-Since"] = saved["last-modified"]

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                etag = resp.getheader("ETag")
                last_mod = resp.getheader("Last-Modified")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            _write_etag_sidecar(etag_path, etag, last_mod)
            return data, True
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return cache_path.read_bytes(), False
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `pytest tests/test_ingest_utils.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/ingest_utils.py tests/test_ingest_utils.py
git commit -m "feat: add conditional_fetch with ETag/Last-Modified support"
```

---

### Task 3: Update AIRI Navigator to use conditional_fetch and remove dead code

**Files:**
- Modify: `scripts/ingest_airi_navigator.py`

- [ ] **Step 1: Add import for ingest_utils**

At the top of `scripts/ingest_airi_navigator.py`, after the existing imports (line 25), add:

```python
from ingest_utils import conditional_fetch
```

- [ ] **Step 2: Replace download_zip with conditional_fetch**

Replace lines 73–83 (`def download_zip()`) with:

```python
def download_zip() -> tuple[Path, bool]:
    """Download the AIRI ZIP with conditional fetch (ETag support)."""
    data, changed = conditional_fetch(ZIP_URL, ZIP_PATH, min_cache_bytes=100_000)
    if not changed:
        print("[airi] ZIP unchanged (304), using cache")
    else:
        print(f"[airi] downloaded {len(data):,} bytes -> {ZIP_PATH.name}")
    return ZIP_PATH, changed
```

- [ ] **Step 3: Remove dead security filter**

Delete the `is_security_relevant` function (lines 111–113) and the dead filter block in `normalize_row` (lines 137–140):

```python
    if not is_security_relevant(title, desc):
        # Keep all incidents anyway — AIRI is curated and adds taxonomy
        # value across the board. Skip only purely non-AI rows.
        pass
```

Also remove `SECURITY_KEYWORDS` (lines 95–108) since nothing references it after removing `is_security_relevant`.

- [ ] **Step 4: Update main() to use the new download_zip signature**

Change line 191 from:

```python
    zip_path = download_zip()
```

To:

```python
    zip_path, _ = download_zip()
```

- [ ] **Step 5: Remove the unused `ssl` import**

The `ssl` import on line 22 was only used in the old `download_zip`. Remove it:

```python
import ssl  # DELETE THIS LINE
```

- [ ] **Step 6: Run the full test suite to verify nothing broke**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/ingest_airi_navigator.py
git commit -m "feat: AIRI uses conditional_fetch, remove dead security filter"
```

---

### Task 4: Update AIAAIC to use conditional_fetch and header-based columns

**Files:**
- Modify: `scripts/ingest_aiaaic_sheet.py`

- [ ] **Step 1: Add import for ingest_utils**

At the top of `scripts/ingest_aiaaic_sheet.py`, after the existing imports (line 25), add:

```python
from ingest_utils import conditional_fetch
```

- [ ] **Step 2: Replace download_csv with conditional_fetch**

Replace lines 127–139 (`def download_csv()`) with:

```python
def download_csv() -> tuple[str, bool]:
    """Fetch the sheet CSV with conditional fetch (ETag support)."""
    data, changed = conditional_fetch(CSV_URL, CACHE_FILE, min_cache_bytes=100_000)
    if not changed:
        print("[aiaaic] CSV unchanged (304), using cache")
    else:
        print(f"[aiaaic] downloaded {len(data):,} bytes -> {CACHE_FILE.name}")
    return data.decode("utf-8", errors="replace"), changed
```

- [ ] **Step 3: Replace positional column constants with header-based lookup**

Delete lines 40–48 (the comment and `COL_*` constants):

```python
# AIAAIC headers come on row index 1 of the dump (row 0 is the section
# label "Incidents"). Columns are positional in the export.
COL_ID, COL_HEADLINE, COL_OCCURRED, COL_DEPLOYER, COL_DEVELOPER = 0, 1, 2, 3, 4
COL_SYSTEM, COL_TECH, COL_PURPOSE = 5, 6, 7
COL_TRIGGER, COL_ETHICAL = 8, 9
COL_JURISDICTION, COL_SECTOR = 10, 11
COL_HARM_INDIV, COL_HARM_SOCIETAL, COL_HARM_ENV = 12, 13, 14
COL_CONSEQ, COL_RESPONSE = 15, 16
COL_SUMMARY = 17
```

Replace with:

```python
EXPECTED_COLUMNS: dict[str, list[str]] = {
    "id":          ["aiaaic id#", "#", "id"],
    "headline":    ["headline/title", "headline", "title"],
    "occurred":    ["occurred", "date"],
    "deployer":    ["deployer(s)", "deployer"],
    "developer":   ["developer(s)", "developer"],
    "system":      ["system(s)", "system"],
    "technology":  ["technology(ies)", "technology"],
    "purpose":     ["purpose(s)", "purpose"],
    "trigger":     ["issue trigger", "trigger"],
    "ethical":     ["issue(s)", "ethical issue(s)", "issue"],
    "jurisdiction": ["jurisdiction", "country"],
    "sector":      ["sector(s)", "sector"],
    "harm_indiv":  ["ind. harm(s)", "individual harm(s)", "individual harm"],
    "harm_societal": ["soc. harm(s)", "societal harm(s)", "societal harm"],
    "harm_env":    ["env. harm(s)", "environmental harm(s)", "environmental harm"],
    "consequence": ["consequence(s)", "consequence"],
    "response":    ["response(s)", "response"],
    "summary":     ["summary", "links"],
}


def build_column_map(header_row: list[str]) -> dict[str, int]:
    """Map logical column names to indices based on the actual header row."""
    normalized = [h.strip().lower() for h in header_row]
    col_map: dict[str, int] = {}
    for key, aliases in EXPECTED_COLUMNS.items():
        for alias in aliases:
            if alias in normalized:
                col_map[key] = normalized.index(alias)
                break
        else:
            print(f"  [aiaaic] WARNING: column '{key}' not found (tried {aliases})", file=sys.stderr)
            col_map[key] = -1
    return col_map
```

- [ ] **Step 4: Add `sys` import**

Add at the top of the file (after the existing imports):

```python
import sys
```

- [ ] **Step 5: Update normalize_row to use column map**

Change `normalize_row` signature from:

```python
def normalize_row(raw_row: list[str]) -> dict | None:
```

To:

```python
def normalize_row(raw_row: list[str], col: dict[str, int]) -> dict | None:
```

Then replace every `raw_row[COL_*]` reference with a safe accessor. Replace the body of `normalize_row` (lines 206–318) with:

```python
def _cell(raw_row: list[str], col: dict[str, int], key: str) -> str:
    """Safely get a cell value by logical column name."""
    idx = col.get(key, -1)
    if idx < 0 or idx >= len(raw_row):
        return ""
    return (raw_row[idx] or "").strip()


def normalize_row(raw_row: list[str], col: dict[str, int]) -> dict | None:
    while len(raw_row) < max(col.values()) + 1:
        raw_row.append("")
    row_id = _cell(raw_row, col, "id")
    if not row_id.startswith("AIAAIC"):
        return None
    if row_id == "AIAAIC ID#":
        return None

    row = {
        "id": row_id,
        "headline": _cell(raw_row, col, "headline"),
        "occurred": _cell(raw_row, col, "occurred"),
        "deployer": _cell(raw_row, col, "deployer"),
        "developer": _cell(raw_row, col, "developer"),
        "system": _cell(raw_row, col, "system"),
        "technology": _cell(raw_row, col, "technology"),
        "purpose": _cell(raw_row, col, "purpose"),
        "trigger": _cell(raw_row, col, "trigger"),
        "ethical": _cell(raw_row, col, "ethical"),
        "jurisdiction": _cell(raw_row, col, "jurisdiction"),
        "sector": _cell(raw_row, col, "sector"),
        "harm_indiv": _cell(raw_row, col, "harm_indiv"),
        "harm_societal": _cell(raw_row, col, "harm_societal"),
        "harm_env": _cell(raw_row, col, "harm_env"),
        "consequence": _cell(raw_row, col, "consequence"),
        "response": _cell(raw_row, col, "response"),
        "summary": _cell(raw_row, col, "summary"),
    }
    if not row["headline"] or len(row["headline"]) < 5:
        return None
    year = parse_year(row["occurred"])
    if not year or year < 1980 or year > 2030:
        return None
    if not is_security_relevant(row):
        return None

    ethical_items = split_taxonomy(row["ethical"])
    owasp_llm: set[str] = set()
    owasp_asi: set[str] = set()
    for item in ethical_items:
        owasp_llm.update(ETHICAL_TO_OWASP_LLM.get(item, []))
        owasp_asi.update(ETHICAL_TO_OWASP_ASI.get(item, []))

    h = row["headline"].lower()
    if "deepfake" in h or "voice clone" in h or "imperson" in h:
        owasp_llm.add("LLM09")
        owasp_asi.add("ASI09")
    if "prompt inject" in h or "jailbreak" in h:
        owasp_llm.add("LLM01")
        owasp_asi.add("ASI01")
    if "data leak" in h or "data breach" in h or "exfil" in h:
        owasp_llm.add("LLM02")
        owasp_asi.add("ASI03")

    affected = (row["developer"] or row["deployer"] or row["system"]).strip()
    if not affected and row["sector"]:
        affected = row["sector"]

    urls = re.findall(r"https?://[^\s,;]+", row["summary"])
    aiaaic_slug = None
    references = []
    for u in urls[:8]:
        u_clean = u.strip(",.;")
        rtype = "report" if "aiaaic.org" in u_clean else "news"
        ref_title = "AIAAIC entry" if "aiaaic.org" in u_clean else u_clean
        references.append({"title": ref_title, "url": u_clean, "type": rtype})
        if "aiaaic.org" in u_clean and "/aiaaic-repository/" in u_clean:
            slug = u_clean.rstrip("/").split("/")[-1]
            aiaaic_slug = slug

    if not references:
        slug = re.sub(r"[^a-z0-9]+", "-", row["headline"].lower()).strip("-")
        references.append({
            "title": "AIAAIC entry",
            "url": f"https://www.aiaaic.org/aiaaic-repository/ai-algorithmic-and-automation-incidents/{slug}",
            "type": "report",
        })

    description = (
        f"AIAAIC report: {row['headline']}. "
        + (f"System: {row['system']}. " if row["system"] else "")
        + (f"Technology: {row['technology']}. " if row["technology"] else "")
        + (f"Purpose: {row['purpose']}. " if row["purpose"] else "")
        + (f"Ethical issues: {row['ethical']}. " if row["ethical"] else "")
        + (f"Reported consequences: {row['consequence']}. " if row["consequence"] else "")
        + (f"Response: {row['response']}." if row["response"] else "")
    ).strip()

    tags = ["aiaaic", "aiaaic-sheet"]
    if row["sector"]:
        tags.append("sector-" + re.sub(r"\s+", "-", row["sector"].lower()))
    if row["jurisdiction"]:
        tags.append("juris-" + re.sub(r"\s+", "-", row["jurisdiction"].lower())[:24])

    return {
        "source_id": row["id"],
        "title": row["headline"][:300],
        "date": str(year),
        "year": year,
        "category": "real-world",
        "description": description[:1500],
        "attack_vector": detect_attack_vector(row),
        "affected": affected[:200],
        "severity": detect_severity(row),
        "owasp_llm": sorted(owasp_llm),
        "owasp_asi": sorted(owasp_asi),
        "mitre_atlas": [],
        "references": references,
        "tags": tags,
    }
```

- [ ] **Step 6: Update main() to build column map and pass it**

Replace the `main()` function (lines 321–337) with:

```python
def main():
    body, _ = download_csv()
    rows = list(csv.reader(io.StringIO(body)))
    print(f"[aiaaic] {len(rows)} raw rows")

    # Find the header row — it's the first row starting with "AIAAIC"
    # or containing "Headline" in any cell.
    col = None
    header_idx = 0
    for i, row in enumerate(rows[:5]):
        joined = " ".join(row).lower()
        if "headline" in joined or "aiaaic id" in joined:
            col = build_column_map(row)
            header_idx = i
            break
    if col is None:
        print("[aiaaic] ERROR: could not find header row", file=sys.stderr)
        return

    out = []
    skipped = 0
    for row in rows[header_idx + 1:]:
        norm = normalize_row(row, col)
        if norm:
            out.append(norm)
        else:
            skipped += 1

    out_path = INGEST / "aiaaic_sheet_incidents.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[aiaaic] wrote {len(out)} security-relevant entries -> {out_path} (skipped {skipped})")
```

- [ ] **Step 7: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add scripts/ingest_aiaaic_sheet.py
git commit -m "feat: AIAAIC uses conditional_fetch and header-based column parsing"
```

---

### Task 5: Update OECD AIM to use robust_fetch

**Files:**
- Modify: `scripts/ingest_oecd_aim.py`

- [ ] **Step 1: Add import for ingest_utils**

At the top of `scripts/ingest_oecd_aim.py`, after the existing imports (line 30), add:

```python
from ingest_utils import robust_fetch
```

- [ ] **Step 2: Replace fetch_page with robust_fetch**

Replace lines 114–128 (`def fetch_page()`) with:

```python
def fetch_page(url: str) -> str | None:
    slug = url.rstrip("/").split("/")[-1]
    cache_file = CACHE / f"{slug}.html"
    try:
        data = robust_fetch(
            url, cache_file, timeout=20, max_retries=3, min_cache_bytes=1000,
        )
        text = data[:800_000].decode("utf-8", errors="replace")
        return text
    except RuntimeError as e:
        print(f"  ! {slug}: {e}", file=sys.stderr)
        return None
```

This preserves the 800KB cap, the per-page caching, and the return-None-on-failure pattern — but adds retry logic via `robust_fetch`.

- [ ] **Step 3: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add scripts/ingest_oecd_aim.py
git commit -m "feat: OECD AIM uses robust_fetch for retry support"
```

---

### Task 6: Verify the full pipeline end-to-end

**Files:**
- None (verification only)

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Clear caches and verify AIRI fetches cleanly**

Delete the AIRI cache to force a fresh fetch:

Run: `python -c "from pathlib import Path; p = Path('ingest/_cache/airi-data.zip'); p.unlink(missing_ok=True); Path(str(p) + '.etag').unlink(missing_ok=True); print('cleared')" `

Then run: `python scripts/ingest_airi_navigator.py`
Expected: Should print download message and complete without errors.

- [ ] **Step 3: Run AIRI again to verify conditional fetch**

Run: `python scripts/ingest_airi_navigator.py`
Expected: Should either print "ZIP unchanged (304)" or re-download (depends on whether server supports ETag). Either way, no crash.

- [ ] **Step 4: Commit any regenerated ingest files if changed**

```bash
git add ingest/airi_navigator_incidents.json ingest/aiaaic_sheet_incidents.json
git commit -m "build: regenerate ingest outputs after pipeline hardening"
```
(Skip if no changes.)
