/**
 * Where the CSS tier's OUTER SHADOW is painted, and the geometry of the two
 * carriers that keep it out of the tier's own sampled backdrop (W18 G1; charter
 * `2026-09-05-w18-union-contour-residual.md`, Decision Log 2 (1)).
 *
 * ## The defect this module exists to remove
 *
 * A `backdrop-filter`'s backdrop is everything painted below the element, and
 * Chromium samples it over the region its blur kernel needs rather than over the
 * filtered element's border box alone. Until W18 the tier drew the outer shadow
 * as a `box-shadow` on the HOST, and the host's three filter layers are that
 * host's own children — painted after it. So every surface blurred its own shadow
 * into its own body, and a later host, whose backdrop contains everything painted
 * before it, blurred its earlier neighbours' shadows in as well. W18 G0 measured
 * both halves by declining the shadow on a scratch bed: the WebGPU tier's interior
 * mean moves by **0.00000** on every cell, this tier's by **+0.0032 to +0.0096**,
 * and the whole of the neighbours' term goes from −0.0058 to +0.0005 on the
 * three-up at the declared spacing of 12 (claims §5.77 §3, `g0/g0-findings.md`).
 * The renderer has no such path: it composites its shadow after it samples.
 *
 * ## Why two carriers and not one
 *
 * A host is a stacking context — the tier writes `isolation: isolate` so its
 * negative-`z` layers have one — and painting order inside a stacking context runs
 * the element's own background and border, then its negative-`z` children in
 * `z-index` order, then its in-flow content. A child of a host can therefore be
 * painted after that host's own filters, and never after a SIBLING host's: the
 * whole of an earlier host's subtree paints before the later host begins. That
 * single fact splits the closure in two.
 *
 *  - **Carrier A, per surface (`layer`).** The shadow joins L3's `box-shadow`
 *    list. L3 is `z-index: -1` where the two filters are −3 and −2, so a surface's
 *    own filters never sample its own shadow. It needs no new element, and L3's
 *    box is exactly the host's border box already — `layerFrame` insets the layer
 *    by the border width from the host's PADDING box, which is the border box —
 *    so the caster box and the corner radius are the host's own with no spread or
 *    radius arithmetic. This is what a single-member group gets, and it is the
 *    per-member fallback inside a group whose last host clips.
 *  - **Carrier B, per group (`group`).** Where a group has more than one member,
 *    every member's shadow has to be painted after every member's filter layers,
 *    which only the group's LAST-PAINTED member can do. So its host carries one
 *    child per member, positioned at that member's own box and radius, each
 *    carrying that member's own shadow, and the whole container is clipped by an
 *    even-odd `clip-path` whose holes are the members' rounded boxes — because the
 *    renderer draws its shadow as `lift · (1 − coverage)` and never on a member's
 *    body. Nothing in it is focusable, hit-testable or announced.
 *  - **The fallback (`host`).** A host whose own computed `overflow` clips its
 *    children clips L3, and a shadow on L3 would be cropped to the padding box —
 *    which is not a dimmer shadow, it is no shadow at all. There the shadow stays
 *    on the host and stays inside the sampled backdrop; the group records that it
 *    did, and `sampledOuterShadowFactor` in `optics.ts` is the bound on what that
 *    costs.
 *
 * The module is pure — no `Document`, no `Element` — so the paint order the
 * carriers produce is a value a test can read. `css-tier-layers.ts` is the module
 * that attaches it, and `packages/calibration/test/tier-coherence.test.ts` (X7)
 * asserts from this output that no filter layer of a group is painted after a
 * shadow the tier paints for that group.
 */

import type { CornerRadii, Rect } from "@vitreajs/vitrea";

import type { StyleDeclarations } from "./css-tier";
import { roundedRectPath } from "./proxy-geometry";

/**
 * Which element carries one surface's outer shadow, and — folded to the weakest
 * of its members — which one a group reports on its resolved state.
 *
 * The ordering `group` > `layer` > `host` is the ordering of how much of the
 * shadow leaves the sampled backdrop: all of it, all of this surface's own, none.
 */
export type CssTierShadowCarrier = "layer" | "group" | "host";

/**
 * One member of a group, as the carrier decision sees it.
 *
 * The members arrive in **document order**, which is the order their hosts paint
 * in: a host is positioned (the tier writes `position: relative` where the author
 * left it static) and carries no `z-index`, so the painting algorithm orders
 * positioned descendants with `z-index: auto` in tree order. The last member of
 * the array is therefore the last-painted one, and it is the only member that can
 * host carrier B.
 */
export interface CssTierShadowMember {
  readonly nodeId: string;
  /** Whether this host's own computed `overflow` clips its children. */
  readonly clipsChildren: boolean;
}

/** What each member got, and what the group reports. */
export interface CssTierShadowPlan {
  /** The group's field on `GlassGroupState` — the weakest carrier any member got. */
  readonly carrier: CssTierShadowCarrier;
  /** Per member, in the order they were given. */
  readonly members: readonly (readonly [string, CssTierShadowCarrier])[];
  /** The member whose host carries every member's shadow, under carrier B. */
  readonly groupHostNodeId?: string;
}

const WEAKEST: Record<CssTierShadowCarrier, number> = { host: 0, layer: 1, group: 2 };

/**
 * Which carrier each member of one group gets, and which the group reports.
 *
 * A lone member never needs carrier B: there is no sibling host whose filters
 * could sample its shadow, so L3 is enough and the group stays at one element per
 * surface. More than one member takes carrier B if the last-painted host can hold
 * it, and falls back to carrier A per member if that host clips — the fallback is
 * per member rather than per group because carrier A is still exact for a
 * surface's OWN shadow, and losing it for every member because one host clips
 * would give up more than the page took away.
 */
export function planCssTierShadow(
  members: readonly CssTierShadowMember[],
): CssTierShadowPlan {
  if (members.length === 0) return { carrier: "layer", members: [] };
  const last = members[members.length - 1] as CssTierShadowMember;
  if (members.length > 1 && !last.clipsChildren) {
    return {
      carrier: "group",
      members: members.map((member) => [member.nodeId, "group"] as const),
      groupHostNodeId: last.nodeId,
    };
  }
  const perMember = members.map(
    (member) => [member.nodeId, member.clipsChildren ? "host" : "layer"] as const,
  );
  let carrier: CssTierShadowCarrier = "layer";
  for (const [, member] of perMember) {
    if (WEAKEST[member] < WEAKEST[carrier]) carrier = member;
  }
  return { carrier, members: perMember };
}

/** One member's shadow, as carrier B has to draw it: its box, its radii, its value. */
export interface CssTierShadowCast {
  readonly nodeId: string;
  /** The host's measured border box, in the viewport's CSS px. */
  readonly bounds: Rect;
  readonly radii: CornerRadii;
  /** The `box-shadow` value `cssTierDeclarations` resolved for this surface. */
  readonly shadow: string;
}

/** The container and its one child per member, ready to be written to the DOM. */
export interface CssTierGroupShadowDeclarations {
  readonly container: StyleDeclarations;
  readonly casters: readonly { readonly nodeId: string; readonly style: StyleDeclarations }[];
}

const px = (value: number): string => `${Math.round(value * 100) / 100}px`;
const round = (value: number): number => Math.round(value * 100) / 100;

/**
 * Carrier B's DOM, as declarations.
 *
 * The container is framed exactly the way the three filter layers are — absolutely
 * positioned and inset by the hosting member's border width from that host's
 * padding box, which puts its own border box on the host's BORDER box — so every
 * caster's offset is a plain difference of two measured rects and no border-box
 * arithmetic is repeated anywhere. Each caster is a box of one member's measured
 * size at one member's radii carrying one member's own resolved shadow value, so
 * the shadow the group paints is the same shadow the surface would have painted
 * for itself; nothing about the amplitude, the offset, the spread or the blur is
 * re-derived here.
 *
 * The clip is the whole point of the container existing rather than the casters
 * being loose children. `clip-path` clips an element and its descendants, so one
 * even-odd path — an outer rectangle covering the shadows' reach, with each
 * member's rounded box as a hole — removes every member's body from every
 * member's shadow in one declaration. That is the renderer's own rule: it draws
 * the shadow as `lift · (1 − coverage)` and paints none of it inside a surface.
 * The holes are cut with `proxy-geometry.ts`'s `roundedRectPath`, the same
 * rounded-rectangle path the backdrop proxies are masked by — one description of
 * a host's silhouette, so a mask and a clip cannot disagree about where a surface
 * ends.
 */
export function cssTierGroupShadowDeclarations(input: {
  readonly hostBounds: Rect;
  readonly hostBorderWidthCssPx: number;
  readonly casts: readonly CssTierShadowCast[];
  /** How far outside the members' boxes a shadow can reach, in CSS px. */
  readonly reachCssPx: number;
}): CssTierGroupShadowDeclarations {
  const { hostBounds, casts, reachCssPx } = input;
  const local = casts.map((cast) => ({
    cast,
    rect: {
      x: round(cast.bounds.x - hostBounds.x),
      y: round(cast.bounds.y - hostBounds.y),
      width: round(cast.bounds.width),
      height: round(cast.bounds.height),
    },
  }));

  const left = Math.min(...local.map((entry) => entry.rect.x)) - reachCssPx;
  const top = Math.min(...local.map((entry) => entry.rect.y)) - reachCssPx;
  const right = Math.max(...local.map((entry) => entry.rect.x + entry.rect.width)) + reachCssPx;
  const bottom = Math.max(...local.map((entry) => entry.rect.y + entry.rect.height)) + reachCssPx;
  const outer = `M ${left} ${top} H ${right} V ${bottom} H ${left} Z`;
  const holes = local.map((entry) => roundedRectPath(entry.rect, entry.cast.radii));

  return {
    container: {
      position: "absolute",
      inset: `-${px(input.hostBorderWidthCssPx)}`,
      "pointer-events": "none",
      "z-index": "-1",
      "clip-path": `path(evenodd, "${[outer, ...holes].join(" ")}")`,
    },
    casters: local.map(({ cast, rect }) => ({
      nodeId: cast.nodeId,
      style: {
        position: "absolute",
        left: px(rect.x),
        top: px(rect.y),
        width: px(rect.width),
        height: px(rect.height),
        "border-radius": cast.radii.map(px).join(" "),
        "pointer-events": "none",
        "box-shadow": cast.shadow,
      },
    })),
  };
}
