/**
 * An ornament that becomes a platter: one `GlassMorph` host for the pair's whole life, in the
 * overlay plane and its own group, hung outside the window's edge by the derived gap and opening
 * into open sky, never over the window (on the texture path a platter over the window would show
 * the environment where the eye expects the window's glass).
 *
 * What the runtime leaves to the page is here once for both ornaments: the audit contract's role
 * on the host (`ornament` closed, `platter` open — the morph passes no data attribute); the
 * platter's lifecycle (Escape, an outside press, a Tab out close it and focus returns to the
 * trigger); the host's box reported to the page every frame it moves, for the dimming layer and
 * the group's declaration; and the recorded workaround for a closed morph realigned onto a moved
 * footprint without invalidating its geometry (a `scroll` event at the host marks it dirty).
 *
 * The morph measures its closed face ONCE and keeps that size while closed, so the face is given
 * the anchor's box (`closed`'s second argument) rather than sized by its content: a face sized by
 * its text measured one place's name and then clipped or floated inside the next one's.
 */

import { APPLE_LIKE_SMOOTHING, GlassGroup, GlassMorph, useGlassRootHandle, type BackdropHint } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type KeyboardEvent, type ReactNode, type RefObject } from "react";

import { DESIGN } from "./layout";
import { ENVIRONMENT_BACKDROP, PLATTER_RADIUS, THICKNESS, type GroupMaterial } from "./shared";
import type { Box } from "./sky/renderer";

export function MorphOrnament(props: {
  readonly groupId: string;
  readonly hostClass: string;
  readonly label: string;
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly morphKey: string;
  readonly placement: "below-start" | "above-start";
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onHostBox: (box: Box | undefined) => void;
  readonly onMorphEnd?: (open: boolean) => void;
  /** The closed face, sized to `box` (border-box) so its measured size is the anchor's. */
  readonly closed: (
    trigger: RefObject<HTMLButtonElement | null>,
    box: { readonly width: number; readonly height: number },
  ) => ReactNode;
  readonly platter: (close: (focusTrigger: boolean) => void, focusFirst: RefObject<HTMLElement | null>) => ReactNode;
}): ReactNode {
  const { groupId, hostClass, box, hint, material, open, onOpenChange } = props;
  const { root } = useGlassRootHandle();
  const trigger = useRef<HTMLButtonElement>(null);
  const first = useRef<HTMLElement>(null);
  const returnFocus = useRef(false);
  const latest = useRef(props);
  latest.current = props;

  // The role, written after each frame; and the host's box, reported whenever it moves.
  const role = open ? "platter" : "ornament";
  useEffect(() => {
    if (root === null) return;
    let last = "";
    const read = (): void => {
      const host = document.querySelector<HTMLElement>(`.${hostClass}`);
      if (host === null) return;
      if (host.getAttribute("data-glass-role") !== role) host.setAttribute("data-glass-role", role);
      const rect = host.getBoundingClientRect();
      const key = [rect.x, rect.y, rect.width, rect.height].map((v) => Math.round(v)).join(",");
      if (key === last) return;
      last = key;
      if (rect.width < 4 || rect.height < 4) {
        latest.current.onHostBox(undefined);
        return;
      }
      latest.current.onHostBox({ x: rect.x, y: rect.y, width: rect.width, height: rect.height });
      // The recorded seam: a closed morph writes `left`/`top` for a moved footprint and the glass
      // keeps its cached box; a scroll event at the host is the geometry sync's own dirty signal.
      host.dispatchEvent(new Event("scroll"));
    };
    read();
    return root.subscribe(read);
  }, [root, role, hostClass, box]);

  // Outside presses close the platter.
  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent): void => {
      const target = event.target as Node | null;
      const host = document.querySelector(`.${hostClass}`);
      if (target !== null && host !== null && host.contains(target)) return;
      onOpenChange(false);
    };
    document.addEventListener("pointerdown", onPointer, true);
    return () => document.removeEventListener("pointerdown", onPointer, true);
  }, [open, onOpenChange, hostClass]);

  // Focus goes into the platter when it opens — to its first tab stop, which in a radio group is
  // the checked option — and back to the trigger when it closes by key.
  useEffect(() => {
    if (open) {
      const stop = [...document.querySelectorAll<HTMLElement>(`.${hostClass} :is(button, input, [tabindex])`)].find(
        (element) => element.tabIndex >= 0 && !element.matches(":disabled"),
      );
      (first.current ?? stop)?.focus({ preventScroll: true });
    } else if (returnFocus.current) {
      returnFocus.current = false;
      trigger.current?.focus({ preventScroll: true });
    }
  }, [open, hostClass]);

  /*
   * A remount (a new `morphKey`, the app's answer to a Reduce Motion change) drops whatever focus
   * was inside the old host. Focus inside the morph is followed through React's tree, which the
   * portal does not break; once the new morph has measured and placed its closed face, focus that
   * was dropped returns to its trigger. Not before: a trigger in an unplaced host cannot be pressed.
   */
  const focusWithin = useRef(false);
  const mountedKey = useRef(props.morphKey);
  useEffect(() => {
    if (root === null || mountedKey.current === props.morphKey) return;
    mountedKey.current = props.morphKey;
    if (!focusWithin.current) return;
    let done = false;
    return root.subscribe(() => {
      const host = document.querySelector<HTMLElement>(`.${hostClass}`);
      if (done || host === null || host.getBoundingClientRect().height < 4) return;
      done = true;
      const active = document.activeElement;
      if (active === null || active === document.body) trigger.current?.focus({ preventScroll: true });
    });
  }, [root, props.morphKey, hostClass]);

  const close = (focusTrigger: boolean): void => {
    returnFocus.current = focusTrigger;
    onOpenChange(false);
  };

  /*
   * Escape closes; so does a Tab that would leave the platter — forward from its last tab stop or
   * backward from its first — with focus back on the trigger, where the person opened it. A press
   * or a focus change elsewhere is the blur handler's.
   */
  const onKey = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === "Escape") {
      event.preventDefault();
      close(true);
      return;
    }
    if (event.key !== "Tab") return;
    const stops = [...event.currentTarget.querySelectorAll<HTMLElement>("button, input, [tabindex]")].filter(
      (element) => element.tabIndex >= 0 && !element.matches(":disabled"),
    );
    const edge = event.shiftKey ? stops[0] : stops[stops.length - 1];
    if (edge !== undefined && document.activeElement === edge) {
      event.preventDefault();
      close(true);
    }
  };

  return (
    <GlassGroup id={groupId} backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <div
        className="ornament-anchor"
        style={{ position: "fixed", left: box.x, top: box.y, width: box.width, height: box.height }}
        onFocus={() => {
          focusWithin.current = true;
        }}
        onBlur={(event) => {
          if (event.relatedTarget !== null) focusWithin.current = false;
        }}
      >
        <GlassMorph
          key={props.morphKey}
          open={open}
          groupId={groupId}
          plane="overlay"
          openPlane="overlay"
          radius={box.height / 2}
          openRadius={PLATTER_RADIUS}
          thickness={THICKNESS}
          openThickness={THICKNESS}
          profile={APPLE_LIKE_SMOOTHING}
          openProfile={APPLE_LIKE_SMOOTHING}
          placement={props.placement}
          gap={DESIGN.platterGap}
          className={`glass ${hostClass}`}
          aria-label={props.label}
          onMorphEnd={props.onMorphEnd}
        >
          {({ open: isOpen }) =>
            isOpen ? (
              <div
                className="platter"
                role="dialog"
                aria-label={props.label}
                onKeyDown={onKey}
                onBlur={(event) => {
                  const next = event.relatedTarget as Node | null;
                  if (next !== null && !event.currentTarget.contains(next)) close(false);
                }}
              >
                {props.platter(close, first)}
              </div>
            ) : (
              props.closed(trigger, { width: box.width, height: box.height })
            )
          }
        </GlassMorph>
      </div>
    </GlassGroup>
  );
}
