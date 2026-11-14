'use strict';

const { createInterface } = require('node:readline/promises');
const { evaluateBridgeRequest } = require('./local-bridge-policy');
const { validateLocalChatResponse } = require('./local-bridge-response');

const OLLAMA_URL = 'http://127.0.0.1:11434/api/chat';
const MAX_RESPONSE_BYTES = 32 * 1024;

async function askLocalSignal(text, consent, fetchResponse = fetch) {
  // This command runs in the current user's terminal and exposes no server.
  const request = evaluateBridgeRequest({ action: 'chat', text }, {
    enabled: true,
    userConsented: consent,
    authenticated: true,
  });
  if (!request.allowed) return { accepted: false, reason: request.reason };

  try {
    const response = await fetchResponse(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      redirect: 'error',
      signal: AbortSignal.timeout(60_000),
      body: JSON.stringify({
        model: 'llama3.2:3b',
        stream: false,
        options: { num_predict: 256 },
        messages: [
          { role: 'system', content: 'You are SIGNAL, the VEIL Research Project assistant. Answer concisely. You cannot observe equipment, verify measurements, or control devices.' },
          { role: 'user', content: request.text },
        ],
      }),
    });

    if (!response.ok || !response.body) {
      await response.body?.cancel();
      return { accepted: false, reason: 'ollama-http-error' };
    }

    const chunks = [];
    let bytes = 0;
    for await (const chunk of response.body) {
      bytes += chunk.byteLength;
      if (bytes > MAX_RESPONSE_BYTES) return { accepted: false, reason: 'response-too-large' };
      chunks.push(chunk);
    }

    let payload;
    try {
      payload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    } catch {
      return { accepted: false, reason: 'invalid-json' };
    }
    const reply = validateLocalChatResponse(payload);
    if (reply.accepted && /[\x1b\x7f-\x9f]/.test(reply.text)) {
      return { accepted: false, reason: 'invalid-content' };
    }
    return reply;
  } catch {
    return { accepted: false, reason: 'ollama-unreachable-or-timeout' };
  }
}

async function main() {
  const terminal = createInterface({ input: process.stdin, output: process.stdout });
  let question;
  try {
    const consent = await terminal.question('Send one question to Ollama on this computer? [y/N] ');
    if (consent.trim().toLowerCase() !== 'y') return;
    question = await terminal.question('Ask SIGNAL: ');
  } finally {
    terminal.close();
  }

  const reply = await askLocalSignal(question, true);
  if (reply.accepted) {
    console.log(reply.text);
    return;
  }
  console.error('SIGNAL could not return a reply (' + reply.reason + ').');
  process.exitCode = 1;
}

if (require.main === module) {
  main().catch(() => {
    console.error('SIGNAL could not read the terminal input.');
    process.exitCode = 1;
  });
}

module.exports = { askLocalSignal };
