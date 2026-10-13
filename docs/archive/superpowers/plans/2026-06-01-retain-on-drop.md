# Retain-on-drop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the pipeline from silently dropping incidents when an upstream source (notably the OECD AIM sliding-window fetch) stops returning them.

**Architecture:** Two complementary changes. (A) The OECD ingester unions its fresh fetch into the committed ingest file instead of overwriting, so nothing ages out of the 3,000-URL window. (B) `merge_and_dedupe.py` re-feeds previously-published incidents (minus explicitly deprecated ids) back into the build as inputs, so the existing dedup machinery either merges them with fresh data or lets them survive — a general backstop for any source.

**Tech Stack:** Python 3.12, pytest. Scripts importable via `tests/conftest.py` (which puts `scripts/` on `sys.path`, so `import merge_and_dedupe as m` and `import ingest_oecd_aim as o` work).

**Determinism constraint:** The build must rebuild byte-identically across UTC days (CI drift check). Retained entries carry unchanged content, so their `_content_snapshot` matches the previous output and `_apply_history` preserves `updated` — no spurious bump. Tested explicitly in Task 5.

---

## File structure

- `scripts/ingest_oecd_aim.py` — add pure `union_with_existing()`; call it in `main()` before writing.
- `scripts/merge_and_dedupe.py` — add pure `_load_prev_incidents()`, `_load_deprecated_ids()`, `load_retained_priors()`; add "step 2b" in `main()` that re-feeds retained priors into `all_entries`.
- `tests/test_ingest_oecd_aim.py` — NEW: unit tests for `union_with_existing`.
- `tests/test_merge_and_dedupe.py` — add unit tests for `load_retained_priors` and an end-to-end retention + determinism test driving `main()` in a tmp dir.

---

## Task 1: OECD ingester — `union_with_existing` helper (pure function + test)

**Files:**
- Modify: `scripts/ingest_oecd_aim.py` (add function above `def main()`, ~line 271)
- Test: `tests/test_ingest_oecd_aim.py` (new)

- [ ] **Step 1: Write the failing test**

Create `tests/test_ingest_oecd_aim.py`:

```python
"""Unit tests for the OECD AIM ingester's union-with-existing behaviour."""

from __future__ import annotations

import ingest_oecd_aim as o


def _entry(sid, title):
    return {"source_id": sid, "title": title, "year": 2026,
            "references": [{"url": "https://oecd.ai/en/incidents/x"}]}


def test_union_keeps_aged_out_existing_entries():
    # Fresh fetch lost OLD-2 (it aged out of the 3000-URL window).
    fresh = [_entry("OECD-AIM-NEW-1", "new one")]
    existing = [_entry("OECD-AIM-OLD-2", "old two")]
    out = o.union_with_existing(fresh, existing)
    ids = {e["source_id"] for e in out}
    assert ids == {"OECD-AIM-NEW-1", "OECD-AIM-OLD-2"}


def test_union_fresh_wins_on_conflict():
    fresh = [_entry("OECD-AIM-1", "fresh title")]
    existing = [_entry("OECD-AIM-1", "stale title")]
    out = o.union_with_existing(fresh, existing)
    assert len(out) == 1
    assert out[0]["title"] == "fresh title"


def test_union_output_sorted_by_source_id():
    fresh = [_entry("OECD-AIM-3", "c"), _entry("OECD-AIM-1", "a")]
    existing = [_entry("OECD-AIM-2", "b")]
    out = o.union_with_existing(fresh, existing)
    assert [e["source_id"] for e in out] == [
        "OECD-AIM-1", "OECD-AIM-2", "OECD-AIM-3"
    ]


def test_union_drops_entries_without_source_id():
    fresh = [{"title": "no id", "references": []}]
    existing = []
    assert o.union_with_existing(fresh, existing) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ingest_oecd_aim.py -v`
Expected: FAIL — `AttributeError: module 'ingest_oecd_aim' has no attribute 'union_with_existing'`

- [ ] **Step 3: Add the helper**

In `scripts/ingest_oecd_aim.py`, insert this function immediately above `def main():` (currently ~line 271):

```python
def union_with_existing(fresh: list[dict], existing: list[dict]) -> list[dict]:
    """Union the fresh fetch with the previously-committed ingest file so the
    OECD corpus only ever grows. Keyed by ``source_id`` (``OECD-AIM-<id>``):
    fresh wins on conflict (latest content); entries present only in
    ``existing`` (aged out of the newest-N sitemap window) are kept. Output is
    sorted by ``source_id`` so the committed file has stable, deterministic
    ordering."""
    by_id: dict[str, dict] = {}
    for e in existing:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    for e in fresh:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    return sorted(by_id.values(), key=lambda e: e.get("source_id") or "")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ingest_oecd_aim.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/ingest_oecd_aim.py tests/test_ingest_oecd_aim.py
git commit -m "feat(ingest): add union_with_existing helper for OECD AIM"
```

---

## Task 2: OECD ingester — wire union into `main()`

**Files:**
- Modify: `scripts/ingest_oecd_aim.py` — the write block at the end of `main()` (currently lines ~320-322)

- [ ] **Step 1: Replace the overwrite with a union-then-write**

In `scripts/ingest_oecd_aim.py`, the current tail of `main()` reads:

```python
    out_path = INGEST / "oecd_aim_full_incidents.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[aim] wrote -> {out_path}")
```

Replace it with:

```python
    out_path = INGEST / "oecd_aim_full_incidents.json"
    existing: list[dict] = []
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, OSError):
            existing = []
    merged = union_with_existing(out, existing)
    print(
        f"[aim] union: {len(out)} fetched + {len(existing)} existing "
        f"-> {len(merged)} retained"
    )
    out_path.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[aim] wrote -> {out_path}")
```

(The trailing newline matches the merge/render writers, which use `newline="\n"` plus a final newline, keeping the committed file POSIX-clean.)

- [ ] **Step 2: Sanity-check the module still imports and tests pass**

Run: `python -c "import sys; sys.path.insert(0,'scripts'); import ingest_oecd_aim"`
Expected: no output, exit 0.

Run: `python -m pytest tests/test_ingest_oecd_aim.py -v`
Expected: PASS (4 passed).

- [ ] **Step 3: Commit**

```bash
git add scripts/ingest_oecd_aim.py
git commit -m "feat(ingest): OECD AIM unions fetch into committed file (no more aging-out)"
```

---

## Task 3: Build retention — pure helpers (`load_retained_priors`, loaders) + tests

**Files:**
- Modify: `scripts/merge_and_dedupe.py` — add three helpers near `_load_prev_state` (~line 645-728)
- Test: `tests/test_merge_and_dedupe.py` — add unit tests

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_merge_and_dedupe.py`:

```python
def test_load_retained_priors_excludes_deprecated():
    prev = [
        {"id": "INC-00001", "title": "kept"},
        {"id": "INC-00002", "title": "deprecated"},
    ]
    out = m.load_retained_priors(prev, {"INC-00002"})
    assert [e["id"] for e in out] == ["INC-00001"]


def test_load_retained_priors_keeps_all_when_none_deprecated():
    prev = [{"id": "INC-00001"}, {"id": "INC-00002"}]
    out = m.load_retained_priors(prev, set())
    assert len(out) == 2


def test_load_retained_priors_skips_entries_without_id():
    prev = [{"title": "no id"}, {"id": "INC-00003", "title": "ok"}]
    out = m.load_retained_priors(prev, set())
    assert [e["id"] for e in out] == ["INC-00003"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_merge_and_dedupe.py -k load_retained_priors -v`
Expected: FAIL — `AttributeError: module 'merge_and_dedupe' has no attribute 'load_retained_priors'`

- [ ] **Step 3: Add the helpers**

In `scripts/merge_and_dedupe.py`, immediately after the `_load_curation_overrides()` function (ends ~line 664, just before `def _load_prev_state(`), add:

```python
def _load_prev_incidents() -> list[dict]:
    """Read the previously-published incidents list (empty if none yet)."""
    prev_path = DATA / "incidents.json"
    if not prev_path.exists():
        return []
    try:
        return json.loads(prev_path.read_text(encoding="utf-8")).get("incidents", [])
    except (json.JSONDecodeError, OSError):
        return []


def _load_deprecated_ids() -> set[str]:
    """Ids that were explicitly retired via merge/dedupe. These must never be
    resurrected by retention."""
    if not DEPRECATIONS_PATH.exists():
        return set()
    try:
        deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    return {d.get("from") for d in deprec.get("deprecations", []) if d.get("from")}


def load_retained_priors(
    prev_incidents: list[dict], deprecated_ids: set[str]
) -> list[dict]:
    """Select previously-published incidents to carry forward into the build.

    Every prior incident is re-fed as a build input EXCEPT those whose id was
    explicitly deprecated (merged away). When re-run through dedupe, a prior
    that still has a live source merges into the fresh entry; a prior with no
    live source survives on its own — so the dataset never silently drops an
    incident just because an upstream feed stopped returning it."""
    out: list[dict] = []
    for e in prev_incidents:
        eid = e.get("id")
        if not eid or eid in deprecated_ids:
            continue
        out.append(e)
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_merge_and_dedupe.py -k load_retained_priors -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_and_dedupe.py tests/test_merge_and_dedupe.py
git commit -m "feat(merge): add retention helpers (load_retained_priors)"
```

---

## Task 4: Build retention — wire retention into `merge_and_dedupe.main()`

> **Revised during implementation.** The "step 2b re-feed before dedupe"
> approach below proved non-idempotent and exposed a latent dedupe bug (it
> dropped 17 CVEs). It was reworked as a **post-build top-up (step 6c)** that
> appends only uncovered priors *after* dedupe, verbatim. See the updated
> `docs/superpowers/specs/2026-06-01-retain-on-drop-design.md` (Part B) and the
> follow-up `docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md`.
>
> **The "step 2b" code block below is the ORIGINAL (superseded) approach,
> retained only for history. The shipped implementation is the step-6c
> post-build top-up described in the spec — do not implement the block below.**

**Files:**
- Modify: `scripts/merge_and_dedupe.py` — `main()`, immediately after the ingest-loading loop (currently ends ~line 814, the `print(f"[{src.name:40s}] ...")` line)

- [ ] **Step 1: Insert the retention step**

In `scripts/merge_and_dedupe.py`, find the end of step 2 in `main()`:

```python
    # 2) Each ingest/*.json (from subagents)
    if INGEST.exists():
        for src in sorted(INGEST.glob("*.json")):
            raw = load_source(src)
            kept = []
            for r in raw:
                norm = normalize_entry(r)
                if norm is not None:
                    kept.append(norm)
            all_entries.extend(kept)
            print(f"[{src.name:40s}] {len(raw):4d} raw -> {len(kept):4d} normalized")
```

Directly AFTER that block (before "# 3) Dedupe"), insert:

```python
    # 2b) Retention backstop: re-feed previously-published incidents (minus
    #     explicitly deprecated ids) as build inputs. Appended AFTER the ingest
    #     feeds so a prior that still has a live source merges INTO the fresh
    #     entry (fresh content wins); a prior with no live source survives.
    #     This makes the dataset archival — no source dropping an entry can
    #     silently delete it. See docs/superpowers/specs/2026-06-01-retain-on-drop-design.md
    prev_incidents = _load_prev_incidents()
    retained = load_retained_priors(prev_incidents, _load_deprecated_ids())
    kept_prior = []
    for r in retained:
        norm = normalize_entry(r)
        if norm is not None:
            kept_prior.append(norm)
    all_entries.extend(kept_prior)
    print(f"[retention] re-fed {len(kept_prior)} prior incident(s) as inputs")
```

- [ ] **Step 2: Verify the module imports**

Run: `python -c "import sys; sys.path.insert(0,'scripts'); import merge_and_dedupe"`
Expected: no output, exit 0.

- [ ] **Step 3: Run the existing merge unit tests (no regressions)**

Run: `python -m pytest tests/test_merge_and_dedupe.py -v`
Expected: PASS (all existing + the 3 new helper tests).

- [ ] **Step 4: Commit**

```bash
git add scripts/merge_and_dedupe.py
git commit -m "feat(merge): retention step re-feeds prior incidents into build"
```

---

## Task 5: End-to-end retention + determinism test

**Files:**
- Test: `tests/test_merge_and_dedupe.py` — add an end-to-end test that drives `main()` against a temp `data/` + `ingest/`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_and_dedupe.py`:

```python
import datetime
import json as _json
from pathlib import Path as _Path


class _FrozenDate(datetime.date):
    """date subclass whose today() is pinned, for cross-day determinism tests."""
    _pinned = datetime.date(2099, 6, 1)

    @classmethod
    def today(cls):
        return cls._pinned


def _oecd_entry(sid, title):
    return {
        "source_id": sid,
        "title": title,
        "description": "A description long enough to pass the minimum length filter.",
        "year": 2026,
        "date": "2026-04-01",
        "attack_vector": "deepfake",
        "severity": "High",
        "references": [{"url": f"https://oecd.ai/en/incidents/{sid}"}],
        "tags": ["oecd-aim"],
    }


def _setup_tmp_repo(tmp_path, monkeypatch):
    data = tmp_path / "data"
    ingest = tmp_path / "ingest"
    data.mkdir()
    ingest.mkdir()
    monkeypatch.setattr(m, "DATA", data)
    monkeypatch.setattr(m, "INGEST", ingest)
    monkeypatch.setattr(m, "DEPRECATIONS_PATH", data / "id_deprecations.json")
    monkeypatch.setattr(m, "CURATION_OVERRIDES_PATH", data / "curation_overrides.json")
    return data, ingest


def test_retention_keeps_dropped_incident_with_stable_id(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)

    # First build: source emits two incidents.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")
    m.main()
    first = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    id_by_src = {
        s: e["id"] for e in first["incidents"] for s in e["source_ids"]
    }
    assert {"OECD-AIM-A", "OECD-AIM-B"} <= set(id_by_src)
    b_id = id_by_src["OECD-AIM-B"]

    # Second build: source dropped incident B (aged out / removed upstream).
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A")]
    ), encoding="utf-8")
    m.main()
    second = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    src_ids_second = {s for e in second["incidents"] for s in e["source_ids"]}

    # B is retained, with the SAME id it had before.
    assert "OECD-AIM-B" in src_ids_second, "dropped incident must be retained"
    b_id_second = next(
        e["id"] for e in second["incidents"] if "OECD-AIM-B" in e["source_ids"]
    )
    assert b_id_second == b_id


def test_deprecated_id_is_not_resurrected(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    # Prior output contains INC-09999, which is recorded as deprecated.
    (data / "incidents.json").write_text(_json.dumps({
        "incidents": [{
            **m.normalize_entry(_oecd_entry("OECD-AIM-DEAD", "Dead dup")),
            "id": "INC-09999", "added": "2026-01-01", "updated": "2026-01-01",
        }]
    }), encoding="utf-8")
    (data / "id_deprecations.json").write_text(_json.dumps({
        "deprecations": [{"from": "INC-09999", "into": "INC-00001",
                          "reason": "merged", "date": "2026-01-01"}]
    }), encoding="utf-8")
    # Current ingest has one live incident.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-LIVE", "Live incident")]
    ), encoding="utf-8")
    m.main()
    out = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    src_ids = {s for e in out["incidents"] for s in e["source_ids"]}
    assert "OECD-AIM-DEAD" not in src_ids, "deprecated entry must not be resurrected"


def test_build_is_deterministic_across_days(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")

    # Build on "day 1".
    monkeypatch.setattr(m, "date", _FrozenDate)
    _FrozenDate._pinned = datetime.date(2099, 6, 1)
    m.main()
    day1 = (data / "incidents.json").read_text(encoding="utf-8")

    # Rebuild on a LATER calendar day with identical inputs.
    _FrozenDate._pinned = datetime.date(2099, 6, 2)
    m.main()
    day2 = (data / "incidents.json").read_text(encoding="utf-8")

    assert day1 == day2, "rebuild on a later UTC day must be byte-identical"
```

- [ ] **Step 2: Run the test to verify it passes**

Run: `python -m pytest tests/test_merge_and_dedupe.py -k "retention or deprecated or deterministic" -v`
Expected: PASS (3 passed). If `test_build_is_deterministic_across_days` fails, a content field is being finalized after `_apply_history` snapshots it — re-examine step ordering in `main()` (steps 4b/4c/4d must run before step 5).

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest tests -q`
Expected: all green.

- [ ] **Step 4: Commit**

```bash
git add tests/test_merge_and_dedupe.py
git commit -m "test(merge): end-to-end retention, deprecation, and cross-day determinism"
```

---

## Task 6: Validate against real data (PR #18 scenario) + full rebuild

**Files:** none (verification only).

- [ ] **Step 1: Record the current real incident count**

Run:
```bash
python -c "import json;d=json.load(open('data/incidents.json',encoding='utf-8'));print('before:',d['incident_count'])"
```
Expected: prints `before: 7725` (or current count on main).

- [ ] **Step 2: Full rebuild with retention active**

Run:
```bash
python scripts/parse_existing.py
python scripts/merge_and_dedupe.py
python scripts/render_markdown.py
python scripts/validate.py
```
Expected: `validate.py` exits 0. The `[retention] re-fed N prior incident(s)` line prints N ≈ the prior count.

- [ ] **Step 3: Confirm no incidents were lost**

Run:
```bash
python -c "import json;d=json.load(open('data/incidents.json',encoding='utf-8'));print('after:',d['incident_count'])"
```
Expected: `after:` count is >= the `before:` count (retention never shrinks the dataset on a no-new-source rebuild).

- [ ] **Step 4: Confirm idempotency (consecutive builds are identical)**

Snapshot the current output, rebuild, and diff the two consecutive builds
against each other (NOT against committed `main` — a one-time diff vs. `main`
is expected and is the actual fix):
```bash
cp data/incidents.json /tmp/inc_run1.json
python scripts/merge_and_dedupe.py
python -c "import sys;a=open('/tmp/inc_run1.json',encoding='utf-8').read();b=open('data/incidents.json',encoding='utf-8').read();print('IDEMPOTENT' if a==b else 'DRIFT');sys.exit(0 if a==b else 1)"
```
Expected: prints `IDEMPOTENT`, exit 0 — the first rebuild already reached the fixed point.

- [ ] **Step 5: Run the full test suite once more**

Run: `python -m pytest tests -q`
Expected: all green.

- [ ] **Step 6: Commit the regenerated data outputs**

```bash
git add data/incidents.json data/incidents.min.json data/id_deprecations.json INCIDENTS.md docs/
git commit -m "chore(data): rebuild outputs with retention active"
```

(If `git status` shows no changes here because retention produced no net difference on current `main`, skip this commit — note that in the PR description.)

---

## Rollout (after all tasks pass)

1. Push `retain-on-drop`, open a PR, `gh pr checks --watch` until green, squash-merge, pull `main` (per `working-style-pr-cadence`).
2. Close stale refresh PR #18 (its branch predates this change) and re-run the **Weekly auto-refresh** workflow so the next refresh PR is built on the retentive pipeline.
3. Future follow-up (separate PR, not now): `source_status` / `last_seen` provenance field to distinguish live-in-feed vs. retained-but-dropped.
