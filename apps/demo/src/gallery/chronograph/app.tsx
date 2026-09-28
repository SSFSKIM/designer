/**
 * The page: the bench and the watch in one painted canvas, the crystal and the loupe over it, and
 * the chronograph's glass controls beside it.
 *
 * State that the scene reads every frame (the chronograph, the loupe's position) is mirrored into
 * a ref the root's loop reads, so a beat of the movement never re-renders React. The audit
 * contract (`window.__glassDemo`) is published here.
 */

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  useGlassAccessibility,
  useGlassRootHandle,
  useGlassWindowActivation,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { INITIAL, lapOrReset, startStop, type ChronoState } from "./chrono";
import { CrystalMenu, DialSwitch, Pushers, TimingWindow } from "./controls";
import { computeLayout, derivedGaps, type Box, type Circle, type CrystalId } from "./layout";
import { constrainLoupe, Crystal, Loupe } from "./optics";
import { paletteFor, type Scheme } from "./palette";
import type { Scene } from "./scene";
import { SceneCanvas, type SceneInputs } from "./scene-canvas";
import { crystalById, crystalThickness } from "./shared";

function useViewport(): { width: number; height: number } {
  const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  useEffect(() => {
    const onResize = (): void => setSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return size;
}

/** A hint the page measured: the relative luminance painted under a box. */
const hintOf = (luminance: number): BackdropHint => ({
  tone: luminance >= 0.18 ? "light" : "dark",
  luminance: Math.round(luminance * 1000) / 1000,
});

export function App(props: {
  readonly scheme: Scheme;
  readonly onScheme: (scheme: Scheme) => void;
  readonly crystal: CrystalId;
  readonly onCrystal: (id: CrystalId) => void;
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { scheme, crystal } = props;
  const { root, materialProfileDocument } = useGlassRootHandle();
  const accessibility = useGlassAccessibility();
  const viewport = useViewport();
  const material = accessibility?.material ?? NOMINAL_ACCESSIBILITY_POLICY.material;
  const gap = useMemo(
    () => derivedGaps(materialProfileDocument, scheme, material, viewport),
    [materialProfileDocument, scheme, material, viewport],
  );
  const layout = useMemo(
    () => computeLayout(viewport.width, viewport.height, gap),
    [viewport.width, viewport.height, gap],
  );
  const palette = paletteFor(scheme);

  const [chrono, setChrono] = useState<ChronoState>(INITIAL);
  const [loupe, setLoupe] = useState<Circle>(layout.loupeRest);
  const [menuOpen, setMenuOpen] = useState(false);
  const [hints, setHints] = useState<Record<string, BackdropHint>>({});

  // A new layout puts the loupe back on its rest if it no longer fits where it was.
  useEffect(() => {
    setLoupe((current) => constrainLoupe(layout, { ...current, r: layout.loupeRest.r }));
  }, [layout]);

  // The lenses step aside wherever the material would otherwise fog or vanish over the dial.
  const activation = useGlassWindowActivation();
  const lensesYield =
    props.reducedTransparency || material.glass === "none" || activation === "inactive";

  const inputs = useRef<SceneInputs>({ chrono, loupe, lensesYield });
  inputs.current = { chrono, loupe, lensesYield };

  const moveLoupe = useCallback((next: Circle) => {
    inputs.current = { ...inputs.current, loupe: next };
    setLoupe(next);
  }, []);

  const onStartStop = useCallback(() => setChrono((s) => startStop(s, performance.now())), []);
  const onLapReset = useCallback(() => setChrono((s) => lapOrReset(s, performance.now())), []);

  // Keyboard: Space runs and stops, L takes a lap, R resets, wherever focus is not already a control.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      const target = event.target as HTMLElement | null;
      if (target?.closest("button, input, [role='radio'], [role='dialog']") != null) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      if (event.key === " ") event.preventDefault();
      // A held key repeats. A pusher acts once per press, so a repeat must not toggle the
      // chronograph or fill the laps while the key is down. The loupe's arrow keys are its own
      // handler's and keep repeating.
      if (event.repeat) return;
      if (event.key === " ") {
        onStartStop();
      } else if (event.key === "l" || event.key === "L") {
        setChrono((s) => (s.running ? lapOrReset(s, performance.now()) : s));
      } else if (event.key === "r" || event.key === "R") {
        setChrono((s) => (s.running ? s : lapOrReset(s, performance.now())));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onStartStop]);

  // The hints: what is painted under each control's own box, measured once the scene has painted.
  const onPrepared = useCallback(
    (scene: Scene) => {
      const pad = (b: Box, by = 8): Box => ({ x: b.x - by, y: b.y - by, width: b.width + by * 2, height: b.height + by * 2 });
      const around = (c: Circle): Box => ({ x: c.cx - c.r, y: c.cy - c.r, width: c.r * 2, height: c.r * 2 });
      setHints({
        dial: hintOf(scene.measure(pad(layout.dial))),
        "crystal-menu": hintOf(scene.measure(pad(layout.crystalMenu))),
        timing: hintOf(scene.measure(layout.timing)),
        lap: hintOf(scene.measure(around(layout.lapButton))),
        start: hintOf(scene.measure(around(layout.startButton))),
      });
    },
    [layout],
  );

  // The crystal menu remounts closed when Reduce Motion changes (a tracked runtime seam).
  const morphKey = `menu-${accessibility?.reducedMotion === true ? "rm" : "m"}-${layout.mode}`;
  useEffect(() => setMenuOpen(false), [morphKey]);

  // The audit contract.
  useEffect(() => {
    const demo = {
      openMenu: () => setMenuOpen(true),
      setReducedTransparency: (value: boolean) => props.onReducedTransparency(value),
      phases: () => ["day", "night", "running", "loupe-on-dial"],
      setPhase: (id: string) => {
        if (id === "day") props.onScheme("light");
        if (id === "night") props.onScheme("dark");
        if (id === "running") setChrono((s) => (s.running ? s : startStop(s, performance.now() - 83_420)));
        if (id === "loupe-on-dial") {
          const { cx, cy, r } = layout.watch;
          moveLoupe(constrainLoupe(layout, { cx: cx + r * 0.02, cy: cy + r * 0.56, r: layout.loupeRest.r }));
        }
      },
    };
    (window as unknown as { __glassDemo: typeof demo }).__glassDemo = demo;
    (window as unknown as { __vitrea: unknown }).__vitrea = root;
  }, [root, layout, moveLoupe, props]);

  const current = crystalById(crystal);

  return (
    <>
      <SceneCanvas layout={layout} palette={palette} inputs={inputs} onPrepared={onPrepared} />
      <Crystal circle={layout.crystal} thickness={crystalThickness(current, layout)} present={!lensesYield} />
      <DialSwitch box={layout.dial} scheme={scheme} hint={hints.dial} onScheme={props.onScheme} />
      <CrystalMenu
        anchor={layout.crystalMenu}
        crystal={crystal}
        hint={hints["crystal-menu"]}
        open={menuOpen}
        morphKey={morphKey}
        reducedTransparency={props.reducedTransparency}
        onOpenChange={setMenuOpen}
        onCrystal={props.onCrystal}
        onReducedTransparency={props.onReducedTransparency}
      />
      <TimingWindow box={layout.timing} chrono={chrono} hint={hints.timing} />
      <Pushers
        lap={layout.lapButton}
        start={layout.startButton}
        chrono={chrono}
        hint={hints.start}
        onStartStop={onStartStop}
        onLapReset={onLapReset}
      />
      <Loupe layout={layout} circle={loupe} present={!lensesYield} onMove={moveLoupe} />
    </>
  );
}
