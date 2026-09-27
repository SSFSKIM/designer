/**
 * The Places window: the twelve places the person goes, a collection read in place — which is
 * exactly what a window is for in the spatial register. The host is the labelled section; the
 * list stays a semantic `<ul>` child, never the host, and every place is a plain link on a
 * lighter child fill (interactive elements lift; the one level of fill never stacks on another).
 *
 * The search ornament above this window narrows nothing away: a match is lifted a step further
 * and becomes where Return goes, so the grid never loses its shape while the person types.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import type { ReactNode } from "react";

import { PLACES, type Place } from "./data";
import type { Box } from "./environment";
import { ENVIRONMENT_BACKDROP, THICKNESS, WINDOW_RADIUS, boxStyle, type GroupMaterial } from "./shared";

export function PlacesWindow(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly match: Place | undefined;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { box, hint, material, match, onHost } = props;
  return (
    <GlassGroup id="places" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={THICKNESS} foreground="vibrant" onHost={onHost}>
        <section aria-labelledby="places-title" data-glass-role="window" className="glass window places" style={boxStyle(box)}>
          <div className="places-inner">
            <h2 id="places-title" className="window-title">
              Places
            </h2>
            <ul className="places-grid">
              {PLACES.map((place) => (
                <li key={place.name}>
                  <a
                    className="place"
                    href={place.href}
                    data-match={match === place ? "" : undefined}
                  >
                    <span className="place-mark" aria-hidden="true">
                      {place.mark}
                    </span>
                    <span className="place-name">{place.name}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}
