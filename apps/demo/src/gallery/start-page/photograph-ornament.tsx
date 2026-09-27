/**
 * The Photograph ornament and the platter it becomes.
 *
 * Closed, it is an ornament hung below the Now module: it names the phase the environment is in
 * and the photograph's maker (the attribution the CC BY photographs ask for, on screen). Pressed,
 * it becomes the Photograph platter by one continuous matched-geometry morph — one glass host for
 * the pair's whole life, in the overlay plane and its own group — opening downward into open
 * environment, never over a window: on the texture path a platter over a window would show the
 * photograph where the eye expects the window's glass.
 *
 * The platter holds the environment's choices and the page's own Reduce Transparency setting,
 * which the root receives as a boolean, so an engine that cannot answer the media query still
 * gets the person's answer. Its lifecycle is the app's, as the runtime leaves it: Escape, a
 * press outside or a Tab out closes it and focus returns to the ornament.
 */

import {
  APPLE_LIKE_SMOOTHING,
  GlassGroup,
  GlassMorph,
  useGlassRootHandle,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import { useEffect, useRef, type KeyboardEvent, type ReactNode } from "react";

import { PHOTOGRAPHS, type PhaseId, type Photograph } from "./data";
import type { Box } from "./environment";
import { ChevronGlyph } from "./icons";
import { ENVIRONMENT_BACKDROP, PLATTER_RADIUS, THICKNESS } from "./shared";

/** The class the morph passes to its one host; the audit contract's role is written on it. */
export const PHOTOGRAPH_HOST_CLASS = "photograph-morph";

export function PhotographOrnament(props: {
  readonly box: Box;
  /** The Now column is narrower than the full face: the ornament shows the phase alone. */
  readonly compact: boolean;
  /** The height the platter may take below its ornament before the viewport's edge. */
  readonly room: number;
  readonly hint: BackdropHint | undefined;
  readonly photo: Photograph;
  readonly follow: boolean;
  readonly reducedTransparency: boolean;
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onChoose: (id: PhaseId) => void;
  readonly onFollow: (follow: boolean) => void;
  readonly onReducedTransparency: (value: boolean) => void;
  readonly onMorphEnd: () => void;
}): ReactNode {
  const { box, hint, photo, follow, reducedTransparency, open, onOpenChange } = props;
  const { root } = useGlassRootHandle();
  const trigger = useRef<HTMLButtonElement>(null);
  const platter = useRef<HTMLDivElement>(null);
  const returnFocus = useRef(false);

  /*
   * The morph renders its host itself and takes no data attributes, so the role the audit
   * contract asks every host to state is written onto it after each frame: `ornament` while it is
   * the closed capsule, `platter` while it is open.
   */
  const role = open ? "platter" : "ornament";
  useEffect(() => {
    if (root === null) return;
    const write = (): void => {
      const host = document.querySelector(`.${PHOTOGRAPH_HOST_CLASS}`);
      if (host !== null && host.getAttribute("data-glass-role") !== role) host.setAttribute("data-glass-role", role);
    };
    write();
    return root.subscribe(write);
  }, [root, role]);

  // Outside presses close the platter; the press that opened it is already over.
  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent): void => {
      const target = event.target as Node | null;
      const host = document.querySelector(`.${PHOTOGRAPH_HOST_CLASS}`);
      if (target !== null && host !== null && host.contains(target)) return;
      onOpenChange(false);
    };
    document.addEventListener("pointerdown", onPointer, true);
    return () => document.removeEventListener("pointerdown", onPointer, true);
  }, [open, onOpenChange]);

  // Focus goes into the platter when it opens, and back to the ornament when it closes by key.
  useEffect(() => {
    if (open) {
      platter.current?.querySelector<HTMLElement>('[role="radio"][aria-checked="true"]')?.focus({ preventScroll: true });
    } else if (returnFocus.current) {
      returnFocus.current = false;
      trigger.current?.focus({ preventScroll: true });
    }
  }, [open]);

  const close = (focusTrigger: boolean): void => {
    returnFocus.current = focusTrigger;
    onOpenChange(false);
  };

  const onPlatterKey = (event: KeyboardEvent<HTMLDivElement>): void => {
    if (event.key === "Escape") {
      event.preventDefault();
      close(true);
      return;
    }
    const target = event.target as HTMLElement;
    if (target.getAttribute("role") !== "radio") return;
    const step = event.key === "ArrowRight" || event.key === "ArrowDown" ? 1 : event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 0;
    if (step === 0) return;
    event.preventDefault();
    const index = PHOTOGRAPHS.findIndex((candidate) => candidate.id === photo.id);
    const nextPhoto = PHOTOGRAPHS[(index + step + PHOTOGRAPHS.length) % PHOTOGRAPHS.length];
    if (nextPhoto === undefined) return;
    props.onChoose(nextPhoto.id);
    requestAnimationFrame(() => {
      platter.current?.querySelector<HTMLElement>(`[data-phase="${nextPhoto.id}"]`)?.focus({ preventScroll: true });
    });
  };

  return (
    <GlassGroup id="photograph" backdrop={ENVIRONMENT_BACKDROP} hint={hint}>
      <div className="photograph-anchor" style={{ position: "fixed", left: box.x, top: box.y }}>
        {/*
          A closed morph never follows a new closed size, so the two faces are two morphs: the
          key remounts it when the layout crosses between them (the app closes it first).
        */}
        <GlassMorph
          key={props.compact ? "compact" : "full"}
          open={open}
          groupId="photograph"
          plane="overlay"
          openPlane="overlay"
          radius={box.height / 2}
          openRadius={PLATTER_RADIUS}
          thickness={THICKNESS}
          openThickness={THICKNESS}
          profile={APPLE_LIKE_SMOOTHING}
          openProfile={APPLE_LIKE_SMOOTHING}
          placement="below-start"
          gap={8}
          className={`glass ${PHOTOGRAPH_HOST_CLASS}`}
          aria-label="Photograph"
          onMorphEnd={props.onMorphEnd}
        >
          {({ open: isOpen }) =>
            isOpen ? (
              <div
                ref={platter}
                className="platter"
                style={{ maxHeight: props.room }}
                role="dialog"
                aria-label="Photograph"
                onKeyDown={onPlatterKey}
                onBlur={(event) => {
                  const next = event.relatedTarget as Node | null;
                  if (next !== null && !event.currentTarget.contains(next)) close(false);
                }}
              >
                <p className="platter-title">Photograph</p>
                <div className="photo-options" role="radiogroup" aria-label="Photograph">
                  {PHOTOGRAPHS.map((candidate) => {
                    const checked = candidate.id === photo.id;
                    return (
                      <button
                        key={candidate.id}
                        type="button"
                        role="radio"
                        aria-checked={checked}
                        tabIndex={checked ? 0 : -1}
                        data-phase={candidate.id}
                        className="photo-option"
                        onClick={() => props.onChoose(candidate.id)}
                      >
                        <img className="photo-thumb" src={candidate.url} alt="" draggable={false} />
                        <span className="photo-label">{candidate.label}</span>
                      </button>
                    );
                  })}
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={follow}
                  className="setting"
                  onClick={() => props.onFollow(!follow)}
                >
                  <span className="setting-label">Follow the time of day</span>
                  <span className="switch" aria-hidden="true">
                    <span className="switch-knob" />
                  </span>
                </button>
                <button
                  type="button"
                  role="switch"
                  aria-checked={reducedTransparency}
                  className="setting"
                  onClick={() => props.onReducedTransparency(!reducedTransparency)}
                >
                  <span className="setting-label">Reduce transparency</span>
                  <span className="switch" aria-hidden="true">
                    <span className="switch-knob" />
                  </span>
                </button>
                <p className="credit">
                  <a href={photo.source}>{photo.title}</a> · {photo.maker} ·{" "}
                  <a href={photo.licenceUrl}>{photo.licence}</a>
                </p>
              </div>
            ) : (
              <button
                ref={trigger}
                type="button"
                className="photograph-trigger"
                data-compact={props.compact ? "" : undefined}
                aria-haspopup="dialog"
                aria-expanded={false}
                onClick={() => onOpenChange(true)}
              >
                <span className="photograph-phase">{photo.label}</span>
                <span className="photograph-maker">
                  <span className="visually-hidden">photograph by </span>
                  {photo.maker}
                </span>
                <ChevronGlyph size={16} className="photograph-chevron" />
              </button>
            )
          }
        </GlassMorph>
      </div>
    </GlassGroup>
  );
}
