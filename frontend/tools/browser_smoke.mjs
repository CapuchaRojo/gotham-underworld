// Actual installed Chromium via CDP. No jsdom, browser download, or security bypass.
import { spawn, spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const browser = process.env.GOON_BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const pin = process.argv[2];
assert.match(pin ?? '', /^[0-9a-f]{64}$/);
assert.ok(existsSync(browser), 'Installed Chromium browser required');
const directory = resolve(repo, '.integration', `browser-${Date.now()}`);
mkdirSync(directory, { recursive: true });
const helper = resolve(repo, 'frontend/tools/smoke_host.py');
const prepared = spawnSync('python', ['-B', helper, 'prepare', '--directory', directory], { cwd: repo, windowsHide: true });
assert.equal(prepared.status, 0, prepared.stderr.toString());
const checkpoint = resolve(directory, 'inspection.bridge.json');
const initial = readFileSync(checkpoint);
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
let host, chrome, socket;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function until(fn, label) {
  for (let i = 0; i < 160; i++) { if (await fn()) return; await delay(100); }
  throw Error(`Timeout: ${label}`);
}
async function startHost() {
  host = spawn('python', ['-B', helper, 'serve', '--directory', directory, '--test-pin', pin], { cwd: repo, windowsHide: true });
  let text = '', errors = '';
  host.stdout.on('data', chunk => { text += chunk; });
  host.stderr.on('data', chunk => { errors += chunk; });
  await until(() => { if (host.exitCode !== null) throw Error(errors); return text.includes('\n'); }, 'host startup');
  return JSON.parse(text.split('\n')[0]); // Code stays in process memory, never evidence/logs.
}
async function stopHost() {
  host.stdin.end('\n');
  await until(() => host.exitCode !== null, 'host shutdown');
}
const pending = new Map();
let sequence = 0;
const events = [];
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const response = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (response.exceptionDetails) throw Error(response.exceptionDetails.text);
  return response.result.value;
}
async function bodyIncludes(value) { return evaluate(`document.body.innerText.includes(${JSON.stringify(value)})`); }
async function pair(code) {
  await evaluate('document.querySelector("#pair-code").focus()');
  await send('Input.insertText', { text: code });
  await evaluate('document.querySelector("button[type=submit]").click()');
  await until(() => bodyIncludes('Connected to the local engine.'), 'browser pairing');
  await until(() => evaluate('document.querySelector("[data-testid=player-cash]")?.textContent === "40"'), 'authoritative projection');
}
try {
  let ready = await startHost();
  assert.equal((await fetch(ready.origin + '/api/v1/state')).status, 401);
  assert.equal((await fetch(ready.origin + '/host/v1/bootstrap', { method: 'POST',
    headers: { 'Content-Type': 'application/json', Origin: 'http://untrusted.invalid' },
    body: JSON.stringify({ host_protocol_version: 1, bundle_id: 'goon-c2b-inspection-v1', code: ready.code }) })).status, 403);
  const profile = resolve(directory, 'chromium-profile');
  chrome = spawn(browser, ['--headless=new', '--no-first-run', '--no-default-browser-check',
    '--disable-background-networking', '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
    `--user-data-dir=${profile}`, 'about:blank'], { windowsHide: true, stdio: 'ignore' });
  const active = resolve(profile, 'DevToolsActivePort');
  await until(() => existsSync(active), 'Chromium startup');
  const port = readFileSync(active, 'utf8').split('\n')[0];
  const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(pages.find(page => page.type === 'page').webSocketDebuggerUrl);
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const promise = pending.get(message.id); pending.delete(message.id);
      if (message.error) promise.reject(Error(message.error.message)); else promise.resolve(message.result);
    } else events.push(message);
  };
  await new Promise(resolve => socket.onopen = resolve);
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable');
  await send('Page.navigate', { url: ready.origin + '/' });
  await until(() => bodyIncludes('One-time console code'), 'React mount');
  await until(() => bodyIncludes('Outbox available'), 'real IndexedDB');
  await pair(ready.code);
  assert.equal(await evaluate('document.querySelector("#pair-code").value'), '');
  const info = await evaluate(`JSON.parse(sessionStorage.getItem('goon.inspection.identity.v1'))`);
  const operation = await evaluate(`(async () => {
    const r = await fetch('/api/v1/operations/operator-fixture-0', {headers: {Authorization: 'Bearer ' + sessionStorage.getItem('goon.host.capability.v1')},cache:'no-store'});
    const b = await r.json(); return {status:r.status,operation:b.operation_status,id:b.receipt?.request_id,career:b.career_id,lineage:b.lineage_id};
  })()`);
  assert.equal(operation.operation, 'committed');
  assert.equal(operation.id, 'operator-fixture-0');
  assert.equal(operation.career, info.career_id); assert.equal(operation.lineage, info.lineage_id);
  const sessionReads = () => events.filter(e => e.method === 'Network.requestWillBeSent' &&
    e.params.request.url.endsWith('/host/v1/session')).length;
  // A durable, unsent test intent must survive inspection without replay.
  const storedIntent = {request_id:'read-only-pending-proof',scope:info.career_id+'\u0000'+info.lineage_id,
    career_id:info.career_id,lineage_id:info.lineage_id,
    envelope:{protocol_version:1,career_id:info.career_id,lineage_id:info.lineage_id,
      request_id:'read-only-pending-proof',expected_revision:info.revision,command:'wait',arguments:{}},
    status:'transmitted',receipt:null,created_at:Date.now(),updated_at:Date.now(),last_error:null};
  await evaluate(`new Promise((resolve,reject)=>{const r=indexedDB.open('goon.outbox.v1',1);r.onerror=()=>reject(Error('open'));r.onsuccess=()=>{const db=r.result;const tx=db.transaction('mutations','readwrite');tx.objectStore('mutations').add(${JSON.stringify(storedIntent)});tx.oncomplete=()=>{db.close();resolve(true)};tx.onerror=()=>reject(Error('write'))}})`);
  assert.equal((await fetch(ready.origin+'/host/v1/bootstrap',{method:'POST',headers:{'Content-Type':'application/json',Origin:ready.origin},body:JSON.stringify({host_protocol_version:1,bundle_id:'goon-c2b-inspection-v1',code:ready.code})})).status,401,'Consumed bootstrap code must be rejected');
  const readsBeforeReload = sessionReads();
  await send('Page.reload');
  await until(() => sessionReads() > readsBeforeReload, 'reload authenticated session request');
  await until(() => bodyIncludes('Connected to the local engine.'), 'reload session revalidation');
  await until(() => bodyIncludes('Outbox available (1 stored requests)'), 'pending outbox inspection');
  const screenshot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  writeFileSync(resolve(directory, 'inspection.png'), Buffer.from(screenshot.data, 'base64'));
  await stopHost();
  const previousOrigin = ready.origin;
  ready = await startHost();
  assert.equal(ready.origin, previousOrigin);
  await send('Page.reload');
  await until(() => bodyIncludes('Pairing required'), 'rotated capability rejection');
  assert.equal(await evaluate('document.querySelector("[data-testid=player-day]") === null'), true);
  await pair(ready.code);
  const preserved = await evaluate(`new Promise((resolve,reject)=>{const r=indexedDB.open('goon.outbox.v1',1);r.onsuccess=()=>{const db=r.result;const tx=db.transaction('mutations','readonly');const q=tx.objectStore('mutations').get('read-only-pending-proof');tx.oncomplete=()=>{db.close();resolve(q.result)}};r.onerror=()=>reject(Error('open'))})`);
  assert.deepEqual(preserved,storedIntent,'Reload/restart must preserve the exact pending intent');
  await evaluate(`new Promise((resolve,reject)=>{const r=indexedDB.open('goon.outbox.v1',1);r.onsuccess=()=>{const db=r.result;const tx=db.transaction('mutations','readwrite');tx.objectStore('mutations').put({request_id:'corrupt-proof',status:'transmitted'});tx.oncomplete=()=>{db.close();resolve(true)}};r.onerror=()=>reject(Error('open'))})`);
  await send('Page.reload');
  await until(()=>bodyIncludes('Outbox unavailable; gameplay remains disabled'),'corrupt outbox fails closed');
  const retained = await evaluate(`new Promise(resolve=>{const r=indexedDB.open('goon.outbox.v1',1);r.onsuccess=()=>{const db=r.result;const tx=db.transaction('mutations','readonly');const q=tx.objectStore('mutations').count();tx.oncomplete=()=>{db.close();resolve(q.result)}}})`);
  assert.equal(retained,2,'Inspection must not delete corrupt or pending records');
  assert.equal(sha(readFileSync(checkpoint)), sha(initial), 'Browser inspection changed checkpoint bytes');
  const requests = events.filter(e => e.method === 'Network.requestWillBeSent').map(e => ({ method: e.params.request.method, url: e.params.request.url }));
  assert.equal(requests.filter(r => r.url.endsWith('/api/v1/commands')).length, 0);
  // Edge's native password reveal control loads a user-agent data: SVG eye icon.
  // It is not a network request or emitted frontend asset; app CSP remains strict.
  const external = requests.filter(r => /^https?:/.test(r.url) && !r.url.startsWith(ready.origin));
  assert.equal(external.length, 0, JSON.stringify(external));
  const errors = events.filter(e => e.method === 'Runtime.exceptionThrown' ||
    (e.method === 'Log.entryAdded' && /content security|refused|unsafe-inline/i.test(e.params.entry.text)));
  assert.equal(errors.length, 0, JSON.stringify(errors));
  const report = { browser, origin: ready.origin, manifest_sha256: pin, checkpoint_sha256: sha(initial),
    career_id: info.career_id, lineage_id: info.lineage_id, original_lookup: operation,
    browser_internal_data_resources: requests.filter(r => r.url.startsWith('data:')).length,
    passed: ['actual React mount','console-code pairing','authenticated session','actual projection',
      'IndexedDB availability','pending intent survives reload and restart without replay','malformed outbox fails closed without deletion','duplicate bootstrap rejected','original-ID GET lookup','reload','stable-port restart','capability rotation',
      'reauthorization','byte-identical checkpoint','no command requests','no external page requests','no CSP errors'], requests };
  writeFileSync(resolve(directory, 'evidence.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ evidence: resolve(directory, 'evidence.json'), screenshot: resolve(directory, 'inspection.png'), passed: report.passed }, null, 2));
} finally {
  if (host && host.exitCode === null) await stopHost();
  if (socket?.readyState === WebSocket.OPEN) { try { await send('Browser.close'); } catch {} socket.close(); }
  if (chrome && chrome.exitCode === null) chrome.kill();
}
