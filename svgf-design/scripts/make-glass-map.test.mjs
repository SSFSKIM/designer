import { test } from 'node:test';
import assert from 'node:assert/strict';
import { generateMap, renderSnippet } from './make-glass-map.mjs';

const OPTS = { width: 360, height: 72, radius: 36, bezel: 16, strength: 60, shape: 'pill' };

function px(map, x, y) {
  const i = (y * map.mapWidth + x) * 4;
  return [map.rgba[i], map.rgba[i + 1], map.rgba[i + 2], map.rgba[i + 3]];
}

test('map is generated at 2x supersample', () => {
  const map = generateMap(OPTS);
  assert.equal(map.mapWidth, 720);
  assert.equal(map.mapHeight, 144);
});

test('optical center is neutral (128/128)', () => {
  const map = generateMap(OPTS);
  const [r, g] = px(map, 360, 72); // element center at 2x
  assert.equal(r, 128);
  assert.equal(g, 128);
});

test('every pixel is fully opaque (premultiplied-alpha rule)', () => {
  const map = generateMap(OPTS);
  for (let i = 3; i < map.rgba.length; i += 4) {
    assert.equal(map.rgba[i], 255, `alpha at byte ${i}`);
  }
});

test('bezel displacement is left-right antisymmetric', () => {
  const map = generateMap(OPTS);
  const y = 72;                       // vertical center row, 2x
  const [rl] = px(map, 8, y);         // inside left bezel
  const [rr] = px(map, map.mapWidth - 1 - 8, y); // mirrored right bezel
  assert.ok(rl !== 128, 'left bezel must displace');
  assert.equal(rl - 128, -(rr - 128)); // opposite horizontal push
});

test('strength scales displacement magnitude', () => {
  // strength is emitted as the feDisplacementMap scale attr, map unchanged
  const weak = renderSnippet({ ...OPTS, strength: 20 });
  const strong = renderSnippet({ ...OPTS, strength: 80 });
  assert.match(weak, /scale="20"/);
  assert.match(strong, /scale="80"/);
});

test('emitted PNG data-URI is a valid PNG', () => {
  const snippet = renderSnippet(OPTS);
  const b64 = snippet.match(/data:image\/png;base64,([A-Za-z0-9+/=]+)/)[1];
  const buf = Buffer.from(b64, 'base64');
  assert.deepEqual([...buf.subarray(0, 8)], [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  assert.equal(buf.subarray(12, 16).toString('latin1'), 'IHDR');
  assert.equal(buf.readUInt32BE(16), 720);  // width at 2x
  assert.equal(buf.readUInt32BE(20), 144);
});

test('filter block carries the sRGB contract attribute', () => {
  assert.match(renderSnippet(OPTS), /color-interpolation-filters="sRGB"/);
});

test('CSS gates frost by @supports blur, never @supports url', () => {
  const s = renderSnippet(OPTS);
  assert.match(s, /@supports \(backdrop-filter: blur\(1px\)\)/);
  assert.doesNotMatch(s, /@supports[^{]*backdrop-filter:\s*url/);
});

test('CSS includes reduced-transparency block', () => {
  assert.match(renderSnippet(OPTS), /prefers-reduced-transparency: reduce/);
});

test('filter id encodes the pixel size (per-breakpoint map discipline)', () => {
  assert.match(renderSnippet(OPTS), /id="svgf-glass-360-72"/);
});

test('refract chain carries its own frost (spike sibling-architecture verdict)', () => {
  const s = renderSnippet(OPTS);
  assert.match(s, /feGaussianBlur[^/]*stdDeviation="3"/);
  assert.match(s, /feColorMatrix[^/]*type="saturate"[^/]*values="1.6"/);
});

test('parent class carries no backdrop-filter (sibling layering, not nesting)', () => {
  const s = renderSnippet(OPTS);
  // the frost backdrop-filter may only appear under .svgf-glass-frost, never on .svgf-glass itself
  const parentRule = s.match(/\.svgf-glass\s*\{[^}]*\}/)[0];
  assert.doesNotMatch(parentRule, /backdrop-filter/);
});
