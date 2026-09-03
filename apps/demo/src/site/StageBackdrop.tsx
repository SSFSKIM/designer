/**
 * The instrument window's ground, and the texture the glass above it samples.
 *
 * One canvas paints two things, and they are one thing on purpose: the graticule
 * (the stance's coordinate reference) and a slow chromatic field. Painting the
 * graticule *into* the registered texture rather than laying it on as a CSS
 * background is what keeps the two tiers honest against each other. A GPU-tier
 * group refracts whatever is in the texture; a graticule drawn outside it would
 * sit over the glass unbent, and the page would be showing a lens that misses half
 * its own backdrop.
 *
 * The field is also doing work rather than decoration: refraction is only legible
 * over backdrop detail, and a 32px grid plus broad hue transitions is the cheapest
 * honest source of both high and low spatial frequency.
 *
 * The ground under both is a prop rather than a constant, because one stage needs
 * to move it: backdrop tone adaptation (W7) is a function of how dark the backdrop
 * is, and a page cannot show a reader a transition it has no way to cross. Every
 * other stage passes nothing and gets the window's own colour, unchanged.
 *
 * `GlassGroup`'s `backdrop` prop declares the source to core, which is what keeps
 * `configuredSource: "texture"` true through any demotion; `setBackdropTexture`
 * hands over the pixels, which core cannot hold (X4). A canvas source is
 * per-frame by nature, so the platform re-marks it dirty on every frame it can
 * draw; core's dirty-epoch accounting still bounds that to at most one pyramid
 * rebuild per dirty source per frame, however many groups sample it.
 */

import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

/**
 * What the ground under the graticule is made of.
 *
 * A record rather than a single colour, because the backdrop tone stage (W7) needs
 * the ground to be a *stated* level and the other stages need it to be the
 * window's own colour, and everything painted over the ground has to follow it.
 * `fill` is the base colour the canvas clears to; `field` scales the chromatic
 * lobes' alpha, and at 0 the lobes are not drawn at all; `graticule` is the grid's
 * stroke, which points in whichever direction this particular ground affords.
 *
 * A flat achromatic ground is not a plainer version of the usual one, it is the
 * bed the tone axis was measured on: a group adapts onto ONE resolved backdrop
 * colour, so a surface only settles into its backdrop *exactly* where the
 * backdrop is the same everywhere under it. Over the drifting field the same
 * adaptation would put a flat average-coloured patch on a graded ground, and the
 * page would be showing an approximation while claiming a convergence.
 */
export interface StageGroundPaint {
  readonly fill: string;
  readonly field: number;
  /**
   * The graticule's stroke, because a hairline's colour is a property of the
   * ground it is drawn on rather than of the page. The window's own ground is
   * light and takes a black grid; the tone stage sweeps a grey from near-black up,
   * and a black grid would disappear into the bottom of that sweep — leaving the
   * lens without the high-frequency half of its backdrop on the one stage whose
   * whole subject is what the surface reads underneath it.
   */
  readonly graticule: string;
}

/**
 * The instrument window's own ground: the colour every stage but the tone one uses.
 *
 * Light and cool, per spec `2026-09-03-demo-hero-daylight` Decision Log 1. On the
 * near-black ground this window used to carry, the material adapted onto the
 * ground and collapsed honestly to flat grey plates — no frost, no soft shadow, no
 * size story beyond the labels — which is the one thing the page's own law says
 * daylight is for. `#dde6eb` is `--stage-0` (`oklch(0.919 0.012 232)`) written as
 * a canvas fill; the two have to be the same colour, because the canvas covers the
 * stage box and the declared luminance below is a statement about this fill.
 */
export const DEFAULT_GROUND: StageGroundPaint = {
  fill: "#dde6eb",
  field: 1,
  graticule: "rgb(0 0 0 / 0.10)",
};

/**
 * `DEFAULT_GROUND.fill`'s linear luminance — the level a group that cannot sample
 * the window (it sits over ordinary DOM, not over the texture) declares as its
 * backdrop hint. A hint takes precedence over sampling on both tiers, so it has to
 * be the ground's real level and nothing else; the texture-sampling groups declare
 * none and let the runtime read the canvas.
 *
 * The arithmetic, so a later reader can check it rather than trust it. `#dde6eb`
 * is sRGB (221, 230, 235), which is (0.866667, 0.901961, 0.921569) as fractions.
 * Each channel through the sRGB transfer function, `c > 0.04045` so
 * `((c + 0.055) / 1.055) ** 2.4` in every case, gives linear
 * (0.723055, 0.791298, 0.830770). Weighted by the Rec. 709 luminance coefficients:
 * `0.2126 * 0.723055 + 0.7152 * 0.791298 + 0.0722 * 0.830770`
 * `= 0.153722 + 0.565937 + 0.059981 = 0.779640`.
 */
export const DEFAULT_GROUND_LUMINANCE = 0.7796;

export interface StageBackdropProps {
  readonly sourceId: string;
  /** Held still under reduced motion; the grid alone still carries the detail. */
  readonly animate: boolean;
  readonly ground?: StageGroundPaint;
}

const GRID = 32;
const LOBES = 4;

/*
 * The field is deliberately gentle, and on a light ground that means it SUBTRACTS.
 *
 * The lobes are composited with `multiply` rather than `lighter`, because the two
 * operators are the same idea pointed at the surface each ground has: on the old
 * near-black window the only way to put colour into the ground was to add light to
 * it, and on this one the only way is to take light out. `lighter` here would
 * drive every lobe towards white and the window would lose both its hue variation
 * and its graticule.
 *
 * A saturated multi-lobe bloom is the "mesh gradient" the effects policy warns
 * about, and it is also self-defeating: it washes out the graticule, which is half
 * the backdrop detail the lens needs. `LOBE_LIGHTNESS` at 0.86 is what keeps the
 * multiply gentle — the darker the lobe colour, the harder it pulls the ground
 * down — so the composite stays a light ground with legible tints in it rather
 * than a mid-toned one with colour over it.
 *
 * The floor is also an accessibility constraint, not only a taste one. Control
 * labels sit on glass over this field, and the darker the field drifts the less
 * contrast the dark ink on that glass has; `e2e/contrast.spec.ts` measures that
 * ratio on the rendered pixels across several phases of the drift, because axe
 * cannot compute contrast over a canvas. Lowering these three numbers is what that
 * test is guarding.
 */
const LOBE_LIGHTNESS = 0.86;
const LOBE_CHROMA = 0.15;
const LOBE_ALPHA = 0.24;

export function StageBackdrop(props: StageBackdropProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  /*
   * Both of these are read inside the ticker rather than closed over, for the
   * same reason: the subscription is set up once per source and re-subscribing on
   * every ground change would drop a frame each time the reader moved the slider,
   * which is the one motion this page is asking them to watch.
   */
  const animateRef = useRef(props.animate);
  animateRef.current = props.animate;
  const groundRef = useRef(props.ground ?? DEFAULT_GROUND);
  groundRef.current = props.ground ?? DEFAULT_GROUND;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null || root === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;

    // A no-op on a CSS-tier root, so this needs no capability check of its own.
    root.setBackdropTexture(props.sourceId, { kind: "canvas", canvas });

    let phase = 0;

    const unsubscribe = ticker.subscribe((dtMs) => {
      const { width, height } = canvas.getBoundingClientRect();
      if (width === 0 || height === 0) return;

      const dpr = window.devicePixelRatio;
      const backingWidth = Math.round(width * dpr);
      const backingHeight = Math.round(height * dpr);
      if (canvas.width !== backingWidth) canvas.width = backingWidth;
      if (canvas.height !== backingHeight) canvas.height = backingHeight;

      if (animateRef.current) phase += dtMs / 9000;

      const ground = groundRef.current;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.fillStyle = ground.fill;
      context.fillRect(0, 0, width, height);

      // The field, first: broad low-frequency colour for the lens to bend.
      if (ground.field > 0) {
        context.globalCompositeOperation = "multiply";
        for (let lobe = 0; lobe < LOBES; lobe += 1) {
          const t = lobe / LOBES;
          const cx = width * (0.2 + 0.6 * ((t + phase * 0.6) % 1));
          const cy = height * (0.18 + 0.64 * ((t * 0.7 + phase) % 1));
          const radius = Math.max(width, height) * 0.52;
          const gradient = context.createRadialGradient(cx, cy, 0, cx, cy, radius);
          const hue = (lobe * 78 + phase * 90) % 360;
          const alpha = LOBE_ALPHA * ground.field;
          gradient.addColorStop(0, `oklch(${LOBE_LIGHTNESS} ${LOBE_CHROMA} ${hue} / ${alpha})`);
          gradient.addColorStop(1, `oklch(${LOBE_LIGHTNESS} ${LOBE_CHROMA} ${hue} / 0)`);
          context.fillStyle = gradient;
          context.beginPath();
          context.arc(cx, cy, radius, 0, Math.PI * 2);
          context.fill();
        }
        context.globalCompositeOperation = "source-over";
      }

      // The graticule, second: the high-frequency half, and the stance's own mark.
      context.strokeStyle = ground.graticule;
      context.lineWidth = 1;
      context.beginPath();
      for (let x = GRID; x < width; x += GRID) {
        context.moveTo(x + 0.5, 0);
        context.lineTo(x + 0.5, height);
      }
      for (let y = GRID; y < height; y += GRID) {
        context.moveTo(0, y + 0.5);
        context.lineTo(width, y + 0.5);
      }
      context.stroke();
    });

    return () => {
      unsubscribe();
      root.setBackdropTexture(props.sourceId, undefined);
    };
  }, [props.sourceId, root, ticker]);

  return <canvas ref={canvasRef} className="stage__canvas" aria-hidden="true" />;
}
