/** Browser preflight shared by G1's input check and candidate reads (claims §5.145). */
import { execFileSync } from "node:child_process";
import { appendFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";
import { createServer } from "vite";

export const here = dirname(fileURLToPath(import.meta.url));
export const pkg = resolve(here, "../..");
export const repo = resolve(pkg, "../..");

export function machinePreflight(label: string) {
  const preference = (key: string): number => {
    try {
      return Number(execFileSync("defaults", ["read", "com.apple.universalaccess", key],
        { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim());
    } catch (error) {
      const stderr = String((error as { stderr?: unknown }).stderr ?? "");
      if (stderr.includes(`(com.apple.universalaccess, ${key}) does not exist`)) return 0;
      throw error;
    }
  };
  const settings = { label, readAt: new Date().toISOString(),
    reduceTransparency: preference("reduceTransparency"),
    increaseContrast: preference("increaseContrast") };
  appendFileSync(resolve(here, "browser-runs.txt"), `${JSON.stringify(settings)}\n`);
  if (settings.reduceTransparency !== 0 || settings.increaseContrast !== 0) {
    throw new Error("Refusing browser run: accessibility must read 0 / 0; settings were not changed");
  }
  return settings;
}

export async function launch(label: string, port = 5216) {
  const machineAccessibility = machinePreflight(label);
  const scratch = process.env["VITREA_WEB_CAPTURES"];
  if (scratch === undefined || resolve(scratch).startsWith(resolve(pkg, "web-captures"))) {
    throw new Error("VITREA_WEB_CAPTURES must explicitly name a scratch capture directory");
  }
  mkdirSync(scratch, { recursive: true });
  const server = await createServer({ configFile: resolve(pkg, "web/vite.config.ts"),
    server: { port, strictPort: true } });
  await server.listen();
  try {
    const browser = await chromium.launch({ channel: "chromium", headless: false,
      args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU"] });
    return { browser, server, machineAccessibility, scratch, url: `http://localhost:${port}` };
  } catch (error) {
    await server.close();
    throw error;
  }
}
