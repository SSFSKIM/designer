import { defineConfig } from "tsup";

/**
 * The WebGPU names the emitted declarations use, declared inside the artifact.
 *
 * Decision Log #23(e) keeps the WebGPU type gap covered *in this workspace*:
 * the renderer compiles with `lib: ["DOM"]`, and TypeScript 6's `lib.dom.d.ts`
 * ships the WebGPU interfaces. Neither fact travels in a tarball. `dts.resolve`
 * inlines the renderer's types into `dist/index.d.ts`, which then names
 * `GPUDevice`, `GPUTextureView` and eleven more that nothing in the published
 * package declares — 29 `TS2304`s out of `node_modules` for a consumer on
 * TypeScript 5, whose DOM lib has no WebGPU at all, with `skipLibCheck: false`.
 *
 * The interfaces are declared empty and global on purpose. An empty interface
 * *merges* with a fuller declaration of the same name, so this block is inert
 * wherever the consumer already has WebGPU types — TypeScript 6's DOM lib, or
 * their own `@webgpu/types` — and there each name keeps its real members: a
 * `GPUDevice` handed out by vitrea is the same `GPUDevice` the consumer's own
 * WebGPU calls accept. Depending on `@webgpu/types` and referencing it from here
 * would not have that property. That package redeclares what TypeScript 6's DOM
 * lib already declares, so the reference puts 48 conflict errors (`TS6200`,
 * `TS2717`, `TS2403`) in front of every consumer on a current TypeScript, and it
 * needs the DOM lib itself to resolve `EventTarget` and `DOMException`.
 *
 * `GPUTextureFormat` cannot join the merge: a *type alias* has no merge rule, and
 * a second declaration is `TS2300 Duplicate identifier`. So it is declared
 * module-locally, where it shadows the global for this one file and collides with
 * nothing. It reaches the published surface in input positions only — the format
 * of the caller's canvas target views — so the open `string` arm keeps every
 * caller assignable while the three formats a WebGPU canvas can actually be
 * configured with stay in autocomplete.
 *
 * `test/bundle-shape.test.ts` compiles the built `dist/index.d.ts` with no DOM
 * lib and no `types`, and fails if any `GPU` name is unresolved.
 */
const WEBGPU_AMBIENT = `declare global {
  interface GPUBuffer {}
  interface GPUCommandEncoder {}
  interface GPUComputePassTimestampWrites {}
  interface GPUDevice {}
  interface GPUExternalTexture {}
  interface GPUExternalTextureDescriptor {}
  interface GPUQueue {}
  interface GPURenderPassTimestampWrites {}
  interface GPUSupportedLimits {}
  interface GPUTexture {}
  interface GPUTextureDescriptor {}
  interface GPUTextureView {}
}
type GPUTextureFormat = "bgra8unorm" | "rgba8unorm" | "rgba16float" | (string & {});
`;

// X7 — publish surface.
//   * `noExternal` bundles the internal @vitrea/* packages into this artifact,
//     so the published package has zero runtime dependencies.
//   * `splitting` keeps the dynamically imported renderer in its own chunk, so
//     a CSS-tier consumer never downloads WGSL.
//   * `dts.resolve` inlines the internal packages' types, so the emitted .d.ts
//     never points at a package that was not published.
//   * `dts.banner` makes those inlined types resolvable on any TypeScript, with
//     nothing installed and no `types` entry configured — see WEBGPU_AMBIENT.
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
