"""UI-independent expression state mapping; no camera/audio or playback claims."""
from dataclasses import dataclass
from enum import Enum

class Mode(str, Enum):
    IDLE = 'idle'
    LISTENING = 'listening'
    THINKING = 'thinking'
    SPEAKING = 'speaking'
    ERROR = 'error'

@dataclass(frozen=True)
class Expression:
    mode: Mode
    mouth_open: float
    eyebrow_raise: float
    blink_allowed: bool

class ExpressionController:
    def __init__(self):
        self.mode = Mode.IDLE
        self.level = 0.0

    def set_mode(self, mode: Mode):
        if not isinstance(mode, Mode):
            raise ValueError('Unknown expression mode')
        self.mode = mode
        self.level = 0.0

    def update_speech_level(self, level: float):
        if not isinstance(level, (int, float)) or level != level or not 0 <= level <= 1:
            raise ValueError('Speech level must be between 0 and 1')
        self.level = float(level) if self.mode == Mode.SPEAKING else 0.0

    def snapshot(self) -> Expression:
        eyebrows = {Mode.IDLE:0.15, Mode.LISTENING:0.5, Mode.THINKING:0.25,
                    Mode.SPEAKING:0.3, Mode.ERROR:0.75}[self.mode]
        return Expression(self.mode, round(self.level * 0.85, 3), eyebrows,
                          self.mode not in (Mode.ERROR,))
