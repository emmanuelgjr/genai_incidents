#!/usr/bin/env node
'use strict';
/*
 * WS6-T5 -- Lighthouse accessibility gate for docs/index.html.
 *
 * Launches Chromium via puppeteer's bundled binary (so this doesn't depend
 * on whatever browser happens to be preinstalled on a given CI runner),
 * hands its debugging port to Lighthouse, and asserts the accessibility
 * category score is >= 0.90 -- the plan's acceptance criterion
 * ("Lighthouse accessibility >= 90").
 *
 * Usage: node check_lighthouse.js <url>   (defaults to http://127.0.0.1:8000/)
 */
const fs = require('fs');
const path = require('path');
const chromeLauncher = require('chrome-launcher');
const { findChrome } = require('./find_chrome');

const URL_TO_TEST = process.argv[2] || 'http://127.0.0.1:8000/';
const MIN_SCORE = 0.90;

async function main() {
  // lighthouse ships as an ESM module in v12; import() works from CJS.
  const { default: lighthouse } = await import('lighthouse');

  const chrome = await chromeLauncher.launch({
    chromePath: findChrome(),
    chromeFlags: ['--headless=new', '--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const options = {
      logLevel: 'error',
      output: 'json',
      onlyCategories: ['accessibility'],
      port: chrome.port,
      // The default 45s Lighthouse timeout can be tight while a 15MB
      // dataset fetch + 13k-row filter/sort settle before FCP/interactive.
      maxWaitForLoad: 90000,
    };
    const runnerResult = await lighthouse(URL_TO_TEST, options);
    const score = runnerResult.lhr.categories.accessibility.score;
    const pct = (score * 100).toFixed(1);

    console.log(`[lighthouse] accessibility score: ${pct} (threshold ${MIN_SCORE * 100})`);
    const failing = Object.values(runnerResult.lhr.audits)
      .filter(a => runnerResult.lhr.categories.accessibility.auditRefs.some(r => r.id === a.id) && a.score !== null && a.score < 1);
    for (const a of failing) {
      console.log(`  - ${a.id}: ${a.title} (score ${a.score})`);
    }

    fs.writeFileSync(path.join(__dirname, 'lighthouse-a11y-report.json'), JSON.stringify(runnerResult.lhr, null, 2));

    if (score < MIN_SCORE) {
      console.error(`\n::error::Lighthouse accessibility score ${pct} is below the required ${MIN_SCORE * 100}`);
      process.exitCode = 1;
    } else {
      console.log('\n[lighthouse] PASS');
    }
  } finally {
    try {
      await chrome.kill();
    } catch (killErr) {
      // Best-effort cleanup only. On Windows, deleting Chrome's temp
      // profile dir can race an antivirus scan / file lock (EPERM) after
      // the process itself is already dead; that's a host quirk, not a
      // failure of the check above, so don't let it override
      // process.exitCode set by the actual score assertion.
      console.warn('chrome.kill() cleanup warning (non-fatal):', killErr.message);
    }
  }
}

main().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
