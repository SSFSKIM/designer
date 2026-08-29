/**
 * X7 — proof that the published artifact has the shape the spec promises:
 * internals bundled in, WGSL only in a lazy chunk, no dependency on a package
 * that was never published, and declarations that resolve with nothing installed.
 *
 * Reads `dist/`, so it needs `pnpm build` to have run (CI builds first).
 */

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(packageRoot, "dist");
const entryPath = join(distDir, "index.js");
const typesPath = join(distDir, "index.d.ts");

const WGSL_MARKER = "vitrea:wgsl-marker";

/**
 * The WebGPU interfaces `tsup.config.ts` banners onto `dist/index.d.ts`, declared
 * empty and global so they merge with whatever the consumer already has. The list
 * is exact: this test fails if one is dropped, and the typecheck below fails if
 * the emitted surface starts naming one that is missing.
 */
const AMBIENT_GPU_INTERFACES = [
  "GPUBuffer",
  "GPUCommandEncoder",
  "GPUComputePassTimestampWrites",
  "GPUDevice",
  "GPUExternalTexture",
  "GPUExternalTextureDescriptor",
  "GPUQueue",
  "GPURenderPassTimestampWrites",
  "GPUSupportedLimits",
  "GPUTexture",
  "GPUTextureDescriptor",
  "GPUTextureView",
] as const;

/**
 * Typecheck one declaration file the way nothing in this workspace does: no DOM
 * lib, no `types`, `skipLibCheck` off. That is the consumer whose `lib.dom.d.ts`
 * has no WebGPU in it — every TypeScript before 6.0 — and the only configuration
 * in which an undeclared `GPU` name in the artifact is visible from in here.
 *
 * The config file lands in the package root because module resolution for the
 * declaration file's own imports has to start there.
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

/** `Cannot find name 'GPUDevice'` and its thirteen siblings. */
const UNRESOLVED_GPU_NAME = /Cannot find name 'GPU\w+'/g;

/**
 * The banner and the declarations it sits on top of. The banner is one blank-line
 * free block, so the first blank line is its end.
 */
const splitAmbient = (declarations: string) => {
  const end = declarations.indexOf("\n\n");
  return { ambient: declarations.slice(0, end), rest: declarations.slice(end + 2) };
};

/** Matches a real module specifier, so prose mentioning `@vitrea/x` never trips the test. */
const IMPORTS_INTERNAL_PACKAGE = /(?:\bfrom|\bimport\(|\bimport)\s*["']@vitrea\//;

describe.skipIf(!existsSync(entryPath))("built artifact shape (X7)", () => {
  const chunks = readdirSync(distDir).filter((name) => name.endsWith(".js") && name !== "index.js");

  // The entry's static import closure: the entry plus every chunk it imports
  // eagerly (tsup may extract shared code into sibling chunks once another
  // workspace package also depends on geometry/motion). Dynamic imports stay
  // excluded — that is what keeps the WGSL chunk lazy.
  const staticClosure = (() => {
    const seen = new Set<string>();
    const queue = ["index.js"];
    const STATIC_IMPORT = /(?:^|[^(\w.])import\s*(?:[\w$*{},\s]+from\s*)?["'](\.\/[^"']+)["']|\bfrom\s*["'](\.\/[^"']+)["']/g;
    while (queue.length > 0) {
      const name = queue.pop() as string;
      if (seen.has(name)) continue;
      seen.add(name);
      const source = readFileSync(join(distDir, name), "utf8");
      for (const match of source.matchAll(STATIC_IMPORT)) {
        const spec = (match[1] ?? match[2]) as string;
        queue.push(spec.replace(/^\.\//, ""));
      }
    }
    return [...seen].map((name) => readFileSync(join(distDir, name), "utf8")).join("\n");
  })();

  it("bundles the internal packages instead of importing them", () => {
    expect(IMPORTS_INTERNAL_PACKAGE.test(staticClosure)).toBe(false);
    expect(staticClosure).toContain("concentric-rounded-rect"); // from @vitrea/geometry
    expect(staticClosure).toContain("interruptible-spring"); // from @vitrea/motion
  });

  it("keeps WGSL out of the entry chunk and inside a lazy chunk", () => {
    expect(staticClosure).not.toContain(WGSL_MARKER);

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

  it("publishes the whole core runtime surface, not just its types", () => {
    const declarations = readFileSync(join(distDir, "index.d.ts"), "utf8");

    for (const name of [
      "resolveGlassGroupState",
      "DEMOTION_RECOVERY",
      "resolveBackdropHint",
      "resolveForegroundAdaptation",
      "resolveMaterial",
      "resolveAccessibilityPolicy",
      "createGlassScene",
      "createFrameScheduler",
      "createDiagnosticsChannel",
    ]) {
      expect(declarations).toContain(name);
    }
  });

  /*
   * Zero dependencies is the X7 claim, and after v0.1.0 it is also a *type*
   * claim. The emitted declarations name fourteen WebGPU globals that this
   * workspace resolves out of `lib.dom.d.ts` and the tarball resolves out of
   * nothing (29 `TS2304`s for a cold consumer on TypeScript 5 with
   * `skipLibCheck: false`). The fix declares them inside the artifact rather than
   * depending on `@webgpu/types` and referencing it — so the empty dependency set
   * covers the types too, and a `reference types` directive reappearing here
   * would mean the artifact had quietly started requiring an install again.
   */
  it("declares no runtime dependencies, and no type dependency either", () => {
    const manifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8")) as {
      dependencies?: Record<string, string>;
    };
    expect(manifest.dependencies ?? {}).toEqual({});

    const declarations = readFileSync(typesPath, "utf8");
    expect(declarations).not.toContain("reference types");
  });

  it("declares the WebGPU globals its own declarations use, and only types", () => {
    const { ambient } = splitAmbient(readFileSync(typesPath, "utf8"));

    expect(ambient.startsWith("declare global {\n")).toBe(true);
    for (const name of AMBIENT_GPU_INTERFACES) {
      expect(ambient).toContain(`  interface ${name} {}\n`);
    }
    // A type alias cannot merge with the DOM lib's declaration of the same name,
    // so this one is module-local rather than global. See tsup.config.ts.
    expect(ambient).toContain("\ntype GPUTextureFormat = ");

    // Types only: the block must never introduce a value, or "no runtime
    // dependencies" would be resting on a global the artifact declares.
    expect(ambient).not.toMatch(/\bdeclare (const|var|let|function|class)\b/);
  });
});

/**
 * The consumer's typecheck, run from in here.
 *
 * `lib: ["ES2022"]` with no `types` is the one configuration available in this
 * workspace that reproduces a pre-6.0 TypeScript: no WebGPU anywhere but the
 * artifact itself. Names from the rest of the DOM (`ImageBitmap`,
 * `HTMLCanvasElement`, `VideoFrame`) are expected to be unresolved there and are
 * not this test's business — every TypeScript's DOM lib has those.
 */
describe.skipIf(!existsSync(entryPath))("published declarations resolve alone (X7)", () => {
  it("names no WebGPU global the artifact does not declare", () => {
    const output = typecheckDeclarations("index.d.ts", "tsconfig.published-dts.json");

    expect(output).not.toMatch(/error TS5\d{3}/); // the config itself was accepted
    expect(output.match(UNRESOLVED_GPU_NAME)).toBe(null);
  }, 120_000);

  it("would notice: strip the ambient block and the check goes red", () => {
    const stripped = "stripped.d.ts";
    const strippedPath = join(distDir, stripped);
    writeFileSync(strippedPath, splitAmbient(readFileSync(typesPath, "utf8")).rest);

    try {
      const output = typecheckDeclarations(stripped, "tsconfig.stripped-dts.json");
      expect(output.match(UNRESOLVED_GPU_NAME)?.length ?? 0).toBeGreaterThan(0);
    } finally {
      rmSync(strippedPath, { force: true });
    }
  }, 120_000);
});

/**
 * Three published packages, and the set is closed on purpose.
 *
 * It was two until the post-v1 API round published the browser host in its own
 * right (Decision Log #30(c)): before that, `vitrea` alone could not mount a
 * root and the host reached npm only inlined inside `vitrea-react`, so a
 * vanilla-JS, Vue or Svelte consumer had no entry at all. The layering is
 * React's own — a pure runtime, a DOM host over it, framework bindings over
 * that — and each artifact externalises the one below it, so a page that mounts
 * roots through two of them still gets one copy of each.
 *
 * The remaining `@vitrea/*` packages stay private and bundled. This assertion
 * is the guard on that: a package that quietly loses `"private": true` starts
 * being published on the next release, and nothing else would notice.
 */
describe("publish surface (X7)", () => {
  it("leaves exactly the three @vitreajs packages publishable", () => {
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

    expect(publishable).toEqual([
      "@vitreajs/vitrea",
      "@vitreajs/vitrea-react",
      "@vitreajs/vitrea-web",
    ]);
  });
});
