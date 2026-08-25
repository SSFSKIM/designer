/**
 * The morph pair (parent acceptance #4): a toolbar button that becomes a menu
 * platter, and the accessible menu that lives inside it.
 *
 * ## Why React Aria's hooks, and not a component library
 *
 * `vitrea-react` takes **no** dependency on an accessibility library (Decision
 * Log #13); the app picks one, and this playground picks the hook-level
 * `react-aria` / `react-stately` packages.
 *
 * The reason is placement. A menu primitive has to supply roles, `aria-expanded`
 * wiring, arrow-key navigation, typeahead and focus management — and vitrea has
 * to supply the geometry, because the platter *is* the morphing glass surface and
 * lives in an overlay plane vitrea owns (X1). Every component-level menu library
 * ships placement as an inseparable part of the menu: React Aria Components'
 * `Popover` and Base UI's `Menu.Positioner` both portal and position the popup
 * themselves, which is precisely the half this composition cannot delegate. The
 * hook packages are the same accessibility implementation with no opinion about
 * where the DOM goes, so they compose instead of competing. (Base UI was also
 * still pre-1.0 at the time of writing, which decided the tie.)
 *
 * Dismissal is deliberately hand-wired rather than taken from `useOverlay`: the
 * trigger sits outside the platter, so an outside-press dismisser would race the
 * press that opened it. Escape, selection, and re-pressing the trigger are what a
 * menu needs, and each is one line.
 */

import { APPLE_LIKE_SMOOTHING, GlassMorph, useToolbarItem } from "vitrea-react";
import { useButton, useMenu, useMenuItem, useMenuTrigger } from "react-aria";
import { Item, useMenuTriggerState, useTreeState } from "react-stately";
import { useEffect, useRef, type Key, type ReactNode, type RefObject } from "react";
import type { AriaMenuProps } from "react-aria";
import type { Node as CollectionNode, TreeState } from "react-stately";

export interface ActionsMenuProps {
  readonly onAction: (key: string) => void;
  /** The menu's accessible name. Defaults to the playground's. */
  readonly label?: string | undefined;
}

/**
 * React Aria's own menu props, plus the two callbacks this composition owns.
 * `onSelect` is separate from `AriaMenuProps["onAction"]` because that one takes
 * the item's value alongside its key, and these items carry none.
 */
type MenuProps = AriaMenuProps<object> & {
  readonly onClose: () => void;
  readonly onSelect: (key: Key) => void;
};

function MenuItem<T>(props: {
  readonly item: CollectionNode<T>;
  readonly state: TreeState<T>;
  readonly onAction: (key: Key) => void;
  readonly onClose: () => void;
}): ReactNode {
  const ref = useRef<HTMLLIElement>(null);
  const { menuItemProps, isFocused } = useMenuItem(
    { key: props.item.key, onAction: props.onAction, onClose: props.onClose },
    props.state,
    ref,
  );

  return (
    <li {...menuItemProps} ref={ref} className="menu__item" data-focused={isFocused}>
      {props.item.rendered}
    </li>
  );
}

function Menu(props: MenuProps & { readonly menuRef: RefObject<HTMLUListElement | null> }): ReactNode {
  const state = useTreeState({ ...props, selectionMode: "none" });
  const { menuProps } = useMenu(props, state, props.menuRef);

  return (
    <ul
      {...menuProps}
      ref={props.menuRef}
      className="menu"
      /*
       * Escape is handled in the capture phase, and chained rather than
       * replacing what React Aria put there.
       *
       * Capture, because the event's target is a menu *item* and the item's own
       * press handling is entitled to stop the bubble before it reaches this
       * element. Chained, because `menuProps.onKeyDownCapture` is part of the
       * collection's keyboard model — overwriting it would silently remove
       * behaviour and leave a menu that only knows how to close.
       */
      onKeyDownCapture={(event) => {
        menuProps.onKeyDownCapture?.(event);
        if (event.key !== "Escape") return;
        event.stopPropagation();
        props.onClose();
      }}
    >
      {[...state.collection].map((item) => (
        <MenuItem
          key={item.key}
          item={item}
          state={state}
          onAction={props.onSelect}
          onClose={props.onClose}
        />
      ))}
    </ul>
  );
}

export function ActionsMenu(props: ActionsMenuProps): ReactNode {
  const state = useMenuTriggerState({});
  const triggerRef = useRef<HTMLButtonElement>(null);
  const { menuTriggerProps, menuProps } = useMenuTrigger<object>({}, state, triggerRef);
  const { buttonProps } = useButton(menuTriggerProps, triggerRef);
  const toolbarItem = useToolbarItem();
  const menuRef = useRef<HTMLUListElement>(null);

  // Focus returns to the trigger on close. React Aria's own restore lives in the
  // `Popover`/`FocusScope` this composition deliberately does without, so the
  // one line it was buying is written here instead.
  const wasOpen = useRef(false);
  useEffect(() => {
    if (wasOpen.current && !state.isOpen) triggerRef.current?.focus();
    wasOpen.current = state.isOpen;
  }, [state.isOpen]);

  /**
   * Put focus in the menu once the press that opened it is over.
   *
   * On a pointer open React Aria focuses the menu container and then hands focus
   * back to the *trigger* when the press ends — and in a morph the trigger has
   * already become the menu, so focus falls to the body and the arrow keys go
   * nowhere. Re-claiming it after the release is the composition's job, not the
   * library's: React Aria is doing the right thing for a trigger that still
   * exists. The keyboard path never needs this, because React Aria focuses an
   * item outright there; running it anyway is a no-op that costs a frame.
   */
  useEffect(() => {
    if (!state.isOpen) return;
    const claim = (): void => {
      requestAnimationFrame(() => {
        const menu = menuRef.current;
        if (menu === null) return;
        if (!menu.contains(menu.ownerDocument.activeElement)) menu.focus();
      });
    };
    claim();
    document.addEventListener("pointerup", claim);
    return () => document.removeEventListener("pointerup", claim);
  }, [state.isOpen]);

  return (
    <GlassMorph
      open={state.isOpen}
      // One profile for both ends, on the interpolable axis. `"continuous"` and
      // `"circular"` are separate fits, and a morph across them is refused
      // rather than blended into a corner nobody measured (Decision Log #22a).
      profile={APPLE_LIKE_SMOOTHING}
      radius={16}
      openRadius={22}
      thickness={8}
      openThickness={16}
      placement="above-start"
      gap={10}
      className="platter"
    >
      {({ open }) =>
        open ? (
          <Menu
            {...menuProps}
            menuRef={menuRef}
            aria-label={props.label ?? "Playground actions"}
            autoFocus={state.focusStrategy ?? true}
            onSelect={(key) => {
              props.onAction(String(key));
              state.close();
            }}
            onClose={() => state.close()}
          >
            <Item key="duplicate">Duplicate</Item>
            <Item key="rename">Rename…</Item>
            <Item key="export">Export as PNG</Item>
            <Item key="delete">Delete</Item>
          </Menu>
        ) : (
          // A plain <button>, not a GlassButton: the platter around it is
          // already the glass surface, and nesting a second one inside it is
          // the same-plane overlap X1 forbids. It still joins the toolbar's
          // roving tab order, because that is a data attribute rather than a
          // property of being glass.
          <button {...buttonProps} {...toolbarItem} ref={triggerRef} className="control" type="button">
            Actions
            <span aria-hidden="true">▾</span>
          </button>
        )
      }
    </GlassMorph>
  );
}
