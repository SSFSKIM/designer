/**
 * The lens chooser: a button in the configure bar that becomes the lens platter.
 *
 * One glass host for the pair's whole life (`GlassMorph`, matched geometry), so the platter
 * emerges from the control that summoned it and nothing cross-fades. The menu inside is React
 * Aria's hook-level menu with single selection, which gives the rows `menuitemradio` semantics,
 * arrow keys and typeahead without handing placement to a library: the platter's geometry is the
 * material's, not a popover's.
 *
 * The lifecycle is the app's, because the morph carries none of it. Escape and a choice close the
 * platter and hand focus back to the trigger it grew from. Tab and Shift+Tab close it and move on
 * to the bar's neighbours in drawn order (order after, finish before), since the morph's host sits
 * at the end of the plane in document order and the browser's own next stop would be the story. A
 * press anywhere outside the platter, or focus leaving it for another element, closes it and
 * leaves focus where the reader put it: the trigger never takes focus back from a click elsewhere.
 *
 * The platter keeps the trigger's radius (28) and thickness (8) at its open end. A generous 28 is
 * already the rounded rectangle a three-row platter wants, and holding the corner and the
 * thickness fixed means the only thing the morph changes is size, which is what the size law then
 * visibly answers: the 56 px trigger is a thin sheet, the platter a thicker, hazier one.
 */

import { APPLE_LIKE_SMOOTHING, GlassMorph } from "@vitreajs/vitrea-react";
import {
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  type Key,
  type ReactNode,
  type Ref,
  type RefObject,
} from "react";
import { useButton, useMenu, useMenuItem, useMenuTrigger, type AriaMenuProps } from "react-aria";
import {
  Item,
  useMenuTriggerState,
  useTreeState,
  type Node as CollectionNode,
  type TreeState,
} from "react-stately";

import { formatPrice, LENSES, lensById, type LensId } from "./content";

export interface LensMenuHandle {
  open(): void;
}

interface LensMenuProps {
  readonly value: LensId;
  readonly onChange: (value: LensId) => void;
  readonly handleRef?: Ref<LensMenuHandle>;
  /** Focus the bar's next (`forward`) or previous stop; called as Tab leaves the open platter. */
  readonly onTabOut: (direction: "forward" | "backward") => void;
}

type MenuProps = AriaMenuProps<object> & {
  readonly menuRef: RefObject<HTMLUListElement | null>;
  /** Escape or a choice: close, and return focus to the trigger. */
  readonly onClose: () => void;
  /** Tab or Shift+Tab: close, and move to the bar's neighbour. */
  readonly onTabOut: (direction: "forward" | "backward") => void;
  /** Focus left for an element outside the platter: close, and leave it there. */
  readonly onFocusLeave: () => void;
};

function LensRow(props: {
  readonly item: CollectionNode<object>;
  readonly state: TreeState<object>;
  readonly onClose: () => void;
}): ReactNode {
  const ref = useRef<HTMLLIElement>(null);
  const { menuItemProps, isFocused, isSelected } = useMenuItem(
    { key: props.item.key, onClose: props.onClose, closeOnSelect: true },
    props.state,
    ref,
  );
  const lens = lensById(String(props.item.key) as LensId);
  return (
    <li
      {...menuItemProps}
      ref={ref}
      className="platter__row"
      data-focused={isFocused ? "" : undefined}
      data-selected={isSelected ? "" : undefined}
    >
      <span className="platter__check" aria-hidden="true">
        {isSelected ? (
          <svg viewBox="0 0 16 16" width="14" height="14">
            <path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" strokeWidth="1.9"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : null}
      </span>
      <span className="platter__name">{lens.short}</span>
      <span className="platter__price">{formatPrice(lens.price)}</span>
    </li>
  );
}

function LensList(props: MenuProps): ReactNode {
  const state = useTreeState(props);
  const { menuProps } = useMenu(props, state, props.menuRef);
  return (
    <ul
      {...menuProps}
      ref={props.menuRef}
      className="platter"
      onKeyDownCapture={(event) => {
        menuProps.onKeyDownCapture?.(event);
        if (event.key === "Escape") {
          event.stopPropagation();
          props.onClose();
        } else if (event.key === "Tab" && !event.altKey && !event.ctrlKey && !event.metaKey) {
          // Handled here, before the collection's own Tab handling, which would park focus on
          // the list and let the browser continue from the end of the plane.
          event.preventDefault();
          event.stopPropagation();
          props.onTabOut(event.shiftKey ? "backward" : "forward");
        }
      }}
      onBlur={(event) => {
        menuProps.onBlur?.(event);
        const next = event.relatedTarget;
        const host = event.currentTarget.closest("[data-vitrea-morph]");
        if (next instanceof Element && !(host?.contains(next) ?? false)) props.onFocusLeave();
      }}
    >
      {[...state.collection].map((item) => (
        <LensRow key={item.key} item={item} state={state} onClose={props.onClose} />
      ))}
    </ul>
  );
}

/**
 * The trigger's face: every lens name stacked in one grid cell, only the chosen one visible, so the
 * trigger is as wide as its widest label whatever is chosen. The runtime re-measures a host when it
 * resizes, not when a sibling's reflow slides it along the bar, so a bar whose members never change
 * width is a bar whose glass is never drawn where a control used to be.
 */
function TriggerFace(props: { readonly current: LensId | null }): ReactNode {
  return (
    <span className="lens__faces">
      {LENSES.map((option) => (
        <span
          key={option.id}
          className="lens__face"
          data-current={option.id === props.current ? "" : undefined}
        >
          {option.short}
          <svg className="lens__chevron" viewBox="0 0 12 12" width="11" height="11" aria-hidden="true">
            <path d="M2.5 7.5 6 4l3.5 3.5" fill="none" stroke="currentColor" strokeWidth="1.6"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
      ))}
    </span>
  );
}

export function LensMenu(props: LensMenuProps): ReactNode {
  const state = useMenuTriggerState({});
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const { menuTriggerProps, menuProps } = useMenuTrigger<object>({}, state, triggerRef);
  const { buttonProps } = useButton(menuTriggerProps, triggerRef);
  const lens = lensById(props.value);

  useImperativeHandle(props.handleRef, () => ({ open: () => state.open(null) }), [state]);

  // Focus returns to the trigger when the platter closes by Escape or a choice, and only then.
  const restoreFocus = useRef(false);
  const close = useCallback(
    (restore: boolean) => {
      restoreFocus.current = restore;
      state.close();
    },
    [state],
  );
  const wasOpen = useRef(false);
  useEffect(() => {
    if (wasOpen.current && !state.isOpen && restoreFocus.current) triggerRef.current?.focus();
    wasOpen.current = state.isOpen;
    restoreFocus.current = false;
  }, [state.isOpen]);

  // A press anywhere outside the platter closes it. Captured, and read off the event's path, so
  // the press that opened the platter (whose target, the trigger, is gone by now) never counts.
  useEffect(() => {
    if (!state.isOpen) return;
    const onPointerDown = (event: PointerEvent): void => {
      const host = menuRef.current?.closest("[data-vitrea-morph]");
      if (host === null || host === undefined || event.composedPath().includes(host)) return;
      close(false);
    };
    document.addEventListener("pointerdown", onPointerDown, true);
    return () => document.removeEventListener("pointerdown", onPointerDown, true);
  }, [close, state.isOpen]);

  const onTabOut = props.onTabOut;
  const tabOut = useCallback(
    (direction: "forward" | "backward") => {
      close(false);
      onTabOut(direction);
    },
    [close, onTabOut],
  );

  // On a pointer open the trigger has already become the platter by the time the press ends,
  // so focus is re-claimed for the menu after the release (the playground's composition).
  useEffect(() => {
    if (!state.isOpen) return;
    const claim = (): void => {
      requestAnimationFrame(() => {
        const menu = menuRef.current;
        if (menu !== null && !menu.contains(menu.ownerDocument.activeElement)) menu.focus();
      });
    };
    claim();
    document.addEventListener("pointerup", claim);
    return () => document.removeEventListener("pointerup", claim);
  }, [state.isOpen]);

  return (
    // The slot reserves the closed footprint from the first render. The morph's own spacer grows
    // from zero once it has measured the trigger, and without the ghost that growth would slide the
    // order button along the bar on the frame after the runtime had measured it.
    <span className="lens-slot">
    <span className="lens__trigger lens__ghost" aria-hidden="true">
      <TriggerFace current={null} />
    </span>
    <GlassMorph
      open={state.isOpen}
      profile={APPLE_LIKE_SMOOTHING}
      openProfile={APPLE_LIKE_SMOOTHING}
      radius={28}
      openRadius={28}
      thickness={8}
      openThickness={8}
      placement="above-start"
      gap={10}
      groupId="lens"
      nodeId="lens-morph"
      className="lens"
    >
      {({ open }) =>
        open ? (
          <LensList
            {...menuProps}
            menuRef={menuRef}
            aria-label="Choose a lens"
            autoFocus={state.focusStrategy ?? true}
            selectionMode="single"
            disallowEmptySelection
            selectedKeys={[props.value]}
            onSelectionChange={(keys) => {
              if (keys === "all") return;
              const [key] = [...keys] as Key[];
              if (key !== undefined) props.onChange(String(key) as LensId);
            }}
            onClose={() => close(true)}
            onTabOut={tabOut}
            onFocusLeave={() => close(false)}
          >
            {LENSES.map((option) => (
              <Item key={option.id} textValue={`${option.short}, ${formatPrice(option.price)}`}>
                {option.short}
              </Item>
            ))}
          </LensList>
        ) : (
          // A plain button: the platter around it is already the material, and a second glass
          // surface inside it would be glass on glass.
          <button
            {...buttonProps}
            ref={triggerRef}
            type="button"
            className="lens__trigger"
            aria-label={`Lens: ${lens.short}`}
          >
            <TriggerFace current={props.value} />
          </button>
        )
      }
    </GlassMorph>
    </span>
  );
}
