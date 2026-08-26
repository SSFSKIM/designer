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
import { HOST_ATTRIBUTES, type GlassHostHandle } from "@vitrea/platform-web";
import { createDriver, createInteractionMachine, type MotionDriver } from "@vitrea/motion";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

import { useGlassRootHandle } from "./context";
import { OutsidePlaneScope } from "./plane-portal";
import { GLASS_CHANNEL_PROPERTIES } from "./interaction";
import { assertSharedCornerReference, smoothingFor, type GlassCornerProfile } from "./shape";
import { GlassSurface } from "./surface";

export type GlassMorphPlacement = "below-start" | "below-end" | "above-start" | "above-end";

export interface GlassMorphState {
  readonly open: boolean;
  /** True while the geometry springs are still travelling. */
  readonly morphing: boolean;
}

export interface GlassMorphProps {
  readonly open: boolean;
  readonly children: (state: GlassMorphState) => ReactNode;
  /** Corner profile of the closed end. The open end must share its reference. */
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
  /** Fired when the geometry settles, with the end it settled at. */
  readonly onMorphEnd?: ((open: boolean) => void) | undefined;
}

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

/** Where the open platter sits relative to the closed footprint. */
function placeOpen(anchor: Rect, size: { width: number; height: number }, placement: GlassMorphPlacement, gap: number): Rect {
  const x = placement.endsWith("start") ? anchor.x : anchor.x + anchor.width - size.width;
  const y = placement.startsWith("below")
    ? anchor.y + anchor.height + gap
    : anchor.y - size.height - gap;
  return { x, y, width: size.width, height: size.height };
}

export function GlassMorph(props: GlassMorphProps): ReactNode {
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
   * placed. Both matter: without the second call there is one frame in which the
   * platter is already out of flow but not yet positioned, and a fixed box with
   * no offsets sits at its static position — which the surrounding layout has
   * just reflowed out from under it.
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
   * A pinned platter is `position: fixed` and its offsets are viewport numbers,
   * so anything that *moves* the spacer invalidates them — not only anything that
   * resizes it. A sibling appearing above it in a column, an ancestor's padding
   * changing, a text node growing two lines: none of those resize the spacer, and
   * all of them leave the platter somewhere the footprint no longer is.
   *
   * So the watch is the spacer's whole containing subtree, and the guard is the
   * anchor itself: a rect equal to the one the drivers are already sitting on is
   * not a reflow. That guard is what keeps this off the per-frame path — the
   * alternative, polling `getBoundingClientRect`, is a layout read every frame in
   * the steady state §Geometry promises none in.
   */
  useEffect(() => {
    if (spacer === null || handle === null) return;

    let last: Rect | null = null;
    const realign = (): void => {
      if (openRef.current || !settledRef.current) return;
      const anchor = anchorRect();
      if (anchor === null) return;
      if (
        last !== null &&
        anchor.x === last.x &&
        anchor.y === last.y &&
        anchor.width === last.width &&
        anchor.height === last.height
      ) {
        return;
      }
      last = anchor;
      retarget(true);
      writeGeometry(handle.host);
    };

    // The chain of boxes the spacer sits inside, up to the plane's host layer or
    // the body. Its top is the subtree a reflow can reach the spacer from: a
    // plane layer is `position: absolute; inset: 0`, so nothing outside one moves
    // what is laid out within it.
    const chain: HTMLElement[] = [];
    for (let node: HTMLElement | null = spacer; node !== null; node = node.parentElement) {
      chain.push(node);
      if (node.dataset.vitreaLayer !== undefined || node === node.ownerDocument.body) break;
    }

    const resize = new ResizeObserver(realign);
    for (const node of chain) resize.observe(node);

    const mutations = new MutationObserver((records) => {
      // vitrea's own per-frame writes land on host elements' `style`, this
      // platter's included. They are the frame loop, not the app's layout.
      const layout = records.some(
        (record) =>
          record.type !== "attributes" ||
          !(record.target instanceof HTMLElement) ||
          !record.target.hasAttribute(HOST_ATTRIBUTES.node),
      );
      if (layout) realign();
    });
    mutations.observe(chain[chain.length - 1] ?? spacer, {
      childList: true,
      subtree: true,
      attributes: true,
      characterData: true,
    });

    window.addEventListener("resize", realign);
    return () => {
      resize.disconnect();
      mutations.disconnect();
      window.removeEventListener("resize", realign);
    };
  }, [anchorRect, handle, retarget, spacer, writeGeometry]);

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

  const surfaceStyle: CSSProperties = {
    ...style,
    // Until the first measurement the platter sits in normal flow, which is what
    // makes the closed footprint whatever the app's own layout says it is.
    position: pinned ? "fixed" : "static",
    overflow: "hidden",
  };

  return (
    <>
      <div
        ref={setSpacer}
        aria-hidden="true"
        data-vitrea-morph-anchor=""
        style={{
          // Holds the closed footprint in the app's layout while the platter is
          // out of flow. Zero until measured, so the first pass measures the
          // platter itself rather than a box that is already reserving space.
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
        data-vitrea-morph-open={open ? "" : undefined}
        // Published because "still travelling" is something a stylesheet and a
        // test both need to see, and because it is the state in which the
        // content inside is deliberately not an activation target.
        data-vitrea-morphing={morphing ? "" : undefined}
        onHost={setHandle}
      >
        <div
          ref={setContent}
          data-vitrea-morph-content=""
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
