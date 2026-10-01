import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os'; import { join } from 'node:path';
const [,, url, out, selector, w='1440', h='1000', theme='light', pad='0', maxh='0', yoff='0'] = process.argv;
const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',
  ['--headless=new','--disable-gpu','--hide-scrollbars','--remote-debugging-port=9333',`--user-data-dir=${mkdtempSync(join(tmpdir(),'cdp'))}`,`--window-size=${w},${h}`,'about:blank']);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tabs; for (let i=0;i<50;i++){ try{ tabs = await (await fetch('http://127.0.0.1:9333/json')).json(); if(tabs.length) break;}catch{} await sleep(200); }
const ws = new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
// Pending CDP replies, keyed by our own numeric request id. A Map plus a
// type check means a reply id from the socket can only ever select a
// resolver we registered ourselves.
let id = 0; const pend = new Map();
ws.onmessage = e => {
  const m = JSON.parse(e.data);
  if (!Number.isInteger(m.id)) return;
  const resolve = pend.get(m.id);
  if (typeof resolve !== 'function') return;
  pend.delete(m.id); resolve(m);
};
const send = (method, params={}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({id:i,method,params})); });
// Run a fixed function in the page with the CSS selector passed as a CDP
// call argument, never spliced into source text.
const callOnDocument = async (fn, arg) => {
  const doc = await send('Runtime.evaluate', {expression: 'document'});
  return send('Runtime.callFunctionOn', {objectId: doc.result.result.objectId, functionDeclaration: fn, arguments: [{value: arg}], returnByValue: true});
};
await send('Emulation.setDeviceMetricsOverride',{width:+w,height:+h,deviceScaleFactor:1.5,mobile:false});
await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:theme}]});
await send('Page.enable'); await send('Runtime.enable');
await send("Page.navigate",{url}); await sleep(9000); if (process.env.CLICK) { await callOnDocument('function (sel) { this.querySelector(sel).click(); }', process.env.CLICK); await sleep(3500); }
const r = await callOnDocument('function (sel) { const el = this.querySelector(sel); el.scrollIntoView(); const b = el.getBoundingClientRect(); return {x: b.x + scrollX, y: b.y + scrollY, w: b.width, h: b.height}; }', selector);
const b = r.result.result.value; const p=+pad; const H = +maxh ? Math.min(b.h, +maxh) : b.h;
await sleep(800);
const s = await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:b.x-p,y:b.y+(+yoff),width:b.w+2*p,height:H+p,scale:1}});
writeFileSync(out, Buffer.from(s.result.data,'base64')); console.log('saved', out, b);
ws.close(); chrome.kill();
