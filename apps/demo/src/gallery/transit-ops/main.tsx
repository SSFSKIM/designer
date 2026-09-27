/**
 * Transit operations: Port Alder Transit's control-room map, a gallery page of the
 * vitrea demo site built under the materialist skill. The design record, including
 * what the runtime resolved and what was measured, is `DESIGN.md` beside this file.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

const container = document.getElementById("root");
if (container === null) throw new Error("The transit-ops page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
