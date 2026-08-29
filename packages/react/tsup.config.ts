import { defineConfig } from "tsup";

// X7 — publish surface. `@vitreajs/vitrea` and `@vitreajs/vitrea-web` are real
// dependencies of this package, so tsup leaves them external; the still-private
// internals are bundled in.
//
// The host layer moved out of this artifact when it was published in its own
// right (Decision Log #30(c)). Externalising it is not only a size saving: a
// page that mounts one root through these bindings and another through the
// vanilla entry must get *one* copy of the host, or it gets two ink
// stylesheets, two plane managers and two registries that cannot see each
// other. `test/publish-shape.test.ts` asserts the specifier survives in the
// built artifact.
const BUNDLED_INTERNALS = /^@vitrea\/(geometry|motion)$/;

/**
 * The two WebGPU names *this* artifact's declarations use, declared inside it.
 *
 * The doctrine, and why an empty global interface rather than a dependency on
 * `@webgpu/types`, is written out in `packages/core/tsup.config.ts`. The short
 * version: an empty interface merges with a real declaration of the same name, so
 * the block is inert wherever the consumer already has WebGPU types and keeps
 * `GPUDevice` interoperable with their own WebGPU calls; a type alias cannot
 * merge at all, so `GPUPowerPreference` is module-local, where it shadows the
 * global for this one file. Its two members are the whole spec union, so nothing
 * is widened away.
 *
 * `test/publish-shape.test.ts` compiles the built `dist/index.d.ts` with no DOM
 * lib and no `types`, and fails if any `GPU` name is unresolved.
 */
const WEBGPU_AMBIENT = `declare global {
  interface GPUDevice {}
}
type GPUPowerPreference = "low-power" | "high-performance";
`;

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
  // load-bearing. A list matches the *specifier* `@vitreajs/vitrea-web`, but that
  // package's own `.d.ts` re-exports through `export *` from a dozen sibling
  // modules — so rollup-plugin-dts leaves those siblings external and emits
  // `import { GlassHostHandle } from "./backdrop-proxy"` into `dist/index.d.ts`,
  // pointing at a file that was never published. Resolving everything inlines the
  // whole chain; `vitrea` and `react` stay external because tsup externalises
  // declared dependencies and peers regardless of this flag.
  // `test/publish-shape.test.ts` asserts the emitted `.d.ts` on the built artifact.
  //
  // `ignoreDeprecations` is scoped to the declaration pass because tsup injects
  // the deprecated `baseUrl` there. Drop it when tsup stops doing that.
  dts: {
    resolve: true,
    banner: WEBGPU_AMBIENT,
    compilerOptions: { ignoreDeprecations: "6.0" },
  },
  // Both halves of the React peer, named rather than inferred. `react-dom` is a
  // devDependency as well (the test environment installs it), and a bundled
  // renderer lands in the artifact as CJS behind esbuild's dynamic-require shim —
  // which throws on the first native-ESM import of the package.
  external: ["react", "react-dom"],
  noExternal: [BUNDLED_INTERNALS],
});
