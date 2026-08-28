/**
 * The runtime's ink, and who gets to overrule it (Decision Log #34(c)).
 *
 * The defect was not the colour. It was the precedence: `platform-web` wrote the
 * resolved ink as an inline `color` on the host, and an inline declaration
 * outranks every application rule short of `!important`. An app that styled a
 * glass host watched its declaration parse, cascade, and silently never apply —
 * while `--vitrea-foreground`, the seam it was told to build on, was published
 * on that same element. The seam was real and unusable at once.
 *
 * jsdom cannot lay out and cannot filter, but it *does* cascade: it applies
 * stylesheet rules, honours specificity, and puts inline style above both. That
 * is the whole property under test here, so this is the right environment for
 * it. What jsdom does not do is substitute `var()` — so the resolved colour is
 * measured in a real engine (`e2e/shared/ink-precedence.spec.ts`, all three) and
 * what is measured here is the shape of the write and the cascade around it.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { HOST_ATTRIBUTES } from "../src/host";
import { INK_RULE, INK_STYLESHEET_ATTRIBUTE, installInkStylesheet } from "../src/ink-stylesheet";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassRoot, type GlassRoot } from "../src/root";

class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

const matcher: MediaMatcher = () => ({
  matches: false,
  media: "(prefers-reduced-motion: reduce)",
  addEventListener: () => {},
  removeEventListener: () => {},
});

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];
let appStyles: HTMLStyleElement[] = [];

function root(): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
  });
  roots.push(created);
  return created;
}

/** A registered host with a class an application rule can name. */
function host(instance: GlassRoot, className: string): HTMLElement {
  const element = document.createElement("button");
  element.className = className;
  element.textContent = "Publish";
  instance.plane("base").hostLayer.append(element);
  instance.registerGroup({ id: "g1" });
  instance.registerHost({ host: element, groupId: "g1", plane: "base" });
  return element;
}

/** An application stylesheet, added the way an application's would be. */
function appStyle(css: string): HTMLStyleElement {
  const element = document.createElement("style");
  element.textContent = css;
  document.head.append(element);
  appStyles.push(element);
  return element;
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  for (const element of appStyles) element.remove();
  roots = [];
  containers = [];
  appStyles = [];
});

describe("the runtime's ink, at a precedence an app can beat", () => {
  it("writes the token inline and the colour nowhere inline", () => {
    const instance = root();
    const element = host(instance, "glass-host");
    instance.runFrame(0);

    // The decision still happens and is still published — this is not the
    // runtime giving up on the ink.
    expect(element.style.getPropertyValue("--vitrea-foreground")).not.toBe("");

    // And it reaches the element through the cascade rather than over it. This
    // is the assertion that failed before #34(c) was closed: the resolved ink
    // used to sit right here, inline, above everything an app could write.
    expect(element.style.getPropertyValue("color")).toBe("");
    // Anchored at a declaration boundary: the inline block legitimately carries
    // `border-color` and a `background-color` transition, and a substring match
    // would pass on those rather than on the property that mattered.
    expect(/(^|;)\s*color\s*:/.test(element.getAttribute("style") ?? "")).toBe(false);
  });

  it("loses to any application rule that names the host at all", () => {
    // The lowest-specificity thing an app is likely to write: one class. Under
    // the inline write this lost silently; under a `:where()` rule it wins,
    // which is the whole point of the change.
    appStyle(".glass-host { color: rgb(4, 5, 6); }");

    const instance = root();
    const element = host(instance, "glass-host");
    instance.runFrame(0);

    expect(getComputedStyle(element).color).toBe("rgb(4, 5, 6)");
  });

  it("keeps deciding for a host the application has not styled", () => {
    // The other half, and the one a naive "just stop writing the colour" fix
    // would break: with no app rule the runtime's answer is still what applies,
    // by way of the rule that resolves the published token.
    const instance = root();
    const element = host(instance, "unstyled-host");
    instance.runFrame(0);

    const applied = getComputedStyle(element).color;
    // jsdom does not substitute `var()`, so what it reports is the reference
    // itself. That the reference is what reaches the element *is* the property:
    // the runtime's `color` is now defined as the published token rather than
    // being a second copy of it. The substituted value is asserted in a real
    // engine by `e2e/shared/ink-precedence.spec.ts`.
    expect(applied).toBe("var(--vitrea-foreground)");
    expect(INK_RULE).toContain("var(--vitrea-foreground)");
  });

  it("installs one sheet per document, before the application's own", () => {
    const instance = root();
    root();

    const sheets = [...document.querySelectorAll(`style[${INK_STYLESHEET_ATTRIBUTE}]`)];
    expect(sheets).toHaveLength(1);

    // First in the head, so an application rule that is *also* zero-specificity
    // — `*`, or its own `:where()` — still wins on source order.
    expect(document.head.firstElementChild).toBe(sheets[0]);

    // Zero specificity, keyed by the host attribute and nothing else.
    expect(INK_RULE).toBe(
      `:where([${HOST_ATTRIBUTES.node}]) { color: var(--vitrea-foreground); }`,
    );

    // Reference-counted: the first root to go does not take the sheet with it.
    instance.destroy();
    roots = roots.filter((candidate) => candidate !== instance);
    expect(document.querySelectorAll(`style[${INK_STYLESHEET_ATTRIBUTE}]`)).toHaveLength(1);
  });

  it("removes the sheet once the last root that claimed it is gone", () => {
    const handle = installInkStylesheet(document);
    expect(handle.element.isConnected).toBe(true);

    handle.dispose();
    expect(handle.element.isConnected).toBe(false);

    // Idempotent: a second `destroy()` must not evict a sheet a sibling root
    // has since installed.
    const second = installInkStylesheet(document);
    handle.dispose();
    expect(second.element.isConnected).toBe(true);
    second.dispose();
  });

  it("stops applying to an element the runtime has released", () => {
    const instance = root();
    const element = document.createElement("button");
    instance.plane("base").hostLayer.append(element);
    instance.registerGroup({ id: "g1" });
    const handle = instance.registerHost({ host: element, groupId: "g1", plane: "base" });
    instance.runFrame(0);

    handle.release();

    // The rule is keyed by the registration attribute, which release removes —
    // so an element vitrea has let go of carries no vitrea ink at all.
    expect(element.hasAttribute(HOST_ATTRIBUTES.node)).toBe(false);
    expect(element.style.getPropertyValue("--vitrea-foreground")).toBe("");
    expect(getComputedStyle(element).color).not.toBe("var(--vitrea-foreground)");
  });
});
