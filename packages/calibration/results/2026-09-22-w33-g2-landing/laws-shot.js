async page => {
  // W33 G2, §5.173: the installed full Chromium at DPR 2, one X6-attested session.
  const out = '/Users/new/Developer/GitHub/designer/.claude/worktrees/w33-g2-landing/packages/calibration/results/2026-09-22-w33-g2-landing';
  await page.waitForSelector('[data-vitrea-root]', { state: 'attached' });
  await page.evaluate(() => document.getElementById('shadow')?.scrollIntoView({
    block: 'center', behavior: 'instant',
  }));
  const readings = [];
  for (const pose of ['active', 'receded']) {
    await page.getByTestId('shadow-pose').selectOption(pose);
    for (const span of ['96', '160']) {
      await page.getByTestId('shadow-span').fill(span);
      await page.waitForTimeout(1200);
      const name = `laws-shadow-${pose}-${span}.png`;
      await page.locator('.stage').first().screenshot({ path: `${out}/${name}` });
      const read = await page.evaluate(() => Object.fromEntries(
        ['shadow-endpoint', 'shadow-sigma', 'shadow-outset', 'shadow-offset',
         'shadow-depth-3', 'shadow-depth-12', 'shadow-depth-24'].map(id => [
          id, document.querySelector(`[data-testid="${id}"]`)?.textContent ?? '',
        ]),
      ));
      readings.push({ name, ...read });
    }
  }
  return { url: page.url(), dpr: await page.evaluate(() => devicePixelRatio), readings };
}
