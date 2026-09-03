/**
 * The laws page's ground: one canvas, painted by whichever law is on stage.
 *
 * The same wiring as the site's `StageBackdrop`, for the same reasons: the
 * canvas is registered as the texture the WebGPU tier samples and it is the
 * ordinary DOM the CSS tier filters, so both tiers see the same pixels. What
 * differs is the painter, because each law needs a different bed. The tone law
 * needs a flat achromatic ground it can be read exactly against; the tint law
 * needs two grounds at once; the body law needs fine text, because a sharp
 * component is only visible over something with edges; the lens needs a
 * checkerboard, because a bend is only visible over a grid.
 *
 * Painters are held in refs and read inside the ticker, so a control moving the
 * ground re-paints on the next frame without re-subscribing.
 */

import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

import { groundFill } from "./law";

export interface PaintContext {
  readonly context: CanvasRenderingContext2D;
  readonly width: number;
  readonly height: number;
}

export type Painter = (paint: PaintContext) => void;

const GRID = 32;

/** The site's graticule, drawn where a law wants the coordinate reference. */
export function paintGraticule({ context, width, height }: PaintContext): void {
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
}

/**
 * W9's bed: one flat achromatic ground at a declared linear level, and nothing
 * else on it. No graticule, deliberately: the law reads the backdrop's mean, and
 * a flat ground is the one bed on which that mean is exactly the number the
 * slider states.
 */
export const paintFlat =
  (level: number): Painter =>
  ({ context, width, height }) => {
    context.fillStyle = groundFill(level);
    context.fillRect(0, 0, width, height);
  };

/** W10's bed: a dark ground on the left, a light one on the right, one graticule. */
export const paintSplit =
  (dark: number, light: number): Painter =>
  (paint) => {
    const { context, width, height } = paint;
    context.fillStyle = groundFill(dark);
    context.fillRect(0, 0, width / 2, height);
    context.fillStyle = groundFill(light);
    context.fillRect(width / 2, 0, width / 2, height);
    paintGraticule(paint);
  };

const LINE = "Liquid Glass is size-parameterised lensing over content that stays legible. ";

/**
 * W11c's bed: a page of small text with a ruled margin. Text is the content whose
 * structure the sharp component keeps and the scatter hazes, and a hairline rule
 * every 4 px is the finest edge the body has to carry.
 */
export const paintText: Painter = ({ context, width, height }) => {
  context.fillStyle = "#1a2530";
  context.fillRect(0, 0, width, height);

  context.strokeStyle = "rgb(255 255 255 / 0.16)";
  context.lineWidth = 1;
  context.beginPath();
  for (let y = 4; y < height; y += 4) {
    context.moveTo(0, y + 0.5);
    context.lineTo(56, y + 0.5);
  }
  context.stroke();

  context.fillStyle = "rgb(238 241 245 / 0.9)";
  context.font = '12px ui-monospace, "SF Mono", Menlo, monospace';
  context.textBaseline = "top";
  const repeats = Math.ceil(width / 480) + 1;
  for (let row = 0, y = 12; y < height; row += 1, y += 18) {
    const shift = (row * 37) % 120;
    context.fillText(LINE.repeat(repeats), 72 - shift, y);
  }
};

/** W11c G2's bed: a 16 px checkerboard, the reference's own lens bed. */
export const paintChecker: Painter = ({ context, width, height }) => {
  const cell = 16;
  for (let y = 0; y < height; y += cell) {
    for (let x = 0; x < width; x += cell) {
      const dark = ((x / cell + y / cell) & 1) === 0;
      context.fillStyle = dark ? "#202830" : "#d6dde3";
      context.fillRect(x, y, cell, cell);
    }
  }
};

export interface LawsBackdropProps {
  readonly sourceId: string;
  readonly painter: Painter;
}

export function LawsBackdrop(props: LawsBackdropProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const painterRef = useRef(props.painter);
  painterRef.current = props.painter;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null || root === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;

    // A no-op on a CSS-tier root, so this needs no capability check of its own.
    root.setBackdropTexture(props.sourceId, { kind: "canvas", canvas });

    const unsubscribe = ticker.subscribe(() => {
      const { width, height } = canvas.getBoundingClientRect();
      if (width === 0 || height === 0) return;

      const dpr = window.devicePixelRatio;
      const backingWidth = Math.round(width * dpr);
      const backingHeight = Math.round(height * dpr);
      if (canvas.width !== backingWidth) canvas.width = backingWidth;
      if (canvas.height !== backingHeight) canvas.height = backingHeight;

      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      painterRef.current({ context, width, height });
    });

    return () => {
      unsubscribe();
      root.setBackdropTexture(props.sourceId, undefined);
    };
  }, [props.sourceId, root, ticker]);

  return <canvas ref={canvasRef} className="stage__canvas" aria-hidden="true" />;
}
