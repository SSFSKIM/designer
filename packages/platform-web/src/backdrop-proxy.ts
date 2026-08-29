/**
 * The backdrop-proxy elements: one per sampling group *per plane* it has members
 * on — a group that straddles two planes is two filtered surfaces, because each
 * plane has its own canvas pair to sit behind.
 *
 * `proxy-geometry.ts` decides the box, the mask and the padding; this module
 * owns the elements that carry them, and three properties of the element set
 * that are contract rather than style:
 *
 * - **`pointer-events: none`.** Verified in all three engines by S1:
 *   `elementFromPoint` at a panel's centre returns the host button, and neither
 *   the proxy nor a canvas appears in `elementsFromPoint`.
 * - **Both spellings of the filter.** WebKit answers `CSS.supports` only for
 *   `-webkit-backdrop-filter`; Chromium and Gecko only for the unprefixed form.
 * - **Deterministic paint order.** S1 measured that swapping two sibling
 *   proxies' paint order shifts their gap-facing bands by mean 0.5–1.0 with
 *   peaks of 7/255 — paint order is *observable*, so for a fidelity-first
 *   library group ordering has to be part of the contract and not an artefact of
 *   insertion order. Proxies are therefore re-sequenced by a stable key on every
 *   sync, not appended as groups arrive.
 *
 * The proxy element itself carries no other style. In particular it never gets
 * `opacity`, `mask-image`, `mix-blend-mode` or a `will-change` — the mask is
 * `clip-path`, which S1 measured equivalent to an SVG mask (A_edge 0.01/4) and
 * which is the one of the two that does not also need a second element.
 */

import { GLASS_PLANES, rectsOverlap, type GlassPlane, type Rect } from "@vitreajs/vitrea";

import type { PlaneLayers } from "./planes";
import { resolveProxyGeometry, type ProxyGeometryInput, type ProxyMember } from "./proxy-geometry";
import type { PlatformDiagnostic, PlatformDiagnosticsChannel } from "./diagnostics";

/** One group's proxy request: where it lives, what it covers, how it filters. */
export interface ProxyRequest {
  readonly groupId: string;
  readonly plane: GlassPlane;
  /** Stable sort key within the plane — the minimum z-slot order of the members. */
  readonly order: number;
  readonly members: readonly ProxyMember[];
  readonly samplingPadding: number;
  readonly mergeDistance: number;
  readonly blurRadius: number;
  readonly saturation: number;
}

export interface BackdropProxyManagerOptions {
  readonly plane: (plane: GlassPlane) => PlaneLayers;
  readonly diagnostics: PlatformDiagnosticsChannel;
  readonly document?: Document;
}

export interface BackdropProxyManager {
  /**
   * Bring the proxy set in line with these requests: create, update, re-order
   * and remove. Idempotent — calling it twice with the same requests writes the
   * same DOM and reports nothing new.
   *
   * Returns the group ids whose proxy element was created, or whose group gained
   * a plane. Those are exactly the ones with a backdrop-root chain nothing has
   * scored yet; every other group's chain is the one already audited. Groups are
   * deduplicated, because a split group creating two elements in one sync is one
   * group to re-audit.
   */
  sync(requests: readonly ProxyRequest[], environment: ProxyEnvironment): readonly string[];
  /**
   * The group's proxy element in one plane.
   *
   * The plane is part of the question, not a detail of it: a group whose members
   * straddle two planes gets *one proxy per plane* (§the rendering contract puts
   * one canvas pair in each), and the two sit under different ancestors, so they
   * are two different backdrop-root chains with two different geometries.
   */
  proxyFor(groupId: string, plane: GlassPlane): HTMLElement | undefined;
  /** Every plane this group currently has a proxy in. */
  planesOf(groupId: string): readonly GlassPlane[];
  /** Drops the group's proxy in every plane. */
  remove(groupId: string): void;
  destroy(): void;
}

export interface ProxyEnvironment {
  readonly devicePixelRatio: number;
  /** From the engine conformance table's row for this engine. */
  readonly maxProxyAreaDevicePx: number;
}

const PROXY_STYLE = "position:absolute;pointer-events:none";

/**
 * The entry key: a group *and* a plane.
 *
 * A group with members on two planes needs a proxy in each — one canvas pair per
 * plane means one filtered surface per plane — and keying by group alone made
 * the two planes fight over a single element: whichever request came last won it,
 * so one plane's surfaces sampled the other plane's box.
 */
const keyOf = (groupId: string, plane: GlassPlane): string => `${plane}␟${groupId}`;

interface ProxyEntry {
  readonly element: HTMLElement;
  readonly groupId: string;
  readonly plane: GlassPlane;
}

export function createBackdropProxyManager(
  options: BackdropProxyManagerOptions,
): BackdropProxyManager {
  const doc = options.document ?? document;
  const { diagnostics } = options;
  const entries = new Map<string, ProxyEntry>();

  const create = (groupId: string, plane: GlassPlane): ProxyEntry => {
    const element = doc.createElement("div");
    element.setAttribute("data-vitrea-proxy", groupId);
    element.setAttribute("data-vitrea-proxy-plane", plane);
    element.setAttribute("aria-hidden", "true");
    element.setAttribute("style", PROXY_STYLE);
    const entry: ProxyEntry = { element, groupId, plane };
    entries.set(keyOf(groupId, plane), entry);
    return entry;
  };

  const report = (groupId: string, finding: PlatformDiagnostic["code"], message: string, severity: PlatformDiagnostic["severity"]): void => {
    diagnostics.report({ code: finding, severity, subjects: [groupId], message });
  };

  return {
    sync(requests, environment) {
      const live = new Set<string>();
      /** Group ids whose chain is new this sync. A Set, so a split group counts once. */
      const created = new Set<string>();
      const boxes: {
        readonly groupId: string;
        readonly plane: GlassPlane;
        /** The padded box: everything this proxy *samples*. */
        readonly box: Rect;
        /** The unpadded shape union: everything this proxy *paints*. */
        readonly clipUnion: Rect;
      }[] = [];

      for (const request of requests) {
        const geometry = resolveProxyGeometry({
          members: request.members,
          samplingPadding: request.samplingPadding,
          mergeDistance: request.mergeDistance,
          blurRadius: request.blurRadius,
          devicePixelRatio: environment.devicePixelRatio,
          maxProxyAreaDevicePx: environment.maxProxyAreaDevicePx,
        } satisfies ProxyGeometryInput);

        if (geometry === undefined) continue;
        const key = keyOf(request.groupId, request.plane);
        live.add(key);

        for (const finding of geometry.findings) {
          report(request.groupId, finding.code, finding.message, finding.severity);
        }

        boxes.push({
          groupId: request.groupId,
          plane: request.plane,
          box: geometry.box,
          clipUnion: geometry.clipUnion,
        });

        const existing = entries.get(key);
        // A missing entry covers both cases the audit cares about, and they are
        // the same case: a first-time group and a group that moved planes both
        // arrive here with no element for this plane, so both get a chain nothing
        // has scored.
        if (existing === undefined) created.add(request.groupId);
        const entry = existing ?? create(request.groupId, request.plane);

        // σ comes from the material, never back-derived from the padding: the
        // padding may legitimately exceed 3σ, and deriving σ from it would make
        // an over-padded group blurrier than the material it belongs to.
        const filter = `blur(${request.blurRadius}px) saturate(${request.saturation})`;
        const { box } = geometry;
        entry.element.setAttribute(
          "style",
          `${PROXY_STYLE};left:${box.x}px;top:${box.y}px;width:${box.width}px;height:${box.height}px` +
            `;clip-path:${geometry.clipPath};-webkit-clip-path:${geometry.clipPath}` +
            `;backdrop-filter:${filter};-webkit-backdrop-filter:${filter}`,
        );
      }

      // The predicate is padded box against the *neighbour's painted region*,
      // not against the neighbour's padded box.
      //
      // Chaining needs one proxy's box to contain another proxy's already
      // filtered output. A group paints only inside its clip union, and its box
      // extends one padding beyond that — so a box-against-box test fires out to
      // *twice* the padding, and over the outer half of that range the boxes
      // intersect in a region neither group paints into. The double filtering
      // this message describes provably does not happen there: 81
      // byte-deterministic cells over 3 blur radii and 4 backdrop classes found
      // zero leak at every separation at or beyond one padding
      // (`spikes/s1-proxy-topology/overlap-experiment/`).
      //
      // Symmetric on purpose. Only the later-painted group is ever contaminated,
      // and the paint order here is deterministic, so this could halve again —
      // but a finding that appears and disappears as ordering changes is worse
      // diagnostics than a statement about the layout.
      //
      // core runs its own overlap test against the *authored* padding, so a pair
      // that only comes within reach once the 3σ floor is applied is invisible
      // to it — and that pair double-filters exactly as measurably as any other.
      for (let i = 0; i < boxes.length; i += 1) {
        for (let j = i + 1; j < boxes.length; j += 1) {
          const a = boxes[i];
          const b = boxes[j];
          if (a === undefined || b === undefined || a.plane !== b.plane) continue;
          if (!rectsOverlap(a.box, b.clipUnion) && !rectsOverlap(b.box, a.clipUnion)) continue;
          diagnostics.report({
            code: "proxy-overlap-after-enforcement",
            severity: "warning",
            subjects: [a.groupId, b.groupId],
            message: `Groups "${a.groupId}" and "${b.groupId}" sit close enough in the "${a.plane}" plane that one group's padded proxy box — its sampling region, the shape union grown by the effective samplingPadding once the ≥ 3σ floor is applied — covers the other group's own shapes, so the later-painted group filters over pixels the earlier one already filtered and the backdrop filter applies twice there. Paint-order dependent, and it falls off steeply with separation: measured at most 3/255 at a 1.5σ gap, mean 0.43 / max 4 at 1σ, mean 2.56 / max 15 at 0.25σ, and byte-identical zero once the gap reaches the padding. Put these surfaces in one group so they share a proxy, separate them by at least the larger group's effective samplingPadding, or lower the group's blur radius.`,
          });
        }
      }

      for (const [key, entry] of entries) {
        if (!live.has(key)) {
          entry.element.remove();
          entries.delete(key);
        }
      }

      // Re-sequence every plane's proxy layer from the requests' stable keys, so
      // paint order is the contract's and not the DOM's memory of insertion.
      const ordered = [...requests]
        .filter((request) => live.has(keyOf(request.groupId, request.plane)))
        .sort((a, b) => a.order - b.order || a.groupId.localeCompare(b.groupId));

      for (const plane of GLASS_PLANES) {
        const forPlane = ordered
          .filter((request) => request.plane === plane)
          .map((request) => entries.get(keyOf(request.groupId, plane))?.element)
          .filter((element): element is HTMLElement => element !== undefined);
        options.plane(plane).proxyLayer.replaceChildren(...forPlane);
      }

      return [...created];
    },

    proxyFor(groupId, plane) {
      return entries.get(keyOf(groupId, plane))?.element;
    },

    planesOf(groupId) {
      return [...entries.values()]
        .filter((entry) => entry.groupId === groupId)
        .map((entry) => entry.plane);
    },

    remove(groupId) {
      for (const [key, entry] of entries) {
        if (entry.groupId !== groupId) continue;
        entry.element.remove();
        entries.delete(key);
      }
    },

    destroy() {
      for (const entry of entries.values()) entry.element.remove();
      entries.clear();
    },
  };
}
