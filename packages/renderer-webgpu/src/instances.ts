/**
 * Instance packing: X8's channel vector plus the six derived floats, into the
 * storage buffer the field pass walks.
 *
 * ## X8 rider 2, made unavoidable
 *
 * The rider (tightened at C3's landing, Decision Log #22b) says a renderer MUST
 * draw a concentric child as a **level set of the parent's field**, because
 * instantiating the child as its own resolved shape adds an offset-approximation
 * error that grows with inset — 0.326 px at 8 px, past the field's own declared
 * bound, and dominant past about 4 px.
 *
 * The way that is honoured here is not a check: a concentric surface is packed
 * with its **parent's** `half/re/k` and its own `inset`, and the shader's only
 * expression is `field(p; those params) + inset`. There is no instantiated-shape
 * path to take, so no future caller can take it by accident. `resolveConcentric`
 * — geometry's other path — is still the right answer for bounds and hit-testing,
 * and this module uses it for exactly that and nothing else.
 *
 * ## Press compression
 *
 * §Motion: "The `pressCompression` channel runs 0…1; this is what 1 means, so the
 * renderer needs no constant of its own." So the scale comes from
 * `DEFAULT_MOTION_PROFILE.pressCompressionScale` rather than from a literal here,
 * and it is applied to `size` before the corner is derived — which matters,
 * because the corner budget is a function of size, so a compressed surface must
 * re-derive its corner rather than scale a corner derived at rest.
 */

import {
  DEFAULT_GROUP_UNION,
  type FieldParams,
  fieldParams,
  governorFieldParams,
  type GroupUnionParams,
  resolveConcentric,
  resolveFromChannels,
  type ResolvedShape,
  type ShapeChannels,
} from "@vitrea/geometry";
import { DEFAULT_MOTION_PROFILE } from "@vitrea/motion";

import { rendererError } from "./errors";
import type { FieldFamily } from "./governor";
import { DEFAULT_MATERIAL_PROFILE, lensDepthPx, type MaterialProfile } from "./material";
import { IDLE_CHANNELS, type GroupRenderInput, type Rect, type SurfaceChannels, type SurfaceInput } from "./render-model";

/** 16 floats, 64 bytes, matching `WGSL_INSTANCE_STRUCT`. */
export const INSTANCE_FLOATS = 16;
export const INSTANCE_BYTES = INSTANCE_FLOATS * 4;

export interface ResolvedSurface {
  readonly nodeId: string;
  /** The surface's own resolved shape — bounds, hit-testing, and the rim's scale. */
  readonly shape: ResolvedShape;
  /** The field parameters actually packed: the parent's, for a concentric child. */
  readonly field: FieldParams;
  /** Level-set offset. 0 for an ordinary surface. */
  readonly inset: number;
  readonly centre: readonly [number, number];
  readonly channels: SurfaceChannels;
  /** Shorter extent in CSS px — what the lens's size gain is a function of. */
  readonly spanPx: number;
  readonly lensDepthPx: number;
}

const channelsOf = (input: SurfaceInput): SurfaceChannels => ({
  ...IDLE_CHANNELS,
  ...input.channels,
});

/** `size` after press compression, which the corner is then derived from. */
function compressedChannels(shape: ShapeChannels, press: number): ShapeChannels {
  if (press <= 0) return shape;
  const scale = 1 - Math.min(1, Math.max(0, press)) * DEFAULT_MOTION_PROFILE.pressCompressionScale;
  return { ...shape, size: [shape.size[0] * scale, shape.size[1] * scale] };
}

/**
 * Resolve one group's surfaces, ordered so that a concentric child always follows
 * its parent. The order matters only for the resolution pass, not for the union —
 * `smoothUnion2` is commutative, which `union.ts` asserts rather than assumes.
 */
export function resolveSurfaces(
  group: GroupRenderInput,
  family: FieldFamily,
  profile: MaterialProfile = DEFAULT_MATERIAL_PROFILE,
): readonly ResolvedSurface[] {
  const byId = new Map<string, SurfaceInput>();
  for (const surface of group.surfaces) {
    if (byId.has(surface.nodeId)) {
      throw rendererError(
        "source-identity",
        `Group "${group.groupId}" lists surface "${surface.nodeId}" twice.`,
        surface.nodeId,
      );
    }
    byId.set(surface.nodeId, surface);
  }

  const resolvedShapes = new Map<string, ResolvedShape>();
  const resolving = new Set<string>();
  const resolveShapeOf = (surface: SurfaceInput): ResolvedShape => {
    const cached = resolvedShapes.get(surface.nodeId);
    if (cached !== undefined) return cached;
    if (resolving.has(surface.nodeId)) {
      throw rendererError(
        "pass-input",
        `Concentric surfaces in group "${group.groupId}" form a cycle through "${surface.nodeId}". A level set needs a parent field that resolves without it.`,
        surface.nodeId,
      );
    }
    resolving.add(surface.nodeId);

    const channels = channelsOf(surface);
    const reference = surface.reference ?? "apple-continuous";

    if (surface.concentricOf === undefined) {
      const shape = resolveFromChannels(
        compressedChannels(surface.shape, channels.press),
        reference,
        surface.family,
        { devMode: false },
      );
      resolvedShapes.set(surface.nodeId, shape);
      resolving.delete(surface.nodeId);
      return shape;
    }

    const parentInput = byId.get(surface.concentricOf.nodeId);
    if (parentInput === undefined) {
      throw rendererError(
        "pass-input",
        `Surface "${surface.nodeId}" is concentric to "${surface.concentricOf.nodeId}", which is not a member of group "${group.groupId}". X8 rider 2 renders a concentric child as a level set of its parent's field, so the parent has to be in the same field pass.`,
        surface.nodeId,
      );
    }
    // The child's OWN resolved shape, for bounds and hit-testing only. What gets
    // packed is the parent's field plus the inset — see the module note.
    const shape = resolveConcentric(resolveShapeOf(parentInput), {
      inset: surface.concentricOf.inset,
    }).shape;
    resolvedShapes.set(surface.nodeId, shape);
    resolving.delete(surface.nodeId);
    return shape;
  };

  const paramsFor = (shape: ResolvedShape): FieldParams =>
    family === "rsup" ? governorFieldParams(shape) : fieldParams(shape);

  // Reference shapes are resolved (a child needs its parent's field) and then
  // dropped: they contribute no instance, no bounds, and no coverage.
  return group.surfaces
    .filter((surface) => surface.fieldReferenceOnly !== true)
    .map((surface): ResolvedSurface => {
    const channels = channelsOf(surface);
    const shape = resolveShapeOf(surface);

    const fieldSource =
      surface.concentricOf === undefined
        ? shape
        : resolveShapeOf(byId.get(surface.concentricOf.nodeId) as SurfaceInput);
    const inset = surface.concentricOf?.inset ?? 0;

    const spanPx = Math.min(shape.channels.size[0], shape.channels.size[1]);
    return {
      nodeId: surface.nodeId,
      shape,
      field: paramsFor(fieldSource),
      inset,
      centre: [fieldSource.channels.center[0], fieldSource.channels.center[1]],
      channels,
      spanPx,
      lensDepthPx: lensDepthPx(shape.channels.thickness, spanPx, profile),
    };
  });
}

/**
 * The group's field-pass rect, in viewport CSS px.
 *
 * Padded by whatever can reach beyond a surface's own contour: the rim band, the
 * union's bulge cap, and one coverage pixel. Not padded by the lens depth — the
 * lens displaces where the backdrop is *sampled from*, not where the material is
 * *drawn*, so paying for it here would widen every group's field pass for nothing.
 */
export function groupFieldRect(
  surfaces: readonly ResolvedSurface[],
  union: GroupUnionParams = DEFAULT_GROUP_UNION,
  rimWidthPx = 2,
): Rect {
  if (surfaces.length === 0) return { x: 0, y: 0, width: 0, height: 0 };

  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  for (const surface of surfaces) {
    const [cx, cy] = surface.shape.channels.center;
    const [w, h] = surface.shape.channels.size;
    minX = Math.min(minX, cx - w / 2);
    minY = Math.min(minY, cy - h / 2);
    maxX = Math.max(maxX, cx + w / 2);
    maxY = Math.max(maxY, cy + h / 2);
  }

  const pad = rimWidthPx + union.maxBulge + 1;
  return {
    x: minX - pad,
    y: minY - pad,
    width: maxX - minX + 2 * pad,
    height: maxY - minY + 2 * pad,
  };
}

/** The same rect snapped outward to whole device pixels. */
export function snapRectToDevicePixels(rect: Rect, devicePixelRatio: number): Rect {
  const x = Math.floor(rect.x * devicePixelRatio) / devicePixelRatio;
  const y = Math.floor(rect.y * devicePixelRatio) / devicePixelRatio;
  const right = Math.ceil((rect.x + rect.width) * devicePixelRatio) / devicePixelRatio;
  const bottom = Math.ceil((rect.y + rect.height) * devicePixelRatio) / devicePixelRatio;
  return { x, y, width: Math.max(right - x, 0), height: Math.max(bottom - y, 0) };
}

/**
 * Pack resolved surfaces into the storage buffer, with centres made relative to
 * the group's rect so the shader's coordinates stay small however far down a long
 * page the group sits — f32 loses resolution at large magnitudes, and a field
 * evaluated at y = 40000 would quantise its own corner.
 */
export function packInstances(
  surfaces: readonly ResolvedSurface[],
  origin: readonly [number, number],
  into?: Float32Array,
): { readonly data: Float32Array; readonly count: number } {
  const needed = Math.max(surfaces.length, 1) * INSTANCE_FLOATS;
  const data =
    into !== undefined && into.length >= needed ? into : new Float32Array(needed);

  for (let i = 0; i < surfaces.length; i += 1) {
    const s = surfaces[i] as ResolvedSurface;
    const o = i * INSTANCE_FLOATS;
    data[o + 0] = s.centre[0] - origin[0];
    data[o + 1] = s.centre[1] - origin[1];
    data[o + 2] = s.field.halfW;
    data[o + 3] = s.field.halfH;
    data[o + 4] = s.field.reach;
    data[o + 5] = s.field.k[0];
    data[o + 6] = s.field.k[1];
    data[o + 7] = s.field.k[2];
    data[o + 8] = s.field.k[3];
    data[o + 9] = s.field.k[4];
    data[o + 10] = s.inset;
    data[o + 11] = s.shape.channels.thickness;
    data[o + 12] = s.channels.press;
    data[o + 13] = s.channels.glow;
    // The shader's `lensDepth` slot: the size-parameterised depth from
    // `material.ts`, already scaled by the `lensStrength` motion channel, so the
    // fragment stage multiplies nothing it could get wrong.
    data[o + 14] = s.lensDepthPx * Math.min(1, Math.max(0, s.channels.lensStrength));
    data[o + 15] = 0;
  }

  return { data, count: surfaces.length };
}
