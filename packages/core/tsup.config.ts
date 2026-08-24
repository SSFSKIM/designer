import { defineConfig } from "tsup";

// X7 — publish surface.
//   * `noExternal` bundles the internal @vitrea/* packages into this artifact,
//     so the published package has zero runtime dependencies.
//   * `splitting` keeps the dynamically imported renderer in its own chunk, so
//     a CSS-tier consumer never downloads WGSL.
//   * `dts.resolve` inlines the internal packages' types, so the emitted .d.ts
//     never points at a package that was not published.
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
  dts: { resolve: [/^@vitrea\//], compilerOptions: { ignoreDeprecations: "6.0" } },
  noExternal: [/^@vitrea\//],
});
