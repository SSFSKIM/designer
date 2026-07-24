# svgf-design Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use doperpowers:subagent-driven-development (recommended) or doperpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `svgf-design` — a material-specialist Agent Skill (engineered liquid glass, goo, grain/print, lighting) that composes with the shipped `figma-design` skill and guarantees a signature SVG-filter material moment on every invocation.

**Architecture:** Overlay skill + computed-optics script (spec Approach A). A new `svgf-design/` directory holds SKILL.md, 7 reference files, and `make-glass-map.mjs` (engineered displacement-map generator). The skill runs figma-design as its base, writes a material commitment into DESIGN.md as law, and extends QA with grep-checkable + visual material checks. Spike-first: the glass-map script's physics and the refraction-tier gating are verified visually in three engines before anything depends on them.

**Tech Stack:** Plain Markdown skill files; Node ≥ 20 with built-ins only (`node:zlib`, `node:test`); SVG filter primitives; playwright (chromium/webkit/firefox) for spike + QA screenshots.

**Spec:** `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md` — read the "Locked design decisions" section before any task; those 11 decisions bind every task here.

## Global Constraints

Copied from the spec — every task's requirements implicitly include these:

- **Signature guarantee:** every skill output contains ≥1 filter-material moment built with actual SVG filter primitives (grep: `<filter` / `filter: url(` / `backdrop-filter: url(`), never CSS `blur()` alone.
- **sRGB everywhere:** every emitted/authored `<filter>` carries `color-interpolation-filters="sRGB"`.
- **Opaque maps:** every displacement-map pixel has alpha=255.
- **Tier gating:** frost tier gated by `@supports (backdrop-filter: blur(1px))`; refraction tier is capability-gated (layered no-op overlay or runtime probe) and NEVER gated by `@supports (backdrop-filter: url())` — that gate false-positives in Firefox.
- **Accessibility blocks mandatory:** `prefers-reduced-motion` and `prefers-reduced-transparency` (near-opaque panel replacement) blocks in every glass/goo output.
- **Filter regions:** explicit tight `x/y/width/height` on every `<filter>`; never filter `body` or a full-viewport wrapper.
- **Map sizing:** signature glass chrome sized in px; per-breakpoint maps for responsive layouts; regenerate beyond ~20% stretch; maps generated at 2× target pixel size.
- **Dosage:** 1 signature surface + ≤2 supporting moments per page.
- **Bans:** no `filter: url` on body-text containers; no decorative wobble on controls; no glass over blank grounds; no glass card grids; no translucent-white-fill + 1px-white-border default card style; no perpetual ambient filter loops.
- **Dependencies:** scripts use Node built-ins only. Skill files are runtime-neutral plain files (no Claude-specific APIs).
- **Hard dependency:** SKILL.md requires figma-design installed; fails loudly, never degrades silently.
- **Register ceilings:** product UI caps at Apple-neat; campaign/brand surfaces may reach the Awwwards ceiling.
- **Commits:** commit at the end of every task (and at marked mid-task points). No attribution lines in commit messages.

## File Structure

```
svgf-design/
  SKILL.md                          # Task 10 — workflow spine + trigger frontmatter
  references/
    filter-mechanics.md             # Task 3 — atlas §0 primer
    grounds.md                      # Task 4 — three ground sources
    glass.md                        # Task 5 — flagship: tiered engineered glass
    goo.md                          # Task 6 — metaball/organic
    grain-print.md                  # Task 7 — grain, paper, duotone, halftone, ink bleed
    lighting.md                     # Task 8 — specular/diffuse
    materials-map.md                # Task 9 — stance→material map, registers, dosage, bans
  scripts/
    make-glass-map.mjs              # Task 2 — hardened from Task 1 spike
    make-glass-map.test.mjs         # Task 2
  examples/
    aurora-glass/                   # Task 11 — DESIGN.md + index.html
    aurora-goo/                     # Task 12 — DESIGN.md + index.html
docs/doperpowers/spikes/glass-spike/   # Task 1 scratch (gitignored via eval workspace pattern — see Task 1)
```

The examples brief (spec §Repo layout): **"Aurora" — a music/spatial-audio product** whose visual model genuinely earns materials; built twice (glass treatment, goo treatment).

---

### Task 1: SPIKE — engineered glass map + three-engine gating verification

**This is a spike task (spec §Risk containment). The deliverable is knowledge, not shipped code. No TDD cycle: build → run → record.**

**Question the spike answers:** (a) Does a per-pixel computed displacement map (kube.io method) read as curved-glass optics — edge bending, stable center — in Chromium? (b) Which refraction-tier gating mechanism works in all three engines: the layered no-op overlay, or a runtime probe? (c) How far can a fluid container stretch the map before the bezel visibly warps?

**Files:**
- Create: `figma-design-workspace/glass-spike/proto-glass-map.mjs` (workspace is already gitignored — spike code is disposable by design)
- Create: `figma-design-workspace/glass-spike/spike-page.html` (generated by the script)

**Interfaces:**
- Produces (knowledge, for Task 2): the verified displacement encoding (sign convention, falloff curve), the chosen gating mechanism, the stretch tolerance. Recorded in the spec's Surprises & Discoveries.

- [ ] **Step 1: Write the prototype generator**

Write `figma-design-workspace/glass-spike/proto-glass-map.mjs`:

```js
#!/usr/bin/env node
// SPIKE: engineered liquid-glass displacement map (kube.io method).
// Generates the map, wraps it in a filter stack, and writes a self-contained
// test page (rich ground + scrolling content + glass pill) for visual
// verification in Chromium / WebKit / Firefox.

import { deflateSync } from 'node:zlib';
import { writeFileSync } from 'node:fs';

// ---- geometry (CSS px) -------------------------------------------------
const W = 360, H = 72;      // element size
const SS = 2;               // supersample: map rendered at 2x (banding guard)
const RADIUS = 36;          // corner radius (= H/2 -> pill)
const BEZEL = 16;           // bezel width
const STRENGTH = 60;        // feDisplacementMap scale, user px

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
function outwardNormal(px, py) {
  const e = 0.5;
  const gx = insideDist(px + e, py, W, H, RADIUS) - insideDist(px - e, py, W, H, RADIUS);
  const gy = insideDist(px, py + e, W, H, RADIUS) - insideDist(px, py - e, W, H, RADIUS);
  const len = Math.hypot(gx, gy) || 1;
  return [-gx / len, -gy / len]; // gradient points inward; flip for outward
}

// Lens falloff over the bezel: 1 at the boundary, 0 at the inner bezel edge.
// Quarter-circle lens slope, clamped (raw slope -> Infinity at the rim).
function falloff(t) {                       // t = insideDist / BEZEL in [0,1]
  const s = (1 - t) / Math.sqrt(Math.max(1 - (1 - t) ** 2, 0.04));
  return Math.min(s / 5, 1);                // normalize: slope 5 = full strength
}

// ---- map ---------------------------------------------------------------
const mw = W * SS, mh = H * SS;
const rgba = Buffer.alloc(mw * mh * 4);
for (let y = 0; y < mh; y++) {
  for (let x = 0; x < mw; x++) {
    const px = (x + 0.5) / SS, py = (y + 0.5) / SS;
    const d = insideDist(px, py, W, H, RADIUS);
    let r = 128, g = 128;
    if (d > 0 && d < BEZEL) {
      const [nx, ny] = outwardNormal(px, py);
      const m = falloff(d / BEZEL);
      // SIGN CONVENTION UNDER TEST: sample outward at the rim (magnify).
      // If the rim reads as pinch instead of a lens, flip both signs and
      // record the flip in the spike verdict.
      r = Math.round(128 + nx * m * 127);
      g = Math.round(128 + ny * m * 127);
    }
    const i = (y * mw + x) * 4;
    rgba[i] = r; rgba[i + 1] = g; rgba[i + 2] = 128; rgba[i + 3] = 255; // opaque, B neutral
  }
}

// ---- minimal PNG encoder (8-bit RGBA, filter 0) ------------------------
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
const dataUri = `data:image/png;base64,${encodePNG(mw, mh, rgba).toString('base64')}`;

// ---- test page ---------------------------------------------------------
// Layered architecture under test:
//   .glass          frost base   (@supports blur gate — reliable everywhere)
//   .glass-refract  overlay with backdrop-filter: url() — Chromium refracts;
//                   WebKit/Firefox MUST no-op harmlessly (that is question b)
const html = `<!doctype html><meta charset="utf-8">
<title>glass spike</title>
<style>
  body { margin: 0; font: 16px/1.5 system-ui; background: #0b0e1a; }
  .ground { min-height: 240vh; padding: 40px; color: #dfe6ff;
    background:
      radial-gradient(60% 40% at 20% 10%, #ff9d5c 0%, transparent 60%),
      radial-gradient(50% 60% at 80% 30%, #4c7dff 0%, transparent 55%),
      radial-gradient(70% 50% at 50% 80%, #b04cff 0%, transparent 60%),
      repeating-linear-gradient(45deg, #141a33 0 40px, #0b0e1a 40px 80px); }
  .glass { position: fixed; left: 50%; bottom: 40px; transform: translateX(-50%);
    width: 360px; height: 72px; border-radius: 36px; overflow: hidden;
    background: rgb(22 26 44 / 92%); }             /* worst case */
  @supports (backdrop-filter: blur(1px)) {
    .glass { background: rgb(22 26 44 / 40%);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      backdrop-filter: blur(14px) saturate(160%); } /* frost tier */
  }
  .glass-refract { position: absolute; inset: 0; pointer-events: none;
    backdrop-filter: url(#glass-refract); }         /* refraction tier (Chromium) */
  .glass::after { content: ""; position: absolute; inset: 0; border-radius: inherit;
    pointer-events: none;
    box-shadow: inset 0 1px 0 rgb(255 255 255 / 42%),
                inset 0 -1px 0 rgb(255 255 255 / 8%),
                inset 1px 0 0 rgb(255 255 255 / 16%); } /* specular rim */
  .glass-label { position: relative; z-index: 1; display: grid; place-items: center;
    height: 100%; color: #fff; font-weight: 600; }
  @media (prefers-reduced-transparency: reduce) {
    .glass { background: rgb(22 26 44 / 97%); backdrop-filter: none;
      -webkit-backdrop-filter: none; }
    .glass-refract { display: none; }
  }
  .stretch { width: 80vw; }  /* toggle class for question (c) */
</style>
<svg width="0" height="0" aria-hidden="true" style="position:absolute">
  <filter id="glass-refract" x="0" y="0" width="100%" height="100%"
          color-interpolation-filters="sRGB" primitiveUnits="userSpaceOnUse">
    <feImage href="${dataUri}" x="0" y="0" width="${W}" height="${H}" result="map"/>
    <feDisplacementMap in="SourceGraphic" in2="map" scale="${STRENGTH}"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
<div class="ground">
  <h1>Spike ground</h1>
  <p>${'Scroll me under the glass. '.repeat(200)}</p>
</div>
<div class="glass"><div class="glass-refract"></div><div class="glass-label">Liquid glass</div></div>`;
writeFileSync(new URL('./spike-page.html', import.meta.url), html);
console.log('wrote spike-page.html — map', mw, 'x', mh, 'strength', STRENGTH);
```

- [ ] **Step 2: Generate and open in Chromium**

```bash
node figma-design-workspace/glass-spike/proto-glass-map.mjs
```
Expected: `wrote spike-page.html — map 720 x 144 strength 60`

Serve and screenshot with the playwright-cli skill (chromium), scrolled to mid-page so content sits under the glass. **Observe (question a):** backdrop bends at the pill's rim, center stays optically flat and legible. If the rim pinches inward instead of lensing, flip the sign convention in Step 1 (both `nx`/`ny` lines), regenerate, re-observe, and note the flip.

- [ ] **Step 3: Verify gating in WebKit and Firefox (question b)**

```bash
cd figma-design-workspace/glass-spike
npx -y playwright@1.54 install webkit firefox
npx -y playwright@1.54 screenshot --browser=webkit  --viewport-size=1280,900 spike-page.html webkit.png
npx -y playwright@1.54 screenshot --browser=firefox --viewport-size=1280,900 spike-page.html firefox.png
```

**Observe:** in both screenshots the glass must show the frost tier (blurred, saturated, legible) and the `.glass-refract` overlay must change nothing — no blanked backdrop, no transparent hole, no broken paint. That is the "harmless no-op" the spec's locked decision 6 requires. If the overlay damages rendering in either engine, test the fallback candidate: gate the overlay behind a one-time JS probe (create a 2×2 test element with `backdrop-filter: url(#glass-refract)` over a known-color fixed div inside a same-origin iframe rendered to canvas via `drawWindow`-free approach — if that proves impractical in the spike timebox, the acceptable v1 probe is `CSS.supports('backdrop-filter','url(#x)') === true && !/firefox|safari/i.test(navigator.userAgent)`, documented as UA-based with the layered overlay as preferred). Record which mechanism won.

- [ ] **Step 4: Measure stretch tolerance (question c)**

In Chromium devtools (or by editing the HTML), add class `stretch` to `.glass` (80vw ≈ 2.8× stretch at 1280px) and then try intermediate widths (400px ≈ 11%, 430px ≈ 19%, 470px ≈ 30%). **Observe:** at which stretch the bezel visibly warps (bezel band widens asymmetrically / corner refraction smears). Record the observed tolerance vs the spec's ~20% working bound.

- [ ] **Step 5: Record the verdict and apply promote-or-discard**

Spec criteria verbatim: *"if per-pixel computed optics can't be made to read as glass, the discard fallback is the atlas §2.1 static gradient-ramp map (two overlapping linear/radial gradients encoding red-horizontal/green-vertical ramps, flat-128 center) — still computed edge-only optics with a stable center, never turbulence wobble. A discard triggers a revision of acceptance #4's wording and a note here."*

Append to the spec's `## Surprises & Discoveries`: the sign convention that won, the falloff normalization used, the gating mechanism that won (overlay vs probe, with the two atlas `[uncertain]` flags now resolved: Firefox's `@supports (backdrop-filter: url())` result, no-op overlay behavior), the measured stretch tolerance, and the promote/discard verdict. **Promote →** Task 2 hardens this code. **Discard →** Task 2 builds the gradient-ramp generator instead (same CLI, same output contract; the map-generation loop is replaced by two-gradient composition) and acceptance #4's wording is revised in the spec.

```bash
git add docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md
git commit -m "docs: record glass-spike verdict in spec"
```

---

### Task 2: `make-glass-map.mjs` — hardened generator + test suite

**Files:**
- Create: `svgf-design/scripts/make-glass-map.mjs`
- Test: `svgf-design/scripts/make-glass-map.test.mjs`

**Interfaces:**
- Consumes: Task 1's verdict (sign convention, falloff, gating mechanism).
- Produces (used verbatim by Tasks 5, 11, and the eval): CLI
  `node svgf-design/scripts/make-glass-map.mjs --width 360 --height 72 --radius 36 --bezel 16 --strength 60 --shape pill`
  printing a single self-contained snippet to stdout containing, in order: (1) the `<svg><filter id="svgf-glass-W-H">…` block with `feImage` data-URI map + `feDisplacementMap`, (2) the paired CSS for both tiers (`.svgf-glass` frost base with `@supports (backdrop-filter: blur(1px))`, `.svgf-glass-refract` overlay, specular rim `::after`, `prefers-reduced-transparency` block), (3) an HTML usage comment showing the three-element structure. Also exports (for tests) `generateMap({width,height,radius,bezel,strength,shape})` returning `{ rgba: Buffer, mapWidth, mapHeight }` and `renderSnippet(opts)` returning the full string. `--shape` accepts `pill | squircle | rect` (squircle = rounded-rect SDF with radius; rect = radius 4).

- [ ] **Step 1: Write the failing tests**

Write `svgf-design/scripts/make-glass-map.test.mjs`:

```js
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test svgf-design/scripts/`
Expected: FAIL — `Cannot find module ... make-glass-map.mjs`

- [ ] **Step 3: Implement**

Write `svgf-design/scripts/make-glass-map.mjs`: port the Task-1 prototype with these changes and nothing more —

1. Wrap geometry in `generateMap(opts)` and page-emission in `renderSnippet(opts)`; apply the sign convention and falloff normalization the spike verdict recorded.
2. `--shape`: `pill` forces `radius = height/2`; `squircle` uses the given radius; `rect` uses radius 4. All three share the rounded-rect SDF.
3. Emit the snippet contract from **Interfaces** exactly: filter id `svgf-glass-<width>-<height>`; class names `.svgf-glass`, `.svgf-glass-refract`; specular rim on `.svgf-glass::after` (the three inset box-shadows from the spike page); the gating mechanism the spike promoted; `prefers-reduced-transparency` block; trailing HTML usage comment:
   ```html
   <!-- usage:
   <div class="svgf-glass"><div class="svgf-glass-refract" aria-hidden="true"></div>
     <div class="svgf-glass-content">…</div></div>
   Regenerate for any width/height differing by >20%. -->
   ```
4. CLI: parse `--width --height --radius --bezel --strength --shape` with `node:util` `parseArgs`; defaults `360 72 36 16 60 pill`; print `renderSnippet` to stdout; `import.meta.url` main-module guard so tests can import without side effects.

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test svgf-design/scripts/`
Expected: 10 pass / 0 fail. Also run the existing figma-design suite to confirm no interference: `node --test scripts/` → 5 pass.

- [ ] **Step 5: Visual re-verification**

Regenerate a snippet, splice it into a copy of the Task-1 spike page (replace the hand-built filter + CSS), screenshot in Chromium via playwright-cli. Expected: identical optics to the promoted spike render.

- [ ] **Step 6: Commit**

```bash
git add svgf-design/scripts/
git commit -m "feat(svgf): add engineered glass displacement-map generator"
```

---

### Task 3: `references/filter-mechanics.md`

**Files:**
- Create: `svgf-design/references/filter-mechanics.md`

**Interfaces:**
- Produces: the primer every other reference links to as `filter-mechanics.md` instead of repeating. Section anchors other files rely on: `## The pipeline`, `## The filter region`, `## The sRGB rule`, `## Premultiplied alpha`, `## What a filter does to the element`.

- [ ] **Step 1: Write the file**

Distill atlas §0 (`docs/research/svg-filter-atlas.md` lines 9–64) into ~120 lines under the five section anchors above. Must-carry values (verbatim facts, not pointers):
- Default region `x="-10%" y="-10%" width="120%" height="120%"` hard-clips big blurs/displacement; fix by enlarging or `filterUnits="userSpaceOnUse"`; zero-area bbox elements vanish with objectBoundingBox regions.
- `in` defaulting rules (first primitive → SourceGraphic; later → previous result); legacy `BackgroundImage` keywords are dead — `backdrop-filter` replaced them.
- The sRGB rule as a command: `color-interpolation-filters="sRGB"` on every filter, with the one-sentence why (linearRGB default makes authored 128-neutral maps drift; engines disagree).
- Opaque maps rule: transparent map pixels displace undefinedly (premultiplied alpha).
- Applying a filter creates a stacking context and makes the element a containing block for fixed/absolute descendants; flattens preserve-3d; dangling `url(#missing)` on SVG elements renders nothing.
- Close with the performance floor (atlas §4.2 rules 1, 3, 5): prefer CSS shorthands when equivalent; tight explicit regions, never filter `<body>`; displacement maps rebuild on resize only.

- [ ] **Step 2: Verify required content**

```bash
grep -c 'color-interpolation-filters="sRGB"' svgf-design/references/filter-mechanics.md  # ≥1
grep -c 'userSpaceOnUse' svgf-design/references/filter-mechanics.md                       # ≥1
grep -ci 'premultiplied' svgf-design/references/filter-mechanics.md                       # ≥1
grep -c '## ' svgf-design/references/filter-mechanics.md                                  # ≥5
```

- [ ] **Step 3: Commit**

```bash
git add svgf-design/references/filter-mechanics.md
git commit -m "docs(svgf): add filter-mechanics primer"
```

---

### Task 4: `references/grounds.md`

**Files:**
- Create: `svgf-design/references/grounds.md`

**Interfaces:**
- Produces: three ground-source sections that `glass.md` and SKILL.md's material commitment reference by name: `## Authored SVG/gradient grounds`, `## Real photography`, `## Simulated product content`.

- [ ] **Step 1: Write the file**

~150 lines. Opening law: *glass over a blank or flat-gray ground is banned; the ground plan is part of the DESIGN.md material commitment.* Per section:
- **Authored** (the guaranteed self-contained baseline): layered radial/linear gradient fields with ≥3 hue stops and structural geometry (repeating-linear-gradient bands, large SVG shapes) so refraction has edges to bend — include one complete copy-adapt CSS block (adapt the Task-1 spike ground) and the rule that a pure two-stop vertical gradient is still "blank" for refraction purposes (nothing to bend).
- **Real photography** (when environment allows): pick images with depth-of-field layers, high local contrast, and diagonal structure; state the Unsplash source-URL pattern used by the vs-Make eval arms; require a dominant-hue token extracted into `:root` so glass tint harmonizes.
- **Simulated product content** (truest to Apple's model): the ground IS the product — map tiles, video frame, waveform canvas, chart field — mocked with realistic content per figma-design's realistic-content discipline; one worked sketch: a spatial-audio waveform field as layered SVG paths.
- Close: ground choice by register — product UI prefers simulated content; campaign/brand prefers authored art or photography.

- [ ] **Step 2: Verify + commit**

```bash
grep -c '^## ' svgf-design/references/grounds.md   # = 3 (+ intro heading if h1 = 1 → total 4 '#' lines)
git add svgf-design/references/grounds.md
git commit -m "docs(svgf): add grounds reference (three sources)"
```

---

### Task 5: `references/glass.md` — the flagship

**Files:**
- Create: `svgf-design/references/glass.md`

**Interfaces:**
- Consumes: Task 2's CLI + snippet contract (quote the exact command and the three-element usage structure); Task 1's promoted gating mechanism; `filter-mechanics.md` anchors; `grounds.md` section names.
- Produces: the glass chapter SKILL.md's build step points to; the ban table rows `materials-map.md` (Task 9) copies for glass.

- [ ] **Step 1: Write the file**

~250 lines, sections in order:
1. **What engineered glass is** — computed refraction at the bezel, optically flat center, specular rim; north stars named (Apple Liquid Glass, kube.io); explicitly contrasted with 2021 glassmorphism (flat blur + translucent white fill + 1px white border, on every card, over gray).
2. **The tier system** — worst-case opaque base → `@supports (backdrop-filter: blur(1px))` frost tier → capability-gated refraction tier (the spike's winning mechanism, with the Firefox `@supports url()` false-positive warning verbatim); both tiers share geometry/tokens; `prefers-reduced-transparency` → near-opaque replacement (Apple's own behavior); `prefers-contrast: more` → solid.
3. **Generating the optics** — the exact Task-2 CLI invocation, what each flag does, the `svgf-glass-<w>-<h>` id convention, the three-element HTML structure, and the sizing law: signature chrome sized in px; per-breakpoint maps; regenerate beyond ~20% stretch (insert the spike's measured tolerance).
4. **Where glass may live** — floating chrome (toolbars, tab bars, sheets, palettes, command palettes) over rich grounds per `grounds.md`; the ban list: no blank grounds, no glass card grids, no glass-as-default-card, frost alone only as fallback tier or quiet supporting surface.
5. **Legibility contract** — text contrast provided by a scrim/tint layer, never by the blur; focus rings unaffected; hit targets undistorted (refraction overlay is `pointer-events: none`, `aria-hidden`).
6. **Motion** — refraction is alive via content scrolling beneath (free); interaction morphs = class toggles between precomputed states or animating the cheap `scale` attribute only; no ambient loops; `prefers-reduced-motion` freezes any animated attribute.
7. **Worked example** — one complete floating-toolbar block (HTML + generated snippet spliced) over an authored ground, annotated line-by-line with which rule each part satisfies.

- [ ] **Step 2: Verify required content**

```bash
grep -c 'make-glass-map.mjs' svgf-design/references/glass.md            # ≥2
grep -c 'prefers-reduced-transparency' svgf-design/references/glass.md  # ≥1
grep -ci 'never.*@supports.*url\|@supports.*url.*false' svgf-design/references/glass.md  # ≥1
grep -c 'pointer-events: none' svgf-design/references/glass.md          # ≥1
```

- [ ] **Step 3: Commit**

```bash
git add svgf-design/references/glass.md
git commit -m "docs(svgf): add engineered-glass flagship reference"
```

---

### Task 6: `references/goo.md`

**Files:**
- Create: `svgf-design/references/goo.md`

**Interfaces:**
- Consumes: `filter-mechanics.md` anchors.
- Produces: the goo chapter; ban rows for Task 9.

- [ ] **Step 1: Write the file**

~180 lines, from atlas §2.2 (lines 274–298):
1. **The mechanism** — blur → alpha contrast (`feColorMatrix` alpha row, e.g. `0 0 0 22 -9`) → composite source atop; `color-interpolation-filters="sRGB"` mandatory; enlarged filter region (blur eats the default 10% padding).
2. **Registers** — playful/organic/creative stances; Awwwards ceiling applies on campaign/brand surfaces only; product UI never gets goo on controls (locked decision 4).
3. **Dosage** — goo is a delight-moment material: one merge animation, one loading motif, one hero identity — on the ≤2-supporting-moments budget unless it IS the signature.
4. **Motion** — merges/morphs on interaction only (class toggle between two blob layouts, transform-animated circles under a static goo filter — transforms animate cheap, the filter itself never re-parametrizes per frame); `prefers-reduced-motion` shows the merged end state.
5. **Two complete recipes** — (a) static organic cluster (SVG circles + goo filter) for a hero identity; (b) interaction merge (two circles translating together on `:hover`/`[data-active]` via CSS transform under the same filter). Full code both.
6. **Bans** — goo never on interactive controls or text; no goo as section-divider default; state changes shown by goo must also exist as text/ARIA (atlas §4.3).

- [ ] **Step 2: Verify + commit**

```bash
grep -c 'sRGB' svgf-design/references/goo.md               # ≥2
grep -ci 'prefers-reduced-motion' svgf-design/references/goo.md  # ≥1
git add svgf-design/references/goo.md
git commit -m "docs(svgf): add goo/organic reference"
```

---

### Task 7: `references/grain-print.md`

**Files:**
- Create: `svgf-design/references/grain-print.md`

**Interfaces:**
- Consumes: `filter-mechanics.md`; the existing conservative grain recipe in `references/effects-policy.md` (figma-design's — extended, not contradicted).
- Produces: the grain-print chapter; ban rows for Task 9.

- [ ] **Step 1: Write the file**

~200 lines, from atlas §2.3 + §2.9:
1. **Grain** — baked-tile static `feTurbulence` (`type="fractalNoise"`, `baseFrequency 0.6–0.9`, `stitchTiles="stitch"`, fixed `seed`), opacity 0.025–0.08, page/section-scoped never per-card, never animated; data-URI tile pattern (the effects-policy recipe, referenced as the base) plus the atlas's richer variants: luminosity-only grain via `feColorMatrix` saturate 0, and colored paper fields.
2. **Duotone as print technique** — `feColorMatrix`/`feComponentTransfer` two-ink mapping with explicit ink hex pairs (the P2 film-festival arm's riso look is the in-repo precedent: marine + flare-orange); duotone as standalone color-grade art direction is v2 — state the boundary.
3. **Halftone** — the atlas §2.9 dot-screen chain (feFlood/feImage 8×8 cell/feTile/saturate-0/arithmetic/discrete) with the Chromium-safest caveat; use on imagery/illustration, never body text.
4. **Ink bleed / edge roughening** — `feTurbulence` + low-scale `feDisplacementMap` on display type ONLY as designed letterform treatment for print stances, radius ≤2px equivalent (scale ≤4), never on body text (the ban), plus `feMorphology`-based rough outlines.
5. **Registers** — editorial/craft/archival/riso stances; pairs with authored paper grounds from `grounds.md`.
6. **Two complete recipes** — (a) full-page paper ground (tile + tint + vignette); (b) duotone photo treatment with ink-pair tokens in `:root`.

- [ ] **Step 2: Verify + commit**

```bash
grep -c 'stitchTiles' svgf-design/references/grain-print.md   # ≥1
grep -ci 'never.*body text' svgf-design/references/grain-print.md  # ≥1
git add svgf-design/references/grain-print.md
git commit -m "docs(svgf): add grain/print reference"
```

---

### Task 8: `references/lighting.md`

**Files:**
- Create: `svgf-design/references/lighting.md`

**Interfaces:**
- Consumes: `filter-mechanics.md`; `glass.md`'s specular rim (CSS-based) to contrast with.
- Produces: the lighting chapter; ban rows for Task 9.

- [ ] **Step 1: Write the file**

~150 lines, from atlas §1.16 + §2.5:
1. **Role** — lighting mostly SERVES glass (the rim highlight); standalone `feSpecularLighting`/`feDiffuseLighting` reserved for badges, seals, one-off material studies, non-interactive hero materials (locked decision 7).
2. **The two paths to a highlight** — CSS inset-shadow specular (what `glass.md` ships — cheap, controllable, cross-engine) vs true `feSpecularLighting` over `SourceAlpha` blur (physically richer; linearRGB-vs-sRGB divergence warning: Safari computes sRGB regardless, accept divergence or stay CSS). When to use which: chrome → CSS; artwork → primitives.
3. **Complete recipes** — (a) embossed seal/badge (the atlas soft-specular chain: SourceAlpha blur → feSpecularLighting surfaceScale 3, specularConstant 0.45, exponent 18, feDistantLight azimuth 225 elevation 50 → composite in → arithmetic merge k3≈0.34); (b) wet/lit hero material with `fePointLight` and an interaction-positioned light (CSS custom property → `x`/`y` attribute swap on hover, no per-frame animation).
4. **Bans** — never on buttons, cards, inputs, navigation chrome; light direction consistent with the page's shadow system (one sun).

- [ ] **Step 2: Verify + commit**

```bash
grep -c 'feSpecularLighting' svgf-design/references/lighting.md  # ≥2
grep -ci 'never.*button' svgf-design/references/lighting.md      # ≥1
git add svgf-design/references/lighting.md
git commit -m "docs(svgf): add lighting reference"
```

---

### Task 9: `references/materials-map.md`

**Files:**
- Create: `svgf-design/references/materials-map.md`

**Interfaces:**
- Consumes: the 18 stance names from `scripts/ingredients.json` (figma-design repo root — read it; do not invent names); ban rows from Tasks 5–8.
- Produces: the routing table SKILL.md's material-commitment step executes; section anchors: `## Register classifier`, `## Stance → material map`, `## Dosage`, `## Ban table`.

- [ ] **Step 1: Write the file**

~220 lines:
1. **Register classifier** (this file DEFINES it — the spec notes figma-design has no named register mechanism): product UI = the deliverable is an interface people operate (dashboards, booking flows, tools, stores' transactional surfaces) → ceiling Apple-neat: engineered glass, quiet grain, CSS specular, no goo on any interactive surface. Campaign/brand = the deliverable's design IS the message (landing/campaign pages, event sites, editorial features, hero-led marketing) → ceiling Awwwards-expressive: goo signatures, halftone imagery, lit hero materials allowed. Mixed pages classify per-surface (a store's hero may be campaign; its checkout is product UI).
2. **Stance → material map** — a table with one row per figma-design stance (all 18, names verbatim from `ingredients.json`), columns: stance, default family, signature-surface suggestion, families explicitly OFF for that stance. Neutral-brief rule stated above the table: no stance/brief material signal → refined-tech home register (engineered glass + simulated-content or authored ground).
3. **Dosage** — 1 signature + ≤2 supporting moments; the signature carries the invocation guarantee; supporting moments must be quieter than the signature (locked decision 3's one-loud-moment rule).
4. **Ban table** — consolidated, one row per ban with its check type (grep vs visual), copied from Tasks 5–8 plus the glass ban line (no blank grounds, no card grids, no white-border default combo) and the global bans (no `filter: url` on body-text containers, no ambient loops, no filter on body/full-viewport).

- [ ] **Step 2: Verify**

```bash
node -e "const i=require('./scripts/ingredients.json'); console.log(i.stances.length, i.stances.map(s=>s.name).join(','))"  # 18, names for the table rows
grep -c '^| ' svgf-design/references/materials-map.md   # ≥ 20 (18 stance rows + headers)
grep -c '## Register classifier' svgf-design/references/materials-map.md  # 1
```

- [ ] **Step 3: Commit**

```bash
git add svgf-design/references/materials-map.md
git commit -m "docs(svgf): add stance-material map, register classifier, ban table"
```

---

### Task 10: `SKILL.md` + install

**Files:**
- Create: `svgf-design/SKILL.md`
- Create (symlink): `~/.claude/skills/svgf-design → /Users/new/Documents/GitHub/SVGF-Design/svgf-design`

**Interfaces:**
- Consumes: every reference by relative path; Task 2's CLI; figma-design as installed sibling skill.
- Produces: the invocable skill.

- [ ] **Step 1: Write SKILL.md**

~1,200–1,800 words. Frontmatter description built from the spec's §Trigger vocabulary verbatim — positive families (glass: liquid glass, glassy, frosted, refraction, lens, translucent chrome; goo: gooey, organic, blob, metaball, liquid/fluid shapes; grain-print: grain, paper texture, riso, halftone, duotone, ink, print texture; lighting: metallic, specular, embossed, lit material, wet; generic: premium material, texture-rich, material design system in the physical sense — not Google's Material Design) and the negative clause (plain UI-design requests without material language stay with figma-design; this skill is invoked for the material dimension).

Body — the four moves, each a numbered section:
1. **Run figma-design as the base.** Check `~/.claude/skills/figma-design/SKILL.md` exists; if missing, STOP and tell the user this skill requires figma-design installed (fail loudly — spec locked decision 1). Then execute that skill's full workflow (classify, sample, commit stance, author DESIGN.md).
2. **Material commitment** — immediately after the stance commitment, append to DESIGN.md a `## Material law` block: family (via `references/materials-map.md` — read it now; refined-tech home register when neutral), the ONE signature surface, dosage (1 signature + ≤2 supporting), ground plan (`references/grounds.md` source), fallback-tier plan, register ceiling from the classifier. Every line phrased as checkable law.
3. **Build** — open the family reference (`references/glass.md` / `goo.md` / `grain-print.md` / `lighting.md`; mechanics questions → `references/filter-mechanics.md`). For glass: generate optics with `node <skill-dir>/scripts/make-glass-map.mjs --width … --height …`, never hand-write displacement filters.
4. **Material QA** — after figma-design's QA, run both halves against the Material law verbatim from the spec: grep-checkable (signature present: `<filter`/`filter: url(`/`backdrop-filter: url(`; frost `@supports (backdrop-filter: blur(1px))` present; NO `@supports (backdrop-filter: url` anywhere; `prefers-reduced-motion` + `prefers-reduced-transparency` present; explicit region attrs on every `<filter`; no filter on body/full-viewport wrapper; no `filter: url` on body-text containers) and visual browser QA (no blank ground under glass, no glass card grid, controls undistorted, text-on-glass contrast via scrim). Fix violations before delivery — the law is the page's own DESIGN.md.

- [ ] **Step 2: Install and smoke-test**

```bash
ln -sfn /Users/new/Documents/GitHub/SVGF-Design/svgf-design ~/.claude/skills/svgf-design
ls -la ~/.claude/skills/svgf-design/SKILL.md   # resolves
head -20 ~/.claude/skills/svgf-design/SKILL.md # frontmatter renders
node --test svgf-design/scripts/               # still 10 pass
```

- [ ] **Step 3: Commit**

```bash
git add svgf-design/SKILL.md
git commit -m "feat(svgf): add SKILL.md workflow spine and install skill"
```

---

### Task 11: Example — Aurora, glass treatment

**Files:**
- Create: `svgf-design/examples/aurora-glass/DESIGN.md`
- Create: `svgf-design/examples/aurora-glass/index.html`

**Interfaces:**
- Consumes: the installed skill (Task 10) — this task IS a run of the skill, executed by the implementer following SKILL.md end-to-end.
- Produces: the canonical glass exemplar `glass.md` readers see referenced from SKILL.md's examples note (Task 12 mirrors it).

**Brief (verbatim, use as the user prompt):** *"Design the web experience for Aurora, a spatial-audio listening room app. The main surface is the listening room: an immersive visual field that responds to what's playing. Users browse rooms, join a room, and control playback. Desktop-first, self-contained single page."*

- [ ] **Step 1: Execute the skill workflow** — follow `svgf-design/SKILL.md` moves 1–3 exactly: figma-design base (sampler seeded, stance committed, DESIGN.md authored), Material law appended (expected: family=glass; signature=floating transport/room controls over the simulated listening-room field — a `grounds.md` simulated-product-content ground; register=product UI → Apple-neat ceiling), build with `make-glass-map.mjs`-generated optics for the transport chrome.
- [ ] **Step 2: Run Material QA** — both halves per SKILL.md move 4, in-browser via playwright-cli screenshots (top, mid-scroll with content under the glass, bottom). Fix violations against the page's own Material law.
- [ ] **Step 3: Verify the global-constraint greps pass on the artifact**

```bash
f=svgf-design/examples/aurora-glass/index.html
grep -c 'backdrop-filter: url(' $f            # ≥1 (refraction tier present)
grep -c '@supports (backdrop-filter: blur(1px))' $f  # ≥1
grep -c 'prefers-reduced-transparency' $f     # ≥1
grep -c 'prefers-reduced-motion' $f           # ≥1
grep -vc '@supports ([^)]*backdrop-filter: url' $f >/dev/null && ! grep -q '@supports ([^)]*backdrop-filter: url' $f && echo GATE-OK
```

- [ ] **Step 4: Commit**

```bash
git add svgf-design/examples/aurora-glass/
git commit -m "feat(svgf): add Aurora glass-treatment example"
```

---

### Task 12: Example — Aurora, goo treatment

**Files:**
- Create: `svgf-design/examples/aurora-goo/DESIGN.md`
- Create: `svgf-design/examples/aurora-goo/index.html`

**Interfaces:**
- Consumes: same installed skill, same brief as Task 11 — but the Material law commits to the goo/organic family (treat the brief's campaign face: Aurora's marketing/landing register, where the Awwwards ceiling applies).
- Produces: the contrast exemplar proving family choice is a decision space (spec acceptance #6).

- [ ] **Step 1: Execute the skill workflow** with the same verbatim brief, Material law committing family=goo (signature: an organic audio-reactive-looking hero identity built from a static goo cluster + one interaction merge; grounds: authored gradient field; register=campaign/brand). The DESIGN.md must record WHY goo is legitimate here (campaign register) where Task 11's product-UI register forbade it — this contrast is the point.
- [ ] **Step 2: Run Material QA** — both halves; verify goo touches no interactive control and no text (grep: the goo filter id must not appear on elements containing `<button`, `<a `, `<input`).
- [ ] **Step 3: Verify greps**

```bash
f=svgf-design/examples/aurora-goo/index.html
grep -c '<filter' $f                       # ≥1
grep -c 'sRGB' $f                          # ≥1
grep -c 'prefers-reduced-motion' $f        # ≥1
```

- [ ] **Step 4: Commit**

```bash
git add svgf-design/examples/aurora-goo/
git commit -m "feat(svgf): add Aurora goo-treatment example"
```

---

### Task 13: A/B eval — figma-design alone vs figma-design + svgf-design

**Files:**
- Create: `figma-design-workspace/svgf-eval/` (gitignored workspace): `brief-{1..4}/{base,svgf}/index.html` + screenshots + `review-grid.html`
- Create: `figma-design-workspace/svgf-eval/assert-material.sh`

**Interfaces:**
- Consumes: both installed skills; the screenshot + grid patterns proven in the prior evals (auto-scroll before fullPage screenshots; serve over http, not file://; one shared playwright-cli browser → serialize or mutex).
- Produces: the judged grid for the user (spec acceptance #7 gate).

**The four briefs (verbatim; svgf arm gets the brief + "use the svgf-design skill", base arm gets the brief + "use the figma-design skill"):**
1. *Spatial/media (home turf):* "Design the review workspace for Lightfall, a photo-culling tool for wedding photographers. The working surface is a full-bleed photo lightbox; culling controls float over it. Desktop, self-contained single page."
2. *Playful consumer (goo):* "Design the landing page for Blend, a build-your-own smoothie subscription aimed at families. Playful, fresh, fruit-forward. Self-contained single page."
3. *Editorial/craft (grain-print):* "Design the site for Petrichor Press, an independent letterpress studio selling prints and running workshops. Self-contained single page."
4. *Neutral (home-register default test):* "Design the class-booking page for Summit Works, a climbing gym. Self-contained single page." — no material language anywhere; the svgf arm must default to the refined-tech home register on its own.

- [ ] **Step 1: Run the 8 arms** — dispatch one worker per arm (same model both arms of a brief; run arms of different briefs in parallel, arms sharing the browser serialized or on fixed ports per the prior eval's mutex pattern). Each worker: the brief + skill instruction, browser QA allowed, output to `brief-N/{base,svgf}/index.html`.
- [ ] **Step 2: Mechanical assertions on the svgf arms**

Write and run `figma-design-workspace/svgf-eval/assert-material.sh`:

```bash
#!/usr/bin/env bash
# Material assertions for svgf arms (spec acceptance #3/#5 subset).
fail=0
for d in figma-design-workspace/svgf-eval/brief-*/svgf; do
  f="$d/index.html"; [ -f "$f" ] || { echo "MISS $f"; fail=1; continue; }
  ok=1
  grep -Eq '<filter|filter: url\(|backdrop-filter: url\(' "$f" || { echo "FAIL signature   $f"; ok=0; }
  grep -q  'prefers-reduced-motion' "$f"                    || { echo "FAIL red-motion  $f"; ok=0; }
  ! grep -q '@supports ([^)]*backdrop-filter: url' "$f"     || { echo "FAIL bad-gate    $f"; ok=0; }
  [ $ok -eq 1 ] && echo "PASS $f" || fail=1
done
# glass-specific (only when the arm chose glass):
for f in figma-design-workspace/svgf-eval/brief-*/svgf/index.html; do
  if grep -q 'backdrop-filter: url(' "$f"; then
    grep -q '@supports (backdrop-filter: blur(1px))' "$f" || { echo "FAIL frost-tier  $f"; fail=1; }
    grep -q 'prefers-reduced-transparency' "$f"           || { echo "FAIL red-transp  $f"; fail=1; }
  fi
done
exit $fail
```

Expected: `PASS` × 4, exit 0. Any FAIL → the arm's output violates the skill's own law; note it (that is eval data, not something to silently fix).

- [ ] **Step 3: Screenshot all 8 + build the grid** — reuse the prior eval's auto-scroll screenshot pattern and grid builder (4 rows × 2 columns: base | svgf), serve over http, hand the URL to the user.
- [ ] **Step 4: USER GATE — the user judges the grid.** Success per spec: the svgf arm visibly adds the material dimension without losing the base skill's neatness. Record the verdict + per-brief observations in the spec's `## Surprises & Discoveries`; commit the spec update.

---

### Task 14: Final verification — acceptance walk

**Files:**
- Modify: `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md` (Outcomes & Retrospective)
- Modify: `README.md` (deliverable #2 status)

- [ ] **Step 1: Full test suites**

```bash
node --test svgf-design/scripts/   # 10 pass / 0 fail
node --test scripts/               # figma-design suite still 5 pass / 0 fail
```

- [ ] **Step 2: Walk the spec's acceptance section as written** — for each of the 7 numbered criteria in "What done looks like", record PASS/FAIL with pointers:
1. *Triggering:* read `svgf-design/SKILL.md` frontmatter — description contains all four positive families + the negative clause (grep each family's head term: `liquid glass`, `gooey`, `riso`, `specular`).
2. *Composition:* both example DESIGN.md files contain a `## Material law` block after the stance commitment with family, signature surface, dosage, ground plan, fallback plan, register ceiling (grep `## Material law` in both).
3. *Signature guarantee:* `grep -El '<filter|filter: url\(|backdrop-filter: url\(' svgf-design/examples/*/index.html` → both files listed; same grep passed on all 4 eval svgf arms (Task 13 Step 2 output).
4. *Engineered glass:* `grep -c 'svgf-glass-' svgf-design/examples/aurora-glass/index.html` ≥1 (script-generated id convention, not hand-tuned turbulence: `grep -c 'feTurbulence' …/aurora-glass/index.html` must be 0 inside the glass filter); frost `@supports` + capability-gated refraction greps from Task 11 Step 3 pass.
5. *Bans hold:* Task 11–13 grep sets pass; visual QA screenshots reviewed.
6. *Range:* `ls svgf-design/examples/` → `aurora-glass aurora-goo`, same brief, two families, both with Material law.
7. *Eval complete:* Task 13 Step 4 verdict recorded in the spec.
- [ ] **Step 3: Write Outcomes & Retrospective** in the spec (acceptance walk results, headline eval verdict, deferred items: v2 families — squigglevision, standalone color-grade); update `README.md`'s deliverable-#2 paragraph from "planned" to shipped-with-pointer.
- [ ] **Step 4: Commit**

```bash
git add docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md README.md
git commit -m "docs: record svgf-design acceptance walk and outcomes"
```
