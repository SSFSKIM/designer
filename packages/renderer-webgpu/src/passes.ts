/**
 * The three drawing passes, as GPU work: field, optics, highlight.
 *
 * Each is scoped to the group's device-pixel rect. The field pass renders *into*
 * a group-sized pair of textures; the optics and highlight passes render into the
 * plane canvases with the viewport and the scissor both set to that rect, so the
 * fullscreen triangle's `uv` indexes the field textures one-to-one and
 * `position.xy` stays in canvas coordinates. X1 forbids two glass surfaces
 * overlapping inside one plane, so those rects are disjoint and the scissor is
 * enough — no depth, no stencil, no sorting.
 *
 * Blending is premultiplied source-over on both canvas passes. Against a cleared
 * canvas it is indistinguishable from no blending, and the reason to have it is
 * the case that is not that: an overlay-plane surface drawn over a base-plane one
 * during a cross-plane morph, where the promotion moves the surface as a unit but
 * the frame in flight can still hold both.
 */

import { OUTPUT_TEXTURE_FORMAT, WORKING_TEXTURE_FORMAT } from "./color";
import { type GpuContext, createUniformSlot, createStorageSlot, type StorageSlot, type UniformSlot } from "./gpu-context";
import type { FieldFamily } from "./governor";
import { INSTANCE_BYTES } from "./instances";
import { pipelineKey } from "./pipeline-cache";
import { poolKey } from "./texture-pool";
import { PASS_LABEL, type PassTimeline } from "./timing";
import { fieldModule, highlightModule, opticsModule } from "./wgsl";

/**
 * Usage masks are computed on FIRST USE, never at module scope.
 *
 * `GPUTextureUsage` is a browser global, and this module is imported outside a
 * browser: `vitrea`'s lazy seam resolves this package in Node to check the
 * renderer's shape (`packages/core/test/renderer-seam.test.ts`). A mask evaluated
 * at module scope makes the whole package throw on import there — a
 * `ReferenceError` from a file that never intended to run, in a test that only
 * wanted to read `backend` and `ready`.
 */
const fieldUsage = (): GPUTextureUsageFlags =>
  GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING;

/** Premultiplied source-over. See the module note. */
const PREMULTIPLIED_OVER: GPUBlendState = {
  color: { srcFactor: "one", dstFactor: "one-minus-src-alpha", operation: "add" },
  alpha: { srcFactor: "one", dstFactor: "one-minus-src-alpha", operation: "add" },
};

/** A rect in device pixels. Integers by construction — see `snapRectToDevicePixels`. */
export interface DeviceRect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface FieldPassArgs {
  readonly groupId: string;
  readonly family: FieldFamily;
  readonly rectDevice: DeviceRect;
  /** CSS px per device px. */
  readonly cssPerDevice: number;
  /** Coverage ramp width in CSS px. One device pixel, unless the governor widens it. */
  readonly coverageRampCss: number;
  /**
   * The governor's `refractionResolutionScale`, 0 < s <= 1. The field targets are
   * allocated at `rectDevice * s` and the optics and highlight passes upsample
   * them; the *rect* is unchanged, so the group still covers the same pixels.
   * `1` is the nominal path and takes exactly the arithmetic it took before the
   * knob existed.
   */
  readonly renderScale: number;
  readonly instances: Float32Array;
  readonly instanceCount: number;
  readonly union: { readonly neckWidth: number; readonly maxBulge: number; readonly separationThreshold: number };
}

export interface FieldTargets {
  readonly field: GPUTexture;
  readonly aux: GPUTexture;
  /** The owning surface's centre and half-extents per pixel (W12 G2) — the lens's oval. */
  readonly aux2: GPUTexture;
  /** The field textures' extent in texels — the group's rect times `renderScale`. */
  readonly width: number;
  readonly height: number;
  /**
   * True when that extent is smaller than the group's rect, so a reader has to
   * filter rather than index. False on the nominal path, where one texel is one
   * device pixel and the read is an exact `textureLoad`.
   */
  readonly upsampled: boolean;
}

export interface OpticsPassArgs {
  readonly groupId: string;
  readonly target: GPUTextureView;
  readonly targetFormat: GPUTextureFormat;
  readonly rectDevice: DeviceRect;
  readonly fields: FieldTargets;
  /** Viewport in device px, and CSS px per device px. */
  readonly viewportDevice: readonly [number, number];
  readonly cssPerDevice: number;
  readonly coverageRampCss: number;
  /** Backdrop uv transform on viewport-normalised coordinates. */
  readonly fit: readonly [number, number, number, number];
  readonly refractionScale: number;
  /** The lens's magnitude gain (W12 G2) — `MaterialProfile.lensRefractionGain`. */
  readonly lensRefractionGain: number;
  /**
   * The lens law (W12 G2), evaluated per pixel from the thickness and the span
   * the field carries: the reference's height and amount laws, the thickness
   * they are read at, the profile's extent and exponent, and the direction's
   * ovalization with its knee — see `MaterialProfile.lensRefractionGain`.
   */
  readonly lensHeightPerSpan: number;
  readonly lensHeightMax: number;
  readonly lensAmountPerSpan: number;
  readonly lensAmountMax: number;
  readonly lensThicknessReference: number;
  readonly lensExtentGain: number;
  readonly lensProfileExponent: number;
  readonly lensOvalization: number;
  readonly lensOvalizationSpanMin: number;
  readonly lensOvalizationSpanMax: number;
  /**
   * The inner shadow's depth gain — W2's `lensSizeGainMax`, which the shadow
   * keeps reading after the lens moved to its own law (W12 G2); the shader
   * evaluates the shadow's depth from the same thickness and span.
   */
  readonly shadowDepthSizeGainMax: number;
  readonly chainMaxLod: number;
  readonly tint: readonly [number, number, number];
  readonly tintAlpha: number;
  readonly adaptTint: readonly [number, number, number];
  readonly adaptStrength: number;
  /** The group's author tint seed in linear light, and the shade law it is painted through (W10). */
  readonly tintSeed: readonly [number, number, number];
  readonly tintToneAdaptation: number;
  /** `[tintShadeDark, tintShadeLight, tintShadeStrength]`. */
  readonly tintShade: readonly [number, number, number];
  readonly rimWidth: number;
  readonly rimAlpha: number;
  readonly specularPower: number;
  readonly specularGain: number;
  readonly lightDirection: readonly [number, number];
  readonly shadowDepth: number;
  readonly shadowAlpha: number;
  /**
   * The size law's gains (W2), applied per pixel against the thickness the
   * shader evaluates from the field pass's span channel. `bodyChainLod` is not
   * a gain but the chain level whose blur already matches the body texture —
   * the origin the scattering term measures its extra octaves from, which only
   * the pyramid that built the body knows.
   *
   * `sizeScatterGainMax` arrives RESOLVED at the ratio the group draws at
   * (W15 G1, claims §5.69 §1): the profile anchors it at dpr 1 and dpr 2 and
   * the caller interpolates, as it already did for the ramp's anchors.
   */
  readonly sizeScatterGainMax: number;
  /**
   * The gain's FAR end at that ratio (W15 G1's re-form, claims §5.70 §4 and §7).
   *
   * The reference's heavy kernel grows with the span, so the gain is a curve and
   * not a number: the shader rises from `sizeScatterGainMax` at `sizeSpanMax` to
   * this at `sizeScatterSpanMax`, along the smoothstep the ramp's far anchor
   * already declines on. Resolved on the CPU like the near end, and equal to it
   * at dpr ≤ 1, where the curve is flat and this uniform changes nothing.
   */
  readonly sizeScatterGainFar: number;
  readonly sizeOcclusionGain: number;
  readonly sizeShadowGainMax: number;
  readonly bodyChainLod: number;
  /**
   * The thickness band (W2) and the scatter facet's frost (W11c), plus the
   * accessibility fold every span-dependent rise multiplies by — the refraction
   * ladder at the preference's cap, the same factor `sizeThicknessUnderPolicy`
   * applies on the CPU. The shader evaluates the thickness curve per pixel from
   * the span the field pass carries; the scattering reads the depth instead.
   */
  readonly sizeSpanMin: number;
  readonly sizeSpanMax: number;
  readonly sizeScatterFloor: number;
  /**
   * The scatter facet's span curve (W11c), which since W13 G1 is the depth
   * ramp's DEEP value: the shader evaluates `floor + (1 − floor) ·
   * smoothstep(sizeSpanMin, sizeScatterSpanMax, span)` per pixel from the span
   * the field pass carries, exactly as it did before the ramp.
   *
   * This and `sizeScatterFloor` also arrive RESOLVED at the ratio (W15 G1,
   * claims §5.69 §2): the deep value is a per-scale law now, and the shader
   * reads one floor and one span top whatever scale produced them.
   */
  readonly sizeScatterSpanMax: number;
  /**
   * The body depth ramp (W13 G1, claims §5.61 §2, §5.64 §5), resolved once per
   * group from the ratio the renderer draws at: the sharp share at the contour
   * at each end of the material's thin/thick curve, and the reach at which the
   * ramp's excursion vanishes into the span curve above, **in CSS px** — the
   * profile names the reach in device px and the caller divides, because the
   * depth the shader has is the field's own and that is in group-local CSS px.
   * All three are already interpolated between the profile's 1x and 2x anchors.
   *
   * The start arrives as its two ENDS rather than as one resolved number: it
   * grades along `sizeThickness(span)` and a group's members need not be one
   * size, so the shader mixes the two ends by the same span the field already
   * carries per pixel.
   */
  readonly sizeScatterRampStartThin: number;
  readonly sizeScatterRampStartThick: number;
  /** The start at `sizeScatterSpanMax` and beyond (the fourth form); the shader declines to it. */
  readonly sizeScatterRampStartFar: number;
  readonly sizeScatterRampReachCssPx: number;
  readonly sizeFold: number;
  /**
   * Backdrop tone adaptation (W7): `[low, high, sizeBiasUnderPolicy, strength]`.
   *
   * The bias is the profile's own divided by the accessibility refraction cap
   * (`backdropToneSizeBiasUnderPolicy`), because the shader multiplies it by the
   * policy-folded `sizeK` while the gate it expresses is geometric.
   */
  readonly backdropTone: readonly [number, number, number, number];
  /**
   * The backdrop source's average colour in linear light, and its luminance —
   * what the adaptation adapts toward, measured by the host. `backdropTone`'s
   * strength is 0 where there is none, so this is not read.
   */
  readonly backdropToneColour: readonly [number, number, number, number];
  /**
   * The outer shadow (W8): `[thinOcclusion, sigmaCss, spreadCss, offsetFieldUv]`.
   *
   * `thinOcclusion` is the THIN regime's peak occlusion in LINEAR light,
   * resolved at this group's backdrop luminance (W14 G1's adaptive alpha, whose
   * key is one number per group) and folded under the accessibility policy. It
   * is no longer a compositing-space alpha, because the shader blends the two
   * regimes before it converts, and the conversion is not linear. The size law
   * is per pixel and stays in the shader. The offset arrives as a **field-texture
   * UV** rather than as CSS px, because only the caller knows how tall the rect
   * the field was rasterised into is.
   */
  readonly outerShadow: readonly [number, number, number, number];
  /**
   * The outer shadow's thick regime (W14 G1): the composite's peak linear
   * occlusion at casting spans 96, 128 and 160 CSS px, folded under the same
   * policy. The shader interpolates between them per pixel from the span the
   * field carries and holds them outside.
   */
  readonly outerShadowThick: readonly [number, number, number];
  /**
   * The lift (W14 G1), the shadow's second term and this tier's alone:
   * `[amplitude, spanMinCss, spanFullCss, chainLod]`.
   *
   * `amplitude` is in LINEAR light, a fraction of the blurred backdrop's own
   * luminance, and is zero where the policy stood the term down. `chainLod` is
   * the continuous chain level whose blur is the profile's `liftBlurSigmaCss` —
   * resolved through the pyramid's own CSS-px-to-texel density and plan
   * downscale, exactly as `bodyChainLod` is, and clamped to `chainMaxLod`.
   */
  readonly outerShadowLift: readonly [number, number, number, number];
  /** The outer shadow's size-law gain — see `MaterialOuterShadow.sizeGain`. */
  readonly outerShadowSizeGain: number;
  /**
   * The field rect's height in CSS px — what the shadow's shift converts through
   * when it lands outside the field texture.
   *
   * The rect is clipped to the canvas and its pad is only the shadow's reach, so
   * the shift runs off the top of the texture both for a surface near the
   * viewport's top edge and, always, for the topmost band of every group. The
   * shader reconstructs the distance it could not read; this is the scale it
   * reconstructs in.
   */
  readonly outerShadowRectCssHeight: number;
  /**
   * The backdrop tone response's anchors (W9): the three solid anchors'
   * encoded-space means, and the reference's settled interior levels there for
   * a thin (`sizeThickness` 0) and a thick (saturated) surface. See
   * `MaterialProfile.backdropToneAnchorX`.
   */
  readonly backdropToneAnchorX: readonly [number, number, number];
  readonly backdropToneResponseThin: readonly [number, number, number];
  readonly backdropToneResponseThick: readonly [number, number, number];
  /** The response law's per-profile authority (0 on dark profiles) — see
   * `MaterialProfile.backdropToneResponseStrength`. */
  readonly backdropToneResponseStrength: number;
  /**
   * The backdrop's LINEAR-space mean under the same weighting as the tone
   * colour — what the response solve composites against. Falls back to the
   * tone level where the host measured no separate linear mean.
   */
  readonly backdropToneLinearMean: number;
  readonly backdrop: { readonly chain: GPUTextureView; readonly body: GPUTextureView } | undefined;
}

export interface HighlightPassArgs {
  readonly groupId: string;
  readonly target: GPUTextureView;
  readonly targetFormat: GPUTextureFormat;
  readonly rectDevice: DeviceRect;
  readonly fields: FieldTargets;
  readonly viewportDevice: readonly [number, number];
  readonly cssPerDevice: number;
  readonly sweep: number;
  readonly sweepBandRadians: number;
  readonly sweepGain: number;
  readonly rimWidth: number;
  readonly pressPointCss: readonly [number, number];
  readonly glowRadiusCss: number;
  readonly glowGain: number;
  readonly colour: readonly [number, number, number];
  /**
   * The optics pass's `backdropTone` and the backdrop's own luminance, forwarded
   * unchanged (W7). A highlight is the material catching light, and a material
   * that has taken its backdrop's tone is not there to catch any — so this pass
   * evaluates the same curve off the same numbers rather than a second copy.
   */
  readonly backdropTone: readonly [number, number, number, number];
  readonly backdropToneLevel: number;
  /**
   * The thickness band and the accessibility fold (W11c), so this pass evaluates
   * the size curve off the per-pixel span exactly as the optics pass does.
   */
  readonly sizeSpanMin: number;
  readonly sizeSpanMax: number;
  readonly sizeFold: number;
  /**
   * The rect the FIELD textures were rasterised into, which since W8 is bigger
   * than `rectDevice`.
   *
   * The outer shadow made the field rect grow by the shadow's reach — about 46
   * CSS px against the rim-and-bulge margin's 3 — and this pass draws nothing out
   * there: `fs_highlight` returns on `coverage <= 0`, so every one of those
   * fragments was rasterised, read twice and discarded. So the pass keeps the
   * small rect as its viewport and scissor and reads the field through the remap
   * this pair implies.
   *
   * **Worth less than it looks, and the number is here rather than a hope.** A/B
   * against the same tree without this scoping, three interleaved bench runs
   * each, comparing the shadow-on to shadow-off ratio on the mobile scene: 3.11
   * against 3.35 at the median, with the two ranges overlapping (2.92…3.37
   * against 3.20…3.62). So this recovers roughly 7% of the shadow's cost, not the
   * third this pass's own timestamp suggested — most of that timestamp is the
   * field texture's write draining into the next pass rather than this pass's own
   * fragments. It stays because it is strictly less work for byte-identical
   * output (the `highlight-press-glow` golden does not move), not because the
   * benchmark can see it clearly.
   */
  readonly fieldRectDevice: DeviceRect;
}

export interface PassRunner {
  fieldPass(encoder: GPUCommandEncoder, args: FieldPassArgs): FieldTargets;
  opticsPass(encoder: GPUCommandEncoder, args: OpticsPassArgs): void;
  highlightPass(encoder: GPUCommandEncoder, args: HighlightPassArgs): void;
  /** A 1×1 transparent texture, for binding a backdrop that is not there. */
  readonly placeholderView: GPUTextureView;
  /** Clear a plane canvas before the group passes, which load rather than clear. */
  clearPass(encoder: GPUCommandEncoder, target: GPUTextureView): void;
  /** Attach a timing collector for this frame, or `undefined` to time nothing. */
  setTimeline(timeline: PassTimeline | undefined): void;
  forget(groupId: string): void;
  destroy(): void;
}

export function createPassRunner(context: GpuContext): PassRunner {
  const { device, pool, cache } = context;
  const uniforms = new Map<string, UniformSlot>();
  const storages = new Map<string, StorageSlot>();

  // `rgba16float` tops out near 65504, so the "no surface here" distance is a
  // large FINITE value: an overflow to +Inf would make every later arithmetic on
  // it a NaN, and NaN coverage is not reliably zero.
  const EMPTY_DISTANCE = 65000;

  const placeholder = device.createTexture({
    label: "vitrea:placeholder",
    size: { width: 1, height: 1, depthOrArrayLayers: 1 },
    format: WORKING_TEXTURE_FORMAT,
    usage: fieldUsage(),
  });

  const uniformSlot = (key: string, floats: number): UniformSlot => {
    let slot = uniforms.get(key);
    if (slot === undefined) {
      slot = createUniformSlot(device, floats, `vitrea:uniform:${key}`);
      uniforms.set(key, slot);
    }
    return slot;
  };

  const storageSlot = (key: string): StorageSlot => {
    let slot = storages.get(key);
    if (slot === undefined) {
      slot = createStorageSlot(device, 8 * INSTANCE_BYTES, `vitrea:instances:${key}`);
      storages.set(key, slot);
    }
    return slot;
  };

  const fieldPipeline = (family: FieldFamily): GPURenderPipeline =>
    cache.renderPipeline(pipelineKey.field(family, WORKING_TEXTURE_FORMAT), () => {
      const module = cache.module(`module:field:${family}`, () => fieldModule(family));
      return {
        label: `vitrea:pipeline:field:${family}`,
        layout: "auto",
        vertex: { module, entryPoint: "vs_fullscreen" },
        fragment: {
          module,
          entryPoint: "fs_field",
          targets: [
            { format: WORKING_TEXTURE_FORMAT },
            { format: WORKING_TEXTURE_FORMAT },
            { format: WORKING_TEXTURE_FORMAT },
          ],
        },
        primitive: { topology: "triangle-list" },
      };
    });

  const opticsPipeline = (format: GPUTextureFormat): GPURenderPipeline =>
    cache.renderPipeline(pipelineKey.optics(format, "premultiplied-over"), () => {
      const module = cache.module("module:optics", opticsModule);
      return {
        label: "vitrea:pipeline:optics",
        layout: "auto",
        vertex: { module, entryPoint: "vs_fullscreen" },
        fragment: {
          module,
          entryPoint: "fs_optics",
          targets: [{ format, blend: PREMULTIPLIED_OVER }],
        },
        primitive: { topology: "triangle-list" },
      };
    });

  const highlightPipeline = (format: GPUTextureFormat): GPURenderPipeline =>
    cache.renderPipeline(pipelineKey.highlight(format, "premultiplied-over"), () => {
      const module = cache.module("module:highlight", highlightModule);
      return {
        label: "vitrea:pipeline:highlight",
        layout: "auto",
        vertex: { module, entryPoint: "vs_fullscreen" },
        fragment: {
          module,
          entryPoint: "fs_highlight",
          targets: [{ format, blend: PREMULTIPLIED_OVER }],
        },
        primitive: { topology: "triangle-list" },
      };
    });

  const scoped = (
    pass: GPURenderPassEncoder,
    rect: DeviceRect,
  ): void => {
    pass.setViewport(rect.x, rect.y, rect.width, rect.height, 0, 1);
    // The oversized fullscreen triangle reaches past the viewport; the scissor is
    // what stops it writing another group's pixels.
    pass.setScissorRect(rect.x, rect.y, rect.width, rect.height);
  };

  const placeholderView = placeholder.createView();
  let timeline: PassTimeline | undefined;

  /** `timestampWrites` is only legal when the device enabled `timestamp-query`. */
  const timed = (label: string): { timestampWrites?: GPURenderPassTimestampWrites } => {
    const slot = timeline?.renderSlot(label);
    return slot === undefined ? {} : { timestampWrites: slot };
  };

  return {
    placeholderView,

    fieldPass(encoder, args) {
      // The rect the group occupies on the canvas, and the extent the field is
      // rasterised at. They differ only under the governor's resolution knob, and
      // at scale 1 the second is the first — `Math.round(w * 1)` on an integer.
      const rectWidth = Math.max(1, Math.round(args.rectDevice.width));
      const rectHeight = Math.max(1, Math.round(args.rectDevice.height));
      const width = Math.max(1, Math.round(args.rectDevice.width * args.renderScale));
      const height = Math.max(1, Math.round(args.rectDevice.height * args.renderScale));

      const field = pool.acquire(poolKey.groupField(args.groupId), {
        width,
        height,
        format: WORKING_TEXTURE_FORMAT,
        usage: fieldUsage(),
        label: `vitrea:group:${args.groupId}:field`,
      });
      const aux = pool.acquire(poolKey.groupAux(args.groupId), {
        width,
        height,
        format: WORKING_TEXTURE_FORMAT,
        usage: fieldUsage(),
        label: `vitrea:group:${args.groupId}:aux`,
      });
      const aux2 = pool.acquire(poolKey.groupAux2(args.groupId), {
        width,
        height,
        format: WORKING_TEXTURE_FORMAT,
        usage: fieldUsage(),
        label: `vitrea:group:${args.groupId}:aux2`,
      });

      // Twelve floats: screen, unionP, counts. The group's origin is deliberately
      // absent — instance centres are packed relative to it, so the shader works
      // in group-local coordinates and never adds it back.
      //
      // `screen.xy` is the group's extent in DEVICE px, not the target's, because
      // the shader multiplies it by `screen.z` to recover group-local CSS. Under
      // the resolution knob the target shrinks while the group does not, and it
      // is the group the geometry is expressed in.
      const slot = uniformSlot(`field:${args.groupId}`, 12);
      slot.data[0] = rectWidth;
      slot.data[1] = rectHeight;
      slot.data[2] = args.cssPerDevice;
      // One TARGET pixel wide, so the analytic coverage stays one texel of
      // antialiasing however coarse the target is. At scale 1 the ratio is 1.
      slot.data[3] = args.coverageRampCss * (rectWidth / width);
      slot.data[4] = args.union.neckWidth;
      slot.data[5] = args.union.maxBulge;
      slot.data[6] = args.union.separationThreshold;
      slot.data[7] = 0;
      // `counts` is a vec4u in the shader; a Float32Array cannot write a u32, so
      // the count goes through a Uint32 view of the same words.
      slot.data[9] = 0;
      slot.data[10] = 0;
      slot.data[11] = 0;
      new Uint32Array(slot.data.buffer, slot.data.byteOffset + 32, 1)[0] = args.instanceCount;
      slot.write();

      const instances = storageSlot(args.groupId);
      instances.ensure(Math.max(args.instanceCount, 1) * INSTANCE_BYTES);
      instances.write(args.instances, Math.max(args.instanceCount, 1) * (INSTANCE_BYTES / 4));

      const pipeline = fieldPipeline(args.family);
      const pass = encoder.beginRenderPass({
        label: `vitrea:pass:field:${args.groupId}`,
        ...timed(PASS_LABEL.field),
        colorAttachments: [
          {
            view: field.createView(),
            loadOp: "clear",
            storeOp: "store",
            clearValue: { r: EMPTY_DISTANCE, g: 0, b: -1, a: 0 },
          },
          {
            view: aux.createView(),
            loadOp: "clear",
            storeOp: "store",
            clearValue: { r: 0, g: 0, b: 0, a: 0 },
          },
          {
            view: aux2.createView(),
            loadOp: "clear",
            storeOp: "store",
            clearValue: { r: 0, g: 0, b: 0, a: 0 },
          },
        ],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(
        0,
        device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: slot.buffer } },
            { binding: 1, resource: { buffer: instances.buffer } },
          ],
        }),
      );
      pass.draw(3);
      pass.end();

      return {
        field,
        aux,
        aux2,
        width,
        height,
        upsampled: width !== rectWidth || height !== rectHeight,
      };
    },

    opticsPass(encoder, args) {
      const slot = uniformSlot(`optics:${args.groupId}`, 96);
      const d = slot.data;
      d[0] = args.viewportDevice[0];
      d[1] = args.viewportDevice[1];
      d[2] = args.cssPerDevice;
      d[3] = args.coverageRampCss;
      d[4] = args.fit[0];
      d[5] = args.fit[1];
      d[6] = args.fit[2];
      d[7] = args.fit[3];
      d[8] = args.refractionScale;
      d[9] = args.lensRefractionGain;
      // The inner shadow's depth gain (W12 G2): W2's size gain, which the
      // shadow keeps after the lens moved to its own law below.
      d[10] = args.shadowDepthSizeGainMax;
      d[11] = args.chainMaxLod;
      d[12] = args.tint[0];
      d[13] = args.tint[1];
      d[14] = args.tint[2];
      d[15] = args.tintAlpha;
      d[16] = args.adaptTint[0];
      d[17] = args.adaptTint[1];
      d[18] = args.adaptTint[2];
      d[19] = args.adaptStrength;
      d[20] = args.tintSeed[0];
      d[21] = args.tintSeed[1];
      d[22] = args.tintSeed[2];
      d[23] = args.tintToneAdaptation;
      d[24] = args.tintShade[0];
      d[25] = args.tintShade[1];
      d[26] = args.tintShade[2];
      d[27] = args.sizeFold;
      d[28] = args.rimWidth;
      d[29] = args.rimAlpha;
      d[30] = args.specularPower;
      d[31] = args.specularGain;
      d[32] = args.lightDirection[0];
      d[33] = args.lightDirection[1];
      d[34] = args.shadowDepth;
      d[35] = args.shadowAlpha;
      d[36] = args.backdrop === undefined ? 0 : 1;
      d[37] = args.fields.width;
      d[38] = args.fields.height;
      d[39] = args.fields.upsampled ? 1 : 0;
      d[40] = args.sizeScatterGainMax;
      d[41] = args.sizeOcclusionGain;
      d[42] = args.sizeShadowGainMax;
      d[43] = args.bodyChainLod;
      d[44] = args.backdropTone[0];
      // The shader divides by `max(high - low, 1e-6)` rather than calling
      // `smoothstep`, so a coinciding pair degrades to a step instead of a NaN —
      // but the floor is kept here too so both tiers see the same edges.
      d[45] = Math.max(args.backdropTone[1], args.backdropTone[0] + 1e-4);
      d[46] = args.backdropTone[2];
      d[47] = args.backdropTone[3];
      d[48] = args.backdropToneColour[0];
      d[49] = args.backdropToneColour[1];
      d[50] = args.backdropToneColour[2];
      d[51] = args.backdropToneColour[3];
      d[52] = args.outerShadow[0];
      d[53] = args.outerShadow[1];
      d[54] = args.outerShadow[2];
      d[55] = args.outerShadow[3];
      d[56] = args.outerShadowSizeGain;
      d[57] = args.outerShadowRectCssHeight;
      // The depth ramp's THICK start (W13 G1's third form), in the first of
      // this vec4's two padding slots. The scatter vec4 holds four numbers
      // already and the ramp's second start needs a home; a padding slot of a
      // vec4 the shader reads anyway costs no bytes and no second binding, and
      // the shader's own comment names it where it is read.
      d[58] = args.sizeScatterRampStartThick;
      // The heavy width's gain at the scatter span curve's TOP (W15 G1's
      // re-form, claims §5.70 §4 and §7), in this vec4's second padding slot.
      // The gain's near end is `size.x` and that vec4 is full; this one already
      // carries the ramp's other span-graded end, so the body's two curves over
      // the same smoothstep sit beside each other. The layout's size is
      // unchanged — the slot was written as zero.
      d[59] = args.sizeScatterGainFar;
      // The response law's anchors and rows (W9), and the linear backdrop mean
      // the solve composites against.
      d[60] = args.backdropToneAnchorX[0];
      d[61] = args.backdropToneAnchorX[1];
      d[62] = args.backdropToneAnchorX[2];
      d[63] = args.backdropToneLinearMean;
      d[64] = args.backdropToneResponseThin[0];
      d[65] = args.backdropToneResponseThin[1];
      d[66] = args.backdropToneResponseThin[2];
      d[67] = args.backdropToneResponseStrength;
      d[68] = args.backdropToneResponseThick[0];
      d[69] = args.backdropToneResponseThick[1];
      d[70] = args.backdropToneResponseThick[2];
      d[71] = 0;
      d[72] = args.sizeScatterFloor;
      // The depth ramp's THIN start (W13 G1), in the slot the retired
      // `sizeScatterSpanMax` held — the scatter facet's second number, where its
      // second number has always been. The thick end is at d[58].
      d[73] = args.sizeScatterRampStartThin;
      d[74] = args.sizeSpanMin;
      d[75] = args.sizeSpanMax;
      // The lens law (W12 G2, claims §5.51): the reference's height and amount
      // laws, then the profile's extent, exponent and ovalization, then the
      // ovalization's knee. The shader evaluates every one per pixel from the
      // thickness and the span the field carries.
      d[76] = args.lensHeightPerSpan;
      d[77] = args.lensHeightMax;
      d[78] = args.lensAmountPerSpan;
      d[79] = args.lensAmountMax;
      d[80] = args.lensExtentGain;
      d[81] = args.lensProfileExponent;
      d[82] = args.lensOvalization;
      d[83] = args.lensThicknessReference;
      d[84] = args.lensOvalizationSpanMin;
      d[85] = args.lensOvalizationSpanMax;
      // The depth ramp's reach in CSS px (W13 G1), in the first of this vec4's
      // two padding slots rather than in a vec4 of its own — the slot W12 G3's
      // retired scale shift briefly held.
      d[86] = args.sizeScatterRampReachCssPx;
      // The scatter span curve's band top (W11c), in this vec4's second padding
      // slot: W13 G1's re-forming keeps the curve underneath the ramp as its
      // deep value, so the shader needs both the span and the depth.
      d[87] = args.sizeScatterSpanMax;
      // The outer shadow's second regime and its second term (W14 G1). The
      // buffer grows by two vec4s rather than borrowing the three free slots
      // above, because the shadow's own block is `shadow` / `shadowSize` and a
      // shadow constant living in `lensOval.zw` would be a layout nobody could
      // read. `d[91]` stays free.
      d[88] = args.outerShadowThick[0];
      d[89] = args.outerShadowThick[1];
      d[90] = args.outerShadowThick[2];
      // The depth ramp's FAR start (W13 G1's fourth form), in the padding slot
      // W14 left free beside the thick regime's three anchors; the shader's own
      // comment names it where it is read.
      d[91] = args.sizeScatterRampStartFar;
      d[92] = args.outerShadowLift[0];
      d[93] = args.outerShadowLift[1];
      d[94] = args.outerShadowLift[2];
      d[95] = args.outerShadowLift[3];
      slot.write();

      const chain = args.backdrop?.chain ?? placeholderView;
      const body = args.backdrop?.body ?? placeholderView;

      const pipeline = opticsPipeline(args.targetFormat);
      const pass = encoder.beginRenderPass({
        label: `vitrea:pass:optics:${args.groupId}`,
        ...timed(PASS_LABEL.optics),
        colorAttachments: [{ view: args.target, loadOp: "load", storeOp: "store" }],
      });
      pass.setPipeline(pipeline);
      scoped(pass, args.rectDevice);
      pass.setBindGroup(
        0,
        device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: slot.buffer } },
            { binding: 1, resource: args.fields.field.createView() },
            { binding: 2, resource: args.fields.aux.createView() },
            { binding: 3, resource: context.chainSampler },
            { binding: 4, resource: chain },
            { binding: 5, resource: body },
            // Linear, no mips: the field targets have one level, and this is only
            // read at all when the governor shrank them below the group's rect.
            { binding: 6, resource: context.flatSampler },
            { binding: 7, resource: args.fields.aux2.createView() },
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    },

    highlightPass(encoder, args) {
      const slot = uniformSlot(`highlight:${args.groupId}`, 32);
      const d = slot.data;
      d[0] = args.viewportDevice[0];
      d[1] = args.viewportDevice[1];
      d[2] = args.cssPerDevice;
      d[3] = 0;
      d[4] = args.sweep;
      d[5] = args.sweepBandRadians;
      d[6] = args.sweepGain;
      d[7] = args.rimWidth;
      d[8] = args.pressPointCss[0];
      d[9] = args.pressPointCss[1];
      d[10] = args.glowRadiusCss;
      d[11] = args.glowGain;
      d[12] = args.colour[0];
      d[13] = args.colour[1];
      d[14] = args.colour[2];
      d[15] = 0;
      d[16] = args.fields.width;
      d[17] = args.fields.height;
      d[18] = args.fields.upsampled ? 1 : 0;
      d[19] = 0;
      d[20] = args.backdropTone[0];
      d[21] = Math.max(args.backdropTone[1], args.backdropTone[0] + 1e-4);
      d[22] = args.backdropTone[2];
      d[23] = args.backdropTone[3];
      d[24] = args.backdropToneLevel;
      d[25] = args.sizeSpanMin;
      d[26] = args.sizeSpanMax;
      d[27] = args.sizeFold;
      /*
       * This pass's uv into the field texture's uv (W8). The field rect is the
       * one the shadow needs; this pass is scoped to the one the surface needs,
       * which is smaller, so the two no longer index one-to-one.
       *
       * Derived from the two rects rather than passed in already-divided, so the
       * one place that knows both is the one place that computes it.
       */
      const fieldRect = args.fieldRectDevice;
      d[28] = args.rectDevice.width / Math.max(fieldRect.width, 1e-6);
      d[29] = args.rectDevice.height / Math.max(fieldRect.height, 1e-6);
      d[30] = (args.rectDevice.x - fieldRect.x) / Math.max(fieldRect.width, 1e-6);
      d[31] = (args.rectDevice.y - fieldRect.y) / Math.max(fieldRect.height, 1e-6);
      slot.write();

      const pipeline = highlightPipeline(args.targetFormat);
      const pass = encoder.beginRenderPass({
        label: `vitrea:pass:highlight:${args.groupId}`,
        ...timed(PASS_LABEL.highlight),
        colorAttachments: [{ view: args.target, loadOp: "load", storeOp: "store" }],
      });
      pass.setPipeline(pipeline);
      scoped(pass, args.rectDevice);
      pass.setBindGroup(
        0,
        device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: { buffer: slot.buffer } },
            { binding: 1, resource: args.fields.field.createView() },
            { binding: 2, resource: args.fields.aux.createView() },
            { binding: 3, resource: context.flatSampler },
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    },

    clearPass(encoder, target) {
      // Deliberately untimed. A render pass with no draw commands is resolved by
      // the driver without ever writing its timestamp pair, so a slot taken here
      // comes back as (0, 0) — indistinguishable from a query that failed. Leaving
      // it out is what lets a non-zero anomaly count mean something.
      const pass = encoder.beginRenderPass({
        label: "vitrea:pass:clear",
        colorAttachments: [
          {
            view: target,
            loadOp: "clear",
            storeOp: "store",
            clearValue: { r: 0, g: 0, b: 0, a: 0 },
          },
        ],
      });
      pass.end();
    },

    setTimeline(next) {
      timeline = next;
    },

    forget(groupId) {
      pool.release(poolKey.groupField(groupId));
      pool.release(poolKey.groupAux(groupId));
      pool.release(poolKey.groupAux2(groupId));
      storages.get(groupId)?.destroy();
      storages.delete(groupId);
      for (const key of [`field:${groupId}`, `optics:${groupId}`, `highlight:${groupId}`]) {
        uniforms.get(key)?.buffer.destroy();
        uniforms.delete(key);
      }
    },

    destroy() {
      for (const slot of uniforms.values()) slot.buffer.destroy();
      uniforms.clear();
      for (const slot of storages.values()) slot.destroy();
      storages.clear();
      placeholder.destroy();
    },
  };
}

/** The output format the plane canvases and the golden readback both use (X5). */
export const CANVAS_FORMAT = OUTPUT_TEXTURE_FORMAT;
