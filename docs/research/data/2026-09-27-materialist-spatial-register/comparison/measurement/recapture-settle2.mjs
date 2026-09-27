// What still changes in the open platter between 1.5 s and 4.5 s after opening, per region.
import { gpuBrowser, frames, CARET, PORT, PNG } from "/Users/new/Developer/GitHub/designer/docs/research/data/2026-09-27-materialist-spatial-register/comparison/measurement/lib.mjs";
const browser = await gpuBrowser();
for (const glass of ["regular", "clear"]) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, colorScheme: "dark" });
  const page = await ctx.newPage();
  await page.goto(`http://localhost:${PORT}/gallery/start-page/?at=15:10${glass === "clear" ? "&glass=clear" : ""}`);
  await page.waitForFunction(() => window.__vitrea && window.__glassDemo);
  await page.addStyleTag({ content: CARET });
  await page.evaluate(() => window.__glassDemo.setPhase("day")); await page.waitForTimeout(900);
  const t0 = Date.now();
  await page.evaluate(() => window.__glassDemo.openMenu());
  const shots = [];
  for (const at of [1500, 2000, 2500, 3000, 3500, 4500, 6000]) {
    const wait = at - (Date.now() - t0); if (wait > 0) await page.waitForTimeout(wait);
    await frames(page, 1);
    const state = await page.evaluate(() => { const r = window.__vitrea; const g = r.scene.glassGroup("photograph"); const el = document.querySelector(".photograph-morph"); const q = el.getBoundingClientRect(); return { rect: [q.x, q.y, q.width, q.height], hint: g.descriptor.backdrop?.luminance, activeEl: document.activeElement?.getAttribute("aria-label") ?? document.activeElement?.textContent?.slice(0, 20) ?? null, focusVisible: document.activeElement?.matches(":focus-visible") ?? null, nodes: (r.renderInput()?.planes ?? []).flatMap((p) => p.nodes.filter((n) => n.groupId === "photograph").map((n) => ({ radius: n.shape?.radius ?? n.radius, w: n.rect?.width ?? null, opacity: n.opacity ?? null, blurSigma: n.optics?.blurSigma, tintAlpha: n.optics?.tintAlpha }))) }; });
    shots.push({ at: Date.now() - t0, png: PNG.sync.read(await page.screenshot()), state });
  }
  const last = shots.at(-1).png;
  for (const s of shots) {
    const a = s.png; let n = 0, max = 0, box = [1e9, 1e9, -1, -1]; let nIn = 0;
    const [rx, ry, rw, rh] = s.state.rect;
    for (let y = 0; y < a.height; y++) for (let x = 0; x < a.width; x++) { const i = (y * a.width + x) * 4; let d = 0; for (let k = 0; k < 3; k++) d = Math.max(d, Math.abs(a.data[i + k] - last.data[i + k])); if (d) { n++; max = Math.max(max, d); box = [Math.min(box[0], x), Math.min(box[1], y), Math.max(box[2], x), Math.max(box[3], y)]; if (x >= rx && x < rx + rw && y >= ry && y < ry + rh) nIn++; } }
    console.log(glass, String(s.at).padStart(5), "vs last: px", n, "inPlatter", nIn, "max", max, "bbox", n ? box.join(",") : "-", "| rect", s.state.rect.map((v) => +v.toFixed(2)).join(","), "hint", s.state.hint, "focus", s.state.activeEl, s.state.focusVisible, "| node", JSON.stringify(s.state.nodes[0]));
  }
  await ctx.close();
}
await browser.close();
