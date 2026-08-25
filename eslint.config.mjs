// Shared ESLint configs for the vitrea workspace.
//
// Each package has a two-line `eslint.config.mjs` that re-exports one of the
// named configs below, so `eslint .` inside a package resolves its own rules
// and its own base path.
//
// X4 (purity law) is enforced in two independent layers:
//   1. the type system — pure packages compile with `lib: ["ES2022"]` and no
//      DOM lib, so `window`, `document` and `HTMLElement` fail `tsc`;
//   2. `no-restricted-globals` below, which also covers `navigator` (declared
//      by @types/node, therefore invisible to layer 1) and gives a message that
//      names the law.
// `packages/core/test/purity-law.test.ts` exercises both layers.

import js from "@eslint/js";
import tseslint from "typescript-eslint";

/** Browser globals that `core`, `geometry` and `motion` must never touch (X4). */
const FORBIDDEN_BROWSER_GLOBALS = [
  "window",
  "document",
  "navigator",
  "self",
  "parent",
  "top",
  "location",
  "screen",
  "customElements",
  "requestAnimationFrame",
  "cancelAnimationFrame",
  "HTMLElement",
  "getComputedStyle",
];

/** DOM types that must not appear even in type position inside pure packages. */
const FORBIDDEN_DOM_TYPES = {
  HTMLElement: "X4: pure packages are DOM-free — model the host abstractly and let platform-web bind it.",
  Element: "X4: pure packages are DOM-free — model the host abstractly and let platform-web bind it.",
  Document: "X4: pure packages are DOM-free.",
  Window: "X4: pure packages are DOM-free.",
  Node: "X4: pure packages are DOM-free — if you meant a graph node, name it explicitly.",
};

const NODE_BUILTIN_PATTERNS = [
  {
    group: ["node:*", "fs", "path", "os", "child_process", "url", "worker_threads"],
    message: "Browser-shipped packages must not import Node built-ins.",
  },
];

const PURITY_MESSAGE =
  "X4 (purity law): core, geometry and motion never reference the DOM. Move browser access to @vitrea/platform-web.";

/**
 * Timers and clocks. `core` is passive by contract: it never schedules and never
 * reads the time — a host drives frames and supplies the timestamp as data (see
 * `FrameInfo`). These are invisible to the DOM-free typecheck because
 * `@types/node` declares them, so the rule below is the only layer that catches
 * them.
 */
const TIMER_AND_CLOCK_GLOBALS = [
  "setTimeout",
  "setInterval",
  "clearTimeout",
  "clearInterval",
  "setImmediate",
  "clearImmediate",
  "queueMicrotask",
  "performance",
  "Date",
];

const PASSIVE_MESSAGE =
  "Core is passive: no timers, no clocks, no rAF. Cadence is driven by the host and time arrives as data (FrameInfo.timeMs).";

export const base = tseslint.config(
  {
    ignores: ["**/dist/**", "**/node_modules/**", "**/coverage/**", "**/.vitrea-tmp/**"],
  },
  js.configs.recommended,
  tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/consistent-type-imports": ["error", { fixStyle: "inline-type-imports" }],
      "@typescript-eslint/no-import-type-side-effects": "error",
      "no-console": ["error", { allow: ["warn", "error"] }],
    },
  },
);

/** core, geometry, motion — no DOM, no Node built-ins, no downstream imports. */
export const pure = tseslint.config(
  ...base,
  {
    files: ["src/**/*.ts"],
    rules: {
      "no-restricted-globals": [
        "error",
        ...FORBIDDEN_BROWSER_GLOBALS.map((name) => ({ name, message: PURITY_MESSAGE })),
      ],
      "@typescript-eslint/no-restricted-types": ["error", { types: FORBIDDEN_DOM_TYPES }],
      "no-restricted-imports": [
        "error",
        {
          patterns: NODE_BUILTIN_PATTERNS,
          paths: [
            {
              name: "@vitrea/platform-web",
              message: "Package boundary: platform-web depends on core, never the other way round.",
            },
            {
              name: "@vitreajs/vitrea-react",
              message: "Package boundary: bindings depend on the runtime, never the other way round.",
            },
          ],
        },
      ],
    },
  },
);

/**
 * core — `pure`, plus the passivity law. The scheduler in `core` is a contract
 * and a reference implementation, never a running loop, so nothing here may arm
 * a timer or read a clock.
 */
export const passive = tseslint.config(...pure, {
  files: ["src/**/*.ts"],
  rules: {
    // A later entry replaces rather than merges, so the purity list is repeated.
    "no-restricted-globals": [
      "error",
      ...FORBIDDEN_BROWSER_GLOBALS.map((name) => ({ name, message: PURITY_MESSAGE })),
      ...TIMER_AND_CLOCK_GLOBALS.map((name) => ({ name, message: PASSIVE_MESSAGE })),
    ],
  },
});

/** platform-web, renderer-webgpu, react, demo — the DOM is their job; Node is not. */
export const browser = tseslint.config(...base, {
  files: ["src/**/*.ts", "src/**/*.tsx"],
  rules: {
    "no-restricted-imports": ["error", { patterns: NODE_BUILTIN_PATTERNS }],
  },
});

/** calibration — a Node CLI: built-ins allowed, the DOM still is not. */
export const node = tseslint.config(...base, {
  files: ["src/**/*.ts"],
  rules: {
    "no-restricted-globals": [
      "error",
      ...["window", "document", "HTMLElement"].map((name) => ({
        name,
        message: "The calibration CLI runs in Node — it has no DOM.",
      })),
    ],
  },
});

// Root config: repo-level files only. Packages carry their own.
//
// `spikes/**` is ignored alongside them: a spike's deliverable is findings, and
// its harness is throwaway browser-context evidence that never ships. Linting it
// against the repo's Node-flavoured root rules only reports globals it is
// supposed to be using.
export default tseslint.config(
  { ignores: ["packages/**", "apps/**", "skills/**", "docs/**", "spikes/**", "Figma Design/**", "figma-design-workspace/**", ".playwright-cli/**", ".claude/**"] },
  ...base,
);
