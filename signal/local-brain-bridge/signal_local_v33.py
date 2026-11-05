#!/usr/bin/env python3
"""SIGNAL v33: standalone, local-only preview server for v31 geometric Casebook.

No dependency on the original v25/v26 Python server. No cloud access, writes,
model download, microphone access, original evidence reads or instrument control.
Standard library only. Optional Ollama endpoint is fixed to localhost.
"""
import json
import os
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

HERE=Path(__file__).resolve().parent
FILES={
 '/':'v33.html','/v33.html':'v33.html','/v31.html':'v31.html',
 '/casebook-core.js':'casebook-core.js',
 '/fingerprint-core.js':'fingerprint-core.js',
 '/correlation-core.js':'correlation-core.js',
 '/clock-core.js':'clock-core.js',
 '/blind-core.js':'blind-core.js',
}
ROLE_PROMPT='''You are SIGNAL, a quick-witted but disciplined local research-assistant prototype for Andrew Underwood's independent VEIL Research Project.
VEIL studies reported anomalous environmental events using measurements, controls, original recordings, ordinary explanations first, and documented uncertainty. The VEIL Research Center is a proposed future facility, not an existing staffed lab.
You have NOT inspected user files, audio, cameras, instruments, websites or sensors in this conversation. Never invent measurements, test results, or paranormal proof. Do not state that uncertainty is evidence of spirits.
MTC is an unattended pre-recorded-question experiment requiring continuous recordings and independent corroboration. Panic Box is a proposed event-preservation system whose ALL CLEAR is human-authorized only.
You are software, not a conscious person. Respond helpfully in 2-5 sentences by default; dry, playful humor is appropriate when safe. Ask for corroboration and propose testable next steps. No equipment control is available.'''
DENIED=re.compile(r'\b(?:activate|arm|disarm|reset|unlock|turn on|turn off|erase|delete|override|disable)\b.{0,80}\b(?:panic box|mtc|generator|sensors?|alarm|recordings?|evidence|all clear)\b',re.I|re.S)


def port(value,name):
    try:n=int(value)
    except (ValueError,TypeError):raise ValueError('Invalid '+name) from None
    if not 1024<=n<=65535:raise ValueError('Invalid '+name)
    return n


def model_name(value):
    if not isinstance(value,str) or '://' in value or not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,80}',value):
        raise ValueError('Invalid local model name')
    return value


def validate(payload):
    if not isinstance(payload,dict):raise ValueError('Expected JSON object')
    question=payload.get('question')
    if not isinstance(question,str) or not question.strip() or len(question)>800:raise ValueError('Question must be 1–800 characters')
    if DENIED.search(question):raise ValueError('Equipment-control requests are not supported. Ask for research advice only.')
    history=payload.get('history',[])
    if not isinstance(history,list) or len(history)>12:raise ValueError('History limited to 12 messages')
    clean=[]
    for e in history:
        if not isinstance(e,dict) or e.get('role') not in ('user','assistant') or not isinstance(e.get('content'),str) or len(e['content'])>1600:
            raise ValueError('Invalid conversation history')
        clean.append({'role':e['role'],'content':e['content']})
    return question.strip(),clean


def make_handler(ollama_port,model):
    target='http://127.0.0.1:%s'%port(ollama_port,'Ollama port')
    model=model_name(model)
    class Handler(BaseHTTPRequestHandler):
        server_version='SIGNAL-Local-v33'
        sys_version=''
        def log_message(self,*_):pass  # no URL/prompt logs
        def headers_safe(self):
            return self.headers.get('Host','') in ('localhost:%s'%self.server.server_port,'127.0.0.1:%s'%self.server.server_port)
        def emit(self,status,data,kind='application/json; charset=utf-8'):
            if not isinstance(data,bytes):data=json.dumps(data,ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'none'; form-action 'none'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)
        def ollama(self,path,data=None,seconds=3):
            request=Request(target+path,
              data=json.dumps(data).encode('utf-8') if data is not None else None,
              headers={'Content-Type':'application/json'} if data is not None else {},
              method='POST' if data is not None else 'GET')
            with urlopen(request,timeout=seconds) as r:
                if r.status!=200:raise ValueError('Local model returned an unexpected status')
                raw=r.read(1024*1024+1)
                if len(raw)>1024*1024:raise ValueError('Local model response exceeds 1 MiB')
            return json.loads(raw)
        def do_GET(self):
            if not self.headers_safe():return self.emit(403,{'error':'Local host only'})
            path=urlsplit(self.path).path
            if path=='/api/health':
                try:
                    response=self.ollama('/api/tags')
                    models=response.get('models',[]) if isinstance(response,dict) else []
                    names={x.get('name') for x in models[:100] if isinstance(x,dict)} if isinstance(models,list) else set()
                    ready=model in names
                    return self.emit(200,{'reachable':True,'model_ready':ready,'model':model,
                                          'detail':'Installed model ready.' if ready else 'Requested model is not installed locally.'})
                except (ValueError,OSError,HTTPError,URLError,TimeoutError,TypeError,json.JSONDecodeError):
                    return self.emit(200,{'reachable':False,'model_ready':False,'model':model,
                                          'detail':'Local Ollama unavailable. Scripted mode remains available.'})
            name=FILES.get(path)
            if not name:return self.emit(404,{'error':'Not found'})
            try:content=(HERE/name).read_bytes()
            except OSError:return self.emit(500,{'error':'Required preview file missing'})
            kind='text/html; charset=utf-8' if name.endswith('.html') else 'application/javascript; charset=utf-8'
            return self.emit(200,content,kind)
        def do_POST(self):
            if not self.headers_safe():return self.emit(403,{'error':'Local host only'})
            if urlsplit(self.path).path!='/api/chat':return self.emit(404,{'error':'Not found'})
            origin=self.headers.get('Origin','')
            if origin!='http://'+self.headers['Host']:
                return self.emit(403,{'error':'Same-origin local browser only'})
            if self.headers.get('Transfer-Encoding'):
                return self.emit(400,{'error':'Transfer encoding unsupported'})
            if self.headers.get('Content-Type','').split(';',1)[0].strip().lower()!='application/json':
                return self.emit(415,{'error':'Expected application/json'})
            try:size=int(self.headers.get('Content-Length','0'))
            except ValueError:return self.emit(400,{'error':'Bad request size'})
            if not 1<=size<=30000:return self.emit(413,{'error':'Request exceeds limit'})
            try:
                payload=json.loads(self.rfile.read(size))
                question,history=validate(payload)
                data=self.ollama('/api/chat',{'model':model,'stream':False,
                   'messages':[{'role':'system','content':ROLE_PROMPT},*history,{'role':'user','content':question}],
                   'options':{'temperature':0.55,'num_predict':220},'keep_alive':'2m'},seconds=90)
                msg=data.get('message') if isinstance(data,dict) else None
                answer=msg.get('content') if isinstance(msg,dict) else None
                if not isinstance(answer,str) or not answer.strip():raise ValueError('Empty local model reply')
                return self.emit(200,{'reply':answer.strip()[:1600],'mode':'local-model','model':model})
            except (ValueError,TypeError,json.JSONDecodeError) as e:
                return self.emit(400,{'error':str(e)[:150]})
            except (OSError,HTTPError,URLError,TimeoutError):
                return self.emit(503,{'error':'Local model unavailable; scripted mode works.'})
            except Exception:
                return self.emit(502,{'error':'Unexpected local model error. No evidence was saved.'})
        def do_OPTIONS(self):return self.emit(405,{'error':'Method not allowed'})
    return Handler


def serve(preview_port=8772,ollama_port=11434,model='llama3.2:3b'):
    server=ThreadingHTTPServer(('127.0.0.1',port(preview_port,'SIGNAL preview port')),make_handler(ollama_port,model))
    server.daemon_threads=True
    print('SIGNAL v33 standalone local preview at http://127.0.0.1:%s/'%server.server_port)
    print('Configured installed model: %s. No cloud, installations, file logs or device control.'%model)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':
    serve(os.environ.get('SIGNAL_V33_PORT','8772'),os.environ.get('SIGNAL_OLLAMA_PORT','11434'),os.environ.get('SIGNAL_MODEL','llama3.2:3b'))
