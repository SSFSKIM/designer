/**
 * Gyre. The field is the ground, the glass is the chrome, and the reading column
 * on the left holds either the statement or a sheet. Composed under `DESIGN.md`.
 */

import { useGlassAccessibility } from "@vitreajs/vitrea-react";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { formatLat, formatLon, type Station } from "./data";
import { createClock } from "./field/clock";
import { Field } from "./field/Field";
import { layerById, type LayerId } from "./field/palettes";
import { LayerControl } from "./glass/LayerControl";
import { LayerMenu, type MenuAction } from "./glass/LayerMenu";
import { Nav } from "./glass/Nav";
import { Probe, type ProbeHandle } from "./glass/Probe";
import { SCRUB_LIMIT_HOURS, Transport } from "./glass/Transport";
import { Hero } from "./Hero";
import { isNarrow, NARROW_BREAKPOINT } from "./layout";
import { AccessSheet } from "./sheets/AccessSheet";
import { MethodSheet } from "./sheets/MethodSheet";
import { RenderingSheet, type Overrides } from "./sheets/RenderingSheet";
import type { SheetId } from "./sheets/Sheet";
import { StationsSheet } from "./sheets/StationsSheet";

export interface AppProps {
  readonly requestedRenderer: "css" | "webgpu";
  readonly overrides: Overrides;
  readonly onOverridesChange: (next: Overrides) => void;
}

const SHEET_ACTIONS: readonly MenuAction[] = [
  { id: "stations", label: "Stations" },
  { id: "method", label: "Method" },
  { id: "rendering", label: "Rendering" },
];

const FIELD_ACTIONS: readonly MenuAction[] = [
  { id: "export", label: "Export field as GeoTIFF" },
  { id: "copy", label: "Copy probe position" },
  { id: "share", label: "Share this view" },
  { id: "reset", label: "Centre the probe" },
];

function useNarrow(): boolean {
  const [narrow, setNarrow] = useState(() => isNarrow(window.innerWidth));
  useEffect(() => {
    const query = window.matchMedia(`(max-width: ${NARROW_BREAKPOINT - 1}px)`);
    const update = (): void => setNarrow(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  return narrow;
}

export function App(props: AppProps): ReactNode {
  const clock = useMemo(createClock, []);
  const [layer, setLayer] = useState<LayerId>("currents");
  const [sheet, setSheet] = useState<SheetId | null>(null);
  const [playing, setPlaying] = useState(true);
  const [offsetHours, setOffsetHours] = useState(0);
  const [fieldFallback, setFieldFallback] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const probe = useRef<ProbeHandle>(null);
  const narrow = useNarrow();
  const policy = useGlassAccessibility();
  const animate = policy === undefined ? true : !policy.reducedMotion;

  useEffect(() => {
    clock.playing = playing;
  }, [clock, playing]);
  useEffect(() => {
    clock.offsetHours = offsetHours;
  }, [clock, offsetHours]);

  const closeSheet = useCallback(() => setSheet(null), []);
  const onFallback = useCallback((fallback: boolean) => setFieldFallback(fallback), []);

  const scrub = (delta: number): void =>
    setOffsetHours((current) =>
      Math.max(-SCRUB_LIMIT_HOURS, Math.min(SCRUB_LIMIT_HOURS, current + delta)),
    );

  const locate = (station: Station, u: number, v: number): void => {
    probe.current?.moveTo(u, v);
    setNotice(`Probe at ${station.id}, ${formatLat(station.lat)} ${formatLon(station.lon)}.`);
    if (narrow) setSheet(null);
  };

  const onAction = (id: string): void => {
    switch (id) {
      case "stations":
      case "method":
      case "rendering":
        setSheet(id);
        break;
      case "export":
        setNotice(`Export queued: gyre-${layer}-20260904-1120.tif, 0.08° grid.`);
        break;
      case "copy": {
        const text = document.querySelector(".probe__position")?.textContent ?? "";
        void navigator.clipboard?.writeText(text).catch(() => undefined);
        setNotice(text === "" ? "Nothing to copy yet." : `Copied ${text}.`);
        break;
      }
      case "share":
        setNotice("Share link ready: gyre.app/v/kuroshio-20260904-1120.");
        break;
      case "reset":
        probe.current?.reset();
        setNotice("Probe centred.");
        break;
      default:
        break;
    }
  };

  const fieldLayer = layerById(layer);
  const menuActions = narrow ? [...SHEET_ACTIONS, ...FIELD_ACTIONS] : FIELD_ACTIONS;

  return (
    <>
      <Field layer={layer} clock={clock} animate={animate} onFallback={onFallback} />
      {fieldFallback ? (
        <div
          className="field field--fallback"
          aria-hidden="true"
          style={{
            background: `linear-gradient(135deg, ${fieldLayer.stops.map((stop) => stop.hex).join(", ")})`,
          }}
        />
      ) : null}

      <main className="column">
        {sheet === null ? <Hero layer={fieldLayer} offsetHours={offsetHours} playing={playing} /> : null}
        {sheet === "stations" ? <StationsSheet onClose={closeSheet} onLocate={locate} /> : null}
        {sheet === "method" ? <MethodSheet onClose={closeSheet} /> : null}
        {sheet === "rendering" ? (
          <RenderingSheet
            requestedRenderer={props.requestedRenderer}
            fieldFallback={fieldFallback}
            overrides={props.overrides}
            onOverridesChange={props.onOverridesChange}
            onClose={closeSheet}
          />
        ) : null}
        {sheet === "access" ? <AccessSheet onClose={closeSheet} /> : null}
      </main>

      <p className="notice" role="status" aria-live="polite">
        {notice ?? ""}
      </p>

      <Nav sheet={sheet} narrow={narrow} onSheet={setSheet} />
      <Probe ref={probe} layer={layer} clock={clock} narrow={narrow} hidden={narrow && sheet !== null} />
      <Transport
        playing={playing}
        offsetHours={offsetHours}
        onTogglePlaying={() => setPlaying((current) => !current)}
        onScrub={scrub}
        onNow={() => setOffsetHours(0)}
      />
      <LayerControl value={layer} onChange={setLayer} />
      {/*
        The morph's closed end is a spacer laid out where the app puts it, and the
        platter follows that spacer. This anchor is the one piece of app DOM that
        positions glass; it is last so the platter is the last host registered.
      */}
      <div className="menu-anchor">
        <LayerMenu
          label="Actions"
          actions={menuActions}
          placement={narrow ? "below-end" : "above-end"}
          onAction={onAction}
        />
      </div>
    </>
  );
}
