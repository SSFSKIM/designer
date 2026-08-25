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
 * `GlassGroup`'s `backdrop` prop declares the source to core, which is what keeps
 * `configuredSource: "texture"` true through any demotion; `setBackdropTexture`
 * hands over the pixels, which core cannot hold (X4). The source is marked dirty
 * on each repaint, feeding core's dirty-epoch accounting: at most one pyramid
 * rebuild per dirty source per frame, however many groups sample it.
 */

import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

export interface StageBackdropProps {
  readonly sourceId: string;
  /** Held still under reduced motion; the grid alone still carries the detail. */
  readonly animate: boolean;
}

const GRID = 32;
const LOBES = 4;

/*
 * The field is deliberately dim.
 *
 * A bright multi-lobe bloom is the "mesh gradient" the effects policy warns about,
 * and it is also self-defeating here: it washes out the graticule, which is half
 * the backdrop detail the lens needs, and it drives the adaptive foreground on the
 * glass towards dark ink on a surface the rest of the page reads as a dark
 * instrument. Peak lightness and alpha are set so the composite stays a dark
 * ground with legible hue variation rather than a light one with colour in it.
 *
 * The ceiling is also an accessibility constraint, not only a taste one. Control
 * labels sit on glass over this field, and the brighter the field drifts the less
 * contrast they have; `e2e/site.spec.ts` measures that ratio on the rendered pixels
 * across several phases of the drift, because axe cannot compute contrast over a
 * canvas. Raising these three numbers is what that test is guarding.
 */
const LOBE_LIGHTNESS = 0.4;
const LOBE_CHROMA = 0.15;
const LOBE_ALPHA = 0.24;

export function StageBackdrop(props: StageBackdropProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animateRef = useRef(props.animate);
  animateRef.current = props.animate;

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

      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.fillStyle = "#0c151a";
      context.fillRect(0, 0, width, height);

      // The field, first: broad low-frequency colour for the lens to bend.
      context.globalCompositeOperation = "lighter";
      for (let lobe = 0; lobe < LOBES; lobe += 1) {
        const t = lobe / LOBES;
        const cx = width * (0.2 + 0.6 * ((t + phase * 0.6) % 1));
        const cy = height * (0.18 + 0.64 * ((t * 0.7 + phase) % 1));
        const radius = Math.max(width, height) * 0.52;
        const gradient = context.createRadialGradient(cx, cy, 0, cx, cy, radius);
        const hue = (lobe * 78 + phase * 90) % 360;
        gradient.addColorStop(
          0,
          `oklch(${LOBE_LIGHTNESS} ${LOBE_CHROMA} ${hue} / ${LOBE_ALPHA})`,
        );
        gradient.addColorStop(1, `oklch(${LOBE_LIGHTNESS} ${LOBE_CHROMA} ${hue} / 0)`);
        context.fillStyle = gradient;
        context.beginPath();
        context.arc(cx, cy, radius, 0, Math.PI * 2);
        context.fill();
      }
      context.globalCompositeOperation = "source-over";

      // The graticule, second: the high-frequency half, and the stance's own mark.
      context.strokeStyle = "rgb(255 255 255 / 0.11)";
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

      /*
       * Only where a group actually declares this source. The canvas is the
       * stage's ground in every mode, but it is a *registered texture* only in the
       * modes whose groups name it; the behaviour mode's groups sample arbitrary
       * DOM through the browser's own `backdrop-filter` instead, and marking a
       * source no group declared is an error rather than a no-op.
       */
      if (root.scene.backdropSource(props.sourceId) !== undefined) {
        root.scene.markBackdropSourceDirty(props.sourceId);
      }
    });

    return () => {
      unsubscribe();
      root.setBackdropTexture(props.sourceId, undefined);
    };
  }, [props.sourceId, root, ticker]);

  return <canvas ref={canvasRef} className="stage__canvas" aria-hidden="true" />;
}
