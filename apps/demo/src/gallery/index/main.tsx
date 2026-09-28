/**
 * The gallery index: eight pages in two registers under the materialist skill, and the flagships
 * (docs/doperpowers/specs/2026-09-27-materialist-proof.md, A;
 * docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md, C).
 *
 * It belongs to the site, so it is written in the site's tokens and components and under
 * its law (`apps/demo/DESIGN.md`). It is content rather than a control layer, so it
 * carries no glass and no depicted material: the demos are where the material is. Each
 * entry's plane and floating lines are read from its page's design record
 * (`src/gallery/<slug>/DESIGN.md`): the plane and the kinds of floating surface, never
 * counts. A spatial entry labels the two lines Environment and Windows, that register's
 * own words for them.
 *
 * The colour scheme is not set here. The site's tokens switch on one attribute, and the
 * page's head mirrors `prefers-color-scheme` onto it before the first paint.
 */
import { StrictMode, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import "../../tokens.css";
import "../../site/site.css";
import "./gallery.css";

const REPOSITORY = "https://github.com/SSFSKIM/designer";
const SKILL = `${REPOSITORY}/tree/main/skills/materialist`;
const SPEC = `${REPOSITORY}/blob/main/docs/doperpowers/specs/2026-09-27-materialist-proof.md`;

interface Demo {
  readonly slug: string;
  readonly title: string;
  readonly register: "instrument" | "spatial";
  readonly brief: string;
  readonly plane: string;
  readonly floating: string;
}

const DEMOS: readonly Demo[] = [
  {
    slug: "music-player",
    register: "instrument",
    title: "Music player",
    brief:
      "A streaming service’s Mac web client, Fathom, with the sounding album’s artwork " +
      "filling the window and the player’s controls floating over it.",
    plane:
      "The sounding release’s artwork, painted cover-fit into one viewport-fixed canvas " +
      "that every glass group reads as its texture.",
    floating:
      "The transport, the volume and the queue’s action, which morphs into a playlist " +
      "menu; the queue itself is an opaque panel.",
  },
  {
    slug: "transit-ops",
    register: "instrument",
    title: "Transit operations",
    brief:
      "The control-room map of Port Alder Transit, where a dispatcher finds what is wrong " +
      "on the network and acts on one vehicle.",
    plane: "A live city map in one full-viewport canvas, its buses moving along their routes.",
    floating:
      "Route, status and search controls along the top, search suggestions, the zoom " +
      "stack and the selected vehicle’s actions; the alerts and the vehicle’s details are " +
      "opaque panels.",
  },
  {
    slug: "photo-review",
    register: "instrument",
    title: "Photo review",
    brief:
      "A culling and adjustment tool for a working photographer deciding on a shoot one " +
      "frame at a time.",
    plane:
      "The selected frame, painted with its adjustments applied into one canvas above " +
      "the filmstrip.",
    floating:
      "The tool palette, which grows into the adjustment platter, the before and after " +
      "toggle and the verdict bar; the shoot, the frame’s data and the filmstrip are opaque.",
  },
  {
    slug: "film-festival",
    register: "instrument",
    title: "Film festival",
    brief:
      "The programme page of the Northlight Film Festival, for a reader choosing what to " +
      "see and buying a ticket.",
    plane:
      "A still from the opening film in one viewport-fixed canvas, cropped so every " +
      "control stands over structure.",
    floating:
      "One row at the top: the navigation, the day control and a Tickets capsule that " +
      "morphs into a platter; the programme scrolls beneath on opaque paper.",
  },
  {
    slug: "park-trails",
    register: "instrument",
    title: "Park trails",
    brief:
      "The trails site for North Cascades National Park, where a hiker plans one route " +
      "and the page beneath reads for it.",
    plane:
      "A photograph of Diablo Lake in one viewport-fixed canvas, cropped so the forested " +
      "ridge lies under the planner.",
    floating:
      "A trip planner: the route capsule, which morphs into the route menu, and weather " +
      "and permits buttons that take the reader down the page; the trail sheet scrolls " +
      "over the photograph on opaque paper.",
  },
  {
    slug: "product-launch",
    register: "instrument",
    title: "Product launch",
    brief:
      "The launch page for the Alder One, a small maker’s mirrorless camera, told section " +
      "by section over its own photography.",
    plane:
      "The camera’s photographs, one per section and per chosen lens or finish, " +
      "cross-dissolving in one viewport-fixed canvas.",
    floating:
      "Section navigation and the display setting at the top; finish, lens and order at " +
      "the bottom, the lens chooser morphing into a platter.",
  },
  {
    slug: "exhibition",
    register: "spatial",
    title: "Exhibition · Weather in Painting",
    brief:
      "The online viewing room of a museum exhibition, Weather in Painting: one work fills " +
      "the screen at a time, and the visitor reads about it while seeing it. The label essay " +
      "and the work’s data sit on glass set into the painting; the audio guide’s transport " +
      "and the way between works hang at that window’s edge. Eight public-domain works, " +
      "credited by title, maker, date and collection.",
    plane:
      "The work on view, painted cover-fit into one viewport-fixed canvas, washed only " +
      "beneath the glass and dissolving from work to work.",
    floating:
      "A label window holding the essay, the work’s data and the rooms, and below its " +
      "edge the ornaments for moving between rooms and for the audio guide.",
  },
  {
    slug: "start-page",
    register: "spatial",
    title: "Start page · Daybreak",
    brief:
      "A browser start page, Daybreak: the day’s photograph fills the window, and the time, " +
      "weather, agenda, tasks and places sit on glass over it, glanceable from across the " +
      "room and workable up close; a search field leads. A full day’s agenda, seven tasks, " +
      "twelve places and a five-day forecast.",
    plane:
      "The day’s photograph of one valley, at dawn, day, dusk or night by the clock, in " +
      "one viewport-fixed canvas graded for each colour scheme.",
    floating:
      "A glance module for the time and weather, windows for places and for the day’s " +
      "agenda and tasks, a search ornament above the places, and a photograph ornament " +
      "that morphs into a platter.",
  },
  {
    slug: "planetarium",
    register: "spatial",
    title: "Planetarium · Tonight",
    brief:
      "A planetarium display, Tonight: the real sky over a place, drawn live and turning with the " +
      "Earth, is the environment. What is up, the Moon and the night’s timeline sit on clear " +
      "Liquid Glass set into it, at the thickness the lens shows best; drag the sky, scrub the " +
      "night, choose a star. The gallery’s flagship, built to show the material’s optics rather " +
      "than its frost.",
    plane:
      "The sky itself, drawn in WebGL from 9,096 catalogue stars, NASA’s Milky Way map and " +
      "astronomy-engine’s Sun, Moon and planets, in one viewport-fixed canvas that turns with " +
      "the clock; the page paints the clear variant’s dimming into it under each window.",
    floating:
      "A Tonight window listing what is up with the chosen object’s card, a Moon module, and " +
      "two ornaments — the place and the time — that morph into platters.",
  },
  {
    slug: "chronograph",
    register: "instrument",
    title: "Chronograph",
    brief:
      "A rattrapante chronograph on a watchmaker’s bench, running live under a domed crystal. " +
      "The crystal and a loupe you can move over the dial are optical glass with nothing on " +
      "them; the stopwatch’s controls beside the watch are the same glass, tuned from Apple’s " +
      "frost toward clear optics, with the calibrated material one choice away for comparison.",
    plane:
      "The bench and the watch on it, painted live in one viewport-fixed canvas: a gridded " +
      "cutting mat, a tapisserie dial whose hands beat eight times a second, and under the " +
      "loupe the same scene drawn twice the size.",
    floating:
      "The crystal and the loupe, which carry nothing; a timing window with the laps; Lap and " +
      "Start buttons; a dial switch; and a crystal capsule that morphs into a platter.",
  },
];

function Entry(props: { readonly demo: Demo; readonly index: number }): ReactNode {
  const { demo, index } = props;
  return (
    <li className="entry">
      <span className="entry__index" aria-hidden="true">
        {String(index + 1).padStart(2, "0")}
      </span>
      <div className="entry__head">
        <h2 className="h2 entry__title">
          <a href={`./${demo.slug}/`}>{demo.title}</a>
        </h2>
        <p className="body entry__brief">{demo.brief}</p>
      </div>
      <dl className="readout readout--entry">
        <div className="readout__row">
          <dt>Register</dt>
          <dd>
            {demo.register === "instrument"
              ? "Instrument: glass over the content"
              : "Spatial: glass is the surface"}
          </dd>
        </div>
        <div className="readout__row">
          <dt>{demo.register === "spatial" ? "Environment" : "Plane"}</dt>
          <dd>{demo.plane}</dd>
        </div>
        <div className="readout__row">
          <dt>{demo.register === "spatial" ? "Windows" : "Floating"}</dt>
          <dd>{demo.floating}</dd>
        </div>
      </dl>
    </li>
  );
}

function Gallery(): ReactNode {
  return (
    <div className="gallery">
      <header className="masthead">
        <p className="wordmark">vitrea</p>
        <h1 className="display">The materialist gallery</h1>
        <p className="lead">
          Ten Liquid Glass pages on vitrea 0.24.0: six instrument pages set glass controls
          over live content, two spatial pages make glass the surface itself, and two
          flagships spend the material’s optics: Tonight on a live sky, and Chronograph on a
          watch under its crystal. Each follows the{" "}
          <a href={SKILL}>materialist skill</a>. The{" "}
          <a href={SPEC}>instrument proof</a> and{" "}
          <a href={`${REPOSITORY}/blob/main/docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md`}>
            spatial register spec
          </a>{" "}
          say what the pages test.
        </p>
      </header>

      <main>
        {/* `role` restates the list: WebKit drops list semantics from a list without markers. */}
        <ol className="gallery__demos" role="list">
          {DEMOS.map((demo, index) => (
            <Entry key={demo.slug} demo={demo} index={index} />
          ))}
        </ol>
      </main>

      <footer className="footer">
        <p className="note">
          Built on vitrea 0.24.0. <time dateTime="2026-09-27">27 September 2026</time>.
        </p>
      </footer>
    </div>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The gallery page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Gallery />
  </StrictMode>,
);
