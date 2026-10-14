# Dependabot alert triage (2026-10-13)

> **Dated record, do-not-regenerate** (CLAUDE.md agreement 4).
> - **Who triaged:** the foreman, read-only.
> - **Sources:** `gh api repos/emmanuelgjr/genai_incidents/dependabot/alerts?state=open`; `npm view`.
> - **Changes made:** none. No alert was dismissed and no package was bumped.

## Open alerts: 8 (2 high, 6 medium)

**All 8 are in `tests/a11y/package-lock.json`.** That is CI-only accessibility tooling (WS6-T5): devDependencies that never ship to `docs/`, the published data or the Python package. The published site, the data, PyPI and HF are not affected.

| # | Severity | Package (locked) | Pulled in by | Patched in | Exposure here |
|---|---|---|---|---|---|
| 2, 3 | high | extract-zip 2.0.1 | `puppeteer-core` ^23 → `@puppeteer/browsers` 2.x, and `lighthouse` 12 → `@puppeteer/browsers` | none | Low. The vulnerability is symlink path traversal when extracting a hostile zip. Our CI installs Chrome with `browser-actions/setup-chrome` (a11y.yml:88), and the scripts take `CHROME_PATH`, so the browser-download path is not normally used. |
| 5-10 | medium | @opentelemetry/instrumentation-{tedious,mongoose,mysql,knex,mysql2,pg} | `lighthouse` 12 → `@sentry/node` 9.47.1 | 0.40-0.73 | None in practice. The flaw is a DB username leaking into span attributes, and this tooling has no database. |

## Fix path (not applied)
- **puppeteer-core ^23 → ^25 (25.13.0).** Its `@puppeteer/browsers` 3.2.4 depends only on `yargs` and `modern-tar`. **extract-zip is gone.**
- **lighthouse ^12 → ^13 (13.5.0).** That moves `@sentry/node` to ^10. The 10.x line no longer lists `@opentelemetry/instrumentation-pg` as a direct dependency, so it is expected to clear 5-10. **Confirm on the regenerated lockfile, not from this reading.**
- **Both are major bumps**, so the a11y workflow (axe, Lighthouse, 380px viewport) must pass on the PR. Owner: WS6, distribution-engineer.
- **Register a14 (Dependabot configuration) is still the user's decision.** This triage does not settle it.
