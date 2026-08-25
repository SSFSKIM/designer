import { cp, mkdir } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vite";

/**
 * Aliased to **source**, not to each package's `dist`, for the same reason
 * platform-web's e2e server is: a site that silently runs a stale build is worse
 * than no site, and this way `pnpm dev` needs no build step. The published
 * artifact is asserted separately, on `dist`, by
 * `packages/react/test/publish-shape.test.ts`.
 */
const packages = fileURLToPath(new URL("../../packages/", import.meta.url));
const here = fileURLToPath(new URL(".", import.meta.url));

/** The committed native ground truth. Machine-specific, and therefore not derived. */
const fixtures = resolve(here, "../reference-apple/fixtures");

const MIME: Record<string, string> = {
  ".png": "image/png",
  ".json": "application/json",
};

/**
 * The native captures, served in dev and copied at build.
 *
 * `apps/reference-apple/fixtures/` is outside this app's root and is not a
 * `public/` directory: it is committed ground truth that belongs to the capture
 * harness, and copying it into the app's source tree would give the repo two
 * copies of a file whose whole value is being the one the harness produced. So the
 * dev server maps `/fixtures/*` onto it and the build copies the two directories
 * the site actually references. The result is a `dist/` that needs nothing but a
 * static file server.
 */
function nativeFixtures(): Plugin {
  return {
    name: "vitrea-native-fixtures",
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const url = request.url ?? "";
        const path = url.split("?")[0] ?? "";
        if (!path.startsWith("/fixtures/")) return next();
        // Normalised and re-rooted, so a `..` in the request cannot escape.
        const relative = normalize(decodeURIComponent(path.slice("/fixtures/".length)));
        if (relative.startsWith("..")) {
          response.statusCode = 403;
          response.end("Forbidden");
          return;
        }
        const file = join(fixtures, relative);
        response.setHeader("Content-Type", MIME[extname(file)] ?? "application/octet-stream");
        createReadStream(file)
          .on("error", () => {
            response.statusCode = 404;
            response.end("Not found");
          })
          .pipe(response);
      });
    },
    async closeBundle() {
      const out = resolve(here, "dist/fixtures");
      await mkdir(out, { recursive: true });
      for (const directory of ["backgrounds", "apple-macos-26.5-1x-light-standard"]) {
        await cp(join(fixtures, directory), join(out, directory), { recursive: true });
      }
    },
  };
}

export default defineConfig({
  /*
   * Relative, so `dist/` is servable from any path: a GitHub Pages project site
   * lives under `/<repo>/`, a user site under `/`, and a preview under neither.
   * Absolute asset URLs would pick one of those and break the other two.
   */
  base: "./",
  plugins: [react(), nativeFixtures()],
  resolve: {
    alias: {
      "@vitrea/core": `${packages}core/src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/platform-web": `${packages}platform-web/src/index.ts`,
      "@vitrea/react": `${packages}react/src/index.ts`,
      // The renderer too, and it was worth the trouble to notice: it reaches the
      // app through core's lazy dynamic import, so without an alias `pnpm dev`
      // silently ran whatever was last built into `dist/`. Aliasing it does not
      // weaken X7 — the import is still dynamic, so the renderer is still a chunk
      // of its own that a CSS-tier session never fetches.
      "@vitrea/renderer-webgpu": `${packages}renderer-webgpu/src/index.ts`,
    },
  },
  build: {
    rollupOptions: {
      input: {
        index: resolve(here, "index.html"),
        playground: resolve(here, "playground/index.html"),
      },
    },
  },
  server: { port: 5173 },
});
