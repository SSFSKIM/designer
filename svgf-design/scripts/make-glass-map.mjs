#!/usr/bin/env node
// Engineered liquid-glass displacement-map generator + self-contained snippet
// emitter. Ported from the Task-1 spike's sibling-architecture prototype
// (figma-design-workspace/glass-spike/proto-glass-map-v2-sibling.mjs), whose
// physics and layering were verified there — do not re-derive them here.
//
// Sign convention (verified, do not flip): outward-normal sampling,
// r = 128 + nx*m*127, g = 128 + ny*m*127. No sign flip.
// Falloff: quarter-circle lens slope over the bezel, normalized by /5 and
// clamped to 1 (min(s/5, 1)).
//
// Architecture (the one non-negotiable lesson from the spike): the refract
// layer must be a SIBLING of the frost layer under a parent that carries NO
// filter/backdrop-filter of its own. An element with backdrop-filter becomes
// its descendants' backdrop root (atlas §2.8) — nesting the refract layer
// inside a filtered ancestor makes it invisibly displace a flat tint instead
// of the real backdrop. Because the refract layer paints AFTER (over) the
// frost layer in Chromium, its own filter chain must reproduce the whole
// glass look: feImage(map) -> feDisplacementMap(scale=strength) ->
// feGaussianBlur(stdDeviation 3) -> feColorMatrix(type=saturate, values=1.6).

import { deflateSync } from 'node:zlib';
import { parseArgs } from 'node:util';

// ---- geometry ------------------------------------------------------------

// Signed distance to a rounded-rect boundary. Positive = inside.
function insideDist(px, py, w, h, r) {
  const cx = px - w / 2, cy = py - h / 2;
  const bx = w / 2 - r, by = h / 2 - r;
  const qx = Math.abs(cx) - bx, qy = Math.abs(cy) - by;
  const outer =
    Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) +
    Math.min(Math.max(qx, qy), 0) - r;
  return -outer;
}

// Outward normal via central differences (shape-agnostic).
function outwardNormal(px, py, w, h, r) {
  const e = 0.5;
  const gx = insideDist(px + e, py, w, h, r) - insideDist(px - e, py, w, h, r);
  const gy = insideDist(px, py + e, w, h, r) - insideDist(px, py - e, w, h, r);
  const len = Math.hypot(gx, gy) || 1;
  return [-gx / len, -gy / len]; // gradient points inward; flip for outward
}

// Lens falloff over the bezel: 1 at the boundary, 0 at the inner bezel edge.
function falloff(t) { // t = insideDist / bezel in [0,1]
  const s = (1 - t) / Math.sqrt(Math.max(1 - (1 - t) ** 2, 0.04));
  return Math.min(s / 5, 1); // normalize: slope 5 = full strength
}

// Resolve the effective corner radius for a shape keyword.
function resolveRadius(shape, height, radius) {
  if (shape === 'pill') return height / 2;
  if (shape === 'rect') return 4;
  return radius; // squircle: given radius, same rounded-rect SDF
}

const SS = 2; // supersample: map rendered at 2x (banding guard)

/**
 * Generate the RGBA displacement map for an element of the given size.
 * @returns {{ rgba: Buffer, mapWidth: number, mapHeight: number }}
 */
export function generateMap({ width, height, radius, bezel, strength, shape }) {
  const r = resolveRadius(shape, height, radius);
  const mw = width * SS, mh = height * SS;
  const rgba = Buffer.alloc(mw * mh * 4);
  for (let y = 0; y < mh; y++) {
    for (let x = 0; x < mw; x++) {
      const px = (x + 0.5) / SS, py = (y + 0.5) / SS;
      const d = insideDist(px, py, width, height, r);
      let rr = 128, gg = 128;
      if (d > 0 && d < bezel) {
        const [nx, ny] = outwardNormal(px, py, width, height, r);
        const m = falloff(d / bezel);
        // SIGN CONVENTION (Task-1 spike verdict, verified): sample outward
        // at the rim (magnify). Do not flip.
        rr = Math.round(128 + nx * m * 127);
        gg = Math.round(128 + ny * m * 127);
      }
      const i = (y * mw + x) * 4;
      rgba[i] = rr; rgba[i + 1] = gg; rgba[i + 2] = 128; rgba[i + 3] = 255; // opaque, B neutral
    }
  }
  void strength; // strength only affects the emitted filter's scale attr, not the map
  return { rgba, mapWidth: mw, mapHeight: mh };
}

// ---- minimal PNG encoder (8-bit RGBA, filter 0) ---------------------------

const CRC_TABLE = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type, 'latin1'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}
function encodePNG(width, height, pixels) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; ihdr[9] = 6; // 8-bit, RGBA
  const stride = width * 4;
  const raw = Buffer.alloc((stride + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (stride + 1)] = 0; // filter type 0
    pixels.copy(raw, y * (stride + 1) + 1, y * stride, (y + 1) * stride);
  }
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

// ---- snippet emission ------------------------------------------------------

/**
 * Render the complete self-contained snippet: SVG filter (data-URI map) +
 * sibling-architecture CSS + HTML usage comment.
 */
export function renderSnippet(opts) {
  const { width, height, radius, bezel, strength, shape } = opts;
  const map = generateMap(opts);
  const dataUri = `data:image/png;base64,${encodePNG(map.mapWidth, map.mapHeight, map.rgba).toString('base64')}`;
  const filterId = `svgf-glass-${width}-${height}`;
  const r = resolveRadius(shape, height, radius);

  return `<svg width="0" height="0" aria-hidden="true" style="position:absolute">
  <filter id="${filterId}" x="0" y="0" width="100%" height="100%"
          color-interpolation-filters="sRGB" primitiveUnits="userSpaceOnUse">
    <feImage href="${dataUri}" x="0" y="0" width="${width}" height="${height}" result="map"/>
    <feDisplacementMap in="SourceGraphic" in2="map" scale="${strength}"
                       xChannelSelector="R" yChannelSelector="G" result="displaced"/>
    <feGaussianBlur in="displaced" stdDeviation="3" result="blurred"/>
    <feColorMatrix in="blurred" type="saturate" values="1.6"/>
  </filter>
</svg>
<style>
  /* Parent: position/radius/overflow only. NO filter/backdrop-filter/opacity
     — every child below shares the page as its backdrop root (atlas §2.8).
     The opaque worst-case fill is gated to browsers WITHOUT backdrop-filter
     support; in supporting browsers .svgf-glass itself must stay transparent
     or its own background would sit under the filter children and swamp the
     backdrop they sample. */
  .svgf-glass { position: relative; width: ${width}px; height: ${height}px;
    border-radius: ${r}px; overflow: hidden; }
  @supports not (backdrop-filter: blur(1px)) {
    .svgf-glass { background: rgb(22 26 44 / 92%); }    /* worst case */
  }
  .svgf-glass-frost { position: absolute; inset: 0; pointer-events: none; }
  @supports (backdrop-filter: blur(1px)) {
    .svgf-glass-frost {
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      backdrop-filter: blur(14px) saturate(160%);
    }
  }
  /* Painted AFTER frost. In Chromium this layer's filter chain must
     reproduce the whole look (displace -> blur -> saturate) because it
     paints OVER the frost layer, occluding it. In Safari/Firefox this
     backdrop-filter is unsupported and the layer paints nothing, leaving
     .svgf-glass-frost visible underneath.
     NEVER nest this layer inside a filtered ancestor — it must stay a
     sibling of .svgf-glass-frost, or the refraction goes invisible. */
  .svgf-glass-refract { position: absolute; inset: 0; pointer-events: none;
    -webkit-backdrop-filter: url(#${filterId});
    backdrop-filter: url(#${filterId}); }
  .svgf-glass-tint { position: absolute; inset: 0; pointer-events: none;
    background: rgb(22 26 44 / 40%); }             /* translucent fill, above both filter layers */
  .svgf-glass::after { content: ""; position: absolute; inset: 0; border-radius: inherit;
    pointer-events: none; z-index: 1;
    box-shadow: inset 0 1px 0 rgb(255 255 255 / 42%),
                inset 0 -1px 0 rgb(255 255 255 / 8%),
                inset 1px 0 0 rgb(255 255 255 / 16%); } /* specular rim */
  .svgf-glass-content { position: relative; z-index: 2; }
  @media (prefers-reduced-transparency: reduce) {
    .svgf-glass { background: rgb(22 26 44 / 97%); }
    .svgf-glass-frost, .svgf-glass-refract, .svgf-glass-tint { display: none; }
  }
</style>
<!-- usage (sibling layers — NEVER nest .svgf-glass-refract inside a filtered ancestor):
<div class="svgf-glass">
  <div class="svgf-glass-frost" aria-hidden="true"></div>
  <div class="svgf-glass-refract" aria-hidden="true"></div>
  <div class="svgf-glass-tint" aria-hidden="true"></div>
  <div class="svgf-glass-content">…</div>
</div>
Regenerate for any width/height differing by >20%. -->`;
}

// ---- CLI --------------------------------------------------------------

function main() {
  const { values } = parseArgs({
    options: {
      width: { type: 'string', default: '360' },
      height: { type: 'string', default: '72' },
      radius: { type: 'string', default: '36' },
      bezel: { type: 'string', default: '16' },
      strength: { type: 'string', default: '60' },
      shape: { type: 'string', default: 'pill' },
    },
  });
  const opts = {
    width: Number(values.width),
    height: Number(values.height),
    radius: Number(values.radius),
    bezel: Number(values.bezel),
    strength: Number(values.strength),
    shape: values.shape,
  };
  console.log(renderSnippet(opts));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
