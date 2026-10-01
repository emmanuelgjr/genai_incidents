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
let id=0; const pend={}; ws.onmessage = e => { const m=JSON.parse(e.data); if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; } };
const send = (method, params={}) => new Promise(r => { const i=++id; pend[i]=r; ws.send(JSON.stringify({id:i,method,params})); });
await send('Emulation.setDeviceMetricsOverride',{width:+w,height:+h,deviceScaleFactor:1.5,mobile:false});
await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:theme}]});
await send('Page.enable'); await send('Runtime.enable');
await send("Page.navigate",{url}); await sleep(9000); if (process.env.CLICK) { await send("Runtime.evaluate",{expression:`document.querySelector(${JSON.stringify(process.env.CLICK)}).click()`}); await sleep(3500); }
const r = await send('Runtime.evaluate',{returnByValue:true, expression:`(()=>{const el=document.querySelector(${JSON.stringify(selector)}); el.scrollIntoView(); const b=el.getBoundingClientRect(); return {x:b.x+scrollX,y:b.y+scrollY,w:b.width,h:b.height};})()`});
const b = r.result.result.value; const p=+pad; const H = +maxh ? Math.min(b.h, +maxh) : b.h;
await sleep(800);
const s = await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:b.x-p,y:b.y+(+yoff),width:b.w+2*p,height:H+p,scale:1}});
writeFileSync(out, Buffer.from(s.result.data,'base64')); console.log('saved', out, b);
ws.close(); chrome.kill();
