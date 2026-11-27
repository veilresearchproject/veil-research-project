# SIGNAL Phase 1 — exact-source offline regression baseline (2026-11-27)

## What was tested
Recreated **six exact Python files** by reading their contents from GitHub on the isolated branch, and verified each recreated file using `git hash-object` against the GitHub blob SHA:

| File | Verified SHA |
|---|---|
| `memory_recall.py` | `2d8b2de70b643584d4bf04342cebe7ac8cba4135` |
| `memory_context_gate.py` | `8209f6492386226288733e04a91cf53fc408c7a7` |
| `guarded_memory_recall.py` | `7fcf28dcff514c6e772104aa50a70e31185ab914` |
| `test_memory_context_gate.py` | `a5ea4ba60aadadf9ca13b9a14e25c9db44c97450` |
| `test_guarded_memory_recall.py` | `5d5620e566fb6f1063fe5b3e9ddc85ff42b54e5f` |
| `test_phase1_memory_integration.py` | `aa1041ae49970cc3e40812923dc7c51e7f77cdb9` |

## Executed test command
Working directory contains the six matching Python files (repository's `signal_lab_demo` folder contents, copied without modification).
```sh
python -m unittest -q test_memory_context_gate test_guarded_memory_recall test_phase1_memory_integration
```
**Result: Ran 27 tests in 0.001s — OK (27 passed, 0 failed).**

This includes 22 existing unit tests and **5 newly committed integration tests**. Scenarios: explicit consent/auth flags, denied reads, reviewed-only notes, metadata-only default, separate text disclosure, source attribution and scientific uncertainty, bounded responses, fail-closed invalid input, no equipment-command execution, and ensuring text never enters the speech response.

## Explicit boundaries
- No full Git repository checkout was possible: the execution container DNS lookup for `github.com` failed. The six source files above were individually retrieved via GitHub connector and verified **byte-for-byte** using Git blob hashes.
- This is **not** the full repository test suite, live CI, Ollama integration, secure identity authentication, mic/speech test, Samsung device test, real sensor test, or a physical lab trial.
- Caller-supplied `authenticated=True` is not a genuine authentication mechanism. Legacy `memory_recall.recall_memory` is unguarded and must stay inaccessible to phone clients.
- Nothing was merged or deployed. No paid API or equipment was used.

## VEL-001 archive reconnaissance (separate track)
Library search surfaced a `VEL-001 v0.1` README (Python logic-only description), plus a separately named `VEIL_Virtual_Lab_v0.2_AI_Ready_Offline.html`. The latter cannot be equated with the claimed **ESP32 C++ host-test v0.2 controller archive** without file inspection and source linkage; no verified ESP32 controller source or host test executable was established in this run. Thus host C++ tests remain **previously reported, not independently reproduced**, and ESP32 target build, virtual electrical simulation and hardware validation remain unverified.

## Next steps
1. On a machine with repository network access, clone this branch and run `python -m unittest discover -s signal_lab_demo -p 'test_*.py'`, recording full stdout and commit SHA.
2. Put the guarded recall entry point behind **real local authentication** and test Ollama conversation integration. Do not expose the unguarded legacy recall method.
3. Locate the actual VEL-001 ESP32 C++ v0.2 archive and run host tests; target compile and simulated electrical faults are separate gates.
4. Preserve source exports and authorized encrypted backups outside the public repository; independently verify restore.
