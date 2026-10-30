"""SIGNAL face desktop alpha. Loopback HTTP only; standard-library Python.

Extends signal_core.Assistant and WindowsVoice; no microphone, cloud or devices.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import signal_core

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'face_assets'
FACES = ('neutral', 'focused', 'amused', 'excited', 'concentrating', 'reassuring')
STATIC = {'/': (ROOT / 'signal_face.html', 'text/html; charset=utf-8'),
          '/signal_face.css': (ROOT / 'signal_face.css', 'text/css; charset=utf-8'),
          '/signal_face.js': (ROOT / 'signal_face.js', 'text/javascript; charset=utf-8')}
STATIC.update({f'/face_assets/{name}.webp': (ASSETS / f'{name}.webp', 'image/webp') for name in FACES})
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"


class DemoModel:
    """Explicitly labeled visual rehearsal only; not an AI."""
    model = 'DEMO: deterministic rehearsal'

    def answer(self, messages):
        prompt = messages[-1]['content'].strip()
        if 'door' in prompt.lower():
            return ('That door again? Fascinating. The most repeatable phenomenon in the lab! '
                    'Still, a known source is useful evidence, not a disappointment.')
        if 'mtc' in prompt.lower() or 'recording' in prompt.lower():
            return ('For our MTC review, first verify timestamps and ordinary sources. '
                    'Please remember: this is a scripted interface demonstration, not an AI analysis.')
        return ('Good to see you. My expression controls are working, but this is a scripted demo. '
                'Start the live mode with local Ollama for actual generated conversation.')


class SessionState:
    def __init__(self, model):
        self.bot = signal_core.Assistant(model, signal_core.Memories(signal_core.default_dir()))
        self.lock = threading.Lock()
        self.mode = 'demo' if isinstance(model, DemoModel) else 'local-ollama'
        self.token = secrets.token_urlsafe(32)
        self.requests = 0

    def status(self):
        voice = self.bot.voice
        proc = voice._process
        return {'mode': self.mode, 'voice_enabled': voice.enabled,
                'speaking': proc is not None and proc.poll() is None,
                'mtc_loaded': self.bot.loaded_mtc is not None,
                'session_id': (self.bot.loaded_mtc or {}).get('session_id'),
                'mic_enabled': False, 'hardware_control': False}


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'SIGNAL-Desktop-alpha'
        sys_version = ''

        def log_message(self, format, *args):
            # No chat content, paths, tokens, or browsing-history data in logs.
            if not self.path.startswith('/api/'):
                return
            print('SIGNAL API:', self.command, self.path.split('?')[0], format % args)

        def _headers(self, status, mime, length):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(length))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Security-Policy', CSP)
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Frame-Options', 'DENY')
            self.end_headers()

        def _json(self, status, data):
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self._headers(status, 'application/json; charset=utf-8', len(payload))
            self.wfile.write(payload)

        def _allowed_host(self):
            return self.headers.get('Host', '') == f'127.0.0.1:{self.server.server_port}'

        def _authorized(self):
            origin = self.headers.get('Origin')
            return (self._allowed_host() and
                    self.headers.get('X-SIGNAL-Token') == state.token and
                    (not origin or origin == f'http://127.0.0.1:{self.server.server_port}'))

        def do_GET(self):
            if not self._allowed_host():
                self._json(403, {'error': 'Loopback host only'})
                return
            route = urlsplit(self.path).path
            if route == '/api/status':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                self._json(200, state.status())
                return
            item = STATIC.get(route)
            if not item:
                self._json(404, {'error': 'Not found'}); return
            file, mime = item
            if not file.is_file():
                self._json(404, {'error': 'Missing local asset'}); return
            payload = file.read_bytes()
            if route == '/':
                # Static HTML token is only readable to a loopback browser's same origin.
                payload = payload.replace(b'__SIGNAL_LOCAL_TOKEN__', state.token.encode('ascii'))
            self._headers(200, mime, len(payload))
            self.wfile.write(payload)

        def do_POST(self):
            route = urlsplit(self.path).path
            if not self._authorized():
                self._json(403, {'error': 'Unauthorized'}); return
            if route not in ('/api/chat', '/api/voice'):
                self._json(404, {'error': 'Not found'}); return
            try:
                size = int(self.headers.get('Content-Length', '-1'))
            except ValueError:
                size = -1
            if size < 2 or size > 8192:
                self._json(413, {'error': 'Invalid or oversized request'}); return
            try:
                data = json.loads(self.rfile.read(size).decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('Expected JSON object')
            except (UnicodeError, ValueError, json.JSONDecodeError):
                self._json(400, {'error': 'Invalid JSON'}); return
            if not state.lock.acquire(blocking=False):
                self._json(409, {'error': 'SIGNAL is still processing another request'}); return
            try:
                if route == '/api/chat':
                    message = data.get('message')
                    if not isinstance(message, str) or not 0 < len(message.strip()) <= 4000:
                        raise ValueError('Message must be 1–4,000 characters')
                    reply = state.bot.action(message.strip())
                    self._json(200, {'reply': reply, 'mode': state.mode, 'status': state.status()})
                else:
                    action = data.get('action')
                    if action not in ('on', 'off', 'stop', 'test', 'list', 'rate'):
                        raise ValueError('Unknown voice operation')
                    if action == 'rate':
                        rate = data.get('rate')
                        if isinstance(rate, bool) or not isinstance(rate, int):
                            raise ValueError('Voice rate requires an integer')
                        command = '/voice rate ' + str(rate)
                    else:
                        command = '/voice ' + action
                    message = state.bot.action(command)
                    self._json(200, {'reply': message, 'status': state.status()})
            except (RuntimeError, ValueError, OSError) as exc:
                self._json(422, {'error': str(exc)[:500]})
            finally:
                state.lock.release()

    return Handler


def make_server(model=None):
    state = SessionState(model or signal_core.LocalModel())
    server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(state))
    server.daemon_threads = True
    return server, state


def main():
    p = argparse.ArgumentParser(description='SIGNAL local-only desktop face alpha')
    p.add_argument('--demo', action='store_true', help='explicit scripted visual demo; no Ollama needed')
    p.add_argument('--no-browser', action='store_true', help='do not automatically open browser')
    args = p.parse_args()
    if os.name != 'nt':
        print('Development preview: Windows speech requires Windows. The chat interface can still be tested.')
    server, state = make_server(DemoModel() if args.demo else None)
    url = f'http://127.0.0.1:{server.server_port}/'
    print('SIGNAL desktop alpha | LOCAL ONLY |', state.mode)
    print('Open this address:', url)
    print('Press Ctrl+C to close the server. No microphone or device control.')
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        state.bot.voice.disable()
        server.server_close()
        print('SIGNAL desktop stopped.')


if __name__ == '__main__':
    main()
