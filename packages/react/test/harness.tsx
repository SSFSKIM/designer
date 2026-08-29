/**
 * One place for the wiring every binding test needs, so the tests themselves
 * read as assertions rather than as setup.
 *
 * Roots are always `autoStart={false}`: a test that races an animation frame is
 * a test that fails on a slow machine. Frames and ticks are stepped by hand
 * through the handle below, which is also the shape an app driving vitrea from
 * its own clock uses.
 */

import { render, type RenderResult } from "@testing-library/react";
import { act } from "react";
import type { ReactNode } from "react";

import { GlassRoot, useGlassRoot, useGlassTicker, type GlassRootProps } from "../src/index";
import type { GlassRoot as PlatformGlassRoot } from "@vitreajs/vitrea-web";
import type { GlassTicker } from "../src/ticker";

export interface Harness {
  readonly result: RenderResult;
  root(): PlatformGlassRoot;
  /** One scene frame: measure, resolve, write. */
  frame(timeMs?: number): void;
  /** One motion step, in milliseconds. */
  tick(dtMs: number): void;
  /** `frame` then `tick`, `count` times — the ordering the live loops produce. */
  run(count: number, dtMs?: number): void;
}

interface CaptureProps {
  readonly onReady: (root: PlatformGlassRoot | null, ticker: GlassTicker) => void;
}

function Capture(props: CaptureProps): ReactNode {
  props.onReady(useGlassRoot(), useGlassTicker());
  return null;
}

export function renderGlass(
  children: ReactNode,
  rootProps: Omit<GlassRootProps, "children"> = {},
): Harness {
  let platformRoot: PlatformGlassRoot | null = null;
  let ticker: GlassTicker | null = null;

  const result = render(
    <GlassRoot autoStart={false} {...rootProps}>
      <Capture
        onReady={(next, nextTicker) => {
          platformRoot = next;
          ticker = nextTicker;
        }}
      />
      {children}
    </GlassRoot>,
  );

  let elapsed = 0;

  const harness: Harness = {
    result,
    root() {
      if (platformRoot === null) throw new Error("The glass root was not created.");
      return platformRoot;
    },
    frame(timeMs) {
      elapsed = timeMs ?? elapsed + 16;
      act(() => {
        harness.root().runFrame(elapsed);
      });
    },
    tick(dtMs) {
      act(() => {
        ticker?.advance(dtMs);
      });
    },
    run(count, dtMs = 16) {
      for (let i = 0; i < count; i += 1) {
        harness.frame(elapsed + dtMs);
        harness.tick(dtMs);
      }
    },
  };

  return harness;
}

/** Every glass host currently registered, in the DOM order the sandwich uses. */
export function hostsIn(root: PlatformGlassRoot, plane: "base" | "overlay" = "base"): Element[] {
  return [...root.plane(plane).hostLayer.querySelectorAll("[data-vitrea-node]")];
}
