"""Map real normalized PCM sample frames to smooth expression levels.

Caller provides samples from actual audio output. This module does not capture
sound, guess phonemes from text, or prove audio was audible.
"""
from math import isfinite, sqrt
from expression_controller import ExpressionController, Mode

class AudioExpressionDriver:
    def __init__(self, face: ExpressionController, attack=0.65, release=0.25, noise_floor=0.02):
        for name, value in (("attack", attack), ("release", release), ("noise_floor", noise_floor)):
            if not isinstance(value, (int, float)) or not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and in [0, 1]")
        self.face = face
        self.attack = attack
        self.release = release
        self.noise_floor = noise_floor
        self.smoothed = 0.0

    def feed_pcm(self, samples):
        """One mono or interleaved float PCM frame with values in [-1,1]."""
        if self.face.mode != Mode.SPEAKING:
            self.smoothed = 0.0
            self.face.update_speech_level(0.0)
            return 0.0
        values = tuple(samples)
        if not values:
            raise ValueError("Empty audio frame")
        if any(not isinstance(v, (int, float)) or not isfinite(v) or abs(v) > 1 for v in values):
            raise ValueError("PCM samples must be finite normalized floats")
        rms = sqrt(sum(float(v) ** 2 for v in values) / len(values))
        level = max(0.0, (rms - self.noise_floor) / max(1e-9, 1 - self.noise_floor))
        speed = self.attack if level > self.smoothed else self.release
        self.smoothed += (level - self.smoothed) * speed
        self.face.update_speech_level(self.smoothed)
        return self.face.snapshot().mouth_open

    def stop(self):
        self.smoothed = 0.0
        self.face.update_speech_level(0.0)
