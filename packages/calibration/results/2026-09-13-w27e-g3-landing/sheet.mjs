#!/usr/bin/env node

/**
 * W27e G3 eye sheets: the landing's public controls and playground ink plate
 * beside the same views at the pre-G2 commit, one sheet per colour scheme.
 */

import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { setTimeout as sleep } from "node:timers/promises";

import { chromium } from "@playwright/test";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  args.set(process.argv[index].replace(/^--/, ""), process.argv[index + 1]);
}
const landingRoot = resolve(args.get("landing") ?? process.cwd());
const beforeRoot = resolve(args.get("before") ?? "");
const out = resolve(
  args.get("out") ?? dirname(fileURLToPath(import.meta.url)),
);
if (beforeRoot === resolve("")) {
  throw new Error("usage: sheet.mjs --before <pre-G2 checkout> [--landing <checkout>] [--out <dir>]");
}

const raw = join(out, "sheets", "raw");
mkdirSync(raw, { recursive: true });

const sides = [
  { key: "before", label: "pre-G2 · de9a9bcd", root: beforeRoot, port: 5341 },
  { key: "landing", label: "W27e G3 landing", root: landingRoot, port: 5342 },
];

const servers = sides.map((side) => {
  const server = spawn("pnpm", ["exec", "vite", "--port", String(side.port), "--strictPort"], {
    cwd: join(side.root, "apps", "demo"),
    stdio: ["ignore", "pipe", "pipe"],
  });
  server.stdout.on("data", () => {});
  server.stderr.on("data", (chunk) => process.stderr.write(`[${side.key}] ${String(chunk)}`));
  return server;
});

async function waitForServer(port) {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    try {
      const response = await fetch(`http://localhost:${String(port)}/`);
      if (response.ok) return;
    } catch {
      // The server is still starting.
    }
    await sleep(500);
  }
  throw new Error(`the demo server on ${String(port)} never came up`);
}

async function captureUnion(page, selectors, path) {
  const box = await page.evaluate((query) => {
    const boxes = query
      .flatMap((selector) => [...document.querySelectorAll(selector)])
      .map((element) => element.getBoundingClientRect())
      .filter(
        (rect) =>
          rect.width > 0 && rect.height > 0 && rect.bottom > 0 && rect.top < window.innerHeight,
      );
    if (boxes.length === 0) return null;
    const left = Math.max(0, Math.min(...boxes.map((box) => box.left)) - 16);
    const top = Math.max(0, Math.min(...boxes.map((box) => box.top)) - 16);
    const right = Math.min(window.innerWidth, Math.max(...boxes.map((box) => box.right)) + 16);
    const bottom = Math.min(window.innerHeight, Math.max(...boxes.map((box) => box.bottom)) + 16);
    return { x: left, y: top, width: right - left, height: bottom - top };
  }, selectors);
  if (box === null) throw new Error(`no visible boxes for ${selectors.join(", ")}`);
  await page.screenshot({ path, clip: box });
}

async function adapterOf(page) {
  return page.evaluate(async () => {
    const adapter = await navigator.gpu?.requestAdapter();
    if (adapter === null || adapter === undefined) return { available: false };
    const info = {
      vendor: adapter.info?.vendor ?? null,
      architecture: adapter.info?.architecture ?? null,
      device: adapter.info?.device ?? null,
      description: adapter.info?.description ?? null,
    };
    const identity = Object.values(info).filter((value) => value !== null).join(" ");
    const reported = adapter.isFallbackAdapter;
    return {
      available: true,
      isFallbackAdapter: reported ?? /swiftshader|llvmpipe|software|cpu/i.test(identity),
      isFallbackAdapterReported: reported ?? null,
      info,
    };
  });
}

async function requireSectionTier(page, section) {
  await page.waitForFunction(
    (id) => {
      const values = [...document.querySelectorAll(`#${id} .readout__row`)]
        .filter((row) => (row.textContent ?? "").includes("What is drawing"))
        .map((row) => row.querySelector("dd")?.textContent?.trim());
      return values.length > 0 && values.every((value) => value === "webgpu");
    },
    section,
  );
}

async function requireInkTier(page) {
  await page.waitForFunction(() => {
    const values = [...document.querySelectorAll("[data-testid^='ink-tier-']")].map((node) =>
      (node.textContent ?? "").trim(),
    );
    return values.length === 2 && values.every((value) => value === "webgpu · css-backdrop");
  });
}

const metadata = {
  takenAt: new Date().toISOString(),
  accessibility: {
    reduceTransparency: process.env.W27E_REDUCE_TRANSPARENCY ?? "unrecorded",
    increaseContrast: process.env.W27E_INCREASE_CONTRAST ?? "unrecorded",
  },
  viewport: { width: 1440, height: 1000, dpr: 1 },
  sides: {},
};

try {
  await Promise.all(sides.map((side) => waitForServer(side.port)));
  const browser = await chromium.launch({
    channel: "chromium",
    args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"],
  });

  for (const side of sides) {
    metadata.sides[side.key] = {
      label: side.label,
      commit: spawnSync("git", ["-C", side.root, "rev-parse", "HEAD"], {
        encoding: "utf8",
      }).stdout.trim(),
      adapter: null,
      captures: {},
    };

    for (const scheme of ["light", "dark"]) {
      const context = await browser.newContext({
        viewport: { width: 1440, height: 1000 },
        deviceScaleFactor: 1,
        colorScheme: scheme,
      });
      const page = await context.newPage();
      const base = `http://localhost:${String(side.port)}`;

      await page.goto(`${base}/`);
      await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
      await page.getByTestId("color-scheme-select").selectOption(scheme);
      await page.evaluate(() => {
        document.getElementById("behavior")?.scrollIntoView({ block: "center", behavior: "instant" });
      });
      await page.waitForFunction(
        () => document.getElementById("behavior")?.hasAttribute("data-current") === true,
      );
      await requireSectionTier(page, "behavior");
      await sleep(2000);

      if (metadata.sides[side.key].adapter === null) {
        const adapter = await adapterOf(page);
        if (adapter.available !== true || adapter.isFallbackAdapter !== false) {
          throw new Error(`${side.key} did not reach a hardware adapter: ${JSON.stringify(adapter)}`);
        }
        metadata.sides[side.key].adapter = adapter;
      }

      const controls = join(raw, `${side.key}-${scheme}-controls.png`);
      await captureUnion(page, [".bar .control", ".segmented .segment", ".platter"], controls);

      await page.goto(`${base}/playground/`);
      await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
      await requireInkTier(page);
      await sleep(2000);
      const plate = join(raw, `${side.key}-${scheme}-plate.png`);
      await captureUnion(page, [".region--ink", ".ink-overlay"], plate);

      metadata.sides[side.key].captures[scheme] = { controls, plate };
      await context.close();
    }
  }

  for (const scheme of ["light", "dark"]) {
    const cards = sides
      .map((side) => {
        const captures = metadata.sides[side.key].captures[scheme];
        const image = (path) => `data:image/png;base64,${readFileSync(path).toString("base64")}`;
        return `<section><h2>${side.label}</h2><h3>Public demo controls</h3><img src="${image(
          captures.controls,
        )}"><h3>Playground tint and ink plate</h3><img src="${image(captures.plate)}"></section>`;
      })
      .join("");
    const context = await browser.newContext({ viewport: { width: 1600, height: 1200 } });
    const sheet = await context.newPage();
    await sheet.setContent(`<!doctype html><style>
      * { box-sizing: border-box; }
      body { margin: 0; padding: 32px; width: 1600px; font: 16px system-ui; color: ${
        scheme === "dark" ? "#f2f2f2" : "#181818"
      }; background: ${scheme === "dark" ? "#15171a" : "#f3f4f6"}; }
      h1 { margin: 0 0 24px; font-size: 28px; }
      h2 { margin: 0 0 14px; font-size: 20px; }
      h3 { margin: 14px 0 8px; font-size: 13px; font-weight: 600; opacity: .72; }
      main { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
      section { min-width: 0; padding: 18px; border: 1px solid ${
        scheme === "dark" ? "#3a3d42" : "#d5d8dc"
      }; background: ${scheme === "dark" ? "#202328" : "#fff"}; }
      img { display: block; width: 100%; height: auto; background: transparent; }
    </style><h1>W27e G3 · ${scheme} scheme · hardware WebGPU</h1><main>${cards}</main>`);
    await sheet.screenshot({ path: join(out, "sheets", `eye-sheet-${scheme}.png`), fullPage: true });
    await context.close();
  }

  await browser.close();
  writeFileSync(join(out, "sheets", "eye.json"), `${JSON.stringify(metadata, null, 2)}\n`);
} finally {
  for (const server of servers) server.kill("SIGTERM");
}
