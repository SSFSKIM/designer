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
 *
 * Note for an app: a plane's DOM is vitrea's, and it sits outside every landmark
 * the page wrote. Content portalled into a plane should be given a place in the
 * document's structure — a `<nav>`, or a named `role="region"` — because nothing
 * else can do it from here.
 *
 * ## Why the portal target is a node this component owns
 *
 * A portalled subtree changes planes by moving that node, never by being given a
 * different container. Two independent reasons, and each on its own is decisive:
 *
 * - **React cannot relocate DOM it has already committed.** Handing `createPortal`
 *   a new container tears the subtree down and builds a new one, which for a glass
 *   surface means releasing its host and registering a fresh node mid-transition.
 * - **React's synthetic events are delegated to the portal's container.** Moving
 *   the *host element* out from under its container instead — the obvious
 *   alternative — leaves it rendered and styled but deaf: no click, no keydown,
 *   nothing. Moving the container takes the listeners with it.
 *
 * The mount node is `display: contents`, so it has no box of its own and the
 * subtree lays out exactly as if it were a direct child of the host layer.
 */

import type { GlassPlane } from "@vitrea/core";
import { useContext, useLayoutEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { PlaneScopeContext, useGlassRoot } from "./context";

export interface PlanePortalProps {
  readonly plane: GlassPlane;
  readonly children: ReactNode;
}

/** Attribute on the mount node. Public, because tests and dev tooling read it. */
export const PLANE_MOUNT_ATTRIBUTE = "data-vitrea-mount";

function createMountNode(): HTMLElement {
  const element = document.createElement("div");
  element.setAttribute(PLANE_MOUNT_ATTRIBUTE, "");
  element.style.display = "contents";
  return element;
}

export function PlanePortal(props: PlanePortalProps): ReactNode {
  const { plane, children } = props;
  const root = useGlassRoot();
  const scope = useContext(PlaneScopeContext);
  /**
   * Fixed for the subtree's life. Switching between rendering in place and
   * rendering through a portal *is* a rebuild whatever the container, so a
   * surface that expects to change planes declares it up front by rendering
   * outside any plane scope (`OutsidePlaneScope`).
   */
  const [inline] = useState(() => scope === plane);

  // Detached at creation, so building it during render observes nothing. It is
  // adopted by a plane below, and never replaced — that is the point.
  const [mount] = useState(() => (inline ? null : createMountNode()));

  useLayoutEffect(() => {
    if (mount === null || root === null) return;
    // `append` moves an already-parented node, so a plane change is a move.
    root.plane(plane).hostLayer.append(mount);
    return () => mount.remove();
  }, [mount, plane, root]);

  const scoped = <PlaneScopeContext.Provider value={plane}>{children}</PlaneScopeContext.Provider>;

  if (inline || mount === null) return scoped;
  // One commit with nothing rendered, while the root's mount effect runs. Glass
  // is what waits; the app's own content never does.
  if (root === null) return null;
  return createPortal(scoped, mount);
}

/**
 * Render a subtree outside any plane scope, so the surfaces inside it portal
 * themselves rather than rendering in place.
 *
 * The one case that needs it is a surface that will change planes: a promotion
 * has to be a move, and only a portalled subtree owns a node that can be moved.
 */
export function OutsidePlaneScope(props: { readonly children: ReactNode }): ReactNode {
  return <PlaneScopeContext.Provider value={null}>{props.children}</PlaneScopeContext.Provider>;
}
