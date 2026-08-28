/**
 * The layer model as a contract: what fires, what stays quiet, and what it costs.
 *
 * Two halves. The first drives `checkLayerModel` directly, because the role
 * table and the two-directional nesting search are decidable from a bare DOM and
 * deserve assertions that do not depend on a whole root. The second drives the
 * real `createGlassRoot.registerHost`, because the thing that actually has to be
 * true is that an app registering glass inside glass hears about it — and that a
 * clean composition, including every arrangement vitrea's own components ship,
 * hears nothing.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { checkLayerModel, contentLayerRole, findNesting } from "../src/layer-model";
import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";
import type { PlatformDiagnostic } from "../src/diagnostics";
import type { MediaMatcher } from "../src/media-policy";

/** jsdom has no ResizeObserver, and `GeometrySync` builds one unconditionally. */
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

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

/** A root plus the codes it reported, so every assertion reads off one channel. */
function rootWithCodes(options: GlassRootOptions = {}): {
  readonly root: GlassRoot;
  readonly codes: string[];
  readonly messages: string[];
} {
  const codes: string[] = [];
  const messages: string[] = [];
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: ({ diagnostic }) => {
      codes.push(diagnostic.code);
      messages.push(diagnostic.message);
    },
    ...options,
  });
  roots.push(created);
  created.registerGroup({ id: "g1" });
  return { root: created, codes, messages };
}

const element = (tag: string, attributes: Record<string, string> = {}): HTMLElement => {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  return node;
};

const collect = (
  candidate: { nodeId: string; host: HTMLElement },
  registered: { nodeId: string; host: HTMLElement }[] = [],
): PlatformDiagnostic[] => {
  const found: PlatformDiagnostic[] = [];
  checkLayerModel(candidate, registered, (diagnostic) => found.push(diagnostic));
  return found;
};

describe("the content-layer role table", () => {
  it("names the list and table structures Apple names", () => {
    expect(contentLayerRole(element("ul"))).toBe("list");
    expect(contentLayerRole(element("ol"))).toBe("list");
    expect(contentLayerRole(element("li"))).toBe("listitem");
    expect(contentLayerRole(element("table"))).toBe("table");
    expect(contentLayerRole(element("tbody"))).toBe("rowgroup");
    expect(contentLayerRole(element("tr"))).toBe("row");
    expect(contentLayerRole(element("td"))).toBe("cell");
    expect(contentLayerRole(element("th"))).toBe("columnheader");
  });

  it("says nothing about the elements a control is actually made of", () => {
    for (const tag of ["div", "button", "a", "span", "nav", "section", "header", "menu"]) {
      expect(contentLayerRole(element(tag))).toBeUndefined();
    }
  });

  it("lets an explicit role override the tag, in both directions", () => {
    // The escape the message names: this <ul> is a menu, not a list.
    expect(contentLayerRole(element("ul", { role: "menu" }))).toBeUndefined();
    expect(contentLayerRole(element("ul", { role: "toolbar" }))).toBeUndefined();
    // And a <div> that declares itself a row is one.
    expect(contentLayerRole(element("div", { role: "row" }))).toBe("row");
    expect(contentLayerRole(element("div", { role: "gridcell" }))).toBe("gridcell");
  });

  it("takes the first token of a role fallback list, as the platform does", () => {
    expect(contentLayerRole(element("div", { role: "row presentation" }))).toBe("row");
    expect(contentLayerRole(element("ul", { role: "menu list" }))).toBeUndefined();
  });
});

describe("finding one host inside another", () => {
  it("finds an outer host the candidate is nested in", () => {
    const outer = element("div");
    const inner = element("button");
    outer.append(inner);

    const found = findNesting({ nodeId: "inner", host: inner }, [{ nodeId: "outer", host: outer }]);
    expect(found?.inner.nodeId).toBe("inner");
    expect(found?.outer.nodeId).toBe("outer");
  });

  it("finds an inner host the candidate wraps — registration order is the app's business", () => {
    const outer = element("div");
    const inner = element("button");
    outer.append(inner);

    const found = findNesting({ nodeId: "outer", host: outer }, [{ nodeId: "inner", host: inner }]);
    expect(found?.inner.nodeId).toBe("inner");
    expect(found?.outer.nodeId).toBe("outer");
  });

  it("says nothing about siblings, however close", () => {
    const parent = element("div");
    const a = element("button");
    const b = element("button");
    parent.append(a, b);

    expect(findNesting({ nodeId: "a", host: a }, [{ nodeId: "b", host: b }])).toBeUndefined();
  });
});

describe("checkLayerModel", () => {
  it("reports glass inside glass as an error naming both surfaces", () => {
    const outer = element("div");
    const inner = element("button");
    outer.append(inner);

    const found = collect({ nodeId: "inner", host: inner }, [{ nodeId: "outer", host: outer }]);
    expect(found.map((entry) => entry.code)).toEqual(["glass-inside-glass"]);
    expect(found[0]?.severity).toBe("error");
    // Inner first, so the pair dedupes to one finding whichever order they registered in.
    expect(found[0]?.subjects).toEqual(["inner", "outer"]);
    expect(found[0]?.message).toContain("controls-layer material");
  });

  it("reports a host on a content-layer element as a warning that names the escape", () => {
    const found = collect({ nodeId: "row", host: element("tr") });
    expect(found.map((entry) => entry.code)).toEqual(["glass-in-content-layer"]);
    expect(found[0]?.severity).toBe("warning");
    expect(found[0]?.message).toContain('role="toolbar"');
  });

  it("says nothing about a plain control registered on its own", () => {
    expect(collect({ nodeId: "n1", host: element("button") })).toEqual([]);
  });
});

describe("registerHost enforces the layer model", () => {
  it("fires when a surface is registered inside another surface's content", () => {
    const { root: instance, codes } = rootWithCodes();
    const outer = document.createElement("div");
    const inner = document.createElement("button");
    outer.append(inner);
    instance.plane("base").hostLayer.append(outer);

    instance.registerHost({ host: outer, groupId: "g1", nodeId: "outer" });
    expect(codes).not.toContain("glass-inside-glass");

    instance.registerHost({ host: inner, groupId: "g1", nodeId: "inner" });
    expect(codes).toContain("glass-inside-glass");
  });

  it("fires when the container registers last, wrapping a surface already registered", () => {
    const { root: instance, codes } = rootWithCodes();
    const outer = document.createElement("div");
    const inner = document.createElement("button");
    outer.append(inner);
    instance.plane("base").hostLayer.append(outer);

    instance.registerHost({ host: inner, groupId: "g1", nodeId: "inner" });
    instance.registerHost({ host: outer, groupId: "g1", nodeId: "outer" });
    expect(codes).toContain("glass-inside-glass");
  });

  it("fires across planes, where the geometric overlap check is silent by design", () => {
    const { root: instance, codes } = rootWithCodes();
    const outer = document.createElement("div");
    const inner = document.createElement("button");
    outer.append(inner);
    instance.plane("base").hostLayer.append(outer);

    instance.registerHost({ host: outer, groupId: "g1", nodeId: "outer", plane: "base" });
    instance.registerHost({ host: inner, groupId: "g1", nodeId: "inner", plane: "overlay" });
    expect(codes).toContain("glass-inside-glass");
  });

  it("fires when a host is registered on a table row", () => {
    const { root: instance, codes } = rootWithCodes();
    const row = document.createElement("tr");
    instance.plane("base").hostLayer.append(row);

    instance.registerHost({ host: row, groupId: "g1", nodeId: "row" });
    expect(codes).toContain("glass-in-content-layer");
  });

  it("says nothing about a row of sibling surfaces — the toolbar shape vitrea ships", () => {
    const { root: instance, codes } = rootWithCodes();
    // `GlassToolbar` is deliberately not a glass surface; its members are
    // siblings inside a plain container. That composition must stay silent.
    const toolbar = document.createElement("div");
    toolbar.setAttribute("role", "toolbar");
    const first = document.createElement("button");
    const second = document.createElement("button");
    toolbar.append(first, second);
    instance.plane("base").hostLayer.append(toolbar);

    instance.registerHost({ host: first, groupId: "g1", nodeId: "n1" });
    instance.registerHost({ host: second, groupId: "g1", nodeId: "n2" });

    expect(codes).not.toContain("glass-inside-glass");
    expect(codes).not.toContain("glass-in-content-layer");
  });

  it("says nothing about a surface whose own content is ordinary DOM", () => {
    const { root: instance, codes } = rootWithCodes();
    const plate = document.createElement("div");
    plate.innerHTML = "<h2>Title</h2><p>Body</p><button>Plain</button>";
    instance.plane("base").hostLayer.append(plate);

    instance.registerHost({ host: plate, groupId: "g1", nodeId: "plate" });
    expect(codes).not.toContain("glass-inside-glass");
    expect(codes).not.toContain("glass-in-content-layer");
  });

  it("costs a production build nothing: with devMode off, neither code is reachable", () => {
    const { root: instance, codes } = rootWithCodes({ devMode: false });
    const outer = document.createElement("tr");
    const inner = document.createElement("button");
    outer.append(inner);
    instance.plane("base").hostLayer.append(outer);

    instance.registerHost({ host: outer, groupId: "g1", nodeId: "outer" });
    instance.registerHost({ host: inner, groupId: "g1", nodeId: "inner" });

    expect(codes).not.toContain("glass-inside-glass");
    expect(codes).not.toContain("glass-in-content-layer");
  });

  it("never runs from a frame: registering nothing new reports nothing new", () => {
    const { root: instance, codes } = rootWithCodes();
    const outer = document.createElement("div");
    const inner = document.createElement("button");
    outer.append(inner);
    instance.plane("base").hostLayer.append(outer);
    instance.registerHost({ host: outer, groupId: "g1", nodeId: "outer" });
    instance.registerHost({ host: inner, groupId: "g1", nodeId: "inner" });

    const after = codes.filter((code) => code === "glass-inside-glass").length;
    for (let frame = 0; frame < 5; frame += 1) instance.runFrame(16 * frame);
    expect(codes.filter((code) => code === "glass-inside-glass").length).toBe(after);
  });
});
