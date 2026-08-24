import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    // `src/` reads the WebGPU flag namespaces off the runtime instead of
    // hardcoding their bit values; Node has no such globals, so the shim supplies
    // them. See test/setup/webgpu-flags.ts.
    setupFiles: ["test/setup/webgpu-flags.ts"],
  },
});
