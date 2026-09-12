/**
 * W27e G1 — the label operator probe's page.
 *
 * G0's composite probe answered *which buffer* a blended label composes
 * against. This one answers a narrower and later question: does the closed form
 * vitrea would evaluate for Apple's label operator agree with what Chromium
 * actually composites, and by how much do the two surviving readings of
 * `inputBackdropAware` differ where they differ.
 *
 * Two instruments, deliberately apart:
 *
 * **The bench** is flat grounds and flat swatches, no glass and no sampling, so
 * the only thing between the authored colour and the read pixel is the filter
 * and (where an arm asks for one) the blend. Every cell is its own isolated
 * group, because a blended swatch in a non-isolated cell would blend against
 * the page behind it and the reading would be of the wrong buffer.
 *
 * **The glass arm** puts the same patches inside a real host on a real
 * material, over the checkerboard page, so the material under a patch varies
 * from pixel to pixel. A patch whose ink carries no backdrop term reads flat
 * there; one whose ink carries a backdrop term reads with a standard deviation.
 * That difference is the CSS-tier fold's information loss, measured rather than
 * argued.
 *
 * Nothing here captures a native pixel and nothing writes under a fixture root.
 */

import "../../../../platform-web/e2e/fixtures/harness.ts";

/**
 * Apple's own label matrices, copied from the probe corpus to the float32 value
 * `packages/calibration/results/2026-09-11-w27e-probe/table.json` records, and
 * pinned again in `test/vibrancy.test.ts`. Four rows of five columns, row order.
 * The dark alpha coefficient is 0.95 in float32.
 */
export const LABEL_MATRICES = {
  light: [1, 0, 0, 0, -1, 0, 1, 0, 0, -1, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0],
  dark: [1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0.949999988079071, 0],
};

/**
 * The blend each scheme's arm reaches for when the operator is read as the
 * classic AppKit vibrancy composite rather than as a saturating transform.
 * `plus-darker` is the newer of the two in CSS; the run records the computed
 * value so a browser that does not support it is visible as a fallback to
 * `normal` rather than as a surprising number.
 */
export const BLEND_FOR_SCHEME = { light: "plus-darker", dark: "plus-lighter" };

/** The material composites a label sits on, bright end to dark end. */
export const GROUNDS = [
  "#ffffff", "#f7f7f7", "#dfe4ea", "#9aa3ad", "#4a4f56", "#22242a", "#000000",
];

/**
 * The inks. Apple's automatic label colour at full and at the 0.85 alpha macOS
 * documents for `labelColor`; vitrea's own two published inks at full and at
 * the nominal secondary alpha; and one chromatic ink, which is the only row
 * that can show whether the operator saturates chroma as well as level.
 */
export const INKS = [
  { id: "black-100", color: "#000000", alpha: 1 },
  { id: "black-085", color: "#000000", alpha: 0.85 },
  { id: "vitrea-dark-100", color: "#1c1c1e", alpha: 1 },
  { id: "vitrea-dark-060", color: "#1c1c1e", alpha: 0.6 },
  { id: "white-100", color: "#ffffff", alpha: 1 },
  { id: "white-085", color: "#ffffff", alpha: 0.85 },
  { id: "vitrea-light-100", color: "#f5f5f7", alpha: 1 },
  { id: "red-100", color: "#ff3b30", alpha: 1 },
];

/**
 * The four arms, per scheme.
 *
 * - `over` is the declared path: the matrix as an `feColorMatrix` at
 *   `color-interpolation-filters: sRGB`, composited source-over.
 * - `fold` is the same operator evaluated on the CPU into one sRGB colour and
 *   painted flat. On a `css-backdrop` group this is the only path available,
 *   because §5.133 §5 measured that a `mix-blend-mode` inside the host
 *   collapses the group's `backdrop-filter` sampling.
 * - `plusblend` is the alternative reading: the same filtered ink combined with
 *   the buffer beneath by the scheme's plus blend.
 * - `blendonly` is the documented AppKit vibrancy without any matrix at all,
 *   carried for scale.
 */
export const ARMS = ["over", "fold", "plusblend", "blendonly"];

const CELL = { width: 32, height: 24, gapX: 4, gapY: 4 };
const BLOCK = {
  width: GROUNDS.length * (CELL.width + CELL.gapX),
  height: INKS.length * (CELL.height + CELL.gapY),
};
const BENCH_ORIGIN = { x: 16, y: 16 };
const BLOCK_GAP = 28;

const HOST = { left: 120, top: 100, width: 560, height: 300 };

/** Material with nothing over it: G0's collapse detector, unchanged. */
const BARE_BAND = { x: 430, y: 300, width: 230, height: 80 };

const regions = [];
let host = null;
let benchVisible = false;

const hex = (value) => {
  const n = value.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255);
};

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/**
 * The operator's closed form, on non-premultiplied encoded sRGB in [0, 1].
 *
 * `feColorMatrix` and `CAColorMatrix` both operate on non-premultiplied
 * channels, which is what antialiased glyph edges need and what §5.133 §5
 * confirmed in the browser (a 50 %-alpha black under the default operator over
 * black reads 115 = round(0.9 × 0.5 × 255)). `inputClamp` = 1 is a plain [0, 1]
 * clamp on the encoded channel after the matrix.
 */
export function applyMatrix(rgba, matrix) {
  const out = [];
  for (let row = 0; row < 4; row += 1) {
    let sum = matrix[row * 5 + 4];
    for (let col = 0; col < 4; col += 1) sum += matrix[row * 5 + col] * rgba[col];
    out.push(clamp01(sum));
  }
  return out;
}

const toCss = ([r, g, b, a]) =>
  `rgb(${Math.round(r * 255)} ${Math.round(g * 255)} ${Math.round(b * 255)} / ${a})`;

function buildDefs() {
  const svg = document.getElementById("defs");
  const ns = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(ns, "defs");
  for (const [scheme, values] of Object.entries(LABEL_MATRICES)) {
    const filter = document.createElementNS(ns, "filter");
    filter.setAttribute("id", `label-${scheme}`);
    // sRGB, not the SVG default linearRGB: the CAColorMatrix the dumps carry is
    // arithmetic on the layer's encoded channels, and linearRGB would be a
    // different operator wearing the same twenty numbers (§5.133 §5).
    filter.setAttribute("color-interpolation-filters", "sRGB");
    filter.setAttribute("x", "-20%");
    filter.setAttribute("y", "-20%");
    filter.setAttribute("width", "140%");
    filter.setAttribute("height", "140%");
    const node = document.createElementNS(ns, "feColorMatrix");
    node.setAttribute("type", "matrix");
    node.setAttribute("values", values.join(" "));
    filter.append(node);
    defs.append(filter);
  }
  svg.append(defs);
}

function buildBench() {
  const bench = document.getElementById("bench");
  let blockIndex = 0;
  for (const scheme of Object.keys(LABEL_MATRICES)) {
    for (const arm of ARMS) {
      const column = blockIndex % 4;
      const row = Math.floor(blockIndex / 4);
      const originX = BENCH_ORIGIN.x + column * (BLOCK.width + BLOCK_GAP);
      const originY = BENCH_ORIGIN.y + row * (BLOCK.height + BLOCK_GAP);
      blockIndex += 1;

      GROUNDS.forEach((ground, gi) => {
        INKS.forEach((ink, ii) => {
          const cell = document.createElement("div");
          cell.className = "cell";
          cell.style.left = `${originX + gi * (CELL.width + CELL.gapX)}px`;
          cell.style.top = `${originY + ii * (CELL.height + CELL.gapY)}px`;
          cell.style.width = `${CELL.width}px`;
          cell.style.height = `${CELL.height}px`;
          cell.style.background = ground;

          const swatch = document.createElement("div");
          swatch.className = "swatch";
          const rgba = [...hex(ink.color), ink.alpha];
          const filtered = applyMatrix(rgba, LABEL_MATRICES[scheme]);
          if (arm === "fold") {
            swatch.style.background = toCss(filtered);
          } else {
            swatch.style.background = toCss(rgba);
            if (arm !== "blendonly") swatch.style.filter = `url(#label-${scheme})`;
            if (arm === "plusblend" || arm === "blendonly") {
              swatch.style.mixBlendMode = BLEND_FOR_SCHEME[scheme];
            }
          }
          cell.append(swatch);
          bench.append(cell);

          regions.push({
            id: `${scheme}--${arm}--${ink.id}--g${gi}`,
            kind: "bench",
            scheme,
            arm,
            ink: ink.id,
            inkColor: ink.color,
            inkAlpha: ink.alpha,
            ground,
            groundIndex: gi,
            filtered: filtered.map((v) => Math.round(v * 1e6) / 1e6),
            blend: swatch.style.mixBlendMode || "normal",
            computedBlend: "",
            element: cell,
          });
        });
      });
    }
  }
}

/** Resolve the computed blend of every bench swatch, after layout. */
function resolveComputedBlends() {
  for (const region of regions) {
    if (region.kind !== "bench") continue;
    const swatch = region.element.firstElementChild;
    region.computedBlend = getComputedStyle(swatch).mixBlendMode;
  }
}

/** The patches the glass arm mounts inside the host. */
function mountPatches(specs) {
  for (const spec of specs) {
    const patch = document.createElement("div");
    patch.className = "patch";
    patch.style.left = `${spec.left}px`;
    patch.style.top = `${spec.top}px`;
    patch.style.width = `${spec.width}px`;
    patch.style.height = `${spec.height}px`;
    patch.style.background = spec.background;
    if (spec.filter) patch.style.filter = spec.filter;
    if (spec.blend) patch.style.mixBlendMode = spec.blend;
    patch.dataset["probeId"] = spec.id;
    host.append(patch);
    regions.push({
      id: spec.id,
      kind: "patch",
      spec: { ...spec },
      computedBlend: getComputedStyle(patch).mixBlendMode,
      element: patch,
    });
  }
}

const api = {
  LABEL_MATRICES,
  BLEND_FOR_SCHEME,
  GROUNDS,
  INKS,
  ARMS,

  applyMatrix,

  /**
   * Whether the engine can express the alternative reading's blends at all.
   * Asked rather than assumed: a value the parser rejects computes to `normal`,
   * and a reading taken through a silently-dropped blend would look like
   * agreement between two readings that were never compared.
   */
  blendSupport() {
    return {
      "mix-blend-mode: plus-darker": CSS.supports("mix-blend-mode", "plus-darker"),
      "mix-blend-mode: plus-lighter": CSS.supports("mix-blend-mode", "plus-lighter"),
      "background-blend-mode: plus-darker": CSS.supports("background-blend-mode", "plus-darker"),
      "background-blend-mode: plus-lighter": CSS.supports("background-blend-mode", "plus-lighter"),
      "mix-blend-mode: multiply": CSS.supports("mix-blend-mode", "multiply"),
    };
  },

  /** Build a glass surface on the named tier, exactly as G0's probe does. */
  async glass({ renderer = "css", sampling = "dom" } = {}) {
    await window.h.createRoot({ renderer });
    if (sampling === "texture") {
      window.h.addTextureGroup({ groupId: "g", sourceId: "src", fill: "#1040c0" });
    } else {
      window.h.addGroup("g");
    }
    window.h.addSurface({
      groupId: "g", nodeId: "n",
      left: HOST.left, top: HOST.top, width: HOST.width, height: HOST.height,
      radius: 28, label: "",
    });
    host = window.h.requireRoot().plane("base").hostLayer.lastElementChild;
    await api.settle();
    return api.state();
  },

  /**
   * The declared path and its CPU fold, side by side on the same material. Both
   * arms are `filter`-only or flat; neither declares a blend, so neither can
   * collapse the group's sampling and the two are readable on one page.
   */
  mountDeclared(scheme) {
    const rgba = [...hex("#1c1c1e"), 1];
    const folded = applyMatrix(rgba, LABEL_MATRICES[scheme]);
    mountPatches([
      {
        id: "glass-over", left: 40, top: 40, width: 120, height: 60,
        background: toCss(rgba), filter: `url(#label-${scheme})`,
      },
      {
        id: "glass-fold", left: 200, top: 40, width: 120, height: 60,
        background: toCss(folded),
      },
    ]);
  },

  /** The alternative reading, alone on its own page for the reason G0 gives. */
  mountPlusBlend(scheme) {
    const rgba = [...hex("#1c1c1e"), 1];
    mountPatches([
      {
        id: "glass-plusblend", left: 40, top: 40, width: 120, height: 60,
        background: toCss(rgba), filter: `url(#label-${scheme})`,
        blend: BLEND_FOR_SCHEME[scheme],
      },
    ]);
  },

  /**
   * Frames paced by real rAF, G0's reasoning unchanged: the GPU tier's backdrop
   * adaptation converges over frames and its collection is asynchronous, so a
   * synchronous burst settles the bookkeeping and not the picture.
   */
  async settle(frames = 24) {
    for (let index = 0; index < frames; index += 1) {
      const time = await new Promise((done) => requestAnimationFrame(done));
      window.h.requireRoot().runFrame(time);
    }
    await new Promise((done) => setTimeout(done, 120));
    const time = await new Promise((done) => requestAnimationFrame(done));
    window.h.requireRoot().runFrame(time);
  },

  state() {
    const group = window.h.capabilities("g");
    return {
      activeRenderer: group?.activeRenderer ?? null,
      samplingBackend: group?.samplingBackend ?? null,
      demotion: group?.demotionReason ?? null,
      probe: window.h.probeVerdict("g") ?? null,
      diagnostics: window.h.diagnosticCodes(),
    };
  },

  /**
   * The bench and the glass arm never share a page. The glass root is a fixed,
   * z-indexed stacking context above everything else, so a visible bench would
   * become the material's backdrop and the glass arm would be sampling the
   * instrument instead of the checkerboard.
   */
  showBench() {
    document.getElementById("bench").style.display = "block";
    benchVisible = true;
    resolveComputedBlends();
  },

  /**
   * Live rects, inset so no antialiased edge is sampled, plus G0's bare-material
   * band when a surface is built.
   */
  regions() {
    const inset = 6;
    const out = [];
    for (const region of regions) {
      if (region.kind === "bench" && !benchVisible) continue;
      const rect = region.element.getBoundingClientRect();
      const { element: _element, ...rest } = region;
      out.push({
        ...rest,
        x: Math.round(rect.left) + inset,
        y: Math.round(rect.top) + inset,
        width: Math.max(1, Math.round(rect.width) - 2 * inset),
        height: Math.max(1, Math.round(rect.height) - 2 * inset),
      });
    }
    if (host) out.push({ id: "bare-material", kind: "bare", ...BARE_BAND });
    return out;
  },
};

buildDefs();
buildBench();
window.probe = api;
document.body.setAttribute("data-probe-ready", "");
