/**
 * **W42's body law, LT: the GPU stage** (G2 `implementation-design.md` §2.1–§2.6, revised in §11
 * and §12, rebuilt as compute in §17). It runs between the field pass and the optics pass for a
 * group whose folded `bodyLawStrength` is above 0 and whose source carries the pyramid's encoded
 * level 0, and it leaves one group texture, **A**: rgb the law's argument M in encoded sRGB, a the
 * wide term's encoded luma L(W). The optics pass reads A at the refracted position
 * (`wgsl/optics.ts` `body_law_body`).
 *
 * Per law surface, on its footprint R_fp (`bodyLawSurfacePlan`) at one texel per device pixel:
 *
 * 1. the capture S0 from the encoded level 0, through the group's fit;
 * 2. the floor, memo C's Gaussian at 0.4 capture texels, clamp mode: S, with S0 and the floor's
 *    horizontal half held in workgroup memory;
 * 3. every stored width — the narrow levels and W — as a separable pair: below 12 device px (6
 *    for an active narrow level, `BODY_LAW_REALISATION`) directly on S in the plan's edge mode,
 *    above it on S decimated by q = 2 (q = 4 from 48), `forward.py`'s `_blur_decimated`;
 * 4. A, which holds the captured backdrop wherever no surface's footprint owns the texel (R2).
 *
 * All of it is one compute pass per group, encoded where the group draws: the floor, the
 * decimation, every width's horizontal pass and every width's vertical pass, each one dispatch for
 * every law surface of the group from a job table (`wgsl/body-law.ts`), and then A. A width is
 * computed only where it is read: its vertical pass over the texels the composite reaches inside A's rect, its
 * horizontal pass over those columns and the rows the vertical kernel reaches (`bodyLawRegions`).
 * Each texel so computed is the texel the whole-footprint pass computed, because every kernel reads
 * the same clamped or zero-padded neighbourhood of the same source.
 *
 * Every tile is rgba32float in the form (value·weight, weight), packed per role into an atlas
 * (`bodyLawPackShelves`), and the Gaussian weights are the instrument's, computed here in f64.
 *
 * The stage is rebuilt only when what it reads moves — the source's build, the fit, the
 * viewport, the group's rect, the surfaces' boxes and corners, the device ratio or a law leaf —
 * on the silhouette tone's model (`silhouette-tone.ts`). A static page rebuilds nothing.
 */

import {
  BODY_LAW_REALISATION,
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
  bodyLawCompositeModule,
  bodyLawDecimateModule,
  bodyLawFloorModule,
} from "./wgsl";
import {
  BODY_LAW_DISPATCH_ROW,
  BODY_LAW_FLOOR_RADIUS_CAP,
  BODY_LAW_FLOOR_TILE,
  BODY_LAW_JOB_VEC4S,
  BODY_LAW_LANES,
  BODY_LAW_RADIUS_CAP,
  BODY_LAW_SEGMENT,
  BODY_LAW_SURFACE_VEC4S,
} from "./wgsl/body-law";

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

/** One grid a surface's widths are blurred on: the footprint at q = 1, else a decimated one. */
export interface BodyLawGrid {
  readonly q: 1 | 2 | 4;
  /** The shared padding in full-resolution texels (0 at q = 1). */
  readonly pad: number;
  readonly width: number;
  readonly height: number;
  /** The widths blurred on this grid. */
  readonly members: readonly BodyLawWidth[];
}

/** Which widths one surface stores, and on which grids. */
export interface BodyLawSurfaceSchedule {
  readonly plan: BodyLawSurfacePlan;
  readonly widths: readonly BodyLawWidth[];
  /** Per decimation factor present: the shared padding and the grid's extent. */
  readonly grids: readonly BodyLawGrid[];
}

/**
 * **The schedule for one surface** — which widths are stored, at which decimation and on which
 * grid. Pure, so a test reads it without a device.
 *
 * The widths of one q share one decimated grid, padded by the largest padding any of them
 * needs. In exact arithmetic that is each width's own `_blur_decimated`: the paddings are
 * multiples of q, so the blocks coincide, and a narrower width's kernel plus the bilinear return
 * never reaches the extra rows (its own padding already exceeds 4 σ_d + 2 texels of the grid).
 */
export function bodyLawSchedule(plan: BodyLawSurfacePlan): BodyLawSurfaceSchedule {
  const narrowFrom = plan.receded ? BODY_LAW_REALISATION.decimateFromDevicePx
    : BODY_LAW_REALISATION.decimateActiveNarrowFromDevicePx;
  const widths: BodyLawWidth[] = [
    ...plan.narrowSigmaDevicePx.map((sigma, role): BodyLawWidth => ({
      role, sigma, q: sigma < 1e-3 ? 0 : bodyLawDecimation(sigma, narrowFrom),
    })),
    { role: "wide", sigma: plan.wideSigmaDevicePx,
      q: plan.wideSigmaDevicePx < 1e-3 ? 0 : bodyLawDecimation(plan.wideSigmaDevicePx) },
  ];
  const fw = plan.footprint.x1 - plan.footprint.x0;
  const fh = plan.footprint.y1 - plan.footprint.y0;
  const grids: BodyLawGrid[] = [];
  for (const q of [1, 2, 4] as const) {
    const members = widths.filter((width) => width.q === q);
    if (members.length === 0) continue;
    const pad = q === 1 ? 0 : Math.max(...members.map((width) => bodyLawDecimationPad(width.sigma, q)));
    grids.push({
      q, pad,
      width: q === 1 ? fw : Math.ceil((fw + 2 * pad) / q),
      height: q === 1 ? fh : Math.ceil((fh + 2 * pad) / q),
      members,
    });
  }
  return { plan, widths, grids };
}

/** A half-open rectangle of texels, [x0, x1) × [y0, y1). */
export interface BodyLawRect {
  readonly x0: number;
  readonly y0: number;
  readonly x1: number;
  readonly y1: number;
}

/** Where one stored width is computed, in its own grid's texels. */
export interface BodyLawWidthRegion {
  readonly width: BodyLawWidth;
  readonly grid: BodyLawGrid;
  /** σ on its grid, and its kernel's radius there. */
  readonly sigma: number;
  readonly radius: number;
  /**
   * Both passes pad with zeros: the normalised mode at q = 1. A decimated grid is blurred with its
   * edge held (`forward.py`): the zeros of the normalised mode are already in its padding.
   */
  readonly zero: boolean;
  /** What the vertical pass writes: every texel the composite reads. */
  readonly written: BodyLawRect;
  /** What the horizontal pass writes: `written`'s columns, and every row the vertical kernel reads. */
  readonly horizontal: BodyLawRect;
}

/**
 * **Where each stored width is computed** for a composite over `composite` (footprint texels) —
 * the pixels of A's rect this surface's footprint covers. Pure, so a test holds it to the
 * whole-footprint graph without a device.
 *
 * At q = 1 the composite reads the pixel's own texel, so the vertical pass writes exactly
 * `composite`. A decimated width is read bilinearly at (P + i + 0.5)/q − 0.5, so it writes the
 * texels from the floor of the first pixel's coordinate to one past the last's, clamped to the
 * grid as the read clamps. The horizontal pass writes the same columns over every row the
 * vertical kernel reaches from those rows, clipped to the grid: a clamped tap lands on the grid's
 * edge row, which lies inside that range whenever the tap's own row lies outside the grid.
 * Neither pass is clipped along its own axis, so every tap reads what the whole-footprint pass
 * read, and each texel computed is that pass's texel.
 */
export function bodyLawRegions(
  schedule: BodyLawSurfaceSchedule,
  composite: BodyLawRect,
): BodyLawWidthRegion[] {
  const zeroMode = schedule.plan.edge === "normalised";
  const regions: BodyLawWidthRegion[] = [];
  for (const grid of schedule.grids) {
    const reach = (low: number, high: number, extent: number): [number, number] => {
      if (grid.q === 1) return [low, high];
      const base = (i: number) => Math.floor((i + grid.pad + 0.5) / grid.q - 0.5);
      const clampTo = (v: number) => Math.min(extent - 1, Math.max(0, v));
      return [clampTo(base(low)), clampTo(base(high - 1) + 1) + 1];
    };
    const [x0, x1] = reach(composite.x0, composite.x1, grid.width);
    const [y0, y1] = reach(composite.y0, composite.y1, grid.height);
    for (const width of grid.members) {
      const sigma = grid.q === 1 ? width.sigma : bodyLawDecimatedSigma(width.sigma, grid.q);
      const radius = Math.floor(TRUNCATE * sigma + 0.5);
      regions.push({
        width, grid, sigma, radius,
        zero: grid.q === 1 && zeroMode,
        written: { x0, y0, x1, y1 },
        horizontal: { x0, x1, y0: Math.max(0, y0 - radius), y1: Math.min(grid.height, y1 + radius) },
      });
    }
  }
  return regions;
}

/**
 * **Shelf packing for an atlas**: tiles in order of height, left to right, a new shelf when the
 * next would pass `limit`. `undefined` when a tile or the stack of shelves does not fit, which the
 * stage reports as a stand-down rather than draw a clipped tile.
 */
export function bodyLawPackShelves(
  sizes: readonly (readonly [number, number])[],
  limit: number,
): { readonly places: readonly (readonly [number, number])[]; readonly width: number;
  readonly height: number } | undefined {
  const order = sizes.map((_, i) => i).sort((a, b) => sizes[b]![1] - sizes[a]![1] || a - b);
  const places: [number, number][] = sizes.map(() => [0, 0]);
  let x = 0, y = 0, shelf = 0, width = 0;
  for (const i of order) {
    const [w, h] = sizes[i]!;
    if (w > limit) return undefined;
    if (x + w > limit) {
      y += shelf;
      x = 0;
      shelf = 0;
    }
    places[i] = [x, y];
    x += w;
    shelf = Math.max(shelf, h);
    width = Math.max(width, x);
  }
  if (y + shelf > limit) return undefined;
  return { places, width: Math.max(width, 1), height: Math.max(y + shelf, 1) };
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

/**
 * Every atlas and A is written by a compute dispatch and read as a texture. RENDER_ATTACHMENT is
 * not for drawing: it lets the implementation zero a new texture with a render pass's clear
 * before its first storage write rather than by a copy (§17's first-frame reading).
 */
const tileUsage = (): GPUTextureUsageFlags =>
  GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.TEXTURE_BINDING |
  GPUTextureUsage.RENDER_ATTACHMENT;

/** Atlases grow in steps of this many texels, so that a surface moving a pixel reallocates nothing. */
const ATLAS_STEP = 64;

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
  /** The group's own job tables, kernels and composite words, released with it. */
  readonly uniforms: Map<string, UniformSlot>;
  readonly storages: Map<string, StorageSlot>;
}

export interface BodyLawStage {
  /**
   * Encode the stage for one group into the frame's encoder, or reuse A. `undefined` where the
   * source has no encoded level 0, or where the group's tiles would pass the device's texture
   * extent or a kernel the line cache's reach (`BODY_LAW_RADIUS_CAP`): the group then draws
   * without the law and its readout says so.
   */
  draw(encoder: GPUCommandEncoder, args: BodyLawStageArgs): BodyLawStageOutput | undefined;
  setTimeline(timeline: PassTimeline | undefined): void;
  afterSubmit(): void;
  cancelQueued(): void;
  forget(resourceId: string): void;
  destroy(): void;
  /** Stage rebuilds since creation, for tests and the bench. */
  readonly rebuilds: number;
}

/** One surface as the stage computes it. */
interface PlannedSurface {
  readonly plan: BodyLawSurfacePlan;
  readonly schedule: BodyLawSurfaceSchedule;
  readonly fw: number;
  readonly fh: number;
  readonly regions: readonly BodyLawWidthRegion[];
}

/** One group's rebuild. */
interface Build {
  readonly args: BodyLawStageArgs;
  readonly encoded: GPUTexture;
  readonly shapes: Float32Array;
  /** Per member of the group, in its order; `undefined` where the member writes nothing A keeps. */
  readonly members: readonly (PlannedSurface | undefined)[];
  readonly a: GPUTexture;
}

type Packed = NonNullable<ReturnType<typeof bodyLawPackShelves>>;

/** Where every tile of a group's build sits: one shelf packing per atlas. */
interface Layout {
  readonly surfaces: readonly { readonly member: number; readonly planned: PlannedSurface }[];
  readonly grids: readonly { readonly surface: number; readonly grid: BodyLawGrid }[];
  readonly regions: readonly { readonly surface: number; readonly region: BodyLawWidthRegion }[];
  readonly floors: Packed;
  readonly decimated: Packed;
  readonly horizontals: Packed;
  readonly writtens: Packed;
}

function layoutOf(members: Build["members"], limit: number): Layout | undefined {
  const surfaces = members.flatMap((planned, member) =>
    planned === undefined ? [] : [{ member, planned }]);
  const grids = surfaces.flatMap(({ planned }, surface) =>
    planned.schedule.grids.filter((grid) => grid.q > 1).map((grid) => ({ surface, grid })));
  const regions = surfaces.flatMap(({ planned }, surface) =>
    planned.regions.map((region) => ({ surface, region })));
  const size = (r: BodyLawRect) => [r.x1 - r.x0, r.y1 - r.y0] as const;
  const floors = bodyLawPackShelves(surfaces.map(({ planned }) => [planned.fw, planned.fh]), limit);
  const decimated = bodyLawPackShelves(grids.map(({ grid }) => [grid.width, grid.height]), limit);
  const horizontals = bodyLawPackShelves(regions.map(({ region }) => size(region.horizontal)), limit);
  const writtens = bodyLawPackShelves(regions.map(({ region }) => size(region.written)), limit);
  if (floors === undefined || decimated === undefined || horizontals === undefined ||
      writtens === undefined) return undefined;
  return { surfaces, grids, regions, floors, decimated, horizontals, writtens };
}

/** One blur job (`WGSL_BODY_LAW_BLUR`'s table). */
interface BlurJob {
  readonly axis: 0 | 1;
  readonly zero: boolean;
  /** 0 atlas A, 1 atlas B. */
  readonly source: 0 | 1;
  readonly lines: readonly [number, number];
  readonly positions: readonly [number, number];
  readonly extent: number;
  readonly sigma: number;
  readonly src: readonly [number, number];
  readonly dst: readonly [number, number];
}

export function createBodyLawStage(context: GpuContext): BodyLawStage {
  const { device, cache, pool } = context;
  const entries = new Map<string, Entry>();
  let timeline: PassTimeline | undefined;
  let rebuilds = 0;
  const limit = device.limits.maxTextureDimension2D;
  /**
   * The atlases so far. Every group's pass writes the same atlases in encoder order and leaves its
   * result in its own A, so one set serves them all; they grow and never shrink while any group
   * runs the law. A growth takes a new texture under a new key, and the one it replaces is
   * released only once the frame is submitted or dropped: an earlier group's pass in the same
   * encoder still reads it.
   */
  const atlases = new Map<string, { key: string; width: number; height: number }>();
  let atlasGeneration = 0;
  let retired: string[] = [];
  const releaseRetired = (): void => {
    for (const key of retired) pool.release(key);
    retired = [];
  };

  const computePipeline = (key: string, module: () => string, entryPoint: string) =>
    cache.computePipeline(`body-law:${key}`, () => ({
      label: `vitrea:pipeline:body-law:${key}`,
      layout: "auto",
      compute: { module: cache.module(`module:body-law:${key}`, module), entryPoint },
    }));
  const aKey = (resourceId: string) => `body-law:${resourceId}:A`;

  const destroyEntry = (resourceId: string, entry: Entry): void => {
    pool.release(aKey(resourceId));
    for (const slot of entry.uniforms.values()) slot.buffer.destroy();
    for (const slot of entry.storages.values()) slot.destroy();
    entries.delete(resourceId);
    if (entries.size > 0) return;
    for (const { key } of atlases.values()) retired.push(key);
    atlases.clear();
    releaseRetired();
  };

  const plan = (args: BodyLawStageArgs): (PlannedSurface | undefined)[] => {
    const { rectDevice, material } = args;
    const extent = bodyLawSourceExtent(args.viewportDevice, args.fit);
    return args.surfaces.map((surface) => {
      const surfacePlan = bodyLawSurfacePlan(
        { centre: surface.centre, size: surface.shape.channels.size }, args.devicePixelRatio,
        material, extent,
      );
      const fp = surfacePlan.footprint;
      const fw = fp.x1 - fp.x0;
      const fh = fp.y1 - fp.y0;
      const composite = {
        x0: Math.max(fp.x0, rectDevice.x) - fp.x0,
        y0: Math.max(fp.y0, rectDevice.y) - fp.y0,
        x1: Math.min(fp.x1, rectDevice.x + rectDevice.width) - fp.x0,
        y1: Math.min(fp.y1, rectDevice.y + rectDevice.height) - fp.y0,
      };
      // A surface whose footprint covers none of A's rect writes nothing A keeps.
      if (fw <= 0 || fh <= 0 || composite.x1 <= composite.x0 || composite.y1 <= composite.y0) {
        return undefined;
      }
      const schedule = bodyLawSchedule(surfacePlan);
      return { plan: surfacePlan, schedule, fw, fh, regions: bodyLawRegions(schedule, composite) };
    });
  };

  /** One group's compute pass: the floor, the decimation, the widths' two passes, and A. */
  const encodeBuild = (encoder: GPUCommandEncoder, resourceId: string, entry: Entry,
    build: Build, layout: Layout): void => {
    const { args } = build;
    const { material, rectDevice } = args;

    const atlas = (name: string, packed: Packed): GPUTextureView => {
      const step = (v: number) => Math.min(limit, Math.ceil(v / ATLAS_STEP) * ATLAS_STEP);
      let current = atlases.get(name);
      if (current === undefined || current.width < packed.width || current.height < packed.height) {
        if (current !== undefined) retired.push(current.key);
        atlasGeneration += 1;
        current = {
          key: `body-law:atlas:${name}:${atlasGeneration}`,
          width: Math.max(current?.width ?? 1, step(packed.width)),
          height: Math.max(current?.height ?? 1, step(packed.height)),
        };
        atlases.set(name, current);
      }
      return pool.acquire(current.key, {
        width: current.width, height: current.height, format: BODY_LAW_TILE_FORMAT,
        usage: tileUsage(), label: `vitrea:body-law:atlas:${name}`,
      }).createView();
    };
    const flooredAtlas = atlas("floored", layout.floors);
    const gridAtlas = atlas("grids", layout.decimated);
    const levelAtlas = atlas("levels", layout.writtens);
    const scratchAtlas = atlas("scratch", layout.horizontals);

    // The group's own slots: a slot is written before the frame is submitted, so two groups
    // sharing one would leave the first group's dispatch reading the second group's words.
    const usedSlots = new Set<string>();
    const uniform = (name: string, data: readonly number[]): GPUBuffer => {
      usedSlots.add(name);
      let slot = entry.uniforms.get(name);
      if (slot === undefined || slot.data.length < data.length) {
        slot?.buffer.destroy();
        slot = createUniformSlot(device, data.length,
          `vitrea:uniform:body-law:${resourceId}:${name}`);
        entry.uniforms.set(name, slot);
      }
      slot.data.fill(0);
      slot.data.set(data);
      slot.write();
      return slot.buffer;
    };
    const storage = (name: string, data: Float32Array): GPUBuffer => {
      usedSlots.add(name);
      let slot = entry.storages.get(name);
      if (slot === undefined) {
        slot = createStorageSlot(device, data.byteLength,
          `vitrea:storage:body-law:${resourceId}:${name}`);
        entry.storages.set(name, slot);
      }
      const buffer = slot.ensure(data.byteLength);
      slot.write(data, data.length);
      return buffer;
    };

    // The half kernels, centre first, one copy per distinct width.
    const weightData: number[] = [];
    const weightStart = new Map<number, number>();
    const kernel = (sigma: number): number => {
      let start = weightStart.get(sigma);
      if (start === undefined) {
        start = weightData.length;
        weightStart.set(sigma, start);
        const full = bodyLawGaussianWeights(sigma);
        const r = full.length >> 1;
        for (let k = 0; k <= r; k++) weightData.push(full[r + k]!);
      }
      return start;
    };
    const blurTable = (jobs: readonly BlurJob[]) => {
      const data = new Int32Array(Math.max(jobs.length, 1) * BODY_LAW_JOB_VEC4S * 4);
      let total = 0;
      jobs.forEach((job, j) => {
        const segments = Math.ceil((job.positions[1] - job.positions[0]) / BODY_LAW_SEGMENT);
        data.set([
          total, segments, job.axis, (job.zero ? 1 : 0) | (job.source << 1),
          job.lines[0], job.lines[1], job.positions[0], job.positions[1],
          job.extent, bodyLawGaussianWeights(job.sigma).length >> 1, kernel(job.sigma), 0,
          job.src[0], job.src[1], job.dst[0], job.dst[1],
        ], j * BODY_LAW_JOB_VEC4S * 4);
        total += segments * (job.lines[1] - job.lines[0]);
      });
      return { data, count: jobs.length, total };
    };
    const minus = (p: readonly [number, number], x: number, y: number) =>
      [p[0] - x, p[1] - y] as const;

    // The job tables, before anything is written, so the weights are written once.
    const floorJobs = new Int32Array(Math.max(layout.surfaces.length, 1) * BODY_LAW_JOB_VEC4S * 4);
    let floorTotal = 0;
    layout.surfaces.forEach(({ planned }, s) => {
      const sigma = planned.plan.floorSigmaDevicePx;
      const tilesX = Math.ceil(planned.fw / BODY_LAW_FLOOR_TILE[0]);
      floorJobs.set([
        floorTotal, tilesX, bodyLawGaussianWeights(sigma).length >> 1, kernel(sigma),
        planned.fw, planned.fh, ...layout.floors.places[s]!,
        planned.plan.footprint.x0, planned.plan.footprint.y0, 0, 0,
      ], s * BODY_LAW_JOB_VEC4S * 4);
      floorTotal += tilesX * Math.ceil(planned.fh / BODY_LAW_FLOOR_TILE[1]);
    });
    const gridPlace = new Map<string, readonly [number, number]>();
    const decimations = new Int32Array(Math.max(layout.grids.length, 1) * BODY_LAW_JOB_VEC4S * 4);
    let decimationTotal = 0;
    layout.grids.forEach(({ surface, grid }, g) => {
      const { planned } = layout.surfaces[surface]!;
      gridPlace.set(`${surface}:${grid.q}`, layout.decimated.places[g]!);
      const texels = grid.width * grid.height;
      decimations.set([
        decimationTotal, texels, grid.q, grid.pad,
        grid.width, grid.height, planned.fw, planned.fh,
        ...layout.floors.places[surface]!, ...layout.decimated.places[g]!,
        planned.plan.edge === "normalised" ? 1 : 0, 0, 0, 0,
      ], g * BODY_LAW_JOB_VEC4S * 4);
      decimationTotal += Math.ceil(texels / BODY_LAW_LANES);
    });
    const horizontal: BlurJob[] = [];
    const vertical: BlurJob[] = [];
    const writtenOffset = new Map<string, readonly [number, number]>();
    layout.regions.forEach(({ surface, region }, r) => {
      const { written: w, horizontal: h, grid } = region;
      const source = grid.q === 1 ? layout.floors.places[surface]! :
        gridPlace.get(`${surface}:${grid.q}`)!;
      const hOffset = minus(layout.horizontals.places[r]!, w.x0, h.y0);
      const wOffset = minus(layout.writtens.places[r]!, w.x0, w.y0);
      writtenOffset.set(`${surface}:${String(region.width.role)}`, wOffset);
      horizontal.push({ axis: 0, zero: region.zero, source: grid.q === 1 ? 0 : 1,
        lines: [h.y0, h.y1], positions: [w.x0, w.x1], extent: grid.width, sigma: region.sigma,
        src: source, dst: hOffset });
      vertical.push({ axis: 1, zero: region.zero, source: 0,
        lines: [w.x0, w.x1], positions: [w.y0, w.y1], extent: grid.height, sigma: region.sigma,
        src: hOffset, dst: wOffset });
    });
    for (const job of [...horizontal, ...vertical]) kernel(job.sigma);
    const weights = storage("kernels", new Float32Array(weightData.length === 0 ? [0] : weightData));

    const slot = timeline?.computeSlot(PASS_LABEL.bodyLaw);
    const pass = encoder.beginComputePass({
      label: "vitrea:pass:body-law",
      ...(slot === undefined ? {} : { timestampWrites: slot }),
    });
    const dispatch = (pipe: GPUComputePipeline, bindings: GPUBindGroupEntry[], x: number,
      y = 1): void => {
      pass.setPipeline(pipe);
      pass.setBindGroup(0, device.createBindGroup({ layout: pipe.getBindGroupLayout(0),
        entries: bindings }));
      pass.dispatchWorkgroups(x, y);
    };
    const flat = (total: number) =>
      [Math.min(total, BODY_LAW_DISPATCH_ROW), Math.ceil(total / BODY_LAW_DISPATCH_ROW)] as const;
    const encodedView = build.encoded.createView();

    if (layout.surfaces.length > 0) {
      dispatch(computePipeline("floor", bodyLawFloorModule, "cs_floor"), [
        { binding: 0, resource: { buffer: uniform("floor", [
          args.viewportDevice[0], args.viewportDevice[1], layout.surfaces.length, floorTotal,
          ...args.fit, material.bodyLawEncodedAveraging === 1 ? 0 : 1, 0, 0, 0,
        ]) } },
        { binding: 3, resource: encodedView },
        { binding: 4, resource: flooredAtlas },
        { binding: 5, resource: { buffer: storage("floor:jobs", new Float32Array(floorJobs.buffer)) } },
        { binding: 6, resource: { buffer: weights } },
      ], ...flat(floorTotal));
    }
    if (layout.grids.length > 0) {
      dispatch(computePipeline("decimate", bodyLawDecimateModule, "cs_decimate"), [
        { binding: 0, resource: { buffer: uniform("decimate", [layout.grids.length, decimationTotal]) } },
        { binding: 1, resource: flooredAtlas },
        { binding: 4, resource: gridAtlas },
        { binding: 5, resource: { buffer: storage("decimate:jobs",
          new Float32Array(decimations.buffer)) } },
      ], ...flat(decimationTotal));
    }
    const blurPipeline = computePipeline("blur", bodyLawBlurModule, "cs_blur");
    const blur = (name: string, jobs: readonly BlurJob[], srcA: GPUTextureView,
      srcB: GPUTextureView, dst: GPUTextureView): void => {
      if (jobs.length === 0) return;
      const t = blurTable(jobs);
      dispatch(blurPipeline, [
        { binding: 0, resource: { buffer: uniform(name, [t.count, t.total]) } },
        { binding: 1, resource: srcA },
        { binding: 2, resource: srcB },
        { binding: 4, resource: dst },
        { binding: 5, resource: { buffer: storage(`${name}:jobs`, new Float32Array(t.data.buffer)) } },
        { binding: 6, resource: { buffer: weights } },
      ], ...flat(t.total));
    };
    blur("widths:h", horizontal, flooredAtlas, gridAtlas, scratchAtlas);
    blur("widths:v", vertical, scratchAtlas, gridAtlas, levelAtlas);

    // A: the surface table names where each member's widths sit.
    const surfaceTable = new Float32Array(build.members.length * BODY_LAW_SURFACE_VEC4S * 4);
    layout.surfaces.forEach(({ member, planned }, s) => {
      const { plan: memberPlan, schedule } = planned;
      const levels = memberPlan.narrowSigmaDevicePx;
      const floorPlace = layout.floors.places[s]!;
      const level = (width: BodyLawWidth): number[] => {
        if (width.q === 0) return [width.sigma, 1, 0, 1, ...floorPlace, planned.fw, planned.fh];
        const grid = schedule.grids.find((g) => g.q === width.q)!;
        return [width.sigma, grid.q, grid.pad, 0,
          ...writtenOffset.get(`${s}:${String(width.role)}`)!, grid.width, grid.height];
      };
      const rows = [
        memberPlan.footprint.x0, memberPlan.footprint.y0, planned.fw, planned.fh,
        memberPlan.spanPx, memberPlan.t, material.bodyLawK[0] * 5 * memberPlan.unitDevicePx,
        levels.length,
        memberPlan.interpolation === "single" ? 0 : memberPlan.interpolation === "linear" ? 1 : 2,
        memberPlan.receded ? 1 : 0, 0, 0,
      ];
      for (let k = 0; k < BODY_LAW_MAX_LEVELS; k++) {
        rows.push(...(k < levels.length ? level(schedule.widths[k]!) : [0, 0, 0, 0, 0, 0, 1, 1]));
      }
      rows.push(...level(schedule.widths[schedule.widths.length - 1]!));
      surfaceTable.set(rows, member * BODY_LAW_SURFACE_VEC4S * 4);
    });
    dispatch(computePipeline("composite", bodyLawCompositeModule, "cs_composite"), [
      { binding: 0, resource: { buffer: uniform("composite", [
        args.viewportDevice[0], args.viewportDevice[1], rectDevice.x, rectDevice.y, ...args.fit,
        args.surfaces.length, args.devicePixelRatio,
        material.bodyLawEncodedAveraging === 1 ? 1 : 0, 0,
        material.bodyLawLambda, material.bodyLawNormal, material.bodyLawHinge, material.bodyLawKnee,
      ]) } },
      { binding: 1, resource: { buffer: storage("shapes", build.shapes) } },
      { binding: 2, resource: { buffer: storage("surfaces", surfaceTable) } },
      { binding: 3, resource: encodedView },
      { binding: 4, resource: flooredAtlas },
      { binding: 5, resource: levelAtlas },
      { binding: 6, resource: build.a.createView() },
    ], Math.ceil(rectDevice.width / 8), Math.ceil(rectDevice.height / 8));
    pass.end();

    // What this build did not use is released; destruction waits for the work already submitted.
    for (const [name, s] of entry.uniforms) {
      if (!usedSlots.has(name)) { s.buffer.destroy(); entry.uniforms.delete(name); }
    }
    for (const [name, s] of entry.storages) {
      if (!usedSlots.has(name)) { s.destroy(); entry.storages.delete(name); }
    }
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
      const stale = entries.get(args.resourceId);
      if (encoded === undefined || surfaces.length === 0) {
        if (stale !== undefined) destroyEntry(args.resourceId, stale);
        return undefined;
      }
      const shapes = packToneShapes(surfaces, args.devicePixelRatio);
      const key = JSON.stringify([
        pyramid.sourceId, pyramid.builtEpoch, pyramid.sizeEpoch, pyramid.plan.width,
        pyramid.plan.height, args.viewportDevice, args.fit, rectDevice, args.devicePixelRatio,
        [...shapes], surfaces.map((surface) => [surface.centre, surface.shape.channels.size]),
        lawKey(material),
      ]);
      if (stale !== undefined && stale.key === key && stale.encoded === encoded &&
          stale.a !== undefined && pool.peek(aKey(args.resourceId)) === stale.a &&
          stale.output !== undefined) {
        return stale.output;
      }

      const members = plan(args);
      const layout = layoutOf(members, limit);
      const fits = layout !== undefined && members.every((member) => member === undefined ||
        (bodyLawGaussianWeights(member.plan.floorSigmaDevicePx).length >> 1) <=
          BODY_LAW_FLOOR_RADIUS_CAP &&
        member.regions.every((region) => region.radius <= BODY_LAW_RADIUS_CAP));
      if (!fits) {
        // Honest rather than clipped: the group draws without the law, and says so.
        if (stale !== undefined) destroyEntry(args.resourceId, stale);
        return undefined;
      }

      const entry: Entry = stale ?? {
        key: undefined, encoded: undefined, a: undefined, output: undefined, unsubmitted: false,
        uniforms: new Map(), storages: new Map(),
      };
      entries.set(args.resourceId, entry);
      rebuilds += 1;
      const a = pool.acquire(aKey(args.resourceId), {
        width: rectDevice.width, height: rectDevice.height, format: BODY_LAW_TILE_FORMAT,
        usage: tileUsage(), label: `vitrea:body-law:${args.resourceId}:A`,
      });
      encodeBuild(encoder, args.resourceId, entry, { args, encoded, shapes, members, a }, layout);

      entry.key = key;
      entry.encoded = encoded;
      entry.a = a;
      entry.unsubmitted = true;
      entry.output = {
        view: a.createView(), origin: [rectDevice.x, rectDevice.y],
        size: [rectDevice.width, rectDevice.height],
      };
      return entry.output;
    },

    afterSubmit() {
      for (const entry of entries.values()) entry.unsubmitted = false;
      releaseRetired();
    },

    cancelQueued() {
      releaseRetired();
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
