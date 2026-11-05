#!/usr/bin/env python3
"""SIGNAL v29 read-only timeline preview on loopback 127.0.0.1:8769.
Requires original server.py from local-brain-bridge. Leaves v25-v28 untouched.
"""
import os
from http.server import ThreadingHTTPServer
from pathlib import Path
from server import Handler, MODEL
HOME=Path(__file__).resolve().parent
PORT=int(os.environ.get('SIGNAL_V29_PORT','8769'))
if not 1024<=PORT<=65535:
    raise ValueError('SIGNAL_V29_PORT must be 1024–65535')
class PreviewHandler(Handler):
    def do_GET(self):
        if self.path in ('/','/v29.html'):
            return self.send(200,(HOME/'v29.html').read_bytes(),'text/html; charset=utf-8')
        for name in ('casebook-core.js','fingerprint-core.js','correlation-core.js'):
            if self.path == '/'+name:
                return self.send(200,(HOME/name).read_bytes(),'application/javascript; charset=utf-8')
        return super().do_GET()
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',PORT),PreviewHandler)
    print(f'SIGNAL v29 local correlation preview: http://127.0.0.1:{PORT}/')
    print(f'Configured local Ollama model: {MODEL}. No hardware or network listener.')
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
