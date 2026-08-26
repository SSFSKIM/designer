/**
 * The proxy element set: what `sync` creates, what it reports, and what it keys
 * elements by.
 *
 * Geometry itself is `proxy-geometry.ts`'s and tested there; what this file is
 * about is the bookkeeping around it — because the bookkeeping is what the
 * backdrop-root audit runs on. A group whose creation is never reported is a
 * group whose chain is never walked, and a group whose two planes share one
 * element is a group sampling the wrong box on one of them.
 */

import { describe, expect, it } from "vitest";

import { createBackdropProxyManager, type ProxyRequest } from "../src/backdrop-proxy";
import { createPlatformDiagnosticsChannel } from "../src/diagnostics";
import { createGlassLayerManager } from "../src/planes";

const ENVIRONMENT = { devicePixelRatio: 2, maxProxyAreaDevicePx: 16_000_000 };

const request = (overrides: Partial<ProxyRequest> = {}): ProxyRequest => ({
  groupId: "g1",
  plane: "base",
  order: 0,
  members: [{ nodeId: "n1", bounds: { x: 100, y: 50, width: 200, height: 80 }, radii: [22, 22, 22, 22] }],
  samplingPadding: 24,
  mergeDistance: 24,
  blurRadius: 8,
  saturation: 1.8,
  ...overrides,
});

function manager(): ReturnType<typeof createBackdropProxyManager> & {
  readonly layers: ReturnType<typeof createGlassLayerManager>;
} {
  const layers = createGlassLayerManager({ document });
  const proxies = createBackdropProxyManager({
    plane: (plane) => layers.plane(plane),
    diagnostics: createPlatformDiagnosticsChannel(),
    document,
  });
  return Object.assign(proxies, { layers });
}

const boxOf = (element: HTMLElement): { left: string; top: string } => ({
  left: element.style.left,
  top: element.style.top,
});

describe("what sync reports back", () => {
  it("reports a group the first time it gets a proxy", () => {
    const proxies = manager();

    expect(proxies.sync([request()], ENVIRONMENT)).toEqual(["g1"]);
  });

  it("reports nothing on a repeat sync — the chain is the one already audited", () => {
    const proxies = manager();
    proxies.sync([request()], ENVIRONMENT);

    expect(proxies.sync([request()], ENVIRONMENT)).toEqual([]);
  });

  it("reports a group that moved to another plane", () => {
    const proxies = manager();
    proxies.sync([request()], ENVIRONMENT);

    // A new plane is a new parent chain, which is exactly what layer 2 walks.
    expect(proxies.sync([request({ plane: "overlay" })], ENVIRONMENT)).toEqual(["g1"]);
    expect(proxies.proxyFor("g1", "base")).toBeUndefined();
    expect(proxies.proxyFor("g1", "overlay")).toBeDefined();
  });

  it("reports a group that arrives long after the first frame", () => {
    // The regression: `created` was never appended to, so the audit's stale set —
    // which starts at "all" and is emptied after frame one — never learned about
    // a group registered later, and its chain went unwalked for the session.
    const proxies = manager();
    for (let frame = 0; frame < 5; frame += 1) proxies.sync([request()], ENVIRONMENT);

    expect(proxies.sync([request(), request({ groupId: "late" })], ENVIRONMENT)).toEqual(["late"]);
  });

  it("reports a split group once, not once per plane", () => {
    const proxies = manager();

    expect(
      proxies.sync(
        [request(), request({ plane: "overlay", members: [{ nodeId: "n2", bounds: { x: 0, y: 0, width: 50, height: 50 }, radii: [8, 8, 8, 8] }] })],
        ENVIRONMENT,
      ),
    ).toEqual(["g1"]);
  });
});

describe("a group with members on two planes", () => {
  const split: readonly ProxyRequest[] = [
    request({
      plane: "base",
      members: [{ nodeId: "n1", bounds: { x: 100, y: 50, width: 200, height: 80 }, radii: [22, 22, 22, 22] }],
    }),
    request({
      plane: "overlay",
      members: [{ nodeId: "n2", bounds: { x: 600, y: 400, width: 120, height: 60 }, radii: [10, 10, 10, 10] }],
    }),
  ];

  it("gets one element per plane, each in its own plane's proxy layer", () => {
    const proxies = manager();
    proxies.sync(split, ENVIRONMENT);

    const base = proxies.proxyFor("g1", "base");
    const overlay = proxies.proxyFor("g1", "overlay");

    expect(base).toBeDefined();
    expect(overlay).toBeDefined();
    expect(base).not.toBe(overlay);
    expect(proxies.layers.plane("base").proxyLayer.contains(base as Node)).toBe(true);
    expect(proxies.layers.plane("overlay").proxyLayer.contains(overlay as Node)).toBe(true);
  });

  it("gives each plane its own geometry — the last request no longer steals the element", () => {
    const proxies = manager();
    proxies.sync(split, ENVIRONMENT);

    // Keyed by group alone, both planes shared one element and one style
    // attribute, so the base plane's surfaces sampled the overlay plane's box.
    expect(boxOf(proxies.proxyFor("g1", "base") as HTMLElement)).not.toEqual(
      boxOf(proxies.proxyFor("g1", "overlay") as HTMLElement),
    );
  });

  it("names both planes, so an audit can walk both chains", () => {
    const proxies = manager();
    proxies.sync(split, ENVIRONMENT);

    expect([...proxies.planesOf("g1")].sort()).toEqual(["base", "overlay"]);
  });

  it("drops every plane's element on remove", () => {
    const proxies = manager();
    proxies.sync(split, ENVIRONMENT);
    proxies.remove("g1");

    expect(proxies.planesOf("g1")).toEqual([]);
    expect(proxies.layers.plane("base").proxyLayer.children).toHaveLength(0);
    expect(proxies.layers.plane("overlay").proxyLayer.children).toHaveLength(0);
  });

  it("drops the plane a group left behind", () => {
    const proxies = manager();
    proxies.sync(split, ENVIRONMENT);
    proxies.sync([split[1] as ProxyRequest], ENVIRONMENT);

    expect(proxies.planesOf("g1")).toEqual(["overlay"]);
    expect(proxies.layers.plane("base").proxyLayer.children).toHaveLength(0);
  });
});
