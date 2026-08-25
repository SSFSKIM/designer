/**
 * Pointer and keyboard events → `@vitrea/motion`'s interaction machine →
 * channel values → render inputs (parent acceptance #3).
 *
 * Three rules shape this file, and all three come from the kernel rather than
 * from React:
 *
 * 1. **The machine collapses the flags, not this module.** A control can be
 *    hovered and focused and held at once; §Motion names one state at a time.
 *    `resolveInteractionState`'s precedence lives in `@vitrea/motion`, so the
 *    binding reports five booleans and reads back one state.
 * 2. **A transition only retargets.** Nothing here places a driver, so a release
 *    mid-press redirects the trajectory the press was already on — position and
 *    velocity carry across untouched. That is acceptance #3's "no snap or
 *    restart", and it is a property of the kernel this module must not undo.
 * 3. **The cap is the machine's.** `advance` applies the profile's `FramePolicy`
 *    at the frame boundary and returns what it applied; clamping again here
 *    would make the cap depend on how many loops a delta passed through.
 *
 * ## Where the values go
 *
 * `pressCompression` becomes a vitrea-owned transform through
 * `setOwnedTransform` — composed on top of the measured rect, never written back
 * into the shape, so no owned animation can dirty the geometry it is animating
 * (platform-web's host contract). The rest are published as custom properties on
 * the host, in the same `--vitrea-*` vocabulary the CSS tier writes, so an app
 * can style against them and a test can read a channel's value without a
 * screenshot. They are also exactly the `SurfaceChannels` the WebGPU renderer
 * consumes — `press`, `glow`, `sweep`, `lensStrength`, `pressPoint` — for
 * whichever layer eventually bridges the two.
 */

import type { GlassHostHandle } from "@vitrea/platform-web";
import {
  createInteractionMachine,
  type InteractionFlags,
  type InteractionMachine,
  type InteractionState,
  type MotionProfile,
} from "@vitrea/motion";
import { useCallback, useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent, type KeyboardEvent as ReactKeyboardEvent } from "react";

import type { GlassTicker } from "./ticker";

/** The custom properties a surface publishes each frame. */
export const GLASS_CHANNEL_PROPERTIES = {
  press: "--vitrea-press",
  glow: "--vitrea-glow",
  lensStrength: "--vitrea-lens",
  pressX: "--vitrea-press-x",
  pressY: "--vitrea-press-y",
  state: "--vitrea-state",
} as const;

/** Keys that activate a button, and therefore press its material. */
const ACTIVATION_KEYS = new Set([" ", "Enter", "Spacebar"]);

export interface GlassInteractionOptions {
  readonly handle: GlassHostHandle | null;
  readonly host: HTMLElement | null;
  readonly ticker: GlassTicker;
  readonly profile: MotionProfile;
  /** Wire the events at all. A decorative surface has no interaction state. */
  readonly interactive: boolean;
  readonly disabled: boolean;
  /** Held by a morph in flight; outranks press in the kernel's collapse order. */
  readonly morphing: boolean;
}

export interface GlassInteractionHandlers {
  readonly onPointerEnter: (event: ReactPointerEvent<HTMLElement>) => void;
  readonly onPointerLeave: (event: ReactPointerEvent<HTMLElement>) => void;
  readonly onPointerDown: (event: ReactPointerEvent<HTMLElement>) => void;
  readonly onPointerUp: (event: ReactPointerEvent<HTMLElement>) => void;
  readonly onPointerCancel: (event: ReactPointerEvent<HTMLElement>) => void;
  readonly onFocus: () => void;
  readonly onBlur: () => void;
  readonly onKeyDown: (event: ReactKeyboardEvent<HTMLElement>) => void;
  readonly onKeyUp: (event: ReactKeyboardEvent<HTMLElement>) => void;
}

export interface GlassInteraction {
  readonly handlers: GlassInteractionHandlers | undefined;
  readonly state: InteractionState;
  /** The live machine — the segmented indicator drives extra channels through it. */
  readonly machine: InteractionMachine;
}

const write = (host: HTMLElement, property: string, value: string, last: Map<string, string>): void => {
  if (last.get(property) === value) return;
  last.set(property, value);
  host.style.setProperty(property, value);
};

/** Four decimals: below a tenth of a device pixel at any plausible scale. */
const num = (value: number): string => value.toFixed(4);

/** What `num` prints for an unchanged scale, so an identity transform is skipped. */
const IDENTITY_SCALE = num(1);

export function useGlassInteraction(options: GlassInteractionOptions): GlassInteraction {
  const { handle, host, ticker, profile, interactive, disabled, morphing } = options;

  const machine = useMemo(() => createInteractionMachine({ profile }), [profile]);

  // Carry the channels across a profile swap. `withReducedMotion` produces a
  // different profile object, and a brand-new machine would start every channel
  // at its idle seed — a visible snap the moment the preference flips.
  const previous = useRef<InteractionMachine | null>(null);
  if (previous.current !== null && previous.current !== machine) {
    for (const channel of machine.channels) {
      const before = previous.current.channels.includes(channel)
        ? previous.current.driver(channel)
        : undefined;
      if (before !== undefined) machine.driver(channel).jumpTo(before.value, before.velocity);
    }
  }
  previous.current = machine;

  const flags = useRef<InteractionFlags>({
    disabled: false,
    morphing: false,
    pressed: false,
    hovered: false,
    focused: false,
  });
  const pressPoint = useRef<readonly [number, number] | null>(null);
  const written = useRef(new Map<string, string>());
  const [state, setState] = useState<InteractionState>(machine.state);

  const applyFlags = useCallback(
    (patch: Partial<InteractionFlags>) => {
      const next = { ...flags.current, ...patch };
      if (
        next.disabled === flags.current.disabled &&
        next.morphing === flags.current.morphing &&
        next.pressed === flags.current.pressed &&
        next.hovered === flags.current.hovered &&
        next.focused === flags.current.focused
      ) {
        return;
      }
      flags.current = next;
      machine.applyFlags(next);
      setState(machine.state);
      handle?.update({ interaction: machine.state });
    },
    [handle, machine],
  );

  useEffect(() => {
    // Dropping the handlers does not drop the state they set. A surface that
    // stops being interactive mid-press would otherwise stay compressed and lit
    // for good, because nothing is left listening for the release.
    applyFlags(
      interactive ? { disabled, morphing } : { disabled, morphing, pressed: false, hovered: false },
    );
  }, [applyFlags, disabled, interactive, morphing]);

  // The flags can settle before the host exists — a surface mounted `disabled`
  // reaches its state on the first render and registers on the next. Pushing the
  // current state whenever the handle arrives is what stops that ordering from
  // losing it, and it costs one patch per registration.
  useEffect(() => {
    handle?.update({ interaction: machine.state });
  }, [handle, machine]);

  // A pointer released outside the surface still ends the press. Without this a
  // drag off the button would leave the material held down for good.
  useEffect(() => {
    if (!interactive) return;
    const release = (): void => applyFlags({ pressed: false });
    window.addEventListener("pointerup", release);
    window.addEventListener("pointercancel", release);
    return () => {
      window.removeEventListener("pointerup", release);
      window.removeEventListener("pointercancel", release);
    };
  }, [applyFlags, interactive]);

  useEffect(() => {
    if (host === null) return;
    const last = written.current;

    const compression = machine.driver("pressCompression");

    return ticker.subscribe((dtMs) => {
      machine.advance(dtMs);

      /*
       * A settled driver is *at* its target, and the kernel says so with a
       * predicate rather than by snapping the value — springs integrate in
       * closed form and approach zero without reaching it. Reading the predicate
       * is what makes "no press" mean no press: comparing the raw value against
       * zero leaves a surface wearing `scale(1)` for ever, and whether it does is
       * a matter of how many frames the engine happened to run.
       */
      const press = compression.settled && compression.target === 0 ? 0 : compression.value;
      const glow = machine.value("glow");
      const lens = machine.value("lensStrength");

      /*
       * Composed on top of the measured rect, and absent rather than identity
       * when there is nothing to express.
       *
       * The test is the *emitted* scale, not the raw channel: a spring
       * approaches zero without arriving, so a compression of 1e-4 is still a
       * positive number and still writes `scale(1.0000)` — a transform that says
       * nothing, on a surface that is not being pressed. How long that lingers
       * depends on how many frames the engine ran, which is no basis for whether
       * an element carries a transform.
       */
      const scaled = num(1 - press * profile.pressCompressionScale);
      handle?.setOwnedTransform(scaled === IDENTITY_SCALE ? undefined : `scale(${scaled})`);

      write(host, GLASS_CHANNEL_PROPERTIES.press, num(press), last);
      write(host, GLASS_CHANNEL_PROPERTIES.glow, num(glow), last);
      write(host, GLASS_CHANNEL_PROPERTIES.lensStrength, num(lens), last);
      write(host, GLASS_CHANNEL_PROPERTIES.state, machine.state, last);

      const point = pressPoint.current;
      if (point !== null) {
        write(host, GLASS_CHANNEL_PROPERTIES.pressX, `${num(point[0])}px`, last);
        write(host, GLASS_CHANNEL_PROPERTIES.pressY, `${num(point[1])}px`, last);
      }
    });
  }, [handle, host, machine, profile.pressCompressionScale, ticker]);

  const setPressPointFromEvent = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      // One layout read, on a press — not in the steady state the read protocol
      // guarantees. `offsetX` would be cheaper but is relative to whichever
      // descendant was hit, which is the icon as often as the button.
      const rect = event.currentTarget.getBoundingClientRect();
      pressPoint.current = [event.clientX - rect.left, event.clientY - rect.top];
    },
    [],
  );

  const centrePressPoint = useCallback(() => {
    if (host === null) return;
    const rect = host.getBoundingClientRect();
    pressPoint.current = [rect.width / 2, rect.height / 2];
  }, [host]);

  const handlers = useMemo<GlassInteractionHandlers | undefined>(() => {
    if (!interactive) return undefined;
    return {
      onPointerEnter: () => applyFlags({ hovered: true }),
      onPointerLeave: () => applyFlags({ hovered: false }),
      onPointerDown: (event) => {
        setPressPointFromEvent(event);
        applyFlags({ pressed: true });
      },
      onPointerUp: () => applyFlags({ pressed: false }),
      onPointerCancel: () => applyFlags({ pressed: false }),
      onFocus: () => applyFlags({ focused: true }),
      onBlur: () => applyFlags({ focused: false, pressed: false }),
      onKeyDown: (event) => {
        if (!ACTIVATION_KEYS.has(event.key) || event.repeat) return;
        centrePressPoint();
        applyFlags({ pressed: true });
      },
      onKeyUp: (event) => {
        if (!ACTIVATION_KEYS.has(event.key)) return;
        applyFlags({ pressed: false });
      },
    };
  }, [applyFlags, centrePressPoint, interactive, setPressPointFromEvent]);

  return { handlers, state, machine };
}
