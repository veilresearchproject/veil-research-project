"""Orchestrate an unscripted SIGNAL demo turn, using existing conversation and stage modules."""
from dataclasses import dataclass
from live_conversation import LiveConversation
from reveal_stage import RevealStage
from expression_controller import Mode

@dataclass(frozen=True)
class TurnResult:
    answer: str | None
    spoken: bool
    status: str

class RevealSession:
    def __init__(self, generate, speaker):
        self.conversation = LiveConversation(generate)
        self.stage = RevealStage()
        self.speaker = speaker

    def ask(self, question: str) -> TurnResult:
        self.stage.begin_listening()
        try:
            self.stage.begin_thinking()
            answer = self.conversation.ask(question)
        except (ValueError, RuntimeError, OSError, TimeoutError) as exc:
            self.stage.face.set_mode(Mode.ERROR)
            return TurnResult(None, False, type(exc).__name__)
        try:
            complete = self.stage.speak(answer, self.speaker)
        except Exception as exc:
            self.stage.face.set_mode(Mode.ERROR)
            return TurnResult(answer, False, type(exc).__name__)
        return TurnResult(answer, complete, 'complete' if complete else 'playback_failed')
