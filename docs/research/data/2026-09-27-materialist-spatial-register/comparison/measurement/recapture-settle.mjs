// Does the open platter come to rest at integer geometry, and when? One page per mode.
import { gpuBrowser, frames, CARET, PORT, sha, PNG } from "/Users/new/Developer/GitHub/designer/docs/research/data/2026-09-27-materialist-spatial-register/comparison/measurement/lib.mjs";
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
  const probe = () => page.evaluate(async () => {
    const el = document.querySelector(".photograph-morph"); const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    const inner = el.querySelector(".platter") ?? el.firstElementChild; const ir = inner ? inner.getBoundingClientRect() : null; const ics = inner ? getComputedStyle(inner) : null;
    const row = [...el.querySelectorAll(".setting, label, button")].slice(0, 3).map((e) => { const q = e.getBoundingClientRect(); return [+q.y.toFixed(3), +q.height.toFixed(3)]; });
    const c = document.querySelector("canvas.environment"); const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
    const h = new Uint8Array(await crypto.subtle.digest("SHA-256", d));
    return { rect: [r.x, r.y, r.width, r.height].map((v) => +v.toFixed(3)), transform: cs.transform, innerRect: ir && [ir.x, ir.y, ir.width, ir.height].map((v) => +v.toFixed(3)), innerTransform: ics?.transform, rows: row, canvas: [...h.slice(0, 6)].map((b) => b.toString(16).padStart(2, "0")).join(""), anims: document.getAnimations().length };
  });
  const samples = [];
  for (const at of [200, 400, 700, 1000, 1400, 2000, 3000, 4500]) {
    const wait = at - (Date.now() - t0); if (wait > 0) await page.waitForTimeout(wait);
    await frames(page, 1);
    const p = await probe();
    const shot = PNG.sync.read(await page.screenshot({ clip: { x: 40, y: 600, width: 360, height: 300 } }));
    samples.push({ at: Date.now() - t0, ...p, shot: sha(shot.data) });
  }
  for (const s of samples) console.log(glass, String(s.at).padStart(5), "rect", s.rect.join(","), "tf", s.transform, "| inner", s.innerRect?.join(","), s.innerTransform, "| rows", JSON.stringify(s.rows), "| canvas", s.canvas, "shot", s.shot, "anims", s.anims);
  await ctx.close();
}
await browser.close();
