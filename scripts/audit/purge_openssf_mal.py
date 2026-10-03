"""One-off, deterministic purge of OpenSSF Malicious Packages (``MAL-``) report
text from the committed ingest/cve_nvd_expanded.json, using the SAME predicate
the OSV path now applies (``ingest_cve_nvd_expanded.is_openssf_malicious_row``).
Not a hand edit; rerunning it is a no-op.

MAL records are Apache-2.0, so their verbatim report text may not be carried.
Rows are dropped, EXCEPT ids listed in ``BARE_IDENTIFIER``: those keep their
id, title label, affected package, tags and reference links (facts and links,
not Apache-protected prose) with the description replaced by an original
sentence. No tag is added: a new tag would change the existing entry that
cites the id.
Reason: the corpus entry INC-08450 is held together by MAL-2026-3607 (its URLs
bridge a nestjs-auth CVE and a mistralai GHSA); dropping the row entirely makes
the merger split INC-08450, which the WS4-T19 guard refuses without a user
ruling. See docs/audits/wave12-ingest-delta-2026-10-03.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from ingest_cve_nvd_expanded import is_openssf_malicious_row  # noqa: E402

BARE_IDENTIFIER = {"MAL-2026-3607"}
STUB_MARK = "Bare identifier for OpenSSF Malicious Packages report"


def stub(row: dict) -> dict:
    row = dict(row)
    row["description"] = (
        f"{STUB_MARK} {row['source_id']} "
        f"(affected: {row.get('affected') or 'n/a'}). The report text is Apache-2.0 and is not "
        "reproduced here; the OSV link and the references below are the sources. Kept so the "
        "incident cluster that cites this report keeps its identifier and links."
    )
    row["description_provenance"] = "original"
    return row


p = ROOT / "ingest" / "cve_nvd_expanded.json"
rows = json.loads(p.read_text(encoding="utf-8"))
out, dropped, stubbed = [], [], []
for r in rows:
    if not is_openssf_malicious_row(r):
        out.append(r)
    elif r["source_id"] in BARE_IDENTIFIER:
        if r["description"].startswith(STUB_MARK):
            out.append(r)
        else:
            out.append(stub(r))
            stubbed.append(r["source_id"])
    else:
        dropped.append(r["source_id"])
if dropped or stubbed:
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"dropped {dropped}; reduced to bare identifier {stubbed}; rows {len(out)}")
