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
              name: "@vitrea/react",
              message: "Package boundary: bindings depend on the runtime, never the other way round.",
            },
          ],
        },
      ],
    },
  },
);

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
export default tseslint.config(
  { ignores: ["packages/**", "apps/**", "skills/**", "docs/**", "Figma Design/**"] },
  ...base,
);
