'use strict';
// Pure, offline validator for a future Ollama /api/chat response. No network calls.
const MAX_REPLY = 4000;
const LABEL = 'LOCAL AI RESPONSE — UNVERIFIED. Not a measurement or equipment status. ';
function validateLocalChatResponse(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return {accepted:false,reason:'invalid-response'};
  if (payload.error !== undefined || payload.done !== true) return {accepted:false,reason:'incomplete-or-error'};
  const msg = payload.message;
  if (!msg || typeof msg !== 'object' || Array.isArray(msg) || msg.role !== 'assistant') return {accepted:false,reason:'invalid-message'};
  if (Object.prototype.hasOwnProperty.call(msg,'tool_calls') || Object.prototype.hasOwnProperty.call(payload,'tool_calls')) return {accepted:false,reason:'tool-calls-not-supported'};
  if (typeof msg.content !== 'string' || !msg.content.trim() || msg.content.length > MAX_REPLY || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(msg.content)) return {accepted:false,reason:'invalid-content'};
  return {accepted:true,reason:'unverified-local-chat',text:LABEL + msg.content.trim()};
}
if (typeof module !== 'undefined' && module.exports) module.exports = {validateLocalChatResponse};
if (typeof globalThis !== 'undefined') globalThis.SignalBridgeResponse = Object.freeze({validateLocalChatResponse});
