#!/usr/bin/env python3
"""Local-only SIGNAL v30 clock review preview. Leaves all older ports/installations alone."""
import os
from pathlib import Path
from http.server import ThreadingHTTPServer
from server import Handler, MODEL
HERE=Path(__file__).resolve().parent
PORT=int(os.environ.get('SIGNAL_V30_PORT','8770'))
if not 1024<=PORT<=65535:raise ValueError('Invalid preview port')
class Preview(Handler):
    def do_GET(self):
        if self.path in ('/','/v30.html'):
            return self.send(200,(HERE/'v30.html').read_bytes(),'text/html; charset=utf-8')
        if self.path in ('/casebook-core.js','/fingerprint-core.js','/correlation-core.js','/clock-core.js'):
            return self.send(200,(HERE/self.path.lstrip('/')).read_bytes(),'application/javascript; charset=utf-8')
        return super().do_GET()
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',PORT),Preview)
    print(f'SIGNAL v30 clock review: http://127.0.0.1:{PORT}/; Ollama: {MODEL}')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
