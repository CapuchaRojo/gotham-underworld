// GTG-26 real-browser synthetic-preview checks. No host or gameplay connection.
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const dist = resolve(repo, 'frontend/dist/preview');
const browser = process.env.GOON_BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
assert.ok(existsSync(browser) && existsSync(resolve(dist, 'index.html')));
const directory = resolve(repo, '.integration', `gtg26-preview-${Date.now()}`);
mkdirSync(directory, {recursive:true});
const policy = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'";
const server = createServer((req,res) => {
  try {
    if (!['GET','HEAD'].includes(req.method)) { res.writeHead(405).end(); return; }
    const name = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
    const file = resolve(dist, '.' + (name === '/' ? '/index.html' : name));
    if (!file.startsWith(dist + sep) || !existsSync(file)) { res.writeHead(404).end(); return; }
    const mime = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8'}[extname(file)];
    if (!mime) { res.writeHead(404).end(); return; }
    res.writeHead(200, {'Content-Type':mime,'Content-Security-Policy':policy,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    res.end(req.method === 'HEAD' ? undefined : readFileSync(file));
  } catch { res.writeHead(400).end(); }
});
await new Promise(done => server.listen(0,'127.0.0.1',done));
const origin = `http://127.0.0.1:${server.address().port}`;
const events=[], pending=new Map(), checks=[];let seq=0,chrome,socket;
const delay=ms=>new Promise(done=>setTimeout(done,ms));
async function until(fn,label) { for(let i=0;i<160;i++){if(await fn())return;await delay(100);}throw Error('Timeout: '+label); }
function send(method,params={}) { return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));}); }
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const body=part=>evaluate(`document.body.innerText.includes(${JSON.stringify(part)})`);
async function click(text){assert.ok(await evaluate(`(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()===${JSON.stringify(text)});if(!b)return false;b.click();return true})()`));}
async function key(key,code,windowsVirtualKeyCode){await send('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode,...(key==='Enter'?{text:'\r',unmodifiedText:'\r'}:{})});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode});}
const state=()=>evaluate('document.querySelector("section[data-state]")?.dataset.state');
try {
  const profile=resolve(directory,'chromium-profile');
  chrome=spawn(browser,['--headless=new','--no-first-run','--no-default-browser-check','--disable-background-networking','--remote-debugging-port=0','--remote-debugging-address=127.0.0.1',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
  const active=resolve(profile,'DevToolsActivePort');await until(()=>existsSync(active),'browser startup');
  const port=readFileSync(active,'utf8').split('\n')[0];
  const pages=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();socket=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
  socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}else events.push(m);};
  await new Promise(done=>socket.onopen=done);
  for(const name of ['Page','Runtime','Log','Network'])await send(name+'.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:origin+'/?engine=live'});
  await until(()=>body('Synthetic Preview'),'preview mount with malicious live query');
  assert.equal(await evaluate('document.querySelector("#pair-code")===null'),true);
  assert.equal(await state(),'choices');checks.push('engine=live query remains synthetic preview');
  assert.ok(await body('$20 guaranteed'));
  assert.ok(await body('Day 1 to before day 2'));checks.push('correct one-action opening terms and exclusive deadline');
  await evaluate(`document.querySelector('section[data-state="choices"] button').focus()`);
  await key('Enter','Enter',13);await until(async()=>await state()==='pending','keyboard option selection');
  assert.equal(await evaluate('document.activeElement.tagName'),'H3');
  assert.equal(await evaluate('[...document.querySelectorAll("button")].find(x=>x.textContent.startsWith("Confirm:")).disabled'),true);
  checks.push('native Enter selects and focuses heading; Confirm disabled');
  await key('Escape','Escape',27);await until(async()=>await state()==='choices','Escape unsent cancel');
  await key('Tab','Tab',9);assert.equal(await evaluate('document.activeElement.tagName'),'BUTTON');checks.push('Escape cancels only unsent choice and Tab continues without trap');
  for(const [label,id] of [['Undiscovered','undiscovered'],['Eligibility','eligibility'],['Choices','choices'],['Refusal','refusal'],['Pending','pending'],['Confirmed','confirmed'],['Rejected','rejected'],['Consequence','consequence']]) {
    await click(label);await until(async()=>await state()===id,label);
    assert.ok(await evaluate('document.querySelector("section[data-state]").innerText.includes("Synthetic Preview")'));
    if(id==='undiscovered')assert.equal(await evaluate('document.querySelector("section[data-state]").innerText.includes("Tess Navarro")'),false);
  }
  checks.push('all eight states render with synthetic labels and undiscovered privacy');
  await click('Pending');await click('Show uncertain transmission example');await until(()=>body('Transmitted, outcome uncertain'),'uncertain state');
  await key('Escape','Escape',27);assert.ok(await body('Transmitted, outcome uncertain'));
  assert.equal(await evaluate('[...document.querySelectorAll("section[data-state] button")].some(x=>/Cancel|Confirm|retry/i.test(x.textContent))'),false);
  checks.push('uncertain transmission has no cancel/retry and Escape cannot undo');
  await click('The Streets');await until(()=>body('places shown.'),'streets count');
  await evaluate(`(()=>{const el=document.querySelector('input[type="search"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,'zzzz-no-place');el.dispatchEvent(new Event('input',{bubbles:true}));})()`);
  await until(()=>body('No places match'),'search empty result');await click('Clear filters and show all places');
  await until(()=>evaluate('document.querySelector("input[type=search]").value === ""'),'filter reset');checks.push('street result count, empty results and filter reset');
  await click('My Life');await until(()=>body('prepaid stay separate'),'money explanation');assert.ok(await body('in 3 days'));checks.push('money separation and relative due wording');
  await click('My Story');await until(()=>body('Confidence labels do not establish source count'),'confidence wording');checks.push('confidence and source count remain distinct');
  await click('Today');await until(async()=>await state()==='choices','return to Today');
  assert.equal(await evaluate('document.querySelectorAll("[style]").length'),0);checks.push('no inline style attributes under strict CSP');
  const storage=await evaluate(`(async()=>({local:Object.keys(localStorage),session:Object.keys(sessionStorage),databases:(await indexedDB.databases()).map(x=>x.name)}))()`);
  assert.deepEqual(storage,{local:[],session:[],databases:[]});checks.push('preview leaves persistent browser storage empty');
  const requests=events.filter(e=>e.method==='Network.requestWillBeSent').map(e=>({method:e.params.request.method,url:e.params.request.url}));
  assert.ok(requests.every(r=>r.url.startsWith(origin+'/')||r.url.startsWith('data:')));
  assert.ok(requests.every(r=>r.method==='GET'&&!/\/(api|host)\//.test(r.url)));
  checks.push('no host/API submissions or external page requests');
  const errors=events.filter(e=>e.method==='Runtime.exceptionThrown'||(e.method==='Log.entryAdded'&&e.params.entry.source==='security'));
  assert.deepEqual(errors,[]);checks.push('no runtime or CSP errors');
  const screenshot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});writeFileSync(resolve(directory,'preview.png'),Buffer.from(screenshot.data,'base64'));
  writeFileSync(resolve(directory,'evidence.json'),JSON.stringify({browser,origin,passed:checks,requests,storage,errors},null,2));
  console.log(JSON.stringify({evidence:resolve(directory,'evidence.json'),screenshot:resolve(directory,'preview.png'),passed:checks},null,2));
} catch(error) {
  if(socket?.readyState===WebSocket.OPEN) {
    const snapshot=await evaluate('({text:document.body.innerText,active:document.activeElement?.outerHTML})');
    writeFileSync(resolve(directory,'failure.json'),JSON.stringify({error:String(error),checks,snapshot,events:events.filter(e=>e.method==="Runtime.exceptionThrown"||e.method==="Log.entryAdded")},null,2));
    console.error('Preview failure evidence:',resolve(directory,'failure.json'));
  }
  throw error;
} finally { if(socket)socket.close();if(chrome)chrome.kill();await new Promise(done=>server.close(done)); }
