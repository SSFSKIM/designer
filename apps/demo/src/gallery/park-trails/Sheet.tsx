/**
 * The sheet: everything on the page that is read rather than operated, printed on opaque paper
 * that scrolls up over the photograph (DESIGN.md, inventory). No glass anywhere in here. Its
 * hierarchy is carried by type, rules and whitespace, so the page reads the same with the
 * material removed, and the one colour it spends is the lupine accent on the planned route.
 */

import { useGlassCapabilities, type GlassGroupState } from "@vitreajs/vitrea-react";
import type { ReactNode, RefObject } from "react";

import {
  BULLETIN,
  CORRIDORS,
  FORECAST,
  forecastAt,
  formatFt,
  formatMi,
  permitSteps,
  PHOTO_CREDIT,
  STATUS_LABEL,
  TRAILS,
  type Trail,
} from "./data";
import { SkyGlyph } from "./glyphs";

export interface SheetProps {
  readonly trail: Trail;
  readonly onChooseRoute: (id: string) => void;
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
  readonly sheetRef: RefObject<HTMLElement | null>;
  readonly permitsRef: RefObject<HTMLElement | null>;
  readonly conditionsRef: RefObject<HTMLElement | null>;
  readonly forecastRef: RefObject<HTMLTableElement | null>;
  readonly trailsRef: RefObject<HTMLElement | null>;
}

const ELEVATION_BANDS = [
  { label: "Valley", ft: 500 },
  { label: "Trailheads", ft: 3500 },
  { label: "Passes", ft: 5500 },
  { label: "Summits", ft: 7500 },
] as const;

function permitSummary(trail: Trail): string {
  if (trail.overnight?.required === "always") return "Required";
  if (trail.overnight !== undefined) return "Only to camp";
  return "None";
}

export function Sheet(props: SheetProps): ReactNode {
  const { trail } = props;
  const steps = permitSteps(trail);
  const today = FORECAST[0];

  return (
    <article ref={props.sheetRef} className="pt-sheet" aria-labelledby="pt-title">
      <header className="pt-masthead">
        <div className="pt-masthead__lead">
          <p className="pt-eyebrow">North Cascades National Park Service Complex · Washington</p>
          <h1 id="pt-title" className="pt-title">
            Trails and conditions
          </h1>
          <p className="pt-lede">
            Twelve trails from the Skagit gorge to Cascade Pass and the far end of Ross Lake, with
            this morning's conditions and what each one asks of you before you go. Choose a route in
            the planner at the top of the window; the list, the bulletin and the permit steps below
            read for it.
          </p>
          <p className="pt-meta">
            Posted Saturday 27 September 2026, 7:40 am, by the Wilderness Information Center,
            Marblemount.
          </p>
          <div className="pt-toolrow">
            <nav className="pt-contents" aria-label="On this page">
              <a href="#pt-trails">Trails</a>
              <a href="#pt-conditions">Conditions</a>
              <a href="#pt-permits">Permit steps</a>
            </nav>
            <label className="pt-switch">
              <input
                type="checkbox"
                role="switch"
                checked={props.reduceTransparency}
                onChange={(event) => props.onReduceTransparency(event.currentTarget.checked)}
              />
              <span className="pt-switch__track" aria-hidden="true" />
              <span>Reduce transparency</span>
            </label>
          </div>
        </div>

        <aside className="pt-planned" aria-labelledby="pt-planned-name">
          <p className="pt-planned__label">Planned route</p>
          <h2 id="pt-planned-name" className="pt-planned__name">
            {trail.name}
          </h2>
          <p className="pt-planned__status">
            <StatusMark status={trail.status} />
            <span>{STATUS_LABEL[trail.status]}.</span> {trail.condition}
          </p>
          <dl className="pt-facts">
            <div>
              <dt>Distance</dt>
              <dd>
                {formatMi(trail.distanceMi)} <span className="pt-facts__unit">{trail.shape}</span>
              </dd>
            </div>
            <div>
              <dt>Climb</dt>
              <dd>{formatFt(trail.gainFt)}</dd>
            </div>
            <div>
              <dt>High point</dt>
              <dd>{formatFt(trail.highFt)}</dd>
            </div>
            <div>
              <dt>Time</dt>
              <dd>{trail.time}</dd>
            </div>
          </dl>
          <p className="pt-planned__trailhead">
            From {trail.trailhead}, {formatFt(trail.trailheadFt)}.
          </p>
        </aside>
      </header>

      <section
        id="pt-trails"
        ref={props.trailsRef}
        className="pt-section"
        aria-labelledby="pt-trails-title"
      >
        <div className="pt-section__head">
          <h2 id="pt-trails-title" className="pt-h2">
            Trails
          </h2>
          <p className="pt-section__note">
            Distances are round trip unless a loop. Climb is total elevation gain. Choose a trail's
            name to plan it.
          </p>
        </div>
        <table className="pt-trails">
          <thead>
            <tr>
              <th scope="col">Trail</th>
              <th scope="col" className="pt-num">
                Distance
              </th>
              <th scope="col" className="pt-num">
                Climb
              </th>
              <th scope="col" className="pt-num">
                High point
              </th>
              <th scope="col">Difficulty</th>
              <th scope="col">Conditions</th>
              <th scope="col">Permit</th>
            </tr>
          </thead>
          {CORRIDORS.map((corridor) => (
            <tbody key={corridor.id}>
              <tr className="pt-trails__corridor">
                <th scope="rowgroup" colSpan={7}>
                  {corridor.name}
                  <span className="pt-trails__access">{corridor.access}</span>
                </th>
              </tr>
              {TRAILS.filter((row) => row.corridor === corridor.id).map((row) => (
                <tr key={row.id} data-selected={row.id === trail.id || undefined}>
                  <th scope="row" className="pt-trails__name">
                    <button
                      type="button"
                      aria-pressed={row.id === trail.id}
                      onClick={() => props.onChooseRoute(row.id)}
                    >
                      {row.name}
                    </button>
                    <span className="pt-trails__trailhead">{row.trailhead}</span>
                  </th>
                  <td className="pt-num">
                    {formatMi(row.distanceMi)}
                    {row.shape === "loop" ? <span className="pt-trails__shape"> loop</span> : null}
                  </td>
                  <td className="pt-num">{formatFt(row.gainFt)}</td>
                  <td className="pt-num">{formatFt(row.highFt)}</td>
                  <td>
                    {row.difficulty}
                    <span className="pt-trails__time">{row.time}</span>
                  </td>
                  <td className="pt-trails__condition">
                    <span className="pt-trails__status">
                      <StatusMark status={row.status} />
                      {STATUS_LABEL[row.status]}
                    </span>
                    <span className="pt-trails__note">{row.condition}</span>
                  </td>
                  <td>
                    {permitSummary(row)}
                    {row.parking === "none" ? null : (
                      <span className="pt-trails__pass">{row.parking}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          ))}
        </table>
      </section>

      <section
        id="pt-conditions"
        ref={props.conditionsRef}
        tabIndex={-1}
        className="pt-section"
        aria-labelledby="pt-conditions-title"
      >
        <div className="pt-section__head">
          <h2 id="pt-conditions-title" className="pt-h2">
            Conditions
          </h2>
          <p className="pt-section__note">
            Entries that bear on {trail.name} are marked. Reported by rangers and visitors; conditions
            change fastest above 6,000 ft.
          </p>
        </div>
        <div className="pt-bulletin">
          {BULLETIN.map((group) => (
            <div key={group.heading} className="pt-bulletin__column">
              <h3 className="pt-h3">{group.heading}</h3>
              <ul className="pt-bulletin__list">
                {group.entries.map((entry) => {
                  const bears = entry.trails?.includes(trail.id) ?? false;
                  return (
                    <li key={entry.text} data-bears={bears || undefined}>
                      <p className="pt-bulletin__date">
                        {entry.date}
                        {bears ? <span className="pt-bulletin__flag">{trail.name}</span> : null}
                      </p>
                      <p>{entry.text}</p>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        {/*
          The weather capsule's destination, and the forecast the planner used to float on glass:
          a table is content, so it lives here, and it reads for the planned route first (its
          trailhead and high point, marked like every other mark of the route on this sheet),
          then for the park's elevation bands.
        */}
        <h3 id="pt-forecast-title" className="pt-h3 pt-forecast__title">
          Forecast by elevation
        </h3>
        <table
          id="pt-forecast"
          ref={props.forecastRef}
          tabIndex={-1}
          className="pt-forecast"
          aria-labelledby="pt-forecast-title"
        >
          <thead>
            <tr className="pt-forecast__groups">
              <td />
              <th scope="colgroup" colSpan={2} className="pt-forecast__route">
                {trail.name}
              </th>
              <th scope="colgroup" colSpan={ELEVATION_BANDS.length}>
                Across the park
              </th>
              <td colSpan={2} />
            </tr>
            <tr>
              <th scope="col">
                <span className="pt-visually-hidden">Day</span>
              </th>
              <th scope="col" data-route="">
                Trailhead <span className="pt-forecast__ft">{formatFt(trail.trailheadFt)}</span>
              </th>
              <th scope="col" data-route="">
                High point <span className="pt-forecast__ft">{formatFt(trail.highFt)}</span>
              </th>
              {ELEVATION_BANDS.map((band) => (
                <th key={band.label} scope="col">
                  {band.label} <span className="pt-forecast__ft">{formatFt(band.ft)}</span>
                </th>
              ))}
              <th scope="col">Freezing level</th>
              <th scope="col" className="pt-num">
                Rain
              </th>
            </tr>
          </thead>
          <tbody>
            {FORECAST.map((day) => (
              <tr key={day.date}>
                <th scope="row">
                  {day.day} <span className="pt-forecast__date">{day.date}</span>
                </th>
                <ForecastCell day={day} ft={trail.trailheadFt} route />
                <ForecastCell day={day} ft={trail.highFt} route />
                {ELEVATION_BANDS.map((band) => (
                  <ForecastCell key={band.label} day={day} ft={band.ft} />
                ))}
                <td>{formatFt(day.freezingLevelFt)}</td>
                <td className="pt-num">{day.precipitation}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section
        id="pt-permits"
        ref={props.permitsRef}
        tabIndex={-1}
        className="pt-section"
        aria-labelledby="pt-permits-title"
      >
        <div className="pt-section__head">
          <h2 id="pt-permits-title" className="pt-h2">
            Permit steps for {trail.name}
          </h2>
          <p className="pt-section__note">
            The park charges no entrance fee. Wilderness permits are free to hold; Recreation.gov
            charges a fee to reserve one.
          </p>
        </div>
        <ol className="pt-steps">
          {steps.map((step, index) => (
            <li key={step.title} data-applies={step.applies || undefined}>
              <span className="pt-steps__number" aria-hidden="true">
                {index + 1}
              </span>
              <div>
                <h3 className="pt-h3">
                  {step.title}
                  {step.applies ? null : <span className="pt-steps__skip"> · not needed</span>}
                </h3>
                <p>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
        <p className="pt-permits__where">
          Wilderness Information Center, 7280 Ranger Station Road, Marblemount. Open daily 7 am to
          6 pm through 11 October{today === undefined ? "" : `; sunset today ${today.sunset}`}.
        </p>
      </section>

      <footer className="pt-footer">
        <p>
          Photograph: {PHOTO_CREDIT.caption}, by{" "}
          <a href={PHOTO_CREDIT.profile}>{PHOTO_CREDIT.photographer}</a> on{" "}
          <a href={PHOTO_CREDIT.photo}>Unsplash</a>.
        </p>
        <p>
          A design study on the vitrea demo site. Trail figures are the published ones; the
          conditions, forecast and closures are composed for the page and dated 27 September 2026.
          For a real trip, ask the park.
        </p>
        <Colophon />
      </footer>
    </article>
  );
}

function ForecastCell(props: {
  readonly day: (typeof FORECAST)[number];
  readonly ft: number;
  readonly route?: boolean;
}): ReactNode {
  const point = forecastAt(props.day, props.ft);
  return (
    <td data-route={props.route === true ? "" : undefined}>
      <span className="pt-forecast__cell">
        <SkyGlyph sky={point.sky} />
        <span className="pt-num">
          {point.highF}° / {point.lowF}°
        </span>
      </span>
      <span className="pt-forecast__word">{point.word}</span>
    </td>
  );
}

function StatusMark(props: { readonly status: Trail["status"] }): ReactNode {
  return <span className="pt-status" data-status={props.status} aria-hidden="true" />;
}

const TIER: Record<GlassGroupState["activeRenderer"], string> = {
  webgpu: "the WebGPU tier",
  css: "the CSS tier",
};

/** What a group's sampling backend means on this page, as a verb phrase: [one, several]. */
const SAMPLING: Record<GlassGroupState["samplingBackend"], readonly [string, string]> = {
  "gpu-texture": ["reads the photograph's own pixels", "read the photograph's own pixels"],
  "css-backdrop": ["samples the page beneath it", "sample the page beneath them"],
  none: ["samples nothing", "sample nothing"],
};

/** "A", "A and B", "A, B and C". */
function list(names: readonly string[]): string {
  if (names.length < 2) return names.join("");
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1] ?? ""}`;
}

type Named = readonly [name: string, state: GlassGroupState];

/** The names that share each value of `key`, in the planner's order. */
function partition(
  states: readonly Named[],
  key: (state: GlassGroupState) => string,
): [string, string[]][] {
  const byValue = new Map<string, string[]>();
  for (const [name, state] of states) {
    const value = key(state);
    byValue.set(value, [...(byValue.get(value) ?? []), name]);
  }
  return [...byValue];
}

/**
 * What drew, read back from the runtime rather than asserted (vitrea.md §7): every group's own
 * state, by the name its capsule carries, because the three do not always agree (the route menu
 * samples the page while it is open; the other two always read the photograph).
 */
function Colophon(): ReactNode {
  const route = useGlassCapabilities("route");
  const weather = useGlassCapabilities("weather");
  const permits = useGlassCapabilities("permits");
  if (route === undefined || weather === undefined || permits === undefined) return null;
  const states: readonly Named[] = [
    ["Route", route],
    ["Weather", weather],
    ["Permits", permits],
  ];
  const tiers = partition(states, (state) => TIER[state.activeRenderer]);
  const tier =
    tiers.length === 1
      ? (tiers[0]?.[0] ?? "")
      : list(tiers.map(([value, names]) => `${value} (${names.join(", ")})`));
  const sampling = partition(states, (state) => state.samplingBackend).map(([backend, names]) => {
    const [one, several] = SAMPLING[backend as GlassGroupState["samplingBackend"]];
    return `${list(names)} ${names.length === 1 ? one : several}`;
  });
  const materials = partition(states, (state) => state.materialDocument?.name ?? "default");
  const material =
    materials.length === 1
      ? (materials[0]?.[0] ?? "")
      : list(materials.map(([value, names]) => `${value} (${names.join(", ")})`));
  return (
    <p className="pt-colophon">
      The planner is Liquid Glass on vitrea, drawn on {tier}: {sampling.join("; ")}, and each
      takes its tone from the backdrop the page measures under it. Material {material}.
    </p>
  );
}
