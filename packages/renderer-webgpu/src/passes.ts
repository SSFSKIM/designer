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

const FIELD_USAGE = GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING;

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
  /** Group rect in viewport CSS px. */
  readonly originCss: readonly [number, number];
  readonly sizeCss: readonly [number, number];
  readonly rectDevice: DeviceRect;
  /** CSS px per device px. */
  readonly cssPerDevice: number;
  /** Coverage ramp width in CSS px. One device pixel, unless the governor widens it. */
  readonly coverageRampCss: number;
  readonly instances: Float32Array;
  readonly instanceCount: number;
  readonly union: { readonly neckWidth: number; readonly maxBulge: number; readonly separationThreshold: number };
}

export interface FieldTargets {
  readonly field: GPUTexture;
  readonly aux: GPUTexture;
  readonly width: number;
  readonly height: number;
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
  readonly bodyLodPerPx: number;
  readonly rimLodBias: number;
  readonly chainMaxLod: number;
  readonly tint: readonly [number, number, number];
  readonly tintAlpha: number;
  readonly adaptTint: readonly [number, number, number];
  readonly adaptStrength: number;
  readonly rimWidth: number;
  readonly rimAlpha: number;
  readonly specularPower: number;
  readonly specularGain: number;
  readonly lightDirection: readonly [number, number];
  readonly shadowDepth: number;
  readonly shadowAlpha: number;
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
    usage: FIELD_USAGE,
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
          targets: [{ format: WORKING_TEXTURE_FORMAT }, { format: WORKING_TEXTURE_FORMAT }],
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
      const width = Math.max(1, Math.round(args.rectDevice.width));
      const height = Math.max(1, Math.round(args.rectDevice.height));

      const field = pool.acquire(poolKey.groupField(args.groupId), {
        width,
        height,
        format: WORKING_TEXTURE_FORMAT,
        usage: FIELD_USAGE,
        label: `vitrea:group:${args.groupId}:field`,
      });
      const aux = pool.acquire(poolKey.groupAux(args.groupId), {
        width,
        height,
        format: WORKING_TEXTURE_FORMAT,
        usage: FIELD_USAGE,
        label: `vitrea:group:${args.groupId}:aux`,
      });

      const slot = uniformSlot(`field:${args.groupId}`, 16);
      slot.data[0] = args.originCss[0];
      slot.data[1] = args.originCss[1];
      slot.data[2] = args.sizeCss[0];
      slot.data[3] = args.sizeCss[1];
      slot.data[4] = width;
      slot.data[5] = height;
      slot.data[6] = args.cssPerDevice;
      slot.data[7] = args.coverageRampCss;
      slot.data[8] = args.union.neckWidth;
      slot.data[9] = args.union.maxBulge;
      slot.data[10] = args.union.separationThreshold;
      slot.data[11] = 0;
      // `counts` is a vec4u in the shader; a Float32Array cannot write a u32, so
      // the count goes through a Uint32 view of the same words.
      slot.data[13] = 0;
      slot.data[14] = 0;
      slot.data[15] = 0;
      new Uint32Array(slot.data.buffer, slot.data.byteOffset + 48, 1)[0] = args.instanceCount;
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

      return { field, aux, width, height };
    },

    opticsPass(encoder, args) {
      const slot = uniformSlot(`optics:${args.groupId}`, 32);
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
      d[9] = args.bodyLodPerPx;
      d[10] = args.rimLodBias;
      d[11] = args.chainMaxLod;
      d[12] = args.tint[0];
      d[13] = args.tint[1];
      d[14] = args.tint[2];
      d[15] = args.tintAlpha;
      d[16] = args.adaptTint[0];
      d[17] = args.adaptTint[1];
      d[18] = args.adaptTint[2];
      d[19] = args.adaptStrength;
      d[20] = args.rimWidth;
      d[21] = args.rimAlpha;
      d[22] = args.specularPower;
      d[23] = args.specularGain;
      d[24] = args.lightDirection[0];
      d[25] = args.lightDirection[1];
      d[26] = args.shadowDepth;
      d[27] = args.shadowAlpha;
      d[28] = args.backdrop === undefined ? 0 : 1;
      d[29] = args.fields.width;
      d[30] = args.fields.height;
      d[31] = 0;
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
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    },

    highlightPass(encoder, args) {
      const slot = uniformSlot(`highlight:${args.groupId}`, 20);
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
      d[18] = 0;
      d[19] = 0;
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
          ],
        }),
      );
      pass.draw(3);
      pass.end();
    },

    clearPass(encoder, target) {
      const pass = encoder.beginRenderPass({
        label: "vitrea:pass:clear",
        ...timed(PASS_LABEL.clear),
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
