/**
 * X4 — policy is a leaf, and the leaf-ness is the whole point.
 *
 * Modelled on `geometry/test/purity.test.ts`, which explains the split: core
 * already proves the LINT layer enforces the purity law, so a pure package's own
 * purity test asserts the complementary thing — that its source is actually
 * clean, and that the type layer has not been quietly weakened to make it so.
 *
 * One assertion here carries more weight than it does in geometry. This package
 * exists *because* it can be imported from both above and below core (Decision
 * Log #23(d)): `renderer-webgpu` sits under core and cannot import it, so the
 * moment `@vitrea/policy` acquires a dependency of any kind — core most of all —
 * the cycle it was created to avoid is back, and the renderer's build is what
 * breaks. "No dependencies" is not hygiene here; it is the load-bearing property.
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = join(packageRoot, "src");

function sourceFiles(): { name: string; text: string }[] {
  return readdirSync(srcDir)
    .filter((f) => f.endsWith(".ts"))
    .map((name) => ({ name, text: readFileSync(join(srcDir, name), "utf8") }));
}

/** Comments talk about the DOM and about core legitimately; only code counts. */
function code(text: string): string {
  return text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
}

const FORBIDDEN = [
  "window",
  "document",
  "navigator",
  "HTMLElement",
  "Element",
  "getComputedStyle",
  "requestAnimationFrame",
  "cancelAnimationFrame",
  "customElements",
  "localStorage",
  "process",
];

describe("policy references nothing outside itself (X4)", () => {
  it("has source files to check", () => {
    const files = sourceFiles();
    expect(files.map((f) => f.name).sort()).toEqual(["index.ts", "refraction.ts"]);
  });

  it("names no browser global or DOM type in any source file", () => {
    for (const { name, text } of sourceFiles()) {
      const body = code(text);
      for (const forbidden of FORBIDDEN) {
        expect(
          new RegExp(`\\b${forbidden}\\b`).test(body),
          `${name} references \`${forbidden}\``,
        ).toBe(false);
      }
    }
  });

  it("imports nothing at all outside this package", () => {
    for (const { name, text } of sourceFiles()) {
      const imports = [...code(text).matchAll(/from\s+"([^"]+)"/g)].map((m) => m[1] as string);
      for (const spec of imports) {
        expect(spec.startsWith("./") || spec.startsWith("../"), `${name} imports "${spec}"`).toBe(
          true,
        );
      }
    }
  });

  it("declares no dependencies in package.json", () => {
    const pkg = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8")) as {
      private?: boolean;
      dependencies?: Record<string, string>;
      peerDependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };
    expect(pkg.dependencies ?? {}).toEqual({});
    expect(pkg.peerDependencies ?? {}).toEqual({});

    // Not @types/node either: it declares ~2000 ambient globals, all of them
    // visible to src/, at which point X4 rests on ESLint alone. This test tree
    // reads files, so it uses `node:fs` directly — that is what `types: []` plus
    // vitest's own environment allows, and src/ still sees none of it.
    expect(Object.keys(pkg.devDependencies ?? {})).not.toContain("@types/node");

    // X7: private, so it is bundled into the three published artifacts rather
    // than published as a fourth. `core/test/bundle-shape.test.ts` guards the set.
    expect(pkg.private).toBe(true);
  });

  it("keeps the DOM-free typecheck rather than relying on lint alone", () => {
    const tsconfig = JSON.parse(readFileSync(join(packageRoot, "tsconfig.json"), "utf8")) as {
      compilerOptions?: { types?: string[]; lib?: string[] };
    };
    expect(tsconfig.compilerOptions?.types).toBeUndefined();
    expect(tsconfig.compilerOptions?.lib).toBeUndefined();
  });

  it("uses the shared `pure` ESLint config, so the lint layer applies too", () => {
    const config = readFileSync(join(packageRoot, "eslint.config.mjs"), "utf8");
    expect(config).toContain("pure");
    expect(config).toContain("../../eslint.config.mjs");
  });
});
