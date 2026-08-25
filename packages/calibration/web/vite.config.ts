import { createReadStream, statSync } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig, type Plugin } from "vite";

/**
 * The calibration scene server — C7's web side.
 *
 * Aliased to **source**, exactly as `platform-web/e2e/vite.config.ts` is, and for
 * the same reason: a calibration cell measured against a stale `dist` would be a
 * number about last week's renderer, published against this week's tier name.
 */
const webRoot = fileURLToPath(new URL(".", import.meta.url));
const packages = fileURLToPath(new URL("../..", import.meta.url));
const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));

/** Where the native harness committed the shared rasters. */
const REFERENCE_FIXTURES = resolve(repoRoot, "apps/reference-apple/fixtures");

/** URL prefix the page fetches backgrounds under. */
export const REFERENCE_MOUNT = "/reference-fixtures";

export const SCENE_SERVER_PORT = 5189;

const CONTENT_TYPES: Record<string, string> = {
  ".png": "image/png",
  ".json": "application/json",
};

/**
 * Serve `apps/reference-apple/fixtures` read-only, in place.
 *
 * The spec's binding rule is that both renderers composite the *identical*
 * pre-rendered raster, so the web side must reach the committed PNG itself. A
 * copy under this package would be a second, silently-diverging description of
 * the one artefact the diff's validity rests on — and Vite's `publicDir` copies
 * on build, which is exactly the wrong semantics for a file another toolchain
 * owns. Hence a read-only mount rather than an asset pipeline.
 */
function referenceFixtures(): Plugin {
  return {
    name: "vitrea-reference-fixtures",
    configureServer(server) {
      server.middlewares.use(REFERENCE_MOUNT, (request, response, next) => {
        const requested = (request.url ?? "/").split("?")[0] ?? "/";
        const relative = normalize(decodeURIComponent(requested)).replace(/^[/\\]+/, "");
        const file = join(REFERENCE_FIXTURES, relative);

        // Containment check before any filesystem work: the mount is a window
        // onto one directory, and `..` must not widen it.
        if (!file.startsWith(REFERENCE_FIXTURES)) {
          response.statusCode = 403;
          response.end("outside the reference fixture mount");
          return;
        }
        if (!statSync(file, { throwIfNoEntry: false })?.isFile()) {
          next();
          return;
        }

        response.setHeader(
          "Content-Type",
          CONTENT_TYPES[extname(file)] ?? "application/octet-stream",
        );
        // No caching: the native harness rewrites these in place when a capture
        // run lands, and a cached raster would silently pin an old background.
        response.setHeader("Cache-Control", "no-store");
        createReadStream(file).pipe(response);
      });
    },
  };
}

export default defineConfig({
  root: webRoot,
  plugins: [referenceFixtures()],
  resolve: {
    alias: {
      "@vitreajs/vitrea": `${packages}core/src/index.ts`,
      "@vitrea/geometry": `${packages}geometry/src/index.ts`,
      "@vitrea/motion": `${packages}motion/src/index.ts`,
      "@vitrea/platform-web": `${packages}platform-web/src/index.ts`,
      "@vitrea/renderer-webgpu": `${packages}renderer-webgpu/src/index.ts`,
    },
  },
  server: {
    port: SCENE_SERVER_PORT,
    strictPort: true,
    // `scenes.json` lives in `apps/reference-apple`, outside this root, and is
    // imported rather than copied for the same reason the rasters are mounted.
    fs: { allow: [repoRoot] },
  },
});
