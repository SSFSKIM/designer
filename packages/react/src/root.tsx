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
  DEFAULT_MATERIAL_PROFILE_DOCUMENT,
  type CssTierMapping,
  type GlassColorScheme,
  type GlassMaterialProfileDocument,
  type GlassRoot as PlatformGlassRoot,
  type GlassWindowActivation,
  type RendererMaterialProfile,
  type ResolvedWindowActivation,
  type VitreaDiagnostic,
  type VitreaDiagnosticSink,
} from "@vitreajs/vitrea-web";
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
  /**
   * Which colour scheme's material the root draws (W21 G3). `"light"` by
   * default, so nothing moves for an app that upgrades; `"dark"` selects the
   * measured dark material, and `"auto"` follows `prefers-color-scheme` and
   * re-derives both tiers when the operating system flips.
   *
   * Distinct from a surface's backdrop `hint`, which states the tone of what is
   * behind that surface. This states which material the surface is made of.
   */
  readonly colorScheme?: GlassColorScheme | undefined;
  /**
   * Which **measured material** this root draws, as one document (W29 G4).
   *
   * Defaults to `macos27MaterialProfileDocument` — what a Mac draws today —
   * with `macos26MaterialProfileDocument` shipped beside it for a page pinned to
   * the material it was designed against. A document carries the active patch
   * and the receded difference for both colour schemes plus the CSS tier's
   * crossing, so selecting one moves every tier and both poses at once; before
   * this prop a React app could not select a reference material at all.
   *
   * Read at construction, because `createGlassRoot` selects it there: a scheme
   * and a window pose move within one material, where a different document is a
   * different material and a root already drawing one has surfaces measured
   * against it.
   */
  readonly materialProfileDocument?: GlassMaterialProfileDocument | undefined;
  /**
   * A tuning over whatever the document selected — the renderer's optical
   * constants, leaf by leaf.
   *
   * Applied live, because `createGlassRoot` exposes a setter for it and a
   * material change is not a reason to tear a root down. Hold the object still
   * between renders: an inline literal is a new value every render and re-derives
   * both tiers each time.
   */
  readonly materialProfile?: RendererMaterialProfile | undefined;
  /**
   * What the material costs to express as `backdrop-filter` plus an overlay, for
   * the visitors on the CSS tier.
   *
   * Calibration's seam rather than an application knob — the shipped mapping is
   * tuned against the dom-tier cells, and the selected document brings its own —
   * and it is surfaced here only so that an app handing this binding a whole
   * measured material by hand can hand over both halves of it. Read at
   * construction, which is where the root reads it.
   */
  readonly cssTierMapping?: Partial<CssTierMapping> | undefined;
  /**
   * Whether this window's glass draws the active material or the receded one
   * (W28 G3). `"auto"` is the default and follows the window's own focus;
   * `"active"` and `"inactive"` pin the pose and win over what the window is
   * doing, which is what a preview, a screenshot or a capture harness needs.
   *
   * A pose of the root, not a state of a surface: a window's activation is one
   * fact per document, so it is not a seventh interaction state and no surface
   * carries it.
   */
  readonly windowActivation?: GlassWindowActivation | undefined;
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
    colorScheme = "light",
    materialProfileDocument,
    materialProfile,
    cssTierMapping,
    windowActivation = "auto",
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

  /*
   * The document the runtime SELECTED, which is not always the one the prop
   * names (W30 Decision Log 1 (f)).
   *
   * `createGlassRoot` reads `materialProfileDocument` once, at construction, and
   * a later change to the prop does not move the material the page draws — so a
   * handle that reported the prop would name a material nothing is drawing, and
   * `GlassToolbar` would open its split at it. Seeded from the prop so the
   * first render, before the mount effect, already derives its layout from the
   * right material; re-stated inside the effect so a rebuild (a `renderer`
   * change, say) carries whatever that construction actually read.
   */
  const [selectedDocument, setSelectedDocument] = useState<GlassMaterialProfileDocument>(
    () => materialProfileDocument ?? DEFAULT_MATERIAL_PROFILE_DOCUMENT,
  );

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

  // Held for the same reason, one line up: the construction effect must not
  // re-run when the scheme changes.
  const schemeRef = useRef<GlassColorScheme>(colorScheme);
  schemeRef.current = colorScheme;

  // And the activation pose, on the same argument.
  const activationRef = useRef<GlassWindowActivation>(windowActivation);
  activationRef.current = windowActivation;

  /*
   * The material props, held in refs for the reason the scheme and the pose
   * above are: the root reads each of them once at construction, and putting an
   * object-valued prop in the effect's dependency list would tear the runtime
   * down and rebuild it — dropping every registration in the tree — the first
   * time a parent re-rendered with a fresh literal. `materialProfile` is
   * additionally applied to the live root below, because the root has a setter
   * for it and a tuning change is not a reason to rebuild anything.
   */
  const documentRef = useRef<GlassMaterialProfileDocument | undefined>(materialProfileDocument);
  documentRef.current = materialProfileDocument;
  const mappingRef = useRef<Partial<CssTierMapping> | undefined>(cssTierMapping);
  mappingRef.current = cssTierMapping;
  const materialRef = useRef<RendererMaterialProfile | undefined>(materialProfile);
  materialRef.current = materialProfile;

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
      // Read at construction so the very first frame draws the right material.
      // A later change reaches the root through the setter below rather than
      // through this dependency list: rebuilding the runtime for a theme toggle
      // would drop every registration in the tree.
      colorScheme: schemeRef.current,
      // Read at construction for the same reason: a root mounted with the pose
      // already pinned must draw it on its first frame rather than flashing the
      // active material for one.
      windowActivation: activationRef.current,
      // Read at construction because the root selects its material there, and
      // for the same reason the two above are: the first frame has to draw the
      // material the app asked for rather than a default it would then be moved
      // off one frame later.
      ...(documentRef.current === undefined
        ? {}
        : { materialProfileDocument: documentRef.current }),
      ...(mappingRef.current === undefined ? {} : { cssTierMapping: mappingRef.current }),
      ...(materialRef.current === undefined ? {} : { materialProfile: materialRef.current }),
    });

    rootRef.current = created;
    setRoot(created);
    setSelectedDocument(documentRef.current ?? DEFAULT_MATERIAL_PROFILE_DOCUMENT);

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

  /*
   * The app's own tuning over the selected document, applied to the live root
   * exactly as the scheme below is.
   *
   * Withdrawing the prop sends the empty patch rather than skipping the call,
   * and that is the whole of "the app took its tuning back": a root that kept
   * the last patch it was given would go on drawing a material the app has
   * stopped asking for. Skipped entirely on the construction pass, where the
   * option above already carried it.
   */
  const materialApplied = useRef(false);
  useEffect(() => {
    if (root === null) return;
    if (!materialApplied.current) {
      materialApplied.current = true;
      return;
    }
    root.setMaterialProfile(materialProfile ?? {});
  }, [materialProfile, root]);

  // The scheme is a material change, applied to the live root exactly as the
  // accessibility overrides above are.
  useEffect(() => {
    if (root === null) return;
    root.setColorScheme(colorScheme);
  }, [colorScheme, root]);

  /*
   * The pose is applied to the live root exactly as the scheme above is, and for
   * the same reason. It is deliberately NOT re-asserted every frame: an app that
   * leaves the prop on `"auto"` and calls `root.setWindowActivation(...)` by hand
   * through `useGlassRoot()` keeps what it set, because a binding that wrote its
   * prop back on every frame would make the imperative seam write-only.
   */
  useEffect(() => {
    if (root === null) return;
    root.setWindowActivation(windowActivation);
  }, [root, windowActivation]);

  /*
   * The bindings' motion runs on the root's frame loop, not on one of their own.
   *
   * The root already owns a cadence, and until it grew `subscribe` there was no
   * way to join it — so these bindings ran a second `requestAnimationFrame`
   * beside it, with no declared ordering between the two. Now the ticker is
   * advanced from the root's own frame, after the scene has settled, which means
   * one wake-up per frame and a defined order: the scene resolves, then the
   * springs step against it.
   *
   * `ticker.start()` is still there and still runs rAF — a consumer driving a
   * bare `createGlassTicker` has no root to borrow a loop from. It is simply no
   * longer what `GlassRoot` uses.
   */
  useEffect(() => {
    if (root === null) return;
    const unsubscribePoll = ticker.subscribe(() => store.poll());
    const unsubscribeFrames = autoStart
      ? root.subscribe(({ deltaMs }) => ticker.advance(deltaMs))
      : undefined;
    return () => {
      unsubscribePoll();
      unsubscribeFrames?.();
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
      materialProfileDocument: selectedDocument,
      ticker,
      profile: motionProfile,
      devMode,
      diagnostics,
      subscribeDiagnostics: (listener) => diagnosticStore.subscribe(listener),
    }),
    [devMode, diagnostics, diagnosticStore, motionProfile, root, selectedDocument, ticker],
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

/**
 * Which pose this root is actually drawing — `"auto"` already folded against the
 * window's focus.
 *
 * The resolved answer, beside the resolved group state and the resolved
 * accessibility policy, because that is what the honesty core is for: a readout
 * says what drew, not what was asked for. `undefined` until the root exists,
 * which is the tree's first commit.
 */
export function useGlassWindowActivation(): ResolvedWindowActivation | undefined {
  const store = useGlassRootStore();
  return useSyncExternalStore(
    useCallback((listener) => store.subscribeWindowActivation(listener), [store]),
    () => store.windowActivation(),
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
