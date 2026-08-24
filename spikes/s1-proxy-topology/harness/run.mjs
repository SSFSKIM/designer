// S1 experiment driver. Captures one PNG per (engine, variant), then runs the
// declared comparisons and writes shots/<engine>/results.json + a combined report.
//
//   node harness/run.mjs                  # all three engines
//   node harness/run.mjs chromium webkit  # a subset

import { chromium, firefox, webkit } from 'playwright';
import { createServer } from 'node:http';
import { readFileSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, extname } from 'node:path';
import { diffROI, heatmap, load, pixel } from './diff.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const PAGES = join(ROOT, 'pages');
const SHOTS = join(ROOT, 'shots');

// Capture window: the glass band plus generous margin. Small files, full signal.
const CAP = { x: 0, y: 240, width: 660, height: 240 };
const VIEW = { width: 1000, height: 800 };

// ---------------------------------------------------------------- static server

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
function serve() {
  return new Promise((res) => {
    const s = createServer((req, r) => {
      const u = new URL(req.url, 'http://x');
      const f = join(PAGES, u.pathname === '/' ? 'bench.html' : u.pathname.slice(1));
      if (!existsSync(f)) { r.writeHead(404); r.end(); return; }
      r.writeHead(200, { 'content-type': MIME[extname(f)] || 'application/octet-stream' });
      r.end(readFileSync(f));
    });
    s.listen(0, '127.0.0.1', () => res({ server: s, port: s.address().port }));
  });
}

// ---------------------------------------------------------------------- variants

const F_BLUR = 'blur(20px) saturate(1.8)';
const F_BRIGHT = 'brightness(1.25)';

/** id -> { q: query params, dsf?, after?: async (page) => void, cap? } */
const VARIANTS = {
  // ---- Q1 sampling equivalence -------------------------------------------------
  'ref-nofilter':   { q: { mode: 'none' } },
  'inplace':        { q: { mode: 'inplace', filter: F_BLUR } },
  'proxy-pad0':     { q: { mode: 'proxy', pad: '0', filter: F_BLUR } },
  'proxy-pad8':     { q: { mode: 'proxy', pad: '8', filter: F_BLUR } },
  'proxy-pad20':    { q: { mode: 'proxy', pad: '20', filter: F_BLUR } },
  'proxy-pad40':    { q: { mode: 'proxy', pad: '40', filter: F_BLUR } },
  'proxy-pad60':    { q: { mode: 'proxy', pad: '60', filter: F_BLUR } },
  'proxy-pad120':   { q: { mode: 'proxy', pad: '120', filter: F_BLUR } },
  'proxy-padfull':  { q: { mode: 'proxy', pad: 'full', filter: F_BLUR } },
  'proxy-mask60':   { q: { mode: 'proxy', pad: '60', maskkind: 'maskimage', filter: F_BLUR } },
  'proxy-wrap60':   { q: { mode: 'proxy', pad: '60', maskkind: 'wrapclip', filter: F_BLUR } },
  'proxy-clippadded': { q: { mode: 'proxy', pad: '60', clip: 'padded', filter: F_BLUR } },
  // background variants, pad=full vs inplace
  'inplace-checker':  { q: { mode: 'inplace', bg: 'checker', filter: F_BLUR } },
  'padfull-checker':  { q: { mode: 'proxy', pad: 'full', bg: 'checker', filter: F_BLUR } },
  'pad60-checker':    { q: { mode: 'proxy', pad: '60', bg: 'checker', filter: F_BLUR } },
  'inplace-image':    { q: { mode: 'inplace', bg: 'image', filter: F_BLUR } },
  'padfull-image':    { q: { mode: 'proxy', pad: 'full', bg: 'image', filter: F_BLUR } },
  'pad60-image':      { q: { mode: 'proxy', pad: '60', bg: 'image', filter: F_BLUR } },
  'inplace-gradient': { q: { mode: 'inplace', bg: 'gradient', filter: F_BLUR } },
  'padfull-gradient': { q: { mode: 'proxy', pad: 'full', bg: 'gradient', filter: F_BLUR } },

  // ---- Q2 double filtering -----------------------------------------------------
  // contract case: two groups, non-overlapping shapes, generous padding -> boxes overlap
  'split-pad60-ab':  { q: { mode: 'proxy', groups: 'split', pad: '60', order: 'ab', filter: F_BLUR } },
  'split-pad60-ba':  { q: { mode: 'proxy', groups: 'split', pad: '60', order: 'ba', filter: F_BLUR } },
  'split-pad0-ab':   { q: { mode: 'proxy', groups: 'split', pad: '0', order: 'ab', filter: F_BLUR } },
  'single-pad60':    { q: { mode: 'proxy', groups: 'single', pad: '60', filter: F_BLUR } },
  // mechanism probe: deliberately overlapping clips, no blur -> exact arithmetic
  'mech-inplace':    { q: { mode: 'inplace', shapes: 'overlap', bg: 'flat', filter: F_BRIGHT } },
  'mech-proxy-ab':   { q: { mode: 'proxy', shapes: 'overlap', groups: 'split', pad: '0', order: 'ab', bg: 'flat', filter: F_BRIGHT } },
  'mech-proxy-ba':   { q: { mode: 'proxy', shapes: 'overlap', groups: 'split', pad: '0', order: 'ba', bg: 'flat', filter: F_BRIGHT } },
  'mech-single':     { q: { mode: 'proxy', shapes: 'overlap', groups: 'single', pad: '0', bg: 'flat', filter: F_BRIGHT } },
  'mech-none':       { q: { mode: 'none', shapes: 'overlap', bg: 'flat' } },
  // stress case: 8px group gap, pad=60 -> each box swallows the other's clip region
  'near-split-ab':   { q: { mode: 'proxy', shapes: 'near', groups: 'split', pad: '60', order: 'ab', filter: F_BLUR } },
  'near-split-ba':   { q: { mode: 'proxy', shapes: 'near', groups: 'split', pad: '60', order: 'ba', filter: F_BLUR } },
  'near-single':     { q: { mode: 'proxy', shapes: 'near', groups: 'single', pad: '60', filter: F_BLUR } },
  'near-split-pad0': { q: { mode: 'proxy', shapes: 'near', groups: 'split', pad: '0', filter: F_BLUR } },
  // same stress case with a pure-amplitude filter, so the diff is exact arithmetic
  'nearb-split-ab':  { q: { mode: 'proxy', shapes: 'near', groups: 'split', pad: '60', order: 'ab', bg: 'flat', filter: 'blur(20px) brightness(1.25)' } },
  'nearb-single':    { q: { mode: 'proxy', shapes: 'near', groups: 'single', pad: '60', bg: 'flat', filter: 'blur(20px) brightness(1.25)' } },
  'nearb-none':      { q: { mode: 'none', shapes: 'near', bg: 'flat' } },

  // ---- Q3 robustness -----------------------------------------------------------
  'scroll-inplace':  { q: { mode: 'inplace', filter: F_BLUR }, scroll: 400 },
  'scroll-padfull':  { q: { mode: 'proxy', pad: 'full', filter: F_BLUR }, scroll: 400 },
  'scroll-pad60':    { q: { mode: 'proxy', pad: '60', filter: F_BLUR }, scroll: 400 },
  'fixed-inplace':   { q: { mode: 'inplace', fixed: 'on', filter: F_BLUR } },
  'fixed-padfull':   { q: { mode: 'proxy', pad: 'full', fixed: 'on', filter: F_BLUR } },
  'fixed-scroll-inplace': { q: { mode: 'inplace', fixed: 'on', filter: F_BLUR }, scroll: 400 },
  'fixed-scroll-padfull': { q: { mode: 'proxy', pad: 'full', fixed: 'on', filter: F_BLUR }, scroll: 400 },
  'zoom2-inplace':   { q: { mode: 'inplace', filter: F_BLUR }, dsf: 2 },
  'zoom2-padfull':   { q: { mode: 'proxy', pad: 'full', filter: F_BLUR }, dsf: 2 },
  'zoom2-pad60':     { q: { mode: 'proxy', pad: '60', filter: F_BLUR }, dsf: 2 },
  // pad sweep at dsf=2: pad=full lost its filter entirely in the first run, so
  // locate the proxy-box size at which the engine stops applying the filter.
  'zoom2-pad120':    { q: { mode: 'proxy', pad: '120', filter: F_BLUR }, dsf: 2 },
  'zoom2-pad200':    { q: { mode: 'proxy', pad: '200', filter: F_BLUR }, dsf: 2 },
  'zoom2-pad300':    { q: { mode: 'proxy', pad: '300', filter: F_BLUR }, dsf: 2 },
  'zoom2-nofilter':  { q: { mode: 'none' }, dsf: 2 },
  'zoom3-padfull':   { q: { mode: 'proxy', pad: 'full', filter: F_BLUR }, dsf: 3 },
  'zoom3-pad60':     { q: { mode: 'proxy', pad: '60', filter: F_BLUR }, dsf: 3 },
  'zoom3-nofilter':  { q: { mode: 'none' }, dsf: 3 },
  // fixed-position in-place reference: the fair comparison under scroll
  'ipf':             { q: { mode: 'inplacefixed', filter: F_BLUR } },
  'ipf-scroll':      { q: { mode: 'inplacefixed', filter: F_BLUR }, scroll: 400 },
  'ipf-fixed-scroll':{ q: { mode: 'inplacefixed', fixed: 'on', filter: F_BLUR }, scroll: 400 },
  'scr-pad60':       { q: { mode: 'proxy', pad: '60', scroller: 'on', filter: F_BLUR } },
  'scr-pad0':        { q: { mode: 'proxy', pad: '0', scroller: 'on', filter: F_BLUR } },
  'scr-nofilter':    { q: { mode: 'none', scroller: 'on' } },
  'ipf-scroller':    { q: { mode: 'inplacefixed', scroller: 'on', filter: F_BLUR } },
  'ipf-scroller-300':{ q: { mode: 'inplacefixed', scroller: 'on', filter: F_BLUR }, innerScroll: 300 },
  'cssz-inplace':    { q: { mode: 'inplace', filter: F_BLUR }, cssZoom: 1.5 },
  'cssz-padfull':    { q: { mode: 'proxy', pad: 'full', filter: F_BLUR }, cssZoom: 1.5 },
  'xf-content-inplace': { q: { mode: 'inplace', xform: 'content', filter: F_BLUR } },
  'xf-content-padfull': { q: { mode: 'proxy', pad: 'full', xform: 'content', filter: F_BLUR } },
  'xf-common-inplace':  { q: { mode: 'inplace', xform: 'common', filter: F_BLUR } },
  'xf-common-padfull':  { q: { mode: 'proxy', pad: 'full', xform: 'common', filter: F_BLUR } },
  'scr-inplace':     { q: { mode: 'inplace', scroller: 'on', filter: F_BLUR } },
  'scr-padfull':     { q: { mode: 'proxy', pad: 'full', scroller: 'on', filter: F_BLUR } },
  'scr-scrolled-inplace': { q: { mode: 'inplace', scroller: 'on', filter: F_BLUR }, innerScroll: 300 },
  'scr-scrolled-padfull': { q: { mode: 'proxy', pad: 'full', scroller: 'on', filter: F_BLUR }, innerScroll: 300 },

  // ---- Q4 canvas interaction ----------------------------------------------------
  'canvas-off-padfull': { q: { mode: 'proxy', pad: 'full', tint: '0', filter: F_BLUR } },
  'canvas-on-padfull':  { q: { mode: 'proxy', pad: 'full', tint: '0.28', hi: '0.35', filter: F_BLUR } },
  // Same tint over an unfiltered backdrop: isolates "did the proxy see the canvas?"
  'canvas-on-nofilter': { q: { mode: 'none', tint: '0.28', hi: '0.35' } },
  'canvas-off-nofilter':{ q: { mode: 'none', tint: '0', hi: '0' } },
  'text-on-padfull':    { q: { mode: 'proxy', pad: 'full', tint: '0.28', text: 'on', filter: F_BLUR } },
  // overlay plane above the base plane's canvases
  'overlay-base-only':  { q: { mode: 'proxy', pad: 'full', tint: '0.28', filter: F_BLUR } },
  'overlay-on':         { q: { mode: 'proxy', pad: 'full', tint: '0.28', overlay: 'on', filter: F_BLUR } },
  'overlay-on-notint':  { q: { mode: 'proxy', pad: 'full', tint: '0', overlay: 'on', filter: F_BLUR } },
};

// ---- Q1s padding sweeps at three blur radii ------------------------------------
// CSS `blur(<length>)` takes the Gaussian standard deviation directly, so if the
// convergence point is a fixed multiple of sigma it must scale with the length.
// One radius cannot tell a real rule from a coincidence.
const SIGMAS = [8, 20, 40];
for (const s of SIGMAS) {
  const f = `blur(${s}px) saturate(1.8)`;
  VARIANTS[`s${s}-padfull`] = { q: { mode: 'proxy', pad: 'full', filter: f } };
  VARIANTS[`s${s}-inplace`] = { q: { mode: 'inplace', filter: f } };
  for (const m of [0, 0.5, 1, 1.5, 2, 2.5, 3, 4]) {
    VARIANTS[`s${s}-pad${m}x`] = { q: { mode: 'proxy', pad: String(Math.round(s * m)), filter: f } };
  }
}

// ---- Q5 backdrop-root ground truth: one style on GlassRoot per variant ----------
const BREAKERS = [
  'none', 'opacity099', 'filterNone', 'filterBlur0', 'filterGrayscale0',
  'maskLinear', 'clipPathInset', 'containPaint', 'isolationIsolate',
  'mixBlend', 'willChangeOpacity', 'willChangeTransform', 'transform3d',
];
for (const b of BREAKERS) {
  VARIANTS['break-' + b] = { q: { mode: 'proxy', pad: 'full', break: b, filter: F_BLUR } };
}

// ---------------------------------------------------------------------- ROIs

// capture-local coords: subtract CAP.y from page y.
const S = (s) => ({ x: s.x, y: s.y - CAP.y, w: s.w, h: s.h });
const A = S({ x: 100, y: 300, w: 200, h: 120 });
const B = S({ x: 340, y: 300, w: 200, h: 120 });
const inset = (r, n) => ({ x: r.x + n, y: r.y + n, w: r.w - 2 * n, h: r.h - 2 * n });

const ROIS = {
  A_all: A,
  A_interior: inset(A, 26),
  A_edge: { ...A, exclude: [inset(A, 26)] },
  B_all: B,
  B_interior: inset(B, 26),
  B_edge: { ...B, exclude: [inset(B, 26)] },
  GAP: { x: 300, y: 60, w: 40, h: 120 },
  OUTSIDE_LEFT: { x: 40, y: 60, w: 56, h: 120 },
  OUTSIDE_ABOVE: { x: 100, y: 6, w: 440, h: 50 },
  B_LEFT_BAND: { x: 340, y: 60, w: 60, h: 120 },
  A_RIGHT_BAND: { x: 240, y: 60, w: 60, h: 120 },
  FULL: { x: 0, y: 0, w: CAP.width, h: CAP.height },
};
// near-gap geometry: A = 100..300, B = 308..508, gap 8px.
// *_inner = the 60px band of each shape nearest the gap, i.e. exactly where a
// sibling's already-filtered pixels would leak in.
const NA = S({ x: 100, y: 300, w: 200, h: 120 });
const NB = S({ x: 308, y: 300, w: 200, h: 120 });
Object.assign(ROIS, {
  NA_interior: inset(NA, 26),
  NB_interior: inset(NB, 26),
  NA_inner: { x: 240, y: 66, w: 54, h: 108 },
  NB_inner: { x: 314, y: 66, w: 54, h: 108 },
  NGAP: { x: 300, y: 60, w: 8, h: 120 },
});
// overlap-shape ROIs for the mechanism probe
const OV = { x: 260, y: 60, w: 80, h: 120 };            // A∩B
const A_ONLY = { x: 120, y: 60, w: 120, h: 120 };
const B_ONLY = { x: 380, y: 60, w: 100, h: 120 };

// ------------------------------------------------------------------- comparisons

const R = ['A_interior', 'A_edge', 'B_interior', 'B_edge', 'GAP', 'OUTSIDE_LEFT', 'OUTSIDE_ABOVE'];

const COMPARES = [
  // Q1: is the portaled masked proxy equivalent to in-place?
  { name: 'Q1 inplace vs proxy pad=0',    a: 'inplace', b: 'proxy-pad0',   rois: R },
  { name: 'Q1 inplace vs proxy pad=8',    a: 'inplace', b: 'proxy-pad8',   rois: R },
  { name: 'Q1 inplace vs proxy pad=20',   a: 'inplace', b: 'proxy-pad20',  rois: R },
  { name: 'Q1 inplace vs proxy pad=40',   a: 'inplace', b: 'proxy-pad40',  rois: R },
  { name: 'Q1 inplace vs proxy pad=60',   a: 'inplace', b: 'proxy-pad60',  rois: R },
  { name: 'Q1 inplace vs proxy pad=120',  a: 'inplace', b: 'proxy-pad120', rois: R },
  { name: 'Q1 inplace vs proxy pad=full', a: 'inplace', b: 'proxy-padfull',rois: R, heat: true },
  // convergence of padding toward the unclamped reference
  { name: 'Q1c pad=full vs pad=0',   a: 'proxy-padfull', b: 'proxy-pad0',   rois: R },
  { name: 'Q1c pad=full vs pad=8',   a: 'proxy-padfull', b: 'proxy-pad8',   rois: R },
  { name: 'Q1c pad=full vs pad=20',  a: 'proxy-padfull', b: 'proxy-pad20',  rois: R },
  { name: 'Q1c pad=full vs pad=40',  a: 'proxy-padfull', b: 'proxy-pad40',  rois: R },
  { name: 'Q1c pad=full vs pad=60',  a: 'proxy-padfull', b: 'proxy-pad60',  rois: R, heat: true },
  { name: 'Q1c pad=full vs pad=120', a: 'proxy-padfull', b: 'proxy-pad120', rois: R },
  // mask mechanism equivalence
  { name: 'Q1m clip-path vs mask-image (pad60)', a: 'proxy-pad60', b: 'proxy-mask60', rois: R },
  { name: 'Q1m clip-path vs overflow-wrap (pad60)', a: 'proxy-pad60', b: 'proxy-wrap60', rois: ['A_interior','A_edge','GAP'] },
  { name: 'Q1m clip=shapes vs clip=padded (halo)', a: 'proxy-pad60', b: 'proxy-clippadded', rois: ['GAP','OUTSIDE_LEFT','A_interior'] },
  // background dependence
  { name: 'Q1b checker: inplace vs pad=full', a: 'inplace-checker', b: 'padfull-checker', rois: R, heat: true },
  { name: 'Q1b checker: pad=full vs pad=60',  a: 'padfull-checker', b: 'pad60-checker',   rois: R },
  { name: 'Q1b image: inplace vs pad=full',   a: 'inplace-image',   b: 'padfull-image',   rois: R, heat: true },
  { name: 'Q1b image: pad=full vs pad=60',    a: 'padfull-image',   b: 'pad60-image',     rois: R },
  { name: 'Q1b gradient: inplace vs pad=full',a: 'inplace-gradient',b: 'padfull-gradient',rois: R },

  // Q2 double filtering
  { name: 'Q2 split pad=60 (AB) vs single group', a: 'single-pad60', b: 'split-pad60-ab', rois: ['A_interior','A_edge','B_interior','B_edge','B_LEFT_BAND','A_RIGHT_BAND','GAP'], heat: true },
  { name: 'Q2 split pad=60 (BA) vs single group', a: 'single-pad60', b: 'split-pad60-ba', rois: ['A_interior','A_edge','B_interior','B_edge','B_LEFT_BAND','A_RIGHT_BAND','GAP'] },
  { name: 'Q2 paint order AB vs BA',              a: 'split-pad60-ab', b: 'split-pad60-ba', rois: ['A_interior','B_interior','B_LEFT_BAND','A_RIGHT_BAND','GAP'], heat: true },
  { name: 'Q2 split pad=0 vs single group',       a: 'single-pad60', b: 'split-pad0-ab', rois: ['A_interior','B_interior','GAP'] },
  // 8px-gap stress: the geometry where sibling chaining, if real, must show up
  { name: 'Q2s near-gap split(AB) vs single group', a: 'near-single', b: 'near-split-ab', rois: ['NA_interior','NA_inner','NB_interior','NB_inner','NGAP'], heat: true },
  { name: 'Q2s near-gap split(BA) vs single group', a: 'near-single', b: 'near-split-ba', rois: ['NA_interior','NA_inner','NB_interior','NB_inner','NGAP'] },
  { name: 'Q2s near-gap order AB vs BA',            a: 'near-split-ab', b: 'near-split-ba', rois: ['NA_inner','NB_inner','NGAP'], heat: true },
  { name: 'Q2s near-gap split pad=0 vs single',     a: 'near-single', b: 'near-split-pad0', rois: ['NA_interior','NB_interior'] },
  { name: 'Q2s near-gap brightness split vs single',a: 'nearb-single', b: 'nearb-split-ab', rois: ['NA_inner','NB_inner','NGAP'], heat: true },

  // Q3 robustness (proxy must equal in-place under each stress)
  { name: 'Q3 scroll=400: inplace vs pad=full',   a: 'scroll-inplace', b: 'scroll-padfull', rois: R, heat: true },
  { name: 'Q3 scroll=400: inplace vs pad=60',     a: 'scroll-inplace', b: 'scroll-pad60',   rois: R },
  { name: 'Q3 fixed behind: inplace vs pad=full', a: 'fixed-inplace',  b: 'fixed-padfull',  rois: R, heat: true },
  { name: 'Q3 fixed+scroll: inplace vs pad=full', a: 'fixed-scroll-inplace', b: 'fixed-scroll-padfull', rois: R, heat: true },
  { name: 'Q3 dsf=2: inplace vs pad=60',          a: 'zoom2-inplace',  b: 'zoom2-pad60',    rois: R, dsf: 2, heat: true },
  { name: 'Q3 dsf=2: inplace vs pad=full',        a: 'zoom2-inplace',  b: 'zoom2-padfull',  rois: R, dsf: 2, heat: true },
  { name: 'Q3 dsf=2: pad=full vs pad=60',         a: 'zoom2-padfull',  b: 'zoom2-pad60',    rois: R, dsf: 2 },
  // "= 0 vs nofilter" means the filter was silently dropped at that proxy size
  { name: 'Q3d dsf=2 pad=60   vs unfiltered',     a: 'zoom2-nofilter', b: 'zoom2-pad60',    rois: ['A_interior'], dsf: 2 },
  { name: 'Q3d dsf=2 pad=120  vs unfiltered',     a: 'zoom2-nofilter', b: 'zoom2-pad120',   rois: ['A_interior'], dsf: 2 },
  { name: 'Q3d dsf=2 pad=200  vs unfiltered',     a: 'zoom2-nofilter', b: 'zoom2-pad200',   rois: ['A_interior'], dsf: 2 },
  { name: 'Q3d dsf=2 pad=300  vs unfiltered',     a: 'zoom2-nofilter', b: 'zoom2-pad300',   rois: ['A_interior'], dsf: 2 },
  { name: 'Q3d dsf=2 pad=full vs unfiltered',     a: 'zoom2-nofilter', b: 'zoom2-padfull',  rois: ['A_interior'], dsf: 2 },
  { name: 'Q3d dsf=1 pad=full vs unfiltered',     a: 'ref-nofilter',   b: 'proxy-padfull',  rois: ['A_interior'] },
  { name: 'Q3d dsf=3 pad=60   vs unfiltered',     a: 'zoom3-nofilter', b: 'zoom3-pad60',    rois: ['A_interior'], dsf: 3 },
  { name: 'Q3d dsf=3 pad=full vs unfiltered',     a: 'zoom3-nofilter', b: 'zoom3-padfull',  rois: ['A_interior'], dsf: 3 },
  // fair scroll comparisons: fixed in-place host vs fixed-plane proxy
  { name: 'Q3f fixed-host vs proxy pad=60 (no scroll)', a: 'ipf', b: 'proxy-pad60', rois: R },
  { name: 'Q3f scroll=400: fixed-host vs proxy pad=60', a: 'ipf-scroll', b: 'scroll-pad60', rois: R, heat: true },
  { name: 'Q3f fixed-content+scroll: fixed-host vs proxy', a: 'ipf-fixed-scroll', b: 'fixed-scroll-padfull', rois: R, heat: true },
  { name: 'Q3f scroll container: fixed-host vs proxy',  a: 'ipf-scroller', b: 'scr-padfull', rois: R, heat: true },
  { name: 'Q3f inner scroll 300: fixed-host vs proxy',  a: 'ipf-scroller-300', b: 'scr-scrolled-padfull', rois: R, heat: true },
  // isolate the scroll-container delta: proxy-vs-proxy first, then host-vs-host
  { name: 'Q3s scroller: proxy pad=full vs pad=60', a: 'scr-padfull', b: 'scr-pad60', rois: R },
  { name: 'Q3s scroller: proxy pad=full vs pad=0',  a: 'scr-padfull', b: 'scr-pad0',  rois: R, heat: true },
  { name: 'Q3s scroller: static host vs fixed host',a: 'scr-inplace', b: 'ipf-scroller', rois: R },
  { name: 'Q3s scroller: proxy pad=full vs unfiltered', a: 'scr-nofilter', b: 'scr-padfull', rois: ['A_interior'] },
  // overlay: does the overlay proxy pick up the BASE plane's tint canvas?
  { name: 'Q4o overlay with base tint vs without base tint', a: 'overlay-on', b: 'overlay-on-notint', rois: ['A_interior','GAP'], heat: true },
  { name: 'Q3 css zoom 1.5: inplace vs pad=full', a: 'cssz-inplace',   b: 'cssz-padfull',   rois: ['FULL'], heat: true },
  { name: 'Q3 xform on content ancestor: inplace vs pad=full', a: 'xf-content-inplace', b: 'xf-content-padfull', rois: R, heat: true },
  { name: 'Q3 xform on content ancestor: vs untransformed proxy', a: 'proxy-padfull', b: 'xf-content-padfull', rois: R },
  { name: 'Q3 xform on common ancestor: inplace vs pad=full',  a: 'xf-common-inplace',  b: 'xf-common-padfull',  rois: R, heat: true },
  { name: 'Q3 xform on common ancestor: vs untransformed proxy', a: 'proxy-padfull', b: 'xf-common-padfull', rois: R },
  { name: 'Q3 scroll container: inplace vs pad=full', a: 'scr-inplace', b: 'scr-padfull', rois: R, heat: true },
  { name: 'Q3 inner scroll 300: inplace vs pad=full', a: 'scr-scrolled-inplace', b: 'scr-scrolled-padfull', rois: R, heat: true },
  { name: 'Q3 inner scroll moved the backdrop at all', a: 'scr-padfull', b: 'scr-scrolled-padfull', rois: ['A_interior','B_interior'] },

  // Q4 canvas interaction
  { name: 'Q4 tint canvas on vs off (proxy)',   a: 'canvas-off-padfull', b: 'canvas-on-padfull', rois: ['A_interior','GAP','OUTSIDE_LEFT'], heat: true },
  { name: 'Q4 overlay plane: base only vs +overlay', a: 'overlay-base-only', b: 'overlay-on', rois: ['A_interior','A_edge','GAP'], heat: true },
];

// Q1s: distance from the un-starved reference, as a multiple of sigma.
for (const s of SIGMAS) {
  for (const m of [0, 0.5, 1, 1.5, 2, 2.5, 3, 4]) {
    COMPARES.push({
      name: `Q1s blur(${s}px) pad=${m}sigma vs pad=full`,
      a: `s${s}-padfull`, b: `s${s}-pad${m}x`,
      rois: ['A_interior', 'A_edge', 'B_edge'],
    });
  }
  COMPARES.push({
    name: `Q1s blur(${s}px) in-place vs pad=full`,
    a: `s${s}-inplace`, b: `s${s}-padfull`,
    rois: ['A_interior', 'A_edge', 'B_edge'],
  });
}

// Q5: for each candidate style on GlassRoot, is the glass still filtered?
//   vs break-none   -> 0 means the style is harmless
//   vs ref-nofilter -> 0 means the backdrop was re-rooted and the filter saw nothing
for (const b of BREAKERS) {
  COMPARES.push({ name: `Q5 break=${b} vs break=none`, a: 'break-none', b: 'break-' + b, rois: ['A_interior', 'A_edge'] });
  COMPARES.push({ name: `Q5 break=${b} vs unfiltered`, a: 'ref-nofilter', b: 'break-' + b, rois: ['A_interior'] });
}

// Q4's real question is arithmetic, not a diff: does the proxy's blurred output
// change when a semi-transparent canvas is painted ABOVE it? Composite the tint
// over the un-tinted proxy numerically and compare to the measured tinted proxy.
const PIXEL_PROBES = [
  { variant: 'mech-none',      at: [[300, 60 + 60], [180, 120], [430, 120]] },
  { variant: 'mech-inplace',   at: [[300, 120], [180, 120], [430, 120]] },
  { variant: 'mech-proxy-ab',  at: [[300, 120], [180, 120], [430, 120]] },
  { variant: 'mech-proxy-ba',  at: [[300, 120], [180, 120], [430, 120]] },
  { variant: 'mech-single',    at: [[300, 120], [180, 120], [430, 120]] },
  { variant: 'canvas-off-padfull', at: [[200, 120], [450, 120]] },
  { variant: 'canvas-on-padfull',  at: [[200, 120], [450, 120]] },
  { variant: 'canvas-off-nofilter',at: [[200, 120], [450, 120]] },
  { variant: 'canvas-on-nofilter', at: [[200, 120], [450, 120]] },
  { variant: 'overlay-on',     at: [[300, 120], [200, 120]] },
  { variant: 'overlay-base-only', at: [[300, 120], [200, 120]] },
];

// ------------------------------------------------------------------------- runner

function urlFor(port, v) {
  const q = new URLSearchParams(v.q).toString();
  return `http://127.0.0.1:${port}/bench.html?${q}`;
}

async function capture(browser, port, id, v, dir) {
  const dsf = v.dsf || 1;
  const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: dsf });
  const page = await ctx.newPage();
  await page.goto(urlFor(port, v), { waitUntil: 'load' });
  await page.waitForSelector('html[data-s1-ready="1"]');
  if (v.cssZoom) await page.evaluate((z) => { document.documentElement.style.zoom = String(z); }, v.cssZoom);
  if (v.innerScroll) {
    await page.evaluate((n) => { document.getElementById('scroller').scrollTop = n; }, v.innerScroll);
  }
  if (v.scroll) await page.evaluate((n) => window.scrollTo(0, n), v.scroll);
  // Let the compositor settle: two rAFs plus a short idle beat.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.waitForTimeout(220);
  const out = join(dir, id + '.png');
  await page.screenshot({ path: out, clip: { ...CAP, ...(v.dsf ? {} : {}) }, animations: 'disabled' });
  await ctx.close();
  return out;
}

// rAF cadence during a programmatic scroll — a weak but real compositing signal.
async function scrollCadence(browser, port) {
  const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(urlFor(port, { q: { mode: 'proxy', pad: '60', tint: '0.28', hi: '0.35', filter: F_BLUR } }));
  await page.waitForSelector('html[data-s1-ready="1"]');
  const res = await page.evaluate(async () => {
    const run = () => new Promise((done) => {
      const dt = []; let last = performance.now(); let y = 0; let n = 0;
      const step = (t) => {
        dt.push(t - last); last = t; y += 8; window.scrollTo(0, y);
        if (++n < 90) requestAnimationFrame(step); else done(dt.slice(2));
      };
      requestAnimationFrame(step);
    });
    const withGlass = await run();
    document.getElementById('glass-root').style.display = 'none';
    window.scrollTo(0, 0);
    const without = await run();
    const stat = (a) => {
      const s = [...a].sort((x, y) => x - y);
      return { mean: +(a.reduce((p, c) => p + c, 0) / a.length).toFixed(2),
               p50: +s[(s.length * 0.5) | 0].toFixed(2),
               p95: +s[(s.length * 0.95) | 0].toFixed(2),
               max: +Math.max(...a).toFixed(2),
               over20: a.filter((x) => x > 20).length, n: a.length };
    };
    return { withGlass: stat(withGlass), withoutGlass: stat(without) };
  });
  await ctx.close();
  return res;
}

async function runProbe(browser, port) {
  const ctx = await browser.newContext({ viewport: VIEW });
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/probe.html`);
  await page.waitForSelector('html[data-probe-ready="1"]', { timeout: 20000 });
  const out = await page.evaluate(() => window.__probeResult);
  await ctx.close();
  return out;
}

// NOTE: playwright's firefox and webkit builds render backdrop-filter as a NO-OP
// in every capture path tested (see harness/engine-check.mjs and the findings
// doc). Their rows here are kept only to document that; do not read pixel
// conclusions for those engines out of this harness.
const ENGINES = {
  chromium: () => chromium.launch(),
  chrome: () => chromium.launch({ channel: 'chrome' }),
  firefox: () => firefox.launch(),
  webkit: () => webkit.launch(),
};

async function main() {
  const want = process.argv.slice(2).filter((a) => ENGINES[a]);
  const names = want.length ? want : Object.keys(ENGINES);
  const { server, port } = await serve();
  const report = {};

  for (const name of names) {
    const dir = join(SHOTS, name);
    mkdirSync(dir, { recursive: true });
    const browser = await ENGINES[name]();
    const version = browser.version();
    console.log(`\n=== ${name} ${version} ===`);

    for (const [id, v] of Object.entries(VARIANTS)) {
      try {
        await capture(browser, port, id, v, dir);
        process.stdout.write('.');
      } catch (e) {
        process.stdout.write('!');
        console.error(`\n  capture ${id}: ${e.message}`);
      }
    }
    console.log('');

    const cache = new Map();
    const get = (id) => {
      if (!cache.has(id)) cache.set(id, load(join(dir, id + '.png')));
      return cache.get(id);
    };

    const comparisons = [];
    for (const c of COMPARES) {
      try {
        const a = get(c.a), b = get(c.b);
        const dsf = c.dsf || 1;
        const rois = {};
        for (const r of c.rois) rois[r] = diffROI(a, b, ROIS[r], dsf);
        let heat = null;
        if (c.heat) {
          heat = `heat/${c.a}__vs__${c.b}.png`;
          mkdirSync(join(dir, 'heat'), { recursive: true });
          heatmap(a, b, join(dir, heat));
        }
        comparisons.push({ name: c.name, a: c.a, b: c.b, rois, heat });
      } catch (e) {
        comparisons.push({ name: c.name, a: c.a, b: c.b, error: e.message });
      }
    }

    // mechanism-probe pixel readings
    const pixels = {};
    for (const pr of PIXEL_PROBES) {
      try {
        const png = get(pr.variant);
        pixels[pr.variant] = pr.at.map(([x, y]) => ({ at: [x, y], rgb: pixel(png, x, y, 1) }));
      } catch (e) { pixels[pr.variant] = { error: e.message }; }
    }
    // overlap-region readings for the mechanism probe
    for (const id of ['mech-none', 'mech-inplace', 'mech-proxy-ab', 'mech-proxy-ba', 'mech-single']) {
      try {
        const png = get(id);
        pixels[id + ':regions'] = {
          A_only: pixel(png, A_ONLY.x + 40, A_ONLY.y + 60),
          overlap: pixel(png, OV.x + 40, OV.y + 60),
          B_only: pixel(png, B_ONLY.x + 40, B_ONLY.y + 60),
        };
      } catch { /* ignore */ }
    }

    let cadence = null, probe = null;
    try { cadence = await scrollCadence(browser, port); } catch (e) { cadence = { error: e.message }; }
    try { probe = await runProbe(browser, port); } catch (e) { probe = { error: e.message }; }

    await browser.close();
    report[name] = { version, comparisons, pixels, cadence, probe };
    writeFileSync(join(dir, 'results.json'), JSON.stringify(report[name], null, 2));
  }

  server.close();
  writeFileSync(join(SHOTS, 'report.json'), JSON.stringify(report, null, 2));
  console.log('\nwrote', join(SHOTS, 'report.json'));
}

main().catch((e) => { console.error(e); process.exit(1); });
