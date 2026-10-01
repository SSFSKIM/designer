// TEMPORARY perf-wave micro-benchmark (not committed): rgba32float copy throughput by form.
import { test } from "@playwright/test";
import { openHarness, requireHardwareAdapter } from "../support";

test("@w42-micro3 copy throughput", async ({ page }) => {
  test.setTimeout(300_000);
  requireHardwareAdapter(await openHarness(page));
  const out = await page.evaluate(async () => {
    const adapter = await navigator.gpu.requestAdapter();
    const device = await adapter!.requestDevice();
    const W = 1024, H = 1024, REPS = 10;
    const results: Record<string, number> = {};
    const time = async (label: string, encode: (e: GPUCommandEncoder) => void) => {
      const walls: number[] = [];
      for (let r = 0; r < 30; r += 1) {
        const t0 = performance.now();
        const e = device.createCommandEncoder();
        encode(e);
        device.queue.submit([e.finish()]);
        await device.queue.onSubmittedWorkDone();
        walls.push(performance.now() - t0);
      }
      walls.sort((a, b) => a - b);
      results[label] = walls[15]! / REPS;
    };
    for (const format of ["rgba32float", "rgba16float"] as const) {
      const tex = () => device.createTexture({ size: [W, H], format,
        usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.STORAGE_BINDING });
      const t = [tex(), tex()];
      for (const [name, wg, body] of [
        ["copy 8x8", "8, 8", "let c = vec2i(g.xy); textureStore(dst, c, textureLoad(src, c, 0) * 0.5);"],
        ["copy 64x1", "64, 1", "let c = vec2i(g.xy); textureStore(dst, c, textureLoad(src, c, 0) * 0.5);"],
        ["copy 64x1 col", "64, 1", "let c = vec2i(g.yx); textureStore(dst, c, textureLoad(src, c, 0) * 0.5);"],
        ["load4 store1", "8, 8", "let c = vec2i(g.xy); textureStore(dst, c, textureLoad(src, c, 0) + textureLoad(src, c + vec2i(1, 0), 0) + textureLoad(src, c + vec2i(0, 1), 0) + textureLoad(src, c + vec2i(1, 1), 0));"],
        ["load16 store1", "8, 8", "let c = vec2i(g.xy); var s = vec4f(0.0); for (var y = 0; y < 4; y++) { for (var x = 0; x < 4; x++) { s += textureLoad(src, c + vec2i(x, y), 0); } } textureStore(dst, c, s);"],
      ] as const) {
        const mod = device.createShaderModule({ code: `
@group(0) @binding(0) var src : texture_2d<f32>;
@group(0) @binding(1) var dst : texture_storage_2d<${format}, write>;
@compute @workgroup_size(${wg}) fn cs(@builtin(global_invocation_id) g : vec3u) {
  if (g.x >= ${W}u || g.y >= ${H}u) { return; }
  ${body}
}` });
        const p = device.createComputePipeline({ layout: "auto", compute: { module: mod, entryPoint: "cs" } });
        const bg = [0, 1].map((i) => device.createBindGroup({ layout: p.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: t[i]!.createView() }, { binding: 1, resource: t[1 - i]!.createView() }] }));
        const [x, y] = wg === "8, 8" ? [W / 8, H / 8] : [W / 64, H];
        await time(`${format} ${name}`, (e) => {
          const pass = e.beginComputePass(); pass.setPipeline(p);
          for (let i = 0; i < REPS; i += 1) { pass.setBindGroup(0, bg[i % 2]!); pass.dispatchWorkgroups(x, y); }
          pass.end();
        });
      }
    }
    return results;
  });
  console.log(JSON.stringify(out, null, 1));
});
