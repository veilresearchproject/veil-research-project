"""Loopback-only Ollama chat connector for SIGNAL demo; stdlib only."""
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

class OllamaBridge:
    def __init__(self, model: str, endpoint: str = 'http://127.0.0.1:11434/api/chat', timeout: float = 45):
        parsed = urlsplit(endpoint)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost') or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path != '/api/chat':
            raise ValueError('Only the local Ollama /api/chat endpoint is allowed')
        if not model.strip() or timeout <= 0:
            raise ValueError('Model and positive timeout required')
        self.model, self.endpoint, self.timeout = model, endpoint, timeout

    def __call__(self, messages: list[dict[str, str]]) -> str:
        payload = json.dumps({'model': self.model, 'messages': messages, 'stream': False}).encode('utf-8')
        request = Request(self.endpoint, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(request, timeout=self.timeout) as response:
            data = json.load(response)
        answer = data.get('message', {}).get('content')
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError('Ollama returned no usable response')
        return answer.strip()
