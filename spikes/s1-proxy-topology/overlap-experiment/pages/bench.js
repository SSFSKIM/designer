// Bench page for the S1 follow-up: cross-group backdrop leak versus separation.
//
// Deliberately a stripped rebuild of S1's `pages/harness.js` rather than a reuse
// of it: this experiment only needs the split-vs-single geometry, and the one
// parameter S1 hard-coded (the gap between the two groups) is the independent
// variable here. Everything else that mattered to the leak table is preserved
// verbatim so the two runs are comparable — shape size 200x120 r32, the same
// per-group proxy construction (absolute box inflated by `pad`, clipped to the
// group's own rounded rect, `backdrop-filter` on the box), the same plane
// sandwich, and the same `blur(Npx) saturate(1.8)` filter.
//
// Params:
//   sigma  = blur standard deviation in CSS px          (default 8, the nominal material)
//   gap    = CSS px between shape A's right edge and B's left edge
//   pad    = proxy box inflation in CSS px              (default 3*sigma, the shipped floor)
//   groups = single | split                             one proxy for both shapes, or one each
//   order  = ab | ba                                    paint order of the two split proxies
//   bg     = checker | image | gradient | flat | mixed  backdrop class
//            (`mixed` is S1's own default scene, rebuilt element for element, so
//             the sigma=20 rows here reproduce S1's leak table exactly)
//   sat    = saturation amount                          (default 1.8, S1's F_BLUR)

(() => {
  const P = new URLSearchParams(location.search);
  const p = (k, d) => (P.has(k) ? P.get(k) : d);
  const pn = (k, d) => (P.has(k) ? parseFloat(P.get(k)) : d);

  const SIGMA = pn('sigma', 8);
  const CFG = {
    sigma: SIGMA,
    gap: pn('gap', 40),
    pad: pn('pad', 3 * SIGMA),
    groups: p('groups', 'single'),
    order: p('order', 'ab'),
    bg: p('bg', 'checker'),
    sat: pn('sat', 1.8),
  };
  const FILTER = `blur(${CFG.sigma}px) saturate(${CFG.sat})`;

  const PLANE_W = 1000;
  const PLANE_H = 800;

  // Shape A is pinned; B slides with the gap. Same size/radius/origin as S1.
  const A = { x: 100, y: 300, w: 200, h: 120, r: 32 };
  const B = { x: A.x + A.w + CFG.gap, y: 300, w: 200, h: 120, r: 32 };

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

  const inflate = (b, n) => ({ x: b.x - n, y: b.y - n, w: b.w + 2 * n, h: b.h + 2 * n });

  function el(tag, style) {
    const n = document.createElement(tag);
    if (style) Object.assign(n.style, style);
    return n;
  }

  // ------------------------------------------------------------------ backdrop

  const pending = [];

  function addImage(scene, top, height) {
    const img = el('img', {
      position: 'absolute',
      left: '0px',
      top: top + 'px',
      width: '1000px',
      height: height + 'px',
      imageRendering: 'pixelated',
    });
    img.src = 'noise.png';
    img.decoding = 'sync';
    pending.push(
      img.decode ? img.decode().catch(() => {}) : new Promise((r) => { img.onload = r; }),
    );
    scene.appendChild(img);
  }

  const GRADIENT =
    'linear-gradient(115deg,#0b3c8f 0%,#1f9ad6 22%,#f2c14e 46%,#e0553d 68%,#5b2a86 88%,#08111f 100%)';

  function buildScene() {
    const scene = el('div', { position: 'relative', minHeight: '2400px' });

    if (CFG.bg === 'mixed') {
      // S1's own scene, rebuilt: gradient ground, a checker band across the top
      // half of the glass, a noise raster across the bottom half, high-contrast
      // type below, colour bars above.
      scene.style.background = GRADIENT;
      scene.appendChild(el('div', {
        position: 'absolute', left: '0px', top: '260px', width: '1000px', height: '90px',
        background: 'repeating-conic-gradient(#fff 0% 25%, #0d0d10 0% 50%) 0 0 / 24px 24px',
      }));
      addImage(scene, 350, 150);
      const t = el('div', {
        position: 'absolute', left: '0px', top: '500px', width: '1000px',
        font: '700 44px/48px ui-sans-serif, -apple-system, Helvetica, Arial, sans-serif',
        color: '#00ff9d', letterSpacing: '-1px', textShadow: '0 0 0 #000',
      });
      t.textContent = 'BACKDROP 0123456789 MMMMM WWWWW';
      scene.appendChild(t);
      scene.appendChild(el('div', {
        position: 'absolute', left: '0px', top: '200px', width: '1000px', height: '56px',
        background: 'repeating-linear-gradient(90deg,#ff0040 0 10px,#00e5ff 10px 20px,#ffe600 20px 30px)',
      }));
      return scene;
    }

    if (CFG.bg === 'flat') {
      scene.style.background = '#3a5a80';
    } else if (CFG.bg === 'gradient') {
      scene.style.background = GRADIENT;
    } else if (CFG.bg === 'checker') {
      // High-frequency, hard-edged, achromatic: S1's strongest tell for any
      // sampling error, and the class most likely to make a small leak visible.
      scene.style.background = 'repeating-conic-gradient(#ffffff 0% 25%, #101014 0% 50%) 0 0 / 24px 24px';
    } else if (CFG.bg === 'image') {
      // Photo-class raster: broadband content, no global structure the eye can
      // predict. Stretched over the whole glass band so no shape sees an edge
      // of it (an edge inside the band would confound the leak with a feature).
      scene.style.background = '#20242c';
      addImage(scene, 200, 340);
    }
    return scene;
  }

  // --------------------------------------------------------------------- proxy

  function makeProxy(shapes, id) {
    const box = inflate(unionBox(shapes), CFG.pad);
    const proxy = el('div', {
      position: 'absolute',
      left: box.x + 'px',
      top: box.y + 'px',
      width: box.w + 'px',
      height: box.h + 'px',
      pointerEvents: 'none',
      backdropFilter: FILTER,
      WebkitBackdropFilter: FILTER,
    });
    proxy.id = id;
    const local = shapes.map((s) => ({ ...s, x: s.x - box.x, y: s.y - box.y }));
    const d = local.map(rrPath).join(' ');
    proxy.style.clipPath = `path("${d}")`;
    proxy.style.webkitClipPath = `path("${d}")`;
    return proxy;
  }

  function buildPlane() {
    const plane = el('div', {
      position: 'fixed',
      left: '0px',
      top: '0px',
      width: PLANE_W + 'px',
      height: PLANE_H + 'px',
      pointerEvents: 'none',
      zIndex: '10',
    });
    const layer = el('div', { position: 'absolute', inset: '0', pointerEvents: 'none' });
    if (CFG.groups === 'single') {
      layer.appendChild(makeProxy([A, B], 'proxy-all'));
    } else {
      const ids = CFG.order === 'ba' ? [['b', B], ['a', A]] : [['a', A], ['b', B]];
      for (const [k, s] of ids) layer.appendChild(makeProxy([s], 'proxy-' + k));
    }
    plane.appendChild(layer);

    // The semantic host DOM, transparent — present so the sandwich is the real
    // one, absent from every measurement because it paints nothing.
    const hosts = el('div', { position: 'absolute', inset: '0' });
    for (const s of [A, B]) {
      hosts.appendChild(
        el('button', {
          position: 'absolute',
          left: s.x + 'px',
          top: s.y + 'px',
          width: s.w + 'px',
          height: s.h + 'px',
          background: 'transparent',
          border: '0',
          borderRadius: s.r + 'px',
          padding: '0',
          pointerEvents: 'auto',
          opacity: '0',
        }),
      );
    }
    plane.appendChild(hosts);
    return plane;
  }

  // ---------------------------------------------------------------------- main

  document.documentElement.style.background = '#000';
  Object.assign(document.body.style, { margin: '0', background: '#000' });

  document.body.appendChild(buildScene());

  const root = el('div', {
    position: 'fixed',
    left: '0px',
    top: '0px',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
  });
  root.id = 'glass-root';
  root.appendChild(buildPlane());
  document.body.appendChild(root);

  window.__cfg = { ...CFG, A, B, filter: FILTER };

  Promise.all(pending).then(() => {
    document.documentElement.setAttribute('data-bench-ready', '1');
  });
})();
