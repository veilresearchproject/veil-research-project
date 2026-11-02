"""Face-state coordination around an actual blocking speaker callback."""
from expression_controller import ExpressionController, Mode
from voice_pipeline import VoicePipeline
from playback_adapter import play_remaining

class RevealStage:
    def __init__(self):
        self.face = ExpressionController()

    def speak(self, answer: str, blocking_speaker):
        """Adapter success means API acknowledged playback, not proof it was heard."""
        self.face.set_mode(Mode.THINKING)
        try:
            pipeline = VoicePipeline(answer)
            if pipeline.done:
                self.face.set_mode(Mode.IDLE)
                return True
            self.face.set_mode(Mode.SPEAKING)
            def speaker(text):
                # No real envelope measurement yet: mouth stays neutral unless supplied.
                return blocking_speaker(text)
            result = play_remaining(pipeline, speaker)
            self.face.set_mode(Mode.IDLE if result.completed else Mode.ERROR)
            return result.completed
        except Exception:
            self.face.set_mode(Mode.ERROR)
            raise

    def begin_listening(self):
        self.face.set_mode(Mode.LISTENING)

    def begin_thinking(self):
        self.face.set_mode(Mode.THINKING)

    def speech_level(self, normalized_level: float):
        self.face.update_speech_level(normalized_level)
