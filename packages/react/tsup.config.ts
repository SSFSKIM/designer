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
  // `ignoreDeprecations` is scoped to the declaration pass because tsup injects
  // the deprecated `baseUrl` there. Drop it when tsup stops doing that.
  dts: { resolve: [BUNDLED_INTERNALS], compilerOptions: { ignoreDeprecations: "6.0" } },
  noExternal: [BUNDLED_INTERNALS],
});
