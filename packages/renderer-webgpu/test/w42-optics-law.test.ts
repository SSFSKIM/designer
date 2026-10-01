/**
 * W42 G2 step 3, U3–U4 — the law's stage and its optics lanes as the renderer drives them, on the
 * fake device (`implementation-design.md` §2.1, §2.7, §4, and R2, R4, R6 of §11; §12 item 4).
 *
 * What is settled here, without an adapter:
 *
 * - **R6**: the complete CPU/WGSL offset map of the optics uniform's W42 lanes and its extent.
 * - **Identity**: at the shipped material, and with every law leaf moved but the strength at 0,
 *   the renderer encodes no law pass, allocates no encoded level 0, and writes the W42 lanes as
 *   zeros after an unchanged first 152 floats.
 * - **The stage**: with the law on, the passes per surface are the schedule's, A is bound at 12,
 *   the lanes carry the fold, and a static frame rebuilds nothing; the fold stands it down.
 * - **The duplicates** the design keeps textually separate until the goldens are read on a GPU
 *   (§10): the landed solve, the author tint and the import's chain target are pinned to the
 *   shipped lines, with every difference named.
 *
 * Whether the WGSL compiles and what it draws are U7's, on a real adapter.
 */

import { describe, expect, it } from "vitest";

import { createGradientProvider, linearGradientStops } from "../src/backdrop";
import { BODY_LAW_DECLARED, bodyLawSurfacePlan } from "../src/body-law";
import { bodyLawSchedule, bodyLawSourceExtent } from "../src/body-law-pass";
import {
  DEFAULT_MATERIAL_PROFILE,
  NOMINAL_MATERIAL_POLICY,
  withMaterialOverrides,
  type MaterialPolicyView,
  type MaterialProfilePatch,
} from "../src/material";
import {
  OPTICS_BODY_LAW_LANES,
  OPTICS_UNIFORM_FLOATS,
  packOpticsBodyLaw,
  type OpticsBodyLaw,
} from "../src/passes";
import type { GroupRenderInput } from "../src/render-model";
import { createWebGPURenderer } from "../src/renderer";
import { WGSL_IMPORT_ENCODED_ENTRY, WGSL_IMPORT_PASS, WGSL_OPTICS_PASS } from "../src/wgsl";
import { createFakeGpu, viewOwner, type FakeGpu } from "./harness/fake-gpu";

const LAW: MaterialProfilePatch = {
  bodyLawStrength: 1,
  bodyLawWidthUnit: 1,
  bodyLawEncodedAveraging: 1,
};

const SURFACE = {
  nodeId: "s", family: "fixed-rounded-rect" as const,
  shape: { center: [120, 80] as [number, number], size: [160, 96] as [number, number],
    radii: [20, 20, 20, 20] as [number, number, number, number], smoothing: 0, thickness: 8 },
};

interface Harness {
  readonly gpu: FakeGpu;
  draw(): void;
  lawPasses(): string[];
  /** The stage's compute pass's bind groups, one per dispatch, in order. */
  lawDispatches(): readonly { readonly entries: readonly GPUBindGroupEntry[] }[];
  optics(): Float32Array;
  importUniform(): Float32Array | undefined;
  opticsBinding(binding: number): GPUBindingResource | undefined;
  setGroup(over: Partial<GroupRenderInput>): void;
  setMaterial(patch: MaterialProfilePatch): void;
  removeGroup(): void;
  destroy(): void;
}

function harness(over: {
  patch?: MaterialProfilePatch; sampled?: boolean; policy?: MaterialPolicyView;
  variant?: "regular" | "clear"; dpr?: number; surfaces?: GroupRenderInput["surfaces"];
} = {}): Harness {
  const gpu = createFakeGpu();
  const renderer = createWebGPURenderer({ viewport: {
    widthCss: 240, heightCss: 160, devicePixelRatio: over.dpr ?? 1,
  } });
  renderer.attachDevice(gpu.device, "vitrea");
  renderer.setMaterialProfile(over.patch ?? LAW);
  renderer.setAccessibility(over.policy ?? NOMINAL_MATERIAL_POLICY);
  if (over.sampled !== false) {
    renderer.registerBackdrop(createGradientProvider({ id: "bg", device: gpu.device,
      stops: linearGradientStops([0.1, 0.2, 0.3], [0.5, 0.6, 0.7]), generation: 1 }));
  }
  let group: GroupRenderInput = {
    groupId: "g", surfaces: over.surfaces ?? [SURFACE], refraction: "true", analysisExact: true,
    variant: over.variant ?? "regular",
    ...(over.sampled === false ? {} : { backdropSourceId: "bg" }),
  };
  renderer.setGroup(group);
  let id = 0;
  const opticsPass = () => gpu.passes.find((pass) => pass.label.startsWith("vitrea:pass:optics:"));
  return {
    gpu,
    draw() {
      gpu.reset();
      renderer.drawFrame({ frame: { id: ++id, timeMs: id * 16 }, optics: {} as GPUTextureView,
        highlight: {} as GPUTextureView });
    },
    lawPasses: () => gpu.passes.map((pass) => pass.label)
      .filter((label) => label.startsWith("vitrea:pass:body-law")),
    lawDispatches: () => gpu.passes.find((pass) => pass.label === "vitrea:pass:body-law")
      ?.bindGroups ?? [],
    optics() {
      const writes = gpu.uniformWrites.filter((write) => write.label.includes("uniform:optics"));
      expect(writes).toHaveLength(1);
      return writes[0]!.data;
    },
    importUniform: () =>
      gpu.uniformWrites.find((write) => write.label === "vitrea:uniform:import:bg")?.data,
    opticsBinding(binding) {
      return opticsPass()?.bindGroups[0]?.entries.find((entry) => entry.binding === binding)
        ?.resource;
    },
    setGroup(next) {
      group = { ...group, ...next };
      renderer.setGroup(group);
    },
    setMaterial: (patch) => renderer.setMaterialProfile(patch),
    removeGroup: () => renderer.removeGroup("g"),
    destroy: () => renderer.destroy(),
  };
}

const labelOf = (gpu: FakeGpu, resource: GPUBindingResource | undefined): string =>
  resource === undefined ? "" : gpu.info(viewOwner(resource as GPUTextureView))?.label ?? "";

/**
 * The dispatches one surface's stage encodes, from the schedule (`body-law-pass.ts`): the floor,
 * the decimation where a width is decimated, every width's horizontal and vertical passes, and A.
 */
function expectedDispatches(patch: MaterialProfilePatch, dpr = 1): number {
  const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
  const viewport: readonly [number, number] = [240 * dpr, 160 * dpr];
  const plan = bodyLawSurfacePlan({ centre: SURFACE.shape.center, size: SURFACE.shape.size }, dpr,
    material, bodyLawSourceExtent(viewport, [1, 1, 0, 0]));
  const schedule = bodyLawSchedule(plan);
  return 1 + (schedule.grids.some((grid) => grid.q > 1) ? 1 : 0) +
    (schedule.grids.length > 0 ? 2 : 0) + 1;
}

/** Code lines of a WGSL region: comments dropped, trimmed, empty lines removed. */
function codeLines(source: string, from: string, to: string): string[] {
  const start = source.indexOf(from);
  expect(start, from).toBeGreaterThanOrEqual(0);
  const end = source.indexOf(to, start);
  expect(end, to).toBeGreaterThan(start);
  return source.slice(start, end + to.length)
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .map((line) => line.replace(/\/\/.*$/, "").trim())
    .filter((line) => line.length > 0);
}

describe("W42 R6: the optics uniform's offset map", () => {
  const struct = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("struct OpticsUniforms {"),
    WGSL_OPTICS_PASS.indexOf("};", WGSL_OPTICS_PASS.indexOf("struct OpticsUniforms {")));
  const members: { name: string; offset: number; floats: number }[] = [];
  let offset = 0;
  for (const line of struct.split("\n")) {
    const match = /^\s*(\w+)\s*:\s*(vec4f|array<vec4f,\s*(\d+)>)\s*,/.exec(line);
    if (match === null) continue;
    const floats = match[3] === undefined ? 4 : 4 * Number(match[3]);
    members.push({ name: match[1]!, offset, floats });
    offset += floats;
  }
  const member = (name: string) => members.find((m) => m.name === name);

  it("is vec4-only, with W42's members from 152 and the extent the pass allocates", () => {
    expect(struct.split("\n").filter((line) => /^\s*\w+\s*:/.test(line))).toHaveLength(members.length);
    expect(offset).toBe(OPTICS_UNIFORM_FLOATS);
    expect(OPTICS_UNIFORM_FLOATS).toBe(248);
    expect(member("bodyE3Neutral1")).toEqual({ name: "bodyE3Neutral1", offset: 148, floats: 4 });
    expect(member("bodyLaw")?.offset).toBe(OPTICS_BODY_LAW_LANES.strength);
    expect(member("bodyLawA")?.offset).toBe(OPTICS_BODY_LAW_LANES.size);
    expect(member("bodyLawTone")?.offset).toBe(OPTICS_BODY_LAW_LANES.e3Strength);
    expect(member("bodyE3High0")?.offset).toBe(OPTICS_BODY_LAW_LANES.e3NeutralHigh);
    expect(member("bodyE3High1")?.offset).toBe(OPTICS_BODY_LAW_LANES.e3NeutralHigh + 4);
    expect(member("bodyTable")).toEqual({ name: "bodyTable", offset: 172, floats: 76 });
  });

  it("names each lane where the shader reads it", () => {
    const L = OPTICS_BODY_LAW_LANES;
    // The vec4 lanes, by component.
    expect([L.strength, L.bandPt, L.origin]).toEqual([152, 153, 154]);
    expect(WGSL_OPTICS_PASS).toContain("if (ou.bodyLaw.x > 0.0 && ou.flags.x > 0.5) {");
    expect(WGSL_OPTICS_PASS).toContain("smoothstep(0.0, ou.bodyLaw.y, -d)");
    expect(WGSL_OPTICS_PASS).toContain("let at = p - ou.bodyLaw.zw - vec2f(0.5);");
    expect([L.size, L.landedToneStrength, L.silhouetteAbscissa]).toEqual([156, 158, 159]);
    expect(WGSL_OPTICS_PASS).toContain("let last = vec2i(ou.bodyLawA.xy) - vec2i(1);");
    expect(WGSL_OPTICS_PASS).toContain("let toneStrength = ou.bodyLawA.z;");
    expect(WGSL_OPTICS_PASS).toContain("if (ou.bodyLawA.w > 0.5) {");
    expect([L.e3Strength, L.e3HighStrength, L.tableStrength]).toEqual([160, 161, 162]);
    expect(WGSL_OPTICS_PASS).toContain("let e3 = clamp(ou.bodyLawTone.x, 0.0, 1.0);");
    expect(WGSL_OPTICS_PASS).toContain("if (ou.bodyLawTone.y > 0.0 && level > 150.0) {");
    expect(WGSL_OPTICS_PASS).toContain("let table = clamp(ou.bodyLawTone.z, 0.0, 1.0);");
    // The table's lanes, relative to 172, as the shader indexes them.
    expect(L.tableLevels - L.table).toBe(0);
    expect(WGSL_OPTICS_PASS).toContain("if (level >= body_table_lane(10u))");
    expect(L.tableSpans - L.table).toBe(11);
    expect(WGSL_OPTICS_PASS).toContain("if (span <= body_table_lane(11u))");
    expect(WGSL_OPTICS_PASS).toContain("} else if (span >= body_table_lane(15u)) {");
    expect(L.tableCodes - L.table).toBe(16);
    expect(WGSL_OPTICS_PASS).toContain("let first = 16u + row * 11u;");
    expect(L.tableGains - L.table).toBe(71);
    expect(L.tableScale - L.table).toBe(74);
    expect(WGSL_OPTICS_PASS).toContain("let gain = body_table_lane(74u) * body_law_gain(level,");
    expect(WGSL_OPTICS_PASS).toContain(
      "vec3f(body_table_lane(71u), body_table_lane(72u), body_table_lane(73u)));");
  });

  it("packs every lane of a law, and zeros from 152 without one", () => {
    const law: OpticsBodyLaw = {
      strength: 0.75, bandPt: 20, argument: {} as GPUTextureView, origin: [11, 12], size: [13, 14],
      landedToneStrength: 0.5, silhouetteAbscissa: true, e3Strength: 1, e3HighStrength: 0.25,
      e3NeutralHigh: [161, 177, 193, 209, 225, 241, 254], tableStrength: 1,
      tableLevels: [0, 64, 96, 128, 160, 176, 192, 208, 224, 240, 255],
      tableSpans: [64, 80, 96, 128, 160],
      tableCodes: Array.from({ length: 5 }, (_, r) =>
        Array.from({ length: 11 }, (_, k) => 100 * r + k)) as never,
      chromaGains: [0.9, 1.1, 1.2], chromaScale: 0.8,
    };
    const d = new Float32Array(OPTICS_UNIFORM_FLOATS).fill(-1);
    packOpticsBodyLaw(d, law);
    expect([...d.slice(0, 152)].every((v) => v === -1)).toBe(true);
    expect([...d.slice(152, 172)]).toEqual([...new Float32Array([
      0.75, 20, 11, 12, 13, 14, 0.5, 1, 1, 0.25, 1, 0, 161, 177, 193, 209, 225, 241, 254, 0,
    ])]);
    expect([...d.slice(172, 183)]).toEqual([0, 64, 96, 128, 160, 176, 192, 208, 224, 240, 255]);
    expect([...d.slice(183, 188)]).toEqual([64, 80, 96, 128, 160]);
    expect(d[188 + 11 * 3 + 7]).toBe(307);
    expect([...d.slice(243, 248)]).toEqual([...new Float32Array([0.9, 1.1, 1.2, 0.8, 0])]);
    packOpticsBodyLaw(d, undefined);
    expect([...d.slice(152)].every((v) => v === 0)).toBe(true);
    packOpticsBodyLaw(d, { ...law, strength: 0 });
    expect([...d.slice(152)].every((v) => v === 0)).toBe(true);
  });
});

describe("W42 identity through the renderer", () => {
  it("encodes nothing, allocates nothing and writes zeros at the shipped material", () => {
    const h = harness({ patch: {} });
    h.draw();
    expect(h.lawPasses()).toEqual([]);
    expect(h.gpu.textures.some((t) => t.label.includes(":encoded") || t.label.includes("body-law")))
      .toBe(false);
    expect(h.gpu.buffers.some((b) => b.label.includes("body-law"))).toBe(false);
    // One encoder and one command buffer a frame, as before the law existed.
    expect(h.gpu.encoders).toBe(1);
    expect(h.gpu.submittedBuffers).toBe(1);
    const d = h.optics();
    expect(d).toHaveLength(OPTICS_UNIFORM_FLOATS);
    expect([...d.slice(152)].every((v) => v === 0)).toBe(true);
    expect(h.importUniform()?.[11]).toBe(0);
    expect(labelOf(h.gpu, h.opticsBinding(12))).toBe("vitrea:placeholder");
    h.destroy();
  });

  it("is the shipped frame with every law leaf moved but the strength at 0", () => {
    const base = harness({ patch: {} });
    base.draw();
    const moved = harness({ patch: {
      bodyLawStrength: 0, bodyLawK: [3, 1.5], bodyLawLambda: 0.4, bodyLawNormal: 0.7,
      bodyLawHinge: -1, bodyLawPose: 1, bodyLawKnee: 2, bodyLawEdgeSwap: 1, bodyLawWidthUnit: 2,
      bodyLawEncodedAveraging: 1, bodyE3HighStrength: 1, bodyToneTableStrength: 1,
    } });
    moved.draw();
    expect(moved.lawPasses()).toEqual([]);
    expect([...moved.optics()]).toEqual([...base.optics()]);
    expect(moved.gpu.passes.map((p) => p.label)).toEqual(base.gpu.passes.map((p) => p.label));
    expect([moved.gpu.encoders, moved.gpu.submittedBuffers]).toEqual([1, 1]);
    base.destroy();
    moved.destroy();
  });
});

describe("W42 stage and lanes with the law on", () => {
  it("runs the schedule's dispatches in one compute pass, binds A at 12 and packs the fold", () => {
    const h = harness();
    h.draw();
    expect(h.lawPasses()).toEqual(["vitrea:pass:body-law"]);
    expect(h.lawDispatches()).toHaveLength(expectedDispatches(LAW));
    // In the frame's own encoder: the law adds a compute pass, not a command buffer.
    expect([h.gpu.encoders, h.gpu.submittedBuffers]).toEqual([1, 1]);
    // The last dispatch writes A.
    expect(labelOf(h.gpu, h.lawDispatches().at(-1)!.entries.find((e) => e.binding === 6)!.resource))
      .toBe("vitrea:body-law:g:A");
    expect(h.gpu.textures.some((t) => t.label === "vitrea:pyramid:bg:encoded")).toBe(true);
    // The gradient is an encoded sRGB source: the import passes its value through.
    expect(h.importUniform()?.[11]).toBe(1);
    expect(labelOf(h.gpu, h.opticsBinding(12))).toBe("vitrea:body-law:g:A");
    const d = h.optics();
    const L = OPTICS_BODY_LAW_LANES;
    expect(d[L.strength]).toBe(1);
    expect(d[L.bandPt]).toBe(BODY_LAW_DECLARED.activeBandPt);
    const origin = [d[L.origin], d[L.origin + 1]];
    const size = [d[L.size], d[L.size + 1]];
    // A covers the surface's own rect, which contains its box (40..200 × 32..128).
    expect(origin[0]).toBeLessThanOrEqual(40);
    expect(origin[1]).toBeLessThanOrEqual(32);
    expect(origin[0]! + size[0]!).toBeGreaterThanOrEqual(200);
    expect(origin[1]! + size[1]!).toBeGreaterThanOrEqual(128);
    expect(d[L.landedToneStrength]).toBeCloseTo(DEFAULT_MATERIAL_PROFILE.backdropToneMax, 6);
    expect(d[L.e3Strength]).toBe(0);
    // No older lane changes owner: the first 152 floats are the law-off frame's.
    const off = harness({ patch: { ...LAW, bodyLawStrength: 0 } });
    off.draw();
    expect([...d.slice(0, 152)]).toEqual([...off.optics().slice(0, 152)]);
    h.destroy();
    off.destroy();
  });

  it("rebuilds nothing on a static frame, and again after a frame that never reached the queue", () => {
    const h = harness();
    h.draw();
    const a = labelOf(h.gpu, h.opticsBinding(12));
    h.draw();
    expect(h.lawPasses()).toEqual([]);
    expect(labelOf(h.gpu, h.opticsBinding(12))).toBe(a);
    h.setGroup({ surfaces: [{ ...SURFACE, shape: { ...SURFACE.shape, center: [124, 80] } }] });
    h.gpu.failNextFinish();
    expect(() => h.draw()).toThrow("encode failed");
    h.draw();
    expect(h.lawDispatches()).toHaveLength(expectedDispatches(LAW));
    h.destroy();
  });

  it("draws the receded pose flat, with one narrow level", () => {
    const patch = { ...LAW, bodyLawPose: 1 };
    const h = harness({ patch });
    h.draw();
    expect(h.optics()[OPTICS_BODY_LAW_LANES.bandPt]).toBe(0);
    expect(h.lawDispatches()).toHaveLength(expectedDispatches(patch));
    h.destroy();
  });

  it("hands E3, the F extension and the table over only under the law", () => {
    const patch: MaterialProfilePatch = { ...LAW, bodyE3Strength: 1, bodyE3HighStrength: 0.5,
      bodyToneTableStrength: 1, bodyToneChromaScale: 0.7 };
    const h = harness({ patch });
    h.draw();
    const d = h.optics();
    const L = OPTICS_BODY_LAW_LANES;
    expect([d[L.e3Strength], d[L.e3HighStrength], d[L.tableStrength], d[L.tableScale]])
      .toEqual([...new Float32Array([1, 0.5, 1, 0.7])]);
    h.destroy();
  });

  it.each([
    ["Reduce Transparency", { patch: LAW, policy: { ...NOMINAL_MATERIAL_POLICY, frost: "increased",
      refraction: "reduced", occlusion: "increased" } as MaterialPolicyView }],
    ["forced colours", { patch: LAW, policy: { ...NOMINAL_MATERIAL_POLICY, occlusion: "opaque" } as
      MaterialPolicyView }],
    ["the clear variant", { patch: LAW, variant: "clear" as const }],
    ["an unsampled group", { patch: LAW, sampled: false }],
  ])("stands down under %s", (_name, over) => {
    const h = harness(over);
    h.draw();
    expect(h.lawPasses()).toEqual([]);
    expect([...h.optics().slice(152)].every((v) => v === 0)).toBe(true);
    h.destroy();
  });

  it("keeps the law under Increase Contrast alone, which lifts no occlusion", () => {
    const h = harness({ policy: { ...NOMINAL_MATERIAL_POLICY, border: "strong",
      ambientTint: "reduced", foreground: "near-monochrome" } });
    h.draw();
    expect(h.lawPasses().length).toBeGreaterThan(0);
    expect(h.optics()[OPTICS_BODY_LAW_LANES.strength]).toBe(1);
    h.destroy();
  });

  it("releases A, its tiles and the encoded level 0 when the law or the group goes", () => {
    const h = harness();
    h.draw();
    const stage = () => h.gpu.textures.filter((t) => t.label.startsWith("vitrea:body-law:"));
    expect(stage().length).toBeGreaterThan(0);
    h.setMaterial({ ...LAW, bodyLawStrength: 0 });
    h.draw();
    expect(stage().every((t) => t.destroyed)).toBe(true);
    const encoded = h.gpu.textures.filter((t) => t.label === "vitrea:pyramid:bg:encoded");
    expect(encoded.every((t) => t.destroyed)).toBe(true);
    h.setMaterial(LAW);
    h.draw();
    expect(stage().some((t) => !t.destroyed)).toBe(true);
    h.removeGroup();
    expect(stage().every((t) => t.destroyed)).toBe(true);
    h.destroy();
  });

  it("gives every member of a close group its own footprint, drawn into one A", () => {
    const capsule = (id: string, x: number) => ({
      nodeId: id, family: "fixed-rounded-rect" as const,
      shape: { center: [x, 80] as [number, number], size: [44, 44] as [number, number],
        radii: [22, 22, 22, 22] as [number, number, number, number], smoothing: 0, thickness: 8 },
    });
    const h = harness({ surfaces: [capsule("a", 70), capsule("b", 126), capsule("c", 182)] });
    h.draw();
    expect(h.lawPasses()).toEqual(["vitrea:pass:body-law"]);
    // One floor job per member, and one composite over all three into one A.
    const floor = h.gpu.uniformWrites.find((w) => w.label === "vitrea:uniform:body-law:g:floor")!;
    expect(floor.data[2]).toBe(3);
    const composite = h.gpu.uniformWrites.find((w) => w.label === "vitrea:uniform:body-law:g:composite")!;
    expect(composite.data[8]).toBe(3);
    const writesA = h.lawDispatches().filter((group) => group.entries.some((e) =>
      e.binding === 6 && labelOf(h.gpu, e.resource) === "vitrea:body-law:g:A"));
    expect(writesA).toHaveLength(1);
    h.destroy();
  });

  it("releases a removed group's own buffers while another law group lives on", () => {
    // A static backdrop rebuilds nothing, so nothing but the removal can release them.
    const gpu = createFakeGpu();
    const renderer = createWebGPURenderer({ viewport: { widthCss: 240, heightCss: 160,
      devicePixelRatio: 1 } });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.setMaterialProfile(LAW);
    renderer.setAccessibility(NOMINAL_MATERIAL_POLICY);
    renderer.registerBackdrop(createGradientProvider({ id: "bg", device: gpu.device,
      stops: linearGradientStops([0.1, 0.2, 0.3], [0.5, 0.6, 0.7]), generation: 1 }));
    for (const [groupId, x] of [["g", 70], ["h", 170]] as const) {
      renderer.setGroup({ groupId, refraction: "true", analysisExact: true, variant: "regular",
        backdropSourceId: "bg",
        surfaces: [{ ...SURFACE, nodeId: groupId, shape: { ...SURFACE.shape, center: [x, 80],
          size: [60, 44] } }] });
    }
    const draw = (id: number) => renderer.drawFrame({ frame: { id, timeMs: id * 16 },
      optics: {} as GPUTextureView, highlight: {} as GPUTextureView });
    draw(1);
    const own = (groupId: string) =>
      gpu.buffers.filter((b) => b.label.includes(`:body-law:${groupId}:`));
    expect(own("h").length).toBeGreaterThanOrEqual(5);
    renderer.removeGroup("h");
    draw(2);
    expect(own("h").every((b) => b.destroyed)).toBe(true);
    expect(own("g").some((b) => !b.destroyed)).toBe(true);
    expect(gpu.textures.filter((t) => t.label === "vitrea:body-law:h:A").every((t) => t.destroyed))
      .toBe(true);
    renderer.destroy();
  });

  it("destroys no texture a pass of the frame binds before the frame is submitted", () => {
    // Two law groups whose second needs larger atlases than the first: the growth must not take
    // the first group's atlases away from its pass, which is still in the unsubmitted encoder.
    const gpu = createFakeGpu();
    const renderer = createWebGPURenderer({ viewport: { widthCss: 240, heightCss: 160,
      devicePixelRatio: 1 } });
    renderer.attachDevice(gpu.device, "vitrea");
    renderer.setMaterialProfile(LAW);
    renderer.setAccessibility(NOMINAL_MATERIAL_POLICY);
    renderer.registerBackdrop(createGradientProvider({ id: "bg", device: gpu.device,
      stops: linearGradientStops([0.1, 0.2, 0.3], [0.5, 0.6, 0.7]), generation: 1 }));
    const group = (groupId: string, size: [number, number], x: number): GroupRenderInput => ({
      groupId, refraction: "true", analysisExact: true, variant: "regular", backdropSourceId: "bg",
      surfaces: [{ ...SURFACE, nodeId: groupId, shape: { ...SURFACE.shape, center: [x, 80], size } }],
    });
    renderer.setGroup(group("small", [44, 44], 50));
    renderer.setGroup(group("large", [120, 96], 160));
    const stale: string[] = [];
    const submit = gpu.device.queue.submit.bind(gpu.device.queue);
    gpu.device.queue.submit = (buffers) => {
      for (const pass of gpu.passes) {
        for (const bindGroup of pass.bindGroups) {
          for (const entry of bindGroup.entries) {
            const record = (entry.resource as { __texture?: GPUTexture }).__texture === undefined
              ? undefined : gpu.info(viewOwner(entry.resource as GPUTextureView));
            if (record?.destroyed === true) stale.push(`${pass.label}: ${record.label}`);
          }
        }
      }
      submit(buffers);
    };
    renderer.drawFrame({ frame: { id: 1, timeMs: 16 }, optics: {} as GPUTextureView,
      highlight: {} as GPUTextureView });
    expect(stale).toEqual([]);
    // The atlases the growth replaced go once the frame is submitted.
    const atlases = gpu.textures.filter((t) => t.label.startsWith("vitrea:body-law:atlas:"));
    expect(atlases.length).toBeGreaterThan(4);
    expect(atlases.filter((t) => !t.destroyed)).toHaveLength(4);
    renderer.destroy();
  });

  it("fills A over the whole group rect before any member draws, receded and unrefracted (R2)", () => {
    // Receded, a member's footprint is its box plus one device px, so the union's neck between
    // close capsules lies outside every footprint. What those pixels read is A's initial fill, the
    // captured backdrop — the rehearsal's A_out = B — provided A covers the union at all.
    const capsule = (id: string, x: number) => ({
      nodeId: id, family: "fixed-rounded-rect" as const,
      shape: { center: [x, 80] as [number, number], size: [44, 44] as [number, number],
        radii: [22, 22, 22, 22] as [number, number, number, number], smoothing: 0, thickness: 8 },
    });
    const h = harness({ patch: { ...LAW, bodyLawPose: 1 },
      surfaces: [capsule("a", 70), capsule("b", 126), capsule("c", 182)] });
    h.setGroup({ refraction: "none" });
    h.draw();
    // The composite reads the encoded level 0 wherever no member's footprint owns the texel.
    const composite = h.lawDispatches().at(-1)!;
    const init = composite.entries.find((e) => e.binding === 3)!.resource;
    expect(labelOf(h.gpu, init)).toBe("vitrea:pyramid:bg:encoded");
    const d = h.optics();
    const L = OPTICS_BODY_LAW_LANES;
    const [x, y, w, hh] = [d[L.origin]!, d[L.origin + 1]!, d[L.size]!, d[L.size + 1]!];
    // Every member's box, and so the union between them, lies inside A.
    expect(x).toBeLessThanOrEqual(48);
    expect(y).toBeLessThanOrEqual(58);
    expect(x + w).toBeGreaterThanOrEqual(204);
    expect(y + hh).toBeGreaterThanOrEqual(102);
    expect(d[L.bandPt]).toBe(0);
    h.destroy();
  });
});

describe("W42 duplicates, pinned to the shipped lines they copy (§10)", () => {
  const fsOptics = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("fn fs_optics("));
  const landed = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("fn body_law_landed_solve("));
  const tinted = WGSL_OPTICS_PASS.slice(WGSL_OPTICS_PASS.indexOf("fn body_law_tinted("));

  it("the landed solve is the shipped solve with the tone, the mean and the backdrop at dec(A)", () => {
    const shipped = codeLines(fsOptics, "var toneAdapt = 0.0;",
      "colour = body_chroma_retention(colour, backdrop, ou.bodyChroma.x);");
    const copy = codeLines(landed, "var toneAdapt = 0.0;",
      "return body_chroma_retention(colour, c, ou.bodyChroma.x);");
    const collapse = shipped.indexOf("var toneTarget = toneColour.rgb;");
    expect(shipped.slice(collapse, collapse + 4)).toEqual([
      "var toneTarget = toneColour.rgb;",
      "if (ou.flags.x > 0.5 || domMaterial) {",
      "toneTarget = mix(toneTarget, backdrop, clamp(ou.toneRowThick.w, 0.0, 1.0));",
      "}",
    ]);
    const expected = [...shipped.slice(0, collapse), "let toneTarget = c;",
      ...shipped.slice(collapse + 4)].map((line) => line
      // The declared differences, and nothing else: the tone strength is the law's own lane
      // (no measured-tone gate), the abscissa and the mean are dec(A)'s, the collapse target is
      // dec(A) whatever the transmission, presence is the caller's, and dec(A) is the backdrop.
      .replace("if (ou.toneAdapt.w > 0.0) {", "if (toneStrength > 0.0) {")
      .replaceAll("toneColour.w", "level")
      .replace("let presentAlpha = adaptedAlpha * mat;", "let presentAlpha = adaptedAlpha;")
      .replace("var colour = mix(backdrop, adapted, presentAlpha);",
        "let colour = mix(c, adapted, presentAlpha);")
      .replace("colour = body_chroma_retention(colour, backdrop, ou.bodyChroma.x);",
        "return body_chroma_retention(colour, c, ou.bodyChroma.x);"));
    expect(copy).toEqual(expected);
    expect(landed).toContain("let toneStrength = ou.bodyLawA.z;");
    expect(landed).toContain("let toneLinearMean = dot(c, LAW_LUMA);");
  });

  it("the tint is the shipped sampled-branch tint, evaluated on any body", () => {
    const shipped = codeLines(fsOptics, "if (tintK > 0.0) {",
      "colour = srgb_to_linear(mix(encodedMaterial, encodedLayer, vec3f(s)));");
    const copy = codeLines(tinted, "fn body_law_tinted(", "return mix(encodedMaterial, encodedLayer, vec3f(tintK));");
    const pairs: readonly (readonly [string, string])[] = [
      // bodyAlpha is 1 on the sampled branch, the only one the law runs on.
      ["let u = bodyAlpha * dot(colour, vec3f(0.2126, 0.7152, 0.0722)) + (1.0 - bodyAlpha) * toneColour.w;",
        "let u = dot(c, vec3f(0.2126, 0.7152, 0.0722));"],
      ["let grip = clamp(ou.seed.w, 0.0, 1.0) * clamp(ou.tone.z, 0.0, 1.0) *",
        "let grip = clamp(ou.seed.w, 0.0, 1.0) * clamp(ou.tone.z, 0.0, 1.0) *"],
      ["(1.0 - toneAdapt * (1.0 - clamp(ou.rim.w, 0.0, 1.0)));",
        "(1.0 - toneAdapt * (1.0 - clamp(ou.rim.w, 0.0, 1.0)));"],
      ["let shade = mix(1.0, clamp(mix(ou.tone.x, ou.tone.y, clamp(u, 0.0, 1.0)), 0.0, 1.0), grip);",
        "let shade = mix(1.0, clamp(mix(ou.tone.x, ou.tone.y, clamp(u, 0.0, 1.0)), 0.0, 1.0), grip);"],
      ["var seed = ou.seed.rgb;", "var seed = ou.seed.rgb;"],
      ["if (ou.rim.z < 1.0) {", "if (ou.rim.z < 1.0) {"],
      ["let neutral = max(seed.r, max(seed.g, seed.b));", "let neutral = max(seed.r, max(seed.g, seed.b));"],
      ["seed = mix(vec3f(neutral), seed, clamp(ou.rim.z, 0.0, 1.0));",
        "seed = mix(vec3f(neutral), seed, clamp(ou.rim.z, 0.0, 1.0));"],
      ["let layer = seed * shade;", "let layer = seed * shade;"],
      ["let encodedMaterial = linear_to_srgb(clamp(colour, vec3f(0.0), vec3f(1.0)));",
        "let encodedMaterial = linear_to_srgb(clamp(c, vec3f(0.0), vec3f(1.0)));"],
      ["let encodedLayer = linear_to_srgb(layer);", "let encodedLayer = linear_to_srgb(layer);"],
      ["if (ou.flags.x > 0.5) {", "return mix(encodedMaterial, encodedLayer, vec3f(tintK));"],
      // The shipped sampled branch decodes the same mix; the delta is taken in encoded codes.
      ["colour = srgb_to_linear(mix(encodedMaterial, encodedLayer, vec3f(s)));",
        "return mix(encodedMaterial, encodedLayer, vec3f(tintK));"],
    ];
    // The shipped lines in their order; the copy computes the encoded material first, so that an
    // untinted pixel returns it before any of the paint's arithmetic.
    let si = 0;
    for (const [ship, dup] of pairs) {
      si = shipped.indexOf(ship, si);
      expect(si, ship).toBeGreaterThanOrEqual(0);
      expect(copy, dup).toContain(dup);
    }
    expect(copy.indexOf("if (tintK <= 0.0) { return encodedMaterial; }"))
      .toBe(copy.indexOf("let encodedMaterial = linear_to_srgb(clamp(c, vec3f(0.0), vec3f(1.0)));") + 1);
    // The shipped coverage the law's copy reads is 's = tintK'.
    expect(shipped).toContain("let s = tintK;");
  });

  it("the import's chain target is fs_import's arithmetic, line for line", () => {
    const shipped = codeLines(WGSL_IMPORT_PASS, "let uv = in.uv * iu.fit.xy + iu.fit.zw;",
      "return vec4f(max(colour, vec3f(0.0)) * alpha, alpha);");
    const copy = codeLines(WGSL_IMPORT_ENCODED_ENTRY, "let uv = in.uv * iu.fit.xy + iu.fit.zw;",
      "return out;");
    let at = 0;
    for (const line of shipped.slice(0, -1)) {
      at = copy.indexOf(line, at);
      expect(at, line).toBeGreaterThanOrEqual(0);
    }
    expect(copy).toContain("out.chain = vec4f(max(colour, vec3f(0.0)) * alpha, alpha);");
    expect(copy).toContain("out.encoded = vec4f(encoded * alpha, alpha);");
  });
});
