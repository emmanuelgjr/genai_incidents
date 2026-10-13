# scripts/archive

One-off historical scripts, kept for reproducibility of past data fixes
(see CHANGELOG). They are not part of the build, are not run by CI or the
Makefile, and should not be used on current data.

- `_finish_cve_from_cache.py`
- `strip_presigned_urls.py` (sanitized INC-11516; see CHANGELOG)

Both resolve the repository root as two levels above this directory.
