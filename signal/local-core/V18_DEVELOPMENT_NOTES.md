# SIGNAL desktop v0.18 — Installed Windows voice selection

The desktop now lists voices exposed by Windows System.Speech and lets the
operator select one or return to the system default. Selection is optional and
lasts only for this run. It neither enables speech nor plays a sample; use Enable
voice and Test voice explicitly. Changing an active voice stops its current
utterance while preserving the existing enabled/off setting.

The server revalidates an exact selected name against the installed inventory.
Missing, invalid or no-longer-installed names preserve the current selection.
Inventory timeouts become a clear error. Listing happens outside the speech
process mutex, so Stop/Disable voice stay available while Windows is listing.
API token, origin and generation-busy guards remain in force.

Speech text and the selected name are carried as JSON on the local process stdin
pipe. They are parsed as data by a fixed PowerShell script; names are not spliced
into PowerShell source or command-line arguments. Rate remains a validated integer.
Unicode names/text are supported by the same UTF-8 pipe.

## Verification

185 Python tests passed, including nine new voice-selection/HTTP/concurrency
tests. Cases cover exact installed selection, explicit default, invalid names,
preserved enabled/off state, no auto speech or model call, safe stdin transport,
inventory timeout, stop responsiveness, authentication and busy rejection.

JavaScript syntax and extended DOM interactions passed installed-list refresh,
selection/default, no automatic sample, and inventory/selection failure handling.
The packaged ZIP passed manifest verification and the launcher guide smoke test.

## Limits

The real Windows speech engine, actual voice inventory, pronunciation, selected
voice playback and rendered layout were not tested here. Not every voice visible
elsewhere in Windows is necessarily exposed to System.Speech. Naturalness depends
on voices already available on the PC. This is not custom expressive speech,
voice cloning or accurate lip synchronization. It adds no download, paid service,
cloud speech fallback, or always-on microphone.
