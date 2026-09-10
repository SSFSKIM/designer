/**
 * One backdrop proxy per sampling group, constructed the way S1 measured it.
 *
 * Four properties are normative, not stylistic:
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
 * 4. **Presence attenuates, never resizes.** A member's `materialization` decides
 *    an alpha: the box, the union and the padding are the ones the group's
 *    measured members give whatever their presence, so one member fading cannot
 *    move the geometry a sibling is rendered from or the blur input a sibling
 *    samples. The one thing it does decide is whether the member is painted at
 *    all — a member at exactly 0 leaves the painted shape, because absence is an
 *    endpoint rather than a low alpha. See `ProxyPresence`.
 *
 * Everything here is pure arithmetic over measured rects: no DOM, no reads. The
 * element that carries the result is `backdrop-proxy.ts`'s job.
 */

import { clipRect, inflateRect, unionRect, type CornerRadii, type Rect } from "@vitreajs/vitrea";

import { requiredSamplingPadding } from "./optics";

/** A group member as this module needs it: a measured rect and its corner radii. */
export interface ProxyMember {
  readonly nodeId: string;
  readonly bounds: Rect;
  readonly radii: CornerRadii;
  /**
   * The clip windows this member's ancestors impose, viewport space, from the
   * read phase (Decision Log #41(k)). Absent for a member nothing clips, which
   * is the common case.
   *
   * A proxy is not inside the app's scroller — it lives in the plane layer — so
   * nothing crops it on the browser's behalf. Before this travelled, a surface
   * scrolled halfway out of an `overflow: scroll` ancestor had its glass painted
   * in full, outside the box that was supposed to be cropping it.
   */
  readonly clip?: readonly Rect[];
  /**
   * The surface's material presence, `[0, 1]`, absent wherever the surface is
   * fully materialized — which is every surface that never animates one, so the
   * resting page never carries this at all.
   *
   * The proxy is the DOM half of a WebGPU-tier group's material, so presence has
   * to reach it or it does not exist. The shader can fade one surface's optics to
   * nothing (§Where each feature lives: presence, not alpha) while the group's
   * proxy — a *sibling* of the host, one per group per plane — goes on filtering
   * the page beneath it, leaving a blurred rectangle standing exactly where the
   * glass was supposed to have gone. `ProxyPresence` is what that value becomes.
   */
  readonly materialization?: number;
}

/**
 * How the proxy element is to carry its members' presence — the *value*, not the
 * declaration, which is `backdrop-proxy.ts`'s.
 *
 * Three kinds because three cases are genuinely different, and the first of them
 * is the one the whole resting page is in:
 *
 * - **`present`.** Every member fully materialized. Nothing is added to the
 *   element at all, so a page that never animates presence writes byte-identical
 *   CSS to the one before this existed.
 * - **`uniform`.** One alpha across the group — every single-member group in
 *   transit, which is nearly every group that ever moves. Carried by `opacity`
 *   on the proxy itself: claims §5.71 §1 measured `opacity: a` and a uniform
 *   `mask-image` of alpha *a* on a `backdrop-filter` layer bit-identical over the
 *   material's interior (RMS 0.000000), and `opacity` is the one of the two that
 *   costs no per-frame image decode and that the CSS tier already ships on every
 *   engine as its portable carrier.
 * - **`per-member`.** Members at different alphas, which no element-level property
 *   can express. Carried by a `mask-image` built from the clip path's own
 *   subpaths at one `fill-opacity` per distinct alpha — and it *replaces* the
 *   clip path rather than joining it, which is measured rather than chosen.
 *
 * **On a `backdrop-filter` layer, Chromium does not compose a `clip-path` and a
 * `mask-image`: the clip wins and the mask has no effect on the filtered
 * backdrop at all.** Measured here on the harness's checkerboard at σ 8, one
 * member, interior against the unfiltered ground: clip alone Δ31, clip +
 * `opacity: 0.5` Δ15, clip + a uniform mask at alpha 0.5 Δ**31**, mask alone at
 * alpha 1 Δ31 with the padding ring byte-identical, mask alone at 0.5 Δ15. So a
 * mask *alone* carries the silhouette exactly and the alpha exactly, matching
 * `opacity` at the same value — this extends claims §5.71 §1, which separated ten
 * carriers on a layer that had no clip path to disagree with.
 *
 * That makes the fallback below load-bearing. Where the engine conformance table
 * does not say `maskOnBackdropFilter: "yes"`, dropping the clip path for a mask
 * the engine might ignore would leave a full-strength blurred rectangle standing
 * proud of the glass — the 102.92/255 halo of property 1 above, the worst artifact
 * S1 measured. So an unverified engine reduces a mixed group to `uniform` at the
 * group's **maximum** presence: nobody is blanked, nobody loses frost they were
 * entitled to, and a member part-way through a transit keeps the group's presence
 * until the group agrees. Same gate, same reason and same table row as the CSS
 * tier's own raster mask (`css-tier.ts`).
 *
 * What that fallback does *not* get to approximate is the endpoint. A member at
 * exactly 0 is absent on every engine, because it leaves the painted shape
 * altogether (`paintedSubpaths`) rather than relying on an alpha to hide it — so
 * `Glass.identity` is identity everywhere, and only the intermediate frost of a
 * disagreeing group is engine-dependent.
 *
 * **Presence is member-local** whichever carrier runs: the group's box, clip union
 * and padding are computed over every measured member whatever its presence, so a
 * member at 0 keeps its place in the geometry and a neighbour at 1 renders
 * byte-identically throughout its neighbour's transit — the proxy's blur input
 * does not move when a sibling fades.
 *
 * The approximation, stated: where two members at *different* alphas overlap,
 * the mask composites their two paths source-over rather than taking either
 * alpha, so the shared pixels read fractionally more present than the front
 * member alone. Members at the same alpha share one `<path>` and are exact under
 * any overlap, which covers every group at rest and every group in a uniform
 * transit; and a group whose members overlap at all is one whose merge distance
 * has already put them in a single shape union.
 *
 * The second approximation, the one that comes with changing carrier: the mask's
 * antialiased contour and the clip path's are the same geometry drawn by two
 * rasterisers, and §5.71 §1 measured them disagreeing by up to one strong code
 * value on the single contour pixel. A group crossing into or out of a mixed
 * presence can therefore move that pixel; nothing inside the shape or in the
 * padding ring moves with it.
 */
export type ProxyPresence =
  | { readonly kind: "present" }
  | { readonly kind: "uniform"; readonly alpha: number }
  | { readonly kind: "per-member"; readonly maskImage: string };

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
  /**
   * The engine conformance table's `maskOnBackdropFilter` row: whether a
   * `mask-image` on a `backdrop-filter` layer composes (claims §5.71 §1). Absent
   * reads as `"unverified"`, which is the conservative answer and the one that
   * keeps the silhouette on `clip-path` — see `ProxyPresence` for what turns on
   * it.
   */
  readonly maskOnBackdropFilter?: "yes" | "no" | "unverified";
}

export interface ProxyGeometry {
  /** The proxy element's border box, in viewport CSS px. */
  readonly box: Rect;
  /**
   * The *unpadded* union of the members' visible extents, in viewport CSS px —
   * the region this proxy can actually paint into, since the clip path never
   * leaves it.
   *
   * "Visible" rather than "measured" since Decision Log #41(k): a member's
   * border box is reported unclipped, so a union built from boxes claimed
   * regions an ancestor was cropping and the sentence above was false under any
   * `overflow: scroll`. The cross-group overlap check in `backdrop-proxy.ts`
   * rests on exactly that sentence.
   *
   * `box` is this rect inflated by `effectivePadding`; the difference between
   * the two is sampled but never drawn, which is what the overlap check needs to
   * tell apart.
   */
  readonly clipUnion: Rect;
  /**
   * `clip-path` value: the exact member-shape union, in proxy-local px, minus any
   * member at zero presence — see `paintedSubpaths`. Untouched by any other
   * presence, so a page that never animates one writes the value it always wrote.
   */
  readonly clipPath: string;
  /**
   * Every member's box in proxy-local px, in the members' own order — the
   * geometry the subpaths are built from, including any member the painted shape
   * has dropped.
   */
  readonly maskBounds: readonly Rect[];
  /** How the element is to carry the members' presence. */
  readonly presence: ProxyPresence;
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
 * cross-group overlap check still fires wherever an enlarged blur really does
 * put one group's sampling region over another group's shapes — going quiet
 * about that under exactly the preference that enlarges the blur would be the
 * worst possible moment to. What that check no longer does is accuse a pair
 * whose padded boxes merely meet outside both clips; `backdrop-proxy.ts` carries
 * the measurement.
 */
export function resolveSamplingGeometry(input: DeclaredSamplingGeometry): SamplingGeometry {
  const samplingPadding = input.samplingPadding ?? requiredSamplingPadding(input.blurRadius);
  return { samplingPadding, mergeDistance: input.mergeDistance ?? samplingPadding };
}

const area = (rect: Rect): number => rect.width * rect.height;

/**
 * A member with no extent contributes nothing.
 *
 * Two different states collapse onto this one predicate on purpose: a host that
 * has not been read yet, and a host its ancestors have cropped to nothing —
 * scrolled out of its scroller, or inside a collapsed panel. Neither can be
 * painted and neither should pull the group's proxy towards it, so "not there"
 * is one answer rather than two.
 */
const isMeasured = (member: ProxyMember): boolean =>
  member.bounds.width > 0 && member.bounds.height > 0;

/**
 * A member reduced to the part of it its ancestors let through.
 *
 * The radii go square on every corner whose edge the clip moved, which is what
 * a rectangular crop of a rounded rect actually looks like: crop the right-hand
 * third of a pill and the left corners stay round, the cut edge is straight.
 * Keeping the radii would put a rounded corner in the middle of a scroller,
 * which reads as a rendering fault rather than as a crop.
 *
 * The clip is folded as rects, which is where the approximation is: a rounded
 * clipping ancestor is carried as its bounding box (see core's `clipRect`), so a
 * surface tucked into a rounded scroller's own corner is treated as marginally
 * more visible than it is. The error is bounded by that ancestor's radius.
 */
function clipMember(member: ProxyMember): ProxyMember {
  if (member.clip === undefined || member.clip.length === 0) return member;

  const bounds = clipRect(member.bounds, member.clip);
  if (bounds.width <= 0 || bounds.height <= 0) return { ...member, bounds };

  const leftCut = bounds.x > member.bounds.x;
  const topCut = bounds.y > member.bounds.y;
  const rightCut = bounds.x + bounds.width < member.bounds.x + member.bounds.width;
  const bottomCut = bounds.y + bounds.height < member.bounds.y + member.bounds.height;

  const [tl, tr, br, bl] = member.radii;
  const radii: CornerRadii = [
    leftCut || topCut ? 0 : tl,
    topCut || rightCut ? 0 : tr,
    rightCut || bottomCut ? 0 : br,
    bottomCut || leftCut ? 0 : bl,
  ];

  return { ...member, bounds, radii };
}

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
 * A member's presence, clamped and quantised to a thousandth.
 *
 * Quantised because the value arrives from a per-frame driver and lands in a
 * style string: three decimals is the precision the CSS tier already writes its
 * own share at, it puts a hard floor under how often the carrier changes, and —
 * the property that matters most — it makes the two endpoints *reachable*. A
 * driver a ten-thousandth away from 1 has arrived, and must write the resting
 * page's own CSS rather than an `opacity: 0.9999` that differs from it.
 *
 * A value that is absent or not a number is a surface that never declared a
 * presence, which is full presence.
 */
function presenceOf(member: ProxyMember): number {
  const declared = member.materialization;
  if (declared === undefined || !Number.isFinite(declared)) return 1;
  return Math.round(Math.min(1, Math.max(0, declared)) * 1000) / 1000;
}

/**
 * The `mask-image` for members that do not share one alpha.
 *
 * One `<path>` per *distinct* alpha rather than per member, so members that agree
 * composite as a single fill and are exact wherever they overlap; a member at
 * alpha 0 is left out altogether, since an absent path and a path filled at zero
 * are the same mask and only one of them is carried in the URL. The subpaths are
 * the clip path's own, which is what keeps the mask from ever disagreeing with
 * the silhouette by more than the antialiased contour pixel §5.71 §1 measured.
 *
 * The SVG is sized in the proxy's own local px, so the declaration's
 * `mask-size: 100% 100%` maps it onto the border box at scale 1 and no rounding
 * of an intrinsic size can shift the geometry.
 */
function presenceMaskImage(
  box: Rect,
  subpaths: readonly string[],
  alphas: readonly number[],
): string {
  const byAlpha = new Map<number, string[]>();
  subpaths.forEach((subpath, index) => {
    const alpha = alphas[index] ?? 1;
    if (alpha === 0 || subpath === "") return;
    const together = byAlpha.get(alpha);
    if (together === undefined) byAlpha.set(alpha, [subpath]);
    else together.push(subpath);
  });

  const paths = [...byAlpha]
    .map(
      ([alpha, together]) =>
        `<path fill="#fff" fill-opacity="${alpha}" d="${together.join(" ")}"/>`,
    )
    .join("");
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${box.width}" height="${box.height}"` +
    ` viewBox="0 0 ${box.width} ${box.height}">${paths}</svg>`;

  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

/**
 * The subpaths the proxy actually paints: every member that has any presence at
 * all.
 *
 * A member at exactly 0 is *absent*, not faint, and that endpoint is not a thing
 * any carrier gets to approximate. Dropping it from the painted shape is what
 * delivers it on the one path where the alpha carrier cannot: the fallback for an
 * engine whose mask on a filtered layer is unverified, which reduces a
 * disagreeing group to one `opacity` and would otherwise hold a dematerialized
 * member at the group's presence. The mask carrier omits the same members for the
 * same reason, and a group where nobody has faded is untouched — the resting page
 * writes the clip path it always wrote.
 *
 * Where *every* member has gone, the shape is unobservable — that group is
 * `display: none` — and a `path("")` is not a valid CSS value, so the full set
 * stands in.
 */
function paintedSubpaths(
  subpaths: readonly string[],
  alphas: readonly number[],
): readonly string[] {
  const painted = subpaths.filter((_, index) => (alphas[index] ?? 1) > 0);
  return painted.length === 0 ? subpaths : painted;
}

function resolvePresence(
  box: Rect,
  subpaths: readonly string[],
  alphas: readonly number[],
  maskable: boolean,
): ProxyPresence {
  /** Full presence is the absence of a carrier, however the group arrived at it. */
  const shared = (alpha: number): ProxyPresence =>
    alpha === 1 ? { kind: "present" } : { kind: "uniform", alpha };

  const first = alphas[0] ?? 1;
  if (alphas.every((alpha) => alpha === first)) return shared(first);
  if (!maskable) return shared(Math.max(...alphas));
  return { kind: "per-member", maskImage: presenceMaskImage(box, subpaths, alphas) };
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
  // Clipped first, then filtered: a member its ancestors crop to nothing is as
  // absent as an unmeasured one, and everything below this line works on the
  // region the group can actually paint rather than on border boxes.
  const members = input.members.map(clipMember).filter(isMeasured);
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

  const alphas = members.map(presenceOf);

  return {
    box,
    clipUnion: union,
    clipPath: `path("${paintedSubpaths(subpaths, alphas).join(" ")}")`,
    maskBounds,
    presence: resolvePresence(box, subpaths, alphas, input.maskOnBackdropFilter === "yes"),
    effectivePadding: capped,
    findings,
  };
}
