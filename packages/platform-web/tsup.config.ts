import { defineConfig } from "tsup";

/**
 * The two WebGPU names *this* artifact's declarations use, declared inside it.
 *
 * The doctrine — and why an empty global interface rather than a dependency on
 * `@webgpu/types` — is written out in `packages/core/tsup.config.ts`. The short
 * version: an empty interface *merges* with a real declaration of the same name,
 * so the block is inert wherever the consumer already has WebGPU types and keeps
 * `GPUDevice` interoperable with their own WebGPU calls; a type *alias* has no
 * merge rule, so `GPUPowerPreference` is module-local, where it shadows the
 * global for this one file. Its two members are the whole spec union, so nothing
 * is widened away.
 *
 * The list is the *emitted surface's*, not the source's. `GPU`,
 * `GPUCanvasContext` and `GPUTextureFormat` are all named inside `webgpu.ts` and
 * none of them reaches a published signature; declaring them here would be dead
 * weight that no check could ever fail on. `test/publish-shape.test.ts` pins the
 * block exactly and compiles the built `dist/index.d.ts` with no `types`, so a
 * surface change that starts naming a third one goes red rather than silent.
 */
const WEBGPU_AMBIENT = `declare global {
  interface GPUDevice {}
}
type GPUPowerPreference = "low-power" | "high-performance";
`;

// X7 — publish surface. This is the framework-agnostic browser host: the third
// published package, and the one `@vitreajs/vitrea-react` is expressed over.
//   * `@vitreajs/vitrea` is a declared dependency, so tsup externalises it and
//     a page that loads both this package and the React bindings gets exactly
//     one copy of the runtime.
//   * `noExternal` bundles the still-internal `@vitrea/*` packages in, so the
//     published package's only runtime dependency is `@vitreajs/vitrea`.
//   * `dts.resolve` inlines their types. Without it rollup-plugin-dts leaves
//     `@vitrea/geometry` external and emits an import of a package that was
//     never published — the same trap `packages/react/tsup.config.ts` documents.
//   * `splitting` keeps the CSS-tier path from dragging anything it does not use.
export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm"],
  target: "es2022",
  outDir: "dist",
  clean: true,
  splitting: true,
  treeshake: true,
  sourcemap: true,
  // `ignoreDeprecations` is scoped to the declaration pass because tsup injects
  // the deprecated `baseUrl` there. Drop it when tsup stops doing that.
  dts: {
    resolve: true,
    banner: WEBGPU_AMBIENT,
    compilerOptions: { ignoreDeprecations: "6.0" },
  },
  noExternal: [/^@vitrea\//],
});
