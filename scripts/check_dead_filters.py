#!/usr/bin/env python3
"""WS6-T5 design pass -- catch a filter control that cannot match anything.

Origin: docs/index.html shipped a "Tier" filter (`<select id="tier">` with
`landmark`/`feed` options) and docs/app.js filtered on `e.tier` -- but no
served data variant (docs/data/incidents.core.json, generated from
data/incidents.min.json) has ever carried a `tier` field. `tier` and
`quality_tier` are two different fields; only `quality_tier` reaches the
site. Selecting "landmark" returned zero rows on the live site, silently,
with no error -- the same failure SHAPE as A1-A4 in the WS6-T5 design-pass
report (a check/control that reports success while doing nothing), just on
a filter control instead of a test gate.

CORRECTED (BOUNCE #2 / D2): the first version of this script discovered
filters through a hand-maintained `FILTER_FIELD` dict of three ids. That
dict IS the hole it exists to close: reintroducing the dead Tier <select>
as markup only (exactly what a contributor adding a new dead filter does)
was measured to give `PASS, exit 0`, because nothing makes the dict grow
when the markup does. The docstring also claimed a `data-filter-field`
selector mechanism that did not exist anywhere in the tree (`git grep
data-filter-field` had exactly one hit: this docstring).

Fixed for real, not just in prose: docs/index.html now carries a literal
`data-filter-field="<incident field>"` attribute on every <select> inside
`.filters`, INCLUDING an explicit `data-filter-field="none"` opt-out on
the one select that genuinely isn't a data filter (#page_size, a
pagination control). Discovery below finds every <select id> in the
filter bar via markup, with no separate registry to fall out of sync --
a <select> with no data-filter-field attribute at all is now itself a
FAIL (can't verify it, and the missing-attribute case is exactly how a
reintroduced dead filter would look), not a silent skip.

This script has three outcomes, deliberately not conflated:

  FAIL (exit 1), unverifiable: a <select id> inside .filters has no
  data-filter-field attribute at all -- discovery cannot tell whether
  it's a real filter or a pagination-style control, so it cannot be
  cleared. This is what closes the original hole: reintroducing the
  Tier <select> markup with no attribute now fails here, immediately,
  with no dict to remember to update.

  FAIL (exit 1), dead field: the field a filter control reads is absent
  from EVERY incident in the core payload -- the Tier bug exactly: not
  "this option currently has zero matches" but "this field cannot ever
  match, structurally".

  WARN (exit 0, printed): a specific hardcoded <option value="..."> has
  zero CURRENT matches even though its field exists -- e.g. a severity
  enum value ("Info") that is part of the taxonomy but happens to have no
  incidents at this exact revision. Hard-failing on this would make the
  gate flaky against normal corpus growth/drift, which is its own
  "cannot pass reliably" failure mode -- so it's reported, not gated.

Run: python scripts/check_dead_filters.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "docs" / "index.html"
CORE_JSON = ROOT / "docs" / "data" / "incidents.core.json"


def discover_selects() -> list[tuple[str, str | None, str]]:
    """Every <select id="..."> inside the .filters bar, in document order.

    Returns (select_id, data_filter_field_or_None, inner_html) tuples.
    data_filter_field is None when the attribute is missing entirely
    (the unverifiable/FAIL case), and the literal string "none" is a
    legitimate, explicit non-filter opt-out (e.g. #page_size).
    """
    html = INDEX_HTML.read_text(encoding="utf-8")
    # The filter bar isn't a single balanced regex-friendly block (nested
    # divs), so instead of trying to match its closing tag, anchor on the
    # opening tag and the immediately-following chips container, which is
    # always the next sibling section in docs/index.html.
    start = html.index('<div class="filters"')
    end = html.index('id="filter-chips"', start)
    filters_html = html[start:end]
    # Strip HTML comments first: a comment that happens to mention the
    # literal text "<select>" (as explanatory prose about this very
    # mechanism, for instance) would otherwise be matched as a real
    # opening tag by the naive regex below, and its non-greedy content
    # group would then swallow the REAL next <select>...</select> as its
    # own body -- silently dropping that select from discovery. Caught by
    # this script's own self-test during the BOUNCE #2 / D2 fix.
    filters_html = re.sub(r'<!--.*?-->', '', filters_html, flags=re.S)

    selects = []
    for sel_m in re.finditer(r'<select\b([^>]*)>(.*?)</select>', filters_html, re.S):
        attrs, inner = sel_m.group(1), sel_m.group(2)
        id_m = re.search(r'id="([^"]*)"', attrs)
        if not id_m:
            continue  # can't identify it; nothing meaningful to check
        field_m = re.search(r'data-filter-field="([^"]*)"', attrs)
        field = field_m.group(1) if field_m else None
        selects.append((id_m.group(1), field, inner))
    return selects


def extract_options(inner_html: str) -> list[str]:
    # Two markup forms in this file: `<option value="x">x</option>`
    # (corpus, quality) and `<option>Text</option>` with no `value`
    # attribute, where the element's own text IS the option's value per
    # the HTML spec (severity). Handle both; the empty `value=""` "all"
    # sentinel is dropped either way since it never has meaningful inner
    # text either. Dynamically-populated selects (year/llm/asi/vector)
    # have no static <option>s beyond that sentinel, so this naturally
    # returns [] for them -- nothing to check, which is correct: their
    # options come from populateOptions() in app.js, straight out of the
    # loaded data, so they cannot go stale independently of it.
    opts = []
    for opt_match in re.finditer(r'<option([^>]*)>([^<]*)</option>', inner_html):
        attrs, text = opt_match.group(1), opt_match.group(2).strip()
        value_m = re.search(r'value="([^"]*)"', attrs)
        value = value_m.group(1) if value_m else text
        if value:
            opts.append(value)
    return opts


def main() -> int:
    if not CORE_JSON.exists():
        print(f"::error::{CORE_JSON} not found -- run `make docs-data` first", file=sys.stderr)
        return 1

    payload = json.loads(CORE_JSON.read_text(encoding="utf-8"))
    incidents = payload["incidents"]

    selects = discover_selects()
    if not selects:
        print("::error::no <select> elements found inside .filters -- discovery is broken", file=sys.stderr)
        return 1

    failed = False
    warned = False
    for select_id, field, inner in selects:
        if field is None:
            print(
                f"::error::#{select_id} is a <select> inside .filters with no "
                f"data-filter-field attribute -- cannot verify it, and an unannotated "
                f"select is exactly how a reintroduced dead filter looks. Add "
                f"data-filter-field=\"<incident field>\", or =\"none\" if it isn't a "
                f"data filter (see #page_size)."
            )
            failed = True
            continue
        if field == "none":
            print(f"[dead-filters] #{select_id}: explicitly not a data filter (data-filter-field=\"none\") -- skipped")
            continue

        options = extract_options(inner)
        field_values = set()
        for e in incidents:
            v = e.get(field)
            if v is None:
                continue
            # LLM/ASI/etc. filter on membership in a list field (owasp_llm,
            # owasp_asi); everything else is a scalar equality filter
            # (severity, corpus, quality_tier, attack_vector, year).
            if isinstance(v, list):
                field_values.update(v)
            else:
                field_values.add(v)
        field_present = any(field in e for e in incidents)

        if not field_present:
            print(
                f"::error::filter #{select_id} reads field `{field}`, which is absent from "
                f"EVERY incident in {CORE_JSON.relative_to(ROOT)} -- this control cannot ever "
                f"match anything (the Tier-filter defect class)"
            )
            failed = True
            continue

        if not options:
            print(f"[dead-filters] #{select_id} ({field}): dynamically populated from loaded data -- OK")
            continue

        dead = [o for o in options if o not in field_values]
        if dead:
            print(
                f"::warning::filter #{select_id} option(s) {dead} currently match 0 incidents "
                f"(field `{field}` exists; these specific values just have no current rows)"
            )
            warned = True
        else:
            print(f"[dead-filters] #{select_id} ({field}): all {len(options)} option(s) have matches -- OK")

    if failed:
        print("\n::error::dead filter control(s) found -- see above")
        return 1
    print(f"\n[dead-filters] PASS -- {len(selects)} select(s) discovered{' (with warnings above)' if warned else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
