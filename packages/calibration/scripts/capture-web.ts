/**
 * The web-side capture driver for C7's calibration matrix.
 *
 * Runs the scene page in a real Chromium, captures the measured region at the
 * native fixture's exact pixel size, and writes a PNG plus the X9 "web cell"
 * descriptor that keys the result matrix.
 *
 * A script rather than a Playwright `test`, deliberately. A test reports
 * pass/fail; this reports *what happened* — which tier drew, on which adapter,
 * whether the two captures agreed — and every one of those outcomes is data the
 * matrix needs to record even when it is the disappointing one. A capture run
 * that skipped or failed instead of writing a labelled CSS-tier cell would leave
 * the matrix with a hole where an honest number belongs.
 *
 * Three rules it exists to enforce:
 *
 * 1. **A real adapter, or a labelled fallback.** C6 measured that Playwright's
 *    bundled headless shell hands back a *software* adapter while
 *    `channel: "chromium"` — the full browser binary — hands back the real one,
 *    so the launch recipe below is copied from `playwright.config.ts` unchanged.
 *    Where no hardware adapter answers, the run does not pretend: it re-captures
 *    on the CSS tier and the cell says `renderer: "css"` with `gpuAdapter`
 *    carrying the reason. A GPU-tier claim measured on a CPU rasteriser is worse
 *    than no claim.
 *
 * 2. **Determinism is measured, not assumed.** Every scene is captured twice
 *    from two independent page loads — the stronger claim, since a repeated
 *    screenshot of one loaded page only proves the compositor is idle. Byte
 *    equality is reported as such; anything else is reported as the mean
 *    absolute channel difference, so a noisy cell is visible in the matrix
 *    rather than being averaged into a fidelity number.
 *
 * 3. **The cell describes what drew.** `renderer`, `samplingBackend` and the
 *    adapter string are read off the page's own resolved `GlassGroupState`
 *    (X2's honesty core), never off the URL that asked for them.
 *
 * Each scene writes three files into `web-captures/<sceneId>/`, suffixed by the
 * tier that actually drew: the PNG, `cell__<tier>.json`, and
 * `report__<tier>.json`. The cell is kept to exactly X9's fields so the matrix's
 * key stays a key; the report carries everything explanatory — resolved state
 * per group, the refraction ladder, diagnostics, whether the run fell back, and
 * any condition that would make the capture misleading.
 */

import { mkdir, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium, type Browser, type BrowserContext } from "@playwright/test";
import { PNG } from "pngjs";
import { createServer, type ViteDevServer } from "vite";

// Extension included so the file runs under node's own type stripping as well as
// under `tsx`; the import is type-only, so both erase it entirely.
import type { SceneReport } from "../web/scene.ts";

/** Dawn needs these to reach the real backend. Copied from playwright.config.ts. */
const GPU_ARGS = ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"];

const HERE = fileURLToPath(new URL(".", import.meta.url));
const PACKAGE_ROOT = resolve(HERE, "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "../..");
const VITE_CONFIG = resolve(PACKAGE_ROOT, "web/vite.config.ts");
const SCENES_JSON = resolve(REPO_ROOT, "apps/reference-apple/scenes.json");
const DEFAULT_OUT = resolve(PACKAGE_ROOT, "web-captures");

/**
 * Mirrors `platform-web/e2e/support.ts`, on purpose and by name: measuring the
 * software path is a legitimate thing to do deliberately and an illegitimate
 * thing to do by accident.
 */
const ALLOW_FALLBACK_ADAPTER = process.env.VITREA_ALLOW_FALLBACK_ADAPTER === "1";

const say = (line: string): void => void process.stdout.write(`${line}\n`);

// ---------------------------------------------------------------------------
// The X9 web cell
// ---------------------------------------------------------------------------

/**
 * One cell of X9's result matrix: the web half of the `native profile × web cell`
 * key. Every field is an observation, and the schema is deliberately narrow —
 * anything explanatory lives in the sibling `report.json` so that adding context
 * can never change the shape of a key.
 */
export interface WebCell {
  readonly engine: "chromium";
  readonly engineVersion: string;
  /** What actually drew, read off the resolved group state. */
  readonly renderer: "webgpu" | "css";
  /** The resolved backend(s). Joined with `+` where a scene's groups differ. */
  readonly samplingBackend: string;
  /** `vendor/architecture` from the real adapter, or why there wasn't one. */
  readonly gpuAdapter: string;
  /** X5 locks v1 calibration to sRGB. */
  readonly colorSpace: string;
  /** How the PNG was taken, in enough detail to reproduce it. */
  readonly capturePath: string;
  readonly sceneId: string;
  readonly pixelSize: readonly [number, number];
  readonly deterministic: boolean;
  /** Mean absolute channel difference between the two captures. 0 when identical. */
  readonly repeatNoise: number;
}

// ---------------------------------------------------------------------------
// Arguments
// ---------------------------------------------------------------------------

interface Options {
  readonly sceneIds: readonly string[];
  readonly renderer: "css" | "webgpu";
  readonly scale: number;
  readonly frames: number;
  readonly colorScheme: "light" | "dark";
  readonly outDir: string;
}

interface SceneMatrix {
  readonly canvas: { readonly width: number; readonly height: number };
  readonly scenes: readonly { readonly id: string }[];
}

function parseOptions(argv: readonly string[], matrix: SceneMatrix): Options {
  const ids: string[] = [];
  let renderer: "css" | "webgpu" = "webgpu";
  let scale = 1;
  let frames = 8;
  let colorScheme: "light" | "dark" = "light";
  let outDir = DEFAULT_OUT;
  let all = false;

  const next = (index: number, flag: string): string => {
    const value = argv[index + 1];
    if (value === undefined) throw new Error(`${flag} needs a value`);
    return value;
  };

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index] as string;
    switch (argument) {
      case "--all":
        all = true;
        break;
      case "--renderer": {
        const value = next(index, argument);
        if (value !== "css" && value !== "webgpu") {
          throw new Error(`--renderer takes css or webgpu, not "${value}"`);
        }
        renderer = value;
        index += 1;
        break;
      }
      case "--scale":
        scale = Number.parseFloat(next(index, argument));
        index += 1;
        break;
      case "--frames":
        frames = Number.parseInt(next(index, argument), 10);
        index += 1;
        break;
      case "--color-scheme": {
        const value = next(index, argument);
        if (value !== "light" && value !== "dark") {
          throw new Error(`--color-scheme takes light or dark, not "${value}"`);
        }
        colorScheme = value;
        index += 1;
        break;
      }
      case "--out":
        outDir = resolve(process.cwd(), next(index, argument));
        index += 1;
        break;
      default:
        if (argument.startsWith("--")) throw new Error(`unknown flag ${argument}`);
        ids.push(argument);
    }
  }

  const declared = matrix.scenes.map((scene) => scene.id);
  const sceneIds = all ? declared : ids;
  if (sceneIds.length === 0) {
    throw new Error(
      "Name at least one scene, or pass --all.\n" +
        `The matrix declares:\n  ${declared.join("\n  ")}`,
    );
  }
  const unknown = sceneIds.filter((id) => !declared.includes(id));
  if (unknown.length > 0) {
    throw new Error(`These are not in the scene matrix: ${unknown.join(", ")}`);
  }

  return { sceneIds, renderer, scale, frames, colorScheme, outDir };
}

// ---------------------------------------------------------------------------
// Capture
// ---------------------------------------------------------------------------

interface Capture {
  readonly png: Buffer;
  readonly report: SceneReport;
}

/**
 * One capture, from a fresh page.
 *
 * The readiness wait is on the page's own signal — the raster decoded, the tier
 * resolved, the frames presented — and never on an interval. A timed wait would
 * sample whatever had happened by then, which for a GPU tier that resolves
 * asynchronously is a coin flip between glass and an empty canvas.
 */
async function capture(
  context: BrowserContext,
  baseUrl: string,
  sceneId: string,
  renderer: "css" | "webgpu",
  frames: number,
  scale: number,
): Promise<Capture> {
  const page = await context.newPage();
  try {
    const query = new URLSearchParams({
      scene: sceneId,
      renderer,
      scale: `${scale}`,
      frames: `${frames}`,
    });
    await page.goto(`${baseUrl}/index.html?${query.toString()}`);
    // `attached`, not the default `visible`: everything the page draws is in a
    // fixed-position stage, so `<html>` has no layout box of its own and the
    // visibility heuristic would time out on a page that is fully rendered.
    await page.waitForSelector("html[data-scene-ready='1'], html[data-scene-error]", {
      state: "attached",
    });

    const failure = await page.getAttribute("html", "data-scene-error");
    if (failure !== null) throw new Error(`the scene page failed to build: ${failure}`);

    const report = (await page.evaluate(
      () => window.__vitreaCalibration.report,
    )) as SceneReport;

    // The measured region only — not the viewport — so the PNG's frame is the
    // scene canvas by construction rather than by the viewport happening to
    // match it.
    const png = await page.locator("#stage").screenshot({ animations: "disabled" });
    return { png, report };
  } finally {
    await page.close();
  }
}

/** Mean absolute channel difference over RGBA. `undefined` when incomparable. */
function meanAbsoluteDifference(a: Buffer, b: Buffer): number | undefined {
  const left = PNG.sync.read(a);
  const right = PNG.sync.read(b);
  if (left.width !== right.width || left.height !== right.height) return undefined;

  let total = 0;
  for (let index = 0; index < left.data.length; index += 1) {
    total += Math.abs((left.data[index] as number) - (right.data[index] as number));
  }
  return total / left.data.length;
}

function adapterString(report: SceneReport): string {
  const { adapter } = report;
  if (!adapter.ok) return `unavailable: ${adapter.why ?? "unknown"}`;
  const identity = [adapter.vendor, adapter.architecture].filter(Boolean).join("/") || "unnamed";
  const detail = adapter.description ?? adapter.device;
  const named = detail === undefined || detail === "" ? identity : `${identity} (${detail})`;
  return adapter.isFallback === true ? `software-fallback: ${named}` : named;
}

/**
 * Why a webgpu request cannot honestly be captured as a GPU-tier cell here.
 *
 * Returns `undefined` when it can. Both an absent adapter and a software one
 * count: the second answers every question plausibly and none of them about
 * whether real glass renders on real hardware.
 */
function gpuTierRefusal(report: SceneReport): string | undefined {
  if (!report.adapter.ok) {
    return `no WebGPU adapter (${report.adapter.why ?? "unknown"})`;
  }
  if (report.adapter.isFallback === true && !ALLOW_FALLBACK_ADAPTER) {
    return (
      `the adapter is a software fallback (${adapterString(report)}); ` +
      "set VITREA_ALLOW_FALLBACK_ADAPTER=1 to measure the software path deliberately"
    );
  }
  const demoted = report.groups.filter((group) => group.state?.activeRenderer !== "webgpu");
  if (demoted.length > 0) {
    const named = demoted
      .map(
        (group) =>
          `${group.id} → ${group.state?.activeRenderer ?? "nothing"}` +
          (group.state?.demotionReason === undefined ? "" : ` (${group.state.demotionReason})`),
      )
      .join(", ");
    return `the runtime resolved the CSS tier anyway: ${named}`;
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// The run
// ---------------------------------------------------------------------------

interface SceneOutcome {
  readonly sceneId: string;
  readonly cell: WebCell;
  readonly fallback: { readonly from: string; readonly to: string; readonly why: string } | undefined;
  readonly problems: readonly string[];
}

async function captureScene(
  context: BrowserContext,
  browser: Browser,
  baseUrl: string,
  sceneId: string,
  options: Options,
): Promise<SceneOutcome> {
  let renderer = options.renderer;
  let first = await capture(context, baseUrl, sceneId, renderer, options.frames, options.scale);
  let fallback: SceneOutcome["fallback"];

  if (renderer === "webgpu") {
    const refusal = gpuTierRefusal(first.report);
    if (refusal !== undefined) {
      // Recorded, and re-captured rather than relabelled: a root that asked for
      // WebGPU and was demoted carries a `demoted` health that a CSS-by-choice
      // root does not, and a cell should describe an ordinary CSS-tier render.
      fallback = { from: "webgpu", to: "css", why: refusal };
      renderer = "css";
      first = await capture(context, baseUrl, sceneId, renderer, options.frames, options.scale);
    }
  }

  const second = await capture(context, baseUrl, sceneId, renderer, options.frames, options.scale);

  const identical = first.png.equals(second.png);
  const difference = identical ? 0 : meanAbsoluteDifference(first.png, second.png);
  if (difference === undefined) {
    throw new Error(
      `The two captures of "${sceneId}" have different dimensions, which is a bug in the ` +
        "capture path rather than noise.",
    );
  }

  const decoded = PNG.sync.read(first.png);
  const expected = first.report.pixelSize;
  const problems = [...first.report.problems];
  if (decoded.width !== expected[0] || decoded.height !== expected[1]) {
    problems.push(
      `The capture is ${decoded.width}×${decoded.height} px but the scene canvas at scale ` +
        `${options.scale} is ${expected[0]}×${expected[1]}. It cannot be diffed against the ` +
        "native fixture without a resample, which would blur the edges being measured.",
    );
  }

  const activeRenderers = new Set(
    first.report.groups.map((group) => group.state?.activeRenderer ?? "none"),
  );
  const backends = [
    ...new Set(first.report.groups.map((group) => group.state?.samplingBackend ?? "none")),
  ];

  const cell: WebCell = {
    engine: "chromium",
    engineVersion: browser.version(),
    // Read off the resolved state, never off the request. A scene whose groups
    // resolved to different renderers would be a contradiction rather than a
    // cell, so it is named as one instead of being silently collapsed.
    renderer:
      activeRenderers.size === 1 && activeRenderers.has("webgpu") ? "webgpu" : "css",
    samplingBackend: backends.join("+"),
    gpuAdapter: adapterString(first.report),
    colorSpace: first.report.canvasColorSpace,
    capturePath:
      `playwright ${browser.version()} element screenshot of #stage, ` +
      `channel=chromium ${GPU_ARGS.join(" ")}, ` +
      `viewport=${first.report.canvas.width}x${first.report.canvas.height} ` +
      `deviceScaleFactor=${options.scale}, colorScheme=${options.colorScheme}, ` +
      `animations=disabled, frames=${first.report.frames}`,
    sceneId,
    pixelSize: [decoded.width, decoded.height],
    deterministic: identical,
    repeatNoise: difference,
  };

  if (activeRenderers.size > 1) {
    problems.push(
      `The scene's groups resolved to different renderers (${[...activeRenderers].join(", ")}), ` +
        "so one cell cannot describe it. The cell reports css, which is the weaker claim.",
    );
  }

  /*
   * Tier-suffixed, inside the scene's own directory.
   *
   * X9 states claims per tier — the texture tier and the dom tier are calibrated
   * and reported separately — so one scene legitimately has two cells, and they
   * have to be able to sit side by side. A single `cell.json` would mean a CSS
   * run silently overwriting a GPU-tier capture, which is the one class of loss
   * a calibration harness may not have.
   */
  const directory = join(options.outDir, sceneId);
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, `${sceneId}__${cell.renderer}.png`), first.png);
  await writeFile(
    join(directory, `cell__${cell.renderer}.json`),
    `${JSON.stringify(cell, undefined, 2)}\n`,
  );
  await writeFile(
    join(directory, `report__${cell.renderer}.json`),
    `${JSON.stringify(
      {
        capturedAt: new Date().toISOString(),
        requestedRenderer: options.renderer,
        colorScheme: options.colorScheme,
        fallback: fallback ?? null,
        problems,
        page: first.report,
      },
      undefined,
      2,
    )}\n`,
  );

  return { sceneId, cell, fallback, problems };
}

async function main(): Promise<void> {
  const matrix = JSON.parse(readFileSync(SCENES_JSON, "utf8")) as SceneMatrix;
  const options = parseOptions(process.argv.slice(2), matrix);

  let server: ViteDevServer | undefined;
  let browser: Browser | undefined;
  const outcomes: SceneOutcome[] = [];

  try {
    server = await createServer({ configFile: VITE_CONFIG });
    await server.listen();
    const url = server.resolvedUrls?.local[0];
    if (url === undefined) throw new Error("the scene server reported no local URL");
    const baseUrl = url.replace(/\/$/, "");
    say(`scene server: ${baseUrl}`);

    // C6's recipe, unchanged. `channel: "chromium"` is the full browser binary
    // and is what produces a hardware adapter rather than SwiftShader; the flags
    // are what let Dawn use it.
    browser = await chromium.launch({ channel: "chromium", args: GPU_ARGS });
    say(`engine: chromium ${browser.version()}`);

    const context = await browser.newContext({
      // The viewport is the scene canvas exactly. The renderer cover-fits a
      // backdrop texture to the viewport, so a viewport of another aspect ratio
      // would frame the raster differently from the page's own `<img>` and the
      // glass would refract pixels other than the ones behind it.
      viewport: { width: matrix.canvas.width, height: matrix.canvas.height },
      deviceScaleFactor: options.scale,
      colorScheme: options.colorScheme,
    });

    for (const sceneId of options.sceneIds) {
      const outcome = await captureScene(context, browser, baseUrl, sceneId, options);
      outcomes.push(outcome);

      const { cell } = outcome;
      say("");
      say(`${sceneId}`);
      say(`  tier          ${cell.renderer} / ${cell.samplingBackend}`);
      say(`  adapter       ${cell.gpuAdapter}`);
      say(`  colour space  ${cell.colorSpace}`);
      say(`  pixels        ${cell.pixelSize[0]}x${cell.pixelSize[1]}`);
      say(
        `  determinism   ${cell.deterministic ? "byte-identical over two loads" : `mad ${cell.repeatNoise.toFixed(6)}`}`,
      );
      say(`  written       ${join(options.outDir, sceneId).replace(`${REPO_ROOT}/`, "")}/`);
      if (outcome.fallback !== undefined) {
        say(`  FELL BACK     ${outcome.fallback.from} → ${outcome.fallback.to}: ${outcome.fallback.why}`);
      }
      for (const problem of outcome.problems) say(`  PROBLEM       ${problem}`);
    }
  } finally {
    await browser?.close();
    await server?.close();
  }

  const fellBack = outcomes.filter((outcome) => outcome.fallback !== undefined).length;
  const flawed = outcomes.filter((outcome) => outcome.problems.length > 0).length;
  say("");
  say(
    `${outcomes.length} scene(s) captured; ${fellBack} fell back to the CSS tier; ` +
      `${flawed} carry problems.`,
  );

  // A problem is a capture that would mislead the matrix, so the exit code says
  // so — while the PNG and the cell are still on disk, labelled, for inspection.
  if (flawed > 0) process.exitCode = 1;
}

main().catch((error: unknown) => {
  console.error(`${basename(process.argv[1] ?? "capture-web")}: ${String(error)}`);
  process.exitCode = 1;
});
