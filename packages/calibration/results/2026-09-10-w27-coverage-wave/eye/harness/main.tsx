/**
 * The eye-sheet harness entry.
 *
 * `?scheme=light|dark` picks the material's colour scheme *and* the page's own
 * ground, because a sheet compares the material under one scheme at a time.
 *
 * `?stepped=1` hands the frame loop to the capture script. `GlassRoot
 * autoStart={false}` stops the root's `requestAnimationFrame`, and
 * `window.__eye.step(dt)` runs exactly one frame — `root.runFrame(clock)` for
 * the scene and the material, then `ticker.advance(dt)` for the bindings'
 * springs, which is the order the root itself uses. A transition strip captured
 * this way carries the frame's own time rather than the time at which a
 * screenshot happened to be taken, and it is the *shipped* timing: nothing here
 * changes a duration or an easing.
 *
 * The renderer is asked for as `webgpu` and the harness publishes what each
 * group resolved to; the capture script refuses a panel that did not reach the
 * GPU tier.
 */

import { GlassRoot, useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { StrictMode, useEffect, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import "./eye.css";
import { Eye } from "./Eye";

const params = new URLSearchParams(window.location.search);
const scheme: "light" | "dark" = params.get("scheme") === "dark" ? "dark" : "light";
const stepped = params.get("stepped") === "1";

document.documentElement.dataset["eyeScheme"] = scheme;

/** The hand-driven clock, outside the effect so a re-render never rewinds it. */
let clock = 0;
const FRAME = 1000 / 60;

function Stepper(): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();

  useEffect(() => {
    if (root === null) return;
    const step = (dtMs: number): number => {
      clock += dtMs;
      root.runFrame(clock);
      ticker.advance(dtMs);
      return clock;
    };
    const api = {
      ready: () => root.ready(),
      step,
      /** Whole frames until `ms` of frame time has passed, at the 60 Hz cadence. */
      run(ms: number): number {
        let spent = 0;
        while (spent + FRAME <= ms + 1e-9) {
          step(FRAME);
          spent += FRAME;
        }
        if (ms - spent > 1e-9) step(ms - spent);
        return clock;
      },
      settle: (frames = 150) => {
        for (let i = 0; i < frames; i += 1) step(FRAME);
        return clock;
      },
      clock: () => clock,
    };
    Object.assign(window, { __eye: api });
    return () => {
      delete (window as unknown as Record<string, unknown>)["__eye"];
    };
  }, [root, ticker]);

  return null;
}

const container = document.getElementById("root");
if (container === null) throw new Error("no #root");

createRoot(container).render(
  <StrictMode>
    <GlassRoot renderer="webgpu" colorScheme={scheme} autoStart={!stepped}>
      {stepped ? <Stepper /> : null}
      <Eye scheme={scheme} />
    </GlassRoot>
  </StrictMode>,
);
