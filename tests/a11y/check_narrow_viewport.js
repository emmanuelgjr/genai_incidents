#!/usr/bin/env node
'use strict';
/*
 * WS6-T5 -- 380px layout gate.
 *
 * The plan's acceptance criterion is "table usable on a 380px viewport".
 * This check loads the page at exactly 380px wide and asserts:
 *   1. The document never becomes wider than the viewport (no page-level
 *      horizontal overflow -- the classic mobile-layout regression, where
 *      one element wider than 380px forces the whole page to scroll
 *      sideways and everything else reflows around it).
 *   2. The incidents table is present and has visible data rows.
 *   3. Every element with an interactive role (button, link, input, select)
 *      inside the filter bar is at least 24px tall (WCAG 2.5.8 AA target
 *      size), since that's the concrete way a 380px layout stops being
 *      "usable" on a touch device even when it doesn't overflow.
 *
 * Usage: node check_narrow_viewport.js <url>
 */
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

const URL_TO_TEST = process.argv[2] || 'http://127.0.0.1:8000/';
const WIDTH = 380;

async function main() {
  const browser = await puppeteer.launch({
    executablePath: findChrome(),
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: 800 });
    await page.goto(URL_TO_TEST, { waitUntil: 'networkidle0', timeout: 120000 });
    await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });

    const report = await page.evaluate((width) => {
      const scrollW = document.documentElement.scrollWidth;
      const rows = document.querySelectorAll('#incidents tbody tr[data-row]').length;
      const smallTargets = [];
      document.querySelectorAll('.filters button, .filters input, .filters select, .cta, .theme-toggle')
        .forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && r.height > 0 && r.height < 24) {
            smallTargets.push({ tag: el.tagName, id: el.id || null, height: Math.round(r.height) });
          }
        });
      return { scrollW, rows, smallTargets };
    }, WIDTH);

    console.log(`[380px] document.scrollWidth = ${report.scrollW} (viewport ${WIDTH})`);
    console.log(`[380px] visible table rows = ${report.rows}`);
    console.log(`[380px] undersized touch targets = ${report.smallTargets.length}`);
    for (const t of report.smallTargets) console.log(`  - ${t.tag}${t.id ? '#' + t.id : ''}: ${t.height}px`);

    let failed = false;
    if (report.scrollW > WIDTH) {
      console.error(`::error::page overflows its 380px viewport (scrollWidth=${report.scrollW})`);
      failed = true;
    }
    if (report.rows === 0) {
      console.error('::error::no incident rows rendered at 380px');
      failed = true;
    }
    if (report.smallTargets.length > 0) {
      console.error('::error::interactive controls under the 24px WCAG 2.5.8 target size at 380px');
      failed = true;
    }

    process.exitCode = failed ? 1 : 0;
    if (!failed) console.log('\n[380px] PASS');
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
