"""Small, offline text-to-speech queue planner. Does not play audio."""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class SpeechPlan:
    chunks: tuple[str, ...]
    original: str

    def verified_complete(self, played_chunks: int) -> bool:
        """Only true if the caller confirms every planned chunk finished playback."""
        return played_chunks == len(self.chunks)

def plan_speech(text: str, max_chars: int = 220) -> SpeechPlan:
    """Split on sentence/word boundaries; never discard words or silently truncate."""
    if max_chars < 20:
        raise ValueError('max_chars must be >= 20')
    normalized = ' '.join(text.split())
    if not normalized:
        return SpeechPlan((), normalized)
    sentences = re.split(r'(?<=[.!?])\s+', normalized)
    chunks = []
    current = ''
    for sentence in sentences:
        words = sentence.split(' ')
        for word in words:
            if len(word) > max_chars:
                raise ValueError('word exceeds max_chars; refusing to truncate')
            candidate = (current + ' ' + word).strip()
            if len(candidate) > max_chars:
                chunks.append(current)
                current = word
            else:
                current = candidate
    if current:
        chunks.append(current)
    assert ' '.join(chunks) == normalized
    return SpeechPlan(tuple(chunks), normalized)
