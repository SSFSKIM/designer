import { RENDERER_TIERS, VITREA_CONTRACTS } from "@vitrea/core";
import { GLASS_ROOT_ACCESSIBILITY_DEFAULTS, SUPPORTED_PLANES } from "@vitrea/react";

/**
 * Placeholder playground (C1). It renders the contract sets the workspace
 * exports today, which is what makes it a real integration check: if the
 * publish shape or the package graph breaks, this page stops building.
 * C9 turns it into the showpiece.
 */
export function App() {
  const rows: readonly [label: string, value: readonly string[]][] = [
    ["renderer tiers", RENDERER_TIERS],
    ["shape families", VITREA_CONTRACTS.shapeFamilies],
    ["interaction states", VITREA_CONTRACTS.interactionStates],
    ["planes", SUPPORTED_PLANES],
    ["a11y defaults", Object.values(GLASS_ROOT_ACCESSIBILITY_DEFAULTS).map(String)],
  ];

  return (
    <main
      style={{
        minHeight: "100vh",
        margin: 0,
        padding: "clamp(1.5rem, 6vw, 5rem)",
        background: "#0b0d10",
        color: "#e8eaed",
        fontFamily: "ui-sans-serif, system-ui, -apple-system, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "clamp(1.75rem, 5vw, 3rem)", margin: "0 0 0.5rem", fontWeight: 600 }}>
        vitrea
      </h1>
      <p style={{ margin: "0 0 2.5rem", opacity: 0.6, maxWidth: "48ch", lineHeight: 1.6 }}>
        Liquid Glass material runtime for the web. The skeleton is wired; no glass is drawn yet.
      </p>

      <dl style={{ display: "grid", gap: "0.75rem", margin: 0 }}>
        {rows.map(([label, value]) => (
          <div key={label} style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            <dt style={{ minWidth: "12rem", opacity: 0.5 }}>{label}</dt>
            <dd style={{ margin: 0, fontVariantNumeric: "tabular-nums" }}>{value.join(" · ")}</dd>
          </div>
        ))}
      </dl>
    </main>
  );
}
