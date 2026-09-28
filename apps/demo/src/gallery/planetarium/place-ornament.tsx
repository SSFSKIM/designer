/**
 * The Place ornament, hung above the window: where the sky is seen from. Pressed, it becomes the
 * Place platter — seven places on two hemispheres, the person's own location, the page's Reduce
 * Transparency setting (which the root receives as a boolean, so an engine that cannot answer
 * the media query still gets the person's answer), and the credit the sky maps carry.
 */

import { useGlassRootHandle, type BackdropHint } from "@vitreajs/vitrea-react";
import type { KeyboardEvent, ReactNode } from "react";

import { PLACES, type Place } from "./astro";
import { CheckGlyph, ChevronGlyph, LocateGlyph } from "./icons";
import { MorphOrnament } from "./morph-ornament";
import { usePlatterPress } from "./platter-press";
import type { GroupMaterial } from "./shared";
import type { Box } from "./sky/renderer";

export const PLACE_HOST_CLASS = "place-morph";

function coordinates(place: Place): string {
  const lat = `${Math.abs(place.latitude).toFixed(1)}° ${place.latitude >= 0 ? "N" : "S"}`;
  const lon = `${Math.abs(place.longitude).toFixed(1)}° ${place.longitude >= 0 ? "E" : "W"}`;
  return `${lat} · ${lon}`;
}

export function PlaceOrnament(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly morphKey: string;
  readonly place: Place;
  readonly locating: boolean;
  readonly reducedTransparency: boolean;
  readonly reducedMotion: boolean;
  readonly open: boolean;
  readonly onOpenChange: (open: boolean) => void;
  readonly onHostBox: (box: Box | undefined) => void;
  readonly onPlace: (place: Place) => void;
  readonly onLocate: () => void;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { place, open } = props;
  const { root } = useGlassRootHandle();
  usePlatterPress(root, `.${PLACE_HOST_CLASS}`, open, props.reducedMotion);
  const listed = PLACES.some((candidate) => candidate.id === place.id);

  /*
   * The radio group is one tab stop, the checked option (roving tabindex), and the arrows move
   * through it with the selection following, Home and End to its ends. "Use my location" is the
   * one option an arrow only FOCUSES: choosing it asks the browser for a position, which is the
   * person's to start with Enter, Space or a click, not something to trigger by passing over it.
   */
  const onOptionKey = (event: KeyboardEvent<HTMLDivElement>): void => {
    const options = [...event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="radio"]')].filter(
      (option) => !option.disabled,
    );
    const at = options.findIndex((option) => option === document.activeElement);
    if (at === -1) return;
    let to: number;
    switch (event.key) {
      case "ArrowDown":
      case "ArrowRight":
        to = (at + 1) % options.length;
        break;
      case "ArrowUp":
      case "ArrowLeft":
        to = (at - 1 + options.length) % options.length;
        break;
      case "Home":
        to = 0;
        break;
      case "End":
        to = options.length - 1;
        break;
      default:
        return;
    }
    event.preventDefault();
    const option = options[to];
    if (option === undefined) return;
    option.focus();
    const chosen = PLACES.find((candidate) => candidate.id === option.dataset.place);
    if (chosen !== undefined && chosen.id !== place.id) props.onPlace(chosen);
  };

  return (
    <MorphOrnament
      groupId="place"
      hostClass={PLACE_HOST_CLASS}
      label="Place"
      box={props.box}
      hint={props.hint}
      material={props.material}
      morphKey={props.morphKey}
      placement="below-start"
      open={open}
      onOpenChange={props.onOpenChange}
      onHostBox={props.onHostBox}
      closed={(trigger, box) => (
        <button
          ref={trigger}
          type="button"
          className="face-trigger place-trigger"
          style={{ width: box.width, height: box.height }}
          aria-haspopup="dialog"
          aria-expanded={false}
          onClick={() => props.onOpenChange(true)}
        >
          <LocateGlyph size={16} className="place-glyph" />
          <span className="place-name">{place.name}</span>
          <span className="place-coords">{coordinates(place)}</span>
          <ChevronGlyph size={14} className="face-chevron" />
        </button>
      )}
      platter={(close) => (
        <div className="place-platter">
          <p className="platter-title">Place</p>
          <div className="place-options" role="radiogroup" aria-label="Place" onKeyDown={onOptionKey}>
            {PLACES.map((candidate) => {
              const checked = candidate.id === place.id;
              return (
                <button
                  key={candidate.id}
                  type="button"
                  role="radio"
                  aria-checked={checked}
                  tabIndex={checked ? 0 : -1}
                  data-place={candidate.id}
                  className="place-option"
                  onClick={() => props.onPlace(candidate)}
                >
                  <span className="place-option-name">{candidate.name}</span>
                  <span className="place-option-country">{candidate.country}</span>
                  {checked ? <CheckGlyph size={14} className="place-check" /> : null}
                </button>
              );
            })}
            <button
              type="button"
              role="radio"
              aria-checked={!listed}
              tabIndex={listed ? -1 : 0}
              className="place-option"
              onClick={props.onLocate}
              disabled={props.locating}
            >
              <span className="place-option-name">
                <LocateGlyph size={14} /> {props.locating ? "Finding you…" : "Use my location"}
              </span>
              <span className="place-option-country">{!listed ? coordinates(place) : "asks the browser once"}</span>
              {!listed ? <CheckGlyph size={14} className="place-check" /> : null}
            </button>
          </div>
          <p className="section-title platter-section">Display</p>
          <button
            type="button"
            role="switch"
            aria-checked={props.reducedTransparency}
            className="setting"
            onClick={() => props.onReducedTransparency(!props.reducedTransparency)}
          >
            <span className="setting-label">Reduce transparency</span>
            <span className="switch" aria-hidden="true">
              <span className="switch-knob" />
            </span>
          </button>
          <p className="credit">
            Sky maps: NASA/Goddard SVS, Gaia DR2 ESA/Gaia/DPAC · Stars: Yale Bright Star Catalogue ·
            Positions: astronomy-engine
          </p>
          <div className="platter-actions">
            <button type="button" className="action action-quiet" onClick={() => close(true)}>
              Done
            </button>
          </div>
        </div>
      )}
    />
  );
}
