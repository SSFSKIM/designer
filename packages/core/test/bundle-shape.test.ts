/**
 * X7 — proof that the published artifact has the shape the spec promises:
 * internals bundled in, WGSL only in a lazy chunk, no dependency on a package
 * that was never published.
 *
 * Reads `dist/`, so it needs `pnpm build` to have run (CI builds first).
 */

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(packageRoot, "dist");
const entryPath = join(distDir, "index.js");

const WGSL_MARKER = "vitrea:wgsl-marker";

/** Matches a real module specifier, so prose mentioning `@vitrea/x` never trips the test. */
const IMPORTS_INTERNAL_PACKAGE = /(?:\bfrom|\bimport\(|\bimport)\s*["']@vitrea\//;

describe.skipIf(!existsSync(entryPath))("built artifact shape (X7)", () => {
  const entry = readFileSync(entryPath, "utf8");
  const chunks = readdirSync(distDir).filter((name) => name.endsWith(".js") && name !== "index.js");

  it("bundles the internal packages instead of importing them", () => {
    expect(IMPORTS_INTERNAL_PACKAGE.test(entry)).toBe(false);
    expect(entry).toContain("concentric-rounded-rect"); // from @vitrea/geometry
    expect(entry).toContain("interruptible-spring"); // from @vitrea/motion
  });

  it("keeps WGSL out of the entry chunk and inside a lazy chunk", () => {
    expect(entry).not.toContain(WGSL_MARKER);

    const lazyChunks = chunks.filter((name) =>
      readFileSync(join(distDir, name), "utf8").includes(WGSL_MARKER),
    );
    expect(lazyChunks).toHaveLength(1);
  });

  it("emits declarations that point at nothing unpublished", () => {
    const declarations = readFileSync(join(distDir, "index.d.ts"), "utf8");
    expect(IMPORTS_INTERNAL_PACKAGE.test(declarations)).toBe(false);
    expect(declarations).toContain("GlassGroupState");
  });

  it("declares no runtime dependencies", () => {
    const manifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8")) as {
      dependencies?: Record<string, string>;
    };
    expect(manifest.dependencies ?? {}).toEqual({});
  });
});

describe("publish surface (X7)", () => {
  it("leaves exactly @vitrea/core and @vitrea/react publishable", () => {
    const packagesDir = join(packageRoot, "..");
    const publishable = readdirSync(packagesDir)
      .filter((entry) => statSync(join(packagesDir, entry)).isDirectory())
      .map(
        (entry) =>
          JSON.parse(readFileSync(join(packagesDir, entry, "package.json"), "utf8")) as {
            name: string;
            private?: boolean;
          },
      )
      .filter((manifest) => manifest.private !== true)
      .map((manifest) => manifest.name)
      .sort();

    expect(publishable).toEqual(["@vitrea/core", "@vitrea/react"]);
  });
});
