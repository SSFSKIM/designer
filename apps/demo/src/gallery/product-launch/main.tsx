/**
 * Product launch: the Alder One, a full-frame camera from a small maker. The design record is
 * `DESIGN.md` beside this file; the page's composition starts in `App.tsx`.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import "./styles.css";

const container = document.getElementById("root");
if (container === null) throw new Error("The product-launch page has no #root to mount into.");

/*
 * The glass root's home, placed before the page in document order. Its layer is fixed and stacked
 * above the page whatever the order, but sequential focus and a screen reader's reading order follow
 * the DOM: with the root appended to the end of <body>, as it is by default, the navigation would be
 * the last thing a keyboard reached. Here it is the first, as a page header is.
 */
const glassLayer = document.createElement("div");
glassLayer.setAttribute("data-glass-layer", "");
container.before(glassLayer);

createRoot(container).render(
  <StrictMode>
    <App glassContainer={glassLayer} />
  </StrictMode>,
);
