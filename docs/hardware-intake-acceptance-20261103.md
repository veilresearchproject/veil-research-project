# VEIL hardware intake and acceptance plan — 2026-11-03

Status: draft engineering process. No equipment performance is certified by this file.

## Two equipment paths
**Mini MTC candidate:** >=8 GB RAM, >=4 logical CPU cores, >=64 GB available SSD space; reliable USB audio capture/output and no sleep/reboot during unattended sessions. Power needs to be evaluated separately. Check independent recording and clock synchronization.

**SIGNAL local AI candidate:** >=16 GB RAM, >=8 logical CPU cores, >=100 GB available SSD space as a starting CPU-only planning floor. Strong preference for 32 GB RAM, a modern SSD, and a supported GPU with enough VRAM for the selected model; GPU compatibility is software-dependent. Our current llama3.2:3b CPU path works, so a donated GPU must not be treated as essential or assumed compatible.

These are *screening targets*, not validated minimum requirements. A 48-hour MTC run is a design aspiration, not an achieved milestone.

## Information requested from every donor
- Make/model, processor, RAM, SSD installed and *available* storage, OS/license, connectivity/ports
- Power adapter and whether included, physical condition, known defects, warranty status
- Loan versus donation, return date, shipping responsibilities and costs, any restrictions
- Photos of label/ports; no serial numbers or sensitive information in public issue threads
- Written permission and exact wording for any acknowledgement (no guaranteed positive review)

## Read-only triage
From repository root:
`python tools/hardware_triage.py tools/example_hardware.json`
`python -m unittest discover -s tools -p "test_hardware_triage.py"`

The tool's assessment is only a candidate filter. **Do not run untrusted donated hardware on the VEIL network or connect it to evidence storage before inspection and clean OS installation.**

## Mini MTC acceptance tests
1. Cold boot, health check, USB microphone and speaker detection
2. Record question playback and microphone input in the same session
3. Test no clipping or dropouts with known test tone, speech, and silence
4. Run a documented 90-minute unattended test; inspect WAV headers, discontinuities and logs
5. Repeat across power cycles; expand to overnight endurance testing after passing
6. Verify independently timestamped second camera/audio recorder where available
7. Preserve raw files and SHA-256 digests; annotate environmental confounders

## SIGNAL desktop acceptance tests
1. Verify offline Ollama model loads with local bridge, without network access
2. Ask ten known prompts; record median/max response latency (not a pass/fail claim)
3. Confirm audio I/O, voice playback and interruption behavior
4. Stress-test sustained use; monitor fan/thermal behavior and RAM usage
5. Confirm no recording, model, or analysis data is uploaded by default

## Outreach integrity
VEIL is an independent research initiative developing methods, prototypes, and software. Do not describe a staffed physical research center as operational. Evaluation findings should be reported fairly even if donated equipment underperforms.
