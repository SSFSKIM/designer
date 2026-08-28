/**
 * One backdrop proxy per sampling group, constructed the way S1 measured it.
 *
 * Three properties are normative, not stylistic:
 *
 * 1. **Box padded, mask exact.** [Filter Effects 2
 *    §3](https://drafts.csswg.org/filter-effects-2/#BackdropRoot) builds the
 *    Backdrop Root Image and clips it "to this border quad", and §2.1 applies
 *    `blur()` with `edgeMode="mirror"` at "the clipped, transformed border box of
 *    the element". So a shape-sized proxy blurs only the pixels inside the shape
 *    and mirrors at its own boundary — it *starves its own blur*. Inflating the
 *    box is how the DOM tier recovers the unclamped sampling the GPU tier gets
 *    for free. Masking to box+padding instead of to the shapes leaves a
 *    full-strength blurred rectangle standing proud of the glass: S1 measured
 *    that halo at GAP mean 102.92/255.
 * 2. **`samplingPadding ≥ 3σ`**, byte-exact at three radii spanning 5×.
 *    Enforced here because only this package knows σ (see `optics.ts`).
 * 3. **Bounded area.** Headless Chromium silently drops `backdrop-filter` above
 *    roughly 1.75–3.0 Mpx of device-pixel proxy area while retail Chrome never
 *    does, so a page cannot tell which rasteriser it is on. Silence is the worst
 *    failure mode, so the area is capped rather than probed.
 *
 * Everything here is pure arithmetic over measured rects: no DOM, no reads. The
 * element that carries the result is `backdrop-proxy.ts`'s job.
 */

import { inflateRect, unionRect, type CornerRadii, type Rect } from "@vitreajs/vitrea";

import { requiredSamplingPadding } from "./optics";

/** A group member as this module needs it: a measured rect and its corner radii. */
export interface ProxyMember {
  readonly nodeId: string;
  readonly bounds: Rect;
  readonly radii: CornerRadii;
}

export type ProxyFindingCode =
  | "sampling-padding-below-3-sigma"
  | "merge-distance-below-effective-padding"
  | "proxy-area-over-cap";

export interface ProxyFinding {
  readonly code: ProxyFindingCode;
  readonly severity: "warning" | "error";
  readonly message: string;
}

export interface ProxyGeometryInput {
  readonly members: readonly ProxyMember[];
  /** The group's authored (or core-defaulted) padding, in CSS px. */
  readonly samplingPadding: number;
  /** The group's merge distance, for the DOM consequence core cannot check. */
  readonly mergeDistance: number;
  /** σ of the group's blur, in CSS px. */
  readonly blurRadius: number;
  readonly devicePixelRatio: number;
  /** From the engine conformance table. `Infinity` where the engine is unbounded. */
  readonly maxProxyAreaDevicePx: number;
}

export interface ProxyGeometry {
  /** The proxy element's border box, in viewport CSS px. */
  readonly box: Rect;
  /** `clip-path` value: the exact member-shape union, in proxy-local px. */
  readonly clipPath: string;
  /** The mask's sub-rects in proxy-local px — the same geometry the path encodes. */
  readonly maskBounds: readonly Rect[];
  /** What the padding actually ended up being, after the 3σ floor and the area cap. */
  readonly effectivePadding: number;
  readonly findings: readonly ProxyFinding[];
}

/** What core resolved, plus what the author actually wrote. */
export interface DeclaredSamplingGeometry {
  /** `undefined` where the author never set one and core defaulted it. */
  readonly samplingPadding: number | undefined;
  readonly mergeDistance: number | undefined;
  /** σ of the group's blur after accessibility policy, in CSS px. */
  readonly blurRadius: number;
}

export interface SamplingGeometry {
  readonly samplingPadding: number;
  readonly mergeDistance: number;
}

/**
 * The group's sampling geometry, with the **default** derived from the blur the
 * material is actually drawing with.
 *
 * core defaults `samplingPadding` to the constant 24, and 24 was never arbitrary:
 * it is 3σ at the regular material's nominal σ of 8, which is exactly the floor
 * enforced below. The two agreed because one was written from the other — and
 * they stop agreeing the moment an accessibility preference moves σ.
 * `reducedTransparency` multiplies frost by 1.75, so σ becomes 14, the floor
 * becomes 42, and every group in the page that never declared a padding is
 * suddenly below a floor it was written to sit exactly on. A 0.1.1 consumer
 * flipped one prop and got a burst of warnings about geometry they had never
 * authored — the library's own default tripping the library's own rule under
 * the library's own accessibility mode.
 *
 * So the default follows σ instead of a constant. Two properties make this a
 * repair rather than a re-tune:
 *
 * - **It is byte-identical at the nominal state.** 3 × 8 = 24 is the constant it
 *   replaces, not a number near it, so every committed box and every golden
 *   stands unchanged.
 * - **An authored value is untouched, warning included.** A padding the author
 *   wrote is a statement about their geometry, and one that cannot cover the
 *   blur is still worth saying so. Deriving over the top of it would be the
 *   runtime overruling an author, which is a worse defect than the one this
 *   fixes. `mergeDistance` follows core's own rule — it defaults to the resolved
 *   padding — with the derived padding substituted.
 *
 * What this deliberately does **not** do is suppress anything. The floor below
 * still enforces, still warns when an authored value is under it, and the
 * cross-group overlap check is untouched: a page whose groups sit too close for
 * an enlarged blur is a real finding, and going quiet about it under exactly the
 * preference that enlarges the blur would be the worst possible moment to.
 */
export function resolveSamplingGeometry(input: DeclaredSamplingGeometry): SamplingGeometry {
  const samplingPadding = input.samplingPadding ?? requiredSamplingPadding(input.blurRadius);
  return { samplingPadding, mergeDistance: input.mergeDistance ?? samplingPadding };
}

const area = (rect: Rect): number => rect.width * rect.height;

/** A member with no measured extent contributes nothing — it has not been read yet. */
const isMeasured = (member: ProxyMember): boolean =>
  member.bounds.width > 0 && member.bounds.height > 0;

/**
 * A rounded rectangle as an SVG path, in the coordinate space of the rect.
 *
 * Circular corners. v1's continuous corner profile lives in the shader
 * (§Geometry: the smoothing channel), and C3's contour math has not landed; a
 * mask that differs from the rendered contour by a sub-pixel sliver at each
 * corner is an honest v1 approximation, and it is stated rather than implied.
 */
export function roundedRectPath(rect: Rect, radii: CornerRadii): string {
  const limit = Math.min(rect.width, rect.height) / 2;
  const clamp = (radius: number): number => Math.max(0, Math.min(radius, limit));
  const tl = clamp(radii[0]);
  const tr = clamp(radii[1]);
  const br = clamp(radii[2]);
  const bl = clamp(radii[3]);
  const { x, y, width, height } = rect;
  const right = x + width;
  const bottom = y + height;

  const arc = (radius: number, toX: number, toY: number): string =>
    radius > 0 ? `A ${radius} ${radius} 0 0 1 ${toX} ${toY} ` : "";

  return (
    `M ${x + tl} ${y} ` +
    `L ${right - tr} ${y} ` +
    arc(tr, right, y + tr) +
    `L ${right} ${bottom - br} ` +
    arc(br, right - br, bottom) +
    `L ${x + bl} ${bottom} ` +
    arc(bl, x, bottom - bl) +
    `L ${x} ${y + tl} ` +
    arc(tl, x + tl, y) +
    "Z"
  );
}

/**
 * The largest padding in `[floor, wanted]` whose padded union fits the area cap,
 * or `floor` when even that does not. Never returns less than `floor`: a
 * starved blur is a visible artifact at every shape edge, while an over-cap
 * proxy is a hazard on one rasteriser — and the caller reports it either way.
 */
function paddingUnderAreaCap(
  union: Rect,
  wanted: number,
  floor: number,
  maxAreaCssPx: number,
): number {
  if (area(inflateRect(union, wanted)) <= maxAreaCssPx) return wanted;

  // (w + 2p)(h + 2p) = A  ->  4p² + 2p(w + h) + (wh - A) = 0
  const b = 2 * (union.width + union.height);
  const c = area(union) - maxAreaCssPx;
  const discriminant = b * b - 16 * c;
  if (discriminant < 0) return floor;

  const solved = (-b + Math.sqrt(discriminant)) / 8;
  return Math.max(floor, Math.min(wanted, Math.floor(solved)));
}

export function resolveProxyGeometry(input: ProxyGeometryInput): ProxyGeometry | undefined {
  const members = input.members.filter(isMeasured);
  if (members.length === 0) return undefined;

  const findings: ProxyFinding[] = [];

  const floor = requiredSamplingPadding(input.blurRadius);
  let padding = input.samplingPadding;

  if (padding < floor) {
    findings.push({
      code: "sampling-padding-below-3-sigma",
      severity: "warning",
      message: `samplingPadding ${input.samplingPadding} is below the 3σ floor of ${floor} for a blur radius of ${input.blurRadius} CSS px, so the proxy would starve its own blur at every shape edge — Filter Effects 2 clips the filter input to the proxy's own border box and mirrors at it. Raised to ${floor}.`,
    });
    padding = floor;
  }

  if (padding > input.mergeDistance) {
    findings.push({
      code: "merge-distance-below-effective-padding",
      severity: "warning",
      message: `The group's effective samplingPadding is ${padding} but its mergeDistance is ${input.mergeDistance}. X1 requires mergeDistance ≥ samplingPadding: below it, two members can sit close enough for their padded proxies to overlap without having merged, and the filter applies twice over the overlap. Raise mergeDistance to at least ${padding}, or lower the blur radius.`,
    });
  }

  const union = members.map((member) => member.bounds).reduce(unionRect);
  const maxAreaCssPx = input.maxProxyAreaDevicePx / (input.devicePixelRatio * input.devicePixelRatio);
  const capped = paddingUnderAreaCap(union, padding, floor, maxAreaCssPx);

  const cappedArea = area(inflateRect(union, capped));
  const stillOver = cappedArea > maxAreaCssPx;
  if (capped !== padding || stillOver) {
    const mpx = (devicePx: number): string => `${(devicePx / 1e6).toFixed(2)} Mpx`;
    findings.push({
      code: "proxy-area-over-cap",
      severity: stillOver ? "error" : "warning",
      message: stillOver
        ? `This group's proxy covers ${mpx(cappedArea * input.devicePixelRatio ** 2)} of device pixels even at the 3σ minimum padding, over this engine's conformance-table limit of ${mpx(input.maxProxyAreaDevicePx)}. Some rasterisers drop backdrop-filter silently above it, so the glass would simply stop frosting with no error. Split the group, or reduce the surface's size.`
        : `This group's samplingPadding was trimmed from ${padding} to ${capped} to keep the proxy under this engine's device-pixel limit of ${mpx(input.maxProxyAreaDevicePx)}, above which some rasterisers drop backdrop-filter silently.`,
    });
  }

  const box = inflateRect(union, capped);
  const maskBounds = members.map((member) => ({
    x: member.bounds.x - box.x,
    y: member.bounds.y - box.y,
    width: member.bounds.width,
    height: member.bounds.height,
  }));

  const subpaths = members.map((member, index) => {
    const local = maskBounds[index];
    return local === undefined ? "" : roundedRectPath(local, member.radii);
  });

  return {
    box,
    clipPath: `path("${subpaths.join(" ")}")`,
    maskBounds,
    effectivePadding: capped,
    findings,
  };
}
