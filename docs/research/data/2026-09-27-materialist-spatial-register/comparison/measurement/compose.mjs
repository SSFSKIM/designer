// Compose each comparison pair: label strip on top, regular left, clear right, 6 px black
// between. Halves at 1440 wide (the 2x capture area-averaged 2:1); if that PNG is over 4 MB,
// the whole composite at 1440 wide instead. No browser: the strips were drawn during the run.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
const require = createRequire("/Users/new/Developer/GitHub/designer/apps/demo/package.json");
const { PNG } = require("pngjs");
const OUT = "/Users/new/Developer/GitHub/designer/docs/research/data/2026-09-27-materialist-spatial-register/comparison";
mkdirSync(OUT, { recursive: true });
const LIMIT = 4 * 1024 * 1024;

function resample(src, w, h) {
  // Exact area average, separable, in encoded values (a display downscale, not a measurement).
  const sw = src.width, sh = src.height;
  const tmp = new Float64Array(w * sh * 3);
  const fx = sw / w, fy = sh / h;
  for (let y = 0; y < sh; y++) for (let x = 0; x < w; x++) {
    const a = x * fx, b = a + fx; let r = 0, g = 0, bl = 0;
    for (let sx = Math.floor(a); sx < Math.ceil(b); sx++) {
      const wgt = Math.min(b, sx + 1) - Math.max(a, sx); const i = (y * sw + sx) * 4;
      r += src.data[i] * wgt; g += src.data[i + 1] * wgt; bl += src.data[i + 2] * wgt;
    }
    const o = (y * w + x) * 3; tmp[o] = r / fx; tmp[o + 1] = g / fx; tmp[o + 2] = bl / fx;
  }
  const out = { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) };
  for (let x = 0; x < w; x++) for (let y = 0; y < h; y++) {
    const a = y * fy, b = a + fy; let r = 0, g = 0, bl = 0;
    for (let sy = Math.floor(a); sy < Math.ceil(b); sy++) {
      const wgt = Math.min(b, sy + 1) - Math.max(a, sy); const i = (sy * w + x) * 3;
      r += tmp[i] * wgt; g += tmp[i + 1] * wgt; bl += tmp[i + 2] * wgt;
    }
    const o = (y * w + x) * 4; out.data[o] = Math.round(r / fy); out.data[o + 1] = Math.round(g / fy); out.data[o + 2] = Math.round(bl / fy); out.data[o + 3] = 255;
  }
  return out;
}

function compose(name, size) {
  const [half, gap] = size === "wide" ? [1440, 6] : [717, 6];
  const left = PNG.sync.read(readFileSync(`/tmp/sp-clear/cmp/${name}-regular.png`));
  const right = PNG.sync.read(readFileSync(`/tmp/sp-clear/cmp/${name}-clear.png`));
  const stripRaw = PNG.sync.read(readFileSync(`/tmp/sp-clear/cmp/strip-${name}-${size}.png`));
  const hh = Math.round((left.height * half) / left.width);
  const W = half * 2 + gap;
  const strip = resample(stripRaw, W, Math.round(stripRaw.height / 2));
  const L = resample(left, half, hh), R = resample(right, half, hh);
  const H = strip.height + hh;
  const png = new PNG({ width: W, height: H, colorType: 2, inputHasAlpha: true });
  png.data.fill(0);
  for (let i = 3; i < png.data.length; i += 4) png.data[i] = 255;
  const blit = (img, ox, oy) => { for (let y = 0; y < img.height; y++) for (let x = 0; x < img.width; x++) { const s = (y * img.width + x) * 4, d = ((oy + y) * W + ox + x) * 4; png.data[d] = img.data[s]; png.data[d + 1] = img.data[s + 1]; png.data[d + 2] = img.data[s + 2]; } };
  blit(strip, 0, 0); blit(L, 0, strip.height); blit(R, half + gap, strip.height);
  return PNG.sync.write(png, { colorType: 2, inputHasAlpha: true, deflateLevel: 9, filterType: -1 });
}

for (const name of ["light-day", "dark-night", "dark-night-platter"]) {
  let size = "wide", buf = compose(name, size);
  if (buf.length > LIMIT) { size = "narrow"; buf = compose(name, size); }
  writeFileSync(`${OUT}/${name}.png`, buf);
  const { width, height } = PNG.sync.read(buf);
  console.log(`${name}.png ${size} ${width}x${height} ${(buf.length / 1048576).toFixed(2)} MB`);
}
