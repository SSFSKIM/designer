/**
 * R1 for W41's E3: the seal changes nothing it does not claim, on the paths no native
 * fixture reads (W38 clause 1c and its bounds declaration, "R1 future fixtures"; W41
 * charter clause 9; c9a §5.192 §5, §5.193).
 *
 * W41 G2 enabled E3 in one endpoint — the macOS 27 light receded document — and its enable
 * domain is narrower than that endpoint: regular variant, nominal material policy, and a
 * texture actually sampled (`bodyE3StrengthUnderPolicy`, folded on the CPU at the optics
 * uniform's pack site). Everywhere else in the same endpoint E3 is declared inert. The
 * calibration bed referees the claimed cells against Apple's pixels; the paths below have
 * no native fixture to referee them, so what they get instead is a regression contract:
 * **the render is byte-identical to the pre-change render wherever the change is not
 * supposed to act.**
 *
 * **The pre-change render is drawn by the same build**, from the harness's
 * `macos27-e3-identity` document: the shipped macOS 27 document with only the light
 * receded patch's `bodyE3Strength` returned to 0. The seal moved that gate-group and no
 * other leaf, so at the gate the twin is the pre-W41 material — and that is read back here
 * rather than trusted: the material the renderer holds is hashed under the digest rule and
 * must be the pre-seal pin `b0d0d8dacc6a03af…`, exactly as `window-activation.spec.ts`
 * reads the sealed endpoints from a browser. Rendering both in one build is what makes a
 * difference attributable to the material and to nothing else in the tree.
 *
 * **The discriminator must DIFFER, and the identities are its one-axis neighbours.** The
 * one pose inside E3's domain — light, window inactive, WebGPU, a supplied flat texture,
 * nominal policy, regular — is rendered with both documents and has to change, or every
 * identity below would pass just as happily against a renderer that ignores E3
 * altogether. It is also rendered a second time with the shipped document, and those two
 * have to be byte-identical: that repeat is what licenses reading any identity here as a
 * statement about the material rather than about luck. Each identity case then leaves
 * the discriminator along exactly one axis — the window pose, the colour scheme, the
 * sampling backend, one accessibility policy, the variant, the tier — so that a failure
 * names the axis whose stand-down broke.
 *
 * **What is compared** is a page screenshot of the glass and 96 CSS px of exterior on every
 * side — every layer the compositor stacks, the proxy, the canvases, the host and its
 * label — byte for byte, RGBA. The margin covers the active document's outer shadow; the
 * receded documents cast none (W32 Decision Log 2). In the discriminator the exterior of
 * the glass's own box must still be identical: E3 is a body operator, and a difference
 * outside the box would be a change it does not claim.
 *
 * **The policies are pinned, not inherited.** Every case states all three overridable
 * preferences through the root's own `setAccessibilityOverrides` — the seam
 * `shared/media-policy.spec.ts` exercises — so a machine running with Reduce Transparency
 * or Increase Contrast on cannot turn the nominal discriminator into a stand-down case.
 * Forced colours is the one preference an app cannot state (`OverridableAccessibilityFlag`
 * omits it by design), so that case emulates the media feature before the page loads.
 */

import { createHash } from "node:crypto";

import { PNG } from "pngjs";
import { expect, test, type Page } from "@playwright/test";
import { DEFAULT_CLEAR_DIMMING } from "@vitreajs/vitrea";

import { materialDigestInput } from "../../../renderer-webgpu/src/material";

import { gotoHarness, requireHardwareAdapter } from "../support";

const GLASS = { x: 300, y: 200, width: 220, height: 120 } as const;
const MARGIN = 96;
const REGION = {
  x: GLASS.x - MARGIN,
  y: GLASS.y - MARGIN,
  width: GLASS.width + 2 * MARGIN,
  height: GLASS.height + 2 * MARGIN,
} as const;

/**
 * A flat, moderately chromatic backdrop: E3's claim is closed over uniform backdrops, and
 * a coloured one exercises both halves of the law — the neutral curve at its encoded luma
 * (about 125) and the chroma gain — without clipping a channel.
 */
const FILL = "rgb(96, 128, 176)";

/**
 * The sealed light receded endpoint, `window-activation.spec.ts`'s full pin since W41 G2.
 */
const SEALED_LIGHT_RECEDED = "7b3d327de9cc81c2da7387a675a91d823429e6a2197beef195b99d04877da2ed";
/**
 * The same endpoint before the seal: W36 G1's pin, retained in that file as the one W41 G2
 * moved, and the prefix `b0d0d8dacc6a03af` the seal's own tests read at the gate.
 */
const PRE_W41_LIGHT_RECEDED = "b0d0d8dacc6a03af8017d0d9a4cec3486bfd95b09c93280a2d2643cf8d0d6c09";

/**
 * The material the renderer holds, hashed under the digest rule — the same function as
 * `window-activation.spec.ts`'s, whose literals are the documents' own digests.
 */
const hash = (value: unknown): string => {
  const sorted = (v: unknown): unknown => Array.isArray(v) ? v.map(sorted)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => a.localeCompare(b))
        .map(([key, entry]) => [key, sorted(entry)])) : v;
  return createHash("sha256")
    .update(JSON.stringify(sorted(materialDigestInput(value))))
    .digest("hex");
};

type Token = "macos27" | "macos27-e3-identity";

interface Pose {
  readonly renderer: "webgpu" | "css";
  readonly colorScheme: "light" | "dark";
  readonly windowActivation: "active" | "inactive";
  /**
   * `texture`: a supplied flat canvas, sampled on the GPU. `dom`: no texture source, so
   * the WebGPU tier samples the page through its proxy (`css-backdrop`). `unsupplied`: a
   * texture source declared and never handed pixels, which X2 resolves to `none`.
   */
  readonly backdrop: "texture" | "dom" | "unsupplied";
  /** Posed on the group, which is where the renderer reads it; `texture` only. */
  readonly variant: "regular" | "clear";
  readonly reducedTransparency: boolean;
  readonly increasedContrast: boolean;
  readonly forcedColors: boolean;
}

const DISCRIMINATOR: Pose = {
  renderer: "webgpu",
  colorScheme: "light",
  windowActivation: "inactive",
  backdrop: "texture",
  variant: "regular",
  reducedTransparency: false,
  increasedContrast: false,
  forcedColors: false,
};

interface Readout {
  readonly state: Record<string, unknown> | undefined;
  readonly activation: string;
  readonly scheme: string;
  readonly policy: {
    readonly reducedTransparency: boolean;
    readonly increasedContrast: boolean;
    readonly forcedColors: boolean;
    readonly material: Record<string, string>;
  };
  readonly variant: string | undefined;
  readonly material: {
    readonly name: string;
    readonly profileKey?: string;
    readonly resolvedMaterialSha256?: string;
    readonly tuned: boolean;
  };
  /** The complete material the live renderer holds; `undefined` on a CSS-tier root. */
  readonly inForce: Record<string, unknown> | undefined;
  readonly rendererActive: boolean;
  /** Fraction of the glass's box the optics canvas painted, read in the drawing task. */
  readonly painted: number | undefined;
  readonly cssLayers: number;
}

interface Render {
  readonly readout: Readout;
  readonly png: Buffer;
  readonly image: PNG;
}

/**
 * One pose, one document, on a freshly loaded page: nothing — no device, no pipeline, no
 * adaptation filter — carries over from the other document's render.
 *
 * The frames are stepped inside one task, so no analysis readback lands between them and
 * both renders draw from the same unobserved adaptation state; with `autoStart` off
 * nothing draws again before the screenshot.
 */
async function render(page: Page, pose: Pose, token: Token): Promise<Render> {
  await gotoHarness(page);
  const readout: Readout = await page.evaluate(
    async ([p, selected, glass, fill, dimming]) => {
      await window.h.settle();
      await window.h.createRoot({
        renderer: p.renderer,
        colorScheme: p.colorScheme,
        windowActivation: p.windowActivation,
        materialDocument: selected,
      });
      const root = window.h.requireRoot();
      root.setAccessibilityOverrides({
        reducedTransparency: p.reducedTransparency,
        increasedContrast: p.increasedContrast,
        reducedMotion: false,
      });
      if (p.variant !== "regular" && p.backdrop !== "texture") {
        throw new Error("this spec poses a variant on the texture group only");
      }
      if (p.backdrop === "texture") {
        window.h.addTextureGroup({
          groupId: "g",
          sourceId: "g.texture",
          fill,
          ...(p.variant === "regular" ? {} : { material: { variant: p.variant, dimming } }),
        });
      } else if (p.backdrop === "dom") {
        window.h.addGroup("g");
      } else {
        root.registerBackdropSource({
          id: "g.texture",
          kind: "texture",
          probe: { taint: "clean", textureCompatibility: "compatible" },
        });
        root.registerGroup({ id: "g", backdropSourceId: "g.texture" });
      }
      window.h.addSurface({
        groupId: "g",
        nodeId: "glass",
        left: glass.x,
        top: glass.y,
        width: glass.width,
        height: glass.height,
        radius: 26,
        label: "R1",
      });
      window.h.frame(3);

      const policy = root.accessibility;
      return {
        state: window.h.capabilities("g"),
        activation: root.windowActivation,
        scheme: root.colorScheme,
        policy: {
          reducedTransparency: policy.reducedTransparency,
          increasedContrast: policy.increasedContrast,
          forcedColors: policy.forcedColors,
          material: { ...policy.material },
        },
        variant: root.renderInput()?.groups.find((group) => group.groupId === "g")?.variant,
        material: { ...root.material },
        inForce: root.rendererBridge?.renderer?.materialProfile as unknown as
          | Record<string, unknown>
          | undefined,
        rendererActive: window.h.rendererActive(),
        painted:
          p.renderer === "webgpu"
            ? window.h.canvasPixels("optics-canvas", "base", glass).painted
            : undefined,
        cssLayers: window.h.layerCount("glass"),
      };
    },
    [pose, token, GLASS, FILL, DEFAULT_CLEAR_DIMMING] as const,
  );
  const png = await page.screenshot({ clip: REGION, animations: "disabled" });
  return { readout, png, image: PNG.sync.read(png) };
}

interface Difference {
  /** Pixels of the region whose RGBA differs by any amount. */
  readonly pixels: number;
  /** Of those, the ones whose centre lies outside the glass's own box. */
  readonly outside: number;
  readonly maxDelta: number;
  readonly first: string;
}

function difference(a: PNG, b: PNG): Difference {
  if (a.width !== b.width || a.height !== b.height) {
    throw new Error(`screenshots differ in size: ${a.width}x${a.height} vs ${b.width}x${b.height}`);
  }
  const scale = a.width / REGION.width;
  let pixels = 0;
  let outside = 0;
  let maxDelta = 0;
  let first = "none";
  for (let y = 0; y < a.height; y += 1) {
    for (let x = 0; x < a.width; x += 1) {
      const index = (y * a.width + x) << 2;
      let delta = 0;
      for (let channel = 0; channel < 4; channel += 1) {
        const d = Math.abs((a.data[index + channel] ?? 0) - (b.data[index + channel] ?? 0));
        delta = Math.max(delta, d);
      }
      if (delta === 0) continue;
      pixels += 1;
      maxDelta = Math.max(maxDelta, delta);
      const cx = REGION.x + (x + 0.5) / scale;
      const cy = REGION.y + (y + 0.5) / scale;
      const inside =
        cx > GLASS.x && cx < GLASS.x + GLASS.width && cy > GLASS.y && cy < GLASS.y + GLASS.height;
      if (!inside) outside += 1;
      if (first === "none") {
        const at = (image: PNG): string => [...image.data.subarray(index, index + 4)].join(",");
        first = `(${cx}, ${cy}) CSS px: ${at(a)} vs ${at(b)}`;
      }
    }
  }
  return { pixels, outside, maxDelta, first };
}

/** Top-level leaves on which two materials in force disagree. */
const differingLeaves = (
  a: Record<string, unknown> | undefined,
  b: Record<string, unknown> | undefined,
): string[] =>
  [...new Set([...Object.keys(a ?? {}), ...Object.keys(b ?? {})])]
    .filter((key) => JSON.stringify(a?.[key]) !== JSON.stringify(b?.[key]))
    .sort();

/**
 * Everything a render reports except what names the document itself: the twin's receded
 * light endpoint records no digest, so `root.material` and the state's `materialDocument`
 * are the two readouts that are meant to differ between the documents.
 */
const comparable = (readout: Readout): unknown => {
  const state = Object.fromEntries(
    Object.entries(readout.state ?? {}).filter(([key]) => key !== "materialDocument"),
  );
  return {
    state,
    activation: readout.activation,
    scheme: readout.scheme,
    policy: readout.policy,
    variant: readout.variant,
    profileKey: readout.material.profileKey,
    tuned: readout.material.tuned,
    rendererActive: readout.rendererActive,
    cssLayers: readout.cssLayers,
  };
};

async function attachOnMismatch(name: string, shipped: Render, twin: Render): Promise<void> {
  await test.info().attach(`${name}-shipped.png`, { body: shipped.png, contentType: "image/png" });
  await test.info().attach(`${name}-e3-identity.png`, { body: twin.png, contentType: "image/png" });
}

const report = (name: string, moved: Difference, extra = ""): void => {
  process.stdout.write(
    `w41-e3-r1 ${name}: ${moved.pixels} differing px (outside the glass ${moved.outside}, ` +
      `max delta ${moved.maxDelta}, first ${moved.first})${extra}\n`,
  );
};

test("discriminator: light inactive, sampled texture, nominal, regular — E3 moves the body and only the body", async ({
  page,
}) => {
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

  const shipped = await render(page, DISCRIMINATOR, "macos27");
  const twin = await render(page, DISCRIMINATOR, "macos27-e3-identity");
  const repeat = await render(page, DISCRIMINATOR, "macos27");

  // The pose is the one inside E3's domain, and the GPU tier really drew it.
  const { readout } = shipped;
  expect(readout.state?.activeRenderer, JSON.stringify(readout.state)).toBe("webgpu");
  expect(readout.state?.samplingBackend).toBe("gpu-texture");
  expect(readout.rendererActive, "no live renderer").toBe(true);
  expect(readout.activation).toBe("inactive");
  expect(readout.scheme).toBe("light");
  expect(readout.variant).toBe("regular");
  expect(readout.policy.forcedColors).toBe(false);
  expect(readout.policy.material).toMatchObject({
    glass: "material",
    frost: "nominal",
    refraction: "nominal",
    occlusion: "nominal",
    border: "nominal",
    ambientTint: "nominal",
    foreground: "adaptive",
  });
  expect(readout.painted, "the optics canvas left the glass unpainted").toBeGreaterThan(0.5);
  expect(comparable(twin.readout)).toEqual(comparable(readout));
  expect(comparable(repeat.readout)).toEqual(comparable(readout));

  // The twin is the pre-W41 material, read back from the renderer rather than assumed: the
  // two materials in force disagree on the gate alone, and under the digest rule the
  // twin's is the pre-seal endpoint while the shipped one is the sealed endpoint its
  // document records — which is what `root.material` reports for it.
  expect(readout.inForce, "the live renderer exposed no material").toBeDefined();
  expect(differingLeaves(readout.inForce, twin.readout.inForce)).toEqual(["bodyE3Strength"]);
  expect(readout.inForce?.bodyE3Strength).toBe(1);
  expect(twin.readout.inForce?.bodyE3Strength).toBe(0);
  const sealed = hash(readout.inForce);
  const preSeal = hash(twin.readout.inForce);
  process.stdout.write(`w41-e3-r1 digests: shipped ${sealed}; e3-identity twin ${preSeal}\n`);
  expect(sealed).toBe(SEALED_LIGHT_RECEDED);
  expect(readout.material.resolvedMaterialSha256).toBe(sealed.slice(0, 16));
  expect(preSeal.slice(0, 16)).toBe("b0d0d8dacc6a03af");
  expect(preSeal).toBe(PRE_W41_LIGHT_RECEDED);
  expect(twin.readout.material.resolvedMaterialSha256).toBeUndefined();

  // The control: the same document twice is the same bytes, or no identity in this file
  // says anything about the material.
  const control = difference(shipped.image, repeat.image);
  report("control (shipped twice)", control);
  if (control.pixels !== 0) await attachOnMismatch("control", shipped, repeat);
  expect(
    control.pixels,
    `two renders of one document differ (${control.first}); the identities below are unreadable`,
  ).toBe(0);

  const moved = difference(shipped.image, twin.image);
  const area = GLASS.width * GLASS.height * (shipped.image.width / REGION.width) ** 2;
  report("discriminator", moved, `; ${(moved.pixels / area).toFixed(3)} of the glass's box`);
  if (moved.pixels === 0 || moved.outside !== 0) {
    await attachOnMismatch("discriminator", shipped, twin);
  }
  expect(
    moved.pixels,
    "E3 moved nothing in the one pose inside its domain, so every identity in this file " +
      "would pass against a renderer that ignores E3: this spec proves nothing as it stands",
  ).toBeGreaterThan(0);
  // A replacement of the body over a flat backdrop moves the whole body, not a stray pixel.
  expect(moved.pixels / area, `${moved.pixels} of ${area} px`).toBeGreaterThan(0.5);
  expect(moved.outside, `E3 moved the exterior, which it does not claim: ${moved.first}`).toBe(0);
});

interface IdentityCase {
  readonly name: string;
  readonly pose: Pose;
  /** The resolved state the pose must reach, so the identity is not vacuous. */
  readonly state: { readonly activeRenderer: string; readonly samplingBackend: string };
  /** Whether the posed endpoint is the light receded one, where the two documents differ. */
  readonly e3InDocument: boolean;
  /** Least painted fraction of the glass's box on the optics canvas; WebGPU only. */
  readonly painted?: number;
  readonly check?: (readout: Readout) => void;
}

const IDENTITY_CASES: readonly IdentityCase[] = [
  {
    name: "window active",
    pose: { ...DISCRIMINATOR, windowActivation: "active" },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: false,
    painted: 0.5,
    check: (readout) => expect(readout.activation).toBe("active"),
  },
  {
    name: "dark scheme, window inactive",
    pose: { ...DISCRIMINATOR, colorScheme: "dark" },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: false,
    painted: 0.5,
    check: (readout) => expect(readout.scheme).toBe("dark"),
  },
  {
    name: "css-backdrop sampling (no texture source)",
    pose: { ...DISCRIMINATOR, backdrop: "dom" },
    state: { activeRenderer: "webgpu", samplingBackend: "css-backdrop" },
    e3InDocument: true,
    painted: 0,
  },
  {
    name: "none sampling (a texture source never supplied)",
    pose: { ...DISCRIMINATOR, backdrop: "unsupplied" },
    state: { activeRenderer: "webgpu", samplingBackend: "none" },
    e3InDocument: true,
    painted: 0,
    check: (readout) => expect(readout.state?.demotionReason).toBe("no-texture-supplied"),
  },
  {
    name: "Reduce Transparency",
    pose: { ...DISCRIMINATOR, reducedTransparency: true },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: true,
    painted: 0.5,
    check: (readout) => {
      expect(readout.policy.reducedTransparency).toBe(true);
      expect(readout.policy.material.occlusion).toBe("increased");
    },
  },
  {
    name: "Increase Contrast",
    pose: { ...DISCRIMINATOR, increasedContrast: true },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: true,
    painted: 0.5,
    check: (readout) => {
      // IC alone lifts no occlusion; E3 stands down on the border and foreground axes.
      expect(readout.policy.increasedContrast).toBe(true);
      expect(readout.policy.reducedTransparency).toBe(false);
      expect(readout.policy.material.border).toBe("strong");
    },
  },
  {
    name: "forced colors",
    pose: { ...DISCRIMINATOR, forcedColors: true },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: true,
    // No painted floor: forced colours draws no glass body at all.
    check: (readout) => {
      expect(readout.policy.forcedColors).toBe(true);
      expect(readout.policy.material.glass).toBe("none");
    },
  },
  {
    name: "clear variant",
    pose: { ...DISCRIMINATOR, variant: "clear" },
    state: { activeRenderer: "webgpu", samplingBackend: "gpu-texture" },
    e3InDocument: true,
    painted: 0.5,
    check: (readout) => expect(readout.variant).toBe("clear"),
  },
  {
    // The CSS tier reads no E3 leaf at the seal: whether it carries, approximates or
    // declines one is W41 Decision Log 4, on its own browser measurement. A carry would
    // make this pose a second discriminator rather than an identity.
    name: "CSS tier",
    pose: { ...DISCRIMINATOR, renderer: "css" },
    state: { activeRenderer: "css", samplingBackend: "css-backdrop" },
    e3InDocument: true,
    check: (readout) => expect(readout.cssLayers, "the CSS tier drew no layers").toBeGreaterThan(0),
  },
];

for (const identity of IDENTITY_CASES) {
  test(`identical: ${identity.name}`, async ({ page }) => {
    if (identity.pose.forcedColors) await page.emulateMedia({ forcedColors: "active" });
    await gotoHarness(page);
    requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

    const shipped = await render(page, identity.pose, "macos27");
    const twin = await render(page, identity.pose, "macos27-e3-identity");
    const { readout } = shipped;

    // The pose reached the path it names, or the identity below is about some other path.
    expect(readout.state, JSON.stringify(readout.state)).toMatchObject(identity.state);
    expect(readout.activation).toBe(identity.pose.windowActivation);
    expect(readout.scheme).toBe(identity.pose.colorScheme);
    expect(readout.policy.forcedColors).toBe(identity.pose.forcedColors);
    identity.check?.(readout);
    if (identity.pose.renderer === "webgpu") {
      expect(readout.rendererActive, "no live renderer").toBe(true);
      expect(readout.variant).toBe(identity.pose.variant);
      // The documents differ in the material this pose draws exactly where the case says:
      // in the light receded endpoint the gate is in force and the pose must fold it out;
      // elsewhere the twin changed nothing the pose reads.
      expect(readout.inForce, "the live renderer exposed no material").toBeDefined();
      expect(differingLeaves(readout.inForce, twin.readout.inForce)).toEqual(
        identity.e3InDocument ? ["bodyE3Strength"] : [],
      );
    }
    if (identity.painted !== undefined) {
      expect(readout.painted, "the optics canvas left the glass unpainted").toBeGreaterThan(
        identity.painted,
      );
    }
    expect(comparable(twin.readout)).toEqual(comparable(readout));

    const moved = difference(shipped.image, twin.image);
    report(identity.name, moved);
    if (moved.pixels !== 0) await attachOnMismatch(identity.name.replace(/\W+/g, "-"), shipped, twin);
    expect(
      moved.pixels,
      `E3 changed a path it does not claim (${identity.name}): first ${moved.first}, ` +
        `max delta ${moved.maxDelta}, ${moved.outside} px outside the glass`,
    ).toBe(0);
  });
}
