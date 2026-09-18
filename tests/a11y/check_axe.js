#!/usr/bin/env node
'use strict';
/*
 * WS6-T5 -- axe-core accessibility gate for docs/index.html.
 *
 * Runs axe-core (via a self-contained puppeteer/Chromium, no reliance on a
 * system browser) against a live copy of the page at two viewport widths
 * (a desktop width and the plan's 380px mobile floor) AND both themes
 * (dark and light). Prints every violation found at any impact level.
 *
 * BOUNCE #2 advisories (b) and (e), both acted on:
 *   (b) This never forced a theme, so it only ever audited whichever theme
 *       the runner's Chromium resolves prefers-color-scheme to by default
 *       (this environment happens to default to light) -- "both themes
 *       clean" was a manual claim this gate did not actually hold. Now
 *       explicitly emulates prefers-color-scheme for each theme before
 *       load, so both are always covered regardless of the runner's
 *       default, in CI as well as locally.
 *   (e) Gated on "critical" impact only, matching the plan's acceptance
 *       criterion verbatim -- but the one real regression this design pass
 *       hit (BOUNCE #2 report, active-sort-column text colour dropping to
 *       4.27:1 against light-theme --panel-2) was axe-core impact
 *       "serious", not "critical", and would have shipped clean under the
 *       old gate. Now fails on "serious" too. This is stricter than the
 *       plan's literal text; recorded here so the gap between "matches the
 *       acceptance criterion" and "would have caught the regression this
 *       task actually produced" isn't silently reopened by a future edit
 *       that relaxes it back to critical-only.
 *
 * Usage: node check_axe.js <url>   (defaults to http://127.0.0.1:8000/)
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

const URL_TO_TEST = process.argv[2] || 'http://127.0.0.1:8000/';
const AXE_SRC = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const VIEWPORTS = [
  { name: 'desktop-1280', width: 1280, height: 900 },
  { name: 'mobile-380', width: 380, height: 800 },
];
const THEMES = ['dark', 'light'];
const GATING_IMPACTS = new Set(['critical', 'serious']);

async function runAt(browser, viewport, theme) {
  const page = await browser.newPage();
  // Forces the pre-paint <head> script's `matchMedia('(prefers-color-scheme:
  // light)')` check to resolve deterministically, independent of whatever
  // the runner's default happens to be (see the file header).
  await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: theme }]);
  await page.setViewport({ width: viewport.width, height: viewport.height });
  await page.goto(URL_TO_TEST, { waitUntil: 'networkidle0', timeout: 120000 });
  // The dataset is a multi-MB fetch; wait for the table to actually paint
  // rows before running axe, or we'd only ever be auditing the loading
  // skeleton.
  await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
  const actualTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await page.evaluate(AXE_SRC);
  const results = await page.evaluate(() => window.axe.run(document, {
    resultTypes: ['violations'],
  }));
  await page.close();
  return { results, actualTheme };
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: findChrome(),
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  let anyGating = false;
  const summary = [];
  try {
    for (const theme of THEMES) {
      for (const vp of VIEWPORTS) {
        const { results, actualTheme } = await runAt(browser, vp, theme);
        if (actualTheme !== theme) {
          console.error(`::error::requested prefers-color-scheme=${theme} but the page resolved data-theme=${actualTheme} -- emulation did not take effect`);
          anyGating = true;
        }
        const gating = results.violations.filter(v => GATING_IMPACTS.has(v.impact));
        if (gating.length) anyGating = true;
        console.log(`\n[axe] theme=${actualTheme} viewport ${vp.name} (${vp.width}x${vp.height}): ` +
          `${results.violations.length} violation rule(s), ${gating.length} critical/serious`);
        for (const v of results.violations) {
          console.log(`  - [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} node(s)) -- ${v.helpUrl}`);
        }
        summary.push({
          theme: actualTheme,
          viewport: vp.name,
          violationRules: results.violations.length,
          gating: gating.length,
          violations: results.violations.map(v => ({
            id: v.id, impact: v.impact, help: v.help, nodeCount: v.nodes.length,
          })),
        });
      }
    }
  } finally {
    await browser.close();
  }

  fs.writeFileSync(
    path.join(__dirname, 'axe-report.json'),
    JSON.stringify({ url: URL_TO_TEST, generated: new Date().toISOString(), results: summary }, null, 2),
  );

  if (anyGating) {
    console.error('\n::error::axe-core found CRITICAL or SERIOUS accessibility violation(s) -- see report above / axe-report.json');
    process.exitCode = 1;
  } else {
    console.log('\n[axe] PASS -- no critical or serious violations at any tested viewport/theme combination');
  }
}

main().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
