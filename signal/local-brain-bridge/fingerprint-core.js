/* SIGNAL Evidence Fingerprint v0.1 — read one user-selected local file, hash in RAM.
 * No network, file upload, disk writes, OCR, AI interpretation or authenticity claims.
 */
(function(root){
'use strict';
const MAX_FILE_SIZE=25*1024*1024,HEX64=/^[0-9a-fA-F]{64}$/;
function fail(s){throw Error(s)}
function reference(value){if(typeof value!=='string')fail('Expected reference digest text');const s=value.trim();if(!HEX64.test(s))fail('Reference SHA-256 must be 64 hexadecimal characters');return s.toLowerCase()}
function subtle(){const s=root.crypto?.subtle;if(!s||typeof s.digest!=='function')fail('Secure local SHA-256 is unavailable in this browser; run on localhost.');return s}
async function bytes(buffer){if(!(buffer instanceof ArrayBuffer))fail('SHA-256 requires ArrayBuffer');if(buffer.byteLength>MAX_FILE_SIZE)fail('File exceeds 25 MiB safe preview limit');const digest=await subtle().digest('SHA-256',buffer);return Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('')}
function compare(digest,expected){return reference(digest)===reference(expected)}
function shortName(s){if(typeof s!=='string'||!s||s.length>255||/[\u0000-\u001f\u007f]/.test(s))fail('Invalid file name');return s.slice(0,120)}
async function fingerprint(file){
 if(!file||typeof file.arrayBuffer!=='function'||typeof file.size!=='number'||!Number.isSafeInteger(file.size)||file.size<0)fail('Select one local file');
 if(file.size>MAX_FILE_SIZE)fail('Preview limit: file is larger than 25 MiB. The file was not read.');
 const name=shortName(file.name);
 const raw=await file.arrayBuffer();if(raw.byteLength!==file.size)fail('File size changed during read; retry.');
 const hash=await bytes(raw);
 return {fileName:name,sizeBytes:file.size,sha256:hash};
}
function note(rec){if(!rec||!HEX64.test(rec.sha256)||!Number.isSafeInteger(rec.sizeBytes)||rec.sizeBytes<0||rec.sizeBytes>MAX_FILE_SIZE)fail('Invalid fingerprint record');
 const name=shortName(rec.fileName);return `Local file selection: ${name}; size: ${rec.sizeBytes} bytes; SHA-256: ${rec.sha256.toLowerCase()}. Hash describes only selected bytes, not origin or authenticity.`;
}
const api=Object.freeze({fingerprint,bytes,compare,reference,note,MAX_FILE_SIZE});
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALFingerprint=api;
})(typeof window!=='undefined'?window:globalThis);
