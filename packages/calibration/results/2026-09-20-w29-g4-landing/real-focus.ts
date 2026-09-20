/**
 * W29 G4, clause 7: the demo losing focus to another application, read without
 * Playwright in the loop, on the macOS 27 material this gate selected (claims §5.155).
 *
 * W28 G4's script (`results/2026-09-15-w28-g4-landing/real-focus.ts`), re-run at this
 * head with two strings changed. Its finding about the DRIVER is W28's and is not
 * re-litigated here; what this run reads is the macOS 27 recede arriving through a real
 * window-manager focus change rather than through a pin.
 *
 * `demo-pose.ts` took this reading first and got a negative one: with the machine's own
 * frontmost application switched to the Finder through LaunchServices, the playground's
 * `document.hasFocus()` stayed **true** and the root stayed `"active"`. That reproduces
 * §5.147 §4's discovery on a real window-manager focus change rather than on
 * `bringToFront()`, and it has an explanation that is about the driver and not about the
 * runtime: Playwright turns Chromium's **focus emulation** on for every page it owns, so
 * that a suite does not break when the developer clicks away. A page held focused by the
 * protocol cannot report losing it, and no amount of activating other applications will
 * change that.
 *
 * So this script takes Playwright out. It launches the same Chromium binary itself with a
 * remote-debugging port, speaks CDP to the page over a bare WebSocket, and evaluates the
 * same two expressions — `document.hasFocus()` and the playground's own resolved
 * `windowActivation` row. Nothing here enables focus emulation, so what the page reports
 * is what the window server told the browser.
 *
 *   tsx results/2026-09-20-w29-g4-landing/real-focus.ts --out /tmp/w29-g4-focus
 *
 * The screen is borrowed for about half a minute and handed back plain.
 */
import { execFileSync, spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";
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
const frontmost = (): string => {
  const asn = run("lsappinfo", ["front"]);
  const name = run("lsappinfo", ["info", "-only", "name", asn]);
  return /"LSDisplayName"="(.*)"/.exec(name)?.[1] ?? name;
};
const activate = (application: string): void => {
  run("open", ["-a", application]);
};
const sleep = (ms: number): Promise<void> => new Promise((done) => setTimeout(done, ms));
const sha = (data: Buffer): string => createHash("sha256").update(data).digest("hex");

const frontmostBefore = frontmost();
const executable = chromium.executablePath();
const browserApp = executable.replace(/\/Contents\/MacOS\/.*$/, "");

const port = 5189;
const debugPort = 9333;
const server = await createServer({
  configFile: resolve(demo, "vite.config.ts"),
  root: demo,
  server: { port, strictPort: true },
});
await server.listen();

const profileDir = resolve(out, "chrome-profile");
mkdirSync(profileDir, { recursive: true });
const child = spawn(
  executable,
  [
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${profileDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--enable-unsafe-webgpu",
    "--enable-features=Vulkan,WebGPU",
    "--window-size=1280,900",
    `http://localhost:${port}/playground/`,
  ],
  { stdio: "ignore" },
);

/** One CDP session over a bare WebSocket — no driver, and so no focus emulation. */
class Session {
  private nextId = 1;
  private readonly pending = new Map<number, (result: unknown) => void>();
  private constructor(private readonly socket: WebSocket) {
    socket.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data)) as { id?: number; result?: unknown };
      if (message.id === undefined) return;
      this.pending.get(message.id)?.(message.result);
      this.pending.delete(message.id);
    });
  }
  static async open(url: string): Promise<Session> {
    const socket = new WebSocket(url);
    await new Promise((done, fail) => {
      socket.addEventListener("open", done, { once: true });
      socket.addEventListener("error", fail, { once: true });
    });
    return new Session(socket);
  }
  send(method: string, params: Record<string, unknown> = {}): Promise<any> {
    const id = this.nextId++;
    return new Promise((done) => {
      this.pending.set(id, done);
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }
  async evaluate(expression: string): Promise<unknown> {
    const result = await this.send("Runtime.evaluate", { expression, returnByValue: true });
    return result?.result?.value;
  }
  close(): void {
    this.socket.close();
  }
}

const READ = `(() => {
  const heading = [...document.querySelectorAll("th")].find(
    (cell) => cell.textContent && cell.textContent.trim() === "windowActivation",
  );
  return {
    hasFocus: document.hasFocus(),
    activation: heading && heading.nextElementSibling
      ? heading.nextElementSibling.textContent.trim() : null,
    pin: document.querySelector(".toggle select").value,
    visibility: document.visibilityState,
  };
})()`;

const readings: Record<string, unknown> = {};
let session: Session | undefined;
try {
  // The browser has to be up and the page has to have built its root before anything is
  // read; the readout row only exists once the React tree has mounted.
  await sleep(6000);
  const targets = (await (await fetch(`http://localhost:${debugPort}/json/list`)).json()) as {
    type: string;
    url: string;
    webSocketDebuggerUrl: string;
  }[];
  const target = targets.find((entry) => entry.type === "page" && entry.url.includes("/playground/"));
  if (target === undefined) throw new Error(`no playground target: ${JSON.stringify(targets)}`);
  session = await Session.open(target.webSocketDebuggerUrl);
  readings["cdpVersion"] = await (await fetch(`http://localhost:${debugPort}/json/version`)).json();

  const screenshot = async (name: string): Promise<string> => {
    const result = await session!.send("Page.captureScreenshot", { format: "png" });
    const png = Buffer.from(result.data, "base64");
    writeFileSync(resolve(out, name), png);
    return sha(png);
  };

  activate(browserApp);
  await sleep(3000);
  readings["frontmostWithBrowser"] = frontmost();
  readings["focused"] = await session.evaluate(READ);
  readings["focusedSha256"] = await screenshot("real-focus-held.png");

  activate("Finder");
  await sleep(5000);
  readings["frontmostAfterSwitch"] = frontmost();
  readings["backgrounded"] = await session.evaluate(READ);
  readings["backgroundedSha256"] = await screenshot("real-focus-lost.png");

  activate(browserApp);
  await sleep(5000);
  readings["frontmostAfterReturn"] = frontmost();
  readings["returned"] = await session.evaluate(READ);
  readings["returnedSha256"] = await screenshot("real-focus-returned.png");
} finally {
  session?.close();
  child.kill();
  await server.close();
  try {
    activate("Finder");
  } catch (error) {
    process.stderr.write(`could not hand the screen back: ${String(error)}\n`);
  }
}

const report = {
  gate: "W29 G4 — a real focus loss, read without a driver, on the macOS 27 material",
  claims: "§5.155",
  why: "Playwright enables Chromium's focus emulation on every page it owns, so a driven "
    + "page cannot report losing focus. This launches the same binary directly and speaks "
    + "CDP over a bare WebSocket instead.",
  executable,
  frontmostBefore,
  frontmostRestored: frontmost(),
  scratch: out,
  readings,
};
const path = resolve(here, "real-focus.json");
if (existsSync(path)) throw new Error(`${path} exists; refusing to overwrite evidence`);
writeFileSync(path, `${JSON.stringify(report, undefined, 2)}\n`);
process.stderr.write(`${JSON.stringify(readings, undefined, 2)}\n`);
