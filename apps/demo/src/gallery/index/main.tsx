/**
 * The gallery index: six demos built under the materialist skill
 * (docs/doperpowers/specs/2026-09-27-materialist-proof.md, A).
 *
 * It belongs to the site, so it is written in the site's tokens and components and under
 * its law (`apps/demo/DESIGN.md`). It is content rather than a control layer, so it
 * carries no glass and no depicted material: the demos are where the material is. Each
 * entry's plane and floating lines are read from that demo's own record
 * (`src/gallery/<slug>/DESIGN.md`) and name the plane and the kinds of floating surface
 * rather than counts, so a fix to a demo does not make its entry here false.
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
  readonly brief: string;
  readonly plane: string;
  readonly floating: string;
}

const DEMOS: readonly Demo[] = [
  {
    slug: "music-player",
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
          <dt>Plane</dt>
          <dd>{demo.plane}</dd>
        </div>
        <div className="readout__row">
          <dt>Floating</dt>
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
          Six Liquid Glass pages on vitrea 0.24.0, each built by one agent that read the{" "}
          <a href={SKILL}>materialist skill</a> and nothing else about design, and each
          carrying its own design record. Three are product surfaces and three are narrative
          pages; every one sets its controls over a live plane and keeps its content
          opaque.{" "}
          <a href={SPEC}>The initiative&rsquo;s spec</a> says what the pages test and how they
          are judged.
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
