// PNG region diff with named ROIs. Region-split matters: the whole S1 question is
// whether error lives in the *interior* (sampling wrong content) or only in an
// *edge band* (blur clamped at the filtered element's own bounds).
import { PNG } from 'pngjs';
import { readFileSync, writeFileSync } from 'node:fs';

export function load(path) {
  return PNG.sync.read(readFileSync(path));
}

function inRect(x, y, r) {
  return x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h;
}

/** roi: { x,y,w,h, exclude?: rect[] } in capture-local CSS px. dsf scales it. */
export function diffROI(a, b, roi, dsf = 1) {
  const R = {
    x: Math.round(roi.x * dsf),
    y: Math.round(roi.y * dsf),
    w: Math.round(roi.w * dsf),
    h: Math.round(roi.h * dsf),
  };
  const ex = (roi.exclude || []).map((r) => ({
    x: Math.round(r.x * dsf),
    y: Math.round(r.y * dsf),
    w: Math.round(r.w * dsf),
    h: Math.round(r.h * dsf),
  }));
  let n = 0, sum = 0, max = 0, over2 = 0, over8 = 0, over24 = 0;
  for (let y = R.y; y < Math.min(R.y + R.h, a.height, b.height); y++) {
    for (let x = R.x; x < Math.min(R.x + R.w, a.width, b.width); x++) {
      if (ex.some((r) => inRect(x, y, r))) continue;
      const i = (a.width * y + x) << 2;
      const j = (b.width * y + x) << 2;
      const d = Math.max(
        Math.abs(a.data[i] - b.data[j]),
        Math.abs(a.data[i + 1] - b.data[j + 1]),
        Math.abs(a.data[i + 2] - b.data[j + 2]),
      );
      n++; sum += d;
      if (d > max) max = d;
      if (d > 2) over2++;
      if (d > 8) over8++;
      if (d > 24) over24++;
    }
  }
  return {
    n,
    mean: n ? +(sum / n).toFixed(2) : 0,
    max,
    pctOver2: n ? +((100 * over2) / n).toFixed(2) : 0,
    pctOver8: n ? +((100 * over8) / n).toFixed(2) : 0,
    pctOver24: n ? +((100 * over24) / n).toFixed(2) : 0,
  };
}

export function heatmap(a, b, outPath, gain = 6) {
  const w = Math.min(a.width, b.width), h = Math.min(a.height, b.height);
  const out = new PNG({ width: w, height: h });
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (a.width * y + x) << 2;
      const j = (b.width * y + x) << 2;
      const k = (w * y + x) << 2;
      const d = Math.max(
        Math.abs(a.data[i] - b.data[j]),
        Math.abs(a.data[i + 1] - b.data[j + 1]),
        Math.abs(a.data[i + 2] - b.data[j + 2]),
      );
      const v = Math.min(255, d * gain);
      out.data[k] = v;
      out.data[k + 1] = d > 24 ? v : 0;
      out.data[k + 2] = d > 2 ? 40 : 0;
      out.data[k + 3] = 255;
    }
  }
  writeFileSync(outPath, PNG.sync.write(out));
}

/** Exact RGB at a capture-local CSS-px point (averaged over a 3x3 device block). */
export function pixel(png, x, y, dsf = 1) {
  const px = Math.round(x * dsf), py = Math.round(y * dsf);
  let r = 0, g = 0, b = 0, n = 0;
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      const i = (png.width * (py + dy) + (px + dx)) << 2;
      r += png.data[i]; g += png.data[i + 1]; b += png.data[i + 2]; n++;
    }
  }
  return [Math.round(r / n), Math.round(g / n), Math.round(b / n)];
}
