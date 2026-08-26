/**
 * `GlassSurface` — the host primitive.
 *
 * One React element becomes one registered glass host. With `asChild` that
 * element is the app's own (`<GlassSurface asChild><button/></GlassSurface>`
 * renders exactly one `<button>`); without it, a `<div>`.
 *
 * ## Where the element ends up
 *
 * X1 puts every glass host inside its plane's host layer, and platform-web
 * *checks* containment rather than adopting the element — moving a node React
 * rendered would break React's own removal path. So this component portals into
 * `root.plane(plane).hostLayer` itself, which is the "zero setup" half of
 * acceptance #1: an app writes `<GlassButton>` and the host lands where the
 * sandwich can sequence it.
 *
 * A surface already inside that subtree renders in place instead — `GlassToolbar`
 * portals once and its buttons stay in its flex flow. `PlaneScopeContext` is what
 * distinguishes the two cases, so nesting costs nothing and needs no prop.
 *
 * The plane layers are `position: absolute; inset: 0`, so a surface positions
 * itself the way any overlay does. That is not an accident of the implementation:
 * v1 documents arbitrary interleaving with foreign stacking contexts out of
 * contract, and all glass lives in the managed planes.
 *
 * ## The shape props (X8's public sugar)
 *
 * `profile` is `"continuous" | "circular"` or a raw number on the interpolable
 * Figma axis; `radius` is one number, because v1's corner algebra is
 * mirror-symmetric and validated for uniform radii only (X8 rider 3); `capsule`
 * derives the radius from the measured box, where it equals the corner budget and
 * makes the shape an exact stadium.
 *
 * Position and size are never declared. They are measured once per frame in the
 * read phase, which is why press compression is a composed transform rather than
 * a shape change: a transform cannot dirty the rect it is animating.
 */

import type { ForegroundAdaptation, GlassPlane, MaterialVariant } from "@vitreajs/vitrea";
import type { GlassHostHandle } from "@vitrea/platform-web";
import {
  useContext,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactNode,
} from "react";

import { mergeSlotProps, renderAsChild } from "./as-child";
import { GlassGroupContext, useGlassGroupId, useGlassRootHandle } from "./context";
import { useGlassInteraction } from "./interaction";
import { PlanePortal } from "./plane-portal";
import { capsuleRadius, radiiFor, smoothingFor, type GlassCornerProfile } from "./shape";

export interface GlassSurfaceOwnProps {
  /** Register the app's own element instead of rendering a `<div>`. */
  readonly asChild?: boolean | undefined;
  readonly children?: ReactNode | undefined;
  /** Which managed plane this surface lives on. v1 ships `base` and `overlay`. */
  readonly plane?: GlassPlane | undefined;
  /** Paint sequence within the plane. Defaults to registration order. */
  readonly order?: number | undefined;
  /**
   * `clear` is persistently more transparent and **requires** a dimming policy on
   * its group; without one core refuses it, renders regular, and says so.
   */
  readonly variant?: MaterialVariant | undefined;
  readonly profile?: GlassCornerProfile | undefined;
  /** Uniform corner radius in CSS px (X8 rider 3). Ignored when `capsule`. */
  readonly radius?: number | undefined;
  /** Derive the radius from the measured box, making the shape an exact stadium. */
  readonly capsule?: boolean | undefined;
  /** Material thickness in CSS px, driving lensing depth and shadow. */
  readonly thickness?: number | undefined;
  readonly foreground?: ForegroundAdaptation | undefined;
  /** Overrides the group in scope. */
  readonly groupId?: string | undefined;
  readonly nodeId?: string | undefined;
  /** Wire pointer and keyboard events into the interaction machine. */
  readonly interactive?: boolean | undefined;
  readonly disabled?: boolean | undefined;
  /** Held true by a morph in flight. */
  readonly morphing?: boolean | undefined;
  /** Called once the host is registered, and with `null` when it is released. */
  readonly onHost?: ((handle: GlassHostHandle | null) => void) | undefined;
  /**
   * `data-*` attributes pass through to the host element. React's own
   * `HTMLAttributes` has no index signature for them, and a glass surface is
   * exactly the kind of element an app hooks a stylesheet or a test onto.
   */
  readonly [dataAttribute: `data-${string}`]: string | number | boolean | undefined;
}

export type GlassSurfaceProps = GlassSurfaceOwnProps &
  Omit<HTMLAttributes<HTMLElement>, "children" | "color">;

/** Advisory default: a control-sized corner. Calibration (C7) replaces it. */
const DEFAULT_RADIUS = 12;
const DEFAULT_THICKNESS = 8;

export function GlassSurface(props: GlassSurfaceProps): ReactNode {
  const {
    asChild = false,
    children,
    plane: declaredPlane = "base",
    order,
    variant,
    profile,
    radius = DEFAULT_RADIUS,
    capsule = false,
    thickness = DEFAULT_THICKNESS,
    foreground,
    groupId: explicitGroupId,
    nodeId: explicitNodeId,
    interactive = false,
    disabled = false,
    morphing = false,
    onHost,
    ...rest
  } = props;

  const { root, ticker, profile: motionProfile } = useGlassRootHandle();
  const groupId = useGlassGroupId(explicitGroupId);
  const group = useContext(GlassGroupContext);
  const generatedId = useId();
  const nodeId = explicitNodeId ?? `vitrea-node${generatedId}`;

  const [host, setHost] = useState<HTMLElement | null>(null);
  const [handle, setHandle] = useState<GlassHostHandle | null>(null);
  /** Follows cross-plane promotion; the prop stays the declared home. */
  const [activePlane, setActivePlane] = useState<GlassPlane>(declaredPlane);
  const focusToRestore = useRef<HTMLElement | null>(null);

  useEffect(() => setActivePlane(declaredPlane), [declaredPlane]);

  const smoothing = smoothingFor(profile);
  const radii = useMemo(() => radiiFor(radius), [radius]);

  /**
   * Everything that is patchable rather than identity, held in a ref.
   *
   * Registration must not depend on any of it. `<GlassSurface foreground={{ mode:
   * "fixed" }}>` is an inline literal on every render, and re-registering an
   * existing node id is a structural throw in core — so the shape props travel
   * through `update`, and only the id, the group, the plane, the element and the
   * shape *family* can require a new registration.
   */
  const patch = useRef({ radii, smoothing, thickness, order, variant, foreground });
  patch.current = { radii, smoothing, thickness, order, variant, foreground };

  // Held in a ref so a fresh closure each render never re-registers the host.
  const onHostRef = useRef(onHost);
  onHostRef.current = onHost;

  useLayoutEffect(() => {
    if (root === null || host === null) return;

    const initial = patch.current;
    const releaseLease = group?.retain();
    const registered = root.registerHost({
      host,
      groupId,
      nodeId,
      plane: declaredPlane,
      shapeFamily: capsule ? "capsule" : "fixed-rounded-rect",
      radii: initial.radii,
      smoothing: initial.smoothing,
      thickness: initial.thickness,
      ...(initial.order === undefined ? {} : { order: initial.order }),
      ...(initial.variant === undefined ? {} : { variant: initial.variant }),
      ...(initial.foreground === undefined ? {} : { foreground: initial.foreground }),
      // React owns placement, so platform-web must not move the element: it
      // records the parent it inserted into, and its synthetic events are
      // delegated to the portal container the element sits under. The plane
      // change becomes a re-render, and `PlanePortal` moves its own mount node.
      onPlaneChange: (next) => {
        // Reparenting is a removal followed by an insertion, and removing a
        // focused element resets focus to the body. platform-web restores focus
        // when it moves the element itself; a consumer that takes placement over
        // owns the restore too, and a morph that silently dropped keyboard focus
        // would be a real accessibility regression.
        const active = host.ownerDocument.activeElement;
        focusToRestore.current =
          active instanceof HTMLElement && host.contains(active) ? active : null;
        setActivePlane(next);
      },
    });

    setHandle(registered);
    onHostRef.current?.(registered);

    return () => {
      onHostRef.current?.(null);
      setHandle(null);
      registered.release();
      releaseLease?.();
    };
  }, [capsule, declaredPlane, group, groupId, host, nodeId, root]);

  /** Runs after the commit that moved the node, which is when focus is restorable. */
  useLayoutEffect(() => {
    const target = focusToRestore.current;
    focusToRestore.current = null;
    if (target !== null && target.ownerDocument.activeElement !== target) target.focus();
  }, [activePlane]);

  // `foreground` is keyed by content for the same reason the group's policy is:
  // an inline literal is a new object every render, and patching on identity
  // would write the same values forever.
  const foregroundKey = JSON.stringify(foreground);

  useEffect(() => {
    handle?.update({
      radii,
      smoothing,
      thickness,
      ...(order === undefined ? {} : { order }),
      variant,
      foreground: patch.current.foreground,
    });
  }, [foregroundKey, handle, order, radii, smoothing, thickness, variant]);

  /**
   * A capsule's radius is half its shorter side, and only the measured box knows
   * which side that is. Read from the scene rather than the DOM: platform-web
   * already measured it this frame, in the phase that is allowed to.
   */
  useEffect(() => {
    if (!capsule || root === null || handle === null) return;
    let applied = -1;
    return ticker.subscribe(() => {
      const bounds = root.scene.glassNode(handle.nodeId)?.bounds;
      if (bounds === undefined) return;
      const next = capsuleRadius(bounds.width, bounds.height);
      if (Math.abs(next - applied) < 0.5) return;
      applied = next;
      handle.update({ radii: radiiFor(next) });
    });
  }, [capsule, handle, root, ticker]);

  const { handlers } = useGlassInteraction({
    handle,
    host,
    ticker,
    profile: motionProfile,
    interactive,
    disabled,
    morphing,
  });

  /**
   * The interaction handlers chained with the consumer's, never spread over them.
   *
   * `<GlassButton onPointerDown={…}>` is the ordinary way to write this, and a
   * spread would silently drop it: the material would still light up and the
   * app's own handler would never run. `mergeSlotProps` is the same merge
   * `asChild` performs one level down, in the same order — the surface's handler
   * first, then the one the consumer passed.
   */
  const slotProps = {
    ...mergeSlotProps({ ...handlers }, rest),
    ref: setHost,
    "data-vitrea-surface": "",
  };

  const element = asChild ? (
    renderAsChild(children, slotProps)
  ) : (
    <div {...slotProps}>{children}</div>
  );

  return <PlanePortal plane={activePlane}>{element}</PlanePortal>;
}
