'use strict';
/*
 * Resolve a Chrome/Chromium executable without downloading one: honour
 * CHROME_PATH if set (what the CI workflow exports), else ask chrome-launcher
 * to enumerate whatever's actually installed (it already knows the standard
 * install locations for Linux GH Actions runners, Windows, and macOS).
 * Keeping this in one place means check_axe.js and check_lighthouse.js can
 * never disagree about which browser they're auditing.
 */
const chromeLauncher = require('chrome-launcher');

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const installations = chromeLauncher.Launcher.getInstallations();
  if (!installations.length) {
    throw new Error(
      'No Chrome/Chromium installation found and CHROME_PATH is not set. ' +
      'Set CHROME_PATH to an executable, or install Chrome.',
    );
  }
  return installations[0];
}

module.exports = { findChrome };
