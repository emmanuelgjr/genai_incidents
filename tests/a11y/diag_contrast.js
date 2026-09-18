'use strict';
// Ad-hoc diagnostic (not a CI gate): prints the specific node targets and
// axe-core failure summaries for color-contrast + region violations, so a
// "N violations" summary from check_axe.js can be traced to the actual CSS
// rule/selector at fault. Usage: node diag_contrast.js <url>
const fs = require('fs');
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');
const AXE_SRC = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

async function main() {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(process.argv[2] || 'http://127.0.0.1:8123/', { waitUntil: 'networkidle0', timeout: 120000 });
  await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
  await page.evaluate(AXE_SRC);
  const results = await page.evaluate(async () => await window.axe.run(document, { runOnly: ['color-contrast', 'region'] }));
  for (const v of results.violations) {
    console.log('RULE', v.id, v.impact);
    for (const n of v.nodes.slice(0, 15)) {
      console.log('  target:', JSON.stringify(n.target));
      console.log('  summary:', n.failureSummary.replace(/\n/g, ' | '));
    }
    if (v.nodes.length > 15) console.log(`  ... and ${v.nodes.length - 15} more`);
  }
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });
