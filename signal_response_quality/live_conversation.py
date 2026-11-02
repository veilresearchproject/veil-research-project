"""Local-only, model-agnostic conversational bridge for a human-led demo."""
from dataclasses import dataclass, field
from typing import Callable
from response_quality import check_answer

PROJECT_CONTEXT = ("SIGNAL is a prototype AI research assistant for the VEIL Research Project, "
                   "an independent evidence-first initiative founded by Andrew Underwood. "
                   "VEIL studies reported unusual environmental events using measurements, controls, "
                   "and ordinary-explanation checks. Do not invent an expansion for VEIL. "
                   "Be playful and concise, but don't claim sentience or fabricated capabilities. "
                   "When talking about sample data, explicitly call it simulated.")

@dataclass
class LiveConversation:
    """Callable receives message history and must return actual model-generated text."""
    generate: Callable[[list[dict[str, str]]], str]
    max_turns: int = 6
    history: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        if self.max_turns < 1:
            raise ValueError('max_turns must be positive')

    def ask(self, user_text: str) -> str:
        question = user_text.strip()
        if not question:
            raise ValueError('Empty question; request clarification')
        history = self.history[-2*self.max_turns:]
        messages = [{'role': 'system', 'content': PROJECT_CONTEXT}, *history,
                    {'role': 'user', 'content': question}]
        answer = self.generate(messages)
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError('No local-model response; offer typed retry')
        flags = check_answer(answer).flags
        if flags:
            raise RuntimeError('Response rejected by quality guard: ' + ', '.join(flags))
        self.history = (history + [{'role': 'user', 'content': question},
                                   {'role': 'assistant', 'content': answer.strip()}])[-2*self.max_turns:]
        return answer.strip()

    def reset(self):
        self.history.clear()
