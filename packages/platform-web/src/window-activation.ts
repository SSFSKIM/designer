import { readWindowFocus } from "./measure";
import type { GlassRoot } from "./root";

/** A window pose, independent of a surface's interaction and presence. */
export type GlassWindowActivation = "auto" | "active" | "inactive";
export type ResolvedWindowActivation = Exclude<GlassWindowActivation, "auto">;

/** The explicit setting wins; visibility is deliberately not an input. */
export function resolveWindowActivation(
  setting: GlassWindowActivation,
  focused: boolean,
): ResolvedWindowActivation {
  return setting === "auto" ? (focused ? "active" : "inactive") : setting;
}

/** The framework-agnostic setter; the method is also on the live root handle. */
export function setWindowActivation(root: GlassRoot, value: GlassWindowActivation): void {
  root.setWindowActivation(value);
}

/**
 * Focus/blur invalidate a reading, not a material. The root consumes the reading
 * in its next read phase, after the engine has settled `document.hasFocus()`.
 * Synthetic focus events cannot invent an activation, and visibility is a
 * separate fact: a visible window can be unfocused. All handles come from the
 * supplied window, so importing this module never needs a browser global.
 */
export function observeWindowActivation(view: Window): {
  read(): boolean;
  invalidate(): void;
  stop(): void;
} {
  let dirty = true;
  let focused = false;
  const invalidate = (): void => { dirty = true; };
  view.addEventListener("focus", invalidate);
  view.addEventListener("blur", invalidate);
  return {
    read() {
      if (dirty) {
        focused = readWindowFocus(view);
        dirty = false;
      }
      return focused;
    },
    invalidate,
    stop() {
      view.removeEventListener("focus", invalidate);
      view.removeEventListener("blur", invalidate);
    },
  };
}
