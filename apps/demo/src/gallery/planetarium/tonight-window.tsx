/**
 * The Tonight window: the one window on the page, a real task unit — where the person reads what
 * is up over their place, chooses an object and reads its card. Content on glass: the runtime's
 * ink on children, the object's card a darker fill, the selected row a lighter one, the list
 * scrolling inside the window's own clip while the host stays still.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import { useEffect, useRef, type ReactNode } from "react";

import {
  constellationOf,
  formatTime,
  twilightTitle,
  type Passage,
  type Place,
  type Sighting,
  type SkyObject,
  type SunState,
} from "./astro";
import { ENVIRONMENT_BACKDROP, THICKNESS, WINDOW_RADIUS, boxStyle, type GroupMaterial } from "./shared";
import { compassOf, DEG } from "./sky/projection";
import type { Box } from "./sky/renderer";

export interface SelectedDetail {
  readonly object: SkyObject;
  readonly altitude: number;
  readonly azimuth: number;
  readonly passage: Passage;
}

function kindLine(object: SkyObject): string {
  const constellation = constellationOf(object.ra, object.dec);
  switch (object.kind) {
    case "sun":
      return `The Sun · in ${constellation}`;
    case "moon":
      return `The Moon · in ${constellation}`;
    case "planet":
      return `Planet · in ${constellation}`;
    case "star":
      return `Star · ${constellation}`;
  }
}

function magnitudeText(mag: number): string {
  return mag < 0 ? `−${Math.abs(mag).toFixed(1)}` : mag.toFixed(1);
}

export function TonightWindow(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly present: boolean;
  readonly place: Place;
  readonly date: Date;
  readonly sun: SunState;
  readonly sightings: readonly Sighting[];
  readonly selected: SelectedDetail | undefined;
  readonly onSelect: (object: SkyObject | undefined) => void;
  readonly moonPhase: string;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { box, hint, material, present, place, date, sun, sightings, selected, onSelect, onHost } = props;
  const list = useRef<HTMLUListElement>(null);

  // A selection made on the sky scrolls its row into view; one made in the list is already there.
  // Not the page's own first choice on arrival: a short window would scroll its header away.
  const firstSelection = useRef(true);
  useEffect(() => {
    const id = selected?.object.id;
    if (id === undefined || list.current === null) return;
    if (firstSelection.current) {
      firstSelection.current = false;
      return;
    }
    const row = list.current.querySelector<HTMLElement>(`[data-object="${id}"]`);
    row?.scrollIntoView({ block: "nearest" });
  }, [selected?.object.id]);

  const next = sun.next;
  const passage = selected?.passage;
  let passageLabel = "";
  let passageValue = "";
  if (passage !== undefined) {
    if (passage.circumpolar === "always-up") {
      passageLabel = "Sets";
      passageValue = "never";
    } else if (passage.circumpolar === "never-up") {
      passageLabel = "Rises";
      passageValue = "never";
    } else if (selected !== undefined && selected.altitude > 0) {
      passageLabel = "Sets";
      passageValue = passage.set === undefined ? "—" : formatTime(passage.set, place.timeZone);
    } else {
      passageLabel = "Rises";
      passageValue = passage.rise === undefined ? "—" : formatTime(passage.rise, place.timeZone);
    }
  }

  return (
    <GlassGroup id="tonight" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={THICKNESS} foreground="vibrant" present={present} onHost={onHost}>
        <section aria-label="Tonight" data-glass-role="window" className="glass window tonight" style={boxStyle(box)}>
          <div className="window-scroll tonight-scroll">
            <header className="tonight-head">
              <p className="eyebrow">Tonight over</p>
              <h2 className="window-title">{place.name}</h2>
              <p className="status">
                <strong>{twilightTitle(sun.phase)}</strong>
                {next === undefined ? null : (
                  <>
                    {" · "}
                    {next.label} {formatTime(next.at, place.timeZone)}
                  </>
                )}
              </p>
            </header>

            {selected === undefined ? (
              <p className="card card-empty">Pick a star or a planet, on the sky or below.</p>
            ) : (
              <article className="card" aria-label={selected.object.name}>
                <h3 className="card-name">{selected.object.name}</h3>
                <p className="card-kind">{kindLine(selected.object)}</p>
                <dl className="facts">
                  <div>
                    <dt>Altitude</dt>
                    <dd>{selected.altitude < 0 ? "below horizon" : `${Math.round(selected.altitude)}°`}</dd>
                  </div>
                  <div>
                    <dt>Direction</dt>
                    <dd>{compassOf(selected.azimuth * DEG)}</dd>
                  </div>
                  <div>
                    <dt>{passageLabel || "Sets"}</dt>
                    <dd>{passageValue || "—"}</dd>
                  </div>
                  <div>
                    <dt>Magnitude</dt>
                    <dd>{magnitudeText(selected.object.mag)}</dd>
                  </div>
                </dl>
              </article>
            )}

            <h3 className="section-title">
              Up now <span className="section-count">{sightings.length}</span>
            </h3>
            <ul ref={list} className="up-list" role="list">
              {sightings.map((sighting) => {
                const active = sighting.object.id === selected?.object.id;
                return (
                  <li key={sighting.object.id}>
                    <button
                      type="button"
                      className="row"
                      data-object={sighting.object.id}
                      aria-pressed={active}
                      onClick={() => onSelect(active ? undefined : sighting.object)}
                    >
                      <span className="row-main">
                        <span className="row-name">{sighting.object.name}</span>
                        <span className="row-kind">
                          {sighting.object.kind === "moon"
                            ? props.moonPhase
                            : sighting.object.kind === "planet"
                              ? "Planet"
                              : constellationOf(sighting.object.ra, sighting.object.dec)}
                        </span>
                      </span>
                      <span className="row-where">
                        <span className="row-alt">{Math.round(sighting.altitude)}°</span>
                        <span className="row-dir">{compassOf(sighting.azimuth * DEG)}</span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
            <p className="tonight-foot">{sightings.length === 0 ? "Nothing bright is up yet." : `As of ${formatTime(date, place.timeZone)}`}</p>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}
