async page => {
  const out = '/Users/new/Developer/GitHub/designer/.claude/worktrees/w36-g2-landing/packages/calibration/results/2026-09-24-w36-g2-landing';
  await page.waitForSelector('[data-vitrea-root]', { state: 'attached' });
  await page.getByTestId('shadow-pose').selectOption('active');
  await page.evaluate(() => document.getElementById('tone').scrollIntoView({
    block: 'center', behavior: 'instant',
  }));
  await page.getByTestId('tone-level').fill('0');
  await page.waitForFunction(() => {
    const text = document.getElementById('tone').textContent;
    return text.includes('0.000 linear') && text.includes('webgpu') && text.includes('gpu-texture');
  });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1200);
  const stage = page.locator('.stage').first();
  const stageBox = await stage.boundingBox();
  const smallBox = await page.getByTestId('tone-small').boundingBox();
  const first = await stage.screenshot({ path: `${out}/laws-black.png`, animations: 'disabled' });
  await page.waitForTimeout(250);
  const second = await stage.screenshot({ path: `${out}/laws-black-repeat.png`, animations: 'disabled' });
  const deterministic = first.equals(second);
  const reading = await page.locator('#tone').innerText();
  const adapter = await page.evaluate(async () => {
    const a = await navigator.gpu.requestAdapter();
    return a ? { vendor: a.info.vendor, architecture: a.info.architecture,
      isFallbackAdapter: a.info.isFallbackAdapter } : null;
  });
  if (!deterministic) throw new Error('Eye capture is not byte-deterministic; retain, do not retry');
  if (!adapter || adapter.vendor !== 'apple' || adapter.isFallbackAdapter) {
    throw new Error('Eye capture did not use the hardware adapter');
  }
  return { url: page.url(), dpr: await page.evaluate(() => devicePixelRatio),
    stageBox, smallBox, deterministic, adapter, reading,
    qualification: 'Demo spans40/112 beside measured span44; juxtaposition, not silhouette equality.' };
}
