'use strict';
// Ad-hoc diagnostic (not a CI gate): prints each incidents-table column's
// rendered width plus the first severity badge's box/style, at 380px. Used
// while tuning the WS6-T5 narrow-table CSS (table-layout: fixed + explicit
// column percentages) to see column widths sum against the viewport instead
// of guessing from a screenshot. Usage: node diag_severity_col.js <url>
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

async function main() {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 380, height: 800 });
  await page.goto(process.argv[2] || 'http://127.0.0.1:8123/', { waitUntil: 'networkidle0', timeout: 120000 });
  await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
  const info = await page.evaluate(() => {
    const th = document.querySelectorAll('#incidents thead th');
    const cols = Array.from(th).map(t => ({ text: t.textContent.trim(), width: t.getBoundingClientRect().width }));
    const badge = document.querySelector('#incidents tbody .sev-badge');
    const badgeRect = badge ? badge.getBoundingClientRect() : null;
    const badgeStyle = badge ? getComputedStyle(badge) : null;
    return {
      cols,
      badgeText: badge ? badge.textContent : null,
      badgeRect,
      badgeWhiteSpace: badgeStyle ? badgeStyle.whiteSpace : null,
      badgeFontSize: badgeStyle ? badgeStyle.fontSize : null,
    };
  });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });
