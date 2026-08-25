/**
 * `GlassToolbar` — the group container, with the WAI-ARIA toolbar pattern.
 *
 * Two things at once, and they are the same thing seen from two sides:
 *
 * - **A sampling group.** Members of one `GlassGroup` share a backdrop source and
 *   a proxy, and their fields union with bounded smooth-min proximity, which is
 *   what makes a row of buttons read as one piece of material rather than several.
 *   That is Apple's `GlassEffectContainer`, and it is why a toolbar creates a
 *   group by default.
 * - **A toolbar.** `role="toolbar"` with one tab stop: Tab reaches the toolbar,
 *   arrows move within it. A row of ten buttons that each take a tab stop is the
 *   thing this pattern exists to prevent.
 *
 * The toolbar is deliberately **not** a glass surface. X1 forbids two glass
 * surfaces overlapping inside one plane — the sandwich cannot put one surface's
 * body above another surface's label — so a glass platter wrapping glass buttons
 * would be a checked dev-mode error. The container is plain DOM; the material
 * comes from its members' union.
 *
 * Tab stops are managed on the DOM rather than through props. An item declares
 * itself with a data attribute and nothing else, so a custom control in a toolbar
 * joins the roving order by rendering `useToolbarItem()`'s props — no index, no
 * registration order, and nothing to keep in sync when children reorder.
 */

import type { GlassPlane } from "@vitreajs/vitrea";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useState,
  type FocusEvent as ReactFocusEvent,
  type HTMLAttributes,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

import { GlassGroup, type GlassGroupProps } from "../group";
import { PlanePortal } from "../plane-portal";

/**
 * The attribute a toolbar item marks itself with, carrying its toolbar's id.
 *
 * The id matters because membership is not containment. A control that portals
 * itself — a morph platter that will be promoted to the overlay plane, for
 * instance — is not a DOM descendant of the toolbar, and it is still one of its
 * items: it is reachable with the arrows, it holds the single tab stop when it is
 * the active one, and a screen reader should read it inside the toolbar. Marking
 * the owner lets the toolbar find its items wherever they ended up.
 */
export const TOOLBAR_ITEM_ATTRIBUTE = "data-vitrea-toolbar-item";

export type ToolbarItemProps = { readonly "data-vitrea-toolbar-item"?: string };

const ToolbarContext = createContext<string | null>(null);

/** Props that opt a control into the toolbar's roving tab order. `{}` outside one. */
export function useToolbarItem(): ToolbarItemProps {
  const toolbarId = useContext(ToolbarContext);
  return useMemo(
    () => (toolbarId === null ? {} : { [TOOLBAR_ITEM_ATTRIBUTE]: toolbarId }),
    [toolbarId],
  );
}

export type ToolbarOrientation = "horizontal" | "vertical";

export interface GlassToolbarProps
  extends Omit<HTMLAttributes<HTMLDivElement>, "role" | "onKeyDown"> {
  readonly children?: ReactNode | undefined;
  readonly "aria-label"?: string | undefined;
  readonly orientation?: ToolbarOrientation | undefined;
  readonly plane?: GlassPlane | undefined;
  /**
   * Create a `GlassGroup` for the members. `false` puts them in the group already
   * in scope, which is what two adjacent toolbars sharing one proxy would want.
   */
  readonly group?: boolean | undefined;
  readonly groupProps?: Omit<GlassGroupProps, "children"> | undefined;
}

/**
 * This toolbar's items, in document order, wherever they live.
 *
 * Searched from the document rather than from the toolbar element, because a
 * portalled or promoted item is still a member — see `TOOLBAR_ITEM_ATTRIBUTE`.
 * `querySelectorAll` returns document order, which for a toolbar whose items sit
 * in one row is the reading order the arrows should follow.
 */
const itemsOf = (toolbar: HTMLElement, toolbarId: string): HTMLElement[] => {
  const selector = `[${TOOLBAR_ITEM_ATTRIBUTE}="${CSS.escape(toolbarId)}"]`;
  return [...toolbar.ownerDocument.querySelectorAll<HTMLElement>(selector)].filter(
    (item) => !item.hasAttribute("disabled") && item.getAttribute("aria-disabled") !== "true",
  );
};

export function GlassToolbar(props: GlassToolbarProps): ReactNode {
  const {
    children,
    orientation = "horizontal",
    plane = "base",
    group = true,
    groupProps,
    ...rest
  } = props;

  const [toolbar, setToolbar] = useState<HTMLDivElement | null>(null);
  const generatedId = useId();
  const toolbarId = `vitrea-toolbar${generatedId}`;

  /** Exactly one item is reachable by Tab; the rest are reached by arrows. */
  const roveTo = useCallback(
    (target: HTMLElement | null) => {
      if (toolbar === null) return;
      const items = itemsOf(toolbar, toolbarId);
      const active = target ?? items[0] ?? null;
      for (const item of items) item.tabIndex = item === active ? 0 : -1;

      /*
       * `aria-owns` for the items that are not descendants.
       *
       * Membership is not containment here, and the accessibility tree has to
       * agree with the arrows: an item a screen reader hears outside the toolbar
       * while Tab and the arrows treat it as inside is worse than either
       * behaviour alone. `aria-owns` is the platform's own answer to that, and
       * an id is assigned where the item has none because that is what it takes.
       */
      const external = items.filter((item) => !toolbar.contains(item));
      for (const item of external) {
        if (item.id === "") item.id = `${toolbarId}-item-${external.indexOf(item)}`;
      }
      const owns = external.map((item) => item.id).join(" ");
      if (owns === "") toolbar.removeAttribute("aria-owns");
      else toolbar.setAttribute("aria-owns", owns);
    },
    [toolbar, toolbarId],
  );

  useEffect(() => {
    if (toolbar === null) return;
    roveTo(null);
    /*
     * Items come and go — a menu opening, a control disabling itself, a platter
     * promoted to another plane — and the tab stop has to survive all of it.
     * Watching the whole document is what membership-without-containment costs;
     * it is filtered to the mutations that can change the item set, and it costs
     * nothing until one happens.
     */
    const observer = new MutationObserver(() => {
      const items = itemsOf(toolbar, toolbarId);
      const current = items.find((item) => item.tabIndex === 0);
      roveTo(current ?? null);
    });
    observer.observe(toolbar.ownerDocument.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["disabled", "aria-disabled", TOOLBAR_ITEM_ATTRIBUTE],
    });
    return () => observer.disconnect();
  }, [roveTo, toolbar, toolbarId]);

  const onFocus = useCallback(
    (event: ReactFocusEvent<HTMLDivElement>) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.getAttribute(TOOLBAR_ITEM_ATTRIBUTE) === toolbarId) {
        roveTo(target);
      }
    },
    [roveTo, toolbarId],
  );

  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLDivElement>) => {
      if (toolbar === null) return;
      const items = itemsOf(toolbar, toolbarId);
      if (items.length === 0) return;

      const next = orientation === "horizontal" ? "ArrowRight" : "ArrowDown";
      const previous = orientation === "horizontal" ? "ArrowLeft" : "ArrowUp";

      const active = document.activeElement;
      const index = active instanceof HTMLElement ? items.indexOf(active) : -1;

      let target: HTMLElement | undefined;
      if (event.key === next) target = items[(index + 1 + items.length) % items.length];
      else if (event.key === previous) target = items[(index - 1 + items.length) % items.length];
      else if (event.key === "Home") target = items[0];
      else if (event.key === "End") target = items[items.length - 1];
      else return;

      if (target === undefined) return;
      event.preventDefault();
      roveTo(target);
      target.focus();
    },
    [orientation, roveTo, toolbar, toolbarId],
  );

  const content = (
    <PlanePortal plane={plane}>
      <div
        {...rest}
        ref={setToolbar}
        role="toolbar"
        aria-orientation={orientation}
        onFocus={onFocus}
        onKeyDown={onKeyDown}
      >
        <ToolbarContext.Provider value={toolbarId}>{children}</ToolbarContext.Provider>
      </div>
    </PlanePortal>
  );

  return group ? <GlassGroup {...groupProps}>{content}</GlassGroup> : content;
}
