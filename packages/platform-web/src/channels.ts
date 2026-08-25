/**
 * The `--vitrea-*` channel vocabulary, and reading it back off a host.
 *
 * §Motion puts the interaction drivers on the CPU and the renderer consumes
 * their *outputs* — every channel is a value, never a time. Which leaves one
 * question this module answers: how does a value computed by a binding reach the
 * compositor, when the binding sits above `platform-web` and the compositor sits
 * below it?
 *
 * Through the host element's own inline style. A binding publishes each channel
 * as a custom property in the vocabulary below; the frame's `write` phase reads
 * them straight back. Two properties make that the right seam rather than a
 * convenient one:
 *
 * - **It costs no layout.** `style.getPropertyValue` reads the *inline*
 *   declaration block — the same object `setProperty` just wrote — so it never
 *   touches the cascade and never forces a style recalculation. The zero-read
 *   steady state GeometrySync guarantees survives it intact.
 * - **It is framework-agnostic.** The channels are already documented as a
 *   styling surface, so any binding — or an app driving its own motion — reaches
 *   the compositor by writing the same properties. Nothing here knows React
 *   exists.
 *
 * A missing property is not an error: an undriven surface is idle, and idle is a
 * legal state with defined values.
 */

import type { Rect } from "vitrea";

/**
 * The custom properties a surface publishes each frame.
 *
 * `state` is not a render channel — it carries the interaction machine's
 * resolved state name for CSS and for tests — but it belongs to the same
 * vocabulary and is listed here so the vocabulary has one home.
 */
export const GLASS_CHANNEL_PROPERTIES = {
  press: "--vitrea-press",
  glow: "--vitrea-glow",
  sweep: "--vitrea-sweep",
  lensStrength: "--vitrea-lens",
  pressX: "--vitrea-press-x",
  pressY: "--vitrea-press-y",
  state: "--vitrea-state",
} as const;

/**
 * Motion-driver outputs for one surface, in the renderer's own shape.
 *
 * `pressPoint` is in **viewport** CSS px here, while a binding publishes it
 * relative to the host's border box — the conversion is this module's, because
 * the host rect it needs is the one the read phase already measured.
 */
export interface SurfaceChannelValues {
  /** `pressCompression`, 0..1. */
  readonly press: number;
  /** `glow`, 0..1. */
  readonly glow: number;
  /** Specular sweep position, 0..1 around the contour. */
  readonly sweep: number;
  /** `lensStrength`, 0..1+. Multiplies the resolved refraction scale. */
  readonly lensStrength: number;
  /** Viewport CSS px. Absent means the renderer uses the surface's centre. */
  readonly pressPoint?: readonly [number, number];
}

/**
 * An undriven surface. `lensStrength` is 1 rather than 0 — a surface nobody is
 * animating still refracts at its material's nominal strength; zero would be a
 * surface with its lens switched off, which is a different claim.
 */
export const IDLE_CHANNELS: SurfaceChannelValues = {
  press: 0,
  glow: 0,
  sweep: 0,
  lensStrength: 1,
};

/** The one thing this module needs from a host. `HTMLElement` satisfies it. */
export interface ChannelSource {
  readonly style: { getPropertyValue(property: string): string };
}

const numberFrom = (raw: string, fallback: number): number => {
  // `parseFloat` stops at the unit, which is what makes `"12.5px"` and `"0.75"`
  // the same call. An unparseable value falls back rather than propagating NaN
  // into a uniform, where it would silently blank a whole pass.
  const value = Number.parseFloat(raw);
  return Number.isFinite(value) ? value : fallback;
};

/**
 * Read one surface's channels off its host.
 *
 * `bounds` is the host's measured viewport rect, used only to lift the press
 * point out of host-local coordinates. A press point needs both axes to mean
 * anything, so a half-written pair is treated as absent.
 */
export function readHostChannels(host: ChannelSource, bounds: Rect): SurfaceChannelValues {
  const read = (property: string): string => host.style.getPropertyValue(property);

  const pressX = read(GLASS_CHANNEL_PROPERTIES.pressX);
  const pressY = read(GLASS_CHANNEL_PROPERTIES.pressY);
  const hasPressPoint = pressX !== "" && pressY !== "";

  return {
    press: numberFrom(read(GLASS_CHANNEL_PROPERTIES.press), IDLE_CHANNELS.press),
    glow: numberFrom(read(GLASS_CHANNEL_PROPERTIES.glow), IDLE_CHANNELS.glow),
    sweep: numberFrom(read(GLASS_CHANNEL_PROPERTIES.sweep), IDLE_CHANNELS.sweep),
    lensStrength: numberFrom(
      read(GLASS_CHANNEL_PROPERTIES.lensStrength),
      IDLE_CHANNELS.lensStrength,
    ),
    ...(hasPressPoint
      ? {
          pressPoint: [
            bounds.x + numberFrom(pressX, 0),
            bounds.y + numberFrom(pressY, 0),
          ] as readonly [number, number],
        }
      : {}),
  };
}
