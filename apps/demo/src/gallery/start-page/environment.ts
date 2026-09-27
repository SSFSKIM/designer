/**
 * The environment: the day's photograph painted into one viewport-sized canvas, graded for the
 * colour scheme, handed to the runtime as a texture, and measured under each group's own box.
 *
 * Three quantities are kept apart here because the skill's spatial conditions keep them apart
 * (SKILL.md §4, the spatial register, condition 1): the SOURCE is these painted pixels; the TONE
 * INPUT a group declares is the level measured under that group's own box from those pixels; the
 * DRAWN level behind a text line is neither, and is measured on rendered pixels by the audit.
 *
 * The statistic is the runtime's own (`packages/platform-web/src/backdrop-tone.ts`): the mean of
 * each channel in ENCODED space, decoded once, then Rec. 709 luma. A declaration made with any
 * other statistic would be a different number standing for the same fact.
 */

import type { BackdropHint } from "@vitreajs/vitrea-react";

import type { Grade, Photograph } from "./data";

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** What was painted, kept so any box can be measured later without repainting. */
export interface Painted {
  readonly data: Uint8ClampedArray;
  readonly width: number;
  readonly height: number;
  /** Device pixels per CSS pixel of this paint. */
  readonly scale: number;
}

const images = new Map<string, Promise<HTMLImageElement>>();

/** Decode a photograph once; every phase change after the first is a repaint, not a fetch. */
export function loadPhotograph(url: string): Promise<HTMLImageElement> {
  let pending = images.get(url);
  if (pending === undefined) {
    const image = new Image();
    image.decoding = "async";
    image.src = url;
    pending = image.decode().then(() => image);
    images.set(url, pending);
  }
  return pending;
}

function gradeTable(grade: Grade): Uint8ClampedArray | undefined {
  if (grade.gain === 1 && !Number.isFinite(grade.ceiling) && grade.lift === 0) return undefined;
  const table = new Uint8ClampedArray(256);
  for (let code = 0; code < 256; code += 1) {
    const lifted = grade.lift + (1 - grade.lift) * (code / 255);
    const graded = Number.isFinite(grade.ceiling)
      ? grade.ceiling * (1 - Math.exp((-grade.gain * lifted) / grade.ceiling))
      : grade.gain * lifted;
    table[code] = Math.round(Math.min(1, Math.max(0, graded)) * 255);
  }
  return table;
}

/**
 * Paint `photo` cover-fit into `canvas` at the viewport's size and `scale` device pixels per CSS
 * pixel, crop by its focal point and zoom, then apply the scheme's grade to every pixel's luma.
 */
export function paintPhotograph(
  canvas: HTMLCanvasElement,
  image: HTMLImageElement,
  photo: Photograph,
  scheme: "light" | "dark",
  viewport: { readonly width: number; readonly height: number },
  scale: number,
): Painted {
  const width = Math.max(1, Math.round(viewport.width * scale));
  const height = Math.max(1, Math.round(viewport.height * scale));
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;
  const context = canvas.getContext("2d", { willReadFrequently: true });
  if (context === null) throw new Error("Daybreak needs a 2D canvas to paint its environment.");

  const cover = Math.max(width / image.naturalWidth, height / image.naturalHeight) * photo.zoom;
  const drawWidth = image.naturalWidth * cover;
  const drawHeight = image.naturalHeight * cover;
  const [fx, fy] = photo.focus;
  const dx = -(drawWidth - width) * fx;
  const dy = -(drawHeight - height) * fy;
  context.imageSmoothingQuality = "high";
  context.drawImage(image, dx, dy, drawWidth, drawHeight);

  const pixels = context.getImageData(0, 0, width, height);
  const table = gradeTable(photo.grade[scheme]);
  if (table !== undefined) {
    // The curve is applied to each pixel's encoded luma and the pixel scaled by the ratio, so
    // the grade darkens the photograph without greying it: a sky stays blue, a field green.
    const data = pixels.data;
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i] as number;
      const g = data[i + 1] as number;
      const b = data[i + 2] as number;
      const luma = Math.round(0.2126 * r + 0.7152 * g + 0.0722 * b);
      if (luma === 0) {
        data[i] = data[i + 1] = data[i + 2] = table[0] as number;
        continue;
      }
      const scale = (table[luma] as number) / luma;
      data[i] = r * scale;
      data[i + 1] = g * scale;
      data[i + 2] = b * scale;
    }
    context.putImageData(pixels, 0, 0);
  }
  return { data: pixels.data, width, height, scale };
}

/** A registered host's footprint as the glass draws it: its box and its own corner radius. */
export interface HostShape {
  readonly box: Box;
  readonly radius: number;
}

/**
 * The clear variant's dimming layer (`DESIGN.md` part two, "Clear-variant comparison"). Neither
 * tier draws the scrim a clear group's `dimming` policy names, so the page paints it here, into
 * the one plane the glass samples: black at `strength` under every host's footprint, full to the
 * edge and fading to nothing `feather` CSS px past it, so the rim bends a gradient and the
 * photograph's own structure rather than a hard step. Uncalibrated: no bed scene declares clear.
 */
export interface Dimming {
  readonly strength: number;
  readonly feather: number;
}

export interface Dimmer {
  /**
   * Composite the layer for these shapes into the canvas and return what is now painted. Only
   * the rectangles of shapes that moved since the last call are recomputed, so a morph's host
   * can be followed frame by frame; the returned pixels are the ones put, so a footprint
   * measured from them describes the composite the glass samples.
   */
  apply(
    shapes: readonly HostShape[],
    dimming: Dimming,
    viewport: { readonly width: number; readonly height: number },
  ): Painted;
}

interface DeviceRect {
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
}

/** Signed distance from a point to a rounded box, CSS px; negative inside. */
function roundedBoxDistance(px: number, py: number, shape: HostShape): number {
  const { box } = shape;
  const hw = box.width / 2;
  const hh = box.height / 2;
  const r = Math.max(0, Math.min(shape.radius, hw, hh));
  const qx = Math.abs(px - (box.x + hw)) - (hw - r);
  const qy = Math.abs(py - (box.y + hh)) - (hh - r);
  const ox = Math.max(qx, 0);
  const oy = Math.max(qy, 0);
  return Math.sqrt(ox * ox + oy * oy) + Math.min(Math.max(qx, qy), 0) - r;
}

/**
 * A dimmer over one paint of the photograph. It keeps the graded paint untouched and writes the
 * composite into its own copy, so moving a footprint restores what it leaves exactly.
 */
export function createDimmer(canvas: HTMLCanvasElement, base: Painted): Dimmer {
  const context = canvas.getContext("2d", { willReadFrequently: true });
  if (context === null) throw new Error("Daybreak needs a 2D canvas to paint its environment.");
  const composite = new ImageData(new Uint8ClampedArray(base.data), base.width, base.height);
  const out = composite.data;
  let applied: { rects: DeviceRect[]; keys: string[]; dimming: string } | undefined;

  return {
    apply(shapes, dimming, viewport) {
      // CSS px of the CURRENT viewport onto this paint, as `measureFootprint` maps them.
      const sx = base.width / viewport.width;
      const sy = base.height / viewport.height;
      const reach = Math.max(0, dimming.feather);
      const rects = shapes.map(
        ({ box }): DeviceRect => ({
          x0: Math.max(0, Math.floor((box.x - reach) * sx)),
          y0: Math.max(0, Math.floor((box.y - reach) * sy)),
          x1: Math.min(base.width, Math.ceil((box.x + box.width + reach) * sx)),
          y1: Math.min(base.height, Math.ceil((box.y + box.height + reach) * sy)),
        }),
      );
      const keys = shapes.map(({ box, radius }) =>
        [box.x, box.y, box.width, box.height, radius, viewport.width, viewport.height].join(","),
      );
      const dimmingKey = `${String(dimming.strength)}|${String(reach)}`;

      const dirty: DeviceRect[] = [];
      const previous = applied;
      if (previous === undefined || previous.dimming !== dimmingKey || previous.keys.length !== keys.length) {
        dirty.push(...rects, ...(previous?.rects ?? []));
      } else {
        keys.forEach((key, index) => {
          const now = rects[index];
          const was = previous.rects[index];
          if (key === previous.keys[index] || now === undefined || was === undefined) return;
          dirty.push({
            x0: Math.min(now.x0, was.x0),
            y0: Math.min(now.y0, was.y0),
            x1: Math.max(now.x1, was.x1),
            y1: Math.max(now.y1, was.y1),
          });
        });
      }

      for (const rect of dirty) {
        if (rect.x1 <= rect.x0 || rect.y1 <= rect.y0) continue;
        // The shapes whose feathered rectangle reaches into this one; nothing else can dim it.
        const near = shapes.filter((_, index) => {
          const other = rects[index];
          return (
            other !== undefined &&
            other.x0 < rect.x1 &&
            other.x1 > rect.x0 &&
            other.y0 < rect.y1 &&
            other.y1 > rect.y0
          );
        });
        for (let y = rect.y0; y < rect.y1; y += 1) {
          const cy = (y + 0.5) / sy;
          let i = (y * base.width + rect.x0) * 4;
          for (let x = rect.x0; x < rect.x1; x += 1, i += 4) {
            const cx = (x + 0.5) / sx;
            let cover = 0;
            for (const shape of near) {
              const distance = roundedBoxDistance(cx, cy, shape);
              if (distance <= 0) {
                cover = 1;
                break;
              }
              if (distance < reach) {
                const t = distance / reach;
                cover = Math.max(cover, 1 - t * t * (3 - 2 * t));
              }
            }
            const keep = 1 - dimming.strength * cover;
            out[i] = (base.data[i] as number) * keep;
            out[i + 1] = (base.data[i + 1] as number) * keep;
            out[i + 2] = (base.data[i + 2] as number) * keep;
          }
        }
        context.putImageData(composite, 0, 0, rect.x0, rect.y0, rect.x1 - rect.x0, rect.y1 - rect.y0);
      }

      applied = { rects, keys, dimming: dimmingKey };
      return { data: out, width: base.width, height: base.height, scale: base.scale };
    },
  };
}

function decode(encoded: number): number {
  return encoded <= 0.04045 ? encoded / 12.92 : Math.pow((encoded + 0.055) / 1.055, 2.4);
}

export interface Footprint {
  /** Relative luminance of the encoded mean, decoded once — the runtime's own reading. */
  readonly luminance: number;
  /** The same level in encoded terms, for the record and the dead-band check. */
  readonly encoded: number;
}

/**
 * Measure the painted pixels under one box, in CSS px of the CURRENT viewport. The canvas is
 * stretched to the viewport, so for the moment between a resize and its repaint the pixels on
 * screen are the old paint scaled; mapping through the viewport measures what is displayed.
 */
export function measureFootprint(
  painted: Painted,
  box: Box,
  viewport: { readonly width: number; readonly height: number },
): Footprint | undefined {
  const sx = painted.width / viewport.width;
  const sy = painted.height / viewport.height;
  const x0 = Math.max(0, Math.floor(box.x * sx));
  const y0 = Math.max(0, Math.floor(box.y * sy));
  const x1 = Math.min(painted.width, Math.ceil((box.x + box.width) * sx));
  const y1 = Math.min(painted.height, Math.ceil((box.y + box.height) * sy));
  if (x1 <= x0 || y1 <= y0) return undefined;
  // Every second device pixel on each axis: the mean of a photograph does not move at that
  // stride, and a 500 × 400 box at 2x is 800 000 pixels otherwise.
  const step = painted.scale >= 2 ? 2 : 1;
  let r = 0;
  let g = 0;
  let b = 0;
  let n = 0;
  for (let y = y0; y < y1; y += step) {
    let i = (y * painted.width + x0) * 4;
    for (let x = x0; x < x1; x += step, i += 4 * step) {
      r += painted.data[i] as number;
      g += painted.data[i + 1] as number;
      b += painted.data[i + 2] as number;
      n += 1;
    }
  }
  const level = [r / n / 255, g / n / 255, b / n / 255] as const;
  const luminance =
    0.2126 * decode(level[0]) + 0.7152 * decode(level[1]) + 0.0722 * decode(level[2]);
  const encoded = 0.2126 * level[0] + 0.7152 * level[1] + 0.0722 * level[2];
  return { luminance, encoded };
}

/**
 * The declaration a group makes from its footprint. The tone has to name a pole for the ink
 * decision to read the level at all (`hintedBackdropLuminance` answers nothing for `mixed`), so
 * it is the side of mid-grey the measured level is on; the level itself is the measurement.
 */
export function hintFrom(footprint: Footprint): BackdropHint {
  return {
    tone: footprint.luminance >= 0.18 ? "light" : "dark",
    luminance: Math.round(footprint.luminance * 1000) / 1000,
  };
}
