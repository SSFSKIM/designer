// TEMPORARY perf-wave micro-benchmark (not committed): blur tap throughput by kernel form.
import { writeFileSync } from "node:fs";
import { test } from "@playwright/test";
import { openHarness, requireHardwareAdapter } from "../support";

test("@w42-micro2 blur throughput", async ({ page }) => {
  test.setTimeout(300_000);
  requireHardwareAdapter(await openHarness(page));
  const out = await page.evaluate(async (Rarg: number) => {
    const adapter = await navigator.gpu.requestAdapter();
    const device = await adapter!.requestDevice({ requiredFeatures: ["float32-blendable"] as GPUFeatureName[],
      requiredLimits: { maxComputeWorkgroupStorageSize: 32768 } });
    const W = 904, H = 490, R = Rarg, REPS = 10;
    const results: Record<string, number> = {};
    const weights = new Float32Array(2 * R + 1).fill(1 / (2 * R + 1));
    const wbuf = device.createBuffer({ size: weights.byteLength, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
    device.queue.writeBuffer(wbuf, 0, weights);
    const tex = () => device.createTexture({ size: [W, H], format: "rgba32float",
      usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.STORAGE_BINDING });
    const ta = [tex(), tex()];
    const bufs = [0, 1].map(() => device.createBuffer({ size: W * H * 16, usage: GPUBufferUsage.STORAGE }));
    const common = `const R : i32 = ${R}; const W : i32 = ${W}; const H : i32 = ${H};`;
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
    // (i) fragment, textureLoad, clamp, weights from storage
    const fmod = device.createShaderModule({ code: `${common}
@vertex fn vs(@builtin(vertex_index) i : u32) -> @builtin(position) vec4f {
  let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u)); return vec4f(p * 2.0 - 1.0, 0.0, 1.0); }
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var src : texture_2d<f32>;
@fragment fn fs(@builtin(position) p : vec4f) -> @location(0) vec4f {
  let c = vec2i(p.xy); var s = vec4f(0.0);
  for (var k = -R; k <= R; k++) { s += wts[k + R] * textureLoad(src, clamp(c + vec2i(0, k), vec2i(0), vec2i(W - 1, H - 1)), 0); }
  return s; }` });
    const fp = device.createRenderPipeline({ layout: "auto", vertex: { module: fmod, entryPoint: "vs" },
      fragment: { module: fmod, entryPoint: "fs", targets: [{ format: "rgba32float" }] } });
    const fbg = [0, 1].map((i) => device.createBindGroup({ layout: fp.getBindGroupLayout(0),
      entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: ta[i]!.createView() }] }));
    await time("fragment texture V (one pass)", (e) => {
      for (let i = 0; i < REPS; i += 1) {
        const p = e.beginRenderPass({ colorAttachments: [{ view: ta[1 - (i % 2)]!.createView(), loadOp: "clear", storeOp: "store", clearValue: [0, 0, 0, 0] }] });
        p.setPipeline(fp); p.setBindGroup(0, fbg[i % 2]!); p.draw(3); p.end();
      }
    });
    // (ii) compute, buffer, thread per pixel, V and H
    for (const axis of ["V", "H"]) {
      const cmod = device.createShaderModule({ code: `${common}
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var<storage, read> src : array<vec4f>;
@group(0) @binding(2) var<storage, read_write> dst : array<vec4f>;
@compute @workgroup_size(64, 1) fn cs(@builtin(global_invocation_id) g : vec3u) {
  let c = vec2i(g.xy); if (c.x >= W || c.y >= H) { return; }
  var s = vec4f(0.0);
  for (var k = -R; k <= R; k++) {
    let t = clamp(c + ${axis === "V" ? "vec2i(0, k)" : "vec2i(k, 0)"}, vec2i(0), vec2i(W - 1, H - 1));
    s += wts[k + R] * src[t.y * W + t.x]; }
  dst[c.y * W + c.x] = s; }` });
      const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
      const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: { buffer: bufs[i]! } }, { binding: 2, resource: { buffer: bufs[1 - i]! } }] }));
      await time(`compute buffer ${axis}`, (e) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < REPS; i += 1) { p.setBindGroup(0, cbg[i % 2]!); p.dispatchWorkgroups(Math.ceil(W / 64), H); }
        p.end();
      });
    }
    // (iii) compute, texture in, storage texture out, thread per pixel, V
    {
      const cmod = device.createShaderModule({ code: `${common}
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var src : texture_2d<f32>;
@group(0) @binding(2) var dst : texture_storage_2d<rgba32float, write>;
@compute @workgroup_size(8, 8) fn cs(@builtin(global_invocation_id) g : vec3u) {
  let c = vec2i(g.xy); if (c.x >= W || c.y >= H) { return; }
  var s = vec4f(0.0);
  for (var k = -R; k <= R; k++) { s += wts[k + R] * textureLoad(src, clamp(c + vec2i(0, k), vec2i(0), vec2i(W - 1, H - 1)), 0); }
  textureStore(dst, c, s); }` });
      const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
      const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: ta[i]!.createView() }, { binding: 2, resource: ta[1 - i]!.createView() }] }));
      await time("compute texture V", (e) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < REPS; i += 1) { p.setBindGroup(0, cbg[i % 2]!); p.dispatchWorkgroups(Math.ceil(W / 8), Math.ceil(H / 8)); }
        p.end();
      });
    }
    // (iv) compute, buffer, LDS: a workgroup of 128 outputs along the axis, weights in LDS
    for (const axis of ["H", "V"]) {
      const N = 128;
      const cmod = device.createShaderModule({ code: `${common}
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var<storage, read> src : array<vec4f>;
@group(0) @binding(2) var<storage, read_write> dst : array<vec4f>;
var<workgroup> row : array<vec4f, ${N + 2 * R}>;
var<workgroup> kw : array<f32, ${2 * R + 1}>;
fn at(i : i32, j : i32) -> i32 { ${axis === "H" ? "return clamp(j, 0, H - 1) * W + clamp(i, 0, W - 1);" : "return clamp(i, 0, H - 1) * W + clamp(j, 0, W - 1);"} }
@compute @workgroup_size(${N}) fn cs(@builtin(local_invocation_id) l : vec3u, @builtin(workgroup_id) wg : vec3u) {
  let base = i32(wg.x) * ${N} - R; let line = i32(wg.y);
  for (var i = i32(l.x); i < ${N + 2 * R}; i += ${N}) { row[i] = src[at(base + i, line)]; }
  for (var i = i32(l.x); i < ${2 * R + 1}; i += ${N}) { kw[i] = wts[i]; }
  workgroupBarrier();
  let o = i32(wg.x) * ${N} + i32(l.x);
  if (o >= ${axis === "H" ? "W" : "H"}) { return; }
  var s = vec4f(0.0);
  for (var k = 0; k <= 2 * R; k++) { s += kw[k] * row[i32(l.x) + k]; }
  dst[at(o, line)] = s; }` });
      const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
      const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: { buffer: bufs[i]! } }, { binding: 2, resource: { buffer: bufs[1 - i]! } }] }));
      await time(`compute buffer LDS ${axis}`, (e) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < REPS; i += 1) { p.setBindGroup(0, cbg[i % 2]!);
          p.dispatchWorkgroups(Math.ceil((axis === "H" ? W : H) / N), axis === "H" ? H : W); }
        p.end();
      });
    }
    // (v) LDS + register blocking: P outputs per thread, weights zero-padded in LDS
    for (const [axis, P, N] of [["H", 4, 256], ["V", 4, 256], ["H", 2, 128], ["H", 8, 512]] as const) {
      const T = N / P;
      const cmod = device.createShaderModule({ code: `${common}
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var<storage, read> src : array<vec4f>;
@group(0) @binding(2) var<storage, read_write> dst : array<vec4f>;
var<workgroup> row : array<vec4f, ${N + 2 * R}>;
var<workgroup> kw : array<f32, ${2 * R + 1 + 2 * (P - 1)}>;
fn at(i : i32, j : i32) -> i32 { ${axis === "H" ? "return clamp(j, 0, H - 1) * W + clamp(i, 0, W - 1);" : "return clamp(i, 0, H - 1) * W + clamp(j, 0, W - 1);"} }
@compute @workgroup_size(${T}) fn cs(@builtin(local_invocation_id) l : vec3u, @builtin(workgroup_id) wg : vec3u) {
  let base = i32(wg.x) * ${N} - R; let line = i32(wg.y);
  for (var i = i32(l.x); i < ${N + 2 * R}; i += ${T}) { row[i] = src[at(base + i, line)]; }
  for (var i = i32(l.x); i < ${2 * R + 1 + 2 * (P - 1)}; i += ${T}) {
    let k = i - ${P - 1};
    kw[i] = select(0.0, wts[max(k, 0)], k >= 0 && k <= 2 * R); }
  workgroupBarrier();
  var s : array<vec4f, ${P}>;
  let b = i32(l.x) * ${P};
  for (var j = 0; j < 2 * R + ${P}; j++) {
    let v = row[b + j];
    for (var m = 0; m < ${P}; m++) { s[m] += kw[j - m + ${P - 1}] * v; }
  }
  for (var m = 0; m < ${P}; m++) {
    let o = i32(wg.x) * ${N} + b + m;
    if (o < ${axis === "H" ? "W" : "H"}) { dst[at(o, line)] = s[m]; }
  } }` });
      const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
      const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: { buffer: bufs[i]! } }, { binding: 2, resource: { buffer: bufs[1 - i]! } }] }));
      await time(`compute buffer LDS P${P} N${N} ${axis}`, (e) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < REPS; i += 1) { p.setBindGroup(0, cbg[i % 2]!);
          p.dispatchWorkgroups(Math.ceil((axis === "H" ? W : H) / N), axis === "H" ? H : W); }
        p.end();
      });
    }
    // (vi) unrolled variants: symmetric P1, symmetric P2, sliding P4
    const variants: Record<string, { P: number; body: string }> = {
      symP1: { P: 1, body: `
  let c = i32(l.x) + R;
  var s0 = kw[R] * row[c];
  for (var k = 1; k <= R; k++) { s0 += kw[R + k] * (row[c - k] + row[c + k]); }
  out(0, s0);` },
      symP2: { P: 2, body: `
  let c = i32(l.x) * 2 + R;
  let w0 = kw[R];
  var s0 = w0 * row[c]; var s1 = w0 * row[c + 1];
  for (var k = 1; k <= R; k++) { let w = kw[R + k];
    s0 += w * (row[c - k] + row[c + k]); s1 += w * (row[c + 1 - k] + row[c + 1 + k]); }
  out(0, s0); out(1, s1);` },
      symP4: { P: 4, body: `
  let c = i32(l.x) * 4 + R;
  let w0 = kw[R];
  var s0 = w0 * row[c]; var s1 = w0 * row[c + 1]; var s2 = w0 * row[c + 2]; var s3 = w0 * row[c + 3];
  for (var k = 1; k <= R; k++) { let w = kw[R + k];
    s0 += w * (row[c - k] + row[c + k]); s1 += w * (row[c + 1 - k] + row[c + 1 + k]);
    s2 += w * (row[c + 2 - k] + row[c + 2 + k]); s3 += w * (row[c + 3 - k] + row[c + 3 + k]); }
  out(0, s0); out(1, s1); out(2, s2); out(3, s3);` },
      isymP4: { P: 4, body: `
  let c = i32(l.x) + R;
  let w0 = kw[R];
  var s0 = w0 * row[c]; var s1 = w0 * row[c + 64]; var s2 = w0 * row[c + 128]; var s3 = w0 * row[c + 192];
  for (var k = 1; k <= R; k++) { let w = kw[R + k];
    s0 += w * (row[c - k] + row[c + k]); s1 += w * (row[c + 64 - k] + row[c + 64 + k]);
    s2 += w * (row[c + 128 - k] + row[c + 128 + k]); s3 += w * (row[c + 192 - k] + row[c + 192 + k]); }
  o0 = i32(wg.x) * 256 + i32(l.x);
  out(0, s0); out(64, s1); out(128, s2); out(192, s3);` },
      iP4: { P: 4, body: `
  let c = i32(l.x);
  var s0 = vec4f(0.0); var s1 = vec4f(0.0); var s2 = vec4f(0.0); var s3 = vec4f(0.0);
  for (var k = 0; k <= 2 * R; k++) { let w = kw[k];
    s0 += w * row[c + k]; s1 += w * row[c + 64 + k]; s2 += w * row[c + 128 + k]; s3 += w * row[c + 192 + k]; }
  o0 = i32(wg.x) * 256 + i32(l.x);
  out(0, s0); out(64, s1); out(128, s2); out(192, s3);` },
      slideP4: { P: 4, body: `
  let b = i32(l.x) * 4;
  var s0 = vec4f(0.0); var s1 = vec4f(0.0); var s2 = vec4f(0.0); var s3 = vec4f(0.0);
  for (var j = 0; j < 2 * R + 4; j++) { let v = row[b + j];
    s0 += kz[j + 3] * v; s1 += kz[j + 2] * v; s2 += kz[j + 1] * v; s3 += kz[j] * v; }
  out(0, s0); out(1, s1); out(2, s2); out(3, s3);` },
    };
    for (const [name, { P, body }] of Object.entries(variants)) for (const axis of ["H"]) {
      const N = 64 * P; const T = 64;
      const cmod = device.createShaderModule({ code: `${common}
@group(0) @binding(0) var<storage, read> wts : array<f32>;
@group(0) @binding(1) var<storage, read> src : array<vec4f>;
@group(0) @binding(2) var<storage, read_write> dst : array<vec4f>;
var<workgroup> row : array<vec4f, ${N + 2 * R}>;
var<workgroup> kw : array<f32, ${2 * R + 1}>;
var<workgroup> kz : array<f32, ${2 * R + 1 + 6}>;
var<private> line : i32; var<private> o0 : i32;
fn at(i : i32, j : i32) -> i32 { return clamp(j, 0, H - 1) * W + clamp(i, 0, W - 1); }
fn out(m : i32, v : vec4f) { let o = o0 + m; if (o < W) { dst[at(o, line)] = v; } }
@compute @workgroup_size(${T}) fn cs(@builtin(local_invocation_id) l : vec3u, @builtin(workgroup_id) wg : vec3u) {
  let base = i32(wg.x) * ${N} - R; line = i32(wg.y); o0 = i32(wg.x) * ${N} + i32(l.x) * ${P};
  for (var i = i32(l.x); i < ${N + 2 * R}; i += ${T}) { row[i] = src[at(base + i, line)]; }
  for (var i = i32(l.x); i < ${2 * R + 1}; i += ${T}) { kw[i] = wts[i]; }
  for (var i = i32(l.x); i < ${2 * R + 7}; i += ${T}) { let k = i - 3; kz[i] = select(0.0, wts[max(k, 0)], k >= 0 && k <= 2 * R); }
  workgroupBarrier();
  ${body}
}` });
      const cp = device.createComputePipeline({ layout: "auto", compute: { module: cmod, entryPoint: "cs" } });
      const cbg = [0, 1].map((i) => device.createBindGroup({ layout: cp.getBindGroupLayout(0),
        entries: [{ binding: 0, resource: { buffer: wbuf } }, { binding: 1, resource: { buffer: bufs[i]! } }, { binding: 2, resource: { buffer: bufs[1 - i]! } }] }));
      await time(`LDS ${name} ${axis}`, (e) => {
        const p = e.beginComputePass(); p.setPipeline(cp);
        for (let i = 0; i < REPS; i += 1) { p.setBindGroup(0, cbg[i % 2]!); p.dispatchWorkgroups(Math.ceil(W / N), H); }
        p.end();
      });
    }
    results["Mtaps per pass"] = (W * H * (2 * R + 1)) / 1e6;
    return results;
  }, Number(process.env["W42_R"] ?? 32));
  writeFileSync("/tmp/w42-perf/micro2.json", JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
});
