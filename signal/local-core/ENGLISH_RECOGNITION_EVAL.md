# SIGNAL English-first recognition evaluation — development prototype

**Status: standalone, offline, manually supplied text pairs. Not a live speech recognizer.**

This tool addresses the English-first microphone/recognition benchmarking roadmap without changing the working SIGNAL Windows installation, touching MTC evidence, or introducing paid APIs.

## What it measures
- Word error rate (WER) = (substitutions + deletions + insertions) / reference words. Values **can exceed 100%** if insertions are numerous.
- Normalized exact-sentence accuracy, ignoring punctuation and letter case.
- Recall for explicitly supplied VEIL terms and phrases (e.g., `MTC`, `Panic Box`); counts are *not* time-aligned.
- Optional manually measured latency, median and nearest-rank p95. **No timing is measured by this program.**

## Safe use on a desktop
1. Keep the known-working SIGNAL installation intact. Use a complete development checkout separately.
2. Run `py -3 -m unittest -v test_english_recognition_eval` from `signal/local-core`.
3. Run `py -3 english_recognition_eval.py english_recognition_demo.json` for a **synthetic** example.
4. For actual tests, use consented, non-sensitive sentences spoken in matched conditions. Listen to the original speech, type the exact reference and paste the output of an **independently run local/offline recognizer** into a private JSON copy with the same schema. Do not commit real transcripts to GitHub.
5. Compare existing microphones using the *same phrases, room, model and settings*. Record microphone name and environmental conditions separately in private notes, not in the JSON schema. A few sentences are exploratory, not a scientifically reliable benchmark.

The tool **does not access microphones, record audio, run ASR/Ollama, store results, write files, send data over a network, or infer user intelligence/education**. It prints aggregate results to the terminal only; the input fixture remains on disk wherever the operator placed it. Keep private transcripts outside GitHub and delete them according to consent and retention rules.

## Input schema
A UTF-8 JSON object with exactly `schema`, `samples`, and `terms`. Each sample has `reference`, `transcript`, and optionally `latency_ms` (measured externally). Empty `transcript` is permitted for total recognition failure. Up to 100 samples, 30 technical terms and 64 KiB input; symlink input is rejected. No speaker identifiers or audio fields are accepted.

## Limitations and next gate
Tokenization is an English-first, case-folded word comparison, not a phonetic/accent model. Punctuation and capitalization errors are intentionally ignored; acronym expansion (e.g. “M T C” vs “MTC”) is not automatically treated as equivalent. Manual reference text can contain errors. A transcript appearing elsewhere in the output can be a false positive for technical-term recall because occurrences are not position-aligned. **No actual microphone or recognizer was tested by this milestone.**

Next: evaluate existing HyperX SoloCast and Blue Snowball microphones with an explicitly chosen offline recognizer on Windows, using the same consented test phrases. Then decide whether opt-in, locally stored pronunciation correction is warranted. Multilingual work follows English one-on-one acceptance.
