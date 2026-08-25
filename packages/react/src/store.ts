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

import type { GlassGroupState, ResolvedAccessibilityPolicy } from "@vitrea/core";
import type { GlassRoot } from "@vitrea/platform-web";
import { createContext, useContext } from "react";

type Listener = () => void;

export interface GlassRootStore {
  subscribeAccessibility(listener: Listener): () => void;
  accessibility(): ResolvedAccessibilityPolicy | undefined;
  subscribeCapabilities(groupId: string, listener: Listener): () => void;
  capabilities(groupId: string): GlassGroupState | undefined;
  /** Re-read everything subscribed. Called once per ticker frame. */
  poll(): void;
}

/** Structural equality over the flat state objects both snapshots are. */
const sameState = (a: GlassGroupState | undefined, b: GlassGroupState | undefined): boolean => {
  if (a === undefined || b === undefined) return a === b;
  return (
    a.configuredSource === b.configuredSource &&
    a.activeRenderer === b.activeRenderer &&
    a.samplingBackend === b.samplingBackend &&
    a.refraction === b.refraction &&
    a.analysis === b.analysis &&
    a.health === b.health &&
    a.demotionReason === b.demotionReason
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
  const capabilityListeners = new Map<string, Set<Listener>>();

  let accessibility: ResolvedAccessibilityPolicy | undefined;
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
      "@vitrea/react: this hook reads runtime state, so it must be rendered inside a <GlassRoot>.",
    );
  }
  return store;
}
