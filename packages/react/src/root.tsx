/**
 * `GlassRoot` — the provider, and the only component that owns a lifecycle.
 *
 * It creates one `platform-web` root, keeps it alive for the tree's lifetime,
 * and tears it down on unmount. Everything else in this package registers
 * against that root and owns nothing.
 *
 * ## Why children render before the root exists
 *
 * The runtime is built in an effect, not during render: `createGlassRoot`
 * appends DOM, starts a `requestAnimationFrame` loop and installs a
 * `MutationObserver`, and doing that from a render body would leak a whole
 * runtime under React 19's StrictMode double-invocation. So the first render
 * has `root === null`, and glass surfaces render nothing for exactly one commit
 * while ordinary page content renders immediately. Gating the whole tree instead
 * would delay the app's own content on vitrea's schedule, which is the wrong
 * trade: acceptance #1 is that a React app wraps its tree and its content stays
 * ordinary DOM.
 *
 * ## Accessibility (parent acceptance #6)
 *
 * Nothing here reads a media query. `platform-web` feeds core's resolver from
 * `matchMedia`, core folds the four preferences into one policy, and this
 * component's three props are the override layer core already models. The fourth
 * preference, `forced-colors`, has no prop on purpose — core's
 * `OverridableAccessibilityFlag` excludes it, so an operating-system colour
 * mandate is not expressible as an app override in the type system, let alone at
 * runtime.
 */

import type {
  AccessibilityOverride,
  AccessibilityOverrides,
  GlassGroupState,
  ResolvedAccessibilityPolicy,
} from "@vitreajs/vitrea";
import { DEFAULT_MOTION_PROFILE, withReducedMotion, type MotionProfile } from "@vitrea/motion";
import {
  consoleDiagnosticSink,
  createGlassRoot,
  type GlassRoot as PlatformGlassRoot,
  type VitreaDiagnostic,
  type VitreaDiagnosticSink,
} from "@vitrea/platform-web";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";

import {
  GlassRootContext,
  useGlassGroupId,
  useGlassRootHandle,
  type GlassRootHandle,
  type RecordedDiagnostic,
} from "./context";
import {
  createGlassRootStore,
  GlassStoreContext,
  useGlassRootStore,
  type GlassRootStore,
} from "./store";
import { createGlassTicker, type GlassTicker } from "./ticker";

export interface GlassRootProps {
  readonly children?: ReactNode | undefined;
  /**
   * Which renderer this root wires. `"css"` (the default, and platform-web's)
   * wires no GPU at all and resolves every group to the CSS tier — the honest
   * configuration of a root with no WebGPU in play, not a placeholder.
   */
  readonly renderer?: "css" | "webgpu" | undefined;
  readonly powerPreference?: GPUPowerPreference | undefined;
  /** `"system"` follows the media query; a boolean overrules it (§Accessibility). */
  readonly reducedMotion?: AccessibilityOverride | undefined;
  readonly reducedTransparency?: AccessibilityOverride | undefined;
  readonly increasedContrast?: AccessibilityOverride | undefined;
  /**
   * Motion constants. Defaults to `DEFAULT_MOTION_PROFILE`, whose numbers are
   * advisory until calibration (C7) replaces them; the Reduced Motion transform
   * is applied on top of whatever is passed, never instead of it.
   */
  readonly profile?: MotionProfile | undefined;
  /** Where the plane DOM is attached. Defaults to `document.body`. */
  readonly container?: HTMLElement | undefined;
  readonly zIndex?: number | undefined;
  /** Dev-mode checks — overlap, variant mixing, the probe's messages. Default true. */
  readonly devMode?: boolean | undefined;
  /** Replaces the console sink. Diagnostics are still recorded for `useGlassDiagnostics`. */
  readonly onDiagnostic?: VitreaDiagnosticSink | undefined;
  /** Drive frames from `requestAnimationFrame`. Default true; tests step by hand. */
  readonly autoStart?: boolean | undefined;
}

interface DiagnosticStore {
  readonly entries: RecordedDiagnostic[];
  subscribe(listener: () => void): () => void;
  push(diagnostic: VitreaDiagnostic): void;
}

/** Newest-last, capped: a devtools panel wants a tail, not an unbounded leak. */
const DIAGNOSTIC_TAIL = 200;

function createDiagnosticStore(): DiagnosticStore {
  const listeners = new Set<() => void>();
  let entries: RecordedDiagnostic[] = [];
  let seq = 0;

  return {
    get entries() {
      return entries;
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    push(diagnostic) {
      seq += 1;
      entries = [...entries, { ...diagnostic, seq }].slice(-DIAGNOSTIC_TAIL);
      for (const listener of [...listeners]) listener();
    },
  };
}

export function GlassRoot(props: GlassRootProps): ReactNode {
  const {
    children,
    renderer = "css",
    powerPreference,
    reducedMotion = "system",
    reducedTransparency = "system",
    increasedContrast = "system",
    profile: baseProfile = DEFAULT_MOTION_PROFILE,
    container,
    zIndex,
    devMode = true,
    onDiagnostic,
    autoStart = true,
  } = props;

  const [root, setRoot] = useState<PlatformGlassRoot | null>(null);
  const rootRef = useRef<PlatformGlassRoot | null>(null);

  const diagnosticStore = useMemo(createDiagnosticStore, []);
  const store: GlassRootStore = useMemo(
    () => createGlassRootStore(() => rootRef.current),
    [],
  );
  const ticker: GlassTicker = useMemo(() => createGlassTicker(), []);

  // Held in a ref so changing the sink never rebuilds the runtime: a callback
  // prop that is a fresh closure every render is the common case, and a root
  // that tore itself down for it would drop every registration in the tree.
  const sinkRef = useRef<VitreaDiagnosticSink | undefined>(onDiagnostic);
  sinkRef.current = onDiagnostic;

  useEffect(() => {
    const consoleSink = consoleDiagnosticSink();
    const sink: VitreaDiagnosticSink = (diagnostic) => {
      diagnosticStore.push(diagnostic);
      // The default is the console *because* acceptance #6 asks for the
      // variant-mixing warning to be visible in devtools without any wiring.
      (sinkRef.current ?? consoleSink)(diagnostic);
    };

    const created = createGlassRoot({
      devMode,
      renderer,
      autoStart,
      diagnosticSink: sink,
      ...(container === undefined ? {} : { container }),
      ...(zIndex === undefined ? {} : { zIndex }),
      ...(powerPreference === undefined ? {} : { webgpu: { powerPreference } }),
    });

    rootRef.current = created;
    setRoot(created);

    return () => {
      created.destroy();
      rootRef.current = null;
      setRoot(null);
    };
  }, [autoStart, container, devMode, diagnosticStore, powerPreference, renderer, zIndex]);

  useEffect(() => {
    if (root === null) return;
    const overrides: AccessibilityOverrides = {
      reducedMotion,
      reducedTransparency,
      increasedContrast,
    };
    root.setAccessibilityOverrides(overrides);
    store.poll();
  }, [increasedContrast, reducedMotion, reducedTransparency, root, store]);

  useEffect(() => {
    if (root === null) return;
    const unsubscribe = ticker.subscribe(() => store.poll());
    if (autoStart) ticker.start();
    return () => {
      unsubscribe();
      ticker.stop();
    };
  }, [autoStart, root, store, ticker]);

  useEffect(() => () => ticker.destroy(), [ticker]);

  const policy = useSyncExternalStore(
    useCallback((listener) => store.subscribeAccessibility(listener), [store]),
    () => store.accessibility(),
    () => undefined,
  );

  // Ordering is motion's, not a preference: app overrides are taken at face
  // value and the Reduced Motion transform goes last, because it is idempotent
  // in the damping floor but not in the response factor.
  const motionProfile = useMemo(
    () => (policy?.reducedMotion === true ? withReducedMotion(baseProfile) : baseProfile),
    [baseProfile, policy?.reducedMotion],
  );

  const diagnostics = useSyncExternalStore(
    useCallback((listener) => diagnosticStore.subscribe(listener), [diagnosticStore]),
    () => diagnosticStore.entries,
    () => diagnosticStore.entries,
  );

  const handle: GlassRootHandle = useMemo(
    () => ({
      root,
      ticker,
      profile: motionProfile,
      devMode,
      diagnostics,
      subscribeDiagnostics: (listener) => diagnosticStore.subscribe(listener),
    }),
    [devMode, diagnostics, diagnosticStore, motionProfile, root, ticker],
  );

  return (
    <GlassRootContext.Provider value={handle}>
      <GlassStoreContext.Provider value={store}>{children}</GlassStoreContext.Provider>
    </GlassRootContext.Provider>
  );
}

/**
 * The resolved capability state of one glass group (X2).
 *
 * Reports what the runtime *actually* resolved, never what was asked for:
 * `configuredSource` survives every demotion, and a demoted group always names
 * its reason. `undefined` means the group is not registered yet — the first
 * commit, or an id that does not exist.
 */
export function useGlassCapabilities(groupId?: string): GlassGroupState | undefined {
  const store = useGlassRootStore();
  const id = useGlassGroupId(groupId);
  return useSyncExternalStore(
    useCallback((listener) => store.subscribeCapabilities(id, listener), [id, store]),
    () => store.capabilities(id),
    () => undefined,
  );
}

/** The four preferences and everything they resolved to (§Accessibility policy). */
export function useGlassAccessibility(): ResolvedAccessibilityPolicy | undefined {
  const store = useGlassRootStore();
  return useSyncExternalStore(
    useCallback((listener) => store.subscribeAccessibility(listener), [store]),
    () => store.accessibility(),
    () => undefined,
  );
}

/** Everything both diagnostics code spaces have reported, newest last. */
export function useGlassDiagnostics(): readonly RecordedDiagnostic[] {
  return useGlassRootHandle().diagnostics;
}

/** The motion constants in force, Reduced Motion already folded in. */
export function useGlassMotionProfile(): MotionProfile {
  return useGlassRootHandle().profile;
}

/**
 * The frame ticker every surface, indicator and morph in this tree animates on.
 *
 * Public because `autoStart={false}` would otherwise be a switch with nothing on
 * the other side: an app driving vitrea from its own clock — a test, a paused
 * scene, a deterministic capture — advances it through here.
 */
export function useGlassTicker(): GlassTicker {
  return useGlassRootHandle().ticker;
}
