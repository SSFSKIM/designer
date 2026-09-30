/**
 * **W42's body law, LT: the GPU stage** (G2 `implementation-design.md` §2.1–§2.6, revised in §11
 * and §12). It runs between the field pass and the optics pass for a group whose folded
 * `bodyLawStrength` is above 0 and whose source carries the pyramid's encoded level 0, and it
 * leaves one group texture, **A**: rgb the law's argument M in encoded sRGB, a the wide term's
 * encoded luma L(W). The optics pass reads A at the refracted position (`wgsl/optics.ts`
 * `body_law_body`).
 *
 * Per law surface, on its footprint R_fp (`bodyLawSurfacePlan`) at one texel per device pixel:
 *
 * 1. the capture S0 from the encoded level 0, through the group's fit;
 * 2. the floor, memo C's Gaussian at 0.4 capture texels, clamp mode: S;
 * 3. every stored width — the narrow levels and W — in separable pairs of two targets:
 *    below 12 device px directly on S in the plan's edge mode, above it on S decimated by
 *    q = 2 (q = 4 from 48), `forward.py`'s `_blur_decimated`;
 * 4. one draw into A, which first holds the captured backdrop everywhere (R2).
 *
 * Every tile is rgba32float in the form (value·weight, weight) (`wgsl/body-law.ts`), and the
 * Gaussian weights are the instrument's, computed here in f64.
 *
 * The stage is rebuilt only when what it reads moves — the source's build, the fit, the
 * viewport, the group's rect, the surfaces' boxes and corners, the device ratio or a law leaf —
 * on the silhouette tone's model (`silhouette-tone.ts`). A static page rebuilds nothing.
 */

import {
  bodyLawDecimation,
  bodyLawSurfacePlan,
  type BodyLawDeviceRect,
  type BodyLawSurfacePlan,
} from "./body-law";
import {
  createStorageSlot,
  createUniformSlot,
  type GpuContext,
  type StorageSlot,
  type UniformSlot,
} from "./gpu-context";
import type { ResolvedSurface } from "./instances";
import type { MaterialProfile } from "./material";
import type { DeviceRect } from "./passes";
import type { PyramidResources } from "./pyramid";
import { packToneShapes } from "./silhouette-tone";
import { PASS_LABEL, type PassTimeline } from "./timing";
import {
  bodyLawBlurModule,
  bodyLawCaptureModule,
  bodyLawCompositeModule,
  bodyLawDecimateModule,
} from "./wgsl";

/** Every tile and A (§11.1, ruled §12 item 3). */
export const BODY_LAW_TILE_FORMAT: GPUTextureFormat = "rgba32float";

/** `ndimage`'s `truncate`, the instrument's `TRUNCATE` (`forward.py:37`). */
const TRUNCATE = 4;

/** The stored narrow levels the composite binds: six interior levels and the contour level. */
export const BODY_LAW_MAX_LEVELS = 7;

/**
 * The instrument's one-dimensional Gaussian: `ndimage`'s kernel at `truncate = 4`, radius
 * `int(4σ + 0.5)`, normalised over its taps (`scipy.ndimage._filters._gaussian_kernel1d`).
 */
export function bodyLawGaussianWeights(sigma: number): Float64Array {
  const radius = Math.floor(TRUNCATE * sigma + 0.5);
  const weights = new Float64Array(2 * radius + 1);
  let sum = 0;
  for (let k = -radius; k <= radius; k++) {
    const w = Math.exp((-0.5 * k * k) / (sigma * sigma));
    weights[k + radius] = w;
    sum += w;
  }
  for (let i = 0; i < weights.length; i++) weights[i] = weights[i]! / sum;
  return weights;
}

/**
 * `_blur_decimated`'s padding, in full-resolution texels: `ceil(4σ/q + 2)·q`. A multiple of q,
 * so every width's blocks are the same blocks.
 */
export function bodyLawDecimationPad(sigma: number, q: number): number {
  return Math.ceil((TRUNCATE * sigma) / q + 2) * q;
}

/** The width the decimated grid is blurred at: the block mean and the return take their share. */
export function bodyLawDecimatedSigma(sigma: number, q: number): number {
  return Math.sqrt(sigma * sigma - (q * q - 1) / 12 - (q * q) / 6) / q;
}

/** One stored width of a surface: a narrow level (0…6) or W (`"wide"`). */
export interface BodyLawWidth {
  readonly role: number | "wide";
  readonly sigma: number;
  /** 0 where the width is the floored capture itself (σ below `forward.py`'s 1e-3). */
  readonly q: 0 | 1 | 2 | 4;
}

/** The passes one surface runs, grouped as they are encoded. */
export interface BodyLawSurfaceSchedule {
  readonly plan: BodyLawSurfacePlan;
  readonly widths: readonly BodyLawWidth[];
  /** Per decimation factor present: the shared padding and the decimated grid's extent. */
  readonly grids: readonly {
    readonly q: 1 | 2 | 4;
    readonly pad: number;
    readonly width: number;
    readonly height: number;
    /** The widths blurred on this grid, in pairs; a pair of one is a one-target pass. */
    readonly pairs: readonly (readonly BodyLawWidth[])[];
  }[];
}

/**
 * **The schedule for one surface** — which widths are stored, at which decimation, on which
 * grid and in which pairs. Pure, so a test reads it without a device.
 *
 * The widths of one q share one decimated grid, padded by the largest padding any of them
 * needs. In exact arithmetic that is each width's own `_blur_decimated`: the paddings are
 * multiples of q, so the blocks coincide, and a narrower width's kernel plus the bilinear return
 * never reaches the extra rows (its own padding already exceeds 4 σ_d + 2 texels of the grid).
 */
export function bodyLawSchedule(plan: BodyLawSurfacePlan): BodyLawSurfaceSchedule {
  const widths: BodyLawWidth[] = [
    ...plan.narrowSigmaDevicePx.map((sigma, role): BodyLawWidth => ({
      role, sigma, q: sigma < 1e-3 ? 0 : bodyLawDecimation(sigma),
    })),
    { role: "wide", sigma: plan.wideSigmaDevicePx,
      q: plan.wideSigmaDevicePx < 1e-3 ? 0 : bodyLawDecimation(plan.wideSigmaDevicePx) },
  ];
  const fw = plan.footprint.x1 - plan.footprint.x0;
  const fh = plan.footprint.y1 - plan.footprint.y0;
  const grids: BodyLawSurfaceSchedule["grids"][number][] = [];
  for (const q of [1, 2, 4] as const) {
    const members = widths.filter((width) => width.q === q);
    if (members.length === 0) continue;
    const pad = q === 1 ? 0 : Math.max(...members.map((width) => bodyLawDecimationPad(width.sigma, q)));
    const pairs: BodyLawWidth[][] = [];
    for (let i = 0; i < members.length; i += 2) pairs.push(members.slice(i, i + 2));
    grids.push({
      q, pad,
      width: q === 1 ? fw : Math.ceil((fw + 2 * pad) / q),
      height: q === 1 ? fh : Math.ceil((fh + 2 * pad) / q),
      pairs,
    });
  }
  return { plan, widths, grids };
}

/**
 * The device pixels whose centres the group's fit maps into the source, [x0, x1) × [y0, y1):
 * R_fp is clipped to it, as `forward.py`'s crop is clipped to its canvas (§2.2).
 */
export function bodyLawSourceExtent(
  viewportDevice: readonly [number, number],
  fit: readonly [number, number, number, number],
): BodyLawDeviceRect {
  const edge = (axis: 0 | 1) => {
    const scale = fit[axis];
    const offset = fit[axis + 2]!;
    const a = (viewportDevice[axis] * (0 - offset)) / scale;
    const b = (viewportDevice[axis] * (1 - offset)) / scale;
    const low = Math.min(a, b), high = Math.max(a, b);
    // `+ 0` so a clip at the plane's origin is +0 rather than the −0 `ceil` returns for it.
    return [Math.ceil(low - 0.5 - 1e-6) + 0, Math.floor(high - 0.5 + 1e-6) + 1] as const;
  };
  const [x0, x1] = edge(0);
  const [y0, y1] = edge(1);
  return { x0, y0, x1, y1 };
}

export interface BodyLawStageArgs {
  /** The group's resource identity on this plane (`groupResourceId`). */
  readonly resourceId: string;
  readonly surfaces: readonly ResolvedSurface[];
  /** The group's source; the stage runs only where it carries `encoded`. */
  readonly pyramid: PyramidResources;
  /** A's extent on the plane: the group's own surface rect, device px. */
  readonly rectDevice: DeviceRect;
  readonly viewportDevice: readonly [number, number];
  readonly fit: readonly [number, number, number, number];
  readonly devicePixelRatio: number;
  readonly material: MaterialProfile;
}

/** What the optics pass reads: A and where it lies on the plane. */
export interface BodyLawStageOutput {
  readonly view: GPUTextureView;
  readonly origin: readonly [number, number];
  readonly size: readonly [number, number];
}

const tileUsage = (): GPUTextureUsageFlags =>
  GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING;

/** The law leaves A depends on, in the order the cache key lists them. */
const lawKey = (m: MaterialProfile): readonly unknown[] => [
  m.bodyLawK, m.bodyLawLambda, m.bodyLawNormal, m.bodyLawHinge, m.bodyLawPose, m.bodyLawKnee,
  m.bodyLawEdgeSwap, m.bodyLawWidthUnit, m.bodyLawEncodedAveraging,
];

interface Entry {
  key: string | undefined;
  encoded: GPUTexture | undefined;
  a: GPUTexture | undefined;
  output: BodyLawStageOutput | undefined;
  /** Encoded this frame and not yet submitted: a cancelled frame built nothing. */
  unsubmitted: boolean;
  readonly textures: Set<string>;
  readonly uniforms: Map<string, UniformSlot>;
  readonly storages: Map<string, StorageSlot>;
}

export interface BodyLawStage {
  /** Encode the stage for one group, or reuse A; `undefined` where the source has no encoded level 0. */
  draw(encoder: GPUCommandEncoder, args: BodyLawStageArgs): BodyLawStageOutput | undefined;
  setTimeline(timeline: PassTimeline | undefined): void;
  afterSubmit(): void;
  cancelQueued(): void;
  forget(resourceId: string): void;
  destroy(): void;
  /** Stage rebuilds since creation, for tests and the bench. */
  readonly rebuilds: number;
}

export function createBodyLawStage(context: GpuContext): BodyLawStage {
  const { device, cache, pool } = context;
  const entries = new Map<string, Entry>();
  let timeline: PassTimeline | undefined;
  let rebuilds = 0;

  const timed = (): { timestampWrites?: GPURenderPassTimestampWrites } => {
    const slot = timeline?.renderSlot(PASS_LABEL.bodyLaw);
    return slot === undefined ? {} : { timestampWrites: slot };
  };

  const pipeline = (
    key: string,
    moduleKey: string,
    module: () => string,
    entryPoint: string,
    targets: number,
  ): GPURenderPipeline =>
    cache.renderPipeline(`body-law:${key}`, () => ({
      label: `vitrea:pipeline:body-law:${key}`,
      layout: "auto",
      vertex: { module: cache.module(`module:body-law:${moduleKey}`, module),
        entryPoint: "vs_fullscreen" },
      fragment: {
        module: cache.module(`module:body-law:${moduleKey}`, module),
        entryPoint,
        targets: Array.from({ length: targets }, () => ({ format: BODY_LAW_TILE_FORMAT })),
      },
      primitive: { topology: "triangle-list" },
    }));
  const capturePipeline = () =>
    pipeline("capture", "capture", bodyLawCaptureModule, "fs_capture", 1);
  const initPipeline = () => pipeline("init", "capture", bodyLawCaptureModule, "fs_init", 1);
  const blurPipeline = (targets: 1 | 2) =>
    pipeline(`blur:${targets}`, `blur:${targets}`, () => bodyLawBlurModule(targets), "fs_blur",
      targets);
  const decimatePipeline = () =>
    pipeline("decimate", "decimate", bodyLawDecimateModule, "fs_decimate", 1);
  const compositePipeline = () =>
    pipeline("composite", "composite", bodyLawCompositeModule, "fs_composite", 1);

  const destroyEntry = (resourceId: string, entry: Entry): void => {
    for (const key of entry.textures) pool.release(key);
    for (const slot of entry.uniforms.values()) slot.buffer.destroy();
    for (const slot of entry.storages.values()) slot.destroy();
    entries.delete(resourceId);
  };

  return {
    get rebuilds() {
      return rebuilds;
    },

    setTimeline(next) {
      timeline = next;
    },

    draw(encoder, args) {
      const { pyramid, material, surfaces, rectDevice } = args;
      const encoded = pyramid.encoded;
      if (encoded === undefined || surfaces.length === 0) {
        const stale = entries.get(args.resourceId);
        if (stale !== undefined) destroyEntry(args.resourceId, stale);
        return undefined;
      }
      let entry = entries.get(args.resourceId);
      if (entry === undefined) {
        entry = {
          key: undefined, encoded: undefined, a: undefined, output: undefined, unsubmitted: false,
          textures: new Set(), uniforms: new Map(), storages: new Map(),
        };
        entries.set(args.resourceId, entry);
      }
      const dpr = args.devicePixelRatio;
      const shapeData = packToneShapes(surfaces, dpr);
      const key = JSON.stringify([
        pyramid.sourceId, pyramid.builtEpoch, pyramid.sizeEpoch, pyramid.plan.width,
        pyramid.plan.height, args.viewportDevice, args.fit, rectDevice, dpr, [...shapeData],
        surfaces.map((surface) => [surface.centre, surface.shape.channels.size]),
        lawKey(material),
      ]);
      const aKey = `body-law:${args.resourceId}:A`;
      if (entry.key === key && entry.encoded === encoded && entry.a !== undefined &&
          pool.peek(aKey) === entry.a && entry.output !== undefined) {
        return entry.output;
      }
      rebuilds += 1;

      const used = new Set<string>();
      const texture = (name: string, width: number, height: number): GPUTexture => {
        const poolKey = `body-law:${args.resourceId}:${name}`;
        used.add(poolKey);
        return pool.acquire(poolKey, {
          width, height, format: BODY_LAW_TILE_FORMAT, usage: tileUsage(),
          label: `vitrea:body-law:${args.resourceId}:${name}`,
        });
      };
      const usedSlots = new Set<string>();
      const uniform = (name: string, data: readonly number[]): UniformSlot => {
        usedSlots.add(name);
        let slot = entry.uniforms.get(name);
        if (slot === undefined || slot.data.length < data.length) {
          slot?.buffer.destroy();
          slot = createUniformSlot(device, data.length, `vitrea:uniform:body-law:${args.resourceId}:${name}`);
          entry.uniforms.set(name, slot);
        }
        slot.data.fill(0);
        slot.data.set(data);
        slot.write();
        return slot;
      };
      const storage = (name: string, data: Float32Array): GPUBuffer => {
        usedSlots.add(name);
        let slot = entry.storages.get(name);
        if (slot === undefined) {
          slot = createStorageSlot(device, data.byteLength,
            `vitrea:storage:body-law:${args.resourceId}:${name}`);
          entry.storages.set(name, slot);
        }
        const buffer = slot.ensure(data.byteLength);
        slot.write(data, data.length);
        return buffer;
      };
      const fullPass = (
        label: string,
        views: readonly GPUTextureView[],
        pipe: GPURenderPipeline,
        bindings: readonly GPUBindGroupEntry[],
      ): void => {
        const pass = encoder.beginRenderPass({
          label: `vitrea:pass:body-law:${label}`,
          ...timed(),
          colorAttachments: views.map((view) => ({
            view, loadOp: "clear" as const, storeOp: "store" as const,
            clearValue: { r: 0, g: 0, b: 0, a: 0 },
          })),
        });
        pass.setPipeline(pipe);
        pass.setBindGroup(0, device.createBindGroup({
          layout: pipe.getBindGroupLayout(0), entries: [...bindings],
        }));
        pass.draw(3);
        pass.end();
      };
      const encodedView = encoded.createView();
      const captureUniform = (name: string, origin: readonly [number, number]): UniformSlot =>
        uniform(name, [
          args.viewportDevice[0], args.viewportDevice[1], origin[0], origin[1],
          ...args.fit,
          material.bodyLawEncodedAveraging === 1 ? 0 : 1, 0, 0, 0,
        ]);

      /** One separable pass of up to two widths, `axis` 0 horizontal, 1 vertical. */
      const blurPass = (
        label: string,
        sources: readonly [GPUTextureView, GPUTextureView],
        targets: readonly GPUTextureView[],
        sigmas: readonly number[],
        axis: 0 | 1,
        zeroPadding: boolean,
      ): void => {
        const kernels = sigmas.map(bodyLawGaussianWeights);
        const header = [
          axis === 0 ? 1 : 0, axis === 1 ? 1 : 0, zeroPadding ? 1 : 0, 0,
          (kernels[0]!.length - 1) / 2, kernels[1] === undefined ? 0 : (kernels[1].length - 1) / 2,
          0, kernels[0]!.length,
        ];
        const data = new Float32Array(8 + kernels.reduce((n, k) => n + k.length, 0));
        data.set(header);
        let at = 8;
        for (const kernel of kernels) {
          data.set(kernel, at);
          at += kernel.length;
        }
        const two = targets.length === 2;
        fullPass(label, targets, blurPipeline(two ? 2 : 1), [
          { binding: 0, resource: { buffer: storage(label, data) } },
          { binding: 1, resource: sources[0] },
          ...(two ? [{ binding: 2, resource: sources[1] }] : []),
        ]);
      };

      const extent = bodyLawSourceExtent(args.viewportDevice, args.fit);
      interface Built {
        readonly index: number;
        readonly schedule: BodyLawSurfaceSchedule;
        readonly floored: GPUTextureView;
        readonly tiles: ReadonlyMap<BodyLawWidth["role"], { view: GPUTextureView; q: number; pad: number }>;
      }
      const built: Built[] = [];
      surfaces.forEach((surface, index) => {
        const plan = bodyLawSurfacePlan(
          { centre: surface.centre, size: surface.shape.channels.size }, dpr, material, extent,
        );
        const fw = plan.footprint.x1 - plan.footprint.x0;
        const fh = plan.footprint.y1 - plan.footprint.y0;
        if (fw <= 0 || fh <= 0) return;
        const schedule = bodyLawSchedule(plan);
        const name = (part: string) => `${index}:${part}`;
        const zero = plan.edge === "normalised";

        // 1. The capture, and 2. its floor (always clamp: `forward.py` `Cell.S`).
        const capture = texture(name("capture"), fw, fh).createView();
        fullPass(name("capture"), [capture], capturePipeline(), [
          { binding: 0, resource: { buffer: captureUniform(name("capture"),
            [plan.footprint.x0, plan.footprint.y0]).buffer } },
          { binding: 1, resource: encodedView },
        ]);
        const scratch0 = texture(name("scratch:1:0"), fw, fh).createView();
        const floored = texture(name("floored"), fw, fh).createView();
        blurPass(name("floor:h"), [capture, capture], [scratch0], [plan.floorSigmaDevicePx], 0, false);
        blurPass(name("floor:v"), [scratch0, scratch0], [floored], [plan.floorSigmaDevicePx], 1, false);

        // 3. Every stored width, grid by grid and pair by pair.
        const tiles = new Map<BodyLawWidth["role"], { view: GPUTextureView; q: number; pad: number }>();
        for (const width of schedule.widths) {
          if (width.q === 0) tiles.set(width.role, { view: floored, q: 1, pad: 0 });
        }
        for (const grid of schedule.grids) {
          let input = floored;
          if (grid.q > 1) {
            input = texture(name(`decimated:${grid.q}`), grid.width, grid.height).createView();
            fullPass(name(`decimate:${grid.q}`), [input], decimatePipeline(), [
              { binding: 0, resource: { buffer: uniform(name(`decimate:${grid.q}`),
                [grid.q, grid.pad, zero ? 1 : 0, 0]).buffer } },
              { binding: 1, resource: floored },
            ]);
          }
          const h0 = texture(name(`scratch:${grid.q}:0`), grid.width, grid.height).createView();
          const h1 = grid.pairs.some((pair) => pair.length === 2)
            ? texture(name(`scratch:${grid.q}:1`), grid.width, grid.height).createView()
            : h0;
          // The decimated grid is blurred with its edge held (`forward.py`): the zeros of the
          // normalised mode are already in its padding.
          const gridZero = grid.q === 1 && zero;
          grid.pairs.forEach((pair, p) => {
            const sigmas = pair.map((width) =>
              grid.q === 1 ? width.sigma : bodyLawDecimatedSigma(width.sigma, grid.q));
            const outs = pair.map((width) => {
              const view = texture(name(`tile:${width.role}`), grid.width, grid.height).createView();
              tiles.set(width.role, { view, q: grid.q, pad: grid.pad });
              return view;
            });
            const scratch = pair.length === 2 ? [h0, h1] : [h0];
            blurPass(name(`w${grid.q}:${p}:h`), [input, input], scratch, sigmas, 0, gridZero);
            blurPass(name(`w${grid.q}:${p}:v`), [h0, h1], outs, sigmas, 1, gridZero);
          });
        }
        built.push({ index, schedule, floored, tiles });
      });

      // 4. A: the captured backdrop everywhere, then each surface over the pixels it owns.
      const a = texture("A", rectDevice.width, rectDevice.height);
      const aView = a.createView();
      const shapes = storage("shapes", shapeData);
      const pass = encoder.beginRenderPass({
        label: "vitrea:pass:body-law:A",
        ...timed(),
        colorAttachments: [{ view: aView, loadOp: "clear", storeOp: "store",
          clearValue: { r: 0, g: 0, b: 0, a: 0 } }],
      });
      const init = initPipeline();
      pass.setPipeline(init);
      pass.setBindGroup(0, device.createBindGroup({ layout: init.getBindGroupLayout(0), entries: [
        { binding: 0, resource: { buffer: captureUniform("init", [rectDevice.x, rectDevice.y]).buffer } },
        { binding: 1, resource: encodedView },
      ] }));
      pass.draw(3);
      const composite = compositePipeline();
      pass.setPipeline(composite);
      for (const { index, schedule, floored, tiles } of built) {
        const { plan } = schedule;
        const x0 = Math.max(plan.footprint.x0, rectDevice.x);
        const y0 = Math.max(plan.footprint.y0, rectDevice.y);
        const x1 = Math.min(plan.footprint.x1, rectDevice.x + rectDevice.width);
        const y1 = Math.min(plan.footprint.y1, rectDevice.y + rectDevice.height);
        if (x1 <= x0 || y1 <= y0) continue;
        const levels = plan.narrowSigmaDevicePx;
        const level = (k: number) => tiles.get(k) ?? { view: floored, q: 1, pad: 0 };
        const wide = tiles.get("wide") ?? { view: floored, q: 1, pad: 0 };
        const lanes = (read: (k: number) => number) =>
          Array.from({ length: 8 }, (_, k) => (k < levels.length ? read(k) : 0));
        const unit = material.bodyLawK[0] * 5 * plan.unitDevicePx;
        const slot = uniform(`${index}:composite`, [
          plan.footprint.x0, plan.footprint.y0, rectDevice.x, rectDevice.y,
          index, surfaces.length, dpr, plan.receded ? 1 : 0,
          plan.spanPx, plan.t, unit, levels.length,
          material.bodyLawLambda, material.bodyLawNormal, material.bodyLawHinge,
          material.bodyLawKnee,
          plan.interpolation === "single" ? 0 : plan.interpolation === "linear" ? 1 : 2,
          material.bodyLawEncodedAveraging, wide.q, wide.pad,
          ...lanes((k) => levels[k]!),
          ...lanes((k) => level(k).q),
          ...lanes((k) => level(k).pad),
        ]);
        pass.setBindGroup(0, device.createBindGroup({ layout: composite.getBindGroupLayout(0), entries: [
          { binding: 0, resource: { buffer: slot.buffer } },
          { binding: 1, resource: { buffer: shapes } },
          ...Array.from({ length: BODY_LAW_MAX_LEVELS }, (_, k) => ({
            binding: 2 + k, resource: k < levels.length ? level(k).view : floored,
          })),
          { binding: 9, resource: wide.view },
        ] }));
        pass.setScissorRect(x0 - rectDevice.x, y0 - rectDevice.y, x1 - x0, y1 - y0);
        pass.draw(3);
      }
      pass.end();

      // What this build did not use is released: a surface that left the group, a grid its
      // widths no longer need. Destruction waits for the work already submitted.
      for (const poolKey of entry.textures) if (!used.has(poolKey)) pool.release(poolKey);
      entry.textures.clear();
      for (const poolKey of used) entry.textures.add(poolKey);
      for (const [name, slot] of entry.uniforms) {
        if (!usedSlots.has(name)) { slot.buffer.destroy(); entry.uniforms.delete(name); }
      }
      for (const [name, slot] of entry.storages) {
        if (!usedSlots.has(name)) { slot.destroy(); entry.storages.delete(name); }
      }

      entry.key = key;
      entry.encoded = encoded;
      entry.a = a;
      entry.unsubmitted = true;
      entry.output = {
        view: aView, origin: [rectDevice.x, rectDevice.y], size: [rectDevice.width, rectDevice.height],
      };
      return entry.output;
    },

    afterSubmit() {
      for (const entry of entries.values()) entry.unsubmitted = false;
    },

    cancelQueued() {
      // A build that never reached the queue left A unwritten: the next frame builds again.
      for (const entry of entries.values()) {
        if (!entry.unsubmitted) continue;
        entry.unsubmitted = false;
        entry.key = undefined;
        entry.output = undefined;
      }
    },

    forget(resourceId) {
      const entry = entries.get(resourceId);
      if (entry !== undefined) destroyEntry(resourceId, entry);
    },

    destroy() {
      for (const [resourceId, entry] of [...entries]) destroyEntry(resourceId, entry);
    },
  };
}
