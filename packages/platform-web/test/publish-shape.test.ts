/**
 * X7 — proof that the framework-agnostic host's published artifact has the
 * shape the spec promises: one runtime dependency (`@vitreajs/vitrea`), the
 * still-private internals bundled in, and declarations that resolve on their
 * own, on any TypeScript, with nothing installed.
 *
 * This package became publishable in the post-v1 API round (Decision Log
 * #30(c)): until then the browser host reached npm only inlined inside
 * `@vitreajs/vitrea-react`, so `vitrea` alone could not mount a root and a
 * vanilla-JS or Vue or Svelte consumer had no entry at all.
 *
 * The declaration check is not decoration. rollup-plugin-dts leaves a
 * re-exported name external when the package it came from re-exports through
 * `export *` from several sibling modules, and it then emits
 * `import { GlassHostHandle } from "./backdrop-proxy"` into an artifact where no
 * such file exists — this package's own `src/index.ts` is exactly that shape,
 * twenty `export *`s deep. The runtime bundle is perfectly correct while the
 * types are unusable, so nothing but a declaration-side assertion catches it.
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
 * The config lands in the package root because resolving `@vitreajs/vitrea` out
 * of the declaration file has to start there. That pulls vitrea's own
 * `dist/index.d.ts` into the program as well, so this check covers the pair the
 * way a consumer installs it.
 */
const typecheckDeclarations = (fileName: string, configName: string): string => {
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

/** `Cannot find name 'GPUDevice'`, `Cannot find name 'GPUTextureFormat'`. */
const UNRESOLVED_GPU_NAME = /Cannot find name 'GPU\w+'/g;

/** The banner is one blank-line free block, so the first blank line is its end. */
const splitAmbient = (declarations: string): { ambient: string; rest: string } => {
  const end = declarations.indexOf("\n\n");
  return { ambient: declarations.slice(0, end), rest: declarations.slice(end + 2) };
};

/**
 * Every module specifier a file imports or re-exports from.
 *
 * Comments are stripped first: this package's prose quotes module-ish strings,
 * and a doc comment is not a dependency.
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

  it("depends on nothing but @vitreajs/vitrea at runtime", () => {
    expect(specifiersIn(runtime).sort()).toEqual(["@vitreajs/vitrea"]);
  });

  it("bundles the still-private internals instead of importing them", () => {
    expect(runtime).not.toMatch(/["']@vitrea\/(geometry|motion|renderer-webgpu)["']/);
  });

  /*
   * `@vitreajs/vitrea` external, not inlined — and the two halves are different
   * assertions. An inlined copy has no specifier to list, so the set above
   * cannot tell "externalised" from "never imported"; what a second copy of core
   * would bring with it is core's own scene machinery, and a page holding two
   * scenes holds two answers to every capability question.
   */
  it("shares one runtime with its consumers rather than inlining a second", () => {
    expect(specifiersIn(runtime)).toContain("@vitreajs/vitrea");
    expect(runtime).not.toContain("frame-phase-violation"); // core's, and only core's
  });

  it("emits declarations that resolve — nothing points at an unpublished file", () => {
    const relative = specifiersIn(types).filter((specifier) => specifier.startsWith("."));
    expect(relative).toEqual([]);
    expect(specifiersIn(types).sort()).toEqual(["@vitreajs/vitrea"]);
  });

  it("declares exactly one dependency, and no type dependency either", () => {
    const manifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8")) as {
      dependencies?: Record<string, string>;
      private?: boolean;
    };
    expect(manifest.dependencies ?? {}).toEqual({ "@vitreajs/vitrea": "workspace:^" });
    expect(manifest.private ?? false).toBe(false);
    expect(types).not.toContain("reference types");
  });

  it("declares the WebGPU globals its own declarations use, and only types", () => {
    const { ambient } = splitAmbient(types);

    // Empty and global, so it merges with the consumer's real WebGPU types
    // wherever they have them — TypeScript 6's DOM lib, or their `@webgpu/types`.
    expect(ambient).toBe(
      'declare global {\n  interface GPUDevice {}\n}\ntype GPUPowerPreference = "low-power" | "high-performance";',
    );
    // Types only: a value here would undo "nothing but vitrea".
    expect(ambient).not.toMatch(/\bdeclare (const|var|let|function|class)\b/);
  });

  /*
   * The entry a vanilla consumer actually reaches for. `createGlassRoot` was
   * always the one entry point an app needs — it was simply unreachable from
   * npm. These names are the mounting path in `README.md`'s quickstart and in
   * `e2e/fixtures/vanilla.ts`, so a rename that broke either would break here.
   */
  it("exports the vanilla mounting path", () => {
    for (const name of [
      "createGlassRoot",
      "GLASS_PLANES",
      "HOST_ATTRIBUTES",
      "GLASS_CHANNEL_PROPERTIES",
      "consoleDiagnosticSink",
    ]) {
      expect(types).toContain(name);
      expect(runtime).toContain(name);
    }
  });
});

/**
 * The consumer's typecheck, run from in here.
 *
 * Unlike core's and vitrea-react's, *this* artifact's declarations name the DOM
 * on purpose — it is the DOM host, and `HTMLElement` is in half its signatures.
 * So the compile below reports plenty of `Cannot find name 'HTMLElement'`, and
 * those are not this test's business: every TypeScript's DOM lib has them, and a
 * browser consumer configures one. WebGPU is the half that only TypeScript 6's
 * DOM lib has, which is why the artifact has to carry it, and the assertion is
 * therefore scoped to `GPU`-prefixed names rather than to a clean compile.
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
   * and not `GPUDevice` — vitrea's own banner declares that one globally, and
   * its declarations are in the program either way.
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
