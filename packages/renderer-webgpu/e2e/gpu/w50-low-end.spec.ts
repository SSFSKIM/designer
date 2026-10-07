/** W50: live uniforms, preserved solve stand-downs, and production WGSL precision. */
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { backdropToneResponse, DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../src/material";
import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

const chart = { lowEndStrength: 1,
  lowEnd44: [20 / 255, 28 / 255, 48 / 255, 60 / 255] as const,
  lowEnd96: [21 / 255, 29 / 255, 49 / 255, 61 / 255] as const,
  lowEnd160: [22 / 255, 30 / 255, 50 / 255, 62 / 255] as const };

test("@gpu W50 chart reaches pixels and preserves every old solve gate", async ({ page }) => {
  requireHardwareAdapter(await openHarness(page));
  const draw = async (patch: Record<string, unknown>, scene = "w36-black",
    options?: Record<string, unknown>) => [...decodeCapture(await page.evaluate(([s, p, o]) =>
    window.vitrea.renderScene(s, undefined, p, o), [scene, patch, options] as const)).data];
  const base = { backdropToneLow: 0, backdropToneHigh: 0.0001, ...chart };
  const on = await draw(base);
  const off = await draw({ ...base, lowEndStrength: 0 });
  expect(on).not.toEqual(off);
  // This scene's physical span is64: interpolated black is20.3846 codes, quantised20.
  expect(on[(50 * 160 + 80) * 4]).toBe(20);
  expect(await draw({ ...base, lowEndStrength: 0, lowEnd44: [1, 1, 1, 1] })).toEqual(off);
  for (const disabled of [
    { backdropToneResponseStrength: 0 },
    { optics: { regular: { tintAlpha: 0 } }, sizeOcclusionGain: 0 },
    { backdropToneLow: 0.5, backdropToneHigh: 0.6, backdropToneSizeBias: 0 },
  ]) {
    expect(await draw({ ...base, ...disabled })).toEqual(await draw({ ...base, ...disabled, lowEndStrength: 0 }));
  }
  expect(await draw(base, "w36-no-tone"))
    .toEqual(await draw({ ...base, lowEndStrength: 0 }, "w36-no-tone"));
  const policy = { accessibility: { glass: "material", frost: "nominal",
    refraction: "nominal", occlusion: "nominal", border: "nominal",
    ambientTint: "reduced", foreground: "adaptive" } };
  expect(await draw(base, "w36-black", policy))
    .toEqual(await draw({ ...base, lowEndStrength: 0 }, "w36-black", policy));
});

test("@gpu W50 production chart agrees with CPU within 0.001 encoded code", async ({ page }) => {
  requireHardwareAdapter(await openHarness(page));
  const source = readFileSync(new URL("../../src/wgsl/optics.ts", import.meta.url), "utf8");
  // Extract executable production functions, not a test-authored WGSL mirror.
  const functionText = (name: string): string => {
    const start = source.indexOf(`fn ${name}(`);
    if (start < 0) throw new Error(`Missing production function ${name}`);
    let depth = 0;
    const brace = source.indexOf("{", start);
    for (let i = brace; i < source.length; i++) {
      if (source[i] === "{") depth++;
      if (source[i] === "}" && --depth === 0) return source.slice(start, i + 1);
    }
    throw new Error(`Unclosed production function ${name}`);
  };
  const profile = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, chart);
  const shader = `
struct Params { toneRowThin:vec4f, toneRowThick:vec4f, toneAnchor:vec4f,
  toneExtra:vec4f, lowEnd44:vec4f, lowEnd96:vec4f, lowEnd160:vec4f }
@group(0) @binding(0) var<uniform> ou: Params;
@group(0) @binding(1) var<storage,read> inputs: array<vec4f>;
@group(0) @binding(2) var<storage,read_write> outputs: array<f32>;
${["srgb_encode", "srgb_decode", "tone_response", "low_end_response"].map(functionText).join("\n")}
@compute @workgroup_size(64) fn main(@builtin(global_invocation_id) id:vec3u) {
  if (id.x >= arrayLength(&inputs)) { return; }
  let v=inputs[id.x];
  outputs[id.x]=srgb_encode(low_end_response(v.x,v.y,v.z,v.w))*255.0;
}`;
  const params = [...profile.backdropToneResponseThin, 1,
    ...profile.backdropToneResponseThick, 0, ...profile.backdropToneAnchorX, 0,
    0, 0, 0, 0, ...chart.lowEnd44, ...chart.lowEnd96, ...chart.lowEnd160];
  const inputs: number[] = [], expected: number[] = [];
  for (const span of [32, 44, 70, 96, 128, 160, 224]) {
    const thickness = Math.min(1, Math.max(0, (span - 32) / 64));
    for (let i = 0; i < 4096; i++) {
      const x = i / (64 * 255), far = span > 96 ? 0.007 : 0;
      inputs.push(x, span, thickness, far);
      const linear = backdropToneResponse(x, thickness, profile, far, span);
      expected.push(255 * (linear <= 0.0031308 ? linear * 12.92 : 1.055 * linear ** (1 / 2.4) - 0.055));
    }
  }
  const actual = await page.evaluate(async ({ shader, params, inputs }) => {
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("Missing adapter");
    const device = await adapter.requestDevice();
    const make = (data: number[], usage: GPUBufferUsageFlags) => {
      const buffer = device.createBuffer({ size: data.length * 4, usage, mappedAtCreation: true });
      new Float32Array(buffer.getMappedRange()).set(data); buffer.unmap(); return buffer;
    };
    const uniform = make(params, GPUBufferUsage.UNIFORM);
    const input = make(inputs, GPUBufferUsage.STORAGE);
    const size = inputs.length;
    const output = device.createBuffer({ size, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC });
    const readback = device.createBuffer({ size, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST });
    const pipeline = await device.createComputePipelineAsync({ layout: "auto",
      compute: { module: device.createShaderModule({ code: shader }), entryPoint: "main" } });
    const bind = device.createBindGroup({ layout: pipeline.getBindGroupLayout(0), entries:
      [uniform, input, output].map((buffer, binding) => ({ binding, resource: { buffer } })) });
    const encoder = device.createCommandEncoder(), pass = encoder.beginComputePass();
    pass.setPipeline(pipeline); pass.setBindGroup(0, bind); pass.dispatchWorkgroups(Math.ceil(inputs.length / 256)); pass.end();
    encoder.copyBufferToBuffer(output, 0, readback, 0, size); device.queue.submit([encoder.finish()]);
    await readback.mapAsync(GPUMapMode.READ);
    const result = [...new Float32Array(readback.getMappedRange())];
    readback.unmap(); [uniform, input, output, readback].forEach(b => b.destroy()); device.destroy();
    return result;
  }, { shader, params, inputs });
  expect(actual).toHaveLength(expected.length);
  let worst = 0;
  for (let i = 0; i < expected.length; i++) {
    expect(Number.isFinite(actual[i])).toBe(true);
    worst = Math.max(worst, Math.abs(actual[i]! - expected[i]!));
  }
  expect(worst).toBeLessThanOrEqual(0.001);
});
