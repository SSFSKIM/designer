import { defineConfig } from "vitest/config";

// Workspace-wide runner: `vitest` at the root runs every package's suite as its
// own project. `pnpm -r test` runs the same suites package-by-package.
export default defineConfig({
  test: {
    projects: ["packages/*"],
  },
});
