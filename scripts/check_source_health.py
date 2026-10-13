"""Track per-source consecutive-failure counts across weekly refreshes and
turn a persistently-dead ingest into a loud, unmissable signal instead of a
per-run ``::warning::`` that nobody reads.

Why this exists (WS4-T9): ``auto-refresh.yml`` runs every ingest step with
``continue-on-error: true`` so one flaky source doesn't block the others, and
only aborts the whole job if ALL of them fail on the SAME run. A single
source that 404s every week forever is invisible to that logic — the job
keeps reporting overall ``success`` while one source silently rots. See
MASTER_IMPROVEMENT_PLAN.md WS4-T9 for the AIRI Navigator instance of this
pattern; this module is the general fix.

State is persisted (committed to the repo, alongside the ingest/*.json
snapshots it watches over) at ``ingest/_state/source_health.json`` — a
subdirectory of ``ingest/`` so it is invisible to
``merge_and_dedupe.py``'s ``INGEST.glob("*.json")`` (non-recursive: it only
matches direct children of ``ingest/``, never ``ingest/_state/*``).

A source can be deliberately silenced past the threshold by hand-editing its
entry in the state file to add ``"paused": true``, a non-empty
``"paused_reason"``, and a ``"paused_until"`` (ISO date) — a visible,
git-blamed, auditable, TIME-BOXED override for a source under active
triage/remediation, not a silent bypass. This is not "never hand-edit" data
(it is pipeline health state, not corpus data); the override is required to
say *why* and *until when* in the same commit that pauses it. All three are
mandatory: ``"paused": true`` with a missing/empty reason, a missing
``paused_until``, or a ``paused_until`` that has already passed is an
INVALID or EXPIRED pause and is deliberately NOT honored — the source goes
back to failing loudly, exactly like an un-paused one, until someone renews
the pause with a fresh reason and date. A silence switch nobody has to
re-justify is indistinguishable from the ``::warning::`` this task exists to
abolish.

``paused_until`` is parsed as a strict, zero-padded ``YYYY-MM-DD`` date, not
compared as a raw string: a raw-string compare fails open, because a
malformed value like the dropped-zero typo ``"2026-7-1"`` (or ``"forever"``,
``"TBD"``, or any other non-date text) sorts as a STRING greater than a
correctly-formatted "today" and was, before this fix, wrongly treated as an
unexpired pause forever. Anything that doesn't parse as a canonical
``YYYY-MM-DD`` date is ``"invalid"`` — not honored. A pause is also capped
at ``MAX_PAUSE_HORIZON_DAYS`` days out from today (see that constant below):
a validly-formatted but absurdly-far-future date (``"9999-12-31"``) is a
permanent silence wearing a time-box costume, and is likewise rejected as
``"invalid"`` so it must be periodically re-justified instead.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = ROOT / "ingest" / "_state" / "source_health.json"
DEFAULT_THRESHOLD = 3  # consecutive failed refreshes before a source goes "stale"
NOT_ATTEMPTED = "not-attempted"  # D95: passed by the workflow for a gated, deliberately skipped step
# D108 (2026-10-13): sources retired by user ruling. A retired source is never
# attempted, never counted, and never alerts; its ingest file and provenance
# stay in the build unchanged (never delete entries). This is CODE, not state:
# the live counters are restored from the `refresh-state` branch each run, and
# update_source_health() stamps `status: retired` over whatever that copy says,
# so no one has to hand-edit that branch. To revive a source, remove it here.
RETIRED_SOURCES: dict[str, dict[str, str]] = {
    "airi_navigator": {
        "retired_on": "2026-10-13",
        "retired_reason": (
            "D108: www.airi-navigator.com has returned 404 since 2026-05-31; "
            "source retired, existing rows retained; revisit only if the site returns"
        ),
    },
}
MAX_PAUSE_HORIZON_DAYS = 180  # ~6 months; a pause can't be dated further out
# than this from "today" without renewal — see pause_status()'s docstring.


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_strict_iso_date(value: str) -> date | None:
    """Parse ``value`` as a canonical, zero-padded ``YYYY-MM-DD`` date, or
    return ``None`` if it isn't one.

    Deliberately stricter than bare ``datetime.strptime(..., "%Y-%m-%d")``:
    that alone still accepts unpadded values like ``"2026-7-1"`` (Python's
    strptime treats ``%m``/``%d`` as 1-or-2 digits), so a round-trip
    re-format check is required to reject a dropped-zero typo instead of
    silently parsing it to *some* date. This is the fix for the fail-open
    where such a value sorted as a STRING greater than today's ISO date and
    was wrongly treated as an unexpired pause.
    """
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
    if parsed.strftime("%Y-%m-%d") != value:
        return None
    return parsed


def pause_status(entry: dict, today: str) -> str:
    """Classify a source's pause request. Returns one of:

    ``"none"``      — not paused, nothing to honor.
    ``"active"``     — paused, with a reason and an unexpired, sane
                        ``paused_until``.
    ``"invalid"``    — ``paused: true`` but missing/empty reason or expiry;
                        or ``paused_until`` doesn't parse as a canonical
                        ``YYYY-MM-DD`` date (dropped-zero typos like
                        ``"2026-7-1"``, non-dates like ``"forever"`` /
                        ``"TBD"``); or ``paused_until`` is more than
                        ``MAX_PAUSE_HORIZON_DAYS`` days out from ``today``
                        (a pause that far out is effectively permanent and
                        must be re-justified periodically instead).
    ``"expired"``    — otherwise-valid pause whose ``paused_until`` has passed.

    Only ``"active"`` silences the loud-failure gate. ``"invalid"`` and
    ``"expired"`` are surfaced as errors, not silently ignored, so a stale
    or malformed pause can't hide a source forever.
    """
    if not entry.get("paused"):
        return "none"
    reason = (entry.get("paused_reason") or "").strip()
    until_raw = (entry.get("paused_until") or "").strip()
    if not reason or not until_raw:
        return "invalid"

    until = _parse_strict_iso_date(until_raw)
    today_d = _parse_strict_iso_date(today)
    if until is None or today_d is None:
        return "invalid"
    if until < today_d:
        return "expired"
    if (until - today_d).days > MAX_PAUSE_HORIZON_DAYS:
        return "invalid"
    return "active"


def update_source_health(
    state: dict,
    outcomes: dict[str, str],
    *,
    today: str,
    threshold: int = DEFAULT_THRESHOLD,
) -> tuple[dict, list[str], list[str], dict[str, str]]:
    """Apply this run's per-source outcomes to ``state``.

    Returns ``(new_state, stale_sources, degraded_sources, pause_notices)``:

    - ``stale_sources``: sources at/above ``threshold`` consecutive failures
      whose pause (if any) is NOT ``"active"`` (see :func:`pause_status`) —
      the "fail loudly" case.
    - ``degraded_sources``: failed this run, below threshold — still just a
      warning.
    - ``pause_notices``: ``{source: pause_status}`` for every stale source
      whose pause status is ``"active"``, ``"invalid"``, or ``"expired"`` —
      so callers can report *why* a stale source did or didn't trip the gate.

    ``state`` is not mutated in place; a new dict is returned so callers can
    diff old vs. new easily in tests.
    """
    new_state: dict = {k: dict(v) for k, v in state.items()}
    stale: list[str] = []
    degraded: list[str] = []
    pause_notices: dict[str, str] = {}

    for source, outcome in outcomes.items():
        if source in RETIRED_SOURCES:
            # D108: whatever outcome a caller passes for a retired source is ignored.
            continue
        if outcome == NOT_ATTEMPTED:
            # D95: the step was not attempted this run (AIRI is retried monthly). A bare
            # GitHub "skipped" is NOT this: it still counts as a failure (tested), so a
            # step skipped by accident cannot hide a dead source.
            # Neither a success nor a failure: leave the counter, status and
            # last_* fields exactly as they were, so skipped weeks cannot reset
            # nor inflate it, and a failed monthly attempt still accumulates.
            continue
        entry = dict(new_state.get(source, {}))
        succeeded = outcome == "success"

        if succeeded:
            entry["consecutive_failures"] = 0
            entry["last_success"] = today
            entry["last_outcome"] = "success"
            entry["status"] = "ok"
        else:
            entry["consecutive_failures"] = int(entry.get("consecutive_failures", 0)) + 1
            entry["last_attempt"] = today
            entry["last_outcome"] = outcome
            if entry["consecutive_failures"] >= threshold:
                entry["status"] = "stale"
            else:
                entry["status"] = "degraded"

        entry.setdefault("consecutive_failures", 0)
        new_state[source] = entry

        if not succeeded:
            if entry["status"] == "stale":
                p = pause_status(entry, today)
                if p == "active":
                    pause_notices[source] = p
                else:
                    stale.append(source)
                    if p in ("invalid", "expired"):
                        pause_notices[source] = p
            else:
                degraded.append(source)

    # D108: stamp retired sources regardless of what outcomes were supplied (the
    # workflow no longer passes one). Prior counters/last_* are kept as history.
    for source, info in RETIRED_SOURCES.items():
        entry = dict(new_state.get(source, {}))
        entry["status"] = "retired"
        entry["retired_on"] = info["retired_on"]
        entry["retired_reason"] = info["retired_reason"]
        entry.setdefault("consecutive_failures", 0)
        new_state[source] = entry

    return new_state, stale, degraded, pause_notices


def render_summary(state: dict, outcomes: dict[str, str]) -> str:
    lines = ["### Source health (consecutive-failure tracking)", "", "| Source | This run | Consecutive failures | Status | Paused |", "|---|---|---|---|---|"]
    # D108: a retired source is listed once, as retired, whether or not a caller
    # passed an outcome for it.
    for source in sorted(set(outcomes) | set(RETIRED_SOURCES)):
        entry = state.get(source, {})
        if source in RETIRED_SOURCES:
            lines.append(f"| {source} | retired {RETIRED_SOURCES[source]['retired_on']} (not attempted) "
                         f"| {entry.get('consecutive_failures', 0)} (frozen) | retired | no |")
            continue
        lines.append(
            f"| {source} | {outcomes[source]}{' (monthly retry; counter unchanged)' if outcomes[source] == NOT_ATTEMPTED else ''} | {entry.get('consecutive_failures', 0)} "
            f"| {entry.get('status', 'unknown')} | {'yes' if entry.get('paused') else 'no'} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outcomes-json", required=True,
        help='JSON object mapping source name -> step outcome, e.g. '
             '\'{"airi_navigator": "failure", "aiaaic_sheet": "success"}\'',
    )
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--today", default=None, help="Override for tests; defaults to UTC today")
    parser.add_argument(
        "--summary-file", type=Path, default=None,
        help="Append the markdown summary here (e.g. $GITHUB_STEP_SUMMARY)",
    )
    args = parser.parse_args(argv)

    outcomes = json.loads(args.outcomes_json)
    today = args.today or utc_today()

    state = load_state(args.state_file)
    new_state, stale, degraded, pause_notices = update_source_health(
        state, outcomes, today=today, threshold=args.threshold
    )
    save_state(args.state_file, new_state)

    summary = render_summary(new_state, outcomes)
    print(summary)
    if args.summary_file:
        with args.summary_file.open("a", encoding="utf-8") as f:
            f.write(summary + "\n")

    for s, p in pause_notices.items():
        entry = new_state[s]
        if p == "active":
            print(f"::warning::{s} has failed {entry['consecutive_failures']} consecutive "
                  f"refreshes and is stale, but alerting is paused until {entry.get('paused_until')} "
                  f"({entry.get('paused_reason')}).")
        elif p == "invalid":
            print(f"::error::{s} is marked paused but the pause is INVALID (missing "
                  f"paused_reason/paused_until, a paused_until that isn't a canonical "
                  f"YYYY-MM-DD date, or one dated more than {MAX_PAUSE_HORIZON_DAYS} days out — "
                  "in ingest/_state/source_health.json) — not honoring it. Fix the pause, "
                  "or this source keeps failing loudly.")
        elif p == "expired":
            print(f"::error::{s}'s pause EXPIRED on {entry.get('paused_until')} — not honoring "
                  "it. Renew paused_until with a fresh reason, or resolve the source.")

    for s in degraded:
        print(f"::warning::{s} failed this refresh ({new_state[s]['consecutive_failures']}/"
              f"{args.threshold} consecutive failures so far).")

    if stale:
        names = ", ".join(sorted(stale))
        print(
            f"::error::{names} — {len(stale)} source(s) failed {args.threshold}+ consecutive "
            "refreshes. This is no longer a per-run warning: the source is stale and the run "
            "is failing loudly on purpose. Investigate, retire the source (tombstone its "
            "corpus entries per Invariant 3, don't delete), or pause this check with a recorded "
            "reason in ingest/_state/source_health.json while remediation is tracked."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
