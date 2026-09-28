/**
 * The Moon module: one glance unit on its own glass — the phase, how much is lit, when it rises
 * and sets, and the next quarter. Figures and a glyph, no prose, bright foreground.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import type { ReactNode } from "react";

import { formatShortDate, formatTime, type MoonState, type Place } from "./astro";
import { MoonGlyph } from "./moon-glyph";
import { ENVIRONMENT_BACKDROP, THICKNESS, WINDOW_RADIUS, boxStyle, type GroupMaterial } from "./shared";
import type { Box } from "./sky/renderer";

export function MoonModule(props: {
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly material: GroupMaterial;
  readonly present: boolean;
  readonly place: Place;
  readonly moon: MoonState;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { box, hint, material, present, place, moon, onHost } = props;
  const zone = place.timeZone;
  return (
    <GlassGroup id="moon" backdrop={ENVIRONMENT_BACKDROP} hint={hint} {...material}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={THICKNESS} foreground="vibrant" present={present} onHost={onHost}>
        <section aria-label="The Moon" data-glass-role="module" className="glass module moon" style={boxStyle(box)}>
          <div className="module-inner">
            <MoonGlyph phase={moon.phase} size={64} className="moon-glyph" />
            <div className="moon-text">
              <p className="moon-phase">{moon.phaseName}</p>
              <p className="moon-lit">
                <span className="moon-percent">{Math.round(moon.illuminated * 100)}%</span> lit
                {moon.phaseName === "Full Moon" || moon.phaseName === "New Moon" ? "" : moon.waxing ? " · waxing" : " · waning"}
              </p>
              <dl className="moon-facts">
                <div>
                  <dt>Rises</dt>
                  <dd>{moon.rise === undefined ? "—" : formatTime(moon.rise, zone)}</dd>
                </div>
                <div>
                  <dt>Sets</dt>
                  <dd>{moon.set === undefined ? "—" : formatTime(moon.set, zone)}</dd>
                </div>
                <div>
                  <dt>{moon.nextQuarter.name}</dt>
                  <dd>{formatShortDate(moon.nextQuarter.at, zone)}</dd>
                </div>
              </dl>
            </div>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}
