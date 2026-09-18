'use strict';
// Ad-hoc visual check (not a CI gate): screenshots a page at a given
// viewport width with one row pre-expanded, for eyeballing layout changes.
// Usage: node screenshot.js <url> <width> <out.png>
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

async function main() {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const url = process.argv[2] || 'http://127.0.0.1:8123/';
  const width = parseInt(process.argv[3] || '380', 10);
  const out = process.argv[4] || 'shot.png';
  await page.setViewport({ width, height: 900 });
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });
  await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
  // expand a row and scroll to the table so the screenshot captures the
  // interesting part of a narrow layout, not just the hero.
  await page.click('#incidents tbody tr[data-row]');
  await new Promise(r => setTimeout(r, 300));
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });
