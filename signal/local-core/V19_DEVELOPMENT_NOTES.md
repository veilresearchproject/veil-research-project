# SIGNAL desktop v0.19 — Explicit human-note conversation context

After loading an MTC session and writing notebook observations, click **Include
notes in conversation** to make a bounded snapshot available to subsequent model
requests. It is off by default. Including does not generate a reply or activate
audio; ask a question afterward.

The context distinguishes **unverified operator claims** from software logs and
automated acoustic flags. Labels such as known_source remain an operator assessment,
and unexplained means no identified cause, not paranormal. Note text is quoted as
JSON data with attribution instructions. These safeguards do not establish that a
model will resist every embedded instruction or interpret a note correctly.

At most eight most-recently-saved observations are included, with the full manual
note section bounded to 5,000 UTF-8 bytes. Whole older entries are omitted to meet
the budget; the interface reports inclusion and omission counts. The saved notebook
remains complete. Every entry is validated against the active session, finite time
range, known schema, manual-author marker, labels and note size before assignment.

Saving a new note clears the active snapshot; include again to refresh it. Failed
saves/imports preserve the previous context. New MTC loads, clear commands, model
changes and saved-chat restores remove active note context. Remove note context
does not delete notebook entries or earlier chat discussion. Earlier replies may
still refer to previous notes, and model context limits can affect recall.

The snapshot itself is temporary and is not included in saved-conversation data.
However, model replies can quote notes, and explicitly saving the chat saves those
completed replies. Original notebook/audio files are not copied into chat snapshots.
No raw WAV is opened or heard by this feature, and no source evidence is modified.

## Verification

197 Python tests passed, including twelve new context/HTTP tests. Cases cover
latest-note bounds, Unicode byte budgets, malformed/cross-session entries, unchanged
file bytes, quoted-data prompt construction, clear/model/restore lifecycle,
authentication, busy rejection, and new-note invalidation.

JavaScript syntax and extended DOM interactions passed explicit include/clear,
attribution labels, no model query on include, and preservation after validation
failure. The new ZIP passed manifest verification and launcher-guide smoke testing.

Windows audio, real Ollama note interpretation and rendered layout remain untested
on Andrew's PC. No scientific finding, verified cause, automatic EVP classification,
cloud service or instrument control is added.
