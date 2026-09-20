/**
 * The three contexts the bindings pass down, and nothing else.
 *
 * They are deliberately small. `vitrea-react` is thin by policy (§Repo layout):
 * it owns React lifecycle and JSX shape, and every decision it does not own
 * lives in `platform-web`, `core` or `motion`. So the contexts carry handles,
 * not state — the runtime state stays where it is authored.
 */

import type { GlassPlane } from "@vitreajs/vitrea";
import type {
  GlassMaterialProfileDocument,
  GlassRoot,
  VitreaDiagnostic,
} from "@vitreajs/vitrea-web";
import type { MotionProfile } from "@vitrea/motion";
import { createContext, useContext } from "react";

import type { GlassTicker } from "./ticker";

/** A diagnostic with the arrival order that lets a devtools panel show a tail. */
export type RecordedDiagnostic = VitreaDiagnostic & { readonly seq: number };

export interface GlassRootHandle {
  /** `null` until the mount effect has built the runtime. */
  readonly root: GlassRoot | null;
  /**
   * Which measured material this root selected — the whole document, both
   * schemes and both poses, and its CSS crossing.
   *
   * Beside `root` rather than on it, because a consumer needs it before the
   * mount effect has run: `GlassToolbar` derives a layout number from the
   * material's blur on its first render, and a root that is still `null` would
   * leave it deriving that number from a material nothing on the page draws
   * (W30 Decision Log 1 (f); the tracker's `GlassToolbar` seam). `root.material`
   * is the resolved IDENTITY of the endpoint that drew — a name, a key and a
   * digest — and cannot be composed into anything; this is the document itself.
   *
   * It is what the ROOT selected, not what the prop currently says. The runtime
   * reads the document once at construction and a later prop change does not
   * move it, so reporting the prop would name a material the page is not
   * drawing.
   */
  readonly materialProfileDocument: GlassMaterialProfileDocument;
  readonly ticker: GlassTicker;
  /** Motion constants, already through the Reduced Motion transform when it applies. */
  readonly profile: MotionProfile;
  readonly devMode: boolean;
  /** Everything both diagnostics code spaces reported, newest last. */
  readonly diagnostics: readonly RecordedDiagnostic[];
  subscribeDiagnostics(listener: () => void): () => void;
}

export const GlassRootContext = createContext<GlassRootHandle | null>(null);

export interface GlassGroupHandle {
  readonly groupId: string;
  /**
   * Take a lease on the group for as long as a surface is registered in it.
   *
   * core refuses to remove a group that still has nodes (`GlassSceneError`
   * `"in-use"`), and React's unmount order across a subtree is not something a
   * binding should be betting a structural throw on. Counting leases makes the
   * order irrelevant: whichever of the group and its last surface unmounts
   * second is the one that performs the removal.
   */
  retain(): () => void;
}

export const GlassGroupContext = createContext<GlassGroupHandle | null>(null);

/**
 * Which plane's host layer the surrounding subtree already renders into.
 *
 * X1 puts every glass host inside its plane's host layer, so a surface that
 * finds no scope portals itself there. One that finds its own plane is already
 * in the right subtree and renders in place — which is what keeps a toolbar's
 * flex layout intact instead of scattering its buttons to the plane root.
 */
export const PlaneScopeContext = createContext<GlassPlane | null>(null);

export function useGlassRootHandle(): GlassRootHandle {
  const handle = useContext(GlassRootContext);
  if (handle === null) {
    throw new Error(
      "vitrea-react: this component must be rendered inside a <GlassRoot>. The root owns the " +
        "planes every glass surface lives in (X1), so there is nowhere to register without one.",
    );
  }
  return handle;
}

/** The runtime itself, or `null` on the first render before the mount effect. */
export function useGlassRoot(): GlassRoot | null {
  return useGlassRootHandle().root;
}

export function useGlassGroupId(explicit?: string): string {
  const group = useContext(GlassGroupContext);
  const groupId = explicit ?? group?.groupId;
  if (groupId === undefined) {
    throw new Error(
      "vitrea-react: no glass group in scope. Wrap this surface in a <GlassGroup> (a group is " +
        "what shares one backdrop source and one sampling proxy) or pass an explicit groupId.",
    );
  }
  return groupId;
}
