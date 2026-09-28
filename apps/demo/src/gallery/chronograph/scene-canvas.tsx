/**
 * The bench canvas: the scene painted from the root's own frame loop and handed to the runtime as
 * the texture every glass group reads.
 *
 * One loop, the root's (`root.subscribe`), never a second requestAnimationFrame beside it. The
 * scene repaints only when what it shows has changed: a beat of the movement, a move of the loupe,
 * a new layout or dial. Between those the runtime re-imports the same canvas.
 */

import { useGlassRoot } from "@vitreajs/vitrea-react";
import { useEffect, useLayoutEffect, useRef, type RefObject, type ReactNode } from "react";

import { chronoAngles, type ChronoState } from "./chrono";
import type { Circle, Layout } from "./layout";
import type { Palette } from "./palette";
import { Scene } from "./scene";
import { BENCH_TEXTURE } from "./shared";

export interface SceneInputs {
  readonly chrono: ChronoState;
  readonly loupe: Circle;
  /** The two lenses have stepped aside (scene.ts): the loupe is drawn as a ring on the bench. */
  readonly lensesYield: boolean;
}

const TAU = Math.PI * 2;

export function SceneCanvas(props: {
  readonly layout: Layout;
  readonly palette: Palette;
  readonly inputs: RefObject<SceneInputs>;
  /** Called once the scene has painted for a new layout or dial, so hints can be re-measured. */
  readonly onPrepared: (scene: Scene) => void;
}): ReactNode {
  const { layout, palette, inputs, onPrepared } = props;
  const root = useGlassRoot();
  const canvas = useRef<HTMLCanvasElement>(null);
  const scene = useRef<Scene | null>(null);
  const dirty = useRef(true);
  const onPreparedRef = useRef(onPrepared);
  onPreparedRef.current = onPrepared;

  useLayoutEffect(() => {
    if (canvas.current === null) return;
    const s = scene.current ?? new Scene(canvas.current);
    scene.current = s;
    s.prepare(layout, palette, Math.min(window.devicePixelRatio || 1, 2));
    dirty.current = true;
  }, [layout, palette]);

  useEffect(() => {
    if (root === null || canvas.current === null) return;
    root.setBackdropTexture(BENCH_TEXTURE, { kind: "canvas", canvas: canvas.current });
    return () => root.setBackdropTexture(BENCH_TEXTURE, undefined);
  }, [root]);

  useEffect(() => {
    if (root === null) return;
    let lastKey = "";
    let prepared = false;
    return root.subscribe(() => {
      const s = scene.current;
      if (s === null) return;
      const now = performance.now();
      const clock = new Date();
      const { chrono, loupe, lensesYield } = inputs.current;
      const beat = Math.floor(Date.now() / 125);
      const key = `${beat}|${loupe.cx.toFixed(1)}|${loupe.cy.toFixed(1)}|${chrono.running}|${chrono.banked}|${chrono.laps.length}|${lensesYield}`;
      if (!dirty.current && key === lastKey) return;
      lastKey = key;
      const wasDirty = dirty.current;
      dirty.current = false;
      const ms = clock.getMilliseconds();
      const seconds = clock.getSeconds() + Math.floor(ms / 125) / 8;
      const minutes = clock.getMinutes() + seconds / 60;
      const hours = (clock.getHours() % 12) + minutes / 60;
      const c = chronoAngles(chrono, now);
      s.paint({
        hands: {
          hour: (hours / 12) * TAU,
          minute: (minutes / 60) * TAU,
          smallSeconds: (seconds / 60) * TAU,
          chrono: c.chrono,
          split: c.split,
          chronoMinutes: c.minutes,
          chronoHours: c.hours,
        },
        date: clock.getDate(),
        loupe,
        loupeRing: lensesYield,
      });
      if (wasDirty || !prepared) {
        prepared = true;
        onPreparedRef.current(s);
      }
    });
  }, [root, inputs]);

  return <canvas ref={canvas} className="bench" aria-hidden="true" />;
}
