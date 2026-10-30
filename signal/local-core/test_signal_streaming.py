"""SIGNAL v0.11: bounded local Ollama streaming and no partial evidence conversation turns."""
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import request, error

import signal_core as core
import signal_desktop as desktop


class FakeResponse:
    def __init__(self, frames):
        self.rows = iter(frames)
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def readline(self, limit):
        try: return next(self.rows)
        except StopIteration: return b''


def ollama_frame(text='', done=False):
    return json.dumps({'message': {'content': text}, 'done': done}).encode() + b'\n'


class OllamaStreamingTests(unittest.TestCase):
    def call(self, frames):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse(frames)) as mocked:
            response=list(core.LocalModel().stream_answer([{'role':'user','content':'Hello'}]))
        payload=json.loads(mocked.call_args.args[0].data)
        self.assertEqual(mocked.call_args.args[0].full_url, 'http://127.0.0.1:11434/api/chat')
        self.assertTrue(payload['stream'])
        self.assertLessEqual(payload['options']['num_predict'], 650)
        return response

    def test_chunks_and_terminal_event(self):
        self.assertEqual(self.call([ollama_frame('Evidence '), ollama_frame('first.', True)]),
                         ['Evidence ', 'first.'])

    def test_completion_without_content_rejected(self):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([ollama_frame('', True)])):
            with self.assertRaisesRegex(RuntimeError, 'incomplete'):
                list(core.LocalModel().stream_answer([]))

    def test_abrupt_end_rejected(self):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([ollama_frame('Partial')])):
            with self.assertRaisesRegex(RuntimeError, 'incomplete'):
                list(core.LocalModel().stream_answer([]))

    def test_oversized_line_rejected(self):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([b'a'*65537])):
            with self.assertRaisesRegex(RuntimeError, 'too large'):
                list(core.LocalModel().stream_answer([]))

    def test_invalid_frame_rejected(self):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([b'not JSON\n'])):
            with self.assertRaisesRegex(RuntimeError, 'Invalid local'):
                list(core.LocalModel().stream_answer([]))

    def test_error_frame_is_not_injected_into_chat(self):
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([b'{"error":"untrusted"}\n'])):
            with self.assertRaisesRegex(RuntimeError, 'generation error'):
                list(core.LocalModel().stream_answer([]))

    def test_reply_size_cap(self):
        content='x'*core.MAX_STREAM_CHARS
        with patch.object(core.request, 'urlopen', return_value=FakeResponse([ollama_frame(content),ollama_frame('Y',True)])):
            with self.assertRaisesRegex(RuntimeError, 'length'):
                list(core.LocalModel().stream_answer([]))

    def test_network_error_has_no_cloud_fallback(self):
        with patch.object(core.request, 'urlopen', side_effect=error.URLError('offline')):
            with self.assertRaisesRegex(RuntimeError, 'No cloud fallback'):
                list(core.LocalModel().stream_answer([]))


class StubStream:
    model = 'simulated-local-model'
    def __init__(self, fail=False): self.fail=fail;self.calls=[]
    def answer(self, messages): raise AssertionError('Must not call nonstreaming answer')
    def stream_answer(self, messages):
        self.calls.append(messages)
        yield 'Verification '
        if self.fail: raise RuntimeError('Synthetic disconnection')
        yield 'requires audio.'


class AssistantStreamingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.model=StubStream()
        self.bot=core.Assistant(self.model,core.Memories(self.tmp.name))
    def tearDown(self): self.tmp.cleanup()

    def test_complete_saves_turn_but_does_not_activate_microphone(self):
        events=list(self.bot.stream_ask('What do the event logs prove?'))
        self.assertEqual([e['event'] for e in events], ['delta','delta','complete'])
        self.assertEqual(events[-1]['reply_length'],len('Verification requires audio.'))
        self.assertEqual(self.bot.history[-1]['content'],'Verification requires audio.')
        self.assertFalse(self.bot.voice.enabled)

    def test_partial_network_failure_never_commits_chat(self):
        self.model.fail=True
        gen=self.bot.stream_ask('What happened?')
        self.assertEqual(next(gen)['text'],'Verification ')
        with self.assertRaisesRegex(RuntimeError, 'disconnection'):
            list(gen)
        self.assertEqual(self.bot.history, [])

    def test_operator_cancel_does_not_commit_chat(self):
        gen=self.bot.stream_ask('Can I stop this?')
        self.assertEqual(next(gen)['event'],'delta')
        gen.close()
        self.assertEqual(self.bot.history,[])

    def test_cancel_event_prevents_partial_commit_and_voice(self):
        stop=threading.Event()
        gen=self.bot.stream_ask('Give a briefing', stop)
        self.assertEqual(next(gen)['event'], 'delta')
        stop.set()
        with self.assertRaisesRegex(RuntimeError,'stopped by operator'):
            list(gen)
        self.assertEqual(self.bot.history, [])
        self.assertFalse(self.bot.voice.enabled)

    def test_prompt_bounds_and_unsupported_models(self):
        with self.assertRaisesRegex(ValueError, '4000'):
            list(self.bot.stream_ask('x'*4001))
        self.bot.model=desktop.DemoModel()
        with self.assertRaisesRegex(RuntimeError, 'does not support'):
            list(self.bot.stream_ask('Hello'))


class EndpointStreamingTests(unittest.TestCase):
    def setUp(self):
        self.model=StubStream()
        self.server,self.state=desktop.make_server(self.model)
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.worker.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
        self.tmp=tempfile.TemporaryDirectory()
        self.state.bot.memories=core.Memories(self.tmp.name)

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.worker.join(2)
        self.tmp.cleanup()

    def call(self, text='What are the evidence limits?', token=True, path='/api/chat/stream'):
        headers={'Content-Type':'application/json'}
        if token: headers['X-SIGNAL-Token']=self.state.token
        req=request.Request(self.base+path,headers=headers,
                            data=json.dumps({'message':text}).encode())
        try:
            with request.urlopen(req,timeout=4) as result:
                return result.status, result.headers.get('Content-Type'), result.read().decode('utf-8')
        except error.HTTPError as exc:
            return exc.code, exc.headers.get('Content-Type'), exc.read().decode('utf-8')

    def test_authorized_stream_and_completion(self):
        code,mime,body=self.call()
        self.assertEqual(code,200)
        self.assertIn('x-ndjson',mime)
        frames=[json.loads(line) for line in body.strip().split('\n')]
        self.assertEqual([x['event'] for x in frames],['delta','delta','complete'])
        self.assertEqual(frames[-1]['status']['stream_supported'],True)
        self.assertEqual(len(self.state.bot.history),2)
        self.assertEqual(self.model.calls[-1][-1]['content'],'What are the evidence limits?')

    def test_authentication_and_commands(self):
        self.assertEqual(self.call(token=False)[0],403)
        self.assertEqual(self.call(text='/clear')[0],422)
        self.assertEqual(self.state.bot.history,[])

    def test_interruption_is_exposed_and_not_saved(self):
        self.model.fail=True
        code,mime,body=self.call()
        frames=[json.loads(line) for line in body.strip().split('\n')]
        self.assertEqual(code,200)
        self.assertEqual([x['event'] for x in frames],['delta','error'])
        self.assertEqual(self.state.bot.history,[])

    def test_stop_endpoint_without_active_stream_is_noop(self):
        code,mime,body=self.call(text='ignored',path='/api/chat/stop')
        self.assertEqual(code,200)
        self.assertFalse(json.loads(body)['stop_requested'])
        self.assertEqual(self.state.bot.history,[])

    def test_stop_endpoint_interrupts_active_stream_without_saving(self):
        entered=threading.Event(); release=threading.Event()
        model=self.model
        def paused(_messages):
            yield 'Starting'
            entered.set()
            if not release.wait(3): raise RuntimeError('Timed out in mock')
            yield 'Ignored after stop'
        model.stream_answer=paused
        result={}
        def worker():
            result['reply']=self.call()
        t=threading.Thread(target=worker)
        t.start()
        self.assertTrue(entered.wait(3))
        self.assertTrue(self.state.streaming_active)
        code,_,body=self.call(path='/api/chat/stop')
        self.assertEqual(code,200)
        self.assertTrue(json.loads(body)['stop_requested'])
        release.set()
        t.join(3)
        self.assertFalse(t.is_alive())
        frames=[json.loads(line) for line in result['reply'][2].strip().split('\n')]
        self.assertEqual([x['event'] for x in frames],['delta','error'])
        self.assertIn('stopped by operator',frames[-1]['error'])
        self.assertEqual(self.state.bot.history,[])
        self.assertFalse(self.state.streaming_active)

    def test_status_and_demo_safety(self):
        self.assertTrue(self.state.status()['stream_supported'])
        self.state.mode='demo'
        self.assertFalse(self.state.status()['stream_supported'])
        self.assertEqual(self.call()[0],422)


if __name__=='__main__': unittest.main()
