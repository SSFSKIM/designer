/**
 * The ground: one fixed, viewport-sized WebGL canvas, and the texture every glass
 * group on the page samples.
 *
 * Two things are wired, and they are separate on purpose. `GlassGroup`'s
 * `backdrop` prop declares the source to the runtime, which keeps
 * `configuredSource: "texture"` true through any demotion; `setBackdropTexture`
 * here hands over the pixels. A canvas source is per-frame by kind, so the runtime
 * re-marks it dirty on every frame it can draw and this component only paints.
 *
 * The canvas is viewport-cover and so is the registered texture, which is the one
 * geometry in which the two mappings agree (DESIGN.md §3).
 */

import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

import { fieldTime, type FieldClock } from "./clock";
import { layerById, type LayerId } from "./palettes";
import { createFieldRenderer } from "./shader";

export const FIELD_TEXTURE_ID = "gyre.field";

/** Backing-store cap. Above this the field costs more than the lens can show. */
const MAX_DPR = 1.5;

export interface FieldProps {
  readonly layer: LayerId;
  readonly clock: FieldClock;
  /** Held still under reduced motion; the field is content, and it stays. */
  readonly animate: boolean;
  readonly onFallback: (fallback: boolean) => void;
}

export function Field(props: FieldProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const layerRef = useRef(props.layer);
  layerRef.current = props.layer;
  const animateRef = useRef(props.animate);
  animateRef.current = props.animate;
  const { clock, onFallback } = props;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null || root === null) return;
    const renderer = createFieldRenderer(canvas);
    if (renderer === null) {
      onFallback(true);
      return;
    }
    onFallback(false);

    root.setBackdropTexture(FIELD_TEXTURE_ID, { kind: "canvas", canvas });

    const unsubscribe = ticker.subscribe((dtMs) => {
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      if (width === 0 || height === 0) return;
      const dpr = Math.min(window.devicePixelRatio, MAX_DPR);
      if (clock.playing && animateRef.current) clock.elapsed += Math.min(dtMs, 50) / 1000;
      renderer.draw(
        layerById(layerRef.current),
        fieldTime(clock),
        Math.round(width * dpr),
        Math.round(height * dpr),
      );
    });

    return () => {
      unsubscribe();
      root.setBackdropTexture(FIELD_TEXTURE_ID, undefined);
      renderer.destroy();
    };
  }, [root, ticker, clock, onFallback]);

  return <canvas ref={canvasRef} className="field" aria-hidden="true" />;
}
