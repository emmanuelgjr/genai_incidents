"""Fire proofs (agreement 6) for v2.13.0 item 8: corrupt one source line, run the guarding
check, expect FAILURE, restore with git checkout. Run on a clean tree:

    python scripts/audit/export_fire_proofs.py

Every line must say FIRES. See docs/audits/ws6-v2130-export-integrity-2026-10-11.md section 6."""
import subprocess, sys, pathlib

R = pathlib.Path(__file__).resolve().parents[2]

CASES = [
    ("STIX modified ignores EXPORTER_VERSION", "scripts/export_stix.py",
     '    return _ts(date_str)[:-4] + f"{EXPORTER_VERSION:03d}Z"', '    return _ts(date_str)',
     ["pytest", "tests/test_export_modified.py", "-q", "-x", "-k", "version_bump or updated_date_plus"]),
    ("STIX modified never moves on content change", "scripts/export_stix.py",
     '        modified = _modified(created, i.get("updated") or i.get("added") or i.get("date"))',
     '        modified = _modified(created)',
     ["pytest", "tests/test_export_modified.py", "-q", "-x", "-k", "content_change_bumps or plus_exporter"]),
    ("STIX exports a new non-content field (confidence)", "scripts/export_stix.py",
     '            "x_rejected_cve_ids": i.get("rejected_cve_ids") or [],',
     '            "x_rejected_cve_ids": i.get("rejected_cve_ids") or [], "x_confidence": i.get("confidence"),',
     ["pytest", "tests/test_export_modified.py", "-q", "-x", "-k", "content_or_explicitly"]),
    ("STIX drops x_source_freshness", "scripts/export_stix.py",
     '        if sf:\n            sdo["x_source_freshness"] = sf', '        if sf:\n            pass',
     ["pytest", "tests/test_export_modified.py", "-q", "-x", "-k", "source_freshness"]),
    ("MISP drops freshness machinetags", "scripts/export_misp.py",
     "    return tags + _freshness_tags(e)", "    return tags",
     ["pytest", "tests/test_export_integrity.py", "-q", "-x", "-k", "misp_freshness or misp_real"]),
    ("MISP event timestamp reverts to fixed Jan-1-of-year", "scripts/export_misp.py",
     '"timestamp": _event_timestamp(year, incidents or []),', '"timestamp": _year_epoch(year),',
     ["pytest", "tests/test_export_integrity.py", "-q", "-x", "-k", "event_timestamp"]),
    ("verify_sums stops comparing digests", "scripts/export_integrity.py",
     "        elif (got := sha256_of(p)) != want:", "        elif (got := want) != want:",
     ["pytest", "tests/test_export_integrity.py", "-q", "-x", "-k", "one_changed_byte"]),
    ("verify_all stops comparing manifest to stats.json", "scripts/export_integrity.py",
     "            errors.extend(f\"{tree.name}/{MANIFEST_NAME}: {e}\" for e in manifest_vs_stats(m))", "            pass",
     ["pytest", "tests/test_export_integrity.py", "-q", "-x", "-k", "disagree_with_stats"]),
    ("HF build stops shipping the manifest/sums", "scripts/export_huggingface.py",
     '    ei.write_sums(out_dir, "*")', "    pass",
     ["pytest", "tests/test_export_integrity.py", "-q", "-x", "-k", "huggingface"]),
    ("DISPUTED card note removed", "scripts/render_markdown.py",
     '    elif e.get("status") == "disputed":', '    elif False:',
     ["pytest", "tests/test_render_markdown.py", "-q", "-x", "-k", "disputed"]),
    ("disputed_count omitted from stats.json writer", "scripts/render_markdown.py",
     '        "disputed_count": sum(1 for e in entries if e.get("status") == "disputed"),',
     '        "disputed_count": 0,',
     [sys.executable, "scripts/render_markdown.py"]),
]

for name, f, old, new, cmd in CASES:
    p = R / f
    src = p.read_text(encoding="utf-8")
    assert old in src, f"{name}: pattern not found"
    p.write_text(src.replace(old, new, 1), encoding="utf-8", newline="")
    try:
        c = [sys.executable, "-m"] + cmd if cmd[0] == "pytest" else cmd
        r = subprocess.run(c, cwd=R, capture_output=True, text=True)
        if "render_markdown" in f and cmd[0] != "pytest":
            # follow with the drift gate that must now fail
            r = subprocess.run([sys.executable, "scripts/check_stats_drift.py"], cwd=R, capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"[{'FIRES' if r.returncode else 'DID NOT FIRE'}] {name} -> exit {r.returncode}: {tail[:140]}")
    finally:
        subprocess.run(["git", "checkout", "--", f], cwd=R, check=True)
        if "render_markdown" in f and cmd[0] != "pytest":
            subprocess.run(["git", "checkout", "--", "data/stats.json", "INCIDENTS.md", "docs/incidents"], cwd=R, check=True)
