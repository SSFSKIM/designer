// PNG region diff. The per-pixel statistic is S1's, unchanged, so the numbers in
// this experiment's table sit in the same units as S1's leak table: the maximum
// absolute per-channel difference over R, G, B, in 0-255 space. Added here: p99
// and p999 of that same statistic, because a leak that lives in a thin band is
// better described by its tail than by a mean diluted over the whole region.
import { PNG } from 'pngjs';
import { readFileSync, writeFileSync } from 'node:fs';

export function load(path) {
  return PNG.sync.read(readFileSync(path));
}

/** roi: { x,y,w,h } in capture-local CSS px. */
export function diffROI(a, b, roi) {
  const hist = new Uint32Array(256);
  let n = 0;
  let sum = 0;
  let max = 0;
  let over2 = 0;
  for (let y = roi.y; y < Math.min(roi.y + roi.h, a.height, b.height); y++) {
    for (let x = roi.x; x < Math.min(roi.x + roi.w, a.width, b.width); x++) {
      const i = (a.width * y + x) << 2;
      const j = (b.width * y + x) << 2;
      const d = Math.max(
        Math.abs(a.data[i] - b.data[j]),
        Math.abs(a.data[i + 1] - b.data[j + 1]),
        Math.abs(a.data[i + 2] - b.data[j + 2]),
      );
      n++;
      sum += d;
      hist[d]++;
      if (d > max) max = d;
      if (d > 2) over2++;
    }
  }
  const quantile = (q) => {
    let seen = 0;
    const target = q * n;
    for (let v = 0; v < 256; v++) {
      seen += hist[v];
      if (seen >= target) return v;
    }
    return 0;
  };
  return {
    n,
    mean: n ? +(sum / n).toFixed(3) : 0,
    p99: n ? quantile(0.99) : 0,
    p999: n ? quantile(0.999) : 0,
    max,
    pctOver2: n ? +((100 * over2) / n).toFixed(2) : 0,
  };
}

export function heatmap(a, b, outPath, gain = 12) {
  const w = Math.min(a.width, b.width);
  const h = Math.min(a.height, b.height);
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
      out.data[k + 1] = d > 8 ? v : 0;
      out.data[k + 2] = d > 0 ? 40 : 0;
      out.data[k + 3] = 255;
    }
  }
  writeFileSync(outPath, PNG.sync.write(out));
}
