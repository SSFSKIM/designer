import { describe, expect, it } from "vitest";

import {
  cssTierGroupShadowDeclarations,
  planCssTierShadow,
} from "../src/css-tier-shadow";

/**
 * The two carriers that take the CSS tier's outer shadow out of its own sampled
 * backdrop (W18 G1; charter `2026-09-05-w18-union-contour-residual.md`, Decision
 * Log 2 (1)).
 *
 * These pin the DECISION and the GEOMETRY, which are the two halves that can be
 * wrong without a pixel looking obviously off: a plan that names the wrong host
 * puts a shadow back inside a neighbour's filter, and a clip whose holes miss a
 * member's box darkens that member's body with a shadow the renderer draws as
 * `lift · (1 − coverage)`. The paint order the plan produces is asserted from the
 * tier's own output in `packages/calibration/test/tier-coherence.test.ts` (X7).
 */
describe("the outer shadow's carriers", () => {
  const member = (nodeId: string, clipsChildren = false) => ({ nodeId, clipsChildren });

  it("keeps a lone surface on its own layer and never builds a container for it", () => {
    // Carrier B exists only because a sibling host's filters cannot be painted
    // behind a child of another host. With one host there is no sibling, so the
    // per-surface carrier is the whole answer and the group stays at three
    // elements per surface.
    const plan = planCssTierShadow([member("solo")]);
    expect(plan.carrier).toBe("layer");
    expect(plan.members).toEqual([["solo", "layer"]]);
    expect(plan.groupHostNodeId).toBeUndefined();
  });

  it("hands a group's shadows to its LAST-painted member", () => {
    const plan = planCssTierShadow([member("a"), member("b"), member("c")]);
    expect(plan.carrier).toBe("group");
    expect(plan.groupHostNodeId).toBe("c");
    expect(plan.members.map(([, carrier]) => carrier)).toEqual(["group", "group", "group"]);
  });

  it("falls back per member where the last host clips, and reports the weakest", () => {
    /*
     * A clipping host clips its children to its padding box, so a container on it
     * would crop every member's shadow — and a shadow on such a host's own L3 is
     * cropped the same way, which is why that member goes all the way back to the
     * host and keeps sampling its own shadow. Its siblings do not: carrier A is
     * still exact for a surface's own shadow, and giving it up for every member
     * because one host clips would concede more than the page took away.
     */
    const plan = planCssTierShadow([member("a"), member("b"), member("c", true)]);
    expect(plan.groupHostNodeId).toBeUndefined();
    expect(plan.members).toEqual([
      ["a", "layer"],
      ["b", "layer"],
      ["c", "host"],
    ]);
    expect(plan.carrier).toBe("host");

    // And a lone clipping host is the same fallback with nothing else in it.
    expect(planCssTierShadow([member("solo", true)]).carrier).toBe("host");
  });

  it("frames the container on the hosting host's border box and cuts every member out", () => {
    const casts = [
      {
        nodeId: "a",
        bounds: { x: 100, y: 200, width: 44, height: 44 },
        radii: [22, 22, 22, 22] as const,
        shadow: "0 8px 31px 3px rgba(0, 0, 0, 0.2)",
      },
      {
        nodeId: "b",
        bounds: { x: 156, y: 200, width: 44, height: 44 },
        radii: [22, 22, 22, 22] as const,
        shadow: "0 8px 31px 3px rgba(0, 0, 0, 0.3)",
      },
    ];
    const declarations = cssTierGroupShadowDeclarations({
      hostBounds: casts[1]!.bounds,
      hostBorderWidthCssPx: 1,
      casts,
      reachCssPx: 42.5,
    });

    // The container is framed the way `layerFrame` frames L1, L2 and L3, so its
    // own border box is the hosting host's border box and every caster's offset
    // is a plain difference of two measured rects.
    expect(declarations.container.inset).toBe("-1px");
    expect(declarations.container["z-index"]).toBe("-1");
    expect(declarations.container["pointer-events"]).toBe("none");

    // The casters carry each member's own resolved value; nothing about the
    // amplitude or the geometry is re-derived beside them.
    expect(declarations.casters.map((caster) => caster.nodeId)).toEqual(["a", "b"]);
    expect(declarations.casters[0]?.style.left).toBe("-56px");
    expect(declarations.casters[0]?.style["box-shadow"]).toBe(casts[0]!.shadow);
    expect(declarations.casters[1]?.style.left).toBe("0px");
    expect(declarations.casters[1]?.style["box-shadow"]).toBe(casts[1]!.shadow);

    // One outer rectangle covering the shadows' reach, then one hole per member —
    // three subpaths under `evenodd`, which is what removes every member's body
    // from every member's shadow.
    const clip = declarations.container["clip-path"] ?? "";
    expect(clip.startsWith("path(evenodd, ")).toBe(true);
    expect(clip.split("M ").length - 1).toBe(3);
    // The outer rectangle reaches past the leftmost member by the whole reach.
    expect(clip).toContain("M -98.5 -42.5");
  });
});
