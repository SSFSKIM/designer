import { describe, expect, it } from "vitest";

import { loadWebGPURenderer, VITREA_CONTRACTS } from "../src/index";

describe("lazy renderer seam (X7)", () => {
  it("resolves the renderer through a dynamic import", async () => {
    const renderer = await loadWebGPURenderer();

    expect(renderer.backend).toBe("webgpu");
    expect(renderer.ready).toBe(false);
    expect(renderer.shaderSource).toContain("vitrea:wgsl-marker");
  });

  it("re-exports the internal contract sets so consumers install one package", () => {
    expect(VITREA_CONTRACTS.shapeFamilies).toContain("concentric-rounded-rect");
    expect(VITREA_CONTRACTS.interactionStates).toContain("morphing");
    expect(VITREA_CONTRACTS.motionDrivers.position).toBe("interruptible-spring");
  });
});
