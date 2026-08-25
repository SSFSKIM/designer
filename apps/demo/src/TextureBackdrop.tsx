/**
 * The texture region's moving backdrop.
 *
 * A canvas rather than a bundled video, for two reasons that both matter: it is
 * one of the GPU-ownable source kinds the spec names, and it needs no asset, so
 * the playground stays self-contained and the same scene renders identically in
 * CI.
 *
 * Two things are wired here, and they are separate on purpose. `GlassGroup`'s
 * `backdrop` prop *declares* the source to core — that is what keeps
 * `configuredSource: "texture"` true through whatever the runtime resolves.
 * `setBackdropTexture` hands over the actual pixels, which core cannot hold
 * because core may not know what a canvas is (X4). Where the GPU tier is live
 * that upgrade is acceptance #2: the glass above genuinely bends these bands.
 * Where it is not, the declaration still stands and the panel reports the
 * demotion by name.
 *
 * The source is marked dirty on every frame it repaints, which is what feeds
 * core's dirty-epoch accounting: at most one pyramid rebuild per dirty source per
 * frame, however many groups sample it.
 */

import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

export interface TextureBackdropProps {
  readonly sourceId: string;
}

const BANDS = 7;

export function TextureBackdrop(props: TextureBackdropProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);

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

      phase += dtMs / 4000;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, width, height);

      for (let band = 0; band < BANDS; band += 1) {
        const t = band / BANDS;
        const y = ((t + phase) % 1) * (height + 240) - 120;
        const gradient = context.createLinearGradient(0, y - 120, width, y + 120);
        gradient.addColorStop(0, `hsl(${(band * 47 + phase * 120) % 360} 78% 58% / 0.85)`);
        gradient.addColorStop(1, `hsl(${(band * 47 + 90 + phase * 120) % 360} 82% 46% / 0.7)`);
        context.fillStyle = gradient;
        context.beginPath();
        context.ellipse(width / 2, y, width * 0.72, 96, 0, 0, Math.PI * 2);
        context.fill();
      }

      root.scene.markBackdropSourceDirty(props.sourceId);
    });

    return () => {
      unsubscribe();
      root.setBackdropTexture(props.sourceId, undefined);
    };
  }, [props.sourceId, root, ticker]);

  return (
    <>
      <canvas ref={canvasRef} className="texture-canvas" aria-hidden="true" />
      <div className="texture-gradient" aria-hidden="true" />
    </>
  );
}
