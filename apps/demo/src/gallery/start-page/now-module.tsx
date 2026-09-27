/**
 * The Now module: the across-the-room glance. The time, the date, what it is like outside and
 * the next five days — figures and a few words, never prose (a glance module's condition).
 *
 * The module is the host: a labelled `<section>` registered through `GlassSurface asChild`,
 * untinted, regular, at the family's one thickness and the windows' fixed radius. Every line of
 * type is a child carrying the runtime's primary or secondary label token.
 */

import { GlassGroup, GlassSurface, type BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import type { ReactNode } from "react";

import {
  CONDITION_LABEL,
  FORECAST,
  TODAY_HIGH,
  TODAY_LOW,
  WEATHER_PLACE,
  weatherAt,
} from "./data";
import type { Box } from "./environment";
import { WeatherGlyph } from "./icons";
import { ENVIRONMENT_BACKDROP, LOCALE, THICKNESS, WINDOW_RADIUS, boxStyle } from "./shared";

const timeFormat = new Intl.DateTimeFormat(LOCALE, { hour: "numeric", minute: "2-digit" });
const dateFormat = new Intl.DateTimeFormat(LOCALE, { weekday: "long", day: "numeric", month: "long" });
const dayFormat = new Intl.DateTimeFormat(LOCALE, { weekday: "short" });
const longDayFormat = new Intl.DateTimeFormat(LOCALE, { weekday: "long" });

export function NowModule(props: {
  readonly now: Date;
  readonly box: Box;
  readonly hint: BackdropHint | undefined;
  readonly onHost: (handle: GlassHostHandle | null) => void;
}): ReactNode {
  const { now, box, hint, onHost } = props;
  const parts = timeFormat.formatToParts(now);
  const clock = parts
    .filter((part) => part.type !== "dayPeriod")
    .map((part) => part.value)
    .join("")
    .trim();
  const period = parts.find((part) => part.type === "dayPeriod")?.value;
  const weather = weatherAt(now);
  const night = now.getHours() >= 20 || now.getHours() < 6;

  return (
    <GlassGroup id="now" backdrop={ENVIRONMENT_BACKDROP} hint={hint}>
      <GlassSurface asChild radius={WINDOW_RADIUS} thickness={THICKNESS} foreground="vibrant" onHost={onHost}>
        <section aria-label="Now" data-glass-role="module" className="glass module now" style={boxStyle(box)}>
          <div className="now-inner">
            <p className="now-clock">
              <time dateTime={now.toISOString()}>
                <span className="now-time">{clock}</span>
                {period === undefined ? null : <span className="now-period">{period}</span>}
              </time>
            </p>
            <p className="now-date">{dateFormat.format(now)}</p>

            <div className="now-weather">
              <WeatherGlyph condition={weather.condition} night={night} size={44} className="now-glyph" />
              <p className="now-temperature" aria-label={`${weather.temperature} degrees`}>
                {weather.temperature}°
              </p>
              <div className="now-conditions">
                <p className="now-condition">{CONDITION_LABEL[weather.condition]}</p>
                <p className="now-range">
                  H {TODAY_HIGH}° · L {TODAY_LOW}° · {WEATHER_PLACE}
                </p>
              </div>
            </div>

            <ol className="forecast" aria-label="Next five days">
              {FORECAST.map(([condition, high, low], index) => {
                const day = new Date(now);
                day.setDate(now.getDate() + index + 1);
                return (
                  <li key={index} className="forecast-day">
                    <span className="forecast-name" aria-label={longDayFormat.format(day)}>
                      {dayFormat.format(day)}
                    </span>
                    <WeatherGlyph condition={condition} size={24} className="forecast-glyph" />
                    <span className="visually-hidden">{CONDITION_LABEL[condition]},</span>
                    <span className="forecast-high" aria-label={`high ${high} degrees`}>
                      {high}°
                    </span>
                    <span className="forecast-low" aria-label={`low ${low} degrees`}>
                      {low}°
                    </span>
                  </li>
                );
              })}
            </ol>
          </div>
        </section>
      </GlassSurface>
    </GlassGroup>
  );
}
