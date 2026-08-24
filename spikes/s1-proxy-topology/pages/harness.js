// S1 spike harness — throwaway. Builds the vitrea per-plane sandwich from URL params
// so that every variant is pixel-comparable: identical page content, identical final
// glass geometry, only the *location of the filter* and the mask/pad strategy differ.
//
// Params (all optional):
//   mode      = proxy | inplace | none            where backdrop-filter lives
//   pad       = <px> | full                       proxy box inflation beyond the shape union
//   clip      = shapes | padded | none            what the proxy's clip/mask covers
//   maskkind  = clippath | maskimage | wrapclip
//   filter    = CSS filter list (default "blur(20px) saturate(1.8)")
//   groups    = single | split                    one proxy for both shapes, or one per shape
//   order     = ab | ba                           paint order of the two split proxies
//   tint      = 0..1                              optics-canvas tint alpha
//   hi        = 0..1                              highlight-canvas alpha
//   text      = on | off                          semantic host DOM labels
//   bg        = mixed | gradient | checker | image | flat
//   fixed     = on | off                          position:fixed content behind the glass
//   xform     = none | content | common | scale    transformed ancestor placement
//   scroller  = on | off                          overflow:auto container under the glass
//   overlay   = on | off                          second (overlay) plane above the base plane
//   scroll    = <px>                              initial window scroll
//   tall      = <px>                              page content height
//   probeflag = on                                render the probe-only fixtures
//
// Shape geometry is fixed and viewport-relative-free so screenshots line up exactly.

const P = new URLSearchParams(location.search);
const p = (k, d) => (P.has(k) ? P.get(k) : d);
const pn = (k, d) => (P.has(k) ? parseFloat(P.get(k)) : d);

export const CFG = {
  mode: p('mode', 'proxy'),
  pad: p('pad', '0'),
  clip: p('clip', 'shapes'),
  maskkind: p('maskkind', 'clippath'),
  filter: p('filter', 'blur(20px) saturate(1.8)'),
  groups: p('groups', 'single'),
  order: p('order', 'ab'),
  tint: pn('tint', 0),
  hi: pn('hi', 0),
  text: p('text', 'off'),
  bg: p('bg', 'mixed'),
  fixed: p('fixed', 'off'),
  xform: p('xform', 'none'),
  scroller: p('scroller', 'off'),
  overlay: p('overlay', 'off'),
  scroll: pn('scroll', 0),
  tall: pn('tall', 2400),
  shapes: p('shapes', 'adjacent'),
  break: p('break', 'none'),
};

// Candidate backdrop-root-forming styles, applied to the GlassRoot — an ancestor
// of the proxy but NOT of the backdrop content. If the engine treats one as
// backdrop-root-forming, the proxy's backdrop becomes empty and the glass goes
// unfiltered. This is the ground truth the structural probe's list must match.
export const BREAKERS = {
  none: {},
  opacity099: { opacity: '0.99' },
  filterNone: { filter: 'none' },
  filterBlur0: { filter: 'blur(0px)' },
  filterGrayscale0: { filter: 'grayscale(0)' },
  maskLinear: { maskImage: 'linear-gradient(#000,#000)', WebkitMaskImage: 'linear-gradient(#000,#000)' },
  clipPathInset: { clipPath: 'inset(0)' },
  containPaint: { contain: 'paint' },
  isolationIsolate: { isolation: 'isolate' },
  mixBlend: { mixBlendMode: 'multiply' },
  willChangeOpacity: { willChange: 'opacity' },
  willChangeTransform: { willChange: 'transform' },
  transform3d: { transform: 'translate3d(0,0,0)' },
};

// Two glass shapes, adjacent with a 40px gap — the double-filter geometry.
// `shapes=overlap` deliberately overlaps them: not a legal vitrea configuration
// (§rendering contract forbids same-plane overlap) but the only way to isolate
// the *mechanism* — whether a later sibling filter samples an earlier one's output.
export const SHAPES = {
  // 40px gap: the ordinary two-group case.
  adjacent: { a: { x: 100, y: 300, w: 200, h: 120, r: 32 },
              b: { x: 340, y: 300, w: 200, h: 120, r: 32 } },
  // 8px gap: the double-filter stress case. With samplingPadding 60 each proxy's
  // box swallows a wide slab of the *other* group's painted clip region, so any
  // sibling filter chaining lands squarely inside the visible glass.
  near:     { a: { x: 100, y: 300, w: 200, h: 120, r: 32 },
              b: { x: 308, y: 300, w: 200, h: 120, r: 32 } },
  // Overlapping clips: illegal under §rendering contract, used only to isolate
  // whether a later sibling filter samples an earlier one's output at all.
  overlap:  { a: { x: 100, y: 300, w: 240, h: 120, r: 32 },
              b: { x: 260, y: 300, w: 240, h: 120, r: 32 } },
}[CFG.shapes] || {
  a: { x: 100, y: 300, w: 200, h: 120, r: 32 },
  b: { x: 340, y: 300, w: 200, h: 120, r: 32 },
};
// Overlay-plane shape sits directly on top of shape A's glass.
export const OVERLAY_SHAPE = { x: 150, y: 330, w: 300, h: 60, r: 20 };

const PLANE_W = 1000;
const PLANE_H = 800;

// ---------------------------------------------------------------- path helpers

function rrPath(s) {
  const { x, y, w, h, r } = s;
  const k = Math.min(r, w / 2, h / 2);
  return (
    `M${x + k},${y}` +
    `H${x + w - k}A${k},${k} 0 0 1 ${x + w},${y + k}` +
    `V${y + h - k}A${k},${k} 0 0 1 ${x + w - k},${y + h}` +
    `H${x + k}A${k},${k} 0 0 1 ${x},${y + h - k}` +
    `V${y + k}A${k},${k} 0 0 1 ${x + k},${y}Z`
  );
}

function unionBox(shapes) {
  const x0 = Math.min(...shapes.map((s) => s.x));
  const y0 = Math.min(...shapes.map((s) => s.y));
  const x1 = Math.max(...shapes.map((s) => s.x + s.w));
  const y1 = Math.max(...shapes.map((s) => s.y + s.h));
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}

function inflate(b, n) {
  return { x: b.x - n, y: b.y - n, w: b.w + 2 * n, h: b.h + 2 * n };
}

// ------------------------------------------------------------------ background

function bgLayers(kind) {
  const grad =
    'linear-gradient(115deg,#0b3c8f 0%,#1f9ad6 22%,#f2c14e 46%,#e0553d 68%,#5b2a86 88%,#08111f 100%)';
  const checker =
    'repeating-conic-gradient(#ffffff 0% 25%, #101014 0% 50%) 0 0 / 24px 24px';
  if (kind === 'flat') return { backgroundImage: 'none', background: '#3a5a80' };
  if (kind === 'gradient') return { background: grad };
  if (kind === 'checker') return { background: checker };
  if (kind === 'image') return { background: '#20242c' };
  return { background: grad };
}

// -------------------------------------------------------------------- builders

function el(tag, cls, style) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (style) Object.assign(n.style, style);
  return n;
}

function buildScene() {
  // #scene is the "arbitrary page content" — the thing the glass must sample.
  const scene = el('div', 'scene');
  Object.assign(scene.style, {
    position: 'relative',
    minHeight: CFG.tall + 'px',
    ...bgLayers(CFG.bg),
  });

  if (CFG.bg === 'mixed' || CFG.bg === 'checker') {
    const ch = el('div', 'checker-band');
    Object.assign(ch.style, {
      position: 'absolute',
      left: '0px',
      top: '260px',
      width: '1000px',
      height: '90px',
      background: 'repeating-conic-gradient(#fff 0% 25%, #0d0d10 0% 50%) 0 0 / 24px 24px',
    });
    scene.appendChild(ch);
  }

  if (CFG.bg === 'mixed' || CFG.bg === 'image') {
    const img = el('img');
    img.src = 'noise.png';
    img.decoding = 'sync';
    Object.assign(img.style, {
      position: 'absolute',
      left: '0px',
      top: '350px',
      width: '1000px',
      height: '150px',
      imageRendering: 'pixelated',
    });
    scene.appendChild(img);
  }

  if (CFG.bg === 'mixed') {
    // High-contrast type crossing the glass band — the classic saturate/blur tell.
    const t = el('div');
    Object.assign(t.style, {
      position: 'absolute',
      left: '0px',
      top: '500px',
      width: '1000px',
      font: '700 44px/48px ui-sans-serif, -apple-system, Helvetica, Arial, sans-serif',
      color: '#00ff9d',
      letterSpacing: '-1px',
      textShadow: '0 0 0 #000',
    });
    t.textContent = 'BACKDROP 0123456789 MMMMM WWWWW';
    scene.appendChild(t);

    const bars = el('div');
    Object.assign(bars.style, {
      position: 'absolute',
      left: '0px',
      top: '200px',
      width: '1000px',
      height: '56px',
      background:
        'repeating-linear-gradient(90deg,#ff0040 0 10px,#00e5ff 10px 20px,#ffe600 20px 30px)',
    });
    scene.appendChild(bars);
  }

  if (CFG.fixed === 'on') {
    const fx = el('div', 'fixed-behind');
    Object.assign(fx.style, {
      position: 'fixed',
      left: '60px',
      top: '280px',
      width: '520px',
      height: '160px',
      background:
        'repeating-linear-gradient(45deg,#ff00c8 0 12px,#00ff62 12px 24px)',
      zIndex: '0',
    });
    document.body.appendChild(fx);
  }

  if (CFG.scroller === 'on') {
    const sc = el('div', 'scroller');
    sc.id = 'scroller';
    Object.assign(sc.style, {
      position: 'absolute',
      left: '60px',
      top: '250px',
      width: '560px',
      height: '230px',
      overflow: 'auto',
      background: '#111',
    });
    const inner = el('div');
    Object.assign(inner.style, {
      height: '1600px',
      background:
        'repeating-linear-gradient(0deg,#ff7a00 0 18px,#0066ff 18px 36px)',
    });
    sc.appendChild(inner);
    scene.appendChild(sc);
  }

  if (CFG.mode === 'inplace') {
    // Reference: backdrop-filter applied to the host element, in place, in the
    // page-content flow — with the semantic content as its children.
    for (const key of ['a', 'b']) {
      const s = SHAPES[key];
      const host = el('div', 'inplace-host');
      Object.assign(host.style, {
        position: 'absolute',
        left: s.x + 'px',
        top: s.y + 'px',
        width: s.w + 'px',
        height: s.h + 'px',
        borderRadius: s.r + 'px',
        background: 'transparent',
        backdropFilter: CFG.filter,
        WebkitBackdropFilter: CFG.filter,
      });
      scene.appendChild(host);
    }
  }

  if (CFG.xform === 'content') {
    const wrap = el('div', 'xform-content');
    wrap.style.transform = 'translate3d(0,0,0)';
    wrap.appendChild(scene);
    return wrap;
  }
  if (CFG.xform === 'scale') {
    const wrap = el('div', 'xform-scale');
    Object.assign(wrap.style, { transform: 'scale(1)', transformOrigin: '0 0' });
    wrap.appendChild(scene);
    return wrap;
  }
  return scene;
}

// ---------------------------------------------------------------- plane / proxy

function makeProxy(shapes, id) {
  const box =
    CFG.pad === 'full'
      ? { x: 0, y: 0, w: PLANE_W, h: PLANE_H }
      : inflate(unionBox(shapes), parseFloat(CFG.pad) || 0);

  const proxy = el('div', 'proxy');
  proxy.id = id;
  Object.assign(proxy.style, {
    position: 'absolute',
    left: box.x + 'px',
    top: box.y + 'px',
    width: box.w + 'px',
    height: box.h + 'px',
    pointerEvents: 'none',
    backdropFilter: CFG.filter,
    WebkitBackdropFilter: CFG.filter,
  });

  // The clip/mask region, expressed in the proxy's own coordinate space.
  const local = shapes.map((s) => ({ ...s, x: s.x - box.x, y: s.y - box.y }));
  const clipShapes =
    CFG.clip === 'padded'
      ? [{ x: 0, y: 0, w: box.w, h: box.h, r: 0 }]
      : local;

  if (CFG.clip !== 'none') {
    const d = clipShapes.map(rrPath).join(' ');
    if (CFG.maskkind === 'clippath') {
      proxy.style.clipPath = `path("${d}")`;
      proxy.style.webkitClipPath = `path("${d}")`;
    } else if (CFG.maskkind === 'maskimage') {
      const svg =
        `<svg xmlns='http://www.w3.org/2000/svg' width='${box.w}' height='${box.h}'>` +
        `<path d='${d}' fill='#000'/></svg>`;
      const url = `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`;
      proxy.style.maskImage = url;
      proxy.style.webkitMaskImage = url;
      proxy.style.maskRepeat = 'no-repeat';
      proxy.style.webkitMaskRepeat = 'no-repeat';
    } else if (CFG.maskkind === 'wrapclip') {
      // Single-shape-only fallback: an overflow-clipping wrapper with radius.
      const s = local[0];
      const wrap = el('div', 'proxy-wrap');
      Object.assign(wrap.style, {
        position: 'absolute',
        left: box.x + s.x + 'px',
        top: box.y + s.y + 'px',
        width: s.w + 'px',
        height: s.h + 'px',
        borderRadius: s.r + 'px',
        overflow: 'hidden',
        pointerEvents: 'none',
      });
      Object.assign(proxy.style, {
        left: -s.x + 'px',
        top: -s.y + 'px',
      });
      wrap.appendChild(proxy);
      return wrap;
    }
  }
  return proxy;
}

function paintOptics(canvas) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (CFG.tint <= 0) return;
  const dpr = canvas.width / PLANE_W;
  ctx.save();
  ctx.scale(dpr, dpr);
  for (const key of ['a', 'b']) {
    const s = SHAPES[key];
    ctx.beginPath();
    ctx.roundRect(s.x, s.y, s.w, s.h, s.r);
    ctx.fillStyle = `rgba(255,255,255,${CFG.tint})`;
    ctx.fill();
    // rim
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = `rgba(255,255,255,${Math.min(1, CFG.tint * 2.2)})`;
    ctx.stroke();
  }
  ctx.restore();
}

function paintHighlight(canvas) {
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (CFG.hi <= 0) return;
  const dpr = canvas.width / PLANE_W;
  ctx.save();
  ctx.scale(dpr, dpr);
  const s = SHAPES.a;
  const g = ctx.createLinearGradient(s.x, s.y, s.x + s.w, s.y + s.h);
  g.addColorStop(0, `rgba(255,255,255,${CFG.hi})`);
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.roundRect(s.x, s.y, s.w, s.h, s.r);
  ctx.fill();
  ctx.restore();
}

function buildPlane(name, shapeList, overlayMode) {
  const plane = el('div', 'plane');
  plane.id = 'plane-' + name;
  Object.assign(plane.style, {
    position: 'fixed',
    left: '0px',
    top: '0px',
    width: PLANE_W + 'px',
    height: PLANE_H + 'px',
    pointerEvents: 'none',
    zIndex: overlayMode ? '20' : '10',
  });

  // 1. backdrop-proxy layer
  if (CFG.mode === 'proxy') {
    const layer = el('div', 'proxy-layer');
    Object.assign(layer.style, {
      position: 'absolute',
      inset: '0',
      pointerEvents: 'none',
    });
    if (overlayMode || CFG.groups === 'single') {
      layer.appendChild(makeProxy(shapeList, 'proxy-' + name + '-all'));
    } else {
      const ids = CFG.order === 'ba' ? ['b', 'a'] : ['a', 'b'];
      for (const k of ids) {
        layer.appendChild(makeProxy([SHAPES[k]], 'proxy-' + name + '-' + k));
      }
    }
    plane.appendChild(layer);
  }

  // 2. optics canvas (transparent; tint/rim placeholder)
  const optics = el('canvas', 'optics');
  optics.id = 'optics-' + name;
  const dpr = window.devicePixelRatio || 1;
  optics.width = PLANE_W * dpr;
  optics.height = PLANE_H * dpr;
  Object.assign(optics.style, {
    position: 'absolute',
    inset: '0',
    width: PLANE_W + 'px',
    height: PLANE_H + 'px',
    pointerEvents: 'none',
  });
  plane.appendChild(optics);

  // 3. semantic host DOM
  const hosts = el('div', 'hosts');
  Object.assign(hosts.style, { position: 'absolute', inset: '0' });
  for (const s of shapeList) {
    const btn = el('button', 'glass-host');
    Object.assign(btn.style, {
      position: 'absolute',
      left: s.x + 'px',
      top: s.y + 'px',
      width: s.w + 'px',
      height: s.h + 'px',
      background: 'transparent',
      border: '0',
      borderRadius: s.r + 'px',
      pointerEvents: 'auto',
      color: '#fff',
      font: '600 22px/1 ui-sans-serif, -apple-system, Helvetica, Arial, sans-serif',
      opacity: CFG.text === 'on' ? '1' : '0',
    });
    btn.textContent = 'Action';
    hosts.appendChild(btn);
  }
  plane.appendChild(hosts);

  // 4. highlight canvas
  const hl = el('canvas', 'highlight');
  hl.id = 'highlight-' + name;
  hl.width = PLANE_W * dpr;
  hl.height = PLANE_H * dpr;
  Object.assign(hl.style, {
    position: 'absolute',
    inset: '0',
    width: PLANE_W + 'px',
    height: PLANE_H + 'px',
    pointerEvents: 'none',
  });
  plane.appendChild(hl);

  paintOptics(optics);
  paintHighlight(hl);
  return plane;
}

// ------------------------------------------------------------------------- main

export function build() {
  document.documentElement.style.background = '#000';
  Object.assign(document.body.style, { margin: '0', background: '#000' });

  const content = buildScene();

  // `inplacefixed`: the in-place reference as a position:fixed host, so it stays
  // put exactly like the plane does. Without this the scroll comparison measures
  // the host scrolling away, not a sampling difference. Must be appended AFTER
  // the scene content so it paints above it, exactly as the plane does.
  const addFixedHosts = () => {
    if (CFG.mode !== 'inplacefixed') return;
    for (const key of ['a', 'b']) {
      const s = SHAPES[key];
      const host = el('div', 'inplace-fixed-host');
      Object.assign(host.style, {
        position: 'fixed', left: s.x + 'px', top: s.y + 'px',
        width: s.w + 'px', height: s.h + 'px', borderRadius: s.r + 'px',
        background: 'transparent', pointerEvents: 'none',
        backdropFilter: CFG.filter, WebkitBackdropFilter: CFG.filter,
      });
      document.body.appendChild(host);
    }
  };

  const root = el('div', 'glass-root');
  root.id = 'glass-root';
  // GlassRoot must have full-viewport geometry, or a `clip-path`/`mask`/`contain`
  // breaker would clip the planes away and be indistinguishable from a re-rooted
  // backdrop. This confound invalidated the first Q5 run.
  Object.assign(root.style, {
    position: 'fixed', left: '0px', top: '0px',
    width: '100%', height: '100%', pointerEvents: 'none',
  });
  // The breaker sits on GlassRoot: an ancestor of the proxy, not of the content.
  Object.assign(root.style, BREAKERS[CFG.break] || {});

  if (CFG.xform === 'common') {
    // A transform on a COMMON ancestor of the backdrop content and the plane root.
    const wrap = el('div', 'xform-common');
    wrap.style.transform = 'translate3d(0,0,0)';
    wrap.appendChild(content);
    document.body.appendChild(wrap);
    addFixedHosts();
    wrap.appendChild(root);
  } else {
    document.body.appendChild(content);
    addFixedHosts();
    document.body.appendChild(root);
  }

  const shapeList = [SHAPES.a, SHAPES.b];
  root.appendChild(buildPlane('base', shapeList, false));
  if (CFG.overlay === 'on') {
    root.appendChild(buildPlane('overlay', [OVERLAY_SHAPE], true));
  }

  if (CFG.scroll) window.scrollTo(0, CFG.scroll);

  // Expose the structural probe target chain for the probe experiments.
  window.__s1 = { CFG, SHAPES, OVERLAY_SHAPE, rrPath, unionBox, inflate };
  document.documentElement.setAttribute('data-s1-ready', '1');
}
