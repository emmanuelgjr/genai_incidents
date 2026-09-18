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
 *   2. `.table-wrap` -- the table's own scroll container -- never gains an
 *      internal horizontal scrollbar either (`scrollWidth <= clientWidth`).
 *      `document.documentElement.scrollWidth` alone (the original version
 *      of this check) CANNOT catch a too-wide table: `.table-wrap` has
 *      `overflow-x: auto` (style.css), so any table overflow is absorbed by
 *      that nested scroller and the outer document never widens. Proved by
 *      forcing the table to `min-width: 1200px` in a throwaway CSS override
 *      and re-running this check unmodified: it printed `docScrollWidth 380`
 *      and exited 0 while the table plainly did not fit (see the WS6-T5
 *      design-pass report for the full before/after transcript).
 *   3. The last cell of the first visible data row (the rightmost column
 *      still shown at this width -- Severity, since .col-llm/.col-asi/
 *      .col-cves are display:none below 640px) has its right edge inside
 *      the viewport (`getBoundingClientRect().right <= innerWidth`). This
 *      is the check that actually catches "table is wider than the
 *      viewport": a table that overflows still reports scrollWidth ===
 *      clientWidth on its own wrap in some fixed-table-layout failure
 *      modes (e.g. the pre-fix CSS, where the browser's auto layout
 *      algorithm sizes Title generously and pushes Severity off-screen
 *      without necessarily creating a wrap-level horizontal scrollbar in
 *      every engine), so this is checked independently rather than
 *      inferred from (2).
 *   4. The incidents table is present and has visible data rows.
 *   5. Every element with an interactive role (button, link, input, select)
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
      const docScrollWidth = document.documentElement.scrollWidth;
      const rows = document.querySelectorAll('#incidents tbody tr[data-row]').length;

      const wrap = document.querySelector('.table-wrap');
      const wrapScrollWidth = wrap ? wrap.scrollWidth : null;
      const wrapClientWidth = wrap ? wrap.clientWidth : null;

      // Rightmost VISIBLE cell of the first data row -- at 380px that's
      // Severity, since .col-llm/.col-asi/.col-cves are display:none below
      // 640px (style.css). getComputedStyle().display catches the hidden
      // columns; offsetParent === null catches any other hide mechanism.
      let lastVisibleCellRight = null;
      let lastVisibleCellTag = null;
      const firstRow = document.querySelector('#incidents tbody tr[data-row]');
      if (firstRow) {
        const cells = Array.from(firstRow.children).filter(
          el => getComputedStyle(el).display !== 'none' && el.offsetParent !== null,
        );
        const last = cells[cells.length - 1];
        if (last) {
          lastVisibleCellRight = last.getBoundingClientRect().right;
          lastVisibleCellTag = `${last.tagName}.${Array.from(last.classList).join('.')}`;
        }
      }

      const smallTargets = [];
      document.querySelectorAll('.filters button, .filters input, .filters select, .cta, .theme-toggle')
        .forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && r.height > 0 && r.height < 24) {
            smallTargets.push({ tag: el.tagName, id: el.id || null, height: Math.round(r.height) });
          }
        });
      return {
        docScrollWidth, rows, smallTargets,
        wrapScrollWidth, wrapClientWidth,
        lastVisibleCellRight, lastVisibleCellTag,
        innerWidth: window.innerWidth,
      };
    }, WIDTH);

    console.log(`[380px] document.scrollWidth = ${report.docScrollWidth} (viewport ${WIDTH})`);
    console.log(`[380px] .table-wrap scrollWidth/clientWidth = ${report.wrapScrollWidth}/${report.wrapClientWidth}`);
    console.log(`[380px] last visible cell (${report.lastVisibleCellTag}) right edge = ${report.lastVisibleCellRight} (innerWidth ${report.innerWidth})`);
    console.log(`[380px] visible table rows = ${report.rows}`);
    console.log(`[380px] undersized touch targets = ${report.smallTargets.length}`);
    for (const t of report.smallTargets) console.log(`  - ${t.tag}${t.id ? '#' + t.id : ''}: ${t.height}px`);

    // Sub-pixel layout rounding (fractional device pixels from CSS
    // transforms/zoom) can put a genuinely-fitting edge a fraction of a
    // pixel over its target; allow a 1px tolerance, not a percentage --
    // a percentage would re-open exactly the "cannot fail" hole this check
    // exists to close.
    const TOLERANCE_PX = 1;

    // .table-wrap's own scrollWidth needs a wider, still-tiny tolerance:
    // measured against the CURRENT, correctly-fitting CSS (four visible
    // columns fixed to 20/24/32/24%, three hidden columns pinned to 0
    // width), Chromium's table-layout:fixed + border-collapse column-width
    // resolution still reports .table-wrap.scrollWidth ~7px above
    // .clientWidth -- reproduced with border-collapse:separate, with the
    // hidden columns removed from the DOM entirely, and with the sticky
    // thead cells de-sticky'd, so it is not caused by any of those and is
    // not remotely visible or reachable in practice (wrap.scrollLeft(7)
    // "succeeds" but shifts no rendered content -- confirmed by screenshot
    // diff). This is two orders of magnitude below the failure signal this
    // check exists to catch: forcing the table to min-width:1200px (the A1
    // repro below) pushes wrapScrollWidth to ~1200, roughly 850px past
    // clientWidth. WRAP_TOLERANCE_PX is set to double the measured noise
    // floor -- enough margin for that reporting quirk across Chromium point
    // releases, nowhere near enough to hide a real overflow.
    const WRAP_TOLERANCE_PX = 16;

    let failed = false;
    if (report.docScrollWidth > WIDTH) {
      console.error(`::error::page overflows its 380px viewport (scrollWidth=${report.docScrollWidth})`);
      failed = true;
    }
    if (report.wrapScrollWidth === null) {
      console.error('::error::.table-wrap not found -- cannot check table overflow');
      failed = true;
    } else if (report.wrapScrollWidth > report.wrapClientWidth + WRAP_TOLERANCE_PX) {
      console.error(`::error::table overflows its own scroll container at 380px ` +
        `(.table-wrap scrollWidth=${report.wrapScrollWidth} > clientWidth=${report.wrapClientWidth}) -- ` +
        `the table requires horizontal scrolling to see all visible columns`);
      failed = true;
    }
    if (report.lastVisibleCellRight === null) {
      console.error('::error::no visible data-row cell found -- cannot check right-edge overflow');
      failed = true;
    } else if (report.lastVisibleCellRight > report.innerWidth + TOLERANCE_PX) {
      console.error(`::error::rightmost visible column (${report.lastVisibleCellTag}) extends past the ` +
        `380px viewport (right=${report.lastVisibleCellRight}, innerWidth=${report.innerWidth})`);
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
