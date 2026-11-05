#!/usr/bin/env python3
"""Independent SIGNAL v28 fingerprint preview at loopback 127.0.0.1:8768.
Requires original local-brain-bridge/server.py. Never modifies v25/v26/v27.
"""
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
from server import Handler, MODEL
HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get('SIGNAL_V28_PORT', '8768'))
if not 1024 <= PORT <= 65535:
    raise ValueError('SIGNAL_V28_PORT must be 1024–65535')

class PreviewHandler(Handler):
    def do_GET(self):
        if self.path in ('/', '/v28.html'):
            return self.send(200, (HERE/'v28.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/casebook-core.js':
            return self.send(200, (HERE/'casebook-core.js').read_bytes(), 'application/javascript; charset=utf-8')
        if self.path == '/fingerprint-core.js':
            return self.send(200, (HERE/'fingerprint-core.js').read_bytes(), 'application/javascript; charset=utf-8')
        return super().do_GET()

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), PreviewHandler)
    print(f'SIGNAL v28 local fingerprint preview: http://127.0.0.1:{PORT}/')
    print(f'Configured local Ollama model: {MODEL}. No internet or cloud listener.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
