// TEMPORARY perf-wave micro-benchmark (not committed): what one render pass, one compute pass and
// one dispatch inside a compute pass cost on this adapter, dependent chain, tiny workloads.
import { writeFileSync } from "node:fs";
import { test } from "@playwright/test";
import { openHarness, requireHardwareAdapter } from "../support";

test("@w42-micro pass overhead", async ({ page }) => {
  test.setTimeout(300_000);
  requireHardwareAdapter(await openHarness(page));
  const out = await page.evaluate(async () => {
    const adapter = await navigator.gpu.requestAdapter();
    const device = await adapter!.requestDevice({ requiredFeatures: ["float32-blendable"] as GPUFeatureName[] });
    const W = 300, H = 200;
    const results: Record<string, number> = {};
    const tex = (i: number) => device.createTexture({ size: [W, H], format: "rgba32float",
      usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.STORAGE_BINDING, label: `t${i}` });
    const ta = [tex(0), tex(1)];
    const rmod = device.createShaderModule({ code: `
@vertex fn vs(@builtin(vertex_index) i : u32) -> @builtin(position) vec4f {
  let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u));
  return vec4f(p * 2.0 - 1.0, 0.0, 1.0);
}
@group(0) @binding(0) var src : texture_2d<f32>;
@fragment fn fs(@builtin(position) p : vec4f) -> @location(0) vec4f {
  return textureLoad(src, vec2i(p.xy), 0) * 0.5 + vec4f(0.25);
}` });
    const rp = device.createRenderPipeline({ layout: "auto", vertex: { module: rmod, entryPoint: "vs" },
      fragment: { module: rmod, entryPoint: "fs", targets: [{ format: "rgba32float" }] } });
    const cmod = device.createShaderModule({ code: `
@group(0) @binding(0) var src : texture_2d<f32>;
@group(0) @binding(1) var dst : texture_storage_2d<rgba32float, write>;
@compute @workgroup_size(8, 8) fn cs(@builtin(global_invocation_id) g : vec3u) {
  if (g.x >= ${W}u || g.y >= ${H}u) { return; }
  textureStore(dst, vec2i(g.xy), textureLoad(src, vec2i(g.xy), 0) * 0.5 + vec4f(0.25));
}` });
    const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
    const bmod = device.createShaderModule({ code: `
@group(0) @binding(0) var<storage, read> src : array<vec4f>;
@group(0) @binding(1) var<storage, read_write> dst : array<vec4f>;
@compute @workgroup_size(64) fn cs(@builtin(global_invocation_id) g : vec3u) {
  if (g.x >= ${W * H}u) { return; }
  dst[g.x] = src[g.x] * 0.5 + vec4f(0.25);
}` });
    const bp = device.createComputePipeline({ layout: "auto", compute: { module: bmod, entryPoint: "cs" } });
    const bufs = [0, 1].map(() => device.createBuffer({ size: W * H * 16, usage: GPUBufferUsage.STORAGE }));
    const rbg = [0, 1].map((i) => device.createBindGroup({ layout: rp.getBindGroupLayout(0),
      entries: [{ binding: 0, resource: ta[i]!.createView() }] }));
    const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
      entries: [{ binding: 0, resource: ta[i]!.createView() }, { binding: 1, resource: ta[1 - i]!.createView() }] }));
    const bbg = [0, 1].map((i) => device.createBindGroup({ layout: bp.getBindGroupLayout(0),
      entries: [{ binding: 0, resource: { buffer: bufs[i]! } }, { binding: 1, resource: { buffer: bufs[1 - i]! } }] }));
    const run = async (label: string, n: number, encode: (e: GPUCommandEncoder, n: number) => void) => {
      const walls: number[] = [];
      for (let r = 0; r < 40; r += 1) {
        const t0 = performance.now();
        const e = device.createCommandEncoder();
        encode(e, n);
        device.queue.submit([e.finish()]);
        await device.queue.onSubmittedWorkDone();
        walls.push(performance.now() - t0);
      }
      walls.sort((a, b) => a - b);
      results[label] = walls[20]!;
    };
    for (const n of [1, 80]) {
      await run(`render passes x${n}`, n, (e, n) => {
        for (let i = 0; i < n; i += 1) {
          const p = e.beginRenderPass({ colorAttachments: [{ view: ta[1 - (i % 2)]!.createView(), loadOp: "clear", storeOp: "store", clearValue: [0, 0, 0, 0] }] });
          p.setPipeline(rp); p.setBindGroup(0, rbg[i % 2]!); p.draw(3); p.end();
        }
      });
      await run(`compute passes x${n}`, n, (e, n) => {
        for (let i = 0; i < n; i += 1) {
          const p = e.beginComputePass(); p.setPipeline(cp); p.setBindGroup(0, cbg[i % 2]!);
          p.dispatchWorkgroups(Math.ceil(W / 8), Math.ceil(H / 8)); p.end();
        }
      });
      await run(`dispatches in one pass (texture) x${n}`, n, (e, n) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < n; i += 1) { p.setBindGroup(0, cbg[i % 2]!); p.dispatchWorkgroups(Math.ceil(W / 8), Math.ceil(H / 8)); }
        p.end();
      });
      await run(`dispatches in one pass (buffer) x${n}`, n, (e, n) => {
        const p = e.beginComputePass(); p.setPipeline(bp);
        for (let i = 0; i < n; i += 1) { p.setBindGroup(0, bbg[i % 2]!); p.dispatchWorkgroups(Math.ceil(W * H / 64)); }
        p.end();
      });
    }
    return results;
  });
  writeFileSync("/tmp/w42-perf/micro.json", JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
});
