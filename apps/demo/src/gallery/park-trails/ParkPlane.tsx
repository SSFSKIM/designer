/**
 * The plane: the photograph of Diablo Lake, painted into a viewport-fixed canvas at the
 * canvas's own box and device-pixel size, and handed to the runtime as the texture "park".
 *
 * What the runtime receives is an ImageBitmap snapshot of the canvas after each paint, placed on
 * the canvas element. That is the same pixels the reader sees (vitrea.md §2: a canvas painted at
 * its own box is exact), imported once per paint rather than once per frame, because nothing on
 * this plane moves between paints: it repaints on resize and on a device-pixel-ratio change, and
 * that is all.
 */

import { useGlassRootHandle } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

import { buildField, PARK_CROP, placeImage, planeState } from "./plane";
import parkUrl from "./images/park-panorama.jpg";

export const PARK_TEXTURE_ID = "park";

/**
 * The photograph's exposure in the dark scheme: a cool multiply of about 0.5. Chosen from the
 * measurement, not by eye alone: at daylight exposure the ridge band under the planner reads
 * 0.40 to 0.52 encoded, where the dark material's body lands mid-grey and its white ink measured
 * 3.0 to 3.9 : 1; the band has to sit near 0.30 for that ink to carry a label.
 */
const NIGHT_EXPOSURE = "rgb(122 128 142)";

export function ParkPlane(props: { readonly onPainted: () => void }): ReactNode {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { root } = useGlassRootHandle();
  const onPainted = useRef(props.onPainted);
  onPainted.current = props.onPainted;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;

    const dark = window.matchMedia("(prefers-color-scheme: dark)");
    let disposed = false;
    let bitmap: ImageBitmap | undefined;
    const image = new Image();
    image.src = parkUrl;

    const paint = async (): Promise<void> => {
      if (disposed || !image.complete || image.naturalWidth === 0) return;
      const width = window.innerWidth;
      const height = window.innerHeight;
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      const placement = placeImage(image.naturalWidth, image.naturalHeight, width, height, PARK_CROP);
      context.imageSmoothingQuality = "high";
      context.drawImage(
        image,
        placement.dx * ratio,
        placement.dy * ratio,
        placement.dw * ratio,
        placement.dh * ratio,
      );
      if (dark.matches) {
        // The night exposure (DESIGN.md, decisions): one uniform multiply over the whole plane,
        // painted in so the glass reads the pixels the reader sees.
        context.globalCompositeOperation = "multiply";
        context.fillStyle = NIGHT_EXPOSURE;
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.globalCompositeOperation = "source-over";
      }
      // Measured off the painted canvas itself, so the field is whatever the reader sees.
      planeState.field = buildField(canvas, { dx: 0, dy: 0, dw: width, dh: height }, width, height);
      onPainted.current();

      if (root === null) return;
      const next = await createImageBitmap(canvas);
      if (disposed) {
        next.close();
        return;
      }
      root.setBackdropTexture(PARK_TEXTURE_ID, {
        kind: "image",
        image: next,
        placement: { kind: "element", element: canvas },
      });
      bitmap?.close();
      bitmap = next;
    };

    let frame = 0;
    const schedule = (): void => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => void paint());
    };

    void image.decode().then(paint, paint);
    window.addEventListener("resize", schedule);
    dark.addEventListener("change", schedule);
    const ratioQuery = window.matchMedia(`(resolution: ${String(window.devicePixelRatio)}dppx)`);
    ratioQuery.addEventListener("change", schedule);

    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", schedule);
      dark.removeEventListener("change", schedule);
      ratioQuery.removeEventListener("change", schedule);
      bitmap?.close();
    };
  }, [root]);

  return <canvas ref={canvasRef} className="pt-plane" aria-hidden="true" />;
}
