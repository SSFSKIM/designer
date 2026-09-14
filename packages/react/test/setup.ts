/**
 * jsdom's gaps, filled — and only the ones the bindings genuinely depend on.
 *
 * `matchMedia` is replaced rather than polyfilled: platform-web reads the four
 * accessibility queries through `window.matchMedia`, and a unit test of
 * acceptance #6 has to be able to *change* the answers. The replacement is a
 * real, controllable matcher with working change events, so a test flips a
 * preference the way the platform would.
 *
 * `document.hasFocus()` is replaced on the same argument, and one consequence
 * makes it load-bearing rather than tidy: jsdom answers **false**, so a root
 * left on `windowActivation: "auto"` resolves `inactive` and every surface in
 * every test in this package would be made of the receded material. That is a
 * silent baseline change for suites that are about something else entirely, so
 * the default here is a focused window — the pose an app is in while someone is
 * using it — and a test that cares moves it by hand.
 */

import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach } from "vitest";

type Listener = (event: { matches: boolean }) => void;

interface FakeQuery {
  matches: boolean;
  readonly media: string;
  readonly listeners: Set<Listener>;
}

const queries = new Map<string, FakeQuery>();

/** Whether the window this suite runs in has focus. Focused unless a test says otherwise. */
let focused = true;

/**
 * Move the window's focus, as the platform would: the answer AND the event.
 *
 * Both halves matter. The activation observer subscribes to `focus`/`blur` to
 * learn that its reading is stale and re-reads `document.hasFocus()` for the
 * answer, so a test that fired only the event would be asserting on a synthetic
 * event's ability to invent a pose, which the runtime deliberately refuses.
 */
export function setWindowFocused(next: boolean): void {
  focused = next;
  window.dispatchEvent(new Event(next ? "focus" : "blur"));
}

/** Flip a media query and fire its change event, exactly as the platform would. */
export function setMediaQuery(media: string, matches: boolean): void {
  const query = queries.get(media);
  if (query === undefined) {
    queries.set(media, { matches, media, listeners: new Set() });
    return;
  }
  query.matches = matches;
  for (const listener of [...query.listeners]) listener({ matches });
}

export function resetMediaQueries(): void {
  queries.clear();
}

function install(): void {
  Object.defineProperty(window, "matchMedia", {
    configurable: true,
    writable: true,
    value: (media: string) => {
      const query = queries.get(media) ?? { matches: false, media, listeners: new Set<Listener>() };
      queries.set(media, query);
      return {
        get matches() {
          return query.matches;
        },
        get media() {
          return query.media;
        },
        addEventListener: (_type: "change", listener: Listener) => query.listeners.add(listener),
        removeEventListener: (_type: "change", listener: Listener) => query.listeners.delete(listener),
      };
    },
  });

  Object.defineProperty(document, "hasFocus", {
    configurable: true,
    writable: true,
    value: () => focused,
  });

  // The morph realigns its closed footprint when the layout under it moves.
  // jsdom never lays anything out, so the observer only has to exist.
  if (!("ResizeObserver" in window)) {
    Object.defineProperty(window, "ResizeObserver", {
      configurable: true,
      writable: true,
      value: class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    });
  }
}

install();

beforeEach(() => {
  resetMediaQueries();
  focused = true;
});

afterEach(() => {
  cleanup();
});
