import { defineConfig } from "tsup";

// X7 — publish surface. @vitrea/core is a real dependency of this package, so it
// stays external; the private internals are bundled in.
const BUNDLED_INTERNALS = /^@vitrea\/(platform-web|geometry|motion)$/;

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm"],
  target: "es2022",
  outDir: "dist",
  clean: true,
  splitting: true,
  treeshake: true,
  sourcemap: true,
  // `dts.resolve: true` rather than a package-name list, and the difference is
  // load-bearing. A list matches the *specifier* `@vitrea/platform-web`, but that
  // package's own `.d.ts` re-exports through `export *` from a dozen sibling
  // modules — so rollup-plugin-dts leaves those siblings external and emits
  // `import { GlassHostHandle } from "./backdrop-proxy"` into `dist/index.d.ts`,
  // pointing at a file that was never published. Resolving everything inlines the
  // whole chain; `@vitrea/core` and `react` stay external because tsup externalises
  // declared dependencies and peers regardless of this flag.
  // `test/publish-shape.test.ts` asserts the emitted `.d.ts` on the built artifact.
  //
  // `ignoreDeprecations` is scoped to the declaration pass because tsup injects
  // the deprecated `baseUrl` there. Drop it when tsup stops doing that.
  dts: { resolve: true, compilerOptions: { ignoreDeprecations: "6.0" } },
  noExternal: [BUNDLED_INTERNALS],
});
