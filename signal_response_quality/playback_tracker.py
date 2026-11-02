"""Sequential TTS playback acknowledgement tracker; does not play audio."""
from dataclasses import dataclass

@dataclass
class PlaybackTracker:
    total_chunks: int
    completed_chunks: int = 0
    failed: bool = False

    def __post_init__(self):
        if type(self.total_chunks) is not int or self.total_chunks < 1:
            raise ValueError("total_chunks must be a positive integer")

    @property
    def done(self) -> bool:
        return self.completed_chunks == self.total_chunks and not self.failed

    @property
    def next_index(self) -> int | None:
        if self.failed or self.done:
            return None
        return self.completed_chunks

    def confirm_completed(self, index: int) -> None:
        if self.failed:
            raise RuntimeError("Playback failed; explicitly resume first")
        if self.done or type(index) is not int or index != self.completed_chunks:
            raise ValueError("Unexpected or duplicate chunk completion")
        self.completed_chunks += 1

    def mark_failed(self, index: int) -> None:
        if self.done or type(index) is not int or index != self.completed_chunks:
            raise ValueError("Only the current chunk can fail")
        self.failed = True

    def resume_failed_chunk(self) -> int:
        if not self.failed:
            raise RuntimeError("No failed chunk to resume")
        self.failed = False
        return self.completed_chunks
