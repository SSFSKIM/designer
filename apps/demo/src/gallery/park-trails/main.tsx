/**
 * Park trails: the trails site for North Cascades National Park, a gallery page of the vitrea
 * demo site built under the materialist skill. The design record is DESIGN.md beside this file.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import "./styles.css";

const container = document.getElementById("root");
if (container === null) throw new Error("The park-trails page has no #root to mount into.");

/*
 * Where the glass root attaches its planes: an element before #root rather than the end of the
 * body, so the planner, the page's instrument, comes first in the document's reading and tab
 * order, the way a header does. It is a plain block with no box of its own; the planes inside it
 * are fixed to the viewport, and nothing on this element or above it filters, masks or clips.
 */
const glassContainer = document.createElement("div");
glassContainer.dataset.ptGlass = "";
container.before(glassContainer);

createRoot(container).render(
  <StrictMode>
    <App glassContainer={glassContainer} />
  </StrictMode>,
);
