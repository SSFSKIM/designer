import { describe, expect, it } from "vitest";

import { createWebGPURenderer, OPTICS_PASS_ID, PLACEHOLDER_WGSL } from "../src/index";

describe("webgpu renderer stub", () => {
  it("reports the webgpu backend and stays honest about not being ready", () => {
    const renderer = createWebGPURenderer();

    expect(renderer.backend).toBe("webgpu");
    expect(renderer.ready).toBe(false);
    expect(renderer.passes).toContain(OPTICS_PASS_ID);
  });

  it("carries the WGSL marker the bundle-shape test asserts on", () => {
    expect(PLACEHOLDER_WGSL).toContain("vitrea:wgsl-marker");
    expect(createWebGPURenderer().shaderSource).toBe(PLACEHOLDER_WGSL);
  });
});
