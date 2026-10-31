# SIGNAL desktop v0.20 — Desktop feedback and persona refinement

This release follows the first confirmed successful live Ollama answer on Andrew's Windows PC.
It does not change the Ollama runtime, recorder, evidence files, public VEIL website or hardware.

- Local server reports the checked launcher release version; the browser displays it instead
  of the stale hard-coded `alpha 0.12` label. The temporary fallback label is `local alpha`.
- The built-in, clearly labeled **character greeting** no longer guesses time of day.
- The local model system instructions now set a warm, eccentric, concise research-assistant
  voice. Jokes are optional and limited to non-critical circumstances. The persona must not
  claim to see, hear, independently remember, authenticate EVP, control devices, or know time.
  It retains the authorized human Panic Box all-clear and ordinary-cause requirements.
- No prompts are transmitted to a paid/cloud model. Local voice and microphone are OFF until
  explicitly enabled. This change does not guarantee the model follows style instructions.

## Windows acceptance

1. Keep the old v0.19 folder. Extract the NEW ZIP separately. Double-click START_HERE.bat.
2. Choose 2 for local Ollama. Confirm the title shows `alpha 0.20`.
3. Confirm the intro says `Ah, there you are` rather than `Good morning`.
4. With local Ollama running, send a light introduction and a serious MTC evidence question.
   Verify the tone is warmer **and** the research answer is appropriately qualified.
5. Only after text passes, opt into Enable voice and Test voice. Then explicitly try microphone.

## Model/runtime limitation

On Andrew's earlier Windows run, Ollama first failed with a CUDA PTX toolchain error.
A manually launched server with `CUDA_VISIBLE_DEVICES=-1` yielded a successful local
`llama3.2:3b` text response; this workaround is not stored by SIGNAL, nor guaranteed on
future PC starts. If Ollama is stopped, restart the working server configuration first.

## Verification caveat

Automated unit and DOM checks validate structured prompt construction, UI metadata and
control paths, **not** whether every local model reply is humorous or scientifically sound.
Actual Windows text/audio acceptance is still an operator test.
