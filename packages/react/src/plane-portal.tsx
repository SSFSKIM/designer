/**
 * Placing a subtree in a plane's host layer, once.
 *
 * X1's sandwich orders a plane by DOM order — optics canvas, host DOM, highlight
 * canvas — so a glass host outside its plane cannot be sequenced at all, and
 * platform-web reports a dev-mode error rather than adopting the element. This is
 * the component that puts it there.
 *
 * It portals only when the subtree is not already inside that plane. That single
 * check is what lets a toolbar portal once and keep its buttons in its own flex
 * flow: without it, every surface would portal independently and a layout would
 * scatter to the plane root.
 */

import type { GlassPlane } from "@vitrea/core";
import { useContext, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { PlaneScopeContext, useGlassRoot } from "./context";

export interface PlanePortalProps {
  readonly plane: GlassPlane;
  readonly children: ReactNode;
}

export function PlanePortal(props: PlanePortalProps): ReactNode {
  const { plane, children } = props;
  const root = useGlassRoot();
  const scope = useContext(PlaneScopeContext);

  const scoped = <PlaneScopeContext.Provider value={plane}>{children}</PlaneScopeContext.Provider>;

  if (scope === plane) return scoped;
  // One commit with nothing rendered, while the root's mount effect runs. Glass
  // is what waits; the app's own content never does.
  if (root === null) return null;
  return createPortal(scoped, root.plane(plane).hostLayer);
}
