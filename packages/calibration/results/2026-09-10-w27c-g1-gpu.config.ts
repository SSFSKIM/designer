/** The W27c G1 isolation proof's private-server recipe; never reuse another harness. */
import { fileURLToPath } from "node:url";
import base from "../../renderer-webgpu/playwright.config";

const renderer = fileURLToPath(new URL("../../renderer-webgpu/", import.meta.url));
const port = Number(process.env.W27C_G1_GPU_PORT ?? "5213");
export default {
  ...base,
  testDir: `${renderer}e2e`,
  use: { ...base.use, baseURL: `http://localhost:${port}` },
  webServer: {
    command: `npx vite --config e2e/vite.config.ts --port ${port} --strictPort`,
    cwd: renderer,
    url: `http://localhost:${port}/e2e/fixtures/index.html`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
};
