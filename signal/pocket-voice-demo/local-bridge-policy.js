'use strict';
// Pure policy boundary: does not open sockets or send requests.
const MAX_TEXT = 500;
function evaluateBridgeRequest(request, settings) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) return {allowed:false, reason:'invalid-request'};
  if (!settings || settings.enabled !== true || settings.userConsented !== true) return {allowed:false, reason:'consent-required'};
  if (settings.authenticated !== true) return {allowed:false, reason:'authentication-required'};
  if (request.action !== 'chat') return {allowed:false, reason:'read-only-chat-only'};
  if (typeof request.text !== 'string' || !request.text.trim() || request.text.length > MAX_TEXT) return {allowed:false, reason:'invalid-text'};
  if (/\b(start|stop|reset|arm|disarm|activate|deactivate|delete|erase|unlock|trigger|override|disable|enable|reboot|shutdown)\b/i.test(request.text)) return {allowed:false, reason:'possible-instrument-command'};
  if (request.instrument || request.device || request.url || request.endpoint || request.token) return {allowed:false, reason:'unexpected-fields'};
  if (Object.keys(request).some(k=>!['action','text'].includes(k))) return {allowed:false,reason:'unexpected-fields'};
  return {allowed:true, reason:'eligible-for-local-chat', text:request.text.trim()};
}
if(typeof module!=='undefined'&&module.exports)module.exports={evaluateBridgeRequest};
if(typeof globalThis!=='undefined')globalThis.SignalBridgePolicy=Object.freeze({evaluateBridgeRequest});
