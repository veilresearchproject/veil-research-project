#!/usr/bin/env python3
"""SIGNAL v38 standalone local-only preview: v33 brain + optional approved memory.

Only the operator controls local memory. No automatic recording, AI memory injection,
remote hardware, transcription, or camera/microphone capture.
"""
import json
import os
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit
from signal_local_v33 import make_handler, model_name, port
import memory_v34

HERE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('SIGNAL_LAB_DATA_DIR', str(Path.home() / '.veil_signal_lab')))
STATIC = {'/': 'v38_lab.html', '/v38_lab.html': 'v38_lab.html',
          '/voice-core.js': 'voice-core.js', '/assignments-core.js': 'assignments-core.js',
          '/audio-core.js': 'audio-core.js', '/dashboard-core.js': 'dashboard-core.js'}


def make_lab_handler(ollama_port, model, directory=DATA_DIR):
    base = make_handler(ollama_port, model)

    class Handler(base):
        server_version = 'SIGNAL-Local-v38'

        def do_GET(self):
            if not self.headers_safe():
                return self.emit(403, {'error': 'Local host only'})
            path = urlsplit(self.path).path
            if path == '/api/memory':
                try:
                    return self.emit(200, memory_v34.load(directory))
                except (OSError, ValueError, json.JSONDecodeError):
                    return self.emit(500, {'error': 'Local memory unavailable. Nothing changed.'})
            if path in STATIC:
                name = STATIC[path]
                try:
                    content = (HERE / name).read_bytes()
                except OSError:
                    return self.emit(500, {'error': 'Preview file missing'})
                kind = 'text/html; charset=utf-8' if name.endswith('.html') else 'application/javascript; charset=utf-8'
                return self.emit(200, content, kind)
            return super().do_GET()

        def do_POST(self):
            path = urlsplit(self.path).path
            if path not in ('/api/memory/add', '/api/memory/remove', '/api/memory/clear'):
                return super().do_POST()
            if not self.headers_safe() or self.headers.get('Origin') != 'http://' + self.headers['Host']:
                return self.emit(403, {'error': 'Local same-origin browser only'})
            if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Type', '').split(';', 1)[0].strip().lower() != 'application/json':
                return self.emit(415, {'error': 'Only JSON with Content-Length supported'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                return self.emit(400, {'error': 'Invalid request length'})
            if not 1 <= size <= 4096:
                return self.emit(413, {'error': 'Memory request too large'})
            try:
                payload = json.loads(self.rfile.read(size))
                if path.endswith('/add'):
                    result = memory_v34.add(directory, payload)
                elif path.endswith('/remove'):
                    result = memory_v34.remove(directory, payload)
                else:
                    result = memory_v34.clear(directory, payload)
                return self.emit(200, {'ok': True, 'result': result})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                return self.emit(400, {'error': str(exc)[:140]})
            except OSError:
                return self.emit(500, {'error': 'Memory storage unavailable. Nothing sent to AI.'})

    return Handler


def serve():
    preview_port = port(os.environ.get('SIGNAL_V38_PORT', '8773'), 'preview port')
    ollama_port = port(os.environ.get('SIGNAL_OLLAMA_PORT', '11434'), 'Ollama port')
    model = model_name(os.environ.get('SIGNAL_MODEL', 'llama3.2:3b'))
    server = ThreadingHTTPServer(('127.0.0.1', preview_port), make_lab_handler(ollama_port, model))
    server.daemon_threads = True
    print('SIGNAL v38 independent preview: http://127.0.0.1:%d/ (not on LAN)' % preview_port)
    print('Approved local memories stay in %s. No automatic AI memory use or hardware control.' % DATA_DIR)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    serve()
