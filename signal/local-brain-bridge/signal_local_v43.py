#!/usr/bin/env python3
"""SIGNAL v43 unified single-operator localhost preview, no real device control.

Inherits v38 local-memory and v33 Ollama browser safeguards; adds only
allowlisted static assets. The browser itself does optional local WAV analysis.
"""
import os
from pathlib import Path
from urllib.parse import urlsplit
from http.server import ThreadingHTTPServer
from signal_local_v38 import make_lab_handler
from signal_local_v33 import model_name, port

HERE = Path(__file__).resolve().parent
STATIC = {'/':'v43_lab.html','/v43_lab.html':'v43_lab.html',
          '/workflow-core.js':'workflow-core.js','/packet-core.js':'packet-core.js'}


def make_unified_handler(ollama_port, model, directory=None):
    if directory is None:
        from signal_local_v38 import DATA_DIR
        directory = DATA_DIR
    previous = make_lab_handler(ollama_port, model, directory)
    class Handler(previous):
        server_version = 'SIGNAL-Local-v43'
        def do_GET(self):
            if not self.headers_safe():
                return self.emit(403, {'error':'Local host only'})
            path = urlsplit(self.path).path
            if path in STATIC:
                name = STATIC[path]
                try:
                    data = (HERE / name).read_bytes()
                except OSError:
                    return self.emit(500, {'error':'Preview asset missing'})
                kind = ('text/html; charset=utf-8' if name.endswith('.html')
                        else 'application/javascript; charset=utf-8')
                return self.emit(200,data,kind)
            return super().do_GET()
    return Handler


def serve():
    preview_port = port(os.environ.get('SIGNAL_V43_PORT','8774'),'preview port')
    ollama_port = port(os.environ.get('SIGNAL_OLLAMA_PORT','11434'),'Ollama port')
    model = model_name(os.environ.get('SIGNAL_MODEL','llama3.2:3b'))
    server = ThreadingHTTPServer(('127.0.0.1',preview_port), make_unified_handler(ollama_port,model))
    server.daemon_threads = True
    print('SIGNAL v43 unified preview: http://127.0.0.1:%d/' % preview_port)
    print('Local-first, no automatic evidence upload, model access opt-in on geometric companion.')
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':
    serve()
