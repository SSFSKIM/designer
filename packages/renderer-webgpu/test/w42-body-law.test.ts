/**
 * W42 G2 step 3, U1: the law's leaves, their identity-table entries, the patch boundary, the
 * accessibility fold, and the CPU references held to the oracle (`implementation-design.md` §1,
 * §4, §6 tests 1–3, under `packages/calibration/results/2026-09-30-w42-g2-identification/`).
 *
 * The expected values in the oracle cases are not written here: `implementation-design/
 * u2_fixtures.py` draws them from the instrument's `forward.py` and `geometry.py`, from the
 * rehearsal's `body.py`, and from the pre-read addendum's `native_t.py`, and writes the fixtures
 * this file reads. No native pixel stands behind any of them.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { resolveAccessibilityPolicy } from "../../core/src/accessibility";
import {
  BODY_LAW_DECLARED,
  bodyLawComposite,
  bodyLawE3Codes,
  bodyLawE3StrengthUnderLaw,
  bodyLawInterpolateLevels,
  bodyLawNarrowSigmaDevicePx,
  bodyLawStrengthUnderPolicy,
  bodyLawSurfacePlan,
  bodyToneTableCodesAt,
  landedToneLinear,
  roundHalfEven,
  type LandedToneInputs,
} from "../src/body-law";
import { linearToSrgbChannel, type Rgb } from "../src/color";
import {
  bodyE3Encoded,
  DEFAULT_MATERIAL_PROFILE,
  MATERIAL_IDENTITY_TABLE,
  materialDigestDroppedLeaves,
  materialDigestInput,
  NOMINAL_MATERIAL_POLICY,
  validateBodyLawPatch,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "../src/material";

const FIXTURES = new URL(
  "../../calibration/results/2026-09-30-w42-g2-identification/implementation-design/fixtures/",
  import.meta.url,
);
const fixture = <T>(name: string): T =>
  JSON.parse(readFileSync(new URL(`${name}.json`, FIXTURES), "utf8")) as T;

const LAW_GATED = ["bodyLawK", "bodyLawLambda", "bodyLawNormal", "bodyLawHinge", "bodyLawPose",
  "bodyLawKnee", "bodyLawEdgeSwap"] as const;
const TABLE_GATED = ["bodyToneTableLevels", "bodyToneTableSpans", "bodyToneTableCodes",
  "bodyToneChromaGains", "bodyToneChromaScale"] as const;
const W42_LEAVES = ["bodyLawStrength", ...LAW_GATED, "bodyLawWidthUnit", "bodyLawEncodedAveraging",
  "bodyE3HighStrength", "bodyE3NeutralHigh", "bodyToneTableStrength", ...TABLE_GATED] as const;

function sorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sorted);
  if (value === null || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => [key, sorted(item)]));
}
const digestOf = (material: MaterialProfile): string => createHash("sha256")
  .update(JSON.stringify(sorted(materialDigestInput(material)))).digest("hex").slice(0, 16);

const swept: MaterialProfilePatch = {
  bodyLawK: [3.1, 1.2], bodyLawLambda: -0.4, bodyLawNormal: 0.25, bodyLawHinge: -1,
  bodyLawPose: 1, bodyLawKnee: 2, bodyLawEdgeSwap: 1,
};
const sweptTable: MaterialProfilePatch = {
  bodyToneTableLevels: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 255],
  bodyToneTableSpans: [1, 2, 3, 4, 5],
  bodyToneTableCodes: [
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
  ],
  bodyToneChromaGains: [0, 3, 1.5], bodyToneChromaScale: 2.5,
};

describe("W42's leaves and identity-table entries (implementation-design.md §1)", () => {
  it("appends five W42 entries after W41's, the gates at their identities", () => {
    const w42 = MATERIAL_IDENTITY_TABLE.filter((entry) => entry.wave === "W42");
    expect(w42.map((entry) => Object.keys(entry.gate))).toEqual([
      ["bodyLawStrength"], ["bodyLawWidthUnit"], ["bodyLawEncodedAveraging"],
      ["bodyE3HighStrength"], ["bodyToneTableStrength"],
    ]);
    const last = MATERIAL_IDENTITY_TABLE.findIndex((entry) => entry.wave === "W41");
    expect(MATERIAL_IDENTITY_TABLE.indexOf(w42[0]!)).toBe(last + 1);
    expect(w42[0]!.gated).toEqual([...LAW_GATED]);
    expect(w42[1]!.gated).toEqual([]);
    expect(w42[2]!.gated).toEqual([]);
    expect(w42[3]!.gated).toEqual(["bodyE3NeutralHigh"]);
    expect(w42[4]!.gated).toEqual([...TABLE_GATED]);
    for (const entry of w42) {
      for (const [path, identity] of Object.entries(entry.gate)) {
        expect(identity).toBe(0);
        expect((DEFAULT_MATERIAL_PROFILE as unknown as Record<string, unknown>)[path]).toBe(0);
      }
      expect(entry.inertLawCase).toContain("w42-body-law.test.ts");
    }
  });

  it("drops every W42 leaf on the runtime default, so the default's digest input is unmoved", () => {
    const dropped = new Set(materialDigestDroppedLeaves(DEFAULT_MATERIAL_PROFILE));
    for (const leaf of W42_LEAVES) expect(dropped, leaf).toContain(leaf);
    const input = materialDigestInput(DEFAULT_MATERIAL_PROFILE) as Record<string, unknown>;
    for (const leaf of W42_LEAVES) expect(input).not.toHaveProperty(leaf);
  });

  it("drops the law's whole zero-gate group while its seven gated leaves are swept", () => {
    const original = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { ...swept, bodyLawStrength: 0 });
    expect(materialDigestInput(off)).toEqual(original);
    const on = withMaterialOverrides(off, { bodyLawStrength: 1 });
    const onInput = materialDigestInput(on) as Record<string, unknown>;
    for (const leaf of LAW_GATED) expect(onInput).toHaveProperty(leaf);
    expect(onInput).not.toEqual(materialDigestInput(
      withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { bodyLawStrength: 1 })));
  });

  it("drops D1 and D2 as plain values at the shipped conventions and discriminates each", () => {
    const original = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    for (const key of ["bodyLawWidthUnit", "bodyLawEncodedAveraging"] as const) {
      const moved = materialDigestInput(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { [key]: 1 }));
      expect(moved).toHaveProperty(key, 1);
      expect(moved).not.toEqual(original);
    }
    expect(materialDigestInput(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
      { bodyLawWidthUnit: 2 }))).toHaveProperty("bodyLawWidthUnit", 2);
  });

  it("drops the F extension's group and computes E3 exactly as W41 at strength 0", () => {
    const original = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    const high = [200, 190, 230, 250, 10, 255, 0] as const;
    const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, { bodyE3NeutralHigh: high });
    expect(materialDigestInput(off)).toEqual(original);
    expect(materialDigestInput(withMaterialOverrides(off, { bodyE3HighStrength: 1 })))
      .toHaveProperty("bodyE3NeutralHigh", high);
    const fields = { bodyE3Gains: [0.93, 0.96, 0.94] as const,
      bodyE3Neutral: [150, 157, 164, 171, 178, 188, 197] as const,
      bodyE3HighStrength: 0, bodyE3NeutralHigh: high };
    for (let i = 0; i < 400; i++) {
      const codes: Rgb = [(i * 37) % 256, (i * 91 + 13) % 256, (i * 53 + 7) % 256];
      const level = codes[0] * 0.2126 + codes[1] * 0.7152 + codes[2] * 0.0722;
      const w41 = bodyE3Encoded(codes, fields.bodyE3Gains, fields.bodyE3Neutral);
      expect(bodyLawE3Codes(codes, level, fields)).toEqual(w41);
    }
  });

  it("drops candidate 2's tone group while its table is swept", () => {
    const original = materialDigestInput(DEFAULT_MATERIAL_PROFILE);
    const off = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, sweptTable);
    expect(materialDigestInput(off)).toEqual(original);
    const on = materialDigestInput(withMaterialOverrides(off, { bodyToneTableStrength: 1 }));
    for (const leaf of TABLE_GATED) expect(on).toHaveProperty(leaf);
  });
});

interface SealedDocument {
  readonly patch: MaterialProfilePatch;
  readonly resolvedMaterialSha256: string;
  readonly resolvedOverActiveDocument?: string;
}
const readDocument = (name: string): SealedDocument => JSON.parse(readFileSync(
  new URL(`../../calibration/profiles/${name}.json`, import.meta.url), "utf8")) as SealedDocument;

describe("the six sealed digests (implementation-design.md §1.2)", () => {
  it.each([
    ["apple-macos-26.5-1x-light-standard", "b2b570e4adcea8fb"],
    ["apple-macos-26.5-1x-dark-standard", "874be66ea501621b"],
    ["apple-macos-27.0-1x-light-standard-glass0.5", "be13dae45098fc89"],
    ["apple-macos-27.0-1x-dark-standard-glass0.5", "2a4323f33df8d799"],
    ["apple-macos-27.0-1x-light-standard-glass0.5-receded", "b0d0d8dacc6a03af"],
    ["apple-macos-27.0-1x-dark-standard-glass0.5-receded", "7c454858a3cbad5b"],
  ])("%s resolves to %s, whatever W42's gated leaves hold behind their gates", (name, sha) => {
    const document = readDocument(name);
    expect(document.resolvedMaterialSha256).toBe(sha);
    for (const leaf of W42_LEAVES) expect(document.patch).not.toHaveProperty(leaf);
    const base = document.resolvedOverActiveDocument
      ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
        readDocument(document.resolvedOverActiveDocument.replace(/\.json$/, "")).patch)
      : DEFAULT_MATERIAL_PROFILE;
    const material = withMaterialOverrides(base, document.patch);
    expect(digestOf(material)).toBe(sha);
    expect(digestOf(withMaterialOverrides(material,
      { ...swept, ...sweptTable, bodyE3NeutralHigh: [1, 2, 3, 4, 5, 6, 7] }))).toBe(sha);
  });
});

describe("W42's patch boundary", () => {
  const invalid: readonly [string, unknown][] = [
    ...[null, "1", NaN, Infinity, -0.01, 1.01].flatMap((v) =>
      ["bodyLawStrength", "bodyE3HighStrength", "bodyToneTableStrength", "bodyLawNormal"]
        .map((k) => [k, v] as [string, unknown])),
    ["bodyLawLambda", -0.51], ["bodyLawLambda", 1.61], ["bodyLawLambda", "0.9"],
    ["bodyToneChromaScale", 3.01], ["bodyToneChromaScale", -1],
    ["bodyLawHinge", 0], ["bodyLawHinge", 0.5], ["bodyLawPose", 2], ["bodyLawKnee", 3],
    ["bodyLawKnee", 1.5], ["bodyLawEdgeSwap", -1], ["bodyLawWidthUnit", 3],
    ["bodyLawEncodedAveraging", 2],
    ["bodyLawK", [2]], ["bodyLawK", [2, 2, 2]], ["bodyLawK", [0.79, 2]], ["bodyLawK", [2, 4.01]],
    ["bodyLawK", [2, null]], ["bodyLawK", new Array(2)],
    ["bodyE3NeutralHigh", [1, 2, 3, 4, 5, 6]], ["bodyE3NeutralHigh", [1, 2, 3, 4, 5, 6, 256]],
    ["bodyToneTableLevels", [0, 64, 64, 128, 160, 176, 192, 208, 224, 240, 255]],
    ["bodyToneTableLevels", [0, 64, 96, 128, 160, 176, 192, 208, 224, 240]],
    ["bodyToneTableSpans", [64, 80, 80, 128, 160]], ["bodyToneTableSpans", [0, 80, 96, 128, 160]],
    ["bodyToneTableCodes", [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]],
    ["bodyToneTableCodes", Array(5).fill([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 256])],
    ["bodyToneTableCodes", [...Array(4).fill([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), [0, 1]]],
    ["bodyToneChromaGains", [1, 1]], ["bodyToneChromaGains", [1, 1, 3.5]],
  ];
  it.each(invalid)("refuses %s = %j, even behind gate zero", (key, value) => {
    expect(() => validateBodyLawPatch({ [key]: value })).toThrow(TypeError);
    expect(() => withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
      { [key]: value } as MaterialProfilePatch)).toThrow(new RegExp(key));
  });

  it("admits the documented ranges and merges each leaf whole", () => {
    const patch: MaterialProfilePatch = { bodyLawStrength: 1, bodyLawWidthUnit: 1,
      bodyLawEncodedAveraging: 1, bodyE3HighStrength: 1, bodyToneTableStrength: 1, ...swept,
      ...sweptTable, bodyE3NeutralHigh: [255, 0, 1, 2, 3, 4, 5] };
    expect(() => validateBodyLawPatch(patch as Record<string, unknown>)).not.toThrow();
    const merged = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
    for (const [key, value] of Object.entries(patch)) {
      expect((merged as unknown as Record<string, unknown>)[key]).toEqual(value);
    }
  });
});

describe("the accessibility fold (implementation-design.md §4; Forks 4 and 6)", () => {
  const policyOf = (flags: Record<string, boolean>) => resolveAccessibilityPolicy({
    reducedTransparency: false, reducedMotion: false, increasedContrast: false,
    forcedColors: false, reducedTransparencySupported: true, ...flags,
  }).material;

  it("keeps the law under no preference, Reduced Motion and Increase Contrast alone", () => {
    for (const flags of [{}, { reducedMotion: true }, { increasedContrast: true }]) {
      expect(bodyLawStrengthUnderPolicy(1, policyOf(flags), "regular", true)).toBe(1);
    }
  });

  it("returns the identity under Reduce Transparency, forced colours, clear and unsampled", () => {
    for (const flags of [{ reducedTransparency: true }, { forcedColors: true },
      { reducedTransparency: true, increasedContrast: true }]) {
      expect(bodyLawStrengthUnderPolicy(1, policyOf(flags), "regular", true)).toBe(0);
    }
    expect(bodyLawStrengthUnderPolicy(1, NOMINAL_MATERIAL_POLICY, "clear", true)).toBe(0);
    expect(bodyLawStrengthUnderPolicy(1, NOMINAL_MATERIAL_POLICY, "regular", false)).toBe(0);
  });

  it("reads E3 through the law's fold on the law's path, not E3's own", () => {
    const ic = policyOf({ increasedContrast: true });
    const folded = bodyLawStrengthUnderPolicy(1, ic, "regular", true);
    expect(bodyLawE3StrengthUnderLaw(1, folded)).toBe(1);
    expect(bodyLawE3StrengthUnderLaw(1, 0)).toBe(0);
  });
});

interface PlanRow {
  readonly component: string;
  readonly centre: readonly [number, number];
  readonly size: readonly [number, number];
  readonly scale: number;
  readonly receded: boolean;
  readonly unit: number;
  readonly box: { x0: number; y0: number; x1: number; y1: number };
  readonly footprint: { x0: number; y0: number; x1: number; y1: number };
  readonly canvas: { x0: number; y0: number; x1: number; y1: number };
  readonly texel: number;
  readonly floor: number;
  readonly span: number;
  readonly t: number;
  readonly wide: number;
  readonly depths: readonly number[];
  readonly narrowAtDepth: readonly number[];
  readonly edge: "clamp" | "normalised";
  readonly levels: readonly number[];
}

describe("the per-surface plan against forward.py (test 2)", () => {
  const { k, rows } = fixture<{ k: [number, number]; rows: PlanRow[] }>("plan");

  it("covers every canonical and bed single shape at both scales, poses and units", () => {
    expect(rows.length).toBeGreaterThanOrEqual(2 * 2 * 3 * 20);
    expect(new Set(rows.map((row) => row.component))).toContain("rrect-112");
  });

  it("reproduces the box, R_fp, texel, floor, widths and level set of every row", () => {
    for (const row of rows) {
      const label = `${row.component} ${row.scale}x ${row.receded ? "receded" : "active"} u${row.unit}`;
      const material = { bodyLawK: k, bodyLawPose: row.receded ? 1 : 0, bodyLawEdgeSwap: 0,
        bodyLawWidthUnit: row.unit };
      const plan = bodyLawSurfacePlan({ centre: row.centre, size: row.size }, row.scale, material,
        row.canvas);
      expect(plan.box, label).toEqual(row.box);
      expect(plan.footprint, label).toEqual(row.footprint);
      expect(plan.texelDevicePx, label).toBe(row.texel);
      expect(plan.floorSigmaDevicePx, label).toBeCloseTo(row.floor, 12);
      expect(plan.spanPx, label).toBe(row.span);
      expect(plan.t, label).toBeCloseTo(row.t, 12);
      expect(plan.edge, label).toBe(row.edge);
      expect(plan.wideSigmaDevicePx, label).toBeCloseTo(row.wide, 10);
      expect(plan.narrowSigmaDevicePx.length, label).toBe(row.levels.length);
      plan.narrowSigmaDevicePx.forEach((v, i) => expect(v, label).toBeCloseTo(row.levels[i]!, 10));
      // Inside the contour the plan is forward.py's σn exactly. From the contour out forward.py
      // holds o = 1 (`forward.py:85–86`: past d = 1e-6 active, from d = 0 receded) and the rehearsal holds the contour's 0.5 or the receded flat
      // value (`body.py:670–672`); the runtime takes the rehearsal's, which is where the band
      // weight is 0 (active) and where coverage has left the body.
      row.depths.forEach((d, i) => {
        const got = bodyLawNarrowSigmaDevicePx(d, plan, material);
        if (d < 0 || (d === 0 && !row.receded)) {
          expect(got, `${label} d${d}`).toBeCloseTo(row.narrowAtDepth[i]!, 10);
        } else {
          const o = row.receded ? 0.4 + 0.4 * row.t : 0.5;
          expect(got, `${label} d${d}`).toBeCloseTo(k[0] * 5 * o * plan.unitDevicePx, 10);
          expect(row.narrowAtDepth[i], `${label} d${d}`).toBeCloseTo(k[0] * 5 * plan.unitDevicePx, 10);
        }
      });
    }
  });

  it("swaps the edge mode under bodyLawEdgeSwap and rounds a margin as Python does", () => {
    const plan = (receded: boolean, swap: number) => bodyLawSurfacePlan(
      { centre: [160, 100], size: [160, 96] }, 2,
      { bodyLawK: [2, 2], bodyLawPose: receded ? 1 : 0, bodyLawEdgeSwap: swap, bodyLawWidthUnit: 1 });
    expect(plan(false, 1).edge).toBe("normalised");
    expect(plan(true, 1).edge).toBe("clamp");
    expect([0.5, 1.5, 2.5, 30.5, 31.4999].map(roundHalfEven)).toEqual([0, 2, 2, 30, 31]);
    expect(BODY_LAW_DECLARED.activeBandPt).toBe(20);
  });
});

interface CompositeRow {
  readonly C: Rgb;
  readonly W: Rgb;
  readonly lam: number;
  readonly w: number;
  readonly hinge: number;
  readonly wideLuma: number;
  readonly M: { channel: Rgb; luma: Rgb; chromaW: Rgb };
}

describe("the composite's algebra against forward.py and body.py (test 3)", () => {
  const { rows } = fixture<{ rows: CompositeRow[] }>("composite");
  it.each([[0, "channel"], [1, "luma"], [2, "chromaW"]] as const)(
    "knee %i reproduces the oracle's %s form on every pair",
    (knee, form) => {
      for (const row of rows) {
        const out = bodyLawComposite(row.C, row.W, { bodyLawLambda: row.lam, bodyLawNormal: row.w,
          bodyLawHinge: row.hinge, bodyLawKnee: knee, bodyLawEncodedAveraging: 1 });
        out.argument.forEach((v, i) => expect(v).toBeCloseTo(row.M[form][i]!, 12));
        expect(out.wideLuma).toBeCloseTo(row.wideLuma, 12);
      }
    },
  );

  it("maps a constant to itself under every knee, hinge and space (clause 7's premise)", () => {
    for (const knee of [0, 1, 2]) {
      for (const hinge of [1, -1]) {
        for (const space of [0, 1]) {
          const g: Rgb = [0.3, 0.3, 0.3];
          const out = bodyLawComposite(g, g, { bodyLawLambda: 1.3, bodyLawNormal: 0.5,
            bodyLawHinge: hinge, bodyLawKnee: knee, bodyLawEncodedAveraging: space });
          // Linear averaging (D2 at its identity, the rejected F2) encodes M at the end.
          const expected = space === 1 ? 0.3 : linearToSrgbChannel(0.3);
          out.argument.forEach((v) => expect(v).toBeCloseTo(expected, 12));
        }
      }
    }
  });

  it("interpolates the levels linearly, or by a cubic through the four nearest", () => {
    const levels = [2, 4, 6, 8, 12];
    const values = levels.map((s) => 0.1 + 0.002 * s * s);   // a quadratic in σ: the cubic is exact
    for (const s of [2, 3, 5.5, 7.9, 10, 12]) {
      expect(bodyLawInterpolateLevels(s, levels, values, "cubic")).toBeCloseTo(0.1 + 0.002 * s * s, 12);
    }
    expect(bodyLawInterpolateLevels(3, [2, 4], [0.2, 0.4], "linear")).toBeCloseTo(0.3, 12);
    expect(bodyLawInterpolateLevels(9, [2], [0.7], "single")).toBe(0.7);
  });
});

interface LandedFixture {
  readonly [endpoint: string]: {
    readonly params: {
      readonly tint: readonly number[];
      readonly tintAlpha: number;
      readonly sizeOcclusionGain: number;
      readonly backdropToneLow: number;
      readonly backdropToneHigh: number;
      readonly backdropToneSizeBias: number;
      readonly backdropToneMax: number;
      readonly anchorX: readonly number[];
      readonly thin: readonly number[];
      readonly thick: readonly number[];
      readonly responseStrength: number;
      readonly black: readonly [number, number, number];
      readonly bodyChromaRetention: number;
      readonly abscissa: unknown;
      readonly sizeToneLevelFar: number;
    };
    readonly cases: readonly { sizeK: number; A: Rgb[]; linear: Rgb[] }[];
  };
}

describe("candidate 1's landed tone against the rehearsal's landed_T (test 3)", () => {
  const landed = fixture<LandedFixture>("landed");
  it.each(Object.keys(landed))("%s: every colour and sizeK within 1e-12", (endpoint) => {
    const { params, cases } = landed[endpoint]!;
    const profile = {
      backdropToneAnchorX: params.anchorX as unknown as MaterialProfile["backdropToneAnchorX"],
      backdropToneResponseThin: params.thin as unknown as MaterialProfile["backdropToneResponseThin"],
      backdropToneResponseThick: params.thick as unknown as MaterialProfile["backdropToneResponseThick"],
      backdropToneResponseStrength: params.responseStrength,
      backdropToneBlackStrength: params.black[0],
      backdropToneBlackThin: params.black[1],
      backdropToneBlackThick: params.black[2],
    };
    for (const { sizeK, A, linear } of cases) {
      const inputs: LandedToneInputs = {
        sizeK, toneLevelFar: 0, neutral: [params.tint[0]!, params.tint[0]!, params.tint[0]!],
        tintAlpha: params.tintAlpha, sizeOcclusionGain: params.sizeOcclusionGain,
        toneStrength: params.backdropToneMax, toneLow: params.backdropToneLow,
        toneHigh: params.backdropToneHigh, toneSizeBias: params.backdropToneSizeBias,
        retention: params.bodyChromaRetention,
        abscissa: params.abscissa === "source(default)" ? "source" : "silhouette", presence: 1,
      };
      A.forEach((a, i) => {
        const y = landedToneLinear(a, inputs, profile);
        y.forEach((v, c) => expect(v, `${endpoint} sizeK ${sizeK} A ${a}`).toBeCloseTo(linear[i]![c]!, 12));
      });
    }
  });
});

interface TonesFixture {
  readonly e3: readonly {
    codes: Rgb; gainLevel: number; gains: [number, number, number];
    neutral: [number, number, number, number, number, number, number];
    high: [number, number, number, number, number, number, number]; strength: number; out: Rgb;
  }[];
  readonly table: readonly {
    endpoint: string; levels: number[]; spans: number[]; codes: number[][];
    gains: [number, number, number]; scale: number; cases: { codes: Rgb; span: number; out: Rgb }[];
  }[];
}

describe("the F extension and candidate 2's table against numpy (test 3)", () => {
  const tones = fixture<TonesFixture>("tones");
  it("computes E3 with the extension and a separate gain argument as the oracle does", () => {
    for (const row of tones.e3) {
      const out = bodyLawE3Codes(row.codes, row.gainLevel, { bodyE3Gains: row.gains,
        bodyE3Neutral: row.neutral, bodyE3HighStrength: row.strength, bodyE3NeutralHigh: row.high });
      out.forEach((v, i) => expect(v).toBeCloseTo(row.out[i]!, 9));
    }
  });

  it("reads the addendum's grid as native_t.py does, with candidate 2's chroma", () => {
    for (const table of tones.table) {
      const fields = {
        bodyToneTableLevels: table.levels as unknown as MaterialProfile["bodyToneTableLevels"],
        bodyToneTableSpans: table.spans as unknown as MaterialProfile["bodyToneTableSpans"],
        bodyToneTableCodes: table.codes as unknown as MaterialProfile["bodyToneTableCodes"],
        bodyToneChromaGains: table.gains, bodyToneChromaScale: table.scale,
      };
      for (const c of table.cases) {
        bodyToneTableCodesAt(c.codes, c.span, fields)
          .forEach((v, i) => expect(v, `${table.endpoint} ${c.span}`).toBeCloseTo(c.out[i]!, 9));
      }
    }
  });
});
