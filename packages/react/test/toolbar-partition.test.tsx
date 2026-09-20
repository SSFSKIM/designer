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
 *     material requires under the *resolved* policy — which moves when Reduce
 *     Transparency thickens the frost — and never less than the advisory core's
 *     own overlap check reads off the descriptor. A constant of the toolbar's
 *     own would be wrong under exactly the preference that enlarges the blur.
 *  4. **The room is enough.** At that gap, neither partition's padded proxy box
 *     reaches the other partition's shapes — which is the predicate
 *     `proxy-overlap-after-enforcement` fires on.
 *
 * Claim 4 is asserted here over the *geometry*, on the same two functions the
 * runtime resolves proxies with, because jsdom lays nothing out: a proxy needs
 * measured members, and a jsdom assertion about one would be asserting a stub.
 * The same claim against real proxies in a real browser is
 * `platform-web`'s `e2e/shared/accessible-padding.spec.ts`.
 */

import { fireEvent, render } from "@testing-library/react";
import { act, useState, type ReactNode } from "react";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_GROUP_SAMPLING,
  NOMINAL_ACCESSIBILITY_POLICY,
  rectsOverlap,
  type Rect,
} from "@vitreajs/vitrea";
import {
  COLOR_SCHEME_MEDIA_QUERY,
  macos26MaterialProfileDocument,
  macos27MaterialProfileDocument,
  resolveProxyGeometry,
  samplingPaddingFor,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";

import {
  DEFAULT_CLEAR_DIMMING,
  GlassButton,
  GlassRoot,
  GlassToolbar,
  GlassToolbarSpacer,
} from "../src/index";
import { useGlassRootHandle, type GlassRootHandle } from "../src/context";
import { renderGlass, type Harness } from "./harness";
import { setMediaQuery } from "./setup";

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

  /**
   * Both paddings a split is checked against; the layout has to clear each.
   *
   * Rounded up, because the control is (W29 G4): the derivation is exact and the
   * overlap check that reads it is a strict inequality, so a gap level with the
   * padding to the last bit is one ulp from a finding — which is what happened
   * on the macOS 27 material under Reduce Transparency. A layout opens whole
   * pixels; this mirror opens the same ones.
   */
  const wanted = (harness: Harness): number =>
    Math.ceil(
      Math.max(
        DEFAULT_GROUP_SAMPLING.samplingPadding,
        // The toolbar measured nothing in jsdom, so the members it derives over
        // are empty — the projection at span 0, which is the floor every group
        // starts at and the honest answer for a row with no extent.
        samplingPaddingFor({ members: [], material: harness.root().accessibility.material }),
      ),
    );

  it("clears the padding the material requires and the advisory core checks against", () => {
    const harness = renderGlass(split);
    harness.run(1);

    expect(gapOf(spacers()[0])).toBeCloseTo(wanted(harness), 6);
  });

  it("follows the material's own requirement when Reduce Transparency thickens the frost", () => {
    // The two paddings are allowed to differ, and at today's material core's
    // published advisory is the larger for a row with no extent — so what this
    // asserts is the composition, plus the fact that makes it move: the term
    // that follows the policy rises under the preference that enlarges the blur,
    // and overtakes the advisory on a bar tall enough to need it.
    const nominal = renderGlass(split, { reducedTransparency: false });
    nominal.run(1);
    expect(gapOf(spacers()[0])).toBeCloseTo(wanted(nominal), 6);
    const atNominalPolicy = nominal.root().accessibility.material;
    nominal.result.unmount();

    const reduced = renderGlass(split, { reducedTransparency: true });
    reduced.run(1);
    expect(gapOf(spacers()[0])).toBeCloseTo(wanted(reduced), 6);
    const atReducedPolicy = reduced.root().accessibility.material;

    const bar = [[420, 52]] as const;
    expect(samplingPaddingFor({ members: bar, material: atReducedPolicy })).toBeGreaterThan(
      samplingPaddingFor({ members: bar, material: atNominalPolicy }),
    );
    const tall = [[420, 72]] as const;
    expect(samplingPaddingFor({ members: tall, material: atReducedPolicy })).toBeGreaterThan(
      DEFAULT_GROUP_SAMPLING.samplingPadding,
    );
  });

  it("is taken over every group the toolbar registers, not the row's material alone", () => {
    // The variants are not close: `clear` samples at σ 4 against the regular
    // material's 1.25, so a clear partition wants about three times the room.
    // A gap derived from the row's own material would be a third of what the
    // item beside it needs.
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" groupProps={{ id: "toolbar" }}>
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton
          nodeId="hidden"
          sharedBackground="hidden"
          groupProps={{ variant: "clear", dimming: DEFAULT_CLEAR_DIMMING }}
        >
          Publish
        </GlassButton>
      </GlassToolbar>,
    );
    harness.run(1);

    const material = harness.root().accessibility.material;
    const clear = samplingPaddingFor({ members: [], material, variant: "clear" });
    expect(clear).toBeGreaterThan(samplingPaddingFor({ members: [], material }));
    // `Math.ceil` for the reason `wanted` gives: the control opens whole pixels.
    expect(gapOf(spacers()[0])).toBeCloseTo(
      Math.ceil(Math.max(DEFAULT_GROUP_SAMPLING.samplingPadding, clear)),
      6,
    );
  });

  it("reads the groups that will exist, not the props they all overrode", () => {
    // The mirror of the case above: a clear row every one of whose partitions
    // stepped out and declared `regular` draws no clear material anywhere, so a
    // gap sized for clear would be room reserved for a phantom.
    const harness = renderGlass(
      <GlassToolbar
        aria-label="Actions"
        groupProps={{ id: "toolbar", variant: "clear", dimming: DEFAULT_CLEAR_DIMMING }}
      >
        <GlassButton nodeId="a" sharedBackground="hidden" groupProps={{ variant: "regular" }}>
          One
        </GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b" sharedBackground="hidden" groupProps={{ variant: "regular" }}>
          Two
        </GlassButton>
      </GlassToolbar>,
    );
    harness.run(1);

    const material = harness.root().accessibility.material;
    expect(gapOf(spacers()[0])).toBeCloseTo(wanted(harness), 6);
    expect(gapOf(spacers()[0])).toBeLessThan(
      samplingPaddingFor({ members: [], material, variant: "clear" }),
    );
  });

  it("opens along the toolbar's own axis, so a vertical bar is separated vertically", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions" orientation="vertical">
        <GlassButton nodeId="a">One</GlassButton>
        <GlassToolbarSpacer />
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );
    harness.run(1);

    const spacer = spacers()[0];
    expect(spacer?.style.minWidth).toBe("");
    expect(Number.parseFloat(spacer?.style.minHeight ?? "NaN")).toBeCloseTo(wanted(harness), 6);
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

/**
 * The seam W30 G4 closed: whose material the gap is derived from.
 *
 * `samplingPaddingFor` composes a *document's* optics, and until 0.20.0 the
 * toolbar could name none — the React surface told it which accessibility
 * policy was resolved and never which material document the root had selected,
 * so a page pinned to `macos26MaterialProfileDocument` opened its split at the
 * macOS 27 material's blur (the tracker's "`GlassToolbar` opens its split at the
 * default document's blur"; W30 Decision Log 1 (f)). `GlassRootHandle` now
 * carries the selected document and the toolbar asks its own material's
 * question.
 *
 * The assertions run on the `clear` variant, deliberately. On `regular` at
 * jsdom's span 0 both materials sit under core's published advisory of 24, so
 * the max hides the whole difference and a case written there would pass over a
 * bug; `clear` samples at four times the blur, which is where the material's own
 * requirement is the term in front.
 */
describe("the gap is derived from the document the root selected (W30 Decision Log 1 (f))", () => {
  const clearSplit = (
    <GlassToolbar
      aria-label="Actions"
      groupProps={{ variant: "clear", dimming: DEFAULT_CLEAR_DIMMING }}
    >
      <GlassButton nodeId="a">One</GlassButton>
      <GlassToolbarSpacer />
      <GlassButton nodeId="b">Two</GlassButton>
    </GlassToolbar>
  );

  /** What the document's own active endpoint asks for, composed here as the toolbar composes it. */
  const wantedAt = (
    document: GlassMaterialProfileDocument,
    scheme: "light" | "dark",
    material: Parameters<typeof samplingPaddingFor>[0]["material"],
  ): number =>
    Math.ceil(
      Math.max(
        DEFAULT_GROUP_SAMPLING.samplingPadding,
        samplingPaddingFor({
          members: [],
          material,
          variant: "clear",
          profile: document.active[scheme].patch,
          cssTierMapping: document.cssTierMapping,
        }),
      ),
    );

  it("opens the macOS 26.5 padding on a root pinned to the macOS 26.5 material", () => {
    const harness = renderGlass(clearSplit, {
      materialProfileDocument: macos26MaterialProfileDocument,
    });
    harness.run(1);

    const material = harness.root().accessibility.material;
    const gap = gapOf(spacers()[0]);
    expect(gap).toBeCloseTo(wantedAt(macos26MaterialProfileDocument, "light", material), 6);
    // ...and it is the macOS 26.5 number rather than the default document's,
    // which is the failure itself: the two differ by the whole of the macOS 27
    // CSS crossing, and the old gap was the larger one.
    const atDefault = samplingPaddingFor({ members: [], material, variant: "clear" });
    expect(gap).toBeLessThan(atDefault);
    const at265 = samplingPaddingFor({
      members: [],
      material,
      variant: "clear",
      profile: macos26MaterialProfileDocument.active.light.patch,
      cssTierMapping: macos26MaterialProfileDocument.cssTierMapping,
    });
    expect(atDefault / at265).toBeCloseTo(2.0439, 3);
  });

  it("leaves a root on the default document exactly where it was", () => {
    // The other half of the fix, and the one that says it is a fix rather than a
    // change: every page that never named a document draws the default one, and
    // its gap is derived from the same endpoint it always was.
    const harness = renderGlass(clearSplit);
    harness.run(1);

    const material = harness.root().accessibility.material;
    expect(gapOf(spacers()[0])).toBeCloseTo(
      Math.ceil(
        Math.max(
          DEFAULT_GROUP_SAMPLING.samplingPadding,
          samplingPaddingFor({ members: [], material, variant: "clear" }),
        ),
      ),
      6,
    );
  });

  it("follows the RESOLVED scheme, because one document's two endpoints differ", () => {
    // The scheme is an axis of the material, not only of the colour: the macOS
    // 27 dark endpoint asks for about 7.6 % more room than the light one at the
    // same variant. Before this seam the toolbar took the light endpoint's
    // number under both, which is an UNDER-pad on a dark root — the direction
    // the derivation exists to rule out.
    const harness = renderGlass(clearSplit, { colorScheme: "dark" });
    harness.run(1);

    const material = harness.root().accessibility.material;
    expect(harness.root().colorScheme).toBe("dark");
    expect(gapOf(spacers()[0])).toBeCloseTo(
      wantedAt(macos27MaterialProfileDocument, "dark", material),
      6,
    );
    expect(
      samplingPaddingFor({
        members: [],
        material,
        variant: "clear",
        profile: macos27MaterialProfileDocument.active.dark.patch,
        cssTierMapping: macos27MaterialProfileDocument.cssTierMapping,
      }),
    ).toBeGreaterThan(samplingPaddingFor({ members: [], material, variant: "clear" }));
  });

  it("reads an endpoint that names no patch as the renderer's own constants, not as the default document's", () => {
    // `GlassMaterialEndpoint.patch` is optional because one shipped endpoint has
    // none: the macOS 26.5 light active material IS the renderer's own leaves.
    // `samplingPaddingFor` therefore distinguishes an absent `profile` key from
    // one present and `undefined`, and this is the case that pins it — the two
    // answers are the macOS 26.5 material and the macOS 27 one.
    expect(macos26MaterialProfileDocument.active.light.patch).toBeUndefined();
    const material = NOMINAL_ACCESSIBILITY_POLICY.material;
    expect(
      samplingPaddingFor({ members: [], material, profile: undefined, cssTierMapping: {} }),
    ).toBeCloseTo(11.1, 6);
    expect(samplingPaddingFor({ members: [], material })).toBeCloseTo(22.6875, 6);
  });

  it("reports the document the ROOT selected, not the one the prop currently names", () => {
    /*
     * `GlassRootHandle.materialProfileDocument`'s own contract, which nothing
     * asserted until the W30 G4 review closure (claims §5.160 §9).
     *
     * `createGlassRoot` reads the document ONCE, at construction, and a later
     * prop change does not move the material the page draws. A handle that
     * reported the prop would therefore name a material nothing on the page is
     * made of, and the toolbar would open its split at that material's blur —
     * the same class of defect as the one this block exists for, one layer up.
     * The prop moves here and the handle, and the gap derived from it, do not.
     */
    let handle: GlassRootHandle | undefined;
    let move: ((next: GlassMaterialProfileDocument) => void) | undefined;

    function Capture(): ReactNode {
      handle = useGlassRootHandle();
      return null;
    }

    function Switcher(): ReactNode {
      const [selected, setSelected] = useState<GlassMaterialProfileDocument>(
        macos26MaterialProfileDocument,
      );
      move = setSelected;
      return (
        <GlassRoot autoStart={false} materialProfileDocument={selected}>
          <Capture />
          {clearSplit}
        </GlassRoot>
      );
    }

    render(<Switcher />);
    const root = handle?.root;
    expect(handle?.materialProfileDocument).toBe(macos26MaterialProfileDocument);
    const before = gapOf(spacers()[0]);

    act(() => move?.(macos27MaterialProfileDocument));

    // The root is the same runtime — a document change must not rebuild it, or
    // every registration in the tree would be dropped for a prop it ignores.
    expect(handle?.root).toBe(root);
    expect(handle?.materialProfileDocument).toBe(macos26MaterialProfileDocument);
    expect(gapOf(spacers()[0])).toBe(before);
  });

  it("follows the system scheme under colorScheme='auto', with the prop standing still", () => {
    /*
     * The other half of the scheme axis, and the reason it is polled through the
     * store rather than read off the prop (claims §5.160 §9, the review closure:
     * the case above drives the scheme by prop, and `"auto"` is the mode where
     * the prop cannot move).
     *
     * Under `"auto"` the runtime resolves the scheme against
     * `prefers-color-scheme`, so the answer changes with the system while
     * `GlassRoot`'s props are byte-identical from one render to the next. A gap
     * held from the first frame would under-pad a dark root the moment the
     * reader turned the system dark, which is the unsafe direction the seam's
     * second axis is about.
     */
    const harness = renderGlass(clearSplit, { colorScheme: "auto" });
    harness.run(1);

    const material = harness.root().accessibility.material;
    expect(harness.root().colorScheme).toBe("light");
    expect(gapOf(spacers()[0])).toBeCloseTo(
      wantedAt(macos27MaterialProfileDocument, "light", material),
      6,
    );

    act(() => {
      setMediaQuery(COLOR_SCHEME_MEDIA_QUERY, true);
    });
    harness.run(1);

    expect(harness.root().colorScheme).toBe("dark");
    const wantedDark = wantedAt(macos27MaterialProfileDocument, "dark", material);
    expect(gapOf(spacers()[0])).toBeCloseTo(wantedDark, 6);
    // ...and it is a different number, so the assertion above is about the move
    // rather than about two beds that happen to agree at jsdom's span 0.
    expect(wantedDark).toBeGreaterThan(
      wantedAt(macos27MaterialProfileDocument, "light", material),
    );
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

      // What the toolbar opens for a row of this size: 420 × 52 contains every
      // member below, and the advisory core checks against is the other term.
      const gap = Math.max(
        DEFAULT_GROUP_SAMPLING.samplingPadding,
        samplingPaddingFor({ members: [[420, 52]], material }),
      );

      const left = partition(0, material);
      const right = partition(204 + gap, material);

      // Both checkers: the padding the proxy is built with, and the descriptor's
      // padding core's own overlap check reads.
      expect(gap).toBeGreaterThanOrEqual(left.effectivePadding);
      expect(gap).toBeGreaterThanOrEqual(DEFAULT_GROUP_SAMPLING.samplingPadding);
      expect(rectsOverlap(left.box, right.clipUnion as Rect)).toBe(false);
      expect(rectsOverlap(right.box, left.clipUnion as Rect)).toBe(false);
      expect([...left.findings, ...right.findings]).toEqual([]);
    });
  }
});
