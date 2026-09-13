/**
 * The `foregroundTone` channel, consumed (W27e G2; claims §5.140 §7).
 *
 * `vibrancy.test.ts` pins the fold and the driver apart. This file holds the two
 * things that are about the *wiring*: what a surface publishes on its very first
 * frame, and what the driver and the ink function do together across a crossing.
 *
 * **Why the crossing is driven here rather than through a root.** A root would be
 * the better instrument and there is no lever for it: in jsdom every host
 * measures zero, so the size law collapses every surface onto its group's
 * declared backdrop, and a group's backdrop cannot be changed after registration
 * (`registerGroup` refuses a duplicate id). The level a jsdom root can produce is
 * therefore fixed at registration, which is exactly the one thing a crossing has
 * to move. So the crossing is driven through the pair the root composes — the
 * driver, and `foregroundDeclarations` reading its value — with the same
 * threshold substitution `root.ts` performs. The seeding half below *is* at the
 * root, because that is where it lives and because it is where a defect was.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  DEFAULT_MOTION_PROFILE,
  ThresholdCrossfadeDriver,
  type DriverConfig,
} from "@vitrea/motion";

import { foregroundDeclarations, FOREGROUND_INK } from "../src/css-tier";
import { CSS_TIER_MAPPING } from "../src/optics";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassRoot, type GlassRoot } from "../src/root";

const TONE = DEFAULT_MOTION_PROFILE.channels.foregroundTone as Extract<
  DriverConfig,
  { kind: "threshold-crossfade" }
>;

class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

const matcher: MediaMatcher = () => ({
  matches: false,
  media: "(prefers-reduced-motion: reduce)",
  addEventListener: () => {},
  removeEventListener: () => {},
});

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];

/** One surface in one group over a declared backdrop, as the root resolves it. */
function surfaceOver(luminance: number): { ink: () => string; instance: GlassRoot } {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const instance = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
  });
  roots.push(instance);
  const host = document.createElement("button");
  instance.plane("base").hostLayer.append(host);
  instance.registerGroup({
    id: "g1",
    backdrop: { tone: luminance >= 0.5 ? "light" : "dark", luminance },
  });
  instance.registerHost({ host, groupId: "g1", plane: "base", nodeId: "n1" });
  return { ink: () => host.style.getPropertyValue("--vitrea-foreground"), instance };
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

describe("a surface's first frame is not a crossing", () => {
  /*
   * The driver is constructed at one pole, and its committed phase is only set
   * once a level has resolved — which happens inside the tier's own render, after
   * the ink for that frame has already been derived. Handing the ink function the
   * construction value on that frame published the pole the driver happened to be
   * built at rather than the pole the level asks for, so a dark surface's first
   * painted frame showed the dark ink and the second showed the light one, with
   * no transit between them: exactly the flash the seed exists to prevent.
   *
   * Found by these cases. The fix is that the tone is passed only once the driver
   * has a level of its own; before that the ink is selected off the level, as it
   * was before this channel was consumed.
   */
  it("publishes the level's own pole from the very first frame, on both poles", () => {
    for (let time = 0; time <= 64; time += 16) {
      const dark = surfaceOver(0);
      dark.instance.runFrame(time);
      expect(dark.ink(), `dark backdrop at ${String(time)}ms`).toBe(FOREGROUND_INK.light);

      const light = surfaceOver(1);
      light.instance.runFrame(time);
      expect(light.ink(), `light backdrop at ${String(time)}ms`).toBe(FOREGROUND_INK.dark);
    }
  });

  it("never publishes a fold on a surface that has not crossed anything", () => {
    // Every frame of a settled surface is exactly a pole. A fold here would mean
    // the driver was mid-transit on a level that never moved.
    const { ink, instance } = surfaceOver(0);
    for (let time = 0; time <= 400; time += 16) {
      instance.runFrame(time);
      expect(ink(), `at ${String(time)}ms`).toBe(FOREGROUND_INK.light);
    }
  });
});

describe("the ink transits between the poles instead of snapping", () => {
  const driver = (): ThresholdCrossfadeDriver =>
    new ThresholdCrossfadeDriver(
      { ...TONE, threshold: CSS_TIER_MAPPING.foregroundCrossover },
      1,
    );
  const inkAt = (level: number, tone: number): string =>
    foregroundDeclarations({ policy: NOMINAL_ACCESSIBILITY_POLICY, level, tone })[
      "--vitrea-foreground"
    ] as string;
  const red = (declaration: string): number =>
    Number(/^rgb\((\d+) /.exec(declaration)?.[1] ?? Number.NaN);

  it("holds inside the dead band and crosses outside it", () => {
    const crossover = CSS_TIER_MAPPING.foregroundCrossover;
    const half = TONE.hysteresis / 2;
    const tone = driver();

    // A level that has crossed the crossover but not the band leaves the ink
    // where it is — which is the whole reason a drifting backdrop cannot pump it.
    tone.retarget(crossover - half);
    tone.advance(1000);
    expect(inkAt(crossover - half, tone.value)).toBe(FOREGROUND_INK.dark);

    tone.retarget(crossover - half - 1e-6);
    tone.advance(1000);
    expect(inkAt(crossover - half - 1e-6, tone.value)).toBe(FOREGROUND_INK.light);
  });

  it("crosses over the channel's 180 ms, monotonically, and lands exactly", () => {
    const tone = driver();
    tone.retarget(0);

    const seen: string[] = [];
    let previous = red(inkAt(0.2, tone.value));
    expect(previous).toBe(0);
    for (let step = 0; step < 12; step += 1) {
      tone.advance(16);
      const declaration = inkAt(0.2, tone.value);
      seen.push(declaration);
      expect(red(declaration)).toBeGreaterThanOrEqual(previous);
      previous = red(declaration);
    }

    const between = seen.filter(
      (value) => value !== FOREGROUND_INK.dark && value !== FOREGROUND_INK.light,
    );
    // 180 ms at 16 ms a frame is eleven frames of fold and one of arrival.
    expect(between.length).toBe(11);
    expect(between[0]).toMatch(/^rgb\(\d+ \d+ \d+ \/ [\d.]+\)$/);
    expect(seen.at(-1)).toBe(FOREGROUND_INK.light);
  });

  it("reverses from wherever it is, without a jump", () => {
    // The driver reverses rather than restarting and the fold is order-free, so a
    // crossing that turns back mid-transit is continuous. A fold whose layer
    // order followed the direction would pop at exactly this moment.
    const tone = driver();
    tone.retarget(0);
    for (let step = 0; step < 5; step += 1) tone.advance(16);
    const midway = red(inkAt(0.2, tone.value));
    expect(midway).toBeGreaterThan(0);
    expect(midway).toBeLessThan(255);

    tone.retarget(1);
    tone.advance(16);
    // One frame's worth of the transit and not a jump: 16 ms of 180 cannot move
    // the fold more than a tenth of the way, and a tenth of 0 → 255 is 26.
    expect(Math.abs(red(inkAt(0.9, tone.value)) - midway)).toBeLessThan(40);
    for (let step = 0; step < 12; step += 1) tone.advance(16);
    expect(inkAt(0.9, tone.value)).toBe(FOREGROUND_INK.dark);
  });
});
