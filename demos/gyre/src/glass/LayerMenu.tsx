/**
 * The actions menu: a `GlassMorph` whose closed end is a plain trigger button and
 * whose open end is a menu. One registered glass host for the pair's whole life;
 * the DOM inside swaps, the glass never does.
 *
 * The menu's accessibility is written by hand rather than taken from a library:
 * `role="menu"`, arrow keys, Home and End, Escape, and focus returned to the
 * trigger on close, which is the whole of what a four-item menu needs. It sits in
 * a sampling group of its own (DESIGN.md §9), because an unplaced platter joins
 * its group's sampling union.
 */

import { APPLE_LIKE_SMOOTHING, GlassGroup, GlassMorph } from "@vitreajs/vitrea-react";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";

import { FIELD_TEXTURE_ID } from "../field/Field";

export interface MenuAction {
  readonly id: string;
  readonly label: string;
}

export interface LayerMenuProps {
  readonly label: string;
  readonly actions: readonly MenuAction[];
  /** Where the platter opens relative to the trigger. */
  readonly placement: "above-end" | "below-end";
  readonly onAction: (id: string) => void;
}

export function LayerMenu(props: LayerMenuProps): ReactNode {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const menuId = useId();
  const wasOpen = useRef(false);

  useEffect(() => {
    if (open) {
      // Focus the first item once the platter has been placed.
      const frame = requestAnimationFrame(() => {
        menuRef.current?.querySelector<HTMLElement>("[role=menuitem]")?.focus();
      });
      return () => cancelAnimationFrame(frame);
    }
    if (wasOpen.current) triggerRef.current?.focus();
    return undefined;
  }, [open]);

  useEffect(() => {
    wasOpen.current = open;
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent): void => {
      const target = event.target;
      if (!(target instanceof Node)) return;
      if (menuRef.current?.contains(target)) return;
      setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  const focusItem = (offset: number, absolute?: "first" | "last"): void => {
    const items = Array.from(menuRef.current?.querySelectorAll<HTMLElement>("[role=menuitem]") ?? []);
    if (items.length === 0) return;
    const current = items.findIndex((item) => item === document.activeElement);
    let next = absolute === "first" ? 0 : absolute === "last" ? items.length - 1 : current + offset;
    next = (next + items.length) % items.length;
    items[next]?.focus();
  };

  return (
    <GlassGroup id="menu" backdrop={{ kind: "texture", id: FIELD_TEXTURE_ID }}>
      <GlassMorph
        open={open}
        profile={APPLE_LIKE_SMOOTHING}
        radius={22}
        openRadius={22}
        thickness={8}
        openThickness={16}
        placement={props.placement}
        gap={10}
        className="platter"
        aria-label={props.label}
      >
        {({ open: isOpen }) =>
          isOpen ? (
            <ul
              ref={menuRef}
              id={menuId}
              role="menu"
              aria-label={props.label}
              className="menu"
              onKeyDown={(event) => {
                switch (event.key) {
                  case "Escape":
                    event.preventDefault();
                    setOpen(false);
                    break;
                  case "ArrowDown":
                    event.preventDefault();
                    focusItem(1);
                    break;
                  case "ArrowUp":
                    event.preventDefault();
                    focusItem(-1);
                    break;
                  case "Home":
                    event.preventDefault();
                    focusItem(0, "first");
                    break;
                  case "End":
                    event.preventDefault();
                    focusItem(0, "last");
                    break;
                  case "Tab":
                    setOpen(false);
                    break;
                  default:
                    break;
                }
              }}
            >
              {props.actions.map((action) => (
                <li key={action.id} role="none">
                  <button
                    type="button"
                    role="menuitem"
                    tabIndex={-1}
                    className="menu__item"
                    onClick={() => {
                      props.onAction(action.id);
                      setOpen(false);
                    }}
                  >
                    {action.label}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <button
              ref={triggerRef}
              type="button"
              className="control control--menu"
              aria-haspopup="menu"
              aria-expanded={false}
              aria-controls={menuId}
              onClick={() => setOpen(true)}
              onKeyDown={(event) => {
                if (event.key === "ArrowDown" || event.key === "ArrowUp") {
                  event.preventDefault();
                  setOpen(true);
                }
              }}
            >
              {props.label}
              <svg className="control__chevron" viewBox="0 0 12 12" aria-hidden="true" focusable="false">
                <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </button>
          )
        }
      </GlassMorph>
    </GlassGroup>
  );
}
