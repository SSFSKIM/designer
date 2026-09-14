/**
 * W28 G4, step 3: what the demo actually does when its window goes to the background
 * (claims §5.148).
 *
 * Two readings, and they answer different questions.
 *
 * **The operable path.** The playground's `windowActivation` pin is the control an
 * adopter can reach, so the sheets are captured through it: the same page at 2×, on
 * headed hardware Chromium, in both schemes, pinned `active` and pinned `inactive`.
 * A pin is deterministic where a real focus change is not, which is the whole reason
 * the control exists (§5.147 §2) and why it is what a sheet can be built from.
 *
 * **The real focus loss.** A pin proves the endpoint is reachable; it does not prove
 * the browser delivers a window-manager focus change to `document.hasFocus()`, which
 * is the one thing Playwright cannot arrange — §5.147 §4 records that `bringToFront()`
 * on a second page leaves the first document focused on all three engines, so G3's
 * tests fed `hasFocus` synthetically and said so. Here the machine itself is used:
 * another application is made frontmost, the page is left alone for several seconds,
 * and the ROOT's own resolved readout is read back. Nothing is simulated and nothing
 * is asserted about a frame — the question is only whether the engine delivered the
 * change at all, and what the runtime resolved when it did.
 *
 * The activation goes through **LaunchServices** (`open -a`) and the frontmost process
 * is read through `lsappinfo`, not through AppleScript. On this machine an AppleEvent
 * to `System Events` or to `Finder` times out at -1712 waiting for an automation
 * consent nobody is present to give, and a reading that needs a dialog answered is not
 * a reading an unattended run can take. LaunchServices needs no such consent and moves
 * the same window-server focus, which is the only part of the mechanism this is about.
 *
 *   tsx results/2026-09-15-w28-g4-landing/demo-pose.ts --out /tmp/w28-g4-demo
 *
 * The frontmost application is recorded before anything is activated and the screen is
 * left in a plain state at the end: this is a shared machine's screen, borrowed for the
 * minutes the reading takes.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium, type Page } from "@playwright/test";
import { createServer } from "vite";

const here = dirname(fileURLToPath(import.meta.url));
const demo = resolve(here, "../../../../apps/demo");

const arg = (name: string, fallback?: string): string => {
  const index = process.argv.indexOf(`--${name}`);
  const value = index < 0 ? fallback : process.argv[index + 1];
  if (value === undefined) throw new Error(`Missing --${name}`);
  return value;
};
const out = resolve(arg("out"));
if (!out.startsWith("/tmp/") && !out.startsWith("/private/tmp/")) {
  throw new Error(`--out must be scratch: ${out}`);
}
mkdirSync(out, { recursive: true });

const run = (command: string, args: readonly string[]): string =>
  execFileSync(command, [...args], { encoding: "utf8" }).trim();
/** The frontmost application's display name, through LaunchServices. */
const frontmost = (): string => {
  const asn = run("lsappinfo", ["front"]);
  const name = run("lsappinfo", ["info", "-only", "name", asn]);
  return /"LSDisplayName"="(.*)"/.exec(name)?.[1] ?? name;
};
/** Make an application frontmost. `open -a` is LaunchServices, not an AppleEvent. */
const activate = (application: string): void => {
  run("open", ["-a", application]);
};
const sleep = (ms: number): Promise<void> => new Promise((done) => setTimeout(done, ms));
const sha = (data: Buffer): string => createHash("sha256").update(data).digest("hex");

/** Who owns the screen right now, so the report can say what was borrowed. */
const frontmostBefore = frontmost();
process.stderr.write(`frontmost before: ${frontmostBefore}\n`);
/** The application bundle Playwright will launch, so it can be made frontmost again. */
const browserApp = chromium.executablePath().replace(/\/Contents\/MacOS\/.*$/, "");

const port = 5188;
const server = await createServer({
  configFile: resolve(demo, "vite.config.ts"),
  // The demo's config leaves `root` to vite's default, which is the process's working
  // directory — and this script runs from the calibration package. Stated, or the dev
  // server serves the wrong tree and `/playground/` 404s.
  root: demo,
  server: { port, strictPort: true },
});
await server.listen();
const browser = await chromium.launch({
  channel: "chromium",
  headless: false,
  args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
});

/** Set one of the playground's pins, found by the label it sits inside. */
const pin = async (page: Page, label: string, value: string): Promise<void> => {
  await page.evaluate(
    ({ label, value }) => {
      const owner = [...document.querySelectorAll("label.toggle")].find((element) =>
        element.textContent?.includes(label),
      );
      const select = owner?.querySelector("select");
      if (select === null || select === undefined) throw new Error(`no ${label}`);
      select.value = value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
    },
    { label, value },
  );
};

/** The runtime's own resolved answer, off the panel row the playground publishes. */
const readActivation = (page: Page): Promise<string | null> =>
  page.evaluate(() => {
    const heading = [...document.querySelectorAll("th")].find(
      (cell) => cell.textContent?.trim() === "windowActivation",
    );
    return heading?.nextElementSibling?.textContent?.trim() ?? null;
  });

const sheets: {
  scheme: string;
  pose: string;
  file: string;
  sha256: string;
  resolved: string | null;
}[] = [];
const focus: Record<string, unknown> = {};

try {
  // ── (a) the operable path, at 2×, both schemes, both pins ────────────────────
  for (const scheme of ["light", "dark"] as const) {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      deviceScaleFactor: 2,
      colorScheme: scheme,
    });
    const page = await context.newPage();
    await page.goto(`http://localhost:${port}/playground/`);
    await page.waitForSelector(".panel");
    // The recede is fitted per scheme, so the sheet has to say which one it shows.
    // The playground's default is `"light"`; the dark sheet pins the other entry.
    await pin(page, "colorScheme pin", scheme);
    await sleep(800);
    for (const pose of ["active", "inactive"] as const) {
      await pin(page, "windowActivation pin", pose);
      // The CSS tier transitions the pose over 240 ms; the sheet is of the settled
      // endpoint, not of a frame in transit.
      await sleep(1200);
      const resolved = await readActivation(page);
      if (resolved !== pose) {
        throw new Error(`playground ${scheme}/${pose}: the root resolved "${resolved}"`);
      }
      const ground = await page.evaluate(() => document.documentElement.dataset["colorScheme"]);
      if (ground !== scheme) {
        throw new Error(`playground ${scheme}/${pose}: the page ground reads "${ground}"`);
      }
      const png = await page.screenshot({ animations: "disabled" });
      const file = `playground-2x-${scheme}-${pose}.png`;
      writeFileSync(resolve(out, file), png);
      sheets.push({ scheme, pose, file, sha256: sha(png), resolved });
      process.stderr.write(`captured ${file}\n`);
    }
    await page.close();
    await context.close();
  }

  // ── (b) a real focus loss on this machine ───────────────────────────────────
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();
  await page.goto(`http://localhost:${port}/playground/`);
  await page.waitForSelector(".panel");
  await page.bringToFront();
  await sleep(1500);

  focus["pin"] = await page.evaluate(() => {
    const owner = [...document.querySelectorAll("label.toggle")].find((element) =>
      element.textContent?.includes("windowActivation pin"),
    );
    return owner?.querySelector("select")?.value ?? null;
  });
  focus["atStart"] = {
    activation: await readActivation(page),
    hasFocus: await page.evaluate(() => document.hasFocus()),
  };

  activate(browserApp);
  await sleep(2500);
  const frontmostWithBrowser = frontmost();
  focus["browserApp"] = browserApp;
  focus["frontmostWithBrowser"] = frontmostWithBrowser;
  focus["afterActivatingBrowser"] = {
    activation: await readActivation(page),
    hasFocus: await page.evaluate(() => document.hasFocus()),
  };
  const focused = await page.screenshot({ animations: "disabled" });
  writeFileSync(resolve(out, "playground-focus-held.png"), focused);
  focus["focusedSha256"] = sha(focused);

  activate("Finder");
  await sleep(4000);
  focus["frontmostAfterSwitch"] = frontmost();
  focus["afterSwitch"] = {
    activation: await readActivation(page),
    hasFocus: await page.evaluate(() => document.hasFocus()),
  };
  const backgrounded = await page.screenshot({ animations: "disabled" });
  writeFileSync(resolve(out, "playground-focus-lost.png"), backgrounded);
  focus["backgroundedSha256"] = sha(backgrounded);

  activate(browserApp);
  await page.bringToFront();
  await sleep(4000);
  focus["frontmostAfterReturn"] = frontmost();
  focus["afterReturn"] = {
    activation: await readActivation(page),
    hasFocus: await page.evaluate(() => document.hasFocus()),
  };
  const refocused = await page.screenshot({ animations: "disabled" });
  writeFileSync(resolve(out, "playground-focus-returned.png"), refocused);
  focus["refocusedSha256"] = sha(refocused);
  focus["backgroundedDiffersFromFocused"] = focus["backgroundedSha256"] !== focus["focusedSha256"];
  focus["returnedMatchesFocused"] = focus["refocusedSha256"] === focus["focusedSha256"];

  await page.close();
  await context.close();
} finally {
  await browser.close();
  await server.close();
  try {
    // The machine was unattended, so "restore" means leaving it in a plain state rather
    // than re-raising whatever system process happened to own the screen. Both readings
    // are in the report, so what the screen was handed back as is on the record.
    activate("Finder");
  } catch (error) {
    process.stderr.write(`could not restore the screen: ${String(error)}\n`);
  }
}

const report = {
  gate: "W28 G4 — the demo's backgrounded pose",
  claims: "§5.148",
  scratch: out,
  frontmostBefore,
  frontmostRestored: frontmost(),
  playgroundSheets: sheets,
  realFocusLoss: focus,
};
const path = resolve(here, "demo-pose.json");
if (existsSync(path)) throw new Error(`${path} exists; refusing to overwrite evidence`);
writeFileSync(path, `${JSON.stringify(report, undefined, 2)}\n`);
process.stderr.write(`\n${JSON.stringify(focus, undefined, 2)}\n`);
