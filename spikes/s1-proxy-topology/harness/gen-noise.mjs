// Deterministic high-frequency raster for the "an image" backdrop case.
// High spatial frequency is the strongest tell for blur-radius and edge-clamp error.
import { PNG } from 'pngjs';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const W = 500;
const H = 75;
const png = new PNG({ width: W, height: H });

// xorshift32 — stable across platforms, no Math.random.
let s = 0x2545f491;
const rnd = () => {
  s ^= s << 13; s >>>= 0;
  s ^= s >> 17;
  s ^= s << 5; s >>>= 0;
  return s / 0x100000000;
};

for (let y = 0; y < H; y++) {
  for (let x = 0; x < W; x++) {
    const i = (W * y + x) << 2;
    // Blocky 5px noise plus a 1px grid — both a low- and a high-frequency probe.
    const bx = Math.floor(x / 5), by = Math.floor(y / 5);
    const blocky = ((bx * 73856093) ^ (by * 19349663)) >>> 0;
    const r = (blocky & 0xff);
    const g = ((blocky >> 8) & 0xff);
    const b = ((blocky >> 16) & 0xff);
    const grid = (x % 4 === 0 || y % 4 === 0) ? 255 : 0;
    png.data[i]     = Math.min(255, (r * 0.7 + grid * 0.3) | 0);
    png.data[i + 1] = Math.min(255, (g * 0.7 + grid * 0.3) | 0);
    png.data[i + 2] = Math.min(255, (b * 0.7 + grid * 0.3) | 0);
    png.data[i + 3] = 255;
  }
}
void rnd;

const out = join(dirname(fileURLToPath(import.meta.url)), '..', 'pages', 'noise.png');
writeFileSync(out, PNG.sync.write(png));
console.log('wrote', out);
