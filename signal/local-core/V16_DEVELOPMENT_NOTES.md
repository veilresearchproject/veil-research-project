# SIGNAL desktop v0.16 — One checked starting point

Double-click **START_HERE.bat** after extracting the full ZIP to a new folder.
It verifies Python 3.10+ and the package's recorded file hashes, then offers:

1. Scripted face demonstration (no AI model).
2. Live assistant using local Ollama.
3. Local setup check without speaking or microphone capture.
4. Automated Python tests using simulated models/audio.
5. The local desktop test checklist, displayed as text.
Q quits without starting anything.

Nothing is launched automatically from the menu. Dispatch uses the current Python
interpreter, fixed argument arrays and absolute script paths, including paths with
spaces. No shell command is assembled from the menu response. The selected program
replaces the menu process; reopen START_HERE for another choice. The batch wrapper
leaves the result visible. No installer, model download or paid service is invoked.

## Package checks

The launcher checks required modules/assets and every file listed in the release
manifest. Missing, changed, oversized or unreadable files cause startup to stop
with extraction guidance. Manifest paths must be canonical relative paths within
the package, with no duplicates, parent traversal, drive names or external links.
These hashes detect accidental damage; they are not a publisher signature and do
not establish that a package came from a trusted source.

All prior entry scripts remain available. A source checkout without a generated
manifest should use developer scripts or build a release first; the checked menu
is intended for the packaged Windows ZIP. It never repairs files automatically,
deletes evidence, or changes saved conversations.

## Repeatable packaging

`build_signal_release.py --output PATH --source-commit FULL_SHA` builds a Windows
ZIP with a fresh byte manifest and source provenance. It includes supported source,
documentation and face assets, excluding runtime JSON memories and WAV recordings.
ZIP entry order and timestamps are stable, so identical source bytes and commit
metadata produce identical archive bytes. A temporary sibling is verified before
replacing the output. Packaging alone does not run tests or establish readiness.

## Verification and limits

176 Python tests passed, including nine launcher tests and three release-builder
tests. Cases include missing/damaged packages, folder paths with spaces, invalid
menu input, explicit dispatch, failed execution, runtime-data exclusion, identical
build hashes and preservation of an existing ZIP after invalid build inputs.
The built archive also passed an extracted-package manifest check and a real
Python guide/quit smoke test without starting audio, a model or a browser.

JavaScript syntax and prior DOM interaction simulations remain passing.
The actual Windows batch wrapper, audio devices, Ollama performance and rendered
layout still need acceptance on Andrew's PC. No hands-free or hardware-readiness
claim is added by the launcher.
