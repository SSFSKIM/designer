/**
 * The gallery index: six demos built under the materialist skill
 * (docs/doperpowers/specs/2026-09-27-materialist-proof.md, A). Content, not a
 * control layer, so it carries no glass: the demos are where the material is.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const DEMOS: readonly { slug: string; title: string; plane: string }[] = [
  { slug: "music-player", title: "Music player", plane: "the album's artwork" },
  { slug: "transit-ops", title: "Transit operations", plane: "a city map with live vehicles" },
  { slug: "photo-review", title: "Photo review", plane: "the photograph on the stage" },
  { slug: "film-festival", title: "Film festival", plane: "the opening film's still" },
  { slug: "park-trails", title: "Park trails", plane: "the park's panorama" },
  { slug: "product-launch", title: "Product launch", plane: "the camera's photography" },
];

function Gallery() {
  return (
    <main style={{ padding: "3rem", fontFamily: "system-ui", maxWidth: "48rem" }}>
      <h1>The gallery</h1>
      <p>Six Liquid Glass demos built under the materialist skill, on vitrea 0.24.0.</p>
      <ul>
        {DEMOS.map((demo) => (
          <li key={demo.slug}>
            <a href={`./${demo.slug}/`}>{demo.title}</a> — over {demo.plane}
          </li>
        ))}
      </ul>
    </main>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The gallery page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Gallery />
  </StrictMode>,
);
