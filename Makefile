.PHONY: build validate render merge install clean test stix taxii misp huggingface ingest-cve ingest-kev ingest-airi ingest-aiaaic ingest-aiid ingest-oecd-aim ingest-redteam ingest-all render-docs-stats check-stats-drift docs-data verify-docs-data a11y

install:
	pip install -r requirements.txt

build: merge render render-docs-stats validate

test:
	pytest tests -q

merge:
	python scripts/parse_existing.py
	python scripts/merge_and_dedupe.py

render:
	python scripts/render_markdown.py

# Template data/stats.json's counts into README/DATASHEET/site/CITATION.cff
# (WS6-T2, invariant 6). Reads stats.json written by `render`; never
# computes a count itself. Idempotent — safe to run every build.
render-docs-stats:
	python scripts/render_docs_stats.py

# CI gate for invariant 6: fails if any doc surface has drifted from
# data/stats.json, or carries a hardcoded total outside a stats:* marker.
check-stats-drift:
	python scripts/check_stats_drift.py

validate:
	python scripts/validate.py

# STIX 2.1 bundle for threat-intel platforms (build artifact, not committed).
stix:
	python scripts/export_stix.py

# Static TAXII-compatible discovery document under docs/taxii2/ (Pages artifact, not committed).
taxii:
	python scripts/export_taxii.py

# MISP feed under docs/misp/ (Pages artifact, not committed).
misp:
	python scripts/export_misp.py

# WS6-T5: mirror data/incidents.min.json into docs/data/ (matching the Pages
# workflow), then split it into the trimmed core payload + lazy per-year
# detail shards the site actually fetches. Pages artifacts, not committed
# (see .gitignore) -- run this to reproduce docs/data/ for local testing.
docs-data:
	mkdir -p docs/data
	cp data/incidents.min.json docs/data/incidents.min.json
	python scripts/gen_docs_core_data.py
	python scripts/gen_data_integrity.py

# CI gate: docs/data/SHA256SUMS must match the files it lists and must list
# everything served under docs/data/. Run `make docs-data` first.
verify-docs-data:
	python scripts/verify_data_integrity.py

# axe-core + Lighthouse accessibility gates + the 380px layout check
# (WS6-T5). Requires `make docs-data`, Node, and `npm install` in
# tests/a11y/ first; serves docs/ on :8123 for the duration of the checks.
a11y: docs-data
	python -m http.server 8123 --directory docs & \
	SERVER_PID=$$!; \
	sleep 1; \
	( cd tests/a11y && node check_axe.js http://127.0.0.1:8123/ \
	  && node check_lighthouse.js http://127.0.0.1:8123/ \
	  && node check_narrow_viewport.js http://127.0.0.1:8123/ ); \
	STATUS=$$?; \
	kill $$SERVER_PID; \
	exit $$STATUS

# Hugging Face dataset package (dist/hf/); add --push with HF_TOKEN set to upload.
huggingface:
	python scripts/export_huggingface.py

# Pull AI/ML/LLM/agent CVEs from NVD + GHSA + OSV.
# Output: ingest/cve_nvd_expanded.json
# Cached responses are stored under ingest/_cache/{nvd,ghsa,osv}/ so the
# script is restartable.  Requires `gh` CLI to be authenticated.
ingest-redteam:
	python scripts/ingest_redteam_benchmarks.py

ingest-cve:
	python scripts/ingest_cve_nvd_expanded.py

# Refresh the CISA Known Exploited Vulnerabilities snapshot.
# Output: ingest/cisa_kev.json
ingest-kev:
	python scripts/ingest_cisa_kev.py

# Pull the MIT FutureTech AI Risk Navigator dataset (wraps AIID with extra
# taxonomy and authoritative incident dates).
# Output: ingest/airi_navigator_incidents.json
ingest-airi:
	python scripts/ingest_airi_navigator.py

# Pull the canonical AIAAIC Repository spreadsheet (~2,200 rows).
# Output: ingest/aiaaic_sheet_incidents.json
ingest-aiaaic:
	python scripts/ingest_aiaaic_sheet.py

# Scrape the OECD AI Incidents Monitor (10k+ pages from the sitemap).
# Cached under ingest/_cache/oecd_aim/ so the script is restartable.
# Override OECD_AIM_LIMIT to control how many URLs to fetch (0 = all).
# Output: ingest/oecd_aim_full_incidents.json
ingest-oecd-aim:
	python scripts/ingest_oecd_aim.py

# Pull AIID data from AIID's own sanctioned bulk-access channel (the
# official weekly snapshot at incidentdatabase.ai/research/snapshots/,
# served from R2) instead of the prohibited high-volume per-page scrape.
# Swap-half of WS0-T4 / decision D1 (2026-07-18). Never extracts
# reports.csv/reports.bson (the `reports.text` field is excluded from
# AIID's CC-BY-SA grant) and persists facts + link only -- see the
# script's module docstring and docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md.
# Output: ingest/aiid_full.json (+ ingest/aiid_full.provenance.json).
ingest-aiid:
	python scripts/ingest_aiid_snapshot.py

# Refresh every external source. Heavy: NVD/GHSA, AIRI, AIAAIC, AIID, OECD AIM.
ingest-all: ingest-cve ingest-kev ingest-airi ingest-aiaaic ingest-aiid ingest-oecd-aim
# D1/E1/WS0-T4 (2026-07-16): AIID's Terms of Use prohibit high-volume/bot
# access; scrape_aiid.py ran ThreadPoolExecutor(max_workers=12) against
# per-incident pages, an active ToS violation. Disabled here (stop-half of
# WS0-T4) and superseded by `ingest-aiid` above (swap-half, landed
# 2026-07-18). scripts/scrape_aiid.py is kept in the repo, unused except
# as a reused-function library for ingest_aiid_snapshot.py (TAXONOMY_RULES /
# severity_for / is_security_relevant); its own network-fetching main()
# must stay disabled here permanently.
#	python scripts/scrape_aiid.py

clean:
	rm -f data/incidents.json data/incidents.min.json data/legacy_consolidated.json INCIDENTS.md
