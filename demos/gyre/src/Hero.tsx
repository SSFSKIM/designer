/**
 * The reading column's default content: the statement, the lede, and the
 * instrument's status. Ordinary DOM over the field, in ink, which the field's
 * lightness floor keeps above 7.8:1 everywhere (DESIGN.md §1).
 */

import type { ReactNode } from "react";

import { formatDate, formatTime, METHOD } from "./data";
import type { FieldLayer } from "./field/palettes";
import { OBSERVATION_TIME, REGION } from "./field/palettes";

export interface HeroProps {
  readonly layer: FieldLayer;
  readonly offsetHours: number;
  readonly playing: boolean;
}

/** The one colormap bar. */
export function Legend(props: { readonly layer: FieldLayer }): ReactNode {
  const { layer } = props;
  const gradient = `linear-gradient(90deg, ${layer.stops.map((stop) => stop.hex).join(", ")})`;
  return (
    <div className="legend" role="img" aria-label={`${layer.quantity} scale from ${layer.min} to ${layer.max} ${layer.unit}`}>
      <span className="legend__bar" style={{ background: gradient }} />
      <span className="legend__ends" aria-hidden="true">
        <span>
          {layer.min.toFixed(layer.decimals)} {layer.unit}
        </span>
        <span>
          {layer.max.toFixed(layer.decimals)} {layer.unit}
        </span>
      </span>
    </div>
  );
}

export function Hero(props: HeroProps): ReactNode {
  const shown = new Date(OBSERVATION_TIME.getTime() + props.offsetHours * 3_600_000);
  const offset =
    props.offsetHours === 0
      ? "observation"
      : `${props.offsetHours > 0 ? "+" : "−"}${Math.abs(props.offsetHours)} h ${props.offsetHours > 0 ? "forecast" : "hindcast"}`;

  return (
    <div className="hero">
      <h1 className="hero__title">Surface currents, resolved to the hour.</h1>
      <p className="hero__lede">
        Gyre assimilates {METHOD.drifters} drifting buoys, {METHOD.altimetry} altimetry tracks and
        every coastal radar into one live field, six hours ahead.
      </p>
      <dl className="hero__status">
        <div>
          <dt>Region</dt>
          <dd>
            {REGION.name}, {REGION.south}°N to {REGION.north}°N, {REGION.west}°E to {REGION.east}°E
          </dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>
            {formatDate(shown)} {formatTime(shown)}, {offset}
            {props.playing ? "" : ", paused"}
          </dd>
        </div>
        <div>
          <dt>Layer</dt>
          <dd>{props.layer.quantity}</dd>
        </div>
      </dl>
      <Legend layer={props.layer} />
      <p className="hero__hint">Drag the probe to read the field at a point.</p>
    </div>
  );
}
