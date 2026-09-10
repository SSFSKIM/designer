/**
 * The toolbar partition — Apple's two ways of splitting a toolbar's shared glass
 * background, as one rule (W27b; the wave's §Design, contract X5).
 *
 * Four claims, and they are the four the charter names:
 *
 *  1. **A split is a sampling-group split, and nothing else.** The children on
 *     either side of a spacer register in different groups; a
 *     `sharedBackground="hidden"` item registers alone; and there is still
 *     exactly one `role="toolbar"`.
 *  2. **The roving tab order does not notice.** `membersOf` orders the stop over
 *     the document by plane anchors, so grouping never reached it — asserted
 *     rather than assumed, because it is the property that makes the partition
 *     free.
 *  3. **The gap is derived.** A spacer's minimum is the sampling padding the
 *     material requires under the *resolved* policy, so it moves when Reduce
 *     Transparency thickens the frost. A constant would be wrong under exactly
 *     the preference that enlarges the blur.
 *  4. **The room is enough.** At the derived gap, neither partition's padded
 *     proxy box reaches the other partition's shapes — which is the predicate
 *     `proxy-overlap-after-enforcement` fires on.
 *
 * Claim 4 is asserted here over the *geometry*, on the same two functions the
 * runtime resolves proxies with, because jsdom lays nothing out: a proxy needs
 * measured members, and a jsdom assertion about one would be asserting a stub.
 * The same claim against real proxies in a real browser is
 * `platform-web`'s `e2e/shared/accessible-padding.spec.ts`.
 */

import { fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { rectsOverlap, type Rect } from "@vitreajs/vitrea";
import { resolveProxyGeometry, samplingPaddingFor } from "@vitreajs/vitrea-web";

import { GlassButton, GlassToolbar, GlassToolbarSpacer } from "../src/index";
import { renderGlass, type Harness } from "./harness";

const groupOf = (harness: Harness, nodeId: string): string | undefined =>
  harness.root().scene.glassNode(nodeId)?.descriptor.groupId;

const spacers = (): HTMLElement[] => [
  ...document.querySelectorAll<HTMLElement>("[data-vitrea-toolbar-spacer]"),
];

/** The minimum a spacer opened, as the layout engine would read it. */
const gapOf = (spacer: HTMLElement | undefined): number =>
  Number.parseFloat(spacer?.style.minWidth ?? "NaN");

describe("a spacer partitions the toolbar", () => {
  it("puts the children on each side of it in different sampling groups", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );

    expect(groupOf(harness, "a")).toBeDefined();
    expect(groupOf(harness, "a")).not.toBe(groupOf(harness, "b"));
  });

  it("is still one toolbar, not two", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );

    expect(harness.result.getAllByRole("toolbar")).toHaveLength(1);
  });

  it("keeps the toolbar's group id on the first partition and suffixes the rest", () => {
    // An unsplit toolbar registers exactly the id it always did; a split cannot
    // register that id twice, so each later partition takes it with its index.
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar" }}>
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="c">Three</GlassButton>
      </GlassToolbar>,
    );

    expect(groupOf(harness, "a")).toBe("toolbar");
    expect(groupOf(harness, "b")).toBe("toolbar-1");
    expect(groupOf(harness, "c")).toBe("toolbar-2");
  });

  it("hands every partition the toolbar's own group props", () => {
    const harness = renderGlass(
      <GlassToolbar
        aria-label="Actions"
        groupProps={{ id: "toolbar", hint: { tone: "dark", luminance: 0.12 } }}
      >
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );

    for (const id of ["toolbar", "toolbar-1"]) {
      expect(harness.root().scene.glassGroup(id)?.descriptor.backdrop?.luminance).toBe(0.12);
    }
  });

  it("does not open a group for a spacer at either end, or for two in a row", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar" }}>
        <GlassToolbarSpacer />
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
        <GlassToolbarSpacer />
      </GlassToolbar>,
    );

    expect(groupOf(harness, "a")).toBe("toolbar");
    expect(groupOf(harness, "b")).toBe("toolbar-1");
    expect(harness.root().scene.glassGroup("toolbar-2")).toBeUndefined();
  });
});

describe("sharedBackgroundVisibility(.hidden)", () => {
  it("gives the item a group of its own and leaves the rest merged", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar" }}>
        <GlassButton nodeId="a">One</GlassButton>
        <GlassButton nodeId="hidden" sharedBackground="hidden">
          Publish
        </GlassButton>
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );

    expect(groupOf(harness, "a")).toBe("toolbar");
    expect(groupOf(harness, "hidden")).toBe("toolbar-1");
    expect(groupOf(harness, "b")).toBe("toolbar-2");
  });

  it("merges the item's own group props over the toolbar's, which is how two tints coexist", () => {
    // One group carries one seed, so a tinted primary action beside a tinted
    // toolbar is only expressible as two groups — the split IS the composition.
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar", tint: "rgb(0 0 255)" }}>
        <GlassButton nodeId="a">One</GlassButton>
        <GlassButton nodeId="hidden" sharedBackground="hidden" groupProps={{ tint: "rgb(255 0 0)" }}>
          Publish
        </GlassButton>
      </GlassToolbar>,
    );

    const shared = harness.root().scene.glassGroup("toolbar")?.descriptor.material?.tint;
    const own = harness.root().scene.glassGroup("toolbar-1")?.descriptor.material?.tint;
    expect(shared).toBeDefined();
    expect(own).toBeDefined();
    expect(shared?.color[2]).toBeGreaterThan(shared?.color[0] ?? 1);
    expect(own?.color[0]).toBeGreaterThan(own?.color[2] ?? 1);
  });

  it("takes an id the item wrote as written, since it names one group and not a series", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar" }}>
        <GlassButton nodeId="a">One</GlassButton>
        <GlassButton nodeId="hidden" sharedBackground="hidden" groupProps={{ id: "primary" }}>
          Publish
        </GlassButton>
      </GlassToolbar>,
    );

    expect(groupOf(harness, "hidden")).toBe("primary");
  });

  it("never lets the two protocol props reach the element", () => {
    renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton sharedBackground="hidden" groupProps={{ tint: "rgb(255 0 0)" }}>
          Publish
        </GlassButton>
      </GlassToolbar>,
    );

    const button = document.querySelector("button");
    expect(button?.getAttribute("sharedBackground")).toBeNull();
    expect(button?.getAttribute("sharedbackground")).toBeNull();
    expect(button?.getAttribute("groupProps")).toBeNull();
    expect(button?.getAttribute("groupprops")).toBeNull();
  });
});

describe("the roving tab order across a split", () => {
  it("is the author's sequence, whatever the grouping is", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton>One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton sharedBackground="hidden">Two</GlassButton>
        <GlassToolbarSpacer kind="flexible" />
        <GlassButton>Three</GlassButton>
      </GlassToolbar>,
    );

    const toolbar = harness.result.getByRole("toolbar");
    const names = ["One", "Two", "Three"].map((name) =>
      harness.result.getByRole("button", { name }),
    );

    // One tab stop for the whole toolbar, on its first item — three groups later
    // as it was with one.
    expect(names.map((item) => item.tabIndex)).toEqual([0, -1, -1]);

    names[0]?.focus();
    fireEvent.keyDown(toolbar, { key: "ArrowRight" });
    expect(document.activeElement).toBe(names[1]);
    fireEvent.keyDown(toolbar, { key: "ArrowRight" });
    expect(document.activeElement).toBe(names[2]);
    fireEvent.keyDown(toolbar, { key: "End" });
    expect(document.activeElement).toBe(names[2]);
    fireEvent.keyDown(toolbar, { key: "Home" });
    expect(document.activeElement).toBe(names[0]);
  });
});

describe("the gap a spacer opens", () => {
  const split = (
    <GlassToolbar aria-label="Actions">
      <GlassButton nodeId="a">One</GlassButton>
      <GlassToolbarSpacer />
      <GlassButton nodeId="b">Two</GlassButton>
    </GlassToolbar>
  );

  it("is the sampling padding the resolved policy requires, not a constant", () => {
    const harness = renderGlass(split);
    harness.run(1);

    const material = harness.root().accessibility.material;
    // The toolbar measured nothing in jsdom, so the members it derives over are
    // empty — the projection at span 0, which is the floor every group starts
    // at and the honest answer for a row with no extent.
    expect(gapOf(spacers()[0])).toBeCloseTo(samplingPaddingFor({ members: [], material }), 6);
  });

  it("grows when Reduce Transparency thickens the frost", () => {
    const nominal = renderGlass(split, { reducedTransparency: false });
    nominal.run(1);
    const atNominal = gapOf(spacers()[0]);
    nominal.result.unmount();

    const reduced = renderGlass(split, { reducedTransparency: true });
    reduced.run(1);
    const atReduced = gapOf(spacers()[0]);

    expect(atReduced).toBeGreaterThan(atNominal);
    expect(atReduced).toBeCloseTo(
      samplingPaddingFor({ members: [], material: reduced.root().accessibility.material }),
      6,
    );
  });

  it("takes the flexible kind's free space without giving up its minimum", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer kind="flexible" />
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );
    harness.run(1);

    const spacer = spacers()[0];
    expect(spacer?.style.flex).toBe("1 1 auto");
    expect(gapOf(spacer)).toBeGreaterThan(0);
  });
});

describe("the room the gap buys", () => {
  /**
   * A toolbar's box bounds its members, and the padding law is monotone in a
   * member's span and extents (`platform-web`'s `proxy-geometry.test.ts`), so
   * the gap derived over the box is an upper bound on either partition's own
   * padding rather than an estimate of it. This is that statement, checked on
   * the two functions the runtime resolves proxies with: at the derived gap
   * neither padded box reaches the other partition's shapes, which is exactly
   * the predicate `proxy-overlap-after-enforcement` fires on.
   */
  const partition = (x: number, material: Parameters<typeof samplingPaddingFor>[0]["material"]) => {
    const members = [
      { nodeId: `${x}-1`, bounds: { x, y: 400, width: 96, height: 44 }, radii: [14, 14, 14, 14] as const },
      { nodeId: `${x}-2`, bounds: { x: x + 108, y: 400, width: 96, height: 44 }, radii: [14, 14, 14, 14] as const },
    ];
    const padding = samplingPaddingFor({
      members: members.map((member) => [member.bounds.width, member.bounds.height] as const),
      material,
    });
    const geometry = resolveProxyGeometry({
      members,
      samplingPadding: padding,
      mergeDistance: padding,
      blurRadius: padding / 3,
      devicePixelRatio: 1,
      maxProxyAreaDevicePx: Number.POSITIVE_INFINITY,
    });
    if (geometry === undefined) throw new Error("the partition measured nothing");
    return geometry;
  };

  for (const reducedTransparency of [false, true]) {
    it(`keeps the two proxies off each other's shapes (reducedTransparency: ${reducedTransparency})`, () => {
      const harness = renderGlass(<GlassToolbar aria-label="Actions" />, { reducedTransparency });
      harness.run(1);
      const material = harness.root().accessibility.material;

      // What the toolbar would open for a row of this size: 420 × 52 contains
      // every member below, so its padding is the larger of the two.
      const gap = samplingPaddingFor({ members: [[420, 52]], material });

      const left = partition(0, material);
      const right = partition(204 + gap, material);

      expect(gap).toBeGreaterThanOrEqual(left.effectivePadding);
      expect(rectsOverlap(left.box, right.clipUnion as Rect)).toBe(false);
      expect(rectsOverlap(right.box, left.clipUnion as Rect)).toBe(false);
      expect([...left.findings, ...right.findings]).toEqual([]);
    });
  }
});
