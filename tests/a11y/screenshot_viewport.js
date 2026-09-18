'use strict';
// Ad-hoc visual check (not a CI gate): screenshots exactly the visible
// viewport (no fullPage scroll) at a given width/height/scrollY, for
// eyeballing a specific section of a narrow layout.
// Usage: node screenshot_viewport.js <url> <width> <height> <scrollY> <out.png>
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

async function main() {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const url = process.argv[2] || 'http://127.0.0.1:8123/';
  const width = parseInt(process.argv[3] || '380', 10);
  const height = parseInt(process.argv[4] || '800', 10);
  const scrollY = parseInt(process.argv[5] || '0', 10);
  const out = process.argv[6] || 'shot.png';
  await page.setViewport({ width, height });
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });
  await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
  if (scrollY) await page.evaluate(y => window.scrollTo(0, y), scrollY);
  await new Promise(r => setTimeout(r, 200));
  await page.screenshot({ path: out });
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });
