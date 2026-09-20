/**
 * The pull-to-push adapter between the runtime and React's render loop.
 *
 * `platform-web`'s root is a pull surface: `capabilities(groupId)` and
 * `accessibility` are getters that recompute on call, and nothing emits when an
 * answer changes. React needs the opposite, so this store polls both once per
 * frame and notifies only when a snapshot actually differs.
 *
 * Two properties make that cheap enough to be honest rather than a compromise:
 * only groups with a live subscriber are polled at all, and the cached snapshot
 * is returned by identity until it changes — which is what `useSyncExternalStore`
 * requires, and what keeps an unchanged frame from re-rendering anything.
 *
 * Polling is what the seam allows today. A change notification on `GlassRoot`
 * would remove this file; it is flagged as parent-impact rather than worked
 * around silently.
 */

import type { GlassGroupState, ResolvedAccessibilityPolicy } from "@vitreajs/vitrea";
import type {
  GlassRoot,
  ResolvedColorScheme,
  ResolvedWindowActivation,
} from "@vitreajs/vitrea-web";
import { createContext, useContext } from "react";

type Listener = () => void;

export interface GlassRootStore {
  subscribeAccessibility(listener: Listener): () => void;
  accessibility(): ResolvedAccessibilityPolicy | undefined;
  subscribeWindowActivation(listener: Listener): () => void;
  windowActivation(): ResolvedWindowActivation | undefined;
  subscribeColorScheme(listener: Listener): () => void;
  colorScheme(): ResolvedColorScheme | undefined;
  subscribeCapabilities(groupId: string, listener: Listener): () => void;
  capabilities(groupId: string): GlassGroupState | undefined;
  /** Re-read everything subscribed. Called once per ticker frame. */
  poll(): void;
}

/**
 * Structural equality over the state, field by field.
 *
 * Field by field rather than by identity because `capabilities(groupId)` builds
 * a fresh object on every call, so identity always differs and every frame
 * would notify.
 *
 * **Every field is compared, and that is a fix rather than a tidy.** This used
 * to list the seven core axes and stop, which meant the four the PLATFORM folds
 * on — the CSS tier's three forms and, from W29 G4, the material document that
 * drew — could change without a subscriber ever being told. The material
 * document made it visible: pinning the playground's `windowActivation` moves a
 * root from its active endpoint to its receded one, the readout is supposed to
 * say so, and it went on naming the active document because nothing here saw
 * the change. A readout that cannot report the axis it exists to report is worse
 * than no readout.
 */
const sameState = (a: GlassGroupState | undefined, b: GlassGroupState | undefined): boolean => {
  if (a === undefined || b === undefined) return a === b;
  return (
    a.configuredSource === b.configuredSource &&
    a.activeRenderer === b.activeRenderer &&
    a.samplingBackend === b.samplingBackend &&
    a.refraction === b.refraction &&
    a.analysis === b.analysis &&
    a.health === b.health &&
    a.demotionReason === b.demotionReason &&
    a.cssBody === b.cssBody &&
    a.cssTint === b.cssTint &&
    a.cssShadow === b.cssShadow &&
    sameMaterialDocument(a.materialDocument, b.materialDocument)
  );
};

/** The material readout, by value: it is a record and it is rebuilt every call. */
const sameMaterialDocument = (
  a: GlassGroupState["materialDocument"],
  b: GlassGroupState["materialDocument"],
): boolean => {
  if (a === undefined || b === undefined) return a === b;
  return (
    a.name === b.name &&
    a.platform === b.platform &&
    a.profileKey === b.profileKey &&
    a.resolvedMaterialSha256 === b.resolvedMaterialSha256 &&
    a.tuned === b.tuned
  );
};

/**
 * The accessibility policy is a fold over four booleans, so comparing the
 * booleans compares the policy: two policies with the same four inputs are
 * equal by construction (`resolveAccessibilityPolicy` is pure).
 */
const samePolicy = (
  a: ResolvedAccessibilityPolicy | undefined,
  b: ResolvedAccessibilityPolicy | undefined,
): boolean => {
  if (a === undefined || b === undefined) return a === b;
  return (
    a.reducedMotion === b.reducedMotion &&
    a.reducedTransparency === b.reducedTransparency &&
    a.increasedContrast === b.increasedContrast &&
    a.forcedColors === b.forcedColors
  );
};

export function createGlassRootStore(root: () => GlassRoot | null): GlassRootStore {
  const accessibilityListeners = new Set<Listener>();
  const activationListeners = new Set<Listener>();
  const schemeListeners = new Set<Listener>();
  const capabilityListeners = new Map<string, Set<Listener>>();

  let accessibility: ResolvedAccessibilityPolicy | undefined;
  let windowActivation: ResolvedWindowActivation | undefined;
  let colorScheme: ResolvedColorScheme | undefined;
  const capabilities = new Map<string, GlassGroupState | undefined>();

  const notify = (listeners: Iterable<Listener>): void => {
    for (const listener of [...listeners]) listener();
  };

  const readAccessibility = (): void => {
    const live = root()?.accessibility;
    if (samePolicy(accessibility, live)) return;
    accessibility = live;
    notify(accessibilityListeners);
  };

  /**
   * One enum, so identity comparison IS the snapshot comparison — the pose has
   * no structure to fold, which is the whole reason it is a pose of the root.
   */
  const readWindowActivation = (): void => {
    const live = root()?.windowActivation;
    if (windowActivation === live) return;
    windowActivation = live;
    notify(activationListeners);
  };

  /**
   * The resolved scheme, on the same argument as the pose above: one enum, so
   * identity is the comparison.
   *
   * Polled rather than taken from the prop, because `colorScheme="auto"` is
   * resolved inside the runtime against `prefers-color-scheme` — the answer
   * moves with the system while the prop stands still. A consumer that derives
   * a number from the scheme's material (`GlassToolbar`'s gap, W30 Decision
   * Log 1 (f)) would otherwise hold the first frame's answer forever.
   */
  const readColorScheme = (): void => {
    const live = root()?.colorScheme;
    if (colorScheme === live) return;
    colorScheme = live;
    notify(schemeListeners);
  };

  const readCapabilities = (groupId: string): void => {
    const live = root()?.capabilities(groupId);
    if (capabilities.has(groupId) && sameState(capabilities.get(groupId), live)) return;
    capabilities.set(groupId, live);
    notify(capabilityListeners.get(groupId) ?? []);
  };

  return {
    subscribeAccessibility(listener) {
      accessibilityListeners.add(listener);
      readAccessibility();
      return () => accessibilityListeners.delete(listener);
    },

    accessibility: () => accessibility,

    subscribeWindowActivation(listener) {
      activationListeners.add(listener);
      readWindowActivation();
      return () => activationListeners.delete(listener);
    },

    windowActivation: () => windowActivation,

    subscribeColorScheme(listener) {
      schemeListeners.add(listener);
      readColorScheme();
      return () => schemeListeners.delete(listener);
    },

    colorScheme: () => colorScheme,

    subscribeCapabilities(groupId, listener) {
      const listeners = capabilityListeners.get(groupId) ?? new Set<Listener>();
      listeners.add(listener);
      capabilityListeners.set(groupId, listeners);
      readCapabilities(groupId);
      return () => {
        listeners.delete(listener);
        if (listeners.size === 0) {
          capabilityListeners.delete(groupId);
          capabilities.delete(groupId);
        }
      };
    },

    capabilities: (groupId) => capabilities.get(groupId),

    poll() {
      readAccessibility();
      readWindowActivation();
      readColorScheme();
      for (const groupId of capabilityListeners.keys()) readCapabilities(groupId);
    },
  };
}

/**
 * The store lives in its own context rather than on the root handle so nothing
 * outside this package can reach the poller: it is a workaround for a missing
 * change notification, not an API.
 */
export const GlassStoreContext = createContext<GlassRootStore | null>(null);

export function useGlassRootStore(): GlassRootStore {
  const store = useContext(GlassStoreContext);
  if (store === null) {
    throw new Error(
      "vitrea-react: this hook reads runtime state, so it must be rendered inside a <GlassRoot>.",
    );
  }
  return store;
}
