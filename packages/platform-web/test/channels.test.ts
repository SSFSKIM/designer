/**
 * The channel vocabulary, read back off a host.
 *
 * The values a binding publishes are the values the GPU draws with, so what is
 * pinned here is the round trip: what `style.setProperty` wrote comes back as a
 * number, an unwritten property comes back as its idle value rather than as
 * `NaN`, and a press point lands in viewport coordinates.
 */

import { describe, expect, it } from "vitest";

import {
  GLASS_CHANNEL_PROPERTIES,
  IDLE_CHANNELS,
  readHostChannels,
  type ChannelSource,
} from "../src/channels";

const BOUNDS = { x: 120, y: 40, width: 200, height: 60 };

/** A host with nothing on it — the shape `document.createElement` starts in. */
const bare = (): ChannelSource => ({ style: { getPropertyValue: () => "" } });

const withChannels = (declared: Record<string, string>): ChannelSource => ({
  style: { getPropertyValue: (property) => declared[property] ?? "" },
});

describe("readHostChannels", () => {
  it("reads what a binding published", () => {
    const channels = readHostChannels(
      withChannels({
        [GLASS_CHANNEL_PROPERTIES.press]: "0.4210",
        [GLASS_CHANNEL_PROPERTIES.glow]: "0.8000",
        [GLASS_CHANNEL_PROPERTIES.sweep]: "0.2500",
        [GLASS_CHANNEL_PROPERTIES.lensStrength]: "1.0600",
      }),
      BOUNDS,
    );

    expect(channels.press).toBeCloseTo(0.421, 6);
    expect(channels.glow).toBeCloseTo(0.8, 6);
    expect(channels.sweep).toBeCloseTo(0.25, 6);
    expect(channels.lensStrength).toBeCloseTo(1.06, 6);
  });

  it("falls back to idle for an undriven surface", () => {
    // A decorative surface has no interaction machine at all, so none of these
    // properties is ever written. Idle is a legal state with defined values —
    // and `lensStrength` idles at 1, because a surface nobody is animating still
    // refracts.
    expect(readHostChannels(bare(), BOUNDS)).toEqual(IDLE_CHANNELS);
  });

  it("falls back rather than propagating NaN from an unparseable value", () => {
    // A `NaN` reaching a uniform blanks a whole pass with no error anywhere.
    const channels = readHostChannels(
      withChannels({ [GLASS_CHANNEL_PROPERTIES.press]: "inherit" }),
      BOUNDS,
    );
    expect(channels.press).toBe(IDLE_CHANNELS.press);
  });

  it("lifts the press point out of host-local coordinates", () => {
    // A binding measures the point against the host's own border box; the
    // renderer places its glow in viewport space, which is the space every
    // measured rect is already in.
    const channels = readHostChannels(
      withChannels({
        [GLASS_CHANNEL_PROPERTIES.pressX]: "30.0000px",
        [GLASS_CHANNEL_PROPERTIES.pressY]: "12.0000px",
      }),
      BOUNDS,
    );

    expect(channels.pressPoint).toEqual([150, 52]);
  });

  it("treats a half-written press point as absent", () => {
    // One axis is not a point. Defaulting the other to zero would put the glow
    // on the surface's edge, which reads as a bug rather than as no press.
    const channels = readHostChannels(
      withChannels({ [GLASS_CHANNEL_PROPERTIES.pressX]: "30.0000px" }),
      BOUNDS,
    );

    expect(channels.pressPoint).toBeUndefined();
  });

  it("survives the round trip through a real element's inline style", () => {
    // The reason this seam costs no layout: `setProperty` and `getPropertyValue`
    // are the same inline declaration block, never the cascade.
    const host = document.createElement("button");
    host.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, "0.5000");
    host.style.setProperty(GLASS_CHANNEL_PROPERTIES.pressX, "10.0000px");
    host.style.setProperty(GLASS_CHANNEL_PROPERTIES.pressY, "20.0000px");

    const channels = readHostChannels(host, BOUNDS);

    expect(channels.glow).toBeCloseTo(0.5, 6);
    expect(channels.pressPoint).toEqual([130, 60]);
  });
});
