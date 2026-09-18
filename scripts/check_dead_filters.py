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

This script has two severities, deliberately not conflated:

  FAIL (exit 1): the FIELD a filter control reads (`select[data-filter-field]`
  in docs/index.html) is absent from EVERY incident in the core payload --
  this is the Tier bug exactly: not "this option currently has zero
  matches" but "this field cannot ever match, structurally". This is the
  check the coordinator asked for.

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

# Filter <select> id -> incident field it filters on (docs/app.js `matches()`).
# Only the ones with a STATIC, hardcoded <option> list are checkable here --
# year/llm/asi/vector are populated by app.js directly from the loaded data
# (populateOptions()), so they cannot go stale independently of the data.
FILTER_FIELD = {
    "severity": "severity",
    "corpus": "corpus",
    "quality": "quality_tier",
}


def extract_options(select_id: str) -> list[str]:
    m = re.search(
        rf'<select id="{re.escape(select_id)}">(.*?)</select>',
        INDEX_HTML.read_text(encoding="utf-8"),
        re.S,
    )
    if not m:
        raise SystemExit(f"::error::no <select id=\"{select_id}\"> found in docs/index.html")
    # Two markup forms in this file: `<option value="x">x</option>` (corpus,
    # quality) and `<option>Text</option>` with no `value` attribute, where
    # the element's own text IS the option's value per the HTML spec
    # (severity). Handle both; the empty `value=""` "all" sentinel is
    # dropped either way since it never has meaningful inner text either.
    opts = []
    for opt_match in re.finditer(r'<option([^>]*)>([^<]*)</option>', m.group(1)):
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

    failed = False
    warned = False
    for select_id, field in FILTER_FIELD.items():
        options = extract_options(select_id)
        field_values = {e[field] for e in incidents if field in e and e[field] is not None}
        field_present = any(field in e for e in incidents)

        if not field_present:
            print(
                f"::error::filter #{select_id} reads field `{field}`, which is absent from "
                f"EVERY incident in {CORE_JSON.relative_to(ROOT)} -- this control cannot ever "
                f"match anything (the Tier-filter defect class)"
            )
            failed = True
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
    print(f"\n[dead-filters] PASS{' (with warnings above)' if warned else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
