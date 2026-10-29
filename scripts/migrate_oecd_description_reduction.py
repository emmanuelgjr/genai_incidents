"""
One-off migration: retroactively apply the OECD AIM narrative-description
reduction (docs/audits/E21-oecd-narrative-licence-2026-07-30.md, outcome (B))
to the already-committed OECD ingest snapshot(s), so the fix reaches every
row already fetched -- including the 40 rows that have aged out of OECD's
own sitemap and can never be re-fetched again by the normal ingest path --
without a costly, CI-infeasible full re-ingest (E21 §5.4: the live sitemap
holds 10,000 incident URLs, ``ingest/_cache/oecd_aim/`` is empty and
gitignored, and a cold OECD_AIM_LIMIT=0 pass has a ~167-minute floor against
the 65-minute OECD fetch step timeout in ``auto-refresh.yml``'s ``oecd-fetch`` job; 60 minutes when this was written).

For each row in each target file:
  1. captures the row's CURRENT (pre-reduction) ``description`` as the
     corpus-classification seed -- exactly the text
     ``merge_and_dedupe.py``'s ``_classify_corpus()`` would have read this
     build if nothing changed, so the persisted ``corpus`` is byte-identical
     to what would have shipped anyway (0 unintended moves; see
     ``ingest_oecd_aim.py::classify_corpus_signal()``'s own docstring);
  2. persists ``corpus`` from that seed;
  2b. if the row's ``attack_vector`` is "other", also re-runs the SAME
     title+narrative reclassification ``merge_and_dedupe.py``'s own
     normalize_entry()/step-4b finalize would otherwise perform against the
     (about-to-be-reduced) ``description`` -- an independent cascade found
     by dry-running this migration once and diffing: reducing `description`
     first regressed 178/4160 rows' `attack_vector` back to "other" (and
     rippled into owasp_llm/owasp_asi/nist_ai_rmf/mitre_atlas via
     fill_taxonomy()). Same fix as `corpus`: seed from the pre-reduction
     text, persist a definitive value, so merge_and_dedupe's own
     reclassify-if-"other" guards never fire post-migration. See
     ``ingest_oecd_aim.py::reclassify_attack_vector_from_narrative()``;
  3. overwrites ``description`` with the same structural template the
     ingest-time fix now produces.

Both the classifier and the template builder are IMPORTED from
``ingest_oecd_aim.py`` (gate advisory, E21 §5.4/§5.6-adjacent) rather than
reimplemented here, so the retroactive path and the forward-fetch path can
never structurally diverge.

Pure transform of a committed ``ingest/*.json`` artifact -- no network call,
no model call, no touch to any ``data/*.json`` output (those are build
artifacts, never hand-edited; ``ingest/*.json`` files are inputs, and this
script plays the same role an ingest script's own output normally would).
Run once, by hand, outside ``make build``:

    python scripts/migrate_oecd_description_reduction.py [path...]

Defaults to ``ingest/oecd_aim_full_incidents.json`` if no path is given.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ingest_oecd_aim import (  # noqa: E402
    build_description,
    classify_corpus_signal,
    reclassify_attack_vector_from_narrative,
)

DEFAULT_TARGETS = [ROOT / "ingest" / "oecd_aim_full_incidents.json"]


def migrate_file(path: Path) -> dict:
    rows = json.loads(path.read_text(encoding="utf-8"))
    stats = {
        "rows": len(rows),
        "corpus_security": 0,
        "corpus_ai_harm": 0,
        "attack_vector_rescued_from_other": 0,
        "description_changed": 0,
        "description_unchanged": 0,
    }
    for row in rows:
        title = row.get("title") or ""
        old_description = row.get("description") or ""
        tags = row.get("tags") or []

        # Step 1+2: seed from the CURRENT (pre-reduction) description, then
        # persist only the derived signal.
        corpus = classify_corpus_signal(title, old_description, tags)
        row["corpus"] = corpus
        stats["corpus_security" if corpus == "security" else "corpus_ai_harm"] += 1

        # Step 2b: rescue an "other" attack_vector the same way, before the
        # narrative signal it depends on is gone.
        old_attack_vector = row.get("attack_vector") or "other"
        new_attack_vector = reclassify_attack_vector_from_narrative(
            old_attack_vector, title, old_description
        )
        if new_attack_vector != old_attack_vector:
            stats["attack_vector_rescued_from_other"] += 1
            row["attack_vector"] = new_attack_vector

        # Step 3: overwrite description with the structural template.
        source_id = row.get("source_id") or ""
        date = row.get("date") or ""
        refs = row.get("references") or []
        url = refs[0].get("url", "") if refs and isinstance(refs[0], dict) else ""
        affected = row.get("affected") or ""
        attack_vector = row.get("attack_vector") or ""
        new_description = build_description(source_id, date, url, affected, attack_vector)
        if new_description != old_description:
            stats["description_changed"] += 1
        else:
            stats["description_unchanged"] += 1
        row["description"] = new_description

    path.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return stats


def main() -> None:
    targets = [Path(p) for p in sys.argv[1:]] or DEFAULT_TARGETS
    for path in targets:
        if not path.exists():
            print(f"[migrate-oecd] {path}: not found, skipping")
            continue
        stats = migrate_file(path)
        print(f"[migrate-oecd] {path.relative_to(ROOT)}: {stats}")


if __name__ == "__main__":
    main()
