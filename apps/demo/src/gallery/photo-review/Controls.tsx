/**
 * The floating layer: three surfaces, and nothing else on glass (`DESIGN.md`, the record).
 *
 * - The tool palette, which is also the adjustment platter: one `GlassMorph` host for its
 *   whole life. Closed it is a 52 x 140 vertical capsule of three tools (r26, half its span);
 *   open it is the same host grown leftward into a 340 x 244 platter, its tool column held in
 *   place at the right edge so the tools never move under the pointer. `placement="below-end"`
 *   with a gap of minus the palette's own height is what puts the platter's top-right corner on
 *   the palette's, so the morph grows in place rather than dropping below its trigger like a
 *   menu. Those are border-box sizes on both tiers (`styles.css`, `.tools-host`). The open
 *   platter's plain controls press its material through the host's channels (`press.ts`).
 * - The compare toggle, a `GlassSegmentedControl` capsule.
 * - The verdict bar, one capsule host whose buttons are fills: reject, rating, pick.
 *
 * Everything inside a surface is a plain button, a range input or a fill, never a host: the
 * surface is already the material. Ink is the pole of the runtime's published primary, at full
 * strength, on child elements (`styles.css`, `--label`).
 */
import {
  GlassMorph,
  GlassSegmentedControl,
  GlassSurface,
} from "@vitreajs/vitrea-react";
import { useId, useRef, type CSSProperties, type KeyboardEvent, type ReactNode } from "react";

import type { Aspect, Develop, Flag, Frame } from "./data";
import { CropIcon, ExposureIcon, PickIcon, RejectIcon, StarIcon, WhiteBalanceIcon } from "./icons";
import { usePlatterPress } from "./press";

export type Tool = "exposure" | "white-balance" | "crop";
export type View = "before" | "after";

/**
 * The size family (`DESIGN.md`): S 40 capsule, M 52 capsule, L 340 x 244 at the palette's radius.
 * The palette's radius is half its 52 px span, so the closed end is a capsule as the verdict
 * bar is; that holds because the host is sized as a border box (`styles.css`, `.tools-host`).
 */
export const PALETTE = { w: 52, h: 140, radius: 26 } as const;
export const PLATTER = { w: 340, h: 244 } as const;
export const COMPARE = { w: 166, h: 40 } as const;
export const VERDICT = { w: 278, h: 52 } as const;
export const THICKNESS = 8;

const TOOLS: readonly { id: Tool; label: string; key: string; icon: () => ReactNode }[] = [
  { id: "exposure", label: "Exposure", key: "E", icon: ExposureIcon },
  { id: "white-balance", label: "White balance", key: "W", icon: WhiteBalanceIcon },
  { id: "crop", label: "Crop", key: "R", icon: CropIcon },
];

export interface ToolsProps {
  readonly tool: Tool | null;
  readonly onTool: (tool: Tool | null) => void;
  readonly frame: Frame;
  readonly onDevelop: (patch: Partial<Develop>) => void;
  readonly onAuto: () => void;
  /** Where the closed palette sits, in viewport px. */
  readonly anchor: { readonly x: number; readonly y: number };
  /** The morph reached an end; `App` re-opens a platter it closed when the window moved it. */
  readonly onMorphEnd: (open: boolean) => void;
}

/**
 * The palette and its platter. Focus follows the tool across the content swap: the button the
 * reader pressed unmounts with the closed content, so the matching button in the other end
 * takes focus as it mounts. A swap the palette did not make, a key or the page closing and
 * re-opening the platter because the window moved it, carries focus the same way when focus
 * was on the palette, read before the swap commits because the focused control is about to go.
 */
export function Tools({ tool, onTool, frame, onDevelop, onAuto, anchor, onMorphEnd }: ToolsProps) {
  const focusRequest = useRef<Tool | null>(null);
  const shown = useRef(tool);
  if (shown.current !== tool) {
    const focusOnPalette = document.activeElement?.closest(".tools-host") != null;
    if (focusRequest.current === null && focusOnPalette) focusRequest.current = tool ?? shown.current;
    shown.current = tool;
  }
  const press = usePlatterPress();
  const choose = (next: Tool | null, focus: Tool) => {
    focusRequest.current = focus;
    onTool(next);
  };
  const column = (
    <ToolColumn tool={tool} focusRequest={focusRequest}
      onPress={(t) => choose(tool === t ? null : t, t)} />
  );
  return (
    <div className="palette-anchor" style={{ left: anchor.x, top: anchor.y }}>
      <GlassMorph
        open={tool !== null}
        placement="below-end"
        gap={-PALETTE.h}
        radius={PALETTE.radius}
        openRadius={PALETTE.radius}
        thickness={THICKNESS}
        openThickness={THICKNESS}
        nodeId="tools"
        className="tools-host"
        onMorphEnd={onMorphEnd}
      >
        {({ open }) =>
          open && tool !== null ? (
            <div
              className="platter"
              style={{ width: PLATTER.w, height: PLATTER.h }}
              onPointerDown={press.onPointerDown}
              onKeyUp={press.onKeyUp}
              onBlur={press.onBlur}
              onKeyDown={(event) => {
                press.onKeyDown(event);
                if (event.key !== "Escape") return;
                event.stopPropagation();
                choose(null, tool);
              }}
            >
              <section className="panel" aria-label={TOOLS.find((t) => t.id === tool)?.label}>
                {tool === "exposure" ? (
                  <ExposurePanel develop={frame.develop} onDevelop={onDevelop} onAuto={onAuto} />
                ) : tool === "white-balance" ? (
                  <WhiteBalancePanel develop={frame.develop} asShot={frame.photo.asShotTemp} onDevelop={onDevelop} />
                ) : (
                  <CropPanel develop={frame.develop} onDevelop={onDevelop} onDone={() => choose(null, "crop")} />
                )}
              </section>
              {column}
            </div>
          ) : (
            <div className="palette" style={{ width: PALETTE.w, height: PALETTE.h }}>
              {column}
            </div>
          )
        }
      </GlassMorph>
    </div>
  );
}

function ToolColumn({ tool, onPress, focusRequest }: {
  tool: Tool | null;
  onPress: (tool: Tool) => void;
  focusRequest: { current: Tool | null };
}) {
  return (
    <div className="tool-column" role="toolbar" aria-orientation="vertical" aria-label="Adjustment tools"
      onKeyDown={(event) => rove(event, "vertical")}>
      {TOOLS.map((t) => (
        <button
          key={t.id}
          type="button"
          className="tool"
          data-tool={t.id}
          aria-pressed={tool === t.id}
          aria-label={t.label}
          title={`${t.label} (${t.key})`}
          tabIndex={(tool ?? "exposure") === t.id ? 0 : -1}
          onClick={() => onPress(t.id)}
          ref={(element) => {
            if (element !== null && focusRequest.current === t.id) {
              focusRequest.current = null;
              element.focus({ preventScroll: true });
            }
          }}
        >
          <t.icon />
        </button>
      ))}
    </div>
  );
}

/** Arrow keys move focus within a toolbar or a radio group of fills, as the ARIA patterns ask. */
function rove(event: KeyboardEvent<HTMLElement>, orientation: "vertical" | "horizontal", select = false) {
  const keys = orientation === "vertical" ? ["ArrowUp", "ArrowDown"] : ["ArrowLeft", "ArrowRight"];
  const dir = event.key === keys[0] ? -1 : event.key === keys[1] ? 1 : 0;
  if (dir === 0) return;
  const items = [...event.currentTarget.querySelectorAll<HTMLButtonElement>("button:not([disabled])")];
  const at = items.findIndex((item) => item === document.activeElement);
  const next = items[(at + dir + items.length) % items.length];
  if (next === undefined) return;
  event.preventDefault();
  event.stopPropagation();
  next.focus();
  if (select) next.click();
}

function formatEv(ev: number): string {
  if (Math.abs(ev) < 0.005) return "0.00 EV";
  return `${ev > 0 ? "+" : "−"}${Math.abs(ev).toFixed(2)} EV`;
}

const signed = (v: number, digits = 0, unit = ""): string =>
  `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(digits)}${unit}`;

function ExposurePanel({ develop, onDevelop, onAuto }: {
  develop: Develop; onDevelop: (patch: Partial<Develop>) => void; onAuto: () => void;
}) {
  const step = (by: number) =>
    onDevelop({ ev: Math.round(Math.min(3, Math.max(-3, develop.ev + by)) * 100) / 100 });
  return (
    <>
      <Slider label="Exposure" value={develop.ev} min={-3} max={3} step={0.05} origin={0}
        display={formatEv(develop.ev)} onChange={(ev) => onDevelop({ ev })} />
      <div className="chip-row" role="group" aria-label="Step exposure">
        <button type="button" className="chip" onClick={() => step(-1)}>{"−"}1</button>
        <button type="button" className="chip" onClick={() => step(-1 / 3)}>{"−⅓"}</button>
        <button type="button" className="chip" onClick={() => step(1 / 3)}>+{"⅓"}</button>
        <button type="button" className="chip" onClick={() => step(1)}>+1</button>
      </div>
      <PanelFoot onReset={() => onDevelop({ ev: 0 })}>
        <button type="button" className="chip" onClick={onAuto}>Auto</button>
      </PanelFoot>
    </>
  );
}

const PRESETS: readonly { id: string; label: string; temp: number | "as-shot"; tint: number }[] = [
  { id: "as-shot", label: "As shot", temp: "as-shot", tint: 0 },
  { id: "daylight", label: "Daylight", temp: 5500, tint: 0 },
  { id: "cloudy", label: "Cloudy", temp: 6500, tint: 0 },
  { id: "tungsten", label: "Tungsten", temp: 2850, tint: 0 },
];

function WhiteBalancePanel({ develop, asShot, onDevelop }: {
  develop: Develop; asShot: number; onDevelop: (patch: Partial<Develop>) => void;
}) {
  const preset = PRESETS.find((p) => (p.temp === "as-shot" ? asShot : p.temp) === develop.temp && p.tint === develop.tint);
  return (
    <>
      <Options label="White balance preset" value={preset?.id ?? null}
        items={PRESETS.map((p) => ({ value: p.id, label: p.label }))}
        onChange={(id) => {
          const p = PRESETS.find((q) => q.id === id);
          if (p !== undefined) onDevelop({ temp: p.temp === "as-shot" ? asShot : p.temp, tint: p.tint });
        }} />
      <Slider label="Temperature" value={develop.temp} min={2000} max={10000} step={50} origin={asShot}
        track="temperature" display={`${develop.temp} K`} onChange={(temp) => onDevelop({ temp })} />
      <Slider label="Tint" value={develop.tint} min={-50} max={50} step={1} origin={0}
        track="tint" display={signed(develop.tint)} onChange={(tint) => onDevelop({ tint })} />
      <PanelFoot onReset={() => onDevelop({ temp: asShot, tint: 0 })} />
    </>
  );
}

const ASPECTS: readonly { value: Aspect; label: string }[] = [
  { value: "original", label: "3:2" },
  { value: "1:1", label: "1:1" },
  { value: "4:5", label: "4:5" },
  { value: "16:9", label: "16:9" },
];

function CropPanel({ develop, onDevelop, onDone }: {
  develop: Develop; onDevelop: (patch: Partial<Develop>) => void; onDone: () => void;
}) {
  return (
    <>
      <Options label="Aspect ratio" value={develop.aspect} items={ASPECTS}
        onChange={(aspect) => onDevelop({ aspect })} />
      <Slider label="Straighten" value={develop.angle} min={-10} max={10} step={0.1} origin={0}
        display={signed(develop.angle, 1, "°")} onChange={(angle) => onDevelop({ angle })} />
      <Slider label="Size" value={Math.round(develop.scale * 100)} min={50} max={100} step={1} origin={100}
        display={`${Math.round(develop.scale * 100)} %`} onChange={(v) => onDevelop({ scale: v / 100 })} />
      <PanelFoot onReset={() => onDevelop({ aspect: "original", angle: 0, scale: 1, cx: 0.5, cy: 0.5 })}>
        <button type="button" className="chip" onClick={onDone}>Done</button>
      </PanelFoot>
    </>
  );
}

function PanelFoot({ onReset, children }: { onReset: () => void; children?: ReactNode }) {
  return (
    <div className="panel-foot">
      <button type="button" className="chip" onClick={onReset}>Reset</button>
      {children}
    </div>
  );
}

/**
 * A range input on glass, in a well: every line of text on the platter sits on a fill of the
 * ink's opposite pole, the way Control Center groups its controls, because bare labels on the
 * dark material measured 4.2:1 over frame 12's plaster wall (`DESIGN.md`, contrast).
 * The knob is a fill, not glass: vitrea refuses nested glass in both directions, so the knob
 * Apple lifts into glass while it is dragged stays a fill on the web (`DESIGN.md`, decisions). Double-click returns it to its origin, as every raw converter does.
 */
function Slider({ label, value, min, max, step, origin, display, onChange, track }: {
  label: string; value: number; min: number; max: number; step: number; origin: number;
  display: string; onChange: (value: number) => void; track?: "temperature" | "tint";
}) {
  const id = useId();
  const at = (v: number) => ((Math.min(max, Math.max(min, v)) - min) / (max - min)) * 100;
  const from = Math.min(at(origin), at(value));
  const to = Math.max(at(origin), at(value));
  const style = { "--from": `${from}%`, "--to": `${to}%` } as CSSProperties;
  return (
    <div className="slider">
      <div className="slider-row">
        <label htmlFor={id}>{label}</label>
        <output htmlFor={id} className="figure">{display}</output>
      </div>
      <input
        id={id}
        type="range"
        className={track === undefined ? "range" : `range range-${track}`}
        min={min}
        max={max}
        step={step}
        value={value}
        style={style}
        onChange={(event) => onChange(Number(event.currentTarget.value))}
        onDoubleClick={() => onChange(origin)}
      />
    </div>
  );
}

function Options<T extends string>({ label, items, value, onChange }: {
  label: string; items: readonly { value: T; label: string }[]; value: T | null; onChange: (value: T) => void;
}) {
  return (
    <div className="options" role="radiogroup" aria-label={label}
      onKeyDown={(event) => rove(event, "horizontal", true)}>
      {items.map((item, i) => (
        <button key={item.value} type="button" role="radio" className="opt"
          aria-checked={item.value === value}
          tabIndex={item.value === value || (value === null && i === 0) ? 0 : -1}
          onClick={() => onChange(item.value)}>
          {item.label}
        </button>
      ))}
    </div>
  );
}

export function Compare({ view, onView, at }: {
  view: View; onView: (view: View) => void; at: { x: number; y: number };
}) {
  return (
    <GlassSegmentedControl<View>
      items={[{ value: "before", label: "Before" }, { value: "after", label: "After" }]}
      value={view}
      onChange={onView}
      aria-label="Compare before and after"
      radius={COMPARE.h / 2}
      thickness={THICKNESS}
      className="compare"
      segmentClassName="compare-seg"
      indicatorClassName="compare-ind"
      style={{ left: at.x, top: at.y, width: COMPARE.w, height: COMPARE.h }}
    />
  );
}

export function Verdict({ frame, onFlag, onRating, at }: {
  frame: Frame; onFlag: (flag: Flag) => void; onRating: (rating: number) => void; at: { x: number; y: number };
}) {
  const rejected = frame.flag === "reject";
  const picked = frame.flag === "pick";
  return (
    <GlassSurface
      capsule
      thickness={THICKNESS}
      interactive
      role="toolbar"
      aria-label="Verdict"
      className="verdict"
      style={{ left: at.x, top: at.y, width: VERDICT.w, height: VERDICT.h }}
      onKeyDown={(event) => rove(event, "horizontal")}
    >
      <button type="button" className="vbtn" aria-pressed={rejected} aria-label="Reject" title="Reject (X)"
        onClick={() => onFlag(rejected ? null : "reject")}>
        <RejectIcon on={rejected} />
      </button>
      <span className="vsep" aria-hidden="true" />
      <div className="stars" role="radiogroup" aria-label="Rating">
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} type="button" role="radio" className="star"
            aria-checked={frame.rating === n}
            aria-label={`${n} star${n > 1 ? "s" : ""}`}
            title={`${n} star${n > 1 ? "s" : ""} (${n})`}
            onClick={() => onRating(frame.rating === n ? 0 : n)}>
            <StarIcon on={n <= frame.rating} />
          </button>
        ))}
      </div>
      <span className="vsep" aria-hidden="true" />
      <button type="button" className="vbtn" aria-pressed={picked} aria-label="Pick" title="Pick (P)"
        onClick={() => onFlag(picked ? null : "pick")}>
        <PickIcon on={picked} />
      </button>
    </GlassSurface>
  );
}
