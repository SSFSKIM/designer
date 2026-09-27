async page => {
  const base = 'http://127.0.0.1:8769';
  const scale = 1;
  const hash = async bytes => page.evaluate(async input => {
    const digest = await crypto.subtle.digest('SHA-256',new Uint8Array(input));
    return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  },Array.from(bytes));
  const hashText = text => page.evaluate(async value => {
    const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value));
    return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  },text);
  const browser = page.context().browser();
  const browserName = browser.browserType().name();
  const version = browser.version();
  if (browserName !== 'chromium' || !/^\d+\./.test(version)) throw new Error('Not full Chromium');
  await page.setViewportSize({width:320,height:280});
  await page.goto(base + '/fixture.html');
  const dpr = await page.evaluate(() => devicePixelRatio);
  const viewport = page.viewportSize();
  if (dpr !== scale || viewport.width !== 320 || viewport.height !== 280)
    throw new Error('Wrong browser viewport or DPR');
  const manifestResponse = await page.request.get(base + '/manifest.json');
  const manifestText = await manifestResponse.text();
  const manifestSha256 = await hashText(manifestText);
  const prepared = JSON.parse(manifestText);
  const configText = await (await page.request.get(base + '/playwright-1x.json')).text();
  const configSha256 = await hashText(configText);
  const config = JSON.parse(configText);
  const fixtureText = await (await page.request.get(base + '/fixture.html')).text();
  const cellsText = await (await page.request.get(base + '/cells.json')).text();
  const proofRowsText = await (await page.request.get(base + '/proof-rows.json')).text();
  if (await hashText(fixtureText) !== prepared.artifacts['fixture.html'] ||
      await hashText(cellsText) !== prepared.artifacts['cells.json'] ||
      await hashText(proofRowsText) !== prepared.artifacts['proof-rows.json'])
    throw new Error('Served fixture is not the prepared fixture');
  if (config.browser.browserName !== browserName ||
      config.browser.launchOptions.channel !== 'chromium' ||
      config.browser.launchOptions.args.join() !== '--force-color-profile=srgb' ||
      config.browser.contextOptions.deviceScaleFactor !== dpr)
    throw new Error('Prepared browser configuration differs');
  const identity = {manifestSha256,configSha256,browserName,version,dpr,viewport,
    userAgent:await page.evaluate(() => navigator.userAgent)};
  const scriptSha256 = await hashText(
    await (await page.request.get(base + '/capture-1x.js')).text());
  if (scriptSha256 !== prepared.artifacts['capture-1x.js'])
    throw new Error('Capture script differs from prepared manifest');
  const proofResponse = await page.request.get(base + '/proof-passed.json');
  if (!proofResponse.ok()) throw new Error('Both-scale pixel proof must pass first');
  const proofText = await proofResponse.text();
  const proofSha256 = await hashText(proofText);
  const proof = JSON.parse(proofText);
  if (!proof.passes || proof.publicManifestSha256!==manifestSha256 ||
      JSON.stringify(proof.sources)!==JSON.stringify(prepared.sources) || proof.runIds.length!==2)
    throw new Error('Proof not bound to this prepared manifest');
  const cells = await (await page.request.get(base + '/cells.json')).json();
  const rows = [];
  for (const [cell, data] of Object.entries(cells)) {
    if (data.scale !== scale) continue;
    for (const route of ['plate','affine']) {
      await page.evaluate(async ({cell,route}) => window.showCell(cell,route), {cell,route});
      const observed = await page.evaluate(() => window.observed);
      if (observed.cell!==cell || observed.route!==route || observed.dpr!==scale ||
          !observed.bodyOnly || observed.productionTier || !observed.filter)
        throw new Error('Fixture did not draw requested BODY cell');
      const path = "/Users/new/vitrea-w41/g1-captures/css-projection" + '/' + route + '/' + cell + '.png';
      const png = await page.screenshot({path,scale:'device'});
      rows.push({cell,route,scale,path,sha256:await hash(png),observed});
    }
  }
  const runId = await page.evaluate(() => crypto.randomUUID());
  return 'W41_CSS_RUN:' + JSON.stringify({kind:'capture',...identity,scriptSha256,proofSha256,runId,
    proofRunIds:proof.runIds,rows});
}