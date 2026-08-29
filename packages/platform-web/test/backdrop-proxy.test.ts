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
import {
  createPlatformDiagnosticsChannel,
  type PlatformDiagnosticsChannel,
} from "../src/diagnostics";
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
  readonly diagnostics: PlatformDiagnosticsChannel;
} {
  const layers = createGlassLayerManager({ document });
  const diagnostics = createPlatformDiagnosticsChannel();
  const proxies = createBackdropProxyManager({
    plane: (plane) => layers.plane(plane),
    diagnostics,
    document,
  });
  return Object.assign(proxies, { layers, diagnostics });
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

/**
 * Two one-member groups in the same plane, `gap` CSS px apart on one row: group
 * `a` spans x 100..200, `b` starts at 200 + gap. The separation is the only
 * thing that varies, which is the independent variable the overlap experiment
 * swept (`spikes/s1-proxy-topology/overlap-experiment/`).
 *
 * At the default σ = 8 the padding is 24, so `gap` and 24 are the two numbers
 * every case below is about.
 */
const pair = (
  gap: number,
  overrides: { readonly a?: Partial<ProxyRequest>; readonly b?: Partial<ProxyRequest> } = {},
): readonly ProxyRequest[] => [
  request({
    groupId: "a",
    members: [
      { nodeId: "a1", bounds: { x: 100, y: 100, width: 100, height: 40 }, radii: [12, 12, 12, 12] },
    ],
    ...overrides.a,
  }),
  request({
    groupId: "b",
    order: 1,
    members: [
      {
        nodeId: "b1",
        bounds: { x: 200 + gap, y: 100, width: 100, height: 40 },
        radii: [12, 12, 12, 12],
      },
    ],
    ...overrides.b,
  }),
];

const overlapFindings = (
  proxies: ReturnType<typeof manager>,
): readonly { readonly subjects: readonly string[]; readonly message: string }[] =>
  proxies.diagnostics.reported.filter(
    (finding) => finding.code === "proxy-overlap-after-enforcement",
  );

/**
 * The cross-group check, and where it stops.
 *
 * The predicate is a padded box against the neighbour's *painted* region, not
 * against the neighbour's padded box. The two differ by exactly one padding, and
 * the overlap experiment measured that difference to be a range where nothing
 * happens: 81 byte-deterministic cells over three blur radii and four backdrop
 * classes, zero leak at every separation at or past one padding. The old
 * box-against-box form fired out to two paddings, so half its reach was a region
 * neither group paints into and the mechanism it names could not occur.
 */
describe("the cross-group overlap check", () => {
  it("fires when one group's padded box reaches the other's painted region", () => {
    const proxies = manager();
    proxies.sync(pair(20), ENVIRONMENT);

    const findings = overlapFindings(proxies);
    expect(findings).toHaveLength(1);
    expect(findings[0]?.subjects).toEqual(["a", "b"]);
    // The message quotes magnitudes from separations the check actually fires
    // at. It used to quote 17/255, which is S1's 0.4σ stress row, and which the
    // experiment re-measured as mostly the clip path's corner antialiasing.
    expect(findings[0]?.message).toContain("3/255 at a 1.5σ gap");
    expect(findings[0]?.message).not.toContain("17/255");
  });

  it("stays quiet where the padded boxes intersect but neither group paints", () => {
    // 40px apart at a padding of 24: the boxes overlap over 216..224, and that
    // strip is outside both clips. Measured byte-identical at every radius.
    const proxies = manager();
    proxies.sync(pair(40), ENVIRONMENT);

    expect(overlapFindings(proxies)).toEqual([]);
  });

  it("puts the boundary at one padding, where the geometry runs out", () => {
    // Exactly at the padding the box edge meets the neighbour's clip edge, and
    // touching is not reaching — the same positive-area rule the plane checks use.
    const quiet = manager();
    quiet.sync(pair(24), ENVIRONMENT);
    expect(overlapFindings(quiet)).toEqual([]);

    const loud = manager();
    loud.sync(pair(23), ENVIRONMENT);
    expect(overlapFindings(loud)).toHaveLength(1);
  });

  it("fires on the wider group's reach even where the narrower group has none", () => {
    // σ = 40 on `b` means a 120px padding: its box covers `a`'s shapes long
    // before `a`'s 24px box gets anywhere near `b`'s. The check is symmetric in
    // the pair, not in the paddings.
    const proxies = manager();
    proxies.sync(pair(50, { b: { blurRadius: 40 } }), ENVIRONMENT);

    expect(overlapFindings(proxies)).toHaveLength(1);
  });

  it("sees the pair that only the 3σ floor creates", () => {
    // What this check exists for: at the authored padding of 2 the groups are
    // nowhere near each other and core's own check is right to stay quiet. The
    // floor raises both to 24, and 24 reaches across a 20px gap.
    const proxies = manager();
    proxies.sync(pair(20, { a: { samplingPadding: 2 }, b: { samplingPadding: 2 } }), ENVIRONMENT);

    expect(overlapFindings(proxies)).toHaveLength(1);
  });

  it("says nothing across planes", () => {
    // Different planes are different canvas pairs and different backdrop roots;
    // a menu over a toolbar is the composition the overlay plane exists for.
    const proxies = manager();
    proxies.sync(pair(20, { b: { plane: "overlay" } }), ENVIRONMENT);

    expect(overlapFindings(proxies)).toEqual([]);
  });
});
