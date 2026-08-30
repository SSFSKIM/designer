/**
 * What the shaders must be, checked structurally.
 *
 * There is no WGSL compiler in a Node unit test, so this file cannot say "the
 * shader compiles" — `e2e/gpu/` does that on a real adapter, and where no adapter
 * exists it is the honest gap in the report. What it *can* say, and what matters
 * most, is that the strings the renderer ships have the properties the contracts
 * name:
 *
 *  - **X8 rider 2** — the field pass has exactly one field call site and it adds
 *    the level-set offset. There is no second path for a concentric child, so the
 *    instantiated-shape path the rider rules out is not expressible.
 *  - **The kernels are `@vitrea/geometry`'s, verbatim** — the fingerprinted
 *    strings S2 benchmarked, spliced in unchanged, so the cost and precision
 *    results transfer with them.
 *  - **X5** — one transfer function, defined once in the prelude, which every
 *    module includes.
 *  - **X7** — the WGSL marker core's bundle test greps for is present.
 */

import { describe, expect, it } from "vitest";
import { fingerprint, WGSL_RSUP, WGSL_RSUPN } from "@vitrea/geometry";

import {
  allShaderSource,
  analysisModule,
  chainModule,
  crossCheckKernelModule,
  fieldModule,
  fieldPassSource,
  highlightModule,
  importModule,
  opticsModule,
  WGSL_FIELD_KERNELS,
  WGSL_INSTANCE_STRUCT,
  WGSL_PRELUDE,
  WGSL_RSUP_GRAD,
  WGSL_RSUPN_GRAD,
  WGSL_SMOOTH_UNION,
} from "../src/wgsl";
import { ANALYSIS_GRID, ANALYSIS_WORKGROUP } from "../src/wgsl/analysis";
import { INSTANCE_FLOATS } from "../src/instances";

const MODULES: readonly (readonly [string, string])[] = [
  ["field:rsupn", fieldModule("rsupn")],
  ["field:rsup", fieldModule("rsup")],
  ["import:sampled", importModule("sampled")],
  ["import:external", importModule("external")],
  ["chain", chainModule()],
  ["analysis", analysisModule()],
  ["optics", opticsModule()],
  ["highlight", highlightModule()],
  ["cross-check", crossCheckKernelModule()],
];

describe("every module", () => {
  it("carries the prelude, so there is one transfer function and one vertex stage", () => {
    for (const [name, source] of MODULES) {
      expect(source, name).toContain("fn linear_to_srgb");
      expect(source, name).toContain("fn vs_fullscreen");
    }
  });

  it("declares each function exactly once", () => {
    // Concatenating the prelude twice, or splicing a kernel into a module that
    // already had it, fails to compile with a message about redefinition — cheap
    // to catch here and confusing to debug on a device.
    for (const [name, source] of MODULES) {
      const declarations = source.match(/^fn\s+(\w+)/gm) ?? [];
      expect(new Set(declarations).size, name).toBe(declarations.length);
    }
  });

  it("has no stray backtick, which would terminate its TypeScript literal", () => {
    // Learned the hard way: a backtick inside a WGSL comment ends the template
    // literal and the file stops parsing several functions later.
    for (const [name, source] of MODULES) {
      expect(source.includes("`"), name).toBe(false);
    }
  });

  it("has balanced braces", () => {
    for (const [name, source] of MODULES) {
      const open = (source.match(/{/g) ?? []).length;
      const close = (source.match(/}/g) ?? []).length;
      expect(open, name).toBe(close);
    }
  });
});

describe("the field kernels come from @vitrea/geometry unchanged", () => {
  it("splices in the exact fingerprinted strings S2 benchmarked", () => {
    // The cost figures (0.0264 and 0.0097 ns/eval/px) and the f32 result belong to
    // these strings. A reformatted copy would carry neither.
    expect(fieldPassSource("rsupn")).toContain(WGSL_RSUPN);
    expect(fieldPassSource("rsup")).toContain(WGSL_RSUP);
    expect(WGSL_FIELD_KERNELS).toContain(WGSL_RSUPN);
    expect(WGSL_FIELD_KERNELS).toContain(WGSL_RSUP);
  });

  it("pins the fingerprints geometry's own sync test pins", () => {
    // Restated here so a change to geometry's WGSL fails this package's suite too,
    // rather than only geometry's.
    expect(fingerprint(WGSL_RSUPN)).toBe("9c24e278");
    expect(fingerprint(WGSL_RSUP)).toBe("13c5190d");
  });

  it("carries the normalization's anchor into the gradient kernel too", () => {
    // `sd_rsupn_grad` is a port of `rsupnFieldAndGradient`, so it has to select
    // the same arm AND differentiate the arm it selected. Reading `dRdt / rho`
    // here while the value kernel reads the anchored form would put the shipped
    // normal out of step with the shipped depth, and every pass downstream
    // consumes the two as one sample.
    expect(WGSL_RSUPN).toContain("select(dRdt / R, dRdt * inv * sqrt(r2), sqrt(r2) >= R)");
    expect(WGSL_RSUPN_GRAD).toContain("let atRho = rho >= R;");
    expect(WGSL_RSUPN_GRAD).toContain("select(dRdt / R, dRdt * inv * rho, atRho)");
    expect(WGSL_RSUPN_GRAD).toContain("select(dRdcx, drhodcx, atRho)");
    expect(WGSL_RSUPN_GRAD).toContain("select(dRdcy, drhodcy, atRho)");
  });

  it("compiles the same kernels into the cross-check as into the pass", () => {
    // Decision Log #20's check would prove nothing about the shipped shader if it
    // compiled a separate copy of the algebra.
    expect(crossCheckKernelModule()).toContain(WGSL_RSUP);
    expect(crossCheckKernelModule()).toContain(WGSL_RSUPN);
  });
});

describe("X8 rider 2 — a concentric child is a level set, with no second path", () => {
  const source = fieldPassSource("rsupn");

  it("evaluates the field exactly once, and adds the inset there", () => {
    // One declaration plus one call site, and nothing else.
    expect(source.match(/sd_rsupn_grad\(/g) ?? []).toHaveLength(2);
    expect(source.match(/^fn sd_rsupn_grad\(/gm) ?? []).toHaveLength(1);
    expect(source).toContain("f.d + s.inset");
  });

  it("passes the instance's own half/re/k — which the CPU fills with the parent's", () => {
    expect(source).toContain("FIELD_FN(p - s.centre, s.half, s.re, k, s.k4)".replace("FIELD_FN", "sd_rsupn_grad"));
  });

  it("has no branch on the offset anywhere", () => {
    // A branch would be a second path, and a second path is what the rider rules
    // out. `inset` is 0 for an ordinary surface, so one expression serves both.
    const arithmetic = source.replace(/\/\/[^\n]*/g, "");
    expect(arithmetic.match(/s\.inset/g) ?? []).toHaveLength(1);
    expect(arithmetic).not.toMatch(/if\s*\([^)]*inset/);
    expect(arithmetic).not.toMatch(/select\([^)]*inset/);
  });

  it("holds for family C as well, so the governor's step keeps the rider", () => {
    const c = fieldPassSource("rsup");
    expect(c.match(/sd_rsup_grad\(/g) ?? []).toHaveLength(2);
    expect(c).toContain("f.d + s.inset");
  });
});

describe("the instance struct", () => {
  it("declares the six derived floats the buffer widens by", () => {
    for (const name of ["re", "k0", "k1", "k2", "k3", "k4"]) {
      expect(WGSL_INSTANCE_STRUCT).toContain(name);
    }
  });

  it("declares X8's geometry plus the render channels, and pads to a legal stride", () => {
    for (const name of ["centre", "half", "inset", "thick", "press", "glow", "lensDepth"]) {
      expect(WGSL_INSTANCE_STRUCT).toContain(name);
    }
    // And the two per-pixel scalars the fragment stages actually read, which are
    // what took the struct past 16 floats: the size law's thickness factor (W2)
    // and the author tint's strength (W3).
    for (const name of ["sizeK", "tintK"]) {
      expect(WGSL_INSTANCE_STRUCT).toContain(name);
    }

    /*
     * The stride RULE, rather than the current number.
     *
     * `centre` and `half` are `vec2f`, which aligns the struct to 8 bytes, so
     * WGSL requires its size to be a multiple of 8 — a storage array of a
     * 68-byte struct is invalid, and the failure arrives as a pipeline-creation
     * error at runtime, which no amount of TypeScript would have caught. Pinning
     * the rule instead of the count is what keeps this useful the next time a
     * per-pixel scalar is added, and it still pins the two sides together.
     */
    const members = WGSL_INSTANCE_STRUCT.match(/^\s+\w+\s*:\s*(f32|vec2f)/gm) ?? [];
    const floats = members.reduce((sum, m) => sum + (m.includes("vec2f") ? 2 : 1), 0);
    expect(floats).toBe(INSTANCE_FLOATS);
    expect((floats * 4) % 8).toBe(0);
  });
});

describe("the two families", () => {
  it("differ by exactly the normalization", () => {
    expect(WGSL_RSUPN).toContain("inverseSqrt(1.0 + g * g)");
    expect(WGSL_RSUP).not.toContain("inverseSqrt");
  });

  it("pair each family's value with its own gradient", () => {
    // Taking family C means taking family C's normal (<= 4.26 degrees), not family
    // D's — the two are not interchangeable at depth.
    expect(WGSL_RSUPN_GRAD).toContain("d2Rds2");
    expect(WGSL_RSUP_GRAD).not.toContain("d2Rds2");
    expect(WGSL_RSUP_GRAD).toContain("rhoHat");
  });

  it("guards the squared corner radius identically", () => {
    for (const source of [WGSL_RSUPN, WGSL_RSUP, WGSL_RSUPN_GRAD, WGSL_RSUP_GRAD]) {
      expect(source).toContain("max(dot(c, c), 1e-20)");
    }
  });

  it("uses no transcendentals in the corner algebra", () => {
    // What makes the angular correction affordable at all: sin and cos of 2*theta
    // come out of the clamped corner vector by division.
    const arithmetic = (src: string): string => src.replace(/\/\/[^\n]*/g, "").replace(/\s+/g, "");
    for (const source of [WGSL_RSUPN_GRAD, WGSL_RSUP_GRAD]) {
      expect(arithmetic(source)).not.toMatch(/\b(atan2|sin|cos|exp|log)\(/);
    }
  });

  it("fires the box branch at the corner-sector boundary, not just inside it", () => {
    // C3 found and fixed a (0,0)-gradient bug exactly here: at max(q) == 0 both
    // clamped-coordinate terms are masked off, so the box term has to carry the
    // whole derivative.
    expect(WGSL_RSUPN_GRAD).toContain("max(q.x, q.y) <= 0.0");
  });
});

describe("the union", () => {
  it("returns the blend weight, so gradient and optics ride the same seam", () => {
    expect(WGSL_SMOOTH_UNION).toContain("fn union_blend(a : f32, b : f32, u : vec3f) -> vec2f");
    // The value and the weight travel together, so one copy of the algebra serves
    // the distance, the gradient, and the four per-surface optical scalars.
    expect(WGSL_SMOOTH_UNION).toContain("vec2f(b + h * (a - b) - k * h * (1.0 - h), h)");
  });

  it("caps the bulge on k, the way union.ts does", () => {
    expect(WGSL_SMOOTH_UNION).toContain("min(neck, 4.0 * maxBulge)");
  });

  it("gates on separation, which is what stops the jelly", () => {
    expect(WGSL_SMOOTH_UNION).toContain("smoothstep(0.0, sep, max(nearest, 0.0))");
  });

  it("clamps once at the end of the fold, not per blend step", () => {
    const source = fieldPassSource("rsupn");
    expect(source).toContain("max(acc.d, nearest - fu.unionP.y)");
  });
});

describe("the passes bind what they read", () => {
  it("gives optics the field, the aux target, and both backdrop textures", () => {
    const source = opticsModule();
    expect(source).toContain("var fieldTexture : texture_2d<f32>");
    expect(source).toContain("var auxTexture : texture_2d<f32>");
    expect(source).toContain("var backdropChain : texture_2d<f32>");
    expect(source).toContain("var backdropBody : texture_2d<f32>");
  });

  it("gives highlight the field and the aux target, and no backdrop", () => {
    const source = highlightModule();
    expect(source).toContain("var auxTexture : texture_2d<f32>");
    expect(source).not.toContain("backdropChain");
  });

  it("reads the field exactly when it is one texel per device pixel", () => {
    // The governor's resolution knob rasterises the field below the group's rect,
    // and then the read has to filter. Nominally it must not: an exact
    // `textureLoad` is what keeps the default path's arithmetic where it was, and
    // a shader that only sampled would move every golden by a filter tap.
    for (const source of [opticsModule(), highlightModule()]) {
      expect(source).toContain("textureLoad(fieldTexture, texel, 0)");
      expect(source).toContain("var fieldSampler : sampler");
    }
    /*
     * The COORDINATE differs between the two, and that is W8 rather than drift.
     * The optics pass is scissored to the field's own rect, so it reads at its own
     * uv. The highlight pass is not any more — the shadow grew the field rect by
     * its reach and the highlight was scoped back to the surface's rect, because
     * it returns on `coverage <= 0` and was paying to rasterise the difference —
     * so it reads through the remap the two rects imply. Either way the nominal
     * path is the exact load above.
     */
    expect(opticsModule()).toContain("textureSampleLevel(fieldTexture, fieldSampler, in.uv, 0.0)");
    expect(highlightModule()).toContain(
      "textureSampleLevel(fieldTexture, fieldSampler, fieldUv, 0.0)",
    );
    expect(highlightModule()).toContain("let fieldUv = in.uv * hu.fieldFit.xy + hu.fieldFit.zw;");
  });

  it("writes two field targets, so per-surface optics survive the union", () => {
    const source = fieldPassSource("rsupn");
    expect(source).toContain("@location(0) field : vec4f");
    expect(source).toContain("@location(1) aux   : vec4f");
  });

  it("binds an external texture only in the video import module", () => {
    // `importExternalTexture` needs its own pipeline; a shared one would not
    // compile against either binding.
    expect(importModule("external")).toContain("texture_external");
    expect(importModule("sampled")).not.toContain("texture_external");
    expect(importModule("external")).toContain("textureSampleBaseClampToEdge");
  });
});

describe("the analysis reduction", () => {
  it("reduces over a power-of-two workgroup, so the tree has no tail case", () => {
    expect(Number.isInteger(Math.log2(ANALYSIS_WORKGROUP))).toBe(true);
    expect(analysisModule()).toContain(`@workgroup_size(${ANALYSIS_WORKGROUP})`);
  });

  it("reads a fixed grid, so its cost does not follow the backdrop's resolution", () => {
    expect(ANALYSIS_GRID * ANALYSIS_GRID).toBe(4096);
    expect(analysisModule()).toContain("au.grid.z");
  });

  it("unpremultiplies before measuring luminance", () => {
    // A transparent backdrop region must read as absent, not as black.
    expect(analysisModule()).toContain("s.rgb / max(s.a, 1e-6)");
  });
});

describe("X5 and X7 markers", () => {
  it("keeps the bundle marker core's X7 test greps for", () => {
    expect(WGSL_PRELUDE).toContain("vitrea:wgsl-marker");
    expect(allShaderSource()).toContain("vitrea:wgsl-marker");
  });

  it("encodes to sRGB exactly once, in the prelude", () => {
    expect((WGSL_PRELUDE.match(/fn linear_to_srgb/g) ?? [])).toHaveLength(1);
    for (const [name, source] of MODULES) {
      expect((source.match(/fn linear_to_srgb/g) ?? []).length, name).toBe(1);
    }
  });

  it("has only the two canvas passes calling encode_output", () => {
    // The pyramid stays linear all the way through; only what reaches a canvas is
    // encoded.
    expect(opticsModule()).toContain("encode_output(");
    expect(highlightModule()).toContain("encode_output(");
    expect(chainModule().split("fn encode_output")[1] ?? "").not.toContain("encode_output(");
    expect(fieldModule("rsupn").split("fn encode_output")[1] ?? "").not.toContain("encode_output(");
  });
});
