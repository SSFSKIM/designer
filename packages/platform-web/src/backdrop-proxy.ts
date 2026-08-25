/**
 * The backdrop-proxy elements: one per sampling group, in the group's plane.
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

import { GLASS_PLANES, rectsOverlap, type GlassPlane, type Rect } from "vitrea";

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
   * Returns the groups whose proxy element was created or moved to another
   * plane. Those are exactly the ones whose backdrop-root chain is new and has
   * to be re-audited; every other group's chain is the one already scored.
   */
  sync(requests: readonly ProxyRequest[], environment: ProxyEnvironment): readonly string[];
  proxyFor(groupId: string): HTMLElement | undefined;
  remove(groupId: string): void;
  destroy(): void;
}

export interface ProxyEnvironment {
  readonly devicePixelRatio: number;
  /** From the engine conformance table's row for this engine. */
  readonly maxProxyAreaDevicePx: number;
}

const PROXY_STYLE = "position:absolute;pointer-events:none";

interface ProxyEntry {
  readonly element: HTMLElement;
  plane: GlassPlane;
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
    element.setAttribute("aria-hidden", "true");
    element.setAttribute("style", PROXY_STYLE);
    const entry: ProxyEntry = { element, plane };
    entries.set(groupId, entry);
    return entry;
  };

  const report = (groupId: string, finding: PlatformDiagnostic["code"], message: string, severity: PlatformDiagnostic["severity"]): void => {
    diagnostics.report({ code: finding, severity, subjects: [groupId], message });
  };

  return {
    sync(requests, environment) {
      const live = new Set<string>();
      const created: string[] = [];
      const boxes: { readonly groupId: string; readonly plane: GlassPlane; readonly box: Rect }[] =
        [];

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
        live.add(request.groupId);

        for (const finding of geometry.findings) {
          report(request.groupId, finding.code, finding.message, finding.severity);
        }

        boxes.push({ groupId: request.groupId, plane: request.plane, box: geometry.box });

        const entry = entries.get(request.groupId) ?? create(request.groupId, request.plane);
        entry.plane = request.plane;

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

      // core runs this same check against the *authored* padding, so a pair that
      // only overlaps once the 3σ floor has been applied is invisible to it —
      // and that pair double-filters exactly as measurably as any other.
      for (let i = 0; i < boxes.length; i += 1) {
        for (let j = i + 1; j < boxes.length; j += 1) {
          const a = boxes[i];
          const b = boxes[j];
          if (a === undefined || b === undefined || a.plane !== b.plane) continue;
          if (!rectsOverlap(a.box, b.box)) continue;
          diagnostics.report({
            code: "proxy-overlap-after-enforcement",
            severity: "warning",
            subjects: [a.groupId, b.groupId],
            message: `The padded proxies of groups "${a.groupId}" and "${b.groupId}" overlap in the "${a.plane}" plane once the samplingPadding ≥ 3σ floor is applied, so the backdrop filter applies twice over the overlap — paint-order dependent, measured drifting up to 17/255. Put these surfaces in one group so they share a proxy, separate them further, or lower the group's blur radius.`,
          });
        }
      }

      for (const [groupId, entry] of entries) {
        if (!live.has(groupId)) {
          entry.element.remove();
          entries.delete(groupId);
        }
      }

      // Re-sequence every plane's proxy layer from the requests' stable keys, so
      // paint order is the contract's and not the DOM's memory of insertion.
      const ordered = [...requests]
        .filter((request) => live.has(request.groupId))
        .sort((a, b) => a.order - b.order || a.groupId.localeCompare(b.groupId));

      for (const plane of GLASS_PLANES) {
        const forPlane = ordered
          .filter((request) => request.plane === plane)
          .map((request) => entries.get(request.groupId)?.element)
          .filter((element): element is HTMLElement => element !== undefined);
        options.plane(plane).proxyLayer.replaceChildren(...forPlane);
      }

      return created;
    },

    proxyFor(groupId) {
      return entries.get(groupId)?.element;
    },

    remove(groupId) {
      const entry = entries.get(groupId);
      entry?.element.remove();
      entries.delete(groupId);
    },

    destroy() {
      for (const entry of entries.values()) entry.element.remove();
      entries.clear();
    },
  };
}
