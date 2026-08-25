/**
 * X4 — geometry is pure math.
 *
 * Core already proves that the LINT layer enforces the purity law (it seeds a
 * real violation and checks both ESLint and tsc reject it). Repeating that here
 * would re-test the shared config rather than this package, so this file asserts
 * the complementary thing: that geometry's own source is actually clean, and that
 * the type layer has not been quietly weakened to make it so.
 *
 * The type layer matters here in a way it does not in core. Geometry keeps
 * `types: []` and no DOM lib, so `window`, `document`, `HTMLElement`, `process`
 * and every Node built-in are compile errors in `src/` — not merely lint errors.
 * Core had to add `types: ["node"]` for its tooling tests, which declares
 * `navigator` and moves half of its guarantee onto ESLint. Geometry gives that up
 * nowhere, which is why `test/harness/env.ts` declares its one global locally
 * instead.
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

/** Comments talk about the DOM legitimately; only code counts. */
function code(text: string): string {
  return text
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\/\/[^\n]*/g, "");
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

describe("geometry references nothing outside itself (X4)", () => {
  it("has source files to check", () => {
    const files = sourceFiles();
    expect(files.length).toBeGreaterThan(8);
    expect(files.map((f) => f.name)).toContain("field.ts");
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
    // Not just "no Node built-ins": geometry has no runtime dependencies of any
    // kind, so every import must be relative. That is what lets it be bundled into
    // vitrea at publish with nothing trailing behind it.
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
      dependencies?: Record<string, string>;
      peerDependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };
    expect(pkg.dependencies ?? {}).toEqual({});
    expect(pkg.peerDependencies ?? {}).toEqual({});

    // And specifically not @types/node. It would declare ~2000 ambient globals —
    // `process`, `navigator`, `setTimeout` — all of them visible to src/, at which
    // point X4 would rest on ESLint alone. The test tree declares the five Node
    // functions it actually uses in test/harness/node-shims.d.ts instead, which
    // keeps the ambient global scope empty.
    expect(Object.keys(pkg.devDependencies ?? {})).not.toContain("@types/node");
  });

  it("keeps the DOM-free typecheck rather than relying on lint alone", () => {
    // If `types` or `lib` ever grows here, `window` and friends stop being compile
    // errors in src/ and X4 quietly drops to a single layer of enforcement. The
    // point of asserting the CONFIG is that the previous test would still pass.
    const tsconfig = JSON.parse(readFileSync(join(packageRoot, "tsconfig.json"), "utf8")) as {
      compilerOptions?: { types?: string[]; lib?: string[] };
    };
    expect(tsconfig.compilerOptions?.types).toBeUndefined();
    expect(tsconfig.compilerOptions?.lib).toBeUndefined();

    const base = JSON.parse(readFileSync(join(packageRoot, "../../tsconfig.base.json"), "utf8")) as {
      compilerOptions: { types: string[]; lib: string[] };
    };
    expect(base.compilerOptions.types).toEqual([]);
    expect(base.compilerOptions.lib).toEqual(["ES2022"]);
  });

  it("uses the shared `pure` ESLint config, so the lint layer applies too", () => {
    const config = readFileSync(join(packageRoot, "eslint.config.mjs"), "utf8");
    expect(config).toContain("pure");
    expect(config).toContain("../../eslint.config.mjs");
  });
});
