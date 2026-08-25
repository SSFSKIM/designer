/**
 * `GlassSegmentedControl` — a radiogroup whose selection indicator is a
 * within-group morph.
 *
 * ## Semantics
 *
 * `role="radiogroup"` on the track, `role="radio"` with `aria-checked` on each
 * segment, arrows move the selection (which in a radio group also moves focus),
 * and only the checked segment is a tab stop. That is the ARIA radio-group
 * pattern, not an approximation of it: a segmented control *is* a radio group
 * that happens to look like a switch.
 *
 * ## The indicator, and why it is not a second glass surface
 *
 * X8 rider 2 calls this the field-reference-only case. A concentric child's field
 * is its parent's plus a positive inset, so `min(parent, parent + inset)` erases
 * the child by construction — an indicator nested in its track's union is
 * invisible. The renderer's answer is to reference the track's geometry as the
 * field the indicator's contour is offset from, and to draw the track once
 * (`SurfaceInput.fieldReferenceOnly`).
 *
 * v1's plumbing cannot express that yet, and this component says so rather than
 * pretending otherwise. Registering the indicator as a glass node would trip X1's
 * same-plane overlap check — the track and the indicator overlap by definition —
 * so the indicator is DOM, and the part that *is* expressible is: its radius is
 * derived through `resolveConcentric`, the level-set resolver, from the track's
 * own resolved shape. Concentricity governs radii, not the curve profile, so it
 * inherits the track's smoothing and reference.
 *
 * ## The slide
 *
 * Driven through `@vitrea/motion`'s interaction machine, carrying the `position`
 * and `size` channels alongside the state-driven ones. The machine is the thing
 * that owns the drivers, so a selection changed mid-slide retargets rather than
 * restarting, and a press on a segment compresses and lights the indicator
 * through the same channels a button uses.
 */

import { resolveConcentric, resolveShape } from "@vitrea/geometry";
import {
  createInteractionMachine,
  STATE_DRIVEN_CHANNELS,
  type InteractionFlags,
} from "@vitrea/motion";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type HTMLAttributes,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

import { useGlassRootHandle } from "../context";
import { GLASS_CHANNEL_PROPERTIES } from "../interaction";
import type { GlassCornerProfile } from "../shape";
import { GlassSurface } from "../surface";
import type { GlassPlane } from "@vitrea/core";

export interface GlassSegment<T extends string = string> {
  readonly value: T;
  readonly label: ReactNode;
  /** Needed when `label` is not text — an icon-only segment must still be named. */
  readonly "aria-label"?: string;
  readonly disabled?: boolean;
}

export interface GlassSegmentedControlProps<T extends string = string>
  extends Omit<HTMLAttributes<HTMLElement>, "onChange" | "role" | "defaultValue"> {
  readonly items: readonly GlassSegment<T>[];
  readonly value: T;
  readonly onChange: (value: T) => void;
  readonly "aria-label"?: string | undefined;
  readonly plane?: GlassPlane | undefined;
  readonly groupId?: string | undefined;
  readonly profile?: GlassCornerProfile | undefined;
  readonly radius?: number | undefined;
  readonly thickness?: number | undefined;
  /** Inward offset of the indicator from the track, in CSS px. */
  readonly indicatorInset?: number | undefined;
  readonly className?: string | undefined;
  readonly indicatorClassName?: string | undefined;
  readonly segmentClassName?: string | undefined;
}

const TRACK_RADIUS = 14;
const TRACK_THICKNESS = 6;
const INDICATOR_INSET = 3;

/** Channels the indicator carries: its geometry, plus the state-driven set. */
const INDICATOR_CHANNELS = ["position", "size", ...STATE_DRIVEN_CHANNELS] as const;

const num = (value: number): string => value.toFixed(4);

export function GlassSegmentedControl<T extends string = string>(
  props: GlassSegmentedControlProps<T>,
): ReactNode {
  const {
    items,
    value,
    onChange,
    plane,
    groupId,
    profile,
    radius = TRACK_RADIUS,
    thickness = TRACK_THICKNESS,
    indicatorInset = INDICATOR_INSET,
    className,
    indicatorClassName,
    segmentClassName,
    ...rest
  } = props;

  const { ticker, profile: motionProfile } = useGlassRootHandle();
  const [track, setTrack] = useState<HTMLElement | null>(null);
  const [indicator, setIndicator] = useState<HTMLDivElement | null>(null);
  const segments = useRef(new Map<string, HTMLButtonElement>());
  const [indicatorRadius, setIndicatorRadius] = useState(radius - indicatorInset);

  const machine = useMemo(
    () => createInteractionMachine({ profile: motionProfile, channels: INDICATOR_CHANNELS }),
    [motionProfile],
  );
  const flags = useRef<InteractionFlags>({
    disabled: false,
    morphing: false,
    pressed: false,
    hovered: false,
    focused: false,
  });
  /** `false` until the first measurement places the indicator instead of animating it. */
  const placed = useRef(false);

  const applyFlags = useCallback(
    (patch: Partial<InteractionFlags>) => {
      flags.current = { ...flags.current, ...patch };
      machine.applyFlags(flags.current);
    },
    [machine],
  );

  /**
   * Retarget the indicator at the selected segment.
   *
   * Measured from the segments' own boxes, not from an assumed equal division:
   * segments size to their labels, and an indicator that assumed otherwise would
   * be visibly wrong on the first non-uniform label.
   */
  const retarget = useCallback(() => {
    const element = segments.current.get(value);
    if (element === undefined || track === null) return;

    const x = element.offsetLeft + indicatorInset;
    const width = element.offsetWidth - indicatorInset * 2;

    machine.driver("position").retarget(x);
    machine.driver("size").retarget(width);
    if (placed.current) return;

    // The first measurement places the indicator rather than sliding it in from
    // wherever a driver happened to start. `jumpTo` moves the value and leaves
    // the target alone, so it comes after the retarget, never instead of it.
    machine.driver("position").jumpTo(x, 0);
    machine.driver("size").jumpTo(width, 0);
    placed.current = true;
  }, [indicatorInset, machine, track, value]);

  useLayoutEffect(retarget, [retarget]);

  /**
   * The concentric radius, through the level-set resolver rather than
   * `radius - inset`. The subtraction is right only for circular corners; the
   * resolver also carries the budget cap and the minimum-radius floor, and it is
   * where the declared error bound lives.
   */
  useLayoutEffect(() => {
    if (track === null) return;
    const width = track.offsetWidth;
    const height = track.offsetHeight;
    if (width === 0 || height === 0) return;

    const parent = resolveShape({
      family: "fixed-rounded-rect",
      center: [0, 0],
      size: [width, height],
      radii: radius,
      profile: profile ?? "continuous",
      thickness,
    });
    setIndicatorRadius(resolveConcentric(parent, { inset: indicatorInset }).shape.corner.radius);
  }, [indicatorInset, profile, radius, thickness, track]);

  useEffect(() => {
    if (indicator === null) return;
    let lastTransform = "";
    return ticker.subscribe((dtMs) => {
      machine.advance(dtMs);

      const x = machine.value("position");
      const width = machine.value("size");
      const press = machine.value("pressCompression");
      const scale = 1 - press * motionProfile.pressCompressionScale;
      const transform = `translateX(${num(x)}px) scale(${num(scale)})`;

      if (transform !== lastTransform) {
        lastTransform = transform;
        indicator.style.transform = transform;
        indicator.style.width = `${num(width)}px`;
      }
      indicator.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, num(press));
      indicator.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, num(machine.value("glow")));
      indicator.style.setProperty(GLASS_CHANNEL_PROPERTIES.lensStrength, num(machine.value("lensStrength")));
    });
  }, [indicator, machine, motionProfile.pressCompressionScale, ticker]);

  const enabled = useMemo(() => items.filter((item) => item.disabled !== true), [items]);

  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLElement>) => {
      const index = enabled.findIndex((item) => item.value === value);
      let next: GlassSegment<T> | undefined;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        next = enabled[(index + 1 + enabled.length) % enabled.length];
      } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        next = enabled[(index - 1 + enabled.length) % enabled.length];
      } else if (event.key === "Home") {
        next = enabled[0];
      } else if (event.key === "End") {
        next = enabled[enabled.length - 1];
      } else {
        return;
      }
      if (next === undefined || next.value === value) return;
      event.preventDefault();
      onChange(next.value);
      segments.current.get(next.value)?.focus();
    },
    [enabled, onChange, value],
  );

  const indicatorStyle: CSSProperties = {
    position: "absolute",
    left: 0,
    top: indicatorInset,
    bottom: indicatorInset,
    borderRadius: indicatorRadius,
    pointerEvents: "none",
    transformOrigin: "center",
  };

  return (
    <GlassSurface
      {...rest}
      role="radiogroup"
      radius={radius}
      thickness={thickness}
      {...(className === undefined ? {} : { className })}
      {...(plane === undefined ? {} : { plane })}
      {...(groupId === undefined ? {} : { groupId })}
      {...(profile === undefined ? {} : { profile })}
      onKeyDown={onKeyDown}
      onHost={(handle) => setTrack(handle?.host ?? null)}
    >
      <div
        ref={setIndicator}
        aria-hidden="true"
        data-vitrea-indicator=""
        className={indicatorClassName}
        style={indicatorStyle}
      />
      {items.map((item) => {
        const selected = item.value === value;
        return (
          <button
            key={item.value}
            type="button"
            role="radio"
            aria-checked={selected}
            {...(item["aria-label"] === undefined ? {} : { "aria-label": item["aria-label"] })}
            disabled={item.disabled === true}
            tabIndex={selected ? 0 : -1}
            className={segmentClassName}
            ref={(element) => {
              if (element === null) segments.current.delete(item.value);
              else segments.current.set(item.value, element);
            }}
            onClick={() => onChange(item.value)}
            onFocus={() => applyFlags({ focused: true })}
            onBlur={() => applyFlags({ focused: false, pressed: false })}
            onPointerEnter={() => applyFlags({ hovered: true })}
            onPointerLeave={() => applyFlags({ hovered: false, pressed: false })}
            onPointerDown={() => applyFlags({ pressed: true })}
            onPointerUp={() => applyFlags({ pressed: false })}
          >
            {item.label}
          </button>
        );
      })}
    </GlassSurface>
  );
}
