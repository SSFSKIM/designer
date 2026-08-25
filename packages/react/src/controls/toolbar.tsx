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

import type { GlassPlane } from "@vitrea/core";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type FocusEvent as ReactFocusEvent,
  type HTMLAttributes,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";

import { GlassGroup, type GlassGroupProps } from "../group";
import { PlanePortal } from "../plane-portal";

/** The attribute a toolbar item marks itself with. Public: tests and dev tools read it. */
export const TOOLBAR_ITEM_ATTRIBUTE = "data-vitrea-toolbar-item";

export type ToolbarItemProps = { readonly "data-vitrea-toolbar-item"?: "" };

const ToolbarContext = createContext<boolean>(false);

/** Props that opt a control into the toolbar's roving tab order. `{}` outside one. */
export function useToolbarItem(): ToolbarItemProps {
  const inToolbar = useContext(ToolbarContext);
  return useMemo(() => (inToolbar ? { [TOOLBAR_ITEM_ATTRIBUTE]: "" as const } : {}), [inToolbar]);
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

const focusableItems = (toolbar: HTMLElement): HTMLElement[] =>
  [...toolbar.querySelectorAll<HTMLElement>(`[${TOOLBAR_ITEM_ATTRIBUTE}]`)].filter(
    (item) => !item.hasAttribute("disabled") && item.getAttribute("aria-disabled") !== "true",
  );

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

  /** Exactly one item is reachable by Tab; the rest are reached by arrows. */
  const roveTo = useCallback(
    (target: HTMLElement | null) => {
      if (toolbar === null) return;
      const items = focusableItems(toolbar);
      const active = target ?? items[0] ?? null;
      for (const item of items) item.tabIndex = item === active ? 0 : -1;
    },
    [toolbar],
  );

  useEffect(() => {
    if (toolbar === null) return;
    roveTo(null);
    // Children come and go — a menu opening, a control disabling itself — and the
    // tab stop has to survive that. Watching the subtree costs nothing until one
    // of those happens.
    const observer = new MutationObserver(() => {
      const items = focusableItems(toolbar);
      const current = items.find((item) => item.tabIndex === 0);
      roveTo(current ?? null);
    });
    observer.observe(toolbar, { childList: true, subtree: true, attributes: true, attributeFilter: ["disabled", "aria-disabled"] });
    return () => observer.disconnect();
  }, [roveTo, toolbar]);

  const onFocus = useCallback(
    (event: ReactFocusEvent<HTMLDivElement>) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.hasAttribute(TOOLBAR_ITEM_ATTRIBUTE)) {
        roveTo(target);
      }
    },
    [roveTo],
  );

  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLDivElement>) => {
      if (toolbar === null) return;
      const items = focusableItems(toolbar);
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
    [orientation, roveTo, toolbar],
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
        <ToolbarContext.Provider value={true}>{children}</ToolbarContext.Provider>
      </div>
    </PlanePortal>
  );

  return group ? <GlassGroup {...groupProps}>{content}</GlassGroup> : content;
}
