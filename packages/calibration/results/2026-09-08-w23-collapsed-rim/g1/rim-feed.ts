/**
 * W23 G1 (f) — the rim law's INPUT, verified on the page rather than assumed
 * (W23 Decision Log 2 (f); G0's gap 5).
 *
 * The shader's rim amplitude is `rimAlpha + rimLevelGain × luminance(material)`, and it takes that
 * level exactly as the tint shade does: the material's own composite where the layer covers the
 * pixel, and the group's MEASURED BACKDROP TONE (`toneColour.w`) where it does not. G0 saw that
 * feed read 0 on some groups and could not tell whether it was absent or genuinely dark, so this
 * reads the published tone per group for every scene of a bed and says which groups carry one.
 *
 * `scene.ts` has published the handed tone in its report since W22 G3, so this captures nothing,
 * opens no fixture and spends no holdout read: every number here is a page-side fact.
 *
 * Usage (from `packages/calibration`):
 *
 *     npx tsx results/2026-09-08-w23-collapsed-rim/g1/rim-feed.ts \
 *       --scale 1 --color-scheme light \
 *       --material-profile profiles/apple-macos-26.5-1x-light-standard.json
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
  readonly scale: number;
  readonly colorScheme: "light" | "dark";
  readonly profile: string | undefined;
  readonly scenes: string;
}

function parse(argv: readonly string[]): Args {
  let scale = 1;
  let colorScheme: "light" | "dark" = "light";
  let profile: string | undefined;
  let scenes = resolve(PACKAGE_ROOT, "../../apps/reference-apple/scenes.json");
  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i + 1] as string;
    switch (argv[i]) {
      case "--scale": scale = Number(value); i += 1; break;
      case "--color-scheme": colorScheme = value as "light" | "dark"; i += 1; break;
      case "--material-profile": profile = resolve(PACKAGE_ROOT, value); i += 1; break;
      case "--scenes": scenes = resolve(PACKAGE_ROOT, value); i += 1; break;
      default: break;
    }
  }
  return { scale, colorScheme, profile, scenes };
}

interface SceneRow {
  readonly id: string;
  readonly set?: string;
  readonly background: string;
  readonly tint?: string;
}

async function main(): Promise<void> {
  const args = parse(process.argv.slice(2));
  const doc = JSON.parse(readFileSync(args.scenes, "utf8")) as { scenes: readonly SceneRow[] };
  // Every scene the bed declares, in the file's own order; the tone is a property
  // of the group and does not depend on which set a scene belongs to, so the
  // holdout scenes are READ here without any fixture being opened.
  const scenes = doc.scenes;
  let server: ViteDevServer | undefined;
  let browser: Awaited<ReturnType<typeof chromium.launch>> | undefined;
  const rows: unknown[] = [];
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
      const profileDoc = JSON.parse(readFileSync(args.profile, "utf8")) as {
        patch?: unknown;
        cssTierMapping?: unknown;
      };
      await context.addInitScript(
        (sections: { patch?: unknown; cssTierMapping?: unknown }) => {
          const w = window as unknown as Record<string, unknown>;
          if (sections.patch !== undefined) w["__vitreaMaterialProfile"] = sections.patch;
          if (sections.cssTierMapping !== undefined) {
            w["__vitreaCssTierMapping"] = sections.cssTierMapping;
          }
        },
        { patch: profileDoc.patch, cssTierMapping: profileDoc.cssTierMapping },
      );
    }
    const page = await context.newPage();
    for (const scene of scenes) {
      const query = new URLSearchParams({
        scene: scene.id,
        renderer: "webgpu",
        scale: `${args.scale}`,
        frames: "3",
      });
      await page.goto(`${baseUrl}/index.html?${query.toString()}`);
      await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", {
        state: "attached",
      });
      const observed = (await page.evaluate(`(function () {
        var report = window.__vitreaCalibration && window.__vitreaCalibration.report;
        if (!report) return null;
        return report.groups.map(function (group) {
          return {
            id: group.id,
            renderer: group.renderer,
            sampling: group.sampling,
            backdropTone: group.backdropTone,
          };
        });
      })()`)) as unknown;
      rows.push({ scene: scene.id, set: scene.set ?? null, background: scene.background,
        tint: scene.tint ?? null, groups: observed });
    }
    await page.close();
  } finally {
    await browser?.close();
    await server?.close();
  }
  process.stdout.write(`${JSON.stringify({ args, rows }, undefined, 2)}\n`);
}

await main();
