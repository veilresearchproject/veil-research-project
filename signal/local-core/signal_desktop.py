"""SIGNAL face desktop alpha v0.16. Loopback HTTP only; standard-library Python.

Extends signal_core.Assistant; push-to-talk is explicitly opt-in, offline and ephemeral.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import signal_core
import signal_listen
import signal_diagnostics
import signal_annotations
import signal_review_import
import signal_packet
import signal_session
import signal_models

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'face_assets'
FACES = ('neutral', 'focused', 'amused', 'excited', 'concentrating', 'reassuring')
SPEECH_POSES = tuple(f'speech_{i}' for i in range(4))
STATIC = {'/': (ROOT / 'signal_face.html', 'text/html; charset=utf-8'),
          '/signal_face.css': (ROOT / 'signal_face.css', 'text/css; charset=utf-8'),
          '/signal_face.js': (ROOT / 'signal_face.js', 'text/javascript; charset=utf-8')}
STATIC.update({f'/face_assets/{name}.webp': (ASSETS / f'{name}.webp', 'image/webp') for name in FACES + SPEECH_POSES})
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
        self.generation_cancel = threading.Event()
        self.streaming_active = False
        self.operation_lock = threading.Lock()
        self.model_operation = None
        self.mode = 'demo' if isinstance(model, DemoModel) else 'local-ollama'
        self.token = secrets.token_urlsafe(32)
        self.requests = 0
        self.listener = signal_listen.PushToTalk()
        self.review_dir = signal_core.default_dir() / 'review_notes'
        self.session_store = signal_session.SessionStore(signal_core.default_dir())

    def begin_model_operation(self, kind):
        with self.operation_lock:
            self.model_operation = {'kind': kind, 'started': time.monotonic()}

    def end_model_operation(self):
        with self.operation_lock:
            self.model_operation = None

    def operation_status(self):
        with self.operation_lock:
            operation = self.model_operation
            if operation is None:
                return None
            return {'kind': operation['kind'],
                    'elapsed_ms': max(0, round((time.monotonic() - operation['started']) * 1000)),
                    'stop_requested': self.streaming_active and self.generation_cancel.is_set()}

    def status(self):
        voice = self.bot.voice
        proc = voice._process
        progress = self.operation_status()
        return {'mode': self.mode, 'voice_enabled': voice.enabled,
                'speaking': proc is not None and proc.poll() is None,
                'mtc_loaded': self.bot.loaded_mtc is not None,
                'session_id': (self.bot.loaded_mtc or {}).get('session_id'),
                'review_loaded': self.bot.loaded_review is not None,
                'stream_supported': self.mode != 'demo' and callable(getattr(self.bot.model, 'stream_answer', None)),
                'generating': progress is not None or self.streaming_active,
                'request_progress': progress,
                'mic_enabled': self.listener.status()['state'] == 'listening', 'hardware_control': False,
                'conversation_turns': len(self.bot.history) // 2}


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'SIGNAL-Desktop-v0.16'
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
            if route == '/api/models':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                if state.mode == 'demo':
                    self._json(422, {'error': 'Start live SIGNAL desktop to choose an installed Ollama model.'}); return
                if not state.lock.acquire(timeout=0.15):
                    self._json(409, {'error': 'Finish the current request before listing models'}); return
                try:
                    self._json(200, {'models': signal_models.installed_models(),
                                     'selected': state.bot.model.model})
                except ValueError as exc:
                    self._json(422, {'error': str(exc)})
                finally:
                    state.lock.release()
                return
            if route == '/api/listen/status':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                self._json(200, state.listener.status(consume=True))
                return
            if route == '/api/status':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                self._json(200, state.status())
                return
            if route == '/api/session':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                try:
                    self._json(200, state.session_store.status())
                except signal_session.SnapshotError as exc:
                    self._json(422, {'error': str(exc)[:250]})
                return
            if route == '/api/diagnostics':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                if state.mode == 'demo':
                    self._json(200, {'mode':'scripted-demo', 'message':'Visual demo only. Start SIGNAL live desktop to run local Ollama setup checks.'})
                else:
                    self._json(200, signal_diagnostics.run_checks(state.bot.model.model, state.bot.voice))
                return
            if route == '/api/review':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                result = state.bot.loaded_review
                self._json(200, {'review': result})
                return
            if route == '/api/export':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                # No files written; browser must explicitly request local export.
                from urllib.parse import parse_qs
                requested = parse_qs(urlsplit(self.path).query)
                kind = requested.get('format', ['json'])
                if len(kind) != 1 or kind[0] not in ('json', 'html'):
                    self._json(422, {'error': 'Choose JSON or printable HTML'}); return
                if not state.lock.acquire(timeout=0.15):
                    self._json(409, {'error': 'SIGNAL is processing another request'}); return
                try:
                    packet = signal_packet.build_packet(state.bot.loaded_mtc, state.bot.loaded_review,
                                                        state.review_dir)
                    payload = (signal_packet.html_bytes(packet) if kind[0] == 'html'
                               else signal_packet.json_bytes(packet))
                    if len(payload) > signal_packet.MAX_PACKET:
                        raise signal_packet.PacketError('Packet exceeds safe export limit')
                    extension = 'html' if kind[0] == 'html' else 'json'
                    mime = ('text/html; charset=utf-8' if extension == 'html'
                            else 'application/json; charset=utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', mime)
                    self.send_header('Content-Length', str(len(payload)))
                    self.send_header('Content-Disposition',
                                     f'attachment; filename="SIGNAL_MTC_{packet["session_id"]}_review.{extension}"')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Content-Security-Policy', CSP)
                    self.send_header('Referrer-Policy', 'no-referrer')
                    self.end_headers()
                    self.wfile.write(payload)
                except (signal_packet.PacketError, signal_annotations.ReviewError,
                        ValueError, OSError) as exc:
                    self._json(422, {'error': str(exc)[:400]})
                finally:
                    state.lock.release()
                return
            if route == '/api/notes':
                if not self._authorized():
                    self._json(403, {'error': 'Unauthorized'}); return
                try:
                    self._json(200, {'notes': signal_annotations.list_notes(state.review_dir, state.bot.loaded_mtc)})
                except (signal_annotations.ReviewError, OSError) as exc:
                    self._json(422, {'error': str(exc)[:300]})
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
            if route not in ('/api/chat', '/api/voice', '/api/listen', '/api/notes', '/api/review', '/api/model-check', '/api/chat/stream', '/api/chat/stop', '/api/session', '/api/models'):
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
            # Stop operates outside the model lock so investigators can interrupt
            # a slow stream. It cannot trigger speech or alter completed history.
            if route == '/api/chat/stop':
                active = state.streaming_active
                if active:
                    state.generation_cancel.set()
                self._json(200, {'stop_requested': bool(active)})
                return
            # Deactivation must remain available during a slow model call.
            # The voice/listener own their short-lived process synchronization.
            # These branches never acquire the generation lock or start audio.
            if route == '/api/voice' and data.get('action') in ('stop', 'off'):
                try:
                    if data['action'] == 'off':
                        state.bot.voice.disable()
                        message = 'Local voice disabled.'
                    else:
                        state.bot.voice.stop()
                        message = 'Speech stopped.'
                    self._json(200, {'reply': message, 'status': state.status()})
                except (RuntimeError, OSError) as exc:
                    self._json(422, {'error': str(exc)[:500]})
                return
            if route == '/api/listen' and data.get('action') == 'stop':
                try:
                    self._json(200, state.listener.stop())
                except (RuntimeError, OSError) as exc:
                    self._json(422, {'error': str(exc)[:500]})
                return
            if not state.lock.acquire(timeout=0.15):
                self._json(409, {'error': 'SIGNAL is still processing another request'}); return
            tracks_model = False
            try:
                if ((route in ('/api/chat', '/api/chat/stream')) or
                    (route == '/api/voice' and data.get('action') == 'test')):
                    if state.listener.status()['state'] == 'listening':
                        raise ValueError('Stop listening before generating or testing speech')
                message = data.get('message')
                tracks_model = (state.mode != 'demo' and
                    (route == '/api/model-check' or
                     (route in ('/api/chat', '/api/chat/stream') and isinstance(message, str)
                      and 0 < len(message.strip()) <= 4000 and not message.lstrip().startswith('/'))))
                if tracks_model:
                    state.begin_model_operation('model-check' if route == '/api/model-check' else 'reply')
                if route == '/api/models':
                    if state.mode == 'demo':
                        raise ValueError('Model selection requires live SIGNAL desktop')
                    if state.listener.status()['state'] == 'listening':
                        raise ValueError('Stop listening before switching models')
                    changed = signal_models.select_model(state.bot, data.get('model'), data.get('confirm_reset'))
                    self._json(200, {'changed': changed, 'selected': state.bot.model.model,
                        'message': ('Model selected for this run. A new chat has started; reload evidence when needed.'
                                    if changed else 'This model is already selected. Current chat is unchanged.'),
                        'status': state.status()})
                elif route == '/api/session':
                    action = data.get('action')
                    if action == 'save':
                        result = state.session_store.save(state.bot.history)
                        self._json(200, {'message': 'Completed conversation saved locally by operator choice.', **result})
                    elif action == 'restore':
                        hist = state.session_store.restore()  # Validate before changing live state.
                        state.bot.voice.stop()
                        state.bot.history = hist
                        state.bot.loaded_mtc = None
                        state.bot.loaded_review = None
                        self._json(200, {'message': 'Chat restored. Reload MTC evidence explicitly if needed.',
                                         'history': hist, 'status': state.status()})
                    elif action == 'delete':
                        removed = state.session_store.delete()
                        self._json(200, {'message': 'Saved conversation deleted. Current conversation left unchanged.',
                                         'deleted': removed})
                    else:
                        raise ValueError('Choose save, restore or delete for conversation snapshot')
                elif route == '/api/chat/stream':
                    message = data.get('message')
                    if not isinstance(message, str) or not 0 < len(message.strip()) <= 4000:
                        raise ValueError('Message must be 1–4,000 characters')
                    if message.lstrip().startswith('/'):
                        raise ValueError('Use normal chat to run explicit SIGNAL commands')
                    if state.mode == 'demo' or not callable(getattr(state.bot.model, 'stream_answer', None)):
                        raise ValueError('Streaming requires the live local Ollama model')
                    state.generation_cancel.clear()
                    state.streaming_active = True
                    # NDJSON lets the browser render text as it arrives. The stream is
                    # loopback-only with the same token/origin protection as normal chat.
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/x-ndjson; charset=utf-8')
                    self.send_header('Cache-Control', 'no-store, no-transform')
                    self.send_header('Content-Security-Policy', CSP)
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Referrer-Policy', 'no-referrer')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.close_connection = True
                    generator = state.bot.stream_ask(message.strip(), state.generation_cancel)
                    try:
                        for event in generator:
                            if event.get('event') == 'complete':
                                event['status'] = state.status()
                            frame = json.dumps(event, ensure_ascii=False).encode('utf-8') + b'\n'
                            self.wfile.write(frame)
                            self.wfile.flush()
                    except (RuntimeError, ValueError, OSError) as exc:
                        # HTTP 200 has already been sent. An explicit error frame makes
                        # partial text visibly incomplete rather than silently accepted.
                        frame = json.dumps({'event': 'error', 'error': str(exc)[:400]}).encode('utf-8') + b'\n'
                        try:
                            self.wfile.write(frame)
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError, OSError):
                            pass
                    finally:
                        generator.close()
                        state.streaming_active = False
                elif route == '/api/model-check':
                    if state.mode == 'demo':
                        raise ValueError('Start live SIGNAL desktop, not the scripted face demo, to test Ollama')
                    # Explicit, harmless canned question. No history, memory, loaded reports, voice or mic.
                    started = time.monotonic()
                    result = state.bot.model.answer([
                        {'role': 'system', 'content': ('You are SIGNAL performing a local connectivity test. '
                           'Reply briefly and accurately. Do not claim to hear audio or verify a cause.')},
                        {'role': 'user', 'content': ('In one sentence: can MTC JSON event logs alone '
                           'prove what was audible in the recording?')}
                    ])
                    if not isinstance(result, str) or not result.strip():
                        raise RuntimeError('Ollama returned an empty response')
                    self._json(200, {'status':'responded',
                        'model':str(getattr(state.bot.model,'model','local model'))[:100],
                        'elapsed_ms':round((time.monotonic()-started)*1000),
                        'reply_preview':result.strip()[:700],
                        'limitations':'Connectivity test only; output is unverified model text. No evidence was analyzed.'})
                elif route == '/api/review':
                    action = data.get('action')
                    if action == 'clear':
                        state.bot.loaded_review = None
                        self._json(200, {'review': None})
                    elif action == 'latest':
                        result = signal_review_import.latest_report(state.bot.loaded_mtc)
                        state.bot.loaded_review = result
                        self._json(200, {'review': result})
                    elif action == 'load':
                        user_path = data.get('path')
                        if not isinstance(user_path, str) or not 0 < len(user_path) <= 1000:
                            raise ValueError('Enter the full local review_summary.json file path')
                        # Assignment happens only after complete validation.
                        result = signal_review_import.import_report(user_path, state.bot.loaded_mtc)
                        state.bot.loaded_review = result
                        self._json(200, {'review': result})
                    else:
                        raise ValueError('Choose latest, load or clear for audio-review summary')
                elif route == '/api/notes':
                    note = signal_annotations.append_note(state.review_dir, state.bot.loaded_mtc,
                                                          data.get('time_s'), data.get('classification'), data.get('note'))
                    self._json(200, {'entry': note, 'message':'Manual observation saved separately from the original evidence.'})
                elif route == '/api/listen':
                    action = data.get('action')
                    if action == 'start':
                        # Enforced server-side as well as in the browser, including multiple tabs.
                        state.bot.voice.stop()
                        self._json(200, state.listener.start())
                    elif action == 'stop':
                        self._json(200, state.listener.stop())
                    else:
                        raise ValueError('Use start or stop for push-to-talk')
                elif route == '/api/chat':
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
                if tracks_model:
                    state.end_model_operation()
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
    print('Press Ctrl+C to close. Microphone only during explicit push-to-talk; no device control.')
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        state.listener.stop()
        state.bot.voice.disable()
        server.server_close()
        print('SIGNAL desktop stopped.')


if __name__ == '__main__':
    main()
