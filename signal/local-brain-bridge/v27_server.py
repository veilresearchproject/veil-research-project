#!/usr/bin/env python3
"""Independent SIGNAL v27 preview on loopback port 8767.

Requires original server.py from the SIGNAL local-brain-bridge folder.
Never changes v25 or v26; does not start or install Ollama.
"""
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
from server import Handler, MODEL

HOME = Path(__file__).resolve().parent
PORT = int(os.environ.get('SIGNAL_V27_PORT', '8767'))
if not 1024 <= PORT <= 65535:
    raise ValueError('SIGNAL_V27_PORT must be 1024–65535')

class PreviewHandler(Handler):
    def do_GET(self):
        if self.path in ('/', '/v27.html'):
            return self.send(200, (HOME / 'v27.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/casebook-core.js':
            return self.send(200, (HOME / 'casebook-core.js').read_bytes(), 'application/javascript; charset=utf-8')
        return super().do_GET()

if __name__ == '__main__':
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), PreviewHandler)
    print(f'SIGNAL v27 Casebook preview: http://127.0.0.1:{PORT}/')
    print(f'Ollama model configured: {MODEL}. Preview runs on this computer only.')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
