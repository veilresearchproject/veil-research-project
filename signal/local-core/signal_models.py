"""Operator-selected installed Ollama models; no downloads or generation requests."""
import json
import re
from urllib import request, error

TAGS_URL = 'http://127.0.0.1:11434/api/tags'
MAX_BYTES = 256_000
NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$')


def installed_models(opener=None):
    """Read bounded local inventory, excluding explicitly remote/cloud entries."""
    opener = opener or request.urlopen
    try:
        with opener(request.Request(TAGS_URL, method='GET'), timeout=2) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Model inventory too large')
        data = json.loads(raw.decode('utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('models'), list):
            raise ValueError('Invalid model inventory')
        names = set()
        for item in data['models']:
            if not isinstance(item, dict):
                continue
            name = item.get('name')
            if not isinstance(name, str) or not NAME.fullmatch(name):
                continue
            if item.get('remote_host') or item.get('remote_model') or 'cloud' in name.lower():
                continue
            names.add(name)
        if len(names) > 100:
            raise ValueError('Too many installed models')
        return sorted(names)
    except (error.URLError, OSError, ValueError, UnicodeError, TypeError) as exc:
        raise ValueError('Could not read installed local models. Start Ollama and refresh the list.') from exc


def select_model(bot, name, confirmed, inventory=None):
    """Caller holds the session lock. Preserve all state on any validation failure."""
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError('Choose a model from the installed list')
    if name not in (inventory or installed_models)():
        raise ValueError('That model is not in the eligible installed list. Refresh and choose again.')
    if name == bot.model.model:
        return False
    if confirmed is not True:
        raise ValueError('Confirm starting a new chat before switching models')
    # No file writes: saved snapshots and source evidence remain unchanged.
    bot.voice.stop()
    bot.model.model = name
    bot.history = []
    bot.loaded_mtc = None
    bot.loaded_review = None
    return True
