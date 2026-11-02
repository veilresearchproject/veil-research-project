"""Offline coordinator for SIGNAL response validation and playback acknowledgement.

Does not synthesize or play audio; caller must report actual playback completion.
"""
from response_quality import check_answer
from voice_queue import plan_speech
from playback_tracker import PlaybackTracker

class VoicePipeline:
    def __init__(self, answer: str, max_chars: int = 220):
        quality = check_answer(answer)
        if not quality.acceptable:
            raise ValueError('Unsafe answer for speech: ' + ', '.join(quality.flags))
        self.plan = plan_speech(answer, max_chars=max_chars)
        self.tracker = PlaybackTracker(len(self.plan.chunks)) if self.plan.chunks else None

    @property
    def done(self):
        return self.tracker is None or self.tracker.done

    def next_chunk(self):
        if self.tracker is None or self.tracker.next_index is None:
            return None
        index = self.tracker.next_index
        return index, self.plan.chunks[index]

    def confirm_played(self, index: int):
        if self.tracker is None:
            raise ValueError('No audio segments to confirm')
        self.tracker.confirm_completed(index)

    def fail_chunk(self, index: int):
        if self.tracker is None:
            raise ValueError('No audio segments to fail')
        self.tracker.mark_failed(index)

    def retry_failed(self):
        if self.tracker is None:
            raise ValueError('No audio segments to retry')
        return self.tracker.resume_failed_chunk()
