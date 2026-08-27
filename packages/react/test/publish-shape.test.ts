/**
 * X7 — proof that `vitrea-react`'s published artifact has the shape the spec
 * promises: internals bundled in, zero runtime dependencies beyond `vitrea`
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

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(packageRoot, "dist");
const entryPath = join(distDir, "index.js");
const typesPath = join(distDir, "index.d.ts");

/**
 * Typecheck one declaration file with no DOM lib, no `types` and `skipLibCheck`
 * off — the consumer whose `lib.dom.d.ts` has no WebGPU in it, which is every
 * TypeScript before 6.0, and the only configuration available in this workspace
 * where an undeclared `GPU` name in the artifact is visible.
 *
 * The config lands in the package root because resolving `react` and
 * `@vitreajs/vitrea` out of the declaration file has to start there. That pulls
 * vitrea's own `dist/index.d.ts` into the program as well, so this check covers
 * the pair the way a consumer installs it.
 */
const typecheckDeclarations = (fileName: string, configName: string) => {
  const configPath = join(packageRoot, configName);
  writeFileSync(
    configPath,
    JSON.stringify({
      compilerOptions: {
        target: "ES2022",
        module: "ESNext",
        moduleResolution: "bundler",
        lib: ["ES2022"],
        types: [],
        strict: true,
        skipLibCheck: false,
        noEmit: true,
      },
      files: [`dist/${fileName}`],
    }),
  );
  try {
    const result = spawnSync(
      process.execPath,
      [join(packageRoot, "node_modules", "typescript/bin/tsc"), "-p", configName],
      { cwd: packageRoot, encoding: "utf8" },
    );
    return (result.stdout ?? "") + (result.stderr ?? "");
  } finally {
    rmSync(configPath, { force: true });
  }
};

/** `Cannot find name 'GPUDevice'`, `Cannot find name 'GPUPowerPreference'`. */
const UNRESOLVED_GPU_NAME = /Cannot find name 'GPU\w+'/g;

/** The banner is one blank-line free block, so the first blank line is its end. */
const splitAmbient = (declarations: string) => {
  const end = declarations.indexOf("\n\n");
  return { ambient: declarations.slice(0, end), rest: declarations.slice(end + 2) };
};

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

  it("depends on nothing but @vitreajs/vitrea and the React peer at runtime", () => {
    expect(specifiersIn(runtime).sort()).toEqual([
      "@vitreajs/vitrea",
      "react",
      "react-dom",
      "react/jsx-runtime",
    ]);
  });

  /*
   * `react-dom` by name, and no require shim — two halves of one assertion.
   *
   * The specifier set above passed while `react-dom` was being *inlined*, because
   * inlined code has no specifier to list: a peer that is missing from the
   * externals looks identical to a peer that was never imported. What the bundled
   * copy does have is esbuild's `__require` shim around its CJS entry, and that
   * shim throws `Dynamic require of "react" is not supported` on the first
   * native-ESM import of the artifact — a publish blocker no other check sees.
   */
  it("imports react-dom rather than inlining a renderer", () => {
    expect(specifiersIn(runtime)).toContain("react-dom");
    expect(runtime).not.toContain("Dynamic require");
  });

  it("bundles the internal packages instead of importing them", () => {
    expect(runtime).not.toMatch(/["']@vitrea\/(platform-web|geometry|motion)["']/);
    expect(runtime).toContain("data-vitrea-node"); // from @vitrea/platform-web
  });

  it("emits declarations that resolve — nothing points at an unpublished file", () => {
    const relative = specifiersIn(types).filter((specifier) => specifier.startsWith("."));
    expect(relative).toEqual([]);
    expect(specifiersIn(types).sort()).toEqual(["@vitreajs/vitrea", "react"]);
  });

  /*
   * One dependency, and the types come with it. The emitted declarations name
   * `GPUDevice` and `GPUPowerPreference`, which this workspace resolves out of
   * `lib.dom.d.ts` and the tarball resolved out of nothing — four of the 29
   * `TS2304`s a cold consumer on TypeScript 5 read out of `node_modules` with
   * `skipLibCheck: false`. They are declared inside the artifact rather than
   * pulled from `@webgpu/types`, so the dependency set did not grow, and a
   * `reference types` directive reappearing here would mean it effectively had.
   */
  it("declares exactly one dependency, and no type dependency either", () => {
    const manifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8")) as {
      dependencies?: Record<string, string>;
    };
    expect(manifest.dependencies ?? {}).toEqual({ "@vitreajs/vitrea": "workspace:^" });
    expect(types).not.toContain("reference types");
  });

  it("declares the WebGPU globals its own declarations use, and only types", () => {
    const { ambient } = splitAmbient(types);

    // Empty and global, so it merges with the consumer's real WebGPU types
    // wherever they have them — TypeScript 6's DOM lib, or their `@webgpu/types`.
    expect(ambient).toBe(
      'declare global {\n  interface GPUDevice {}\n}\ntype GPUPowerPreference = "low-power" | "high-performance";',
    );
    // Types only: a value here would undo "nothing but vitrea and the peer".
    expect(ambient).not.toMatch(/\bdeclare (const|var|let|function|class)\b/);
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

/**
 * The consumer's typecheck, run from in here.
 *
 * Names from the rest of the DOM (`ImageBitmap`, `OffscreenCanvas`) are expected
 * to be unresolved with no DOM lib and are not this test's business — every
 * TypeScript's DOM lib has those. WebGPU is the half that only TypeScript 6's
 * has, which is why the artifact has to carry it.
 */
describe.skipIf(!existsSync(entryPath))("published declarations resolve alone (X7)", () => {
  it("names no WebGPU global the artifact does not declare", () => {
    const output = typecheckDeclarations("index.d.ts", "tsconfig.published-dts.json");

    expect(output).not.toMatch(/error TS5\d{3}/); // the config itself was accepted
    expect(output.match(UNRESOLVED_GPU_NAME)).toBe(null);
  }, 120_000);

  /*
   * Teeth. Without this the check above passes for a build that emits nothing at
   * all. Stripping this package's banner leaves `GPUPowerPreference` unresolved
   * and not `GPUDevice` — vitrea's own banner declares that one globally, and its
   * declarations are in the program either way.
   */
  it("would notice: strip the ambient block and the check goes red", () => {
    const stripped = "stripped.d.ts";
    const strippedPath = join(distDir, stripped);
    writeFileSync(strippedPath, splitAmbient(readFileSync(typesPath, "utf8")).rest);

    try {
      const output = typecheckDeclarations(stripped, "tsconfig.stripped-dts.json");
      expect(output).toContain("Cannot find name 'GPUPowerPreference'");
    } finally {
      rmSync(strippedPath, { force: true });
    }
  }, 120_000);
});
