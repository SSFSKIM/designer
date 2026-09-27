/**
 * The plane: the still from the opening film, fixed to the viewport and handed to the runtime.
 *
 * One `<canvas>` is painted once per resize and snapshotted into an `ImageBitmap`. The bitmap is
 * the texture, placed by the canvas element, so the glass samples exactly the pixels the reader
 * sees at exactly the box they occupy. It is imported once rather than re-read from the canvas on
 * every frame, which is what a canvas source would cost for a picture that never changes between
 * resizes. The canvas is also read back by the page: every group's hint is measured off these
 * pixels under the group's footprint after each repaint (`beneath.ts`), which is why its context
 * is created for frequent reads and why a repaint is announced through `onPaint`.
 *
 * The crop is anchored rather than centred. A centred cover fit puts the day control and Tickets
 * over flat grey sky (a luminance standard deviation of 1.0 of 255 under both, measured), where the
 * lens has nothing to bend. Anchoring the frame's right edge at the nearest lamp standard and its
 * top just above the signs puts every bar group over structure at any desktop aspect: the facades
 * under the navigation, the traffic light and the hotel's windows under the days, the head of a
 * lamp standard under Tickets. The "50" sign falls in the gap between the navigation and the days:
 * under the navigation's end it cost the dark scheme's white labels their margin (DESIGN.md).
 */

import { useGlassRoot } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode } from "react";

import stillUrl from "./images/ironai-crossing.jpg";

export const STILL_SOURCE_ID = "still";

/** Where the frame is anchored, as fractions of the photograph (2600 x 1463 at placement). */
const ANCHOR_RIGHT = 1961 / 2600;
const ANCHOR_TOP = 297 / 1463;

interface Crop {
  readonly sx: number;
  readonly sy: number;
  readonly sw: number;
  readonly sh: number;
}

/** Cover the viewport while keeping the anchor's right edge and top in frame. */
function cropFor(image: HTMLImageElement, width: number, height: number): Crop {
  const right = image.naturalWidth * ANCHOR_RIGHT;
  const top = image.naturalHeight * ANCHOR_TOP;
  const scale = Math.max(width / right, height / (image.naturalHeight - top));
  const sw = width / scale;
  const sh = height / scale;
  return { sx: Math.max(0, right - sw), sy: top, sw, sh };
}

export interface StillProps {
  /** Called with the canvas each time it has been repainted, before the texture is handed over. */
  readonly onPaint?: (canvas: HTMLCanvasElement) => void;
}

export function Still(props: StillProps): ReactNode {
  const { onPaint } = props;
  const root = useGlassRoot();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const onPaintRef = useRef(onPaint);
  onPaintRef.current = onPaint;

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d", { willReadFrequently: true });
    if (canvas === null || context === null || context === undefined) return;

    const image = new Image();
    image.decoding = "async";
    image.src = stillUrl;

    let disposed = false;
    let bitmap: ImageBitmap | null = null;
    let painted = 0;

    const paint = async (): Promise<void> => {
      if (!image.complete || image.naturalWidth === 0) return;
      const ticket = ++painted;
      const width = window.innerWidth;
      const height = window.innerHeight;
      const dpr = window.devicePixelRatio;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      const { sx, sy, sw, sh } = cropFor(image, width, height);
      context.imageSmoothingEnabled = true;
      context.imageSmoothingQuality = "high";
      context.drawImage(image, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
      onPaintRef.current?.(canvas);

      if (root === null) return;
      const next = await createImageBitmap(canvas);
      // A resize that landed while this snapshot was being taken supersedes it.
      if (disposed || ticket !== painted) {
        next.close();
        return;
      }
      root.setBackdropTexture(STILL_SOURCE_ID, {
        kind: "image",
        image: next,
        placement: { kind: "element", element: canvas },
      });
      bitmap?.close();
      bitmap = next;
    };

    let pending: number | undefined;
    const onResize = (): void => {
      window.clearTimeout(pending);
      pending = window.setTimeout(() => void paint(), 90);
    };

    image.addEventListener("load", () => void paint());
    if (image.complete) void paint();
    window.addEventListener("resize", onResize);

    return () => {
      disposed = true;
      window.clearTimeout(pending);
      window.removeEventListener("resize", onResize);
      root?.setBackdropTexture(STILL_SOURCE_ID, undefined);
      bitmap?.close();
    };
  }, [root]);

  return (
    <canvas
      ref={canvasRef}
      className="ff-still"
      role="img"
      aria-label="Still from Ironai: pedestrians cross a snow-covered street in Otaru, past a speed-limit sign, a traffic light and a line of lamp standards."
    />
  );
}
