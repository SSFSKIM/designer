/**
 * The package must import cleanly where there is no WebGPU.
 *
 * This is not hypothetical and it is not about Node for its own sake:
 * `@vitrea/core`'s lazy seam (X7) resolves this package through a dynamic import,
 * and `packages/core/test/renderer-seam.test.ts` exercises that in a plain Node
 * environment to read `backend`, `ready` and `shaderSource` off the result.
 *
 * A usage mask computed at module scope — `GPUTextureUsage.RENDER_ATTACHMENT |
 * ...` — makes the whole package throw a `ReferenceError` on import there, from a
 * file that never intended to run, in a test that only wanted to read three
 * fields. That happened; this is the guard.
 *
 * The rule it enforces: **browser globals are read on first use, never at module
 * scope.** `src/` deliberately reads the flag namespaces off the runtime rather
 * than hardcoding their bit values, so the browser stays the authority on them —
 * and the price of that choice is exactly this discipline.
 */

import { describe, expect, it, vi } from "vitest";

/** The globals the test setup shims in, so they can be removed again. */
const WEBGPU_GLOBALS = ["GPUBufferUsage", "GPUTextureUsage", "GPUMapMode"] as const;

async function importWithoutWebGPU(): Promise<Record<string, unknown>> {
  const saved = new Map<string, PropertyDescriptor | undefined>();
  for (const name of WEBGPU_GLOBALS) {
    saved.set(name, Object.getOwnPropertyDescriptor(globalThis, name));
    Reflect.deleteProperty(globalThis, name);
  }
  // A fresh module instance: the entry has already been evaluated by other tests,
  // and a cached one would prove nothing about evaluation order. `resetModules`
  // rather than a cache-busting query, because Vite treats a specifier with an
  // interpolated tail as a glob and refuses to resolve it.
  vi.resetModules();
  try {
    return (await import("../src/index")) as Record<string, unknown>;
  } finally {
    for (const [name, descriptor] of saved) {
      if (descriptor !== undefined) Object.defineProperty(globalThis, name, descriptor);
    }
  }
}

describe("importing the package without WebGPU", () => {
  it("does not touch a browser global at module scope", async () => {
    for (const name of WEBGPU_GLOBALS) {
      expect(name in globalThis, `${name} should be shimmed before the test removes it`).toBe(true);
    }

    const module = await importWithoutWebGPU();
    expect(typeof module.createWebGPURenderer).toBe("function");
  });

  it("builds a renderer that is honest about not being ready", async () => {
    // Exactly what core's seam test reads. `ready` is false because no device is
    // attached, and `shaderSource` carries the marker X7's bundle test greps for.
    const module = await importWithoutWebGPU();
    const create = module.createWebGPURenderer as () => {
      backend: string;
      ready: boolean;
      shaderSource: string;
      passes: readonly string[];
    };
    const renderer = create();

    expect(renderer.backend).toBe("webgpu");
    expect(renderer.ready).toBe(false);
    expect(renderer.shaderSource).toContain("vitrea:wgsl-marker");
    expect(renderer.passes.length).toBeGreaterThan(0);
  });
});
