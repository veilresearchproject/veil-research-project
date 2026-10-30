# SIGNAL Desktop v0.7 — Facial motion refinement (October 30, 2026)

**Reason for revision:** v0.6 drew a dark slit on an existing closed mouth, swapped entire-face images at a fixed 180 ms rhythm, and could jump to the neutral portrait while another expression was active. Those effects were visually distracting.

**Changes:**
- Removed the artificial dark opening; new poses are generated only by tiny, bounded geometric deformation of the approved neutral portrait’s existing mouth-region pixels (maximum 2.3 original pixels). The neutral speech frame is byte-for-byte identical to neutral.webp, and other speech poses use lossless WebP encoding to avoid altering the rest of the portrait.
- No fabricated teeth or mouth interior, and no edits to the other six approved expression images.
- Speaking animation uses a nonuniform cadence with rests and now preloads its images to reduce flicker.
- Facial expressions remain steady; we do not switch an amused or focused face to a different portrait mid-speech.
- Removed whole-head zoom while talking and the automatic idle “breathing” scale.
- Added Motion: subtle / Motion: still toggle. It does not affect text conversation or Windows audio.
- Respects reduced-motion preferences, remains silent during preview, and stops the animation when speech stops.

**Limitation:** This is *not* lip sync. Without phoneme/viseme timing from the actual local TTS, it should remain restrained. Do not represent it as accurate speech animation.

**Next desktop acceptance test:** Run demo, inspect preview with Motion: subtle; switch to still; then launch local Ollama and test /voice on, speech start/stop, and whether the selected portrait remains stable. The local synthetic browser/test environment is not the real Windows hardware.
