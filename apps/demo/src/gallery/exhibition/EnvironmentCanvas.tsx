/**
 * The environment's canvas, and the dissolve between works.
 *
 * A change of work is a state change of the environment, never the glass moving: the canvas
 * cross-dissolves over `DISSOLVE_MS`, stepped from the root's own frame loop (`root.subscribe`,
 * so there is no second rAF loop beside the runtime's), and every frame of it re-measures what
 * was painted under each group, so each declared backdrop describes the painted mix and not its
 * destination. Reduce Motion, read live from the resolved policy, makes the dissolve a cut; so
 * does `setPhase`, which must show a work within two frames.
 */

import { useGlassRoot } from "@vitreajs/vitrea-react";
import { useEffect, useLayoutEffect, useRef, type ReactNode } from "react";

import {
  EnvironmentPainter,
  type Footprint,
  type FootprintReading,
  type Scheme,
} from "./painter";
import { WORKS, type Work } from "./works";

const DISSOLVE_MS = 700;

export const TEXTURE_ID = "environment";

interface DissolveState {
  from: Work;
  to: Work | undefined;
  mix: number;
}

export interface EnvironmentProps {
  readonly work: Work;
  /** Cut rather than dissolve to this work (a `setPhase`, a deep link, the first paint). */
  readonly instant: boolean;
  readonly reducedMotion: boolean;
  readonly scheme: Scheme;
  readonly footprints: Readonly<Record<string, Footprint>>;
  readonly onReadings: (readings: Record<string, FootprintReading>, sourceMean: number) => void;
}

export function EnvironmentCanvas(props: EnvironmentProps): ReactNode {
  const { work, instant, reducedMotion, scheme, footprints } = props;
  const root = useGlassRoot();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const painterRef = useRef<EnvironmentPainter | null>(null);
  const dissolve = useRef<DissolveState>({ from: work, to: undefined, mix: 0 });
  const stopDissolve = useRef<(() => void) | undefined>(undefined);
  /** Bumped by every change of work, so an image that decodes late cannot start a stale one. */
  const navigation = useRef(0);
  const latest = useRef({ scheme, footprints, onReadings: props.onReadings, root });
  latest.current = { scheme, footprints, onReadings: props.onReadings, root };

  const paint = useRef((): void => {
    const painter = painterRef.current;
    if (painter === null) return;
    const { scheme: s, footprints: f, onReadings } = latest.current;
    const painted = painter.paint({ ...dissolve.current, scheme: s, footprints: f });
    if (painted !== undefined) onReadings(painted.readings, painted.source);
  });

  // The painter, and every image: the current work first, the other seven after it, so a visit
  // to the next room dissolves at once rather than waiting on a download.
  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    const painter = new EnvironmentPainter(canvas);
    painterRef.current = painter;
    const first = dissolve.current.from;
    void painter.load(first).then(() => {
      if (painterRef.current === painter) paint.current();
      for (const other of WORKS) if (other.id !== first.id) void painter.load(other);
    });
    return () => {
      stopDissolve.current?.();
      painterRef.current = null;
    };
  }, []);

  // The canvas is the texture: supplied once, re-imported by the runtime every frame it samples.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (root === null || canvas === null) return;
    root.setBackdropTexture(TEXTURE_ID, { kind: "canvas", canvas });
    return () => root.setBackdropTexture(TEXTURE_ID, undefined);
  }, [root]);

  // A change of work.
  useLayoutEffect(() => {
    const painter = painterRef.current;
    const current = dissolve.current;
    const showing = current.to ?? current.from;
    if (painter === null || work.id === showing.id) return;
    stopDissolve.current?.();
    stopDissolve.current = undefined;
    navigation.current += 1;
    const token = navigation.current;

    const cut = (): void => {
      dissolve.current = { from: work, to: undefined, mix: 0 };
      paint.current();
    };
    const host = latest.current.root;
    if (instant || reducedMotion || host === null) {
      dissolve.current = { from: work, to: undefined, mix: 0 };
      if (painter.isLoaded(work)) cut();
      else
        void painter.load(work).then(() => {
          if (token === navigation.current) cut();
        });
      return;
    }

    const begin = (): void => {
      // An interrupted dissolve commits to where it was going and starts again from there.
      const from = dissolve.current.to ?? dissolve.current.from;
      dissolve.current = { from, to: work, mix: 0 };
      let elapsed = 0;
      const unsubscribe = host.subscribe(({ deltaMs }) => {
        elapsed += Math.min(deltaMs, 50);
        const u = Math.min(1, elapsed / DISSOLVE_MS);
        dissolve.current.mix = u * u * (3 - 2 * u);
        if (u >= 1) {
          dissolve.current = { from: work, to: undefined, mix: 0 };
          unsubscribe();
          if (stopDissolve.current === unsubscribe) stopDissolve.current = undefined;
        }
        paint.current();
      });
      stopDissolve.current = unsubscribe;
    };
    if (painter.isLoaded(work)) begin();
    else
      void painter.load(work).then(() => {
        if (token === navigation.current) begin();
      });
  }, [work, instant, reducedMotion]);

  // A new scheme or a new layout re-grades and re-measures at once.
  useLayoutEffect(() => {
    paint.current();
  }, [scheme, footprints]);

  return (
    <canvas
      ref={canvasRef}
      className="exh-environment"
      role="img"
      aria-label={`${work.title}, ${work.artist}, ${work.date}. ${work.alt}`}
    />
  );
}
