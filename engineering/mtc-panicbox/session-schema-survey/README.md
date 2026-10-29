# VEIL MTC — read-only session schema survey (draft v0.1.0)

**Prepared October 29, 2026.** This development-only helper describes the *structure* of three JSON log files from a completed MTC v0.1.4 session without assuming an undocumented event schema. It never examines WAV audio or determines whether an experimental test succeeded.

## What it does

- Reads `session_result.json`, `session_metadata.json`, and `events.jsonl` from a **stopped, copied** MTC session folder.
- Prints JSON report containing file sizes, SHA-256 current-file digests, top-level JSON types, JSON field **names/types/occurrence counts**, and JSONL line counts/errors. Sensitive field **values** (such as played questions, audio transcripts, identity or event details) are **not printed**.
- Fails closed with `HOLD` / process exit code 2 when required files are missing or malformed, a final-path symlink is used, or size bounds are exceeded. `SCHEMA_PROFILED_ONLY` / exit code 0 means the three log files were parseable enough to profile; **NOT** that recording, question playback, termination, continuity, or paranormal activity was verified.
- Python 3.9+, standard library only, no network/API, no file writes, no imports of the live MTC recorder, no equipment access. The tool doesn't inspect raw WAVs.

## Home PC usage (only AFTER Andrew reviews and approves)

1. On the **personal home Windows computer** (never AJAX/work equipment), ensure the MTC recorder is stopped. Preserve the original session folder and make an independent complete copy for review.
2. With Python 3 installed, open PowerShell from the directory containing `mtc_session_schema_survey.py`.
3. Run on your **copied** session, replacing the example path:

```powershell
py -3 .\mtc_session_schema_survey.py "C:\VEIL\review-copy\MTC_20261027_215040_70c105"
```

4. If desired, save the report to a **different** directory (not inside your original evidence folder), e.g.:

```powershell
py -3 .\mtc_session_schema_survey.py "C:\VEIL\review-copy\MTC_20261027_215040_70c105" | Out-File -FilePath "C:\VEIL\review-output\mtc_schema_report.json" -Encoding utf8
```

The report is safe *relative to raw session values*, but field names, file hashes and sizes are still metadata. Review before sharing. Because report is printed, accidental shell redirection into an evidence folder is still possible; choose the output location carefully.

## Run synthetic regression tests

```powershell
py -3 -m unittest -v test_mtc_session_schema_survey.py
```

Do not upload private audio/logs to GitHub. Do not merge this draft into `main` or deploy it to the home recording PC without Andrew's review.

## Limits and technical notes

- Only **one file's** SHA-256 computed at inspection time; this does not prove historical integrity, chain of custody or matched copy unless compared to a preserved original.
- JSONL is expected to contain one JSON value per line; a scalar/list row is profiled and warned about rather than silently treated as a recognized event.
- A valid schema survey **cannot** infer `success`, `normal stop`, whether questions played, 90-minute audio duration, split-WAV seam continuity, microphone health, spoken words or paranormal source. All event string values remain deliberately hidden.
- File caps: 2 MiB per small JSON file, 16 MiB event log, 256 KiB per event line. Limit path proliferation to 120 distinct paths; nested inspection depth 3 and array sampling 12 items. Excess distinct paths trigger warning, and may be incomplete.
- This is a feasibility tool designed against generated/synthetic data. **Actual October 27 logs have not been accessed.** Structural differences may require revisions. Home Windows compatibility has not yet been verified.
- Further checks should proceed in the existing staged validation protocol in [draft PR #14](https://github.com/veilresearchproject/veil-research-project/pull/14). WAV structure tools are separately staged in [draft PR #13](https://github.com/veilresearchproject/veil-research-project/pull/13); exploratory clip screening is in [draft PR #10](https://github.com/veilresearchproject/veil-research-project/pull/10).

**No purchase, outreach, external upload, home PC control, production recorder modification, or public scientific claim authorized.**
