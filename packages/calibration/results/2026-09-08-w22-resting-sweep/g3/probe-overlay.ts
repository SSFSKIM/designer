/**
 * W22 G3 — the live read on the stacked scene: what the overlay group is actually handed.
 *
 * G0 measured the miss from the outside (claims §5.94 §5: the overlay draws what the shipped dark
 * law gives at a backdrop of linear 0.1344, where the base pane's own rendered output is 0.0470)
 * and named one untested candidate for it — the overlay's `css-backdrop` proxy sampling past the
 * base pane through the padding. This script settles it from the inside, off the running page:
 *
 * - the group's resolved `GlassGroupState` (renderer, sampling backend), so the read is about the
 *   configuration that actually drew;
 * - the group's **measured backdrop tone**, published by `scene.ts`'s report since this gate — the
 *   response law's own input, which is the quantity G0 could only invert for;
 * - the group's **proxy box** and its members' rects, read off the live DOM, against the base
 *   pane's rect: the candidate is a geometric claim and this is the geometry;
 * - the `unsampledMaterial` layer pair the GPU tier composited the overlay at.
 *
 * It captures nothing and writes no PNG, so it spends no holdout read: the pixels are never opened
 * and no native fixture is touched. Everything it prints is a page-side fact.
 *
 * Usage (from `packages/calibration`):
 *
 *     npx tsx results/2026-09-08-w22-resting-sweep/g3/probe-overlay.ts \
 *       --scene checkerboard__glass-over-glass__rest --scale 1 --color-scheme dark \
 *       --material-profile profiles/apple-macos-26.5-1x-dark-standard.json
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";
import { createServer, type ViteDevServer } from "vite";

const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];
const HERE = fileURLToPath(new URL(".", import.meta.url));
const PACKAGE_ROOT = resolve(HERE, "../../..");
const VITE_CONFIG = resolve(PACKAGE_ROOT, "web/vite.config.ts");

interface Args {
  scene: string;
  scale: number;
  colorScheme: "light" | "dark";
  renderer: "webgpu" | "css";
  profile: string | undefined;
}

function parse(argv: readonly string[]): Args {
  const args: Args = {
    scene: "checkerboard__glass-over-glass__rest",
    scale: 1,
    colorScheme: "dark",
    renderer: "webgpu",
    profile: undefined,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i + 1];
    switch (argv[i]) {
      case "--scene": args.scene = value as string; i += 1; break;
      case "--scale": args.scale = Number(value); i += 1; break;
      case "--color-scheme": args.colorScheme = value as "light" | "dark"; i += 1; break;
      case "--renderer": args.renderer = value as "webgpu" | "css"; i += 1; break;
      case "--material-profile": args.profile = resolve(PACKAGE_ROOT, value as string); i += 1; break;
      default: break;
    }
  }
  return args;
}

async function main(): Promise<void> {
  const args = parse(process.argv.slice(2));
  let server: ViteDevServer | undefined;
  let browser: Awaited<ReturnType<typeof chromium.launch>> | undefined;
  try {
    server = await createServer({ configFile: VITE_CONFIG });
    await server.listen();
    const baseUrl = (server.resolvedUrls?.local[0] ?? "").replace(/\/$/, "");
    browser = await chromium.launch({ channel: "chromium", args: GPU_ARGS });
    const context = await browser.newContext({
      viewport: { width: 320, height: 200 },
      deviceScaleFactor: args.scale,
      colorScheme: args.colorScheme,
    });
    if (args.profile !== undefined) {
      const doc = JSON.parse(readFileSync(args.profile, "utf8")) as {
        patch?: unknown;
        cssTierMapping?: unknown;
      };
      await context.addInitScript(
        (sections: { patch?: unknown; cssTierMapping?: unknown }) => {
          const w = window as unknown as Record<string, unknown>;
          if (sections.patch !== undefined) w["__vitreaMaterialProfile"] = sections.patch;
          if (sections.cssTierMapping !== undefined) w["__vitreaCssTierMapping"] = sections.cssTierMapping;
        },
        { patch: doc.patch, cssTierMapping: doc.cssTierMapping },
      );
    }

    const page = await context.newPage();
    const query = new URLSearchParams({
      scene: args.scene,
      renderer: args.renderer,
      scale: `${args.scale}`,
      frames: "3",
    });
    await page.goto(`${baseUrl}/index.html?${query.toString()}`);
    await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", {
      state: "attached",
    });

    // Evaluated as a source string rather than as a closure: `tsx` compiles this
    // file with esbuild, which injects a `__name` helper into every arrow it
    // lowers, and that helper does not exist in the page's realm.
    const observed = (await page.evaluate(`(function () {
      var report = window.__vitreaCalibration.report;
      function rectOf(element) {
        if (element === null) return null;
        var box = element.getBoundingClientRect();
        return { x: box.x, y: box.y, width: box.width, height: box.height };
      }
      var proxies = Array.prototype.map.call(
        document.querySelectorAll("[data-vitrea-proxy]"),
        function (element) {
          return {
            groupId: element.getAttribute("data-vitrea-proxy"),
            plane: element.getAttribute("data-vitrea-proxy-plane"),
            box: rectOf(element),
            clipPath: element.style.clipPath,
            backdropFilter: element.style.backdropFilter,
          };
        },
      );
      var hosts = Array.prototype.map.call(
        document.querySelectorAll(".glass-host"),
        function (element, index) {
          return { index: index, box: rectOf(element) };
        },
      );
      return { groups: report.groups, surfaces: report.surfaces, proxies: proxies, hosts: hosts };
    })()`)) as unknown;

    process.stdout.write(`${JSON.stringify({ args: args, observed: observed }, undefined, 2)}\n`);
    await page.close();
  } finally {
    await browser?.close();
    await server?.close();
  }
}

await main();
