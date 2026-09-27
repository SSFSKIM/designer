/**
 * Press on the open platter's plain controls, driven through the platter host's channels.
 *
 * A `GlassMorph` host is the press target only while it is collapsed: open, it is not
 * interactive, because the controls inside it are what a reader presses, and those are plain
 * buttons rather than glass (vitrea refuses glass inside glass). So nothing would press the
 * material when a chip, an option or a tool inside the platter is pressed. This hook does for
 * the platter what the runtime's own interaction does for a glass control (materialist
 * `references/vitrea.md` section 6): it writes the host's press and glow channels, with the
 * press point at the contact, on the springs and targets of the root's motion profile. Reduce
 * Motion therefore removes the compression and keeps the glow exactly as it does for the
 * runtime's own controls, because the profile it reads already has that folded in.
 *
 * No transform and no colour. The WebGPU tier compresses the drawn field by the profile's scale
 * about its centre and lights it from the press point; the CSS tier draws the glow from the
 * same point and no compression, because its compression is the host's owned transform, which
 * only the runtime can write (`DESIGN.md`, decisions).
 *
 * The morph writes its own glow channel on every frame of the React ticker. A listener added
 * to the root's frame loop when a press begins runs after that ticker, so its value is the one
 * the next frame reads; it leaves the loop as soon as both channels are back at rest, and puts
 * back the press point the runtime had published.
 */
import {
  GLASS_CHANNEL_PROPERTIES,
  useGlassMotionProfile,
  useGlassRootHandle,
  type MotionProfile,
} from "@vitreajs/vitrea-react";
import { useCallback, useEffect, useRef, type FocusEvent, type KeyboardEvent, type PointerEvent } from "react";

/** The platter's host: the morph's registered element, which carries the page's class. */
const HOST = ".tools-host";
/** Keys that activate a button, and therefore press the material, as the runtime's controls do. */
const ACTIVATION_KEYS = new Set([" ", "Enter"]);

const PRESS = GLASS_CHANNEL_PROPERTIES.press;
const GLOW = GLASS_CHANNEL_PROPERTIES.glow;
const PRESS_X = GLASS_CHANNEL_PROPERTIES.pressX;
const PRESS_Y = GLASS_CHANNEL_PROPERTIES.pressY;

/** Four decimals, as the runtime's own binding writes them. */
const num = (value: number): string => value.toFixed(4);

interface Press {
  readonly host: HTMLElement;
  /** The press point the runtime had published before this press, put back at rest. */
  readonly saved: { readonly x: string; readonly y: string };
  pressed: boolean;
  press: number;
  velocity: number;
  glow: number;
  stop: () => void;
}

/**
 * One step of the kernel's interruptible spring in closed form (`@vitrea/motion`'s
 * `SpringDriver`, which the page cannot import): `responseMs` is the undamped period, and a
 * release mid-press redirects from the current value and velocity rather than restarting.
 */
function springStep(press: Press, target: number, responseMs: number, zeta: number, dtMs: number): void {
  const t = dtMs / 1000;
  const w = (2 * Math.PI * 1000) / responseMs;
  const y0 = press.press - target;
  const v0 = press.velocity;
  let y: number;
  let v: number;
  if (Math.abs(zeta - 1) < 1e-6) {
    const decay = Math.exp(-w * t);
    const c = v0 + w * y0;
    y = (y0 + c * t) * decay;
    v = (v0 - w * c * t) * decay;
  } else if (zeta < 1) {
    const wd = w * Math.sqrt(1 - zeta * zeta);
    const decay = Math.exp(-zeta * w * t);
    const cos = Math.cos(wd * t);
    const sin = Math.sin(wd * t);
    const b = (v0 + zeta * w * y0) / wd;
    y = decay * (y0 * cos + b * sin);
    v = decay * ((b * wd - zeta * w * y0) * cos - (y0 * wd + zeta * w * b) * sin);
  } else {
    const s = w * Math.sqrt(zeta * zeta - 1);
    const r1 = -zeta * w + s;
    const r2 = -zeta * w - s;
    const c1 = (v0 - r2 * y0) / (r1 - r2);
    const c2 = (v0 - r1 * y0) / (r1 - r2);
    y = c1 * Math.exp(r1 * t) - c2 * Math.exp(r2 * t);
    v = c1 * r1 * Math.exp(r1 * t) - c2 * r2 * Math.exp(r2 * t);
  }
  press.press = target + y;
  press.velocity = v;
}

/**
 * Advance one press by a frame. Returns false once it is back at rest, or the moment the
 * platter starts to morph, and the caller then leaves the loop.
 */
function advance(press: Press, profile: MotionProfile, deltaMs: number): boolean {
  const compression = profile.channels.pressCompression;
  const glow = profile.channels.glow;
  // The kernel's binding table fixes these two kinds; a profile that rebinds them is not one
  // this page knows how to step, so it leaves the channels to the runtime.
  if (compression.kind !== "interruptible-spring" && compression.kind !== "critically-damped") return false;
  if (glow.kind !== "attack-decay") return false;

  // A morph outranks press in the runtime's collapse order: the channels go back to it at once.
  if (!press.host.isConnected || press.host.hasAttribute("data-vitrea-morphing")) return false;
  const held = press.pressed;
  const targets = held ? profile.stateTargets.pressed : profile.stateTargets.idle;
  const pressTarget = targets.pressCompression ?? 0;
  const glowTarget = targets.glow ?? 0;
  const dtMs = Math.min(Math.max(deltaMs, 0), profile.frame.maxDeltaMs);
  if (dtMs > 0) {
    springStep(press, pressTarget, compression.responseMs, compression.dampingRatio, dtMs);
    const tau = glowTarget > press.glow ? glow.attackMs : glow.decayMs;
    press.glow = tau <= 0 ? glowTarget : glowTarget + (press.glow - glowTarget) * Math.exp(-dtMs / tau);
  }
  const atRest =
    !held &&
    Math.abs(press.press - pressTarget) <= compression.restDistance &&
    Math.abs(press.velocity) <= compression.restVelocity &&
    Math.abs(press.glow - glowTarget) <= glow.restDistance;
  if (atRest) return false;
  press.host.style.setProperty(PRESS, num(press.press));
  press.host.style.setProperty(GLOW, num(press.glow));
  return true;
}

function restore(host: HTMLElement, property: string, value: string): void {
  if (value === "") host.style.removeProperty(property);
  else host.style.setProperty(property, value);
}

export interface PlatterPressHandlers {
  readonly onPointerDown: (event: PointerEvent<HTMLElement>) => void;
  readonly onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  readonly onKeyUp: (event: KeyboardEvent<HTMLElement>) => void;
  readonly onBlur: (event: FocusEvent<HTMLElement>) => void;
}

/**
 * Handlers for the element that holds the platter's controls. A press on any enabled button
 * inside it presses the platter's material at the contact point; a range input's drag does not,
 * because a slider's knob is what a drag moves, and the platter does not flex under it.
 */
export function usePlatterPress(): PlatterPressHandlers {
  const { root } = useGlassRootHandle();
  const profile = useGlassMotionProfile();
  const profileRef = useRef(profile);
  profileRef.current = profile;
  const live = useRef<Press | null>(null);

  const settle = useCallback(() => {
    const press = live.current;
    if (press === null) return;
    live.current = null;
    press.stop();
    press.host.style.setProperty(PRESS, num(0));
    restore(press.host, PRESS_X, press.saved.x);
    restore(press.host, PRESS_Y, press.saved.y);
  }, []);

  const begin = useCallback(
    (host: HTMLElement, x: number, y: number) => {
      if (root === null || host.hasAttribute("data-vitrea-morphing")) return;
      if (live.current !== null && live.current.host !== host) settle();
      let press = live.current;
      if (press === null) {
        const read = (property: string): number => Number.parseFloat(host.style.getPropertyValue(property)) || 0;
        const started: Press = {
          host,
          saved: { x: host.style.getPropertyValue(PRESS_X), y: host.style.getPropertyValue(PRESS_Y) },
          pressed: true,
          press: read(PRESS),
          velocity: 0,
          glow: read(GLOW),
          stop: () => undefined,
        };
        started.stop = root.subscribe(({ deltaMs }) => {
          if (!advance(started, profileRef.current, deltaMs) && live.current === started) settle();
        });
        live.current = press = started;
      }
      press.pressed = true;
      host.style.setProperty(PRESS_X, `${num(x)}px`);
      host.style.setProperty(PRESS_Y, `${num(y)}px`);
    },
    [root, settle],
  );

  const release = useCallback(() => {
    if (live.current !== null) live.current.pressed = false;
  }, []);

  // A pointer released anywhere ends the press, as the runtime's own controls do; without it a
  // drag off the button would leave the platter held down.
  useEffect(() => {
    window.addEventListener("pointerup", release);
    window.addEventListener("pointercancel", release);
    return () => {
      window.removeEventListener("pointerup", release);
      window.removeEventListener("pointercancel", release);
      settle();
    };
  }, [release, settle]);

  const control = (event: { target: EventTarget; currentTarget: HTMLElement }): HTMLButtonElement | null => {
    const button = event.target instanceof Element ? event.target.closest("button") : null;
    return button !== null && !button.disabled && event.currentTarget.contains(button) ? button : null;
  };

  return {
    onPointerDown: (event) => {
      if (event.button !== 0 || control(event) === null) return;
      const host = event.currentTarget.closest<HTMLElement>(HOST);
      if (host === null) return;
      // One layout read, on a press, as the runtime's binding takes it.
      const rect = host.getBoundingClientRect();
      begin(host, event.clientX - rect.left, event.clientY - rect.top);
    },
    onKeyDown: (event) => {
      if (!ACTIVATION_KEYS.has(event.key) || event.repeat) return;
      const button = control(event);
      const host = event.currentTarget.closest<HTMLElement>(HOST);
      if (button === null || host === null) return;
      const at = button.getBoundingClientRect();
      const rect = host.getBoundingClientRect();
      begin(host, at.x + at.width / 2 - rect.left, at.y + at.height / 2 - rect.top);
    },
    onKeyUp: (event) => {
      if (ACTIVATION_KEYS.has(event.key)) release();
    },
    onBlur: release,
  };
}
