/**
 * W27e G0 — the foreground composite probe's page.
 *
 * Two questions, one page.
 *
 * **Which buffer does a blended label see?** Every probe below is a flat slab of
 * ink inside the shipped plane sandwich, built through the same public façade
 * the e2e suite uses (`platform-web/e2e/fixtures/harness.ts`), so what is under
 * test is the real DOM and not a mock of it. The instrument is a PAIR of blend
 * identities over the same spot, because either one alone is degenerate against
 * a near-white material:
 *
 *   - white under `multiply` renders `M = (1 − αb) + αb·Cb`
 *   - black under `plus-lighter` renders `P = αb·Cb`, the premultiplied backdrop
 *
 * so `αb = 1 + P − M` and `Cb = P / αb`. The pair therefore reports the blend
 * backdrop's COLOUR AND ITS ALPHA in code values, rather than a verdict. A blend
 * group that is empty reads `αb = 0`; one holding the drawn material reads the
 * material's own composite; one holding the raw page reads the page's hard
 * checkerboard, which the page ground is a checkerboard to make unmistakable.
 *
 * Each mount point gets its OWN page load. The first run mixed them and learnt
 * why: a blending element mounted inside the glass root collapses the material
 * for every group in it, so a mixed capture would have answered a question
 * about blending with a picture of broken glass.
 *
 * **Does `feColorMatrix` reproduce the CAColorMatrix arithmetic?** The bench at
 * the bottom is flat swatches on flat grounds, no glass and no blending, so the
 * only thing between the authored colour and the read pixel is the filter.
 */

import "../../../../platform-web/e2e/fixtures/harness.ts";

/** Rec.709 luma, the decomposition the layer dumps fit exactly. */
const LUMA = [0.2126, 0.7152, 0.0722];

/**
 * `out = b + a·Y(c) + m·(c − Y(c))` as a 4×5 CAColorMatrix / feColorMatrix.
 * The alpha row is identity, as both dumps have it.
 */
function vibrancyMatrix(b, a, m) {
  const row = (index) =>
    LUMA.map((l, i) => (i === index ? a * l + m * (1 - l) : a * l - m * l)).concat([0, b]);
  return [...row(0), ...row(1), ...row(2), 0, 0, 0, 1, 0];
}

export const OPERATORS = {
  default: { b: 0.9, a: 0.1, m: 1.5 },
  "dark-glass": { b: 0.15, a: 1.35, m: 3.0 },
};

const HOST = { left: 120, top: 100, width: 560, height: 300 };
const SIZE = 60;

/** Where a pair goes when it is meant to sit over the drawn material. */
const ON_GLASS = { x: 160, y: 130 };
/** Where a pair goes when it is meant to sit over bare page. */
const OFF_GLASS = { x: 760, y: 130 };
/** Material with nothing over it: the collapse detector. */
const BARE_BAND = { x: 430, y: 300, width: 230, height: 80 };
/** Page with no glass over it: the raw-checkerboard reference. */
const PAGE_ONLY = { x: 900, y: 130, width: 60, height: 60 };

/** The pair, and the third probe that reads the material through the operator. */
const PAIR = [
  { suffix: "white-multiply", color: "#ffffff", blend: "multiply", dy: 0 },
  { suffix: "black-pluslighter", color: "#000000", blend: "plus-lighter", dy: 80 },
  { suffix: "ctrl-white-plain", color: "#ffffff", dy: 160 },
];

/**
 * The label set, all of it inside the host element — the shape W27e G2 would
 * actually ship. `slab` is the control that keeps the rest honest: an ordinary
 * opaque sibling appended FIRST at the same auto z-index, so it is unarguably
 * painted below and inside whatever group the host establishes. A blend probe
 * that reads the slab but not the material proves the group works and the
 * material is what is missing from it.
 */
const LABEL_SLAB = { left: 30, top: 180, width: 300, height: 60, color: "#0080ff" };
const LABEL_PATCHES = [
  { id: "label-white-multiply", color: "#ffffff", blend: "multiply", left: 30, top: 20 },
  { id: "label-black-pluslighter", color: "#000000", blend: "plus-lighter", left: 120, top: 20 },
  { id: "label-black-vib-plain", color: "#000000", filter: "url(#vib-default)", left: 210, top: 20 },
  {
    id: "label-black-vib-multiply",
    color: "#000000",
    filter: "url(#vib-default)",
    blend: "multiply",
    left: 300,
    top: 20,
  },
  { id: "slab-white-multiply", color: "#ffffff", blend: "multiply", left: 50, top: 190 },
  { id: "slab-grey-multiply", color: "#808080", blend: "multiply", left: 140, top: 190 },
  {
    id: "slab-black-vib-multiply",
    color: "#000000",
    filter: "url(#vib-default)",
    blend: "multiply",
    left: 230,
    top: 190,
  },
];

function buildDefs() {
  const svg = document.getElementById("defs");
  const ns = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(ns, "defs");
  for (const [name, { b, a, m }] of Object.entries(OPERATORS)) {
    const filter = document.createElementNS(ns, "filter");
    filter.setAttribute("id", `vib-${name}`);
    // sRGB, not the SVG default linearRGB: the CAColorMatrix the dumps carry is
    // arithmetic on the layer's encoded channels, and linearRGB would be a
    // different operator wearing the same twenty numbers.
    filter.setAttribute("color-interpolation-filters", "sRGB");
    filter.setAttribute("x", "-20%");
    filter.setAttribute("y", "-20%");
    filter.setAttribute("width", "140%");
    filter.setAttribute("height", "140%");
    const node = document.createElementNS(ns, "feColorMatrix");
    node.setAttribute("type", "matrix");
    node.setAttribute("values", vibrancyMatrix(b, a, m).join(" "));
    filter.append(node);
    defs.append(filter);
  }
  svg.append(defs);
}

/** The flat bench: colour × operator × ground, with nothing else in the way. */
const BENCH_COLORS = [
  { id: "black", css: "#000000" },
  { id: "white", css: "#ffffff" },
  { id: "grey50", css: "#808080" },
  { id: "red", css: "#ff3b30" },
  { id: "blue", css: "#0a84ff" },
  { id: "black-a50", css: "rgba(0, 0, 0, 0.5)" },
  { id: "white-a50", css: "rgba(255, 255, 255, 0.5)" },
];
const BENCH_VARIANTS = [
  { id: "plain", filter: "none" },
  { id: "default", filter: "url(#vib-default)" },
  { id: "dark-glass", filter: "url(#vib-dark-glass)" },
  // Whether Chromium honours an SVG filter reference in `backdrop-filter` at
  // all — the alternative mechanism the wave has to rule in or out.
  { id: "backdrop-default", backdropFilter: "url(#vib-default)" },
];
const BENCH_GROUNDS = [
  { id: "on-black", css: "#000000", left: 0 },
  { id: "on-white", css: "#ffffff", left: 500 },
];

const benchRegions = [];

function buildBench() {
  const bench = document.getElementById("matrix-bench");
  for (const ground of BENCH_GROUNDS) {
    const element = document.createElement("div");
    element.className = "ground";
    element.style.left = `${ground.left}px`;
    element.style.width = "500px";
    element.style.background = ground.css;
    bench.append(element);
    BENCH_VARIANTS.forEach((variant, row) => {
      BENCH_COLORS.forEach((color, column) => {
        const swatch = document.createElement("div");
        swatch.className = "swatch";
        const left = 20 + column * 60;
        const top = 15 + row * 55;
        swatch.style.left = `${left}px`;
        swatch.style.top = `${top}px`;
        swatch.style.background = color.css;
        if (variant.filter !== undefined) swatch.style.filter = variant.filter;
        if (variant.backdropFilter !== undefined) {
          swatch.style.backdropFilter = variant.backdropFilter;
          swatch.style.webkitBackdropFilter = variant.backdropFilter;
          // A backdrop-filter needs something to filter and nothing of its own
          // in the way, so this variant's swatch carries no background.
          swatch.style.background = "transparent";
        }
        element.append(swatch);
        benchRegions.push({
          id: `${ground.id}__${variant.id}__${color.id}`,
          kind: "bench",
          ground: ground.id,
          variant: variant.id,
          color: color.id,
          authored: color.css,
          // Page coordinates, inset so no anti-aliased edge is sampled.
          x: ground.left + left + 8,
          y: 520 + top + 8,
          width: 24,
          height: 24,
        });
      });
    });
  }
}

let host;
let mounted = new Map();

/** The rungs of the ancestor chain a probe can be mounted on. */
function mountPoint(mount) {
  const glassRoot = window.h.requireRoot();
  switch (mount) {
    case "host":
      return host;
    case "host-layer":
      return glassRoot.plane("base").hostLayer;
    case "plane-root":
      return glassRoot.plane("base").root;
    case "glass-root":
      return glassRoot.layers.root;
    default:
      return document.body;
  }
}

const probe = {
  operators: OPERATORS,
  matrices: Object.fromEntries(
    Object.entries(OPERATORS).map(([name, { b, a, m }]) => [name, vibrancyMatrix(b, a, m)]),
  ),

  /** Build a root, one group, one surface. `sampling` picks the backend. */
  async glass({ renderer = "css", sampling = "dom" } = {}) {
    await window.h.createRoot({ renderer });
    if (sampling === "texture") {
      window.h.addTextureGroup({ groupId: "g", sourceId: "src", fill: "#1040c0" });
    } else {
      window.h.addGroup("g");
    }
    window.h.addSurface({
      groupId: "g",
      nodeId: "n",
      left: HOST.left,
      top: HOST.top,
      width: HOST.width,
      height: HOST.height,
      radius: 28,
      label: "",
    });
    host = window.h.requireRoot().plane("base").hostLayer.lastElementChild;
    // NOT `host.textContent = ""`: the CSS tier's three material layers are the
    // host's own children and clearing text deletes them. The surface is built
    // label-less instead.
    await probe.settle();
    return probe.state();
  },

  /**
   * Frames paced by real rAF, not a loop.
   *
   * The GPU tier's backdrop adaptation converges over frames and its collection
   * is asynchronous, so a synchronous burst of `runFrame` calls settles the
   * bookkeeping and not the picture — and a baseline and a probe capture taken
   * at different points on that curve would differ for a reason that has
   * nothing to do with blending.
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

  /**
   * One blend pair at one rung. `over` says whether it sits on the glass or on
   * bare page; the rung says which group it lands in. Position is written in
   * PAGE coordinates and read back from the live box, so a host border or a
   * containing block never silently shifts a read region off its probe.
   */
  async mountPair(mount, over = "glass") {
    const parent = mountPoint(mount);
    const origin = over === "glass" ? ON_GLASS : OFF_GLASS;
    const box = parent.getBoundingClientRect();
    for (const spec of PAIR) {
      const element = document.createElement("div");
      element.className = "patch";
      const id = `${mount}--${spec.suffix}`;
      element.dataset.patch = id;
      element.style.left = `${origin.x - box.left}px`;
      element.style.top = `${origin.y + spec.dy - box.top}px`;
      element.style.width = `${SIZE}px`;
      element.style.height = `${SIZE}px`;
      element.style.background = spec.color;
      if (spec.blend !== undefined) element.style.mixBlendMode = spec.blend;
      parent.append(element);
      mounted.set(id, element);
    }
    await probe.settle(6);
  },

  /**
   * ONE decorated slab at one rung — the single-variable form of `mountPair`.
   *
   * Separating `filter` from `mix-blend-mode` is the whole point of it: the two
   * are different triggers with different reach (a `filter` re-roots its own
   * DESCENDANTS' backdrop, a blend forces the enclosing group to isolate), and
   * a capture carrying both cannot say which one moved the material.
   */
  async mountSolo(spec, mount = "host", over = "glass") {
    const parent = mountPoint(mount);
    const origin = over === "glass" ? ON_GLASS : OFF_GLASS;
    const box = parent.getBoundingClientRect();
    const element = document.createElement("div");
    element.className = "patch";
    element.dataset.patch = spec.id;
    element.style.left = `${origin.x - box.left}px`;
    element.style.top = `${origin.y - box.top}px`;
    element.style.width = `${SIZE}px`;
    element.style.height = `${SIZE}px`;
    if (spec.backgrounds === undefined) element.style.background = spec.color;
    else {
      // Two of the element's OWN background layers, blended against each other.
      // `background-blend-mode` composes inside the element and creates no
      // stacking context, so this is the candidate carrier that might darken
      // without asking the enclosing group to isolate.
      element.style.backgroundImage = spec.backgrounds
        .map((layer) => `linear-gradient(${layer}, ${layer})`)
        .join(", ");
      element.style.backgroundBlendMode = spec.backgroundBlend;
    }
    if (spec.blend !== undefined) element.style.mixBlendMode = spec.blend;
    if (spec.filter !== undefined) element.style.filter = spec.filter;
    parent.append(element);
    mounted.set(spec.id, element);
    await probe.settle(8);
  },

  /** Take one back off again — the reversibility half of a causal claim. */
  async unmount(id) {
    mounted.get(id)?.remove();
    mounted.delete(id);
    await probe.settle(8);
  },

  /** The full in-host label set, including the opaque-sibling control. */
  async addLabels() {
    const slab = document.createElement("div");
    slab.className = "patch";
    slab.style.left = `${LABEL_SLAB.left}px`;
    slab.style.top = `${LABEL_SLAB.top}px`;
    slab.style.width = `${LABEL_SLAB.width}px`;
    slab.style.height = `${LABEL_SLAB.height}px`;
    slab.style.background = LABEL_SLAB.color;
    host.append(slab);
    mounted.set("slab", slab);

    for (const spec of LABEL_PATCHES) {
      const element = document.createElement("div");
      element.className = "patch";
      element.dataset.patch = spec.id;
      element.style.left = `${spec.left}px`;
      element.style.top = `${spec.top}px`;
      element.style.width = `${SIZE}px`;
      element.style.height = `${SIZE}px`;
      element.style.background = spec.color;
      if (spec.blend !== undefined) element.style.mixBlendMode = spec.blend;
      if (spec.filter !== undefined) element.style.filter = spec.filter;
      host.append(element);
      mounted.set(spec.id, element);
    }
    await probe.settle(6);
  },

  /**
   * What actually drew, read off the resolved group state — X2's honesty core.
   * Never what the URL asked for.
   */
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
   * Every reading's page rect. Mounted probes report their LIVE box, inset so
   * that no anti-aliased edge is ever sampled.
   */
  regions() {
    const live = [...mounted.entries()].map(([id, element]) => {
      const box = element.getBoundingClientRect();
      const style = window.getComputedStyle(element);
      return {
        id,
        kind: "probe",
        blend: style.mixBlendMode,
        filter: style.filter,
        background: style.backgroundColor,
        x: Math.round(box.left) + 8,
        y: Math.round(box.top) + 8,
        width: Math.round(box.width) - 16,
        height: Math.round(box.height) - 16,
      };
    });
    return [
      ...live,
      { id: "bare-material", kind: "bare", ...BARE_BAND },
      { id: "page-ground", kind: "page", ...PAGE_ONLY },
      ...benchRegions,
    ];
  },

  /** One candidate backdrop-root trigger, on the host or on an ancestor. */
  async setStyle(target, property, value) {
    const element = target === "host" ? host : mountPoint(target);
    if (value === null) element.style.removeProperty(property);
    else element.style.setProperty(property, value);
    await probe.settle(8);
    return window.getComputedStyle(element).getPropertyValue(property);
  },
};

buildDefs();
buildBench();
window.probe = probe;
document.documentElement.setAttribute("data-probe-ready", "");
