'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { askLocalSignal } = require('./local-chat.cjs');

const reply = content => ({ done: true, message: { role: 'assistant', content } });

test('consent and request policy run before any local request', async () => {
  let calls = 0;
  const send = async () => { calls++; };
  assert.equal((await askLocalSignal('Hello', false, send)).reason, 'consent-required');
  assert.equal((await askLocalSignal('Start the MTC', true, send)).reason, 'possible-instrument-command');
  assert.equal(calls, 0);
});

test('sends a single chat to loopback and labels the validated reply', async () => {
  const result = await askLocalSignal('  Hello  ', true, async (url, options) => {
    assert.equal(url, 'http://127.0.0.1:11434/api/chat');
    assert.equal(options.redirect, 'error');
    const body = JSON.parse(options.body);
    assert.equal(body.model, 'llama3.2:3b');
    assert.equal(body.stream, false);
    assert.equal(body.tools, undefined);
    assert.deepEqual(body.messages.at(-1), { role: 'user', content: 'Hello' });
    return Response.json(reply('Hello, Andy.'));
  });
  assert.match(result.text, /UNVERIFIED.*Hello, Andy\./);
});

test('rejects model tool calls and malformed responses', async () => {
  const toolReply = reply('Hello');
  toolReply.message.tool_calls = [];
  const result = await askLocalSignal('Hello', true, async () => Response.json(toolReply));
  assert.equal(result.reason, 'tool-calls-not-supported');
  assert.equal((await askLocalSignal('Hello', true, async () => new Response('{'))).reason, 'invalid-json');
});

test('rejects oversized responses and cancels the body stream', async () => {
  let cancelled = false;
  const body = new ReadableStream({
    start(controller) { controller.enqueue(new Uint8Array(33 * 1024)); },
    cancel() { cancelled = true; },
  });
  const result = await askLocalSignal('Hello', true, async () => new Response(body));
  assert.equal(result.reason, 'response-too-large');
  assert.equal(cancelled, true);
});

test('reports unavailable Ollama and HTTP errors without echoing server text', async () => {
  const unreachable = await askLocalSignal('Hello', true, async () => { throw new Error('details'); });
  const missing = await askLocalSignal('Hello', true, async () => new Response('details', { status: 404 }));
  assert.deepEqual(unreachable, { accepted: false, reason: 'ollama-unreachable-or-timeout' });
  assert.deepEqual(missing, { accepted: false, reason: 'ollama-http-error' });
});

test('filters terminal control characters from otherwise valid responses', async () => {
  const result = await askLocalSignal('Hello', true, async () => Response.json(reply('hello\u009b31m')));
  assert.equal(result.reason, 'invalid-content');
});
