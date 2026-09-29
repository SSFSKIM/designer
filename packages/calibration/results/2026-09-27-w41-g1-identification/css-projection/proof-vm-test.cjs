// Simulate the playwright-cli run-code VM without starting a browser.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');

const publicDir = process.argv[2];
const script = fs.readFileSync(path.join(publicDir, 'proof-1x.js'), 'utf8');
const browserGlobals = {
  crypto: webcrypto, TextEncoder, devicePixelRatio: 1,
  navigator: { userAgent: 'Chrome/123' }, window: { showProof: async () => {} },
};
const page = {
  context: () => ({ browser: () => ({
    browserType: () => ({ name: () => 'chromium' }), version: () => '123.0.0',
  }) }),
  setViewportSize: async () => {}, goto: async () => {},
  viewportSize: () => ({ width: 320, height: 280 }),
  request: { get: async url => ({
    text: async () => fs.readFileSync(path.join(publicDir, new URL(url).pathname.slice(1)), 'utf8'),
  }) },
  evaluate: (fn, arg) => vm.runInNewContext('(' + fn.toString() + ')', browserGlobals)(arg),
  screenshot: async () => Buffer.from('offline mock screenshot'),
};
(async () => {
  const callback = vm.runInNewContext('(' + script + ')', { page, __end__: () => {} });
  console.log(await callback(page));
})().catch(error => { console.error(error); process.exitCode = 1; });
