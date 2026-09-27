/**
 * Film festival: scaffold stub. The maker replaces this file
 * (docs/doperpowers/specs/2026-09-27-materialist-proof.md, A).
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const container = document.getElementById("root");
if (container === null) throw new Error("The film-festival page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <main style={{ padding: "3rem", fontFamily: "system-ui" }}>
      <h1>Film festival</h1>
      <p>Being built.</p>
    </main>
  </StrictMode>,
);
