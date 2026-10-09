# D42(3): per-merge evidence for the refresh's OECD/AIID-driven changes, 2026-10-03

**Status: dated evidence record, for the user's ruling. Do not regenerate.** This
is a proposal, not an approval. Nothing here is authorized; the build reads
`docs/audits/D42-approved-refresh-merges.json`, which does not exist until the user
rules. The machine-readable form of the recommendations below is
`docs/audits/D42-proposed-refresh-merges.json` (marked PROPOSED). No deprecation
or data was written.

**Scope.** `docs/audits/refresh-tripwire-2026-10-03.md` found 7 new `merged`
deprecations and 4 retitles. Re-running with the AIID snapshot refreshed as well
(the WS4-T14 step, snapshot `backup-20260928101247`) shows the gate would refuse
**17 changes**: the same 7 merges plus **10 retitles of published IDs**. All 17 are
listed. The snapshot adds 6 of the retitles, all to AIID's own title for the absorbed id.

**Method [R].** Inputs: today's OECD crawl (`OECD_AIM_LIMIT=3000
python scripts/ingest_oecd_aim.py`), the fresh AIID snapshot
(`python scripts/ingest_aiid_snapshot.py`), the published corpus at `HEAD`. Rebuild
run with the gate's check stubbed out in a scratch process, so the build ran to
completion; then compared with `git show HEAD:data/incidents.json`; the tree was
restored (`git status --porcelain` shows no data or ingest change). Per merge,
the raw OECD and AIID records of both sides were read.

**Mechanism common to every item.** None of the 7 pairs shares a reference URL.
Each change is produced by an AIID id on an OECD row's `extra_source_ids` acting as
a dedup key. Two of the bad ones come from single OECD rows citing several AIID ids
(`OECD-AIM-2026-07-20-7ddf` cites AIID-1535, 1569, 1609, three distinct incidents;
`OECD-AIM-2024-06-24-413e` cites 1655 and 1656). That is an editorial claim by OECD,
not evidence that the incidents are one.

## A. The 7 merges

| # | retired -> into | retired (OECD/AIID record) | into (published) | recommendation |
|---|---|---|---|---|
| 1 | INC-02381 -> INC-01579 | AIID-1370 "California Teen Reportedly Died of Overdose ... ChatGPT", 2025-05-31 | OECD-AIM-2026-05-12-55cf "OpenAI Sued After ChatGPT Advice Allegedly Leads to Fatal Overdose"; cites AIID-1370 | **Approve.** Same death; the lawsuit row cites the AIID incident. |
| 2 | INC-14310 -> INC-01994 | OECD-AIM-2026-07-01-6cd1 "Tesla Autopilot Failure and Data Suppression ...", cites AIID-1686 | OECD-AIM-2026-02-20-224a "US Court Upholds $243 Million Verdict Against Tesla"; cites AIID-1686 | **Approve** the merge (same $243M case). Not the retitle (see B). |
| 3 | INC-01469 -> INC-00699 | OECD-AIM-2026-03-24-ed03 "Music Publishers Sue Anthropic", cites AIID-1657 | OECD-AIM-2026-03-18-eb49 "BMG Sues Anthropic ..."; cites AIID-1657 | **Unsure, lean no.** Two filings; only one AIID id joins them (AIID-1657, "Anthropic Allegedly Copied Copyrighted Song Lyrics"). Approve only if AIID-1657 is treated as one incident. |
| 4 | INC-08148 -> INC-01628 | OECD-AIM-2026-06-08-113e "AI Chatbots Falsely Pose as Licensed Doctors in Pennsylvania", cites AIID-1108 | AIID-1108 "Digital Rights Groups Accuse Meta and Character.AI of ... Unlicensed Therapy" + OECD-2026-05-05-e377 "Pennsylvania Sues Character.AI" | **Unsure, lean no.** Different event from AIID-1108; the target's existing grouping is itself doubtful. |
| 5 | INC-13241 -> INC-01514 | OECD-AIM-2026-06-21-bcb5 "AI-Powered Data Centers ... Spark Legal Battle" (Mississippi), cites AIID-1677 | OECD-AIM-2026-04-14-1df3 "NAACP Sues xAI ... Gas Turbine" (Memphis); cites AIID-1677 | **Approve.** Same xAI turbine-pollution incident per the shared AIID id. |
| 6 | INC-14317 -> INC-13066 | AIID-1569 "GPT-4o ... Michael Lines's Delusions" (California, 2025-03-28) + OECD-2026-07-01-994d | AIID-1535 "OpenAI Allegedly Failed to Intervene ... Montreal Web Developer Alice Carrier's Suicide" + 2 OECD rows | **Do not approve.** Different people and events; bridged by one multi-citing OECD row that also pulls in AIID-1609 (Florida pastor). Same pair the 09-15 gate marked unrelated. |
| 7 | INC-14902 -> INC-00699 | OECD-AIM-2026-07-11-995f "Suno AI Exposed for Scraping ... and User Data Breach", cites AIID-1655 | INC-00699 (BMG v. Anthropic) | **Do not approve.** Not a lawsuit against Anthropic. INC-00699 becomes a 15-source "music AI" hub by chaining AIID-1655/1656/1657. |

If the user does not approve an item, approving nothing for it keeps the build
failing closed; the fix is then in the merge heuristic (do not let one OECD row's
AIID cross-references bridge distinct published entries), which is a design
decision for a follow-up task. The gate cannot "reject and continue" by itself.

## B. The 10 retitles of published IDs

| ID | published title | rebuilt title | basis | recommendation |
|---|---|---|---|---|
| INC-01579 | OpenAI Sued After ChatGPT Advice ... Fatal Overdose | California Teen Reportedly Died of Overdose ... | equals AIID-1370's title | Approve (with merge 1) |
| INC-13321 | DuckDuckGo AI Spreads False Trump Death Story ... | DuckDuckGo Search Assist Reportedly Falsely Claimed ... Rabies | equals AIID-1644's title | Approve |
| INC-14517 | OpenAI GPT-5.6 AI Model Deletes User Files ... | OpenAI GPT-5.6 Sol Agent Reportedly Deleted Most Files ... | equals AIID-1671's title; also absorbs AIID-1672 (a separate production-database incident) | Approve, noting AIID-1672 joins the row |
| INC-07910 | Google Gemini AI Deletes 28,745 Lines of Code ... | Google Gemini 3.5 Coding Agent Reportedly Caused Production Portal Outage ... | equals AIID-1673's title | Approve |
| INC-07783 | Lyft Driver Uses AI-Generated Images ... | Lyft Driver in Boca Raton, Florida, Allegedly Used Purported Google Gemini-Generated Image ... | equals AIID-1679's title | Approve |
| INC-01514 | NAACP Sues xAI Over Illegal Gas Turbine Use ... | xAI Data Centers Linked to Unpermitted Pollution in Mississippi and Tennessee | an OECD row's headline | Approve if merge 5 is approved |
| INC-01994 | US Court Upholds $243 Million Verdict Against Tesla ... | Tesla Faces Trial Over Fatal Autopilot Crash in Florida | an earlier OECD row citing AIID-1686 | **Do not approve** (a different trial) |
| INC-00699 | BMG Sues Anthropic ... | Record Labels Sue AI Music Generators for Copyright Infringement | generic hub headline; not AIID's title | **Do not approve** |
| INC-00813 | Claude Code Project Files RCE & API Token Exfiltration (CVE-2025-59536 & CVE-2026-21852) | Unknown Actor Reportedly Exploited Cline's Claude-Powered GitHub Issue-Triage Workflow ... | AIID-1680's title; the row is a CVE-keyed Claude Code cluster of 5 sources | **Do not approve** (unrelated incident) |
| INC-03717 | Deepfake Porn Sites Use Breeze Liu's Image Without Consent | Dozens of Dutch Women, Including Politicians ... Targeted With AI-Made ... | AIID-1684's title, absorbed through OECD-AIM-2024-03-22-e868 | **Do not approve** (unrelated incident) |

Two of the retitles (INC-00813, INC-03717) have no deprecation: a published ID's
content is swapped by absorbing a new row, so a gate on deprecations alone would
have missed them. That is why the gate also checks retitles.

## C. Not gated, for completeness

The fresh snapshot also edits 24 existing titles upstream with no OECD/AIID id absorbed (for example
"Reportedly"/"Allegedly" insertions) (mostly AIID-authored rows). They are not gated; they are upstream title changes, listed here so
the PR diff is not a surprise.

## D. What approving does

Copy the approved subset into `docs/audits/D42-approved-refresh-merges.json` under
the schema in `scripts/merge_and_dedupe.py::_load_refresh_merge_approvals` (entries
of `{"kind": "merge", "from", "into"}` or `{"kind": "retitle", "id"}`, an
`authorization` marker with `decision`, `ruled_by: "user"`, and the matching
`entries_sha256`). The record that ruling must also pin the hash in code, as
WS4-T21 did for D28, or the tamper-plus-recompute shape stays open.
