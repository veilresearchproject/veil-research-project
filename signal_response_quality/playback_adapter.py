"""Adapter between VoicePipeline and a blocking audio output function.

The audio callback MUST return True only after playback actually completes.
Queuing an audio buffer is not a successful acknowledgement.
"""
from dataclasses import dataclass
from typing import Callable, Protocol

class Pipeline(Protocol):
    @property
    def done(self) -> bool: ...
    def next_chunk(self) -> tuple[int, str] | None: ...
    def confirm_played(self, index: int) -> None: ...
    def fail_chunk(self, index: int) -> None: ...
    def retry_failed(self) -> int: ...

@dataclass(frozen=True)
class PlaybackResult:
    completed: bool
    played_now: int
    failed_index: int | None
    error: str | None = None

def play_remaining(pipeline: Pipeline, play_blocking: Callable[[str], bool]) -> PlaybackResult:
    """Play in order, fail closed; retry must be explicitly requested."""
    played = 0
    while (next_item := pipeline.next_chunk()) is not None:
        index, text = next_item
        try:
            confirmed = play_blocking(text)
        except Exception as exc:
            pipeline.fail_chunk(index)
            return PlaybackResult(False, played, index, type(exc).__name__)
        if confirmed is not True:
            pipeline.fail_chunk(index)
            return PlaybackResult(False, played, index, "playback_not_confirmed")
        pipeline.confirm_played(index)
        played += 1
    return PlaybackResult(pipeline.done, played, None if pipeline.done else -1,
                          None if pipeline.done else "playback_paused")
