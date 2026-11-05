#!/usr/bin/env python3
"""SIGNAL v33 local readiness checks. Offline by default, no changes to v25.

Run: py -3 signal_doctor.py
Opt-in extra tests: py -3 signal_doctor.py --tests
Opt-in local-only Ollama check: py -3 signal_doctor.py --check-ollama
Machine output: py -3 signal_doctor.py --json

No downloads, cloud APIs, file modification, model activation or instrument control.
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
REQUIRED = ('v33.html','signal_local_v33.py','casebook-core.js','fingerprint-core.js',
            'correlation-core.js','clock-core.js','blind-core.js')
TEST_SCRIPTS = ('test_casebook.cjs','test_fingerprint.cjs','test_correlation.cjs',
                'test_clock.cjs','test_blind.cjs','test_v33_ui.cjs')


def result(check, status, detail):
    return {'check':check, 'status':status, 'detail':detail}


def inspect_files(folder):
    findings=[]
    for name in REQUIRED:
        p=folder/name
        if not p.is_file():
            findings.append(result('file:'+name,'FAIL','Required preview file is missing.'))
        elif p.is_symlink():
            findings.append(result('file:'+name,'FAIL','Symbolic-link preview file rejected.'))
        elif p.stat().st_size<80 or p.stat().st_size>2_000_000:
            findings.append(result('file:'+name,'FAIL','Unexpected file size; inspect source.'))
        else:
            findings.append(result('file:'+name,'PASS','Present; content authenticity not certified.'))
    return findings


def inspect_runtime():
    findings=[]
    findings.append(result('python','PASS' if sys.version_info>=(3,9) else 'FAIL',
                           'Python %s.%s running.'%(sys.version_info.major,sys.version_info.minor)))
    node=shutil.which('node')
    findings.append(result('node','PASS' if node else 'WARN',
                           'Node.js available for optional offline test execution.' if node else 'Node.js not found; optional JavaScript tests cannot run here.'))
    return findings


def compile_preview(folder):
    p=folder/'signal_local_v33.py'
    if not p.is_file():return result('python-syntax','FAIL','Preview server file missing.')
    try:
        compile(p.read_text(encoding='utf-8'),str(p),'exec')
        return result('python-syntax','PASS','Preview server Python syntax compiles without executing it.')
    except (UnicodeError, OSError, SyntaxError, ValueError):
        return result('python-syntax','FAIL','Preview server Python source could not compile.')


def run_test_scripts(folder):
    node=shutil.which('node')
    if not node:
        return [result('node-tests','WARN','Node.js missing; no script was executed.')]
    reports=[]
    for name in TEST_SCRIPTS:
        if not (folder/name).is_file():
            reports.append(result('test:'+name,'WARN','Test script missing; no test executed.'))
            continue
        try:
            run=subprocess.run([node,str(folder/name)],cwd=str(folder),timeout=25,
                               capture_output=True,text=True,check=False,env=os.environ.copy())
            if run.returncode==0 and re.search(r'\b\d+/\d+\b',run.stdout):
                summary=[x.strip() for x in run.stdout.splitlines() if re.search(r'\b\d+/\d+\b',x)]
                reports.append(result('test:'+name,'PASS',(summary[-1] if summary else 'Test passed.')[:170]))
            else:
                reports.append(result('test:'+name,'FAIL','Node test did not finish cleanly; run script manually for diagnostic detail.'))
        except (OSError,subprocess.TimeoutExpired):
            reports.append(result('test:'+name,'FAIL','Node test failed to start or exceeded 25 seconds.'))
    return reports


def run_http_integration(folder):
    path=folder/'test_local_v33.py'
    if not path.is_file():return result('http-integration','WARN','HTTP integration test script missing.')
    try:
        proc=subprocess.run([sys.executable,'-m','unittest','-q','test_local_v33'],cwd=str(folder),
                            capture_output=True,text=True,timeout=25,check=False)
        if proc.returncode==0 and 'Ran 26 tests' in proc.stderr:
            return result('http-integration','PASS','26/26 local HTTP server integration tests passed with fake Ollama.')
        return result('http-integration','FAIL','HTTP integration test failed; run the script directly for details.')
    except (OSError,subprocess.TimeoutExpired):
        return result('http-integration','FAIL','HTTP integration test failed to start or timed out.')


def check_ollama(model):
    if not isinstance(model,str) or '://' in model or not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,80}',model):
        return result('local-ollama','FAIL','Invalid local model name; no network request made.')
    try:
        request=Request('http://127.0.0.1:11434/api/tags',headers={'Accept':'application/json'},method='GET')
        with urlopen(request,timeout=2) as resp:
            if resp.status!=200:raise ValueError('Local Ollama unexpected status')
            data=resp.read(65537)
            if len(data)>65536:raise ValueError('Local Ollama response too large')
            tags=json.loads(data.decode('utf-8'))
        models=tags.get('models',[]) if isinstance(tags,dict) else []
        if not isinstance(models,list):raise ValueError('Model list is not valid')
        names={m.get('name') for m in models[:100] if isinstance(m,dict) and isinstance(m.get('name'),str)}
        if model in names:return result('local-ollama','PASS','Local Ollama responds and the requested installed model is listed.')
        return result('local-ollama','WARN','Local Ollama responds, but the configured model was not listed. No model was downloaded.')
    except (OSError,ValueError,UnicodeError,HTTPError,URLError,TimeoutError,TypeError,json.JSONDecodeError):
        return result('local-ollama','WARN','Local Ollama model unavailable or not responding. Nothing was started or downloaded.')


def inspect_port(port=8772):
    try:
        with socket.create_connection(('127.0.0.1',port),timeout=0.3):
            return result('preview-port','WARN','Local preview port already has a listener; choose another port before launching.')
    except OSError:
        return result('preview-port','PASS','Local preview port not accepting connections at inspection time.')


def audit(folder=ROOT,*,tests=False,ollama=False,port=False,model='llama3.2:3b'):
    report=inspect_files(folder)+inspect_runtime()+[compile_preview(folder)]
    if tests:report+=run_test_scripts(folder)+[run_http_integration(folder)]
    else:report.append(result('node-tests','SKIP','Use --tests to run deterministic Node tests.'))
    if ollama:report.append(check_ollama(model))
    else:report.append(result('local-ollama','SKIP','Use --check-ollama for opt-in loopback-only model lookup.'))
    if port:report.append(inspect_port())
    else:report.append(result('preview-port','SKIP','Use --check-port for opt-in port check.'))
    totals={s:sum(x['status']==s for x in report) for s in ('PASS','WARN','FAIL','SKIP')}
    launch_ready=(totals['FAIL']==0 and any(x['check']=='file:signal_local_v33.py' and x['status']=='PASS' for x in report))
    return {'schema':'signal-readiness-v32','version':1,'launch_ready':launch_ready,'results':report,'totals':totals,
            'note':'Readiness check only. Device speech, v25, physical hardware, media authenticity and scientific outcomes were not tested.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description='SIGNAL v33 offline-first readiness audit. Never installs or changes files.')
    parser.add_argument('--tests',action='store_true',help='Run allowlisted local Node.js tests.')
    parser.add_argument('--check-ollama',action='store_true',help='Opt-in query to 127.0.0.1:11434 only.')
    parser.add_argument('--check-port',action='store_true',help='Check whether local preview port 8772 is in use.')
    parser.add_argument('--json',action='store_true',help='Print JSON status instead of readable text.')
    args=parser.parse_args(argv)
    model=os.environ.get('SIGNAL_MODEL','llama3.2:3b')
    outcome=audit(tests=args.tests,ollama=args.check_ollama,port=args.check_port,model=model)
    if args.json:print(json.dumps(outcome,indent=2,ensure_ascii=False))
    else:
        print('SIGNAL v33 LOCAL READINESS REPORT (no changes or purchases)')
        for row in outcome['results']:print('%-5s %-29s %s'%(row['status'],row['check'],row['detail']))
        print('TOTALS: '+', '.join('%s=%s'%(k,v) for k,v in outcome['totals'].items()))
        print('PREVIEW LAUNCH READY:', 'YES' if outcome['launch_ready'] else 'NO (inspect failed required files or tests)')
        print(outcome['note'])
    return 1 if outcome['totals']['FAIL'] else 0


if __name__=='__main__':sys.exit(main())
