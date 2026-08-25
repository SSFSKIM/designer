/**
 * X7 — proof that `@vitrea/react`'s published artifact has the shape the spec
 * promises: internals bundled in, zero runtime dependencies beyond `@vitrea/core`
 * and the React peer, and — the one this suite added — a `.d.ts` that resolves.
 *
 * The declaration check is not decoration. rollup-plugin-dts leaves a
 * re-exported name external when the package it came from re-exports through
 * `export *` from several sibling modules, and it then emits
 * `import { GlassHostHandle } from "./backdrop-proxy"` into an artifact where no
 * such file exists. The runtime bundle is perfectly correct while the types are
 * unusable, so nothing but a declaration-side assertion catches it.
 *
 * Reads `dist/`, so it needs `pnpm build` to have run (CI builds first).
 */

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(packageRoot, "dist");
const entryPath = join(distDir, "index.js");
const typesPath = join(distDir, "index.d.ts");

/**
 * Every module specifier a file imports or re-exports from.
 *
 * Comments are stripped first: this package's own prose quotes module-ish
 * strings, and a doc comment is not a dependency.
 */
const specifiersIn = (source: string): string[] => {
  const code = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
  const found = new Set<string>();
  for (const match of code.matchAll(/(?:\bfrom|\bimport\(|^\s*import)\s*["']([^"']+)["']/gm)) {
    if (match[1] !== undefined) found.add(match[1]);
  }
  return [...found];
};

describe.skipIf(!existsSync(entryPath))("built artifact shape (X7)", () => {
  const runtime = readFileSync(entryPath, "utf8");
  const types = readFileSync(typesPath, "utf8");

  it("depends on nothing but @vitrea/core and the React peer at runtime", () => {
    expect(specifiersIn(runtime).sort()).toEqual(["@vitrea/core", "react", "react/jsx-runtime"]);
  });

  it("bundles the internal packages instead of importing them", () => {
    expect(runtime).not.toMatch(/["']@vitrea\/(platform-web|geometry|motion)["']/);
    expect(runtime).toContain("data-vitrea-node"); // from @vitrea/platform-web
  });

  it("emits declarations that resolve — nothing points at an unpublished file", () => {
    const relative = specifiersIn(types).filter((specifier) => specifier.startsWith("."));
    expect(relative).toEqual([]);
    expect(specifiersIn(types).sort()).toEqual(["@vitrea/core", "react"]);
  });

  it("declares the components an app imports", () => {
    for (const name of [
      "GlassRoot",
      "GlassGroup",
      "GlassSurface",
      "GlassMorph",
      "GlassButton",
      "GlassIconButton",
      "GlassToolbar",
      "GlassSegmentedControl",
      "useGlassCapabilities",
    ]) {
      expect(types).toContain(name);
      expect(runtime).toContain(name);
    }
  });
});
