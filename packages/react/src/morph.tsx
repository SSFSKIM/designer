/**
 * `GlassMorph` — one surface, two shapes (parent acceptance #4).
 *
 * A toolbar button becomes a menu platter as **one continuous material
 * transition**, not a crossfade of two surfaces. That distinction is the whole
 * feature, and it is what dictates the structure here: there is exactly one
 * registered glass host for the pair's whole life, and what interpolates is X8's
 * channel set — `{ center, size, radii, smoothing, thickness }` — every channel a
 * number, every number on its own spring. The DOM content inside the platter
 * swaps; the glass never does.
 *
 * ## Two transitions (W27d)
 *
 * That is `transition="matchedGeometry"`, the default and everything the rest of
 * this comment describes. Apple's `GlassEffectTransition` names a second one, and
 * it is a different transition rather than a cheaper version of the first:
 * `.materialize` brings a surface in **without matching a neighbour's geometry**,
 * "by gradually modulating the light bending and lensing" rather than by fading.
 * `transition="materialize"` is that: two surfaces, each on its own box for its
 * whole life, one handing presence to the other while their contents crossfade.
 * `MaterializeMorph` below owns it, and the two paths share only the placement
 * arithmetic and the reflow watch — a matched morph interpolates where a
 * materialising pair does not, so there is no useful middle layer between them.
 *
 * ## Matched geometry, measured rather than declared
 *
 * Both ends are measured, so a menu whose items grow does not need a hard-coded
 * size. The closed end is a spacer that holds the button's footprint in whatever
 * layout the app wrote; the open end is the platter's own content, laid out at
 * `width: max-content` inside a clipped box, so its natural size is readable on
 * the frame it mounts without ever being painted at that size.
 *
 * ## The corner reference (Decision Log #22a)
 *
 * The two ends must be fit against the *same* reference curve. `"circular"` sits
 * on the Figma smoothing axis and `"continuous"` on the Apple-direct fit, and
 * they are separate fits rather than two points on one axis — an interpolated
 * corner between them has no measured error bound. `assertSharedCornerReference`
 * refuses that pair at the API boundary, where the prop is still nameable.
 *
 * ## Interruption
 *
 * Every channel is an interruptible spring, and opening or closing only
 * `retarget`s: position and velocity carry across untouched. Reversing mid-flight
 * therefore redirects the trajectory the platter is already on. The state channels
 * ride the interaction machine in parallel, and the machine's own `advance`
 * returns the clamped delta the geometry drivers are stepped with, so one capped
 * frame boundary governs the whole morph.
 *
 * ## Unit promotion (X1)
 *
 * Opening promotes the surface to the overlay plane as a unit — body, semantic
 * host and highlight together — so the transition renders on one canvas pair and
 * the platter's glass correctly occludes the toolbar's DOM beneath it. The demotion
 * waits until the closing morph has finished: a plane change mid-flight would be a
 * seam in the middle of the transition the plane exists to avoid.
 */

import type { GlassPlane } from "@vitreajs/vitrea";
import { HOST_ATTRIBUTES, type GlassHostHandle } from "@vitreajs/vitrea-web";
import {
  clampFrameDelta,
  createDriver,
  createInteractionMachine,
  type MotionDriver,
} from "@vitrea/motion";
import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

import { useGlassRootHandle } from "./context";
import { OutsidePlaneScope, PLANE_ANCHOR_ATTRIBUTE } from "./plane-portal";
import { GLASS_CHANNEL_PROPERTIES } from "./interaction";
import { assertSharedCornerReference, smoothingFor, type GlassCornerProfile } from "./shape";
import { GlassSurface } from "./surface";

export type GlassMorphPlacement = "below-start" | "below-end" | "above-start" | "above-end";

/**
 * Which supported transition the pair performs.
 *
 * `matchedGeometry` is one surface travelling between the two ends' shapes, and
 * the default because it is the stronger claim: nothing crossfades, so nothing
 * can double-expose. `materialize` is two surfaces, each on its own geometry,
 * where presence rather than geometry carries the transition — the shape to
 * reach for when the two ends are not the same object seen twice.
 */
export type GlassMorphTransition = "matchedGeometry" | "materialize";

export interface GlassMorphState {
  /**
   * Which end this content is. Under `matchedGeometry` it is the morph's own
   * `open`, because there is one platter and it is at one end at a time; under
   * `materialize` the render prop is called once per end, so it is the end being
   * rendered — the closed end still receives `false` while the morph is open.
   */
  readonly open: boolean;
  /** True while the geometry springs — or the materialize crossfade — travel. */
  readonly morphing: boolean;
}

export interface GlassMorphProps {
  readonly open: boolean;
  readonly children: (state: GlassMorphState) => ReactNode;
  /** Defaults to `matchedGeometry`. Not meant to change over a pair's life. */
  readonly transition?: GlassMorphTransition | undefined;
  /** Corner profile of the closed end. Matched geometry requires a shared reference. */
  readonly profile?: GlassCornerProfile | undefined;
  readonly openProfile?: GlassCornerProfile | undefined;
  readonly radius?: number | undefined;
  readonly openRadius?: number | undefined;
  readonly thickness?: number | undefined;
  readonly openThickness?: number | undefined;
  readonly placement?: GlassMorphPlacement | undefined;
  /** Gap between the closed footprint and the open platter, in CSS px. */
  readonly gap?: number | undefined;
  readonly plane?: GlassPlane | undefined;
  readonly openPlane?: GlassPlane | undefined;
  readonly groupId?: string | undefined;
  readonly nodeId?: string | undefined;
  readonly className?: string | undefined;
  readonly style?: CSSProperties | undefined;
  readonly "aria-label"?: string | undefined;
  /** Fired after geometry, or both material presence and content, reach the requested end. */
  readonly onMorphEnd?: ((open: boolean) => void) | undefined;
}

/**
 * The wrapper each end's `children` are rendered into, named because two
 * independent readers need it: the crossfade writes to it, and the footprint
 * watch has to know those writes are the runtime's own and not the app's layout.
 */
const MORPH_CONTENT_ATTRIBUTE = "data-vitrea-morph-content";

const CLOSED_RADIUS = 14;
const OPEN_RADIUS = 20;
const CLOSED_THICKNESS = 8;
const OPEN_THICKNESS = 14;
const DEFAULT_GAP = 8;

interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

const num = (value: number): string => value.toFixed(3);

const sameRect = (a: Rect, b: Rect | null): boolean =>
  b !== null && a.x === b.x && a.y === b.y && a.width === b.width && a.height === b.height;

/**
 * Call back whenever the layout under the closed footprint moves.
 *
 * A placed platter is `position: fixed` and its offsets are viewport numbers, so
 * anything that *moves* the spacer invalidates them — not only anything that
 * resizes it. A sibling appearing above it in a column, an ancestor's padding
 * changing, a text node growing two lines: none of those resize the spacer, and
 * all of them leave the platter somewhere the footprint no longer is.
 *
 * So the watch is the spacer's whole containing subtree. It deliberately does
 * *not* guard against redundant calls: what counts as a real move is the
 * caller's question, and both callers answer it by comparing the anchor rect
 * they last placed against. That comparison is what keeps this off the per-frame
 * path — the alternative, polling `getBoundingClientRect`, is a layout read
 * every frame in the steady state §Geometry promises none in.
 *
 * `watched` is one more element to observe for resize: the open end's content,
 * whose natural size decides a materialising platter's box and which is not in
 * the spacer's chain at all.
 */
function useFootprintWatch(
  spacer: HTMLElement | null,
  watched: HTMLElement | null,
  active: boolean,
  onReflow: () => void,
): void {
  // Held in a ref so a fresh closure each render never rebuilds the observers.
  const callback = useRef(onReflow);
  callback.current = onReflow;

  useEffect(() => {
    if (spacer === null || !active) return;
    const reflow = (): void => callback.current();

    // The chain of boxes the spacer sits inside, up to the plane's host layer or
    // the body. Its top is the subtree a reflow can reach the spacer from: a
    // plane layer is `position: absolute; inset: 0`, so nothing outside one moves
    // what is laid out within it.
    const chain: HTMLElement[] = [];
    for (let node: HTMLElement | null = spacer; node !== null; node = node.parentElement) {
      chain.push(node);
      if (node.dataset.vitreaLayer !== undefined || node === node.ownerDocument.body) break;
    }

    const resize = new ResizeObserver(reflow);
    for (const node of chain) resize.observe(node);
    if (watched !== null) resize.observe(watched);

    const mutations = new MutationObserver((records) => {
      // vitrea's own per-frame writes land on host elements' `style`, this
      // platter's included. They are the frame loop, not the app's layout.
      //
      // And on this component's own content nodes, which is the same fact one
      // level in: `MaterializeMorph` writes `opacity`, `visibility` and
      // `pointer-events` to them on every frame of a crossfade, and a source end
      // parked on the base plane sits inside the very subtree observed here. Read
      // as layout, those writes call back into `anchorRect` and `sizeOf` — a
      // `getBoundingClientRect` and two offset reads — and force a synchronous
      // layout on every transition frame, in the package whose batched read
      // protocol exists to prevent exactly that.
      const runtime = (target: Node | null): boolean =>
        target instanceof HTMLElement &&
        (target.hasAttribute(HOST_ATTRIBUTES.node) ||
          target.hasAttribute(MORPH_CONTENT_ATTRIBUTE));
      const layout = records.some(
        (record) => record.type !== "attributes" || !runtime(record.target),
      );
      if (layout) reflow();
    });
    mutations.observe(chain[chain.length - 1] ?? spacer, {
      childList: true,
      subtree: true,
      attributes: true,
      characterData: true,
    });

    window.addEventListener("resize", reflow);
    return () => {
      resize.disconnect();
      mutations.disconnect();
      window.removeEventListener("resize", reflow);
    };
  }, [active, spacer, watched]);
}

/** Where the open platter sits relative to the closed footprint. */
function placeOpen(anchor: Rect, size: { width: number; height: number }, placement: GlassMorphPlacement, gap: number): Rect {
  const x = placement.endsWith("start") ? anchor.x : anchor.x + anchor.width - size.width;
  const y = placement.startsWith("below")
    ? anchor.y + anchor.height + gap
    : anchor.y - size.height - gap;
  return { x, y, width: size.width, height: size.height };
}

/**
 * The two transitions are two components, and the switch is a remount.
 *
 * They share no state worth carrying across: one owns seven springs and a single
 * registered host, the other owns two hosts and a crossfade. `transition` is a
 * property of the pair rather than something an app toggles mid-flight, so the
 * remount costs nothing anybody can see and keeps each path's lifecycle honest.
 */
export function GlassMorph(props: GlassMorphProps): ReactNode {
  if (props.transition === "materialize") return <MaterializeMorph {...props} />;
  return <MatchedGeometryMorph {...props} />;
}

function MatchedGeometryMorph(props: GlassMorphProps): ReactNode {
  const {
    open,
    children,
    profile,
    openProfile = profile,
    radius = CLOSED_RADIUS,
    openRadius = OPEN_RADIUS,
    thickness = CLOSED_THICKNESS,
    openThickness = OPEN_THICKNESS,
    placement = "below-start",
    gap = DEFAULT_GAP,
    plane = "base",
    openPlane = "overlay",
    groupId,
    nodeId,
    className,
    style,
    onMorphEnd,
  } = props;

  // Both ends resolved against the same reference, or nothing renders. The
  // refusal is the guarantee; a silently blended corner would be unmeasured.
  assertSharedCornerReference(
    { label: "`profile` (the closed end)", profile },
    { label: "`openProfile` (the open end)", profile: openProfile },
  );

  const { ticker, profile: motionProfile } = useGlassRootHandle();

  const [spacer, setSpacer] = useState<HTMLDivElement | null>(null);
  const [content, setContent] = useState<HTMLDivElement | null>(null);
  const [handle, setHandle] = useState<GlassHostHandle | null>(null);
  const [pinned, setPinned] = useState(false);
  const [morphing, setMorphing] = useState(false);
  const [closedSize, setClosedSize] = useState<{ width: number; height: number } | null>(null);

  const machine = useMemo(() => createInteractionMachine({ profile: motionProfile }), [motionProfile]);

  /** Seeds for the geometry drivers. Only the first values matter; the rest retarget. */
  const seed = useRef({ radius, smoothing: smoothingFor(profile), thickness });

  /**
   * The geometry half of X8, one driver per channel. §Motion gives position,
   * size and radius their own springs: they do not share a `t`, and a solver
   * that assumed they did would be wrong about interruption.
   */
  const drivers = useMemo(() => {
    const { channels } = motionProfile;
    return {
      x: createDriver(channels.position, 0),
      y: createDriver(channels.position, 0),
      width: createDriver(channels.size, 0),
      height: createDriver(channels.size, 0),
      radius: createDriver(channels.radius, seed.current.radius),
      smoothing: createDriver(channels.radius, seed.current.smoothing),
      thickness: createDriver(channels.radius, seed.current.thickness),
    } satisfies Record<string, MotionDriver>;
  }, [motionProfile]);

  const openRef = useRef(open);
  openRef.current = open;
  const settledRef = useRef(true);
  const onMorphEndRef = useRef(onMorphEnd);
  onMorphEndRef.current = onMorphEnd;

  /** The closed footprint, live: it follows whatever layout the app wrote. */
  const anchorRect = useCallback((): Rect | null => {
    if (spacer === null) return null;
    const rect = spacer.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }, [spacer]);

  /**
   * The natural size of whatever end is currently mounted. `width: max-content`
   * on the content node is what makes this readable while the platter itself is
   * still clipped to the other end's box.
   */
  const contentSize = useCallback((): { width: number; height: number } | null => {
    if (content === null) return null;
    return { width: content.offsetWidth, height: content.offsetHeight };
  }, [content]);

  /**
   * The platter's box, from the drivers.
   *
   * Written from the frame loop, and once more the moment the surface is
   * placed. Both matter, and the second one more than it looks: the placing
   * commit is exactly where React drops the explicit zero box the unplaced
   * platter carries (see `surfaceStyle`), and a `fixed` element with no offsets
   * falls back to its *static* position — the plane host layer's origin, which
   * is the box the zero box exists to avoid. Style lands in the commit's
   * mutation phase and this runs in the layout effect after it, so the two are
   * one frame, not two.
   */
  const writeGeometry = useCallback(
    (host: HTMLElement) => {
      host.style.left = `${num(drivers.x.value)}px`;
      host.style.top = `${num(drivers.y.value)}px`;
      host.style.width = `${num(drivers.width.value)}px`;
      host.style.height = `${num(drivers.height.value)}px`;
    },
    [drivers],
  );

  /** Point every geometry driver at the end `open` names. */
  const retarget = useCallback(
    (place: boolean) => {
      const anchor = anchorRect();
      if (anchor === null) return;

      const target = openRef.current
        ? placeOpen(anchor, contentSize() ?? anchor, placement, gap)
        : anchor;

      const geometry: readonly [MotionDriver, number][] = [
        [drivers.x, target.x],
        [drivers.y, target.y],
        [drivers.width, target.width],
        [drivers.height, target.height],
        [drivers.radius, openRef.current ? openRadius : radius],
        [drivers.smoothing, smoothingFor(openRef.current ? openProfile : profile)],
        [drivers.thickness, openRef.current ? openThickness : thickness],
      ];

      for (const [driver, value] of geometry) {
        // Retarget always, jump only when placing. `jumpTo` moves where the
        // channel *is* and deliberately leaves where it is *going* alone — it is
        // the one operation that breaks continuity, so it does not get to decide
        // a destination. Placing without retargeting first therefore drops the
        // surface at the right spot and immediately springs it back to whatever
        // the old target was, which for a fresh driver is zero.
        driver.retarget(value);
        if (place) driver.jumpTo(value, 0);
      }
      if (!place) {
        settledRef.current = false;
        setMorphing(true);
      }
    },
    [anchorRect, contentSize, drivers, gap, openProfile, openRadius, openThickness, placement, profile, radius, thickness],
  );

  /**
   * Measure the closed end, then pin. The pinned box equals the natural one, so
   * the extra commit is invisible.
   *
   * Measured on a frame rather than in a layout effect, and that is not caution:
   * layout effects run child-first, so a surface inside a portalled subtree runs
   * its own measurement before the ancestor that attaches that subtree to the
   * document — and an element in a detached tree measures zero. Waiting for a
   * frame makes the measurement independent of where in a tree the morph sits.
   */
  useEffect(() => {
    if (content === null || pinned) return;
    return ticker.subscribe(() => {
      const width = content.offsetWidth;
      const height = content.offsetHeight;
      if (width === 0 || height === 0) return;
      setClosedSize({ width, height });
      setPinned(true);
    });
  }, [content, pinned, ticker]);

  /**
   * Place once, then only ever animate.
   *
   * The distinction matters more than it looks: `jumpTo` is the one operation
   * that breaks continuity, and a mount is the only moment a surface has no
   * history to be continuous with. Everything after it retargets, including a
   * reversal mid-flight.
   */
  const placed = useRef(false);
  const wasOpen = useRef(open);

  useLayoutEffect(() => {
    if (!pinned || handle === null) return;

    const first = !placed.current;
    const changed = wasOpen.current !== open;
    placed.current = true;
    wasOpen.current = open;
    if (!first && !changed) return;

    // Promote as a unit before the geometry moves, so the whole transition
    // renders on the destination plane's canvas pair.
    if (open && handle.plane !== openPlane) handle.promoteTo(openPlane);

    retarget(first);
    if (first) {
      writeGeometry(handle.host);
      return;
    }
    machine.applyFlags({
      disabled: false,
      morphing: true,
      pressed: false,
      hovered: false,
      focused: false,
    });
  }, [handle, machine, open, openPlane, pinned, retarget, writeGeometry]);

  /**
   * Realign the closed end with its footprint when the layout under it moves.
   *
   * The watch itself is `useFootprintWatch`; what belongs here is when a reflow
   * is allowed to move the platter. Only while it is closed and settled: open,
   * or in flight, its box is the springs' and a jump would be a seam.
   */
  const lastAnchor = useRef<Rect | null>(null);
  useFootprintWatch(spacer, null, handle !== null, () => {
    if (openRef.current || !settledRef.current || handle === null) return;
    const anchor = anchorRect();
    if (anchor === null || sameRect(anchor, lastAnchor.current)) return;
    lastAnchor.current = anchor;
    retarget(true);
    writeGeometry(handle.host);
  });

  useEffect(() => {
    if (handle === null || !pinned) return;
    const host = handle.host;
    let lastRadius = -1;

    return ticker.subscribe((rawDtMs) => {
      // One capped frame boundary for the whole morph: the machine applies the
      // profile's FramePolicy and hands back what it applied.
      const dtMs = machine.advance(rawDtMs);
      if (dtMs > 0) {
        for (const driver of Object.values(drivers)) driver.advance(dtMs);
      }

      writeGeometry(host);
      host.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, num(machine.value("glow")));

      const nextRadius = Math.max(drivers.radius.value, 0);
      if (Math.abs(nextRadius - lastRadius) > 0.25) {
        lastRadius = nextRadius;
        handle.update({
          radii: [nextRadius, nextRadius, nextRadius, nextRadius],
          smoothing: drivers.smoothing.value,
          thickness: drivers.thickness.value,
        });
      }

      // Every channel X8 interpolates, not only the box. A same-box morph — a
      // platter that only rounds its corners or thickens — travels entirely in
      // the shape drivers, and a predicate blind to them calls it settled on the
      // frame it starts.
      const settled = Object.values(drivers).every((driver) => driver.settled);
      if (settled === settledRef.current) return;
      settledRef.current = settled;
      if (!settled) return;

      setMorphing(false);
      machine.applyFlags({
        disabled: false,
        morphing: false,
        pressed: false,
        hovered: false,
        focused: false,
      });
      // Demote only once the platter has finished shrinking: a plane change
      // mid-flight is the seam the overlay plane exists to avoid.
      if (!openRef.current && handle.plane !== plane) handle.promoteTo(plane);
      onMorphEndRef.current?.(openRef.current);
    });
  }, [drivers, handle, machine, pinned, plane, ticker, writeGeometry]);

  const state: GlassMorphState = { open, morphing };

  /*
   * Where the platter logically sits, published for anything that has to reason
   * about the author's sequence rather than the DOM's.
   *
   * The spacer already holds the closed footprint in the app's own layout, which
   * makes it exactly the element that answers "where did this come from" — and
   * the platter itself cannot answer it, because it is hoisted into a plane host
   * layer whose child order is an accident of effect order and of whichever
   * plane it was last promoted to. The platter carries the id as
   * `PLANE_ANCHOR_ATTRIBUTE`, which is how `GlassToolbar` finds it — from the
   * item, upwards, so it works wherever the app marked the item.
   */
  const anchorId = `vitrea-morph-anchor${useId()}`;

  /*
   * Out of flow from the first commit, and empty until it has been placed
   * (Decision Log #28(d)).
   *
   * The platter used to sit in normal flow until the closed end was measured, on
   * the reasoning that flow is what makes the closed footprint the app's own
   * layout. That reasoning was already carried by the spacer above — the platter
   * never contributed to the app's layout at all, because the layout it was in
   * was the *plane host layer's*, and a host layer is `position: absolute;
   * inset: 0` over the viewport. A block-level box there is not "wherever the app
   * put it": it is the full width of the viewport, at the viewport's origin.
   *
   * That box was registered. `GlassSurface` registers in its layout effect and
   * `registerHost` ends in `geometry.track`, which marks the node dirty on the
   * spot, so the next read phase measured it and published it — into
   * `checkSamePlaneOverlap`, which then reported the platter overlapping every
   * surface on the plane, and into `checkGroupProxyOverlap`, which stretched the
   * platter's group's proxy union from the origin to wherever the group really
   * was. The demo's `DESIGN.md` §9 rule 2 is that transient written up as law:
   * keep the top-left corner clear of glass, and give a morph its own group.
   *
   * Ordering cannot close the window. Placement needs a measurement, and the
   * measurement waits for a frame on purpose (see the pin effect above): layout
   * effects run child-first, so a morph inside a portalled subtree would measure
   * itself before the ancestor that attaches that subtree to the document. So the
   * fix is not to place sooner but to claim nothing until placed — an explicitly
   * empty box, which overlaps nothing, unions to nothing a proxy can sample, and
   * hit-tests as nothing. Its measured floor is 2×2 rather than 0×0, because the
   * collapsed platter still paints the 1px border the material gives it and a
   * border-box width cannot go below its own borders; the `realign` effect then
   * moves it onto the spacer's position as soon as anything reflows, so what the
   * scene sees is a point at the footprint rather than a box at the origin.
   *
   * The measurement is unaffected: `contentSize` reads the *content* node, and
   * `width: max-content` is intrinsic, so it resolves from the content itself
   * rather than from the platter that clips it. Rejected on the way here:
   * parking the empty box offscreen instead of at the origin, which reads as
   * tidier and is worse — a group's proxy union is the union of its members'
   * bounds, so a member parked a viewport away drags that union with it, and the
   * one composition it would newly break (a morph sharing a group) is the one
   * this is meant to make safe. Empty is inert wherever it sits; distance is not.
   *
   * The offsets are written out rather than left to `auto` for the same reason
   * `writeGeometry` runs on the placing commit: a `fixed` box with no offsets
   * sits at its *static* position, which is the box this is getting rid of.
   */
  const surfaceStyle: CSSProperties = {
    ...style,
    position: "fixed",
    overflow: "hidden",
    ...(pinned ? {} : { left: 0, top: 0, width: 0, height: 0 }),
  };

  return (
    <>
      <div
        ref={setSpacer}
        id={anchorId}
        aria-hidden="true"
        data-vitrea-morph-anchor=""
        style={{
          // Holds the closed footprint in the app's layout. The platter is out
          // of flow for its whole life, so this is the only element that ever
          // stands in the app's own layout for it — and it is zero until the
          // measurement arrives, because until then there is no footprint to
          // reserve. That growth from zero is a reflow of whatever sits beside
          // it, which is the other half of the demo's §9 law.
          width: closedSize?.width ?? 0,
          height: closedSize?.height ?? 0,
          visibility: "hidden",
          pointerEvents: "none",
        }}
      />
      {/* Outside the surrounding plane scope, so the platter portals into a node
          of its own — which is what lets a promotion move it rather than rebuild
          it. Its box comes from the springs, so it never needed the layout it
          gives up; the spacer above holds its place in the app's own flow. */}
      <OutsidePlaneScope>
      <GlassSurface
        plane={plane}
        radius={radius}
        thickness={thickness}
        morphing={morphing}
        // The platter is the press target while it is collapsed, and stops being
        // one once it is a menu: the content inside it becomes the thing being
        // pressed. This is also why a morph's collapsed content must not be a
        // glass surface of its own — two surfaces nested in one plane is exactly
        // the overlap X1 forbids, and the platter is already the material.
        interactive={!open}
        style={surfaceStyle}
        {...(className === undefined ? {} : { className })}
        {...(profile === undefined ? {} : { profile })}
        {...(groupId === undefined ? {} : { groupId })}
        {...(nodeId === undefined ? {} : { nodeId })}
        {...(props["aria-label"] === undefined ? {} : { "aria-label": props["aria-label"] })}
        data-vitrea-morph=""
        {...{ [PLANE_ANCHOR_ATTRIBUTE]: anchorId }}
        data-vitrea-morph-open={open ? "" : undefined}
        // Published because "still travelling" is something a stylesheet and a
        // test both need to see, and because it is the state in which the
        // content inside is deliberately not an activation target.
        data-vitrea-morphing={morphing ? "" : undefined}
        onHost={setHandle}
      >
        <div
          ref={setContent}
          {...{ [MORPH_CONTENT_ATTRIBUTE]: "" }}
          style={{
            width: "max-content",
            /*
             * Content in flight is not an activation target.
             *
             * A menu activates on pointer *up* — that is the platform behaviour
             * that lets you press a trigger, drag to an item and release on it —
             * and a platter that is still growing slides its items under a
             * cursor that has not moved. Without this, the press that opened the
             * menu picks whichever item happened to arrive under it, and which
             * one that is depends on the frame the release lands in. Interaction
             * resumes the moment the geometry settles.
             */
            pointerEvents: morphing ? "none" : undefined,
          }}
        >
          {children(state)}
        </div>
      </GlassSurface>
      </OutsidePlaneScope>
    </>
  );
}

/**
 * `transition="materialize"` — two surfaces, one presence between them (W27d).
 *
 * Apple's `.materialize` brings glass in "by gradually modulating the light
 * bending and lensing", explicitly *not* by fading it, and it matches no
 * neighbour's geometry. So this path is structurally the opposite of the matched
 * morph above: two registered hosts, each parked on its own measured box for its
 * whole life, and nothing interpolating between them. What travels is presence.
 *
 * ## Presence carries the material; the crossfade carries only content
 *
 * The material's arrival and departure are the `present` prop — X6: presence
 * scales the optical terms and never the element's opacity, on the host or on
 * any ancestor, because an `opacity < 1` anywhere above a host forms a Backdrop
 * Root and kills the group's proxy sampling. The only thing this component fades
 * is the DOM *inside* each platter, which is not material and is not sampled.
 * That is the whole of Apple's "materialize is not a fade" as code: a reader who
 * changes the two `style.opacity` writes below to the hosts breaks sampling and
 * the rule in one edit.
 *
 * ## The end that is not on screen
 *
 * The destination exists from the first `open` until the closing crossfade ends,
 * and then unmounts — the author's open-end content is a menu, and a menu that
 * stays mounted while closed keeps its listeners, its focus management and its
 * place in the tab order. The source stays mounted for the pair's life: it is
 * the control the morph returns to. Whichever end is absent is inert in three
 * independent ways — its material has no presence, its host takes no pointer
 * events, and its content is `visibility: hidden` once the fade has landed,
 * which is also what takes it out of the tab order and the accessibility tree.
 *
 * ## Two ends, two nodes, two ids
 *
 * A `nodeId` names the closed end and the open end is `${nodeId}-open`; without
 * one each `GlassSurface` generates its own. Both ends carry the same
 * `PLANE_ANCHOR_ATTRIBUTE`, because both were hoisted out of the same place in
 * the app's layout and the spacer is still the element that says where.
 *
 * That suffix is therefore RESERVED, and it is published as such in the README:
 * a scene may not carry two nodes under one id, so an app that names another
 * surface `${nodeId}-open` gets core's `duplicate-id` `GlassSceneError` at
 * registration. The alternative — deriving an id nobody could collide with —
 * would cost the readable node id that every capture cell, readout and test
 * identifies this pair's two ends by.
 *
 * ## Reduced Motion
 *
 * Presence steps to its target in the host (the root's resolved policy), and the
 * content crossfade steps with it: the profile arrives already transformed, so
 * `reducedMotionApplied` is the whole test and the two halves cannot disagree.
 */
function MaterializeMorph(props: GlassMorphProps): ReactNode {
  const {
    open,
    children,
    profile,
    openProfile = profile,
    radius = CLOSED_RADIUS,
    openRadius = OPEN_RADIUS,
    thickness = CLOSED_THICKNESS,
    openThickness = OPEN_THICKNESS,
    placement = "below-start",
    gap = DEFAULT_GAP,
    plane = "base",
    openPlane = "overlay",
    groupId,
    nodeId,
    className,
    style,
    onMorphEnd,
  } = props;

  // No `assertSharedCornerReference` here, and the omission is the feature: the
  // refusal exists because an interpolated corner between two fits has no
  // measured error bound (Decision Log #22a), and nothing here interpolates a
  // corner. Each end is drawn at its own profile, on its own reference, for its
  // whole life — so a `"circular"` trigger materialising into a `"continuous"`
  // platter is two measured shapes rather than an unmeasured blend.

  const { ticker, profile: motionProfile } = useGlassRootHandle();

  const [spacer, setSpacer] = useState<HTMLDivElement | null>(null);
  const [sourceContent, setSourceContent] = useState<HTMLDivElement | null>(null);
  const [openContent, setOpenContent] = useState<HTMLDivElement | null>(null);
  const [sourceHandle, setSourceHandle] = useState<GlassHostHandle | null>(null);
  const [openHandle, setOpenHandle] = useState<GlassHostHandle | null>(null);
  const [closedSize, setClosedSize] = useState<Size | null>(null);
  const [openSize, setOpenSize] = useState<Size | null>(null);
  /**
   * The open end exists from the first `open` until its crossfade has landed.
   *
   * Seeded from `open` rather than false, so that a controlled mount at
   * `open={true}` — a menu restored from a URL, a panel an app opens with the
   * page — renders both ends on its first commit instead of committing the
   * closed end alone and then mounting the other from a passive effect one
   * commit later.
   */
  const [mounted, setMounted] = useState(open);
  const [morphing, setMorphing] = useState(false);

  /**
   * The one switch. Everything the transition does hangs off it — which end is
   * present, which way the content crossfade points, which host is inert — so
   * the two halves cannot drift apart, and neither can start before the open end
   * knows where it is: an unplaced platter materialising at the plane layer's
   * origin is exactly the box Decision Log #28(d) got rid of.
   */
  const materialized = open && mounted && openSize !== null;

  /**
   * The content crossfade, on the materialization channel's own driver.
   *
   * The same channel the host drives presence on, because they are two halves of
   * one transition: Apple's `.materialize` fades content while the material
   * materialises. Read from the *root's resolved* profile, so an app that retunes
   * the channel retunes the content with it — the host's own presence is on the
   * default profile, which is why `arrived` below asks the material rather than
   * this driver when the transition is over. Reduced Motion zeroes the duration
   * rather than branching, the same shape §Accessibility gives every other
   * reduction, and `jumpTo` is what makes zero mean *this frame* instead of
   * *next frame*.
   */
  const instant = motionProfile.reducedMotionApplied;
  /**
   * The driver in flight, so that replacing it is a change of TUNING and never a
   * change of state.
   *
   * Both of this memo's inputs move without the transition moving. Reduced
   * Motion is a media query the user can flip mid-flight, and `motionProfile` is
   * an identity: an app that hands `GlassRoot` an inline `profile` object hands
   * it a new one on every render of the root. Seeding the replacement at 0 makes
   * either of those retarget to 1 from nothing and replay the whole crossfade
   * while the material's own presence — which lives in the root and is not
   * reseeded — never moved. So the outgoing driver's value and target are carried
   * across, and only the ramp between them is retuned.
   */
  const outgoingFade = useRef<MotionDriver | null>(null);
  const fade = useMemo(() => {
    const config = motionProfile.channels.materialization;
    const previous = outgoingFade.current;
    const next = createDriver(
      instant && config.kind === "monotonic-ease" ? { ...config, durationMs: 0 } : config,
      previous?.value ?? 0,
    );
    // `createDriver` starts settled, so a driver caught mid-ramp needs its target
    // put back; one that was already settled is left settled rather than pointed
    // at the value it is standing on, which would be a ramp of length zero.
    if (previous !== null && previous.target !== previous.value) next.retarget(previous.target);
    outgoingFade.current = next;
    return next;
  }, [instant, motionProfile]);

  const openRef = useRef(open);
  openRef.current = open;
  const mountedRef = useRef(mounted);
  mountedRef.current = mounted;
  const onMorphEndRef = useRef(onMorphEnd);
  onMorphEndRef.current = onMorphEnd;
  /** The end a change of `open` owes a report to, cleared when it is made. */
  const pendingEnd = useRef<boolean | null>(null);

  /**
   * Whether the transition is over, asked of what actually drew.
   *
   * Not "has the crossfade's driver settled": presence runs in the host, on the
   * *default* profile's materialization channel, while the crossfade here runs on
   * whatever profile the root resolved — so an app that lengthens or shortens the
   * channel makes the two halves different lengths, and only one of them is this
   * component's driver. The material's own published value is the honest answer,
   * and it is the one that decides when the open end may be released: unmounting
   * on the crossfade alone would cut a slower dematerialisation off mid-flight.
   */
  const materializedRef = useRef(materialized);
  materializedRef.current = materialized;
  const sourceHandleRef = useRef(sourceHandle);
  sourceHandleRef.current = sourceHandle;
  const openHandleRef = useRef(openHandle);
  openHandleRef.current = openHandle;
  const arrived = useCallback((): boolean => {
    if (!fade.settled) return false;
    const present = materializedRef.current ? 1 : 0;
    return (
      presenceReached(sourceHandleRef.current, 1 - present) &&
      presenceReached(openHandleRef.current, present)
    );
  }, [fade]);

  const anchorRect = useCallback((): Rect | null => {
    if (spacer === null) return null;
    const rect = spacer.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }, [spacer]);

  /**
   * Place both ends from the live footprint.
   *
   * Run on the commit that measures either end and on every reflow, never per
   * frame: no box here is animated, so there is nothing for a frame loop to
   * interpolate and nothing to keep writing. The open end's size is read live
   * where it can be — a menu whose items grow re-places without a state round
   * trip — and falls back to the measurement that gated `materialized`.
   */
  const place = useCallback(() => {
    const anchor = anchorRect();
    if (anchor === null) return;
    if (sourceHandle !== null && closedSize !== null) writeBox(sourceHandle.host, anchor);
    const size = sizeOf(openContent) ?? openSize;
    if (openHandle !== null && size !== null) {
      writeBox(openHandle.host, placeOpen(anchor, size, placement, gap));
    }
  }, [anchorRect, closedSize, gap, openContent, openHandle, openSize, placement, sourceHandle]);

  /**
   * The crossfade, written straight to the two content nodes.
   *
   * Never declared in JSX, so React has nothing to reset and these writes never
   * fight a re-render — the same division `writeGeometry` keeps in the matched
   * path. `visibility` is what actually removes the absent end: opacity 0 leaves
   * content focusable and readable by assistive technology, and an end that is
   * not on screen must be neither.
   */
  const writeContent = useCallback(() => {
    const alpha = fade.value;
    writeContentAlpha(sourceContent, 1 - alpha, !materialized);
    writeContentAlpha(openContent, alpha, materialized);
  }, [fade, materialized, openContent, sourceContent]);

  /**
   * Take the absent end out of the hit test.
   *
   * It keeps its box for its whole life — presence, not layout, is what removes
   * its material — so without this the open platter's footprint would go on
   * swallowing presses meant for whatever is beneath it.
   *
   * Written imperatively rather than through the `style` prop, and that is not a
   * preference: a plane's host layer is `pointer-events: none` and
   * `registerHost` re-enables the host with an inline `auto`, so a React-managed
   * `pointerEvents` that goes from `"none"` to absent *removes the runtime's
   * own property* and leaves the surface unhittable for good. Measured: the open
   * platter stopped answering `elementFromPoint` entirely.
   */
  const writeHitTesting = useCallback(() => {
    if (sourceHandle !== null) setHitTesting(sourceHandle.host, !materialized);
    if (openHandle !== null) setHitTesting(openHandle.host, materialized);
  }, [materialized, openHandle, sourceHandle]);

  useLayoutEffect(() => {
    place();
    writeContent();
    writeHitTesting();
  }, [place, writeContent, writeHitTesting]);

  /** The open end appears at the first `open` and is released once it has gone. */
  useEffect(() => {
    if (open) setMounted(true);
  }, [open]);

  /** A change of `open` owes exactly one `onMorphEnd`, at the end it lands on. */
  const wasOpen = useRef(open);
  useEffect(() => {
    if (wasOpen.current === open) return;
    wasOpen.current = open;
    pendingEnd.current = open;
  }, [open]);

  /**
   * Point the crossfade at the end `materialized` names.
   *
   * `retarget` re-anchors a monotone ramp on its current value, so a reversal
   * mid-flight continues from where the content actually is rather than
   * restarting — the same interruption rule the matched morph's springs keep,
   * in the one family §Motion allows opacity to use.
   *
   * **Place once, then only ever animate** — the matched path's rule (§Place
   * once, `MatchedMorph`), for the same reason: a mount is the only moment a
   * transition has no history to be continuous with, and `jumpTo` is the one
   * operation that breaks continuity. It matters more here than there, because
   * `materialized` cannot be true on a first commit however `open` arrives: the
   * open end has to be laid out before it can be measured, so a controlled mount
   * at `open={true}` reaches the materialized state one frame late and would
   * otherwise ramp a crossfade the author never asked for on a platter they
   * declared already open.
   *
   * Placement is asked of `open` and not of `materialized`, which is the whole
   * distinction: a closed mount is placed on its first commit because the driver
   * already sits at the end `open` names, and an open one is not placed until the
   * measurement it is waiting for arrives.
   */
  const placedFade = useRef(false);
  useLayoutEffect(() => {
    const target = materialized ? 1 : 0;
    if (fade.target === target) {
      if (open === (target === 1)) placedFade.current = true;
      return;
    }
    const first = !placedFade.current;
    placedFade.current = true;
    if (instant || first) fade.jumpTo(target);
    else fade.retarget(target);
    setMorphing(!arrived());
    writeContent();
  }, [arrived, fade, instant, materialized, open, writeContent]);

  /**
   * Measure each end once, on a frame.
   *
   * On a frame rather than in a layout effect for the reason the matched path
   * gives: layout effects run child-first, so a morph inside a portalled subtree
   * would measure itself before the ancestor that attaches that subtree to the
   * document, and an element in a detached tree measures zero. Both ends are
   * measured from their own `width: max-content` content node, which resolves
   * intrinsically and is therefore readable while the platter clipping it is
   * still the empty box it was registered as.
   */
  useEffect(() => {
    const pending = closedSize === null || (mounted && openSize === null);
    if (!pending) return;
    return ticker.subscribe(() => {
      if (closedSize === null) {
        const size = sizeOf(sourceContent);
        if (size !== null) setClosedSize(size);
      }
      if (mounted && openSize === null) {
        const size = sizeOf(openContent);
        if (size !== null) setOpenSize(size);
      }
    });
  }, [closedSize, mounted, openContent, openSize, sourceContent, ticker]);

  /** The crossfade's frame loop, and the only per-frame work this path does. */
  useEffect(() => {
    return ticker.subscribe((rawDtMs) => {
      // The same capped frame boundary the machine applies in the matched path:
      // a stalled tab resumes a transition rather than finding it over.
      const dtMs = clampFrameDelta(rawDtMs, motionProfile.frame);
      if (dtMs > 0) fade.advance(dtMs);
      writeContent();

      if (!arrived()) {
        setMorphing(true);
        return;
      }
      setMorphing(false);

      // Released only once it has finished dematerialising: unmounting it on the
      // frame the author closed would cut the transition off at its first value.
      if (!openRef.current && mountedRef.current && fade.value <= 0) {
        setMounted(false);
        setOpenSize(null);
      }

      // Reported only when the crossfade is where that end says it should be, so
      // the frame `open` flips — with the open end not yet measured, and the
      // fade still settled at the other end — reports nothing.
      const end = pendingEnd.current;
      if (end !== null && fade.value === (end ? 1 : 0)) {
        pendingEnd.current = null;
        onMorphEndRef.current?.(end);
      }
    });
  }, [arrived, fade, motionProfile, ticker, writeContent]);

  /**
   * Both ends follow the footprint; neither has a box a reflow may not move.
   *
   * Two inputs decide those boxes, so both are compared: the footprint, and the
   * open end's own natural size — a menu that grows a row moves nothing else on
   * the page, and a platter still cut to its old size would clip it.
   */
  const placed = useRef<{ anchor: Rect; open: Size | null } | null>(null);
  useFootprintWatch(spacer, openContent, sourceHandle !== null, () => {
    const anchor = anchorRect();
    if (anchor === null) return;
    const size = sizeOf(openContent);
    const last = placed.current;
    if (last !== null && sameRect(anchor, last.anchor) && sameSize(size, last.open)) return;
    placed.current = { anchor, open: size };
    place();
  });

  const anchorId = `vitrea-morph-anchor${useId()}`;

  /*
   * Out of flow from the first commit, and an explicitly empty box until placed
   * — Decision Log #28(d), which applies to both ends here for the same reason
   * it applied to one: a block-level box in a plane's host layer is the full
   * width of the viewport at the viewport's origin, and registration publishes
   * it to the overlap checks and to the group's proxy union before any
   * measurement exists. Empty overlaps nothing and unions to nothing.
   */
  const boxStyle = (placed: boolean): CSSProperties => ({
    ...style,
    position: "fixed",
    overflow: "hidden",
    ...(placed ? {} : { left: 0, top: 0, width: 0, height: 0 }),
  });

  const shared = {
    ...(className === undefined ? {} : { className }),
    ...(groupId === undefined ? {} : { groupId }),
    morphing,
    "data-vitrea-morph": "",
    [PLANE_ANCHOR_ATTRIBUTE]: anchorId,
    "data-vitrea-morph-open": open ? "" : undefined,
    "data-vitrea-morphing": morphing ? "" : undefined,
  };

  return (
    <>
      <div
        ref={setSpacer}
        id={anchorId}
        aria-hidden="true"
        data-vitrea-morph-anchor=""
        style={{
          width: closedSize?.width ?? 0,
          height: closedSize?.height ?? 0,
          visibility: "hidden",
          pointerEvents: "none",
        }}
      />
      <OutsidePlaneScope>
        <GlassSurface
          {...shared}
          plane={plane}
          radius={radius}
          thickness={thickness}
          present={!materialized}
          // The closed end is the press target while it is the one on screen,
          // exactly as the matched platter is: its content is a label, not a
          // control, and the material under it is what is being pressed.
          interactive={!materialized}
          style={boxStyle(closedSize !== null)}
          {...(profile === undefined ? {} : { profile })}
          {...(nodeId === undefined ? {} : { nodeId })}
          {...(props["aria-label"] === undefined ? {} : { "aria-label": props["aria-label"] })}
          data-vitrea-morph-end="source"
          data-vitrea-morph-present={materialized ? undefined : ""}
          onHost={setSourceHandle}
        >
          <div ref={setSourceContent} {...{ [MORPH_CONTENT_ATTRIBUTE]: "" }} style={CONTENT_STYLE}>
            {children({ open: false, morphing })}
          </div>
        </GlassSurface>
      </OutsidePlaneScope>
      {!mounted ? null : (
        <OutsidePlaneScope>
          <GlassSurface
            {...shared}
            plane={openPlane}
            radius={openRadius}
            thickness={openThickness}
            present={materialized}
            style={boxStyle(openSize !== null)}
            {...(openProfile === undefined ? {} : { profile: openProfile })}
            {...(nodeId === undefined ? {} : { nodeId: `${nodeId}-open` })}
            data-vitrea-morph-end="destination"
            data-vitrea-morph-present={materialized ? "" : undefined}
            onHost={setOpenHandle}
          >
            <div ref={setOpenContent} {...{ [MORPH_CONTENT_ATTRIBUTE]: "" }} style={CONTENT_STYLE}>
              {children({ open: true, morphing })}
            </div>
          </GlassSurface>
        </OutsidePlaneScope>
      )}
    </>
  );
}

interface Size {
  width: number;
  height: number;
}

/**
 * Constant, and that is load-bearing: `opacity`, `visibility` and
 * `pointerEvents` on these nodes are written from the frame loop, and a style
 * object whose values changed between renders would have React overwrite them.
 */
const CONTENT_STYLE: CSSProperties = { width: "max-content" };

const sameSize = (a: Size | null, b: Size | null): boolean =>
  a === null || b === null ? a === b : a.width === b.width && a.height === b.height;

/** A content node's natural size, or `null` while it is still unlaid-out. */
function sizeOf(content: HTMLElement | null): Size | null {
  if (content === null) return null;
  const width = content.offsetWidth;
  const height = content.offsetHeight;
  return width === 0 || height === 0 ? null : { width, height };
}

/**
 * Whether a host's *published* presence has reached a value.
 *
 * Read off the inline custom property the root writes each frame — the same
 * number the renderer and the CSS tier consume — rather than off any driver this
 * component owns, because the driver this component owns is not the one that
 * moves the material.
 */
function presenceReached(handle: GlassHostHandle | null, target: number): boolean {
  if (handle === null) return true;
  const raw = handle.host.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES.materialization);
  const value = raw === "" ? 1 : Number.parseFloat(raw);
  return Math.abs(value - target) < 1e-3;
}

/** `auto` is what `registerHost` writes; a host layer under it is `none`. */
function setHitTesting(host: HTMLElement, enabled: boolean): void {
  host.style.setProperty("pointer-events", enabled ? "auto" : "none");
}

function writeBox(host: HTMLElement, box: Rect): void {
  host.style.left = `${num(box.x)}px`;
  host.style.top = `${num(box.y)}px`;
  host.style.width = `${num(box.width)}px`;
  host.style.height = `${num(box.height)}px`;
}

/**
 * One end's content at one moment of the crossfade.
 *
 * Content in flight is not an activation target, for the reason the matched
 * morph gives: a menu activates on pointer *up*, and a platter still arriving
 * slides its items under a cursor that has not moved.
 *
 * `arriving` is the end the transition is travelling TOWARD, and it is what
 * decides `visibility` — not this end's instantaneous alpha. The two differ for
 * exactly one commit at each reversal, and that commit is the one that matters:
 * `materialized` flips on the layout pass while the driver is still at the value
 * it had, so on a close the SOURCE is written at alpha 0 on the same commit the
 * app is told the menu shut. Hidden there, it is out of the tab order and out of
 * the accessibility tree, and an app's close-time `focus()` on it — the ordinary
 * way a menu returns focus to its trigger — is a silent no-op; focus then falls
 * to `<body>` when the open end unmounts. Reading the direction instead is also
 * what this component's own contract says (§Two ends: an end is hidden "once the
 * fade has landed", not the moment it is pointed away from) and what claims
 * §5.132 §5 says: absent content is hidden from hit testing, focus and the
 * accessibility tree, and the end a transition is arriving at is not absent.
 *
 * An arriving end at alpha 0 is transparent, focusable and readable, which is
 * what a return of focus needs and is not element opacity in X6's sense: it is
 * app content inside the platter, never the host or an ancestor of one.
 */
function writeContentAlpha(content: HTMLElement | null, alpha: number, arriving: boolean): void {
  if (content === null) return;
  content.style.opacity = num(alpha);
  content.style.visibility = alpha <= 0 && !arriving ? "hidden" : "";
  content.style.pointerEvents = alpha >= 1 ? "" : "none";
}
