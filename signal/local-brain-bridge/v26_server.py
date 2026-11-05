#!/usr/bin/env python3
"""Standalone SIGNAL v26 preview server; shares v0.1 loopback Ollama bridge.

Runs at 127.0.0.1:8766, leaving a v25/old server on 8765 untouched.
Run from the local-brain-bridge directory with `py -3 v26_server.py`.
"""
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
from server import Handler, MODEL  # Reuse reviewed, loopback-only model routes.

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get('SIGNAL_V26_PORT', '8766'))
if not 1024 <= PORT <= 65535:
    raise ValueError('SIGNAL_V26_PORT must be 1024–65535')

class PreviewHandler(Handler):
    def do_GET(self):
        if self.path in ('/', '/v26.html'):
            return self.send(200, (HERE / 'v26.html').read_bytes(), 'text/html; charset=utf-8')
        return super().do_GET()

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), PreviewHandler)
    print(f'SIGNAL v26 geometric preview: http://127.0.0.1:{PORT}/')
    print(f'Uses local Ollama model {MODEL}; no public-network listener or cloud service.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
