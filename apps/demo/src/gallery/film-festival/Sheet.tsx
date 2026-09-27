/**
 * The content layer: a printed programme. Opaque paper, hairlines, whitespace and square corners;
 * no glass, no shadow. It scrolls over the fixed still, and its scrolling column carries the
 * scroll edge (see `main.tsx`), so it dissolves into the film before it reaches the bar.
 */

import type { ReactNode, Ref } from "react";

import {
  FESTIVAL,
  FILMS,
  PASSES,
  SCREENINGS,
  STRANDS,
  VENUES,
  clock,
  dayOf,
  filmOf,
  minutesOf,
  screeningOf,
  strandOf,
  venueOf,
  type DayId,
  type Film,
  type PassId,
} from "./data";
import haarUrl from "./images/haar-shore.jpg";

/** The schedule's vertical scale: 1.4 px per minute keeps a 66-minute film at four lines. */
const PX_PER_MINUTE = 1.4;

const NUMBER_WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight"];

export interface SheetProps {
  readonly scrollRef: Ref<HTMLDivElement>;
  readonly day: DayId;
  readonly onDay: (day: DayId) => void;
  readonly onPass: (pass: PassId) => void;
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (on: boolean) => void;
}

export function Sheet(props: SheetProps): ReactNode {
  const { scrollRef, day, onDay, onPass, reducedTransparency, onReducedTransparency } = props;

  return (
    <div ref={scrollRef} className="ff-scroll">
      <section className="ff-hero" id="top" aria-labelledby="ff-title">
        <div className="ff-tab">
          <p className="ff-eyebrow">
            {FESTIVAL.edition} · {FESTIVAL.dates}
          </p>
          <h1 id="ff-title" className="ff-title">
            {FESTIVAL.name} <span>Film Festival</span>
          </h1>
          <p className="ff-lede">Twenty-four films in three cinemas over four winter days.</p>
          <p className="ff-opening">
            Opens Thursday at 19:30 at the Regent with Aoi Hayama’s <cite>Ironai</cite>.{" "}
            <a href="#programme" onClick={() => onDay("thu")}>
              See Thursday
            </a>
          </p>
          <p className="ff-caption">
            Behind: a still from <cite>Ironai</cite>. Photograph by{" "}
            <a href="https://unsplash.com/@plainery_">Plainery n.</a> on Unsplash.
          </p>
        </div>
      </section>

      <main className="ff-sheet" id="main">
        <Programme day={day} />
        <Strands />
        <Passes onPass={onPass} />
        <Visit reducedTransparency={reducedTransparency} onReducedTransparency={onReducedTransparency} />
      </main>

      <footer className="ff-footer">
        <p>
          Stills: <cite>Ironai</cite>, photograph by{" "}
          <a href="https://unsplash.com/@plainery_">Plainery n.</a>; <cite>Haar</cite>, photograph by{" "}
          <a href="https://unsplash.com/@elintabitha">Elin Tabitha</a>. Both on Unsplash.
        </p>
        <p>
          The festival, its cinemas and nineteen of its films are invented for this page; the five
          Restored films are real. A Liquid Glass demo on vitrea 0.24.0.{" "}
          <a href="../">Back to the gallery</a>
        </p>
      </footer>
    </div>
  );
}

function Programme(props: { readonly day: DayId }): ReactNode {
  const { day } = props;
  const screenings = SCREENINGS.filter((s) => s.day === day);
  const starts = screenings.map((s) => minutesOf(s.start));
  const ends = screenings.map((s) => minutesOf(s.start) + filmOf(s).minutes);
  const axisStart = Math.floor(Math.min(...starts) / 60) * 60;
  const axisEnd = Math.ceil(Math.max(...ends) / 60) * 60;
  const hours: number[] = [];
  for (let m = axisStart; m <= axisEnd; m += 60) hours.push(m);
  const height = (axisEnd - axisStart) * PX_PER_MINUTE;

  return (
    <section id="programme" className="ff-section" aria-labelledby="programme-title">
      <div className="ff-section-head">
        <h2 id="programme-title">Programme</h2>
        <p className="ff-day-title" aria-live="polite">
          {dayOf(day).long}
          <span>
            {NUMBER_WORDS[screenings.length]} {screenings.length === 1 ? "film" : "films"}
          </span>
        </p>
      </div>

      <div className="ff-schedule">
        <div className="ff-schedule-head" aria-hidden="true">
          <span />
          {VENUES.map((venue) => (
            <span key={venue.id} className="ff-venue-head">
              <b>{venue.name}</b>
              {venue.seats} seats
            </span>
          ))}
        </div>
        <div className="ff-schedule-body" style={{ height }}>
          <ol className="ff-hours" aria-hidden="true">
            {hours.map((m) => (
              <li key={m} style={{ top: (m - axisStart) * PX_PER_MINUTE }}>
                {clock(m)}
              </li>
            ))}
          </ol>
          {VENUES.map((venue) => (
            <section key={venue.id} className="ff-venue" aria-label={`${venue.name}, ${venue.seats} seats`}>
              <ol className="ff-slots">
                {screenings
                  .filter((s) => s.venue === venue.id)
                  .map((s) => {
                    const film = filmOf(s);
                    const start = minutesOf(s.start);
                    return (
                      <li
                        key={s.film}
                        className="ff-slot"
                        data-gala={film.strand === "galas" ? "" : undefined}
                        style={{
                          top: (start - axisStart) * PX_PER_MINUTE,
                          height: film.minutes * PX_PER_MINUTE,
                        }}
                      >
                        <p className="ff-slot-time">
                          <time>{s.start}</time>–<time>{clock(start + film.minutes)}</time>
                        </p>
                        <h3 className="ff-slot-title">{film.title}</h3>
                        <p className="ff-slot-meta">
                          {film.director} · {film.country} · {film.minutes} min
                        </p>
                        <p className="ff-slot-strand">{film.billing ?? strandOf(film.strand).name}</p>
                      </li>
                    );
                  })}
              </ol>
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}

function when(film: Film): string {
  const screening = screeningOf(film.id);
  return `${dayOf(screening.day).short} ${screening.start}, ${venueOf(screening.venue).name}`;
}

function Strands(): ReactNode {
  const galas = FILMS.filter((film) => film.strand === "galas");
  const rest = STRANDS.filter((strand) => strand.id !== "galas");

  return (
    <section id="strands" className="ff-section" aria-labelledby="strands-title">
      <div className="ff-section-head">
        <h2 id="strands-title">Strands</h2>
        <p className="ff-section-note">Five ways through the programme.</p>
      </div>

      <div className="ff-galas">
        <figure className="ff-figure">
          <img
            src={haarUrl}
            width={1800}
            height={1200}
            alt="Still from Haar: a lone figure in a dark coat walks a flat shoreline in thick sea fog, a pier faint behind."
          />
          <figcaption>
            <cite>Haar</cite> (Morag Lindsay, 2027) closes the festival on Sunday. Photograph by{" "}
            <a href="https://unsplash.com/@elintabitha">Elin Tabitha</a> on Unsplash.
          </figcaption>
        </figure>
        <div className="ff-strand ff-strand--galas">
          <h3>{strandOf("galas").name}</h3>
          <p className="ff-strand-line">{strandOf("galas").line}</p>
          <ol className="ff-gala-list">
            {galas.map((film) => (
              <li key={film.id}>
                <p className="ff-gala-billing">{film.billing}</p>
                <h4>
                  <cite>{film.title}</cite>
                </h4>
                <p className="ff-gala-meta">
                  {film.director} · {film.country} {film.year} · {film.minutes} min · {when(film)}
                </p>
                <p className="ff-gala-line">{film.line}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>

      <div className="ff-strand-grid">
        {rest.map((strand) => (
          <div key={strand.id} className="ff-strand">
            <h3>{strand.name}</h3>
            <p className="ff-strand-line">{strand.line}</p>
            <ol className="ff-strand-films">
              {FILMS.filter((film) => film.strand === strand.id).map((film) => (
                <li key={film.id}>
                  <cite>{film.title}</cite>
                  <span>
                    {film.director}, {film.year}
                  </span>
                  <span>{when(film)}</span>
                </li>
              ))}
            </ol>
          </div>
        ))}
      </div>
    </section>
  );
}

function Passes(props: { readonly onPass: (pass: PassId) => void }): ReactNode {
  return (
    <section id="passes" className="ff-section" aria-labelledby="passes-title">
      <div className="ff-section-head">
        <h2 id="passes-title">Passes</h2>
        <p className="ff-section-note">Box office in the Regent’s foyer, 10:00–21:00 every day.</p>
      </div>
      <ul className="ff-passes">
        {PASSES.map((pass) => (
          <li key={pass.id} id={`pass-${pass.id}`} className="ff-pass">
            <h3>{pass.name}</h3>
            <p className="ff-pass-price">£{pass.price}</p>
            <p className="ff-pass-detail">{pass.detail}</p>
            <button type="button" className="ff-pass-buy" onClick={() => props.onPass(pass.id)}>
              Buy {pass.name.toLowerCase()}
            </button>
          </li>
        ))}
      </ul>
      <p className="ff-pass-note">
        Companion tickets are free for anyone who needs one. Every Tolbooth screening carries audio
        description, and every Real Weather screening is captioned.
      </p>
    </section>
  );
}

interface VisitProps {
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (on: boolean) => void;
}

function Visit(props: VisitProps): ReactNode {
  const { reducedTransparency, onReducedTransparency } = props;
  return (
    <section id="visit" className="ff-section" aria-labelledby="visit-title">
      <div className="ff-section-head">
        <h2 id="visit-title">Visit</h2>
        <p className="ff-section-note">Three cinemas, eight minutes apart on foot along the quay.</p>
      </div>
      <ul className="ff-venues">
        {VENUES.map((venue) => (
          <li key={venue.id} className="ff-venue-card">
            <h3>{venue.name}</h3>
            <p className="ff-venue-address">{venue.address}</p>
            <p className="ff-venue-seats">{venue.seats} seats</p>
            <p>{venue.access}</p>
          </li>
        ))}
      </ul>

      <div className="ff-settings" role="group" aria-labelledby="settings-title">
        <h3 id="settings-title">This page</h3>
        <label className="ff-switch">
          <input
            type="checkbox"
            role="switch"
            checked={reducedTransparency}
            onChange={(event) => onReducedTransparency(event.currentTarget.checked)}
          />
          <span className="ff-switch-track" aria-hidden="true" />
          <span className="ff-switch-label">Reduce transparency</span>
        </label>
        <p>
          Makes the floating controls frostier and more opaque. It follows your system setting until
          you change it here.
        </p>
      </div>
    </section>
  );
}

