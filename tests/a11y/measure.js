'use strict';
// Ad-hoc measurement script (not a CI gate) -- used to capture the
// before/after numbers for the WS6-T5 report: time to first table paint,
// JS heap after load, and total transferred bytes for the page + dataset.
const puppeteer = require('puppeteer-core');
const { findChrome } = require('./find_chrome');

const URL_TO_TEST = process.argv[2] || 'http://127.0.0.1:8123/';
const WIDTH = parseInt(process.argv[3] || '1280', 10);

async function main() {
  const browser = await puppeteer.launch({
    executablePath: findChrome(),
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: WIDTH, height: 900 });
    let totalBytes = 0;
    const client = await page.target().createCDPSession();
    await client.send('Network.enable');
    client.on('Network.loadingFinished', e => { totalBytes += e.encodedDataLength || 0; });

    const t0 = Date.now();
    await page.goto(URL_TO_TEST, { waitUntil: 'networkidle0', timeout: 120000 });
    const tNetIdle = Date.now() - t0;
    await page.waitForSelector('#incidents tbody tr[data-row]', { timeout: 60000 });
    const tFirstRow = Date.now() - t0;

    const metrics = await page.metrics();
    const heap = await page.evaluate(() => performance.memory ? performance.memory.usedJSHeapSize : null);
    const rowCount = await page.evaluate(() => document.querySelectorAll('#incidents tbody tr').length);
    const totalIncidents = await page.evaluate(() => (window.DATA || []).length);

    console.log(JSON.stringify({
      url: URL_TO_TEST,
      viewportWidth: WIDTH,
      msToNetworkIdle: tNetIdle,
      msToFirstTableRow: tFirstRow,
      domNodesInTableBody: rowCount,
      totalIncidentsLoaded: totalIncidents,
      jsHeapUsedBytes: heap,
      puppeteerMetrics: metrics,
      totalTransferredBytes: totalBytes,
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(err => { console.error(err); process.exit(1); });
